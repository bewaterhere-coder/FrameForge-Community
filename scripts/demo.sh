#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
printf '\n=== 1. Discover available guidance ===\n'
python3 -m frameforge.cli --plugins | python3 -c '
import json, sys
items = json.load(sys.stdin)["plugins"]
for item in items:
    stage = "Candidate" if item.get("evidence_level") == "candidate" else "Available"
    print("- {} {} [{}]".format(item["id"], item["version"], stage))
print("Total: {} plugin manifests".format(len(items)))
'
printf '\n=== 2. Inspect the sample game ===\n'
python3 - "$ROOT/examples/sample-game-godot" <<'PY'
import sys
from frameforge.core import inspect
result = inspect(sys.argv[1])
print("Project: FrameForge Sample Game (Godot 4)")
print("Suggested plugins:")
for item in result["suggested_plugins"]:
    print("- {} {} ({})".format(item["plugin_id"], item["version"], item["status"]))
print("Explicitly selected plugins:")
for item in result["selected_plugins"]:
    print("- {} {}".format(item["id"], item["version"]))
print("Project-owned standards:")
for domain, path in sorted(result["standards"].items()):
    print("- {}: {}".format(domain, path))
print("Advisory items: {}".format(len(result["advisories"])))
for item in result["advisories"]:
    print("- {}: {} ({})".format(item["topic"], item["status"], item["confidence"]))
print("Warnings: {}".format(len(result["warnings"])))
print("Blocking: {}".format(str(result["blocking"]).lower()))
print("Scope: read-only static advisory; Godot editor/build/runtime are not executed.")
PY
