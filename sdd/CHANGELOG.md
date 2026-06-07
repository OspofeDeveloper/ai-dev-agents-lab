# Changelog del ecosistema SDD

Formato: `## <versión> — <fecha>`. Las líneas con `⚠` son cambios que afectan a proyectos ya inicializados (`wf-sdd-update` las muestra al actualizar).

## 0.1.0 — 2026-06-07

Primera versión sellada. Estado consolidado tras las fases 0-3 del ROADMAP:

- Enforcement determinista: `sdd-seal.py` (sellado de planes, autor≠sellador), `sdd-gate-check.py` (gates PreToolUse), `sdd-task-state.py` (estados de tasks).
- Ciclo de vida completo: `wf-task-run` (ejecución con estado persistente y commits trazables) y `wf-bug` (fast-lane de mantenimiento con triaje contra CA).
- Onramp brownfield: `wf-spec-from-code` + `kb-spec-characterization` (specs de caracterización con evidencia obligatoria).
- ⚠ Los specs con CAs `[INFERIDO]` bloquean `wf-prepare-plan` y el sellado de planes (igual que `[INCOMPLETO]`).
- ⚠ Layout de feature por subcarpetas (`features/<n>/spec|design|plan|tasks/`); el layout plano anterior sigue siendo válido (los workflows leen ambos, no los mezclan).
- ⚠ Infraestructura única: un solo `.claude/` raíz con rules de carga perezosa por `paths:` (`.claude/rules/sdd-<fase>.md`); los layouts antiguos (`.claude/phases/`, `<fase>/.claude/`) siguen reconocidos por el hook.
- Mapa `artifacts` en `project-init.json` (ubicación de artefactos por fase).
- Versionado del ecosistema: `VERSION` + sello `.sdd/sdd-version.json` + `wf-sdd-update`.
