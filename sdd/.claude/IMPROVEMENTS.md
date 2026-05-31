# Análisis: gentle-ai vs SDD Lab — Puntos de mejora adoptables

Referencia: https://github.com/Gentleman-Programming/gentle-ai (3.5k stars, 417 forks)

## Qué es gentle-ai

Ecosistema configurador de agentes de IA (14 plataformas: Claude Code, Cursor, Gemini CLI, etc.) que añade memoria persistente, skill registry, SDD workflows y herramientas MCP a cualquier agente. No es un pipeline SDD completo — es la capa de infraestructura que rodea al agente.

---

## Mejoras adoptables (ordenadas por impacto)

### 1. Skill Registry — descubrimiento indexado de skills ✅ IMPLEMENTADO

**¿Qué tiene gentle-ai?**
Un archivo `.atl/skill-registry.md` generado automáticamente con cuatro campos por skill: nombre, trigger/descripción completa, scope (proyecto/usuario) y path exacto al `SKILL.md`. Los agentes consultan el registry para encontrar skills sin necesidad de conocer la estructura del filesystem.

**¿Qué tenemos nosotros?**
Rootmaps en los `CLAUDE.md` de cada fase — tablas estáticas de intención → workflow. No hay un índice central consultable.

**Propuesta implementada:**
`sdd/.claude/skill-registry.md` generado por `wf-sdd-status`. Regla 18 en `kb-sdd-skill-architecture`.

---

### 2. Token budget en la skill style guide

**¿Qué tiene gentle-ai?**
`docs/skill-style-guide.md` define rangos explícitos: objetivo 180–450 tokens, recomendado máximo 700, hard cap 1000.

**¿Qué tenemos nosotros?**
`kb-sdd-creation-guide` define estructura pero no criterio de densidad. Algunas kb-* superan 300 líneas.

**Propuesta:**
Añadir a `kb-sdd-creation-guide` criterios de densidad:
- `kb-*` normativas: objetivo ≤ 300 líneas; si supera → revisar SRP
- `wf-*`: objetivo ≤ 150 líneas; si supera → mover pasos a `references/`
- `kb-*` de stack (tasks/): pueden ser más largas (templates de código)

---

### 3. SDD Init Harness → `wf-kmm-init`

**¿Qué tiene gentle-ai?**
Comando `/sdd-init` que calibra el proyecto antes de codear: detecta stack, frameworks, test commands, convenciones, produce un artefacto de estado que todos los agentes consumen.

**¿Qué tenemos nosotros?**
`kmm-explorer` hace exploración per-request. No hay paso zero persistente.

**Propuesta:**
`wf-kmm-init` que produce `kmm_project_state.md` con stack, módulos, test setup, convenciones, estado de features. Todos los agentes KMM leen este archivo al inicio si existe.

---

### 4. Work Unit Commits + Chained PRs

**¿Qué tiene gentle-ai?**
Skills `work-unit-commits` y `chained-pr`: reglas para commits como unidades revisables (máx 400 líneas), dividir PRs grandes en cadenas, mantener tests junto al código.

**¿Qué tenemos nosotros?**
Nada formal. Los agentes KMM implementadores no tienen criterio de tamaño de commit.

**Propuesta:**
Dos skills en `sdd/tech/kmm/skills/tasks/`:
- `kb-kmm-work-unit-commits`: criterio de tamaño, tests junto al código, convención de mensaje
- `kb-kmm-chained-pr`: cuándo dividir en PRs encadenadas, estrategia stacked vs. feature branch

---

### 5. Cognitive Doc Design — documentación de bajo coste cognitivo

**¿Qué tiene gentle-ai?**
Skill `cognitive-doc-design`: 6 patrones (lead with answer, divulgación progresiva, agrupación, señalización, tablas > prosa, empatía con revisores).

**¿Qué tenemos nosotros?**
`kb-sdd-creation-guide` dice cómo estructurar skills pero no tiene principios de calidad cognitiva del contenido.

**Propuesta:**
Sección "Principios de calidad cognitiva" en `kb-sdd-creation-guide`: respuesta primero, divulgación progresiva, tablas > prosa para decisiones, referencias > repetición inline.

---

## Lo que tienen y NO adoptaríamos

| Componente | Por qué no |
|---|---|
| **Engram** (memoria MCP automática) | Requiere servidor MCP externo; nuestro sistema `memory/` cubre el caso |
| **OpenCode SDD Profiles** | Solo aplica a OpenCode; usamos frontmatter de agentes |
| **Multi-platform support** | Somos Claude Code — complejidad sin beneficio |
| **Branch/PR naming skill** | Git workflow genérico, no SDD pipeline |

---

## Lo que tenemos y ellos no

- Pipeline completo PRD → Spec → Design → Plan → Tasks con fases, agentes y guardrails
- Arquitectura de tech targets (`tech/kmm/`) separada de las fases
- SSoT/SRP enforcement como reglas normativas explícitas
- Cross-phase KB sharing con contrato explícito
- Agentes especializados por modo cognitivo (explorador, planificador, escritor, auditor)

---

## Prioridad sugerida de adopción

| # | Mejora | Esfuerzo | Impacto | Estado |
|---|---|---|---|---|
| 1 | Skill Registry | Bajo | Medio | ✅ Implementado |
| 2 | `wf-kmm-init` (SDD Init para KMM) | Medio | Alto | Pendiente |
| 3 | Token budget / densidad en kb-sdd-creation-guide | Bajo | Medio | Pendiente |
| 4 | Work Unit Commits + Chained PRs para KMM | Medio | Medio | Pendiente |
| 5 | Cognitive Doc Design en kb-sdd-creation-guide | Bajo | Bajo-Medio | Pendiente |
