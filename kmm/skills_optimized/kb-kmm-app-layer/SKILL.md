---
name: kb-kmm-app-layer
description: "Knowledge base for the app layer in KMM projects: composition root, navigation, feature composition, ephemeral screen state coordination, and brand/context-dependent decisions."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# App Layer KMM — Knowledge Base

## Rule 1: `app` is the composition root

`app` assembles pieces already defined in `features` and `core`. It decides how they connect — it does not redefine their internal logic. It may know multiple features because its job is to compose the final application.

## Rule 2: `app` contains no feature domain logic and no business screens

`app` must not absorb: business logic of a feature · repositories or use cases scoped to one feature · screens representing a feature domain · feature-specific domain models.

If a piece has its own functional semantics beyond composition, it does not belong in `app`.

## Rule 3: Global navigation lives in `app`

`app` defines: the navigation graph · global destinations · how feature callbacks connect to concrete routes · how routing changes per brand or context.

Features do not know routes or global navigation controllers.

## Rule 4: `app` translates feature facts into concrete navigation

Features emit facts, events, or effects. `app` decides what to do with them in terms of navigation and composition:
- feature expresses what happened
- `app` decides where to go or which composition to activate

This keeps features reusable and decoupled from any single navigation scheme.

## Rule 5: Feature composition is resolved in `app`

When a screen combines content from multiple features, the assembly decision belongs to `app`. It may: decide which features appear in a composed screen · pass slots or callbacks to an aggregator screen · include or omit sections per context.

Features must not import each other to resolve themselves.

## Rule 6: Brand, flavor, and global context decisions live in `app`

If a decision changes per brand, flavor, environment, or global app condition, its natural place is `app`. Typical cases: different routing per brand · different screen composition per brand · selection of a concrete implementation in the composition root.

Features must not know these variants except through already-resolved cross-cutting contracts.

## Rule 7: A ViewModel in `app` only coordinates ephemeral composed-screen state

An `app` ViewModel is valid only when coordinating ephemeral UI state across multiple sections of a single composed screen: temporary UI state between features · composition callbacks · state that belongs to no single feature.

Not valid: moving business logic out of features or hiding a poorly modelled feature.

## Rule 8: `app` wires implementations; it does not define shared domain contracts

The contract lives in `core` or the relevant feature. A concrete implementation may be chosen or assembled from `app` if the decision is compositional. `app` selects and connects — it does not define shared structural truth.

## Rule 9: `app` does not substitute `core`

If a piece becomes reusable, stable, and shared across multiple features, evaluate whether it belongs in `core`. `app` must not accumulate: shared contracts · cross-cutting domain models · reusable logic across multiple contexts · general-purpose infrastructure. These turn `app` into a pseudo shared-domain layer.

## Rule 10: `app` does not substitute a feature

When a piece grows in functional complexity and stops being mere composition, migrate it to a real feature.

Drift signals: a screen in `app` develops its own business logic · an `app` ViewModel starts orchestrating use cases for a concrete domain · states, events, and effects already describe a complete functional domain.

## Rule 11: `app` optimises assembly clarity

Reading `app` should make clear: which destinations exist · which feature handles each destination · how aggregated screens are composed · where global brand or context decisions are made.

If understanding the global composition requires inspecting multiple mutually coupled features, architectural clarity is breaking down.

## Rule 12: This skill defines conceptual rules only

Not defined here: concrete navigation APIs · DI libraries · implementation details. If a rule depends on Koin, Voyager, Navigation Compose, or any concrete library, it does not belong here.

- Global architecture skill → relationship between `app`, `features`, and `core`
- Feature skill → internal microarchitecture of each feature
- DI skill → dependency registration
- Concrete navigation skill → operational details if the stack requires them