# miuix

[简体中文](README.md) | English

![License](https://img.shields.io/badge/license-MIT-blue)
![Miuix](https://img.shields.io/badge/Miuix-0.9.4-3482FF)
![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-8A2BE2)

Teach your Coding Agent to use [Miuix](https://github.com/compose-miuix-ui/miuix), the Compose Multiplatform UI library that recreates Xiaomi's HyperOS look

From an empty directory, one command generates a compiling Android / desktop / web project, and the UI code you write after compiles on the first try: every signature is extracted from the Miuix source, every trap carries `file:line` evidence

## What it does

- **Scaffold from an empty directory**: `scripts/new_app.py` generates a Kotlin Multiplatform (Android / desktop / web, any subset) or plain Android project, with a bundled Gradle wrapper; the sample `App.kt` already shows theming / a collapsing top bar / grouped preferences / navigation / a confirm dialog
- **Signatures extracted, not copied**: 183 `@Composable`s, 54 top-level functions, 37 `Defaults`, 177 public types, 943 icons, all generated from source, each linked to its line at `v0.9.4` on GitHub
- **Traps with evidence**: 174 entries / 696 traps (200 cause compile errors, crashes or clearly wrong behaviour), each citing the source line that proves it
- **Topic-split references**: 17 generated topic files plus hand-written recipes, loaded on demand instead of all at once

## Install

```bash
npx skills add yspbwx2010/skills --skill miuix
```

or the Claude Code plugin marketplace:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install miuix@yspbwx2010-skills
```

or copy `miuix/skills/miuix/` into your agent's skills directory (`~/.claude/skills/` for Claude Code)

## Versions

Targets Miuix **0.9.4** (the Maven Central release) · Kotlin 2.4.20 / Compose Multiplatform 1.12.0 · compileSdk 37 / minSdk 24 · JDK 21

It tracks the release, not `main`: a breaking change from `main` written into the reference would make the code fail to compile against the release

## Maintenance

Maintenance and upgrade procedures are in [CONTRIBUTING.md](CONTRIBUTING.md)

## License

[MIT](../LICENSE)
