# File Map — Chi tiết sửa đổi

## Tổng quan

**8 file sửa + 3 file mới = 11 thay đổi** trên tổng ~60+ file

```
neural-memory/src/neural_memory/
│
├── core/
│   ├── neuron.py          ← SỬA
│   │   ├── NeuronType: +ETERNAL, +ANCHOR
│   │   ├── NeuronState.decay_rate: 0.1 → 0.0
│   │   └── NeuronState.decay(): exponential → no-op (return self)
│   │
│   ├── synapse.py         ← GIỮ NGUYÊN
│   │   └── 18 SynapseTypes đủ dùng
│   │
│   ├── fiber.py           ← GIỮ NGUYÊN
│   │   └── Đã có compression_tier field sẵn
│   │
│   └── brain.py           ← SỬA
│       ├── BrainConfig.decay_rate: 0.1 → 0.0
│       └── BrainConfig.activation_threshold: 0.2 → 0.08
│
├── engine/
│   ├── activation.py      ← GIỮ NGUYÊN
│   │   └── SpreadingActivation thuật toán gốc tốt
│   │
│   ├── reflex_activation.py ← SỬA
│   │   └── _compute_time_factor: sigmoid aggressive → gentle hyperbolic
│   │       Gốc: max(0.1, 1/(1+exp((h-72)/36)))  — 7 ngày = 0.15
│   │       Mới: max(0.5, 1/(1+days*0.002))       — 365 ngày = 0.58
│   │
│   ├── lifecycle.py       ← SỬA NẶNG
│   │   ├── DecayManager.apply_decay() → no-op (return empty report)
│   │   ├── DecayManager giữ class shell cho backward compat
│   │   └── ReinforcementManager → GIỮ NGUYÊN (reinforcement tốt)
│   │
│   ├── consolidation.py   ← SỬA
│   │   ├── PRUNE strategy → DEMOTE strategy (hạ tier, không xóa)
│   │   ├── COMPRESS strategy → delegate to CompressionTierManager
│   │   └── Tất cả strategy khác → GIỮ NGUYÊN
│   │
│   ├── stabilization.py   ← SỬA
│   │   ├── noise_floor: 0.05 → 0.01
│   │   ├── dampening_factor: 0.85 → 0.92
│   │   ├── homeostatic_target: 0.5 → 0.4
│   │   ├── homeostatic_strength: 0.3 → 0.15
│   │   └── max_iterations: 10 → 8
│   │
│   ├── retrieval.py       ← SỬA
│   │   └── Sau activation + stabilization: apply RelevanceScorer
│   │       → Sort results by relevance
│   │       → Token budget allocation by tier
│   │
│   ├── compression.py     ← MỚI ✨
│   │   ├── CompressionTierManager
│   │   ├── evaluate() — quyết định tier dựa trên age + frequency
│   │   ├── demote() — nén fiber xuống tier
│   │   ├── promote() — thăng tier khi recall
│   │   ├── Tier 0 (HOT): full detail
│   │   ├── Tier 1 (WARM): summary + key neurons
│   │   └── Tier 2 (COLD): core facts only
│   │
│   ├── relevance.py       ← MỚI ✨
│   │   ├── RelevanceScorer
│   │   ├── score = recency*0.3 + frequency*0.25 + connections*0.15
│   │   │         + tier_bonus + eternal_bonus
│   │   ├── ContextBudgetAllocator
│   │   └── Token budget: tier 0 > tier 1 > tier 2
│   │
│   ├── sufficiency.py     ← GIỮ NGUYÊN
│   ├── reconstruction.py  ← GIỮ NGUYÊN
│   ├── causal_traversal.py ← GIỮ NGUYÊN
│   ├── clustering.py      ← GIỮ NGUYÊN
│   ├── depth_prior.py     ← GIỮ NGUYÊN
│   └── write_queue.py     ← GIỮ NGUYÊN
│
├── extraction/
│   ├── parser.py          ← SỬA
│   │   ├── +_VN_TONE_MAP (diacritics normalization)
│   │   ├── +_VN_STOPWORDS (loại từ vô nghĩa)
│   │   ├── +_normalize_vietnamese() (fuzzy tone matching)
│   │   └── Tích hợp vào query decomposition
│   │
│   └── router.py          ← GIỮ NGUYÊN
│
├── cli/
│   ├── main.py            ← GIỮ NGUYÊN (register thêm tier command)
│   └── commands/
│       ├── tier.py        ← MỚI ✨
│       │   ├── nmem tier status — phân bố tier
│       │   ├── nmem tier promote <id> — thăng tier
│       │   └── nmem tier demote — chạy cycle
│       └── ...còn lại GIỮ NGUYÊN
│
├── integrations/          ← GIỮ NGUYÊN
├── storage/               ← GIỮ NGUYÊN
├── training/              ← GIỮ NGUYÊN
└── mcp/                   ← GIỮ NGUYÊN
```

## Dependency Graph (thứ tự sửa)

```
Phase 1 (độc lập, sửa song song):
  neuron.py ──┐
  brain.py ───┤── không phụ thuộc nhau
  stabilization.py ─┘

Phase 1 (phụ thuộc neuron.py):
  lifecycle.py ← cần ETERNAL type check
  reflex_activation.py ← cần NeuronState changes

Phase 2 (phụ thuộc Phase 1):
  compression.py (MỚI) ← cần ETERNAL type, fiber.compression_tier
  relevance.py (MỚI) ← cần NeuronState fields
  consolidation.py ← cần compression.py
  retrieval.py ← cần relevance.py

Phase 3 (độc lập):
  parser.py ← Vietnamese NLP, không phụ thuộc Phase 1-2

Phase 4 (phụ thuộc tất cả):
  tests/ ← test toàn bộ
```
