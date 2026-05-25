# SDD PRD — Etapa de entrada de requisitos

Este directorio contiene la capa de conocimiento y preflight para la entrada del pipeline SDD: el PRD o documento de requisitos inicial.

El objetivo de esta etapa no es generar Specs ni tomar decisiones técnicas. Su trabajo es comprobar que el documento de entrada:
- describe negocio y no implementación
- explicita actores y alcance
- deja visible qué queda fuera
- puede pasar a `wf-spec-analyze` sin arrastrar ambigüedades evitables

## Componentes

| Skill | Tipo | Rol |
|---|---|---|
| `kb-prd-expert` | Knowledge base | Reglas de qué debe y qué no debe contener un PRD |
| `kb-product-change-governance` | Knowledge base (cross-fase) | Reglas de gobernanza, clasificación y trazabilidad de cambios de producto. Vive aquí pero la cargan también los 4 agentes Spec. Instalar `sdd/spec/` sin esta kb deja a sus agentes sin reglas para distinguir gaps de change requests. Nota: `kb-prd-expert` también es cross-fase (la cargan `sdd-spec-explorer`, `sdd-spec-writer` y `sdd-spec-planner` para leer el PRD de entrada). |
| `prd-expert` | Agente worker | Ayuda a redactar, reorganizar y revisar PRDs con guía |
| `wf-prd-create` | Workflow | Genera un `prd.md` inicial a partir de notas o brief |
| `wf-prd-review` | Workflow | Revisión rápida de limpieza y procesabilidad antes de entrar en `spec` |
| `wf-prd-change` | Workflow | Formaliza un cambio de producto, actualiza PRD y deja trazabilidad en `product-changelog.md` y `changes/CR-XXX/` |

## Relación con el resto del pipeline

```text
PRD
  ↓ /wf-prd-create      (opcional, para redactar el documento)
  ↓ /wf-prd-review      (opcional, recomendado)
  ↓ /wf-spec-analyze    (obligatorio)
  ↓ /wf-spec-features-first
  ↓ /wf-prepare-plan
  ↓ /wf-prepare-tasks
```

`wf-prd-create` sirve para redactar el documento inicial. `wf-prd-review` no sustituye a `wf-spec-analyze`: solo revisa si el PRD está bien planteado antes de entrar en la fase Spec.

> Durante una ejecución concreta del pipeline, el PRD se trata como snapshot estable. Pero en producción el PRD sigue siendo la fuente de verdad de negocio. Si cambia el producto comprometido, usa `wf-prd-change`; si solo estás resolviendo una ambigüedad, usa `_analysis.md` y los workflows de spec correspondientes.

## Cuándo usar `wf-prd-change`

Usa `wf-prd-change` cuando la decisión ya no es una aclaración menor, sino un cambio real de producto. Ejemplos típicos:

- una capacidad pasa de fase futura a MVP
- una exclusión deja de ser válida
- cambia una regla de negocio transversal
- cambia qué actor puede ejecutar una capacidad
- una respuesta a un gap introduce una entidad persistente, un catálogo reutilizable o una nueva granularidad funcional no comprometida en el PRD

En esos casos, el orden correcto es:

```text
1. Actualizar PRD con /wf-prd-change
2. Medir impacto con /wf-prd-sync-impact
3. Resincronizar specs afectados con /wf-spec-sync-from-prd
```

## Estructura recomendada para cambios de producto

```text
prd/
├── PRD.md
├── product-changelog.md
└── changes/
    └── CR-001/
        ├── change-request.md
        └── decision.md
```

`product-changelog.md` resume el historial global. Cada carpeta `changes/CR-XXX/` agrupa el detalle operativo y evita repartir la semántica del cambio entre archivos sueltos en la raíz del PRD.
