import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Literal


# === Rotary Positional Embedding (RoPE) — корректная версия для (B, T, C) ===
def apply_rope(q, k, dim=64):
    """
    Применяет Rotary Position Embedding к первым `dim` измерениям Q и K.
    :param q: (B, T, C)
    :param k: (B, T, C)
    :param dim: размерность для RoPE (должна быть <= C)
    :return: q_rot, k_rot — вращённые тензоры той же формы
    """
    device = q.device
    B, T, C = q.shape
    if dim > C:
        raise ValueError(f"dim={dim} > C={C}")
    half_dim = dim // 2

    # Генерируем частоты: (half_dim//2,)
    theta = torch.arange(0, half_dim, 2, dtype=torch.float32, device=device)
    theta = 1.0 / (10000 ** (theta / half_dim))  # (half_dim//2,)

    # Позиции: (T,)
    pos = torch.arange(T, device=device).float()
    freqs = pos.unsqueeze(-1) * theta.unsqueeze(0)  # (T, half_dim//2)

    # Создаём sin и cos: (T, half_dim)
    sin = torch.sin(freqs).repeat_interleave(2, dim=-1)  # (T, half_dim)
    cos = torch.cos(freqs).repeat_interleave(2, dim=-1)  # (T, half_dim)

    # Добавляем batch: (1, T, half_dim)
    cos = cos.unsqueeze(0)
    sin = sin.unsqueeze(0)

    # Разделяем только первую часть
    q1 = q[..., :half_dim]          # (B, T, half_dim)
    q2 = q[..., half_dim:dim]       # (B, T, half_dim)
    q_rest = q[..., dim:]           # (B, T, C-dim)

    k1 = k[..., :half_dim]
    k2 = k[..., half_dim:dim]
    k_rest = k[..., dim:]

    # Применяем поворот
    q_rot_part = torch.cat([q1 * cos - q2 * sin, q1 * sin + q2 * cos], dim=-1)  # (B, T, dim)
    q_rot = torch.cat([q_rot_part, q_rest], dim=-1)  # (B, T, C)

    k_rot_part = torch.cat([k1 * cos - k2 * sin, k1 * sin + k2 * cos], dim=-1)
    k_rot = torch.cat([k_rot_part, k_rest], dim=-1)

    return q_rot, k_rot


# === Attention Layer с маской — только 3D ===
class AttentionLayer(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.q_proj = nn.Linear(hidden_dim, hidden_dim)
        self.k_proj = nn.Linear(hidden_dim, hidden_dim)
        self.v_proj = nn.Linear(hidden_dim, hidden_dim)
        self.out_proj = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None):
        """
        :param x: (B, T, C)
        :param mask: (B, T) — 1 если токен валиден
        :return: (B, T, C)
        """
        B, T, C = x.shape

        # Проекции
        Q = self.q_proj(x)  # (B, T, C)
        K = self.k_proj(x)
        V = self.v_proj(x)

        # RoPE
        Q, K = apply_rope(Q, K, dim=C)

        # Scaled dot-product attention: (B, T, T)
        attn_weights = Q @ K.transpose(-2, -1) / (C ** 0.5)

        # Маска
        if mask is not None:
            mask = mask.unsqueeze(1)  # (B, 1, T)
            attn_weights = attn_weights.masked_fill(mask == 0, float('-inf'))

        attn_weights = F.softmax(attn_weights, dim=-1)
        out = attn_weights @ V  # (B, T, C)

        return self.out_proj(out)


# === Основная модель: ChatNN ===
class ChatNN(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
        num_layers: int = 2,
        max_length: int = 64,
        pad_token_id: int = 0,
        eos_token_id: int = 0
    ):
        """
        :param vocab_size: размер словаря
        :param pad_token_id: ID для <PAD> (обычно 0)
        :param eos_token_id: ID для <EOS> (можно тот же, что и PAD)
        """
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.max_length = max_length
        self.pad_token_id = pad_token_id
        self.eos_token_id = eos_token_id

        # Эмбеддинги
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=pad_token_id)
        self.pos_embedding = nn.Embedding(max_length, embedding_dim)

        # Адаптация размера
        if embedding_dim != hidden_dim:
            self.input_proj = nn.Linear(embedding_dim, hidden_dim)
        else:
            self.input_proj = None

        # Трансформерные слои
        self.layers = nn.ModuleList([
            AttentionLayer(hidden_dim) for _ in range(num_layers)
        ])

        self.norm = nn.LayerNorm(hidden_dim)
        self.fc = nn.Linear(hidden_dim, vocab_size)
        self.dropout = nn.Dropout(0.3)

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

        # Адаптация
        if self.input_proj is not None:
            x = self.input_proj(x)  # (B, T, H)

        # Нормализация
        x = self.norm(x)
        x = self.dropout(x)

        # Проход по слоям
        for layer in self.layers:
            residual = x
            x = layer(self.norm(x), mask=mask)
            x = residual + x
            x = self.dropout(x)

        # Финальная нормализация и выход
        x = self.norm(x)
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