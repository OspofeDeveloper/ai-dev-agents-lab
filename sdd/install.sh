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
PIPELINE_DIR="$SCRIPT_DIR/pipeline"
SHARED_DIR="$PIPELINE_DIR/spec/shared/templates"
CLAUDE_DIR="$(pwd)/.claude"
KMM_DIR="$SCRIPT_DIR/tech/kmm"

usage() {
  echo "Uso: bash install.sh [all|prd|spec|design|plan|tasks|<fase1,fase2,...>] [--prune]"
  echo "  all (por defecto): instala el ecosistema SDD completo"
  echo "  prd,spec          : instala PRD y Spec"
  echo "  prd,spec,design   : instala PRD, Spec y Design"
  echo "  --prune           : elimina del .claude/ las skills/agents SDD de fases no seleccionadas"
  echo "  --design-role <r> : con la fase design, qué capa instalar: system (autora DESIGN.md),"
  echo "                      feature (autora flows/views/ui_prompt) o full (ambas, por defecto)."
  echo "                      Forma: --design-role=system|feature|full"
  echo "  --artifacts-<fase>=<dir> : directorio raíz de los artefactos de esa fase (prd|spec|design)"
  echo "                      cuando NO es el canónico (p. ej. --artifacts-spec=specs). Reescribe el"
  echo "                      glob de directorio de la regla a '<dir>/**'. Lo pasa wf-project-init"
  echo "                      según el mapa artifacts del proyecto (Paso 5.6/6)."
  echo "  --no-claude-md    : no siembra .claude/CLAUDE.md (lo autora wf-project-init en su Paso 7)"
}

RAW_ARG="all"
PRUNE=0
DESIGN_ROLE="full"   # system | feature | full — qué agente+bundle de la fase design instalar
NO_CLAUDE_MD=0       # 1 = no sembrar CLAUDE.md (wf-project-init lo autora él mismo en su Paso 7)
# Directorio raíz de artefactos por fase si NO es el canónico (Paso 5.6/6). Vacío =
# canónico (= nombre de la fase). bash 3.2 (macOS) no tiene arrays asociativos: tres vars.
ART_PRD=""
ART_SPEC=""
ART_DESIGN=""
for arg in "$@"; do
  case "$arg" in
    --prune) PRUNE=1 ;;
    --design-role=*) DESIGN_ROLE="${arg#*=}" ;;
    --artifacts-prd=*)    ART_PRD="${arg#*=}";    ART_PRD="${ART_PRD%/}" ;;
    --artifacts-spec=*)   ART_SPEC="${arg#*=}";   ART_SPEC="${ART_SPEC%/}" ;;
    --artifacts-design=*) ART_DESIGN="${arg#*=}"; ART_DESIGN="${ART_DESIGN%/}" ;;
    --no-claude-md) NO_CLAUDE_MD=1 ;;
    -h|--help|help) usage; exit 0 ;;
    *) RAW_ARG="$arg" ;;
  esac
done
case "$DESIGN_ROLE" in
  system|feature|full) ;;
  *) echo "ERROR: --design-role invalido: '$DESIGN_ROLE' (usa system|feature|full)"; exit 1 ;;
esac

# ¿El rol incluye la capa system / la capa feature?
design_has_system() { [ "$DESIGN_ROLE" = "system" ] || [ "$DESIGN_ROLE" = "full" ]; }
design_has_feature() { [ "$DESIGN_ROLE" = "feature" ] || [ "$DESIGN_ROLE" = "full" ]; }

# Partición de la fase design por rol (SSoT del split de agentes, A0).
DESIGN_SHARED_KB="kb-design-expert kb-design-system-contract kb-design-brief kb-design-governance kb-a11y-expert kb-a11y-web-expert kb-design-motion-expert kb-design-iconography-expert kb-design-voice kb-design-layout"
DESIGN_SYSTEM_WF="wf-design-intake wf-design-moodboard wf-design-system wf-design-extract wf-design-validate wf-design-delta wf-design-export wf-design-branch wf-design-sync wf-design-a11y-audit"
DESIGN_SYSTEM_KB="kb-design-characterization kb-design-style-decision-tree kb-design-style-taxonomy"
DESIGN_FEATURE_WF="wf-design-feature-prototype wf-design-variant wf-design-feedback"
DESIGN_FEATURE_KB="kb-design-feature-artifacts kb-design-conflict-expert kb-design-forms"

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
  copy_template "feature_spec_template.md"   "$PIPELINE_DIR/spec/skills/wf-spec-fast-track/references"
  copy_template "feature_readme_template.md" "$PIPELINE_DIR/spec/skills/wf-spec-fast-track/references"
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
  install_agent "$PIPELINE_DIR/prd/agents/prd-expert.md"
fi
if has_phase "spec"; then
  install_agent "$PIPELINE_DIR/prd/agents/prd-expert.md" 2>/dev/null || true
  install_agent "$PIPELINE_DIR/spec/agents/sdd-spec-explorer.md"
  install_agent "$PIPELINE_DIR/spec/agents/sdd-spec-planner.md"
  install_agent "$PIPELINE_DIR/spec/agents/sdd-spec-writer.md"
  install_agent "$PIPELINE_DIR/spec/agents/sdd-spec-auditor.md"
fi
if has_phase "design"; then
  if design_has_system; then
    install_agent "$PIPELINE_DIR/design/agents/design-system-architect.md"
  fi
  if design_has_feature; then
    install_agent "$PIPELINE_DIR/design/agents/design-feature-architect.md"
  fi
fi
if has_phase "plan"; then
  install_agent "$PIPELINE_DIR/plan/agents/plan-architect.md"
  install_agent "$PIPELINE_DIR/plan/agents/plan-auditor.md"
fi
if has_phase "tasks"; then
  install_agent "$PIPELINE_DIR/tasks/agents/task-generator.md"
  install_agent "$PIPELINE_DIR/tasks/agents/qa-engineer.md"
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
  for skill_dir in "$PIPELINE_DIR/prd/skills"/*/; do
    install_skill "$skill_dir"
  done
fi

if has_phase "spec"; then
  # spec necesita algunas skills de prd como dependencia
  install_skill "$PIPELINE_DIR/prd/skills/kb-prd-expert"
  install_skill "$PIPELINE_DIR/prd/skills/kb-product-change-governance"
  install_skill "$PIPELINE_DIR/prd/skills/wf-prd-change"
  install_skill "$PIPELINE_DIR/prd/skills/wf-prd-review"

  for skill_dir in "$PIPELINE_DIR/spec/skills"/*/; do
    install_skill "$skill_dir"
  done
fi

if has_phase "design"; then
  # design necesita kb-spec-expert como dependencia cross-fase
  install_skill "$PIPELINE_DIR/spec/skills/kb-spec-expert"

  # KBs compartidas: van en ambos roles (el design-feature-architect carga el
  # contrato del sistema como referencia de solo-lectura).
  for s in $DESIGN_SHARED_KB; do
    install_skill "$PIPELINE_DIR/design/skills/$s"
  done

  # Capa system: autoría del DESIGN.md (intake, moodboard, system, extract,
  # validate, delta, export, branch, sync, a11y-audit + KBs de dirección visual).
  if design_has_system; then
    for s in $DESIGN_SYSTEM_WF $DESIGN_SYSTEM_KB; do
      install_skill "$PIPELINE_DIR/design/skills/$s"
    done
  fi

  # Capa feature: autoría de flows/views/ui_prompt (prototype, variant, feedback
  # + KBs de artefactos por feature).
  if design_has_feature; then
    for s in $DESIGN_FEATURE_WF $DESIGN_FEATURE_KB; do
      install_skill "$PIPELINE_DIR/design/skills/$s"
    done
  fi
fi

if has_phase "plan"; then
  # plan necesita kb-spec-expert, las KBs a11y (núcleo + deltas web) y kb-design-governance (handoff Design→Plan) como dependencias cross-fase
  install_skill "$PIPELINE_DIR/spec/skills/kb-spec-expert"
  install_skill "$PIPELINE_DIR/design/skills/kb-a11y-expert"
  install_skill "$PIPELINE_DIR/design/skills/kb-a11y-web-expert"
  install_skill "$PIPELINE_DIR/design/skills/kb-design-governance"

  for skill_dir in "$PIPELINE_DIR/plan/skills"/*/; do
    install_skill "$skill_dir"
  done
fi

if has_phase "tasks"; then
  # tasks necesita kb-plan-expert y kb-spec-expert (qa-engineer) como dependencias
  install_skill "$PIPELINE_DIR/plan/skills/kb-plan-expert"
  install_skill "$PIPELINE_DIR/spec/skills/kb-spec-expert"

  for skill_dir in "$PIPELINE_DIR/tasks/skills"/*/; do
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
# si el proyecto usa un directorio no canónico (Paso 5.6/6), wf-project-init lo
# pasa con --artifacts-<fase> y la reescritura del glob de directorio la hace
# este script de forma determinista (antes era una edición a mano del agente,
# fácil de omitir — CU-1.m). El backstop es el check rule-globs de verify().
mkdir -p "$CLAUDE_DIR/rules"

# Directorio raíz del glob de cada fase: el override de --artifacts-<fase> o, si
# no se dio, el canónico (= nombre de la fase).
phase_dir() {
  case "$1" in
    prd)    echo "${ART_PRD:-prd}" ;;
    spec)   echo "${ART_SPEC:-spec}" ;;
    design) echo "${ART_DESIGN:-design}" ;;
    *)      echo "" ;;
  esac
}

phase_globs() {
  local dir
  case "$1" in
    prd)    dir="$(phase_dir prd)";    printf '%s\n' "$dir/**" "**/prd*.md" "**/*_analysis.md" "**/*_discovery.md" ;;
    spec)   dir="$(phase_dir spec)";   printf '%s\n' "$dir/**" "**/features/*/spec/**" "**/*_spec.md" "**/*_features.md" ;;
    design) dir="$(phase_dir design)"; printf '%s\n' "$dir/**" "**/features/*/design/**" "**/DESIGN*.md" "**/*_flows.md" "**/*_views.md" "**/*_ui_prompt*.md" ;;
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
    cat "$PIPELINE_DIR/$p/CLAUDE.md"
  } > "$CLAUDE_DIR/rules/sdd-$p.md"
  echo "  ✓ rules/sdd-$p.md"
}

for p in prd spec design plan tasks; do
  if has_phase "$p"; then
    install_phase_rule "$p"
  fi
done

# Regla de orquestación EAGER: una regla en .claude/rules/ SIN frontmatter
# `paths:` se carga al arrancar la sesión, igual que un CLAUDE.md (doc Claude
# Code: memory §path-specific-rules). Es el carril para la disciplina transversal
# que el orquestador necesita ANTES de tocar ficheros (readiness mecánica, no por
# topología; orden del pipeline; no bypasear gates) — justo el momento que las
# reglas de fase (lazy por `paths:`) no cubren. Ver DECISIONS D-021. Se escribe
# siempre (no lo alcanza el --prune, que solo borra sdd-<fase>.md / overlays).
install_orchestration_rule() {
  {
    echo "---"
    echo "description: Disciplina de orquestación SDD (transversal, carga eager — no declara globs)"
    echo "---"
    echo ""
    cat "$PIPELINE_DIR/orchestration.md"
    # Línea específica de frontera, activada por topología: solo tiene sentido si
    # el proyecto instala PRD y Spec (la única frontera con verificador hoy).
    if has_phase prd && has_phase spec; then
      echo ""
      echo "## Frontera PRD → Spec"
      echo ""
      echo "- Antes de recomendar o entrar en Spec con un PRD existente, comprueba la readiness mecánicamente: \`python3 .sdd/scripts/sdd-prd-ready.py <prd.md>\`. El script imprime el veredicto en **stdout** y sale con **código ≠0 cuando no está listo** (\`2\` = no listo, por diseño para gates): eso **no es un error** — lee el veredicto de stdout, no lo trates como comando fallido. Si el veredicto no es \`READY\` (hay \`OPEN_ASSUMPTIONS\`/\`ASSUMPTION_MISMATCH\`, o está \`UNSEALED\`), el siguiente paso correcto es **revisar el PRD** (\`wf-prd-review\`), no generar specs. Nunca declares el PRD \"listo\" sin la evidencia del script."
    fi
  } > "$CLAUDE_DIR/rules/sdd-orchestration.md"
  echo "  ✓ rules/sdd-orchestration.md (eager)"
}
install_orchestration_rule

# CLAUDE.md raíz: SOLO se siembra si no existe ya uno. wf-project-init lo regenera
# después (Paso 7) con la plantilla específica del proyecto; wf-sdd-update reinstala
# fases SIN pisar ese CLAUDE.md con el genérico del ecosistema (191 líneas). Por eso,
# si ya hay un CLAUDE.md, se respeta. Para refrescar uno genérico stand-alone: bórralo antes.
# Con --no-claude-md (lo pasa wf-project-init) NO se siembra: el skill lo escribe él, y así
# su Write no choca con un fichero pre-sembrado que el harness exigiría leer antes.
if [ "$NO_CLAUDE_MD" = "1" ]; then
  echo "  ✓ CLAUDE.md (omitido — lo autora wf-project-init)"
elif [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
  echo "  ✓ CLAUDE.md (preservado — ya existía)"
else
  PHASE_COUNT="${#PHASES[@]}"
  if has_phase "all" || [ "$PHASE_COUNT" -gt 1 ]; then
    cp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
  else
    for p in prd spec design plan tasks; do
      if has_phase "$p"; then
        cp "$PIPELINE_DIR/$p/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
      fi
    done
  fi
  echo "  ✓ CLAUDE.md"
fi

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
for script in sdd-seal.py sdd-gate-check.py sdd-task-state.py sdd-sync-check.py sdd-skill-allow.py sdd-amend.py sdd-features-index.py sdd-project-status.py sdd-kb-check.py sdd-release.py sdd-next-id.py sdd-resolve-path.py sdd-design-resolve.py sdd-source-drift.py sdd-prd-ready.py; do
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

# Stack declarado por el proyecto (si ya escribió su project-init.json). Lo usan
# tanto la poda de overlays obsoletos (6b) como la re-aplicación del overlay
# (Paso 7). Vacío si aún no hay project-init.json (p. ej. el primer install de un
# init nuevo, antes de que el agente escriba el estado).
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

MANAGED_SKILLS=""
MANAGED_AGENTS=""
for d in prd spec design plan tasks; do
  for s in "$PIPELINE_DIR/$d/skills"/*/; do
    [ -d "$s" ] && MANAGED_SKILLS="$MANAGED_SKILLS $(basename "$s")"
  done
  for a in "$PIPELINE_DIR/$d/agents"/*.md; do
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

# ── 6b. Podar overlays de stack obsoletos (cambio de stack) ─────────────────
# Un overlay de OTRO stack (p. ej. kmm) que sobreviva tras cambiar el stack del
# proyecto (p. ej. a ios/android/agnostico) NO es inerte como una fase de más:
# su regla sdd-<stack>.md carga convenciones del stack equivocado sobre .kt y
# artefactos de plan/tasks, y sus agentes/skills (wf-<stack>-*, <stack>-*) son
# basura invocable. Como un proyecto solo puede tener UN stack, si el proyecto
# declara un stack conocido distinto, las piezas EXCLUSIVAS del overlay ajeno se
# retiran SIEMPRE (a diferencia de una fase de más, no son inertes; no requieren
# --prune). Las piezas de basename compartido (plan-architect.md, kb-plan-expert…)
# NO se tocan: el install base de arriba ya las restauró a su variante genérica.
if [ -n "$PROJECT_STACK" ]; then
  STALE_OVL_SKILLS=""
  STALE_OVL_AGENTS=""
  STALE_OVL_RULES=""
  for techdir in "$SCRIPT_DIR/tech"/*/; do
    [ -d "$techdir" ] || continue
    st=$(basename "$techdir")
    [ "$st" = "$PROJECT_STACK" ] && continue
    # skills exclusivas del overlay (raíz + subdirs plan/ y tasks/, como las
    # instala tech/<stack>/install.sh). Los contenedores plan/tasks se saltan.
    for s in "$techdir"skills/*/ "$techdir"skills/plan/*/ "$techdir"skills/tasks/*/; do
      [ -d "$s" ] || continue
      n=$(basename "$s")
      case "$n" in plan|tasks) continue ;; esac
      if ! in_list "$n" "$MANAGED_SKILLS" && [ -d "$CLAUDE_DIR/skills/$n" ]; then
        in_list "$n" "$STALE_OVL_SKILLS" || STALE_OVL_SKILLS="$STALE_OVL_SKILLS $n"
      fi
    done
    # agentes exclusivos del overlay (los de basename compartido los restaura el base)
    for a in "$techdir"agents/*.md; do
      [ -f "$a" ] || continue
      n=$(basename "$a")
      if ! in_list "$n" "$MANAGED_AGENTS" && [ -f "$CLAUDE_DIR/agents/$n" ]; then
        in_list "$n" "$STALE_OVL_AGENTS" || STALE_OVL_AGENTS="$STALE_OVL_AGENTS $n"
      fi
    done
    # regla del stack ajeno (convención sdd-<stack>.md)
    if [ -f "$CLAUDE_DIR/rules/sdd-$st.md" ]; then
      STALE_OVL_RULES="$STALE_OVL_RULES $st"
    fi
  done
  if [ -n "$STALE_OVL_SKILLS" ] || [ -n "$STALE_OVL_AGENTS" ] || [ -n "$STALE_OVL_RULES" ]; then
    echo ""
    echo "Retirando overlay(s) de stack obsoleto(s) (el proyecto declara stack '$PROJECT_STACK')..."
    for name in $STALE_OVL_SKILLS; do
      rm -rf "$CLAUDE_DIR/skills/$name"
      echo "  ✗ skills/$name/ (overlay ajeno)"
    done
    for name in $STALE_OVL_AGENTS; do
      rm -f "$CLAUDE_DIR/agents/$name"
      echo "  ✗ agents/$name (overlay ajeno)"
    done
    for st in $STALE_OVL_RULES; do
      rm -f "$CLAUDE_DIR/rules/sdd-$st.md"
      echo "  ✗ rules/sdd-$st.md (overlay ajeno)"
    done
  fi
fi

# ── 7. Re-aplicar el overlay de stack si el proyecto lo declara ─────────────
# La instalación de fases genéricas copia por basename y PISA las variantes
# del overlay (plan-architect.md, kb-plan-expert...). Si el proyecto declara
# un stack en .sdd/project-init.json, re-aplicar el overlay al final restaura
# las variantes. (/wf-sdd-update ya sigue este orden; esto cubre la ejecución
# manual de install.sh, que antes degradaba el proyecto en silencio.)
# PROJECT_STACK se calcula antes del Paso 6 (lo comparte con la poda 6b).

if [ -n "$PROJECT_STACK" ] && { has_phase plan || has_phase tasks; }; then
  if [ -f "$SCRIPT_DIR/tech/$PROJECT_STACK/install.sh" ]; then
    echo ""
    echo "Proyecto con stack '$PROJECT_STACK' declarado: re-aplicando el overlay"
    echo "(la instalación genérica de plan/tasks pisa sus variantes por basename)..."
    (cd "$ENFORCE_ROOT" && bash "$SCRIPT_DIR/tech/$PROJECT_STACK/install.sh")
  else
    echo ""
    echo "ℹ El stack '$PROJECT_STACK' no tiene overlay especialista en este ecosistema:"
    echo "  plan/tasks operan en modo genérico (agentes stack-agnósticos). Nada que reinstalar."
  fi
fi

# ── 8. Verificar que las KBs declaradas por los agentes están instaladas ────
# (ROADMAP 1.5) Check determinista: el auto-reporte "KB Load Status" del agente
# es señal secundaria; esta es la autoritativa. No bloquea — avisa de instalaciones
# incompletas (agente presente con alguna KB de su frontmatter sin instalar).

if command -v python3 >/dev/null 2>&1 && [ -f "$ENFORCE_ROOT/.sdd/scripts/sdd-kb-check.py" ]; then
  echo ""
  echo "Verificando KBs de los agentes instalados..."
  if python3 "$ENFORCE_ROOT/.sdd/scripts/sdd-kb-check.py" --claude-dir "$CLAUDE_DIR" --all; then
    :
  else
    echo "  ⚠ Algún agente declara KBs no instaladas (ver arriba). Si era una"
    echo "    instalación por fases, reinstala con la fase/overlay que las aporta."
  fi
fi

echo ""
echo "Done. Ejecuta /skills y /agents para revisar que Claude ha cargado correctamente el ecosistema. Si no lo ha hecho, comienza una sesión nueva de Claude para que se carguen."
