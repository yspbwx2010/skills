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
