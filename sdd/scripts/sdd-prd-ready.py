#!/usr/bin/env python3
"""Detector determinista de readiness de un PRD antes de entrar en la fase spec.

Un PRD está READY para pasar a spec cuando (a) no tiene marcas `[ASUNCIÓN]`
inline sin confirmar y (b) está sellado (línea `Aprobado por:` con un valor
real, no el placeholder `[pendiente…]`). Este script da la parte VERIFICABLE del
gate PRD→spec: el orquestador no decide "el PRD está listo" a ojo ni por la
topología de ficheros (autor≠verificador, mismo principio que sdd-seal.py y
sdd-sync-check.py). Ver DECISIONS D-020.

Además verifica el invariante 1:1 de anti-fabricación (`kb-prd-expert` Regla 12):
nº de marcas inline `[ASUNCIÓN]` == nº de entradas `[ASN-XXX]` de la sección
`## Asunciones del PRD`. El conteo de marcas EXCLUYE menciones en PROSA (líneas
de blockquote/callout `>` como el bloque de origen del PRD o la nota de la
sección, y el interior de `## Asunciones del PRD`, donde viven las entradas) que
no son marcas reales sobre una afirmación de negocio — esa es la falsa-positiva
que inflaba el `grep -c` crudo (CU-2.b).

Uso:
    sdd-prd-ready.py <prd.md> [--json]

Exit codes: 0 = READY; 1 = error de uso o IO; 2 = NO listo.

Veredictos (prioridad de arriba abajo):
    ASSUMPTION_MISMATCH  nº de marcas inline ≠ nº de entradas `[ASN-XXX]` (huérfanas)
    OPEN_ASSUMPTIONS     hay marcas `[ASUNCIÓN]` inline sin confirmar
    UNSEALED             sin marcas abiertas pero falta el sello `Aprobado por:`
    READY                sin asunciones abiertas, 1:1 correcto y sellado
"""
import json
import re
import sys
from pathlib import Path

# `\[ASUNCIÓN` sin exigir el `]` de cierre: detecta el canónico `[ASUNCIÓN]` y la
# variante verbosa `[ASUNCIÓN: …]` (consistente con wf-prd-review Paso 5.5).
ASSUMPTION_RE = re.compile(r"\[ASUNCIÓN")
ASN_ENTRY_RE = re.compile(r"\[ASN-\d+\]")
ASSUMPTIONS_HEADING_RE = re.compile(r"^\s*#{1,6}\s+Asunciones del PRD\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^\s*#{1,6}\s+")
SEAL_RE = re.compile(r"Aprobado por:\s*\**\s*(?P<val>.*?)\s*$", re.MULTILINE)


def analyze(text: str) -> dict:
    """Devuelve conteos + veredicto de readiness. Función pura sobre el texto."""
    lines = text.splitlines()
    inline = 0
    in_assumptions_section = False
    for line in lines:
        if ASSUMPTIONS_HEADING_RE.match(line):
            in_assumptions_section = True
            continue
        if in_assumptions_section and HEADING_RE.match(line):
            in_assumptions_section = False  # otra sección posterior
        # Excluir prosa: entradas de la sección de asunciones y callouts `>`.
        if in_assumptions_section:
            continue
        if line.lstrip().startswith(">"):
            continue
        inline += len(ASSUMPTION_RE.findall(line))

    entries = len(set(ASN_ENTRY_RE.findall(text)))

    m = SEAL_RE.search(text)
    val = (m.group("val").strip().strip("*[]").strip() if m else "")
    sealed = bool(val) and "pendiente" not in val.lower()

    if inline != entries:
        verdict = "ASSUMPTION_MISMATCH"
    elif inline > 0:
        verdict = "OPEN_ASSUMPTIONS"
    elif not sealed:
        verdict = "UNSEALED"
    else:
        verdict = "READY"

    return {
        "verdict": verdict,
        "inline_marks": inline,
        "asn_entries": entries,
        "one_to_one": inline == entries,
        "sealed": sealed,
        "approved_by": val if sealed else None,
    }


DETAIL = {
    "READY": "PRD listo para spec: sin asunciones abiertas, 1:1 correcto y sellado.",
    "OPEN_ASSUMPTIONS": (
        "hay {inline_marks} marca(s) `[ASUNCIÓN]` sin confirmar — revísalas con "
        "wf-prd-review antes de generar specs (o continúa con --allow-unreviewed-prd)."
    ),
    "UNSEALED": (
        "no quedan asunciones abiertas pero el PRD no está sellado (`Aprobado por:` "
        "sigue en placeholder) — cierra la aprobación con wf-prd-review."
    ),
    "ASSUMPTION_MISMATCH": (
        "conteo desalineado: {inline_marks} marca(s) inline vs {asn_entries} entrada(s) "
        "`[ASN-XXX]` — hay una marca huérfana o una entrada sin marca (revisar 1:1)."
    ),
}


def main() -> int:
    args = sys.argv[1:]
    as_json = "--json" in args
    rest = [a for a in args if a != "--json"]
    if len(rest) != 1:
        print("ERROR: uso: sdd-prd-ready.py <prd.md> [--json]", file=sys.stderr)
        return 1

    path = Path(rest[0])
    try:
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except OSError as e:
        print(f"ERROR: no se puede leer el PRD: {e}", file=sys.stderr)
        return 1

    result = analyze(text)
    result["path"] = str(path)

    if as_json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        detail = DETAIL[result["verdict"]].format(**result)
        print(f"{result['verdict']}: {path} — {detail}")

    return 0 if result["verdict"] == "READY" else 2


if __name__ == "__main__":
    sys.exit(main())
