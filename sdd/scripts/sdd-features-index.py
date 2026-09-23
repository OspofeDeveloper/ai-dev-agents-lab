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
    spec `Estado: RETIRADO` .......... RETIRADA (por encima de todo, D-074)
    con spec y veredicto en readiness  el del readiness report (autoridad), salvo
                                       un LISTA sobre spec en BORRADOR → BLOQUEADA (D-077)
                                       y un PENDIENTE_GENERACIÓN sobre spec que existe,
                                       que es matriz estancada y no veredicto (D-089):
                                       se descarta y cae al camino marker-based
    con spec, sin readiness ...........  marcador-based provisional:
        [INCOMPLETO]/[CRÍTICO]/[INFERIDO] → BLOQUEADA
        avisos de gobernanza != ninguno   → REQUIERE_CAMBIO_PRD
        `Estado: BORRADOR`                → BLOQUEADA, pendiente de validacion (D-077)
        limpio y sellado                  → LISTA

Uso:
    sdd-features-index.py <dir>            # regenera <base>_features.md en <dir>
    sdd-features-index.py <dir> --check    # exit 2 si el de disco difiere (CI/gate)
    sdd-features-index.py <dir> --stdout   # imprime, no escribe
    sdd-features-index.py <dir> --discovery <path>   # discovery explícito

<dir> es el directorio raíz de artefactos spec: contiene `features/` y donde
viven `_features.md` / `_readiness_report.md`.

Dónde se busca el discovery (en orden, primera coincidencia gana):
  1. `--discovery <path>` explícito.
  2. `*_discovery.md` dentro de <dir>, EXCLUYENDO `*_code_discovery.md`.
  3. Los demás directorios de `artifacts` de `.sdd/project-init.json` (buscado
     hacia arriba desde <dir>), empezando por `prd`, con la misma exclusión.

La exclusión no es cosmética (D-083): `<scope>_code_discovery.md` es el mapa de
CAPACIDADES del onramp brownfield (`wf-spec-from-code discover`), no el universo
de features de un PRD, y encaja en el glob por puro sufijo. En una adopción
(D-079) los dos conviven en la misma raíz y `sorted()` decide por orden
alfabético: `billing_code_discovery.md` gana a `prd_discovery.md` y el índice
sale con el universo equivocado — y, si aún no había índice previo del que
heredar el nombre, también con el nombre equivocado
(`billing_code_features.md`). En brownfield puro el daño es menor y también
real: el mapa tiene otro formato, así que la feature se indexa sin nombre y las
fuentes declaran `discovery=sí` sobre un discovery que no existe. Sin mapa como
discovery, el índice se construye desde los specs — que es justo lo que
`wf-spec-from-code` promete para ese caso.

El paso 3 existe porque el discovery lo genera `wf-spec-discover` a partir del
PRD y se llama `<basename_prd>_discovery.md`: en topología `authoring`
(`artifacts.prd` != `artifacts.spec`) vive en el directorio del PRD, no en la
raíz spec. Sin este cruce de frontera el índice no ve el universo de features y
registra solo las ya generadas — perdiendo en silencio las PENDIENTE_GENERACIÓN.

Exit codes: 0 = OK (regenerado / en sync); 1 = error de uso o IO;
            2 = (--check) el archivo de disco está desactualizado.

Política conservadora: si no hay discovery, el índice se construye solo con los
specs presentes (caso fast-track standalone) — pero lo DECLARA en un aviso
visible dentro del propio artefacto y en stderr, porque un índice sin discovery
no es un mapa completo del producto. Nunca aborta por una sección ausente o
malformada — la omite.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

CANON_STATES = ("LISTA", "BLOQUEADA", "PENDIENTE_GENERACIÓN", "REQUIERE_CAMBIO_PRD",
                "RETIRADA")
# ROADMAP 11.10: esta nota va DENTRO de `_features.md`, que lo lee una persona.
# Describe el estado y la accion en lenguaje natural; el `F-00X` se queda porque es
# el identificador con el que el usuario nombra la feature, no una invocacion.
PENDIENTE_NOTE = (
    "> {fid} está identificada en el discovery pero aún no tiene spec generada. "
    "Pide que se genere cuando quieras procesarla."
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


def is_code_discovery(path: Path) -> bool:
    """`<scope>_code_discovery.md`: el mapa de capacidades del onramp brownfield.

    Encaja en el glob `*_discovery.md` por sufijo y NO es un discovery de
    features (ver la nota de D-083 en el docstring del módulo).
    """
    return path.name.endswith("_code_discovery.md")


def first_discovery(directory: Path) -> Path | None:
    """Primer `*_discovery.md` de <dir> que sea de verdad un discovery."""
    for cand in sorted(directory.glob("*_discovery.md")):
        if not is_code_discovery(cand):
            return cand
    return None


def sibling_artifact_dirs(directory: Path) -> list[Path]:
    """Directorios de artefactos declarados en `.sdd/project-init.json`, salvo <dir>.

    Busca el `.sdd/project-init.json` hacia arriba desde <dir> (el más cercano
    gana, como el resto del ecosistema). `prd` va primero porque el discovery se
    deriva del PRD; el resto en orden alfabético para que la búsqueda sea
    determinista. Ausencia o JSON inválido → lista vacía, nunca excepción: el
    índice sigue siendo utilizable sin `.sdd/`.
    """
    init = None
    for base in [directory] + list(directory.parents):
        cand = base / ".sdd" / "project-init.json"
        if cand.is_file():
            init = cand
            break
    if init is None:
        return []
    try:
        data = json.loads(read_text(init))
    except (ValueError, TypeError):
        return []
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict):
        return []
    root = init.parent.parent
    keys = sorted(artifacts, key=lambda k: (k != "prd", k))
    dirs = []
    for key in keys:
        val = artifacts.get(key)
        if not isinstance(val, str) or not val:
            continue
        cand = (root / val).resolve()
        if cand != directory and cand.is_dir() and cand not in dirs:
            dirs.append(cand)
    return dirs


def find_discovery(directory: Path, explicit: str | None) -> tuple[Path | None, bool]:
    """Localiza el discovery. Devuelve (path, viene_de_fuera_de_<dir>).

    `viene_de_fuera` importa para el nombre de salida: el índice se llama
    `<base_discovery>_features.md` solo cuando ambos comparten directorio; si el
    discovery vive en otra raíz (topología `authoring`), el índice conserva el
    nombre derivado de <dir> y no importa el basename del PRD.

    El barrido automático descarta los `*_code_discovery.md` (D-083); un
    `--discovery <path>` explícito se respeta tal cual: es una orden de quien
    invoca, y el filtro existe para el descubrimiento, no para vetar una vía.
    """
    if explicit:
        cand = Path(explicit).expanduser()
        if cand.is_file():
            return cand, cand.parent.resolve() != directory
        return None, False
    local = first_discovery(directory)
    if local:
        return local, False
    for sib in sibling_artifact_dirs(directory):
        cand = first_discovery(sib)
        if cand:
            return cand, True
    return None, False


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
    """Extrae `> key: valor` del header de un artefacto.

    Tolera la variante en negrita (`> **key:** valor`), que es la que usa la
    cabecera de los specs de caracterizacion: leyendo solo la forma pelada esos
    campos salian ausentes y el indice los omitia en silencio ([[D-066]]).
    """
    m = re.search(r"^>\s*\**" + re.escape(key) + r"\**\s*:\s*\**\s*(.*?)\**\s*$",
                  text, re.MULTILINE)
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


# Specs que el escaneo NO pudo indexar por cabecera incompleta. No es una lista
# de cortesia: sin `Feature ID` el spec se cae del indice ENTERO y el resultado es
# un artefacto parcial con apariencia de completo — el peor modo de fallo posible
# ([[D-046]], [[D-066]]). Se vuelca en stderr y dentro del propio indice.
SPECS_SIN_CABECERA: list[str] = []

# Features cuyo spec YA existe en disco y a las que la `## Matriz de readiness` del
# informe en disco sigue llamando `PENDIENTE_GENERACIÓN` ([[D-089]]). El indice se
# corrige solo (el veredicto se descarta y gana el camino marker-based), pero el
# informe del que salio sigue estancado — y a ese lo regenera una persona.
READINESS_ESTANCADO: list[str] = []


def parse_spec(path: Path, features_root: Path) -> dict | None:
    text = read_text(path)
    if not text:
        return None
    fid = header_field(text, "Feature ID")
    if not fid:
        m = FID_RE.search(text[:600])
        fid = m.group(0) if m else None
    if not fid:
        SPECS_SIN_CABECERA.append(f"{path} (sin `Feature ID`: NO se indexa)")
        return None
    if not header_field(text, "Origen de alcance"):
        SPECS_SIN_CABECERA.append(f"{path} (sin `Origen de alcance`: se indexa incompleto)")
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
        "estado": header_field(text, "Estado"),
        "retirada": header_field(text, "Retirada"),
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


SIN_VALIDAR_MOTIVO = "pendiente de validación (el spec sigue en BORRADOR)"


def _sin_validar(spec: dict) -> bool:
    """El spec DECLARA `Estado: BORRADOR` (D-061/D-077).

    Conservador, igual que `gate_spec_fiable` y que `status_sync`: un spec legacy
    sin la linea `Estado:` NO cuenta como sin validar — devuelve False y sigue el
    camino de siempre. Solo bloquea lo que se afirma, nunca lo que se omite.
    """
    return (spec.get("estado") or "").strip().upper() == "BORRADOR"


def derive_state(spec: dict | None, verdict: dict | None) -> tuple[str, str]:
    if spec is None:
        return "PENDIENTE_GENERACIÓN", "—"
    # Un `PENDIENTE_GENERACIÓN` sobre un spec que EXISTE no es un veredicto: es un
    # informe que se quedo atras ([[D-089]]). Pasa en cada iteracion por subset — el
    # Paso 6 de `wf-spec-features-first` regenera el indice ANTES del readiness del
    # Paso 8, asi que el unico informe en disco es el de la tanda anterior, que
    # listaba estas features como pendientes. Que el spec exista es un hecho
    # mecanico del disco; el veredicto es un juicio, y el disco es mas fresco (mismo
    # razonamiento que el carve-out de `LISTA` sobre BORRADOR, [[D-077]]). Sin esto
    # el indice sale contradiciendose solo: `Ruta spec` a un fichero que existe,
    # `Estado: PENDIENTE_GENERACIÓN` y la nota de "aun no tiene spec generada".
    if verdict and verdict["estado"] == "PENDIENTE_GENERACIÓN":
        READINESS_ESTANCADO.append(spec.get("fid") or str(spec.get("path") or "?"))
        verdict = None
    # La baja manda sobre todo lo demas ([[D-074]]). Va ANTES del veredicto del
    # readiness a proposito: una feature que el producto ya no contempla no es
    # "BLOQUEADA" —no hay nada que desbloquear— y ningun informe puede resucitarla.
    # El unico escritor de `Estado: RETIRADO` es `sdd-seal.py --retire`.
    if (spec.get("estado") or "").strip().upper() == "RETIRADO":
        return "RETIRADA", (spec.get("retirada") or "dada de baja").strip()
    # `LISTA` es el unico veredicto que el sello puede desmentir (D-077). Un spec en
    # BORRADOR no se puede planificar —`gate_spec_fiable` lo deniega (D-061)—, asi que
    # un informe que lo declare LISTA promete algo que el gate incumple una fase mas
    # tarde. El sello es un hecho mecanico de la cabecera, no un juicio, y la cabecera
    # es mas fresca que el informe: un delta o una resincronizacion posteriores desellan
    # (`--unseal`) sin que nadie regenere el readiness.
    if verdict:
        if verdict["estado"] == "LISTA" and _sin_validar(spec):
            return "BLOQUEADA", SIN_VALIDAR_MOTIVO
        return verdict["estado"], verdict.get("bloqueantes", "—")
    if spec["has_marker"]:
        return "BLOQUEADA", "marcadores [INCOMPLETO]/[CRÍTICO]/[INFERIDO] en el spec"
    if has_gobernanza(spec.get("gobernanza")):
        return "REQUIERE_CAMBIO_PRD", f"gobernanza: {spec['gobernanza']}"
    # Va DESPUES de marcadores y gobernanza a proposito: los dos son motivos mas
    # concretos, y ademas un spec con marcadores abiertos NO se puede validar
    # (`sdd-seal.py spec --check` lo deniega). Decirle a alguien "falta validarlo"
    # cuando el sellador va a rechazarlo es mandarlo a un callejon sin salida.
    if _sin_validar(spec):
        return "BLOQUEADA", SIN_VALIDAR_MOTIVO
    return "LISTA", "—"


# ── Render (función pura) ──────────────────────────────────────────────────


def relpath_or_name(path: Path | None, base: Path) -> str | None:
    """Ruta del discovery relativa a <dir>, con `/` siempre (salida portable).

    `os.path.relpath` no toca el disco y funciona aunque no compartan prefijo
    (da `../…`). Si son volúmenes distintos (Windows) cae al nombre a secas.
    """
    if path is None:
        return None
    try:
        return Path(os.path.relpath(path, base)).as_posix()
    except ValueError:
        return path.name


def render(directory: Path, discovery: dict, specs: dict, verdicts: dict,
           disc_name: str | None, ready_present: bool,
           disc_rel: str | None = None) -> str:
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
    if disc_rel:
        out.append(f"> Discovery: `{disc_rel}` (fuera de esta raíz de artefactos)")
    if discovery.get("prd_origen"):
        out.append(f"> Spec origen: {discovery['prd_origen']}")
    if not disc_name and specs:
        out.append(
            "> ⚠ SIN DISCOVERY: este índice solo refleja los specs presentes. "
            "Las features identificadas y todavía NO generadas "
            "(`PENDIENTE_GENERACIÓN`) no aparecen aquí. Regenera con "
            "`--discovery <path>` o revisa `artifacts` en "
            "`.sdd/project-init.json`."
        )
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


def build(directory: Path, discovery_arg: str | None = None) -> tuple[str, Path]:
    disc_path, disc_external = find_discovery(directory, discovery_arg)
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

    # Nombre de salida: el existente, o derivado del discovery LOCAL, o <dir>_features.md
    if existing:
        out_path = existing
    elif disc_path and not disc_external:
        out_path = directory / (disc_path.name.replace("_discovery.md", "_features.md"))
    else:
        out_path = directory / f"{directory.name}_features.md"

    content = render(
        directory, discovery, specs, verdicts,
        disc_name=disc_path.name if disc_path else None,
        disc_rel=relpath_or_name(disc_path, directory) if disc_external else None,
        ready_present=ready_path is not None,
    )
    return content, out_path


def main(argv: list[str]) -> int:
    args: list[str] = []
    flags: set[str] = set()
    discovery_arg: str | None = None
    skip = -1
    for i, a in enumerate(argv):
        if i == skip:
            continue
        if a.startswith("--discovery="):
            discovery_arg = a.split("=", 1)[1]
        elif a == "--discovery":
            if i + 1 >= len(argv):
                sys.stderr.write("[features-index] --discovery requiere una ruta\n")
                return 1
            discovery_arg = argv[i + 1]
            skip = i + 1
        elif a.startswith("--"):
            flags.add(a)
        else:
            args.append(a)
    if len(args) != 1:
        sys.stderr.write(
            "uso: sdd-features-index.py <dir> [--check | --stdout] "
            "[--discovery <path>]\n"
        )
        return 1
    directory = Path(args[0]).resolve()
    if not directory.is_dir():
        sys.stderr.write(f"[features-index] no es un directorio: {directory}\n")
        return 1
    if discovery_arg and not Path(discovery_arg).expanduser().is_file():
        sys.stderr.write(
            f"[features-index] --discovery no existe: {discovery_arg}\n"
        )
        return 1

    content, out_path = build(directory, discovery_arg)

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
    if SPECS_SIN_CABECERA:
        sys.stderr.write(
            f"[features-index] ⚠ {len(SPECS_SIN_CABECERA)} spec(s) con la cabecera "
            "incompleta — el indice NO los refleja bien:\n")
        for s in SPECS_SIN_CABECERA:
            sys.stderr.write(f"  - {s}\n")
        sys.stderr.write(
            "  Repon `Feature ID` y `Origen de alcance` en su cabecera y regenera. "
            "Mientras falten, este indice esta incompleto ([[D-066]]).\n")
    if READINESS_ESTANCADO:
        sys.stderr.write(
            f"[features-index] ⚠ matriz de readiness estancada: "
            f"{len(READINESS_ESTANCADO)} feature(s) con spec en disco que el informe "
            f"sigue dando por generar ({', '.join(READINESS_ESTANCADO)}).\n"
            "  Este indice ya las deriva de sus specs, pero el "
            "`_readiness_report.md` es de una tanda anterior: su veredicto no ha "
            "visto estos specs. Regeneralo antes de decidir nada con el ([[D-089]]).\n"
        )
    if "> ⚠ SIN DISCOVERY" in content:
        sys.stderr.write(
            "[features-index] ⚠ sin discovery: el índice solo cubre los specs "
            "presentes; las features aún no generadas no aparecen. Pasa "
            "--discovery <path> o revisa `artifacts` en .sdd/project-init.json.\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
