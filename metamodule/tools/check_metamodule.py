#!/usr/bin/env python3
"""Scaffold the metamodule template and assert it is a valid metamodule.

A metamodule is a module whose module.prop has metamodule=1 (or true) and a valid id, plus the
hook scripts. This gate builds the template with new_metamodule.py and checks the produced
module.prop and zip against those rules. Standard library only; exits 1 on any problem.
"""
import pathlib
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "metamodule"
ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9._-]+$")
REQUIRED = ("id", "name", "version", "versionCode", "author", "description")


def parse_prop(text: str) -> dict:
    d = {}
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td) / "m"
        rc = subprocess.run([sys.executable, str(SKILL / "scripts" / "new_metamodule.py"), str(d),
                             "--id", "meta-ci", "--name", "Meta CI", "--zip"],
                            capture_output=True, text=True)
        if rc.returncode:
            print("FAIL: new_metamodule.py:\n" + rc.stderr, file=sys.stderr)
            return 1

        prop = parse_prop((d / "module.prop").read_text())
        for k in REQUIRED:
            if k not in prop:
                print(f"FAIL: module.prop missing {k}", file=sys.stderr)
                return 1
        if not ID_RE.match(prop["id"]):
            print(f"FAIL: id {prop['id']!r} fails the install-time regex", file=sys.stderr)
            return 1
        if prop.get("metamodule", "").lower() not in ("1", "true"):
            print("FAIL: module.prop must set metamodule=1 (or true) — otherwise it is a regular module",
                  file=sys.stderr)
            return 1
        for hook in ("metamount.sh", "metainstall.sh", "metauninstall.sh"):
            if not (d / hook).is_file():
                print(f"FAIL: missing hook {hook}", file=sys.stderr)
                return 1
        # metamount must set the mount source to KSU
        if "KSU" not in (d / "metamount.sh").read_text():
            print("FAIL: metamount.sh does not tag mounts with source \"KSU\"", file=sys.stderr)
            return 1
        # metauninstall must read the MODULE_ID env var, not assign it from $1
        if re.search(r'MODULE_ID\s*=\s*"?\$1"?', (d / "metauninstall.sh").read_text()):
            print("FAIL: metauninstall.sh sets MODULE_ID from $1; the id arrives as the $MODULE_ID env var",
                  file=sys.stderr)
            return 1

        names = zipfile.ZipFile(d.parent / "meta-ci.zip").namelist()
        if "module.prop" not in names:
            print("FAIL: zip has no module.prop at its root", file=sys.stderr)
            return 1

    print("metamodule template ok: metamodule=1, valid id, three hooks, source=KSU, MODULE_ID env")
    return 0


if __name__ == "__main__":
    sys.exit(main())
