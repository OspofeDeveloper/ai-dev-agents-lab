---
name: kb-kmm-model-boundaries
description: "Knowledge base for model boundary rules in KMM projects: nullable DTO policy, null cleanup at data-to-domain mapping, and default values for domain and presentation models."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Model Boundaries — Knowledge Base

## Rule 1: This skill defines model-boundary policy, not architecture or HTTP implementation

This skill defines how models should behave when crossing representation boundaries in a KMM project.

It governs:

- tolerance at the remote edge
- null cleanup when leaving `data`
- constructor ergonomics and stability for internal models

It does not define:

- feature folder structure
- repository placement
- HTTP client configuration
- DI wiring
- screen-state flow or navigation behavior

If a rule still applies when the HTTP library, DI library, or feature layout changes, it belongs here.

---

## Rule 2: DTOs are tolerant transport models

Request and response DTOs exist to describe the payload contract with external systems, not to assert internal invariants.

By default, DTO fields should be nullable when the value comes from a remote source that may omit it, send it as `null`, or evolve without coordination.

The goal is to make the transport layer tolerant to incomplete or inconsistent backend payloads instead of leaking those assumptions into domain or presentation.

This rule applies first to response DTOs. Request DTOs may stay non-null only when the app itself is the authoritative source of the value and the contract requires it.

---

## Rule 3: Domain and presentation models represent already-sanitized data

`domain` and `presentation` models should express the stable shape that the app wants to consume internally.

By default, internal models should not preserve accidental nullability inherited from transport unless `null` has real product meaning.

Therefore:

- remote nullability is absorbed at the edge
- domain models expose the cleaned representation
- presentation models receive already-clean values or intentionally meaningful nulls

If `null` remains in a domain or presentation model, that nullability must represent business or UI semantics, not backend inconsistency.

---

## Rule 4: Null cleanup happens in the `data` to `domain` mapper

The mandatory normalization point is the mapper that converts infrastructure models into domain models.

That mapper is responsible for:

- replacing nullable transport values with safe defaults
- filtering null elements from collections
- normalizing nested nullable structures
- deciding when missing data becomes a default, an empty value, or a controlled domain error

Do not defer remote null cleanup to use cases, ViewModels, or composables. Once data leaves `data`, the domain contract should already be coherent.

→ Templates: `references/model_boundary_templates.md`

---

## Rule 5: Domain models default to total constructors

By default, every parameter in a domain model should have a default value.

This supports:

- safe construction in tests and previews
- resilience during incremental mapping changes
- simpler state replacement and copy flows
- lower boilerplate when composing partial domain values

Defaults must still be semantically valid for the model. Use empty strings, empty collections, `false`, `0`, or nested default instances only when they preserve a meaningful internal invariant.

If a domain model cannot have a sensible default for a field, that is a signal to reconsider whether the type is actually modeling more than one state.

---

## Rule 6: Presentation models default to render-safe values

By default, every parameter in a presentation model or screen state should have a default value.

The purpose is to make UI state:

- easy to initialize
- safe to preview
- stable under recomposition
- tolerant of incremental feature loading

Defaults in presentation should optimize for render safety: empty text, empty lists, disabled flags, idle states, or `null` only when absence is a first-class UI state.

This rule applies to screen state and any dedicated UI model owned by `presentation`.

---

## Rule 7: Defaults do not replace meaning

Using defaults is a normalization strategy, not permission to erase semantics blindly.

When choosing a fallback, the mapper must preserve the meaning that matters to the product:

- use empty collections for absent lists when absence has no semantic difference
- keep nullable fields only when the distinction between missing and present matters
- escalate to a domain error when a missing value makes the payload unusable

A model should not keep nullable fields merely because the backend does.

---

## Rule 8: This skill is consumed by layer and networking skills

This skill provides the SSoT for model-boundary rules.

It should be combined with:

- `kb-kmm-network-contracts` for remote boundary rules
- `kb-kmm-feature-clean-architecture` for layer placement and mapper ownership
- `kb-kmm-core-layer` when the same policy applies to cross-cutting shared models

Those skills may reference this one, but should not duplicate its policy.
