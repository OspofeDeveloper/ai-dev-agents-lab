---
name: kb-kmm-navigation-viewmodel-events
description: "Knowledge base for navigation events and effects from ViewModel in KMM projects: Intent/Events pattern, Channel vs StateFlow, LaunchedEffect rules, and separation between business logic, Composable, and concrete destination."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Navigation ViewModel Events — Knowledge Base

## Rule 1: Business logic does not navigate; it emits effects

When navigation depends on a business condition, the ViewModel does not navigate directly. It emits an effect consumed by the Composable.

The concrete destination is still decided outside the ViewModel.

---

## Rule 2: Effects name facts, not concrete destinations

A navigation effect must express what happened:

- `LoginSuccess`
- `RegistrationRequired`
- `SessionExpired`

It must not encode global graph routes directly.

---

## Rule 3: The ViewModel separates renderable state from one-shot effects

The ViewModel has two distinct responsibilities and they must not collapse:

- `State`: lo que la pantalla puede renderizar de forma estable
- `Events`: efectos de una sola vez que la UI debe consumir

Practical rule:

- si algo cambia lo que la pantalla muestra de forma persistente, va en `State`
- si algo dispara una acción puntual como navegar, abrir diálogo o lanzar snackbar, va en `Events`

Do not use persistent state to model flow decisions that `app` must translate externally.

→ Patterns: `references/viewmodel-and-navigation-events.md`

---

## Rule 4: Renderable errors live in `State`; flow outcomes live in `Events`

Not every error is an effect.

When an error only changes the UI of the current screen, it must be represented as renderable screen state.

Typical examples:

- credenciales inválidas
- cuenta bloqueada
- error genérico de red mostrado en la propia screen

When the result represents a flow fact that may be translated differently by app, brand, or context, it must be emitted as an `Event`.

Typical examples:

- `LoginSuccess`
- `FirstLoginRequired`
- `AccountInactive`
- `SessionExpired`

The key difference is not whether something "is an error", but whether the consequence is locally renderable or requires an external composition/navigation decision.

---

## Rule 5: The ViewModel does not decide app-, brand-, or routing-dependent behavior

If one app navigates for a fact and another shows an error, that decision does not belong to the feature ViewModel.

The ViewModel emits the semantic fact once. `app` or the `NavHost` decides how to translate it:

- navegar a un destino
- mostrar snackbar o diálogo
- activar otra composición

This applies especially to brand, flavor, or global-context differences.

Ownership of that decision lives in `kb-kmm-app-layer`.

---

## Rule 6: Choose a single emission pattern per project

Typical options:

- `Channel` con entrega única
- `StateFlow` con reset manual

Choose one and apply it consistently. Do not mix patterns arbitrarily across equivalent screens.

→ Patterns: `references/viewmodel-and-navigation-events.md`

## Rule 7: Input events use `Intent` naming

When a screen models UI → ViewModel input, the preferred convention is `<Screen>Intent` as the input sealed interface.

The ViewModel exposes `onEvent(intent: <Screen>Intent)` as the single UI event entry point.

## Rule 8: Output effects use `Events` naming

When the pattern uses `Channel` or an equivalent stream for output effects, the preferred convention is `<Screen>Events`.

That type represents facts emitted from the ViewModel to the UI, not user inputs or concrete destinations.

## Rule 9: The `LaunchedEffect` key depends on the pattern

The correct key is not universal:

- con `Channel`, usar `LaunchedEffect(viewModel)`
- con `StateFlow` con reset, usar `LaunchedEffect(uiState.effect)`

`LaunchedEffect(Unit)` is invalid for this problem because it hides owner changes or relevant re-entries.

→ Patterns: `references/viewmodel-and-navigation-events.md`

## Rule 10: Navigation effects do not mix with `Intent`

`Intent` models input interaction.

Navigation effects model outputs or state consequences.

Mixing them increases the risk of duplicated events, incorrect collection, or repeated navigation after recomposition.

---

## Rule 11: The ViewModel must not know concrete destinations or navigation mechanisms

The ViewModel must not:

- recibir `NavController`, `Navigator` o equivalentes
- emitir rutas concretas, `Route`, `Destination` o ids del grafo global
- decidir `popBackStack`, `navigate`, `replace` o variantes concretas
- inyectar estrategias cuyo único propósito sea elegir una acción de app para un mismo hecho semántico

If an abstraction exists only to decide whether a fact triggers navigation, an error, or another composition, it belongs to `app`, not to the feature ViewModel.

---

## Rule 12: `State` models must be UI-semantic, not final render decisions

When an error or result lives in `State`, the preference is to model it as a UI-semantic type, not as final text or a navigation instruction.

Valid examples:

- `LoginError.InvalidCredentials(attemptsRemaining)`
- `LoginError.AccountBlocked`
- `LoginError.Generic`

Invalid as ViewModel SSoT:

- strings literales finales
- rutas
- decisiones de brand sobre qué hacer con el mismo outcome

The Screen may map that semantic state to `UiText`, resources, or concrete components.

---

## Rule 13: This skill does not define DI or the navigation library

This skill defines only the ViewModel ↔ Composable coordination pattern for navigation.

It does not define:

- `NavHost`
- rutas
- `NavController`
- Koin u otra DI

Concrete navigation lives in `kb-kmm-navigation-compose`.

## Checklist before close

- Does input event naming use `<Screen>Intent`?
- Does output effect naming use `<Screen>Events`?
- Does `State` contain only renderable data and not flow decisions?
- Are renderable errors in `State` and flow outcomes in `Events`?
- Is the same semantic fact emitted only once without brand-specific branching inside the ViewModel?
- Does each effect name a fact rather than a concrete destination?
- Does the ViewModel avoid `NavController`, routes, and app-dependent routing strategies?
- Does effect collection use the correct `LaunchedEffect` key for the chosen pattern?
