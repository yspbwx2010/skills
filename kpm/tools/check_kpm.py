#!/usr/bin/env python3
"""Build the KPM template and assert the result is a loadable module shape.

A KPM must be an arm64 ELF *relocatable* object carrying the .kpm.info/.kpm.init/.kpm.exit
sections the loader requires. This gate scaffolds the template with new_kpm.py, compiles it
against a KernelPatch checkout, links it partially, and checks the ELF — the same shape checks
KernelPatch's own loader runs. Uses clang/ld.lld/llvm-readelf (no aarch64-none-elf GCC needed).

    check_kpm.py --kp-src /path/to/KernelPatch

Exits 1 on any problem. Skips (exit 0 with a notice) if clang or the KernelPatch source is absent,
so it never blocks a machine that can't build; CI provides both.
"""
import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "kpm"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kp-src", default="", help="KernelPatch source checkout")
    args = ap.parse_args()

    for tool in ("clang", "ld.lld", "llvm-readelf"):
        if not shutil.which(tool):
            print(f"skip: {tool} not found (CI provides it)")
            return 0
    kp = pathlib.Path(args.kp_src) if args.kp_src else None
    if not kp or not (kp / "kernel" / "include" / "kpmodule.h").is_file():
        print("skip: KernelPatch source not found (pass --kp-src)")
        return 0

    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td) / "m"
        rc = run([sys.executable, str(SKILL / "scripts" / "new_kpm.py"), str(d),
                  "--name", "ci-mod", "--kp-dir", str(kp)])
        if rc.returncode:
            print("FAIL: new_kpm.py:\n" + rc.stderr, file=sys.stderr)
            return 1
        k = kp / "kernel"
        incs = [".", "include", "patch/include", "linux/include",
                "linux/arch/arm64/include", "linux/tools/arch/arm64/include"]
        cc = ["clang", "--target=aarch64-none-elf", "-ffreestanding", "-fno-common", "-O2"]
        for i in incs:
            cc += ["-I", str(k / i)]
        cc += ["-c", str(d / "module.c"), "-o", str(d / "module.o")]
        r = run(cc)
        if r.returncode:
            print("FAIL: compile:\n" + r.stderr, file=sys.stderr)
            return 1
        kpm = d / "ci-mod.kpm"
        r = run(["ld.lld", "-r", "-o", str(kpm), str(d / "module.o")])
        if r.returncode:
            print("FAIL: link:\n" + r.stderr, file=sys.stderr)
            return 1

        hdr = run(["llvm-readelf", "-h", str(kpm)]).stdout
        if "REL (Relocatable file)" not in hdr or "AArch64" not in hdr:
            print("FAIL: .kpm is not an arm64 relocatable ELF", file=sys.stderr)
            return 1
        secs = run(["llvm-readelf", "-S", str(kpm)]).stdout
        for need in (".kpm.info", ".kpm.init", ".kpm.exit"):
            if need not in secs:
                print(f"FAIL: .kpm missing required section {need}", file=sys.stderr)
                return 1

    print("kpm template ok: arm64 ET_REL with .kpm.info/.kpm.init/.kpm.exit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
