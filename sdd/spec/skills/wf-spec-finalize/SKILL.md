---
name: wf-spec-finalize
description: Genera el Spec SDD final a partir de un documento de requisitos y su análisis de gaps respondido. Activa en frases como "genera el spec final", "finaliza el spec", "convierte el análisis en spec", "transforma este documento en spec", "construye el spec definitivo".
argument-hint: "<archivo.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-analyst
---

# Workflow: FINALIZE

Tu objetivo es construir el Spec SDD final usando la información ya validada por el humano. Usa `kb-spec-expert` como guía estructural para asegurarte de que el Spec resultante cumple los 8 elementos y pasa la Prueba de Pureza.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del archivo de requisitos original (no el `_analysis.md`).

Si no hay argumento, informa al usuario:
> "Uso: `/wf-spec-finalize <archivo.md>`"
> "Ejemplo: `/wf-spec-finalize docs/requisitos.md`"

---

## Paso 2: Verificar archivos

Verifica que el archivo principal existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

Busca el archivo de análisis en este orden:
1. `<nombre_base>_analysis.md` en el mismo directorio (nombre canónico)
2. Si no existe, busca cualquier `*_analysis.md` en el mismo directorio y usa el más reciente
3. Si tampoco existe ninguno → informa: "No se encontró un archivo de análisis. Primero ejecuta `/wf-spec-analyze <archivo.md>` para generarlo."

---

## Paso 3: Leer el contenido

Lee el archivo principal y el `_analysis.md` en su totalidad.

Comprueba la severidad de los items pendientes en el `_analysis.md`:
- Si hay items `[CRÍTICO]_(pendiente)_` sin respuesta → informa al usuario: "Hay X gaps **críticos** sin responder. Las HUs afectadas se marcarán como `[INCOMPLETO]` en el spec." Lista las HUs afectadas (campo `Afecta` de cada gap). **Continúa.**
- Si solo hay items `[INFORMATIVO]_(pendiente)_` → informa al usuario que se aplicarán las asunciones por defecto y **continúa**.

---

## Paso 4: Construir el Spec

1. **Extraer las respuestas** de los items `[P-XXX]` del análisis
2. **Integrar respuestas exactamente como las escribió el cliente** — sin interpretar ni ampliar
3. **Procesar contaminaciones de Pureza**: para cada contaminación `[C-XXX]` del análisis, lee el campo `Acción`:
   - `ACEPTAR` o `EDITAR`: usar la reescritura (modificada o no) en lugar del texto original
   - `RECHAZAR`: conservar el texto original del documento y documentar la excepción en una sección `## Excepciones de Pureza` del spec con la justificación del cliente
   - Si no hay campo `Acción` marcado: aplicar la reescritura sugerida por defecto (compatibilidad con análisis anteriores)
4. **Construir el Spec** con los 8 elementos en orden (ver template)
5. **Aplicar la Prueba de Pureza** sobre lo que tú mismo escribas antes de producir el output
6. **Asignar cada CA a su HU padre**: cada CA debe incluir `← HU-XXX` referenciando la historia que cubre
7. **Marcar HUs incompletas**: para cada gap `[CRÍTICO]_(pendiente)_`, localiza las HUs indicadas en su campo `Afecta` y añade al final de cada una: `> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-XXX]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.` Genera la HU con la información disponible. Los CAs asociados se generan parcialmente si es posible o se omiten con referencia al gap.
8. **Auto-marcar el Checklist**: marca `[x]` los items que puedes verificar directamente del spec que generaste; deja `[ ]` solo los que requieren validación humana posterior
9. **Rellenar la sección "Resumen de generación"** del template: completa las tablas de estado de los 8 elementos, HUs incompletas, asunciones por defecto aplicadas y contaminaciones de Pureza procesadas. Si una tabla no aplica, escribe "Ninguna." debajo del encabezado correspondiente

---

## Paso 5: Reglas de integración

- **No inventar**: si el cliente no respondió un gap `[CRÍTICO]`, no inferir la respuesta — generar la HU con la información disponible y marcarla `[INCOMPLETO]`. Para gaps `[INFORMATIVO]` sin respuesta, usar únicamente la "Asunción por defecto" declarada en el análisis — no añadir nada más.
- **No interpretar**: el texto del cliente va tal cual, sin parafrasear
- **No añadir**: si la respuesta del cliente cubre exactamente el gap, no expandirla con suposiciones adicionales

---

## Paso 6: Formato del Spec

Consulta `references/output_template.md` para la estructura exacta del Spec SDD final.

---

## Paso 7: Escribir el resultado

Determina el path de salida: mismo directorio que el archivo de entrada + nombre base + `_spec.md`.
- Ejemplo: `docs/requisitos.md` → `docs/requisitos_spec.md`

Escribe el Spec generado en ese path.

---

## Paso 7.5: Generar el documento de trazabilidad

Genera el archivo `_traceability.md` que mapea cada RF del documento original a las HUs que lo implementan.

**Por qué ahora:** En este momento tienes en contexto tanto el documento de origen (con sus RFs o secciones funcionales) como el spec recién generado (con sus HUs). Es el único punto del pipeline donde se puede establecer la procedencia RF→HU antes de que las HUs se distribuyan en features tras el decompose.

### Extraer las HUs del spec generado

Lee el spec que acabas de escribir y lista todas las HUs con su ID y título.

### Mapear cada HU a su RF de origen

Usando el documento de requisitos original (ya leído en el Paso 3), identifica qué RF o sección funcional motivó cada HU:

- **Si el PRD tiene RFs numerados** (ej: "RF-4 Control Horario"): asigna directamente el ID del RF.
- **Si el PRD tiene secciones funcionales sin numeración** (ej: "## Control Horario"): crea IDs RF-001, RF-002… basándose en los títulos de sección y añade al final del documento la nota: `> Los IDs de RF son inferidos de las secciones funcionales del PRD — el documento original no los numera explícitamente.`
- **Si el PRD no tiene estructura clara**: agrupa las HUs por tema funcional, crea IDs RF sintéticos y añade la misma nota.

### Construir el documento de trazabilidad

Consulta `references/traceability_template.md` para la estructura exacta.

- Columna Feature = `—` para todas las HUs (se completará en `wf-spec-decompose`)
- Estado = `pendiente-decompose` para todas las HUs
- Genera también la tabla de Cobertura por RF (agrupando HUs por RF)
- Historial: una fila inicial con tipo "inicial" y fecha de hoy

**Path de salida:** mismo directorio que el spec + nombre base + `_traceability.md`
- Ejemplo: `docs/prd.md` → `docs/prd_traceability.md`

Escribe el archivo.

---

## Paso 8: Informar al usuario

Tras escribir los archivos, informa **solo** lo siguiente en terminal:

- Spec generado: `<path>_spec.md`
- Trazabilidad: `<path>_traceability.md`

> El detalle completo (estado de los 8 elementos, HUs incompletas, asunciones y contaminaciones) está dentro de la sección "Resumen de generación" del propio spec.

Añade **siempre** al final del output los siguientes bloques:

---
**PRD CONGELADO**

El documento `[path_del_prd_original]` queda congelado a partir de este momento.
No lo modifiques directamente. Para cambios futuros sobre el spec:

  `/wf-spec-delta analyze <path>_spec.md --new-reqs <descripcion_del_cambio.md>`

Los cambios quedarán registrados en el Changelog del spec y en `_traceability.md`.

---
**Siguiente paso** — descomponer el spec monolítico en features:

  `/wf-spec-decompose <path>_spec.md`

Si editas el spec manualmente antes de descomponer, puedes re-validarlo con `/wf-spec-validate <path>_spec.md`.

---
