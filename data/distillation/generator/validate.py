"""
validate.py — JSONL Doğrulama Scripti
=======================================
Tüm JSONL dosyalarını parse eder, required field'ları kontrol eder,
dağılım raporu üretir.

Kullanım:
    python -m generator.validate --dir ./
"""

import json
import sys
import argparse
from pathlib import Path
from collections import Counter


REQUIRED_FIELDS = {"id", "platform", "task_type", "language", "system", "user", "schema_hint", "tags"}
VALID_PLATFORMS = {"meta", "google_ads", "tiktok", "x", "linkedin", "pinterest", "snap", "reddit", "amazon_ads", "mixed"}
VALID_TASK_TYPES = {
    "CAMPAIGN_DIAGNOSIS", "COPYWRITING", "CREATIVE_BRIEF", "BUDGET_RULES_AUTOMATION",
    "STRATEGY_PLAYBOOK", "POST_MORTEM", "LANDING_OFFER", "ANOMALY_TRIAGE",
    "MULTI_CHANNEL", "MARKET_EXPANSION",
}


def validate_jsonl(filepath: Path, max_errors: int = 50) -> dict:
    """Tek bir JSONL dosyasını doğrula."""
    stats = {
        "file": str(filepath),
        "total_lines": 0,
        "valid_lines": 0,
        "errors": [],
        "task_counts": Counter(),
        "platform_counts": Counter(),
        "tag_counts": Counter(),
    }

    if not filepath.exists():
        stats["errors"].append(f"File not found: {filepath}")
        return stats

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            stats["total_lines"] += 1
            line = line.strip()

            if not line:
                continue

            # Parse JSON
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                stats["errors"].append(f"Line {i}: JSON parse error — {e}")
                if len(stats["errors"]) >= max_errors:
                    stats["errors"].append(f"... max errors ({max_errors}) reached, stopping.")
                    break
                continue

            # Check required fields
            missing = REQUIRED_FIELDS - set(obj.keys())
            if missing:
                # Allow eval_metadata and other extra fields
                actual_missing = missing - {"eval_metadata"}
                if actual_missing:
                    stats["errors"].append(f"Line {i} ({obj.get('id', '?')}): missing fields: {actual_missing}")
                    if len(stats["errors"]) >= max_errors:
                        break
                    continue

            # Validate platform
            platform = obj.get("platform", "")
            if platform not in VALID_PLATFORMS:
                stats["errors"].append(f"Line {i} ({obj.get('id', '?')}): invalid platform: {platform}")

            # Validate task_type
            task_type = obj.get("task_type", "")
            if task_type not in VALID_TASK_TYPES:
                # Allow DPO instruction lines
                if "description" not in obj:
                    stats["errors"].append(f"Line {i} ({obj.get('id', '?')}): invalid task_type: {task_type}")

            # Count distributions
            if task_type in VALID_TASK_TYPES:
                stats["task_counts"][task_type] += 1
            if platform in VALID_PLATFORMS:
                stats["platform_counts"][platform] += 1
            for tag in obj.get("tags", []):
                stats["tag_counts"][tag] += 1

            # Check user prompt is non-empty
            user = obj.get("user", "")
            if len(user) < 50:
                stats["errors"].append(f"Line {i} ({obj.get('id', '?')}): user prompt too short ({len(user)} chars)")

            stats["valid_lines"] += 1

    return stats


def print_report(stats: dict):
    """Doğrulama raporunu yazdır."""
    print(f"\n{'='*60}")
    print(f"FILE: {stats['file']}")
    print(f"{'='*60}")
    print(f"Total lines:  {stats['total_lines']:>10,}")
    print(f"Valid lines:  {stats['valid_lines']:>10,}")
    print(f"Errors:       {len(stats['errors']):>10,}")

    if stats["errors"]:
        print(f"\nFirst {min(10, len(stats['errors']))} errors:")
        for e in stats["errors"][:10]:
            print(f"  [X] {e}")

    if stats["task_counts"]:
        total = sum(stats["task_counts"].values())
        print(f"\nTask Distribution ({total} examples):")
        for k, v in stats["task_counts"].most_common():
            print(f"  {k:30s} {v:>8,} ({v/total*100:5.1f}%)")

    if stats["platform_counts"]:
        total = sum(stats["platform_counts"].values())
        print(f"\nPlatform Distribution ({total} examples):")
        for k, v in stats["platform_counts"].most_common():
            print(f"  {k:15s} {v:>8,} ({v/total*100:5.1f}%)")

    special_tags = ["low_spend_guardrail", "negative_margin", "misleading_correlation", "outage_delay", "error"]
    has_special = any(stats["tag_counts"].get(t, 0) > 0 for t in special_tags)
    if has_special:
        total = sum(stats["task_counts"].values()) or 1
        print(f"\nSpecial Tags:")
        for tag in special_tags:
            count = stats["tag_counts"].get(tag, 0)
            print(f"  {tag:30s} {count:>8,} ({count/total*100:5.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Validate JSONL files")
    parser.add_argument("--dir", type=str, default=".", help="Directory containing JSONL files")
    parser.add_argument("--file", type=str, default=None, help="Specific file to validate")
    parser.add_argument("--max-errors", type=int, default=50)
    args = parser.parse_args()

    target_dir = Path(args.dir)
    all_passed = True

    if args.file:
        files = [Path(args.file)]
    else:
        files = sorted(target_dir.glob("*.jsonl"))

    if not files:
        print(f"No JSONL files found in {target_dir}")
        sys.exit(1)

    for filepath in files:
        stats = validate_jsonl(filepath, args.max_errors)
        print_report(stats)
        if stats["errors"]:
            all_passed = False

    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL FILES VALID")
    else:
        print("❌ SOME FILES HAVE ERRORS — see above")
    print(f"{'='*60}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
