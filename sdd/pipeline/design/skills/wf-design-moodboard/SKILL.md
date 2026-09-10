---
name: wf-design-moodboard
description: "Captura inspiracion visual no estructurada antes del discovery: el usuario describe vibes (paletas, fotografia, atmosfera, ilustracion, texturas) y produce un _design_moodboard.md que alimenta wf-design-intake para cerrar style_family y adjectives. Util para juniors."
when_to_use: "Activa con frases como 'quiero capturar inspiración visual', 'crea un moodboard', 'tengo referencias de estilo', 'quiero definir vibes antes del brief', 'captura referencias de diseño'. No activa para cerrar el brief formal (usa wf-design-intake) ni para generar el sistema visual (usa wf-design-system)."
argument-hint: "<feature_spec.md> [--prd <prd.md>] [--output <path>] [--mode interactive|auto]"
effort: high
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# design-moodboard — Captura de inspiracion visual

**Corres en el hilo principal.** Esta skill **es** una entrevista: siete preguntas abiertas al usuario
sobre como deberia sentirse su producto. Un `context: fork` no puede presentar una pregunta
([[D-002]]/[[D-045]]), asi que ahi este workflow no tenia forma de funcionar — y el riesgo no era
quedarse a medias, era **rellenar las respuestas por su cuenta**: un moodboard fabricado tiene
exactamente la misma pinta que uno real ([[D-072]]).

Tu rol es de **orquestador**: recoges la inspiracion del usuario **con fidelidad** y **delegas** la
articulacion de ese material crudo en `design-system-architect` con la tool `Agent` y
`run_in_background: false` ([[D-043]]). Traducir "madera clara" al vocabulario del taxonomy es trabajo
del experto, con sus `kb-*` en contexto; recoger literalmente lo que el usuario dijo es tuyo.

**No leas el spec ni el PRD** ([[D-031]]) y **no escribas el moodboard** ([[D-060]]): pasas paths, y
el agente lee, redacta y escribe — es su artefacto.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del spec**: primer argumento posicional.
- **Path del PRD** opcional via `--prd`.
- **Path de salida** opcional via `--output`.
- **Modo** opcional via `--mode` (`interactive` por defecto, `auto` para flujos no asistidos).

Si no hay path, informa:
> "Uso: `/wf-design-moodboard <feature_spec.md> [--prd <prd.md>] [--output <path>] [--mode interactive|auto]`"

## Paso 2: Verificar el Spec

Comprobacion **mecanica**, sin leer el contenido:

```bash
!test -f "<path_spec>" && echo EXISTE || echo NO_EXISTE
```

`NO_EXISTE` → deten: la inspiracion se captura para una feature concreta, y ese path no existe. Si el
contenido es o no un Spec SDD utilizable lo valora tu delegado, que es quien lo lee.

## Paso 3: Resolver PRD

Si `--prd` se paso, comprueba que existe. Si no, intenta resolver `prd.md` en la raiz del producto (`test -f`). Si no existe, continua sin PRD (no bloqueante). En los dos casos pasas **el path**, no el contenido.

## Paso 4: Determinar path de salida

- Si `--output` se paso, usalo.
- Si no, escribe `<basename>_design_moodboard.md`: en la subcarpeta `design/` de la feature si el spec esta en `features/<nombre>/spec/` (crea el directorio si no existe); en el mismo directorio del spec en otros casos (layout plano legacy).

## Paso 5: Captura del material crudo

### Modo `interactive` (por defecto)

Estas siete son **abiertas a proposito**: el material que buscas es como el usuario habla de su
producto, no una opcion de un menu. Presentalas en conversacion —agrupadas, no de una en una— y
reserva `AskUserQuestion` para las dos que si son cerradas (la 6 y la 7). **No interpretes las
respuestas**: viajan literales al Paso 6. Adapta el enunciado al contexto del spec:

1. **Vibe general en una frase**: "Si tuvieras que describir como deberia sentirse esta app en una frase, sin pensar en colores ni botones, ¿que dirias?"
2. **Apps que admiras**: "¿Hay una app o producto que admires por como se siente — no por funcionalidad, por sensacion? ¿Cuales?"
3. **Lo que NO quieres**: "¿Hay algo que tengas claro que NO quieres? (ejemplo: serio en exceso, infantil, demasiado corporativo, frio…)"
4. **Atmosfera**: "Si esto fuera un espacio fisico, ¿como seria? ¿Un loft minimalista, una libreria antigua, un laboratorio, una cafeteria, un parque?"
5. **Paleta intuitiva**: "¿Que colores te vienen a la cabeza cuando piensas en este producto, aunque no sepas como los usarias? Puedes nombrar colores o objetos del mundo real ('madera clara', 'cielo de tarde')."
6. **Fotografia o ilustracion**: "¿Imaginas el producto con fotografia, ilustracion, ambos, o sin imagery? Si hay imagery, ¿de que tipo?"
7. **Tono al hablar**: "¿Como te gustaria que la app te hablara? Como un asistente formal, un companero cercano, un experto neutral, un coach motivador?"

Permite respuestas vacias ("no se", "no me importa"). No fuerces decisiones. Recopila lo que el usuario ofrezca.

### Modo `auto`

No preguntes al usuario. Pasa los paths del spec y del PRD al agente con la senal de modo `auto` para
que derive el mood directamente del material funcional. **El artefacto tiene que decir que nadie lo
dijo**: el agente marca cada candidato como derivado y de que material, para que `wf-design-intake` no
lo lea como una preferencia del usuario que nunca existio.

## Paso 6: Articular el mood board (delegado)

Delega con la tool `Agent` ([[D-043]]), `subagent_type: "design-system-architect"` y
**`run_in_background: false`**, con este prompt:

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
- Genera el moodboard segun la plantilla y **escribelo tu** en el output path: eres su autor ([[D-059]]/[[D-060]]). Informa de la ruta al terminar.
- Las respuestas del usuario entran **literales** en su seccion; tu traduccion al taxonomy va aparte y con su razon. Si una respuesta vino vacia ("no se", "no me importa"), eso se documenta como tal — no se rellena.
```

## Paso 7: Comprobar el resultado

```bash
!test -f "<path_moodboard>" && echo ESCRITO || echo FALTA
```

`FALTA` → no lo escribas tu ([[D-060]]): reporta que el agente no dejo el artefacto y para. Que su
informe diga que lo escribio no es que este escrito ([[D-047]]).

## Paso 8: Informar al usuario

Reporta:
- path del moodboard generado
- vibe principal capturada
- candidatos a `style_family` inferidos
- siguiente paso, en lenguaje natural: cerrar el brief visual del producto, que consumira este moodboard si esta en el directorio esperado. **No le des el comando** — te lo pide hablando.

## Paso 9: Integracion con `wf-design-intake`

`wf-design-intake` debe, en su Paso 5 (derivar contexto base), buscar `<basename>_design_moodboard.md` en la subcarpeta `design/` de la feature o en el mismo directorio del spec (layout plano legacy). Si existe:
- usar las pistas de `style_family` como propuestas iniciales del arbol de decision
- usar los adjetivos sugeridos como punto de partida para `adjectives`
- usar la atmosfera y referencias como input adicional para Visual Personality

El moodboard nunca sustituye al brief; lo alimenta.
