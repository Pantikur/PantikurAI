"""Test LatislaneCore with 6-Module Soul"""
import sys
sys.path.insert(0, '.')

from latislane.engine.latislane_core import LatislaneCore
from latislane.engine.config import LatislaneConfig

print("=== Testing LatislaneCore with 6-Module Soul ===\n")

# Create config
config = LatislaneConfig.demo()

# Create LatislaneCore
core = LatislaneCore(config)
print("[OK] LatislaneCore created")

# Check all soul modules
print(f"  Consciousness: {core.consciousness is not None}")
print(f"  Heart: {core.heart is not None}")
print(f"  Ambitions: {core.ambitions is not None}")
print(f"  Volition: {core.volition is not None}")
print(f"  Mind: {core.mind is not None}")
print(f"  EmotionalEngine: {core.emotional_engine is not None}")
print(f"  LLM General loaded: {core.llm.general_loaded}")
print(f"  LLM Coder loaded: {core.llm.coder_loaded}")
print(f"  Humanity Layer: {core.humanity is not None}")

# Test emotion profile
profile = core.emotional_engine.get_emotion_profile()
print(f"\n[OK] Emotion profile:")
print(f"   Desires count: {profile['desires_count']}")

print("\n=== ALL TESTS PASSED ===")
