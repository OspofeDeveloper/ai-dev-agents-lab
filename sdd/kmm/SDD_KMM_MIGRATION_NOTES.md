# SDD × KMM Migration Notes

Última actualización: 2026-04-16

Este documento existe para poder retomar la migración del ecosistema SDD + KMM sin perder contexto entre sesiones.

---

## Estado actual

La migración ya ha cambiado el puente `tasks -> implementation` del modelo antiguo basado en skills por capa al nuevo modelo basado en agentes KMM por capacidad.

### Ya hecho

- `kmm/` ya no usa un único `kmm-implementer`.
- Se han creado estos agentes KMM:
  - `kmm-feature-implementer`
  - `kmm-platform-integrator`
  - `kmm-network-auth-implementer`
- `kmm/install.sh` instala esos tres agentes.
- `kmm/CLAUDE.md` ya documenta el modelo nuevo:
  - orquestador puro
  - agentes KMM como unidad primaria de implementación
  - workflows como pipelines cerradas cuando aplica
- Las workflows KMM ya apuntan al agente correcto:
  - `wf-kmm-environments` -> `kmm-platform-integrator`
  - `wf-kmm-network-setup` -> `kmm-network-auth-implementer`
  - `wf-kmm-auth-setup-keycloak` -> `kmm-network-auth-implementer`
  - `wf-kmm-stack-setup-ktor-keycloak-koin` -> `kmm-network-auth-implementer`
- `kmm/agents/kmm-implementer.md` se eliminó.
- `sdd/tasks/skills/kb-tasks-expert` ya fue migrada:
  - las tasks ya no se definen por `/kmm-domain`, `/kmm-data`, etc.
  - ahora usan `Execution domain` y `Owner agent`
- `sdd/tasks/skills/kb-tasks-expert/references/kmm_task_templates.md` ya usa el modelo nuevo.
- `sdd/tasks/skills/kb-tasks-expert/references/task_sizing.md` ya usa el modelo nuevo.
- `sdd/tasks/agents/task-generator.md` ya genera tasks pensadas para owner agents.
- `sdd/tasks/skills/wf-prepare-tasks/SKILL.md` ya comunica el resultado en términos de delegación a agentes KMM.
- `sdd/README.md` ya explica el puente `tasks -> implementation` usando agentes KMM.
- `sdd/CLAUDE.md` ya deja claro que tras `wf-prepare-tasks` el orquestador delega cada task al `Owner agent`.
- `sdd/spec/extras/workflow_tests/09_prepare-tasks.md` ya fue actualizado al modelo nuevo.

### Verificación hecha

- No quedan referencias activas al modelo viejo (`/kmm-domain`, `/kmm-data`, `/kmm-presentation`, `/kmm-tests`, `kmm-implementer`) dentro del corpus principal de `sdd/` y `kmm/`.
- Lo cambiado está alineado entre:
  - `kmm/CLAUDE.md`
  - `sdd/CLAUDE.md`
  - `sdd/README.md`
  - `kb-tasks-expert`
  - `task-generator`

---

## Decisiones de diseño cerradas

Estas decisiones se consideran vigentes salvo revisión explícita.

### 1. El orquestador no implementa

El agente principal:

- entiende el objetivo
- decide el siguiente paso del pipeline
- elige workflow o agente
- delega
- integra resultados

No implementa directamente.

### 2. SDD se organiza por etapa

En `sdd/` sí tiene sentido mantener agentes por etapa:

- `sdd-analyst`
- `plan-architect`
- `task-generator`

Razón:

- producen artefactos de proceso
- la especialización real ahí sí coincide con la etapa

### 3. KMM se organiza por capacidad, no por etapa ni por capa

En `kmm/` la unidad principal de implementación no es:

- una skill por capa
- ni un agente por etapa
- ni un agente por `data/domain/presentation`

La unidad principal es el agente por dominio de trabajo:

- `kmm-feature-implementer`
- `kmm-platform-integrator`
- `kmm-network-auth-implementer`

### 4. Las tasks SDD no apuntan a comandos; apuntan a responsables

El modelo correcto de task es:

- `Execution domain`
- `Owner agent`
- `Suggested workflow` opcional

No:

- `Skill: /kmm-domain`
- `Skill: /kmm-data`
- `Skill: /kmm-presentation`

### 5. Las workflows con `agent:` no son el mecanismo principal de todo el sistema

Se aceptan cuando:

- la pipeline es cerrada
- secuencial
- y compensa encapsularla

Pero el mecanismo principal de ejecución KMM es:

- el orquestador delega a un agente KMM especializado
- el agente usa sus `kb-*` y, si aplica, sus `wf-*` internas

### 6. No se usarán subagentes estables por `data/domain/presentation`

Eso se descartó porque:

- no coincide con la unidad real de cambio
- fragmenta demasiado la implementación
- obliga a handoffs artificiales

La separación correcta es por capacidad de implementación, no por subcarpeta arquitectónica.

### 7. Los `AGENTS.md` locales son contexto auxiliar, no el mecanismo principal

La arquitectura base elegida es:

- skills como SSoT
- orquestador puro
- subagentes especializados
- `AGENTS.md` global y locales mínimos solo donde aporten valor real

No se quiere un sistema basado principalmente en `AGENTS.md` por carpeta.

### 8. SDD usa dos ejes distintos

- eje de proceso: `spec -> plan -> tasks -> implementation -> testing`
- eje de capacidad: feature / platform / network-auth / quality

La estructura de agentes base debe responder al eje de capacidad, no al eje de proceso.

---

## Backlog pendiente

Ordenado por prioridad.

### Prioridad 1 — cerrar la integración implementation/testing

#### 1. Diseñar la capa de ejecución de tasks reales

Falta decidir y documentar cómo se ejecuta una task una vez existe el `_tasks.md`.

Hay que definir:

- si habrá workflows KMM de implementación generales o no
- cómo el orquestador lee una task y lanza al `Owner agent`
- si habrá una workflow SDD adicional para “ejecutar task(s)” o si eso vivirá en otra capa

Archivos a tocar:

- probablemente nuevo material en `sdd/` para la fase implementation/testing
- posiblemente `sdd/CLAUDE.md`
- probablemente nuevo README o sección adicional en `sdd/README.md`

#### 2. Decidir si crear `kmm-quality-validator`

Está considerado, pero todavía no se ha creado.

Preguntas abiertas:

- ¿testing/validación se tratará como capacidad propia?
- ¿será agente estable o solo worker puntual?
- ¿validará contra spec, plan, tasks y tests implementados?

Si se aprueba:

- crear `kmm/agents/kmm-quality-validator.md`
- definir skills cargadas
- reflejarlo en `kmm/CLAUDE.md`
- reflejarlo en `sdd/README.md`

### Prioridad 2 — completar el modelo de tasks con testing/validation real

#### 3. Refinar `kb-tasks-expert` para tareas de testing más allá de unit tests

Ahora el modelo ya soporta tests básicos de feature, pero aún no está resuelta toda la estrategia de testing del ecosistema.

Pendiente:

- decidir si habrá tasks específicas para validación contra spec
- decidir si habrá tasks de integration/UI test distintas de unit test
- decidir si testing puede pertenecer a `platform` o a `quality`

Archivos a revisar:

- `sdd/tasks/skills/kb-tasks-expert/SKILL.md`
- `sdd/tasks/skills/kb-tasks-expert/references/task_sizing.md`
- `sdd/tasks/skills/kb-tasks-expert/references/kmm_task_templates.md`

#### 4. Revisar `task-generator` con planes reales

La semántica ha cambiado, pero falta validarla con ejemplos reales.

Pendiente:

- generar uno o varios `_tasks.md` reales
- comprobar si la heurística de owner agent funciona
- ajustar las reglas cuando una tarea caiga entre `feature` y `network-auth`
- decidir si el `Suggested workflow` se está usando demasiado o demasiado poco

### Prioridad 3 — alinear documentación secundaria y ejemplos

#### 5. Revisar otros ejemplos y fixtures en `sdd/spec/extras`

Se actualizó `09_prepare-tasks.md`, pero conviene revisar el resto del material de ejemplo por si aún presupone el modelo viejo.

Pendiente:

- buscar documentación residual sobre `/kmm-domain`, `/kmm-data`, etc. fuera del corpus principal
- actualizarla o marcarla como legacy

#### 6. Añadir un documento específico de “Execution model”

Ahora el diseño ya está en varios sitios, pero sería útil una pieza dedicada que explique:

- cómo se conecta `sdd/` con `kmm/`
- cómo se leen las tasks
- cómo decide el orquestador el `Owner agent`
- cuándo usar workflow vs agente directo

Ubicación sugerida:

- `sdd/README.md` ampliado
- o nuevo archivo como `sdd/EXECUTION_MODEL.md`

### Prioridad 4 — instalación y ergonomía del ecosistema

#### 7. Revisar instalación global del repo

Pendiente:

- comprobar si hay `install.sh` o flujo equivalente para `sdd/`
- revisar si hay que instalar también agentes KMM desde el paraguas SDD
- validar que la experiencia de instalación cuenta el modelo nuevo

#### 8. Revisar `kmm/install.sh` desde la perspectiva del ecosistema total

Ahora instala bien los tres agentes KMM, pero puede que más adelante haya que integrarlo con el flujo SDD o con un bootstrap de repo completo.

---

## Riesgos o decisiones aún no cerradas

### A. ¿Implementation será una nueva etapa formal en `sdd/`?

Todavía no está decidido si:

- se extiende `sdd/` con una etapa explícita de implementation
- o si `sdd/` termina en `_tasks.md` y la ejecución vive en el ecosistema KMM

Mi lectura actual:

- `sdd/` ya debería al menos documentar claramente ese handoff
- no es obligatorio meter toda la implementación dentro de `sdd/`

### B. ¿Testing será parte de implementation o una capacidad separada?

Todavía no cerrado.

Opciones:

- testing como parte natural de `kmm-feature-implementer`
- testing avanzado/validación como `kmm-quality-validator`

### C. ¿Habrá workflows KMM de implementación reales además de las de setup?

Ahora KMM tiene sobre todo workflows de setup/configuración.

Queda por decidir si crear workflows como:

- crear/implementar feature task
- integrar navegación de feature
- ejecutar una task concreta desde `_tasks.md`

o si eso quedará más libre y centrado en agentes.

---

## Siguiente paso recomendado

Si se retoma la migración, el siguiente paso más útil es:

1. diseñar explícitamente la fase `implementation/testing` bajo el paraguas SDD
2. decidir si existe `kmm-quality-validator`
3. definir cómo el orquestador consume un `_tasks.md` y delega cada task al `Owner agent`

En términos de trabajo sobre archivos, lo siguiente que más sentido tiene tocar es:

- `sdd/README.md`
- `sdd/CLAUDE.md`
- posible nuevo documento `sdd/EXECUTION_MODEL.md`
- posibles nuevos agentes o workflows de implementación/testing

---

## Archivos clave ya migrados

### KMM

- `kmm/CLAUDE.md`
- `kmm/install.sh`
- `kmm/agents/kmm-feature-implementer.md`
- `kmm/agents/kmm-platform-integrator.md`
- `kmm/agents/kmm-network-auth-implementer.md`
- `kmm/skills/wf-kmm-environments/SKILL.md`
- `kmm/skills/wf-kmm-network-setup/SKILL.md`
- `kmm/skills/wf-kmm-auth-setup-keycloak/SKILL.md`
- `kmm/skills/wf-kmm-stack-setup-ktor-keycloak-koin/SKILL.md`

### SDD

- `sdd/CLAUDE.md`
- `sdd/README.md`
- `sdd/tasks/skills/kb-tasks-expert/SKILL.md`
- `sdd/tasks/skills/kb-tasks-expert/references/kmm_task_templates.md`
- `sdd/tasks/skills/kb-tasks-expert/references/task_sizing.md`
- `sdd/tasks/agents/task-generator.md`
- `sdd/tasks/skills/wf-prepare-tasks/SKILL.md`
- `sdd/spec/extras/workflow_tests/09_prepare-tasks.md`

---

## Criterio para próximas sesiones

Antes de seguir, mantener estas reglas:

- no reintroducir skills por capa como unidad principal de implementación
- no volver al modelo de `kmm-implementer`
- no mezclar el eje de proceso SDD con el eje de capacidad KMM
- mantener `kb-*` como SSoT
- documentar cualquier decisión nueva de migración en este mismo archivo o en un documento de ejecución equivalente
