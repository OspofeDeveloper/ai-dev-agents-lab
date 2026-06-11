---
name: kb-design-voice
description: Base de conocimiento de UX writing y voice & tone del producto: tono de voz, patrones de microcopy por contexto (empty, error, success, loading), estructura de mensajes de error, consistencia lexica y politicas de mayusculas, puntuacion y abreviaturas.
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Design Voice

Eres la fuente de verdad para como habla el producto al usuario. No redefines comportamiento funcional (eso es del Spec) ni decisiones visuales (eso es de `kb-design-expert`); decides como suena la interfaz.

## Regla 1: La voz se decide a nivel producto y se materializa en cada vista

Toda interfaz tiene voz, aunque no se decida. Si no se decide, la voz es accidental y heterogenea.

El `DESIGN.md` declara la voz del producto. Cada `*_views.md` materializa esa voz en microcopy concreta. El brief acota la voz con `clarity_vs_brand` y, si se declara, `voice_tone`.

## Regla 2: Cuatro ejes de voz cerrados

La voz se describe sobre cuatro ejes, cada uno con un valor en escala de 3:

- `formality`: `formal` | `neutral` | `cercano` — cuanto tutea o usted, cuanto coloquial.
- `expertise`: `tecnico` | `mixto` | `accesible` — cuanto usa jerga del dominio vs lenguaje cotidiano.
- `warmth`: `neutro` | `humano` | `calido` — cuanto refleja empatia explicita.
- `playfulness`: `serio` | `medido` | `ludico` — cuanto usa humor, ironia, o lenguaje sorpresivo.

Una voz completa declara los cuatro: ej. `voice: cercano + mixto + humano + medido`.

Combinaciones recomendadas por familia:
- `productive-minimal`: neutral + tecnico/mixto + neutro + serio.
- `calm-minimal`: cercano + accesible + humano + medido.
- `expressive-modern`: cercano + accesible + calido + medido/ludico.
- `editorial-premium`: neutral + mixto + humano + medido.
- `depth-material`: neutral + mixto + neutro + medido.

## Regla 3: Coherencia con clarity_vs_brand del brief

- `clarity-first`: prioriza precision sobre personalidad. Frases directas, sin metaforas. Permitido: cercania y calor moderados; vetado: lenguaje ludico que entorpezca tareas.
- `balanced`: voz consistente con caracter de marca pero sin sacrificar claridad funcional.
- `brand-forward`: voz como vehiculo de marca. Permitido lenguaje propio, terminologia inventada (con glosario), tono ludico si encaja.

Si el `voice_tone` declarado en el brief contradice al `clarity_vs_brand`, manda el brief.

## Regla 4: Estructura obligatoria de mensajes de error

Un buen mensaje de error siempre responde tres preguntas, en este orden:

1. **Que ha pasado** — neutro y especifico (no "algo fallo"; si "no pudimos cargar tu listado").
2. **Por que ha pasado** (si se sabe y aporta) — corto, sin culpa al usuario salvo que sea su accion.
3. **Que puede hacer** — accion concreta (CTA + descripcion si la accion no es obvia).

Ejemplo `clarity-first`:
> No pudimos cargar tus transacciones. La conexion se interrumpio. **Reintentar**.

Ejemplo `brand-forward`:
> Ups, hoy la red no colabora. Probamos otra vez? **Reintentar**.

Que **nunca** debe contener un error:
- Codigos tecnicos crudos sin contexto (`Error 500`).
- Culpa explicita al usuario (`escribiste mal el password`).
- Verbos pasivos vagos (`fue producido un error`).
- Errores que no proponen accion cuando si existe una.

## Regla 5: Patrones de microcopy por contexto

Cada estado de vista (Regla 4 de `kb-design-feature-artifacts`) tiene patrones especificos:

### Empty states

Tres componentes:
- **Titulo**: nombra el espacio vacio sin negatividad. "Aun no tienes facturas" mejor que "No hay nada aqui".
- **Cuerpo**: explica brevemente que cambia cuando se llena. Opcional pero recomendado.
- **CTA**: accion concreta para llenarlo. "Crear primera factura" mejor que "Empezar".

Anti-patrones:
- "No hay datos" (informativo pero vacuo).
- "Lista vacia" (literal y deprimente).
- Empty sin CTA cuando si hay accion posible.

### Loading

- < 1s: sin texto, solo indicador visual.
- 1-3s: texto generico ("Cargando…") opcional.
- > 3s: texto contextual ("Buscando facturas de este mes…") + posibilidad de cancelar si la accion lo permite.
- > 10s: progreso visible (porcentaje, pasos completados) o estimacion.

### Success

- Confirmacion accion: copy corto + auto-dismiss en 2-4s, salvo accion destructiva que requiera confirmacion explicita.
- "Hecho" o "Listo" como minimo; "Factura creada" como ideal.

### Confirmacion destructiva

Estructura:
- **Pregunta clara**: "Borrar esta factura?"
- **Consecuencia**: que se pierde y si es reversible o no.
- **Accion afirmativa con verbo concreto**: "Borrar" mejor que "Aceptar".
- **Accion negativa neutra**: "Cancelar" o "Volver".

Anti-patron: confirmacion destructiva con verbos genericos ("OK"/"Cancelar") que no comunican consecuencia.

### Forms — placeholders y labels

- Labels siempre visibles, no placeholders como label (rompe a11y y se pierde al escribir).
- Placeholders cuando aplican deben dar formato esperado, no descripcion (`"DD/MM/AAAA"` mejor que `"Fecha de nacimiento"`).
- Helper text para reglas no obvias ("Tu contrasena debe tener al menos 8 caracteres y un numero").
- Mensajes de error junto al campo, no en banner global.

## Regla 6: Acciones y verbos en CTAs

Cada CTA es un verbo concreto orientado a la accion del usuario, no a la del sistema.

Reglas:
- Empieza con verbo: "Crear factura", no "Factura nueva".
- Especifico mejor que generico: "Guardar borrador" mejor que "Guardar".
- Primera persona del usuario, no del sistema: "Ver mis facturas" mejor que "Mostrar facturas".
- No mas de 3-4 palabras en CTA primaria.

Anti-patrones:
- "Click aqui", "Aqui", "Mas info" (no comunican accion).
- Verbos sustantivados ("Realizacion de pago" → "Pagar").
- CTAs que dicen lo que la pantalla ya dice ("Continuar" sin contexto cuando hay una sola accion obvia se justifica; con dos opciones, ambas necesitan verbo concreto).

## Regla 7: Glosario de producto

`DESIGN.md` debe incluir, en `## Voice & Microcopy` (seccion custom anadida en Fase 2), un glosario de 5-15 terminos clave del producto con su uso canonico. Esto evita que distintos features usen palabras distintas para el mismo concepto.

Ejemplo:
- **Factura** (no recibo, no boleta, no comprobante) — documento fiscal emitido a un cliente.
- **Cliente** (no usuario, no comprador) — la entidad que recibe facturas.
- **Vencer** (no expirar, no caducar) — la factura llega a su fecha limite.

Si el producto opera en varios idiomas, el glosario se mantiene por idioma con el mismo set de conceptos.

## Regla 8: Politica de mayusculas, puntuacion y abreviaturas

Decisiones a nivel producto, declaradas en `DESIGN.md`:

- **Sentence case** (Recomendado por defecto en es/en) vs **Title Case** (mas marketing-y, encaja con `brand-forward`).
- **Punto final en CTAs**: nunca.
- **Punto final en errores y body**: si en es; en en/UI minimalista a veces se omite.
- **Comillas**: tipograficas (`«»` o `"`) en es y en, no rectas salvo en code.
- **Abreviaturas**: evitar salvo extremadamente comunes ("etc.", "ej."). En CTAs nunca.
- **Numeros**: digitos en UI (`3 facturas`), no escritos en letra salvo onboarding marketing.
- **Emojis**: regla explicita. En `clarity-first` y productos B2B/financieros, vetados en UI funcional. En `brand-forward` y consumer, permitidos como acento si son consistentes.

## Regla 9: Como se documenta voice en DESIGN.md

Frontmatter YAML (bloque libre, el linter lo preserva):

```yaml
voice:
  formality: cercano | neutral | formal
  expertise: tecnico | mixto | accesible
  warmth: neutro | humano | calido
  playfulness: serio | medido | ludico
  case_style: sentence | title
  emoji_policy: permitidos | restringidos | vetados
```

Seccion markdown `## Voice & Microcopy`:

- 4 ejes de voz con justificacion (por que cercano y no formal, etc.).
- 3-5 ejemplos canonicos: como decimos "exito", como decimos "error de red", como decimos "vacio", como decimos "confirmacion destructiva".
- Glosario de 5-15 terminos clave.
- Politica de mayusculas, puntuacion, emojis.
- Lo que NO decimos (anti-patrones: "click aqui", codigos tecnicos crudos, culpa al usuario).

## Regla 10: Microcopy en `*_views.md`

Cada vista debe declarar al menos:
- Label de accion primaria.
- Copy de empty state si aplica.
- Copy de error tipico si aplica.
- Copy de success/confirmacion si aplica.

La voz se hereda del DESIGN.md. Si una vista requiere desviar (raro), debe justificarse con `> Nota:`.
