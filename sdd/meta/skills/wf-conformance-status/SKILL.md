---
name: wf-conformance-status
description: "Genera un snapshot de cobertura de la bateria de conformance leyendo la matriz del ROADMAP: conteo por Estado, ejes en hueco (happy/edge/harness/args) y progreso X/N por fase y global. No escribe escenarios ni el ROADMAP; solo lee y agrega. Espejo mecanico de wf-sdd-status."
when_to_use: "Activa con frases como 'que cobertura de conformance tenemos', 'cuanto falta para 48/48', 'que skills tienen huecos en los ejes', 'estado de la bateria de conformance', 'progreso del ROADMAP de conformance'. No activa para escribir o completar escenarios (usa wf-conformance-author) ni para inventariar skills/agentes del ecosistema (usa wf-sdd-status)."
argument-hint: "[--phase <prd|spec|design|plan|tasks|meta|bootstrap>] [--output <path>]"
effort: low
allowed-tools: [Read, Write, Bash]
context: fork
user-invocable: true
---

# wf-conformance-status — Cobertura de la batería de conformance

Genera un snapshot de cobertura de la batería de conformance. No requiere agente: es recolección y conteo determinista sobre la matriz del ROADMAP, sin razonamiento experto.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **`--phase`**: fase a inspeccionar (`prd`, `spec`, `design`, `plan`, `tasks`, `meta`, `bootstrap`). Si se omite, cobertura global.
- **`--output`**: path del archivo de salida (opcional; si no se especifica, solo muestra en pantalla).

---

## Paso 2: Calcular la cobertura (núcleo determinista)

Ejecuta el script que parsea la matriz de `conformance/ROADMAP.md` y agrega la cobertura:

```bash
python3 sdd/scripts/sdd-conformance-coverage.py
```

Con filtro de fase: `python3 sdd/scripts/sdd-conformance-coverage.py --phase <fase>`.
Para consumo programático: añade `--json`.

(Si el repo se invoca desde otra raíz, ajusta a `scripts/sdd-conformance-coverage.py`.)

El script es la **SSoT de la agregación**: parsea la matriz (una fila por `wf-*`, respetando los pipes escapados de la columna Args), cuenta por Estado, detecta ejes `🟡`/`❌` y calcula el progreso `X/N`. No edites el ROADMAP a mano para "cuadrar" el contador: la matriz es la fuente, el script solo la lee.

**Fallback sin python3:** si `python3` no está disponible o el script falla, no bloquees. Deriva el snapshot leyendo `conformance/ROADMAP.md` directamente: cuenta las filas por Estado y el bloque **Progreso**, y avisa con `⚠ No se pudo ejecutar el script; conteo leído del ROADMAP`.

---

## Paso 3: Construir el snapshot

A partir de la salida del script, estructura el snapshot:

- **Por fase**: skills contadas vs declaradas (señala la deriva `⚠` si no cuadran), y el desglose de Estados.
- **Ejes en hueco**: cuántos `🟡`/`❌` por eje (Happy/Edge/Harness/Args OK) y la lista de skills con su anotación de *Huecos detectados*.
- **Progreso**: el contador `Revisadas: X / N · Completadas · Revisadas sin huecos · Con huecos · Pendientes`.

Incluye en la cabecera la versión del ecosistema: `cat sdd/VERSION` + `git -C sdd rev-parse --short HEAD`.

---

## Paso 4: Output

Si se especificó `--output`:
- Escribe el snapshot en el path indicado.
- Informa: `"Snapshot de cobertura guardado en <path>."`

Si no se especificó `--output`:
- Muestra el snapshot directamente al usuario.

Sugiere al final:
- Si hay skills con ejes `🟡`/`❌` que merezcan escenarios: `"Cierra los huecos con /wf-conformance-author <skill>."`
- Si la deriva por fase muestra `declaradas ≠ contadas`: `"La matriz del ROADMAP no cuadra con su cabecera de fase; revísala antes de seguir."`
- Si todo está `COMPLETADO`/`REVISADO`: `"Cobertura cerrada (X/N). Lo que queda es ejecutar los escenarios sobre proyectos reales y reportar desviaciones (ver conformance/README.md)."`
