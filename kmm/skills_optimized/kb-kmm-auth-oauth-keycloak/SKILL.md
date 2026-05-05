---
name: kb-kmm-auth-oauth-keycloak
description: "Knowledge base for OAuth with Keycloak in KMM projects: token endpoints, required parameters, grant types, form-urlencoded payloads, and per-environment configuration."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# OAuth Keycloak KMM — Knowledge Base

## Rule 1: Keycloak is a concrete OAuth provider

This skill defines only what is specific to Keycloak. Session persistence and HTTP client integration are not defined here.

## Rule 2: The token endpoint depends on the realm

```text
/realms/{realm}/protocol/openid-connect/token
```

`realm` comes from project or environment configuration — never hardcoded in the implementation.
→ Templates: `references/keycloak_auth_templates.md`

## Rule 3: Login and refresh use form encoding

Requests are sent as `application/x-www-form-urlencoded` via `submitForm` or equivalent.
Required params: `grant_type` · `client_id` · `username` + `password` (login) · `refresh_token` (refresh)
→ Templates: `references/keycloak_auth_templates.md`

## Rule 4: Grant types are configuration, not scattered literals

Values like `password` or `refresh_token` must come from centralized constants or configuration — not repeated across features.

## Rule 5: Keycloak responses are normalized

Keycloak token DTOs are mapped to the project's internal model before being consumed by other layers.

## Rule 6: This provider does not define automatic refresh

This skill covers the Keycloak contract only. For automatic refresh within Ktor, see `kb-kmm-auth-ktor-plugin`.