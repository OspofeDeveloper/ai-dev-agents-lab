# prepare-delta — Evolución Incremental de un Spec

**Caso de uso**: añadir, modificar o eliminar funcionalidad en un `_spec.md` ya existente sin regenerarlo desde cero.

Comando: `/prepare-delta <submode> <archivo_spec.md> [--new-reqs <archivo.md>]`

---

## Orquestador: `prepare-delta` (`SKILL.md`)

Gestiona dos submodos: `analyze` (genera el análisis del delta) y `apply` (integra los cambios validados). Verifica archivos y precondiciones en cada submode, delega al agente `sdd-analyst` en modo `delta`, y escribe los artefactos resultantes.

**Checkpoint de bloqueo** (submode `apply`): si el `_delta_analysis.md` tiene gaps `[CRÍTICO]_(pendiente)_` sin respuesta, el orquestador para y lista los que deben resolverse antes de aplicar.

**Salida**:
- `analyze` → `_delta_analysis.md` con inventario de cambios (HUs/CAs añadidos, modificados, eliminados) y gaps detectados
- `apply` → `_spec.md` actualizado con versión incrementada (ej: `1.0 → 1.1`) y sección `## Changelog`

---

## Workflow (Capa 3)

### `spec-delta/`

**Modo**: `delta` (submodos: `analyze`, `apply`)

**Submode `analyze`**:
1. Hace inventario del spec existente (HUs y CAs numerados)
2. Compara con el nuevo documento de requisitos para identificar:
   - HUs/CAs **añadidos** (nuevas funcionalidades)
   - HUs/CAs **modificados** (cambios de comportamiento)
   - HUs/CAs **eliminados** (funcionalidades deprecadas)
3. Para cada cambio, aplica los 3 checks de `spec-expert` (completitud, pureza, testabilidad)
4. Genera gaps `[D-XXX]` para información faltante o ambigua
5. Produce el `_delta_analysis.md` con el inventario completo

**Submode `apply`**:
1. Lee el spec original y el `_delta_analysis.md` respondido
2. Aplica los cambios de forma **quirúrgica**: solo toca lo que cambia, no modifica el resto
3. Verifica que el resultado sigue teniendo los 8 elementos SDD intactos (auditoría de pureza)
4. Incrementa la versión del spec
5. Añade sección `## Changelog` documentando los cambios y asunciones aplicadas

**Principio clave**: el delta es mínimo. No es una reescritura del spec — es una cirugía precisa sobre el spec existente.

Template de output del análisis en `references/delta_analysis_template.md`.

---

## Flujo típico

```
# Spec existente en producción
features/auth/auth_spec.md  (versión 1.0)

/prepare-delta analyze features/auth/auth_spec.md --new-reqs new_auth_requirements.md
  → features/auth/auth_delta_analysis.md

[edita auth_delta_analysis.md: responde gaps [CRÍTICO]]

/prepare-delta apply features/auth/auth_spec.md features/auth/auth_delta_analysis.md
  → features/auth/auth_spec.md actualizado (versión 1.1)
```

Después de `apply`, es recomendable ejecutar `/check-conflicts` si el proyecto tiene múltiples features, para verificar que el cambio no introduce inconsistencias con otras features.
