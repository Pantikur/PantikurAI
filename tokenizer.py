import json
from typing import List, Dict
from collections import Counter


class SimpleTokenizer:
    """
    Простой токенизатор для чат-бота с поддержкой <PAD>, <EOS>
    """

    def __init__(self, vocab_size: int = 5000):
        self.vocab_size = vocab_size
        self.pad_token = "<PAD>"
        self.eos_token = "<EOS>"
        self.unk_token = "<UNK>"

        # Специальные токены
        self.special_tokens = [self.pad_token, self.eos_token, self.unk_token]
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}

    def build_vocab(self, texts: List[str]):
        """Строит словарь по списку текстов"""
        all_words = []
        for text in texts:
            words = text.lower().split()
            all_words.extend(words)

        # Считаем частоты
        counter = Counter(all_words)
        most_common = counter.most_common(self.vocab_size - len(self.special_tokens))

        # Формируем словарь
        self.vocab = {token: idx for idx, token in enumerate(self.special_tokens)}
        for word, _ in most_common:
            if word not in self.vocab:
                self.vocab[word] = len(self.vocab)

        # Обратный словарь
        self.inverse_vocab = {idx: word for word, idx in self.vocab.items()}

    def encode(self, text: str, add_eos: bool = True, max_length: int = 64) -> List[int]:
        """Кодирует текст в последовательность индексов"""
        words = text.lower().split()
        ids = [self.vocab.get(word, self.vocab[self.unk_token]) for word in words]

        if add_eos:
            ids.append(self.vocab[self.eos_token])

        # Обрезаем или дополняем
        if len(ids) > max_length:
            ids = ids[:max_length]
        else:
            ids += [self.vocab[self.pad_token]] * (max_length - len(ids))

        return ids

    def decode(self, token_ids: List[int]) -> str:
        """Декодирует последовательность индексов обратно в текст"""
        words = []
        for idx in token_ids:
            word = self.inverse_vocab.get(idx, self.unk_token)
            if word == self.pad_token:
                break
            if word == self.eos_token:
                break
            if word not in self.special_tokens:
                words.append(word)
        return " ".join(words)

    def save(self, filepath: str):
        """Сохраняет токенизатор"""
        data = {
            "vocab": self.vocab,
            "inverse_vocab": self.inverse_vocab,
            "vocab_size": self.vocab_size,
            "pad_token": self.pad_token,
            "eos_token": self.eos_token,
            "unk_token": self.unk_token
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, filepath: str):
        """Загружает токенизатор"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.vocab = data["vocab"]
        self.inverse_vocab = data["inverse_vocab"]
        self.vocab_size = data["vocab_size"]
        self.pad_token = data["pad_token"]
        self.eos_token = data["eos_token"]
        self.unk_token = data["unk_token"]