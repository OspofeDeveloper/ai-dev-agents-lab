# Robustez e instalación — `EC-ROBUST`

!!! warning "Área en construcción"
    Casos de instalación y resiliencia. Cobertura prevista: `wf-sdd-update` sobre un
    proyecto con overlay (sobreviven las variantes de stack); reinstalación con
    `--prune` (poda huérfanos) y sin `--prune` (avisa); merge idempotente de
    `settings.json` (preserva lo del equipo); layout plano legacy leído sin migrar;
    sesión abierta en un subdirectorio del proyecto (marcadores buscados hacia
    arriba hasta el git root); degradación con `tests: none`. Auto-cubierto por
    `tests/test_install_sh.py`, `test_kmm_install_sh.py`, `test_setup_sh.py`.
