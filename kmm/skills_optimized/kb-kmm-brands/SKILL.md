---
name: kb-kmm-brands
description: "Knowledge base for brands in KMM projects: product identity per brand, brand catalogue, base values per brand, assets/naming/bundle ID, and separation between brand differences and environment differences."
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Brands — Knowledge Base

## Rule 1: `brand` is a product identity dimension

A `brand` represents a product identity within the same technical base. It may define: product name · visual identity and assets · base bundle/application ID · brand-specific texts or resources · functional composition or brand-dependent routing.

It does not define the integration target or operational deployment environment — that belongs to `env`.

## Rule 2: The brand catalogue is a stable source of truth

The project must clearly express: which brands exist · the canonical identifier of each brand · which base values belong to each one.

This catalogue is stable and must exist before materializing flavors, targets, or concrete variants.

## Rule 3: Brand values are base values, not full variants

Brand values are those that remain stable regardless of environment: display name · base bundle/app ID · brand assets and resources · product branding.

Values that change per deployment or external integration belong to `env`, not `brand`.

## Rule 4: `brand` and `env` must not absorb each other

A brand must not encode differences that are actually environmental. An environment must not encode product identity. The final variant always results from combining a brand identity and an operational environment.

If a rule stops making sense when only the brand changes → it is a `brand` rule.
If a rule stops making sense when only the environment changes → it is an `env` rule.

## Rule 5: The variant matrix consumes the brand catalogue

The `brand × env` matrix is built from the brand catalogue and the environment catalogue. The `environments` skill composes both dimensions but does not redefine what a brand is.

## Rule 6: Functional differences per brand belong to architecture and app layer

If a brand changes navigation · screen composition · visible features · implementation wiring — those decisions are coordinated with `kb-kmm-app-layer` and `kb-kmm-clean-architecture`.

This skill defines the semantics of the `brand` dimension only, not how each difference is implemented at runtime.

## Rule 7: Android and iOS consume the `brand` dimension

Android materializes `brand` via flavors. iOS via targets, schemes, or build configuration. Base brand semantics live here, not in the platform implementation.