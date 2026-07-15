#!/usr/bin/env python3
"""Validador determinista del frontmatter obligatorio de un PRD.

`kb-prd-expert` Regla 3 exige cinco campos en el frontmatter YAML del PRD:
`type`, `product`, `version`, `created`, `status`. El agente `prd-expert` los
transcribe del template, pero al ser disciplina conductual (no determinista)
omite alguno de forma intermitente — observado sobre todo con `status` (CU-2.i).
Este script da la parte VERIFICABLE de esa completitud, en la línea de la Regla 9
de `kb-sdd-conformance`: una propiedad comprobable por máquina no debe depender
del juicio del agente.

En un PRD **recién creado** cuatro de los cinco campos tienen valor canónico
determinista y son AUTO-COMPLETABLES (`--fix`):
    type    → product-requirements
    version → 1.0
    created → fecha de hoy (o `--today YYYY-MM-DD`)
    status  → draft
`product` es contenido real (el nombre del producto): no se inventa. Si falta,
se reporta como hueco de contenido y `--fix` no lo puede cerrar.

Uso:
    sdd-prd-frontmatter.py <prd.md> [--fix] [--json] [--today YYYY-MM-DD]

Exit codes: 0 = frontmatter completo (o completado por --fix); 1 = error de uso
o IO; 2 = incompleto (falta `product`, o falta algún mecánico y no se pasó --fix,
o el fichero no tiene bloque de frontmatter).
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

REQUIRED = ("type", "product", "version", "created", "status")
# Campos con valor canónico en un PRD nuevo. `product` NO está: es contenido.
AUTOFIXABLE = ("type", "version", "created", "status")

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)
KEY_RE = re.compile(r"^\s*([A-Za-z_][\w-]*)\s*:")


def default_value(key: str, today: str) -> str:
    return {
        "type": "product-requirements",
        "version": "1.0",
        "created": today,
        "status": "draft",
    }[key]


def frontmatter_keys(text: str):
    """Claves presentes en el bloque de frontmatter, o None si no hay bloque."""
    m = FRONTMATTER_RE.search(text)
    if not m:
        return None
    keys = set()
    for line in m.group(1).splitlines():
        km = KEY_RE.match(line)
        if km:
            keys.add(km.group(1))
    return keys


def analyze(text: str) -> dict:
    """Función pura sobre el texto: qué campos obligatorios faltan."""
    keys = frontmatter_keys(text)
    if keys is None:
        return {
            "has_frontmatter": False,
            "missing": list(REQUIRED),
            "missing_autofixable": list(AUTOFIXABLE),
            "missing_content": ["product"],
            "complete": False,
        }
    missing = [k for k in REQUIRED if k not in keys]
    return {
        "has_frontmatter": True,
        "missing": missing,
        "missing_autofixable": [k for k in missing if k in AUTOFIXABLE],
        "missing_content": [k for k in missing if k not in AUTOFIXABLE],
        "complete": not missing,
    }


def fix(text: str, today: str):
    """Inserta los campos mecánicos que falten. Devuelve (nuevo_texto, añadidos).

    No toca `product` (contenido). Si no hay bloque de frontmatter, no fabrica uno
    (devuelve el texto intacto y `None`): eso es un problema mayor que reportar.
    """
    m = FRONTMATTER_RE.search(text)
    if not m:
        return text, None
    keys = frontmatter_keys(text)
    to_add = [k for k in AUTOFIXABLE if k not in keys]
    if not to_add:
        return text, []
    block = m.group(1)
    additions = "\n".join(f"{k}: {default_value(k, today)}" for k in to_add)
    new_block = f"{block}\n{additions}"
    new_text = text[: m.start(1)] + new_block + text[m.end(1) :]
    return new_text, to_add


def main() -> int:
    args = sys.argv[1:]
    as_json = "--json" in args
    do_fix = "--fix" in args
    today = date.today().isoformat()
    pos = [a for a in args if not a.startswith("--")]
    # --today <valor>
    if "--today" in args:
        idx = args.index("--today")
        if idx + 1 >= len(args):
            print("ERROR: --today requiere un valor YYYY-MM-DD", file=sys.stderr)
            return 1
        today = args[idx + 1]
        pos = [a for a in pos if a != today]
    if len(pos) != 1:
        print(
            "ERROR: uso: sdd-prd-frontmatter.py <prd.md> [--fix] [--json] [--today YYYY-MM-DD]",
            file=sys.stderr,
        )
        return 1

    path = Path(pos[0])
    try:
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except OSError as e:
        print(f"ERROR: no se puede leer el PRD: {e}", file=sys.stderr)
        return 1

    added = []
    if do_fix:
        new_text, added = fix(text, today)
        if added:
            try:
                path.write_text(new_text, encoding="utf-8")
            except OSError as e:
                print(f"ERROR: no se puede escribir el PRD: {e}", file=sys.stderr)
                return 1
            text = new_text

    result = analyze(text)
    result["path"] = str(path)
    result["fixed"] = added or []

    if as_json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["complete"]:
        msg = "COMPLETO"
        if added:
            msg += f" (añadidos: {', '.join(added)})"
        print(f"{msg}: {path}")
    else:
        parts = []
        if added:
            parts.append(f"añadidos {', '.join(added)}")
        if result["missing_content"]:
            parts.append(
                f"falta contenido no auto-completable: {', '.join(result['missing_content'])}"
            )
        if not result["has_frontmatter"]:
            parts.append("el PRD no tiene bloque de frontmatter YAML")
        elif result["missing_autofixable"] and not do_fix:
            parts.append(
                f"faltan {', '.join(result['missing_autofixable'])} (corrige con --fix)"
            )
        print(f"INCOMPLETO: {path} — {'; '.join(parts)}", file=sys.stderr)

    return 0 if result["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
