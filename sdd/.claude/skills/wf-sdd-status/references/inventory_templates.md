# Plantillas de inventario del ecosistema SDD

## Formato del snapshot (Paso 6)

```
# SDD Ecosystem Status
Fecha: <fecha>
Alcance: <fase o global>

## Resumen
- Skills totales: X (Y kb-*, Z wf-*)
- Agentes totales: N
- KBs sin consumidor: M
- Workflows sin registrar en rootmap: P

## Por fase

### <fase> (o .claude para meta-ecosistema)
Agentes (N):
  - <nombre> — <primera linea de description>

kb-* (Y):
  - <nombre> — <primera linea de description>

wf-* (Z):
  - <nombre> [SIN REGISTRAR?] — <primera linea de description>

### tech/<stack>
  [misma estructura]

## KBs sin consumidor
  - <path> — <nombre>

## Workflows sin registrar en rootmap
  - <path> — <nombre>
```

## Formato del skill-registry (Paso 6.5)

```markdown
# SDD Skill Registry
<!-- Auto-generado por wf-sdd-status. No editar manualmente. -->
<!-- Total: X skills | Y user-invocable | Z kb-* -->

## Meta-Ecosistema (.claude/)
| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| <nombre> | <primera línea de description> | true/false | <path relativo desde sdd/> |

## Fase: PRD
...
## Fase: Spec
...
## Fase: Design
...
## Fase: Plan
...
## Fase: Tasks
...
## Tech: KMM — Plan
## Tech: KMM — Tasks
## Tech: KMM — Workflows
```

`Path` siempre relativo desde `sdd/` (ejemplo: `.claude/skills/kb-sdd-audit-content/SKILL.md`).
