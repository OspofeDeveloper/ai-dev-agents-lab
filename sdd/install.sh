#!/bin/bash
# install.sh — Distribuye templates y despliega el ecosistema SDD al .claude del proyecto
#
# Uso:
#   bash install.sh                        — instala el ecosistema SDD completo
#   bash install.sh all                    — idem
#   bash install.sh prd                    — solo fase PRD
#   bash install.sh prd,spec               — varias fases separadas por comas
#   bash install.sh prd,spec,design,plan   — combinacion de fases
#   bash install.sh prd,spec --prune       — ademas, elimina skills/agents SDD
#                                            de fases NO seleccionadas que queden
#                                            en .claude/ de un install anterior

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_DIR="$SCRIPT_DIR/spec/shared/templates"
CLAUDE_DIR="$(pwd)/.claude"
KMM_DIR="$SCRIPT_DIR/tech/kmm"

usage() {
  echo "Uso: bash install.sh [all|prd|spec|design|plan|tasks|<fase1,fase2,...>] [--prune]"
  echo "  all (por defecto): instala el ecosistema SDD completo"
  echo "  prd,spec          : instala PRD y Spec"
  echo "  prd,spec,design   : instala PRD, Spec y Design"
  echo "  --prune           : elimina del .claude/ las skills/agents SDD de fases no seleccionadas"
}

RAW_ARG="all"
PRUNE=0
for arg in "$@"; do
  case "$arg" in
    --prune) PRUNE=1 ;;
    -h|--help|help) usage; exit 0 ;;
    *) RAW_ARG="$arg" ;;
  esac
done

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
  local p
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

# Registro de lo instalado en este run (para la reconciliacion final)
INSTALLED_AGENTS=""
INSTALLED_SKILLS=""

install_agent() {
  local src="$1"
  local name
  name=$(basename "$src")
  cp "$src" "$CLAUDE_DIR/agents/$name"
  INSTALLED_AGENTS="$INSTALLED_AGENTS $name"
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
  install_agent "$SCRIPT_DIR/tasks/agents/qa-engineer.md"
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
  INSTALLED_SKILLS="$INSTALLED_SKILLS $name"
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
  # tasks necesita kb-plan-expert y kb-spec-expert (qa-engineer) como dependencias
  install_skill "$SCRIPT_DIR/plan/skills/kb-plan-expert"
  install_skill "$SCRIPT_DIR/spec/skills/kb-spec-expert"

  for skill_dir in "$SCRIPT_DIR/tasks/skills"/*/; do
    install_skill "$skill_dir"
  done
fi

# Las skills tecnicas de stack (tech/<stack>/skills/plan y tasks) NO se instalan
# aqui: las instala el overlay del stack (wf-<stack>-init → tech/<stack>/install.sh),
# que ademas sobreescribe por nombre las piezas genericas con su variante especializada.

# ── 4. Instalar CLAUDE.md raíz y reglas de fase ────────────────────────────

echo ""
echo "Instalando CLAUDE.md y reglas de fase..."

# Reglas de fase con carga perezosa NATIVA por path (.claude/rules/ con
# frontmatter `paths:`): el harness carga las instrucciones de la fase solo
# cuando se tocan ficheros que matchean los globs — sin depender de que el
# modelo obedezca prosa. Los globs por defecto combinan el directorio canónico
# de la fase con patrones por nombre de artefacto (independientes del layout);
# wf-project-init añade el directorio real del mapa `artifacts` del proyecto.
mkdir -p "$CLAUDE_DIR/rules"

phase_globs() {
  case "$1" in
    prd)    printf '%s\n' "prd/**" "**/prd*.md" "**/*_analysis.md" "**/*_discovery.md" ;;
    spec)   printf '%s\n' "spec/**" "**/features/*/spec/**" "**/*_spec.md" "**/*_features.md" ;;
    design) printf '%s\n' "design/**" "**/features/*/design/**" "**/DESIGN*.md" "**/*_flows.md" "**/*_views.md" "**/*_ui_prompt.md" ;;
    plan)   printf '%s\n' "**/*_plan.md" ;;
    tasks)  printf '%s\n' "**/*_tasks.md" "**/*_bugs.md" "**/*_qa_plan.md" "**/*_qa_report.md" ;;
  esac
}

install_phase_rule() {
  local p="$1"
  {
    echo "---"
    echo "paths:"
    phase_globs "$p" | while read -r g; do echo "  - \"$g\""; done
    echo "---"
    echo ""
    cat "$SCRIPT_DIR/$p/CLAUDE.md"
  } > "$CLAUDE_DIR/rules/sdd-$p.md"
  echo "  ✓ rules/sdd-$p.md"
}

for p in prd spec design plan tasks; do
  if has_phase "$p"; then
    install_phase_rule "$p"
  fi
done

# CLAUDE.md raíz: pipeline completo si hay varias fases, el de la fase si es una.
# En el flujo wf-project-init este archivo se regenera después (Paso 7) con la
# plantilla del proyecto, que siempre lo sobreescribe.
PHASE_COUNT="${#PHASES[@]}"
if has_phase "all" || [ "$PHASE_COUNT" -gt 1 ]; then
  cp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
else
  for p in prd spec design plan tasks; do
    if has_phase "$p"; then
      cp "$SCRIPT_DIR/$p/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    fi
  done
fi
echo "  ✓ CLAUDE.md"

# ── 4b. Instalar scripts de enforcement en .sdd/scripts/ ───────────────────
# Van a .sdd/ (no a .claude/) porque son parte del proyecto: committeables y
# ejecutables en CI sin depender de ~/.sdd-home de cada dev.
# SDD_PROJECT_ROOT permite a wf-project-init (que instala cada fase con cwd en
# su subdirectorio) dirigirlos a la raíz real del proyecto.

ENFORCE_ROOT="${SDD_PROJECT_ROOT:-$(pwd)}"

# Versión del ecosistema: VERSION (SSoT) + commit como respaldo de precisión.
SDD_VERSION="$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null | tr -d '[:space:]')"
[ -n "$SDD_VERSION" ] || SDD_VERSION="unknown"
SDD_COMMIT="$(git -C "$SCRIPT_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"

echo ""
echo "Instalando scripts de enforcement..."
mkdir -p "$ENFORCE_ROOT/.sdd/scripts"
for script in sdd-seal.py sdd-gate-check.py sdd-task-state.py sdd-sync-check.py sdd-skill-allow.py; do
  cp "$SCRIPT_DIR/scripts/$script" "$ENFORCE_ROOT/.sdd/scripts/$script"
  # Sello de versión en el propio script: viaja commiteado al repo del proyecto
  # y a CI, donde no hay ~/.sdd-home al lado para preguntarle.
  if command -v python3 >/dev/null 2>&1; then
    SDD_STAMP="$SDD_VERSION+$SDD_COMMIT" python3 - "$ENFORCE_ROOT/.sdd/scripts/$script" <<'PYEOF'
import os, sys
from pathlib import Path
p = Path(sys.argv[1]); lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
stamp = f"# sdd-version: {os.environ['SDD_STAMP']}\n"
out = [lines[0], stamp] + [l for l in lines[1:] if not l.startswith("# sdd-version:")]
p.write_text("".join(out), encoding="utf-8")
PYEOF
  fi
  echo "  ✓ $ENFORCE_ROOT/.sdd/scripts/$script"
done

# Sello de instalación del proyecto: qué versión del ecosistema produjo esta copia.
cat > "$ENFORCE_ROOT/.sdd/sdd-version.json" <<EOF
{
  "version": "$SDD_VERSION",
  "commit": "$SDD_COMMIT",
  "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "installed_by": "install.sh"
}
EOF
echo "  ✓ $ENFORCE_ROOT/.sdd/sdd-version.json (sdd $SDD_VERSION+$SDD_COMMIT)"

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

# ── 6. Reconciliar piezas SDD de fases no seleccionadas ─────────────────────
# Detecta skills/agents que pertenecen al ecosistema SDD (existen en alguna
# fase del framework) pero NO se instalaron en este run: huerfanos de un
# install anterior con mas fases. Solo toca piezas SDD — las skills/agents
# propios del proyecto y los overlays de stack (tech/<stack>) no se tocan.

in_list() {
  case " $2 " in *" $1 "*) return 0 ;; esac
  return 1
}

MANAGED_SKILLS=""
MANAGED_AGENTS=""
for d in prd spec design plan tasks; do
  for s in "$SCRIPT_DIR/$d/skills"/*/; do
    [ -d "$s" ] && MANAGED_SKILLS="$MANAGED_SKILLS $(basename "$s")"
  done
  for a in "$SCRIPT_DIR/$d/agents"/*.md; do
    [ -f "$a" ] && MANAGED_AGENTS="$MANAGED_AGENTS $(basename "$a")"
  done
done

ORPHAN_SKILLS=""
for dir in "$CLAUDE_DIR/skills"/*/; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  if in_list "$name" "$MANAGED_SKILLS" && ! in_list "$name" "$INSTALLED_SKILLS"; then
    ORPHAN_SKILLS="$ORPHAN_SKILLS $name"
  fi
done

ORPHAN_AGENTS=""
for f in "$CLAUDE_DIR/agents"/*.md; do
  [ -f "$f" ] || continue
  name=$(basename "$f")
  if in_list "$name" "$MANAGED_AGENTS" && ! in_list "$name" "$INSTALLED_AGENTS"; then
    ORPHAN_AGENTS="$ORPHAN_AGENTS $name"
  fi
done

ORPHAN_PHASE_DOCS=""
for p in prd spec design plan tasks; do
  if { [ -f "$CLAUDE_DIR/rules/sdd-$p.md" ] || [ -f "$CLAUDE_DIR/phases/$p.md" ]; } && ! has_phase "$p"; then
    ORPHAN_PHASE_DOCS="$ORPHAN_PHASE_DOCS $p"
  fi
done

if [ -n "$ORPHAN_SKILLS" ] || [ -n "$ORPHAN_AGENTS" ] || [ -n "$ORPHAN_PHASE_DOCS" ]; then
  echo ""
  if [ "$PRUNE" = "1" ]; then
    echo "Eliminando piezas SDD de fases no seleccionadas (--prune)..."
    for name in $ORPHAN_SKILLS; do
      rm -rf "$CLAUDE_DIR/skills/$name"
      echo "  ✗ skills/$name/ eliminada"
    done
    for name in $ORPHAN_AGENTS; do
      rm -f "$CLAUDE_DIR/agents/$name"
      echo "  ✗ agents/$name eliminado"
    done
    for p in $ORPHAN_PHASE_DOCS; do
      rm -f "$CLAUDE_DIR/rules/sdd-$p.md" "$CLAUDE_DIR/phases/$p.md"
      echo "  ✗ rules/sdd-$p.md eliminado"
    done
  else
    echo "⚠ Piezas SDD de fases no seleccionadas detectadas en .claude/ (de un install anterior):"
    for name in $ORPHAN_SKILLS; do echo "    skills/$name/"; done
    for name in $ORPHAN_AGENTS; do echo "    agents/$name"; done
    for p in $ORPHAN_PHASE_DOCS; do echo "    rules/sdd-$p.md"; done
    echo "  Siguen instaladas e invocables. Para eliminarlas: bash install.sh $RAW_ARG --prune"
  fi
fi

# ── 7. Re-aplicar el overlay de stack si el proyecto lo declara ─────────────
# La instalación de fases genéricas copia por basename y PISA las variantes
# del overlay (plan-architect.md, kb-plan-expert...). Si el proyecto declara
# un stack en .sdd/project-init.json, re-aplicar el overlay al final restaura
# las variantes. (/wf-sdd-update ya sigue este orden; esto cubre la ejecución
# manual de install.sh, que antes degradaba el proyecto en silencio.)

PROJECT_STACK=""
if command -v python3 >/dev/null 2>&1 && [ -f "$ENFORCE_ROOT/.sdd/project-init.json" ]; then
  PROJECT_STACK="$(python3 - "$ENFORCE_ROOT/.sdd/project-init.json" <<'PYEOF'
import json, sys
try:
    stack = json.load(open(sys.argv[1])).get("stack")
    print(stack if isinstance(stack, str) and stack.replace("-", "").isalnum() else "")
except Exception:
    print("")
PYEOF
)"
fi

if [ -n "$PROJECT_STACK" ] && { has_phase plan || has_phase tasks; }; then
  if [ -f "$SCRIPT_DIR/tech/$PROJECT_STACK/install.sh" ]; then
    echo ""
    echo "Proyecto con stack '$PROJECT_STACK' declarado: re-aplicando el overlay"
    echo "(la instalación genérica de plan/tasks pisa sus variantes por basename)..."
    (cd "$ENFORCE_ROOT" && bash "$SCRIPT_DIR/tech/$PROJECT_STACK/install.sh")
  else
    echo ""
    echo "⚠ El proyecto declara stack '$PROJECT_STACK' pero este ecosistema no tiene"
    echo "  tech/$PROJECT_STACK/install.sh. Las variantes del overlay pueden haber quedado"
    echo "  pisadas por las piezas genéricas de plan/tasks — re-aplica el overlay manualmente."
  fi
fi

echo ""
echo "Done. Reinicia Claude Code para activar los agentes y skills."
