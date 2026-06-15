# Arranque y sesión — `EC-INIT`

!!! warning "Área en construcción"
    Casos del hook `SessionStart` y del init. Cobertura prevista: proyecto virgen →
    wizard de modo (`mode-undecided`); modo libre → silencio para siempre;
    `init-pending` / `init-incomplete` → reparación; `version-drift` → aviso de una
    línea sin bloquear; opt-out por `CI`/`SDD_NON_INTERACTIVE`/`sdd-mode.json`;
    exclusión del repo del ecosistema; deny/allowlist por ruta; techo git en
    monorepos. Buena parte está auto-cubierta por `tests/test_session_hook.py`.
