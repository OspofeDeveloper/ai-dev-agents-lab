---
name: wf-task-run
description: "Ejecuta las tasks de un _tasks.md con estado persistente, validación de DoD y commits trazables (T-00X, CA-XXX). Delega cada task a su Owner agent (overlay de stack) o la implementa el orquestador en modo agnóstico. Cierra el ciclo spec → plan → tasks → implementación."
when_to_use: "Activa en frases como 'ejecuta las tasks', 'implementa la siguiente task', 'continúa con la implementación', 'corre T-003', 'retoma las tasks de la feature'. No activa para generar tasks (usa wf-prepare-tasks), ni para arreglar bugs sobre código ya entregado (usa wf-bug)."
argument-hint: "<feature_tasks.md> [--task T-00X | --next | --all] [--no-commit]"
effort: high
allowed-tools: [Read, Write, Edit, Bash, Agent]
context: fork
user-invocable: true
---

# task-run — Ejecución de Tasks con estado persistente

Tu rol es de **director de ejecución**: seleccionas la task elegible, la delegas a su owner, validas el DoD con evidencia y registras estado y commit. **No marcas estados a mano**: todos los cambios de estado pasan por `sdd-task-state.py` (autor ≠ marcador). No reordenas tasks ni redefines su contenido.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del `_tasks.md`**: primer argumento (obligatorio)
- **Selección**: `--task T-00X` (una concreta) | `--next` (la siguiente elegible) | `--all` (en orden hasta terminar o bloquearse). **Default: `--next`** — una task por invocación.
- `--no-commit`: no commitear (el usuario gestiona el historial)

Sin argumentos → informa:
> "Uso: `/wf-task-run <feature_tasks.md> [--task T-00X | --next | --all] [--no-commit]`"

## Paso 2: Verificar precondiciones (gate)

1. Lee el `_tasks.md` completo. Debe contener tasks `## T-XXX:` y header de trazabilidad.
2. Resuelve `Plan origen` (relativo al `_tasks.md`) y verifica `Estado: VALIDADO` en el plan. Si está en `BORRADOR` → detén:
   > "❌ El plan origen ya no está VALIDADO. Pasa `/wf-plan-validate <plan.md>` antes de ejecutar tasks."
3. Si el plan declara `Status sync` distinto de `in_sync` → detén y remite a resincronizar.
4. Determina el modo de ejecución desde `.sdd/project-init.json` (directorio actual o ancestro): con `"stack"` concreto → los owners son agentes del overlay; `"agnostico"` o sin archivo → modo genérico (owner `orquestador` = tú implementas).

No bypasses este gate: existe también como verificación determinista en `.sdd/scripts/sdd-gate-check.py`.

## Paso 3: Inicializar / leer estados

```bash
!python3 .sdd/scripts/sdd-task-state.py check <tasks.md>
```

- Si reporta `SIN_ESTADO` en alguna task (archivo legacy o recién generado) → `init` primero:
  ```bash
  !python3 .sdd/scripts/sdd-task-state.py init <tasks.md>
  ```
- Si el script no existe en `.sdd/scripts/`, detén e indica reinstalar con `install.sh` — **no gestiones estados a mano**.

## Paso 4: Seleccionar task

- `--task T-00X`: verifica con `check` que está `PENDIENTE` (o `EN_CURSO` ya iniciada) y sus `Dependencies` HECHAS. Si no es elegible → informa qué dependencias faltan y detén.
- `--next` (default): `python3 .sdd/scripts/sdd-task-state.py next <tasks.md>` → usa el ID devuelto. Si devuelve `COMPLETO` → informa y termina. Si `NINGUNA_ELEGIBLE` → muestra el `check` (qué está bloqueado y por qué) y termina. Si `RETENIDAS_POR_ENMIENDA` → solo quedan tasks retenidas por una enmienda pendiente en el plan (stale puntual de `/wf-spec-amend`); informa y remite a cerrar la revisión del plan (la dejó indicada el amend) o a `/wf-plan-validate <plan.md>` (el re-sellado absorbe la enmienda) — no las fuerces.
- `--all`: repite el ciclo Pasos 5-8 mientras `next` devuelva IDs.

## Paso 5: Marcar EN_CURSO y delegar al owner

```bash
!python3 .sdd/scripts/sdd-task-state.py set <tasks.md> T-00X EN_CURSO
```

Lee el bloque completo de la task (Spec CA, Plan ref, Componente, Layer, Input, DoD, y `Deuda asumida` si está presente).

Si la task declara `- **Deuda asumida:** TD-00X`, inclúyela en el prompt del owner como **restricción a respetar**: implementa conforme a la decisión documentada en la sección `## Deuda técnica asumida` del plan, asumiendo la limitación descrita. El owner NO debe "resolver" la limitación por su cuenta ni cambiar de enfoque para evitarla — si cree que la deuda ya no aplica o que hay una salida mejor, lo reporta, no lo decide.

**Modo overlay** (owner = agente del stack): invoca el `Agent` tool con `subagent_type` = el `Owner agent` de la task, **`run_in_background: false`** y este prompt:

```
Implementa la task T-00X de <tasks.md>.

<bloque completo de la task>

Contexto del plan (sección referida en Plan ref): <extracto relevante del _plan.md>

INSTRUCCIONES:
- Implementa EXACTAMENTE lo que define la task. No expandas alcance ni toques componentes de otras tasks.
- El Definition of done es tu contrato de salida. Reporta evidencia concreta de cada punto del DoD (archivos creados/modificados, salida de compilación/tests).
- Si descubres que la task no es implementable tal cual (falta un contrato, contradicción con el código), NO improvises: reporta el bloqueo con detalle.
- Si el bloqueo es que un CA del spec es AMBIGUO (admite más de una implementación y el texto no determina cuál), repórtalo identificando el CA-XXX y las interpretaciones posibles — no elijas una por tu cuenta.
- Reporta honestamente: si algo falla, di qué y por qué. Un reporte de fallo es un resultado válido; uno falsamente verde no.
```

> **`run_in_background: false` es obligatorio ([[D-043]]).** Desde Claude Code v2.1.198 los subagentes corren en **background por defecto**, y el Paso 6 valida el DoD contra el **reporte del owner** y el Paso 7 commitea lo que escribió: sin el flag validarías y commitearías **antes** de que el owner termine de escribir. **Espera su resultado**; no deduzcas que acabó listando ficheros ni relances un segundo owner sobre la misma task.

**Modo agnóstico** (owner = `orquestador`): implementa tú la task directamente con las mismas reglas (alcance exacto, DoD como contrato, honestidad en el reporte).

## Paso 6: Validar DoD con verificación ejecutable

1. Contrasta el reporte del owner contra cada punto del `Definition of done`. Verifica tú que los archivos declarados existen (`Read`/`ls`) — no aceptes el reporte sin evidencia.
2. **Verificación ejecutable** (si el proyecto la permite):
   - Si existe `<stack>_project_state.md` (p. ej. `kmm_project_state.md`), usa sus comandos de build/test declarados.
   - Si no, detecta el runner por archivos del repo (`gradlew`, `package.json`, `Makefile`, `pyproject.toml`...) y ejecuta build + tests del módulo afectado.
   - Si no hay forma razonable de ejecutar nada, registra explícitamente "verificación ejecutable: no disponible" en el resumen — nunca lo presentes como verificado.
3. Para tasks `Layer: test` en orden TDD, el DoD esperado es RED: el test compila y **falla** con mensaje claro. Verde prematuro = fallo de DoD.

## Paso 7: Cerrar estado

- **DoD cumplido** → `set T-00X HECHA`. Si el script devuelve exit 2 (deps no hechas), algo está mal en el orden: detén e informa, no uses `--force`.
- **DoD no cumplido pero recuperable** (falta un detalle, test en rojo inesperado) → deja `EN_CURSO`, informa qué falta y detén (en `--all`, detén el lote).
- **Bloqueo real** (dependencia externa, contradicción con el plan) → `set T-00X BLOQUEADA --motivo "<motivo concreto>"`. Según el origen del bloqueo:
  - **CA ambiguo** (la intención no cambia, pero el texto admite varias implementaciones) → back-edge corto: `/wf-spec-amend <spec.md> --ca CA-XXX --from-task T-00X`. No re-desciendas el waterfall por una aclaración.
  - **El comportamiento esperado debe cambiar** → `/wf-spec-delta analyze <spec.md> --new-reqs <descripción>`.
  - **Contradicción del plan con el repo** → `/wf-plan-validate <plan.md>`.

## Paso 8: Commit trazable

Salvo `--no-commit`:

```bash
!git add <archivos de la task + tasks.md> && git commit -m "T-00X: <título de la task> [CA-XXX]"
```

- Un commit por task — incluye el `_tasks.md` actualizado (estado + Progreso) en el mismo commit.
- `CA-XXX` sale del campo `Spec CA` de la task; si es `—`, omite el sufijo.
- Nunca `git add -A` indiscriminado: solo lo que la task tocó. Si hay cambios ajenos en el working tree, déjalos fuera y avisa.

> SSoT del criterio de empaquetado: `kb-delivery-discipline` (por qué el commit-unidad es atómico y verde, tests junto al código, y cómo dividir una feature grande en una cadena de PRs apilados por fronteras de dependencia). El commit-por-task no cambia.

## Paso 9: Informar

- Task(s) ejecutada(s), estado final y commit(s).
- Resumen de la tabla `## Progreso` (X/N HECHA).
- Resultado de la verificación ejecutable (o su ausencia, explícita).
- Siguiente paso: la task que devuelve `next`, o si `COMPLETO` → "Feature implementada. Cierra el ciclo QA con `/wf-qa-verify <path>_qa_plan.md` (si no existe el QA plan: `/wf-qa-plan generate <path>_spec.md` primero); `/wf-spec-readiness` para el estado global."
