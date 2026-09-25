#!/usr/bin/env python3
"""Compile every template under skills/gki/assets/ against a real kernel build.

Each assets/<name>/ is copied to a temporary directory and built with the out-of-tree Kbuild
command the skill documents. The build must exit 0, produce a .ko and print no warning (the
kernel's CONFIG_WERROR=y already turns compiler warnings into errors; this also catches modpost
warnings and "the compiler differs from the one used to build the kernel"). The vermagic of each
.ko is printed so it can be compared with the kernel's.

It needs the output of a full kernel build (.config and a complete Module.symvers), so it runs
locally, not in CI. It never writes into the asset directories.

    check_gki.py --ksrc KERNEL_SRC --kout KERNEL_OUT [--clang-bin DIR]

Exits 1 on any failure.
"""
import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "skills" / "gki" / "assets"


def vermagic(ko: pathlib.Path, env: dict) -> str:
    if shutil.which("modinfo", path=env["PATH"]):
        r = subprocess.run(["modinfo", "-F", "vermagic", str(ko)],
                           capture_output=True, text=True, env=env)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    m = re.search(rb"vermagic=([^\0]*)\0", ko.read_bytes())  # the .modinfo string, read directly
    return m.group(1).decode() if m else "?"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ksrc", required=True, help="kernel source tree")
    ap.add_argument("--kout", required=True, help="full kernel build output (O=)")
    ap.add_argument("--clang-bin", default="", help="the branch's clang bin/ (else clang from PATH)")
    args = ap.parse_args()

    ksrc = pathlib.Path(args.ksrc).resolve()
    kout = pathlib.Path(args.kout).resolve()
    for need in (ksrc / "Makefile", kout / ".config", kout / "Module.symvers"):
        if not need.is_file():
            print(f"FAIL: {need} not found (need the source tree and a full build's output)",
                  file=sys.stderr)
            return 1
    env = dict(os.environ)
    if args.clang_bin:
        env["PATH"] = str(pathlib.Path(args.clang_bin).resolve()) + os.pathsep + env["PATH"]

    assets = sorted(p for p in ASSETS.iterdir() if p.is_dir())
    if not assets:
        print(f"FAIL: no templates under {ASSETS}", file=sys.stderr)
        return 1
    failed = 0
    for asset in assets:
        with tempfile.TemporaryDirectory() as td:
            mdir = pathlib.Path(td) / asset.name
            shutil.copytree(asset, mdir)
            cmd = ["make", "-C", str(ksrc), f"O={kout}", "ARCH=arm64", "LLVM=1", "LLVM_IAS=1",
                   "KCFLAGS=-D__ANDROID_COMMON_KERNEL__", f"M={mdir}", "-j4", "modules"]
            r = subprocess.run(cmd, capture_output=True, text=True, env=env)
            log = r.stdout + r.stderr
            warnings = [l for l in log.splitlines() if re.search(r"warning:", l, re.I)]
            kos = sorted(mdir.glob("*.ko"))
            if r.returncode or warnings or not kos:
                failed += 1
                why = (f"exit {r.returncode}" if r.returncode
                       else f"{len(warnings)} warning(s)" if warnings else "no .ko produced")
                print(f"FAIL {asset.name}: {why}\n{log}", file=sys.stderr)
                continue
            for ko in kos:
                print(f"ok   {asset.name}: {ko.name}  vermagic={vermagic(ko, env)}")
    if failed:
        print(f"\n{failed} template(s) failed", file=sys.stderr)
        return 1
    print(f"all {len(assets)} templates build warning-free")
    return 0


if __name__ == "__main__":
    sys.exit(main())
