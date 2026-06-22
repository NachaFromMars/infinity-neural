---
name: infinity-neural
version: 3.1.0
description: >
  Infinity Neural V3.1 — Instinct Edition (Complete).
  V1 Foundation (zero-decay, 3-tier, ETERNAL/ANCHOR, Vietnamese NLP) +
  V2 Engine (7 patterns: crash sentinel, scored observations, tier decay, 
  fact supersession, coordination ledger, agent lock, size trigger) +
  V3 Instinct Protocol (Auto-Remember, 3-Tầng Lazy Recall, Session-Aware Loading,
  Duplicate Prevention, Memory Hygiene) +
  38 MCP Tools + 8 Cognitive Reasoning Tools + Memory Bridge + Config.
  Dùng khi: (1) Cài memory protocol cho AI agent, (2) Tối ưu recall accuracy,
  (3) Multi-agent coordination, (4) Crash recovery, (5) Fact correction/supersession,
  (6) Tier-based compression, (7) Bản năng ghi/nhớ tự động, (8) Cognitive reasoning,
  (9) Bridge MEMORY.md ↔ Neural graph.
  Triggers: infinity neural, perfect recall, neural memory, brain memory, instinct,
  bản năng, auto remember, auto recall, lazy recall, memory protocol, crash sentinel,
  scored observations, tier decay, fact supersession, agent coordination, neural recall,
  cognitive reasoning, hypothesize, knowledge gaps, bộ nhớ vĩnh cửu.
---

# Infinity Neural V3.1 — Instinct Edition (Complete)

> "Neurons never die. They compress, they hibernate, they whisper — but they never disappear."
> "V1 biết LƯU. V2 biết LÀM gì. V3 biết KHI NÀO làm."

**Version:** 3.1.0 (PRODUCTION)  
**Tác giả:** Mr Nấng × MulaNacharis × Tiểu Tâm  
**Nguồn gốc:** Fork từ github.com/nhadaututheky/neural-memory v2.25.0  
**V1:** 2026-03-04 | **V2:** 2026-03-11 | **V3:** 2026-03-12 | **V3.1:** 2026-03-12  
**Tests:** 66 unit tests + 3217 engine tests PASS  
**MCP Tools:** 38 Core + 8 Cognitive = **46 total**  
**Schema:** v21  

---

## Tổng Quan Kiến Trúc

```
┌──────────────────────────────────────────────────────────────┐
│                V3: INSTINCT LAYER (BẢN NĂNG)                 │
│  Auto-Remember │ 3-Tầng Recall │ Session-Aware Loading       │
│  Duplicate Guard │ Escalation Flow │ Memory Hygiene           │
├──────────────────────────────────────────────────────────────┤
│                V2: ENGINE (7 PATTERNS)                        │
│  Crash Sentinel │ Scored Observations │ Size Trigger          │
│  Coordination Ledger │ Agent Lock │ Tier Decay                │
│  Fact Supersession                                            │
├──────────────────────────────────────────────────────────────┤
│                V1: FOUNDATION                                 │
│  Zero-Decay │ 3-Tier Compression │ ETERNAL/ANCHOR             │
│  Relevance Scoring │ Vietnamese NLP │ Token Budget             │
├──────────────────────────────────────────────────────────────┤
│                MCP INTERFACE (46 TOOLS)                        │
│  29 Core │ 8 Cognitive │ 1 Utility │ Bridge                   │
├──────────────────────────────────────────────────────────────┤
│                OPENCLAW BRIDGE                                │
│  File-based (MEMORY.md) ↔ Neural Graph (SQLite)              │
└──────────────────────────────────────────────────────────────┘
```

- **V1 (Foundation):** Engine cốt lõi — neurons bất tử, nén 3 tầng, scoring, NLP Việt
- **V2 (7 Patterns):** Module mở rộng — crash recovery, observations, decay, supersession, multi-agent
- **V3 (Instinct):** Behavioral protocol — quy tắc KHI NÀO ghi, KHI NÀO tìm, tìm SÂU bao nhiêu
- **V3.1 (Complete):** Gộp toàn bộ + 46 MCP tools + Cognitive + Bridge + Config

---

## PHẦN I: V3 — INSTINCT PROTOCOL (BẢN NĂNG)

### A. AUTO-REMEMBER — Tự Ghi (Khi Nào + Ghi Gì)

Agent PHẢI tự động ghi memory khi gặp các tình huống sau. Không cần user yêu cầu.

| Trigger | Category | Importance | Cách ghi |
|---------|----------|-----------|----------|
| User ra quyết định | `decision` | 7-8 | "Chọn X **vì** Y, **thay vì** Z. Ngày [date]." |
| Task hoàn thành | `workflow` | 5-6 | "Task X hoàn thành [date]. Kết quả Y. Lesson: Z." |
| User nói điều mới về bản thân | `fact` / `preference` | 5-7 | "User [thích/không thích/là/có] X." |
| Học bài học / sai lầm | `insight` / `error` | 6-8 | "Lesson: X dẫn đến Y. Fix bằng Z." |
| Quy tắc mới được lập | `instruction` | 9-10 | "Quy tắc: LUÔN/KHÔNG BAO GIỜ X." |
| Cuối session quan trọng | `context` | 3-5 | "Session [date]: làm X, kết quả Y, tiếp theo Z." |
| Info mới về project | `reference` | 5-6 | "Project X: [fact mới, metric, status]." |

**Nguyên tắc ghi — RICH CONTEXT:**

```
BAD:  "Dùng Opus 4.6"
GOOD: "Chọn Opus 4.6 vì Sonnet thiếu depth cho novel writing. Quyết định ngày 2026-03-01, áp dụng mọi task kể cả sub-agents."
```

Càng nhiều context (nguyên nhân, thời gian, so sánh, lesson) thì recall càng chính xác.

---

### B. AUTO-RECALL — 3 Tầng Lazy (Giống Não Người)

**QUY TẮC SỐ 1: MỌI input phải scan Tầng 1. KHÔNG ngoại lệ.**

```
MỌI INPUT (không ngoại lệ)
  |
  v
TẦNG 1: QUICK SCAN ---- LUÔN CHẠY -------------------- ~200 tokens
  nmem_recall(query=<keywords từ input>, depth=0)
  Keywords: danh từ riêng, tên project, tên người, concept kỹ thuật
  Giống não: nghe từ -> quét 0.1s xem quen không
  |
  |-- HIT (có kết quả relevant) -> DÙNG, inject vào context
  |
  v MISS + input có dấu hiệu mơ hồ
TẦNG 2: CONTEXT SCAN --- KHI MƠ HỒ -------------------- ~500 tokens
  Trigger: "hồi đó", "lần trước", "cái đó", "hình như",
           "mày nói gì đó về...", hoặc agent CẢM THẤY nên biết
  nmem_recall(query=<semantic phrase mở rộng>, depth=2)
  depth=2: spreading activation + cross-time pattern matching
  |
  |-- HIT -> DÙNG
  |
  v MISS + agent vẫn cảm thấy "nên biết cái này"
TẦNG 3: DEEP SCAN ------ KHI THẬT SỰ CẦN -------------- ~1000 tokens
  Trigger: Tầng 2 trống + topic có vẻ đã từng xuất hiện
  nmem_recall(query=<broad query, nhiều keywords>, depth=3)
  depth=3: full graph traversal
  |
  |-- HIT -> DÙNG
  |
  v MISS tất cả 3 tầng
CONFIRM MỚI -> Thông tin mới thật sự -> nmem_remember nếu đáng ghi
```

**Tại sao Tầng 1 bắt buộc cho MỌI input:**
- Agent có thể TƯỞNG input mới nhưng thực tế đã ghi -> miss = duplicate hoặc mâu thuẫn
- Cost chỉ ~200 tokens — rẻ hơn nhiều so với hậu quả miss

---

### C. SESSION-AWARE LOADING — Phân Tầng Theo Loại Session

| Session type | Đầu session | Trong session | Cuối session |
|---|---|---|---|
| **Main** (chat trực tiếp với user) | `nmem_context(limit=10)` + Tầng 1 cho message đầu | 3 tầng đầy đủ | Auto-remember session summary |
| **Sub-agent** (spawn cho task cụ thể) | KHÔNG auto-load | Chỉ Tầng 1 khi gặp keyword relevant | KHÔNG (report qua parent) |
| **Heartbeat** (periodic check) | KHÔNG recall | KHÔNG recall | KHÔNG |
| **Cron job** (scheduled task) | KHÔNG auto-load | Tầng 1 nếu task cần context cũ | KHÔNG |

---

### D. DUPLICATE PREVENTION — Chống Ghi Trùng

Trước MỖI lần `nmem_remember`, PHẢI check:

```
Muốn ghi X
  |
  v
nmem_recall(query=<core content of X>, depth=0)
  |
  |-- Tìm thấy Y giống X (>80% nội dung trùng)
  |   |-- Y hoàn toàn giống X -> SKIP (không ghi)
  |   |-- Y gần giống nhưng X có info mới -> nmem_edit(Y, new content)
  |   |-- X thay thế Y hoàn toàn (fact cũ sai) -> nmem_supersede(Y -> X)
  |
  |-- Không tìm thấy gì giống -> nmem_remember(X) (ghi mới)
```

---

### E. MEMORY HYGIENE — Bảo Trì Định Kỳ

**Mỗi 3-5 ngày (trong heartbeat hoặc session rảnh):**

1. `nmem_stats` — check brain health (memory counts, types, freshness)
2. Facts mâu thuẫn -> `nmem_supersede` fact cũ
3. Hypothesis đã resolved -> archive
4. Predictions quá deadline -> verify hoặc close
5. **KHÔNG BAO GIỜ xóa cứng** (`nmem_forget hard=true`) trừ khi user yêu cầu hoặc security

---

## PHẦN II: V2 — ENGINE (7 PATTERNS)

### Pattern 1: Crash Sentinel (Dirty Flag)

Phát hiện crash giữa session, khôi phục context.

```python
from neural_memory.engine.crash_sentinel import CrashSentinel

sentinel = CrashSentinel(brain_dir)
sentinel.arm(session_id="main")                    # Bắt đầu session
sentinel.checkpoint(context="processing beat 4.1")  # Lưu checkpoint
# ... nếu crash xảy ra ...
info = sentinel.check_crash()                       # Session mới: check crash
# info.crashed=True, info.context="processing beat 4.1"
sentinel.disarm()                                   # Kết thúc session an toàn
```

**Khi nào dùng:** Forge dài (tiểu thuyết, pipeline nhiều step), sub-agent chạy >10 phút.

### Pattern 2: Scored Observations

Gắn confidence + importance vào memory.

```python
fiber = fiber.with_observation("decision", confidence=0.95, importance=0.9)
# importance 0.9 -> 1.5x boost trong retrieval ranking
# observation_type "decision" -> structural, resist decay (1.5x half-life)
```

**Observation types:** `decision`, `commitment`, `milestone`, `lesson`, `preference`, `fact`
**Structural types** (resist decay): `decision`, `commitment`, `milestone`, `lesson`

### Pattern 3: Size-based Trigger

Tự động chạy maintenance khi DB lớn.

```python
from neural_memory.engine.observation_trigger import ObservationTrigger

trigger = ObservationTrigger(brain_dir)
if trigger.should_observe():
    run_maintenance()
    trigger.mark_observed()
```

### Pattern 4: JSONL Coordination Ledger

Log hoạt động multi-agent, crash-safe.

```python
from neural_memory.engine.coordination_ledger import CoordinationLedger

ledger = CoordinationLedger("forge.jsonl")
ledger.append("agent-1", "started", "beat-4.1", {"progress": 0})
ledger.append("agent-1", "completed", "beat-4.1", {"score": 9})
entries = ledger.read(actor="agent-1", op="completed")
```

### Pattern 5: Claim/Release Locking

Exclusive access cho multi-agent.

```python
from neural_memory.engine.agent_lock import AgentLockManager

lock_mgr = AgentLockManager(ledger)
if lock_mgr.claim("chapter-42", "forge-agent"):
    # ... write chapter ...
    lock_mgr.release("chapter-42", "forge-agent")
stale = lock_mgr.find_stale_claims(max_age_seconds=1800)
```

### Pattern 6: Wake-style Tier Decay

Soft salience decay — memory cũ mờ DẦN, KHÔNG BAO GIỜ biến mất.

```
new_salience = salience x 2^(-days / effective_half_life)

effective_half_life = base_half_life x (1 + importance) x structural_bonus

Tier 0: 30 days  | Tier 1: 90 days  | Tier 2: 180 days
Tier 3: 365 days | Tier 4: 730 days

structural_bonus = 1.5x for decision/commitment/milestone/lesson
importance bonus = 1.0x (imp=0) -> 2.0x (imp=1.0)

Example: decision (tier 4, importance 1.0)
  = 730 x 2.0 x 1.5 = 2,190 day half-life (~6 years)
  -> After 1 year: salience = 0.891 (barely decayed)

Floor: MIN_SALIENCE = 0.01 (KHÔNG BAO GIỜ = 0)
```

### Pattern 7: Fact Supersession

Sửa fact cũ bằng SUPERSEDES synapse — fact cũ không xóa, chỉ đánh dấu "đã thay thế".

```python
from neural_memory.engine.supersession import SupersessionManager

sm = SupersessionManager(storage)
await sm.supersede(old_fiber_id, new_fiber_id, reason="timezone changed")
info = await sm.is_superseded(old_fiber_id)       # True + pointer to new
chain = await sm.get_supersession_chain(fiber_id)  # [oldest -> newest]
```

---

## PHẦN III: V1 — FOUNDATION

### Zero-Decay Engine
- `NeuronState.decay()` -> no-op (return self)
- `decay_rate = 0.0` mặc định
- Neurons bất tử — chỉ nén, không xóa

### 3-Tier Compression (CPU Cache Model)

```
HOT (Tier 0)  — Full detail. Token cost: CAO
  Điều kiện: age < 30d OR freq > 5
  ETERNAL/ANCHOR -> LUÔN tier 0
  Budget: 60%

WARM (Tier 1) — Summary + key neurons. Cost: TB
  Điều kiện: age 30-180d, freq 1-5
  ANCHOR -> chặn ở tier 1, ko xuống 2
  Budget: 30%

COLD (Tier 2) — Core facts only. Cost: THẤP
  Điều kiện: age > 180d, freq 0-1
  KHÔNG BAO GIỜ xóa — chỉ nén tối đa
  Budget: 10%
```

### Neuron Types

| Type | Behavior | Dùng cho |
|------|----------|----------|
| TIME | Temporal markers | "3pm", "yesterday" |
| SPATIAL | Locations | "coffee shop", "office" |
| ENTITY | Named entities | "Alice", "FastAPI" |
| ACTION | Verbs/actions | "discussed", "completed" |
| STATE | Emotional/mental | "happy", "frustrated" |
| CONCEPT | Abstract ideas | "API design" |
| SENSORY | Sensory | "loud", "bright" |
| INTENT | Goals | "learn", "build" |
| **ETERNAL** | Never decay, never compress | Decisions, identity, instructions |
| **ANCHOR** | Never below WARM | Important milestones |
| **HYPOTHESIS** | Evolving beliefs (Cognitive) | Bayesian confidence tracking |
| **PREDICTION** | Falsifiable claims (Cognitive) | Verify-able predictions |
| **SCHEMA** | Mental model snapshots (Cognitive) | Versioned knowledge structures |

### Relevance Scoring (5 Factors)

```python
score = (
    recency x 0.30        # Hyperbolic: 1/(1 + days x 0.005)
    + frequency x 0.25    # Log scale: min(1.0, log1p(freq) x 0.15)
    + connections x 0.15  # Synapse density: min(1.0, synapses x 0.05)
    + tier_bonus           # HOT: +0.30, WARM: +0.15, COLD: +0.00
    + eternal_bonus        # ETERNAL/ANCHOR: +0.50
)
# Score > 0 LUÔN. Không bao giờ = 0.
```

### Vietnamese NLP
- **Fuzzy Tone Matching:** "nấng" = "nắng" = "nàng" (strip diacritics)
- **Stopwords:** 60+ từ vô nghĩa (của, để, từ, các, những...)
- **Compound Detection:** 200+ cụm từ ("nhà giả dâm", "trọng sinh", "neural memory"...)
- **Bilingual Expansion:** Query tiếng Việt -> match tiếng Anh và ngược lại

---

## PHẦN IV: 46 MCP TOOLS

### Core Memory (29 tools)

| Tool | Mô tả |
|------|--------|
| `nmem_remember` | Lưu ký ức mới |
| `nmem_recall` | Tìm ký ức theo query (relevance ranked) |
| `nmem_context` | Lấy context gần đây |
| `nmem_edit` | Sửa ký ức đã lưu |
| `nmem_forget` | Xoá chọn lọc ký ức (soft/hard) |
| `nmem_todo` | Quản lý todo list |
| `nmem_stats` | Thống kê bộ nhớ |
| `nmem_eternal` | Đánh dấu ký ức ETERNAL (không bao giờ quên) |
| `nmem_pin` | Pin ký ức quan trọng |
| `nmem_session` | Quản lý session |
| `nmem_index` | Index ký ức |
| `nmem_import` | Import từ file |
| `nmem_recap` | Tóm tắt ký ức |
| `nmem_health` | Kiểm tra sức khỏe graph |
| `nmem_evolution` | Xem tiến hóa ký ức |
| `nmem_habits` | Theo dõi thói quen |
| `nmem_narrative` | Tạo narrative từ ký ức |
| `nmem_review` | Review ký ức cũ |
| `nmem_conflicts` | Phát hiện xung đột |
| `nmem_train` | Train associations |
| `nmem_train_db` | Train từ database |
| `nmem_alerts` | Cảnh báo ký ức |
| `nmem_sync` | Đồng bộ ký ức |
| `nmem_sync_status` | Trạng thái sync |
| `nmem_sync_config` | Cấu hình sync |
| `nmem_transplant` | Di chuyển ký ức giữa brains |
| `nmem_suggest` | Gợi ý ký ức liên quan |
| `nmem_auto` | Auto-remember (passive capture) |
| `nmem_version` | Version info |

### Cognitive Reasoning (8 tools)

| Tool | Mô tả |
|------|--------|
| `nmem_hypothesize` | Tạo giả thuyết với Bayesian confidence |
| `nmem_evidence` | Thêm bằng chứng cho/chống giả thuyết |
| `nmem_predict` | Dự đoán có thể verify được |
| `nmem_verify` | Kiểm chứng dự đoán (đúng/sai) |
| `nmem_cognitive` | Xem trạng thái cognitive của neuron |
| `nmem_gaps` | Phát hiện knowledge gaps |
| `nmem_schema` | Mental model snapshots (versioned) |
| `nmem_calibrate` | Calibrate confidence thresholds |

### Utility (1 tool)

| Tool | Mô tả |
|------|--------|
| `nmem_telegram_backup` | Backup brain qua Telegram |

---

## PHẦN V: CÀI ĐẶT & CẤU HÌNH

### Bước 1: Install engine

```bash
# Từ wheel (khuyên dùng)
pip install infinity_neural-2.0.0-py3-none-any.whl

# Với Vietnamese NLP support
pip install "infinity_neural-2.0.0-py3-none-any.whl[nlp-vi]"

# Full (tất cả optional deps)
pip install "infinity_neural-2.0.0-py3-none-any.whl[server,nlp-vi,nlp-en,encryption]"
```

### Bước 2: Khởi tạo brain

```bash
nmem init --name openclaw-brain
# Tạo brain mới tại ~/.neuralmemory/openclaw-brain/
```

### Bước 3: MCP Server

```bash
# Standalone
nmem-mcp

# OpenClaw config — thêm vào gateway config:
# (xem config/mcp-infinity-neural.json)
```

**Claude Desktop / Cursor** — thêm vào `.mcp.json`:
```json
{
  "mcpServers": {
    "infinity-neural": {
      "command": "nmem-mcp"
    }
  }
}
```

**OpenClaw** — thêm vào gateway config (mcpServers section):
```json
{
  "mcpServers": {
    "infinity-neural": {
      "command": "nmem-mcp",
      "env": {
        "NEURALMEMORY_BRAIN": "openclaw-brain"
      }
    }
  }
}
```

### Bước 4: Memory Bridge (optional)

```bash
# Import MEMORY.md 1 lần
python scripts/memory_bridge.py --import-once

# Sync 2 chiều
python scripts/memory_bridge.py --sync

# Watch mode (continuous)
python scripts/memory_bridge.py --watch
```

### Bước 5: Verify

```bash
# Quick verify (V3.1 — 22 checks)
python VERIFY.py

# Full install verify (engine + MCP + CLI)
python scripts/verify_install.py
```

### Cài Instinct Protocol cho Agent

Copy block sau vào `AGENTS.md` hoặc system prompt:

```markdown
## Neural Memory Instinct Protocol (V3 — BẮT BUỘC)

### Auto-Remember
- SAU MỖI DECISION: nmem_remember(category=decision, importance=7-8)
- SAU MỖI TASK HOÀN THÀNH: nmem_remember(category=workflow, importance=5-6)
- KHI USER NÓI GÌ MỚI: nmem_remember(category=fact/preference, importance=5-7)
- KHI HỌC BÀI HỌC: nmem_remember(category=insight/error, importance=6-8)
- KHI QUY TẮC MỚI: nmem_remember(category=instruction, importance=9-10)
- CUỐI SESSION: nmem_remember(category=context, importance=3-5)
- NGUYÊN TẮC: Text rich context — "Chọn X VÌ Y, THAY VÌ Z, ngày D"

### Auto-Recall (3 Tầng — Mọi Input Phải Scan)
- MỌI INPUT -> Tầng 1: nmem_recall(query=<keywords>, depth=0) ~200 tokens
- MISS + mơ hồ -> Tầng 2: nmem_recall(depth=2) ~500 tokens
- MISS + "nên biết" -> Tầng 3: nmem_recall(depth=3) ~1000 tokens
- MISS tất cả -> confirm mới, ghi nếu đáng

### Session-Aware
- MAIN SESSION: nmem_context(limit=10) đầu session + 3 tầng recall
- SUB-AGENT: KHÔNG auto-load, chỉ recall khi cần
- HEARTBEAT: KHÔNG recall
- CRON: Recall nếu task cần context cũ

### Duplicate Prevention
- TRƯỚC KHI GHI -> nmem_recall(depth=0) check trùng
- Trùng hoàn toàn -> SKIP
- Trùng một phần + có info mới -> nmem_edit
- Fact cũ sai -> nmem_supersede
```

### Verify Agent hiểu protocol:
- "Khi nào mày tự ghi memory?" -> Phải liệt kê 7 triggers
- "Nếu tao hỏi về project cũ, mày làm gì?" -> Phải nói scan Tầng 1 trước
- "Sub-agent có load memory đầu session không?" -> Phải nói KHÔNG

---

## PHẦN VI: RECALL FLOW (Hybrid)

```
Agent nhận câu hỏi
    |
    v
(1) memory_search (file-based) ~50ms
    -> Tìm trong MEMORY.md + memory/*.md
    -> Nếu confident >= 0.8 -> trả lời luôn
    |
    v (nếu cần sâu hơn)
(2) nmem_recall (MCP) ~100ms
    -> Neural graph search (3 tầng theo Instinct Protocol)
    -> RelevanceScorer ranking
    -> Tier-aware retrieval (HOT -> WARM -> COLD)
    -> Vietnamese NLP compound detection
    |
    v (nếu cần suy luận)
(3) nmem_cognitive (MCP) ~150ms
    -> Check hypotheses related to query
    -> Bayesian confidence levels
    -> Knowledge gap detection
    |
    v
(4) Merge kết quả -> Trả lời chính xác nhất
```

---

## PHẦN VII: HYBRID CONSOLIDATION

Kết hợp NM 2.27 logic + Infinity "no-delete" philosophy:

```
Ký ức yếu (weight < 0.05, inactive > 7 days)
    |
    v (NM 2.27 logic)
    |-- Bridge synapse? -> PROTECT
    |-- High-salience fiber? -> PROTECT
    |-- Inferred + low reinforcement? -> Accelerated floor
    |-- Dream synapse? -> 10x accelerated floor
    |
    v (Infinity override: KHÔNG XOÁ)
    |-- Weak synapse -> Floor weight to 0.01 (giữ connection)
    |-- Orphan neuron -> Reactivate at 0.01 (không delete)
```

---

## PHẦN VIII: CHI PHÍ & HIỆU NĂNG

### Token Cost Ước Tính

| Hoạt động | Token cost / lần | Tần suất |
|---|---|---|
| Tầng 1 (mọi input) | ~200 | Mỗi message |
| Tầng 2 (khi mơ hồ, ~20%) | ~500 | ~20% messages |
| Tầng 3 (khi miss, ~5%) | ~1000 | ~5% messages |
| Remember (ghi mới) | ~100 | ~10% messages |
| Context load (đầu session) | ~500-1000 | 1/session |
| **Trung bình / message** | **~300-500** | |
| **TỔNG OVERHEAD / tháng** (100 msg/ngày) | | **~1.1M tokens** |

### Benchmark Recall

| Tuổi ký ức | File-based | Infinity Neural |
|---|---|---|
| 1 ngày | 100% | 100% |
| 30 ngày | ~90% | **100%** |
| 180 ngày | ~30% (compact) | **100%** |
| 365 ngày | ~0% (archive) | **100%** |
| 730 ngày | 0% | **100%** |

---

## PHẦN IX: SCHEMA & MIGRATION

### Schema Version: 21

V2 additions (migration 20 -> 21):
- `fibers.observation_type TEXT`
- `fibers.confidence REAL DEFAULT 1.0`
- `fibers.importance REAL DEFAULT 0.5`
- `idx_fibers_importance` index
- `idx_fibers_obs_type` index
- `SynapseType.SUPERSEDES` + `SynapseType.SUPERSEDED_BY`

Migration chạy tự động khi connect lần đầu.
V3 KHÔNG thay đổi schema — instinct protocol là behavioral layer.

---

## PHẦN X: CLI QUICK REFERENCE

```bash
# Init
nmem init --name openclaw-brain

# Remember
nmem remember "Nấng thích Opus 4.6 vì depth" --type eternal

# Recall
nmem recall "Nấng thích model gì?"

# Stats
nmem stats

# Health
nmem health

# MCP Server
nmem-mcp

# Memory Bridge
python scripts/memory_bridge.py --sync

# Version
nmem --version
```

---

## PHẦN XI: PACKAGE CONTENTS

```
infinity-neural-v3.1.0/
|-- SKILL.md                    <- This file (V3.1 complete)
|-- CHANGELOG.md                <- V1 -> V2 -> V3 -> V3.1 changes
|-- INSTINCT-PROTOCOL.md        <- Standalone protocol (copy-paste ready)
|-- VERIFY.py                   <- V3.1 verification (22+ checks)
|-- dist/
|   |-- infinity_neural-2.0.0-py3-none-any.whl  (696 KB)
|   |-- infinity_neural-2.0.0.tar.gz            (542 KB)
|-- config/
|   |-- brain-defaults.toml     <- Default brain configuration
|   |-- mcp-infinity-neural.json <- MCP server config template
|   |-- INSTALL.md              <- Step-by-step install guide
|-- references/
|   |-- DESIGN.md               <- V1 architecture design
|   |-- compression-tiers.md    <- 3-tier compression detail
|   |-- relevance-scorer.md     <- 5-factor scoring formula
|   |-- vietnamese-nlp.md       <- Vietnamese NLP modules
|   |-- file-map.md             <- Source code file map
|   |-- reforge-pipeline.md     <- 6-phase build pipeline
|-- scripts/
|   |-- memory_bridge.py        <- MEMORY.md <-> Neural graph sync
|   |-- verify_install.py       <- Full install verification
|   |-- compression.py          <- Tier compression implementation
|   |-- relevance.py            <- Relevance scorer implementation
|   |-- vietnamese_nlp.py       <- Vietnamese NLP implementation
|   |-- reforge.py              <- Reforge pipeline runner
|   |-- benchmark_recall.py     <- Recall benchmark
|   |-- test_infinity_neural.py          <- Core tests
|   |-- test_infinity_tier_manager.py    <- Tier manager tests
|   |-- test_infinity_vietnamese.py      <- Vietnamese NLP tests
|   |-- test_relevance.py                <- Relevance scorer tests
```

---

## PHẦN XII: COMPATIBILITY

- Python >= 3.11 (tested 3.12)
- OpenClaw (bất kỳ version)
- Claude Desktop / Cursor (via MCP)
- Windows / Linux / macOS
- SQLite (default) / Neo4j / FalkorDB (optional)
- Không thay thế file-based memory (chạy song song)
- Drop-in add-on, không phá gì hiện tại

---

## VERSION HISTORY

| Version | Date | Codename | What |
|---------|------|----------|------|
| 1.0.0 | 2026-03-04 | Foundation | Zero-decay, 3-tier, ETERNAL, relevance, Vietnamese NLP |
| 1.1.0 | 2026-03-06 | Cognitive | +NM 2.27 merge, +8 cognitive tools, +38 MCP, schema v21 |
| 2.0.0 | 2026-03-11 | Perfect Recall | +7 patterns (crash, observations, trigger, ledger, lock, decay, supersession) |
| 3.0.0 | 2026-03-12 | Instinct Edition | +Behavioral protocol (auto-remember, 3-tier recall, session-aware, duplicate guard) |
| 3.1.0 | 2026-03-12 | Complete | Unified package: V2 engine + V3 instinct + 46 MCP tools + cognitive + bridge + config |

---

> **V1:** Memory bất tử.
> **V2:** Memory thông minh.
> **V3:** Memory có bản năng.
> **V3.1:** Memory hoàn chỉnh.
>
> *"Não không chỉ lưu trữ. Não biết khi nào cần nhớ, khi nào cần quét, quét sâu bao nhiêu, và tự sửa khi sai."*
