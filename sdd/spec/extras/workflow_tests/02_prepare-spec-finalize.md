# Test 02 — `wf-spec-finalize`

**Propósito del workflow:** Generar el spec monolítico limpio con los 8 elementos SDD a partir del PRD original (y opcionalmente del `prd_analysis.md` previo con gaps ya respondidos). Es el segundo paso obligatorio tras `analyze`.

---

## Prompt de activación

```
/wf-spec-finalize sdd/prd-hogar-sad.md
```

Si existe un `prd_analysis.md` en el mismo directorio, el agente debe detectarlo y usarlo automáticamente.

---

## Flujo esperado paso a paso

### Paso 1 — El orquestador L1 parsea el comando
**Actor:** skill `wf-spec-finalize` (L1)
**Acción:** Lee el path del PRD.
**Verifica precondiciones:**
- El archivo PRD existe
- Busca si existe `prd_analysis.md` en el mismo directorio
- Si encuentra gaps `_(pendiente)_` con severidad `[CRÍTICO]` en el analysis → **bloquea y avisa al usuario**
- Si no hay analysis, lo acepta (puede hacer finalize sin analyze previo, pero no es lo ideal)

**Señal de correcto:** Si hay gaps CRÍTICO sin resolver, el agente no lanza el subagente sino que informa al usuario qué gaps debe responder primero.

---

### Paso 2 — El orquestador lanza el subagente `sdd-analyst`
**Actor:** skill `wf-spec-finalize` (L1)
**Acción:** Invoca `Agent(subagent_type="sdd-analyst")` con:
```
modo: finalize
documento_prd: <contenido del PRD>
analysis: <contenido de prd_analysis.md, si existe>
```

**Señal de correcto:** El payload incluye el analysis si existe.

---

### Paso 3 — El subagente `sdd-analyst` enruta al workflow correcto
**Actor:** agente `sdd-analyst` (L2)
**Carga como contexto:**
- Knowledge `kb-spec-expert` — definición y reglas de los 8 elementos SDD
- Knowledge `kb-gap-conventions` — cómo manejar gaps INFORMATIVO que aún están sin responder
- Workflow `wf-spec-finalize` — instrucciones paso a paso

---

### Paso 4 — El subagente ejecuta el workflow `wf-spec-finalize`
**Actor:** agente `sdd-analyst` (L2), guiado por `wf-spec-finalize` (L3)
**Acciones en orden:**
1. Lee el PRD y el analysis (si existe)
2. Para cada uno de los 8 elementos, genera el contenido a partir del PRD:
   - **Actores:** tabla de roles con capacidades
   - **Historias de Usuario:** formato "Como X, quiero Y, para que Z"
   - **Journeys:** pasos secuenciales con problema resuelto
   - **Resultados y Éxito:** qué significa "completado"
   - **Instrucciones Inambiguas:** reglas de negocio + tabla de navegación
   - **Criterios de Aceptación:** GIVEN/WHEN/THEN con referencia a HU padre
   - **Checklist de Validación:** 9 checkpoints
   - **Fuera de Alcance:** exclusiones funcionales (sin técnicas)
3. Aplica la Prueba de Pureza a cada frase sospechosa:
   > "¿Cambiaría esta frase si pasáramos a web o a Python?"
   > - SÍ → eliminar o mover al Plan
   > - NO → puede quedarse
4. Para gaps INFORMATIVO aún pendientes: aplica la asunción propuesta en el analysis
5. Para gaps INFORMATIVO sin analysis: aplica la asunción más conservadora y la marca en el spec

**Señal de correcto:** El spec resultante no contiene palabras como "Kotlin", "ViewModel", "API REST", "JWT", "RecyclerView", ni ningún término de la tabla `prohibited_items.md`.

---

### Paso 5 — El subagente escribe el artefacto de salida
**Actor:** agente `sdd-analyst` (L2)
**Acción:** Genera `prd_spec.md` en el mismo directorio que el PRD
**Contenido esperado:**
- Los 8 secciones bien diferenciadas con headers claros
- IDs consistentes: HU-001, CA-001, J-001, etc.
- Los CAs tienen referencia a la HU que los origina
- Sin contaminación técnica

---

## Resultado esperado

| Elemento | Valor |
|----------|-------|
| Archivo generado | `prd_spec.md` |
| Artefacto | Spec monolítico válido con 8 elementos SDD |
| Bloqueo | Si hay gaps CRÍTICO sin resolver en el analysis |
| Siguiente paso | `/wf-spec-decompose` o `/wf-spec-validate` |

---

## Señales de fallo (qué validar)

- El spec contiene términos técnicos (frameworks, lenguajes, patrones)
- Alguno de los 8 elementos está ausente
- Los CAs no tienen referencia a HU padre
- Los gaps INFORMATIVO se ignoran en vez de aplicar asunción
- El agente avanza pese a gaps CRÍTICO sin resolver
- El ID de los CAs no sigue un formato consistente
