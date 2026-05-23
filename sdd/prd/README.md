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
| `prd-expert` | Agente worker | Ayuda a redactar, reorganizar y revisar PRDs con guía |
| `wf-prd-create` | Workflow | Genera un `prd.md` inicial a partir de notas o brief |
| `wf-prd-review` | Workflow | Revisión rápida de limpieza y procesabilidad antes de entrar en `spec` |

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

> Tras pasar a la fase Spec, **el PRD se congela**. Las decisiones de negocio que los Specs necesitan (gaps `[P-XXX]` detectados por `wf-spec-analyze`) se anotan en el `_analysis.md`, no en el PRD. La única condición que justifica volver a editar el PRD es contaminación técnica detectada (veredicto `REQUIERE_LIMPIEZA_PRD` del analyze).
