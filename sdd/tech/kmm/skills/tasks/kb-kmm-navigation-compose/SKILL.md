---
name: kb-kmm-navigation-compose
description: "Base de conocimiento de implementación de navegación con Compose Navigation + Kotlin Serialization en KMM: rutas @Serializable, NavHost, nested graphs, back stack, deep links de grafo, shell adaptativo, testing del grafo y constraints de commonMain."
argument-hint: "topic de navegación a consultar (opcional)"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Compose Multiplatform Navigation Compose — Base de Conocimiento

## Regla 1: Esta skill implementa el grafo Compose; no define ownership ni contratos globales

Esta skill define la implementación concreta del grafo con Compose Navigation y rutas type-safe.

No define por sí sola:

- ownership arquitectónico de la navegación
- contrato entre `app` y features
- patrón de efectos de navegación desde ViewModel
- integración de plataforma con el host
- DI concreta

Esas reglas viven en:

- `kb-kmm-navigation-contracts`
- `kb-kmm-navigation-viewmodel-events`
- `kb-kmm-navigation-platform-behaviors`
- `kb-koin` si aplica

## Regla 2: Setup y dependencias mínimas se fijan por librería

La implementación usa el artefacto Compose Multiplatform de Navigation Compose y Kotlin Serialization en `commonMain`.

Versión mínima de referencia: `org.jetbrains.androidx.navigation:navigation-compose:2.8+`.

La configuración exacta de dependencias y plugin pertenece a templates, no a esta regla conceptual.

→ Templates: `references/setup-and-routes.md`

## Regla 3: Las rutas son type-safe y viven en `commonMain`

Todas las rutas viven en `commonMain`.

Cada ruta es:

- `object` si no lleva argumentos
- `data class` si lleva argumentos
- `@Serializable object` si representa la raíz de un nested graph

Los argumentos opcionales llevan valor por defecto.

→ Templates: `references/setup-and-routes.md`

## Regla 4: En `commonMain` se usan APIs multiplataforma de navegación

Para extraer argumentos se usa `backStackEntry.toRoute<T>()`.

Está prohibido usar `SavedStateHandle.toRoute()` en `commonMain` porque depende de AndroidX Lifecycle.

Los argumentos complejos deben cruzar la ruta como primitivos serializables, no como objetos de plataforma.

→ Templates: `references/setup-and-routes.md`

## Regla 5: El `NavHost` vive en `commonMain` y comparte owner con el shell

El `NavHost` y todo el grafo viven en `commonMain`.

`AppNavGraph` recibe el `navController` como parámetro requerido, sin default. El owner es siempre el shell o el test que lo invoca.

Esto garantiza que el mismo `navController` se comparta entre el `NavHost` y el componente de navegación del shell.

No usar `LocalNavController` como `CompositionLocal`, porque empeora testabilidad y oculta ownership.

→ Templates: `references/navhost-and-backstack.md`

## Regla 6: El back stack se manipula con criterios explícitos de flujo

La combinación `popUpTo`, `inclusive`, `launchSingleTop`, `saveState` y `restoreState` se usa según el tipo de flujo:

- `inclusive = true` cuando el origen no debe quedar en stack
- `launchSingleTop` en navegación por tabs
- `saveState` y `restoreState` en shell por tabs para conservar estado

`popBackStack()` y `navigateUp()` no son intercambiables semánticamente. Si un destino puede recibirse vía deep link, ignorar el `Boolean` de `popBackStack()` está prohibido y debe existir fallback explícito.

→ Templates: `references/navhost-and-backstack.md`

## Regla 7: Los nested graphs preservan la frontera entre features y `app`

Navegar al graph aterriza en su `startDestination`; navegar a una ruta aterriza en ese destino concreto.

Cada feature expone su registro de grafo con callbacks o lambdas de salida.

La feature:

- no recibe el `NavController`
- no conoce rutas de otras features
- no decide composición global

Las rutas compartidas y el `NavController` permanecen centralizados en `app`.

→ Templates: `references/nested-graphs-and-multimodule.md`

## Regla 8: El shell adaptativo es responsabilidad del runtime Compose, no del contrato de navegación

La navegación por tabs aplica siempre las opciones necesarias para evitar duplicados y conservar estado.

La selección del item activo se sincroniza con la jerarquía actual del destino.

En entornos adaptativos:

- `NavigationBar` en compact
- `NavigationRail` en medium
- `NavigationDrawer` en expanded

La implementación concreta del shell y sus layouts vive en templates.

→ Templates: `references/bottom-nav-and-adaptive.md`

## Regla 9: Esta skill resuelve deep links dentro del grafo, no la integración del host

La skill cubre la resolución de deep links una vez el host entrega el evento al runtime de navegación.

La configuración de plataforma que conecta URLs, intents, universal links o bridges nativos pertenece a `kb-kmm-navigation-platform-behaviors`.

Los placeholders del URI deben coincidir con los nombres de los parámetros de la ruta `@Serializable`.

→ Templates: `references/deeplinks.md`

## Regla 10: El scoping de ViewModel y los side effects se consumen desde sus skills autoritativas

El grafo Compose puede necesitar scoping de ViewModel y consumo de side effects, pero no define su patrón normativo.

Para scoping y paso de parámetros, consultar la DI activa y el patrón autoritativo de navegación desde ViewModel.

Para efectos de navegación y `LaunchedEffect`, la skill autoritativa es `kb-kmm-navigation-viewmodel-events`.

→ Templates: `references/viewmodel-scoping.md`

## Regla 11: Testing del grafo pertenece a la implementación Compose

El testing del grafo y de la integración con `NavHost` pertenece a esta dimensión porque valida la implementación concreta de Compose Navigation.

Los tests de ViewModel aislados siguen perteneciendo a `kb-kmm-navigation-viewmodel-events`, no a esta skill.

→ Templates: `references/testing.md`

## Regla 12: Las transiciones son un detalle de implementación del `NavHost`

Las transiciones globales se definen en el `NavHost`; las transiciones por ruta sobreescriben las globales.

En iOS deben preferirse transiciones compatibles con Compose Multiplatform. Predictive back animation no convierte Android en fuente de verdad del diseño del grafo.

→ Templates: `references/animations.md`

## Regla 13: Los comportamientos de plataforma no contaminan esta skill

`BackHandler`, predictive back y bridges del host no viven aquí.

Si una decisión depende de AndroidManifest, AppDelegate, SceneDelegate, universal links o APIs del host, delegar en `kb-kmm-navigation-platform-behaviors`.

## Regla 14: Requisitos no negociables de esta implementación

Mientras el proyecto use Compose Navigation + Kotlin Serialization:

- rutas type-safe con `@Serializable`
- `AppNavGraph` recibe el `navController` como parámetro requerido
- `SavedStateHandle.toRoute()` está prohibido en `commonMain`
- el retorno de `popBackStack()` no se ignora en entry points de deep link
- el shell adaptativo respeta la semántica compact/medium/expanded
