---
name: kb-kmm-feature-clean-architecture
description: "Knowledge base for the internal architecture of a KMM feature: presentation/domain/data layers, contract and implementation placement, allowed dependencies, and criteria for promoting responsibilities to core."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Feature Internal Architecture — Knowledge Base

## Rule 1: This skill defines a feature's micro-architecture, not the global project architecture

This skill governs how each feature is organized internally. It defines sublayers, ownership, allowed dependencies, and the separation between contracts and implementations within a single feature.

It does not define:

- global rules between `app`, `features`, and `core`
- DI decisions
- HTTP libraries
- global auth or navigation policy

If a rule holds true regardless of where the feature sits in the global architecture, it belongs here. If it affects the relationship between `app`, `features`, and `core`, it belongs in the global architecture skill.

---

## Rule 2: A feature is organized into layers internally

Each feature may be structured into three conceptual sublayers:

- `presentation`: Screen, Section, ViewModel, state, events, effects, and UI mappers
- `domain`: feature-owned domain models, repository contracts, and use cases
- `data`: repository implementations, remote APIs, DTOs, response handlers, and infrastructure-to-domain mappers

The exact folder structure may vary by project, but the separation of responsibilities must not.

When a screen uses a ViewModel, the project's preferred convention is to split it as:

- `presentation/<screen>/<Screen>Screen.kt`
- `presentation/<screen>/viewmodel/<Screen>ViewModel.kt`
- `presentation/<screen>/viewmodel/<Screen>State.kt`
- `presentation/<screen>/viewmodel/<Screen>Intent.kt`
- `presentation/<screen>/viewmodel/<Screen>Events.kt`

→ Templates: `references/presentation_viewmodel_patterns.md`

---

## Rule 3: Internal dependencies point toward domain

The correct dependency direction within a feature is:

```text
presentation -> domain <- data
```

Therefore:

- `presentation` may depend on `domain`
- `data` may depend on `domain`
- `domain` must not depend on `presentation` or `data`

The feature must not collapse these layers into a single unit in a way that erases important conceptual boundaries.

---

## Rule 4: `presentation` handles only UI state and coordination

The `presentation` layer contains the screen representation and its immediate coordination:

- `Screen` or `Section`
- `ViewModel`
- screen state
- UI → ViewModel input events
- ViewModel → UI output effects
- domain-to-presentation model transformations when needed for rendering

When a screen ViewModel exists, the project's preferred conventions are:

- `<Screen>State` for screen state
- `<Screen>Intent` for UI → ViewModel input events
- `<Screen>Events` for ViewModel → UI output effects
- `fun onEvent(intent: <Screen>Intent)` as the single entry point of the ViewModel

When state is held directly in the ViewModel, the preferred form is `var state by mutableStateOf(...)` with `private set`.

The exact split between `State`, `Intent`, and `Events` — including which outcomes must be emitted as effects and which decisions the ViewModel is not allowed to make — is delegated to `kb-kmm-navigation-viewmodel-events`.

`presentation` must not contain:

- network access or persistence logic
- DTOs
- HTTP client or storage implementation details
- global navigation decisions outside callbacks or effects

---

## Rule 5: The ViewModel does not talk to infrastructure

The ViewModel consumes use cases or domain contracts from the feature. It has no knowledge of concrete implementations or technical details from `data`.

Derived rules:

- it must not depend on data sources
- it must not depend on DTOs
- it must not build network requests or interpret HTTP responses
- it must not contain logic that belongs in repositories or infrastructure mappers

If the ViewModel starts resolving too many business rules, a use case or domain abstraction is missing.

---

## Rule 6: `domain` holds the feature's stable rules

The `domain` sublayer defines what the feature needs to express its business logic without coupling to how data is fetched or persisted.

It may contain:

- feature-owned domain models
- feature repository interfaces
- feature use cases
- feature-specific domain errors, where applicable

It must not contain:

- DTOs
- library-specific annotations or types from the infrastructure layer
- concrete repository implementations
- models designed solely for UI rendering

The criteria for when a feature-specific error should exist and how it relates to `AppError` are delegated to `kb-kmm-app-errors`.

---

## Rule 7: Repositories are a contract in `domain` and an implementation in `data`

Within a feature, the repository is split into two pieces:

- interface in `domain`
- implementation in `data`

The interface expresses operations in domain terms. The implementation knows about data sources, mappings, caching, persistence, and source composition.

Upper layers must never depend on the concrete implementation.

---

## Rule 8: `data` encapsulates external sources and technical details

The `data` sublayer contains everything needed to fulfill `domain` contracts:

- concrete repositories
- remote APIs
- local data sources
- DTOs, persistence entities, or transport models
- response handlers for special HTTP contracts, when needed
- infrastructure-to-domain mappers

`data` may depend on `domain` and on shared infrastructure. It must not leak its technical types into `presentation` or `domain`.

When remote HTTP access exists, the `Api` is the only `data` piece that touches the HTTP client. The repository consumes it and adapts the result to domain.

If an HTTP `responseHandler` becomes non-trivial, it may be extracted to `data/responseHandlers/` to separate request-building from special contract parsing.

→ Templates: `references/feature_remote_data_patterns.md`

---

## Rule 9: Remote services speak DTO; the feature speaks domain

Internal feature boundaries must preserve this separation:

- APIs consume and return DTOs or technical models
- repositories convert those models to domain
- use cases and the ViewModel work with domain models

If a DTO reaches the ViewModel or the Screen, the boundary between `data` and `domain` is broken.

The nullability policy for DTOs and the cleanup required before entering `domain` are delegated to `kb-kmm-model-boundaries`.

If the project uses a cross-cutting result/error contract (`AppResult<T, AppError>` or equivalent), that abstraction may cross the repository boundary and reach use cases and the ViewModel. What must not cross that boundary are DTOs, `HttpResponse`, status codes, or HTTP client exceptions.

The policy for when to preserve an error and when to adapt it is delegated to `kb-kmm-app-errors`.

---

## Rule 10: Mappers live at the point of representation change

Each mapper must live where one representation is transformed into another:

- DTO → domain in `data`
- domain → UI model in `presentation`, only if that UI model genuinely exists
- `AppError` → `UiText` in `presentation`, when the UI needs to render it

Do not mix infrastructure and UI transformations in the same mapper.

The default-value policy for `domain` and `presentation` models is delegated to `kb-kmm-model-boundaries`. Each layer converts toward the representation it needs.

When data crosses layer boundaries and represents a clear semantic unit, the project preference is to encapsulate it in a layer-specific model rather than passing it as loose variables:

- `UiModel` in `presentation`, when a composed input or state representation is needed
- `Model` in `domain`
- `Dto` in `data`

---

## Rule 11: Not everything requires a use case, but every business rule needs an explicit home

If an operation represents a business rule, multi-source coordination, or a meaningful transformation, it must live in a use case or an equivalent domain contract.

Do not create trivial use cases for ceremony, but do not leave business logic scattered across ViewModels or repositories without intent.

The practical rule is:

- source access and orchestration → repository
- business rule or action → use case
- screen state coordination → ViewModel

If an operation only needs to propagate `AppResult` from repository to ViewModel, the use case may be a simple pass-through. If it needs to combine multiple `AppResult` values, apply business rules, or prioritize errors, that logic belongs in the use case.

The cross-cutting `AppResult` / `AppError` policy is delegated to `kb-kmm-app-errors`.

---

## Rule 12: A feature retains only what belongs to its domain

Something must stay inside a feature if its use and meaning belong exclusively to that feature.

Something must be promoted to `core` when:

- multiple features consume it
- it represents a shared business model
- it is a cross-cutting use case
- it is reusable infrastructure with no feature-specific semantics

Do not promote pieces to `core` speculatively. They must first demonstrate that they are genuinely shared.

---

## Rule 13: Sharing code between features does not justify cross-feature dependencies

If Feature B needs a rule or piece of data that currently lives in Feature A, the solution is not to depend on Feature A.

Valid options are:

- extract the shared contract or model to `core`
- extract the shared repository or use case to `core`
- reassess whether both pieces are actually a single feature

Features must not reuse each other as if they were internal libraries.

---

## Rule 14: Navigation is not part of a feature's internal domain

A feature may emit events or effects to signal that something relevant happened, but it has no knowledge of routes, global destinations, or navigation controllers.

Therefore:

- effects describe facts, not concrete destinations
- the `Screen` exposes outward-facing callbacks
- the ViewModel does not receive a `Navigator` or `NavController`

This rule aligns the feature's micro-architecture with the global application architecture.

---

## Rule 15: Layers are optimized for clarity of responsibility, not empty ceremony

The split into `presentation`, `domain`, and `data` exists to protect change boundaries and keep the feature scalable.

It does not mandate an artificial number of files or types for small features. But even in simple features, these questions must have clear answers:

- where does UI logic live?
- where does the business rule live?
- where do technical details live?
- what contracts isolate the layers from each other?

If those answers are not obvious, the feature is not sufficiently well separated.

---

## Rule 16: This skill defines conceptual rules; other skills specify DI or infrastructure

This skill only establishes the internal micro-architecture of a feature.

- The global architecture skill defines how the feature fits into `app / features / core`
- The DI skill defines how its pieces are registered
- The networking, auth, and storage skills define the concrete technical contracts and implementations

If a rule depends on Koin, Ktor, SQLDelight, or any other library, it does not belong here.

---

## Pre-close checklist

- Does every screen with a ViewModel use `presentation/<screen>/viewmodel/` as the preferred location?
- Does the ViewModel expose `onEvent(intent)` as its single entry point?
- Does the screen state use `<Screen>State` and not a generic name inconsistent with the project convention?
- Does `presentation` avoid mixing in DTOs, data sources, or infrastructure details?