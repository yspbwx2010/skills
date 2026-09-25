#!/usr/bin/env python3
"""Scaffold the APM template and assert apd would accept it.

apd rejects a module whose module.prop has no valid `id` (regex ^[a-zA-Z][a-zA-Z0-9._-]+$) or is
missing required keys. This gate builds the template with new_module.py and checks the produced
module.prop and zip against those rules — the same checks apd's installer runs. Standard library
only; exits 1 on any problem.
"""
import pathlib
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "apm"
ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9._-]+$")
REQUIRED = ("id", "name", "version", "versionCode", "author", "description")


def parse_prop(text: str) -> dict:
    d = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        d[k.strip()] = v.strip()
    return d


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td) / "m"
        rc = subprocess.run([sys.executable, str(SKILL / "scripts" / "new_module.py"), str(d),
                             "--id", "ci_mod", "--name", "CI Mod", "--zip"],
                            capture_output=True, text=True)
        if rc.returncode:
            print("FAIL: new_module.py:\n" + rc.stderr, file=sys.stderr)
            return 1

        prop_file = d / "module.prop"
        if not prop_file.is_file():
            print("FAIL: module.prop not generated", file=sys.stderr)
            return 1
        if prop_file.read_text().endswith("\r\n") or "\r\n" in prop_file.read_text():
            print("FAIL: module.prop must use LF newlines", file=sys.stderr)
            return 1
        prop = parse_prop(prop_file.read_text())
        for k in REQUIRED:
            if k not in prop:
                print(f"FAIL: module.prop missing {k}", file=sys.stderr)
                return 1
        if not ID_RE.match(prop["id"]):
            print(f"FAIL: id {prop['id']!r} fails apd's regex", file=sys.stderr)
            return 1
        if not prop["versionCode"].isdigit():
            print("FAIL: versionCode must be an integer", file=sys.stderr)
            return 1

        # the reject-bad-id path
        bad = subprocess.run([sys.executable, str(SKILL / "scripts" / "new_module.py"),
                              str(pathlib.Path(td) / "bad"), "--id", "1bad", "--name", "x"],
                             capture_output=True, text=True)
        if bad.returncode == 0:
            print("FAIL: scaffold accepted an invalid id", file=sys.stderr)
            return 1

        zpath = d.parent / "ci_mod.zip"
        if not zpath.is_file():
            print("FAIL: --zip did not produce a zip", file=sys.stderr)
            return 1
        names = zipfile.ZipFile(zpath).namelist()
        if "module.prop" not in names:
            print("FAIL: zip has no module.prop at its root", file=sys.stderr)
            return 1

    print(f"apm template ok: module.prop valid (id={prop['id']}), zip has module.prop at root")
    return 0


if __name__ == "__main__":
    sys.exit(main())
