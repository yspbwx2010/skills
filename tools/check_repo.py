#!/usr/bin/env python3
"""Every skill in this repository is installable and listed.

Each skill lives in <name>/ with the installable directory at <name>/skills/<name>/. Both
`npx skills add` and the Claude Code marketplace find skills through
.claude-plugin/marketplace.json only, so a skill missing from it cannot be installed at all.
This gate checks, for every <name>/skills/<name>/SKILL.md and every marketplace entry:

- the marketplace has a plugin named <name> with source "./<name>";
- SKILL.md's `name:` and <name>/.claude-plugin/plugin.json's `name` (if present) are <name>;
- <name>/README.md (Chinese, default) and <name>/README.en.md exist, and the root READMEs link to them;
- <name>/AGENTS.md exists and <name>/CLAUDE.md is exactly `@AGENTS.md`.

Standard library only; exits 1 on any problem.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    errors: list[str] = []
    market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    plugins = {p["name"]: p for p in market.get("plugins", [])}
    on_disk = sorted(p.parent.name for p in ROOT.glob("*/skills/*/SKILL.md")
                     if p.parent.name == p.parent.parent.parent.name)
    strays = sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("*/skills/*/SKILL.md")
                    if p.parent.name != p.parent.parent.parent.name)
    for s in strays:
        errors.append(f"{s}: a skill must sit at <name>/skills/<name>/SKILL.md")

    for name in sorted(set(on_disk) | set(plugins)):
        where = f"{name}/"
        if name not in plugins:
            errors.append(f"{where}: not in .claude-plugin/marketplace.json, so it cannot be installed")
        elif plugins[name].get("source") != f"./{name}":
            errors.append(f"marketplace plugin {name}: source must be \"./{name}\", "
                          f"not {plugins[name].get('source')!r}")
        skill_md = ROOT / name / "skills" / name / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"marketplace plugin {name}: {skill_md.relative_to(ROOT)} does not exist")
            continue
        m = re.search(r"^name:\s*(\S+)\s*$", skill_md.read_text(encoding="utf-8"), re.M)
        if not m or m.group(1) != name:
            errors.append(f"{skill_md.relative_to(ROOT)}: frontmatter name must be {name!r}")
        manifest = ROOT / name / ".claude-plugin" / "plugin.json"
        if manifest.is_file() and json.loads(manifest.read_text(encoding="utf-8")).get("name") != name:
            errors.append(f"{manifest.relative_to(ROOT)}: name must be {name!r}")
        for readme in ("README.md", "README.en.md"):
            if not (ROOT / name / readme).is_file():
                errors.append(f"{where}{readme} is missing")
            if f"]({name}/{readme})" not in (ROOT / readme).read_text(encoding="utf-8"):
                errors.append(f"root {readme} does not link to {name}/{readme}")
        if not (ROOT / name / "AGENTS.md").is_file():
            errors.append(f"{where}AGENTS.md is missing")
        claude = ROOT / name / "CLAUDE.md"
        if not claude.is_file() or claude.read_text(encoding="utf-8").strip() != "@AGENTS.md":
            errors.append(f"{where}CLAUDE.md must contain exactly @AGENTS.md")

    for e in errors:
        print(f"  {e}", file=sys.stderr)
    if errors:
        print("\nrepository layout check failed", file=sys.stderr)
        return 1
    print(f"repository layout ok: {', '.join(on_disk)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
