"""InfinityNeural Relevance Scorer — replace Ebbinghaus decay with multi-factor ranking.

Instead of decaying memories toward zero (prune), InfinityNeural scores each neuron
by RELEVANCE at query time. Old memories rank lower but NEVER disappear.

Factors:
- Recency: gentle hyperbolic (1 year old = 0.35, not 0)
- Frequency: log-scaled access count
- Connections: synapse density
- Tier bonus: HOT > WARM > COLD
- Eternal bonus: ETERNAL/ANCHOR neurons always rank high
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from neural_memory.core.neuron import NeuronType
from neural_memory.utils.timeutils import utcnow

if TYPE_CHECKING:
    from neural_memory.core.neuron import NeuronState
    from neural_memory.engine.activation import ActivationResult


@dataclass(frozen=True)
class RelevanceConfig:
    """Configuration for relevance scoring."""
    
    # Factor weights (must sum to ~1.0 for base_score)
    weight_recency: float = 0.30
    weight_frequency: float = 0.25
    weight_connections: float = 0.15
    
    # Additive bonuses (not weighted)
    tier_bonus_hot: float = 0.30
    tier_bonus_warm: float = 0.15
    tier_bonus_cold: float = 0.0
    eternal_bonus: float = 0.5
    
    # Recency decay rate (gentle)
    recency_decay_factor: float = 0.005  # 1/(1 + days * 0.005)
    
    # Frequency log scale factor
    frequency_scale: float = 0.15  # log1p(freq) * 0.15
    
    # Connection density scale
    connection_scale: float = 0.05  # synapse_count * 0.05


class RelevanceScorer:
    """Score neurons by relevance, not existence.
    
    Unlike Ebbinghaus decay which reduces activation to zero over time,
    relevance scoring ensures old memories always have score > 0.
    
    Formula:
        base_score = recency*0.3 + frequency*0.25 + connections*0.15
        total = base_score + tier_bonus + eternal_bonus
        
    Example scores:
        - 1 day old, freq=1, 5 synapses, tier=0: ~0.83
        - 30 days old, freq=3, 5 synapses, tier=1: ~0.67
        - 365 days old, freq=1, 2 synapses, tier=2: ~0.22
        - ETERNAL, any age: ~0.72+ (eternal_bonus)
    """
    
    def __init__(self, config: RelevanceConfig | None = None):
        self.config = config or RelevanceConfig()
    
    def score(
        self,
        neuron_state: NeuronState,
        neuron_type: NeuronType,
        synapse_count: int,
        compression_tier: int,
        current_time: datetime | None = None,
    ) -> float:
        """Calculate relevance score for a neuron.
        
        Args:
            neuron_state: State with activation_level, access_frequency, last_activated
            neuron_type: Type of neuron (ETERNAL/ANCHOR get bonus)
            synapse_count: Number of synapses connected to this neuron
            compression_tier: Current tier (0=HOT, 1=WARM, 2=COLD)
            current_time: Reference time (default: now)
            
        Returns:
            Relevance score (always > 0.0)
        """
        current_time = current_time or utcnow()
        
        # Factor 1: Recency — gentle hyperbolic, never zero
        if neuron_state.last_activated:
            days = (current_time - neuron_state.last_activated).total_seconds() / 86400
        else:
            # Never activated → default to old
            days = 365.0
        
        recency = 1.0 / (1.0 + days * self.config.recency_decay_factor)
        # Examples: 1d=0.995, 30d=0.87, 180d=0.53, 365d=0.35
        
        # Factor 2: Frequency — log scale, capped at 1.0
        frequency = min(1.0, math.log1p(neuron_state.access_frequency) * self.config.frequency_scale)
        # Examples: freq=1→0.10, freq=5→0.27, freq=20→0.46, freq=100→0.69
        
        # Factor 3: Connection density — more connected = more important
        connections = min(1.0, synapse_count * self.config.connection_scale)
        # Examples: 5 synapses=0.25, 10=0.50, 20+=1.0
        
        # Base score from weighted factors
        base_score = (
            recency * self.config.weight_recency
            + frequency * self.config.weight_frequency
            + connections * self.config.weight_connections
        )
        
        # Factor 4: Tier bonus (additive)
        tier_bonus = {
            0: self.config.tier_bonus_hot,    # HOT
            1: self.config.tier_bonus_warm,   # WARM
            2: self.config.tier_bonus_cold,   # COLD
        }.get(compression_tier, 0.0)
        
        # Factor 5: Eternal bonus (additive)
        eternal_bonus = 0.0
        if neuron_type in (NeuronType.ETERNAL, NeuronType.ANCHOR):
            eternal_bonus = self.config.eternal_bonus
        
        return base_score + tier_bonus + eternal_bonus
    
    def score_activation_result(
        self,
        result: ActivationResult,
        neuron_state: NeuronState,
        neuron_type: NeuronType,
        synapse_count: int,
        compression_tier: int,
        current_time: datetime | None = None,
    ) -> float:
        """Score an ActivationResult (convenience wrapper).
        
        Args:
            result: ActivationResult from spreading activation
            neuron_state: State for this neuron
            neuron_type: Type of neuron
            synapse_count: Synapse count
            compression_tier: Current tier
            current_time: Reference time
            
        Returns:
            Relevance score
        """
        return self.score(
            neuron_state=neuron_state,
            neuron_type=neuron_type,
            synapse_count=synapse_count,
            compression_tier=compression_tier,
            current_time=current_time,
        )


@dataclass(frozen=True)
class TokenBudgetConfig:
    """Configuration for token budget allocation."""
    
    # Total token budget for recall context
    max_tokens: int = 1500
    
    # Budget allocation per tier (percentages)
    tier_0_pct: float = 0.60  # HOT gets 60%
    tier_1_pct: float = 0.30  # WARM gets 30%
    tier_2_pct: float = 0.10  # COLD gets 10%


class ContextBudgetAllocator:
    """Allocate token budget intelligently across recall results.
    
    InfinityNeural uses tiered token allocation:
    - Tier 0 (HOT): 60% of budget, full content
    - Tier 1 (WARM): 30% of budget, summary + key details
    - Tier 2 (COLD): 10% of budget, one-liner summary
    
    Within each tier, allocation is proportional to relevance score.
    """
    
    def __init__(self, config: TokenBudgetConfig | None = None):
        self.config = config or TokenBudgetConfig()
    
    def allocate(
        self,
        results: list[tuple[ActivationResult, float, int]],  # (result, relevance, tier)
    ) -> dict[str, int]:
        """Allocate token budget across results.
        
        Args:
            results: List of (ActivationResult, relevance_score, compression_tier)
            
        Returns:
            Dict mapping neuron_id → allocated_tokens
        """
        # Group by tier
        tier_0 = [(r, rel) for r, rel, t in results if t == 0]
        tier_1 = [(r, rel) for r, rel, t in results if t == 1]
        tier_2 = [(r, rel) for r, rel, t in results if t == 2]
        
        # Calculate tier budgets
        tier_budgets = {
            0: int(self.config.max_tokens * self.config.tier_0_pct),
            1: int(self.config.max_tokens * self.config.tier_1_pct),
            2: int(self.config.max_tokens * self.config.tier_2_pct),
        }
        
        allocation: dict[str, int] = {}
        
        # Allocate within each tier proportionally by relevance
        for tier, tier_results in [(0, tier_0), (1, tier_1), (2, tier_2)]:
            if not tier_results:
                continue
            
            tier_budget = tier_budgets[tier]
            total_relevance = sum(rel for _, rel in tier_results)
            
            if total_relevance == 0:
                # Equal split if all have zero relevance
                per_result = tier_budget // len(tier_results)
                for r, _ in tier_results:
                    allocation[r.neuron_id] = per_result
            else:
                # Proportional split by relevance
                for r, rel in tier_results:
                    tokens = int(tier_budget * rel / total_relevance)
                    allocation[r.neuron_id] = tokens
        
        return allocation
    
    def allocate_and_sort(
        self,
        results: list[tuple[ActivationResult, float, int]],
    ) -> list[tuple[ActivationResult, int]]:
        """Allocate budget and return sorted results.
        
        Args:
            results: List of (ActivationResult, relevance_score, compression_tier)
            
        Returns:
            List of (ActivationResult, allocated_tokens) sorted by relevance descending
        """
        allocation = self.allocate(results)
        
        # Sort by relevance descending
        sorted_results = sorted(
            [(r, rel, t) for r, rel, t in results],
            key=lambda x: x[1],  # sort by relevance
            reverse=True,
        )
        
        return [(r, allocation.get(r.neuron_id, 0)) for r, _, _ in sorted_results]
