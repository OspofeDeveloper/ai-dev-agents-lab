---
name: kb-kmm-ios-environments
description: "Knowledge base for the iOS implementation of the multi-brand/multi-environment system in KMM: XCConfig, target/build configuration/scheme, XCConfig → Script Build Phase → Gradle flow, and Xcode file structure."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM iOS Environments — Knowledge Base

## Rule 1: This skill implements iOS — it does not define global semantics

This skill describes how to materialize the `brand × env` matrix on iOS.

It does not define:

- what `brand` means
- what `env` means
- which values form part of the shared contract
- the general sensitivity policy

Those rules live in:

- `kb-kmm-brands`
- `kb-kmm-environments`

---

## Rule 2: iOS uses XCConfig as its operational variant source

The iOS materialization is based on:

- `XCConfig`
- target
- build configuration
- scheme
- script build phase

The selected scheme and the active build configuration in Xcode determine which variant iOS materializes.

---

## Rule 3: XCConfig → Script → Gradle flow

The standard operational flow is:

1. The developer selects a scheme.
2. The scheme activates a target and a build configuration.
3. The associated XCConfig exposes values such as `APP_ENV`.
4. The script build phase reads those values.
5. The script invokes Gradle with explicit properties.

The concrete implementation of that script lives in `references/ios_script_build_phase_template.md`.

---

## Rule 4: The XCConfig hierarchy separates shared layers from the variant layer

The iOS configuration distinguishes:

- a shared level
- a debug/release level
- a brand × env level

The brand × env file must not absorb the debug/release layer on its own; both are assigned from the Xcode configuration.

→ Templates: `references/ios_xcconfig_templates.md`

---

## Rule 5: Target, Build Configuration, and Scheme are distinct responsibilities

In iOS:

- the **target** represents the compilation unit for a brand
- the **build configuration** represents the debug/release × env layer
- the **scheme** selects which combination is activated per action

These must not be treated as the same mechanism.

---

## Rule 6: The iOS implementation does not define Android

This skill contains no rules about:

- the BuildConfig plugin
- Android product flavors
- `.properties` files
- Gradle task name resolution

The Android implementation belongs to `kb-kmm-android-environments`.

---

## Rule 7: Values passed by the script to Gradle must be minimal and explicit

The script build phase must not reconstruct variant logic beyond passing the properties Gradle needs to identify the active variant.

Variant semantics are already resolved by:

- target
- build configuration
- scheme
- XCConfig

→ Templates: `references/ios_script_build_phase_template.md`

---

## Rule 8: iOS troubleshooting belongs to this dimension

Errors related to:

- unlinked XCConfig
- empty `APP_ENV`
- wrong target
- incorrect scheme
- misconfigured build configuration

are handled in this dimension, not in the global semantic skill.