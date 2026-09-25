# {{APP_NAME}}

A Miuix (HyperOS-style) Compose Multiplatform app. There is one copy of the UI code:
`composeApp/src/commonMain/kotlin/…/App.kt`.

Needs **JDK 21**.
<!-- @if:android -->
The Android target also needs **Android SDK Platform 37** (set `sdk.dir=…` in `local.properties`, or set `ANDROID_HOME`).
<!-- @endif -->

| Platform | Build / run |
| --- | --- |
<!-- @if:android -->
| Android | `./gradlew :androidApp:assembleDebug` (install on a device: `:androidApp:installDebug`) |
<!-- @endif -->
<!-- @if:desktop -->
| Desktop | `./gradlew :composeApp:run` |
<!-- @endif -->
<!-- @if:web -->
| Web | `./gradlew :composeApp:wasmJsBrowserDevelopmentRun`; distribution: `:composeApp:wasmJsBrowserDistribution` → `composeApp/build/dist/wasmJs/productionExecutable/` |
<!-- @endif -->

All versions are pinned in `gradle/libs.versions.toml`: Gradle 9.7.1 · Kotlin 2.4.20 · Compose Multiplatform 1.12.0 · miuix 0.9.4
<!-- @if:android -->
· AGP 9.4.1 · activity-compose 1.13.0
<!-- @endif -->
