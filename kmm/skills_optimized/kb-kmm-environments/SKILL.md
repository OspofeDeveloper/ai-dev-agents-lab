---
name: kb-kmm-environments
description: "Knowledge base for environments and variants in KMM projects: stable env semantics, brand×env matrix composition, derived vs declarative values, platform-specific sources of truth, and criteria for sensitive configuration."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Environments — Knowledge Base

## Rule 1: `env` is a separate dimension from `brand`

The variant system combines two conceptually independent axes:

| Dimension | Controls |
|-----------|----------|
| `env` | integration target, URLs, build suffixes, environment flags, and any environment-dependent configuration |

`brand` semantics are defined in `kb-kmm-brands`.

This skill focuses on `env` and on how `env` combines with the brand catalog to form variants.

---

## Rule 2: The variant matrix composes brands and environments

Before considering Gradle, XCConfig, or any tooling, the project must clearly express:

- which environments exist
- which combination produces each variant
- which values belong to a specific variant

The `brand × env` matrix is built by combining:

- the brand catalog defined in `kb-kmm-brands`
- the environment catalog defined by this skill

Android and iOS simply materialize that matrix through different mechanisms.

---

## Rule 3: Environment values are those that change per operational target

`env` groups differences such as:

- base URL or integration target
- build suffixes
- environment flags
- external configuration that varies across pre, pro, staging, qa, or equivalents

If a value stays the same when only the environment changes, it does not belong in `env`.

---

## Rule 4: Distinguish declarative values from derived values

Not every configuration variable needs to be declared explicitly per variant.

- **Declarative:** values that cannot be safely derived from `brand` and `env` alone — such as URLs, keys, external identifiers, or arbitrary flags.
- **Derived:** values the system can compute deterministically from `brand` and `env`.

Tooling must not require manually persisting derived values that can already be computed reliably.

---

## Rule 5: Shared code consumes a single configuration contract

The project exposes a single configuration object or contract accessible from `commonMain`.

That contract must reflect the active variant at compile time or resolution time, regardless of how the platform materializes it:

- Gradle properties
- product flavors
- BuildConfig
- XCConfig
- build scripts

The shared semantics remain stable even as the underlying mechanism changes.

---

## Rule 6: Each platform has its own operational source of truth

Variant semantics are unified, but each platform may have a different operational source:

- Android may resolve the variant from explicit properties, tasks, or flavors
- iOS may resolve it from target, build configuration, scheme, and/or XCConfig

The important rule is not that both platforms work the same way, but that both resolve the same conceptual variant matrix.

---

## Rule 7: Sensitive configuration follows a different policy than public configuration

Not all variant values are treated equally:

- public or non-sensitive values may be versioned
- secrets and credentials must not be committed
- the system must allow CI or the build environment to inject those values without breaking the variant matrix

Sensitivity policy is part of the system design, not the tooling.

---

## Rule 8: Android and iOS implementations live in separate skills

This skill defines only the stable semantics of the multi-brand/multi-environment system.

Concrete implementation decisions live in:

- `kb-kmm-android-environments`
- `kb-kmm-ios-environments`

Do not duplicate rules specific to:

- Gradle plugins
- `BuildConfig`
- `XCConfig`
- Xcode scripts
- target / build configuration / scheme

---

## Rule 9: Workflows compose brands, environments, and tooling

Workflows may use this skill to:

- consume the brand catalog defined in `kb-kmm-brands`
- build the variant matrix
- decide what is derived and what is declarative
- identify which values are sensitive

Operational implementation is delegated to the Android and iOS skills — it is not redefined here.