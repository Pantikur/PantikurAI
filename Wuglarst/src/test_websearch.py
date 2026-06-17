
# test_websearch.py
# Работает по команде python test_websearch.py

from web_search import WebSearch, SimpleTrainer, TestResult
from typing import List
import os
import json
from collections import Counter

def main():
    # 🔧 Инициализация
    print("🚀 Запуск WebSearch теста...")
    ws = WebSearch()
    trainer = SimpleTrainer(log_file="../../data/training_data.jsonl")
    ws.set_trainer(trainer)
    ws.init_driver()

    if not ws.driver:
        print("❌ Ошибка: драйвер не инициализирован")
        return

    try:
        # 🔎 Тестируемые слова (можно добавить/убрать)
        words = ["кот", "самолёт", "тюлень", "воскресенье", "математика"]
        timeout = 10.0

        print(f"📊 Старт теста {len(words)} слов, timeout={timeout} сек...")
        results: List[TestResult] = ws.run_test(words, timeout=timeout)

        # 📊 Вывод результатов
        print("\n📈 Результаты:")
        for r in results:
            print(f"  {r.word}: {'✅' if r.success else '❌'} (score={r.score:.1f}, time={r.time_ms}мс, source={r.source})")
            if not r.success and r.time_ms > 0:
                print(f"    ⚠️ Ошибка: {r.error}")

        # 💾 Сохранение кэша
        ws.save_knowledge_cache(cache_file="../../data/knowledge_cache.json")

        # 🧠 Статистика по дообучению (если есть данные)
        trainer_file = "../../data/training_data.jsonl"
        if os.path.exists(trainer_file):
            with open(trainer_file, "r", encoding="utf-8") as f:
                records = [json.loads(line) for line in f]

            successful = [r for r in records if r["definition"]]
            print(f"\n🧠 Статистика тренера ({len(successful)} успешных запросов):")
            if successful:
                # Считаем популярные веса
                feature_counts = Counter()
                for r in successful:
                    if r["weights"]:
                        for k, v in r["weights"].items():
                            if isinstance(v, bool):
                                feature_counts[k] += v

                print("  🔑 Топ признаков:")
                for k, v in feature_counts.most_common(5):
                    print(f"    {k}: {v}")

        print("\n✅ Тест завершён успешно")

    finally:
        # 🧹 Закрытие драйвера
        if ws.driver:
            ws.driver.quit()
        print("🧹 Драйвер закрыт")

    
if __name__ == "__main__":
    main()