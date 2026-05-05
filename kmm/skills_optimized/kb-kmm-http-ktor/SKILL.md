---
name: kb-kmm-http-ktor
description: "Knowledge base for HTTP implementation with Ktor in KMM projects: HttpClient configuration, plugins, JSON serialization, logging, timeouts, relative paths, and Ktor-specific utilities."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Ktor HTTP — Knowledge Base

## Rule 1: This skill defines mechanism, not policy

This skill describes how to implement the HTTP client with Ktor. It does not define architecture rules, DI, or auth strategy on its own.

It implements the technical mechanism that fulfills the remote contract defined by `kb-kmm-network-contracts`.

When other decisions are needed, the relevant skills must be referenced.

It does not define:

- network error taxonomy
- stable remote contracts
- placement in `core` or a feature
- DI registration
- authentication strategy

---

## Rule 2: Standard HttpClient configuration

A Ktor `HttpClient` in KMM must configure, at minimum, the following when applicable to the project:

- `ContentNegotiation` with `Json`
- `Logging` with the project logger
- `DefaultRequest` for the base URL and common headers
- `HttpTimeout` for consistent timeouts

Plugin order must be explicit and consistent with the project strategy.

The concrete configuration must serve the project's remote contract — not redefine it.

→ Templates: `references/ktor_http_templates.md`

---

## Rule 3: Relative paths and centralized base URL

Remote services use relative paths. The base URL is configured in the client and must not be repeated in each service.

→ Templates: `references/ktor_http_templates.md`

---

## Rule 4: OAuth forms and similar endpoints use `submitForm`

When an endpoint requires `application/x-www-form-urlencoded`, the Ktor implementation uses `submitForm` instead of a JSON `setBody`.

---

## Rule 5: Ktor utilities live outside features

Helpers such as `tryCall`, the default `responseHandler`, exception mappers, and Ktor loggers live in `core/network` or equivalent. They must not be duplicated per feature.

These utilities implement the project's stable remote contract and must not invent a parallel contract that diverges from the one defined in `kb-kmm-network-contracts`.

→ Templates: `references/ktor_http_templates.md`

`tryCall` and its default `responseHandler` must return `AppResult<T, AppError>`. `NetworkError` is a concrete implementation of `AppError`, not the primary contract propagated across the app.

---

## Rule 6: Ktor logging delegates to the cross-cutting logger

The `Logging` plugin must not talk directly to a platform logging library. It must delegate to a shared project abstraction.

---

## Rule 7: Optional JSON conventions are applied per client

Options such as `ignoreUnknownKeys` or `classDiscriminator = "\$type"` belong to the specific client configuration. If an API does not need a given convention, it must not be applied by default.

---

## Rule 8: Auth strategy is not defined here

If the project uses automatic Bearer tokens, refresh token logic, or multiple clients, refer to:

- `kb-kmm-auth-contracts`
- `kb-kmm-auth-oauth-keycloak` if applicable
- `kb-kmm-auth-ktor-plugin` if the mechanism uses Ktor plugins

---

## Rule 9: This skill implements the remote edge, not the domain adaptation

Ktor covers the remote boundary:

- builds requests
- executes HTTP calls
- applies serialization
- translates exceptions and responses to the agreed remote contract

Transforming that remote contract into domain models belongs to the repository and is governed by:

- `kb-kmm-network-contracts`
- `kb-kmm-feature-clean-architecture`
- `kb-kmm-core-layer` if the piece is cross-cutting

When a feature defines its own HTTP piece, the project's preferred name for that boundary is `<Feature>Api`.

---

## Rule 10: `tryCall` centralizes exceptions; `responseHandler` is injectable for special HTTP contracts

`tryCall` catches all Ktor client exceptions and normalizes them to `AppError`. It is the single point where `ConnectTimeoutException`, `SocketTimeoutException`, `JsonConvertException`, and similar exceptions are handled.

`HttpResponse` interpretation is not fixed: `tryCall` accepts a `responseHandler` parameter that can be replaced when an endpoint needs to handle non-standard success codes (`202`, `204`, etc.), parse rich error bodies, or return a taxonomy other than `NetworkError`.

- `defaultResponseHandler` is the default implementation: resolves the common case (`2xx → body<T>()`) and maps HTTP errors to `NetworkError`
- alternative handlers are used from the feature `Api` or from `core/network/` and return `AppResult<T, AppError>`
- if a handler is trivial, it may remain private in the `Api`; if it has its own logic or grows, the preference is to extract it to `data/responseHandlers/`
- `Api` classes must not repeat status-code-by-status-code parsing outside their specific `responseHandler`

→ Templates: `references/ktor_http_templates.md`

---

## Pre-close checklist

- Does every HTTP call in the `Api` use `tryCall` as the common wrapper?
- Is manual `try/catch` and status code parsing avoided inside the `Api`?
- Are special endpoint HTTP contracts resolved via `responseHandler` rather than reimplementing the wrapper?
- Does the `Api` return DTOs or technical models — not domain models?
- Are non-trivial `responseHandler` instances extracted from request-building once they have their own substance?
- Is the `Api` still the only `data` piece that touches the HTTP client?