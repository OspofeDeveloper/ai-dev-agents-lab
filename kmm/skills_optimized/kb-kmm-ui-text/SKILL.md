---
name: kb-kmm-ui-text
description: "Knowledge base for the UiText pattern in Compose Multiplatform: `UiText` decouples ViewModel and UI when handling translatable and dynamic text."
argument-hint: "implementación, uso en state, uso en viewmodel, testing"
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# UiText Pattern — Knowledge Base

## Rule 1: `UiText` decouples the ViewModel from visual text resolution

The ViewModel produces `UiText`, not a `String` resolved with Composable APIs.

Final text resolution happens in UI.

## Rule 2: `UiText` lives in `commonMain` and does not depend on platform types

The sealed interface and its variants live in `commonMain`.

Depending on `@StringRes` or Android-specific contexts is forbidden.

→ Templates: `references/ui-text-pattern.md`

## Rule 3: The representation distinguishes dynamic text from translatable text

The pattern separates two cases:

- dynamic text coming from external sources
- text based on shared, translatable resources

The concrete sealed-interface shape belongs in templates.

→ Templates: `references/ui-text-pattern.md`

## Rule 4: `UiText` is materialized only in the UI layer

Resolution through `asString()` or equivalent happens in Composables.

Calling `stringResource()` in the ViewModel to resolve text is forbidden.

## Rule 5: UI state may expose `UiText` without breaking presentation boundaries

Screen state may expose `UiText?` for errors, messages, and derived text.

This lets the ViewModel build a stable visual representation without coupling to the UI runtime.

→ Templates: `references/ui-text-pattern.md`

## Rule 6: `AppError -> UiText` mapping lives in presentation

When the project uses a cross-cutting error such as `AppError`, conversion to `UiText` belongs to presentation/UI.

Cross-cutting `AppError` policy lives in `kb-kmm-app-errors`; this skill defines only its visual representation.

→ Templates: `references/ui-text-pattern.md`

## Rule 7: This skill builds on `kb-kmm-resources`; it does not replace it

`UiText` consumes the base shared resource system defined in `kb-kmm-resources`.

It does not redefine localization, resource directories, or `Res` system rules.

## Rule 8: ViewModel tests validate `UiText`, not resolved strings

In ViewModel tests, compare the `UiText` value directly.

There is no need to render UI or compare materialized strings.

→ Templates: `references/ui-text-pattern.md`

## Rule 9: A `UiModel` must expose the complete text intent

If a visible field can be translatable in some cases and dynamic in others, the `UiModel` must expose a single `UiText` already decided by presentation.

Splitting that decision across primitives so the UI reconstructs the final text is forbidden, for example:

- `String` + `Boolean` so the UI decides whether to prepend a resource
- `String` + `StringResource?` so the Composable chooses which one to show
- flags, enums, or helper conditions whose only purpose is letting the UI assemble the final text

The UI may materialize `UiText`, but it must not complete text-selection logic that belongs to the mapper or ViewModel.

→ Templates: `references/ui-text-pattern.md`

## Rule 10: Non-negotiable requirements

- `UiText` en `commonMain`
- visual resolution only in UI
- `ResourceString` or equivalent for translatable text
- `DynamicString` or equivalent for external text
- `AppError -> UiText` mapping in presentation/UI
- use `UiText` in UI models when a field can be dynamic OR translatable depending on the condition; use `StringResource` directly when it is always a fixed resource
- do not split one text intent into helper primitives so the UI can reconstruct it
