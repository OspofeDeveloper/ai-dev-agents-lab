---
name: kb-kmm-navigation-compose
description: Base de conocimiento de implementación de navegación con Compose Navigation + Kotlin Serialization en KMM: rutas @Serializable, NavHost, nested graphs, back stack, deep links de grafo, shell adaptativo y constraints de commonMain.
argument-hint: "topic de navegación a consultar (opcional)"
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Compose Multiplatform — Navigation Compose

---

## Alcance

Esta skill implementa navegación con:

- Compose Navigation
- Kotlin Serialization
- Compose Multiplatform

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

---

## 1. Setup y dependencias

Versión mínima: `org.jetbrains.androidx.navigation:navigation-compose:2.8+` (artifact CMP; soporta type-safe routes en `commonMain`). Requiere también `kotlin("plugin.serialization")` y `kotlinx.serialization.json` en `commonMain`.

- Para las dependencias Gradle y el plugin de serialización, ver [setup-and-routes.md](references/setup-and-routes.md)

---

## 2. Rutas type-safe

### 2.1 Definición con `@Serializable`

Todas las rutas van en `commonMain`. Cada ruta es un `object` (sin argumentos) o una `data class` (con argumentos). Los argumentos opcionales llevan valor por defecto. Las raíces de nested graphs también son `@Serializable object`.

- Para ejemplos completos de definición de rutas, ver [setup-and-routes.md](references/setup-and-routes.md)

### 2.2 Restricciones en commonMain

- Usar `backStackEntry.toRoute<T>()` para extraer argumentos, **nunca** `SavedStateHandle.toRoute()` (API de AndroidX Lifecycle, no disponible en `commonMain`)
- Pasar argumentos complejos como primitivos serializables, no como objetos Parcelable

---

## 3. NavHost y destinations

### 3.1 NavHost en commonMain

El NavHost y todo el grafo de navegación viven en `commonMain`. `AppNavGraph` acepta el `navController` como parámetro requerido (sin default): el owner es siempre el `AppShell` en producción o el test que lo invoca. Esto garantiza que el mismo `navController` sea compartido por el NavHost y el componente de navegación del shell (bottom bar / rail / drawer).

- Para el patrón completo de `AppNavGraph.kt` y extracción de argumentos, ver [navhost-and-backstack.md](references/navhost-and-backstack.md)

### 3.2 `rememberNavController()`

`rememberNavController()` ya está atado al `SavedStateRegistry` del host: sobrevive a cambios de configuración sin trabajo adicional. No usar `LocalNavController` CompositionLocal — hace el grafo difícil de testear.

---

## 4. Back stack management

### 4.1 `popUpTo` + `inclusive`

`inclusive = true` elimina también la ruta destino del `popUpTo`. Úsalo cuando la pantalla de origen no debe quedar en el stack (flujos de autenticación, onboarding).

### 4.2 `launchSingleTop`

Obligatorio en BottomNavigation. Evita duplicar el destino si ya está en el top del stack.

### 4.3 `saveState` / `restoreState`

Obligatorios en BottomNavigation para no perder el scroll position ni el estado del formulario al cambiar de tab.

### 4.4 `popBackStack()` vs `navigateUp()`

| Función | Comportamiento |
|---|---|
| `popBackStack()` | Elimina la entrada actual del back stack. No hace nada si ya está en el root. |
| `navigateUp()` | Igual que `popBackStack()`, pero si el stack está vacío, delega al sistema (equivale a pulsar el botón Up de Android). |

Usar `popBackStack()` para "Atrás" desde pantallas internas. Usar `navigateUp()` en la action bar/toolbar.

**`popBackStack()` devuelve un `Boolean`** — `false` si el stack ya estaba vacío. En destinos que pueden recibirse vía deep link, manejar ese caso con un fallback a `HomeRoute`.

- Para todos los ejemplos de back stack, ver [navhost-and-backstack.md](references/navhost-and-backstack.md)

---

## 5. Nested NavGraphs

### 5.1 Navegar al graph vs a una ruta

`navController.navigate(MainGraph)` aterriza en el `startDestination` del graph. `navController.navigate(ProfileRoute("123"))` va directo a la ruta, en cualquier graph.

- Para ejemplos de nested graphs, ver [nested-graphs-and-multimodule.md](references/nested-graphs-and-multimodule.md)

### 5.2 Feature modules con grafos independientes

Cada feature expone `fun NavGraphBuilder.featureGraph(...)` con lambdas para las acciones de salida. El feature **nunca** recibe el `NavController` — solo emite callbacks que `:app` resuelve.

Las rutas se centralizan en `:app/navigation/`. Features nunca dependen entre sí ni conocen rutas de otros features — solo dependen del contrato central. El `NavController` nunca sale de `:app`.

- Para la estructura de módulos y el patrón de registro de grafos, ver [nested-graphs-and-multimodule.md](references/nested-graphs-and-multimodule.md)

---

## 6. Shell y navegación adaptativa

Las opciones de navegación por tabs se aplican **siempre** en el `onClick` de cada tab:

```
popUpTo<StartDestination> { saveState = true }   // StartDestination = startDestination del NavHost
launchSingleTop = true
restoreState = true
```

La sincronización del item seleccionado se hace con `currentDestination?.hierarchy?.any { it.hasRoute(item.route::class) }`.

En CMP con soporte para tablet y desktop, el shell se adapta al tamaño de ventana:

| Window size class | Ancho | Componente |
|---|---|---|
| Compact | < 600 dp | `NavigationBar` (bottom) |
| Medium | 600–840 dp | `NavigationRail` (lateral izquierdo) |
| Expanded | > 840 dp | `NavigationDrawer` permanente (lateral) |

Usar `calculateWindowSizeClass()` de `androidx.compose.material3.windowsizeclass` en commonMain.

- Para los tres layouts completos (`AppShell`, `CompactLayout`, `MediumLayout`, `ExpandedLayout`), ver [bottom-nav-and-adaptive.md](references/bottom-nav-and-adaptive.md)

---

## 7. Deep Links de grafo

Esta skill cubre solo la resolución del deep link una vez el host entrega el evento al runtime de navegación. La configuración de plataforma que conecta URLs, intents, universal links o bridges nativos debe delegarse a `kb-kmm-navigation-platform-behaviors`.

Los argumentos del URI se mapean automáticamente a los campos de la ruta `@Serializable` cuando se usa `navDeepLink<T>(basePath = ...)`. Para URIs custom, los placeholders `{campo}` deben coincidir con los nombres de los parámetros de la data class.

- Para los patrones de deep link dentro del grafo, ver [deeplinks.md](references/deeplinks.md)

---

## 8. ViewModel scoping

### Scoping disponible

| Scope | API | Duración |
|---|---|---|
| Pantalla (default) | helper de DI del proyecto | Vive mientras la entrada existe en el back stack |
| Nested graph | helper de DI del proyecto con `graphEntry` | Sobrevive a navegación entre rutas del mismo grafo |

Si el proyecto usa Koin, consultar `kb-koin` y la `kb-kmm-navigation-viewmodel-events`, que contiene el patron autoritativo y sus referencias de implementacion.

### Restricción: no usar `SavedStateHandle` en commonMain

`SavedStateHandle` es una API de AndroidX Lifecycle. En commonMain, pasar los argumentos al ViewModel via constructor desde el Composable usando el mecanismo de parámetros de la DI activa.

- Para ejemplos completos de scoping y paso de parametros, consultar `kb-kmm-navigation-viewmodel-events` -> `references/viewmodel-and-navigation-events.md`

---

## 9. ViewModel events y side effects

El patrón de efectos de navegación desde ViewModel no se define en esta skill.

Esta skill solo consume ese patrón cuando necesita integrarse con el grafo Compose.

- Para el patron completo de efectos y `LaunchedEffect`, consultar `kb-kmm-navigation-viewmodel-events` -> `references/viewmodel-and-navigation-events.md`
- La fuente normativa de ese patrón es `kb-kmm-navigation-viewmodel-events`

---

## 10. Animaciones de transición

Las transiciones globales se definen en el `NavHost`. Las transiciones por ruta sobreescriben las globales. Para iOS, usar solo las basadas en `AnimatedContentTransitionScope` (multiplataforma).

| Feature | Android | iOS |
|---|---|---|
| `slideIntoContainer` / `slideOutOfContainer` | Soportado | Soportado |
| `fadeIn` / `fadeOut` | Soportado | Soportado |
| Predictive back animation | Automático (Android 14+) | No aplica |
| SharedElement transitions | Experimental (CMP 1.7) | Limitado |

- Para los patrones de transición global y por ruta, ver [animations.md](references/animations.md)

---

## Requisitos NO Negociables

_Específicos de Compose Navigation + Kotlin Serialization. Si cambia la librería, revisitar._

- Rutas type-safe con `@Serializable` — sin strings hardcodeados
- `AppNavGraph` recibe el `navController` como parámetro requerido
- `SavedStateHandle.toRoute()` prohibido en `commonMain` (API de AndroidX Lifecycle, solo Android)
- Ignorar el `Boolean` de retorno de `popBackStack()` está prohibido en destinos que pueden ser entry points de deep link
- Navegación adaptativa: `NavigationBar` en Compact, `NavigationRail` en Medium, `NavigationDrawer` en Expanded

---

**Version**: 3.0.0
**Ultima actualizacion**: 2026-04-11
**Compatibilidad**: Compose Multiplatform 1.7+, Kotlin 2.0+, Navigation Compose 2.8+
