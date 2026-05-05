---
name: wf-kmm-environments
description: "Set up a multi-brand/multi-environment system in a KMM project by composing stable variant semantics and their Android and iOS implementations."
argument-hint: "[brands and environments, e.g. 'pre pro' or 'cuideo felizvita with pre and pro']"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-platform-integrator
---

# wf-kmm-environments

Set up a multi-brand/multi-environment system in a KMM project by composing stable semantics and per-platform implementations.

---

## Step 1: Gather requirements

If the user has not specified all parameters, ask for:

1. **Brands** — how many brands, plus names and application IDs
2. **Environments** — which build environments, and whether any add an App ID suffix
3. **API URLs** — one base URL per `brand × env` combination
4. **Additional variables** — API keys, feature flags, analytics keys, or other variant-dependent values

Once collected, compute the `brand × env` matrix and confirm it with the user before touching files, following **Rule 2** of `kb-kmm-environments` and **Rule 2** of `kb-kmm-brands`.

---

## Step 2: Read the current project state

Read these files to understand what exists and what is missing:

- `gradle/libs.versions.toml`
- `composeApp/build.gradle.kts`
- `iosApp/iosApp.xcodeproj/project.pbxproj` for existing targets and schemes
- `iosApp/Configuration/` to verify whether XCConfigs already exist

---

## Step 3: Consult stable variant semantics

Consult `kb-kmm-brands` and `kb-kmm-environments` to fix:

- brand catalogue
- `brand × env` matrix
- declarative vs derived values
- variable sensitivity
- shared contract consumed by `commonMain`

Use as anchors:

- `kb-kmm-brands` -> **Regla 1**, **Regla 2** y **Regla 4**
- `kb-kmm-environments` -> **Regla 1**, **Regla 2**, **Regla 4**, **Regla 5** y **Regla 7**

---

## Step 4: Apply the Android implementation

Consult `kb-kmm-android-environments` to:

- register the BuildConfig plugin
- configure flavor dimensions and `productFlavors`
- implement `brand/env` resolution
- declare shared-contract `buildConfigField` entries
- create `.properties` only for declarative values

Use **Rule 2**, **Rule 3**, **Rule 4**, and **Rule 5** of `kb-kmm-android-environments` as anchors.

---

## Step 5: Sync Gradle

Run a Gradle sync to verify that the newly declared plugin and its dependencies resolve before continuing. If it fails, review the declaration in `libs.versions.toml` first.

---

## Step 6: Apply the iOS implementation

Consult `kb-kmm-ios-environments` to:

- create the XCConfig hierarchy
- prepare targets, build configurations, and schemes
- add the script build phase
- pass only the minimum variant properties to Gradle

Use **Rule 2**, **Rule 3**, **Rule 4**, and **Rule 7** of `kb-kmm-ios-environments` as anchors.

If the project requires manual Xcode steps, derive them from the references of `kb-kmm-ios-environments`; do not turn this workflow into the normative source for those steps.

---

## Step 7: Report to the user

After applying all changes, report:

- list of created or modified files
- any pending manual Xcode steps from Step 6, explicitly
- post-setup usage reference: read `references/usage_reference.md` from `kb-kmm-environments` and show its content to the user
- suggested next step: verify the build by running the default Android variant and selecting a scheme in Xcode
