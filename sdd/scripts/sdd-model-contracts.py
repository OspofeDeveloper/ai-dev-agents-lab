#!/usr/bin/env python3
"""Cada regla tiene un dueño: el lint de los contratos de modelos compartidos (D-111).

Un modelo compartido —Movimiento, Cuenta— tiene una feature dueña (la discovery la
asigna y `_features.md` la publica en su «Tabla de shared models»). Hasta D-111 el
dueño solo definía el modelo en su Plan, y las reglas del modelo —qué se puede
editar o borrar, cómo aparece, qué invariantes tiene— las escribía cada spec a su
manera. Los conflictos entre features salían de ahí: un consumidor que suponía una
regla que el dueño no decía, o que la reescribía distinta al corregirse.

Desde D-111 el dueño publica el contrato en su spec y los consumidores lo citan:

    ## Contrato de modelos compartidos          (en el spec dueño)
    ### Movimiento
    #### Orígenes externos
    | Origen | Operación | Qué crea o cambia | ¿Se puede tocar…? | Si se toca… |
    | F-005 (deudas) · R-001 | Registrar deuda | gasto vinculado | no | — |

    ## Modelos de otras features                (en el spec consumidor)
    | Modelo | Dueña | Qué hace esta feature con él | Regla que aplica |
    | Movimiento | F-001 | crea un gasto al registrar una deuda | Orígenes externos de F-001 |
    | Movimiento | F-001 | lectura: suma los gastos del mes | Contrato de F-001 |
    ### Peticiones al dueño
    ### [R-001] A F-001 (Movimiento): el gasto de una deuda viva no se edita
    - **Estado**: pendiente

Este script es el lint de arquitectura de esas fronteras. Lo que comprueba es solo
estructural —qué cita a quién—; si una frase de un CA fija una regla de un modelo
ajeno lo juzga el auditor, no un regex.

    1. Contrato: el dueño de un modelo compartido tiene su `### <Modelo>` en el
       contrato.
    2. Catálogo: cada consumidor que CREA O CAMBIA el modelo (fila que no empieza
       por «lectura») tiene al menos una fila suya en «Orígenes externos» del dueño.
    3. Peticiones: una `R-NNN` está atendida cuando una fila de orígenes del dueño
       la cita; si no, está pendiente.
    4. Dependencias: un consumidor que usa un modelo sin que el índice lo declare
       como referencia suya. Es un aviso: el auditor de conflictos no mira esa frontera.

Un spec sin ninguna de las dos secciones es anterior a D-111: se avisa y no se le
exige nada, para que un proyecto que actualiza no se quede bloqueado.

Uso:
    sdd-model-contracts.py <raíz_spec> [--json]

Exit: 0 sin problemas que bloqueen · 2 con alguno (contrato, catálogo o petición) ·
1 error de uso. Los avisos no cambian el exit.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FID_RE = re.compile(r"\bF-(?:C-)?\d+\b")
RID_RE = re.compile(r"\bR-\d{3,4}\b")
CONTRATO = "Contrato de modelos compartidos"
CONSUMO = "Modelos de otras features"
PETICION_RE = re.compile(r"^#{3,4}\s*\[(?P<id>R-\d{3,4})\]\s*(?P<titulo>.*)$", re.MULTILINE)
ESTADO_PETICION_RE = re.compile(r"^\s*[-*]\s*\**\s*Estado\s*\**\s*:\s*(.*)$", re.MULTILINE)
RETIRADA = ("retirada", "retirado", "descartada")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def fid_key(fid: str):
    m = re.match(r"(F-(?:C-)?)(\d+)", fid)
    return (m.group(1), int(m.group(2))) if m else (fid, 0)


def h2(text: str, title: str) -> str:
    """Cuerpo de la sección `## <title>` (hasta el siguiente `## `)."""
    m = re.search(r"^##\s+" + re.escape(title) + r"\b[^\n]*$(.*?)(?=^##\s|\Z)",
                  text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else ""


def has_h2(text: str, title: str) -> bool:
    return re.search(r"^##\s+" + re.escape(title) + r"\b", text, re.MULTILINE) is not None


def rows(text: str) -> list[list[str]]:
    """Filas de datos de las tablas markdown de `text` (sin cabecera ni separador)."""
    out, header_seen = [], False
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            header_seen = False
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        if not header_seen:
            header_seen = True
            continue
        out.append(cells)
    return out


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9áéíóúñü]", "", name.lower())


def index(features_md: str):
    """(rutas fid->ruta, nombres fid->name, modelos norm->{name, owner, refs})."""
    rutas, nombres = {}, {}
    for m in re.finditer(r"^###\s+(F-(?:C-)?\d+):\s*(.*?)\s*$(.*?)(?=^###\s|^##\s|\Z)",
                         features_md, re.MULTILINE | re.DOTALL):
        nombres[m.group(1)] = m.group(2).strip()
        rm = re.search(r"^-\s*\*\*Ruta spec\*\*\s*:\s*(.*)$", m.group(3), re.MULTILINE)
        ruta = rm.group(1).strip() if rm else ""
        if ruta and not ruta.startswith("("):
            rutas[m.group(1)] = ruta
    modelos = {}
    for row in rows(h2(features_md, "Tabla de shared models")):
        if len(row) < 3:
            continue
        owner = FID_RE.findall(row[1])
        if owner:
            modelos[norm(row[0])] = {"name": row[0].strip(" `*"), "owner": owner[0],
                                     "refs": set(FID_RE.findall(row[2]))}
    return rutas, nombres, modelos


def contrato(text: str) -> dict:
    """norm(modelo) -> {name, origenes: [{fids, rids, celda}]} del contrato del dueño."""
    body = h2(text, CONTRATO)
    out = {}
    heads = list(re.finditer(r"^###\s+(.+?)\s*$", body, re.MULTILINE))
    for n, m in enumerate(heads):
        end = heads[n + 1].start() if n + 1 < len(heads) else len(body)
        block = body[m.end():end]
        om = re.search(r"^####\s+Or[ií]genes externos\b.*?$(.*)", block, re.MULTILINE | re.DOTALL)
        origenes = []
        for row in rows(om.group(1) if om else ""):
            origenes.append({"fids": set(FID_RE.findall(row[0])),
                             "rids": set(RID_RE.findall(row[0])), "celda": row[0]})
        name = m.group(1).strip(" `*")
        out[norm(name)] = {"name": name, "origenes": origenes}
    return out


def consumo(text: str) -> tuple[list[dict], list[dict]]:
    """(usos, peticiones) de la sección del consumidor."""
    body = h2(text, CONSUMO)
    tabla = re.split(r"^###\s", body, maxsplit=1, flags=re.MULTILINE)[0]
    usos = []
    for row in rows(tabla):
        if len(row) < 3:
            continue
        owner = FID_RE.findall(row[1])
        usos.append({"modelo": row[0].strip(" `*"), "owner": owner[0] if owner else "",
                     # Solo lectura si lo dice en cualquier punto de la celda: la plantilla pide
                     # empezar por «lectura:», pero un escritor que lo pone en medio («asocia… ;
                     # lectura de su identidad») no escribe sobre el modelo, y tratarlo como
                     # escritura inventa un catálogo incompleto (pasada 1 de CU-3.ab).
                     "que": row[2], "escribe": not re.search(r"\blectura\b|\bsolo lee\b",
                                                             row[2].lower())})
    peticiones = []
    heads = list(PETICION_RE.finditer(body))
    for n, m in enumerate(heads):
        end = heads[n + 1].start() if n + 1 < len(heads) else len(body)
        block = body[m.end():end]
        em = ESTADO_PETICION_RE.search(block)
        titulo = m.group("titulo").strip()
        owner = FID_RE.findall(titulo)
        modelo = re.search(r"\(([^)]+)\)", titulo)
        peticiones.append({"id": m.group("id"), "titulo": titulo,
                           "owner": owner[0] if owner else "",
                           "modelo": modelo.group(1).strip() if modelo else "",
                           "estado": (em.group(1).strip().strip("*_ ") if em else "pendiente")})
    return usos, peticiones


def check(directory: Path) -> dict:
    features_md_path = next(iter(sorted(directory.glob("*_features.md"))), None)
    features_md = read_text(features_md_path) if features_md_path else ""
    rutas, nombres, modelos = index(features_md)
    label = {f: f"{f} ({n})" if n else f for f, n in nombres.items()}
    specs = {}
    for fid, ruta in rutas.items():
        p = (directory / ruta)
        if p.is_file():
            specs[fid] = read_text(p)

    nuevos = {f for f, t in specs.items() if has_h2(t, CONTRATO) or has_h2(t, CONSUMO)}
    anteriores = sorted(set(specs) - nuevos, key=fid_key)
    contratos = {f: contrato(specs[f]) for f in nuevos}
    usos = {f: consumo(specs[f]) for f in nuevos}

    sin_contrato, catalogo, peticiones, no_declaradas, uso = [], [], [], [], []
    # 1. El dueño publica el contrato de cada modelo suyo.
    for key, mod in sorted(modelos.items()):
        o = mod["owner"]
        if o in nuevos and key not in contratos[o]:
            sin_contrato.append({"owner": o, "modelo": mod["name"],
                                 "que": f"{label.get(o, o)} es dueña de {mod['name']} y su spec "
                                        "no publica su contrato."})
    for c in sorted(nuevos, key=fid_key):
        lista, pets = usos[c]
        for u in lista:
            key = norm(u["modelo"])
            mod = modelos.get(key)
            owner = u["owner"] or (mod["owner"] if mod else "")
            if owner and owner != c:
                uso.append({"feature": c, "owner": owner, "modelo": u["modelo"],
                            "escribe": u["escribe"]})
            # 4. Dependencia que el índice no declara.
            if mod and c != mod["owner"] and c not in mod["refs"]:
                no_declaradas.append({"feature": c, "modelo": mod["name"], "owner": mod["owner"],
                                      "que": f"{label.get(c, c)} usa {mod['name']} y el índice no "
                                             "la declara como referencia."})
            elif not mod and owner:
                no_declaradas.append({"feature": c, "modelo": u["modelo"], "owner": owner,
                                      "que": f"{label.get(c, c)} usa {u['modelo']}, que el índice "
                                             "no tiene como modelo compartido."})
            # 2. Catálogo: quien crea o cambia el modelo sale en los orígenes del dueño.
            if u["escribe"] and owner in nuevos and owner != c:
                c_mod = contratos[owner].get(key)
                if c_mod is not None and not any(c in o["fids"] for o in c_mod["origenes"]):
                    catalogo.append({"owner": owner, "consumidor": c, "modelo": c_mod["name"],
                                     "operacion": u["que"],
                                     "que": f"{label.get(c, c)} {u['que'][:1].lower()}"
                                            f"{u['que'][1:].rstrip('.')}, y el contrato de "
                                            f"{c_mod['name']} en {label.get(owner, owner)} no "
                                            "lo recoge."})
        # 3. Peticiones al dueño: atendidas si el dueño las cita en sus orígenes.
        for p in pets:
            if p["estado"].lower().startswith(RETIRADA):
                continue
            owner = p["owner"]
            atendida = owner in contratos and any(
                p["id"] in o["rids"] for m in contratos[owner].values() for o in m["origenes"])
            if not atendida:
                peticiones.append({"consumidor": c, "owner": owner, "id": p["id"],
                                   "modelo": p["modelo"], "titulo": p["titulo"],
                                   "que": f"{label.get(c, c)} pide a "
                                          f"{label.get(owner, owner or 'su dueña')}: "
                                          + re.sub(r"^A\s+F-\S+\s*(\([^)]*\))?\s*:\s*", "",
                                                   p["titulo"])})

    return {"anteriores_a_d111": anteriores, "sin_contrato": sin_contrato, "catalogo": catalogo,
            "peticiones": peticiones, "no_declaradas": no_declaradas, "uso": uso,
            "bloquea": bool(sin_contrato or catalogo or peticiones)}


def problemas_de(data: dict, fid: str) -> list[str]:
    """Lo que impide sellar `fid` (condición 10 de `sdd-seal.py spec`)."""
    out = [p["que"] for p in data["sin_contrato"] if p["owner"] == fid]
    out += [p["que"] for p in data["catalogo"] if p["owner"] == fid]
    out += [f"{p['id']} sin atender: {p['que']}" for p in data["peticiones"]
            if p["consumidor"] == fid]
    return out


def spec_root(spec_path: Path) -> Path | None:
    """La raíz de artefactos spec de un spec: el ancestro que tiene `*_features.md`."""
    for d in spec_path.resolve().parents:
        if any(d.glob("*_features.md")):
            return d
    return None


def render(data: dict) -> str:
    out = ["# Contratos de modelos compartidos", ""]
    secciones = [("Dueñas sin contrato publicado", data["sin_contrato"]),
                 ("Catálogo de orígenes incompleto", data["catalogo"]),
                 ("Peticiones al dueño sin atender", data["peticiones"]),
                 ("Avisos: dependencias que el índice no declara", data["no_declaradas"])]
    for titulo, lista in secciones:
        if lista:
            out += [f"## {titulo}", ""] + [f"- {p['que']}" for p in lista] + [""]
    if data["anteriores_a_d111"]:
        out += ["## Avisos: specs anteriores a los contratos (no se les exige nada)", "",
                "- " + ", ".join(data["anteriores_a_d111"]), ""]
    if len(out) == 2:
        out.append("Sin problemas: cada regla de un modelo compartido tiene su dueño.")
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1 or not Path(args[0]).is_dir():
        print(__doc__.split("Uso:")[1].split("Exit:")[0].strip(), file=sys.stderr)
        return 1
    data = check(Path(args[0]))
    if "--json" in argv:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(render(data))
    return 2 if data["bloquea"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
