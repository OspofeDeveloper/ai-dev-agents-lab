# Scripts deterministas

Los scripts son el músculo del enforcement: convierten la prosa "verifica que X" en
garantías mecánicas (ver [diseño técnico](../entender/tecnico.md)). Viven en
`sdd/scripts/` (SSoT) y se distribuyen a `.sdd/scripts/` de cada proyecto, sellados
con su versión. Esta página es la referencia de interfaz y exit codes.

!!! abstract "Convención de exit codes"
    Los **hooks** (gate, permisos, lint, sesión) salen casi siempre `0` y comunican
    su decisión por stdout — fallan abiertos. Las **herramientas CLI** usan
    `0` = OK, `1` = error de uso/IO, `2` = condición de negocio no cumplida,
    `3` = no encontrado (solo `find`).

---

## Gates — deniegan (hooks)

### `sdd-gate-check.py` · hook `PreToolUse` (matcher `Skill`)
Verifica precondiciones **por contenido** antes de invocar un workflow.

- **Entrada:** JSON del hook por stdin.
- **Gates:** `wf-prepare-tasks` (plan `VALIDADO`, sin enmiendas) · `wf-prepare-plan`
  / `wf-design-system` / `wf-design-feature-prototype` / `wf-qa-plan` (spec sin
  `[INCOMPLETO]`/`[CRÍTICO]`/`[INFERIDO]`, `status_sync` fiable, hash de PRD
  sincronizado) · `wf-task-run` (plan origen vigente; task no retenida por enmienda).
- **Exit:** `0` siempre (deniega emitiendo JSON; fail-open ante stdin malformado,
  path no resoluble o error interno).

---

## Selladores — escriben estado (un solo autor por estado)

### `sdd-seal.py` · `seal | check | unseal <plan.md>`
Sella un plan a `Estado: VALIDADO` solo si pasan **8 condiciones** (estructura;
4 líneas de gaps en "ninguno"; sin `[INCOMPLETO]`; spec origen resoluble y sin
marcadores; `status_sync` fiable; hash de PRD; **cobertura de todo `CA-XXX`**; deuda
técnica aprobada). Si falla, fuerza `BORRADOR`.

- **Exit:** `0` OK/sellado · `1` error IO · `2` condiciones no cumplidas.

### `sdd-task-state.py` · `init | check | next | set <tasks.md> [T-00X ESTADO] [--motivo …] [--force]`
Único escritor del estado de una task. Máquina de transiciones validada
(`PENDIENTE → EN_CURSO → HECHA | BLOQUEADA`); `HECHA` exige deps `HECHA`, `BLOQUEADA`
exige `--motivo`, reapertura solo con `--force`. `next` resuelve elegibilidad y
salta tasks retenidas por enmienda. Regenera la tabla `## Progreso`.

- **Exit:** `0` OK · `1` error IO · `2` transición inválida / no elegible.

### `sdd-release.py` · `stamp | check <feature_dir> [--tag T] [--sha S] [--note …]`
Vincula el cierre de una feature a un commit. **Gate:** rechaza sin `_qa_report.md`
APTO/APTO_CON_RESERVAS. Captura el SHA con `git rev-parse` (no se teclea); escribe
`R-00X` en `<feature>_release.md` (las re-releases se acumulan).

- **Exit:** `0` OK · `1` error de uso · `2` gate rechazado.

### `sdd-sync-check.py` · `seal | check | check-all <spec|dir> [--mark] [--prd …]`
Detector de deriva PRD→spec. `seal` escribe `derived_from_prd_hash: sha256:<hex>`.
`check` recomputa: IN_SYNC / DERIVA / SIN_SELLO / PRD_NO_RESUELVE. Con `--mark`,
degrada `status_sync` a `needs_review`.

- **Exit:** `0` OK/sin deriva · `1` error IO · `2` deriva detectada.

### `sdd-amend.py` · `mark | clear | list | next-ref <plan.md> [--ca CA-XXX | --ref E-00X | --all]`
Anota `> **Enmienda pendiente:** CA-XXX (E-00X, fecha)` tras `Estado:` del plan
(numeración `E-NNN` determinista). `sdd-seal.py` la absorbe al re-validar.

- **Exit:** `0` OK · `1` error IO · `2` nada que limpiar / plan sin `Estado`.

---

## Funciones puras — no escriben

### `sdd-resolve-path.py` · `write | find | rel-from | kinds <kind> <input> [--local-root D]`
SSoT del layout de artefactos. `write` → ruta canónica donde escribir; `find` →
artefacto existente en **ambos** layouts; `rel-from` → ruta relativa para el header
de trazabilidad.

- **Exit:** `0` OK · `1` error de uso · `3` (`find`) no existe.

### `sdd-next-id.py` · `<prefijo> <archivo…> [--width N]`
Siguiente ID secuencial libre (`B-00X`, `F-001`, …). Lookbehind para desambiguar
prefijos (`F` ≠ `RF` ≠ `F-C`).

- **Exit:** `0` ID emitido · `1` error de uso.

### `sdd-features-index.py` · `<dir> [--check | --stdout]`
Regenera `_features.md` como función pura de specs + discovery + readiness.

- **Exit:** `0` OK · `1` error IO · `2` (`--check`) desactualizado en disco.

### `sdd-project-status.py` · `<dir> [--output F]`
Informe PM read-only: agrega el estado real de las features escaneando disco.

- **Exit:** `0` siempre.

---

## Permisos y meta-tooling (hooks)

### `sdd-skill-allow.py` · hook `PermissionRequest` (matcher `Skill`)
Auto-aprueba **solo** workflows `wf-*`; `kb-*` y skills ajenas siguen el flujo
normal. Se evalúa después del gate `PreToolUse` (cuyo deny prevalece).

- **Exit:** `0` siempre.

### `sdd-structural-lint.py` · `[--check] [--json] [--severity blocking|warning|all] [--root P]`
Validador estructural del ecosistema (NAME-MISMATCH, CITED-RULE-MISSING,
ABSOLUTE-PATH, ALLOWED-TOOLS-MISMATCH, DESCRIPTION-TOO-LONG…). Gate de cierre de los
workflows de creación.

- **Exit:** `0` limpio · `1` solo warnings · `2` ≥1 blocking (con `--check`).

### `sdd-meta-lint-hook.py` · hook `PostToolUse` (`Write|Edit|MultiEdit`)
Al editar a mano un `SKILL.md`/agente del ecosistema, inyecta sus findings blocking
vía `additionalContext`. Advisory: nunca deshace la escritura.

- **Exit:** `0` siempre.

### `sdd-scaffold.py` · `kb | wf | agent <nombre> --phase <fase> [--dry-run] [--force]`
Genera el esqueleto con frontmatter canónico por construcción. Lo que produce pasa
el linter con 0 blocking.

- **Exit:** `0` escrito/dry-run · `2` error / destino existe.

### `sdd-kb-check.py` · `[--all | --agent <n>] [--claude-dir P] [--quiet]`
Verifica que cada KB declarada en el frontmatter `skills:` de un agente existe
instalada.

- **Exit:** `0` OK · `1` error de uso · `2` KB faltante.

---

## Distribución y bootstrap

### `generate-skill-registry.py`
Escanea el ecosistema y regenera `meta/skill-registry.md` (el catálogo no puede
mentir porque sale del filesystem).

### `merge-claude-settings.py` · `<source.json> <dest.json>`
Merge conservador e idempotente de `settings.json`: añade lo del framework,
preserva lo del proyecto. SSoT del merge de hooks/permisos.

### `bootstrap/sdd-session-check.sh` · hook `SessionStart`
Inyecta la directiva `[SDD-PROTOCOL]` (`mode-undecided` / `init-pending` /
`init-incomplete` / `version-drift`) según el estado del proyecto. Se silencia en
CI (`CI=true`, `SDD_NON_INTERACTIVE=1`).

- **Exit:** `0` siempre.

!!! note "Versión actual"
    Las cifras y la lista reflejan el ecosistema en su versión vigente
    (`sdd/VERSION`). Cada copia instalada lleva su sello `# sdd-version:` en la
    línea 2 del script.
