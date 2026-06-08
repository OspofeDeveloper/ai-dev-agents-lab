#!/usr/bin/env python3
"""Informe PM read-only del estado del proyecto (ROADMAP 2.6).

El pipeline producía artefactos pero no tenía una vista que respondiera "¿en
qué punto está cada feature y qué falta?". Este script la genera de forma
DETERMINISTA escaneando `features/` y leyendo el estado que ya está sellado en
cada artefacto — no inventa nada ni razona: agrega. Como `wf-sdd-status`, es
recolección mecánica sin agente.

Ground truth = los artefactos en disco. Por cada feature determina la fase
alcanzada (por presencia de artefactos), el estado de esa fase (leído de su
header/tabla, no del README a mano), el bloqueo y la siguiente acción concreta.

Fuentes por feature (subcarpetas o layout plano legacy):
    spec/*_spec.md        estado del spec (vía _features.md o marcadores)
    plan/*_plan.md        Estado: BORRADOR|VALIDADO (lo sella sdd-seal.py) + enmienda
    tasks/*_tasks.md      tabla ## Progreso (la regenera sdd-task-state.py)
    tasks/*_qa_report.md  veredicto APTO|APTO_CON_RESERVAS|NO_APTO
    tasks/*_bugs.md       entradas B-00X (señal de mantenimiento)
Más `_features.md` (índice generado) para el estado de spec y las features
PENDIENTE_GENERACIÓN que aún no tienen carpeta.

Uso:
    sdd-project-status.py <dir>              # informe a stdout
    sdd-project-status.py <dir> --output <f> # además escribe el informe en <f>

<dir> es el directorio raíz de artefactos spec (contiene `features/` y
`_features.md`). Exit 0 siempre que pueda leer el directorio; 1 en error de uso.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FID_RE = re.compile(r"\bF-(?:C-)?\d+\b")
MARKER_RE = re.compile(r"\[(?:INCOMPLETO|CR[IÍ]TICO|INFERIDO)\]")
PLAN_ESTADO_RE = re.compile(
    r"^\s*(?:[-*>]\s*)?\**Estado:?\**\s*:?\s*(BORRADOR|VALIDADO)\b", re.MULTILINE
)
AMEND_RE = re.compile(r"\**Enmienda pendiente", re.IGNORECASE)
PROGRESO_ROW_RE = re.compile(
    r"^\|\s*(T-\d{3,4})\s*\|\s*(PENDIENTE|EN_CURSO|HECHA|BLOQUEADA)\s*\|", re.MULTILINE
)
BUG_RE = re.compile(r"^##\s+B-\d+\s*:", re.MULTILINE)

# Orden de fases (índice = "lo lejos que ha llegado")
PHASE_ORDER = ["PENDIENTE", "Spec", "Plan", "Tasks", "QA", "Cerrada"]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def first(directory: Path, *patterns: str) -> Path | None:
    for pat in patterns:
        matches = sorted(directory.glob(pat))
        if matches:
            return matches[0]
    return None


def fid_sort_key(fid: str):
    m = re.match(r"(F-(?:C-)?)(\d+)", fid)
    return (m.group(1), int(m.group(2))) if m else (fid, 0)


def header_field(text: str, key: str) -> str | None:
    m = re.search(r"^>\s*\**" + re.escape(key) + r"\**\s*:\s*(.*)$", text, re.MULTILINE)
    return m.group(1).strip().strip("`") if m else None


def section(text: str, title: str) -> str:
    m = re.search(
        r"^##\s+" + re.escape(title) + r"\s*$(.*?)(?=^##\s|\Z)",
        text, re.MULTILINE | re.DOTALL,
    )
    return m.group(1) if m else ""


def features_resumen(features_md: str) -> dict:
    """fid -> {estado, bloqueantes} desde el `## Resumen de estado` de _features.md."""
    out = {}
    for line in section(features_md, "Resumen de estado").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2 or all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        fm = FID_RE.search(cells[0])
        if fm and cells[1] in ("LISTA", "BLOQUEADA", "PENDIENTE_GENERACIÓN",
                               "REQUIERE_CAMBIO_PRD"):
            out[fm.group(0)] = {
                "estado": cells[1],
                "bloqueantes": cells[-1] if len(cells) >= 3 else "—",
                "name": cells[0].split(":", 1)[-1].strip() if ":" in cells[0] else "",
            }
    return out


def qa_verdict(text: str) -> str:
    for v in ("NO_APTO", "APTO_CON_RESERVAS", "APTO"):
        if v in text:
            return v
    return "?"


def analyze_feature(fdir: Path, resumen: dict) -> dict:
    """Determina fase, estado, bloqueo y siguiente acción de una feature en disco."""
    name = fdir.name
    spec = first(fdir, "spec/*_spec.md", "*_spec.md")
    plan = first(fdir, "plan/*_plan.md", "*_plan.md")
    tasks = first(fdir, "tasks/*_tasks.md", "*_tasks.md")
    qa = first(fdir, "tasks/*_qa_report.md", "*_qa_report.md")
    bugs = first(fdir, "tasks/*_bugs.md", "*_bugs.md")

    fid = None
    if spec:
        fid = header_field(read_text(spec), "Feature ID")
    if not fid:
        # intenta mapear por nombre contra el resumen
        for k, v in resumen.items():
            if v.get("name") == name:
                fid = k
                break
    fid = fid or name

    rmeta = resumen.get(fid, {})
    n_bugs = len(BUG_RE.findall(read_text(bugs))) if bugs else 0

    # ── QA alcanzada ──
    if qa:
        verdict = qa_verdict(read_text(qa))
        if verdict == "APTO":
            return _row(fid, name, "Cerrada", "QA: APTO", "—",
                        "✓ ciclo cerrado" + (f" · {n_bugs} bug(s)" if n_bugs else ""), n_bugs)
        if verdict == "APTO_CON_RESERVAS":
            return _row(fid, name, "QA", "APTO_CON_RESERVAS", "reservas (PARCIAL/MANUAL)",
                        "resolver reservas o aceptar", n_bugs)
        if verdict == "NO_APTO":
            return _row(fid, name, "QA", "NO_APTO", "CA sin cobertura o divergente",
                        "/wf-bug y re-verificar (/wf-qa-verify)", n_bugs)
        return _row(fid, name, "QA", "veredicto ?", "report ilegible",
                    "revisar _qa_report.md", n_bugs)

    # ── Tasks alcanzada ──
    if tasks:
        states = PROGRESO_ROW_RE.findall(read_text(tasks))
        total = len(states)
        done = sum(1 for _, st in states if st == "HECHA")
        blocked = sum(1 for _, st in states if st == "BLOQUEADA")
        if total == 0:
            return _row(fid, name, "Tasks", "sin progreso", "tabla ## Progreso vacía",
                        "/wf-task-run --next", n_bugs)
        prog = f"{done}/{total} HECHA"
        if done == total:
            return _row(fid, name, "Tasks", f"COMPLETO ({prog})", "—",
                        "/wf-qa-verify", n_bugs)
        bloqueo = f"{blocked} bloqueada(s)" if blocked else "en curso"
        return _row(fid, name, "Tasks", prog, bloqueo, "/wf-task-run --next", n_bugs)

    # ── Plan alcanzado ──
    if plan:
        ptext = read_text(plan)
        m = PLAN_ESTADO_RE.search(ptext)
        estado = m.group(1) if m else "?"
        amend = bool(AMEND_RE.search(ptext))
        if amend:
            return _row(fid, name, "Plan", f"{estado} · enmienda pendiente",
                        "CA enmendado sin cerrar", "cerrar enmienda / re-validar", n_bugs)
        if estado == "VALIDADO":
            return _row(fid, name, "Plan", "VALIDADO", "—", "/wf-prepare-tasks", n_bugs)
        return _row(fid, name, "Plan", estado, "sin validar", "/wf-plan-validate", n_bugs)

    # ── Solo Spec ──
    if spec:
        estado = rmeta.get("estado")
        if not estado:
            estado = "BLOQUEADA" if MARKER_RE.search(read_text(spec)) else "LISTA"
        if estado == "LISTA":
            return _row(fid, name, "Spec", "LISTA", "—", "/wf-prepare-plan", n_bugs)
        if estado == "BLOQUEADA":
            return _row(fid, name, "Spec", "BLOQUEADA",
                        rmeta.get("bloqueantes", "marcadores en el spec"),
                        "responder gaps + /wf-spec-gap-resolve", n_bugs)
        if estado == "REQUIERE_CAMBIO_PRD":
            return _row(fid, name, "Spec", "REQUIERE_CAMBIO_PRD",
                        "alcance derivado sin consolidar", "/wf-prd-change", n_bugs)
        return _row(fid, name, "Spec", estado, rmeta.get("bloqueantes", "—"), "—", n_bugs)

    return _row(fid, name, "Spec", "sin artefactos", "carpeta vacía",
                "/wf-spec-fast-track o /wf-spec-features-first", n_bugs)


def _row(fid, name, fase, estado, bloqueo, accion, n_bugs):
    return {"fid": fid, "name": name, "fase": fase, "estado": estado,
            "bloqueo": bloqueo or "—", "accion": accion, "bugs": n_bugs}


def build(directory: Path) -> str:
    features_md_path = first(directory, "*_features.md")
    resumen = features_resumen(read_text(features_md_path)) if features_md_path else {}
    project = directory.name
    if features_md_path:
        m = re.search(r"^#\s+Features Index:\s*(.*)$", read_text(features_md_path),
                      re.MULTILINE)
        if m:
            project = m.group(1).strip()

    rows = []
    features_dir = directory / "features"
    seen_fids = set()
    if features_dir.is_dir():
        for fdir in sorted(p for p in features_dir.iterdir() if p.is_dir()):
            row = analyze_feature(fdir, resumen)
            rows.append(row)
            seen_fids.add(row["fid"])

    # Features PENDIENTE_GENERACIÓN del índice que aún no tienen carpeta
    for fid, meta in resumen.items():
        if fid in seen_fids:
            continue
        if meta.get("estado") == "PENDIENTE_GENERACIÓN":
            rows.append(_row(fid, meta.get("name", ""), "PENDIENTE", "PENDIENTE_GENERACIÓN",
                             "sin spec", f"/wf-spec-features-first --features {fid}", 0))

    rows.sort(key=lambda r: fid_sort_key(r["fid"]))

    # Resumen
    by_phase = {p: 0 for p in PHASE_ORDER}
    for r in rows:
        by_phase[r["fase"]] = by_phase.get(r["fase"], 0) + 1
    total_bugs = sum(r["bugs"] for r in rows)

    out = []
    out.append(f"# Estado del proyecto: {project}")
    resumen_line = " · ".join(
        f"{by_phase[p]} {p.lower()}" for p in PHASE_ORDER if by_phase.get(p)
    )
    out.append(f"> {len(rows)} feature(s) — {resumen_line or 'sin features'}"
               + (f" · {total_bugs} bug(s) registrado(s)" if total_bugs else ""))
    out.append("> Informe generado por `sdd-project-status.py` (read-only, no edita nada).")
    out.append("")
    out.append("## Por feature")
    out.append("")
    out.append("| Feature | Fase | Estado | Bloqueo | Siguiente acción |")
    out.append("|---|---|---|---|---|")
    for r in rows:
        label = f"{r['fid']}: {r['name']}" if r["name"] else r["fid"]
        bug_note = f" · ⚠ {r['bugs']} bug(s)" if r["bugs"] else ""
        out.append(f"| {label} | {r['fase']} | {r['estado']} | {r['bloqueo']}{bug_note} "
                   f"| {r['accion']} |")
    out.append("")

    # Siguiente foco: features accionables que no están cerradas ni pendientes
    actionable = [r for r in rows if r["fase"] not in ("Cerrada", "PENDIENTE")]
    if actionable:
        out.append("## Siguiente foco")
        out.append("")
        for r in actionable:
            label = f"{r['fid']}: {r['name']}" if r["name"] else r["fid"]
            out.append(f"- **{label}** ({r['fase']}) → {r['accion']}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    out_idx = argv.index("--output") if "--output" in argv else -1
    out_file = argv[out_idx + 1] if 0 <= out_idx < len(argv) - 1 else None
    if out_file and out_file in args:
        args.remove(out_file)
    if len(args) != 1:
        sys.stderr.write("uso: sdd-project-status.py <dir> [--output <archivo>]\n")
        return 1
    directory = Path(args[0]).resolve()
    if not directory.is_dir():
        sys.stderr.write(f"[project-status] no es un directorio: {directory}\n")
        return 1

    report = build(directory)
    sys.stdout.write(report)
    if out_file:
        Path(out_file).write_text(report, encoding="utf-8")
        sys.stderr.write(f"[project-status] informe escrito en {out_file}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
