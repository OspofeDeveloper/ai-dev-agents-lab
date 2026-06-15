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
| C1 | **Resolución de ruta / layout** (dónde escribir y leer artefactos) | Alto — artefacto en directorio equivocado; gates/índice fallan o se dispersa el estado | Sí (función pura de path+kind+root) | **MIGRAR** → `sdd-resolve-path.py` |
| C2 | **Headers de trazabilidad** (escribir `Spec origen`/`Plan origen` relativo correcto) | Alto — header irresoluble → no se puede sellar | Parcial: la **verificación** ya existe (`sdd-seal.py`); falta el **cómputo en escritura** | **MIGRAR (write-side)** — se pliega en C1 |
| C3c | **Numeración B-00X** (bugs) | Alto — colisión de IDs en `_bugs.md` | Sí (scan + max+1) | **MIGRAR** → `sdd-next-id.py` |
| C3d | **Numeración TC-XXX** (casos QA) | Alto — colisión en `_qa_plan.md` | Sí | **MIGRAR** → `sdd-next-id.py` |
| C3a | **Feature ID F-001 directo** (fast-track sin discovery) | Medio — colisión en `_features.md` (el modo `--feature` lo toma del discovery, sin riesgo) | Sí | **MIGRAR** → `sdd-next-id.py` (mismo script) |
| C4 | **Detección de artefacto preexistente en ambos layouts** | Alto — no lo encuentra → lo regenera/pisa | Sí (mismo grafo de rutas que C1) | **MIGRAR** — modo `--find` de `sdd-resolve-path.py` |
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

### 11.2a — `sdd-resolve-path.py` (FLAGSHIP) 🟠

**Problema.** La regla de resolución de ubicación de artefactos es **una frase
canónica repetida en ~20 SKILL.md**: 14 archivos con la variante "el directorio
que contiene `features/`" y ~22 con "layout plano / subcarpeta de fase". Cada
copia es una oportunidad de divergencia y un punto donde el modelo puede escribir
en el sitio equivocado. Subsume C2 (write-side: emitir el `Spec origen` relativo
correcto) y C4 (encontrar un artefacto existente en ambos layouts).

**Diseño propuesto.** Script puro que, dado el artefacto de entrada (p. ej. el
spec), el tipo de salida (`spec|design|plan|tasks|brief|features-index|...`) y la
raíz del proyecto (con `artifacts.*` de `project-init.json` si existe), devuelve:
- `--write`: el directorio/ruta canónica donde escribir (subcarpeta de fase para
  features nuevas; plano para features legacy; raíz del producto para artefactos
  de producto; checkout del SSoT para repos consumidores).
- `--find <basename>`: la ruta del artefacto existente buscando en ambos layouts,
  o vacío si no existe (cierra C4).
- `--rel-from <A> <B>`: la ruta relativa correcta de B desde A (cierra C2
  write-side: el `Spec origen` que hoy el modelo computa a mano).

**Evidencia (representativa).** `plan/skills/wf-prepare-plan/SKILL.md` (resolución
de `_plan.md`, `Spec origen`, `_features.md`, `DESIGN.md`),
`tasks/skills/wf-prepare-tasks/SKILL.md`, `design/skills/wf-design-system|intake|
feature-prototype|sync|extract`, `spec/skills/wf-spec-fast-track|delta|readiness|
from-code|features-first`.

**Coste/riesgo.** ALTO en superficie (rewire de ~20 skills a invocar el script en
vez de recitar la frase) pero el script en sí es pequeño y muy testeable. Riesgo
de regresión gestionable con la suite 11.3 (añadir `test_sdd_resolve_path.py` +
verificar que el sellador sigue resolviendo `Spec origen`). Recomendado como
milestone propio.

### 11.2b — `sdd-next-id.py` 🟡

**Problema.** Tres numeraciones secuenciales se asignan hoy por prosa
("escanea el archivo, asigna el siguiente"): `B-00X` en `_bugs.md`
(`wf-bug/SKILL.md:90`), `TC-XXX` en `_qa_plan.md` (`kb-qa-expert/SKILL.md:17`),
`F-001` directo en fast-track (`wf-spec-fast-track/SKILL.md:139`). Colisión =
corrupción del registro / del índice de features.

**Diseño propuesto.** `sdd-next-id.py <prefijo> <archivo>` → escanea los IDs
existentes del prefijo en el archivo (regex `B-(\d+)`, `TC-(\d+)`, `F-(\d+)`),
devuelve el siguiente con el padding canónico. Escritura atómica si además
inserta (o solo emite el ID y el workflow lo escribe — decidir). Precedente
exacto: `sdd-amend.py next-ref` ya hace esto para `E-00X`.

**Coste/riesgo.** BAJO — script pequeño, 3 call-sites, autocontenido. Buen primer
paso por sí solo.

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

De los 14 puntos inventariados: **3 ya estaban cubiertos** por scripts, **6 se
quedan en prosa** justificadamente (juicio/humano/bajo valor), y **5 merecen
migración**, que se consolidan en **2 scripts nuevos** — `sdd-resolve-path.py`
(absorbe C1+C2-write+C4, el grueso del riesgo de dispersión de estado) y
`sdd-next-id.py` (C3a/c/d, colisiones de ID). El flagship es `sdd-resolve-path.py`
por blast radius (~20 skills recitando la misma frase). Ambos son milestones
independientes; `sdd-next-id.py` es el de menor coste/riesgo para empezar.
