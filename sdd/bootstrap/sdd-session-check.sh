#!/bin/bash
# Hook SessionStart del ecosistema SDD.
# Comprueba de forma determinista el estado SDD del proyecto y, solo cuando
# procede, inyecta una directiva [SDD-PROTOCOL] en el contexto de la sesion.
#
# Estados:
#   .sdd/project-init.json existe                  → proyecto SDD inicializado, no inyecta nada
#   .claude/sdd-mode.json con mode "free"          → modo libre, no inyecta nada
#   .claude/sdd-mode.json con mode "sdd" sin init  → inyecta directiva init-pending
#   sin marcador ni init                           → inyecta directiva mode-undecided (wizard)
#
# Instalado por setup.sh en ~/.claude/hooks/sdd-session-check.sh
set -u

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
cd "$PROJECT_DIR" 2>/dev/null || exit 0

# No aplicar en el home del usuario (una sesion en ~ no es un proyecto)
[ "$PROJECT_DIR" = "$HOME" ] && exit 0

# No aplicar dentro del propio repo del ecosistema SDD
SDD_HOME="$(cat "$HOME/.sdd-home" 2>/dev/null || true)"
if [ -n "$SDD_HOME" ]; then
  case "$PROJECT_DIR/" in
    "$SDD_HOME/"*) exit 0 ;;
  esac
fi

# 1. Proyecto SDD inicializado → verificar que el init esta completo
if [ -f .sdd/project-init.json ]; then
  PHASES_LINE="$(tr -d '\n' < .sdd/project-init.json | grep -o '"phases"[[:space:]]*:[[:space:]]*\[[^]]*\]' || true)"
  MISSING=""
  for f in prd spec design plan tasks; do
    case "$PHASES_LINE" in
      *"\"$f\""*) [ -f "$f/.claude/CLAUDE.md" ] || MISSING="$MISSING $f" ;;
    esac
  done
  if [ -n "$MISSING" ]; then
    echo "[SDD-PROTOCOL] init-incomplete — Este proyecto declara las fases [$MISSING ] en .sdd/project-init.json pero no estan instaladas (falta <fase>/.claude/CLAUDE.md). Antes de atender la peticion del usuario, invoca el skill wf-project-init (opcion 'Completar / ampliar') para reparar la instalacion. No repitas el wizard de modo."
  fi
  exit 0
fi

# 2. Modo ya decidido
if [ -f .claude/sdd-mode.json ]; then
  if grep -q '"mode"[[:space:]]*:[[:space:]]*"free"' .claude/sdd-mode.json; then
    exit 0
  fi
  if grep -q '"mode"[[:space:]]*:[[:space:]]*"sdd"' .claude/sdd-mode.json; then
    echo "[SDD-PROTOCOL] init-pending — Este proyecto esta marcado en modo SDD pero no tiene .sdd/project-init.json. Antes de atender la peticion del usuario, invoca el skill wf-project-init para completar la inicializacion. No repitas el wizard de modo."
    exit 0
  fi
fi

# 3. Sin decision de modo → pedir el wizard
cat <<'EOF'
[SDD-PROTOCOL] mode-undecided — Este proyecto no tiene decidido el modo de trabajo de Claude. Antes de atender la primera peticion del usuario, presenta el wizard de modo siguiendo el "Protocolo SDD de inicio de sesion" definido en el CLAUDE.md global (~/.claude/CLAUDE.md): pregunta con AskUserQuestion entre "Modo SDD" y "Modo libre", persiste la eleccion en .claude/sdd-mode.json y actua en consecuencia.
EOF
exit 0
