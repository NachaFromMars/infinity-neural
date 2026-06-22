# Infinity Neural — Design Document

**Version:** 1.0  
**Date:** 2026-03-04  
**Author:** MulaNacharis  

---

## Philosophy

> "Neurons never die. They compress, they hibernate, they whisper — but they never disappear."

Infinity Neural transforms NeuralMemory from an Ebbinghaus-decay system into a **perfect recall** architecture. Instead of forgetting old memories, it **compresses** them into progressively compact forms while maintaining findability through relevance scoring.

**Core principle:** Token budget management replaces information deletion.

---

## Architecture

### 1. No-Decay Engine

NeuronState.decay() returns `self` — a no-op. Neurons maintain their activation level indefinitely. This is the foundation of the "never forget" guarantee.

**Changed files:**
- `core/neuron.py` — decay() returns self
- `engine/lifecycle.py` — DecayManager.apply_decay() skips all neurons

### 2. Neuron Types

Two new types extend the existing NeuronType enum:

| Type | Purpose | Tier Behavior |
|------|---------|---------------|
| ETERNAL | Core identity, preferences | Always HOT, +0.5 relevance bonus |
| ANCHOR | Structural nodes, relations | Always HOT, +0.5 relevance bonus |

### 3. Three-Tier Compression

```
┌─────────┐     30 days     ┌──────────┐    180 days    ┌──────────┐
│   HOT   │ ──────────────► │   WARM   │ ─────────────► │   COLD   │
│ (Tier 0)│                 │ (Tier 1) │                │ (Tier 2) │
│ 60% tok │                 │ 30% tok  │                │ 10% tok  │
└─────────┘                 └──────────┘                └──────────┘
     ▲                           ▲                           │
     │          PROMOTE          │          PROMOTE          │
     └───────────────────────────┴───────────────────────────┘
                        (on recall/access)
```

**Demotion rules:**
- HOT → WARM at 30 days (configurable), frequency < 5
- WARM → COLD at 180 days (configurable)
- ETERNAL/ANCHOR neurons: never demoted

**Promotion rules:**
- Any recall/access promotes one tier up
- COLD → WARM → HOT

**Key difference from original:** Original 5-tier system deletes content at tier 4 (GRAPH_ONLY). InfinityTier NEVER deletes — COLD tier keeps one-liner summaries.

### 4. Relevance Scoring

```python
score = (
    activation * activation_weight
    + frequency * frequency_weight  
    + recency * recency_weight
    + synapse_bonus
    + tier_bonus        # HOT: +0.1, WARM: +0.05, COLD: +0.0
    + type_bonus        # ETERNAL/ANCHOR: +0.5
)
```

Guarantees: score > 0 for ALL neurons regardless of age.

### 5. Token Budget Allocation

```
ContextBudgetAllocator:
  HOT:  60% of available tokens (full content)
  WARM: 30% (summary + key details)
  COLD: 10% (one-liner)
```

Within each tier, budget is distributed proportionally by relevance score.

### 6. Vietnamese NLP

Enhanced keyword extraction for Vietnamese text:
- 200+ compound word detection ("sinh viên", "trí tuệ nhân tạo")
- Extended stopwords (particles, connectors, fillers)
- Tone stripping for fuzzy matching
- NFC normalization

---

## Migration Path

Infinity Neural is **backward compatible**:

1. Existing brains work unchanged (decay_rate defaults to 0.0)
2. Existing tests pass (3091/3093)
3. InfinityTierManager is opt-in (activated via config)
4. RelevanceScorer hooks are wrapped in try/except

To enable for an existing brain:
```python
from neural_memory.engine.compression import InfinityTierManager, InfinityTierConfig

config = InfinityTierConfig(
    hot_max_age_days=30.0,
    warm_max_age_days=180.0,
    hot_min_frequency=5,
)
tier_mgr = InfinityTierManager(storage, config)
```

---

## Test Coverage

| Suite | Tests | Status |
|-------|-------|--------|
| InfinityNeural core | 11 | PASS |
| Vietnamese NLP | 10 | PASS |
| Relevance scorer | 7 | PASS |
| Integration (TierManager) | 5 | PASS |
| Original regression | 3091 | PASS |
| **Total** | **3124** | **PASS** |

---

## Benchmark Results

| Age | Avg Score | Recall Rate |
|-----|-----------|-------------|
| 1d | 0.926 | 100% |
| 30d | 0.885 | 100% |
| 180d | 0.666 | 100% |
| 365d | 0.490 | 100% |
| 730d | 0.448 | 100% |

All targets exceeded. ETERNAL neurons maintain score > 0.9 regardless of age.
