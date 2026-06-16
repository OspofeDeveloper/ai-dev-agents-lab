---
name: wf-design-system
description: "Crea o actualiza el DESIGN.md de un producto desde un feature spec validado y un DESIGN_BRIEF.md cerrado: identidad visual persistente que alimenta el generador de UI (Stitch en mobile, generadores web/desktop) y futuros prototipos de feature."
when_to_use: "Activa en frases como 'crea el DESIGN.md', 'genera el sistema visual desde el spec', 'prepara el contrato visual del producto', 'actualiza el DESIGN.md'. No activa para generar planes KMM ni tasks."
argument-hint: "generate <feature_spec.md> [--prd <prd.md>] [--brief <DESIGN_BRIEF.md>] [--design-file DESIGN.md] [--no-brief]"
effort: high
allowed-tools: [Read, Write, Bash, Agent, AskUserQuestion, WebSearch, WebFetch]
user-invocable: true
---

# design-system — Orquestador del Flujo SDD (Etapa Design)

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el Spec esta listo, delegas la definicion del sistema visual al agente `design-architect`, y escribes el `DESIGN.md` resultante.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (solo `generate` esta soportado)
- **Path del spec**: primer argumento posicional tras el modo
- **Path del PRD** opcional mediante `--prd`
- **Path del DESIGN_BRIEF.md** opcional mediante `--brief`
- **Path de DESIGN.md** opcional mediante `--design-file`
- **Override de brief** opcional mediante `--no-brief` (solo para casos legacy o experimentacion)

Si no hay argumento o el modo no es valido, informa:
> "Uso: `/wf-design-system generate <archivo_spec.md> [--prd <prd.md>] [--brief <DESIGN_BRIEF.md>] [--design-file DESIGN.md] [--no-brief]`"

## Paso 2: Verificar el Spec

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Deten la ejecucion si ocurre cualquiera de estos casos:
   - hay HUs `[INCOMPLETO]`
   - hay items `[CRITICO]_(pendiente)_`
   - `status_sync: stale`
   - `status_sync: needs_review`
4. Si el archivo no parece un Spec SDD validado (no contiene "Historias de Usuario" y "Criterios de Aceptacion"), informa:
   > "Este archivo no parece un Spec SDD validado. Primero ejecuta los workflows de spec."

## Paso 2b: Resolver DESIGN_BRIEF.md (gate obligatorio)

El `DESIGN_BRIEF.md` es precondicion de este workflow salvo override explicito. Reduce diseno generico al cerrar direccion visual y autonomia antes de tocar tokens.

1. Si se paso `--brief <path>`, lee ese archivo directamente y continua.
2. Si no se paso `--brief`, busca `DESIGN_BRIEF.md` en la raiz del producto:
   - si `.sdd/project-init.json` declara `artifacts.design`, en ese directorio
   - si el spec esta dentro de `features/<nombre>/` (directamente o en su subcarpeta `spec/`), en el directorio que contiene `features/`
   - en otros casos, usa el mismo directorio del spec
3. Si existe, leelo y usalo como fuente prioritaria para direccion visual.
4. Si **no existe** y **no se paso `--no-brief`**, deten el flujo con:
   > "No hay `DESIGN_BRIEF.md` cerrado. Ejecuta primero `/wf-design-intake generate <feature_spec.md>` para fijar direccion visual y autonomia. Si quieres saltarte el intake (modo legacy o experimental), reintenta con `--no-brief`."
5. Si se paso `--no-brief`, continua sin brief y deja documentada esta decision en el output (campo `brief_override: true` en el rationale).

## Paso 2c: Obtener PRD

Si se paso `--prd <path>` en los argumentos, lee ese archivo directamente.

Si no se paso `--prd`:
1. Intenta resolver automaticamente un PRD en la raiz del producto o en rutas obvias del repo si existe uno con naming reconocible.
2. Si encuentras uno, leelo y usalo.
3. Si no encuentras ninguno, continua sin PRD.

El PRD enriquece la derivacion de Visual Personality con nombre, vision y audiencia reales del producto, pero no es bloqueante.

## Paso 2d: Research de apps de referencia

1. Busca `<basename>_design_discovery.md` (donde `<basename>` es el nombre del spec sin `_spec.md`): en la subcarpeta `design/` de la feature si el spec esta en `features/<nombre>/spec/`; si no, en el mismo directorio del spec (layout plano legacy).
2. **Si existe**: leelo completo y usalo como input de Reference Apps en el Paso 4. Salta el research inline.
3. **Si no existe**: ejecuta research inline ligero:
   - Deriva 2-3 queries adaptadas (sector + actor + flujos dominantes + tono funcional).
   - Ejecuta WebSearch y guarda un resumen de 3-5 apps con su aspecto concreto.
   - Si los resultados son pobres, continua sin research — el agente marcara `DESIGN_GAP` en Reference Apps.
4. Si el modo de trabajo del usuario prefiere validacion interactiva, sugiere ejecutar `/wf-design-discover <feature_spec.md>` antes de continuar — produce un discovery validado y reutilizable.

## Paso 2e: Enforce de `reference_apps_policy`

Si hay `DESIGN_BRIEF.md` y su `reference_apps_policy` es `required`:
- si el research no produjo referencias utilizables, deten el flujo
- no delegues al agente
- informa:
  > "El `DESIGN_BRIEF.md` exige `reference_apps_policy: required` y no se obtuvo research suficiente. Completa referencias reales o relaja la policy a `preferred`/`optional`."

Si la policy es `preferred` u `optional`, continua.

## Paso 3: Determinar paths y cargar starter kit

- Si se paso `--design-file`, usa ese path.
- Si no (regla de layout): si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.design`, crea o actualiza `<raíz>/<artifacts.design>/DESIGN.md`.
- En otro caso, crea o actualiza `DESIGN.md` en el directorio raiz del producto:
  - si el spec esta dentro de `features/<nombre>/` (directamente o en su subcarpeta `spec/`), usa el directorio que contiene `features/`
  - en otros casos, usa el mismo directorio del spec

Si el archivo ya existe, leelo completo para usarlo como base.

Si el archivo **NO existe** y el brief declara `product_preset` distinto de `none`:
- carga el frontmatter base del preset desde `${CLAUDE_SKILL_DIR}/../kb-design-expert/references/preset_starter_kits.md` de `kb-design-expert`
- carga los componentes base del preset desde `${CLAUDE_SKILL_DIR}/../kb-design-expert/references/preset_components.md` de `kb-design-expert`
- arranca con ese starter kit al 70% en lugar de DESIGN.md en blanco
- pasa este contenido base al agente como `DESIGN.md actual` para que lo precise (no parta de cero)

## Paso 4: Delegar al agente design-architect

Invoca al agente siguiendo las **Reglas 2, 3, 4 y 6** de `kb-design-system-contract` (formato y secciones, Visual Personality, Reference Apps, materializar el brief sin reabrirlo), la **Regla 3** de `kb-design-expert` (orden de derivación: dirección de producto primero) y la **Regla 2** de `kb-design-governance` (política de evolución extender vs mutar), mas la jerarquía de `kb-design-brief` y la taxonomía de `kb-design-style-taxonomy`.

Construye el prompt usando la plantilla de `${CLAUDE_SKILL_DIR}/references/design_system_prompt.md`, pasando el contenido de: spec, PRD (si existe), brief (si existe), research de apps (si existe), y DESIGN.md actual (si existe).

## Paso 5: Manejar DESIGN_GAPs

Si el agente devuelve `DESIGN_GAP` o `DESIGN_GAPs`:
- informa la lista al usuario
- no escribas el archivo
- sugiere completar el spec o aportar contexto visual de producto

## Paso 5b: Anclar la direccion visual (confirmacion humana)

Determina si la **direccion visual quedo no anclada** — es decir, sin fuente humana fiable de `style_family`/paleta/`motion_level`. Aplica el criterio de `kb-design-governance` Regla 5: la direccion esta NO anclada si se cumple **cualquiera** de:

- se invoco con `--no-brief` (Paso 2b dejo `brief_override: true`), o
- el brief resuelto se cerro en modo `auto` con `autonomy_policy: ai-default` sin confirmacion humana (lee `autonomy_policy` del `DESIGN_BRIEF.md` del Paso 2b), y/o
- el research de Reference Apps fue pobre o ausente (mismo criterio que el Paso 2d/2e marca como `DESIGN_GAP` en Reference Apps).

**Si la direccion esta anclada** (brief cerrado con `autonomy_policy` distinto de `ai-default`, o research suficiente, sin `--no-brief`): salta este paso. El `DESIGN.md` nacera con `origin: generated`, `direction_confidence: confirmed`.

**Si la direccion esta NO anclada:** antes de escribir, presenta al usuario las decisiones de direccion que el agente infirio y pide confirmacion explicita con `AskUserQuestion`:
- `style_family` (y `secondary_family` si aplica)
- paleta: `primary` y `accent`/secundario
- `motion_level`

Pregunta si confirma esa direccion visual inferida. Segun la respuesta:

- **Confirma** → el `DESIGN.md` nace con `origin: generated`, `direction_confidence: confirmed`. No se aplican marcadores `[INFERIDO]` de direccion ni sello provisional.
- **No confirma, o no hay interaccion** (modo headless/CI: `SDD_NON_INTERACTIVE=1` o `CI=true`, o el usuario no responde) → el `DESIGN.md` nace **provisional**:
  - frontmatter con `origin: generated-provisional` y `direction_confidence: provisional`,
  - los campos de direccion inferidos sin evidencia (`style_family`, paleta, `motion_level`) se marcan `[INFERIDO]` (marcador informativo de la fase, SSoT en `kb-design-characterization`; **NO bloquea ningun gate**),
  - la entrada de `## Changelog` refleja el estado: `[direccion: provisional]`.

**No bloquees indefinidamente.** Sin interaccion, el camino por defecto es **escribir provisional, no abortar**. El sello es informativo; la promocion a `confirmed` ocurre despues en `wf-design-validate` con confirmacion humana explicita (ver `kb-design-governance` Regla 5).

## Paso 6: Escribir y validar el resultado

Antes de escribir, verifica si el archivo ya existe:
```bash
!test -f "<path_design>" && echo "EXISTE" || echo "NO_EXISTE"
```
Si ya existe → pregunta al usuario:
> "Ya existe `<path_design>`. ¿Deseas regenerarlo?"
- Si responde **no** → informa el path del artefacto existente y detén.
- Si responde **sí** → continúa.

1. Escribe el output del agente en el path destino como `DESIGN.md`.
2. Ejecuta el linter de Google design.md sobre el archivo generado:
   ```bash
   npx @google/design.md lint <path_design>
   ```
3. Segun el resultado:
   - **Sin errores**: confirma al usuario que el archivo supera la validacion `@google/design.md`.
   - **Con errores**: muestra la lista completa. Indica cuales requieren correccion manual (tokens rotos, referencias inexistentes, contraste WCAG insuficiente, orden de secciones canonicas incorrecto).
   - **npx no disponible o fallo de entorno**: informa al usuario e indica que puede ejecutarlo manualmente con `npx @google/design.md lint <path_design>`.

## Paso 7: Informar al usuario

- path del `DESIGN.md` generado
- si se uso `DESIGN_BRIEF.md`, indicalo explicitamente
- resultado de la validacion del linter (OK, errores o no ejecutado)
- breve resumen del sistema visual: paleta principal, personalidad visual derivada y apps de referencia usadas
- siguiente paso recomendado:
  > "Ahora ejecuta `/wf-design-feature-prototype generate <feature_spec.md> [--design-file <DESIGN.md>]`"
