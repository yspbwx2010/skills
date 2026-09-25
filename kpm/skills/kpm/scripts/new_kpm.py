#!/usr/bin/env python3
"""Generate a buildable KernelPatch Module skeleton in an empty directory.

    new_kpm.py <dir> --name my-module [--author you] [--description "..."] [--kp-dir /path]

Copies the template (module.c + Makefile), substitutes the metadata, and — if --kp-dir is
given — records it so `make` just works. Standard library only.
"""
import argparse
import pathlib
import re
import sys

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "template"
NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,31}$")  # KPM_NAME is <= 32 bytes


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a KernelPatch Module (KPM).")
    ap.add_argument("dir", help="target directory (must be empty or not exist)")
    ap.add_argument("--name", required=True, help="module name (KPM_NAME, <= 32 bytes, unique)")
    ap.add_argument("--author", default="you")
    ap.add_argument("--description", default="A KernelPatch Module")
    ap.add_argument("--kp-dir", default="", help="path to a KernelPatch source checkout")
    args = ap.parse_args()

    if not NAME_RE.match(args.name):
        print(f"error: invalid --name {args.name!r}: use [A-Za-z0-9._-], <= 32 chars",
              file=sys.stderr)
        return 2
    if len(args.description.encode()) > 512:
        print("error: --description exceeds 512 bytes", file=sys.stderr)
        return 2

    dst = pathlib.Path(args.dir)
    if dst.exists() and any(dst.iterdir()):
        print(f"error: {dst} is not empty", file=sys.stderr)
        return 2
    dst.mkdir(parents=True, exist_ok=True)

    subs = {"__NAME__": args.name, "__AUTHOR__": args.author, "__DESCRIPTION__": args.description}
    for src in sorted(TEMPLATE.iterdir()):
        text = src.read_text(encoding="utf-8")
        for k, v in subs.items():
            text = text.replace(k, v)
        (dst / src.name).write_text(text, encoding="utf-8")

    kp = args.kp_dir.strip()
    hint = ""
    if kp:
        (dst / "kp_dir.mk").write_text(f"KP_DIR ?= {kp}\n", encoding="utf-8")
        # make the Makefile pick it up without an env var
        mk = (dst / "Makefile").read_text(encoding="utf-8")
        mk = mk.replace("CC = $(TARGET_COMPILE)gcc",
                        "-include kp_dir.mk\n\nCC = $(TARGET_COMPILE)gcc")
        (dst / "Makefile").write_text(mk, encoding="utf-8")
        hint = f"  KP_DIR is set to {kp}\n"

    lines = [f"Created KPM skeleton in {dst}"]
    if hint:
        lines.append(hint.rstrip("\n"))
    lines.append("Build:")
    lines.append("  export TARGET_COMPILE=aarch64-none-elf-")
    if not kp:
        lines.append("  export KP_DIR=/path/to/KernelPatch")
    lines.append(f"  cd {dst} && make")
    lines.append(f"Output: {args.name}.kpm")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
