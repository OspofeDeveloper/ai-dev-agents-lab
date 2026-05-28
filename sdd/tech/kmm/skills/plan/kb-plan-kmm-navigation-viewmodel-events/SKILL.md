---
name: kb-plan-kmm-navigation-viewmodel-events
description: "Base de conocimiento de eventos y efectos de navegación desde ViewModel en proyectos KMM: patrón Intent/Events, Channel vs StateFlow, reglas de LaunchedEffect y separación entre lógica de negocio, Composable y destino concreto."
argument-hint: ""
effort: low
allowed-tools: [Read]
user-invocable: false
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

## Regla 3: El ViewModel separa estado renderizable de efectos de una sola vez

El ViewModel tiene dos responsabilidades distintas y no deben colapsarse:

- `State`: lo que la pantalla puede renderizar de forma estable
- `Events`: efectos de una sola vez que la UI debe consumir

Regla práctica:

- si algo cambia lo que la pantalla muestra de forma persistente, va en `State`
- si algo dispara una acción puntual como navegar, abrir diálogo o lanzar snackbar, va en `Events`

No usar el estado persistente para modelar decisiones de flujo que la app debe traducir externamente.

→ Patterns: `references/viewmodel-and-navigation-events.md`

---

## Regla 4: Los errores renderizables viven en `State`; los outcomes de flujo viven en `Events`

No todo error es un efecto.

Cuando un error solo cambia la UI de la pantalla actual, debe representarse como estado renderizable de pantalla.

Ejemplos típicos:

- credenciales inválidas
- cuenta bloqueada
- error genérico de red mostrado en la propia screen

Cuando el resultado representa un hecho de flujo que puede traducirse distinto según app, brand o contexto, debe emitirse como `Event`.

Ejemplos típicos:

- `LoginSuccess`
- `FirstLoginRequired`
- `AccountInactive`
- `SessionExpired`

La diferencia clave no es si algo "es error" o "no es error", sino si la consecuencia es renderizable localmente o si requiere una decisión externa de composición o navegación.

---

## Regla 5: El ViewModel no decide comportamientos dependientes de app, brand o routing

Si ante un mismo hecho una app navega y otra muestra un error, esa decisión no pertenece al ViewModel de la feature.

El ViewModel emite el hecho semántico una sola vez. La capa `app` o el `NavHost` decide cómo traducirlo:

- navegar a un destino
- mostrar snackbar o diálogo
- activar otra composición

Esto aplica especialmente a diferencias por brand, flavor o contexto global.

La ownership de esa decisión vive en `kb-kmm-app-layer`.

---

## Regla 6: Los efectos one-shot se emiten siempre con `Channel`

El patrón del proyecto es `Channel` con entrega única. No se usa `StateFlow` con reset manual para efectos one-shot.

→ Patterns: `references/viewmodel-and-navigation-events.md`

## Regla 7: Los eventos de entrada usan el naming `Intent`

Cuando una pantalla modela entradas UI -> ViewModel, la convención preferida del proyecto es usar `<Pantalla>Intent` como sealed interface de entrada.

El ViewModel expone `onEvent(intent: <Pantalla>Intent)` como único punto de entrada de eventos de UI.

## Regla 8: Los efectos de salida usan el naming `Events`

Cuando el patrón usa `Channel` o un stream equivalente para efectos de salida, la convención preferida es `<Pantalla>Events`.

Ese tipo representa hechos emitidos por el ViewModel hacia la UI, no entradas del usuario ni destinos concretos.

## Regla 9: La key de `LaunchedEffect` para `Channel`

Con `Channel`, usar siempre `LaunchedEffect(viewModel)` como key.

`LaunchedEffect(Unit)` no es válido porque oculta cambios de owner o re-entradas relevantes.

→ Patterns: `references/viewmodel-and-navigation-events.md`

## Regla 10: Los efectos de navegación no se mezclan con `Intent`

Los `Intent` modelan interacción de entrada.

Los efectos de navegación modelan salidas o consecuencias de estado.

Mezclarlos aumenta el riesgo de eventos duplicados, recolección incorrecta o navegación repetida por recomposición.

---

## Regla 11: El ViewModel tiene prohibido conocer destinos concretos o mecanismos de navegación

El ViewModel no debe:

- recibir `NavController`, `Navigator` o equivalentes
- emitir rutas concretas, `Route`, `Destination` o ids del grafo global
- decidir `popBackStack`, `navigate`, `replace` o variantes concretas
- inyectar estrategias cuyo único propósito sea elegir una acción de app para un mismo hecho semántico

Si una abstracción existe solo para decidir si ante un hecho se navega, se muestra error o se compone otra pantalla, esa abstracción pertenece a `app`, no al ViewModel de feature.

---

## Regla 12: Los modelos de `State` deben ser semánticos de UI, no decisiones finales de render

Cuando un error o resultado vive en `State`, la preferencia es modelarlo como tipo semántico de UI y no como texto final o instrucción de navegación.

Ejemplos válidos:

- `LoginError.InvalidCredentials(attemptsRemaining)`
- `LoginError.AccountBlocked`
- `LoginError.Generic`

Ejemplos no válidos como SSoT del ViewModel:

- strings literales finales
- rutas
- decisiones de brand sobre qué hacer con el mismo outcome

La Screen puede mapear ese estado semántico a `UiText`, recursos o componentes concretos.

---

## Regla 13: Esta skill no define DI ni librería de navegación

Esta skill solo define el patrón de coordinación ViewModel ↔ Composable para navegación.

No define:

- `NavHost`
- rutas
- `NavController`
- Koin u otra DI

La navegación concreta vive en `kb-kmm-navigation-compose`.

## Checklist antes de cerrar

- ¿Los eventos de entrada se llaman `<Pantalla>Intent`?
- ¿Los efectos de salida se llaman `<Pantalla>Events`?
- ¿El `State` solo contiene datos renderizables y no decisiones de flujo?
- ¿Los errores renderizables están en `State` y los outcomes de flujo en `Events`?
- ¿El mismo hecho semántico se emite una sola vez sin bifurcarse por brand dentro del ViewModel?
- ¿Cada efecto nombra un hecho y no un destino concreto?
- ¿El ViewModel evita `NavController`, rutas y estrategias de routing dependientes de app?
- ¿La recolección de efectos usa `LaunchedEffect(viewModel)` con `Channel`?
