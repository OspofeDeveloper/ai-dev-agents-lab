# Suite de tests del ecosistema SDD

Black-box tests del ecosistema SDD. Sustituyen la verificacion ad-hoc en
tmpdirs por una suite reproducible. Dos bloques:

- **Scripts deterministas** (ROADMAP 11.3a): los 13 scripts de `sdd/scripts/`.
- **Installers** (ROADMAP 11.3b): `install.sh`, `tech/kmm/install.sh`, `setup.sh`.
- **Hook de sesion** (ROADMAP 11.3c): `bootstrap/sdd-session-check.sh`.

## Como correrla

Desde la **raiz del repo**:

```bash
bash sdd/tests/run-tests.sh
```

o directamente:

```bash
python3 -m unittest discover -s sdd/tests -p 'test_*.py' -v
```

Para un solo script:

```bash
python3 -m unittest discover -s sdd/tests -p 'test_sdd_seal.py' -v
```

## Diseno

- **Solo stdlib** (`unittest`, `subprocess`, `tempfile`, `json`, `pathlib`,
  `shutil`). Cero dependencias externas (no pytest). Compatible con Python 3.9+.
- **Black-box por subproceso**: cada test invoca el script/installer como CLI
  (`python3 sdd/scripts/<x>.py <args>` o `bash <installer>.sh ...`) sobre
  fixtures creados en `tempfile.TemporaryDirectory()` y comprueba exit code +
  stdout/stderr + ficheros resultantes. Refleja el contrato real y evita
  importar modulos con guion en el nombre.
- Helpers compartidos en `_helpers.py` (`run_script`, `run_script_at`,
  `run_bash`, `write`).

## Cobertura — scripts deterministas (11.3a)

| Script | Fichero de test | Que cubre |
|---|---|---|
| `sdd-seal.py` | `test_sdd_seal.py` | sellable -> sella; no sellable (CA sin cubrir, `[INFERIDO]`/`[CRÍTICO]`/`[INCOMPLETO]`, gap abierto, spec origen no resoluble, TD pendiente); idempotencia; deteccion de tamper; `--unseal`; TD aprobada no bloquea |
| `sdd-gate-check.py` | `test_sdd_gate_check.py` | precondicion OK -> permite; fallida -> deny con motivo; fail-open (stdin ilegible, skill sin gate, path no resoluble) |
| `sdd-task-state.py` | `test_sdd_task_state.py` | init + tabla Progreso; transiciones validas/invalidas; bloqueo por deps; persistencia; idempotencia; BLOQUEADA exige motivo; reapertura con `--force` |
| `merge-claude-settings.py` | `test_merge_claude_settings.py` | dest inexistente -> copia; merge conserva claves del proyecto; idempotente; no duplica matchers; elimina hooks deprecated |
| `sdd-features-index.py` | `test_sdd_features_index.py` | genera `_features.md`; idempotente byte-identico; `--check` 0/2; `--stdout`; layout subcarpeta y plano legacy; estados (PENDIENTE_GENERACIÓN, BLOQUEADA, LISTA); readiness autoritativo |
| `sdd-structural-lint.py` | `test_sdd_structural_lint.py` | los 10 tipos de finding (plantado vs limpio); exit codes 0/1/2; forma de `--json`; `--severity`; los 2 edge-cases criticos (description-provenance, fork-pattern) |
| `generate-skill-registry.py` | `test_generate_skill_registry.py` | escaneo correcto; idempotencia byte-identica; nueva skill aparece tras regenerar |
| `sdd-amend.py` | `test_sdd_amend.py` | mark/clear/list/next-ref; numeracion E-NNN; roundtrip mark->clear |
| `sdd-release.py` | `test_sdd_release.py` | gate QA (NO_APTO -> exit 2; APTO/APTO_CON_RESERVAS); SHA mecanico contra repo git real; re-releases R-00X |
| `sdd-sync-check.py` | `test_sdd_sync_check.py` | sello de hash del PRD; deriva plantada vs limpia; `--mark`; `check-all` |
| `sdd-project-status.py` | `test_sdd_project_status.py` | fase por presencia de artefactos; read-only (digest invariante); PENDIENTE_GENERACIÓN; layout plano |
| `sdd-kb-check.py` | `test_sdd_kb_check.py` | KB presente/ausente; `--agent`/`--all`; frontmatter inline y multilinea |
| `sdd-skill-allow.py` | `test_sdd_skill_allow.py` | auto-allow de `wf-*`; kb/skills ajenas pasan al flujo normal; forma `plugin:skill` |

## Cobertura — installers (11.3b)

Tests de integracion que instalan el ecosistema en proyectos sinteticos
(tmpdir) y verifican los invariantes que han mordido en sesiones reales.

| Installer | Fichero de test | Que cubre |
|---|---|---|
| `install.sh` | `test_install_sh.py` | install all (agentes/skills/rules/scripts sellados/settings/CLAUDE.md); install por fase (spec, plan) con dependencias cross-fase; fase desconocida -> exit 1; `--prune` poda huerfanos / sin `--prune` avisa; idempotencia del merge de settings; `SDD_PROJECT_ROOT` redirige `.sdd/` a la raiz |
| `tech/kmm/install.sh` | `test_kmm_install_sh.py` | regla `sdd-kmm.md` con `paths:`; NO pisa el CLAUDE.md raiz (lo crea ni lo sobreescribe); instala `kb-kmm-project-state-protocol` (bug 0.1) y agentes KMM; override por basename de `plan-architect`/`kb-plan-expert`; install.sh re-aplica el overlay leyendo `stack` de project-init.json (bug 6.6); stack desconocido -> aviso sin fallo |
| `setup.sh` | `test_setup_sh.py` | install fresco (hook, `~/.sdd-home`, registro en settings, bloque SDD-BOOTSTRAP, skills globales); idempotencia (no duplica hook ni bloque); preserva settings/CLAUDE.md ajenos; `--uninstall` revierte preservando lo ajeno; arg desconocido -> exit 1. Aislado con `HOME` falso; NO ejercita `--dev` (mutaria el repo real) |

## Cobertura — hook de sesion (11.3c)

`test_session_hook.py` (24): matriz de estados de `bootstrap/sdd-session-check.sh`,
aislado con `CLAUDE_PROJECT_DIR` + `HOME` falso + `CI=""`/`SDD_NON_INTERACTIVE=""`
(neutralizan la herencia del runner). El hook siempre sale 0; la senal es su stdout.

| Grupo | Que cubre |
|---|---|
| estados de directiva | virgen -> `mode-undecided`; `sdd-mode.json` free -> silencio; sdd sin init -> `init-pending`; init completo -> silencio; init con fase sin regla -> `init-incomplete`; init gana sobre modo |
| version-drift | sellos distintos -> `version-drift`; iguales -> silencio; sin sello de proyecto -> silencio |
| opt-out | `CI=true` y `SDD_NON_INTERACTIVE=1` -> silencio; `CI=false` actua; `HOME==proyecto` -> silencio |
| exclusion repo SDD | proyecto bajo `~/.sdd-home` -> silencio; fuera -> actua |
| deny/allowlist (5.6) | denylist hit -> silencio / miss y comentada -> actua; allowlist opt-in fuera -> silencio / cubriendo -> actua |
| techo git monorepo (5.7) | encuentra marcador en ancestro hasta el git root; gana el ancestro mas cercano; no cruza el git root; sin git no sube. `@skipIf` si no hay git |

> **Tiempo de ejecucion:** los tests de `install.sh`/`tech/kmm/install.sh` son
> lentos (~1-2 min cada fichero) porque cada install copia ~130 skills fichero a
> fichero en tmpdir. `setup.sh` es rapido (~2 s). Los de scripts deterministas
> tambien (segundos). Para iterar rapido, corre solo el fichero relevante con
> `-p`.

## Notas de testabilidad

- `sdd-structural-lint.py` gano un flag `--root <path>` (retrocompatible: default
  = escanear el arbol del ecosistema, comportamiento de siempre) para poder
  apuntarlo a arboles-fixture aislados. La suite verifica que el escaneo por
  defecto sigue intacto (`DefaultScanTest`).
- `generate-skill-registry.py` no acepta argumento de ruta ni `--check`; resuelve
  su raiz desde `__file__` y siempre escribe `meta/skill-registry.md`. Para
  aislarlo se copia el script a un arbol-fixture y se ejecuta desde ahi. No hay
  modo `--check` que testear (no existe).
