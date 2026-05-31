---
name: kb-plan-kmm-ui-text
description: Patrón UIText en Compose Multiplatform como decisión arquitectónica: cuándo usarlo, qué problema resuelve, separación ViewModel-UI para texto traducible y dinámico. Úsalo cuando haya que planificar cómo un ViewModel expone texto a la UI.
allowed-tools: [Read]
effort: low
user-invocable: false
---

# UIText — Patrón de planificación

→ Implementación concreta (sealed interface, Regla 10, templates): `kb-tasks-kmm-ui-text`

## Qué problema resuelve

Un ViewModel en commonMain no puede llamar a `stringResource()` — esa API es Composable.
Sin `UIText`, el ViewModel debe recibir el `String` resuelto desde la UI o hardcodear texto,
rompiendo el desacoplamiento entre lógica y presentación.

`UIText` es un sealed interface en commonMain que representa la *intención textual*:
- texto traducible (referencia a un string resource)
- texto dinámico (valor externo o construido en runtime)

La resolución final ocurre solo en la capa UI.

## Cuándo incluir UIText en el plan

Incluir el patrón cuando:
- El ViewModel produce mensajes de error, etiquetas o textos que dependen del resultado de negocio
- Los mismos errores o mensajes pueden ser dinámicos (del servidor) o traducibles (de recursos)
- El estado de pantalla necesita exponer texto que no es siempre un string resource fijo

No incluirlo si todos los campos de texto visibles son siempre strings resources fijos →
en ese caso basta con `StringResource` directamente en el `UiModel`.

## Decisión de diseño: UIText vs StringResource

| Situación | Tipo a usar |
|---|---|
| Campo siempre traducible, nunca dinámico | `StringResource` (de compose.resources) |
| Campo que puede ser dinámico O traducible según condición | `UIText` |
| Mensaje de error de negocio mapeado en presentation | `UIText` |
| Texto hardcodeado temporal (prototipo) | `String` — marcar como pendiente |

## Dónde vive UIText en la arquitectura

- `UIText` sealed interface → `core/ui/` en `commonMain`
- Resolución (`asString()`) → capa Composable
- Mapping `AppError → UIText` → presentation/UI de la feature
- El ViewModel **no** llama a `stringResource()` ni resuelve el texto

## Relación con otros contratos del plan

- `AppError` (ver `kb-kmm-app-errors`) define los errores; `UIText` define cómo representarlos visualmente
- `UIText` consume el sistema de recursos de `kb-cmp-resources`
- Si la feature usa `UIText`, el plan debe contemplar la pieza de mapping en la capa presentation
