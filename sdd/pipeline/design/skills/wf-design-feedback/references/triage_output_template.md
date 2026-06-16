# Plantilla de salida — Triage de feedback

Sobrescribir el archivo de captura con este formato:

```markdown
---
source: <cliente|pm|dev|qa|stitch|otro>
captured_at: <fecha ISO>
triaged_at: <fecha ISO>
feature: <path_spec o N/A>
status: triaged
---

# Design Feedback — <fuente>

## Feedback original

> <texto literal>

## Triage

### Item 1: <resumen del item del feedback>
- **Categoria**: brief_change | design_delta | feature_view_change | microcopy_change | a11y_concern | functional_change | out_of_scope
- **Severidad**: BAJA | MEDIA | ALTA | CRITICA
- **Razonamiento**: <por que cae en esta categoria>
- **Accion propuesta**: <comando concreto o decision concreta>
- **Owner sugerido**: <PD lead, Junior con apoyo, dev, PM, cliente>

### Item 2: ...

## Plan de aplicacion sugerido

1. <accion 1, en orden>
2. <accion 2>
3. ...

## Items descartados (out_of_scope)

- <item descartado>: <razon>
```
