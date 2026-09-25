// AGP 9 has built-in Kotlin support: do not add org.jetbrains.kotlin.android.
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "{{PACKAGE}}"
    compileSdk = 37 // androidx.compose 1.12, which miuix 0.9.4 depends on, requires >= 37

    defaultConfig {
        applicationId = "{{PACKAGE}}"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
    }
}

kotlin {
    jvmToolchain(21)
}

dependencies {
    implementation(project(":composeApp"))
    implementation(libs.androidx.activity.compose)
}
