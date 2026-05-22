import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pickle
import os
import random
from typing import List, Tuple


# === Глобальные параметры ===
MAX_LENGTH = 64
TEMPERATURE = 0.8
TOP_K = 40
TOP_P = 0.9
BEAM_WIDTH = 5
ONLINE_LR = 0.0001  # Меньше, чем основное обучение


# === RoPE (Rotary Positional Embedding) ===
def apply_rope(q, k, dim=64):
    """
    Применяет Rotary Positional Embedding к query и key.
    Позволяет модели понимать порядок токенов без абсолютных позиций.
    """
    device = q.device
    batch_size, seq_len, _ = q.shape
    half_dim = dim // 2

    # Частоты для разных позиций
    theta = torch.arange(0, half_dim, 2, dtype=torch.float32, device=device)
    theta = 1.0 / (10000 ** (theta / half_dim))

    pos = torch.arange(seq_len, device=device).unsqueeze(-1)  # [seq_len, 1]
    freqs = pos * theta  # [seq_len, half_dim]

    sin = torch.sin(freqs).repeat_interleave(2, dim=-1)
    cos = torch.cos(freqs).repeat_interleave(2, dim=-1)

    # Применяем к q и k
    q_rot = torch.cat([q[..., ::2] * cos - q[..., 1::2] * sin,
                       q[..., 1::2] * cos + q[..., ::2] * sin], dim=-1)
    k_rot = torch.cat([k[..., ::2] * cos - k[..., 1::2] * sin,
                       k[..., 1::2] * cos + k[..., ::2] * sin], dim=-1)

    return q_rot, k_rot


class AttentionLayer(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.q_proj = nn.Linear(hidden_dim, hidden_dim)
        self.k_proj = nn.Linear(hidden_dim, hidden_dim)
        self.v_proj = nn.Linear(hidden_dim, hidden_dim)
        self.out_proj = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, x, mask=None):
        """
        :param x: [batch, seq_len, hidden_dim]
        :param mask: [batch, seq_len] — 1 если токен валиден, 0 если <PAD>
        """
        B, T, C = x.shape

        Q = self.q_proj(x)  # [B, T, C]
        K = self.k_proj(x)  # [B, T, C]
        V = self.v_proj(x)  # [B, T, C]

        # RoPE
        Q, K = apply_rope(Q, K, dim=C)

        # Scaled dot-product attention
        attn_weights = Q @ K.transpose(-2, -1) / (C ** 0.5)  # [B, T, T]

        if mask is not None:
            mask = mask.unsqueeze(1).unsqueeze(2)  # [B, 1, 1, T]
            attn_weights = attn_weights.masked_fill(mask == 0, float('-inf'))

        attn_weights = torch.softmax(attn_weights, dim=-1)
        out = attn_weights @ V  # [B, T, C]
        return self.out_proj(out)


class ChatDataset(Dataset):
    def __init__(self, data_file):
        with open(data_file, 'rb') as f:
            data = pickle.load(f)
        self.input_sequences = data['input_sequences']
        self.target_sequences = data['target_sequences']

    def __len__(self): return len(self.input_sequences)

    def __getitem__(self, idx):
        return (
            torch.tensor(self.input_sequences[idx], dtype=torch.long),
            torch.tensor(self.target_sequences[idx], dtype=torch.long)
        )


class ChatNN(nn.Module):
    def __init__(self, vocab_size, embedding_dim=128, hidden_dim=256, num_layers=2):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.layers = nn.ModuleList([
            AttentionLayer(hidden_dim) for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(hidden_dim)
        self.fc = nn.Linear(hidden_dim, vocab_size)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x, mask=None):
        embedded = self.embedding(x)  # [B, T, E]
        if embedded.size(-1) != self.hidden_dim:
            embedded = nn.Linear(embedded.size(-1), self.hidden_dim).to(embedded.device)(embedded)

        out = embedded
        for layer in self.layers:
            out = out + layer(self.norm(out), mask)  # Residual
            out = self.dropout(out)
        logits = self.fc(out)
        return logits, None

    # --- BEAM SEARCH ---
    def beam_search(self, input_ids, max_length=64, beam_width=5, temperature=0.8):
        """
        Beam Search для более качественной генерации.
        """
        self.eval()
        device = input_ids.device
        B = input_ids.size(0)

        sequences = [(input_ids.clone(), 0.0)]  # (tokens, score)

        with torch.no_grad():
            for _ in range(max_length):
                candidates = []
                for seq, score in sequences:
                    outputs, _ = self(seq, mask=(seq != 0))
                    next_token_logits = outputs[:, -1, :] / temperature
                    probs = torch.softmax(next_token_logits, dim=-1)

                    top_probs, top_indices = torch.topk(probs, beam_width)
                    for i in range(beam_width):
                        token_id = top_indices[0, i].item()
                        token_prob = top_probs[0, i].item()
                        new_seq = torch.cat([seq, torch.tensor([[token_id]], device=device)], dim=1)
                        candidates.append((new_seq, score + np.log(token_prob)))

                # Выбираем лучшие beam_width кандидатов
                candidates.sort(key=lambda x: x[1], reverse=True)
                sequences = candidates[:beam_width]

                # Если все последовательности закончились
                if all(seq[0][-1, -1].item() == 0 or seq[0][-1, -1].item() in [2, 3, 4] for seq, _ in sequences):
                    break

        return sequences[0][0].cpu().numpy()[0]  # Лучший результат

    # --- ONLINE LEARNING ---
    def online_update(self, input_ids, target_ids, optimizer, criterion, device='cpu'):
        """
        Обновляет модель на основе одного взаимодействия.
        Вызывается после каждого ответа бота.
        """
        self.train()
        input_ids = input_ids.to(device)
        target_ids = target_ids.to(device)

        optimizer.zero_grad()
        outputs, _ = self(input_ids, mask=(input_ids != 0))
        loss = criterion(outputs.view(-1, self.vocab_size), target_ids.view(-1))
        loss.backward()
        optimizer.step()

        return loss.item()


# === УЛУЧШЕННАЯ ГЕНЕРАЦИЯ С BEAM SEARCH ===
def generate_response(model, tokenizer, text, device='cpu', max_length=MAX_LENGTH):
    model.eval()
    word_to_idx = tokenizer['word_to_idx']
    idx_to_word = tokenizer['idx_to_word']
    pad_id = word_to_idx.get('<PAD>', 0)
    unk_id = word_to_idx.get('<UNK>', 1)

    # Токенизация
    words = text.lower().split()
    indices = [word_to_idx.get(w, unk_id) for w in words]
    input_tensor = torch.tensor([indices], dtype=torch.long).to(device)
    model.to(device)

    # Beam Search
    generated_ids = model.beam_search(
        input_tensor,
        max_length=max_length,
        beam_width=BEAM_WIDTH,
        temperature=TEMPERATURE
    )

    # Отсекаем после <PAD> или конца предложения
    response_tokens = []
    for idx in generated_ids:
        if idx in [pad_id, unk_id]:
            break
        word = idx_to_word.get(idx, '')
        if word in ['.', '!', '?']:
            response_tokens.append(word)
            break
        response_tokens.append(word)

    return ' '.join(response_tokens).strip()


# === ОБУЧЕНИЕ ===
def train_model(data_file, vocab_size, embedding_dim=128, hidden_dim=256, num_layers=2, epochs=100, batch_size=32, lr=0.001):
    dataset = ChatDataset(data_file)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = ChatNN(vocab_size, embedding_dim, hidden_dim, num_layers)
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    optimizer = optim.Adam(model.parameters(), lr=lr)

    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for inputs, targets in dataloader:
            optimizer.zero_grad()
            outputs, _ = model(inputs, mask=(inputs != 0))
            loss = criterion(outputs.view(-1, vocab_size), targets.view(-1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {total_loss/len(dataloader):.4f}')

    os.makedirs('Wuglarst/models', exist_ok=True)
    torch.save(model.state_dict(), 'Wuglarst/models/chat_model.pth')
    print('✅ Модель обучена и сохранена!')
    return model


# === ONLINE LEARNING ХЕЛПЕР ===
def setup_online_learning(model_path, tokenizer_path, lr=ONLINE_LR):
    """
    Подготавливает модель для онлайн-обучения.
    """
    with open(tokenizer_path, 'rb') as f:
        tokenizer = pickle.load(f)

    model = ChatNN(tokenizer['vocab_size'])
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss(ignore_index=tokenizer['word_to_idx']['<PAD>'])

    return model, tokenizer, optimizer, criterion