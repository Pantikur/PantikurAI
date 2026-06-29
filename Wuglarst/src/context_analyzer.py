# Wuglarst/src/context_analyzer.py
# Анализ контекста истории сообщений и логики диалога

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextAnalyzer:
    """
    Анализирует контекст истории сообщений:
    - Темы и их изменение
    - Эмоциональную динамику
    - Логику и причинно-следственные связи
    - Повторяющиеся паттерны
    """
    
    def __init__(self):
        self.context_history: List[Dict[str, Any]] = []
        self.topic_memory: Dict[str, float] = {}  # topic -> last_seen_timestamp
        self.emotion_timeline: List[Dict[str, Any]] = []
        self.logic_patterns: List[Dict[str, Any]] = []
        
        # Ключевые слова для тем
        self.topic_keywords = {
            "работа": ["работа", "офис", "начальник", "коллеги", "проект", "задача", "дедлайн"],
            "отношения": ["отношения", "любимый", "любимая", "парень", "девушка", "развод", "свадьба", "свидание"],
            "семья": ["семья", "родители", "дети", "брат", "сестра", "мама", "папа"],
            "здоровье": ["здоровье", "боль", "врач", "лекарство", "симптом", "диагноз"],
            "учеба": ["учеба", "школа", "универ", "экзамен", "курсовая", "диплом"],
            "хобби": ["хобби", "интерес", "увлечение", "спорт", "музыка", "книги", "игры"],
            "финансы": ["деньги", "зарплата", "кредит", "долг", "покупка", "бюджет"],
            "путешествия": ["путешествие", "отпуск", "страна", "город", "отель", "билет"],
            "еда": ["еда", "рецепт", "готовить", "ресторан", "кафе", "ужин", "завтрак"],
            "технологии": ["технологии", "компьютер", "телефон", "программа", "интернет", "гаджет"],
            "эмоции": ["грусть", "радость", "злость", "страх", "тревога", "счастье", "депрессия"],
            "цели": ["цель", "план", "мечта", "желание", "намерение", "стремление"],
            "воспоминания": ["вспоминаю", "раньше", "ранее", "в детстве", "помню", "было"],
            "предсказания": ["будущее", "завтра", "скоро", "ожидание", "прогноз"],
        }
        
        # Эмоциональные маркеры
        self.emotion_markers = {
            "positive": ["😊", "❤️", "🙂", "классно", "отлично", "прекрасно", "доволен", "счастлив", "радостно"],
            "negative": ["😢", "😡", "😰", "грустно", "плохо", "злюсь", "тревожно", "устал", "разочарован"],
            "neutral": ["😐", "нормально", "так себе", "без разницы", "не знаю", "может быть"],
        }
        
        # Логические связки
        self.logic_connectors = {
            "причина": ["потому что", "поскольку", "так как", "из-за", "следовательно", "поэтому"],
            "условие": ["если", "когда", "при условии", "если бы", "в случае"],
            "противопоставление": ["но", "однако", "зато", "вместо", "несмотря на", "хотя"],
            "последовательность": ["затем", "потом", "далее", "в конце концов", "в итоге"],
            "усиление": ["особенно", "в частности", "более того", "к тому же", "кроме того"],
            "вопрос": ["почему", "зачем", "как", "когда", "где", "кто", "что"],
        }
    
    def analyze_context(self, messages: List[Dict[str, str | bool]]) -> Dict[str, Any]:
        """
        Полный анализ контекста диалога.
        
        Возвращает:
        - topics: текущие темы
        - emotion_trend: эмоциональный тренд
        - logic_summary: логическая структура
        - patterns: выявленные паттерны
        - suggestions: рекомендации для ответа
        """
        if not messages:
            return self._empty_analysis()
        
        # Извлекаем тексты сообщений
        texts: List[str] = [str(msg.get("message", "")) for msg in messages if msg.get("message")]
        
        if not texts:
            return self._empty_analysis()
        
        # 1. Анализ тем
        topics = self._analyze_topics(texts)
        
        # 2. Анализ эмоций
        emotion_trend = self._analyze_emotions(texts)
        
        # 3. Анализ логики
        logic_summary = self._analyze_logic(texts)
        
        # 4. Выявление паттернов
        patterns = self._detect_patterns(texts)
        
        # 5. Рекомендации
        suggestions = self._generate_suggestions(topics, emotion_trend, logic_summary, patterns)
        
        result = {
            "topics": topics,
            "emotion_trend": emotion_trend,
            "logic_summary": logic_summary,
            "patterns": patterns,
            "suggestions": suggestions,
            "message_count": len(messages),
            "analyzed_at": datetime.now().isoformat(),
        }
        
        logger.info(f"📊 Context analyzed: {len(topics)} topics, emotion={emotion_trend['dominant']}, logic={logic_summary['type']}")
        return result
    
    def _analyze_topics(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Анализ тем в сообщениях."""
        topic_scores = {}
        
        for text in texts:
            text_lower = text.lower()
            for topic, keywords in self.topic_keywords.items():
                score = sum(1 for kw in keywords if kw in text_lower)
                if score > 0:
                    topic_scores[topic] = topic_scores.get(topic, 0) + score
        
        # Сортируем по убыванию
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"topic": topic, "score": score, "relevance": score / len(texts)}
            for topic, score in sorted_topics[:5]  # Топ-5 тем
        ]
    
    def _analyze_emotions(self, texts: List[str]) -> Dict[str, Any]:
        """Анализ эмоционального тона."""
        emotion_counts = {"positive": 0, "negative": 0, "neutral": 0}
        emotion_details = []
        
        for i, text in enumerate(texts):
            text_lower = text.lower()
            detected = []
            
            for emotion, markers in self.emotion_markers.items():
                count = sum(1 for marker in markers if marker in text_lower)
                if count > 0:
                    emotion_counts[emotion] += count
                    detected.append((emotion, count))
            
            if detected:
                emotion_details.append({
                    "message_index": i,
                    "detected": detected,
                    "dominant": max(detected, key=lambda x: x[1])[0]
                })
        
        # Определяем доминирующую эмоцию
        dominant = max(emotion_counts.items(), key=lambda x: x[1])[0]
        total = sum(emotion_counts.values())
        
        return {
            "dominant": dominant,
            "distribution": {k: v / max(total, 1) for k, v in emotion_counts.items()},
            "details": emotion_details,
            "trend": self._calculate_emotion_trend(emotion_details)
        }
    
    def _calculate_emotion_trend(self, details: List[Dict]) -> str:
        """Определяет тренд эмоций (растёт/падает/стабильно)."""
        if len(details) < 2:
            return "insufficient_data"
        
        # Сравниваем первую и последнюю эмоции
        first = details[0]["dominant"]
        last = details[-1]["dominant"]
        
        if first == last:
            return "stable"
        elif first == "negative" and last in ["positive", "neutral"]:
            return "improving"
        elif first in ["positive", "neutral"] and last == "negative":
            return "worsening"
        else:
            return "fluctuating"
    
    def _analyze_logic(self, texts: List[str]) -> Dict[str, Any]:
        """Анализ логической структуры."""
        logic_types = {
            "reasoning": 0,  # причинно-следственные связи
            "questioning": 0,  # вопросы
            "contradiction": 0,  # противоречия
            "sequence": 0,  # последовательность
            "conditional": 0,  # условия
        }
        
        logic_examples = []
        
        for i, text in enumerate(texts):
            text_lower = text.lower()
            
            for logic_type, connectors in self.logic_connectors.items():
                count = sum(1 for conn in connectors if conn in text_lower)
                if count > 0:
                    logic_types[logic_type] += count
                    if len(logic_examples) < 3:
                        logic_examples.append({
                            "message_index": i,
                            "type": logic_type,
                            "example": text[:100]
                        })
        
        dominant_logic = max(logic_types.items(), key=lambda x: x[1])[0]
        
        return {
            "type": dominant_logic,
            "distribution": logic_types,
            "examples": logic_examples,
            "complexity": sum(logic_types.values()) / max(len(texts), 1)
        }
    
    def _detect_patterns(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Выявление повторяющихся паттернов."""
        patterns = []
        
        # 1. Повторяющиеся слова
        word_counts = {}
        for text in texts:
            words = text.lower().split()
            for word in words:
                if len(word) > 3:  # игнорируем короткие слова
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        frequent_words = [(w, c) for w, c in word_counts.items() if c >= 2]
        if frequent_words:
            patterns.append({
                "type": "repeated_words",
                "words": [{"word": w, "count": c} for w, c in frequent_words[:5]],
                "significance": "frequent_themes"
            })
        
        # 2. Вопросы и утверждения
        question_count = sum(1 for t in texts if "?" in t)
        statement_count = len(texts) - question_count
        
        if question_count > 0:
            patterns.append({
                "type": "question_ratio",
                "questions": question_count,
                "statements": statement_count,
                "ratio": question_count / max(len(texts), 1),
                "significance": "inquisitive" if question_count > statement_count else "declarative"
            })
        
        # 3. Длина сообщений
        lengths = [len(t) for t in texts]
        avg_length = sum(lengths) / max(len(lengths), 1)
        
        if lengths and max(lengths) - min(lengths) > 50:
            patterns.append({
                "type": "length_variance",
                "average": avg_length,
                "min": min(lengths),
                "max": max(lengths),
                "significance": "variable_engagement"
            })
        
        return patterns
    
    def _generate_suggestions(self, topics: List[Dict], emotion_trend: Dict, 
                             logic_summary: Dict, patterns: List[Dict]) -> List[str]:
        """Генерация рекомендаций для ответа."""
        suggestions = []
        
        # Рекомендации по темам
        if topics:
            main_topic = topics[0]["topic"]
            suggestions.append(f"Сфокусируйтесь на теме '{main_topic}'")
        
        # Рекомендации по эмоциям
        if emotion_trend["dominant"] == "negative":
            suggestions.append("Проявите эмпатию и поддержку")
        elif emotion_trend["dominant"] == "positive":
            suggestions.append("Поддержите позитивный настрой")
        
        if emotion_trend["trend"] == "worsening":
            suggestions.append("Эмоциональный фон ухудшается — будьте осторожны")
        elif emotion_trend["trend"] == "improving":
            suggestions.append("Ситуация улучшается — поощряйте позитив")
        
        # Рекомендации по логике
        if logic_summary["type"] == "questioning":
            suggestions.append("Пользователь задаёт вопросы — дайте развёрнутые ответы")
        elif logic_summary["type"] == "reasoning":
            suggestions.append("Пользователь рассуждает — поддержите логическую цепочку")
        
        # Рекомендации по паттернам
        for pattern in patterns:
            if pattern["type"] == "repeated_words":
                words = [w["word"] for w in pattern["words"][:3]]
                suggestions.append(f"Повторяются слова: {', '.join(words)} — затроньте эту тему")
        
        return suggestions[:5]  # Максимум 5 рекомендаций
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Возвращает пустой анализ."""
        return {
            "topics": [],
            "emotion_trend": {"dominant": "neutral", "distribution": {}, "trend": "insufficient_data"},
            "logic_summary": {"type": "unknown", "distribution": {}, "complexity": 0},
            "patterns": [],
            "suggestions": [],
            "message_count": 0,
            "analyzed_at": None,
        }
    
    def update_memory(self, context_analysis: Dict[str, Any]):
        """Обновляет память о контексте."""
        self.context_history.append(context_analysis)
        
        # Ограничиваем историю последними 10 анализами
        if len(self.context_history) > 10:
            self.context_history = self.context_history[-10:]
        
        # Обновляем тему
        for topic in context_analysis.get("topics", []):
            self.topic_memory[topic["topic"]] = datetime.now().timestamp()
        
        # Обновляем эмоциональную временную шкалу
        if context_analysis.get("emotion_trend"):
            self.emotion_timeline.append({
                "timestamp": datetime.now().isoformat(),
                "dominant": context_analysis["emotion_trend"]["dominant"],
                "trend": context_analysis["emotion_trend"]["trend"],
            })
            # Ограничиваем шкалу
            if len(self.emotion_timeline) > 20:
                self.emotion_timeline = self.emotion_timeline[-20:]
        
        logger.info(f"🧠 Context memory updated: {len(self.context_history)} analyses, "
                   f"{len(self.topic_memory)} topics, {len(self.emotion_timeline)} emotion points")
