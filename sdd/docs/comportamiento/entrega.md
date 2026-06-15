# Plan, tasks y entrega — `EC-DELIV`

!!! warning "Área en construcción"
    Casos del sellado y la ejecución (el complemento *en positivo* de los
    [gates](gates.md)). Cobertura prevista: `sdd-seal.py` sella `VALIDADO` solo con
    las 8 condiciones (y degrada a `BORRADOR` si se altera a mano); máquina de
    estados de tasks (`sdd-task-state.py`: transiciones válidas, deps, `--force`);
    `wf-task-run` con verificación ejecutable y commit por task; QA con evidencia
    (`DIVERGENTE` → `wf-bug`, nunca se ajusta el TC); gate de release (sin QA APTO →
    rechazo) y captura del SHA con git. Muy auto-cubierto por `tests/` (seal,
    task-state, release).
