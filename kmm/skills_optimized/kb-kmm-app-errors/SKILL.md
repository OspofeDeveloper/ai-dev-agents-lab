---
name: kb-kmm-app-errors
description: "Knowledge base for the cross-cutting error and result contract in KMM projects: AppResult, AppError, error taxonomy ownership, and inter-layer adaptation rules."
effort: medium
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# kb-kmm-app-errors

## Rule 1: `AppResult<T, AppError>` is the preferred cross-cutting contract

Propagate success/failure between layers using a value-based typed contract, not propagated exceptions:
- `AppResult<T, AppError>` — cross-cutting result contract
- `AppError` — cross-cutting error contract
- concrete `AppError` implementations per technical or functional domain

Exact type names are not mandated, but the contract must be explicit, typed, and shared.

→ Templates: `references/app_error_contract_templates.md`

## Rule 2: Exceptions are not the primary inter-layer contract

Exceptions may exist inside libraries, adapters, or infrastructure details, but must not be the stable language between data, domain, and presentation.

Prohibited as stable app contracts:
- `kotlin.Result` as a project-wide standard
- `Throwable` or `Exception` exposed by repositories, use cases, or ViewModels
- exception hierarchies as a substitute for `AppError`

Exceptions are caught and normalized at the appropriate boundary. What flows upward is `AppResult` with `AppError`.

## Rule 3: `AppError` is a base contract; concrete taxonomies specialize by domain

`AppError` must not become a catch-all sealed class. Correct structure:
- `AppError` as the shared base contract
- domain-specific taxonomies that implement `AppError`

Valid examples: `NetworkError : AppError` · `AuthError : AppError` · `StorageError : AppError` · `FeatureXError : AppError` (if scoped to one feature)

The UI consumes `AppError`; lower layers supply concrete variants.

→ Templates: `references/app_error_contract_templates.md`

## Rule 4: An error lives in `core` only if its meaning is cross-cutting

Lives in `core` if: used by multiple features · represents shared infrastructure or common domain · meaning is feature-independent.

Lives inside a feature if: applies only to that feature · expresses domain-specific rules or validations · has no value outside it.

Ownership criteria are set here. Concrete location is supported by `kb-kmm-core-layer` and `kb-kmm-feature-clean-architecture`.

## Rule 5: The remote boundary normalizes to `AppResult<T, AppError>`

The HTTP boundary: catches technical exceptions · parses error bodies if needed · maps details to a concrete `AppError` implementation · returns `AppResult<T, AppError>`.

Repositories must not receive `HttpResponse`, `Throwable`, or `ResponseException` as a stable contract.

## Rule 6: The repository preserves the error unless there is a semantic reason to adapt it

Default behavior: transform `Success` to domain · pass `Error` up unchanged.

Adapt an error only when its business meaning changes at a boundary. Valid cases:
- collapsing multiple technical errors into a shared business error
- translating a remote error to a feature-specific taxonomy with distinct semantics
- prioritizing a specific variant when combining multiple sources

Do not remap errors by convention or duplicate taxonomies without purpose.

## Rule 7: Use cases transform errors only when it is business logic

A use case may propagate `AppResult` as-is · combine multiple `AppResult` · prioritize errors · translate a technical error to a business one — but only when the transformation expresses a business rule or application policy. Otherwise the error passes through unchanged.

## Rule 8: The ViewModel reacts to `AppError`; it does not interpret technical details

The ViewModel consumes the cross-cutting error contract and decides its impact on screen state: show feedback · activate retry · expose `UiText` · emit a side effect.

Must not know: HTTP codes · client exceptions · raw error bodies · transport internals.

## Rule 9: `AppError → UiText` mapping lives in presentation

Infrastructure produces a concrete `AppError` → repository/use case propagates or adapts → presentation converts to `UiText` or equivalent.

Neither networking nor domain should produce visual messages as a primary contract.

→ Templates: `references/app_error_contract_templates.md`

## Rule 10: A backend string is not yet a UI policy

A backend text message may be used as: input for a concrete `AppError` implementation · dynamic text in presentation, if the project explicitly allows it.

The decision to display, replace, or translate it belongs to presentation/UI.

## Rule 11: This skill defines the cross-cutting contract; other skills define local variants

Combine with:
- `kb-kmm-network-contracts` — network error variant and remote boundary
- `kb-kmm-auth-contracts` — session and auth policies
- `kb-kmm-feature-clean-architecture` — ownership and adaptation within a feature
- `kb-kmm-ui-text` — visual error representation
- `kb-kmm-core-layer` — when a taxonomy belongs in `core`

Other skills must not redefine what `AppError` is or how `AppResult` is used as a cross-cutting contract — they must delegate.