---
name: wf-kmm-auth-setup-keycloak
description: "Set up OAuth authentication with Keycloak in a KMM project by separating session contracts, OAuth provider logic, and the technical HTTP integration mechanism."
argument-hint: "[IDS_BASE_URL, realm, client_id, grant types, refresh strategy, HTTP mechanism]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-network-auth-implementer
---

# wf-kmm-auth-setup-keycloak

## Step 1: Treat this workflow as composition, not as a normative source

This skill sets up Keycloak auth by composing specialized skills.

It does not define new architecture, session, provider, or HTTP-mechanism rules.

---

## Step 2: Confirm architecture and ownership first

Apply:

- `kb-kmm-clean-architecture` -> **Regla 2**
- `kb-kmm-core-layer` -> **Regla 7** y **Regla 13**
- `kb-kmm-feature-clean-architecture` -> **Regla 7** y **Regla 12**
- `kb-kmm-app-layer` -> **Regla 8**
- `kb-kmm-app-errors` -> **Regla 1**, **Regla 5** y **Regla 6**

This decides:

- where the session contract lives
- which cross-cutting result/error contract the app uses
- which pieces are cross-cutting and belong in `core`
- which implementations belong to a concrete feature
- which final wiring/composition belongs to `app`

---

## Step 3: Confirm auth policy

Apply `kb-kmm-auth-contracts` to confirm:

- whether access token and refresh token exist
- how session expiry is detected
- which endpoints are public
- where the session contract or token store lives
- how auth integrates into `AppResult` / `AppError`

Use **Rule 2**, **Rule 3**, and **Rule 4** of `kb-kmm-auth-contracts` as anchors.

---

## Step 4: Confirm Keycloak-specific details

Apply `kb-kmm-auth-oauth-keycloak` and collect:

- `IDS_BASE_URL`
- `realm`
- `client_id`
- grant type de login
- grant type de refresh
- entornos y variaciones de configuración

Use **Rule 2**, **Rule 3**, and **Rule 4** of `kb-kmm-auth-oauth-keycloak` as anchors.

---

## Step 5: Detect the active HTTP mechanism

Detect whether the project uses Ktor or another HTTP library. Do not assume Keycloak implies Ktor.

---

## Step 6: Create contracts before implementations

Create or verify:

- session store or repository
- session events
- identity API
- internal token models

The location of these pieces must respect layer skills. Do not assume every auth contract automatically belongs in `core` without proving it is cross-cutting.

Separation between contract, provider, and implementation must follow **Rule 7** of `kb-kmm-auth-contracts`.

---

## Step 7: Implement the Keycloak provider

Create the `IdentityApi` implementation with form submission and token-endpoint path following `kb-kmm-auth-oauth-keycloak`.

Apply **Rule 2**, **Rule 3**, and **Rule 5** of that skill.

If the `Api` must parse rich login errors or handle special success responses, do it through the shared remote-wrapper `responseHandler` described in `kb-kmm-http-ktor`, not by duplicating `try/catch`.

---

## Step 8: Separate refresh mechanism from policy and provider

Keep these dimensions explicitly separate:

- session policy -> `kb-kmm-auth-contracts`
- OAuth provider -> `kb-kmm-auth-oauth-keycloak`
- technical mechanism -> HTTP skill or corresponding plugin

Do not mix provider decisions with mechanism decisions.

---

## Step 9: Implement the refresh mechanism

Only if the project uses Ktor and the agreed strategy is automatic client auth, apply `kb-kmm-auth-ktor-plugin`.

Use **Rule 1**, **Rule 2**, **Rule 4**, and **Rule 7** of `kb-kmm-auth-ktor-plugin` as anchors.

If the project uses another mechanism, implement the corresponding variant without introducing Ktor rules into this workflow.

---

## Step 10: Register and report

Register the pieces in DI while preserving separation between contracts, provider logic, and technical implementations.

Report separately:

- auth contracts created
- Keycloak integration created
- technical mechanism chosen to apply auth in requests
