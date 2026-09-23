#!/usr/bin/env python3
"""Back-compat wrapper. Runtime is engine/pipeline.py + packs/HYPE."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import main

if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv:
        argv = ["run", "HYPE"]
    elif argv[0] in {"run", "capture", "extract", "build"} and (len(argv) == 1):
        argv = ["run", "HYPE"]
    raise SystemExit(main(argv if argv[0] == "run" else ["run", "HYPE"]))
