---
name: wf-spec-delta
description: "Evoluciona un Spec de feature existente de forma incremental. Modo 'analyze' genera un informe delta con HUs y CAs anadidos, modificados y eliminados; modo 'apply' integra los cambios validados en el spec. La resolucion de HUs [INCOMPLETO] desde un _analysis.md pertenece a wf-spec-gap-resolve."
when_to_use: "Activa en frases como 'quiero anadir funcionalidad al spec', 'actualiza el spec con estos requisitos nuevos', 'evoluciona el spec con este cambio', 'genera el delta del spec'."
argument-hint: "analyze <spec.md> --new-reqs <desc.md> | apply <spec.md> <delta.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-writer
---

# Workflow: DELTA

Tu objetivo es gestionar la evolución controlada de un Spec SDD existente. Usa `kb-spec-expert` para asegurarte de que los cambios propuestos y el spec resultante mantienen la pureza funcional y los 8 elementos SDD.

**Regla de oro:** El delta nunca reescribe la historia del spec — solo la extiende. Los cambios deben ser mínimos y quirúrgicos. Si el documento de nuevos requisitos describe en realidad un cambio de scope, prioridad o exclusión del producto, indícalo explícitamente y remite a `wf-prd-change` antes de seguir.

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
Si no hay argumento o el modo no es válido, informa al usuario:
> "Uso:"
> - "`/wf-spec-delta analyze <feature_spec.md> --new-reqs <description.md>`"
> - "`/wf-spec-delta apply <feature_spec.md> <feature_delta_analysis.md>`"

Ejemplos:
- `analyze features/auth/spec/auth_spec.md --new-reqs new_requirements.md`
- `apply features/auth/spec/auth_spec.md features/auth/spec/auth_delta_analysis.md`

Si el usuario intenta usar `resolve`, remítele a:
> "`/wf-spec-gap-resolve <feature_spec.md> [--analysis <path_analysis.md>]`"

---

## Paso 2: Verificar archivos

**Modo `analyze`:**
1. Verifica que el spec existe y termina en `_spec.md`. Si no → informa: "El primer argumento debe ser un spec SDD (`_spec.md`). Para generar un spec nuevo, usa `/wf-spec-analyze`."
2. Verifica que el archivo de nuevos requisitos existe. Si no → informa con la ruta exacta y detén.

**Modo `apply`:**
1. Verifica que el spec existe y termina en `_spec.md`.
2. Verifica que el delta analysis existe y termina en `_delta_analysis.md`. Si no → informa: "El segundo argumento debe ser un delta analysis generado por `/wf-spec-delta analyze`."
3. Lee el delta analysis y comprueba si hay gaps `[CRÍTICO]` con `_(pendiente)_` sin respuesta. Si los hay → informa al usuario: "Hay X gaps **críticos** sin responder. Las HUs afectadas se marcarán como `[INCOMPLETO]`." **Continúa.**

---

## Paso 3: Leer el contenido

Lee ambos archivos en su totalidad.

---

## Submodo ANALYZE

### Paso 4A: Inventariar el spec existente

Extrae y lista internamente (no en el output):
- Todos los actores con sus capacidades
- Todas las HUs con sus IDs y títulos
- Todos los CAs con sus IDs, HU padre y GIVEN/WHEN/THEN
- Todos los Journeys con sus IDs
- Todas las Instrucciones Inambiguas (reglas de comportamiento)
- La sección Fuera de Alcance

### Paso 5A: Analizar los nuevos requisitos

Lee el documento de nuevos requisitos e identifica, consultando `kb-spec-expert` para verificar pureza funcional:

- **HUs AÑADIDAS**: funcionalidades que no existen en el spec actual. Una nueva HU es: mismo actor (o actor nuevo) con objetivo funcional no cubierto por ninguna HU existente.
- **HUs MODIFICADAS**: funcionalidades existentes cuyo comportamiento, actor o valor cambia. Cita la HU original.
- **HUs ELIMINADAS**: funcionalidades del spec actual que los nuevos requisitos explícitamente eliminan o reemplazan. Cita la HU a eliminar.
- **CAs AFECTADOS**: para cada HU añadida/modificada, identifica los CAs nuevos o los cambios a CAs existentes (GIVEN/WHEN/THEN).
- **Reglas de comportamiento**: nuevas reglas, modificaciones a reglas existentes, reglas que quedan obsoletas.
- **Impacto en Fuera de Alcance**: si los nuevos requisitos mueven algo de fuera a dentro del alcance, o viceversa.

### Paso 6A: Aplicar la Prueba de Pureza

Consulta `kb-spec-expert` para verificar que cada cambio propuesto está libre de contaminación técnica. Si un nuevo requisito contiene tech (frameworks, APIs, patrones de implementación), propón la reescritura funcional equivalente.

### Paso 7A: Detectar gaps funcionales en los nuevos requisitos

Aplica la misma lógica que el modo ANALYZE estándar sobre los nuevos requisitos en el contexto del spec existente. Consulta `kb-gap-conventions` para el formato de IDs `[D-XXX]` (prefijo D = Delta), las definiciones de severidad y el marcador `_(pendiente)_`.

Si el supuesto "nuevo requisito" en realidad redefine el alcance del MVP, una exclusión del PRD o una regla transversal del producto, detén el delta y remite a `wf-prd-change`.

### Paso 8A: Formato del informe delta

Usa `${CLAUDE_SKILL_DIR}/references/delta_analysis_template.md` para estructurar el informe.

---

## Submodo APPLY

### Paso 4B: Segunda verificación de gaps críticos

Si hay gaps `[CRÍTICO]` con `_(pendiente)_` en el delta analysis → informa al usuario qué HUs se marcarán `[INCOMPLETO]` y **continúa**. (Coherente con el Paso 2.)

### Paso 5B: Integrar los cambios

Aplica los cambios siguiendo las reglas de `${CLAUDE_SKILL_DIR}/references/spec_delta_integration_rules.md` (no interpretar, no ampliar, no inferir; reglas por tipo: HUs añadidas/modificadas/eliminadas, CAs, Journeys, Instrucciones Inambiguas, Fuera de Alcance).

### Paso 6B: Actualizar versionado y Changelog

Incrementar la versión en el header del spec (1.0 → 1.1, 1.2 → 1.3, 2.0 → 2.1).

Añadir o actualizar `## Changelog` al final del spec (orden cronológico inverso) siguiendo la plantilla de `${CLAUDE_SKILL_DIR}/references/changelog_template.md`. Si se aplicaron asunciones `[INFORMATIVO]`, añadir también `## Asunciones Aplicadas (v[X.Y])` antes del Changelog.

### Paso 6B.5: Regenerar `_features.md` (si existe)

`_features.md` es un índice **generado** (no se edita a mano): la trazabilidad RF→HU→Feature y el estado se derivan de los specs en disco. Tras escribir el spec actualizado, regenera el índice desde la raíz del proyecto (el directorio que contiene `.sdd/`):

```
python3 .sdd/scripts/sdd-features-index.py <raíz_spec>
```

`<raíz_spec>` es el directorio que contiene `features/` y `_features.md` (si el spec está en `features/<nombre>/` —directamente o en `spec/`— es el directorio que contiene `features/`; en otro caso, el del propio spec). Si no existe `_features.md` ni discovery, o falta el script, omitir silenciosamente (el delta del spec ya está aplicado).

---

### Paso 7B: Aplicar la Prueba de Pureza al spec resultante

Consulta `kb-spec-expert` y verifica que el spec final no tiene contaminación técnica. Si la hay, señálala en el output.

### Paso 8B: Auto-verificar el checklist

Revisa que el spec resultante sigue teniendo los 8 elementos SDD. Si alguno ha quedado incompleto, márcalo como `[ ]` en el checklist del spec.

---

## Paso N-1: Escribir el resultado

- **Modo `analyze`**: mismo directorio que el spec + nombre base + `_delta_analysis.md`
  - Ejemplo: `features/auth/spec/auth_spec.md` → `features/auth/spec/auth_delta_analysis.md`
- **Modo `apply`**: sobreescribe el spec existente con la versión actualizada

---

## Paso N-0.5: Verificación de conflictos tras apply (no bloqueante)

Solo en modo `apply`. Busca si existe un `_features.md` en el proyecto (si el spec está dentro de `features/<nombre>/` — directamente o en su subcarpeta `spec/` — búscalo en el directorio que contiene `features/`; en otro caso, en el mismo directorio):

- **Si existe `_features.md`**: lee todos los specs `*_spec.md` de las features declaradas. Ejecuta el workflow `wf-spec-conflict` con el spec recién actualizado + todos los otros specs. Si detecta conflictos → escribe el informe en `<nombre>_conflict_report.md` en el mismo directorio que el spec.
- **Si no existe `_features.md`**: omitir este paso.

Este paso es **informativo y no bloquea** el flujo.

---

## Paso N: Informar al usuario

**Tras analyze:** path del delta generado, impacto (HUs añadidas/modificadas/eliminadas, CAs afectados), nº de gaps `[CRÍTICO]` e `[INFORMATIVO]` pendientes. Siguiente paso: responder gaps críticos y ejecutar `/wf-spec-delta apply`.

**Tras apply:** path del spec actualizado, nueva versión, resumen de cambios (HUs/CAs). Si se actualizó `_features.md`: indicar "✓ Trazabilidad actualizada". Si hay conflictos: referenciar `_conflict_report.md`. Siguiente paso: `/wf-spec-validate <path>_spec.md`.
