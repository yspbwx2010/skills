#!/usr/bin/env python3
"""Render data/miuix-api.json + data/gotchas/*.yaml into references/*.md.

Signatures in the output are reconstructed from the extracted JSON, never typed by
hand, so the reference cannot drift from the source the way the project's own docs did.

The output is one file per topic plus references/index.md. It used to be a single
10,800-line components.md, which an agent could only use through grep + sed -n line
ranges; a topic file is small enough to open whole when the task is "build a settings
page", and the index says which file holds which symbol.

Usage:
    render.py [--api data/miuix-api.json] [--gotchas data/gotchas] [--out-dir references]
    render.py --check        # exit 1 if references/ differs from a fresh render
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

# ------------------------------------------------------------------ yaml subset
# Always this parser, never PyYAML when it happens to be installed: the rendered references
# must not depend on the host, or render.py --check passes on one machine and fails in CI.
_ESCAPES = {"n": "\n", "t": "\t"}


class YamlError(ValueError):
    pass


def _scalar(text: str):
    t = text.strip()
    if not t:
        return ""
    if t == "[]":
        return []
    if t == "{}":
        return {}
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        body = t[1:-1]
        if t[0] == "'":
            return body
        # one pass, so \\n stays a backslash followed by n
        return re.sub(r"\\(.)", lambda m: _ESCAPES.get(m.group(1), m.group(1)), body)
    if t in ("true", "false"):
        return t == "true"
    if t == "null" or t == "~":
        return None
    return t


def _strip_comment(line: str) -> str:
    out, quote, escaped = [], None, False
    for c in line:
        if quote:
            out.append(c)
            if escaped:
                escaped = False
            elif c == "\\" and quote == '"':
                escaped = True
            elif c == quote:
                quote = None
            continue
        if c in "\"'":
            quote = c
            out.append(c)
            continue
        if c == "#" and (not out or out[-1] in " \t"):
            break
        out.append(c)
    return "".join(out).rstrip()


def load_yaml(text: str):
    """Parse the restricted YAML the gotchas files are written in.

    Deliberately not a general YAML implementation: mappings, lists of mappings,
    scalars, empty inline collections and block scalars are all these files use, and
    a skill's script has to run on a bare `python3` without a pip install.
    """
    lines = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        stripped = _strip_comment(raw)
        if not stripped.strip():
            continue
        lines.append((len(stripped) - len(stripped.lstrip()), stripped.strip()))
    value, idx = _parse_block(lines, 0, lines[0][0] if lines else 0)
    if idx != len(lines):
        raise YamlError(f"unparsed content from line {idx}: {lines[idx][1][:60]!r}")
    return value


def _parse_block(lines, i, indent):
    if i >= len(lines):
        return None, i
    if lines[i][1].startswith("- "):
        seq = []
        while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
            item_head = lines[i][1][2:].strip()
            if ":" in item_head and not item_head.startswith(("\"", "'")):
                # a mapping whose first key sits on the dash line
                sub = [(indent + 2, item_head)]
                j = i + 1
                while j < len(lines) and lines[j][0] > indent and not (
                        lines[j][0] == indent and lines[j][1].startswith("- ")):
                    sub.append((lines[j][0], lines[j][1]))
                    j += 1
                val, _ = _parse_block(sub, 0, indent + 2)
                seq.append(val)
                i = j
            else:
                seq.append(_scalar(item_head))
                i += 1
        return seq, i
    mapping = {}
    while i < len(lines) and lines[i][0] == indent:
        line = lines[i][1]
        if line.startswith("- "):
            break
        m = re.match(r'^("(?:[^"\\]|\\.)*"|\'[^\']*\'|[^:]+):\s*(.*)$', line)
        if not m:
            raise YamlError(f"bad mapping line: {line[:60]!r}")
        key, rest = _scalar(m.group(1)), m.group(2).strip()
        if rest in ("|", ">", "|-", ">-"):
            buf, j = [], i + 1
            while j < len(lines) and lines[j][0] > indent:
                buf.append(lines[j][1])
                j += 1
            mapping[key] = ("\n" if rest.startswith("|") else " ").join(buf)
            i = j
        elif rest:
            mapping[key] = _scalar(rest)
            i += 1
        else:
            if i + 1 < len(lines) and lines[i + 1][0] > indent:
                mapping[key], i = _parse_block(lines, i + 1, lines[i + 1][0])
            else:
                mapping[key] = None
                i += 1
    return mapping, i


# ------------------------------------------------------------------ rendering
def format_signature(fn: dict) -> str:
    """Rebuild the declaration from extracted data, marking what must be passed."""
    head = "@Composable\n" if fn.get("composable") else ""
    recv = f"{fn['receiver']}." if fn.get("receiver") else ""
    # `suspend` and `inline` change how the function can be called, so they stay in the
    # signature; visibility does not (everything rendered here is public).
    mods = [m for m in fn.get("modifiers") or [] if m in SIG_MODIFIERS]
    lead = " ".join(mods + ["fun"] + ([fn["type_params"]] if fn.get("type_params") else []))
    if not fn.get("params"):
        body = f"{lead} {recv}{fn['name']}()"
    else:
        lines = [f"{lead} {recv}{fn['name']}("]
        for p in fn["params"]:
            mods = " ".join(p.get("modifiers") or [])
            mods = f"{mods} " if mods else ""
            piece = f"    {mods}{p['name']}: {p['type']}"
            if p.get("default") is not None:
                piece += f" = {p['default']}"
            piece += ","
            if p.get("required"):
                piece += "  // required"
            lines.append(piece)
        lines.append(")")
        body = "\n".join(lines)
    if fn.get("returns"):
        body += f": {fn['returns']}"
    return head + body


SIG_MODIFIERS = ("suspend", "inline", "operator", "infix", "tailrec", "expect", "actual")
SEV = {"high": "🔴", "medium": "🟡", "low": "⚪"}
CATEGORY = {
    "basic": "basic component", "layout": "overlay content layout", "overlay": "Overlay overlay",
    "window": "Window overlay", "theme": "theme", "utils": "interaction utility", "anim": "easing",
    "color": "color", "icon": "icon", "nav": "navigation", "blur": "blur",
    "squircle": "smooth corners", "shader": "shader", "preference": "preference", "interfaces": "interface",
}


def category_of(fn: dict) -> str:
    pkg = fn.get("package") or ""
    tail = pkg.rsplit(".", 1)[-1]
    return CATEGORY.get(tail, tail or "?")


def gotcha_for(gotchas: dict, fn: dict):
    """Look the hand layer up by qualified name first, then by bare name."""
    if fn.get("receiver"):
        key = f"{fn['receiver']}.{fn['name']}"
        if key in gotchas:
            return key, gotchas[key]
    if fn["name"] in gotchas:
        return fn["name"], gotchas[fn["name"]]
    return None, {}


def load_gotchas(d: pathlib.Path) -> dict:
    merged: dict = {}
    for f in sorted(d.glob("*.yaml")):
        try:
            data = load_yaml(f.read_text(encoding="utf-8")) or {}
        except Exception as e:  # a broken hand-written file must be loud, not silent
            print(f"error: {f.name}: {e}", file=sys.stderr)
            raise
        for k, v in data.items():
            if k in merged:
                print(f"warning: {k} defined in two gotchas files", file=sys.stderr)
            merged[k] = v
    return merged


# ------------------------------------------------------------------ topics
# miuix-ui is split by what you are building, not by package: `basic/` alone was 5,000 lines.
# Keyed by source file stem so a component, its Defaults object and its types land together.
UI_BASIC = {
    "ui-scaffold": ["Scaffold", "TopAppBar", "Surface", "Card", "Divider", "PullToRefresh",
                    "ScrollBar", "SmallTitle", "Component"],
    "ui-navigation": ["NavigationBar", "NavigationRail", "TabRow", "BreadcrumbBar",
                      "FloatingToolbar", "FloatingActionButton", "SearchBar"],
    "ui-input": ["Button", "IconButton", "Switch", "Checkbox", "RadioButton", "Slider",
                 "TextField", "NumberPicker", "Dropdown"],
    "ui-display": ["Text", "Icon", "Badge", "ProgressIndicator", "Tooltip", "Snackbar", "ListPopup"],
    "ui-color": ["ColorPicker", "ColorPalette"],
}
UI_DIR = {"overlay": "ui-overlay", "window": "ui-overlay", "layout": "ui-overlay",
          "theme": "ui-theme", "anim": "ui-theme", "api": "ui-theme", "interfaces": "ui-theme",
          "utils": "ui-utils", "color": "ui-color"}
PREF_DIR = {"preference": "preference", "menu": "preference-menu", "popup": "preference-menu"}

TOPIC_META = {  # slug -> (title, what to open it for)
    "recipes": ("Recipes", "Compile-verified combinations: bottom bar + pager + collapsing top bar, Chinese text on the web, icons for common meanings"),
    "ui-scaffold": ("Scaffold & containers", "Page skeleton: Scaffold, TopAppBar, Card, Surface, dividers, pull-to-refresh, scrollbar, BasicComponent"),
    "ui-navigation": ("Navigation", "NavigationBar / NavigationRail / TabRow / BreadcrumbBar / FloatingToolbar / FAB / SearchBar"),
    "ui-input": ("Input controls", "Button, Switch, Checkbox, RadioButton, Slider, TextField, NumberPicker, Dropdown"),
    "ui-display": ("Display & feedback", "Text, Icon, Badge, ProgressIndicator, Tooltip, Snackbar, ListPopup content"),
    "ui-color": ("Color picking", "The ColorPicker family, ColorPalette, color-space types"),
    "ui-overlay": ("Overlays", "The Overlay* and Window* families of Dialog / BottomSheet / ListPopup, and overlay content layout"),
    "ui-theme": ("Theme", "MiuixTheme, colors, fonts, dynamic color, easing, HoldDown interaction"),
    "ui-utils": ("Interaction utilities", "overScroll bounce, press feedback, haptics, Pager gesture-conflict handling, back-gesture scope"),
    "preference": ("Preferences", "The various *Preference rows of miuix-preference"),
    "preference-menu": ("Preference menus & popups", "The popup menus themselves (DropdownMenu / CascadingListPopup, etc.); the dropdown preference rows *DropdownPreference / *SpinnerPreference are in preference.md"),
    "nav": ("Navigation framework", "miuix-nav: NavDisplay, back stack, transitions, predictive back gesture"),
    "blur": ("Blur", "miuix-blur: background blur, progressive blur, highlight, sensor"),
    "squircle": ("Smooth corners", "miuix-squircle: the squircle shape and clipping"),
    "shader": ("Shader", "miuix-shader"),
    "core": ("Core utilities", "miuix-core: platform detection and other low-level helpers"),
    "icons": ("Icon list", "Every MiuixIcons name; grep here before writing an icon"),
}
ORDER = list(TOPIC_META)


class RouteError(ValueError):
    pass


def route(mod: str, file: str) -> str:
    """Topic slug for a declaration, from its module and source path. Loud on anything new."""
    short = mod.removeprefix("miuix-")
    rel = file.split("/top/yukonga/miuix/kmp/", 1)[-1]
    parts = rel.split("/")
    first, stem = parts[0], parts[-1].split(".")[0]
    if mod == "miuix-ui":
        if first == "basic":
            for slug, stems in UI_BASIC.items():
                if stem in stems:
                    return slug
            raise RouteError(f"miuix-ui/basic/{stem}.kt is unclassified: give it a topic in UI_BASIC in render.py")
        if first in UI_DIR:
            return UI_DIR[first]
        raise RouteError(f"miuix-ui/{first}/ is unclassified: give it a topic in UI_DIR in render.py")
    if mod == "miuix-preference":
        if first in PREF_DIR:
            return PREF_DIR[first]
        raise RouteError(f"miuix-preference/{first}/ is unclassified: give it a topic in PREF_DIR in render.py")
    if short in TOPIC_META:
        return short
    raise RouteError(f"module {mod} has no topic yet: add an entry to TOPIC_META in render.py")


# ------------------------------------------------------------------ sections
def _gotcha_lines(g: dict) -> list[str]:
    out = []
    if g.get("gotchas"):
        out += ["**Traps**", ""]
        for h in g["gotchas"]:
            if isinstance(h, dict):
                out.append(f"- {SEV.get(h.get('severity'), '⚪')} {h.get('text', '')}"
                           f"  (`{h.get('evidence', '?')}`)")
        out.append("")
    if isinstance(g.get("visual"), dict):
        out += ["**Spec** " + " · ".join(f"{k} {vv}" for k, vv in g["visual"].items()), ""]
    if g.get("state"):
        out += [f"**State** {g['state']}", ""]
    if g.get("m3"):
        out += [f"**vs Material3** {g['m3']}", ""]
    return out


REPO = "https://github.com/compose-miuix-ui/miuix"


def _src_link(base: str, loc: str) -> str:
    """`path:line` -> a markdown link at the extracted ref, so readers without a checkout can open it."""
    path, _, line = loc.partition(":")
    anchor = f"#L{line.split('-')[0]}" if line else ""
    return f"[`{loc}`]({base}/{path}{anchor})"


def _function_section(fn: dict, g: dict, defaults: dict, types_by_name: dict,
                      repeat: bool = False, base: str = f"{REPO}/blob/main") -> list[str]:
    recv = f"{fn['receiver']}." if fn.get("receiver") else ""
    out = [f"## {recv}{fn['name']}  ·  {category_of(fn)}", ""]
    # Overloads share one hand-written entry. Printing it under every overload repeated
    # OverlaySpinnerPreference's traps six times; the first overload sits right above.
    if repeat:
        out += ["*Another overload. See the previous section for the hand-written notes "
                "(traps, spec, state, vs M3).*", ""]
    elif g.get("summary"):
        out += [str(g["summary"]), ""]
    if fn.get("doc"):
        out += ["> " + fn["doc"].replace("\n", "\n> "), ""]
    imp = f"{fn['package']}.{fn['name']}" if fn.get("package") else None
    out += ["```kotlin"]
    if imp:
        out += [f"import {imp}", ""]
    out += [format_signature(fn), "```", ""]
    if fn.get("expect_actual"):
        out += [f"Platform impls: {', '.join(fn['platforms'])}", ""]
    for p in fn.get("params", []):
        if p.get("doc"):
            out.append(f"- `{p['name']}` — {p['doc']}")
    if any(p.get("doc") for p in fn.get("params", [])):
        out.append("")
    dobj = defaults.get(fn["name"] + "Defaults")
    if dobj:
        out += [f"**{dobj['name']}**", ""]
        for df in dobj["functions"]:
            args = [f"{p['name']}: {p['type']}" + (f" = {p['default']}" if p["default"] else "")
                    for p in df["params"]]
            one_line = f"{df['name']}({', '.join(args)})"
            if len(one_line) <= 100:
                out.append(f"- `{one_line}`")
            else:
                # 8-parameter colour factories are unreadable on one line, and these
                # factory parameters are exactly what 7 of the project's doc pages omit
                out += ["", "```kotlin", f"{dobj['name']}.{df['name']}("]
                out += [f"    {a}," for a in args]
                out += [")", "```", ""]
        for c in dobj["constants"]:
            out.append(f"- `{c['name']} = {c['value']}`")
        out.append("")
    colors_t = types_by_name.get(fn["name"] + "Colors")
    if colors_t:
        priv = [p for p in colors_t["params"] if p.get("private")]
        out += [f"**{colors_t['name']}** ({colors_t['kind']}) "
                + (f"⚠️ {len(priv)}/{len(colors_t['params'])} constructor params are `private val` and "
                   "**cannot be read from an instance**; these names are only usable as named arguments "
                   "to the factory functions above."
                   if priv else ""), ""]
    if not repeat:
        out += _gotcha_lines(g)
    if fn.get("examples"):
        out += ["**Compilable examples** " + " · ".join(_src_link(base, e) for e in fn["examples"]), ""]
    loc = f"{fn['file']}:{fn['line']}"
    out += [f"<sub>Source {_src_link(base, loc)}</sub>", ""]
    return out


def _type_line(t: dict) -> str:
    # The import path is what a reader cannot guess: nested types import their outer class.
    outer = t["qualified"].split(".")[0]
    imp = f"`import {t['package']}.{outer}`" if t.get("package") else ""
    if t["kind"] == "enum":
        return f"- `{t['qualified']}` **enum** — {', '.join(t['entries']) or '(no entries)'} · {imp}"
    if not t["params"]:
        return f"- `{t['qualified']}` **{t['kind']}** · {imp}"
    req = [p["name"] for p in t["params"] if p["required"]]
    args = ", ".join(f"{p['name']}: {p['type']}" for p in t["params"])
    note = f"(required: {', '.join(req)})" if req else "(all params have defaults; constructible with no args)"
    return (f"- `{t['qualified']}({args[:160]}{'…' if len(args) > 160 else ''})`"
            f" **{t['kind']}** {note} · {imp}")


def render_all(api: dict, gotchas: dict, recipes: list[tuple[str, str]] | None = None) -> dict[str, str]:
    """Every output file, name -> text. Pure: the caller decides whether to write or compare."""
    version = api["miuix_version"]
    ref = api.get("source_ref") or "main"
    base = f"{REPO}/blob/{ref}"
    raw = f"https://raw.githubusercontent.com/compose-miuix-ui/miuix/{ref}"
    locate = (f"Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `{ref}`]({REPO}/tree/{ref}). "
              f"Without a local checkout, fetch the source: `curl -sL {raw}/<path> | sed -n '100,140p'`.")
    bucket: dict[str, dict] = {s: {"fns": [], "types": [], "props": [], "icons": {}, "notes": []}
                               for s in ORDER}
    defaults, types_by_name, homes = {}, {}, {}
    for mod, m in api["modules"].items():
        for o in m["defaults_objects"]:
            defaults[o["name"]] = o
            homes[o["name"]] = route(mod, o["file"])
        for o in m["other_objects"]:
            homes.setdefault(o["name"], route(mod, o["file"]))
        for t in m.get("types", []):
            types_by_name[t["name"]] = t
            homes.setdefault(t["name"], route(mod, t["file"]))
        for fn in m["functions"]:
            bucket[route(mod, fn["file"])]["fns"].append(fn)
        for t in m.get("types", []):
            # every public type, including marker interfaces (NavKey) and no-arg classes
            # (SnackbarHostState): leaving them out left their import path unfindable
            if not t["name"].endswith("Colors"):
                bucket[route(mod, t["file"])]["types"].append(t)
        seen = set()
        for c in m["constants"]:
            # expect/actual pairs report the same property once per platform file
            if c["visibility"] == "public" and c.get("top_level") and c["name"] not in seen:
                seen.add(c["name"])
                bucket[route(mod, c["file"])]["props"].append(c)
                homes.setdefault(c["name"], route(mod, c["file"]))
        for i in m.get("icons") or []:
            ns = i["namespace"] or "(directly on MiuixIcons)"
            bucket["icons"]["icons"].setdefault((mod, i.get("package") or "?", ns), []).append(i["name"])

    used: set = set()
    files: dict[str, str] = {}
    counts: dict[str, int] = {}
    symbols: dict[str, list[str]] = {}
    for slug in ORDER:
        b = bucket[slug]
        title, blurb = TOPIC_META[slug]
        names: list[str] = []
        body: list[str] = []
        shown: set = set()
        for fn in sorted(b["fns"], key=lambda f: (f["name"].lower(), f.get("receiver") or "")):
            key, g = gotcha_for(gotchas, fn)
            if key:
                used.add(key)
            body += _function_section(fn, g, defaults, types_by_name,
                                      repeat=bool(key) and key in shown, base=base)
            if key:
                shown.add(key)
            names.append((f"{fn['receiver']}." if fn.get("receiver") else "") + fn["name"])
        if b["props"]:
            body += [f"## Top-level properties & CompositionLocals ({len(b['props'])})", ""]
            for c in sorted(b["props"], key=lambda c: c["name"]):
                # `val LocalContentColor = compositionLocalOf { … }` has no written type; the
                # initializer's head says what it is just as well
                decl = (f"{c['name']}: {c['type']}" if c["type"]
                        else f"{c['name']} = {c['value'].split('{')[0].strip()} {{ … }}")
                loc = f"{c['file']}:{c['line']}"
                body.append(f"- `{decl}`  <sub>{_src_link(base, loc)}</sub>")
                names.append(c["name"])
                g = gotchas.get(c["name"])
                if g:
                    used.add(c["name"])
                    if g.get("summary"):
                        body.append(f"  {g['summary']}")
                    for h in g.get("gotchas") or []:
                        if isinstance(h, dict):
                            body.append(f"  - {SEV.get(h.get('severity'), '⚪')} {h.get('text', '')}"
                                        f"  (`{h.get('evidence', '?')}`)")
            body.append("")
        if b["types"]:
            body += [f"## Public types in this topic ({len(b['types'])})", ""]
            body += [_type_line(t) for t in sorted(b["types"], key=lambda t: t["qualified"])]
            body.append("")
        if b["icons"]:
            total = sum(len(v) for v in b["icons"].values())
            body += [f"## Icons ({total})", "",
                     "Every icon is an **extension property** on `MiuixIcons` (or one of its sub-objects), "
                     "so you import two things: `MiuixIcons` itself, and the package the icon name lives in.", "",
                     "```kotlin",
                     "import top.yukonga.miuix.kmp.icon.MiuixIcons",
                     "import top.yukonga.miuix.kmp.icon.extended.Back      // miuix-icons module",
                     "import top.yukonga.miuix.kmp.icon.basic.Search       // Basic, bundled with miuix-ui",
                     "",
                     "Icon(MiuixIcons.Back, contentDescription = \"Back\")",
                     "Icon(MiuixIcons.Light.Back, contentDescription = \"Back\")   // pick a weight",
                     "Icon(MiuixIcons.Basic.Search, contentDescription = \"Search\")",
                     "```", ""]
            for (mod, pkg, ns), icon_names in sorted(b["icons"].items()):
                recv = "MiuixIcons" + ("" if ns.startswith("(") else f".{ns}")
                body += [f"**{recv}.*** — {len(icon_names)} · module `{mod}` · `import {pkg}.<IconName>`", "",
                         "```", ", ".join(sorted(icon_names)), "```", ""]
        # hand-written notes on types / objects / namespaces go next to the code they describe
        notes = sorted(k for k in set(gotchas) - used if homes.get(k) == slug)
        if notes:
            body += ["## Notes on types & namespaces", ""]
            for name in notes:
                used.add(name)
                g = gotchas[name]
                body += [f"### {name}", ""]
                if g.get("summary"):
                    body += [str(g["summary"]), ""]
                body += _gotcha_lines(g)
        if not body:
            continue
        head = [f"# {title}", "",
                f"{blurb}. Signatures are generated automatically from the miuix **{version}** source, "
                f"not hand-written. See [index.md](index.md) for the other topics.", "", locate, ""]
        files[f"{slug}.md"] = "\n".join(head + body) + "\n"
        counts[slug] = len(names)
        symbols[slug] = names

    # Hand-written recipes: combinations the API reference cannot express on its own. Each one
    # was compiled in an empty-directory trial; check_skill.py still validates every symbol.
    if recipes:
        title, blurb = TOPIC_META["recipes"]
        body = [f"# {title}", "", f"{blurb}. Hand-written, from `data/recipes/`; each was compiled in an "
                f"empty-directory trial. See [index.md](index.md) for the other topics.", ""]
        names = []
        for _, text in recipes:
            body += [text.rstrip(), ""]
            names += [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
        files["recipes.md"] = "\n".join(body) + "\n"
        counts["recipes"] = len(names)
        symbols["recipes"] = names

    orphan = sorted(set(gotchas) - used)
    files["index.md"] = _index(version, files, counts, symbols, orphan, locate)
    return files


def _index(version, files, counts, symbols, orphan, locate) -> str:
    out = ["# Miuix reference index", "",
           f"For miuix **{version}**. One file per topic; signatures are generated from the source "
           "(maintainers regenerate with `tools/render.py` at the repo root — do not hand-edit).", "", locate, "",
           "**Find a symbol**: grep the section headings across files, then pull that section by line.", "",
           "```bash",
           'grep -rn "^## Switch  " references/            # -> references/ui-input.md:<line>',
           'sed -n "<line>,+60p" references/ui-input.md     # read that section',
           "```", "",
           "**Build a kind of UI**: pick a topic file from the table and read it whole — each is kept "
           "to around a thousand-odd lines.", "",
           "| File | Topic | For | Entries | Lines |", "| --- | --- | --- | ---: | ---: |"]
    for slug in ORDER:
        name = f"{slug}.md"
        if name not in files:
            continue
        title, blurb = TOPIC_META[slug]
        n = counts[slug] if slug != "icons" else "—"
        out.append(f"| [{name}]({name}) | {title} | {blurb} | {n} | {files[name].count(chr(10))} |")
    out += ["", "## Symbol -> file", ""]
    for slug in ORDER:
        if slug in ("icons", "recipes") or not symbols.get(slug):
            continue
        uniq = list(dict.fromkeys(symbols[slug]))
        out += [f"**{slug}.md** — " + ", ".join(f"`{s}`" for s in uniq), ""]
    if orphan:
        out += ["## ⚠️ Hand-written entries with no matching public API", "",
                "These names have an entry in `data/gotchas/` but no public declaration of the same name "
                "in the source — either the name is wrong, or the API was removed:", ""]
        out += [f"- `{o}`" for o in orphan] + [""]
    return "\n".join(out) + "\n"


def main() -> int:
    here = pathlib.Path(__file__).parent.parent
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--api", default=str(here / "data/miuix-api.json"))
    ap.add_argument("--gotchas", default=str(here / "data/gotchas"))
    ap.add_argument("--recipes", default=str(here / "data/recipes"))
    ap.add_argument("--out-dir", default=str(here / "skills/miuix/references"))
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the out dir differs from a fresh render (stale or extra files)")
    args = ap.parse_args()
    api = json.loads(pathlib.Path(args.api).read_text(encoding="utf-8"))
    gdir = pathlib.Path(args.gotchas)
    gotchas = load_gotchas(gdir) if gdir.is_dir() else {}
    rdir = pathlib.Path(args.recipes)
    recipes = [(f.name, f.read_text(encoding="utf-8")) for f in sorted(rdir.glob("*.md"))] if rdir.is_dir() else []
    try:
        files = render_all(api, gotchas, recipes)
    except RouteError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    out = pathlib.Path(args.out_dir)
    existing = {p.name for p in out.glob("*.md")} if out.is_dir() else set()
    if args.check:
        stale = sorted(n for n, t in files.items()
                       if not (out / n).is_file() or (out / n).read_text(encoding="utf-8") != t)
        extra = sorted(existing - set(files))
        for n in stale:
            print(f"  stale or missing: {out / n}", file=sys.stderr)
        for n in extra:
            print(f"  extra (render no longer produces it): {out / n}", file=sys.stderr)
        if stale or extra:
            print("\nreferences/ is out of sync with data; re-run render.py", file=sys.stderr)
            return 1
        print(f"references/ is up to date ({len(files)} files)")
        return 0
    out.mkdir(parents=True, exist_ok=True)
    for n in existing - set(files):  # a topic that no longer exists must not linger as truth
        (out / n).unlink()
    for n, t in files.items():
        (out / n).write_text(t, encoding="utf-8")
    total = sum(t.count("\n") for t in files.values())
    biggest = max((t.count("\n"), n) for n, t in files.items())
    print(f"wrote {len(files)} files to {out} ({total:,} lines, largest {biggest[1]} "
          f"{biggest[0]:,}; {len(gotchas)} hand-written entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
