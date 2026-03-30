---
name: spec-delta
description: Workflow interno para el modo DELTA del agente sdd-analyst. Define cómo analizar cambios incrementales a un Spec existente (submodo analyze) y cómo integrarlos de forma segura (submodo apply). Cargado como contexto por sdd-analyst — no invocar directamente.
allowed-tools: [Read]
disable-model-invocation: true
---

# Workflow: DELTA

Tu objetivo es gestionar la evolución controlada de un Spec SDD existente. Usa `spec-expert` para asegurarte de que los cambios propuestos y el spec resultante mantienen la pureza funcional y los 8 elementos SDD.

**Regla de oro:** El delta nunca reescribe la historia del spec — solo la extiende. Los cambios deben ser mínimos y quirúrgicos. Si el documento de nuevos requisitos describe en realidad un cambio de scope masivo, indícalo explícitamente al finalizar y sugiere volver a partir de un PRD completo.

---

## Submodo ANALYZE

### Qué debes hacer

**1. Inventariar el spec existente**

Extrae y lista internamente (no en el output):
- Todos los actores con sus capacidades
- Todas las HUs con sus IDs y títulos
- Todos los CAs con sus IDs, HU padre y GIVEN/WHEN/THEN
- Todos los Journeys con sus IDs
- Todas las Instrucciones Inambiguas (reglas de comportamiento)
- La sección Fuera de Alcance

**2. Analizar los nuevos requisitos**

Lee el documento de nuevos requisitos e identifica, consultando `spec-expert` para verificar pureza funcional:

- **HUs AÑADIDAS**: funcionalidades que no existen en el spec actual. Una nueva HU es: mismo actor (o actor nuevo) con objetivo funcional no cubierto por ninguna HU existente.
- **HUs MODIFICADAS**: funcionalidades existentes cuyo comportamiento, actor o valor cambia. Cita la HU original.
- **HUs ELIMINADAS**: funcionalidades del spec actual que los nuevos requisitos explícitamente eliminan o reemplazan. Cita la HU a eliminar.
- **CAs AFECTADOS**: para cada HU añadida/modificada, identifica los CAs nuevos o los cambios a CAs existentes (GIVEN/WHEN/THEN).
- **Reglas de comportamiento**: nuevas reglas, modificaciones a reglas existentes, reglas que quedan obsoletas.
- **Impacto en Fuera de Alcance**: si los nuevos requisitos mueven algo de fuera a dentro del alcance, o viceversa.

**3. Aplicar la Prueba de Pureza**

Consulta `spec-expert` para verificar que cada cambio propuesto está libre de contaminación técnica. Si un nuevo requisito contiene tech (frameworks, APIs, patrones de implementación), propón la reescritura funcional equivalente.

**4. Detectar gaps funcionales en los nuevos requisitos**

Aplica la misma lógica que el modo ANALYZE estándar pero sobre los nuevos requisitos en el contexto del spec existente. Genera gaps `[D-XXX]` (prefijo D = Delta, para distinguir de los `[P-XXX]` del spec original):
- `[D-001][CRÍTICO]`: impide definir un CA verificable para el cambio propuesto
- `[D-002][INFORMATIVO]`: edge case asumible, con Asunción por defecto

**5. Producir el output**

Usa `references/delta_analysis_template.md` para estructurar el informe.

---

## Submodo APPLY

### Qué debes hacer

**1. Verificar que no hay gaps críticos sin resolver**

Si hay `[CRÍTICO]_(pendiente)_` en el delta analysis → lista cuáles y detén la ejecución. (El orquestador ya debería haber bloqueado esto — es una segunda línea de defensa.)

**2. Integrar los cambios exactamente como los aprobó el humano**

Reglas de integración (las mismas del modo FINALIZE, aplicadas a los cambios):
- **No interpretar**: el texto aprobado va tal cual
- **No ampliar**: si la respuesta cubre el gap, no expandirla
- **No inferir**: si algo quedó sin responder pero era [INFORMATIVO], usa solo la Asunción por defecto

Para cada tipo de cambio:

- **HUs AÑADIDAS**: insertar después de la última HU existente con numeración consecutiva (ej: si el spec llega hasta HU-006, la primera nueva es HU-007).
- **HUs MODIFICADAS**: reemplazar solo el texto de la HU afectada; mantener el ID original.
- **HUs ELIMINADAS**: eliminar la HU y todos sus CAs asociados. Renumerar HUs y CAs afectados para mantener secuencia sin huecos.
- **CAs NUEVOS**: insertar con numeración consecutiva al final de los CAs de su HU padre. Incluir `← HU-XXX`.
- **CAs MODIFICADOS**: reemplazar solo el GIVEN/WHEN/THEN del CA afectado; mantener el ID.
- **CAs ELIMINADOS**: eliminar y renumerar los CAs restantes del spec para eliminar huecos.
- **Journeys**: actualizar añadiendo/modificando/eliminando pasos según los cambios de HUs.
- **Instrucciones Inambiguas**: añadir/modificar/eliminar reglas según el delta.
- **Fuera de Alcance**: actualizar si el delta lo especifica.

**3. Actualizar el versionado**

Incrementar la versión en el header del spec:
- Si existe campo `Versión` o similar → incrementar el número menor (1.0 → 1.1, 1.2 → 1.3, 2.0 → 2.1)
- Si no existe → añadir al header: `> Versión: 1.1 | Actualizado: [YYYY-MM-DD]`

**4. Añadir o actualizar la sección Changelog**

Al final del spec (después de Fuera de Alcance), añadir o actualizar:

```markdown
## Changelog

### v[X.Y] — [YYYY-MM-DD]
- **Añadidas**: HU-XXX "[título]"[, HU-YYY "[título]"]
- **Modificadas**: HU-XXX "[título original]" — [descripción breve del cambio]
- **Eliminadas**: HU-XXX "[título]" (y sus CAs asociados)
- **CAs nuevos**: CA-XXX a CA-YYY
- **CAs modificados**: CA-XXX "[título]"
- **CAs eliminados**: CA-XXX "[título]"
- **Reglas**: [nueva/modificada/eliminada] "[descripción breve]"
```

Si el spec ya tenía una sección Changelog, añade la nueva entrada al inicio (orden cronológico inverso).

**5. Documentar asunciones aplicadas**

Si se aplicaron asunciones de gaps `[INFORMATIVO]`, añadir antes del Changelog:

```markdown
## Asunciones Aplicadas (v[X.Y])

- **[D-XXX]**: [descripción de la asunción aplicada por defecto]
```

**6. Aplicar la Prueba de Pureza al spec resultante completo**

Consulta `spec-expert` y verifica que el spec final no tiene contaminación técnica. Si la hay (puede haberse introducido al integrar respuestas del cliente), señálala en el output para que el orquestador lo informe al usuario.

**7. Auto-verificar el checklist**

Revisa que el spec resultante sigue teniendo los 8 elementos SDD. Si alguno ha quedado incompleto por la integración de cambios, márcalo como `[ ]` en el checklist del spec.
