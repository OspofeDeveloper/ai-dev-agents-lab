# Design Lab — Guía de la fase Design

Este directorio define un paquete focalizado en la etapa de **Design** dentro del pipeline SDD: cierre del brief visual del producto, sistema visual persistente, derivacion de flows y views por feature, y preparacion del handoff al generador de UI (Stitch en mobile, generadores web en web/desktop) antes de entrar en Plan.

> **Audiencia.** El **hilo principal (orquestador)** enruta la petición del usuario al workflow o agente correcto — el enrutado efectivo lo hacen las `description` de los skills (eager) y la regla eager `sdd-routing.md`. Un **subagente especialista** (p. ej. `design-system-architect`) también carga esta guía al tocar artefactos de Design: para él es **contexto de fase**, no una instrucción de rol — su contrato de trabajo es su propio system prompt + sus `kb-*`.

> **Precondiciones, desambiguación y fronteras de esta fase** (spec validado + brief como entrada, onramp brownfield, saltable por feature, y las desambiguaciones críticas intake/delta/branch/variant) viven en la regla **eager** `sdd-routing.md`, para que el hilo principal las tenga al orientar sin tocar ficheros.

## Fit de esta fase (para quien es y para quien no)

Esta fase esta disenada para un encaje concreto. Declararlo evita falsas expectativas:

- **Para quien ES**: equipos **sin disenador dedicado** que necesitan un contrato visual consistente; productos **greenfield** (el sistema visual nace aqui); prototipado **mobile** con Stitch y **web/desktop** con prompt de ensamblaje tool-agnostic (`target_tool: web-generic`, reutilizable por v0/Lovable/bolt o codigo a mano). Soporta a11y **WCAG completa por plataforma**: nucleo platform-neutral (`kb-a11y-expert`) mas los deltas web/desktop de puntero fino y teclado primario (`kb-a11y-web-expert`), auditables con `/wf-design-a11y-audit`. Stitch sigue siendo el destino mobile, pero ya no es el unico.
- **Escala y multiplataforma ([[D-011]])**: ademas del caso greenfield sin disenador, la fase cubre **equipos con funcion de diseno dedicada** y **escala multi-repo** — un repo de diseno SSoT propio (topologia `design`) que comparten varias superficies/productos, con **divergencia multi-plataforma nativa** (Android Material vs iOS HIG, phone/tablet) modelada como **base ⊕ override per-view** (`kb-design-feature-artifacts` Regla 8) + capa de mapeo de componente por plataforma en el `DESIGN.md` (`kb-design-system-contract` Regla 11), consumida por los repos de codigo en **solo lectura** (`design_source` + resolucion determinista `sdd-design-resolve.py`; drift cross-repo via `sdd-source-drift.py`). Es **aditivo**: el flujo greenfield no cambia.
- **Onramp brownfield**: si la UI **ya existe en produccion** y no se va a rediseñar, el `DESIGN.md` se deriva por ingenieria inversa con `/wf-design-extract` (CSS/tokens/componentes/capturas → `DESIGN.md` con `origin: extracted` y evidencia por token). Es la entrada ALTERNATIVA a la fase (no exige spec ni brief), espejo de `/wf-spec-from-code` en Spec. El `DESIGN.md` extraido fluye como cualquier otro: auditable (`wf-design-validate`), evolucionable (`wf-design-delta`), exportable (`wf-design-export`).
- **Lo que NO cubre**: integracion con Figma (ni import de variables ni export de Figma Tokens) sigue **fuera de alcance** (decision ROADMAP 7.6, 2026-06-10); sus destinos son Stitch (mobile) y `web-generic` (web/desktop). **Actualizacion [[D-011]] (2026-06-18):** el fit ya **se expandio** a equipos con diseno dedicado / escala multi-repo, asi que la condicion que 7.6 puso para reconsiderar Figma («que el fit se expandiera a equipos con disenador propio») **queda satisfecha** — pero reabrir Figma es una decision de producto **separada y aun no tomada**; hasta entonces, fuera. Un equipo con disenador que ya produce sus propios specs visuales puede ademas escribir el `DESIGN.md` a mano respetando el contrato (`kb-design-system-contract`) y auditarlo con `/wf-design-validate`.
- **Es saltable**: por proyecto (la fase es opcional en el init) y **por feature** — una feature sin superficie de UI visible pasa de Spec a Plan directamente. La regla canonica de cuando Design es obligatorio vive en `kb-plan-expert` y la aplica `wf-prepare-plan`; esta fase no fuerza su propio uso.

## Precondiciones por workflow (referencia)

| Workflow | Spec validado | DESIGN_BRIEF.md | DESIGN.md |
|---|---|---|---|
| `wf-design-moodboard` | si | no | no |
| `wf-design-intake` | si | no (lo genera) | no |
| `wf-design-discover` | si | recomendado | no |
| `wf-design-system` | si | si (gate) | opcional (lo crea o actualiza) |
| `wf-design-extract` | no (entrada alternativa) | no | no (lo crea) |
| `wf-design-validate` | no | recomendado | si |
| `wf-design-delta` | no | si (gate) | si |
| `wf-design-branch` | no | no | si |
| `wf-design-variant` | si | si | si |
| `wf-design-feature-prototype` | si | si (gate) | si |
| `wf-design-export` | no | no | si |
| `wf-design-sync` | no (los lee) | recomendado | si |
| `wf-design-a11y-audit` | no | recomendado | si |
| `wf-design-feedback capture` | no | no | no |
| `wf-design-feedback triage` | no | recomendado (contexto) | recomendado |

## Camino canonico (pipeline recomendado)

Para un producto desde cero hasta dev-ready:

```
spec validado
  -> wf-design-moodboard      (opcional, util para juniors o cuando el direccion visual no esta clara)
  -> wf-design-intake          (gate: produce DESIGN_BRIEF.md; soporta --learn)
  -> wf-design-discover        (opcional, recomendado: research validado de apps)
  -> wf-design-system          (genera DESIGN.md desde starter kit del preset)
  -> wf-design-validate        (auditoria continua; estricto por defecto)
  -> wf-design-feature-prototype (deriva flows/views/ui_prompt por feature)
  -> wf-design-a11y-audit      (auditoria especifica de accesibilidad)
  -> wf-design-export          (handoff a codigo: CSS, Style Dictionary, Compose, SwiftUI, Tailwind)
  -> Stitch -> wf-prepare-plan
  -> wf-plan-validate
```

**Camino minimo (equipos pequenos / modo ligero):** de los tres workflows pre-`DESIGN.md`, solo `wf-design-intake` es gate obligatorio. `wf-design-moodboard` y `wf-design-discover` son aceleradores opt-in (moodboard especialmente util para juniors o direccion no clara); pueden omitirse sin penalizacion. Aguas abajo, `wf-design-system` → `wf-design-feature-prototype` no cambia. La pareja `wf-design-branch` (sistema completo) / `wf-design-variant` (feature concreta) cubre propositos distintos y no se solapa; su desambiguacion canonica vive en `kb-design-governance` Regla 4 (branch/delta/intake/variant).

Loops de mantenimiento:
- Cambios en `DESIGN.md`: `wf-design-delta analyze` → revisar → `apply`.
- Exploraciones paralelas sin tocar production: `wf-design-branch create`.
- A/B por feature: `wf-design-variant create`.
- Feedback de stakeholders: `wf-design-feedback capture` → `triage` → workflow apropiado.

## Modo enseñanza para diseñadores junior

Si la persona que pide tiene poca experiencia, o pide explicitamente acompanamiento ("explicame por que", "soy nuevo en esto"), activar:

- `wf-design-intake --mode guided --learn`: arbol de decision navegable con explicaciones por pregunta.
- Sugerir `wf-design-moodboard` antes del intake para capturar inspiracion no estructurada.
- `wf-design-validate --pedagogical`: hallazgos con explicacion extendida y referencia a regla concreta.

Cargado por defecto si el hilo principal detecta dudas conceptuales repetidas en una misma sesion.

## Skills de conocimiento Design

Las `kb-*` viven en el frontmatter `skills: [...]` de los agentes de la fase; el harness las inyecta en el contexto del subagente. El hilo principal no las consulta ni necesita su inventario: vive en `sdd/meta/skill-registry.md` (mapa humano: el `README.md` de la fase). Las dependencias cross-fase (`kb-spec-expert`) las resuelve `install.sh design` automáticamente.

El contrato de cada artefacto (`flows`, `views`, `ui_prompt`), la jerarquia de fuentes y las reglas de direccion visual viven en las kbs (`kb-design-expert`, `kb-design-brief`, `kb-design-style-taxonomy`). No las redefinas aqui.

## Nota sobre `DESIGN.md`

El contrato normativo de `DESIGN.md` (estructura del frontmatter YAML, secciones markdown obligatorias, presets y starter kits) vive en `kb-design-system-contract`. Las reglas de gobernanza del artefacto (versioning, ownership, gate de validacion) viven en `kb-design-governance`. No redefinas esas reglas aqui.
