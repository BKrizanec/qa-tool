"""Usage: qa-tool-audit <repo> [--json] [--out FILE]"""
from __future__ import annotations

import argparse
from pathlib import Path

from . import audit
from .report import to_json, to_markdown


def main() -> None:
    ap = argparse.ArgumentParser(prog="qa-tool-audit", description="Audit what a Cucumber-JVM suite really verifies.")
    ap.add_argument("repo", type=Path)
    ap.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    analyzer = audit(args.repo.resolve())
    result = to_json(analyzer) if args.json else to_markdown(analyzer, args.repo.resolve().name)
    if args.out:
        args.out.write_text(result + "\n", encoding="utf-8")
    else:
        print(result)


if __name__ == "__main__":
    main()
