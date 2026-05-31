# Comparativa Gentle-AI vs SDD Ecosistema

Análisis de `github.com/gentleman-programming/gentle-ai-main` — 2026-05-31.
Fuente: exploración directa del repositorio.

Pendientes: mejoras relacionadas con persistencia y memoria entre sesiones.

---

## Pendientes de implementar

### 1. Session Close Protocol (mandatory)

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

### 2. Proactive Save Triggers detallados

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

### 3. `openspec/config.yaml` — Configuración de proyecto persistente

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

### 4. State Recovery Post-Compaction

Guardan `state.yaml` en cada artefacto de cambio con el estado del DAG:

```yaml
phase: tasks
completed: [proposal, specs, design]
pending: [apply, verify, archive]
last_change: agent-builder
```

Si la conversación se compacta, el orquestador puede recuperar exactamente en qué punto estaba sin preguntar al usuario.

**Gap:** Nuestras sesiones son largas y la compactación rompe el contexto del orquestador. No hay mecanismo de recovery — el usuario tiene que re-orientar al orquestador desde cero.
