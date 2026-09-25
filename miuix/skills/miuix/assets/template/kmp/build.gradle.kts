// plugins declare their version only here; submodules apply them as needed.
plugins {
    // @if:android
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.android.kmp.library) apply false
    // @endif
    alias(libs.plugins.kotlin.multiplatform) apply false
    alias(libs.plugins.kotlin.compose) apply false
    alias(libs.plugins.kotlin.serialization) apply false
    alias(libs.plugins.compose.multiplatform) apply false
}
