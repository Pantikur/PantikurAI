import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Literal, Tuple


# === RMSNorm — улучшенная нормализация ===
class RMSNorm(nn.Module):
    """
    Root Mean Square Layer Normalization.
    Стабильнее чем LayerNorm для генерации текста.
    """
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # RMS = sqrt(mean(x^2))
        norm = x.pow(2).mean(-1, keepdim=True).add(self.eps).rsqrt()
        return x * norm * self.weight


# === Rotary Positional Embedding (RoPE) — универсальная версия ===
def apply_rope(q, k, dim=64):
    """
    Применяет Rotary Position Embedding к первым `dim` измерениям Q и K.
    Работает с 3D (B, T, C) и 4D (B, heads, T, C).
    """
    device = q.device
    ndim = q.ndim  # 3 или 4
    
    if ndim == 3:
        B, T, C = q.shape
        # Добавляем head dimension
        q = q.unsqueeze(1)  # (B, 1, T, C)
        k = k.unsqueeze(1)
        ndim = 4
    else:
        B, heads, T, C = q.shape
    
    if dim > C:
        raise ValueError(f"dim={dim} > C={C}")
    half_dim = dim // 2

    # Генерируем частоты
    theta = torch.arange(0, half_dim, 2, dtype=torch.float32, device=device)
    theta = 1.0 / (10000 ** (theta / half_dim))

    # Позиции
    pos = torch.arange(T, device=device).float()
    freqs = pos.unsqueeze(-1) * theta.unsqueeze(0)

    # Создаём sin и cos
    sin = torch.sin(freqs).repeat_interleave(2, dim=-1)
    cos = torch.cos(freqs).repeat_interleave(2, dim=-1)

    # Добавляем batch и heads dimensions
    cos = cos.unsqueeze(0).unsqueeze(0)  # (1, 1, T, half_dim)
    sin = sin.unsqueeze(0).unsqueeze(0)

    # Разделяем
    q1 = q[..., :half_dim]
    q2 = q[..., half_dim:dim]
    q_rest = q[..., dim:]

    k1 = k[..., :half_dim]
    k2 = k[..., half_dim:dim]
    k_rest = k[..., dim:]

    # Применяем поворот
    q_rot_part = torch.cat([q1 * cos - q2 * sin, q1 * sin + q2 * cos], dim=-1)
    q_rot = torch.cat([q_rot_part, q_rest], dim=-1)

    k_rot_part = torch.cat([k1 * cos - k2 * sin, k1 * sin + k2 * cos], dim=-1)
    k_rot = torch.cat([k_rot_part, k_rest], dim=-1)

    # Если было 3D, убираем head dimension
    if ndim == 3:
        q_rot = q_rot.squeeze(1)
        k_rot = k_rot.squeeze(1)

    return q_rot, k_rot


# === Multi-Head Attention — улучшенная версия ===
class MultiHeadAttention(nn.Module):
    """
    Multi-Head Attention с RoPE.
    Разбивает hidden_dim на head_count голов, каждая работает в своём подпространстве.
    """
    def __init__(self, hidden_dim: int, head_count: int = 4, dropout: float = 0.1):
        super().__init__()
        assert hidden_dim % head_count == 0, "hidden_dim должен делиться на head_count"
        
        self.hidden_dim = hidden_dim
        self.head_count = head_count
        self.head_dim = hidden_dim // head_count
        self.dropout = nn.Dropout(dropout)
        
        # Все проекции в одну линейную layer для эффективности
        self.qkv_proj = nn.Linear(hidden_dim, hidden_dim * 3)
        self.out_proj = nn.Linear(hidden_dim, hidden_dim)
        
        # RoPE применяется к каждой голове
        self.rope_dim = self.head_dim  # размер для поворота
        
    def _reshape_for_heads(self, x: torch.Tensor) -> torch.Tensor:
        """(B, T, H) → (B, heads, T, head_dim)"""
        B, T, H = x.shape
        x = x.view(B, T, self.head_count, self.head_dim)
        return x.transpose(1, 2)  # (B, heads, T, head_dim)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        B, T, C = x.shape
        
        # Q, K, V проекции
        qkv = self.qkv_proj(x)  # (B, T, 3*H)
        q, k, v = qkv.chunk(3, dim=-1)  # каждый (B, T, H)
        
        # reshaping для multi-head
        q = self._reshape_for_heads(q)  # (B, heads, T, head_dim)
        k = self._reshape_for_heads(k)
        v = self._reshape_for_heads(v)
        
        # RoPE на каждую голову
        q, k = apply_rope(q, k, dim=self.rope_dim)
        
        # Scaled dot-product attention
        attn_scores = (q @ k.transpose(-2, -1)) / (self.head_dim ** 0.5)  # (B, heads, T, T)
        
        # Mask: (B, 1, T) → (B, 1, 1, T)
        if mask is not None:
            mask = mask.unsqueeze(1).unsqueeze(1)  # (B, 1, 1, T)
            attn_scores = attn_scores.masked_fill(mask == 0, float('-inf'))
        
        attn_weights = F.softmax(attn_scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        out = attn_weights @ v  # (B, heads, T, head_dim)
        
        # Back to (B, T, H)
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        
        return self.out_proj(out)


# === Feed-Forward Network — улучшенная версия (GLU) ===
class FeedForward(nn.Module):
    """
    Improved Feed-Forward с Gated Linear Unit (GLU).
    Расширяет dim в 2x и применяет gating для лучшего обучения.
    """
    def __init__(self, hidden_dim: int, ff_dim: int = None, dropout: float = 0.1):
        super().__init__()
        self.ff_dim = ff_dim or hidden_dim * 4
        self.w1 = nn.Linear(hidden_dim, self.ff_dim)
        self.w2 = nn.Linear(self.ff_dim, hidden_dim)
        self.w_gate = nn.Linear(hidden_dim, self.ff_dim)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # GLU: w2(GELU(w1(x)) * sigmoid(w_gate(x)))
        gate = torch.sigmoid(self.w_gate(x))
        activated = F.gelu(self.w1(x))
        out = activated * gate
        return self.dropout(self.w2(out))


# === Improved Transformer Block ===
class TransformerBlock(nn.Module):
    """
    Transformer block: MultiHeadAttention + FFN с LayerNorm и residual.
    Pre-LN (LayerNorm перед каждым блоком) — стабильнее при обучении.
    """
    def __init__(self, hidden_dim: int, head_count: int = 4, ff_dim: int = None, dropout: float = 0.1):
        super().__init__()
        self.attention = MultiHeadAttention(hidden_dim, head_count, dropout)
        self.ffn = FeedForward(hidden_dim, ff_dim, dropout)
        self.norm_attn = nn.LayerNorm(hidden_dim)
        self.norm_ffn = nn.LayerNorm(hidden_dim)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Pre-LN Attention
        attn_out = self.attention(self.norm_attn(x), mask=mask)
        x = x + self.dropout(attn_out)
        
        # Pre-LN FFN
        ffn_out = self.ffn(self.norm_ffn(x))
        x = x + self.dropout(ffn_out)
        
        return x


# === Основная модель: ChatNN (улучшенная) ===
class ChatNN(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
        num_layers: int = 4,        # Увеличено с 2 до 4
        max_length: int = 256,       # Увеличено с 64 до 256
        pad_token_id: int = 0,
        eos_token_id: int = 0,
        head_count: int = 4,         # Multi-head attention heads
        ff_dim: int = None,          # Feed-forward dim (по умолч. hidden*4)
        dropout: float = 0.1         # Уменьшено с 0.3 до 0.1
    ):
        """
        Улучшенная модель с Multi-Head Attention и GLU FFN.
        """
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.max_length = max_length
        self.pad_token_id = pad_token_id
        self.eos_token_id = eos_token_id
        self.head_count = head_count

        # Эмбеддинги
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=pad_token_id)
        self.pos_embedding = nn.Embedding(max_length, embedding_dim)

        # RMSNorm (стабильнее чем LayerNorm для генерации)
        self.norm_input = RMSNorm(embedding_dim)

        # Адаптация размера
        if embedding_dim != hidden_dim:
            self.input_proj = nn.Linear(embedding_dim, hidden_dim)
        else:
            self.input_proj = None

        # Улучшенные трансформерные слои
        ff_dim = ff_dim or hidden_dim * 4
        self.layers = nn.ModuleList([
            TransformerBlock(hidden_dim, head_count, ff_dim, dropout)
            for _ in range(num_layers)
        ])

        self.norm_final = RMSNorm(hidden_dim)
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
        # Weight tying — только если embedding_dim == hidden_dim
        self.weight_tying = (embedding_dim == hidden_dim)

    def forward(self, input_ids: torch.LongTensor, mask: Optional[torch.Tensor] = None):
        """
        :param input_ids: (B, T)
        :param mask: (B, T)
        :return: logits (B, T, vocab_size)
        """
        B, T = input_ids.shape
        device = input_ids.device

        # Позиции
        pos = torch.arange(0, T, device=device).unsqueeze(0)  # (1, T)

        # Эмбеддинги
        x = self.embedding(input_ids)  # (B, T, E)
        x = x + self.pos_embedding(pos)  # (B, T, E)

        # Нормализация входных данных
        x = self.norm_input(x)

        # Адаптация размера
        if self.input_proj is not None:
            x = self.input_proj(x)  # (B, T, H)

        # Проход по слоям
        for layer in self.layers:
            x = layer(x, mask=mask)

        # Финальная нормализация и выход
        x = self.norm_final(x)
        
        # Weight tying: используем weights embedding для проекции на vocab
        if self.weight_tying:
            logits = torch.matmul(x, self.embedding.weight.T)  # (B, T, V)
        else:
            logits = self.fc(x)  # (B, T, V)
        
        return logits

    # --- BEAM SEARCH ---
    def _generate_beam(
        self,
        input_ids: torch.LongTensor,
        max_new_tokens: int = 64,
        temperature: float = 0.8,
        top_k: int = 40,
        beam_width: int = 5
    ) -> torch.Tensor:
        """
        Генерация с beam search.
        """
        self.eval()
        device = input_ids.device

        with torch.no_grad():
            sequences = [(input_ids.clone(), 0.0)]  # (seq, score)

            for _ in range(max_new_tokens):
                all_candidates = []
                for seq, score in sequences:
                    logits = self(seq, mask=(seq != self.pad_token_id))
                    next_logits = logits[:, -1, :] / temperature

                    if top_k > 0:
                        top_values, top_indices = torch.topk(next_logits, top_k)
                        probs = F.softmax(top_values, dim=-1)
                    else:
                        probs = F.softmax(next_logits, dim=-1)
                        top_indices = torch.arange(self.vocab_size, device=device).unsqueeze(0)

                    for i, prob in enumerate(probs[0]):
                        token_id = top_indices[0, i].item()
                        new_score = score + float(torch.log(prob + 1e-12))
                        new_seq = torch.cat([seq, torch.tensor([[token_id]], device=device)], dim=1)
                        all_candidates.append((new_seq, new_score))

                all_candidates.sort(key=lambda x: x[1], reverse=True)
                sequences = all_candidates[:beam_width]

                # Остановка, если все последовательности закончились
                if all(seq[0, -1].item() == self.eos_token_id for seq, _ in sequences):
                    break

            return sequences[0][0][0]  # (N,)

    # --- NUCLEUS SAMPLING (top_p) ---
    def _generate_nucleus(
        self,
        input_ids: torch.LongTensor,
        max_new_tokens: int = 64,
        temperature: float = 0.8,
        top_p: float = 0.9,
        do_sample: bool = True
    ) -> torch.Tensor:
        """
        Генерация с nucleus sampling (top_p).
        """
        self.eval()
        device = input_ids.device
        seq = input_ids.clone()

        with torch.no_grad():
            for _ in range(max_new_tokens):
                logits = self(seq, mask=(seq != self.pad_token_id))
                next_logits = logits[:, -1, :] / temperature
                probs = F.softmax(next_logits, dim=-1)

                # Top-p filtering
                sorted_probs, sorted_indices = torch.sort(probs, descending=True, dim=-1)
                cumsum_probs = torch.cumsum(sorted_probs, dim=-1)
                nucleus = cumsum_probs <= top_p
                nucleus[:, 1:] = nucleus[:, :-1].clone()
                nucleus[:, 0] = 0  # первый всегда остаётся

                filtered_probs = sorted_probs.clone()
                filtered_probs[~nucleus] = 0.0
                filtered_probs = filtered_probs / filtered_probs.sum(dim=-1, keepdim=True)

                # Выбор
                if do_sample:
                    next_token_idx = torch.multinomial(filtered_probs, num_samples=1)
                else:
                    next_token_idx = torch.argmax(filtered_probs, dim=-1, keepdim=True)

                next_token = sorted_indices.gather(-1, next_token_idx)

                seq = torch.cat([seq, next_token], dim=1)

                # Остановка при EOS
                if next_token.item() == self.eos_token_id:
                    break

        return seq[0]

    # --- ЕДИНЫЙ ИНТЕРФЕЙС ГЕНЕРАЦИИ ---
    def generate(
        self,
        input_ids: torch.LongTensor,
        method: Literal["beam", "nucleus"] = "beam",
        max_new_tokens: int = 64,
        temperature: float = 0.8,
        top_k: int = 40,
        top_p: float = 0.9,
        beam_width: int = 5,
        do_sample: bool = True
    ) -> torch.Tensor:
        """
        Универсальный метод генерации.
        :param method: 'beam' или 'nucleus'
        :param top_p: для nucleus sampling
        :param do_sample: использовать случайный выбор (иначе argmax)
        """
        if method == "beam":
            return self._generate_beam(
                input_ids=input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_k=top_k,
                beam_width=beam_width
            )
        elif method == "nucleus":
            return self._generate_nucleus(
                input_ids=input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample
            )
        else:
            raise ValueError(f"method должен быть 'beam' или 'nucleus', получено: {method}")


# === Глобальная функция для совместимости с импортом ===
def generate_response(
    model: ChatNN,
    input_ids: torch.LongTensor,
    method: str = "beam",
    max_new_tokens: int = 64,
    temperature: float = 0.8,
    top_k: int = 40,
    top_p: float = 0.9,
    beam_width: int = 5,
    do_sample: bool = True
):
    """
    Обёртка для model.generate — чтобы можно было импортировать напрямую.
    """
    return model.generate(
        input_ids=input_ids,
        method=method,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        beam_width=beam_width,
        do_sample=do_sample
    )