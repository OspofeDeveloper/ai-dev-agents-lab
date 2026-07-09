---
name: kb-design-governance
description: Gobernanza temporal del sistema visual del producto. Define el contrato de handoff de DESIGN.md a plan-architect, la politica extender vs mutar al acumular features, el versionado semver del sistema visual, la distincion operativa entre wf-design-intake/delta/branch/variant y el ciclo de confianza de direccion (provisional → confirmed). SSoT de kb-design-expert Reglas 10, 15, 22 y 23.
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Design Governance

Eres la fuente de verdad para la gobernanza del sistema visual a lo largo del tiempo: como se entrega a la fase plan, como se hace evolucionar sin romper consumidores, como se versiona y que workflow usar segun la naturaleza del cambio.

Esta KB no redefine el contrato visual ni el formato del `DESIGN.md` (eso vive en `kb-design-system-contract`). Cubre exclusivamente la dimension temporal y operativa del sistema visual.

## Regla 1: La salida de design debe ser consumible por plan

La fase `plan` no debe depender del prototipo visual en si, pero si del contrato aprobado.

Por eso `design` debe dejar explicitado:
- pantallas requeridas
- componentes interactivos clave
- formularios y campos
- estados especiales
- navegacion entre vistas
- decisiones visuales que impactan arquitectura UI
- decisiones a11y per-vista (focus order, labels de screen reader, anuncios live, hints), gobernadas por `kb-a11y-expert` y documentadas en `### Notas de accesibilidad` de cada vista

Si un detalle visual afecta a navegacion, validacion o estructura de estado, debe quedar escrito en `*_views.md`, no solo en el prompt de ensamblaje (Stitch u otro generador de UI).

`plan-architect` carga esta KB cross-fase para conocer que campos del `DESIGN.md` y de los `*_views.md` puede tratar como contrato estable al derivar el plan tecnico.

## Regla 2: Politica de evolucion del sistema visual

`DESIGN.md` es de producto y persistente. Cuando llega una segunda feature (o sucesivas), el sistema visual se acumula, no se reescribe.

Distincion obligatoria:

- **Extender**: anadir tokens, componentes o estados nuevos que no existian. Esta permitido siempre que no choquen con los existentes. La regeneracion via `wf-design-system` debe preservar lo previo.
- **Mutar**: cambiar valor de un token, redefinir un componente o eliminar una decision ya escrita. Requiere proceso explicito.

Reglas de mutacion:

1. Una regeneracion via `wf-design-system` **no debe mutar tokens existentes silenciosamente**. Si detecta una mutacion necesaria (ej. el nuevo feature obliga a un radio mayor por accesibilidad), debe marcarla como `DESIGN_GAP` y proponerla en el rationale.
2. Las mutaciones intencionales se canalizan via `wf-design-delta analyze | apply`, no por regeneracion completa.
3. Si el `DESIGN_BRIEF.md` cambia (cambia `style_family`, `clarity_vs_brand`, etc.), eso es un cambio de **brief**, no un delta del sistema: se canaliza via `wf-design-intake` (ver Regla 4). Solo la rematerializacion posterior del `DESIGN.md`, ya con el brief nuevo, pasa por `wf-design-delta`. Cambiar `style_family`/`clarity_vs_brand` directamente con `delta` rompe la trazabilidad (anti-patron, ver Regla 4).
4. Toda mutacion aplicada debe dejar traza en la seccion `## Changelog` del `DESIGN.md` con `[feature: <id>] <que cambio y por que>`.

Anti-patron: regenerar `DESIGN.md` con una segunda feature como spec de entrada y dejar que el agente "actualice" valores sin avisar. El cliente pierde la trazabilidad y los componentes implementados rompen.

## Regla 3: Versionado semver del DESIGN.md

`DESIGN.md` lleva en el frontmatter un campo `version: MAJOR.MINOR.PATCH` que sigue semver adaptado al sistema visual:

- **MAJOR**: cambio que rompe trazabilidad o impacto visual significativo:
  - cambia `style_family` o `secondary_family`
  - cambia `clarity_vs_brand`
  - cambia color primary, accent o esquema de modos (introducir dark mode donde no existia, eliminar light, etc.)
  - elimina componentes ya en uso
  - cambia tipografia principal
- **MINOR**: extension compatible:
  - anade tokens nuevos sin tocar existentes
  - anade componentes nuevos
  - anade estados a componentes existentes
  - amplia type scale con nuevos roles
  - anade modo de color (high-contrast donde no existia)
- **PATCH**: ajuste fino sin impacto en consumidores:
  - corrige valores de spacing en componentes
  - actualiza copy de `Do's and Don'ts`
  - corrige referencias rotas en tokens
  - ajusta easing curves manteniendo el rol
  - corrige errores tipograficos en el rationale

Reglas de version:

1. Toda regeneracion via `wf-design-system` o `wf-design-delta apply` debe actualizar la version segun el tipo de cambio mayor detectado.
2. `wf-design-delta analyze` determina el version bump en su propuesta; el usuario puede sobreescribirlo en `apply`.
3. La version en el frontmatter debe coincidir con la del ultimo entry de `## Changelog`.
4. `wf-design-export` registra la version en el manifest de tokens para que el repo de codigo pueda detectar drift.

Anti-patron: bumpear PATCH cuando se rompio trazabilidad. El equipo de codigo confiara en semver para decidir si su build necesita ajustes; si mientes con la version, romperas su CI.

## Regla 4: Branch, delta e intake no son intercambiables

Tres workflows tocan el sistema visual de forma incremental, cada uno con su proposito. No mezclar.

- **`wf-design-intake`** se usa cuando cambian variables del **brief**: `style_family`, `clarity_vs_brand`, `voice_tone`, `autonomy_policy`, `target_platforms`, `accessibility_target`. Implica que la direccion del producto se redefine y todo lo que viene aguas abajo (DESIGN.md, views, ui_prompt) debe revisarse.
- **`wf-design-delta`** se usa cuando cambian **tokens, componentes o secciones del DESIGN.md** sin tocar el brief. La direccion del producto se mantiene; solo se ajusta como se materializa. Mutaciones requieren `analyze` + `apply` para preservar trazabilidad y bump de version coherente.
- **`wf-design-branch`** se usa cuando se quiere **explorar** una variante sin comprometer `DESIGN.md`. La exploracion puede terminar mergeando, descartandose o quedando viva como referencia. No es production-ready hasta merge.
- **`wf-design-variant`** se usa cuando se quieren **comparar A/B** variantes de una feature concreta, no del sistema completo. Una variant es feature-scoped; un branch es system-scoped.

Decision tree:
- ¿Cambia el brief? → `wf-design-intake`.
- ¿Cambia el sistema visual sin tocar brief? → `wf-design-delta`.
- ¿Quiero explorar sin tocar production? → `wf-design-branch`.
- ¿Quiero A/B una feature concreta? → `wf-design-variant`.

Anti-patrones:
- Usar `branch` para evitar `intake` cuando el brief debe cambiar (acabas con branches que en realidad son productos distintos).
- Usar `delta` para introducir cambios que rompen `style_family` (eso es brief, no delta; resultado: trazabilidad rota).
- Usar `variant` para experimentar funcionalidad (eso es spec, no design).

## Regla 5: Ciclo de vida de la confianza de direccion (provisional → confirmed)

Un `DESIGN.md` puede nacer con una direccion visual **no anclada**: `style_family`, paleta primaria/accent y `motion_level` inferidos sin fuente humana fiable. Es invencion plausible con formato de autoridad, y el ecosistema la marca como tal hasta que un humano la confirme.

Los **valores validos** del frontmatter (`origin: generated-provisional`, `direction_confidence: provisional|confirmed`) y su semantica son SSoT de `kb-design-system-contract` Regla 10. Esta regla gobierna su **transicion temporal**: que la dispara, quien la escribe y quien la limpia.

**Cuando nace provisional (en el origen — `wf-design-system`):** la direccion esta no anclada cuando se cumple cualquiera de estas condiciones:
- se invoco con `--no-brief` (`brief_override: true`), o
- el brief resuelto se cerro en modo `auto` con `autonomy_policy: ai-default` (`kb-design-brief` Reglas 3 y 4) sin confirmacion humana, y/o
- el research de Reference Apps fue pobre o ausente (mismo criterio que marca `DESIGN_GAP` en Reference Apps, `kb-design-system-contract` Regla 4).

Con la direccion no anclada, `wf-design-system` **pide confirmacion humana explicita** antes de escribir (presenta `style_family`, paleta primaria/accent y `motion_level` inferidos):
- **confirmada** → nace `origin: generated`, `direction_confidence: confirmed`. Sin sello provisional.
- **no confirmada, o sin interaccion** (headless/CI) → nace `origin: generated-provisional`, `direction_confidence: provisional`; los campos de direccion inferidos sin evidencia se marcan `[INFERIDO]`; la entrada de `## Changelog` refleja el estado provisional. **Sin interaccion el camino por defecto es escribir provisional, no abortar**: el sello es informativo y no rompe el pipeline aguas abajo.

**Quien promueve provisional → confirmed (al validar — `wf-design-validate`):** la promocion **no es mecanica** (la fase Design no tiene script ni sellador). Es **juicio humano confirmado**. Cuando `wf-design-validate` detecta `direction_confidence: provisional` y la auditoria de direccion pasa, pide confirmacion explicita al usuario; **solo si confirma**:
1. promueve `origin: generated-provisional → generated` y `direction_confidence: provisional → confirmed`,
2. limpia los marcadores `[INFERIDO]` de los campos de direccion ya confirmados,
3. añade una entrada a `## Changelog` registrando la confirmacion.

Esta es la **unica edicion** que `wf-design-validate` hace del documento — acotada y gated por confirmacion (mismo patron que la confirmacion de `[ASUNCIÓN]` en `wf-prd-review`). Si el usuario **no confirma**, el `DESIGN.md` permanece provisional y validate **no toca el archivo** (sigue siendo read-only en ese camino).

**Quien NO promueve:** ni el agente por su cuenta, ni una regeneracion silenciosa, ni `wf-design-delta`. La promocion exige confirmacion humana explicita; autoaprobarla es el mismo fallo que inventar la direccion.

**Traza en `## Changelog`:** tanto el nacimiento provisional como la promocion dejan entrada (`[direccion: provisional]` / `[direccion: confirmada]`), coherente con la Regla 2 (toda mutacion deja traza). La promocion de `provisional → confirmed` que no toca tokens es un cambio **PATCH** de version (Regla 3): no rompe trazabilidad ni cambia valores visuales, solo eleva la confianza declarada.

Anti-patron: tratar `generated-provisional` como un estado final comodo. Es un punto de partida a remontar — la direccion sigue sin validar y el equipo de codigo no debe confiar en ella hasta `confirmed`.
