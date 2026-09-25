# Theme

MiuixTheme, colors, fonts, dynamic color, easing, HoldDown interaction. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## InteractionSource.collectIsHeldDownAsState  ·  interface

Subscribes to HoldDownInteraction on an InteractionSource and returns a State of "whether it is in the hold-down state". hold-down means "kept in a pressed state because a menu/dropdown has popped up", not an ordinary press.

> Subscribes to this [MutableInteractionSource] and returns a [State] representing whether this
> component is selected or not.

```kotlin
import top.yukonga.miuix.kmp.interfaces.collectIsHeldDownAsState

@Composable
fun InteractionSource.collectIsHeldDownAsState(): State<Boolean>
```

**Traps**

- 🟡 The two Interactions HoldDown/Release are emitted only by the internal HoldDownObserver, which is driven by the holdDownState: Boolean parameter of Card / IconButton / BasicComponent. If you remember a MutableInteractionSource yourself and pass it to some other component, this State is always false -- unless you emit(HoldDownInteraction.HoldDown()) into the source yourself. The correct usage is to pass the same interactionSource to both the above components and this function, and control holdDownState yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/interfaces/HoldDownInteraction.kt:84`)
- 🟡 Internally it is LaunchedEffect(this), keyed on the InteractionSource instance. If what you pass in is a MutableInteractionSource newly created on every recomposition, the subscription keeps restarting and drops the current hold state. The source passed in must be remembered.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/interfaces/HoldDownInteraction.kt:53`)
- ⚪ The KDoc text is wrong -- one sentence mentions both selected and focused, two words that are both incorrect (most likely a leftover from copy-editing collectIsFocusedAsState). Do not understand its semantics from the KDoc.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/interfaces/HoldDownInteraction.kt:46`)

**State** Self-held state: internally it remembers a mutableStateOf(false) and a HoldDown list, using counting to support nested/overlapping holds. The caller only needs to ensure interactionSource is remembered. The returned State is definitely false on the first frame, as the subscription is established inside a LaunchedEffect.

**vs Material3** Corresponds to foundation's collectIsPressedAsState / collectIsHoveredAsState / collectIsFocusedAsState family, with the same usage. HoldDownInteraction itself is a Miuix-custom Interaction type, with no corresponding concept in foundation/material3.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/interfaces/HoldDownInteraction.kt:51`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/interfaces/HoldDownInteraction.kt#L51)</sub>

## darkColorScheme  ·  theme

Constructs Miuix's dark color table, with slots that map one-to-one to lightColorScheme, passed to MiuixTheme(colors=) or ThemeController(darkColors=).

```kotlin
import top.yukonga.miuix.kmp.theme.darkColorScheme

fun darkColorScheme(
    primary: Color = Color(0xFF277AF7),
    onPrimary: Color = Color.White,
    primaryVariant: Color = Color(0xFF0073DD),
    onPrimaryVariant: Color = Color(0xFF99C7F1),
    error: Color = Color(0xFFF12522),
    onError: Color = Color.White,
    errorContainer: Color = Color(0xFF2E0603),
    onErrorContainer: Color = Color(0xFFFFDAD6),
    disabledPrimary: Color = Color(0xFF253E64),
    disabledOnPrimary: Color = Color(0xFF677993),
    disabledPrimaryButton: Color = Color(0xFF253E64),
    disabledOnPrimaryButton: Color = Color(0xFF677893),
    disabledPrimarySlider: Color = Color(0xFF44587C),
    primaryContainer: Color = Color(0xFF338FE4),
    onPrimaryContainer: Color = Color.White,
    secondary: Color = Color(0xFF505050),
    onSecondary: Color = Color.White,
    secondaryVariant: Color = Color(0xFF434343),
    onSecondaryVariant: Color = Color(0xFFD9D9D9),
    disabledSecondary: Color = Color(0xFF3F3F3F),
    disabledOnSecondary: Color = Color(0xFF797979),
    disabledSecondaryVariant: Color = Color(0xFF404040),
    disabledOnSecondaryVariant: Color = Color(0xFF707170),
    secondaryContainer: Color = Color(0xFF434343),
    onSecondaryContainer: Color = Color(0xFF7C7C7C),
    secondaryContainerVariant: Color = Color(0xFF4F4F4F),
    onSecondaryContainerVariant: Color = Color(0xFF959595),
    tertiaryContainer: Color = Color(0xFF2B3B54),
    onTertiaryContainer: Color = Color(0xFF4788ff),
    tertiaryContainerVariant: Color = Color(0xFF505050),
    background: Color = Color(0xFF242424),
    onBackground: Color = Color(0xE6FFFFFF),
    onBackgroundVariant: Color = Color(0xFF787E96),
    surface: Color = Color.Black,
    onSurface: Color = Color(0xFFF2F2F2),
    surfaceVariant: Color = Color(0xFF242424),
    onSurfaceSecondary: Color = Color(0xCCFFFFFF),
    onSurfaceVariantSummary: Color = Color(0x80FFFFFF),
    onSurfaceVariantActions: Color = Color(0x66FFFFFF),
    disabledOnSurface: Color = Color(0xFF666666),
    surfaceContainer: Color = Color(0xFF242424),
    onSurfaceContainer: Color = Color(0xE6FFFFFF),
    onSurfaceContainerVariant: Color = Color(0xFF737373),
    surfaceContainerHigh: Color = Color(0xFF242424),
    onSurfaceContainerHigh: Color = Color(0xFF666666),
    surfaceContainerHighest: Color = Color(0xFF2D2D2D),
    onSurfaceContainerHighest: Color = Color(0xFFE9E9E9),
    outline: Color = Color(0xFF404040),
    dividerLine: Color = Color(0xFF393939),
    windowDimming: Color = Color.Black.copy(alpha = 0.6F),
    sliderKeyPoint: Color = Color(0x4D7A8AA6),
    sliderKeyPointForeground: Color = Color(0xFF5DAAFF),
    sliderBackground: Color = Color(0x26FFFFFF),
): Colors
```

**Traps**

- 🔴 MiuixTheme(colors = darkColorScheme()) directly is the easiest trap to fall into: that overload does not provide LocalContentColor, whose fallback value is Color.Black, so all text and icons on the dark background are black. Either switch to MiuixTheme(controller = ThemeController(...)), or supply LocalContentColor yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/ContentColor.kt:21`)
- ⚪ The dark scheme's primary is 0xFF277AF7, a value tuned independently from the light 0xFF3482FF; error/errorContainer etc. are the same. When customizing the theme you must give both schemes explicitly, not just override one.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/Colors.kt:452`)
- 🟡 Same as lightColorScheme: Colors has no equals, two calls yield unequal instances, so do not inline darkColorScheme() into a remember key.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/Colors.kt:68`)

**Spec** primary #277AF7 · error #F12522

**State** A pure factory function, stateless, same as lightColorScheme.

**vs Material3** Corresponds to material3's darkColorScheme(). Same slot differences as lightColorScheme; additionally, M3's dark scheme applies surface tonal elevation by default, while Miuix has no such mechanism and expresses hierarchy only through the three explicit slots surfaceContainer/High/Highest.

**Compilable examples** [`example/shared/src/commonMain/kotlin/ColorPage.kt:73`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L73)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/Colors.kt:451`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/Colors.kt#L451)</sub>

## defaultTextStyles  ·  theme

Constructs Miuix's 14 text-style slots, passed to MiuixTheme(textStyles=); Miuix's Text uses the main one by default.

```kotlin
import top.yukonga.miuix.kmp.theme.defaultTextStyles

fun defaultTextStyles(
    main: TextStyle = Main,
    paragraph: TextStyle = Paragraph,
    body1: TextStyle = Body1,
    body2: TextStyle = Body2,
    button: TextStyle = Button,
    footnote1: TextStyle = Footnote1,
    footnote2: TextStyle = Footnote2,
    headline1: TextStyle = Headline1,
    headline2: TextStyle = Headline2,
    subtitle: TextStyle = Subtitle,
    title1: TextStyle = Title1,
    title2: TextStyle = Title2,
    title3: TextStyle = Title3,
    title4: TextStyle = Title4,
): TextStyles
```

**Traps**

- 🟡 The 14 default styles set only fontSize (paragraph additionally sets lineHeight, subtitle additionally sets fontWeight) and contain no color at all. The doc's claim that "style color comes from onBackground" is wrong -- color is resolved in Text via the chain color parameter -> style.color -> LocalContentColor, unrelated to TextStyles.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/TextStyles.kt:146`)
- 🟡 None of the 14 styles set a fontFamily, and there is no global font entry point in the library. To change the global font you can only put fontFamily into all 14 slots, e.g. defaultTextStyles(main = ..., paragraph = ..., ...) passing them one by one.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/TextStyles.kt:114`)
- 🟡 All 14 properties of TextStyles are internal set, so after obtaining MiuixTheme.textStyles you cannot modify it in place (it does not compile). There is only one modification path: construct a new defaultTextStyles(...) and pass it to MiuixTheme.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/TextStyles.kt:52`)
- ⚪ The private default styles are all get() = TextStyle(...) computed properties, so every call to defaultTextStyles() creates 14 new TextStyle objects. Do not inline it frame-by-frame inside composition.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/TextStyles.kt:147`)
- ⚪ LocalTextStyles is read only by Miuix's own Text and does not affect BasicText or material3's Text. When mixing the two UI libraries, font sizes are not automatically unified.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/TextStyles.kt:250`)

**Spec** main 17.sp (the default style of Miuix Text) · paragraph 17.sp + lineHeight 1.2em (the only slot with a line height) · body1 16.sp · body2 14.sp · button 17.sp · footnote1 13.sp · footnote2 11.sp · headline1 17.sp · headline2 16.sp · subtitle 14.sp + FontWeight.Bold (the only slot with a font weight) · title1 32.sp · title2 24.sp · title3 20.sp · title4 18.sp

**State** A pure factory function. The returned TextStyles internally holds 14 MutableState (internal set), updated in place by MiuixTheme to keep instance identity stable. The caller does not need to remember it, as MiuixTheme already remembers it internally.

**vs Material3** Corresponds to material3's Typography. M3 has 15 display/headline/title/body/label slots each with fontWeight/lineHeight/letterSpacing fully specified; Miuix gives only fontSize, and the slot names (main/paragraph/footnote/subtitle) are a different set. material3's LocalTextStyle and Miuix's LocalTextStyles do not interoperate.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/TextStyles.kt:114`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/TextStyles.kt#L114)</sub>

## folmeSpring  ·  easing

Constructs a Compose SpringSpec from Folme-style two parameters (damping ratio + response time in seconds); all animations in the library go through it, so use it rather than spring() when you want your own animation to match the Miuix feel.

> Creates a [SpringSpec] from damping and response parameters.

```kotlin
import top.yukonga.miuix.kmp.anim.folmeSpring

fun <T> folmeSpring(
    damping: Float,  // required
    response: Float,  // required
    visibilityThreshold: T? = null,
): SpringSpec<T>
```

- `damping` — The damping ratio. 1.0 = critically damped (no overshoot),   < 1.0 = underdamped (oscillates), > 1.0 = overdamped.
- `response` — The response time in seconds. Smaller values = faster animation.
- `visibilityThreshold` — The magnitude below which the animation is considered settled and the   invisible settle tail is cut; null falls back to the framework default displacement threshold.

**Traps**

- 🟡 response is not stiffness. The conversion is stiffness = (2*PI/response)^2, and the smaller the response the faster. folmeSpring(damping = 1f, response = 0.4f) gives a stiffness of about 247, much softer than Compose spring()'s default 1500; putting a familiar stiffness value (e.g. 1500) directly into response gives a stiffness of about 1.75e-5, and the animation looks completely still.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/anim/MiuixEasing.kt:24`)
- 🟡 The generic T can only be inferred from visibilityThreshold or the expected type. A form like val spec = folmeSpring(1f, 0.3f) with no expected type does not compile (Not enough information to infer type variable T); you must write folmeSpring<Float>(1f, 0.3f). The library's TopAppBar is written this way.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/anim/MiuixEasing.kt:19`)
- ⚪ visibilityThreshold defaults to null, taking the framework's default displacement threshold, so the spring's exponential-decay long tail runs dozens of extra frames of recomposition. Only NavigationRail in the whole library passes 0.001f. It is worth passing an explicit threshold for high-frequency animations.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:595`)

**Spec** press-in damping 1.0 / response 0.2 · press-out damping 0.95 / response 0.35 · hover-in damping 1.0 / response 0.6 · hover-out damping 0.96 / response 0.2 · dialog-show-hide damping 0.9 / response 0.3 · bottom-sheet damping 0.9 / response 0.38

**State** A pure function returning an immutable SpringSpec. It can (and should) be placed in a top-level private val for reuse, as the library's MiuixIndication does, without needing remember.

**vs Material3** No counterpart -- it is just a parameter-conversion wrapper around androidx.compose.animation.core.spring(), turning (dampingRatio, stiffness) into (damping, response). Note that the hand-written SpringEngine/SpringMath in SpringUtils.kt is a separate path dedicated to overscroll, unrelated to folmeSpring, and its parameters do not match either.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/anim/MiuixEasing.kt:19`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/anim/MiuixEasing.kt#L19)</sub>

## lightColorScheme  ·  theme

Constructs Miuix's light color table (all color slots have Xiaomi-style defaults), passed to MiuixTheme(colors=) or ThemeController(lightColors=).

```kotlin
import top.yukonga.miuix.kmp.theme.lightColorScheme

fun lightColorScheme(
    primary: Color = Color(0xFF3482FF),
    onPrimary: Color = Color.White,
    primaryVariant: Color = Color(0xFF3482FF),
    onPrimaryVariant: Color = Color(0xFFAECDFF),
    error: Color = Color(0xFFE94634),
    onError: Color = Color(0xFFFFFFFF),
    errorContainer: Color = Color(0xFFFDF6F4),
    onErrorContainer: Color = Color(0xFF410002),
    disabledPrimary: Color = Color(0xFFC2D9FF),
    disabledOnPrimary: Color = Color(0xFFF3F8FF),
    disabledPrimaryButton: Color = Color(0xFFC2D9FF),
    disabledOnPrimaryButton: Color = Color(0xFFFFFFFF),
    disabledPrimarySlider: Color = Color(0xFFB8CFF5),
    primaryContainer: Color = Color(0xFF5D9BFF),
    onPrimaryContainer: Color = Color.White,
    secondary: Color = Color(0xFFE6E6E6),
    onSecondary: Color = Color.White,
    secondaryVariant: Color = Color(0xFFF0F0F0),
    onSecondaryVariant: Color = Color(0xFF303030),
    disabledSecondary: Color = Color(0xFFF0F0F0),
    disabledOnSecondary: Color = Color(0xFFFCFCFC),
    disabledSecondaryVariant: Color = Color(0xFFF2F2F2),
    disabledOnSecondaryVariant: Color = Color(0xFFB2B2B2),
    secondaryContainer: Color = Color(0xFFF0F0F0),
    onSecondaryContainer: Color = Color(0xFFA9A9A9),
    secondaryContainerVariant: Color = Color(0xFFF0F0F0),
    onSecondaryContainerVariant: Color = Color(0xFFA8A8A8),
    tertiaryContainer: Color = Color(0xFFEAF2FF),
    onTertiaryContainer: Color = Color(0xFF3482FF),
    tertiaryContainerVariant: Color = Color(0xFFEAF2FF),
    background: Color = Color.White,
    onBackground: Color = Color.Black,
    onBackgroundVariant: Color = Color(0xFF8C93B0),
    surface: Color = Color(0xFFF7F7F7),
    onSurface: Color = Color.Black,
    surfaceVariant: Color = Color.White,
    onSurfaceSecondary: Color = Color(0xCC000000),
    onSurfaceVariantSummary: Color = Color(0x99000000),
    onSurfaceVariantActions: Color = Color(0x66000000),
    disabledOnSurface: Color = Color(0xFFB2B2B2),
    surfaceContainer: Color = Color.White,
    onSurfaceContainer: Color = Color.Black,
    onSurfaceContainerVariant: Color = Color(0xFF959595),
    surfaceContainerHigh: Color = Color(0xFFE8E8E8),
    onSurfaceContainerHigh: Color = Color(0xFFA2A2A2),
    surfaceContainerHighest: Color = Color(0xFFE8E8E8),
    onSurfaceContainerHighest: Color = Color.Black,
    outline: Color = Color(0xFFD9D9D9),
    dividerLine: Color = Color(0xFFE0E0E0),
    windowDimming: Color = Color.Black.copy(alpha = 0.3F),
    sliderKeyPoint: Color = Color(0x4DA3B3CD),
    sliderKeyPointForeground: Color = Color(0xFF6EB5FF),
    sliderBackground: Color = Color(0x0F000000),
): Colors
```

**Traps**

- 🟡 Colors is a plain class, not a data class, and has no equals/hashCode/toString. Calling lightColorScheme() twice yields two instances that are never equal, so remember(lightColorScheme()) { ... } re-executes on every recomposition; to override individual colors you should call it once and remember the result, or use Colors.copy(...).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/Colors.kt:68`)
- 🟡 All disabledXxx slots are pre-flattened opaque solid colors (e.g. disabledPrimary = 0xFFC2D9FF), not foreground colors with alpha. After replacing background/surface, these disabled colors do not adapt along with them and need to be recomputed manually.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/Colors.kt:350`)
- ⚪ The light primary is 0xFF3482FF and the dark primary is 0xFF277AF7 -- the two schemes are not a lightness flip of the same hue value; every color slot was tuned independently. When doing brand recoloring you cannot just change one primary and expect the dark scheme to derive automatically.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/Colors.kt:342`)

**Spec** primary #3482FF (Xiaomi blue) · onPrimary Color.White · error #E94634

**State** A pure factory function, stateless. Each call creates a new Colors instance; do not inline it as a remember key inside composition.

**vs Material3** Corresponds to material3's lightColorScheme(). The slot system is different: Miuix names slots by control purpose (disabledPrimaryButton / disabledPrimarySlider / sliderKeyPoint / sliderBackground / windowDimming / dividerLine), while M3 uses role triples. Miuix has no tertiary (only the tertiaryContainer family), no inverseSurface/inversePrimary/scrim/surfaceTint, so the two cannot be mapped to each other directly.

**Compilable examples** [`example/shared/src/commonMain/kotlin/ColorPage.kt:72`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L72)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/Colors.kt:341`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/Colors.kt#L341)</sub>

## MiuixTheme  ·  theme

The theme root of the entire library, providing Colors / TextStyles / LocalIndication / LocalContentColor / LocalOverscrollFactory downward. Every Miuix component must be wrapped inside it.

> The Miuix theme that provides color and text styles for the Miuix components.
> This theme supports dynamic color schemes through the [ThemeController].

```kotlin
import top.yukonga.miuix.kmp.theme.MiuixTheme

@Composable
fun MiuixTheme(
    controller: ThemeController,  // required
    textStyles: TextStyles = MiuixTheme.textStyles,
    content: @Composable () -> Unit,  // required
)
```

- `controller` — The [ThemeController] that controls the current color scheme.
- `textStyles` — The text styles for the Miuix components.
- `content` — The content of the Miuix theme.

**Traps**

- 🔴 The two overloads are not equivalent. MiuixTheme(controller=) provides LocalContentColor (= colors.onBackground), while MiuixTheme(colors=)'s CompositionLocalProvider does not include it. And the default value of LocalContentColor is Color.Black, so the intuitive form MiuixTheme(colors = darkColorScheme()) draws all Text/Icon as black on a dark background. To use the colors overload you must add another layer yourself: CompositionLocalProvider(LocalContentColor provides colors.onBackground).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/MiuixTheme.kt:62`)
- 🟡 The same omission also affects LocalColorSchemeMode: the colors overload does not provide it, and its default value is null, so under the colors overload MiuixTheme.colorSchemeMode is always null and MiuixTheme.isDynamicColor is always false -- code that relies on this check to decide whether to take the dynamic-color branch silently takes the wrong branch.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/ThemeController.kt:266`)
- 🟡 Not wrapping in MiuixTheme still compiles, runs, and does not error: LocalColors is staticCompositionLocalOf { lightColorScheme() }. Forgetting to wrap the theme manifests as "the whole page is light in dark mode" rather than a crash or blank screen, making it hard to trace back to "forgot to wrap the theme".  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/Colors.kt:618`)
- 🔴 Both overloads unconditionally inject LocalOverscrollFactory = MiuixOverscrollFactory, meaning that under MiuixTheme all Compose scrollable components already have Miuix bounce built in. Adding Modifier.overScrollVertical() to a LazyColumn at this point stacks two independent offsets and springs, adding the displacements and consuming the velocity twice. Choose one: either rely on the theme alone, or pass overscrollEffect = null to the scrollable component and then use the modifier.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/MiuixTheme.kt:39`)
- 🔴 ThemeController is named controller, but all seven properties are val (the file only imports getValue, not setValue) and there is no way to modify it after construction. remember { ThemeController(mode) } freezes the theme mode permanently; switching light/dark requires rebuilding the ThemeController instance (e.g. remember(mode) { ThemeController(mode) }, or simply not remembering it).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/ThemeController.kt:226`)
- 🟡 MiuixTheme uses a keyless remember to create a permanently identity-stable Colors copy, then writes the latest values back into it in place on every recomposition. There are two consequences: MiuixTheme.colorScheme is a mutable object that quietly changes value in your hands and cannot be used as a snapshot cache; and remember(colors) { ... } keyed on Colors never re-executes because the reference never changes.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/MiuixTheme.kt:30`)

**State** It holds no business state itself. The theme state lives in ThemeController (immutable, switched by rebuilding the instance) or is held by the caller as Colors. MiuixTheme internally remembers an identity-stable copy of Colors/TextStyles and writes back slot-by-slot with updateColorsFrom/updateTextStylesFrom on every recomposition; because Color uses structuralEqualityPolicy, no recomposition is triggered when the value has not changed.

**vs Material3** Corresponds to androidx.compose.material3.MaterialTheme. Differences: MiuixTheme additionally provides LocalIndication (MiuixIndication) and LocalOverscrollFactory, which M3 does not touch; M3's MaterialTheme has only one overload and its ColorScheme is an @Immutable data holder, while Miuix's Colors is a mutable object and the two overloads have different capabilities; MiuixTheme does no tonal elevation and has no shapes slot.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/Demo.kt:31`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/Demo.kt#L31) · [`example/shared/src/commonMain/kotlin/ui/Theme.kt:43`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ui/Theme.kt#L43)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/MiuixTheme.kt:24`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/MiuixTheme.kt#L24)</sub>

## MiuixTheme  ·  theme

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> The Miuix theme that provides color and text styles for the Miuix components.
> This theme uses the provided [colors] and [textStyles].

```kotlin
import top.yukonga.miuix.kmp.theme.MiuixTheme

@Composable
fun MiuixTheme(
    colors: Colors = MiuixTheme.colorScheme,
    textStyles: TextStyles = MiuixTheme.textStyles,
    content: @Composable () -> Unit,  // required
)
```

- `colors` — The color scheme for the Miuix components.
- `textStyles` — The text styles for the Miuix components.
- `content` — The content of the Miuix theme.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/Demo.kt:31`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/Demo.kt#L31) · [`example/shared/src/commonMain/kotlin/ui/Theme.kt:43`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ui/Theme.kt#L43)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/MiuixTheme.kt:54`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/MiuixTheme.kt#L54)</sub>

## platformDynamicColors  ·  theme

An expect/actual function that returns the current platform's dynamic-color Colors. ThemeController calls it when in a Monet* mode and keyColor == null.

```kotlin
import top.yukonga.miuix.kmp.theme.platformDynamicColors

@Composable
expect fun platformDynamicColors(
    dark: Boolean,  // required
): Colors
```

Platform impls: androidMain, commonMain, skikoMain

**Traps**

- 🔴 The Android implementation has no remember anywhere. MiuixTheme calls controller.currentColors() on every recomposition, so under MonetSystem + keyColor == null (the Material You default usage recommended by the doc), every recomposition performs one Settings.Secure ContentResolver IPC, one JSONObject parse, and a full MaterialKolor scheme generation. The outer updateColorsFrom diffs the result so it does not blow up recomposition, but the computation is wasted, and MiuixTheme usually wraps the whole app. When calling it yourself, always wrap it in a remember.  (`miuix-ui/src/androidMain/kotlin/top/yukonga/miuix/kmp/theme/DynamicColors.android.kt:29`)
- 🔴 The actual on non-Android platforms (desktop / iOS / macOS / wasm / js) is only one line, monetSystemColors(dark), which uses the hard-coded seed color 0xFF6750A4 (the Material baseline purple) + TonalSpot + Spec2021 and reads no system colors at all. Android < 31 also falls to the same path. So "cross-platform dynamic color" is actually only truly dynamic on Android 31+.  (`miuix-ui/src/skikoMain/kotlin/top/yukonga/miuix/kmp/theme/DynamicColors.skiko.kt:9`)
- ⚪ The Android implementation has an unconditional Log.d (with string interpolation) left in production code, executed once per recomposition alongside the item above.  (`miuix-ui/src/androidMain/kotlin/top/yukonga/miuix/kmp/theme/DynamicColors.android.kt:30`)
- ⚪ In the fallback path that reads system_accent/system_neutral resources (which may be taken from SDK >= 31; on 33/34 it also falls here whenever theme_customization_overlay_packages cannot be read, and the path further branches internally on SDK >= 34), error / onError / errorContainer / onErrorContainer are hard-coded M3 baseline red (0xFFB3261E / 0xFFFFFFFF / 0xFFF9DEDC / 0xFF410E0B) and do not follow the wallpaper. Only when theme_customization_overlay_packages is read successfully and colorsFromSeed is taken (requiring Android 33+) are the error colors derived from the seed color.  (`miuix-ui/src/androidMain/kotlin/top/yukonga/miuix/kmp/theme/DynamicColors.android.kt:207`)
- ⚪ It is @Composable, and the Android implementation reads LocalContext, so it cannot be called outside composition (ViewModel, initialization code).  (`miuix-ui/src/androidMain/kotlin/top/yukonga/miuix/kmp/theme/DynamicColors.android.kt:27`)

**State** Stateless, re-reading the platform and recomputing on every call. The caller (ThemeController.currentColors) does not cache this branch either -- only the keyColor != null branch has a remember.

**vs Material3** Corresponds to androidx.compose.material3.dynamicLightColorScheme/dynamicDarkColorScheme. Differences: the official version is an ordinary function (Context parameter) and the caller decides when to remember; the Miuix version is @Composable with no internal caching. The official version exists only on Android 31+, while the Miuix version is a KMP expect/actual that degrades to a fixed seed color on other platforms rather than being unavailable at compile time.

**Compilable examples** [`example/shared/src/commonMain/kotlin/ColorPage.kt:74`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L74)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/DynamicColors.kt:9`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/DynamicColors.kt#L9)</sub>

## Top-level properties & CompositionLocals (3)

- `LocalContentColor = compositionLocalOf { … }`  <sub>[`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/ContentColor.kt:21`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/ContentColor.kt#L21)</sub>
- `LocalDismissState = staticCompositionLocalOf<(() -> Unit)?> { … }`  <sub>[`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/DismissState.kt:26`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/DismissState.kt#L26)</sub>
- `SinOutEasing: Easing`  <sub>[`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/anim/SinOutEasing.kt:10`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/anim/SinOutEasing.kt#L10)</sub>

## Public types in this topic (12)

- `AccelerateEasing(factor: Float)` **class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.anim.AccelerateEasing`
- `ColorSchemeMode` **enum** — System, Light, Dark, MonetSystem, MonetLight, MonetDark · `import top.yukonga.miuix.kmp.theme.ColorSchemeMode`
- `DecelerateEasing(factor: Float)` **class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.anim.DecelerateEasing`
- `ExperimentalScrollBarApi` **class** · `import top.yukonga.miuix.kmp.interfaces.ExperimentalScrollBarApi`
- `HoldDownInteraction` **interface** · `import top.yukonga.miuix.kmp.interfaces.HoldDownInteraction`
- `HoldDownInteraction.HoldDown` **class** · `import top.yukonga.miuix.kmp.interfaces.HoldDownInteraction`
- `HoldDownInteraction.Release(holdDown: HoldDown)` **class** (required: holdDown) · `import top.yukonga.miuix.kmp.interfaces.HoldDownInteraction`
- `MiuixTheme` **object** · `import top.yukonga.miuix.kmp.theme.MiuixTheme`
- `TextStyles(main: TextStyle, paragraph: TextStyle, body1: TextStyle, body2: TextStyle, button: TextStyle, footnote1: TextStyle, footnote2: TextStyle, headline1: TextStyle, …)` **class** (required: main, paragraph, body1, body2, button, footnote1, footnote2, headline1, headline2, subtitle, title1, title2, title3, title4) · `import top.yukonga.miuix.kmp.theme.TextStyles`
- `ThemeColorSpec` **enum** — Spec2021, Spec2025 · `import top.yukonga.miuix.kmp.theme.ThemeColorSpec`
- `ThemeController(colorSchemeMode: ColorSchemeMode, lightColors: Colors, darkColors: Colors, keyColor: Color?, colorSpec: ThemeColorSpec, paletteStyle: ThemePaletteStyle, isDark:…)` **class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.theme.ThemeController`
- `ThemePaletteStyle` **enum** — TonalSpot, Neutral, Vibrant, Expressive, Rainbow, FruitSalad, Monochrome, Fidelity, Content · `import top.yukonga.miuix.kmp.theme.ThemePaletteStyle`

