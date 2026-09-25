#!/usr/bin/env python3
"""Runnable check for sync.py's Kotlin signature parser.

Run: python3 scripts/test_sync.py
Every fixture below is a shape that actually occurs in the miuix sources;
if the parser regresses on one, the extracted knowledge base silently loses
or mangles parameters, which is exactly the failure mode this whole skill
exists to prevent.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from sync import (split_top_level, parse_params, find_functions, find_objects,
                  find_constants, find_icons, merge_platform_variants, find_types)


def test_split_top_level():
    # plain
    assert split_top_level("a, b, c") == ["a", "b", "c"]
    # nested generics: the comma inside Map<> must not split
    assert split_top_level("a: Map<String, Int>, b: Int") == ["a: Map<String, Int>", "b: Int"]
    # lambda type with two params
    assert split_top_level("f: (Boolean, Int) -> Unit, g: Int") == ["f: (Boolean, Int) -> Unit", "g: Int"]
    # the arrow's '>' must not be read as closing an angle bracket
    assert split_top_level("f: () -> Unit, g: Int") == ["f: () -> Unit", "g: Int"]
    # default value containing a call with its own args
    assert split_top_level("a: W = W.a.union(W.b), c: Int = 1") == ["a: W = W.a.union(W.b)", "c: Int = 1"]
    # default value that is a lambda
    assert split_top_level("h: @Composable () -> Unit = { Host() }, i: Int") == \
        ["h: @Composable () -> Unit = { Host() }", "i: Int"]
    # trailing comma yields no empty entry
    assert split_top_level("a: Int, b: Int,") == ["a: Int", "b: Int"]
    # string literal containing a comma or bracket must not affect depth
    assert split_top_level('a: String = "x, y", b: Int') == ['a: String = "x, y"', "b: Int"]
    print("  split_top_level ok")


def test_parse_params():
    p = parse_params("checked: Boolean, onCheckedChange: ((Boolean) -> Unit)?, modifier: Modifier = Modifier")
    assert [x["name"] for x in p] == ["checked", "onCheckedChange", "modifier"], p
    assert p[0]["type"] == "Boolean"
    # nullable-but-no-default is REQUIRED — the exact confusion the audit found in 6 doc pages
    assert p[1]["type"] == "((Boolean) -> Unit)?"
    assert p[1]["default"] is None
    assert p[1]["required"] is True
    assert p[2]["default"] == "Modifier"
    assert p[2]["required"] is False
    # a nullable param WITH an explicit null default is optional
    q = parse_params("onSelectedIndexChange: ((Int) -> Unit)? = null")
    assert q[0]["default"] == "null" and q[0]["required"] is False
    # vararg / modifiers on the parameter
    r = parse_params("vararg items: String, block: () -> Unit")
    assert r[0]["name"] == "items" and r[0]["type"] == "String", r
    print("  parse_params ok")


KT = '''
package top.yukonga.miuix.kmp.basic

/**
 * A [Switch] component with Miuix style.
 *
 * @param checked The checked state of the [Switch].
 * @param onCheckedChange The callback when the state changes.
 * @param modifier The modifier to be applied.
 */
@Composable
fun Switch(
    checked: Boolean,
    onCheckedChange: ((Boolean) -> Unit)?,
    modifier: Modifier = Modifier,
    colors: SwitchColors = SwitchDefaults.switchColors(),
    enabled: Boolean = true,
) {
    body()
}

@Composable
private fun SwitchImpl(a: Int) {}

@Composable
internal fun SwitchInternal(a: Int) {}

@Composable
fun Scaffold(
    modifier: Modifier = Modifier,
    popupHost: @Composable () -> Unit = { MiuixPopupHost() },
    contentWindowInsets: WindowInsets = WindowInsets.systemBars.union(WindowInsets.displayCutout),
    content: @Composable (PaddingValues) -> Unit,
) {}

fun BackdropEffectScope.blur(radiusX: Float, radiusY: Float = radiusX) {}

object SwitchDefaults {
    val CornerRadius = 32.dp
    private val Hidden = 1.dp

    @Composable
    fun switchColors(
        checkedTrackColor: Color = MiuixTheme.colorScheme.primary,
        uncheckedTrackColor: Color = MiuixTheme.colorScheme.surface,
    ): SwitchColors = SwitchColors(checkedTrackColor, uncheckedTrackColor)
}

internal const val SQUIRCLE_CONTROL = 0.643f
'''


def test_find_functions():
    fns = find_functions(KT)
    names = [f["name"] for f in fns]
    # private and internal must be excluded from the public surface
    assert "SwitchImpl" not in names, names
    assert "SwitchInternal" not in names, names
    assert "Switch" in names and "Scaffold" in names, names

    sw = next(f for f in fns if f["name"] == "Switch")
    assert sw["composable"] is True
    assert [p["name"] for p in sw["params"]] == \
        ["checked", "onCheckedChange", "modifier", "colors", "enabled"], sw["params"]
    # KDoc @param descriptions attach to the right parameters
    assert sw["params"][0]["doc"] == "The checked state of the [Switch]."
    assert sw["doc"].startswith("A [Switch] component with Miuix style.")
    # required set: the two with no default
    assert [p["name"] for p in sw["params"] if p["required"]] == ["checked", "onCheckedChange"]

    sc = next(f for f in fns if f["name"] == "Scaffold")
    assert [p["name"] for p in sc["params"]] == \
        ["modifier", "popupHost", "contentWindowInsets", "content"], sc["params"]
    assert sc["params"][1]["default"] == "{ MiuixPopupHost() }"
    assert sc["params"][2]["default"] == "WindowInsets.systemBars.union(WindowInsets.displayCutout)"
    assert sc["params"][3]["required"] is True

    # extension receiver captured, not folded into the name
    bl = next(f for f in fns if f["name"] == "blur")
    assert bl["receiver"] == "BackdropEffectScope", bl
    assert bl["composable"] is False

    # type parameters and modifiers survive -- a signature without them is a different function
    gen = {f["name"]: f for f in find_functions(
        "@Composable\npublic inline fun <reified T : NavKey> rememberNavBackStack(vararg elements: T): NavBackStack = x\n"
        "suspend fun PagerState.springAnimateToPage(target: Int) {}\n"
        "fun <T : Comparable<T>> clampAll(xs: List<T>): List<T> = xs\n")}
    assert gen["rememberNavBackStack"]["type_params"] == "<reified T : NavKey>", gen["rememberNavBackStack"]
    assert "inline" in gen["rememberNavBackStack"]["modifiers"]
    assert gen["springAnimateToPage"]["type_params"] is None
    assert "suspend" in gen["springAnimateToPage"]["modifiers"]
    assert gen["clampAll"]["type_params"] == "<T : Comparable<T>>", gen["clampAll"]
    print("  find_functions ok")


def test_find_objects():
    objs = find_objects(KT)
    o = next(o for o in objs if o["name"] == "SwitchDefaults")
    assert [f["name"] for f in o["functions"]] == ["switchColors"], o["functions"]
    # the factory's parameters are what users actually pass — 7 doc pages omit these
    assert [p["name"] for p in o["functions"][0]["params"]] == \
        ["checkedTrackColor", "uncheckedTrackColor"]
    # public constants exposed, private ones hidden
    assert [c["name"] for c in o["constants"]] == ["CornerRadius"], o["constants"]
    assert o["constants"][0]["value"] == "32.dp"
    print("  find_objects ok")


def test_find_constants():
    cs = find_constants(KT)
    names = {c["name"]: c for c in cs}
    assert "SQUIRCLE_CONTROL" in names
    assert names["SQUIRCLE_CONTROL"]["value"] == "0.643f"
    assert names["SQUIRCLE_CONTROL"]["visibility"] == "internal"
    # initializer on the line after `=` (how every CompositionLocal with a long type is written)
    wrapped = find_constants(
        "public val LocalNavTransitionScope: ProvidableCompositionLocal<NavTransitionScope> =\n"
        "    staticCompositionLocalOf { error(\"none\") }\n"
        "val Plain: Int\n    get() = 1\n"
    )
    w = {c["name"]: c for c in wrapped}
    assert "LocalNavTransitionScope" in w, wrapped
    assert w["LocalNavTransitionScope"]["type"] == "ProvidableCompositionLocal<NavTransitionScope>"
    assert w["LocalNavTransitionScope"]["value"].startswith("staticCompositionLocalOf"), w
    assert w["LocalNavTransitionScope"]["visibility"] == "public"
    assert "Plain" not in w, "a getter is not an initializer"
    assert w["LocalNavTransitionScope"]["top_level"] is True
    ctor = {c["name"]: c for c in find_constants("data class Style(\n    val color: Int = 0,\n)\n")}
    assert ctor["color"]["top_level"] is False, "a primary constructor property is not a top-level val"
    print("  find_constants ok")


ICONS_KT = '''
package top.yukonga.miuix.kmp.icon.extended

val MiuixIcons.Add: ImageVector
    get() = MiuixIcons.Regular.Add

val MiuixIcons.Light.Add: ImageVector
    get() { return build() }

val MiuixIcons.Basic.Search: ImageVector
    get() = built

private val _addLight: ImageVector? = null
val NotAnIcon: String = "x"
'''


def test_find_icons():
    icons = find_icons(ICONS_KT)
    got = {(i["namespace"], i["name"]) for i in icons}
    assert got == {(None, "Add"), ("Light", "Add"), ("Basic", "Search")}, got
    # backing fields and non-ImageVector vals are not icons
    assert not any(i["name"].startswith("_") for i in icons)
    assert not any(i["name"] == "NotAnIcon" for i in icons)
    print("  find_icons ok")


PLATFORM_FNS = [
    {"name": "getRoundedCorner", "receiver": None, "sourceset": "commonMain",
     "file": "a/Utils.kt", "params": [{"name": "d", "type": "Density"}],
     "modifiers": ["expect"], "doc": "Reads the system corner radius.", "composable": True},
    {"name": "getRoundedCorner", "receiver": None, "sourceset": "androidMain",
     "file": "a/Utils.android.kt", "params": [{"name": "d", "type": "Density"}],
     "modifiers": ["actual"], "doc": None, "composable": True},
    {"name": "getRoundedCorner", "receiver": None, "sourceset": "skikoMain",
     "file": "a/Utils.skiko.kt", "params": [{"name": "d", "type": "Density"}],
     "modifiers": ["actual"], "doc": None, "composable": True},
    {"name": "Switch", "receiver": None, "sourceset": "commonMain",
     "file": "b/Switch.kt", "params": [{"name": "checked", "type": "Boolean"}],
     "modifiers": [], "doc": None, "composable": True},
]


def test_merge_platform_variants():
    merged = merge_platform_variants(PLATFORM_FNS)
    assert len(merged) == 2, [m["name"] for m in merged]
    g = next(m for m in merged if m["name"] == "getRoundedCorner")
    # the expect declaration is the API contract, so its KDoc survives the merge
    assert g["doc"] == "Reads the system corner radius."
    assert g["file"] == "a/Utils.kt"
    assert sorted(g["platforms"]) == ["androidMain", "commonMain", "skikoMain"]
    assert g["expect_actual"] is True
    s2 = next(m for m in merged if m["name"] == "Switch")
    assert s2["expect_actual"] is False and s2["platforms"] == ["commonMain"]
    print("  merge_platform_variants ok")


GOTCHAS_YAML = '''
# basic input controls
Switch:
  summary: "the two-state switch in a settings row"
  gotchas:
    - text: "onCheckedChange is nullable but has no default: Switch(checked = x) alone fails to compile"
      severity: high
      evidence: miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Switch.kt:68
    - text: "the size is fixed at 49x28.dp, and it comes after modifier"
      severity: medium
      evidence: miuix-ui/.../Switch.kt:140
  visual:
    size: "49x28.dp (fixed)"
    corner: full
  state: "purely controlled"
  m3: "maps to material3.Switch, but no ripple"

Divider:
  summary: "divider"
  gotchas: []
  state: "stateless"
  m3: "maps to HorizontalDivider"

Card:
  summary: "card container"
  gotchas:
    - text: "shadowElevation is only a boolean switch"
      severity: medium
      evidence: Card.kt:52
  notes: |
    line one
    line two
'''


def test_load_yaml():
    from render import load_yaml
    d = load_yaml(GOTCHAS_YAML)
    assert set(d) == {"Switch", "Divider", "Card"}, list(d)
    sw = d["Switch"]
    assert sw["summary"] == "the two-state switch in a settings row"
    assert len(sw["gotchas"]) == 2, sw["gotchas"]
    # a colon inside the quoted text must not split the mapping
    assert sw["gotchas"][0]["severity"] == "high"
    # 'path:line' as an unquoted scalar keeps its colon
    assert sw["gotchas"][0]["evidence"].endswith("Switch.kt:68"), sw["gotchas"][0]["evidence"]
    assert sw["visual"]["size"] == "49x28.dp (fixed)"
    assert sw["visual"]["corner"] == "full"
    # empty inline list, not None
    assert d["Divider"]["gotchas"] == []
    # block scalar keeps its line breaks
    assert d["Card"]["notes"].splitlines() == ["line one", "line two"]
    # '#' inside a quoted scalar is not a comment
    assert load_yaml('a:\n  b: "x # y"\n')["a"]["b"] == "x # y"
    # double-quoted escapes decode as in YAML, whatever else is installed
    assert load_yaml('a: "\\\\\\\\"\n')["a"] == "\\\\"
    assert load_yaml('a: "\\\\n \\" \\n"\n')["a"] == '\\n " \n'
    # an escaped backslash before the closing quote still closes it
    assert load_yaml('a: "x\\\\" # c\n')["a"] == "x\\"
    print("  load_yaml ok")


def test_render_signature():
    from render import format_signature
    fn = {
        "name": "Switch", "receiver": None, "composable": True,
        "package": "top.yukonga.miuix.kmp.basic",
        "params": [
            {"name": "checked", "type": "Boolean", "default": None, "required": True},
            {"name": "onCheckedChange", "type": "((Boolean) -> Unit)?", "default": None, "required": True},
            {"name": "modifier", "type": "Modifier", "default": "Modifier", "required": False},
        ],
        "returns": None,
    }
    sig = format_signature(fn)
    assert "@Composable" in sig
    assert "fun Switch(" in sig
    assert "checked: Boolean," in sig
    assert "modifier: Modifier = Modifier," in sig
    # required params must be visibly marked -- the single most common miuix mistake
    assert sig.count("// required") == 2, sig
    # suspend / inline and type parameters are part of how you call it
    gen = format_signature({"name": "rememberNavBackStack", "receiver": None, "composable": True,
                            "modifiers": ["public", "inline"], "type_params": "<reified T : NavKey>",
                            "params": [{"name": "elements", "type": "T", "default": None,
                                        "required": True, "modifiers": ["vararg"]}],
                            "returns": "NavBackStack"})
    assert "inline fun <reified T : NavKey> rememberNavBackStack(" in gen, gen
    assert "public" not in gen, gen
    sus = format_signature({"name": "springAnimateToPage", "receiver": "PagerState",
                            "modifiers": ["suspend"], "params": [], "returns": None})
    assert sus == "suspend fun PagerState.springAnimateToPage()", sus
    print("  format_signature ok")


TYPES_KT = '''
@Stable
class ThemeController(
    colorSchemeMode: ColorSchemeMode = ColorSchemeMode.System,
    lightColors: Colors = lightColorScheme(),
    isDark: Boolean? = null,
) {
    val colorSchemeMode: ColorSchemeMode by mutableStateOf(colorSchemeMode)
}

@Stable
enum class ColorSchemeMode {
    System,
    Light,
    MonetSystem,
}

data class NavDisplayEffects(
    val scrim: Boolean = true,
)

@Immutable
class SwitchColors(
    private val checkedThumbColor: Color,
    private val uncheckedThumbColor: Color,
) {
    @Composable
    internal fun thumbColor(checked: Boolean): Color = checkedThumbColor
}

internal class Hidden(val a: Int)

interface PopupPositionProvider {
    enum class Align { Start, End, TopStart }
}
'''


def test_find_types():
    types = find_types(TYPES_KT)
    by = {t["name"]: t for t in types}
    assert "Hidden" not in by, "an internal type must not appear in the public API surface"
    assert set(by) >= {"ThemeController", "ColorSchemeMode", "NavDisplayEffects",
                       "SwitchColors", "PopupPositionProvider"}, sorted(by)

    tc = by["ThemeController"]
    assert tc["kind"] == "class"
    # 构造参数全有默认值 => 可以零参构造，这正是 skill 骨架依赖的事实
    assert [p["name"] for p in tc["params"]] == ["colorSchemeMode", "lightColors", "isDark"]
    assert all(not p["required"] for p in tc["params"])

    cm = by["ColorSchemeMode"]
    assert cm["kind"] == "enum"
    assert cm["entries"] == ["System", "Light", "MonetSystem"], cm["entries"]

    # XxxColors 的构造参数是 private val —— 审计里 9 个文档页把它们当可读属性列出
    sc = by["SwitchColors"]
    assert sc["params"][0]["private"] is True, sc["params"][0]

    assert by["NavDisplayEffects"]["kind"] == "data class"

    # entries with KDoc between them, and a `;` inside a comment (PagerInterceptionMode in 0.9.4)
    documented = {t["name"]: t for t in find_types(
        "enum class Mode(val title: String) {\n"
        "    /** Uses native gestures; the default. */\n    Native(\"Default\"),\n\n"
        "    /**\n     * Lets swipes interrupt.\n     */\n    CrossAxis(\"Cross-Axis\"),\n}\n")}
    assert documented["Mode"]["entries"] == ["Native", "CrossAxis"], documented["Mode"]["entries"]
    print("  find_types ok")


def test_gotcha_lookup():
    """Extension functions are keyed by their qualified name in the hand layer.

    Writing `Modifier.pressable:` in the YAML is the natural and correct way to name
    an extension, but the renderer walks functions whose `name` is the bare
    `pressable`. Matching on the bare name alone silently dropped 21 of 160
    hand-written entries -- they rendered nowhere and were reported as orphans.
    """
    from render import gotcha_for
    gotchas = {"Modifier.pressable": {"summary": "扩展"}, "Switch": {"summary": "组件"}}
    ext = {"name": "pressable", "receiver": "Modifier"}
    plain = {"name": "Switch", "receiver": None}
    missing = {"name": "Nope", "receiver": None}
    assert gotcha_for(gotchas, ext) == ("Modifier.pressable", {"summary": "扩展"})
    assert gotcha_for(gotchas, plain) == ("Switch", {"summary": "组件"})
    assert gotcha_for(gotchas, missing) == (None, {})
    # a bare-name entry still matches an extension when no qualified key exists
    assert gotcha_for({"pressable": {"x": 1}}, ext)[0] == "pressable"
    print("  gotcha_lookup ok")


if __name__ == "__main__":
    for fn in [test_split_top_level, test_parse_params, test_find_functions,
               test_find_objects, test_find_constants, test_find_icons,
               test_merge_platform_variants, test_find_types,
               test_load_yaml, test_render_signature, test_gotcha_lookup]:
        fn()
    print("all checks passed")
