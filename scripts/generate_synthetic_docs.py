"""Generate the synthetic document sets and ground truth (Plan Section 14, tasks DATA-01..04).

Usage (from backend/):
    uv sync --group data
    uv run --group data playwright install chromium     # first time only
    uv run --group data python ../scripts/generate_synthetic_docs.py --demo-date 2026-10-18

Outputs:
    data/synthetic/{lotus_apparel,kandy_knits,stress}/...   documents
    data/ground_truth/<same path>.json                      expected values per document
    data/synthetic/manifest.json                            index, planted issues, demo upload order

Re-running regenerates everything. PDF bytes (and so SHA-256) change on each run because
Chromium embeds a creation timestamp: generate once, commit, and only regenerate on purpose.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))

from synthetic.build import Builder  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--demo-date",
        type=date.fromisoformat,
        default=date(2026, 10, 18),
        help="Demo day. The boiler certificate expires 23 days after it (Plan 20.1).",
    )
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--data-root", type=Path, default=Path(__file__).resolve().parents[1] / "data"
    )
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        records = Builder(browser, args.data_root, args.demo_date, args.seed).run()
        browser.close()

    by_set = Counter(r.rel_path.split("/")[0] for r in records)
    by_quality = Counter(r.quality for r in records)
    sys.stdout.write(f"Generated {len(records)} documents: {dict(by_set)}\n")
    sys.stdout.write(f"By quality: {dict(by_quality)}\n")
    sys.stdout.write("Planted demo issues:\n")
    for r in records:
        for issue in r.planted_issues:
            if r.factory == "la":
                sys.stdout.write(f"  - {r.rel_path}: {issue}\n")


if __name__ == "__main__":
    main()
