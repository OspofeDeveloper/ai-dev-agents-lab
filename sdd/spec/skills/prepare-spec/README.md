# prepare-spec — Crear y Validar Specs SDD

**Caso de uso**: transformar un documento de requisitos en un Spec SDD válido, o validar uno ya existente.

Comando: `/prepare-spec <modo> <archivo> [--capability <nombre>]`

---

## Orquestador: `prepare-spec` (`SKILL.md`)

Parsea argumentos, verifica archivos y precondiciones, delega al agente `sdd-analyst` con el modo correspondiente, y escribe el artefacto resultante. No razona ni analiza directamente.

**Modos soportados**:

| Modo | Entrada | Salida |
|------|---------|--------|
| `analyze` | PRD / documento de requisitos | `_analysis.md` con gaps `[CRÍTICO]`/`[INFORMATIVO]` |
| `finalize` | Documento original + `_analysis.md` respondido | `_spec.md` con los 8 elementos SDD |
| `validate` | `_spec.md` existente | Informe inline (no genera archivo) |
| `fast-track` | Documento de una sola capability + `--capability <nombre>` | `features/<nombre>/<nombre>_spec.md` + README + entrada en `_features.md` |

**Checkpoint de bloqueo** (modo `finalize`): si el `_analysis.md` tiene gaps `[CRÍTICO]_(pendiente)_` sin respuesta, el orquestador para y lista cuáles deben responderse antes de continuar.

---

## Workflows (Capa 3)

### `spec-analyze/`

**Modo**: `analyze`

Audita el documento de requisitos aplicando los 3 checks de `spec-expert`:
1. **Completitud**: presencia de los 8 elementos SDD
2. **Pureza**: ausencia de términos técnicos (consulta `prohibited_items.md` y `error_patterns.md` de `spec-expert`)
3. **Testabilidad**: cada CA tiene GIVEN/WHEN/THEN completo y es verificable independientemente

Para cada problema detectado genera un gap `[P-XXX]` con severidad y, si la información falta, formula la pregunta para el cliente con el campo "Respuesta: _(pendiente)_".

Template de output en `references/output_template.md`.

---

### `spec-finalize/`

**Modo**: `finalize`

Integra las respuestas del cliente (del `_analysis.md` completado) en el Spec final con los 8 elementos SDD. Principio: no inventa, no interpreta, no expande — transcribe exactamente lo que el cliente respondió.

Para los gaps `[INFORMATIVO]` sin responder, aplica las asunciones por defecto definidas en el análisis.

Template de output en `references/output_template.md`.

---

### `spec-validate/`

**Modo**: `validate`

Audita un `_spec.md` existente para detectar regresiones introducidas por edición manual. Aplica los mismos 3 checks que `spec-analyze`. No genera ningún archivo: el resultado se imprime directamente al usuario como `APROBADO` o `REQUIERE_REVISIÓN`.

Útil como gate antes de ejecutar `/prepare-plan`.

Template de output en `references/output_template.md`.

---

### `spec-fast-track/`

**Modo**: `fast-track`

Genera directamente el spec de una sola capability sin pasar por el spec monolítico. Combina en una sola pasada el análisis, la gestión de gaps y la generación del spec. Útil para proyectos maduros que añaden features individuales.

- Gaps `[CRÍTICO]` sin respuesta se documentan en `## Items Pendientes` dentro del spec (bloquean `/prepare-plan`)
- Gaps `[INFORMATIVO]` se resuelven con asunciones y se documentan en `## Asunciones Aplicadas`
- Genera también el `README.md` de la feature y actualiza (o crea) el `_features.md` del proyecto

Templates en `references/feature_spec_template.md` y `references/feature_readme_template.md`.

---

## Flujo típico

```
/prepare-spec analyze prd.md
  → prd_analysis.md

[edita prd_analysis.md: responde gaps [CRÍTICO]]

/prepare-spec finalize prd.md
  → prd_spec.md

[edición manual opcional]

/prepare-spec validate prd_spec.md
  → informe inline
```

O en modo fast-track para una sola feature:

```
/prepare-spec fast-track feature-doc.md --capability mi-feature
  → features/mi-feature/mi-feature_spec.md
  → features/mi-feature/README.md
  → _features.md (creado o actualizado)
```
