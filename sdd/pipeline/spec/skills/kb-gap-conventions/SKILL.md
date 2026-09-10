---
name: kb-gap-conventions
description: "Convenciones SSoT del sistema de gaps y marcadores del pipeline SDD: formatos de ID, severidades, marcador de pendiente y reglas de bloqueo."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Gap Conventions — SSoT de Gaps y Marcadores SDD

Este skill es el **Single Source of Truth** para todas las convenciones de gaps y marcadores de la fase Spec en adelante (analyze, fast-track, delta, caracterización, plan). Consúltalo antes de generar, formatear o verificar cualquier gap en cualquier modo.

> **Marcador de la fase PRD — fuera de este skill**: la red anti-fabricación del PRD usa `[ASUNCIÓN]` (afirmación de negocio inferida, no trazable a la fuente, pendiente de confirmación humana en `wf-prd-review`). No es un gap del pipeline ni lo gestionan los gates de spec; su SSoT es `kb-prd-expert` (Regla 12).

---

## Formatos de ID de gap

| Contexto | Prefijo | Ejemplo |
|----------|---------|---------|
| Análisis de documento origen (modos `analyze`, `fast-track`) | `[P-XXX]` | `[P-001]`, `[P-042]` |
| Análisis de cambios incrementales (modo `delta`) | `[D-XXX]` | `[D-001]`, `[D-003]` |

**Numeración**: secuencial desde `001` y **por linaje** — no por artefacto. Sin saltos, salvo los **bloques reservados** del fan-out paralelo ([[D-056]], abajo), que sí los dejan a propósito.

Un linaje es el `_analysis.md` de un documento origen **más todos los specs derivados de él**.
Los IDs no se reinician al pasar del análisis al spec: si el análisis llegó a `[P-008]`, el
primer gap que levante un spec de ese linaje es `[P-009]`. El ID se pide al script, que escanea
**todos** los ficheros del linaje:

```bash
!python3 .sdd/scripts/sdd-next-id.py P <analysis.md> <spec_1.md> <spec_2.md> …
```

> **Por qué por linaje y no por artefacto ([[D-054]]).** Un spec referencia gaps de los dos
> sitios a la vez: su marcador dice `Pendiente de gap(s): [P-011]` sin decir en qué fichero
> vive. Si cada artefacto reiniciara en `001`, dos gaps distintos compartirían ID dentro del
> mismo spec y el marcador sería ambiguo — y `wf-spec-gap-resolve`, que resuelve por ID, no
> podría saber a cuál se refiere. Medido: un writer continuó la numeración por su cuenta
> (analysis hasta `P-008`, spec desde `P-009`) **contradiciendo esta regla tal como estaba
> escrita**, y acertó. La regla se alinea con lo que la práctica ya demostró correcto.

**El fan-out paralelo: quien reparte es quien los ve a todos ([[D-056]]).** El linaje se calcula
sobre lo que hay **en disco**, así que varios escritores lanzados a la vez piden todos el mismo
"siguiente ID libre": sus specs todavía no existen. **No lo resuelve el escritor, lo resuelve quien
lanza**: `wf-spec-features-first` pide el primer ID libre del linaje y reparte **bloques de 10**,
uno por escritor, que viajan en `--gap-id-start`. Los huecos entre bloques son deliberados — un ID
sin usar no cuesta nada; dos gaps distintos con el mismo ID corrompen la trazabilidad.

> **Esto no era un riesgo teórico.** Se documentó como *"puede pasar en un fan-out paralelo"* y
> pasó en la **primera** pasada paralela siguiente (11 de CU-3.a): con 4 escritores,
> `movement-tracking` y `debt-tracking` reclamaron los dos `[P-009]` para gaps distintos —uno
> informativo, otro crítico y bloqueante—.

**Lo que sigue sin poder garantizarse: regenerar el análisis.** `wf-spec-analyze` numera desde
`001` dentro de su documento, así que un análisis regenerado con **más** gaps que el anterior
invade el rango que los specs derivados ya reclamaron. No se arregla desplazando su base: el
rescate de respuestas (`--export/--import-answers`) empareja por **ID y título**, y moverla
garantizaría **cero** coincidencias, perdiendo decisiones de negocio que valen más que la unicidad
del ID. Y el riesgo de fondo no es nuevo: tras regenerar, los `P-XXX` del análisis **ya no
significan lo mismo**, colisionen o no (ver `wf-spec-analyze`, "Rescatar las respuestas antes de
sobrescribir").

**Lo que sostiene la resolución en todos los casos** es la regla de arriba: se busca **primero en el
spec**. Y el corolario se mantiene: un `P-XXX` **no identifica un gap por sí solo fuera de su
spec** — al citarlo en un informe, en un conflicto o al usuario, nómbralo junto al fichero donde
vive.

---

## Dónde vive un gap: dos hogares, y cuál manda ([[D-054]])

Un `[P-XXX]` puede estar definido en **uno de dos sitios**, y los dos son legítimos:

| Hogar | Cuándo | Quién lo escribe |
|---|---|---|
| `_analysis.md` del documento origen | El gap sale de leer el PRD | `wf-spec-analyze` |
| `## Items Pendientes` del propio spec | El gap **nace al escribir el spec** | `wf-spec-fast-track` (Paso 6, "gap handling inline") |

**La doble ubicación no es un accidente: es forzosa.** `wf-spec-fast-track` corre con `--analysis`
**opcional** —en modo directo (`--capability`) y en todo el onramp brownfield de
`wf-spec-from-code` no hay ningún `_analysis.md`—, así que el spec tiene que poder alojar sus
propios gaps o esas dos entradas del pipeline se quedan sin sitio donde ponerlos.

Y hay una clase de gap que el análisis **estructuralmente no puede contener**: el de **segundo
orden**, que nace del cruce de dos respuestas. Medido (conformance, 2026-09-07): la respuesta a
un gap fijó una relación 1:1 y la de otro introdujo 1:N; el cruce de ambas —"¿y si cambias el
importe cuando hay reparto?"— no existía cuando se escribió el análisis, porque las respuestas
no existían. El análisis se deriva del **PRD**; ese gap se deriva de las **respuestas**.

**Regla de resolución — manda dónde está definido el bloque.** Quien resuelva un `[P-XXX]`
referenciado por un spec lo busca **primero en el `## Items Pendientes` de ese spec** y, si no
está ahí, en el `_analysis.md` del linaje. La respuesta se escribe **en el fichero donde vive el
bloque**, con la misma vía sancionada de [[D-042]]:

```bash
!python3 .sdd/scripts/sdd-analysis-gaps.py "<fichero donde vive el gap>" --answer P-XXX "texto"
```

**Un gap tiene UN solo bloque respondible ([[D-057]]).** Lo que hace respondible a un bloque es su
campo `- **Respuesta**:`. Si el mismo `[P-XXX]` tiene ese campo en dos ficheros, hay **dos sitios
donde contestar y ninguno manda**: responder en uno deja el otro en `_(pendiente)_` para siempre, y
los dos documentos acaban diciendo cosas distintas sobre la misma decisión.

Por eso `## Items Pendientes` es **solo** para los gaps que **nacen al escribir ese spec**. Un gap
del análisis que afecta a la feature **se referencia, no se reproduce**: se anota en
`## Asunciones Aplicadas` —citando su ID, su fichero y la asunción que aplicaste— y **sin** campo
`Respuesta`, porque ese gap ya tiene el suyo en el análisis.

```markdown
- **[A-002]** (sobre [P-007], que vive en `prd/prd_analysis.md` y sigue sin responder): cuentas y
  tarjetas se tratan igual en esta feature. Si se responde allí y la respuesta cambia esto, pide
  que se actualice este spec.
```

> **Medido (pasada 11 de CU-3.a).** Un spec heredó `[P-007]` del análisis y lo reprodujo entero en
> sus `Items Pendientes`, con su propio `- **Respuesta**: _(pendiente)_`. El writer **declaró la
> herencia y citó el fichero de origen** —hizo lo cuidadoso— pero el resultado eran dos bloques
> respondibles para una sola pregunta. No es un caso de descuido: es que la regla no existía.

El script es **agnóstico al documento**: parsea cualquier fichero con bloques de gap, así que
`--list`, `--check` y `--answer` funcionan igual sobre un `_analysis.md` que sobre un `_spec.md`.
Un `--check` contra el análisis **no dice nada** sobre los gaps que viven en el spec: si un spec
tiene `[INCOMPLETO]`, hay que checkear **el spec**.

---

## La forma del bloque de gap es contrato, no estilo ([[D-058]])

Un gap se escribe **siempre** así, viva donde viva —en el `_analysis.md` o en el
`## Items Pendientes` de un spec—:

```markdown
### [P-XXX][SEVERIDAD] Título del gap
- **Contexto**: …
- **Pregunta para el cliente**: …
- **Respuesta**: _(pendiente)_
```

**Encabezado `###` con el ID entre corchetes, y los campos como bullets `- **Campo**: valor`.**
No es una preferencia de formato: es lo que parsea `sdd-analysis-gaps.py`, y de ese parseo cuelgan
`--list` (lo que se le enseña al usuario), `--check` (el gate) y `--answer` (la única vía
sancionada para escribir una respuesta, [[D-042]]).

> **Qué pasa si se escribe de otra forma (medido, pasada 12 de CU-3.a).** Un spec puso sus gaps
> como lista de viñetas —`- **[P-011][INFORMATIVO]** …`— con todo el contenido correcto. El script
> **dejó de verlos**: `--check` devolvió `VACUOUS` y `--answer P-011` falló con exit 2 sin tocar el
> fichero. **Falla ruidosamente**, que es el diseño de [[D-037]] —nunca decir *"0 abiertos"* sobre
> algo que no se ha sabido parsear—, y en aquel caso eran informativos, así que no bloqueó nada.
> Con un `[CRÍTICO]` ese gap habría quedado **inalcanzable desde la vía sancionada**: el gate
> denegando el plan y el script incapaz de responderlo. Tercera vía posible hacia el callejón de
> [[D-054]], esta vez por el formato.

**Corolario para quien escribe:** si tu caso no encaja en las plantillas, adapta **la prosa** de la
cabecera —esa es tuya— pero **no la forma del bloque**.

---

## Severidades

### Marcador advisory opcional: `[PUEDE_REQUERIR_CR]`

Se puede añadir como marcador complementario a un gap cuando la propia pregunta o una futura respuesta tienen alta probabilidad de convertirse en change request de producto.

Formato:

- `[P-001][CRÍTICO][PUEDE_REQUERIR_CR]`
- `[P-002][INFORMATIVO][PUEDE_REQUERIR_CR]`

Uso:

- no cambia por sí solo la severidad del gap
- no bloquea automáticamente el pipeline
- obliga al agente y al usuario a reevaluar la respuesta con `kb-product-change-governance` antes de derivar discovery/specs si la respuesta introduce expansión de capacidad

Casos típicos:

- la respuesta puede introducir un catálogo persistente nuevo
- la respuesta puede añadir una nueva granularidad funcional
- la respuesta puede crear un flujo de usuario no comprometido en el PRD
- la respuesta puede convertir una referencia implícita en una capacidad gestionable explícita

### `[CRÍTICO]`

Marca las HUs afectadas como `[INCOMPLETO]` en el spec si no se responde. El spec se genera igualmente, pero las HUs incompletas no pueden avanzar a plan/tasks. Aplica cuando el gap impide:
- Definir un CA verificable (GIVEN/WHEN/THEN completo e inequívoco)
- Identificar el actor principal de un Journey
- Determinar el estado de éxito de un Journey
- Resolver una regla de negocio con interpretaciones funcionales incompatibles entre sí

Formato completo: `[P-001][CRÍTICO]` o `[D-001][CRÍTICO]`

### `[INFORMATIVO]`

No bloquea. Se avanza aplicando la "Asunción por defecto" declarada si el humano no responde. Aplica para:
- Edge cases con comportamiento conservador asumible
- Prioridad relativa entre opciones igualmente válidas
- Comportamiento en condiciones poco probables
- Preferencias de UX menores que no afectan la funcionalidad core

Formato completo: `[P-002][INFORMATIVO]` o `[D-002][INFORMATIVO]`

**Obligatorio**: todo gap `[INFORMATIVO]` debe incluir una "Asunción por defecto" que declare explícitamente qué se aplicará si el humano no responde.

---

## Marcador de pendiente

El marcador `_(pendiente)_` se inserta en el campo **"Respuesta"** de cada gap hasta que el humano lo reemplaza con su respuesta real.

### Formato de un gap en un informe de análisis

```markdown
### [P-001][CRÍTICO] Título descriptivo del gap
- **Contexto**: [dónde se detectó el gap en el documento]
- **Afecta**: [HU-001, HU-003 — lista de HUs que no pueden completarse sin esta respuesta]
- **Pregunta para el cliente**: [pregunta concreta y específica — sin inventar opciones]
- **Respuesta**: _(pendiente)_

### [P-002][INFORMATIVO] Título descriptivo del gap
- **Contexto**: [dónde se detectó el gap en el documento]
- **Pregunta para el cliente**: [pregunta concreta y específica]
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: [qué se aplicará si el cliente no responde]
```

> **Nota sobre `Afecta`**: El campo `Afecta` es obligatorio en gaps `[CRÍTICO]` y permite trazar qué HUs quedarán marcadas como `[INCOMPLETO]` si el gap no se responde. No aplica a gaps `[INFORMATIVO]` (estos siempre tienen asunción por defecto).

---

## Quién escribe las respuestas — ámbito cerrado ([[D-042]])

Las respuestas de los `[P-XXX]` son **decisiones de negocio del usuario**. Quién puede escribirlas, y con qué mecanismo, es una tabla cerrada — no una zona a improvisar:

| Qué | Quién | Mecanismo |
|---|---|---|
| Responder un `[P-XXX]` | **el usuario** | edita el `_analysis.md` y sustituye `_(pendiente)_` — **vía normativa** |
| El usuario **dicta** la respuesta en la conversación | el hilo principal | `sdd-analysis-gaps.py <analysis.md> --answer P-XXX "texto"` por `Bash` |
| El **contenido** de una respuesta | nadie más | ni el hilo principal ni un agente la inventan, completan ni interpretan |
| Saber si quedan gaps abiertos | cualquiera | `sdd-analysis-gaps.py <analysis.md> --check` |

**El hilo principal nunca hace `Read`/`Edit`/`Write` del `_analysis.md`.** Vale **aunque tenga esas tools disponibles**: el `allowed-tools` de un skill no es enforcement duro ([[D-038]]), así que la restricción es normativa. Lo único que main ejecuta sobre el fichero es el script — mismo reparto que `wf-prd-review` con `sdd-prd-apply.py`.

El motivo de que el dictado vaya por script y no por edición del agente: sustituir `_(pendiente)_` por un texto dado es una **operación mecánica sin juicio**, y una operación sin juicio no se delega a un modelo ([[D-030]]). Además deja precondiciones fail-safe que una edición libre no da: no se sobrescribe en silencio una respuesta ya escrita por una persona, y un `P-XXX` inexistente se rechaza listando los válidos.

---

## Reglas de bloqueo para orquestadores

Los orquestadores verifican la presencia de marcadores pendientes antes de avanzar al siguiente paso del pipeline:

### En `wf-prepare-plan` (generar plan desde spec)

| Condición en el `_spec.md` | Acción del orquestador |
|-----------------------------|------------------------|
| Hay HUs marcadas `[INCOMPLETO]` | **Bloquear**: listar las HUs incompletas y los gaps que las bloquean |
| Hay gaps `[CRÍTICO]` **abiertos** en `## Items Pendientes` (con `Respuesta: _(pendiente)_`) | **Bloquear**: un crítico respondido NO bloquea — su bloque se conserva por trazabilidad ([[D-054]]); lo que bloquea es la respuesta pendiente |
| Hay CAs marcados `[INFERIDO]` (caracterización) | **Bloquear**: igual que `[INCOMPLETO]` — comportamiento no confirmado |
| Hay gaps `[INFORMATIVO]` con `_(pendiente)_` pero no `[INCOMPLETO]` | **Continuar** con advertencia — su asunción por defecto ya está aplicada y debe constar en `## Asunciones Aplicadas` ([[D-063]]) |
| Sin marcadores pendientes | **Continuar** normalmente |

**No verifiques esto a ojo ni con un `grep` propio.** La autoridad es
`sdd-seal.py spec <path> --check`, que además comprueba lo que ningún marcador delata:
`status_sync` no fiable, deriva respecto al PRD origen, CAs sin HU padre y asunciones aplicadas sin
rastro. Un spec **no es sellable** si falla cualquiera de esas condiciones. La tabla de arriba
describe **qué** bloquea; el script es **quien** lo dice.

> **Esta tabla omitía `[CRÍTICO]` ([[D-067]]).** Se autodeclaraba SSoT y su patrón literal de
> verificación —el que un auditor copia tal cual— dejaba pasar un crítico abierto que el sellador
> sí deniega. Cuatro ficheros definían este conjunto y ninguno coincidía con el script. Ahora hay
> una definición y tres citas.

---

## Convenciones para "Asunción por defecto" — y por qué no es un detalle menor

- Debe ser la opción **más conservadora** (la que minimiza las asunciones funcionales)
- Debe ser **específica**: no "se comportará de forma estándar" sino "se mostrará un mensaje de error genérico y el usuario permanecerá en la pantalla actual"
- Se documenta en el spec generado en la sección `## Asunciones Aplicadas`
- En modo `delta`, se documenta en la sección `## Asunciones Aplicadas (vX.Y)` del spec actualizado

Un `[INFORMATIVO]` sin responder **no se queda sin decidir**: se aplica su `Asunción por defecto`,
y esa asunción entra en los CAs del spec como si alguien la hubiera elegido. Es la opción
conservadora, así que **no expande** el producto — pero sigue siendo una decisión tomada en nombre
de una persona que quizá nunca supo que existía.

Dos consecuencias:

- **La asunción se enseña, no se resume.** El script la emite en `--list --json` (campo `asuncion`)
  para que quien presente el gap la muestre **verbatim**, igual que el `contexto` y el `problema`.
- **Confirmar una asunción se escribe.** Si la persona la revisa y dice «sí, esa está bien», eso se
  aplica con `--answer` **con el texto de la asunción**, no se deja en `_(pendiente)_`. La
  diferencia importa: `_(pendiente)_` significa *nadie lo ha mirado*; una respuesta significa
  *alguien lo decidió*. Aguas abajo son cosas distintas.

**Los `[INFORMATIVO][PUEDE_REQUERIR_CR]` son el caso que no se puede pasar por alto.** Ese flag
declara que **la respuesta podría mover el producto**. Si nunca se pregunta, la vía de gobernanza
que el flag existe para abrir no se recorre jamás — no porque se eligiera lo conservador, sino
porque nadie lo planteó. Se surfacean **siempre**, aunque la persona decline revisar el resto.

---

## La obligación de marcar rige **cada escritura** sobre el spec ([[D-063]])

`## Asunciones Aplicadas` no es un trámite de la generación: es el invariante de que **nada de lo
que dice el spec fue decidido en silencio**. Y un invariante que mantiene *un* workflow no es un
invariante del artefacto — hay que preguntarse **quién más escribe ese fichero** ([[D-039]], que
aprendió esto en el PRD). Sobre un spec escriben cuatro:

| Escritor | Cuándo | Qué debe marcar |
|---|---|---|
| `wf-spec-fast-track` | al generarlo | la asunción de cada `[INFORMATIVO]` que aplique |
| `wf-spec-delta` | al evolucionarlo | ídem, en `## Asunciones Aplicadas (vX.Y)` |
| `wf-spec-gap-resolve` | al integrar una respuesta | **lo que complete más allá de lo que la respuesta dice** |
| `wf-spec-amend` | al aclarar un CA | **el dato que fije y que el CA no determinaba** |

Los dos últimos son los que se olvidan, porque no "generan": integran. Pero una respuesta a un gap
casi nunca trae todo lo que hace falta para cerrar una HU, y lo que falte lo pone quien escribe.
**Si lo pusiste tú y no sale de lo que te dijeron, es una asunción y va anotada** — con su
`[A-00X]`, citando de dónde sale (el gap, la respuesta, la enmienda). Numera continuando desde el
`[A-00X]` más alto presente; si la sección no existe, créala arrancando en `A-001`.

**Dos escapatorias, nombradas para que no se cuelen** (son las de [[D-039]], que se colaron en el
PRD precisamente por sentirse inocentes):

- **Estrechar o reinterpretar un CA, una exclusión o una regla transversal que ya estaba es una
  decisión, no higiene.** Se cuela porque se siente como limpieza: *"si no matizo este CA queda
  contradictorio con la respuesta nueva"*. Matizarlo está bien; matizarlo **sin marca** no.
- **No vale diferir una decisión de alcance a la fase siguiente.** Dejar para Design o para Plan
  *"el detalle fino"* mientras resuelves por tu cuenta la frontera de lo que la feature hace es el
  patrón exacto que se midió en el PRD: **diferir lo pequeño y decidir lo grande**. Materia de
  Design es el cómo; qué hace el producto es de aquí para arriba.

**Backstop mecánico, y lo que NO cubre.** `sdd-seal.py spec --check` deniega el sello si un gap
`[INFORMATIVO]` sin responder no tiene entrada que lo cite en `## Asunciones Aplicadas` ([[D-063]]):
la decisión está tomada —su asunción ya vive en los CAs— así que tiene que verse. Lo que ese check
**no** puede hacer es decidir si una frase traza a lo que te dijeron: eso es juicio semántico y no
es mecanizable ([[D-039]] ya lo descartó). Lo mecanizable es que la decisión sea **visible**; que
esté **bien** es tuyo.

---

## Marcadores de specs de caracterización: `[INFERIDO]` y `[SOSPECHA_BUG]`

Solo aplican en specs con `Origen: characterization` (brownfield, generados por `wf-spec-from-code`):

- **`[INFERIDO]`** — a nivel de CA: comportamiento deducido del código pero no observado con evidencia directa. **Bloquea igual que `[INCOMPLETO]`** (gates y sellador lo verifican mecánicamente). Se resuelve con confirmación humana en `/wf-spec-gap-resolve`.
- **`[SOSPECHA_BUG]`** — nota informativa (no bloquea): el comportamiento documentado parece defectuoso; el CA describe igualmente lo que el código hace. Deriva a decisión de producto (`wf-spec-delta` o `wf-bug`).

El detalle normativo (jerarquía de evidencia, formato, degradación sin tests) vive en `kb-spec-characterization`.

---

## Marcador de HU incompleta: `[INCOMPLETO]`

El marcador `[INCOMPLETO]` se aplica a nivel de HU en el spec generado cuando un gap `[CRÍTICO]` que la afecta (campo `Afecta`) quedó sin respuesta.

### Formato en el spec generado

Al final de cada HU afectada:
```markdown
> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001], [P-003]. Responde esos gaps en <dónde viven> y pide que se complete la HU.
```

**`<dónde viven>` no es decorativo: es la diferencia entre una salida y un callejón** ([[D-054]]).
Un gap tiene dos hogares, así que la frase nombra el que corresponde:

| Los gaps del marcador vienen de… | La frase dice |
|---|---|
| El análisis del documento origen | ``Responde esos gaps en `prd/prd_analysis.md` `` (la ruta real) |
| El `## Items Pendientes` de este mismo spec | `Responde esos gaps en la sección «Items Pendientes» de este spec` |
| Los dos hogares a la vez | Nombra cada uno con sus IDs: ``[P-002] en `prd/prd_analysis.md`, [P-009] en «Items Pendientes»`` |

> **Por qué esto está escrito con esta insistencia (medido, pasada 11 de CU-3.a).** Esta plantilla
> decía *"Responde esos gaps en el `_analysis.md`"*, fijo. Un spec salió con
> `Pendiente de gap(s): [P-009]` —un gap que vivía en su **propia** sección— y esa frase mandaba al
> usuario a un fichero donde `[P-009]` no existe. Es el callejón de [[D-054]] otra vez, por la vía
> del texto en vez de la de las herramientas: el writer copió la plantilla, que es exactamente lo
> que se le pide hacer.


> **Qué es contrato y qué es prosa, en esta misma línea** (ROADMAP 11.10). El marcador
> `[INCOMPLETO]`, el prefijo `Pendiente de gap(s):` y los `[P-XXX]` son **estado que se
> parsea** (`sdd-gate-check.py`, `sdd-seal.py`, `wf-spec-readiness` Paso 4) y no se tocan.
> La frase que cierra la línea la lee **una persona** dentro de su spec: va en lenguaje
> natural, sin comando. Las menciones a `wf-*` del resto de este documento sí se quedan —
> describen el mecanismo al agente que carga la KB, no le dictan qué decirle al usuario.

### Efecto en el pipeline

- Una HU marcada `[INCOMPLETO]` **se incluye** en el spec con toda la información disponible
- Los CAs asociados se generan parcialmente si es posible (con el GIVEN/WHEN disponible) o se omiten con referencia al gap
- `wf-prepare-plan` **bloquea** si el feature spec contiene HUs `[INCOMPLETO]`
- Para completar: responder el gap **en el fichero donde vive su bloque** ([[D-054]]) y pedir que se completen las historias afectadas; al integrar la respuesta se retira la marca
