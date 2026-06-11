# Reporte de Auditoría Estructural — Ecosistema SDD
**Modo:** structural | **Alcance:** global | **Fecha:** 2026-06-11

---

## Hallazgos bloqueantes

Ninguno. El ecosistema no tiene referencias rotas.

---

## Hallazgos de advertencia

```
[ADVERTENCIA] HUERFANA
Archivo: sdd/tasks/skills/kb-delivery-discipline/SKILL.md
Referencia: kb-delivery-discipline
Descripcion: Ningun agente del ecosistema la lista en su skills: [...]. La KB existe
             pero no se inyecta en ningun agente via el mecanismo de carga del harness.
Accion sugerida: Decidir si kb-delivery-discipline debe conectarse a algun agente
                 existente (candidatos: task-generator o qa-engineer) o documentarse
                 como excepcion explicita al patron de consumo via skills: [...].
Nota: Caso conocido documentado en docs/FABLE_REPORT.md (punto 25).
```

---

## Checks detallados

### Agentes — skills: [...] vs existencia de KBs (22 agentes)

| Agente | Skills declaradas | Estado |
|---|---|---|
| `design-architect` | 17 KBs | OK |
| `sdd-auditor` | 4 KBs | OK |
| `sdd-author` | 3 KBs | OK |
| `plan-architect` (generic) | 5 KBs | OK |
| `plan-auditor` (generic) | 4 KBs | OK |
| `prd-expert` | 2 KBs | OK |
| `sdd-spec-auditor` | 6 KBs | OK |
| `sdd-spec-explorer` | 7 KBs | OK |
| `sdd-spec-planner` | 7 KBs | OK |
| `sdd-spec-writer` | 7 KBs | OK |
| `qa-engineer` | 3 KBs | OK |
| `task-generator` (generic) | 3 KBs | OK |
| `kmm-explorer` | 27 KBs | OK |
| `kmm-feature-logic-implementer` | 10 KBs | OK |
| `kmm-feature-ui-implementer` | 8 KBs | OK |
| `kmm-network-auth-implementer` | 13 KBs | OK |
| `kmm-planner` | 23 KBs | OK |
| `kmm-platform-integrator` | 15 KBs | OK |
| `kmm-tester` | 3 KBs | OK |
| `plan-architect` (KMM) | 10 KBs | OK |
| `plan-auditor` (KMM) | 7 KBs | OK |
| `task-generator` (KMM) | 5 KBs | OK |

### Agentes — `name:` vs nombre de archivo

Todos sincronizados. 0 desincronizaciones.

### wf-* — `agent:` vs existencia del agente en agents/ (55 workflows)

Todas las referencias resolven correctamente. 0 referencias rotas.

### wf-* — `name:` vs nombre de directorio

Todos sincronizados. 0 desincronizaciones.

### CLAUDE.md rootmaps — referencias a wf-* y kb-* (8 CLAUDE.md)

Todas las referencias resuelven. 0 referencias rotas.

Referencias cross-fase correctas documentadas (no son errores):
- `spec/CLAUDE.md` → `/wf-prd-change` (vive en `prd/skills/`)
- `tasks/CLAUDE.md` → `/wf-spec-amend`, `/wf-spec-delta` (viven en `spec/skills/`)
- `tasks/CLAUDE.md` → `/wf-plan-validate` (vive en `plan/skills/`)

### kb-* — consumo por al menos un agente

Total KBs: 73 | Consumidas: 72 | Huerfanas: 1 (`kb-delivery-discipline`)

---

## Resumen

| Severidad | Tipo | Cantidad |
|---|---|---|
| Bloqueante `[ROTO]` | Referencia no resolvible | 0 |
| Advertencia `[HUERFANA]` | KB sin consumidor | 1 |
| Advertencia `[DESREGISTRADA]` | Workflow sin entrada en rootmap | 0 |
| Advertencia `[NOMBRE-DESINCRONIZADO]` | Frontmatter vs archivo | 0 |

**Estado global: CONSISTENTE**
