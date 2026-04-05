---
name: wf-spec-readiness
description: Analiza los artefactos post-spec-generation (specs de feature, READMEs, _features.md, _conflict_report.md opcional) y genera un informe de readiness que indica qué features están listas para plan, cuáles están bloqueadas y por qué, y el orden de implementación recomendado. Activa en frases como "qué features están listas", "readiness de las features", "cuáles puedo planificar", "orden de implementación", "verifica readiness", "qué falta para planificar".
argument-hint: "<path/features/>"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-analyst
---

# Workflow: READINESS

Tu objetivo es sintetizar el estado de los artefactos post-spec-generation en un informe accionable que le diga al usuario exactamente qué features puede pasar a `/wf-prepare-plan` y en qué orden. No generas ni modificas ningún artefacto existente — solo lees y sintetizas. Usa `kb-gap-conventions` para interpretar marcadores `[INCOMPLETO]` y severidades, y `kb-conflict-expert` para interpretar severidades de conflictos.

**Regla de oro:** Este informe es una fotografía del estado actual. No propone resoluciones — indica qué falta y dónde encontrarlo.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Directorio de features**: el primer argumento. Debe ser el directorio que contiene las carpetas de features (ej: `docs/features/`).

Si no hay argumento, intenta inferir buscando un directorio `features/` en el directorio actual.

Si no hay argumento y no se puede inferir, informa al usuario:
> "Uso: `/wf-spec-readiness <path/features/>`"
> "Ejemplo: `/wf-spec-readiness docs/features/`"

---

## Paso 2: Localizar artefactos

1. Busca `*_features.md` en el directorio padre del directorio de features (ej: si features/ está en `docs/features/`, busca `docs/*_features.md`).
2. Busca todos los `*_spec.md` dentro de `<features-dir>/*/<nombre>_spec.md` (un nivel de profundidad).
3. Busca todos los `README.md` dentro de `<features-dir>/*/README.md`.
4. Busca `*_conflict_report.md` en el directorio padre del directorio de features (opcional — puede no existir).

Valida:
- Si no hay `_features.md` → detén: "No se encontró `_features.md` en `<directorio_padre>`. Ejecuta `/wf-spec-features-first` o `/wf-spec-fast-track` primero."
- Si no hay specs → detén: "No se encontraron specs de feature en `<features-dir>`. Ejecuta `/wf-spec-features-first` o `/wf-spec-fast-track` primero."
- Si falta algún README → advertencia no bloqueante: "Falta README.md en `<feature>/`. Las dependencias de esta feature se inferirán solo del `_features.md`."
- Si no hay `_conflict_report.md` → advertencia no bloqueante: "No se encontró `_conflict_report.md`. Ejecuta `/wf-spec-conflict` para un análisis de conflictos completo. Continuando sin análisis de conflictos."

---

## Paso 3: Leer todos los artefactos

Lee el contenido completo de:
- `_features.md`
- Cada `*_spec.md` de feature
- Cada `README.md` de feature (los que existan)
- `_conflict_report.md` (si existe)

---

## Paso 4: Inventariar estado de cada feature

Para cada feature, extrae:

### 4a — Identificación

Del `_features.md`, extrae para cada feature:
- Feature ID (F-001, F-002, etc.)
- Nombre de la feature
- Ruta al spec

### 4b — Gaps (marcadores [INCOMPLETO])

Busca la cadena literal `[INCOMPLETO]` en el spec de la feature. Para cada HU marcada:
- ID de la HU (ej: HU-003)
- Gaps que la bloquean (referenciados en la línea que contiene `Pendiente de gap(s):` o `[P-XXX]` cercanos al marcador)

Clasifica la feature como **BLOQUEADA_POR_GAPS** si tiene al menos una HU `[INCOMPLETO]`.

### 4c — Conflictos no resueltos

Si existe `_conflict_report.md`:
- Busca todos los conflictos de severidad **ALTA** que involucren esta feature.
- Un conflicto se considera no resuelto si aparece en el informe (el informe refleja el estado en el momento de su generación; si se resolvió, el usuario debió re-ejecutar `/wf-spec-conflict`).

Clasifica la feature como **BLOQUEADA_POR_CONFLICTOS** si tiene al menos un conflicto ALTA asociado.

### 4d — Dependencias

Del README de la feature, extrae la sección `## Dependencias`:
- **Requiere**: lista de features que deben implementarse antes
- **Bloquea**: lista de features que dependen de esta

Complementa con el `_features.md`: si una feature referencia un shared model cuyo owner es otra feature, la feature referenciadora depende de la feature owner (a menos que ya esté en la lista de Requiere).

Construye la lista unificada de dependencias para cada feature.

---

## Paso 5: Construir el grafo de dependencias

1. Crea un grafo dirigido donde cada nodo es una feature y cada arista va de la dependencia hacia la feature que la requiere.
2. Detecta ciclos. Si hay un ciclo → repórtalo en la sección correspondiente del informe pero no detengas la ejecución. Excluye las features del ciclo del topological sort.
3. Realiza un **topological sort** agrupando en fases (waves) las features que pueden ejecutarse en paralelo:
   - **Fase 1**: features sin dependencias entrantes (nodos raíz)
   - **Fase 2**: features cuyas dependencias están todas en Fase 1
   - **Fase N**: features cuyas dependencias están todas en fases anteriores

---

## Paso 6: Determinar readiness de cada feature

Para cada feature, asigna un estado:

| Estado | Condición |
|--------|-----------|
| `LISTA` | Sin `[INCOMPLETO]`, sin conflictos ALTA, todas las dependencias también LISTA o sin dependencias |
| `LISTA_PARA_PLAN` | Sin `[INCOMPLETO]`, sin conflictos ALTA, pero alguna dependencia no está LISTA (la feature en sí puede planificarse, pero su implementación debe esperar) |
| `BLOQUEADA_POR_GAPS` | Tiene HUs `[INCOMPLETO]` |
| `BLOQUEADA_POR_CONFLICTOS` | Involucrada en conflicto(s) ALTA no resueltos |
| `ESPERANDO_DEPENDENCIAS` | Sin gaps ni conflictos propios, pero alguna dependencia tiene gaps o conflictos que impiden planificar |

Una feature puede tener múltiples bloqueos simultáneos. En ese caso, listar todos los motivos. La prioridad de display es: GAPS > CONFLICTOS > DEPENDENCIAS.

**Nota importante sobre LISTA vs LISTA_PARA_PLAN**: Una feature `LISTA_PARA_PLAN` puede pasar a `/wf-prepare-plan` (no tiene bloqueos propios), pero su implementación posterior dependerá de que sus dependencias estén también planificadas e implementadas. Indica al usuario que puede planificar pero debe respetar el orden de fases para implementar.

---

## Paso 7: Formato del informe

Usa `references/readiness_report_template.md` para estructurar el informe.

---

## Paso 8: Escribir el resultado

Path de salida: directorio padre del directorio de features + `<basename>_readiness_report.md`
- El basename se toma del `_features.md` encontrado (ej: si es `prd-hogar-sad_features.md` → `prd-hogar-sad_readiness_report.md`)
- Ejemplo: `docs/prd-hogar-sad_features.md` → `docs/prd-hogar-sad_readiness_report.md`

Escribe el informe en el archivo correspondiente.

---

## Paso 8.5: Actualizar estado en `_features.md`

Tras escribir el readiness report, actualiza el `_features.md` encontrado en el Paso 2:

### 8.5a — Estado por feature

Para cada bloque de feature en la sección `## Features identificadas`, actualiza (o añade si no existe) la línea:
```
- **Estado**: [LISTA | LISTA_PARA_PLAN | BLOQUEADA_POR_GAPS | BLOQUEADA_POR_CONFLICTOS | ESPERANDO_DEPENDENCIAS]
```

Usa el estado determinado en el Paso 6. Si una feature tiene múltiples bloqueos, usa el de mayor prioridad (GAPS > CONFLICTOS > DEPENDENCIAS).

### 8.5b — Resumen de estado

Añade o actualiza la sección `## Resumen de estado` (justo después de `## Features identificadas`, antes de `## Tabla de shared models`):

```markdown
## Resumen de estado

> Última actualización: [YYYY-MM-DD] | Fuente: `<path>_readiness_report.md`

| Feature | Estado | Bloqueantes |
|---------|--------|-------------|
| F-001: [nombre] | LISTA | — |
| F-002: [nombre] | BLOQUEADA_POR_GAPS | P-001, P-002 |
```

### 8.5c — Historial de cambios

Si existe la sección `## Historial de cambios` en `_features.md`, añade una fila:
```
| [versión+1] | [YYYY-MM-DD] | readiness | Estado actualizado desde wf-spec-readiness |
```

---

## Paso 9: Informar al usuario

- Path del informe generado
- Resumen rápido:
  - N features listas de M totales
  - N features bloqueadas (desglose por tipo de bloqueo)
- Siguiente paso según el estado:
  - **Todas listas**: "Todas las features están listas. Ejecuta `/wf-prepare-plan generate <feature_spec.md>` siguiendo el orden de fases del informe."
  - **Algunas listas**: "Puedes empezar con las features LISTA y LISTA_PARA_PLAN de las primeras fases. Las features bloqueadas requieren acción — consulta el informe para los detalles."
  - **Ninguna lista**: "Ninguna feature está lista para planificar. Revisa el informe para los bloqueos y resuélvelos antes de continuar."
