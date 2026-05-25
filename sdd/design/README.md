# SDD Design — Prototipado visual entre Spec y Plan

Este directorio introduce la fase `design` del pipeline SDD. Su responsabilidad es transformar un `*_spec.md` validado en un contrato visual reutilizable por Stitch y en artefactos por feature que permitan validar flujos y vistas antes de entrar en el plan tecnico.

Diagramas detallados de esta fase: [DIAGRAMS.md](/Users/oscar/Documents/GitHub/ai-dev-agents-lab/sdd/design/DIAGRAMS.md).

## Objetivo de la fase

`design` no redefine producto ni implementacion. Su trabajo es cerrar:

- identidad visual persistente del producto
- inventario de vistas por feature
- secuencias y transiciones de interfaz
- contrato canonico de pantallas y estados visuales
- prompt estructurado de ensamblaje para Stitch

## Artefactos

### Producto

- `DESIGN.md`
  - SSoT visual de producto: tokens, componentes, layout y guidance

### Por feature

- `<feature>_flows.md`
  - secuencias, precondiciones y transiciones
- `<feature>_views.md`
  - SSoT de pantallas, componentes, acciones y estados visuales
- `<feature>_ui_prompt.md`
  - ensamblaje para Stitch a partir de `DESIGN.md`, `flows` y `views`

## Workflows disponibles

### 1. Crear o actualizar el sistema visual

```text
/wf-design-system generate features/account/account_spec.md
```

Genera o actualiza `DESIGN.md` a nivel producto.

### 2. Preparar el prototipo de una feature

```text
/wf-design-feature-prototype generate features/account/account_spec.md
```

Genera flows, views y prompt de ensamblaje para Stitch en el directorio de la feature.

## Regla operativa

El orden correcto es:

`spec validado -> DESIGN.md -> flows/views/ui_prompt -> Stitch -> plan -> tasks`

## Nota sobre el formato de `DESIGN.md`

`DESIGN.md` sigue el formato abierto de Google: front matter YAML para tokens normativos y markdown para rationale. Como comprobacion opcional, puede validarse con `npx @google/design.md lint DESIGN.md`.
