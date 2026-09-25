# Preference menus & popups

The popup menus themselves (DropdownMenu / CascadingListPopup, etc.); the dropdown preference rows *DropdownPreference / *SpinnerPreference are in preference.md. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## OverlayDropdownDialog  ·  popup

The Overlay-layer dialog-style option-list primitive: a list + one confirm button at the bottom. OverlaySpinnerPreference's dialog mode calls it.

> Overlay dialog for a [DropdownEntry].
> 
> Item clicks call [top.yukonga.miuix.kmp.basic.DropdownItem.onClick], and [collapseOnSelection]
> controls whether the dialog is dismissed after a click.

```kotlin
import top.yukonga.miuix.kmp.popup.OverlayDropdownDialog

@Composable
fun OverlayDropdownDialog(
    entry: DropdownEntry,  // required
    title: String,  // required
    dialogButtonString: String,  // required
    show: Boolean,  // required
    onDismiss: () -> Unit,  // required
    onDismissFinished: () -> Unit,  // required
    dropdownColors: DropdownColors,  // required
    popupModifier: Modifier = Modifier,
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = true,
)
```

**Traps**

- 🟡 title, dialogButtonString, and dropdownColors are all required with no default; show / onDismiss / onDismissFinished must also be handled by you. It is a public API but the doc site has no corresponding page.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt:149`)
- ⚪ Rows inside the dialog **have no first/last special-casing** and always use 12.dp top/bottom padding (only popup mode has the 20/12 distinction). This is intentional, because the list is scrollable.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/DropdownEntriesContent.kt:79`)
- ⚪ The internal custom Layout strictly requires exactly 2 children (list + button); when the count is wrong it silently returns layout(0, 0), a 0×0 empty dialog, without throwing.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt:205`)
- 🟡 The LazyColumn's item key is a positionally-built string (`"$entryIdx-$itemIdx"`), not a content key. Reordering the list while the dialog is shown misaligns state.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/DropdownEntriesContent.kt:70`)

**Spec** layout It measures the bottom button first and then gives the remaining height to the LazyColumn, so the button is never pushed off-screen by a long list · margins The list is flush left/right with 24.dp top/bottom (insideMargin = DpSize(0.dp, 24.dp)); the button 24.dp left/right, 12.dp top, minimum height 50.dp · rows Rows 28.dp left/right, minimum height 56.dp, minimum width 200.dp and fillMaxWidth; uniformly 12.dp top/bottom; a single line's inner text is not width-limited (only popup mode limits it to 216.dp) · colors The accompanying DropdownDefaults.dialogDropdownColors() uses tertiaryContainer as the selected background and a transparent container, different from popup's surfaceContainer

**State** Fully controlled. The confirm button directly calls onDismiss (the Window version goes through LocalDismissState; the two are ultimately equivalent).

**vs Material3** Corresponds to material3's AlertDialog with a single-select list inside, or the dialog popped up by androidx.preference's ListPreference. Difference: there is no "cancel/confirm" two-button semantics here, only a single close button, and selecting takes effect immediately.

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt:115`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt#L115)</sub>

## OverlayDropdownDialog  ·  popup

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Overlay dialog for one or more [DropdownEntry] groups.
> 
> Groups are separated by dividers. Item clicks call [top.yukonga.miuix.kmp.basic.DropdownItem.onClick], and [collapseOnSelection]
> controls whether the dialog is dismissed after a click.

```kotlin
import top.yukonga.miuix.kmp.popup.OverlayDropdownDialog

@Composable
fun OverlayDropdownDialog(
    entries: List<DropdownEntry>,  // required
    title: String,  // required
    dialogButtonString: String,  // required
    show: Boolean,  // required
    onDismiss: () -> Unit,  // required
    onDismissFinished: () -> Unit,  // required
    dropdownColors: DropdownColors,  // required
    popupModifier: Modifier = Modifier,
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = entries.size <= 1,
)
```

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt:149`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt#L149)</sub>

## OverlayDropdownMenu  ·  menu

An action menu that uses a whole row (BasicComponent) as its trigger: only an arrow on the right, no selected value shown. Functionally it fully overlaps with OverlayDropdownPreference(showValue = false); which to pick is just a semantic preference.

> A [BasicComponent] wrapper that opens an [OverlayDropdownPopup] for a single [DropdownEntry].

```kotlin
import top.yukonga.miuix.kmp.menu.OverlayDropdownMenu

@Composable
fun OverlayDropdownMenu(
    entry: DropdownEntry,  // required
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    maxHeight: Dp? = null,
    enabled: Boolean = true,
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Traps**

- 🔴 It has only the entry / entries overloads, **no convenient items: List<String> version**, and no selectedIndex / onSelectedIndexChange / showValue. Each item's behavior must be written into DropdownItem.onClick, and you compute the selected state yourself. Calling it the way you use DropdownPreference fails to compile.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayDropdownMenu.kt:73`)
- 🔴 It must be wrapped in a Scaffold, otherwise the overlay silently fails to appear.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/MiuixPopupUtils.kt:595`)
- 🟡 When all groups are empty the whole row is automatically disabled (actualEnabled = enabled && hasEntries) and the overlay does not enter composition. Empty groups are filtered out first, so dividers never appear on either side of an empty group.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayDropdownMenu.kt:105`)
- 🟡 collapseOnSelection: the entry overload defaults to true, the entries overload defaults to `entries.size <= 1`. When used as a multi-group action menu the default is "do not collapse after selecting", convenient for consecutive operations but easily mistaken for a bug.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayDropdownMenu.kt:87`)
- 🟡 The expanded state is self-held and one-way out only: there is only onExpandedChange, no expanded input parameter, so you cannot open the menu programmatically.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayDropdownMenu.kt:91`)

**Spec** end On the right there is only DropdownArrowEndAction (a 10×16.dp up-down arrow), no value text · popup Width 200–288.dp, only the first 8 items are measured for width; rows 20.dp left/right, first/last rows 20.dp and the rest 12.dp, inner text limited to 216.dp width; right-aligned · row Minimum height 56.dp, default padding 16.dp

**State** No value state. The expanded state and press state are held by internal remember (not Saveable); the press highlight persists until the overlay's exit animation finishes. DropdownEntry.enabled can gray out a whole group but the menu still pops.

**vs Material3** Corresponds to material3's DropdownMenu attached to a ListItem. Differences: M3's expanded is fully controlled (`DropdownMenu(expanded, onDismissRequest)`), here it is uncontrollable; M3's DropdownMenuItem is an arbitrary composable slot, here it is the DropdownItem data class (fixed text/icon/summary/children structure).

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayDropdownMenuDemo.kt:119`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayDropdownMenuDemo.kt#L119)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayDropdownMenu.kt:32`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayDropdownMenu.kt#L32)</sub>

## OverlayDropdownMenu  ·  menu

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [BasicComponent] wrapper that opens an [OverlayDropdownPopup] for one or more [DropdownEntry] groups.

```kotlin
import top.yukonga.miuix.kmp.menu.OverlayDropdownMenu

@Composable
fun OverlayDropdownMenu(
    entries: List<DropdownEntry>,  // required
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    maxHeight: Dp? = null,
    enabled: Boolean = true,
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = entries.size <= 1,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayDropdownMenuDemo.kt:119`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayDropdownMenuDemo.kt#L119)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayDropdownMenu.kt:73`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayDropdownMenu.kt#L73)</sub>

## OverlayDropdownPopup  ·  popup

The Overlay overlay primitive shared by Dropdown/Spinner/Menu: it renders a set of DropdownEntry into a Scaffold overlay. Use it directly when you want to assemble your own trigger (rather than a ready-made Preference row).

> Overlay dropdown popup for a single [DropdownEntry].
> 
> Item clicks call [top.yukonga.miuix.kmp.basic.DropdownItem.onClick], and [collapseOnSelection]
> controls whether the popup is dismissed after a click.

```kotlin
import top.yukonga.miuix.kmp.popup.OverlayDropdownPopup

@Composable
fun OverlayDropdownPopup(
    entry: DropdownEntry,  // required
    show: Boolean,  // required
    onDismiss: () -> Unit,  // required
    onDismissFinished: () -> Unit,  // required
    maxHeight: Dp?,  // required
    dropdownColors: DropdownColors,  // required
    renderInRootScaffold: Boolean,  // required
    collapseOnSelection: Boolean = true,
)
```

**Traps**

- 🔴 The three parameters maxHeight, dropdownColors, and renderInRootScaffold **have no default values** and must be passed explicitly (maxHeight = null means unlimited). This is the opposite of the convention in all Preference-layer components.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt:40`)
- 🟡 It is a public API but **the whole doc site has no corresponding page**, and there is no sidebar entry either. You can only read the source.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt:35`)
- 🟡 Clicks are called back by (group index, item index), with two getOrNull bounds-guards: swapping entries for a shorter list while the overlay is shown will not crash, but the click is **silently discarded** -- with no indication.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt:82`)
- ⚪ The overlay anchor is fixed to PopupPositionProvider.Align.End (right-aligned) and does not expose an alignment parameter.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt:92`)
- ⚪ The entries overload's collapseOnSelection defaults to `entries.size <= 1`, the entry overload defaults to true -- the defaults are written again at the primitive layer rather than left entirely to the caller.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt:72`)

**Spec** align Fixed right-aligned · width ListPopupColumn clamps the width to 200.dp–288.dp, and only the first 8 items' intrinsic widths participate in measurement · rows Rows 20.dp left/right; the top of the first row / bottom of the last row of the whole overlay 20.dp, the rest 12.dp; a single line's inner text limited to 216.dp width · divider A 1.5.dp divider between groups, 20.dp left/right and 4.dp top/bottom

**State** Fully controlled: show / onDismiss / onDismissFinished are all given by the caller. The selection haptic is Confirm (the ContextClick on expand is emitted by the trigger). onDismissFinished fires only when the hide animation plays to completion, and not on mid-way cancellation -- if you use it to reset the press state, note that it is never called when the overlay is conditionally removed from composition.

**vs Material3** Corresponds to material3's DropdownMenu itself. Differences: M3's menu content is an arbitrary composable slot with adjustable PopupProperties, here it is a fixed DropdownEntry data structure + fixed right alignment + fixed width range.

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt:35`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt#L35)</sub>

## OverlayDropdownPopup  ·  popup

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Overlay dropdown popup for one or more [DropdownEntry] groups.
> 
> Groups are separated by dividers. Entries without selection state can be used as action menus.

```kotlin
import top.yukonga.miuix.kmp.popup.OverlayDropdownPopup

@Composable
fun OverlayDropdownPopup(
    entries: List<DropdownEntry>,  // required
    show: Boolean,  // required
    onDismiss: () -> Unit,  // required
    onDismissFinished: () -> Unit,  // required
    maxHeight: Dp?,  // required
    dropdownColors: DropdownColors,  // required
    renderInRootScaffold: Boolean,  // required
    collapseOnSelection: Boolean = entries.size <= 1,
)
```

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt:64`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/OverlayDropdownPopup.kt#L64)</sub>

## OverlayIconCascadingDropdownMenu  ·  menu

An IconButton-triggered two-level cascading menu: items whose DropdownItem.children is non-null become submenu triggers. Used for two-level actions like "more → sort by → by name/by time".

> An [IconButton] wrapper that opens an [OverlayCascadingListPopup] for a single [DropdownEntry].
> 
> Items whose [top.yukonga.miuix.kmp.basic.DropdownItem.children] is non-empty become submenu
> triggers; cascading depth is limited to 2. Keep the entry and item order stable while the menu is
> shown; item state such as [top.yukonga.miuix.kmp.basic.DropdownItem.selected] may change.

```kotlin
import top.yukonga.miuix.kmp.menu.OverlayIconCascadingDropdownMenu

@Composable
fun OverlayIconCascadingDropdownMenu(
    entry: DropdownEntry,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    maxHeight: Dp? = null,
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    backgroundColor: Color = Color.Unspecified,
    cornerRadius: Dp = IconButtonDefaults.CornerRadius,
    minHeight: Dp = IconButtonDefaults.MinHeight,
    minWidth: Dp = IconButtonDefaults.MinWidth,
    content: @Composable () -> Unit,  // required
)
```

**Traps**

- 🟡 The depth is hard-limited to 2. Deeper children are ignored, and **not entirely silently** -- it will println one line `[CascadingListPopup] Cascading depth is limited to 2; deeper children are ignored.`, with a file-level boolean guaranteeing it prints only once per process. The "silently ignored" the doc consistently states is inaccurate.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingMorphContent.kt:117`)
- 🟡 If a first-level item has children, its own onClick is ignored (clicking = expanding the submenu); but second-level items are always treated as leaves and their onClick is called. So the rule "non-null children means onClick is ignored" only holds at the first level.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingListPopupLayout.kt:325`)
- 🔴 During the time the menu is expanded, the **order** of entry / item must stay stable: the cascade layer tracks the expanded item by positional index, not by object reference. Reordering the list while expanded misaligns the submenu. State such as an item's selected can change, but the order cannot.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconCascadingDropdownMenu.kt:28`)
- ⚪ Both collapseOnSelection overloads default to true, unlike other entries overloads which default to `entries.size <= 1`. A multi-group cascading menu collapses after selecting.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconCascadingDropdownMenu.kt:80`)
- 🟡 Constructing entries / children inline inside the composable body creates new instances on every recomposition. DropdownItem.children's KDoc explicitly requires stabilization (using remember), otherwise the cascade layer recomposes unnecessarily.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:336`)
- 🔴 It must be wrapped in a Scaffold, otherwise the overlay silently fails to appear. It bypasses this module's popup primitive and directly calls miuix-ui's OverlayCascadingListPopup.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconCascadingDropdownMenu.kt:128`)

**Spec** submenu_marker A row with a submenu draws a chevron at its end (a 10×16.dp ArrowRight) instead of a checkmark, deliberately in a softer summary color; at the same time the accessibility role switches from Role.RadioButton to Role.Button · second_level Second-level rows are always hasSubmenu = false; the first/last markers are controlled by the parent layer (the header occupies first, only the last child occupies last) · button IconButton defaults to minimum 40×40.dp, corner radius 40.dp

**State** No value state. The expanded state, press state, and the currently-expanded first-level item are all held internally; the expanded first-level item is recorded by **position**, which is why the order must be stable.

**vs Material3** No counterpart. material3 has no built-in cascading/submenu DropdownMenu (you must nest Popups yourself), and androidx.preference's PreferenceScreen nesting is page-level navigation, not menu-level cascading.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayIconCascadingDropdownMenuDemo.kt:97`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayIconCascadingDropdownMenuDemo.kt#L97) · [`example/shared/src/commonMain/kotlin/MainPage.kt:268`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MainPage.kt#L268)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconCascadingDropdownMenu.kt:32`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconCascadingDropdownMenu.kt#L32)</sub>

## OverlayIconCascadingDropdownMenu  ·  menu

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> An [IconButton] wrapper that opens an [OverlayCascadingListPopup] for one or more
> [DropdownEntry] groups. Items whose [top.yukonga.miuix.kmp.basic.DropdownItem.children] is
> non-empty become submenu triggers; cascading depth is limited to 2. Keep the entry and item order
> stable while the menu is shown; item state such as
> [top.yukonga.miuix.kmp.basic.DropdownItem.selected] may change.

```kotlin
import top.yukonga.miuix.kmp.menu.OverlayIconCascadingDropdownMenu

@Composable
fun OverlayIconCascadingDropdownMenu(
    entries: List<DropdownEntry>,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    maxHeight: Dp? = null,
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    backgroundColor: Color = Color.Unspecified,
    cornerRadius: Dp = IconButtonDefaults.CornerRadius,
    minHeight: Dp = IconButtonDefaults.MinHeight,
    minWidth: Dp = IconButtonDefaults.MinWidth,
    content: @Composable () -> Unit,  // required
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayIconCascadingDropdownMenuDemo.kt:97`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayIconCascadingDropdownMenuDemo.kt#L97) · [`example/shared/src/commonMain/kotlin/MainPage.kt:268`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MainPage.kt#L268)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconCascadingDropdownMenu.kt:73`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconCascadingDropdownMenu.kt#L73)</sub>

## OverlayIconDropdownMenu  ·  menu

An action menu that uses an IconButton as its trigger (typical use: a top-bar "more" button). It does not go through BasicComponent and has no title/summary row.

> An [IconButton] wrapper that opens an [OverlayDropdownPopup] for a single [DropdownEntry].

```kotlin
import top.yukonga.miuix.kmp.menu.OverlayIconDropdownMenu

@Composable
fun OverlayIconDropdownMenu(
    entry: DropdownEntry,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    maxHeight: Dp? = null,
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    backgroundColor: Color = Color.Unspecified,
    cornerRadius: Dp = IconButtonDefaults.CornerRadius,
    minHeight: Dp = IconButtonDefaults.MinHeight,
    minWidth: Dp = IconButtonDefaults.MinWidth,
    content: @Composable () -> Unit,  // required
)
```

**Traps**

- 🟡 It has no Preference slots such as title / summary / startAction / endActions -- it renders `Box { IconButton; Popup }`. What the trigger looks like is entirely decided by the final required content trailing lambda.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconDropdownMenu.kt:108`)
- 🔴 It has only the entry / entries overloads, no convenient items version; each item's behavior is written on DropdownItem.onClick.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconDropdownMenu.kt:65`)
- 🟡 When entries is all empty the IconButton goes straight into a disabled state (enabled = actualEnabled); the button grays out rather than "tapping produces no menu".  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconDropdownMenu.kt:95`)
- 🔴 It must be wrapped in a Scaffold, otherwise the overlay silently fails to appear (the doc page has a danger callout stating this). Note also that it belongs to the optional artifact miuix-preference, while the OverlayListPopup that it transitively calls via OverlayDropdownPopup is in miuix-ui -- a project depending only on miuix-ui cannot use this component, and neither the doc frontmatter nor the body states the artifact ownership.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/MiuixPopupUtils.kt:595`)
- 🟡 The doc example's Import section lists only the component itself, yet the example uses extension icons like MiuixIcons.Edit / Sort / SelectAll -- these are in the separate artifact miuix-icons, and miuix-ui does not carry a transitive dependency, so copying it gives an unresolved reference.  (`docs/components/overlayicondropdownmenu.md:27`)

**Spec** button IconButton defaults to minimum 40×40.dp, corner radius 40.dp; the four parameters (backgroundColor / cornerRadius / minHeight / minWidth) are forwarded as-is to IconButtonDefaults · popup Width 200–288.dp, only the first 8 items measured for width; rows 20.dp left/right, first/last 20.dp and the rest 12.dp, inner text limited to 216.dp width; right-aligned

**State** No value state. The expanded state and press state use internal remember; the press highlight is passed in via the IconButton's holdDownState and is not reset until the overlay's exit animation finishes.

**vs Material3** Corresponds to material3's IconButton + DropdownMenu combination. Differences: M3 requires you to hold `var expanded by remember` yourself, here the component self-holds it and it cannot be driven externally; M3's menu items are arbitrary composables, here they are the DropdownItem data structure.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayIconDropdownMenuDemo.kt:90`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayIconDropdownMenuDemo.kt#L90) · [`example/shared/src/commonMain/kotlin/MainPage.kt:279`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MainPage.kt#L279)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconDropdownMenu.kt:28`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconDropdownMenu.kt#L28)</sub>

## OverlayIconDropdownMenu  ·  menu

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> An [IconButton] wrapper that opens an [OverlayDropdownPopup] for one or more [DropdownEntry] groups.

```kotlin
import top.yukonga.miuix.kmp.menu.OverlayIconDropdownMenu

@Composable
fun OverlayIconDropdownMenu(
    entries: List<DropdownEntry>,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    maxHeight: Dp? = null,
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = entries.size <= 1,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    backgroundColor: Color = Color.Unspecified,
    cornerRadius: Dp = IconButtonDefaults.CornerRadius,
    minHeight: Dp = IconButtonDefaults.MinHeight,
    minWidth: Dp = IconButtonDefaults.MinWidth,
    content: @Composable () -> Unit,  // required
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayIconDropdownMenuDemo.kt:90`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayIconDropdownMenuDemo.kt#L90) · [`example/shared/src/commonMain/kotlin/MainPage.kt:279`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MainPage.kt#L279)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconDropdownMenu.kt:65`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/OverlayIconDropdownMenu.kt#L65)</sub>

## WindowDropdownDialog  ·  popup

The Window-layer dialog-style option-list primitive: a list + a confirm button at the bottom. WindowSpinnerPreference's dialog mode calls it.

> Window-layer dialog for a [DropdownEntry].
> 
> Item clicks call [top.yukonga.miuix.kmp.basic.DropdownItem.onClick], and [collapseOnSelection]
> controls whether the dialog is dismissed after a click.

```kotlin
import top.yukonga.miuix.kmp.popup.WindowDropdownDialog

@Composable
fun WindowDropdownDialog(
    entry: DropdownEntry,  // required
    title: String,  // required
    dialogButtonString: String,  // required
    show: Boolean,  // required
    onDismiss: () -> Unit,  // required
    onDismissFinished: () -> Unit,  // required
    dropdownColors: DropdownColors,  // required
    popupModifier: Modifier = Modifier,
    collapseOnSelection: Boolean = true,
)
```

**Traps**

- 🟡 title, dialogButtonString, and dropdownColors are required with no defaults; there is no renderInRootScaffold. A public API but the doc site has no corresponding page.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt:145`)
- 🟡 The bottom confirm button's onClick goes through `dismiss?.invoke()` (LocalDismissState), while the Overlay version is a direct onDismiss. The two are equivalent, but LocalDismissState defaults to null, so in theory if it cannot be obtained the button does nothing when tapped.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt:196`)
- ⚪ Rows inside the dialog always use 12.dp top/bottom padding, with no first/last special-casing (only popup mode has the 20/12 distinction).  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/DropdownEntriesContent.kt:79`)
- 🟡 The LazyColumn's item key is a positionally-built string, not a content key; reordering the list while shown misaligns state. The internal Layout requires exactly 2 children, otherwise it silently returns 0×0.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/DropdownEntriesContent.kt:70`)

**Spec** layout It measures the bottom button first and then gives the remaining height to the LazyColumn, so the button is never pushed off-screen by a long list · margins The list is flush left/right with 24.dp top/bottom; the button 24.dp left/right, 12.dp top, minimum height 50.dp · rows Rows 28.dp left/right, minimum height 56.dp, minimum width 200.dp and fillMaxWidth; uniformly 12.dp top/bottom; inner text not width-limited · colors The accompanying dialogDropdownColors(): selected background tertiaryContainer, transparent container

**State** Fully controlled. show / onDismiss / onDismissFinished are given by the caller; the close action is routed internally through LocalDismissState.

**vs Material3** Corresponds to material3's AlertDialog with a nested single-select list, or androidx.preference's ListPreference dialog. Difference: there is only one close button, selecting takes effect immediately, and there is no confirm/cancel two-button semantics.

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt:113`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt#L113)</sub>

## WindowDropdownDialog  ·  popup

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Window-layer dialog for one or more [DropdownEntry] groups.
> 
> Groups are separated by dividers. Item clicks call [top.yukonga.miuix.kmp.basic.DropdownItem.onClick], and [collapseOnSelection]
> controls whether the dialog is dismissed after a click.

```kotlin
import top.yukonga.miuix.kmp.popup.WindowDropdownDialog

@Composable
fun WindowDropdownDialog(
    entries: List<DropdownEntry>,  // required
    title: String,  // required
    dialogButtonString: String,  // required
    show: Boolean,  // required
    onDismiss: () -> Unit,  // required
    onDismissFinished: () -> Unit,  // required
    dropdownColors: DropdownColors,  // required
    popupModifier: Modifier = Modifier,
    collapseOnSelection: Boolean = entries.size <= 1,
)
```

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt:145`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt#L145)</sub>

## WindowDropdownMenu  ·  menu

An action menu that uses a whole row as its trigger, with the overlay on a platform window; it does not depend on a Scaffold, and the menu can extend beyond the host bounds.

> A [BasicComponent] wrapper that opens a [WindowDropdownPopup] for a single [DropdownEntry].

```kotlin
import top.yukonga.miuix.kmp.menu.WindowDropdownMenu

@Composable
fun WindowDropdownMenu(
    entry: DropdownEntry,  // required
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    maxHeight: Dp? = null,
    enabled: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Traps**

- 🔴 It has only the entry / entries overloads, no convenient items version, and no selectedIndex / onSelectedIndexChange / showValue.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowDropdownMenu.kt:71`)
- 🔴 It has no renderInRootScaffold parameter (the Overlay version does), so copying a call from the Overlay version fails to compile.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowDropdownMenu.kt:71`)
- 🟡 When all groups are empty the whole row is automatically disabled and the overlay does not enter composition.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowDropdownMenu.kt:104`)
- 🟡 collapseOnSelection: the entry overload defaults to true, the entries overload defaults to `entries.size <= 1` (with multiple groups it does not collapse after selecting).  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowDropdownMenu.kt:84`)
- ⚪ The collapse path goes through LocalDismissState rather than calling onDismiss directly; that CompositionLocal defaults to null, so in theory if it cannot be obtained it silently fails to collapse.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/theme/DismissState.kt:26`)

**Spec** end On the right there is only a 10×16.dp up-down arrow, no value text · popup Width 200–288.dp, only the first 8 items measured for width; rows 20.dp left/right, first/last 20.dp and the rest 12.dp, inner text limited to 216.dp width; right-aligned · row Minimum height 56.dp, default padding 16.dp

**State** No value state. The expanded state and press state use internal remember (not Saveable); the press highlight persists until the overlay's exit animation finishes.

**vs Material3** Corresponds to material3's DropdownMenu attached to a ListItem. The Window version's platform Popup behavior is closest to M3's default implementation, but expanded cannot be controlled externally.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowDropdownMenuDemo.kt:119`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowDropdownMenuDemo.kt#L119)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowDropdownMenu.kt:32`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowDropdownMenu.kt#L32)</sub>

## WindowDropdownMenu  ·  menu

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [BasicComponent] wrapper that opens a [WindowDropdownPopup] for one or more [DropdownEntry] groups.

```kotlin
import top.yukonga.miuix.kmp.menu.WindowDropdownMenu

@Composable
fun WindowDropdownMenu(
    entries: List<DropdownEntry>,  // required
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    maxHeight: Dp? = null,
    enabled: Boolean = true,
    collapseOnSelection: Boolean = entries.size <= 1,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowDropdownMenuDemo.kt:119`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowDropdownMenuDemo.kt#L119)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowDropdownMenu.kt:71`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowDropdownMenu.kt#L71)</sub>

## WindowDropdownPopup  ·  popup

The Window-layer dropdown overlay primitive, shared by the Window variants of Dropdown/Spinner/Menu. Use it directly when you want to assemble your own trigger.

> Window-layer dropdown popup for a single [DropdownEntry].
> 
> Item clicks call [top.yukonga.miuix.kmp.basic.DropdownItem.onClick], and [collapseOnSelection]
> controls whether the popup is dismissed after a click.

```kotlin
import top.yukonga.miuix.kmp.popup.WindowDropdownPopup

@Composable
fun WindowDropdownPopup(
    entry: DropdownEntry,  // required
    show: Boolean,  // required
    onDismiss: () -> Unit,  // required
    onDismissFinished: () -> Unit,  // required
    maxHeight: Dp?,  // required
    dropdownColors: DropdownColors,  // required
    collapseOnSelection: Boolean = true,
)
```

**Traps**

- 🔴 maxHeight and dropdownColors have no default values and must be passed explicitly (maxHeight = null means unlimited); there is no renderInRootScaffold (the Overlay version has it).  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt:41`)
- 🟡 A public API, but the doc site has no corresponding page and there is no sidebar entry either; you can only read the source.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt:36`)
- 🟡 The collapse after selection does not call onDismiss directly but reads LocalDismissState from inside the overlay and calls it; that CompositionLocal defaults to null, and when it cannot be obtained it silently fails to collapse. Ultimately equivalent to the Overlay version's direct onDismiss, but the debugging path differs.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt:92`)
- 🟡 Clicks are called back by (group index, item index), with two getOrNull bounds-guards: swapping for a shorter list while shown will not crash, but the click is silently discarded.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt:88`)
- ⚪ The overlay anchor is fixed to right-aligned (PopupPositionProvider.Align.End) and does not expose an alignment parameter.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt:78`)

**Spec** align Fixed right-aligned · width ListPopupColumn clamps the width to 200.dp–288.dp, and only the first 8 items' intrinsic widths participate in measurement · rows Rows 20.dp left/right; the overlay's first-row top / last-row bottom 20.dp, the rest 12.dp; a single line's inner text limited to 216.dp width · divider A 1.5.dp divider between groups, 20.dp left/right and 4.dp top/bottom

**State** Fully controlled: show / onDismiss / onDismissFinished are given by the caller. Selection haptic Confirm. onDismissFinished fires only when the hide animation plays to completion, and is never called when the overlay is conditionally removed from composition.

**vs Material3** Corresponds to material3's DropdownMenu itself (a platform Popup). Difference: the content is a fixed DropdownEntry data structure, and alignment and width range are hard-coded.

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt:36`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt#L36)</sub>

## WindowDropdownPopup  ·  popup

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Window-layer dropdown popup for one or more [DropdownEntry] groups.
> 
> Groups are separated by dividers. Entries without selection state can be used as action menus.

```kotlin
import top.yukonga.miuix.kmp.popup.WindowDropdownPopup

@Composable
fun WindowDropdownPopup(
    entries: List<DropdownEntry>,  // required
    show: Boolean,  // required
    onDismiss: () -> Unit,  // required
    onDismissFinished: () -> Unit,  // required
    maxHeight: Dp?,  // required
    dropdownColors: DropdownColors,  // required
    collapseOnSelection: Boolean = entries.size <= 1,
)
```

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt:63`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/popup/WindowDropdownPopup.kt#L63)</sub>

## WindowIconCascadingDropdownMenu  ·  menu

An IconButton-triggered two-level cascading menu on a platform window; it does not depend on a Scaffold.

> An [IconButton] wrapper that opens a [WindowCascadingListPopup] for a single [DropdownEntry].
> 
> Items whose [top.yukonga.miuix.kmp.basic.DropdownItem.children] is non-empty become submenu
> triggers; cascading depth is limited to 2. Keep the entry and item order stable while the menu is
> shown; item state such as [top.yukonga.miuix.kmp.basic.DropdownItem.selected] may change.

```kotlin
import top.yukonga.miuix.kmp.menu.WindowIconCascadingDropdownMenu

@Composable
fun WindowIconCascadingDropdownMenu(
    entry: DropdownEntry,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    maxHeight: Dp? = null,
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    backgroundColor: Color = Color.Unspecified,
    cornerRadius: Dp = IconButtonDefaults.CornerRadius,
    minHeight: Dp = IconButtonDefaults.MinHeight,
    minWidth: Dp = IconButtonDefaults.MinWidth,
    content: @Composable () -> Unit,  // required
)
```

**Traps**

- 🟡 The depth is hard-limited to 2; deeper children are ignored and a warning is println'd once (not entirely silently).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingMorphContent.kt:117`)
- 🔴 During the time the menu is expanded, the order of entry / item must stay stable: the cascade layer tracks the expanded item by positional index rather than object reference, so reordering while expanded misaligns the submenu.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconCascadingDropdownMenu.kt:27`)
- ⚪ Both collapseOnSelection overloads default to true, unlike other entries overloads which default to `entries.size <= 1`.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconCascadingDropdownMenu.kt:77`)
- 🟡 A first-level item with children has its onClick ignored (clicking expands it), while second-level items are treated as leaves and call onClick -- the rule "non-null children means onClick is ignored" only holds at the first level.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/layout/CascadingListPopupLayout.kt:325`)
- 🟡 There is no renderInRootScaffold; constructing entries/children inline creates new instances on every recomposition, and the KDoc requires stabilizing with remember.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:336`)

**Spec** submenu_marker A row with a submenu draws a 10×16.dp chevron at its end instead of a checkmark, in a softer summary color; the accessibility role switches from RadioButton to Button · button IconButton defaults to minimum 40×40.dp, corner radius 40.dp

**State** No value state. The expanded state, press state, and the currently-expanded first-level item are all held internally; the expanded first-level item is recorded by position.

**vs Material3** No counterpart. material3 has no built-in cascading-submenu DropdownMenu.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowIconCascadingDropdownMenuDemo.kt:97`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowIconCascadingDropdownMenuDemo.kt#L97)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconCascadingDropdownMenu.kt:32`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconCascadingDropdownMenu.kt#L32)</sub>

## WindowIconCascadingDropdownMenu  ·  menu

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> An [IconButton] wrapper that opens a [WindowCascadingListPopup] for one or more
> [DropdownEntry] groups. Items whose [top.yukonga.miuix.kmp.basic.DropdownItem.children] is
> non-empty become submenu triggers; cascading depth is limited to 2. Keep the entry and item order
> stable while the menu is shown; item state such as
> [top.yukonga.miuix.kmp.basic.DropdownItem.selected] may change.

```kotlin
import top.yukonga.miuix.kmp.menu.WindowIconCascadingDropdownMenu

@Composable
fun WindowIconCascadingDropdownMenu(
    entries: List<DropdownEntry>,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    maxHeight: Dp? = null,
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    backgroundColor: Color = Color.Unspecified,
    cornerRadius: Dp = IconButtonDefaults.CornerRadius,
    minHeight: Dp = IconButtonDefaults.MinHeight,
    minWidth: Dp = IconButtonDefaults.MinWidth,
    content: @Composable () -> Unit,  // required
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowIconCascadingDropdownMenuDemo.kt:97`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowIconCascadingDropdownMenuDemo.kt#L97)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconCascadingDropdownMenu.kt:71`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconCascadingDropdownMenu.kt#L71)</sub>

## WindowIconDropdownMenu  ·  menu

An IconButton-triggered action menu on a platform window; it does not depend on a Scaffold.

> An [IconButton] wrapper that opens a [WindowDropdownPopup] for a single [DropdownEntry].

```kotlin
import top.yukonga.miuix.kmp.menu.WindowIconDropdownMenu

@Composable
fun WindowIconDropdownMenu(
    entry: DropdownEntry,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    maxHeight: Dp? = null,
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    backgroundColor: Color = Color.Unspecified,
    cornerRadius: Dp = IconButtonDefaults.CornerRadius,
    minHeight: Dp = IconButtonDefaults.MinHeight,
    minWidth: Dp = IconButtonDefaults.MinWidth,
    content: @Composable () -> Unit,  // required
)
```

**Traps**

- 🟡 It has no Preference slots such as title/summary and renders `Box { IconButton; Popup }`; the trigger's appearance is decided by the final required content trailing lambda.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconDropdownMenu.kt:75`)
- 🔴 It has only the entry / entries overloads, no convenient items version; and no renderInRootScaffold.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconDropdownMenu.kt:63`)
- 🟡 When entries is all empty the IconButton is directly disabled and grays out, rather than "tapping produces no menu".  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconDropdownMenu.kt:92`)
- 🟡 It lives in the optional artifact miuix-preference (the WindowDropdownPopup it transitively calls is also in that artifact), so a project depending only on miuix-ui cannot use this component; the doc frontmatter only writes requiresScaffoldHost / hostComponent / popupHost, with no statement of artifact ownership.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconDropdownMenu.kt:28`)
- 🟡 The doc example's Import section is missing the extension icons (MiuixIcons.Edit etc. are in the separate artifact miuix-icons), so copying it gives an unresolved reference.  (`docs/components/windowicondropdownmenu.md:22`)

**Spec** button IconButton defaults to minimum 40×40.dp, corner radius 40.dp; the four IconButtonDefaults parameters are forwarded as-is · popup Width 200–288.dp, only the first 8 items measured for width; rows 20.dp left/right, first/last 20.dp and the rest 12.dp, inner text limited to 216.dp width; right-aligned

**State** No value state. The expanded state and press state use internal remember; the press highlight is carried by the IconButton's holdDownState and is not reset until the overlay's exit animation finishes.

**vs Material3** Corresponds to material3's IconButton + DropdownMenu. Same difference as OverlayIconDropdownMenu: expanded cannot be driven externally, and menu items are a fixed data structure rather than arbitrary composables.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowIconDropdownMenuDemo.kt:90`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowIconDropdownMenuDemo.kt#L90)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconDropdownMenu.kt:28`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconDropdownMenu.kt#L28)</sub>

## WindowIconDropdownMenu  ·  menu

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> An [IconButton] wrapper that opens a [WindowDropdownPopup] for one or more [DropdownEntry] groups.

```kotlin
import top.yukonga.miuix.kmp.menu.WindowIconDropdownMenu

@Composable
fun WindowIconDropdownMenu(
    entries: List<DropdownEntry>,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    maxHeight: Dp? = null,
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    collapseOnSelection: Boolean = entries.size <= 1,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    backgroundColor: Color = Color.Unspecified,
    cornerRadius: Dp = IconButtonDefaults.CornerRadius,
    minHeight: Dp = IconButtonDefaults.MinHeight,
    minWidth: Dp = IconButtonDefaults.MinWidth,
    content: @Composable () -> Unit,  // required
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowIconDropdownMenuDemo.kt:90`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowIconDropdownMenuDemo.kt#L90)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconDropdownMenu.kt:63`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/menu/WindowIconDropdownMenu.kt#L63)</sub>

