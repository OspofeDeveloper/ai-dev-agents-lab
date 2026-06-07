---
name: kb-sdd-stack-overlay-contract
description: "Contrato normativo que debe cumplir un overlay de stack (tech/<stack>) para integrarse en el ecosistema SDD: piezas obligatorias y opcionales, mecanismo de override por nombre sobre las piezas genericas de plan/tasks, init especialista con project state, registro en project-init.json y puntos de integracion con wf-project-init y los gates de plan/tasks. No cubre la estructura de directorios de tech targets (ver kb-sdd-skill-architecture, Regla 16) ni las convenciones de creacion de piezas (ver kb-sdd-creation-guide)."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KB SDD Stack Overlay Contract

Un **overlay de stack** es el paquete `tech/<stack>/` que especializa las fases `plan` y `tasks` (y opcionalmente la implementación) para una tecnología concreta. Las fases `prd`, `spec` y `design` son neutrales: un overlay nunca las modifica.

Principio rector: **el modo genérico es el caso base; el overlay especializa, nunca habilita.** Un proyecto sin overlay debe poder recorrer el pipeline completo (specs → plan → tasks → implementación por el orquestador). El overlay sustituye piezas genéricas por variantes expertas, no añade capacidades que el pipeline genérico no tenga.

---

## Piezas obligatorias

| Pieza | Path | Responsabilidad |
|---|---|---|
| Installer del overlay | `tech/<stack>/install.sh` | Copia agentes y skills del overlay al `.claude` del proyecto destino. Se ejecuta SIEMPRE después del install base de fases |
| Init especialista | `tech/<stack>/skills/wf-<stack>-init/` | Genera `<stack>_project_state.md` con el estado técnico real del proyecto. Modos `detect` (exploración de proyecto existente) y `configure` (preguntas para proyecto nuevo). Registra su ejecución en `stack_workflows_run` de `.sdd/project-init.json` |
| Project state | `<stack>_project_state.md` (raíz del proyecto destino) | SSoT del estado técnico: targets, arquitectura, librerías, comandos de build/test. Lo leen todos los agentes del stack antes de operar |
| CLAUDE.md del overlay | `tech/<stack>/CLAUDE.md` | Orquestador del stack: rootmap de sus `wf-*`, tabla de sus agentes y principios de delegación |

## Piezas opcionales

| Pieza | Cuándo aportarla |
|---|---|
| Variantes por override de `plan-architect`, `plan-auditor`, `task-generator` (`tech/<stack>/agents/`, mismo nombre de archivo) | Cuando el stack tiene arquitectura prescriptiva propia (capas, módulos, convenciones) que el plan/tasks debe imponer |
| Variantes por override de `kb-plan-expert` (`skills/plan/`) y `kb-tasks-expert` (`skills/tasks/`) | Acompañan a las variantes de agentes: mismo contrato metodológico, contenido especializado |
| KBs de stack para plan (`skills/plan/kb-*`) y tasks (`skills/tasks/kb-*`) | Conocimiento por dominio (DI, networking, navegación, testing...). Separación estricta: KBs de plan planifican, KBs de tasks implementan |
| Agentes de implementación propios (`agents/<stack>-*.md`) | Cuando las tasks se delegan a workers especializados en vez del orquestador |
| Workflows de setup (`skills/wf-<stack>-*`) | Pipelines cerradas de configuración (auth, networking, environments...) |
| Protocolo de project state (`skills/kb-<stack>-project-state-protocol`) | Cuando hay agentes propios que deben leer el project state como precondición |

---

## Mecanismo de override por nombre

1. `install.sh` (base) instala las piezas genéricas de fase en `<fase>/.claude/` del proyecto.
2. `tech/<stack>/install.sh` se ejecuta **después** y copia por basename (`rm -rf` + copia): toda pieza del overlay con el mismo nombre que una genérica la **sustituye**.

Reglas para una variante válida:

- **Conserva el contrato externo**: misma metodología, misma taxonomía de gaps (`DESIGN_GAP`/`TECH_GAP`/`TRACE_GAP`/`PLAN_GAP`), mismos estados (`BORRADOR`/`VALIDADO`), mismo formato de artefacto de salida y misma regla canónica de Design. Solo especializa el **cómo** (capas, librerías, owners, templates).
- Los workflows de fase (`wf-prepare-plan`, `wf-prepare-tasks`, `wf-plan-validate`) **nunca** se sobreescriben: son neutrales y resuelven el stack por los gates.
- Los owners de tasks en la variante son los agentes del stack; en la genérica, `orquestador`.

---

## Puntos de integración con el ecosistema

| Punto | Qué debe ocurrir |
|---|---|
| `wf-project-init` Paso 4 (detección silenciosa) | Añadir la condición de detección del stack a la tabla (archivos/patrones que lo delatan) |
| `wf-project-init` Paso 8 (despacho) | Si las fases incluyen `plan`/`tasks` y existe `wf-<stack>-init`, se invoca via Skill tool. El overlay queda registrado: `"stack": "<stack>"`, `"specialist_workflow": "wf-<stack>-init"` |
| Gates de `wf-prepare-plan` / `wf-prepare-tasks` | Con `specialist_workflow` no nulo exigen `<stack>_project_state.md`; el init especialista DEBE generarlo o el pipeline queda bloqueado |
| `sdd/meta/skill-registry.md` | Ejecutar `wf-sdd-status` tras crear o modificar el overlay |

---

## Invariantes

1. **No romper el modo genérico**: eliminar el overlay de un proyecto (o no instalarlo) deja un pipeline funcional.
2. **Idempotencia**: reinstalar el overlay produce el mismo resultado; `wf-<stack>-init` detecta estado previo y pregunta antes de rehacer.
3. **Project state como precondición, no como cache**: si el proyecto cambia de forma relevante, se regenera con `wf-<stack>-init --force`; los agentes no lo editan a mano.
4. **El overlay no toca `prd/`, `spec/` ni `design/`** del proyecto destino.
5. **Cierre verificable de los agentes implementadores**: todo agente del overlay que modifique código debe cerrar con verificación ejecutable — build de los módulos afectados y tests relevantes usando los comandos declarados en `<stack>_project_state.md`, reporte honesto del comando y su salida real (un fallo se reporta tal cual, nunca como éxito), y declaración explícita "verificación ejecutable: no disponible — <motivo>" cuando no se pueda ejecutar nada. Es la contraparte dentro del agente de lo que `wf-task-run` (Paso 6) y `wf-bug` (Paso 4) exigen desde fuera. La concreción del contrato vive en la KB de protocolo del stack (referencia canónica: `kb-kmm-project-state-protocol`, Regla 6) y los agentes la referencian con una sección corta de cierre, sin reescribirla inline.

---

## Checklist de conformidad

- [ ] `tech/<stack>/install.sh` ejecutable y con el mismo mecanismo de copia por basename
- [ ] `wf-<stack>-init` con modos detect/configure, manejo de estado previo y registro en `stack_workflows_run`
- [ ] `<stack>_project_state.md` generado con secciones mínimas: targets/runtime, arquitectura, dependencias clave, comandos build/test
- [ ] Agentes implementadores con contrato de cierre verificable (invariante 5): sección de cierre que referencia la regla del protocolo del stack
- [ ] Variantes de override (si las hay) conservan el contrato externo de la pieza genérica
- [ ] Condición de detección añadida a `wf-project-init` Paso 4
- [ ] Registrado en `skill-registry.md` via `wf-sdd-status`
