# Wuglarst/src/tokenizer.py — SimpleTokenizer (совместимый с tokenizer.json)
#
# Вынесен из chatbot.py для уменьшения размера модуля.

import json
from typing import List

QWEN25_MAX_LENGTH = 512


class SimpleTokenizer:
    """Токенизатор, совместимый с tokenizer.json"""
    def __init__(self, tokenizer_path: str, max_length: int = QWEN25_MAX_LENGTH):
        with open(tokenizer_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.vocab = data["vocab"]
        # inverse_vocab из train.py — dict {str_idx: word}
        # Например: {"0": "<PAD>", "2": "<EOS>", "71": "же"}
        inv = data["inverse_vocab"]
        first_key = next(iter(inv.keys())) if inv else ""
        try:
            int(first_key)
            # {str_idx: word} → {int: word}
            self.inverse_vocab = {int(k): v for k, v in inv.items()}
        except (ValueError, TypeError):
            # {word: idx} → {int: word}
            self.inverse_vocab = {v: k for k, v in inv.items()}

        self.pad_token_id = self.vocab.get("<PAD>", 0)
        self.eos_token_id = self.vocab.get("<EOS>", 2)
        self.unk_token_id = self.vocab.get("<UNK>", 1)
        self.max_length = max_length

    def encode(self, text: str, add_eos: bool = False, max_length: int | None = None) -> List[int]:
        if max_length is None:
            max_length = self.max_length
        words = text.lower().split()
        ids = [self.vocab.get(word, self.unk_token_id) for word in words]
        if add_eos:
            ids.append(self.eos_token_id)
        if len(ids) >= max_length:
            ids = ids[:max_length - 1] + [ids[-1]]  # сохраняем последний токен
        else:
            ids += [self.pad_token_id] * (max_length - len(ids))
        return ids

    def decode(self, token_ids: List[int]) -> str:
        words = []
        for idx in token_ids:
            if idx in [self.pad_token_id, self.eos_token_id]:
                break
            # inverse_vocab теперь dict {int: word}
            word = self.inverse_vocab.get(int(idx), "<UNK>")  # type: ignore[arg-type]
            if word not in ["<PAD>", "<UNK>", "<EOS>"]:
                words.append(word)
        return " ".join(words)