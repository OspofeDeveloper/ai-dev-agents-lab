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
        Además, `design_ssot` agrupa dos invariantes cross-repo de diseño (advisory):
        - `dual_design_ssot` (D-012): el consumer declara `design_source` Y su
          `artifacts_source` también trae diseño co-localizado → dos SSoT de diseño.
        - `design_target_coverage` (D-011/D-012): la familia de plataforma que el
          consumer consume (`design_targets`) no está entre las que autora el repo de
          diseño (`target_platforms` del `design_source`) → `gap: true` + `uncovered_families`.

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


def _read_json(path: Path):
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
    return None


def dual_design_ssot(root: Path) -> dict:
    """¿Más de un SSoT de diseño para el producto? (invariante D-012, advisory).

    Conflicto: el consumer declara `design_source` (el diseño vive en un repo de
    diseño aparte, 5.C1b) PERO su `artifacts_source` (el repo SSoT de specs/authoring)
    TAMBIÉN trae diseño co-localizado (su `project-init.json` declara la fase `design`).
    Son dos `DESIGN.md` candidatos para el mismo producto → viola la SSoT: `wf-prepare-plan`
    resuelve por `design_source` y el co-localizado queda compitiendo en silencio. Se
    AVISA, no se bloquea (puede ser una ventana de migración). El veredicto sale del
    estado declarado de los repos, no del agente.
    """
    obj = _read_json(root / ".sdd/project-init.json")
    if not isinstance(obj, dict):
        return {"design_source": None, "artifacts_source": None,
                "artifacts_source_declares_design": False, "dual_design_ssot": False}
    design_source = obj.get("design_source")
    artifacts_source = obj.get("artifacts_source")
    declares = False
    if design_source and artifacts_source:
        ssot = _read_json((root / artifacts_source / ".sdd/project-init.json").resolve())
        if isinstance(ssot, dict):
            phases = ssot.get("phases")
            in_phases = "design" in phases if isinstance(phases, list) else False
            declares = in_phases or ssot.get("design_role") in ("system", "full")
    return {
        "design_source": design_source,
        "artifacts_source": artifacts_source,
        "artifacts_source_declares_design": declares,
        "dual_design_ssot": bool(design_source and declares),
    }


def _family(label: str) -> str | None:
    """Familia de un design target (`<familia>[-<plataforma>][-<formfactor>]`): primer
    token antes del `-`. Net: la cobertura se mide por familia, no por etiqueta completa."""
    if not isinstance(label, str) or not label.strip():
        return None
    return label.split("-", 1)[0]


def design_target_coverage(root: Path) -> dict:
    """¿El repo de diseño cubre la familia de plataforma que consume el consumer?
    (cobertura cross-repo, advisory — hermano de `dual_design_ssot`, D-011/D-012).

    Un consumer con repo de diseño aparte (5.C1b) declara `design_source` + `design_targets`
    (los targets que consume, p. ej. `mobile-android`). El repo de diseño declara su
    `target_platforms` (familias que autora, p. ej. `["web"]`). Si la familia del consumer
    NO está entre las del repo de diseño, no hay bundles para su plataforma: al resolver
    heredará la base agnóstica (posiblemente sesgada a otra superficie). Se AVISA, no se
    bloquea (el repo de diseño puede ampliarse). El veredicto sale del estado declarado de
    ambos repos, no del agente. Si no podemos leer las familias del `design_source`, no se
    afirma un gap (`gap: false`, `source_target_platforms: null`)."""
    empty = {
        "design_targets": [],
        "consumer_families": [],
        "source_target_platforms": None,
        "uncovered_families": [],
        "gap": False,
    }
    obj = _read_json(root / ".sdd/project-init.json")
    if not isinstance(obj, dict):
        return empty
    design_source = obj.get("design_source")
    design_targets = obj.get("design_targets")
    if not design_source or not isinstance(design_targets, list) or not design_targets:
        return empty
    consumer_families = sorted({f for t in design_targets if (f := _family(t))})
    src = _read_json((root / design_source / ".sdd/project-init.json").resolve())
    source_platforms = src.get("target_platforms") if isinstance(src, dict) else None
    if not isinstance(source_platforms, list) or not source_platforms:
        # Sin las familias del repo de diseño no podemos afirmar un gap.
        return {**empty, "design_targets": design_targets,
                "consumer_families": consumer_families}
    uncovered = sorted(f for f in consumer_families if f not in source_platforms)
    return {
        "design_targets": design_targets,
        "consumer_families": consumer_families,
        "source_target_platforms": source_platforms,
        "uncovered_families": uncovered,
        "gap": bool(uncovered),
    }


def check(root: Path) -> dict:
    obj = _read_json(root / ".sdd/project-init.json")

    sources: list[dict] = []
    if isinstance(obj, dict):
        for path_key, pin_key, kind, tokens in SOURCES:
            path = obj.get(path_key)
            pin = obj.get(pin_key)
            if not path or not pin:
                continue
            src = (root / path).resolve()
            exists = src.exists()
            head = _git(src, "rev-parse", "--short", "HEAD") if exists else None
            git_ok = head is not None and pin != "unknown"
            drifted = bool(git_ok and head != pin)
            changed = _changed(src, pin, head, tokens) if drifted else []
            sources.append({
                "kind": kind,
                "path": path,
                "pin": pin,
                # `exists` distingue "la ruta no resuelve" (repo movido/borrado → re-apuntar
                # con /wf-project-init → Completar/ampliar) de "sin git" (git_ok:false con
                # exists:true): antes ambos colapsaban en git_ok:false, un fallo silencioso.
                "exists": exists,
                "head": head,
                "git_ok": git_ok,
                "drifted": drifted,
                "changed": changed,
            })

    return {
        "sources": sources,
        "any_drift": any(s["drifted"] for s in sources),
        # `any_missing`: alguna fuente pineada ya no resuelve en disco (ruta relativa rota
        # por mover un repo de forma independiente). Señal explícita para re-apuntar; los
        # workflows de plan la consumen como precondición advisory.
        "any_missing": any(not s["exists"] for s in sources),
        "design_ssot": {
            **dual_design_ssot(root),
            "design_target_coverage": design_target_coverage(root),
        },
    }


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
