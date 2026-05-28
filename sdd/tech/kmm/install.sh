#!/bin/bash
# install.sh — Despliega el ecosistema KMM al .claude del proyecto
# Ejecutar desde el directorio del proyecto KMM destino:
#   bash /path/to/kmm/install.sh [normal|optimized]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$(pwd)/.claude"
SKILL_VARIANT="${1:-normal}"
AGENTS_SOURCE_DIR="$SCRIPT_DIR/agents"
SKILLS_SOURCE_DIR="$SCRIPT_DIR/skills"
CLAUDE_SOURCE_FILE="$SCRIPT_DIR/CLAUDE.md"
shopt -s nullglob

case "$SKILL_VARIANT" in
  normal)
    ;;
  optimized)
    AGENTS_SOURCE_DIR="$SCRIPT_DIR/agents_optimized"
    SKILLS_SOURCE_DIR="$SCRIPT_DIR/skills_optimized"
    CLAUDE_SOURCE_FILE="$SCRIPT_DIR/CLAUDE_optimized.md"
    ;;
  *)
    echo "Uso: bash /path/to/kmm/install.sh [normal|optimized]"
    exit 1
    ;;
esac

# ── 1. Instalar agentes ────────────────────────────────────────────────────

echo "Instalando agentes..."
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

for skill_dir in "$SKILLS_SOURCE_DIR"/wf-*/; do
  install_skill "$skill_dir"
done

# ── 3. Instalar CLAUDE.md ──────────────────────────────────────────────────

echo ""
echo "Instalando CLAUDE.md desde $(basename "$CLAUDE_SOURCE_FILE")..."
cp "$CLAUDE_SOURCE_FILE" "$CLAUDE_DIR/CLAUDE.md"
echo "  ✓ CLAUDE.md"

# ── 4. Instalar settings.json ──────────────────────────────────────────────

echo ""
echo "Instalando settings.json..."
cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
echo "  ✓ settings.json"

echo ""
echo "Done. Reinicia Claude Code para activar los agentes y skills."
