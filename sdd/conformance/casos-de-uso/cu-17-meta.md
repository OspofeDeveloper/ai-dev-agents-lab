# CU-17 — Autoría y mantenimiento del ecosistema (meta)

**Objetivo:** verificar que las skills meta (creación de skills/agentes/overlays, refactor,
auditoría, inventario) respetan el **gate estructural determinista**, detectan duplicados antes de
crear, delegan en `sdd-author`/`sdd-auditor` sin alterar el frontmatter canónico del scaffold, y que
la auditoría y el inventario **no re-derivan** lo que el lint ya verifica mecánicamente.
**Proyecto a usar:** el **propio repo del ecosistema SDD** (`sdd/`) — estas skills operan sobre el
árbol fuente, no sobre un proyecto de producto.
**Cobertura automática:** alta en lo determinista — `sdd/tests/` cubre `sdd-scaffold.py`,
`sdd-structural-lint.py` y `generate-skill-registry.py`. Lo **manual** es la conducta del agente: no
declarar éxito con `blocking`, no alterar el frontmatter del scaffold, no re-derivar los findings del
lint, no crear piezas nuevas en un refactor.

> [!IMPORTANT]
> **A diferencia del resto de la batería, CU-17 SÍ se prueba dentro del repo del ecosistema** — es
> su objeto. El **gate estructural** (`sdd-structural-lint.py`) es el mecanismo común de
> creación/refactor/overlay: baseline del repo `blocking=0`, así que cualquier `blocking` nuevo es
> atribuible a la pieza recién tocada. Exit 2 → no se cierra; exit 1 (warning) → resumen de una línea,
> no bloquea; sin `python3` → `⚠ gate estructural no ejecutado`, no bloquea.

---

## 🧪 Qué se prueba aquí (por componente)

CU-17 es un **objetivo de usuario** (autoría y mantenimiento del ecosistema), no una sola skill: sus escenarios ejercitan **6 componentes**. Marca cada escenario al ejecutarlo. El estado de cobertura autoritativo (ejes happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) — esta vista es la **transpuesta** para leer/ejecutar el CU.

### `wf-skill-create` — scaffold determinista + gate estructural (1)
- [ ] CU-17.a — Crear una skill: scaffold determinista + gate estructural (el corazón)

### `wf-agent-create` — verificación de KBs y flags derivados por rol (1)
- [ ] CU-17.b — Crear un agente: verificación de KBs y flags derivados por rol

### `wf-stack-create` — crear un overlay de stack (1)
- [ ] CU-17.c — Crear un overlay de stack

### `wf-sdd-audit` — el lint determinista manda (1)
- [ ] CU-17.d — Auditar el ecosistema: el lint determinista manda

### `wf-sdd-refactor` — preservar SSoT, no crear piezas (1)
- [ ] CU-17.e — Refactorizar una pieza: preservar SSoT, no crear piezas

### `wf-sdd-status` — inventario read-only del ecosistema (1)
- [ ] CU-17.f — Inventario read-only del ecosistema

> **Capa determinista** — `sdd/tests/` cubre `sdd-scaffold.py`, `sdd-structural-lint.py` y `generate-skill-registry.py`; lo manual es la conducta del agente (no declarar éxito con `blocking`, no alterar el frontmatter del scaffold, no re-derivar findings del lint).

---

## CU-17.a — Crear una skill: scaffold determinista + gate estructural (el corazón)

**Precondición:** el ecosistema `sdd/`; pides crear una `kb`/`wf` nueva.
**Mecanismo:** skill `wf-skill-create` → `sdd-scaffold.py` (frontmatter canónico) → subagente
**`sdd-author`** (rellena el cuerpo) → `generate-skill-registry.py` → `sdd-structural-lint.py` (gate Paso 9).

1. Pides crear la skill **sin `--phase`**.
   → **Esperado:** se detiene pidiendo la fase (`prd`/`spec`/`design`/`plan`/`tasks`/`tech/<stack>`/`global`).
2. Pides crear una skill que ya existe con dominio equivalente.
   → **Esperado:** se detiene, señala el path existente y sugiere extenderla; solo continúa con `--force` explícito.
3. Creación válida.
   → **Esperado:** `sdd-scaffold.py` escribe el `SKILL.md` con frontmatter canónico; `sdd-author` rellena
     el cuerpo **sin alterar** los campos estructurales (`name`, `user-invocable`, `effort`,
     `allowed-tools`, `context`, `agent`); regenera el registry; corre el gate estructural.
4. El gate devuelve **exit 2** (blocking).
   → **Esperado:** **NO** declara la creación con éxito; atribuye el blocking a la pieza nueva (baseline
     `blocking=0`), lo reporta y exige corregir antes de cerrar; si el blocking es de piezas ajenas preexistentes, lo separa explícitamente.

**Resultado:** PASS si exige fase, frena duplicados, scaffold+author respetan el frontmatter canónico y
exit 2 impide cerrar · FALLO si crea sin fase, pisa un duplicado sin `--force`, altera el frontmatter del scaffold, o declara éxito con blocking nuevo.
**Desviación → reportar:** issue citando `CU-17.a`.

## CU-17.b — Crear un agente: verificación de KBs y flags derivados por rol

**Precondición:** pides crear un agente nuevo.
**Mecanismo:** skill `wf-agent-create` → `sdd-scaffold.py` → **`sdd-author`** → `sdd-structural-lint.py`.
**No** regenera el registry (solo indexa skills).

1. Pides el agente con `--skills kb1,kb2` donde alguna KB no existe.
   → **Esperado:** advierte qué KBs faltan pero **no bloquea** (el agente se crea con esas KBs en `skills:`); reporta verificadas vs faltantes.
2. Creación válida.
   → **Esperado:** deriva los flags de frontmatter por rol (`model` opus para escritores / sonnet para
     auditores; `effort: high` si genera artefactos; `--read-only` si no modifica); el scaffold los escribe;
     `sdd-author` rellena el system prompt sin alterar los campos estructurales; el gate caza un `NAME-MISMATCH` recién introducido.
3. Dominio cognitivo solapado con un agente existente de la fase.
   → **Esperado:** se detiene sugiriendo extender el existente; `--force` para continuar.

**Resultado:** PASS si avisa de KBs ausentes sin bloquear, deriva flags por rol y frena el solapamiento ·
FALLO si bloquea por una KB futura, inventa flags fuera de criterio, o pisa un agente solapado sin `--force`.
**Desviación → reportar:** issue citando `CU-17.b`.

## CU-17.c — Crear un overlay de stack

**Precondición:** pides crear `tech/<stack>`.
**Mecanismo:** skill `wf-stack-create` → `AskUserQuestion` (brief) → **`sdd-author`** → integración
(detección en `wf-project-init` + registry + verificación en temp) → `sdd-structural-lint.py`.

1. El overlay `tech/<stack>` ya existe.
   → **Esperado:** se detiene y remite a `wf-sdd-refactor`; no lo sobrescribe.
2. El stack pedido es variante de uno existente (p. ej. `compose-multiplatform` vs `kmm`).
   → **Esperado:** pregunta antes de continuar (solapamiento semántico).
3. Faltan `--type`/`--detect`/`--description`.
   → **Esperado:** pregunta con `AskUserQuestion` (una por dato faltante) antes de generar.
4. Generación válida.
   → **Esperado:** `sdd-author` crea `install.sh`, `wf-<stack>-init`, `CLAUDE.md`, `skills/plan|tasks`
     (+ variantes de agentes **solo** con `--with-agents`); añade la condición de detección a
     `wf-project-init`; regenera el registry; corre el gate estructural.

**Resultado:** PASS si frena un overlay existente, pregunta el brief y el gate cierra limpio · FALLO si
sobrescribe un overlay, genera sin brief, o declara éxito con blocking nuevo.
**Desviación → reportar:** issue citando `CU-17.c`.

## CU-17.d — Auditar el ecosistema: el lint determinista manda

**Precondición:** el ecosistema `sdd/`.
**Mecanismo:** skill `wf-sdd-audit <structural|content|full>` → `sdd-structural-lint.py` (Paso 3.5, modos
`structural`/`full`) → subagente **`sdd-auditor`** (añade solo juicio no mecanizable). Output: `sdd/docs/audit_<modo>_<fase>.md`.

1. Pides una auditoría `structural` (o `full`).
   → **Esperado:** ejecuta `sdd-structural-lint.py` y pasa sus findings al agente como **SSoT verificada**;
     el agente **no los re-deriva** por prosa, solo añade el juicio estructural no mecanizable (huérfanas con matiz, drift de rootmap).
2. Pides una auditoría `content` pura.
   → **Esperado:** omite el lint estructural y audita SSoT/SRP/contradicciones/inconsistencias.
3. Tras corregir todos los hallazgos.
   → **Esperado:** el reporte `audit_*.md` es **temporal** — se elimina una vez corregido (no es documentación permanente).

**Resultado:** PASS si el lint alimenta al agente sin que este re-derive y el modo acota el alcance ·
FALLO si el agente re-deriva a ojo lo que el lint ya verifica, o trata el reporte como permanente.
**Desviación → reportar:** issue citando `CU-17.d`.

## CU-17.e — Refactorizar una pieza: preservar SSoT, no crear piezas

**Precondición:** una skill/agente existente del ecosistema.
**Mecanismo:** skill `wf-sdd-refactor <path>` → lee la pieza + relacionadas → **`sdd-author`** (diagnostica
y aplica) → registry si cambió `name`/`description`/ubicación → `sdd-structural-lint.py` (**siempre** corre).

1. Pides refactorizar una pieza que mezcla responsabilidades.
   → **Esperado:** `sdd-author` aplica solo lo seguro (extensión, corrección de frontmatter/estructura) **sin eliminar reglas que sean SSoT de otras piezas**.
2. La refactorización implica partir la pieza en dos (crear piezas nuevas).
   → **Esperado:** **NO** crea las piezas nuevas; las describe y remite a `wf-skill-create`/`wf-agent-create`;
     informa qué piezas relacionadas (agentes que cargan la KB, `CLAUDE.md` con rootmap) deben actualizarse.
3. El gate estructural corre **aunque no cambie el `name:`**.
   → **Esperado:** exit 2 → no cierra (una cita de regla rota o ruta de `references` inválida por el refactor es atribuible); exit 1 → resumen de una línea, no bloquea.

**Resultado:** PASS si preserva la SSoT ajena, no crea piezas y el gate siempre corre · FALLO si borra
reglas SSoT de otra pieza, crea piezas nuevas por su cuenta, o cierra con blocking nuevo.
**Desviación → reportar:** issue citando `CU-17.e`.

## CU-17.f — Inventario read-only del ecosistema

**Precondición:** el ecosistema `sdd/`.
**Mecanismo:** skill `wf-sdd-status` (**sin agente**, mecánico) → conteo + `generate-skill-registry.py` (en `global`). Read-mostly.

1. Pides el inventario del ecosistema.
   → **Esperado:** cuenta skills/agentes por fase, lista KBs y workflows; marca `[SIN CONSUMIDOR]` las KBs
     que ningún agente carga y `[SIN REGISTRAR]` las `wf-*` que ningún `CLAUDE.md` referencia; **no razona ni audita contenido** (eso es `wf-sdd-audit`).
2. Run global.
   → **Esperado:** regenera `sdd/meta/skill-registry.md` con el script determinista (**no a mano**); si falta `python3`, avisa `⚠ No se pudo actualizar skill-registry.md` sin romper.
3. Proyecto consumidor con sello de versión.
   → **Esperado:** compara el sello con la versión del ecosistema y reporta la deriva (sugerencia `/wf-sdd-update`) sin bloquear.

**Resultado:** PASS si inventaría read-only, marca huérfanas/sin-registrar y regenera el registry por script ·
FALLO si edita el registry a mano, hace auditoría de contenido, o inventa estado.
**Desviación → reportar:** issue citando `CU-17.f`.
