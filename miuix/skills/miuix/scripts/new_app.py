#!/usr/bin/env python3
"""Generate a compiling Miuix project from assets/template (standard library only, Python 3.9+)."""
import argparse
import html
import re
import shutil
import stat
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template"
ALL_TARGETS = ("android", "desktop", "web")
# Java + Kotlin hard keywords: in a package name they are either illegal or need backticks.
RESERVED = set(
    "abstract assert boolean break byte case catch char class const continue default do double else enum "
    "extends final finally float for goto if implements import instanceof int interface long native new "
    "package private protected public return short static strictfp super switch synchronized this throw "
    "throws transient try void volatile while true false null "
    "as fun in is object typealias typeof val var when".split()
)
MARKER = re.compile(r"@(if:(\w+)|endif)\b")
# Only these text files are rendered; gradlew / gradlew.bat / jar are copied as-is (.bat keeps CRLF)
TEXT_SUFFIXES = {".kt", ".kts", ".toml", ".properties", ".xml", ".html", ".md", ".gitignore"}

EPILOG = """\
Layouts:
  kmp      composeApp (the KMP shared module, all UI) + androidApp (the APK shell). Pick any of targets android,desktop,web.
  android  a single app module (com.android.application, no KMP); only --targets android.

Examples:
  python3 scripts/new_app.py ~/work/notes --name "Notes" --package com.example.notes
  python3 scripts/new_app.py ./desk --name "Desk Tool" --package org.acme.desk --targets desktop
  python3 scripts/new_app.py ./phone --name "Phone" --package com.example.phone --layout android

The output needs JDK 21; with an android target it also needs Android SDK Platform 37 (ANDROID_HOME or local.properties).
"""


def fail(msg):
    sys.exit(f"new_app.py: error: {msg}")


def check_package(pkg):
    parts = pkg.split(".")
    if len(parts) < 2:
        fail(f"package {pkg!r} needs at least two segments (e.g. com.example.myapp), as an Android applicationId requires")
    for p in parts:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", p):
            fail(f"package {pkg!r} segment {p!r} is invalid: each segment must start with a letter and contain only letters, digits, underscores")
        if p in RESERVED:
            fail(f"package {pkg!r} segment {p!r} is a Java/Kotlin keyword")


def parse_args(argv):
    ap = argparse.ArgumentParser(
        prog="new_app.py",
        description="Generate a compiling Compose project on Miuix 0.9.4, then just edit the UI code.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("dest", help="target directory: must not exist or be empty (unless --force)")
    ap.add_argument("--name", required=True, help='app display name, e.g. "My App" (title bar, window title, web title, Android label)')
    ap.add_argument("--package", required=True, help="package / applicationId, e.g. com.example.myapp")
    ap.add_argument("--layout", choices=("kmp", "android"), default="kmp", help="project layout, default kmp")
    ap.add_argument(
        "--targets",
        help="comma-separated platforms: any combination of android,desktop,web. kmp defaults to all three; the android layout is android only",
    )
    ap.add_argument("--force", action="store_true", help="write even if the target dir is non-empty (overwrites same-named files, deletes nothing else)")
    a = ap.parse_args(argv)

    a.name = a.name.strip()
    if not a.name or any(ord(c) < 32 for c in a.name):
        fail("--name must not be empty or contain control characters such as newlines")
    check_package(a.package)

    raw = a.targets or ("android" if a.layout == "android" else ",".join(ALL_TARGETS))
    targets = [t.strip() for t in raw.split(",") if t.strip()]
    bad = [t for t in targets if t not in ALL_TARGETS]
    if bad or not targets:
        fail(f"--targets only accepts a combination of {','.join(ALL_TARGETS)}, got {raw!r}")
    if a.layout == "android" and targets != ["android"]:
        fail("--layout android only supports --targets android; use --layout kmp for desktop/web")
    a.targets = set(targets)
    return a


def escape(value, suffix):
    if suffix in (".kt", ".kts"):
        return value.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$")
    if suffix in (".xml", ".html"):
        return html.escape(value)
    return value


def render(text, suffix, flags, tokens):
    out, stack = [], []
    for n, line in enumerate(text.splitlines(keepends=True), 1):
        m = MARKER.search(line)
        if m:
            if m.group(2):
                stack.append(m.group(2) in flags)
            elif not stack:
                raise ValueError(f"line {n} has an unmatched @endif")
            else:
                stack.pop()
            continue
        if all(stack):
            out.append(line)
    if stack:
        raise ValueError("@if with no matching @endif")
    text = "".join(out)
    for k, v in tokens.items():
        text = text.replace("{{" + k + "}}", escape(v, suffix))
    return text


def generate(a):
    dest = Path(a.dest).expanduser().resolve()
    if dest.exists() and not dest.is_dir():
        fail(f"{dest} exists and is not a directory")
    if dest.exists() and any(dest.iterdir()) and not a.force:
        fail(f"{dest} is not an empty directory (use --force to overwrite same-named files)")

    kmp = a.layout == "kmp"
    android = "android" in a.targets
    ui_root = "composeApp/src/commonMain" if kmp else "app/src/main"
    droid_root = "androidApp/src/main" if kmp else "app/src/main"

    # (source in the template, target in the output, whether it is needed)
    plan = [
        ("common", ".", True),
        (a.layout, ".", True),
        ("shared-ui/App.kt", f"{ui_root}/kotlin/App.kt", True),
        ("android-entry/MainActivity.kt", f"{droid_root}/kotlin/MainActivity.kt", android),
        ("android-entry/AndroidManifest.xml", f"{droid_root}/AndroidManifest.xml", android),
    ]
    skip = set()
    if kmp:
        skip = {p for t, p in (("android", "androidApp"), ("desktop", "composeApp/src/jvmMain"),
                               ("web", "composeApp/src/wasmJsMain")) if t not in a.targets}

    files = []  # (source file, relative target path)
    for src, dst, need in plan:
        if not need:
            continue
        s = TEMPLATE / src
        if s.is_file():
            files.append((s, Path(dst)))
            continue
        for f in sorted(s.rglob("*")):
            rel = f.relative_to(s)
            if f.is_file() and not any(rel.as_posix() == p or rel.as_posix().startswith(p + "/") for p in skip):
                files.append((f, Path(dst) / rel))

    flags = set(a.targets) | {a.layout}
    project = re.sub(r"[^A-Za-z0-9]+", "", a.name) or a.package.rsplit(".", 1)[-1]
    tokens = {"PACKAGE": a.package, "APP_NAME": a.name, "PROJECT_NAME": project}
    pkg_dir = Path(*a.package.split("."))

    for src, rel in files:
        # files under the source root (…/kotlin/X.kt) move into subdirs by package name
        if rel.suffix == ".kt" and rel.parent.name == "kotlin":
            rel = rel.parent / pkg_dir / rel.name
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        suffix = src.suffix if src.suffix else src.name if src.name.startswith(".") else ""
        if suffix in TEXT_SUFFIXES:
            try:
                text = render(src.read_text(encoding="utf-8"), suffix, flags, tokens)
            except ValueError as e:
                fail(f"template {src.relative_to(TEMPLATE)}: {e}")
            out.write_text(text, encoding="utf-8")
            shutil.copymode(src, out)
        else:
            shutil.copy2(src, out)

    gw = dest / "gradlew"
    gw.chmod(gw.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return dest


def next_steps(a, dest):
    steps = []
    if a.layout == "android":
        steps.append("./gradlew :app:assembleDebug                      # APK: app/build/outputs/apk/debug/")
    else:
        if "desktop" in a.targets:
            steps.append("./gradlew :composeApp:run                         # desktop window")
        if "web" in a.targets:
            steps.append("./gradlew :composeApp:wasmJsBrowserDevelopmentRun # browser")
        if "android" in a.targets:
            steps.append("./gradlew :androidApp:assembleDebug               # APK")
    ui = "app/src/main" if a.layout == "android" else "composeApp/src/commonMain"
    lines = [f"Generated a {a.layout} project (targets: {','.join(t for t in ALL_TARGETS if t in a.targets)}): {dest}",
             f"UI code: {ui}/kotlin/{a.package.replace('.', '/')}/App.kt", "", "Next steps:", f"  cd {dest}"]
    lines += [f"  {s}" for s in steps]
    lines.append("Needs JDK 21" + ("; Android needs SDK Platform 37 (ANDROID_HOME or sdk.dir in local.properties)" if "android" in a.targets else ""))
    return "\n".join(lines)


def main(argv=None):
    a = parse_args(argv)
    dest = generate(a)
    print(next_steps(a, dest))


if __name__ == "__main__":
    main()
