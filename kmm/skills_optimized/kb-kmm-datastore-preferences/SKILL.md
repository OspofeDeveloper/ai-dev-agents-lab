---
name: kb-kmm-datastore-preferences
description: "Knowledge base for using Preferences DataStore in KMM projects: shared factory, platform-specific path resolution, key ownership, and adapters over local storage."
effort: medium
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Preferences DataStore — Knowledge Base

## Rule 1: Preferences DataStore is local infrastructure, not a domain contract

`Preferences DataStore` is a technical key-value persistence mechanism. It does not define business rules or domain contracts.

Its responsibility is to:

- persist simple values
- expose reactive reads via `Flow`
- encapsulate local storage details

It must never become:

- a domain contract exposed directly across the app
- a substitute for a repository or store with its own semantics
- a place where auth, networking, or UI rules are mixed in

---

## Rule 2: The shared factory lives in `commonMain`

The base creation of `Preferences DataStore` must be centralized in a reusable common piece, typically built on `PreferenceDataStoreFactory.createWithPath`.

That shared piece:

- knows how to create the `DataStore<Preferences>`
- does not decide platform-specific paths
- has no Android or iOS dependencies

→ Templates: `references/preferences_datastore_templates.md`

---

## Rule 3: The physical path is resolved per platform

The actual file location belongs to the host.

The correct convention is:

- `commonMain` defines the shared factory
- `androidMain` resolves the path using `Context`
- `iosMain` resolves the path using native filesystem APIs

This skill does not absorb general platform-split rules; it only applies this criterion to its own mechanism.

→ Templates: `references/preferences_datastore_templates.md`

---

## Rule 4: `DataStore<Preferences>` is registered as a technical dependency

`DataStore<Preferences>` must be registered in DI as an infrastructure dependency.

Its registration:

- may live in `nativeModule` or equivalent when creation is platform-dependent
- does not replace the repository or adapter that exposes meaningful operations
- does not turn DI into the SSoT for ownership

Architectural placement and wiring are governed by:

- `kb-kmm-core-layer`
- `kb-kmm-feature-clean-architecture`
- `kb-koin`

---

## Rule 5: Keys must not be mixed into domain contracts without reason

`Preferences.Key<*>` are a technical persistence detail.

The preferred convention is:

- define them close to the adapter or storage module that uses them
- group them by functional or storage scope
- avoid placing them in domain interfaces if they add no value outside the implementation

Do not use a repository interface as a mere container for keys.

→ Templates: `references/preferences_datastore_templates.md`

---

## Rule 6: An adapter, store, or repository with explicit semantics must sit on top of DataStore

The raw `DataStore<Preferences>` must not propagate through all layers of the app.

A piece with clear intent must wrap it, for example:

- `SessionLocalDataSource`
- `SettingsStore`
- `UserPreferencesRepository`

That piece must:

- translate keys into meaningful operations
- centralize reads and writes
- decide whether to expose `Flow`, `suspend fun`, or both

---

## Rule 7: A piece belongs in `core` only if multiple features share it

DataStore integration should be promoted to `core` when:

- it persists state shared across multiple features
- it implements cross-cutting local infrastructure
- it is consumed by auth, app, or several distinct features

It must stay in a feature when:

- it only persists state owned by that feature
- its keys and operations have no meaning outside it

This skill sets the criterion for local storage. Final ownership decisions are governed by the layer skills.

---

## Rule 8: DataStore must not mix local storage with remote coordination

A single implementation must not combine without clear justification:

- local reads/writes via DataStore
- HTTP calls
- session refresh logic
- business rules

When a repository needs both, separate the local adapter from the higher-level coordination layer whenever the complexity warrants it.

This skill does not forbid all composition, but sets the preferred direction: local storage separate from remote integration.

---

## Rule 9: DataStore helpers and extensions belong to the local storage domain, not to networking

Extensions for reading and writing `String`, `Boolean`, or `Long` are local storage utilities.

They must live:

- alongside DataStore
- or in a local/shared persistence module

They must not be placed under networking or auth packages unless they are genuinely part of those responsibilities.

---

## Rule 10: This skill covers Preferences DataStore only — not Proto DataStore

This skill is scoped to `DataStore<Preferences>`.

It does not cover:

- Proto DataStore
- protobuf serializers
- typed schema migrations

If the project requires those decisions, they must live in a separate skill.

---

## Rule 11: This skill combines with layer, DI, and consumer skills

This skill is used alongside:

- `kb-kmm-core-layer` — to decide whether storage is cross-cutting
- `kb-kmm-feature-clean-architecture` — for feature-owned storage
- `kb-koin` — for wiring and registration
- `kb-kmm-auth-contracts` or feature skills — when auth or settings consume this mechanism

Do not duplicate auth, app state, or networking rules here. This skill only defines how to introduce Preferences DataStore behind a clean boundary.