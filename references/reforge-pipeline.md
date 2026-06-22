# Reforge Pipeline — Chi tiết 6 Phase

## Phase 0: CLONE & BASELINE (30 phút)

### Mục tiêu
Clone NeuralMemory gốc, xác nhận hoạt động, tạo baseline metrics.

### Bước thực hiện

```bash
# 1. Clone
cd ~/.openclaw/workspace/InfinityNeural
git clone https://github.com/nhadaututtheky/neural-memory source
cd source

# 2. Install dev mode
pip install -e ".[dev]"

# 3. Chạy tests gốc — PHẢI 584 PASS
pytest tests/ -v --tb=short 2>&1 | tee ../baseline-tests.log

# 4. Baseline metrics
python -c "
import time, asyncio
from neural_memory import Brain
from neural_memory.storage import InMemoryStorage
from neural_memory.engine.encoder import MemoryEncoder
from neural_memory.engine.retrieval import ReflexPipeline

async def benchmark():
    storage = InMemoryStorage()
    brain = Brain.create('bench')
    await storage.save_brain(brain)
    storage.set_brain(brain.id)
    encoder = MemoryEncoder(storage, brain.config)
    
    # Encode 100 memories
    for i in range(100):
        await encoder.encode(f'Memory number {i} about topic {i%10}')
    
    # Benchmark recall
    pipeline = ReflexPipeline(storage, brain.config)
    start = time.perf_counter()
    for _ in range(50):
        await pipeline.query('topic 5')
    elapsed = (time.perf_counter() - start) * 1000
    print(f'50 queries: {elapsed:.1f}ms ({elapsed/50:.1f}ms/query)')

asyncio.run(benchmark())
" 2>&1 | tee ../baseline-benchmark.log

# 5. Tạo branch
git checkout -b reforge/infinity-neural
```

### Checklist Phase 0
- [ ] Clone thành công
- [ ] pip install không lỗi
- [ ] 584 tests PASS
- [ ] Baseline benchmark ghi lại
- [ ] Branch tạo xong

---

## Phase 1: CORE ENGINE REFORGE (2-3 giờ)

### Mục tiêu
Tắt decay, sửa time factor, thêm Eternal neurons.

### 1.1 — core/neuron.py

**Thêm NeuronType:**
```python
# Thêm vào class NeuronType(StrEnum):
ETERNAL = "eternal"    # Không bao giờ decay, không nén
ANCHOR = "anchor"      # Mốc quan trọng, không xuống tier 2
```

**Sửa NeuronState defaults:**
```python
# decay_rate: float = 0.1  → SỬA:
decay_rate: float = 0.0

# Sửa method decay():
def decay(self, time_delta_seconds: float) -> NeuronState:
    """InfinityNeural: no decay. Neurons are immortal."""
    return self  # no-op
```

### 1.2 — core/brain.py

**Sửa BrainConfig defaults:**
```python
decay_rate: float = 0.0          # was 0.1
activation_threshold: float = 0.08  # was 0.2
```

### 1.3 — engine/lifecycle.py

**Sửa DecayManager:**
```python
class DecayManager:
    """InfinityNeural: Decay disabled. Replaced by CompressTierManager."""
    
    async def apply_decay(self, storage, reference_time=None, dry_run=False):
        """No-op. InfinityNeural does not decay neurons."""
        return DecayReport(reference_time=reference_time or utcnow())
```

**Giữ nguyên ReinforcementManager.**

### 1.4 — engine/reflex_activation.py

**Sửa _compute_time_factor:**
```python
def _compute_time_factor(self, fiber, reference_time):
    """Gentle time factor. Old fibers still conduct."""
    if fiber.last_conducted is None:
        return 0.8
    age_days = (reference_time - fiber.last_conducted).total_seconds() / 86400
    return max(0.5, 1.0 / (1.0 + age_days * 0.002))
```

### 1.5 — engine/stabilization.py

```python
class StabilizationConfig:
    max_iterations: int = 8        # was 10
    noise_floor: float = 0.01      # was 0.05
    dampening_factor: float = 0.92  # was 0.85
    homeostatic_target: float = 0.4  # was 0.5
    homeostatic_strength: float = 0.15  # was 0.3
```

### Checklist Phase 1
- [ ] neuron.py: ETERNAL + ANCHOR types
- [ ] neuron.py: decay_rate=0.0, decay() no-op
- [ ] brain.py: BrainConfig defaults
- [ ] lifecycle.py: DecayManager no-op
- [ ] reflex_activation.py: gentle time factor
- [ ] stabilization.py: params adjusted

---

## Phase 2: COMPRESSION SYSTEM (1-2 giờ)

### Mục tiêu
Tạo 3-tier compression thay thế prune. Tạo relevance scorer.

### 2.1 — engine/compression.py (MỚI)

Code: [scripts/compression.py](../scripts/compression.py)

### 2.2 — engine/relevance.py (MỚI)

Code: [scripts/relevance.py](../scripts/relevance.py)

### 2.3 — engine/consolidation.py (SỬA)

PRUNE → DEMOTE. COMPRESS → 3-tier delegate.

### 2.4 — engine/retrieval.py (SỬA)

Tích hợp RelevanceScorer + ContextBudgetAllocator.

### Checklist Phase 2
- [ ] compression.py tạo mới
- [ ] relevance.py tạo mới
- [ ] consolidation.py: PRUNE→DEMOTE
- [ ] retrieval.py: relevance ranking

---

## Phase 3: VIETNAMESE NLP (1 giờ)

Code: [scripts/vietnamese_nlp.py](../scripts/vietnamese_nlp.py)

### Checklist Phase 3
- [ ] Tone map + fuzzy matching
- [ ] Stopwords
- [ ] Compound detection
- [ ] Bilingual expansion

---

## Phase 4: TEST & FIX (1-2 giờ)

Tests: [scripts/test_infinity_neural.py](../scripts/test_infinity_neural.py)

```bash
pytest tests/ -v --tb=short
```

### Checklist Phase 4
- [ ] 584 tests gốc PASS
- [ ] test_no_decay PASS
- [ ] test_eternal_neurons PASS
- [ ] test_compression_tiers PASS
- [ ] test_tier_promotion PASS
- [ ] test_relevance_ranking PASS
- [ ] test_vietnamese_recall PASS
- [ ] test_time_factor_gentle PASS

---

## Phase 5: COUNCIL & SHIP (30 phút)

```bash
pip install -e .
openclaw gateway restart
```

### Checklist Phase 5
- [ ] Council score ≥ 8/10
- [ ] Benchmark: 180-day recall ≥ 90%
- [ ] pip install clean
- [ ] OpenClaw plugin hoạt động
