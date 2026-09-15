---
name: wf-prd-change-cascade
description: "Propaga un cambio de PRD por el pipeline en una conversacion: change → sync-impact → spec-sync → conflict → readiness → design-sync → reporte de plan/tasks stale. Auto-aplica los deltas inequivocos y sostiene sus gates."
when_to_use: "Activa en frases como 'propaga este cambio de PRD por todo el pipeline', 'haz todo el cascade tras el cambio', 'resincroniza todo lo que cuelga del PRD', 'corre la cadena completa de sync post-cambio', 'no quiero encadenar a mano change → sync-impact → spec-sync → conflict → readiness'. No activa para gestionar un cambio aislado sin propagar (usa wf-prd-change), ni para medir impacto sin aplicar (usa wf-prd-sync-impact), ni para resincronizar solo specs (usa wf-spec-sync-from-prd)."
argument-hint: "<prd.md> [--new-reqs <cambio.md>] [--features F-001,F-002,...] [--review-before-apply] [--skip-design] [--dry-run]"
effort: high
allowed-tools: [Bash, Agent, AskUserQuestion, Skill]
user-invocable: true
---

# Workflow: PRD-CHANGE-CASCADE (Orquestador, hilo principal)

Tu objetivo es ejecutar de principio a fin la cadena de propagación de un cambio de PRD, que de otro modo el usuario encadena a mano: gestionar el cambio, medir su impacto, resincronizar specs, revalidar conflictos y readiness, sincronizar diseño y reportar qué planes y tasks quedaron stale.

**Regla de oro:** eres un orquestador puro. No clasificas el cambio, no analizas impacto, no editas specs ni mides deriva tú mismo. Cada workflow que orquestas ya tiene su agente y sus KBs; tú no duplicas ese conocimiento, y **no escribes ningún artefacto** ([[D-060]]).

> **Corres en el hilo principal, y por eso tus paradas existen ([[D-045]]/[[D-075]]).** Hasta la
> v0.109.0 esta skill era `context: fork` e invocaba los demás workflows con el `Skill` tool.
> Declaraba cuatro *"checkpoints humanos"* que **ningún fork puede presentar**: un gate escrito
> donde no hay turno no se presenta, se decide solo — y el pipeline entero salía con pinta de
> correcto. Ahora preguntas tú, en el momento, y continúas en el mismo turno con lo que el usuario
> elija.

> **Cómo orquestas — dos mecanismos, y ninguno es intercambiable.**
> - **Los workers de otras fases se delegan con la tool `Agent`** ([[D-043]]), con el
>   `subagent_type` que indica cada paso y **`run_in_background: false`**. Son `context: fork` con
>   su `agent:` declarado: el delegado **ejecuta** los pasos de esa skill, no la invoca ([[D-044]]).
> - **`wf-prd-change` se invoca con el `Skill` tool**, y es la única. Corre en el hilo principal
>   igual que tú: sus instrucciones entran en **esta misma conversación**, así que su gate se
>   presenta de verdad. No hay fork, no hay clon, no hay asincronía.
>
> **Esperar es que te entreguen el informe** ([[D-047]]): vale el `tool_result` de tu llamada o la
> notificación de fin del agente. Nunca mires si el fichero aparece en disco ni relances un segundo
> delegado. Si no tienes el informe, **paras y lo dices**.

**Filosofía de paradas:** corre sin fricción todo lo mecánico y read-only (medición de impacto, conflict, readiness, design-sync, reporte de stale) **Y aplica automáticamente los deltas de spec inequívocos** (severidad `minor` + acción `delta`). Detente donde una persona debe decidir: (1) la clasificación del cambio de producto y sus bifurcaciones de alcance —que sostiene `wf-prd-change` dentro de tu propio turno—, (2) features con cambio no trivial (`major` / `manual_review` / `repartition`), que NO se resincronizan solas, (3) decisiones visuales de Design (diagnóstico de `wf-design-sync` → el usuario decide), (4) revalidación de plan y aprobación de deuda. El checkpoint de features no triviales **no aborta el cascade**: se preguntan y se continúa aplicando los deltas inequívocos. `--review-before-apply` restaura la parada conservadora antes de cualquier apply (incluso los `minor`).

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del PRD**: primer argumento.
- `--new-reqs <cambio.md>`: documento del cambio. Si está presente, el cascade arranca en `wf-prd-change`. Si está ausente, asume que el cambio **ya se gestionó** (el PRD ya se actualizó y existe `changes/CR-XXX/`) y arranca en la medición de impacto.
- `--features F-001,...`: subset de features a resincronizar en la fase apply. Si está ausente, las decide el análisis de sync.
- `--review-before-apply`: fuerza la parada antes de aplicar **incluso los deltas `minor`** (el comportamiento conservador, ahora opt-in). Por defecto el cascade aplica solo los deltas inequívocos (`minor` + `delta`).
- `--skip-design`: omite explícitamente la fase Design aunque exista `DESIGN.md`.
- `--dry-run`: ejecuta solo las fases read-only (impacto, conflict, readiness, design-sync, reporte) sin aplicar nada; no toca el PRD ni los specs.

Si no hay PRD → informa el uso con todos los flags y detén.

---

## Paso 2: Verificar el archivo y resolver el contexto del proyecto

Verifica que el PRD existe; si no → informa con la ruta exacta y detén.

```bash
!test -f "<prd.md>" && echo "EXISTE" || echo "NO_EXISTE"
!test -f .sdd/project-init.json && cat .sdd/project-init.json
```

De `.sdd/project-init.json`, si existe, resuelve:
- `phases` instaladas (decide qué fases del cascade aplican: `design`, `plan`, `tasks`).
- `artifacts.spec` / `artifacts.design` (raíces de artefactos; si no están declaradas, usa el directorio del PRD).

Esta resolución gobierna la **profundidad adaptativa**: una fase no instalada no se ejecuta, se reporta como omitida.

---

## Paso 3 (gate de clasificación): Gestionar el cambio de producto

**Solo si se pasó `--new-reqs`.** Invoca con el `Skill` tool:
> `wf-prd-change <prd.md> --new-reqs <cambio.md>`

**Por qué con el `Skill` tool y sin flag de aplazamiento ([[D-075]]).** `wf-prd-change` corre en el hilo principal y tiene un **gate obligatorio**: confirmar la clasificación del cambio y resolver las bifurcaciones de alcance preguntando al usuario ([[D-040]]). Tú también corres en el hilo principal, así que **ese gate se presenta dentro de tu turno** y el usuario lo responde aquí mismo. Mientras fuiste un fork esto era imposible y el cambio se aplicaba con `--defer-decisions`, dejando el PRD `OPEN_ASSUMPTIONS` y la decisión aplazada a una revisión posterior; ese rodeo ya no hace falta y el flag se retiró.

Cuando termine, lee su veredicto:
- Si clasificó el cambio como **solo `CLARIFICATION`** (no reescribió el PRD) → **DETENTE** e informa: el cambio no altera el producto comprometido, así que no hay nada que propagar. Dile, en lenguaje natural, que lo que corresponde es **completar los huecos del spec afectado o evolucionarlo**, según el artefacto, y termina.
- Si hubo **cambio de producto** (PRD actualizado, `changes/CR-XXX/` registrado) → continúa al Paso 4.

Si NO se pasó `--new-reqs`: verifica que existe `product-changelog.md` o `changes/` junto al PRD. Si no existe ninguno → **DETENTE** e informa: no hay constancia de un cambio gestionado; hay que **formalizar antes el cambio sobre el PRD** o volver a lanzarlo indicando el documento del cambio. Si existe → continúa.

---

## Paso 4: Medir el impacto (read-only)

Delega con la tool `Agent` ([[D-043]]) y **espera su informe**:

```
Agent(
  subagent_type: "sdd-spec-auditor",
  run_in_background: false,
  prompt: "Lee `.claude/skills/wf-prd-sync-impact/SKILL.md` y ejecuta sus pasos TÚ MISMO sobre estos argumentos: <prd.md>. NO uses el `Skill` tool: ya eres el agente al que esa skill delega (`agent: sdd-spec-auditor`), así que invocarla te forkearía en un clon tuyo. Dentro de ese SKILL.md, `${CLAUDE_SKILL_DIR}` es `.claude/skills/wf-prd-sync-impact/`. Al terminar, informa del path exacto del `_sync_report.md` y del estado por artefacto (`in_sync` / `needs_review` / `stale` / `unknown`)."
)
```

Del **informe del delegado** (no del disco) extrae:
- Features con specs marcados `needs_review` o `stale` (entran a resincronización).
- Si todo está `in_sync` → no hay nada que propagar: salta al Paso 9 e informa que el pipeline ya estaba sincronizado.

---

## Paso 5 (gate): Resincronizar specs

### 5a — Analyze (read-only)

```
Agent(
  subagent_type: "sdd-spec-writer",
  run_in_background: false,
  prompt: "Lee `.claude/skills/wf-spec-sync-from-prd/SKILL.md` y ejecuta sus pasos TÚ MISMO en modo `analyze` sobre estos argumentos: analyze <prd.md>. NO uses el `Skill` tool: ya eres el agente al que esa skill delega (`agent: sdd-spec-writer`), así que invocarla te forkearía en un clon tuyo. Dentro de ese SKILL.md, `${CLAUDE_SKILL_DIR}` es `.claude/skills/wf-spec-sync-from-prd/`. Al terminar, dame por cada feature afectada: su ID, el path de su `_sync_requirements.md`, su `severidad` (minor|major|structural) y su `acción` (delta|manual_review|repartition|retire)."
)
```

### 5b — Particionar las features afectadas

Usando la clasificación del analyze, parte las features en dos conjuntos:
- **Conjunto AUTO-APPLY** = features con `acción: delta` **Y** `severidad: minor` (cambios inequívocos).
- **Conjunto STOP** = features con `severidad: major` **O** `acción: manual_review` **O** `acción: repartition` **O** `acción: retire`.

  `retire` nunca entra en AUTO-APPLY, por severidad que traiga: dar de baja una feature es irreversible en la práctica —hay planes y tareas encima— y su gate necesita el impacto delante ([[D-074]]).

Si el conjunto STOP **no** está vacío → **pregunta con `AskUserQuestion`**, con la lista delante (una feature por línea: ID, nombre, severidad y por qué no es automática):
- *Continuar con el resto* (recomendada) — se aplican solo las inequívocas; las del conjunto STOP quedan intactas y se recogen en el resumen final.
- *Parar aquí* — no se aplica nada y el usuario decide feature por feature antes de seguir.

En la pregunta, describe lo que necesita cada una **en lenguaje natural** —evolucionar el spec con el cambio, revisarlo a mano, rehacer su partición, darla de baja— y **no nombres el workflow** ([[D-019]]). Este es un checkpoint humano real y ahora puedes sostenerlo: **no lo bypasees** aplicando el conjunto STOP por tu cuenta.

### 5c — Apply (o parada conservadora)

- Si se pasó `--review-before-apply` **O** `--dry-run` → **NO apliques nada**; presenta la clasificación completa (AUTO-APPLY + STOP). En `--dry-run`, salta al Paso 9 con el análisis como salida.
- Caso normal → aplica el conjunto AUTO-APPLY:

```
Agent(
  subagent_type: "sdd-spec-writer",
  run_in_background: false,
  prompt: "Lee `.claude/skills/wf-spec-sync-from-prd/SKILL.md` y ejecuta sus pasos TÚ MISMO en modo `apply` sobre estos argumentos: apply <prd.md> --features <IDs minor+delta>. NO uses el `Skill` tool: ya eres el agente al que esa skill delega (`agent: sdd-spec-writer`), así que invocarla te forkearía en un clon tuyo. Dentro de ese SKILL.md, `${CLAUDE_SKILL_DIR}` es `.claude/skills/wf-spec-sync-from-prd/`. Al terminar, dime por cada spec tocado: su path, la versión nueva y que su validación quedó reabierta."
)
```

  Si en el Paso 1 se recibió `--features`, usa la **intersección** de ese subset con el conjunto AUTO-APPLY.

> **Cada spec que se aplica sale de aquí en `BORRADOR`, y eso se dice ([[D-061]]).** El apply
> reabre la validación (`--unseal`): lo que alguien validó ya no es lo que hay. No es un efecto
> secundario que se pueda callar —el readiness del Paso 6 los verá bloqueados y el usuario no
> sabrá por qué—, así que **anótalo para el resumen final**: cada spec resincronizado necesita
> volver a validarse. Es el mismo aviso que el Paso 3 deja sobre el PRD cuando su sello se reabre.

---

## Paso 6: Revalidar conflictos y readiness (read-only)

Solo si en el Paso 5c se aplicó al menos un spec.

**Conflictos** — por cada spec resincronizado, delega un auditor, y **emite las N llamadas en un único mensaje**: con el flag, ese mensaje no vuelve hasta que han terminado todas, y esa es la barrera que necesita el readiness ([[D-047]]).

```
Agent(
  subagent_type: "sdd-spec-auditor",
  run_in_background: false,
  prompt: "Lee `.claude/skills/wf-spec-conflict/SKILL.md` y ejecuta sus pasos TÚ MISMO sobre estos argumentos: <spec.md> --features-dir <features_dir>. NO uses el `Skill` tool ([[D-044]]): ya eres su agente y te forkearía en un clon. Dentro de ese SKILL.md, `${CLAUDE_SKILL_DIR}` es `.claude/skills/wf-spec-conflict/`. Al terminar, dime el path del informe y los conflictos de severidad ALTA, si los hay."
)
```

**El informe lo escribe cada auditor**, junto a su spec: tú no escribes ninguno ni los consolidas ([[D-059]]/[[D-060]]).

**Readiness** — después de la barrera:

```
Agent(
  subagent_type: "sdd-spec-auditor",
  run_in_background: false,
  prompt: "Lee `.claude/skills/wf-spec-readiness/SKILL.md` y ejecuta sus pasos TÚ MISMO sobre estos argumentos: <features_dir>/. NO uses el `Skill` tool ([[D-044]]): ya eres su agente y te forkearía en un clon. Dentro de ese SKILL.md, `${CLAUDE_SKILL_DIR}` es `.claude/skills/wf-spec-readiness/`. Al terminar, dime el path del `_readiness_report.md` y qué features quedan bloqueadas y por qué."
)
```

Si no se aplicó ningún spec, omite este paso e indícalo.

---

## Paso 7 (gate si hay decisiones visuales): Sincronizar Design (adaptativo)

Aplica profundidad adaptativa:
- Si se pasó `--skip-design`, o la fase `design` no está instalada, o **no existe `DESIGN.md`** en la raíz de diseño → omite esta fase y repórtala como "no aplica".
- Si existe `DESIGN.md` → delega:

```
Agent(
  subagent_type: "design-system-architect",
  run_in_background: false,
  prompt: "Lee `.claude/skills/wf-design-sync/SKILL.md` y ejecuta sus pasos TÚ MISMO sobre estos argumentos: <DESIGN.md>. NO uses el `Skill` tool: ya eres el agente al que esa skill delega (`agent: design-system-architect`), así que invocarla te forkearía en un clon tuyo. Dentro de ese SKILL.md, `${CLAUDE_SKILL_DIR}` es `.claude/skills/wf-design-sync/`. Al terminar, dime el path del informe y qué flows/views/ui_prompt/exports quedaron stale."
)
```

  **No regeneres** los artefactos de diseño: este paso solo diagnostica. Si el informe deja decisiones visuales abiertas, **preséntalas con `AskUserQuestion`** —regenerar ahora lo que quedó stale, o dejarlo para una pasada de diseño aparte— y respeta la elección.

---

## Paso 8 (gate si hay derivados): Reportar planes y tasks stale (adaptativo, read-only)

Para cada feature resincronizada, comprueba mecánicamente si existen artefactos aguas abajo:

```bash
!test -f "features/<nombre>/plan/<nombre>_plan.md" && echo "PLAN" || echo "SIN_PLAN"
!test -f "features/<nombre>/tasks/<nombre>_tasks.md" && echo "TASKS" || echo "SIN_TASKS"
```

Si las fases `plan`/`tasks` no están instaladas o no hay artefactos → repórtalo como "sin derivados aguas abajo". Si existen → **márcalos como candidatos a revisión** (no los regeneres): un spec que cambió invalida potencialmente su plan y sus tasks. Con derivados delante, **pregunta con `AskUserQuestion`** si quiere revalidarlos ahora o dejarlos anotados como deuda; descríbelo en lenguaje natural, sin nombrar el workflow.

---

## Paso 9: Presentar el resumen del cascade

**No escribes ningún informe** ([[D-060]]). El resumen es un diagnóstico para el usuario, no un artefacto del proyecto: lo presentas en la conversación, con una fila por fase —fase · ejecutada/parada/omitida · artefacto producido (el path que te dio su autor) · estado · qué queda pendiente—, diferenciando:
- fases ejecutadas automáticamente,
- gates donde paraste y qué eligió el usuario,
- fases omitidas por profundidad adaptativa (no instalada, sin `DESIGN.md`, sin derivados).

> **Por qué ya no se escribe un `_cascade_report.md`.** Consolidar en un fichero lo que produjeron
> tus delegados es redactar un artefacto que no es tuyo: cada informe tiene un autor declarado, y
> esa autoría es lo que lo hace auditable ([[D-060]]). Medido: el orquestador consolidó cuatro
> informes de conflicto y, al transcribir contenido que no había producido, **adjudicó un hallazgo
> al auditor equivocado**. Lo que el usuario necesita saber cabe en tu respuesta; lo que hay que
> conservar ya está escrito, cada cosa por quien la hizo.

---

## Paso 10: Degradación con gracia

Si cualquier sub-workflow invocado **no está instalado** o falla:
- no abortes todo el cascade: registra esa fase como `no disponible` con el motivo, continúa con las fases independientes posibles y refléjalo en el resumen.
- Si la fase fallida es un prerequisito duro de las siguientes (p. ej. el apply de specs falló), detén las dependientes e indícalo.

---

## Paso 11: Informar al usuario

Cierra con lo que pasó y lo que queda, **en lenguaje natural y sin nombrar workflows ni comandos** ([[D-019]]):

- qué se propagó y hasta dónde;
- **qué specs quedaron en borrador** por haberse resincronizado, y que hay que revalidarlos antes de planificar sobre ellos;
- qué features no se tocaron y qué necesita cada una;
- si hay planes o tareas que revisar.

Ofrécete a continuar con lo siguiente que corresponda ("cuando quieras revalidamos los specs que han cambiado"), en vez de dictarle un comando para que lo teclee.
