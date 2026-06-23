# infinity-neural — Zero-decay neural memory with instinct-level recall

> Neurons never die. V3.1 adds instinct-level auto-remember and 3-layer lazy recall so agents write and retrieve memories the way humans do — automatically, without being told.

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blueviolet)](https://github.com/NachaFromMars)

## Overview
Infinity Neural V3.1 is a complete neural memory system for OpenClaw agents. V1 established zero-decay storage with 3-tier compression (HOT/WARM/COLD), ETERNAL/ANCHOR neuron types, and Vietnamese NLP. V2 added 7 engine patterns: crash sentinel, scored observations, coordination ledger, agent lock, tier decay, fact supersession, and size-based triggers. V3 installs instinct-level behavior: auto-remember 7 trigger types, 3-layer lazy recall, session-aware loading, duplicate prevention, and memory hygiene. Ships with 46 MCP tools and a MEMORY.md↔neural graph bridge.

## Features
- **Zero decay** — no pruning, no forgetting; neurons compress but never die
- **3-tier** — HOT (active) / WARM (stable) / COLD (archived)
- **Auto-Remember** — 7 triggers: decision, workflow, fact, insight, instruction, context, reference
- **3-Layer Lazy Recall** — Tier 1 (~200 tokens) → Tier 2 (~500) → Tier 3 (~1000) on miss
- **Fact supersession** — correct stale facts without losing history
- **46 MCP tools** — 38 core + 8 cognitive (hypothesize, predict, verify, gaps, calibrate...)
- **Memory Bridge** — `scripts/memory_bridge.py` syncs MEMORY.md ↔ neural graph
- **Tested** — 66 unit + 3217 engine tests PASS, schema v21

## Trigger Keywords (OpenClaw)
infinity neural, neural memory, auto remember, auto recall, lazy recall, crash sentinel, fact supersession, agent coordination, bộ nhớ vĩnh cửu

## Related Skills
- [core-brain-mula](https://github.com/NachaFromMars/core-brain-mula) — zero-decay neural memory setup
- [memory-tiering](https://github.com/NachaFromMars/memory-tiering) — 3-tier memory management

---
Part of the [NachaFromMars](https://github.com/NachaFromMars) OpenClaw skill ecosystem.
