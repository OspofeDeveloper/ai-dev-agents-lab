#!/usr/bin/env python3
"""Hook PostToolUse del meta-repo: lint estructural al editar skills/agentes (11.4c).

Da feedback INMEDIATO al editar a mano un `*/SKILL.md` o `*/agents/*.md` del
ecosistema, sin esperar al gate de cierre de los workflows de creacion (11.4b)
ni a una auditoria manual (11.4a). Cubre el escenario real recurrente de este
repo: editar una pieza directamente cuando sdd-author no esta disponible.

Es ADVISORY (PostToolUse no puede deshacer la escritura): si la pieza recien
editada tiene findings BLOCKING del linter, los inyecta como `additionalContext`
para que el modelo los vea y corrija. Si esta limpia, no emite nada.

Se cablea en el workspace de desarrollo (`sdd/.claude/settings.json`) via
`setup.sh --dev` (matcher Write|Edit|MultiEdit). El script vive en
`sdd/scripts/` (committeado) y resuelve la raiz del ecosistema desde su propia
ubicacion — no depende de variables de entorno del proyecto.

Defensivo: cualquier fallo (stdin ilegible, sin python3 del linter, etc.) ->
exit 0 silencioso. Nunca estorba una edicion.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Raiz del ecosistema: por defecto, el arbol donde vive este script.
# SDD_META_LINT_ROOT permite apuntarlo a un arbol-fixture aislado en tests
# (retrocompatible: sin la variable, comportamiento de siempre).
SDD_ROOT = Path(os.environ.get("SDD_META_LINT_ROOT") or
                Path(__file__).resolve().parent.parent).resolve()
LINT = Path(__file__).resolve().parent / "sdd-structural-lint.py"

EDIT_TOOLS = {"Write", "Edit", "MultiEdit"}


def _is_skill_or_agent(rel_parts) -> bool:
    """rel_parts: partes de la ruta relativa a SDD_ROOT.
    Cuenta como pieza del ecosistema un SKILL.md bajo skills/ o un .md bajo agents/,
    excluyendo el mirror .claude/."""
    if ".claude" in rel_parts:
        return False
    if rel_parts and rel_parts[-1] == "SKILL.md" and "skills" in rel_parts:
        return True
    if "agents" in rel_parts and rel_parts[-1].endswith(".md"):
        return True
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") not in EDIT_TOOLS:
        return 0
    fp = ((payload.get("tool_input") or {}).get("file_path") or "").strip()
    if not fp:
        return 0

    try:
        edited = Path(fp).resolve()
        rel = edited.relative_to(SDD_ROOT)
    except Exception:
        return 0  # fuera del arbol del ecosistema

    if not _is_skill_or_agent(rel.parts):
        return 0

    if not LINT.exists():
        return 0
    try:
        proc = subprocess.run(
            [sys.executable, str(LINT), "--root", str(SDD_ROOT),
             "--json", "--severity", "blocking"],
            capture_output=True, text=True, timeout=30,
        )
        findings = json.loads(proc.stdout or "[]")
    except Exception:
        return 0

    rel_str = str(rel)
    mine = [f for f in findings if f.get("file") == rel_str]
    if not mine:
        return 0

    lines = [f"⚠ El archivo que acabas de editar (`{rel_str}`) tiene "
             f"{len(mine)} finding(s) estructural(es) BLOCKING del linter:"]
    for f in mine:
        lines.append(f"  - L{f.get('line')} [{f.get('type')}] {f.get('message')}")
    lines.append("Corrige antes de dar la pieza por buena. "
                 "Detalle: `python3 sdd/scripts/sdd-structural-lint.py --severity blocking`.")

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "\n".join(lines),
        }
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
