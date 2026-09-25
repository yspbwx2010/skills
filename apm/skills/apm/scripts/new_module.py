#!/usr/bin/env python3
"""Scaffold an APatch module (APM) in an empty directory.

    new_module.py <dir> --id my_module --name "My Module" [--author you] [--description "..."]
                        [--zip]

Writes module.prop, customize.sh and the boot-script skeletons, and an empty system/ tree.
With --zip, also packs a flashable <id>.zip. Standard library only.
"""
import argparse
import pathlib
import re
import sys
import zipfile

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "template"
ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9._-]+$")  # apd's rule, enforced at install


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold an APatch module (APM).")
    ap.add_argument("dir", help="target directory (must be empty or not exist)")
    ap.add_argument("--id", required=True, help="module id (^[a-zA-Z][a-zA-Z0-9._-]+$)")
    ap.add_argument("--name", required=True)
    ap.add_argument("--author", default="you")
    ap.add_argument("--description", default="An APatch module")
    ap.add_argument("--zip", action="store_true", help="also build a flashable <id>.zip")
    args = ap.parse_args()

    if not ID_RE.match(args.id):
        print(f"error: invalid --id {args.id!r}: must match ^[a-zA-Z][a-zA-Z0-9._-]+$",
              file=sys.stderr)
        return 2

    dst = pathlib.Path(args.dir)
    if dst.exists() and any(dst.iterdir()):
        print(f"error: {dst} is not empty", file=sys.stderr)
        return 2
    dst.mkdir(parents=True, exist_ok=True)

    subs = {"__ID__": args.id, "__NAME__": args.name,
            "__AUTHOR__": args.author, "__DESCRIPTION__": args.description}
    for src in sorted(TEMPLATE.iterdir()):
        if src.is_dir():
            continue  # system/ handled below
        text = src.read_text(encoding="utf-8")
        for k, v in subs.items():
            text = text.replace(k, v)
        (dst / src.name).write_text(text, encoding="utf-8")
    (dst / "system").mkdir(exist_ok=True)  # empty overlay tree, ready for files

    if args.zip:
        zpath = dst.parent / f"{args.id}.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(dst.rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(dst).as_posix())
        print(f"Built {zpath}")

    print(f"Created APM skeleton in {dst}\n"
          f"  id={args.id}\n"
          f"Add files under system/ to overlay /system; edit service.sh for boot work.\n"
          f"Pack for flashing:  cd {dst} && zip -r ../{args.id}.zip . -x '.*'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
