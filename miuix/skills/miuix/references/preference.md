# Preferences

The various *Preference rows of miuix-preference. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## ArrowPreference  ·  preference

A navigation-style settings row with a fixed arrow on the right, used to drill into a sub-page or open a self-managed dialog; it only handles appearance and clicks, and holds no value.

> An arrow with a title and a summary.

```kotlin
import top.yukonga.miuix.kmp.preference.ArrowPreference

@Composable
fun ArrowPreference(
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    startAction: @Composable (() -> Unit)? = null,
    endActions: @Composable RowScope.() -> Unit = {},
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    onClick: (() -> Unit)? = null,
    holdDownState: Boolean = false,
    enabled: Boolean = true,
)
```

- `title` — The title of the [ArrowPreference].
- `modifier` — The modifier to be applied to the [ArrowPreference].
- `titleColor` — The color of the title.
- `summary` — The summary of the [ArrowPreference].
- `summaryColor` — The color of the summary.
- `startAction` — The [Composable] content on the start side of the [ArrowPreference].
- `endActions` — The [Composable] content on the end side of the [ArrowPreference].
- `bottomAction` — The [Composable] content at the bottom of the [ArrowPreference].
- `insideMargin` — The margin inside the [ArrowPreference].
- `holdDownState` — Used to determine whether it is in the pressed state.
- `enabled` — Whether the [ArrowPreference] is clickable.

**ArrowPreferenceDefaults**

- `endActionColors()`

**Traps**

- 🟡 The arrow color is in fact not customizable. `ArrowPreferenceDefaults.endActionColors()` is public and looks like a configuration entry point, but ArrowPreference's parameter list has no argument that accepts EndActionColors; the factory is only called internally by the private ArrowPreferenceEndAction. Both fields of EndActionColors are private val and their accessor functions are internal, so even with an instance you cannot read them. To change the arrow color you must draw your own inside endActions.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/ArrowPreference.kt:95`)
- ⚪ The default value of endActions is `{}` rather than null, so the wrapping Row with padding(end = 8.dp) always exists. Even if you pass no endActions at all, there is always an 8dp gap between the title and the arrow -- unlike CheckboxPreference/SliderPreference (default null, no Row when not passed).  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/ArrowPreference.kt:71`)
- ⚪ It does not pass a role to BasicComponent. The Switch/Checkbox/RadioButton/Dropdown in the same group all pass an explicit semantic role; only ArrowPreference and the two Sliders do not, so screen readers will not announce this row as a button. The Preference layer also does not expose onClickLabel.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/ArrowPreference.kt:63`)
- 🟡 Omitting onClick makes the whole row non-clickable: BasicComponent only attaches Modifier.clickable when `enabled && onClick != null`. The arrow is still drawn, but it neither consumes gestures nor gives any press feedback -- it looks tappable but does nothing.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Component.kt:146`)

**Spec** arrow A 10×16.dp Image (MiuixIcons.Basic.ArrowRight), fixed size and not adjustable; RTL uses graphicsLayer scaleX = -1f to mirror it, not a different icon · row Minimum height 56.dp, default padding 16.dp on all four sides (BasicComponentDefaults.InsideMargin) · text Title uses headline1 size + FontWeight.Medium, summary uses body2; neither passes maxLines/overflow, so long text always wraps, never ellipsizes, and the line height grows · gap A fixed 8.dp between endActions and the arrow

**State** Pure forwarding, zero state of its own. onClick is the only interaction entry. holdDownState is an "externally injected press state": when the caller opens its own Dialog it sets it true, keeping this row highlighted as pressed until it is manually set back to false in the Dialog's onDismissFinished -- it needs a remember/rememberSaveable MutableState held by the caller.

**vs Material3** No one-to-one counterpart. The closest is material3's ListItem with a chevron in trailingContent, or androidx.preference's Preference(fragment=...). Differences: M3 ListItem has no external press-state injection like holdDownState, and no fixed startAction/endActions/bottomAction three-slot layout; conversely ArrowPreference has none of M3's overlineContent/supportingContent multi-line structure.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/ArrowPreferenceDemo.kt:41`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ArrowPreferenceDemo.kt#L41) · [`docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt:70`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingActionButtonDemo.kt#L70) · [`docs/demo/src/commonMain/kotlin/FloatingToolbarDemo.kt:83`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingToolbarDemo.kt#L83) · [`docs/demo/src/commonMain/kotlin/TopAppBarDemo.kt:99`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TopAppBarDemo.kt#L99)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/ArrowPreference.kt:49`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/ArrowPreference.kt#L49)</sub>

## CheckboxPreference  ·  preference

A settings row with a checkbox that can sit at the row's start or end; used for multi-select lists or boolean items. Purely controlled.

> A checkbox with a title and a summary.

```kotlin
import top.yukonga.miuix.kmp.preference.CheckboxPreference

@Composable
fun CheckboxPreference(
    title: String,  // required
    checked: Boolean,  // required
    onCheckedChange: ((Boolean) -> Unit)?,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    checkboxColors: CheckboxColors = CheckboxDefaults.checkboxColors(),
    startAction: @Composable (() -> Unit)? = null,
    endActions: @Composable (RowScope.() -> Unit)? = null,
    checkboxLocation: CheckboxLocation = CheckboxLocation.Start,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    holdDownState: Boolean = false,
    enabled: Boolean = true,
)
```

- `title` — The title of the [CheckboxPreference].
- `checked` — The checked state of the [CheckboxPreference].
- `onCheckedChange` — The callback when the checked state of the [CheckboxPreference] is changed.
- `modifier` — The modifier to be applied to the [CheckboxPreference].
- `titleColor` — The color of the title.
- `summary` — The summary of the [CheckboxPreference].
- `summaryColor` — The color of the summary.
- `checkboxColors` — The [CheckboxColors] of the [CheckboxPreference].
- `startAction` — The [Composable] content on the start side of the [CheckboxPreference].
- `endActions` — The [Composable] content on the end side of the [CheckboxPreference].
- `checkboxLocation` — The location of checkbox, [CheckboxLocation.Start] or [CheckboxLocation.End].
- `bottomAction` — The [Composable] content at the bottom of the [CheckboxPreference].
- `insideMargin` — The margin inside the [CheckboxPreference].
- `holdDownState` — Used to determine whether it is in the pressed state.
- `enabled` — Whether the [CheckboxPreference] is clickable.

**Traps**

- 🔴 onCheckedChange is nullable but **has no default value**, so it must be passed explicitly (you can pass null). The doc checkboxpreference.md writes No in the Required column; omitting the parameter as it suggests fails to compile directly. Nullable ≠ omittable.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/CheckboxPreference.kt:52`)
- 🔴 The parameter order is (title, checked, onCheckedChange), the reverse of SwitchPreference's (checked, onCheckedChange, title). Positional arguments cannot be swapped between the two.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/CheckboxPreference.kt:50`)
- 🟡 Passing onCheckedChange = null does not turn the row into a static display. The onClick handed to BasicComponent is always a non-null lambda, so the row still attaches clickable and still shows press highlight; it just does nothing when tapped (the checkbox body does correctly become non-clickable). To be truly non-interactive you must pass enabled = false.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/CheckboxPreference.kt:123`)
- 🟡 Tri-state checkbox (Indeterminate) is unreachable at this layer. Internally it always constructs `ToggleableState(checked)` from a Boolean; the underlying Checkbox supports Indeterminate but Preference has no entry point. For tri-state you must assemble your own BasicComponent with miuix-ui's Checkbox.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/CheckboxPreference.kt:151`)
- ⚪ Haptics fire only when the checkbox body itself is tapped (Checkbox's internal triStateToggleable provides them); tapping other areas of the row has no haptics.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Checkbox.kt:146`)

**Spec** spacing The checkbox has its own padding(end = 5.dp); the user's startAction adds another 5.dp via StartActionSlot; BasicComponent adds a further 8.dp between the start slot and the body. So "checkbox → icon" is 5.dp and "icon → title" is 5+8=13.dp · empty_slot When checkboxLocation = End and no startAction is passed, the start slot is passed null as a whole, BasicComponent takes the no-start branch, and that 8.dp is not produced either (it is not a blank placeholder) · row Minimum height 56.dp, default padding 16.dp

**State** Purely controlled. checked is held by the caller; internally the component only uses rememberUpdatedState to stabilize the callback, with no self-held state. CheckboxLocation is an ordinary enum parameter, not state.

**vs Material3** Corresponds to material3 ListItem + Checkbox, or androidx.preference's CheckBoxPreference. Differences: M3's TriStateCheckbox tri-state capability is cut at this layer; androidx's automatic persistence and dependency linkage do not exist here; conversely this adds checkboxLocation (start/end), something M3 ListItem needs a manual slot swap to achieve.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/CheckboxPreferenceDemo.kt:45`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/CheckboxPreferenceDemo.kt#L45) · [`example/shared/src/commonMain/kotlin/component/CheckboxSection.kt:38`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/CheckboxSection.kt#L38)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/CheckboxPreference.kt:49`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/CheckboxPreference.kt#L49)</sub>

## OverlayDropdownPreference  ·  preference

A settings row that shows the current selected value on the right and, when clicked, pops up a dropdown menu in a Scaffold overlay. Suited for cases with few options that need to follow the Scaffold's blur/scale effects.

> A dropdown with a title and a summary.

```kotlin
import top.yukonga.miuix.kmp.preference.OverlayDropdownPreference

@Composable
fun OverlayDropdownPreference(
    items: List<String>,  // required
    selectedIndex: Int,  // required
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
    showValue: Boolean = true,
    renderInRootScaffold: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    onSelectedIndexChange: ((Int) -> Unit)? = null,
)
```

- `items` — The options of the [OverlayDropdownPreference].
- `selectedIndex` — The index of the selected option.
- `title` — The title of the [OverlayDropdownPreference].
- `modifier` — The modifier to be applied to the [OverlayDropdownPreference].
- `titleColor` — The color of the title.
- `summary` — The summary of the [OverlayDropdownPreference].
- `summaryColor` — The color of the summary.
- `dropdownColors` — The [DropdownColors] of the [OverlayDropdownPreference].
- `startAction` — The [Composable] content on the start side of the [OverlayDropdownPreference].
- `bottomAction` — The [Composable] content at the bottom of the [OverlayDropdownPreference].
- `insideMargin` — The margin inside the [OverlayDropdownPreference].
- `maxHeight` — The maximum height of the [OverlayListPopup].
- `enabled` — Whether the [OverlayDropdownPreference] is enabled.
- `showValue` — Whether to show the selected value of the [OverlayDropdownPreference].
- `renderInRootScaffold` — Whether to render the popup in the root (outermost) Scaffold.   When true (default), the popup covers the full screen. When false, it renders within the   current Scaffold's bounds with position compensation.
- `onExpandedChange` — The callback to be invoked when the expanded state of the [OverlayDropdownPreference] changes.
- `onSelectedIndexChange` — The callback when the selected index of the [OverlayDropdownPreference] is changed.

**Traps**

- 🔴 It must be wrapped in a Scaffold. Without one, LocalPopupStates degrades to a default list that no host renders, and the overlay **silently fails to appear** -- no error, no crash, no log, just nothing happening on tap. Several doc examples (such as the Disabled State in overlaydropdownpreference.md) themselves fail to wrap it in a Scaffold.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/utils/MiuixPopupUtils.kt:595`)
- 🔴 Only the `items: List<String>` overload has onSelectedIndexChange. The entry / entries overloads **have no such parameter at all**: the selection callback must be written into each DropdownItem.onClick, and the selected state must be computed and passed in yourself as `selected = ...`. Calling the entries overload the way the items overload is written fails to compile.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:217`)
- 🔴 When items is empty the component automatically becomes disabled: `actualEnabled = enabled && itemsNotEmpty`. Even if you pass enabled = true, an empty list grays out this row, makes it non-clickable, and the popup never enters composition. When data loads asynchronously this is the expected "auto-gray while loading" behavior, but it is not in the doc.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:146`)
- 🟡 The default value of collapseOnSelection varies by overload: the items overload hard-codes true and does not expose the parameter; the entry overload defaults to true; the entries overload defaults to `entries.size <= 1` -- meaning with multiple groups it **does not collapse after selecting**.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:232`)
- 🟡 The entries overload's default collapseOnSelection uses the **unfiltered** entries.size, while rendering uses nonEmptyEntries after empty groups are filtered out. Passing an empty DropdownEntry (making size 2) silently flips the default from true to false, while the screen still shows only one group.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:250`)
- 🟡 The selected-value Text shown by the entries overload has no weight/align, while the single-group entry overload has `weight(1f, fill = false)` + align(CenterVertically). BasicComponent clamps the end area's width to 60% of the remaining width, and under that constraint weightless long text fills the Row and pushes the following 10dp arrow past the boundary. In the multi-group case a long selected value risks clipping the arrow.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:291`)
- ⚪ The multi-group overload joins the text of the selected item in every group with newlines into one block, rather than showing only one value. Moreover this concatenation is written inside the endActions lambda without remember, re-traversing all groups on every recomposition.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:282`)
- 🟡 The expanded state is self-held and **one-way out only**: there is only onExpandedChange to observe, no expanded input parameter, so the outside cannot programmatically expand or collapse the menu. The entire Dropdown/Spinner/Menu family is like this (isHoldDown too); none of them provides a controlled expanded.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:132`)
- 🟡 The items overload's `remember(items, selectedIndex, onSelectedIndexChange)` treats the callback lambda as a key. Call sites almost always write an inline lambda, whose identity changes on every recomposition, so the cache is invalidated every frame and the whole DropdownItem list is rebuilt every frame. To avoid it, remember a stable callback reference outside yourself.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:77`)
- ⚪ The press highlight is not released as soon as you let go: isHoldDown is reset by the overlay's onDismissFinished, i.e. this row does not return to normal until the menu's exit animation finishes. This is the intentional MIUI feel, but if you have wrapped your own animation listener you may feel the state is stuck.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:200`)
- 🟡 All four doc pages (overlaydropdownpreference / overlayspinnerpreference / windowdropdownpreference / windowspinnerpreference) write the default-value column of onSelectedIndexChange as `-` (meaning no default), while the source is actually `= null` and can be omitted. The Required column on the same row says No, contradicting itself.  (`docs/components/overlaydropdownpreference.md:218`)

**Spec** end_arrow DropdownArrowEndAction, a 10×16.dp bidirectional up-down arrow (MiuixIcons.Basic.ArrowUpDown), not ArrowRight · value_text body2 size, color onSurfaceVariantActions; when disabled/empty-list it is uniformly changed to disabledOnSecondaryVariant (arrow the same color) · popup_align The overlay is fixed to right alignment (PopupPositionProvider.Align.End), not changeable · popup_width Clamped by ListPopupColumn between 200.dp–288.dp, and only the **first 8 items'** intrinsic widths participate in measurement -- from the 9th item on, no matter how long, they do not contribute to the width and may be truncated · popup_row In popup mode each row has 20.dp left/right; the top of the first row and the bottom of the last row of the whole overlay are 20.dp, the rest 12.dp; a single line's inner text is limited to 216.dp width. This is the library's only "first/last item special-casing", and it changes padding, not corner radius · divider A 1.5.dp divider between groups, 20.dp left/right and 4.dp top/bottom; empty groups are filtered out beforehand, so dividers never appear on either side of an empty group · row Minimum height 56.dp, default padding 16.dp

**State** Value is controlled + expanded state is self-held. selectedIndex / DropdownItem.selected are given by the caller; isDropdownExpanded and isHoldDown are remembered internally (not rememberSaveable, so the menu collapses after a config change). Disabling has three layers ANDed together: row-level enabled → DropdownEntry.enabled (grays out the whole group but the menu still pops) → DropdownItem.enabled; in overlay rows the disabled color has the highest priority, overriding the selected state.

**vs Material3** Corresponds to material3's ExposedDropdownMenuBox + ExposedDropdownMenu, or androidx.preference's ListPreference. Differences: M3's expanded is controlled state held by the caller, whereas here it is self-held by the component and cannot be driven externally; M3's menu anchors on the text field with width following the anchor, while here it is fixed right-aligned with width clamped to 200–288dp; androidx's ListPreference has built-in entries/entryValues and persistence, none of which exist here.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayDropdownPreferenceDemo.kt:120`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayDropdownPreferenceDemo.kt#L120) · [`example/shared/src/commonMain/kotlin/AboutPage.kt:457`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L457) · [`example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt:116`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt#L116) · [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:200`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L200)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:58`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt#L58)</sub>

## OverlayDropdownPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.OverlayDropdownPreference

@Composable
fun OverlayDropdownPreference(
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
    showValue: Boolean = true,
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayDropdownPreferenceDemo.kt:120`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayDropdownPreferenceDemo.kt#L120) · [`example/shared/src/commonMain/kotlin/AboutPage.kt:457`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L457) · [`example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt:116`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt#L116) · [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:200`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L200)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:113`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt#L113)</sub>

## OverlayDropdownPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.OverlayDropdownPreference

@Composable
fun OverlayDropdownPreference(
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
    showValue: Boolean = true,
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = entries.size <= 1,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayDropdownPreferenceDemo.kt:120`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayDropdownPreferenceDemo.kt#L120) · [`example/shared/src/commonMain/kotlin/AboutPage.kt:457`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L457) · [`example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt:116`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/MultiScaffoldTestPage.kt#L116) · [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:200`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L200)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt:217`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlayDropdownPreference.kt#L217)</sub>

## OverlaySpinnerPreference  ·  preference

A heavier selection row than OverlayDropdownPreference: options are DropdownItem (supporting per-item icon, summary, and individual disabling), and it can be presented as either a popup menu or a dialog.

> A spinner component with Miuix style. (Popup Mode)

```kotlin
import top.yukonga.miuix.kmp.preference.OverlaySpinnerPreference

@Composable
fun OverlaySpinnerPreference(
    items: List<DropdownItem>,  // required
    selectedIndex: Int,  // required
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    maxHeight: Dp? = null,
    enabled: Boolean = true,
    showValue: Boolean = true,
    renderInRootScaffold: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    onSelectedIndexChange: ((Int) -> Unit)? = null,
)
```

- `items` — The list of [DropdownItem] to be shown in the [OverlaySpinnerPreference].
- `selectedIndex` — The index of the selected item in the [OverlaySpinnerPreference].
- `title` — The title of the [OverlaySpinnerPreference].
- `modifier` — The [Modifier] to be applied to the [OverlaySpinnerPreference].
- `titleColor` — The color of the title of the [OverlaySpinnerPreference].
- `summary` — The summary of the [OverlaySpinnerPreference].
- `summaryColor` — The color of the summary of the [OverlaySpinnerPreference].
- `spinnerColors` — The [SpinnerColors] of the [OverlaySpinnerPreference].
- `startAction` — The [Composable] content on the start side of the [OverlaySpinnerPreference].
- `bottomAction` — The [Composable] content at the bottom of the [OverlaySpinnerPreference].
- `insideMargin` — The [PaddingValues] to be applied inside the [OverlaySpinnerPreference].
- `maxHeight` — The maximum height of the dropdown popup.
- `enabled` — Whether the [OverlaySpinnerPreference] is enabled.
- `showValue` — Whether to show the value of the [OverlaySpinnerPreference].
- `renderInRootScaffold` — Whether to render the popup in the root (outermost) Scaffold.   When true (default), the popup covers the full screen. When false, it renders within the   current Scaffold's bounds with position compensation.
- `onExpandedChange` — The callback to be invoked when the expanded state of the [OverlaySpinnerPreference] changes.
- `onSelectedIndexChange` — The callback to be invoked when the selected index of the [OverlaySpinnerPreference] is changed.

**Traps**

- 🔴 popup mode and dialog mode are not a boolean toggle but are **selected by whether or not dialogButtonString is passed**, choosing the overload. It is required, has no default, and its position varies by overload: it is the 4th parameter in the items version and the 3rd in the entry / entries versions. Without it you land on the popup overload, with it you land on the dialog overload -- there are 6 functions of the same name in all, and it is very easy to pick the wrong one in IDE completion.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:288`)
- 🟡 The three dialog-mode overloads **have no maxHeight parameter**, so the dialog height cannot be limited (the list relies on an internal Layout measuring the button first and then giving the remaining height to the LazyColumn). Only popup mode has maxHeight.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:288`)
- 🟡 The default colors of the two modes differ: popup uses DropdownDefaults.dropdownColors() (selected background surfaceContainer), dialog uses dialogDropdownColors() (selected background tertiaryContainer, transparent container). The same data in a different mode gives the selected item a different background color.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:298`)
- 🟡 popup mode's expanded state uses rememberSaveable, while dialog mode and all other Dropdown/Menu components use ordinary remember. Consequence: after an Android config change or process restore, the popup-mode Spinner will **re-pop its menu by itself**; meanwhile the isHoldDown restored at the same moment is false (ordinary remember), so the press highlight and the expanded state do not match.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:174`)
- 🟡 The element type of items is DropdownItem, not List<String> (DropdownPreference is String). Internally it converts with item.copy(selected = ..., onClick = { onSelectedIndexChange(index); item.onClick?.invoke() }), which **keeps and chains** the onClick you originally wrote on the item -- both callbacks execute.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:82`)
- 🟡 The KDoc says `@param spinnerColors The [SpinnerColors] ...`, but SpinnerColors is already @Deprecated (a typealias of DropdownColors), and you should actually pass DropdownColors. Worse is another typealias: `SpinnerEntry = DropdownItem` (a single item), not DropdownEntry (a group). Literally translating SpinnerEntry → DropdownEntry by name from the old Spinner API is guaranteed to be wrong.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:536`)
- 🔴 Same as OverlayDropdownPreference: it must be wrapped in a Scaffold; the entry/entries overloads have no onSelectedIndexChange; empty entries auto-resolve to disabled; the expanded state is self-held and cannot be driven externally.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:190`)
- 🔴 The example in windowspinnerpreference.md writes `private class RoundedRectanglePainter(...)` as a local class inside the composable body -- Kotlin local classes cannot have the private modifier, so copying it fails to compile. The sister page overlayspinnerpreference.md and the demo both omit private.  (`docs/components/windowspinnerpreference.md:55`)

**Spec** dialog_layout Inside the dialog it first measures the bottom confirm button and then gives the remaining height to the LazyColumn, so the button is never pushed off-screen by a long list; the list is flush left/right with 24.dp top/bottom; the button has 24.dp left/right, 12.dp top, and a minimum height of 50.dp · dialog_row dialog-mode rows are 28.dp left/right, minimum height 56.dp, minimum width 200.dp and fillMaxWidth; all rows are uniformly 12.dp top/bottom (**deliberately no first/last special-casing**, because the list is scrollable); a single line's inner text is not width-limited · popup_row popup-mode rows are 20.dp left/right; first-row top / last-row bottom 20.dp, the rest 12.dp; a single line's inner text is limited to 216.dp width · item_slots Each item may have a leading icon (minimum 26.dp square + 12.dp trailing), primary text body1 Medium, and summary body2; the selected checkmark is 20.dp, and when not selected the checkmark is a transparent placeholder so the row width does not change · value_text The selected value on the right of the row is body2, with weight(1f, fill = false) and TextOverflow.Ellipsis

**State** Value controlled + expanded state self-held. popup mode's expanded state is restored across config changes (rememberSaveable), dialog mode's is not -- if you rely on "the menu should close after rotating the screen", popup mode breaks that expectation.

**vs Material3** Corresponds to a combination of androidx.preference's ListPreference (dialog form) and material3's ExposedDropdownMenu (popup form). M3 has no design of "the same component switching between overlay and dialog via one required string parameter"; androidx's ListPreference has built-in entryValues and persistence, none of which exist here.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt:160`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt#L160) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:178`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L178)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:60`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt#L60)</sub>

## OverlaySpinnerPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.OverlaySpinnerPreference

@Composable
fun OverlaySpinnerPreference(
    entry: DropdownEntry,  // required
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    maxHeight: Dp? = null,
    enabled: Boolean = true,
    showValue: Boolean = true,
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt:160`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt#L160) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:178`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L178)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:115`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt#L115)</sub>

## OverlaySpinnerPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.OverlaySpinnerPreference

@Composable
fun OverlaySpinnerPreference(
    entries: List<DropdownEntry>,  // required
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    maxHeight: Dp? = null,
    enabled: Boolean = true,
    showValue: Boolean = true,
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = entries.size <= 1,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt:160`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt#L160) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:178`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L178)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:155`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt#L155)</sub>

## OverlaySpinnerPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [OverlaySpinnerPreference] component with Miuix style, show Spinner as dialog. (Dialog Mode)

```kotlin
import top.yukonga.miuix.kmp.preference.OverlaySpinnerPreference

@Composable
fun OverlaySpinnerPreference(
    items: List<DropdownItem>,  // required
    selectedIndex: Int,  // required
    title: String,  // required
    dialogButtonString: String,  // required
    modifier: Modifier = Modifier,
    popupModifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dialogDropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    enabled: Boolean = true,
    showValue: Boolean = true,
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    onSelectedIndexChange: ((Int) -> Unit)? = null,
)
```

- `items` — the list of [DropdownItem] to be shown in the [OverlaySpinnerPreference].
- `selectedIndex` — the index of the selected item in the [OverlaySpinnerPreference].
- `title` — the title of the [OverlaySpinnerPreference].
- `dialogButtonString` — the string of the button in the dialog.
- `modifier` — the [Modifier] to be applied to the [OverlaySpinnerPreference].
- `popupModifier` — the [Modifier] to be applied to the popup of the [OverlaySpinnerPreference].
- `titleColor` — the color of the title of the [OverlaySpinnerPreference].
- `summary` — the summary of the [OverlaySpinnerPreference].
- `summaryColor` — the color of the summary of the [OverlaySpinnerPreference].
- `startAction` — the action to be shown at the start side of the [OverlaySpinnerPreference].
- `bottomAction` — the action to be shown at the bottom of the [OverlaySpinnerPreference].
- `insideMargin` — the [PaddingValues] to be applied inside the [OverlaySpinnerPreference].
- `enabled` — whether the [OverlaySpinnerPreference] is enabled.
- `showValue` — whether to show the value of the [OverlaySpinnerPreference].
- `renderInRootScaffold` — Whether to render the dialog in the root (outermost) Scaffold.   When true (default), the dialog covers the full screen. When false, it renders within the   current Scaffold's bounds.
- `onExpandedChange` — the callback to be invoked when the expanded state of the [OverlaySpinnerPreference] changes.
- `onSelectedIndexChange` — the callback to be invoked when the selected index of the [OverlaySpinnerPreference] is changed.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt:160`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt#L160) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:178`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L178)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:288`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt#L288)</sub>

## OverlaySpinnerPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.OverlaySpinnerPreference

@Composable
fun OverlaySpinnerPreference(
    entry: DropdownEntry,  // required
    title: String,  // required
    dialogButtonString: String,  // required
    modifier: Modifier = Modifier,
    popupModifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dialogDropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    enabled: Boolean = true,
    showValue: Boolean = true,
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt:160`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt#L160) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:178`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L178)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:344`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt#L344)</sub>

## OverlaySpinnerPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.OverlaySpinnerPreference

@Composable
fun OverlaySpinnerPreference(
    entries: List<DropdownEntry>,  // required
    title: String,  // required
    dialogButtonString: String,  // required
    modifier: Modifier = Modifier,
    popupModifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dialogDropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    enabled: Boolean = true,
    showValue: Boolean = true,
    renderInRootScaffold: Boolean = true,
    collapseOnSelection: Boolean = entries.size <= 1,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt:160`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlaySpinnerPreferenceDemo.kt#L160) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:178`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L178)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt:386`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/OverlaySpinnerPreference.kt#L386)</sub>

## RadioButtonPreference  ·  preference

A settings row with a radio button; the whole row is clickable. Used for a set of mutually exclusive options. When selected, the title and summary change color -- it is the only component in this group with a selected-state text feedback.

> A radio button with a title and a summary.

```kotlin
import top.yukonga.miuix.kmp.preference.RadioButtonPreference

@Composable
fun RadioButtonPreference(
    title: String,  // required
    selected: Boolean,  // required
    onClick: (() -> Unit)?,  // required
    modifier: Modifier = Modifier,
    summary: String? = null,
    colors: RadioButtonPreferenceColors = RadioButtonPreferenceDefaults.radioButtonPreferenceColors(),
    radioButtonColors: RadioButtonColors = RadioButtonDefaults.radioButtonColors(),
    startAction: @Composable (() -> Unit)? = null,
    endActions: @Composable (RowScope.() -> Unit)? = null,
    radioButtonLocation: RadioButtonLocation = RadioButtonLocation.Start,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    holdDownState: Boolean = false,
    enabled: Boolean = true,
)
```

- `title` — The title of the [RadioButtonPreference].
- `selected` — The selected state of the [RadioButtonPreference].
- `onClick` — The callback when the [RadioButtonPreference] is clicked.
- `modifier` — The modifier to be applied to the [RadioButtonPreference].
- `summary` — The summary of the [RadioButtonPreference].
- `colors` — The [RadioButtonPreferenceColors] of the title and summary.
- `radioButtonColors` — The [RadioButtonColors] of the [RadioButtonPreference].
- `startAction` — The [Composable] content on the start side of the [RadioButtonPreference].
- `endActions` — The [Composable] content on the end side of the [RadioButtonPreference].
- `radioButtonLocation` — The location of radio button, [RadioButtonLocation.Start] or [RadioButtonLocation.End].
- `bottomAction` — The [Composable] content at the bottom of the [RadioButtonPreference].
- `insideMargin` — The margin inside the [RadioButtonPreference].
- `holdDownState` — Used to determine whether it is in the pressed state.
- `enabled` — Whether the [RadioButtonPreference] is clickable.

**RadioButtonPreferenceDefaults**


```kotlin
RadioButtonPreferenceDefaults.radioButtonPreferenceColors(
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    selectedTitleColor: BasicComponentColors = BasicComponentDefaults.titleColor(color = MiuixTheme.colorScheme.primary),
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    selectedSummaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(color = MiuixTheme.colorScheme.primary),
)
```


**RadioButtonPreferenceColors** (data class) ⚠️ 4/4 constructor params are `private val` and **cannot be read from an instance**; these names are only usable as named arguments to the factory functions above.

**Traps**

- 🔴 There is no titleColor / summaryColor parameter; instead they are merged into a single `colors: RadioButtonPreferenceColors`. Copying `titleColor = ...` over from SwitchPreference / CheckboxPreference fails to compile (No parameter with name titleColor). To change colors you must go through RadioButtonPreferenceDefaults.radioButtonPreferenceColors(...).  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/RadioButtonPreference.kt:58`)
- 🟡 onClick is nullable but **has no default value** and must be passed explicitly. Passing null causes the same problem as CheckboxPreference: the row is still clickable, still shows press highlight, and just does nothing when tapped.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/RadioButtonPreference.kt:55`)
- 🟡 When selected, the title and summary default to the theme primary color. If your intuition from other Preferences assumes text color is constant, the selected item in a radio group will suddenly change color -- this is intentional design, but it is the only component in this group that does so. If you do not want it, explicitly set selectedTitleColor/selectedSummaryColor back to the normal color.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/RadioButtonPreference.kt:149`)
- ⚪ The RadioButton body is explicitly passed onClick = null, so it is not clickable and emits no haptics on its own; the whole-row click is the only interaction path, and the haptic fires at row level. The haptic type also depends on the selected state **before** the click: tapping an already-selected item again emits ToggleOff rather than ToggleOn.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/RadioButtonPreference.kt:86`)
- ⚪ All four fields of RadioButtonPreferenceColors are private val with only internal accessor methods. The doc listing them as readable properties is wrong; once you have an instance you cannot read any color.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/RadioButtonPreference.kt:163`)

**Spec** spacing The radio button has its own padding(end = 5.dp); startAction adds another 5.dp via StartActionSlot; BasicComponent adds a further 8.dp. Structurally identical to CheckboxPreference · selected_color Selected-state title/summary default to MiuixTheme.colorScheme.primary · row Minimum height 56.dp, default padding 16.dp

**State** Purely controlled. selected and the mutual-exclusion logic are entirely on the caller: typically `var selectedIndex by remember { mutableIntStateOf(0) }`, with each row passing `selected = index == selectedIndex` and `onClick = { selectedIndex = index }`. The components do not know about each other, and there is no RadioGroup-style container.

**vs Material3** Corresponds to material3 ListItem + RadioButton (with Modifier.selectableGroup()), or the expanded form of androidx.preference's ListPreference. Differences: there is no selectableGroup semantic container here, so a radio group is not recognized as one group in the accessibility tree; conversely M3 has no built-in "text turns theme color when selected".

**Compilable examples** [`docs/demo/src/commonMain/kotlin/RadioButtonDemo.kt:42`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/RadioButtonDemo.kt#L42) · [`docs/demo/src/commonMain/kotlin/RadioButtonPreferenceDemo.kt:42`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/RadioButtonPreferenceDemo.kt#L42) · [`example/shared/src/commonMain/kotlin/component/RadioButtonSection.kt:28`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/RadioButtonSection.kt#L28)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/RadioButtonPreference.kt:52`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/RadioButtonPreference.kt#L52)</sub>

## RangeSliderPreference  ·  preference

The two-thumb version of SliderPreference; value is a ClosedFloatingPointRange, used for price ranges, frequency bands, upper/lower thresholds, and similar dual-end selections.

> A range slider preference with a title and a summary.
> 
> The [RangeSlider] is placed in the [BasicComponent]'s bottom action area, displaying below the title and summary text.
> This component is typically used in settings screens for range selection scenarios such as price filters,
> frequency bands, or dual-threshold controls.

```kotlin
import top.yukonga.miuix.kmp.preference.RangeSliderPreference

@Composable
fun RangeSliderPreference(
    value: ClosedFloatingPointRange<Float>,  // required
    onValueChange: (ClosedFloatingPointRange<Float>) -> Unit,  // required
    modifier: Modifier = Modifier,
    title: String? = null,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    startAction: @Composable (() -> Unit)? = null,
    valueText: String? = null,
    endActions: @Composable (RowScope.() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    onClick: (() -> Unit)? = null,
    holdDownState: Boolean = false,
    enabled: Boolean = true,
    valueRange: ClosedFloatingPointRange<Float> = 0f..1f,
    steps: Int = 0,
    onValueChangeFinished: (() -> Unit)? = null,
    sliderHeight: Dp = SliderDefaults.MinHeight,
    sliderColors: SliderColors = SliderDefaults.sliderColors(),
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
    showKeyPoints: Boolean = false,
    keyPoints: List<Float>? = null,
    magnetThreshold: Float = 0.02f,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
)
```

- `value` — Current values of the [RangeSlider]. If either value is outside of [valueRange] provided, it will be coerced to this range.
- `onValueChange` — Lambda in which values should be updated.
- `modifier` — The modifier to be applied to the [RangeSliderPreference].
- `title` — The title of the [RangeSliderPreference].
- `titleColor` — The color of the title.
- `summary` — The summary of the [RangeSliderPreference].
- `summaryColor` — The color of the summary.
- `startAction` — The [Composable] content on the start side of the [RangeSliderPreference].
- `valueText` — A nullable [String] representing the current slider value, displayed in the end area with summary-style formatting.   If null, no value text is shown. The text is rendered inside the existing [Row] layout structure with [Alignment.CenterVertically]   and [RowScope.weight] applied, consistent with the summary text style.
- `endActions` — The [Composable] content on the end side of the [RangeSliderPreference], following the [valueText] within the same [Row].
- `bottomAction` — The [Composable] content at the top of the bottom area, above the [RangeSlider].
- `onClick` — The callback triggered when the [RangeSliderPreference] is clicked. When non-null, an arrow icon is displayed in the end area.
- `holdDownState` — Used to determine whether the component is in the pressed state.
- `enabled` — Whether the [RangeSliderPreference] is enabled.
- `valueRange` — Range of values that [RangeSlider] values can take. Passed [value] will be coerced to this range.
- `steps` — If positive, specifies the amount of discrete allowable values between the endpoints of [valueRange].
- `onValueChangeFinished` — Lambda to be invoked when value change has ended.
- `sliderHeight` — The height of the [RangeSlider].
- `sliderColors` — The [SliderColors] of the [RangeSlider].
- `hapticEffect` — The haptic effect of the [RangeSlider].
- `showKeyPoints` — Whether to show the key points (step indicators) on the slider. Only works when [keyPoints] is not null.
- `keyPoints` — Custom key point values to display on the slider. If null, uses step positions from [steps] parameter.   Values should be within [valueRange].
- `magnetThreshold` — The magnetic snap threshold as a fraction (0.0 to 1.0). When the slider value is within this   distance from a key point, it will snap to that point. Default is 0.02 (2%). Only applies when [keyPoints] is set.
- `insideMargin` — The margin inside the [RangeSliderPreference].

**Traps**

- 🟡 It has one fewer parameter than SliderPreference: no reverseDirection (24 parameters vs 25). Copying call code from SliderPreference that includes reverseDirection = ... fails to compile.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SliderPreference.kt:212`)
- 🔴 Same as SliderPreference: the doc semantics of showKeyPoints are reversed. When keyPoints is non-null, points are drawn regardless of whether showKeyPoints is true or false; showKeyPoints only decides whether to draw the step points when keyPoints == null.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:1329`)
- 🟡 The underlying RangeSlider likewise has require(steps >= 0) and require(valueRange.start < valueRange.endInclusive), so an illegal range throws rather than being silently corrected.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:513`)
- 🟡 bottomAction is likewise redefined as content "above the slider"; onClick is likewise bound to the right arrow; valueText color is likewise hard-coded. All three are line-for-line the same as SliderPreference.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SliderPreference.kt:275`)
- 🔴 The doc's "With Start Icon" example likewise uses the non-existent `MiuixIcons.Basic.Audio`; copying it fails to compile.  (`docs/components/rangesliderpreference.md:113`)

**Spec** title title is String?, omittable · arrow 10×16.dp, sharing the same private implementation as SliderPreference · gap A fixed 8.dp between the title area and the slider

**State** Purely controlled. value is a ClosedFloatingPointRange<Float>, remembered by the caller; onValueChange returns the new range every frame. There is no role, so the screen-reader semantics come only from the underlying RangeSlider.

**vs Material3** material3 has a RangeSlider but no corresponding Preference wrapper; androidx.preference has no range-type Preference at all. This is a Miuix-specific addition.

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/SliderSection.kt:101`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SliderSection.kt#L101)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SliderPreference.kt:212`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SliderPreference.kt#L212)</sub>

## SliderPreference  ·  preference

A settings row with a slider below the title, optionally showing the current value text on the right; used for continuous adjustments like volume, brightness, or font size. The slider renders in BasicComponent's bottomAction area, not inline in the row.

> A slider preference with a title and a summary.
> 
> The [Slider] is placed in the [BasicComponent]'s bottom action area, displaying below the title and summary text.
> This component is typically used in settings screens for value adjustment scenarios such as volume, brightness,
> or font size controls.

```kotlin
import top.yukonga.miuix.kmp.preference.SliderPreference

@Composable
fun SliderPreference(
    value: Float,  // required
    onValueChange: (Float) -> Unit,  // required
    modifier: Modifier = Modifier,
    title: String? = null,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    startAction: @Composable (() -> Unit)? = null,
    valueText: String? = null,
    endActions: @Composable (RowScope.() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    onClick: (() -> Unit)? = null,
    holdDownState: Boolean = false,
    enabled: Boolean = true,
    valueRange: ClosedFloatingPointRange<Float> = 0f..1f,
    steps: Int = 0,
    onValueChangeFinished: (() -> Unit)? = null,
    reverseDirection: Boolean = false,
    sliderHeight: Dp = SliderDefaults.MinHeight,
    sliderColors: SliderColors = SliderDefaults.sliderColors(),
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
    showKeyPoints: Boolean = false,
    keyPoints: List<Float>? = null,
    magnetThreshold: Float = 0.02f,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
)
```

- `value` — The current value of the [Slider]. If outside of [valueRange] provided, value will be coerced to this range.
- `onValueChange` — The callback to be called when the value changes.
- `modifier` — The modifier to be applied to the [SliderPreference].
- `title` — The title of the [SliderPreference].
- `titleColor` — The color of the title.
- `summary` — The summary of the [SliderPreference].
- `summaryColor` — The color of the summary.
- `startAction` — The [Composable] content on the start side of the [SliderPreference].
- `valueText` — A nullable [String] representing the current slider value, displayed in the end area with summary-style formatting.   If null, no value text is shown. The text is rendered inside the existing [Row] layout structure with [Alignment.CenterVertically]   and [RowScope.weight] applied, consistent with the summary text style.
- `endActions` — The [Composable] content on the end side of the [SliderPreference], following the [valueText] within the same [Row].
- `bottomAction` — The [Composable] content at the top of the bottom area, above the [Slider].
- `onClick` — The callback triggered when the [SliderPreference] is clicked. When non-null, an arrow icon is displayed in the end area.
- `holdDownState` — Used to determine whether the component is in the pressed state.
- `enabled` — Whether the [SliderPreference] is enabled.
- `valueRange` — Range of values that this slider can take. The passed [value] will be coerced to this range.
- `steps` — If positive, specifies the amount of discrete allowable values between the endpoints of [valueRange].   For example, a range from 0 to 10 with 4 [steps] allows 4 values evenly distributed between 0 and 10 (i.e., 2, 4, 6, 8).   If [steps] is 0, the slider will behave continuously and allow any value from the range. Must not be negative.
- `onValueChangeFinished` — Called when value change has ended. This should not be used to update the slider value   (use [onValueChange] instead), but rather to know when the user has completed selecting a new value by ending a drag or a click.
- `reverseDirection` — Controls the direction of this slider. When false (default), slider increases from left to right.   When true, slider increases from right to left (useful for RTL layouts or custom direction requirements).
- `sliderHeight` — The height of the [Slider].
- `sliderColors` — The [SliderColors] of the [Slider].
- `hapticEffect` — The haptic effect of the [Slider].
- `showKeyPoints` — Whether to show the key points (step indicators) on the slider. Only works when [keyPoints] is not null.
- `keyPoints` — Custom key point values to display on the slider. If null, uses step positions from [steps] parameter.   Values should be within [valueRange]. For example, for a range of 0f..100f, you might specify listOf(0f, 25f, 50f, 75f, 100f).
- `magnetThreshold` — The magnetic snap threshold as a fraction (0.0 to 1.0). When the slider value is within this   distance from a key point, it will snap to that point. Default is 0.02 (2%). Only applies when [keyPoints] is set.
- `insideMargin` — The margin inside the [SliderPreference].

**Traps**

- 🟡 The bottomAction you pass is not the "bottom-most" content but is redefined as content "above the slider" -- internally the component wraps bottomAction into `Column { your bottomAction; Slider }`. There is no slot to place something below the slider.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SliderPreference.kt:147`)
- 🟡 "Clickable" and "shows an arrow" are bound together: `showArrow = onClick != null`. Passing onClick necessarily produces the right arrow; you cannot have a clickable slider row without an arrow, nor conversely show only an arrow without responding to clicks.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SliderPreference.kt:112`)
- 🔴 The KDoc for showKeyPoints says "Only works when keyPoints is not null", but the actual semantics are exactly the opposite: computeKeyPointFractions branches so that if keyPoints is non-null it draws the custom points (ignoring showKeyPoints), and showKeyPoints only decides whether to draw the points at step positions when keyPoints == null. Writing `keyPoints = listOf(...)` + `showKeyPoints = false` per the doc expecting no points to be drawn will still draw them.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:1329`)
- 🟡 The real condition under which magnetThreshold takes effect is stronger than the doc: resolveValueFromFraction returns straight into the quantization branch when steps > 0, so the magnet code never runs. Magnet only makes sense when steps == 0 and keyPoints != null. The doc only says "Only applies when keyPoints is set".  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:1264`)
- 🟡 An illegal valueRange or a negative steps throws IllegalArgumentException directly, not the "will be coerced" the doc implies. The underlying Slider has require(steps >= 0) and require(valueRange.start < valueRange.endInclusive), so an empty or reversed range crashes on the spot. Only value itself is coerced.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:104`)
- ⚪ The valueText's size and color are hard-coded in the component (body2 + onSurfaceVariantActions / disabled color), do not go through any colors parameter, and are not affected by summaryColor. To customize it you can only switch to drawing your own via endActions.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SliderPreference.kt:132`)
- 🔴 The doc's "With Start Icon" example uses `MiuixIcons.Basic.Audio`, which does not exist -- the Basic icon set has only seven: ArrowRight / ArrowUpDown / Check / Close / Search / SearchCleanup / Sidebar. Copying it fails to compile (unresolved reference).  (`docs/components/sliderpreference.md:114`)
- 🟡 The doc's property table places title before modifier, while the source order is (value, onValueChange, modifier, title, ...). Writing positional arguments in the table's order causes type mismatches.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SliderPreference.kt:84`)
- ⚪ It does not pass a role, so a screen reader will not announce this row as an adjustable control (the slider body carries its own semantics, but the outer row does not).  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SliderPreference.kt:115`)

**Spec** title title is String? -- the only Preference in this group that allows no title; passing null produces no Text at all (not a blank placeholder row) · arrow 10×16.dp, a line-by-line copy of ArrowPreference's arrow (same RTL scaleX mirroring, same reuse of ArrowPreferenceDefaults.endActionColors()) · gap A fixed 8.dp between the title area and the slider (a Spacer BasicComponent inserts before bottomAction), not adjustable · row Minimum height 56.dp, but the slider and text stretch it taller; default padding 16.dp

**State** Purely controlled. value and onValueChange are held by the caller; onValueChangeFinished is only for knowing that dragging ended -- do not write the value back inside it. Of the 25 parameters, the vast majority flatten the underlying Slider's tuning surface as-is; the Preference layer does no processing.

**vs Material3** Corresponds to material3's ListItem + Slider combination; androidx.preference's SeekBarPreference is the closest. Differences: SeekBarPreference auto-persists an integer value and has XML attributes for min/max/increment, none of which exist here; conversely this adds keyPoints (custom key points), magnetThreshold (magnet), hapticEffect, and reverseDirection, capabilities M3 Slider lacks.

**Compilable examples** [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:242`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L242) · [`example/shared/src/commonMain/kotlin/component/ArrowSection.kt:71`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ArrowSection.kt#L71) · [`example/shared/src/commonMain/kotlin/component/BlurSection.kt:179`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BlurSection.kt#L179) · [`example/shared/src/commonMain/kotlin/component/SliderSection.kt:41`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SliderSection.kt#L41)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SliderPreference.kt:83`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SliderPreference.kt#L83)</sub>

## SwitchPreference  ·  preference

A settings row with a switch; the whole row is clickable to toggle. Used for boolean settings. Purely controlled: checked in, onCheckedChange out.

> A switch with a title and a summary.

```kotlin
import top.yukonga.miuix.kmp.preference.SwitchPreference

@Composable
fun SwitchPreference(
    checked: Boolean,  // required
    onCheckedChange: (Boolean) -> Unit,  // required
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    startAction: @Composable (() -> Unit)? = null,
    endActions: @Composable RowScope.() -> Unit = {},
    bottomAction: (@Composable () -> Unit)? = null,
    switchColors: SwitchColors = SwitchDefaults.switchColors(),
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    holdDownState: Boolean = false,
    enabled: Boolean = true,
)
```

- `checked` — The checked state of the [SwitchPreference].
- `onCheckedChange` — The callback when the checked state of the [SwitchPreference] is changed.
- `title` — The title of the [SwitchPreference].
- `modifier` — The modifier to be applied to the [SwitchPreference].
- `titleColor` — The color of the title.
- `summary` — The summary of the [SwitchPreference].
- `summaryColor` — The color of the summary.
- `startAction` — The [Composable] content on the start side of the [SwitchPreference].
- `endActions` — The [Composable] content on the end side of the [SwitchPreference].
- `bottomAction` — The [Composable] content at the bottom of the [SwitchPreference].
- `switchColors` — The [SwitchColors] of the [SwitchPreference].
- `insideMargin` — The margin inside the [SwitchPreference].
- `holdDownState` — Used to determine whether it is in the pressed state.
- `enabled` — Whether the [SwitchPreference] is clickable.

**Traps**

- 🔴 The parameter order is the reverse of CheckboxPreference: SwitchPreference is (checked, onCheckedChange, title, ...), CheckboxPreference is (title, checked, onCheckedChange, ...). Copy-pasting positional arguments between the two fails to compile (String passed to Boolean). Always use named arguments.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SwitchPreference.kt:46`)
- 🟡 onCheckedChange is a non-null `(Boolean) -> Unit`, inconsistent with the nullable types of CheckboxPreference/RadioButtonPreference in the same group. The underlying Switch supports passing a null callback for read-only semantics (no toggleable attached), but the Preference layer does not forward null, so you cannot make a read-only switch here -- you can only use enabled = false.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SwitchPreference.kt:47`)
- ⚪ Haptic feedback fires only when you tap the switch itself. Once the Switch receives a non-null callback it attaches toggleable and emits ToggleOn/ToggleOff haptics; tapping other areas of the row goes through BasicComponent.onClick with no haptics at all. On the same settings page, Switch/Checkbox have control-level haptics while RadioButtonPreference has row-level haptics, so the three feel inconsistent.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Switch.kt:119`)
- ⚪ There are two toggleable nodes in the accessibility tree: the outer row clickable(role = Role.Switch) and the inner Switch toggleable(role = Role.Switch). A screen reader may read it twice.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SwitchPreference.kt:90`)
- 🟡 In the Chinese doc switchpreference.md the "Type" column of the property table was written as `Yes` (the value from the English Required column shifted over), so following it you would not know the callback signature. The actual type is `(Boolean) -> Unit`, and it is required.  (`docs/zh_CN/components/switchpreference.md:63`)

**Spec** row Minimum height 56.dp, default padding 16.dp; the switch body's size is decided by miuix-ui's Switch, the Preference layer only forwards switchColors · gap A fixed 8.dp between endActions and the switch (endActions defaults to `{}`, so that wrapping Row always exists)

**State** Purely controlled. The caller keeps its own `var checked by remember { mutableStateOf(false) }` and, inside onCheckedChange, both updates the state and persists it. The component does not remember, restore, or know about a settings key.

**vs Material3** Corresponds to material3's ListItem + Switch combination, or androidx.preference's SwitchPreferenceCompat. The fundamental difference from the latter is zero persistence: no key, no defaultValue, no automatic write to SharedPreferences. The difference from M3 Switch is that there is no thumbContent slot here, and the whole-row click and the control click are two different gesture paths (different haptics).

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayBottomSheetDemo.kt:82`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayBottomSheetDemo.kt#L82) · [`docs/demo/src/commonMain/kotlin/SwitchPreferenceDemo.kt:45`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SwitchPreferenceDemo.kt#L45) · [`docs/demo/src/commonMain/kotlin/WindowBottomSheetDemo.kt:83`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowBottomSheetDemo.kt#L83) · [`example/shared/src/commonMain/kotlin/AboutPage.kt:464`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AboutPage.kt#L464)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SwitchPreference.kt:45`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/SwitchPreference.kt#L45)</sub>

## WindowDropdownPreference  ·  preference

Structurally identical to OverlayDropdownPreference, differing only in that the overlay uses a platform window rather than a Scaffold overlay slot; it does not depend on a Scaffold, and the menu can extend beyond the host window's bounds.

> A dropdown with a title and a summary, rendered at window level without `Scaffold`.

```kotlin
import top.yukonga.miuix.kmp.preference.WindowDropdownPreference

@Composable
fun WindowDropdownPreference(
    items: List<String>,  // required
    selectedIndex: Int,  // required
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
    showValue: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    onSelectedIndexChange: ((Int) -> Unit)? = null,
)
```

- `items` — The options of the [WindowDropdownPreference].
- `selectedIndex` — The index of the selected option.
- `title` — The title of the [WindowDropdownPreference].
- `modifier` — The modifier to be applied to the [WindowDropdownPreference].
- `titleColor` — The color of the title.
- `summary` — The summary of the [WindowDropdownPreference].
- `summaryColor` — The color of the summary.
- `dropdownColors` — The [DropdownColors] of the [WindowDropdownPreference].
- `startAction` — The [Composable] content on the start side of the [WindowDropdownPreference].
- `bottomAction` — The [Composable] content at the bottom of the [WindowDropdownPreference].
- `insideMargin` — The margin inside the [WindowDropdownPreference].
- `maxHeight` — The maximum height of the [WindowListPopup].
- `enabled` — Whether the [WindowDropdownPreference] is enabled.
- `showValue` — Whether to show the selected value of the [WindowDropdownPreference].
- `onExpandedChange` — The callback to be invoked when the expanded state of the [WindowDropdownPreference] changes.
- `onSelectedIndexChange` — The callback when the selected index of the [WindowDropdownPreference] is changed.

**Traps**

- 🔴 It has no renderInRootScaffold parameter (the Overlay version does). The entire Window* family does not accept this parameter, so copying call code from the Overlay version with it included fails to compile. Conversely this also means the Window version can be used without a Scaffold.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt:109`)
- 🔴 The entry / entries overloads likewise have no onSelectedIndexChange; only the items: List<String> overload does.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt:211`)
- 🔴 An empty items / all-empty groups likewise auto-resolve to disabled: `actualEnabled = enabled && itemsNotEmpty` (the entries version is `enabled && hasEntries`); passing emptyList() shows a disabled state even with enabled = true, and the popup is not created.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt:141`)
- 🟡 The showValue behavior of the two overloads differs: the entry version takes the text of the first selected item and carries weight/align; the entries version joins the selected items' text of all groups with newlines, and that Text has no weight and no align, so it easily competes with the arrow for space.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt:283`)
- 🟡 collapseOnSelection defaults: entry overload true, entries overload `entries.size <= 1`; the items overload does not expose the parameter (hard-codes true internally).  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt:225`)
- 🟡 The expanded state is likewise self-held and one-way out only (only onExpandedChange, no expanded input parameter).  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt:136`)

**Spec** same_as_overlay The visual spec is exactly the same as OverlayDropdownPreference: 10×16.dp up-down arrow, right-aligned overlay, width 200–288.dp, first/last rows 20.dp and the rest 12.dp, divider 1.5.dp · difference The only difference is the overlay is hosted on the platform window layer, can extend beyond the host Scaffold/window bounds, and is not subject to the Scaffold's blur/scale processing

**State** Same as the Overlay version: value controlled, expanded state self-held. The collapse path takes one extra hop: it goes through LocalDismissState rather than calling onDismiss directly; that CompositionLocal defaults to null, so in theory if it cannot be obtained it silently fails to collapse.

**vs Material3** Same as OverlayDropdownPreference. Relative to M3's DropdownMenu (itself a platform Popup), the Window version behaves closer in positioning and crossing bounds, but expanded is still not externally controllable.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowDropdownPreferenceDemo.kt:118`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowDropdownPreferenceDemo.kt#L118) · [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:209`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L209) · [`example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt:185`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt#L185) · [`example/shared/src/commonMain/kotlin/component/DropdownSection.kt:150`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/DropdownSection.kt#L150)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt:56`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt#L56)</sub>

## WindowDropdownPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.WindowDropdownPreference

@Composable
fun WindowDropdownPreference(
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
    showValue: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowDropdownPreferenceDemo.kt:118`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowDropdownPreferenceDemo.kt#L118) · [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:209`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L209) · [`example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt:185`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt#L185) · [`example/shared/src/commonMain/kotlin/component/DropdownSection.kt:150`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/DropdownSection.kt#L150)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt:109`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt#L109)</sub>

## WindowDropdownPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.WindowDropdownPreference

@Composable
fun WindowDropdownPreference(
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
    showValue: Boolean = true,
    collapseOnSelection: Boolean = entries.size <= 1,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowDropdownPreferenceDemo.kt:118`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowDropdownPreferenceDemo.kt#L118) · [`example/shared/src/commonMain/kotlin/PullToRefreshPage.kt:209`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/PullToRefreshPage.kt#L209) · [`example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt:185`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt#L185) · [`example/shared/src/commonMain/kotlin/component/DropdownSection.kt:150`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/DropdownSection.kt#L150)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt:211`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowDropdownPreference.kt#L211)</sub>

## WindowSpinnerPreference  ·  preference

The platform-window version of OverlaySpinnerPreference: likewise dual popup/dialog modes and DropdownItem options, but it does not depend on a Scaffold.

> A spinner component with Miuix style, rendered at window level without `Scaffold`. (Popup Mode)

```kotlin
import top.yukonga.miuix.kmp.preference.WindowSpinnerPreference

@Composable
fun WindowSpinnerPreference(
    items: List<DropdownItem>,  // required
    selectedIndex: Int,  // required
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    maxHeight: Dp? = null,
    enabled: Boolean = true,
    showValue: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    onSelectedIndexChange: ((Int) -> Unit)? = null,
)
```

- `items` — The list of [DropdownItem] to be shown in the [WindowSpinnerPreference].
- `selectedIndex` — The index of the selected item in the [WindowSpinnerPreference].
- `title` — The title of the [WindowSpinnerPreference].
- `modifier` — The [Modifier] to be applied to the [WindowSpinnerPreference].
- `titleColor` — The color of the title of the [WindowSpinnerPreference].
- `summary` — The summary of the [WindowSpinnerPreference].
- `summaryColor` — The color of the summary of the [WindowSpinnerPreference].
- `spinnerColors` — The [SpinnerColors] of the [WindowSpinnerPreference].
- `startAction` — The [Composable] content on the start side of the [WindowSpinnerPreference].
- `bottomAction` — The [Composable] content at the bottom of the [WindowSpinnerPreference].
- `insideMargin` — The [PaddingValues] to be applied inside the [WindowSpinnerPreference].
- `maxHeight` — The maximum height of the dropdown popup.
- `enabled` — Whether the [WindowSpinnerPreference] is enabled.
- `showValue` — Whether to show the value of the [WindowSpinnerPreference].
- `onExpandedChange` — The callback to be invoked when the expanded state of the [WindowSpinnerPreference] changes.
- `onSelectedIndexChange` — The callback to be invoked when the selected index of the [WindowSpinnerPreference] is changed.

**Traps**

- 🔴 It has no renderInRootScaffold parameter (every overload of the Overlay version does). Copying a call from the Overlay version fails to compile.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt:146`)
- 🔴 It likewise switches between the popup / dialog overloads by whether dialogButtonString is present; dialog mode likewise has no maxHeight.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt:273`)
- 🟡 popup mode's expanded state uses rememberSaveable while dialog mode uses ordinary remember, the same inconsistency as the Overlay version: after a config change, popup re-pops by itself.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt:164`)
- 🔴 Empty entries auto-resolve to disabled (actualEnabled = enabled && hasEntries), and the overlay does not participate in composition at all.  (`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt:178`)
- 🟡 If you build options using DropdownItem's compatibility secondary constructor `DropdownItem(icon, title, summary)` and pass null for title, text becomes an empty string; the row's showValue on the right silently shows nothing because of the `text.isNullOrEmpty()` check. None of the 7 doc pages document this secondary constructor.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:351`)
- 🔴 The doc example's `private class RoundedRectanglePainter(...)` is a local class inside the composable body; Kotlin does not allow private local classes, so copying it fails to compile.  (`docs/components/windowspinnerpreference.md:55`)

**Spec** same_as_overlay Row and overlay specs are the same as OverlaySpinnerPreference: popup rows 20.dp left/right / first-last 20.dp / rest 12.dp / inner text limited to 216.dp; dialog rows 28.dp left/right, uniformly 12.dp, not width-limited; divider 1.5.dp · difference The overlay is hosted on the platform window layer, can extend beyond the host bounds, and is not affected by the Scaffold

**State** Same as the Overlay version. Collapse goes through LocalDismissState (default null) rather than calling onDismiss directly.

**vs Material3** Same as OverlaySpinnerPreference. Relative to M3, the Window version is closer to material3 DropdownMenu's platform Popup behavior on "can the menu extend beyond the parent container".

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt:158`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt#L158) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:186`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L186)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt:57`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt#L57)</sub>

## WindowSpinnerPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.WindowSpinnerPreference

@Composable
fun WindowSpinnerPreference(
    entry: DropdownEntry,  // required
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    maxHeight: Dp? = null,
    enabled: Boolean = true,
    showValue: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt:158`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt#L158) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:186`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L186)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt:108`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt#L108)</sub>

## WindowSpinnerPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.WindowSpinnerPreference

@Composable
fun WindowSpinnerPreference(
    entries: List<DropdownEntry>,  // required
    title: String,  // required
    modifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    maxHeight: Dp? = null,
    enabled: Boolean = true,
    showValue: Boolean = true,
    collapseOnSelection: Boolean = entries.size <= 1,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt:158`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt#L158) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:186`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L186)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt:146`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt#L146)</sub>

## WindowSpinnerPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [WindowSpinnerPreference] component with Miuix style, show Spinner as dialog, rendered at window level without `Scaffold`. (Dialog Mode)

```kotlin
import top.yukonga.miuix.kmp.preference.WindowSpinnerPreference

@Composable
fun WindowSpinnerPreference(
    items: List<DropdownItem>,  // required
    selectedIndex: Int,  // required
    title: String,  // required
    dialogButtonString: String,  // required
    modifier: Modifier = Modifier,
    popupModifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dialogDropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    enabled: Boolean = true,
    showValue: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
    onSelectedIndexChange: ((Int) -> Unit)? = null,
)
```

- `items` — the list of [DropdownItem] to be shown in the [WindowSpinnerPreference].
- `selectedIndex` — the index of the selected item in the [WindowSpinnerPreference].
- `title` — the title of the [WindowSpinnerPreference].
- `dialogButtonString` — the string of the button in the dialog.
- `modifier` — the [Modifier] to be applied to the [WindowSpinnerPreference].
- `popupModifier` — the [Modifier] to be applied to the popup of the [WindowSpinnerPreference].
- `titleColor` — the color of the title of the [WindowSpinnerPreference].
- `summary` — the summary of the [WindowSpinnerPreference].
- `summaryColor` — the color of the summary of the [WindowSpinnerPreference].
- `startAction` — the action to be shown at the start side of the [WindowSpinnerPreference].
- `bottomAction` — The [Composable] content at the bottom of the [WindowSpinnerPreference].
- `insideMargin` — the [PaddingValues] to be applied inside the [WindowSpinnerPreference].
- `enabled` — whether the [WindowSpinnerPreference] is enabled.
- `showValue` — whether to show the value of the [WindowSpinnerPreference].
- `onExpandedChange` — the callback to be invoked when the expanded state of the [WindowSpinnerPreference] changes.
- `onSelectedIndexChange` — the callback to be invoked when the selected index of the [WindowSpinnerPreference] is changed.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt:158`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt#L158) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:186`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L186)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt:274`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt#L274)</sub>

## WindowSpinnerPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.WindowSpinnerPreference

@Composable
fun WindowSpinnerPreference(
    entry: DropdownEntry,  // required
    title: String,  // required
    dialogButtonString: String,  // required
    modifier: Modifier = Modifier,
    popupModifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dialogDropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    enabled: Boolean = true,
    showValue: Boolean = true,
    collapseOnSelection: Boolean = true,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt:158`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt#L158) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:186`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L186)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt:328`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt#L328)</sub>

## WindowSpinnerPreference  ·  preference

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.preference.WindowSpinnerPreference

@Composable
fun WindowSpinnerPreference(
    entries: List<DropdownEntry>,  // required
    title: String,  // required
    dialogButtonString: String,  // required
    modifier: Modifier = Modifier,
    popupModifier: Modifier = Modifier,
    titleColor: BasicComponentColors = BasicComponentDefaults.titleColor(),
    summary: String? = null,
    summaryColor: BasicComponentColors = BasicComponentDefaults.summaryColor(),
    spinnerColors: DropdownColors = DropdownDefaults.dialogDropdownColors(),
    startAction: @Composable (() -> Unit)? = null,
    bottomAction: (@Composable () -> Unit)? = null,
    insideMargin: PaddingValues = BasicComponentDefaults.InsideMargin,
    enabled: Boolean = true,
    showValue: Boolean = true,
    collapseOnSelection: Boolean = entries.size <= 1,
    onExpandedChange: ((Boolean) -> Unit)? = null,
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt:158`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowSpinnerPreferenceDemo.kt#L158) · [`example/shared/src/commonMain/kotlin/component/SpinnerSection.kt:186`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SpinnerSection.kt#L186)

<sub>Source [`miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt:368`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-preference/src/commonMain/kotlin/top/yukonga/miuix/kmp/preference/WindowSpinnerPreference.kt#L368)</sub>

## Public types in this topic (4)

- `ArrowPreferenceDefaults` **object** · `import top.yukonga.miuix.kmp.preference.ArrowPreferenceDefaults`
- `CheckboxLocation` **enum** — Start, End · `import top.yukonga.miuix.kmp.preference.CheckboxLocation`
- `RadioButtonLocation` **enum** — Start, End · `import top.yukonga.miuix.kmp.preference.RadioButtonLocation`
- `RadioButtonPreferenceDefaults` **object** · `import top.yukonga.miuix.kmp.preference.RadioButtonPreferenceDefaults`

