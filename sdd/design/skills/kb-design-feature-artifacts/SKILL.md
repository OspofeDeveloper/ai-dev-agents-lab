---
name: kb-design-feature-artifacts
description: Contrato normativo de los artefactos de feature en la fase design — flows (secuencias, navegacion y transiciones), views (SSoT de pantallas con todos los estados aplicables: default, loading, empty, error, partial, success) y ui_prompt (ensamblaje para Stitch sin redefinir funcionalidad). Define trazabilidad obligatoria a journeys y CAs del spec, microcopy minimo por vista y delegaciones a kb-design-forms y kb-design-voice. SSoT extraida de kb-design-expert (Reglas 4, 7, 8, 9, 19, 20, 21).
argument-hint: "(cargada automaticamente por workflows y agentes de design)"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KB Design Feature Artifacts

Fuente de verdad del contrato de los artefactos de feature dentro de la fase `design`: `*_flows.md`, `*_views.md` y `*_ui_prompt.md`.

Esta KB no cubre el sistema visual de producto (`DESIGN.md`, `DESIGN_BRIEF.md`) — esa SSoT vive en `kb-design-expert` y `kb-design-brief`. Aqui se define como derivar pantallas, estados y prompts de ensamblaje a partir de un spec validado, sin reabrir decisiones funcionales ni redefinir el sistema visual.

## Regla 1: Cada vista debe trazar a journeys y CAs

Toda pantalla o dialogo debe existir porque un journey o un CA del spec lo exige.

Prueba de trazabilidad:
> "¿Que journey, HU o CA justifica esta vista?"

- Si hay trazabilidad clara, la vista esta justificada.
- Si no la hay, la vista es especulativa y no debe incluirse.

Esto incluye **condiciones de visibilidad y comportamiento condicional de elementos UI**: si el spec no dice explicitamente que un elemento debe ocultarse o mostrarse bajo cierta condicion, no introduzcas esa condicion en `*_views.md`. Las condiciones de UI no trazables al spec son comportamiento inventado.

## Regla 2: Los flows describen secuencia y navegacion, no el contrato visual

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

Los estados visuales viven en `*_views.md` (Regla 4).

Si el archivo incluye un mapa de navegacion consolidado al final, debe marcarse como derivado con la nota `> Derivado de las tablas de transiciones por flujo. La fuente normativa son dichas tablas.` Si hay conflicto entre el mapa y una tabla individual, manda la tabla del flujo individual.

→ Template: `/Users/oscar/Documents/GitHub/ai-dev-agents-lab/sdd/design/skills/kb-design-expert/references/feature_flows_template.md`

## Regla 3: Las views son la SSoT de la pantalla

`*_views.md` traduce journeys a pantallas concretas:
- nombre de vista
- objetivo
- actor
- origen funcional
- componentes obligatorios
- estados visuales (ver Regla 4)
- acciones primarias/secundarias
- notas de responsive y plataforma

Es el documento que evita prompts ambiguos tipo "haz una pantalla bonita de cuentas".
Si `flows` y `views` entran en conflicto sobre una pantalla concreta, manda `views` para todo lo relativo a composicion, estados y componentes.

Reglas adicionales para mantener `*_views.md` limpio:
- **Solo decisiones, no razonamientos**: cada campo normativo contiene la decision tomada. El razonamiento que llevo a elegir una variante de componente sobre otra no va inline; si es valioso preservarlo, usa un bloque `> Nota:` al final de la vista, separado de la definicion.
- **Dependencias cross-feature**: si una vista incluye elementos que pertenecen a otra feature (entidades, campos o estructuras definidas en otro spec), marcalos con `[Dependencia: F-XXX]`. La vista describe que existe el elemento, no define su estructura interna.

→ Template: `/Users/oscar/Documents/GitHub/ai-dev-agents-lab/sdd/design/skills/kb-design-expert/references/feature_views_template.md`

## Regla 4: Estados de vista declarados en `*_views.md`

Cada `*_views.md` debe declarar, por cada vista, los estados que aplican:

- `default` (con contenido normal cargado)
- `loading` (mientras se obtienen datos)
- `empty` (cuando no hay datos legitimos para mostrar)
- `error` (cuando la carga o accion fallo)
- `partial` (datos parciales o stale, si aplica)
- `success` (confirmacion de accion, si aplica)

Por cada estado declarado, especificar:

- decision visual (que componentes aparecen, que se oculta, color/copy)
- microcopy esperada (ver Regla 5; reglas de voz delegadas a `kb-design-voice`)
- accion principal (si la hay): en `empty`, suele ser "crear el primer item"; en `error`, "reintentar"; en `success`, "continuar" o cierre automatico.

Reglas:

1. Una vista sin `empty` ni `error` declarados es validable solo si el spec garantiza que esos estados no pueden ocurrir (caso raro).
2. `loading` que dura mas de 1s debe usar skeleton; menos, spinner inline.
3. `empty` no es "lista vacia" silenciosa: debe orientar al usuario sobre que hacer.
4. `error` no es "algo fallo": indica que paso, por que (si se sabe) y como recuperarse.

Anti-patron: vista que solo declara `default` y deja `loading`/`empty`/`error` a improvisacion de dev. Estos estados son el 30% del tiempo real de uso del producto.

## Regla 5: Cada vista declara microcopy minimo

Cada `*_views.md` debe declarar la microcopy critica de la vista: label de accion primaria, copy de empty state, copy de error tipico y copy de loading si lleva texto. Las reglas de voz, tono, estructura de errores y glosario son SSoT de `kb-design-voice` — esta regla solo obliga a documentar la microcopy, no a inventarla.

Implicacion:
- `wf-design-validate` marca como `[ALTO]` una vista que tenga empty state declarado sin copy.
- La voz no se redefine por vista; se hereda del `DESIGN.md`. Si una vista necesita desviar (raro), debe justificarse con `> Nota:`.

## Regla 6: Formularios delegan a `kb-design-forms`

Si una vista contiene un formulario, no redefinir patrones de form en `*_views.md`. La SSoT es `kb-design-forms`: layout (label/field/helper/error), validacion, estados de campo, multistep, autosave, conditional fields, file upload, submit.

La vista declara:
- Lista de campos en orden, con tipo, label, obligatoriedad y regla de validacion resumida.
- CTA primaria del form con copy concreto.
- Estados de form: editable, submitting, success, error.

Patrones de campo, errores y validacion se asumen segun `kb-design-forms`. Cualquier desviacion debe justificarse.

## Regla 7: El prompt para Stitch debe ensamblar, no volver a definir

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
- estados importantes (los declarados en Regla 4)
- consistencia visual
- ausencia de funcionalidades no descritas

No debe:
- volver a enumerar todos los componentes ya definidos en `*_views.md`
- duplicar microcopy extensa de dialogs o formularios
- convertirse en una segunda SSoT por pantalla
- repetir valores de tokens, nombres de componentes ni reglas de formato ya definidas en `DESIGN.md`. Si quieres recordarle a Stitch el uso de un componente o token concreto, citalos por nombre y remite a `DESIGN.md` como fuente; no copies sus valores dentro del prompt.

→ Template: `/Users/oscar/Documents/GitHub/ai-dev-agents-lab/sdd/design/skills/kb-design-expert/references/feature_ui_prompt_template.md`
