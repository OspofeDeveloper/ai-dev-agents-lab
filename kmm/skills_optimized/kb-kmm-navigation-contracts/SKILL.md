---
name: kb-kmm-navigation-contracts
description: "Knowledge base for navigation contracts in KMM projects: app/feature ownership, routes as a central contract, NavController encapsulation, and separation between navigation, features, and composition."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Navigation Contracts — Knowledge Base

## Rule 1: Navigation is an `app` composition decision

Concrete navigation belongs to `app`, not to features.

`app` decides: which graph exists · which destination is activated · how feature exits are resolved · how the navigation shell is composed.

Aligned with: `kb-kmm-app-layer` · `kb-kmm-clean-architecture`

---

## Rule 2: Features emit exits; they do not navigate directly

A feature does not receive the `NavController` or decide concrete routes.

The feature: exposes exit callbacks · emits navigation facts or domain effects · delegates concrete destination resolution to `app`.

This keeps the feature decoupled from the global graph.

---

## Rule 3: The route contract is central and shared

Routes or destinations form a central navigation contract accessible from `app`.

Features do not depend on each other to navigate. If a feature needs to exit toward another, it expresses that through a callback or effect — never by importing the concrete destination directly.

---

## Rule 4: The `NavController` is encapsulated

The `NavController` or equivalent lives in the top-level composable shell or in the graph owner.

It must not: be exposed to features · be stored in a global `CompositionLocal` · become part of domain state.

---

## Rule 5: Routes are the contract; the concrete mechanism lives elsewhere

This skill defines the architectural navigation contract: ownership · boundaries · flow between `app` and features.

It does not define how that contract is implemented with a concrete library.

Compose Navigation implementation lives in `kb-kmm-navigation-compose`.

---

## Rule 6: Navigation effects are a different contract from the graph

When navigation depends on business logic, the ViewModel emits a navigation effect or event.

How that effect is modeled in ViewModel/Composable lives in `kb-kmm-navigation-viewmodel-events`, not here.

---

## Rule 7: Navigation must not break feature independence

Features: do not know other features' routes · do not depend on each other to navigate · do not share `NavController`.

Composition between features is resolved from `app`.
