# Changelog del ecosistema SDD

Formato: `## <versión> — <fecha>`. Las líneas con `⚠` son cambios que afectan a proyectos ya inicializados (`wf-sdd-update` las muestra al actualizar).

## 0.2.0 — 2026-06-07

Enforcement de sincronía PRD→spec y auto-allow acotado (ROADMAP 1.3 y 1.4):

- Detección determinista de deriva PRD→spec: `sdd-sync-check.py` (script de enforcement nuevo) sella `derived_from_prd_hash` (sha256 del PRD origen) en el header del spec; `seal` al generar/resincronizar, `check`/`check-all --mark` para detectar divergencia (degrada `status_sync` a `needs_review`). Único escritor del campo: el script (separación autor/verificador).
- ⚠ Los gates (`sdd-gate-check.py`) y el sellador de planes (`sdd-seal.py`) ahora verifican el hash: si el PRD cambió desde que se generó/sincronizó el spec, `wf-prepare-plan`/`wf-design-*` se deniegan y el plan no se sella hasta resincronizar (`/wf-prd-sync-impact` + `/wf-spec-sync-from-prd`). Los specs sin sello (legacy) no bloquean.
- Auto-allow de Skills acotado: el `Skill(.*)` universal del `settings.json` se sustituye por `sdd-skill-allow.py` (PermissionRequest), que solo auto-aprueba workflows SDD (`wf-*`); cualquier otra skill sigue el flujo normal de permisos. Los gates PreToolUse prevalecen sobre el allow.
- ⚠ Migración automática al actualizar: `merge-claude-settings.py` elimina del settings del proyecto la entrada antigua de auto-allow universal (identificada por su comando exacto; los hooks propios del equipo no se tocan) y añade la acotada. Hace falta re-ejecutar la instalación (`/wf-sdd-update`) para distribuir los scripts nuevos a `.sdd/scripts/`.

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
