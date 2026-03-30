#!/bin/bash
# install.sh — Distribuye templates y despliega el ecosistema SDD a ~/.claude
# Ejecutar desde el directorio sdd/: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_DIR="$SCRIPT_DIR/spec/shared/templates"
CLAUDE_DIR="$HOME/.claude"

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

copy_template "feature_spec_template.md"   "$SCRIPT_DIR/spec/skills/decompose-spec/spec-decompose/references"
copy_template "feature_readme_template.md" "$SCRIPT_DIR/spec/skills/decompose-spec/spec-decompose/references"
copy_template "feature_spec_template.md"   "$SCRIPT_DIR/spec/skills/prepare-spec/spec-fast-track/references"
copy_template "feature_readme_template.md" "$SCRIPT_DIR/spec/skills/prepare-spec/spec-fast-track/references"

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
install_agent "$SCRIPT_DIR/plan/agents/plan-architect.md"
install_agent "$SCRIPT_DIR/tasks/agents/task-generator.md"

# ── 3. Instalar skills ─────────────────────────────────────────────────────

echo ""
echo "Instalando skills..."
mkdir -p "$CLAUDE_DIR/skills"

install_skill() {
  local src_dir="$1"
  local name
  name=$(basename "$src_dir")
  rm -rf "$CLAUDE_DIR/skills/$name"
  cp -r "$src_dir" "$CLAUDE_DIR/skills/$name"
  echo "  ✓ skills/$name/"
}

# Core knowledge — se aplana desde spec/skills/core/ (cada subdirectorio es un skill independiente)
install_skill "$SCRIPT_DIR/spec/skills/core/spec-expert"
install_skill "$SCRIPT_DIR/spec/skills/core/gap-conventions"
install_skill "$SCRIPT_DIR/spec/skills/core/decompose-expert"
install_skill "$SCRIPT_DIR/spec/skills/core/conflict-expert"

# Orquestadores spec
install_skill "$SCRIPT_DIR/spec/skills/prepare-spec"
install_skill "$SCRIPT_DIR/spec/skills/decompose-spec"
install_skill "$SCRIPT_DIR/spec/skills/prepare-delta"
install_skill "$SCRIPT_DIR/spec/skills/check-conflicts"

# Plan
install_skill "$SCRIPT_DIR/plan/skills/plan-expert"
install_skill "$SCRIPT_DIR/plan/skills/prepare-plan"

# Tasks
install_skill "$SCRIPT_DIR/tasks/skills/tasks-expert"
install_skill "$SCRIPT_DIR/tasks/skills/prepare-tasks"

echo ""
echo "Done. Reinicia Claude Code para activar los agentes y skills."
