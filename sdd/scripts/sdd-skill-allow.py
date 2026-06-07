#!/usr/bin/env python3
"""Auto-allow acotado de Skills SDD (Fase 1.4 del ROADMAP).

Sustituye el auto-allow universal `Skill(.*)` (que aprobaba CUALQUIER skill,
incluidas las ajenas al ecosistema) por una aprobación acotada: solo las
workflows SDD (`wf-*`) se aprueban sin fricción. Cualquier otra skill sigue
el flujo normal de permisos del harness.

Se registra como hook PermissionRequest (matcher: Skill) en el settings.json
del proyecto. Emite la decisión `allow` SOLO si la skill invocada es una wf-*;
en cualquier otro caso no emite nada (el harness pregunta al usuario).

Nota de seguridad: los gates PreToolUse (sdd-gate-check.py) se evalúan ANTES
de la fase de permisos y un deny del gate prevalece — este allow no permite
saltarse fases del pipeline.
"""
import json
import re
import sys

# Workflows del ecosistema: prefijo wf- en kebab-case (kb-* no son invocables
# por el usuario y los agentes las cargan por frontmatter, no via Skill).
WF_SKILL_RE = re.compile(r"wf-[a-z0-9][a-z0-9-]*")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # stdin ilegible → no decidir (flujo normal de permisos)

    if payload.get("tool_name") != "Skill":
        return 0
    skill = ((payload.get("tool_input") or {}).get("skill") or "").strip()
    # Tolerar forma cualificada plugin:skill
    skill = skill.split(":")[-1]

    if WF_SKILL_RE.fullmatch(skill):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {"behavior": "allow"},
            }
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
