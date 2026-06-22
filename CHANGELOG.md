# Infinity Neural — Changelog

## V3.1.0 (2026-03-12) — Complete Edition

### What's new in V3.1
V3.1 is a **unified package** that resolves packaging issues in V3.0.0 and merges
all components into a single, self-contained distribution.

**Fixes:**
- **CRITICAL:** Replaced V1 wheel (1.0.0) with V2 wheel (2.0.0) — V3.0.0 shipped the wrong engine
- VERIFY.py now passes 22/22 checks out of the box (V3.0.0 failed 12/22 with its bundled wheel)

**Restored from V1.1 (missing in V3.0.0):**
- `config/brain-defaults.toml` — Default brain configuration
- `config/mcp-infinity-neural.json` — MCP server config template
- `config/INSTALL.md` — Step-by-step install guide
- `scripts/memory_bridge.py` — MEMORY.md <-> Neural graph sync
- `scripts/verify_install.py` — Full install verification (engine + MCP + CLI)

**SKILL.md rewritten:**
- Merged V3 Instinct Protocol + V2 engine docs + V1 foundation
- Added 46 MCP tools documentation (29 core + 8 cognitive + 1 utility)
- Added 13 neuron types (including 3 cognitive: HYPOTHESIS, PREDICTION, SCHEMA)
- Added Hybrid Recall Flow (file-based -> MCP -> cognitive)
- Added Hybrid Consolidation docs (NM 2.27 + Infinity no-delete)
- Added token cost analysis and benchmark recall table
- Added complete CLI quick reference

**Updated:**
- VERIFY.py — Updated version references to 3.1.0
- CHANGELOG.md — Complete history V1 -> V3.1

### Meta
- Engine: infinity_neural-2.0.0 wheel (V2, schema v21, 7 patterns)
- Instinct Protocol: V3 behavioral layer (unchanged from V3.0.0)
- Total files: 27
- Total package: ~1.3 MB

---

## V3.0.0 (2026-03-12) — Instinct Edition

### New: Behavioral Instinct Layer
V3 did not modify engine code. V3 added a **behavioral protocol** on top of V2 engine.

- **Auto-Remember Protocol** — 7 trigger types with importance scoring
- **3-Tier Lazy Recall** — Brain-inspired escalation: Quick (depth=0) -> Context (depth=2) -> Deep (depth=3)
- **Session-Aware Loading** — Main (full), Sub-agent (minimal), Heartbeat (none), Cron (on-demand)
- **Duplicate Prevention** — Pre-check before every remember: skip/edit/supersede
- **Memory Hygiene** — Guidelines for periodic maintenance
- **INSTINCT-PROTOCOL.md** — Standalone portable protocol file
- **VERIFY.py** — 18 checks (V1 + V2 + V3 instinct presence)

### Known issues (fixed in V3.1)
- Package shipped with V1 wheel (1.0.0) instead of V2 wheel (2.0.0)
- Missing config files, memory_bridge.py, verify_install.py
- SKILL.md did not document MCP tools or cognitive reasoning

---

## V2.0.0 (2026-03-11) — Perfect Recall Edition (7 Patterns)

### New Modules
- **engine/crash_sentinel.py** (320 LOC) — Dirty flag crash detection
- **engine/observation_trigger.py** (190 LOC) — Size-based maintenance trigger
- **engine/coordination_ledger.py** (265 LOC) — JSONL append-only ledger
- **engine/agent_lock.py** (220 LOC) — Advisory claim/release locking
- **engine/tier_decay.py** (250 LOC) — Soft salience decay by tier
- **engine/supersession.py** (230 LOC) — Fact supersession via SUPERSEDES synapses

### Modified
- **core/fiber.py** (+65 LOC) — observation_type, confidence, importance fields
- **core/synapse.py** (+2 types) — SUPERSEDES / SUPERSEDED_BY
- **engine/retrieval.py** (+5 LOC) — Importance multiplier in scoring
- **engine/hooks.py** (+4 events) — SESSION_START/END/CHECKPOINT/CRASH_DETECTED
- **storage/sqlite_schema.py** — Migration 20 -> 21

### Tests
- 66 unit tests, 70+ inline verifications, 0 regressions

---

## V1.1.0 (2026-03-06) — Cognitive Edition

### Merged
- Combined Infinity Memory 1.0 + Neural Memory 2.27.1
- 38 MCP tools (29 core + 8 cognitive + 1 utility)
- Security: SQL injection fix in sqlite_synapses.py
- Schema v20 -> v21 with cognitive tables
- 3217 engine tests PASS

---

## V1.0.0 (2026-03-04) — Foundation

- Fork from neural-memory v2.25.0
- Zero-decay (Ebbinghaus disabled, decay() -> no-op)
- 3-tier compression (HOT 30d / WARM 180d / COLD infinity)
- ETERNAL/ANCHOR neuron types
- Relevance scoring (5 factors)
- Vietnamese NLP (200+ compound words, tone stripping, stopwords)
- 3124 tests PASS
