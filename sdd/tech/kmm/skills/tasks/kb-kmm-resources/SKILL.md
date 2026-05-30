---
name: kb-kmm-resources
description: "Base de conocimiento sobre recursos compartidos en Compose Multiplatform: strings, imágenes, fonts, raw files y localización con compose.resources."
argument-hint: "tema a consultar (opcional): strings, images, fonts, raw, localization"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Compose Multiplatform Resources — Base de Conocimiento

## Regla 1: Los recursos compartidos viven en `commonMain/composeResources`

Todos los recursos compartidos viven en `commonMain/composeResources/`.

Esto incluye:

- strings
- drawables
- fonts
- raw files

Los recursos nativos de plataforma, como launch icons o splash screens, no viven aquí.

## Regla 2: El acceso a recursos compartidos usa `Res` y APIs de `compose.resources`

El acceso compartido usa la clase `Res` y las funciones de `org.jetbrains.compose.resources`.

Está prohibido hardcodear strings o rutas cuando el recurso pertenece al sistema compartido.

## Regla 3: Los strings se resuelven en UI salvo necesidad explícita fuera de Composable

En Composables se usa `stringResource()`.

Fuera de Composables, `getString()` solo se usa cuando realmente se necesita el `String` materializado en ese punto.

Si el proyecto usa `kb-tasks-kmm-ui-text`, el ViewModel no resuelve strings para estado/UI models: expone `UIText` o `StringResource` y la UI los materializa.

→ Templates: `${CLAUDE_SKILL_DIR}/references/string-resources.md`

## Regla 4: La localización se organiza por carpetas `values-{locale}`

El archivo base vive en `values/`.

Las traducciones viven en carpetas `values-{locale}/` con el mismo nombre de fichero.

→ Templates: `${CLAUDE_SKILL_DIR}/references/string-resources.md`

## Regla 5: `@StringRes` no forma parte del contrato compartido

`@StringRes` pertenece a Android y está prohibido en `commonMain`.

Para referencias a strings compartidos se usa `StringResource` de `compose.resources`.

## Regla 6: La estructura del sistema de recursos se configura en el módulo compartido

El módulo compartido declara `compose.components.resources` y configura la generación de `Res`.

La estructura exacta de carpetas y la configuración Gradle son detalles de implementación.

→ Templates: `${CLAUDE_SKILL_DIR}/references/setup-and-structure.md`

## Regla 7: Imágenes, fonts y raw files usan el canal de acceso correspondiente

Cada tipo de recurso usa su API específica:

- imágenes con `painterResource`
- fonts con `Font`
- raw files con `Res.readBytes`

La elección del tipo de recurso pertenece a esta dimensión; su uso concreto pertenece a templates.

→ Templates: `${CLAUDE_SKILL_DIR}/references/image-font-raw.md`

## Regla 8: `StringResource` puede usarse directamente en UiModels para campos siempre traducibles

Cuando un campo de un UiModel es siempre un string de recurso (nunca un valor dinámico externo), puede tipificarse directamente como `StringResource` de `compose.resources`.

El mapper de presentación asigna la clave correspondiente:

```kotlin
data class HomeWorkerUiModel(
    val contractType: StringResource = Res.string.home_contract_type_none,
    val state: StringResource = Res.string.home_worker_status_none
)

fun ContractType.toStringResource(): StringResource = when (this) {
    ContractType.UNDEFINED -> Res.string.home_contract_type_undefined
    ContractType.TEMPORARY -> Res.string.home_contract_type_temporary
    // ...
}
```

El Composable lo resuelve con `stringResource(field)`.

Cuando el campo puede ser dinámico O traducible según condición, usar `UIText` en su lugar.

→ Cuándo usar `UIText` vs `StringResource` y la regla de no dividir la intención textual: `kb-tasks-kmm-ui-text`

## Regla 9: Esta skill no sustituye al patrón de exposición textual

Esta skill define el sistema base de recursos compartidos.

No define cómo un ViewModel expone texto traducible a UI. Ese patrón vive en `kb-tasks-kmm-ui-text`.

## Regla 10: Requisitos no negociables

- strings y drawables compartidos en `commonMain/composeResources/`
- `stringResource()` para textos en Composables
- `getString()` solo cuando se necesita el `String` fuera de UI
- soporte de localización con carpetas `values-{locale}/`
- recursos platform-specific fuera de `commonMain`
