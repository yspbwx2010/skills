# Miuix reference index

For miuix **0.9.4**. One file per topic; signatures are generated from the source (maintainers regenerate with `tools/render.py` at the repo root — do not hand-edit).

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

**Find a symbol**: grep the section headings across files, then pull that section by line.

```bash
grep -rn "^## Switch  " references/            # -> references/ui-input.md:<line>
sed -n "<line>,+60p" references/ui-input.md     # read that section
```

**Build a kind of UI**: pick a topic file from the table and read it whole — each is kept to around a thousand-odd lines.

| File | Topic | For | Entries | Lines |
| --- | --- | --- | ---: | ---: |
| [recipes.md](recipes.md) | Recipes | Compile-verified combinations: bottom bar + pager + collapsing top bar, Chinese text on the web, icons for common meanings | 3 | 187 |
| [ui-scaffold.md](ui-scaffold.md) | Scaffold & containers | Page skeleton: Scaffold, TopAppBar, Card, Surface, dividers, pull-to-refresh, scrollbar, BasicComponent | 21 | 1064 |
| [ui-navigation.md](ui-navigation.md) | Navigation | NavigationBar / NavigationRail / TabRow / BreadcrumbBar / FloatingToolbar / FAB / SearchBar | 17 | 943 |
| [ui-input.md](ui-input.md) | Input controls | Button, Switch, Checkbox, RadioButton, Slider, TextField, NumberPicker, Dropdown | 17 | 1094 |
| [ui-display.md](ui-display.md) | Display & feedback | Text, Icon, Badge, ProgressIndicator, Tooltip, Snackbar, ListPopup content | 24 | 1191 |
| [ui-color.md](ui-color.md) | Color picking | The ColorPicker family, ColorPalette, color-space types | 26 | 938 |
| [ui-overlay.md](ui-overlay.md) | Overlays | The Overlay* and Window* families of Dialog / BottomSheet / ListPopup, and overlay content layout | 8 | 530 |
| [ui-theme.md](ui-theme.md) | Theme | MiuixTheme, colors, fonts, dynamic color, easing, HoldDown interaction | 11 | 384 |
| [ui-utils.md](ui-utils.md) | Interaction utilities | overScroll bounce, press feedback, haptics, Pager gesture-conflict handling, back-gesture scope | 15 | 475 |
| [preference.md](preference.md) | Preferences | The various *Preference rows of miuix-preference | 24 | 1213 |
| [preference-menu.md](preference-menu.md) | Preference menus & popups | The popup menus themselves (DropdownMenu / CascadingListPopup, etc.); the dropdown preference rows *DropdownPreference / *SpinnerPreference are in preference.md | 20 | 753 |
| [nav.md](nav.md) | Navigation framework | miuix-nav: NavDisplay, back stack, transitions, predictive back gesture | 13 | 501 |
| [blur.md](blur.md) | Blur | miuix-blur: background blur, progressive blur, highlight, sensor | 25 | 879 |
| [squircle.md](squircle.md) | Smooth corners | miuix-squircle: the squircle shape and clipping | 14 | 486 |
| [shader.md](shader.md) | Shader | miuix-shader | 7 | 145 |
| [core.md](core.md) | Core utilities | miuix-core: platform detection and other low-level helpers | 6 | 146 |
| [icons.md](icons.md) | Icon list | Every MiuixIcons name; grep here before writing an icon | — | 62 |

## Symbol -> file

**ui-scaffold.md** — `BasicComponent`, `Card`, `HorizontalDivider`, `HorizontalScrollBar`, `MiuixScrollBehavior`, `PullToRefresh`, `rememberPullToRefreshState`, `rememberScrollBarAdapter`, `rememberTopAppBarState`, `Scaffold`, `SmallTitle`, `SmallTopAppBar`, `Surface`, `TopAppBar`, `VerticalDivider`, `VerticalScrollBar`

**ui-navigation.md** — `BreadcrumbBar`, `FloatingActionButton`, `FloatingNavigationBar`, `FloatingNavigationBarItem`, `FloatingToolbar`, `InputField`, `List<BreadcrumbItem>.joinToPath`, `NavigationBar`, `RowScope.NavigationBarItem`, `NavigationRail`, `NavigationRailItem`, `rememberNavigationRailState`, `SearchBar`, `TabRow`, `TabRowWithContour`, `LocalNavigationBarDisplayMode`

**ui-input.md** — `Button`, `Checkbox`, `RowScope.DropdownArrowEndAction`, `DropdownImpl`, `IconButton`, `NumberPicker`, `RadioButton`, `RangeSlider`, `Slider`, `SpinnerItemImpl`, `Switch`, `TextButton`, `TextField`, `VerticalSlider`

**ui-display.md** — `Badge`, `BadgedBox`, `CircularProgressIndicator`, `Icon`, `InfiniteProgressIndicator`, `LinearProgressIndicator`, `ListPopupColumn`, `ListPopupContent`, `TooltipScope.PlainTooltip`, `rememberListPopupLayoutInfo`, `rememberTooltipState`, `TooltipScope.RichTooltip`, `RichTooltipBox`, `Snackbar`, `SnackbarHost`, `Text`, `TooltipBox`

**ui-color.md** — `ColorPalette`, `ColorPicker`, `Modifier.drawCheckerboard`, `HsvAlphaSlider`, `HsvColorPicker`, `HsvHueSlider`, `HsvSaturationSlider`, `HsvValueSlider`, `OkHsvAlphaSlider`, `OkHsvColorPicker`, `OkHsvHueSlider`, `OkHsvSaturationSlider`, `OkHsvValueSlider`, `OkLabAChannelSlider`, `OkLabAlphaSlider`, `OkLabBChannelSlider`, `OkLabColorPicker`, `OkLabLightnessSlider`, `OkLchAlphaSlider`, `OkLchChromaSlider`, `OkLchColorPicker`, `OkLchHueSlider`, `OkLchLightnessSlider`, `Color.toHsv`, `Color.toOkLab`, `Color.toOkLch`

**ui-overlay.md** — `OverlayBottomSheet`, `OverlayCascadingListPopup`, `OverlayDialog`, `OverlayListPopup`, `WindowBottomSheet`, `WindowCascadingListPopup`, `WindowDialog`, `WindowListPopup`

**ui-theme.md** — `InteractionSource.collectIsHeldDownAsState`, `darkColorScheme`, `defaultTextStyles`, `folmeSpring`, `lightColorScheme`, `MiuixTheme`, `platformDynamicColors`, `LocalContentColor`, `LocalDismissState`, `SinOutEasing`

**ui-utils.md** — `Modifier.horizontalPagerSwipeOverride`, `Modifier.iosStyleMomentumHalt`, `Modifier.overScrollHorizontal`, `Modifier.overScrollOutOfBound`, `Modifier.overScrollVertical`, `Modifier.pagerGestureOverride`, `Modifier.pressable`, `Modifier.scrollEndHaptic`, `PagerState.springAnimateToPage`, `WindowNavigationEventScope`, `LocalOverScrollState`, `PagerNavigationSpringSpec`

**preference.md** — `ArrowPreference`, `CheckboxPreference`, `OverlayDropdownPreference`, `OverlaySpinnerPreference`, `RadioButtonPreference`, `RangeSliderPreference`, `SliderPreference`, `SwitchPreference`, `WindowDropdownPreference`, `WindowSpinnerPreference`

**preference-menu.md** — `OverlayDropdownDialog`, `OverlayDropdownMenu`, `OverlayDropdownPopup`, `OverlayIconCascadingDropdownMenu`, `OverlayIconDropdownMenu`, `WindowDropdownDialog`, `WindowDropdownMenu`, `WindowDropdownPopup`, `WindowIconCascadingDropdownMenu`, `WindowIconDropdownMenu`

**nav.md** — `navBackStackOf`, `navDirectionalTransition`, `NavDisplay`, `navGraphicsTransition`, `Modifier.navSwipeDismiss`, `PredictiveBackHandler`, `rememberNavBackStack`, `rememberNavController`, `rememberNavSystemCornerRadius`, `WindowNavigationEventBridge`, `LocalNavTransitionScope`, `NavProgrammaticEasing`

**blur.md** — `RuntimeShader.asBrush`, `RuntimeShader.asComposeShader`, `BackdropEffectScope.blendColors`, `BackdropEffectScope.blur`, `BackdropEffectScope.colorControls`, `Modifier.drawBackdrop`, `BackdropEffectScope.effect`, `isRuntimeShaderSupported`, `Modifier.layerBackdrop`, `BackdropEffectScope.noiseDither`, `BackdropEffectScope.progressiveBlur`, `Modifier.progressiveTextureBlur`, `BackdropEffectScope.progressiveTextureBlurEffect`, `rememberDeviceTilt`, `rememberLayerBackdrop`, `rememberTiltLight`, `RuntimeShader`, `BackdropEffectScope.runtimeShaderEffect`, `Modifier.textureBlur`, `BackdropEffectScope.textureBlurEffect`, `Modifier.textureEffect`, `LocalRuntimeShaderCache`

**squircle.md** — `Modifier.absoluteSquircleBackground`, `Modifier.absoluteSquircleClip`, `Modifier.absoluteSquircleSurface`, `Path.addSquircleRect`, `isSquircleEnabled`, `Modifier.squircleBackground`, `Modifier.squircleBorder`, `Modifier.squircleClip`, `Modifier.squircleSurface`, `LocalSquircleEnabled`

**shader.md** — `RuntimeShader.asAndroidRuntimeShader`, `RuntimeShader.asBrush`, `RuntimeShader.asComposeShader`, `RuntimeShader.asSkikoRuntimeShader`, `isRenderEffectSupported`, `isRuntimeShaderSupported`, `RuntimeShader`

**core.md** — `getCornerRadiusBottom`, `getRoundedCorner`, `platform`, `platformDialogProperties`, `RemovePlatformDialogDefaultEffects`, `hasFocusReassignBug`

