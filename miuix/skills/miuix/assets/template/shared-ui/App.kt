package {{PACKAGE}}

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.input.nestedscroll.nestedScroll
import androidx.compose.ui.unit.dp
import kotlinx.serialization.Serializable
import top.yukonga.miuix.kmp.basic.BasicComponent
import top.yukonga.miuix.kmp.basic.ButtonDefaults
import top.yukonga.miuix.kmp.basic.Card
import top.yukonga.miuix.kmp.basic.Icon
import top.yukonga.miuix.kmp.basic.IconButton
import top.yukonga.miuix.kmp.basic.MiuixScrollBehavior
import top.yukonga.miuix.kmp.basic.Scaffold
import top.yukonga.miuix.kmp.basic.SmallTitle
import top.yukonga.miuix.kmp.basic.TextButton
import top.yukonga.miuix.kmp.basic.TopAppBar
import top.yukonga.miuix.kmp.icon.MiuixIcons
import top.yukonga.miuix.kmp.icon.extended.Back
import top.yukonga.miuix.kmp.nav.core.NavDisplay
import top.yukonga.miuix.kmp.nav.core.NavKey
import top.yukonga.miuix.kmp.nav.core.rememberNavBackStack
import top.yukonga.miuix.kmp.preference.ArrowPreference
import top.yukonga.miuix.kmp.preference.SwitchPreference
import top.yukonga.miuix.kmp.theme.ColorSchemeMode
import top.yukonga.miuix.kmp.theme.MiuixTheme
import top.yukonga.miuix.kmp.theme.ThemeController
import top.yukonga.miuix.kmp.window.WindowDialog

// @if:web
// UI text is English: the web (wasmJs) target has no CJK font, so Chinese renders as boxes. For Chinese, see references/recipes.md "Chinese text on the web".
// @endif

// miuix-nav route keys must be @Serializable (needs the kotlin serialization compiler plugin).
@Serializable
sealed interface Route : NavKey {
    @Serializable data object Home : Route

    @Serializable data object About : Route
}

@Composable
fun App() {
    // Use the controller overload: MiuixTheme(colors = …) does not provide LocalContentColor, so text stays black in dark mode.
    MiuixTheme(controller = remember { ThemeController(ColorSchemeMode.System) }) {
        // Write <Route> explicitly: (Route.Home) alone infers the type as Home, which crashes on state save after pushing About.
        val backStack = rememberNavBackStack<Route>(Route.Home)
        // Register an entry per concrete subtype; entry<Route> does not match subtypes. The system back key pops by default.
        NavDisplay(backStack = backStack) {
            entry<Route.Home> { HomePage(onOpenAbout = { backStack.add(Route.About) }) }
            entry<Route.About> { AboutPage(onBack = { backStack.removeLastOrNull() }) }
        }
    }
}

@Composable
private fun HomePage(onOpenAbout: () -> Unit) {
    var notifications by remember { mutableStateOf(true) }
    var showResetDialog by remember { mutableStateOf(false) }
    // MiuixScrollBehavior is a @Composable function; call it directly in composition, don't wrap it in remember { }.
    val scrollBehavior = MiuixScrollBehavior()

    Scaffold(
        topBar = { TopAppBar(title = "{{APP_NAME}}", scrollBehavior = scrollBehavior) },
    ) { padding ->
        LazyColumn(
            // Without nestedScroll the top bar won't collapse; overscroll is already provided by MiuixTheme, don't add overScrollVertical() on top.
            modifier = Modifier.fillMaxHeight().nestedScroll(scrollBehavior.nestedScrollConnection),
            // The Scaffold's padding does not apply automatically; without it the content sits under the top bar.
            contentPadding = padding,
        ) {
            item {
                SmallTitle(text = "General")
                // Preference does not handle group corners; wrap a group of preferences in a Card.
                Card(modifier = Modifier.padding(horizontal = 12.dp)) {
                    SwitchPreference(
                        checked = notifications,
                        onCheckedChange = { notifications = it },
                        title = "Notifications",
                        summary = if (notifications) "On" else "Off",
                    )
                    ArrowPreference(
                        title = "Reset settings",
                        summary = "Shows a confirm dialog",
                        onClick = { showResetDialog = true },
                    )
                    ArrowPreference(title = "About", onClick = onOpenAbout)
                }
            }
        }
    }

    ConfirmDialog(
        show = showResetDialog,
        title = "Reset settings?",
        summary = "All options go back to their defaults.",
        onConfirm = { notifications = true },
        onDismiss = { showResetDialog = false },
    )
}

@Composable
private fun AboutPage(onBack: () -> Unit) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = "About",
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        // MiuixIcons.Back is from the miuix-icons module; miuix-ui bundles only the seven MiuixIcons.Basic.*.
                        Icon(imageVector = MiuixIcons.Back, contentDescription = "Back")
                    }
                },
            )
        },
    ) { padding ->
        Card(modifier = Modifier.padding(padding).padding(12.dp)) {
            BasicComponent(title = "{{APP_NAME}}", summary = "Built with Miuix 0.9.4")
        }
    }
}

@Composable
private fun ConfirmDialog(
    show: Boolean,
    title: String,
    summary: String,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
) {
    // WindowDialog shows anywhere; OverlayDialog must be inside a Scaffold or it silently renders nothing.
    // Without onDismissRequest, tapping outside and pressing back cannot dismiss it.
    WindowDialog(show = show, title = title, summary = summary, onDismissRequest = onDismiss) {
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            TextButton(text = "Cancel", onClick = onDismiss, modifier = Modifier.weight(1f))
            TextButton(
                text = "Confirm",
                onClick = {
                    onConfirm()
                    onDismiss()
                },
                modifier = Modifier.weight(1f),
                // TextButton's colors is TextButtonColors: passing buttonColorsPrimary() won't compile.
                colors = ButtonDefaults.textButtonColorsPrimary(),
            )
        }
    }
}
