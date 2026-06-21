#!/usr/bin/env python3
# sdd-version: 0.37.0+3cdfd2d
"""Resolutor determinista de rutas de artefactos SDD (Fase 11.2a del ROADMAP).

La regla de ubicación de artefactos era una frase canónica recitada en ~20
SKILL.md ("el directorio que contiene `features/`", "subcarpeta de fase /
layout plano legacy", "el `Spec origen` relativo desde el _plan.md"). Cada copia
es una oportunidad de divergencia y un punto donde el modelo puede escribir en el
sitio equivocado o emitir un header de trazabilidad irresoluble. Este script la
hace ÚNICA y testeable: función pura de (kind, input, layout) → ruta.

Subsume tres puntos de la auditoría 11.2:
  C1  — dónde escribir un artefacto (modo `write`).
  C2  — emitir el `Spec origen`/`Plan origen` relativo correcto (modo `rel-from`).
  C4  — encontrar un artefacto preexistente en AMBOS layouts (modo `find`).

NO escribe nada: solo emite rutas (pseudo-función pura, como `sdd-next-id.py` o
`sdd-amend.py next-ref`). El workflow consume la ruta y escribe el artefacto.

Modelo de layout (la SSoT que antes vivía en prosa):
  - Una feature vive en `features/<nombre>/`. Dos layouts conviven:
      · subcarpeta de fase (nuevo):  features/<nombre>/<fase>/<nombre>_<suf>
      · plano legacy:                features/<nombre>/<nombre>_<suf>
  - La "raíz de artefactos" / "el directorio que contiene `features/`" es el
    padre de la carpeta de feature; ahí viven los artefactos de PRODUCTO
    (_discovery.md, _features.md, _readiness_report.md, DESIGN.md, DESIGN_BRIEF.md).
  - plan/tasks/qa/release/bugs son artefactos LOCALES en repos consumidores:
    con `--local-root <dir>` se colocan bajo <dir>/features/<nombre>/<fase>/ (el
    plan vive en ESTE repo, no junto al spec del SSoT).

Uso:
    sdd-resolve-path.py write <kind> <input_path> [--local-root <dir>]
        Emite la ruta canónica donde escribir un artefacto <kind> derivado de
        <input_path> (típicamente el spec). Respeta el layout de <input_path>.

    sdd-resolve-path.py find <kind> <input_path>
        Emite la ruta del artefacto <kind> existente buscando en AMBOS layouts
        (o en la raíz de producto para kinds de producto). Vacío si no existe.

    sdd-resolve-path.py rel-from <anchor_file> <target_file>
        Emite la ruta relativa que hay que ESCRIBIR DENTRO de <anchor_file> para
        apuntar a <target_file> (p. ej. el `Spec origen` de un plan).

    sdd-resolve-path.py kinds        # lista los kinds conocidos

Kinds de feature  (viven dentro de features/<nombre>/[<fase>/]):
    spec plan tasks qa-plan qa-report release bugs
    flows views ui-prompt design-discovery
Kinds de producto (viven en la raíz que contiene features/):
    discovery features-index readiness analysis design-doc design-brief

Exit codes:
    0 = OK (ruta emitida / encontrada)
    1 = error de uso (kind o argumentos inválidos)
    3 = (find) no existe el artefacto en ningún layout
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# fase de subcarpeta, sufijo de fichero
FEATURE_KINDS = {
    "spec": ("spec", "_spec.md"),
    "plan": ("plan", "_plan.md"),
    "tasks": ("tasks", "_tasks.md"),
    "qa-plan": ("tasks", "_qa_plan.md"),
    "qa-report": ("tasks", "_qa_report.md"),
    "release": ("tasks", "_release.md"),
    "bugs": ("tasks", "_bugs.md"),
    "flows": ("design", "_flows.md"),
    "views": ("design", "_views.md"),
    "ui-prompt": ("design", "_ui_prompt.md"),
    "design-discovery": ("design", "_design_discovery.md"),
}

# kind de producto → ("glob", patrón) para nombre derivado del PRD, o
#                      ("fixed", nombre) para nombre fijo.
PRODUCT_KINDS = {
    "discovery": ("glob", "*_discovery.md"),
    "features-index": ("glob", "*_features.md"),
    "readiness": ("glob", "*_readiness_report.md"),
    "analysis": ("glob", "*_analysis.md"),
    "design-doc": ("fixed", "DESIGN.md"),
    "design-brief": ("fixed", "DESIGN_BRIEF.md"),
}

PHASE_DIRS = {"spec", "plan", "tasks", "design"}

# Todos los sufijos conocidos, del más largo al más corto (para derivar el base
# del nombre de fichero cuando el input no está dentro de una feature).
_ALL_SUFFIXES = sorted(
    {suf for _, suf in FEATURE_KINDS.values()}
    | {"_discovery.md", "_features.md", "_readiness_report.md", "_analysis.md"},
    key=len,
    reverse=True,
)


def fail(msg: str) -> int:
    sys.stderr.write(f"ERROR: {msg}\n")
    return 1


def strip_suffix(name: str) -> str:
    """Quita el sufijo de artefacto conocido más largo de un nombre de fichero."""
    for suf in _ALL_SUFFIXES:
        if name.endswith(suf):
            return name[: -len(suf)]
    # sin sufijo conocido: quita solo la extensión .md
    return name[:-3] if name.endswith(".md") else name


def feature_context(input_path: Path):
    """Detecta la carpeta de feature, el nombre y el layout de un path.

    Devuelve (feature_dir | None, nombre, layout) donde layout ∈
    {"subfolder", "flat", "none"}. `feature_dir` es el ancestro
    `features/<nombre>/` más cercano; None si el path no cuelga de `features/`.
    """
    p = input_path
    feature_dir = None
    # El primer ancestro cuyo padre se llama "features" es la carpeta de feature.
    for ancestor in [p] + list(p.parents):
        parent = ancestor.parent
        if parent.name == "features":
            feature_dir = ancestor
            break

    if feature_dir is None:
        return None, strip_suffix(p.name), "none"

    nombre = feature_dir.name
    # Layout: ¿el input está directamente en la feature (plano) o en una
    # subcarpeta de fase (nuevo)?
    if p.parent == feature_dir:
        layout = "flat"
    elif p.parent.parent == feature_dir and p.parent.name in PHASE_DIRS:
        layout = "subfolder"
    else:
        # input más profundo de lo esperado (p. ej. un asset): trátalo como
        # subfolder respecto a la feature (caso conservador).
        layout = "subfolder"
    return feature_dir, nombre, layout


def product_root(input_path: Path) -> Path:
    """Raíz de artefactos de producto = el directorio que contiene `features/`."""
    feature_dir, _, _ = feature_context(input_path)
    if feature_dir is not None:
        # feature_dir = features/<nombre>; el dir que CONTIENE features/ es su
        # abuelo (features/<nombre> → features/ → raíz de producto).
        return feature_dir.parent.parent
    # input no está en una feature: si es un directorio, es la raíz; si es un
    # fichero, su directorio.
    return input_path if input_path.is_dir() else input_path.parent


def resolve_write(kind: str, input_path: Path, local_root: Path | None) -> Path:
    if kind not in FEATURE_KINDS:
        raise ValueError(
            f"`write` solo aplica a kinds de feature; '{kind}' no lo es "
            f"(¿artefacto de producto? esos no se resuelven por feature)"
        )
    phase, suffix = FEATURE_KINDS[kind]
    feature_dir, nombre, layout = feature_context(input_path)
    filename = f"{nombre}{suffix}"

    # Repo consumidor: el artefacto local vive en ESTE repo, siempre en
    # subcarpeta de fase, replicando el nombre de la feature del SSoT.
    if local_root is not None:
        return local_root / "features" / nombre / phase / filename

    if feature_dir is None:
        # Fuera de una feature: mismo directorio que el input, base + sufijo.
        return input_path.parent / filename
    if layout == "flat":
        return feature_dir / filename
    return feature_dir / phase / filename


def resolve_find(kind: str, input_path: Path) -> Path | None:
    if kind in FEATURE_KINDS:
        phase, suffix = FEATURE_KINDS[kind]
        feature_dir, nombre, _ = feature_context(input_path)
        if feature_dir is None:
            cand = input_path.parent / f"{nombre}{suffix}"
            return cand if cand.is_file() else None
        candidates = [
            feature_dir / phase / f"{nombre}{suffix}",  # subcarpeta
            feature_dir / f"{nombre}{suffix}",          # plano legacy
        ]
        for c in candidates:
            if c.is_file():
                return c
        return None

    if kind in PRODUCT_KINDS:
        root = product_root(input_path)
        mode, pat = PRODUCT_KINDS[kind]
        if mode == "fixed":
            cand = root / pat
            return cand if cand.is_file() else None
        matches = sorted(root.glob(pat))
        return matches[0] if matches else None

    raise ValueError(f"kind desconocido: '{kind}'")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="sdd-resolve-path.py", add_help=True, description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="mode")

    p_write = sub.add_parser("write", help="ruta canónica donde escribir")
    p_write.add_argument("kind")
    p_write.add_argument("input_path")
    p_write.add_argument("--local-root", default=None,
                         help="raíz del repo consumidor (plan/tasks viven aquí)")

    p_find = sub.add_parser("find", help="ruta de un artefacto existente")
    p_find.add_argument("kind")
    p_find.add_argument("input_path")

    p_rel = sub.add_parser("rel-from", help="ruta relativa a escribir dentro de un fichero")
    p_rel.add_argument("anchor_file")
    p_rel.add_argument("target_file")

    sub.add_parser("kinds", help="lista los kinds conocidos")

    try:
        ns = parser.parse_args(argv)
    except SystemExit:
        return 1

    if ns.mode is None:
        parser.print_help(sys.stderr)
        return 1

    if ns.mode == "kinds":
        print("feature:", " ".join(sorted(FEATURE_KINDS)))
        print("producto:", " ".join(sorted(PRODUCT_KINDS)))
        return 0

    if ns.mode == "rel-from":
        anchor = Path(ns.anchor_file)
        target = Path(ns.target_file)
        print(os.path.relpath(str(target), str(anchor.parent)))
        return 0

    if ns.mode == "write":
        try:
            out = resolve_write(
                ns.kind, Path(ns.input_path),
                Path(ns.local_root) if ns.local_root else None,
            )
        except ValueError as e:
            return fail(str(e))
        print(out.as_posix())
        return 0

    if ns.mode == "find":
        try:
            out = resolve_find(ns.kind, Path(ns.input_path))
        except ValueError as e:
            return fail(str(e))
        if out is None:
            return 3
        print(out.as_posix())
        return 0

    return fail(f"modo desconocido: {ns.mode}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
