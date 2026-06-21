#!/usr/bin/env python3
# sdd-version: 0.37.0+3cdfd2d
"""Resolución determinista `base ⊕ override` de artefactos de feature por design target (D-011 12.6).

La topología `design` (D-011) modela la divergencia por design target como
**base agnóstica + override per-view** (`kb-design-feature-artifacts` Regla 8):
`<feature>_views.md`/`_flows.md` son la base; `targets/<target>/<feature>_*.md`
contiene SOLO las secciones (vistas/flujos) que divergen. La resolución para un
consumidor es `base ⊕ override(target)`: por cada sección, si el target la
overridea gana completa; si no, hereda la base intacta.

Esta es la pieza DETERMINISTA de esa resolución (el contrato vive en la Regla 8;
aquí se ejecuta). Herramienta de PROYECTO: se distribuye a `.sdd/scripts/` (igual
que `sdd-resolve-path.py`), porque la resolución ocurre en proyectos (el repo de
diseño al generar, o un consumer al resolver su target).

Grano = sección `## ` de nivel 2 (una vista es `## Vista N: <Nombre>`, un flujo
`## Flujo N: <Nombre>`). El emparejamiento base↔override es por el **nombre**
estable de la sección (se ignora el ordinal `Vista N:` / `Flujo N:`), así renumerar
las vistas no rompe la resolución. La sección de preámbulo/convención (texto antes
del primer `## `) se conserva de la base.

Subcomando:
    resolve --base <path> [--override <path>] [--merged]
        Sin `--merged` (default): emite (JSON) el MANIFIESTO de resolución —
        por sección, su `source` (base|override), y las listas `overridden`,
        `inherited`, `override_only`, más `has_override`.
        Con `--merged`: emite a stdout el documento markdown RESUELTO (base con las
        secciones overrideadas sustituidas y las override-only añadidas).
        Si `--override` se omite o el fichero no existe → no hay override: todo
        hereda la base (caso "target sin override → base intacta").

Exit codes:
    0 = OK
    1 = error de uso (p. ej. `--base` ausente o ilegible)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Prefijo ordinal de una sección de artefacto de feature: "Vista 1: ", "Flujo 2: ".
# Se ignora para emparejar base↔override por el NOMBRE estable de la sección.
_ORDINAL_RE = re.compile(r"^\s*\w+\s+\d+\s*:\s*", re.UNICODE)


def fail(msg: str) -> int:
    sys.stderr.write(f"ERROR: {msg}\n")
    return 1


def _section_key(heading: str) -> str:
    """Clave estable de una sección: su nombre, sin el ordinal `Vista N:`/`Flujo N:`."""
    return _ORDINAL_RE.sub("", heading).strip().lower()


def _split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    """(preámbulo, [(heading, bloque)]) partiendo por encabezados `## ` de nivel 2.

    `heading` es el texto tras `## ` (sin el `#`). `bloque` es el encabezado + su
    contenido hasta el siguiente `## ` o EOF (con el `\n` final preservado).
    El preámbulo es todo lo anterior al primer `## ` (título, `> Spec origen`, intro).
    """
    lines = text.splitlines(keepends=True)
    preamble: list[str] = []
    sections: list[tuple[str, str]] = []
    cur_heading: str | None = None
    cur_body: list[str] = []

    def _flush() -> None:
        if cur_heading is not None:
            sections.append((cur_heading, "".join(cur_body)))

    for line in lines:
        # `## ` de nivel 2 exacto (no `###`).
        if re.match(r"^##\s+(?!#)", line):
            _flush()
            cur_heading = line.lstrip("#").strip()
            cur_body = [line]
        elif cur_heading is None:
            preamble.append(line)
        else:
            cur_body.append(line)
    _flush()
    return "".join(preamble), sections


def resolve(base_path: Path, override_path: Path | None) -> dict:
    base_text = base_path.read_text(encoding="utf-8")
    base_pre, base_secs = _split_sections(base_text)

    has_override = bool(override_path and override_path.is_file())
    ov_secs: list[tuple[str, str]] = []
    if has_override:
        _, ov_secs = _split_sections(override_path.read_text(encoding="utf-8"))
    ov_by_key = {_section_key(h): (h, body) for h, body in ov_secs}

    resolved: list[dict] = []
    merged_blocks: list[str] = []
    overridden: list[str] = []
    inherited: list[str] = []
    base_keys = set()

    for heading, body in base_secs:
        key = _section_key(heading)
        base_keys.add(key)
        if key in ov_by_key:
            ov_heading, ov_body = ov_by_key[key]
            resolved.append({"heading": ov_heading, "source": "override"})
            merged_blocks.append(ov_body)
            overridden.append(ov_heading)
        else:
            resolved.append({"heading": heading, "source": "base"})
            merged_blocks.append(body)
            inherited.append(heading)

    override_only: list[str] = []
    for heading, body in ov_secs:
        if _section_key(heading) not in base_keys:
            resolved.append({"heading": heading, "source": "override"})
            merged_blocks.append(body)
            override_only.append(heading)

    return {
        "base": str(base_path),
        "override": str(override_path) if has_override else None,
        "has_override": has_override,
        "sections": resolved,
        "overridden": overridden,
        "inherited": inherited,
        "override_only": override_only,
        "_preamble": base_pre,
        "_merged_blocks": merged_blocks,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="sdd-design-resolve.py", add_help=True, description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="mode")
    p = sub.add_parser("resolve", help="base ⊕ override per-view de un artefacto de feature")
    p.add_argument("--base", required=True, help="ruta al artefacto base (agnóstico)")
    p.add_argument("--override", default=None, help="ruta al override del target (opcional)")
    p.add_argument("--merged", action="store_true", help="emite el markdown resuelto en vez del manifiesto JSON")

    try:
        ns = parser.parse_args(argv)
    except SystemExit:
        return 1

    if ns.mode != "resolve":
        parser.print_help(sys.stderr)
        return 1

    base_path = Path(ns.base)
    if not base_path.is_file():
        return fail(f"base no encontrada o ilegible: {ns.base}")
    override_path = Path(ns.override) if ns.override else None

    result = resolve(base_path, override_path)

    if ns.merged:
        out = result["_preamble"] + "".join(result["_merged_blocks"])
        sys.stdout.write(out)
        return 0

    # Manifiesto: oculta los campos internos (`_preamble`, `_merged_blocks`).
    manifest = {k: v for k, v in result.items() if not k.startswith("_")}
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
