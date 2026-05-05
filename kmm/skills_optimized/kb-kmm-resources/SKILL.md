---
name: kb-kmm-resources
description: "Knowledge base for shared resources in Compose Multiplatform: strings, images, fonts, raw files, and localization with compose.resources."
argument-hint: "tema a consultar (opcional): strings, images, fonts, raw, localization"
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Compose Multiplatform Resources — Knowledge Base

## Rule 1: Shared resources live in `commonMain/composeResources`

All shared resources live in `commonMain/composeResources/`.

This includes:

- strings
- drawables
- fonts
- raw files

Platform-native resources such as launch icons or splash screens do not live here.

## Rule 2: Shared resource access uses `Res` and `compose.resources` APIs

Shared access uses the `Res` class and functions from `org.jetbrains.compose.resources`.

Hardcoding strings or paths is forbidden when the resource belongs to the shared system.

## Rule 3: Strings resolve in UI unless there is an explicit need outside Composable

Use `stringResource()` in Composables.

Outside Composables, use `getString()` only when a materialized `String` is really needed at that point.

If the project uses `kb-kmm-ui-text`, the ViewModel does not resolve strings for UI state or UI models: it exposes `UiText` or `StringResource`, and the UI materializes them.

→ Templates: `references/string-resources.md`

## Rule 4: Localization uses `values-{locale}` folders

The base file lives in `values/`.

Translations live in `values-{locale}/` folders with the same filename.

→ Templates: `references/string-resources.md`

## Rule 5: `@StringRes` is not part of the shared contract

`@StringRes` is Android-specific and forbidden in `commonMain`.

Use `StringResource` from `compose.resources` for shared string references.

## Rule 6: Resource system structure is configured in the shared module

The shared module declares `compose.components.resources` and configures `Res` generation.

Exact folder structure and Gradle configuration are implementation details.

→ Templates: `references/setup-and-structure.md`

## Rule 7: Images, fonts, and raw files use their corresponding access channel

Each resource type uses its own API:

- images with `painterResource`
- fonts con `Font`
- raw files with `Res.readBytes`

Choosing the resource type belongs to this dimension; concrete usage belongs to templates.

→ Templates: `references/image-font-raw.md`

## Rule 8: `StringResource` may be used directly in UI models for always-translatable fields

When a UI-model field is always a resource string and never a dynamic external value, it may be typed directly as `StringResource` from `compose.resources`.

The presentation mapper assigns the corresponding key, and the Composable resolves it with `stringResource(field)`.

When a field can be dynamic OR translatable depending on the condition, use `UiText` instead (`kb-kmm-ui-text`).

Do not use `StringResource` plus helper primitives so the UI reconstructs the final text. If there is a branch between dynamic and translatable text, presentation must close that decision as `UiText`.

## Rule 9: This skill does not replace the text exposure pattern

This skill defines the base shared resource system.

It does not define how a ViewModel exposes translatable text to UI. That pattern lives in `kb-kmm-ui-text`.

## Rule 10: Non-negotiable requirements

- shared strings and drawables in `commonMain/composeResources/`
- `stringResource()` for text in Composables
- `getString()` only when a `String` is needed outside UI
- localization support through `values-{locale}/` folders
- platform-specific resources outside `commonMain`
