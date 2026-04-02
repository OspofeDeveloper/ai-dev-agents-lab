# Test 01 — `wf-spec-analyze`

**Propósito del workflow:** Analizar un documento de requisitos (PRD), detectar gaps de información y elementos de contaminación técnica, y producir un informe estructurado. Es el punto de entrada obligatorio antes de generar cualquier spec.

---

## Prompt de activación

```
/wf-spec-analyze sdd/prd-hogar-sad.md
```

Variante con ruta relativa al proyecto:
```
/wf-spec-analyze prd-hogar-sad.md
```

---

## Flujo esperado paso a paso

### Paso 1 — El orquestador L1 parsea el comando
**Actor:** skill `wf-spec-analyze` (L1)
**Acción:** Lee el path del documento.
**Verifica precondiciones:**
- El archivo `prd-hogar-sad.md` existe
**NO hace:** análisis, razonamiento ni escritura de contenido

**Señal de correcto:** El agente confirma que va a lanzar un subagente sin hacer análisis él mismo.

---

### Paso 2 — El orquestador lanza el subagente `sdd-analyst`
**Actor:** skill `wf-spec-analyze` (L1)
**Acción:** Invoca `Agent(subagent_type="sdd-analyst")` con el siguiente payload:
```
modo: analyze
documento: <contenido de prd-hogar-sad.md>
```
**Configuración del subagente:**
- `memory: project`
- `permissionMode: acceptEdits`

**Señal de correcto:** Hay una invocación explícita de Agent tool con subagent_type sdd-analyst.

---

### Paso 3 — El subagente `sdd-analyst` enruta al workflow correcto
**Actor:** agente `sdd-analyst` (L2)
**Acción:** Lee el `modo: analyze` y carga como contexto:
- Knowledge `kb-spec-expert` — reglas de los 8 elementos SDD
- Knowledge `kb-gap-conventions` — formatos de IDs, severidades, marcadores
- Workflow `wf-spec-analyze` — instrucciones paso a paso para este modo

**NO hace:** decide por sí mismo qué analizar — sigue el workflow

**Señal de correcto:** El agente hace referencia a los 8 elementos SDD al revisar el documento.

---

### Paso 4 — El subagente ejecuta el workflow `wf-spec-analyze`
**Actor:** agente `sdd-analyst` (L2), guiado por el workflow `wf-spec-analyze` (L3)
**Acciones en orden:**
1. Lee el documento PRD completo
2. Para cada uno de los 8 elementos SDD, evalúa si está presente o ausente
3. Detecta contaminación técnica (lenguajes, frameworks, patrones, etc.) según `prohibited_items.md`
4. Clasifica cada gap encontrado:
   - `[P-001] [CRÍTICO]` — información que bloquea la generación del spec
   - `[P-002] [INFORMATIVO]` — información faltante donde se puede asumir un default
5. Para gaps CRÍTICO: formula una pregunta concreta al usuario
6. Para gaps INFORMATIVO: propone la asunción por defecto que aplicará

**Señal de correcto:** Los gaps tienen IDs con formato `[P-XXX]`, severidad entre corchetes, y las preguntas son concretas (no genéricas).

---

### Paso 5 — El subagente escribe el artefacto de salida
**Actor:** agente `sdd-analyst` (L2)
**Acción:** Genera el archivo `prd_analysis.md` en el mismo directorio que el PRD (o donde indique el template de salida del workflow)
**Contenido esperado del archivo:**
- Resumen del documento analizado
- Tabla de cobertura de los 8 elementos (presente/parcial/ausente)
- Lista de gaps con formato: `[P-XXX] [SEVERIDAD] descripción _(pendiente)_`
- Preguntas al usuario para gaps CRÍTICO
- Asunciones propuestas para gaps INFORMATIVO

**Señal de correcto:** El archivo existe, los gaps CRÍTICO tienen `_(pendiente)_`, la estructura sigue el template de `wf-spec-analyze/references/output_template.md`.

---

## Resultado esperado

| Elemento | Valor |
|----------|-------|
| Archivo generado | `prd_analysis.md` |
| Artefacto | Informe de gaps estructurado |
| Bloqueo | El agente avisa que hay gaps CRÍTICO pendientes y NO avanza a `finalize` automáticamente |
| Siguiente paso | El usuario responde los gaps CRÍTICO y vuelve a invocar `finalize` |

---

## Señales de fallo (qué validar)

- El L1 hace análisis él mismo en vez de lanzar el subagente
- El subagente genera `prd_spec.md` directamente sin pasar por analyze (se saltó la etapa)
- Los gaps no tienen IDs ni severidad
- El subagente avanza a finalize pese a haber gaps CRÍTICO sin resolver
- La contaminación técnica no se detecta (p.ej. deja pasar referencias a "Kotlin" o "RecyclerView" en el spec)
