# Test 05 — `wf-spec-decompose`

**Propósito del workflow:** Partir un spec monolítico (`prd_spec.md`) en specs por feature, identificar shared models y sus owners, y detectar conflictos entre features. Es el segundo paso tras `finalize`.

---

## Prompt de activación

```
/wf-spec-decompose sdd/prd_spec.md
```

---

## Flujo esperado paso a paso

### Paso 1 — El orquestador L1 parsea el comando
**Actor:** skill `wf-spec-decompose` (L1)
**Acción:** Lee el path del spec monolítico.
**Verifica precondiciones:**
- El archivo existe
- Es un archivo `*_spec.md` (no un PRD raw ni un analysis)
- Idealmente verifica que tiene estructura de spec SDD (aunque no bloquea si no puede confirmarlo)

**Señal de correcto:** El agente no empieza a descomponer él mismo — lanza el subagente.

---

### Paso 2 — El orquestador lanza el subagente `sdd-analyst`
**Actor:** skill `wf-spec-decompose` (L1)
**Acción:** Invoca `Agent(subagent_type="sdd-analyst")` con:
```
modo: decompose
spec: <contenido de prd_spec.md>
output_dir: <directorio donde está el spec>
```

---

### Paso 3 — El subagente `sdd-analyst` enruta al workflow correcto
**Actor:** agente `sdd-analyst` (L2)
**Carga como contexto:**
- Knowledge `kb-spec-expert` — para validar que cada spec de feature sigue los 8 elementos
- Knowledge `kb-decompose-expert` — criterios de feature válida, reglas de shared models, ownership
- Knowledge `kb-conflict-expert` — para detectar conflictos durante la partición
- Workflow `wf-spec-decompose` — instrucciones paso a paso

---

### Paso 4 — El subagente ejecuta el workflow `wf-spec-decompose`
**Actor:** agente `sdd-analyst` (L2), guiado por `wf-spec-decompose` (L3)
**Acciones en orden:**

**4a. Identificar features:**
- Agrupa HUs, Journeys y CAs por cohesión funcional (no por estructura técnica)
- Verifica que cada feature candidata cumple los 3 criterios del kb-decompose-expert:
  1. Tiene al menos 1 Journey propio que no depende de otra feature
  2. Tiene mínimo 3 CAs propios
  3. Tiene actor claro
- Nombra cada feature con `kebab-case`

**4b. Identificar shared models:**
- Detecta entidades de dominio usadas en más de 1 feature
- Para cada shared model, determina el owner usando los criterios de desempate:
  1. Feature que crea el modelo explícitamente
  2. Feature que tiene CRUD completo
  3. Feature con mayor cobertura de CAs sobre el modelo
  4. Proximidad semántica
- Las features no-owner solo referencian el modelo, no lo redefinen

**4c. Generar `prd_features.md`:**
- Índice de features con nombre, descripción de 1 línea y lista de HUs asignadas
- Tabla de shared models con columnas: modelo | owner | referencias

**4d. Generar spec por feature:**
- Para cada feature: `features/<nombre>/<nombre>_spec.md` con los 8 elementos SDD
- Solo incluye las HUs, Journeys y CAs asignados a esa feature
- Los shared models del owner: los define completamente
- Los shared models no-owner: los referencia pero no los redefine

**4e. Generar README por feature:**
- `features/<nombre>/README.md` con visión general de la feature

**4f. Ejecutar check de conflictos automático:**
- Detecta conflictos entre features según las 5 reglas del kb-conflict-expert
- Si hay conflictos: genera `_conflict_report.md` en el directorio raíz
- Si no hay conflictos: lo indica en la respuesta inline (no genera el archivo)

**Señal de correcto:** Cada spec de feature es autocontenido y verificable sin leer el spec monolítico.

---

### Paso 5 — El subagente escribe los artefactos de salida
**Actor:** agente `sdd-analyst` (L2)
**Archivos generados:**
```
prd_features.md
features/
  feature-a/
    feature-a_spec.md
    README.md
  feature-b/
    feature-b_spec.md
    README.md
  ...
_conflict_report.md   (solo si hay conflictos)
```

---

## Resultado esperado

| Elemento | Valor |
|----------|-------|
| Archivos generados | `prd_features.md` + `features/X/X_spec.md` + `features/X/README.md` × N |
| Conflictos | `_conflict_report.md` si los hay |
| Bloqueo | No bloquea — el conflict report es informativo |
| Siguiente paso | `/wf-prepare-plan features/X/X_spec.md` para cada feature |

---

## Señales de fallo (qué validar)

- El L1 hace la partición él mismo en vez de lanzar el subagente
- Las features no cumplen los 3 criterios mínimos (feature con 1-2 CAs)
- Los shared models se duplican en múltiples specs en vez de asignarse a un owner
- El spec de una feature referencia HUs o CAs de otra feature
- No se genera `prd_features.md`
- El conflict report no se genera cuando hay HUs duplicadas entre features
- Los specs de feature tienen contaminación técnica (el agente "mejoró" el contenido al copiar)
