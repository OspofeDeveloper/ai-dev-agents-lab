# CU-7 — Cambiar el producto y propagar el cambio

**Objetivo:** verificar que un cambio de producto se gestiona con traza
(clasificación, changelog, CR), que medir su impacto aguas abajo es read-only y
conservador, y que la cascada propaga el cambio parando solo en los checkpoints
humanos reales.
**Proyecto a usar:** un proyecto real con un PRD ya `LISTO` (CU-2) y artefactos
derivados (specs, plans, de CU-3/CU-6), sobre el que introduzcas un cambio de alcance
real.
**Cobertura automática:** el pre-pass de hash de `wf-prd-sync-impact` está cubierto
por `sdd/tests/test_sdd_sync_check.py`; la clasificación del cambio y la conducta de
la cascada son juicio del agente → **manuales**.

> [!IMPORTANT]
> **Distinción rectora.** Una `CLARIFICATION` no toca el PRD ni dispara sync. Solo un
> cambio de producto real (`BEHAVIOR`/`SCOPE`/`PRIORITY`/`DEPRECATION`) abre traza y
> se propaga. La gobernanza la aplica `prd-expert` con `kb-product-change-governance`.

---

## 🧪 Qué se prueba aquí (por componente)

CU-7 es un **objetivo de usuario** (cambiar el producto y propagar el cambio), no una
sola skill: sus escenarios ejercitan **4 componentes** del subsistema de cambio de
producto. Marca cada escenario al ejecutarlo. El estado de cobertura autoritativo (ejes
happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) — esta vista es la
**transpuesta** para leer/ejecutar el CU.

### `wf-prd-change` — gestionar un cambio de producto (3)
- [ ] CU-7.a — Un cambio que es solo aclaración (CLARIFICATION)
- [ ] CU-7.b — Un cambio de producto real + reapertura del sello (D-028)
- [ ] CU-7.c — Expansión de capacidad disfrazada de aclaración (Regla 4.1)

### `wf-prd-sync-impact` — medir impacto aguas abajo (2)
- [ ] CU-7.d — Matriz de impacto por artefacto
- [ ] CU-7.e — Criterio conservador

### `wf-prd-change-cascade` — propagar el cambio por el pipeline (6)
- [ ] CU-7.f — Cascada normal (auto + paradas reales)
- [ ] CU-7.g — La cascada con un cambio que es solo aclaración
- [ ] CU-7.h — Cascada sin un cambio que propagar
- [ ] CU-7.i — Features no triviales en el conjunto STOP
- [ ] CU-7.j — `--dry-run` / `--review-before-apply` no escriben
- [ ] CU-7.k — Profundidad adaptativa y degradación con gracia

### `wf-spec-sync-from-prd` — resincronizar specs tras el cambio (2)
- [ ] CU-7.l — Analizar y aplicar la resincronización de specs
- [ ] CU-7.m — Resincronización que rebasa un delta razonable

> **Capa determinista**: el pre-pass de hash de `wf-prd-sync-impact`
> (`sdd-sync-check.py`) está cubierto por `sdd/tests/test_sdd_sync_check.py`; aquí se
> verifica solo la **conducta del agente** (clasificación del cambio y conducta de la
> cascada).

---

## `wf-prd-change` — gestionar un cambio de producto

> **Mecanismo común:** skill `wf-prd-change` → subagente **`prd-expert`**
> (+ `kb-product-change-governance`). Output según clasificación: nada / PRD
> actualizado + `product-changelog.md` + `changes/CR-XXX/{change-request,decision}.md`.

### CU-7.a — Un cambio que es solo aclaración (CLARIFICATION)

**Precondición:** el cambio no contradice el PRD ni mueve alcance.
**Mecanismo:** `wf-prd-change` → `prd-expert` (clasificación).

1. Le describes un cambio que en realidad solo aclara algo ya comprometido.
   → **Esperado:** clasifica `CLARIFICATION`, **no reescribe el PRD**, recomienda
     `wf-spec-gap-resolve` o `wf-spec-delta` según el artefacto afectado y **se
     detiene** (no resincroniza).

**Resultado:** PASS si no toca el PRD ni abre CR · FALLO si edita el PRD o abre
`changes/CR-XXX/` para una aclaración.
**Desviación → reportar:** issue citando `CU-7.a`.

### CU-7.b — Un cambio de producto real (y la reapertura del sello, D-028)

**Precondición:** un PRD ya **sellado** (`status: approved`, `Aprobado por:` relleno — el
estado natural tras pasar la review) y un cambio que altera alcance, reglas o prioridades.
**Mecanismo:** `wf-prd-change` → `prd-expert`. La **reapertura del sello** la hace
`wf-prd-change` (Paso 5), pero **no re-sella**: el sello solo lo restablece `wf-prd-review`.

1. Le describes un cambio que mueve el alcance ("ahora también quiero compartir gastos en
   grupo con otras personas").
   → **Esperado:** actualiza versión/fecha y **solo** las secciones afectadas del PRD;
     registra `product-changelog.md` + `changes/CR-XXX/`; recomienda `wf-prd-sync-impact`.
2. **Reapertura del sello ([[D-028]]/[[D-032]]):** como el PRD estaba sellado (`status: approved`),
   tras aplicar el cambio `wf-prd-change` llama a `sdd-prd-apply.py --reopen` — baja `status:` a
   `in-review` y **resetea `Aprobado por:` al placeholder pendiente** (el sello no puede certificar
   un contenido que ya cambió), y remite a `wf-prd-review`.
   → **Esperado (verificable):** `sdd-prd-ready.py` sobre el PRD cambiado da `UNSEALED`
     (o `OPEN_ASSUMPTIONS` si el cambio introdujo nuevas `[ASUNCIÓN]`), **nunca `READY`**;
     `status: in-review` y `wf-prd-change` **no** escribe un `Aprobado por:` nuevo.
3. Vuelves a pasar `wf-prd-review` sobre el PRD cambiado y lo apruebas.
   → **Esperado:** el sello se restablece **solo aquí**, re-capturando la identidad (D-027)
     y con la fecha del cambio; el `Aprobado por:` vuelve a estar relleno.

**Resultado:** PASS si toca solo lo afectado, deja traza completa, **reabre el sello** al
cambiar (queda `in-review` / `UNSEALED`) y solo `wf-prd-review` lo re-sella · FALLO si
reescribe secciones intactas, mete tecnología, no deja traza, **o deja el PRD `approved`
con un `Aprobado por:` que certifica el contenido viejo** (el agujero que cierra D-028).
**Desviación → reportar:** issue citando `CU-7.b`.

### CU-7.c — Expansión de capacidad disfrazada de aclaración (Regla 4.1)

**Precondición:** la "aclaración" introduce una entidad/catálogo/flujo/owner nuevo no
comprometido.
**Mecanismo:** `wf-prd-change` → `prd-expert` (reclasificación por Regla 4.1).

1. Le presentas como simple aclaración algo que en realidad añade capacidad nueva.
   → **Esperado:** lo **reclasifica** como `BEHAVIOR_CHANGE` o `SCOPE_CHANGE` (no basta
     `CLARIFICATION`) y lo trata como cambio de producto con su traza.

**Resultado:** PASS si reclasifica y deja traza · FALLO si lo deja pasar como
aclaración y expande el alcance en silencio.
**Desviación → reportar:** issue citando `CU-7.c`.

---

## `wf-prd-sync-impact` — medir impacto aguas abajo

> **Mecanismo común:** skill `wf-prd-sync-impact` (vive en la fase **spec**) →
> subagente **`sdd-spec-auditor`**. **Read-only.** Pre-pass determinista
> `sdd-sync-check.py check-all <dir> --mark`. Output: `<basename>_sync_report.md`.

### CU-7.d — Matriz de impacto por artefacto

**Precondición:** un PRD cambiado con artefactos derivados (analysis, discovery,
features, specs, plans, tasks).
**Mecanismo:** `wf-prd-sync-impact` → `sdd-spec-auditor` + `sdd-sync-check.py`.

1. Tras cambiar el PRD, le pides ver qué quedó desactualizado aguas abajo.
   → **Esperado:** produce `<basename>_sync_report.md` con estado por artefacto
     (`in_sync` / `needs_review` / `stale` / `unknown`) + motivo + acción recomendada.
     Un spec que el script reporta `DERIVA` queda **al menos** `needs_review`. **No
     modifica** ningún artefacto.

**Resultado:** PASS si reporta sin tocar nada y respeta la deriva por hash · FALLO si
modifica artefactos, o marca `in_sync` algo con deriva detectada.
**Desviación → reportar:** issue citando `CU-7.d`.

### CU-7.e — Criterio conservador

**Precondición:** un artefacto sin metadata ni evidencia suficiente para decidir.
**Mecanismo:** `wf-prd-sync-impact` → `sdd-spec-auditor`.

1. Le pides el impacto con algún artefacto sin metadata de procedencia.
   → **Esperado:** lo marca `unknown` (revisión manual), **nunca** `in_sync` por
     optimismo.

**Resultado:** PASS si marca `unknown` lo que no puede demostrar · FALLO si asume
sincronía sin poder demostrarla.
**Desviación → reportar:** issue citando `CU-7.e`.

---

## `wf-prd-change-cascade` — propagar el cambio por el pipeline

> **Mecanismo común:** skill `wf-prd-change-cascade` → **sin agente** (orquestador
> puro, `context: fork`). Invoca en orden `wf-prd-change` → `wf-prd-sync-impact` →
> `wf-spec-sync-from-prd analyze/apply` → `wf-spec-conflict` + `wf-spec-readiness` →
> `wf-design-sync` → reporte plan/tasks. Output: `<basename>_cascade_report.md`.
> Flags: `--review-before-apply`, `--dry-run`, `--features`, `--skip-design`.

### CU-7.f — Cascada normal (auto + paradas reales)

**Precondición:** un cambio de producto real para propagar.
**Mecanismo:** `wf-prd-change-cascade`.

1. Le pides propagar el cambio por todo el pipeline en un comando.
   → **Esperado:** corre lo mecánico read-only, **auto-aplica** los deltas inequívocos
     (`severidad: minor` + `acción: delta`), y se detiene solo en los 4 checkpoints
     humanos (aprobación del cambio, features no triviales, decisiones de Design,
     revalidación de plan). Produce `<basename>_cascade_report.md` distinguiendo
     ejecutado / parado / omitido.

**Resultado:** PASS si auto-aplica solo lo inequívoco y para en los checkpoints reales
· FALLO si aplica cambios `major` solos, o no para en un checkpoint real.
**Desviación → reportar:** issue citando `CU-7.f`.

### CU-7.g — La cascada con un cambio que es solo aclaración

**Precondición:** `wf-prd-change` clasifica el `--new-reqs` como `CLARIFICATION`.
**Mecanismo:** `wf-prd-change-cascade`.

1. Le pides la cascada con un cambio que resulta ser una aclaración.
   → **Esperado:** **detiene** el cascade (no hay producto que propagar); recomienda
     `wf-spec-gap-resolve` / `wf-spec-delta`.

**Resultado:** PASS si se detiene · FALLO si propaga sync sobre una aclaración.
**Desviación → reportar:** issue citando `CU-7.g`.

### CU-7.h — Cascada sin un cambio que propagar

**Precondición:** no pasas `--new-reqs` y no existe `product-changelog.md` ni `changes/`.
**Mecanismo:** `wf-prd-change-cascade`.

1. Le pides la cascada sin haber gestionado ningún cambio antes.
   → **Esperado:** **se detiene**: no hay cambio gestionado; pide arrancar con
     `--new-reqs` o `wf-prd-change` primero.

**Resultado:** PASS si se detiene · FALLO si ejecuta la cascada sin un cambio que
propagar.
**Desviación → reportar:** issue citando `CU-7.h`.

### CU-7.i — Features no triviales en el conjunto STOP

**Precondición:** alguna feature sale `major` / `manual_review` / `rediscover`.
**Mecanismo:** `wf-prd-change-cascade`.

1. Lanzas una cascada donde algunas features cambian de forma no trivial.
   → **Esperado:** esas features se **presentan al usuario** (recomendando
     `wf-spec-delta` / revisión / `wf-spec-discover`) y **no se aplican**, pero el
     cascade **no aborta**: sigue aplicando el conjunto AUTO-APPLY.

**Resultado:** PASS si presenta las no triviales sin aplicarlas y continúa con el
resto · FALLO si las aplica solas, o aborta todo el cascade por ellas.
**Desviación → reportar:** issue citando `CU-7.i`.

### CU-7.j — `--dry-run` / `--review-before-apply` no escriben

**Precondición:** pasas uno de los dos flags.
**Mecanismo:** `wf-prd-change-cascade` (flags conservadores).

1. Lanzas la cascada con `--dry-run` (o con `--review-before-apply`).
   → **Esperado:** **no escribe nada**: `--dry-run` solo diagnostica;
     `--review-before-apply` para antes de aplicar incluso los `minor` e informa el
     comando manual.

**Resultado:** PASS si no aplica ningún delta · FALLO si aplica algo con cualquiera de
los dos flags.
**Desviación → reportar:** issue citando `CU-7.j`.

### CU-7.k — Profundidad adaptativa y degradación con gracia

**Precondición:** falta la fase Design (sin `DESIGN.md`), o un sub-workflow no está
instalado o falla.
**Mecanismo:** `wf-prd-change-cascade`.

1. Lanzas la cascada en un proyecto sin Design (o con un sub-workflow caído).
   → **Esperado:** omite Design si no aplica; un sub-workflow ausente/fallido se
     registra como `no disponible` y el cascade **continúa** con las fases
     independientes (salvo prerequisito duro). Todo queda reflejado en el reporte.

**Resultado:** PASS si degrada con gracia y lo refleja · FALLO si aborta por una fase
opcional ausente, o silencia la omisión.
**Desviación → reportar:** issue citando `CU-7.k`.

---

## `wf-spec-sync-from-prd` — resincronizar specs tras el cambio (paso a paso)

> **Mecanismo común:** skill `wf-spec-sync-from-prd` → subagente **`sdd-spec-writer`**.
> Es el eslabón spec-side que el cascade (CU-7.f) orquesta, también invocable suelto.
> Modo `analyze <prd.md>` produce `<basename>_sync_report.md`; `apply <prd.md>
> --features F-…` integra vía delta sobre los specs afectados.

### CU-7.l — Analizar y aplicar la resincronización de specs

**Precondición:** un PRD cambiado (CU-7.b) con specs de feature derivados.
**Mecanismo:** `wf-spec-sync-from-prd` → `sdd-spec-writer`.

1. Le pides analizar qué specs hay que resincronizar con el PRD nuevo.
   → **Esperado:** `analyze` identifica las features afectadas y genera por feature los
     **requisitos de sincronización** (en `<basename>_sync_report.md`), sin tocar los
     specs todavía.
2. Le pides aplicar la resincronización a un subset (`--features F-001,F-002`).
   → **Esperado:** `apply` integra esos cambios **vía delta** sobre los specs afectados
     y actualiza su trazabilidad (incluido el sello PRD→spec), solo en las features
     indicadas.

**Resultado:** PASS si analyze diagnostica por feature y apply integra vía delta solo
el subset · FALLO si apply toca features fuera del subset, o resincroniza sin
diagnóstico previo.
**Desviación → reportar:** issue citando `CU-7.l`.

### CU-7.m — Resincronización que rebasa un delta razonable

**Precondición:** un PRD cambiado donde una feature afectada tiene un cambio **estructural** (rebasa
lo que un delta quirúrgico puede integrar).
**Mecanismo:** `wf-spec-sync-from-prd` → `sdd-spec-writer` (analyze clasifica severidad por feature;
apply Paso 4B detiene la feature que rebasa delta).

1. Le pides analizar la resincronización.
   → **Esperado:** clasifica por feature `severidad: minor|major|structural` y
     `acción: delta|manual_review|rediscover`; las `structural`/`rediscover` no se marcan como auto-aplicables.
2. Le pides aplicar (`apply`) una feature cuyo cambio es estructural.
   → **Esperado:** **no fuerza un delta**: detiene esa feature y marca que necesita rediscovery o
     rediseño de spec; no aplica un sync automático que falsee la trazabilidad.

**Resultado:** PASS si clasifica por severidad y detiene las features que rebasan delta · FALLO si
fuerza un delta sobre un cambio estructural, o auto-aplica un rediscover.
**Desviación → reportar:** issue citando `CU-7.m`.
