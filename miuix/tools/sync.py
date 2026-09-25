#!/usr/bin/env python3
"""Extract the Miuix public API from Kotlin source into a machine-readable knowledge base.

Why this exists: miuix's own docs drifted from its source (272 findings, 28 of them
"copy the example and it will not compile"). Anything hand-copied rots the same way,
so signatures are never written by hand here -- they are re-extracted from the source
and diffed. Run with --check in CI or before trusting the baked data.

Usage:
    sync.py --src <path-to-miuix-checkout> [--out data/miuix-api.json]
    sync.py --src <path> --check          # exit 1 if the committed data is stale
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

OPEN, CLOSE = "([{", ")]}"
IDENT = re.compile(r"[A-Za-z0-9_>]")
VISIBILITY = ("private", "internal", "protected", "public")
MODIFIERS = (
    "public private internal protected expect actual inline suspend open override "
    "external final abstract operator infix tailrec annotation data value"
).split()


# --------------------------------------------------------------------------- masking
def mask(src: str) -> str:
    """Blank out comments and string contents, preserving offsets.

    Every structural scan (bracket depth, declaration finding) runs on the mask so a
    comma inside "a, b" or a brace inside a comment can never shift the parse.
    """
    out = list(src)
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        two = src[i:i + 2]
        if two == "//":
            while i < n and src[i] != "\n":
                out[i] = " "
                i += 1
        elif two == "/*":
            while i < n and src[i:i + 2] != "*/":
                if src[i] != "\n":
                    out[i] = " "
                i += 1
            for j in range(i, min(i + 2, n)):
                out[j] = " "
            i += 2
        elif two == '""' and src[i:i + 3] == '"""':
            out[i] = out[i + 1] = out[i + 2] = " "
            i += 3
            while i < n and src[i:i + 3] != '"""':
                if src[i] != "\n":
                    out[i] = " "
                i += 1
            for j in range(i, min(i + 3, n)):
                out[j] = " "
            i += 3
        elif c in "\"'":
            quote = c
            out[i] = " "
            i += 1
            while i < n and src[i] != quote:
                if src[i] == "\\":
                    out[i] = " "
                    i += 1
                    if i < n:
                        out[i] = " "
                        i += 1
                    continue
                if src[i] != "\n":
                    out[i] = " "
                i += 1
            if i < n:
                out[i] = " "
            i += 1
        else:
            i += 1
    return "".join(out)


def _depths(masked: str):
    """Yield (index, bracket_depth, angle_depth) across a masked string."""
    depth = angle = 0
    for i, c in enumerate(masked):
        prev = masked[i - 1] if i else ""
        if c in OPEN:
            depth += 1
        elif c in CLOSE:
            depth -= 1
        elif c == "<" and IDENT.match(prev or " ") and masked[i + 1:i + 2] != "=":
            angle += 1
        elif c == ">" and angle > 0 and prev != "-":
            # '->' is an arrow, never a closing generic
            angle -= 1
        yield i, depth, angle


def split_top_level(s: str, sep: str = ",") -> list[str]:
    """Split on `sep` only where bracket and generic depth are both zero."""
    m = mask(s)
    parts, start = [], 0
    for i, depth, angle in _depths(m):
        if m[i] == sep and depth == 0 and angle == 0:
            parts.append(s[start:i])
            start = i + 1
    parts.append(s[start:])
    return [p.strip() for p in parts if p.strip()]


def _find_top_level(s: str, chars: str) -> int:
    """Index of the first char from `chars` at zero depth, or -1."""
    m = mask(s)
    for i, depth, angle in _depths(m):
        if m[i] in chars and depth == 0 and angle == 0:
            return i
    return -1


def match_bracket(masked: str, open_idx: int) -> int:
    """Index of the bracket closing the one at `open_idx`, or -1."""
    depth = 0
    for i in range(open_idx, len(masked)):
        if masked[i] in OPEN:
            depth += 1
        elif masked[i] in CLOSE:
            depth -= 1
            if depth == 0:
                return i
    return -1


# --------------------------------------------------------------------------- params
def parse_params(param_str: str) -> list[dict]:
    params = []
    for raw in split_top_level(param_str):
        chunk = raw.strip().rstrip(",")
        annotations = []
        while chunk.startswith("@"):
            head = re.match(r"@[A-Za-z_][A-Za-z0-9_.]*(\([^)]*\))?\s*", chunk)
            if not head:
                break
            annotations.append(head.group(0).strip())
            chunk = chunk[head.end():]
        colon = _find_top_level(chunk, ":")
        if colon < 0:
            continue
        name_part, rest = chunk[:colon].strip(), chunk[colon + 1:].strip()
        tokens = [t for t in name_part.split() if t]
        if not tokens:
            continue
        name = tokens[-1]
        pmods = [t for t in tokens[:-1] if t in ("vararg", "crossinline", "noinline")]
        eq = -1
        mrest = mask(rest)
        for i, depth, angle in _depths(mrest):
            if (mrest[i] == "=" and depth == 0 and angle == 0
                    and mrest[i - 1:i] not in ("=", "!", "<", ">") and mrest[i + 1:i + 2] != "="):
                eq = i
                break
        if eq >= 0:
            ptype, default = rest[:eq].strip(), rest[eq + 1:].strip()
        else:
            ptype, default = rest.strip(), None
        params.append({
            "name": name,
            "type": ptype,
            "default": default,
            "required": default is None,
            "modifiers": pmods,
            "annotations": annotations,
            "doc": None,
        })
    return params


# --------------------------------------------------------------------------- kdoc
KDOC_RE = re.compile(r"/\*\*(.*?)\*/", re.S)


def parse_kdoc(block: str) -> dict:
    lines = []
    for line in block.splitlines():
        line = line.strip()
        line = re.sub(r"^/\*\*", "", line)
        line = re.sub(r"\*/$", "", line)
        line = re.sub(r"^\*\s?", "", line)
        lines.append(line.rstrip())
    desc, params, i = [], {}, 0
    current = None
    for line in lines:
        m = re.match(r"@param\s+(\[?)([A-Za-z_][A-Za-z0-9_]*)\]?\s*(.*)", line)
        if m:
            current = m.group(2)
            params[current] = m.group(3).strip()
            continue
        if line.startswith("@"):
            current = None
            continue
        if current:
            if line:
                params[current] = (params[current] + " " + line).strip()
        elif not params:
            desc.append(line)
    return {"desc": "\n".join(desc).strip(), "params": params}


def _walk_back_annotations(src: str, pos: int) -> tuple[list[str], str]:
    """Annotations attached to the declaration at `pos`, and the text left above them.

    Only contiguous annotation lines immediately above the declaration count. A coarse
    "look back N characters" scan reads annotations out of the *previous* declaration's
    body -- e.g. Scaffold's `content: @Composable (PaddingValues) -> Unit` would mark
    the next top-level function as @Composable.
    """
    head = src[:pos]
    line_start = head.rfind("\n") + 1
    anns = re.findall(r"@([A-Za-z_][A-Za-z0-9_]*)", head[line_start:])
    rest = head[:line_start].rstrip()
    while rest:
        ls = rest.rfind("\n") + 1
        line = rest[ls:].strip()
        if not line.startswith("@"):
            break
        anns += re.findall(r"@([A-Za-z_][A-Za-z0-9_]*)", line)
        rest = rest[:ls].rstrip()
    return anns, rest


def kdoc_before(src: str, masked: str, pos: int) -> dict | None:
    """The KDoc block immediately above `pos`, skipping annotation lines."""
    _, stripped = _walk_back_annotations(src, pos)
    if not stripped.endswith("*/"):
        return None
    start = stripped.rfind("/**")
    if start < 0:
        return None
    return parse_kdoc(stripped[start:])


# --------------------------------------------------------------------------- decls
FUN_RE = re.compile(
    r"(?m)^[ \t]*(?P<mods>(?:(?:" + "|".join(MODIFIERS) + r")[ \t]+)*)"
    # type parameters may nest one level: `<reified T : NavKey>`, `<T : Comparable<T>>`
    r"fun[ \t]+(?:(?P<tparams><(?:[^<>]|<[^<>]*>)*>)[ \t]+)?(?P<sig>[A-Za-z_][A-Za-z0-9_.<>?]*)[ \t]*\("
)
OBJ_RE = re.compile(r"(?m)^[ \t]*(?P<mods>(?:(?:" + "|".join(MODIFIERS) + r")[ \t]+)*)"
                    r"object[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_]*)[ \t]*\{")
VAL_RE = re.compile(r"(?m)^(?P<indent>[ \t]*)(?P<mods>(?:(?:" + "|".join(MODIFIERS) +
                    r"|const|lateinit)[ \t]+)*)(?P<kind>val|var)[ \t]+"
                    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)[ \t]*(?::[ \t]*(?P<type>[^=\n]+?))?[ \t]*=[ \t]*"
                    # the initializer may start on the next line: `val Local…: Provid…<T> =\n    staticCompositionLocalOf {`
                    # -- requiring it on the `=` line is how LocalNavTransitionScope went missing from 0.9.4
                    r"(?P<value>.+|\n[ \t]*\S.*)$")


def _visibility(mods: str) -> str:
    for v in VISIBILITY:
        if re.search(rf"\b{v}\b", mods):
            return v
    return "public"


def _brace_depth_at(masked: str) -> list[int]:
    """Depth *before* each index, counting only braces."""
    depths, d = [], 0
    for c in masked:
        depths.append(d)
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
    return depths


def find_functions(src: str, top_level_only: bool = True, include_nonpublic: bool = False) -> list[dict]:
    masked = mask(src)
    bd = _brace_depth_at(masked)
    out = []
    for m in FUN_RE.finditer(masked):
        if top_level_only and bd[m.start()] != 0:
            continue
        vis = _visibility(m.group("mods"))
        if vis != "public" and not include_nonpublic:
            continue
        open_idx = m.end() - 1
        close_idx = match_bracket(masked, open_idx)
        if close_idx < 0:
            continue
        params = parse_params(src[open_idx + 1:close_idx])
        tail = src[close_idx + 1:close_idx + 200]
        rt = re.match(r"[ \t]*:[ \t]*([^={\n]+)", tail)
        sig = m.group("sig")
        dot = sig.rfind(".")
        receiver, name = (sig[:dot], sig[dot + 1:]) if dot > 0 else (None, sig)
        doc = kdoc_before(src, masked, m.start())
        if doc:
            for p in params:
                p["doc"] = doc["params"].get(p["name"])
        anns, _ = _walk_back_annotations(src, m.start())
        out.append({
            "name": name,
            "receiver": receiver,
            "composable": "Composable" in anns,
            "annotations": anns,
            "modifiers": m.group("mods").split(),
            # dropped before 0.9.4's sync: `rememberNavBackStack(vararg elements: T)` with no
            # `<reified T : NavKey>` left readers guessing what T was
            "type_params": " ".join(src[m.start("tparams"):m.end("tparams")].split()) if m.group("tparams") else None,
            "visibility": vis,
            "params": params,
            "returns": rt.group(1).strip() if rt else None,
            "doc": doc["desc"] if doc else None,
            "line": src[:m.start()].count("\n") + 1,
        })
    return out


def find_objects(src: str) -> list[dict]:
    masked = mask(src)
    bd = _brace_depth_at(masked)
    out = []
    for m in OBJ_RE.finditer(masked):
        if bd[m.start()] != 0 or _visibility(m.group("mods")) != "public":
            continue
        open_idx = masked.index("{", m.end() - 1)
        close_idx = match_bracket(masked, open_idx)
        body = src[open_idx + 1:close_idx]
        out.append({
            "name": m.group("name"),
            "functions": find_functions(body, top_level_only=True),
            "constants": [c for c in find_constants(body) if c["visibility"] == "public"],
            "doc": (kdoc_before(src, masked, m.start()) or {}).get("desc"),
            "line": src[:m.start()].count("\n") + 1,
        })
    return out


def find_constants(src: str) -> list[dict]:
    masked = mask(src)
    bd = _brace_depth_at(masked)
    out = []
    for m in VAL_RE.finditer(masked):
        if bd[m.start()] != 0:
            continue
        value = src[m.start("value"):m.end("value")].strip()
        out.append({
            "name": m.group("name"),
            "kind": m.group("kind"),
            "type": (m.group("type") or "").strip() or None,
            "value": value,
            "visibility": _visibility(m.group("mods")),
            "const": "const" in m.group("mods"),
            # brace depth 0 also matches a primary constructor's `val x: T = ...` lines (they sit
            # inside parentheses, not braces); only an unindented declaration is really top-level
            "top_level": m.group("indent") == "",
            "line": src[:m.start()].count("\n") + 1,
        })
    return out


PACKAGE_RE = re.compile(r"(?m)^package[ \t]+([A-Za-z_][\w.]*)")


def find_package(src: str) -> str | None:
    m = PACKAGE_RE.search(mask(src))
    return m.group(1) if m else None


ICON_RE = re.compile(
    r"(?m)^[ \t]*(?:public[ \t]+)?val[ \t]+MiuixIcons"
    r"(?:\.(?P<ns>[A-Za-z_]\w*))?\.(?P<name>[A-Za-z_]\w*)[ \t]*:[ \t]*ImageVector\b"
)


def find_icons(src: str) -> list[dict]:
    """Icon names, which are extension properties, not vals with an initializer.

    Worth extracting on its own: the audit found five separate places where a
    non-existent icon (MiuixIcons.Save, MiuixIcons.Basic.Audio) was written by
    someone working from the docs. An authoritative name list is the fix.
    """
    masked = mask(src)
    out = []
    for m in ICON_RE.finditer(masked):
        out.append({
            "name": m.group("name"),
            "namespace": m.group("ns"),
            "qualified": "MiuixIcons." + (f"{m.group('ns')}." if m.group("ns") else "") + m.group("name"),
            "line": src[:m.start()].count("\n") + 1,
        })
    return out


def merge_platform_variants(functions: list[dict]) -> list[dict]:
    """Collapse an expect declaration and its actuals into one entry.

    Without this, getRoundedCorner shows up three times (commonMain + androidMain +
    skikoMain) and an agent reading the knowledge base cannot tell overloads from
    platform implementations. The expect declaration wins as canonical because it is
    the API contract and carries the KDoc.
    """
    groups: dict[tuple, list[dict]] = {}
    order: list[tuple] = []
    for f in functions:
        key = (f.get("receiver"), f["name"], tuple(p["type"] for p in f["params"]))
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(f)
    merged = []
    for key in order:
        variants = groups[key]
        canonical = next(
            (v for v in variants if "expect" in v.get("modifiers", [])),
            next((v for v in variants if v.get("sourceset") == "commonMain"), variants[0]),
        )
        entry = dict(canonical)
        entry["platforms"] = sorted({v.get("sourceset") for v in variants if v.get("sourceset")})
        entry["expect_actual"] = len(variants) > 1
        if entry["expect_actual"]:
            entry["actual_files"] = sorted(
                v["file"] for v in variants if "actual" in v.get("modifiers", []) and v.get("file")
            )
        entry.pop("sourceset", None)
        merged.append(entry)
    return merged


TYPE_RE = re.compile(
    r"(?m)^(?P<indent>[ \t]*)(?P<mods>(?:(?:public|private|internal|protected|expect|actual|open|"
    r"abstract|sealed|final|inner|annotation|data|value|enum|fun)[ \t]+)*)"
    r"(?P<kind>class|interface|object)[ \t]+(?P<name>[A-Za-z_]\w*)"
)


def _kind_of(mods: str, kw: str) -> str:
    if "enum" in mods:
        return "enum"
    if kw == "class" and "data" in mods:
        return "data class"
    if kw == "class" and "value" in mods:
        return "value class"
    if kw == "class" and "sealed" in mods:
        return "sealed class"
    return kw


def find_types(src: str, _depth: int = 0, _prefix: str = "") -> list[dict]:
    """Public classes, interfaces, objects and enums, with their constructor parameters.

    Needed because a constructor call is API too: ThemeController(...), DropdownItem(...),
    SwitchColors(...). Without this the reference cannot tell an agent that
    ThemeController takes no required arguments, or that every XxxColors constructor
    parameter is `private val` and therefore unreadable from the instance -- the
    misconception nine of the project's own doc pages are built on.
    """
    masked = mask(src)
    bd = _brace_depth_at(masked)
    out = []
    for m in TYPE_RE.finditer(masked):
        if bd[m.start()] != 0:
            continue
        if _visibility(m.group("mods")) != "public":
            continue
        if "companion" in src[max(0, m.start() - 20):m.start()]:
            continue
        after = m.end()
        # optional generic parameter list
        gm = re.match(r"[ \t]*<[^>]*>", masked[after:])
        if gm:
            after += gm.end()
        params = []
        pm = re.match(r"[ \t]*\(", masked[after:])
        if pm:
            open_idx = after + pm.end() - 1
            close_idx = match_bracket(masked, open_idx)
            if close_idx > 0:
                raw = src[open_idx + 1:close_idx]
                params = parse_params(raw)
                for p, chunk in zip(params, split_top_level(raw)):
                    p["private"] = bool(re.match(r"^\s*private\b", chunk))
                    p["property"] = bool(re.search(r"\b(val|var)\b", chunk.split(":")[0]))
                after = close_idx + 1
        brace = masked.find("{", after)
        nl = masked.find("\n", after)
        body, entries, nested, members = "", [], [], []
        if brace >= 0 and (nl < 0 or brace < masked.find("\n\n", after) or brace - after < 400):
            end = match_bracket(masked, brace)
            if end > 0:
                body = src[brace + 1:end]
        kind = _kind_of(m.group("mods"), m.group("kind"))
        if kind == "enum" and body:
            # masked: a KDoc above an entry (`/** Uses … */ Native("Default"),`) otherwise swallows
            # the entry name -- all three PagerInterceptionMode entries were lost that way
            head = mask(body).split(";")[0]
            for e in split_top_level(head):
                name = re.match(r"([A-Za-z_]\w*)", e.strip())
                if name:
                    entries.append(name.group(1))
        if body:
            cm = re.search(r"(?m)^[ \t]*companion[ \t]+object[^\n{]*\{", mask(body))
            if cm:
                cbody_start = cm.end() - 1
                cend = match_bracket(mask(body), cbody_start)
                if cend > 0:
                    members = find_functions(body[cbody_start + 1:cend])
            if _depth == 0:
                nested = find_types(body, _depth + 1, _prefix + m.group("name") + ".")
        out.append({
            "name": m.group("name"),
            "qualified": _prefix + m.group("name"),
            "kind": kind,
            "params": params,
            "entries": entries,
            "companion_functions": members,
            "doc": (kdoc_before(src, masked, m.start()) or {}).get("desc"),
            "line": src[:m.start()].count("\n") + 1,
        })
        out += nested
    return out


# --------------------------------------------------------------------------- driver
SKIP_DIRS = {"build", ".git", ".gradle"}
TEST_MARKERS = ("commonTest", "desktopTest", "androidTest", "iosTest", "jvmTest", "Test.kt")


def module_of(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.relative_to(root).parts[0]


def sourceset_of(path: pathlib.Path) -> str:
    parts = path.parts
    return parts[parts.index("src") + 1] if "src" in parts else "?"


def kotlin_files(root: pathlib.Path, subdirs: list[str]) -> list[pathlib.Path]:
    files = []
    for sub in subdirs:
        base = root / sub
        if not base.is_dir():
            continue
        for p in base.rglob("*.kt"):
            if SKIP_DIRS & set(p.parts):
                continue
            if any(t in str(p) for t in TEST_MARKERS):
                continue
            files.append(p)
    return sorted(files)


def library_version(root: pathlib.Path) -> str | None:
    cfg = root / "build-plugins/src/main/kotlin/BuildConfig.kt"
    if not cfg.is_file():
        return None
    m = re.search(r'LIBRARY_VERSION\s*=\s*"([^"]+)"', cfg.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def source_ref(root: pathlib.Path) -> str | None:
    """The git ref the data was extracted from: the release tag when the checkout sits on one.

    The references link every source location to GitHub at this ref. A tag keeps those links
    stable and readable; a bare commit hash still works when someone syncs from a branch.
    """
    import subprocess
    for args in (["describe", "--tags", "--exact-match"], ["rev-parse", "HEAD"]):
        try:
            out = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                                 text=True, check=True).stdout.strip()
            if out:
                return out
        except (OSError, subprocess.CalledProcessError):
            continue
    return None


def build_demo_index(root: pathlib.Path) -> dict[str, list[str]]:
    """component name -> example call sites, from code that is actually compiled.

    The audit found docs examples rot while `docs/demo` and `example/shared` do not
    (they are Gradle subprojects and break the build when they go stale), so the
    knowledge base points at those instead of shipping hand-written snippets.
    """
    index: dict[str, list[str]] = {}
    sources = []
    for sub in ("docs/demo/src", "example/shared/src"):
        base = root / sub
        if base.is_dir():
            sources += [p for p in base.rglob("*.kt") if SKIP_DIRS & set(p.parts) == set()]
    texts = [(p, p.read_text(encoding="utf-8", errors="replace")) for p in sorted(sources)]
    return {"__files__": [str(p.relative_to(root)) for p, _ in texts]}, texts


def attach_demos(components: list[dict], texts, root: pathlib.Path) -> None:
    for comp in components:
        hits = []
        pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(comp['name'])}\s*\(")
        for p, text in texts:
            m = pat.search(text)
            if m:
                hits.append(f"{p.relative_to(root)}:{text[:m.start()].count(chr(10)) + 1}")
        comp["examples"] = hits[:4]


def extract(root: pathlib.Path) -> dict:
    modules = sorted(p.name for p in root.glob("miuix-*") if p.is_dir())
    out = {
        "miuix_version": library_version(root),
        "source_ref": source_ref(root),
        "source_root": str(root),
        "modules": {},
    }
    _, demo_texts = build_demo_index(root)
    all_components = []
    for mod in modules:
        files = kotlin_files(root, [mod])
        comps, objs, consts, icons, types = [], [], [], [], []
        for f in files:
            src = f.read_text(encoding="utf-8", errors="replace")
            rel = str(f.relative_to(root))
            ss = sourceset_of(f)
            pkg = find_package(src)
            for fn in find_functions(src):
                fn["file"] = rel
                fn["sourceset"] = ss
                fn["module"] = mod
                fn["package"] = pkg
                comps.append(fn)
            for ic in find_icons(src):
                ic["file"] = rel
                # each icon is an extension property: `MiuixIcons.Back` needs `import <package>.Back`
                ic["package"] = pkg
                icons.append(ic)
            for t in find_types(src):
                t["file"] = rel
                t["package"] = pkg
                types.append(t)
            for o in find_objects(src):
                o["file"] = rel
                o["sourceset"] = ss
                o["package"] = pkg
                objs.append(o)
            for c in find_constants(src):
                if c["visibility"] in ("public", "internal"):
                    c["file"] = rel
                    consts.append(c)
        comps = merge_platform_variants(comps)
        out["modules"][mod] = {
            "files": len(files),
            "functions": comps,
            "icons": sorted(icons, key=lambda i: (i["namespace"] or "", i["name"])),
            "types": sorted(types, key=lambda t: t["qualified"]),
            "defaults_objects": [o for o in objs if o["name"].endswith("Defaults")],
            "other_objects": [o for o in objs if not o["name"].endswith("Defaults")],
            "constants": consts,
        }
        all_components += comps
    attach_demos(all_components, demo_texts, root)
    return out


def summarize(data: dict) -> str:
    lines = [f"miuix {data['miuix_version']}"]
    tot_c = tot_o = tot_k = 0
    for mod, m in data["modules"].items():
        comp = sum(1 for f in m["functions"] if f["composable"])
        fn = len(m["functions"]) - comp
        lines.append(f"  {mod:<18} {m['files']:>3} files  "
                     f"{comp:>3} @Composable  {fn:>3} fn  "
                     f"{len(m['defaults_objects']):>2} Defaults  {len(m['constants']):>3} const"
                     + f"  {len(m['types']):>3} types"
                     + (f"  {len(m['icons']):>4} icons" if m["icons"] else ""))
        tot_c += comp
        tot_o += len(m["defaults_objects"])
        tot_k += len(m["constants"])
    lines.append(f"  {'TOTAL':<18}      {tot_c:>3} @Composable  "
                 f"{'':>7}{tot_o:>2} Defaults  {tot_k:>3} const")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True, help="path to a miuix checkout")
    ap.add_argument("--out", default=str(pathlib.Path(__file__).parent.parent / "data/miuix-api.json"))
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed data is stale")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.src).resolve()
    if not (root / "settings.gradle.kts").is_file():
        print(f"error: {root} is not a miuix checkout (no settings.gradle.kts)", file=sys.stderr)
        return 2
    data = extract(root)
    data.pop("source_root", None)
    text = json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True) + "\n"

    out = pathlib.Path(args.out)
    if args.check:
        if not out.is_file():
            print(f"stale: {out} does not exist", file=sys.stderr)
            return 1
        if out.read_text(encoding="utf-8") != text:
            print(f"stale: {out} differs from a fresh extraction of {root}\n"
                  f"       run: {pathlib.Path(__file__).name} --src {root}", file=sys.stderr)
            return 1
        print(f"up to date ({out})")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out} ({len(text):,} bytes)")
    print(summarize(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
