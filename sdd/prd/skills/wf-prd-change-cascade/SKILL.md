---
name: wf-prd-change-cascade
description: "Orquesta en un solo comando la propagacion de un cambio de PRD por el pipeline (change → sync-impact → spec-sync → conflict → readiness → design-sync → reporte de plan/tasks stale): corre lo mecanico read-only, auto-aplica los deltas de spec inequivocos (minor) y para solo en los checkpoints humanos. Profundidad adaptativa."
when_to_use: "Activa en frases como 'propaga este cambio de PRD por todo el pipeline', 'haz todo el cascade tras el cambio', 'resincroniza todo lo que cuelga del PRD', 'corre la cadena completa de sync post-cambio', 'no quiero encadenar a mano change → sync-impact → spec-sync → conflict → readiness'. No activa para gestionar un cambio aislado sin propagar (usa wf-prd-change), ni para medir impacto sin aplicar (usa wf-prd-sync-impact), ni para resincronizar solo specs (usa wf-spec-sync-from-prd)."
argument-hint: "<prd.md> [--new-reqs <cambio.md>] [--features F-001,F-002,...] [--review-before-apply] [--skip-design] [--dry-run]"
effort: high
allowed-tools: [Read, Write, Bash, Skill]
context: fork
---

# Workflow: PRD-CHANGE-CASCADE (Orquestador)

Tu objetivo es ejecutar de principio a fin la cadena de propagación de un cambio de PRD, que hoy el usuario encadena a mano: gestionar el cambio, medir su impacto, resincronizar specs, revalidar conflictos y readiness, sincronizar diseño y reportar qué planes y tasks quedaron stale.

**Regla de oro:** eres un orquestador puro. No clasificas el cambio, no analizas impacto, no editas specs ni mides deriva tú mismo. Invocas los workflows existentes en el orden correcto, consolidas sus salidas y **paras solo en los checkpoints humanos reales**. Cada workflow invocado ya delega a su agente y carga sus KBs; tú no duplicas ese conocimiento.

**Filosofía de paradas:** corre sin fricción todo lo mecánico y read-only (medición de impacto, conflict, readiness, design-sync, reporte de stale) **Y aplica automáticamente los deltas de spec inequívocos** (severidad `minor` + acción `delta`). Detente únicamente donde una persona debe decidir: (1) aprobar el cambio de producto (`wf-prd-change`), (2) features con cambio no trivial (`major` / `manual_review` / `rediscover`), que NO se resincronizan solas, (3) decisiones visuales de Design (diagnóstico de `wf-design-sync` → el usuario decide), (4) revalidación de plan y aprobación de deuda. El checkpoint de features no triviales **no aborta el cascade**: se presentan al usuario y se continúa aplicando los deltas inequívocos. `--review-before-apply` restaura la parada conservadora antes de cualquier apply (incluso los `minor`).

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

Lee `.sdd/project-init.json` si existe para resolver:
- `phases` instaladas (decide qué fases del cascade aplican: `design`, `plan`, `tasks`).
- `artifacts.spec` / `artifacts.design` (raíces de artefactos; si no están declaradas, usa el directorio del PRD).

Esta resolución gobierna la **profundidad adaptativa**: una fase no instalada no se ejecuta, se reporta como omitida.

---

## Paso 3 (checkpoint humano): Gestionar el cambio de producto

**Solo si se pasó `--new-reqs`.** Invoca con el Skill tool:
> `wf-prd-change <prd.md> --new-reqs <cambio.md>`

Espera a que termine y lee su veredicto:
- Si clasificó el cambio como **solo `CLARIFICATION`** (no reescribió el PRD) → **DETENTE** e informa: el cambio no altera el producto comprometido; el cascade de sync no aplica. Recomienda `wf-spec-gap-resolve` o `wf-spec-delta` según el artefacto afectado, y termina.
- Si hubo **cambio de producto** (PRD actualizado, `changes/CR-XXX/` registrado) → continúa al Paso 4.

Si NO se pasó `--new-reqs`: verifica que existe `product-changelog.md` o `changes/` junto al PRD. Si no existe ninguno → **DETENTE** e informa: no hay constancia de un cambio gestionado; arranca con `--new-reqs <cambio.md>` o ejecuta `wf-prd-change` primero. Si existe → continúa.

> Este es el primer checkpoint humano: la aprobación del cambio la materializa `wf-prd-change`. El cascade no la salta.

---

## Paso 4: Medir el impacto (read-only)

Invoca con el Skill tool:
> `wf-prd-sync-impact <prd.md>`

Produce `<basename>_sync_report.md` con el estado por artefacto (`in_sync` / `needs_review` / `stale` / `unknown`). Lee el reporte y extrae:
- Features con specs marcados `needs_review` o `stale` (entran a resincronización).
- Si todo está `in_sync` → no hay nada que propagar: salta al Paso 8 (reporte final) e informa que el pipeline ya estaba sincronizado.

---

## Paso 5 (checkpoint humano): Resincronizar specs

### 5a — Analyze (read-only)
Invoca con el Skill tool:
> `wf-spec-sync-from-prd analyze <prd.md>`

Genera los `<nombre>_sync_requirements.md` por feature afectada. Cada feature trae su clasificación: `severidad: minor|major|structural` y `acción: delta|manual_review|rediscover`.

### 5b — Particionar las features afectadas
Usando la clasificación del analyze, parte las features en dos conjuntos:
- **Conjunto AUTO-APPLY** = features con `acción: delta` **Y** `severidad: minor` (cambios inequívocos).
- **Conjunto STOP** = features con `severidad: major` **O** `acción: manual_review` **O** `acción: rediscover`.

Si el conjunto STOP **no** está vacío → preséntalo al usuario como features que **NO se resincronizan solas** y requieren decisión humana: para cada una indica severidad/acción y recomienda `wf-spec-delta` (para los `major` o cambios de comportamiento), revisión manual, o `wf-spec-discover` (para los `rediscover`). **No las apliques.** Este es un checkpoint humano real, pero **NO aborta el cascade**: continúa aplicando el conjunto AUTO-APPLY.

### 5c — Apply (o parada conservadora)
- Si se pasó `--review-before-apply` **O** `--dry-run` → **NO apliques nada**; presenta la clasificación completa (AUTO-APPLY + STOP). En `--dry-run`, salta al Paso 8 con el análisis como salida. Con `--review-before-apply`, informa el comando para aplicar manualmente (`wf-spec-sync-from-prd apply <prd.md> --features ...`).
- Caso normal → aplica automáticamente el conjunto AUTO-APPLY. Invoca con el Skill tool:
  > `wf-spec-sync-from-prd apply <prd.md> --features <IDs minor+delta>`

  Si en el Paso 1 se recibió `--features`, usa la **intersección** de ese subset con el conjunto AUTO-APPLY. Espera a que termine.

---

## Paso 6: Revalidar conflictos y readiness (read-only)

Solo si en el Paso 5c se aplicó al menos un spec:
- Invoca `wf-spec-conflict` para cada spec resincronizado contra el directorio de features (o `wf-spec-features-first` lo hace en bloque si prefieres; aquí invoca conflict directamente por spec). Consolida `_conflict_report.md` si hay conflictos.
- Invoca `wf-spec-readiness <features_dir>/` para regenerar `_readiness_report.md` y el estado por feature.

Si no se aplicó ningún spec, omite este paso e indícalo.

---

## Paso 7: Sincronizar Design (adaptativo)

Aplica profundidad adaptativa:
- Si se pasó `--skip-design`, o la fase `design` no está instalada, o **no existe `DESIGN.md`** en la raíz de diseño → omite esta fase y repórtala como "no aplica".
- Si existe `DESIGN.md` → invoca con el Skill tool:
  > `wf-design-sync <DESIGN.md>`

  Produce `<basename>_design_sync_report.md` con flows/views/ui_prompt/exports stale. **No regeneres** los artefactos de diseño: este paso solo diagnostica; las acciones recomendadas las ejecuta el usuario después.

---

## Paso 8: Reportar planes y tasks stale (adaptativo, read-only)

Para cada feature resincronizada, comprueba mecánicamente si existen artefactos aguas abajo (`Bash`/`Read`):
- `features/<nombre>/plan/<nombre>_plan.md` (o layout plano legacy)
- `features/<nombre>/tasks/<nombre>_tasks.md`

Si las fases `plan`/`tasks` no están instaladas o no hay artefactos → repórtalo como "sin derivados aguas abajo". Si existen → **márcalos como candidatos a revisión** (no los regeneres): un spec que cambió invalida potencialmente su plan y sus tasks. Recomienda `wf-plan-validate` y, si procede, regenerar con `wf-prepare-plan` / `wf-prepare-tasks`.

---

## Paso 9: Consolidar el reporte de cascade

Escribe `<basename>_cascade_report.md` junto al PRD con una fila por fase: fase · ejecutada/omitida/parada · artefacto producido · estado · siguiente acción pendiente. Diferencia explícitamente:
- fases ejecutadas automáticamente,
- checkpoints donde se detuvo esperando decisión humana,
- fases omitidas por profundidad adaptativa (no instalada, sin `DESIGN.md`, sin derivados).

## Paso 10: Degradación con gracia

Si cualquier sub-workflow invocado **no está instalado** (el Skill tool no lo encuentra) o falla:
- no abortes todo el cascade: registra esa fase como `no disponible` con el motivo, continúa con las fases independientes posibles y refléjalo en el reporte de cascade.
- Si la fase fallida es un prerequisito duro de las siguientes (p. ej. el apply de specs falló), detén las dependientes e indícalo.

## Paso 11: Informar al usuario

Presenta el resumen del cascade: qué se ejecutó, dónde se paró y por qué, qué quedó pendiente de decisión humana y cuál es el siguiente comando recomendado. Si el cascade se detuvo en un checkpoint, deja claro el comando exacto para reanudar.
