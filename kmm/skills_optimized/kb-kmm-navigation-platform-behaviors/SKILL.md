---
name: kb-kmm-navigation-platform-behaviors
description: "Knowledge base for navigation integration with platform-specific behaviors in KMM: BackHandler, predictive back, and deep-link host bridges."
argument-hint: "[back behavior | predictive back | platform deep links]"
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Navigation Platform Behaviors — Knowledge Base

## Scope

This skill defines navigation behaviors that depend on platform integration or host runtime. It specifies how Compose navigation connects to system events without redefining the graph, routes, or architectural ownership of navigation.

It does not define:
- the architectural navigation contract
- the ViewModel → side effect → callback pattern
- the Compose Navigation graph or type-safe routes
- the project's DI library

Delegate those concerns to:
- `kb-kmm-navigation-contracts`
- `kb-kmm-navigation-viewmodel-events`
- `kb-kmm-navigation-compose`
- `kb-koin` if applicable

## Rule 1: `BackHandler` is a platform behavior, not a graph rule

Using `BackHandler` belongs to host integration and screen lifecycle. It must not be modeled as part of the graph contract.

- Use `BackHandler` only when the screen must intercept the back gesture or button for a clear functional reason.
- The interception decision lives in the UI or a platform adapter, not in the ViewModel as a direct navigation call.
- The resulting action must delegate to callbacks or effects already defined by the project's navigation contract.

→ Templates: `references/backhandler.md`

## Rule 2: Predictive back is an Android-specific capability

Predictive back integration is an Android host detail and must remain separate from general graph design.

- Do not turn predictive back into a global requirement for all KMM navigation.
- Encapsulate integration in the Android host layer or specific adapters, keeping `commonMain` free of Android framework details.
- If a screen does not need special integration, use the default system behavior.

## Rule 3: Deep links are split between graph resolution and platform integration

Resolving a route inside the `NavHost` belongs to the Compose navigation implementation. The configuration that connects URLs, intents, universal links, or native bridges belongs here.

- The graph decides how a deep link is interpreted once it enters navigation.
- Android resolves `intent-filters` and delivers the link to the host.
- iOS resolves universal links, custom schemes, or equivalent bridges and delivers the link to the host.
- The platform must never become the source of truth for the destination catalog.

## Rule 4: The platform delivers events; `app` translates; features do not know the host

Navigation events coming from the system must enter through the host and be translated to the navigation contract defined in `app`.

- The platform captures the external event.
- `app` adapts it to a graph route or action.
- Features receive only the result of that composition; they do not know intents, native URLs, or system APIs.

## Rule 5: Platform APIs must not leak into the Compose skill

If a decision depends on `AndroidManifest`, `AppDelegate`, `SceneDelegate`, universal links, intents, or equivalent host contracts, it does not belong in the Compose Navigation skill.

- Keep those rules here or in platform-specific documentation.
- `kb-kmm-navigation-compose` should only assume that the host already delivers the event to the graph.
