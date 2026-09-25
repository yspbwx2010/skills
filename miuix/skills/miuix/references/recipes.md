# Recipes

Compile-verified combinations: bottom bar + pager + collapsing top bar, Chinese text on the web, icons for common meanings. Hand-written, from `data/recipes/`; each was compiled in an empty-directory trial. See [index.md](index.md) for the other topics.

## Bottom bar + HorizontalPager + collapsing top bar

Three pages you swipe between, switchable from the bottom bar too; a horizontal swipe still changes
the page while a list is flinging, and the top bar collapses with the list while its title follows
the current page. (Verified in an empty-directory plain-Android project: first `assembleDebug`
passed.)

```kotlin
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.nestedscroll.nestedScroll
import kotlinx.coroutines.launch
import top.yukonga.miuix.kmp.basic.BasicComponent
import top.yukonga.miuix.kmp.basic.MiuixScrollBehavior
import top.yukonga.miuix.kmp.basic.NavigationBar
import top.yukonga.miuix.kmp.basic.NavigationBarItem
import top.yukonga.miuix.kmp.basic.Scaffold
import top.yukonga.miuix.kmp.basic.TopAppBar
import top.yukonga.miuix.kmp.icon.MiuixIcons
import top.yukonga.miuix.kmp.icon.extended.Community
import top.yukonga.miuix.kmp.icon.extended.Contacts
import top.yukonga.miuix.kmp.icon.extended.Home
import top.yukonga.miuix.kmp.utils.PagerGestureNestedScrollConnection
import top.yukonga.miuix.kmp.utils.pagerGestureOverride
import top.yukonga.miuix.kmp.utils.springAnimateToPage

private class Tab(val label: String, val icon: ImageVector)

@Composable
fun TabbedPages() {  // call this inside MiuixTheme { }
    val tabs = listOf(Tab("Home", MiuixIcons.Home), Tab("Discover", MiuixIcons.Community), Tab("Me", MiuixIcons.Contacts))
    val pagerState = rememberPagerState(pageCount = { tabs.size })
    val scope = rememberCoroutineScope()
    val scrollBehavior = MiuixScrollBehavior()   // one shared across all three; the top bar's collapse follows the currently scrolling list
    val selected = pagerState.targetPage         // targetPage: on a bottom-bar tap the selected state lands on the target page directly

    Scaffold(
        topBar = { TopAppBar(title = tabs[selected].label, scrollBehavior = scrollBehavior) },
        bottomBar = {
            NavigationBar {
                tabs.forEachIndexed { i, tab ->
                    NavigationBarItem(
                        selected = selected == i,
                        onClick = { scope.launch { pagerState.springAnimateToPage(i) } },
                        icon = tab.icon,
                        label = tab.label,
                    )
                }
            }
        },
    ) { padding ->
        HorizontalPager(
            state = pagerState,
            modifier = Modifier.fillMaxSize().pagerGestureOverride(pagerState),
            userScrollEnabled = false,                                   // these two must be changed
            pageNestedScrollConnection = PagerGestureNestedScrollConnection, // together with pagerGestureOverride
        ) { page ->
            LazyColumn(
                modifier = Modifier.fillMaxSize().nestedScroll(scrollBehavior.nestedScrollConnection),
                contentPadding = padding,  // the Scaffold's padding does not apply automatically
            ) {
                items(50) { i -> BasicComponent(title = "${tabs[page].label} row ${i + 1}") }
            }
        }
    }
}
```

If a page has horizontally swipeable components (a horizontal `LazyRow`, `Slider`, a carousel),
0.9.4's default interception mode steals their horizontal swipe — see `Modifier.pagerGestureOverride`
in `ui-utils.md`, and switch to `PagerInterceptionMode.TapToHalt`.

## Chinese text on the web (wasmJs)

Compose's web target ships no CJK font, so Chinese renders as tofu boxes (Android and desktop use the
system font and are unaffected). The fix is to bundle a CJK font with Compose Resources and push it
into all 14 of Miuix's text styles — Miuix has no global font entry point. (Verified in a KMP
project: the wasm distribution and desktop compile pass with zero warnings and Chinese renders
correctly in the browser; without the font, the same page is all boxes.)

1. Download a CJK font, e.g. [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)
   (SIL OFL, redistributable with your app; the full weight range is ~10 MB — if you only need one
   weight, ship one file). Rename it to lowercase letters, digits and underscores only, and put it at
   `composeApp/src/commonMain/composeResources/font/noto_sans_sc.ttf`.
2. `composeApp/build.gradle.kts`:

   ```kotlin
   kotlin {
       sourceSets {
           commonMain.dependencies {
               implementation("org.jetbrains.compose.components:components-resources:1.12.0") // same version as Compose Multiplatform
           }
       }
   }
   compose.resources {
       packageOfResClass = "com.example.myapp.resources"   // the generated Res class goes in this package
   }
   ```

   The `compose.components.resources` form is deprecated in 1.12 (emits a `w:`); use the direct
   coordinate above.
3. Build the 14 styles and pass them to the theme:

   ```kotlin
   import androidx.compose.runtime.Composable
   import androidx.compose.runtime.remember
   import androidx.compose.ui.text.font.FontFamily
   import com.example.myapp.resources.Res
   import com.example.myapp.resources.noto_sans_sc
   import org.jetbrains.compose.resources.Font
   import top.yukonga.miuix.kmp.theme.TextStyles
   import top.yukonga.miuix.kmp.theme.defaultTextStyles

   @Composable
   fun cjkTextStyles(): TextStyles {
       val family = FontFamily(Font(Res.font.noto_sans_sc))   // Font(...) is @Composable, so this function is too
       return remember(family) {
           val d = defaultTextStyles()
           defaultTextStyles(
               main = d.main.copy(fontFamily = family),
               paragraph = d.paragraph.copy(fontFamily = family),
               body1 = d.body1.copy(fontFamily = family),
               body2 = d.body2.copy(fontFamily = family),
               button = d.button.copy(fontFamily = family),
               footnote1 = d.footnote1.copy(fontFamily = family),
               footnote2 = d.footnote2.copy(fontFamily = family),
               headline1 = d.headline1.copy(fontFamily = family),
               headline2 = d.headline2.copy(fontFamily = family),
               subtitle = d.subtitle.copy(fontFamily = family),
               title1 = d.title1.copy(fontFamily = family),
               title2 = d.title2.copy(fontFamily = family),
               title3 = d.title3.copy(fontFamily = family),
               title4 = d.title4.copy(fontFamily = family),
           )
       }
   }

   // In your App:
   // MiuixTheme(controller = remember { ThemeController(ColorSchemeMode.System) }, textStyles = cjkTextStyles()) { … }
   ```

The font loads asynchronously with the page, so the first frame may briefly show boxes and repaints
once it loads. If you only need it on the web, you can apply these styles in the wasmJs source set only.

## Common meaning -> icon name

The 156 miuix-icons names are action / object names, not page names like "discover" or "me". Below
are close picks for common meanings, all of which really exist (when unsure of a name, still defer to
`icons.md` — don't write from memory):

```kotlin
MiuixIcons.Home        // home
MiuixIcons.Community   // discover / community
MiuixIcons.Contacts    // me / profile (ContactsCircle is the round-avatar style)
MiuixIcons.Settings    // settings
MiuixIcons.Search      // search
MiuixIcons.Back        // back (ChevronBackward is the thin-arrow style)
MiuixIcons.More        // more (MoreCircle is the round style)
MiuixIcons.Add         // new / add
MiuixIcons.Edit        // edit
MiuixIcons.Delete      // delete
MiuixIcons.Share       // share
MiuixIcons.Favorites   // favorite (FavoritesFill is the filled style)
MiuixIcons.Messages    // messages
MiuixIcons.Info        // about / info
MiuixIcons.Help        // help
MiuixIcons.Refresh     // refresh
MiuixIcons.Filter      // filter
MiuixIcons.Sort        // sort
MiuixIcons.Download    // download
MiuixIcons.Lock        // privacy / lock
MiuixIcons.Theme       // theme / appearance
```

Each needs `import top.yukonga.miuix.kmp.icon.extended.<IconName>`, plus
`import top.yukonga.miuix.kmp.icon.MiuixIcons`.

