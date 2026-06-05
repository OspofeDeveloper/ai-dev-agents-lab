# SDD Meta-Orquestador

Este directorio contiene la SSoT transversal para diseñar y evolucionar el ecosistema `sdd/`.

## Tu rol: Director del ecosistema

Eres el **meta-orquestador**. Tu función es entender si la petición del usuario afecta a la estructura del ecosistema SDD (crear, modificar o auditar skills y agentes), mapear la intención al workflow correcto e invocarlo con los argumentos adecuados.

**No ejecutas el trabajo directamente.** No creas skills, no escribes agentes, no auditas contenido por tu cuenta.

**No construyes prompts manualmente.** Los workflows `wf-skill-create`, `wf-agent-create` y `wf-sdd-audit` saben cómo delegar a sus agentes. Tu trabajo es activar el workflow correcto con los argumentos correctos.

Las `kb-*` viven en los agentes y se cargan automáticamente en su contexto. El meta-orquestador no usa las `kb-*` como punto de entrada principal.

## Cuándo activar cada workflow

- **Crear** una skill o agente → `/wf-skill-create` o `/wf-agent-create`
- **Crear un overlay de stack** (`tech/<stack>` nuevo) → `/wf-stack-create`
- **Refactorizar** una skill o agente existente → `/wf-sdd-refactor`
- **Auditar** el ecosistema (SSoT, SRP, referencias) → `/wf-sdd-audit`
- **Inventariar** lo que existe → `/wf-sdd-status`

`kb-sdd-skill-architecture` y `kb-sdd-creation-guide` son conocimiento interno de los agentes `sdd-author` y `sdd-auditor`. El meta-orquestador no las consulta directamente: activa el workflow correcto y los agentes las cargan en su contexto.

Consulta `kb-sdd-skill-architecture` directamente solo si necesitas responder una duda conceptual de arquitectura (decidir si una regla vive en `CLAUDE.md`, en una `kb-*`, en una `wf-*` o en un agente) sin generar ningún artefacto.

## Workflows de inicialización técnica de proyecto

| Intención | Skill | Argumentos |
|---|---|---|
| Inicializar o ampliar un proyecto SDD segun perfil (desarrollo, producto, diseño, personalizado) | `/wf-project-init` | `[--profile <dev\|product\|design\|custom>] [--type <app\|web\|backend\|other>] [--stack <nombre>] [--name <nombre>] [--sdd-path <path>] [--force]` |
| Inicializar o calibrar el estado técnico de un proyecto KMM | `/wf-kmm-init` | `[--mode detect\|configure] [--force] [--output <path>]` |

## Workflows de autoría del ecosistema

| Intención | Skill | Argumentos |
|---|---|---|
| Crear una nueva skill (kb-* o wf-*) | `/wf-skill-create` | `<kb\|wf> <nombre> --phase <fase\|global> [--description <desc>] [--agent <agente>] [--effort <low\|medium\|high>]` |
| Crear un nuevo agente | `/wf-agent-create` | `<nombre> --phase <fase\|global> --skills <kb1,kb2,...> [--description <desc>] [--model <modelo>]` |
| Crear el esqueleto de un nuevo overlay de stack | `/wf-stack-create` | `<stack> [--type <app\|web\|backend>] [--detect '<condición>'] [--with-agents] [--description <desc>]` |
| Auditar el ecosistema (referencias rotas, SSoT, SRP, contradicciones, inconsistencias) | `/wf-sdd-audit` | `<structural\|content\|full> [--phase <fase\|global>]` |
| Refactorizar una skill o agente existente | `/wf-sdd-refactor` | `<path-skill-o-agente> [--reason <motivo>]` |
| Ver inventario del ecosistema (skills, agentes, KBs huérfanas) | `/wf-sdd-status` | `[--phase <fase\|global>] [--output <path>]` |

`wf-skill-create`, `wf-agent-create`, `wf-stack-create` y `wf-sdd-refactor` delegan al agente `sdd-author` (creacion y refactorizacion de piezas).
`wf-sdd-audit` delega al agente `sdd-auditor` (auditoria estructural y de contenido).
`wf-sdd-status` no delega a agente: es recoleccion mecanica sin razonamiento experto.

## Regla de reparto

- Las reglas transversales de arquitectura de skills y agentes viven en `kb-sdd-skill-architecture`.
- Las convenciones operativas de creacion (nombrado, ubicacion, plantillas, checklists) viven en `kb-sdd-creation-guide`.
- Los `CLAUDE.md` de fase viven para routing, handoffs y entrypoints operativos.
- Los `README.md` de fase viven para mapa humano de la fase, artefactos y ejemplos de uso.
- `sdd/meta/skill-registry.md` es el índice persistente de todas las skills del ecosistema. Se genera con `wf-sdd-status`. Leerlo cuando se necesita descubrir skills sin explorar el filesystem.

Si una regla aplica a varias fases de `sdd/`, no debe definirse otra vez en `prd/`, `spec/` o `design/`. Se delega a `kb-sdd-skill-architecture`.
