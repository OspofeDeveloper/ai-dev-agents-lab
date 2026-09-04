#!/usr/bin/env python3
"""Verificador y aplicador determinista de los gaps de un `_analysis.md`.

Dos trabajos, los dos mecanizables al 100% y hoy hechos a ojo (ver DECISIONS D-042):

1. `--check` — ¿quedan gaps `[CRÍTICO]` sin responder? De esa respuesta cuelgan dos
   ramas duras de `wf-spec-features-first` (detenerse, o continuar aceptando HUs
   `[INCOMPLETO]` con `--allow-open-critical-gaps`) y el cierre de
   `wf-spec-gap-resolve`. Hasta ahora lo decidía un agente leyendo prosa: contar
   marcadores `_(pendiente)_` no es juicio, es un conteo.

2. `--list` — los gaps con su PREGUNTA, para que el orquestador arme el gate sin abrir
   el fichero. `--check` da recuento e IDs, pero el mensaje del gate tiene que decir QUÉ
   se pregunta en cada uno; hasta ahora eso solo llegaba dentro del informe del delegado,
   y una sesión que retomaba el trabajo se quedaba sin vía sancionada.

3. `--answer` — escribir la respuesta que el usuario DICTA en el chat en vez de
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
    sdd-analysis-gaps.py <analysis.md> --list [--json]
    sdd-analysis-gaps.py <analysis.md> --answer P-001 "texto de la respuesta" [--force] [--json]
    sdd-analysis-gaps.py <analysis.md> --export-answers
    sdd-analysis-gaps.py <analysis.md> --import-answers <respuestas.json> [--force] [--json]

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
# El `\s*` entre grupos tolera la variante espaciada (`[CRÍTICO] [PUEDE_REQUERIR_CR]`):
# sin él, el flag se cuela en el titulo y DESAPARECE de `flags`, en silencio. Y por ese
# flag enruta el gate de gobernanza de wf-spec-features-first (D-052), asi que la
# degradacion no da error: simplemente el gate no se abre nunca.
GAP_HEADING_RE = re.compile(
    r"^\s*#{1,6}\s+\[(?P<id>[PD]-\d+)\](?P<flags>(?:\s*\[[^\]\n]+\])*)\s*(?P<title>.*)$"
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


# Campos etiquetados dentro del bloque de un gap: `- **Contexto**: ...`.
FIELD_RE = re.compile(
    r"^\s*[-*+]\s*\**\s*(?P<label>[^:*][^:]*?)\s*\**\s*:\s*(?P<value>.*)$")
# Etiqueta del informe -> clave que emite `--list`. `Respuesta` NO esta aqui a
# proposito: el texto de las respuestas lo da `--export-answers`, no este modo.
LIST_FIELDS = {
    "contexto": "contexto",
    "problema": "problema",
    "afecta": "afecta",
    "pregunta para el cliente": "question",
}


def _gap_fields(lines, start, end) -> dict:
    """Campos etiquetados de UN bloque de gap, verbatim y con continuaciones.

    Un campo puede seguir en las lineas siguientes mientras no empiece otro bullet,
    otro encabezado ni una linea en blanco. Se devuelve tal cual esta escrito: este
    texto se le ENSENA al usuario para que responda, asi que resumirlo o
    reformatearlo seria degradar justo lo que tiene que leer.
    """
    out, label, buf = {}, None, []

    def flush():
        if label and label not in out:
            out[label] = " ".join(buf).strip()

    for j in range(start, end):
        line = lines[j]
        if HEADING_RE.match(line):
            break
        m = FIELD_RE.match(line)
        if m:
            flush()
            key = LIST_FIELDS.get(" ".join(m.group("label").lower().split()))
            label, buf = key, [m.group("value").strip()]
            continue
        if label is None:
            continue
        if not line.strip() or re.match(r"^\s*[-*+]\s", line):
            flush()
            label, buf = None, []
            continue
        buf.append(line.strip())
    flush()
    return {k: v for k, v in out.items() if k}


def list_gaps(text: str, source: str, only_gap: str = None) -> dict:
    """Los gaps con su PREGUNTA Y SU CONTEXTO, para que el orquestador arme el gate
    y presente cada gap sin abrir el fichero.

    `--check` da el recuento y los IDs, pero el mensaje del gate tiene que decir
    **qué se pregunta en cada uno** ([[D-042]]). Hasta ahora eso solo llegaba dentro
    del informe del delegado, así que en una sesión que retoma el trabajo —los gaps se
    responden un martes y se sigue el jueves— main se quedaba sin vía sancionada y
    acababa grepeando prosa del artefacto. Esto es esa vía.

    Emite también `contexto`, `problema` y `afecta` ([[D-053]]): sin ellos la pregunta
    llega pelada, y son los campos que dicen POR QUÉ importa y CUÁNTO detalle hace
    falta. Van **verbatim**: main es un relé hacia la pantalla, no un resumidor.

    Emite metadatos, no el documento. **No** emite el texto de la respuesta — para eso
    está `--export-answers`.
    """
    lines = text.splitlines()
    gaps = parse_gaps(text)
    # El bloque de un gap va de su encabezado al siguiente encabezado (de gap o no).
    starts = [i for i, line in enumerate(lines) if GAP_HEADING_RE.match(line)]
    bounds = {}
    for n, s0 in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        for j in range(s0 + 1, end):
            if HEADING_RE.match(lines[j]) and not GAP_HEADING_RE.match(lines[j]):
                end = j
                break
        bounds[s0] = end
    fields = {}
    for s0 in starts:
        gid = GAP_HEADING_RE.match(lines[s0]).group("id")
        fields[gid] = _gap_fields(lines, s0 + 1, bounds[s0])
    if only_gap is not None:
        known = [g["id"] for g in gaps]
        if only_gap not in known:
            raise GapError(
                f"{only_gap} no existe en el informe. IDs validos: "
                + (", ".join(known) if known else "(ninguno)"))
        gaps = [g for g in gaps if g["id"] == only_gap]
    return {
        "action": "list",
        "source": source,
        "total": len(gaps),
        "gaps": [
            {"id": g["id"], "severity": g["severity"], "flags": g["flags"],
             "title": g["title"],
             "question": fields.get(g["id"], {}).get("question"),
             "contexto": fields.get(g["id"], {}).get("contexto"),
             "problema": fields.get(g["id"], {}).get("problema"),
             "afecta": fields.get(g["id"], {}).get("afecta"),
             "answered": g["answered"]}
            for g in gaps
        ],
    }


def _norm_title(title: str) -> str:
    """Título normalizado para emparejar: minúsculas, espacios colapsados, sin
    puntuación de cierre. NO se hace matching difuso a propósito (ver export_answers)."""
    return " ".join(title.lower().split()).rstrip(" .:;,")


def export_answers(text: str, source: str) -> dict:
    """Extrae las respuestas ya escritas, para poder devolverlas a un análisis nuevo.

    Existe porque regenerar un `_analysis.md` lo SOBRESCRIBE: las respuestas que el
    usuario dio se pierden, y un cambio de PRD después de responder los gaps no es un
    caso raro — es el caso normal ([[D-051]]).
    """
    gaps = parse_gaps(text)
    return {
        "action": "export-answers",
        "source": source,
        "exported": sum(1 for g in gaps if g["answered"]),
        "answers": [
            {"id": g["id"], "severity": g["severity"], "flags": g["flags"],
             "title": g["title"], "answer": g["answer"]}
            for g in gaps if g["answered"]
        ],
    }


def import_answers(text: str, payload: dict, force: bool):
    """Devuelve las respuestas exportadas a un análisis recién regenerado.

    **Empareja por ID Y por título, y no adivina.** El análisis no es reproducible
    (medido en conformance: mismo PRD byte-idéntico → 11/5, 12/7, 11/7, 16/11, 5/2 y
    7/4 gaps en pasadas sucesivas), así que un mismo `P-XXX` puede ser otra pregunta
    en el documento nuevo. Lo que no case exacto **no se escribe**: se reporta para que
    lo reconcilie quien tiene los dos documentos delante. Un script que adivina aquí
    daría falso rigor, y el falso rigor en una respuesta de negocio es peor que el hueco.
    """
    target = parse_gaps(text)
    if not target:
        raise GapError(
            "el análisis destino no contiene ningún bloque de gap: no se ha podido "
            "parsear (¿es el `_analysis.md`?)")
    by_id = {g["id"]: g for g in target}
    applied, needs_review = [], []
    for item in payload.get("answers") or []:
        gid, title, ans = item.get("id"), item.get("title") or "", item.get("answer")
        dest = by_id.get(gid)
        if dest is None:
            needs_review.append({**item, "reason": "id_ausente"})
            continue
        if _norm_title(dest["title"]) != _norm_title(title):
            needs_review.append({**item, "reason": "titulo_distinto",
                                 "destino_title": dest["title"]})
            continue
        if dest["answered"] and not force:
            needs_review.append({**item, "reason": "ya_respondido",
                                 "destino_answer": dest["answer"]})
            continue
        text, _ = apply_answer(text, gid, ans, force=True)
        by_id = {g["id"]: g for g in parse_gaps(text)}
        applied.append({"id": gid, "title": title})

    after = check(parse_gaps(text))
    return text, {
        "action": "import-answers",
        "applied": len(applied),
        "applied_ids": [a["id"] for a in applied],
        "needs_review": needs_review,
        "verdict": after["verdict"],
        "critical_open": after["critical_open"],
        "critical_open_ids": after["critical_open_ids"],
    }


def _parse_args(argv):
    as_json = False
    force = False
    do_check = False
    do_export = False
    do_list = False
    only_gap = None
    import_path = None
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
        elif a == "--export-answers":
            do_export = True
        elif a == "--list":
            do_list = True
        elif a == "--gap":
            only_gap = next(it, None)
            if only_gap is None:
                raise GapError("--gap requiere <P-XXX>", code=1)
        elif a == "--import-answers":
            import_path = next(it, None)
            if import_path is None:
                raise GapError("--import-answers requiere <respuestas.json>", code=1)
        elif a == "--answer":
            gap_id = next(it, None)
            value = next(it, None)
            if gap_id is None or value is None:
                raise GapError('--answer requiere <P-XXX> "texto de la respuesta"', code=1)
            answer = (gap_id, value)
        else:
            rest.append(a)
    return (as_json, force, do_check, do_export, do_list, only_gap,
            import_path, answer, rest)


def main() -> int:
    try:
        (as_json, force, do_check, do_export, do_list, only_gap, import_path,
         answer, rest) = _parse_args(sys.argv[1:])
    except GapError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return e.code

    modes = [do_check, do_export, do_list, import_path is not None, answer is not None]
    if len(rest) != 1 or sum(1 for m in modes if m) != 1:
        print('ERROR: uso: sdd-analysis-gaps.py <analysis.md> --check [--json] | '
              '--answer P-XXX "texto" [--force] [--json] | --export-answers | '
              '--import-answers <respuestas.json> [--force] [--json] | --list', file=sys.stderr)
        return 1

    path = Path(rest[0])
    try:
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except OSError as e:
        print(f"ERROR: no se puede leer el análisis: {e}", file=sys.stderr)
        return 1

    if do_export:
        print(json.dumps(export_answers(text, str(path)), ensure_ascii=False, indent=2))
        return 0

    if do_list:
        try:
            result = list_gaps(text, str(path), only_gap)
        except GapError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return e.code
        if as_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            for g in result["gaps"]:
                flags = "".join(f"[{f}]" for f in g["flags"])
                mark = "✓" if g["answered"] else "·"
                print(f"{mark} {g['id']}{flags} {g['title']}")
                if only_gap:
                    for label in ("contexto", "problema", "afecta"):
                        if g.get(label):
                            print(f"    {label.capitalize()}: {g[label]}")
                if g["question"]:
                    print(f"    {g['question']}")
        return 0

    if import_path is not None:
        try:
            payload = json.loads(Path(import_path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"ERROR: no se puede leer el export de respuestas: {e}",
                  file=sys.stderr)
            return 1
        try:
            new_text, result = import_answers(text, payload, force)
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
            print(f"OK: {result['applied']} respuesta(s) devueltas "
                  f"({', '.join(result['applied_ids']) or '—'}).")
            for nr in result["needs_review"]:
                print(f"  SIN APLICAR {nr['id']} [{nr['reason']}]: {nr['title']}")
            if result["needs_review"]:
                print("  → Reconcílialas a mano: el análisis no es reproducible y un "
                      "mismo P-XXX puede ser otra pregunta. No se adivina.")
        return 2 if result["needs_review"] else 0

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
