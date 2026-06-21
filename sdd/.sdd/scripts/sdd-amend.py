#!/usr/bin/env python3
# sdd-version: 0.37.0+3cdfd2d
"""Marcador determinista de enmiendas de CA sobre planes SDD (Fase 4.2 del ROADMAP).

Mismo principio que sdd-seal.py y sdd-task-state.py: separa el AUTOR del que
MARCA. `wf-spec-amend` aplica la aclaracion de un CA en el spec, pero la
anotacion `Enmienda pendiente` del plan afectado (el "stale puntual" que
retiene selectivamente las tasks que referencian ese CA) solo la escribe y
limpia este script. Consumidores de la anotacion: sdd-gate-check.py (deniega
`wf-task-run --task` sobre tasks retenidas y `wf-prepare-tasks` sobre planes
con enmiendas abiertas) y sdd-task-state.py (`next` salta tasks retenidas).

Uso:
    sdd-amend.py mark <plan.md> --ca CA-XXX [--ref E-00X]    # anota enmienda pendiente (asigna E-NNN si no se pasa --ref)
    sdd-amend.py clear <plan.md> (--ca CA-XXX | --ref E-00X | --all)
    sdd-amend.py list <plan.md>                              # lista anotaciones pendientes (no escribe)
    sdd-amend.py next-ref <archivo.md> [<archivo2.md> ...]   # siguiente E-NNN libre escaneando los archivos dados

Formato canonico de la anotacion (una linea por enmienda, tras `Estado:` del header):
    > **Enmienda pendiente:** CA-003 (E-002, 2026-06-07)

Asignacion de ref en `mark`: si no se pasa --ref, escanea el propio plan y el
`Spec origen` de su header (donde el changelog registra las enmiendas ya
aplicadas) y asigna el siguiente E-NNN — numeracion secuencial determinista,
nunca por prosa de agente.

Limpieza: `clear` la ejecutan los flujos tras la revision scoped del plan
(wf-spec-amend) y sdd-seal.py la absorbe al re-sellar con --seal (un plan
re-validado contra el spec vigente ya incorpora la enmienda).

Exit codes: 0 = OK; 1 = error de uso o IO; 2 = plan sin linea `Estado:`
            reconocible (no parece un plan SDD) o nada que limpiar con --ca/--ref.
"""
import re
import sys
from datetime import date
from pathlib import Path

# Mismas tolerancias de formato que sdd-seal.py / sdd-gate-check.py.
ESTADO_RE = re.compile(
    r"^\s*(?:[-*>]\s*)?\**Estado:?\**\s*:?\s*(?:BORRADOR|VALIDADO)\s*\**\s*$",
    re.MULTILINE,
)
AMEND_RE = re.compile(
    r"^[ \t]*(?:[-*>][ \t]*)?\**Enmienda pendiente:?\**[ \t]*:?[ \t]*"
    r"(?P<ca>CA-\d{3,4})[ \t]*\([ \t]*(?P<ref>E-\d{3,4})(?:[ \t]*,[ \t]*(?P<fecha>[\d-]+))?[ \t]*\)[ \t]*$",
    re.MULTILINE,
)
SPEC_ORIGEN_RE = re.compile(r"Spec origen(?:\*\*)?\s*:?\**\s*`?(?P<path>[^`\s|]+)`?", re.IGNORECASE)
REF_RE = re.compile(r"\bE-(\d{3,4})\b")


def fail_usage(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    print(__doc__.split("Uso:")[1].split("Formato canonico")[0], file=sys.stderr)
    return 1


def read(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"ERROR: no se puede leer {path}: {e}", file=sys.stderr)
        return None


def find_amendments(text):
    """Lista de dicts {ca, ref, fecha, start, end} en orden de documento."""
    return [
        {"ca": m.group("ca"), "ref": m.group("ref"), "fecha": m.group("fecha") or "",
         "start": m.start(), "end": m.end()}
        for m in AMEND_RE.finditer(text)
    ]


def next_ref_from(texts):
    """Siguiente E-NNN libre escaneando todos los textos dados."""
    used = [int(n) for t in texts for n in REF_RE.findall(t)]
    return f"E-{(max(used) + 1 if used else 1):03d}"


def cmd_mark(plan_path: Path, ca: str, ref: str | None) -> int:
    text = read(plan_path)
    if text is None:
        return 1
    estado_m = ESTADO_RE.search(text)
    if estado_m is None:
        print(f"ERROR: '{plan_path}' no tiene linea `Estado:` reconocible — no parece un plan SDD.",
              file=sys.stderr)
        return 2
    existing = find_amendments(text)
    for a in existing:
        if a["ca"] == ca:
            print(f"YA_MARCADA: {ca} ya tiene enmienda pendiente ({a['ref']}, {a['fecha'] or 'sin fecha'}) — sin cambios")
            print(f"REF: {a['ref']}")
            return 0
    if ref is None:
        # Escanear plan + spec origen (changelog de enmiendas aplicadas) para el siguiente E-NNN
        texts = [text]
        spec_m = SPEC_ORIGEN_RE.search(text)
        if spec_m:
            p = Path(spec_m.group("path"))
            spec_path = p if p.is_absolute() else (plan_path.parent / p).resolve()
            try:
                texts.append(spec_path.read_text(encoding="utf-8"))
            except OSError:
                pass  # spec no resoluble → numerar solo con lo visible en el plan
        ref = next_ref_from(texts)
    elif not re.fullmatch(r"E-\d{3,4}", ref):
        return fail_usage(f"--ref invalido: {ref} (formato: E-00X)")

    # Insertar la anotacion inmediatamente despues de la linea Estado del header
    line = f"> **Enmienda pendiente:** {ca} ({ref}, {date.today().isoformat()})"
    insert_at = text.index("\n", estado_m.end() - 1) + 1 if "\n" in text[estado_m.end() - 1:] else len(text)
    new_text = text[:insert_at] + line + "\n" + text[insert_at:]
    plan_path.write_text(new_text, encoding="utf-8")
    print(f"MARK OK: {ca} → {ref} anotada en {plan_path}")
    print(f"REF: {ref}")
    return 0


def cmd_clear(plan_path: Path, ca: str | None, ref: str | None, clear_all: bool) -> int:
    text = read(plan_path)
    if text is None:
        return 1
    amendments = find_amendments(text)
    targets = [a for a in amendments
               if clear_all or (ca and a["ca"] == ca) or (ref and a["ref"] == ref)]
    if not targets:
        if clear_all:
            print("Sin enmiendas pendientes — nada que limpiar.")
            return 0
        print(f"NADA_QUE_LIMPIAR: ninguna enmienda pendiente coincide con "
              f"{ca or ref} en {plan_path}", file=sys.stderr)
        return 2
    # Eliminar lineas completas, de atras a adelante para no invalidar offsets
    for a in sorted(targets, key=lambda x: x["start"], reverse=True):
        line_start = text.rfind("\n", 0, a["start"]) + 1
        line_end = text.index("\n", a["end"]) + 1 if "\n" in text[a["end"]:] else len(text)
        text = text[:line_start] + text[line_end:]
    plan_path.write_text(text, encoding="utf-8")
    for a in targets:
        print(f"CLEAR OK: {a['ca']} ({a['ref']}) limpiada de {plan_path}")
    return 0


def cmd_list(plan_path: Path) -> int:
    text = read(plan_path)
    if text is None:
        return 1
    amendments = find_amendments(text)
    print(f"=== sdd-amend list — {plan_path} ===")
    for a in amendments:
        print(f"  {a['ca']} ({a['ref']}, {a['fecha'] or 'sin fecha'})")
    print(f"RESULTADO: {len(amendments)} enmienda(s) pendiente(s)")
    return 0


def cmd_next_ref(paths) -> int:
    texts = []
    for p in paths:
        t = read(Path(p))
        if t is None:
            return 1
        texts.append(t)
    print(next_ref_from(texts))
    return 0


def main(argv) -> int:
    if len(argv) < 3:
        return fail_usage("faltan argumentos")
    cmd = argv[1]
    if cmd == "next-ref":
        return cmd_next_ref(argv[2:])
    plan_path = Path(argv[2])
    rest = argv[3:]

    def opt(name):
        if name in rest:
            i = rest.index(name)
            if i + 1 >= len(rest):
                fail_usage(f"{name} exige un valor")
                sys.exit(1)
            return rest[i + 1]
        return None

    if cmd == "mark":
        ca = opt("--ca")
        if not ca or not re.fullmatch(r"CA-\d{3,4}", ca):
            return fail_usage(f"mark exige --ca CA-XXX (recibido: {ca})")
        return cmd_mark(plan_path, ca, opt("--ref"))
    if cmd == "clear":
        ca, ref, clear_all = opt("--ca"), opt("--ref"), "--all" in rest
        if not (ca or ref or clear_all):
            return fail_usage("clear exige --ca CA-XXX, --ref E-00X o --all")
        return cmd_clear(plan_path, ca, ref, clear_all)
    if cmd == "list":
        return cmd_list(plan_path)
    return fail_usage(f"comando desconocido: {cmd}")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
