import torch
from torch.utils.data import Dataset
from typing import List, Tuple
import json


class ChatDataset(Dataset):
    """
    Датасет для обучения чат-бота.
    Ожидает список пар: [{"user": "Привет", "bot": "Здравствуй!"}, ...]
    """

    def __init__(self, data_path: str, tokenizer, max_length: int = 64):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.pairs = self._load_data(data_path)

    def _load_data(self, data_path: str) -> List[Tuple[str, str]]:
        """Загружает данные из JSON"""
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        pairs = []
        for item in data:
            user_msg = item.get("user", "").strip()
            bot_msg = item.get("bot", "").strip()
            if user_msg and bot_msg:
                pairs.append((user_msg, bot_msg))
        return pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        user_text, bot_text = self.pairs[idx]

        # Кодируем вход (вопрос пользователя)
        input_ids = self.tokenizer.encode(user_text, add_eos=True, max_length=self.max_length)
        # Цель — ответ бота (с <EOS>)
        target_ids = self.tokenizer.encode(bot_text, add_eos=True, max_length=self.max_length)

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "target_ids": torch.tensor(target_ids, dtype=torch.long),
            "mask": (torch.tensor(input_ids) != self.tokenizer.vocab[self.tokenizer.pad_token]).float()
        }