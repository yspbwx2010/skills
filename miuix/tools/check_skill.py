#!/usr/bin/env python3
"""Verify every Miuix symbol used in the skill's own prose against the extracted API.

The audit's single most damaging finding about miuix's own docs was §7.10: the
examples are hand-written and nothing checks them, so 28 of them no longer compile.
This skill would rot exactly the same way without a gate, so this is that gate --
every Kotlin identifier the skill names is looked up in data/miuix-api.json.

Usage:
    check_skill.py                # exit 1 on any unknown symbol
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent.parent
CODE_BLOCK = re.compile(r"```(?:kotlin|kt)\n(.*?)```", re.S)
BLOCKQUOTE = re.compile(r"(?m)^>.*$")
# a call or a qualified reference we can check: Name( ... or Ns.Name
CALL = re.compile(r"(?<![A-Za-z0-9_.])([A-Z][A-Za-z0-9_]*)\s*\(")
ICON_REF = re.compile(r"MiuixIcons\.(?:([A-Z][A-Za-z0-9_]*)\.)?([A-Z][A-Za-z0-9_]*)")
IMPORT = re.compile(r"(?m)^[ \t]*import\s+([a-z][\w.]*\.)([A-Za-z_][\w]*)\s*(?://.*)?$")
DECL = re.compile(r"\b(?:class|object|interface|fun)\s+([A-Z][A-Za-z0-9_]*)")

# Kotlin/Compose/stdlib names that legitimately appear and are not Miuix API.
ALLOW = {
    "Modifier", "Color", "PaddingValues", "Unit", "Boolean", "Int", "Float", "String", "Dp",
    "MutableInteractionSource", "WindowInsets", "Composable", "List", "Map", "Set",
    "RoundedCornerShape", "Text", "Row", "Column", "Box", "Spacer", "LazyColumn",
    "CompositionLocalProvider", "LaunchedEffect", "Icon", "Switch", "Card", "Button",
    "SolidColor", "Brush", "Shape", "TextStyle", "FontWeight", "ImageVector",
    "MutableState", "State", "Alignment", "Arrangement", "DpSize", "DpOffset",
    "EnterTransition", "ExitTransition", "AnimationSpec", "InteractionSource",
    "HorizontalPager", "VerticalPager", "PagerState",
}


def load_api() -> dict:
    data = json.loads((HERE / "data/miuix-api.json").read_text(encoding="utf-8"))
    names, icons, packages = set(), set(), {}
    for mod in data["modules"].values():
        for f in mod["functions"]:
            names.add(f["name"])
            if f.get("package"):
                packages.setdefault(f["name"], set()).add(f["package"])
        for o in mod["defaults_objects"] + mod["other_objects"]:
            names.add(o["name"])
            for df in o["functions"]:
                names.add(df["name"])
        for i in mod.get("icons", []):
            icons.add((i["namespace"], i["name"]))
        for t in mod.get("types", []):
            names.add(t["name"])
            if t.get("package"):
                packages.setdefault(t["name"], set()).add(t["package"])
            for e in t.get("entries", []):
                names.add(e)
            for cf in t.get("companion_functions", []):
                names.add(cf["name"])
    return {"version": data["miuix_version"], "names": names,
            "icons": icons, "packages": packages}


def check_file(path: pathlib.Path, api: dict) -> list[str]:
    text = path.read_text(encoding="utf-8")
    # KDoc quoted into the reference is the library's own commentary, not this skill's
    # examples, and it legitimately names third-party symbols (ModalBottomSheet, ...).
    text = BLOCKQUOTE.sub("", text)
    problems = []
    for block in CODE_BLOCK.findall(text):
        line_of = lambda frag: text[:text.index(frag)].count("\n") + 1 if frag in text else 0
        # classes / objects / functions the snippet declares itself are not Miuix API, and neither
        # is anything it imports from a non-Miuix package (Compose Resources' Font, FontFamily ...)
        declared = set(DECL.findall(block))
        declared |= {name for pkg, name in IMPORT.findall(block) if not pkg.startswith("top.yukonga.miuix")}
        for name in set(CALL.findall(block)):
            if name in ALLOW or name in api["names"] or name in declared:
                continue
            # enum/class references used as values are not in the function index;
            # only flag things that look like a call to a Miuix composable
            problems.append(f"{path.name}:{line_of(name)}  unknown call `{name}(`")
        for ns, name in set(ICON_REF.findall(block)):
            ns = ns or None
            known = {(n, m) for n, m in api["icons"]}
            if (ns, name) not in known and (None, name) not in known:
                problems.append(f"{path.name}  icon does not exist `MiuixIcons."
                                f"{ns + '.' if ns else ''}{name}`")
        for pkg, name in IMPORT.findall(block):
            if not pkg.startswith("top.yukonga.miuix"):
                continue
            if name in api["names"] or name in {n for _, n in api["icons"]}:
                pkgs = api["packages"].get(name)
                if pkgs and pkg.rstrip(".") not in pkgs:
                    problems.append(f"{path.name}  wrong import package `{pkg}{name}`, "
                                    f"actually in {sorted(pkgs)}")
            else:
                problems.append(f"{path.name}  imported a symbol that does not exist `{pkg}{name}`")
    return problems


def main() -> int:
    api = load_api()
    skill = HERE / "skills/miuix"
    targets = [skill / "SKILL.md"] + sorted((skill / "references").glob("*.md"))
    targets = [t for t in targets if t.is_file()]
    problems = []
    for t in targets:
        problems += check_file(t, api)
    for p in problems:
        print("  " + p, file=sys.stderr)
    checked = ", ".join(t.name for t in targets)
    if problems:
        print(f"\n{len(problems)} symbols do not match the real miuix {api['version']} API (checked {checked})",
              file=sys.stderr)
        return 1
    print(f"every Miuix symbol in the skill matches the real miuix {api['version']} API ({checked})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
