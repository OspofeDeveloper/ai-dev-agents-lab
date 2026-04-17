#!/bin/bash
# install.sh — Despliega el ecosistema KMM al .claude del proyecto
# Ejecutar desde el directorio del proyecto KMM destino: bash /path/to/kmm/install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$(pwd)/.claude"

# ── 1. Instalar agentes ────────────────────────────────────────────────────

echo "Instalando agentes..."
mkdir -p "$CLAUDE_DIR/agents"

install_agent() {
  local src="$1"
  local name
  name=$(basename "$src")
  cp "$src" "$CLAUDE_DIR/agents/$name"
  echo "  ✓ agents/$name"
}

install_agent "$SCRIPT_DIR/agents/kmm-feature-implementer.md"
install_agent "$SCRIPT_DIR/agents/kmm-platform-integrator.md"
install_agent "$SCRIPT_DIR/agents/kmm-network-auth-implementer.md"

# ── 2. Instalar skills ─────────────────────────────────────────────────────

echo ""
echo "Instalando skills..."
mkdir -p "$CLAUDE_DIR/skills"

install_skill() {
  local src_dir="${1%/}"
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

for skill_dir in "$SCRIPT_DIR/skills"/*/; do
  install_skill "$skill_dir"
done

# ── 3. Instalar CLAUDE.md ──────────────────────────────────────────────────

echo ""
echo "Instalando CLAUDE.md..."
cp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
echo "  ✓ CLAUDE.md"

# ── 4. Instalar settings.json ──────────────────────────────────────────────

echo ""
echo "Instalando settings.json..."
cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
echo "  ✓ settings.json"

echo ""
echo "Done. Reinicia Claude Code para activar los agentes y skills."
