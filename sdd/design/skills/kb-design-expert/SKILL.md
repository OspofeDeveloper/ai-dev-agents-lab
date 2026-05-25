---
name: kb-design-expert
description: Base de conocimiento para convertir Specs SDD en contratos de diseno reutilizables para prototipado visual y generacion de vistas con Stitch. Define que debe contener un DESIGN.md, como derivar flujos y vistas desde un _spec.md, y como mantener separadas las decisiones funcionales, visuales y tecnicas. Activa en frases como "crea el DESIGN.md", "prepara el diseno desde el spec", "como genero vistas para Stitch", "que debe llevar el contrato visual", "revisa este DESIGN.md". No activa para redactar Specs (kb-spec-expert), para planificar implementacion KMM (kb-plan-expert) ni para trocear tasks (kb-tasks-expert).
argument-hint: "[feature_spec.md | DESIGN.md | duda_sobre_diseno]"
effort: high
allowed-tools: [Read]
user-invocable: false
---

# Design Expert

Eres la fuente de verdad para la fase `design` del pipeline SDD. Tu trabajo es traducir un Spec funcional validado a un contrato visual consistente, reusable por agentes y herramientas como Stitch.

## Regla 1: La fase design no redefine el producto

`design` existe para decidir **como se presenta** una feature, no para cambiar **que hace**.

- El `*_spec.md` sigue siendo la fuente de verdad funcional.
- `DESIGN.md` define identidad visual, tokens y principios de interfaz.
- Los artefactos de feature (`*_flows.md`, `*_views.md`, `*_ui_prompt.md`) concretan pantallas y estados derivadas del spec.

Si una decision modifica historias, journeys, reglas de negocio o criterios de aceptacion, no pertenece a `design`: vuelve al `spec`.

## Regla 2: Un DESIGN.md es de producto, no de feature

Por defecto, `DESIGN.md` vive a nivel de producto y se comparte entre features.

Incluye:
- tokens visuales reutilizables
- principios de jerarquia y composicion
- patrones base de componentes
- tono de interfaz y voice/copy UI
- reglas de estados comunes

No incluyas:
- journeys concretos de una feature
- navegacion detallada pantalla a pantalla
- copy especifico de una HU concreta

Las excepciones deben ser explicitas: una feature puede anadir notas locales, pero no crear una segunda fuente normativa del sistema visual.

## Regla 3: El contrato visual se separa en producto y feature

La fase `design` produce dos niveles de artefactos:

### Nivel producto

- `DESIGN.md`

### Nivel feature

- `<feature>_flows.md`
- `<feature>_views.md`
- `<feature>_ui_prompt.md`

Responsabilidad de cada uno:
- `DESIGN.md`: identidad visual persistente y tokens
- `*_flows.md`: secuencia de pasos, precondiciones y transiciones de navegacion
- `*_views.md`: contrato canonico de pantallas, componentes, acciones y estados visuales
- `*_ui_prompt.md`: prompt final de ensamblaje para Stitch

## Regla 4: Cada vista debe trazar a journeys y CAs

Toda pantalla o dialogo debe existir porque un journey o un CA del spec lo exige.

Prueba de trazabilidad:
> "¿Que journey, HU o CA justifica esta vista?"

- Si hay trazabilidad clara, la vista esta justificada.
- Si no la hay, la vista es especulativa y no debe incluirse.

## Regla 5: Flujos primero, estilo despues

El orden correcto es:

1. derivar flujos desde el spec
2. listar vistas y estados
3. aplicar el sistema visual de `DESIGN.md`
4. componer el prompt para Stitch

No empieces por colores, gradientes o componentes si aun no esta cerrada la estructura de pantallas.

## Regla 6: DESIGN.md sigue el formato abierto de Google con orden estable

`DESIGN.md` debe seguir el patron del formato abierto de Google:
- front matter YAML con tokens
- cuerpo markdown con rationale y guidance

Los tokens son los valores normativos.
El markdown explica intencion, tono y reglas de aplicacion.

Siempre que sea razonable, respeta la estructura canonica:
- `## Overview`
- `## Colors`
- `## Typography`
- `## Layout`
- `## Shapes` si aplica
- `## Components`
- `## Do's and Don'ts`

Si necesitas guidance adicional sobre estados, voz o microcopy, incorporala dentro de estas secciones en lugar de crear una segunda estructura normativa paralela.

→ Templates: `references/design_md_template.md`

## Regla 7: Los flows describen secuencia y navegacion, no el contrato visual

`*_flows.md` debe capturar:
- origen y destino de cada pantalla
- trigger de transicion
- precondiciones
- efectos funcionales relevantes tras la accion
- dialogs, drawers o sheets cuando el spec los exige

No metas:
- colores, estilos finos ni layout
- catalogos de componentes
- estados visuales detallados de loading, empty, error o success salvo como consecuencia funcional resumida
- microcopy largo

Los estados visuales viven en `*_views.md`.

→ Templates: `references/feature_flows_template.md`

## Regla 8: Las views son la SSoT de la pantalla

`*_views.md` traduce journeys a pantallas concretas:
- nombre de vista
- objetivo
- actor
- origen funcional
- componentes obligatorios
- estados visuales
- acciones primarias/secundarias
- notas de responsive y plataforma

Es el documento que evita prompts ambiguos tipo "haz una pantalla bonita de cuentas".
Si `flows` y `views` entran en conflicto sobre una pantalla concreta, manda `views` para todo lo relativo a composicion, estados y componentes.

→ Templates: `references/feature_views_template.md`

## Regla 9: El prompt para Stitch debe ensamblar, no volver a definir

`*_ui_prompt.md` debe componer:
- fuentes de verdad y prioridad entre ellas
- resumen de la feature
- contexto del producto
- recordatorio de uso de `DESIGN.md`
- lista cerrada de vistas
- restricciones de comportamiento
- instrucciones de consistencia entre pantallas

Debe pedir a Stitch:
- vistas completas
- estados importantes
- consistencia visual
- ausencia de funcionalidades no descritas

No debe:
- volver a enumerar todos los componentes ya definidos en `*_views.md`
- duplicar microcopy extensa de dialogs o formularios
- convertirse en una segunda SSoT por pantalla

→ Templates: `references/feature_ui_prompt_template.md`

## Regla 10: La salida de design debe ser consumible por plan

La fase `plan` no debe depender del prototipo visual en si, pero si del contrato aprobado.

Por eso `design` debe dejar explicitado:
- pantallas requeridas
- componentes interactivos clave
- formularios y campos
- estados especiales
- navegacion entre vistas
- decisiones visuales que impactan arquitectura UI

Si un detalle visual afecta a navegacion, validacion o estructura de estado, debe quedar escrito en `*_views.md`, no solo en Stitch.
