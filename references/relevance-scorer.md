# Relevance Scorer — Thay thế Ebbinghaus Decay

## Vấn đề gốc: Ebbinghaus giết memory

```
Ebbinghaus: retention = e^(-0.1 × days)
→ 7 ngày:   50% activation
→ 30 ngày:  5% activation
→ 60 ngày:  ~0% → PRUNE (xóa vĩnh viễn)
```

Memory cũ bị **xóa khỏi existence**. Không tìm lại được.

## Giải pháp: Relevance Ranking

Memory **luôn tồn tại**. Khi recall, chỉ **xếp hạng** theo relevance.
Score cao = hiển thị trước. Score thấp = hiển thị sau (hoặc chỉ khi cần).
Score KHÔNG BAO GIỜ = 0.

## Công thức

```python
import math
from datetime import datetime
from neural_memory.core.neuron import NeuronType

class RelevanceScorer:
    """Score neurons by relevance, not existence."""
    
    # Trọng số mỗi factor
    W_RECENCY = 0.30
    W_FREQUENCY = 0.25
    W_CONNECTIONS = 0.15
    W_TIER = 1.0       # tier bonus là additive, không weighted
    W_ETERNAL = 1.0     # eternal bonus là additive
    
    def score(
        self,
        neuron_state,
        neuron_type: NeuronType,
        synapse_count: int,
        compression_tier: int,
        current_time: datetime,
    ) -> float:
        """
        Tính relevance score.
        
        Returns: float > 0 LUÔN. Không bao giờ 0.
        """
        
        # Factor 1: Recency — gentle hyperbolic, never zero
        if neuron_state.last_activated:
            days = (current_time - neuron_state.last_activated).total_seconds() / 86400
        else:
            days = 365  # default cho neuron chưa từng access
        recency = 1.0 / (1.0 + days * 0.005)
        # 1 ngày: 0.995, 30 ngày: 0.87, 180 ngày: 0.53, 365 ngày: 0.35
        
        # Factor 2: Frequency — log scale, cap at 1.0
        frequency = min(1.0, math.log1p(neuron_state.access_frequency) * 0.15)
        # freq=1: 0.10, freq=5: 0.27, freq=20: 0.46, freq=100: 0.69
        
        # Factor 3: Connection density — more connected = more important
        connections = min(1.0, synapse_count * 0.05)
        # 5 synapses: 0.25, 10: 0.50, 20+: 1.0
        
        # Factor 4: Tier bonus (additive)
        tier_bonus = {0: 0.30, 1: 0.15, 2: 0.0}.get(compression_tier, 0.0)
        
        # Factor 5: Eternal bonus (additive)
        eternal_bonus = 0.5 if neuron_type in (NeuronType.ETERNAL, NeuronType.ANCHOR) else 0.0
        
        # Combine
        base_score = (
            recency * self.W_RECENCY
            + frequency * self.W_FREQUENCY  
            + connections * self.W_CONNECTIONS
        )
        
        return base_score + tier_bonus + eternal_bonus
```

## Bảng so sánh chi tiết

### Memory 30 ngày, frequency=3, 5 synapses:

| | Ebbinghaus | Relevance |
|---|---|---|
| Activation / Score | 0.05 (gần chết) | 0.58 |
| Tìm được? | Khó (dưới threshold) | ✅ Dễ |

### Memory 180 ngày, frequency=1, 3 synapses:

| | Ebbinghaus | Relevance |
|---|---|---|
| Activation / Score | ~0.00 (đã prune) | 0.31 |
| Tìm được? | ❌ ĐÃ XÓA | ✅ Có (rank thấp) |

### Memory 365 ngày, frequency=0, 2 synapses:

| | Ebbinghaus | Relevance |
|---|---|---|
| Activation / Score | 0.00 (xóa lâu rồi) | 0.22 |
| Tìm được? | ❌ KHÔNG TỒN TẠI | ✅ Có (rank thấp nhất) |

### ETERNAL neuron (bất kỳ tuổi nào):

| | Ebbinghaus | Relevance |
|---|---|---|
| Score | Decay như thường | 0.72+ (eternal bonus) |
| Tìm được? | Phụ thuộc tuổi | ✅ LUÔN top results |

## Context Budget Allocator

Sau khi score, cần phân bổ token budget thông minh:

```python
class ContextBudgetAllocator:
    """Phân bổ token cho recall results."""
    
    def allocate(
        self,
        results: list[ScoredResult],
        max_tokens: int = 1500,
    ) -> list[ScoredResult]:
        """
        Phân bổ token budget:
        - Tier 0: full content (60% budget)
        - Tier 1: summary + key details (30% budget)  
        - Tier 2: one-liner summary (10% budget)
        
        Trong mỗi tier: phân theo relevance score proportional.
        """
        # Sort by relevance descending
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        tier_budgets = {
            0: int(max_tokens * 0.60),
            1: int(max_tokens * 0.30),
            2: int(max_tokens * 0.10),
        }
        
        for tier in [0, 1, 2]:
            tier_results = [r for r in results if r.compression_tier == tier]
            if not tier_results:
                continue
            budget = tier_budgets[tier]
            total_score = sum(r.relevance_score for r in tier_results)
            if total_score == 0:
                continue
            for r in tier_results:
                r.token_budget = int(budget * r.relevance_score / total_score)
        
        return results
```

## Tại sao KHÔNG dùng decay cho ranking?

Có thể nghĩ: "giữ decay nhưng đừng prune". Nhưng:

1. **Decay exponential quá hung** — 30 ngày = 5% là quá thấp cho ranking
2. **Decay không xét frequency** — memory dùng 100 lần cũng decay giống dùng 1 lần
3. **Decay không xét connections** — memory cô lập decay giống memory central
4. **Relevance multi-factor tốt hơn** — 5 yếu tố > 1 yếu tố

Relevance Scorer = **thay thế hoàn toàn**, không phải bổ sung.
