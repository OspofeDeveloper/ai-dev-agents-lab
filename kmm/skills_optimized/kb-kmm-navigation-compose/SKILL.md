---
name: kb-kmm-navigation-compose
description: "Knowledge base for navigation implementation with Compose Navigation + Kotlin Serialization in KMM: @Serializable routes, NavHost, nested graphs, back stack, graph deep links, adaptive shell, graph testing, and commonMain constraints."
argument-hint: "navigation topic to look up (optional)"
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Compose Navigation — Knowledge Base

## Rule 1: This skill implements the Compose graph — it does not define ownership or global contracts

This skill defines the concrete graph implementation using Compose Navigation and type-safe routes.

It does not define on its own:

- architectural ownership of navigation
- the contract between `app` and features
- the navigation effects pattern from the ViewModel
- platform integration with the host
- concrete DI

Those rules live in:

- `kb-kmm-navigation-contracts`
- `kb-kmm-navigation-viewmodel-events`
- `kb-kmm-navigation-platform-behaviors`
- `kb-koin` if applicable

---

## Rule 2: Setup and minimum dependencies are fixed per library

The implementation uses the Compose Multiplatform Navigation artifact and Kotlin Serialization in `commonMain`.

Minimum reference version: `org.jetbrains.androidx.navigation:navigation-compose:2.8+`.

The exact dependency and plugin configuration belongs in templates, not in this conceptual rule.

→ Templates: `references/setup-and-routes.md`

---

## Rule 3: Routes are type-safe and live in `commonMain`

All routes live in `commonMain`.

Each route is:

- an `object` if it carries no arguments
- a `data class` if it carries arguments
- a `@Serializable object` if it represents the root of a nested graph

Optional arguments must have a default value.

→ Templates: `references/setup-and-routes.md`

---

## Rule 4: Only multiplatform navigation APIs are used in `commonMain`

Arguments are extracted using `backStackEntry.toRoute<T>()`.

`SavedStateHandle.toRoute()` is forbidden in `commonMain` because it depends on AndroidX Lifecycle.

Complex arguments must cross the route as serializable primitives, not as platform objects.

→ Templates: `references/setup-and-routes.md`

---

## Rule 5: The `NavHost` lives in `commonMain` and shares its owner with the shell

The `NavHost` and the entire graph live in `commonMain`.

`AppNavGraph` receives the `navController` as a required parameter with no default. The owner is always the shell or the test that invokes it.

This guarantees the same `navController` is shared between the `NavHost` and the shell's navigation component.

Do not use `LocalNavController` as a `CompositionLocal` — it reduces testability and hides ownership.

→ Templates: `references/navhost-and-backstack.md`

---

## Rule 6: Back stack manipulation follows explicit flow criteria

The combination of `popUpTo`, `inclusive`, `launchSingleTop`, `saveState`, and `restoreState` is applied according to flow type:

- `inclusive = true` when the origin must not remain on the stack
- `launchSingleTop` for tab navigation
- `saveState` and `restoreState` in tab shells to preserve state

`popBackStack()` and `navigateUp()` are not semantically interchangeable. If a destination can be reached via deep link, ignoring the `Boolean` returned by `popBackStack()` is forbidden — an explicit fallback must exist.

→ Templates: `references/navhost-and-backstack.md`

---

## Rule 7: Nested graphs preserve the boundary between features and `app`

Navigating to a graph lands on its `startDestination`; navigating to a route lands on that specific destination.

Each feature exposes its graph registration via callbacks or exit lambdas.

The feature:

- does not receive the `NavController`
- does not know other features' routes
- does not decide global composition

Shared routes and the `NavController` remain centralized in `app`.

→ Templates: `references/nested-graphs-and-multimodule.md`

---

## Rule 8: The adaptive shell is a Compose runtime responsibility, not a navigation contract

Tab navigation always applies the options needed to avoid duplicates and preserve state.

The active item selection is synchronized with the current destination hierarchy.

In adaptive layouts:

- `NavigationBar` on compact
- `NavigationRail` on medium
- `NavigationDrawer` on expanded

The concrete shell implementation and its layouts live in templates.

→ Templates: `references/bottom-nav-and-adaptive.md`

---

## Rule 9: This skill resolves deep links within the graph — not host integration

This skill covers deep link resolution once the host delivers the event to the navigation runtime.

Platform configuration connecting URLs, intents, universal links, or native bridges belongs to `kb-kmm-navigation-platform-behaviors`.

URI placeholders must match the parameter names of the `@Serializable` route.

→ Templates: `references/deeplinks.md`

---

## Rule 10: ViewModel scoping and side effects are governed by their authoritative skills

The Compose graph may require ViewModel scoping and side effect consumption, but does not define their normative pattern.

For scoping and parameter passing, refer to the active DI and the authoritative navigation-from-ViewModel pattern.

For navigation effects and `LaunchedEffect`, the authoritative skill is `kb-kmm-navigation-viewmodel-events`.

→ Templates: `references/viewmodel-scoping.md`

---

## Rule 11: Graph testing belongs to the Compose implementation dimension

Graph and `NavHost` integration testing belongs here because it validates the concrete Compose Navigation implementation.

Isolated ViewModel tests remain under `kb-kmm-navigation-viewmodel-events`, not this skill.

→ Templates: `references/testing.md`

---

## Rule 12: Transitions are a `NavHost` implementation detail

Global transitions are defined in the `NavHost`; per-route transitions override the global ones.

On iOS, transitions compatible with Compose Multiplatform should be preferred. Predictive back animation does not make Android the source of truth for graph design.

→ Templates: `references/animations.md`

---

## Rule 13: Platform behaviors do not belong in this skill

`BackHandler`, predictive back, and host bridges do not live here.

If a decision depends on `AndroidManifest`, `AppDelegate`, `SceneDelegate`, universal links, or host APIs, delegate to `kb-kmm-navigation-platform-behaviors`.

---

## Rule 14: Non-negotiable requirements of this implementation

While the project uses Compose Navigation + Kotlin Serialization:

- routes must be type-safe with `@Serializable`
- `AppNavGraph` must receive the `navController` as a required parameter
- `SavedStateHandle.toRoute()` is forbidden in `commonMain`
- the return value of `popBackStack()` must not be ignored at deep link entry points
- the adaptive shell must respect compact/medium/expanded semantics