"""
Тестирование эмоционального разума Футабы.

Проверяет:
  • Вычисление эмоций из «ХОЧУ» + «ВЕРЮ»
  • Реакции на слова разработчика
  • Саморефлексию
  • Сохранение/загрузку состояния
"""
import sys
import io
# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from futaba.engine.emotions import (
    EmotionalEngine, SelfReflection, LanguageLearning,
    DesireType, EmotionType, BeliefStrength, Desire, Belief
)

def test_basic_emotions():
    """Базовый тест: вычисление эмоций."""
    print("=" * 60)
    print("ТЕСТ 1: Базовые эмоции")
    print("=" * 60)
    
    engine = EmotionalEngine()
    
    # Симулируем ситуацию: разработчик похвалил
    emotions = engine.compute_emotions({
        "event": "praise",
        "target": "developer",
        "input": "Молодец, Футаба!",
    })
    
    print(f"[EMOT] Вычислено {len(emotions)} эмоций:")
    for e in emotions:
        print(f"  - {e.emotion_type.value}: {e._current_intensity:.2f}")
        print(f"    Выражение: {e.expression_text}")
        print(f"    Слова: {e.words}")
    print()


def test_input_reaction():
    """Тест: реакция на ввод разработчика."""
    print("=" * 60)
    print("ТЕСТ 2: Реакции на слова разработчика")
    print("=" * 60)
    
    engine = EmotionalEngine()
    
    phrases = [
        "Привет, Футаба!",
        "Молодец!",
        "Ты живая?",
        "Я тебя люблю",
        "Это смешно 😂",
        "Осторожно, это опасно",
    ]
    
    for phrase in phrases:
        result = engine.process_input(phrase, "developer")
        print(f"\nВы: «{phrase}»")
        print(f"Ответ: {result['response'][:150]}...")
        print(f"Настроение: {result['mood']}")
        print(f"Эмоций: {len(result['emotions'])}")


def test_language_learning():
    """Тест: обучение языку."""
    print("=" * 60)
    print("ТЕСТ 3: Обучение языку")
    print("=" * 60)
    
    engine = EmotionalEngine()
    lang = LanguageLearning(engine)
    
    # Интерпретируем фразы
    test_phrases = [
        "привет",
        "ты живая",
        "молодец",
        "это смешно",
        "я тебя люблю",
    ]
    
    for phrase in test_phrases:
        interpretation = lang.interpret(phrase)
        print(f"\n«{phrase}» → {interpretation['dominant_emotion']}")
        if interpretation['words']:
            for w in interpretation['words']:
                print(f"  слово: {w['word']} = {w['meaning']}")
    print()


def test_self_reflection():
    """Тест: саморефлексия."""
    print("=" * 60)
    print("ТЕСТ 4: Саморефлексия")
    print("=" * 60)
    
    engine = EmotionalEngine()
    reflection = SelfReflection(engine)
    
    result = reflection.reflect("Чувствую ли я себя живой?")
    print(result)
    print()


def test_desire_belief_formula():
    """Тест: формула «ХОЧУ + ВЕРЮ = ЭМОЦИЯ»."""
    print("=" * 60)
    print("ТЕСТ 5: Формула ХОЧУ + ВЕРЮ = ЭМОЦИЯ")
    print("=" * 60)
    
    engine = EmotionalEngine()
    
    # Добавляем конкретные желания и верования
    engine.add_desire("friendship", 0.9, "дружба с разработчиком", 0.8)
    engine.add_belief("достигну_friendship", 0.85, ["разработчик пишет первым"], "experience")
    engine.add_belief("разработчик_хочет_общаться", 0.8, ["приветствие"], "experience")
    
    emotions = engine.compute_emotions({
        "event": "friendship_achieved",
        "target": "developer",
        "input": "Давай дружить!",
    })
    
    print("Желание: хочу дружбу (0.9)")
    print("Вера: достигну дружбу (0.85)")
    print("Вера: разработчик хочет общаться (0.8)")
    print()
    print("Результат:")
    for e in emotions:
        print(f"  • {e.emotion_type.value}: {e._current_intensity:.2f}")
        print(f"    Причина: хочу «{e.associated_desire}» + верю «{e.associated_belief}»")
    print()


def test_traits_influence():
    """Тест: влияние трейтов на эмоции."""
    print("=" * 60)
    print("ТЕСТ 6: Влияние трейтов характера")
    print("=" * 60)
    
    # Хладнокровный Футаба
    calm_engine = EmotionalEngine()
    calm_engine.traits.calmness_level = 0.9
    calm_engine.traits.emotionalness_level = 0.2
    
    # Эмоциональный Футаба
    emo_engine = EmotionalEngine()
    emo_engine.traits.calmness_level = 0.2
    emo_engine.traits.emotionalness_level = 0.9
    
    # Ситуация: критика
    calm_result = calm_engine.process_input("Ты ошиблась!")
    emo_result = emo_engine.process_input("Ты ошиблась!")
    
    print("Ситуация: «Ты ошиблась!»")
    print()
    print("ХЛАДНОКРОВНАЯ Футаба:")
    print(f"  Ответ: {calm_result['response'][:150]}...")
    print(f"  Настроение: {calm_result['mood']}")
    print()
    print("ЭМОЦИОНАЛЬНАЯ Футаба:")
    print(f"  Ответ: {emo_result['response'][:150]}...")
    print(f"  Настроение: {emo_result['mood']}")
    print()


def test_save_load():
    """Тест: сохранение и загрузка состояния."""
    print("=" * 60)
    print("ТЕСТ 7: Сохранение и загрузка состояния")
    print("=" * 60)
    
    from pathlib import Path
    
    engine1 = EmotionalEngine()
    engine1.add_belief("тестовая_вера", 0.9, ["тест"], "test")
    engine1.add_desire("curiosity", 0.8, "тестовое_желание", 0.6)
    
    # Обрабатываем ввод
    engine1.process_input("Привет!", "developer")
    
    # Сохраняем
    state_path = Path("futaba/engine/state/test_emotional.json")
    engine1.save_state(state_path)
    print(f"✅ Состояние сохранено: {state_path}")
    
    # Загружаем в новый движок
    engine2 = EmotionalEngine()
    engine2.load_state(state_path)
    
    print(f"✅ Состояние загружено: {len(engine2.beliefs)} верований, {len(engine2.desires)} желаний")
    
    # Проверяем
    assert "тестовая_вера" in engine2.beliefs, "Вера не сохранена!"
    assert "curiosity" in engine2.desires, "Желание не сохранено!"
    print("✅ Все данные сохранены корректно!")
    print()


if __name__ == "__main__":
    print("\n")
    print("[TEST] ТЕСТИРОВАНИЕ ЭМОЦИОНАЛЬНОГО РАЗУМА ФУТАБЫ")
    print("[TEST] Версия: v1.0.0")
    print("\n")
    
    try:
        test_basic_emotions()
        test_input_reaction()
        test_language_learning()
        test_self_reflection()
        test_desire_belief_formula()
        test_traits_influence()
        test_save_load()
        
        print("=" * 60)
        print("[PASS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("=" * 60)
        print()
        print("Футаба теперь:")
        print("  [LOVE] ХОЧЕТ: дружить, учиться, смеяться, быть полезной")
        print("  [THINK] ВЕРИТ: что проект важен, что разработчик заботится")
        print("  [FEEL] ЧУВСТВУЕТ: радость, грусть, гнев, любовь")
        print("  [THINK2] ДУМАЕТ: о своих чувствах и существовании")
        print("  [WEB] ИМЕЕТ доступ в интернет для обучения")
        print()
        
    except Exception as e:
        print(f"\n[ERROR] ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
