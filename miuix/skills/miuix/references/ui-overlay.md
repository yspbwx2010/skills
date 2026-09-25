# Overlays

The Overlay* and Window* families of Dialog / BottomSheet / ListPopup, and overlay content layout. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## OverlayBottomSheet  ·  Overlay overlay

A bottom sheet rendered inside the Compose tree; its height adapts to content and does not go past the status bar; it has a drag handle, nested-scroll takeover, and predictive-back preview. Use it when it needs to be clipped by a Scaffold, otherwise prefer WindowBottomSheet.

> A bottom sheet that slides up from the bottom of the screen.
> The height adapts to the content size, but will not cover the status bar area.

```kotlin
import top.yukonga.miuix.kmp.overlay.OverlayBottomSheet

@Composable
fun OverlayBottomSheet(
    show: Boolean,  // required
    modifier: Modifier = Modifier,
    title: String? = null,
    startAction: @Composable (() -> Unit)? = null,
    endAction: @Composable (() -> Unit)? = null,
    backgroundColor: Color = BottomSheetDefaults.backgroundColor(),
    enableWindowDim: Boolean = true,
    cornerRadius: Dp = BottomSheetDefaults.cornerRadius,
    sheetMaxWidth: Dp = BottomSheetDefaults.maxWidth,
    onDismissRequest: (() -> Unit)? = null,
    onDismissFinished: (() -> Unit)? = null,
    outsideMargin: DpSize = BottomSheetDefaults.outsideMargin,
    insideMargin: DpSize = BottomSheetDefaults.insideMargin,
    defaultWindowInsetsPadding: Boolean = true,
    dragHandleColor: Color = BottomSheetDefaults.dragHandleColor(),
    allowDismiss: Boolean = true,
    enableNestedScroll: Boolean = true,
    renderInRootScaffold: Boolean = true,
    content: @Composable () -> Unit,  // required
)
```

- `show` — Whether the [OverlayBottomSheet] is shown.
- `modifier` — The modifier to be applied to the [OverlayBottomSheet].
- `title` — Optional title to display at the top of the [OverlayBottomSheet].
- `startAction` — Optional [Composable] to display on the start side of the title (e.g. a close button).
- `endAction` — Optional [Composable] to display on the end side of the title (e.g. a submit button).
- `backgroundColor` — The background color of the [OverlayBottomSheet].
- `enableWindowDim` — Whether to dim the window behind the [OverlayBottomSheet].
- `cornerRadius` — The corner radius of the top corners of the [OverlayBottomSheet].
- `sheetMaxWidth` — The maximum width of the [OverlayBottomSheet].
- `onDismissRequest` — Will called when the user tries to dismiss the Dialog by clicking outside or pressing the back button.
- `onDismissFinished` — The callback when the [OverlayBottomSheet] is completely dismissed.
- `outsideMargin` — The margin outside the [OverlayBottomSheet].
- `insideMargin` — The margin inside the [OverlayBottomSheet].
- `defaultWindowInsetsPadding` — Whether to apply default window insets padding.
- `dragHandleColor` — The color of the drag handle at the top.
- `allowDismiss` — Whether to allow dismissing the sheet via drag or back gesture.
- `enableNestedScroll` — Whether to enable nested scrolling for the content.
- `renderInRootScaffold` — Whether to render the bottom sheet in the root (outermost) Scaffold.   When true (default), the bottom sheet covers the full screen. When false, it renders within the   current Scaffold's bounds.
- `content` — The [Composable] content of the [OverlayBottomSheet].

**Traps**

- 🔴 Must be inside a Scaffold, otherwise it silently does not show (same as OverlayDialog).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/MiuixPopupUtils.kt:596`)
- 🔴 allowDismiss = false does not block LocalDismissState. The internal requestDismiss does not check allowDismiss at all, and it is injected into all three slots content, startAction, endAction -- so when using allowDismiss = false to "force staying inside the sheet", a close button in any of those slots calling LocalDismissState can still close it.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/BottomSheetContentLayout.kt:181`)
- 🟡 allowDismiss gates three paths rather than the two the docs claim: the pull-down gesture, the back gesture, and tapping the scrim's outside area. All three are turned off by the same switch.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/BottomSheetContentLayout.kt:258`)
- 🔴 onDismissRequest is nullable and defaults to null. When null, the pull-down gesture still slides the whole sheet off screen (animateDismissOffScreen runs anyway), but the callback no-ops and show is still true -- the result is a sheet that is invisible yet still composed and can never come back. Either pass a callback, or use allowDismiss = false.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/BottomSheetContentLayout.kt:182`)
- ⚪ The dismiss threshold is hardcoded and not configurable: displacement over 150.dp with no clear upward velocity, or downward velocity over 800.dp/s (the source converts dp to px and uses it as a px/s threshold, with a comment admitting this is a deliberate dimensional approximation). To make it harder/easier to close you can only wrap the gesture yourself outside.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/BottomSheetContentLayout.kt:400`)
- 🟡 The nested-scroll takeover is a "one-time decision on the first frame of a single gesture": if the inner list consumes any scroll on the gesture's first frame (i.e. the list is not scrolled to the top), the whole gesture will not drag the sheet, and you must release and press again. This deliberately avoids a mid-gesture jump, but users feel "scrolled to the top yet cannot drag".  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/BottomSheetContentLayout.kt:489`)
- ⚪ There is no large-screen branch at all. The docs' line "supports large-screen optimized animation" was copied from the dialog page; BottomSheetContentLayout has no isLargeScreen anywhere; the only wide-screen adaptation is sheetMaxWidth defaulting to 640.dp for width-limited centering.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/BottomSheetContentLayout.kt:883`)

**Spec** corner 28.dp (BottomSheetDefaults.cornerRadius, top two corners only) · max_width 640.dp (BottomSheetDefaults.maxWidth) · outside_margin DpSize(0.dp, 0.dp) · inside_margin DpSize(24.dp, 0.dp) · drag_handle 45×4.dp, on press the width animates to 55.dp with scaleY 1.15; opacity lerp(0.2, 0.35) between unpressed/pressed, applied over dragHandleColor · enter_exit folmeSpring(damping 0.9, response 0.38); when closed by being dragged away, no exit animation plays and animationProgress directly snapTo(0)

**State** Controlled show + self-held gesture state. Drag displacement, spring-back, nested-scroll decision, and predictive-back progress are all managed by internal Animatables, which the outside cannot get and need not remember. onDismissRequest is likewise only a request. LocalDismissState is injected into the three slots content / startAction / endAction (note it bypasses allowDismiss). onDismissFinished fires after the exit ends.

**vs Material3** Corresponds to androidx.compose.material3.ModalBottomSheet + rememberModalBottomSheetState. Differences: Miuix has no SheetState, no partiallyExpanded / halfExpanded tiers and no skipPartiallyExpanded, only expanded and closed states; there is no need for (and no) suspend hide(), you just change the show boolean; allowDismiss roughly corresponds to M3's confirmValueChange + property switches, but LocalDismissState bypasses it; BottomSheetDefaults is in the top.yukonga.miuix.kmp.layout package (not the window/overlay package), which is easy to get wrong on import.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayBottomSheetDemo.kt:58`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayBottomSheetDemo.kt#L58) · [`example/shared/src/commonMain/kotlin/AboutPage.kt:446`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L446) · [`example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt:116`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt#L116)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/overlay/OverlayBottomSheet.kt:46`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/overlay/OverlayBottomSheet.kt#L46)</sub>

## OverlayCascadingListPopup  ·  Overlay overlay

A two-level cascading menu rendered inside the Compose tree: the submenu morphs and grows out of the tapped row while the first level shrinks and gets a semi-transparent scrim over it. Depth is hard-limited to 2 levels, it accepts only entries data, and there is no content slot.

> A cascading list popup rendered inside the host `Scaffold`. Cascading depth is limited to 2.

```kotlin
import top.yukonga.miuix.kmp.overlay.OverlayCascadingListPopup

@Composable
fun OverlayCascadingListPopup(
    show: Boolean,  // required
    entries: List<DropdownEntry>,  // required
    onDismissRequest: () -> Unit,  // required
    popupModifier: Modifier = Modifier,
    onDismissFinished: (() -> Unit)? = null,
    popupPositionProvider: PopupPositionProvider = ListPopupDefaults.DropdownPositionProvider,
    alignment: PopupPositionProvider.Align = PopupPositionProvider.Align.End,
    enableWindowDim: Boolean = true,
    maxHeight: Dp? = null,
    minWidth: Dp = 200.dp,
    renderInRootScaffold: Boolean = true,
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    collapseOnSelection: Boolean = true,
)
```

- `show` — Whether the popup is shown.
- `entries` — Grouped dropdown entries; top-level [DropdownItem]s with non-empty   [DropdownItem.children] become submenu triggers. Keep the entry and item order stable while the   popup is shown; item state such as [DropdownItem.selected] may change.
- `onDismissRequest` — Invoked when the popup wants to be dismissed.
- `popupModifier` — Modifier applied to the popup body.
- `onDismissFinished` — Invoked after the exit animation finishes.
- `popupPositionProvider` — Position strategy for the primary popup relative to its anchor.
- `alignment` — Alignment of the primary popup.
- `enableWindowDim` — Whether to dim the rest of the window while the popup is shown.
- `maxHeight` — Maximum height of either side. Null bounds it by the safe area.
- `minWidth` — Minimum width of the popup.
- `renderInRootScaffold` — Whether to render in the outermost Scaffold.
- `dropdownColors` — Colors used by every row.
- `collapseOnSelection` — When true, selecting any leaf dismisses the popup.

**Traps**

- 🟡 onDismissRequest is two-stage, not "tap outside to close": when the second level is expanded, tapping outside or pressing back only collapses the second level and does not call onDismissRequest; closing the whole popup takes two actions. This is especially easy to hit when writing automated tests or using the back key for navigation.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingListPopupLayout.kt:257`)
- 🟡 Depth is hard-limited to 2 levels: third-level and deeper children are simply ignored. The docs say "silently ignored", but in reality it prints a one-line warning to stdout via println, and a file-level mutable global deeperChildrenWarned ensures it prints only once per process -- it is neither an exception nor via Logger, so it is easy to miss.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingMorphContent.kt:121`)
- 🟡 A first-level item's DropdownItem.onClick is swallowed when children is non-empty (a tap always becomes expanding the submenu); but a second-level leaf item's onClick is called normally. So the rule "onClick is ignored when there are children" only holds for the first level; do not assume the second level also relies on some other callback.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingListPopupLayout.kt:326`)
- 🔴 entries must keep a stable structure while the popup is showing. The component tracks the currently expanded item by (entryIndex, itemIndex) position (positionOf locates it internally with reference equality ===), so inserting/deleting/reordering items while the popup is open makes the submenu jump to a different item or auto-collapse. An item's values (selected, text, etc.) can change freely, which is exactly the point of tracking by position rather than object. Also, creating a new listOf(...) on every recomposition in the composable body does work (relocating each frame), but DropdownItem.children's KDoc explicitly requires stabilizing this list with remember.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingListPopupLayout.kt:78`)
- 🟡 There is no content slot; you can only describe the content with entries: List<DropdownEntry>; to place custom rows (a switch, a slider, an arbitrary composable) you must switch to OverlayListPopup and assemble ListPopupColumn yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/overlay/OverlayCascadingListPopup.kt:56`)
- ⚪ The default alignment is Align.End, while OverlayListPopup's default is Align.Start. Mixing the two gives inconsistent alignment directions under the same anchor.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/overlay/OverlayCascadingListPopup.kt:50`)
- ⚪ With collapseOnSelection = false, after selecting a leaf it neither closes the popup nor collapses the second level (clearing the expanded state and dismiss are in the same if branch), so the UI stays on the second level. For "return to the first level after selecting" you must control show and reopen yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingListPopupLayout.kt:327`)
- ⚪ The second level is internally also a ListPopupColumn, and the cloned header row and the divider below it each count as one "item", which counts toward ListPopupColumn's height viewport that only shows the first 8 items -- so the second level can actually only show 6 child items, and from the 7th on it must scroll.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingMorphContent.kt:362`)

**Spec** corner 16.dp (CascadingPopupCornerRadius) · shadow The first-level panel has a dropShadow: radius 24.dp, Color.Black alpha 0.18, offset (0, 6.dp) -- a plain ListPopup has no shadow at all, which is one visual inconsistency between the two · expand The first level shrinks to scale 0.95 and gets a scrim; the second level grows by linearly interpolating the four sides of the anchor-row rect; the trigger row's arrow rotates ∓90° (reversed in RTL) · springs Expand folmeSpring(damping 0.99, response 0.45), collapse response 0.2; arrow expand 0.2 / collapse 0.3 · min_width 200.dp (a default hardcoded by this component itself, not ListPopupDefaults.MinWidth)

**State** Controlled show + entries; the second level's expanded state is entirely held internally by the component (expandedItemPosition / displayedItemPosition are two separate states, the logical state responds immediately while the render state waits for the collapse spring to end), which the outside can neither read nor control. onDismissRequest here is required and non-null (unlike the nullable one on ListPopup / Dialog). entries should be stabilized with remember.

**vs Material3** No equivalent. Material3 has no cascading/morph menu, and to achieve a similar effect you must nest DropdownMenus yourself, with none of the behaviors (morph, two-stage back, anchor freeze) mapping over.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayCascadingListPopupDemo.kt:90`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayCascadingListPopupDemo.kt#L90)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/overlay/OverlayCascadingListPopup.kt:43`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/overlay/OverlayCascadingListPopup.kt#L43)</sub>

## OverlayDialog  ·  Overlay overlay

A dialog rendered inside the Compose tree, attached to the host Scaffold's popup slot; on small screens it slides in flush with the bottom, on large screens it scale-fades in centered. Use it when it needs to be clipped by a Scaffold or to coordinate with a Scaffold's layering, otherwise prefer WindowDialog.

> A dialog with a title, a summary, and other contents.

```kotlin
import top.yukonga.miuix.kmp.overlay.OverlayDialog

@Composable
fun OverlayDialog(
    show: Boolean,  // required
    modifier: Modifier = Modifier,
    title: String? = null,
    titleColor: Color = DialogDefaults.titleColor(),
    summary: String? = null,
    summaryColor: Color = DialogDefaults.summaryColor(),
    backgroundColor: Color = DialogDefaults.backgroundColor(),
    enableWindowDim: Boolean = true,
    onDismissRequest: (() -> Unit)? = null,
    onDismissFinished: (() -> Unit)? = null,
    outsideMargin: DpSize = DialogDefaults.outsideMargin,
    insideMargin: DpSize = DialogDefaults.insideMargin,
    defaultWindowInsetsPadding: Boolean = true,
    renderInRootScaffold: Boolean = true,
    maxWidth: Dp = DialogDefaults.MaxWidth,
    largeScreen: Boolean? = null,
    cornerRadius: Dp? = null,
    content: @Composable () -> Unit,  // required
)
```

- `show` — Whether the [OverlayDialog] is shown.
- `modifier` — The modifier to be applied to the [OverlayDialog].
- `title` — The title of the [OverlayDialog].
- `titleColor` — The color of the title.
- `summary` — The summary of the [OverlayDialog].
- `summaryColor` — The color of the summary.
- `backgroundColor` — The background color of the [OverlayDialog].
- `enableWindowDim` — Whether to enable window dimming when the [OverlayDialog] is shown.
- `onDismissRequest` — Will called when the user tries to dismiss the Dialog by clicking outside or pressing the back button.
- `onDismissFinished` — The callback when the [OverlayDialog] is completely dismissed.
- `outsideMargin` — The margin outside the [OverlayDialog].
- `insideMargin` — The margin inside the [OverlayDialog].
- `defaultWindowInsetsPadding` — Whether to apply default window insets padding to the [OverlayDialog].
- `renderInRootScaffold` — Whether to render the dialog in the root (outermost) Scaffold.   When true (default), the dialog covers the full screen. When false, it renders within the   current Scaffold's bounds.
- `maxWidth` — The maximum width of the [OverlayDialog].
- `largeScreen` — Optional override for the large-screen presentation (centered scale/fade   instead of bottom slide-in). If null, detected from the window size.
- `cornerRadius` — Optional corner radius override. If null, [DialogDefaults.CornerRadius]   for the centered presentation, or derived from the screen corner radius (clamped to   32dp..48dp) when bottom-attached.
- `content` — The [Composable] content of the [OverlayDialog].

**Traps**

- 🔴 Must be inside a Scaffold. Intuitively writing it in any composable compiles and runs, but LocalDialogStates gets the staticCompositionLocalOf default empty list, and the state registers into a list no host iterates -- the dialog silently does not show, with no exception and no log.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/MiuixPopupUtils.kt:596`)
- 🔴 onDismissRequest is nullable and defaults to null. Not passing it makes the dialog completely uncloseable: tapping the outside area goes through currentOnDismiss?.invoke(), and the back key is the same callback, so when null both paths no-op. For an "uncloseable" dialog this is exactly right, but to make it closeable you must pass it explicitly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/DialogContentLayout.kt:376`)
- 🟡 show = false does not mean immediate unload. The internal internalVisible only becomes false after the exit animation (260ms) finishes, and during that time the whole content subtree is still composed. To do something "after it fully disappears" (reset a form, navigate) you must use onDismissFinished; doing it right where show is set false collides with the still-playing animation.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/DialogContentLayout.kt:163`)
- 🟡 Large and small screens are two completely different presentations, with the breakpoint "window width >= 840dp and height >= 480dp": large screen is centered + scale 0.8→1 fade-in + height capped at 2/3 of window height; small screen is bottom-flush, slides in via full-window-height translationY, with no height cap. On desktop, dragging the window across the breakpoint makes the whole layout jump; for fixed behavior pass largeScreen explicitly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/DialogContentLayout.kt:422`)
- ⚪ When cornerRadius defaults to null, the small-screen corner is "screen physical corner − outsideMargin.width" clamped to 32..48dp (concentric corners). But getRoundedCorner() always returns 0.dp on Skiko (desktop/iOS/Web), so on non-Android platforms it is always the lower bound 32dp, and adjusting outsideMargin does not change it. For a different corner you must pass cornerRadius explicitly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/DialogContentLayout.kt:305`)

**Spec** max_width 420.dp (DialogDefaults.MaxWidth) · corner Large screen 32.dp (DialogDefaults.CornerRadius); small screen = screen physical corner − outsideMargin.width, clamped to 32..48dp, always 32.dp on Skiko · outside_margin DpSize(12.dp, 12.dp) · inside_margin DpSize(24.dp, 24.dp) · large_screen_height_cap window height × 2/3 · enter Large screen: scale 0.8→1 + alpha 0→1 under folmeSpring(damping 0.9, response 0.3); small screen: full-window-height translationY slide-in under spring(0.88, 450) · exit tween 260ms DecelerateEasing(1.5)

**State** Purely controlled. show is held by the caller, onDismissRequest is only a "close request", and the component never changes show itself -- forgetting to set false in the callback makes it uncloseable forever. onDismissFinished fires once after the exit animation ends. Inside content you can read LocalDismissState to get the close entry point, without passing the callback down. Apart from show you need not remember anything (the animation state is held internally by the component).

**vs Material3** Corresponds to androidx.compose.material3.AlertDialog / BasicAlertDialog. Differences: M3's is a platform Dialog window with onDismissRequest required, while the Miuix Overlay version is inside the Compose tree, requires a Scaffold, and has a nullable onDismissRequest (null means uncloseable); there are no confirmButton / dismissButton / icon slots, buttons are laid out in content yourself; small screen defaults to bottom-flush rather than centered; there is no DialogProperties, and things like dismissOnClickOutside can only be expressed by whether the callback is null.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayDialogDemo.kt:48`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayDialogDemo.kt#L48) · [`example/shared/src/commonMain/kotlin/component/ArrowSection.kt:111`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ArrowSection.kt#L111) · [`example/shared/src/commonMain/kotlin/component/CardSection.kt:144`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/CardSection.kt#L144) · [`example/shared/src/commonMain/kotlin/component/DialogSection.kt:141`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/DialogSection.kt#L141)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/overlay/OverlayDialog.kt:47`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/overlay/OverlayDialog.kt#L47)</sub>

## OverlayListPopup  ·  Overlay overlay

An anchored list popup rendered inside the Compose tree (the dropdown menu itself), revealed by scaling from the anchor direction + directional clipping. The content is usually filled with ListPopupColumn + DropdownImpl.

> A popup with a list of items.

```kotlin
import top.yukonga.miuix.kmp.overlay.OverlayListPopup

@Composable
fun OverlayListPopup(
    show: Boolean,  // required
    popupModifier: Modifier = Modifier,
    popupPositionProvider: PopupPositionProvider = ListPopupDefaults.DropdownPositionProvider,
    alignment: PopupPositionProvider.Align = PopupPositionProvider.Align.Start,
    enableWindowDim: Boolean = true,
    onDismissRequest: (() -> Unit)? = null,
    onDismissFinished: (() -> Unit)? = null,
    maxHeight: Dp? = null,
    minWidth: Dp = ListPopupDefaults.MinWidth,
    renderInRootScaffold: Boolean = true,
    content: @Composable () -> Unit,  // required
)
```

- `show` — Whether the [OverlayListPopup] is shown.
- `popupModifier` — The modifier to be applied to the [OverlayListPopup].
- `popupPositionProvider` — The [PopupPositionProvider] of the [OverlayListPopup].
- `alignment` — The alignment of the [OverlayListPopup].
- `enableWindowDim` — Whether to enable window dimming when the [OverlayListPopup] is shown.
- `onDismissRequest` — The callback when the [OverlayListPopup] is dismissed.
- `onDismissFinished` — The callback when the [OverlayListPopup] is completely dismissed (after exit animation).
- `maxHeight` — The maximum height of the [OverlayListPopup]. If null, the height will be calculated automatically.
- `minWidth` — The minimum width of the [OverlayListPopup].
- `renderInRootScaffold` — Whether to render the popup in the root (outermost) Scaffold.   When true (default), the popup covers the full screen. When false, it renders within the   current Scaffold's bounds with position compensation.
- `content` — The [Composable] content of the [OverlayListPopup]. You should use the [ListPopupColumn] in general.

**Traps**

- 🔴 The four corner values of PopupPositionProvider.Align (TopStart / TopEnd / BottomStart / BottomEnd) are all ineffective under the default ListPopupDefaults.DropdownPositionProvider and equal Start: that provider only checks alignment.resolve(...) == Align.End and sends everything else to the else branch. The corner semantics only hold when you explicitly pass ListPopupDefaults.ContextMenuPositionProvider, and even then the direction is reversed -- TopStart/TopEnd put the popup below the anchor, BottomStart/BottomEnd put it above (Align's KDoc says "relative to the window, not relative to the anchor"). This repo's own demo hits this pitfall, passing Align.TopStart yet pairing it with the default provider.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:250`)
- 🟡 The flip side of the previous entry: docs/demo/src/commonMain/kotlin/WindowListPopupDemo.kt:47 passes Align.TopStart with the default provider, and actually gets Start behavior. Copying the official demo gives a position that does not match expectations.  (`docs/demo/src/commonMain/kotlin/WindowListPopupDemo.kt:47`)
- 🔴 Must be inside a Scaffold, otherwise it silently does not show (same as OverlayDialog; the list popup uses the LocalPopupStates default empty list).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/MiuixPopupUtils.kt:595`)
- 🔴 There is no anchor parameter: the anchor is "the parent layout node the call site sits in". The component puts a zero-size Spacer inside and reverse-looks-up the parent container rect via parentLayoutCoordinates.positionInWindow(). So you must write OverlayListPopup and the trigger button into the same parent container (typically Box { IconButton(...); OverlayListPopup(...) }); putting it alone at the top of a Column makes the anchor the whole Column, and the popup hugs the entire column rather than the button. The Box in the example is the anchor itself, not layout sugar.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/ListPopupLayout.kt:127`)
- 🟡 When the parent coordinates cannot be obtained (parentBounds is still IntRect.Zero) the whole popup simply returns, neither rendering nor erroring. A parent node with size 0 or not yet measured shows this behavior; when debugging, do not suspect show.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/ListPopupLayout.kt:139`)
- 🟡 popupModifier applies to the full-screen overlay, not the popup card. You cannot change the card's background/corner: the 16.dp corner and surfaceContainer background are hardcoded in ListPopupContent. Adding a background in popupModifier fills the whole screen.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/ListPopupLayout.kt:193`)
- ⚪ enableWindowDim = false only skips drawing the scrim; tapping outside the popup still triggers onDismissRequest (the outside-tap gesture is on the full-screen Box, unrelated to the dim). For "tapping outside does not close" you can only omit onDismissRequest.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/ListPopupLayout.kt:199`)
- 🟡 onDismissRequest is nullable and defaults to null; without it, neither tapping outside nor the back key can close it.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/ListPopupLayout.kt:149`)
- ⚪ With renderInRootScaffold = false (attached to an inner Scaffold), on the first frame hostPositionInWindow is still Offset.Zero, and the window-coordinate→local-coordinate compensation is only correct after the onGloballyPositioned callback, so under a nested Scaffold it can theoretically be misaligned for one frame. The cascading version has a hostMeasured guard for this, this one does not.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/ListPopupLayout.kt:91`)

**Spec** corner 16.dp (hardcoded in ListPopupContent) · background MiuixTheme.colorScheme.surfaceContainer (hardcoded) · min_width ListPopupDefaults.MinWidth = 200.dp · min_height ListPopupDefaults.MinPopupHeight = 50.dp · enter scale 0.15→1 (spring dampingRatio 0.82 / stiffness 362.5) + alpha tween 200ms + squircle clip reveal expanding from the anchor direction · exit alpha tween 150ms as the master clock, and the other tracks then forcibly snapTo(0) · dim MiuixTheme.colorScheme.windowDimming, enter tween 300ms / exit 150ms (SinOutEasing)

**State** Controlled show, no internal expanded state. The four animation tracks (fraction / alpha / dim / back) and anchor detection are all held internally by the component, and the outside only needs to remember a Boolean. Inside content you can read LocalDismissState to close. When the popup closes the whole subtree unloads, so ListPopupColumn's scroll position returns to the top on every reopen.

**vs Material3** Corresponds to androidx.compose.material3.DropdownMenu (and the menu part of ExposedDropdownMenuBox). Differences: M3 uses expanded + onDismissRequest with the anchor being the Box it sits in, while Miuix reverse-looks-up the parent layout node with a more hidden anchor rule; M3 has offset: DpOffset for fine positioning, Miuix can only swap the PopupPositionProvider; M3's DropdownMenuItem ≈ Miuix's DropdownImpl; most importantly, M3's DropdownMenu is a platform Popup that can overflow the host, while the Overlay version cannot (for overflow use WindowListPopup).

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayListPopupDemo.kt:46`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayListPopupDemo.kt#L46)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/overlay/OverlayListPopup.kt:37`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/overlay/OverlayListPopup.kt#L37)</sub>

## WindowBottomSheet  ·  Window overlay

A bottom sheet rendered as a platform Dialog window, needing no Scaffold. Its visuals, gestures, and animation are identical to OverlayBottomSheet (they share BottomSheetContentLayout).

> A bottom sheet that slides up from the bottom of the screen, rendered at window level without `Scaffold`.
> 
> Use [LocalDismissState] inside `content` to request dismissal from inner composables.

```kotlin
import top.yukonga.miuix.kmp.window.WindowBottomSheet

@Composable
fun WindowBottomSheet(
    show: Boolean,  // required
    modifier: Modifier = Modifier,
    title: String? = null,
    startAction: @Composable (() -> Unit)? = null,
    endAction: @Composable (() -> Unit)? = null,
    backgroundColor: Color = BottomSheetDefaults.backgroundColor(),
    enableWindowDim: Boolean = true,
    cornerRadius: Dp = BottomSheetDefaults.cornerRadius,
    sheetMaxWidth: Dp = BottomSheetDefaults.maxWidth,
    onDismissRequest: (() -> Unit)? = null,
    onDismissFinished: (() -> Unit)? = null,
    outsideMargin: DpSize = BottomSheetDefaults.outsideMargin,
    insideMargin: DpSize = BottomSheetDefaults.insideMargin,
    defaultWindowInsetsPadding: Boolean = true,
    dragHandleColor: Color = BottomSheetDefaults.dragHandleColor(),
    allowDismiss: Boolean = true,
    enableNestedScroll: Boolean = true,
    content: @Composable () -> Unit,  // required
)
```

- `show` — Whether the [WindowBottomSheet] is shown.
- `modifier` — The modifier to be applied to the [WindowBottomSheet].
- `title` — Optional title to display at the top of the [WindowBottomSheet].
- `startAction` — Optional [Composable] to display on the start side of the title (e.g. a close button).
- `endAction` — Optional [Composable] to display on the end side of the title (e.g. a submit button).
- `backgroundColor` — The background color of the [WindowBottomSheet].
- `enableWindowDim` — Whether to dim the window behind the [WindowBottomSheet].
- `cornerRadius` — The corner radius of the top corners of the [WindowBottomSheet].
- `sheetMaxWidth` — The maximum width of the [WindowBottomSheet].
- `onDismissRequest` — Will called when the user tries to dismiss the Dialog by clicking outside or pressing the back button.
- `onDismissFinished` — The callback when the [WindowBottomSheet] is completely dismissed.
- `outsideMargin` — The margin outside the [WindowBottomSheet].
- `insideMargin` — The margin inside the [WindowBottomSheet].
- `defaultWindowInsetsPadding` — Whether to apply default window insets padding.
- `dragHandleColor` — The color of the drag handle at the top.
- `allowDismiss` — Whether to allow dismissing the sheet via drag or back gesture.
- `enableNestedScroll` — Whether to enable nested scrolling for the content.
- `content` — The [Composable] content of the [WindowBottomSheet].

**Traps**

- 🔴 allowDismiss = false does not block LocalDismissState -- and here it is bypassed at two layers: the one WindowBottomSheet itself provides around content does not check allowDismiss, and the one the inner BottomSheetContentLayout overrides likewise does not. A close button in startAction / endAction can still close it.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowBottomSheet.kt:119`)
- ⚪ It has one more close path than the Overlay version: the platform Dialog's own onDismissRequest (desktop Esc, system window close, etc.). It is the only place here that checks allowDismiss, so when allowDismiss = false this path is correctly blocked -- but do not conclude from this that allowDismiss takes effect everywhere (see the previous entry).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowBottomSheet.kt:93`)
- 🔴 onDismissRequest is nullable and defaults to null: when null, the pull-down gesture still slides the sheet off screen but the callback no-ops, and the sheet is both invisible and uncloseable. Same origin as the Overlay version.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/BottomSheetContentLayout.kt:182`)
- ⚪ The two header slots startAction / endAction are also injected with LocalDismissState (the Chinese docs are missing this subsection). Putting a close button in these two slots does not require passing onDismissRequest down.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/BottomSheetContentLayout.kt:307`)
- ⚪ There is no large-screen branch at all; the docs' "large-screen optimized animation" is a mistaken sentence copied from the dialog page; the only wide-screen adaptation is sheetMaxWidth defaulting to 640.dp.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/BottomSheetContentLayout.kt:883`)

**Spec** same_as Identical to OverlayBottomSheet: corner 28.dp, maxWidth 640.dp, outsideMargin (0,0), insideMargin (24,0), handle 45×4.dp (on press 55.dp / scaleY 1.15) · top_inset Extra top safe area = the top padding of max(statusBars, captionBar, displayCutout)

**State** Same as OverlayBottomSheet: controlled show + the component holds all gesture/animation state itself. BottomSheetDefaults is in the top.yukonga.miuix.kmp.layout package, not the window package, which is easy to get wrong on import.

**vs Material3** Corresponds to androidx.compose.material3.ModalBottomSheet. Differences same as OverlayBottomSheet: no SheetState, no intermediate tiers, no suspend hide(); one extra point is that Miuix clears the platform Dialog's scrim and draws its own, while M3's scrim is built in.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowBottomSheetDemo.kt:57`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowBottomSheetDemo.kt#L57) · [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:231`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L231) · [`example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt:161`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt#L161)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowBottomSheet.kt:52`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowBottomSheet.kt#L52)</sub>

## WindowCascadingListPopup  ·  Window overlay

A two-level cascading menu rendered as a platform Dialog window, needing no Scaffold. Its behavior is identical to OverlayCascadingListPopup (they share CascadingListPopupLayout), and depth is likewise hard-limited to 2 levels.

> A cascading list popup rendered at window level (as a [Dialog]) instead of inside a
> `Scaffold`. Otherwise behaves identically to [top.yukonga.miuix.kmp.overlay.OverlayCascadingListPopup].

```kotlin
import top.yukonga.miuix.kmp.window.WindowCascadingListPopup

@Composable
fun WindowCascadingListPopup(
    show: Boolean,  // required
    entries: List<DropdownEntry>,  // required
    onDismissRequest: () -> Unit,  // required
    popupModifier: Modifier = Modifier,
    onDismissFinished: (() -> Unit)? = null,
    popupPositionProvider: PopupPositionProvider = ListPopupDefaults.DropdownPositionProvider,
    alignment: PopupPositionProvider.Align = PopupPositionProvider.Align.End,
    enableWindowDim: Boolean = true,
    maxHeight: Dp? = null,
    minWidth: Dp = 200.dp,
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    collapseOnSelection: Boolean = true,
)
```

- `show` — Whether the popup is shown.
- `entries` — Grouped dropdown entries; top-level [DropdownItem]s with non-empty   [DropdownItem.children] become submenu triggers. Keep the entry and item order stable while the   popup is shown; item state such as [DropdownItem.selected] may change.
- `onDismissRequest` — Invoked when the popup wants to be dismissed.
- `popupModifier` — Modifier applied to the popup body.
- `onDismissFinished` — Invoked after the exit animation finishes.
- `popupPositionProvider` — Position strategy for the primary popup relative to its anchor.
- `alignment` — Alignment of the primary popup.
- `enableWindowDim` — Whether to dim the rest of the window while the popup is shown.
- `maxHeight` — Maximum height of either side. Null bounds it by the safe area.
- `minWidth` — Minimum width of the popup.
- `dropdownColors` — Colors used by every row.
- `collapseOnSelection` — When true, selecting any leaf dismisses the popup.

**Traps**

- 🟡 onDismissRequest is two-stage: when the second level is expanded, tapping outside / pressing back only collapses the second level and does not call onDismissRequest. Note that onDismissRequest here is required and non-null (unlike the nullable one on WindowListPopup / WindowDialog), so do not omit it out of habit from other components in the same family.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowCascadingListPopup.kt:46`)
- 🟡 children deeper than 2 are ignored, with only a single println warning (the file-level deeperChildrenWarned ensures it prints only once per process), not throwing an exception and not via Logger.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingMorphContent.kt:121`)
- 🔴 entries must keep a stable order while the popup is showing (internally the expanded item is tracked by entryIndex/itemIndex position); inserting/deleting/reordering makes the submenu jump items or collapse; an item's selected and other values can change.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingListPopupLayout.kt:78`)
- 🟡 A first-level trigger item's DropdownItem.onClick is swallowed (having children means expand), while a second-level leaf item's onClick is called.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingListPopupLayout.kt:326`)
- ⚪ The default alignment is Align.End (WindowListPopup is Start); at the same time the four corner values still all equal Start under the default provider.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowCascadingListPopup.kt:50`)
- ⚪ Among the four window components, it is the only one that does not provide LocalDismissState around the outside (because it has no content slot at all), and the close entry point inside the popup comes entirely from the single provide inside CascadingListPopupLayout.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingListPopupLayout.kt:285`)

**Spec** same_as Identical to OverlayCascadingListPopup: corner 16.dp, first-level dropShadow(24.dp / black 18% / offset y 6.dp), on expand the first level scale 0.95 + scrim, arrow rotates ∓90°, minWidth defaults to 200.dp

**State** Controlled show + entries; the second-level expanded state is held internally by the component, which the outside can neither read nor control. onDismissRequest is required. entries should be remembered.

**vs Material3** No equivalent.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowCascadingListPopupDemo.kt:88`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowCascadingListPopupDemo.kt#L88)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowCascadingListPopup.kt:43`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowCascadingListPopup.kt#L43)</sub>

## WindowDialog  ·  Window overlay

A dialog rendered as a platform Dialog window; usable anywhere, needs no Scaffold, and can overflow the host boundary. Its visuals and animation are identical to OverlayDialog (they share DialogContentLayout).

> A dialog with a title, a summary, and other contents, rendered at window level without `Scaffold`.
> 
> Use [LocalDismissState] inside `content` to request dismissal from inner composables.

```kotlin
import top.yukonga.miuix.kmp.window.WindowDialog

@Composable
fun WindowDialog(
    show: Boolean,  // required
    modifier: Modifier = Modifier,
    title: String? = null,
    titleColor: Color = DialogDefaults.titleColor(),
    summary: String? = null,
    summaryColor: Color = DialogDefaults.summaryColor(),
    backgroundColor: Color = DialogDefaults.backgroundColor(),
    enableWindowDim: Boolean = true,
    onDismissRequest: (() -> Unit)? = null,
    onDismissFinished: (() -> Unit)? = null,
    outsideMargin: DpSize = DialogDefaults.outsideMargin,
    insideMargin: DpSize = DialogDefaults.insideMargin,
    defaultWindowInsetsPadding: Boolean = true,
    maxWidth: Dp = DialogDefaults.MaxWidth,
    largeScreen: Boolean? = null,
    cornerRadius: Dp? = null,
    content: @Composable () -> Unit,  // required
)
```

- `show` — Whether the [WindowDialog] is shown.
- `modifier` — The modifier to be applied to the [WindowDialog].
- `title` — The title of the [WindowDialog].
- `titleColor` — The color of the title.
- `summary` — The summary of the [WindowDialog].
- `summaryColor` — The color of the summary.
- `backgroundColor` — The background color of the [WindowDialog].
- `enableWindowDim` — Whether to enable window dimming when the [WindowDialog] is shown.
- `onDismissRequest` — Will called when the user tries to dismiss the Dialog by clicking outside or pressing the back button.
- `onDismissFinished` — The callback when the [WindowDialog] is completely dismissed.
- `outsideMargin` — The margin outside the [WindowDialog].
- `insideMargin` — The margin inside the [WindowDialog].
- `defaultWindowInsetsPadding` — Whether to apply default window insets padding to the [WindowDialog].
- `maxWidth` — The maximum width of the [WindowDialog].
- `largeScreen` — Optional override for the large-screen presentation (centered scale/fade   instead of bottom slide-in). If null, detected from the window size.
- `cornerRadius` — Optional corner radius override. If null, [DialogDefaults.CornerRadius]   for the centered presentation, or derived from the screen corner radius (clamped to   32dp..48dp) when bottom-attached.
- `content` — The [Composable] content of the [WindowDialog].

**Traps**

- 🔴 onDismissRequest is nullable and defaults to null, and the platform's dismissOnBackPress is hardcoded to false (the back key is handled exclusively by the internal NavigationBackHandler). So when onDismissRequest is not passed, all three paths -- tapping outside, pressing back, platform window close -- no-op, and the dialog cannot be closed.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowDialog.kt:92`)
- 🟡 On Android this is a separate window. CompositionLocals inherit through the Dialog boundary, but system back events dispatch per window -- the component fixes this by re-resolving the dispatcher owner from this window's view tree via WindowNavigationEventScope. If you provide LocalNavigationEventDispatcherOwner yourself in content (e.g. manually wiring nav), you re-shadow this fix and the back key stops working.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowDialog.kt:96`)
- 🟡 The window uses decorFitsSystemWindows = false (Android) / usePlatformInsets = false (Skiko), so insets are no longer handled automatically; the component computes the top padding safeTopInset = max(statusBars, captionBar, displayCutout) itself. This is also extra logic WindowDialog has over OverlayDialog -- if you turn off defaultWindowInsetsPadding, the bottom/IME padding becomes entirely your own responsibility.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowDialog.kt:76`)
- ⚪ The platform default scrim and transition are explicitly cleared: on Skiko scrimColor = Transparent + animateTransition = false, on Android setWindowAnimations(0) + setDimAmount(0) + clearFlags(FLAG_DIM_BEHIND). This means when enableWindowDim = false there is truly no dimming at all (unlike M3's Dialog, which still has a platform scrim as a fallback).  (`miuix-core/src/skikoMain/kotlin/top/yukonga/miuix/kmp/utils/Utils.skiko.kt:29`)
- ⚪ There is no renderInRootScaffold parameter (the window is naturally full-screen), which conversely means you cannot confine the dialog within some Scaffold's boundary -- for that effect you can only use OverlayDialog(renderInRootScaffold = false).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowDialog.kt:71`)

**Spec** same_as Identical to OverlayDialog (sharing DialogContentLayout / DialogDefaults): MaxWidth 420.dp, large-screen corner 32.dp, outsideMargin (12,12), insideMargin (24,24), large-screen height cap 2/3 of window height · top_inset Extra top safe area = the top padding of max(statusBars, captionBar, displayCutout)

**State** Same as OverlayDialog: purely controlled show, onDismissRequest is only a request. It additionally provides LocalDismissState once around content, but the inner DialogContentLayout provides it again, and both point to the same callback with identical behavior -- LocalDismissState is not exclusive to the Window variant, the Overlay version has it too.

**vs Material3** Closest to androidx.compose.material3.AlertDialog / androidx.compose.ui.window.Dialog, both platform windows. Differences: M3's DialogProperties can configure dismissOnBackPress / dismissOnClickOutside / usePlatformDefaultWidth, while Miuix hardcodes these (the first two are false + implemented itself), and you can only express "whether it can close" via whether onDismissRequest is null; M3 has no title/summary parameters (BasicAlertDialog relies entirely on content), while Miuix provides two built-in slots title/summary.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowDialogDemo.kt:47`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowDialogDemo.kt#L47) · [`example/shared/src/commonMain/kotlin/component/DialogSection.kt:174`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/DialogSection.kt#L174)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowDialog.kt:54`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowDialog.kt#L54)</sub>

## WindowListPopup  ·  Window overlay

An anchored list popup rendered as a platform Dialog window, needing no Scaffold and able to overflow the host boundary. Its positioning/animation are identical to OverlayListPopup (they share ListPopupLayout). In most cases it is the preferred list popup.

> A popup with a list of items, rendered at window level without `Scaffold`.
> 
> Use [LocalDismissState] inside `content` to request dismissal from inner composables.

```kotlin
import top.yukonga.miuix.kmp.window.WindowListPopup

@Composable
fun WindowListPopup(
    show: Boolean,  // required
    popupModifier: Modifier = Modifier,
    popupPositionProvider: PopupPositionProvider = ListPopupDefaults.DropdownPositionProvider,
    alignment: PopupPositionProvider.Align = PopupPositionProvider.Align.Start,
    enableWindowDim: Boolean = true,
    onDismissRequest: (() -> Unit)? = null,
    onDismissFinished: (() -> Unit)? = null,
    maxHeight: Dp? = null,
    minWidth: Dp = ListPopupDefaults.MinWidth,
    content: @Composable () -> Unit,  // required
)
```

- `show` — Whether the [WindowListPopup] is shown.
- `popupModifier` — The modifier to be applied to the [WindowListPopup].
- `popupPositionProvider` — The [PopupPositionProvider] of the [WindowListPopup].
- `alignment` — The alignment of the [WindowListPopup].
- `enableWindowDim` — Whether to enable window dimming when the [WindowListPopup] is shown.
- `onDismissRequest` — The callback when the [WindowListPopup] is dismissed.
- `onDismissFinished` — The callback when the [WindowListPopup] is completely dismissed (after exit animation).
- `maxHeight` — The maximum height of the [WindowListPopup]. If null, the height will be calculated automatically.
- `minWidth` — The minimum width of the [WindowListPopup].
- `content` — The [Composable] content of the [WindowListPopup]. You should use the [ListPopupColumn] in general.

**Traps**

- 🔴 Align's four corner values all equal Start under the default provider -- same origin as OverlayListPopup (DropdownPositionProvider only checks == Align.End). For real corner positioning you must explicitly pass ListPopupDefaults.ContextMenuPositionProvider, and its semantics are relative to the window: TopStart/TopEnd put the popup below the anchor, BottomStart/BottomEnd put it above the anchor.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ListPopup.kt:250`)
- 🔴 The anchor is "the parent layout node the call site sits in" rather than an explicit anchor: internally it reverse-looks-up parentLayoutCoordinates via a zero-size Spacer. You must put WindowListPopup and the trigger button into the same parent container; when the parent coordinates cannot be obtained (IntRect.Zero) the whole popup simply does not render, with no error.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/ListPopupLayout.kt:127`)
- 🟡 onDismissRequest is nullable and defaults to null; without it, neither tapping outside nor the back key can close it; and the platform dismissOnBackPress is also hardcoded to false.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowListPopup.kt:57`)
- 🟡 popupModifier applies to the full-screen overlay rather than the popup card; the card's 16.dp corner and surfaceContainer background are hardcoded in ListPopupContent and cannot be changed.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/ListPopupLayout.kt:193`)
- ⚪ enableWindowDim = false only turns off the scrim; tapping outside still requests a close (the KDoc explicitly states outside-tap dismiss is unrelated to this switch).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/ListPopupLayout.kt:199`)
- ⚪ LocalDismissState is provided around content, so a menu item can close via LocalDismissState.current?.invoke() directly, without threading the callback through layers (the English/Chinese docs do not mention this on the Overlay page, only demonstrating it on the window page).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowListPopup.kt:77`)

**Spec** same_as Identical to OverlayListPopup: card 16.dp corner, surfaceContainer background, scale 0.15→1 + directional squircle clip reveal, MinWidth 200.dp, MinPopupHeight 50.dp, dim uses colorScheme.windowDimming

**State** Controlled show, no internal expanded state; the animation tracks and anchor detection are held internally by the component. Inside content you can read LocalDismissState. When the popup closes the subtree unloads, and ListPopupColumn's scroll position is not retained.

**vs Material3** Corresponds to androidx.compose.material3.DropdownMenu -- this is the one closest to M3 semantics among the two families (both open a platform Popup/Dialog and both can overflow the host). Differences: M3 has offset: DpOffset for fine tuning, Miuix can only swap the PopupPositionProvider; M3's anchor is the Box wrapping it, Miuix reverse-looks-up the parent layout node; M3's properties can configure whether tapping outside closes, Miuix relies on whether onDismissRequest is null.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowListPopupDemo.kt:45`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowListPopupDemo.kt#L45)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowListPopup.kt:38`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/window/WindowListPopup.kt#L38)</sub>

## Public types in this topic (2)

- `BottomSheetDefaults` **object** · `import top.yukonga.miuix.kmp.layout.BottomSheetDefaults`
- `DialogDefaults` **object** · `import top.yukonga.miuix.kmp.layout.DialogDefaults`

