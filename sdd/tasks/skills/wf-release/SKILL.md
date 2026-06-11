---
name: wf-release
description: "Vincula el cierre de una feature (QA APTO) a un punto verificable de producción: registra el commit SHA y, opcionalmente, un tag de release, cerrando la trazabilidad CA → TC → task → commit → release. Recolección mecánica determinista (no agente): el SHA lo da git, el gate lo aplica sdd-release.py."
when_to_use: "Activa con frases como 'releasa esta feature', 'marca la release', 'esta feature ya está en producción', 'taggea el cierre de la feature', 'registra el SHA de entrega', 'vincula la feature al tag'. No activa para ejecutar tasks (usa wf-task-run), verificar QA (usa wf-qa-verify) ni para el estado global del proyecto (usa wf-project-status)."
argument-hint: "<feature_dir|tasks_path> [--tag <tag>] [--no-tag] [--note <texto>]"
effort: low
allowed-tools: [Read, Bash, AskUserQuestion]
context: fork
user-invocable: true
---

# wf-release — Noción mínima de release

Marca el cierre de una feature contra producción: registra el **commit SHA** (verdad mecánica de git) y, si se pide, un **tag**. Es el último eslabón de la trazabilidad — la cadena `CA → TC → task → commit → release` (SSoT en `kb-traceability-rules` Regla 11).

No requiere agente: es recolección mecánica sin razonamiento experto, como `wf-project-status`. El gate de cierre (una feature no se releasa sin QA APTO) y la captura del SHA los aplica `sdd-release.py` — el orquestador no teclea SHAs ni decide si la feature está cerrada.

**Es de bajo impacto en el repo**: el registro (`<n>_release.md`) es read-mostly; crear un tag git sí modifica el repo y se hace solo con confirmación explícita.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Feature** (obligatorio): el directorio de la feature (`features/<nombre>/`) o un path de artefacto dentro de ella (`.../<nombre>_tasks.md`, `_qa_report.md`). Si te dan un archivo, usa su directorio de feature (sube desde `tasks/` si aplica).
- **`--tag <tag>`** (opcional): nombre del tag de release a registrar (p. ej. `v1.2.0`).
- **`--no-tag`** (opcional): registra solo el SHA, no ofrezcas crear tag git.
- **`--note <texto>`** (opcional): nota de la entrada de release (p. ej. `hotfix B-003`).

Sin feature → informa el uso:
> "Uso: `/wf-release <feature_dir|tasks_path> [--tag <tag>] [--no-tag] [--note <texto>]`"

## Paso 2: Registrar el release (gate de cierre + SHA mecánico)

Ejecuta desde la raíz del proyecto (el directorio que contiene `.sdd/`):

```bash
python3 .sdd/scripts/sdd-release.py stamp <feature_dir> [--tag <tag>] [--note <texto>] --date <fecha real de tu contexto>
```

El script:
- **Rechaza (exit 2)** si la feature no tiene `_qa_report.md` o su veredicto es `NO_APTO`. En ese caso, NO insistas: comunica el bloqueo y remite a cerrar el ciclo QA con `/wf-qa-verify` (o `/wf-bug` si hay divergencias). Releasar algo que no pasó QA está prohibido.
- Permite `APTO` y `APTO_CON_RESERVAS`; con reservas, el veredicto queda grabado en la entrada (releasar con reservas se documenta, no se oculta).
- Captura el **commit SHA** del HEAD vía `git rev-parse` (no lo tecleas tú). Si la feature no está en repo git, el script rechaza salvo que pases `--sha`.
- Escribe la entrada `R-00X` en `<n>_release.md` (único escritor; las re-releases se acumulan).

Si el script no existe:
> "⚠ Falta `.sdd/scripts/sdd-release.py`. Re-ejecuta la instalación del ecosistema (`install.sh`) para reponer los scripts."

## Paso 3: Crear el tag git (opcional, con confirmación)

Solo si se pasó `--tag` y NO se pasó `--no-tag`:

1. Comprueba si el tag ya existe: `git tag -l <tag>`.
2. Si no existe, pregunta al usuario con `AskUserQuestion` si crear el tag anotado ahora (crear un tag modifica el repo):
   - **Sí** → `git tag -a <tag> -m "Release <feature>: QA APTO en <SHA corto>"` sobre el mismo SHA registrado. Avisa de que el push del tag (`git push --tags`) queda en manos del usuario.
   - **No** → deja el tag solo registrado en `<n>_release.md`; el usuario lo creará/aplicará cuando convenga.
3. Si el tag ya existe, no lo recrees: informa y continúa (el registro ya lo referencia).

Sin `--tag`, no hay tag: el release queda anclado al SHA, que ya es un punto verificable.

## Paso 4: Informar

- Entrada de release creada (`R-00X`), SHA corto, tag (si lo hay) y veredicto QA en que se apoya.
- Path del `<n>_release.md`.
- Recordatorio si el veredicto era `APTO_CON_RESERVAS`: la release lleva reservas conocidas (PARCIAL/MANUAL) — explícito en el registro.
- Siguiente paso: el estado global ya refleja la release —
  > "`/wf-project-status` mostrará esta feature como cerrada con su release. Si hace falta el tag remoto: `git push origin <tag>`."
