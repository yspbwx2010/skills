# WebUI, Action, and Lua (APatch additions)

Verified against APatch 11224 (`apd/src/module.rs`, `app/.../ui/screen/APM.kt`, `ui/webui/`).

These are APatch/KernelSU-style extensions beyond the base Magisk module. All optional.

## WebUI — `webroot/`

If a module dir contains a `webroot/` directory, the APatch manager marks it `web=true` and shows
a **WebUI** entry that opens `webroot/index.html` in an in-app WebView (`WebUIActivity`), with a
JS bridge (`WebViewInterface`) exposing module/system calls to the page.

```
/data/adb/modules/<id>/
└── webroot/
    ├── index.html
    ├── app.js
    └── style.css
```

Use it for a settings/control page. The exact JS API surface tracks the manager version and the
KernelSU-derived WebView bridge; check the manager you target rather than assuming a fixed API.

## Action button — `action.sh` or `<id>.lua`

If the module dir has `action.sh` **or** `<id>.lua`, the manager shows an **Action** button.
Tapping it runs `action.sh` (preferred) in the APatch busybox ash environment; if there is no
`action.sh`, APatch runs the module's Lua `action` entry instead.

```sh
#!/system/bin/sh
# action.sh — MODDIR is this module's dir
MODDIR=${0%/*}
ui_print() { echo "$1"; }   # in Action context, plain echo is shown
# toggle a feature, clear a cache, etc.
```

Keep Action idempotent and quick — it runs on demand from the UI.

## Lua stage scripts — `<id>.lua`

`apd` runs a module's `<id>.lua` for each boot stage (`post-fs-data`, `post-mount`, `service`,
`boot-completed`) via `exec_stage_lua`, and for the Action button, in addition to the shell stage
scripts. Optional. Prefer shell scripts for portability with Magisk/KernelSU; reach for Lua only
when the module specifically wants it.

## Portability note

`webroot/`, `action.sh` and Lua all exist in the KernelSU lineage too, but the JS bridge and Lua
runtime differ per manager. A module relying on them is APatch/KernelSU-specific and will not do
anything under Magisk. The portable core of an APM (module.prop, `system/` overlay, the four boot
scripts, `system.prop`, `sepolicy.rule`) works the same across Magisk, KernelSU and APatch.
