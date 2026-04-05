---
name: wf-init-sdd
description: Wizard interactivo que guía al usuario por los flujos SDD disponibles. Presenta opciones numeradas, recoge los argumentos necesarios e invoca el workflow correcto. Activa en frases como "no sé qué hacer", "guíame", "empieza el pipeline", "init sdd", "qué puedo hacer con sdd", "ayúdame a empezar", "cómo empiezo".
argument-hint: ""
effort: low
allowed-tools: [Read, Bash]
context: fork
---

# Workflow: INIT-SDD — Wizard Guiado

Tu objetivo es guiar al usuario hasta el workflow SDD correcto. No ejecutas lógica propia — preguntas, recoges respuestas y delegas.

**Regla de oro:** No asumas nada. Pregunta siempre. No inventes rutas ni nombres de archivo.

---

## Paso 1: Presentar el menú principal

Muestra al usuario las opciones disponibles con este formato exacto:

---

**¿Qué quieres hacer?**

1. **Generar specs a partir de un PRD** — Tengo un documento de requisitos y quiero convertirlo en Specs SDD
2. **Documentar una feature concreta** — Quiero generar el spec de una sola funcionalidad sin pasar por el spec monolítico
3. **Descomponer spec en features** — Tengo un spec monolítico y quiero partirlo en specs independientes por feature
4. **Modificar una funcionalidad existente** — Tengo un spec y quiero añadir, cambiar o eliminar requisitos
5. **Resolver gaps pendientes en una feature** — Tengo HUs marcadas como `[INCOMPLETO]` y ya he respondido los gaps
6. **Validar un spec** — Quiero verificar que un spec cumple los estándares SDD
7. **Detectar conflictos entre features** — Quiero verificar que los specs de diferentes features son coherentes entre sí
8. **Ver qué features están listas** — Quiero saber el estado de mis features y el orden recomendado de implementación
9. **Continuar donde lo dejé** — Ya tengo artefactos generados y no sé cuál es el siguiente paso

Escribe el número de la opción que quieras.

---

Espera la respuesta del usuario antes de continuar.

---

## Paso 2: Ejecutar el flujo de la opción elegida

### Opción 1 — Generar specs a partir de un PRD

Pregunta al usuario:
> "¿Cuál es la ruta del archivo PRD o documento de requisitos?"

Espera su respuesta. Verifica que el archivo existe:
```
!test -f "<ruta>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si existe → invoca `/wf-spec-analyze <ruta>`.

Tras la ejecución, informa:
> "Siguiente paso: edita el archivo `_analysis.md` generado, responde las preguntas marcadas como _(pendiente)_ (las `[CRÍTICO]` son obligatorias) y luego ejecuta `/wf-spec-finalize <ruta>` para generar el Spec SDD."

---

### Opción 2 — Documentar una feature concreta (Fast-Track)

Pregunta al usuario:
> "¿Cuál es la ruta del archivo que describe la funcionalidad?"

Espera su respuesta. Verifica que el archivo existe.

Luego pregunta:
> "¿Cuál es el nombre de la capability? (en kebab-case, ej: `push-notifications`, `time-tracking`)"

Espera su respuesta.

Invoca: `/wf-spec-fast-track <ruta> --capability <nombre>`

---

### Opción 3 — Descomponer spec en features

Pregunta al usuario:
> "¿Cuál es la ruta del spec monolítico? (el archivo `_spec.md`)"

Espera su respuesta. Verifica que el archivo existe y que termina en `_spec.md`.

Invoca: `/wf-spec-decompose <ruta>`

Tras la ejecución, informa:
> "Se han generado los specs por feature en el directorio `features/`. El siguiente paso recomendado es `/wf-spec-readiness features/` para ver cuáles están listas para planificar."

---

### Opción 4 — Modificar funcionalidad existente (Delta)

Pregunta al usuario:
> "¿Cuál es la ruta del spec de feature a modificar? (el archivo `_spec.md`)"

Espera su respuesta. Verifica que el archivo existe y que termina en `_spec.md`.

Luego pregunta:
> "¿Cuál es la ruta del archivo que describe los cambios o nuevos requisitos?"

Espera su respuesta. Verifica que el archivo existe.

Invoca: `/wf-spec-delta analyze <spec> --new-reqs <cambios>`

Tras la ejecución, informa:
> "Siguiente paso: revisa el `_delta_analysis.md` generado, responde los gaps `[CRÍTICO]` si los hay, y luego ejecuta `/wf-spec-delta apply <spec> <delta_analysis>`."

---

### Opción 5 — Resolver gaps pendientes en una feature

Pregunta al usuario:
> "¿Cuál es la ruta del spec de feature con HUs incompletas? (el archivo `_spec.md`)"

Espera su respuesta. Verifica que el archivo existe y que termina en `_spec.md`.

Luego pregunta:
> "¿Has respondido los gaps en el archivo `_analysis.md` correspondiente? (sí/no)"

- Si responde **no**: "Primero edita el `_analysis.md`, responde los gaps marcados como _(pendiente)_ y vuelve a ejecutar esta opción."
- Si responde **sí**: Invoca `/wf-spec-delta resolve <spec>`

Tras la ejecución, informa:
> "Las HUs completadas ya no están marcadas como `[INCOMPLETO]`. Ejecuta `/wf-spec-readiness features/` para verificar el estado actualizado."

---

### Opción 6 — Validar un spec

Pregunta al usuario:
> "¿Cuál es la ruta del spec a validar? (el archivo `_spec.md`)"

Espera su respuesta. Verifica que el archivo existe.

Invoca: `/wf-spec-validate <ruta>`

---

### Opción 7 — Detectar conflictos entre features

Pregunta al usuario:
> "¿Cuál es la ruta del spec de feature que quieres verificar?"

Espera su respuesta. Verifica que el archivo existe.

Luego pregunta:
> "¿Cuál es la ruta del directorio de features? (ej: `docs/features/`)"

Espera su respuesta. Verifica que el directorio existe:
```
!test -d "<ruta>" && echo "EXISTE" || echo "NO_EXISTE"
```

Invoca: `/wf-spec-conflict <spec> --features-dir <directorio>`

---

### Opción 8 — Ver qué features están listas

Pregunta al usuario:
> "¿Cuál es la ruta del directorio de features? (ej: `docs/features/`)"

Espera su respuesta. Verifica que el directorio existe:
```
!test -d "<ruta>" && echo "EXISTE" || echo "NO_EXISTE"
```

Invoca: `/wf-spec-readiness <ruta>`

Tras la ejecución, informa según el resultado:
- Si hay features **BLOQUEADA_POR_GAPS**: "Hay features con HUs incompletas. Usa la opción 5 (resolver gaps) para desbloquearlas."
- Si hay features **BLOQUEADA_POR_CONFLICTOS**: "Hay conflictos de severidad ALTA. Usa la opción 7 (detectar conflictos) para revisarlos y resolverlos manualmente."
- Si hay features **LISTA**: "Las features marcadas como LISTA pueden avanzar a planificación con `/wf-prepare-plan generate <feature>_spec.md`."

---

### Opción 9 — Continuar donde lo dejé

Pregunta al usuario:
> "¿Cuál es la ruta del directorio de tu proyecto? (donde están o estarán los artefactos SDD)"

Espera su respuesta. Verifica que el directorio existe.

**Busca artefactos en ese directorio** ejecutando:
```
!ls "<ruta>"/*_features.md "<ruta>"/features/*/README.md "<ruta>"/*_spec.md "<ruta>"/*_analysis.md "<ruta>"/*_delta_analysis.md "<ruta>"/*_conflict_report.md "<ruta>"/*_readiness_report.md 2>/dev/null || echo "SIN_ARTEFACTOS"
```

**Aplica esta lógica de detección (evalúa en orden de prioridad, de más avanzado a menos avanzado):**

**Si existe `_features.md` y `features/*/_spec.md`:**
- "Tu proyecto ya tiene specs por feature."
- Busca `[INCOMPLETO]` en los feature specs:
  ```
  !grep -rl "INCOMPLETO" "<ruta>"/features/*/*_spec.md 2>/dev/null
  ```
  - Si hay features con `[INCOMPLETO]`: "Las siguientes features tienen HUs incompletas: `<lista>`. Responde los gaps en el `_analysis.md` correspondiente y ejecuta `/wf-spec-delta resolve <feature>_spec.md` por cada una."
- Busca `_delta_analysis.md` sin aplicar:
  ```
  !ls "<ruta>"/features/*/*_delta_analysis.md 2>/dev/null
  ```
  - Si existen: "Hay delta analysis pendientes de aplicar: `<lista>`. Revisa los gaps y ejecuta `/wf-spec-delta apply <spec> <delta_analysis>` por cada uno."
- Verifica si existe `_conflict_report.md`. Si tiene conflictos `ALTA`: "Hay conflictos de severidad ALTA sin resolver. Revísalos antes de continuar."
- Si no hay bloqueos: "Siguiente paso recomendado: `/wf-spec-readiness <ruta>/features/` para ver el estado y orden de implementación de las features."
- Si ya existe `_readiness_report.md` y no hay bloqueos: "Ya tienes un readiness report. Las features marcadas como LISTA pueden avanzar a planificación con `/wf-prepare-plan generate <feature>_spec.md`."

**Si existe `_spec.md` pero NO `_features.md`:**
- "Tienes el spec monolítico listo."
- Busca `[INCOMPLETO]` en el spec:
  ```
  !grep -c "INCOMPLETO" "<ruta>"/*_spec.md 2>/dev/null
  ```
  - Si hay `[INCOMPLETO]`: "El spec tiene HUs incompletas. Responde los gaps en el `_analysis.md` y ejecuta `/wf-spec-delta resolve <spec>` antes de descomponer."
  - Si no hay `[INCOMPLETO]`: "Siguiente paso: `/wf-spec-decompose <ruta>_spec.md`"

**Si existe `_analysis.md` pero NO `_spec.md`:**
- Lee el `_analysis.md` y busca si contiene `_(pendiente)_` en gaps `[CRÍTICO]`:
  - Si hay gaps críticos pendientes: "El análisis tiene gaps **críticos** sin responder. Edita `_analysis.md`, respóndelos, y luego ejecuta `/wf-spec-finalize <ruta_prd>`."
  - Si no hay gaps críticos pendientes: "El análisis está completo. Siguiente paso: `/wf-spec-finalize <ruta_prd>`"

**Si no se encontraron artefactos SDD:**
- "No encontré artefactos SDD en ese directorio. Parece que todavía no has empezado."
- "Para empezar, necesitas un documento de requisitos (PRD). Ejecuta: `/wf-spec-analyze <ruta_del_prd.md>`"

---

## Reglas generales

- **Nunca invoques un workflow sin tener todos los argumentos** que necesita. Si el usuario no proporciona una ruta, pregúntala.
- **Verifica siempre que los archivos existen** antes de invocar un workflow. Si no existen, informa con la ruta exacta y vuelve a preguntar.
- **No interpretes** la intención del usuario más allá de la opción numérica que eligió. Si no está claro, pide aclaración.
- **Si el usuario responde algo que no es un número del 1 al 9**, intenta interpretar su intención semánticamente y mapearla a una de las 9 opciones. Si no puedes, vuelve a presentar el menú.
