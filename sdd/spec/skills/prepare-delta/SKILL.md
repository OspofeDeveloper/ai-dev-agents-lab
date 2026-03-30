---
name: prepare-delta
description: Orquestador SDD para evolucionar Specs de feature existentes con requisitos nuevos. Modo 'analyze' genera un informe delta que muestra HUs y CAs añadidos, modificados y eliminados; modo 'apply' integra los cambios validados en el spec, incrementando la versión y añadiendo Changelog. Activa en frases como "quiero añadir funcionalidad al spec", "actualiza el spec con estos requisitos nuevos", "añade esta feature al spec existente", "evoluciona el spec con este cambio", "genera el delta del spec".
argument-hint: "analyze <feature_spec.md> --new-reqs <description.md> | apply <feature_spec.md> <delta_analysis.md>"
effort: high
allowed-tools: [Read, Write, Agent]
disable-model-invocation: true
---

# prepare-delta — Orquestador del Flujo Delta SDD

Tu rol es de **orquestador puro**: parseas argumentos, verificas archivos, delegas el trabajo analítico al agente `sdd-analyst` en modo `delta`, y escribes el output resultante. No realizas el análisis ni la integración de cambios directamente — eso lo hace el agente especializado.

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
> - "`/prepare-delta analyze <feature_spec.md> --new-reqs <description.md>`"
> - "`/prepare-delta apply <feature_spec.md> <feature_delta_analysis.md>`"

Ejemplos:
- `analyze features/auth/auth_spec.md --new-reqs new_requirements.md` → modo=analyze, spec=features/auth/auth_spec.md, new-reqs=new_requirements.md
- `apply features/auth/auth_spec.md features/auth/auth_delta_analysis.md` → modo=apply, spec=features/auth/auth_spec.md, delta=features/auth/auth_delta_analysis.md

---

## Paso 2: Verificar archivos

**Modo `analyze`:**
1. Verifica que el spec existe y termina en `_spec.md`. Si no termina en `_spec.md` → informa: "El primer argumento debe ser un spec SDD (`_spec.md`). Para generar un spec nuevo, usa `/prepare-spec`."
2. Verifica que el archivo de nuevos requisitos existe. Si no → informa con la ruta exacta y detén.

**Modo `apply`:**
1. Verifica que el spec existe y termina en `_spec.md`.
2. Verifica que el delta analysis existe y termina en `_delta_analysis.md`. Si no → informa: "El segundo argumento debe ser un delta analysis generado por `/prepare-delta analyze`."
3. Lee el delta analysis y comprueba si hay items `[CRÍTICO]_(pendiente)_` sin respuesta. Si los hay → lista cuáles y detén: "Hay gaps **críticos** sin responder en el delta analysis. Son obligatorios antes de aplicar los cambios."

---

## Paso 3: Leer el contenido

Lee ambos archivos en su totalidad.

---

## Paso 4: Delegar al agente sdd-analyst

Invoca el agente `sdd-analyst` pasándole como prompt el siguiente bloque (con los valores reales sustituidos):

**Para modo `analyze`:**
```
Modo: delta
Submodo: analyze
Path del spec existente: <path_completo>
Contenido del Spec existente:
---
<contenido_completo_del_spec>
---
Path de los nuevos requisitos: <path_completo>
Contenido de los nuevos requisitos:
---
<contenido_completo_del_archivo_de_requisitos>
---
```

**Para modo `apply`:**
```
Modo: delta
Submodo: apply
Path del spec existente: <path_completo>
Contenido del Spec existente:
---
<contenido_completo_del_spec>
---
Contenido del delta analysis validado:
---
<contenido_completo_del_delta_analysis>
---
```

Espera a que el agente complete su ejecución y recibe su output estructurado.

---

## Paso 5: Escribir el resultado

Determina el path de salida:
- Modo `analyze`: mismo directorio que el spec + nombre base + `_delta_analysis.md`
  - Ejemplo: `features/auth/auth_spec.md` → `features/auth/auth_delta_analysis.md`
- Modo `apply`: sobreescribe el spec existente con la versión actualizada devuelta por el agente.

Escribe el output del agente en el archivo correspondiente.

---

## Paso 5.5: Verificación de conflictos tras apply (no bloqueante)

Solo en modo `apply`. Busca si existe un `_features.md` en el proyecto (igual que hace `prepare-plan`: dos niveles arriba si el spec está en `features/<nombre>/`, o en el mismo directorio):

- **Si existe `_features.md`**: lee todos los specs `*_spec.md` de las features declaradas. Invoca el agente `sdd-analyst` en modo `conflict` pasándole el spec recién actualizado + todos los otros specs de features. Si detecta conflictos → escribe el informe en `<nombre>_conflict_report.md` en el mismo directorio que el spec actualizado. Si no detecta conflictos → solo mencionarlo brevemente en el Paso 6.
- **Si no existe `_features.md`**: omitir este paso.

Este paso es **informativo y no bloquea** el flujo.

---

## Paso 6: Informar al usuario

**Tras analyze:**
- Path del delta analysis generado
- Resumen de impacto: cuántas HUs añadidas/modificadas/eliminadas, cuántos CAs afectados
- Cuántos gaps `[CRÍTICO]` pendientes (obligatorios) y cuántos `[INFORMATIVO]` (opcionales)
- Siguiente paso: "Revisa `<path>_delta_analysis.md`, responde los gaps `[CRÍTICO]` marcados como _(pendiente)_ y luego ejecuta `/prepare-delta apply <spec.md> <delta_analysis.md>`"

**Tras apply:**
- Path del spec actualizado
- Nueva versión del spec (ej: v1.0 → v1.1)
- Resumen de cambios integrados: HUs y CAs añadidos/modificados/eliminados
- Resultado de la verificación de conflictos (Paso 5.5):
  - Sin conflictos o sin `_features.md`: omitir o indicar brevemente
  - Con conflictos: "⚠ Se detectaron conflictos. Revisa `<path>_conflict_report.md` antes de continuar con `/prepare-plan`."
- Siguiente paso: "Puedes validar la integridad del spec actualizado con `/prepare-spec validate <path>_spec.md`"
