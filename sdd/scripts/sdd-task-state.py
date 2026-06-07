#!/usr/bin/env python3
"""Gestor determinista de estados de tasks SDD (Fase 2.1 del ROADMAP).

Mismo principio que sdd-seal.py: separa el AUTOR del que marca el ESTADO.
`wf-task-run` delega la implementacion al owner de cada task, pero el estado
persistente (`Estado: PENDIENTE|EN_CURSO|HECHA|BLOQUEADA`) solo lo escribe
este script, validando transiciones y dependencias mecanicamente. Tambien
regenera la tabla `## Progreso` para que nunca derive del estado real.

Uso:
    sdd-task-state.py init <tasks.md>                  # añade Estado: PENDIENTE a tasks sin estado + tabla Progreso
    sdd-task-state.py check <tasks.md>                 # resumen de estados (no escribe)
    sdd-task-state.py next <tasks.md>                  # imprime el ID de la siguiente task elegible
    sdd-task-state.py set <tasks.md> T-00X <ESTADO> [--motivo "..."] [--force]

Estados y transiciones validas:
    PENDIENTE  -> EN_CURSO | BLOQUEADA
    EN_CURSO   -> HECHA | BLOQUEADA | PENDIENTE   (HECHA exige deps HECHAS salvo --force)
    BLOQUEADA  -> PENDIENTE | EN_CURSO            (desbloqueo; exige --motivo al bloquear)
    HECHA      -> PENDIENTE                       (reapertura, solo con --force)

Elegibilidad (`next`): la primera task en orden de documento con estado
PENDIENTE cuyas Dependencies estan todas HECHA (o son `ninguna`).

Exit codes: 0 = OK; 1 = error de uso o IO; 2 = transicion invalida / no elegible /
            tasks sin inicializar (en `next`).
"""
import re
import sys
from pathlib import Path

STATES = ("PENDIENTE", "EN_CURSO", "HECHA", "BLOQUEADA")
TRANSITIONS = {
    "PENDIENTE": {"EN_CURSO", "BLOQUEADA"},
    "EN_CURSO": {"HECHA", "BLOQUEADA", "PENDIENTE"},
    "BLOQUEADA": {"PENDIENTE", "EN_CURSO"},
    "HECHA": set(),  # reapertura solo con --force
}

TASK_HEADER_RE = re.compile(r"^##\s+(?P<id>T-\d{3,4})\s*:\s*(?P<title>.+?)\s*$", re.MULTILINE)
# Tolera variantes: `- **Estado:** X`, `**Estado**: X`, `Estado: X` (con motivo opcional tras ` — `)
ESTADO_LINE_RE = re.compile(
    r"^(?P<prefix>\s*(?:[-*]\s*)?\**Estado:?\**\s*:?\s*)(?P<value>PENDIENTE|EN_CURSO|HECHA|BLOQUEADA)(?P<motivo>\s+—\s+.*)?\s*$",
    re.MULTILINE,
)
DEPS_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?\**Dependencies:?\**\s*:?\s*(?P<deps>.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
PROGRESO_HEADER = "## Progreso"


def fail_usage(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    print(__doc__, file=sys.stderr)
    sys.exit(1)


def read_tasks(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"ERROR: no se puede leer {path}: {e}", file=sys.stderr)
        sys.exit(1)


def parse_tasks(text):
    """Devuelve lista de dicts: id, title, start, end, estado(None|str), motivo, deps(list)."""
    headers = list(TASK_HEADER_RE.finditer(text))
    tasks = []
    for i, m in enumerate(headers):
        start = m.start()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = text[start:end]
        em = ESTADO_LINE_RE.search(block)
        dm = DEPS_LINE_RE.search(block)
        deps = []
        if dm:
            raw = dm.group("deps")
            deps = re.findall(r"T-\d{3,4}", raw)
        tasks.append({
            "id": m.group("id"),
            "title": m.group("title"),
            "start": start,
            "end": end,
            "estado": em.group("value") if em else None,
            "motivo": (em.group("motivo") or "").strip(" —").strip() if em else "",
            "deps": deps,
        })
    return tasks


def progreso_table(tasks):
    total = len(tasks)
    by = {s: sum(1 for t in tasks if t["estado"] == s) for s in STATES}
    lines = [
        PROGRESO_HEADER,
        "",
        "<!-- Tabla generada por sdd-task-state.py — no editar a mano. -->",
        "",
        f"**{by['HECHA']}/{total} HECHA** · {by['EN_CURSO']} en curso · "
        f"{by['PENDIENTE']} pendientes · {by['BLOQUEADA']} bloqueadas",
        "",
        "| Task | Estado | Dependencias | Nota |",
        "|---|---|---|---|",
    ]
    for t in tasks:
        deps = ", ".join(t["deps"]) if t["deps"] else "—"
        nota = t["motivo"] if t["estado"] == "BLOQUEADA" and t["motivo"] else ""
        lines.append(f"| {t['id']}: {t['title']} | {t['estado'] or 'SIN_ESTADO'} | {deps} | {nota} |")
    return "\n".join(lines) + "\n"


def replace_progreso(text, tasks):
    """Inserta o reemplaza la seccion ## Progreso (antes de la primera task)."""
    table = progreso_table(tasks)
    existing = re.search(
        rf"^{re.escape(PROGRESO_HEADER)}\s*$.*?(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL
    )
    if existing:
        return text[: existing.start()] + table + "\n" + text[existing.end():]
    first = TASK_HEADER_RE.search(text)
    pos = first.start() if first else len(text)
    return text[:pos] + table + "\n" + text[pos:]


def set_estado_in_block(text, task, new_state, motivo=""):
    """Reescribe (o inserta) la linea Estado dentro del bloque de la task."""
    block = text[task["start"]:task["end"]]
    suffix = f" — {motivo}" if motivo else ""
    em = ESTADO_LINE_RE.search(block)
    if em:
        new_block = (
            block[: em.start()]
            + em.group("prefix") + new_state + suffix
            + block[em.end():]
        )
    else:
        # Insertar como primera linea de metadata tras el header de la task
        lines = block.splitlines(keepends=True)
        insert_at = 1
        while insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
        lines.insert(insert_at, f"- **Estado:** {new_state}{suffix}\n")
        new_block = "".join(lines)
    return text[: task["start"]] + new_block + text[task["end"]:]


def eligible(task, by_id):
    if task["estado"] != "PENDIENTE":
        return False
    return all(by_id.get(d, {}).get("estado") == "HECHA" for d in task["deps"])


def cmd_init(path):
    text = read_tasks(path)
    tasks = parse_tasks(text)
    if not tasks:
        print(f"ERROR: {path} no contiene tasks (`## T-XXX:`)", file=sys.stderr)
        sys.exit(1)
    added = 0
    # Procesar de atras a adelante para no invalidar offsets
    for t in reversed(tasks):
        if t["estado"] is None:
            text = set_estado_in_block(text, t, "PENDIENTE")
            added += 1
    tasks = parse_tasks(text)
    text = replace_progreso(text, tasks)
    path.write_text(text, encoding="utf-8")
    print(f"init OK: {len(tasks)} tasks, {added} inicializadas a PENDIENTE, tabla Progreso regenerada")
    sys.exit(0)


def cmd_check(path):
    text = read_tasks(path)
    tasks = parse_tasks(text)
    if not tasks:
        print(f"ERROR: {path} no contiene tasks (`## T-XXX:`)", file=sys.stderr)
        sys.exit(1)
    by_id = {t["id"]: t for t in tasks}
    print(f"=== sdd-task-state check — {path} ===")
    for t in tasks:
        marker = "→" if eligible(t, by_id) else " "
        motivo = f" — {t['motivo']}" if t["motivo"] else ""
        print(f"  {marker} {t['id']}: {t['estado'] or 'SIN_ESTADO'}{motivo}")
    total = len(tasks)
    done = sum(1 for t in tasks if t["estado"] == "HECHA")
    print(f"RESULTADO: {done}/{total} HECHA")
    sys.exit(0)


def cmd_next(path):
    text = read_tasks(path)
    tasks = parse_tasks(text)
    if not tasks:
        print(f"ERROR: {path} no contiene tasks (`## T-XXX:`)", file=sys.stderr)
        sys.exit(1)
    if any(t["estado"] is None for t in tasks):
        print("SIN_INICIALIZAR: ejecuta `init` primero", file=sys.stderr)
        sys.exit(2)
    by_id = {t["id"]: t for t in tasks}
    for t in tasks:
        if eligible(t, by_id):
            print(t["id"])
            sys.exit(0)
    if all(t["estado"] == "HECHA" for t in tasks):
        print("COMPLETO")
        sys.exit(0)
    print("NINGUNA_ELEGIBLE")
    sys.exit(2)


def cmd_set(path, task_id, new_state, motivo, force):
    if new_state not in STATES:
        fail_usage(f"estado invalido: {new_state} (validos: {', '.join(STATES)})")
    text = read_tasks(path)
    tasks = parse_tasks(text)
    by_id = {t["id"]: t for t in tasks}
    task = by_id.get(task_id)
    if not task:
        print(f"ERROR: {task_id} no existe en {path}", file=sys.stderr)
        sys.exit(1)
    current = task["estado"]
    if current is None:
        print("SIN_INICIALIZAR: ejecuta `init` primero", file=sys.stderr)
        sys.exit(2)
    if new_state == current:
        print(f"{task_id} ya esta en {new_state} — sin cambios")
        sys.exit(0)
    allowed = new_state in TRANSITIONS[current] or (force and current == "HECHA" and new_state == "PENDIENTE")
    if not allowed:
        print(f"TRANSICION INVALIDA: {task_id} {current} -> {new_state}"
              + (" (HECHA solo se reabre con --force)" if current == "HECHA" else ""), file=sys.stderr)
        sys.exit(2)
    if new_state == "BLOQUEADA" and not motivo:
        print("ERROR: BLOQUEADA exige --motivo", file=sys.stderr)
        sys.exit(2)
    if new_state == "HECHA" and not force:
        missing = [d for d in task["deps"] if by_id.get(d, {}).get("estado") != "HECHA"]
        if missing:
            print(f"DEPENDENCIAS NO HECHAS: {task_id} depende de {', '.join(missing)} "
                  "(usa --force solo si sabes lo que haces)", file=sys.stderr)
            sys.exit(2)
    text = set_estado_in_block(text, task, new_state, motivo if new_state == "BLOQUEADA" else "")
    tasks = parse_tasks(text)
    text = replace_progreso(text, tasks)
    path.write_text(text, encoding="utf-8")
    print(f"set OK: {task_id} {current} -> {new_state}" + (f" — {motivo}" if motivo else ""))
    sys.exit(0)


def main(argv):
    if len(argv) < 3:
        fail_usage("faltan argumentos")
    cmd, path = argv[1], Path(argv[2])
    if cmd == "init":
        cmd_init(path)
    elif cmd == "check":
        cmd_check(path)
    elif cmd == "next":
        cmd_next(path)
    elif cmd == "set":
        if len(argv) < 5:
            fail_usage("uso: set <tasks.md> T-00X <ESTADO> [--motivo \"...\"] [--force]")
        task_id, new_state = argv[3], argv[4]
        motivo = ""
        force = "--force" in argv[5:]
        if "--motivo" in argv[5:]:
            i = argv.index("--motivo")
            if i + 1 >= len(argv):
                fail_usage("--motivo exige un valor")
            motivo = argv[i + 1]
        cmd_set(path, task_id, new_state, motivo, force)
    else:
        fail_usage(f"comando desconocido: {cmd}")


if __name__ == "__main__":
    main(sys.argv)
