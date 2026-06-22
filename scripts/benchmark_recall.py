"""InfinityNeural Benchmark — Recall accuracy at 30/180/365 days.

Measures:
1. Can old memories be found? (recall rate)
2. Are old memories ranked correctly? (relevance score)
3. Token efficiency per tier (budget allocation)
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent / "source" / "src"))

from neural_memory.core.neuron import NeuronState, NeuronType
from neural_memory.engine.relevance import (
    ContextBudgetAllocator,
    RelevanceScorer,
    TokenBudgetConfig,
)
from neural_memory.engine.compression import InfinityTier, InfinityTierConfig


def benchmark_recall_accuracy():
    """Benchmark recall at different ages."""
    scorer = RelevanceScorer()
    now = datetime(2026, 3, 4, 12, 0, 0)
    
    print("=" * 70)
    print("INFINITY NEURAL — RECALL ACCURACY BENCHMARK")
    print("=" * 70)
    
    # Test matrix: age × neuron_type × tier
    ages_days = [1, 7, 30, 90, 180, 365, 730]
    neuron_types = [
        (NeuronType.ENTITY, "ENTITY"),
        (NeuronType.CONCEPT, "CONCEPT"),
        (NeuronType.ETERNAL, "ETERNAL"),
        (NeuronType.ANCHOR, "ANCHOR"),
        (NeuronType.ACTION, "ACTION"),
    ]
    
    print(f"\n{'Age':>8} | {'Type':>10} | {'Tier':>6} | {'Score':>8} | {'Findable':>10}")
    print("-" * 60)
    
    total_tests = 0
    findable_count = 0
    scores_by_age: dict[int, list[float]] = {}
    
    for age in ages_days:
        scores_by_age[age] = []
        for ntype, nname in neuron_types:
            # Determine expected tier
            if age <= 30:
                tier = InfinityTier.HOT
            elif age <= 180:
                tier = InfinityTier.WARM
            else:
                tier = InfinityTier.COLD
            
            # ETERNAL/ANCHOR always HOT
            if ntype in (NeuronType.ETERNAL, NeuronType.ANCHOR):
                tier = InfinityTier.HOT
            
            state = NeuronState(
                neuron_id=f"bench-{age}-{nname}",
                activation_level=max(0.1, 1.0 - age * 0.001),
                access_frequency=max(1, 10 - age // 30),
                last_activated=now - timedelta(days=age),
            )
            
            score = scorer.score(
                neuron_state=state,
                neuron_type=ntype,
                synapse_count=5,
                compression_tier=int(tier),
                current_time=now,
            )
            
            findable = score > 0.05
            total_tests += 1
            if findable:
                findable_count += 1
            scores_by_age[age].append(score)
            
            tier_name = ["HOT", "WARM", "COLD"][int(tier)]
            status = "✅ YES" if findable else "❌ NO"
            print(f"{age:>6}d | {nname:>10} | {tier_name:>6} | {score:>8.4f} | {status:>10}")
    
    recall_rate = findable_count / total_tests * 100
    
    print(f"\n{'=' * 60}")
    print(f"RECALL RATE: {findable_count}/{total_tests} ({recall_rate:.1f}%)")
    print(f"{'=' * 60}")
    
    # Average scores by age
    print(f"\n{'Age':>8} | {'Avg Score':>10} | {'Min Score':>10} | {'Max Score':>10}")
    print("-" * 50)
    for age in ages_days:
        scores = scores_by_age[age]
        avg = sum(scores) / len(scores)
        mn = min(scores)
        mx = max(scores)
        print(f"{age:>6}d | {avg:>10.4f} | {mn:>10.4f} | {mx:>10.4f}")
    
    # Token budget allocation
    print(f"\n{'=' * 60}")
    print("TOKEN BUDGET ALLOCATION")
    print(f"{'=' * 60}")
    
    for total_tokens in [4000, 8000, 16000, 32000]:
        config = TokenBudgetConfig(max_tokens=total_tokens)
        hot_budget = int(total_tokens * config.tier_0_pct)
        warm_budget = int(total_tokens * config.tier_1_pct)
        cold_budget = int(total_tokens * config.tier_2_pct)
        print(f"\nTotal: {total_tokens} tokens")
        print(f"  HOT:  {hot_budget:>6} ({config.tier_0_pct*100:.0f}%)")
        print(f"  WARM: {warm_budget:>6} ({config.tier_1_pct*100:.0f}%)")
        print(f"  COLD: {cold_budget:>6} ({config.tier_2_pct*100:.0f}%)")
    
    # Verdict
    print(f"\n{'=' * 60}")
    print("VERDICT")
    print(f"{'=' * 60}")
    
    target_30d = sum(1 for s in scores_by_age[30] if s > 0.05) / len(scores_by_age[30]) * 100
    target_180d = sum(1 for s in scores_by_age[180] if s > 0.05) / len(scores_by_age[180]) * 100
    target_365d = sum(1 for s in scores_by_age[365] if s > 0.05) / len(scores_by_age[365]) * 100
    
    print(f"  30-day recall:  {target_30d:.0f}% (target: 100%)")
    print(f"  180-day recall: {target_180d:.0f}% (target: 95%)")
    print(f"  365-day recall: {target_365d:.0f}% (target: 90%)")
    print(f"  Overall recall: {recall_rate:.1f}% (target: 95%)")
    
    passed = recall_rate >= 95 and target_180d >= 95 and target_365d >= 90
    print(f"\n  BENCHMARK: {'✅ PASS' if passed else '❌ FAIL'}")
    
    return passed, recall_rate


if __name__ == "__main__":
    passed, rate = benchmark_recall_accuracy()
    sys.exit(0 if passed else 1)
