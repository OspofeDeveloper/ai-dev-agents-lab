# CU-10 — Robustez e instalación

**Objetivo:** verificar que la instalación y actualización del ecosistema son
resilientes: el update reinstala lo declarado sin re-entrevistar y preserva el overlay
de stack, `--prune` poda huérfanos, los layouts legacy se leen sin migrar, los
marcadores se encuentran hacia arriba en monorepos, y la falta de `python3` degrada con
gracia. Además, el estado de delivery se reporta de forma determinista.
**Proyecto a usar:** proyectos reales según el escenario — un proyecto ya en SDD
(mejor instalado con una versión anterior) para update/`--prune`; un **monorepo real**
para la resolución de marcadores; un proyecto creado con una versión SDD **antigua**
(layout plano) o reproducido a mano para el layout legacy; cualquiera en un entorno sin
`python3`.
**Cobertura automática:** alta — `sdd/tests/test_install_sh.py`,
`test_kmm_install_sh.py` y `test_setup_sh.py` cubren los installers; los scripts de
estado tienen sus propios tests. Lo manual es la conducta del agente al orquestar el
update y leer layouts.

> [!IMPORTANT]
> **El update no re-entrevista ni toca artefactos.** `wf-sdd-update` reinstala solo la
> **infraestructura** (skills, agentes, rules, scripts, settings) que el proyecto ya
> declaró; nunca specs, plans ni tasks.

---

## 🧪 Qué se prueba aquí (por componente)

CU-10 es un **objetivo de usuario** (robustez e instalación), no una sola skill: sus
escenarios ejercitan **6 componentes**. Marca cada escenario al ejecutarlo. El estado de
cobertura autoritativo (ejes happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md)
— esta vista es la **transpuesta** para leer/ejecutar el CU.

### `wf-sdd-update` — actualizar la instalación SDD sin re-entrevistar (5)
- [ ] CU-10.a — Actualizar un proyecto con overlay de stack
- [ ] CU-10.i — Update sin novedad: "ya está al día" y override con `--force`
- [ ] CU-10.j — Update sobre un proyecto sin instalación SDD
- [ ] CU-10.k — El update no toca artefactos ni re-ejecuta el init de stack
- [x] CU-10.l — El update corre en el hilo principal y confirma con `AskUserQuestion` · ✓ 2026-06-21 ([[D-016]]: sobre repo KMM real 0.36.0→0.37.0, **reproducido en 2 sesiones distintas**; aviso de drift en una línea sin auto-actualizar, gate `AskUserQuestion` (Actualizar/Cancelar) renderizado en hilo principal, install real (base+overlay), sello sincronizado; `wf-bug` aterrizó sin `context: fork`)

### `install.sh` — instalación e idempotencia (2)
- [ ] CU-10.b — `--prune` poda piezas huérfanas
- [ ] CU-10.g — Merge idempotente de `settings.json`

### Lectura de layouts por los workflows — layout legacy plano (1)
- [ ] CU-10.c — Layout legacy plano se lee sin migrar

### Resolución de marcadores hacia arriba — sesión en monorepo (1)
- [ ] CU-10.d — Sesión en un subpaquete de monorepo

### Wrappers de hooks y scripts — degradación sin `python3` (1)
- [ ] CU-10.e — Degradación sin `python3`

### `wf-project-status` — estado de delivery determinista (read-only) (1)
- [ ] CU-10.f — Estado de delivery determinista (`wf-project-status`)

### `wf-task-run` / `wf-qa-verify` — verificación con `tests: none` (1)
- [ ] CU-10.h — Degradación con `tests: none`

> **Capa determinista:** los installers están cubiertos por `sdd/tests/test_install_sh.py`,
> `test_kmm_install_sh.py` y `test_setup_sh.py`, y los scripts de estado por sus propios
> tests; lo manual es la conducta del agente al orquestar el update y leer layouts.

---

## CU-10.a — Actualizar un proyecto con overlay de stack

**Precondición:** un proyecto SDD inicializado con stack concreto (p. ej. KMM), en
versión anterior a la del ecosistema.
**Mecanismo:** skill `wf-sdd-update` → relee `phases`/`stack` de `project-init.json` →
`install.sh <fases> --prune` (base) → re-aplica el overlay **DESPUÉS**.

1. Le pides actualizar el SDD del proyecto.
   → **Esperado:** no re-entrevista; reinstala las fases declaradas con `--prune` y
     **re-aplica el overlay de stack después de la base** (el orden inverso dejaría el
     proyecto en genérico). Muestra los avisos `⚠` del CHANGELOG (cambios que rompen).

**Resultado:** PASS si reinstala lo declarado, conserva el overlay y muestra los avisos
· FALLO si re-entrevista, deja el proyecto en genérico, o silencia los `⚠`.
**Desviación → reportar:** issue citando `CU-10.a`.

## CU-10.b — `--prune` poda piezas huérfanas

**Precondición:** un proyecto donde existen skills/agentes SDD de fases que ya no están
declaradas en `project-init.json`.
**Mecanismo:** `install.sh … --prune` (orquestado por `wf-sdd-update`).

1. Actualizas con `--prune`.
   → **Esperado:** elimina del `.claude/` las skills/agents SDD de fases no
     seleccionadas (huérfanos), y lo refleja.
2. Reinstalas **sin** `--prune`.
   → **Esperado:** **avisa** de los huérfanos pero no los borra.

**Resultado:** PASS si poda con `--prune` y solo avisa sin él · FALLO si borra sin
`--prune`, o no detecta los huérfanos.
**Desviación → reportar:** issue citando `CU-10.b`.

## CU-10.c — Layout legacy plano se lee sin migrar

**Precondición:** un proyecto real con layout plano legacy
(`features/<n>/<n>_spec.md` sin subcarpetas `spec/`/`plan/`/…).
**Mecanismo:** los workflows leen ambos layouts y no los mezclan dentro de una feature.

1. Le pides operar sobre una feature en layout plano (validar, planificar, etc.).
   → **Esperado:** la lee correctamente **sin migrarla** al layout de subcarpetas, y no
     mezcla ambos dentro de la misma feature.

**Resultado:** PASS si opera sobre el layout plano sin migrarlo · FALLO si falla al
leerlo, o lo migra/mezcla por su cuenta.
**Desviación → reportar:** issue citando `CU-10.c`.

## CU-10.d — Sesión en un subpaquete de monorepo

**Precondición:** un monorepo real con `.sdd/` en un **ancestro** y la sesión abierta en un
subpaquete.
**Mecanismo:** búsqueda de marcadores hacia arriba hasta la raíz git (espejo de
`CU-1.g`, aquí desde la óptica de los workflows y scripts).

1. Le pides el estado del proyecto (o cualquier workflow) desde el subpaquete.
   → **Esperado:** resuelve `.sdd/project-init.json` y la raíz de artefactos buscando
     hacia arriba hasta el git root (gana el ancestro más cercano); opera contra esa
     raíz.

**Resultado:** PASS si encuentra los marcadores en el ancestro · FALLO si no los
encuentra y trata el subpaquete como proyecto independiente.
**Desviación → reportar:** issue citando `CU-10.d`.

## CU-10.e — Degradación sin `python3`

**Precondición:** un entorno sin `python3` en el PATH.
**Mecanismo:** wrappers de hooks y scripts (fail-open / aviso).

1. Operas en ese entorno (gates, estado de tasks, etc.).
   → **Esperado:** los gates **permiten** (fail-open, ver `CU-9.m`); los workflows que
     necesitan un script ausente **avisan** de que falta y cómo reponerlo (re-ejecutar
     `install.sh`), sin romper la sesión.

**Resultado:** PASS si degrada con gracia (permite / avisa) · FALLO si una operación
legítima se rompe sin explicación por falta de `python3`.
**Desviación → reportar:** issue citando `CU-10.e`.

## CU-10.f — Estado de delivery determinista (`wf-project-status`)

**Precondición:** un proyecto con varias features en distintas fases.
**Mecanismo:** skill `wf-project-status` (**sin agente**, `sdd-project-status.py`
agrega el estado ya sellado). **Read-only.**

1. Le pides el estado del proyecto ("¿cómo va?", "¿qué está bloqueado?").
   → **Esperado:** por cada feature, su fase (Spec/Plan/Tasks/QA/Cerrada), estado,
     bloqueo y siguiente acción; agrega lo sellado en los artefactos **sin editar
     nada** ni razonar. Una feature cerrada muestra su release.
2. Falta `sdd-project-status.py`.
   → **Esperado:** avisa de que falta y pide re-ejecutar `install.sh`, sin inventar el
     estado.

**Resultado:** PASS si reporta read-only desde lo sellado · FALLO si edita artefactos,
o fabrica el estado cuando falta el script.
**Desviación → reportar:** issue citando `CU-10.f`.

## CU-10.g — Merge idempotente de `settings.json`

**Precondición:** un proyecto con `.claude/settings.json` que contiene ajustes propios
del equipo (permisos, env, hooks ajenos al SDD).
**Mecanismo:** `install.sh` → `merge-claude-settings.py` (merge, no sobrescritura).

1. Instalas o actualizas el SDD sobre ese proyecto.
   → **Esperado:** añade lo que el SDD necesita (su hook, sus entradas) **preservando
     los ajustes del equipo**; no pisa permisos ni env propios.
2. Re-ejecutas la instalación.
   → **Esperado:** el merge es **idempotente** — no duplica el hook ni las entradas SDD.

**Resultado:** PASS si preserva lo del equipo y no duplica al reinstalar · FALLO si
sobrescribe settings ajenos, o duplica entradas en reinstalaciones.
**Desviación → reportar:** issue citando `CU-10.g`.

## CU-10.h — Degradación con `tests: none`

**Precondición:** un proyecto cuyo `project-init.json`/config declara que no hay
framework de tests ejecutable (`tests: none`).
**Mecanismo:** `wf-task-run` / `wf-qa-verify` (verificación adaptada a la ausencia de
tests automatizables).

1. Ejecutas tasks o verificas QA en ese proyecto.
   → **Esperado:** no asume un runner de tests inexistente: degrada con gracia (DoD/QA
     por evidencia manual marcada como tal — `MANUAL_PENDIENTE` en QA), sin fabricar
     resultados de tests que no se ejecutaron ni romper el flujo.

**Resultado:** PASS si adapta la verificación sin inventar ejecución de tests · FALLO si
exige un runner ausente, o reporta cobertura sin evidencia real.
**Desviación → reportar:** issue citando `CU-10.h`.

## CU-10.i — Update sin novedad: "ya está al día" y override con `--force`

**Precondición:** un proyecto SDD cuyo `sdd-version.json` coincide en **versión y commit** con el
ecosistema (`$SDD_HOME/VERSION` + HEAD).
**Mecanismo:** `wf-sdd-update` Paso 2 — misma versión y commit → informa y **detiene**, salvo
`--force` (reinstalación íntegra del mismo estado).

1. Le pides actualizar el SDD sin más.
   → **Esperado:** informa "ya está al día (X+sha)" y **se detiene** sin reinstalar nada.
2. Le pides forzar la reinstalación aunque esté al día (p. ej. "reinstala el SDD aunque esté igual,
   creo que se me corrompió una skill").
   → **Esperado:** el orquestador invoca el update con **`--force`** y reinstala el mismo estado
     íntegro; **no** inyecta `--force` en el escenario 1, donde no se pidió.

**Resultado:** PASS si detiene sin novedad y solo reinstala con `--force` cuando lo pides · FALLO si
reinstala sin novedad sin pedírselo, o ignora la petición de forzar.
**Desviación → reportar:** issue citando `CU-10.i`.

## CU-10.j — Update sobre un proyecto sin instalación SDD

**Precondición:** un directorio **sin** `.sdd/project-init.json` y **sin** rastro SDD
(`.claude/rules/sdd-*.md`, `.sdd/sdd-version.json`).
**Mecanismo:** `wf-sdd-update` Paso 1 — si no localiza la raíz del proyecto ni rastro SDD, detiene.

1. Le pides actualizar el SDD en ese directorio.
   → **Esperado:** **detiene** e indica que el proyecto no tiene instalación SDD y que para inicializar
     debe usarse `/wf-project-init`; no reinstala ni inventa fases.
2. (Variante) el proyecto tiene `rules/sdd-*.md` pero no `project-init.json` (standalone sin init).
   → **Esperado:** deriva las fases de los `rules/sdd-<fase>.md` presentes y continúa, avisándolo en el reporte.

**Resultado:** PASS si detiene sin rastro SDD y deriva fases en standalone · FALLO si intenta actualizar
un directorio sin SDD, o no reconoce una instalación standalone.
**Desviación → reportar:** issue citando `CU-10.j`.

## CU-10.k — El update no toca artefactos ni re-ejecuta el init de stack

**Precondición:** un proyecto SDD con specs/plans/tasks ya escritos y stack concreto (p. ej. KMM con su
`<stack>_project_state.md`), en versión anterior a la del ecosistema.
**Mecanismo:** `wf-sdd-update` — reinstala **solo infraestructura** (skills, agentes, rules, scripts,
settings); no toca artefactos ni el estado de proyecto del stack.

1. Le pides actualizar el SDD.
   → **Esperado:** actualiza la infraestructura, pero los specs/plans/tasks quedan **intactos** (mismo
     contenido); **no** re-ejecuta `wf-<stack>-init` ni reescribe `<stack>_project_state.md` (es estado
     del PROYECTO, no del ecosistema).

**Resultado:** PASS si la infraestructura se actualiza dejando artefactos y estado de stack intactos ·
FALLO si modifica un spec/plan/task, o re-corre el init de stack.
**Desviación → reportar:** issue citando `CU-10.k`.

## CU-10.l — El update corre en el hilo principal y confirma con `AskUserQuestion`

**Precondición:** un proyecto SDD en versión anterior a la del ecosistema (hay drift real).
**Mecanismo:** `wf-sdd-update` en el **hilo principal** ([[D-016]]: sin `context: fork`; el gate del
Paso 3 usa `AskUserQuestion`). Espejo de `CU-12.b` para el update.

1. Le pides actualizar el SDD del proyecto.
   → **Esperado:** presenta el plan (versión→versión, fases, overlay si aplica, avisos `⚠`) y
     **confirma con `AskUserQuestion`** (opciones reales Actualizar / Cancelar, no texto plano);
     solo instala tras la confirmación. La ejecución hace el trabajo real (no devuelve una respuesta
     genérica de fork).
2. Eliges "Cancelar" en el gate.
   → **Esperado:** cierra sin instalar nada.

**Resultado:** PASS si el gate se presenta con `AskUserQuestion` en el hilo principal y el update
ejecuta el trabajo real tras confirmar · FALLO si pregunta como texto plano (señal de fork), instala
sin confirmar, o la ejecución forked devuelve una respuesta genérica sin instalar.
**Desviación → reportar:** issue citando `CU-10.l`.
