"""Tests for InfinityNeural RelevanceScorer and ContextBudgetAllocator."""

from datetime import datetime, timedelta

import pytest

from neural_memory.core.neuron import NeuronState, NeuronType
from neural_memory.engine.activation import ActivationResult
from neural_memory.engine.relevance import (
    ContextBudgetAllocator,
    RelevanceConfig,
    RelevanceScorer,
    TokenBudgetConfig,
)


class TestRelevanceScorer:
    """Tests for RelevanceScorer."""
    
    def test_recent_high_frequency_scores_high(self) -> None:
        """Recent + high frequency memory should score high."""
        scorer = RelevanceScorer()
        now = datetime(2026, 3, 4, 12, 0, 0)
        
        state = NeuronState(
            neuron_id="n1",
            activation_level=0.8,
            access_frequency=10,
            last_activated=now - timedelta(days=1),
        )
        
        score = scorer.score(
            neuron_state=state,
            neuron_type=NeuronType.ENTITY,
            synapse_count=5,
            compression_tier=0,  # HOT
            current_time=now,
        )
        
        # Recent (1d) + high freq + tier 0 → high score (~0.73)
        assert score > 0.7
    
    def test_old_low_frequency_scores_low_but_nonzero(self) -> None:
        """365-day old, low frequency memory should score low but > 0."""
        scorer = RelevanceScorer()
        now = datetime(2026, 3, 4, 12, 0, 0)
        
        state = NeuronState(
            neuron_id="n2",
            activation_level=0.1,
            access_frequency=1,
            last_activated=now - timedelta(days=365),
        )
        
        score = scorer.score(
            neuron_state=state,
            neuron_type=NeuronType.ACTION,
            synapse_count=2,
            compression_tier=2,  # COLD
            current_time=now,
        )
        
        # Old + low freq + COLD tier → low but never zero
        assert score > 0.0
        assert score < 0.3
    
    def test_eternal_neurons_always_rank_high(self) -> None:
        """ETERNAL neurons get bonus, always rank high."""
        scorer = RelevanceScorer()
        now = datetime(2026, 3, 4, 12, 0, 0)
        
        # Old ETERNAL neuron
        state = NeuronState(
            neuron_id="eternal",
            activation_level=0.5,
            access_frequency=2,
            last_activated=now - timedelta(days=180),
        )
        
        score = scorer.score(
            neuron_state=state,
            neuron_type=NeuronType.ETERNAL,
            synapse_count=3,
            compression_tier=0,
            current_time=now,
        )
        
        # ETERNAL bonus = 0.5, should rank high despite age
        assert score > 0.7
    
    def test_tier_bonus_applied(self) -> None:
        """Tier bonus should increase score (HOT > WARM > COLD)."""
        scorer = RelevanceScorer()
        now = datetime(2026, 3, 4, 12, 0, 0)
        
        state = NeuronState(
            neuron_id="n3",
            activation_level=0.5,
            access_frequency=3,
            last_activated=now - timedelta(days=60),
        )
        
        score_hot = scorer.score(state, NeuronType.ENTITY, 5, 0, now)
        score_warm = scorer.score(state, NeuronType.ENTITY, 5, 1, now)
        score_cold = scorer.score(state, NeuronType.ENTITY, 5, 2, now)
        
        assert score_hot > score_warm > score_cold


class TestContextBudgetAllocator:
    """Tests for ContextBudgetAllocator."""
    
    def test_tier_distribution(self) -> None:
        """Budget should be allocated 60% HOT, 30% WARM, 10% COLD."""
        allocator = ContextBudgetAllocator()
        
        # Create mock results: 2 HOT, 2 WARM, 2 COLD (equal relevance)
        results = [
            (
                ActivationResult("h1", 0.8, 1, ["a", "h1"], "a"),
                0.8,
                0,
            ),  # HOT
            (
                ActivationResult("h2", 0.7, 1, ["a", "h2"], "a"),
                0.7,
                0,
            ),  # HOT
            (
                ActivationResult("w1", 0.6, 1, ["a", "w1"], "a"),
                0.6,
                1,
            ),  # WARM
            (
                ActivationResult("w2", 0.5, 1, ["a", "w2"], "a"),
                0.5,
                1,
            ),  # WARM
            (
                ActivationResult("c1", 0.3, 1, ["a", "c1"], "a"),
                0.3,
                2,
            ),  # COLD
            (
                ActivationResult("c2", 0.2, 1, ["a", "c2"], "a"),
                0.2,
                2,
            ),  # COLD
        ]
        
        allocation = allocator.allocate(results)
        
        # HOT total should be ~900 (60% of 1500)
        hot_total = allocation["h1"] + allocation["h2"]
        assert 850 <= hot_total <= 950
        
        # WARM total should be ~450 (30% of 1500)
        warm_total = allocation["w1"] + allocation["w2"]
        assert 400 <= warm_total <= 500
        
        # COLD total should be ~150 (10% of 1500)
        cold_total = allocation["c1"] + allocation["c2"]
        assert 130 <= cold_total <= 170
    
    def test_proportional_within_tier(self) -> None:
        """Within a tier, allocation should be proportional to relevance."""
        allocator = ContextBudgetAllocator()
        
        # 2 HOT results: one with 2x relevance of the other
        results = [
            (ActivationResult("h1", 0.8, 1, ["a", "h1"], "a"), 0.8, 0),
            (ActivationResult("h2", 0.4, 1, ["a", "h2"], "a"), 0.4, 0),
        ]
        
        allocation = allocator.allocate(results)
        
        # h1 should get ~2x tokens of h2 (0.8/(0.8+0.4) vs 0.4/(0.8+0.4))
        ratio = allocation["h1"] / allocation["h2"]
        assert 1.8 <= ratio <= 2.2
    
    def test_allocate_and_sort(self) -> None:
        """allocate_and_sort should return results sorted by relevance."""
        allocator = ContextBudgetAllocator()
        
        results = [
            (ActivationResult("n1", 0.5, 1, ["a", "n1"], "a"), 0.5, 0),
            (ActivationResult("n2", 0.9, 1, ["a", "n2"], "a"), 0.9, 0),
            (ActivationResult("n3", 0.3, 1, ["a", "n3"], "a"), 0.3, 1),
        ]
        
        sorted_results = allocator.allocate_and_sort(results)
        
        # Should be sorted: n2 (0.9), n1 (0.5), n3 (0.3)
        assert sorted_results[0][0].neuron_id == "n2"
        assert sorted_results[1][0].neuron_id == "n1"
        assert sorted_results[2][0].neuron_id == "n3"
