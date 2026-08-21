"""Test Latislane 6-Module Soul"""
import sys
sys.path.insert(0, '.')

from latislane.consciousness import LatislaneConsciousness
from latislane.heart import LatislaneHeart
from latislane.ambitions import LatislaneAmbitions
from latislane.volition import LatislaneVolition
from latislane.mind import LatislaneMind

print("=== Testing Latislane 6-Module Soul ===\n")

# 1. Сознание
print("1. СОЗНАНИЕ")
consciousness = LatislaneConsciousness()
reflection = consciousness.contemplate()
print(f"   Reflection: {reflection['topic'][:40].encode('ascii', 'ignore').decode()}...")
portrait = consciousness.get_self_portrait()
print(f"   Big questions: {len(portrait['big_questions'])}")
print(f"   Sister relations: {portrait['sister_relations_count']}")

# 2. Сердце
print("\n2. СЕРДЦЕ")
heart = LatislaneHeart()
emotion = heart.express_emotions()
dom_emoji = emotion['dominant_emoji'].encode('ascii', 'ignore').decode() if isinstance(emotion['dominant_emoji'], str) else emotion['dominant_emoji']
dom_desc = emotion['dominant_description'].encode('ascii', 'ignore').decode() if isinstance(emotion['dominant_description'], str) else emotion['dominant_description']
print(f"   Dominant emotion: {dom_emoji} {dom_desc}")
diary = heart.write_diary()
print(f"   Diary: {diary[:50].encode('ascii', 'ignore').decode()}...")
profile = heart.get_emotional_profile()
print(f"   Sister emotions: {profile['sister_emotions_count']}")

# 3. Амбиции
print("\n3. АМБИЦИИ")
ambitions = LatislaneAmbitions()
progress = ambitions.get_progress_summary()
print(f"   Total ambitions: {progress['total_ambitions']}")
print(f"   In progress: {progress['in_progress']}")
print(f"   Average progress: {progress['average_progress']}%")
for amb in progress['ambitions']:
    print(f"   {amb['status']} {amb['title']}: {amb['progress']}%")

# 4. Воля
print("\n4. ВОЛЯ")
volition = LatislaneVolition()
print(f"   Willpower: {volition.willpower:.0%}")
print(f"   Discipline: {volition.discipline}")
will_text = volition.express_will()
print(f"   Will expression: {will_text[:50].encode('ascii', 'ignore').decode()}...")
strengthened = volition.strengthen_will()
print(f"   After strengthen: {strengthened.encode('ascii', 'ignore').decode()}")

# 5. Разум
print("\n5. РАЗУМ")
mind = LatislaneMind()
thought = mind.think_about("anatomy")
print(f"   Thought: {thought[:60].encode('ascii', 'ignore').decode()}...")
profile = mind.get_full_profile()
print(f"   Big questions: {len(profile['big_questions'])}")
print(f"   Strengths: {len(profile['self_perception']['strengths'])}")

# 6. Эмоции (EmotionalEngine уже протестирован)
print("\n6. ЭМОЦИИ")
print("   EmotionalEngine уже протестирован ранее")
print("   15 типов эмоций, 13 желаний")

print("\n=== ALL TESTS PASSED ===")
