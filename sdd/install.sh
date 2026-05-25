#!/bin/bash
# install.sh — Distribuye templates y despliega el ecosistema SDD al .claude del proyecto
# Ejecutar desde el directorio sdd/: bash install.sh [all|prd|spec|design]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_DIR="$SCRIPT_DIR/spec/shared/templates"
CLAUDE_DIR="$(pwd)/.claude"
INSTALL_TARGET="${1:-all}"

usage() {
  echo "Uso: bash install.sh [all|prd|spec|design]"
  echo "  all (por defecto): instala el ecosistema SDD completo"
  echo "  prd: instala solo agentes, skills y CLAUDE.md relacionados con PRD"
  echo "  spec: instala solo agentes, skills y CLAUDE.md relacionados con Spec"
  echo "  design: instala solo agentes, skills y CLAUDE.md relacionados con Design"
}

case "$INSTALL_TARGET" in
  all|prd|spec|design)
    ;;
  -h|--help|help)
    usage
    exit 0
    ;;
  *)
    echo "ERROR: argumento no soportado: $INSTALL_TARGET"
    usage
    exit 1
    ;;
esac

# ── 1. Distribuir templates compartidos a las skills que los necesitan ─────

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

if [ "$INSTALL_TARGET" = "all" ]; then
  echo "Distribuyendo templates compartidos..."
  copy_template "feature_spec_template.md"   "$SCRIPT_DIR/spec/skills/wf-spec-fast-track/references"
  copy_template "feature_readme_template.md" "$SCRIPT_DIR/spec/skills/wf-spec-fast-track/references"
fi

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

if [ "$INSTALL_TARGET" = "prd" ]; then
  install_agent "$SCRIPT_DIR/prd/agents/prd-expert.md"
elif [ "$INSTALL_TARGET" = "spec" ]; then
  install_agent "$SCRIPT_DIR/prd/agents/prd-expert.md"
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-explorer.md"
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-planner.md"
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-writer.md"
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-auditor.md"
elif [ "$INSTALL_TARGET" = "design" ]; then
  install_agent "$SCRIPT_DIR/design/agents/design-architect.md"
else
  install_agent "$SCRIPT_DIR/prd/agents/prd-expert.md"
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-explorer.md"
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-planner.md"
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-writer.md"
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-auditor.md"
  install_agent "$SCRIPT_DIR/design/agents/design-architect.md"
  install_agent "$SCRIPT_DIR/plan/agents/plan-architect.md"
  install_agent "$SCRIPT_DIR/tasks/agents/task-generator.md"
fi

# ── 3. Instalar skills ─────────────────────────────────────────────────────

echo ""
echo "Instalando skills..."
mkdir -p "$CLAUDE_DIR/skills"

install_skill() {
  local src_dir="${1%/}"
  local name
  name=$(basename "$src_dir")
  if [ ! -f "$src_dir/SKILL.md" ]; then
    return 0
  fi
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

if [ "$INSTALL_TARGET" = "prd" ]; then
  for skill_dir in "$SCRIPT_DIR/prd/skills"/*/; do
    install_skill "$skill_dir"
  done
elif [ "$INSTALL_TARGET" = "spec" ]; then
  install_skill "$SCRIPT_DIR/prd/skills/kb-prd-expert"
  install_skill "$SCRIPT_DIR/prd/skills/kb-product-change-governance"
  install_skill "$SCRIPT_DIR/prd/skills/wf-prd-change"
  install_skill "$SCRIPT_DIR/prd/skills/wf-prd-review"

  for skill_dir in "$SCRIPT_DIR/spec/skills"/*/; do
    install_skill "$skill_dir"
  done
elif [ "$INSTALL_TARGET" = "design" ]; then
  install_skill "$SCRIPT_DIR/spec/skills/kb-spec-expert"

  for skill_dir in "$SCRIPT_DIR/design/skills"/*/; do
    install_skill "$skill_dir"
  done
else
  for skill_dir in "$SCRIPT_DIR/prd/skills"/*/; do
    install_skill "$skill_dir"
  done

  for skill_dir in "$SCRIPT_DIR/spec/skills"/*/; do
    install_skill "$skill_dir"
  done

  for skill_dir in "$SCRIPT_DIR/design/skills"/*/; do
    install_skill "$skill_dir"
  done

  for skill_dir in "$SCRIPT_DIR/plan/skills"/*/; do
    install_skill "$skill_dir"
  done

  for skill_dir in "$SCRIPT_DIR/tasks/skills"/*/; do
    install_skill "$skill_dir"
  done
fi

# ── 4. Instalar CLAUDE.md ─────────────────────────────────────────────────

echo ""
echo "Instalando CLAUDE.md..."
if [ "$INSTALL_TARGET" = "prd" ]; then
  cp "$SCRIPT_DIR/prd/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
elif [ "$INSTALL_TARGET" = "spec" ]; then
  cp "$SCRIPT_DIR/spec/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
elif [ "$INSTALL_TARGET" = "design" ]; then
  cp "$SCRIPT_DIR/design/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
else
  cp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
fi
echo "  ✓ CLAUDE.md"

# ── 5. Instalar settings.json ──────────────────────────────────────────────

echo ""
echo "Instalando settings.json..."
cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
echo "  ✓ settings.json"

echo ""
echo "Done. Reinicia Claude Code para activar los agentes y skills."
