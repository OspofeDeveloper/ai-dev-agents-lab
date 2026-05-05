---
name: kb-kmm-clean-architecture
description: "Knowledge base for layered architecture in KMM projects: app/core/features roles, allowed dependencies, composition, navigation, feature aggregation, and rules for sharing data without coupling."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Layered Architecture KMM — Knowledge Base

## Rule 1: Architecture defines layers and boundaries, not technologies

This skill defines the stable architectural structure: layers, ownership, allowed dependencies, and composition rules. If a rule holds true regardless of the HTTP, DI, or auth library, it belongs here.

## Rule 2: The project layers are `app`, `features`, and `core`

```text
app/ -> features/ -> core/
```

Conceptual dependency direction only — not a physical folder template. Dependencies always point inward:
- `app` may depend on `features` and `core`
- `features` may depend on `core`
- `core` does not depend on `features` or `app`

The authoritative structural unit is `app` / `features` / `core` — not an abstract `presentation/domain/data` split distributed freely across the codebase.

## Rule 3: Each layer has a distinct responsibility

- `app` — composition root and global assembly decisions
- `features` — autonomous product domain and UI units
- `core` — shared domain and cross-cutting infrastructure

Detailed rules for each layer live in their specialized skills. This skill only fixes inter-layer relationships and global boundaries.

## Rule 4: Features are autonomous and do not depend on each other

- a feature may depend on `core`
- a feature must not depend on another feature
- a feature must not make global application composition decisions

Internal feature microarchitecture belongs to the feature skill.

## Rule 5: `app` decides global composition

`app` resolves navigation, feature assembly, and global decisions dependent on context, brand, or composition. Detailed rules live in the `app` skill. This skill only establishes that these decisions do not belong in `features` or `core`.

## Rule 6: `core` concentrates shared and cross-cutting pieces

`core` groups contracts, domain, and reusable infrastructure shared across multiple features. Detailed rules for what enters, what is excluded, and internal organization live in the `core` skill. This skill only establishes that `core` does not know concrete features or `app` composition.

## Rule 7: Navigation is resolved in `app`, not in features

Features may emit facts or callbacks. Concrete navigation belongs to `app`: global destinations · brand or context-dependent routing · aggregated screen composition. Detailed navigation and composition policy lives in the `app` skill.

## Rule 8: Sharing data between features requires extracting responsibility to the correct level

If a feature needs data or logic also used by another feature, it must not depend on that feature. Decision tree:
- shared external data source → move repository to `core/domain`
- shared transformation or use case → move to `core/domain/usecase`
- ephemeral UI state within a single aggregated screen → coordinate via a screen ViewModel in `app`

If this recurs frequently between the same features, re-evaluate whether they are truly two separate features.

## Rule 9: Infrastructure details stay encapsulated behind clear boundaries

HTTP, persistence, auth, and DI are infrastructure details. They must be encapsulated behind contracts or composition points appropriate to the consuming layer. The architecture defines: which layer may know each detail · where each implementation lives · which contracts and boundaries must be respected.

The architecture does not change because a concrete library changes.

## Rule 10: This skill defines conceptual rules; layer skills and workflows only apply them

`wf-*` and the specialized `app`, `core`, and `feature` skills consult this skill to respect the global system topology. This skill does not define operational steps, concrete implementation snippets, or duplicate detailed rules already covered by specialized layer skills.