---
name: kb-design-feature-artifacts
description: Contrato normativo de los artefactos de feature en la fase design — flows (secuencias, navegacion y transiciones), views (SSoT de pantallas con todos los estados aplicables: default, loading, empty, error, partial, success) y ui_prompt (ensamblaje tool-agnostic sin redefinir funcionalidad; SSoT de target_tool stitch|web-generic y target_platforms). Define trazabilidad obligatoria a journeys y CAs del spec, microcopy minimo por vista y delegaciones a kb-design-forms y kb-design-voice. SSoT extraida de kb-design-expert (Reglas 4, 7, 8, 9, 19, 20, 21).
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KB Design Feature Artifacts

Fuente de verdad del contrato de los artefactos de feature dentro de la fase `design`: `*_flows.md`, `*_views.md` y `*_ui_prompt.md`.

Esta KB no cubre el sistema visual de producto (`DESIGN.md`, `DESIGN_BRIEF.md`) — esa SSoT vive en `kb-design-system-contract` (contrato del `DESIGN.md`) y `kb-design-brief` (brief). Aqui se define como derivar pantallas, estados y prompts de ensamblaje a partir de un spec validado, sin reabrir decisiones funcionales ni redefinir el sistema visual.

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

→ Template: `${CLAUDE_SKILL_DIR}/references/feature_flows_template.md`

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

→ Template: `${CLAUDE_SKILL_DIR}/references/feature_views_template.md`

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

## Regla 7: El prompt de ensamblaje debe ensamblar, no volver a definir

`*_ui_prompt.md` es un prompt de ensamblaje **tool-agnostic**: ensambla las fuentes de verdad para que un generador de UI produzca las vistas, sin volver a definir lo que ya vive en `DESIGN.md` y `*_views.md`. El generador concreto se declara, no se asume.

### Target del prompt (`target_tool` y `target_platforms`) — SSoT

Esta KB es la única fuente de verdad de la noción de target del `ui_prompt`. El template y `wf-design-feature-prototype` la consumen; no la redefinen.

- **`target_tool`**: declara la herramienta de ensamblaje destino. Valores:
  - `stitch` — prompt para Google Stitch, destino de prototipado **mobile** (formato histórico, no se degrada).
  - `web-generic` — prompt de ensamblaje **web reutilizable** por v0, Lovable, bolt, otros generadores web, o código a mano. Describe componentes en términos de HTML semántico/ARIA, breakpoints responsive y estados, sin jerga propietaria.
- **`target_platforms`**: en cada archivo de salida es **una superficie** (`mobile` | `desktop` | `web`). El producto puede cubrir varias (lo declara `accessibility.target_platforms` del `DESIGN.md`); en ese caso se genera **un `ui_prompt` por superficie**, no uno mezclado.

Selección de `target_tool` según la superficie:
- `mobile` → `stitch`.
- `web` o `desktop` → `web-generic`.

**Multi-superficie (producto que cubre varias plataformas).** Cuando `accessibility.target_platforms` del `DESIGN.md` incluye más de una familia (p. ej. `[mobile, web]`), NO se produce un prompt ambiguo ni se "elige una": se genera **un prompt especializado por superficie**, nombrado con sufijo de superficie:
- `<feature>_ui_prompt.mobile.md` → `target_tool: stitch`, `target_platforms: mobile`
- `<feature>_ui_prompt.web.md` → `target_tool: web-generic`, `target_platforms: web`
- (`desktop` se cubre con `web-generic` salvo que el stack imponga otra cosa; documéntalo en el prompt)

Si el producto cubre una sola superficie, se genera un único `<feature>_ui_prompt.md` (sin sufijo). Los `*_flows.md` y `*_views.md` son por defecto **una sola copia agnóstica de superficie** con `### Notas responsive` cuando aplica: la divergencia *responsive* por superficie (tamaño/orientación) se resuelve en el ensamblaje del `ui_prompt`, no en los flows/views. La divergencia **real por design target** (componentes nativos Android/iOS, layout tablet) sí se materializa en flows/views, pero como **override per-view sobre la base agnóstica**, nunca duplicando la copia entera — ver **Regla 8**.

El cuerpo del prompt es común a cualquier target (fuentes de verdad, vistas, restricciones); solo cambia el **vocabulario de componentes y estados** según `target_tool`.

### Estructura común (cualquier `target_tool`)

`*_ui_prompt.md` debe componer:
- `target_tool` y `target_platforms` declarados explícitamente
- fuentes de verdad y prioridad entre ellas
- resumen de la feature
- contexto del producto
- recordatorio de uso de `DESIGN.md`
- lista cerrada de vistas
- restricciones de comportamiento
- instrucciones de consistencia entre pantallas

Debe pedir al generador de UI:
- vistas completas
- estados importantes (los declarados en Regla 4); en `web-generic`, cubrir explícitamente loading/empty/error/focus/hover/disabled
- consistencia visual
- ausencia de funcionalidades no descritas

No debe:
- volver a enumerar todos los componentes ya definidos en `*_views.md`
- duplicar microcopy extensa de dialogs o formularios
- convertirse en una segunda SSoT por pantalla
- repetir valores de tokens, nombres de componentes ni reglas de formato ya definidas en `DESIGN.md`. Si quieres recordarle al generador el uso de un componente o token concreto, citalos por nombre y remite a `DESIGN.md` como fuente; no copies sus valores dentro del prompt.

### Especialización por `target_tool`

- **`stitch`** (mobile): mantiene el formato y la jerga del prompt Stitch actual. No degradar.
- **`web-generic`** (web/desktop): componentes en términos de **HTML semántico y ARIA** (no widgets propietarios), **breakpoints responsive**, y estados completos (loading/empty/error/focus/hover/disabled). La accesibilidad web la gobierna `kb-a11y-web-expert`; el prompt remite a ella, no la recopia.

→ Template: `${CLAUDE_SKILL_DIR}/references/feature_ui_prompt_template.md`

## Regla 8: Divergencia por design target — base agnóstica + override per-view ([[D-011]])

Por defecto, `*_flows.md` y `*_views.md` son **una sola base agnóstica** de superficie (Regla 7). Cuando un producto diverge de verdad por **design target** —el caso de la topología `design` de D-011: componentes nativos Android Material vs iOS HIG, o layout phone/tablet— esa divergencia se modela como **base + override per-view**, **nunca** forkeando la copia entera ni metiendo condicionales de plataforma inline en la base.

**Grano del override: la vista entera (per-view).** La unidad de override es la vista (el átomo de `*_views.md`, Regla 3); `flows` igual cuando cambia la navegación. La resolución para un consumidor es **`base ⊕ override(target)`**, determinista:

- si el target tiene override de una vista → esa vista **gana completa**;
- si no lo tiene → **hereda la base intacta**.

Un target sin directorio de override hereda toda la base (el caso común: un producto con un único target `mobile` no tiene `targets/`). Solo se materializa lo que diverge — **no se duplica lo idéntico**.

**Per-component se descarta.** `*_views.md` es markdown en prosa, no un árbol de componentes con IDs estables; fusionar prosa componente-a-componente no es determinista. La especificidad de **componente nativo** (Material vs HIG, patrón de navegación) es un asunto de **sistema**, no de la vista: vive en la capa de mapeo de componente por plataforma del `DESIGN.md` (`kb-design-system-contract`). La vista se mantiene agnóstica y solo se overridea por **layout/composición** (p. ej. master-detail en tablet). **Per-state** queda como refinamiento futuro opt-in: solo si el uso real muestra una vista que diverge en un único estado y re-enunciarla molesta.

**Layout** (los overrides cuelgan de la base, no la sustituyen):
```
<feature>_flows.md            # base agnóstica
<feature>_views.md            # base agnóstica
<feature>_ui_prompt.<surface>.md
targets/<design-target>/      # SOLO si ese target diverge de la base
  <feature>_views.md          # override per-view (componentes nativos / layout tablet)
  <feature>_flows.md          # override (solo si la navegación cambia)
  <feature>_ui_prompt.md
```

**Trazabilidad (Regla 1 sigue vigente).** Un override traza a su vista base + el mismo journey/CA del spec + el `DESIGN.md`; no introduce vistas ni comportamiento ausentes de la base o el spec. La etiqueta de design target y su convención (`<familia>[-<plataforma>][-<formfactor>]`, familia ∈ `{mobile,web,desktop}`) son SSoT del init (D-011); aquí solo se consume para nombrar `targets/<design-target>/`.

> **Dónde se aplica la resolución** (emitir/consumir base + overrides al generar o al resolver en el consumer) es responsabilidad de `wf-design-feature-prototype` + `design-feature-architect` (D-011 12.6); esta regla es el **contrato** que implementan. Coste asumido: una vista overrideada re-enuncia sus estados no cambiados — acotado a las vistas que divergen.
