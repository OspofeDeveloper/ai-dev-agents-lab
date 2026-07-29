#!/usr/bin/env python3
"""Grafo determinista de dependencias entre asunciones de un PRD (Q2a, DECISIONS D-029).

`kb-prd-expert` permite que una entrada `[ASN-XXX]` de `## Asunciones del PRD`
declare de qué otras asunciones depende con un sufijo `Depende de: ASN-YYY` (IDs
**pelados**, sin corchetes, para no inflar el conteo 1:1 de `sdd-prd-ready.py`).
Este script hace VERIFICABLE esa relación —hasta ahora la LLM la notaba a ojo en
cada review (cascada no determinista observada en CU-2.e)— de dos formas:

  - grafo: parsea las aristas y valida que apunten a asunciones existentes y que
    no haya ciclos (autodependencias incluidas).
  - --check --rejected: dado el conjunto de asunciones RECHAZADAS en el review,
    reporta HUÉRFANAS — un dependiente de una rechazada que no esté también
    rechazado (quedaría en el PRD apoyado en algo que se eliminó). Es el backstop
    pre-sello que `wf-prd-review` corre ANTES de `sdd-prd-apply.py`.

ORDEN DEL BACKSTOP ([[D-037]]). El check se apoya en las entradas `[ASN-XXX]` y sus
aristas, así que **solo tiene sentido antes de aplicar**: `sdd-prd-apply.py` retira
las entradas decididas y, si la sección queda vacía, la elimina entera — entonces no
hay aristas que comprobar y el check saldría "OK" sin haber verificado nada. Ese
falso OK (observado en conformance CU-2.j) es peor que no correrlo, porque se lee
como garantía. Por eso, si se pide `--check --rejected <no vacío>` sobre un documento
sin entradas, el script sale VACUOUS (exit 2) en vez de OK.

TERCER DESENLACE: --keep ([[D-037]]). Un dependiente de una rechazada no siempre debe
caer: la dependencia puede quedar satisfecha de otra forma (p. ej. se rechaza "el
Usuario gestiona el catálogo de categorías" pero "presupuesto por categoría" sigue en
pie sobre categorías fijas). `--keep ASN-XXX` declara que ese dependiente se
**conserva conscientemente** tras haberlo presentado al usuario, y deja de contar
como huérfano. Es una declaración deliberada y separada de `--confirm`: no se puede
silenciar el check confirmándolo todo, hay que **nombrar** el dependiente — lo que
exige haber visto la cascada.

La *identificación* de la arista es juicio de la creación (se recuerda una vez);
su *cumplimiento* aquí es determinista. `sdd-prd-ready.py` (invariante 1:1) no se
toca: la arista pelada `ASN-006` no casa con su `ASN_ENTRY_RE` (`\\[ASN-\\d+\\]`).

Uso:
    sdd-prd-deps.py <prd.md> [--json]
    sdd-prd-deps.py <prd.md> --check --rejected ASN-006,ASN-007 [--keep ASN-008] [--json]

Exit codes:
    0 = OK (grafo válido; y en --check, sin huérfanas)
    1 = error de uso o IO
    2 = grafo malformado (arista a ASN inexistente / ciclo) o, en --check, huérfanas
        o check vacuo (VACUOUS: no quedan entradas que comprobar)
"""
import json
import re
import sys
from pathlib import Path

ASN_ENTRY_RE = re.compile(r"\[ASN-\d+\]")
ASSUMPTIONS_HEADING_RE = re.compile(r"^\s*#{1,6}\s+Asunciones del PRD\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^\s*#{1,6}\s+")
# `Depende de:` tolera negrita markdown (`**Depende de:**`) y mayúsculas.
DEPENDS_RE = re.compile(r"Depende de:\s*\**\s*(.+)$", re.IGNORECASE)
BARE_ASN_RE = re.compile(r"ASN-\d+")


def parse_graph(text: str):
    """Parsea `## Asunciones del PRD` → (nodos en orden, grafo {asn: [deps]}). Puro."""
    in_section = False
    nodes: list[str] = []
    graph: dict[str, list[str]] = {}
    for line in text.splitlines():
        if ASSUMPTIONS_HEADING_RE.match(line):
            in_section = True
            continue
        if in_section and HEADING_RE.match(line):
            in_section = False  # empieza otra sección
        if not in_section:
            continue
        m = ASN_ENTRY_RE.search(line)
        if not m:
            continue
        node = m.group(0).strip("[]")  # `[ASN-007]` -> `ASN-007`
        if node not in graph:
            nodes.append(node)
            graph[node] = []
        dm = DEPENDS_RE.search(line)
        if dm:
            # `Depende de:` va al final de la entrada; corta en el siguiente `·`
            # por robustez si hubiera más campos, y extrae los IDs pelados.
            chunk = dm.group(1).split("·")[0]
            for dep in BARE_ASN_RE.findall(chunk):
                if dep not in graph[node]:
                    graph[node].append(dep)
    return nodes, graph


def _find_cycles(graph: dict[str, list[str]]):
    """DFS: devuelve ciclos (listas de nodos), autodependencias incluidas."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    stack: list[str] = []
    cycles: list[list[str]] = []

    def dfs(u: str):
        color[u] = GRAY
        stack.append(u)
        for v in graph.get(u, []):
            if v not in color:  # arista colgante (a ASN inexistente): se ignora aquí
                continue
            if color[v] == GRAY:
                cycles.append(stack[stack.index(v):] + [v])
            elif color[v] == WHITE:
                dfs(v)
        stack.pop()
        color[u] = BLACK

    for n in graph:
        if color[n] == WHITE:
            dfs(n)
    return cycles


def analyze(text: str, rejected=None, keep=None) -> dict:
    nodes, graph = parse_graph(text)
    nodeset = set(nodes)
    dangling = sorted(
        f"{n}->{d}" for n in nodes for d in graph[n] if d not in nodeset
    )
    cycles = _find_cycles(graph)
    result = {
        "nodes": nodes,
        "graph": {n: graph[n] for n in nodes if graph[n]},
        "dangling_edges": dangling,
        "cycles": cycles,
    }
    if rejected is not None:
        R = set(rejected)
        K = set(keep or [])
        orphans = sorted(
            n for n in nodes
            if n not in R and n not in K and any(d in R for d in graph[n])
        )
        result["rejected"] = sorted(R)
        result["kept"] = sorted(K)
        result["orphans"] = orphans
        # Vacuidad ([[D-037]]): se pide comprobar rechazos sobre un documento que ya
        # no tiene entradas `[ASN-XXX]` — típicamente porque el backstop se corrió
        # DESPUÉS de `sdd-prd-apply.py`. No hay nada que comprobar: no es un OK.
        result["vacuous"] = bool(R) and not nodes
    return result


def main() -> int:
    args = sys.argv[1:]
    as_json = "--json" in args
    do_check = "--check" in args
    rest, rejected, keep = [], None, None
    it = iter([a for a in args if a not in ("--json", "--check")])
    for a in it:
        if a in ("--rejected", "--keep"):
            val = next(it, None)
            if val is None:
                print(f"ERROR: {a} requiere una lista ASN-001,ASN-002", file=sys.stderr)
                return 1
            ids = [x.strip() for x in val.split(",") if x.strip()]
            if a == "--rejected":
                rejected = ids
            else:
                keep = ids
        else:
            rest.append(a)

    if len(rest) != 1:
        print(
            "ERROR: uso: sdd-prd-deps.py <prd.md> [--json] "
            "[--check --rejected ASN-001,ASN-002 [--keep ASN-003]]",
            file=sys.stderr,
        )
        return 1
    if do_check and rejected is None:
        print("ERROR: --check requiere --rejected ASN-...", file=sys.stderr)
        return 1
    if keep is not None and not do_check:
        print("ERROR: --keep solo aplica con --check --rejected", file=sys.stderr)
        return 1

    path = Path(rest[0])
    try:
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except OSError as e:
        print(f"ERROR: no se puede leer el PRD: {e}", file=sys.stderr)
        return 1

    result = analyze(
        text,
        rejected=rejected if do_check else None,
        keep=keep if do_check else None,
    )
    result["path"] = str(path)
    malformed = bool(result["dangling_edges"]) or bool(result["cycles"])
    vacuous = bool(do_check and result.get("vacuous"))
    bad = malformed or vacuous or (do_check and bool(result["orphans"]))

    if as_json:
        print(json.dumps(result, ensure_ascii=False))
    elif do_check:
        if vacuous:
            print(
                f"VACUOUS: {path} — no quedan entradas `[ASN-XXX]` que comprobar, pero se "
                f"pasaron rechazos ({', '.join(result['rejected'])}). El backstop de "
                f"dependencias va ANTES de `sdd-prd-apply.py`: después, la sección de "
                f"asunciones ya no existe y este check no verificaría nada."
            )
        elif result["orphans"]:
            kept = f" · conservadas conscientemente: {', '.join(result['kept'])}" if result["kept"] else ""
            print(
                f"ORPHANS: {path} — dependiente(s) de una asunción rechazada sin "
                f"rechazar/decidir: {', '.join(result['orphans'])}{kept}"
                f" (si el usuario decidió conservar alguna, pásala con --keep)"
            )
        elif malformed:
            print(f"MALFORMED: {path} — grafo inválido (dangling/ciclos), revísalo.")
        else:
            kept = f" (conservadas conscientemente: {', '.join(result['kept'])})" if result["kept"] else ""
            print(
                f"OK: {path} — sin huérfanas: toda dependencia de una rechazada está "
                f"resuelta{kept}."
            )
    else:
        if malformed:
            det = []
            if result["dangling_edges"]:
                det.append("aristas a ASN inexistente: " + ", ".join(result["dangling_edges"]))
            if result["cycles"]:
                det.append("ciclos: " + "; ".join("->".join(c) for c in result["cycles"]))
            print(f"MALFORMED: {path} — " + " · ".join(det))
        else:
            n_edges = sum(len(v) for v in result["graph"].values())
            print(
                f"OK: {path} — grafo de dependencias válido "
                f"({len(result['graph'])} nodo(s) con dependencias, {n_edges} arista(s))."
            )

    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
