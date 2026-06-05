---
name: wf-design-feature-prototype
description: "Deriva artefactos de prototipado visual de una feature a partir de su _spec.md, un DESIGN.md y, si existe, un DESIGN_BRIEF.md. Genera flows, views y prompt para Stitch listos para contrastar con cliente antes del plan tecnico."
when_to_use: "Activa en frases como 'genera las vistas para Stitch', 'crea el prototipo de la feature', 'prepara flows y prompt de diseno', 'deriva las pantallas desde el spec'. No activa para modificar el spec, ni para generar plan o tasks."
argument-hint: "generate <feature_spec.md> [--design-file DESIGN.md] [--brief DESIGN_BRIEF.md] [--no-brief]"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: design-architect
---

# design-feature-prototype — Orquestador del Flujo SDD (Etapa Design)

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el Spec y el `DESIGN.md` estan listos, delegas la derivacion de artefactos al agente `design-architect`, y escribes los resultados.

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

## Paso 4: Determinar outputs y detectar features ya prototipadas

Determina el directorio de salida:
- si el spec esta en la subcarpeta `spec/` de una feature → subcarpeta hermana `design/`: `features/<nombre>/design/` (crea el directorio si no existe)
- si el spec esta directamente en `features/<nombre>/` (layout plano legacy) o fuera de una feature → el mismo directorio del spec

Alli crea:
- `<feature>_flows.md`
- `<feature>_views.md`
- `<feature>_ui_prompt.md`

Donde `<feature>` es el nombre base del spec sin `_spec.md`.

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

## Paso 5: Delegar al agente design-architect

Invoca al agente siguiendo la **Regla 3**, la **Regla 4**, la **Regla 7**, la **Regla 8**, la **Regla 9** y la **Regla 14** de `kb-design-expert`, mas la jerarquia de fuentes definida en `kb-design-brief` Regla 10: `flows` describen secuencia y navegacion, `views` son la SSoT de la pantalla, `ui_prompt` debe ensamblar sin volver a definir, y el brief gobierna las decisiones cerradas.

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
Features ya prototipadas (views + flows resumidos, opcional):
---
<resumen_features_previas_o_N/A>
---
INSTRUCCION: produce tres artefactos separados y completos:
1. <feature>_flows.md
2. <feature>_views.md
3. <feature>_ui_prompt.md

Si se pasan features previas, ejecuta tambien una revision de conflictos siguiendo `kb-design-conflict-expert` (Reglas 1-5). Si detectas conflictos, listalos al final del bundle con el formato de la Regla 6 y NO escribas artefactos hasta que el usuario decida; si son falsos positivos, declara `[POSIBLE-CONFLICTO-DESIGN-XX]` segun Regla 7.

Aplica las reglas de kb-design-expert y kb-design-brief que tienes en contexto:
- Regla 4: cada vista debe trazar a HU/Journey/CA del spec — condiciones de UI no trazables son comportamiento inventado
- Regla 7: flows capturan secuencia, precondiciones y transiciones — no estados visuales ni componentes
- Regla 8: views son la SSoT de pantalla — solo decisiones, condiciones trazables al spec, dependencias cross-feature marcadas con [Dependencia: F-XXX]
- Regla 9: ui_prompt ensambla sin redefinir — no copies tokens ni componentes de DESIGN.md
- Regla 14: DESIGN.md y los artefactos de feature materializan el brief, no lo reabren (la jerarquia de fuentes vive en kb-design-brief Regla 10)
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

- paths generados
- total de vistas derivadas
- siguiente paso recomendado:
  > "Usa `<feature>_ui_prompt.md` junto con `DESIGN.md` y `DESIGN_BRIEF.md` si existe en Stitch para generar las vistas y, tras validar con cliente, continúa con `/wf-prepare-plan generate <feature_spec.md>` y después `/wf-plan-validate <feature_plan.md>`."
