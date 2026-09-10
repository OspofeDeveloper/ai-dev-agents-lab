---
name: wf-design-intake
description: "Cierra el DESIGN_BRIEF.md antes de generar el sistema visual: fija modo de decision, preset, familia visual, densidad, profundidad, motion y policy de referencias y autonomia. Delega a design-system-architect. Modos guided, hybrid y auto."
when_to_use: "Activa con frases como 'cierra el brief de diseño', 'necesito el design brief', 'quiero definir el brief visual', 'preparar el brief antes de diseñar', 'genera el DESIGN_BRIEF.md'. No activa si ya existe un DESIGN_BRIEF.md y solo se quiere actualizar (usa wf-design-delta) ni para generar directamente el DESIGN.md sin brief (el brief es gate obligatorio)."
argument-hint: "generate <feature_spec.md> [--prd <prd.md>] [--output DESIGN_BRIEF.md] [--mode guided|hybrid|auto] [--preset <name>] [--learn] [--allow-overwrite-brief]"
effort: high
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# design-intake — Orquestador del Flujo SDD (Pre-etapa Design)

**Corres en el hilo principal.** Cerrar el brief **es** una conversacion con el usuario —el arbol de
decision se recorre pregunta a pregunta, y en `hybrid` cada propuesta se confirma—, y eso solo puede
hacerlo quien tiene turno: un `context: fork` no puede presentar una pregunta ([[D-002]]/[[D-045]]).
Tu rol es de **orquestador**: parseas argumentos, verificas precondiciones deterministas, **sostienes
los gates** con `AskUserQuestion`, y **delegas** en `design-system-architect` —el analisis experto y
la redaccion del `DESIGN_BRIEF.md`— con la tool `Agent` y `run_in_background: false` ([[D-043]]).

**No leas el spec, ni el PRD, ni el brief existente** ([[D-031]]): pasas **paths**, y quien los lee es
tu delegado, que tiene las `kb-*` para interpretarlos. **Y no escribes el brief** ([[D-060]]): lo
redacta y lo escribe el agente, que es su autor. Vale **aunque las tools estuvieran disponibles**
([[D-038]]).

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo del workflow**: la primera palabra (solo `generate`)
- **Path del spec**: primer argumento posicional tras el modo
- **Path del PRD** opcional mediante `--prd`
- **Path de salida del brief** opcional mediante `--output`
- **Modo de decision** opcional mediante `--mode` (`guided`, `hybrid`, `auto`)
- **Preset** opcional mediante `--preset`
- **Modo enseñanza** opcional mediante `--learn`: activa explicaciones extendidas en cada pregunta, ideal para diseñadores junior. Compatible con `guided` y `hybrid`.

Si falta el modo o el path:
> "Uso: `/wf-design-intake generate <archivo_spec.md> [--prd <prd.md>] [--output DESIGN_BRIEF.md] [--mode guided|hybrid|auto] [--preset <name>] [--learn]`"

Si `--mode` no se pasa, usa `hybrid` por defecto.

## Paso 2: Verificar el Spec

Comprobacion **mecanica**, sin leer el contenido:

```bash
!test -f "<path_spec>" && echo EXISTE || echo NO_EXISTE
!grep -Eqi '^\s*>?\s*\**Estado\**\s*:?\s*\**\s*VALIDADO' "<path_spec>" && echo VALIDADO || echo SIN_SELLAR
```

- `NO_EXISTE` → deten: el brief se cierra contra un spec, y ese path no existe.
- `SIN_SELLAR` → **no bloquea**, pero dilo al informar: un brief cerrado sobre un spec que aun puede
  cambiar hereda esa inestabilidad.

La valoracion de si el contenido es un Spec SDD utilizable **no la haces tu**: la hace tu delegado en
el Paso 6, que es quien lo lee con `kb-design-brief` en contexto.

## Paso 3: Obtener PRD

Si se paso `--prd`, comprueba que existe y **pasa su path**. Si no se paso, continua sin PRD: mejora
la calidad del brief, pero no es bloqueante.

## Paso 4: Determinar el path de salida y detectar brief existente

1. Resolver path:
   - Si se paso `--output`, usalo.
   - Si no (regla de layout): si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.design`, usa `<raíz>/<artifacts.design>/DESIGN_BRIEF.md`.
   - En otro caso, usa `DESIGN_BRIEF.md` en la raiz del producto (el directorio que contiene `features/` si el spec esta dentro de `features/<nombre>/` — directamente o en su subcarpeta `spec/` —, el mismo directorio en otros casos).

2. Comprobar si el archivo ya existe:
   - **Si existe**: leelo completo y **actualiza**, preservando las variables ya cerradas y revisando
     solo consistencia. Ese es el comportamiento por defecto **siempre**, no solo en `--mode auto`:
     es la via no destructiva, y las variables cerradas son decisiones de producto de una persona.
   - **Rehacerlo desde cero** descarta decisiones de producto ya tomadas por una persona, asi que
     **se pregunta aqui** con `AskUserQuestion` ([[D-024]]) — salvo que venga `--allow-overwrite-brief`,
     que es el usuario habiendolo elegido ya ([[D-026]]):
     - **Actualizar (recomendado)** → preserva las variables cerradas y revisa consistencia.
     - **Rehacer desde cero** → nombra en la pregunta lo que se descarta (las variables cerradas y su
       `## Update log`). Si declina, no se escribe nada.
   - **Si no existe**: continua normal, lo escribira tu delegado en el Paso 7.

Pasa el **path** del brief existente (si lo hay) al agente como base. Cualquier variable que cambie debe registrarse en una nueva seccion `## Update log` con `[<fecha>] <variable>: <antes> -> <despues> — <motivo>` por parte del agente.

## Paso 5: Buscar moodboard opcional

Busca `<basename>_design_moodboard.md`: en la subcarpeta `design/` de la feature si el spec esta en `features/<nombre>/spec/`; si no, en el mismo directorio del spec (layout plano legacy).

- Si existe, leelo completo y pasalo al agente como input adicional para `style_family`, `adjectives` y Visual Personality.
- Si no existe y el modo es `guided` o `hybrid` con `--learn` activo, ofrece capturar antes la inspiracion visual (es un paso previo, corto, que mejora `style_family` y `adjectives`). Descríbelo en lenguaje natural — el usuario te lo pide hablando, no tecleando el comando. Si declina o el modo es `auto`, continua sin moodboard.

## Paso 5b: Resolver `target_platforms` (familias) — D-011

`target_platforms` del brief usa el vocabulario de **familias** `{mobile, web, desktop}` (`kb-design-brief` Regla 11), no `iOS`/`Android`. Resuélvelo antes de delegar:

- Si `.sdd/project-init.json` declara `design_targets` (topología `design`, o consumer con repo de diseño aparte), **derívalo** con el subcomando determinista (no lo teclees):
  ```bash
  !python3 "$SDD_HOME/scripts/sdd-init-detect.py" target-platforms --targets "<design_targets separados por comas>" --json
  ```
  Usa su `.target_platforms`.
- Si no hay `design_targets`, tómalo de las superficies del proyecto (init/spec/PRD), con el mismo vocabulario de familias. Default `[mobile]` si nada lo declara.

Pásalo al agente en el prompt del Paso 6.

## Paso 6: Cerrar el brief

El cierre tiene **dos mitades y en este orden**: primero el experto propone contra sus KBs, luego el
usuario decide lo que le toca decidir. Nunca al reves — proponer sin las KBs es opinar, y decidir sin
el usuario es fabricar la direccion visual del producto.

### 6A · Propuesta del experto (delegada)

Delega con la tool `Agent` ([[D-043]]), `subagent_type: "design-system-architect"` y
**`run_in_background: false`**, en modo `design-intake-propose`. El agente **lee los paths** (spec, PRD,
brief existente, moodboard) y devuelve, **sin escribir nada todavia**: valor propuesto para `preset`,
`style_family`, `clarity_vs_brand`, `density`, `color_energy` y `motion_level`, cada uno con su
**razon** y su **fuente** (spec / PRD / moodboard / default del taxonomy), mas los conflictos que
detecte y las variables que no pueda cerrar sin el usuario.

En `--mode auto` este paso **es el unico**: no hay 6B, y se va directo al 6C con la propuesta como
decision, marcando `autonomy_policy: ai-default`.

### 6B · Las decisiones que son del usuario (aqui, con `AskUserQuestion`)

- **`guided`**: recorre el arbol de decision de `kb-design-style-decision-tree` **pregunta a pregunta**,
  usando la propuesta del 6A como opcion recomendada de cada una. Con `--learn`, cada pregunta lleva su
  micro-explicacion del coste de decidirla mal.
- **`hybrid`** (por defecto): presenta las seis variables propuestas **en una sola tanda** y pide
  confirmacion o correccion. Lo que no se corrige se toma como aprobado.
- **Los conflictos que el 6A haya detectado se resuelven aqui**, no en silencio: `guided` pregunta,
  `hybrid` propone la correccion y la confirma, `auto` autocorrige y lo documenta.

Cada respuesta del usuario viaja **literal** al 6C. No la interpretes ni la normalices: traducirla al
vocabulario del taxonomy es trabajo del agente, y con su razon escrita.

### 6C · Redaccion del brief (delegada)

Delega otra vez, mismo `subagent_type` y mismo flag, en modo `design-intake-close`, con:

```text
Modo: design-intake-close
Path del spec: <path>
Contenido del spec:
---
<contenido completo>
---
Contenido del PRD (si existe):
---
<contenido o "no proporcionado">
---
Contenido del DESIGN_BRIEF.md existente (si aplica):
---
<contenido o "no existe">
---
Contenido del moodboard (si existe):
---
<contenido o "no existe">
---
Modo de decision: <guided|hybrid|auto>
Modo enseñanza (--learn): <true|false>
Preset solicitado (--preset): <valor o "ninguno">
target_platforms (resuelto en Paso 5b, familias mobile|web|desktop): <lista>
Decisiones del usuario (Paso 6B), literales: <variable: respuesta, una por linea, o "ninguna (modo auto)">
Path de salida del brief: <path resuelto en el Paso 4>

INSTRUCCION:
1. Aplica `kb-design-brief`, `kb-design-style-decision-tree` y `kb-design-style-taxonomy` para cerrar las variables del brief:
   - **Manda lo que dijo el usuario**, tal como viene arriba. Tu trabajo es traducirlo al vocabulario del taxonomy y dejar escrita esa traduccion, no sustituirla por tu criterio.
   - Lo que el usuario no decidio se cierra desde spec/PRD/moodboard, y **cada variable asi cerrada registra su fuente** en `## Inferencias automaticas`.
   - En modo `auto` no hubo usuario: marca `autonomy_policy: ai-default` y registra la fuente de todas.
2. Aplica deteccion de preset segun la heuristica de `kb-design-brief`. Si se paso --preset, usalo directo. Si ninguno encaja, usa `none`.
3. Valida consistencia con los checks de `kb-design-brief`. Los conflictos ya vienen resueltos del Paso 6B; si aparece uno nuevo que no puedas resolver sin el usuario, devuelvelo como `DESIGN_GAP` en vez de decidirlo. No cierres con conflictos silenciosos.
4. Genera el contenido completo del `DESIGN_BRIEF.md` siguiendo la plantilla de `kb-design-brief`. El brief debe dejar claro: quien decide ambiguedades, direccion visual base, tradeoff claridad vs marca y que puede completar la IA mas adelante.
5. Fija `target_platforms` con el valor resuelto en el Paso 5b (familias `{mobile, web, desktop}`, `kb-design-brief` Regla 11 — nunca `iOS`/`Android`). Si quedara indefinido, márcalo `DESIGN_GAP`.
6. Si una decision critica no puede tomarse (contradiccion irresoluble), devuelve `DESIGN_GAP` con la variable concreta y NO escribas el brief.
7. Si no hay `DESIGN_GAP`, **escribe tu el `DESIGN_BRIEF.md`** en el path de salida e informa de la ruta: eres su autor ([[D-059]]/[[D-060]]).
```

## Paso 7: Comprobar el resultado

1. Si el agente devuelve `DESIGN_GAP`, **no hay brief**: reporta al usuario las variables pendientes y deten.
2. En caso contrario, comprueba que el fichero esta donde dijo:

   ```bash
   !test -f "<path_brief>" && echo ESCRITO || echo FALTA
   ```

   `FALTA` → no lo escribas tu ([[D-060]]): reporta que el agente no dejo el artefacto y para. Que el
   informe diga que lo escribio no es que este escrito ([[D-047]]).

## Paso 8: Informar al usuario

Reporta:
- path del `DESIGN_BRIEF.md`
- modo usado (`guided`, `hybrid`, `auto`)
- preset usado o `none`
- familia visual cerrada
- policy de autonomia
- siguiente paso recomendado:
  > "Ahora ejecuta `/wf-design-system generate <feature_spec.md> [--prd <prd.md>] [--brief <DESIGN_BRIEF.md>]`"

> Nota: un brief cerrado en modo `auto` con `autonomy_policy: ai-default` deja la direccion visual **no anclada** aguas abajo. `wf-design-system` lo detecta y pedira confirmacion humana de la direccion antes de escribir el `DESIGN.md`; sin confirmacion, el `DESIGN.md` nace `origin: generated-provisional` (ciclo de vida en `kb-design-governance` Regla 5). Si quieres anclar la direccion ya en el brief, usa `--mode guided` o `hybrid`.
