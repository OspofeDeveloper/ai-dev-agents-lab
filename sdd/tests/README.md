# Suite de tests de `sdd/scripts/`

Unit / black-box tests de los scripts deterministas del ecosistema SDD
(ROADMAP 11.3a). Sustituyen la verificacion ad-hoc en tmpdirs por una suite
reproducible.

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
- **Black-box por subproceso**: cada test invoca `python3 sdd/scripts/<x>.py
  <args>` sobre fixtures creados en `tempfile.TemporaryDirectory()` y comprueba
  exit code + stdout/stderr + ficheros resultantes. Refleja el contrato real
  (los scripts son CLIs) y evita importar modulos con guion en el nombre.
- Helpers compartidos en `_helpers.py` (`run_script`, `run_script_at`, `write`).

## Cobertura

| Script | Fichero de test | Que cubre |
|---|---|---|
| `sdd-seal.py` | `test_sdd_seal.py` | sellable -> sella; no sellable (CA sin cubrir, `[INFERIDO]`/`[CRÍTICO]`/`[INCOMPLETO]`, gap abierto, spec origen no resoluble, TD pendiente); idempotencia; deteccion de tamper; `--unseal`; TD aprobada no bloquea |
| `sdd-gate-check.py` | `test_sdd_gate_check.py` | precondicion OK -> permite; fallida -> deny con motivo; fail-open (stdin ilegible, skill sin gate, path no resoluble) |
| `sdd-task-state.py` | `test_sdd_task_state.py` | init + tabla Progreso; transiciones validas/invalidas; bloqueo por deps; persistencia; idempotencia; BLOQUEADA exige motivo; reapertura con `--force` |
| `merge-claude-settings.py` | `test_merge_claude_settings.py` | dest inexistente -> copia; merge conserva claves del proyecto; idempotente; no duplica matchers; elimina hooks deprecated |
| `sdd-features-index.py` | `test_sdd_features_index.py` | genera `_features.md`; idempotente byte-identico; `--check` 0/2; `--stdout`; layout subcarpeta y plano legacy; estados (PENDIENTE_GENERACIÓN, BLOQUEADA, LISTA); readiness autoritativo |
| `sdd-structural-lint.py` | `test_sdd_structural_lint.py` | los 10 tipos de finding (plantado vs limpio); exit codes 0/1/2; forma de `--json`; `--severity`; los 2 edge-cases criticos (description-provenance, fork-pattern) |
| `generate-skill-registry.py` | `test_generate_skill_registry.py` | escaneo correcto; idempotencia byte-identica; nueva skill aparece tras regenerar |

## Notas de testabilidad

- `sdd-structural-lint.py` gano un flag `--root <path>` (retrocompatible: default
  = escanear el arbol del ecosistema, comportamiento de siempre) para poder
  apuntarlo a arboles-fixture aislados. La suite verifica que el escaneo por
  defecto sigue intacto (`DefaultScanTest`).
- `generate-skill-registry.py` no acepta argumento de ruta ni `--check`; resuelve
  su raiz desde `__file__` y siempre escribe `meta/skill-registry.md`. Para
  aislarlo se copia el script a un arbol-fixture y se ejecuta desde ahi. No hay
  modo `--check` que testear (no existe).
