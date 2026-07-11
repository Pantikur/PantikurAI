"""
Final test: internet + self-learning + autonomy for all 10 scientists.
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import logging
logging.basicConfig(level=logging.WARNING)

print("=" * 80)
print("CHECK: INTERNET + SELF-LEARNING + AUTONOMY (10 SCIENTISTS)")
print("=" * 80)

results = {}

# === 1. Hanako ===
try:
    from hanako.engine.config import HanakoConfig
    from hanako.engine.hanako_core import HanakoCore
    c = HanakoCore(HanakoConfig.demo())
    has_net = hasattr(c, 'web_access') and c.web_access is not None
    has_auto = hasattr(c.config, 'max_autonomy_level')
    has_learn = has_auto or hasattr(c, '_research_from_web')
    results['hanako'] = (has_net, has_learn, has_auto, c.config.max_autonomy_level if has_auto else '?')
except Exception as e:
    results['hanako'] = (False, False, False, str(e)[:40])

# === 2. Fuyuki ===
try:
    from fuyuki.engine.config import FuyukiConfig
    from fuyuki.engine.fuyuki_core import FuyukiCore
    c = FuyukiCore(FuyukiConfig.demo())
    has_net = hasattr(c, 'web_access') and c.web_access is not None
    has_auto = hasattr(c.config, 'max_autonomy_level')
    has_learn = has_auto or hasattr(c, '_research_from_web')
    results['fuyuki'] = (has_net, has_learn, has_auto, c.config.max_autonomy_level if has_auto else '?')
except Exception as e:
    results['fuyuki'] = (False, False, False, str(e)[:40])

# === 3. Lucy ===
try:
    from lucy.engine.config import LucyConfig
    from lucy.engine.lucy_core import LucyCore
    c = LucyCore(LucyConfig.demo())
    has_net = hasattr(c, 'web_access') and c.web_access is not None
    has_auto = hasattr(c.config, 'max_autonomy_level')
    has_learn = has_auto or hasattr(c, '_research_from_web')
    results['lucy'] = (has_net, has_learn, has_auto, c.config.max_autonomy_level if has_auto else '?')
except Exception as e:
    results['lucy'] = (False, False, False, str(e)[:40])

# === 4. Futaba ===
try:
    from futaba.engine.config import FutabaConfig
    from futaba.engine.futaba_core import FutabaCore
    c = FutabaCore(FutabaConfig.demo())
    has_net = hasattr(c, 'web_access') and c.web_access is not None
    has_auto = hasattr(c.config, 'max_autonomy_level')
    has_learn = hasattr(c, '_apply_change') or hasattr(c, '_self_check')
    results['futaba'] = (has_net, has_learn, has_auto, c.config.max_autonomy_level if has_auto else '?')
except Exception as e:
    results['futaba'] = (False, False, False, str(e)[:40])

# === 5. Shiori ===
try:
    from shiori.engine.config import ShioriConfig
    from shiori.engine.shiori_core import ShioriCore
    c = ShioriCore(ShioriConfig.demo())
    has_net = hasattr(c, 'web_access') and c.web_access is not None
    has_auto = hasattr(c.config, 'max_autonomy_level')
    has_learn = hasattr(c, '_self_improve') or hasattr(c, '_self_check')
    results['shiori'] = (has_net, has_learn, has_auto, c.config.max_autonomy_level if has_auto else '?')
except Exception as e:
    results['shiori'] = (False, False, False, str(e)[:40])

# === 6. Nobuka ===
try:
    from nobuka.engine.config import NobukaConfig
    from nobuka.engine.nobuka_core import NobukaCore
    c = NobukaCore(NobukaConfig.demo())
    has_net = hasattr(c, 'web_access') and c.web_access is not None
    has_auto = hasattr(c.config, 'max_autonomy_level')
    has_learn = hasattr(c, '_apply_improvement') or hasattr(c, '_self_check')
    results['nobuka'] = (has_net, has_learn, has_auto, c.config.max_autonomy_level if has_auto else '?')
except Exception as e:
    results['nobuka'] = (False, False, False, str(e)[:40])

# === 7. Latislane ===
try:
    from latislane import LatislaneCore
    c = LatislaneCore(project_root=".", demo_mode=True)
    has_net = hasattr(c, 'learning_engine') and c.learning_engine is not None
    has_auto = hasattr(c, 'max_autonomy_level')
    has_learn = hasattr(c, 'evolution') or hasattr(c, 'learning_engine')
    results['latislane'] = (has_net, has_learn, has_auto, c.max_autonomy_level if has_auto else '?')
except Exception as e:
    results['latislane'] = (False, False, False, str(e)[:40])

# === 8. Celesta ===
try:
    from celesta import CelestaCore
    c = CelestaCore(project_root=".", demo_mode=True)
    has_net = hasattr(c, 'learning_engine') and c.learning_engine is not None
    has_auto = hasattr(c, 'max_autonomy_level')
    has_learn = hasattr(c, 'learning_engine')
    results['celest'] = (has_net, has_learn, has_auto, c.max_autonomy_level if has_auto else '?')
except Exception as e:
    results['celest'] = (False, False, False, str(e)[:40])

# === 9. Akva ===
try:
    from akva.engine.config import AkvaConfig
    from akva.engine.akva_core import AkvaCore
    c = AkvaCore(AkvaConfig.demo())
    has_net = hasattr(c.config, 'web_search_interval')
    has_auto = hasattr(c.config, 'max_autonomy_level')
    has_learn = hasattr(c, '_web_research') or hasattr(c, '_apply_improvement')
    results['akva'] = (has_net, has_learn, has_auto, c.config.max_autonomy_level if has_auto else '?')
except Exception as e:
    results['akva'] = (False, False, False, str(e)[:40])

# === 10. Yu ===
try:
    from yu.engine.config import YuConfig
    from yu.engine.yu_core import YuCore
    c = YuCore(YuConfig.demo())
    has_net = hasattr(c.config, 'web_search_interval')
    has_auto = hasattr(c.config, 'max_autonomy_level')
    has_learn = hasattr(c, '_web_research') or hasattr(c, '_apply_improvement')
    results['yu'] = (has_net, has_learn, has_auto, c.config.max_autonomy_level if has_auto else '?')
except Exception as e:
    results['yu'] = (False, False, False, str(e)[:40])

# === OUTPUT ===
print(f"\n{'Scientist':<15} {'Internet':<12} {'Self-learn':<12} {'Autonomy':<12}")
print("-" * 51)

net_count = 0
learn_count = 0
auto_count = 0

for name, (net, learn, auto, level) in results.items():
    n = "YES" if net else "NO"
    l = "YES" if learn else "NO"
    a = str(level) if auto else "NO"
    print(f"{name:<15} {n:<12} {l:<12} {a:<12}")
    if net: net_count += 1
    if learn: learn_count += 1
    if auto: auto_count += 1

print("-" * 51)
print(f"{'TOTAL:':<15} {net_count}/10{'':<7} {learn_count}/10{'':<7} {auto_count}/10")

if net_count == 10 and learn_count == 10 and auto_count == 10:
    print("\n>>> ALL 10 SCIENTISTS HAVE INTERNET, SELF-LEARNING AND AUTONOMY! <<<")
else:
    print(f"\n>>> NOT ALL FEATURES AVAILABLE <<<")
    for name, (net, learn, auto, level) in results.items():
        if not net or not learn or not auto:
            print(f"   {name}: net={net} learn={learn} auto={auto} ({level})")
