#!/bin/bash
# install.sh — Distribuye templates y despliega el ecosistema SDD al .claude del proyecto
#
# Uso:
#   bash install.sh                        — instala el ecosistema SDD completo
#   bash install.sh all                    — idem
#   bash install.sh prd                    — solo fase PRD
#   bash install.sh prd,spec               — varias fases separadas por comas
#   bash install.sh prd,spec,design,plan   — combinacion de fases

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_DIR="$SCRIPT_DIR/spec/shared/templates"
CLAUDE_DIR="$(pwd)/.claude"
KMM_DIR="$SCRIPT_DIR/tech/kmm"

RAW_ARG="${1:-all}"

usage() {
  echo "Uso: bash install.sh [all|prd|spec|design|plan|tasks|<fase1,fase2,...>]"
  echo "  all (por defecto): instala el ecosistema SDD completo"
  echo "  prd,spec          : instala PRD y Spec"
  echo "  prd,spec,design   : instala PRD, Spec y Design"
}

# Construir lista de fases a instalar
PHASES=()
if [ "$RAW_ARG" = "all" ]; then
  PHASES=(all)
else
  IFS=',' read -ra PHASES <<< "$RAW_ARG"
  for phase in "${PHASES[@]}"; do
    case "$phase" in
      prd|spec|design|plan|tasks) ;;
      -h|--help|help) usage; exit 0 ;;
      *)
        echo "ERROR: fase no reconocida: '$phase'"
        usage
        exit 1
        ;;
    esac
  done
fi

# Helper: comprueba si una fase está en la lista seleccionada
has_phase() {
  local target="$1"
  for p in "${PHASES[@]}"; do
    [ "$p" = "all" ] && return 0
    [ "$p" = "$target" ] && return 0
  done
  return 1
}

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

if has_phase "spec"; then
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

if has_phase "prd"; then
  install_agent "$SCRIPT_DIR/prd/agents/prd-expert.md"
fi
if has_phase "spec"; then
  install_agent "$SCRIPT_DIR/prd/agents/prd-expert.md" 2>/dev/null || true
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-explorer.md"
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-planner.md"
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-writer.md"
  install_agent "$SCRIPT_DIR/spec/agents/sdd-spec-auditor.md"
fi
if has_phase "design"; then
  install_agent "$SCRIPT_DIR/design/agents/design-architect.md"
fi
if has_phase "plan"; then
  install_agent "$SCRIPT_DIR/plan/agents/plan-architect.md"
  install_agent "$SCRIPT_DIR/plan/agents/plan-auditor.md"
fi
if has_phase "tasks"; then
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
  find "$src_dir" -not -name "README.md" -not -name ".DS_Store" -not -type d | while read -r file; do
    rel="${file#"$src_dir/"}"
    dest="$CLAUDE_DIR/skills/$name/$rel"
    mkdir -p "$(dirname "$dest")"
    cp "$file" "$dest"
  done
  echo "  ✓ skills/$name/"
}

if has_phase "prd"; then
  for skill_dir in "$SCRIPT_DIR/prd/skills"/*/; do
    install_skill "$skill_dir"
  done
fi

if has_phase "spec"; then
  # spec necesita algunas skills de prd como dependencia
  install_skill "$SCRIPT_DIR/prd/skills/kb-prd-expert"
  install_skill "$SCRIPT_DIR/prd/skills/kb-product-change-governance"
  install_skill "$SCRIPT_DIR/prd/skills/wf-prd-change"
  install_skill "$SCRIPT_DIR/prd/skills/wf-prd-review"

  for skill_dir in "$SCRIPT_DIR/spec/skills"/*/; do
    install_skill "$skill_dir"
  done
fi

if has_phase "design"; then
  # design necesita kb-spec-expert como dependencia
  install_skill "$SCRIPT_DIR/spec/skills/kb-spec-expert"

  for skill_dir in "$SCRIPT_DIR/design/skills"/*/; do
    install_skill "$skill_dir"
  done
fi

if has_phase "plan"; then
  # plan necesita kb-spec-expert y kb-a11y-expert como dependencias
  install_skill "$SCRIPT_DIR/spec/skills/kb-spec-expert"
  install_skill "$SCRIPT_DIR/design/skills/kb-a11y-expert"

  for skill_dir in "$SCRIPT_DIR/plan/skills"/*/; do
    install_skill "$skill_dir"
  done
fi

if has_phase "tasks"; then
  # tasks necesita kb-plan-expert como dependencia
  install_skill "$SCRIPT_DIR/plan/skills/kb-plan-expert"

  for skill_dir in "$SCRIPT_DIR/tasks/skills"/*/; do
    install_skill "$skill_dir"
  done
fi

# Las skills tecnicas de stack (tech/<stack>/skills/plan y tasks) NO se instalan
# aqui: las instala el overlay del stack (wf-<stack>-init → tech/<stack>/install.sh),
# que ademas sobreescribe por nombre las piezas genericas con su variante especializada.

# ── 4. Instalar CLAUDE.md ─────────────────────────────────────────────────

echo ""
echo "Instalando CLAUDE.md..."
# Con múltiples fases, instalar el CLAUDE.md del pipeline completo si hay más de una fase,
# o el de la fase concreta si solo se pide una.
PHASE_COUNT="${#PHASES[@]}"
if has_phase "all" || [ "$PHASE_COUNT" -gt 1 ]; then
  cp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
elif has_phase "prd"; then
  cp "$SCRIPT_DIR/prd/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
elif has_phase "spec"; then
  cp "$SCRIPT_DIR/spec/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
elif has_phase "design"; then
  cp "$SCRIPT_DIR/design/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
elif has_phase "plan"; then
  cp "$SCRIPT_DIR/plan/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
elif has_phase "tasks"; then
  cp "$SCRIPT_DIR/tasks/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
fi
echo "  ✓ CLAUDE.md"

# ── 5. Instalar settings.json (merge, sin pisar el del proyecto) ───────────

echo ""
echo "Instalando settings.json..."
if [ ! -f "$CLAUDE_DIR/settings.json" ]; then
  cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
  echo "  ✓ settings.json"
elif command -v python3 >/dev/null 2>&1; then
  python3 "$SCRIPT_DIR/scripts/merge-claude-settings.py" \
    "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
  echo "  ✓ settings.json (merge sobre el existente)"
else
  echo "  ⚠ settings.json existente y python3 no disponible: no se modifica."
  echo "    Revisa manualmente que los hooks de $SCRIPT_DIR/settings.json esten presentes."
fi

echo ""
echo "Done. Reinicia Claude Code para activar los agentes y skills."
