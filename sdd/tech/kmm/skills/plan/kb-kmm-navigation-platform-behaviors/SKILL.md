---
name: kb-kmm-navigation-platform-behaviors
description: "Reglas para integración de navegación con comportamientos de plataforma en KMM, como BackHandler, predictive back y bridges de deep links."
argument-hint: "[back behavior | predictive back | platform deep links]"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# kb-kmm-navigation-platform-behaviors

## Responsabilidad y alcance
Esta skill define comportamientos de navegación que dependen de integración con la plataforma o del runtime del host. Su responsabilidad es fijar cómo se conectan la navegación Compose y los eventos del sistema sin redefinir el grafo, las rutas ni la propiedad arquitectónica de la navegación.

No define:
- el contrato arquitectónico de navegación
- el patrón ViewModel -> side effect -> callback
- el grafo Compose Navigation ni las rutas type-safe
- la librería de DI del proyecto

Para esos temas, delegar en:
- `kb-kmm-navigation-contracts`
- `kb-plan-kmm-navigation-viewmodel-events`
- `kb-kmm-navigation-compose`
- `kb-plan-koin` si aplica

## Regla 1: BackHandler es un comportamiento de plataforma, no una regla de grafo
El uso de `BackHandler` pertenece a la integración con el host y al ciclo de vida de la pantalla. No debe modelarse como si fuera parte del contrato del grafo.

- Solo usar `BackHandler` cuando la pantalla necesite interceptar el gesto o botón atrás por una razón funcional clara.
- La decisión de interceptar atrás vive en la UI o en un adaptador de plataforma, no en el ViewModel como llamada directa a navegación.
- La acción resultante debe delegar a callbacks o efectos ya definidos por el contrato de navegación del proyecto.

→ Templates: `references/backhandler.md`

## Regla 2: Predictive back se trata como capacidad específica de Android
La integración con predictive back es un detalle del host Android y debe mantenerse separada del diseño general del grafo.

- No convertir predictive back en requisito global de toda navegación KMM.
- Encapsular la integración en la capa Android del host o en adaptadores específicos, manteniendo `commonMain` libre de detalles del framework Android.
- Si una pantalla no necesita integración especial, usar el comportamiento por defecto del sistema.

## Regla 3: Los deep links se separan entre resolución de grafo e integración de plataforma
La resolución de una ruta dentro del `NavHost` pertenece a la implementación de navegación Compose. La configuración que conecta URLs, intents, universal links o bridges nativos pertenece a esta skill.

- El grafo decide cómo se interpreta un deep link una vez entra en navegación.
- Android resuelve `intent-filters` y entrega el enlace al host.
- iOS resuelve universal links, custom schemes o bridges equivalentes y entrega el enlace al host.
- La plataforma nunca debe convertirse en la fuente de verdad del catálogo de destinos.

## Regla 4: La plataforma entrega eventos; app traduce; features no conocen el host
Los eventos de navegación que provienen del sistema deben entrar por el host y traducirse al contrato de navegación definido en `app`.

- La plataforma captura el evento externo.
- `app` lo adapta a una ruta o acción del grafo.
- Las features solo reciben el resultado de esa composición; no conocen intents, URLs nativas ni APIs del sistema.

## Regla 5: Las APIs de plataforma no deben contaminar la skill Compose
Cuando una decisión depende de AndroidManifest, AppDelegate, SceneDelegate, universal links, intents o contratos equivalentes del host, no pertenece a la skill de Compose Navigation.

- Mantener esas reglas en esta skill o en documentación específica de plataforma.
- La skill `kb-kmm-navigation-compose` solo debe asumir que el host ya entrega el evento al grafo.
