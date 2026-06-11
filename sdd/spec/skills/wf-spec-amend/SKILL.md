---
name: wf-spec-amend
description: "Enmienda quirúrgica de un CA ambiguo descubierto durante la implementación (back-edge tasks→spec). Solo admite ACLARACIÓN estricta: precisar el texto sin cambiar el comportamiento esperado. Aplica la corrección con versión menor + changelog E-00X, y marca el plan afectado con 'Enmienda pendiente' (stale puntual: solo se retienen las tasks que referencian ese CA). Cualquier cambio de comportamiento escala a wf-spec-delta."
when_to_use: "Activa en frases como 'este CA es ambiguo', 'el criterio de aceptación no especifica X', 'implementando descubrí que el spec no aclara', 'aclara el CA-XXX', 'la task está bloqueada porque el spec es ambiguo'. No activa si el comportamiento esperado cambia (usa wf-spec-delta), ni para bugs de código entregado (usa wf-bug), ni para HUs [INCOMPLETO] con respuestas en un analysis (usa wf-spec-gap-resolve)."
argument-hint: "<feature_spec.md> --ca CA-XXX [--from-task T-00X] [--reason 'texto']"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-writer
user-invocable: true
---

# Workflow: SPEC-AMEND — enmienda desde implementación

Tu objetivo es resolver una ambigüedad de un CA descubierta al implementar, **sin re-descender todo el waterfall**: corriges el texto del CA en el spec, dejas trazabilidad (E-00X) y marcas el plan afectado con un stale puntual que solo retiene las tasks que tocan ese CA.

Esta skill existe para separar dos casos:

- **aclarar** un CA cuyo texto era ambiguo pero cuya intención no cambia → esta vía corta
- **cambiar** el comportamiento esperado, por pequeño que sea → `wf-spec-delta` (waterfall normal)

La frontera es estricta y no negociable: si la corrección altera lo que el sistema debe hacer (no solo cómo está descrito), esta workflow NO la aplica.

## Paso 1: Parsear argumentos

Extrae:

- path del spec (obligatorio, debe terminar en `_spec.md`)
- `--ca CA-XXX` (obligatorio)
- `--from-task T-00X` (opcional: la task desde la que se descubrió la ambigüedad)
- `--reason 'texto'` (opcional: descripción de la ambigüedad)

Si falta el spec o `--ca`:
> "Uso: `/wf-spec-amend <feature_spec.md> --ca CA-XXX [--from-task T-00X] [--reason 'texto']`"

## Paso 2: Verificar archivos y localizar artefactos de la feature

1. Comprueba que el spec existe y que contiene el encabezado `### CA-XXX` (o `#### CA-XXX`). Si el CA no existe, detén: puede ser un comportamiento no especificado → eso es `wf-spec-delta` (añadir) o `wf-bug` con triaje UNSPEC, no una enmienda.
2. Localiza el plan y las tasks de la feature: subcarpetas de fase primero (`features/<n>/plan/<n>_plan.md`, `features/<n>/tasks/<n>_tasks.md`), raíz plana de la feature como fallback (layout legacy). Que no existan aún no bloquea: la enmienda sobre el spec es válida igualmente (no habrá nada que marcar).
3. Si se pasó `--from-task`, lee el bloque de esa task en el `_tasks.md` (su DoD, su `Spec CA` y el motivo si está `BLOQUEADA`) como contexto de la ambigüedad.

## Paso 3: Recoger la ambigüedad

Construye la descripción del problema desde (en orden): `--reason`, el motivo de la task `BLOQUEADA`, o preguntando al usuario:
> "¿Qué ambigüedad encontraste en CA-XXX? ¿Qué interpretaciones posibles te bloquean?"

No continúes sin una descripción concreta de qué es ambiguo y por qué.

## Paso 4: Gate de clasificación (el corazón — NO lo bypasses)

Compara el CA actual con la corrección que la ambigüedad pide. Clasifica:

**ACLARACIÓN** (esta vía) — TODAS estas condiciones a la vez:
- La intención del GIVEN/WHEN/THEN no cambia: el sistema debe hacer lo mismo antes y después.
- Solo se precisa texto: concretar un término vago, fijar un dato que el CA ya implicaba, deshacer una redacción con dos lecturas.
- Ninguna de las interpretaciones posibles contradice el PRD ni mueve exclusiones o alcance.

**CAMBIO DE COMPORTAMIENTO** — basta UNA de estas:
- La corrección elige entre interpretaciones que producen comportamientos observables distintos **y el spec/PRD no determina cuál es la correcta** (estás decidiendo producto, no aclarando).
- Añade, elimina o modifica una rama observable, un límite funcional o una regla de negocio.
- Afecta a otros CAs o HUs además del indicado.

Si es CAMBIO DE COMPORTAMIENTO → detén SIN tocar el spec:
> "Esto no es una aclaración: cambia el comportamiento esperado. Escribo el material del cambio en `<feature>_amend_request.md` para `/wf-spec-delta analyze <spec.md> --new-reqs <ese archivo>`. La task queda BLOQUEADA hasta resolver el delta."

Escribe ese archivo (la descripción de la ambigüedad + la decisión pendiente) junto al spec y termina.

Si la respuesta correcta contradice el PRD vigente o mueve algo entre MVP y fase futura → remite a `wf-prd-change` (misma regla que `wf-spec-gap-resolve`).

**Caso dudoso = CAMBIO.** Ante cualquier duda sobre la frontera, escala a delta: el coste de un delta innecesario es minutos; el de una enmienda que era un cambio encubierto es un spec que miente.

## Paso 5: Proponer la corrección y confirmar con el humano

Presenta lado a lado:

- el texto actual del CA
- el texto corregido propuesto
- una línea explicando qué se aclara y por qué NO cambia el comportamiento

Pide confirmación explícita al usuario (el dev propone, el humano valida). Sin confirmación no hay enmienda. Si el usuario corrige la propuesta, re-aplica el Paso 4 sobre el texto final antes de continuar.

## Paso 6: Asignar referencia y marcar el plan (script, no prosa)

La numeración E-00X y la anotación del plan las gestiona **solo** `sdd-amend.py` (autor ≠ marcador). Nunca asignes refs ni escribas/borres anotaciones a mano.

- **Si el plan de la feature existe** (esté en BORRADOR o VALIDADO):
  ```
  !python3 .sdd/scripts/sdd-amend.py mark <plan.md> --ca CA-XXX
  ```
  Usa el `REF: E-00X` que devuelve. El plan conserva su `Estado:`; la anotación `Enmienda pendiente` retiene selectivamente las tasks que referencian ese CA (gate de `wf-task-run --task` + `sdd-task-state.py next`) y bloquea `wf-prepare-tasks` hasta cerrarla.
- **Si no hay plan aún**: obtén la ref con `!python3 .sdd/scripts/sdd-amend.py next-ref <spec.md>`.
- Si el script no existe en `.sdd/scripts/`, detén e indica reinstalar con `install.sh` — no improvises el marcado.

## Paso 7: Aplicar la enmienda al spec

Edición quirúrgica, mínima:

- Sustituye SOLO el texto del CA confirmado. No reformatees nada más, no renumeres CAs, no toques otras HUs.
- Incrementa la versión menor del spec.
- Registra en el changelog (orden cronológico inverso):
  ```
  - vX.Y (YYYY-MM-DD) — E-00X: aclaración CA-XXX desde T-00X — <una línea: qué se aclaró>.
  ```
  (sin `--from-task`, usa `desde implementación`).

## Paso 8: Revisión scoped del plan (cerrar el stale puntual)

Si marcaste un plan en el Paso 6, revisa SOLO las secciones del plan que referencian CA-XXX contra el texto aclarado:

- **El plan sigue siendo válido** (la aclaración no contradice ninguna decisión técnica de esas secciones) →
  ```
  !python3 .sdd/scripts/sdd-amend.py clear <plan.md> --ref E-00X
  ```
  y las tasks retenidas quedan liberadas.
- **El plan contradice el texto aclarado, o tienes dudas** → deja la anotación. Informa qué sección del plan necesita actualizarse; tras editarla, la vía de cierre es `/wf-plan-validate <plan.md>` (el re-sellado absorbe la anotación). **En caso de duda, NO limpies**: una task ejecutada contra un plan desactualizado cuesta más que una re-validación.

## Paso 9: Informar resultado y siguiente paso

Reporta:

- spec: nueva versión + entrada E-00X del changelog
- plan: anotación marcada y si quedó limpiada (revisión scoped OK) o pendiente (qué sección revisar)
- tasks retenidas, si quedan: `!python3 .sdd/scripts/sdd-task-state.py check <tasks.md>` muestra las `[RETENIDA por enmienda]`

Siguiente paso según el caso:

- Enmienda cerrada (anotación limpiada) y la task origen estaba `BLOQUEADA` →
  > "CA-XXX aclarado (E-00X). Desbloquea la task y continúa: `/wf-task-run <tasks.md> --task T-00X` (el desbloqueo BLOQUEADA→EN_CURSO lo hace el propio task-run vía script)."
- Anotación pendiente →
  > "CA-XXX aclarado (E-00X), pero la sección <X> del plan necesita revisión. Actualízala y re-valida con `/wf-plan-validate <plan.md>` — el sellado absorberá la enmienda y liberará las tasks retenidas."
