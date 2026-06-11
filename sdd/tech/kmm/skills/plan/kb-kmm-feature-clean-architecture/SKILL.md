---
name: kb-kmm-feature-clean-architecture
description: "Arquitectura interna de una feature KMM: capas presentation/domain/data, ubicación de contratos e implementaciones, dependencias permitidas y criterios para subir responsabilidades a core."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Arquitectura interna de feature KMM — Base de Conocimiento

## Regla 1: Esta skill define la microarquitectura de una feature, no la arquitectura global del proyecto

Esta skill regula cómo se organiza internamente cada feature. Define subcapas, ownership, dependencias permitidas y separación entre contratos e implementaciones dentro de una feature concreta.

No define:

- reglas globales entre `app`, `features` y `core`
- decisiones de DI
- librerías HTTP
- política global de auth o navegación

Si una regla sigue siendo cierta aunque la feature se mueva dentro de la arquitectura global, pertenece aquí. Si afecta a la relación entre `app`, `features` y `core`, pertenece a la skill de arquitectura global.

---

## Regla 2: Dentro de una feature se sigue separación por capas

Cada feature puede organizarse internamente en tres subcapas conceptuales:

- `presentation`: Screen, Section, ViewModel, state, events, effects y mappers de UI
- `domain`: modelos de dominio propios de la feature, repositorios como contrato y use cases
- `data`: implementaciones de repositorio, APIs remotas, DTOs, response handlers y mappers de infraestructura a dominio

La estructura exacta de carpetas puede variar por proyecto, pero la separación de responsabilidades no.

Cuando una pantalla usa ViewModel, la convención preferida del proyecto es separar esa pantalla en:

- `presentation/<pantalla>/<Pantalla>Screen.kt`
- `presentation/<pantalla>/viewmodel/<Pantalla>ViewModel.kt`
- `presentation/<pantalla>/viewmodel/<Pantalla>State.kt`
- `presentation/<pantalla>/viewmodel/<Pantalla>Intent.kt`
- `presentation/<pantalla>/viewmodel/<Pantalla>Events.kt`

→ Templates: `${CLAUDE_SKILL_DIR}/references/presentation_viewmodel_patterns.md`

---

## Regla 3: Las dependencias internas apuntan hacia dominio

La dirección correcta dentro de una feature es:

```text
presentation -> domain <- data
```

Por tanto:

- `presentation` puede depender de `domain`
- `data` puede depender de `domain`
- `domain` no depende de `presentation` ni de `data`

La feature no debe colapsar estas capas en una sola unidad si eso borra fronteras conceptuales importantes.

---

## Regla 4: `presentation` solo maneja estado y coordinación de UI

La capa `presentation` contiene la representación de pantalla y su coordinación inmediata:

- `Screen` o `Section`
- `ViewModel`
- estado de pantalla
- eventos de entrada UI -> ViewModel
- efectos de salida ViewModel -> UI
- transformaciones de dominio a modelo de presentación cuando sean necesarias para renderizar

En este proyecto, cuando existe un ViewModel de pantalla, el patrón preferido es separar entradas (`Intent`), estado (`State`) y efectos one-shot (`Events`) con un único punto de entrada `onIntent`.

→ Naming exacto, tipos, uso de `Channel` y decisiones del ViewModel: `kb-plan-kmm-navigation-viewmodel-events`

Si el estado se mantiene directamente en el ViewModel, la forma preferida es `var state by mutableStateOf(...)` con `private set`.

`presentation` no debe contener:

- lógica de acceso a red o persistencia
- DTOs
- detalles de cliente HTTP o storage
- decisiones globales de navegación fuera de callbacks o efectos

---

## Regla 5: El `ViewModel` no habla con infraestructura

El `ViewModel` consume casos de uso o contratos de dominio de la feature. No conoce implementaciones concretas ni detalles técnicos de `data`.

Reglas derivadas:

- no depende de data sources
- no depende de DTOs
- no construye requests de red ni interpreta respuestas HTTP
- no contiene lógica que pertenezca a repositorios o mappers de infraestructura

Si el `ViewModel` empieza a resolver demasiadas reglas de negocio, falta un use case o una abstracción de dominio.

---

## Regla 6: `domain` contiene las reglas estables de la feature

La subcapa `domain` define lo que la feature necesita para expresar su negocio sin acoplarse a cómo se obtiene o persiste la información.

Puede contener:

- modelos de dominio propios de la feature
- interfaces de repositorio de la feature
- use cases de la feature
- errores de dominio propios de la feature, si aplica

`domain` no contiene:

- DTOs
- anotaciones o tipos específicos de librerías de infraestructura
- implementaciones concretas de repositorio
- modelos pensados solo para renderizar UI

El criterio para decidir si un error propio de feature debe existir y cómo se relaciona con `AppError` pertenece a `kb-kmm-app-errors`.

---

## Regla 7: Los repositorios son contrato en `domain` e implementación en `data`

Dentro de una feature, el repositorio se separa en dos piezas:

- interfaz en `domain`
- implementación en `data`

La interfaz expresa operaciones en términos de dominio. La implementación conoce data sources, mapeos, caché, persistencia y composición de fuentes.

La capa superior nunca depende de la implementación concreta.

---

## Regla 8: `data` encapsula fuentes externas y detalles técnicos

La subcapa `data` contiene todo detalle necesario para cumplir los contratos de `domain`:

- repositorios concretos
- APIs remotas
- local data sources
- DTOs, entities de persistencia o modelos de transporte
- response handlers para contratos HTTP especiales, cuando hagan falta
- mappers entre infraestructura y dominio

`data` puede depender de `domain` y de infraestructura compartida. No debe filtrar sus tipos técnicos hacia `presentation` ni `domain`.

Cuando existe acceso remoto HTTP, la `Api` es la única pieza de `data` que toca el cliente HTTP. El repositorio consume esa pieza y adapta el resultado a dominio.

Si un `responseHandler` HTTP deja de ser trivial, puede extraerse a `data/responseHandlers/` para separar el request-building del parsing de contratos especiales.

→ Templates: `${CLAUDE_SKILL_DIR}/references/feature_remote_data_patterns.md`

---

## Regla 9: Los servicios remotos hablan DTO; la feature habla dominio

Los límites internos de una feature deben preservar esta separación:

- APIs consumen y devuelven DTOs o modelos técnicos
- repositorios convierten esos modelos a dominio
- use cases y `ViewModel` trabajan con modelos de dominio

Si un DTO llega al `ViewModel` o a la `Screen`, la frontera entre `data` y `domain` está rota.

Si el proyecto usa un contrato transversal de resultado y error (`AppResult<T, AppError>` o equivalente), esa abstracción puede atravesar el repositorio y llegar a use cases y ViewModel. Lo que no debe cruzar la frontera son DTOs, `HttpResponse`, status codes o excepciones del cliente HTTP.

La política de cuándo conservar un error y cuándo adaptarlo se delega a `kb-kmm-app-errors`.

---

## Regla 10: Los mappers viven junto al cambio de representación

Cada mapper debe vivir donde se transforma una representación en otra:

- DTO -> dominio en `data`
- dominio -> UI model en `presentation`, solo si ese modelo de UI realmente existe
- `AppError` -> `UiText` en `presentation` (→ `kb-kmm-app-errors` Regla 9)

No mezclar en un mismo mapper transformaciones de infraestructura y de UI. Cada capa convierte hacia la representación que necesita.

Cuando un dato cruza fronteras entre capas y representa una unidad semántica clara, la preferencia del proyecto es encapsularlo en un modelo propio de esa capa en lugar de pasarlo como variables sueltas:

- `UiModel` en `presentation`, cuando haga falta una representación de entrada o estado compuesta
- `Model` en `domain`
- `Dto` en `data`

---

## Regla 11: No todo requiere use case, pero toda lógica de negocio sí necesita un hogar explícito

Si una operación representa una regla de negocio, coordinación de varias fuentes o una transformación relevante, debe vivir en un use case o en un contrato de dominio equivalente.

No crear use cases triviales solo por ritual, pero tampoco dejar lógica de negocio dispersa en `ViewModel` o repositorios sin criterio.

La regla práctica es:

- acceso y orquestación de fuentes -> repositorio
- regla o acción de negocio -> use case
- coordinación de estado de pantalla -> `ViewModel`

Si una operación solo necesita propagar `AppResult` desde repositorio a `ViewModel`, el use case puede ser un simple pass-through. Si necesita combinar varios `AppResult`, aplicar reglas de negocio o priorizar errores, esa lógica pertenece al use case.

La política transversal de `AppResult` / `AppError` pertenece a `kb-kmm-app-errors`.

---

## Regla 12: Una feature solo conserva lo que es propio de su dominio

Algo debe quedarse dentro de una feature si su uso y significado pertenecen únicamente a esa feature.

Algo debe subir a `core` si:

- lo consumen varias features
- representa un modelo compartido del negocio
- es un caso de uso transversal
- es infraestructura reutilizable sin semántica específica de una feature

No subir piezas a `core` por anticipación. Primero deben demostrar que son realmente compartidas.

---

## Regla 13: Compartir código entre features no justifica dependencias cruzadas

Si Feature B necesita una regla o dato que hoy vive en Feature A, la solución no es depender de Feature A.

Las opciones válidas son:

- extraer el contrato o modelo compartido a `core`
- extraer el repositorio o use case compartido a `core`
- reevaluar si ambas piezas son en realidad una sola feature

Las features no se reutilizan entre sí como si fueran librerías internas.

---

## Regla 14: La navegación no forma parte del dominio interno de la feature

La feature puede emitir eventos o efectos para expresar que ocurrió algo relevante, pero no conoce rutas, destinos globales ni controladores de navegación.

Por tanto:

- los efectos describen hechos, no destinos concretos
- la `Screen` expone callbacks hacia fuera
- el `ViewModel` no recibe `Navigator` ni `NavController`

Esta regla alinea la microarquitectura de la feature con la arquitectura global de la aplicación.

---

## Regla 15: Las capas se optimizan para claridad de responsabilidades, no para ceremonias vacías

La separación en `presentation`, `domain` y `data` existe para proteger fronteras de cambio y mantener la feature escalable.

No obliga a crear un número artificial de archivos o tipos si la feature es pequeña. Pero incluso en features simples deben seguir claras estas preguntas:

- dónde vive la lógica de UI
- dónde vive la regla de negocio
- dónde viven los detalles técnicos
- qué contratos aíslan unas capas de otras

Si esas respuestas no son evidentes, la feature no está suficientemente bien separada.

---

## Regla 16: Esta skill define reglas conceptuales; otras skills concretan DI o infraestructura

Esta skill solo fija la microarquitectura interna de una feature.

- La skill de arquitectura global define cómo encaja la feature en `app / features / core`
- La skill de DI define cómo se registran sus piezas
- Las skills de networking, auth o storage definen los contratos e implementaciones técnicas concretas

Si una regla depende de Koin, Ktor, SQLDelight o cualquier otra librería, no pertenece aquí.

→ Checklist de cierre: `${CLAUDE_SKILL_DIR}/references/feature-checklist.md`
