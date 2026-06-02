---
name: kb-design-expert
description: Skill raiz de la fase design del pipeline SDD. Define los principios estructurales que rigen toda la fase — separacion entre design y spec, niveles de artefactos producto vs feature, y orden de derivacion — y enruta a las KBs hermanas que contienen los contratos especificos. Activa en frases como "como esta organizada la fase design", "que produce design", "por donde empiezo el diseno", "que diferencia hay entre DESIGN.md y los artefactos de feature". No activa para reglas del contrato de DESIGN.md (kb-design-system-contract), artefactos de feature (kb-design-feature-artifacts) ni gobernanza/evolucion (kb-design-governance).
argument-hint: "(cargada automaticamente por workflows y agentes de design)"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Design Expert

Skill raiz de la fase `design`. Define los principios estructurales que rigen la traduccion de un Spec funcional validado a un contrato visual reusable por agentes y herramientas como Stitch.

Esta KB es deliberadamente delgada. Cubre solo los principios transversales que organizan la fase. El contrato del `DESIGN.md` y de los artefactos de feature vive en KBs hermanas:

- `kb-design-system-contract` — contrato normativo de `DESIGN.md` como artefacto de producto: formato Google design.md, frontmatter YAML obligatorio (visual_personality, color modes, type scale, components con estados), secciones canonicas y reglas de quoting.
- `kb-design-feature-artifacts` — contrato de los artefactos por feature: trazabilidad a journeys/CAs, `*_flows.md`, `*_views.md` con todos los estados aplicables, microcopy minimo y `*_ui_prompt.md` como ensamblaje para Stitch.
- `kb-design-governance` — gobernanza temporal del sistema visual: consumibilidad por plan, politica extender vs mutar al acumular features, versionado semver y distincion operativa entre `wf-design-intake`, `wf-design-delta`, `wf-design-branch` y `wf-design-variant`.
- `kb-design-brief` — contrato del `DESIGN_BRIEF.md`: modos, autonomia, presets y jerarquia de fuentes.
- `kb-a11y-expert` — criterios normativos de accesibilidad aplicables al sistema visual y a cada vista.

Esta KB define los tres principios que justifican esa separacion.

## Regla 1: La fase design no redefine el producto

`design` existe para decidir **como se presenta** una feature, no para cambiar **que hace**.

- El `*_spec.md` sigue siendo la fuente de verdad funcional.
- `DESIGN.md` define identidad visual, tokens y principios de interfaz.
- Los artefactos de feature (`*_flows.md`, `*_views.md`, `*_ui_prompt.md`) concretan pantallas y estados derivadas del spec.

Si una decision modifica historias, journeys, reglas de negocio o criterios de aceptacion, no pertenece a `design`: vuelve al `spec`.

El contrato de `DESIGN.md` como artefacto (formato, secciones obligatorias, frontmatter, estados de componentes, color modes, type scale, visual personality, reference apps) es SSoT de `kb-design-system-contract`.

El contrato de los artefactos por feature (trazabilidad, separacion flows/views/ui_prompt, estados de vista, microcopy) es SSoT de `kb-design-feature-artifacts`.

## Regla 2: El contrato visual se separa en producto y feature

La fase `design` produce dos niveles de artefactos. Esta separacion es estructural y gobierna todo lo demas:

### Nivel producto

- `DESIGN_BRIEF.md` — direccion visual base, policy de autonomia y tradeoffs antes de derivar el sistema visual. Contrato definido en `kb-design-brief`.
- `DESIGN.md` — identidad visual persistente y tokens del producto. Contrato definido en `kb-design-system-contract`.

### Nivel feature

- `<feature>_flows.md` — secuencia de pasos, precondiciones y transiciones de navegacion.
- `<feature>_views.md` — contrato canonico de pantallas, componentes, acciones y estados visuales.
- `<feature>_ui_prompt.md` — prompt final de ensamblaje para Stitch.

Las reglas de cada artefacto de feature (que debe contener, que no debe contener, como traza al spec, que estados declara) viven en `kb-design-feature-artifacts`.

La politica de evolucion temporal del nivel producto (extender vs mutar, versionado semver) y la consumibilidad por la fase `plan` viven en `kb-design-governance`.

## Regla 3: Direccion de producto primero, artefactos de feature despues

El orden correcto es:

1. cerrar `DESIGN_BRIEF.md` si hace falta
2. derivar o actualizar `DESIGN.md` a nivel producto
3. derivar flujos desde el spec
4. listar vistas y estados
5. componer el prompt para Stitch

Implicaciones:
- no empieces a derivar pantallas de feature sin haber fijado antes la direccion visual de producto
- no empieces por colores, gradientes o componentes de una pantalla si aun no esta cerrada su estructura funcional
- `DESIGN_BRIEF.md` y `DESIGN.md` pertenecen al nivel producto; `flows`, `views` y `ui_prompt` pertenecen al nivel feature

La distincion entre los workflows que tocan el sistema visual de forma incremental (`wf-design-intake`, `wf-design-delta`, `wf-design-branch`, `wf-design-variant`) y cuando usar cada uno vive en `kb-design-governance`.
