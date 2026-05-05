---
name: kb-kmm-android-environments
description: "Android implementation knowledge base for the multi-brand/multi-environment system in KMM: product flavors, BuildConfig plugin (gmazzo), brand/env resolution, .properties files and shared contract generation."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Android Environments KMM — Knowledge Base

## Rule 1: This skill implements Android, it does not define global semantics

This skill describes how to materialize the `brand × env` matrix in Android.

Not defined here — see indicated skills:
- meaning of `brand` / `env` → `kb-kmm-brands`, `kb-kmm-environments`
- which values must exist per variant → `kb-kmm-brands`, `kb-kmm-environments`
- secret sensitivity policy → `kb-kmm-environments`

## Rule 2: The BuildConfig plugin materializes the shared contract

Android uses `com.github.gmazzo.buildconfig` to generate an object accessible from `commonMain`. If the project already has the plugin at a different version, use the existing version.

→ Templates: `references/android_buildconfig_templates.md`

## Rule 3: Android models variants with per-dimension flavors

- one flavor dimension for `brand`
- one flavor dimension for `env`

The combination of both dimensions produces the Android variants.

→ Templates: `references/android_buildconfig_templates.md`

## Rule 4: `brand` and `env` resolution has explicit priority

```text
1. Explicit Gradle properties
2. Inference from task name
3. Default values
```

Explicit priority is the stable path for CI and any integration where depending on the task name is undesirable.

→ Templates: `references/android_buildconfig_templates.md`

## Rule 5: `.properties` files store only declarative values

`{brand}-{env}.properties` files live at the project root. They contain only values Android cannot derive automatically from `brand` and `env`. Do not use them for purely derived values that the `buildConfig` block can already compute.

→ Templates: `references/android_properties_templates.md`

## Rule 6: The `buildConfig` block combines a fixed scaffold and project fields

Two distinct zones:
- fixed scaffold: variant resolution and properties loading
- project-specific `buildConfigField` entries to expose in the shared contract

Only fields the project has decided to publish in its shared contract need to be exposed.

→ Templates: `references/android_buildconfig_templates.md`

## Rule 7: This skill does not define iOS

XCConfig, schemes, Xcode build configurations, and build phase scripts belong to `kb-kmm-ios-environments`.

## Rule 8: Android troubleshooting belongs to this skill

Errors related to: BuildConfig plugin · Android flavors · `.properties` loading · `-Papp.brand` / `-Papp.env` resolution — handled here, not in the global semantic skill.