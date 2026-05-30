---
name: wf-design-moodboard
description: "Captura inspiracion visual no estructurada antes del discovery. El usuario describe vibes (paletas, fotografia, atmosfera, ilustracion, texturas) y produce un <basename>_design_moodboard.md que alimenta wf-design-intake con material concreto para cerrar style_family y adjectives con precision. Especialmente util para disenadores junior."
when_to_use: "Activa con frases como 'quiero capturar inspiración visual', 'crea un moodboard', 'tengo referencias de estilo', 'quiero definir vibes antes del brief', 'captura referencias de diseño'. No activa para cerrar el brief formal (usa wf-design-intake) ni para generar el sistema visual (usa wf-design-system)."
argument-hint: "<feature_spec.md> [--prd <prd.md>] [--output <path>] [--mode interactive|auto]"
effort: medium
allowed-tools: [Read, Write, WebSearch]
context: fork
---

# design-moodboard — Captura de inspiracion visual

Tu rol es producir un mood board textual a partir de la descripcion del usuario, antes de cerrar familia visual y adjectives en el brief. No decides; ayudas a articular lo que esta latente.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del spec**: primer argumento posicional.
- **Path del PRD** opcional via `--prd`.
- **Path de salida** opcional via `--output`.
- **Modo** opcional via `--mode` (`interactive` por defecto, `auto` para flujos no asistidos).

Si no hay path, informa:
> "Uso: `/wf-design-moodboard <feature_spec.md> [--prd <prd.md>] [--output <path>] [--mode interactive|auto]`"

## Paso 2: Verificar el Spec

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Si no parece un Spec SDD validado, deten:
   > "Este archivo no parece un Spec SDD validado. Primero ejecuta los workflows de spec."

## Paso 3: Resolver PRD

Si `--prd` se paso, leelo. Si no, intenta resolver `prd.md` en la raiz del producto. Si no existe, continua sin PRD (no bloqueante).

## Paso 4: Determinar path de salida

- Si `--output` se paso, usalo.
- Si no, escribe `<basename>_design_moodboard.md` en el mismo directorio del spec.

## Paso 5: Captura del mood

### Modo `interactive` (por defecto)

Realiza al usuario una serie de preguntas abiertas, sin forzar opciones cerradas. Adapta las preguntas al contexto del spec:

1. **Vibe general en una frase**: "Si tuvieras que describir como deberia sentirse esta app en una frase, sin pensar en colores ni botones, ¿que dirias?"
2. **Apps que admiras**: "¿Hay una app o producto que admires por como se siente — no por funcionalidad, por sensacion? ¿Cuales?"
3. **Lo que NO quieres**: "¿Hay algo que tengas claro que NO quieres? (ejemplo: serio en exceso, infantil, demasiado corporativo, frio…)"
4. **Atmosfera**: "Si esto fuera un espacio fisico, ¿como seria? ¿Un loft minimalista, una libreria antigua, un laboratorio, una cafeteria, un parque?"
5. **Paleta intuitiva**: "¿Que colores te vienen a la cabeza cuando piensas en este producto, aunque no sepas como los usarias? Puedes nombrar colores o objetos del mundo real ('madera clara', 'cielo de tarde')."
6. **Fotografia o ilustracion**: "¿Imaginas el producto con fotografia, ilustracion, ambos, o sin imagery? Si hay imagery, ¿de que tipo?"
7. **Tono al hablar**: "¿Como te gustaria que la app te hablara? Como un asistente formal, un companero cercano, un experto neutral, un coach motivador?"

Permite respuestas vacias ("no se", "no me importa"). No fuerces decisiones. Recopila lo que el usuario ofrezca.

### Modo `auto`

Deriva el mood directamente del spec y PRD:
- Sector y dominio del producto.
- Actor principal (perfil, contexto de uso).
- Tono funcional del spec (urgencia, calma, repeticion, exploracion).
- Cualquier mencion de marca en el PRD.

Genera el mood sin preguntar, con menos resolucion que en modo interactivo pero suficiente para alimentar el intake.

## Paso 6: Research complementario (opcional)

Si el usuario menciono apps o referencias en la captura, hacer WebSearch ligero para confirmar y enriquecer:
- ¿Existe esa app? ¿Que aspecto destacan los reviews / award sites?
- Si menciono un sector o estilo amplio, buscar 2-3 referencias profesionales del sector.

Si las busquedas no aportan, no insistir.

## Paso 7: Escribir el mood board

Escribe `<basename>_design_moodboard.md` con esta estructura:

```markdown
---
spec: <path_spec>
mode: interactive | auto
generated_at: <fecha ISO>
---

# Design Moodboard — <feature name>

## Vibe en una frase

> <la frase del usuario o derivada del spec>

## Atmosfera

<descripcion textual del espacio o sensacion fisica analoga>

## Paleta intuitiva

- Colores o referencias del mundo real mencionadas: <lista>
- Energia cromatica probable: <low | medium | high> (inferida)
- Modo dominante probable: <light | dark | ambos>

## Imagery

- Tipo de imagery deseada: <fotografia | ilustracion | sin imagery | mixto>
- Caracter: <documental | aspiracional | minimal | abstracto | hand-drawn | otro>
- Notas: <si las hay>

## Tono al hablar

<resumen del tono deseado en una linea>

## Referencias mencionadas por el usuario

- **<App o producto 1>**: <que aspecto destacan, segun usuario o research>
- **<App o producto 2>**: <...>

## Lo que NO se quiere

- <anti-patron 1>
- <anti-patron 2>

## Pistas para style_family (inferencia, no decision)

Basandose en el mood capturado, los candidatos a `style_family` son:

1. **<candidato principal>** — porque <razon corta>
2. **<candidato alternativo>** — porque <razon corta>

Esta inferencia se materializa en `wf-design-intake`, no aqui. El moodboard es entrada, no decision.

## Pistas para adjectives

Adjetivos sugeridos derivados del mood (entre 8-12, sin filtrar):

- <adjetivo>: <implicacion intuitiva>
- ...

## Notas finales

<cualquier observacion del usuario que no encaje en las secciones anteriores>
```

## Paso 8: Informar al usuario

Reporta:
- path del moodboard generado
- vibe principal capturada
- candidatos a `style_family` inferidos
- siguiente paso recomendado:
  > "Ahora ejecuta `/wf-design-intake generate <feature_spec.md> --mode hybrid` — el intake consumira este moodboard si esta en el directorio esperado."

## Paso 9: Integracion con `wf-design-intake`

`wf-design-intake` debe, en su Paso 5 (derivar contexto base), buscar `<basename>_design_moodboard.md` en el mismo directorio del spec. Si existe:
- usar las pistas de `style_family` como propuestas iniciales del arbol de decision
- usar los adjetivos sugeridos como punto de partida para `adjectives`
- usar la atmosfera y referencias como input adicional para Visual Personality

El moodboard nunca sustituye al brief; lo alimenta.
