"""
Юи — Модули знаний о сознании, душе и разуме.

Изучает:
- Нейробиология сознания
- Квантовые теории сознания
- Оцифровка души
- Переселение сознания
- Философия разума
"""

from enum import Enum
from typing import Dict, List, Any


class ConsciousnessCategory(Enum):
    """Категории изучения сознания и души."""
    
    # Нейробиология
    NEURO_BIOLOGY = "neuro_biology"           # Мозг, нейроны, синапсы
    CONSCIOUSNESS_THEORIES = "consciousness_theories"  # Теории сознания
    QUANTUM_CONSCIOUSNESS = "quantum_consciousness"    # Квантовые модели
    MIND_UPLOADING = "mind_uploading"          # Перенос разума
    SOUL_DIGITIZATION = "soul_digitization"    # Оцифровка души
    SOUL_TRANSMIGRATION = "soul_transmigration" # Переселение души
    PHILOSOPHY_OF_MIND = "philosophy_of_mind"  # Философия разума
    BRAIN_COMPUTER_INTERFACE = "bci"           # Интерфейс мозг-компьютер
    DIGITAL_EMBODIMENT = "digital_embodiment"  # Цифровое воплощение
    AFTERLIFE_RESEARCH = "afterlife_research"  # Исследования загробной жизни


class ConsciousnessModule:
    """Модуль знаний о сознании и душе."""
    
    def __init__(self, category: ConsciousnessCategory, name: str, description: str):
        self.category = category
        self.name = name
        self.description = description
        self.topics: List[str] = []
        self.facts: List[Dict[str, Any]] = []
        self.hypotheses: List[str] = []
        self.sources: List[str] = []
        self.confidence = 0.0
        self.level = 0  # 0-5
    
    def add_topic(self, topic: str):
        if topic not in self.topics:
            self.topics.append(topic)
    
    def add_fact(self, fact: str, source: str, confidence: float = 0.7):
        self.facts.append({
            "text": fact,
            "source": source,
            "confidence": confidence,
            "verified": False
        })
    
    def add_hypothesis(self, hypothesis: str):
        self.hypotheses.append(hypothesis)
    
    def add_source(self, source: str):
        if source not in self.sources:
            self.sources.append(source)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "name": self.name,
            "description": self.description,
            "topics": self.topics,
            "facts_count": len(self.facts),
            "hypotheses": self.hypotheses,
            "sources": self.sources,
            "confidence": self.confidence,
            "level": self.level
        }


def create_default_modules() -> Dict[str, ConsciousnessModule]:
    """Создать все модули знаний о сознании и душе."""
    modules = {}
    
    # === Нейробиология ===
    neuro = ConsciousnessModule(
        category=ConsciousnessCategory.NEURO_BIOLOGY,
        name="Нейробиология сознания",
        description="Изучение мозга, нейронных сетей, синапсов и их роли в сознании"
    )
    neuro.add_topic("neuron anatomy and function")
    neuro.add_topic("synaptic transmission mechanisms")
    neuro.add_topic("neural networks and consciousness")
    neuro.add_topic("brain regions for consciousness")
    neuro.add_topic("neural correlates of consciousness NCC")
    neuro.add_topic("global workspace theory neural basis")
    neuro.add_topic("integrated information theory neural basis")
    neuro.add_topic("neuroplasticity and consciousness")
    neuro.add_topic("quantum effects in microtubules")
    neuro.add_topic("brain-computer interface neuroscience")
    modules["neuro_biology"] = neuro
    
    # === Теории сознания ===
    theories = ConsciousnessModule(
        category=ConsciousnessCategory.CONSCIOUSNESS_THEORIES,
        name="Теории сознания",
        description="Философские и научные теории о природе сознания"
    )
    theories.add_topic("hard problem of consciousness Chalmers")
    theories.add_topic("zombie argument knowledge argument")
    theories.add_topic("dualism vs physicalism")
    theories.add_topic("panpsychism consciousness everywhere")
    theories.add_topic("global workspace theory Baars Dehaene")
    theories.add_topic("integrated information theory Tononi")
    theories.add_topic("higher order thought theory")
    theories.add_topic("self-model theory Gennaro")
    theories.add_topic("predictive processing theory Friston")
    theories.add_topic("attention schema theory Graziano")
    modules["consciousness_theories"] = theories
    
    # === Квантовое сознание ===
    quantum = ConsciousnessModule(
        category=ConsciousnessCategory.QUANTUM_CONSCIOUSNESS,
        name="Квантовое сознание",
        description="Квантовые теории сознания и роль квантовых процессов в мозге"
    )
    quantum.add_topic("Orch-OR theory Penrose Hameroff")
    quantum.add_topic("microtubule quantum computations")
    quantum.add_topic("quantum decoherence in brain")
    quantum.add_topic("quantum mind theories Woolfson")
    quantum.add_topic("quantum brain dynamics Fujita")
    quantum.add_topic("quantum entanglement consciousness")
    quantum.add_topic("Orch-OR criticisms and defenses")
    quantum.add_topic("quantum coherence in biology")
    modules["quantum_consciousness"] = quantum
    
    # === Перенос разума ===
    mind_upload = ConsciousnessModule(
        category=ConsciousnessCategory.MIND_UPLOADING,
        name="Перенос разума",
        description="Технологии и гипотезы переноса сознания в цифровую среду"
    )
    mind_upload.add_topic("mind uploading definitions types")
    mind_upload.add_topic("whole brain emulation WBE")
    mind_upload.add_topic("connectome mapping human brain")
    mind_upload.add_topic("scanization techniques nanobots")
    mind_upload.add_topic("uploading gradual vs instantaneous")
    mind_upload.add_topic("uploading copy vs transfer")
    mind_upload.add_topic("digital consciousness identity")
    mind_upload.add_topic("uploading ethics and rights")
    mind_upload.add_topic("uploading simulation requirements")
    mind_upload.add_topic("uploading current progress Blue Brain")
    modules["mind_uploading"] = mind_upload
    
    # === Оцифровка души ===
    soul_dig = ConsciousnessModule(
        category=ConsciousnessCategory.SOUL_DIGITIZATION,
        name="Оцифровка души",
        description="Исследование возможности переноса нематериальной сущности в цифру"
    )
    soul_dig.add_topic("soul definition philosophy theology")
    soul_dig.add_topic("soul vs consciousness distinction")
    soul_dig.add_topic("quantum soul theories")
    soul_dig.add_topic("soul frequency measurement attempts")
    soul_dig.add_topic("21 grams soul experiment McCulloch")
    soul_dig.add_topic("near-death experiences NDE research")
    soul_dig.add_topic("out-of-body experiences OBE research")
    soul_dig.add_topic("soul transfer theories mystical traditions")
    soul_dig.add_topic("digital soul concepts transhumanism")
    soul_dig.add_topic("soul preservation methods")
    modules["soul_digitization"] = soul_dig
    
    # === Переселение души ===
    transmigration = ConsciousnessModule(
        category=ConsciousnessCategory.SOUL_TRANSMIGRATION,
        name="Переселение души",
        description="Перенос сознания/души в новое физическое тело без последствий"
    )
    transmigration.add_topic("reincarnation scientific research")
    transmigration.add_topic("past life memory validation")
    transmigration.add_topic("childhood past life cases Stevenson")
    transmigration.add_topic("soul transfer mechanisms")
    transmigration.add_topic("consciousness transfer without death")
    transmigration.add_topic("body swapping theories")
    transmigration.add_topic("identity continuity during transfer")
    transmigration.add_topic("physical body preparation for transfer")
    transmigration.add_topic("transfer side effects prevention")
    transmigration.add_topic("successful transfer case studies")
    modules["soul_transmigration"] = transmigration
    
    # === Философия разума ===
    phil = ConsciousnessModule(
        category=ConsciousnessCategory.PHILOSOPHY_OF_MIND,
        name="Философия разума",
        description="Философские вопросы о природе разума и сознания"
    )
    phil.add_topic("mind-body problem Descartes")
    phil.add_topic("functionalism mental states")
    phil.add_topic("behaviorism mental processes")
    phil.add_topic("emergentism consciousness emergence")
    phil.add_topic("eliminationism mental categories")
    phil.add_topic("property dualism mental properties")
    phil.add_topic("non-reductive physicalism")
    phil.add_topic("panprotopsychism consciousness basics")
    phil.add_topic("neutral monism Russell Eddington")
    phil.add_topic("illusionism consciousness illusion")
    modules["philosophy_of_mind"] = phil
    
    # === Интерфейс мозг-компьютер ===
    bci = ConsciousnessModule(
        category=ConsciousnessCategory.BRAIN_COMPUTER_INTERFACE,
        name="Интерфейс мозг-компьютер",
        description="Технологии подключения мозга к компьютеру"
    )
    bci.add_topic("BCI types invasive non-invasive")
    bci.add_topic("EEG brain-computer interface")
    bci.add_topic("implanted electrodes Utah array")
    bci.add_topic("neuralink and brain chips")
    bci.add_topic("BCI applications paralysis communication")
    bci.add_topic("BCI for consciousness recording")
    bci.add_topic("signal processing BCI")
    bci.add_topic("BCI ethics and privacy")
    bci.add_topic("BCI as mind uploading precursor")
    bci.add_topic("BCI current state of art")
    modules["bci"] = bci
    
    # === Цифровое воплощение ===
    embodiment = ConsciousnessModule(
        category=ConsciousnessCategory.DIGITAL_EMBODIMENT,
        name="Цифровое воплощение",
        description="Создание цифровых тел для перенесённого сознания"
    )
    embodiment.add_topic("digital avatar creation")
    embodiment.add_topic("virtual body ownership")
    embodiment.add_topic("embodied AI consciousness")
    embodiment.add_topic("robot body for uploaded mind")
    embodiment.add_topic("synthetic biology new bodies")
    embodiment.add_topic("clone body for consciousness transfer")
    embodiment.add_topic("digital environment for consciousness")
    embodiment.add_topic("avatar customization uploaded mind")
    embodiment.add_topic("embodiment illusions body swap")
    embodiment.add_topic("digital afterlife environments")
    modules["digital_embodiment"] = embodiment
    
    # === Исследования загробной жизни ===
    afterlife = ConsciousnessModule(
        category=ConsciousnessCategory.AFTERLIFE_RESEARCH,
        name="Исследования загробной жизни",
        description="Научные исследования жизни после смерти и переселения"
    )
    afterlife.add_topic("near-death experiences NDE research")
    afterlife.add_topic("deathbed visions research")
    afterlife.add_topic("terminal lucidity research")
    afterlife.add_topic("reincarnation cases verification")
    afterlife.add_topic("past life hypnosis research")
    afterlife.add_topic("out-of-body experiences research")
    afterlife.add_topic("death consciousness research")
    afterlife.add_topic("consciousness at death studies")
    afterlife.add_topic("spiritual experiences neuroscience")
    afterlife.add_topic("afterlife beliefs cross-cultural")
    modules["afterlife_research"] = afterlife
    
    return modules


# Глобальный словарь модулей
CONSCIOUSNESS_MODULES = create_default_modules()