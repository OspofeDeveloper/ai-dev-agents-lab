---
name: kb-sdd-skill-architecture
description: "Reglas transversales para decidir cuando crear una kb, workflow o agente dentro de sdd, y como repartir responsabilidades entre CLAUDE.md, README y skills sin romper SSoT ni SRP. Incluye la arquitectura de tech targets (kmm, android, flutter) y su relacion con las fases del pipeline."
argument-hint: "[pregunta o tarea sobre diseño de skills/agentes]"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KB SDD Skill Architecture

Usa esta knowledge base como SSoT cuando haya que crear, dividir, refactorizar o auditar skills y agentes en cualquier fase del pipeline SDD (`prd`, `spec`, `design`, `plan`, `tasks`) o en un tech target (`tech/<stack>`).

## Regla 1: Capas fijas del ecosistema SDD

Cada fase de `sdd/` se organiza en estas capas:

- `CLAUDE.md`: orquestador local. Hace routing por intención, selecciona workflow o agente y describe handoffs.
- `wf-*`: pipeline cerrada y reusable. Parsea argumentos, verifica precondiciones, delega y escribe artefactos.
- agente: worker especializado por tipo de razonamiento o dominio. Ejecuta el trabajo intelectual.
- `kb-*`: conocimiento reusable y transversal. Define reglas, criterios y convenciones; no ejecuta pasos.
- `README.md`: mapa humano de la fase. Explica casos de uso, artefactos y entrypoints, pero no define la política global de skills.

Si una regla no encaja claramente en una sola capa, está mal ubicada o mezcla responsabilidades.

## Regla 2: Cuándo crear una `kb-*`

Crea una `kb-*` solo cuando exista conocimiento reusable que deba mantenerse estable y compartido.

Señales correctas:

- la misma regla la necesitan varios workflows o varios agentes
- el contenido es normativo o conceptual, no procedural
- la decisión debe sobrevivir a cambios de workflow o de fase
- una fase puede consumirla aunque la SSoT viva físicamente en otra fase

No crear una `kb-*` si el contenido es solo una secuencia de pasos, un caso de uso aislado o una decisión que pertenece a un único workflow.

## Regla 3: Cuándo crear una `wf-*`

Crea una `wf-*` cuando exista una pipeline cerrada con input, output y guardrails claros.

Una `wf-*` encaja si:

- parsea argumentos o flags
- valida precondiciones y bloqueos
- siempre sigue una secuencia reconocible
- delega el trabajo al agente adecuado
- produce artefactos o mutaciones de estado concretas

Una `wf-*` no debe convertirse en knowledge base ni en agente encubierto. Orquesta; no piensa por varias capas a la vez.

## Regla 4: Cuándo crear un agente

Crea un agente cuando el problema requiera juicio experto continuo dentro de un dominio o modo cognitivo.

Patrones válidos:

- exploración y diagnóstico
- planificación del approach
- escritura o evolución de artefactos
- auditoría y validación
- traducción entre artefactos de distinta naturaleza

No crear un agente si basta con una `kb-*` conceptual o con una `wf-*` determinista.

## Regla 5: Dónde vive cada tipo de verdad

- Reglas de dominio, convenciones y criterios: `kb-*`
- Secuencia operacional y guardrails de ejecución: `wf-*`
- Routing, intención del usuario y handoffs entre piezas: `CLAUDE.md`
- Mapa de fase, artefactos y ejemplos de uso: `README.md`
- Juicio especializado y producción real: agente

Si un README empieza a prescribir frontmatters, política de skills o reglas transversales de arquitectura, está invadiendo una SSoT que no le toca.

## Regla 6: Single Source of Truth real

Cada regla importante debe vivir en un solo sitio.

Aplicación práctica:

- una `wf-*` referencia la regla de una `kb-*`; no la reescribe inline
- un `README.md` enlaza la política global; no la vuelve a formular
- un `CLAUDE.md` de fase decide a quién delega; no duplica el contenido interno de las skills
- si una regla cambia, se actualiza la skill SSoT y el resto delega

→ Templates: `${CLAUDE_SKILL_DIR}/references/skill-architecture-patterns.md`

## Regla 7: Single Responsibility para skills y agentes

Una pieza está bien cortada cuando su responsabilidad puede describirse con una sola función principal.

Señales de mala partición:

- una `kb-*` mezcla varias dimensiones de verdad
- una `wf-*` mezcla varios pipelines no equivalentes
- un agente hace a la vez exploración, escritura y auditoría sin una razón fuerte
- una skill combina política estable con detalles accidentales de implementación

Si una pieza necesita explicarse con varias frases coordinadas por "y", probablemente está ancha de más.

## Regla 8: Separación por dimensión de decisión

Organiza las skills por la verdad que poseen, no por una mezcla accidental de contexto.

Ejemplos:

- una skill de gobernanza de cambios no debe absorber reglas de redacción de PRD
- una skill de trazabilidad no debe redefinir criterios de conflicto
- una skill de diseño visual no debe redefinir la política documental general de `sdd`

Cuando dos skills tocan un mismo proceso, una debe ser la SSoT y la otra debe referenciarla explícitamente.

## Regla 9: Cross-fase permitido, pero con SSoT única

Una `kb-*` puede vivir en una fase y ser consumida por agentes de otra si esa es su ubicación natural de SSoT.

Reglas:

- la ubicación física la decide la fuente de verdad, no el consumidor
- el consumo cross-fase debe documentarse en el mapa de la fase consumidora
- no se duplican skills hermanas para evitar dependencias incómodas

## Regla 10: Política de frontmatter para `kb-*`

Para el ecosistema SDD actual:

- `allowed-tools: [Read]` o equivalente vacío si la skill es puramente textual
- `user-invocable: false` cuando la skill es conocimiento de fondo para agentes
- sin `context: fork` en `kb-*`
- sin `disable-model-invocation: true` cuando la skill deba poder precargarse en subagentes

Esta política se deriva del comportamiento esperado por la documentación oficial de Claude Skills y del uso real de las `kb-*` de `prd/spec/design`.

## Regla 11: Política de frontmatter para `wf-*`

Para el ecosistema SDD actual:

- `allowed-tools` debe cubrir lo que el workflow realmente hace
- `context: fork` cuando la workflow se ejecuta como tarea separada
- `agent:` cuando el workflow está diseñado para delegar siempre en un agente concreto
- no usar `disable-model-invocation: true` si se espera routing desde lenguaje natural vía `CLAUDE.md`
- `description:` solo para qué hace el workflow (funcional, conciso); `when_to_use:` para frases de activación y exclusiones explícitas — nunca mezclar ambas cosas en `description`

Una `wf-*` puede ser manual-only, pero eso debe ser una excepción explícita, no la política por defecto.

## Regla 12: Reglas documentales de fase

Los documentos de fase deben quedarse dentro de su responsabilidad:

- `CLAUDE.md`: routing, handoffs, entrypoints, bloqueos
- `README.md`: mapa humano, casos de uso, artefactos, estructura de directorios
- `DIAGRAMS.md`: vistas explicativas correctas, sin simplificaciones que cambien responsabilidades reales

Si la política de creación de skills o agentes aparece repetida en varios READMEs de fase, hay deriva documental.

## Regla 13: Cuándo dividir una pieza existente

Divide una pieza si empieza a mezclar:

- varias dimensiones de verdad
- política estable y ejecución operativa
- contrato y detalle accidental
- conocimiento reusable y un pipeline específico
- supera los criterios de densidad de `kb-sdd-creation-guide` (≥ 300 líneas para `kb-*` normativas, ≥ 150 para `wf-*`)

Orden recomendado:

1. extraer la nueva SSoT más estable
2. adelgazar la pieza antigua para que delegue
3. actualizar workflows, agentes y documentación que dependan de ella

## Regla 14: References no son una segunda SSoT

Los archivos de `references/` sirven para templates, patrones y ejemplos cargados bajo demanda.

No deben contener:

- la única copia de una regla normativa
- decisiones globales no mencionadas en `SKILL.md`
- una segunda definición de responsabilidades ya descritas en la skill

→ Templates: `${CLAUDE_SKILL_DIR}/references/skill-architecture-patterns.md`

## Regla 15: Criterio para cerrar una limpieza

Una familia de skills y agentes está saneada cuando:

- no hay contradicciones entre documentos hermanos
- cada regla importante tiene una única SSoT
- los READMEs no duplican política global
- las workflows componen y no redefinen
- los agentes tienen una responsabilidad clara
- las `kb-*` se consumen como conocimiento reusable, no como puntos de entrada ambiguos

## Regla 16: Tech targets — estructura de directorio y separación de fases

Un **tech target** (KMM, Android nativo, Flutter, etc.) no es una fase del pipeline SDD. Es un stack de implementación que aporta conocimiento especializado a las fases de `plan` y `tasks`.

→ Estructura canónica y ejemplo KMM: `${CLAUDE_SKILL_DIR}/references/skill-architecture-patterns.md` (sección Tech Target Directory Structure)
→ Contrato operativo del overlay (piezas obligatorias, override por nombre sobre las genéricas de plan/tasks, init especialista e integración con `wf-project-init` y los gates): `kb-sdd-stack-overlay-contract`. Para crear un overlay nuevo: `/wf-stack-create`.

### Contrato de carga por agente

Cuando `plan-architect` genera un plan técnico para el stack KMM, carga:

1. `sdd/plan/skills/kb-plan-expert` (genérico de fase)
2. `sdd/tech/kmm/skills/plan/kb-kmm-*` (específicos del stack)

El agente **no** mezcla KBs de `tasks/` al planificar, ni KBs de `plan/` al generar tasks.

### Criterio de ubicación para una `kb-*` de stack

- Si la KB describe arquitectura, capas, contratos o estructuras conceptuales del stack → `tech/<stack>/skills/plan/`
- Si la KB describe implementaciones concretas, plantillas de código o configuraciones de plataforma → `tech/<stack>/skills/tasks/`
- Si la KB es transversal a plan y tasks (vocabulario o convenciones del stack) → `tech/<stack>/skills/` (raíz, sin subdirectorio de fase)

### KB dual: mismo dominio, contenido diferente por fase

Un dominio puede requerir una KB en `plan/` **y** otra en `tasks/` con el mismo nombre pero contenido distinto. El directorio es el discriminador; no hay conflicto de SSoT.

| Fase | Nivel de contenido | Ejemplo: `kb-cmp-resources` |
|---|---|---|
| `plan/` | Qué implica, qué estructura genera, qué decisiones hay que tomar | Qué es compose-resources, estructura de carpetas, qué módulos se ven afectados, qué tareas debe contemplar el plan |
| `tasks/` | Cómo se implementa exactamente | `build.gradle.kts` exacto, snippets `Res.*`, configuración de localización |

Señal de que una KB necesita split dual: contiene secciones de "qué/por qué" mezcladas con secciones de "cómo/código". Extraer el nivel conceptual a `plan/` y el nivel de implementación a `tasks/`.

### Añadir un nuevo tech target

1. Crear `sdd/tech/<nuevo_stack>/skills/plan/` y `/tasks/`
2. Registrar el stack y sus agentes en el `CLAUDE.md` del orquestador raíz
3. No tocar la estructura de ninguna fase existente

### Anti-patrones

- Un directorio `<stack>/` al mismo nivel que las fases (`prd/`, `spec/`, etc.) rompe la separación fases/targets.
- KBs de `tasks` cargadas en el agente de `plan` (y viceversa) introducen conocimiento accidental fuera de contexto.
- Un stack sin `agents/` solo puede ser invocado por agentes de fase — documentar explícitamente si ese es el diseño.

## Regla 17: Umbral de delegación — inline vs agente vs pipeline

No toda operación merece un subagente. Clasificar cada paso según su coste real:

**Hacer inline (sin delegar):**
- parseo de argumentos y flags
- verificación de precondiciones (archivo existe, nombre válido, naming convention)
- colección mecánica de rutas o listas (find, grep estructural)
- escritura de un artefacto cuyo contenido ya fue generado por el agente

**Delegar a un agente:**
- generación de contenido complejo (frontmatter + body de skill o agente)
- diagnóstico de violaciones de SSoT/SRP que requiere juicio sobre el ecosistema
- exploración de contexto amplio con razonamiento cruzado entre archivos
- decisiones de partición arquitectónica o refactorización de múltiples piezas

**Usar pipeline completo (wf-* que delega a agente):**
- tarea ambigua entre dominios que requiere precondiciones + razonamiento experto
- operación con impacto en invariantes del ecosistema (afecta rootmaps, registros, referencias cruzadas)
- flujo con guardrails y output concreto definido

Anti-patrones:
- hacer una ceremonia de subagente para un parseo de argumentos (overhead sin beneficio)
- intentar generar contenido complejo inline (contamina contexto, mezcla roles)

Ejemplo canónico en el ecosistema: `wf-sdd-status` no delega a ningún agente porque es colección mecánica de inventario — caso 1 puro.

## Regla 18: Skill Registry — índice persistente del ecosistema

`sdd/meta/skill-registry.md` es el índice central de todas las skills del ecosistema.

- Lo genera y actualiza `wf-sdd-status` automáticamente en cada run global.
- Lo leen agentes que necesitan descubrir skills sin explorar el filesystem: `sdd-author` (detección de duplicados), `sdd-auditor` (cobertura estructural).
- No es una segunda SSoT: cada regla sigue viviendo en su `SKILL.md`. El registry solo almacena nombre, descripción de una línea, invocabilidad y path.
- No se edita manualmente. Si está desactualizado: ejecutar `wf-sdd-status`.

## Regla 19: KB Load Status — protocolo de verificación de contexto

Las KBs se inyectan en el contexto del agente vía el campo `skills: [...]` del frontmatter por el harness de Claude Code. El agente no las carga explícitamente: simplemente las recibe o no las recibe. Si una KB falla silenciosamente, el agente opera sin sus reglas normativas sin saberlo.

Todo agente que declare `skills: [...]` en frontmatter debe:

1. Al inicio de cada sesión, verificar si el contenido de cada KB declarada es accesible (puede referenciar sus secciones o conceptos clave).
2. Incluir al final de cada respuesta un bloque `## KB Load Status` con el estado de cada KB: `loaded` si el contenido es accesible, `missing` si no lo está.
3. Si alguna KB aparece como `missing`, advertirlo antes de proceder y pedir al usuario que inyecte el contenido.

Formato normalizado del bloque:

```
## KB Load Status
- kb-nombre-1: loaded
- kb-nombre-2: missing ⚠️

> ⚠️ `kb-nombre-2` no está disponible en contexto. El output puede ser incompleto.
> Inyecta su contenido antes de continuar.
```

Este protocolo no aplica a agentes sin `skills: [...]` declaradas.
