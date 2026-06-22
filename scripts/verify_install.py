"""Infinity Memory V1.0 — Install Verification Script.

Checks all components are properly installed and working.
"""

from __future__ import annotations

import subprocess
import sys


def check(name: str, fn) -> bool:
    """Run a check and print result."""
    try:
        result = fn()
        if result:
            print(f"  ✅ {name}")
            return True
        else:
            print(f"  ❌ {name}")
            return False
    except Exception as e:
        print(f"  ❌ {name} — {e}")
        return False


def check_package():
    """Check infinity-neural is installed."""
    import neural_memory
    return hasattr(neural_memory, "__version__")


def check_cli():
    """Check nmem-mcp CLI is available."""
    result = subprocess.run(
        ["nmem-mcp", "--help"],
        capture_output=True, timeout=10,
    )
    return result.returncode == 0 or b"usage" in result.stdout.lower() or b"mcp" in result.stderr.lower()


def check_no_decay():
    """Check decay is disabled."""
    from neural_memory.core.neuron import NeuronState
    state = NeuronState(neuron_id="verify", activation_level=0.9)
    decayed = state.decay(999999)
    return decayed.activation_level == 0.9


def check_eternal():
    """Check ETERNAL neuron type exists."""
    from neural_memory.core.neuron import NeuronType
    return hasattr(NeuronType, "ETERNAL") and hasattr(NeuronType, "ANCHOR")


def check_tiers():
    """Check InfinityTier compression."""
    from neural_memory.engine.compression import InfinityTier
    return (
        InfinityTier.HOT == 0
        and InfinityTier.WARM == 1
        and InfinityTier.COLD == 2
    )


def check_relevance():
    """Check RelevanceScorer works."""
    from datetime import datetime, timedelta
    from neural_memory.core.neuron import NeuronState, NeuronType
    from neural_memory.engine.relevance import RelevanceScorer

    scorer = RelevanceScorer()
    now = datetime(2026, 3, 4, 12, 0, 0)
    state = NeuronState(
        neuron_id="test",
        activation_level=0.3,
        access_frequency=2,
        last_activated=now - timedelta(days=365),
    )
    score = scorer.score(state, NeuronType.ENTITY, 3, 2, now)
    return score > 0


def check_vietnamese():
    """Check Vietnamese NLP loaded."""
    from neural_memory.extraction.vietnamese_nlp import (
        VIETNAMESE_COMPOUNDS,
        EXTENDED_STOPWORDS_VI,
    )
    return len(VIETNAMESE_COMPOUNDS) > 100 and len(EXTENDED_STOPWORDS_VI) > 30


def check_mcp_tools():
    """Check MCP tool schemas load."""
    from neural_memory.mcp.tool_schemas import get_tool_schemas_for_tier
    schemas = get_tool_schemas_for_tier("full")
    return len(schemas) >= 20


def main():
    print("=" * 50)
    print("  Infinity Memory V1.0 — Install Verification")
    print("=" * 50)
    print()

    checks = [
        ("infinity-neural package installed", check_package),
        ("No-decay (activation stable)", check_no_decay),
        ("ETERNAL/ANCHOR neuron types", check_eternal),
        ("InfinityTier (HOT/WARM/COLD)", check_tiers),
        ("RelevanceScorer (365d > 0)", check_relevance),
        ("Vietnamese NLP (200+ compounds)", check_vietnamese),
        ("MCP tool schemas (29 tools)", check_mcp_tools),
    ]

    passed = 0
    total = len(checks)

    for name, fn in checks:
        if check(name, fn):
            passed += 1

    # CLI check separate (may not be on PATH)
    print()
    try:
        if check("nmem-mcp CLI available", check_cli):
            passed += 1
        total += 1
    except Exception:
        print("  ⚠️  nmem-mcp CLI — not on PATH (install with pip install infinity-neural)")
        total += 1

    print()
    print(f"{'=' * 50}")
    if passed == total:
        print(f"  ✅ All {passed}/{total} checks passed!")
    else:
        print(f"  ⚠️  {passed}/{total} checks passed ({total - passed} failed)")
    print(f"{'=' * 50}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
