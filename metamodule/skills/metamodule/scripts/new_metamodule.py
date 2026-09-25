#!/usr/bin/env python3
"""Scaffold a metamodule (KernelSU / APatch mount-backend module) in an empty directory.

    new_metamodule.py <dir> --id meta-example --name "My Metamodule"
                            [--author you] [--description "..."] [--zip]

Writes module.prop (with metamodule=1) and the three hook stubs (metamount.sh, metainstall.sh,
metauninstall.sh). With --zip, also packs a flashable <id>.zip. Standard library only.
"""
import argparse
import pathlib
import re
import sys
import zipfile

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "template"
ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9._-]+$")  # same rule ksud/apd enforce at install


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a metamodule.")
    ap.add_argument("dir", help="target directory (must be empty or not exist)")
    ap.add_argument("--id", required=True, help="metamodule id; convention: start with meta-")
    ap.add_argument("--name", required=True)
    ap.add_argument("--author", default="you")
    ap.add_argument("--description", default="A metamodule mount backend")
    ap.add_argument("--zip", action="store_true", help="also build a flashable <id>.zip")
    args = ap.parse_args()

    if not ID_RE.match(args.id):
        print(f"error: invalid --id {args.id!r}: must match ^[a-zA-Z][a-zA-Z0-9._-]+$", file=sys.stderr)
        return 2
    if not args.id.startswith("meta-"):
        print(f"warning: metamodule id {args.id!r} does not start with 'meta-' (recommended convention)",
              file=sys.stderr)

    dst = pathlib.Path(args.dir)
    if dst.exists() and any(dst.iterdir()):
        print(f"error: {dst} is not empty", file=sys.stderr)
        return 2
    dst.mkdir(parents=True, exist_ok=True)

    subs = {"__ID__": args.id, "__NAME__": args.name,
            "__AUTHOR__": args.author, "__DESCRIPTION__": args.description}
    for src in sorted(TEMPLATE.iterdir()):
        text = src.read_text(encoding="utf-8")
        for k, v in subs.items():
            text = text.replace(k, v)
        (dst / src.name).write_text(text, encoding="utf-8")

    if args.zip:
        zpath = dst.parent / f"{args.id}.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(dst.rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(dst).as_posix())
        print(f"Built {zpath}")

    print(f"Created metamodule skeleton in {dst}\n"
          f"  id={args.id} (metamodule=1)\n"
          f"Edit metamount.sh (your mount backend), then flash in the KernelSU/APatch manager and reboot.\n"
          f"Every mount must use source \"KSU\".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
