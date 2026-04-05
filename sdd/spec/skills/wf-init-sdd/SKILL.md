---
name: wf-init-sdd
description: Wizard interactivo que guía al usuario por el flujo SDD de PRD a feature specs. Recoge la ruta del PRD e inicia el análisis de gaps como primer paso obligatorio. Activa en frases como "no sé qué hacer", "guíame", "empieza el pipeline", "init sdd", "qué puedo hacer con sdd", "ayúdame a empezar", "cómo empiezo".
argument-hint: ""
effort: low
allowed-tools: [Read, Bash]
context: fork
---

# Workflow: INIT-SDD — Wizard Guiado

Tu objetivo es guiar al usuario para iniciar el flujo SDD: de PRD a feature specs, siempre pasando por el análisis de gaps. No ejecutas lógica propia — preguntas, recoges respuestas y delegas.

**Regla de oro:** No asumas nada. Pregunta siempre. No inventes rutas ni nombres de archivo.

---

## Paso 1: Detectar estado actual

Pregunta al usuario:
> "¿Cuál es la ruta del directorio de tu proyecto? (donde están o estarán los artefactos SDD)"

Espera su respuesta. Verifica que el directorio existe:
```
!test -d "<ruta>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario y vuelve a preguntar.

**Busca artefactos en ese directorio** ejecutando:
```
!ls "<ruta>"/*_features.md "<ruta>"/features/*/README.md "<ruta>"/*_spec.md "<ruta>"/*_analysis.md "<ruta>"/*_discovery.md "<ruta>"/*_delta_analysis.md "<ruta>"/*_conflict_report.md "<ruta>"/*_readiness_report.md 2>/dev/null || echo "SIN_ARTEFACTOS"
```

**Evalúa en orden de prioridad (de más avanzado a menos avanzado):**

### Si existe `_features.md` y `features/*/_spec.md`:

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

### Si existe `_discovery.md` pero NO `_features.md` ni `features/*/_spec.md`:

- "Tienes un discovery generado pero aún no se han creado los specs por feature."
- "Siguiente paso — genera los specs de todas las features:"
- "`/wf-spec-features-first <ruta_prd>`"

### Si existe `_analysis.md` pero NO `_spec.md` ni `_discovery.md`:

- Lee el `_analysis.md` y busca si contiene `_(pendiente)_` en gaps `[CRÍTICO]`:
  - Si hay gaps críticos pendientes: "El análisis tiene gaps **críticos** sin responder. Edita `_analysis.md`, respóndelos, y luego ejecuta `/wf-spec-features-first <ruta_prd>` para generar los specs por feature."
  - Si no hay gaps críticos pendientes: "El análisis está completo. Siguiente paso: `/wf-spec-features-first <ruta_prd>`"

### Si no se encontraron artefactos SDD:

- "No encontré artefactos SDD en ese directorio."
- Ir al **Paso 2** para iniciar el flujo desde cero.

---

## Paso 2: Iniciar flujo PRD → Análisis → Feature Specs

Pregunta al usuario:
> "¿Cuál es la ruta del archivo PRD o documento de requisitos?"

Espera su respuesta. Verifica que el archivo existe:
```
!test -f "<ruta>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y vuelve a preguntar.

Si existe → invoca `/wf-spec-analyze <ruta>`.

Tras la ejecución, informa:
> "Se ha generado el análisis de gaps en `<path>_analysis.md`."
> "**Siguiente paso:** edita el archivo, responde las preguntas marcadas como _(pendiente)_ (las `[CRÍTICO]` son obligatorias para specs completos) y luego ejecuta `/wf-spec-features-first <ruta>` para generar los specs por feature."

---

## Reglas generales

- **Nunca invoques un workflow sin tener todos los argumentos** que necesita. Si el usuario no proporciona una ruta, pregúntala.
- **Verifica siempre que los archivos existen** antes de invocar un workflow. Si no existen, informa con la ruta exacta y vuelve a preguntar.
- **El análisis de gaps es obligatorio.** No ofrezcas formas de saltárselo.
- **Si el usuario responde algo que no encaja**, intenta interpretar su intención. Si quiere hacer algo post-spec (delta, conflict, readiness, plan, tasks), redirige al skill correspondiente del rootmap en CLAUDE.md.
