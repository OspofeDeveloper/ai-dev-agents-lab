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

**Numeración**: secuencial desde `001`, sin saltos, **por linaje** — no por artefacto.

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

El script es **agnóstico al documento**: parsea cualquier fichero con bloques de gap, así que
`--list`, `--check` y `--answer` funcionan igual sobre un `_analysis.md` que sobre un `_spec.md`.
Un `--check` contra el análisis **no dice nada** sobre los gaps que viven en el spec: si un spec
tiene `[INCOMPLETO]`, hay que checkear **el spec**.

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
| Hay CAs marcados `[INFERIDO]` (caracterización) | **Bloquear**: igual que `[INCOMPLETO]` — comportamiento no confirmado; remitir a `/wf-spec-gap-resolve` |
| Hay gaps `[INFORMATIVO]` con `_(pendiente)_` pero no `[INCOMPLETO]` | **Continuar** con advertencia |
| Sin marcadores pendientes | **Continuar** normalmente |

**Patrón de verificación**: buscar la cadena literal `[INCOMPLETO]` para HUs incompletas, `[INFERIDO]` para CAs de caracterización sin confirmar, y `_(pendiente)_` para gaps sin responder.

---

## Convenciones para "Asunción por defecto"

- Debe ser la opción **más conservadora** (la que minimiza las asunciones funcionales)
- Debe ser **específica**: no "se comportará de forma estándar" sino "se mostrará un mensaje de error genérico y el usuario permanecerá en la pantalla actual"
- Se documenta en el spec generado en la sección `## Asunciones Aplicadas`
- En modo `delta`, se documenta en la sección `## Asunciones Aplicadas (vX.Y)` del spec actualizado

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
> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001], [P-003]. Responde esos gaps en el `_analysis.md` y pide que se complete la HU.
```

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
- Para completar: responder el gap en el `_analysis.md`, luego ejecutar `/wf-spec-gap-resolve <feature_spec.md>` para integrar la respuesta y eliminar la marca
