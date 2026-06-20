#!/bin/bash
# Hook SessionStart del ecosistema SDD.
# Comprueba de forma determinista el estado SDD del proyecto y, solo cuando
# procede, inyecta una directiva [SDD-PROTOCOL] en el contexto de la sesion.
#
# Estados:
#   .sdd/project-init.json existe                  → proyecto SDD inicializado:
#       - fases declaradas sin instalar             → init-incomplete
#       - specialist_workflow sin run en            → specialist-init-pending (no bloquea)
#         .sdd/stack-runs.jsonl
#       - version del sello != ecosistema           → version-drift (no bloquea)
#   .claude/sdd-mode.json con mode "free"          → modo libre, no inyecta nada
#   .claude/sdd-mode.json con mode "sdd" sin init  → inyecta directiva init-pending
#   sin marcador ni init                           → inyecta directiva mode-undecided (wizard)
#
# Instalado por setup.sh en ~/.claude/hooks/sdd-session-check.sh
set -u

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
cd "$PROJECT_DIR" 2>/dev/null || exit 0
PROJECT_DIR_PHYS="$(pwd -P)"   # ruta fisica (sin symlinks); git resuelve symlinks

# Modo CI/headless: en runners no interactivos el protocolo de sesion se
# suprime por completo — no hay humano para el wizard, el init ni decisiones
# de update. SDD_NON_INTERACTIVE=1 es el opt-out explicito; CI=true es el
# estandar de facto de los runners (GitHub Actions, GitLab CI, CircleCI...).
# El opt-out commiteable por repo sigue siendo .claude/sdd-mode.json.
if [ "${SDD_NON_INTERACTIVE:-}" = "1" ] || [ "${CI:-}" = "true" ]; then
  exit 0
fi

# No aplicar en el home del usuario (una sesion en ~ no es un proyecto)
[ "$PROJECT_DIR" = "$HOME" ] && exit 0

# No aplicar dentro del propio repo del ecosistema SDD
SDD_HOME="$(cat "$HOME/.sdd-home" 2>/dev/null || true)"
if [ -n "$SDD_HOME" ]; then
  case "$PROJECT_DIR/" in
    "$SDD_HOME/"*) exit 0 ;;
  esac
  # Tambien el repo git que contiene el framework (SDD_HOME puede ser un
  # subdirectorio, p. ej. <repo>/sdd): una sesion en ese repo es desarrollo
  # del ecosistema, no un proyecto consumidor. Si git no esta disponible,
  # se omite esta exclusion adicional. Se compara con rutas fisicas porque
  # git devuelve el toplevel resuelto (sin symlinks).
  SDD_REPO="$(git -C "$SDD_HOME" rev-parse --show-toplevel 2>/dev/null || true)"
  if [ -n "$SDD_REPO" ]; then
    case "$PROJECT_DIR_PHYS/" in
      "$SDD_REPO/"*) exit 0 ;;
    esac
  fi
fi

# Opt-out por ruta (ROADMAP 5.6): el dev puede silenciar el hook en proyectos
# concretos SIN tocar cada repo. Dos listas opcionales de PREFIJOS de ruta en
# ~/.claude/ (un prefijo por linea; '#' comenta, lineas vacias se ignoran,
# '~' se expande a $HOME):
#   sdd-denylist  → si el proyecto cuelga de algun prefijo listado, silencio total.
#   sdd-allowlist → si existe y tiene algun prefijo, el hook SOLO actua dentro de
#                   esos prefijos (modo opt-in); fuera de ellos, silencio.
# El opt-out por repo y commiteable sigue siendo .claude/sdd-mode.json.
_sdd_path_listed() {  # $1=archivo de lista → 0 si PROJECT_DIR cuelga de algun prefijo
  local list="$1" raw prefix
  [ -f "$list" ] || return 1
  while IFS= read -r raw || [ -n "$raw" ]; do
    raw="${raw%%#*}"                        # quita comentario
    raw="${raw%$'\r'}"                      # CR de Windows
    raw="${raw#"${raw%%[![:space:]]*}"}"    # ltrim
    raw="${raw%"${raw##*[![:space:]]}"}"    # rtrim
    [ -z "$raw" ] && continue
    case "$raw" in "~"|"~/"*) prefix="$HOME${raw#\~}" ;; *) prefix="$raw" ;; esac
    prefix="${prefix%/}"
    [ -z "$prefix" ] && continue
    case "$PROJECT_DIR/"      in "$prefix/"*) return 0 ;; esac
    case "$PROJECT_DIR_PHYS/" in "$prefix/"*) return 0 ;; esac
  done < "$list"
  return 1
}

_sdd_path_listed "$HOME/.claude/sdd-denylist" && exit 0

if [ -f "$HOME/.claude/sdd-allowlist" ] && \
   grep -qE '^[[:space:]]*[^#[:space:]]' "$HOME/.claude/sdd-allowlist" 2>/dev/null; then
  _sdd_path_listed "$HOME/.claude/sdd-allowlist" || exit 0
fi

# Raiz SDD en monorepos (ROADMAP 5.7): los marcadores SDD (.sdd/project-init.json,
# .claude/sdd-mode.json) viven en la raiz del proyecto, pero la sesion puede
# abrirse en un subpaquete. Se buscan hacia arriba hasta el toplevel git (techo);
# fuera de git, solo el propio directorio (comportamiento previo intacto). Gana
# el ancestro mas cercano: un .sdd/ propio del subpaquete prevalece sobre el raiz.
SDD_CEILING="$(git -C "$PROJECT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "$SDD_CEILING" ] && SDD_CEILING="$(cd "$SDD_CEILING" 2>/dev/null && pwd -P || echo "$SDD_CEILING")"
[ -z "$SDD_CEILING" ] && SDD_CEILING="$PROJECT_DIR_PHYS"

_sdd_find_up() {  # $1=ruta relativa del marcador → echo del dir ancestro que lo tiene
  local marker="$1" dir="$PROJECT_DIR_PHYS"
  while :; do
    [ -e "$dir/$marker" ] && { printf '%s' "$dir"; return 0; }
    [ "$dir" = "$SDD_CEILING" ] && break
    [ "$dir" = "/" ] && break
    dir="$(dirname "$dir")"
  done
  return 1
}

INIT_ROOT="$(_sdd_find_up ".sdd/project-init.json" || true)"
MODE_ROOT="$(_sdd_find_up ".claude/sdd-mode.json" || true)"

# 1. Proyecto SDD inicializado → verificar que el init esta completo
if [ -n "$INIT_ROOT" ]; then
  INIT_JSON="$INIT_ROOT/.sdd/project-init.json"
  # Extraer las fases declaradas. Parser primario: python3 (JSON real).
  # Fallback sin python3: extraccion textual del array. Ante JSON malformado,
  # PHASES_LIST queda vacia y no se inyecta nada (conservador: mejor no
  # disparar init-incomplete espurio en cada sesion).
  if command -v python3 >/dev/null 2>&1; then
    PHASES_LIST="$(python3 -c '
import json, sys
try:
    with open(sys.argv[1]) as f:
        phases = json.load(f).get("phases", [])
    if isinstance(phases, list):
        print(" ".join(p for p in phases if isinstance(p, str)))
except Exception:
    pass
' "$INIT_JSON" 2>/dev/null || true)"
  else
    PHASES_LIST="$(tr -d '\n' < "$INIT_JSON" \
      | grep -o '"phases"[[:space:]]*:[[:space:]]*\[[^]]*\]' \
      | grep -o '"[a-z]*"' | tr -d '"' | grep -vx 'phases' | tr '\n' ' ' || true)"
  fi
  MISSING=""
  for f in prd spec design plan tasks; do
    case " $PHASES_LIST " in
      *" $f "*)
        # Layout actual: regla de fase en .claude/rules/sdd-<fase>.md
        # Layouts legacy: .claude/phases/<fase>.md y <fase>/.claude/CLAUDE.md
        [ -f "$INIT_ROOT/.claude/rules/sdd-$f.md" ] || [ -f "$INIT_ROOT/.claude/phases/$f.md" ] || [ -f "$INIT_ROOT/$f/.claude/CLAUDE.md" ] || MISSING="$MISSING $f"
        ;;
    esac
  done
  if [ -n "$MISSING" ]; then
    echo "[SDD-PROTOCOL] init-incomplete — Este proyecto declara las fases [$MISSING ] en .sdd/project-init.json pero no estan instaladas (falta .claude/phases/<fase>.md). Antes de atender la peticion del usuario, invoca el skill wf-project-init (opcion 'Completar / ampliar') para reparar la instalacion. No repitas el wizard de modo."
    exit 0
  fi

  # Init especialista de stack pendiente (precondicion contextual, NUNCA bloquea):
  # si project-init.json declara specialist_workflow y no hay run registrado en
  # .sdd/stack-runs.jsonl, avisar para completar el init tecnico del stack ANTES de
  # plan/tasks/implementacion. La logica vive en sdd-init-detect.py (specialist-status);
  # degrada en silencio sin SDD_HOME / python3 / script. No hace exit: la deriva de
  # version puede coexistir como segundo aviso.
  if [ -n "$SDD_HOME" ] && command -v python3 >/dev/null 2>&1 \
     && [ -f "$SDD_HOME/scripts/sdd-init-detect.py" ]; then
    SPECIALIST_STATUS="$(python3 "$SDD_HOME/scripts/sdd-init-detect.py" specialist-status --root "$INIT_ROOT" 2>/dev/null || true)"
    if printf '%s' "$SPECIALIST_STATUS" | grep -q '"pending"[[:space:]]*:[[:space:]]*true'; then
      SPECIALIST_WF="$(printf '%s' "$SPECIALIST_STATUS" | grep -o '"specialist_workflow"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/' || true)"
      [ -z "$SPECIALIST_WF" ] && SPECIALIST_WF="wf-<stack>-init"
      echo "[SDD-PROTOCOL] specialist-init-pending — El init tecnico del stack de este proyecto ($SPECIALIST_WF) aun no se ha ejecutado (sin registro en .sdd/stack-runs.jsonl). NUNCA bloquea: ante una peticion de PRD/spec/design solo menciona en UNA linea que esta pendiente y atiende al usuario con normalidad. Antes de cualquier trabajo de stack (plan, tasks o implementacion) invoca $SPECIALIST_WF como precondicion, y solo entonces. No repitas el wizard de modo."
    fi
  fi

  # Deteccion de deriva de version (informativa, nunca bloquea): compara el
  # sello de la instalacion (.sdd/sdd-version.json) con el VERSION del
  # ecosistema. Solo avisa si ambos lados son legibles y difieren.
  if [ -n "$SDD_HOME" ] && [ -f "$SDD_HOME/VERSION" ] && [ -f "$INIT_ROOT/.sdd/sdd-version.json" ]; then
    ECO_VERSION="$(tr -d '[:space:]' < "$SDD_HOME/VERSION" 2>/dev/null || true)"
    ECO_COMMIT="$(git -C "$SDD_HOME" rev-parse --short HEAD 2>/dev/null || true)"
    PROJ_VERSION="$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$INIT_ROOT/.sdd/sdd-version.json" | head -1 | sed 's/.*"\([^"]*\)"$/\1/' || true)"
    PROJ_COMMIT="$(grep -o '"commit"[[:space:]]*:[[:space:]]*"[^"]*"' "$INIT_ROOT/.sdd/sdd-version.json" | head -1 | sed 's/.*"\([^"]*\)"$/\1/' || true)"
    if [ -n "$ECO_VERSION" ] && [ -n "$PROJ_VERSION" ]; then
      if [ "$ECO_VERSION" != "$PROJ_VERSION" ] || { [ -n "$ECO_COMMIT" ] && [ -n "$PROJ_COMMIT" ] && [ "$ECO_COMMIT" != "$PROJ_COMMIT" ]; }; then
        echo "[SDD-PROTOCOL] version-drift — La instalacion SDD de este proyecto es de la version $PROJ_VERSION+${PROJ_COMMIT:-?} y el ecosistema esta en $ECO_VERSION+${ECO_COMMIT:-?}. Es solo un aviso: menciona brevemente al usuario que, cuando le convenga, puede PEDIRTE que actualices el proyecto, y continua con su peticion con normalidad. NO le des el comando crudo (/wf-sdd-update): si lo pide, invoca tu el skill wf-sdd-update via Skill tool (asi evitas que lance el slash-command a secas, que pierde contexto e idioma). No actualices sin que lo pida."
      fi
    fi
  fi
  exit 0
fi

# 2. Modo ya decidido
if [ -n "$MODE_ROOT" ]; then
  MODE_JSON="$MODE_ROOT/.claude/sdd-mode.json"
  if grep -q '"mode"[[:space:]]*:[[:space:]]*"free"' "$MODE_JSON"; then
    exit 0
  fi
  if grep -q '"mode"[[:space:]]*:[[:space:]]*"sdd"' "$MODE_JSON"; then
    echo "[SDD-PROTOCOL] init-pending — Este proyecto esta marcado en modo SDD pero no tiene .sdd/project-init.json. Antes de atender la peticion del usuario, invoca el skill wf-project-init para completar la inicializacion. No repitas el wizard de modo."
    exit 0
  fi
fi

# 3. Sin decision de modo → pedir el wizard
cat <<'EOF'
[SDD-PROTOCOL] mode-undecided — Este proyecto no tiene decidido el modo de trabajo de Claude. Antes de atender la primera peticion del usuario, presenta el wizard de modo siguiendo el "Protocolo SDD de inicio de sesion" definido en el CLAUDE.md global (~/.claude/CLAUDE.md): pregunta con AskUserQuestion entre "Modo SDD" y "Modo libre", persiste la eleccion en .claude/sdd-mode.json y actua en consecuencia.
EOF
exit 0
