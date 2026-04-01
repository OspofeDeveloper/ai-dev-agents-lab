#!/bin/bash
# install.sh — Distribuye templates y despliega el ecosistema SDD al .claude del proyecto
# Ejecutar desde el directorio sdd/: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_DIR="$SCRIPT_DIR/spec/shared/templates"
CLAUDE_DIR="$(pwd)/.claude"

# ── 1. Distribuir templates compartidos a las skills que los necesitan ─────

echo "Distribuyendo templates compartidos..."

copy_template() {
  local filename="$1"
  local dest_dir="$2"
  local src="$SHARED_DIR/$filename"
  local dst="$dest_dir/$filename"
  if [ ! -f "$src" ]; then
    echo "ERROR: Template no encontrado: $src"
    exit 1
  fi
  mkdir -p "$dest_dir"
  cp "$src" "$dst"
  echo "  ✓ ${dst#"$SCRIPT_DIR/"}"
}

copy_template "project_map_template.md"      "$SCRIPT_DIR/spec/skills/wf-spec-map/references"
copy_template "feature_analysis_template.md" "$SCRIPT_DIR/spec/skills/wf-spec-map-analyze/references"
copy_template "feature_readme_template.md"   "$SCRIPT_DIR/spec/skills/wf-spec-map-generate/references"

# ── 2. Instalar agentes ────────────────────────────────────────────────────

echo ""
echo "Instalando agentes..."
mkdir -p "$CLAUDE_DIR/agents"

install_agent() {
  local src="$1"
  local name
  name=$(basename "$src")
  cp "$src" "$CLAUDE_DIR/agents/$name"
  echo "  ✓ agents/$name"
}

install_agent "$SCRIPT_DIR/spec/agents/sdd-analyst.md"

# ── 3. Instalar skills ─────────────────────────────────────────────────────

echo ""
echo "Instalando skills..."
mkdir -p "$CLAUDE_DIR/skills"

install_skill() {
  local src_dir="$1"
  local name
  name=$(basename "$src_dir")
  rm -rf "$CLAUDE_DIR/skills/$name"
  mkdir -p "$CLAUDE_DIR/skills/$name"
  find "$src_dir" -not -name "README.md" -not -type d | while read -r file; do
    rel="${file#"$src_dir/"}"
    dest="$CLAUDE_DIR/skills/$name/$rel"
    mkdir -p "$(dirname "$dest")"
    cp "$file" "$dest"
  done
  echo "  ✓ skills/$name/"
}

# Instalar todos los skills de spec (estructura plana)
for skill_dir in "$SCRIPT_DIR/spec/skills"/*/; do
  install_skill "$skill_dir"
done

# ── 4. Instalar CLAUDE.md ─────────────────────────────────────────────────

echo ""
echo "Instalando CLAUDE.md..."
cp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
echo "  ✓ CLAUDE.md"

# ── 5. Instalar settings.json ──────────────────────────────────────────────

echo ""
echo "Instalando settings.json..."
cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
echo "  ✓ settings.json"

echo ""
echo "Done. Reinicia Claude Code para activar los agentes y skills."
