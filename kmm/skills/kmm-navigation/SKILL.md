---
name: kb-kmm-navigation
description: Base de conocimiento sobre navegación type-safe en Compose Multiplatform: rutas @Serializable, NavHost, nested graphs, deep links, shell adaptativo, back stack, scoping de ViewModels y NavigationSideEffect.
argument-hint: "topic de navegación a consultar (opcional)"
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Compose Multiplatform — Navegación

---

## Contrato de Navegación

Estas reglas son invariantes de arquitectura, independientes de la librería de navegación que se use:

- **Rutas como tipos en `commonMain`**: cada destino es un tipo (objeto o clase), no un string. Se ubican en el paquete de navegación de `:app` accesible por todas las features sin que ellas dependan entre sí.
- **NavHost y todo el grafo en `commonMain`**: el `NavHost` y las extensiones `NavGraphBuilder` viven en `commonMain`.
- **Features exponen, no navegan**: cada feature expone una función de registro de su grafo que acepta lambdas para las acciones de salida. Nunca recibe el `NavController` — solo emite callbacks que `:app` resuelve.
- **NavController encapsulado**: el `NavController` vive en el composable shell de nivel superior. No se expone a features ni se almacena en un `CompositionLocal` global.
- **Lógica de navegación en ViewModel**: cuando la navegación depende de lógica de negocio, el ViewModel emite un `NavigationSideEffect` via `Channel` o `StateFlow`. Elegir uno y aplicarlo consistentemente en todo el proyecto. Nunca mezclar navegación con `UiEvent` — riesgo de navegaciones duplicadas en recompose.
- **Separación entre features**: `:feature:A` no depende de `:feature:B` para navegar. Solo dependen del contrato central de rutas.

Todo lo que sigue es la implementación de este contrato con Compose Navigation + Kotlin Serialization.

---

## 1. Setup y dependencias

Versión mínima: `org.jetbrains.androidx.navigation:navigation-compose:2.8+` (artifact CMP; soporta type-safe routes en `commonMain`). Requiere también `kotlin("plugin.serialization")` y `kotlinx.serialization.json` en `commonMain`.

- Para las dependencias Gradle y el plugin de serialización, ver [setup-and-routes.md](resources/setup-and-routes.md)

---

## 2. Rutas type-safe

### 2.1 Definición con `@Serializable`

Todas las rutas van en `commonMain`. Cada ruta es un `object` (sin argumentos) o una `data class` (con argumentos). Los argumentos opcionales llevan valor por defecto. Las raíces de nested graphs también son `@Serializable object`.

- Para ejemplos completos de definición de rutas, ver [setup-and-routes.md](resources/setup-and-routes.md)

### 2.2 Restricciones en commonMain

- Usar `backStackEntry.toRoute<T>()` para extraer argumentos, **nunca** `SavedStateHandle.toRoute()` (API de AndroidX Lifecycle, no disponible en `commonMain`)
- Pasar argumentos complejos como primitivos serializables, no como objetos Parcelable

---

## 3. NavHost y destinations

### 3.1 NavHost en commonMain

El NavHost y todo el grafo de navegación viven en `commonMain`. `AppNavGraph` acepta el `navController` como parámetro requerido (sin default): el owner es siempre el `AppShell` en producción o el test que lo invoca. Esto garantiza que el mismo `navController` sea compartido por el NavHost y el componente de navegación del shell (bottom bar / rail / drawer).

- Para el patrón completo de `AppNavGraph.kt` y extracción de argumentos, ver [navhost-and-backstack.md](resources/navhost-and-backstack.md)

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

- Para todos los ejemplos de back stack, ver [navhost-and-backstack.md](resources/navhost-and-backstack.md)

---

## 5. Nested NavGraphs

### 5.1 Navegar al graph vs a una ruta

`navController.navigate(MainGraph)` aterriza en el `startDestination` del graph. `navController.navigate(ProfileRoute("123"))` va directo a la ruta, en cualquier graph.

- Para ejemplos de nested graphs, ver [nested-graphs-and-multimodule.md](resources/nested-graphs-and-multimodule.md)

### 5.2 Feature modules con grafos independientes

Cada feature expone `fun NavGraphBuilder.featureGraph(...)` con lambdas para las acciones de salida. El feature **nunca** recibe el `NavController` — solo emite callbacks que `:app` resuelve.

Las rutas se centralizan en `:app/navigation/`. Features nunca dependen entre sí ni conocen rutas de otros features — solo dependen del contrato central. El `NavController` nunca sale de `:app`.

- Para la estructura de módulos y el patrón de registro de grafos, ver [nested-graphs-and-multimodule.md](resources/nested-graphs-and-multimodule.md)

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

- Para los tres layouts completos (`AppShell`, `CompactLayout`, `MediumLayout`, `ExpandedLayout`), ver [bottom-nav-and-adaptive.md](resources/bottom-nav-and-adaptive.md)

---

## 7. Deep Links

Los argumentos del URI se mapean automáticamente a los campos de la ruta `@Serializable` cuando se usa `navDeepLink<T>(basePath = ...)`. Para URIs custom, los placeholders `{campo}` deben coincidir con los nombres de los parámetros de la data class.

Requiere configuración en `AndroidManifest.xml` (Android) y en `Info.plist` / `Entitlements` (iOS Universal Links).

- Para todos los patrones de deep link y configuración por plataforma, ver [deeplinks.md](resources/deeplinks.md)

---

## 8. ViewModel scoping

### Scoping disponible

| Scope | API | Duración |
|---|---|---|
| Pantalla (default) | `koinNavViewModel()` | Vive mientras la entrada existe en el back stack |
| Nested graph | `koinViewModel(viewModelStoreOwner = graphEntry)` | Sobrevive a navegación entre rutas del mismo grafo |

### Restricción: no usar `SavedStateHandle` en commonMain

`SavedStateHandle` es una API de AndroidX Lifecycle. En commonMain, pasar los argumentos al ViewModel via constructor desde el Composable usando `parametersOf(route.userId)`.

- Para ejemplos completos de scoping y paso de parámetros, ver [viewmodel-and-navigation-events.md](resources/viewmodel-and-navigation-events.md)

---

## 9. NavigationSideEffect desde ViewModel

### Opciones

**`Channel<NavigationEvent>` (BUFFERED)** — garantiza entrega única; el canal se cancela con el scope del `LaunchedEffect`.

**`StateFlow` con reset** — modelo UDF puro; requiere llamar a `onEffectHandled()` tras consumir el evento.

### Regla del `LaunchedEffect`

La key depende del patrón:
- **Channel:** usar `LaunchedEffect(viewModel)` — colecta el Flow una sola vez mientras el ViewModel vive; se reinicia si el Composable re-entra con un ViewModel distinto
- **StateFlow:** usar `LaunchedEffect(uiState.effect)` — el bloque se re-ejecuta cuando el valor del efecto cambia; `LaunchedEffect(viewModel)` no sirve aquí porque StateFlow emite un snapshot, no un stream continuo

Nunca usar `LaunchedEffect(Unit)` — no detecta cambios de ViewModel en re-entradas a la composición.

**Tradeoffs:**

| | `Channel` (BUFFERED) | `StateFlow` con reset |
|---|---|---|
| Entrega única | Garantizada por el Channel | Manual (`onEffectHandled`) |
| Testabilidad | Requiere `runTest` + `launch` | Snapshot directo del estado |
| Consistencia UDF | Rompe el modelo estado puro | 100% UDF |
| Pérdida de eventos | Imposible (buffered) | Posible si se resetea antes de colectar |

- Para ambos patrones completos (ViewModel + Composable), ver [viewmodel-and-navigation-events.md](resources/viewmodel-and-navigation-events.md)

---

## 10. Animaciones de transición

Las transiciones globales se definen en el `NavHost`. Las transiciones por ruta sobreescriben las globales. Para iOS, usar solo las basadas en `AnimatedContentTransitionScope` (multiplataforma).

| Feature | Android | iOS |
|---|---|---|
| `slideIntoContainer` / `slideOutOfContainer` | Soportado | Soportado |
| `fadeIn` / `fadeOut` | Soportado | Soportado |
| Predictive back animation | Automático (Android 14+) | No aplica |
| SharedElement transitions | Experimental (CMP 1.7) | Limitado |

- Para los patrones de transición global y por ruta, ver [animations.md](resources/animations.md)

---

## 11. BackHandler y Predictive Back

`BackHandler` en commonMain viene de `androidx.compose.ui.platform` (CMP 1.6+). **No usar** `androidx.activity.compose.BackHandler` — es Android-only y rompe la compilación en iOS/Desktop.

Para predictive back en Android 13+, declarar `android:enableOnBackInvokedCallback="true"` en `AndroidManifest.xml`. En iOS, el gesto de swipe-back es manejado automáticamente por UIKit.

- Para el ejemplo de `BackHandler` con formularios, ver [backhandler.md](resources/backhandler.md)

---

## 12. Testing de navegación

`TestNavHostController` requiere `android.content.Context` — los tests de integración del grafo son **instrumentados (Android)** y van en `androidTest/`, no en `commonTest`.

Los únicos tests que van en `commonTest` son los del ViewModel (usando fake del canal de navegación).

- Para los tres patrones de test (integración de grafo, verificación de ruta, fake para ViewModel), ver [testing.md](resources/testing.md)

---

## Requisitos NO Negociables

_Específicos de Compose Navigation + Kotlin Serialization. Si cambia la librería, revisitar._

- Rutas type-safe con `@Serializable` — sin strings hardcodeados
- `AppNavGraph` recibe el `navController` como parámetro requerido; el owner es siempre el shell o el test
- `LaunchedEffect(viewModel)` como key en el patrón Channel; `LaunchedEffect(uiState.effect)` en el patrón StateFlow; nunca `LaunchedEffect(Unit)`
- Scoping de ViewModel con `koinNavViewModel()` o equivalente (Hilt: `hiltViewModel()`), nunca instanciación directa
- `SavedStateHandle.toRoute()` prohibido en `commonMain` (API de AndroidX Lifecycle, solo Android)
- `androidx.activity.compose.BackHandler` prohibido en `commonMain` — usar `androidx.compose.ui.platform.BackHandler`
- Ignorar el `Boolean` de retorno de `popBackStack()` está prohibido en destinos que pueden ser entry points de deep link
- Navegación adaptativa: `NavigationBar` en Compact, `NavigationRail` en Medium, `NavigationDrawer` en Expanded
- Tests de integración del grafo en `androidTest` (instrumentados), no en `commonTest`

---

**Version**: 3.0.0
**Ultima actualizacion**: 2026-04-11
**Compatibilidad**: Compose Multiplatform 1.7+, Kotlin 2.0+, Navigation Compose 2.8+
