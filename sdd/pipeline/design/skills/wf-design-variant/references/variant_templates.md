# Plantillas para A/B testing visual

## Plantilla de `<feature>_variants.md`

```markdown
---
spec: <path>
design: <path>
brief: <path>
variants: [A, B, ...]
hypothesis: "<texto>"
metric: "<metric clave del brief que evalua>"
status: pending_validation
created_at: <fecha>
---

# Variants — <feature name>

## Hipotesis

> <texto literal>

## Metrica clave

<que metric del brief se va a usar para decidir>

## Variantes

### Variante A
- **Descripcion**: <texto>
- **Archivos**:
  - `<feature>_views.A.md`
  - `<feature>_flows.A.md`
  - `<feature>_ui_prompt.A.md`
- **Diferencias clave respecto a B**: <bullets>

### Variante B
- **Descripcion**: <texto>
- **Archivos**: ...

## Plan de validacion

1. Implementar ambas variantes en codigo (lectura del `_ui_prompt.<X>.md` para Stitch o handoff a dev).
2. Definir el split (50/50, 70/30, otro).
3. Definir el periodo (X dias o N usuarios).
4. Definir criterio de decision (mejora >= Y% en metric).

## Resultados

Pendiente. Tras la validacion, actualizar este documento con:
- ganador
- delta de la metrica
- decision: aplicar ganador via `wf-design-delta apply` o iterar.
```

## Plantilla de sección `## Resultados` (modo compare)

```markdown
## Resultados (validados el <fecha>)

| Variante | Metric | Delta vs control | Observaciones |
|---|---|---|---|
| A | XX% | baseline | <notas> |
| B | YY% | +Z% | <notas> |

**Ganador**: <X | empate | no concluyente>
**Decision**: <aplicar X via wf-design-delta | iterar | descartar A/B>

## Aprendizajes

- <bullet>
- <bullet>
```
