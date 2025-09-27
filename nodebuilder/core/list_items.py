# ---------- file: nodebuilder/core/list_items.py ----------
from pathlib import Path
import json

def list_items() -> None:
    cwd = Path.cwd()
    nodes_dir = cwd / "nodes"
    workflows_dir = cwd / "workflows"

    print("\nAvailable Nodes:")
    if nodes_dir.exists() and nodes_dir.is_dir():
        for p in sorted(nodes_dir.iterdir()):
            manifest = p / "manifest.json"
            if manifest.exists():
                try:
                    j = json.loads(manifest.read_text())
                    desc = j.get("description", "")
                except Exception:
                    desc = "(could not parse manifest.json)"
                print(f" - {p.name}: {desc}")
            else:
                print(f" - {p.name}: (no manifest.json)")
    else:
        print(" (no nodes found)")

    print("\nAvailable Workflows:")
    if workflows_dir.exists() and workflows_dir.is_dir():
        for p in sorted(workflows_dir.iterdir()):
            manifest = p / "manifest.json"
            if manifest.exists():
                try:
                    j = json.loads(manifest.read_text())
                    desc = j.get("description", "")
                except Exception:
                    desc = "(could not parse manifest.json)"
                print(f" - {p.name}: {desc}")
            else:
                print(f" - {p.name}: (no manifest.json)")
    else:
        print(" (no workflows found)")