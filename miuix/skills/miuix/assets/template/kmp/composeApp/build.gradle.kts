// @if:web
import org.jetbrains.kotlin.gradle.ExperimentalWasmDsl

// @endif
plugins {
    alias(libs.plugins.kotlin.multiplatform)
    // @if:android
    // Since AGP 9, a KMP module can no longer use com.android.application / com.android.library; the APK comes from the androidApp module.
    alias(libs.plugins.android.kmp.library)
    // @endif
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.compose.multiplatform)
    // miuix-nav route keys need @Serializable; the runtime library is brought in by miuix-nav as an api dependency.
    alias(libs.plugins.kotlin.serialization)
}

kotlin {
    jvmToolchain(21)

    // @if:android
    android {
        namespace = "{{PACKAGE}}.shared"
        compileSdk = 37 // androidx.compose 1.12, which miuix 0.9.4 depends on, requires >= 37
        minSdk = 24
    }

    // @endif
    // @if:desktop
    jvm()

    // @endif
    // @if:web
    @OptIn(ExperimentalWasmDsl::class)
    wasmJs {
        browser()
        binaries.executable()
    }

    // @endif
    sourceSets {
        commonMain.dependencies {
            // in KMP, use the coordinates with no platform suffix; Gradle metadata picks the right variant per target.
            implementation(libs.miuix.ui)
            implementation(libs.miuix.preference)
            implementation(libs.miuix.icons)
            implementation(libs.miuix.nav)
        }
        // @if:desktop
        jvmMain.dependencies {
            implementation(compose.desktop.currentOs)
        }
        // @endif
    }
}
// @if:desktop

compose.desktop {
    application {
        mainClass = "{{PACKAGE}}.MainKt"
    }
}
// @endif
