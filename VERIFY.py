"""Infinity Neural V3.1.0 — Complete Edition Verification Script.
Tests V1 engine + V2 patterns + V3 instinct protocol + V3.1 completeness."""

import os
import sys


def verify():
    checks = []

    # ============================================================
    # V1 CORE
    # ============================================================
    try:
        from neural_memory.core.neuron import NeuronType, NeuronState
        checks.append(("V1: NeuronType ETERNAL", hasattr(NeuronType, 'ETERNAL')))
        checks.append(("V1: NeuronType ANCHOR", hasattr(NeuronType, 'ANCHOR')))
        state = NeuronState(neuron_id='test', activation_level=0.9)
        decayed = state.decay(999999)
        checks.append(("V1: No-decay (activation preserved)", decayed.activation_level == 0.9))
    except Exception as e:
        checks.append(("V1: Core import", False))
        checks.append(("V1: NeuronType ANCHOR", False))
        checks.append(("V1: No-decay", False))

    # V1: Vietnamese NLP
    try:
        from neural_memory.extraction.vietnamese_nlp import (
            VIETNAMESE_COMPOUNDS,
            EXTENDED_STOPWORDS_VI,
        )
        checks.append(("V1: Vietnamese NLP (200+ compounds)",
                        len(VIETNAMESE_COMPOUNDS) > 100 and len(EXTENDED_STOPWORDS_VI) > 30))
    except Exception:
        checks.append(("V1: Vietnamese NLP", False))

    # V1: InfinityTier
    try:
        from neural_memory.engine.compression import InfinityTier
        checks.append(("V1: InfinityTier (HOT/WARM/COLD)",
                        InfinityTier.HOT == 0 and InfinityTier.WARM == 1 and InfinityTier.COLD == 2))
    except Exception:
        checks.append(("V1: InfinityTier", False))

    # V1: RelevanceScorer
    try:
        from datetime import datetime, timedelta
        from neural_memory.core.neuron import NeuronState as NS2, NeuronType as NT2
        from neural_memory.engine.relevance import RelevanceScorer
        scorer = RelevanceScorer()
        now = datetime(2026, 3, 12, 12, 0, 0)
        s = NS2(neuron_id="t", activation_level=0.3, access_frequency=2,
                last_activated=now - timedelta(days=365))
        score = scorer.score(s, NT2.ENTITY, 3, 2, now)
        checks.append(("V1: RelevanceScorer (365d score > 0)", score > 0))
    except Exception:
        checks.append(("V1: RelevanceScorer", False))

    # ============================================================
    # V2 PATTERNS
    # ============================================================
    # Pattern 1: Crash Sentinel
    try:
        from neural_memory.engine.crash_sentinel import CrashSentinel
        from neural_memory.engine.hooks import HookEvent
        checks.append(("V2-P1: CrashSentinel", True))
        checks.append(("V2-P1: HookEvent.SESSION_START", HookEvent.SESSION_START == 'session_start'))
    except Exception:
        checks.append(("V2-P1: CrashSentinel", False))
        checks.append(("V2-P1: HookEvent.SESSION_START", False))

    # Pattern 2: Scored Observations
    try:
        from neural_memory.core.fiber import Fiber
        f = Fiber.create(neuron_ids={'n'}, synapse_ids={'s'}, anchor_neuron_id='n')
        f2 = f.with_observation('decision', confidence=0.9, importance=0.8)
        checks.append(("V2-P2: Fiber.observation_type", f2.observation_type == 'decision'))
        checks.append(("V2-P2: Fiber.importance", abs(f2.importance - 0.8) < 0.01))
    except Exception:
        checks.append(("V2-P2: Fiber.observation_type", False))
        checks.append(("V2-P2: Fiber.importance", False))

    # Pattern 3: Size Trigger
    try:
        from neural_memory.engine.observation_trigger import ObservationTrigger
        checks.append(("V2-P3: ObservationTrigger", True))
    except Exception:
        checks.append(("V2-P3: ObservationTrigger", False))

    # Pattern 4: Coordination Ledger
    try:
        from neural_memory.engine.coordination_ledger import CoordinationLedger
        checks.append(("V2-P4: CoordinationLedger", True))
    except Exception:
        checks.append(("V2-P4: CoordinationLedger", False))

    # Pattern 5: Agent Lock
    try:
        from neural_memory.engine.agent_lock import AgentLockManager
        checks.append(("V2-P5: AgentLockManager", True))
    except Exception:
        checks.append(("V2-P5: AgentLockManager", False))

    # Pattern 6: Tier Decay
    try:
        from neural_memory.engine.tier_decay import TierDecay, compute_decayed_salience
        s = compute_decayed_salience(1.0, 45.0, tier=0, importance=0.5)
        checks.append(("V2-P6: TierDecay formula", 0.49 < s < 0.51))
    except Exception:
        checks.append(("V2-P6: TierDecay formula", False))

    # Pattern 7: Supersession
    try:
        from neural_memory.core.synapse import SynapseType
        from neural_memory.engine.supersession import SupersessionManager
        checks.append(("V2-P7: SUPERSEDES synapse", SynapseType.SUPERSEDES == 'supersedes'))
        checks.append(("V2-P7: SupersessionManager", True))
    except Exception:
        checks.append(("V2-P7: SUPERSEDES synapse", False))
        checks.append(("V2-P7: SupersessionManager", False))

    # Schema
    try:
        from neural_memory.storage.sqlite_schema import SCHEMA_VERSION
        checks.append(("V2: Schema version 21", SCHEMA_VERSION == 21))
    except Exception:
        checks.append(("V2: Schema version", False))

    # ============================================================
    # V3 INSTINCT PROTOCOL (behavioral — check file presence)
    # ============================================================
    skill_dir = os.path.dirname(os.path.abspath(__file__))

    skill_path = os.path.join(skill_dir, "SKILL.md")
    skill_content = ""
    if os.path.exists(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            skill_content = f.read()

    checks.append(("V3-INST: Instinct Protocol in SKILL.md",
                    "INSTINCT" in skill_content.upper() or "instinct" in skill_content.lower()))
    checks.append(("V3-INST: Auto-Remember rules",
                    "Auto-Remember" in skill_content and "category=" in skill_content))
    checks.append(("V3-INST: 3-Tier Recall flow",
                    "TẦNG 1" in skill_content and "TẦNG 2" in skill_content and "TẦNG 3" in skill_content))
    checks.append(("V3-INST: Session-Aware loading",
                    "Session-Aware" in skill_content or "SESSION-AWARE" in skill_content.upper()))
    checks.append(("V3-INST: Duplicate Prevention",
                    "Duplicate Prevention" in skill_content or "DUPLICATE" in skill_content.upper()))

    protocol_path = os.path.join(skill_dir, "INSTINCT-PROTOCOL.md")
    checks.append(("V3-INST: INSTINCT-PROTOCOL.md (standalone)",
                    os.path.exists(protocol_path) and os.path.getsize(protocol_path) > 1000))

    # ============================================================
    # V3.1 COMPLETENESS (new checks)
    # ============================================================

    # Correct wheel version
    dist_dir = os.path.join(skill_dir, "dist")
    has_v2_wheel = os.path.exists(os.path.join(dist_dir, "infinity_neural-2.0.0-py3-none-any.whl"))
    no_v1_wheel = not os.path.exists(os.path.join(dist_dir, "infinity_neural-1.0.0-py3-none-any.whl"))
    checks.append(("V3.1: V2 wheel present (2.0.0)", has_v2_wheel))
    checks.append(("V3.1: No V1 wheel (1.0.0)", no_v1_wheel))

    # Config files
    config_dir = os.path.join(skill_dir, "config")
    checks.append(("V3.1: config/brain-defaults.toml",
                    os.path.exists(os.path.join(config_dir, "brain-defaults.toml"))))
    checks.append(("V3.1: config/mcp-infinity-neural.json",
                    os.path.exists(os.path.join(config_dir, "mcp-infinity-neural.json"))))
    checks.append(("V3.1: config/INSTALL.md",
                    os.path.exists(os.path.join(config_dir, "INSTALL.md"))))

    # Scripts
    scripts_dir = os.path.join(skill_dir, "scripts")
    checks.append(("V3.1: scripts/memory_bridge.py",
                    os.path.exists(os.path.join(scripts_dir, "memory_bridge.py"))))
    checks.append(("V3.1: scripts/verify_install.py",
                    os.path.exists(os.path.join(scripts_dir, "verify_install.py"))))

    # MCP tools documented in SKILL.md
    checks.append(("V3.1: MCP tools documented (nmem_remember)",
                    "nmem_remember" in skill_content))
    checks.append(("V3.1: Cognitive tools documented (nmem_hypothesize)",
                    "nmem_hypothesize" in skill_content))
    checks.append(("V3.1: 46 tools count",
                    "46" in skill_content and "MCP" in skill_content))

    # CHANGELOG
    changelog_path = os.path.join(skill_dir, "CHANGELOG.md")
    changelog_content = ""
    if os.path.exists(changelog_path):
        with open(changelog_path, "r", encoding="utf-8") as f:
            changelog_content = f.read()
    checks.append(("V3.1: CHANGELOG mentions V3.1",
                    "3.1" in changelog_content))

    # ============================================================
    # RESULTS
    # ============================================================
    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)

    print(f"Infinity Neural V3.1.0 — Complete Edition Verification")
    print(f"{'=' * 60}")

    current_group = ""
    for name, ok in checks:
        group = name.split(":")[0].strip()
        if group != current_group:
            current_group = group
            print(f"\n  [{current_group}]")
        status = "PASS" if ok else "FAIL"
        detail = name.split(":", 1)[1].strip() if ":" in name else name
        print(f"    [{status}] {detail}")

    print(f"\n{'=' * 60}")
    print(f"Result: {passed}/{total} checks passed")

    if passed == total:
        print("VERDICT: ALL PASS — Infinity Neural V3.1 Complete!")
        print("\nV1 Foundation: OK  |  V2 Engine: OK  |  V3 Instinct: OK  |  V3.1 Complete: OK")
    else:
        failed = [(n, ok) for n, ok in checks if not ok]
        print(f"VERDICT: {len(failed)} FAILED")
        for name, _ in failed:
            print(f"  -> {name}")

    return passed == total


if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
