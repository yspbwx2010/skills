# Navigation

NavigationBar / NavigationRail / TabRow / BreadcrumbBar / FloatingToolbar / FAB / SearchBar. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## BreadcrumbBar  ·  basic component

A file-manager-style path breadcrumb — capsule segments + arrow separators; on overflow it scrolls horizontally rather than collapsing into an ellipsis, and automatically scrolls the highlighted segment to center.

> A horizontal breadcrumb navigation bar with Miuix style. Displays a trail of path segments as
> capsule-shaped items separated by arrow icons. When the content overflows the available width, it
> scrolls horizontally instead of collapsing — matching the file-manager convention on mobile
> devices.
> 
> The [highlightIndex] is decoupled from the [items] list: the caller may show the full path while
> highlighting any segment (e.g. the current directory or a parent the user navigated back to).

```kotlin
import top.yukonga.miuix.kmp.basic.BreadcrumbBar

@Composable
fun BreadcrumbBar(
    items: List<BreadcrumbItem>,  // required
    onItemClick: (Int) -> Unit,  // required
    modifier: Modifier = Modifier,
    highlightIndex: Int = items.lastIndex,
    enabled: Boolean = true,
    colors: BreadcrumbBarColors = BreadcrumbBarDefaults.breadcrumbBarColors(),
    insideMargin: PaddingValues = BreadcrumbBarDefaults.InsideMargin,
    itemMaxWidth: Dp = BreadcrumbBarDefaults.ItemMaxWidth,
    scrollState: ScrollState? = null,
    interactionSource: MutableInteractionSource? = null,
    indication: Indication? = LocalIndication.current,
)
```

- `items` — The list of [BreadcrumbItem]s to display.
- `onItemClick` — Callback invoked with the index of the clicked item.
- `modifier` — The modifier to be applied to the [BreadcrumbBar].
- `highlightIndex` — The index of the highlighted item. Defaults to the last item.   Pass a negative value (e.g. `-1`) to disable highlighting and auto-scroll entirely.
- `enabled` — Whether the items are clickable. When disabled, items use the disabled color   scheme but horizontal scrolling remains active.
- `colors` — The [BreadcrumbBarColors] of the [BreadcrumbBar].
- `insideMargin` — The margin inside the [BreadcrumbBar].
- `itemMaxWidth` — The maximum width of each capsule-shaped item. Text beyond this is truncated.
- `scrollState` — The [ScrollState] to be used for horizontal scrolling. If null, an internal   state is created. Pass an externally hoisted state to preserve scroll position across recompositions.
- `interactionSource` — The [MutableInteractionSource] to be used for the items.
- `indication` — The [Indication] to be used for click interactions.

**BreadcrumbBarDefaults**


```kotlin
BreadcrumbBarDefaults.breadcrumbBarColors(
    color: Color = MiuixTheme.colorScheme.onBackground.copy(alpha = 0.55f),
    highlightColor: Color = MiuixTheme.colorScheme.primary,
    disabledColor: Color = MiuixTheme.colorScheme.disabledOnSecondaryVariant,
    separatorColor: Color = MiuixTheme.colorScheme.onSurfaceVariantActions,
    backgroundColor: Color = MiuixTheme.colorScheme.onBackground.copy(alpha = 0.1f),
    highlightBackgroundColor: Color = MiuixTheme.colorScheme.primary.copy(alpha = 0.2f),
    disabledBackgroundColor: Color = MiuixTheme.colorScheme.disabledSecondaryVariant,
)
```

- `InsideMargin = PaddingValues(horizontal = 12.dp, vertical = 8.dp)`
- `ItemHeight = 32.dp`
- `ItemHorizontalPadding = 10.dp`
- `ItemMaxWidth = 160.dp`

**BreadcrumbBarColors** (data class) 

**Traps**

- 🟡 highlightIndex defaults to items.lastIndex; passing a negative value (e.g. -1) turns off both the highlight and the auto-scroll. It is decoupled from items — you can show the full path while highlighting any segment (e.g. the parent directory the user backed into).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/BreadcrumbBar.kt:95`)
- 🟡 The auto-scroll coordinate reconstructs content coordinates with `positionInRoot().x + scrollState.value`, which implicitly assumes "the BreadcrumbBar's own left edge is the window's left edge." Placing it in a Row with left padding, or to the right of a NavigationRail, will shift the highlighted segment's centered position overall.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/BreadcrumbBar.kt:206`)
- ⚪ When enabled = false the arrow separators also switch to disabledColor rather than separatorColor, i.e. the description of separatorColor only holds in the enabled state; but horizontal scrolling still works in the disabled state.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/BreadcrumbBar.kt:147`)
- ⚪ BreadcrumbItem's text is optional and falls back to path when null. To display "My Phone" while the path is /storage/emulated/0, you rely on separating these two fields.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/BreadcrumbBar.kt:151`)
- ⚪ insideMargin is added inside horizontalScroll (`modifier.horizontalScroll(...).padding(insideMargin)`), so this inner padding scrolls away with the content rather than staying fixed at the container's edge.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/BreadcrumbBar.kt:141`)

**Spec** item_height 32.dp (capsule, CircleShape) · item_horizontal_padding 10.dp (equal to the corner radius, making the two ends full semicircles) · item_max_width 160.dp (overflow is Ellipsis-truncated) · inside_margin PaddingValues(horizontal = 12.dp, vertical = 8.dp) · separator a 10×16.dp arrow icon, 4.dp on each side; mirrored with scaleX = -1 under RTL · colors the background color is derived from the text color (onBackground alpha 0.1, primary alpha 0.2), auto-adapting to light/dark themes

**State** Purely controlled (items + onItemClick + highlightIndex). scrollState can be passed in to preserve the scroll position; if not passed it is rememberScrollState internally. The first positioning uses scrollTo for an instant jump, subsequent highlightIndex changes use animateScrollTo.

**vs Material3** No counterpart. Material3 has no breadcrumb component; the biggest difference from a Web breadcrumb is that on overflow it scrolls horizontally rather than collapsing into `...`.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt:61`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt#L61) · [`example/shared/src/commonMain/kotlin/component/BreadcrumbBarSection.kt:43`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BreadcrumbBarSection.kt#L43)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/BreadcrumbBar.kt:91`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/BreadcrumbBar.kt#L91)</sub>

## FloatingActionButton  ·  basic component

A floating action button, 60×60 true circle (built on Surface + CircleShape, not squircle), with a 4.dp shadow.

> A [FloatingActionButton] component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.FloatingActionButton

@Composable
fun FloatingActionButton(
    onClick: () -> Unit,  // required
    modifier: Modifier = Modifier,
    shape: Shape = CircleShape,
    containerColor: Color = MiuixTheme.colorScheme.primary,
    shadowElevation: Dp = FloatingActionButtonDefaults.ShadowElevation,
    minWidth: Dp = FloatingActionButtonDefaults.MinWidth,
    minHeight: Dp = FloatingActionButtonDefaults.MinHeight,
    content: @Composable () -> Unit,  // required
)
```

- `onClick` — The callback when the [FloatingActionButton] is clicked.
- `modifier` — The modifier to be applied to the [FloatingActionButton].
- `shape` — The shape of the [FloatingActionButton].
- `containerColor` — The color of the [FloatingActionButton].
- `shadowElevation` — The shadow elevation of the [FloatingActionButton].
- `minWidth` — The minimum width of the [FloatingActionButton].
- `minHeight` — The minimum height of the [FloatingActionButton].
- `content` — The [Composable] content of the [FloatingActionButton].

**FloatingActionButtonDefaults**

- `MinWidth = 60.dp`
- `MinHeight = 60.dp`
- `ShadowElevation = 4.dp`

**Traps**

- 🔴 When it delegates to Surface it passes only color=containerColor and no contentColor, so Surface uses the default MiuixTheme.colorScheme.onSurface to provide LocalContentColor. Result: the Icon in the default blue FAB gets onSurface (a dark text color) instead of onPrimary, which in a light theme is a 'blue background with a black icon'. You must explicitly write tint = MiuixTheme.colorScheme.onPrimary in content —— example/shared/src/commonMain/kotlin/AppContent.kt:645 does exactly this, but the example in the official docs docs/components/floatingactionbutton.md:24 omits it, so copying the docs gives the wrong contrast.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/FloatingActionButton.kt:46`)
- ⚪ It is the only button at this layer that still exposes shape: Shape (default CircleShape), because it builds on Surface rather than squircleSurface. So the FAB is a mathematically exact circle, not the same curvature as the squircle outline of adjacent Card/Button.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/FloatingActionButton.kt:39`)
- 🟡 There is no enabled parameter, so it can't be disabled; there is also no extended (icon + text) variant, and the width is driven by content (minWidth is only defaultMinSize).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/FloatingActionButton.kt:36`)

**Spec** min_size 60×60.dp (defaultMinSize) · shape CircleShape (true circle, not squircle) · shadow 4.dp (graphicsLayer shadowElevation, clip=false)

**State** Purely stateless, marked @NonRestartableComposable. Positioning/avoidance is left entirely to the caller (Scaffold has a floatingActionButton slot).

**vs Material3** Corresponds to material3.FloatingActionButton. Differences: no elevation state changes (no rise on press), no SmallFAB/LargeFAB/ExtendedFAB variants, no enabled, and the content color is not automatically taken as onPrimary (see above).

**Compilable examples** [`docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt#L53) · [`docs/demo/src/commonMain/kotlin/ScaffoldDemo.kt:79`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ScaffoldDemo.kt#L79) · [`example/shared/src/commonMain/kotlin/AppContent.kt:441`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L441)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/FloatingActionButton.kt:36`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/FloatingActionButton.kt#L36)</sub>

## FloatingNavigationBar  ·  basic component

A capsule-shaped bottom navigation bar floating above content (50dp corner radius, with a shadow and an optional outline). Put it in the Scaffold's bottomBar or floatingToolbar slot.

> A floating navigation bar that supports 2 to 5 items.

```kotlin
import top.yukonga.miuix.kmp.basic.FloatingNavigationBar

@Composable
fun FloatingNavigationBar(
    modifier: Modifier = Modifier,
    color: Color = MiuixTheme.colorScheme.surfaceContainer,
    cornerRadius: Dp = FloatingToolbarDefaults.CornerRadius,
    horizontalAlignment: Alignment.Horizontal = CenterHorizontally,
    horizontalOutSidePadding: Dp = FloatingNavigationBarDefaults.HorizontalOutSidePadding,
    shadowElevation: Dp = FloatingNavigationBarDefaults.ShadowElevation,
    showDivider: Boolean = false,
    defaultWindowInsetsPadding: Boolean = true,
    content: @Composable () -> Unit,  // required
)
```

- `modifier` — A [Modifier] to be applied to the [FloatingNavigationBar] for additional customization.
- `color` — The background color of the [FloatingNavigationBar].
- `cornerRadius` — The corner radius of the [FloatingNavigationBar], used for rounded corners.
- `horizontalAlignment` — The alignment of the [FloatingNavigationBar] within its parent, typically used to center it horizontally.
- `horizontalOutSidePadding` — The horizontal padding to be applied outside the [FloatingNavigationBar].
- `shadowElevation` — The shadow elevation of the [FloatingNavigationBar].
- `showDivider` — Whether to show the divider line around the [FloatingNavigationBar].
- `defaultWindowInsetsPadding` — whether to apply default window insets padding to the [FloatingNavigationBar].
- `content` — The content of the [FloatingNavigationBar], usually [FloatingNavigationBarItem]s.

**FloatingNavigationBarDefaults**

- `HorizontalOutSidePadding = 36.dp`
- `ShadowElevation = 1.dp`
- `HorizontalPadding = 12.dp`
- `ItemSpacing = 12.dp`
- `IconSize = 28.dp`
- `IconPadding = 10.dp`
- `SelectedPressedAlpha = 0.5f`
- `UnselectedPressedAlpha = 0.6f`
- `UnselectedAlpha = 0.4f`

**Traps**

- 🔴 The modifier the caller passes is not at the head of the chain — it is inserted via `.then(modifier)` after the library's own squircleBackground and before the horizontal padding (the source explicitly suppresses ktlint's modifier-not-used-at-root rule for this). Consequences: your `.background(...)` will cover the capsule background, your `.padding(...)` becomes inner padding rather than outer margin, and things like `.size()` also act at the wrong layer. To control the outer position, rely on the parent container, not the modifier.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:350`)
- 🟡 shadowElevation is just a boolean switch: the shadow is added only when `if (shadowElevation > 0.dp)`, and the shadow parameters are hard-coded to radius=10.dp, black, alpha=0.2f. Passing 1.dp and passing 40.dp render exactly the same.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:336`)
- 🟡 The bottom spacing is a nameless magic number: iOS is always 36.dp; other platforms look at the bottom inset of `WindowInsets.navigationBars` — when non-zero it uses `26.dp + system inset` (so three-button navigation is about 74dp), and only when the inset is 0 (desktop / Web / landscape side navigation, etc.) does it fall back to 36.dp. Moreover this padding is added unconditionally (NavigationBar.kt:314); defaultWindowInsetsPadding = false only turns off the captionBar segment (NavigationBar.kt:317-322) and cannot turn it off — to change it you can only make a negative offset in the parent container or rewrite this component yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:289`)

**Spec** corner_radius 50.dp (defaults to FloatingToolbarDefaults.CornerRadius) · min_height 52.dp · horizontal_outside_padding 36.dp (takes effect only when horizontalAlignment is Start/End) · horizontal_padding 12.dp (inside the bar), item_spacing 12.dp · shadow fixed radius=10.dp / black / alpha=0.2f, switched by shadowElevation > 0.dp · divider when showDivider = true it fakes a 1px border with "an outline-colored squircle background + 0.75.dp padding" (avoiding the squircle outline calculation)

**State** Purely controlled, zero state. content is a plain lambda (not RowScope) and arranges itself into a Row internally.

**vs Material3** No direct counterpart. The closest is M3 expressive's FloatingToolbar/HorizontalFloatingToolbar, but that M3 set doesn't carry navigation semantics. M3's NavigationBar is bottom-anchored full width, with no floating capsule form.

**Compilable examples** [`example/shared/src/commonMain/kotlin/AppContent.kt:598`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L598)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:275`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt#L275)</sub>

## FloatingNavigationBarItem  ·  basic component

An item of the floating navigation bar, drawing only one icon.

> A [FloatingNavigationBarItem] that is suitable for [FloatingNavigationBar].

```kotlin
import top.yukonga.miuix.kmp.basic.FloatingNavigationBarItem

@Composable
fun FloatingNavigationBarItem(
    selected: Boolean,  // required
    onClick: () -> Unit,  // required
    icon: ImageVector,  // required
    label: String,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    colors: NavigationBarItemColors = NavigationBarDefaults.navigationBarItemColors(),
    badge: (@Composable () -> Unit)? = null,
)
```

- `selected` — Whether the item is selected.
- `onClick` — The callback when the item is clicked.
- `icon` — The icon of the item.
- `label` — The label of the item.
- `modifier` — The modifier to be applied to the [FloatingNavigationBarItem].
- `enabled` — Whether the item is enabled.
- `colors` — The icon and label colors, with state opacity applied to their alpha.
- `badge` — The optional badge shown on the item's icon, typically a [Badge].

**Traps**

- 🔴 The label parameter is never rendered as text — it is only used as the icon's contentDescription. This component is always icon-only (unlike NavigationBarItem's three modes). Assuming that passing label shows text is wrong.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:415`)
- 🟡 It is a plain function, not a RowScope extension (NavigationBarItem is); the two signatures look identical but are not interchangeable, and it does not split the width evenly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:377`)
- 🟡 It uses NavigationBarDefaults.navigationBarItemColors(), while the three alpha constants in FloatingNavigationBarDefaults (SelectedPressedAlpha / UnselectedPressedAlpha / UnselectedAlpha) have zero references in the whole repository and are dead constants in the public API. Changing them has no effect — and their values happen to equal those in NavigationBarDefaults, so you can't tell the difference either.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:530`)

**Spec** icon_size 28.dp · icon_padding 10.dp (all sides) · alpha the same set as NavigationBarItem (0.4 / 0.6 / 0.5 / 1.0, multiplied with the original color's alpha)

**State** Purely controlled. indication = null, no ripple.

**vs Material3** No counterpart.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/NavigationBarDemo.kt:105`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/NavigationBarDemo.kt#L105) · [`example/shared/src/commonMain/kotlin/AppContent.kt:619`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L619)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:377`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt#L377)</sub>

## FloatingToolbar  ·  basic component

A container responsible only for appearance (a rounded card + optional shadow/outline); its position on screen is decided by the parent — the typical usage is to place it in the Scaffold's floatingToolbar slot and position it with floatingToolbarPosition.

> A [FloatingToolbar] that renders its content in a Card, arranged either horizontally or vertically.
> The actual placement on screen is handled by the parent, typically Scaffold.

```kotlin
import top.yukonga.miuix.kmp.basic.FloatingToolbar

@Composable
fun FloatingToolbar(
    modifier: Modifier = Modifier,
    color: Color = FloatingToolbarDefaults.defaultColor(),
    cornerRadius: Dp = FloatingToolbarDefaults.CornerRadius,
    outSidePadding: PaddingValues = FloatingToolbarDefaults.OutSidePadding,
    shadowElevation: Dp = 4.dp,
    showDivider: Boolean = false,
    content: @Composable () -> Unit,  // required
)
```

- `modifier` — The modifier to be applied to the [FloatingToolbar].
- `color` — Background color of the [FloatingToolbar].
- `cornerRadius` — Corner radius of the [FloatingToolbar].
- `outSidePadding` — Padding outside the [FloatingToolbar].
- `shadowElevation` — The shadow elevation of the [FloatingToolbar].
- `showDivider` — Whether to show the divider line around the [FloatingToolbar].
- `content` — The [Composable] content of the [FloatingToolbar].

**FloatingToolbarDefaults**

- `defaultColor()`
- `CornerRadius = 50.dp`
- `OutSidePadding = PaddingValues(12.dp, 8.dp)`

**Traps**

- 🟡 The KDoc says "arranged either horizontally or vertically," but the component has no orientation parameter; internally it is just a Box. Whether it is horizontal or vertical depends entirely on whether you put a Row or a Column in content yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/FloatingToolbar.kt:70`)
- 🟡 shadowElevation is a boolean switch; the shadow parameters are hard-coded to radius=10.dp, black, alpha=0.1f. 4.dp and 40.dp render the same.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/FloatingToolbar.kt:57`)
- 🟡 It handles no window insets itself, and doesn't know bottomBar exists. When placed in the Scaffold's floatingToolbar slot with a Bottom* position it covers the NavigationBar (see the Scaffold entry); with a Top*/Center* position it shifts down by one status-bar height due to Scaffold's topInset double-counting.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Scaffold.kt:282`)

**Spec** corner_radius 50.dp · outside_padding PaddingValues(12.dp, 8.dp) · shadow fixed radius=10.dp / black / alpha=0.1f · divider same as FloatingNavigationBar, drawing the border with "an outline-colored squircle + 0.75.dp padding"

**State** Stateless. Here the modifier is at the head of the chain (opposite to FloatingNavigationBar), which is idiomatic Compose. It is marked @NonRestartableComposable and is a pure delegating wrapper.

**vs Material3** Corresponds to material3 expressive's HorizontalFloatingToolbar / VerticalFloatingToolbar. The differences are obvious: that M3 set comes with orientation, expanded/collapsed animation, a floatingActionButton slot, and scroll linkage (FloatingToolbarScrollBehavior); this Miuix one is only 101 lines, a pure appearance container, with orientation and animation all left to the caller. The ToolbarPosition enum is defined in Scaffold.kt, not here.

**Compilable examples** [`example/shared/src/commonMain/kotlin/AppContent.kt:445`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L445)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/FloatingToolbar.kt:38`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/FloatingToolbar.kt#L38)</sub>

## InputField  ·  basic component

A pill-shaped input field dedicated to SearchBar (defined in SearchBar.kt, not TextField.kt). It ships with a search icon, a clear button, and an IME Search action, and must be used paired with the expanded state.

> A text field to input a query in a search bar with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.InputField

@Composable
fun InputField(
    query: String,  // required
    onQueryChange: (String) -> Unit,  // required
    onSearch: (String) -> Unit,  // required
    expanded: Boolean,  // required
    onExpandedChange: (Boolean) -> Unit,  // required
    modifier: Modifier = Modifier,
    label: String = "",
    enabled: Boolean = true,
    textStyle: TextStyle? = null,
    color: Color = MiuixTheme.colorScheme.surfaceContainerHigh,
    leadingIcon: @Composable (() -> Unit)? = null,
    trailingIcon: @Composable (() -> Unit)? = null,
    interactionSource: MutableInteractionSource? = null,
)
```

- `query` — the query text to be shown in the input field.
- `onQueryChange` — the callback to be invoked when the input service updates the query. An   updated text comes as a parameter of the callback.
- `onSearch` — the callback to be invoked when the input service triggers the   [ImeAction.Search] action. The current [query] comes as a parameter of the callback.
- `expanded` — whether the search bar is expanded and showing search results.
- `onExpandedChange` — the callback to be invoked when the search bar's expanded state is   changed.
- `modifier` — the [Modifier] to be applied to this input field.
- `label` — the label to be shown when the input field is not focused.
- `enabled` — the enabled state of this input field. When `false`, this component will not   respond to user input, and it will appear visually disabled and disabled to accessibility   services.
- `textStyle` — Style configuration that applies at character level such as color, font etc.
- `color` — the background color of the input field's capsule. Pass [Color.Transparent] when   drawing your own background behind it (e.g. a backdrop blur).
- `leadingIcon` — the leading icon to be displayed at the start of the input field.
- `trailingIcon` — the trailing icon to be displayed at the end of the input field.
- `interactionSource` — an optional hoisted [MutableInteractionSource] for observing and   emitting [Interaction]s for this input field. You can use this to change the search bar's   appearance or preview the search bar in different states. Note that if `null` is provided,   interactions will still happen internally.

**Traps**

- 🔴 It clears the text on collapse: in LaunchedEffect(expanded), when expanded becomes false and it currently has focus, it delays(100), fades the text out, and calls onQueryChange(""). That is, collapsing the search box = discarding the user's input; this is not optional and there is no toggle.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt:302`)
- 🔴 In onFocusChanged, as soon as it gains focus it unconditionally calls onExpandedChange(true). So expanded / onExpandedChange must actually be wired to a state; using it as an ordinary input field (writing onExpandedChange as an empty lambda) makes it fail to expand on tap and gives wrong keyboard and clear-button behavior.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt:242`)
- 🟡 On Android SDK ≤ 27 there is a system bug in focus reassignment (issuetracker 433382598). The code's workaround is: in the collapsed state, set BasicTextField's enabled to false and take over taps via pointerInput. The condition is `hasFocusReassignBug = Build.VERSION.SDK_INT <= Build.VERSION_CODES.O_MR1` (miuix-core/src/androidMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.android.kt:24), and the library's minSdk is 24 (build-plugins/src/main/kotlin/BuildConfig.kt:14), so it actually affects API 24-27 (the comment at SearchBar.kt:226 says 'API 26-27', which is narrower than the implementation). On these versions the collapsed-state InputField is not a truly enabled input field.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt:249`)
- ⚪ If leadingIcon/trailingIcon are not passed, you get the built-in search icon and clear button (the clear button fades in only when query is non-empty, and a tap calls onQueryChange("")). Passing custom icons removes the clear functionality entirely and you must implement it yourself. The default background is surfaceContainerHigh; to draw your own background (e.g. a blur backdrop) pass color = Color.Transparent.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt:188`)

**Spec** shape CircleShape pill · min_height 45.dp (SearchBarDefaults.InputFieldMinHeight) · label_font 17.sp Medium · icon_padding leading icon start 16 / end 8, trailing icon start 8 / end 16

**State** Purely controlled and tightly coupled: the four-piece set query/onQueryChange and expanded/onExpandedChange are all required. singleLine is hardcoded to true and imeAction hardcoded to Search. The text style = textStyles.main + Medium, then merged with the caller's textStyle, and the color is forced to LocalContentColor.

**vs Material3** Corresponds to material3.SearchBarDefaults.InputField. Behavior is close, but the Miuix version actively clears query on collapse and has no placeholder parameter (label serves that role).

**Compilable examples** [`docs/demo/src/commonMain/kotlin/SearchBarDemo.kt:49`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SearchBarDemo.kt#L49) · [`example/shared/src/commonMain/kotlin/MainPage.kt:321`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MainPage.kt#L321) · [`example/shared/src/commonMain/kotlin/component/SuperSearchBar.kt:240`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SuperSearchBar.kt#L240)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt:158`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt#L158)</sub>

## List<BreadcrumbItem>.joinToPath  ·  basic component

An extension function that joins the path segments of a breadcrumb list into a complete path string.

> Joins the [path] segments of all [BreadcrumbItem]s in this list into a single path string using
> the given [separator].

```kotlin
import top.yukonga.miuix.kmp.basic.joinToPath

fun List<BreadcrumbItem>.joinToPath(
    separator: String = "/",
): String
```

- `separator` — The separator placed between path segments. Defaults to `"/"`.

**Traps**

- ⚪ It joins each item's path field, not the display text. In scenarios where an item was given an alias text, joinToPath's result is the real path rather than the text you see — this is exactly its intent, but it's easily misused as "joining display text."  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/BreadcrumbBar.kt:334`)
- ⚪ separator defaults to "/", and a no-argument call does not automatically add leading/trailing slashes — `listOf(a, b).joinToPath()` gives "a/b" rather than "/a/b". For Windows style pass "\\" explicitly (a single-backslash literal in Kotlin source).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/BreadcrumbBar.kt:334`)

**Spec** 

**State** A pure function, stateless.

**vs Material3** No counterpart.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt:68`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt#L68) · [`example/shared/src/commonMain/kotlin/component/BreadcrumbBarSection.kt:67`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BreadcrumbBarSection.kt#L67)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/BreadcrumbBar.kt:334`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/BreadcrumbBar.kt#L334)</sub>

## NavigationBar  ·  basic component

A bottom navigation bar with a slot-based API (you place NavigationBarItems inside content yourself), with a divider and bottom system-bar spacing. Put it in the Scaffold's bottomBar.

> A [NavigationBar] that with 2 to 5 items.

```kotlin
import top.yukonga.miuix.kmp.basic.NavigationBar

@Composable
fun NavigationBar(
    modifier: Modifier = Modifier,
    color: Color = MiuixTheme.colorScheme.surface,
    showDivider: Boolean = true,
    defaultWindowInsetsPadding: Boolean = true,
    mode: NavigationBarDisplayMode = NavigationBarDisplayMode.IconAndText,
    content: @Composable RowScope.() -> Unit,  // required
)
```

- `modifier` — The modifier to be applied to the [NavigationBar].
- `color` — The color of the [NavigationBar].
- `showDivider` — Whether to show the divider line between the [NavigationBar] and the content.
- `defaultWindowInsetsPadding` — whether to apply default window insets padding to the [NavigationBar].
- `mode` — The mode for displaying items in the [NavigationBar]. It can show icons, text or both.
- `content` — The content of the [NavigationBar], usually [NavigationBarItem]s.

**NavigationBarDefaults**


```kotlin
NavigationBarDefaults.navigationBarItemColors(
    unselectedContentColor: Color = MiuixTheme.colorScheme.onSurfaceContainer,
    selectedContentColor: Color = MiuixTheme.colorScheme.onSurfaceContainer,
)
```

- `ItemHeight = 64.dp`
- `IconSize = 26.dp`
- `LabelFontSize = 12.sp`
- `IconTopPadding = 8.dp`
- `BottomPadding = 8.dp`
- `SelectedPressedAlpha = 0.5f`
- `UnselectedPressedAlpha = 0.6f`
- `UnselectedAlpha = 0.4f`

**Traps**

- 🔴 It has no parameters like items / selected / onClick (such examples in the docs are wrong and won't compile). The only signature is slot-based: `NavigationBar { items.forEachIndexed { i, item -> NavigationBarItem(selected = ..., onClick = ..., icon = ..., label = ...) } }`, where content is a required trailing lambda.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:74`)
- 🟡 It doesn't handle horizontal window insets at all (TopAppBar handles the Horizontal of displayCutout/navigationBars, NavigationRail handles Start, only this one doesn't). In landscape + notch screens the outermost items get clipped; the caller must add windowInsetsPadding on the modifier.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:109`)
- 🟡 On iOS the bottom spacing is hard-coded to 20.dp (it does not read WindowInsets.navigationBars), because that inset is unreliable for CMP on iOS. On an iPad or a device without a Home Indicator you get the same 20dp gap, which you can only turn off with defaultWindowInsetsPadding = false and then add your own.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:113`)
- ⚪ The display mode (IconAndText / IconOnly / IconWithSelectedLabel) is dispatched to the item via CompositionLocal, so there is no mode parameter on the item. If you place a NavigationBarItem outside NavigationBar (or under a separate CompositionLocalProvider layer), you get the default IconAndText.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:105`)

**Spec** item_height 64.dp · icon_size 26.dp · label_font_size 12.sp · icon_top_padding 8.dp (selected state; when unselected in IconWithSelectedLabel it changes to (64-26)/2 = 19.dp, centered) · label_bottom_padding 8.dp · caption_bar_anim when entering/leaving split-screen / freeform window, the captionBar height transitions with tween(300ms) to avoid an inset-jump flicker

**State** Purely controlled, zero state. The selected state is driven entirely by the caller's selected: Boolean + onClick; the component knows nothing about routing (miuix-nav is an independent module with no code dependency here). mode is dispatched down one-directionally via LocalNavigationBarDisplayMode.

**vs Material3** Corresponds to material3.NavigationBar. Differences: M3's NavigationBarItem has label/alwaysShowLabel/colors etc.; Miuix expresses the same thing with a three-way mode enum + CompositionLocal; M3 has a windowInsets parameter accepting any WindowInsets, while Miuix only has a boolean switch and no horizontal direction; M3's item has an indicator pill background, while Miuix's bottom-bar item has no indicator (it distinguishes only by color alpha).

**Compilable examples** [`example/shared/src/commonMain/kotlin/AppContent.kt:478`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L478)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:74`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt#L74)</sub>

## RowScope.NavigationBarItem  ·  basic component

A single item of the bottom navigation bar, icon + text, with badge support. Can only be placed inside NavigationBar.

> A [NavigationBarItem] that is suitable for [NavigationBar].

```kotlin
import top.yukonga.miuix.kmp.basic.NavigationBarItem

@Composable
fun RowScope.NavigationBarItem(
    selected: Boolean,  // required
    onClick: () -> Unit,  // required
    icon: ImageVector,  // required
    label: String,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    colors: NavigationBarItemColors = NavigationBarDefaults.navigationBarItemColors(),
    badge: (@Composable () -> Unit)? = null,
)
```

- `selected` — Whether the item is selected.
- `onClick` — The callback when the item is clicked.
- `icon` — The icon of the item.
- `label` — The label of the item.
- `modifier` — The modifier to be applied to the [NavigationBarItem].
- `enabled` — Whether the item is enabled.
- `colors` — The icon and label colors, with state opacity applied to their alpha.
- `badge` — The optional badge shown on the item's icon, typically a [Badge].

**NavigationBarItemColors** (data class) ⚠️ 2/2 constructor params are `private val` and **cannot be read from an instance**; these names are only usable as named arguments to the factory functions above.

**Traps**

- 🔴 It is an extension function on `RowScope` (internally using weight(1f) to split the width evenly). Placing it in a Column, Box, or any non-RowScope scope fails to compile directly; and the identically named FloatingNavigationBarItem is a plain function — the two are not interchangeable.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:145`)
- 🟡 The selected/pressed colors are `original color.alpha * factor` multiplied rather than replaced (unselected 0.4, unselected-pressed 0.6, selected-pressed 0.5). Passing Color.Transparent stays fully transparent, and passing a semi-transparent color multiplies once more on top of it — for "grey when unselected, blue when selected" you can't rely on colors alone; you must pass two different color values.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:498`)
- ⚪ indication is explicitly set to null, so there is no ripple feedback; press feedback relies entirely on the alpha multiplication above. This is the deliberate MIUI look, but it means LocalIndication has no effect here.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:173`)
- ⚪ The morph in IconWithSelectedLabel mode uses `by animateDpAsState` / `by animateFloatAsState`, but both reads are sunk outside composition: iconTopPadding is read inside the measure lambda of `Modifier.layout{}` (NavigationBar.kt:219), and textAlpha inside `graphicsLayer{}` (NavigationBar.kt:237). So this 300ms animation only re-measures/redraws and does not recompose the item every frame. What actually reads the progress in composition is the label leaf of NavigationRailItem (font size is a composition-time parameter of Text and cannot be sunk).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:205`)

**Spec** icon_size 26.dp · label_font_size 12.sp, bold when selected (FontWeight.Bold), Normal when unselected · alpha unselected 0.4 / unselected-pressed 0.6 / selected-pressed 0.5 / selected 1.0 (all multiplied with the original color's alpha) · morph_duration 300ms tween (in IconWithSelectedLabel mode the icon moves up + the text fades in)

**State** Purely controlled. Both selected and onClick are required; there is no internal selected state. interactionSource is built internally and cannot be passed in from outside.

**vs Material3** Corresponds to material3.NavigationBarItem. That M3's is also a RowScope extension is the same; the differences are that M3 has alwaysShowLabel, an indicator pill, and a configurable NavigationBarItemColors with 6 color slots, while Miuix has only two base colors + fixed alpha factors and no indicator.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/NavigationBarDemo.kt:70`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/NavigationBarDemo.kt#L70) · [`docs/demo/src/commonMain/kotlin/ScaffoldDemo.kt:69`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ScaffoldDemo.kt#L69) · [`example/shared/src/commonMain/kotlin/AppContent.kt:569`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L569)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:145`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt#L145)</sub>

## NavigationRail  ·  basic component

A side navigation bar, for wide screens. Since 0.9.4 it is one of two overloads: `NavigationRail(expanded = …)` is a fixed layout (collapsed = the classic vertical stack with icon above and text below, expanded = a pill list with icon in front and text after, no toggle button, no animation); `NavigationRail(state = rememberNavigationRailState())` is a switchable layout (a built-in expand/collapse button at the top, with a continuous morph animation between the two layouts). Passing nothing means fixed collapsed.

> A non-expandable [NavigationRail] for wide screens.

```kotlin
import top.yukonga.miuix.kmp.basic.NavigationRail

@Composable
fun NavigationRail(
    modifier: Modifier = Modifier,
    expanded: Boolean = false,
    header: @Composable (ColumnScope.() -> Unit)? = null,
    color: Color = MiuixTheme.colorScheme.surface,
    showDivider: Boolean = true,
    defaultWindowInsetsPadding: Boolean = true,
    minWidth: Dp = NavigationRailDefaults.MinWidth,
    expandedWidth: Dp = NavigationRailDefaults.ExpandedWidth,
    scrollState: ScrollState = rememberScrollState(),
    content: @Composable ColumnScope.() -> Unit,  // required
)
```

- `modifier` — The modifier to be applied to the [NavigationRail].
- `expanded` — Whether the rail uses its expanded layout.
- `header` — The header of the [NavigationRail], usually a [FloatingActionButton] or a logo.
- `color` — The color of the [NavigationRail].
- `showDivider` — Whether to show the divider line between the [NavigationRail] and the content.
- `defaultWindowInsetsPadding` — whether to apply default window insets padding to the [NavigationRail].
- `minWidth` — The minimum width of the [NavigationRail], used for the collapsed state.
- `expandedWidth` — The width of the [NavigationRail] when [expanded] is true.
- `scrollState` — The [ScrollState] of the rail's scrollable content column.
- `content` — The content of the [NavigationRail], usually [NavigationRailItem]s.

**NavigationRailDefaults**

- `MinWidth = 80.dp`
- `ExpandedWidth = 240.dp`
- `VerticalPadding = 24.dp`
- `HeaderSpacing = 24.dp`
- `IconSize = 28.dp`
- `IconTextSpacing = 4.dp`
- `ItemVerticalPadding = 12.dp`
- `LabelFontSize = 12.sp`
- `ExpandedLabelFontSize = 16.sp`
- `ExpandedItemHorizontalMargin = 12.dp`
- `ExpandedItemCornerRadius = 16.dp`
- `CollapsedIndicatorVerticalPadding = 4.dp`
- `ExpandedItemContentHorizontalPadding = 14.dp`
- `ExpandedItemContentVerticalPadding = 14.dp`
- `ExpandedItemIconTextSpacing = 16.dp`
- `ExpandContentDescription = "`
- `CollapseContentDescription = "`

**Traps**

- 🔴 0.9.4 is a breaking change: the original single `NavigationRail(modifier, state: NavigationRailState? = null, …)` was split into `NavigationRail(modifier, expanded: Boolean = false, …)` and `NavigationRail(state: NavigationRailState, modifier, …)`, with state becoming non-null and moved to first position. The old forms `NavigationRail(state = null)`, `NavigationRail(state = if (wide) railState else null)`, and the positional `NavigationRail(Modifier.x, railState)` all fail to compile on 0.9.4 because no matching overload exists (it does not silently fall through to the other overload); the named-parameter form `NavigationRail(modifier = m, state = railState)` still compiles. Migration: change nullable state to always passing a non-null state, and drive wide/narrow screens with expand()/collapse(); change places that passed null to omitting it or writing `expanded = false`. Conversely, `expanded = …` written for 0.9.4 also fails to compile on 0.9.4-rc01 and earlier.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:143`)
- 🟡 The two overloads have asymmetric capabilities: the expand/collapse button and the morph animation belong only to the state overload, and as soon as you use the state overload the button always appears — no parameter can hide it; the expanded overload never has a button, and when expanded flips, the width and item layout jump within one frame (the progress is a `remember(expanded) { mutableStateOf(0f/1f) }` constant, not an animation). So "animation but no built-in button" is impossible with either overload; for "auto-expand on wide screens with animation" you must use the state overload + call expand()/collapse() yourself in a LaunchedEffect.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:196-204`)
- 🟡 expandContentDescription / collapseContentDescription exist only on the state overload (the expanded overload has no button and naturally lacks these two parameters); passing them to the expanded overload fails to compile. The defaults are hard-coded English "Expand navigation rail" / "Collapse navigation rail"; when using the state overload and needing localization you must pass them explicitly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:151-152`)
- 🟡 The library has no breakpoints or adaptive logic; whether it expands comes only from the caller's state or expanded (the sample app itself uses width >= 1200.dp). And although miuix-ui declares a dependency on material3-window-size-class, no line of Kotlin in the whole repository uses WindowSizeClass — don't expect the library to provide WindowSizeClass integration.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:190`)
- 🟡 When expandedWidth is smaller than minWidth it is silently corrected to minWidth via coerceAtLeast (expanded equals not expanded, without an error). Also, changing minWidth away from the default 80.dp breaks a deliberately tuned numeric coincidence: the collapsed-state icon center (80-28)/2 = 26dp exactly equals the expanded state's 12dp outer margin + 14dp inner padding, so under the default parameters the X coordinates of the state overload's icon and toggle button stay perfectly still throughout the animation; after changing minWidth they drift left and right during expansion.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:192`)
- ⚪ The insets order of the inner scroll column is deliberate: statusBars.only(Top) is outside verticalScroll (the top spacing stays fixed and doesn't scroll), navigationBars.only(Bottom) is inside verticalScroll (the bottom spacing scrolls with the content to the end). The background color is also deliberately drawn before the insets padding, so the rail's color spreads under the side notch. Changing the order of these lines produces visible visual bugs.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:242-244`)

**Spec** collapsed_width 80.dp (MinWidth) · expanded_width 240.dp (ExpandedWidth) · icon_size 28.dp · label_font_size collapsed 12.sp → expanded 16.sp (the state overload interpolates; the expanded overload takes one of the two ends directly) · expanded_pill corner radius 16.dp, left/right outer margin 12.dp, inner padding 14.dp, icon-to-text spacing 16.dp · vertical_padding 24.dp (top and bottom of content), HeaderSpacing 24.dp (after the expand button/header) · expand_content_description only the state overload has this parameter; the defaults are hard-coded English "Expand navigation rail" / "Collapse navigation rail"; for localization you must pass it explicitly

**State** The expanded overload is stateless: expanded is passed directly by the caller, and internally it only remembers a constant progress, flipping means an instant jump. The state overload's state is hosted by the caller's rememberNavigationRailState() (non-null, required); the expand animation is driven by a single State<Float> timeline, and it deliberately does not destructure with `by` — progress is passed to the item as a State<Float> via CompositionLocal and its .value is read only inside Modifier.layout{} and the measure lambda, so spring frames only re-measure and don't recompose. The sole composition-time read is isolated in the label leaf (font size is a composition-time parameter of Text and cannot be sunk).

**vs Material3** Corresponds to material3.NavigationRail (and M3 expressive's WideNavigationRail). M3 expresses the narrow/wide forms with two separate components; Miuix uses two identically named overloads: the expanded boolean overload gives static narrow/wide layouts, and the state overload does a continuous morph animation between them; that M3 has a header slot is the same; M3's windowInsets parameter degenerates here into a boolean switch.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/NavigationRailDemo.kt:69`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/NavigationRailDemo.kt#L69) · [`example/shared/src/commonMain/kotlin/AppContent.kt:364`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L364)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:91`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt#L91)</sub>

## NavigationRail  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> An expandable [NavigationRail] for wide screens.
> 
> The rail shows a built-in toggle and animates between [minWidth] and [expandedWidth] according
> to [state].

```kotlin
import top.yukonga.miuix.kmp.basic.NavigationRail

@Composable
fun NavigationRail(
    state: NavigationRailState,  // required
    modifier: Modifier = Modifier,
    header: @Composable (ColumnScope.() -> Unit)? = null,
    color: Color = MiuixTheme.colorScheme.surface,
    showDivider: Boolean = true,
    defaultWindowInsetsPadding: Boolean = true,
    minWidth: Dp = NavigationRailDefaults.MinWidth,
    expandedWidth: Dp = NavigationRailDefaults.ExpandedWidth,
    expandContentDescription: String = NavigationRailDefaults.ExpandContentDescription,
    collapseContentDescription: String = NavigationRailDefaults.CollapseContentDescription,
    scrollState: ScrollState = rememberScrollState(),
    content: @Composable ColumnScope.() -> Unit,  // required
)
```

- `state` — Controls the expanded/collapsed state.
- `modifier` — The modifier to be applied to the [NavigationRail].
- `header` — The header of the [NavigationRail], usually a [FloatingActionButton] or a logo.
- `color` — The color of the [NavigationRail].
- `showDivider` — Whether to show the divider line between the [NavigationRail] and the content.
- `defaultWindowInsetsPadding` — whether to apply default window insets padding to the [NavigationRail].
- `minWidth` — The minimum width of the [NavigationRail], used for the collapsed state.
- `expandedWidth` — The width of the [NavigationRail] when expanded.
- `expandContentDescription` — The accessible description of the built-in toggle while the rail   is collapsed; override it to localize the announcement.
- `collapseContentDescription` — The accessible description of the built-in toggle while the   rail is expanded; override it to localize the announcement.
- `scrollState` — The [ScrollState] of the rail's scrollable content column.
- `content` — The content of the [NavigationRail], usually [NavigationRailItem]s.

**NavigationRailDefaults**

- `MinWidth = 80.dp`
- `ExpandedWidth = 240.dp`
- `VerticalPadding = 24.dp`
- `HeaderSpacing = 24.dp`
- `IconSize = 28.dp`
- `IconTextSpacing = 4.dp`
- `ItemVerticalPadding = 12.dp`
- `LabelFontSize = 12.sp`
- `ExpandedLabelFontSize = 16.sp`
- `ExpandedItemHorizontalMargin = 12.dp`
- `ExpandedItemCornerRadius = 16.dp`
- `CollapsedIndicatorVerticalPadding = 4.dp`
- `ExpandedItemContentHorizontalPadding = 14.dp`
- `ExpandedItemContentVerticalPadding = 14.dp`
- `ExpandedItemIconTextSpacing = 16.dp`
- `ExpandContentDescription = "`
- `CollapseContentDescription = "`

**Compilable examples** [`docs/demo/src/commonMain/kotlin/NavigationRailDemo.kt:69`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/NavigationRailDemo.kt#L69) · [`example/shared/src/commonMain/kotlin/AppContent.kt:364`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L364)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:142`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt#L142)</sub>

## NavigationRailItem  ·  basic component

An item of the side navigation bar. In a state-overload rail it continuously morphs with the expand progress between "icon above, text below" and "a pill with icon in front, text after"; in the expanded overload it is fixed to one of these.

> A [NavigationRailItem] that is suitable for [NavigationRail].

```kotlin
import top.yukonga.miuix.kmp.basic.NavigationRailItem

@Composable
fun NavigationRailItem(
    selected: Boolean,  // required
    onClick: () -> Unit,  // required
    icon: ImageVector,  // required
    label: String,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    badge: (@Composable () -> Unit)? = null,
)
```

- `selected` — Whether the item is selected.
- `onClick` — The callback when the item is clicked.
- `icon` — The icon of the item.
- `label` — The label of the item.
- `modifier` — The modifier to be applied to the [NavigationRailItem].
- `enabled` — Whether the item is enabled.
- `badge` — The optional badge shown on the item's icon, typically a [Badge].

**Traps**

- 🟡 The selected state is expressed only by a surfaceContainerHigh squircle behind the icon: tint is unconditionally onSurfaceContainer and fontWeight is unconditionally Medium; neither the icon/text color nor the weight changes with selected. Since 0.9.4 the collapsed (classic) layout also draws this background hugging the icon (14.dp left/right, 4.dp top/bottom); in 0.9.4-rc01 and earlier the classic rail (state == null) had no visual effect for selected at all — only the expandable rail drew the pill. On older versions you must wrap your own background to show selection; after upgrading to 0.9.4 you must delete that homemade background to avoid stacking two layers.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:383-387`)
- 🟡 It has no colors parameter (NavigationBarItem does). All colors come from the theme's onSurfaceContainer / surfaceContainerHigh; to change them you can only swap the theme.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:340-341`)
- ⚪ The two layout paths attach indication differently: the classic path (the fixed layout with expanded = false) attaches it on selectable (the whole item has a ripple); the morph path (state overload, or expanded = true) sets selectable's indication to null and instead attaches it on the indicator Box (the ripple only follows the icon/pill). So the same LocalIndication has a different visual scope in the two forms.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:477`)
- ⚪ Since 0.9.4 the padding wrapping the icon on the classic path (expanded = false) (14.dp left/right, 4.dp top/bottom) is unconditional, with only the background looking at selected: so an unselected item is also 8.dp taller than in 0.9.4-rc01, and the icon area grows from 28.dp wide to 56.dp wide. When upgrading from an older version, adjacent content aligned to the old dimensions will be misaligned, and a column of items will overflow its height and start scrolling earlier; the classic item in 0.9.4-rc01 and earlier had no such padding.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:392-395`)

**Spec** icon_size 28.dp · collapsed_label 12.sp; the icon is wrapped in a layer of padding (14.dp left/right, 4.dp top/bottom, regardless of selection; the classic path also has it since 0.9.4), the icon block is 56×36.dp; IconTextSpacing 4.dp is added between the icon block and the text, so the visual gap from the icon's bottom edge to the text is 8.dp (the morph path's collapsed state is likewise 8.dp); item top/bottom padding 12.dp (icon top edge to item top 16.dp) · expanded_label 16.sp, overlong text uses TextOverflow.Ellipsis (no hard clip) · indicator a surfaceContainerHigh squircle with 16.dp corner radius; when collapsed it hugs the icon at 14.dp left/right, 4.dp top/bottom (the classic path also draws it since 0.9.4); when expanded it grows into a full pill (14.dp top/bottom)

**State** Purely controlled (selected + onClick). Whether it takes the morph path is decided by whether LocalNavigationRailExpandInfo is null: non-null when the rail uses the state overload or expanded = true, null taking the classic Column path when expanded = false; the item itself does not know the rail's state object. All geometry is interpolated by float in the measure lambda and each coordinate is rounded only once (to avoid odd/even rounding jitter between adjacent frames).

**vs Material3** Corresponds to material3.NavigationRailItem. M3's item has alwaysShowLabel, an indicator pill, and a full NavigationRailItemColors; Miuix uses a single fixed-color squircle to indicate selection in both forms, the icon/text color does not change with selection, and the colors are not configurable.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/NavigationRailDemo.kt:73`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/NavigationRailDemo.kt#L73) · [`example/shared/src/commonMain/kotlin/AppContent.kt:368`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L368)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:329`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt#L329)</sub>

## rememberNavigationRailState  ·  basic component

Creates and remembers the side bar's expanded/collapsed state. Only NavigationRail's state overload accepts it (non-null, required); once passed the rail gets a built-in toggle button and an expand animation.

> Creates and remembers a [NavigationRailState] that survives configuration changes and process
> death.

```kotlin
import top.yukonga.miuix.kmp.basic.rememberNavigationRailState

@Composable
fun rememberNavigationRailState(
    initialValue: NavigationRailValue = NavigationRailValue.Collapsed,
): NavigationRailState
```

- `initialValue` — The initial [NavigationRailValue]. Defaults to [NavigationRailValue.Collapsed].

**Traps**

- ⚪ currentValue is private set and can only be modified via expand() / collapse() / toggle(); it cannot be assigned directly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:694`)
- 🟡 "Auto-expand on wide screens" must be written yourself: something like `LaunchedEffect(isWide) { if (isWide) state.expand() else state.collapse() }` (when you don't need the button and animation you can also just use `NavigationRail(expanded = isWide)`). Don't use if/else on width to switch between the state overload and the expanded overload — those are two different call sites, and state such as the rail's scroll position will be rebuilt with no animation; likewise, for wide/narrow-screen adaptation keep the navigation host at the same composition position, since placing a route container in each of the two if/else branches will rebuild the current route.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:731`)

**Spec** 

**State** rememberSaveable + a Saver that stores the enum as its ordinal, surviving configuration changes and process death. The public NavigationRailState.Saver can be dropped into a custom listSaver/mapSaver. The expand animation is derived declaratively by the rail from currentValue, so changing the state makes it animate with no extra call needed.

**vs Material3** No counterpart. M3's NavigationRail has no state object and switches the wide/narrow form by swapping components; WideNavigationRail's expanded state in M3 is WideNavigationRailState / rememberWideNavigationRailState (expressive, still experimental), which is semantically close but has a different API.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/NavigationRailDemo.kt:59`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/NavigationRailDemo.kt#L59) · [`example/shared/src/commonMain/kotlin/AppContent.kt:358`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L358)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt:731`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationRail.kt#L731)</sub>

## SearchBar  ·  basic component

A search-bar shell — responsible for showing outsideEndAction (a cancel button and the like) and the results-area content when expanded, and registering back-key handling. The actual input field is the paired but independent InputField.

> A [SearchBar] component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.SearchBar

@Composable
fun SearchBar(
    inputField: @Composable () -> Unit,  // required
    onExpandedChange: (Boolean) -> Unit,  // required
    modifier: Modifier = Modifier,
    insideMargin: DpSize = SearchBarDefaults.InsideMargin,
    expanded: Boolean = false,
    outsideEndAction: @Composable (() -> Unit)? = null,
    content: @Composable ColumnScope.() -> Unit,  // required
)
```

- `inputField` — the input field to input a query in the [SearchBar].
- `onExpandedChange` — the callback to be invoked when the [SearchBar]'s expanded state is   changed.
- `modifier` — the [Modifier] to be applied to the [SearchBar].
- `insideMargin` — The margin inside the [SearchBar].
- `expanded` — whether the [SearchBar] is expanded and showing search results.
- `outsideEndAction` — the action to be shown at the end side of the [SearchBar] when it is   expanded.
- `content` — the content to be shown when the [SearchBar] is expanded.

**SearchBarDefaults**

- `InsideMargin = DpSize(12.dp, 0.dp)`
- `InputFieldMinHeight = 45.dp`
- `InputFieldFontSize = 17.sp`
- `LeadingIconStartPadding = 16.dp`
- `LeadingIconEndPadding = 8.dp`
- `TrailingIconStartPadding = 8.dp`
- `TrailingIconEndPadding = 16.dp`

**Traps**

- 🔴 The SearchBar's expanded and the InputField's expanded are two independent parameters that the caller must wire together manually with the same state. Passing expanded only to SearchBar while InputField is not wired means the input field won't gain focus or trigger expansion.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt:86`)
- 🔴 Undocumented side effect: when expanded becomes false, InputField automatically clears the query — delay(100) → text fades out → calls onQueryChange("") → restores opacity → clearFocus. Code that saves query as the "submitted search term" will have it wiped by the component; the hand-written `searchText = ""` in the doc example is actually redundant.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt:304`)
- 🟡 SearchBar internally registers a NavigationBackHandler: when expanded is true it intercepts the system back and calls back onExpandedChange(false). This brings a runtime dependency (androidx.navigationevent), and also means your own back handling will be preempted by it.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt:122`)
- 🟡 InputField's expansion is focus-driven (onFocusChanged → onExpandedChange(true)), and it has a workaround for the focus-reassignment bug on Android API 26-27: when collapsed the whole TextField is disabled, and click-to-expand is instead handled by an external pointerInput. So on these OS versions the collapsed TextField is enabled=false, and any custom logic depending on its editability will break.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt:229`)

**Spec** inside_margin DpSize(12.dp, 0.dp) (horizontal 12dp, vertical 0dp) · input_field_shape CircleShape (capsule) · outside_end_action_anim expandHorizontally + slideInHorizontally (slides in from the right)

**State** SearchBar itself is stateless; expanded is fully controlled (the default false is only the value when the parameter is omitted, it does not mean it flips itself). InputField is also controlled and only internally holds a focusRequester, interactionSource, and an Animatable for fade-out. Three state edges: gaining focus → expand; expanded becomes true → request focus; expanded becomes false while focused → clear + unfocus.

**vs Material3** Corresponds to material3.SearchBar / DockedSearchBar + SearchBarDefaults.InputField. The structure is similar (both are a shell + inputField slot + controlled expanded), but M3's SearchBar covers the full screen when expanded and comes with an animation container, while Miuix just expands an AnimatedVisibility block in place; M3 does not clear query for you on collapse, Miuix does.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/SearchBarDemo.kt:47`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SearchBarDemo.kt#L47) · [`example/shared/src/commonMain/kotlin/MainPage.kt:318`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MainPage.kt#L318) · [`example/shared/src/commonMain/kotlin/component/SuperSearchBar.kt:80`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SuperSearchBar.kt#L80)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt:81`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SearchBar.kt#L81)</sub>

## TabRow  ·  basic component

A flat segmented tab bar (no outer frame); the selected item is indicated by a squircle background block, and when labels exceed the width it can scroll horizontally and automatically scrolls the selected item to center.

> A [TabRow] with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.TabRow

@Composable
fun TabRow(
    tabs: List<String>,  // required
    selectedTabIndex: Int,  // required
    onTabSelected: (Int) -> Unit,  // required
    modifier: Modifier = Modifier,
    colors: TabRowColors = TabRowDefaults.tabRowColors(),
    minWidth: Dp = TabRowDefaults.TabRowMinWidth,
    maxWidth: Dp = TabRowDefaults.TabRowMaxWidth,
    height: Dp = TabRowDefaults.TabRowHeight,
    cornerRadius: Dp = TabRowDefaults.TabRowCornerRadius,
    itemSpacing: Dp = 9.dp,
    contentAlignment: Alignment = Alignment.Center,
    listState: LazyListState? = null,
    interactionSource: MutableInteractionSource? = null,
    indication: Indication? = null,
)
```

- `tabs` — The text to be displayed in the [TabRow].
- `selectedTabIndex` — The selected tab index of the [TabRow].
- `onTabSelected` — The callback when a tab is selected.
- `modifier` — The modifier to be applied to the [TabRow].
- `colors` — The colors of the [TabRow].
- `minWidth` — The minimum width of the tab in [TabRow].
- `maxWidth` — The maximum width of the tab in [TabRow].
- `height` — The height of the [TabRow].
- `cornerRadius` — The round corner radius of the tab in [TabRow].
- `itemSpacing` — The spacing between tabs in [TabRow].
- `contentAlignment` — The content alignment of the tab in [TabRow].
- `listState` — The [LazyListState] to be used for the [TabRow].
- `interactionSource` — The [MutableInteractionSource] to be used for the [TabRow].
- `indication` — The [Indication] to be used for the [TabRow].

**TabRowDefaults**


```kotlin
TabRowDefaults.tabRowColors(
    backgroundColor: Color = MiuixTheme.colorScheme.surface,
    contentColor: Color = MiuixTheme.colorScheme.onSurfaceVariantSummary,
    selectedBackgroundColor: Color = MiuixTheme.colorScheme.surfaceContainer,
    selectedContentColor: Color = MiuixTheme.colorScheme.onBackground,
)
```

- `TabRowHeight = 42.dp`
- `TabRowWithContourHeight = 45.dp`
- `TabRowCornerRadius = 12.dp`
- `TabRowWithContourCornerRadius = 8.dp`
- `TabRowMinWidth = 76.dp`
- `TabRowWithContourMinWidth = 62.dp`
- `TabRowMaxWidth = 98.dp`
- `TabRowWithContourMaxWidth = 84.dp`

**TabRowColors** (data class) ⚠️ 4/4 constructor params are `private val` and **cannot be read from an instance**; these names are only usable as named arguments to the factory functions above.

**Traps**

- 🔴 The maxWidth parameter (and its default TabRowMaxWidth = 98.dp) actually clamps nothing. Entering the `idealWidth > maxWidth` branch in calculateTabWidth already presupposes that `totalMaxWidth < availableWidth` holds, so it always returns idealWidth, and the `else maxWidth` line is an unreachable branch. Result: the tab width has only a lower bound, no upper bound, and always splits to fill the container — placing two or three tabs on a wide screen gives giant tabs hundreds of dp wide; passing maxWidth won't stop it, and you can only wrap the TabRow in a widthIn yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:494`)
- 🟡 The modifier is sandwiched inside `Modifier.fillMaxWidth().then(modifier).height(height)`. Writing `.height(...)` in the modifier is overridden by the trailing height parameter, and writing `.width(...)` is interfered with by the leading fillMaxWidth — to change the size use the height parameter and an outer container.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:105`)
- 🟡 There is one interactionSource for the whole TabRow, passed to every TabItem. Once you explicitly pass one, pressing any tab makes all tabs show press feedback simultaneously. The default null (each selectable builds its own internally) is the normal behavior.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:181`)
- ⚪ indication defaults to null, so there is no ripple by default. This is a deliberate performance tradeoff — only when you pass indication is a squircleClip (an off-screen layer) added.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:366`)
- ⚪ The selected indicator is placed directly at `selectedTabIndex * (tabWidth + spacing) - scrollOffset`, with no animation, so switching is a hard jump. For a sliding animation use TabRowWithContour.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:155`)

**Spec** height 42.dp (TabRowDefaults.TabRowHeight) · corner_radius 12.dp · min_width 76.dp (the only width constraint that actually takes effect) · max_width 98.dp (declared value, does not actually take effect, see above) · item_spacing 9.dp (a default literal, not in Defaults) · item unselected has a 1.dp squircle outline, selected has no outline; horizontal inner padding 12.dp; font size body1; maxLines=1 + Ellipsis

**State** Purely controlled (selectedTabIndex + onTabSelected). The internal LazyListState can be passed in (the listState parameter); if not passed it is built internally. The selected item auto-scrolls to center: the first time uses scrollToItem for an instant jump, afterward uses animateScrollToItem. The horizontal remaining scroll amount is entirely consumed by a NestedScrollConnection while the vertical is passed through unchanged, so scrolling the TabRow to its end doesn't drag the outer horizontal, but the outer vertical list still scrolls normally.

**vs Material3** Corresponds to material3's TabRow/ScrollableTabRow + PrimaryTabRow family, but the form is completely different. M3 is "an underline indicator + text tabs," while Miuix is an iOS/MIUI-style segmented control (the selected item gets a rounded background block). M3 uses a tabs slot + Tab child components, while Miuix takes a `List<String>` directly and cannot customize the content of an individual tab (there is no entry for an icon or a custom composable).

**Compilable examples** [`docs/demo/src/commonMain/kotlin/TabRowDemo.kt:44`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TabRowDemo.kt#L44) · [`example/shared/src/commonMain/kotlin/component/TabRowSection.kt:37`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/TabRowSection.kt#L37)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:84`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt#L84)</sub>

## TabRowWithContour  ·  basic component

A segmented tab bar with an outer frame — compared with TabRow it adds a background frame and inset, and the selected indicator has a 200ms sliding animation. The parameter list is word-for-word identical to TabRow, only the defaults differ.

> A [TabRowWithContour] with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.TabRowWithContour

@Composable
fun TabRowWithContour(
    tabs: List<String>,  // required
    selectedTabIndex: Int,  // required
    onTabSelected: (Int) -> Unit,  // required
    modifier: Modifier = Modifier,
    colors: TabRowColors = TabRowDefaults.tabRowColors(),
    minWidth: Dp = TabRowDefaults.TabRowWithContourMinWidth,
    maxWidth: Dp = TabRowDefaults.TabRowWithContourMaxWidth,
    height: Dp = TabRowDefaults.TabRowWithContourHeight,
    cornerRadius: Dp = TabRowDefaults.TabRowWithContourCornerRadius,
    itemSpacing: Dp = 5.dp,
    contentAlignment: Alignment = Alignment.Center,
    listState: LazyListState? = null,
    interactionSource: MutableInteractionSource? = null,
    indication: Indication? = null,
)
```

- `tabs` — The text to be displayed in the [TabRow].
- `selectedTabIndex` — The selected tab index of the [TabRow].
- `onTabSelected` — The callback when a tab is selected.
- `modifier` — The modifier to be applied to the [TabRow].
- `colors` — The colors of the [TabRow].
- `minWidth` — The minimum width of the tab in [TabRow].
- `maxWidth` — The maximum width of the tab in [TabRow].
- `height` — The height of the [TabRow].
- `cornerRadius` — The round corner radius of the tab in [TabRow].
- `itemSpacing` — The spacing between tabs in [TabRow].
- `contentAlignment` — The content alignment of the tab in [TabRow].
- `listState` — The [LazyListState] to be used for the [TabRow].
- `interactionSource` — The [MutableInteractionSource] to be used for the [TabRow].
- `indication` — The [Indication] to be used for the [TabRow].

**Traps**

- 🔴 It shares the same calculateTabWidth as TabRow, so maxWidth (default TabRowWithContourMaxWidth = 84.dp) likewise never takes effect, and tabs always split to fill.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:494`)
- ⚪ There are four differences from TabRow: an extra outer frame inset by 5.dp (outer corner radius = cornerRadius + 5.dp); the indicator slides with Animatable + tween(200, LinearEasing) rather than jumping hard; the item font size is body2 whereas TabRow's is body1, and the item has no extra horizontal 12.dp padding; TabItemWithContour also does not draw TabRow's "unselected 1.dp squircle outline" (TabRow.kt:360-364 vs 409-429). The rest (width calculation, center scrolling, nested scroll consuming the horizontal) is all the same — which to pick depends only on whether you want an outer frame and a sliding animation.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:226`)
- ⚪ The outer BoxWithConstraints has no background (TabRow does); the background is drawn on the inner layer. So passing it `Modifier.background(...)` lands differently than with TabRow.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:229`)

**Spec** height 45.dp · corner_radius 8.dp (outer-frame corner radius = 8 + 5 = 13.dp) · contour_padding 5.dp (a hard-coded literal, not configurable) · min_width 62.dp · max_width 84.dp (declared value, does not actually take effect) · item_spacing 5.dp · indicator_anim tween(200ms, LinearEasing); the first placement uses snapTo, only afterward animateTo

**State** The same controlled model as TabRow, plus an extra internal Animatable driving the indicator displacement and a lastSettledSelectedTabIndex used to distinguish "first placement" from "subsequent switch."

**vs Material3** Same as TabRow — M3 has no framed segmented-control counterpart; the closest is SingleChoiceSegmentedButtonRow, but that is button-group semantics, not tabs.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/TabRowDemo.kt:55`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TabRowDemo.kt#L55) · [`example/shared/src/commonMain/kotlin/component/TabRowSection.kt:58`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/TabRowSection.kt#L58)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:209`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt#L209)</sub>

## Top-level properties & CompositionLocals (1)

- `LocalNavigationBarDisplayMode = compositionLocalOf { … }`  <sub>[`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt:558`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NavigationBar.kt#L558)</sub>

## Public types in this topic (13)

- `BreadcrumbBarDefaults` **object** · `import top.yukonga.miuix.kmp.basic.BreadcrumbBarDefaults`
- `BreadcrumbItem(path: String, text: String?)` **data class** (required: path) · `import top.yukonga.miuix.kmp.basic.BreadcrumbItem`
- `FloatingActionButtonDefaults` **object** · `import top.yukonga.miuix.kmp.basic.FloatingActionButtonDefaults`
- `FloatingNavigationBarDefaults` **object** · `import top.yukonga.miuix.kmp.basic.FloatingNavigationBarDefaults`
- `FloatingToolbarDefaults` **object** · `import top.yukonga.miuix.kmp.basic.FloatingToolbarDefaults`
- `NavigationBarDefaults` **object** · `import top.yukonga.miuix.kmp.basic.NavigationBarDefaults`
- `NavigationBarDisplayMode` **enum** — IconAndText, IconOnly, IconWithSelectedLabel · `import top.yukonga.miuix.kmp.basic.NavigationBarDisplayMode`
- `NavigationItem(label: String, icon: ImageVector)` **data class** (required: label, icon) · `import top.yukonga.miuix.kmp.basic.NavigationItem`
- `NavigationRailDefaults` **object** · `import top.yukonga.miuix.kmp.basic.NavigationRailDefaults`
- `NavigationRailState(initialValue: NavigationRailValue)` **class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.basic.NavigationRailState`
- `NavigationRailValue` **enum** — Collapsed, Expanded · `import top.yukonga.miuix.kmp.basic.NavigationRailValue`
- `SearchBarDefaults` **object** · `import top.yukonga.miuix.kmp.basic.SearchBarDefaults`
- `TabRowDefaults` **object** · `import top.yukonga.miuix.kmp.basic.TabRowDefaults`

