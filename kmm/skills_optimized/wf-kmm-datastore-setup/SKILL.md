---
name: wf-kmm-datastore-setup
description: "Set up Preferences DataStore in a KMM project by composing layered architecture, DI wiring, and platform providers without mixing local storage with auth or networking."
argument-hint: "[storage scope, target module, active DI, expected consumers]"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-platform-integrator
---

# wf-kmm-datastore-setup

## Step 1: Confirm ownership and consumers

Before creating anything, confirm or infer:

1. whether the storage is cross-cutting (`core`) or feature-owned
2. which consumer uses it: auth, settings, app state, or a concrete feature
3. which DI is active, following `kb-koin` if applicable
4. which platforms are active and how native dependencies are resolved

Apply:

- `kb-kmm-core-layer`
- `kb-kmm-feature-clean-architecture`
- `kb-kmm-datastore-preferences`

---

## Step 2: Create the shared technical base first

Create the shared `Preferences DataStore` piece in `commonMain`, following **Rule 2** and **Rule 10** of `kb-kmm-datastore-preferences`.

This includes:

- shared factory
- filename
- genuinely shared utilities, if needed

Do not introduce business keys or auth logic yet.

---

## Step 3: Create platform providers

Implement physical path resolution per platform, following **Rule 3** of `kb-kmm-datastore-preferences`.

In particular:

- `androidMain` uses `Context`
- `iosMain` uses native filesystem APIs

Do not mix repository wiring or domain consumers here.

---

## Step 4: Create keys and an adapter with explicit semantics

Create a clearly-intended piece on top of `DataStore<Preferences>`, following **Rule 5** and **Rule 6** of `kb-kmm-datastore-preferences`.

Valid examples:

- `SessionLocalDataSource`
- `SettingsStore`
- `UserPreferencesRepository`

Group keys alongside that piece or in a keys file within the same scope.

---

## Step 5: Keep local storage separate from remote coordination

If the final consumer also uses network or auth, do not mix by default:

- local persistence in DataStore
- remote calls
- session refresh

Follow **Rule 8** of `kb-kmm-datastore-preferences` and keep the local adapter separate from upper-layer coordination unless the project already has a clear reason not to.

---

## Step 6: Register in DI without turning DI into the normative source

Register:

- the `DataStore<Preferences>` provider
- the local adapter/store/repository that consumes it

Follow:

- `kb-koin` para el wiring
- la **Regla 4** de `kb-kmm-datastore-preferences`

If creation depends on platform, use `nativeModule` or the project's equivalent pattern.

---

## Step 7: Verify the final boundary

Check that the result satisfies:

- `DataStore<Preferences>` does not leak raw into upper layers
- keys are not mixed into domain contracts without need
- storage helpers do not live under network packages
- ownership (`core` vs feature) follows the layer skills

---

## Step 8: Report with clear separation

Report separately:

- shared DataStore technical base created
- platform providers created
- local adapter/store/repository created
- DI wiring performed
- consumers still pending connection
