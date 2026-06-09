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

# 1. Proyecto SDD inicializado → verificar que el init esta completo
if [ -f .sdd/project-init.json ]; then
  # Extraer las fases declaradas. Parser primario: python3 (JSON real).
  # Fallback sin python3: extraccion textual del array. Ante JSON malformado,
  # PHASES_LIST queda vacia y no se inyecta nada (conservador: mejor no
  # disparar init-incomplete espurio en cada sesion).
  if command -v python3 >/dev/null 2>&1; then
    PHASES_LIST="$(python3 -c '
import json
try:
    with open(".sdd/project-init.json") as f:
        phases = json.load(f).get("phases", [])
    if isinstance(phases, list):
        print(" ".join(p for p in phases if isinstance(p, str)))
except Exception:
    pass
' 2>/dev/null || true)"
  else
    PHASES_LIST="$(tr -d '\n' < .sdd/project-init.json \
      | grep -o '"phases"[[:space:]]*:[[:space:]]*\[[^]]*\]' \
      | grep -o '"[a-z]*"' | tr -d '"' | grep -vx 'phases' | tr '\n' ' ' || true)"
  fi
  MISSING=""
  for f in prd spec design plan tasks; do
    case " $PHASES_LIST " in
      *" $f "*)
        # Layout actual: regla de fase en .claude/rules/sdd-<fase>.md
        # Layouts legacy: .claude/phases/<fase>.md y <fase>/.claude/CLAUDE.md
        [ -f ".claude/rules/sdd-$f.md" ] || [ -f ".claude/phases/$f.md" ] || [ -f "$f/.claude/CLAUDE.md" ] || MISSING="$MISSING $f"
        ;;
    esac
  done
  if [ -n "$MISSING" ]; then
    echo "[SDD-PROTOCOL] init-incomplete — Este proyecto declara las fases [$MISSING ] en .sdd/project-init.json pero no estan instaladas (falta .claude/phases/<fase>.md). Antes de atender la peticion del usuario, invoca el skill wf-project-init (opcion 'Completar / ampliar') para reparar la instalacion. No repitas el wizard de modo."
    exit 0
  fi

  # Deteccion de deriva de version (informativa, nunca bloquea): compara el
  # sello de la instalacion (.sdd/sdd-version.json) con el VERSION del
  # ecosistema. Solo avisa si ambos lados son legibles y difieren.
  if [ -n "$SDD_HOME" ] && [ -f "$SDD_HOME/VERSION" ] && [ -f .sdd/sdd-version.json ]; then
    ECO_VERSION="$(tr -d '[:space:]' < "$SDD_HOME/VERSION" 2>/dev/null || true)"
    ECO_COMMIT="$(git -C "$SDD_HOME" rev-parse --short HEAD 2>/dev/null || true)"
    PROJ_VERSION="$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' .sdd/sdd-version.json | head -1 | sed 's/.*"\([^"]*\)"$/\1/' || true)"
    PROJ_COMMIT="$(grep -o '"commit"[[:space:]]*:[[:space:]]*"[^"]*"' .sdd/sdd-version.json | head -1 | sed 's/.*"\([^"]*\)"$/\1/' || true)"
    if [ -n "$ECO_VERSION" ] && [ -n "$PROJ_VERSION" ]; then
      if [ "$ECO_VERSION" != "$PROJ_VERSION" ] || { [ -n "$ECO_COMMIT" ] && [ -n "$PROJ_COMMIT" ] && [ "$ECO_COMMIT" != "$PROJ_COMMIT" ]; }; then
        echo "[SDD-PROTOCOL] version-drift — La instalacion SDD de este proyecto es de la version $PROJ_VERSION+${PROJ_COMMIT:-?} y el ecosistema esta en $ECO_VERSION+${ECO_COMMIT:-?}. Es solo un aviso: menciona brevemente al usuario que puede actualizar con /wf-sdd-update cuando le convenga, y continua con su peticion con normalidad. No actualices sin que lo pida."
      fi
    fi
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
