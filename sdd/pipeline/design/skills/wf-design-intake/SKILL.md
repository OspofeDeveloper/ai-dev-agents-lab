---
name: wf-design-intake
description: "Cierra el DESIGN_BRIEF.md antes de generar el sistema visual: fija modo de decision, preset, familia visual, densidad, profundidad, motion y policy de referencias y autonomia. Delega a design-architect. Modos guided, hybrid y auto."
when_to_use: "Activa con frases como 'cierra el brief de diseño', 'necesito el design brief', 'quiero definir el brief visual', 'preparar el brief antes de diseñar', 'genera el DESIGN_BRIEF.md'. No activa si ya existe un DESIGN_BRIEF.md y solo se quiere actualizar (usa wf-design-delta) ni para generar directamente el DESIGN.md sin brief (el brief es gate obligatorio)."
argument-hint: "generate <feature_spec.md> [--prd <prd.md>] [--output DESIGN_BRIEF.md] [--mode guided|hybrid|auto] [--preset <name>] [--learn]"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: design-architect
user-invocable: true
---

# design-intake — Orquestador del Flujo SDD (Pre-etapa Design)

Tu rol es de **orquestador puro**: parseas argumentos, verificas precondiciones, derivas contexto base, delegas el cierre del brief al agente `design-architect` (modo `design-intake`) y escribes el `DESIGN_BRIEF.md` resultante. No tomas decisiones de direccion visual por tu cuenta.

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

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Si no parece un Spec SDD validado, deten con:
   > "Este archivo no parece un Spec SDD validado. Primero ejecuta los workflows de spec."

## Paso 3: Obtener PRD

Si se paso `--prd`, leelo.
Si no se paso, continua sin PRD. El PRD mejora la calidad del brief, pero no es bloqueante.

## Paso 4: Determinar el path de salida y detectar brief existente

1. Resolver path:
   - Si se paso `--output`, usalo.
   - Si no (regla de layout): si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.design`, usa `<raíz>/<artifacts.design>/DESIGN_BRIEF.md`.
   - En otro caso, usa `DESIGN_BRIEF.md` en la raiz del producto (el directorio que contiene `features/` si el spec esta dentro de `features/<nombre>/` — directamente o en su subcarpeta `spec/` —, el mismo directorio en otros casos).

2. Comprobar si el archivo ya existe:
   - **Si existe**: leelo completo. Pregunta al usuario:
     > "Ya existe `DESIGN_BRIEF.md`. ¿Quieres (a) revisarlo y actualizar variables concretas, (b) sobrescribirlo desde cero, o (c) cancelar?"
   - En modo `--mode auto` sin interaccion: por defecto `actualizar` preservando las variables ya cerradas y solo revisando consistencia.
   - **Si no existe**: continua normal, lo crearas en el Paso 7.

Pasa el contenido del brief existente (si lo hay) al agente como base. Cualquier variable que cambie debe registrarse en una nueva seccion `## Update log` con `[<fecha>] <variable>: <antes> -> <despues> — <motivo>` por parte del agente.

## Paso 5: Buscar moodboard opcional

Busca `<basename>_design_moodboard.md`: en la subcarpeta `design/` de la feature si el spec esta en `features/<nombre>/spec/`; si no, en el mismo directorio del spec (layout plano legacy).

- Si existe, leelo completo y pasalo al agente como input adicional para `style_family`, `adjectives` y Visual Personality.
- Si no existe y el modo es `guided` o `hybrid` con `--learn` activo, sugiere al usuario ejecutar primero `/wf-design-moodboard`. Si rechaza o el modo es `auto`, continua sin moodboard.

## Paso 6: Delegar al agente design-architect

Construye el prompt para el agente con:

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

INSTRUCCION:
1. Aplica `kb-design-brief`, `kb-design-style-decision-tree` y `kb-design-style-taxonomy` para cerrar las variables del brief segun el modo de decision:
   - `guided`: recorre el arbol de decision pregunta a pregunta. Si --learn, anade micro-explicacion por pregunta sobre el coste de una decision mal tomada.
   - `hybrid`: propon valor para preset, style_family, clarity_vs_brand, density, color_energy y motion_level; pide confirmacion. Si no se corrige, toma como aprobado.
   - `auto`: decide todas las variables desde spec/PRD/moodboard. Marca `autonomy_policy: ai-default` y registra fuente de cada variable en `## Inferencias automaticas`.
2. Aplica deteccion de preset segun la heuristica de `kb-design-brief`. Si se paso --preset, usalo directo. Si ninguno encaja, usa `none`.
3. Valida consistencia con los checks de `kb-design-brief`. Resuelve conflictos segun el modo (preguntar en guided, proponer correccion en hybrid, autocorregir y documentar en auto). No cierres con conflictos silenciosos.
4. Genera el contenido completo del `DESIGN_BRIEF.md` siguiendo la plantilla de `kb-design-brief`. El brief debe dejar claro: quien decide ambiguedades, direccion visual base, tradeoff claridad vs marca y que puede completar la IA mas adelante.
5. Si una decision critica no puede tomarse (usuario no responde, contradiccion irresoluble), devuelve `DESIGN_GAP` con la variable concreta y NO produzcas el brief.
```

Invoca el agente `design-architect` con ese prompt.

## Paso 7: Escribir el brief

1. Si el agente devuelve `DESIGN_GAP`, no escribas el archivo. Reporta al usuario las variables pendientes y deten.
2. En caso contrario, escribe el contenido devuelto por el agente en el path resuelto en el Paso 4.

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
