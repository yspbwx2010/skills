# Input controls

Button, Switch, Checkbox, RadioButton, Slider, TextField, NumberPicker, Dropdown. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## Button  ·  basic component

Miuix's basic button, squircle corners + content slot (RowScope). The default is a gray-background button; for a blue-background primary button you must explicitly swap colors.

> A [Button] component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.Button

@Composable
fun Button(
    onClick: () -> Unit,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    cornerRadius: Dp = ButtonDefaults.CornerRadius,
    minWidth: Dp = ButtonDefaults.MinWidth,
    minHeight: Dp = ButtonDefaults.MinHeight,
    colors: ButtonColors = ButtonDefaults.buttonColors(),
    insideMargin: PaddingValues = ButtonDefaults.InsideMargin,
    interactionSource: MutableInteractionSource? = null,
    indication: Indication? = LocalIndication.current,
    content: @Composable RowScope.() -> Unit,  // required
)
```

- `onClick` — The callback when the [Button] is clicked.
- `modifier` — The modifier to be applied to the [Button].
- `enabled` — Whether the [Button] is enabled.
- `cornerRadius` — The corner radius of the [Button].
- `minWidth` — The minimum width of the [Button].
- `minHeight` — The minimum height of the [Button].
- `colors` — The [ButtonColors] of the [Button].
- `insideMargin` — The margin inside the [Button].
- `interactionSource` — The [MutableInteractionSource] to be used for the [Button].
- `indication` — The [Indication] to be used for the [Button].
- `content` — The [Composable] content of the [Button].

**ButtonDefaults**


```kotlin
ButtonDefaults.buttonColors(
    color: Color = MiuixTheme.colorScheme.secondaryVariant,
    disabledColor: Color = MiuixTheme.colorScheme.disabledSecondaryVariant,
    contentColor: Color = MiuixTheme.colorScheme.onSecondaryVariant,
    disabledContentColor: Color = MiuixTheme.colorScheme.disabledOnSecondaryVariant,
)
```


```kotlin
ButtonDefaults.buttonColorsPrimary(
    color: Color = MiuixTheme.colorScheme.primary,
    disabledColor: Color = MiuixTheme.colorScheme.disabledPrimaryButton,
    contentColor: Color = MiuixTheme.colorScheme.onPrimary,
    disabledContentColor: Color = MiuixTheme.colorScheme.disabledOnPrimaryButton,
)
```


```kotlin
ButtonDefaults.textButtonColors(
    color: Color = MiuixTheme.colorScheme.secondaryVariant,
    disabledColor: Color = MiuixTheme.colorScheme.disabledSecondaryVariant,
    textColor: Color = MiuixTheme.colorScheme.onSecondaryVariant,
    disabledTextColor: Color = MiuixTheme.colorScheme.disabledOnSecondaryVariant,
)
```


```kotlin
ButtonDefaults.textButtonColorsPrimary(
    color: Color = MiuixTheme.colorScheme.primary,
    disabledColor: Color = MiuixTheme.colorScheme.disabledPrimaryButton,
    textColor: Color = MiuixTheme.colorScheme.onPrimary,
    disabledTextColor: Color = MiuixTheme.colorScheme.disabledOnPrimaryButton,
)
```

- `MinWidth = 58.dp`
- `MinHeight = 40.dp`
- `CornerRadius = 16.dp`
- `InsideMargin = PaddingValues(horizontal = 16.dp, vertical = 13.dp)`

**ButtonColors** (data class) 

**Traps**

- 🟡 The default colors is buttonColors(), whose background is secondaryVariant (light theme 0xFFF0F0F0, a near-white gray; dark 0xFF434343), not the theme color. Writing Button(onClick){Text("OK")} per M3 intuition gives a gray button; for a blue background with white text you must explicitly pass colors = ButtonDefaults.buttonColorsPrimary().  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Button.kt:181`)
- 🟡 There is no shape parameter, only cornerRadius(Dp); no elevation / tonalElevation / contentPadding. Shapes other than a rounded rectangle (e.g. a cut corner) are impossible; you can only change the radius. The padding parameter is called insideMargin.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Button.kt:76`)
- ⚪ Button's content slot injects no text style; a bare Text inside it gets LocalTextStyles.main (17sp) rather than textStyles.button; only TextButton explicitly applies textStyles.button. The two happen to both be 17sp, so no difference shows today, but relying on this is unsafe.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Button.kt:147`)
- ⚪ minWidth/minHeight go through defaultMinSize and can be overridden by an external modifier's size/widthIn (the opposite of Switch/Checkbox's requiredSize).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Button.kt:67`)

**Spec** min_size 58×40.dp (defaultMinSize, overridable by modifier) · corner 16.dp squircle (not RoundedCornerShape) · inside_margin horizontal 16.dp / vertical 13.dp

**State** Purely stateless. onClick is required and non-null; when enabled=false, clickable is turned off and it switches to disabledColor/disabledContentColor. contentColor is propagated via CompositionLocalProvider(LocalContentColor), so the inner Icon/Text follow the color automatically.

**vs Material3** Corresponds to androidx.compose.material3.Button. Differences: the default fill is gray, not primary; no elevation/ripple (press feedback comes from MiuixIndication's alpha overlay); shape→cornerRadius:Dp; contentPadding→insideMargin; none of the ElevatedButton/OutlinedButton/FilledTonalButton variants.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/ButtonDemo.kt:58`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ButtonDemo.kt#L58)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Button.kt:50`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Button.kt#L50)</sub>

## Checkbox  ·  basic component

A tri-state checkbox, circular (not square), fixed 26.dp size; the check mark is a hand-drawn animation clipped by arc length.

> A [Checkbox] component with Miuix style, supporting three states: On, Off, and Indeterminate.

```kotlin
import top.yukonga.miuix.kmp.basic.Checkbox

@Composable
fun Checkbox(
    state: ToggleableState,  // required
    onClick: (() -> Unit)?,  // required
    modifier: Modifier = Modifier,
    colors: CheckboxColors = CheckboxDefaults.checkboxColors(),
    enabled: Boolean = true,
)
```

- `state` — The current [ToggleableState] of the [Checkbox].
- `onClick` — The callback to be called when the [Checkbox] is clicked. The caller is   responsible for updating the state. If `null`, the [Checkbox] is not interactive.
- `modifier` — The modifier to be applied to the [Checkbox].
- `colors` — The [CheckboxColors] of the [Checkbox].
- `enabled` — Whether the [Checkbox] is enabled.

**CheckboxDefaults**


```kotlin
CheckboxDefaults.checkboxColors(
    checkedForegroundColor: Color = MiuixTheme.colorScheme.onPrimary,
    uncheckedForegroundColor: Color = MiuixTheme.colorScheme.secondary,
    disabledCheckedForegroundColor: Color = MiuixTheme.colorScheme.disabledOnPrimary,
    disabledUncheckedForegroundColor: Color = MiuixTheme.colorScheme.disabledOnPrimary,
    checkedBackgroundColor: Color = MiuixTheme.colorScheme.primary,
    uncheckedBackgroundColor: Color = MiuixTheme.colorScheme.secondary,
    disabledCheckedBackgroundColor: Color = MiuixTheme.colorScheme.disabledPrimary,
    disabledUncheckedBackgroundColor: Color = MiuixTheme.colorScheme.disabledSecondary,
)
```


**CheckboxColors** (data class) ⚠️ 8/8 constructor params are `private val` and **cannot be read from an instance**; these names are only usable as named arguments to the factory functions above.

**Traps**

- 🔴 The API is Checkbox(state: ToggleableState, onClick: (() -> Unit)?); there is no Boolean + onCheckedChange overload. Writing Checkbox(checked = x, onCheckedChange = { }) per M3 fails to compile. The correct form passes ToggleableState(bool) (or On/Off/Indeterminate), with onClick taking no argument and the caller computing the next state itself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Checkbox.kt:60`)
- 🔴 The size uses requiredSize(26.dp) placed after modifier, so it ignores externally passed constraints. Wrapping it in Modifier.size(40.dp) or sizeIn(min = 48.dp) changes nothing —— the touch hit area is always 26.dp (below the 48dp accessibility minimum target, with no compensating padding). To enlarge the hit area you must wrap it in your own clickable Box.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Checkbox.kt:173`)
- 🟡 Miuix's Checkbox is circular (CircleShape); the unchecked state is a filled gray circle (uncheckedBackgroundColor = secondary), not M3's hollow rounded square. Visually it belongs to the same family as Switch/RadioButton and matches no M3 design mockup.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Checkbox.kt:141`)
- 🟡 The sink feedback (SinkFeedback 0.85) is attached via pressable and controlled by the enabled parameter, not by onClick. A 'read-only' checkbox with onClick=null still shrinks a bit when pressed but its state doesn't change, which is easily mistaken for a broken tap. For it to be fully silent you also need enabled=false.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Checkbox.kt:174`)
- ⚪ The internal triStateToggleable is passed a null interactionSource, pressable uses its own private source, and the component exposes no interactionSource parameter. There is no way to observe its pressed/hovered state externally.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Checkbox.kt:160`)

**Spec** size 26×26.dp (requiredSize, not adjustable via modifier) · shape CircleShape (circular) · stroke check-mark stroke width = 9% of size (about 2.34.dp at 26.dp), round cap and join · anim background/foreground color tween(300), check-mark alpha enter 10ms / exit 150ms, the check tip overshoots (0.85 at 200ms → 0.803 at 300ms)

**State** Purely controlled. Both state and onClick are required (onClick can be explicitly null → degrades to a pure semantics node, non-interactive). The Indeterminate state is not a separate path; it lerps the check's three points toward the center, collapsing them into a horizontal line. The haptic type is decided by the current state at press time.

**vs Material3** Corresponds to material3.TriStateCheckbox (not Checkbox). Differences: no Boolean convenience overload, no interactionSource parameter, circular rather than rounded square, size hardcoded to 26.dp and unchangeable, no 48dp touch-target compensation.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/CheckboxDemo.kt:46`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/CheckboxDemo.kt#L46) · [`example/shared/src/commonMain/kotlin/component/CheckboxSection.kt:60`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/CheckboxSection.kt#L60)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Checkbox.kt:60`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Checkbox.kt#L60)</sub>

## RowScope.DropdownArrowEndAction  ·  basic component

The up-down double-arrow indicator at the end of a dropdown/Spinner trigger row. It is an extension function on RowScope, meant for the row end of Preference-type components.

```kotlin
import top.yukonga.miuix.kmp.basic.DropdownArrowEndAction

@Composable
fun RowScope.DropdownArrowEndAction(
    actionColor: Color,  // required
    modifier: Modifier = Modifier,
)
```

**Traps**

- 🟡 It is an extension function on RowScope (internally it uses align(Alignment.CenterVertically)) and can only be called within a Row scope. Putting it in a Column, a Box, or a top-level composable fails to compile, reporting an "unresolved reference" rather than a scope error, which is easily mistaken for a missing import.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:45`)
- ⚪ actionColor is required, has no default, and does not automatically take the theme color. The library's callers generally pass a color chosen by enabled state, so when using it yourself remember to handle the disabled state.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:46`)
- ⚪ It draws MiuixIcons.Basic.ArrowUpDown (an up-down double arrow, meaning "switchable"), not the ArrowRight chevron used by cascading/submenu rows. Their size constants happen to both be 10×16.dp (ArrowSize and ChevronSize), so do not conflate their semantics just because the sizes match.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:54`)

**Spec** size 10×16.dp (DropdownDefaults.ArrowSize, hardcoded inside the component) · alignment internally fixed align(Alignment.CenterVertically)

**State** Stateless, purely decorative. contentDescription is passed as null (invisible to screen readers), so the semantics must be carried by the row it sits in. It does not rotate with the expanded state.

**vs Material3** Closest to ExposedDropdownMenuDefaults.TrailingIcon -- but M3's rotates 180° with expanded, while Miuix's is a static up-down double arrow whose meaning is "this row can switch value" rather than "the menu is expanded".

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:45`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt#L45)</sub>

## DropdownImpl  ·  basic component

A single-row rendering primitive inside dropdowns/menus (icon + title + summary + a trailing checkmark or arrow). Use it when hand-writing menu items inside ListPopupColumn, to keep the visuals consistent with the library's built-in menus.

> The implementation of the dropdown.

```kotlin
import top.yukonga.miuix.kmp.basic.DropdownImpl

@Composable
fun DropdownImpl(
    item: DropdownItem,  // required
    optionSize: Int,  // required
    isSelected: Boolean,  // required
    index: Int,  // required
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    enabled: Boolean = item.enabled,
    dialogMode: Boolean = false,
    hasSubmenu: Boolean = false,
    isFirst: Boolean = index == 0,
    isLast: Boolean = index == optionSize - 1,
    onSelectedIndexChange: (Int) -> Unit,  // required
)
```

- `item` — The item of the current option.
- `optionSize` — The size of the options.
- `isSelected` — Whether the option is selected.
- `index` — The index of the current option in the options.
- `dropdownColors` — The [DropdownColors] used to style the option row.
- `enabled` — Whether the option is clickable. Disabled rows ignore clicks and use the disabled text color.
- `dialogMode` — Whether the item is shown in dialog mode.
- `hasSubmenu` — When true, this row acts as a submenu trigger: a trailing chevron is shown   instead of the selection check, and the row's accessibility role becomes [Role.Button].
- `isFirst` — Whether this row is the first row of the entire popup. Controls the larger top   padding in popup mode. Defaults to `index == 0`; multi-entry callers should pass the   popup-global flag so only the actual first row gets extra padding.
- `isLast` — Whether this row is the last row of the entire popup. Controls the larger bottom   padding in popup mode. Defaults to `index == optionSize - 1`; multi-entry callers should pass   the popup-global flag.
- `onSelectedIndexChange` — The callback invoked with [index] when the option is selected.

**Traps**

- 🟡 There are two public overloads: the text: String version (simple) and the item: DropdownItem version (full). Only the item version has the three parameters hasSubmenu / isFirst / isLast, and the docs only include the text version, so when you need a submenu arrow or first/last padding across multiple groups you must use the item version.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:81`)
- 🔴 dialogMode: Boolean = false sits between enabled and onSelectedIndexChange, yet the property tables throughout the docs all omit it. Passing arguments positionally per the docs mis-slots the argument meant for onSelectedIndexChange into dialogMode and fails to compile. Always use named arguments.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:227`)
- 🟡 isFirst / isLast default to deriving from index == 0 and index == optionSize - 1, which is "first/last within this group". When assembling multiple DropdownEntry groups into one popup you must explicitly pass the popup-global first/last flags, otherwise the first and last rows of every group get the enlarged 20dp padding, visually adding several extra gaps.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:90`)
- 🟡 dialogMode = true is not just a background swap: the first/last rows no longer have the enlarged 20dp padding (all 12dp), horizontal padding changes from 20dp to 28dp, and it adds minHeight 56dp / minWidth 200dp / fillMaxWidth, and internally removes the 216dp text-width cap. Mistakenly passing true inside a popup deforms the whole column's layout.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:133`)
- ⚪ When hasSubmenu = true the trailing checkmark is replaced by a chevron and the accessibility role changes from RadioButton to Button (Dropdown.kt:149, :186-214). Here isSelected still changes the text color and chevron color (:120-124, :190-194), and the row background also uses selectedContainerColor (:107-111, which under the default dropdownColors() equals containerColor so is invisible, and under dialogDropdownColors() is tertiaryContainer), but you never see a checkmark. Do not use a hasSubmenu row to express "selected".  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:149`)
- ⚪ enabled defaults to item.enabled, but passing it explicitly fully overrides it (no AND is performed). The AND of DropdownEntry.enabled and item.enabled is done by the caller (the cascading layer) itself, so when hand-writing you must compute it yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:87`)
- 🟡 DropdownItem has a public secondary constructor constructor(icon, title, summary) not documented anywhere, kept for compatibility with the deprecated SpinnerEntry. All three parameters have defaults, so DropdownItem() also compiles and yields text = empty string (when title is null it goes through title.orEmpty()) -- an empty text makes things like DropdownPreference not show a value because of text.isNullOrEmpty(). This constructor also gives you no access to enabled / selected / onClick / children, so normally always use the primary constructor and write text = explicitly.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:351`)

**Spec** check_icon CheckIconSize 20.dp, start padding CheckIconStartPadding 12.dp · chevron ChevronSize 10×16.dp (replaces the checkmark when hasSubmenu) · icon_cell IconMinSize 26.dp, spacing from text IconEndPadding 12.dp · text_width_cap MaxItemTextWidth 216.dp (popup mode only, removed under dialogMode) · horizontal_padding popup mode InsideHorizontalPadding 20.dp; dialogMode DialogHorizontalPadding 28.dp · vertical_padding first/last rows FirstLastVerticalPadding 20.dp, middle rows MiddleVerticalPadding 12.dp; all 12.dp under dialogMode · dialog_mode_min MinHeight 56.dp / MinWidth 200.dp (dialogMode only)

**State** A purely controlled display row with no internal state. The selected state is passed in via isSelected, and a tap passes back index to onSelectedIndexChange (not the item). Colors are all decided by DropdownColors, with DropdownDefaults.dropdownColors() for popups and dialogDropdownColors() for dialogs (the latter has a transparent containerColor and uses tertiaryContainer for the selected state).

**vs Material3** Corresponds to androidx.compose.material3.DropdownMenuItem. Differences: M3 uses three composable slots text / leadingIcon / trailingIcon + onClick, fully free; Miuix takes the DropdownItem data class, the trailing part can only be a "checkmark" or a "chevron", with no slot to swap; the selected semantics are built into Miuix (M3's DropdownMenuItem has no selected concept); the callback passes index rather than a no-arg onClick.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayListPopupDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayListPopupDemo.kt#L53) · [`docs/demo/src/commonMain/kotlin/WindowListPopupDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowListPopupDemo.kt#L53)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:81`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt#L81)</sub>

## DropdownImpl  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

```kotlin
import top.yukonga.miuix.kmp.basic.DropdownImpl

@Composable
fun DropdownImpl(
    text: String,  // required
    optionSize: Int,  // required
    isSelected: Boolean,  // required
    index: Int,  // required
    dropdownColors: DropdownColors = DropdownDefaults.dropdownColors(),
    enabled: Boolean = true,
    dialogMode: Boolean = false,
    onSelectedIndexChange: (Int) -> Unit,  // required
)
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/OverlayListPopupDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayListPopupDemo.kt#L53) · [`docs/demo/src/commonMain/kotlin/WindowListPopupDemo.kt:53`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/WindowListPopupDemo.kt#L53)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:220`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt#L220)</sub>

## IconButton  ·  basic component

An icon-only button, transparent background by default, 40×40, fully pill-shaped corners. Commonly used in TopAppBar / toolbars.

> A [IconButton] component with Miuix style.
> 
> Icon buttons help people take supplementary actions with a single tap. They’re used when a
> compact button is required, such as in a toolbar or image list.

```kotlin
import top.yukonga.miuix.kmp.basic.IconButton

@Composable
fun IconButton(
    onClick: () -> Unit,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    holdDownState: Boolean = false,
    backgroundColor: Color = Color.Unspecified,
    cornerRadius: Dp = IconButtonDefaults.CornerRadius,
    minHeight: Dp = IconButtonDefaults.MinHeight,
    minWidth: Dp = IconButtonDefaults.MinWidth,
    content: @Composable () -> Unit,  // required
)
```

- `onClick` — The callback when the [IconButton] is clicked.
- `modifier` — The modifier to be applied to the [IconButton]
- `enabled` — Whether the [IconButton] is enabled.
- `holdDownState` — Used to determine whether it is in the pressed state.
- `backgroundColor` — The background color of of the [IconButton].
- `cornerRadius` — The corner radius of of the [IconButton].
- `minHeight` — The minimum height of of the [IconButton].
- `minWidth` — The minimum width of the [IconButton].
- `content` — The content of this icon button, typically an [Icon].

**IconButtonDefaults**

- `MinWidth = 40.dp`
- `MinHeight = 40.dp`
- `CornerRadius = 40.dp`

**Traps**

- 🔴 enabled=false merely swaps the whole clickable for an empty Modifier and does no graying-out. A disabled-state icon looks identical to the enabled state, so users can't tell it isn't clickable. To show disabled state you must dim the Icon tint in content yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/IconButton.kt:63`)
- 🟡 There is no IconButtonColors class, only a bare backgroundColor: Color, defaulting to Color.Unspecified (transparent). There is also no contentColor —— the icon color is entirely decided by the external LocalContentColor; IconButton injects none.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/IconButton.kt:45`)
- ⚪ It exposes no interactionSource / indication parameter and builds its own MutableInteractionSource internally. To observe the pressed state externally you can only drive it in reverse via holdDownState (which mirrors the boolean into a HoldDownInteraction).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/IconButton.kt:51`)

**Spec** min_size 40×40.dp (defaultMinSize, overridable) · corner 40.dp squircle —— equals MinHeight, i.e. fully pill/circular by default

**State** Purely stateless. onClick is required. When holdDownState=true it stays in the pressed visual (used for 'menu is open, keep the anchor highlighted').

**vs Material3** Corresponds to material3.IconButton. Differences: M3 has IconButtonColors (including disabledContentColor) that automatically grays the disabled-state icon, which Miuix does not do at all; M3 defaults to a 48dp touch target, Miuix is 40dp with no minimumInteractiveComponentSize compensation.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/FloatingToolbarDemo.kt:61`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/FloatingToolbarDemo.kt#L61) · [`docs/demo/src/commonMain/kotlin/IconButtonDemo.kt:48`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/IconButtonDemo.kt#L48) · [`docs/demo/src/commonMain/kotlin/OverlayBottomSheetDemo.kt:62`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayBottomSheetDemo.kt#L62) · [`docs/demo/src/commonMain/kotlin/TooltipDemo.kt:54`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TooltipDemo.kt#L54)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/IconButton.kt:40`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/IconButton.kt#L40)</sub>

## NumberPicker  ·  basic component

An inertial wheel number picker (the kind in the HyperOS time picker). It simulates depth with scaling + fade, with no 3D cylindrical perspective.

> A [NumberPicker] component with Miuix style.
> 
> A vertical scroll picker that displays a range of numbers with the selected value centered.
> Items fade out and scale down as they move away from the center.

```kotlin
import top.yukonga.miuix.kmp.basic.NumberPicker

@Composable
fun NumberPicker(
    value: Int,  // required
    onValueChange: (Int) -> Unit,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    range: IntRange = 0..10,
    label: (Int) -> String = { it.toString() },
    visibleItemCount: Int = 5,
    wrapAround: Boolean = false,
    colors: NumberPickerColors = NumberPickerDefaults.colors(),
    textStyle: TextStyle = MiuixTheme.textStyles.title1,
    itemHeight: Dp = NumberPickerDefaults.ItemHeight,
)
```

- `value` — The current selected value. If outside [range], it will be coerced into the range.
- `onValueChange` — The callback invoked when the selected value changes.
- `modifier` — The modifier to be applied to the [NumberPicker].
- `enabled` — Whether the [NumberPicker] is enabled for user interaction.
- `range` — The range of selectable values.
- `label` — A function that converts a value to its display string.
- `visibleItemCount` — The number of visible items. Must be odd and at least 3.
- `wrapAround` — Whether the picker wraps around from the last item to the first (infinite scrolling).
- `colors` — The [NumberPickerColors] for this [NumberPicker].
- `textStyle` — The [TextStyle] for the picker items.
- `itemHeight` — The height of each item in the picker.

**NumberPickerDefaults**


```kotlin
NumberPickerDefaults.colors(
    selectedTextColor: Color = MiuixTheme.colorScheme.onSurface,
    unselectedTextColor: Color = MiuixTheme.colorScheme.onSurfaceSecondary,
    disabledSelectedTextColor: Color = MiuixTheme.colorScheme.disabledOnSecondary,
    disabledUnselectedTextColor: Color = MiuixTheme.colorScheme.disabledOnSecondary,
)
```

- `ItemHeight = 45.dp`

**NumberPickerColors** (data class) ⚠️ 4/4 constructor params are `private val` and **cannot be read from an instance**; these names are only usable as named arguments to the factory functions above.

**Traps**

- 🔴 Two require checks throw during composition: visibleItemCount must be odd and >= 3, and range must not be empty. Writing visibleItemCount = 4 crashes outright, not silently rounded.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NumberPicker.kt:82`)
- 🔴 It hardcodes fillMaxWidth() internally, placed after modifier. When several NumberPickers are placed side by side in a Row (the most common hour/minute/second usage), each grabs the full width and causes overflow —— you must pass Modifier.weight(1f) to each.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NumberPicker.kt:161`)
- 🔴 Fully controlled: after release-and-snap it calls onValueChange(newValue) and immediately snapTo(0f) on the internal offset. If the caller doesn't write the new value back to value (or writes it back a frame late), the view instantly snaps back to the old value. You must never ignore onValueChange.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NumberPicker.kt:217`)
- 🟡 The height is hardcoded to itemHeight × visibleItemCount (default 45 × 5 = 225.dp), and a height given by an external modifier is overridden. To change the height you can only adjust itemHeight or visibleItemCount.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NumberPicker.kt:162`)
- ⚪ All item rendering is wrapped in if (itemHeightPx > 0), and itemHeightPx only gets a value after onSizeChanged returns —— the wheel is blank on the first composition frame. When it appears in a dialog/BottomSheet you may see a one-frame blank.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NumberPicker.kt:231`)
- ⚪ itemHeightPx = size.height / visibleItemCount is integer division, so at densities where 45.dp converts to a non-divisible pixel count it accumulates a few pixels of error, showing as a slight deviation between the wheel item spacing and itemHeight.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NumberPicker.kt:168`)

**Spec** item_height 45.dp (NumberPickerDefaults.ItemHeight) · total_height itemHeight × visibleItemCount (default 225.dp, not changeable via modifier) · text default textStyles.title1 (32.sp); if the passed style's fontWeight is null it auto-fills SemiBold · falloff alpha = (1-d)(1-0.5d), scale = 1-0.2d, color linearly interpolated between selected↔unselected (d is the normalized distance from center)

**State** Purely controlled. value must be updated externally in response to onValueChange. Drag offset and inertial offset are two separate things (dragOffset + Animatable), and after release it runs a four-step coroutine 'transfer → decay → snap → commit → reset'. It fires a haptic each time it crosses an item, and an isUserScrolling gate ensures programmatic value changes don't fire haptics.

**vs Material3** No counterpart (Material3 has no wheel picker). The closest is M3's internal TimePicker implementation, but it's not exposed as a public component.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/NumberPickerDemo.kt:43`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/NumberPickerDemo.kt#L43) · [`example/shared/src/commonMain/kotlin/component/NumberPickerSection.kt:43`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/NumberPickerSection.kt#L43)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NumberPicker.kt:69`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/NumberPicker.kt#L69)</sub>

## RadioButton  ·  basic component

A radio button, but it draws a 'check mark' rather than a ring —— when unselected there is nothing on screen. It reproduces the look of HyperOS single-choice lists.

> A [RadioButton] component with Miuix style.
> 
> Displays a checkmark indicator when selected, matching the miuix-classic SingleChoicePreference
> visual style. When unselected, no indicator is shown.

```kotlin
import top.yukonga.miuix.kmp.basic.RadioButton

@Composable
fun RadioButton(
    selected: Boolean,  // required
    onClick: (() -> Unit)?,  // required
    modifier: Modifier = Modifier,
    colors: RadioButtonColors = RadioButtonDefaults.radioButtonColors(),
    enabled: Boolean = true,
)
```

- `selected` — Whether the [RadioButton] is currently selected.
- `onClick` — The callback to be called when the [RadioButton] is clicked. The caller is   responsible for updating the state. If `null`, the [RadioButton] is not interactive.
- `modifier` — The modifier to be applied to the [RadioButton].
- `colors` — The [RadioButtonColors] of the [RadioButton].
- `enabled` — Whether the [RadioButton] is enabled.

**RadioButtonDefaults**


```kotlin
RadioButtonDefaults.radioButtonColors(
    selectedColor: Color = MiuixTheme.colorScheme.primary,
    disabledSelectedColor: Color = MiuixTheme.colorScheme.disabledPrimary,
)
```


**RadioButtonColors** (data class) ⚠️ 2/2 constructor params are `private val` and **cannot be read from an instance**; these names are only usable as named arguments to the factory functions above.

**Traps**

- 🔴 When unselected it is completely invisible: alpha=0 and trimEnd=0, the draw function returns at the very start, and the 26.dp area is entirely empty. Placing it at the right end of a list item (a check on the selected item, blank for the rest) is correct, but used as a standalone control (e.g. a row of side-by-side options) users can't tell where to tap at all. For that scenario use Checkbox or draw your own ring.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/RadioButton.kt:189`)
- 🔴 The size is requiredSize(26.dp) placed after modifier; it can't be enlarged externally nor can the touch hit area be expanded, same as Checkbox.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/RadioButton.kt:121`)
- 🟡 RadioButtonColors has only two fields, selectedColor / disabledSelectedColor —— because the unselected state draws nothing at all, there is no 'unselected color' concept to configure.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/RadioButton.kt:226`)
- 🟡 onClick is nullable but required (same as Checkbox). There is no RadioGroup / mutual-exclusion container; the single-choice semantics (who is selected, whom to clear on a tap) are entirely maintained by the caller; the internal selectable also explicitly disables indication.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/RadioButton.kt:61`)
- ⚪ Its check mark and Checkbox's come from two different design mockups (RadioButton is a 56 viewport, 12.5% stroke; Checkbox is a 23 viewport, 9% stroke), so after normalization the shapes differ. When the two appear side by side, the check-mark thickness and corner angle show a visible difference.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/RadioButton.kt:131`)

**Spec** size 26×26.dp (requiredSize, not adjustable) · unselected not drawn at all (no ring, no border) · stroke 7/56 ≈ 12.5% width (about 3.25.dp at 26.dp) · anim alpha enter 10ms / exit 150ms, check-mark trimEnd tween(300, FastOutSlowIn)

**State** Purely controlled. selected + onClick are required; when onClick=null it degrades to a pure semantics node. The press sink feedback is the same as Checkbox (SinkFeedback 0.85, pressable delay=null), controlled by enabled rather than onClick.

**vs Material3** Corresponds to material3.RadioButton. The differences are huge: M3 draws a hollow ring when unselected, Miuix draws nothing; M3 has unselectedColor/disabledUnselectedColor, Miuix does not; the size is not adjustable; no 48dp touch-target compensation.

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/RadioButton.kt:59`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/RadioButton.kt#L59)</sub>

## RangeSlider  ·  basic component

A two-thumb range slider. It has cross-over takeover logic (once the two values coincide, pushing further automatically switches which side is being dragged).

> A [RangeSlider] component with Miuix style.
> 
> Range Sliders expand upon [Slider] using the same concepts but allow the user to select 2 values.
> The two values are still bounded by the value range but they also cannot cross each other.

```kotlin
import top.yukonga.miuix.kmp.basic.RangeSlider

@Composable
fun RangeSlider(
    value: ClosedFloatingPointRange<Float>,  // required
    onValueChange: (ClosedFloatingPointRange<Float>) -> Unit,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    valueRange: ClosedFloatingPointRange<Float> = 0f..1f,
    steps: Int = 0,
    onValueChangeFinished: (() -> Unit)? = null,
    height: Dp = SliderDefaults.MinHeight,
    colors: SliderColors = SliderDefaults.sliderColors(),
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
    showKeyPoints: Boolean = false,
    keyPoints: List<Float>? = null,
    magnetThreshold: Float = 0.02f,
)
```

- `value` — Current values of the RangeSlider. If either value is outside of [valueRange] provided, it will be coerced to this range.
- `onValueChange` — Lambda in which values should be updated.
- `modifier` — The modifier to be applied to the [RangeSlider].
- `enabled` — Whether the [RangeSlider] is enabled.
- `valueRange` — Range of values that Range Slider values can take. Passed [value] will be coerced to this range.
- `steps` — If positive, specifies the amount of discrete allowable values between the endpoints of [valueRange].
- `onValueChangeFinished` — Lambda to be invoked when value change has ended.
- `height` — The height of the [RangeSlider].
- `colors` — The [SliderColors] of the [RangeSlider].
- `hapticEffect` — The haptic effect of the [RangeSlider].
- `showKeyPoints` — Whether to show the key points (step indicators) on the slider. Only works when [keyPoints] is not null.
- `keyPoints` — Custom key point values to display on the slider. If null, uses step positions from [steps] parameter.   Values should be within [valueRange].
- `magnetThreshold` — The magnetic snap threshold as a fraction (0.0 to 1.0). When the slider value is within this   distance from a key point, it will snap to that point. Default is 0.02 (2%). Only applies when [keyPoints] is set.

**Traps**

- 🔴 Accessibility is incomplete: semantics has only a stateDescription string, no progressBarRangeInfo and no setProgress (both of which Slider and VerticalSlider have). A screen reader can read out the current range but cannot adjust it at all.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:793`)
- 🟡 During a drag it ignores the externally passed value (it only syncs its local mirror when !isDragging). So a controlled pattern like 'clamp/quantize the value in onValueChange and write it back' doesn't take effect during the drag; only after release is it overwritten by the external value.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:538`)
- 🟡 There is no reverseDirection parameter (direction only auto-mirrors with RTL), and no 'minimum gap' parameter —— the two thumbs can fully coincide, and pushing further after coinciding triggers cross-over takeover, switching the drag target.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:498`)
- ⚪ value is of type ClosedFloatingPointRange<Float>, written as a..b; it is likewise subject to require(valueRange.start < endInclusive), so a degenerate range crashes during composition. The key-point radius here uses SliderDefaults.KeyPointRadius (3.855.dp), inconsistent with Slider's barHeight/7.5.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:991`)

**Spec** track 28.dp tall (height parameter), the span between the two thumbs is the foreground color · thumb two of them, radius = track radius × 0.72, each with independent hover/drag scaling · key_point radius SliderDefaults.KeyPointRadius = 3.855.dp

**State** Controlled + a local mirror during drag. onValueChange returns a new ClosedFloatingPointRange. Haptics are managed per side by RangeSliderHapticState, and on cross-over takeover the key-point state is handed over to the other side to avoid duplicate haptics.

**vs Material3** Corresponds to material3.RangeSlider. Differences: no startThumb/endThumb/track slots; no setProgress accessibility action; adds keyPoints snapping and hapticEffect.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/SliderDemo.kt:52`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SliderDemo.kt#L52)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:498`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt#L498)</sub>

## Slider  ·  basic component

A horizontal slider. A thick pill track (28.dp) with an embedded white-dot thumb, supporting steps hard-stepping or keyPoints magnetic snapping, with three levels of haptic feedback.

> A [Slider] component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.Slider

@Composable
fun Slider(
    value: Float,  // required
    onValueChange: (Float) -> Unit,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    valueRange: ClosedFloatingPointRange<Float> = 0f..1f,
    steps: Int = 0,
    onValueChangeFinished: (() -> Unit)? = null,
    reverseDirection: Boolean = false,
    height: Dp = SliderDefaults.MinHeight,
    colors: SliderColors = SliderDefaults.sliderColors(),
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
    showKeyPoints: Boolean = false,
    keyPoints: List<Float>? = null,
    magnetThreshold: Float = 0.02f,
)
```

- `value` — The current value of the [Slider]. If outside of [valueRange] provided, value will be coerced to this range.
- `onValueChange` — The callback to be called when the value changes.
- `modifier` — The modifier to be applied to the [Slider].
- `enabled` — Whether the [Slider] is enabled.
- `valueRange` — Range of values that this slider can take. The passed [value] will be coerced to this range.
- `steps` — If positive, specifies the amount of discrete allowable values between the endpoints of [valueRange].   For example, a range from 0 to 10 with 4 [steps] allows 4 values evenly distributed between 0 and 10 (i.e., 2, 4, 6, 8).   If [steps] is 0, the slider will behave continuously and allow any value from the range. Must not be negative.
- `onValueChangeFinished` — Called when value change has ended. This should not be used to update the slider value   (use [onValueChange] instead), but rather to know when the user has completed selecting a new value by ending a drag or a click.
- `reverseDirection` — Controls the direction of this slider. When false (default), slider increases from left to right.   When true, slider increases from right to left (useful for RTL layouts or custom direction requirements).
- `height` — The height of the [Slider].
- `colors` — The [SliderColors] of the [Slider].
- `hapticEffect` — The haptic effect of the [Slider].
- `showKeyPoints` — Whether to show the key points (step indicators) on the slider. Only works when [keyPoints] is not null.
- `keyPoints` — Custom key point values to display on the slider. If null, uses step positions from [steps] parameter.   Values should be within [valueRange]. For example, for a range of 0f..100f, you might specify listOf(0f, 25f, 50f, 75f, 100f).
- `magnetThreshold` — The magnetic snap threshold as a fraction (0.0 to 1.0). When the slider value is within this   distance from a key point, it will snap to that point. Default is 0.02 (2%). Only applies when [keyPoints] is set.

**SliderDefaults**


```kotlin
SliderDefaults.sliderColors(
    foregroundColor: Color = MiuixTheme.colorScheme.primary,
    disabledForegroundColor: Color = MiuixTheme.colorScheme.disabledPrimarySlider,
    backgroundColor: Color = MiuixTheme.colorScheme.sliderBackground,
    disabledBackgroundColor: Color = MiuixTheme.colorScheme.disabledSecondary,
    thumbColor: Color = MiuixTheme.colorScheme.onPrimary,
    disabledThumbColor: Color = MiuixTheme.colorScheme.disabledOnPrimary,
    keyPointColor: Color = MiuixTheme.colorScheme.sliderKeyPoint,
    keyPointForegroundColor: Color = MiuixTheme.colorScheme.sliderKeyPointForeground,
)
```

- `MinHeight = 28.dp`
- `KeyPointRadius = 3.855.dp`
- `DefaultHapticEffect = SliderHapticEffect.Edge`

**SliderColors** (data class) ⚠️ 8/8 constructor params are `private val` and **cannot be read from an instance**; these names are only usable as named arguments to the factory functions above.

**Traps**

- 🔴 showKeyPoints's KDoc says 'Only works when keyPoints is not null', which is the opposite of the implementation and wrong both ways: (1) passing keyPoints without showKeyPoints=true, the key points aren't drawn (but snapping still works); (2) without keyPoints, with only steps>0 and showKeyPoints=true, the step points are drawn normally. To display key points you must explicitly set showKeyPoints = true.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:1328`)
- 🔴 The accessibility setProgress action is attached to semantics, outside the enabled check. When enabled=false all gesture Modifiers are removed, but screen-reader software can still call setProgress to change the value and trigger onValueChange —— a disabled slider is writable by accessibility services.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:245`)
- 🟡 onDragStarted immediately computes the value from the touch position and calls back, meaning a tap anywhere on the track jumps the thumb straight there (unlike M3, where you must drag the thumb itself). There is no toggle to disable this behavior.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:220`)
- 🟡 Two require checks throw during composition rather than silently falling back: steps must be >= 0, and valueRange.start must be strictly less than endInclusive. Using 0f..0f or a reversed range crashes outright.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:104`)
- ⚪ isPressed (collectIsPressedAsState) is always false: nothing in the whole file emits a PressInteraction to interactionSource (interactionSource is only wired to hoverable and indication(_, null); draggable doesn't take it). So the thumb enlargement is driven only by dragging and mouse hover; a touchscreen 'press and hold' doesn't enlarge it. Likewise .indication(interactionSource, null) is a no-op.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:119`)
- ⚪ steps > 0 and keyPoints are two mutually exclusive branches, with steps taking priority: whenever steps>0, the magnetThreshold and keyPoints snapping logic is never reached. The key-point radius in Slider is barHeight/7.5 (3.733.dp at 28.dp), while RangeSlider uses SliderDefaults.KeyPointRadius = 3.855.dp, a 3% difference when placed side by side on the same page.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:1264`)

**Spec** track 28.dp tall (SliderDefaults.MinHeight), clipped into a pill, width fillMaxWidth · thumb radius = track radius × 0.72 (diameter about 20.2.dp at 28.dp), drawn inside the track; ×1.127 on drag/hover · press during drag the whole track overlays a 4.4% black layer (tween 150) · key_point radius barHeight/7.5

**State** Purely controlled. onValueChange fires every frame, onValueChangeFinished fires once on release. value is coerceIn'd to valueRange, and the displayed value goes through animateFloatAsState (spring(0.9,1755), stiffer, during drag; spring(0.96,322), softer, after release). Three haptic levels: None / Edge (default, only 0% and 100%) / Step.

**vs Material3** Corresponds to material3.Slider. Differences: no thumb/track slots; the appearance is 'a small dot embedded in a thick track' rather than 'a thin track + a large thumb outside the track'; adds keyPoints snapping, reverseDirection, hapticEffect; the touch target is only 28.dp.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/SliderDemo.kt:43`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SliderDemo.kt#L43)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:88`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt#L88)</sub>

## SpinnerItemImpl  ·  basic component

A deprecated (DeprecationLevel.WARNING) Spinner single-row rendering function, now just a thin alias for DropdownImpl(item = ...). New code should always use DropdownImpl directly.

```kotlin
import top.yukonga.miuix.kmp.basic.SpinnerItemImpl

@Composable
fun SpinnerItemImpl(
    entry: DropdownItem,  // required
    entryCount: Int,  // required
    isSelected: Boolean,  // required
    index: Int,  // required
    spinnerColors: DropdownColors,  // required
    dialogMode: Boolean = false,
    onSelectedIndexChange: (Int) -> Unit,  // required
)
```

**Traps**

- 🟡 The entire Spinner naming family is deprecated and unified into Dropdown: SpinnerItemImpl → DropdownImpl, SpinnerEntry → DropdownItem (typealias), SpinnerColors → DropdownColors (typealias), SpinnerDefaults → DropdownDefaults. When you see Spinner* in old code, just migrate per replaceWith; the runtime behavior is identical.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:254`)
- 🟡 The parameter names differ from DropdownImpl (entry / entryCount / spinnerColors correspond to item / optionSize / dropdownColors), so migration cannot just rename the function; and spinnerColors has no default and must be passed explicitly, whereas DropdownImpl's dropdownColors has a default.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:269`)
- ⚪ It hardcodes enabled to entry.enabled and forwards it, with no separate enabled parameter -- making a row "data available but temporarily untappable" is impossible in this function, so you must switch to DropdownImpl.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:279`)
- ⚪ When forwarding it does not pass hasSubmenu / isFirst / isLast and always takes the defaults (isFirst = index == 0, isLast = index == entryCount - 1). Using it in a multi-group scenario means you cannot get the popup-global first/last padding control.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:273`)

**Spec** same_as Exactly the same as DropdownImpl (it only forwards): checkmark 20.dp, popup horizontal padding 20.dp, first/last 20.dp / middle 12.dp vertical padding, under dialogMode horizontal 28.dp, vertical all 12.dp, minHeight 56.dp

**State** Stateless, pure forwarding. onSelectedIndexChange passes back index.

**vs Material3** No equivalent (M3 has no Spinner concept; semantically it is still DropdownMenuItem).

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt:264`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Dropdown.kt#L264)</sub>

## Switch  ·  basic component

A switch. A 49×28 pill track + 20.dp thumb, with half-sensitivity dragging and hysteresis haptics; it is the most finely tuned component at this layer for feel.

> A [Switch] component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.Switch

@Composable
fun Switch(
    checked: Boolean,  // required
    onCheckedChange: ((Boolean) -> Unit)?,  // required
    modifier: Modifier = Modifier,
    colors: SwitchColors = SwitchDefaults.switchColors(),
    enabled: Boolean = true,
)
```

- `checked` — The checked state of the [Switch].
- `onCheckedChange` — The callback to be called when the state of the [Switch] changes.
- `modifier` — The modifier to be applied to the [Switch].
- `colors` — The [SwitchColors] of the [Switch].
- `enabled` — Whether the [Switch] is enabled.

**SwitchDefaults**


```kotlin
SwitchDefaults.switchColors(
    checkedThumbColor: Color = if (isDynamicColor) LocalColors.current.onPrimary else MiuixTheme.colorScheme.onPrimary,
    uncheckedThumbColor: Color = if (isDynamicColor) LocalColors.current.onSurface.copy(0.38f) else MiuixTheme.colorScheme.onSecondary,
    disabledCheckedThumbColor: Color = if (isDynamicColor) LocalColors.current.surface else MiuixTheme.colorScheme.disabledOnPrimary,
    disabledUncheckedThumbColor: Color = MiuixTheme.colorScheme.disabledOnSecondary,
    checkedTrackColor: Color = MiuixTheme.colorScheme.primary,
    uncheckedTrackColor: Color = MiuixTheme.colorScheme.secondary,
    disabledCheckedTrackColor: Color = MiuixTheme.colorScheme.disabledPrimary,
    disabledUncheckedTrackColor: Color = MiuixTheme.colorScheme.disabledSecondary,
)
```


**SwitchColors** (data class) ⚠️ 8/8 constructor params are `private val` and **cannot be read from an instance**; these names are only usable as named arguments to the factory functions above.

**Traps**

- 🔴 onCheckedChange is nullable but has no default, so it is required. For a read-only switch you must explicitly write onCheckedChange = null (the component then degrades to a pure semantics node, recognizable by screen readers but non-interactive); simply omitting the parameter fails to compile.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Switch.kt:68`)
- 🔴 .size(49.dp, 28.dp) placed after modifier silently overrides the caller's size. Passing Modifier.size(80.dp, 40.dp) doesn't give a large switch, only a 49×28 switch centered in an empty 80×40 box (there's also a wrapContentSize(Center) before it). The switch size is entirely non-configurable in the current implementation.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Switch.kt:143`)
- 🟡 The drag gesture is attached only to the 20.dp thumb, not the track. Pressing and dragging horizontally on an empty part of the track won't move the thumb (it's only recognized as a tap toggle or swallowed by the parent's scroll).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Switch.kt:168`)
- 🟡 The parameter order is (checked, onCheckedChange, modifier, colors, enabled) —— colors comes before enabled, deviating from the template order mandated by AGENTS.md:107-127 (boolean flags should come before visual parameters). Checkbox / RadioButton / TextField / BasicComponent deviate likewise; those that follow the template (enabled before colors) are Button / Slider / NumberPicker. So passing the fourth argument positionally fails to compile due to a type mismatch; always use named arguments.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Switch.kt:70`)
- ⚪ Under Monet dynamic color (colorSchemeMode being MonetSystem/MonetLight/MonetDark), the off-state thumb color is special-cased to onSurface.copy(0.38f) rather than onSecondary. If you copy the non-dynamic-color branch when customizing SwitchColors, the thumb and track will clash in color under dynamic color.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Switch.kt:232`)

**Spec** size 49×28.dp (fixed, placed after modifier, not adjustable via modifier) · shape CircleShape pill · thumb 20.dp circle; off-state offset 4.dp, on-state 25.dp, travel 21.dp; scales to 1.127 on press/drag/hover · anim thumb displacement spring(0.7, 987) and scale spring(0.6, 987) correspond to Folme response 0.2s; track color change spring(0.99, 438.6) corresponds to 0.3s

**State** Purely controlled. Drag displacement is added directly into the spring target value (so the drag itself is also damped); only when released past the halfway point (>10.5) does it invoke(!checked), and it only settles once the external checked is updated. The haptics are a hysteresis state machine: reset at the midpoint, fire at the endpoints, and on release, if it hasn't fired along the way, fire once more.

**vs Material3** Corresponds to material3.Switch. Differences: no thumbContent slot, no track border, doesn't use AnchoredDraggable but a hand-written draggable + half-sensitivity; SwitchColors has only 8 fields (M3 has 12+); the size is entirely hardcoded.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/SwitchDemo.kt:44`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/SwitchDemo.kt#L44) · [`example/shared/src/commonMain/kotlin/component/SwitchSection.kt:47`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SwitchSection.kt#L47)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Switch.kt:66`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Switch.kt#L66)</sub>

## TextButton  ·  basic component

A convenience wrapper for a button with text; internally it maps TextButtonColors to ButtonColors and delegates to Button. Note it also has a background by default.

> A [TextButton] component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.TextButton

@Composable
fun TextButton(
    text: String,  // required
    onClick: () -> Unit,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    cornerRadius: Dp = ButtonDefaults.CornerRadius,
    minWidth: Dp = ButtonDefaults.MinWidth,
    minHeight: Dp = ButtonDefaults.MinHeight,
    colors: TextButtonColors = ButtonDefaults.textButtonColors(),
    insideMargin: PaddingValues = ButtonDefaults.InsideMargin,
    textStyle: TextStyle? = null,
    interactionSource: MutableInteractionSource? = null,
    indication: Indication? = LocalIndication.current,
)
```

- `text` — The text of the [TextButton].
- `onClick` — The callback when the [TextButton] is clicked.
- `modifier` — The modifier to be applied to the [TextButton].
- `enabled` — Whether the [TextButton] is enabled.
- `cornerRadius` — The corner radius of the [TextButton].
- `minWidth` — The minimum width of the [TextButton].
- `minHeight` — The minimum height of the [TextButton].
- `colors` — The [TextButtonColors] of the [TextButton].
- `insideMargin` — The margin inside the [TextButton].
- `interactionSource` — The [MutableInteractionSource] to be used for the [TextButton].
- `indication` — The [Indication] to be used for the [TextButton].

**TextButtonColors** (data class) 

**Traps**

- 🔴 colors is of type TextButtonColors, not ButtonColors; the two classes' fields correspond one-to-one but with different names (contentColor vs textColor). Passing ButtonDefaults.buttonColorsPrimary() to TextButton fails to compile; you must use textButtonColorsPrimary().  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Button.kt:119`)
- 🔴 The default background is secondaryVariant (gray), not transparent. M3's TextButton is a background-less text-only button; Miuix's TextButton is just 'Button + an auto-wrapped Text' and looks exactly like Button. For a transparent button you must pass color = Color.Transparent yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Button.kt:217`)
- ⚪ There is no content slot; you can only pass a String. To place an icon + text, use Button directly. textStyle is nullable; when null it uses MiuixTheme.textStyles.button.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Button.kt:121`)

**Spec** min_size 58×40.dp (same as Button) · corner 16.dp squircle

**State** Purely stateless; all parameters are passed through to Button.

**vs Material3** Corresponds to material3.TextButton. The differences are large: M3's TextButton has no background and no border, while Miuix's has a gray fill by default; and its colors type is separate and not interchangeable with Button's.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/ButtonDemo.kt:76`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/ButtonDemo.kt#L76) · [`docs/demo/src/commonMain/kotlin/Demo.kt:122`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/Demo.kt#L122) · [`docs/demo/src/commonMain/kotlin/OverlayBottomSheetDemo.kt:54`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayBottomSheetDemo.kt#L54) · [`docs/demo/src/commonMain/kotlin/OverlayCascadingListPopupDemo.kt:85`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/OverlayCascadingListPopupDemo.kt#L85)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Button.kt:111`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Button.kt#L111)</sub>

## TextField  ·  basic component

A filled text field, squircle background + a 2.dp border that grows on focus + a floating label. Three overloads correspond to the TextFieldState / TextFieldValue / String state models.

> A [TextField] component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.TextField

@Composable
fun TextField(
    state: TextFieldState,  // required
    modifier: Modifier = Modifier,
    insideMargin: DpSize = TextFieldDefaults.InsideMargin,
    colors: TextFieldColors = TextFieldDefaults.textFieldColors(),
    cornerRadius: Dp = TextFieldDefaults.CornerRadius,
    label: String = "",
    useLabelAsPlaceholder: Boolean = false,
    enabled: Boolean = true,
    readOnly: Boolean = false,
    inputTransformation: InputTransformation? = null,
    textStyle: TextStyle = MiuixTheme.textStyles.main,
    keyboardOptions: KeyboardOptions = KeyboardOptions.Default,
    onKeyboardAction: KeyboardActionHandler? = null,
    lineLimits: TextFieldLineLimits = TextFieldLineLimits.Default,
    leadingIcon: @Composable (() -> Unit)? = null,
    trailingIcon: @Composable (() -> Unit)? = null,
    onTextLayout: (Density.(getResult: () -> TextLayoutResult?) -> Unit)? = null,
    interactionSource: MutableInteractionSource? = null,
    cursorBrush: Brush = SolidColor(colors.borderColor),
    outputTransformation: OutputTransformation? = null,
    scrollState: ScrollState = rememberScrollState(),
)
```

- `state` — The [TextFieldState] to be shown in the text field.
- `modifier` — The modifier to be applied to the [TextField].
- `insideMargin` — The margin inside the [TextField].
- `colors` — The [TextFieldColors] applied to the [TextField]. Use   [TextFieldDefaults.textFieldColors] to customize.
- `cornerRadius` — The corner radius of the [TextField].
- `label` — The label to be displayed when the [TextField] is empty.
- `useLabelAsPlaceholder` — Whether to use the label as a placeholder.
- `enabled` — Whether the [TextField] is enabled.
- `readOnly` — Whether the [TextField] is read-only.
- `inputTransformation` — The input transformation to be applied to the [TextField].
- `textStyle` — The text style to be applied to the [TextField].
- `keyboardOptions` — The keyboard options to be applied to the [TextField].
- `onKeyboardAction` — The keyboard action handler for the [TextField].
- `lineLimits` — The line limits for the [TextField].
- `leadingIcon` — The leading icon to be displayed in the [TextField].
- `trailingIcon` — The trailing icon to be displayed in the [TextField].
- `onTextLayout` — The callback to be called when the text layout changes.
- `interactionSource` — The interaction source to be applied to the [TextField].
- `cursorBrush` — The brush to be used for the cursor.
- `outputTransformation` — The output transformation for the text field.
- `scrollState` — The scroll state for the text field.

**TextFieldDefaults**


```kotlin
TextFieldDefaults.textFieldColors(
    backgroundColor: Color = MiuixTheme.colorScheme.secondaryContainer,
    labelColor: Color = MiuixTheme.colorScheme.onSecondaryContainer,
    borderColor: Color = MiuixTheme.colorScheme.primary,
)
```

- `CornerRadius = 16.dp`
- `InsideMargin = DpSize(16.dp, 16.dp)`

**TextFieldColors** (data class) 

**Traps**

- 🔴 In the TextFieldState overload, remember(label, useLabelAsPlaceholder){ derivedStateOf { … state.text … } } has no state in its key, yet the closure reads it. After swapping the TextFieldState instance (e.g. rebuilding state per form-field id, or switching the edited object at the same position), the label state machine keeps watching the old instance forever: typing in the new field doesn't float the label up, and clearing doesn't drop it back. The other two overloads put the value in the key; only this one doesn't. Workaround: wrap this position in key(state){ … } or use the String overload.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TextField.kt:108`)
- 🔴 TextFieldColors has only three fields — backgroundColor / labelColor / borderColor — with no disabled or error variants. A field with enabled=false looks exactly like an enabled one (it just doesn't respond to input), and the error state has no built-in appearance at all —— you must draw it yourself.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TextField.kt:419`)
- 🟡 There are no placeholder / supportingText / isError / prefix / suffix / shape parameters, and no OutlinedTextField variant. The placeholder role is served by label + useLabelAsPlaceholder=true (when there is text the label simply isn't drawn, rather than floating up).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TextField.kt:89`)
- 🟡 insideMargin is a DpSize (a horizontal and a vertical value) rather than PaddingValues, so asymmetric padding is impossible. Also the label and the input area are overlaid in the same Box, offset by ±insideMargin.height/2, so shrinking insideMargin.height clips the floated-up label.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TextField.kt:379`)
- 🟡 The label's font-size animation is carried by animateDpAsState and consumed via `.value.sp` (Compose has no ready-made TextUnit animation, TextField.kt:451/525). Note Dp is only the animation carrier; after `.value` takes the raw Float it still sets fontSize in sp, so the label size scales with system font size like the body text. What does not scale is the float-up offset ±insideMargin.height/2 (DpSize, TextField.kt:446/533): with a larger font the gap between label and body text doesn't grow proportionally, so the floated-up state may sit too close.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TextField.kt:525`)

**Spec** corner 16.dp squircle · inside_margin DpSize(16.dp, 16.dp) · border 0.dp when unfocused, animates up to 2.dp on focus, color gradients from backgroundColor to primary · label_font 17 in resting state (dp used as sp), 10 when floated up · colors secondaryContainer background / onSecondaryContainer label / primary border and cursor

**State** Choose one of three models: TextFieldState (self-holding, recommended), TextFieldValue+onValueChange, or String+onValueChange (the latter two are purely controlled). The focus state is driven by interactionSource.collectIsFocusedAsState, and when null is passed it is built internally. cursorBrush defaults to colors.borderColor.

**vs Material3** Corresponds to material3.TextField / OutlinedTextField. Differences: only one appearance (filled squircle); no isError/supportingText/placeholder/prefix/suffix; no disabled colors; the focus indicator is a border growing from 0 to 2.dp rather than an underline.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/TextFieldDemo.kt:42`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TextFieldDemo.kt#L42) · [`example/shared/src/commonMain/kotlin/component/ArrowSection.kt:121`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ArrowSection.kt#L121) · [`example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt:241`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt#L241) · [`example/shared/src/commonMain/kotlin/component/ColorPickerSection.kt:142`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ColorPickerSection.kt#L142)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TextField.kt:82`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TextField.kt#L82)</sub>

## TextField  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A [TextField] component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.TextField

@Composable
fun TextField(
    value: TextFieldValue,  // required
    onValueChange: (TextFieldValue) -> Unit,  // required
    modifier: Modifier = Modifier,
    insideMargin: DpSize = TextFieldDefaults.InsideMargin,
    colors: TextFieldColors = TextFieldDefaults.textFieldColors(),
    cornerRadius: Dp = TextFieldDefaults.CornerRadius,
    label: String = "",
    useLabelAsPlaceholder: Boolean = false,
    enabled: Boolean = true,
    readOnly: Boolean = false,
    textStyle: TextStyle = MiuixTheme.textStyles.main,
    keyboardOptions: KeyboardOptions = KeyboardOptions.Default,
    keyboardActions: KeyboardActions = KeyboardActions.Default,
    leadingIcon: @Composable (() -> Unit)? = null,
    trailingIcon: @Composable (() -> Unit)? = null,
    singleLine: Boolean = false,
    maxLines: Int = if (singleLine) 1 else Int.MAX_VALUE,
    minLines: Int = 1,
    visualTransformation: VisualTransformation = VisualTransformation.None,
    onTextLayout: (TextLayoutResult) -> Unit = {},
    interactionSource: MutableInteractionSource? = null,
    cursorBrush: Brush = SolidColor(colors.borderColor),
)
```

- `value` — The input [TextFieldValue] to be shown in the text field.
- `onValueChange` — The callback that is triggered when the input service updates values in   [TextFieldValue]. An updated [TextFieldValue] comes as a parameter of the callback.
- `modifier` — The modifier to be applied to the [TextField].
- `insideMargin` — The margin inside the [TextField].
- `colors` — The [TextFieldColors] applied to the [TextField]. Use   [TextFieldDefaults.textFieldColors] to customize.
- `cornerRadius` — The corner radius of the [TextField].
- `label` — The label to be displayed when the [TextField] is empty.
- `useLabelAsPlaceholder` — Whether to use the label as a placeholder.
- `enabled` — Whether the [TextField] is enabled.
- `readOnly` — Whether the [TextField] is read-only.
- `textStyle` — The text style to be applied to the [TextField].
- `keyboardOptions` — The keyboard options to be applied to the [TextField].
- `keyboardActions` — The keyboard actions to be applied to the [TextField].
- `leadingIcon` — The leading icon to be displayed in the [TextField].
- `trailingIcon` — The trailing icon to be displayed in the [TextField].
- `singleLine` — Whether the text field is single line.
- `maxLines` — The maximum number of lines allowed to be displayed in [TextField].
- `minLines` — The minimum number of lines allowed to be displayed in [TextField]. It is required   that 1 <= [minLines] <= [maxLines].
- `visualTransformation` — The visual transformation to be applied to the [TextField].
- `onTextLayout` — The callback to be called when the text layout changes.
- `interactionSource` — The interaction source to be applied to the [TextField].
- `cursorBrush` — The brush to be used for the cursor.

**TextFieldDefaults**


```kotlin
TextFieldDefaults.textFieldColors(
    backgroundColor: Color = MiuixTheme.colorScheme.secondaryContainer,
    labelColor: Color = MiuixTheme.colorScheme.onSecondaryContainer,
    borderColor: Color = MiuixTheme.colorScheme.primary,
)
```

- `CornerRadius = 16.dp`
- `InsideMargin = DpSize(16.dp, 16.dp)`

**TextFieldColors** (data class) 

**Compilable examples** [`docs/demo/src/commonMain/kotlin/TextFieldDemo.kt:42`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TextFieldDemo.kt#L42) · [`example/shared/src/commonMain/kotlin/component/ArrowSection.kt:121`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ArrowSection.kt#L121) · [`example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt:241`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt#L241) · [`example/shared/src/commonMain/kotlin/component/ColorPickerSection.kt:142`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ColorPickerSection.kt#L142)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TextField.kt:188`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TextField.kt#L188)</sub>

## TextField  ·  basic component

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> A text field component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.TextField

@Composable
fun TextField(
    value: String,  // required
    onValueChange: (String) -> Unit,  // required
    modifier: Modifier = Modifier,
    insideMargin: DpSize = TextFieldDefaults.InsideMargin,
    colors: TextFieldColors = TextFieldDefaults.textFieldColors(),
    cornerRadius: Dp = TextFieldDefaults.CornerRadius,
    label: String = "",
    useLabelAsPlaceholder: Boolean = false,
    enabled: Boolean = true,
    readOnly: Boolean = false,
    textStyle: TextStyle = MiuixTheme.textStyles.main,
    keyboardOptions: KeyboardOptions = KeyboardOptions.Default,
    keyboardActions: KeyboardActions = KeyboardActions.Default,
    leadingIcon: @Composable (() -> Unit)? = null,
    trailingIcon: @Composable (() -> Unit)? = null,
    singleLine: Boolean = false,
    maxLines: Int = if (singleLine) 1 else Int.MAX_VALUE,
    minLines: Int = 1,
    visualTransformation: VisualTransformation = VisualTransformation.None,
    onTextLayout: (TextLayoutResult) -> Unit = {},
    interactionSource: MutableInteractionSource? = null,
    cursorBrush: Brush = SolidColor(colors.borderColor),
)
```

- `value` — The text to be displayed in the text field.
- `onValueChange` — The callback to be called when the value changes.
- `modifier` — The modifier to be applied to the [TextField].
- `insideMargin` — The margin inside the [TextField].
- `colors` — The [TextFieldColors] applied to the [TextField]. Use   [TextFieldDefaults.textFieldColors] to customize.
- `cornerRadius` — The corner radius of the [TextField].
- `label` — The label to be displayed when the [TextField] is empty.
- `useLabelAsPlaceholder` — Whether to use the label as a placeholder.
- `enabled` — Whether the [TextField] is enabled.
- `readOnly` — Whether the [TextField] is read-only.
- `textStyle` — The text style to be applied to the [TextField].
- `keyboardOptions` — The keyboard options to be applied to the [TextField].
- `keyboardActions` — The keyboard actions to be applied to the [TextField].
- `leadingIcon` — The leading icon to be displayed in the [TextField].
- `trailingIcon` — The trailing icon to be displayed in the [TextField].
- `singleLine` — Whether the text field is single line.
- `maxLines` — The maximum number of lines allowed to be displayed in [TextField].
- `minLines` — The minimum number of lines allowed to be displayed in [TextField]. It is required   that 1 <= [minLines] <= [maxLines].
- `visualTransformation` — The visual transformation to be applied to the [TextField].
- `onTextLayout` — The callback to be called when the text layout changes.
- `interactionSource` — The interaction source to be applied to the [TextField].
- `cursorBrush` — The brush to be used for the cursor.

**TextFieldDefaults**


```kotlin
TextFieldDefaults.textFieldColors(
    backgroundColor: Color = MiuixTheme.colorScheme.secondaryContainer,
    labelColor: Color = MiuixTheme.colorScheme.onSecondaryContainer,
    borderColor: Color = MiuixTheme.colorScheme.primary,
)
```

- `CornerRadius = 16.dp`
- `InsideMargin = DpSize(16.dp, 16.dp)`

**TextFieldColors** (data class) 

**Compilable examples** [`docs/demo/src/commonMain/kotlin/TextFieldDemo.kt:42`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/TextFieldDemo.kt#L42) · [`example/shared/src/commonMain/kotlin/component/ArrowSection.kt:121`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ArrowSection.kt#L121) · [`example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt:241`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/BottomSheetSection.kt#L241) · [`example/shared/src/commonMain/kotlin/component/ColorPickerSection.kt:142`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/ColorPickerSection.kt#L142)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TextField.kt:294`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/TextField.kt#L294)</sub>

## VerticalSlider  ·  basic component

A vertical slider, the same algorithm as Slider with height swapped for width. By default it grows from bottom to top.

> A vertical [Slider] component with Miuix style.

```kotlin
import top.yukonga.miuix.kmp.basic.VerticalSlider

@Composable
fun VerticalSlider(
    value: Float,  // required
    onValueChange: (Float) -> Unit,  // required
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    valueRange: ClosedFloatingPointRange<Float> = 0f..1f,
    steps: Int = 0,
    onValueChangeFinished: (() -> Unit)? = null,
    reverseDirection: Boolean = false,
    width: Dp = SliderDefaults.MinHeight,
    colors: SliderColors = SliderDefaults.sliderColors(),
    effect: Boolean = false,
    hapticEffect: SliderDefaults.SliderHapticEffect = SliderDefaults.DefaultHapticEffect,
    showKeyPoints: Boolean = false,
    keyPoints: List<Float>? = null,
    magnetThreshold: Float = 0.02f,
)
```

- `value` — The current value of the [Slider]. If outside of [valueRange] provided, value will be coerced to this range.
- `onValueChange` — The callback to be called when the value changes.
- `modifier` — The modifier to be applied to the [Slider].
- `enabled` — Whether the [Slider] is enabled.
- `valueRange` — Range of values that this slider can take. The passed [value] will be coerced to this range.
- `steps` — If positive, specifies the amount of discrete allowable values between the endpoints of [valueRange].
- `onValueChangeFinished` — Called when value change has ended.
- `reverseDirection` — Controls the direction of this slider. When false (default), slider increases from bottom to top.   When true, slider increases from top to bottom.
- `width` — The width of the vertical [Slider].
- `colors` — The [SliderColors] of the [Slider].
- `effect` — Whether to show the effect of the [Slider].
- `hapticEffect` — The haptic effect of the [Slider].
- `showKeyPoints` — Whether to show the key points (step indicators) on the slider. Only works when [keyPoints] is not null.
- `keyPoints` — Custom key point values to display on the slider. If null, uses step positions from [steps] parameter.   Values should be within [valueRange].
- `magnetThreshold` — The magnetic snap threshold as a fraction (0.0 to 1.0). When the slider value is within this   distance from a key point, it will snap to that point. Default is 0.02 (2%). Only applies when [keyPoints] is set.

**Traps**

- 🔴 The parameter effect: Boolean = false is never referenced anywhere in the function body; it is a completely dead parameter (the docs slider.md even describe it as 'whether to show a special effect'). Passing true does nothing.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:306`)
- 🟡 reverseDirection's meaning is opposite to the horizontal version: horizontal false = left to right, vertical false = bottom to top (true is top to bottom). Also the vertical version doesn't read LocalLayoutDirection at all and has no RTL mirroring (which vertical genuinely doesn't need, but don't expect symmetry with the horizontal version's behavior).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:861`)
- 🟡 The size parameter is called width (not height), and its default still reuses SliderDefaults.MinHeight = 28.dp. The length is provided by an external modifier (internally it's fillMaxHeight), so placed in a parent with unbounded height it collapses to 0.  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:470`)
- ⚪ Like the horizontal Slider, when enabled=false the setProgress semantics are still writable; isPressed is likewise always false. It also doesn't attach .hoverable, so its structure is asymmetric with the horizontal version (hover detection is maintained by a bare pointerInput; functionality is unaffected).  (`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:448`)

**Spec** track 28.dp wide (default, parameter name width), height fillMaxHeight, clipped into a pill · thumb same as Slider, radius = track radius × 0.72 · direction bottom to top when reverseDirection=false

**State** Same as Slider: purely controlled, onValueChange + onValueChangeFinished, with progressBarRangeInfo/setProgress accessibility semantics.

**vs Material3** No counterpart (Material3 has no official vertical Slider).

**Compilable examples** [`example/shared/src/commonMain/kotlin/component/SliderSection.kt:162`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/component/SliderSection.kt#L162)

<sub>Source [`miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt:295`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/Slider.kt#L295)</sub>

## Public types in this topic (13)

- `ButtonDefaults` **object** · `import top.yukonga.miuix.kmp.basic.ButtonDefaults`
- `CheckboxDefaults` **object** · `import top.yukonga.miuix.kmp.basic.CheckboxDefaults`
- `DropdownDefaults` **object** · `import top.yukonga.miuix.kmp.basic.DropdownDefaults`
- `DropdownEntry(items: List<DropdownItem>, enabled: Boolean)` **data class** (required: items) · `import top.yukonga.miuix.kmp.basic.DropdownEntry`
- `DropdownItem(text: String, enabled: Boolean, selected: Boolean, onClick: (() -> Unit)?, icon: @Composable ((Modifier) -> Unit)?, summary: String?, children: List<DropdownIte…)` **data class** (required: text) · `import top.yukonga.miuix.kmp.basic.DropdownItem`
- `IconButtonDefaults` **object** · `import top.yukonga.miuix.kmp.basic.IconButtonDefaults`
- `NumberPickerDefaults` **object** · `import top.yukonga.miuix.kmp.basic.NumberPickerDefaults`
- `RadioButtonDefaults` **object** · `import top.yukonga.miuix.kmp.basic.RadioButtonDefaults`
- `SliderDefaults` **object** · `import top.yukonga.miuix.kmp.basic.SliderDefaults`
- `SliderDefaults.SliderHapticEffect` **enum** — None, Edge, Step · `import top.yukonga.miuix.kmp.basic.SliderDefaults`
- `SpinnerDefaults` **object** · `import top.yukonga.miuix.kmp.basic.SpinnerDefaults`
- `SwitchDefaults` **object** · `import top.yukonga.miuix.kmp.basic.SwitchDefaults`
- `TextFieldDefaults` **object** · `import top.yukonga.miuix.kmp.basic.TextFieldDefaults`

