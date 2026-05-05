---
name: kb-kmm-auth-ktor-plugin
description: "Knowledge base for automatic authentication implemented with Ktor plugins in KMM projects: two HTTP clients, auth plugin, public endpoint bypass, and transparent token refresh."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Auth Ktor Plugin KMM — Knowledge Base

## Rule 1: This skill implements the automatic auth mechanism over Ktor

Concrete implementation. Depends on:
`kb-kmm-auth-contracts` (session policy) · `kb-kmm-http-ktor` (HTTP mechanism) · `kb-koin` or active DI skill (dependency registration)

Not defined here: general session policy · OAuth provider contract · global error taxonomy · architectural layer location · concrete DI library.

## Rule 2: Two-client pattern when refresh uses an independent HTTP call

If the refresh token is executed from within the intercepted HTTP mechanism, use two separate client instances:
- **Identity client** — login and refresh against the OAuth provider
- **App client** — main API with automatic authentication

Separation prevents recursion or circular dependencies during refresh.
→ Templates: `references/ktor_auth_plugin_templates.md`

## Rule 3: Auth plugin in the app client

The authenticated client installs a plugin that:
1. detects bypass for public endpoints
2. reads stored tokens
3. checks expiry
4. attempts refresh if applicable
5. injects the Bearer token if present
6. emits a session-expired event if the refresh is no longer valid

→ Templates: `references/ktor_auth_plugin_templates.md`

## Rule 4: Public endpoint bypass convention

If a public endpoint is called through the authenticated client, an explicit convention must exist to skip auth. A typical implementation uses a technical header such as `No-Auth: true`, which the plugin removes before sending the request.

## Rule 5: The plugin may require controlled blocking

Ktor's plugin API may require `runBlocking` to read flows or execute refresh inside hooks like `onRequest`. This detail is specific to this implementation.

If the refresh operation returns a result, the preferred convention is `AppResult<TokenInfo, AppError>`. The plugin reacts to `onSuccess`/`onError` — no special contract beyond the rest of the project is needed. The cross-cutting definition of `AppResult`/`AppError` belongs to `kb-kmm-app-errors`.

## Rule 6: Feature services consume the authenticated client only

Features consume the main client. Only the identity provider implementation uses the secondary Identity client.

## Rule 7: This skill automates refresh; it does not define the provider or session contract

The Ktor plugin only orchestrates: reading session state · deciding whether to attach a token or attempt refresh · bypassing public endpoints · emitting technical behaviour when the session is unrecoverable.

Session semantics, expiry, and OAuth provider belong to:
`kb-kmm-app-errors` · `kb-kmm-auth-contracts` · provider skill (e.g. `kb-kmm-auth-oauth-keycloak`)

## Rule 8: DI integration and configuration are external to the plugin

The plugin needs dependencies such as session store, refresh function, or base URLs — this skill does not impose how they are resolved. Concrete resolution via DI, factories, or manual wiring belongs to the active DI skill or the project's composition root.