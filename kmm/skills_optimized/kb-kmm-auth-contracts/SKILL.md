---
name: kb-kmm-auth-contracts
description: "Knowledge base for authentication contracts in KMM projects: tokens, refresh, session expiry, public endpoints, and separation between auth policy and transport mechanism."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Auth Contracts KMM — Knowledge Base

## Rule 1: Auth is a cross-cutting policy

Auth defines session and access rules, not the concrete technology implementing them. This skill describes the stable policy regardless of Ktor, OAuth provider, or DI changes.

Contract location is decided by layer skills:
`kb-kmm-core-layer` (cross-cutting) · `kb-kmm-feature-clean-architecture` (single feature) · `kb-kmm-app-layer` (wiring/composition only)

## Rule 2: Explicit token and session contract

If the project uses access and refresh tokens, a clear contract must exist for: reading and storing access token · reading and storing refresh token · knowing access/refresh token expiry · clearing the session · emitting session-expired events when applicable.

Login, refresh, and session read operations that return a result use `AppResult<T, AppError>` as the preferred convention. The cross-cutting definition of `AppResult`/`AppError` belongs to `kb-kmm-app-errors` — this skill only defines how auth integrates with that contract.

→ Templates: `references/auth_contracts_templates.md`

## Rule 3: Automatic refresh is a policy, not a client detail

If the access token expires and a valid refresh token exists, the system attempts renewal before considering the session lost. How that refresh is implemented belongs in a concrete implementation skill.

Refresh must not invent a different error contract. On failure it returns `AppError` and lets the technical mechanism or upper layer react accordingly.

## Rule 4: Public vs authenticated endpoints

The project must be able to distinguish public from authenticated endpoints. The concrete convention for bypassing auth depends on the technical mechanism used.

## Rule 5: Consumers do not know about internal refresh

Use cases, ViewModels, and feature services must not manually coordinate the refresh cycle if the project strategy automates it — they consume the already-authenticated API.

## Rule 6: OAuth providers are implementation variants

Keycloak, Auth0, or any other provider do not change the general session policy. Provider-specific details belong in a separate skill.

## Rule 7: This skill defines session policy; other skills define provider and mechanism

Combine with:
- `kb-kmm-app-errors` — cross-cutting result and error contract
- `kb-kmm-auth-oauth-keycloak` (or equivalent) — OAuth provider specifics
- `kb-kmm-auth-ktor-plugin` (or equivalent) — technical mechanism
- layer skills — location and ownership decisions

Do not duplicate provider, HTTP client, or DI rules here.