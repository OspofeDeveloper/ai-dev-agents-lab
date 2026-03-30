# Test 07 — `prepare-delta`

**Propósito del workflow:** Evolucionar un spec existente de forma incremental cuando llegan nuevos requisitos. Analiza qué cambia (HUs/CAs añadidos, modificados o eliminados), detecta gaps de la nueva info, y actualiza el spec sin destruir el trabajo previo. Tiene dos sub-modos: `analyze` y `apply`.

---

## Prompts de activación

**Sub-modo 1: Analizar qué cambia**
```
/prepare-delta analyze sdd/features/hogar/hogar_spec.md --new-reqs sdd/nuevos-requisitos.md
```

**Sub-modo 2: Aplicar el delta al spec (tras responder gaps)**
```
/prepare-delta apply sdd/features/hogar/hogar_spec.md sdd/features/hogar/hogar_delta_analysis.md
```

---

## Flujo esperado — Sub-modo `analyze`

### Paso 1 — El orquestador L1 parsea el comando
**Actor:** skill `prepare-delta` (L1)
**Acción:** Lee `analyze`, el spec existente y el documento de nuevos requisitos.
**Verifica precondiciones:**
- El spec existe
- El documento de nuevos requisitos existe
- Son archivos `.md`

---

### Paso 2 — El orquestador lanza el subagente `sdd-analyst`
**Actor:** skill `prepare-delta` (L1)
**Acción:** Invoca `Agent(subagent_type="sdd-analyst")` con:
```
modo: delta
sub_modo: analyze
spec_actual: <contenido del spec existente>
nuevos_requisitos: <contenido del documento de nuevos requisitos>
```

---

### Paso 3 — El subagente enruta y carga contexto
**Actor:** agente `sdd-analyst` (L2)
**Carga como contexto:**
- Knowledge `spec-expert` — para entender los 8 elementos y la Prueba de Pureza
- Knowledge `gap-conventions` — para usar IDs `[D-XXX]` (delta) en vez de `[P-XXX]`
- Knowledge `conflict-expert` — para detectar si el delta introduce contradicciones con el spec actual
- Workflow `spec-delta` — instrucciones paso a paso

---

### Paso 4 — El subagente ejecuta el workflow `spec-delta` (analyze)
**Actor:** agente `sdd-analyst` (L2), guiado por `spec-delta` (L3)
**Acciones en orden:**
1. Lee el spec actual y los nuevos requisitos en paralelo
2. Clasifica cada elemento nuevo:
   - **AÑADIR:** HU/CA/Journey nuevo que no existe en el spec actual
   - **MODIFICAR:** HU/CA existente que cambia de forma
   - **ELIMINAR:** HU/CA que los nuevos requisitos eliminan explícitamente
3. Aplica Prueba de Pureza a los nuevos requisitos (elimina contaminación técnica)
4. Detecta gaps en los nuevos requisitos (usa IDs `[D-XXX]`, no `[P-XXX]`)
5. Detecta si el delta introduce contradicciones con el spec actual (conflict-expert)
6. Si hay gaps `[CRÍTICO]`: los lista y bloquea el `apply`

**Señal de correcto:** Los IDs del delta usan prefijo `[D-XXX]` diferenciado de los IDs del spec original `[P-XXX]`.

---

### Paso 5 — El subagente escribe el delta analysis
**Actor:** agente `sdd-analyst` (L2)
**Archivo generado:** `features/hogar/hogar_delta_analysis.md`
**Contenido:**
```
# Delta Analysis: hogar_spec.md
Nuevos requisitos: nuevos-requisitos.md
Versión actual spec: 1.0

## Cambios propuestos
### AÑADIR
- HU nueva: "Como cuidador, quiero..."
- CA-nuevo: GIVEN/WHEN/THEN

### MODIFICAR
- HU-003: cambiar objetivo de "X" a "Y"

### ELIMINAR
- CA-012: ya no es relevante según nuevos requisitos

## Gaps detectados
- [D-001] [CRÍTICO] ¿Qué pasa si...? _(pendiente)_

## Conflictos detectados
- El CA nuevo entra en contradicción con CA-007 actual
```

---

## Flujo esperado — Sub-modo `apply`

### Paso 1 — El orquestador verifica precondiciones del apply
**Actor:** skill `prepare-delta` (L1)
**Verifica:**
- El spec existe
- El delta_analysis existe
- No hay gaps `[D-XXX] [CRÍTICO] _(pendiente)_` sin resolver en el delta_analysis

**Si hay gaps CRÍTICO pendientes:** Bloquea y pide al usuario que los resuelva primero.

---

### Paso 2 — El orquestador lanza el subagente
**Actor:** skill `prepare-delta` (L1)
**Acción:** Invoca `Agent(subagent_type="sdd-analyst")` con:
```
modo: delta
sub_modo: apply
spec_actual: <contenido del spec existente>
delta_analysis: <contenido del delta analysis (ya con gaps respondidos)>
```

---

### Paso 3-4 — El subagente aplica el delta
**Actor:** agente `sdd-analyst` (L2)
**Acciones en orden:**
1. Lee el spec actual y el delta analysis
2. Para cada cambio en el delta analysis:
   - AÑADIR: inserta en la sección correcta del spec, asigna nuevos IDs correlativos
   - MODIFICAR: actualiza el contenido, preserva el ID original
   - ELIMINAR: elimina el elemento, no deja hueco en la numeración (resequencia si es necesario)
3. Añade sección de Changelog al spec:
   ```
   ## Changelog
   ### v1.1 (fecha)
   - Añadido: HU-008 ...
   - Modificado: HU-003 ...
   - Eliminado: CA-012 ...
   ```
4. Actualiza el número de versión del spec (1.0 → 1.1)

### Paso 5 — El subagente sobreescribe el spec actualizado
**Actor:** agente `sdd-analyst` (L2)
**Archivo modificado:** `features/hogar/hogar_spec.md` (versión 1.1)

---

## Resultado esperado

| Sub-modo | Archivos generados/modificados | Bloqueo |
|----------|-------------------------------|---------|
| `analyze` | `hogar_delta_analysis.md` (nuevo) | Si hay gaps `[D-XXX] [CRÍTICO]` en los nuevos requisitos |
| `apply` | `hogar_spec.md` (actualizado a v1.1) | Si hay gaps `[D-XXX] [CRÍTICO]` sin resolver |

---

## Señales de fallo (qué validar)

- Los IDs del delta usan `[P-XXX]` en vez de `[D-XXX]`
- El `apply` sobreescribe el spec sin respetar los IDs originales (los renumera)
- El `apply` no añade la sección Changelog
- El `apply` avanza con gaps `[CRÍTICO]` sin resolver
- El agente modifica el spec directamente sin pasar por `analyze` primero (si el usuario solo pidió analyze)
- Los cambios ELIMINAR dejan referencias huérfanas en el spec (CAs que referencian HUs eliminadas)
