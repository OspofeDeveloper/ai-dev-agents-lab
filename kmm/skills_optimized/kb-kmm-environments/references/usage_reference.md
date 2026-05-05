# Post-Setup Usage Reference

## § Android build commands

```bash
./gradlew :composeApp:assemble{Brand}{Env}Debug
# e.g.: ./gradlew :composeApp:assembleBrand1Env1Debug

./gradlew :composeApp:assemble{Brand}{Env}Release
# e.g.: ./gradlew :composeApp:assembleBrand2Env2Release
```

With explicit properties (Priority 1 — recommended for CI/CD):
```bash
./gradlew assembleBrand1Env2Release -Papp.brand=brand1 -Papp.env=env2
```

---

## § iOS build

Select the scheme in Xcode (e.g. `Brand1-Env1`) and run normally. The scheme selection is the single source of truth — no ambiguity possible.

---

## § Using BuildConfig in shared code

```kotlin
import {basePackage}.BuildConfig

if (BuildConfig.IS_PRE) {
    // staging-only logic
}

val baseUrl = BuildConfig.APP_BASE_URL

when {
    BuildConfig.BRAND.startsWith("{BRAND1}") -> { /* brand1 logic */ }
    BuildConfig.BRAND.startsWith("{BRAND2}") -> { /* brand2 logic */ }
}
```

---

## § Adding a new variable

1. Add it to all Android `.properties` files.
2. In `composeApp/build.gradle.kts`, add it inside the `buildConfig { }` block:
   ```kotlin
   buildConfigField("KEY", properties.getProperty("KEY").trim())
   ```
3. If iOS Swift code also needs it: add it to each XCConfig and reference it in `Info.plist` as `$(KEY)`.

Implementation references:

- Android: see `kb-kmm-android-environments` → `references/android_properties_templates.md` and `references/android_buildconfig_templates.md`
- iOS: see `kb-kmm-ios-environments` → `references/ios_xcconfig_templates.md` and `references/ios_script_build_phase_template.md`