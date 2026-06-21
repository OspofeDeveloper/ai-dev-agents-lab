#!/usr/bin/env python3
# sdd-version: 0.37.0+3cdfd2d
"""Detector determinista de deriva PRD→spec (Fase 1.3 del ROADMAP).

`status_sync` es declarativo: lo escribe el workflow y miente en silencio si
alguien edita el PRD fuera de `wf-prd-change`. Este script añade la parte
VERIFICABLE: sella un hash del contenido del PRD origen en el header del spec
(`derived_from_prd_hash`) y permite recomputarlo después para detectar
divergencia real, sin depender de que nadie declare nada.

Separación autor/verificador (mismo principio que sdd-seal.py): el hash solo
lo escribe este script; los agentes nunca lo rellenan a mano.

Uso:
    sdd-sync-check.py seal <spec.md> [--prd <prd.md>]   # calcula y escribe el hash del PRD origen
    sdd-sync-check.py check <spec.md> [--mark]          # verifica; con --mark degrada status_sync a needs_review si hay deriva
    sdd-sync-check.py check-all <dir> [--mark]          # escanea todos los *_spec.md bajo <dir>

Exit codes: 0 = OK / sin deriva / no aplica; 1 = error de uso o IO; 2 = deriva detectada.

Estados de `check`:
    IN_SYNC          el hash sellado coincide con el PRD actual
    DERIVA           el PRD cambió desde que se generó/sincronizó el spec
    SIN_SELLO        el spec no declara `derived_from_prd_hash` (legacy: no bloquea)
    NO_APLICA        el spec no deriva de un PRD (`derived_from_prd: N/A`)
    PRD_NO_RESUELVE  el path declarado no es legible (conservador: no bloquea)

Semántica de deriva (kb-traceability-rules): un mismatch significa que el PRD
cambió, no que ESTE spec esté necesariamente afectado — por eso `--mark`
escribe `needs_review` (no `stale`); `wf-prd-sync-impact`/`wf-spec-sync-from-prd`
deciden el impacto real por feature.
"""
import hashlib
import re
import sys
from pathlib import Path

HASH_LEN = 16  # prefijo hex del sha256 sellado (suficiente contra colisión accidental)

# `derived_from_prd:` exige el `:` tras "prd" — no matchea _version ni _hash
PRD_PATH_RE = re.compile(r"derived_from_prd\s*:\s*`?(?P<path>[^`\s|]+)`?")
PRD_HASH_RE = re.compile(
    r"(?P<prefix>derived_from_prd_hash\s*:\s*)(?P<value>sha256:[0-9a-fA-F]{8,64}|N/A|pending)"
)
PRD_VERSION_LINE_RE = re.compile(r"^.*derived_from_prd_version\s*:.*$", re.MULTILINE)
PRD_PATH_LINE_RE = re.compile(r"^.*derived_from_prd\s*:.*$", re.MULTILINE)
STATUS_SYNC_RE = re.compile(r"(?P<prefix>status_sync\s*:\s*[\"']?)(?P<value>\w+)")


def fail_usage(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    print(__doc__.split("Uso:")[1].split("Exit codes:")[0], file=sys.stderr)
    return 1


def prd_hash(prd_path: Path) -> str:
    """sha256 del contenido del PRD, con line endings normalizados (CRLF→LF)."""
    text = prd_path.read_text(encoding="utf-8")
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def resolve_prd(spec_path: Path, spec_text: str, override=None):
    """Devuelve (path_legible | None, valor_declarado | None).

    El path declarado se resuelve relativo al directorio del spec; si no
    resuelve ahí, se intenta relativo al cwd (specs legacy con paths de raíz
    de proyecto).
    """
    if override is not None:
        p = Path(override)
        return (p if p.is_file() else None), str(override)
    m = PRD_PATH_RE.search(spec_text)
    if m is None:
        return None, None
    declared = m.group("path")
    if declared.upper() in ("N/A", "UNKNOWN"):
        return None, declared
    p = Path(declared)
    candidates = [p] if p.is_absolute() else [spec_path.parent / p, p]
    for c in candidates:
        if c.is_file():
            return c, declared
    return None, declared


def cmd_seal(spec_path: Path, prd_override=None) -> int:
    try:
        spec_text = spec_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"ERROR: no se puede leer el spec: {e}", file=sys.stderr)
        return 1

    prd_path, declared = resolve_prd(spec_path, spec_text, prd_override)
    if declared is None:
        print(f"NO_APLICA: {spec_path} no declara `derived_from_prd` — nada que sellar.")
        return 0
    if declared.upper() in ("N/A", "UNKNOWN") and prd_path is None:
        print(f"NO_APLICA: {spec_path} declara `derived_from_prd: {declared}` — nada que sellar.")
        return 0
    if prd_path is None:
        print(f"ERROR: el PRD origen declarado ('{declared}') no resuelve a un archivo legible "
              f"(relativo a {spec_path.parent} ni al cwd). No se puede sellar.", file=sys.stderr)
        return 1

    digest = prd_hash(prd_path)
    new_value = f"sha256:{digest[:HASH_LEN]}"

    m = PRD_HASH_RE.search(spec_text)
    if m is not None:
        if m.group("value") == new_value:
            print(f"IN_SYNC: el sello ya era {new_value}; sin cambios. ({spec_path})")
            return 0
        new_text = spec_text[:m.start()] + m.group("prefix") + new_value + spec_text[m.end():]
        action = f"actualizado ({m.group('value')} → {new_value})"
    else:
        # Insertar tras la línea derived_from_prd_version (o derived_from_prd como fallback)
        anchor = PRD_VERSION_LINE_RE.search(spec_text) or PRD_PATH_LINE_RE.search(spec_text)
        if anchor is None:
            print("ERROR: el spec no tiene header de trazabilidad PRD reconocible "
                  "(`derived_from_prd:`) — no parece un spec SDD derivado.", file=sys.stderr)
            return 1
        line = anchor.group(0)
        # Replica el prefijo de línea del header (`> ` en los templates canónicos)
        prefix = re.match(r"^\s*(?:>\s*)?", line).group(0)
        insert = f"\n{prefix}derived_from_prd_hash: {new_value}"
        new_text = spec_text[:anchor.end()] + insert + spec_text[anchor.end():]
        action = f"sellado ({new_value})"

    spec_path.write_text(new_text, encoding="utf-8")
    print(f"OK: derived_from_prd_hash {action} en {spec_path} (PRD: {prd_path})")
    return 0


def check_one(spec_path: Path, mark: bool):
    """Devuelve (estado, detalle). Estados: IN_SYNC | DERIVA | SIN_SELLO | NO_APLICA | PRD_NO_RESUELVE | ILEGIBLE."""
    try:
        spec_text = spec_path.read_text(encoding="utf-8")
    except OSError as e:
        return "ILEGIBLE", str(e)

    prd_path, declared = resolve_prd(spec_path, spec_text)
    if declared is None or declared.upper() in ("N/A", "UNKNOWN"):
        return "NO_APLICA", f"`derived_from_prd: {declared}` — el spec no deriva de un PRD"

    m = PRD_HASH_RE.search(spec_text)
    if m is None:
        return "SIN_SELLO", "el spec no declara `derived_from_prd_hash` (sellar con `seal`)"
    sealed = m.group("value")
    if sealed in ("N/A", "pending"):
        return "SIN_SELLO", f"`derived_from_prd_hash: {sealed}` (sellar con `seal`)"
    if prd_path is None:
        return "PRD_NO_RESUELVE", f"'{declared}' no es legible desde {spec_path.parent} ni el cwd"

    digest = prd_hash(prd_path)
    sealed_hex = sealed.split(":", 1)[1].lower()
    if digest.startswith(sealed_hex):
        return "IN_SYNC", f"PRD: {prd_path}"

    detail = f"el PRD '{prd_path}' cambió desde el sellado ({sealed} ≠ sha256:{digest[:HASH_LEN]})"
    if mark:
        sm = STATUS_SYNC_RE.search(spec_text)
        if sm and sm.group("value") in ("in_sync", "unknown"):
            new_text = spec_text[:sm.start()] + sm.group("prefix") + "needs_review" + spec_text[sm.end():]
            spec_path.write_text(new_text, encoding="utf-8")
            detail += f" — status_sync: {sm.group('value')} → needs_review"
    return "DERIVA", detail


def cmd_check(spec_path: Path, mark: bool) -> int:
    estado, detalle = check_one(spec_path, mark)
    print(f"{estado}: {spec_path} — {detalle}")
    if estado == "ILEGIBLE":
        return 1
    return 2 if estado == "DERIVA" else 0


def cmd_check_all(root: Path, mark: bool) -> int:
    if not root.is_dir():
        print(f"ERROR: '{root}' no es un directorio.", file=sys.stderr)
        return 1
    specs = sorted(p for p in root.rglob("*_spec.md") if ".git" not in p.parts)
    if not specs:
        print(f"No se encontró ningún *_spec.md bajo {root}.")
        return 0
    print(f"=== sdd-sync-check check-all — {root} ({len(specs)} specs) ===")
    any_drift = any_error = False
    for spec in specs:
        estado, detalle = check_one(spec, mark)
        marker = {"IN_SYNC": "✓", "DERIVA": "✗"}.get(estado, "·")
        print(f"  {marker} [{estado}] {spec} — {detalle}")
        any_drift |= estado == "DERIVA"
        any_error |= estado == "ILEGIBLE"
    if any_drift:
        print("RESULTADO: hay specs con DERIVA — analiza el impacto con /wf-prd-sync-impact "
              "y resincroniza con /wf-spec-sync-from-prd.")
        return 2
    if any_error:
        return 1
    print("RESULTADO: sin deriva detectada.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] not in ("seal", "check", "check-all"):
        return fail_usage("comando requerido: seal | check | check-all")
    cmd, rest = args[0], args[1:]

    if cmd == "seal":
        prd_override = None
        if "--prd" in rest:
            i = rest.index("--prd")
            if i + 1 >= len(rest):
                return fail_usage("--prd requiere un path")
            prd_override = rest[i + 1]
            rest = rest[:i] + rest[i + 2:]
        if len(rest) != 1:
            return fail_usage("uso: seal <spec.md> [--prd <prd.md>]")
        return cmd_seal(Path(rest[0]), prd_override)

    mark = "--mark" in rest
    rest = [a for a in rest if a != "--mark"]
    if len(rest) != 1:
        return fail_usage(f"uso: {cmd} <path> [--mark]")
    if cmd == "check":
        return cmd_check(Path(rest[0]), mark)
    return cmd_check_all(Path(rest[0]), mark)


if __name__ == "__main__":
    sys.exit(main())
