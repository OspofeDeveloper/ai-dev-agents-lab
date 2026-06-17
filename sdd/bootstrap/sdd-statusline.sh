#!/usr/bin/env bash
# sdd-statusline.sh — segmento de status line con el modo SDD del proyecto.
#
# Uso:
#   sdd-statusline.sh [CWD]     # con CWD explícito (lo pasa una statusline propia, p. ej. statusline.py)
#   <json> | sdd-statusline.sh  # sin arg: lee el JSON de la status line por stdin y saca el cwd
#
# Imprime un segmento corto con color ANSI tenue, o NADA si SDD no aplica
# (proyecto sin decidir / fuera de un proyecto). Pensado para COMPONERSE con la
# statusline que ya tenga el usuario: imprime solo el segmento, sin separadores.
#
# Estados (find-up hasta la raíz git, mismo criterio que el hook de sesión):
#   .sdd/project-init.json     → SDD inicializado  → "⚙ SDD:<topology>"   (verde)
#   .claude/sdd-mode.json free → modo libre         → "⚙ SDD:libre"         (tenue)
#   .claude/sdd-mode.json sdd  → init sin completar → "⚙ SDD:init pendiente"(amarillo)
#
# NUNCA falla: siempre exit 0; ante cualquier error imprime nada (no debe poder
# romper la status line que lo invoca).

cwd="${1:-}"
if [ -z "$cwd" ]; then
  _json="$(cat 2>/dev/null)"
  cwd="$(printf '%s' "$_json" | sed -n 's/.*"current_dir"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
  [ -z "$cwd" ] && cwd="$(printf '%s' "$_json" | sed -n 's/.*"cwd"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
fi
[ -z "$cwd" ] && cwd="$PWD"
[ -d "$cwd" ] || exit 0

# Techo de la búsqueda: la raíz git (si la hay), si no el propio cwd.
top="$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null)"
ceil="${top:-$cwd}"

d="$cwd"; init=""; mode_file=""
while :; do
  [ -z "$init" ] && [ -f "$d/.sdd/project-init.json" ] && init="$d/.sdd/project-init.json"
  [ -z "$mode_file" ] && [ -f "$d/.claude/sdd-mode.json" ] && mode_file="$d/.claude/sdd-mode.json"
  [ -n "$init" ] && break
  [ "$d" = "$ceil" ] && break
  [ "$d" = "/" ] && break
  d="$(dirname "$d")"
done

esc=$'\033'
DIM="${esc}[2m"; GRN="${esc}[32m"; YEL="${esc}[33m"; RST="${esc}[0m"

# Extrae el valor (string) de una clave de primer nivel de un JSON plano.
_field() { sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" "$2" 2>/dev/null | head -1; }

if [ -n "$init" ]; then
  topo="$(_field topology "$init")"; [ -z "$topo" ] && topo="sdd"
  printf '%s⚙ SDD:%s%s' "$GRN" "$topo" "$RST"
elif [ -n "$mode_file" ]; then
  m="$(_field mode "$mode_file")"
  case "$m" in
    free) printf '%s⚙ SDD:libre%s' "$DIM" "$RST" ;;
    sdd)  printf '%s⚙ SDD:init pendiente%s' "$YEL" "$RST" ;;
  esac
fi
exit 0
