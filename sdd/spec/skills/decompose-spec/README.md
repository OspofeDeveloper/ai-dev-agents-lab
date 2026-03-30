# decompose-spec — Descomponer un Spec en Features

**Caso de uso**: partir un `_spec.md` monolítico validado en Specs SDD independientes por feature.

Comando: `/decompose-spec <archivo_spec.md>`

---

## Orquestador: `decompose-spec` (`SKILL.md`)

Verifica que el spec esté listo (sin `_(pendiente)_`, con los 8 elementos SDD), delega la partición al agente `sdd-analyst` en modo `decompose`, gestiona el ownership checkpoint de shared models, y escribe todos los artefactos resultantes.

**Checkpoint de ownership**: si el agente devuelve shared models con owner ambiguo, el orquestador pausa, presenta las opciones al usuario con el criterio de desempate de `decompose-expert`, y espera confirmación antes de escribir ningún archivo.

**Verificación automática de conflictos** (post-escritura): si se generaron 2 o más features, el orquestador invoca automáticamente `sdd-analyst` en modo `conflict`. Es no bloqueante — informa del resultado pero no impide continuar.

**Salida**:
- `_features.md` — índice de features con tabla de shared models y sus owners
- `features/<nombre>/<nombre>_spec.md` — spec independiente por cada feature
- `features/<nombre>/README.md` — descripción de la feature
- `_conflict_report.md` — si se detectaron conflictos (opcional)

---

## Workflow (Capa 3)

### `spec-decompose/`

**Modo**: `decompose`

Recibe el Spec monolítico y aplica las reglas de `decompose-expert` para:

1. **Identificar features**: agrupa HUs por unidad funcional cohesiva aplicando el test de independencia
2. **Validar candidatas**: cada feature propuesta debe tener journeys independientes, mínimo 3 CAs y actor claro; si no cumple, propone fusión con otra feature
3. **Declarar shared models**: identifica modelos de datos referenciados por más de una feature y asigna ownership según los criterios de desempate
4. **Producir artefactos**:
   - `_features.md` con la tabla de features y shared models (template: `references/features_template.md`)
   - `_spec.md` por feature con los 8 elementos SDD, CAs renumerados localmente (templates: `references/feature_spec_template.md` y `references/feature_readme_template.md`)

**Restricciones clave**: el agente copia literalmente el contenido del spec original — no reescribe, no sintetiza, no inventa. Solo reorganiza y renumera.

---

## Flujo típico

```
/prepare-spec finalize prd.md
  → prd_spec.md

/decompose-spec prd_spec.md
  → prd_features.md
  → features/authentication/authentication_spec.md
  → features/authentication/README.md
  → features/time-tracking/time-tracking_spec.md
  → features/time-tracking/README.md
  → [_conflict_report.md si hay conflictos]

[Para cada feature:]
/prepare-plan features/authentication/authentication_spec.md
/prepare-tasks features/authentication/authentication_plan.md
```

**Orden recomendado**: empieza por las features owner de shared models, ya que su plan define los modelos que las demás features consumen.
