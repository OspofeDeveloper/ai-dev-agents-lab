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

import os
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


def _planificable(directory: Path) -> dict:
    """fid -> texto corto de si se puede planificar ya, desde el mapa de bloques (D-112)."""
    try:
        data = spec_pending(directory)
    except Exception:  # la vista de proyecto no se cae por un índice raro
        return {}
    bloque = {f: b["bloque"] for b in data.get("bloques", []) for f in b["features"]}
    textos = {"planificable": "sí", "lista_para_validar": "al validarla",
              "pendiente_corregir": "al corregirla y validarla",
              "pendiente_copiar": "al copiar lo ya decidido y validarla"}
    out = {}
    for f, v in data.get("por_feature", {}).items():
        e = v["estado_plan"]
        if e in textos:
            out[f] = textos[e]
        elif e == "pendiente_propio":
            out[f] = f"tras el bloque {bloque.get(f, '?')}"
        else:
            out[f] = "al final" if v.get("lectora") else "espera a otro bloque"
    return out


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
    # Si se puede planificar ya, por feature (D-112): una feature lista no espera a que el
    # resto del proyecto cierre sus decisiones.
    plan = _planificable(directory) if features_md_path else {}
    out.append("## Por feature")
    out.append("")
    out.append("| Feature | Fase | Estado | Planificable | Bloqueo | Siguiente acción |")
    out.append("|---|---|---|---|---|---|")
    for r in rows:
        label = f"{r['fid']}: {r['name']}" if r["name"] else r["fid"]
        bug_note = f" · ⚠ {r['bugs']} bug(s)" if r["bugs"] else ""
        out.append(f"| {label} | {r['fase']} | {r['estado']} | {plan.get(r['fid'], '—')} "
                   f"| {r['bloqueo']}{bug_note} | {r['accion']} |")
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


def _gap_title(text: str, gid: str) -> str:
    """El título de la cabecera `### [P-XXX][…] <título>` de un gap."""
    m = re.search(r"^#{2,4}\s*\[" + re.escape(gid) + r"\](?:\[[^\]]*\])*\s*(.*)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


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


DECISION_FIELD_RE = re.compile(r"^\s*[-*]\s*\*\*(Qué hay que decidir|Ejemplo|Afecta también a)\*\*\s*:\s*(.*)$",
                               re.MULTILINE)
OPCION_RE = re.compile(r"^\s*[-*]\s*\*\*Opción\s*\d+\s*[—–-]\s*(?P<titulo>[^*]+?)\*\*\s*:\s*"
                       r"(?P<efecto>.*?)\s*\*Cambia:\*\s*(?P<cambia>.*)$", re.MULTILINE)


def _decision(directory: Path, conflict_id: str) -> dict | None:
    """La `Decisión de producto` de un conflicto, del informe que lo describe (D-109).

    Se busca el bloque `### [CF-XXX]` en los informes de conflictos —por feature y
    consolidado— y se toma el más reciente que la traiga: es lo que el hilo principal
    presenta tal cual, en vez de preguntar qué documento manda."""
    for rep, block in _bloques_conflicto(directory, conflict_id):
            if "Decisión de producto" not in block:
                continue
            campos = {k: v.strip() for k, v in DECISION_FIELD_RE.findall(block)}
            opciones = [{"titulo": o["titulo"].strip(), "efecto": o["efecto"].strip().rstrip("."),
                         "cambia": sorted(set(FID_RE.findall(o["cambia"])), key=fid_sort_key)}
                        for o in OPCION_RE.finditer(block)]
            if opciones:
                # Las features que la decisión no cambia pero que leen algo que cambia
                # (D-112): esperan a ella sin entrar en su bloque.
                afecta = sorted(set(FID_RE.findall(campos.get("Afecta también a", ""))),
                                key=fid_sort_key)
                return {"que_decidir": campos.get("Qué hay que decidir", ""),
                        "ejemplo": campos.get("Ejemplo", ""), "opciones": opciones,
                        "afecta": afecta,
                        "informe": os.path.relpath(rep)}
    return None


def _bloques_conflicto(directory: Path, conflict_id: str):
    """Los bloques `### [CF-XXX]` de un conflicto, del informe más reciente al más antiguo.

    Los IDs se sacan con regex: el readiness escribe `` `CF-F001-03` (= `CF-F005-03`) ``, y
    partirlo por «/» dejaba las comillas y el alias dentro del ID, que no casaba con nada:
    ese conflicto salía siempre sin su decisión de producto (CU-3.ac)."""
    ids = list(dict.fromkeys(re.findall(r"CF-[\w]+(?:-[\w]+)*", conflict_id))) or [conflict_id]
    reports = sorted(list(directory.glob("features/*/spec/*_conflict_report.md"))
                     + list(directory.glob("*_conflict_report.md")),
                     key=lambda p: p.stat().st_mtime, reverse=True)
    for rep in reports:
        text = read_text(rep)
        for cid in ids:
            m = re.search(r"^###\s*\[" + re.escape(cid) + r"\][^\n]*\n(.*?)(?=^###\s|^##\s|\Z)",
                          text, re.MULTILINE | re.DOTALL)
            if m:
                yield rep, m.group(1)


UNICA_OPCION_RE = re.compile(r"^\s*[-*]\s*\*\*(?:Única opción|Opción única)\*\*\s*[—–:-]\s*"
                             r"\*Cambia:\*\s*(?P<cambia>.+)$", re.MULTILINE | re.IGNORECASE)
QUE_FALTA_RE = re.compile(r"^\s*[-*]\s*\*\*Qué falta (?:reflejar|copiar|añadir|escribir)[^*]*\*\*"
                          r"\s*:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
TRASLADO_FIELD_RE = re.compile(r"^\s*[-*]\s*\*\*(Qué|Decidido en|Falta en)\*\*\s*:\s*(.*)$",
                               re.MULTILINE)


def _traslado(directory: Path, conflict_id: str) -> dict | None:
    """Un conflicto que no es una decisión: el dueño ya decidió y otra feature no lo ha
    copiado (D-113), o el usuario ya respondió y la regla quedó fuera de su dueño (v0.127.1). El auditor lo marca con Causa «Sin trasladar» y un bloque «Traslado»;
    se aplica sin preguntar al usuario lo que ya respondió."""
    for rep, block in _bloques_conflicto(directory, conflict_id):
        # «Decidido fuera del dueño» (v0.127.1) es lo mismo visto desde el otro lado: lo
        # decidió el usuario, quedó en otra feature y lo recoge el dueño.
        if not re.search(r"\*\*Causa\*\*\s*:\s*\**\s*(?:Sin trasladar|Decidido fuera del due[ñn]o)",
                         block, re.IGNORECASE):
            continue
        campos = {k: v.strip() for k, v in TRASLADO_FIELD_RE.findall(block)}
        falta = sorted(set(FID_RE.findall(campos.get("Falta en", ""))), key=fid_sort_key)
        if campos.get("Qué") and falta:
            return {"que": campos["Qué"], "decidido_en":
                    sorted(set(FID_RE.findall(campos.get("Decidido en", ""))), key=fid_sort_key),
                    "falta_en": falta, "informe": os.path.relpath(rep)}
    # Una decisión de una sola opción no es una decisión (v0.127.1), pero la regla en prosa
    # no bastó: en CU-3.ac (3) el auditor reconoció el saldo negativo como ya decidido y aun
    # así lo escribió como «Decisión de producto» con «Única opción», y salió como decisión
    # menor. Lo determinista lo decide el script (v0.127.3): con una sola opción, se aplica.
    for rep, block in _bloques_conflicto(directory, conflict_id):
        if "Decisión de producto" not in block:
            continue
        unicas = [m.group("cambia") for m in UNICA_OPCION_RE.finditer(block)]
        opciones = [m.group("cambia") for m in OPCION_RE.finditer(block)]
        if len(unicas) + len(opciones) != 1:
            break
        cambia = (unicas + opciones)[0]
        # «F-001 (registro-movimientos) — añade esa frase, cerrando la referencia que F-005
        # ya le hace»: las features que cambian van antes de la raya; lo de después explica.
        falta = sorted(set(FID_RE.findall(re.split(r"\s+[—–]\s+", cambia, maxsplit=1)[0])),
                       key=fid_sort_key)
        que = QUE_FALTA_RE.search(block)
        texto = que.group(1).strip() if que else re.split(r"\s+[—–]\s+", cambia, maxsplit=1)[-1].strip()
        if falta and texto:
            return {"que": texto, "decidido_en": [], "falta_en": falta,
                    "informe": os.path.relpath(rep)}
        break
    return None


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


def _add_traslado(add, directory: Path, conflict_id: str, label: dict) -> bool:
    tr = _traslado(directory, conflict_id)
    if not tr:
        return False
    add("trasladar", tr["falta_en"],
        f"Ya decidido, falta copiarlo a " + " y ".join(label.get(f, f) for f in tr["falta_en"])
        + f": {tr['que']}",
        "Aplicarlo sin preguntar: la decisión ya está tomada; la feature vuelve a validarse.",
        "wf-spec-delta sobre cada feature donde falta", bloquea=False, conflicto=conflict_id,
        traslado=tr)
    return True


def spec_pending(directory: Path, lote: list | None = None) -> dict:
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
    motivos, conflictos_viejos, tocados = [], [], []
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
        # Un spec corregido después de su propio informe de conflictos: el readiness
        # que se rehiciera ahora leería ese informe viejo —que aún da el conflicto por
        # abierto— y no lo cerraría nunca. Primero sus conflictos, luego el readiness
        # (D-104).
        for f, sp in specs.items():
            rep = sp.with_name(sp.name.replace("_spec.md", "_conflict_report.md"))
            if (rep.is_file() and rep.stat().st_mtime < sp.stat().st_mtime
                    and (m := ESTADO_SPEC_RE.search(read_text(sp))) and m.group(1) == "BORRADOR"):
                conflictos_viejos.append(f)
        if conflictos_viejos:
            motivos.append("informe de conflictos anterior a su spec: " + ", ".join(conflictos_viejos))
        reports = sorted(directory.glob("features/*/spec/*_conflict_report.md")) + \
            sorted(directory.glob("*_conflict_report.md"))
        if any(r.stat().st_mtime > rts for r in reports):
            motivos.append("hay informes de conflictos más nuevos que él")
    readiness_vigente = bool(readiness) and not motivos
    estado_cf = _estado_conflictos(directory)
    cerrados_inc = _cerrados_incrementales(rtext)
    if motivos:
        cv = sorted(conflictos_viejos, key=fid_sort_key)
        add("readiness", sorted(specs, key=fid_sort_key),
            "El informe de readiness no refleja los specs actuales (" + "; ".join(motivos) + ").",
            ("Revisar de nuevo los conflictos de " + _y([label.get(f, f) for f in cv])
             + " y después rehacer la medición de readiness." if cv else
             "Rehacer la medición de readiness, que arbitra los conflictos y da el estado de cada feature."),
            ("wf-spec-conflict (por feature) → wf-spec-readiness" if cv else "wf-spec-readiness"),
            motivos=motivos, conflictos=cv, tocados=sorted(
                set(tocados) | set(conflictos_viejos), key=fid_sort_key))

    # ── 1. Gaps críticos abiertos y 2. respuestas reabiertas (análisis) ──
    disc = re.search(r"^>\s*Discovery:\s*`?([^`\n]+?)`?\s*(?:\(|$)", features_md, re.MULTILINE)
    analysis = None
    disc_path = (directory / disc.group(1).strip()).resolve() if disc else None
    if disc:
        cand = (directory / disc.group(1).strip()).resolve()
        cand = cand.with_name(cand.name.replace("_discovery.md", "_analysis.md"))
        analysis = cand if cand.is_file() else None
    analysis = analysis or first(directory, "*_analysis.md")
    atext = read_text(analysis) if analysis else ""
    for gid, sev, resp, reab, block in _gap_blocks(atext):
        if sev == "CRÍTICO" and resp in ("", PENDIENTE_TXT):
            add("gap_critico", [], f"La decisión {gid} del análisis sigue sin responder.",
                f"Responder {gid}; las historias que dependen de ella quedan incompletas hasta entonces.",
                "sdd-analysis-gaps --answer + wf-spec-gap-resolve", gap=gid,
                titulo=_gap_title(atext, gid),
                fichero=os.path.relpath(analysis) if analysis else "")
        if reab:
            # Un spec usa una respuesta del análisis si la cita o si la declara en su
            # cabecera (`Respuestas del análisis aplicadas`, copiada del discovery). Solo
            # la cita no basta: un escritor que aplica la respuesta sin nombrarla deja el
            # spec fuera de la lista, validado con la decisión retirada (D-104).
            # Y para los specs escritos antes de esa cabecera, el campo `Afecta` del
            # gap: nombra las features por su nombre ("deudas y reembolsos entre amigos").
            cita = re.compile(r"\b" + re.escape(gid) + r"\b")
            am = re.search(r"^\s*[-*+]\s*\**\s*Afecta\s*\**\s*:\s*(.*)$", block, re.MULTILINE)
            afecta = (am.group(1) if am else "").lower()

            def usa(f, sp):
                text = read_text(sp)
                nombre = idx.get(f, {}).get("name", "").replace("-", " ").lower()
                return (cita.search(header_field(text, "Respuestas del análisis aplicadas") or "")
                        or cita.search(text) or (nombre and nombre in afecta))
            afectados = sorted([f for f, sp in specs.items()
                                if _mtime_iso(sp) < reab and usa(f, sp)], key=fid_sort_key)
            mapa = disc_path and disc_path.is_file() and _mtime_iso(disc_path) < reab and cita.search(
                read_text(disc_path))
            if afectados or mapa:
                add("reabierto", afectados,
                    f"La respuesta a {gid} cambió ({reab}) después de escribir "
                    + (", ".join(label[f] for f in afectados) if afectados else "el mapa de features")
                    + (" y el mapa de features" if afectados and mapa else "") + ".",
                    f"Revisar esos specs con la respuesta nueva de {gid}."
                    + (" El mapa de features también la usa: las features que se generen después"
                       " partirán de él." if mapa else ""),
                    "wf-spec-delta", gap=gid, mapa=bool(mapa))
    for fid, sp in sorted(specs.items(), key=lambda kv: fid_sort_key(kv[0])):
        stext = read_text(sp)
        for gid, sev, resp, _, _ in _gap_blocks(stext):
            if sev == "CRÍTICO" and resp in ("", PENDIENTE_TXT):
                add("gap_critico", [fid], f"{label[fid]} tiene la decisión {gid} sin responder.",
                    f"Responder {gid}; sus historias incompletas se completan con la respuesta.",
                    "wf-spec-gap-resolve", gap=gid, titulo=_gap_title(stext, gid),
                    fichero=os.path.relpath(sp))

    # ── 2b. Contratos de modelos compartidos (D-111) ──
    # Una regla de un modelo compartido vive en su dueño. Lo que un consumidor
    # necesita y el dueño no recoge —una petición `R-NNN` o una operación que no
    # sale en su catálogo de orígenes— se resuelve en el DUEÑO: un cambio sobre
    # un solo spec, no un conflicto que arbitrar entre dos.
    contratos = _contracts_module()
    cdata = contratos.check(directory) if contratos else None
    if cdata:
        for p in cdata["sin_contrato"]:
            add("peticion", [p["owner"]], p["que"],
                f"Que {label.get(p['owner'], p['owner'])} publique el contrato de {p['modelo']}: "
                "qué puede hacer el usuario con él y qué otras features lo crean o cambian.",
                "wf-spec-delta sobre el dueño", owner=p["owner"], modelo=p["modelo"])
        for p in cdata["catalogo"]:
            add("peticion", sorted({p["owner"], p["consumidor"]}, key=fid_sort_key), p["que"],
                f"Decidir en {label.get(p['owner'], p['owner'])} cómo recoge su contrato esa "
                "operación —qué crea o cambia y qué puede hacer el usuario con ello—; se escribe "
                "solo en el dueño.",
                "wf-spec-delta sobre el dueño", owner=p["owner"], modelo=p["modelo"],
                consumidor=p["consumidor"])
        for p in cdata["peticiones"]:
            add("peticion", sorted({p["owner"], p["consumidor"]} - {""}, key=fid_sort_key),
                f"{p['que']} ({p['id']}).",
                f"Atenderla en {label.get(p['owner'], p['owner'] or 'el dueño')}: el cambio se "
                "escribe solo en el dueño y cita la petición en su catálogo de orígenes.",
                "wf-spec-delta sobre el dueño", owner=p["owner"], modelo=p["modelo"],
                consumidor=p["consumidor"], peticion=p["id"])

    # ── 3. Conflictos ALTA (arbitrados por el readiness) ──
    if rtext:
        filas_alta = _table_rows(rtext, "Conflictos ALTA no resueltos")
        for row in _sin_repetidos(filas_alta):
            if (_cerrado_despues(estado_cf, row[0], readiness.stat().st_mtime)
                    or set(CF_ID_RE.findall(row[0])) & cerrados_inc):
                continue
            fids = sorted(set(FID_RE.findall(" ".join(row[1:3]))), key=fid_sort_key)
            desc = row[3] if len(row) > 3 else ""
            if _add_traslado(add, directory, row[0], label):
                continue
            add("conflicto_alta", fids,
                f"Conflicto {row[0]} entre " + " y ".join(label.get(f, f) for f in fids)
                + (f": {desc}" if desc else "") + ("" if readiness_vigente
                                                    else " (según el readiness anterior)"),
                "Decidir cómo se comporta el producto; los specs que cambian se corrigen y vuelven a validarse.",
                "decisión de producto → wf-spec-delta sobre cada spec que cambia", conflicto=row[0],
                opciones=fids, decision=_decision(directory, row[0]))

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
    # Lo que los specs declaran usar también respalda una dependencia (D-111): si el índice
    # olvidó que presupuesto lee movimientos, el spec lo dice en «Modelos de otras features», y
    # sin esto ese olvido se convertía en un ciclo «sin respaldo» que bloqueaba (pasada 1 de
    # CU-3.ab). El hueco del índice ya sale como aviso aparte.
    for u in (cdata or {}).get("uso", []):
        owners.setdefault(u["owner"], set()).add(u["feature"])
    grupos = []
    for comp in _cycles(graph):
        nombres = _y([label.get(f, f) for f in comp])
        sueltas = [(a, b) for a in comp for b in graph.get(a, ())
                   if b in comp and a not in owners.get(b, set())]
        if not sueltas:
            grupos.append({"features": comp,
                           "que": f"{nombres} usan datos unas de otras: es lo normal y no "
                                  "frena a ninguna; al planificar, empieza por las que dan "
                                  "los datos."})
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
        # Lo que la validación pidió corregir (v0.127.1): no está lista para validar —
        # validarla otra vez volvería a fallar— sino para corregir. No es una decisión.
        bloqueo = header_field(stext, "La validación pide corregir") or ""
        vb = re.match(r"\(v([\d.]+)\)\s*", bloqueo)
        version = re.search(r"^>\s*\**Versi[oó]n\**\s*:\s*\**\s*(\d+(?:\.\d+)*)", stext,
                            re.MULTILINE)
        # Con la versión cambiada, el arreglo ya está aplicado: vuelve a «lista para validar».
        corregido = bool(vb and version and vb.group(1) != version.group(1))
        hallazgos = [] if corregido else [
            x.strip() for x in bloqueo[vb.end() if vb else 0:].split(" · ") if x.strip()]
        if hallazgos:
            add("corregir", [fid],
                f"{label[fid]}: la validación pide corregir: " + " · ".join(hallazgos),
                "Corregirlo con un cambio en el spec (el hallazgo literal es el requisito) y "
                "volver a validarlo; no hay nada que decidir.",
                "wf-spec-delta sobre el spec → wf-spec-validate", hallazgos=hallazgos)
            continue
        av = (header_field(stext, "Avisos de gobernanza") or "").strip("* ")
        aceptado = header_field(stext, "Alcance derivado aceptado")
        if av.lower() not in SIN_AVISO and not aceptado:
            derivadas.append(fid)
            add("alcance_derivado", [fid],
                f"{label[fid]} tiene alcance que solo existe en una respuesta del análisis ({av}).",
                "Formalizarlo en el PRD, o aceptarlo con nombre al validar el spec.",
                "wf-prd-change | wf-spec-validate --accept-derived-scope",
                pregunta=_pregunta_alcance(av))
        sin_validar.append(fid)
    if sin_validar:
        # Validar un spec que aún tiene que cambiar es sellarlo para desellarlo: los que
        # esperan a un pendiente anterior que los toca se separan y no se ofrecen (D-103).
        motivo = {}
        for it in items:
            if it["tipo"] in ("gap_critico", "peticion", "reabierto", "conflicto_alta", "ciclo"):
                que = {"gap_critico": f"pregunta {it.get('gap')}",
                       "peticion": f"contrato de {it.get('modelo')}",
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
    # Sin la tabla, un readiness al día no tiene MEDIA que arbitrar: su plantilla omitía la
    # sección cuando no había ninguno, y el cierre final de CU-3.ac (3) leyó entonces los
    # informes sueltos y recomendó «4 decisiones menores» ya resueltas (v0.128.0).
    if rtext and (readiness_vigente
                  and not re.search(r"^##\s+Conflictos MEDIA abiertos", rtext, re.MULTILINE)):
        pass
    elif rtext and re.search(r"^##\s+Conflictos MEDIA abiertos", rtext, re.MULTILINE):
        for row in _sin_repetidos(_table_rows(rtext, "Conflictos MEDIA abiertos")):
            if (_cerrado_despues(estado_cf, row[0], readiness.stat().st_mtime)
                    or set(CF_ID_RE.findall(row[0])) & cerrados_inc):
                continue
            fids = sorted(set(FID_RE.findall(" ".join(row[1:3]))), key=fid_sort_key)
            desc = row[3] if len(row) > 3 else ""
            if _add_traslado(add, directory, row[0], label):
                continue
            add("conflicto_media", fids,
                f"Conflicto {row[0]} (media) entre " + " y ".join(label.get(f, f) for f in fids)
                + (f": {desc}" if desc else ""),
                "No bloquea; si el arreglo toca un spec ya validado, ese spec vuelve a validarse.",
                "decisión de producto → wf-spec-delta sobre cada spec que cambia", bloquea=False,
                conflicto=row[0], opciones=fids, decision=_decision(directory, row[0]),
                descripcion=desc)
    else:
        vistos = set()
        raiz = estado_cf["__raiz__"]
        for rep in sorted(directory.glob("features/*/spec/*_conflict_report.md")):
            for row in _table_rows(read_text(rep), "Resumen de conflictos"):
                if len(row) >= 4 and row[2].upper().startswith("MEDIA") and row[0] not in vistos:
                    vistos.add(row[0])
                    # El informe más reciente manda, también por alias.
                    if not estado_cf.get(row[0], (True, 0))[0]:
                        continue
                    if raiz(row[0]) in {raiz(v) for v in vistos - {row[0]}}:
                        continue
                    fids = sorted(set(FID_RE.findall(row[3])), key=fid_sort_key)
                    add("conflicto_media", fids,
                        f"Conflicto {row[0]} (media) según el informe de {rep.parent.parent.name}, "
                        "sin arbitrar: el readiness no los recoge todavía.",
                        "Rehacer el readiness para confirmarlo antes de resolverlo.",
                        "wf-spec-readiness", bloquea=False, conflicto=row[0])

    # ── 7b. Sugerencias de la validación (v0.126.2) ──
    # Lo que un auditor vio con arreglo concreto y no bloquea; el sellador lo deja en la
    # cabecera. No frena el plan, pero se ve y se ofrece.
    for fid, sp in sorted(specs.items(), key=lambda kv: fid_sort_key(kv[0])):
        sug = header_field(read_text(sp), "Sugerencias de la validación")
        for x in [x.strip() for x in (sug or "").split(" · ") if x.strip()]:
            add("sugerencia", [fid], x,
                "Aplicarla con un cambio en el spec; la feature vuelve a validarse.",
                "wf-spec-delta sobre el spec", bloquea=False)

    # ── 8. Features sin generar ──
    pend = [f for f, meta in idx.items() if meta["estado"].startswith("PENDIENTE")]
    if pend:
        add("generar", sorted(pend, key=fid_sort_key),
            f"{len(pend)} feature(s) sin spec: " + ", ".join(label[f] for f in pend) + ".",
            "Generar sus specs cuando convenga.",
            "wf-spec-features-first --features", bloquea=False)

    # Lo ya decidido que falta copiar cambia el spec: validarlo antes es sellarlo para
    # desellarlo. CU-3.ac (3): presupuesto salía a la vez en «Validar las listas» y en
    # «Aplicar lo ya decidido», y validar iba primero.
    a_copiar = {f for i in items if i["tipo"] == "trasladar" for f in i["features"]}
    for it in items:
        if it["tipo"] != "validar" or not a_copiar & set(it["features"]):
            continue
        fuera = [f for f in it["features"] if f in a_copiar]
        it["features"] = [f for f in it["features"] if f not in a_copiar]
        it["en_espera"] += [{"feature": f, "motivo": ["falta copiar lo ya decidido"]}
                            for f in fuera]
        it["que"] = ((f"{len(it['features'])} spec(s) en borrador listos para validar: "
                      + ", ".join(label[f] for f in it["features"]) + ".")
                     if it["features"] else "Ningún spec en borrador está listo para validar "
                                            "todavía.")
        it["que"] += " Esperan a lo anterior: " + "; ".join(
            f"{label[e['feature']]} ({', '.join(e['motivo'])})" for e in it["en_espera"]) + "."

    orden = ["readiness", "gap_critico", "peticion", "reabierto", "conflicto_alta", "ciclo",
             "alcance_derivado", "corregir", "validar", "trasladar", "conflicto_media",
             "sugerencia", "generar"]
    items.sort(key=lambda it: orden.index(it["tipo"]))
    for n, it in enumerate(items, 1):
        it["orden"] = n
    bloq = sum(1 for i in items if i["bloquea_plan"])
    # La frase con que main abre el cierre, ya escrita para copiarla: el aviso de los
    # grupos como regla en prosa no salió en ninguno de 8 cierres (D-104, como la línea
    # de modo de D-101).
    # Un total suelto ("Quedan 6 pendientes") no dice de qué: mezcla preguntas, conflictos y
    # specs, y el lector lo toma por specs (D-110). Se dice qué es cada cosa, separando lo que
    # impide planificar de lo que no.
    bloqueantes = [i for i in items if i["bloquea_plan"]]
    resto = [i for i in items if not i["bloquea_plan"]]
    if not items:
        resumen = "No queda nada pendiente en Spec: se puede planificar."
    else:
        resumen = ("Para poder planificar falta: " + _y(_desglose(bloqueantes)) + "."
                   if bloqueantes else "Ya se puede planificar.")
        if resto:
            resumen += " Además, sin bloquear: " + _y(_desglose(resto)) + "."
    resumen += "".join(" " + g["que"] for g in grupos)
    # Con varias preguntas críticas, el mapa de lo que hay que tratar antes de tratar nada
    # (D-106): el usuario elige si las responde todas, las de unas features o de una en una.
    criticas = [{"gap": i["gap"], "features": i["features"], "titulo": i.get("titulo", ""),
                 "fichero": i.get("fichero", "")} for i in items if i["tipo"] == "gap_critico"]
    no_declaradas = cdata["no_declaradas"] if cdata else []
    mapa = _mapa(items, specs, label, cdata, readiness_vigente, lote,
                 titulos={f: _titulo(sp) for f, sp in specs.items()},
                 aprobador=_aprobador(directory))
    return {"total": len(items), "bloqueantes": bloq, "resumen": resumen,
            "dependencias_no_declaradas": no_declaradas, **mapa,
            "readiness_vigente": readiness_vigente, "items": items, "grupos": grupos,
            "preguntas_criticas": criticas}


# Lo que no es una decisión de nadie en concreto: la medición desactualizada nombra a todas
# las features, validar y generar son el paso siguiente, no lo que lo impide.
NO_DECISION = ("readiness", "validar", "generar", "corregir")


def _titulo(spec_path: Path) -> str:
    """El nombre de la feature como lo escribe su spec («# Spec: Visión General»), con sus
    tildes: el slug del índice («vision-general») salía en todos los cierres sin ellas."""
    m = re.search(r"^#\s+Spec:\s*(.+?)\s*$", read_text(spec_path), re.MULTILINE)
    if not m or FID_RE.fullmatch(m.group(1).strip()):
        return ""
    return " ".join(w if (w.isupper() and len(w) > 1) else w.lower() for w in m.group(1).split())


def _aprobador(directory: Path) -> str:
    """Quién aprobará lo que se valide desde el mapa: el `user.name` de git (D-027)."""
    import subprocess
    try:
        r = subprocess.run(["git", "config", "user.name"], cwd=directory, capture_output=True,
                           text=True, timeout=5)
        return r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _mapa(items: list, specs: dict, label: dict, cdata: dict | None,
          readiness_vigente: bool, lote: list | None = None, titulos: dict | None = None,
          aprobador: str = "") -> dict:
    """Qué se puede planificar ya y qué bloques de decisiones faltan para el resto (D-112).

    La lista plana decía «para poder planificar falta: …» del proyecto entero, y una feature
    sin nada pendiente esperaba a todas: en CU-3.ab, categorías estaba lista y no se podía
    planificar nada. El gate del plan siempre fue por feature; lo que bloqueaba era cómo se
    presentaba. Aquí cada feature dice si se puede planificar ya, y lo pendiente se agrupa
    en bloques: dos features van juntas solo si comparten una decisión. Leer algo que otro
    decide no las junta —la decisión lo dice en `Afecta también a`— y sale como espera.

    El texto lo lee un usuario final, no quien conoce el pipeline (v0.126.1): nombres de
    feature legibles, qué significa cada línea, y también lo que no frena nada —los
    conflictos menores y las features sin spec—, porque el mapa es «qué falta para
    cerrarlo todo», no solo «qué falta para empezar». La pregunta y sus opciones salen ya
    escritas: el preview que main tenía que componer no salió en ningún cierre.
    """
    decisiones = [i for i in items if i["bloquea_plan"] and i["tipo"] not in NO_DECISION]

    def cambia(it):
        # Las features que la decisión puede cambiar, de las opciones de su decisión de
        # producto; no las que solo menciona. Con un modelo central (movimientos) todo
        # conflicto lo nombra, y juntar por nombrar dejaba un único bloque con todo dentro:
        # el «todo o nada» de siempre (D-112).
        ops = (it.get("decision") or {}).get("opciones") or []
        fs = sorted({f for o in ops for f in o["cambia"]}, key=fid_sort_key)
        return [f for f in (fs or it["features"]) if f in specs]
    padre = {f: f for f in specs}

    def raiz(f):
        while padre[f] != f:
            padre[f] = padre[padre[f]]
            f = padre[f]
        return f
    for it in decisiones:
        fs = cambia(it)
        for f in fs[1:]:
            padre[raiz(f)] = raiz(fs[0])

    propios = {f: [i["orden"] for i in decisiones if f in cambia(i)] for f in specs}
    espera = {f: [] for f in specs}
    for it in decisiones:
        for f in (it.get("decision") or {}).get("afecta", []):
            if f in espera and f not in cambia(it) and it["orden"] not in espera[f]:
                espera[f].append(it["orden"])
    # Una feature que solo lee y lo hace de varias con decisiones abiertas (un resumen, un
    # panel) depende de todo lo demás: se planifica al final, no se la mete en un bloque.
    lectoras = set()
    usos = (cdata or {}).get("uso", [])
    con_decisiones = {f for f in specs if propios[f]}
    for f in specs:
        mios = [u for u in usos if u["feature"] == f]
        duenos = {u["owner"] for u in mios} & con_decisiones
        if not propios[f] and mios and not any(u["escribe"] for u in mios) and len(duenos) >= 3:
            lectoras.add(f)

    sellado = {f: bool((m := ESTADO_SPEC_RE.search(read_text(sp))) and m.group(1) == "VALIDADO")
               for f, sp in specs.items()}
    a_corregir = {f for i in items if i["tipo"] == "corregir" for f in i["features"]}
    a_copiar = {f for i in items if i["tipo"] == "trasladar" for f in i["features"]}
    por_feature = {}
    for f in sorted(specs, key=fid_sort_key):
        if propios[f]:
            estado = "pendiente_propio"
        elif f in a_corregir:
            estado = "pendiente_corregir"
        elif f in a_copiar and not sellado[f]:
            # Sellada, se sigue pudiendo planificar: el traslado la desella al aplicarse.
            estado = "pendiente_copiar"
        elif espera[f] or f in lectoras:
            estado = "espera_a_otro"
        else:
            estado = "planificable" if sellado[f] else "lista_para_validar"
        por_feature[f] = {"estado_plan": estado, "pendientes": propios[f], "espera": espera[f],
                          "lectora": f in lectoras}

    titulos = titulos or {}

    def nombre(f):
        # «presupuesto mensual (F-004)», no «F-004 (presupuesto-mensual)»: el usuario
        # reconoce la feature por su nombre; el ID va detrás, para quien lo busque.
        if titulos.get(f):
            return f"{titulos[f]} ({f})"
        m = re.match(r"(F-[\w-]+?) \((.+)\)$", label.get(f, f))
        return f"{m.group(2).replace('-', ' ')} ({m.group(1)})" if m else label.get(f, f)

    def nombres(fs):
        return _y([nombre(f) for f in fs])

    def corto(f):
        if titulos.get(f):
            return titulos[f]
        m = re.match(r"F-[\w-]+? \((.+)\)$", label.get(f, f))
        return m.group(1).replace("-", " ") if m else f

    grupos_b = {}
    for f in sorted(specs, key=fid_sort_key):
        if propios[f]:
            grupos_b.setdefault(raiz(f), []).append(f)
    ordenados = sorted(grupos_b.values(),
                       key=lambda fs: (len({o for f in fs for o in propios[f]}), fs[0]))
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    bloques, de_feature = [], {}
    for n, fs in enumerate(ordenados):
        for f in fs:
            de_feature[f] = letras[n % 26]
    por_orden = {i["orden"]: i for i in items}
    for n, fs in enumerate(ordenados):
        letra = letras[n % 26]
        mias = sorted({o for f in fs for o in propios[f]})
        fuera = sorted({o for f in fs for o in espera[f]} - set(mias))
        depende = sorted({de_feature[g] for o in fuera for g in cambia(por_orden[o])
                          if g in de_feature} - {letra})
        preview = ["Decisiones de este bloque:", ""]
        for k, o in enumerate(mias, 1):
            preview += _linea_decision(k, por_orden[o], [nombre(g) for g in cambia(por_orden[o])])
        tipos_b = {por_orden[o]["tipo"] for o in mias}
        if tipos_b <= {"alcance_derivado"}:
            pie = ["", "Basta con tu respuesta y validar: no hace falta cambiar ningún spec."]
        else:
            pie = ["", "Con todas las respuestas: un cambio por spec, una revisión de",
                   "conflictos y la validación del bloque. Después ya se pueden planificar."]
        preview += pie
        bloques.append({"bloque": letra, "features": fs, "decisiones": mias, "espera": fuera,
                        "depende_de": depende, "preview": "\n".join(preview)})

    menores = [i for i in items if i["tipo"] == "conflicto_media"]
    traslados = [i for i in items if i["tipo"] == "trasladar"]
    sugerencias = [i for i in items if i["tipo"] == "sugerencia"]
    sin_spec = [f for i in items if i["tipo"] == "generar" for f in i["features"]]

    corregir = [i for i in items if i["tipo"] == "corregir"]
    medir = next((i for i in items if i["tipo"] == "readiness"), None)
    lineas = []
    if not readiness_vigente:
        # «Puede cambiar lo que sigue» junto a «Ya puedes planificar» se leía como una
        # contradicción (v0.127.1): lo sellado se planifica igual; lo que se mueve es el resto.
        lineas.append("La medición de qué está listo es anterior a los últimos cambios: lo de "
                      "abajo puede moverse al rehacerla. Lo ya validado se puede planificar igual.")
        lineas.append("")
    ya = [f for f, v in por_feature.items() if v["estado_plan"] == "planificable"]
    validar = [f for f, v in por_feature.items() if v["estado_plan"] == "lista_para_validar"]
    if (not decisiones and not validar and not menores and not sin_spec and not traslados
            and not sugerencias and not corregir and readiness_vigente):
        lineas.append("Todo está cerrado: puedes planificar cualquier feature.")
    if ya:
        lineas.append(f"Ya puedes planificar: {nombres(ya)}.")
    if validar:
        lineas.append("Se pueden planificar en cuanto las valides (no les falta ninguna "
                      f"decisión): {nombres(validar)}.")
    if corregir:
        fs = [f for it in corregir for f in it["features"]]
        lineas.append(f"Falta corregir lo que vio la validación en {nombres(fs)}: no hay nada "
                      "que decidir; se corrige y se vuelve a validar.")
    if (ya or validar or corregir) and (decisiones or menores or traslados):
        lineas.append("Lo que quede abierto en otras features no les impide empezar.")
    if bloques:
        lineas.append("")
        lineas.append("Al resto le faltan decisiones. Van en bloques: cada bloque se trata de "
                      "una vez y no espera a los demás salvo que se diga:")
    for b in bloques:
        que = _y(_desglose([por_orden[o] for o in b["decisiones"]]))
        dep = (f" Además espera a {_n(len(b['espera']), 'decisión', 'decisiones')} del "
               + _y([f"bloque {d}" for d in b["depende_de"]])
               + ", que cambia algo que lee."
               if b["depende_de"] else " Solo depende de sí mismo.")
        lineas.append(f"- Bloque {b['bloque']} — {nombres(b['features'])}: falta {que}.{dep}")
    sueltas = [f for f, v in por_feature.items()
               if v["estado_plan"] == "espera_a_otro" and not v["lectora"]]
    for f in sueltas:
        de = sorted({de_feature[g] for o in espera[f] for g in cambia(por_orden[o])
                     if g in de_feature})
        lineas.append(f"- {nombre(f)}: no le falta nada propio, pero espera al "
                      + _y([f"bloque {d}" for d in de]) + ", que cambia algo que lee.")
    if lectoras:
        lineas.append(f"- Al final: {nombres(sorted(lectoras, key=fid_sort_key))}. Lee datos "
                      "de casi todas: conviene planificarla cuando las demás estén cerradas.")
    if traslados:
        lineas.append("")
        fs = sorted({f for it in traslados for f in it["features"]}, key=fid_sort_key)
        lineas.append(f"Ya decidido, falta copiarlo: {_n(len(traslados), 'cambio', 'cambios')} en "
                      f"{_y([corto(f) for f in fs])}. No hace falta que decidas nada: se aplica "
                      "lo que ya respondiste, y "
                      + ("esa feature vuelve" if len(fs) == 1 else "esas features vuelven")
                      + " a validarse.")
    if menores:
        lineas.append("")
        # Contadas por feature, no una a una: el detalle va en el preview de su opción. Cuatro
        # párrafos de huecos en la pregunta tapaban el resto del mapa.
        tocan = sorted({f for it in menores for f in (cambia(it) or it["features"])},
                       key=fid_sort_key)
        uno = len(menores) == 1
        lineas.append(f"Sin frenar nada, {'queda' if uno else 'quedan'} "
                      f"{_n(len(menores), 'decisión menor', 'decisiones menores')}, "
                      f"en {_y([corto(f) for f in tocan])}. "
                      + ("Puedes tomarla ahora o más adelante; si cambia una feature ya validada, "
                         if uno else "Puedes tomarlas ahora o más adelante; si una cambia una "
                         "feature ya validada, ")
                      + "esa feature vuelve a validarse.")
    if sugerencias:
        fs = sorted({f for it in sugerencias for f in it["features"]}, key=fid_sort_key)
        lineas.append("")
        lineas.append(f"La validación dejó {_n(len(sugerencias), 'sugerencia', 'sugerencias')} "
                      f"en {_y([corto(f) for f in fs])}: "
                      + ("no frena nada. Aplicarla" if len(sugerencias) == 1
                         else "no frenan nada. Aplicarlas")
                      + f" vuelve a validar {_y([corto(f) for f in fs])}, sin revisar "
                      "conflictos: son criterios que prueban reglas ya escritas.")
    if sin_spec:
        lineas.append("")
        lineas.append(f"Sin spec todavía: {nombres(sin_spec)}. No frena a las demás; se genera "
                      "cuando quieras.")

    # Las opciones del cierre, en orden y con su preview: caben 4, y la última es siempre
    # «Lo dejo para luego». Lo que no cabe se dice en la pregunta, para pedirlo con palabras.
    cand = []
    # Quién aprueba va en la opción (v0.128.0): elegir validar con el nombre delante es
    # aprobar lo que pase la auditoría, y no se pregunta después en cada lote. Sin nombre
    # de git, se pregunta como antes.
    sella = ([f"Si pasan la auditoría, quedan validadas a nombre de {aprobador}; si algo "
              "bloquea, se quedan en borrador y te digo qué."] if aprobador else
             ["Se te pregunta una vez quién aprueba. Las que pasen quedan listas para "
              "planificar."])
    if not readiness_vigente:
        prev = []
        tocados = (medir or {}).get("tocados") or []
        cv = (medir or {}).get("conflictos") or []
        if (medir or {}).get("motivos") == ["no hay informe de readiness"]:
            prev += ["Todavía no se ha medido qué está listo.", ""]
        elif tocados:
            prev += [f"Han cambiado después de la última medición: {nombres(tocados)}.", ""]
        else:
            prev += ["Hay cambios posteriores a la última medición.", ""]
        if cv:
            prev += [f"Primero se revisan los conflictos de {nombres(cv)}, y después se mide.",
                     ""]
        prev += ["Tarda unos minutos. Lo ya validado se puede planificar igual; si sale algo",
                 "nuevo, lo verás en el mapa."]
        cand.append({"label": "Rehacer la medición",
                     "description": "Mide otra vez qué está listo con los últimos cambios.",
                     "preview": "\n".join(prev), "accion": "readiness"})
    if validar:
        cand.append({"label": f"Validar las listas ({len(validar)})",
                     "description": (f"Se validan a nombre de {aprobador} si pasan la "
                                     "auditoría, y ya se pueden planificar."
                                     if aprobador else "Las sellas y ya se pueden planificar, "
                                     "aunque el resto siga abierto."),
                     "preview": "\n".join(["Se valida:" if len(validar) == 1 else "Se validan juntas:", ""]
                                          + [f"- {nombre(f)}" for f in validar]
                                          + [""] + sella),
                     "accion": "validar", "aprueba": aprobador})
    if corregir:
        prev = ["Lo que pidió corregir la validación (no se te pregunta nada):", ""]
        k = 0
        for it in corregir:
            for h in it["hallazgos"]:
                k += 1
                prev += [f"{k}. {nombre(it['features'][0])}: {h}"]
        prev += ["", "Se corrige cada spec, se comprueba que no choca con nada y se valida."] + sella
        cand.append({"label": f"Corregir lo que pidió la validación ({len(corregir)})",
                     "description": "Arreglos sin decisiones nuevas; después se valida otra vez.",
                     "preview": "\n".join(prev), "accion": "corregir", "aprueba": aprobador})
    if traslados:
        prev = ["Ya decidido, falta copiarlo (no se te pregunta nada):", ""]
        for k, it in enumerate(traslados, 1):
            tr = it["traslado"]
            prev += [f"{k}. {tr['que']}",
                     "   Falta en: " + _y([nombre(f) for f in tr["falta_en"]])
                     + ("; decidido en " + _y([nombre(f) for f in tr["decidido_en"]])
                        if tr["decidido_en"] else "")]
        prev += ["", "Se copian juntos, se comprueba que cierran lo que tenían que cerrar y se",
                 "validan."] + sella
        cand.append({"label": f"Aplicar lo ya decidido ({len(traslados)})",
                     "description": "Copia decisiones que ya tomaste a las features donde faltan.",
                     "preview": "\n".join(prev), "accion": "trasladar", "aprueba": aprobador})
    for b in bloques:
        n = len(b["decisiones"])
        cand.append({"label": f"Bloque {b['bloque']} — " + _y([corto(f) for f in b["features"]][:2])
                              + ("…" if len(b["features"]) > 2 else ""),
                     "description": _n(n, "decisión", "decisiones") + "; "
                                    + ("espera al " + _y([f"bloque {d}" for d in b["depende_de"]])
                                       if b["depende_de"] else "solo depende de sí mismo") + ".",
                     "preview": b["preview"], "accion": f"bloque:{b['bloque']}"})
    if menores:
        prev = ["Decisiones menores (no frenan nada):", ""]
        for k, it in enumerate(menores, 1):
            prev += _linea_decision(k, it, [nombre(g) for g in (cambia(it) or it["features"])])
        cand.append({"label": f"Decisiones menores ({len(menores)})",
                     "description": "No frenan nada; tomarlas ahora evita revalidar después.",
                     "preview": "\n".join(prev), "accion": "menores"})
    if sugerencias:
        prev = ["Sugerencias de la validación (no frenan nada):", ""]
        for k, it in enumerate(sugerencias, 1):
            prev += [f"{k}. {nombre(it['features'][0])}: {it['que']}"]
        prev += ["", "Se aplican, se auditan y se validan, sin revisar conflictos: son criterios",
                 "que prueban reglas ya escritas."] + sella
        cand.append({"label": f"Aplicar sugerencias ({len(sugerencias)})",
                     "description": "Pequeños arreglos que vio la validación.",
                     "preview": "\n".join(prev), "accion": "sugerencias", "aprueba": aprobador})
    if sin_spec:
        cand.append({"label": "Generar " + _y([corto(f) for f in sin_spec][:2])
                              + ("…" if len(sin_spec) > 2 else ""),
                     "description": "Crea su spec; no afecta a lo que ya está.",
                     "accion": "generar"})
    opciones = cand[:3]
    if opciones:
        opciones[0] = {**opciones[0], "label": opciones[0]["label"] + " (Recomendado)"}
    opciones.append({"label": "Lo dejo para luego",
                     "description": "Lo que ya está listo se puede planificar igualmente.",
                     "accion": "luego"})
    sobran = [c["label"] for c in cand[3:]]
    # Tras validar un lote, su resultado encabeza el cierre (v0.126.2): la tabla se
    # imprimía en una herramienta y main pasaba directo al mapa, sin enseñarla.
    cabeza = []
    if lote:
        sellador = _seal_module()
        if sellador:
            cabeza = sellador.lineas_lote(lote) + [""]
    pregunta = "\n".join(cabeza + lineas) + "\n\n¿Por dónde seguimos?" + (
        " (También puedes pedirme con tus palabras: "
        + _y([x[:1].lower() + x[1:] for x in sobran]) + ".)" if sobran else "")
    return {"por_feature": por_feature, "bloques": bloques, "mapa": "\n".join(lineas),
            "cierre": {"pregunta": pregunta, "opciones": opciones}}


def _pregunta_alcance(av: str) -> str:
    """El aviso de gobernanza («alcance derivado desde P-002; alcance derivado (deshacer un
    cobro…, decisión de producto sobre CF-…) decidido por el usuario…») como pregunta."""
    m = re.search(r"alcance derivado \(([^,)]+)", av)
    refs = sorted(set(re.findall(r"\b(?:P|CF)-[\w-]*\d", av)))
    que = f"«{m.group(1).strip()}»" if m else "lo que salió de tus respuestas"
    return (f"¿Das por bueno {que}? No está en el PRD: salió de tus respuestas"
            + (f" ({', '.join(refs)})" if refs else "")
            + ". Si lo aceptas, queda con tu nombre al validar; si no, se añade antes al PRD.")


def _pregunta(it: dict) -> str:
    """La decisión en una frase: la de su decisión de producto, o lo que dice el pendiente.

    Sin decisión de producto (un informe anterior a D-109), la descripción del readiness y
    no el `que`, que empieza por «Conflicto `CF-…` (media) entre F-001 (…)»: eso es para
    quien mantiene el pipeline, no para quien decide."""
    if it["tipo"] == "alcance_derivado":
        return it.get("pregunta") or it["que"]
    dec = it.get("decision") or {}
    que = dec.get("que_decidir") or it.get("descripcion") or it["que"]
    que = re.sub(r"\s+", " ", que.replace("`", "")).strip()
    # Sin recortar: la vista previa tiene sitio, y «…ni F-0…» a media palabra no se lee.
    return que[:1].upper() + que[1:]


def _linea_decision(k: int, it: dict, fs: list) -> list:
    """Una decisión de un bloque, para el `preview` de su opción."""
    ident = (it.get("conflicto") or it.get("peticion") or it.get("gap") or "").replace("`", "")
    out = [f"{k}. {_pregunta(it)}", "   Afecta a: " + (_y(fs) if fs else "—")]
    ops = [o["titulo"] for o in (it.get("decision") or {}).get("opciones", [])]
    if ops:
        out.append("   Opciones: " + " · ".join(ops))
    if ident:
        out.append(f"   ({ident})")
    return out


def _n(n: int, uno: str, varios: str) -> str:
    return f"{n} {uno if n == 1 else varios}"


def _desglose(items: list) -> list:
    """Qué es cada pendiente, contado por tipo y en el orden de la lista (D-110)."""
    cuenta = {}
    for it in items:
        if it["tipo"] == "validar":
            n = len(it["features"]) + len(it.get("en_espera", []))
        elif it["tipo"] == "generar":
            n = len(it["features"])
        else:
            n = 1
        cuenta[it["tipo"]] = cuenta.get(it["tipo"], 0) + n
    texto = {
        "readiness": lambda n: "volver a medir si las specs están listas",
        "gap_critico": lambda n: "responder " + _n(n, "pregunta", "preguntas"),
        "peticion": lambda n: "completar " + _n(n, "contrato de un modelo compartido",
                                                   "contratos de modelos compartidos"),
        "reabierto": lambda n: "revisar " + _n(n, "respuesta cambiada", "respuestas cambiadas"),
        "conflicto_alta": lambda n: "resolver " + _n(n, "conflicto grave", "conflictos graves"),
        "ciclo": lambda n: "romper " + _n(n, "dependencia circular", "dependencias circulares"),
        "alcance_derivado": lambda n: "decidir " + _n(n, "alcance que no está en el PRD",
                                                     "alcances que no están en el PRD"),
        "corregir": lambda n: "corregir " + _n(n, "spec que la validación frenó",
                                                "specs que la validación frenó"),
        "validar": lambda n: "validar " + _n(n, "spec", "specs"),
        "trasladar": lambda n: "aplicar " + _n(n, "decisión ya tomada", "decisiones ya tomadas"),
        "conflicto_media": lambda n: _n(n, "conflicto menor", "conflictos menores"),
        "sugerencia": lambda n: _n(n, "sugerencia de la validación",
                                   "sugerencias de la validación"),
        "generar": lambda n: _n(n, "feature sin spec", "features sin spec"),
    }
    return [texto[t](n) for t, n in cuenta.items()]


CF_ID_RE = re.compile(r"\bCF-[\w]+(?:-[\w]+)*?-\d+\b")
ALIAS_RE = re.compile(r"`?(CF-[\w]+(?:-[\w]+)*?-\d+)`?\s*\(?\s*=\s*`?(CF-[\w]+(?:-[\w]+)*?-\d+)`?")
CERRADO_RE = re.compile(r"resuelt|cerrad|descartad", re.IGNORECASE)


def _conflict_reports(directory: Path) -> list[Path]:
    return sorted(list(directory.glob("features/*/spec/*_conflict_report.md"))
                  + list(directory.glob("*_conflict_report.md")),
                  key=lambda p: p.stat().st_mtime)


def _estado_conflictos(directory: Path) -> dict:
    """ID de conflicto -> (abierto, mtime del informe que lo dice), con sus alias.

    Manda el informe más reciente que lo lista en su «Resumen de conflictos»: dos informes
    se contradicen por diseño (cada uno ve el choque desde su feature), y uno viejo sigue
    dándolo por abierto cuando el nuevo ya lo cerró. Los alias («`CF-F001-05` (= `CF-F005-04`)»)
    son el mismo conflicto: cerrar uno cierra el otro. CU-3.ac (3): el cierre final daba
    por abiertos cuatro conflictos resueltos, uno de ellos solo por su alias en un informe
    estancado.
    """
    padre = {}

    def raiz(x):
        while padre.setdefault(x, x) != x:
            x = padre[x]
        return x

    reports = _conflict_reports(directory)
    for rep in reports:
        for a, b in ALIAS_RE.findall(read_text(rep)):
            padre[raiz(a)] = raiz(b)
    estado = {}
    for rep in reports:      # del más viejo al más nuevo: el último que lo diga, manda
        mt = rep.stat().st_mtime
        for row in _table_rows(read_text(rep), "Resumen de conflictos"):
            ids = CF_ID_RE.findall(row[0])
            if not ids:
                continue
            # Sin columna Estado (informes anteriores) se da por abierto.
            abierto = not (len(row) >= 5 and CERRADO_RE.search(row[-1]))
            for cid in ids:
                estado[raiz(cid)] = (abierto, mt)
    return {cid: estado[raiz(cid)] for cid in set(padre) | set(estado)
            if raiz(cid) in estado} | {"__raiz__": raiz}


def _cerrado_despues(estado: dict, conflict_id: str, desde: float) -> bool:
    """Si algún informe posterior a `desde` da el conflicto (o un alias suyo) por cerrado."""
    for cid in CF_ID_RE.findall(conflict_id) or [conflict_id]:
        e = estado.get(cid) or estado.get(estado["__raiz__"](cid))
        if e and not e[0] and e[1] > desde:
            return True
    return False


def _sin_repetidos(rows: list[list[str]]) -> list[list[str]]:
    """Quita las filas que el propio readiness da por el mismo hallazgo que otra.

    Dos auditores ven el mismo choque desde cada lado y le ponen dos IDs; el readiness lo
    escribe («Mismo hallazgo que CF-F005-01, visto desde el otro lado») pero deja las dos
    filas, y cada una salía como una decisión que tomar (pasada 1 de CU-3.ab).
    """
    ids = {r[0].strip() for r in rows}
    out = []
    for r in rows:
        desc = r[3] if len(r) > 3 else ""
        m = re.match(r"\s*\**\s*Mismo hallazgo que\s+(CF-[\w-]+)", desc, re.IGNORECASE)
        if m and m.group(1) in ids and m.group(1) != r[0].strip():
            continue
        out.append(r)
    return out


def _seal_module():
    """`sdd-seal.py`, hermano de este script; None si no está instalado."""
    path = Path(__file__).resolve().parent / "sdd-seal.py"
    if not path.is_file():
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("sdd_seal", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _contracts_module():
    """`sdd-model-contracts.py`, hermano de este script; None si no está instalado."""
    path = Path(__file__).resolve().parent / "sdd-model-contracts.py"
    if not path.is_file():
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("sdd_model_contracts", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render_pending(data: dict) -> str:
    out = ["# Pendientes de la fase Spec", ""]
    notas = [f"> Nota (no es un pendiente): {g['que']}" for g in data.get("grupos", [])]
    notas += [f"> Aviso (no es un pendiente): {d['que']}"
              for d in data.get("dependencias_no_declaradas", [])]
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


INCREMENTAL_TITLE = "Actualización incremental"
SIN_VALIDAR_TXT = "pendiente de validación (el spec sigue en BORRADOR)"


def _cerrados_incrementales(rtext: str) -> set:
    """Los conflictos que una actualización incremental del readiness dio por cerrados."""
    m = re.search(r"^\s*[-*]\s*\*\*Cerrados\*\*\s*:\s*(.*)$", section(rtext, INCREMENTAL_TITLE),
                  re.MULTILINE)
    return set(CF_ID_RE.findall(m.group(1))) if m else set()


def refresh_readiness(directory: Path, solo_criterios: list | None = None) -> dict:
    """Pone al día el readiness sin rehacerlo, cuando no hay nada que arbitrar (v0.128.0).

    Rehacerlo con un agente costaba 3-6 minutos por vuelta, y tras copiar algo ya decidido
    solo decía «el conflicto queda cerrado» (pasada 1 de CU-3.ac (3): 4 mediciones, 21 min).
    Se puede sin agente si: no hay features nuevas; cada spec cambiado tiene un informe de
    conflictos posterior (o el cambio solo añadió criterios: `solo_criterios`); y ningún
    informe posterior abre un conflicto que el readiness no tenga ya. Entonces lo que cambia
    es mecánico: qué conflictos se cerraron y las filas de la matriz que solo esperaban a
    ellos. Si algo de eso falla, `ok` es False y los `motivos` dicen por qué: hace falta la
    medición completa.
    """
    solo = {Path(x).resolve() for x in (solo_criterios or [])}
    readiness = first(directory, "*_readiness_report.md")
    if not readiness:
        return {"ok": False, "motivos": ["no hay informe de readiness"]}
    rtext = read_text(readiness)
    rts = readiness.stat().st_mtime
    features_md_path = first(directory, "*_features.md")
    idx = _index_blocks(read_text(features_md_path) if features_md_path else "")
    specs = {f: (directory / m["ruta"]).resolve() for f, m in idx.items()
             if m["ruta"] and (directory / m["ruta"]).resolve().is_file()}
    motivos = []
    rmat = {r[0].split(":")[0].strip(): r for r in _table_rows(rtext, "Matriz de readiness")}
    nuevas = [f for f in specs if f not in rmat or "PENDIENTE" in rmat[f][1]]
    if nuevas:
        motivos.append("features nuevas desde la medición: " + ", ".join(sorted(nuevas)))
    revisados = []
    for f, sp in sorted(specs.items(), key=lambda kv: fid_sort_key(kv[0])):
        if sp.stat().st_mtime <= rts:
            continue
        rep = sp.with_name(sp.name.replace("_spec.md", "_conflict_report.md"))
        if rep.is_file() and rep.stat().st_mtime >= sp.stat().st_mtime:
            revisados.append(f)
        elif sp in solo:
            revisados.append(f)
        elif (m := ESTADO_SPEC_RE.search(read_text(sp))) and m.group(1) == "BORRADOR":
            motivos.append(f"{f} cambió y sus conflictos no se han revisado después")
        # Si no, solo se selló después: el sello no cambia lo medido.
    estado_cf = _estado_conflictos(directory)
    raiz = estado_cf["__raiz__"]
    conocidos = [r[0] for r in _table_rows(rtext, "Conflictos ALTA no resueltos")
                 + _table_rows(rtext, "Conflictos MEDIA abiertos")]
    raices = {raiz(c) for k in conocidos for c in CF_ID_RE.findall(k)}
    for rep in _conflict_reports(directory):
        if rep.stat().st_mtime <= rts:
            continue
        for row in _table_rows(read_text(rep), "Resumen de conflictos"):
            ids = CF_ID_RE.findall(row[0])
            abierto = not (len(row) >= 5 and CERRADO_RE.search(row[-1]))
            if ids and abierto and not {raiz(i) for i in ids} & raices:
                motivos.append(f"conflicto nuevo que arbitrar: {ids[0]} "
                               f"({rep.parent.parent.name})")
    if motivos:
        return {"ok": False, "motivos": motivos}

    cerrados = sorted(_cerrados_incrementales(rtext) | {
        c for k in conocidos for c in CF_ID_RE.findall(k)
        if _cerrado_despues(estado_cf, c, rts)})
    # Las filas de la matriz que solo esperaban a conflictos ya cerrados.
    lineas = rtext.split("\n")
    sec = section(rtext, "Matriz de readiness")
    for n, ln in enumerate(lineas):
        if not ln.strip().startswith("|") or ln not in sec:
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        fm = FID_RE.search(cells[0]) if cells else None
        if not fm or len(cells) < 5 or fm.group(0) not in specs:
            continue
        partes = [x.strip() for x in cells[-1].split(";") if x.strip() and x.strip() != "—"]
        quedan = [x for x in partes if not (CF_ID_RE.findall(x)
                                            and set(CF_ID_RE.findall(x)) <= set(cerrados))]
        if quedan == partes:
            continue
        borrador = bool((m := ESTADO_SPEC_RE.search(read_text(specs[fm.group(0)])))
                        and m.group(1) == "BORRADOR")
        if not quedan:
            cells[1], cells[-1] = ("BLOQUEADA", SIN_VALIDAR_TXT) if borrador else ("LISTA", "—")
        else:
            cells[-1] = "; ".join(quedan)
        if len(cells) >= 4 and cells[3].isdigit():
            cells[3] = str(sum(1 for x in quedan if CF_ID_RE.search(x)))
        lineas[n] = "| " + " | ".join(cells) + " |"
    texto = "\n".join(lineas)
    import datetime
    bloque = (f"## {INCREMENTAL_TITLE}\n\n"
              f"> {datetime.date.today().isoformat()} — puesta al día sin rehacer el informe: los "
              "cambios posteriores no abrieron nada que arbitrar. Donde lo de abajo no coincida "
              "con esto, manda esto.\n\n"
              f"- **Cerrados**: {', '.join(cerrados) or 'ninguno'}\n"
              f"- **Specs revisados después**: {', '.join(revisados) or 'ninguno'}\n\n---\n\n")
    texto = re.sub(r"^##\s+" + INCREMENTAL_TITLE + r".*?(?=^##\s)", "", texto,
                   flags=re.MULTILINE | re.DOTALL)
    m = re.search(r"^##\s", texto, re.MULTILINE)
    texto = texto[:m.start()] + bloque + texto[m.start():] if m else texto + "\n" + bloque
    readiness.write_text(texto, encoding="utf-8")
    return {"ok": True, "cerrados": cerrados, "revisados": revisados,
            "informe": os.path.relpath(readiness)}


def main(argv: list[str]) -> int:
    lote, solo = None, []
    if "--solo-criterios" in argv:
        i = argv.index("--solo-criterios")
        solo = [a for a in argv[i + 1:] if not a.startswith("--")]
        argv = argv[:i] + [a for a in argv[i + 1:] if a.startswith("--")]
    if "--lote" in argv:
        i = argv.index("--lote")
        lote = [a for a in argv[i + 1:] if not a.startswith("--")]
        argv = argv[:i] + [a for a in argv[i + 1:] if a.startswith("--")]
    args = [a for a in argv if not a.startswith("--")]
    out_idx = argv.index("--output") if "--output" in argv else -1
    out_file = argv[out_idx + 1] if 0 <= out_idx < len(argv) - 1 else None
    if out_file and out_file in args:
        args.remove(out_file)
    if len(args) != 1:
        sys.stderr.write("uso: sdd-project-status.py <dir> [--output <archivo>] | "
                         "<dir> --spec-pending [--json] [--lote <spec.md> …] | "
                         "<dir> --refresh-readiness [--solo-criterios <spec.md> …]\n")
        return 1
    directory = Path(args[0]).resolve()
    if not directory.is_dir():
        sys.stderr.write(f"[project-status] no es un directorio: {directory}\n")
        return 1

    if "--refresh-readiness" in argv:
        data = refresh_readiness(directory, solo)
        import json
        sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        return 0 if data["ok"] else 2

    if "--spec-pending" in argv:
        data = spec_pending(directory, lote)
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
