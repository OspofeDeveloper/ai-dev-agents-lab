---
name: wf-design-intake
description: "Cierra un DESIGN_BRIEF.md antes de generar el sistema visual. Guia al usuario o a la IA para fijar modo de decision, preset, familia visual, densidad, profundidad, motion, policy de referencias y autonomia, reduciendo ambiguedades antes de crear DESIGN.md."
when_to_use: "Activa con frases como 'cierra el brief de diseño', 'necesito el design brief', 'quiero definir el brief visual', 'preparar el brief antes de diseñar', 'genera el DESIGN_BRIEF.md'. No activa si ya existe un DESIGN_BRIEF.md y solo se quiere actualizar (usa wf-design-delta) ni para generar directamente el DESIGN.md sin brief (el brief es gate obligatorio)."
argument-hint: "generate <feature_spec.md> [--prd <prd.md>] [--output DESIGN_BRIEF.md] [--mode guided|hybrid|auto] [--preset <name>] [--learn]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
---

# design-intake — Orquestador del Flujo SDD (Pre-etapa Design)

Tu rol es cerrar un `DESIGN_BRIEF.md` de producto antes de generar `DESIGN.md`.

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
> "Uso: `/wf-design-intake generate <archivo_spec.md> [--prd <prd.md>] [--output DESIGN_BRIEF.md] [--mode guided|hybrid|auto] [--preset <name>]`"

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
   - Si no, usa `DESIGN_BRIEF.md` en la raiz del producto (dos niveles arriba si el spec esta en `features/<nombre>/`, en el mismo directorio en otros casos).

2. Comprobar si el archivo ya existe:
   - **Si existe**: leelo completo y trata sus decisiones como base. Pregunta al usuario:
     > "Ya existe `DESIGN_BRIEF.md`. ¿Quieres (a) revisarlo y actualizar variables concretas, (b) sobrescribirlo desde cero, o (c) cancelar?"
   - En modo `--mode auto` sin interaccion: por defecto `actualizar` preservando las variables ya cerradas y solo revisando consistencia.
   - **Si no existe**: continua normal, lo crearas en el Paso 9.

Si se va a actualizar, cualquier variable que cambie debe registrarse en una nueva seccion `## Update log` con `[<fecha>] <variable>: <antes> -> <despues> — <motivo>`.

## Paso 5: Derivar contexto base

Extrae del spec y PRD, si existe:
- categoria de producto
- actor principal
- tarea dominante
- tono funcional
- riesgos de mala UX
- necesidad probable de claridad vs diferenciacion

Busca tambien `<basename>_design_moodboard.md` en el mismo directorio del spec. Si existe, leelo:
- usa las pistas de `style_family` como propuestas iniciales para el arbol de decision
- usa los adjetivos sugeridos como punto de partida para `adjectives`
- usa la atmosfera y referencias como input adicional para Visual Personality

Si no existe el moodboard, en modos `guided` o `hybrid` con `--learn` activo, sugiere al usuario ejecutar primero `/wf-design-moodboard` para capturar inspiracion. Si el usuario rechaza o esta en modo `auto`, continua.

Usa `kb-design-style-taxonomy`, `kb-design-brief` y `kb-design-style-decision-tree` como criterio conceptual, aunque no los cites como texto al usuario salvo que haga falta.

## Paso 6: Resolver el modo de decision

### Si `--mode guided`

Aplica el arbol de decision de `kb-design-style-decision-tree` (Reglas 2-9) en orden secuencial. Por cada pregunta:

1. Lanza la pregunta concreta del arbol.
2. Si `--learn` esta activo, anade una micro-explicacion (1-2 frases) sobre el coste de una decision mal tomada: "Si eliges `color_energy: high` aqui, la legibilidad de listas densas baja porque el ojo prioriza el acento sobre el contenido".
3. Recoge la respuesta. Si el usuario duda, ofrece el default conservador de la regla aplicable y avanza.

Cierra en este orden:
- `style_family` (Regla 2 del arbol)
- `clarity_vs_brand` (Regla 3)
- `density` (Regla 4)
- `depth` (Regla 5)
- `color_energy` (Regla 6)
- `motion_level` (Regla 7)
- `typography_mode` (Regla 8 — propon default segun familia y pide confirmacion)
- `voice_tone` (Regla 9 — propon default y pide confirmacion)
- `target_platforms`, `accessibility_target`, `reference_apps_policy` (suelen venir del spec o PRD; preguntar solo si no se pueden inferir)
- `product_preset` (si encaja claramente con uno de los presets, proponerlo al final como atajo; el preset acelera, no sustituye)
- `autonomy_policy` (normalmente `strict-user-control` cuando el modo es `guided`)

Si el usuario no responde una decision critica, deten y no escribas el brief.

### Si `--mode hybrid`

Propone un valor para cada variable critica y presentalo como recomendacion breve al usuario.
Pide confirmacion o correccion solo de:
- preset
- style_family
- clarity_vs_brand
- density
- color_energy
- motion_level

Si el usuario no corrige, toma la propuesta como aprobada.

### Si `--mode auto`

Decide todas las variables desde spec y PRD.
Marca en el brief que la autonomia es `ai-default`.

**Trazabilidad obligatoria**: por cada variable cerrada, registra la fuente de la inferencia. Fuentes validas:
- `spec`: extraida o derivada del feature spec
- `PRD`: extraida o derivada del PRD
- `preset`: heredada del preset aplicado
- `inferred`: deducida por heuristica del agente sin fuente directa

Esta tabla de trazabilidad se incluye en la seccion `## Inferencias automaticas` del brief (ver template). Permite al usuario auditar por que cada variable quedo como quedo y revertir las que considere mal inferidas.

## Paso 7: Aplicar presets (con deteccion automatica)

Antes de aplicar presets, **detectar automaticamente** el mas probable desde el spec y PRD usando esta heuristica:

- B2B / dashboard / backoffice / herramienta de trabajo → `b2b-operational`.
- Fintech / banca / pagos / regulado financiero → `fintech-trust`.
- Salud / mindfulness / wellness / bienestar → `health-calm`.
- Consumer / lifestyle / social / fitness / engagement → `consumer-lifestyle`.
- Media / lectura / contenido curado / luxury → `content-editorial`.

Comportamiento por modo:

- **`auto`**: aplica el preset detectado sin preguntar. Marca `product_preset` como `inferred` en el brief.
- **`hybrid`**: propon el preset detectado al usuario y pide confirmacion:
  > "Detecte que este producto encaja con el preset `<X>` por <razon corta>. ¿Confirmar o cambiar? (confirmar / cambiar a <Y> / none)"
- **`guided`**: muestra los presets disponibles y pide al usuario que elija explicitamente, mostrando una linea por cada uno.

Si el usuario proporciona `--preset` en CLI, respeta esa eleccion y omite la deteccion.

Cuando se aplica un preset:
- carga los defaults de `${CLAUDE_SKILL_DIR}/../kb-design-brief/references/design_presets.md` de `kb-design-brief`
- usa esos defaults como base
- ajusta solo lo que contradiga al producto real
- documenta en el brief que `product_preset` y `source: preset|user|inferred`

Si tras la deteccion ningun preset encaja, usa `none` y decide campo a campo.

## Paso 8: Validar consistencia

Antes de escribir el archivo:
1. Revisa conflictos con `${CLAUDE_SKILL_DIR}/../kb-design-brief/references/consistency_checks.md`.
2. Si detectas una contradiccion:
   - en `guided`, pide al usuario resolverla
   - en `hybrid`, propon una correccion y pide confirmacion
   - en `auto`, autocorrige la variable y documenta la razon

No cierres un brief con conflictos silenciosos.

## Paso 9: Escribir el brief

Escribe un `DESIGN_BRIEF.md` usando el formato de `${CLAUDE_SKILL_DIR}/../kb-design-brief/references/design_brief_template.md` de `kb-design-brief`.

El brief debe dejar claro:
- quien decide las ambiguedades
- cual es la direccion visual base
- que tradeoff manda entre claridad y marca
- que puede completar la IA mas adelante y que no

## Paso 10: Informar al usuario

Reporta:
- path del `DESIGN_BRIEF.md`
- modo usado (`guided`, `hybrid`, `auto`)
- preset usado o `none`
- familia visual cerrada
- policy de autonomia
- siguiente paso recomendado:
  > "Ahora ejecuta `/wf-design-system generate <feature_spec.md> [--prd <prd.md>] [--brief <DESIGN_BRIEF.md>]`"
