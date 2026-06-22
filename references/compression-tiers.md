# Compression Tier System — Thiết kế chi tiết

## Triết lý: CPU Cache Model

Memory không xóa — chỉ di chuyển ra xa hơn. Giống CPU cache:

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  Tier 0 — HOT (L1 Cache)                                │
│  ─────────────────────────                               │
│  Full detail. Mọi neuron, synapse, fiber đều nguyên vẹn  │
│                                                          │
│  Điều kiện:                                              │
│  - Age < 30 ngày  HOẶC  frequency > 5                   │
│  - NeuronType = ETERNAL → LUÔN tier 0                    │
│  - Manual pin → tier 0 vĩnh viễn                         │
│                                                          │
│  Token cost khi recall: CAO (full content)               │
│  Recall precision: 100%                                  │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Tier 1 — WARM (L2 Cache)                                │
│  ─────────────────────────                               │
│  Summary + key neurons giữ nguyên                        │
│                                                          │
│  Điều kiện:                                              │
│  - Age 30-180 ngày  VÀ  frequency 1-5                   │
│  - NeuronType = ANCHOR → không xuống tier 2              │
│                                                          │
│  Nén:                                                    │
│  - Fiber.summary = tóm tắt text                          │
│  - Giữ: ENTITY, CONCEPT, ETERNAL, ANCHOR neurons        │
│  - Nén: ACTION, STATE, SENSORY → compressed flag         │
│  - Synapse: giữ tất cả, giảm metadata precision          │
│                                                          │
│  Token cost khi recall: TRUNG BÌNH (summary + key)       │
│  Recall precision: ~85%                                  │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Tier 2 — COLD (L3 Cache / Archive)                      │
│  ────────────────────────────────                        │
│  Core facts only                                         │
│                                                          │
│  Điều kiện:                                              │
│  - Age > 180 ngày  VÀ  frequency 0-1                    │
│                                                          │
│  Nén:                                                    │
│  - Fiber: chỉ summary + anchor_neuron_id                 │
│  - Chỉ giữ: ENTITY + CONCEPT + ETERNAL neurons          │
│  - Synapse: chỉ CAUSED_BY, LEADS_TO, IS_A               │
│  - Mọi thứ khác: hash reference (có thể trace nhưng     │
│    không reconstruct full)                               │
│                                                          │
│  Token cost khi recall: THẤP (1-2 dòng summary)         │
│  Recall precision: ~60% (facts + relationships)          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Quy tắc thăng/giáng

### Giáng tier (Demote) — chạy tự động qua consolidation

| Điều kiện | Hành động |
|---|---|
| Fiber age > 30 ngày VÀ frequency ≤ 5 VÀ tier = 0 | Demote 0 → 1 |
| Fiber age > 180 ngày VÀ frequency ≤ 1 VÀ tier = 1 | Demote 1 → 2 |
| NeuronType = ETERNAL | **BỎ QUA** — không bao giờ demote |
| NeuronType = ANCHOR | **Chặn ở tier 1** — không xuống 2 |
| Manual pin (metadata.pinned = true) | **BỎ QUA** — không demote |

### Thăng tier (Promote) — khi recall thành công

| Sự kiện | Hành động |
|---|---|
| Recall hit fiber tier 2 | Promote 2 → 1 |
| Recall hit fiber tier 1 | Promote 1 → 0 |
| Recall hit fiber tier 0 | Tăng frequency (đã ở top) |
| Mọi promote | Reset age counter |

### Giải nén khi thăng tier

**2 → 1:**
- Fiber summary đã có → giữ nguyên
- Query context xung quanh → reconstruct ENTITY + CONCEPT neurons
- KHÔNG khôi phục ACTION/STATE/SENSORY chi tiết
- Synapse: mở rộng lại từ core (CAUSED_BY, LEADS_TO, IS_A) + infer thêm

**1 → 0:**
- Nếu compressed neurons có hash reference → lookup từ storage
- Nếu không có (đã mất detail) → giữ summary + neurons hiện tại
- Thực tế: promote chỉ reset age, content tier 1 khá đủ

## Nén cụ thể khi giáng

### Tier 0 → Tier 1 (CompressToWarm)

```python
async def compress_to_warm(self, fiber: Fiber, storage: NeuralStorage):
    """Nén fiber từ tier 0 xuống tier 1."""
    
    # 1. Tạo summary nếu chưa có
    if not fiber.summary:
        texts = await self._collect_fiber_texts(fiber, storage)
        fiber = fiber.with_summary(self._generate_summary(texts))
    
    # 2. Đánh dấu compressed cho ACTION/STATE/SENSORY neurons
    for neuron_id in fiber.neuron_ids:
        neuron = await storage.get_neuron(neuron_id)
        if neuron.type in (NeuronType.ACTION, NeuronType.STATE, NeuronType.SENSORY):
            state = await storage.get_neuron_state(neuron_id)
            compressed_state = state.with_metadata(compressed=True, 
                                                    original_content_hash=hash(neuron.content))
            await storage.update_neuron_state(compressed_state)
    
    # 3. Update fiber tier
    updated = fiber.with_compression_tier(1)
    await storage.update_fiber(updated)
```

### Tier 1 → Tier 2 (CompressToCold)

```python
async def compress_to_cold(self, fiber: Fiber, storage: NeuralStorage):
    """Nén fiber từ tier 1 xuống tier 2."""
    
    KEEP_TYPES = {NeuronType.ENTITY, NeuronType.CONCEPT, 
                  NeuronType.ETERNAL, NeuronType.ANCHOR}
    KEEP_SYNAPSES = {SynapseType.CAUSED_BY, SynapseType.LEADS_TO, SynapseType.IS_A}
    
    # 1. Lọc neurons — chỉ giữ ENTITY, CONCEPT, ETERNAL, ANCHOR
    neurons_to_keep = set()
    for neuron_id in fiber.neuron_ids:
        neuron = await storage.get_neuron(neuron_id)
        if neuron.type in KEEP_TYPES:
            neurons_to_keep.add(neuron_id)
    
    # 2. Lọc synapses — chỉ giữ causal + taxonomic
    synapses_to_keep = set()
    for synapse_id in fiber.synapse_ids:
        synapse = await storage.get_synapse(synapse_id)
        if synapse.type in KEEP_SYNAPSES:
            synapses_to_keep.add(synapse_id)
    
    # 3. Update fiber — minimal
    updated = Fiber(
        id=fiber.id,
        neuron_ids=neurons_to_keep,
        synapse_ids=synapses_to_keep,
        anchor_neuron_id=fiber.anchor_neuron_id,
        summary=fiber.summary,  # giữ summary
        compression_tier=2,
        # ... giữ metadata, timestamps
    )
    await storage.update_fiber(updated)
```

## Token Budget khi Recall

```python
def allocate_token_budget(total_tokens: int, results: list[FiberResult]):
    """Phân bổ token budget theo tier."""
    tier_0 = [r for r in results if r.tier == 0]
    tier_1 = [r for r in results if r.tier == 1]
    tier_2 = [r for r in results if r.tier == 2]
    
    # Tier 0 được 60% budget
    # Tier 1 được 30% budget
    # Tier 2 được 10% budget
    budgets = {
        0: int(total_tokens * 0.60),
        1: int(total_tokens * 0.30),
        2: int(total_tokens * 0.10),
    }
    
    # Trong mỗi tier, phân bổ theo relevance score
    for tier, fibers in [(0, tier_0), (1, tier_1), (2, tier_2)]:
        if not fibers:
            continue
        tier_budget = budgets[tier]
        total_relevance = sum(f.relevance for f in fibers)
        for f in fibers:
            f.token_budget = int(tier_budget * f.relevance / total_relevance)
```

## Thống kê kỳ vọng

Ví dụ brain với 1000 memories sau 1 năm:

| Tier | % memories | Token cost khi recall |
|---|---|---|
| Tier 0 (HOT) | ~20% (200) | 60% budget |
| Tier 1 (WARM) | ~50% (500) | 30% budget |
| Tier 2 (COLD) | ~30% (300) | 10% budget |

So sánh NeuralMemory gốc: 70% memories đã bị prune (xóa vĩnh viễn). InfinityNeural: 0% xóa, 100% vẫn recall được.
