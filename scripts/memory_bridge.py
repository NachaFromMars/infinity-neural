"""Memory Bridge — Sync MEMORY.md ↔ Infinity Neural Graph.

Bridges OpenClaw's file-based memory with InfinityNeural's graph memory.
Two-way sync: file changes → graph, graph recalls → file annotations.

Usage:
    python memory_bridge.py --import-once    # Import MEMORY.md into graph
    python memory_bridge.py --sync           # One-time bidirectional sync
    python memory_bridge.py --watch          # Continuous watch mode
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_workspace() -> Path:
    """Get OpenClaw workspace path."""
    workspace = os.environ.get("OPENCLAW_WORKSPACE")
    if workspace:
        return Path(workspace)
    # Default paths
    for p in [
        Path.home() / ".openclaw" / "workspace",
        Path.home() / ".clawd" / "workspace",
    ]:
        if p.exists():
            return p
    return Path.home() / ".openclaw" / "workspace"


def get_memory_file() -> Path:
    """Get MEMORY.md path."""
    return get_workspace() / "MEMORY.md"


def get_daily_dir() -> Path:
    """Get memory/ daily notes directory."""
    d = get_workspace() / "memory"
    d.mkdir(exist_ok=True)
    return d


def get_state_file() -> Path:
    """Get bridge state file for tracking sync."""
    d = get_workspace() / "memory"
    d.mkdir(exist_ok=True)
    return d / "bridge-state.json"


def load_state() -> dict:
    """Load bridge state."""
    sf = get_state_file()
    if sf.exists():
        try:
            return json.loads(sf.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_sync": None, "memory_md_hash": None, "imported_sections": []}


def save_state(state: dict) -> None:
    """Save bridge state."""
    sf = get_state_file()
    sf.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


def hash_content(content: str) -> str:
    """Hash content for change detection."""
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def parse_memory_sections(content: str) -> list[dict]:
    """Parse MEMORY.md into sections with headers and content."""
    sections = []
    current_header = "ROOT"
    current_lines: list[str] = []

    for line in content.split("\n"):
        if line.startswith("## "):
            if current_lines:
                sections.append({
                    "header": current_header,
                    "content": "\n".join(current_lines).strip(),
                    "hash": hash_content("\n".join(current_lines)),
                })
            current_header = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append({
            "header": current_header,
            "content": "\n".join(current_lines).strip(),
            "hash": hash_content("\n".join(current_lines)),
        })

    return [s for s in sections if s["content"]]


def classify_memory(header: str, content: str) -> str:
    """Classify memory as ETERNAL, ANCHOR, or regular."""
    header_lower = header.lower()
    content_lower = content.lower()

    # ETERNAL: identity, preferences, core truths
    eternal_keywords = [
        "identity", "name", "who", "preference", "rule", "principle",
        "quy tắc", "tên", "danh tính", "sở thích", "nguyên tắc",
    ]
    if any(kw in header_lower or kw in content_lower[:100] for kw in eternal_keywords):
        return "ETERNAL"

    # ANCHOR: workspace, tools, config, structure
    anchor_keywords = [
        "workspace", "tool", "config", "setup", "infrastructure",
        "công cụ", "cài đặt", "cấu hình",
    ]
    if any(kw in header_lower or kw in content_lower[:100] for kw in anchor_keywords):
        return "ANCHOR"

    return "ENTITY"


async def import_memory_to_graph(memory_file: Path, brain_name: str = "openclaw-brain") -> int:
    """Import MEMORY.md sections into InfinityNeural graph via CLI."""
    if not memory_file.exists():
        print(f"⚠️  {memory_file} not found")
        return 0

    content = memory_file.read_text(encoding="utf-8")
    sections = parse_memory_sections(content)
    imported = 0

    for section in sections:
        mem_type = classify_memory(section["header"], section["content"])
        text = f"[{section['header']}] {section['content'][:500]}"

        # Use nmem CLI to remember
        cmd = f'nmem remember "{text}"'
        if mem_type == "ETERNAL":
            cmd = f'nmem eternal set "{section["header"]}" "{section["content"][:300]}"'

        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "NEURALMEMORY_BRAIN": brain_name},
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                imported += 1
                print(f"  ✅ [{mem_type}] {section['header']}")
            else:
                print(f"  ⚠️  [{mem_type}] {section['header']} — {stderr.decode()[:100]}")
        except Exception as e:
            print(f"  ❌ [{mem_type}] {section['header']} — {e}")

    return imported


async def import_daily_notes(daily_dir: Path, brain_name: str = "openclaw-brain") -> int:
    """Import daily memory/*.md files into graph."""
    imported = 0
    for md_file in sorted(daily_dir.glob("*.md")):
        if md_file.name.startswith("bridge-") or md_file.name.startswith("heartbeat"):
            continue
        content = md_file.read_text(encoding="utf-8")
        if not content.strip():
            continue

        text = f"[Daily {md_file.stem}] {content[:500]}"
        try:
            proc = await asyncio.create_subprocess_shell(
                f'nmem remember "{text}"',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "NEURALMEMORY_BRAIN": brain_name},
            )
            await proc.communicate()
            if proc.returncode == 0:
                imported += 1
                print(f"  ✅ {md_file.name}")
        except Exception as e:
            print(f"  ❌ {md_file.name} — {e}")

    return imported


async def sync_once(brain_name: str = "openclaw-brain") -> None:
    """One-time sync: MEMORY.md → graph."""
    state = load_state()
    memory_file = get_memory_file()

    if not memory_file.exists():
        print("⚠️  MEMORY.md not found. Nothing to sync.")
        return

    content = memory_file.read_text(encoding="utf-8")
    current_hash = hash_content(content)

    if current_hash == state.get("memory_md_hash"):
        print("✅ MEMORY.md unchanged since last sync. Skipping.")
        return

    print(f"🔄 Syncing MEMORY.md → InfinityNeural graph...")
    imported = await import_memory_to_graph(memory_file, brain_name)
    print(f"\n📊 Imported {imported} sections from MEMORY.md")

    # Also sync daily notes
    daily_dir = get_daily_dir()
    daily_count = await import_daily_notes(daily_dir, brain_name)
    print(f"📊 Imported {daily_count} daily notes")

    state["memory_md_hash"] = current_hash
    state["last_sync"] = datetime.now().isoformat()
    save_state(state)
    print(f"\n✅ Sync complete. Total: {imported + daily_count} memories")


async def watch_mode(brain_name: str = "openclaw-brain", interval: int = 60) -> None:
    """Watch MEMORY.md for changes and auto-sync."""
    print(f"👁️  Watching MEMORY.md (interval: {interval}s)")
    print(f"   Brain: {brain_name}")
    print(f"   Press Ctrl+C to stop\n")

    last_hash = None
    while True:
        try:
            memory_file = get_memory_file()
            if memory_file.exists():
                content = memory_file.read_text(encoding="utf-8")
                current_hash = hash_content(content)
                if current_hash != last_hash:
                    if last_hash is not None:
                        print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] Change detected!")
                        await sync_once(brain_name)
                    last_hash = current_hash
            await asyncio.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 Watch stopped.")
            break
        except Exception as e:
            print(f"⚠️  Error: {e}")
            await asyncio.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Infinity Memory Bridge")
    parser.add_argument("--import-once", action="store_true", help="Import MEMORY.md once")
    parser.add_argument("--sync", action="store_true", help="One-time bidirectional sync")
    parser.add_argument("--watch", action="store_true", help="Continuous watch mode")
    parser.add_argument("--brain", default="openclaw-brain", help="Brain name")
    parser.add_argument("--interval", type=int, default=60, help="Watch interval (seconds)")
    args = parser.parse_args()

    if args.import_once:
        asyncio.run(import_memory_to_graph(get_memory_file(), args.brain))
    elif args.sync:
        asyncio.run(sync_once(args.brain))
    elif args.watch:
        asyncio.run(watch_mode(args.brain, args.interval))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
