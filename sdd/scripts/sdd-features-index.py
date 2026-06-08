#!/usr/bin/env python3
"""Regenerador determinista de `_features.md` (Fase 5.4 del ROADMAP).

`_features.md` era un hub monolítico editado a mano por varios workflows
(fast-track por feature, features-first en consolidación, readiness en estado).
Con dos devs en ramas paralelas eso garantiza conflicto de merge aunque editen
features distintas. Este script lo convierte en un artefacto GENERADO: una
función pura de sus fuentes, igual que `generate-skill-registry.py` hace con el
registry. Un conflicto en `_features.md` pasa a ser ruido — se regenera tras el
merge — y la SSoT real vive repartida y co-localizada por feature.

Reparto de SSoT (ninguna lo redefine):
    _discovery.md        universo de features, shared models, RF→Feature.
    features/*/spec/      cada spec es la SSoT de "feature generada" + sus
                          marcadores reales ([INCOMPLETO]/[CRÍTICO]/[INFERIDO]),
                          Feature ID, HUs y CAs. (También layout plano legacy.)
    _readiness_report.md  (opcional) veredicto refinado por feature (conflictos
                          ALTA, dependencias) — su `## Matriz de readiness`.

Salida = función pura de las entradas (SIN timestamp de reloj): re-ejecutar sin
cambios en las fuentes produce bytes idénticos → idempotente, sin churn de git.

Derivación de Estado por feature (prioridad):
    sin spec ......................... PENDIENTE_GENERACIÓN
    con spec y veredicto en readiness  el del readiness report (autoridad)
    con spec, sin readiness ...........  marcador-based provisional:
        [INCOMPLETO]/[CRÍTICO]/[INFERIDO] → BLOQUEADA
        avisos de gobernanza != ninguno   → REQUIERE_CAMBIO_PRD
        limpio                            → LISTA

Uso:
    sdd-features-index.py <dir>            # regenera <base>_features.md en <dir>
    sdd-features-index.py <dir> --check    # exit 2 si el de disco difiere (CI/gate)
    sdd-features-index.py <dir> --stdout   # imprime, no escribe

<dir> es el directorio raíz de artefactos spec: contiene `features/` y donde
viven `_discovery.md` / `_features.md` / `_readiness_report.md`.

Exit codes: 0 = OK (regenerado / en sync); 1 = error de uso o IO;
            2 = (--check) el archivo de disco está desactualizado.

Política conservadora: si no hay discovery, el índice se construye solo con los
specs presentes (caso fast-track standalone). Nunca aborta por una sección
ausente o malformada — la omite.
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path

CANON_STATES = ("LISTA", "BLOQUEADA", "PENDIENTE_GENERACIÓN", "REQUIERE_CAMBIO_PRD")
PENDIENTE_NOTE = (
    "> Esta feature está identificada en el discovery pero aún no se ha generado "
    "spec. Ejecuta /wf-spec-features-first <prd.md> --features {fid} cuando quieras "
    "procesarla."
)

# ── Helpers de parseo ──────────────────────────────────────────────────────

FID_RE = re.compile(r"\bF-(?:C-)?\d+\b")
MARKER_RE = re.compile(r"\[(?:INCOMPLETO|CR[IÍ]TICO|INFERIDO)\]")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def first_glob(directory: Path, pattern: str) -> Path | None:
    matches = sorted(directory.glob(pattern))
    return matches[0] if matches else None


def fid_sort_key(fid: str):
    """Orden natural: agrupa por prefijo (F-, F-C-) y ordena por número."""
    m = re.match(r"(F-(?:C-)?)(\d+)", fid)
    if m:
        return (m.group(1), int(m.group(2)))
    return (fid, 0)


def bullet(line_body: str, key: str) -> str | None:
    """Extrae el valor de un bullet `- **key**: valor` (o None)."""
    m = re.match(
        r"\s*-\s*\*\*" + re.escape(key) + r"\*\*\s*:\s*(.*)$", line_body
    )
    return m.group(1).strip() if m else None


def header_field(text: str, key: str) -> str | None:
    """Extrae `> key: valor` del header de un artefacto."""
    m = re.search(r"^>\s*" + re.escape(key) + r"\s*:\s*(.*)$", text, re.MULTILINE)
    return m.group(1).strip() if m else None


def split_feature_blocks(section: str) -> list[tuple[str, str, str]]:
    """Parte una sección en bloques `### F-XXX: nombre` → (fid, nombre, cuerpo)."""
    blocks = []
    parts = re.split(r"^###\s+(F-(?:C-)?\d+)\s*:\s*(.*)$", section, flags=re.MULTILINE)
    # parts: [pre, fid1, name1, body1, fid2, name2, body2, ...]
    for i in range(1, len(parts), 3):
        fid = parts[i].strip()
        name = parts[i + 1].strip()
        body = parts[i + 2] if i + 2 < len(parts) else ""
        blocks.append((fid, name, body))
    return blocks


def section(text: str, title: str) -> str:
    """Devuelve el cuerpo de la sección `## title` hasta el siguiente `## `."""
    m = re.search(
        r"^##\s+" + re.escape(title) + r"\s*$(.*?)(?=^##\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return m.group(1) if m else ""


def table_rows(section_text: str) -> list[list[str]]:
    """Filas de la primera tabla markdown de la sección (sin header ni separador)."""
    rows = []
    seen_sep = False
    for line in section_text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            if rows or seen_sep:
                break
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= {"-", ":", " "} for c in cells) and cells:
            seen_sep = True
            continue
        if not seen_sep:  # cabecera
            continue
        rows.append(cells)
    return rows


# ── Modelos de datos (dicts simples, sin clases) ───────────────────────────


def parse_discovery(path: Path | None) -> dict:
    """Universo de features + shared models + RF→Feature desde el discovery."""
    out = {"project": None, "prd_origen": None, "features": {}, "shared_models": [],
           "rf_feature": []}
    if not path:
        return out
    text = read_text(path)
    if not text:
        return out
    m = re.search(r"^#\s+Feature Discovery:\s*(.*)$", text, re.MULTILINE)
    if m:
        out["project"] = m.group(1).strip()
    out["prd_origen"] = header_field(text, "PRD origen")

    for fid, name, body in split_feature_blocks(section(text, "Features identificadas")):
        feat = {"name": name}
        for src_key, dst_key in (
            ("Descripción", "descripcion"),
            ("Actor principal", "actor"),
            ("Journeys anticipados", "journeys"),
            ("CAs derivables", "cas_derivables"),
            ("Scope (RFs)", "scope_rfs"),
            ("Modelos propios", "modelos_propios"),
            ("Modelos compartidos (owner)", "modelos_owner"),
            ("Modelos compartidos (ref)", "modelos_ref"),
            ("Origen de alcance", "origen"),
            ("Avisos de gobernanza", "gobernanza"),
        ):
            for line in body.splitlines():
                val = bullet(line, src_key)
                if val is not None:
                    feat[dst_key] = val
                    break
        out["features"][fid] = feat

    for cells in table_rows(section(text, "Tabla de shared models")):
        if len(cells) >= 3:
            out["shared_models"].append(cells[:3])  # Modelo | Owner | Refs

    for cells in table_rows(section(text, "Trazabilidad RF → Feature")):
        if len(cells) >= 3:
            out["rf_feature"].append({"rf": cells[0], "titulo": cells[1],
                                      "feature": cells[2]})
    return out


def parse_spec(path: Path, features_root: Path) -> dict | None:
    text = read_text(path)
    if not text:
        return None
    fid = header_field(text, "Feature ID")
    if not fid:
        m = FID_RE.search(text[:600])
        fid = m.group(0) if m else None
    if not fid:
        return None
    m = re.search(r"^#\s+Spec:\s*(.*)$", text, re.MULTILINE)
    title = m.group(1).strip() if m else fid
    try:
        relpath = path.relative_to(features_root).as_posix()
    except ValueError:
        relpath = path.name
    hus = re.findall(r"^###\s+(HU-\d+)\s*:", text, re.MULTILINE)
    cas = re.findall(r"^###\s+(CA-\d+)\s*:.*?←\s*(HU-\d+)", text, re.MULTILINE)
    return {
        "fid": fid,
        "title": title,
        "relpath": relpath,
        "status_sync": header_field(text, "status_sync"),
        "origen": header_field(text, "Origen de alcance"),
        "gobernanza": header_field(text, "Avisos de gobernanza"),
        "has_marker": bool(MARKER_RE.search(text)),
        "hus": hus,
        "cas": cas,
    }


def parse_readiness(path: Path | None) -> dict:
    """fid → {estado, bloqueantes} desde la `## Matriz de readiness`."""
    verdicts = {}
    if not path:
        return verdicts
    text = read_text(path)
    for cells in table_rows(section(text, "Matriz de readiness")):
        if len(cells) < 2:
            continue
        fm = FID_RE.search(cells[0])
        if not fm:
            continue
        estado = cells[1].strip()
        if estado not in CANON_STATES:
            continue
        bloqueantes = cells[-1].strip() if len(cells) >= 3 else "—"
        verdicts[fm.group(0)] = {"estado": estado, "bloqueantes": bloqueantes}
    return verdicts


# ── Derivación de estado ───────────────────────────────────────────────────


def has_gobernanza(value: str | None) -> bool:
    if not value:
        return False
    v = value.strip().lower()
    return v not in ("", "ninguno", "ninguna", "n/a", "—", "-")


def derive_state(spec: dict | None, verdict: dict | None) -> tuple[str, str]:
    if spec is None:
        return "PENDIENTE_GENERACIÓN", "—"
    if verdict:
        return verdict["estado"], verdict.get("bloqueantes", "—")
    if spec["has_marker"]:
        return "BLOQUEADA", "marcadores [INCOMPLETO]/[CRÍTICO]/[INFERIDO] en el spec"
    if has_gobernanza(spec.get("gobernanza")):
        return "REQUIERE_CAMBIO_PRD", f"gobernanza: {spec['gobernanza']}"
    return "LISTA", "—"


# ── Render (función pura) ──────────────────────────────────────────────────


def render(directory: Path, discovery: dict, specs: dict, verdicts: dict,
           disc_name: str | None, ready_present: bool) -> str:
    project = discovery.get("project") or directory.name
    fids = sorted(set(discovery["features"]) | set(specs), key=fid_sort_key)

    states = {}
    for fid in fids:
        states[fid] = derive_state(specs.get(fid), verdicts.get(fid))

    out = []
    out.append(f"# Features Index: {project}")
    out.append(
        "> GENERADO por `sdd-features-index.py` — NO editar a mano. "
        "Regenera con: `python3 .sdd/scripts/sdd-features-index.py <dir>`"
    )
    fuentes = (
        f"discovery={'sí' if disc_name else 'no'}, "
        f"specs={len(specs)}, "
        f"readiness={'sí' if ready_present else 'no'}"
    )
    out.append(f"> Fuentes: {fuentes}")
    if discovery.get("prd_origen"):
        out.append(f"> Spec origen: {discovery['prd_origen']}")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## Features identificadas")
    out.append("")

    for fid in fids:
        feat = discovery["features"].get(fid, {})
        spec = specs.get(fid)
        name = feat.get("name") or (spec["title"] if spec else fid)
        estado, _ = states[fid]
        out.append(f"### {fid}: {name}")
        if feat.get("descripcion"):
            out.append(f"- **Descripción**: {feat['descripcion']}")
        if feat.get("actor"):
            out.append(f"- **Actor principal**: {feat['actor']}")
        if feat.get("journeys"):
            out.append(f"- **Journeys propios**: {feat['journeys']}")
        if spec and spec["cas"]:
            ca_ids = [c[0] for c in spec["cas"]]
            out.append(f"- **CAs propios**: {ca_ids[0]} a {ca_ids[-1]}"
                       if len(ca_ids) > 1 else f"- **CAs propios**: {ca_ids[0]}")
        elif feat.get("cas_derivables"):
            out.append(f"- **CAs propios**: {feat['cas_derivables']} (derivables — sin spec)")
        if feat.get("modelos_propios"):
            out.append(f"- **Modelos propios**: {feat['modelos_propios']}")
        if feat.get("modelos_owner"):
            out.append(f"- **Modelos compartidos (owner)**: {feat['modelos_owner']}")
        if feat.get("modelos_ref"):
            out.append(f"- **Modelos compartidos (ref)**: {feat['modelos_ref']}")
        out.append(f"- **Ruta spec**: {spec['relpath'] if spec else '(pendiente de generación)'}")
        out.append(f"- **Estado**: {estado}")
        origen = (spec or feat).get("origen")
        if origen:
            out.append(f"- **Origen de alcance**: {origen}")
        gobernanza = (spec or feat).get("gobernanza")
        if gobernanza:
            out.append(f"- **Avisos de gobernanza**: {gobernanza}")
        if estado == "PENDIENTE_GENERACIÓN":
            out.append(PENDIENTE_NOTE.format(fid=fid))
        out.append("")

    out.append("---")
    out.append("")
    out.append("## Resumen de estado")
    out.append("")
    out.append("| Feature | Estado | Bloqueantes |")
    out.append("|---------|--------|-------------|")
    for fid in fids:
        feat = discovery["features"].get(fid, {})
        spec = specs.get(fid)
        name = feat.get("name") or (spec["title"] if spec else fid)
        estado, bloqueantes = states[fid]
        out.append(f"| {fid}: {name} | {estado} | {bloqueantes or '—'} |")
    out.append("")

    if discovery["shared_models"]:
        out.append("---")
        out.append("")
        out.append("## Tabla de shared models")
        out.append("")
        out.append("| Modelo | Feature Owner | Features que lo referencian |")
        out.append("|---|---|---|")
        for modelo, owner, refs in discovery["shared_models"]:
            out.append(f"| {modelo} | {owner} | {refs} |")
        out.append("")

    if discovery["rf_feature"]:
        out.append("---")
        out.append("")
        out.append("## Trazabilidad RF → HU → Feature")
        out.append("")
        out.append("| RF | Feature | HU | Estado |")
        out.append("|---|---|---|---|")
        for row in discovery["rf_feature"]:
            feature = row["feature"]
            fm = FID_RE.search(feature)
            fid = fm.group(0) if fm else ""
            spec = specs.get(fid)
            estado = states.get(fid, ("", ""))[0]
            hus = ", ".join(spec["hus"]) if spec and spec["hus"] else "HUs no generadas todavía"
            out.append(f"| {row['rf']} | {feature} | {hus} | {estado} |")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


# ── Orquestación ───────────────────────────────────────────────────────────


def build(directory: Path) -> tuple[str, Path]:
    disc_path = first_glob(directory, "*_discovery.md")
    ready_path = first_glob(directory, "*_readiness_report.md")
    existing = first_glob(directory, "*_features.md")

    discovery = parse_discovery(disc_path)
    verdicts = parse_readiness(ready_path)

    specs = {}
    features_dir = directory / "features"
    if features_dir.is_dir():
        spec_paths = sorted(features_dir.glob("*/spec/*_spec.md"))
        covered_dirs = {p.parent.parent for p in spec_paths}
        for p in sorted(features_dir.glob("*/*_spec.md")):  # layout plano legacy
            if p.parent not in covered_dirs:
                spec_paths.append(p)
        for p in spec_paths:
            parsed = parse_spec(p, directory)
            if parsed:
                specs.setdefault(parsed["fid"], parsed)

    # Nombre de salida: el existente, o derivado del discovery, o <dir>_features.md
    if existing:
        out_path = existing
    elif disc_path:
        out_path = directory / (disc_path.name.replace("_discovery.md", "_features.md"))
    else:
        out_path = directory / f"{directory.name}_features.md"

    content = render(
        directory, discovery, specs, verdicts,
        disc_name=disc_path.name if disc_path else None,
        ready_present=ready_path is not None,
    )
    return content, out_path


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    if len(args) != 1:
        sys.stderr.write(
            "uso: sdd-features-index.py <dir> [--check | --stdout]\n"
        )
        return 1
    directory = Path(args[0]).resolve()
    if not directory.is_dir():
        sys.stderr.write(f"[features-index] no es un directorio: {directory}\n")
        return 1

    content, out_path = build(directory)

    if "--stdout" in flags:
        sys.stdout.write(content)
        return 0

    if "--check" in flags:
        current = read_text(out_path) if out_path.exists() else ""
        if current == content:
            print(f"[features-index] EN_SYNC: {out_path.name}")
            return 0
        sys.stderr.write(
            f"[features-index] DESACTUALIZADO: {out_path.name} difiere de la "
            f"regeneración. Ejecuta: python3 .sdd/scripts/sdd-features-index.py "
            f"{args[0]}\n"
        )
        return 2

    # Escritura atómica (tempfile + os.replace): varios fast-tracks pueden
    # regenerar en paralelo; os.replace es atómico en POSIX → nunca un archivo
    # a medias, peor caso gana el último (y features-first cierra con la pasada
    # autoritativa).
    fd, tmp = tempfile.mkstemp(dir=str(out_path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp, out_path)
    except OSError:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    n_feat = content.count("\n### F-")
    print(f"[features-index] regenerado {out_path.name} ({n_feat} features)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
