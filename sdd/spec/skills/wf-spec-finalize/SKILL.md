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
- Si hay items `[CRÍTICO]_(pendiente)_` sin respuesta → lista cuáles y detén: "Hay gaps **críticos** sin responder en `_analysis.md`. Son obligatorios para continuar."
- Si solo hay items `[INFORMATIVO]_(pendiente)_` → informa al usuario que se aplicarán las asunciones por defecto y **continúa**.

---

## Paso 4: Construir el Spec

1. **Extraer las respuestas** de los items `[P-XXX]` del análisis
2. **Integrar respuestas exactamente como las escribió el cliente** — sin interpretar ni ampliar
3. **Construir el Spec** con los 8 elementos en orden (ver template)
4. **Aplicar la Prueba de Pureza** sobre lo que tú mismo escribas antes de producir el output
5. **Asignar cada CA a su HU padre**: cada CA debe incluir `← HU-XXX` referenciando la historia que cubre
6. **Auto-marcar el Checklist**: marca `[x]` los items que puedes verificar directamente del spec que generaste; deja `[ ]` solo los que requieren validación humana posterior

---

## Paso 5: Reglas de integración

- **No inventar**: si el cliente no respondió un gap `[CRÍTICO]`, no inferirlo; el proceso debe haberse detenido antes de llegar aquí. Para gaps `[INFORMATIVO]` sin respuesta, usar únicamente la "Asunción por defecto" declarada en el análisis — no añadir nada más.
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

## Paso 8: Informar al usuario

Tras escribir el archivo, informa:
- Path del spec generado
- Estado de los 8 elementos SDD (cuáles están completos)
- Si se aplicaron asunciones por defecto: cuántas y en qué secciones
- Si hay items `[PENDIENTE]` restantes: cuántos y cuáles
- Siguiente paso: "Si editas el spec manualmente, puedes re-validarlo con `/wf-spec-validate <path>_spec.md`"
