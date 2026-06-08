#!/bin/bash
# install.sh — Despliega el ecosistema KMM al .claude del proyecto
# Ejecutar desde el directorio del proyecto KMM destino:
#   bash /path/to/kmm/install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$(pwd)/.claude"
AGENTS_SOURCE_DIR="$SCRIPT_DIR/agents"
SKILLS_SOURCE_DIR="$SCRIPT_DIR/skills"
CLAUDE_SOURCE_FILE="$SCRIPT_DIR/CLAUDE.md"
shopt -s nullglob

# ── 1. Instalar agentes ────────────────────────────────────────────────────

echo "Instalando agentes desde $(basename "$AGENTS_SOURCE_DIR")..."
mkdir -p "$CLAUDE_DIR/agents"

install_agent() {
  local src="$1"
  local name
  name=$(basename "$src")
  cp "$src" "$CLAUDE_DIR/agents/$name"
  echo "  ✓ agents/$name"
}

for agent_file in "$AGENTS_SOURCE_DIR"/*.md; do
  install_agent "$agent_file"
done

# ── 2. Instalar skills ─────────────────────────────────────────────────────

echo ""
echo "Instalando skills desde $(basename "$SKILLS_SOURCE_DIR")..."
mkdir -p "$CLAUDE_DIR/skills"

install_skill() {
  local src_dir="${1%/}"
  local name
  name=$(basename "$src_dir")
  rm -rf "$CLAUDE_DIR/skills/$name"
  mkdir -p "$CLAUDE_DIR/skills/$name"
  find "$src_dir" -type f ! -name ".DS_Store" | while read -r file; do
    rel="${file#"$src_dir/"}"
    dest="$CLAUDE_DIR/skills/$name/$rel"
    mkdir -p "$(dirname "$dest")"
    cp "$file" "$dest"
  done
  echo "  ✓ skills/$name/"
}

for subdir in plan tasks; do
  for skill_dir in "$SKILLS_SOURCE_DIR/$subdir"/*/; do
    install_skill "$skill_dir"
  done
done

# KBs transversales en la raíz de skills/ (p. ej. kb-kmm-project-state-protocol,
# precondición de los agentes KMM)
for skill_dir in "$SKILLS_SOURCE_DIR"/kb-*/; do
  install_skill "$skill_dir"
done

for skill_dir in "$SKILLS_SOURCE_DIR"/wf-*/; do
  install_skill "$skill_dir"
done

# ── 3. Instalar CLAUDE.md del stack como regla de carga perezosa ───────────
# Va a .claude/rules/sdd-kmm.md con frontmatter `paths:`: el harness carga el
# orquestador del stack solo al tocar código Kotlin o artefactos de plan/tasks.
# NO se sobreescribe el CLAUDE.md raíz del proyecto.

echo ""
echo "Instalando regla del stack desde $(basename "$CLAUDE_SOURCE_FILE")..."
mkdir -p "$CLAUDE_DIR/rules"
{
  echo "---"
  echo "paths:"
  echo '  - "**/*.kt"'
  echo '  - "**/*.kts"'
  echo '  - "**/*_plan.md"'
  echo '  - "**/*_tasks.md"'
  echo "---"
  echo ""
  cat "$CLAUDE_SOURCE_FILE"
} > "$CLAUDE_DIR/rules/sdd-kmm.md"
echo "  ✓ rules/sdd-kmm.md"

# ── 4. Instalar settings.json (merge, sin pisar el del proyecto) ───────────

echo ""
echo "Instalando settings.json..."
SDD_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ ! -f "$CLAUDE_DIR/settings.json" ]; then
  cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
  echo "  ✓ settings.json"
elif command -v python3 >/dev/null 2>&1; then
  python3 "$SDD_ROOT/scripts/merge-claude-settings.py" \
    "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
  echo "  ✓ settings.json (merge sobre el existente)"
else
  echo "  ⚠ settings.json existente y python3 no disponible: no se modifica."
  echo "    Revisa manualmente que los hooks de $SCRIPT_DIR/settings.json esten presentes."
fi

# ── 5. Refrescar el sello de versión (el overlay forma parte del ecosistema) ─

ENFORCE_ROOT="${SDD_PROJECT_ROOT:-$(pwd)}"
SDD_VERSION="$(cat "$SDD_ROOT/VERSION" 2>/dev/null | tr -d '[:space:]')"
[ -n "$SDD_VERSION" ] || SDD_VERSION="unknown"
SDD_COMMIT="$(git -C "$SDD_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
mkdir -p "$ENFORCE_ROOT/.sdd"
cat > "$ENFORCE_ROOT/.sdd/sdd-version.json" <<EOF
{
  "version": "$SDD_VERSION",
  "commit": "$SDD_COMMIT",
  "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "installed_by": "tech/kmm/install.sh"
}
EOF
echo "  ✓ .sdd/sdd-version.json (sdd $SDD_VERSION+$SDD_COMMIT)"

# ── 6. Verificar KBs de los agentes del overlay (ROADMAP 1.5) ───────────────
# Los agentes KMM declaran muchas KBs de stack; este check determinista avisa
# si alguna no quedó instalada. No bloquea.

if command -v python3 >/dev/null 2>&1 && [ -f "$ENFORCE_ROOT/.sdd/scripts/sdd-kb-check.py" ]; then
  echo ""
  echo "Verificando KBs de los agentes instalados..."
  if ! python3 "$ENFORCE_ROOT/.sdd/scripts/sdd-kb-check.py" --claude-dir "$CLAUDE_DIR" --all; then
    echo "  ⚠ Algún agente declara KBs no instaladas (ver arriba)."
  fi
fi

echo ""
echo "Done. Reinicia Claude Code para activar los agentes y skills."
