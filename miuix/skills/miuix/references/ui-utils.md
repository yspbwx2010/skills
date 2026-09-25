# Interaction utilities

overScroll bounce, press feedback, haptics, Pager gesture-conflict handling, back-gesture scope. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## Modifier.horizontalPagerSwipeOverride  ·  interaction utility

The actual implementation of pagerGestureOverride's CrossAxisInterceptor mode: it recognizes horizontal drag preemptively in the Initial pass and drives the pager by putting the drag and the post-release snap into the same PagerState.scroll(UserInput); vertical drag is yielded to the page content. Normally use pagerGestureOverride directly; you don't need to call this separately.

> Drives horizontal drag and settling in one [PagerState.scroll] mutation.
> New touches take over at the displayed position; vertical gestures stay with children.
> 
> Set [HorizontalPager]'s userScrollEnabled to false and its pageNestedScrollConnection to
> [PagerGestureNestedScrollConnection] while enabled to prevent competing gesture recognition.

```kotlin
import top.yukonga.miuix.kmp.utils.horizontalPagerSwipeOverride

fun Modifier.horizontalPagerSwipeOverride(
    pagerState: PagerState,  // required
    enabled: Boolean = true,
    onIntercepted: (() -> Unit)? = null,
): Modifier
```

**Traps**

- 🔴 It decides in the Initial pass (parent before child): if the horizontal displacement exceeds touchSlop and is greater than the vertical displacement it consumes the event. All horizontally swipeable children in the page (LazyRow, a horizontally scrolling TabRow, Slider, carousels) have their horizontal swipe intercepted by the pager and can't scroll themselves. The native pager gives the child priority. Don't use CrossAxis mode for pages that contain horizontal gestures, and put things like TabRow outside the pager.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:227`)
- 🟡 Every press (including a plain tap) cancels the pager's in-progress animation and opens a new scroll(UserInput), snapping to the nearest page by rounding the current position on release. So if the user taps the page content during a springAnimateToPage paging animation, the pager stops at the page nearest to the position at that moment rather than the original target page; logic observing pagerState.isScrollInProgress will also briefly see true on each tap.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:182`)
- ⚪ The release-snap rule is hard-coded: a velocity above 400.dp/s rounds toward the velocity direction (ceil/floor), otherwise it rounds to nearest, then animates over with PagerNavigationSpringSpec, at most one page away from the current displayed position. It doesn't read HorizontalPager's flingBehavior / snapPositionalThreshold, and there is no tunable parameter.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:260`)
- ⚪ After userScrollEnabled = false the native pager no longer handles the mouse wheel/touchpad, and this modifier makes up for it in the Main pass: only wheel/Pan events whose horizontal component is greater than the vertical page (each wheel notch is converted at 48.dp), and a purely vertical wheel does not page.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:307`)

**State** No external state. The node internally holds motionJob (the current scroll coroutine) and a wheel-event channel; when the pagerState instance changes or the node detaches (including the modifier being removed because enabled goes from true to false) the in-progress animation is cancelled.

**vs Material3** Replaces the native HorizontalPager's draggable + flingBehavior. Natively it is negotiated by pageNestedScrollConnection and the child, with the child taking priority; here the parent intercepts preemptively in the Initial pass. It provides its own pageLeft/pageRight accessibility actions (paging via springAnimateToPage) and handles the directions of RTL and reverseLayout.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:141`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt#L141)</sub>

## Modifier.iosStyleMomentumHalt  ·  interaction utility

The implementation of pagerGestureOverride's TapToHalt mode: it attaches flingTracker's nested scroll; on press, if the child list is doing inertia scroll it requests a halt, and after this gesture is judged to be a horizontal swipe (dx > slop and dx > 2·dy) it swallows it, so this one doesn't page; with no inertia it doesn't intervene at all and leaves the horizontal swipe to the native pager.

> Requests a child fling halt on touch down and consumes that gesture's horizontal drag.
> When no child fling is active, leaves horizontal swipes to the native pager.

```kotlin
import top.yukonga.miuix.kmp.utils.iosStyleMomentumHalt

fun Modifier.iosStyleMomentumHalt(
    flingTracker: PagerFlingTrackerConnection,  // required
    enabled: Boolean = true,
    onHalted: (() -> Unit)? = null,
): Modifier
```

**Traps**

- 🔴 It doesn't receive PagerState and never drives the pager; paging relies entirely on HorizontalPager's own gesture. So you must keep userScrollEnabled = true and the default pageNestedScrollConnection, and cannot keep CrossAxis's configuration.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:411`)
- ⚪ haltFling = true is set on press, and the inertia is cut off on the next frame before the finger even lifts; then if it is judged a vertical drag, haltFling is reset and handed to the list to handle normally. onHalted is called back at the moment of press (as long as there was inertia then), and does not mean this gesture is ultimately a horizontal swipe.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:429`)

**State** All state is in the passed-in flingTracker, which the caller must remember; pointerInput is keyed by flingTracker / enabled / onHalted, and a change in any of them restarts the gesture coroutine.

**vs Material3** androidx pager has no counterpart. This makes "during inertia the first horizontal swipe only halts, doesn't page" a deterministic behavior, mimicking iOS's inertia halt; the rest of the time it is entirely native pager behavior.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:411`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt#L411)</sub>

## Modifier.overScrollHorizontal  ·  interaction utility

Adds the same set of Folme bounce to a horizontally scrollable container. It is a thin wrapper around overScrollOutOfBound(isVertical = false).

```kotlin
import top.yukonga.miuix.kmp.utils.overScrollHorizontal

fun Modifier.overScrollHorizontal(
    nestedScrollToParent: Boolean = true,
    isEnabled: () -> Boolean = { true },
): Modifier
```

**Traps**

- 🔴 The problem of stacking with the theme-injected MiuixOverscrollFactory is exactly the same as the vertical version, and horizontally scrollable components must also pass overscrollEffect = null. TabRow's two internal LazyRows both pass it explicitly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:308`)
- 🟡 Modifier.scrollEndHaptic() handles only the vertical axis (reads only available.y / consumed.y), so adding it to a horizontal list is a silent no-op. Horizontal scrolling to the boundary gets no haptic feedback, and there is no error either.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/ScrollEndHaptic.kt:60`)
- 🟡 The damping range takes the window width containerDpSize.width, not the component's own width. On a narrow horizontal item list the bounce amplitude is on the large side.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:237`)
- ⚪ Attaching both overScrollVertical() and overScrollHorizontal() to the same component creates two entirely independent nodes (each with its own clipToBounds layer and its own spring), not a single two-axis implementation. For two axes use the theme-injected MiuixOverscrollEffect, which itself handles X/Y independently.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:64`)

**State** Same as overScrollVertical.

**vs Material3** Same as overScrollVertical.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:64`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt#L64)</sub>

## Modifier.overScrollOutOfBound  ·  interaction utility

The real implementation of the bounce; overScrollVertical/overScrollHorizontal are just its two wrappers. The only reason to use it directly is when the direction is decided by a variable.

> Overscroll effect when scrolling to the boundary.
> 
> The effect engages only during a press or pan gesture session (touch drag; trackpad pan on
> Android). Mouse wheel and keyboard scrolling pass through untouched, as does desktop/macOS
> trackpad scrolling (delivered as wheel events).

```kotlin
import top.yukonga.miuix.kmp.utils.overScrollOutOfBound

fun Modifier.overScrollOutOfBound(
    isVertical: Boolean = true,
    nestedScrollToParent: Boolean = true,
    isEnabled: () -> Boolean = { true },
): Modifier
```

- `isVertical` — Whether the overscroll effect is vertical or horizontal.
- `nestedScrollToParent` — Whether to dispatch nested scroll events to parent. Pass-through deltas (non-gesture sources such as mouse wheel, and while pull-to-refresh is active) are forwarded to ancestors regardless of this flag.
- `isEnabled` — Whether the overscroll effect is enabled.

**Traps**

- 🔴 LocalOverScrollState is compositionLocalOf { OverScrollState() }, and nowhere in the whole repository provides it -- the default factory's result is cached on this top-level CompositionLocal object, effectively a process-level singleton. Consequences: when any one list on screen goes out of bounds, all PullToRefresh see isOverScrollActive == true; in multi-Scaffold / multi-window scenarios two unrelated lists' overscroll states pollute each other. isOverScrollActive's setter is internal set, so the outside cannot correct it manually. To isolate it you can only do CompositionLocalProvider(LocalOverScrollState provides OverScrollState()) yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:482`)
- 🔴 The accompanying cleanup is done in reverse order: MiuixOverscrollEffectNode.onDetach first sets effect.getOverScrollState to null, and only the next line calls effect.resetAll(), while resetAll clears isOverScrollActive using exactly that getter, so it inevitably short-circuits. After a list that is out of bounds is removed from composition (e.g. switching tabs), the global isOverScrollActive remains true, and the immediately following pull-to-refresh fails directly until the next scroll of any kind corrects it. This is a window-of-time bug, not a permanent one, but "pull to refresh immediately after switching tabs" is a very easy path to hit.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/OverscrollFactory.kt:379`)
- 🟡 isEnabled() is evaluated immediately at modifier construction, and when it returns false the whole modifier (including clipToBounds) is not added. The lambda parameter makes it look like lazy evaluation, but it is not.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:92`)
- 🟡 nestedScrollToParent = false only blocks forwarding "within a gesture session". Delta from non-gesture sources (mouse wheel etc. where source != UserInput) and delta while PullToRefresh is active are still unconditionally forwarded to the ancestor; this parameter cannot stop that.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:321`)
- ⚪ The modifier version's applyDrag has no scrollRange == 0 guard, while the Factory version does (OverscrollFactory.kt:133 / :141's if (delta == 0f || scrollRangeH == 0f) return and its Y-axis version). When scrollRange is 0 it computes 0f/0f = NaN and passes it all the way to translationY, breaking the layer transform. The asymmetric guards between the two implementations are themselves a signal.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:277`)

**State** Stateless externally. The cooperative state lives on two CompositionLocals: LocalOverScrollState (a process-level singleton, see above) and LocalPullToRefreshState (provided normally by PullToRefresh). Because PullToRefresh's connection is attached at the outer layer, the isOverScrollActive it reads is always the value written by the previous event -- a deliberately accepted one-frame-delayed cooperation.

**vs Material3** No direct counterpart. foundation's equivalent concept is OverscrollEffect + Modifier.overscroll, but this modifier takes its own path of NestedScrollConnection + LayoutModifierNode and does not interoperate with the official interface.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:87`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt#L87)</sub>

## Modifier.overScrollVertical  ·  interaction utility

Adds Folme-style boundary bounce (a damping curve + a critically-damped spring) to a vertically scrollable container. It is a thin wrapper around overScrollOutOfBound(isVertical = true).

```kotlin
import top.yukonga.miuix.kmp.utils.overScrollVertical

fun Modifier.overScrollVertical(
    nestedScrollToParent: Boolean = true,
    isEnabled: () -> Boolean = { true },
): Modifier
```

**Traps**

- 🔴 Under MiuixTheme it stacks with the theme-injected MiuixOverscrollFactory rather than replacing it -- two independent offsets and springs run at once, adding displacement and consuming velocity twice. The correct usage is to pass overscrollEffect = null to the scrollable component, as the library's TabRow does. This contract appears in the docs only as a single line of code comment.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TabRow.kt:169`)
- 🟡 isEnabled is a lambda parameter but is evaluated immediately (called synchronously in the composable's composition scope), not lazily. Reading snapshot state inside the lambda (e.g. listState.canScrollForward) causes the calling composable to recompose wholesale and rebuild the entire Modifier chain when scrollability flips; when it returns false, even clipToBounds is not added.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:92`)
- 🟡 Bounce accumulates only within a "press / trackpad pan" gesture session: PointerEventType.Scroll (wheel) only follows the current session state and does not open its own session, so mouse wheel and keyboard scrolling pass through as-is without bounce, and desktop macOS trackpad also arrives as wheel events -- so on desktop you see no effect in most cases, and this is not a bug. Since 0.9.4, any pointer press (including mouse) counts as opening a session, so a custom mouse drag can also bounce; previously mouse press was explicitly excluded. Standard Compose scrollable components do not respond to mouse drag themselves, so this change is invisible for ordinary lists.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:165`)
- 🟡 The damping range scrollRange takes the window size (LocalWindowInfo.containerDpSize.height), not the height of the modified component itself. When attached to a small control, the bounce amplitude is still computed against the whole window height, and the feel is on the soft side.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:235`)
- ⚪ The modifier unconditionally adds a clipToBounds() layer first, so content cannot be drawn beyond the component's bounds. Watch out in scenarios with shadows/glow that need overflow drawing.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:95`)

**State** Stateless externally. The internal OverscrollNode's offset is an ordinary Float that bypasses snapshots (invisible to Compose, triggering re-placement manually via invalidatePlacement); the only channel broadcast externally is the global LocalOverScrollState.isOverScrollActive, whose setter is internal set, so the outside can only read it.

**vs Material3** foundation's official entry point is Modifier.overscroll(rememberOverscrollEffect()). overScrollVertical does not implement the OverscrollEffect interface but implements its own NestedScrollConnection + LayoutModifierNode, so it cannot be passed to a LazyColumn's overscrollEffect parameter, nor composed with the official Modifier.overscroll -- to use the official interface, use MiuixOverscrollEffect().

**Compilable examples** [`docs/demo/src/commonMain/kotlin/PullToRefreshDemo.kt:66`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/PullToRefreshDemo.kt#L66) · [`example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt:212`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt#L212) · [`example/shared/src/commonMain/kotlin/component/SuperSearchBar.kt:216`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SuperSearchBar.kt#L216) · [`example/shared/src/commonMain/kotlin/utils/PageUtils.kt:46`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/utils/PageUtils.kt#L46)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:51`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt#L51)</sub>

## Modifier.pagerGestureOverride  ·  interaction utility

Attached to a HorizontalPager's modifier to resolve the conflict where "when a page contains a vertical list, you can't swipe horizontally to change pages during the list's inertia scroll/spring-back." It dispatches by mode: CrossAxisInterceptor (default) = horizontalPagerSwipeOverride, which takes over horizontal drag and snapping itself; TapToHalt = iosStyleMomentumHalt, which only halts the child list's inertia while paging is still left to the native pager; Native = returns this unchanged.

> Applies [mode] to a [HorizontalPager].
> 
> For Cross-Axis mode, configure the pager as documented in [horizontalPagerSwipeOverride].
> [flingTracker] is required for [PagerInterceptionMode.TapToHalt].

```kotlin
import top.yukonga.miuix.kmp.utils.pagerGestureOverride

fun Modifier.pagerGestureOverride(
    pagerState: PagerState,  // required
    mode: PagerInterceptionMode = PagerInterceptionMode.CrossAxisInterceptor,
    enabled: Boolean = true,
    flingTracker: PagerFlingTrackerConnection? = null,
    onTriggered: (() -> Unit)? = null,
): Modifier
```

**Traps**

- 🔴 The default CrossAxisInterceptor mode requires the HorizontalPager to set both userScrollEnabled = false and pageNestedScrollConnection = PagerGestureNestedScrollConnection; missing either one causes two gesture sets to fight over the same PagerState or abnormal spring-back. These two parameters are on the HorizontalPager, not on this modifier, and adding only the modifier without changing the pager parameters is the most common wrong wiring.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:138`)
- 🔴 Conversely, when switching to Native or TapToHalt you must restore userScrollEnabled and pageNestedScrollConnection to the pager defaults: these two branches don't use pagerState at all and don't drive the pager (TapToHalt only halts the child list and swallows that one horizontal swipe). Keeping CrossAxis's userScrollEnabled = false gives a pager that can't be swiped at all. To switch modes at runtime, switch these two parameters together by mode as the sample does.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:475`)
- 🟡 How to choose among the four overloads: when flingTracker is not passed, Kotlin overload resolution picks the two @Composable ones (they have fewer unspecified default parameters), which internally remember a PagerFlingTrackerConnection. So writing Modifier.pagerGestureOverride(state) in a non-@Composable context (a plain fun returning Modifier, inside a remember { } lambda) reports "@Composable invocations can only happen from the context of a @Composable function"; to use it there, pass flingTracker explicitly (null is fine too, only TapToHalt then stops working).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:516`)
- 🟡 The non-Composable overload silently returns this when mode = TapToHalt and flingTracker == null, with no error and no warning, appearing as "chose iOS-like but nothing happens." When passing the tracker yourself you must remember { PagerFlingTrackerConnection() }; inlining new makes each recomposition swap the instance, and pointerInput keyed by it restarts the gesture coroutine and loses the in-progress inertia-tracking state.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:482`)
- 🟡 The mode: Int overload is interpreted by the ordinal of PagerInterceptionMode.entries: 0 = Native, 1 = CrossAxisInterceptor, 2 = TapToHalt; out of range (negative or ≥ 3) doesn't throw but silently falls to Native. Note the Int overload has no default value, whereas the Enum overload defaults to CrossAxisInterceptor (ordinal 1), so a 0 read from settings is not the "default mode."  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:499`)
- 🟡 When enabled = false every branch just returns this and the modifier is a complete no-op — it does not disable paging. Under the CrossAxis configuration userScrollEnabled is already false, so the pager then becomes completely unswipeable; if userScrollEnabled is still true, the native gesture pages as usual. To turn off swipe-paging you must set both enabled and userScrollEnabled to false; to "turn off interception while keeping native swiping" you must set userScrollEnabled back to true.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:145`)
- 🟡 Only applicable to HorizontalPager. CrossAxis's recognition logic is hard-wired to judge on the x-axis and scroll by delta.x, yielding to the child once the vertical exceeds slop; attached to a VerticalPager it becomes horizontal drag driving vertical paging while vertical drag can't page. TapToHalt's tracker also only tracks child inertia in the y direction.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:227`)
- ⚪ A 0.9.4-added API whose signature will change in the next version: an unreleased commit on main has added a required parameter flingBehavior: FlingBehavior to each pagerGestureOverride overload, removed horizontalPagerSwipeOverride, and renamed CrossAxisInterceptor to CrossAxis (ordinal unchanged). When upgrading miuix you must change all call sites; the Int overload that persists the mode by ordinal is least affected by the rename.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:462`)

**State** The modifier itself holds no business state; the page index is all in the caller's PagerState. CrossAxis's node internally holds a running PagerState.scroll(UserInput) coroutine; the @Composable overloads additionally remember a PagerFlingTrackerConnection (created even when mode is not TapToHalt). mode usually comes from persisted settings, passing the ordinal directly with the Int overload.

**vs Material3** androidx.compose.foundation.pager has no counterpart. The official docs' stated motivation is: in the native HorizontalPager, during a child list's inertia scroll or spring-back, a horizontal swipe cannot reliably change pages. CrossAxis mode makes that one horizontal swipe page directly; TapToHalt mode fixes the behavior as "the first horizontal swipe only halts, doesn't page; the next one pages." Under CrossAxis the snap animation and velocity thresholds are all implemented by Miuix itself, and HorizontalPager's flingBehavior parameter has no effect on touch swiping.

**Compilable examples** [`example/shared/src/commonMain/kotlin/AppContent.kt:762`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L762)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:462`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt#L462)</sub>

## Modifier.pagerGestureOverride  ·  interaction utility

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Accepts a stored mode ordinal; invalid values select [PagerInterceptionMode.Native].

```kotlin
import top.yukonga.miuix.kmp.utils.pagerGestureOverride

fun Modifier.pagerGestureOverride(
    pagerState: PagerState,  // required
    mode: Int,  // required
    enabled: Boolean = true,
    flingTracker: PagerFlingTrackerConnection? = null,
    onTriggered: (() -> Unit)? = null,
): Modifier
```

**Compilable examples** [`example/shared/src/commonMain/kotlin/AppContent.kt:762`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L762)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:491`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt#L491)</sub>

## Modifier.pagerGestureOverride  ·  interaction utility

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Applies [mode] with a remembered [PagerFlingTrackerConnection].
> See [horizontalPagerSwipeOverride] for Cross-Axis pager configuration.

```kotlin
import top.yukonga.miuix.kmp.utils.pagerGestureOverride

@Composable
fun Modifier.pagerGestureOverride(
    pagerState: PagerState,  // required
    mode: PagerInterceptionMode = PagerInterceptionMode.CrossAxisInterceptor,
    enabled: Boolean = true,
    onTriggered: (() -> Unit)? = null,
): Modifier
```

**Compilable examples** [`example/shared/src/commonMain/kotlin/AppContent.kt:762`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L762)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:510`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt#L510)</sub>

## Modifier.pagerGestureOverride  ·  interaction utility

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Accepts a stored mode ordinal; invalid values select [PagerInterceptionMode.Native].

```kotlin
import top.yukonga.miuix.kmp.utils.pagerGestureOverride

@Composable
fun Modifier.pagerGestureOverride(
    pagerState: PagerState,  // required
    mode: Int,  // required
    enabled: Boolean = true,
    onTriggered: (() -> Unit)? = null,
): Modifier
```

**Compilable examples** [`example/shared/src/commonMain/kotlin/AppContent.kt:762`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L762)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:530`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt#L530)</sub>

## Modifier.pressable  ·  interaction utility

A trimmed-down version of clickable that handles only press appearance (indication lifecycle + InteractionSource management + role/disabled semantics); it has no click callback, and the click behavior must be layered separately with clickable/combinedClickable/toggleable.

> Configure component to receive press via accessibility "press" event.
> 
> Add this modifier to the element to make it pressable within its bounds and show an indication as
> specified in [indication] parameter.
> 
> If [interactionSource] is `null`, and [indication] is an [IndicationNodeFactory], an internal
> [MutableInteractionSource] will be lazily created along with the [indication] only when needed.
> This reduces the performance cost of clickable during composition, as creating the [indication]
> can be delayed until there is an incoming [androidx.compose.foundation.interaction.Interaction].
> If you are only passing a remembered [MutableInteractionSource] and you are never using it
> outside of clickable, it is recommended to instead provide `null` to enable lazy creation. If you
> need [indication] to be created eagerly, provide a remembered [MutableInteractionSource].
> 
> If [indication] is _not_ an [IndicationNodeFactory], and instead implements the deprecated
> [Indication.rememberUpdatedInstance] method, you should explicitly pass a remembered
> [MutableInteractionSource] as a parameter for [interactionSource] instead of `null`, as this
> cannot be lazily created inside pressable.

```kotlin
import top.yukonga.miuix.kmp.utils.pressable

fun Modifier.pressable(
    interactionSource: MutableInteractionSource?,  // required
    indication: Indication? = null,
    enabled: Boolean = true,
    role: Role? = null,
    delay: Long? = TAP_INDICATION_DELAY,
)
```

- `interactionSource` — [MutableInteractionSource] that will be used to dispatch   [PressInteraction.Press] when this pressable is pressed. If `null`, an internal   [MutableInteractionSource] will be created if needed.
- `indication` — indication to be shown when modified element is pressed. By default, indication   from [LocalIndication] will be used. Pass `null` to show no indication, or current value from   [LocalIndication] to show theme default
- `enabled` — Controls the enabled state. When `false`, this modifier will appear disabled for   accessibility services
- `role` — the type of user interface element. Accessibility services might use this to describe   the element or do customizations
- `delay` — how long to wait before appearing 'pressed' (emitting [PressInteraction.Press]).   If `null`, even if the animation is subsequently scrolled or consumed, a "pressed" appears directly.

**Traps**

- 🔴 The first parameter interactionSource has no default value, so Modifier.pressable() does not compile (reports No value passed for parameter interactionSource) -- the official doc example is written this way. To use a node-internal lazily-built source you must explicitly write Modifier.pressable(interactionSource = null).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Pressable.kt:86`)
- 🔴 "SinkFeedback is the default effect" is wrong. The indication default value is null, taking the "no indication needed" fast path inside pressableWithIndicationIfNeeded, resulting in no visual feedback at all. For the sink effect you must explicitly pass indication = SinkFeedback().  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Pressable.kt:87`)
- 🟡 The KDoc line "By default, indication from LocalIndication will be used" was copied wholesale from Compose's clickable and does not hold for pressable -- nothing in the whole file reads LocalIndication (that import only serves the KDoc link). Do not infer behavior from the KDoc.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Pressable.kt:75`)
- 🔴 The semantics set only role and disabled, with no onClick, no keyboard-Enter trigger, and no accessibility click action. A control made with only pressable is completely inoperable under TalkBack. The library's three call sites all additionally layer combinedClickable(Card) / triStateToggleable(Checkbox) / selectable(RadioButton) to supply behavior.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Pressable.kt:352`)
- 🟡 delay defaults to 150ms before emitting PressInteraction.Press (to prevent a flicker when a press immediately turns into a scroll). The library's Card / Checkbox / RadioButton all pass delay = null to get an instant press state. To have feedback the instant you press you must explicitly pass delay = null. A fast tap does not lose feedback -- Press+Release are emitted together on release -- but it lights up 150ms late.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Pressable.kt:145`)

**State** A stateless modifier. When interactionSource is passed null, the node lazily builds one internally and clears it on onDetach (the press is not observable externally); to observe the press externally with something like collectIsPressedAsState, you must remember { MutableInteractionSource() } yourself and pass it in, and pass the same instance to the clickable layered on top.

**vs Material3** The counterpart is foundation's Modifier.clickable (not anything in material3). Differences: it removes onClick, keyboard trigger, and accessibility click action; it adds a delay parameter; and the default indication is null rather than LocalIndication.current. The design intent is to separate "appearance" from "behavior", letting a Card layer an outer pressable(TiltFeedback) + inner combinedClickable with two sets of feedback -- something a single clickable(indication=) cannot do.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Pressable.kt:85`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Pressable.kt#L85)</sub>

## Modifier.scrollEndHaptic  ·  interaction utility

Gives one haptic feedback when a scroll flings to the boundary. Attach it to a scrollable container's Modifier (the library example writes it before overScrollVertical).

> Applies a haptic feedback effect when a scrollable container is flung to its boundaries.

```kotlin
import top.yukonga.miuix.kmp.utils.scrollEndHaptic

fun Modifier.scrollEndHaptic(
    hapticFeedbackType: HapticFeedbackType = HapticFeedbackType.TextHandleMove,
): Modifier
```

- `hapticFeedbackType` — The type of haptic feedback to perform.

**Traps**

- 🔴 It supports only the vertical axis. onPreScroll and onPostFling read only available.y / consumed.y, and the internal state enum only has TopBoundaryHit / BottomBoundaryHit, so available.x / consumed.x are never read. Attaching it to a LazyRow or any horizontal scroll is a silent no-op -- no error, no warning, and neither the modifier name nor the docs have any direction qualifier.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/ScrollEndHaptic.kt:60`)
- 🟡 The trigger is attached only to onPostFling, with no onPostScroll path. Slowly dragging to the end (producing no fling) never vibrates; only a fast fling to the end vibrates. Meanwhile the neighboring Overscroll specifically adds a bounce for "session ended but no fling", so the same "reach the boundary" action produces the inconsistency of "there is a bounce but no haptic".  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/ScrollEndHaptic.kt:68`)
- ⚪ The trigger also has two undocumented thresholds: |available.y| must be greater than 1f, and |consumed.y| must be greater than or equal to 25f. A slight boundary contact does not vibrate.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/ScrollEndHaptic.kt:71`)
- ⚪ The default feedback type is HapticFeedbackType.TextHandleMove (the text-handle-drag level), not LongPress. For a more pronounced vibration you must pass it explicitly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/ScrollEndHaptic.kt:125`)

**State** The node internally holds a three-state enum (Idle / TopBoundaryHit / BottomBoundaryHit), set on hitting a boundary, reset only after scrolling more than 1px from the boundary toward the content, and zeroed on onDetach. Completely stateless and callback-free externally.

**vs Material3** No counterpart. Neither foundation nor material3 provides scroll-boundary haptics; the only official near-equivalent is some built-in haptics of LazyList since Compose 1.9, with different semantics.

**Compilable examples** [`example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt:88`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt#L88) · [`example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt:211`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt#L211) · [`example/shared/src/commonMain/kotlin/utils/PageUtils.kt:45`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/utils/PageUtils.kt#L45)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/ScrollEndHaptic.kt:124`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/ScrollEndHaptic.kt#L124)</sub>

## PagerState.springAnimateToPage  ·  interaction utility

Uses the PagerNavigationSpringSpec spring to animate the pager to a target page, for TabRow / navigation-item clicks, replacing animateScrollToPage. A suspend function, to be called in a coroutine.

> Animates to [target] using [PagerNavigationSpringSpec] after the first layout.
> Uses [MutatePriority.UserInput] so focus scrolling cannot interrupt the animation.

```kotlin
import top.yukonga.miuix.kmp.utils.springAnimateToPage

suspend fun PagerState.springAnimateToPage(
    target: Int,  // required
)
```

**Traps**

- 🟡 When target is not within 0 until pageCount it returns directly, without clamping and without throwing; the native animateScrollToPage clamps an out-of-range page index into the legal range. Passing pageCount or -1 does nothing.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:94`)
- 🟡 It runs with MutatePriority.UserInput: a Default-priority scroll such as a focus scroll cannot interrupt it, while it itself interrupts an in-progress same-level scroll (including a pager being dragged by the user). Conversely, under CrossAxis mode any new press cancels it at the same-level priority and snaps to the page nearest at that moment.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:95`)
- ⚪ When the page hasn't finished its first layout (layoutInfo.pageSize == 0) it doesn't animate and just sets currentPage to the target page.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:109`)

**State** It only reads and writes the passed-in PagerState. As soon as the animation starts it updateTargetPage(target), so pagerState.targetPage immediately becomes the target page, while currentPage changes as the scroll passes through intermediate pages; which one TabRow's selectedTabIndex is bound to determines whether the indicator jumps directly or steps page by page.

**vs Material3** Corresponds to PagerState.animateScrollToPage. Differences: no pageOffsetFraction or animationSpec parameters, the spring is fixed to PagerNavigationSpringSpec (the native default is a StiffnessMediumLow spring); across multiple pages the native one first jumps near the target then animates, while here it scrolls all the way by the actual distance and every intermediate page gets composed; an out-of-range target is ignored directly rather than clamped; the priority is UserInput rather than Default.

**Compilable examples** [`example/shared/src/commonMain/kotlin/AppContent.kt:829`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L829) · [`example/shared/src/commonMain/kotlin/component/TabRowSection.kt:63`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/TabRowSection.kt#L63)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:93`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt#L93)</sub>

## WindowNavigationEventScope  ·  interaction utility

An expect/actual composable function that rebinds the handling of back events (predictive back) to the dispatcher of the platform window that hosts the content. You only need to write it by hand when you build your own standalone window host.

> Rebinds back-event handling to the platform window hosting [content].
> 
> On Android a separate platform window (such as a platform `Dialog`) receives system back events
> through its own dispatcher only. A `LocalNavigationEventDispatcherOwner` explicitly provided in
> the host composition is inherited across the window boundary and would register back handlers
> on a dispatcher that never sees this window's events, so this scope re-resolves the owner from
> the window's view tree; when no view-tree owner exists, the inherited value is kept. The
> resolution matches the local's own host-default path, so behavior is unchanged when nothing was
> explicitly provided.
> 
> On Skiko platforms dialogs are layered inside the host window and this scope is a pass-through.
> 
> The Window* components in this library apply it automatically; wrap the root of a custom
> separate-window host whose content uses predictive-back handlers.

```kotlin
import top.yukonga.miuix.kmp.utils.WindowNavigationEventScope

@Composable
expect fun WindowNavigationEventScope(
    content: @Composable () -> Unit,  // required
)
```

Platform impls: androidMain, commonMain, skikoMain

**Traps**

- ⚪ The library's WindowDialog / WindowBottomSheet / WindowListPopup / WindowCascadingListPopup already wrap this layer automatically. Wrapping it again inside these components' content is redundant (harmless but useless). The only case that truly needs hand-writing is "a custom standalone window host + a predictive back handler used inside the content".  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowDialog.kt:96`)
- 🟡 On Android, if no NavigationEventDispatcherOwner is found in the window's view tree, it silently keeps the inherited value (takes the else branch and calls content() directly), with no error and no downgrade notice. In that case a back handler registered inside is attached to a dispatcher that never receives this window's events, manifesting as "the back key does nothing".  (`miuix-ui/src/androidMain/kotlin/top/yukonga/miuix/kmp/utils/WindowNavigationEventScope.android.kt:21`)
- ⚪ owner is cached with remember(view) and re-resolved only when LocalView changes. If the dispatcher owner is attached to the view tree only after the window is created, it keeps using the null read at the start.  (`miuix-ui/src/androidMain/kotlin/top/yukonga/miuix/kmp/utils/WindowNavigationEventScope.android.kt:18`)
- ⚪ The actual on non-Android (skiko: desktop / iOS / web) is only one line, content(), a pure pass-through -- because on those platforms dialogs are stacked inside the host window with no window boundary to cross. Do not expect it to do anything on desktop.  (`miuix-ui/src/skikoMain/kotlin/top/yukonga/miuix/kmp/utils/WindowNavigationEventScope.skiko.kt:11`)

**State** Stateless. It does only one CompositionLocal override (LocalNavigationEventDispatcherOwner) and holds no mutable state.

**vs Material3** No counterpart. material3's Dialog / ModalBottomSheet rely on androidx.activity's BackHandler + LocalOnBackPressedDispatcherOwner, and cross-window owner rebinding is handled internally by Compose's DialogWrapper; Miuix takes the newer androidx.navigationevent system, which is why this explicit scope function is needed.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/WindowNavigationEventScope.kt:25`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/WindowNavigationEventScope.kt#L25)</sub>

## Top-level properties & CompositionLocals (2)

- `LocalOverScrollState = compositionLocalOf { … }`  <sub>[`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt:482`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/Overscroll.kt#L482)</sub>
- `PagerNavigationSpringSpec: SpringSpec<Float>`  <sub>[`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:83`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt#L83)</sub>
  The spring used for Miuix pager paging (stiffness 322.2, damping ratio about 0.9, visibilityThreshold 0.5f), used by both springAnimateToPage and CrossAxis mode's release-snap.
  - ⚪ In native mode (Native / TapToHalt) HorizontalPager still uses its own flingBehavior, so the feel is inconsistent with the Tab-click spring. To unify them, pass flingBehavior = PagerDefaults.flingBehavior(state = pagerState, snapAnimationSpec = PagerNavigationSpringSpec) as the sample does. It is a SpringSpec<Float> and can only be used on Float animations.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:83`)

## Public types in this topic (13)

- `MiuixIndication(color: Color)` **class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.utils.MiuixIndication`
- `MiuixOverscrollEffect` **class** · `import top.yukonga.miuix.kmp.utils.MiuixOverscrollEffect`
- `MiuixOverscrollFactory` **object** · `import top.yukonga.miuix.kmp.utils.MiuixOverscrollFactory`
- `MiuixPopupUtils` **class** · `import top.yukonga.miuix.kmp.utils.MiuixPopupUtils`
- `MiuixPopupUtils.DialogState(showState: MutableState<Boolean>, zIndex: Float)` **class** (required: showState, zIndex) · `import top.yukonga.miuix.kmp.utils.MiuixPopupUtils`
- `MiuixPopupUtils.PopupState(showState: MutableState<Boolean>, zIndex: Float)` **class** (required: showState, zIndex) · `import top.yukonga.miuix.kmp.utils.MiuixPopupUtils`
- `OverScrollState` **class** · `import top.yukonga.miuix.kmp.utils.OverScrollState`
- `PagerFlingTrackerConnection` **class** · `import top.yukonga.miuix.kmp.utils.PagerFlingTrackerConnection`
- `PagerGestureNestedScrollConnection` **object** · `import top.yukonga.miuix.kmp.utils.PagerGestureNestedScrollConnection`
- `PagerInterceptionMode` **enum** — Native, CrossAxisInterceptor, TapToHalt · `import top.yukonga.miuix.kmp.utils.PagerInterceptionMode`
- `PressFeedbackType` **enum** — None, Sink, Tilt · `import top.yukonga.miuix.kmp.utils.PressFeedbackType`
- `SinkFeedback(sinkAmount: Float, animationSpec: AnimationSpec<Float>)` **data class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.utils.SinkFeedback`
- `TiltFeedback(tiltAmount: Float, animationSpec: AnimationSpec<Float>)` **data class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.utils.TiltFeedback`

## Notes on types & namespaces

### PagerFlingTrackerConnection

The NestedScrollConnection used by TapToHalt mode: in onPreFling it records whether the child is doing a vertical inertia (isChildFlinging); after being set haltFling on press, it throws a CancellationException in the child inertia's next-frame onPreScroll to cut off the inertia, and in onPostFling swallows the remaining vertical velocity so it isn't passed to the outer layer.

**Traps**

- 🟡 isChildFlinging and haltFling are read-only externally (internal set); the caller cannot trigger a halt manually and can only read them to drive the UI. You also don't need to Modifier.nestedScroll(tracker) yourself: iosStyleMomentumHalt already attaches this connection on its own node, and only attaching it on the pager's modifier (the ancestor of the page's inner list) can receive the child list's fling.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:418`)
- ⚪ It only recognizes vertical: isChildFlinging = available.y != 0f, and the halt too only takes effect in the y direction. A horizontal list's inertia in the page is not recognized.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:394`)

### PagerGestureNestedScrollConnection

The NestedScrollConnection singleton paired with CrossAxis mode: it only swallows the remaining horizontal velocity in onPostFling and leaves the vertical velocity unchanged for the outer layer, without overriding onPreScroll/onPostScroll. Per the KDoc, vertical scroll and velocity are left to the page content, including when the pager rests between two pages.

**Traps**

- 🟡 It is passed to HorizontalPager's pageNestedScrollConnection parameter, not attached with Modifier.nestedScroll on the page's inner list or on the pager's modifier. It is used only in CrossAxis mode; the official docs require Native / TapToHalt modes to restore the pager defaults, and the sample switches between it and PagerDefaults.pageNestedScrollConnection(pagerState, Orientation.Horizontal) by mode.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:128`)

### PagerInterceptionMode

The three modes of pagerGestureOverride: Native (native gesture, modifier is a no-op), CrossAxisInterceptor (a horizontal swipe can interrupt the paging process and child-list scroll, the default), TapToHalt (during a child list's inertia the first horizontal swipe only halts, doesn't page).

**Traps**

- ⚪ The title field is a display name for the settings UI; Native's title is "Default," but pagerGestureOverride's default mode is CrossAxisInterceptor (title "Cross-Axis"). Judging whether it is the default mode by title == "Default" is wrong.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:67`)
- ⚪ The ordinal order is the persistence format: Native = 0, CrossAxisInterceptor = 1, TapToHalt = 2; the mode: Int overload is interpreted in this order, out of range falls to Native. When persisting, store the ordinal rather than the name to be more resilient to enum renames.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/PagerGestureUtils.kt:65`)

