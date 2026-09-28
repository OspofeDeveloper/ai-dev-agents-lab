# [Feature Name]

> **Feature ID**: F-00X
> **Spec**: spec/[nombre]_spec.md
> **Actor principal**: [quién usa esta feature]
> **Spec monolítico origen**: [path/_spec.md]
> **PRD origen**: [path/al/PRD.md | N/A]
> **PRD version**: [1.0 | unknown | N/A]
> **Change ref**: [CR-XXX | N/A]
> **Status sync**: [in_sync | needs_review | stale | unknown]
> **Origen de alcance**: [PRD | PRD + analysis respondido | characterization (código, commit SHA)]
> **Avisos de gobernanza**: [ninguno | alcance derivado desde P-00X]

## Descripción

[Una frase describiendo el objetivo funcional de esta feature]

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | [ModeloX] | [Esta feature lo crea y gestiona] |
| Referencia | [ModeloY] | [Owner: F-00Z — nombre-feature] |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | spec/[nombre]_spec.md | ✓ |
| Plan | plan/[nombre]_plan.md | — |
| Tasks | tasks/[nombre]_tasks.md | — |

<!-- Si la feature usa layout plano legacy, omite los prefijos de subcarpeta (spec/, plan/, tasks/) en las rutas de este README. -->

## Dependencias

- **Requiere**: [la feature dueña de **cada** modelo compartido que este spec usa y no es suyo — o "Ninguna" solo si no usa ninguno]

<!-- "Requiere" se deriva de la tabla de Shared Models del spec, con la misma regla que aplica la
     medición de readiness: si usas un modelo cuyo dueño es otra feature, dependes de ella (D-100).
     No es "qué conviene implementar antes" a tu juicio. Dos features que se requieren entre sí es
     un ciclo real: déjalo escrito, que es lo que permite verlo antes del readiness. -->
- **Bloquea**: [feature(s) que dependen de esta — o "Ninguna"]
