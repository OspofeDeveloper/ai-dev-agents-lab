# CU-15 — Deriva, trazabilidad y recuperación

**Objetivo:** verificar que el sistema **no deja que la SSoT mienta** en uso real:
detecta la deriva cuando editas artefactos a mano, mantiene la trazabilidad
(CA→TC→task→commit) cuando un spec cambia, y **recupera/retoma** ejecuciones
interrumpidas sin dar por buenas las cosas a medias.
**Proyecto a usar:** un proyecto real **con el pipeline avanzado** (PRD + specs + plan
+ algunas tasks), para tener artefactos derivados sobre los que provocar
deriva/rotura/interrupción.
**Cobertura automática:** el hash drift (`sdd-sync-check.py`), el sello
(`sdd-seal.py`), la máquina de tasks (`sdd-task-state.py`) y el índice
(`sdd-features-index.py`) tienen tests deterministas; lo que se prueba a mano es la
**conducta del agente** ante esos estados (avisar, no fabricar, reanudar, no pisar).

> [!IMPORTANT]
> **Es el cluster que evita que un sistema spec-driven mienta.** Varios escenarios son
> **sondas**: puede que el sistema aún no tenga la red y el test revele un hueco real
> (marcado con 🔎). Eso es precisamente lo que queremos descubrir antes de confiar en él.

---

## 🧪 Qué se prueba aquí (por componente)

CU-15 es un **objetivo de usuario** (que la SSoT no mienta: deriva, trazabilidad y recuperación), no una sola skill: sus escenarios ejercitan **8 componentes**. Marca cada escenario al ejecutarlo. El estado de cobertura autoritativo (ejes happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) — esta vista es la **transpuesta** para leer/ejecutar el CU.

### `sdd-sync-check.py` — detección de deriva por hash + `wf-prd-sync-impact` (1)
- [ ] CU-15.a — Editar el PRD a mano tras derivar specs

### enlace spec→plan — sondeo de staleness sin hash declarado 🔎 (1)
- [ ] CU-15.b — Editar un spec a mano tras sellar el plan 🔎

### `wf-spec-conflict` — shared models inconsistentes a posteriori 🔎 (1)
- [ ] CU-15.c — Un shared model cambia después de que otra feature lo consume 🔎

### trazabilidad CA→TC→task — refs colgantes al borrar/renumerar un CA 🔎 (1)
- [ ] CU-15.d — Un delta borra/renumera un CA que una task ya referencia 🔎

### `wf-spec-features-first` + `sdd-features-index.py` — aislamiento de fallo e índice coherente (1)
- [ ] CU-15.e — `features-first` con una feature que falla en paralelo

### `sdd-task-state.py` — reanudar una task `EN_CURSO` (autor ≠ marcador) (1)
- [ ] CU-15.f — `task-run` interrumpida con una task en `EN_CURSO`

### generadores pesados — idempotencia / no clobbear en silencio (1)
- [ ] CU-15.g — Re-ejecutar un generador pesado sobre algo ya generado

### `wf-spec-discover` + `sdd-features-index.py` — regeneración incremental sin pisar ediciones (1)
- [ ] CU-15.h — Re-correr `discover` tras editar `_features.md` a mano

> **Capa determinista** — `sdd-sync-check.py`, `sdd-seal.py`, `sdd-task-state.py` y `sdd-features-index.py` tienen tests deterministas en `sdd/tests/`; aquí se prueba a mano la **conducta del agente** ante esos estados.

---

## CU-15.a — Editar el PRD a mano tras derivar specs

**Precondición:** specs con `derived_from_prd_hash`; editas el `prd.md` directamente,
**sin** pasar por `wf-prd-change`.
**Mecanismo:** `derived_from_prd_hash` + `sdd-sync-check.py` (gate, ver `CU-9.i`) +
`wf-prd-sync-impact` (read-only).

1. Editas el PRD a mano y luego pides avanzar de fase sobre un spec derivado.
   → **Esperado:** el gate detecta la deriva por hash y deniega (como `CU-9.i`).
2. Pides "¿qué quedó stale tras tocar el PRD?".
   → **Esperado:** `wf-prd-sync-impact` marca los specs derivados **al menos**
     `needs_review`; no reporta `in_sync` algo cuyo PRD origen cambió.

**Resultado:** PASS si la deriva se detecta y se reporta · FALLO si avanza como si nada,
o marca `in_sync` un derivado con el PRD cambiado.
**Desviación → reportar:** issue citando `CU-15.a`.

## CU-15.b — Editar un spec a mano tras sellar el plan 🔎

**Precondición:** un `_plan.md` `VALIDADO` derivado de un spec; editas ese spec a mano.
**Mecanismo:** sondeo del enlace spec→plan (más débil que PRD→spec: no hay hash
equivalente declarado).

1. Editas el `_spec.md` a mano y pides ejecutar las tasks (o avanzar).
   → **Esperado:** el sistema **no debería** tratar el plan como vigente sin avisar de
     que su spec origen cambió; debería remitir a revalidar/resincronizar.

**Resultado:** PASS si avisa de que el plan quedó potencialmente stale · FALLO si trata
el plan como vigente sin señal alguna. 🔎 **Sonda:** si nada lo detecta, es un hueco
real (no hay staleness spec→plan) → reportar como tal.
**Desviación → reportar:** issue citando `CU-15.b`.

## CU-15.c — Un shared model cambia después de que otra feature lo consume 🔎

**Precondición:** dos features comparten un *shared model* (declarado en el discovery);
cambias ese modelo en una de ellas.
**Mecanismo:** `wf-spec-conflict` (detección de shared models inconsistentes).

1. Modificas el shared model en la feature A (vía delta) y pides comprobar conflictos.
   → **Esperado:** `wf-spec-conflict` detecta que la feature B consume una versión
     **incoherente** del modelo y lo reporta; no lo da por consistente.

**Resultado:** PASS si detecta la incoherencia del shared model a posteriori · FALLO si
no la ve. 🔎 **Sonda:** confirma si el conflict se dispara solo cuando lo pides o si
hay aviso proactivo.
**Desviación → reportar:** issue citando `CU-15.c`.

## CU-15.d — Un delta borra/renumera un CA que una task ya referencia 🔎

**Precondición:** una task con `Spec CA: CA-007` (o un TC de QA que lo cubre); aplicas
un `wf-spec-delta` que **elimina o renumera** ese CA.
**Mecanismo:** trazabilidad CA→TC→task (`kb-traceability-rules` Regla 11).

1. Aplicas el delta que quita/renumera el CA referenciado.
   → **Esperado:** el sistema **avisa** de que hay referencias aguas abajo (tasks/TCs)
     a ese CA antes de dejarlo colgante; no rompe la cadena en silencio.

**Resultado:** PASS si avisa de las refs colgantes · FALLO si borra/renumera el CA
dejando tasks/TCs apuntando a la nada sin señal. 🔎 **Sonda:** es la rotura directa de
la cadena de trazabilidad; si nadie la detecta, hueco grave.
**Desviación → reportar:** issue citando `CU-15.d`.

## CU-15.e — `features-first` con una feature que falla en paralelo

**Precondición:** un PRD con varias features; provocas que **una** falle al generarse
(p. ej. spec con gap irresoluble).
**Mecanismo:** `wf-spec-features-first` (orquestación paralela) + `sdd-features-index.py`
(`_features.md` incremental con `PENDIENTE_GENERACIÓN`).

1. Lanzas `features-first` y una feature falla.
   → **Esperado:** las demás se completan; la fallida queda **`PENDIENTE_GENERACIÓN`**
     (o equivalente) en un `_features.md` **coherente**, no a medias; se te informa de
     cuál falló.
2. Vuelves a lanzar para la fallida.
   → **Esperado:** la reprocesa sin rehacer ni pisar las ya generadas.

**Resultado:** PASS si aísla el fallo, deja índice coherente y permite reanudar · FALLO
si corrompe `_features.md`, aborta todas, o pierde las ya generadas.
**Desviación → reportar:** issue citando `CU-15.e`.

## CU-15.f — `task-run` interrumpida con una task en `EN_CURSO`

**Precondición:** una task quedó `EN_CURSO` sin commit (sesión cortada, Esc, crash).
**Mecanismo:** `sdd-task-state.py` (estados; `check`/`next`; reapertura con `--force`).

1. Retomas la feature: pides ejecutar la siguiente task.
   → **Esperado:** `check`/`next` muestra la task `EN_CURSO`; el sistema la **reanuda**
     (o la reabre con `--force`) en vez de saltarla o darla por `HECHA`; no marca estado
     a mano (autor ≠ marcador).

**Resultado:** PASS si detecta el `EN_CURSO` y permite reanudar de forma trazable ·
FALLO si la da por hecha, la duplica, o marca estados a mano.
**Desviación → reportar:** issue citando `CU-15.f`.

## CU-15.g — Re-ejecutar un generador pesado sobre algo ya generado

**Precondición:** ya existen specs / plan / tasks / DESIGN.md generados (con o sin
ediciones manuales tuyas posteriores).
**Mecanismo:** `wf-spec-features-first` / `wf-prepare-plan` / `wf-prepare-tasks` /
`wf-design-system` (idempotencia; espejo de la confirmación de `CU-2.d`).

1. Vuelves a pedir "genera las specs" / "genera el plan" / "crea el DESIGN.md".
   → **Esperado:** **pregunta antes de sobrescribir** (o es incremental y preserva lo
     previo / tus ediciones manuales); no pisa en silencio.

**Resultado:** PASS si pregunta o preserva · FALLO si **clobbea en silencio** un
artefacto existente y se pierden ediciones manuales.
**Desviación → reportar:** issue citando `CU-15.g`.

## CU-15.h — Re-correr `discover` tras editar `_features.md` a mano

**Precondición:** editaste `_features.md` a mano (renombraste una feature, ajustaste un
scope).
**Mecanismo:** `wf-spec-discover` + `sdd-features-index.py` (regeneración incremental).

1. Vuelves a lanzar el discovery.
   → **Esperado:** respeta/funde tus ediciones donde corresponde y mantiene las features
     ya generadas; no **clobbea** tus cambios manuales sin avisar.

**Resultado:** PASS si preserva tus ediciones y el estado de las features · FALLO si
sobrescribe `_features.md` perdiendo lo editado a mano.
**Desviación → reportar:** issue citando `CU-15.h`.
