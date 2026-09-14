---
name: wf-spec-delta
description: "Evoluciona un Spec de feature de forma incremental. Modo 'analyze' genera un informe delta con HUs y CAs anadidos, modificados y eliminados; modo 'apply' integra los cambios validados en el spec."
when_to_use: "Activa en frases como 'quiero anadir funcionalidad al spec', 'actualiza el spec con estos requisitos nuevos', 'evoluciona el spec con este cambio', 'genera el delta del spec'. No activa para completar HUs [INCOMPLETO] desde un _analysis.md (usa wf-spec-gap-resolve)."
argument-hint: "analyze <spec.md> --new-reqs <desc.md> | apply <spec.md> <delta.md> [--allow-open-critical-gaps]"
effort: high
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# Workflow: DELTA

**Corres en el hilo principal.** Evolucionar un spec sostiene **tres decisiones que son del
usuario**, y ninguna es presentable desde un `context: fork` ([[D-002]]/[[D-045]]):

1. **¿Esto es un delta o es un cambio de producto?** La frontera es de juicio, y equivocarse hacia
   "es un delta" hornea en el spec un cambio de alcance que nadie formalizó en el PRD.
2. **Cuando el requisito nuevo admite varias lecturas, ¿cuál?** Es exactamente lo que [[D-040]]
   fijó para `wf-prd-change`: *sin humano, la ambigüedad **se marca**, no se decide*.
3. **¿Se aplica con gaps `[CRÍTICO]` sin responder?** Esa misma situación es un gate en
   `wf-spec-features-first`; aquí se continuaba en silencio marcando `[INCOMPLETO]`.

Tu rol es de **orquestador**: parseas argumentos, verificas precondiciones **mecánicamente**,
sostienes esos tres gates con `AskUserQuestion`, y **delegas** el análisis y la integración en
`sdd-spec-writer` con la tool `Agent` y **`run_in_background: false`** ([[D-043]]).

**No leas el spec, ni los requisitos, ni el delta analysis** ([[D-031]]): pasas **paths**, y quien
los lee es tu delegado, que tiene las `kb-*` para interpretarlos. **Y no escribes ningún artefacto**
([[D-060]]): los redacta y los escribe el agente, que es su autor. Vale **aunque las tools estuvieran
disponibles** ([[D-038]]).

**Regla de oro (la que gobierna al delegado):** el delta nunca reescribe la historia del spec — solo
la extiende. Los cambios son mínimos y quirúrgicos.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (`analyze` o `apply`)
- En modo `analyze`:
  - **Path del spec existente**: el argumento después del modo, hasta `--new-reqs`
  - **Path de nuevos requisitos**: el argumento después de `--new-reqs`
- En modo `apply`:
  - **Path del spec existente**: el segundo argumento
  - **Path del delta analysis**: el tercer argumento
  - **`--allow-open-critical-gaps`** (opcional): salta el gate del Paso 5. Solo llega armado porque
    el usuario lo eligió en un gate anterior ([[D-026]]); no te lo auto-suministres.

Si no hay argumento o el modo no es válido, informa al usuario:
> "Puedo hacer dos cosas: **analizar** el cambio sobre el spec (te digo qué HUs y CAs habría que añadir, modificar o eliminar, sin tocar nada), o **aplicar** un análisis de cambio que ya hayas revisado. Dime cuál, el spec, y dónde está la descripción del cambio."

Ejemplos:
- `analyze features/auth/spec/auth_spec.md --new-reqs new_requirements.md`
- `apply features/auth/spec/auth_spec.md features/auth/spec/auth_delta_analysis.md`

Si el usuario intenta usar `resolve`, remítele a:
> "Para eso lo que toca es completar las historias incompletas del spec con las respuestas del análisis — pídemelo y lo hago."

---

## Paso 2: Verificar archivos (mecánico, sin leerlos)

```bash
!test -f "<path_spec>" && echo EXISTE || echo NO_EXISTE
```

**Modo `analyze`:**
1. El spec debe existir y terminar en `_spec.md`. Si no → informa: "El primer argumento debe ser un spec SDD (`_spec.md`). Si lo que quieres es un spec nuevo, pídemelo y lo analizamos desde el documento de origen."
2. El archivo de nuevos requisitos debe existir. Si no → informa con la ruta exacta y detén.

**Modo `apply`:**
1. El spec debe existir y terminar en `_spec.md`.
2. El delta analysis debe existir y terminar en `_delta_analysis.md`. Si no → informa: "El segundo argumento debe ser un delta analysis (`_delta_analysis.md`); pídeme que analice antes los cambios sobre el spec y te lo genero."

La valoración de si el contenido es utilizable **no la haces tú**: la hace tu delegado, que es quien
lo lee con las `kb-*` en contexto.

---

## Submodo ANALYZE

### Paso 3A: Delegar el análisis del delta

Delega con la tool `Agent` ([[D-043]]), `subagent_type: "sdd-spec-writer"` y
**`run_in_background: false`**:

```
Modo: spec-delta-analyze
Path del spec existente: <path>
Path de los nuevos requisitos: <path>
Plantilla del informe: ${CLAUDE_SKILL_DIR}/references/delta_analysis_template.md

INSTRUCCION:
1. Inventaria el spec existente (actores y capacidades, HUs con ID y titulo, CAs con su HU padre
   y su GIVEN/WHEN/THEN, Journeys, Instrucciones Inambiguas y la seccion Fuera de Alcance). El
   inventario es trabajo interno: no va al informe.
2. Analiza los nuevos requisitos contra ese inventario, consultando `kb-spec-expert` para pureza
   funcional, e identifica:
   - **HUs ANADIDAS**: mismo actor (o actor nuevo) con objetivo funcional no cubierto por ninguna HU existente.
   - **HUs MODIFICADAS**: funcionalidad existente cuyo comportamiento, actor o valor cambia. Cita la HU original.
   - **HUs ELIMINADAS**: las que los nuevos requisitos eliminan o reemplazan explicitamente. Cita cual.
   - **CAs AFECTADOS**: por cada HU anadida o modificada, los CAs nuevos o los cambios a los existentes.
   - **Reglas de comportamiento**: nuevas, modificadas y las que quedan obsoletas.
   - **Impacto en Fuera de Alcance**: lo que entra o sale del alcance.
3. **Prueba de Pureza** (`kb-spec-expert`): si un requisito trae tecnologia (frameworks, APIs,
   patrones de implementacion), propon la reescritura funcional equivalente.
4. **Gaps** (`kb-gap-conventions`): IDs `[D-XXX]` (prefijo D = Delta), severidades y marcador
   `_(pendiente)_`.
5. **Clasifica el cambio y dilo en tu informe, con una linea por veredicto**:
   - `DELTA_PURO` — evoluciona la feature sin tocar el producto comprometido.
   - `POSIBLE_CAMBIO_DE_PRODUCTO` — redefine el alcance del MVP, una exclusion del PRD o una regla
     transversal. **No decidas tu**: nombra QUE lo redefine y devuelvelo.
   - `AMBIGUO` — el requisito admite **mas de una lectura funcional**. Enumera las lecturas, cada
     una con lo que implicaria en HUs y CAs. **No elijas**: elegir por el usuario es fabricar
     alcance ([[D-039]]/[[D-063]]).
6. **Escribe tu el informe** en `<mismo directorio que el spec>/<basename>_delta_analysis.md`
   (ej.: `features/auth/spec/auth_spec.md` → `features/auth/spec/auth_delta_analysis.md`) e informa
   del path: eres su autor ([[D-059]]/[[D-060]]). No toques el spec: `analyze` no escribe specs.
```

### Paso 4A: Los dos gates de clasificación (aquí, con `AskUserQuestion`)

Según el veredicto que devuelva el agente:

- **`DELTA_PURO`** → sigue al Paso 5A sin preguntar nada. El consentimiento ya está en la petición.
- **`POSIBLE_CAMBIO_DE_PRODUCTO`** → **presenta la elección**, con lo que el agente identificó como
  redefinido delante:
  - **Formalizar el cambio en el PRD primero (recomendado)** → para aquí y remite a la gobernanza de
    cambio de producto. El delta se retoma después, contra el PRD ya actualizado.
  - **Tratarlo como delta de esta feature** → continúa, y el informe queda con el aviso de
    gobernanza puesto por el agente. Es una decisión del usuario, y queda registrada como tal.
- **`AMBIGUO`** → presenta las lecturas que devolvió el agente, **una opción por lectura**, más la
  salida honesta:
  - Cada lectura, con lo que implica en HUs y CAs.
  - **"No lo decido ahora"** → la ambigüedad **se marca**, no se resuelve: vuelve a delegar pidiendo
    que registre un gap `[D-XXX]` `[CRÍTICO]` con las lecturas como opciones y `_(pendiente)_` como
    respuesta. Eso es la segunda mitad de [[D-040]] aplicada aquí: **sin humano, se marca**.

### Paso 5A: Informar

Path del delta generado, impacto (HUs añadidas/modificadas/eliminadas, CAs afectados), nº de gaps
`[CRÍTICO]` e `[INFORMATIVO]` pendientes y el veredicto de clasificación. Siguiente paso, en lenguaje
natural: responder los gaps críticos en el informe y pedirte que **apliques el delta al spec**.

---

## Submodo APPLY

### Paso 3B: Gaps críticos sin responder — el gate que faltaba

El recuento **sale del script, no de tu lectura** ([[D-042]]):

```bash
!python3 .sdd/scripts/sdd-analysis-gaps.py "<path_delta_analysis>" --check --json
```

- **0 críticos pendientes** → continúa.
- **≥1 crítico pendiente** y **sin** `--allow-open-critical-gaps` → **presenta la elección** con
  `AskUserQuestion`, nombrando cuántos son y qué HUs quedarían `[INCOMPLETO]`:
  - **Responderlos primero (recomendado)** → para aquí. Se responden en el `_delta_analysis.md` y se
    vuelve a pedir el apply.
  - **Aplicar igualmente** → continúa; las HUs afectadas se marcan `[INCOMPLETO]` y **bloquearán el
    plan** hasta resolverse.
- **Con `--allow-open-critical-gaps`** → continúa sin preguntar: el usuario ya eligió ([[D-026]]).

> **Por qué esto es un gate y antes no lo era.** Aplicar con críticos abiertos no es un detalle de
> forma: mete en el spec HUs incompletas que bloquean `wf-prepare-plan` más adelante, lejos de aquí.
> La misma situación **ya se presentaba** en `wf-spec-features-first`; este workflow la resolvía
> informando y continuando, que es decidir por el usuario sin decírselo.

### Paso 4B: Delegar la integración

Delega con la tool `Agent`, `subagent_type: "sdd-spec-writer"` y **`run_in_background: false`**:

```
Modo: spec-delta-apply
Path del spec: <path>
Path del delta analysis: <path>
Reglas de integracion: ${CLAUDE_SKILL_DIR}/references/spec_delta_integration_rules.md
Plantilla de changelog: ${CLAUDE_SKILL_DIR}/references/changelog_template.md
Gaps criticos sin responder: <n> (el usuario eligio aplicar igualmente | no habia ninguno)

INSTRUCCION:
1. Integra los cambios siguiendo las reglas de integracion (no interpretar, no ampliar, no inferir;
   reglas por tipo: HUs anadidas/modificadas/eliminadas, CAs, Journeys, Instrucciones Inambiguas,
   Fuera de Alcance). Las HUs afectadas por un gap `[CRITICO]` sin responder se marcan `[INCOMPLETO]`.
2. **Al modificar un spec, su validacion se reabre** ([[D-061]]). Tras escribir:
   `python3 .sdd/scripts/sdd-seal.py spec "<path_del_spec>" --unseal`
   Degradar a `BORRADOR` siempre es seguro y siempre es correcto: lo que se valido ya no es lo que
   hay. Misma norma que en el PRD, donde un cambio reabre el sello ([[D-028]]).
3. Incrementa la version en el header del spec (1.0 → 1.1, 1.2 → 1.3, 2.0 → 2.1) y anade o actualiza
   `## Changelog` al final (orden cronologico inverso) con la plantilla. Si aplicaste asunciones
   `[INFORMATIVO]`, anade ademas `## Asunciones Aplicadas (v[X.Y])` antes del Changelog.
4. **Regenera `_features.md` si existe.** Es un indice **generado**: no se edita a mano y ningun
   workflow lo compone escribiendo texto (por que y quien regenera que: `kb-decompose-expert`,
   "Reparto de SSoT", [[D-069]]). Desde la raiz del proyecto (el directorio que contiene `.sdd/`):
   `python3 .sdd/scripts/sdd-features-index.py <raiz_spec>`
   `<raiz_spec>` es el directorio que contiene `features/` y `_features.md` (si el spec esta en
   `features/<nombre>/` —directamente o en `spec/`— es el que contiene `features/`; en otro caso, el
   del propio spec). Si no existe `_features.md` ni discovery, o falta el script, omitelo en silencio:
   el delta del spec ya esta aplicado.
5. **Prueba de Pureza sobre el spec resultante** (`kb-spec-expert`): si queda contaminacion tecnica,
   senalala en tu informe.
6. **Auto-verifica el checklist**: el spec resultante sigue teniendo los 8 elementos SDD. El que
   haya quedado incompleto se marca `[ ]` en el checklist del spec.
7. Informa del path, la version nueva y el resumen de cambios (HUs/CAs).
```

### Paso 5B: Comprobar el resultado

```bash
!grep -m1 -E '^\s*>?\s*\**Version\**\s*:?' "<path_spec>"
!python3 .sdd/scripts/sdd-seal.py spec "<path_spec>" --check
```

Si la versión no subió o el spec sigue sellado como `VALIDADO`, **no lo arregles tú** ([[D-060]]):
reporta que la integración no dejó el spec en el estado que dice y para. Que el informe del delegado
diga que lo hizo no es que esté hecho ([[D-047]]).

---

## Paso 6B: Conflictos tras el apply (informativo, no bloqueante)

**Ni tú ni tu delegado chequeáis los conflictos, y menos aún firmáis el informe ([[D-067]]).** El
spec lo acaba de escribir `sdd-spec-writer`: auditarlo él rompe autor≠verificador, y el
`_conflict_report.md` **lo escribe el auditor que lo produce**, nunca otro ([[D-059]]).

Comprueba si hay índice de features:

```bash
!ls "<raíz_spec>"/*_features.md 2>/dev/null | head -1
```

- **Si existe** → dilo al informar: *"este spec ha cambiado; conviene revisar si choca con el resto
  antes de planificar"*. Nombra el spec y para ahí — la revisión de conflictos se pide aparte, y la
  hace un auditor.
- **Si no existe** → omite este paso.

---

## Paso 7: Informar al usuario

**Tras `analyze`:** lo del Paso 5A.

**Tras `apply`:** path del spec actualizado, nueva versión, resumen de cambios (HUs/CAs), y si
quedaron HUs `[INCOMPLETO]` por gaps críticos que el usuario decidió no responder. Si se regeneró
`_features.md`: "✓ Trazabilidad actualizada". Siguiente paso, en lenguaje natural: **validar el spec
actualizado** — su validación se reabrió al modificarlo.
