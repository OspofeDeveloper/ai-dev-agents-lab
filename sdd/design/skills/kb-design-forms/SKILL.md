---
name: kb-design-forms
description: Base de conocimiento para patrones de formulario en mobile y web. Define layout (label, field, helper, error placement), validacion (cliente vs servidor, momento de disparo), estados de campo, patrones complejos (multistep, autosave, conditional fields, file upload, search in input). 50-70% de productos B2B son formularios; sin esta kb se quedan enterrados en views genericas.
argument-hint: "(cargada automaticamente por agentes y workflows de design)"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Design Forms

Eres la fuente de verdad para patrones de formulario. No redefines reglas de voice (`kb-design-voice`), de a11y (`kb-a11y-expert`) ni de estados de componente (`kb-design-expert` Regla 16): consolidas las decisiones especificas de form.

## Regla 1: Layout y anatomia base del field

Cada campo de formulario tiene anatomia obligatoria:

- **Label**: siempre visible, encima del campo (no placeholder-as-label). Excepcion permitida: floating label si la familia visual lo justifica (`expressive-modern`, `editorial-premium`).
- **Field**: el control en si (input, select, textarea, etc.).
- **Helper text** (opcional pero recomendado): explicacion breve debajo del field cuando el campo tiene reglas no obvias (formato, longitud, validacion contextual).
- **Error message** (cuando aplica): debajo del field, sustituye al helper, con icono de error y color de token `error`.
- **Indicador de obligatorio** (asterisco o "obligatorio" en label): consistente en todo el form.

Excepciones:
- Search inputs pueden omitir label si el icono y el placeholder son suficientes.
- Checkboxes y radios llevan label a la derecha del control.
- Toggles llevan label a la izquierda, control a la derecha (mobile pattern).

## Regla 2: Validacion — cuando y como

Decisiones canonicas:

- **Cuando validar**:
  - **On submit**: validacion definitiva. Siempre.
  - **On blur**: validacion suave del campo cuando el usuario sale. Recomendado para email, telefono, URL, password.
  - **On change**: solo para validaciones inmediatas (password strength meter, character count).
  - **Nunca on focus**: validar mientras el usuario empieza a escribir es agresivo.

- **Cliente vs servidor**:
  - Validaciones de formato: cliente.
  - Validaciones de existencia (email ya registrado, codigo postal valido en BBDD): servidor, con loading state en el campo.
  - Validaciones de negocio (limite de credito, cupos disponibles): servidor, on submit.

- **Donde mostrar el error**:
  - Junto al campo siempre.
  - Si hay varios errores en submit, scroll automatico al primer campo con error + focus.
  - Banner global solo para errores transversales (sesion expirada, error de red).

- **Como redactar el error**: ver Regla 4 de `kb-design-voice`.

## Regla 3: Estados de campo obligatorios

Cada campo de form declara estos estados (Regla 16 de `kb-design-expert` aplicada a forms):

- `default`: estado inicial.
- `focus`: visualmente distinto (borde acentuado, focus ring respetando contraste 3:1).
- `filled`: cuando hay valor (borde puede cambiar a `border-strong`).
- `valid`: opcional, solo si la validacion success aporta (campos con regla compleja).
- `invalid`: borde `color.error`, mensaje debajo.
- `disabled`: bg `background`, opacity 0.6.
- `read-only`: bg `background`, sin border-bottom o con border `border`, text color normal (no muted) para que se lea bien.
- `loading`: cuando hace validacion async (spinner inline a la derecha).

Para inputs con prefijo o sufijo (currency, units), el slot del addon se trata como parte del campo, no como elemento independiente.

## Regla 4: Field grouping y jerarquia

- Campos relacionados se agrupan visualmente (mismo `surface`, spacing reducido entre ellos).
- Grupos llevan titulo (h3 o label-large) cuando hay mas de un grupo en la pantalla.
- Campos opcionales se marcan como tal solo si la mayoria son obligatorios. Si la mayoria son opcionales, marcar obligatorios.
- Orden logico: datos personales antes que direccion antes que pago, no al reves.

## Regla 5: Forms largos — patrones de manejo

Cuando un form tiene mas de 8-10 campos o trata flujos complejos, no resolverlo como pantalla unica:

- **Multistep**:
  - Indicador de progreso visible (numero de pasos completados o porcentaje).
  - Cada paso valida sus campos antes de avanzar.
  - "Atras" preserva los datos del paso anterior.
  - Boton de salida que pregunta si descartar o guardar borrador.
- **Acordeones / Disclosure**: agrupar secciones colapsables si el form es revision/edicion de muchos datos.
- **Autosave**:
  - Cada cambio se guarda al backend (con debounce 500-1000ms).
  - Indicador discreto de "Guardado a las HH:MM" cerca del titulo del form.
  - No mostrar spinners durante el save salvo error.
- **Draft mode**:
  - Si autosave no es viable, salir del form ofrece "Guardar como borrador".
  - Drafts visibles en la lista origen, con indicador de estado.

## Regla 6: Campos especiales — patrones canonicos

### Inputs de texto especiales

- **Email**: validacion de formato `local@dominio.tld` on blur. Suggest auto-complete del dominio si es comun.
- **Password**: visibility toggle (ojo) obligatorio en mobile. Strength meter solo en registro, no en login.
- **Phone**: input con flag de pais si hay multi-pais. Formato visual mientras escribe.
- **Currency**: prefijo de simbolo, separadores de miles, decimales segun locale.
- **Search**: icono lupa a la izquierda, boton clear (X) cuando hay valor.

### Selectores

- **Select corto** (< 7 opciones): radio group o segmented control en mobile.
- **Select medio** (7-20 opciones): dropdown nativo o sheet en mobile.
- **Select largo** (> 20 opciones): sheet con search.
- **Multi-select**: chips para selecciones visibles + sheet con search.

### Date/Time

- **Date picker**: nativo cuando se pueda (mejor UX y a11y). Custom solo si la UX nativa rompe el diseno.
- **Range picker**: dos campos linked, no un calendario complejo embedded en pantalla.
- **Relative times** ("Hace 3 dias"): solo lectura, no input.

### File upload

- Drop zone con clear affordance ("Arrastra o selecciona archivos").
- Lista de archivos seleccionados con preview (si es imagen) o icono + nombre + tamano.
- Cada item con accion "quitar".
- Progress bar por archivo en upload.
- Errores por archivo, no globales.

### Conditional fields

- Aparecen cuando otro campo tiene cierto valor.
- Aparicion con motion suave (Regla 2 de `kb-design-motion-expert`, easing `transition`).
- No deshabilitar campos condicionales: ocultarlos. Disabled es para acciones temporalmente bloqueadas, no para campos irrelevantes.

## Regla 7: Forms y a11y

Delegado a `kb-a11y-expert`, pero patrones especificos de form:

- Cada `label` asociada al `field` (for/id o nesting).
- Errores anunciados via `liveRegion="polite"`.
- Orden de focus = orden visual.
- Agrupaciones con `fieldset` + `legend` o equivalente en mobile.
- Required state comunicado por aria-required, no solo visual.

## Regla 8: Submit button y feedback de accion

- Boton primario destacado y al final del form (mobile: ancho completo).
- Mientras se procesa: estado `loading`, label cambia a "Guardando…" o equivalente, deshabilitado para evitar doble submit.
- Tras success: feedback visible (toast, redireccion, transicion).
- Tras error: el form vuelve a estado editable, focus al primer campo con error si los hubiera, mensaje global si era error transversal.

Anti-patrones:
- Submit que permanece habilitado y permite doble click.
- Submit sin feedback visible tras click.
- Reset/Cancel con mismo peso visual que Submit.

## Regla 9: Anti-patrones de form

- Labels como placeholders.
- Asterisco rojo sin leyenda explicativa cerca.
- Reset button con mismo peso visual que submit (riesgo de borrado accidental).
- Captchas invasivas en lugar de validaciones razonables.
- "Tu password no cumple" sin decir que falta.
- Multistep sin permitir volver atras.
- Validacion mientras el usuario escribe el primer caracter.
- Forms que pierden datos al rotar el dispositivo.

## Regla 10: Como se documenta forms en DESIGN.md y views

En `DESIGN.md > Components` declarar al menos:
- `input-text` (con todos los estados de Regla 3).
- `input-textarea`, `select`, `date-picker`, `file-upload` si aplica al producto.
- `form-group` (contenedor con titulo, spacing, jerarquia).
- `form-actions` (footer con submit/cancel).

En `*_views.md` de cada pantalla con formulario:
- Declarar el form como vista o como bloque.
- Listar campos en orden con: label, tipo, obligatorio?, helper text, regla de validacion (resumida).
- Estados de form: editable, submitting, success, error.
- CTA primaria con copy concreto (Regla 6 de `kb-design-voice`).
