# Display & feedback

Text, Icon, Badge, ProgressIndicator, Tooltip, Snackbar, ListPopup content. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## Badge  ·  basic component

The red-dot/number badge itself. With no content it's a 6.dp dot; with content it's a pill of at least 16.dp. It usually goes into BadgedBox's badge slot.

> A badge represents dynamic information such as a number of pending requests in a navigation bar.
> 
> Badges can be icon only or contain short text.
> 
> See [BadgedBox] for a top level layout that will properly place the badge relative to content
> such as text or an icon.

```kotlin
import top.yukonga.miuix.kmp.basic.Badge

@Composable
fun Badge(
    modifier: Modifier = Modifier,
    containerColor: Color = BadgeDefaults.containerColor,
    contentColor: Color = BadgeDefaults.contentColor,
    content: @Composable (RowScope.() -> Unit)? = null,
)
```

- `modifier` — the [Modifier] to be applied to this badge
- `containerColor` — the color used for the background of this badge
- `contentColor` — the preferred color for content inside this badge
- `content` — optional content to be rendered inside this badge

**BadgeDefaults**

- `Size = 6.dp`
- `LargeSize = 16.dp`

**Traps**

- ⚪ Badge itself does no positioning; it's just a rounded Row; the 'floating at the top-right' effect comes entirely from BadgedBox. Using Badge alone you must offset it yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Badge.kt:143`)
- ⚪ With content it overrides the entire LocalTextStyles via CompositionLocalProvider (replacing main with footnote2 + a 16.sp line height, centered). So a Text inside the badge gets a different default style than outside; this is to keep the number vertically centered under cross-platform font metrics, so don't manually change lineHeight inside it.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Badge.kt:163`)

**Spec** dot_size 6.dp (BadgeDefaults.Size, when no content) · with_content minimum 16.dp (LargeSize), plus 4.dp padding on each side · shape CircleShape · colors error background / onError text

**State** Purely stateless. content is nullable; whether there is content decides the size and padding.

**vs Material3** Corresponds to material3.Badge. The structure is essentially a port of M3 (the same layoutId/Ruler mechanism), with minor numeric tweaks.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BadgeDemo.kt:55`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BadgeDemo.kt#L55) · [`docs/demo/src/commonMain/kotlin/NavigationBarDemo.kt:77`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/NavigationBarDemo.kt#L77) · [`docs/demo/src/commonMain/kotlin/NavigationRailDemo.kt:80`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/NavigationRailDemo.kt#L80) · [`example/shared/src/commonMain/kotlin/AppContent.kt:742`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L742)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Badge.kt:133`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Badge.kt#L133)</sub>

## BadgedBox  ·  basic component

A layout container that hangs a badge at the anchor's top-right. Its own size exactly equals the anchor, and the badge is drawn overflowing beyond the bounds.

> Miuix badge box.
> 
> A badge represents dynamic information such as a number of pending requests in a navigation bar.
> 
> Badges can be icon only or contain short text.
> 
> A common use case is to display a badge with navigation bar items.

```kotlin
import top.yukonga.miuix.kmp.basic.BadgedBox

@Composable
fun BadgedBox(
    badge: @Composable BoxScope.() -> Unit,  // required
    modifier: Modifier = Modifier,
    content: @Composable BoxScope.() -> Unit,  // required
)
```

- `badge` — the badge to be displayed - typically a [Badge]
- `modifier` — the [Modifier] to be applied to this BadgedBox
- `content` — the anchor to which this badge will be positioned

**Traps**

- 🔴 The badge measurement only clears minHeight; minWidth is passed through as-is (the comment says 'we don't want the text to take more space than needed', but it only handles height). Once BadgedBox lands in a parent with minWidth > 0 (a fillMaxWidth Row/Column, or any propagateMinConstraints=true container like Card/Surface/Button), the badge is stretched to full width, so hasContent = badgePlaceable.width > 6.dp is inevitably misjudged as true, the whole set of offsets takes the wrong branch (using 12/14.dp instead of 6.dp), and the badge position shifts overall. Workaround: wrap BadgedBox in something like wrapContentWidth to break the minimum-width constraint.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Badge.kt:74`)
- 🔴 The layout's width and height are taken entirely from the anchor's size. A badge with content (height ≥16.dp, offset 12/14.dp) has a negative y and also overflows on the right, so it gets clipped by an ancestor's clipToBounds / clip(shape) (e.g. Card's squircleSurface, Surface's clip); to leave room you must add padding to the anchor yourself. The content-less 6.dp dot computes x = anchorWidth-6, y = 0, sitting exactly at the edge without overflowing, unaffected by clipping.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Badge.kt:84`)
- 🟡 It has a built-in Ruler clamping mechanism (BadgeTopRuler/BadgeEndRuler) to keep the badge from crossing a certain ancestor boundary, but the Modifier.badgeBounds() that provides the ruler is internal and unusable outside the library. When no ancestor provides one it degrades to 'no clamping'.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Badge.kt:238`)
- 🟡 'Whether there is content' is inferred from the badge's measured width > 6.dp, not from whether content is null. Adding Modifier.size(10.dp) to a content-less Badge makes it judged as having content and positioned with the 12/14.dp offset.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Badge.kt:93`)

**Spec** offset_no_content 6.dp both horizontal and vertical · offset_with_content horizontal 12.dp / vertical 14.dp · baseline forwards only the anchor's FirstBaseline/LastBaseline; text inside the badge doesn't pollute the parent's baseline alignment

**State** A purely stateless layout. The badge parameter is required and comes first; content (the anchor) is the trailing lambda.

**vs Material3** Corresponds to material3.BadgedBox. The structure shares an origin, but the M3 version's minWidth handling and offset constants may differ; the Miuix version's failure to zero out minWidth is a genuine behavioral defect.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BadgeDemo.kt:55`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BadgeDemo.kt#L55) · [`example/shared/src/commonMain/kotlin/component/BadgeSection.kt:44`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BadgeSection.kt#L44) · [`example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt:372`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/liquid/LiquidGlassNavigationBar.kt#L372)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Badge.kt:51`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Badge.kt#L51)</sub>

## CircularProgressIndicator  ·  basic component

A ring progress indicator. Passing null for progress means the indeterminate state (a rotating arc); passing 0f..1f means the determinate state.

> A [CircularProgressIndicator] with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.CircularProgressIndicator

@Composable
fun CircularProgressIndicator(
    modifier: Modifier = Modifier,
    progress: Float? = null,
    colors: ProgressIndicatorColors = ProgressIndicatorDefaults.progressIndicatorColors(),
    strokeWidth: Dp = ProgressIndicatorDefaults.DefaultCircularProgressIndicatorStrokeWidth,
    size: Dp = ProgressIndicatorDefaults.DefaultCircularProgressIndicatorSize,
)
```

- `modifier` — The modifier to be applied to the indicator.
- `progress` — The current progress value between 0.0f and 1.0f, or null for indeterminate state.
- `colors` — The colors used for the indicator.
- `strokeWidth` — The width of the circular stroke.
- `size` — The size (diameter) of the circular indicator.

**Traps**

- 🟡 size is a parameter, not decided by the modifier: `modifier.semantics{}.size(size)`, so a size written in the modifier is overridden by the trailing size.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt:161`)
- ⚪ It shares ProgressIndicatorColors with LinearProgressIndicator, so disabledForegroundColor likewise never takes effect (no enabled parameter).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt:132`)

**Spec** size 30.dp (DefaultCircularProgressIndicatorSize) · stroke_width 4.dp · indeterminate_anim rotation tween(1000ms, LinearEasing) looping infinitely + an independent sweep animation

**State** Stateless, purely controlled. progress == null means the indeterminate state.

**vs Material3** Corresponds to material3.CircularProgressIndicator, with differences the same as LinearProgressIndicator (nullable Float vs two overloads; no fine-grained parameters beyond gapSize/trackColor).

**Compilable examples** [`docs/demo/src/commonMain/kotlin/ProgressIndicatorDemo.kt:66`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ProgressIndicatorDemo.kt#L66) · [`example/shared/src/commonMain/kotlin/component/ProgressIndicatorSection.kt:59`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ProgressIndicatorSection.kt#L59)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt:124`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt#L124)</sub>

## Icon  ·  basic component

A monochrome icon container; tint defaults to LocalContentColor, so placed inside Button/Card/Badge it follows the color automatically. Four overloads: ImageVector / ImageBitmap / Painter+Color / Painter+ColorProducer.

> A [Icon] component with Miuix style.
> 
> Draws [imageVector] using [tint], with a default value of [LocalContentColor]. If [imageVector]
> has no intrinsic size, this component falls back to the recommended default size. Icon is an
> opinionated component designed to be used with single-color icons so that they can be tinted
> correctly for the component they are placed in. For multicolored icons and icons that should not
> be tinted, use [Color.Unspecified] for [tint]. For generic images that should not be tinted, and
> do not follow the recommended icon size, use [androidx.compose.foundation.Image] instead. For a
> clickable icon, see [IconButton].

```kotlin
import top.yukonga.miuix.kmp.basic.Icon

@Composable
fun Icon(
    imageVector: ImageVector,  // required
    contentDescription: String?,  // required
    modifier: Modifier = Modifier,
    tint: Color = LocalContentColor.current,
)
```

- `imageVector` — [ImageVector] to draw inside this icon
- `contentDescription` — text used by accessibility services to describe what this icon   represents. This should always be provided unless this icon is used for decorative purposes,   and does not represent a meaningful action that a user can take. This text should be localized,   such as by using [stringResource] or similar
- `modifier` — the [Modifier] to be applied to this icon
- `tint` — tint to be applied to [imageVector]. If [Color.Unspecified] is provided, then no tint   is applied.

**Traps**

- 🔴 24.dp is only the fallback when 'the painter has no intrinsic size', not a default size. ImageVector uses its own defaultWidth/defaultHeight, and Miuix's built-in icon sizes are all over the map (ArrowRight 10×16, Search 20×20, Check 26×26, Close/Sidebar 24×24, SearchCleanup 18.199984×18.199984). To unify icon sizes you must pass Modifier.size(...) yourself (the external modifier comes first and correctly overrides the fallback).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt:193`)
- 🟡 contentDescription has no default and is a required parameter; for decorative icons pass null explicitly (when null is passed the component adds no semantics).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt:55`)
- 🟡 The ColorProducer overload's parameter order is (painter, tint, contentDescription, modifier), with tint before contentDescription, the opposite of the other three overloads. Positional arguments silently pick the wrong overload or fail to compile; always name them. It keeps a resident GraphicsLayer to buy 'a tint change only redraws, not recomposes'.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt:171`)
- ⚪ Passing tint = Color.Unspecified means no tinting (use this for multicolor icons); the ColorProducer overload instead passes null to mean no tinting. The two ways of writing 'no tinting' differ.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt:131`)

**Spec** fallback_size 24.dp (only when the painter has no intrinsic size) · content_scale ContentScale.Fit

**State** Purely stateless. tint defaults to LocalContentColor.current, i.e. decided by the containing container (Button/Card/Surface/Badge all provide it).

**vs Material3** Corresponds to material3.Icon. Behavior is essentially the same, with one extra ColorProducer overload. Note Miuix's built-in icons aren't uniformly 24dp like material-icons.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BadgeDemo.kt:56`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BadgeDemo.kt#L56) · [`docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt#L53) · [`docs/demo/src/commonMain/kotlin/ButtonDemo.kt:64`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ButtonDemo.kt#L64) · [`docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt:58`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt#L58)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt#L53)</sub>

## Icon  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [Icon] component with Miuix style.
> 
> Draws [bitmap] using [tint], with a default value of [LocalContentColor]. If [bitmap] has no
> intrinsic size, this component falls back to the recommended default size. Icon is an
> opinionated component designed to be used with single-color icons so that they can be tinted
> correctly for the component they are placed in. For multicolored icons and icons that should not
> be tinted, use [Color.Unspecified] for [tint]. For generic images that should not be tinted, and
> do not follow the recommended icon size, use [androidx.compose.foundation.Image] instead. For a
> clickable icon, see [IconButton].

```kotlin
import top.yukonga.miuix.kmp.basic.Icon

@Composable
fun Icon(
    bitmap: ImageBitmap,  // required
    contentDescription: String?,  // required
    modifier: Modifier = Modifier,
    tint: Color = LocalContentColor.current,
)
```

- `bitmap` — [ImageBitmap] to draw inside this icon
- `contentDescription` — text used by accessibility services to describe what this icon   represents. This should always be provided unless this icon is used for decorative purposes,   and does not represent a meaningful action that a user can take. This text should be localized,   such as by using [stringResource] or similar
- `modifier` — the [Modifier] to be applied to this icon
- `tint` — tint to be applied to [bitmap]. If [Color.Unspecified] is provided, then no tint is   applied.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BadgeDemo.kt:56`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BadgeDemo.kt#L56) · [`docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt#L53) · [`docs/demo/src/commonMain/kotlin/ButtonDemo.kt:64`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ButtonDemo.kt#L64) · [`docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt:58`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt#L58)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt:88`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt#L88)</sub>

## Icon  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [Icon] component with Miuix style.
> 
> Draws [painter] using [tint], with a default value of [LocalContentColor]. If [painter] has no
> intrinsic size, this component falls back to the recommended default size. Icon is an
> opinionated component designed to be used with single-color icons so that they can be tinted
> correctly for the component they are placed in. For multicolored icons and icons that should not
> be tinted, use [Color.Unspecified] for [tint]. For generic images that should not be tinted, and
> do not follow the recommended icon size, use [androidx.compose.foundation.Image] instead. For a
> clickable icon, see [IconButton].

```kotlin
import top.yukonga.miuix.kmp.basic.Icon

@Composable
fun Icon(
    painter: Painter,  // required
    contentDescription: String?,  // required
    modifier: Modifier = Modifier,
    tint: Color = LocalContentColor.current,
)
```

- `painter` — [Painter] to draw inside this icon
- `contentDescription` — text used by accessibility services to describe what this icon   represents. This should always be provided unless this icon is used for decorative purposes,   and does not represent a meaningful action that a user can take. This text should be localized,   such as by using [stringResource] or similar
- `modifier` — the [Modifier] to be applied to this icon
- `tint` — tint to be applied to [painter]. If [Color.Unspecified] is provided, then no tint is   applied.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BadgeDemo.kt:56`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BadgeDemo.kt#L56) · [`docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt#L53) · [`docs/demo/src/commonMain/kotlin/ButtonDemo.kt:64`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ButtonDemo.kt#L64) · [`docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt:58`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt#L58)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt:124`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt#L124)</sub>

## Icon  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [Icon] component with Miuix style.
> 
> Draws [painter] using a [tint] produced by a [ColorProducer]. The producer is read at draw time,
> so a tint that changes frequently (animations, scroll-driven values) does not recompose this
> Icon. If [painter] has no intrinsic size, this component falls back to the recommended default
> size. Icon is an opinionated component designed to be used with single-color icons so that they
> can be tinted correctly for the component they are placed in. For multicolored icons and icons
> that should not be tinted, pass `null` for [tint]. For generic images that should not be tinted,
> and do not follow the recommended icon size, use [androidx.compose.foundation.Image] instead.
> For a clickable icon, see [IconButton].

```kotlin
import top.yukonga.miuix.kmp.basic.Icon

@Composable
fun Icon(
    painter: Painter,  // required
    tint: ColorProducer?,  // required
    contentDescription: String?,  // required
    modifier: Modifier = Modifier,
)
```

- `painter` — [Painter] to draw inside this icon
- `tint` — tint to be applied to [painter]. If null, then no tint is applied.
- `contentDescription` — text used by accessibility services to describe what this icon   represents. This should always be provided unless this icon is used for decorative purposes,   and does not represent a meaningful action that a user can take. This text should be localized,   such as by using [stringResource] or similar
- `modifier` — the [Modifier] to be applied to this icon

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BadgeDemo.kt:56`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BadgeDemo.kt#L56) · [`docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BasicComponentDemo.kt#L53) · [`docs/demo/src/commonMain/kotlin/ButtonDemo.kt:64`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ButtonDemo.kt#L64) · [`docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt:58`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt#L58)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt:171`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Icon.kt#L171)</sub>

## InfiniteProgressIndicator  ·  basic component

An "infinite" indicator of one ring + one orbiting dot, for waiting scenarios where there is no progress to speak of.

> A [InfiniteProgressIndicator] with Miuix style.
> The indicator is a circular indicator with an orbiting dot.

```kotlin
import top.yukonga.miuix.kmp.basic.InfiniteProgressIndicator

@Composable
fun InfiniteProgressIndicator(
    modifier: Modifier = Modifier,
    color: Color = Color.Gray,
    size: Dp = ProgressIndicatorDefaults.DefaultInfiniteProgressIndicatorSize,
    strokeWidth: Dp = ProgressIndicatorDefaults.DefaultInfiniteProgressIndicatorStrokeWidth,
    orbitingDotSize: Dp = ProgressIndicatorDefaults.DefaultInfiniteProgressIndicatorOrbitingDotSize,
)
```

- `modifier` — The modifier to be applied to the indicator.
- `color` — The color of the indicator.
- `size` — The size (diameter) of the circular indicator.
- `strokeWidth` — The width of the circular stroke.
- `orbitingDotSize` — The size of the orbiting dot.

**Traps**

- 🟡 It has neither a progress parameter nor a colors parameter; the color is a separate `color: Color = Color.Gray`, hard-coded and not going through the theme (there is no corresponding token in MiuixTheme.colorScheme). Under a dark theme, not passing color gives an abrupt grey.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt:222`)
- ⚪ The track radius is hard-coded as `radius - 2 * orbitingDotSize`, so changing orbitingDotSize changes both the dot's size and its orbit radius at once, and the two cannot be tuned independently.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt:253`)

**Spec** size 20.dp · stroke_width 2.dp · orbiting_dot_size 2.dp · rotation tween(800ms, LinearEasing) looping infinitely

**State** Stateless, pure animation.

**vs Material3** No counterpart. The closest is M3's indeterminate CircularProgressIndicator, but the visual language is completely different (M3 is a gapped-arc sweep, this is a full ring + orbiting dot).

**Compilable examples** [`docs/demo/src/commonMain/kotlin/ProgressIndicatorDemo.kt:74`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ProgressIndicatorDemo.kt#L74) · [`example/shared/src/commonMain/kotlin/OverscrollLoadMorePage.kt:197`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/OverscrollLoadMorePage.kt#L197) · [`example/shared/src/commonMain/kotlin/component/ProgressIndicatorSection.kt:67`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ProgressIndicatorSection.kt#L67)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt:220`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt#L220)</sub>

## LinearProgressIndicator  ·  basic component

A horizontal bar progress indicator. Passing null for progress means the indeterminate state (a looping rounded segment); passing 0f..1f means the determinate state.

> A [LinearProgressIndicator] with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.LinearProgressIndicator

@Composable
fun LinearProgressIndicator(
    modifier: Modifier = Modifier,
    progress: Float? = null,
    colors: ProgressIndicatorColors = ProgressIndicatorDefaults.progressIndicatorColors(),
    height: Dp = ProgressIndicatorDefaults.DefaultLinearProgressIndicatorHeight,
)
```

- `modifier` — The modifier to be applied to the indicator.
- `progress` — The current progress value between 0.0f and 1.0f, or null for indeterminate state.
- `colors` — The colors used for the indicator.
- `height` — The height of the indicator.

**Traps**

- 🟡 The indeterminate state actually has only one segment scrolling, not three. The phase offset in `drawIndeterminateSegment` is written as `segmentIndex * (0.45f + 0.55f)`, and the parenthesized part exactly equals 1.0, while the position is taken modulo 1, so the three loop iterations draw completely identical rectangles. Visually it appears as "one segment scrolling," and this is algebraically certain, not an illusion.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt:275`)
- 🟡 The modifier is followed by `.fillMaxWidth().height(height)` — a width constraint you write in the modifier is overridden by fillMaxWidth, and a height you write is overridden by the height parameter. To control the width, rely on the parent container.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt:72`)
- ⚪ The disabledForegroundColor parameter in progressIndicatorColors() never takes effect: none of the three indicators has an enabled parameter, and internally they all call `colors.foregroundColor(true)`. It is a color token shared over from Slider, and passing it does nothing.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt:56`)

**Spec** height 6.dp (DefaultLinearProgressIndicatorHeight) · corner_radius height / 2 (semicircles at both ends) · indeterminate_cycle tween(1250ms, LinearEasing) looping infinitely, segment width takes 45%

**State** Stateless, purely controlled. progress is coerceIn(0f, 1f). progress == null is the only way to express the indeterminate state (carrying the semantics via null, not two overloads).

**vs Material3** Corresponds to material3.LinearProgressIndicator. M3 uses two separate overloads to distinguish determinate/indeterminate (one takes `() -> Float`, one doesn't), while Miuix merges them into one with a nullable Float; M3 has parameters like gapSize/drawStopIndicator/strokeCap, while Miuix only has height and a set of colors.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/ProgressIndicatorDemo.kt:52`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ProgressIndicatorDemo.kt#L52) · [`example/shared/src/commonMain/kotlin/component/ProgressIndicatorSection.kt:38`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ProgressIndicatorSection.kt#L38)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt:49`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ProgressIndicator.kt#L49)</sub>

## ListPopupColumn  ·  basic component

The content container for a list popup: it automatically aligns all children to the same width and comes with vertical scrolling. The content of the ListPopup family should basically always be filled with it.

> A column that automatically aligns the width to the widest item.

```kotlin
import top.yukonga.miuix.kmp.basic.ListPopupColumn

@Composable
fun ListPopupColumn(
    content: @Composable () -> Unit,  // required
)
```

- `content` — The items

**Traps**

- 🟡 The width counts only the maxIntrinsicWidth of the first 8 children (MAX_ITEMS_FOR_WIDTH = 8, to avoid a full-subtree intrinsic traversal). From the 9th item on, no matter how wide, it does not participate in width calculation and gets truncated or wrapped. This limit is a private const the KDoc does not mention at all. Putting the longest item within the first 8 works around it.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:92`)
- 🟡 The viewport height = the sum of the first 8 items' heights (the modifier chain is height(IntrinsicSize.Min) + verticalScroll, and minIntrinsicHeight only sums 8 items). This is intentional for height (an 8-row-high scrollable viewport), but "item" means a direct child measurable -- a divider and a cascading-menu cloned header each count as one item, so a three-group menu with 2 dividers actually shows only 6 rows.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:138`)
- 🟡 The width is hard-clamped between 200dp..288dp, and no matter how wide the content, it cannot grow past 288dp. Passing a larger minWidth to the outer popup does not help: ListPopupContent uses a plain Box (ListPopup.kt:607, propagateMinConstraints defaults to false), the minWidth ListPopupLayout sets in .layout (ListPopupLayout.kt:214) is relaxed away by it, so when ListPopupColumn measures, constraints.minWidth is always 0 and the bounds are the literals 200dp/288dp; the minIntrinsicHeight branch (ListPopup.kt:136) directly coerceIn(200dp, 288dp) on top of that. The component also has no maxWidth parameter -- for wider you can only skip ListPopupColumn and write your own equal-width container.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:91`)
- 🔴 There is already a verticalScroll inside, so do not wrap another scroll container outside or inside. More critically, you cannot stuff a LazyColumn / LazyRow in as a child: the custom MeasurePolicy calls maxIntrinsicWidth / minIntrinsicHeight on each child, and Lazy layouts do not support intrinsic measurement, so it throws directly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:124`)

**Spec** width Adaptive, equal to the max intrinsic width of the first 8 items, clamped to 200.dp..288.dp (the lower bound is also affected by the outer minWidth) · height The sum of the first 8 children's heights; the overflow relies on the built-in verticalScroll · layout Children are laid out top to bottom in order, all stretched to the same width; placeRelative handles RTL

**State** An internal rememberScrollState manages scrolling and cannot be read or reset from outside. When the popup closes the whole subtree unloads (for both the Overlay/Window families), so on every reopen the scroll position starts from the top. There is also a Modifier.focusGroup(), the only focus handling in the entire popup system.

**vs Material3** No direct equivalent. M3's DropdownMenu is internally a plain Column + verticalScroll, with neither "all items equal width" nor an 8-row viewport rule; to get the equal-width effect in M3 you must write IntrinsicSize.Max yourself.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:79`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt#L79)</sub>

## ListPopupContent  ·  basic component

The scale/fade-in/directional-clip container for a list popup card. It is a low-level primitive for custom popup hosts -- when using the ready-made OverlayListPopup / WindowListPopup you do not need to touch it directly.

> The scaling, fading and clip-revealing container that hosts a list popup's content.

```kotlin
import top.yukonga.miuix.kmp.basic.ListPopupContent

@Composable
fun ListPopupContent(
    popupContentSize: IntSize,  // required
    onPopupContentSizeChange: (IntSize) -> Unit,  // required
    fractionProgress: () -> Float,  // required
    alphaProgress: () -> Float,  // required
    popupLayoutPosition: PopupLayoutPosition,  // required
    localTransformOrigin: TransformOrigin,  // required
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,  // required
)
```

- `popupContentSize` — The last reported size of the content, compared against the latest   measurement to avoid redundant [onPopupContentSizeChange] callbacks.
- `onPopupContentSizeChange` — Called when the measured content size changes.
- `fractionProgress` — Provides the current scale/clip-reveal fraction (0 → 1) of the popup.
- `alphaProgress` — Provides the current alpha (0 → 1) of the popup content.
- `popupLayoutPosition` — The [PopupLayoutPosition] describing the popup's spawn direction.
- `localTransformOrigin` — The transform origin local to the content used while scaling.
- `modifier` — The modifier to be applied to the popup container.
- `content` — The content of the popup.

**Traps**

- 🔴 All animation parameters are externally driven, and the component produces no progress itself. When fractionProgress returns 0 the scale is 0.15 and the clip height is 0 -- using it as a static card directly (without feeding progress) gives you something completely invisible. For static use you must pass { 1f }.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:612`)
- 🟡 The 16.dp corner and the surfaceContainer background are hardcoded in the function body, and the modifier parameter is inserted after the internal graphicsLayer and before the background -- a passed background modifier is covered by that internal background layer, so the card's appearance cannot be changed.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:604`)
- 🟡 popupContentSize and onPopupContentSizeChange are a pair of parameters that must form a closed loop: the callback happens in onGloballyPositioned, and only by storing the value back and passing it into popupContentSize does the internal "only call back when the size changed" comparison hold; breaking the loop causes a per-frame callback + recomposition storm.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:619`)
- ⚪ graphicsLayer must be written before the user modifier (a source comment cites issue #373: drawing-type modifiers written before graphicsLayer do not follow its transform). When assembling a similar container yourself, if you put graphicsLayer at the end of the chain, the background/border will not scale with it during animation.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:607`)

**Spec** corner 16.dp (hardcoded) · background MiuixTheme.colorScheme.surfaceContainer (hardcoded) · scale 0.15f + 0.85f × fraction, transform origin taken from localTransformOrigin · reveal A squircle clip band expanding along the popup direction: growing from the top when below the anchor, from the bottom when above, and from the middle toward both sides when centered; when squircle is off it degrades to a plain rounded rectangle

**State** Fully controlled, no internal state. fractionProgress / alphaProgress are passed as () -> Float rather than Float, deferring the read to the draw phase to skip recomposition -- keep this form when calling it yourself and do not unpack to Float early. popupLayoutPosition and localTransformOrigin usually come from rememberListPopupLayoutInfo.

**vs Material3** No equivalent.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:594`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt#L594)</sub>

## TooltipScope.PlainTooltip  ·  basic component

An appearance container for a simple text tooltip; it can only be written in TooltipBox's tooltip slot.

> A plain tooltip that briefly describes an anchor with a short text label, using the Miuix inverse
> surface style.

```kotlin
import top.yukonga.miuix.kmp.basic.PlainTooltip

@Composable
fun TooltipScope.PlainTooltip(
    modifier: Modifier = Modifier,
    caretShape: Shape? = null,
    maxWidth: Dp = TooltipDefaults.PlainTooltipMaxWidth,
    cornerRadius: Dp = TooltipDefaults.PlainTooltipCornerRadius,
    containerColor: Color = TooltipDefaults.plainTooltipContainerColor,
    contentColor: Color = TooltipDefaults.plainTooltipContentColor,
    insideMargin: PaddingValues = TooltipDefaults.PlainTooltipInsideMargin,
    content: @Composable () -> Unit,  // required
)
```

- `modifier` — the modifier applied to the tooltip.
- `caretShape` — when non-null, draws a caret pointing at the anchor; null (default) keeps the   Miuix caret-less style.
- `maxWidth` — the maximum width of the tooltip.
- `cornerRadius` — the corner radius of the tooltip.
- `containerColor` — the container color of the tooltip.
- `contentColor` — the content color of the tooltip.
- `insideMargin` — the margin inside the tooltip.
- `content` — the tooltip content, usually a short [Text].

**Traps**

- 🔴 It is an extension function of `TooltipScope`; calling it outside TooltipBox's tooltip slot fails to compile.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:455`)
- 🟡 caretShape defaults to null, i.e. by default there is no little caret pointing at the anchor. And it is not really a Shape parameter — it is only null-checked as a switch, and the actual caret is a hard-coded triangle Path; passing any non-null Shape gives the same triangle.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:549`)
- 🟡 The caret is drawn only when the orientation is Above or Below. With a Start/End orientation, even passing caretShape draws nothing (silently no-op).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:550`)

**Spec** max_width 200.dp · corner_radius 12.dp · inside_margin PaddingValues(horizontal = 12.dp, vertical = 8.dp) · caret_size DpSize(16.dp, 8.dp); its position is coerceIn-clamped within the corner radius so it doesn't run onto the corner

**State** Stateless. It obtains positioning and obtainAnchorBounds() via TooltipScope to decide the caret's orientation and horizontal position.

**vs Material3** Corresponds to material3.PlainTooltip (also a TooltipScope extension). M3's caret is a real Shape provided via TooltipDefaults and customizable, while Miuix's caretShape is just a boolean switch; M3's PlainTooltip has maxWidth/shape/contentColor/containerColor/tonalElevation/shadowElevation, while Miuix lacks the two elevation items.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:455`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt#L455)</sub>

## rememberListPopupLayoutInfo  ·  basic component

Computes "anchor rect + content size + positioning strategy" into the safe area, margins, transform origin, and popup direction needed to place the popup. Use it for custom popup hosts; you do not need to touch it when using ready-made components.

> Computes and remembers the [ListPopupLayoutInfo] for a list popup from its anchor and content size.

```kotlin
import top.yukonga.miuix.kmp.basic.rememberListPopupLayoutInfo

@Composable
fun rememberListPopupLayoutInfo(
    alignment: PopupPositionProvider.Align,  // required
    popupPositionProvider: PopupPositionProvider,  // required
    parentBounds: IntRect,  // required
    popupContentSize: IntSize,  // required
): ListPopupLayoutInfo
```

- `alignment` — The [PopupPositionProvider.Align] of the popup relative to the window.
- `popupPositionProvider` — The [PopupPositionProvider] that computes the popup offset and margins.
- `parentBounds` — The bounds of the anchor (parent) component in window coordinates.
- `popupContentSize` — The measured size of the popup content; [IntSize.Zero] before it is measured.

**Traps**

- 🟡 When popupContentSize is passed IntSize.Zero (not yet measured) it returns a "predicted origin" -- deriving the anchor's corresponding corner directly by alignment; only after measurement is done does it switch to a measured origin back-derived from the actual computed position. So the transformOrigin differs between the first and second frame, and caching it as a stable value shows a jump at the animation's start point.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:446`)
- 🟡 The popupLayoutPosition it returns is not a literal translation of the alignment you passed, but back-derived from the computed actual offset (comparing the popup center with the anchor center, comparing the left/right edge distances). When the popup is clamped by the boundary, or the vertical direction falls into the "center on the anchor when neither above nor below fits" branch, the back-derived result disagrees with the alignment you requested, and the animation origin changes accordingly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:512`)
- ⚪ The safe-area accounting of windowBounds is: subtract displayCutout on the left/right, statusBars on top, navigationBars + captionBar on the bottom. The top boundary does not subtract the notch (in portrait it is covered by the status bar, in landscape the notch is on the sides). The desktop captionBar also counts toward the bottom boundary, which matters when the window title bar is at the bottom.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:438`)

**Spec** outputs windowBounds (safe-area rect), popupMargin (converted to px by provider.getMargins(), the default dropdown provider is vertical 8.dp / horizontal 0.dp), effectiveTransformOrigin (window coordinates), localTransformOrigin (0..1 normalized, fed directly to graphicsLayer), popupLayoutPosition (showBelow / showAbove / isRightAligned)

**State** Pure computation + remember, no side effects, no internal mutable state. All branches recompute from the parameters and current insets; when containerSize is 0, safeTransformOrigin guards against NaN.

**vs Material3** No equivalent. M3 uses the PopupPositionProvider interface + Popup positioning itself, and does not expose animation info like the transform origin/popup direction.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:399`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt#L399)</sub>

## rememberTooltipState  ·  basic component

Creates and remembers a tooltip's show/hide state, deciding whether it is a "brief hint" or a "persistent card."

> Creates and remembers a [TooltipState].

```kotlin
import top.yukonga.miuix.kmp.basic.rememberTooltipState

@Composable
fun rememberTooltipState(
    initialIsVisible: Boolean = false,
    isPersistent: Boolean = false,
    mutatorMutex: MutatorMutex = BasicTooltipDefaults.GlobalMutatorMutex,
): TooltipState
```

- `initialIsVisible` — whether the tooltip is initially visible.
- `isPersistent` — whether the tooltip stays visible until explicitly dismissed.
- `mutatorMutex` — the [MutatorMutex] used to ensure only one tooltip is shown at a time.

**Traps**

- 🔴 isPersistent = false (the default) does not mean "it times out automatically." The timeout branch's condition is `!isPersistent && mutatePriority != UserInput`, and all gesture entries use UserInput — so a non-persistent tooltip popped by a touch long-press also doesn't time out; only programmatically calling state.show() (default MutatePriority.Default) consumes that TooltipDuration.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:202`)
- 🟡 It remembers by (isPersistent, mutatorMutex) — using an isPersistent that changes with state rebuilds the whole state and loses the current show/hide. Also, the default mutatorMutex is `BasicTooltipDefaults.GlobalMutatorMutex`, which is @ExperimentalFoundationApi; the source shields it internally with @OptIn, but if you pass this value explicitly you need to add @OptIn yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:243`)

**Spec** 

**State** Uses remember (not rememberSaveable). Under the same MutatorMutex only one tooltip is globally visible — a new show() preempts and closes the old one. isVisible remains true while the animation hasn't finished, to ensure an interrupted enter can play its exit in reverse.

**vs Material3** Corresponds to material3.rememberTooltipState(initialIsVisible, isPersistent, mutatorMutex), with basically identical signature and semantics. The difference is that Miuix's implementation forks from foundation's BasicTooltipState and restores the M3 behavior of "a persistent one is not closed when the mouse leaves the anchor."

**Compilable examples** [`docs/demo/src/commonMain/kotlin/TooltipDemo.kt:29`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TooltipDemo.kt#L29) · [`example/shared/src/commonMain/kotlin/component/TooltipSection.kt:28`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/TooltipSection.kt#L28)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:239`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt#L239)</sub>

## TooltipScope.RichTooltip  ·  basic component

A rich tooltip with a title, body, and action buttons; it can only be written in TooltipBox's tooltip slot.

> A rich tooltip that explains an anchor with an optional [title], body [text], and an optional
> [action], using the Miuix surface-container card style.

```kotlin
import top.yukonga.miuix.kmp.basic.RichTooltip

@Composable
fun TooltipScope.RichTooltip(
    modifier: Modifier = Modifier,
    title: (@Composable () -> Unit)? = null,
    action: (@Composable () -> Unit)? = null,
    caretShape: Shape? = null,
    maxWidth: Dp = TooltipDefaults.RichTooltipMaxWidth,
    cornerRadius: Dp = TooltipDefaults.RichTooltipCornerRadius,
    colors: RichTooltipColors = TooltipDefaults.richTooltipColors(),
    insideMargin: PaddingValues = TooltipDefaults.RichTooltipInsideMargin,
    text: @Composable () -> Unit,  // required
)
```

- `modifier` — the modifier applied to the tooltip.
- `title` — the optional title shown above the body.
- `action` — the optional action shown below the body.
- `caretShape` — when non-null, draws a caret pointing at the anchor; null (default) keeps the   Miuix caret-less style.
- `maxWidth` — the maximum width of the tooltip.
- `cornerRadius` — the corner radius of the tooltip.
- `colors` — the [RichTooltipColors] of the tooltip.
- `insideMargin` — the margin inside the tooltip.
- `text` — the body content of the tooltip.

**RichTooltipColors** (data class) 

**Traps**

- 🔴 It is also a `TooltipScope` extension function, and its three caretShape limitations are exactly the same as PlainTooltip's (no caret by default, Shape is just a switch, only above/below orientations supported).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:498`)
- 🔴 To make it "stay until the user acts" you must do both: use `rememberTooltipState(isPersistent = true)` for state, and pass focusable = true to TooltipBox. Doing only the former means clicking outside won't close it; doing only the latter means one popped by a touch long-press still doesn't time out (see TooltipBox), but it disappears once the mouse moves away.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:219`)

**Spec** max_width 320.dp · corner_radius 16.dp · inside_margin PaddingValues(all = 16.dp) · action_button corner radius 8.dp, inner padding horizontal 12.dp / vertical 6.dp · caret_size DpSize(16.dp, 8.dp), only Above/Below take effect

**State** No state of its own; persistence is decided by the external TooltipState(isPersistent). When persistent, dismiss() actively cancels the suspended show coroutine.

**vs Material3** Corresponds to material3.RichTooltip (the title/action/text three-slot structure is consistent). Differences are the same as PlainTooltip: the caret is just a switch, no elevation parameter; also M3's RichTooltip more commonly defaults to a persistent + focusable combination, while Miuix needs it configured by hand.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:498`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt#L498)</sub>

## RichTooltipBox  ·  basic component

A convenience wrapper around RichTooltip — it takes the three content blocks title / text / action directly and internally builds a persistent state and RichTooltip for you.

> A rich tooltip convenience that wraps [TooltipBox] + [RichTooltip] with an optional title and a
> single text action. The action invokes [onActionClick] then dismisses the tooltip.
> 
> The tooltip is persistent: trigger it via long press / hover, or hoist [state] and call
> [TooltipState.show] from the anchor's own click. It is dismissed by an outside tap, a back press,
> or the action.

```kotlin
import top.yukonga.miuix.kmp.basic.RichTooltipBox

@Composable
fun RichTooltipBox(
    text: String,  // required
    modifier: Modifier = Modifier,
    state: TooltipState = rememberTooltipState(isPersistent = true),
    title: String? = null,
    actionText: String? = null,
    onActionClick: (() -> Unit)? = null,
    enabled: Boolean = true,
    positioning: TooltipAnchorPosition = TooltipAnchorPosition.Below,
    colors: RichTooltipColors = TooltipDefaults.richTooltipColors(),
    content: @Composable () -> Unit,  // required
)
```

- `text` — the body text of the tooltip.
- `modifier` — the modifier applied to the anchor wrapper.
- `state` — the [TooltipState] controlling visibility.
- `title` — the optional title shown above the body.
- `actionText` — the optional action label.
- `onActionClick` — called when the action is clicked, before the tooltip is dismissed.
- `enabled` — whether hover / long press on the anchor shows the tooltip.
- `positioning` — the preferred [TooltipAnchorPosition] of the tooltip.
- `colors` — the [RichTooltipColors] of the tooltip.
- `content` — the anchor content.

**Traps**

- 🟡 Its state default is `rememberTooltipState(isPersistent = true)`, opposite to TooltipBox's convenience version's `isPersistent = false`. When mixing the two, note that the difference between "disappears on a tap" and "must be closed manually" comes from here.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:675`)
- 🔴 A persistent tooltip does not time out automatically (the timeout branch takes effect only for non-persistent and non-UserInput priority), so using this convenience version means you must give the user a way to close it — an action button, clicking outside (requires focusable), or an explicit state.dismiss().  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:202`)

**Spec** inherits_rich_tooltip max_width 320.dp / corner_radius 16.dp / inside_margin 16.dp

**State** Internally builds a persistent TooltipState by default, or one can be passed in externally for programmatic show/hide control.

**vs Material3** No one-to-one counterpart — M3 has only the single TooltipBox container, and the difference between rich and plain is reflected by which component you put in the tooltip slot. Miuix additionally provides this convenience shell.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/TooltipDemo.kt:58`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TooltipDemo.kt#L58) · [`example/shared/src/commonMain/kotlin/component/TooltipSection.kt:47`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/TooltipSection.kt#L47)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:672`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt#L672)</sub>

## Snackbar  ·  basic component

The default appearance of a single snackbar (message + optional action button + optional dismiss button). Usually not used directly; it is called by SnackbarHost's default content, and you write it explicitly only when customizing the appearance.

> A Snackbar is a temporary message that appears at the bottom of the screen.

```kotlin
import top.yukonga.miuix.kmp.basic.Snackbar

@Composable
fun Snackbar(
    data: SnackbarData,  // required
    modifier: Modifier = Modifier,
    cornerRadius: Dp = SnackbarDefaults.CornerRadius,
    colors: SnackbarColors = SnackbarDefaults.snackbarColors(),
    insideMargin: PaddingValues = SnackbarDefaults.InsideMargin,
)
```

- `data` — data of the [Snackbar]
- `modifier` — modifier to be applied to the [Snackbar]
- `cornerRadius` — corner radius of the [Snackbar]
- `colors` — colors of the [Snackbar]
- `insideMargin` — margin inside the [Snackbar]

**SnackbarDefaults**


```kotlin
SnackbarDefaults.snackbarColors(
    containerColor: Color = MiuixTheme.colorScheme.onSecondaryVariant,
    contentColor: Color = MiuixTheme.colorScheme.secondaryVariant,
    actionContentColor: Color = MiuixTheme.colorScheme.onPrimary,
    dismissActionContentColor: Color = MiuixTheme.colorScheme.onSurfaceContainerVariant,
    actionContainerColor: Color = MiuixTheme.colorScheme.primary,
)
```

- `CornerRadius = 16.dp`
- `InsideMargin = PaddingValues(all = 12.dp)`
- `OuterPadding = PaddingValues(start = 12.dp, end = 12.dp, top = 8.dp)`
- `ActionCornerRadius = 50.dp`
- `ActionInsideMargin = PaddingValues(horizontal = 12.dp, vertical = 0.dp)`

**SnackbarColors** (data class) 

**Traps**

- 🔴 It takes SnackbarData, not a string. When customizing content you must read values via `data.visuals.message` / `.actionLabel` / `.withDismissAction`, and call `data.performAction()` / `data.dismiss()` in the buttons to wrap up — if you don't, the suspended coroutine of showSnackbar never returns.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:392`)
- 🟡 The constructor of SnackbarDuration.Custom carries `require(durationMillis > 0)`, so passing 0 or a negative number throws rather than "disappearing immediately" or "never disappearing" (the latter uses Indefinite). Also, within the SnackbarDuration scope `Long` resolves to the sibling `data object Long`, so the source must write kotlin.Long.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:91`)
- ⚪ The shadow parameters are hard-coded (radius=10.dp / black / alpha=0.1f); there is no elevation parameter to tune.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:405`)

**Spec** corner_radius 16.dp (squircle) · inside_margin PaddingValues(all = 12.dp) · outer_padding PaddingValues(start = 12.dp, end = 12.dp, top = 8.dp) · action_button corner radius 50.dp, inner padding horizontal 12.dp / vertical 0.dp · shadow fixed radius=10.dp / black / alpha=0.1f

**State** Stateless. It provides colors.contentColor as LocalContentColor via CompositionLocalProvider, so the internal Text/Icon automatically pick up the correct foreground color.

**vs Material3** Corresponds to material3.Snackbar. M3's Snackbar also takes SnackbarData (or an overload taking action/dismissAction slots directly); the difference is that M3 has finer parameters like shape/containerColor/contentColor/actionContentColor/actionOnNewLine/elevation, while Miuix only has cornerRadius/colors/insideMargin, and elevation is not tunable.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:385`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt#L385)</sub>

## SnackbarHost  ·  basic component

The host and stack layout for snackbars — it watches the SnackbarHostState queue, plays enter/exit animations, runs the auto-dismiss timer, and handles swipe-to-dismiss. Put it in the Scaffold's snackbarHost slot.

> Host for [Snackbar]s to be shown.

```kotlin
import top.yukonga.miuix.kmp.basic.SnackbarHost

@Composable
fun SnackbarHost(
    state: SnackbarHostState,  // required
    modifier: Modifier = Modifier,
    canSwipeToDismiss: Boolean = true,
    content: @Composable (SnackbarData) -> Unit = { Snackbar(it) },
)
```

- `state` — state of the [SnackbarHost]
- `modifier` — modifier to be applied to the [SnackbarHost]
- `canSwipeToDismiss` — flag of can be dismissed by swipe of the current [SnackbarHost]
- `content` — content of the [SnackbarHost]

**Traps**

- 🔴 The auto-dismiss timer lives in SnackbarHost, not in SnackbarHostState. Without mounting SnackbarHost into composition (the Scaffold's snackbarHost defaults to an empty lambda), showSnackbar's coroutine suspends forever and entries keep piling up in the state. This is the root cause of "calling showSnackbar and nothing happens."  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:302`)
- 🔴 The parameter name is state, not hostState (the doc example writing `SnackbarHost(hostState = ...)` won't compile).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:273`)
- 🟡 It is stack-based rather than queue-based: calling showSnackbar multiple times makes several show at once (the new one is added to the head of the list + LazyColumn reverseLayout, so visually the newer is below), rather than playing them one at a time in a queue. For "show only the latest" you must dismiss the old ones yourself first.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:224`)
- ⚪ The timeout duration is adjusted by the accessibility service's calculateRecommendedTimeoutMillis (and is always reported as "with icon + with text"), so on a device with the accessibility service enabled the actual dwell time is longer than 4000/10000ms.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:255`)
- ⚪ "Logical removal" and "composition removal" are separate: dismiss only sets visible to false, and the actual removal from the list is done by the UI side after the exit animation goes idle. So the length of currentSnackbars is briefly larger than the visible entries.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:299`)

**Spec** host_bottom_padding 12.dp · duration Short 4000ms / Long 10000ms / Indefinite Long.MAX_VALUE / Custom custom (must be > 0) · swipe_threshold dismisses once the displacement exceeds half the width (positionalThreshold = distance * 0.5f) · enter slideInVertically + expandVertically(clip = false) · exit the bottommost one (index == 0) slides out, the rest use fadeOut; all with shrinkVertically(clip = false)

**State** SnackbarHostState is `remember { SnackbarHostState() }` by the caller (not rememberSaveable, not restored on process death). showSnackbar is suspend and suspends until that entry is dismissed or performAction'd, returning a SnackbarResult; therefore it must be called inside rememberCoroutineScope().launch. newestSnackbarData() / oldestSnackbarData() are suspend member functions (not extension functions).

**vs Material3** Corresponds to material3.SnackbarHost. The biggest difference is that M3's SnackbarHostState shows only one at a time (a new one cancels the old, serialized via a Mutex), whereas Miuix is a stack that can layer several at once; M3's host does only single-entry animation, while Miuix's host is internally a reverseLayout LazyColumn. M3's parameter name is hostState, Miuix's is state.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/SnackbarDemo.kt:54`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SnackbarDemo.kt#L54) · [`example/shared/src/commonMain/kotlin/AppContent.kt:404`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L404)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:272`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt#L272)</sub>

## Text  ·  basic component

A thin wrapper over BasicText; the default style is taken from LocalTextStyles.current.main (17sp). Four overloads: String/AnnotatedString × Color/ColorProducer.

> A [Text] component with Miuix style.
> 
> High level element that displays text and provides semantics / accessibility information.
> 
> The default [style] uses [LocalTextStyles.current.main]. If you are setting your own style, you
> may want to consider first retrieving the current style, and using [TextStyle.copy] to keep any
> theme defined attributes, only modifying the specific attributes you want to override.
> 
> For ease of use, commonly used parameters from [TextStyle] are also present here. The order of
> precedence is as follows:
> - If a parameter is explicitly set here (i.e, it is _not_ `null` or [TextUnit.Unspecified]), then
>   this parameter will always be used.
> - If a parameter is _not_ set, (`null` or [TextUnit.Unspecified]), then the corresponding value
>   from [style] will be used instead.
> 
> Additionally, for [color], if [color] is not set, and [style] does not have a color, then
> [LocalContentColor] will be used.

```kotlin
import top.yukonga.miuix.kmp.basic.Text

@Composable
fun Text(
    text: String,  // required
    modifier: Modifier = Modifier,
    color: Color = Color.Unspecified,
    autoSize: TextAutoSize? = null,
    fontSize: TextUnit = TextUnit.Unspecified,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight? = null,
    fontFamily: FontFamily? = null,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Clip,
    softWrap: Boolean = true,
    maxLines: Int = Int.MAX_VALUE,
    minLines: Int = 1,
    onTextLayout: ((TextLayoutResult) -> Unit)? = null,
    style: TextStyle = LocalTextStyles.current.main,
)
```

- `text` — the text to be displayed
- `modifier` — the [Modifier] to be applied to this layout node
- `color` — [Color] to apply to the text. If [Color.Unspecified], and [style] has no color set,   this will be [LocalContentColor].
- `autoSize` — Enable auto sizing for this text composable. Finds the biggest font size that   fits in the available space and lays the text out with this size. This performs multiple layout   passes and can be slower than using a fixed font size. This takes precedence over sizes defined   through [fontSize] and [style]. See [TextAutoSize].
- `fontSize` — the size of glyphs to use when painting the text. See [TextStyle.fontSize].
- `fontStyle` — the typeface variant to use when drawing the letters (e.g., italic). See   [TextStyle.fontStyle].
- `fontWeight` — the typeface thickness to use when painting the text (e.g., [FontWeight.Bold]).
- `fontFamily` — the font family to be used when rendering the text. See [TextStyle.fontFamily].
- `letterSpacing` — the amount of space to add between each letter. See   [TextStyle.letterSpacing].
- `textDecoration` — the decorations to paint on the text (e.g., an underline). See   [TextStyle.textDecoration].
- `textAlign` — the alignment of the text within the lines of the paragraph. See   [TextStyle.textAlign].
- `lineHeight` — line height for the [Paragraph] in [TextUnit] unit, e.g. SP or EM. See   [TextStyle.lineHeight].
- `overflow` — how visual overflow should be handled.
- `softWrap` — whether the text should break at soft line breaks. If false, the glyphs in the   text will be positioned as if there was unlimited horizontal space. If [softWrap] is false,   [overflow] and TextAlign may have unexpected effects.
- `maxLines` — An optional maximum number of lines for the text to span, wrapping if necessary.   If the text exceeds the given number of lines, it will be truncated according to [overflow] and   [softWrap]. It is required that 1 <= [minLines] <= [maxLines].
- `minLines` — The minimum height in terms of minimum number of visible lines. It is required   that 1 <= [minLines] <= [maxLines].
- `onTextLayout` — callback that is executed when a new text layout is calculated. A   [TextLayoutResult] object that callback provides contains paragraph information, size of the   text, baselines and other details. The callback can be used to add additional decoration or   functionality to the text. For example, to draw selection around the text.
- `style` — style configuration for the text such as color, font, line height etc.

**Traps**

- 🔴 LocalTextStyles is internal and unavailable outside the library, so you can't use CompositionLocalProvider to swap the default text style for a subtree. To override locally you can only nest MiuixTheme(textStyles = ...) (copying the entire 14-item TextStyles bag), or pass style explicitly on every Text. Miuix also has no single-value LocalTextStyle like M3's.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/TextStyles.kt:250`)
- 🔴 The color fallback chain is explicit color → style.color → LocalContentColor, and LocalContentColor's default is Color.Black. MiuixTheme's controller overload provides LocalContentColor, but the MiuixTheme(colors = ...) overload does not —— with the latter in a dark theme, a Text with no explicit color will be black text on a black background.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/MiuixTheme.kt:62`)
- 🔴 The ColorProducer overload's lambda is not a composable context (ColorProducer is an ordinary fun interface, and Text is not inline), so writing MiuixTheme.colorScheme.xxx inside it fails to compile. The theme color must be read outside first and then passed into the lambda. The example in the docs components/text.md is wrong.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt:191`)
- 🟡 The AnnotatedString overload automatically adds 'primary color + underline' to every LinkAnnotation that doesn't already carry a style. For a different link style you must fill in styles when constructing the AnnotatedString, or it will be overwritten.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt:315`)
- ⚪ Within the same file onTextLayout has two signatures: the String overload is ((TextLayoutResult)->Unit)? = null, and the AnnotatedString overload is (TextLayoutResult)->Unit = {}. Passing null when switching overloads fails to compile.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt:309`)
- ⚪ The AnnotatedString overload's inlineContent is a bare Map, which is unstable to Compose and prevents this Text from skipping recomposition.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt:308`)

**Spec** default_style LocalTextStyles.current.main = 17.sp · overflow TextOverflow.Clip (no ellipsis by default)

**State** Purely stateless. The ColorProducer overload is a zero-recomposition channel for 'high-frequency color changes'; the color is read at draw time, skipping the entire color fallback chain.

**vs Material3** Corresponds to material3.Text. Differences: the default style comes from LocalTextStyles.main rather than an externally providable LocalTextStyle; the theme's text styles are a 14-item bag, and you can't override just one item; it adds automatic link coloring.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BadgeDemo.kt:62`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BadgeDemo.kt#L62) · [`docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt:67`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt#L67) · [`docs/demo/src/commonMain/kotlin/ButtonDemo.kt:70`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ButtonDemo.kt#L70) · [`docs/demo/src/commonMain/kotlin/CardDemo.kt:51`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/CardDemo.kt#L51)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt:90`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt#L90)</sub>

## Text  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [Text] component with Miuix style.
> 
> High level element that displays text and provides semantics / accessibility information.
> 
> The default [style] uses [LocalTextStyles.current.main]. If you are setting your own style, you
> may want to consider first retrieving the current style, and using [TextStyle.copy] to keep any
> theme defined attributes, only modifying the specific attributes you want to override.
> 
> For ease of use, commonly used parameters from [TextStyle] are also present here. The order of
> precedence is as follows:
> - If a parameter is explicitly set here (i.e, it is _not_ `null` or [TextUnit.Unspecified]), then
>   this parameter will always be used.
> - If a parameter is _not_ set, (`null` or [TextUnit.Unspecified]), then the corresponding value
>   from [style] will be used instead.

```kotlin
import top.yukonga.miuix.kmp.basic.Text

@Composable
fun Text(
    text: String,  // required
    color: ColorProducer,  // required
    modifier: Modifier = Modifier,
    autoSize: TextAutoSize? = null,
    fontSize: TextUnit = TextUnit.Unspecified,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight? = null,
    fontFamily: FontFamily? = null,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Clip,
    softWrap: Boolean = true,
    maxLines: Int = Int.MAX_VALUE,
    minLines: Int = 1,
    onTextLayout: ((TextLayoutResult) -> Unit)? = null,
    style: TextStyle = LocalTextStyles.current.main,
)
```

- `text` — the text to be displayed
- `color` — the [ColorProducer] that returns a [Color]. Useful when providing a color value that   changes frequently without needing to recompose. Overrides the text color provided in [style].
- `modifier` — the [Modifier] to be applied to this layout node
- `autoSize` — Enable auto sizing for this text composable. Finds the biggest font size that   fits in the available space and lays the text out with this size. This performs multiple layout   passes and can be slower than using a fixed font size. This takes precedence over sizes defined   through [fontSize] and [style]. See [TextAutoSize].
- `fontSize` — the size of glyphs to use when painting the text. See [TextStyle.fontSize].
- `fontStyle` — the typeface variant to use when drawing the letters (e.g., italic). See   [TextStyle.fontStyle].
- `fontWeight` — the typeface thickness to use when painting the text (e.g., [FontWeight.Bold]).
- `fontFamily` — the font family to be used when rendering the text. See [TextStyle.fontFamily].
- `letterSpacing` — the amount of space to add between each letter. See   [TextStyle.letterSpacing].
- `textDecoration` — the decorations to paint on the text (e.g., an underline). See   [TextStyle.textDecoration].
- `textAlign` — the alignment of the text within the lines of the paragraph. See   [TextStyle.textAlign].
- `lineHeight` — line height for the [Paragraph] in [TextUnit] unit, e.g. SP or EM. See   [TextStyle.lineHeight].
- `overflow` — how visual overflow should be handled.
- `softWrap` — whether the text should break at soft line breaks. If false, the glyphs in the   text will be positioned as if there was unlimited horizontal space. If [softWrap] is false,   [overflow] and TextAlign may have unexpected effects.
- `maxLines` — An optional maximum number of lines for the text to span, wrapping if necessary.   If the text exceeds the given number of lines, it will be truncated according to [overflow] and   [softWrap]. It is required that 1 <= [minLines] <= [maxLines].
- `minLines` — The minimum height in terms of minimum number of visible lines. It is required   that 1 <= [minLines] <= [maxLines].
- `onTextLayout` — callback that is executed when a new text layout is calculated. A   [TextLayoutResult] object that callback provides contains paragraph information, size of the   text, baselines and other details. The callback can be used to add additional decoration or   functionality to the text. For example, to draw selection around the text.
- `style` — style configuration for the text such as color, font, line height etc.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BadgeDemo.kt:62`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BadgeDemo.kt#L62) · [`docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt:67`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt#L67) · [`docs/demo/src/commonMain/kotlin/ButtonDemo.kt:70`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ButtonDemo.kt#L70) · [`docs/demo/src/commonMain/kotlin/CardDemo.kt:51`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/CardDemo.kt#L51)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt:189`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt#L189)</sub>

## Text  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [Text] component with Miuix style.
> 
> High level element that displays text and provides semantics / accessibility information.
> 
> The default [style] uses [LocalTextStyles.current.main]. If you are setting your own style, you
> may want to consider first retrieving the current style, and using [TextStyle.copy] to keep any
> theme defined attributes, only modifying the specific attributes you want to override.
> 
> For ease of use, commonly used parameters from [TextStyle] are also present here. The order of
> precedence is as follows:
> - If a parameter is explicitly set here (i.e, it is _not_ `null` or [TextUnit.Unspecified]), then
>   this parameter will always be used.
> - If a parameter is _not_ set, (`null` or [TextUnit.Unspecified]), then the corresponding value
>   from [style] will be used instead.
> 
> Additionally, for [color], if [color] is not set, and [style] does not have a color, then
> [LocalContentColor] will be used.

```kotlin
import top.yukonga.miuix.kmp.basic.Text

@Composable
fun Text(
    text: AnnotatedString,  // required
    modifier: Modifier = Modifier,
    color: Color = Color.Unspecified,
    autoSize: TextAutoSize? = null,
    fontSize: TextUnit = TextUnit.Unspecified,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight? = null,
    fontFamily: FontFamily? = null,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Clip,
    softWrap: Boolean = true,
    maxLines: Int = Int.MAX_VALUE,
    minLines: Int = 1,
    inlineContent: Map<String, InlineTextContent> = mapOf(),
    onTextLayout: (TextLayoutResult) -> Unit = {},
    style: TextStyle = LocalTextStyles.current.main,
)
```

- `text` — the text to be displayed
- `modifier` — the [Modifier] to be applied to this layout node
- `color` — [Color] to apply to the text. If [Color.Unspecified], and [style] has no color set,   this will be [LocalContentColor].
- `autoSize` — Enable auto sizing for this text composable. Finds the biggest font size that   fits in the available space and lays the text out with this size. This performs multiple layout   passes and can be slower than using a fixed font size. This takes precedence over sizes defined   through [fontSize] and [style]. See [TextAutoSize].
- `fontSize` — the size of glyphs to use when painting the text. See [TextStyle.fontSize].
- `fontStyle` — the typeface variant to use when drawing the letters (e.g., italic). See   [TextStyle.fontStyle].
- `fontWeight` — the typeface thickness to use when painting the text (e.g., [FontWeight.Bold]).
- `fontFamily` — the font family to be used when rendering the text. See [TextStyle.fontFamily].
- `letterSpacing` — the amount of space to add between each letter. See   [TextStyle.letterSpacing].
- `textDecoration` — the decorations to paint on the text (e.g., an underline). See   [TextStyle.textDecoration].
- `textAlign` — the alignment of the text within the lines of the paragraph. See   [TextStyle.textAlign].
- `lineHeight` — line height for the [Paragraph] in [TextUnit] unit, e.g. SP or EM. See   [TextStyle.lineHeight].
- `overflow` — how visual overflow should be handled.
- `softWrap` — whether the text should break at soft line breaks. If false, the glyphs in the   text will be positioned as if there was unlimited horizontal space. If [softWrap] is false,   [overflow] and TextAlign may have unexpected effects.
- `maxLines` — An optional maximum number of lines for the text to span, wrapping if necessary.   If the text exceeds the given number of lines, it will be truncated according to [overflow] and   [softWrap]. It is required that 1 <= [minLines] <= [maxLines].
- `minLines` — The minimum height in terms of minimum number of visible lines. It is required   that 1 <= [minLines] <= [maxLines].
- `inlineContent` — a map storing composables that replaces certain ranges of the text, used to   insert composables into text layout. See [InlineTextContent].
- `onTextLayout` — callback that is executed when a new text layout is calculated. A   [TextLayoutResult] object that callback provides contains paragraph information, size of the   text, baselines and other details. The callback can be used to add additional decoration or   functionality to the text. For example, to draw selection around the text.
- `style` — style configuration for the text such as color, font, line height etc.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BadgeDemo.kt:62`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BadgeDemo.kt#L62) · [`docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt:67`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt#L67) · [`docs/demo/src/commonMain/kotlin/ButtonDemo.kt:70`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ButtonDemo.kt#L70) · [`docs/demo/src/commonMain/kotlin/CardDemo.kt:51`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/CardDemo.kt#L51)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt:291`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt#L291)</sub>

## Text  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [Text] component with Miuix style.
> 
> High level element that displays text and provides semantics / accessibility information.
> 
> The default [style] uses [LocalTextStyles.current.main]. If you are setting your own style, you
> may want to consider first retrieving the current style, and using [TextStyle.copy] to keep any
> theme defined attributes, only modifying the specific attributes you want to override.
> 
> For ease of use, commonly used parameters from [TextStyle] are also present here. The order of
> precedence is as follows:
> - If a parameter is explicitly set here (i.e, it is _not_ `null` or [TextUnit.Unspecified]), then
>   this parameter will always be used.
> - If a parameter is _not_ set, (`null` or [TextUnit.Unspecified]), then the corresponding value
>   from [style] will be used instead.

```kotlin
import top.yukonga.miuix.kmp.basic.Text

@Composable
fun Text(
    text: AnnotatedString,  // required
    color: ColorProducer,  // required
    modifier: Modifier = Modifier,
    autoSize: TextAutoSize? = null,
    fontSize: TextUnit = TextUnit.Unspecified,
    fontStyle: FontStyle? = null,
    fontWeight: FontWeight? = null,
    fontFamily: FontFamily? = null,
    letterSpacing: TextUnit = TextUnit.Unspecified,
    textDecoration: TextDecoration? = null,
    textAlign: TextAlign? = null,
    lineHeight: TextUnit = TextUnit.Unspecified,
    overflow: TextOverflow = TextOverflow.Clip,
    softWrap: Boolean = true,
    maxLines: Int = Int.MAX_VALUE,
    minLines: Int = 1,
    inlineContent: Map<String, InlineTextContent> = mapOf(),
    onTextLayout: (TextLayoutResult) -> Unit = {},
    style: TextStyle = LocalTextStyles.current.main,
)
```

- `text` — the text to be displayed
- `color` — the [ColorProducer] that returns a [Color]. Useful when providing a color value that   changes frequently without needing to recompose. Overrides the text color provided in [style].
- `modifier` — the [Modifier] to be applied to this layout node
- `autoSize` — Enable auto sizing for this text composable. Finds the biggest font size that   fits in the available space and lays the text out with this size. This performs multiple layout   passes and can be slower than using a fixed font size. This takes precedence over sizes defined   through [fontSize] and [style]. See [TextAutoSize].
- `fontSize` — the size of glyphs to use when painting the text. See [TextStyle.fontSize].
- `fontStyle` — the typeface variant to use when drawing the letters (e.g., italic). See   [TextStyle.fontStyle].
- `fontWeight` — the typeface thickness to use when painting the text (e.g., [FontWeight.Bold]).
- `fontFamily` — the font family to be used when rendering the text. See [TextStyle.fontFamily].
- `letterSpacing` — the amount of space to add between each letter. See   [TextStyle.letterSpacing].
- `textDecoration` — the decorations to paint on the text (e.g., an underline). See   [TextStyle.textDecoration].
- `textAlign` — the alignment of the text within the lines of the paragraph. See   [TextStyle.textAlign].
- `lineHeight` — line height for the [Paragraph] in [TextUnit] unit, e.g. SP or EM. See   [TextStyle.lineHeight].
- `overflow` — how visual overflow should be handled.
- `softWrap` — whether the text should break at soft line breaks. If false, the glyphs in the   text will be positioned as if there was unlimited horizontal space. If [softWrap] is false,   [overflow] and TextAlign may have unexpected effects.
- `maxLines` — An optional maximum number of lines for the text to span, wrapping if necessary.   If the text exceeds the given number of lines, it will be truncated according to [overflow] and   [softWrap]. It is required that 1 <= [minLines] <= [maxLines].
- `minLines` — The minimum height in terms of minimum number of visible lines. It is required   that 1 <= [minLines] <= [maxLines].
- `inlineContent` — a map storing composables that replaces certain ranges of the text, used to   insert composables into text layout. See [InlineTextContent].
- `onTextLayout` — callback that is executed when a new text layout is calculated. A   [TextLayoutResult] object that callback provides contains paragraph information, size of the   text, baselines and other details. The callback can be used to add additional decoration or   functionality to the text. For example, to draw selection around the text.
- `style` — style configuration for the text such as color, font, line height etc.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/BadgeDemo.kt:62`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BadgeDemo.kt#L62) · [`docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt:67`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/BreadcrumbBarDemo.kt#L67) · [`docs/demo/src/commonMain/kotlin/ButtonDemo.kt:70`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ButtonDemo.kt#L70) · [`docs/demo/src/commonMain/kotlin/CardDemo.kt:51`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/CardDemo.kt#L51)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt:397`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Text.kt#L397)</sub>

## TooltipBox  ·  basic component

A container that attaches a tooltip to any anchor — triggered by long-press (touch) or hover (mouse). There are two overloads: the full version takes positionProvider + a tooltip slot + state, and the convenience version takes only a text string.

> A tooltip box that anchors a [tooltip] (a [PlainTooltip] or [RichTooltip]) to its [content].
> 
> The tooltip is shown on hover (desktop / web) or long press (touch), or programmatically via
> [TooltipState.show]. It is built on the foundation tooltip primitives, so triggering, the global
> single-tooltip behavior, and the auto-dismiss timeout match the platform behavior.

```kotlin
import top.yukonga.miuix.kmp.basic.TooltipBox

@Composable
fun TooltipBox(
    positionProvider: PopupPositionProvider,  // required
    tooltip: @Composable TooltipScope.() -> Unit,  // required
    state: TooltipState,  // required
    modifier: Modifier = Modifier,
    focusable: Boolean = false,
    enableUserInput: Boolean = true,
    content: @Composable () -> Unit,  // required
)
```

- `positionProvider` — the [PopupPositionProvider] positioning the tooltip, usually from   [TooltipDefaults.rememberTooltipPositionProvider].
- `tooltip` — the tooltip content.
- `state` — the [TooltipState] controlling visibility.
- `modifier` — the modifier applied to the anchor wrapper.
- `focusable` — whether the tooltip is focusable; true for interactive rich tooltips so an   outside tap dismisses them and their actions are reachable.
- `enableUserInput` — whether hover / long press on the anchor shows the tooltip.
- `content` — the anchor content.

**Traps**

- 🟡 The convenience version `TooltipBox(text = ...)` has a fully hard-coded style: body2 font size, maxLines = 2, Ellipsis truncation, with no configurable parameters. Slightly longer text gets truncated to two lines with an ellipsis; for more control you must switch to the full version + PlainTooltip.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:621`)
- 🟡 The tooltip's orientation is not inferred from the positionProvider's behavior but by casting it to TooltipPopupPositionProvider and reading the positioning field; if the cast fails it is always treated as Below. When passing a custom PopupPositionProvider, the caret of PlainTooltip/RichTooltip is drawn on the wrong side (or not drawn at all).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:283`)
- 🔴 All gesture entries (long-press, mouse hover) call show() with MutatePriority.UserInput, while the timeout branch is taken only when "not persistent and the priority is not UserInput" — that is, a tooltip popped by a touch long-press never times out automatically and can only be dismissed by tapping elsewhere or an explicit dismiss. The mouse one retracts when the pointer leaves the anchor. Only programmatically calling state.show() consumes TooltipDuration.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:202`)
- 🟡 focusable defaults to false. When a RichTooltip carries a clickable action you must explicitly pass focusable = true, otherwise clicking outside won't close it and its inner buttons may be unclickable.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:278`)

**Spec** enter fadeIn + scaleIn(initialScale = 0.9f), reusing ListPopupDefaults's animation spec · exit fadeOut + scaleOut(targetScale = 0.9f); the exit scale deliberately uses a spring rather than a tween (so it can pick up the unfinished enter velocity and avoid a "pause then reverse")

**State** state is hosted by rememberTooltipState() and required (the convenience version has a default). TooltipState uses a MutatorMutex to ensure only one tooltip is visible at a time. isVisible is judged by `transition.targetState || !transition.isIdle`, i.e. it counts as visible even while the animation hasn't finished, ensuring an interrupted enter can play its exit animation in reverse.

**vs Material3** Corresponds to material3.TooltipBox (also a positionProvider + tooltip + state + content structure). This Miuix set is forked from foundation's experimental BasicTooltipBox, and the only substantive behavior change is: when the mouse leaves the anchor, a persistent tooltip is not closed (so the cursor can move onto a RichTooltip to click its buttons) — which is exactly M3's behavior. M3's TooltipDefaults provides factories like rememberPlainTooltipPositionProvider(), while Miuix expresses the orientation with the TooltipAnchorPosition enum.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/TooltipDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TooltipDemo.kt#L53) · [`example/shared/src/commonMain/kotlin/MainPage.kt:267`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MainPage.kt#L267) · [`example/shared/src/commonMain/kotlin/component/TooltipSection.kt:42`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/TooltipSection.kt#L42)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:273`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt#L273)</sub>

## TooltipBox  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A plain tooltip convenience that wraps [TooltipBox] + [PlainTooltip] for a short text label.

```kotlin
import top.yukonga.miuix.kmp.basic.TooltipBox

@Composable
fun TooltipBox(
    text: String,  // required
    modifier: Modifier = Modifier,
    state: TooltipState = rememberTooltipState(isPersistent = false),
    enabled: Boolean = true,
    positioning: TooltipAnchorPosition = TooltipAnchorPosition.Below,
    containerColor: Color = TooltipDefaults.plainTooltipContainerColor,
    contentColor: Color = TooltipDefaults.plainTooltipContentColor,
    content: @Composable () -> Unit,  // required
)
```

- `text` — the text label of the tooltip.
- `modifier` — the modifier applied to the anchor wrapper.
- `state` — the [TooltipState] controlling visibility.
- `enabled` — whether hover / long press on the anchor shows the tooltip.
- `positioning` — the preferred [TooltipAnchorPosition] of the tooltip.
- `containerColor` — the container color of the tooltip.
- `contentColor` — the content color of the tooltip.
- `content` — the anchor content.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/TooltipDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TooltipDemo.kt#L53) · [`example/shared/src/commonMain/kotlin/MainPage.kt:267`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MainPage.kt#L267) · [`example/shared/src/commonMain/kotlin/component/TooltipSection.kt:42`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/TooltipSection.kt#L42)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt:621`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Tooltip.kt#L621)</sub>

## Public types in this topic (21)

- `BadgeDefaults` **object** · `import top.yukonga.miuix.kmp.basic.BadgeDefaults`
- `ListPopupDefaults` **object** · `import top.yukonga.miuix.kmp.basic.ListPopupDefaults`
- `ListPopupLayoutInfo(windowBounds: IntRect, popupMargin: IntRect, effectiveTransformOrigin: TransformOrigin, localTransformOrigin: TransformOrigin, popupLayoutPosition: PopupLayoutP…)` **data class** (required: windowBounds, popupMargin, effectiveTransformOrigin, localTransformOrigin, popupLayoutPosition) · `import top.yukonga.miuix.kmp.basic.ListPopupLayoutInfo`
- `PopupLayoutPosition(showBelow: Boolean, showAbove: Boolean, isRightAligned: Boolean)` **data class** (required: showBelow, showAbove, isRightAligned) · `import top.yukonga.miuix.kmp.basic.PopupLayoutPosition`
- `PopupPositionProvider` **interface** · `import top.yukonga.miuix.kmp.basic.PopupPositionProvider`
- `PopupPositionProvider.Align` **enum** — Start, End, TopStart, TopEnd, BottomStart, BottomEnd · `import top.yukonga.miuix.kmp.basic.PopupPositionProvider`
- `ProgressIndicatorDefaults` **object** · `import top.yukonga.miuix.kmp.basic.ProgressIndicatorDefaults`
- `SnackbarData` **interface** · `import top.yukonga.miuix.kmp.basic.SnackbarData`
- `SnackbarDefaults` **object** · `import top.yukonga.miuix.kmp.basic.SnackbarDefaults`
- `SnackbarDuration` **interface** · `import top.yukonga.miuix.kmp.basic.SnackbarDuration`
- `SnackbarDuration.Custom(durationMillis: kotlin.Long)` **data class** (required: durationMillis) · `import top.yukonga.miuix.kmp.basic.SnackbarDuration`
- `SnackbarDuration.Indefinite` **object** · `import top.yukonga.miuix.kmp.basic.SnackbarDuration`
- `SnackbarDuration.Long` **object** · `import top.yukonga.miuix.kmp.basic.SnackbarDuration`
- `SnackbarDuration.Short` **object** · `import top.yukonga.miuix.kmp.basic.SnackbarDuration`
- `SnackbarHostState` **class** · `import top.yukonga.miuix.kmp.basic.SnackbarHostState`
- `SnackbarResult` **enum** — Dismissed, ActionPerformed · `import top.yukonga.miuix.kmp.basic.SnackbarResult`
- `SnackbarVisuals(message: String, actionLabel: String?, withDismissAction: Boolean, duration: SnackbarDuration)` **data class** (required: message, actionLabel, withDismissAction, duration) · `import top.yukonga.miuix.kmp.basic.SnackbarVisuals`
- `TooltipAnchorPosition` **value class** · `import top.yukonga.miuix.kmp.basic.TooltipAnchorPosition`
- `TooltipDefaults` **object** · `import top.yukonga.miuix.kmp.basic.TooltipDefaults`
- `TooltipScope` **interface** · `import top.yukonga.miuix.kmp.basic.TooltipScope`
- `TooltipState` **interface** · `import top.yukonga.miuix.kmp.basic.TooltipState`

## Notes on types & namespaces

### SnackbarHostState

The state holder for Snackbar (package top.yukonga.miuix.kmp.basic), passed to SnackbarHost(state = …). The display entry is the member function suspend fun showSnackbar(message: String, actionLabel: String? = null, withDismissAction: Boolean = false, duration: SnackbarDuration = SnackbarDuration.Short): SnackbarResult; there are also the suspend newestSnackbarData() / oldestSnackbarData().

**Traps**

- 🟡 showSnackbar suspends until this Snackbar is closed before returning (internally result.await()), so it must be called inside the scope.launch { } of a rememberCoroutineScope(); calling it twice in a row in the same coroutine means the second one appears only after the first disappears.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:183-228`)
- ⚪ SnackbarDuration is not a Material3 enum but a sealed interface: the three data objects Short, Long, Indefinite, plus Custom(durationMillis: Long) that can specify a millisecond count.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Snackbar.kt:82-91`)

