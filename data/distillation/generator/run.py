"""
run.py — Ana Orchestrator
===========================
1M örnek üretmek için batch mode destekli ana çalıştırma scripti.

Kullanım:
    # Tüm 1M'i üret (parça parça dosyalara yazar):
    python -m generator.run --total 1000000 --batch-size 50000

    # Tek bir batch üret:
    python -m generator.run --total 50000 --batch-size 50000 --start-id 1

    # Küçük test:
    python -m generator.run --total 100 --batch-size 100
"""

import argparse
import json
import os
import sys
import time
import random
from pathlib import Path

# Ensure the parent directory is in the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generator import config as C
from generator.task_generators import (
    campaign_diagnosis,
    copywriting,
    creative_brief,
    budget_rules,
    strategy_playbook,
    post_mortem,
    landing_offer,
    anomaly_triage,
    multi_channel,
    market_expansion,
)


# ──────────────────────────────────────────────
# TASK -> GENERATOR MAPPING
# ──────────────────────────────────────────────

TASK_GENERATORS = {
    "CAMPAIGN_DIAGNOSIS":      campaign_diagnosis.generate,
    "COPYWRITING":             copywriting.generate,
    "CREATIVE_BRIEF":          creative_brief.generate,
    "BUDGET_RULES_AUTOMATION": budget_rules.generate,
    "STRATEGY_PLAYBOOK":       strategy_playbook.generate,
    "POST_MORTEM":             post_mortem.generate,
    "LANDING_OFFER":           landing_offer.generate,
    "ANOMALY_TRIAGE":          anomaly_triage.generate,
    "MULTI_CHANNEL":           multi_channel.generate,
    "MARKET_EXPANSION":        market_expansion.generate,
}


def _build_task_schedule(total: int) -> list[str]:
    """
    Task type dağılımını belirle.
    MARKET_EXPANSION, STRATEGY_PLAYBOOK'un dağılımını paylaşır (others %15 -> her biri %3).
    """
    schedule = []
    for task_type, ratio in C.TASK_DISTRIBUTION.items():
        count = int(total * ratio)
        schedule.extend([task_type] * count)

    # MARKET_EXPANSION explicitly (not in TASK_DISTRIBUTION — others share)
    # Zaten STRATEGY_PLAYBOOK vb %3 ile tanımlı; MARKET_EXPANSION'ı da ekle
    me_count = int(total * 0.03)
    # Fazladan MARKET_EXPANSION ekle (STRATEGY_PLAYBOOK ile aynı havuzda)
    # Toplam zaten ~%97 -> kalanı MARKET_EXPANSION yap
    remaining = total - len(schedule)
    schedule.extend(["MARKET_EXPANSION"] * remaining)

    random.shuffle(schedule)
    return schedule[:total]


def _build_platform_schedule(total: int) -> list[str]:
    """Platform dağılımını belirle."""
    schedule = []
    for platform, ratio in C.PLATFORM_DISTRIBUTION.items():
        count = int(total * ratio)
        schedule.extend([platform] * count)

    # Kalanı rastgele dağıt
    remaining = total - len(schedule)
    all_platforms = list(C.PLATFORM_DISTRIBUTION.keys())
    for _ in range(remaining):
        schedule.append(random.choice(all_platforms))

    random.shuffle(schedule)
    return schedule[:total]


def generate_batch(
    start_id: int,
    batch_size: int,
    output_dir: Path,
    batch_num: int,
    seed: int | None = None,
) -> Path:
    """Tek bir batch üretip dosyaya yaz."""
    if seed is not None:
        random.seed(seed + batch_num)

    task_schedule = _build_task_schedule(batch_size)
    platform_schedule = _build_platform_schedule(batch_size)

    # Output file
    output_file = output_dir / f"dataset_batch_{batch_num:04d}.jsonl"

    written = 0
    errors = 0
    t0 = time.time()

    with open(output_file, "w", encoding="utf-8") as f:
        for i in range(batch_size):
            example_id = f"PA-{start_id + i:06d}"
            task_type = task_schedule[i]
            platform = platform_schedule[i]

            gen_fn = TASK_GENERATORS.get(task_type, campaign_diagnosis.generate)

            try:
                example = gen_fn(platform=platform, example_id=example_id)
                line = json.dumps(example, ensure_ascii=False)
                f.write(line + "\n")
                written += 1
            except Exception as e:
                errors += 1
                # Write error placeholder
                error_example = {
                    "id": example_id,
                    "platform": platform,
                    "task_type": task_type,
                    "language": "tr",
                    "system": C.TEACHER_SYSTEM_PROMPT,
                    "user": f"[GENERATION_ERROR: {str(e)[:200]}]",
                    "schema_hint": C.SCHEMA_HINT,
                    "tags": [task_type, platform, "error"],
                }
                f.write(json.dumps(error_example, ensure_ascii=False) + "\n")

            # Progress log every 5000
            if (i + 1) % 5000 == 0:
                elapsed = time.time() - t0
                rate = (i + 1) / elapsed
                print(f"  Batch {batch_num}: {i+1}/{batch_size} ({rate:.0f} examples/s) errors={errors}")

    elapsed = time.time() - t0
    print(f"  Batch {batch_num} complete: {written} written, {errors} errors, {elapsed:.1f}s -> {output_file}")
    return output_file


def merge_batches(output_dir: Path, final_name: str = "dataset.jsonl") -> Path:
    """Tüm batch dosyalarını tek bir dosyaya birleştir."""
    final_path = output_dir / final_name

    batch_files = sorted(output_dir.glob("dataset_batch_*.jsonl"))
    if not batch_files:
        print("No batch files found to merge.")
        return final_path

    total_lines = 0
    with open(final_path, "w", encoding="utf-8") as out:
        for bf in batch_files:
            with open(bf, "r", encoding="utf-8") as inp:
                for line in inp:
                    out.write(line)
                    total_lines += 1

    print(f"Merged {len(batch_files)} batches -> {final_path} ({total_lines} lines)")
    return final_path


def print_distribution_report(output_dir: Path):
    """Dağılım raporu yazdır."""
    final = output_dir / "dataset.jsonl"
    if not final.exists():
        print("No merged dataset found.")
        return

    task_counts: dict[str, int] = {}
    platform_counts: dict[str, int] = {}
    tag_counts: dict[str, int] = {}
    total = 0

    with open(final, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                task_counts[obj["task_type"]] = task_counts.get(obj["task_type"], 0) + 1
                platform_counts[obj["platform"]] = platform_counts.get(obj["platform"], 0) + 1
                for tag in obj.get("tags", []):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                total += 1
            except Exception:
                pass

    print(f"\n{'='*60}")
    print(f"DISTRIBUTION REPORT — {total} examples")
    print(f"{'='*60}")

    print("\nTask Type Distribution:")
    for k, v in sorted(task_counts.items(), key=lambda x: -x[1]):
        pct = v / total * 100
        target = C.TASK_DISTRIBUTION.get(k, 0.03) * 100
        print(f"  {k:30s} {v:>8,} ({pct:5.1f}%) target: {target:.0f}%")

    print("\nPlatform Distribution:")
    for k, v in sorted(platform_counts.items(), key=lambda x: -x[1]):
        pct = v / total * 100
        target = C.PLATFORM_DISTRIBUTION.get(k, 0.05) * 100
        print(f"  {k:15s} {v:>8,} ({pct:5.1f}%) target: {target:.0f}%")

    print("\nSpecial Scenario Tags:")
    for tag in ["low_spend_guardrail", "negative_margin", "misleading_correlation", "outage_delay", "error"]:
        count = tag_counts.get(tag, 0)
        pct = count / total * 100
        print(f"  {tag:30s} {count:>8,} ({pct:5.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Omni-Platform Ads Distillation Dataset Generator")
    parser.add_argument("--total", type=int, default=C.DEFAULT_TOTAL_EXAMPLES, help="Total examples to generate")
    parser.add_argument("--batch-size", type=int, default=C.DEFAULT_BATCH_SIZE, help="Examples per batch file")
    parser.add_argument("--start-id", type=int, default=1, help="Starting ID number")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--no-merge", action="store_true", help="Don't merge batches at end")
    parser.add_argument("--report-only", action="store_true", help="Only print distribution report")
    args = parser.parse_args()

    # Output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(__file__).resolve().parent.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.report_only:
        print_distribution_report(output_dir)
        return

    print(f"Generating {args.total:,} examples in batches of {args.batch_size:,}")
    print(f"Output: {output_dir}")
    print(f"Seed: {args.seed}")
    print()

    total_batches = (args.total + args.batch_size - 1) // args.batch_size
    t_start = time.time()

    for batch_num in range(total_batches):
        batch_start_id = args.start_id + batch_num * args.batch_size
        current_batch_size = min(args.batch_size, args.total - batch_num * args.batch_size)

        print(f"Batch {batch_num + 1}/{total_batches} — IDs PA-{batch_start_id:06d} to PA-{batch_start_id + current_batch_size - 1:06d}")
        generate_batch(
            start_id=batch_start_id,
            batch_size=current_batch_size,
            output_dir=output_dir,
            batch_num=batch_num + 1,
            seed=args.seed,
        )

    t_total = time.time() - t_start
    print(f"\nAll {total_batches} batches generated in {t_total:.1f}s ({args.total / t_total:.0f} examples/s)")

    if not args.no_merge:
        merge_batches(output_dir)
        print_distribution_report(output_dir)

    print("\nDEVAM yazarsan sonraki batch'e geçerim.")


if __name__ == "__main__":
    main()
