#!/bin/bash
# Setup global del ecosistema SDD. Instala en la maquina del usuario:
#   1. wf-project-init en ~/.claude/skills/            (skill global de init)
#   2. ~/.sdd-home                                      (ruta al framework SDD)
#   3. Hook SessionStart en ~/.claude/hooks/            (chequeo determinista de estado SDD)
#   4. Registro del hook en ~/.claude/settings.json     (merge, sin pisar otros hooks)
#   5. Bloque gestionado SDD-BOOTSTRAP en ~/.claude/CLAUDE.md (protocolo de inicio de sesion)
#
# Uso:
#   bash setup.sh           — instala (o reinstala) el bootstrap global
#   bash setup.sh --update  — alias de lo anterior, util tras git pull
#   bash setup.sh --dev     — ademas, materializa el meta-orquestador (sdd/meta/)
#                             como symlinks en sdd/.claude/ para desarrollar el ecosistema
set -e

DEV_MODE=0
case "${1:-}" in
  ""|-u|--update) ;;
  --dev) DEV_MODE=1 ;;
  -h|--help) echo "Uso: bash setup.sh [--update|--dev]"; exit 0 ;;
  *) echo "Argumento desconocido: '$1'"; echo "Uso: bash setup.sh [--update|--dev]"; exit 1 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
GLOBAL_SKILLS_DIR="$CLAUDE_DIR/skills"
TARGET="$GLOBAL_SKILLS_DIR/wf-project-init"
SOURCE="$SCRIPT_DIR/bootstrap/skills/wf-project-init"

if [ ! -d "$SOURCE" ]; then
  echo "Error: no se encuentra $SOURCE"
  echo "Asegurate de ejecutar este script desde el directorio raiz del ecosistema SDD."
  exit 1
fi

# Precondicion: python3 es necesario para el merge de ~/.claude/settings.json
# (paso 4). Se verifica ANTES de tocar nada para no dejar el bootstrap a medias
# (hook copiado pero sin registrar).
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 no esta disponible y setup.sh lo necesita para registrar"
  echo "el hook en ~/.claude/settings.json sin pisar tu configuracion existente."
  echo "Instalalo y reintenta:"
  echo "  macOS : xcode-select --install   (o: brew install python3)"
  echo "  Linux : sudo apt install python3 (o equivalente de tu distro)"
  echo "No se ha modificado nada."
  exit 1
fi

# ── 1. Skills globales de bootstrap (wf-project-init, wf-sdd-update) ────────
mkdir -p "$GLOBAL_SKILLS_DIR"
rm -rf "$TARGET"
cp -r "$SOURCE" "$TARGET"
rm -rf "$GLOBAL_SKILLS_DIR/wf-sdd-update"
cp -r "$SCRIPT_DIR/bootstrap/skills/wf-sdd-update" "$GLOBAL_SKILLS_DIR/wf-sdd-update"

# ── 2. SDD_HOME en ~/.sdd-home ──────────────────────────────────────────────
echo "$SCRIPT_DIR" > "$HOME/.sdd-home"

# ── 3. Hook SessionStart ────────────────────────────────────────────────────
HOOKS_DIR="$CLAUDE_DIR/hooks"
HOOK_TARGET="$HOOKS_DIR/sdd-session-check.sh"
mkdir -p "$HOOKS_DIR"
cp "$SCRIPT_DIR/bootstrap/sdd-session-check.sh" "$HOOK_TARGET"
chmod +x "$HOOK_TARGET"

# ── 4. Registrar el hook en ~/.claude/settings.json (merge idempotente) ─────
SETTINGS="$CLAUDE_DIR/settings.json" python3 - <<'PYEOF'
import json, os

path = os.environ["SETTINGS"]
data = {}
if os.path.exists(path):
    with open(path) as f:
        data = json.load(f)

hook_cmd = os.path.expanduser("~/.claude/hooks/sdd-session-check.sh")
session_start = data.setdefault("hooks", {}).setdefault("SessionStart", [])

already = any(
    h.get("command", "").endswith("sdd-session-check.sh")
    for matcher in session_start
    for h in matcher.get("hooks", [])
)
if not already:
    session_start.append({"hooks": [{"type": "command", "command": hook_cmd}]})
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print("Hook SessionStart registrado en " + path)
else:
    print("Hook SessionStart ya registrado en " + path)
PYEOF

# ── 5. Bloque gestionado en ~/.claude/CLAUDE.md ─────────────────────────────
GLOBAL_MD="$CLAUDE_DIR/CLAUDE.md"
BLOCK_SRC="$SCRIPT_DIR/bootstrap/claude-global-block.md"
BLOCK_START="<!-- >>> SDD-BOOTSTRAP >>>"
BLOCK_END="<!-- <<< SDD-BOOTSTRAP <<<"

if [ -f "$GLOBAL_MD" ]; then
  # Eliminar el bloque gestionado previo (si existe) preservando el resto
  awk -v s="$BLOCK_START" -v e="$BLOCK_END" '
    index($0, s) == 1 { skip = 1 }
    !skip { print }
    index($0, e) == 1 { skip = 0 }
  ' "$GLOBAL_MD" > "$GLOBAL_MD.tmp"
  mv "$GLOBAL_MD.tmp" "$GLOBAL_MD"
  # Asegurar separacion con el contenido previo del usuario
  [ -s "$GLOBAL_MD" ] && [ -n "$(tail -c 1 "$GLOBAL_MD")" ] && echo "" >> "$GLOBAL_MD"
fi
cat "$BLOCK_SRC" >> "$GLOBAL_MD"

# ── 6. (--dev) Meta-orquestador como symlinks en sdd/.claude/ ───────────────
# El repo gitignora sdd/.claude/; la fuente versionada vive en sdd/meta/.
# Los symlinks hacen que las skills y agentes meta esten activos al trabajar
# en el repo, y que editar via .claude/ modifique directamente la fuente.
if [ "$DEV_MODE" = "1" ]; then
  REPO_CLAUDE="$SCRIPT_DIR/.claude"
  mkdir -p "$REPO_CLAUDE/skills" "$REPO_CLAUDE/agents"
  ln -sfn "$SCRIPT_DIR/meta/CLAUDE.md" "$REPO_CLAUDE/CLAUDE.md"
  for agent in "$SCRIPT_DIR"/meta/agents/*.md; do
    ln -sfn "$agent" "$REPO_CLAUDE/agents/$(basename "$agent")"
  done
  for skill in "$SCRIPT_DIR"/meta/skills/*/; do
    skill="${skill%/}"
    ln -sfn "$skill" "$REPO_CLAUDE/skills/$(basename "$skill")"
  done
  # skills de bootstrap tambien activas en el repo para probarlas sin instalar global
  ln -sfn "$SCRIPT_DIR/bootstrap/skills/wf-project-init" "$REPO_CLAUDE/skills/wf-project-init"
  ln -sfn "$SCRIPT_DIR/bootstrap/skills/wf-sdd-update" "$REPO_CLAUDE/skills/wf-sdd-update"
  echo "Modo dev: meta-orquestador symlinkeado en $REPO_CLAUDE"
fi

# ── Resumen ─────────────────────────────────────────────────────────────────
echo ""
echo "SDD bootstrap completado."
echo "  wf-project-init     → $TARGET"
echo "  wf-sdd-update       → $GLOBAL_SKILLS_DIR/wf-sdd-update"
echo "  SDD_HOME            → $HOME/.sdd-home ($SCRIPT_DIR)"
echo "  Hook SessionStart   → $HOOK_TARGET"
echo "  Protocolo global    → bloque SDD-BOOTSTRAP en $GLOBAL_MD"
echo ""
echo "A partir de ahora, al iniciar sesion de Claude en cualquier proyecto:"
echo "  - sin estado SDD     → wizard de modo (SDD / libre)"
echo "  - modo sdd sin init  → se lanza /wf-project-init automaticamente"
echo "  - modo libre o init completado → sesion normal, sin preguntas"
echo ""
echo "Para actualizar tras un git pull: bash setup.sh --update"
