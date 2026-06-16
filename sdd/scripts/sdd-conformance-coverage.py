#!/usr/bin/env python3
"""Cobertura determinista de la bateria de conformance (ROADMAP de conformance).

Parsea la matriz "una fila por wf-*" de `conformance/ROADMAP.md` y produce, sin
razonamiento experto, la foto de cobertura: por fase y global, conteo por Estado,
ejes en hueco (🟡/❌) y progreso X/N. Es el nucleo mecanico de `wf-conformance-status`
(espejo de `generate-skill-registry.py` para `wf-sdd-status`).

NO escribe ROADMAP.md ni decide nada: solo lee la matriz y cuenta. La SSoT del
"que deberia pasar" sigue siendo el catalogo `casos-de-uso/cu-*.md`; la SSoT del
estado de cobertura es la propia matriz del ROADMAP, que este script agrega.

Uso:
    python3 sdd/scripts/sdd-conformance-coverage.py [--roadmap <path>] [--phase <fase>] [--json]

  --roadmap  ruta al ROADMAP de conformance (default: conformance/ROADMAP.md
             relativo a la raiz del ecosistema en que vive este script).
  --phase    filtra la salida a una fase (prd|spec|design|plan|tasks|meta|bootstrap).
  --json     salida estructurada para consumo programatico.

Salida por defecto: reporte legible por fase + resumen global con el contador X/N.
Exit 0 siempre que el ROADMAP sea parseable; exit 1 si no se encuentra/parsea.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SDD_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROADMAP = SDD_ROOT / "conformance" / "ROADMAP.md"

AXES = ["Happy", "Edge", "Harness", "Args OK"]
ESTADOS = ["PENDIENTE", "REVISADO", "CON-HUECOS", "COMPLETADO"]
PHASE_HEADER = re.compile(r"^##\s+Fase\s+([\w/]+)\s*\((\d+)\)", re.IGNORECASE)


def _cells(line: str) -> list[str]:
    """Celdas de una fila markdown `| a | b | ... |` ya trimadas.

    Respeta los pipes escapados `\\|` (literales dentro de una celda, p. ej. en
    `--light\\|--standard`): solo parte en pipes NO escapados y luego los
    desescapa. Sin esto, las celdas Args con `\\|` desplazan toda la fila.
    """
    inner = line.strip().strip("|")
    parts = re.split(r"(?<!\\)\|", inner)
    return [c.strip().replace("\\|", "|") for c in parts]


def _is_separator(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c)


def parse_roadmap(text: str) -> dict:
    """Devuelve {phases: [{name, declared, rows:[...]}], rows_total}."""
    phases: list[dict] = []
    current: dict | None = None
    header_cols: list[str] | None = None

    for raw in text.splitlines():
        m = PHASE_HEADER.match(raw)
        if m:
            current = {"name": m.group(1).lower(), "declared": int(m.group(2)), "rows": []}
            phases.append(current)
            header_cols = None
            continue
        if not raw.lstrip().startswith("|"):
            continue
        cells = _cells(raw)
        if not cells or _is_separator(cells):
            continue
        # Fila de cabecera de la tabla: primera celda == "Skill"
        if cells[0].lower() == "skill":
            header_cols = cells
            continue
        # Fila de datos: primera celda es un wf-*
        if current is not None and cells[0].startswith("wf-"):
            row = _row_from_cells(cells, header_cols)
            if row:
                current["rows"].append(row)

    rows_total = sum(len(p["rows"]) for p in phases)
    return {"phases": phases, "rows_total": rows_total}


def _row_from_cells(cells: list[str], header: list[str] | None) -> dict | None:
    # Indices canonicos si la cabecera coincide; si no, posicionales conocidos.
    idx = {
        "skill": 0,
        "happy": 4,
        "edge": 5,
        "harness": 6,
        "args": 7,
        "estado": 8,
        "huecos": 9,
    }
    if header:
        low = [h.lower() for h in header]
        def find(*names):
            for n in names:
                if n in low:
                    return low.index(n)
            return None
        idx = {
            "skill": find("skill") or 0,
            "happy": find("happy"),
            "edge": find("edge"),
            "harness": find("harness"),
            "args": find("args ok", "args"),
            "estado": find("estado"),
            "huecos": find("huecos detectados", "huecos"),
        }
    try:
        def get(k):
            i = idx.get(k)
            return cells[i] if i is not None and i < len(cells) else ""
        return {
            "skill": get("skill"),
            "happy": get("happy"),
            "edge": get("edge"),
            "harness": get("harness"),
            "args": get("args"),
            "estado": get("estado").upper(),
            "huecos": get("huecos"),
        }
    except Exception:
        return None


def _axis_gaps(row: dict) -> list[str]:
    gaps = []
    for axis, key in [("Happy", "happy"), ("Edge", "edge"), ("Harness", "harness"), ("Args OK", "args")]:
        v = row.get(key, "")
        if "❌" in v:
            gaps.append(f"{axis}:❌")
        elif "🟡" in v:
            gaps.append(f"{axis}:🟡")
    return gaps


def summarize(parsed: dict, phase_filter: str | None) -> dict:
    phases = parsed["phases"]
    if phase_filter:
        phases = [p for p in phases if p["name"] == phase_filter.lower()]

    estado_counts = {e: 0 for e in ESTADOS}
    gaps_by_axis = {a: 0 for a in AXES}
    phase_out = []
    total_rows = 0
    rows_with_gaps = []

    for p in phases:
        p_estado = {e: 0 for e in ESTADOS}
        for row in p["rows"]:
            total_rows += 1
            est = row["estado"]
            if est in estado_counts:
                estado_counts[est] += 1
                p_estado[est] += 1
            gaps = _axis_gaps(row)
            for g in gaps:
                axis = g.split(":")[0]
                gaps_by_axis[axis] = gaps_by_axis.get(axis, 0) + 1
            if gaps:
                rows_with_gaps.append({"skill": row["skill"], "gaps": gaps, "huecos": row["huecos"]})
        phase_out.append({
            "name": p["name"],
            "declared": p["declared"],
            "counted": len(p["rows"]),
            "estado": p_estado,
        })

    completadas = estado_counts["COMPLETADO"]
    revisadas_sin_huecos = estado_counts["REVISADO"]
    revisadas = completadas + revisadas_sin_huecos
    return {
        "total_rows": total_rows,
        "estado_counts": estado_counts,
        "revisadas": revisadas,
        "progreso": f"{revisadas}/{total_rows}",
        "gaps_by_axis": gaps_by_axis,
        "rows_with_gaps": rows_with_gaps,
        "phases": phase_out,
    }


def render(summary: dict, phase_filter: str | None) -> str:
    out = []
    out.append("# Cobertura de conformance (matriz del ROADMAP)")
    if phase_filter:
        out.append(f"Alcance: fase {phase_filter}")
    out.append("")
    out.append("## Por fase")
    for p in summary["phases"]:
        drift = "" if p["declared"] == p["counted"] else f"  ⚠ declaradas {p['declared']} ≠ contadas {p['counted']}"
        est = " · ".join(f"{e}:{p['estado'][e]}" for e in ESTADOS if p["estado"][e])
        out.append(f"- **{p['name']}** ({p['counted']}){drift}: {est or '—'}")
    out.append("")
    out.append("## Ejes en hueco")
    any_gap = False
    for a in AXES:
        n = summary["gaps_by_axis"].get(a, 0)
        if n:
            any_gap = True
            out.append(f"- {a}: {n}")
    if not any_gap:
        out.append("- ninguno (todos los ejes ✅ o —)")
    if summary["rows_with_gaps"]:
        out.append("")
        out.append("### Skills con ejes parciales/huecos")
        for r in summary["rows_with_gaps"]:
            out.append(f"- {r['skill']}: {', '.join(r['gaps'])} — {r['huecos'] or '—'}")
    out.append("")
    out.append("## Progreso")
    ec = summary["estado_counts"]
    out.append(
        f"**Revisadas: {summary['revisadas']} / {summary['total_rows']}** · "
        f"Completadas: {ec['COMPLETADO']} · Revisadas sin huecos: {ec['REVISADO']} · "
        f"Con huecos: {ec['CON-HUECOS']} · Pendientes: {ec['PENDIENTE']}"
    )
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Cobertura determinista de la bateria de conformance.")
    ap.add_argument("--roadmap", type=Path, default=DEFAULT_ROADMAP)
    ap.add_argument("--phase", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not args.roadmap.is_file():
        print(f"ERROR: no se encuentra el ROADMAP en {args.roadmap}", file=sys.stderr)
        return 1
    text = args.roadmap.read_text(encoding="utf-8")
    parsed = parse_roadmap(text)
    if parsed["rows_total"] == 0:
        print("ERROR: no se encontraron filas wf-* en la matriz del ROADMAP.", file=sys.stderr)
        return 1
    summary = summarize(parsed, args.phase)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(render(summary, args.phase))
    return 0


if __name__ == "__main__":
    sys.exit(main())
