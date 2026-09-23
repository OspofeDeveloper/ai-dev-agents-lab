#!/usr/bin/env python3
"""Probe determinista del contrato de fan-out: ¿salieron las N llamadas juntas?

El contrato lleva desde [[D-047]] en negrita en los tres emisores del ecosistema
(`wf-spec-features-first` Pasos 5 y 7, `wf-prd-change-cascade`, `wf-design-variant`):
cuando se delega en varios agentes a la vez, **las N llamadas `Agent` salen en un
único mensaje**. Con `CLAUDE_CODE_FORK_SUBAGENT=0` cada mensaje es una barrera, así
que repartirlas serializa la tanda de verdad.

Se incumplió tres veces con el contrato delante ([[D-084]], [[D-092]]), siempre en la
forma **`1 + (N-1)`**: una llamada de prueba y el resto después. Y las tres las
encontró una persona leyendo el transcript a mano. Este script hace ese trabajo:

    sdd-fanout-check.py <session.jsonl | dir-de-sesiones> [--json] [--quiet]

Cómo decide (y por qué no puede ser más simple):

1. Recorre los mensajes del **asistente** y agrupa por `message.id` los `tool_use`
   de la tool `Agent`. Un mensaje con 3 llamadas es UNA emisión de tamaño 3. Esto
   es lo que el contrato mide: llamadas **por mensaje**, no agentes lanzados.
2. Clasifica cada emisión en un **cubo** `(subagent_type, skill del prompt)`. La
   skill sale del `.claude/skills/<nombre>/SKILL.md` que el prompt manda leer
   ([[D-044]]). Sin el segundo componente el probe daría falsos positivos con las
   delegaciones **secuenciales por contrato**: `wf-spec-analyze` y luego
   `wf-spec-discover` son dos encargos distintos al mismo `sdd-spec-explorer`, y no
   son un fan-out roto.
3. Corta los cubos por **turno humano**: un mensaje real del usuario abre segmento.
   Relanzar delegados después de que el usuario decida algo (un `STOP_*` presentado
   en un gate, una tanda cortada por el límite de sesión) es correcto y no se marca.
4. Un segmento de un cubo con **dos o más emisiones** es el hallazgo: el fan-out se
   repartió en varios mensajes. Se reportan los tamaños en orden (`1 + 2`), el hueco
   entre la primera y la segunda emisión —el coste real— y los `message.id`.

Exit codes: 0 = sin hallazgos; 1 = error de uso o IO; 2 = fan-out serializado.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SKILL_RE = re.compile(r"\.claude/skills/([a-z0-9][a-z0-9-]*)/SKILL\.md")
ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})")


def parse_ts(value):
    """Segundos desde epoch aproximados, solo para medir huecos. None si no parsea."""
    if not isinstance(value, str):
        return None
    m = ISO_RE.match(value)
    if not m:
        return None
    y, mo, d, h, mi, s = (int(x) for x in m.groups())
    # Aritmética de calendario simplificada: solo se usan DIFERENCIAS, y una tanda
    # no cruza meses. Evita depender de zoneinfo/dateutil.
    return ((((y * 12 + mo) * 31 + d) * 24 + h) * 60 + mi) * 60 + s


def is_human_turn(row):
    """Un mensaje escrito por la persona, no un `tool_result` ni un hand-back."""
    if row.get("type") != "user":
        return False
    content = row.get("message", {}).get("content")
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "tool_result":
                return False
            if part.get("type") == "text" and part.get("text", "").strip():
                return True
    return False


def emissions(rows):
    """[(msg_id, ts, [(subagent_type, skill), …])] en orden, solo mensajes con Agent."""
    out = []
    for row in rows:
        if row.get("type") != "assistant":
            continue
        message = row.get("message", {})
        content = message.get("content")
        if not isinstance(content, list):
            continue
        calls = []
        for part in content:
            if not isinstance(part, dict) or part.get("type") != "tool_use":
                continue
            if part.get("name") != "Agent":
                continue
            inp = part.get("input") or {}
            prompt = inp.get("prompt") or ""
            m = SKILL_RE.search(prompt)
            calls.append((inp.get("subagent_type") or "?", m.group(1) if m else "—"))
        if calls:
            out.append((message.get("id") or f"row-{len(out)}",
                        parse_ts(row.get("timestamp")), calls))
    return out


def analyze(rows):
    """Segmenta por turno humano y agrupa por cubo. Devuelve (hallazgos, limpias)."""
    segments = [[]]
    # El transcript parte UN mensaje del asistente en varias filas, una por bloque de
    # contenido: las 3 llamadas de un fan-out llegan como 3 filas con el MISMO
    # `message.id`. Fusionarlas por ese id es lo que hace que el probe cuente
    # llamadas-por-mensaje (lo que el contrato mide) y no filas.
    indice = {}
    for row in rows:
        if is_human_turn(row):
            segments.append([])
            indice = {}
            continue
        if row.get("type") != "assistant":
            continue
        for mid, ts, calls in emissions([row]):
            if mid in indice:
                segments[-1][indice[mid]][2].extend(calls)
            else:
                indice[mid] = len(segments[-1])
                segments[-1].append([mid, ts, list(calls)])

    hallazgos, limpias = [], []
    for segment in segments:
        cubos = {}
        for mid, ts, calls in segment:
            # Una emisión cuenta en el cubo de cada llamada que lleva: si un mensaje
            # mezcla dos encargos distintos (raro, pero legítimo), cada cubo ve las
            # suyas y ninguno queda con un recuento inflado.
            for bucket in set(calls):
                n = sum(1 for c in calls if c == bucket)
                cubos.setdefault(bucket, []).append({"msg": mid, "ts": ts, "n": n})
        for (agent, skill), items in cubos.items():
            total = sum(i["n"] for i in items)
            if len(items) == 1:
                if total > 1:
                    limpias.append({"agent": agent, "skill": skill, "n": total,
                                    "msg": items[0]["msg"]})
                continue
            gap = None
            if items[0]["ts"] is not None and items[1]["ts"] is not None:
                gap = items[1]["ts"] - items[0]["ts"]
            hallazgos.append({
                "agent": agent,
                "skill": skill,
                "total": total,
                "forma": " + ".join(str(i["n"]) for i in items),
                "hueco_s": gap,
                "mensajes": [i["msg"] for i in items],
            })
    return hallazgos, limpias


def load(path: Path):
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # el transcript puede traer líneas truncadas al final
    return rows


def resolve(arg: str) -> Path | None:
    path = Path(arg).expanduser()
    if path.is_dir():
        sessions = sorted(path.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        return sessions[-1] if sessions else None
    return path if path.is_file() else None


def main(argv: list[str]) -> int:
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        sys.stderr.write(
            "uso: sdd-fanout-check.py <session.jsonl | dir-de-sesiones> "
            "[--json] [--quiet]\n")
        return 1
    path = resolve(args[0])
    if path is None:
        sys.stderr.write(f"[fanout-check] no hay transcript legible en: {args[0]}\n")
        return 1

    hallazgos, limpias = analyze(load(path))
    veredicto = "FANOUT_SERIALIZADO" if hallazgos else "OK"

    if "--json" in flags:
        print(json.dumps({"verdict": veredicto, "transcript": str(path),
                          "findings": hallazgos, "clean_fanouts": limpias},
                         ensure_ascii=False, indent=2))
        return 2 if hallazgos else 0

    if not hallazgos:
        if "--quiet" not in flags:
            print(f"[fanout-check] OK: {len(limpias)} tanda(s) en un único mensaje "
                  f"({path.name})")
            for c in limpias:
                print(f"  ✓ {c['n']}× {c['agent']} ({c['skill']}) en {c['msg']}")
        return 0

    print(f"[fanout-check] FANOUT_SERIALIZADO: {len(hallazgos)} tanda(s) repartidas "
          f"en varios mensajes, {len(limpias)} en un único mensaje ({path.name})")
    for h in hallazgos:
        hueco = f", {h['hueco_s']}s entre la 1ª y la 2ª" if h["hueco_s"] is not None else ""
        print(f"  ✗ {h['total']}× {h['agent']} ({h['skill']}) emitidas como "
              f"{h['forma']}{hueco}")
        for mid in h["mensajes"]:
            print(f"      {mid}")
    print("  El contrato pide las N llamadas en UN mensaje ([[D-047]], [[D-084]]): con "
          "cada mensaje actuando de barrera, repartirlas serializa la tanda.")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
