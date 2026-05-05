---
name: wf-kmm-stack-setup-ktor-keycloak-koin
description: "Shortcut for setting up the common KMM stack based on Koin, Ktor, and OAuth with Keycloak by composing separate skills without turning them into a single mixed source."
argument-hint: "[APP_BASE_URL, IDS_BASE_URL, realm, client_id, grant types, environments, and optional use of $type]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-network-auth-implementer
---

# wf-kmm-stack-setup-ktor-keycloak-koin

## Step 1: Treat this workflow as composition, not as a normative source

This skill exists as a shortcut for the usual stack. It defines no new rules; it composes specialized skills.

---

## Step 2: Apply layer architecture rules first

Apply:

- `kb-kmm-clean-architecture` -> **Regla 2**
- `kb-kmm-core-layer` -> **Rule 7** and **Rule 13**
- `kb-kmm-feature-clean-architecture` -> **Rule 7** and **Rule 12**
- `kb-kmm-app-layer` -> **Rule 8**
- `kb-koin` -> **Rule 1**, **Rule 2**, and **Rule 10**

This decides:

- which pieces belong in `core`
- which pieces stay inside a feature
- which wiring or composition belongs to `app`
- how dependencies are registered in Koin

---

## Step 3: Apply stable contracts before concrete mechanisms

Apply:

- `kb-kmm-network-contracts` -> **Rule 3**, **Rule 5**, **Rule 6**, and **Rule 11**
- `kb-kmm-app-errors` -> **Rule 1**, **Rule 5**, and **Rule 6**
- `kb-kmm-auth-contracts` -> **Rule 2**, **Rule 3**, **Rule 4**, and **Rule 7**
- `kb-kmm-auth-oauth-keycloak` -> **Rule 2**, **Rule 3**, **Rule 4**, and **Rule 5**

This fixes:

- cross-cutting result/error contract
- remote contract and error taxonomy
- session and refresh policy
- Keycloak-specific contract

Do not implement Ktor or the auth plugin before these contracts are settled.

---

## Step 4: Apply concrete technical implementations

Apply:

- `kb-kmm-http-ktor` -> **Rule 2**, **Rule 5**, and **Rule 10**
- `kb-kmm-auth-ktor-plugin` -> **Rule 1**, **Rule 2**, **Rule 4**, and **Rule 7**

This implements:

- the HTTP edge with Ktor
- the technical automatic-auth integration over Ktor
- the two-client pattern if intercepted refresh requires it

Do not move auth-policy, OAuth-provider, or architectural-placement decisions into these skills.

---

## Step 5: Execute project setup

1. add the required Ktor, Koin, and auth dependencies
2. create shared contracts in `core` or feature-owned contracts as indicated by the layer skills
3. implement `IdentityApi` and the remaining Keycloak-specific pieces
4. implement the identity HTTP client and the app HTTP client
5. install the auth plugin in the app client when applicable
6. register dependencies in Koin without mixing contracts and implementations
7. verify that features consume only the authenticated client and do not coordinate refresh manually

Execution must explicitly respect:

- `kb-kmm-network-contracts` -> **Rule 6**
- `kb-kmm-auth-contracts` -> **Rule 7**
- `kb-kmm-http-ktor` -> **Rule 8** and **Rule 9**
- `kb-kmm-auth-ktor-plugin` -> **Rule 6** and **Rule 8**

---

## Step 6: Keep contract, provider, and mechanism explicitly separate

During execution, always distinguish these three dimensions:

- remote contract and session contract
- concrete OAuth provider, such as Keycloak
- technical mechanism used to apply auth in Ktor

If a decision changes when replacing Keycloak but not when replacing Ktor, it does not belong to `kb-kmm-auth-ktor-plugin`.

If a decision changes when replacing Ktor but not when replacing Keycloak, it does not belong to `kb-kmm-auth-oauth-keycloak`.

---

## Step 7: Report without mixing layers

Report in three blocks:

- contracts and structural rules applied
- concrete implementations chosen
- pending manual steps per environment or platform
