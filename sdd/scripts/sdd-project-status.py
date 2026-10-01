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
    sdd-project-status.py <dir> --spec-pending [--json]
                                             # pendientes de la fase Spec, en orden (D-102)

<dir> es el directorio raíz de artefactos spec (contiene `features/` y
`_features.md`). Exit 0 siempre que pueda leer el directorio; 1 en error de uso.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FID_RE = re.compile(r"\bF-(?:C-)?\d+\b")
MARKER_RE = re.compile(r"\[(?:INCOMPLETO|CR[IÍ]TICO|INFERIDO)\]")
# Copia literal de `sdd-features-index.py::SIN_VALIDAR_MOTIVO` (D-077). Los dos
# scripts derivan el mismo estado desde fuentes distintas —el indice desde el spec,
# este desde el indice— y un test compara las dos cadenas.
SIN_VALIDAR_MOTIVO = "pendiente de validación (el spec sigue en BORRADOR)"
PLAN_ESTADO_RE = re.compile(
    r"^\s*(?:[-*>]\s*)?\**Estado:?\**\s*:?\s*(BORRADOR|VALIDADO)\b", re.MULTILINE
)
AMEND_RE = re.compile(r"\**Enmienda pendiente", re.IGNORECASE)
PROGRESO_ROW_RE = re.compile(
    r"^\|\s*(T-\d{3,4})\s*\|\s*(PENDIENTE|EN_CURSO|HECHA|BLOQUEADA)\s*\|", re.MULTILINE
)
BUG_RE = re.compile(r"^##\s+B-\d+\s*:", re.MULTILINE)
RELEASE_ENTRY_RE = re.compile(
    r"^##\s+R-(\d+)\b.*?(?=^##\s+R-|\Z)", re.MULTILINE | re.DOTALL
)
RELEASE_SHA_RE = re.compile(r"Commit/SHA:\**\s*`?[0-9a-f]+`?\s*\(`?([0-9a-f]+)`?\)")
RELEASE_TAG_RE = re.compile(r"Tag:\**\s*`([^`]+)`")

# Orden de fases (índice = "lo lejos que ha llegado")
PHASE_ORDER = ["PENDIENTE", "Spec", "Plan", "Tasks", "QA", "Cerrada", "Retirada"]


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
        # Los estados canonicos los define `sdd-features-index.py` (CANON_STATES);
        # esta tupla es su copia del lado lector y el test las compara ([[D-069]]).
        # Un estado fuera de ella no se pinta mal: la feature DESAPARECE del informe.
        if fm and cells[1] in ("LISTA", "BLOQUEADA", "PENDIENTE_GENERACIÓN",
                               "REQUIERE_CAMBIO_PRD", "RETIRADA"):
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


def release_coord(fdir: Path) -> str | None:
    """Coordenada del último release de la feature (tag o SHA corto), o None."""
    rel = first(fdir, "tasks/*_release.md", "*_release.md")
    if not rel:
        return None
    text = read_text(rel)
    entries = sorted(RELEASE_ENTRY_RE.finditer(text),
                     key=lambda m: int(m.group(1)), reverse=True)
    if not entries:
        return None
    block = entries[0].group(0)
    tag = RELEASE_TAG_RE.search(block)
    if tag:
        return tag.group(1)
    sha = RELEASE_SHA_RE.search(block)
    return sha.group(1) if sha else "registrado"


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

    # ── Dada de baja ([[D-074]]) ──
    # Va ANTES de la cascada de fases: una feature retirada suele tener plan o tasks
    # en disco, y la cascada la pintaria como si siguiera en marcha. No pide accion
    # y no entra en el siguiente foco — que es justo el punto de retirarla.
    estado_idx = rmeta.get("estado")
    retirada = estado_idx == "RETIRADA" or (
        spec and (header_field(read_text(spec), "Estado") or "").strip().upper() == "RETIRADO")
    if retirada:
        motivo = rmeta.get("bloqueantes") if estado_idx == "RETIRADA" else None
        if not motivo or motivo == "—":
            motivo = (header_field(read_text(spec), "Retirada") if spec else "") or "dada de baja"
        return _row(fid, name, "Retirada", "RETIRADA", motivo, "—", n_bugs)

    # ── QA alcanzada ──
    if qa:
        verdict = qa_verdict(read_text(qa))
        if verdict == "APTO":
            rel = release_coord(fdir)
            if rel:
                return _row(fid, name, "Cerrada", f"QA: APTO · release {rel}", "—",
                            "✓ entregado" + (f" · {n_bugs} bug(s)" if n_bugs else ""), n_bugs)
            return _row(fid, name, "Cerrada", "QA: APTO", "sin release",
                        "/wf-release" + (f" · {n_bugs} bug(s)" if n_bugs else ""), n_bugs)
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
        # El sello entra en el fallback igual que en `sdd-features-index.py::derive_state`
        # (D-077): `gate_spec_fiable` deniega el plan de un spec en BORRADOR (D-061), asi
        # que anunciar "LISTA → /wf-prepare-plan" manda al usuario contra el gate. Los
        # marcadores van primero: son el motivo mas concreto, y un spec con marcadores
        # abiertos tampoco se puede validar.
        spec_text = read_text(spec)
        sin_validar = (header_field(spec_text, "Estado") or "").strip().upper() == "BORRADOR"
        if not estado:
            if MARKER_RE.search(spec_text):
                estado = "BLOQUEADA"
            elif sin_validar:
                estado, rmeta = "BLOQUEADA", {**rmeta, "bloqueantes": SIN_VALIDAR_MOTIVO}
            else:
                estado = "LISTA"
        elif estado == "LISTA" and sin_validar:
            estado, rmeta = "BLOQUEADA", {**rmeta, "bloqueantes": SIN_VALIDAR_MOTIVO}
        if estado == "LISTA":
            return _row(fid, name, "Spec", "LISTA", "—", "/wf-prepare-plan", n_bugs)
        if estado == "BLOQUEADA":
            bloqueantes = rmeta.get("bloqueantes") or "marcadores en el spec"
            # La accion depende del motivo: mandar a "responder gaps" a quien solo tiene
            # el spec sin sellar es un callejon sin salida — no hay gap que responder.
            accion = ("/wf-spec-validate" if SIN_VALIDAR_MOTIVO.split(" (")[0] in bloqueantes
                      else "responder gaps + /wf-spec-gap-resolve")
            return _row(fid, name, "Spec", "BLOQUEADA", bloqueantes, accion, n_bugs)
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
    actionable = [r for r in rows if r["fase"] not in ("Cerrada", "PENDIENTE", "Retirada")]
    if actionable:
        out.append("## Siguiente foco")
        out.append("")
        for r in actionable:
            label = f"{r['fid']}: {r['name']}" if r["name"] else r["fid"]
            out.append(f"- **{label}** ({r['fase']}) → {r['accion']}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


# ───────────────────────── Pendientes de la fase Spec (D-102) ─────────────────────────
#
# `--spec-pending` responde "¿qué falta para que las specs se puedan planificar, y en
# qué orden?" leyendo SOLO ficheros, para que el hilo principal ofrezca el siguiente
# paso al cerrar cada flujo de Spec sin depender de lo que recuerde ni del
# «Próximos pasos» del readiness, que envejece en cuanto se toca un spec.
#
# Orden (el primero que aplica es el que se ofrece):
#   0 readiness desactualizado  → sus conflictos no son de fiar hasta rehacerlo
#   1 gaps críticos abiertos    (análisis y specs)
#   2 respuestas reabiertas     → specs escritos con la respuesta anterior
#   3 conflictos ALTA           (tabla arbitrada del readiness)
#   4 ciclos de dependencias    (`Requiere` de los READMEs, D-100) que NO respalda la
#                               tabla de shared models; los que sí respalda son grupos que
#                               se planifican juntos, un aviso y no un pendiente (D-103)
#   5 alcance derivado          sin formalizar ni aceptar (bloquea validar, D-102)
#   6 specs sin validar         (separa los listos de los que esperan a 1-4, D-103)
#   7 conflictos MEDIA          (informes de conflicto, sin arbitrar; no bloquean)
#   8 features sin generar

GAP_HEAD_RE = re.compile(r"^#{2,4}\s*\[(?P<id>P-\d+)\]\[(?P<sev>CR[IÍ]TICO|INFORMATIVO)\]",
                         re.MULTILINE)
PENDIENTE_TXT = "_(pendiente)_"
REOPENED_LINE_RE = re.compile(r"^\s*[-*+]\s*\**\s*Reabierto\s*\**\s*:\s*(\S+)", re.MULTILINE)
ESTADO_SPEC_RE = re.compile(r"^\s*(?:[-*>]\s*)?\**Estado:?\**\s*:?\s*(BORRADOR|VALIDADO|RETIRADO)\b",
                            re.MULTILINE)
SIN_AVISO = ("", "ninguno", "ninguna", "—", "-")


def _index_blocks(features_md: str) -> dict:
    """fid -> {name, ruta, estado, origen, avisos} desde los bloques `### F-XXX:` del índice."""
    out = {}
    for m in re.finditer(r"^###\s+(F-(?:C-)?\d+):\s*(.*?)\s*$(.*?)(?=^###\s|^##\s|\Z)",
                         features_md, re.MULTILINE | re.DOTALL):
        body = m.group(3)

        def field(label):
            fm = re.search(r"^-\s*\*\*" + re.escape(label) + r"\*\*\s*:\s*(.*)$", body, re.MULTILINE)
            return fm.group(1).strip() if fm else ""
        ruta = field("Ruta spec")
        out[m.group(1)] = {
            "name": m.group(2).strip(),
            "ruta": "" if ruta.startswith("(") else ruta,
            "estado": field("Estado"),
            "origen": field("Origen de alcance"),
            "avisos": field("Avisos de gobernanza"),
        }
    return out


def _table_rows(text: str, title: str) -> list[list[str]]:
    rows = []
    for line in section(text, title).splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= {"-", ":", " "} for c in cells) or cells[0].lower() in ("id", "feature"):
            continue
        rows.append(cells)
    return rows


def _gap_blocks(text: str):
    """[(id, severidad, respuesta, reabierto_ts, bloque)] de un análisis o un spec."""
    heads = list(GAP_HEAD_RE.finditer(text))
    out = []
    for n, m in enumerate(heads):
        end = heads[n + 1].start() if n + 1 < len(heads) else len(text)
        nxt = re.search(r"^#{1,4}\s", text[m.end():end], re.MULTILINE)
        block = text[m.end():m.end() + nxt.start()] if nxt else text[m.end():end]
        am = re.search(r"^\s*[-*+]\s*\**\s*Respuesta\s*\**\s*:\s*(.*)$", block, re.MULTILINE)
        rm = REOPENED_LINE_RE.search(block)
        sev = "CRÍTICO" if m.group("sev").upper().startswith("CR") else "INFORMATIVO"
        out.append((m.group("id"), sev, am.group(1).strip() if am else "",
                    rm.group(1) if rm else None, block))
    return out


def _mtime_iso(path: Path) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _shared_owners(features_md: str) -> dict:
    """owner_fid -> {fids que referencian algún modelo suyo}, desde la tabla de shared models."""
    out = {}
    for row in _table_rows(features_md, "Tabla de shared models"):
        if len(row) < 3:
            continue
        owner = FID_RE.findall(row[1])
        if owner:
            out.setdefault(owner[0], set()).update(FID_RE.findall(row[2]))
    return out


def _y(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " y " + items[-1]


def _cycles(graph: dict) -> list[list[str]]:
    """Componentes fuertemente conexos de tamaño > 1 (Tarjan)."""
    index, low, stack, on, out, counter = {}, {}, [], set(), [], [0]

    def strong(v):
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in graph.get(v, ()):
            if w not in graph:
                continue
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                out.append(sorted(comp, key=fid_sort_key))

    for v in sorted(graph, key=fid_sort_key):
        if v not in index:
            strong(v)
    return out


def spec_pending(directory: Path) -> dict:
    items = []

    def add(tipo, features, que, accion, via, bloquea=True, **extra):
        items.append({"tipo": tipo, "features": features, "que": que, "accion": accion,
                      "via": via, "bloquea_plan": bloquea, **extra})

    features_md_path = first(directory, "*_features.md")
    features_md = read_text(features_md_path) if features_md_path else ""
    idx = _index_blocks(features_md)
    label = {fid: f"{fid} ({m['name']})" if m["name"] else fid for fid, m in idx.items()}

    specs = {}   # fid -> Path
    for fid, meta in idx.items():
        if meta["ruta"]:
            sp = (directory / meta["ruta"]).resolve()
            if sp.is_file():
                specs[fid] = sp
    readmes = {}
    for fid, sp in specs.items():
        fdir = sp.parent.parent if sp.parent.name == "spec" else sp.parent
        if (fdir / "README.md").is_file():
            readmes[fid] = fdir / "README.md"

    # ── 0. Readiness ──
    readiness = first(directory, "*_readiness_report.md")
    rtext = read_text(readiness) if readiness else ""
    motivos = []
    if specs and not readiness:
        motivos.append("no hay informe de readiness")
    elif readiness:
        rmat = {r[0].split(":")[0].strip(): r for r in _table_rows(rtext, "Matriz de readiness")}
        viejas = [f for f in specs if f in rmat and "PENDIENTE" in rmat[f][1]]
        if viejas:
            motivos.append("da por generar features que ya tienen spec: " + ", ".join(viejas))
        rts = readiness.stat().st_mtime
        tocados = [f for f, sp in specs.items() if sp.stat().st_mtime > rts
                   and (m := ESTADO_SPEC_RE.search(read_text(sp))) and m.group(1) == "BORRADOR"]
        if tocados:
            motivos.append("specs modificados después del informe: " + ", ".join(tocados))
        reports = sorted(directory.glob("features/*/spec/*_conflict_report.md")) + \
            sorted(directory.glob("*_conflict_report.md"))
        if any(r.stat().st_mtime > rts for r in reports):
            motivos.append("hay informes de conflictos más nuevos que él")
    readiness_vigente = bool(readiness) and not motivos
    if motivos:
        add("readiness", sorted(specs, key=fid_sort_key),
            "El informe de readiness no refleja los specs actuales (" + "; ".join(motivos) + ").",
            "Rehacer la medición de readiness, que arbitra los conflictos y da el estado de cada feature.",
            "wf-spec-readiness", motivos=motivos)

    # ── 1. Gaps críticos abiertos y 2. respuestas reabiertas (análisis) ──
    disc = re.search(r"^>\s*Discovery:\s*`?([^`\n]+?)`?\s*(?:\(|$)", features_md, re.MULTILINE)
    analysis = None
    if disc:
        cand = (directory / disc.group(1).strip()).resolve()
        cand = cand.with_name(cand.name.replace("_discovery.md", "_analysis.md"))
        analysis = cand if cand.is_file() else None
    analysis = analysis or first(directory, "*_analysis.md")
    atext = read_text(analysis) if analysis else ""
    for gid, sev, resp, reab, _ in _gap_blocks(atext):
        if sev == "CRÍTICO" and resp in ("", PENDIENTE_TXT):
            add("gap_critico", [], f"La decisión {gid} del análisis sigue sin responder.",
                f"Responder {gid}; las historias que dependen de ella quedan incompletas hasta entonces.",
                "sdd-analysis-gaps --answer + wf-spec-gap-resolve", gap=gid)
        if reab:
            cita = re.compile(r"\b" + re.escape(gid) + r"\b")
            afectados = [f for f, sp in specs.items()
                         if cita.search(read_text(sp)) and _mtime_iso(sp) < reab]
            if afectados:
                add("reabierto", afectados,
                    f"La respuesta a {gid} cambió ({reab}) después de escribir "
                    + ", ".join(label[f] for f in afectados) + ".",
                    f"Revisar esos specs con la respuesta nueva de {gid}.",
                    "wf-spec-delta", gap=gid)
    for fid, sp in sorted(specs.items(), key=lambda kv: fid_sort_key(kv[0])):
        stext = read_text(sp)
        for gid, sev, resp, _, _ in _gap_blocks(stext):
            if sev == "CRÍTICO" and resp in ("", PENDIENTE_TXT):
                add("gap_critico", [fid], f"{label[fid]} tiene la decisión {gid} sin responder.",
                    f"Responder {gid}; sus historias incompletas se completan con la respuesta.",
                    "wf-spec-gap-resolve", gap=gid)

    # ── 3. Conflictos ALTA (arbitrados por el readiness) ──
    if rtext:
        for row in _table_rows(rtext, "Conflictos ALTA no resueltos"):
            fids = sorted(set(FID_RE.findall(" ".join(row[1:3]))), key=fid_sort_key)
            desc = row[3] if len(row) > 3 else ""
            add("conflicto_alta", fids,
                f"Conflicto {row[0]} entre " + " y ".join(label.get(f, f) for f in fids)
                + (f": {desc}" if desc else "") + ("" if readiness_vigente
                                                    else " (según el readiness anterior)"),
                "Elegir qué feature es la dueña; la otra se corrige y vuelve a validarse.",
                "elegir dueña → wf-spec-delta sobre la otra", conflicto=row[0],
                opciones=fids)

    # ── 4. Ciclos (Requiere de los READMEs) ──
    # Un ciclo es un grupo (componente fuerte), no un camino: se nombra por sus miembros y
    # nunca como cadena de flechas, que inventaría aristas que no existen (D-103). Si cada
    # dependencia del grupo la respalda un modelo compartido —B es dueña de un modelo que A
    # referencia—, el ciclo es del dominio (una cuenta necesita sus movimientos y un
    # movimiento su cuenta): no hay nada que quitar, se planifican juntas. Solo bloquea si
    # alguna dependencia no tiene ese respaldo, y entonces se nombra esa.
    graph = {}
    for fid, rd in readmes.items():
        req = re.search(r"^\s*-\s*\*\*Requiere\*\*\s*:\s*(.*)$", read_text(rd), re.MULTILINE)
        graph[fid] = [f for f in FID_RE.findall(req.group(1) if req else "") if f != fid]
    owners = _shared_owners(features_md)
    grupos = []
    for comp in _cycles(graph):
        nombres = _y([label.get(f, f) for f in comp])
        sueltas = [(a, b) for a in comp for b in graph.get(a, ())
                   if b in comp and a not in owners.get(b, set())]
        if not sueltas:
            grupos.append({"features": comp,
                           "que": f"{nombres} dependen unas de otras a través de sus modelos "
                                  "compartidos: se planifican juntas."})
            continue
        add("ciclo", comp,
            f"Dependencia circular entre {nombres}. Sin un modelo compartido que la respalde: "
            + "; ".join(f"{a} dice necesitar a {b} sin usar ningún modelo suyo"
                        for a, b in sueltas) + ".",
            "Revisar si esas dependencias hacen falta; la que sobre se quita de su spec.",
            "wf-spec-delta sobre la feature cuya dependencia sobra",
            opciones=[f"{a} → {b}" for a, b in sueltas])

    # ── 5. Alcance derivado y 6. specs sin validar ──
    derivadas, sin_validar = [], []
    for fid, sp in sorted(specs.items(), key=lambda kv: fid_sort_key(kv[0])):
        stext = read_text(sp)
        m = ESTADO_SPEC_RE.search(stext)
        if not m or m.group(1) != "BORRADOR":
            continue
        av = (header_field(stext, "Avisos de gobernanza") or "").strip("* ")
        aceptado = header_field(stext, "Alcance derivado aceptado")
        if av.lower() not in SIN_AVISO and not aceptado:
            derivadas.append(fid)
            add("alcance_derivado", [fid],
                f"{label[fid]} tiene alcance que solo existe en una respuesta del análisis ({av}).",
                "Formalizarlo en el PRD, o aceptarlo con nombre al validar el spec.",
                "wf-prd-change | wf-spec-validate --accept-derived-scope")
        sin_validar.append(fid)
    if sin_validar:
        # Validar un spec que aún tiene que cambiar es sellarlo para desellarlo: los que
        # esperan a un pendiente anterior que los toca se separan y no se ofrecen (D-103).
        motivo = {}
        for it in items:
            if it["tipo"] in ("gap_critico", "reabierto", "conflicto_alta", "ciclo"):
                que = {"gap_critico": f"pregunta {it.get('gap')}",
                       "reabierto": f"respuesta reabierta {it.get('gap')}",
                       "conflicto_alta": f"conflicto {it.get('conflicto')}",
                       "ciclo": "dependencia circular"}[it["tipo"]]
                for f in it["features"]:
                    motivo.setdefault(f, [])
                    if que not in motivo[f]:
                        motivo[f].append(que)
        listos = [f for f in sin_validar if f not in motivo]
        espera = [{"feature": f, "motivo": motivo[f]} for f in sin_validar if f in motivo]
        que = (f"{len(listos)} spec(s) en borrador listos para validar: "
               + ", ".join(label[f] for f in listos) + "." if listos
               else "Ningún spec en borrador está listo para validar todavía.")
        if espera:
            que += " Esperan a lo anterior: " + "; ".join(
                f"{label[e['feature']]} ({', '.join(e['motivo'])})" for e in espera) + "."
        add("validar", listos, que,
            "Validarlos (de uno en uno o todos juntos); sin sello no se pueden planificar.",
            "wf-spec-validate", derivadas=derivadas, en_espera=espera)

    # ── 7. Conflictos MEDIA: los que el readiness mantiene tras arbitrar ──
    # De su tabla «Conflictos MEDIA abiertos». Un readiness de antes de D-102 no la trae:
    # entonces se cae a los informes sueltos y se dice que no están arbitrados.
    if rtext and re.search(r"^##\s+Conflictos MEDIA abiertos", rtext, re.MULTILINE):
        for row in _table_rows(rtext, "Conflictos MEDIA abiertos"):
            fids = sorted(set(FID_RE.findall(" ".join(row[1:3]))), key=fid_sort_key)
            desc = row[3] if len(row) > 3 else ""
            add("conflicto_media", fids,
                f"Conflicto {row[0]} (media) entre " + " y ".join(label.get(f, f) for f in fids)
                + (f": {desc}" if desc else ""),
                "No bloquea; si el arreglo toca un spec ya validado, ese spec vuelve a validarse.",
                "elegir dueña → wf-spec-delta sobre la otra", bloquea=False, conflicto=row[0],
                opciones=fids)
    else:
        vistos = set()
        for rep in sorted(directory.glob("features/*/spec/*_conflict_report.md")):
            for row in _table_rows(read_text(rep), "Resumen de conflictos"):
                if len(row) >= 4 and row[2].upper().startswith("MEDIA") and row[0] not in vistos:
                    vistos.add(row[0])
                    fids = sorted(set(FID_RE.findall(row[3])), key=fid_sort_key)
                    add("conflicto_media", fids,
                        f"Conflicto {row[0]} (media) según el informe de {rep.parent.parent.name}, "
                        "sin arbitrar: el readiness no los recoge todavía.",
                        "Rehacer el readiness para confirmarlo antes de resolverlo.",
                        "wf-spec-readiness", bloquea=False, conflicto=row[0])

    # ── 8. Features sin generar ──
    pend = [f for f, meta in idx.items() if meta["estado"].startswith("PENDIENTE")]
    if pend:
        add("generar", sorted(pend, key=fid_sort_key),
            f"{len(pend)} feature(s) sin spec: " + ", ".join(label[f] for f in pend) + ".",
            "Generar sus specs cuando convenga.",
            "wf-spec-features-first --features", bloquea=False)

    orden = ["readiness", "gap_critico", "reabierto", "conflicto_alta", "ciclo",
             "alcance_derivado", "validar", "conflicto_media", "generar"]
    items.sort(key=lambda it: orden.index(it["tipo"]))
    for n, it in enumerate(items, 1):
        it["orden"] = n
    return {"total": len(items), "bloqueantes": sum(1 for i in items if i["bloquea_plan"]),
            "readiness_vigente": readiness_vigente, "items": items, "grupos": grupos}


def render_pending(data: dict) -> str:
    out = ["# Pendientes de la fase Spec", ""]
    notas = [f"> Nota (no es un pendiente): {g['que']}" for g in data.get("grupos", [])]
    if not data["items"]:
        out.append("Nada pendiente: todas las specs generadas están validadas y sin bloqueos.")
        return "\n".join(out + ([""] + notas if notas else [])) + "\n"
    out.append(f"{data['total']} pendiente(s), {data['bloqueantes']} de ellos impiden planificar. "
               "En orden:")
    out.append("")
    for it in data["items"]:
        marca = "" if it["bloquea_plan"] else " _(no bloquea)_"
        out.append(f"{it['orden']}. {it['que']}{marca}")
        out.append(f"   → {it['accion']}")
    if notas:
        out += [""] + notas
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    out_idx = argv.index("--output") if "--output" in argv else -1
    out_file = argv[out_idx + 1] if 0 <= out_idx < len(argv) - 1 else None
    if out_file and out_file in args:
        args.remove(out_file)
    if len(args) != 1:
        sys.stderr.write("uso: sdd-project-status.py <dir> [--output <archivo>] | "
                         "<dir> --spec-pending [--json]\n")
        return 1
    directory = Path(args[0]).resolve()
    if not directory.is_dir():
        sys.stderr.write(f"[project-status] no es un directorio: {directory}\n")
        return 1

    if "--spec-pending" in argv:
        data = spec_pending(directory)
        if "--json" in argv:
            import json
            sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        else:
            sys.stdout.write(render_pending(data))
        return 0

    report = build(directory)
    sys.stdout.write(report)
    if out_file:
        Path(out_file).write_text(report, encoding="utf-8")
        sys.stderr.write(f"[project-status] informe escrito en {out_file}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
