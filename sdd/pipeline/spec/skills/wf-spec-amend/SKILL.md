---
name: wf-spec-amend
description: "Enmienda quirurgica de un CA ambiguo descubierto durante la implementacion (back-edge tasks-spec). Solo admite ACLARACION estricta: precisar el texto sin cambiar el comportamiento esperado. Cualquier cambio de comportamiento escala a wf-spec-delta."
when_to_use: "Activa en frases como 'este CA es ambiguo', 'el criterio de aceptación no especifica X', 'implementando descubrí que el spec no aclara', 'aclara el CA-XXX', 'la task está bloqueada porque el spec es ambiguo'. No activa si el comportamiento esperado cambia (usa wf-spec-delta), ni para bugs de código entregado (usa wf-bug), ni para HUs [INCOMPLETO] con respuestas en un analysis (usa wf-spec-gap-resolve)."
argument-hint: "<feature_spec.md> --ca CA-XXX [--from-task T-00X] [--reason 'texto']"
effort: high
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# Workflow: SPEC-AMEND — enmienda desde implementación

Resuelve una ambigüedad de un CA descubierta al implementar **sin re-descender todo el waterfall**: se corrige el texto del CA, queda trazado con `E-00X`, y el plan afectado se marca con un stale puntual que solo retiene las tasks que tocan ese CA.

Este workflow corre en el **hilo principal** (igual que `wf-prd-change`, `wf-spec-validate` y `wf-plan-validate`, y **no** en `context: fork`) por una razón que es su propio núcleo ([[D-068]]): sostiene **dos gates humanos** —la clasificación aclaración-vs-cambio y la confirmación del texto final palabra por palabra— y un subagente no puede presentar ninguno de los dos. Mientras esto fue un fork, la parte que da valor a la skill no era ejecutable.

**Tu rol es de orquestador puro.** El análisis del CA y la edición los hace el agente `sdd-spec-writer`; tú sostienes los gates y ejecutas los scripts deterministas. **No hagas `Read` ni `cat` del spec** ([[D-031]]/[[D-060]]): lo que necesitas ver te lo devuelve tu delegado. Vale **aunque las tools estén disponibles** — `allowed-tools` es declarativo, no una jaula ([[D-038]]).

La frontera es estricta y no negociable: si la corrección altera lo que el sistema debe hacer (no solo cómo está descrito), esta workflow NO la aplica.

---

## Paso 1: Parsear argumentos

- path del spec (obligatorio, debe terminar en `_spec.md`)
- `--ca CA-XXX` (obligatorio)
- `--from-task T-00X` (opcional: la task desde la que se descubrió la ambigüedad)
- `--reason 'texto'` (opcional: descripción de la ambigüedad)

Si falta el spec o `--ca`:
> "Necesito el spec de la feature y el CA que hay que aclarar. Si la duda salió implementando una task, dímelo y lo dejo trazado."

---

## Paso 2: Verificar y localizar

```bash
!test -f "<path_spec>" && grep -c "^#\{3,4\}[[:space:]]*CA-XXX" "<path_spec>"
```

Si el spec no existe → informa la ruta exacta y detén. Si el CA **no aparece**, detén: puede ser un comportamiento no especificado, y eso es evolucionar el spec o tramitarlo como defecto, no enmendarlo.

**Si el spec declara `Estado: RETIRADO`, tampoco se enmienda ([[D-078]]):**

```bash
!grep -Eq '^[[:space:]]*[-*>]?[[:space:]]*\*{0,2}Estado:?\*{0,2}[[:space:]]*:?[[:space:]]*RETIRADO' "<path_spec>" && echo RETIRADO || echo VIGENTE
```

`RETIRADO` → detén e informa con la traza `Retirada:` delante. Aclarar el texto de un CA de una
feature cancelada no desbloquea nada —sus tasks están denegadas por la baja, no por la ambigüedad—
y el `--unseal` del Paso 7 la reactivaría en silencio. Si la decisión de producto cambió, primero se
reactiva la feature; la enmienda viene después.

Localiza plan y tasks de la feature: subcarpetas de fase primero (`features/<n>/plan/<n>_plan.md`, `features/<n>/tasks/<n>_tasks.md`), raíz plana de la feature como fallback (layout legacy). Que no existan aún **no bloquea**: la enmienda sobre el spec es válida igualmente.

---

## Paso 3 (gate): Recoger la ambigüedad

La descripción sale, en orden: de `--reason`; del motivo de la task `BLOQUEADA` si se pasó `--from-task`; o **preguntándosela al usuario** con `AskUserQuestion`:
> "¿Qué ambigüedad encontraste en CA-XXX? ¿Qué interpretaciones posibles te bloquean?"

**No continúes sin una descripción concreta** de qué es ambiguo y por qué. Ahora sí puedes pedirla: estás en el hilo principal.

---

## Paso 4: Delegar el análisis (tool `Agent`, y esperar)

Delega con la tool `Agent` ([[D-043]]), `subagent_type: "sdd-spec-writer"` y **`run_in_background: false`**:

  prompt: "Analiza CA-XXX de <path_spec> ante esta ambigüedad: <descripción>. NO escribas nada todavía. Devuélveme: (1) el texto ACTUAL del CA, verbatim; (2) el texto CORREGIDO que propones; (3) una línea de por qué NO cambia el comportamiento; (4) tu clasificación. Clasifica ACLARACIÓN solo si se cumplen las tres: la intención del GIVEN/WHEN/THEN no cambia, solo se precisa texto (concretar un término vago, fijar un dato que el CA ya implicaba, deshacer una redacción con dos lecturas), y ninguna interpretación posible contradice el PRD ni mueve exclusiones o alcance. Clasifica CAMBIO DE COMPORTAMIENTO si basta una: la corrección elige entre interpretaciones con comportamientos observables distintos y el spec/PRD no determina cuál es la correcta; añade, elimina o modifica una rama observable, un límite funcional o una regla de negocio; o afecta a otros CAs o HUs. Ante cualquier duda sobre la frontera, clasifica CAMBIO. Si es CAMBIO, escribe además `<feature>_amend_request.md` junto al spec con la ambigüedad y la decisión pendiente, y dime su path."

**Has esperado cuando su informe está en tu contexto como resultado de tu llamada** ([[D-047]]). Si no lo tienes, **paras y lo dices**: no reconstruyes su veredicto leyendo el spec.

---

## Paso 5 (gate): Clasificación y confirmación del texto

**Si clasificó CAMBIO DE COMPORTAMIENTO** → no se toca el spec:
> "Esto no es una aclaración: cambia el comportamiento esperado. El material del cambio queda en `<path>` para tramitarlo como **evolución del spec**. La task sigue bloqueada hasta que se resuelva."

Si además contradice el PRD vigente o mueve algo entre MVP y fase futura, dilo: primero hay que formalizar el cambio de producto sobre el PRD.

**Si clasificó ACLARACIÓN** → presenta con `AskUserQuestion`, **lado a lado**: el texto actual del CA, el corregido, y la línea de por qué no cambia el comportamiento. **Sin confirmación explícita no hay enmienda** (el dev propone, el humano valida).

- **Confirmado** → sigue al Paso 6.
- **Corregido por el usuario** → vuelve al Paso 4 con el texto final: la clasificación se re-aplica sobre lo que de verdad se va a escribir, no sobre lo que se propuso.
- **Declinado** → termina sin tocar nada.

> **Este gate es el corazón de la skill — NO lo bypasees.** El coste de escalar a una evolución innecesaria son minutos; el de una enmienda que era un cambio encubierto es **un spec que miente**.

---

## Paso 6: Asignar referencia y marcar el plan (script, no prosa)

La numeración `E-00X` y la anotación del plan las gestiona **solo** `sdd-amend.py` (autor ≠ marcador). Nunca asignes refs ni escribas anotaciones a mano.

- **Si el plan existe** (en `BORRADOR` o `VALIDADO`):
  ```bash
  !python3 .sdd/scripts/sdd-amend.py mark <plan.md> --ca CA-XXX
  ```
  Usa el `REF: E-00X` que devuelve. El plan conserva su `Estado:`; la anotación retiene selectivamente las tasks que referencian ese CA y bloquea la generación de tasks hasta cerrarla.
- **Si no hay plan aún**: `!python3 .sdd/scripts/sdd-amend.py next-ref <spec.md>`.
- **Si falta el script**: detén e indica reinstalar el ecosistema — no improvises el marcado.

---

## Paso 7: Delegar la enmienda (tool `Agent`, y esperar)

Misma delegación, con la ref ya asignada:

  prompt: "Aplica esta enmienda en <path_spec>, edición quirúrgica y mínima. Sustituye SOLO el texto de CA-XXX por: <texto confirmado>. No reformatees nada más, no renumeres CAs, no toques otras HUs. Incrementa la versión menor del spec. Añade al `## Changelog` (orden cronológico inverso) la línea: `- vX.Y (<fecha real de tu contexto>) — E-00X: aclaración CA-XXX desde T-00X — <qué queda fijado> (ya determinado por <dónde: el CA, otro CA, el PRD>).` — sin `--from-task`, usa `desde implementación`. La entrada dice qué se fijó y contra qué traza, no solo que hubo enmienda ([[D-063]]). Después ejecuta `python3 .sdd/scripts/sdd-seal.py spec <path_spec> --unseal` ([[D-061]]): lo que se validó ya no es lo que hay. Confírmame la versión nueva y la línea de changelog."

---

## Paso 8: Cerrar el stale puntual del plan

Si marcaste un plan en el Paso 6, la revisión **scoped** de las secciones que referencian CA-XXX contra el texto aclarado la hace tu delegado (no la haces tú leyendo el plan). Con su veredicto:

- **El plan sigue siendo válido** → `!python3 .sdd/scripts/sdd-amend.py clear <plan.md> --ref E-00X`, y las tasks retenidas quedan liberadas.
- **El plan contradice el texto aclarado, o hay dudas** → deja la anotación e informa qué sección necesita actualizarse. **En caso de duda, NO limpies**: una task ejecutada contra un plan desactualizado cuesta más que una re-validación.

---

## Paso 9: Informar

- spec: versión nueva + entrada `E-00X` del changelog, y que su validación quedó reabierta.
- plan: si se marcó y si quedó limpiado o pendiente (qué sección revisar).
- tasks retenidas, si quedan: `!python3 .sdd/scripts/sdd-task-state.py check <tasks.md>`.

Siguiente paso, **en lenguaje natural y sin nombrar el workflow**:
- Enmienda cerrada y la task origen estaba bloqueada → dile que cuando quiera retoma esa task y sigue por donde estaba; el desbloqueo se hace solo al reanudarla.
- Anotación pendiente → dile que actualice la sección del plan y te pida que **lo re-valides**: al sellarlo se absorbe la enmienda y se liberan las tasks retenidas.
