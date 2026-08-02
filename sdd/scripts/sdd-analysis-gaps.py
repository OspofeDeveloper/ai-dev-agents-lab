#!/usr/bin/env python3
"""Verificador y aplicador determinista de los gaps de un `_analysis.md`.

Dos trabajos, los dos mecanizables al 100% y hoy hechos a ojo (ver DECISIONS D-042):

1. `--check` — ¿quedan gaps `[CRÍTICO]` sin responder? De esa respuesta cuelgan dos
   ramas duras de `wf-spec-features-first` (detenerse, o continuar aceptando HUs
   `[INCOMPLETO]` con `--allow-open-critical-gaps`) y el cierre de
   `wf-spec-gap-resolve`. Hasta ahora lo decidía un agente leyendo prosa: contar
   marcadores `_(pendiente)_` no es juicio, es un conteo.

2. `--answer` — escribir la respuesta que el usuario DICTA en el chat en vez de
   editar el fichero. La vía normativa sigue siendo que el usuario edite el
   `_analysis.md`; cuando dicta, el hilo principal ejecuta este script y NO hace
   `Read`/`Edit`/`Write` del artefacto (mismo reparto que `sdd-prd-apply.py` en la
   fase PRD). La sustitución es mecánica: nadie interpreta la respuesta.

El formato del gap es SSoT de `kb-gap-conventions` (§"Formato de un gap en un informe
de análisis"):

    ### [P-001][CRÍTICO][PUEDE_REQUERIR_CR] Título del gap
    - **Contexto**: ...
    - **Afecta**: ...
    - **Pregunta para el cliente**: ...
    - **Respuesta**: _(pendiente)_

Se aceptan campos EXTRA dentro del bloque (los informes reales añaden p. ej.
`- **Problema**:`) y los IDs `[D-XXX]` de los delta analysis, no solo `[P-XXX]`.

Uso:
    sdd-analysis-gaps.py <analysis.md> --check [--json]
    sdd-analysis-gaps.py <analysis.md> --answer P-001 "texto de la respuesta" [--force] [--json]

Exit codes: 0 = ok; 1 = error de uso o IO; 2 = veredicto bloqueante / precondición fallida.

Veredictos de `--check`:
    VACUOUS             el documento no tiene NINGÚN bloque de gap: no se ha sabido
                        parsear. Es exit 2 a propósito (lección de D-037): un
                        verificador que responde "0 críticos abiertos" sobre un
                        documento que no entiende es un no-op silencioso.
    CRITICAL_OPEN       quedan gaps `[CRÍTICO]` con `_(pendiente)_`.
    CRITICAL_ANSWERED   ningún `[CRÍTICO]` abierto (los `[INFORMATIVO]` nunca bloquean:
                        se reportan porque cada uno aplicará su "Asunción por defecto").
"""
import json
import re
import sys
from pathlib import Path

PENDING = "_(pendiente)_"

# `### [P-001][CRÍTICO][PUEDE_REQUERIR_CR] Título` — el ID y los flags entre corchetes.
GAP_HEADING_RE = re.compile(
    r"^\s*#{1,6}\s+\[(?P<id>[PD]-\d+)\](?P<flags>(?:\[[^\]\n]+\])*)\s*(?P<title>.*)$"
)
HEADING_RE = re.compile(r"^\s*#{1,6}\s+")
# `- **Respuesta**: valor` (tolera `*`/`_` y espacios alrededor del rótulo).
ANSWER_RE = re.compile(r"^(?P<prefix>\s*[-*+]\s*\**\s*Respuesta\s*\**\s*:\s*)(?P<value>.*)$")
FLAG_RE = re.compile(r"\[([^\]]+)\]")

CRITICAL = "CRÍTICO"
INFORMATIVE = "INFORMATIVO"


class GapError(Exception):
    def __init__(self, msg, code=2):
        super().__init__(msg)
        self.code = code


def parse_gaps(text: str) -> list:
    """Devuelve la lista de gaps del documento, en orden de aparición.

    Cada gap: {id, severity, flags, title, answered, answer, answer_line}
    `answer_line` es el índice 0-based de la línea `- **Respuesta**:` (o None si el
    bloque no la tiene — informe malformado, que `--answer` rechaza explícitamente).
    """
    lines = text.splitlines()
    gaps = []
    current = None
    for i, line in enumerate(lines):
        m = GAP_HEADING_RE.match(line)
        if m:
            flags = FLAG_RE.findall(m.group("flags") or "")
            severity = CRITICAL if CRITICAL in flags else (
                INFORMATIVE if INFORMATIVE in flags else None)
            current = {
                "id": m.group("id"),
                "severity": severity,
                "flags": flags,
                "title": m.group("title").strip(),
                "answered": False,
                "answer": None,
                "answer_line": None,
            }
            gaps.append(current)
            continue
        if current is None:
            continue
        if HEADING_RE.match(line):
            current = None  # el bloque del gap termina en el siguiente encabezado
            continue
        if current["answer_line"] is not None:
            continue  # ya tenemos su campo Respuesta; ignoramos repeticiones
        am = ANSWER_RE.match(line)
        if am:
            value = am.group("value").strip()
            current["answer_line"] = i
            current["answer"] = value
            current["answered"] = bool(value) and value != PENDING
    return gaps


def check(gaps: list) -> dict:
    crit = [g for g in gaps if g["severity"] == CRITICAL]
    info = [g for g in gaps if g["severity"] == INFORMATIVE]
    crit_open = [g for g in crit if not g["answered"]]
    info_open = [g for g in info if not g["answered"]]
    if not gaps:
        verdict = "VACUOUS"
    elif crit_open:
        verdict = "CRITICAL_OPEN"
    else:
        verdict = "CRITICAL_ANSWERED"
    return {
        "verdict": verdict,
        "total": len(gaps),
        "critical_total": len(crit),
        "critical_open": len(crit_open),
        "critical_open_ids": [g["id"] for g in crit_open],
        "informative_total": len(info),
        "informative_open": len(info_open),
        "informative_open_ids": [g["id"] for g in info_open],
        "gaps": [{k: g[k] for k in ("id", "severity", "flags", "title", "answered")}
                 for g in gaps],
    }


DETAIL = {
    "VACUOUS": (
        "el documento no contiene ningún bloque de gap `[P-XXX]`/`[D-XXX]`. No es "
        "\"sin gaps críticos\": es que no se ha podido parsear — comprueba que el path "
        "es el `_analysis.md` y que respeta el formato de `kb-gap-conventions`."
    ),
    "CRITICAL_OPEN": (
        "quedan {critical_open} de {critical_total} gap(s) `[CRÍTICO]` sin responder "
        "({critical_open_str}). Respóndelos en el fichero (campo `- **Respuesta**:`) o "
        "continúa aceptando HUs `[INCOMPLETO]` con `--allow-open-critical-gaps`."
    ),
    "CRITICAL_ANSWERED": (
        "ningún gap `[CRÍTICO]` abierto ({critical_total} respondido(s) de "
        "{critical_total}); {informative_open} `[INFORMATIVO]` sin responder aplicarán "
        "su asunción por defecto."
    ),
}


def apply_answer(text: str, gap_id: str, answer: str, force: bool):
    """Sustituye `_(pendiente)_` por `answer` en el campo Respuesta de `gap_id`.

    Precondiciones fail-safe (exit 2, sin escribir): el gap existe, tiene campo
    Respuesta, y sigue en `_(pendiente)_` salvo `--force`. Nunca se pisa en silencio
    una respuesta ya escrita por una persona.
    """
    gaps = parse_gaps(text)
    if not gaps:
        raise GapError(
            "el documento no contiene ningún bloque de gap: no se ha podido parsear "
            "(¿es el `_analysis.md`?)")
    target = next((g for g in gaps if g["id"] == gap_id), None)
    if target is None:
        ids = ", ".join(g["id"] for g in gaps)
        raise GapError(f"el gap {gap_id} no existe en el documento. IDs válidos: {ids}")
    if target["answer_line"] is None:
        raise GapError(
            f"el bloque de {gap_id} no tiene campo `- **Respuesta**:`; el informe está "
            f"malformado respecto a `kb-gap-conventions` y no se toca a ciegas")
    # Normalizamos espacios: la respuesta ocupa UNA línea de bullet markdown. Se
    # reporta el texto final para que quede a la vista qué se escribió.
    normalized = " ".join(answer.split())
    if not normalized:
        raise GapError("la respuesta está vacía", code=1)
    if normalized == PENDING:
        raise GapError("la respuesta no puede ser el propio marcador de pendiente", code=1)
    if target["answered"] and not force:
        raise GapError(
            f"{gap_id} ya tiene respuesta ({target['answer']!r}). No se sobrescribe una "
            f"respuesta humana en silencio: usa --force si de verdad quieres cambiarla")

    lines = text.splitlines(keepends=True)
    idx = target["answer_line"]
    raw = lines[idx]
    newline = "\n" if raw.endswith("\n") else ""
    m = ANSWER_RE.match(raw.rstrip("\n"))
    lines[idx] = f"{m.group('prefix')}{normalized}{newline}"
    new_text = "".join(lines)

    after = check(parse_gaps(new_text))
    result = {
        "action": "answer",
        "gap": gap_id,
        "severity": target["severity"],
        "previous": target["answer"],
        "answer": normalized,
        "overwritten": bool(target["answered"]),
        "verdict": after["verdict"],
        "critical_open": after["critical_open"],
        "critical_open_ids": after["critical_open_ids"],
    }
    return new_text, result


def _parse_args(argv):
    as_json = False
    force = False
    do_check = False
    answer = None
    rest = []
    it = iter(argv)
    for a in it:
        if a == "--json":
            as_json = True
        elif a == "--force":
            force = True
        elif a == "--check":
            do_check = True
        elif a == "--answer":
            gap_id = next(it, None)
            value = next(it, None)
            if gap_id is None or value is None:
                raise GapError('--answer requiere <P-XXX> "texto de la respuesta"', code=1)
            answer = (gap_id, value)
        else:
            rest.append(a)
    return as_json, force, do_check, answer, rest


def main() -> int:
    try:
        as_json, force, do_check, answer, rest = _parse_args(sys.argv[1:])
    except GapError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return e.code

    if len(rest) != 1 or (do_check == (answer is not None)):
        print('ERROR: uso: sdd-analysis-gaps.py <analysis.md> --check [--json] | '
              '--answer P-XXX "texto" [--force] [--json]', file=sys.stderr)
        return 1

    path = Path(rest[0])
    try:
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except OSError as e:
        print(f"ERROR: no se puede leer el análisis: {e}", file=sys.stderr)
        return 1

    if do_check:
        result = check(parse_gaps(text))
        result["path"] = str(path)
        if as_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            detail = DETAIL[result["verdict"]].format(
                critical_open_str=", ".join(result["critical_open_ids"]), **result)
            print(f"{result['verdict']}: {path} — {detail}")
        return 0 if result["verdict"] == "CRITICAL_ANSWERED" else 2

    try:
        new_text, result = apply_answer(text, answer[0], answer[1], force)
    except GapError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return e.code

    try:
        path.write_text(new_text, encoding="utf-8")
    except OSError as e:
        print(f"ERROR: no se puede escribir el análisis: {e}", file=sys.stderr)
        return 1

    result["path"] = str(path)
    if as_json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"OK: {result['gap']} respondido — quedan {result['critical_open']} gap(s) "
              f"`[CRÍTICO]` abierto(s)"
              + (f" ({', '.join(result['critical_open_ids'])})."
                 if result["critical_open_ids"] else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
