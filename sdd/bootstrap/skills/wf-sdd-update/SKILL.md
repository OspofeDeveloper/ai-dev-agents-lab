---
name: wf-sdd-update
description: "Actualiza la instalación SDD de un proyecto a la versión actual del ecosistema, sin re-entrevistar: relee fases y stack de project-init.json, reinstala con --prune, re-aplica el overlay DESPUÉS de la base y muestra los avisos de cambios que rompen del CHANGELOG."
when_to_use: "Activa con frases como 'actualiza el sdd del proyecto', 'sdd update', 'trae la última versión del ecosistema', 'el hook avisa de version-drift', 'sincroniza las skills con el ecosistema'. No activa para inicializar un proyecto nuevo (usa wf-project-init) ni para ampliar fases (usa wf-project-init → Completar / ampliar)."
argument-hint: "[--force]"
effort: low
allowed-tools: [Read, Write, Edit, Bash]
context: fork
---

# wf-sdd-update — Update no destructivo de la instalación SDD

Tu rol: reinstalar mecánicamente lo que el proyecto YA declaró, a la versión actual del ecosistema. **No re-entrevistas** (eso es de `wf-project-init`), no decides fases nuevas, no tocas artefactos (`specs`, `plans`, `tasks` — solo infraestructura: skills, agentes, rules, scripts, settings).

---

## Paso 1: Localizar proyecto y ecosistema

1. **Raíz del proyecto**: el directorio (actual o ancestro) que contiene `.sdd/project-init.json`. Si no existe:
   - pero hay `.claude/rules/sdd-*.md` o `.sdd/sdd-version.json` → instalación standalone sin init: deriva las fases de los archivos `rules/sdd-<fase>.md` presentes y continúa (avísalo en el reporte).
   - y tampoco hay rastro SDD → detén: "Este proyecto no tiene instalación SDD. Para inicializar: `/wf-project-init`."
2. **SDD_HOME**: léelo de `~/.sdd-home`. Verifica que `$SDD_HOME/install.sh` y `$SDD_HOME/VERSION` existen. Si no → detén e indica re-clonar el ecosistema o re-ejecutar `setup.sh`.

## Paso 2: Comparar versiones

```bash
!cat ~/.sdd-home && SDD_HOME=$(cat ~/.sdd-home) && cat "$SDD_HOME/VERSION" && git -C "$SDD_HOME" rev-parse --short HEAD
!cat .sdd/sdd-version.json 2>/dev/null || echo "SIN_SELLO"
```

- Proyecto sin sello (`SIN_SELLO` y sin `sdd_version` en `project-init.json`) → instalación pre-versionado: continúa (el update lo sellará por primera vez).
- **Misma versión y mismo commit** → informa "ya está al día (X+sha)" y detén, salvo `--force` (reinstalación íntegra del mismo estado, útil tras una copia corrupta).

## Paso 3: Plan de actualización y avisos de rotura

1. Lee de `project-init.json`: `phases`, `stack`, `artifacts`.
2. Lee `$SDD_HOME/CHANGELOG.md` y extrae las entradas posteriores a la versión instalada. Las líneas `⚠` son cambios que afectan a proyectos ya inicializados.
3. Presenta el plan ANTES de ejecutar:
   - versión instalada → versión nueva (con commits)
   - fases que se reinstalarán + overlay de stack si aplica
   - avisos `⚠` del changelog (p. ej. "los specs con [INFERIDO] ahora bloquean el plan: planes antes sellables pueden dejar de serlo")
   - recuerda que `--prune` eliminará piezas SDD huérfanas de fases no declaradas
4. Espera confirmación del usuario.

## Paso 4: Ejecutar (orden crítico: base primero, overlay después)

Desde la raíz del proyecto:

```bash
!SDD_HOME=$(cat ~/.sdd-home) && SDD_PROJECT_ROOT="$(pwd)" bash "$SDD_HOME/install.sh" <fase1,fase2,...> --prune
```

Si `stack` es concreto (ni `agnostico` ni null) y existe `$SDD_HOME/tech/<stack>/install.sh`:

```bash
!SDD_HOME=$(cat ~/.sdd-home) && SDD_PROJECT_ROOT="$(pwd)" bash "$SDD_HOME/tech/<stack>/install.sh"
```

**El overlay SIEMPRE después de la base**: la base reinstala las piezas genéricas y el overlay vuelve a aplicar sus sustituciones por basename (agentes y kbs especializados con el mismo nombre). Invertir el orden deja el proyecto en genérico aunque declare stack.

No re-ejecutes `wf-<stack>-init` (el `<stack>_project_state.md` del proyecto es estado del PROYECTO, no del ecosistema — no se toca).

## Paso 5: Sellar versión en project-init.json

Si existe `project-init.json`, sincroniza su campo `sdd_version` con el sello nuevo:

```bash
!python3 - <<'EOF'
import json
from pathlib import Path
stamp = json.loads(Path(".sdd/sdd-version.json").read_text())
p = Path(".sdd/project-init.json")
data = json.loads(p.read_text())
data["sdd_version"] = f"{stamp['version']}+{stamp['commit']}"
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("sdd_version =", data["sdd_version"])
EOF
```

## Paso 5b: Asegurar `.gitignore`

Asegura que el `.gitignore` del proyecto contiene la línea `.claude/settings.local.json` — añádela si falta (crea el archivo si no existe; nunca toques el resto del contenido). Es la única pieza SDD que no se commitea; los proyectos inicializados antes de la 0.5.0 no la tienen.

## Paso 6: Verificar y reportar

1. Checks mecánicos:
   ```bash
   !cat .sdd/sdd-version.json && head -2 .sdd/scripts/sdd-seal.py | tail -1
   !for f in $(python3 -c "import json;print(' '.join(json.load(open('.sdd/project-init.json'))['phases']))" 2>/dev/null); do test -f ".claude/rules/sdd-$f.md" && echo "OK rule sdd-$f" || echo "FALTA rule sdd-$f"; done
   ```
2. Reporta: versión vieja → nueva, fases reinstaladas, overlay re-aplicado (sí/no), avisos `⚠` aplicables, y piezas eliminadas por `--prune` si las hubo.
3. Recuerda: reiniciar Claude Code para recargar skills/agents, y commitear los cambios de `.claude/` y `.sdd/` (la política de git del proyecto los versiona; la única excepción es `settings.local.json`).
