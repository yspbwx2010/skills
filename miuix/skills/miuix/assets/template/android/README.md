# {{APP_NAME}}

A Miuix (HyperOS-style) plain Android app, a single `app` module. The UI code is in
`app/src/main/kotlin/…/App.kt`.

Needs **JDK 21** and **Android SDK Platform 37** (set `sdk.dir=…` in `local.properties`, or set
`ANDROID_HOME`).

- Build: `./gradlew :app:assembleDebug` → `app/build/outputs/apk/debug/app-debug.apk`
- Install on a device: `./gradlew :app:installDebug`

All versions are pinned in `gradle/libs.versions.toml` (Gradle 9.7.1 · AGP 9.4.1 · Kotlin 2.4.20 ·
miuix 0.9.4).
