"""FrameForge command line interface."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import manifests, inspect


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only project framework discovery and advisory")
    parser.add_argument("project", nargs="?", default=".", help="Project root")
    parser.add_argument("--plugins", action="store_true", help="List available plugin metadata")
    parser.add_argument("--plugin-dir", help="Read additional declarative plugin manifests from this directory")
    args = parser.parse_args(argv)
    try:
        if args.plugins:
            print(json.dumps({"plugins": list(manifests(args.plugin_dir).values())}, ensure_ascii=False, indent=2))
            return 0
        result = inspect(Path(args.project), plugin_dir=args.plugin_dir)
    except (ValueError, OSError) as exc:
        print(f"FrameForge: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
