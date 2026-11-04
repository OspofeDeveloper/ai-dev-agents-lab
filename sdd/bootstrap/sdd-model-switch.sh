#!/bin/bash
# Hook PreModelSwitch del ecosistema SDD (v0.128.8).
# En un proyecto SDD inicializado, cambiar la sesion a un modelo que no es Opus pide
# confirmacion: el orquestador del ecosistema esta medido con Opus, y con Sonnet se salto
# pasos de criterio en la regeneracion de CU-3.ac sin que nadie lo notara. No prohibe: quien
# quiera probar otro modelo lo confirma a sabiendas.
#
# "ask" solo es una pregunta en /model interactivo; en -p, /config o el SDK Claude Code lo
# trata como un rechazo. Por eso en CI/headless el hook no dice nada.
#
# Instalado por setup.sh en ~/.claude/hooks/sdd-model-switch.sh
set -u

if [ "${SDD_NON_INTERACTIVE:-}" = "1" ] || [ "${CI:-}" = "true" ]; then
  exit 0
fi
command -v python3 >/dev/null 2>&1 || exit 0

HOOK_INPUT=""
if [ ! -t 0 ]; then
  IFS= read -r -d '' -t 1 HOOK_INPUT || true
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
SDD_HOME="$(cat "$HOME/.sdd-home" 2>/dev/null || true)"

printf '%s' "$HOOK_INPUT" | PROJECT_DIR="$PROJECT_DIR" SDD_HOME="$SDD_HOME" python3 -c '
import json, os, subprocess, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
to_model = str(data.get("to_model") or "")
if not to_model or "opus" in to_model.lower():
    sys.exit(0)
project = os.path.realpath(data.get("cwd") or os.environ["PROJECT_DIR"])
home = os.path.realpath(os.path.expanduser("~"))
if project == home:
    sys.exit(0)
sdd_home = os.environ.get("SDD_HOME", "")
if sdd_home:
    def top(p):
        try:
            return subprocess.run(["git", "-C", p, "rev-parse", "--show-toplevel"],
                                  capture_output=True, text=True, timeout=5).stdout.strip()
        except Exception:
            return ""
    repo = top(sdd_home) or os.path.realpath(sdd_home)
    if (project + "/").startswith(os.path.realpath(repo) + "/"):
        sys.exit(0)    # el repo del ecosistema no es un proyecto SDD
# Como el hook de inicio: se busca .sdd/project-init.json hacia arriba hasta la raiz git.
techo = ""
try:
    techo = subprocess.run(["git", "-C", project, "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=5).stdout.strip()
except Exception:
    pass
techo = os.path.realpath(techo) if techo else project
d = project
while True:
    if os.path.isfile(os.path.join(d, ".sdd", "project-init.json")):
        break
    if d in (techo, "/"):
        sys.exit(0)
    d = os.path.dirname(d)
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreModelSwitch",
    "permissionDecision": "ask",
    "permissionDecisionReason": (
        f"Este es un proyecto SDD y vas a pasar a {to_model}. El orquestador del ecosistema "
        "esta medido con Opus: con otros modelos se salta pasos de criterio. ¿Cambias igualmente?"),
}}, ensure_ascii=False))
'
exit 0
