#!/usr/bin/env python3
"""Verificador determinista de KBs declaradas por los agentes (ROADMAP 1.5).

El "KB Load Status" que cada agente incluye al final de su respuesta es
**auto-reportado**: el propio agente dice si sus KBs están `loaded` o `missing`.
Es la misma debilidad que el sellador resolvió para los planes — una señal que
el emisor controla. Este script añade la parte VERIFICABLE: comprueba que cada
KB declarada en el frontmatter `skills:` de un agente instalado existe de verdad
en `.claude/skills/`. El auto-reporte queda como señal secundaria en contexto.

El set de KBs de un agente es fijo (su frontmatter), no cambia entre
delegaciones — por eso el punto de verificación eficiente es la instalación y el
arranque, no "antes de cada delegación". `install.sh` lo ejecuta tras instalar;
también es invocable a demanda y en CI.

Uso:
    sdd-kb-check.py [--claude-dir <path>] [--all]           # todos los agentes
    sdd-kb-check.py [--claude-dir <path>] --agent <nombre>  # un agente
    sdd-kb-check.py ... --quiet                             # solo resumen

Y una segunda verificación, del mismo espíritu (D-069): que el bloque
`## Verificación de contexto` del cuerpo del agente **enumere todas** las KBs de
su `skills:`. Es lo que cierra el circuito: el `KB Load Status` solo puede
reportar `missing` de lo que está enumerado, así que una KB declarada y no
enumerada es invisible para el auto-reporte Y para todo lo demás. Esa lista
duplica el frontmatter, y una enumeración duplicada deriva sola.

`--claude-dir` por defecto: el `.claude/` del directorio actual o un ancestro.

Exit codes: 0 = todas las KBs declaradas existen instaladas y están enumeradas;
            1 = error de uso / no se encuentra `.claude/`;
            2 = al menos un agente declara una KB que no está instalada, o no la
                enumera en su `## Verificación de contexto`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SKILLS_INLINE_RE = re.compile(r"^skills:\s*\[(?P<body>.*?)\]\s*$", re.MULTILINE)


def resolve_claude_dir(explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit).resolve()
        return p if p.is_dir() else None
    cur = Path.cwd().resolve()
    for d in (cur, *cur.parents):
        cand = d / ".claude"
        if cand.is_dir():
            return cand
    return None


def parse_agent_skills(agent_md: Path) -> list[str]:
    """Extrae la lista `skills:` del frontmatter (forma inline o multilínea)."""
    try:
        text = agent_md.read_text(encoding="utf-8")
    except OSError:
        return []
    # Acota al frontmatter (excluye el `---` de cierre para no parsearlo como bullet)
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[:end]
    m = SKILLS_INLINE_RE.search(text)
    if m:
        body = m.group("body")
    else:
        # Forma multilínea: `skills:\n  - kb-a\n  - kb-b`
        mm = re.search(r"^skills:\s*$(?P<items>(?:\n\s*-\s*.+)+)", text, re.MULTILINE)
        if not mm:
            return []
        body = ",".join(re.findall(r"-\s*(.+)", mm.group("items")))
    skills = []
    for raw in body.split(","):
        name = raw.strip().strip("'\"")
        # Solo nombres de skill plausibles (descarta restos de parseo como `--`)
        if name and re.match(r"^[A-Za-z][A-Za-z0-9_-]*$", name):
            skills.append(name)
    return skills


def unlisted_in_context_check(agent_md: Path, declared: list[str]) -> list[str]:
    """KBs declaradas que el cuerpo NO enumera en `## Verificación de contexto`.

    El `KB Load Status` que el agente reporta al final de cada respuesta solo
    cubre lo que esa seccion enumera: una KB fuera de una lista PARCIAL nunca
    sale `missing`, ni ahi ni en ningun otro sitio. Como esa lista duplica el
    frontmatter, deriva sola — misma clase de fallo que dejo la Regla 10 de
    kb-traceability-rules enumerando tres gates cuando ya eran cuatro.

    Remitir en generico ("cada KB de tu frontmatter") NO es un hallazgo: es la
    forma preferida, porque no duplica y por tanto no puede quedarse corta.
    """
    text = agent_md.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"##\s+Verificaci[oó]n de contexto(.*?)(?=\n##\s|\Z)", text, re.S)
    if m is None:
        return list(declared)
    listed = set(re.findall(r"`(kb-[a-z0-9-]+)`", m.group(1)))
    # Enumera TODAS o NINGUNA. La forma generica —"cada KB de tu frontmatter"—
    # es correcta y ademas es la unica que no puede derivar: no duplica nada.
    # Lo que falla es la lista PARCIAL, que se lee como exhaustiva y no lo es.
    if not listed:
        return []
    return [kb for kb in declared if kb not in listed]


def check_agent(agent_md: Path, skills_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """Devuelve (declaradas, no_instaladas, no_enumeradas) para un agente."""
    declared = parse_agent_skills(agent_md)
    missing = [
        kb for kb in declared
        if not (skills_dir / kb / "SKILL.md").is_file()
    ]
    return declared, missing, unlisted_in_context_check(agent_md, declared)


def main(argv: list[str]) -> int:
    quiet = "--quiet" in argv
    args = [a for a in argv if not a.startswith("--")]
    claude_dir = None
    if "--claude-dir" in argv:
        i = argv.index("--claude-dir")
        if i + 1 < len(argv):
            claude_dir = argv[i + 1]
            if claude_dir in args:
                args.remove(claude_dir)
    one_agent = None
    if "--agent" in argv:
        i = argv.index("--agent")
        if i + 1 < len(argv):
            one_agent = argv[i + 1]
            if one_agent in args:
                args.remove(one_agent)

    cdir = resolve_claude_dir(claude_dir)
    if cdir is None:
        sys.stderr.write("[kb-check] no se encontró `.claude/` "
                         "(usa --claude-dir <path>)\n")
        return 1
    agents_dir = cdir / "agents"
    skills_dir = cdir / "skills"
    if not agents_dir.is_dir():
        if not quiet:
            print(f"[kb-check] sin agentes en {agents_dir} — nada que verificar")
        return 0

    if one_agent:
        name = one_agent if one_agent.endswith(".md") else f"{one_agent}.md"
        agent_files = [agents_dir / name]
        if not agent_files[0].is_file():
            sys.stderr.write(f"[kb-check] agente no encontrado: {agent_files[0]}\n")
            return 1
    else:
        agent_files = sorted(agents_dir.glob("*.md"))

    total_missing = 0
    agents_with_gaps = 0
    total_unlisted = 0
    agents_unlisted = 0
    for agent_md in agent_files:
        declared, missing, unlisted = check_agent(agent_md, skills_dir)
        if missing:
            agents_with_gaps += 1
            total_missing += len(missing)
            sys.stderr.write(
                f"  ⚠ {agent_md.stem}: {len(missing)}/{len(declared)} KB(s) no "
                f"instaladas → {', '.join(missing)}\n"
            )
        if unlisted:
            agents_unlisted += 1
            total_unlisted += len(unlisted)
            sys.stderr.write(
                f"  ⚠ {agent_md.stem}: {len(unlisted)}/{len(declared)} KB(s) "
                f"declaradas y NO enumeradas en `## Verificación de contexto` → "
                f"{', '.join(unlisted)}\n"
            )

    if total_missing:
        sys.stderr.write(
            f"[kb-check] {total_missing} KB(s) declaradas pero no instaladas en "
            f"{agents_with_gaps} agente(s). Reinstala el ecosistema (`install.sh`) "
            f"con la fase/overlay que las aporta.\n"
        )
    if total_unlisted:
        sys.stderr.write(
            f"[kb-check] {total_unlisted} KB(s) sin enumerar en {agents_unlisted} "
            f"agente(s): su `KB Load Status` no las cubre, así que si el harness no "
            f"las inyecta nadie se entera. Añádelas a `## Verificación de contexto`.\n"
        )
    if total_missing or total_unlisted:
        return 2

    if not quiet:
        print(f"[kb-check] OK: {len(agent_files)} agente(s), todas las KBs "
              f"declaradas están instaladas y enumeradas")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
