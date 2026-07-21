#!/usr/bin/env python3
"""Aplica deterministamente las decisiones de review de un PRD (Q3, DECISIONS D-030).

`wf-prd-review` recoge en el hilo principal, vía `AskUserQuestion`, qué hacer con
cada asunción `[ASN-XXX]` (confirmar / editar / rechazar) y, al sellar, quién
aprobó. Hasta ahora esas ediciones las aplicaba el orquestador leyendo el PRD
entero (`Read`) y reescribiéndolo (`Write`) — lo que reintroduce en el contexto
del hilo principal el documento que el Paso 3 pide NO cargar. Este script hace esa
edición MECÁNICA (Regla 9 de `kb-sdd-conformance`: lo mecanizable no se deja al
juicio de un agente) para que main la invoque por `Bash` sin cargar el PRD.

Ligadura inline↔entrada. El marcador inline es anónimo (`[ASUNCIÓN]`, sin ID, por
diseño de `kb-prd-expert`), así que cada entrada `[ASN-XXX]` se empareja con su marca
en dos pasadas: (1) por TEXTO exacto normalizado cuando la entrada cita la afirmación
literal y es único; (2) para las residuales (la creación a veces parafrasea o abrevia
la entrada), por MÁXIMO SOLAPAMIENTO de palabras de contenido, asignación golosa por
puntuación descendente y determinista. Ni el orden ni el texto exacto están garantizados
por la creación por separado —una PRD real emitió el cuerpo (exclusiones) y la sección
(numeración) en órdenes distintos y con paráfrasis—, pero texto+solapamiento sí es robusto.
Guardas:
  - precondición dura: si al entrar el 1:1 no cuadra, exit 2 (resuélvelo antes).
  - fail-safe: una entrada a tocar que no case por texto ni comparta ninguna palabra de
    contenido con marca alguna no se asigna → exit 2 en vez de editar a ciegas.

Fuera de alcance (límite honesto, heredado de Q2a/D-029): borrar prosa de brief que
dependía de una asunción rechazada (líneas sin marca). La cascada asunción↔asunción
la resuelve el gate con `sdd-prd-deps.py`; aquí solo se APLICAN las decisiones ya
tomadas.

Uso:
    # Aplicar decisiones de asunciones (modo review, Paso 5.5):
    sdd-prd-apply.py <prd.md> [--confirm ASN-001,ASN-002] \\
        [--edit ASN-004="texto nuevo"] [--reject ASN-006,ASN-007] [--json]

    # Sellar la aprobación (Paso 6, ortogonal — no combinar con lo anterior):
    sdd-prd-apply.py <prd.md> --seal "Nombre (Rol) (YYYY-MM-DD)" [--json]

Exit codes:
    0 = aplicado
    1 = error de uso o IO
    2 = precondición 1:1 rota / desalineación / ASN inexistente / sello no hallado
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ASSUMPTION_RE = re.compile(r"\[ASUNCIÓN")
# marca completa a eliminar de la línea inline (canónica y variante verbosa)
ASSUMPTION_MARK_RE = re.compile(r"\s*\[ASUNCIÓN[^\]]*\]")
ASN_ENTRY_RE = re.compile(r"\[ASN-\d+\]")
ASSUMPTIONS_HEADING_RE = re.compile(r"^\s*#{1,6}\s+Asunciones del PRD\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^\s*#{1,6}\s+")
# prefijo de lista/heading que se conserva al editar (`- `, `* `, `#### `, …)
PREFIX_RE = re.compile(r"^(\s*(?:[-*+]\s+|#{1,6}\s+)?)")
# valor del sello: conserva todo hasta `Aprobado por:` (con negrita opcional)
SEAL_LINE_RE = re.compile(r"^(?P<prefix>.*?Aprobado por:\**)\s*.*$")
# palabras de contenido (≥4, admite acentos/ñ) para la guarda de desalineación
WORD_RE = re.compile(r"[0-9a-záéíóúüñ]{4,}", re.IGNORECASE)


class ApplyError(Exception):
    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


def _content_words(text: str) -> set:
    return {w.lower() for w in WORD_RE.findall(text)}


def _entry_assertion(line: str) -> str:
    """Texto de la afirmación de una entrada `[ASN-XXX]` (tras el ID, hasta ` · `)."""
    m = ASN_ENTRY_RE.search(line)
    after = line[m.end():] if m else line
    after = after.lstrip(" *—-·:").strip()
    return after.split(" · ")[0].strip().strip('"“”').strip()


def _inline_assertion(line: str) -> str:
    """Texto de una línea inline sin su prefijo de lista/heading ni el marcador."""
    body = ASSUMPTION_MARK_RE.sub("", line)
    prefix = PREFIX_RE.match(body).group(1)
    return body[len(prefix):].strip().strip('"“”').strip()


def _normalize(text: str) -> str:
    """Forma canónica para comparar afirmación de entrada vs línea inline."""
    t = re.sub(r"[^0-9a-záéíóúüñ ]+", " ", text.lower())
    return re.sub(r"\s+", " ", t).strip()


def parse_structure(text: str) -> dict:
    """Localiza marcas inline (índices en orden de doc) y entradas `[ASN-XXX]`.

    Reproduce la exclusión de prosa de `sdd-prd-ready.py`: no cuenta como marca
    inline el interior de `## Asunciones del PRD` ni los callouts `>`.
    """
    lines = text.split("\n")
    inline_lines: list[int] = []       # índices de línea con marca inline
    raw_occurrences = 0                 # total de tokens `[ASUNCIÓN` (para el 1:1)
    entries: list[tuple[str, int]] = []  # (asn_id, índice de línea) en orden de sección
    in_section = False
    section_start = None
    section_end = None

    for i, line in enumerate(lines):
        if ASSUMPTIONS_HEADING_RE.match(line):
            in_section = True
            section_start = i
            continue
        if in_section and HEADING_RE.match(line):
            in_section = False
            section_end = i
        if in_section:
            m = ASN_ENTRY_RE.search(line)
            if m:
                entries.append((m.group(0).strip("[]"), i))
            continue
        if line.lstrip().startswith(">"):
            continue
        hits = ASSUMPTION_RE.findall(line)
        if hits:
            inline_lines.append(i)
            raw_occurrences += len(hits)

    if section_start is not None and section_end is None:
        section_end = len(lines)

    return {
        "lines": lines,
        "inline_lines": inline_lines,
        "raw_occurrences": raw_occurrences,
        "entries": entries,
        "section_start": section_start,
        "section_end": section_end,
    }


def _strip_trailing_separator(lines: list[str]) -> list[str]:
    """Quita líneas en blanco finales y un único `---` colgante al final."""
    while lines and lines[-1].strip() == "":
        lines.pop()
    if lines and lines[-1].strip() == "---":
        lines.pop()
        while lines and lines[-1].strip() == "":
            lines.pop()
    return lines


def apply_decisions(text: str, confirm: set, edit: dict, reject: set) -> tuple:
    """Aplica confirm/edit/reject por mapeo posicional. Devuelve (nuevo_texto, dict)."""
    st = parse_structure(text)
    lines = st["lines"]
    inline_lines = st["inline_lines"]
    entries = st["entries"]

    # Precondición 1:1 (misma semántica que sdd-prd-ready.py).
    n_inline = len(inline_lines)
    if st["raw_occurrences"] != n_inline:
        raise ApplyError(
            f"formato inesperado: {st['raw_occurrences']} token(s) [ASUNCIÓN] en "
            f"{n_inline} línea(s) — se espera una marca por línea."
        )
    if n_inline != len(entries):
        raise ApplyError(
            f"1:1 roto: {n_inline} marca(s) inline vs {len(entries)} entrada(s) "
            "[ASN-XXX]. Resuélvelo con sdd-prd-ready.py antes de aplicar."
        )

    targeted = confirm | set(edit) | reject
    entry_line_by_id = {asn: eidx for asn, eidx in entries}
    unknown = sorted(a for a in targeted if a not in entry_line_by_id)
    if unknown:
        raise ApplyError(f"asunción(es) inexistente(s): {', '.join(unknown)}")
    overlap = (confirm & set(edit)) | (confirm & reject) | (set(edit) & reject)
    if overlap:
        raise ApplyError(
            f"decisión ambigua (misma ASN en más de una acción): {', '.join(sorted(overlap))}",
            code=1,
        )

    # --- Ligadura marca-inline ↔ entrada --------------------------------
    # El marcador inline es anónimo, así que se empareja por TEXTO (las entradas
    # citan la afirmación casi literal) y, para las que no casan por texto único,
    # por POSICIÓN entre las residuales. Ni el orden ni el texto están garantizados
    # por la creación por separado (una PRD real emitió cuerpo y sección en órdenes
    # distintos — regresión en test_sdd_prd_apply), pero su combinación es robusta.
    body = [(idx, _normalize(_inline_assertion(lines[idx]))) for idx in inline_lines]
    ent = [(asn, _normalize(_entry_assertion(lines[eidx]))) for asn, eidx in entries]
    body_text_count = Counter(t for _, t in body)
    body_by_text: dict = {}
    for idx, t in body:
        body_by_text.setdefault(t, []).append(idx)

    pair: dict = {}     # asn -> índice de línea inline
    used: set = set()
    residual_entries = []
    for asn, t in ent:
        cands = [i for i in body_by_text.get(t, []) if i not in used]
        if t and body_text_count[t] == 1 and cands:
            pair[asn] = cands[0]
            used.add(cands[0])
        else:
            residual_entries.append(asn)

    # Residuales (la creación parafrasea algunas entradas: ni texto exacto ni
    # posición sirven). Se asignan por MÁXIMO SOLAPAMIENTO de palabras de
    # contenido, de forma golosa por puntuación descendente (los pares fuertes
    # primero), y determinista. Un residual sin ninguna palabra en común no se
    # asigna → desalineación (exit 2), nunca se edita a ciegas.
    residual_body = [idx for idx, _ in body if idx not in used]
    entry_words = {asn: _content_words(_entry_assertion(lines[entry_line_by_id[asn]]))
                   for asn in residual_entries}
    body_words = {idx: _content_words(_inline_assertion(lines[idx])) for idx in residual_body}
    scored = sorted(
        (
            (-len(entry_words[asn] & body_words[idx]), asn, idx)
            for asn in residual_entries for idx in residual_body
        ),
        key=lambda s: (s[0], s[1], s[2]),
    )
    asn_done: set = set()
    body_done: set = set()
    for neg, asn, idx in scored:
        if neg == 0 or asn in asn_done or idx in body_done:
            continue
        pair[asn] = idx
        asn_done.add(asn)
        body_done.add(idx)
    missing = sorted(a for a in residual_entries if a in targeted and a not in asn_done)
    if missing:
        raise ApplyError(
            f"desalineación en {', '.join(missing)}: ninguna marca inline comparte "
            "contenido con la entrada (¿1:1 correcto? ¿PRD editado a mano?) — no edito a ciegas."
        )

    to_delete: set = set()
    to_modify: dict = {}

    for asn in targeted:
        entry_idx = entry_line_by_id[asn]
        inline_idx = pair[asn]
        inline_line = lines[inline_idx]

        # La entrada de la sección se elimina en los tres casos.
        to_delete.add(entry_idx)
        if asn in reject:
            to_delete.add(inline_idx)
        elif asn in confirm:
            to_modify[inline_idx] = ASSUMPTION_MARK_RE.sub("", inline_line).rstrip()
        else:  # edit
            prefix = PREFIX_RE.match(inline_line).group(1)
            to_modify[inline_idx] = prefix + edit[asn].strip()

    # ¿queda alguna entrada tras las bajas? Si no, elimina la sección entera.
    section_removed = False
    remaining = [idx for _, idx in entries if idx not in to_delete]
    if not remaining and st["section_start"] is not None:
        for i in range(st["section_start"], st["section_end"]):
            to_delete.add(i)
        section_removed = True

    out = [
        to_modify.get(i, line)
        for i, line in enumerate(lines)
        if i not in to_delete
    ]
    if section_removed:
        out = _strip_trailing_separator(out)

    result = {
        "confirmed": sorted(confirm),
        "edited": sorted(edit),
        "rejected": sorted(reject),
        "section_removed": section_removed,
    }
    return "\n".join(out), result


def apply_seal(text: str, value: str) -> tuple:
    """Sustituye el valor de la línea `Aprobado por:` (sobrescribe en re-revisión)."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = SEAL_LINE_RE.match(line)
        if m:
            lines[i] = f"{m.group('prefix')} {value.strip()}"
            return "\n".join(lines), {"sealed": value.strip()}
    raise ApplyError("no se encontró la línea `Aprobado por:` para sellar.")


def _parse_args(argv):
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    confirm: set = set()
    reject: set = set()
    edit: dict = {}
    seal = None
    rest = []
    it = iter(args)
    for a in it:
        if a == "--confirm":
            confirm |= {x.strip() for x in (next(it, "") or "").split(",") if x.strip()}
        elif a == "--reject":
            reject |= {x.strip() for x in (next(it, "") or "").split(",") if x.strip()}
        elif a == "--edit":
            spec = next(it, "") or ""
            if "=" not in spec:
                raise ApplyError('--edit requiere ASN-XXX="texto nuevo"', code=1)
            asn, new = spec.split("=", 1)
            edit[asn.strip()] = new
        elif a == "--seal":
            seal = next(it, None)
            if seal is None:
                raise ApplyError('--seal requiere un valor "Nombre (Rol) (fecha)"', code=1)
        else:
            rest.append(a)
    return as_json, rest, confirm, reject, edit, seal


def main() -> int:
    try:
        as_json, rest, confirm, reject, edit, seal = _parse_args(sys.argv[1:])
    except ApplyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return e.code

    if len(rest) != 1:
        print(
            'ERROR: uso: sdd-prd-apply.py <prd.md> [--confirm A,B] '
            '[--edit ASN-XXX="texto"] [--reject C,D] | --seal "valor" [--json]',
            file=sys.stderr,
        )
        return 1

    has_decisions = bool(confirm or reject or edit)
    if seal is not None and has_decisions:
        print("ERROR: --seal es ortogonal; no lo combines con --confirm/--edit/--reject.",
              file=sys.stderr)
        return 1
    if seal is None and not has_decisions:
        print("ERROR: nada que aplicar (indica --confirm/--edit/--reject o --seal).",
              file=sys.stderr)
        return 1

    path = Path(rest[0])
    try:
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except OSError as e:
        print(f"ERROR: no se puede leer el PRD: {e}", file=sys.stderr)
        return 1

    try:
        if seal is not None:
            new_text, result = apply_seal(text, seal)
        else:
            new_text, result = apply_decisions(text, confirm, edit, reject)
    except ApplyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return e.code

    try:
        path.write_text(new_text, encoding="utf-8")
    except OSError as e:
        print(f"ERROR: no se puede escribir el PRD: {e}", file=sys.stderr)
        return 1

    result["path"] = str(path)
    if as_json:
        print(json.dumps(result, ensure_ascii=False))
    elif seal is not None:
        print(f"OK: {path} — sellado: {result['sealed']}")
    else:
        det = []
        if result["confirmed"]:
            det.append(f"confirmadas {', '.join(result['confirmed'])}")
        if result["edited"]:
            det.append(f"editadas {', '.join(result['edited'])}")
        if result["rejected"]:
            det.append(f"rechazadas {', '.join(result['rejected'])}")
        extra = " · sección de asunciones vaciada y eliminada" if result["section_removed"] else ""
        print(f"OK: {path} — {'; '.join(det)}{extra}.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
