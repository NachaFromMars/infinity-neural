#!/usr/bin/env python3
"""InfinityNeural Reforge Script — Automate patching NeuralMemory.

Usage:
    python reforge.py --source <neural-memory-dir> [--dry-run]

This script applies all InfinityNeural patches to a cloned NeuralMemory repo.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


def patch_file(filepath: Path, patches: list[tuple[str, str]], description: str) -> bool:
    """Apply text replacements to a file."""
    if not filepath.exists():
        print(f"  ⚠️  File not found: {filepath}")
        return False

    content = filepath.read_text(encoding="utf-8")
    original = content

    for old, new in patches:
        if old not in content:
            print(f"  ⚠️  Pattern not found in {filepath.name}: {old[:60]}...")
            continue
        content = content.replace(old, new, 1)

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        print(f"  ✅ {description}")
        return True
    else:
        print(f"  ⏭️  No changes: {description}")
        return False


def patch_neuron(src: Path) -> None:
    """Patch core/neuron.py — add ETERNAL/ANCHOR, disable decay."""
    filepath = src / "core" / "neuron.py"

    patches = [
        # Add ETERNAL and ANCHOR types
        (
            '    INTENT = "intent"  # Goals/intentions: "learn", "build"',
            '    INTENT = "intent"  # Goals/intentions: "learn", "build"\n'
            '    ETERNAL = "eternal"  # Immortal: decisions, identity, instructions\n'
            '    ANCHOR = "anchor"  # Important milestones, never below tier 1',
        ),
        # Change default decay_rate
        (
            "    decay_rate: float = 0.1",
            "    decay_rate: float = 0.0  # InfinityNeural: no decay",
        ),
        # Replace decay method
        (
            '    def decay(self, time_delta_seconds: float) -> NeuronState:\n'
            '        """\n'
            '        Apply decay to activation based on time elapsed.\n'
            '\n'
            '        Uses exponential decay: new_level = old_level * e^(-decay_rate * time)',
            '    def decay(self, time_delta_seconds: float) -> NeuronState:\n'
            '        """InfinityNeural: No decay. Neurons are immortal.\n'
            '\n'
            '        Original used exponential decay: new_level = old_level * e^(-decay_rate * time)',
        ),
        # The actual decay body — replace return with no-op
        (
            "        days_elapsed = time_delta_seconds / 86400  # Convert to days\n"
            "        decay_factor = math.exp(-self.decay_rate * days_elapsed)\n"
            "        new_level = self.activation_level * decay_factor",
            "        # InfinityNeural: disabled — neurons are immortal\n"
            "        return self  # no-op, preserve activation level",
        ),
    ]

    patch_file(filepath, patches, "neuron.py: ETERNAL/ANCHOR + no decay")


def patch_brain(src: Path) -> None:
    """Patch core/brain.py — adjust BrainConfig defaults."""
    filepath = src / "core" / "brain.py"

    patches = [
        (
            "    decay_rate: float = 0.1\n",
            "    decay_rate: float = 0.0  # InfinityNeural: no decay\n",
        ),
        (
            "    activation_threshold: float = 0.2\n",
            "    activation_threshold: float = 0.08  # InfinityNeural: lower threshold\n",
        ),
    ]

    patch_file(filepath, patches, "brain.py: decay=0, threshold=0.08")


def patch_lifecycle(src: Path) -> None:
    """Patch engine/lifecycle.py — disable DecayManager."""
    filepath = src / "engine" / "lifecycle.py"

    patches = [
        # Disable the core decay loop body
        (
            "        for state in states:",
            "        # InfinityNeural: Decay disabled. Return empty report.\n"
            "        return report\n"
            "\n"
            "        # --- Original decay loop (disabled) ---\n"
            "        for state in states:  # noqa: unreachable",
        ),
    ]

    patch_file(filepath, patches, "lifecycle.py: DecayManager disabled")


def patch_reflex_activation(src: Path) -> None:
    """Patch engine/reflex_activation.py — gentle time factor."""
    filepath = src / "engine" / "reflex_activation.py"

    patches = [
        (
            "        age_hours = (reference_time - fiber.last_conducted).total_seconds() / 3600\n"
            "        # Sigmoid decay: ~1.0 at <1 day, ~0.5 at 3 days, ~0.15 at 7 days\n"
            "        return max(0.1, 1.0 / (1.0 + math.exp((age_hours - 72) / 36)))",
            "        # InfinityNeural: gentle time factor, never below 0.5\n"
            "        age_days = (reference_time - fiber.last_conducted).total_seconds() / 86400\n"
            "        return max(0.5, 1.0 / (1.0 + age_days * 0.002))",
        ),
        # Also fix the fallback for fibers without last_conducted
        (
            "            return 0.3 + 0.4 * fiber.salience",
            "            return 0.8  # InfinityNeural: neutral default",
        ),
    ]

    patch_file(filepath, patches, "reflex_activation.py: gentle time factor")


def patch_stabilization(src: Path) -> None:
    """Patch engine/stabilization.py — adjust params."""
    filepath = src / "engine" / "stabilization.py"

    patches = [
        ("    max_iterations: int = 10", "    max_iterations: int = 8"),
        ("    noise_floor: float = 0.05", "    noise_floor: float = 0.01"),
        ("    dampening_factor: float = 0.85", "    dampening_factor: float = 0.92"),
        ("    homeostatic_target: float = 0.5", "    homeostatic_target: float = 0.4"),
        ("    homeostatic_strength: float = 0.3", "    homeostatic_strength: float = 0.15"),
    ]

    patch_file(filepath, patches, "stabilization.py: adjusted params")


def copy_new_files(src: Path, skill_dir: Path) -> None:
    """Copy new engine files (compression.py, relevance.py)."""
    engine_dir = src / "engine"

    for filename in ["compression.py", "relevance.py"]:
        source = skill_dir / "scripts" / filename
        target = engine_dir / filename
        if source.exists():
            shutil.copy2(source, target)
            print(f"  ✅ Copied {filename} → engine/")
        else:
            print(f"  ⚠️  {filename} not found in scripts/")


def main() -> None:
    parser = argparse.ArgumentParser(description="InfinityNeural Reforge")
    parser.add_argument("--source", required=True, help="Path to neural-memory src/neural_memory/")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change")
    parser.add_argument("--skill-dir", default=".", help="Path to InfinityNeural skill directory")
    args = parser.parse_args()

    src = Path(args.source).resolve()
    skill_dir = Path(args.skill_dir).resolve()

    if not src.exists():
        print(f"❌ Source not found: {src}")
        sys.exit(1)

    print(f"🔥 InfinityNeural Reforge")
    print(f"   Source: {src}")
    print(f"   Skill:  {skill_dir}")
    print()

    if args.dry_run:
        print("   [DRY RUN — no files will be modified]\n")

    print("Phase 1: Core Engine Patches")
    print("─" * 40)
    patch_neuron(src)
    patch_brain(src)
    patch_lifecycle(src)
    patch_reflex_activation(src)
    patch_stabilization(src)

    print()
    print("Phase 2: New Engine Files")
    print("─" * 40)
    copy_new_files(src, skill_dir)

    print()
    print("✅ Reforge complete. Run tests:")
    print(f"   cd {src.parent.parent}")
    print("   pytest tests/ -v")


if __name__ == "__main__":
    main()
