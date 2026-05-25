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

Esto incluye **condiciones de visibilidad y comportamiento condicional de elementos UI**: si el spec no dice explicitamente que un elemento debe ocultarse o mostrarse bajo cierta condicion, no introduzcas esa condicion en `*_views.md`. Las condiciones de UI no trazables al spec son comportamiento inventado.

## Regla 5: Flujos primero, estilo despues

El orden correcto es:

1. derivar flujos desde el spec
2. listar vistas y estados
3. aplicar el sistema visual de `DESIGN.md`
4. componer el prompt para Stitch

No empieces por colores, gradientes o componentes si aun no esta cerrada la estructura de pantallas.

## Regla 6: DESIGN.md sigue el formato abierto de Google con orden estable

`DESIGN.md` sigue la especificacion oficial `@google/design.md`:
- **Front matter YAML**: tokens con tipos estrictos
- **Cuerpo markdown**: rationale y guidance en prose

Los tokens son los valores normativos. El markdown explica intencion, tono y reglas de aplicacion.

**Secciones canonicas** — deben aparecer en este orden exacto entre si:
- `## Overview`
- `## Colors`
- `## Typography`
- `## Layout`
- `## Elevation & Depth`
- `## Shapes`
- `## Components`
- `## Do's and Don'ts`

**Secciones custom** — el linter las preserva sin error; incluirlas en estas posiciones recomendadas:
- `## Visual Personality` → despues de `## Overview`, antes de `## Colors`
- `## Accessibility` → despues de `## Components`, antes de `## Motion & Micro-interactions`
- `## Motion & Micro-interactions` → despues de `## Accessibility`, antes de `## Reference Apps`
- `## Reference Apps` → despues de `## Motion`, antes de `## Do's and Don'ts`

**Token types validos:**
- `colors`: hex `"#RRGGBB"` en sRGB
- `typography`: objeto con `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`. Para cifras tabuladas usar `fontFeature: "tnum"` — **nunca `fontVariantNumeric`** (no es un campo valido del schema)
- `spacing` / `rounded`: strings con unidad (`"8px"`, `"1rem"`, `"0.875rem"`)
- `components`: propiedades estandar reconocidas por el linter: `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. Otras propiedades (`minHeight`, `borderColor`, `placeholderColor`, etc.) son toleradas pero generan warnings. Referencias con `{categoria.nombre}`.
- `visual_personality` / `motion` / `accessibility`: objetos libres — el linter los preserva sin validarlos. Pueden usar enteros, booleans y strings sin restriccion.

**Quoting obligatorio dentro de `components:`** — todos los valores dentro de `components:` deben ser **strings entrecomillados**, incluidos numericos como `fontWeight` o dimensiones. Un valor bare integer (ej. `fontWeight: 600`) hace crashear el linter con `raw.match is not a function`, porque internamente llama `.match()` a cada valor buscando referencias `{tokens.x}`. Correcto: `fontWeight: "600"`, `padding: "16px 24px"`, `minHeight: "48dp"`. Esta restriccion **solo aplica a `components:`**; los bloques top-level (`typography`, `accessibility`, etc.) pueden usar enteros/booleans bare sin problema.

Validar el resultado con `npx @google/design.md lint DESIGN.md`: cubre orden de secciones canonicas, referencias rotas, presencia de al menos un color primario y contraste WCAG AA en pares de color.

> Los criterios normativos de accesibilidad (contraste, touch targets, dynamic type, motion, focus, labels, anuncios live) viven en `kb-a11y-expert`. La seccion `## Accessibility` del `DESIGN.md` materializa esos criterios para el producto; no los redefine aqui.

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

Si el archivo incluye un mapa de navegacion consolidado al final, debe marcarse como derivado con la nota `> Derivado de las tablas de transiciones por flujo. La fuente normativa son dichas tablas.` Si hay conflicto entre el mapa y una tabla individual, manda la tabla del flujo individual.

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

Reglas adicionales para mantener `*_views.md` limpio:
- **Solo decisiones, no razonamientos**: cada campo normativo contiene la decision tomada. El razonamiento que llevo a elegir una variante de componente sobre otra no va inline; si es valioso preservarlo, usa un bloque `> Nota:` al final de la vista, separado de la definicion.
- **Dependencias cross-feature**: si una vista incluye elementos que pertenecen a otra feature (entidades, campos o estructuras definidas en otro spec), marcalos con `[Dependencia: F-XXX]`. La vista describe que existe el elemento, no define su estructura interna.

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
- repetir valores de tokens, nombres de componentes ni reglas de formato ya definidas en `DESIGN.md`. Si quieres recordarle a Stitch el uso de un componente o token concreto, citalos por nombre y remite a `DESIGN.md` como fuente; no copies sus valores dentro del prompt.

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
- decisiones a11y per-vista (focus order, labels de screen reader, anuncios live, hints), gobernadas por `kb-a11y-expert` y documentadas en `### Notas de accesibilidad` de cada vista

Si un detalle visual afecta a navegacion, validacion o estructura de estado, debe quedar escrito en `*_views.md`, no solo en Stitch.

## Regla 11: Visual Personality es obligatorio en todo DESIGN.md

`DESIGN.md` debe incluir la seccion `## Visual Personality` y su bloque `visual_personality:` en el frontmatter YAML. Sin esta seccion, el agente y Stitch no tienen un norte de caracter visual y el output es generico.

**En el frontmatter:**
```yaml
visual_personality:
  adjectives:
    - adjetivo_1: implicacion concreta en UI
    - adjetivo_2: implicacion concreta en UI
  anti_adjectives:
    - evitar_1
    - evitar_2
```

**En la seccion markdown:**
- 5-7 adjetivos de marca con su implicacion concreta en decisiones de UI (no basta listar el adjetivo sin la implicacion)
- 2-3 anti-adjetivos: lo que este sistema visual explicitamente NO es, con el comportamiento concreto a evitar

**Como derivar los adjetivos:**
- Del PRD: nombre del producto, vision, audiencia objetivo y diferenciadores
- Del spec: contexto de uso (frecuencia, urgencia, tipo de datos), tipo de tarea del actor

Si no hay PRD disponible, derivar desde el spec: un spec de finanzas personales con foco en velocidad operativa y legibilidad numerica conduce a adjetivos como "utilitario", "confiable", "veloz". Un spec de fitness con gamificacion conduce a "energetico", "motivador", "visual".

## Regla 12: Reference Apps es obligatorio en todo DESIGN.md

`DESIGN.md` debe incluir la seccion `## Reference Apps` con 3-5 apps reales del mercado en la misma categoria de producto.

**Formato de cada referencia:**
- Nombre de la app
- Aspecto concreto a tomar (no solo el nombre): densidad, paleta, tipografia, componentes, micro-interacciones
- Por que es relevante para este producto concreto

Las referencias se obtienen via web research en el `wf-design-system` antes de delegar al agente. Si no hay research disponible, marcar la seccion con `[DESIGN_GAP: investigar apps de referencia en la categoria <nombre_categoria>]` en lugar de inventar referencias.

Un DESIGN.md sin Reference Apps obliga a Stitch a generar el estilo sin norte → resultado amateur. Una referencia concreta ("tomar de Revolut la densidad de informacion en listas y la tipografia numerica prominente") guia al generador hacia decisiones profesionales.
