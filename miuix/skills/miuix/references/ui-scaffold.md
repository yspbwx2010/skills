# Scaffold & containers

Page skeleton: Scaffold, TopAppBar, Card, Surface, dividers, pull-to-refresh, scrollbar, BasicComponent. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## BasicComponent  ·  basic component

The layout skeleton of the entire Miuix list-item/settings-item system (all of miuix-preference is built on it); not a 'visible component'. The structure is [start slot] 8dp [title/summary or arbitrary content] 8dp [end slot], with an optional bottomAction below.

> A basic component with Miuix style. Widely used in other extension components.

```kotlin
import top.yukonga.miuix.kmp.basic.BasicComponent

@Composable
fun BasicComponent(
    modifier: Modifier = Modifier,
    title: String? = null,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    startAction: @Composable (() -> Unit)? = null,
    endActions: @Composable (RowScope.() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    onClick: (() -> Unit)? = null,
    onClickLabel: String? = null,
    role: Role? = null,
    holdDownState: Boolean = false,
    enabled: Boolean = true,
    interactionSource: MutableInteractionSource? = null,
)
```

- `modifier` — The modifier to be applied to the [BasicComponent].
- `title` — The title of the [BasicComponent].
- `titleColor` — The color of the title.
- `summary` — The summary of the [BasicComponent].
- `summaryColor` — The color of the summary.
- `startAction` — The [Composable] content on the start side of the [BasicComponent].
- `endActions` — The [Composable] content on the end side of the [BasicComponent].
- `bottomAction` — The [Composable] content at the bottom of the [BasicComponent].
- `insideMargin` — The margin inside the [BasicComponent].
- `onClick` — The callback when the [BasicComponent] is clicked.
- `onClickLabel` — Optional label describing the click action for accessibility services.
- `role` — The semantic [Role] of the [BasicComponent] for accessibility services.
- `holdDownState` — Used to determine whether it is in the pressed state.
- `enabled` — Whether the [BasicComponent] is enabled.
- `interactionSource` — The [MutableInteractionSource] for the [BasicComponent].   The value should remain null or non-null for the lifetime of this component;   switching across recompositions will allocate a new internal source and lose pending interactions.

**BasicComponentDefaults**


```kotlin
BasicComponentDefaults.titleColor(
    color: Color = MiuixTheme.colorScheme.onBackground,
    disabledColor: Color = MiuixTheme.colorScheme.disabledOnSecondaryVariant,
)
```


```kotlin
BasicComponentDefaults.summaryColor(
    color: Color = MiuixTheme.colorScheme.onSurfaceVariantSummary,
    disabledColor: Color = MiuixTheme.colorScheme.disabledOnSecondaryVariant,
)
```

- `InsideMargin = PaddingValues(16.dp)`

**BasicComponentColors** (data class) 

**Traps**

- 🔴 AGENTS.md:185 says it's a '2:5:3 weighted distribution', but there is no 2:5:3 in the code at all. The current implementation is: start is measured with the full maxWidth and has no cap; end goes through maxIntrinsicWidth and is hard-capped at 6/10 of the remaining width; center takes what's left. Don't compute layout results from 2:5:3.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt:217`)
- 🔴 The endActions slot is measured with maxIntrinsicWidth. Putting a component that doesn't support intrinsic measurement (LazyRow/LazyColumn and the like) into it throws outright. The end slot should only hold things with a computable intrinsic width, like switches, arrows, and short text.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt:216`)
- 🔴 startAction has no width cap at all (measured with the full maxWidth). The design assumes it's an icon or a small avatar; putting a long Text into it eats the whole row, squeezing center to 0 width and stacking the text vertically one character at a time.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt:211`)
- 🟡 heightIn(min = 56.dp) and fillMaxWidth() are both placed after modifier and are forced: a list item always fills the width and is at least 56.dp tall, and can't be made into a wrap-content inline element.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt:161`)
- 🟡 The custom Layout guards height against Constraints.Infinity but not width (layout(width = maxWidth, ...) uses maxWidth directly). Putting BasicComponent in a horizontally scrollable parent (horizontalScroll / LazyRow) yields an infinite-width constraint. This path has no guard.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt:236`)
- 🟡 The convenience overload's title/summary take only the fontSize from textStyles (title additionally hardcodes FontWeight.Medium), not the whole TextStyle —— properties like lineHeight in headline1/body2 won't take effect. For full typography control switch to the overload with a content slot.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt:92`)
- ⚪ The KDoc explicitly requires interactionSource to stay 'always null' or 'always non-null' over the component's lifecycle; switching midway reallocates the internal source and drops unfinished interactions.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt:55`)
- ⚪ When both start and end are null it takes a fast path (a plain Column), bypassing the custom Layout and intrinsic measurement entirely. Only when the two side slots are actually needed do you pay the cost of intrinsic measurement.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt:167`)

**Spec** min_height 56.dp (heightIn, forced) · inside_margin PaddingValues(16.dp) · column_gap 8.dp (hardcoded, not configurable) · end_cap the end slot takes at most 60% of 'the width remaining after deducting start and the gaps', and shrinks by intrinsic (if the content isn't wide it doesn't take the space) · bottom_gap 8.dp between bottomAction and the main row

**State** Purely stateless. onClick is nullable; when null or enabled=false no clickable is installed. clickableModifier is cached with remember, keyed on the boolean onClick != null rather than the lambda itself (the lambda is held by rememberUpdatedState), so a freshly created lambda each frame doesn't rebuild the Modifier chain. holdDownState goes through HoldDownObserver. The three columns are each vertically centered, and end sticks to the right via placeRelative (auto-mirrored in RTL).

**vs Material3** Corresponds to material3.ListItem. Differences: Miuix uses a custom Layout + intrinsic measurement for the three-column distribution (AGENTS.md explicitly forbids changing it to Row + weight(1f); a past change caused text to stack vertically one character at a time when start/end overflowed); no ListItemColors multi-slot coloring, only titleColor/summaryColor; none of the leadingContent/trailingContent/overlineContent/supportingContent naming.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt:40`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt#L40) · [`docs/demo/src/commonMain/kotlin/PullToRefreshDemo.kt:73`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/PullToRefreshDemo.kt#L73) · [`docs/demo/src/commonMain/kotlin/SearchBarDemo.kt:80`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SearchBarDemo.kt#L80) · [`example/shared/src/commonMain/kotlin/IconPage.kt:195`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/IconPage.kt#L195)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt:59`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt#L59)</sub>

## BasicComponent  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A basic component with Miuix style. Widely used in other extension components.

```kotlin
import top.yukonga.miuix.kmp.basic.BasicComponent

@Composable
fun BasicComponent(
    modifier: Modifier = Modifier,
    startAction: @Composable (() -> Unit)? = null,
    endActions: @Composable (RowScope.() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    onClick: (() -> Unit)? = null,
    onClickLabel: String? = null,
    role: Role? = null,
    holdDownState: Boolean = false,
    enabled: Boolean = true,
    interactionSource: MutableInteractionSource? = null,
    content: @Composable ColumnScope.() -> Unit,  // required
)
```

- `modifier` — The modifier to be applied to the [BasicComponent].
- `startAction` — The [Composable] content on the start side of the [BasicComponent].
- `endActions` — The [Composable] content on the end side of the [BasicComponent].
- `bottomAction` — The [Composable] content at the bottom of the [BasicComponent].
- `insideMargin` — The margin inside the [BasicComponent].
- `onClick` — The callback when the [BasicComponent] is clicked.
- `onClickLabel` — Optional label describing the click action for accessibility services.
- `role` — The semantic [Role] of the [BasicComponent] for accessibility services.
- `holdDownState` — Used to determine whether it is in the pressed state.
- `enabled` — Whether the [BasicComponent] is enabled.
- `interactionSource` — The [MutableInteractionSource] for the [BasicComponent].   The value should remain null or non-null for the lifetime of this component;   switching across recompositions will allocate a new internal source and lose pending interactions.
- `content` — The content of the [BasicComponent].

**BasicComponentDefaults**


```kotlin
BasicComponentDefaults.titleColor(
    color: Color = MiuixTheme.colorScheme.onBackground,
    disabledColor: Color = MiuixTheme.colorScheme.disabledOnSecondaryVariant,
)
```


```kotlin
BasicComponentDefaults.summaryColor(
    color: Color = MiuixTheme.colorScheme.onSurfaceVariantSummary,
    disabledColor: Color = MiuixTheme.colorScheme.disabledOnSecondaryVariant,
)
```

- `InsideMargin = PaddingValues(16.dp)`

**BasicComponentColors** (data class) 

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt:40`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt#L40) · [`docs/demo/src/commonMain/kotlin/PullToRefreshDemo.kt:73`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/PullToRefreshDemo.kt#L73) · [`docs/demo/src/commonMain/kotlin/SearchBarDemo.kt:80`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SearchBarDemo.kt#L80) · [`example/shared/src/commonMain/kotlin/IconPage.kt:195`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/IconPage.kt#L195)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt:126`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt#L126)</sub>

## Card  ·  basic component

A rounded-corner container with two overloads: one with no input and one with onClick/onLongPress. Default padding is 0; it is often used as the shell around a list item, wrapping a BasicComponent.

> A [Card] component with Miuix style.
> Card contain content and actions that relate information about a subject.
> 
> This [Card] does not handle input events

```kotlin
import top.yukonga.miuix.kmp.basic.Card

@Composable
fun Card(
    modifier: Modifier = Modifier,
    cornerRadius: Dp = CardDefaults.CornerRadius,
    insideMargin: PaddingValues = CardDefaults.InsideMargin,
    colors: CardColors = CardDefaults.defaultColors(),
    content: @Composable ColumnScope.() -> Unit,  // required
)
```

- `modifier` — The modifier to be applied to the [Card].
- `cornerRadius` — The corner radius of the [Card].
- `insideMargin` — The margin inside the [Card].
- `colors` — [CardColors] that will be used to resolve the color(s) used for the [Card].
- `content` — The [Composable] content of the [Card].

**CardDefaults**


```kotlin
CardDefaults.defaultColors(
    color: Color = MiuixTheme.colorScheme.surfaceContainer,
    contentColor: Color = MiuixTheme.colorScheme.onSurfaceContainer,
)
```

- `CornerRadius = 16.dp`
- `InsideMargin = PaddingValues(0.dp)`

**CardColors** (data class) 

**Traps**

- 🔴 insideMargin defaults to PaddingValues(0.dp), not 16.dp. Dropping a Text into a Card per M3 intuition makes it hug the edge. This is deliberate (it usually holds a BasicComponent/Preference that carries its own 16.dp padding), but placing custom content directly requires passing insideMargin yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Card.kt:195`)
- 🔴 The clickable overload's pressFeedbackType defaults to None and showIndication defaults to false —— meaning a Card given an onClick has no visual feedback on tap by default. For a sink animation pass pressFeedbackType = PressFeedbackType.Sink (or Tilt); for an alpha overlay pass showIndication = true; the two are independent channels.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Card.kt:92`)
- 🟡 The two overloads share exactly the same leading parameters and all have defaults, so `Card { }` resolves to the no-input overload (Kotlin picks the more specific, fewer-parameter overload). Passing any named parameter unique to the interactive overload (any one of pressFeedbackType / showIndication / holdDownState / onClick / onLongPress) resolves to the interactive overload. But only onClick and onLongPress actually make it clickable —— Card.kt:118 `isClickable = hasOnClick || hasLongPress`, so writing only showIndication = true gives a Card that took the interactive overload yet installs no combinedClickable, and tapping it does nothing.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Card.kt:87`)
- 🟡 Press feedback uses pressable(delay = null), skipping Pressable's default 150ms TAP_INDICATION_DELAY (that delay exists to distinguish 'press' from 'start scrolling'). Put a Card with Sink/Tilt in a scrollable list and swiping a finger across it triggers the sink animation immediately.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Card.kt:140`)

**Spec** corner 16.dp squircle · inside_margin PaddingValues(0.dp) (no padding by default) · colors surfaceContainer / onSurfaceContainer

**State** Purely stateless. onClick / onLongPress are both nullable; when both are null no combinedClickable is installed. holdDownState goes through HoldDownObserver. Physical feedback (Sink/Tilt) is attached to the card's outer modifier, and the alpha overlay is attached to the inner Column.

**vs Material3** Corresponds to material3.Card / Card(onClick=). Differences: no elevation/border/CardColors 4-color system (only color+contentColor); a tap has no ripple and no feedback by default; default contentPadding is 0 (M3 is also 0, but M3's ListItem is not); adds the pressFeedbackType physical-deformation feedback.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/CardDemo.kt:42`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/CardDemo.kt#L42) · [`docs/demo/src/commonMain/kotlin/DividerDemo.kt:46`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/DividerDemo.kt#L46) · [`docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt:48`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt#L48) · [`docs/demo/src/commonMain/kotlin/FloatingToolbarDemo.kt:50`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingToolbarDemo.kt#L50)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Card.kt:50`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Card.kt#L50)</sub>

## Card  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [Card] component with Miuix style.
> Card contain contain content and actions that relate information about a subject.
> 
> This [Card] handles input events

```kotlin
import top.yukonga.miuix.kmp.basic.Card

@Composable
fun Card(
    modifier: Modifier = Modifier,
    cornerRadius: Dp = CardDefaults.CornerRadius,
    insideMargin: PaddingValues = CardDefaults.InsideMargin,
    colors: CardColors = CardDefaults.defaultColors(),
    pressFeedbackType: PressFeedbackType = PressFeedbackType.None,
    showIndication: Boolean = false,
    holdDownState: Boolean = false,
    onClick: (() -> Unit)? = null,
    onLongPress: (() -> Unit)? = null,
    content: @Composable ColumnScope.() -> Unit,  // required
)
```

- `modifier` — The modifier to be applied to the [Card].
- `cornerRadius` — The corner radius of the [Card].
- `insideMargin` — The margin inside the [Card].
- `colors` — [CardColors] that will be used to resolve the color(s) used for the [Card].
- `pressFeedbackType` — The press feedback type of the [Card].
- `showIndication` — Whether to show indication of the [Card].
- `holdDownState` — Whether the [Card] is in a hold-down state.
- `onClick` — The callback to be invoked when the [Card] is clicked.
- `onLongPress` — The callback to be invoked when the [Card] is long pressed.
- `content` — The [Composable] content of the [Card].

**CardDefaults**


```kotlin
CardDefaults.defaultColors(
    color: Color = MiuixTheme.colorScheme.surfaceContainer,
    contentColor: Color = MiuixTheme.colorScheme.onSurfaceContainer,
)
```

- `CornerRadius = 16.dp`
- `InsideMargin = PaddingValues(0.dp)`

**CardColors** (data class) 

**Compilable examples** [`docs/demo/src/commonMain/kotlin/CardDemo.kt:42`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/CardDemo.kt#L42) · [`docs/demo/src/commonMain/kotlin/DividerDemo.kt:46`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/DividerDemo.kt#L46) · [`docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt:48`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt#L48) · [`docs/demo/src/commonMain/kotlin/FloatingToolbarDemo.kt:50`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingToolbarDemo.kt#L50)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Card.kt:87`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Card.kt#L87)</sub>

## HorizontalDivider  ·  basic component

A horizontal divider. Implemented with Canvas + drawLine (not Box + background), default 0.75.dp, color dividerLine.

> A divider is a thin line that groups content in lists and layouts.

```kotlin
import top.yukonga.miuix.kmp.basic.HorizontalDivider

@Composable
fun HorizontalDivider(
    modifier: Modifier = Modifier,
    thickness: Dp = DividerDefaults.Thickness,
    color: Color = DividerDefaults.DividerColor,
)
```

- `modifier` — the [Modifier] to be applied to this divider line.
- `thickness` — thickness of this divider line. Using [Dp.Hairline] will produce a single pixel   divider regardless of screen density.
- `color` — color of this divider line.

**Traps**

- 🟡 It hardcodes fillMaxWidth() internally and always fills the available width. For a list divider with 'left indentation', you can only add padding in the passed-in modifier (padding takes effect before fillMaxWidth); you can't narrow it via width/wrapContentWidth.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Divider.kt:34`)
- ⚪ Thickness defaults to 0.75.dp, thinner than M3's 1.dp. Using Dp.Hairline gives a density-independent single-pixel line (drawLine's start/end take thickness/2 so the stroke lands exactly on the center line, without half-pixel bleed).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Divider.kt:71`)

**Spec** thickness 0.75.dp (DividerDefaults.Thickness) · color MiuixTheme.colorScheme.dividerLine

**State** Purely stateless, @NonRestartableComposable.

**vs Material3** Corresponds to material3.HorizontalDivider. Differences: default thickness 0.75dp rather than 1dp; implemented with Canvas rather than Box, so things like Modifier.background have no effect on it.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/DividerDemo.kt:55`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/DividerDemo.kt#L55) · [`example/shared/src/commonMain/kotlin/TextStylePage.kt:124`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/TextStylePage.kt#L124) · [`example/shared/src/commonMain/kotlin/component/BlurSection.kt:177`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BlurSection.kt#L177)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Divider.kt:30`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Divider.kt#L30)</sub>

## HorizontalScrollBar  ·  basic component

A horizontal scrollbar; its parameter list is word-for-word identical to VerticalScrollBar, only the direction differs.

> A horizontal scrollbar.

```kotlin
import top.yukonga.miuix.kmp.basic.HorizontalScrollBar

@Composable
fun HorizontalScrollBar(
    adapter: ScrollBarAdapter,  // required
    modifier: Modifier = Modifier,
    reverseLayout: Boolean = false,
    trackPadding: PaddingValues = PaddingValues(0.dp),
    colors: ScrollBarColors = ScrollBarDefaults.scrollBarColors(),
    thumbWidth: Dp = ScrollBarDefaults.ThumbWidth,
    cornerRadius: Dp = ScrollBarDefaults.CornerRadius,
    thumbMinLength: Dp = ScrollBarDefaults.ThumbMinLength,
    endPadding: Dp = ScrollBarDefaults.EndPadding,
)
```

- `adapter` — [ScrollBarAdapter] that communicates with the scrollable component.
- `modifier` — The modifier to apply to this layout.
- `reverseLayout` — Reverse the direction of scrolling and layout.
- `trackPadding` — Padding applied to the track to skip content padding areas.
- `colors` — The colors of the scrollbar.
- `thumbWidth` — The width of the thumb.
- `cornerRadius` — The corner radius. [Dp.Unspecified] defaults to half of [thumbWidth].
- `thumbMinLength` — The minimum length of the thumb.
- `endPadding` — The padding from the end edge.

**Traps**

- 🟡 The value of trackPadding in the horizontal branch hard-codes LayoutDirection to Ltr (`trackPadding.calculateLeftPadding(LayoutDirection.Ltr)` / `calculateRightPadding(LayoutDirection.Ltr)`). Under an RTL layout the start/end padding is taken from the opposite side.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:248`)
- 🔴 Same as the vertical version: initially invisible (opacity 0), does not wrap content (occupies a horizontal strip of thumbWidth + endPadding×2 height), and requires opt-in.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:478`)

**Spec** same_as_vertical thumb 3.64.dp / endPadding 3.46.dp / minLength 36.dp / touch band 48.dp

**State** Same as VerticalScrollBar, a read-only adapter.

**vs Material3** No counterpart.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:175`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt#L175)</sub>

## MiuixScrollBehavior  ·  basic component

The factory for TopAppBar collapse behavior; it returns a ScrollBehavior carrying a nestedScrollConnection. To collapse the title bar, first call it in composition, then pass the state to the bar and attach the connection to the content.

> Returns a [ScrollBehavior] that adjusts its properties to affect the colors and
> height of the top app bar.
> 
> A top app bar that is set up with this [ScrollBehavior] will immediately collapse
> when the nested content is pulled up, and will expand back the collapsed area when the
> content is pulled all the way down.

```kotlin
import top.yukonga.miuix.kmp.basic.MiuixScrollBehavior

@Composable
fun MiuixScrollBehavior(
    state: TopAppBarState = rememberTopAppBarState(),
    canScroll: () -> Boolean = { true },
    snapAnimationSpec: AnimationSpec<Float>? = spring(stiffness = 2500f),
    flingAnimationSpec: DecayAnimationSpec<Float>? = rememberSplineBasedDecay(),
): ScrollBehavior
```

- `state` — the state object to be used to control or observe the top app bar's scroll   state. See [rememberTopAppBarState] for a state that is remembered across compositions.
- `canScroll` — a callback used to determine whether scroll events are to be handled by this   [ExitUntilCollapsedScrollBehavior]
- `snapAnimationSpec` — an optional [AnimationSpec] that defines how the top app bar snaps   to either fully collapsed or fully extended state when a fling or a drag scrolled it into   an intermediate position
- `flingAnimationSpec` — an optional [DecayAnimationSpec] that defined how to fling the top   app bar when the user flings the app bar itself, or the content below it

**Traps**

- 🔴 The name is upper camel case and looks like a constructor or object, but it is actually a @Composable function (the source uses @Suppress("ComposableNaming") to silence the naming warning). It cannot be written as a top-level val, nor called inside remember{} / LaunchedEffect; it must be called directly in composition scope.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:249`)
- 🟡 In the sole implementation it returns, isPinned is always false, and there is no second ScrollBehavior in the library. Although the ScrollBehavior interface exposes an isPinned member, the whole repository has no read site for it — to "pin" you can only switch to SmallTopAppBar; there is no counterpart such as pinnedScrollBehavior.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:480`)

**Spec** snap_spec spring(stiffness = 2500f) (the default snap stiffness is very high, nearly an instant return to place; this is the MIUI feel rather than Material's slow spring-back) · settle_threshold collapsedFraction < 0.5f springs back to expanded, otherwise collapses fully

**State** Each call remembers by the four-tuple (state, canScroll, snapAnimationSpec, flingAnimationSpec). state defaults to rememberTopAppBarState() (rememberSaveable, surviving configuration changes and process death). canScroll is a closure called in real time on every scroll, usable to forbid collapse under certain conditions.

**vs Material3** Corresponds to TopAppBarDefaults.exitUntilCollapsedScrollBehavior(). M3 provides three — pinned / enterAlways / exitUntilCollapsed; Miuix has only this one, and the factory function name carries neither a remember prefix nor a Defaults ownership.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/TopAppBarDemo.kt:56`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TopAppBarDemo.kt#L56) · [`example/shared/src/commonMain/kotlin/AboutPage.kt:88`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L88) · [`example/shared/src/commonMain/kotlin/ColorPage.kt:66`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L66) · [`example/shared/src/commonMain/kotlin/IconPage.kt:77`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/IconPage.kt#L77)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:250`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt#L250)</sub>

## PullToRefresh  ·  basic component

A MIUI-style pull-to-refresh container (damping curve + capsule indicator). Wrap scrollable content in it; it can cooperate with a TopAppBar's collapse behavior.

> A container that supports the "pull-to-refresh" gesture.
> 
> This composable follows a hoisted state pattern, where the logical `isRefreshing` state
> is managed by the caller (e.g., a ViewModel). It coordinates nested scrolling to enable a
> pull-to-refresh action, displays a customizable indicator, and triggers a callback when a
> refresh is requested.

```kotlin
import top.yukonga.miuix.kmp.basic.PullToRefresh

@Composable
fun PullToRefresh(
    isRefreshing: Boolean,  // required
    onRefresh: () -> Unit,  // required
    modifier: Modifier = Modifier,
    pullToRefreshState: PullToRefreshState = rememberPullToRefreshState(),
    contentPadding: PaddingValues = PaddingValues(0.dp),
    topAppBarScrollBehavior: ScrollBehavior? = null,
    color: Color = PullToRefreshDefaults.color,
    circleSize: Dp = PullToRefreshDefaults.circleSize,
    refreshTexts: List<String> = PullToRefreshDefaults.refreshTexts,
    refreshTextStyle: TextStyle = PullToRefreshDefaults.refreshTextStyle,
    onPullProgress: ((Float) -> Unit)? = null,
    content: @Composable () -> Unit,  // required
)
```

- `isRefreshing` — A boolean state representing whether a refresh is currently in progress. This state should be hoisted and is the source of truth for the refresh operation, in both directions: raising it to `true` while the indicator is idle shows the indicator programmatically (e.g. refresh-on-entry), and lowering it to `false` ends the refresh. If it is `false` when the indicator settles into its refreshing state — because it was never raised, or was raised and lowered again before the next frame — the refresh is treated as already finished and the completion animation runs immediately; a `true` that arrives later shows the indicator again.
- `onRefresh` — A lambda to be invoked when a refresh is triggered by the user. This lambda should initiate the data loading, set `isRefreshing` to `true`, and is responsible for eventually setting it back to `false` upon completion. It is not invoked when the indicator settles while `isRefreshing` is already `true`; the gesture joins the refresh in progress.
- `modifier` — The modifier to be applied to this container.
- `pullToRefreshState` — The state object that manages the UI and animations of the indicator. See [rememberPullToRefreshState].
- `contentPadding` — The padding to be applied to the content. The top padding is used to correctly offset the refresh indicator.
- `topAppBarScrollBehavior` — An optional [ScrollBehavior] for a `TopAppBar` to coordinate scrolling between the app bar and the pull-to-refresh gesture.
- `color` — The color of the refresh indicator.
- `circleSize` — The size of the refresh indicator's animated circle.
- `refreshTexts` — A list of strings representing the text shown in different states.
- `refreshTextStyle` — The [TextStyle] for the refresh indicator text.
- `onPullProgress` — A callback that observes [PullToRefreshState.fullDragProgress]: the drag progress across the full visual range from 0.0 to 1.0 (where 1.0 represents the maximum stretch distance). Unlike threshold-relative progress, this value continues to increase when the user pulls beyond the threshold. Invoked once with the current value on composition, then on every change — whether driven by a pull gesture or by the programmatic expansion and completion animations. Useful for external components that need to react to pull depth in real time.
- `content` — The content to be displayed inside the container.

**PullToRefreshDefaults**

- `color = Color.Gray`
- `circleSize = 20.dp`
- `refreshTexts = listOf(`
- `refreshTextStyle = TextStyle(`

**Traps**

- 🔴 isRefreshing is a level value that the caller must host; the component calls onRefresh only once when the pull passes the threshold. If onRefresh doesn't set isRefreshing to true, the indicator immediately retracts; if it isn't set back to false after refresh completes, it spins forever.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:159`)
- 🔴 Only a touch/touchpad press-pan gesture can start a pull session: the mouse wheel (PointerEventType.Scroll) does not change the session state, and mouse press is also explicitly excluded (`it.type != PointerType.Mouse`). On desktop and Web you can never pull out the refresh indicator with a mouse — this is deliberate (the wheel has no "release" event), but it makes people think the component is broken.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:199`)
- 🔴 The name contentPadding is misleading: it is never applied to content; its only use is `RefreshHeader(modifier = Modifier.offset(y = contentPadding.calculateTopPadding()))`, and left/right/bottom are all ignored. It is actually "the top offset of the refresh indicator," used to push the indicator below the TopAppBar.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:234`)
- 🟡 After passing topAppBarScrollBehavior, the appbar's scroll events are forwarded via PullToRefresh's arbitrating connection (when Idle the appbar collapses first, during a pull refresh takes priority, during refreshing everything is consumed). Don't additionally attach the same scrollBehavior.nestedScrollConnection to the inner list, or the same scroll amount gets consumed twice.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:174`)
- ⚪ onPullProgress is collected by snapshotFlow, and at composition it immediately calls back once with the current value (usually 0f), only then followed by real changes. Don't treat "receiving the callback" as the signal that "the user started pulling."  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:151`)
- 🟡 The default strings are four hard-coded English lines ("Pull down to refresh" / "Release to refresh" / "Refreshing..." / "Refreshed successfully"), and the default color is Color.Gray rather than a theme color. For localization and coloring you must explicitly pass refreshTexts and color.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:1027`)

**Spec** damping_curve f(x) = x - x² + x³/3, slope decreasing monotonically from 1 to 0 (1:1 tracking at the start, heavier the more you pull); f(1) = 1/3, i.e. the maximum damped displacement is one third of the window height · trigger_threshold default refreshThreshold = 0.25 → trigger displacement = 0.25 × H/3 = H/12; converted to a finger travel of about 0.091×H (about 219px on a 2400px screen) · indicator_full_scale H × (1/6) × (1/4) = H/24, i.e. a finger slide of about 0.044×H (about 104px) already fills the indicator · circle_size 20.dp · text_style 14.sp / Bold / Color.Gray · complete_anim tween(200ms, CubicBezierEasing(0f, 0f, 0f, 0.37f)) (fast first, then extremely slow)

**State** Bidirectional level sync — the external isRefreshing and the internal five-state machine (Idle / Pulling / ThresholdReached / Refreshing / RefreshComplete) drive each other, with the effect keyed by refreshState so as to re-sample the level (preventing a true→false pulse within one frame from being lost). The indicator displacement is driven by a hand-written frame loop + a spring engine, updating both dragOffset (visual) and currentTouch (the input of the damping curve) every frame, so that when the user grabs the list mid-way it doesn't jump.

**vs Material3** Corresponds to material3.PullToRefreshBox / rememberPullToRefreshState. M3's state only manages progress and animation, and the indicator is fully replaceable (an indicator slot); Miuix's indicator is four hard-coded Canvas drawings, only color/size/text are changeable, with no indicator slot. M3's Modifier.pullToRefresh also works, Miuix only has the wrapper container. Also, M3's pull is draggable with a mouse on desktop, while Miuix explicitly excludes the mouse.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/PullToRefreshDemo.kt:59`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/PullToRefreshDemo.kt#L59) · [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:136`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L136)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:125`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt#L125)</sub>

## rememberPullToRefreshState  ·  basic component

Creates and remembers the visual state object for pull-to-refresh. You only need to call it explicitly when tuning the threshold or reading the pull progress externally.

> Creates and remembers a [PullToRefreshState] across recompositions.
> 
> This state object is responsible for managing the visual aspects of the refresh indicator,
> such as its position and animation. The logical `isRefreshing` state should be hoisted and
> managed separately.

```kotlin
import top.yukonga.miuix.kmp.basic.rememberPullToRefreshState

@Composable
fun rememberPullToRefreshState(
    refreshThreshold: Float = 0.25f,
): PullToRefreshState
```

- `refreshThreshold` — An optional pull progress threshold (0.0 ~ 1.0) representing the percentage of the full damped drag range required to trigger refresh. Default is 0.25 (25%). Lower values make refresh easier to trigger; higher values require a deeper pull. 0.0 triggers on any pull, however small.

**Traps**

- 🟡 It uses remember rather than rememberSaveable — the state resets to zero after a screen rotation or process death. The isRefreshing that truly needs to survive configuration changes must be hosted by the caller with rememberSaveable (this is also why the signature splits it out).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:262`)
- 🟡 refreshThreshold is "the fraction of the full damping travel" rather than pixels or dp, and is coerceIn(0f, 1f). The trigger point is triggerProgressOffset = refreshThreshold × full damping travel, determined independently (PullToRefresh.kt:511 / 579), so passing 0f indeed triggers on any bit of pull, and lowering it lowers it without bound. The other hard-coded threshold refreshThresholdOffset (window height × 1/6 × 1/4) participates in only two places: taken as max with triggerProgressOffset as the denominator of pullProgress (effectiveThresholdOffset, PullToRefresh.kt:319-320), and taken as min to decide the indicator's full-draw point (visualProgress, PullToRefresh.kt:364-365).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:272`)
- ⚪ The threshold depends on LocalWindowInfo.current.containerSize.height, and on the first frame the window size may still be 0, at which point the threshold is 0. The code has a SideEffect and a while loop specifically to remedy this startup race; a side effect is that in scenarios where isRefreshing is set to true programmatically on the first frame, the indicator position is retroactively corrected once.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:269`)
- ⚪ The cachedNestedScrollConnection on PullToRefreshState is a public var, an internal implementation detail leaking into the public API. Don't read or write it.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:331`)

**Spec** 

**State** Holds the visual state itself (dragOffset / refreshState / three progress values), with the logical state isRefreshing externalized. Publicly readable are refreshThreshold and three derivedStateOf progress values: pullProgress (relative to the trigger threshold, saturating at 1), fullDragProgress (relative to the full range, used for onPullProgress), and visualProgress (relative to the smaller of the two thresholds, ensuring the indicator is certainly fully drawn when entering ThresholdReached).

**vs Material3** Corresponds to material3.rememberPullToRefreshState. M3's state only exposes distanceFraction and an animate method; Miuix adds threshold configuration, the five-state machine, and three progress values with distinct semantics.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/PullToRefreshDemo.kt:47`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/PullToRefreshDemo.kt#L47) · [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:76`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L76)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt:256`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/PullToRefresh.kt#L256)</sub>

## rememberScrollBarAdapter  ·  basic component

Normalizes a ScrollState / LazyListState / LazyGridState into the three quantities the scrollbar can read (total content length, current offset, viewport length). Three identically named overloads dispatch by state type.

> Create and [remember] [ScrollBarAdapter] for [ScrollState].

```kotlin
import top.yukonga.miuix.kmp.basic.rememberScrollBarAdapter

@Composable
fun rememberScrollBarAdapter(
    scrollState: ScrollState,  // required
): ScrollBarAdapter
```

**Traps**

- 🟡 A lazy list's contentSize is extrapolated as "average visible-item size × total item count," not the real total length. When item heights differ, the thumb length and position jump during scrolling — this is a fundamental compromise of lazy scrollbars and the main source of known issues. Only equal-height lists scroll smoothly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:603`)
- 🟡 The column count of a LazyGrid is inferred from the visible items (counting consecutively increasing columns until they break). A grid containing spanning items (GridItemSpan > 1) miscounts the column count, distorting the thumb ratio.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:773`)
- ⚪ Only these three states have overloads. TextFieldScrollState, PagerState, and custom scrollable components have no adapter; you must implement the ScrollBarAdapter interface yourself (four members, one of which, scrollTo, is suspend).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:62`)

**Spec** 

**State** Stateless; it just remembers a read-only view keyed by the scroll state object. The adapter does not own scrolling; scrollTo forwards to the original state (a distance smaller than one screen uses precise scrollBy, otherwise it estimates the target index via average height and then snapTo).

**vs Material3** No counterpart; corresponds to JetBrains Compose Desktop's identically named rememberScrollbarAdapter (mind the casing: Miuix is ScrollBar with two capitals).

**Compilable examples** [`example/shared/src/commonMain/kotlin/AboutPage.kt:440`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L440) · [`example/shared/src/commonMain/kotlin/ColorPage.kt:160`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L160) · [`example/shared/src/commonMain/kotlin/IconPage.kt:349`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/IconPage.kt#L349) · [`example/shared/src/commonMain/kotlin/LicensePage.kt:142`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/LicensePage.kt#L142)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:79`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt#L79)</sub>

## rememberScrollBarAdapter  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Create and [remember] [ScrollBarAdapter] for [LazyListState].

```kotlin
import top.yukonga.miuix.kmp.basic.rememberScrollBarAdapter

@Composable
fun rememberScrollBarAdapter(
    scrollState: LazyListState,  // required
): ScrollBarAdapter
```

**Compilable examples** [`example/shared/src/commonMain/kotlin/AboutPage.kt:440`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L440) · [`example/shared/src/commonMain/kotlin/ColorPage.kt:160`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L160) · [`example/shared/src/commonMain/kotlin/IconPage.kt:349`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/IconPage.kt#L349) · [`example/shared/src/commonMain/kotlin/LicensePage.kt:142`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/LicensePage.kt#L142)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:90`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt#L90)</sub>

## rememberScrollBarAdapter  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Create and [remember] [ScrollBarAdapter] for [LazyGridState].

```kotlin
import top.yukonga.miuix.kmp.basic.rememberScrollBarAdapter

@Composable
fun rememberScrollBarAdapter(
    scrollState: LazyGridState,  // required
): ScrollBarAdapter
```

**Compilable examples** [`example/shared/src/commonMain/kotlin/AboutPage.kt:440`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L440) · [`example/shared/src/commonMain/kotlin/ColorPage.kt:160`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L160) · [`example/shared/src/commonMain/kotlin/IconPage.kt:349`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/IconPage.kt#L349) · [`example/shared/src/commonMain/kotlin/LicensePage.kt:142`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/LicensePage.kt#L142)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:101`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt#L101)</sub>

## rememberTopAppBarState  ·  basic component

Creates and remembers a TopAppBarState (collapse limit, current collapse amount, cumulative content scroll amount). Normally you don't call it directly, since MiuixScrollBehavior's default parameter already does; call it explicitly only when you need to share it across components or read the collapse progress.

> Creates a [TopAppBarState] that is remembered across compositions.

```kotlin
import top.yukonga.miuix.kmp.basic.rememberTopAppBarState

@Composable
fun rememberTopAppBarState(
    initialHeightOffsetLimit: Float = -Float.MAX_VALUE,
    initialHeightOffset: Float = 0f,
    initialContentOffset: Float = 0f,
): TopAppBarState
```

- `initialHeightOffsetLimit` — the initial value for [TopAppBarState.heightOffsetLimit], which   represents the pixel limit that a top app bar is allowed to collapse when the scrollable   content is scrolled
- `initialHeightOffset` — the initial value for [TopAppBarState.heightOffset]. The initial   offset height offset should be between zero and [initialHeightOffsetLimit].
- `initialContentOffset` — the initial value for [TopAppBarState.contentOffset]

**Traps**

- ⚪ The default of initialHeightOffsetLimit is -Float.MAX_VALUE rather than 0. Before the large title's measured height is written in, collapsedFraction's denominator is this huge negative number and the ratio is almost always 0; don't treat the collapsedFraction read on the first frame as the real state.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:276`)
- ⚪ The overlappedFraction property exposed on TopAppBarState has no read site anywhere in the repository, and no component changes its appearance based on it. It is not a usable signal for "whether content covers the bar"; don't use it for visual judgments as the KDoc describes.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:356`)

**Spec** 

**State** rememberSaveable + listSaver, saving 4 values (limit / offset / contentOffset / pinnedBySmallTopAppBar); restore is backward-compatible with the old 3-element list. Note that heightOffsetLimit is a plain var, not snapshot state (changing it alone triggers no re-measure), while heightOffset is a mutableFloatStateOf whose setter does coerceIn(limit, 0f).

**vs Material3** Corresponds to material3.rememberTopAppBarState, with basically identical parameters and semantics; Miuix adds one internal pinnedBySmallTopAppBar field used for wide/narrow-screen switching.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:275`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt#L275)</sub>

## Scaffold  ·  basic component

The library's only page-root container. It uses SubcomposeLayout to hand-place 7 slots (topBar / bottomBar / fab / floatingToolbar / snackbarHost / popupHost / content), and it is also the host for all Overlay* popups and dialogs. Any page that uses an Overlay-family component must wrap a layer of it.

> A [Scaffold] component with Miuix style.
> 
> This implements the basic miuix design visual layout structure.
> 
> To show a [Snackbar], use [SnackbarHostState.showSnackbar].

```kotlin
import top.yukonga.miuix.kmp.basic.Scaffold

@Composable
fun Scaffold(
    modifier: Modifier = Modifier,
    topBar: @Composable () -> Unit = {},
    bottomBar: @Composable () -> Unit = {},
    floatingActionButton: @Composable () -> Unit = {},
    floatingActionButtonPosition: FabPosition = FabPosition.End,
    floatingToolbar: @Composable () -> Unit = {},
    floatingToolbarPosition: ToolbarPosition = ToolbarPosition.BottomCenter,
    snackbarHost: @Composable () -> Unit = {},
    popupHost: @Composable () -> Unit = { MiuixPopupHost() },
    containerColor: Color = MiuixTheme.colorScheme.surface,
    contentWindowInsets: WindowInsets = WindowInsets.systemBars.union(WindowInsets.displayCutout),
    content: @Composable (PaddingValues) -> Unit,  // required
)
```

- `modifier` — the [Modifier] to be applied to this scaffold.
- `topBar` — top app bar of the screen.
- `bottomBar` — bottom bar of the screen.
- `floatingActionButton` — floating action button of the screen.
- `floatingActionButtonPosition` — position of the floating action button.
- `floatingToolbar` — floating toolbar of the screen.
- `floatingToolbarPosition` — position of the floating toolbar.
- `snackbarHost` — component to host [Snackbar]s that are pushed to be shown via   [SnackbarHostState.showSnackbar], typically a [SnackbarHost].
- `popupHost` — component to host overlay dropdowns & [OverlayDialog]s that are pushed to be show, typically a [MiuixPopupHost].
- `containerColor` — the color used for the background of this scaffold. Use [Color.Transparent]   to have no color.
- `contentWindowInsets` — window insets to be passed to [content] slot via [PaddingValues]   params. Scaffold will take the insets into account from the top/bottom only if the [topBar]/   [bottomBar] are not present, as the scaffold expect [topBar]/[bottomBar] to handle insets   instead. Any insets consumed by other insets padding modifiers or [consumeWindowInsets] on a   parent layout will be excluded from [contentWindowInsets].
- `content` — content of the screen. The lambda receives a [PaddingValues] that should be   applied to the content root via [Modifier.padding] and [Modifier.consumeWindowInsets] to   properly offset top and bottom bars. If using [Modifier.verticalScroll], apply this modifier to   the child of the scroll, and not on the scroll itself.

**Traps**

- 🔴 The two host slots have asymmetric defaults: popupHost already mounts MiuixPopupHost() by default so popups work out of the box, whereas snackbarHost defaults to an empty lambda `{}`. Following intuition and only writing `SnackbarHostState()` + `showSnackbar()` makes nothing appear — you must explicitly write `snackbarHost = { SnackbarHost(state = snackbarHostState) }`. Worse, showSnackbar is suspend and completes via a timer inside SnackbarHost; with no host mounted that coroutine suspends forever and entries pile up in the state.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Scaffold.kt:87`)
- 🔴 The PaddingValues that the content lambda receives do not take effect automatically. Scaffold measures content with looseConstraints and place(0, 0), i.e. content fills the whole screen and sits directly under topBar. You must apply `Modifier.padding(paddingValues)` yourself (or convert the top value into a LazyColumn's contentPadding). Omitting it will definitely be obscured when there is a topBar.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Scaffold.kt:351`)
- 🟡 The content PaddingValues are computed only from topBar height / bottomBar height / contentWindowInsets; FAB and floatingToolbar do not participate at all. If you assume "adding padding means it won't be covered," the bottom will still be covered by the FAB or the floating toolbar, and you need to add extra bottom spacing yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Scaffold.kt:325`)
- 🟡 The available height for floatingToolbar is `layoutHeight - topBar height - topInset - bottomInset`, and only the bottomBar height is not subtracted. So a floating toolbar in a bottom position such as BottomCenter will sit directly on top of the NavigationBar (the FAB has dedicated avoidance logic). To have both coexist you must add bottom padding to the floatingToolbar yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Scaffold.kt:282`)
- 🟡 The floatingToolbar's y coordinate is written as `topBarPlaceable.height + topInset + position.y - 4dp`, but TopAppBar/SmallTopAppBar already carry status-bar padding internally, so their height already includes topInset — which amounts to counting the status-bar height twice. BottomStart/BottomCenter/BottomEnd work out correctly because position.y carries a negative sign that cancels it out; the Top* and Center* positions shift down by about one status-bar height, and are also unconditionally pushed up 4dp into the topBar. Correct non-bottom positions yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Scaffold.kt:290`)
- 🟡 Scaffold passes no insets to topBar / bottomBar — the contract is "each bar handles its own side." So a custom bar must write its own windowInsetsPadding, otherwise it will be crushed under the status bar / gesture bar; and Scaffold's contentWindowInsets is no longer added to content when a bar is present.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Scaffold.kt:69`)
- 🟡 When Scaffolds are nested, each level news up its own popup/dialog list, but at the same time passes the outermost one through as LocalRootPopupStates/LocalRootDialogStates; and the renderInRootScaffold of Overlay* components defaults to true. The result is "a dialog popped inside an inner Scaffold renders into the outermost Scaffold" — to confine it to the inner one you must explicitly pass renderInRootScaffold = false.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/MiuixPopupUtils.kt:176`)

**Spec** fab_spacing 12.dp (spacing between the FAB and bottomBar / screen bottom; a private constant, not configurable) · floating_toolbar_spacing 4.dp (spacing between the floating toolbar and the bottom edge; a private constant, not configurable) · container_color MiuixTheme.colorScheme.surface · content_window_insets WindowInsets.systemBars ∪ WindowInsets.displayCutout

**State** Stateless itself. snackbarHostState / the topAppBar's ScrollBehavior / the various selectedIndex are all remembered by the caller and passed into the slots. The only thing it holds is the popup/dialog list (a remembered mutableStateListOf, tied to the Scaffold lifecycle), dispatched down via 4 CompositionLocals. The PaddingValues passed to content is a mutable object whose identity never changes; value changes only trigger a re-measure of the nodes that read it and do not recompose content.

**vs Material3** Corresponds to androidx.compose.material3.Scaffold, with much of the implementation copied line by line from upstream (including the explicit copy of MutableWindowInsets). Differences: it adds the two extra slot groups floatingToolbar + floatingToolbarPosition and popupHost; FabPosition has an extra EndOverlay position (ignores bottomBar and covers it directly); snackbarHost defaults to empty (M3 is also empty, but nearly every tutorial in the M3 ecosystem writes one in, and the Miuix docs once claimed "no SnackbarHost is provided," which was misleading); no M3 contentColor parameter.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt:51`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt#L51) · [`docs/demo/src/commonMain/kotlin/FloatingToolbarDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingToolbarDemo.kt#L53) · [`docs/demo/src/commonMain/kotlin/NavigationBarDemo.kt:66`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/NavigationBarDemo.kt#L66) · [`docs/demo/src/commonMain/kotlin/OverlayDropdownMenuDemo.kt:110`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayDropdownMenuDemo.kt#L110)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Scaffold.kt:79`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Scaffold.kt#L79)</sub>

## SmallTitle  ·  basic component

A group sub-title for settings pages (the HyperOS-style bluish-gray bold small text). At 43 lines, it's the smallest component at this layer.

> A [SmallTitle] with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.SmallTitle

@Composable
fun SmallTitle(
    text: String,  // required
    modifier: Modifier = Modifier,
    textColor: Color = MiuixTheme.colorScheme.onBackgroundVariant,
    insideMargin: PaddingValues = SmallTitleDefaults.InsideMargin,
)
```

- `text` — The text to be displayed in the [SmallTitle].
- `modifier` — The modifier to be applied to the [SmallTitle].
- `textColor` — The color of the [SmallTitle].
- `insideMargin` — The margin inside the [SmallTitle].

**SmallTitleDefaults**

- `InsideMargin = PaddingValues(28.dp, 8.dp)`

**Traps**

- 🟡 There are no style / fontSize / fontWeight parameters; the style is hardcoded to MiuixTheme.textStyles.subtitle (14.sp Bold), and you can only change the color and padding. For a different font size you must forgo it and write Text directly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SmallTitle.kt:25`)
- 🟡 The default padding is PaddingValues(28.dp, 8.dp) —— the 28.dp horizontal exceeds BasicComponent/Card's 16.dp. This is so the group title left-aligns with the list-item text under the usual layout where 'the Card also has a 12.dp outer margin'; if your Card lacks that 12.dp outer margin, the title will be indented 12.dp more than the body text, and you must pass insideMargin to correct it.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SmallTitle.kt:42`)

**Spec** style MiuixTheme.textStyles.subtitle = 14.sp Bold · inside_margin PaddingValues(28.dp horizontal, 8.dp vertical) · color MiuixTheme.colorScheme.onBackgroundVariant (0xFF8C93B0 in light, a bluish gray)

**State** Purely stateless, @NonRestartableComposable.

**vs Material3** No direct counterpart. The closest is M3 ListItem's overline or a hand-drawn section header.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/SmallTitleDemo.kt:41`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SmallTitleDemo.kt#L41) · [`example/shared/src/commonMain/kotlin/ColorPage.kt:103`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L103) · [`example/shared/src/commonMain/kotlin/MainPage.kt:317`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MainPage.kt#L317) · [`example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt:112`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt#L112)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SmallTitle.kt:25`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/SmallTitle.kt#L25)</sub>

## SmallTopAppBar  ·  basic component

A fixed 52dp-tall small title bar with vertically centered content. Use it for wide screens, secondary pages, or when you don't need large-title collapse.

> A [SmallTopAppBar] with Miuix style.
> 
> The [SmallTopAppBar] can be configured with a title, a navigation icon, and action icons.

```kotlin
import top.yukonga.miuix.kmp.basic.SmallTopAppBar

@Composable
fun SmallTopAppBar(
    title: String,  // required
    modifier: Modifier = Modifier,
    color: Color = MiuixTheme.colorScheme.surface,
    titleColor: Color = MiuixTheme.colorScheme.onSurface,
    subtitle: String = "",
    subtitleColor: Color = MiuixTheme.colorScheme.onSurfaceVariantSummary,
    navigationIcon: @Composable () -> Unit = {},
    actions: @Composable RowScope.() -> Unit = {},
    scrollBehavior: ScrollBehavior? = null,
    defaultWindowInsetsPadding: Boolean = true,
    titlePadding: Dp = TopAppBarDefaults.TitlePadding,
    navigationIconPadding: Dp = TopAppBarDefaults.NavigationIconPadding,
    actionIconPadding: Dp = TopAppBarDefaults.ActionIconPadding,
    bottomContent: @Composable () -> Unit = {},
)
```

- `title` — The title of the [SmallTopAppBar].
- `modifier` — The modifier to be applied to the  [SmallTopAppBar].
- `color` — The background color of the [SmallTopAppBar].
- `titleColor` — The color of the title text.
- `subtitle` — The subtitle displayed below the title bar area.
- `subtitleColor` — The color of the subtitle text.
- `navigationIcon` — The [Composable] content that represents the navigation icon.
- `actions` — The [Composable] content that represents the action icons.
- `scrollBehavior` — The [ScrollBehavior] that controls the behavior of the [SmallTopAppBar].
- `defaultWindowInsetsPadding` — Whether to apply default window insets padding to the [SmallTopAppBar].
- `titlePadding` — The horizontal padding of the [SmallTopAppBar]'s title.
- `navigationIconPadding` — The start padding of the navigation icon.
- `actionIconPadding` — The end padding of the action icons.
- `bottomContent` — The [Composable] content displayed below the title bar area.

**Traps**

- 🔴 Although the parameters include scrollBehavior, it never collapses. The moment the component enters composition it uses SideEffect to set pinnedBySmallTopAppBar to true and zeroes out both heightOffsetLimit and heightOffset, so the collapse range is squashed to 0. Moreover scrollBehavior is never passed down to SmallTopAppBarLayout (TopAppBar.kt:213-227); there is no alpha animation in the layout, the small title is always visible and there is no fade-in. The only real use of passing scrollBehavior is to share the same behavior/state with a TopAppBar: it preserves contentOffset when switching between wide/narrow screens, so that switching back to TopAppBar lands directly on the correct collapse state. Expecting it to collapse per the TopAppBar docs is wrong.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:189`)
- 🟡 Switching the same ScrollBehavior between SmallTopAppBar and TopAppBar (wide/narrow-screen adaptation) is specifically supported: when switching back to TopAppBar it uses contentOffset to judge whether the content has already scrolled down and lands directly on fully collapsed or fully expanded, avoiding a sudden pop of the large title. Conversely, sharing one ScrollBehavior between two TopAppBars is undefined; don't do that.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:653`)
- 🟡 As with TopAppBar, the top `systemBars.only(Top)` padding still takes effect when defaultWindowInsetsPadding = false.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:1031`)

**Spec** bar_height 52.dp (TopAppBarDefaults.CollapsedHeight) · content_vertical_center the baseline is SmallTopAppBarCenterHeight / 2 = 25.dp, 1dp higher than the geometric center of 52dp — this is deliberate visual balancing, not a typo · subtitle_bottom_padding 8.dp

**State** Shares TopAppBarState with TopAppBar. It only writes, never reads: a SideEffect one-directionally pins the state. The small title's show/hide is judged under the pinned branch using `contentOffset < 0f` (because collapsedFraction is always 0 when limit==0).

**vs Material3** Corresponds to material3.TopAppBar (CenterAlignedTopAppBar is semantically closer, since the title is centered and clamped by the navigation/action icons). M3 uses `TopAppBarDefaults.pinnedScrollBehavior()` to express "no collapse," whereas Miuix flattens the state within the component itself, so whether it is pinned is determined by which component you use, not by the behavior.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayDropdownMenuDemo.kt:111`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayDropdownMenuDemo.kt#L111) · [`docs/demo/src/commonMain/kotlin/OverlayIconCascadingDropdownMenuDemo.kt:94`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayIconCascadingDropdownMenuDemo.kt#L94) · [`docs/demo/src/commonMain/kotlin/OverlayIconDropdownMenuDemo.kt:87`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayIconDropdownMenuDemo.kt#L87) · [`docs/demo/src/commonMain/kotlin/ScaffoldDemo.kt:62`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ScaffoldDemo.kt#L62)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:173`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt#L173)</sub>

## Surface  ·  basic component

The lowest-level container primitive: shape + background + optional border + optional shadow. It is the only container at this layer that still accepts an arbitrary Shape, and FloatingActionButton is built on top of it.

> A [Surface] component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.Surface

@Composable
fun Surface(
    modifier: Modifier = Modifier,
    shape: Shape = SurfaceDefaults.Shape,
    color: Color = MiuixTheme.colorScheme.surface,
    contentColor: Color = MiuixTheme.colorScheme.onSurface,
    border: BorderStroke? = null,
    shadowElevation: Dp = SurfaceDefaults.ShadowElevation,
    content: @Composable () -> Unit,  // required
)
```

- `modifier` — The modifier to be applied to the [Surface].
- `shape` — The shape of the [Surface].
- `color` — The color of the [Surface].
- `contentColor` — The content color of the [Surface].
- `border` — The border of the [Surface].
- `shadowElevation` — The shadow elevation of the [Surface].
- `content` — The [Composable] content of the [Surface].

**SurfaceDefaults**

- `Shape = RectangleShape`
- `ShadowElevation = 0.dp`

**Traps**

- 🟡 The default shape is RectangleShape, not rounded. For rounded corners you must pass shape yourself; and it uses a standard Compose Shape rather than squircle, so its outline curvature differs from Card/Button and the difference shows when mixed.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Surface.kt:150`)
- ⚪ The non-interactive overload adds semantics{isTraversalGroup = true}; the overload with onClick does not. That means a clickable Surface is not an accessibility traversal group, so screen-reader order may differ from what you expect.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Surface.kt:107`)
- ⚪ A graphicsLayer is inserted only when shadowElevation>0, with clip=false —— the shadow is drawn outside the clip. The background is drawn by background() after clip(shape), so the border is clipped by the shape. There is no tonalElevation (Miuix does no elevation tonal lightening).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Surface.kt:134`)

**Spec** shape RectangleShape (default) · shadow 0.dp (no shadow by default) · colors surface / onSurface

**State** Purely stateless. Two overloads: one without onClick and one with. Both have propagateMinConstraints=true (min constraints are passed to content) and propagate contentColor via LocalContentColor.

**vs Material3** Corresponds to material3.Surface. Differences: no tonalElevation (M3 uses it for dark-mode lightening), only shadowElevation; no checked/selected overloads.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/SurfaceDemo.kt:39`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SurfaceDemo.kt#L39)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Surface.kt:46`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Surface.kt#L46)</sub>

## Surface  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [Surface] component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.Surface

@Composable
fun Surface(
    onClick: () -> Unit,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    shape: Shape = SurfaceDefaults.Shape,
    color: Color = MiuixTheme.colorScheme.surface,
    contentColor: Color = MiuixTheme.colorScheme.onSurface,
    border: BorderStroke? = null,
    shadowElevation: Dp = SurfaceDefaults.ShadowElevation,
    interactionSource: MutableInteractionSource? = null,
    indication: Indication? = LocalIndication.current,
    content: @Composable () -> Unit,  // required
)
```

- `onClick` — The callback when the [Surface] is clicked.
- `modifier` — The modifier to be applied to the [Surface].
- `enabled` — Whether the [Surface] is enabled.
- `shape` — The shape of the [Surface].
- `color` — The color of the [Surface].
- `contentColor` — The content color of the [Surface].
- `border` — The border of the [Surface].
- `shadowElevation` — The shadow elevation of the [Surface].
- `interactionSource` — The [MutableInteractionSource] to be used for the [Surface].
- `indication` — The [Indication] to be used for the [Surface].
- `content` — The [Composable] content of the [Surface].

**SurfaceDefaults**

- `Shape = RectangleShape`
- `ShadowElevation = 0.dp`

**Compilable examples** [`docs/demo/src/commonMain/kotlin/SurfaceDemo.kt:39`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SurfaceDemo.kt#L39)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Surface.kt:89`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Surface.kt#L89)</sub>

## TopAppBar  ·  basic component

A MIUI-style collapsible large-title bar — when expanded it shows a large-font largeTitle, and as content scrolls up it collapses into a 52dp-tall small title bar. Use it when you want the collapse effect; use SmallTopAppBar for a fixed height.

> A [TopAppBar] with Miuix style that can collapse and expand based on the
> scroll position of the content below it.
> 
> The [TopAppBar] can be configured with a title, a navigation icon, and action icons.
> The large title will collapse when the content is scrolled up and expand when
> the content is scrolled down.

```kotlin
import top.yukonga.miuix.kmp.basic.TopAppBar

@Composable
fun TopAppBar(
    title: String,  // required
    modifier: Modifier = Modifier,
    color: Color = MiuixTheme.colorScheme.surface,
    titleColor: Color = MiuixTheme.colorScheme.onSurface,
    largeTitle: String = title,
    largeTitleColor: Color = MiuixTheme.colorScheme.onSurface,
    subtitle: String = "",
    subtitleColor: Color = MiuixTheme.colorScheme.onSurfaceVariantSummary,
    navigationIcon: @Composable () -> Unit = {},
    actions: @Composable RowScope.() -> Unit = {},
    scrollBehavior: ScrollBehavior? = null,
    defaultWindowInsetsPadding: Boolean = true,
    titlePadding: Dp = TopAppBarDefaults.TitlePadding,
    navigationIconPadding: Dp = TopAppBarDefaults.NavigationIconPadding,
    actionIconPadding: Dp = TopAppBarDefaults.ActionIconPadding,
    bottomContent: @Composable () -> Unit = {},
)
```

- `title` — The title of the [TopAppBar].
- `modifier` — The modifier to be applied to the  [TopAppBar].
- `color` — The background color of the [TopAppBar].
- `titleColor` — The color of the collapsed small title text.
- `largeTitle` — The large title of the [TopAppBar].
- `largeTitleColor` — The color of the expanded large title text.
- `subtitle` — The subtitle displayed below the title bar area.
- `subtitleColor` — The color of the subtitle text.
- `navigationIcon` — The [Composable] content that represents the navigation icon.
- `actions` — The [Composable] content that represents the action icons.
- `scrollBehavior` — The [ScrollBehavior] that controls the behavior of the [TopAppBar].
- `defaultWindowInsetsPadding` — Whether to apply default window insets padding to the [TopAppBar].
- `titlePadding` — The horizontal padding of the [TopAppBar]'s title & large title.
- `navigationIconPadding` — The start padding of the navigation icon.
- `actionIconPadding` — The end padding of the action icons.
- `bottomContent` — The [Composable] content displayed below the title bar area.

**TopAppBarDefaults**

- `TitlePadding = 26.dp`
- `NavigationIconPadding = 16.dp`
- `ActionIconPadding = 16.dp`
- `CollapsedHeight = 52.dp`
- `SmallTopAppBarCenterHeight = 50.dp`
- `LargeTitleBottomPadding = 4.dp`
- `SubtitleBottomPadding = 8.dp`

**Traps**

- 🔴 Just passing scrollBehavior to TopAppBar will not collapse it. You must also attach `Modifier.nestedScroll(scrollBehavior.nestedScrollConnection)` to the scrolling content (LazyColumn / verticalScroll container) so the collapse amount has a source.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:451`)
- 🟡 `defaultWindowInsetsPadding = false` only turns off the left and right sides (the Horizontal of displayCutout + navigationBars); the top `systemBars.only(Top)` padding is written outside the if and takes effect unconditionally. Fully taking over the status-bar height yourself is impossible; you can only accept this padding instead.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:806`)
- ⚪ The large title's fade-out endpoint is at 1/3 of the collapse progress (`1f - (frac * 3f).coerceIn(0,1)`), and the small title's appearance threshold is also 1/3 (`collapsedFraction * 3f >= 1f`). That is, by the time you scroll one third of the way the title switch is already complete, and only the height changes over the remaining two thirds. To "keep the large title visible the whole time" you need to enlarge the largeTitle's height yourself rather than tweak the animation.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:650`)
- ⚪ The `translationY` offset used when the small title fades in is hard-coded to 20f, and graphicsLayer's translationY unit is pixels, not dp. On a 3x-density screen the physical displacement is only one third of a 1x screen, so on high-density devices this animation is barely noticeable.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:684`)
- ⚪ The collapse limit heightOffsetLimit is written by the inner large-title Column's onSizeChanged, and it is a plain var, not snapshot state (changing it alone triggers no re-measure). Before the height is measured on the first frame this value is the initial -Float.MAX_VALUE, at which point collapsedFraction = heightOffset / -Float.MAX_VALUE is nearly always 0 (not NaN; the isNaN fallback in the measure lambda at TopAppBar.kt:867 guards heightOffset itself, not collapsedFraction). Don't read collapsedFraction on the first frame to make business decisions.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:758`)

**Spec** collapsed_height 52.dp (TopAppBarDefaults.CollapsedHeight, the bar height after collapse) · title_padding 26.dp (horizontal inner padding of the title and large title) · navigation_icon_padding 16.dp · action_icon_padding 16.dp · large_title_bottom_padding 4.dp (when there is no subtitle); with a subtitle it switches to SubtitleBottomPadding = 8.dp · title_max_width 90% of the available width (total width minus the navigation icon and action area); a private constant TITLE_WIDTH_FRACTION, not configurable · small_title_anim show folmeSpring(damping=1.0, response=0.3), hide response=0.15 (hide is twice as fast as show)

**State** A purely controlled shell + an externally hosted TopAppBarState. scrollBehavior is nullable (not passing it means a non-collapsing fixed large-title bar). During scrolling all state reads are sunk into the layout/draw phase (closures + Modifier.offset{} / graphicsLayer{} / measure lambda), so 60fps scrolling produces no recomposition; the only thing that recomposes is the derivedStateOf<Boolean> for the small title's show/hide, which flips only once or twice per scroll.

**vs Material3** Corresponds to material3's LargeTopAppBar / TopAppBar family, but the semantics differ. M3's TopAppBar is a single "title + navigation + actions" form and switches behavior via the three implementations of TopAppBarScrollBehavior (pinned/enterAlways/exitUntilCollapsed); Miuix has only one exitUntilCollapsed behavior (ScrollBehavior.isPinned is always false), merges the large/small titles into the same component, and additionally provides subtitle and bottomContent slots. M3's colors/windowInsets parameters are split here into color/titleColor/largeTitleColor/subtitleColor and a boolean switch defaultWindowInsetsPadding.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/TopAppBarDemo.kt:59`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TopAppBarDemo.kt#L59) · [`example/shared/src/commonMain/kotlin/utils/PageUtils.kt:103`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/utils/PageUtils.kt#L103)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt:100`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TopAppBar.kt#L100)</sub>

## VerticalDivider  ·  basic component

A vertical divider, the symmetric implementation of HorizontalDivider.

> A divider is a thin line that groups content in lists and layouts.

```kotlin
import top.yukonga.miuix.kmp.basic.VerticalDivider

@Composable
fun VerticalDivider(
    modifier: Modifier = Modifier,
    thickness: Dp = DividerDefaults.Thickness,
    color: Color = DividerDefaults.DividerColor,
)
```

- `modifier` — the [Modifier] to be applied to this divider line.
- `thickness` — thickness of this divider line. Using [Dp.Hairline] will produce a single pixel   divider regardless of screen density.
- `color` — color of this divider line.

**Traps**

- 🔴 It hardcodes fillMaxHeight() internally. Placed in a parent with unbounded height (e.g. a Row inside a vertical scroll, or a Row without IntrinsicSize.Min), fillMaxHeight gets no finite constraint and the divider's height collapses to 0 —— looking like it 'wasn't drawn'. The standard fix is to add Modifier.height(IntrinsicSize.Min) or an explicit height to the parent Row.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Divider.kt:57`)

**Spec** thickness 0.75.dp · color MiuixTheme.colorScheme.dividerLine

**State** Purely stateless, @NonRestartableComposable.

**vs Material3** Corresponds to material3.VerticalDivider; the same unbounded-height problem exists in M3 too; the only difference is the default thickness.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/DividerDemo.kt:76`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/DividerDemo.kt#L76) · [`example/shared/src/commonMain/kotlin/component/DialogSection.kt:317`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/DialogSection.kt#L317)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Divider.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Divider.kt#L53)</sub>

## VerticalScrollBar  ·  basic component

An independent scrollbar attached beside scrollable content (it does not wrap the content). The whole ScrollBar API is marked @ExperimentalScrollBarApi.

> A vertical scrollbar.

```kotlin
import top.yukonga.miuix.kmp.basic.VerticalScrollBar

@Composable
fun VerticalScrollBar(
    adapter: ScrollBarAdapter,  // required
    modifier: Modifier = Modifier,
    reverseLayout: Boolean = false,
    trackPadding: PaddingValues = PaddingValues(0.dp),
    colors: ScrollBarColors = ScrollBarDefaults.scrollBarColors(),
    thumbWidth: Dp = ScrollBarDefaults.ThumbWidth,
    cornerRadius: Dp = ScrollBarDefaults.CornerRadius,
    thumbMinLength: Dp = ScrollBarDefaults.ThumbMinLength,
    endPadding: Dp = ScrollBarDefaults.EndPadding,
)
```

- `adapter` — [ScrollBarAdapter] that communicates with the scrollable component.
- `modifier` — The modifier to apply to this layout.
- `reverseLayout` — Reverse the direction of scrolling and layout.
- `trackPadding` — Padding applied to the track to skip content padding areas.
- `colors` — The colors of the scrollbar.
- `thumbWidth` — The width of the thumb.
- `cornerRadius` — The corner radius. [Dp.Unspecified] defaults to half of [thumbWidth].
- `thumbMinLength` — The minimum length of the thumb.
- `endPadding` — The padding from the end edge.

**Traps**

- 🟡 The whole ScrollBar API requires opt-in (@ExperimentalScrollBarApi), though the level is WARNING not ERROR — it compiles without @OptIn, just with a warning. The annotation's own description says "has known issues and may change without notice," and it is the only component in this group without a docs page (there is no scrollbar.md under docs/components/).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/interfaces/ExperimentalScrollBarApi.kt:15`)
- 🔴 It does not wrap content but is a sibling node that occupies its own place: in measurePolicy the width is fixed at thumbWidth + endPadding×2 and the height fills constraints.maxHeight. The correct usage is to put it and the scrolling content together in a Box and align it to the edge; placing it directly in a Column takes up a row.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:464`)
- 🔴 The initial opacity is 0f, and in drawBehind `opacity <= 0f` returns directly — that is, the scrollbar is completely invisible on first entering the page; you must scroll once (or hover the mouse) for it to fade in, then it fades out after 1 second. What seems like "it didn't render" is mostly this.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:272`)
- ⚪ The fade-out animation is hard-coded as `animate(initialValue = 1f, ...)`, so when interrupted and re-triggered mid-way it first jumps back to fully opaque and then fades out, showing a flicker.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:301`)
- ⚪ Clicking the empty track area neither pages nor jumps — the gesture has two layers of filtering: first whether it falls within the 48dp touch band, then whether it falls within the thumb's pixel range; only when both pass does dragging begin.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:366`)
- 🟡 The thumb-length animation is implemented by writing snapshot state and launching a coroutine inside drawBehind (an explicit Compose anti-pattern; it only avoids entering an infinite redraw thanks to two gates, "difference ≥ 1px" and "skip if the previous animation hasn't finished"). This is one of the main reasons this component is marked experimental, and it risks blowing up on future Compose versions.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:415`)

**Spec** thumb_width 3.64.dp (animates to 6.dp on hover/drag, tween 150ms) · end_padding 3.46.dp · thumb_min_length 36.dp · corner_radius Dp.Unspecified → takes half of thumbWidth · alpha 0.1 normally, 0.3 on hover/drag (when thumbColor is Unspecified; if a color is passed explicitly it uses that color's own alpha) · fade starts fading out 1000ms after scrolling stops, fade-out takes 500ms · touch_target a 48.dp-wide touch band

**State** Holds no scroll state at all — it reads only the three quantities "total content length / current offset / viewport length" from a ScrollBarAdapter, and scrolling is still owned by the original ScrollState/LazyListState. Internally it only has visual state like opacity, isDragging, and displayedThumbLength.

**vs Material3** No counterpart (Material3 mobile has no scrollbar component). By lineage it is JetBrains Compose Desktop's Scrollbar: structures and names like ScrollBarAdapter, LazyLineContentAdapter, and firstFloatingVisibleItemIndex all come from there.

**Compilable examples** [`example/shared/src/commonMain/kotlin/AboutPage.kt:439`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L439) · [`example/shared/src/commonMain/kotlin/ColorPage.kt:159`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/ColorPage.kt#L159) · [`example/shared/src/commonMain/kotlin/IconPage.kt:348`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/IconPage.kt#L348) · [`example/shared/src/commonMain/kotlin/LicensePage.kt:141`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/LicensePage.kt#L141)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt:135`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt#L135)</sub>

## Public types in this topic (20)

- `BasicComponentDefaults` **object** · `import top.yukonga.miuix.kmp.basic.BasicComponentDefaults`
- `CardDefaults` **object** · `import top.yukonga.miuix.kmp.basic.CardDefaults`
- `DividerDefaults` **object** · `import top.yukonga.miuix.kmp.basic.DividerDefaults`
- `FabPosition` **value class** · `import top.yukonga.miuix.kmp.basic.FabPosition`
- `PullToRefreshDefaults` **object** · `import top.yukonga.miuix.kmp.basic.PullToRefreshDefaults`
- `PullToRefreshState(coroutineScope: CoroutineScope)` **class** (required: coroutineScope) · `import top.yukonga.miuix.kmp.basic.PullToRefreshState`
- `RefreshState` **interface** · `import top.yukonga.miuix.kmp.basic.RefreshState`
- `RefreshState.Idle` **object** · `import top.yukonga.miuix.kmp.basic.RefreshState`
- `RefreshState.Pulling` **object** · `import top.yukonga.miuix.kmp.basic.RefreshState`
- `RefreshState.RefreshComplete` **object** · `import top.yukonga.miuix.kmp.basic.RefreshState`
- `RefreshState.Refreshing` **object** · `import top.yukonga.miuix.kmp.basic.RefreshState`
- `RefreshState.ThresholdReached` **object** · `import top.yukonga.miuix.kmp.basic.RefreshState`
- `ScrollBarAdapter` **interface** · `import top.yukonga.miuix.kmp.basic.ScrollBarAdapter`
- `ScrollBarDefaults` **object** · `import top.yukonga.miuix.kmp.basic.ScrollBarDefaults`
- `ScrollBehavior` **interface** · `import top.yukonga.miuix.kmp.basic.ScrollBehavior`
- `SmallTitleDefaults` **object** · `import top.yukonga.miuix.kmp.basic.SmallTitleDefaults`
- `SurfaceDefaults` **object** · `import top.yukonga.miuix.kmp.basic.SurfaceDefaults`
- `ToolbarPosition` **value class** · `import top.yukonga.miuix.kmp.basic.ToolbarPosition`
- `TopAppBarDefaults` **object** · `import top.yukonga.miuix.kmp.basic.TopAppBarDefaults`
- `TopAppBarState(initialHeightOffsetLimit: Float, initialHeightOffset: Float, initialContentOffset: Float)` **class** (required: initialHeightOffsetLimit, initialHeightOffset, initialContentOffset) · `import top.yukonga.miuix.kmp.basic.TopAppBarState`

