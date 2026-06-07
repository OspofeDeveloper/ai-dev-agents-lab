#!/usr/bin/env python3
"""Gate mecanico PreToolUse del pipeline SDD (Fase 1.1 del ROADMAP).

Se registra como hook PreToolUse (matcher: Skill) en el settings.json del
proyecto. Antes de que el orquestador invoque una wf-* con gate, verifica las
precondiciones POR CONTENIDO (no por existencia) y deniega la invocacion si
no se cumplen. Convierte los "obligatorio" de la prosa en bloqueos reales.

Protocolo: recibe el JSON del hook por stdin; si el gate falla, emite el JSON
de decision `permissionDecision: deny` con motivo accionable y sale 0. Si todo
pasa (o no aplica), no emite nada y sale 0.

Politica conservadora: solo se bloquea con evidencia positiva de violacion.
Si los argumentos no permiten resolver el artefacto (path ausente/ambiguo),
se PERMITE — el gate es una red de seguridad, no un parser de toda sintaxis;
las validaciones de prosa del workflow siguen aplicando.

Gates (tabla GATES):
  wf-prepare-tasks            → el `*_plan.md` del arg debe tener `Estado: VALIDADO`
  wf-prepare-plan             → el `*_spec.md` del arg sin [INCOMPLETO]/[CRITICO] y status_sync fiable
  wf-design-system            → idem sobre el spec de entrada
  wf-design-feature-prototype → idem sobre el spec de entrada
  wf-task-run                 → el `Plan origen` del `*_tasks.md` sigue `Estado: VALIDADO`
"""
import json
import re
import sys
from pathlib import Path

ESTADO_RE = re.compile(
    r"^\s*(?:[-*>]\s*)?\**Estado:?\**\s*:?\s*(?P<value>BORRADOR|VALIDADO)\s*\**\s*$",
    re.MULTILINE,
)


def find_md_arg(args: str, marker: str):
    """Primer token .md cuyo nombre contiene el marcador (p. ej. '_plan')."""
    for token in re.findall(r"[^\s\"']+\.md", args or ""):
        if marker in Path(token).name:
            return Path(token)
    return None


def read(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def gate_plan_validado(args: str):
    plan_path = find_md_arg(args, "_plan")
    if plan_path is None:
        return None  # sin path resoluble → permitir (politica conservadora)
    text = read(plan_path)
    if text is None:
        return f"El plan '{plan_path}' no existe o no es legible. Genera el plan primero con /wf-prepare-plan generate <spec.md>."
    m = ESTADO_RE.search(text)
    if m is None:
        return f"'{plan_path}' no tiene linea `Estado:` reconocible — no parece un plan SDD sellable. Ejecuta /wf-plan-validate {plan_path} primero."
    if m.group("value") != "VALIDADO":
        return f"El plan '{plan_path}' esta en Estado: {m.group('value')}. Ejecuta /wf-plan-validate {plan_path} y resuelve sus hallazgos antes de generar tasks."
    return None


def gate_spec_fiable(args: str):
    # Nota: el DESIGN_BRIEF.md no se verifica aqui (su ubicacion es ambigua
    # desde los args); ese gate sigue siendo de la prosa del workflow.
    spec_path = find_md_arg(args, "_spec")
    if spec_path is None:
        return None
    text = read(spec_path)
    if text is None:
        return f"El spec '{spec_path}' no existe o no es legible."
    n_inc = len(re.findall(r"\[INCOMPLETO\]", text))
    if n_inc:
        return f"El spec '{spec_path}' tiene {n_inc} HU(s) [INCOMPLETO]. Resuelvelas con /wf-spec-gap-resolve antes de continuar."
    n_crit = len(re.findall(r"\[CR[IÍ]TICO\]", text))
    if n_crit:
        return f"El spec '{spec_path}' tiene {n_crit} gap(s) [CRITICO] abiertos. Resuelvelos antes de continuar."
    sync = re.search(r"status_sync\s*:\s*[\"']?(\w+)", text)
    if sync and sync.group(1) != "in_sync":
        return f"El spec '{spec_path}' declara status_sync: {sync.group(1)} (no fiable). Resincroniza con /wf-spec-sync-from-prd antes de continuar."
    return None


def gate_tasks_plan_vigente(args: str):
    """wf-task-run: el plan referenciado por `Plan origen` del _tasks.md sigue VALIDADO."""
    tasks_path = find_md_arg(args, "_tasks")
    if tasks_path is None:
        return None
    text = read(tasks_path)
    if text is None:
        return f"El tasks '{tasks_path}' no existe o no es legible. Generalo primero con /wf-prepare-tasks generate <plan.md>."
    m = re.search(r"Plan origen(?:\*\*)?\s*:?\**\s*`?(?P<path>[^`\s|]+)`?", text, re.IGNORECASE)
    if m is None:
        return None  # sin header resoluble → permitir (politica conservadora)
    plan_path = Path(m.group("path"))
    if not plan_path.is_absolute():
        plan_path = (tasks_path.parent / plan_path).resolve()
    plan_text = read(plan_path)
    if plan_text is None:
        return f"El `Plan origen` de '{tasks_path}' no resuelve ('{plan_path}'). Corrige el header antes de ejecutar tasks."
    pm = ESTADO_RE.search(plan_text)
    if pm and pm.group("value") != "VALIDADO":
        return (f"El plan origen '{plan_path}' esta en Estado: {pm.group('value')} — fue degradado tras generar las tasks. "
                f"Ejecuta /wf-plan-validate {plan_path} antes de ejecutar tasks.")
    return None


GATES = {
    "wf-prepare-tasks": gate_plan_validado,
    "wf-prepare-plan": gate_spec_fiable,
    "wf-design-system": gate_spec_fiable,
    "wf-design-feature-prototype": gate_spec_fiable,
    "wf-task-run": gate_tasks_plan_vigente,
}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # stdin ilegible → no interferir

    if payload.get("tool_name") != "Skill":
        return 0
    tool_input = payload.get("tool_input") or {}
    skill = (tool_input.get("skill") or "").strip()
    args = tool_input.get("args") or ""

    gate = GATES.get(skill)
    if gate is None:
        return 0

    try:
        reason = gate(args)
    except Exception:
        return 0  # error interno del gate → no bloquear el pipeline

    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"[SDD-GATE] {skill}: {reason}",
            }
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
