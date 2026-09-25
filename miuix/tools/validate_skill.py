#!/usr/bin/env python3
"""Check every skill under skills/ against the Agent Skills specification.

https://agentskills.io/specification -- the rules the installers (`npx skills`, Claude Code
plugins, Codex, Cursor ...) rely on when they discover a skill:

  * name: 1-64 chars, lowercase a-z 0-9 and single hyphens, equal to the directory name
  * description: 1-1024 chars;  compatibility: at most 500 chars when present
  * SKILL.md body under 500 lines (the whole file is loaded when the skill activates)

Plus what this repo adds on top: every relative link in SKILL.md and in the skill's
markdown files must resolve inside the skill directory -- a skill is copied around on its
own, so a link that climbs out of it is broken for every user.

    validate_skill.py            # exit 1 on any violation
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
MAX_BODY_LINES = 500


def frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    fields: dict[str, str] = {}
    key = None
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2).strip().strip('"').strip("'")
        elif key and line.startswith((" ", "\t")):  # folded continuation or a metadata map
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields, text[end + 5:]


def check_skill(skill_dir: pathlib.Path) -> list[str]:
    rel = skill_dir.relative_to(ROOT)
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        return [f"{rel}: missing SKILL.md"]
    parsed = frontmatter(md.read_text(encoding="utf-8"))
    if parsed is None:
        return [f"{rel}/SKILL.md: has no YAML frontmatter delimited by ---"]
    fm, body = parsed
    problems = []
    name, desc = fm.get("name", ""), fm.get("description", "")
    if not (1 <= len(name) <= 64 and NAME_RE.match(name)):
        problems.append(f"{rel}/SKILL.md: name {name!r} is invalid (1-64 chars of lowercase alphanumerics separated by single hyphens)")
    if name != skill_dir.name:
        problems.append(f"{rel}/SKILL.md: name {name!r} must equal the directory name {skill_dir.name!r}")
    if not 1 <= len(desc) <= 1024:
        problems.append(f"{rel}/SKILL.md: description length {len(desc)}, must be 1-1024 chars")
    if "compatibility" in fm and not 1 <= len(fm["compatibility"]) <= 500:
        problems.append(f"{rel}/SKILL.md: compatibility length {len(fm['compatibility'])}, must be 1-500 chars")
    n = body.count("\n")
    if n >= MAX_BODY_LINES:
        problems.append(f"{rel}/SKILL.md: body is {n} lines; the spec recommends < {MAX_BODY_LINES}, move detail into references/")
    for doc in sorted(skill_dir.rglob("*.md")):  # includes SKILL.md itself
        text = doc.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            target = m.group(1).split("#", 1)[0]
            if not target or re.match(r"^[a-z]+:", target):  # anchors, http:, mailto: ...
                continue
            resolved = (doc.parent / target).resolve()
            line = text[:m.start()].count("\n") + 1
            where = f"{doc.relative_to(ROOT)}:{line}"
            if not resolved.is_relative_to(skill_dir.resolve()):
                problems.append(f"{where}  link {target} points outside the skill directory (the skill is copied on its own)")
            elif not resolved.exists():
                problems.append(f"{where}  link {target} points to a file that does not exist")
    return problems


def main() -> int:
    skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    if not skills:
        print("error: no skill under skills/", file=sys.stderr)
        return 2
    problems = [p for s in skills for p in check_skill(s)]
    for p in problems:
        print("  " + p, file=sys.stderr)
    if problems:
        print(f"\n{len(problems)} violations of the Agent Skills spec", file=sys.stderr)
        return 1
    print(f"Agent Skills spec check passed: {', '.join(s.name for s in skills)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
