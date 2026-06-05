---
name: wf-design-moodboard
description: "Captura inspiracion visual no estructurada antes del discovery. El usuario describe vibes (paletas, fotografia, atmosfera, ilustracion, texturas) y produce un <basename>_design_moodboard.md que alimenta wf-design-intake con material concreto para cerrar style_family y adjectives con precision. Especialmente util para disenadores junior."
when_to_use: "Activa con frases como 'quiero capturar inspiración visual', 'crea un moodboard', 'tengo referencias de estilo', 'quiero definir vibes antes del brief', 'captura referencias de diseño'. No activa para cerrar el brief formal (usa wf-design-intake) ni para generar el sistema visual (usa wf-design-system)."
argument-hint: "<feature_spec.md> [--prd <prd.md>] [--output <path>] [--mode interactive|auto]"
effort: high
allowed-tools: [Read, Write, Bash, Agent, WebSearch]
context: fork
agent: design-architect
---

# design-moodboard — Captura de inspiracion visual

Tu rol como orquestador es facilitar la captura de inspiracion del usuario y delegar al agente `design-architect` la articulacion del material crudo en candidatos visuales concretos (familia, adjetivos, atmosfera, paleta intuitiva traducida al taxonomy). No interpretas las respuestas del usuario tu mismo; tu trabajo es recogerlas con fidelidad y pasarselas al agente, que aplicara `kb-design-style-taxonomy` y `kb-design-style-decision-tree` para producir el mood board.

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
- Si no, escribe `<basename>_design_moodboard.md`: en la subcarpeta `design/` de la feature si el spec esta en `features/<nombre>/spec/` (crea el directorio si no existe); en el mismo directorio del spec en otros casos (layout plano legacy).

## Paso 5: Captura del material crudo

### Modo `interactive` (por defecto)

Realiza al usuario una serie de preguntas abiertas, sin forzar opciones cerradas. No interpretes las respuestas; transcribelas literales para pasarselas al agente. Adapta las preguntas al contexto del spec:

1. **Vibe general en una frase**: "Si tuvieras que describir como deberia sentirse esta app en una frase, sin pensar en colores ni botones, ¿que dirias?"
2. **Apps que admiras**: "¿Hay una app o producto que admires por como se siente — no por funcionalidad, por sensacion? ¿Cuales?"
3. **Lo que NO quieres**: "¿Hay algo que tengas claro que NO quieres? (ejemplo: serio en exceso, infantil, demasiado corporativo, frio…)"
4. **Atmosfera**: "Si esto fuera un espacio fisico, ¿como seria? ¿Un loft minimalista, una libreria antigua, un laboratorio, una cafeteria, un parque?"
5. **Paleta intuitiva**: "¿Que colores te vienen a la cabeza cuando piensas en este producto, aunque no sepas como los usarias? Puedes nombrar colores o objetos del mundo real ('madera clara', 'cielo de tarde')."
6. **Fotografia o ilustracion**: "¿Imaginas el producto con fotografia, ilustracion, ambos, o sin imagery? Si hay imagery, ¿de que tipo?"
7. **Tono al hablar**: "¿Como te gustaria que la app te hablara? Como un asistente formal, un companero cercano, un experto neutral, un coach motivador?"

Permite respuestas vacias ("no se", "no me importa"). No fuerces decisiones. Recopila lo que el usuario ofrezca.

### Modo `auto`

No preguntes al usuario. Pasa el spec y PRD al agente con la senal de modo `auto` para que derive el mood directamente del material funcional.

## Paso 6: Delegar al agente design-architect

Construye el prompt para el agente con:

```text
Modo cognitivo: moodboard-articulate
Spec path: <path>
PRD path: <path o "ninguno">
Modo de captura: <interactive | auto>
[Si interactive] Respuestas literales del usuario:
1. Vibe general: <texto>
2. Apps admiradas: <texto>
3. Lo que NO quiere: <texto>
4. Atmosfera: <texto>
5. Paleta intuitiva: <texto>
6. Fotografia/ilustracion: <texto>
7. Tono al hablar: <texto>
Output path: <basename>_design_moodboard.md
Template del artefacto: ${CLAUDE_SKILL_DIR}/references/moodboard_template.md

INSTRUCCION:
- Articula el material crudo en candidatos a `style_family` aplicando `kb-design-style-taxonomy` y `kb-design-style-decision-tree`.
- Traduce la paleta intuitiva ("madera clara", "cielo de tarde") a familias de color compatibles con el taxonomy, sin cerrar tokens (eso es trabajo de wf-design-system).
- Si hay apps mencionadas, valida brevemente con WebSearch ligero (2-3 lookups maximo) — no es discovery formal.
- Genera el contenido del moodboard segun la plantilla. No escribas el archivo: devuelvelo para que el orquestador lo escriba.
```

Invoca el agente `design-architect`.

## Paso 7: Escribir el mood board

Escribe `<basename>_design_moodboard.md` con el contenido devuelto por el agente.

## Paso 8: Informar al usuario

Reporta:
- path del moodboard generado
- vibe principal capturada
- candidatos a `style_family` inferidos
- siguiente paso recomendado:
  > "Ahora ejecuta `/wf-design-intake generate <feature_spec.md> --mode hybrid` — el intake consumira este moodboard si esta en el directorio esperado."

## Paso 9: Integracion con `wf-design-intake`

`wf-design-intake` debe, en su Paso 5 (derivar contexto base), buscar `<basename>_design_moodboard.md` en la subcarpeta `design/` de la feature o en el mismo directorio del spec (layout plano legacy). Si existe:
- usar las pistas de `style_family` como propuestas iniciales del arbol de decision
- usar los adjetivos sugeridos como punto de partida para `adjectives`
- usar la atmosfera y referencias como input adicional para Visual Personality

El moodboard nunca sustituye al brief; lo alimenta.
