---
name: wf-project-status
description: "Informe PM read-only del estado del proyecto SDD: por cada feature, en qué fase del pipeline está (Spec/Plan/Tasks/QA/Cerrada), su estado, el bloqueo y la siguiente acción concreta. Recolección mecánica determinista (no agente): agrega el estado ya sellado en los artefactos, no razona ni edita nada."
when_to_use: "Activa con frases como 'estado del proyecto', 'cómo va el proyecto', 'qué features faltan', 'qué está bloqueado', 'informe de estado', 'dónde está cada feature', 'siguiente paso de cada feature', 'resumen para PM', 'qué puedo planificar/implementar ahora'. No activa para inventariar el ecosistema SDD (usa wf-sdd-status) ni para readiness funcional de specs (usa wf-spec-readiness)."
argument-hint: "[<raíz_artefactos_spec>] [--output <path>]"
effort: low
allowed-tools: [Read, Bash]
context: fork
---

# wf-project-status — Informe PM read-only del proyecto

Genera una vista de delivery del proyecto: en qué punto está cada feature y qué falta para avanzarla. No requiere agente — es recolección mecánica sin razonamiento experto, igual que `wf-sdd-status` lo es para el ecosistema. **Es read-only: no edita ningún artefacto.**

El estado real ya vive sellado en los artefactos (`Estado:` del plan lo escribe `sdd-seal.py`, la tabla `## Progreso` la regenera `sdd-task-state.py`, el veredicto QA lo escribe `wf-qa-verify`, el índice `_features.md` lo genera `sdd-features-index.py`). Este workflow solo los **agrega**; por eso lo hace un script determinista y no un agente.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Raíz de artefactos spec** (opcional): el directorio que contiene `features/` y `_features.md`. Si no se pasa, resuélvelo por la regla de layout: si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.spec`, usa ese directorio; si no, usa el directorio actual.
- **`--output <path>`** (opcional): además de mostrarlo, escribe el informe en ese archivo.

---

## Paso 2: Ejecutar el agregador

Ejecuta desde la raíz del proyecto (el directorio que contiene `.sdd/`):

```
python3 .sdd/scripts/sdd-project-status.py <raíz_artefactos_spec> [--output <path>]
```

Si el script no existe:
> "⚠ Falta `.sdd/scripts/sdd-project-status.py`. Re-ejecuta la instalación del ecosistema (`install.sh`) para reponer los scripts."

Si no hay `features/` ni `_features.md` en la raíz indicada, el informe sale vacío: informa al usuario de que aún no hay features generadas y remite a `/wf-spec-features-first`.

---

## Paso 3: Presentar al usuario

Muestra el informe tal cual lo emite el script (tabla por feature + resumen + "Siguiente foco"). No lo reescribas ni lo interpretes: es la SSoT de estado agregada. Puedes añadir una frase corta señalando el cuello de botella más evidente (p. ej. "3 features esperan validación de plan") y, si el usuario lo pide, profundizar en una feature concreta leyendo sus artefactos.

La columna **Siguiente acción** ya da el comando exacto por feature: úsalo para encadenar el siguiente paso del pipeline si el usuario quiere avanzar una feature concreta.
