---
name: kb-koin
description: "Koin DI knowledge base for KMM projects: feature-based module organization, registration types, qualifier pattern with enums, nativeModule expect/actual, initKoin and module ordering."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Koin DI KMM — Knowledge Base

## Rule 1: Koin defines wiring, not architectural ownership

Koin only resolves and wires dependencies. Ownership of each piece (`core`, feature, `app`) is decided by:
`kb-kmm-core-layer` · `kb-kmm-feature-clean-architecture` · `kb-kmm-app-layer` · `kb-kmm-clean-architecture`

Koin then registers those pieces in modules aligned with that structure.

## Rule 2: Module organization

```text
app/di/
  initKoin.kt         ← entry point, registers all modules
  appModule.kt        ← app-level ViewModels and UseCases
core/di/
  coreModule.kt       ← cross-cutting infrastructure and BuildConfig
  nativeModule.kt     ← expect val nativeModule (platform-specific)
features/<feature>/di/
  <feature>Module.kt
```

Conceptual wiring map — physical structure may vary as long as responsibility and clarity are preserved. No dynamic modules or lazy module loading. All modules registered in `initKoin`.

→ Templates: `references/koin_init_templates.md`

## Rule 3: initKoin — initialization

Single `initKoin(config: KoinAppDeclaration? = null)` in `commonMain`. Platform call sites:
- **Android**: `Application.onCreate()` — passes `androidLogger` and `androidContext`
- **iOS**: `ComposeUIViewController(configure = { initKoin() })`

`config` lets each platform inject its own configuration without `initKoin` knowing platform details.

→ Templates: `references/koin_init_templates.md`

## Rule 4: Registration types

| Type | DSL | Lifecycle | When to use |
|------|-----|-----------|-------------|
| `single` | `single { }` / `singleOf(::Class)` | App-wide singleton | Repositories, services, APIs, infrastructure clients, config |
| `factory` | `factory { }` / `factoryOf(::Class)` | New instance per injection | Use Cases |
| `viewModel` | `viewModelOf(::Class)` | Compose/Voyager lifecycle | Screen ViewModels |
| `single` (ViewModel) | `singleOf(::Class)` | Shared across screens | Shared ViewModels — exceptional |

**Golden rule**: unsure between `single`/`factory` for a Use Case → use `factory`.

Prefer `viewModelOf(::Class)` in `commonMain`. Avoid `viewModel { ... }` lambda DSL in KMP `commonMain` unless the project has the correct artifact/import and a concrete reason.

## Rule 5: Qualifiers distinguish instances, not architecture

Multiple instances of the same type → use **enums as qualifiers**, grouped by domain:

| Enum | File | Distinguishes |
|------|------|---------------|
| `NetworkQualifiers` | `core/di/NetworkQualifiers.kt` | HTTP clients, base URLs, network config |
| `AuthQualifiers` | `core/auth/data/AuthQualifiers.kt` | Identity client, client_id, grant types |
| `AndroidQualifiers` | `androidMain/.../AndroidQualifiers.kt` | Android implementations |
| `iOSQualifier` | `iosMain/.../iOSQualifier.kt` | iOS implementations |

Platform qualifiers are used only in `nativeModule` — never consumed from `commonMain`.

→ Templates: `references/koin_feature_module_template.md`

## Rule 6: Modules register the structure decided by layer skills

Typical feature wiring order:
```text
single      -> Api / Service
single      -> Repository
factory     -> Use Cases
viewModelOf -> ViewModels
```
This is a common wiring pattern, not an architectural rule independent of layer skills.

→ Templates: `references/koin_feature_module_template.md`

## Rule 7: nativeModule — platform-specific code

`expect val nativeModule` in `commonMain`, with `actual` in `androidMain` and `iosMain`. Registers platform-varying dependencies (DataStore, BLE, Firebase, etc.).

Always registered **first** in `initKoin` when other modules depend on platform infrastructure.

→ Templates: `references/koin_init_templates.md`

## Rule 8: expect/actual factory functions

When `commonMain` needs one implementation per platform with no need to distinguish multiple instances, use an `expect`/`actual` factory function instead of platform qualifiers.

## Rule 9: initKoin order and lazy resolution

Koin resolves **lazily** — instances are created on first request, not on module registration.

Required order:
```text
nativeModule → coreModule → [features] → appModule
```
Expresses structural dependencies, not initialization sequence.

## Rule 10: Koin does not define architecture or technical stack

Koin wires dependencies only. Architectural rules belong in the corresponding skill. Networking, auth, and persistence rules live in their own skills. If a rule holds true regardless of Koin, it doesn't belong here.

## Rule 11: Combine with layer and infrastructure skills

Use alongside: `kb-kmm-core-layer` · `kb-kmm-feature-clean-architecture` · `kb-kmm-app-layer` · networking / auth / storage skills (when the registered dependency belongs to those dimensions).

Koin registers and resolves; it doesn't redefine the conceptual rules of those pieces.

## Checklist

- [ ] Every `commonMain` ViewModel uses `viewModelOf(::Class)`?
- [ ] `viewModel { ... }` avoided unless explicitly needed and properly supported?
- [ ] New module registered before `appModule` in `initKoin`?
- [ ] Global order: `nativeModule → coreModule → [features] → appModule`?
