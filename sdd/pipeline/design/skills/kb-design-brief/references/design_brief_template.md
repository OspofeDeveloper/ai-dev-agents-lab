# Template de DESIGN_BRIEF.md

```md
---
version: alpha
decision_mode: guided
autonomy_policy: strict-user-control
product_preset: fintech-trust
style_family: productive-minimal
secondary_family: none
density: medium
depth: low
typography_mode: utilitarian
color_energy: low
motion_level: low
clarity_vs_brand: clarity-first
reference_apps_policy: required
target_platforms:        # familias: mobile | web | desktop (iOS/Android ⇒ mobile)
  - mobile
accessibility_target: AA
voice_tone:
  formality: neutral
  expertise: mixto
  warmth: neutro
  playfulness: serio
---

# Design Brief

## Product Context

- **Producto**: <nombre o categoria>
- **Actor principal**: <quien usa la app>
- **Tarea dominante**: <que hace con mas frecuencia>
- **Riesgo si el diseno falla**: <confusion, baja conversion, errores operativos, etc.>

## Decision Model

- **Modo de trabajo**: <guided | hybrid | auto>
- **Policy de autonomia**: <strict-user-control | suggest-then-confirm | ai-default>
- **Quien decide las ambiguedades**: <usuario | IA con confirmacion | IA>

## Preset y Direccion Base

- **Preset**: <preset o none>
- **Familia visual**: <style_family>
- **Familia secundaria**: <secondary_family o none> — solo si refuerza sin mezclar direcciones incompatibles
- **Prioridad principal**: <clarity-first | balanced | brand-forward>
- **Motivo**: <por que esta direccion encaja con el producto>

## Visual Decisions

- **Density**: <low | medium | high> — <implicacion visible>
- **Depth**: <flat | low | medium | high> — <implicacion visible>
- **Typography mode**: <utilitarian | neutral-humanist | brand-forward | editorial> — <implicacion visible>
- **Color energy**: <low | medium | high> — <implicacion visible>
- **Motion level**: <none | low | medium> — <implicacion visible>

## Guardrails

- **Debe priorizar**:
  - <regla 1>
  - <regla 2>
- **Debe evitar**:
  - <anti-patron 1>
  - <anti-patron 2>

## Reference Apps Policy

- **Policy**: <required | preferred | optional>
- **Apps deseadas por el usuario**: <lista o N/A>
- **Notas de research**: <lista o N/A>

## Platforms & Accessibility

- **Target platforms**: <familias: mobile | web | desktop — iOS/Android ⇒ mobile; tablet es form-factor, no familia>
- **Accessibility target**: <AA | AAA>
- **Notas especiales**: <reduce motion especialmente importante, high contrast, etc.>

## Voice & Tone

Decision opcional pero recomendada. Si se omite, se hereda de la familia segun `kb-design-voice` Regla 2.

- **Formalidad**: <formal | neutral | cercano>
- **Expertise**: <tecnico | mixto | accesible>
- **Calidez**: <neutro | humano | calido>
- **Playfulness**: <serio | medido | ludico>
- **Politica de emojis**: <permitidos | restringidos | vetados>
- **Justificacion**: <por que esta voz encaja con el producto y el actor>

## Success Metrics

KPIs de UX que miden si el diseno funciona. Opcional pero recomendado: sin metricas, no se puede saber si el sistema es exitoso o solo bonito.

- **Task completion rate**: <% objetivo en flow critico> — ej. "85% completa el registro de cuenta sin abandono".
- **Error rate**: <% maximo aceptable> — ej. "< 5% de errores de validacion en checkout".
- **Time-on-task**: <segundos objetivo> — ej. "buscar y aplicar un filtro: < 8s".
- **Engagement** (si aplica): <retention D7, NPS, satisfaction score>.
- **A11y compliance**: <AA | AAA | metricas concretas como zero-violation en axe>.

Estas metricas no se miden en design directamente, pero su declaracion permite que cualquier `wf-design-delta` o `wf-design-feedback` se evalue contra ellas.

## Consistency Review

- **Conflictos detectados**: <ninguno o lista>
- **Resolucion**: <como se resolvieron>

## Inferencias automaticas

> Solo aplicable si el brief se cerro en `--mode auto`. En modos `guided` o `hybrid`, esta seccion se omite.

| Variable | Valor cerrado | Fuente | Justificacion breve |
|---|---|---|---|
| style_family | <valor> | spec \| PRD \| preset \| inferred | <razon> |
| secondary_family | <valor o none> | spec \| PRD \| preset \| inferred | <razon> |
| density | <valor> | spec \| PRD \| preset \| inferred | <razon> |
| depth | <valor> | spec \| PRD \| preset \| inferred | <razon> |
| typography_mode | <valor> | spec \| PRD \| preset \| inferred | <razon> |
| color_energy | <valor> | spec \| PRD \| preset \| inferred | <razon> |
| motion_level | <valor> | spec \| PRD \| preset \| inferred | <razon> |
| clarity_vs_brand | <valor> | spec \| PRD \| preset \| inferred | <razon> |
| reference_apps_policy | <valor> | spec \| PRD \| preset \| inferred | <razon> |
| accessibility_target | <valor> | spec \| PRD \| preset \| inferred | <razon> |

Las variables marcadas como `inferred` son las que mas conviene revisar manualmente: no tienen anclaje directo en spec, PRD ni preset.
```
