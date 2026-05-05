---
name: wf-kmm-network-setup
description: "Set up the networking layer in a KMM project by composing architecture rules, DI, and the chosen HTTP implementation without coupling the workflow to a single auth strategy."
argument-hint: "[HTTP stack, base URLs, environments, JSON conventions, and auth strategy if applicable]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-network-auth-implementer
---

# wf-kmm-network-setup

## Step 1: Gather structural decisions

Confirm with the user or infer from the project:

1. project base architecture and layer placement, following **Rule 2** of `kb-kmm-clean-architecture`
2. `core` rules, following **Rule 3** and **Rule 7** of `kb-kmm-core-layer`
3. feature microarchitecture, following **Rule 2** and **Rule 7** of `kb-kmm-feature-clean-architecture`
4. `app` rules, following **Rule 1** and **Rule 8** of `kb-kmm-app-layer`
5. active DI library, following **Rule 1** and **Rule 2** of the corresponding skill (`kb-koin` if applicable)
6. cross-cutting result/error contract, following **Rule 1** and **Rule 3** of `kb-kmm-app-errors`
7. chosen HTTP implementation, following **Rule 1** and **Rule 2** of the concrete skill (`kb-kmm-http-ktor` if applicable)
8. whether auth exists and which strategy it uses, following `kb-kmm-auth-contracts` and the applicable specific skill
9. backend conventions such as JSON discriminators, special errors, or multiple base URLs

Do not assume a concrete auth strategy just because networking is being configured.

---

## Step 2: Read the current project state

Read dependencies, DI modules, environment configuration, and the structure of `core/` and features to detect which contracts already exist and which pieces are missing.

---

## Step 3: Create stable contracts first

Apply:

- `kb-kmm-clean-architecture` -> **Regla 2**
- `kb-kmm-core-layer` -> **Regla 7** y **Regla 13**
- `kb-kmm-feature-clean-architecture` -> **Regla 7** y **Regla 12**
- `kb-kmm-app-layer` -> **Regla 8**
- `kb-kmm-app-errors` -> **Regla 1**, **Regla 5** y **Regla 6**
- `kb-kmm-network-contracts` -> **Regla 3**, **Regla 5**, **Regla 6** y **Regla 11**
- la skill de DI activa -> reglas de wiring, nunca ownership

Do not create auth-coupled mechanisms yet unless they are confirmed.

---

## Step 4: Implement the chosen HTTP library

If the stack is Ktor, apply `kb-kmm-http-ktor` for:

- Gradle dependencies
- required HTTP client or clients
- serialization
- logging
- timeouts
- Ktor-specific utilities
- without introducing DI or auth decisions that belong to other skills

Use **Rule 2**, **Rule 5**, and **Rule 10** of `kb-kmm-http-ktor` as anchors.

If the project already has a common remote wrapper, reuse it. Do not reimplement `try/catch` or manual status-code parsing inside each `Api`.

**Before writing a version in `libs.versions.toml`**, read the file and check whether a `ktor` entry already exists. If it does, use that version; do not overwrite it with a default one.

If the stack is not Ktor, use the equivalent skill and do not mix this workflow's criteria with a different library.

---

## Step 5: Integrate auth only if it is in scope

If the project requires authentication:

- apply `kb-kmm-auth-contracts`, especially its separation between policy and mechanism
- apply the corresponding OAuth provider skill if it exists
- apply the concrete HTTP-client integration mechanism skill only if it is confirmed

If an endpoint needs rich errors or special HTTP contracts, solve them through the common-wrapper `responseHandler`, not with duplicated service logic.

---

## Step 6: Register in DI while preserving separation of responsibilities

Register clients, APIs, repositories, and configuration in the active DI without moving architecture or auth rules into the DI skill.

Placement before registration follows these rules:

- genuinely cross-cutting contracts or utilities -> `core`
- repositories, data sources, and services owned by a single feature -> inside that feature
- global composition or final wiring -> `app`

DI registration follows **Rule 1** and **Rule 10** of the active DI skill.

---

## Step 7: Report with clear separation

Report which contracts were created, which concrete implementations were chosen, and which parts remain open because they depend on provider or mechanism decisions.
