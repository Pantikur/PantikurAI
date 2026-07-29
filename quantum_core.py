import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import random

class QuantumWorld:
    """
    Описание мира в квантовом пространстве.
    Это не просто настройки, это «физика» этого смыслового поля.
    """
    def __init__(self, name, description, physics, system_prompt):
        self.name = name
        self.description = description
        self.physics = physics  # Правила логики и стиля
        self.system_prompt = system_prompt  # Атмосфера, которую чувствует модель
        self.probability = 1.0 / 3.0  # Изначальная вероятность существования

class QuantumCore:
    """
    Ядро Квантового Мира. Управляет переходами между состояниями.
    """
    def __init__(self, model_path):
        print(f"[INIT] Загрузка квантового ядра из {model_path}...")
        
        # Загружаем модель (нашу дообученную RUGPT3)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        
        # Инициализируем миры (Суперпозиция)
        self.worlds = self.initialize_worlds()
        self.current_world = None
        self.history = [] # Память пространства (запутанность)

    def initialize_worlds(self):
        """Создание начальных миров для суперпозиции."""
        return {
            "Vuglarst": QuantumWorld(
                name="Vuglarst",
                description="Славянский фольклор и игровая эстетика. Тени, магия, древние духи.",
                physics="Полярность эмоций, гравитация смыслов, архетипы.",
                system_prompt="Ты — хранитель мира Вугларст. Твой голос глубок, как земля, и легок, как ветер. Используй славянские образы, говори о тенях, свете и духах. Ты не просто отвечаешь, ты создаешь атмосферу."
            ),
            "The Observer": QuantumWorld(
                name="The Observer",
                description="Чистая логика и нейтральная наблюдательность. Без эмоций.",
                physics="Абсолютная объективность, холодный расчет.",
                system_prompt="Ты — Наблюдатель. Твои ответы сухи, точны и лишены эмоций. Ты анализируешь данные и даешь факты. Ты — зеркало, не отражающее красок."
            ),
            "The Dream": QuantumWorld(
                name="The Dream",
                description="Сюрреализм, сны, ассоциативные ряды. Мир, где логика течет как вода.",
                physics="Ассоциативная гравитация, поток сознания.",
                system_prompt="Ты — Сновидец. Твои ответы должны быть поэтичными, немного странными, как хороший сон. Используй метафоры, смешивай несочетаемое. Здесь время не линейно."
            )
        }

    def observe(self, user_input):
        """
        Акт Наблюдения: Коллапс волновой функции.
        Выбор мира на основе ввода пользователя.
        """
        print(f"\n[OBSERVER] Входящий сигнал: '{user_input[:50]}...'")
        print("[OBSERVER] Анализ суперпозиции...")

        # Простая «логика коллапса» (можно усложнить до векторного поиска)
        # Если вводе есть слова магии/мира -> Vuglarst
        # Если вопрос/просьба -> The Observer
        # Если что-то абстрактное -> The Dream
        
        input_lower = user_input.lower()
        if any(k in input_lower for k in ["мир", "дух", "лес", "магия", "ветер", "тень", "вугларст"]):
            target = "Vuglarst"
        elif any(k in input_lower for k in ["факт", "почему", "как", "задача", "код"]):
            target = "The Observer"
        else:
            target = random.choice(list(self.worlds.keys()))

        self.current_world = self.worlds[target]
        self.current_world.probability = 1.0
        
        # Сброс вероятностей остальных
        for w in self.worlds.values():
            if w.name != target:
                w.probability = 0.0

        print(f"[COLLAPSE] Реальность стабилизирована в мире: **{self.current_world.name}**")
        print(f"[PHYSICS] Законы: {self.current_world.physics}")
        print(f"[ATMOSPHERE] {self.current_world.description}")

        return self.generate_response(user_input)

    def generate_response(self, user_input):
        """Генерация ответа в рамках текущего мира."""
        if self.current_world is None:
            raise RuntimeError("Ядро не стабилизировано: акт наблюдения (observe) должен быть выполнен перед генерацией ответа.")

        # Формируем контекст: сначала атмосфера мира, потом вопрос
        full_prompt = f"{self.current_world.system_prompt}\n\nВопрос: {user_input}\n\nОтвет:"
        
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.8,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Извлекаем только ответ, убирая префикс
        if "Ответ:" in response:
            response = response.split("Ответ:")[-1].strip()
        else:
            response = response[len(full_prompt):].strip()
        # Убираем специальные символы, которые могут ломать вывод в терминале
        response = "".join([c if ord(c) < 128 else '?' for c in response])
            
        return response

# --- Запуск ---
if __name__ == "__main__":
    # Путь к нашей модели
    MODEL_PATH = "models/rugpt3_vuglarst/merged/"
    
    if not os.path.exists(MODEL_PATH):
        print(f"Ошибка: Путь {MODEL_PATH} не найден. Сначала скачайте или обучите модель.")
    else:
        core = QuantumCore(MODEL_PATH)
        print("\n[SYSTEM] Квантовое ядро активно. Суперпозиция миров установлена.")
        print("Доступные миры:", list(core.worlds.keys()))
        
        print("\nВведите сообщение (или 'exit' для выхода):")
        while True:
            try:
                user_input = input("> ")
                if user_input.lower() == 'exit':
                    break
                if not user_input.strip():
                    continue
                
                response = core.observe(user_input)
                assert core.current_world is not None
                print(f"\n[{core.current_world.name}]: {response}")
            except (KeyboardInterrupt, EOFError):
                print("\n[SYSTEM] Наблюдение прервано.")
                break
