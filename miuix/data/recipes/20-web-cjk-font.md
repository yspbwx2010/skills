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
