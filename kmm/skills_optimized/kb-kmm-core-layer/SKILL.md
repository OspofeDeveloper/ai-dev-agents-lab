---
name: kb-kmm-core-layer
description: "Knowledge base for the core layer in KMM projects: shared domain, cross-cutting infrastructure, criteria for promoting responsibilities from features, and rules to prevent core from becoming a dumping ground."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Core Layer — Knowledge Base

## Rule 1: `core` holds what is shared and stable

The `core` layer exists to host reusable, stable pieces that belong neither to a single feature nor to `app`-level composition.

Its value lies in centralizing truly cross-cutting contracts and capabilities without coupling them to any specific feature domain.

---

## Rule 2: `core` has no knowledge of specific features or application navigation

`core` must not depend on `features` or `app`, nor be aware of their composition decisions.

Therefore, `core` must never contain:

- global navigation destinations
- feature screens or ViewModels
- rules that reference specific features
- brand-dependent composition resolved at the app level

If a piece needs to know about a specific feature in order to exist, it does not belong in `core`.

---

## Rule 3: `core` holds two kinds of truth — shared domain and shared infrastructure

Valid responsibilities in `core` generally fall into two categories:

- **Shared domain:** models, contracts, and use cases consumed by multiple features
- **Shared infrastructure:** networking, storage, logging, resources, technical configuration, and other cross-cutting capabilities

Both are valid, but they must not be mixed carelessly within the same unit.

---

## Rule 4: Shared domain in `core` must be genuinely cross-cutting

A model or use case belongs in `core` only if multiple features need it with the same meaning.

Valid signals for promoting something to `core`:

- multiple features consume the same repository or contract
- multiple features share the same business model
- multiple features rely on the same rule or use case

Nothing should be promoted to `core` out of anticipation or for one-off convenience.

---

## Rule 5: Shared infrastructure in `core` must be decoupled from feature domains

Shared technical pieces in `core` exist to provide reusable capabilities, not to encode rules belonging to a specific feature.

Typical examples:

- networking
- local persistence
- logging
- resources
- cross-cutting configuration
- reusable authentication contracts

If a technical piece is designed for a single feature, it must live close to that feature — even if it relies on infrastructure from `core`.

---

## Rule 6: `core` is not a dumping ground

Not everything that has no obvious home belongs in `core`.

The following must not enter `core`:

- generic utilities with no clear ownership
- invented abstractions with no real consumers
- logic extracted prematurely
- pieces moved only to reduce imports or avoid reasoning about the correct domain

Moving something to `core` without a clear architectural reason merely shifts the mess to a layer that is harder to clean up.

---

## Rule 7: A contract moves to `core` when multiple features depend on it — not when only one does

If a repository, model, or use case serves a single feature, it must stay in that feature.

Promote to `core` only when:

- it no longer belongs semantically to a single feature
- multiple features consume it naturally
- its meaning is already shared across the system

`core` must represent shared truth, not future possibilities.

---

## Rule 8: `core` shields features from repeated infrastructure details

Features may depend on `core`, but they should never have to reconstruct repeated details around networking, storage, auth, logging, or cross-cutting technical configuration.

`core` acts as a stabilization point for those capabilities, provided they are exposed through clear contracts or boundaries.

---

## Rule 9: `core` contracts must survive library changes

When a `core` piece defines a shared abstraction, that abstraction must not be contaminated by implementation details of a specific library — unless the skill is explicitly about a concrete technical implementation.

This applies especially to:

- networking contracts
- auth contracts
- abstracted persistence
- logging or telemetry

The stable part lives in `core`; the concrete implementation is specialized wherever appropriate.

---

## Rule 10: `core` may be organized internally by cross-cutting domains, not by features

The internal structure of `core` must reflect shared capabilities, for example:

- `domain/`
- `network/`
- `storage/`
- `resources/`
- `auth/`
- `brand/`

The exact organization may vary, but it must always express cross-cutting ownership — never dependency on specific features.

---

## Rule 11: `core` does not replace `app`

`core` does not decide global composition or application routing.

It is not responsible for:

- choosing which screen is displayed
- resolving composition of aggregate screens
- making brand-level navigation decisions
- acting as the composition root

When `core` starts assembling the app, the boundary with `app` has been broken.

---

## Rule 12: `core` does not replace features

`core` must not absorb rules that still belong to a single feature.

Warning signs:

- models whose name and meaning are tied to a single feature
- use cases used by one feature but moved "for cleanliness"
- repositories created in `core` without real multiple consumers

Doing so reduces feature cohesion and causes `core` to lose semantic precision.

---

## Rule 13: Promoting a piece to `core` requires demonstrating stability and reuse

Before moving something from a feature to `core`, verify:

- the piece carries the same meaning in more than one feature
- it will actually be consumed by multiple features, not just potentially
- it can live in `core` without referencing specific feature domains
- moving it genuinely improves the architecture rather than diluting ownership

If the answer is not clear, the piece should remain in the feature.

---

## Rule 14: `core` must have clear semantic ownership

Every piece in `core` must clearly answer one of these questions:

- What cross-cutting contract does it define?
- What shared capability does it provide?
- What common model does it represent?
- What reusable infrastructure does it encapsulate?

If it cannot be explained in a single sentence why something belongs in `core`, it probably does not.

---

## Rule 15: This skill defines only conceptual rules for the `core` layer

This skill does not cover concrete details of Koin, Ktor, SQLDelight, or any other technology.

- The global architecture skill defines the relationship between `app`, `features`, and `core`
- The features skill defines what must remain inside a feature
- The networking, auth, DI, and storage skills define contracts and implementations specific to each technical dimension

If a rule depends on a concrete library, it does not belong here.