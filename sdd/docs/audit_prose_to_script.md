# Auditoría: prosa sustituible por scripts deterministas (ROADMAP 11.2)

**Fecha:** 2026-06-15 · **Rama:** develop

## Objetivo y criterio

El patrón sellador/gates/task-state (autor ≠ verificador mecánico) demostró que
la prosa "verifica/computa X" es el punto débil del sistema. Esta auditoría
inventaría **todos** los puntos del flujo que hoy dependen de que el modelo
obedezca prosa para verificar o computar algo determinista, y decide cuáles
migrar a script.

**Criterio de corte (del ROADMAP 11.2):**
> Si el fallo de la prosa **corrompe estado o trazabilidad** → script.
> Si solo **degrada la calidad del texto** → prosa.

Se añade un segundo filtro de **mecanizabilidad**: un punto solo migra si su
cómputo es genuinamente determinista. Lo que exige juicio semántico o
confirmación humana se queda en prosa aunque su fallo sea grave (un script que
"adivina" daría falsa sensación de rigor).

Metodología: barrido de `*/SKILL.md`, `references/*.md` y `*/agents/*.md` de
todas las fases (excluido `.claude/`, `docs/`, `tests/`), verificado con grep
sobre el árbol fuente.

---

## Veredicto por categoría

| # | Punto prosa-dependiente | Riesgo si falla | Mecanizable | Veredicto |
|---|---|---|---|---|
| C1 | **Resolución de ruta / layout** (dónde escribir y leer artefactos) | Alto — artefacto en directorio equivocado; gates/índice fallan o se dispersa el estado | Sí (función pura de path+kind+root) | **✅ HECHO** → `sdd-resolve-path.py` (modo `write`) |
| C2 | **Headers de trazabilidad** (escribir `Spec origen`/`Plan origen` relativo correcto) | Alto — header irresoluble → no se puede sellar | Parcial: la **verificación** ya existe (`sdd-seal.py`); falta el **cómputo en escritura** | **✅ HECHO (write-side)** → `sdd-resolve-path.py` (modo `rel-from`) |
| C3c | **Numeración B-00X** (bugs) | Alto — colisión de IDs en `_bugs.md` | Sí (scan + max+1) | **MIGRAR** → `sdd-next-id.py` |
| C3d | **Numeración TC-XXX** (casos QA) | Bajo — la matriz se enumera `TC-001..N` en UNA pasada de derivación (no append incremental); al regenerar reinicia | N/A para `next-id` (devuelve *un* siguiente ID, no encaja con generación batch) | **PROSA** — reclasificado al implementar 11.2b (ver nota) |
| C3a | **Feature ID F-001 directo** (fast-track sin discovery) | Medio — colisión en `_features.md` (el modo `--feature` lo toma del discovery, sin riesgo) | Sí | **MIGRAR** → `sdd-next-id.py` (mismo script) |
| C4 | **Detección de artefacto preexistente en ambos layouts** | Alto — no lo encuentra → lo regenera/pisa | Sí (mismo grafo de rutas que C1) | **✅ HECHO** → `sdd-resolve-path.py` (modo `find`) |
| C3b | **Numeración E-00X** (enmiendas) | Alto | — | **YA HECHO** — `sdd-amend.py` único escritor; la prosa ya prohíbe asignar a mano |
| C6 | **Citas `Regla N de kb-X`** desactualizadas | Medio — lógica obsoleta | — | **YA HECHO** — `sdd-structural-lint.py` (CITED-RULE-MISSING, 11.4) |
| C2v | **Verificación** de headers ya escritos | Alto | — | **YA HECHO** — `sdd-seal.py` (header legible + CAs) y `sdd-sync-check.py` (hash PRD) |
| C5e | **Ownership de shared models** (empate) | Alto — modelo en feature equivocada | No — 4 criterios + confirmación humana en empate | **PROSA** (juicio + gate humano) |
| C5f | **Gate de gobernanza** (detectar cambio de producto en respuestas de analysis) | Alto — scope creep silencioso | No — juicio semántico vs `kb-product-change-governance` | **PROSA** |
| C5a | **Detección de layout en `wf-project-init`** (carpetas candidatas) | Alto — mapping `artifacts.*` erróneo | No del todo — interactivo, one-time, confirmado por humano | **PROSA** |
| C5d | **Guards de presencia de sección / tipo de artefacto** ("sin `## Accessibility` detente"; "parece un Plan") | Medio — el gate lo rechaza después igual | Parcial, bajo valor | **PROSA** |
| C5c | **Formato/presencia de campos de header** (más allá de los críticos) | Medio — los críticos ya los verifica el sellador | Parcial, bajo valor | **PROSA** |
| C3e | **Numeración TD-00X** (deuda técnica) | Bajo — dentro de un plan, revisado por humano | Sí pero baja frecuencia | **PROSA** (no compensa) |

---

## Migraciones recomendadas (sub-ítems de 11.2)

### 11.2a — `sdd-resolve-path.py` (FLAGSHIP) ✅ HECHO (2026-06-15, v0.31.0)

**Problema.** La regla de resolución de ubicación de artefactos era **una frase
canónica repetida en ~20 SKILL.md**: 14 archivos con la variante "el directorio
que contiene `features/`" y ~22 con "layout plano / subcarpeta de fase". Cada
copia es una oportunidad de divergencia y un punto donde el modelo puede escribir
en el sitio equivocado. Subsume C2 (write-side: emitir el `Spec origen` relativo
correcto) y C4 (encontrar un artefacto existente en ambos layouts).

**Diseño implementado.** Script puro (no escribe, solo emite rutas) con tres modos:
- `write <kind> <input> [--local-root <dir>]`: la ruta canónica donde escribir,
  respetando el layout del input (subcarpeta de fase vs plano legacy); con
  `--local-root` redirige los artefactos locales (plan/tasks) al repo consumidor.
- `find <kind> <input>`: la ruta del artefacto existente buscando en AMBOS
  layouts (o en la raíz de producto para kinds de producto), o vacío + exit 3
  (cierra C4).
- `rel-from <anchor> <target>`: la ruta relativa a escribir DENTRO de anchor para
  apuntar a target (cierra C2 write-side: el `Spec origen` sin `../` a mano).

Kinds de feature: spec/plan/tasks/qa-plan/qa-report/release/bugs/flows/views/
ui-prompt/design-discovery. Kinds de producto: discovery/features-index/readiness/
analysis/design-doc/design-brief.

**Límite de alcance deliberado.** El script es una función pura de **layout**: NO
lee `artifacts.*` ni `artifacts_source` de `project-init.json`. Esos casos (raíz
de artefactos declarada por el init, DESIGN.md bajo `artifacts.design`) quedan en
la **prosa-fallback** de cada skill, que se conserva íntegra como degradación.

**Call-sites cableados** (resolutor primario + prosa degradada a fallback): los de
escritura/búsqueda que corrompen estado o trazabilidad —
`plan/skills/wf-prepare-plan` (path del `_plan.md`, `Spec origen` vía `rel-from`,
`find` de `_features.md`/`DESIGN.md`/`flows`/`views`),
`tasks/skills/wf-prepare-tasks` (path del `_tasks.md`),
`spec/skills/wf-spec-fast-track` (existencia del spec en ambos layouts),
`design/skills/wf-design-feature-prototype` (los 3 paths flows/views/ui_prompt).
Las menciones puramente descriptivas del layout en otras skills (explicación, no
cómputo de ruta) se dejan en prosa: no corrompen.

**Estado.** Distribuido por `install.sh` a `.sdd/scripts/`; `test_sdd_resolve_path.py`
(23 tests) en la suite 11.3 (un bug real cazado: `product_root` resolvía un nivel
de más). Baseline del linter intacto (0 blocking). CHANGELOG 0.31.0 sin ⚠.

### 11.2b — `sdd-next-id.py` ✅ HECHO (2026-06-15, v0.30.0)

**Problema.** Numeraciones secuenciales asignadas por prosa ("escanea el
archivo, asigna el siguiente"). Colisión = corrupción del registro / del índice.

**Diseño implementado.** `sdd-next-id.py <prefijo> <archivo...> [--width N]` →
escanea los IDs del prefijo (regex `(?<![A-Za-z0-9])<prefijo>-(\d+)`), devuelve
el siguiente con padding (default 3). **Solo emite** el ID (no escribe — el
workflow escribe la entrada), pseudo-función pura como `sdd-amend.py next-ref`.
Lookbehind desambigua prefijos: `F` no matchea `RF-001` ni `F-C-003`, `R` no
matchea `CR-001`; `F` y `F-C` son secuencias independientes.

**Decisión refinada al implementar — solo 2 de los 3 call-sites migran.**
- ✅ `B-00X` (`wf-bug`) y `F-NNN` (`wf-spec-fast-track`): **append incremental**
  a `_bugs.md`/`_features.md` en el tiempo → riesgo real de miscount. Migrados,
  con fallback a contar a mano si no hay python3/script.
- ❌ `TC-XXX` (`kb-qa-expert`): la matriz se **enumera `TC-001..N` en una sola
  pasada de derivación** (no append). `next-id` devuelve *un* siguiente ID y no
  encaja con generación batch; el riesgo de colisión es bajo. **Se queda en
  prosa**, con la KB aclarada (enumeración batch, reinicia al regenerar).

**Estado.** Distribuido por `install.sh` a `.sdd/scripts/`; `test_sdd_next_id.py`
(10 tests) en la suite 11.3; CHANGELOG 0.30.0 (sin ⚠, aditivo).

### NO migrar (se quedan en prosa, justificado)

C5e (ownership de empate), C5f (gobernanza de scope creep), C5a (detección de
layout interactiva), C5d/C5c (guards de presencia, bajo valor), C3e (TD-00X).
Razón común: exigen juicio semántico o confirmación humana, o su fallo lo atrapa
un gate posterior — un script daría falso rigor sin reducir corrupción real.

### Ya cubierto (sin acción)

E-00X (`sdd-amend.py`), citas de regla (`sdd-structural-lint.py`), verificación de
headers y deriva PRD (`sdd-seal.py` / `sdd-sync-check.py`), consolidación de
`_features.md` (`sdd-features-index.py`, cerrado en 5.4).

---

## Resumen ejecutivo

De los 14 puntos inventariados: **3 ya estaban cubiertos** por scripts, **7 se
quedan en prosa** justificadamente (juicio/humano/bajo valor; TC-XXX se sumó a
este grupo al implementar 11.2b — es enumeración batch, no append), y **2 grupos
merecen migración** en 2 scripts:

- **`sdd-next-id.py` (11.2b) — ✅ HECHO** (v0.30.0): C3a (F-NNN) + C3c (B-00X),
  los call-sites de append incremental. Bajo coste, 2 call-sites cableados.
- **`sdd-resolve-path.py` (11.2a) — ✅ HECHO** (v0.31.0): absorbe C1 (dónde
  escribir) + C2-write (emitir `Spec origen` relativo) + C4 (find en ambos
  layouts). El flagship por blast radius; cableado en los 4 call-sites de
  escritura/búsqueda que corrompen estado (plan/tasks/fast-track/feature-prototype)
  con la prosa anterior conservada como fallback. Función pura de layout (no lee
  `project-init.json`: esos casos siguen en la prosa-fallback).

**Inventario 11.2 cerrado**: auditoría + las 2 migraciones completadas.
