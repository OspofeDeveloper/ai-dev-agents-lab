---
name: wf-design-feature-prototype
description: "Deriva flows, views y un prompt de ensamblaje tool-agnostic (target_tool stitch en mobile, web-generic en web/desktop) de una feature desde su _spec.md, el DESIGN.md y el DESIGN_BRIEF.md, listos para contrastar con cliente antes del plan tecnico."
when_to_use: "Activa en frases como 'genera las vistas para Stitch', 'crea el prototipo de la feature', 'prepara flows y prompt de diseno', 'deriva las pantallas desde el spec'. No activa para modificar el spec, ni para generar plan o tasks."
argument-hint: "generate <feature_spec.md> [--design-file DESIGN.md] [--brief DESIGN_BRIEF.md] [--no-brief]"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: design-feature-architect
user-invocable: true
---

# design-feature-prototype — Orquestador del Flujo SDD (Etapa Design)

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el Spec y el `DESIGN.md` estan listos, delegas la derivacion de artefactos al agente `design-feature-architect`, y escribes los resultados.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (solo `generate` esta soportado)
- **Path del spec**: primer argumento posicional
- **Path de DESIGN.md** mediante `--design-file` opcional
- **Path de DESIGN_BRIEF.md** mediante `--brief` opcional
- **Override de brief** opcional mediante `--no-brief` (solo legacy o experimental)

Si no hay argumento o el modo no es valido, informa:
> "Uso: `/wf-design-feature-prototype generate <archivo_spec.md> [--design-file DESIGN.md] [--brief DESIGN_BRIEF.md] [--no-brief]`"

## Paso 2: Verificar el Spec

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Deten la ejecucion si:
   - hay HUs `[INCOMPLETO]`
   - hay items `[CRITICO]_(pendiente)_`
   - `status_sync: stale`
   - `status_sync: needs_review`
4. Verifica que parece un Spec SDD validado.

## Paso 3: Resolver DESIGN.md

- Si se pasa `--design-file`, usalo.
- Si no, busca `DESIGN.md`:
  - si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.design`, en ese directorio
  - si el spec esta dentro de `features/<nombre>/` (directamente o en su subcarpeta `spec/`), en el directorio que contiene `features/`
  - en el mismo directorio en otros casos

Si no existe, deten:
> "No se encontro `DESIGN.md`. Primero ejecuta `/wf-design-system generate <spec.md>` o indica `--design-file`."

Lee `DESIGN.md` completo.

## Paso 3b: Resolver DESIGN_BRIEF.md (gate obligatorio)

El `DESIGN_BRIEF.md` es precondicion salvo override explicito: la feature debe heredar la misma policy de autonomia, `clarity_vs_brand` y `accessibility_target` que el sistema visual.

1. Si se pasa `--brief <path>`, leelo y continua.
2. Si no, busca `DESIGN_BRIEF.md`:
   - si `.sdd/project-init.json` declara `artifacts.design`, en ese directorio
   - si el spec esta dentro de `features/<nombre>/` (directamente o en su subcarpeta `spec/`), en el directorio que contiene `features/`
   - en el mismo directorio en otros casos
3. Si existe, leelo completo y pasalo al agente como fuente prioritaria.
4. Si **no existe** y **no se paso `--no-brief`**, deten el flujo con:
   > "No hay `DESIGN_BRIEF.md`. Ejecuta primero `/wf-design-intake generate <feature_spec.md>` para fijar direccion y autonomia. Para saltar el intake (legacy o experimental), reintenta con `--no-brief`."
5. Si se paso `--no-brief`, continua solo con `DESIGN.md` y deja documentada esta decision en el bundle resultante.

## Paso 3c: Resolver `target_tool` del ui_prompt

La noción de `target_tool` / `target_platforms` y la regla de selección son SSoT de `kb-design-feature-artifacts` Regla 7. Resuelve `target_platforms` con esta prioridad:
1. `target_platforms` del `DESIGN_BRIEF.md` si existe
2. `accessibility.target_platforms` del DESIGN.md
3. Si ninguno lo declara, asume `mobile` (compatibilidad con el destino histórico) y anótalo para el usuario.

Deriva las superficies a generar y su `target_tool`:
- una sola superficie `mobile` → un `ui_prompt`, `target_tool: stitch`
- una sola superficie `web`/`desktop` → un `ui_prompt`, `target_tool: web-generic`
- **multi-superficie** (p. ej. `[mobile, web]`) → **un `ui_prompt` por superficie** (no uno mezclado): `mobile`→`stitch`, `web`/`desktop`→`web-generic` (ver `kb-design-feature-artifacts` Regla 7, sección multi-superficie).

Pasa al agente en el Paso 5 la lista de superficies con su `target_tool` (una o varias). `flows`/`views` se generan una sola vez (agnósticos); el `ui_prompt` se genera por superficie.

## Paso 3d: Resolver design targets y divergencia (D-011)

Lee `design_targets` de `.sdd/project-init.json` (topología `design`, o el `design_targets` que declara un consumer). Decide si hay divergencia per-target (`kb-design-feature-artifacts` Regla 8):

- **Sin `design_targets`, o una sola base** (p. ej. `[mobile]`): NO hay overrides. `flows`/`views` se generan una sola vez como base agnóstica (comportamiento de siempre). Ignora el resto de este paso.
- **Design targets que divergen** (p. ej. `[mobile-android, mobile-ios]`, o plataformas con sistemas de componentes distintos): además de la base se generan **overrides per-view por target** bajo `targets/<design-target>/`, **solo** para las vistas/flujos que divergen de verdad. La especificidad de **componente nativo** (Material vs HIG) la aporta la capa `## Platform Components` del `DESIGN.md` (`kb-design-system-contract` Regla 11), **no** la vista — la vista solo se overridea por layout/composición.

Guarda `DESIGN_TARGETS` (los divergentes) para los Pasos 4 y 5.

## Paso 4: Determinar outputs y detectar features ya prototipadas

Determina los tres paths de salida con el resolutor determinista de layout (respeta el layout del spec de entrada):
```bash
!python3 .sdd/scripts/sdd-resolve-path.py write flows "<spec_path>"
!python3 .sdd/scripts/sdd-resolve-path.py write views "<spec_path>"
!python3 .sdd/scripts/sdd-resolve-path.py write ui-prompt "<spec_path>"
```
Crea los directorios intermedios antes de escribir. **Fallback** a mano:
- si el spec esta en la subcarpeta `spec/` de una feature → subcarpeta hermana `design/`: `features/<nombre>/design/`
- si el spec esta directamente en `features/<nombre>/` (layout plano legacy) o fuera de una feature → el mismo directorio del spec

Alli se crean `<feature>_flows.md`, `<feature>_views.md` y el/los `ui_prompt`, donde `<feature>` es el nombre base del spec sin `_spec.md`. El `ui_prompt` se nombra según las superficies resueltas en 3c:
- **una sola superficie** → `<feature>_ui_prompt.md` (sin sufijo, como hasta ahora).
- **multi-superficie** → uno por superficie: `<feature>_ui_prompt.mobile.md`, `<feature>_ui_prompt.web.md` (el resolutor `write ui-prompt` da el path base; añade el sufijo `.<superficie>` antes de `.md`).

**Si el Paso 3d marcó design targets divergentes**, los overrides cuelgan del mismo directorio de la base, en `targets/<design-target>/` (no sustituyen la base):
- `targets/<target>/<feature>_views.md` — SOLO las vistas que divergen (per-view, Regla 8).
- `targets/<target>/<feature>_flows.md` — solo si la navegación de ese target cambia.
- `targets/<target>/<feature>_ui_prompt.md` — si el ensamblaje del target diverge.
Un target sin divergencia real **no genera** override (hereda la base). La base nunca se duplica.

Antes de continuar, verifica si el artefacto principal ya existe:
```bash
!test -f "<feature>_flows.md" && echo "EXISTE" || echo "NO_EXISTE"
```
Si ya existe → pregunta al usuario:
> "Ya existen los artefactos de prototipado para `<feature>` (`_flows.md`, `_views.md`, `_ui_prompt.md`). ¿Deseas regenerarlos?"
- Si responde **no** → informa los paths existentes y detén.
- Si responde **sí** → continúa.

Antes de delegar, busca otras features ya prototipadas en el directorio hermano:
- Lista las features con `_views.md` y `_flows.md` existentes, en ambos layouts: `features/*/design/*` (subcarpetas) y `features/*/*` (plano legacy).
- Si las hay, lee los `_views.md` y `_flows.md` de hasta 3 features previas (las mas recientes) y pasalos al agente para que aplique `kb-design-conflict-expert`.
- Si es la primera feature del producto, no hace falta este chequeo.

## Paso 5: Delegar al agente design-feature-architect

Invoca al agente siguiendo la **Regla 3** de `kb-design-expert` (orden de derivación), las **Reglas 1, 2, 3 y 7** de `kb-design-feature-artifacts` (trazabilidad de cada vista, flows como secuencia, views como SSoT de pantalla, ui_prompt que ensambla sin redefinir) y la **Regla 6** de `kb-design-system-contract` (los artefactos materializan el brief sin reabrirlo), mas la jerarquia de fuentes definida en `kb-design-brief` Regla 10: `flows` describen secuencia y navegacion, `views` son la SSoT de la pantalla, `ui_prompt` debe ensamblar sin volver a definir, y el brief gobierna las decisiones cerradas.

Usa este prompt:

```text
Modo: feature-prototype
Path del spec: <path_spec>
Contenido del Spec:
---
<contenido_spec>
---
Contenido del DESIGN.md:
---
<contenido_design>
---
Contenido del DESIGN_BRIEF.md:
---
<contenido_brief_o_N/A>
---
Superficies a generar (resuelto en Paso 3c) — una por línea, con su target_tool:
- <superficie> → <stitch | web-generic>   (p. ej. "mobile → stitch", "web → web-generic")
---
Design targets divergentes (resuelto en Paso 3d; "ninguno" si no aplica):
<lista_design_targets_divergentes_o_ninguno>
---
Features ya prototipadas (views + flows resumidos, opcional):
---
<resumen_features_previas_o_N/A>
---
INSTRUCCION: produce los artefactos separados y completos:
1. <feature>_flows.md — una sola copia agnóstica de superficie (con `### Notas responsive` si hay varias superficies).
2. <feature>_views.md — una sola copia agnóstica de superficie (idem).
3. ui_prompt **por superficie** (kb-design-feature-artifacts Regla 7 es la SSoT del target):
   - una sola superficie → `<feature>_ui_prompt.md`.
   - varias superficies → uno por superficie: `<feature>_ui_prompt.mobile.md` (target_tool stitch), `<feature>_ui_prompt.web.md` (target_tool web-generic). Cada uno declara su `target_tool` y su `target_platforms` singular.
   Con `web-generic`, describe componentes en HTML semántico/ARIA, breakpoints y estados completos (loading/empty/error/focus/hover/disabled), y remite a `kb-a11y-web-expert` para a11y web sin recopiarla. Con `stitch`, mantén el formato Stitch mobile.
4. (SOLO si hay design targets divergentes) Por cada target que diverja, genera `targets/<target>/<feature>_views.md` con **solo las vistas que cambian** respecto a la base (per-view, kb-design-feature-artifacts Regla 8) y `targets/<target>/<feature>_flows.md` solo si la navegación de ese target cambia. La divergencia de **componente nativo** (Material vs HIG) se toma de `## Platform Components` del DESIGN.md (kb-design-system-contract Regla 11) — NO la redefinas en la vista; la vista solo overridea layout/composición. NO dupliques vistas que no divergen: heredan la base. La resolución consumidor es `base ⊕ override` (determinista, `sdd-design-resolve.py`).

Si se pasan features previas, ejecuta tambien una revision de conflictos siguiendo `kb-design-conflict-expert` (Reglas 1-5). Si detectas conflictos, listalos al final del bundle con el formato de la Regla 6 y NO escribas artefactos hasta que el usuario decida; si son falsos positivos, declara `[POSIBLE-CONFLICTO-DESIGN-XX]` segun Regla 7.

Aplica las reglas de kb-design-feature-artifacts, kb-design-system-contract y kb-design-brief que tienes en contexto:
- kb-design-feature-artifacts Regla 1: cada vista debe trazar a HU/Journey/CA del spec — condiciones de UI no trazables son comportamiento inventado
- kb-design-feature-artifacts Regla 2: flows capturan secuencia, precondiciones y transiciones — no estados visuales ni componentes
- kb-design-feature-artifacts Regla 3: views son la SSoT de pantalla — solo decisiones, condiciones trazables al spec, dependencias cross-feature marcadas con [Dependencia: F-XXX]
- kb-design-feature-artifacts Regla 7: ui_prompt ensambla sin redefinir — no copies tokens ni componentes de DESIGN.md
- kb-design-system-contract Regla 6: DESIGN.md y los artefactos de feature materializan el brief, no lo reabren (la jerarquia de fuentes vive en kb-design-brief Regla 10)
- kb-design-brief: respetar `clarity_vs_brand`, `target_platforms`, `accessibility_target`, `autonomy_policy` y guardrails relevantes ya cerrados

No inventes funcionalidad fuera del spec.
Si faltan datos criticos, devuelve DESIGN_GAPs y no produzcas artefactos parciales.

Formato de output: usa el bundle definido en ${CLAUDE_SKILL_DIR}/references/output_bundle_template.md de esta skill.
```

## Paso 6: Manejar DESIGN_GAPs

Si el agente devuelve `DESIGN_GAP` o `DESIGN_GAPs`:
- informa al usuario
- no escribas archivos

## Paso 7: Escribir resultados

Parsea la respuesta del agente usando el formato de bundle de `${CLAUDE_SKILL_DIR}/references/output_bundle_template.md`: extrae cada bloque `===FILE: <nombre>===` como archivo separado y escribe cada uno en su path correspondiente.

## Paso 8: Informar al usuario

- paths generados (base y, si aplica, los overrides `targets/<target>/...`)
- total de vistas derivadas; por target divergente, qué vistas overridea
- `target_tool` / `target_platforms` resueltos
- si se generaron overrides, recuerda cómo resolver un target (determinista):
  > `python3 .sdd/scripts/sdd-design-resolve.py resolve --base <feature>_views.md --override targets/<target>/<feature>_views.md --merged`
  > (sin `--override`, o si el target no tiene override, devuelve la base intacta)
- siguiente paso recomendado (según `target_tool`):
  > Con `stitch`: "Usa `<feature>_ui_prompt.md` junto con `DESIGN.md` y `DESIGN_BRIEF.md` si existe en Stitch para generar las vistas y, tras validar con cliente, continúa con `/wf-prepare-plan generate <feature_spec.md>` y después `/wf-plan-validate <feature_plan.md>`."
  > Con `web-generic`: "Usa `<feature>_ui_prompt.md` junto con `DESIGN.md` (y `DESIGN_BRIEF.md` si existe) con tu generador de UI web (v0, Lovable, bolt) o como guía de implementación a mano y, tras validar con cliente, continúa con `/wf-prepare-plan generate <feature_spec.md>` y después `/wf-plan-validate <feature_plan.md>`."
