#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.preflight import format_preflight, has_required_failures, run_preflight


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local demo/build readiness.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when required checks fail.")
    args = parser.parse_args()

    checks = run_preflight(ROOT)
    print(format_preflight(checks))
    return 1 if args.strict and has_required_failures(checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
