---
name: wf-spec-analyze
description: "Recopila las decisiones de negocio que necesitan los Specs desde un PRD vigente: mapea que elementos del Spec saldran del PRD, detecta contaminacion tecnica y formula preguntas concretas. Genera un _analysis.md."
when_to_use: "Activa en frases como 'prepara los inputs para los specs', 'que decisiones de negocio faltan para los specs', 'analiza este PRD para empezar los specs', 'genera el analisis previo al spec'."
argument-hint: "<archivo.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-explorer
user-invocable: true
---

# Workflow: ANALYZE

Este workflow pertenece a la fase Spec y **requiere un PRD o documento de requisitos previo** como entrada. Si el usuario todavía no tiene ese artefacto, remítelo a la fase PRD antes de continuar.

Tu objetivo es **recopilar las decisiones de negocio que los Specs necesitarán** a partir de un PRD vigente. No auditas el PRD ni le buscas defectos funcionales por deporte: el PRD ya hizo su trabajo en la fase anterior y, según `kb-prd-expert`, no tiene por qué contener HUs, Journeys, CAs ni Checklist — esos elementos pertenecen al Spec y se generarán después.

Usa `kb-spec-expert` para aplicar los 3 checks. El Check 1 mapea qué elementos del Spec se generarán a partir del PRD; el Check 2 detecta contaminación técnica (única condición que sí justifica retocar el PRD dentro del propio analyze); el Check 3 evalúa la testabilidad si el PRD ya tuviera CAs formales.

**Regla de oro:** Nunca rellenas huecos funcionales. Si algo no está definido o es ambiguo, lo marcas con `_(pendiente)_` en el campo "Respuesta" del gap (consulta `kb-gap-conventions` para el formato exacto) y formulas una pregunta concreta. El cliente decide, tú detectas. Si la respuesta pendiente realmente encubre un cambio de alcance, prioridad o reglas de negocio, debes remitir a `wf-prd-change`.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del archivo a analizar.

Si no hay argumento, informa al usuario:
> "Uso: `/wf-spec-analyze <archivo.md>`"
> "Ejemplo: `/wf-spec-analyze docs/requisitos.md`"

---

## Paso 2: Verificar el archivo

Verifica que el archivo existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

Si el nombre termina en `_spec.md`, `_plan.md` o `_tasks.md` → informa:
> "Este archivo parece un artefacto posterior del pipeline SDD. `/wf-spec-analyze` opera sobre PRDs o documentos de requisitos previos a Spec."

**Readiness del PRD (advisory, [[D-020]]).** Analyze solo produce un `_analysis.md` (no genera specs), así que **no bloquea**, pero **sí surfacea** las asunciones sin confirmar del PRD —la red que la fase PRD promete pero que este análisis, por sí solo, no resolvía—:
```
!python3 .sdd/scripts/sdd-prd-ready.py "<path>"
```
Si el veredicto es `OPEN_ASSUMPTIONS`/`ASSUMPTION_MISMATCH`, inclúyelo en el informe (Paso 8) como aviso: "el PRD arrastra N `[ASUNCIÓN]` sin confirmar; revísalas con `/wf-prd-review` antes de generar specs — este análisis no las resuelve". Si falta el script, omite el aviso y continúa.

---

## Paso 3: Leer el contenido

Lee el archivo en su totalidad.

---

## Paso 4: Mapear elementos del Spec y detectar problemas reales

### Check 1 — Mapeo de elementos del Spec a generar
Para cada uno de los 8 elementos del Spec (consulta `kb-spec-expert` para su definición), determina su estado de partida en el PRD:

- Actores
- Historias de Usuario (Como/quiero/para que)
- Recorridos de Usuario
- Resultados y Éxito
- Instrucciones Inambiguas (incluyendo tabla de destinos de navegación si hay flujos de navegación)
- Criterios de Aceptación (GIVEN/WHEN/THEN)
- Checklist de Validación
- Fuera de Alcance

Para cada uno, indica si ya viene en el PRD, si se generará entero durante la fase Spec, o si está parcial y se completará en Spec. **Esto no es un score de defectos**: lo normal en un PRD es que HUs formales, Journeys paso a paso, CAs en GIVEN/WHEN/THEN y Checklist no estén — pertenecen al Spec, no al PRD (`kb-prd-expert` Regla 9). El propósito de este check es dar visibilidad de qué se va a generar después, no señalar carencias.

### Check 2 — Pureza (única vía legítima para tocar el PRD)
Consulta `prohibited_items.md` y `error_patterns.md` del skill `kb-spec-expert` antes de emitir tu veredicto. Para cada frase problemática:
- Cita el fragmento exacto
- Explica por qué es técnico
- Propón la reescritura funcional

**Importante**: ésta es la **única** condición que justifica devolver el documento a la fase PRD. Si el Check 2 está limpio, el PRD se considera correcto tal cual está y se procede con los Specs, incluso si los Checks 1 o 3 reportan elementos ausentes (es lo esperable).

### Check 3 — Testabilidad
Si el PRD ya incluye CAs formales (poco habitual en un PRD), cada uno debe ser verificable objetivamente e independientemente, tener GIVEN/WHEN/THEN completo, y referenciar su HU padre. Los que no cumplan estos criterios deben aparecer con su reformulación sugerida. Si no hay CAs en el PRD, indica `NO_APLICA` — los CAs se generarán en la fase Spec.

---

## Paso 5: Formular gaps funcionales → preguntas [P-XXX]

Si encuentras información funcional ausente o ambigua (no técnica), formúlala como pregunta para el cliente. Cada gap debe ser:
- Concreto (no "¿qué más falta?")
- Sin opciones inventadas (el cliente decide)
- Neutro: no empujes hacia una solución que ya expanda el producto

Consulta `kb-gap-conventions` para el formato de IDs `[P-XXX]`, las definiciones de severidad `[CRÍTICO]` / `[INFORMATIVO]`, el marcador `_(pendiente)_` y el formato exacto de cada gap en el informe.

**Importante:** si el problema detectado no es una ambigüedad sino una contradicción entre el PRD vigente y una decisión nueva de negocio ("esto pasa de fase 2 a MVP", "se elimina esta exclusión", "ahora otro actor puede hacerlo"), no lo reduzcas a un gap normal. Márcalo explícitamente como **requiere change request** y remite a `wf-prd-change`.

**Importante 2 — posibles respuestas que expanden capacidad:** detecta también cuándo la propia pregunta puede desembocar fácilmente en una expansión funcional no comprometida en el PRD. En esos casos:

- añade el marcador advisory `[PUEDE_REQUERIR_CR]`
- redacta la pregunta de forma neutra, sin presentar como opciones "normales" soluciones expansivas
- deja claro que, si la respuesta introduce una entidad persistente, un catálogo reutilizable, una nueva granularidad funcional o un flujo adicional de usuario, deberá reevaluarse con `kb-product-change-governance`

Ejemplo de mala formulación:
- "¿catálogo persistente o texto libre?"

Mejor:
- "¿cómo se identifica este elemento en el producto actual?"
- y, si la respuesta introduce catálogo persistente o gestión reutilizable, escalar a `wf-prd-change`

### Campo "Afecta" (obligatorio en CRÍTICO)

Para cada gap `[CRÍTICO]`, determina qué HUs del documento no pueden completarse sin la respuesta a este gap. Lista sus IDs en el campo `- **Afecta**: [HU-001, HU-003]`. Si las HUs aún no tienen IDs asignados (porque el documento es un PRD sin HUs formales), describe las funcionalidades afectadas en texto libre (ej: `- **Afecta**: funcionalidad de login, recuperación de contraseña`).

### Clasificación de severidad (obligatoria)

Consulta `kb-gap-conventions` para las definiciones completas. Resumen:

- **`[CRÍTICO]`**: las HUs indicadas en "Afecta" quedarán marcadas `[INCOMPLETO]` en el spec si no se responde. Se generarán con la información disponible pero no podrán avanzar a plan/tasks.
- **`[INFORMATIVO]`**: continúa con asunción por defecto (edge cases asumibles, preferencias menores). **Siempre incluye una "Asunción por defecto"** con lo que se aplicará si el cliente no responde.
- **`[PUEDE_REQUERIR_CR]`**: marcador advisory opcional. Añádelo si la futura respuesta podría introducir expansión de capacidad y, por tanto, exigir `wf-prd-change` antes de derivar specs.

---

## Paso 6: Formato del informe

Consulta [output_template.md](output_template.md) para la estructura exacta del informe.

---

## Paso 7: Escribir el resultado

Determina el directorio de salida (regla de layout): si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.prd`, usa ese directorio (relativo a la raíz que contiene `.sdd/`); si no, usa el mismo directorio que el archivo de entrada. Nombre: nombre base del archivo de entrada + `_analysis.md`.
- Ejemplo (sin mapa): `docs/requisitos.md` → `docs/requisitos_analysis.md`
- Ejemplo (con `"artifacts": {"prd": "docs/prd"}`): → `docs/prd/requisitos_analysis.md`

Antes de escribir, verifica si el archivo ya existe:
```bash
!test -f "<path_calculado>" && echo "EXISTE" || echo "NO_EXISTE"
```
Si ya existe → pregunta al usuario:
> "Ya existe `<path>`. ¿Deseas regenerarlo?"
- Si responde **no** → informa el path del artefacto existente y detén.
- Si responde **sí** → continúa.

Escribe el informe generado en ese path.

---

## Paso 8: Informar al usuario

Tras escribir el archivo, informa:
- Path del archivo generado
- Veredicto del Estado de preparación para Specs
- Resumen: cuántos elementos del Spec se generarán desde cero vs. ya parciales en PRD, cuántas contaminaciones técnicas detectadas (si las hay), cuántos `[P-XXX]` pendientes (desglosados: CRÍTICOS e INFORMATIVOS)
- Siguiente paso:
  - Si veredicto = `LISTO_PARA_SPECS`: "Anota cualquier aclaración adicional en `<path>_analysis.md` y ejecuta `/wf-spec-features-first <archivo.md>` para el flujo completo, o `/wf-spec-discover <archivo.md> --analysis <path>_analysis.md` para el paso a paso."
  - Si veredicto = `LISTO_PARA_SPECS_CON_PREGUNTAS`: "Anota las respuestas a las preguntas marcadas como _(pendiente)_ en `<path>_analysis.md`. Después decide una de estas dos vías: (a) resolver primero los gaps `[CRÍTICO]` y ejecutar `/wf-spec-features-first <archivo.md>`; (b) continuar igualmente ejecutando `/wf-spec-features-first <archivo.md> --allow-open-critical-gaps` para aceptar HUs `[INCOMPLETO]`."
  - Si veredicto = `REQUIERE_LIMPIEZA_PRD`: "Hay contaminación técnica en el PRD. Tienes dos vías para limpiarlo: (a) aplicar tú mismo las reescrituras de la sección Pureza del análisis; (b) delegar la limpieza al agente `prd-expert` o ejecutar `/wf-prd-review <archivo.md>` para un diagnóstico previo más estructurado antes de corregir. Tras la corrección, vuelve a ejecutar `/wf-spec-analyze <archivo.md>`."
  - Si detectaste cambio de producto: "Antes de continuar con Specs, formaliza el cambio en el PRD con `/wf-prd-change <archivo.md> --new-reqs <cambio.md>` y luego evalúa impacto con `/wf-prd-sync-impact <archivo.md>`."
