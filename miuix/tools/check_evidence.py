#!/usr/bin/env python3
"""Keep the hand layer's `evidence: path:line` references pointing at real source.

Every trap in data/gotchas/*.yaml cites the line that proves it. Those citations are plain
text, so an upstream commit that inserts two lines above them silently turns every one into a
pointer at the wrong code -- the skill would still look authoritative while citing nonsense.

Two jobs:

    check_evidence.py --src .miuix-src
        Gate. Every evidence path must exist in the checkout and every line (or a-b range)
        must be inside the file. Exit 1 otherwise.

    check_evidence.py --src .miuix-src --rebase OLD_REV [--write]
        After pulling upstream. For every citation into a file that changed between OLD_REV
        and the checkout's HEAD, map the old line through the diff:
          moved    the cited line is untouched, only shifted -> new number is certain
          touched  the cited line itself was edited or deleted -> the claim needs re-reading
        --write rewrites the "moved" numbers in place; "touched" ones are only listed, because
        whether the trap still holds is a question about meaning, not about line numbers.
"""
from __future__ import annotations

import argparse
import difflib
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
EVIDENCE = re.compile(r'(evidence:\s*"?)([\w./-]+\.(?:kt|kts|md|toml)):(\d+)(?:-(\d+))?')


def refs(gotchas: pathlib.Path):
    """Yield (yaml file, match) for every evidence citation, in file order."""
    for f in sorted(gotchas.glob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        for m in EVIDENCE.finditer(text):
            yield f, m


def git(src: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(src), *args], check=True,
                          capture_output=True, text=True).stdout


def line_map(old: list[str], new: list[str]) -> dict[int, int]:
    """1-based old line -> 1-based new line, only for lines the diff left untouched."""
    out: dict[int, int] = {}
    sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    for tag, i1, i2, j1, _ in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                out[i1 + k + 1] = j1 + k + 1
    return out


def check(src: pathlib.Path, gotchas: pathlib.Path) -> int:
    problems, n = [], 0
    cache: dict[str, int | None] = {}
    for f, m in refs(gotchas):
        n += 1
        path, a, b = m.group(2), int(m.group(3)), int(m.group(4) or m.group(3))
        if path not in cache:
            p = src / path
            cache[path] = len(p.read_text(encoding="utf-8").splitlines()) if p.is_file() else None
        size = cache[path]
        where = f"{f.name}: {path}:{m.group(3)}{'-' + m.group(4) if m.group(4) else ''}"
        if size is None:
            problems.append(f"{where}  file does not exist")
        elif not (1 <= a <= b <= size):
            problems.append(f"{where}  line out of range (the file has only {size} lines)")
    for p in problems:
        print("  " + p, file=sys.stderr)
    if problems:
        print(f"\n{len(problems)} / {n} evidence citations are invalid", file=sys.stderr)
        return 1
    print(f"evidence gate passed: all {n} path:line citations land in real files and line ranges of the {src.name} checkout")
    return 0


def rebase(src: pathlib.Path, gotchas: pathlib.Path, old_rev: str, write: bool) -> int:
    changed = set(git(src, "diff", "--name-only", old_rev, "HEAD").split())
    maps: dict[str, dict[int, int] | None] = {}
    moved, touched, same = [], [], 0
    edits: dict[pathlib.Path, list[tuple[int, int, str]]] = {}
    for f, m in refs(gotchas):
        path = m.group(2)
        if path not in changed:
            same += 1
            continue
        if path not in maps:
            try:
                old = git(src, "show", f"{old_rev}:{path}").splitlines()
            except subprocess.CalledProcessError:
                old = []
            p = src / path
            maps[path] = line_map(old, p.read_text(encoding="utf-8").splitlines()) if p.is_file() else None
        mp = maps[path]
        a, b = int(m.group(3)), int(m.group(4) or m.group(3))
        label = f"{f.name}: {path.rsplit('/', 1)[-1]}:{m.group(3)}{'-' + m.group(4) if m.group(4) else ''}"
        # a range survives only if every line in it survived, and still in one piece
        got = [mp.get(i) for i in range(a, b + 1)] if mp is not None else [None]
        new = [x for x in got if x is not None]
        if len(new) != len(got) or any(y - x != 1 for x, y in zip(new, new[1:])):
            touched.append(label)
            continue
        na, nb = new[0], new[-1]
        repl = f"{path}:{na}" + (f"-{nb}" if m.group(4) else "")
        if (na, nb) != (a, b):
            moved.append(f"{label} → {na}{'-' + str(nb) if m.group(4) else ''}")
            edits.setdefault(f, []).append((m.start(2), m.end(), repl))
        else:
            same += 1
    if write:
        for f, es in edits.items():
            text = f.read_text(encoding="utf-8")
            for s, e, r in sorted(es, reverse=True):
                text = text[:s] + r + text[e:]
            f.write_text(text, encoding="utf-8")
    print(f"unaffected {same} · shifted only {len(moved)}{' (rewritten)' if write else ''} · "
          f"changed, need review {len(touched)}")
    for x in moved:
        print(f"  moved    {x}")
    for x in touched:
        print(f"  touched  {x}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="path to the miuix checkout the evidence cites")
    ap.add_argument("--gotchas", default=str(HERE / "data/gotchas"))
    ap.add_argument("--rebase", metavar="OLD_REV", help="map citations written against OLD_REV onto HEAD")
    ap.add_argument("--write", action="store_true", help="with --rebase: rewrite the moved line numbers")
    args = ap.parse_args()
    src, gotchas = pathlib.Path(args.src).resolve(), pathlib.Path(args.gotchas)
    if args.rebase:
        return rebase(src, gotchas, args.rebase, args.write)
    return check(src, gotchas)


if __name__ == "__main__":
    sys.exit(main())
