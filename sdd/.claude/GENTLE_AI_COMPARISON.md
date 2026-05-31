# Comparativa Gentle-AI vs SDD Ecosistema

Análisis de `github.com/gentleman-programming/gentle-ai-main` — 2026-05-31.
Fuente: exploración directa del repositorio.

---

## Lo que tienen ellos y nosotros no

### 1. Model Assignment Table por fase

El orquestador asigna modelo diferente según la naturaleza del trabajo:

| Fase | Modelo | Razón |
|---|---|---|
| explore, spec, tasks, apply, verify | Sonnet | Lectura/escritura estructurada |
| propose, design | Opus | Decisiones arquitectónicas |
| archive | Haiku | Cierre mecánico |

**Gap:** Todos nuestros agentes usan el mismo modelo sin distinción de coste por tipo de trabajo.

---

### 2. Skill Resolution Feedback Loop

Los subagentes reportan al orquestador cómo cargaron sus skills:
- `paths-injected` — cargadas por path directo
- `fallback-registry` — cargadas desde el registry
- `fallback-path` — cargadas por path de fallback
- `none` — no se cargaron

Si el orquestador recibe `none` o `fallback-*`, detecta pérdida de contexto y re-inyecta el registry antes de continuar.

**Gap:** No sabemos si un agente cargó sus KBs correctamente. No hay feedback loop entre agente y orquestador sobre carga de skills.

---

### 3. Sub-Agent Launch Deduplication

El orquestador mantiene un log `(phase, task-fingerprint)` por sesión y no lanza el mismo par dos veces.

**Gap:** En conversaciones largas o con re-intentos podemos lanzar el mismo agente para el mismo trabajo varias veces sin saberlo.

---

### 4. `delegate_only` en frontmatter

Además de `user-invocable`, tienen un campo `delegate_only: true/false`. Si es `true`, el orquestador no puede invocar ese skill inline — solo puede delegarlo a un subagente.

**Gap:** Nuestro `user-invocable: false` no distingue entre "no invocable por el usuario" y "no invocable inline por el orquestador". La semántica es más difusa.

---

### 5. `_shared/` con protocolos comunes

Directorio con archivos que todos los agentes de fase deben leer antes de trabajar:
- `sdd-phase-common.md` — skeleton idéntico para todas las fases (carga de skills, recuperación de artefactos, persistencia, return envelope)
- `skill-resolver.md` — protocolo universal para que subagentes resuelvan skills antes de ejecutar
- `persistence-contract.md` — contrato de persistencia detallado
- `engram-convention.md` — naming determinístico de Engram

**Gap:** Cada agente nuestro tiene sus propias instrucciones de carga sin un skeleton común. Si cambia el protocolo, hay que actualizar cada agente por separado.

---

### 6. `references/` por skill

Las skills pueden tener un subdirectorio `references/` con archivos de referencia adicionales (documentación larga, ejemplos, casos edge). El `SKILL.md` es conciso y apunta a esos archivos cuando necesita profundidad.

**Gap:** Metemos todo en `SKILL.md`. Skills grandes no tienen manera de externalizar su contenido de referencia sin romper la estructura.

---

### 7. Session Close Protocol (mandatory)

Protocolo obligatorio al final de cada sesión para guardar en memoria:

```
## Goal       — qué estábamos haciendo
## Instructions — preferencias del usuario descubiertas
## Discoveries  — findings técnicos, gotchas, learnings
## Accomplished — items completados con detalle
## Next Steps   — qué queda por hacer
## Relevant Files — path — descripción
```

Cada agente lo ejecuta aunque el usuario no lo pida explícitamente.

**Gap:** Tenemos memoria automática pero no un protocolo formalizado de cierre. El criterio de qué guardar al final es implícito.

---

### 8. Proactive Save Triggers detallados

Lista explícita de cuándo guardar en memoria **sin esperar al usuario**:
- Decisión arquitectónica tomada
- Convención de equipo establecida
- Tool/library elegida con tradeoffs
- Bug fix con root cause identificada
- Feature implementada con approach no-obvio
- Gotcha, edge case, comportamiento inesperado encontrado
- Patrón establecido (naming, estructura, convención)
- Preferencia de usuario o constraint aprendida
- Setup o configuración completada

**Gap:** Tenemos memoria automática pero el criterio de cuándo guardar es más difuso. No hay una lista normativa que los agentes puedan seguir.

---

### 9. `openspec/config.yaml` — Configuración de proyecto persistente

Archivo de configuración a nivel de proyecto que el orquestador lee en el init y propaga a todos los agentes:

```yaml
strict_tdd: true
test_commands:
  unit: go test ./...
  integration: go test -tags=integration ./...
rules:
  apply: [red-green-refactor]
  verify: [check-coverage]
```

**Gap:** No tenemos configuración de proyecto persistente entre sesiones. Decisiones como "este proyecto usa TDD estricto" o "el modelo preferido es X" se pierden al cerrar la conversación.

---

### 10. State Recovery Post-Compaction

Guardan `state.yaml` en cada artefacto de cambio con el estado del DAG:

```yaml
phase: tasks
completed: [proposal, specs, design]
pending: [apply, verify, archive]
last_change: agent-builder
```

Si la conversación se compacta, el orquestador puede recuperar exactamente en qué punto estaba sin preguntar al usuario.

**Gap:** Nuestras sesiones son largas y la compactación rompe el contexto del orquestador. No hay mecanismo de recovery — el usuario tiene que re-orientar al orquestador desde cero.

---

## Lo que hacemos diferente (no peor)

Su SDD es más ligero — 10 fases orientadas a implementación:
`propose → specs → design → tasks → apply → verify → archive`

El nuestro es más profundo en la fase de producto:
- PRD con revisión y change governance
- Análisis de gaps con decisiones de negocio
- Discovery de features con trazabilidad RF→Feature
- Specs con HUs, criterios de aceptación y shared models
- Design system completo (DESIGN_BRIEF, DESIGN.md, flows, views, ui_prompt)

Su "spec" es un delta spec por dominio. El nuestro tiene trazabilidad RF→HU→Feature completa. Son objetivos distintos — el nuestro cubre más fase de producto, el suyo cubre mejor la fase de implementación.

---

## Priorización de los 3 más aplicables

1. **Model assignment por fase** — impacto directo en coste/calidad, implementable en frontmatter de agentes
2. **Skill resolution feedback** — mejora la fiabilidad de carga de KBs en subagentes, sin cambios de arquitectura
3. **State recovery post-compaction** — nuestras sesiones son largas y la compactación es un problema real y recurrente
