---
name: kb-kmm-network-contracts
description: "Knowledge base for networking contracts in KMM projects: network errors, typed results, boundaries between remote services and repositories, and stable rules independent of the HTTP library."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Network Contracts KMM — Knowledge Base

## Rule 1: Separate the network contract from the HTTP implementation

Networking policy must survive an HTTP library change. This skill therefore defines stable concepts, not Ktor, Retrofit, or other implementation details.

Contract location is decided by layer skills:

- `kb-kmm-core-layer` when the contract is cross-cutting across multiple features
- `kb-kmm-feature-clean-architecture` when the contract belongs to a single feature

---

## Rule 2: This skill defines integration boundaries, not general layer architecture

This skill governs only the boundary between:

- HTTP client or remote API
- technical error/result contract
- repository that adapts the remote response to domain

It does not define:

- internal feature structure
- physical file placement
- HTTP client implementation
- dependency registration
- authentication behavior

If a rule still applies when the HTTP library changes, it belongs here. If it talks about folders, DI, Ktor, or concrete auth, it belongs elsewhere.

---

## Rule 3: The preferred contract is `AppResult<T, AppError>`

Remote operations do not expose raw exceptions to upper layers. They return a typed success/error result.

Preferred convention:

- `AppResult<T, AppError>` as the cross-cutting result contract
- `AppError` as the cross-cutting error contract
- `NetworkError` as the concrete `AppError` implementation for the network domain

Stable principle: upper layers do not interpret unnormalized transport exceptions, and networking integrates into the same result/error contract used by the rest of the project.

The cross-cutting `AppResult` / `AppError` definition belongs to `kb-kmm-app-errors`. This skill consumes it and specializes it for the remote edge.

→ Templates: `references/network_contracts_templates.md`

---

## Rule 4: `NetworkError` is a concrete `AppError` implementation

Transport and protocol errors map to a stable technical contract, for example:

- no connection
- serialization error
- unauthorized
- timeout
- conflict
- server error
- unknown error

The exact taxonomy may vary, but it must be unique and shared within the network domain.

In this convention:

- `AppError` is the base contract
- `NetworkError` implements `AppError`
- other domains may provide other concrete implementations (`BleError`, `CoreError`, etc.)

UI and upper domain layers work with `AppError`; networking contributes only one concrete variant within that contract.

General ownership, adaptation, and propagation policy for `AppError` belongs to `kb-kmm-app-errors`.

→ Templates: `references/network_contracts_templates.md`

---

## Rule 5: The remote API exposes technical models inside `AppResult`

The remote boundary speaks in transport/integration terms:

- DTOs
- HTTP payloads
- normalized network errors
- typed results using the project's cross-cutting contract

It does not expose domain models or raw HTTP client details upward.

---

## Rule 6: The repository adapts the remote contract to domain

The repository consumes the remote contract and adapts it to domain needs:

- transforms DTOs to domain models
- preserves or converts remote errors to the appropriate upper-layer contract
- hides HTTP client details from use cases and UI

This rule does not decide whether the repository lives in `core` or inside a feature. That decision belongs to layer skills.

Preferred pattern:

- the API returns `AppResult<Dto, AppError>`
- the repository transforms `Success` with `map { dto -> domain }`
- the error passes upward unchanged unless there is a clear business reason to adapt it

This avoids redundant remapping and preserves a single error taxonomy across the app.

---

## Rule 7: Base URL, global headers, and auth are not part of the stable remote contract

Base URL, global headers, automatic auth, and other client decisions belong to infrastructure.

This skill only fixes that those decisions must not contaminate the stable remote contract.

---

## Rule 8: Logging and observability stay behind abstractions

If the project logs network traffic, it must do so through a reusable abstraction (`AppLogger` or equivalent), not by coupling each service to a concrete logging library.

---

## Rule 9: JSON polymorphism and backend conventions are integration contracts

If the backend uses discriminators such as `"$type"`, custom error codes, or payload conventions, those rules belong to the network integration contract, not to architecture or DI.

---

## Rule 10: This skill defines remote contracts; other skills decide location and implementation

Combine with:

- `kb-kmm-app-errors` for the cross-cutting `AppResult` / `AppError` contract
- `kb-kmm-core-layer` to decide whether the contract is cross-cutting
- `kb-kmm-feature-clean-architecture` to decide how it integrates inside a feature
- `kb-kmm-http-ktor` to implement it with Ktor, if applicable
- auth skills for any authentication policy or mechanism

Do not duplicate rules that already belong to those dimensions.

---

## Rule 11: HTTP error normalization produces `AppResult<T, AppError>`

Reading HTTP codes, parsing error bodies, and mapping client exceptions belong to the remote edge, not to the repository or ViewModel.

Stable pattern:

- `tryCall` or an equivalent helper executes the call
- `responseHandler` or an equivalent helper transforms `HttpResponse` into `AppResult<T, AppError>`
- the repository consumes that already-normalized result

When a `responseHandler` stops being trivial or becomes specific enough to its own contract, it may be extracted to `data/responseHandlers/` instead of staying embedded in the `Api`.

The repository must not reinterpret status codes or parse backend error bodies.

## Rule 12: UI consumes a cross-cutting error, not an HTTP detail

Presentation layers should not know `HttpResponse`, status codes, or client exceptions.

Correct flow:

- ViewModel consumes `AppResult<Domain, AppError>` or equivalent
- presentation reacts through `onSuccess` / `onError`
- conversion to `UiText` or visual representation happens in presentation/UI

Networking contributes an error variant; UI consumes the project's cross-cutting contract.
