---
name: wf-stack-create
description: "Crea el esqueleto de un nuevo overlay de stack (tech/<stack>) conforme a kb-sdd-stack-overlay-contract: directorios, install.sh, wf-<stack>-init (detect/configure), CLAUDE.md y opcionalmente variantes de agentes y KBs de plan/tasks. Delega la redaccion a sdd-author."
when_to_use: "Activa con frases como 'crea el overlay de android', 'añade soporte para next', 'nuevo stack flutter', 'scaffolding del tech target fastapi', 'quiero que SDD soporte el stack X'. No activa para crear skills sueltas (usa wf-skill-create), ni agentes sueltos (usa wf-agent-create), ni para inicializar un proyecto con un stack ya soportado (usa wf-project-init)."
argument-hint: "<stack> [--type <app|web|backend>] [--detect '<archivos/patrones que delatan el stack>'] [--with-agents] [--description <desc>]"
effort: medium
allowed-tools: [Read, Write, Bash, Agent, AskUserQuestion]
user-invocable: true
---

# wf-stack-create — Scaffolding de overlays de stack

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el overlay no existe, recopilas el brief y delegas la creación al agente `sdd-author`, que conoce el contrato (`kb-sdd-stack-overlay-contract`). No redactas el contenido del overlay directamente.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Stack**: primera palabra, en minúscula (ej. `android`, `next`, `fastapi`)
- **`--type`**: `app`, `web` o `backend` (obligatorio si no es deducible del nombre)
- **`--detect`**: condición de detección (archivos/patrones; ej. `"app/build.gradle.kts sin iosApp/"`)
- **`--with-agents`**: crear también variantes de `plan-architect`, `plan-auditor` y `task-generator`
- **`--description`**: descripción libre del stack y sus convenciones

Si `$ARGUMENTS` está vacío:
> "Uso: `/wf-stack-create <stack> [--type <app|web|backend>] [--detect '<condición>'] [--with-agents] [--description <desc>]`"

---

## Paso 2: Verificar que no existe

```bash
test -d "tech/<stack>" && echo "overlay-exists"
```

Si existe → detén:
> "❌ Ya existe `tech/<stack>/`. Para evolucionarlo usa `/wf-sdd-refactor tech/<stack> --reason <motivo>`."

Comprueba también solapamiento semántico con overlays existentes (`ls tech/`): si el stack pedido es una variante de uno existente (ej. `compose-multiplatform` vs `kmm`), pregunta al usuario antes de continuar.

---

## Paso 3: Completar el brief

Si falta `--type`, `--detect` o `--description`, pregunta con `AskUserQuestion` (una pregunta por dato faltante, opciones cerradas cuando aplique). Datos mínimos del brief:

- Tipo de proyecto y targets/runtime del stack
- Condición de detección para `wf-project-init` Paso 4
- Arquitectura prescriptiva (¿el stack impone capas/convenciones? → justifica `--with-agents`)
- Comandos canónicos de build y test
- Librerías/convenciones núcleo que el `project_state` debe capturar

---

## Paso 4: Delegar a sdd-author

Invoca `sdd-author` con este encargo:

> Crea el esqueleto del overlay `tech/<stack>/` siguiendo `kb-sdd-stack-overlay-contract` y los templates de `${CLAUDE_SKILL_DIR}/references/scaffold-templates.md`:
>
> 1. `tech/<stack>/install.sh` — desde el template, ajustando subdirectorios reales.
> 2. `tech/<stack>/skills/wf-<stack>-init/SKILL.md` — init especialista con modos detect/configure, manejo de estado previo, generación de `<stack>_project_state.md` y registro del run en el log append-only `.sdd/stack-runs.jsonl`. Modelo de referencia: `tech/kmm/skills/wf-kmm-init/SKILL.md`.
> 3. `tech/<stack>/CLAUDE.md` — orquestador del overlay con rootmap mínimo.
> 4. `tech/<stack>/skills/plan/` y `skills/tasks/` — vacíos con `README.md` indicando qué tipo de KBs alojan, salvo que el brief aporte dominios concretos.
> 5. Solo con `--with-agents`: variantes de `plan-architect.md`, `plan-auditor.md` y `task-generator.md` en `tech/<stack>/agents/` que conserven el contrato externo de las genéricas (gaps, estados, formato) y especialicen arquitectura y owners.
>
> Brief del stack: [type, detección, arquitectura, comandos, librerías del Paso 3].

---

## Paso 5: Integración post-generación

Tras el OK de `sdd-author`:

1. **Detección**: añade la condición `--detect` a la tabla del Paso 4 de `bootstrap/skills/wf-project-init/SKILL.md` (fila nueva: condición → stack).
2. **Registry**: ejecuta `python3 sdd/scripts/generate-skill-registry.py` para regenerar `sdd/meta/skill-registry.md`.
3. **Verificación**: instala el overlay en un directorio temporal sobre un install base de `plan,tasks` y comprueba que el override por nombre y la estructura son correctos.

---

## Paso 5.5: Gate estructural obligatorio (cierre)

Este paso es **determinista y obligatorio**: el overlay no se da por creado con defectos estructurales mecanizables en sus skills y agentes. La SSoT de qué se valida es el script `sdd/scripts/sdd-structural-lint.py` (no se re-describen los checks aquí; el script es la autoridad). Un overlay genera varias piezas a la vez (init especialista, CLAUDE.md, variantes de agentes y KBs), cualquiera de las cuales puede introducir un `NAME-MISMATCH`, una cita rota o un `REFERENCE-PATH-MISSING`.

Ejecuta el linter sobre el árbol fuente:
```bash
python3 sdd/scripts/sdd-structural-lint.py --check
```

Interpreta el exit code:

- **Exit 2 (hay BLOCKING)**: NO declares el overlay creado con éxito. El baseline del repo es `blocking=0`, así que cualquier blocking nuevo es atribuible a las piezas recién generadas. Ejecuta `python3 sdd/scripts/sdd-structural-lint.py --severity blocking` para ver el detalle, reporta los findings al usuario y exige corregirlos antes de cerrar.
  - Si — y solo si — algún blocking es sobre **piezas ajenas preexistentes** (no las del overlay recién creado), dílo explícitamente, sepáralo de lo atribuible al overlay, y deja que el usuario decida.
- **Exit 1 (solo WARNING)**: NO bloquea el cierre. Reporta un resumen de **una línea** con el conteo por tipo.
- **Exit 0 (limpio)**: cierra sin observaciones de lint.

Si python3 o el script no están disponibles, avisa con `⚠ gate estructural no ejecutado` y no bloquees por ello.

---

## Paso 6: Informe final

- Estructura creada bajo `tech/<stack>/`
- Piezas obligatorias y opcionales generadas (y cuáles quedaron pendientes de contenido experto)
- Checklist de conformidad del contrato con su estado
- Siguiente paso: poblar las KBs de dominio con `/wf-skill-create kb <nombre> --phase tech/<stack>` y probar `/wf-project-init` en un proyecto real del stack
