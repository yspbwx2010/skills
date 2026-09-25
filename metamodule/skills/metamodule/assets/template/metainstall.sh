#!/system/bin/sh
# SOURCED (not executed) during a regular module's install, like customize.sh.
# Inherits installer vars (MODPATH, ZIPFILE, ARCH, API, KSU_VER, ...) and functions
# (ui_print, abort, set_perm, set_perm_recursive, install_module).
# NOT run when installing this metamodule itself.

install_module          # run the built-in install; move files into your own store afterward if needed
