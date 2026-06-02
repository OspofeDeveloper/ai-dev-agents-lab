---
name: wf-spec-readiness
description: "Analiza los artefactos post-spec-generation (specs de feature, READMEs, _features.md, _conflict_report.md) y genera un informe de readiness que indica que features estan listas para plan, cuales estan bloqueadas y por que, y el orden de implementacion recomendado."
when_to_use: "Activa en frases como 'que features estan listas', 'readiness de las features', 'cuales puedo planificar', 'orden de implementacion', 'verifica readiness', 'que falta para planificar'."
argument-hint: "<path/features/>"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-auditor
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
- Ruta al spec (si existe)

**Detección de features no generadas aún**: si una feature del `_features.md` no tiene archivo `*_spec.md` correspondiente en `<features-dir>/<nombre>/`, marca la feature como `PENDIENTE_GENERACIÓN` y omite los Pasos 4b–4d para ella (no hay spec que inspeccionar). Sus dependencias se infieren solo del `_features.md`.

### 4b — Gaps (marcadores [INCOMPLETO])

Busca la cadena literal `[INCOMPLETO]` en el spec de la feature. Para cada HU marcada:
- ID de la HU (ej: HU-003)
- Gaps que la bloquean (referenciados en la línea que contiene `Pendiente de gap(s):` o `[P-XXX]` cercanos al marcador)

Clasifica la feature como **BLOQUEADA** si tiene al menos una HU `[INCOMPLETO]`.

### 4c — Conflictos no resueltos

Si existe `_conflict_report.md`:
- Primero verifica el estado general del informe. Debe indicar explícitamente `SIN_CONFLICTOS` o `CONFLICTOS_DETECTADOS`.
- Si el archivo existe pero no deja ese estado de forma inequívoca, trátalo como artefacto ambiguo y repórtalo en el informe de readiness.
- Busca todos los conflictos de severidad **ALTA** que involucren esta feature.
- Un conflicto se considera no resuelto si aparece en el informe (el informe refleja el estado en el momento de su generación; si se resolvió, el usuario debió re-ejecutar `/wf-spec-conflict`).

Clasifica la feature como **BLOQUEADA** si tiene al menos un conflicto ALTA asociado.

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
| `LISTA` | Sin `[INCOMPLETO]`, sin conflictos ALTA, sin artefactos ambiguos y sin dependencias bloqueantes |
| `BLOQUEADA` | Tiene HUs `[INCOMPLETO]`, conflictos ALTA, dependencias bloqueantes o artefactos ambiguos que impiden decidir con seguridad |
| `PENDIENTE_GENERACIÓN` | Identificada en el discovery pero aún no se ha generado spec (no se ha incluido en ninguna iteración de `wf-spec-features-first`). No es un bloqueo accionable — refleja que el humano aún no ha pedido procesarla. |
| `REQUIERE_CAMBIO_PRD` | El spec o `_features.md` declara alcance derivado desde analysis que debería consolidarse primero en PRD, o el artefacto explicita un aviso de gobernanza pendiente |

Una feature puede tener múltiples bloqueos simultáneos. En ese caso, listar todos los motivos en la columna de bloqueantes. La prioridad de display es: CAMBIO_PRD > GAPS > CONFLICTOS > DEPENDENCIAS > AMBIGÜEDAD_DE_ARTEFACTO.

**Nota importante**: el readiness report usa solo estados canónicos. El detalle fino se expresa en la columna `Bloqueantes`, no creando variantes de estado adicionales.

**Nota sobre `PENDIENTE_GENERACIÓN`**: estas features se incluyen en el `_features.md` y en el informe de readiness como visibilidad del backlog, pero no participan del topological sort ni del orden de implementación — no hay spec con dependencias declaradas hasta que se generen. Si otra feature ya generada declara una dependencia sobre una `PENDIENTE_GENERACIÓN`, esa dependencia se reporta como "dependencia hacia feature no generada todavía" (no bloquea readiness de la feature ya generada, pero sí señala al usuario qué generar a continuación).

---

## Paso 7: Formato del informe

Usa `${CLAUDE_SKILL_DIR}/references/readiness_report_template.md` para estructurar el informe.

---

## Paso 8: Escribir el resultado

Path de salida: directorio padre del directorio de features + `<basename>_readiness_report.md`
- El basename se toma del `_features.md` encontrado (ej: si es `prd-hogar-sad_features.md` → `prd-hogar-sad_readiness_report.md`)
- Ejemplo: `docs/prd-hogar-sad_features.md` → `docs/prd-hogar-sad_readiness_report.md`

Antes de escribir, verifica si el archivo ya existe:
- `!test -f "<path>"` — si existe, informa al usuario del path y pregunta: `[sobreescribir | cancelar]`. Continua solo si elige sobreescribir.

Escribe el informe en el archivo correspondiente.

---

## Paso 8.5: Actualizar estado en `_features.md`

Sigue la guía de `${CLAUDE_SKILL_DIR}/references/features_update_guide.md` para:
- **8.5a**: actualizar la línea `- **Estado**: [...]` por feature usando el estado de mayor prioridad
- **8.5b**: añadir o actualizar `## Resumen de estado` con tabla de estado actual
- **8.5c**: añadir fila al `## Historial de cambios` si la sección existe

---

## Paso 9: Informar al usuario

Informa: path del informe, resumen (N listas de M totales, N bloqueadas por tipo, N `PENDIENTE_GENERACIÓN`). Siguientes pasos según estado: si todas listas → ejecutar `/wf-prepare-plan generate` por fase; si algunas listas → empezar con primeras fases; si ninguna → resolver bloqueos; si hay `PENDIENTE_GENERACIÓN` → proporcionar comando `/wf-spec-features-first <prd.md> --features ...`.
