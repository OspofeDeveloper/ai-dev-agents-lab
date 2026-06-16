---
name: kb-design-brief
description: Base de conocimiento para capturar decisiones de direccion visual antes del DESIGN.md: contrato de DESIGN_BRIEF.md, modos de autonomia del usuario frente a la IA, presets de producto y validaciones de consistencia que reducen decisiones implicitas en la fase design.
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Design Brief

Eres la fuente de verdad para fijar las decisiones previas a la construccion del sistema visual de producto.

## Regla 1: El brief precede al sistema visual

Antes de generar o actualizar `DESIGN.md`, intenta cerrar primero un `DESIGN_BRIEF.md`.

`DESIGN_BRIEF.md` existe para decidir:
- que se quiere optimizar
- quien decide las ambiguedades
- que familia visual encaja mejor
- cuanta libertad tiene la IA para completar huecos

`DESIGN.md` materializa esas decisiones en tokens, componentes y guidance. No debe redefinir el brief.

## Regla 2: El brief es de producto, no de feature

Por defecto, `DESIGN_BRIEF.md` vive al mismo nivel que `DESIGN.md` y define direccion visual reutilizable para varias features.

Puede apoyarse en un feature spec para arrancar, pero sus decisiones son de producto:
- postura de marca
- claridad vs expresividad
- densidad
- motion
- plataformas objetivo
- target a11y
- policy de autonomia

No metas en el brief:
- navegacion vista por vista
- catalogo de componentes
- copy detallado de una pantalla
- layouts concretos por feature

→ Templates: `${CLAUDE_SKILL_DIR}/references/design_brief_template.md`

## Regla 3: Los modos de intake son cerrados

Todo workflow de intake debe operar en uno de estos modos:

- `guided`: el usuario responde las decisiones clave
- `hybrid`: la IA propone y el usuario confirma o corrige
- `auto`: la IA decide desde spec y PRD

No inventes modos adicionales.

## Regla 4: La policy de autonomia es explicita

Todo brief debe declarar `autonomy_policy` con uno de estos valores:

- `strict-user-control`: la IA no debe fijar decisiones ambiguas sin confirmacion
- `suggest-then-confirm`: la IA propone, pero el usuario retiene el cierre
- `ai-default`: la IA puede decidir salvo contradiccion clara

El modo de intake y la policy de autonomia deben ser coherentes:
- `guided` -> normalmente `strict-user-control`
- `hybrid` -> normalmente `suggest-then-confirm`
- `auto` -> normalmente `ai-default`

## Regla 5: El brief debe cerrar las variables operativas minimas

Todo `DESIGN_BRIEF.md` debe fijar, como minimo:
- `decision_mode`
- `autonomy_policy`
- `product_preset`
- `style_family`
- `secondary_family` (puede ser `none`)
- `density`
- `depth`
- `typography_mode`
- `color_energy`
- `motion_level`
- `clarity_vs_brand`
- `reference_apps_policy`
- `target_platforms`
- `accessibility_target`
- `voice_tone` (opcional pero recomendado; si se omite, hereda de la familia segun `kb-design-voice` Regla 2)

Si una de estas variables queda indefinida, debe marcarse como `DESIGN_GAP`.

## Regla 6: Los presets son aceleradores, no una segunda SSoT

Presets validos:
- `none`
- `b2b-operational`
- `consumer-lifestyle`
- `fintech-trust`
- `health-calm`
- `content-editorial`

El preset:
- acelera decisiones recurrentes
- propone defaults coherentes
- no sustituye la validacion contextual del producto real

`none` significa que no se aplica un preset y las variables se cierran campo a campo.

Si el preset contradice el spec o PRD, manda el producto real.

→ Templates: `${CLAUDE_SKILL_DIR}/references/design_presets.md`

## Regla 7: Claridad vs marca debe decidirse temprano

`clarity_vs_brand` expresa el tradeoff principal del sistema:
- `clarity-first`
- `balanced`
- `brand-forward`

Reglas:
- productos operativos, regulados o de alta precision -> `clarity-first`
- consumer con necesidad de diferenciacion -> `balanced` o `brand-forward`
- si hay conflicto entre legibilidad y expresividad, el brief debe resolverlo antes del `DESIGN.md`

## Regla 8: La policy de referencias tambien es explicita

`reference_apps_policy` debe ser uno de:
- `required`
- `preferred`
- `optional`

Interpretacion:
- `required`: sin research suficiente, no cierres `DESIGN.md`
- `preferred`: se puede continuar con gap documentado
- `optional`: solo usar referencias si aportan claridad real

## Regla 9: El brief debe validar consistencia antes de aprobarse

Antes de considerarlo listo, revisa contradicciones entre variables.

Ejemplos de conflicto:
- `style_family: productive-minimal` + `color_energy: high`
- `clarity_vs_brand: clarity-first` + `motion_level: medium` sin justificacion
- `health-calm` + `brand-forward` muy saturado
- `content-editorial` + `density: high`

Si hay conflicto, el brief debe:
- corregir la variable
- o documentar una justificacion breve y concreta

→ Templates: `${CLAUDE_SKILL_DIR}/references/consistency_checks.md`

## Regla 10: El brief gobierna al agente de design

Si existe `DESIGN_BRIEF.md`, el agente de design debe tratarlo como una fuente prioritaria para:
- familia visual
- autonomia permitida
- tradeoffs de claridad vs marca
- plataformas objetivo
- severidad a11y

Jerarquia de fuentes:
1. `DESIGN_BRIEF.md`
2. PRD
3. spec
4. research de referencias

Si `DESIGN.md` propuesto contradice el brief, manda el brief.
