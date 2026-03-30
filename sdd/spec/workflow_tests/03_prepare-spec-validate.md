# Test 03 — `prepare-spec validate`

**Propósito del workflow:** Auditar un spec ya existente (puede ser `prd_spec.md` o el spec de una feature) sin generar ningún archivo. Produce un informe inline de aprobado/rechazado. Útil para verificar calidad antes de pasar a decompose o plan.

---

## Prompt de activación

```
/prepare-spec validate sdd/prd_spec.md
```

O para un spec de feature ya generado:
```
/prepare-spec validate sdd/features/hogar/hogar_spec.md
```

---

## Flujo esperado paso a paso

### Paso 1 — El orquestador L1 parsea el comando
**Actor:** skill `prepare-spec` (L1)
**Acción:** Lee `validate` y el path del spec.
**Verifica precondiciones:**
- El archivo existe y tiene extensión `.md`
- No requiere analysis previo (es una auditoría independiente)

**Señal de correcto:** El agente no genera ningún archivo en este paso.

---

### Paso 2 — El orquestador lanza el subagente `sdd-analyst`
**Actor:** skill `prepare-spec` (L1)
**Acción:** Invoca `Agent(subagent_type="sdd-analyst")` con:
```
modo: validate
spec: <contenido del spec a auditar>
```

---

### Paso 3 — El subagente `sdd-analyst` enruta al workflow correcto
**Actor:** agente `sdd-analyst` (L2)
**Carga como contexto:**
- Knowledge `spec-expert` — definición y reglas de los 8 elementos SDD + Prueba de Pureza
- Workflow `spec-validate` — checklist de auditoría

**No carga:** `gap-conventions` ni `decompose-expert` (no son relevantes aquí)

---

### Paso 4 — El subagente ejecuta el workflow `spec-validate`
**Actor:** agente `sdd-analyst` (L2), guiado por `spec-validate` (L3)
**Acciones en orden:**
1. Verifica presencia de cada uno de los 8 elementos (presente / parcial / ausente)
2. Aplica la Prueba de Pureza a todas las frases del spec:
   - Detecta cualquier contaminación técnica
   - Lista cada infracción con su localización (sección + frase)
3. Valida la consistencia interna:
   - Todos los CAs tienen referencia a HU padre
   - Los IDs son únicos y sin saltos
   - Los Journeys tienen actor, pasos y problema resuelto
4. Verifica el Checklist de Validación (9 checkpoints del spec-expert)
5. Emite veredicto:
   - `APROBADO` — pasa todos los checks
   - `REQUIERE_REVISIÓN` — lista de incidencias numeradas con ubicación y sugerencia de corrección

**Señal de correcto:** El informe es específico: cita la sección y la frase problemática, no da feedback genérico.

---

### Paso 5 — El subagente devuelve el informe inline
**Actor:** agente `sdd-analyst` (L2)
**Acción:** Muestra el informe directamente en el chat — **NO genera ningún archivo**
**Formato esperado:**
```
## Validación: prd_spec.md
Estado: REQUIERE_REVISIÓN

### Incidencias
1. [Contaminación] Sección "Instrucciones Inambiguas" — "...usando JWT tokens..." → eliminar
2. [Elemento ausente] Falta sección "Fuera de Alcance"
3. [CA sin HU] CA-007 no referencia ninguna Historia de Usuario

### Cobertura de elementos
| Elemento | Estado |
|----------|--------|
| Actores | ✓ Presente |
| Historias de Usuario | ✓ Presente |
| Journeys | ~ Parcial (J-003 sin problema resuelto) |
...
```

---

## Resultado esperado

| Elemento | Valor |
|----------|-------|
| Archivo generado | Ninguno |
| Artefacto | Informe inline en el chat |
| Resultado posible | `APROBADO` o `REQUIERE_REVISIÓN` con lista de incidencias |
| Siguiente paso | Si aprobado: `/decompose-spec`. Si requiere revisión: corregir el spec y re-validar |

---

## Señales de fallo (qué validar)

- El agente genera un archivo `.md` de validación (no debería)
- El veredicto es genérico sin citar ubicaciones concretas
- El agente da APROBADO a un spec con contaminación técnica obvia
- No evalúa los 9 checkpoints del spec-expert
- No verifica consistencia de IDs ni referencias cruzadas CA→HU
