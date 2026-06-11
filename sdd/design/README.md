# SDD Design — Prototipado visual entre Spec y Plan

Este directorio introduce la fase `design` del pipeline SDD. Su responsabilidad es transformar un `*_spec.md` validado en un contrato visual reutilizable por Stitch y en artefactos por feature que permitan validar flujos y vistas antes de entrar en el plan tecnico.

## Fit declarado

| | |
|---|---|
| **Para quién es** | Equipos sin diseñador dedicado; productos greenfield (el sistema visual nace aquí); prototipado **mobile** con Stitch y **web/desktop** con prompt de ensamblaje tool-agnostic (`target_tool: web-generic`, reutilizable por v0/Lovable/bolt o código a mano). a11y WCAG completa por plataforma: núcleo platform-neutral (`kb-a11y-expert`) + deltas web/desktop de puntero fino y teclado primario (`kb-a11y-web-expert`). Stitch ya no es el único destino |
| **Onramp brownfield** | UI ya en producción que no se va a rediseñar: `wf-design-extract` deriva el `DESIGN.md` por ingeniería inversa (CSS/tokens/componentes/capturas → `origin: extracted`, evidencia por token). Entrada alternativa a la fase, espejo de `wf-spec-from-code` en Spec |
| **Qué no cubre** | Integración Figma (import de variables / export de Figma Tokens) **fuera de alcance** por decisión ROADMAP 7.6 (2026-06-10): la fase apunta a equipos sin diseñador; destinos Stitch (mobile) y `web-generic`. Se reconsideraría solo si el fit se expandiera a equipos con diseñador propio (decisión de producto). Equipos con diseñador que ya produce specs visuales: pueden escribir `DESIGN.md` a mano respetando el contrato y auditarlo con `wf-design-validate` |
| **Cuándo saltarla** | Por proyecto: la fase es opcional en el init. Por feature: sin superficie de UI visible, Spec pasa a Plan directamente — la regla canónica de cuándo Design es obligatorio vive en `kb-plan-expert` y la aplica `wf-prepare-plan` |

Diagramas detallados de esta fase: [DIAGRAMS.md](DIAGRAMS.md).

## Objetivo de la fase

`design` no redefine producto ni implementacion. Su trabajo es cerrar:

- direccion visual y autonomia de decision del producto (intake)
- identidad visual persistente del producto con type scale, color modes, iconografia, motion catalog y voice & tone (sistema visual)
- inventario de vistas por feature con estados completos y microcopy
- secuencias y transiciones de interfaz
- contrato canonico de pantallas, componentes y estados visuales
- prompt estructurado de ensamblaje para Stitch
- mantenimiento del sistema en produccion (validacion continua, evolucion incremental, A/B, exploracion paralela)
- handoff al equipo de codigo (tokens exportables, auditoria a11y, feedback estructurado de stakeholders)

## Artefactos

### Producto

- `DESIGN_BRIEF.md` — SSoT previa de direccion visual y autonomia de decision. Incluye `voice_tone` y `Success Metrics`.
- `DESIGN.md` (versionado semver) — SSoT visual de producto: tokens (light + dark), type scale completa, componentes con todos sus estados, iconografia, motion catalog, voice & microcopy, accessibility. Puede tener `origin: extracted` (+ `evidence_base`, `evidence_coverage`) cuando se derivo por ingenieria inversa de una UI existente con `wf-design-extract`.
- `<producto>_design_extraction.md` — inventario crudo de la extraccion brownfield (paleta, tipografia, componentes y spacing observados con su evidencia y confianza). Gate humano de `wf-design-extract discover` antes de generar el `DESIGN.md`.
- `DESIGN.<branch>.md` — exploraciones paralelas del sistema visual sin tocar main.
- `_delta_analysis.md` — propuestas de cambio al sistema visual antes de aplicarlas.
- `tokens/` — tokens exportados a CSS, Style Dictionary, Compose, SwiftUI o Tailwind para handoff a codigo.
- `a11y_audit_<fecha>.md` — reportes persistidos de auditoria de accesibilidad.
- `<feature>_design_feedback.md` / `design_feedback_<fecha>.md` — feedback de stakeholders capturado y triajeado por categoria accionable.

### Por feature

- `<feature>_design_moodboard.md` — captura de inspiracion visual no estructurada (opcional, util para juniors).
- `<feature>_design_discovery.md` — research validado de apps de referencia (opcional, recomendado).
- `<feature>_flows.md` — secuencias, precondiciones y transiciones.
- `<feature>_views.md` — SSoT de pantallas con estados (default, loading, empty, error, partial, success) y microcopy minima.
- `<feature>_ui_prompt.md` — ensamblaje para Stitch a partir de brief, DESIGN.md, flows y views.
- `<feature>_variants.md` — A/B testing visual con hipotesis y metrica.
- `<feature>_views.<A|B>.md` / `<feature>_flows.<A|B>.md` — artefactos de cada variante en un A/B.

## Workflows disponibles

Los workflows se organizan en siete capas operativas. Detalle completo de pipelines y diagramas en [DIAGRAMS.md](DIAGRAMS.md).

### Inspiracion (opcional, anterior al intake)

```text
/wf-design-moodboard features/account/account_spec.md
```

Captura vibe, atmosfera, paleta intuitiva y referencias. Util para juniors o cuando la direccion visual no esta clara. Alimenta automaticamente al intake.

### Intake (gate del sistema visual)

```text
/wf-design-intake generate features/account/account_spec.md --mode hybrid [--preset b2b-operational] [--learn]
```

Cierra `DESIGN_BRIEF.md` con las 14 variables operativas. Detecta preset automaticamente desde spec/PRD. `--learn` activa modo enseñanza con explicaciones por decision. Si el brief ya existe, ofrece revisar / sobrescribir / cancelar.

### Discovery (opcional, recomendado)

```text
/wf-design-discover features/account/account_spec.md --brief DESIGN_BRIEF.md
```

Research validado de apps de referencia. Si no se ejecuta, `wf-design-system` hace research inline mas ligero.

### Generacion

```text
/wf-design-system generate features/account/account_spec.md --brief DESIGN_BRIEF.md
/wf-design-feature-prototype generate features/account/account_spec.md --brief DESIGN_BRIEF.md
```

`wf-design-system` arranca desde un starter kit del preset (al 70%) cuando aplica, no desde archivo en blanco. `wf-design-feature-prototype` deriva flows + views + ui_prompt aplicando `kb-design-conflict-expert` si hay otras features ya prototipadas.

Para una UI **ya en producción** (brownfield), en vez de generar desde el spec/brief:

```text
/wf-design-extract discover ./src/ui
/wf-design-extract generate ./src/ui
```

`wf-design-extract` deriva el `DESIGN.md` por ingeniería inversa con evidencia obligatoria por token (jerarquía: design tokens > CSS leído con `archivo:línea` > valor en componente > medición de captura > `[INFERIDO]`). Documenta las inconsistencias reales de la UI sin promediarlas (`[INCONSISTENTE]`); marca `origin: extracted` y `evidence_base: commit <SHA>`. `discover` se detiene en un gate humano para confirmar el inventario antes de generar. No exige spec validado ni `DESIGN_BRIEF.md`: es entrada alternativa a la fase. El `[INFERIDO]` no bloquea gates (la fase Design no sella mecánicamente): es informativo.

### Evolucion y validacion

```text
/wf-design-validate DESIGN.md --brief DESIGN_BRIEF.md [--views <views.md>] [--pedagogical]
/wf-design-delta analyze DESIGN.md --new-reqs cambios.md
/wf-design-delta apply DESIGN.md design_delta_analysis.md
```

`wf-design-validate` es estricto por defecto (`--lenient` para opt-out) y soporta modo `--pedagogical` para juniors. `wf-design-delta` aplica extensiones y mutaciones preservando lo previo, dejando rastro en `## Changelog` y haciendo bump semver.

### Exploracion y A/B

```text
/wf-design-branch create explorar-brand-forward
/wf-design-branch compare main explorar-brand-forward
/wf-design-branch merge explorar-brand-forward --into main

/wf-design-variant create features/checkout/checkout_spec.md --variants A,B --hypothesis "CTA mas prominente sube task completion"
/wf-design-variant compare features/checkout/checkout_variants.md
```

`branch` opera a nivel sistema; `variant` a nivel feature. Ninguno toca production hasta merge o aplicar ganador.

### Handoff y feedback

```text
/wf-design-export DESIGN.md --platforms css,style-dictionary,compose,swiftui
/wf-design-a11y-audit DESIGN.md --views features/checkout/checkout_views.md --brief DESIGN_BRIEF.md --target AA
/wf-design-feedback capture feedback_cliente.md --source cliente --feature features/checkout/checkout_spec.md
/wf-design-feedback triage features/checkout/checkout_design_feedback.md
```

`export` produce tokens consumibles por el equipo de codigo. `a11y-audit` verifica contraste real, touch targets, focus order y labels. `feedback` captura el comentario literal del stakeholder y lo triajea en una de siete categorias accionables.

## Pipeline canonico

```
spec validado
  -> wf-design-moodboard         (opcional)
  -> wf-design-intake             (gate: DESIGN_BRIEF.md)
  -> wf-design-discover           (opcional, recomendado)
  -> wf-design-system             (DESIGN.md desde starter kit del preset)
  -> wf-design-validate           (auditoria continua, estricto por defecto)
  -> wf-design-feature-prototype  (flows + views + ui_prompt por feature)
  -> wf-design-a11y-audit         (auditoria de accesibilidad)
  -> wf-design-export             (tokens a codigo)
  -> Stitch -> wf-prepare-plan
```

Loops de mantenimiento:
- Cambios en `DESIGN.md`: `wf-design-delta analyze` → revisar → `apply`.
- Exploraciones paralelas: `wf-design-branch`.
- A/B por feature: `wf-design-variant`.
- Feedback de cliente: `wf-design-feedback capture` → `triage` → workflow apropiado.

## Modos de uso por perfil

### Diseñador junior (acompanamiento maximo)

```text
/wf-design-moodboard features/X/X_spec.md          # captura inspiracion
/wf-design-intake generate features/X/X_spec.md --mode guided --learn    # arbol de decision con explicaciones
/wf-design-discover features/X/X_spec.md           # research validado
/wf-design-system generate features/X/X_spec.md    # starter kit del preset
/wf-design-validate DESIGN.md --pedagogical        # validacion con explicaciones
```

### Diseñador senior / PD Lead (eficiencia)

```text
/wf-design-intake generate features/X/X_spec.md --mode auto    # IA decide con trazabilidad
/wf-design-system generate features/X/X_spec.md
/wf-design-validate DESIGN.md
/wf-design-feature-prototype generate features/X/X_spec.md
/wf-design-export DESIGN.md --platforms style-dictionary
```

### Mantenimiento en produccion

```text
/wf-design-validate DESIGN.md                            # auditoria continua
/wf-design-delta analyze DESIGN.md --new-reqs cambios.md # cambios incrementales
/wf-design-a11y-audit DESIGN.md                          # auditoria a11y
/wf-design-feedback capture feedback.md                  # incorporar feedback estructurado
```

## Skills del dominio design

**Knowledge bases (kb-*)**:

- `kb-design-expert` — reglas de la fase `design`, estructura de `DESIGN.md` y artefactos de feature.
- `kb-design-brief` — contrato de `DESIGN_BRIEF.md`, modos de decision, presets, variables minimas y jerarquia de fuentes.
- `kb-design-style-taxonomy` — taxonomia visual: familias validas, escalas operativas, anti-patrones y regla escape `custom`.
- `kb-design-conflict-expert` — deteccion de conflictos visuales y de UX entre features.
- `kb-design-motion-expert` — catalogo operativo de motion: roles, durations, easing y micro-interacciones por componente.
- `kb-design-iconography-expert` — sistema de iconografia: libreria, stroke/fill, grid, tamanos por rol y semantica.
- `kb-design-voice` — UX writing: tono, estructura de errores, microcopy, glosario, politica de mayusculas y emojis.
- `kb-design-forms` — patrones de formulario: layout, validacion, estados de campo, multistep, autosave.
- `kb-design-layout` — sistema de layout y responsive: grid, breakpoints, adaptive vs responsive, safe areas.
- `kb-design-style-decision-tree` — arbol de decision navegable para junior: que familia, que clarity vs brand, etc.
- `kb-design-characterization` — metodologia de ingenieria inversa: extraer un `DESIGN.md` desde la UI existente con evidencia obligatoria por token, `[INFERIDO]`, inconsistencias documentadas sin promediar, header `origin: extracted`.
- `kb-a11y-expert` — criterios de accesibilidad mobile aplicados a design y plan.

**Workflows (wf-*)**:

- `wf-design-moodboard` — capa anterior al intake: captura inspiracion visual no estructurada (vibe, atmosfera, paleta intuitiva, referencias).
- `wf-design-intake` — cierra el `DESIGN_BRIEF.md` en modo `guided`, `hybrid` o `auto`. Acepta `--learn` para modo enseñanza con explicaciones extendidas.
- `wf-design-discover` — research interactivo de apps de referencia.
- `wf-design-system` — genera o actualiza `DESIGN.md` a nivel producto.
- `wf-design-extract` — deriva el `DESIGN.md` por ingenieria inversa de una UI ya en produccion (brownfield); modos `discover` (inventario con gate humano) y `generate`.
- `wf-design-validate` — audita `DESIGN.md` sin regenerar.
- `wf-design-delta` — evolucion incremental (`analyze` / `apply`) sobre `DESIGN.md`.
- `wf-design-branch` — explora variantes paralelas del sistema visual (`create | list | compare | merge | discard`).
- `wf-design-variant` — A/B testing visual a nivel de feature con hipotesis y metrica.
- `wf-design-export` — exporta tokens a CSS, Style Dictionary, Compose, SwiftUI o Tailwind.
- `wf-design-a11y-audit` — auditoria ejecutiva de a11y: contraste, touch targets, focus order, labels.
- `wf-design-feedback` — captura y triage de feedback de stakeholders (cliente, PM, dev, QA, Stitch).
- `wf-design-feature-prototype` — deriva `flows`, `views` y `ui_prompt` de una feature.

## Como extender el sistema

Catalogos cerrados (familias, presets, anti-patrones, voice axes, components) son SSoT. Cualquier extension respeta el principio de fuente unica.

### Anadir un preset de producto

- Editar `skills/kb-design-brief/references/design_presets.md` con la nueva entrada (defaults de las 14 variables + voice_tone).
- Anadir el starter kit base en `skills/kb-design-expert/references/preset_starter_kits.md` (frontmatter completo: color modes, type scale, motion catalog, iconografia, voice).
- Anadir los componentes especificos del preset en `skills/kb-design-expert/references/preset_components.md`.
- Anadir la heuristica de deteccion automatica en `kb-design-style-decision-tree` si aplica.
- No duplicar la descripcion del preset en `README` ni en `CLAUDE.md`.

### Anadir una familia visual nueva

- Editar `skills/kb-design-style-taxonomy/SKILL.md` Reglas 2-4 (definicion + implicaciones + criterios de seleccion) y Regla 11 ("cuando NO usar").
- Anadir ejemplo "bien vs mal" en `references/style_profile_examples.md`.
- Anadir motion base e iconography base sugeridos en Regla 3.
- Si rompe escalas existentes, tambien actualizar Reglas 8-10.

### Anadir un anti-patron visual

- Editar `skills/kb-design-style-taxonomy/SKILL.md` Regla 7.
- Si afecta a una familia concreta, mencionarlo en su Regla 2-4.

### Anadir un check de consistencia del brief

- Editar `skills/kb-design-brief/references/consistency_checks.md`.
- Si introduce una variable nueva, actualizar Regla 5 (variables operativas minimas) y el template del brief.

### Anadir reglas a las kbs especializadas

- **Motion**: editar `skills/kb-design-motion-expert/SKILL.md`.
- **Iconography**: editar `skills/kb-design-iconography-expert/SKILL.md`.
- **Voice & microcopy**: editar `skills/kb-design-voice/SKILL.md`.
- **Forms**: editar `skills/kb-design-forms/SKILL.md`.
- **Layout / responsive**: editar `skills/kb-design-layout/SKILL.md`.
- **Conflictos entre features**: editar `skills/kb-design-conflict-expert/SKILL.md`.
- **Accesibilidad**: editar `skills/kb-a11y-expert/SKILL.md`.

### Anadir un componente al starter kit de un preset

- Editar `skills/kb-design-expert/references/preset_components.md` con el componente y todos sus estados aplicables (Regla 7 de `kb-design-system-contract`).
- Actualizar `skills/kb-design-system-contract/references/component_anatomy_checklist.md` si introduce una tipologia nueva.

### Anadir un workflow nuevo

- Crear directorio `skills/wf-<nombre>/` con `SKILL.md`.
- Declarar precondiciones, argumentos, pasos y delegacion al agente si aplica.
- Anadirlo al rootmap de `CLAUDE.md` y a la seccion correspondiente del README.
- Si introduce un artefacto nuevo, anadirlo a "Artefactos" del README y al diagrama de contrato de artefactos en `DIAGRAMS.md`.

### Despues de cualquier extension

- Verificar que `references/design_brief_template.md` y `references/design_md_template.md` siguen coherentes.
- Confirmar que `wf-design-validate` cubre la nueva variable o regla (anadir un check si es necesario).
- Si afecta a tokens, verificar que `wf-design-export` los exporta correctamente a todas las plataformas.

## Reglas normativas

Las reglas operativas de esta fase viven en las kbs y son SSoT. Este README no redefine reglas: si una regla cambia, se edita en su kb correspondiente.

- **Direccion visual estructurada** (familias, escalas, anti-patrones, custom escape) → `kb-design-style-taxonomy`.
- **Modos de intake** (`guided | hybrid | auto`, `--learn`, deteccion automatica de preset) y **policy de autonomia** → `kb-design-brief`.
- **Arbol de decision para juniors** → `kb-design-style-decision-tree`.
- **Contrato de `DESIGN.md`**, trazabilidad a journeys/CAs, separacion producto/feature, estados de componente (Regla 16), type scale (Regla 17), color modes (Regla 18), estados de vista (Regla 19), versionado semver (Regla 22), branch vs delta vs intake (Regla 23) → `kb-design-expert`.
- **Motion** (roles, durations, easing, reduced-motion) → `kb-design-motion-expert`.
- **Iconografia** (libreria, stroke/fill, grid, tamanos por rol) → `kb-design-iconography-expert`.
- **UX writing y voice & tone** (ejes de voz, estructura de errores, microcopy por contexto, glosario, mayusculas y emojis) → `kb-design-voice`.
- **Patrones de formulario** (layout, validacion, estados de campo, multistep, autosave) → `kb-design-forms`.
- **Layout y responsive** (grid, breakpoints, adaptive vs responsive, safe areas, foldables) → `kb-design-layout`.
- **Conflictos visuales entre features** → `kb-design-conflict-expert`.
- **Accesibilidad mobile** (WCAG 2.2) → `kb-a11y-expert`.

## Nota sobre el formato de `DESIGN.md`

`DESIGN.md` sigue el formato abierto de Google: front matter YAML para tokens normativos y markdown para rationale. El linter `npx @google/design.md lint DESIGN.md` se ejecuta automaticamente al final de `wf-design-system` y `wf-design-delta apply`.

Estructura del frontmatter (Reglas 2, 3, 7, 8, 9 de `kb-design-system-contract` y Regla 3 de `kb-design-governance` para el versionado):

- `version: MAJOR.MINOR.PATCH` — semver del sistema visual.
- `visual_personality` — perfil estructurado (familia, escalas, adjectives, anti_patterns).
- `colors.light` + `colors.dark` (+ `high-contrast` opcional) — modo dark obligatorio.
- `typography` — type scale completa: display, h1-h3, body, body-sm, label, caption, code.
- `iconography` — libreria base unica, stroke/fill, grid, tamanos por rol.
- `motion` — level, reduced-motion policy, durations y easing por rol.
- `voice` — formality, expertise, warmth, playfulness, emoji_policy.
- `components` — cada componente con todos los estados aplicables (ver `skills/kb-design-system-contract/references/component_anatomy_checklist.md`).

Secciones markdown: `## Overview`, `## Visual Personality`, `## Colors`, `## Color Modes`, `## Typography`, `## Layout`, `## Elevation & Depth`, `## Shapes`, `## Components`, `## Iconography`, `## Accessibility`, `## Motion & Micro-interactions`, `## Reference Apps`, `## Voice & Microcopy`, `## Do's and Don'ts`, `## Changelog`.

Cuando el brief declara `product_preset` distinto de `none`, `wf-design-system` arranca desde el starter kit del preset (al 70%), no desde archivo en blanco. Starter kits viven en `skills/kb-design-expert/references/preset_starter_kits.md` y `preset_components.md`.
