---
name: kb-tasks-kmm-ui-text
description: "Base de conocimiento sobre el patrón UiText en Compose Multiplatform: `UIText` desacopla ViewModel y UI para manejar textos traducibles y dinámicos."
argument-hint: "implementación, uso en state, uso en viewmodel, testing"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# UiText Pattern — Base de Conocimiento

## Regla 1: `UIText` desacopla el ViewModel de la resolución visual del texto

El ViewModel produce `UIText`, no `String` resuelto mediante APIs Composable.

La resolución final del texto ocurre en UI.

## Regla 2: `UIText` vive en `commonMain` y no depende de tipos de plataforma

El sealed interface y sus variantes viven en `commonMain`.

Está prohibido depender de `@StringRes` o de contextos específicos de Android.

→ Templates: `references/ui-text-pattern.md`

## Regla 3: La representación distingue texto dinámico de texto traducible

El patrón separa dos casos:

- texto dinámico proveniente de fuentes externas
- texto basado en recursos compartidos y traducibles

La forma concreta del sealed interface pertenece a templates.

→ Templates: `references/ui-text-pattern.md`

## Regla 4: `UIText` se materializa solo en la capa UI

La resolución mediante `asString()` o equivalente ocurre en Composables.

Está prohibido llamar a `stringResource()` en el ViewModel para resolver texto.

## Regla 5: El estado de UI puede exponer `UIText` sin romper fronteras de presentación

El estado de pantalla puede exponer `UIText?` para errores, mensajes y textos derivados.

Esto permite que el ViewModel construya una representación visual estable sin acoplarse al runtime UI.

→ Templates: `references/ui-text-pattern.md`

## Regla 6: El mapping `AppError -> UIText` vive en presentation

Cuando el proyecto usa un error transversal como `AppError`, la conversión a `UIText` pertenece a presentation/UI.

La política transversal de `AppError` vive en `kb-kmm-app-errors`; esta skill solo define su representación visual.

→ Templates: `references/ui-text-pattern.md`

## Regla 7: Esta skill se apoya en `kb-kmm-resources`, no la sustituye

`UIText` consume el sistema base de recursos compartidos definido en `kb-kmm-resources`.

No redefine localización, directorios de recursos ni reglas del sistema `Res`.

## Regla 8: Los tests de ViewModel validan `UIText`, no strings resueltos

En tests de ViewModel se compara el valor `UIText` directamente.

No hace falta renderizar UI ni comparar strings materializados.

→ Templates: `references/ui-text-pattern.md`

## Regla 9: Un `UiModel` debe exponer la intención textual completa

Si un campo visible puede ser a veces traducible y a veces dinámico, el `UiModel` debe exponer un único `UIText` ya decidido por presentation.

Está prohibido repartir esa decisión entre varios primitivos para que la UI reconstruya el texto final, por ejemplo:

- `String` + `Boolean` para decidir si la UI debe anteponer un recurso
- `String` + `StringResource?` para que el Composable elija cuál mostrar
- flags, enums o condiciones auxiliares cuyo único propósito sea que la UI monte el texto final

La UI puede materializar `UIText`, pero no completar la lógica de selección textual que pertenece al mapper o al ViewModel.

→ Templates: `references/ui-text-pattern.md`

## Regla 10: Requisitos no negociables

- `UIText` como `sealed class` en `commonMain` (`core/ui/`)
- resolución visual solo en UI mediante `asString()` en Composables
- `UIText.Resource` para texto traducible (strings resources con o sin args)
- `UIText.Dynamic` para texto proveniente de datos externos o dinámicos
- mapping `AppError -> UIText` en presentation/UI
- en UiModels, usar `UIText` cuando un campo puede ser dinámico O traducible según condición; usar `StringResource` directamente cuando es siempre un recurso fijo
- no dividir una misma intención textual en primitivos auxiliares para que la UI la reconstruya
