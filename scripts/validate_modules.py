#!/usr/bin/env python3
"""CI check: every modules/*/module.json must be valid JSON and declare the
required fields, so a broken manifest fails fast instead of silently
breaking module discovery at runtime."""
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ["id", "name", "version", "description", "api_version", "author"]

MODULES_ROOT = Path(__file__).resolve().parents[1] / "modules"


def main() -> int:
    if not MODULES_ROOT.exists():
        print(f"No modules directory at {MODULES_ROOT}")
        return 0

    errors = []
    for module_dir in sorted(MODULES_ROOT.iterdir()):
        manifest_path = module_dir / "module.json"
        if not module_dir.is_dir() or not manifest_path.exists():
            continue
        try:
            manifest = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"{manifest_path}: invalid JSON ({exc})")
            continue

        for field in REQUIRED_FIELDS:
            if field not in manifest:
                errors.append(f"{manifest_path}: missing required field '{field}'")

        if manifest.get("id") != module_dir.name:
            errors.append(f"{manifest_path}: id '{manifest.get('id')}' does not match folder name '{module_dir.name}'")

        if "id" in manifest and not str(manifest["id"]).replace("_", "").replace("-", "").isalnum():
            errors.append(f"{manifest_path}: id must be alphanumeric (with - or _)")

    if errors:
        print("Module manifest validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"All module manifests valid ({len(list(MODULES_ROOT.iterdir()))} checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
