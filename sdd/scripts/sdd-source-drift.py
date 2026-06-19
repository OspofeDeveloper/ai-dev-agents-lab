#!/usr/bin/env python3
"""Detección determinista de drift de fuentes externas pineadas (D-011 12.5).

Un repo consumer pinea las fuentes de las que depende en `.sdd/project-init.json`:
`artifacts_source`+`artifacts_source_pin` (el repo SSoT de specs) y, si el diseño
vive aparte (D-011 5.C1b), `design_source`+`design_source_pin` (el repo `design`).
Este script compara cada pin con el `HEAD` actual de su checkout y, si difiere,
lista los artefactos relevantes que cambiaron entre el pin y HEAD — el subsistema
de staleness CROSS-REPO. Consolida en un script lo que antes era una comprobación
recitada en prosa por `wf-prepare-plan` (mismo criterio que el inventario 11.2).

Herramienta de PROYECTO: se distribuye a `.sdd/scripts/` (la comprobación corre en
el repo consumer). El veredicto es **advisory** (no bloquea): el SHA y el diff los
da git, no el agente.

Subcomando:
    check [--root <dir>]
        Lee `<root>/.sdd/project-init.json` y emite (JSON) una entrada por fuente
        externa pineada (`specs`, `design`): `pin`, `head`, `drifted`, `git_ok` y
        `changed` (artefactos relevantes cambiados `pin..HEAD`). `any_drift` resume.
        Repos sin fuentes externas (standalone/authoring/design) → `sources: []`.

Exit codes:
    0 = OK (siempre; es un reporte advisory)
    1 = error de uso
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Fuentes externas pineadas: (clave_path, clave_pin, kind, tokens_de_artefacto_relevante).
SOURCES = [
    ("artifacts_source", "artifacts_source_pin", "specs",
     ("_spec.md", "_features.md", "_discovery.md", "_analysis.md", "prd.md")),
    ("design_source", "design_source_pin", "design",
     ("DESIGN.md", "DESIGN_BRIEF.md", "_views.md", "_flows.md", "_ui_prompt", "tokens/")),
]


def fail(msg: str) -> int:
    sys.stderr.write(f"ERROR: {msg}\n")
    return 1


def _git(cwd: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True, text=True, check=True,
        )
        return r.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def _changed(src: Path, pin: str, head: str, tokens: tuple[str, ...]) -> list[str]:
    """Artefactos relevantes cambiados entre pin..HEAD (best-effort; [] si git falla)."""
    out = _git(src, "diff", "--name-only", f"{pin}..{head}")
    if out is None:
        return []
    files = [ln for ln in out.splitlines() if ln.strip()]
    return [f for f in files if any(tok in f for tok in tokens)]


def check(root: Path) -> dict:
    init_json = root / ".sdd/project-init.json"
    obj = None
    if init_json.is_file():
        try:
            obj = json.loads(init_json.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            obj = None

    sources: list[dict] = []
    if isinstance(obj, dict):
        for path_key, pin_key, kind, tokens in SOURCES:
            path = obj.get(path_key)
            pin = obj.get(pin_key)
            if not path or not pin:
                continue
            src = (root / path).resolve()
            head = _git(src, "rev-parse", "--short", "HEAD") if src.exists() else None
            git_ok = head is not None and pin != "unknown"
            drifted = bool(git_ok and head != pin)
            changed = _changed(src, pin, head, tokens) if drifted else []
            sources.append({
                "kind": kind,
                "path": path,
                "pin": pin,
                "head": head,
                "git_ok": git_ok,
                "drifted": drifted,
                "changed": changed,
            })

    return {"sources": sources, "any_drift": any(s["drifted"] for s in sources)}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="sdd-source-drift.py", add_help=True, description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="mode")
    p = sub.add_parser("check", help="drift de fuentes externas pineadas (specs/design)")
    p.add_argument("--root", default=None, help="raíz del repo consumer (default: cwd)")

    try:
        ns = parser.parse_args(argv)
    except SystemExit:
        return 1

    if ns.mode != "check":
        parser.print_help(sys.stderr)
        return 1

    root = Path(ns.root).resolve() if ns.root else Path.cwd()
    print(json.dumps(check(root), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
