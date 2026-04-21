---
name: kb-kmm-ui-text
description: "Base de conocimiento sobre el patrón UiText en Compose Multiplatform: sealed interface para desacoplar ViewModel de la capa UI, manejo de strings traducibles y dinámicos."
argument-hint: "implementación, uso en state, uso en viewmodel, testing"
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# UiText Pattern — Base de Conocimiento

## Regla 1: `UiText` desacopla el ViewModel de la resolución visual del texto

El ViewModel produce `UiText`, no `String` resuelto mediante APIs Composable.

La resolución final del texto ocurre en UI.

## Regla 2: `UiText` vive en `commonMain` y no depende de tipos de plataforma

El sealed interface y sus variantes viven en `commonMain`.

Está prohibido depender de `@StringRes` o de contextos específicos de Android.

→ Templates: `references/ui-text-pattern.md`

## Regla 3: La representación distingue texto dinámico de texto traducible

El patrón separa dos casos:

- texto dinámico proveniente de fuentes externas
- texto basado en recursos compartidos y traducibles

La forma concreta del sealed interface pertenece a templates.

→ Templates: `references/ui-text-pattern.md`

## Regla 4: `UiText` se materializa solo en la capa UI

La resolución mediante `asString()` o equivalente ocurre en Composables.

Está prohibido llamar a `stringResource()` en el ViewModel para resolver texto.

## Regla 5: El estado de UI puede exponer `UiText` sin romper fronteras de presentación

El estado de pantalla puede exponer `UiText?` para errores, mensajes y textos derivados.

Esto permite que el ViewModel construya una representación visual estable sin acoplarse al runtime UI.

→ Templates: `references/ui-text-pattern.md`

## Regla 6: El mapping `AppError -> UiText` vive en presentation

Cuando el proyecto usa un error transversal como `AppError`, la conversión a `UiText` pertenece a presentation/UI.

La política transversal de `AppError` vive en `kb-kmm-app-errors`; esta skill solo define su representación visual.

→ Templates: `references/ui-text-pattern.md`

## Regla 7: Esta skill se apoya en `kb-kmm-resources`, no la sustituye

`UiText` consume el sistema base de recursos compartidos definido en `kb-kmm-resources`.

No redefine localización, directorios de recursos ni reglas del sistema `Res`.

## Regla 8: Los tests de ViewModel validan `UiText`, no strings resueltos

En tests de ViewModel se compara el valor `UiText` directamente.

No hace falta renderizar UI ni comparar strings materializados.

→ Templates: `references/ui-text-pattern.md`

## Regla 9: Requisitos no negociables

- `UiText` en `commonMain`
- resolución visual solo en UI
- `ResourceString` o equivalente para texto traducible
- `DynamicString` o equivalente para texto externo
- mapping `AppError -> UiText` en presentation/UI
