---
name: kb-design-expert
description: Base de conocimiento para convertir Specs SDD en contratos de diseno reutilizables para prototipado visual y generacion de vistas con Stitch. Define que debe contener un DESIGN.md, como derivar flujos y vistas desde un _spec.md, y como mantener separadas las decisiones funcionales, visuales y tecnicas. Activa en frases como "crea el DESIGN.md", "prepara el diseno desde el spec", "como genero vistas para Stitch", "que debe llevar el contrato visual", "revisa este DESIGN.md". No activa para redactar Specs (kb-spec-expert), para planificar implementacion KMM (kb-plan-expert) ni para trocear tasks (kb-tasks-expert).
argument-hint: "(cargada automaticamente por workflows y agentes de design)"
effort: low
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

- `DESIGN_BRIEF.md`
- `DESIGN.md`

### Nivel feature

- `<feature>_flows.md`
- `<feature>_views.md`
- `<feature>_ui_prompt.md`

Responsabilidad de cada uno:
- `DESIGN_BRIEF.md`: direccion visual base, policy de autonomia y tradeoffs antes de derivar el sistema visual
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

## Regla 5: Direccion de producto primero, artefactos de feature despues

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
- `## Reference Apps` → despues de `## Motion`, antes de `## Voice & Microcopy`
- `## Voice & Microcopy` → despues de `## Reference Apps`, antes de `## Do's and Don'ts`

**Token types validos:**
- `colors`: hex `"#RRGGBB"` en sRGB
- `typography`: objeto con `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`. Para cifras tabuladas usar `fontFeature: "tnum"` — **nunca `fontVariantNumeric`** (no es un campo valido del schema)
- `spacing` / `rounded`: strings con unidad (`"8px"`, `"1rem"`, `"0.875rem"`)
- `components`: propiedades estandar reconocidas por el linter: `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. Otras propiedades (`minHeight`, `borderColor`, `placeholderColor`, etc.) son toleradas pero generan warnings. Referencias con `{categoria.nombre}`.
- `visual_personality` / `motion` / `accessibility`: objetos libres — el linter los preserva sin validarlos. Pueden usar enteros, booleans y strings sin restriccion.

**Quoting obligatorio dentro de `components:`** — todos los valores dentro de `components:` deben ser **strings entrecomillados**, incluidos numericos como `fontWeight` o dimensiones. Un valor bare integer (ej. `fontWeight: 600`) hace crashear el linter con `raw.match is not a function`, porque internamente llama `.match()` a cada valor buscando referencias `{tokens.x}`. Correcto: `fontWeight: "600"`, `padding: "16px 24px"`, `minHeight: "48dp"`. Esta restriccion **solo aplica a `components:`**; los bloques top-level (`typography`, `accessibility`, etc.) pueden usar enteros/booleans bare sin problema.

Validar el resultado con `npx @google/design.md lint DESIGN.md`: cubre orden de secciones canonicas, referencias rotas, presencia de al menos un color primario y contraste WCAG AA en pares de color.

> Los criterios normativos de accesibilidad (contraste, touch targets, dynamic type, motion, focus, labels, anuncios live) viven en `kb-a11y-expert`. La seccion `## Accessibility` del `DESIGN.md` materializa esos criterios para el producto; no los redefine aqui.

→ Templates: `${CLAUDE_SKILL_DIR}/references/design_md_template.md`

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

→ Templates: `${CLAUDE_SKILL_DIR}/references/feature_flows_template.md`

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

→ Templates: `${CLAUDE_SKILL_DIR}/references/feature_views_template.md`

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

→ Templates: `${CLAUDE_SKILL_DIR}/references/feature_ui_prompt_template.md`

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

## Regla 11: Visual Personality es obligatorio y estructurado en todo DESIGN.md

`DESIGN.md` debe incluir la seccion `## Visual Personality` y su bloque `visual_personality:` en el frontmatter YAML. Sin esta seccion, el agente y Stitch no tienen un norte de caracter visual y el output es generico.

La eleccion de estilo se rige por `kb-design-style-taxonomy`. No uses etiquetas vagas como unica decision normativa.

**En el frontmatter:**
```yaml
visual_personality:
  style_family: productive-minimal
  secondary_family: depth-material
  density: medium
  depth: low
  typography_mode: utilitarian
  color_energy: low
  motion_level: low
  adjectives:
    - adjetivo_1: implicacion concreta en UI
    - adjetivo_2: implicacion concreta en UI
  anti_patterns:
    - evitar_1
    - evitar_2
```

Campos:
- `style_family`: familia principal cerrada, elegida segun `kb-design-style-taxonomy`
- `secondary_family`: opcional, solo si ayuda a matizar sin mezclar direcciones incompatibles
- `density`, `depth`, `typography_mode`, `color_energy`, `motion_level`: usar exclusivamente los valores validos y reglas de `kb-design-style-taxonomy`
- `adjectives`: 5-7 adjetivos con implicacion concreta
- `anti_patterns`: 2-4 resultados visuales a evitar

**En la seccion markdown:**
- 5-7 adjetivos de marca con su implicacion concreta en decisiones de UI (no basta listar el adjetivo sin la implicacion)
- 2-4 anti-patrones: lo que este sistema visual explicitamente NO es, con el comportamiento concreto a evitar
- explicacion breve de por que la `style_family` elegida encaja con el producto, actor y tarea dominante

**Como derivar los adjetivos:**
- Del PRD: nombre del producto, vision, audiencia objetivo y diferenciadores
- Del spec: contexto de uso (frecuencia, urgencia, tipo de datos), tipo de tarea del actor

Si no hay PRD disponible, derivar desde el spec: un spec de finanzas personales con foco en velocidad operativa y legibilidad numerica conduce a una familia `productive-minimal` con `typography_mode: utilitarian`. Un spec de fitness con gamificacion suele conducir a `expressive-modern` con `color_energy: high` y `motion_level: medium`.

## Regla 12: Reference Apps es obligatorio en todo DESIGN.md

`DESIGN.md` debe incluir la seccion `## Reference Apps` con 3-5 apps reales del mercado en la misma categoria de producto.

**Formato de cada referencia:**
- Nombre de la app
- Aspecto concreto a tomar (no solo el nombre): densidad, paleta, tipografia, componentes, micro-interacciones
- Por que es relevante para este producto concreto

Las referencias se obtienen via web research en el `wf-design-system` antes de delegar al agente. Si no hay research disponible, marcar la seccion con `[DESIGN_GAP: investigar apps de referencia en la categoria <nombre_categoria>]` en lugar de inventar referencias.

Un DESIGN.md sin Reference Apps obliga a Stitch a generar el estilo sin norte → resultado amateur. Una referencia concreta ("tomar de Revolut la densidad de informacion en listas y la tipografia numerica prominente") guia al generador hacia decisiones profesionales.

## Regla 13: Selecciona una familia de estilo antes de derivar tokens

Antes de elegir colores, tipografia, radios o componentes, decide la familia visual base siguiendo `kb-design-style-taxonomy`.

Orden correcto:
1. contexto de producto y actor
2. `style_family` y perfil estructurado de `visual_personality`
3. apps de referencia
4. tokens y componentes

Si el documento salta directamente a tokens sin haber fijado `style_family`, la direccion visual queda infraespecificada y tendera a lo generico.

## Regla 14: DESIGN.md materializa el brief, no lo reabre

Cuando exista `DESIGN_BRIEF.md`, `DESIGN.md` debe materializar sus decisiones cerradas. No reabras variables ya fijadas en el brief salvo contradiccion clara con spec o PRD.

La jerarquia de fuentes y el listado de variables gobernadas por el brief son SSoT de `kb-design-brief` Regla 10. Cuando aqui se diga "el brief manda", se entiende segun esa regla.

Implicacion practica para el agente:
- Si `DESIGN.md` propuesto contradice el brief, el agente lo corrige antes de escribir.
- Si la contradiccion procede del spec o el PRD, el agente la senala como `DESIGN_GAP` en lugar de decidir unilateralmente.

## Regla 15: Politica de evolucion del sistema visual

`DESIGN.md` es de producto y persistente. Cuando llega una segunda feature (o sucesivas), el sistema visual se acumula, no se reescribe.

Distincion obligatoria:

- **Extender**: anadir tokens, componentes o estados nuevos que no existian. Esta permitido siempre que no choquen con los existentes. La regeneracion via `wf-design-system` debe preservar lo previo.
- **Mutar**: cambiar valor de un token, redefinir un componente o eliminar una decision ya escrita. Requiere proceso explicito.

Reglas de mutacion:

1. Una regeneracion via `wf-design-system` **no debe mutar tokens existentes silenciosamente**. Si detecta una mutacion necesaria (ej. el nuevo feature obliga a un radio mayor por accesibilidad), debe marcarla como `DESIGN_GAP` y proponerla en el rationale.
2. Las mutaciones intencionales se canalizan via `wf-design-delta analyze | apply`, no por regeneracion completa.
3. Si el `DESIGN_BRIEF.md` cambia (cambia `style_family`, `clarity_vs_brand`, etc.), eso es por definicion una mutacion del sistema: usar `wf-design-delta` y documentar la razon.
4. Toda mutacion aplicada debe dejar traza en la seccion `## Changelog` del `DESIGN.md` con `[feature: <id>] <que cambio y por que>`.

Anti-patron: regenerar `DESIGN.md` con una segunda feature como spec de entrada y dejar que el agente "actualice" valores sin avisar. El cliente pierde la trazabilidad y los componentes implementados rompen.

## Regla 16: Componentes deben declarar todos los estados aplicables

Cualquier componente interactivo declarado en `DESIGN.md` o referenciado en `*_views.md` debe enumerar todos los estados que aplican a su tipologia. Esta es la causa mas comun de regresiones visuales en dev.

Estados base por tipo:

- **Interactivos (button, link, tab, toggle, checkbox, radio, switch)**: `default`, `hover` (solo si target_platforms incluye Web/desktop), `focus-visible`, `active` (pressed), `disabled`, `loading` (si aplica accion async), `selected` (si aplica multi-estado).
- **Inputs (text-input, textarea, select, date-picker, file-picker)**: `default`, `focus`, `filled`, `valid`, `invalid`, `disabled`, `read-only`. Adicionales: `loading` si valida async.
- **Contenedores con estado (card, list-item, accordion)**: `default`, `hover` (si interactivo), `selected`, `disabled`, `loading`, `expanded`/`collapsed` (si aplica).
- **Indicadores (badge, tag, chip)**: `default`, `selected`, `removable` (si aplica), `disabled`.
- **Vistas grandes (page, sheet, modal, drawer)**: `entering`, `default`, `exiting`. Para pantallas con datos: ver Regla 19.

Reglas comunes:

1. Si un estado aplica al componente segun esta tabla y no se declara, `wf-design-validate` lo marca como `[ALTO]`.
2. Cada estado declarado debe tener decisiones visuales concretas (color, opacity, border, motion). Estado sin decision es decoracion vacia.
3. La omision intencional de un estado (`disabled` no aplica porque el boton siempre esta activo en esa vista) debe documentarse con `# N/A: <razon>`.

Anti-patron: declarar solo `default` y dejar que dev "improvise" los demas. El producto saldra inconsistente.

## Regla 17: Type scale completa y obligatoria

`DESIGN.md` debe declarar una type scale completa en el frontmatter YAML, no solo `font-family`. Sin scale, cada feature inventa sus tamanos.

Roles minimos obligatorios:

- `display`: tamano hero (40-72px segun densidad), uso en empty states, landing, milestones.
- `h1`/`h2`/`h3`: jerarquia de pantalla. Como minimo dos niveles, idealmente tres.
- `body`: texto base de lectura (14-17px segun densidad).
- `body-sm`: secundario (12-14px).
- `label`: etiquetas de campo, botones, tags (11-13px, normalmente medium weight).
- `caption`: metadata, helper text (10-12px).
- `code` (si aplica): tipografia monoespaciada para contenido tecnico.

Cada rol declara:

- `size` (px o rem)
- `line-height` (numero o px)
- `font-weight` (numerico: 400, 500, 600, 700)
- `letter-spacing` (px, normalmente negativo en displays grandes y positivo en labels)
- `text-transform` si aplica (uppercase en labels operativos, none en el resto)

`typography_mode` del brief sugiere la familia de fuentes y el peso base:

- `utilitarian`: family Inter/IBM Plex/SF Pro, weight base 400, labels en 500.
- `neutral-humanist`: family Inter/Geist/SF Pro, contrastes de peso suaves.
- `brand-forward`: dos fuentes (display custom + body neutral), pesos contrastados.
- `editorial`: serif para display y h1-h2, sans para body.

Anti-patron: declarar solo "tipografia Inter 16px" y permitir que cada vista invente jerarquia. El producto pierde jerarquia visual.

## Regla 18: Color modes declarados

`DESIGN.md` debe declarar al menos modo `light` y modo `dark`. El modo `high-contrast` es opcional pero recomendado si `accessibility_target: AAA`.

Estructura de tokens de color en el frontmatter:

```yaml
colors:
  light:
    background: <token o valor>
    surface: <token o valor>
    surface-elevated: <token o valor>
    on-background: <texto sobre background>
    on-surface: <texto sobre surface>
    primary: <token o valor>
    on-primary: <texto sobre primary>
    border: <token o valor>
    success: <token o valor>
    warning: <token o valor>
    error: <token o valor>
    info: <token o valor>
  dark:
    background: <...>
    surface: <...>
    # ... mismas claves que light
```

Reglas:

1. Cada token de color en `light` tiene su equivalente en `dark`. Faltar uno es `DESIGN_GAP`.
2. Cada par foreground/background (ej. `on-primary` sobre `primary`) cumple el ratio de contraste del `accessibility_target` del brief. Esto lo verifica `wf-design-a11y-audit`.
3. Modo `dark` no es invertir colores literalmente: redefine surface, on-surface y elevation para preservar legibilidad. Usar superficies cercanas a negro puro (#0E0E10) en lugar de #000 plano.
4. La politica de seleccion de modo (automatica via system, manual via toggle, fija) se documenta en `## Color Modes` del markdown.

Anti-patron: declarar solo `light` y dejar dark mode como "lo hara el dev". Resultado: dark mode roto en produccion.

## Regla 19: Estados de vista declarados en `*_views.md`

Cada `*_views.md` debe declarar, por cada vista, los estados que aplican:

- `default` (con contenido normal cargado)
- `loading` (mientras se obtienen datos)
- `empty` (cuando no hay datos legitimos para mostrar)
- `error` (cuando la carga o accion fallo)
- `partial` (datos parciales o stale, si aplica)
- `success` (confirmacion de accion, si aplica)

Por cada estado declarado, especificar:

- decision visual (que componentes aparecen, que se oculta, color/copy)
- microcopy esperada (delegada a `kb-design-voice` cuando este disponible)
- accion principal (si la hay): en `empty`, suele ser "crear el primer item"; en `error`, "reintentar"; en `success`, "continuar" o cierre automatico.

Reglas:

1. Una vista sin `empty` ni `error` declarados es validable solo si el spec garantiza que esos estados no pueden ocurrir (caso raro).
2. `loading` que dura mas de 1s debe usar skeleton; menos, spinner inline.
3. `empty` no es "lista vacia" silenciosa: debe orientar al usuario sobre que hacer.
4. `error` no es "algo fallo": indica que paso, por que (si se sabe) y como recuperarse.

Anti-patron: vista que solo declara `default` y deja `loading`/`empty`/`error` a improvisacion de dev. Estos estados son el 30% del tiempo real de uso del producto.

## Regla 20: Cada vista declara microcopy minimo

Cada `*_views.md` debe declarar la microcopy critica de la vista: label de accion primaria, copy de empty state, copy de error tipico y copy de loading si lleva texto. Las reglas de voz, tono, estructura de errores y glosario son SSoT de `kb-design-voice` — esta regla solo obliga a documentar la microcopy, no a inventarla.

Implicacion:
- `wf-design-validate` marca como `[ALTO]` una vista que tenga empty state declarado sin copy.
- La voz no se redefine por vista; se hereda del `DESIGN.md`. Si una vista necesita desviar (raro), debe justificarse con `> Nota:`.

## Regla 21: Formularios delegan a `kb-design-forms`

Si una vista contiene un formulario, no redefinir patrones de form en `*_views.md`. La SSoT es `kb-design-forms`: layout (label/field/helper/error), validacion, estados de campo, multistep, autosave, conditional fields, file upload, submit.

La vista declara:
- Lista de campos en orden, con tipo, label, obligatoriedad y regla de validacion resumida.
- CTA primaria del form con copy concreto.
- Estados de form: editable, submitting, success, error.

Patrones de campo, errores y validacion se asumen segun `kb-design-forms`. Cualquier desviacion debe justificarse.

## Regla 22: Versionado semver del DESIGN.md

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

## Regla 23: Branch, delta e intake no son intercambiables

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
