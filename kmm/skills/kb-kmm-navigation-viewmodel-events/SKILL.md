---
name: kb-kmm-navigation-viewmodel-events
description: "Base de conocimiento de efectos de navegación desde ViewModel en proyectos KMM: NavigationSideEffect, Channel vs StateFlow, reglas de LaunchedEffect y separación entre lógica de negocio, Composable y destino concreto."
argument-hint: ""
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Navigation ViewModel Events — Base de Conocimiento

## Regla 1: La lógica de negocio no navega; emite efectos

Cuando la navegación depende de una condición de negocio, el ViewModel no navega directamente. Emite un efecto que el Composable consume.

El destino concreto sigue decidiéndose fuera del ViewModel.

---

## Regla 2: Los efectos nombran hechos, no destinos concretos

Un efecto de navegación debe expresar qué ocurrió:

- `LoginSuccess`
- `RegistrationRequired`
- `SessionExpired`

No debe codificar directamente rutas del grafo global.

---

## Regla 3: Elegir un único patrón de emisión por proyecto

Las opciones habituales son:

- `Channel` con entrega única
- `StateFlow` con reset manual

Elegir uno y aplicarlo de forma consistente. No mezclar patrones arbitrariamente entre pantallas equivalentes.

→ Patterns: `references/viewmodel-and-navigation-events.md`

---

## Regla 4: La key de `LaunchedEffect` depende del patrón

La key correcta no es universal:

- con `Channel`, usar `LaunchedEffect(viewModel)`
- con `StateFlow` con reset, usar `LaunchedEffect(uiState.effect)`

`LaunchedEffect(Unit)` no es válido para este problema porque oculta cambios de owner o re-entradas relevantes.

→ Patterns: `references/viewmodel-and-navigation-events.md`

---

## Regla 5: Los efectos de navegación no se mezclan con `UiEvent`

Los `UiEvent` modelan interacción de entrada.

Los efectos de navegación modelan salidas o consecuencias de estado.

Mezclarlos aumenta el riesgo de eventos duplicados, recolección incorrecta o navegación repetida por recomposición.

---

## Regla 6: Esta skill no define DI ni librería de navegación

Esta skill solo define el patrón de coordinación ViewModel ↔ Composable para navegación.

No define:

- `NavHost`
- rutas
- `NavController`
- Koin u otra DI

La navegación concreta vive en `kb-kmm-navigation-compose`.
