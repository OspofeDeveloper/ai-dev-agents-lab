#!/usr/bin/env python3
"""Generador determinista de sdd/meta/skill-registry.md.

Escanea el filesystem del ecosistema SDD y regenera el registry completo:
nombre, descripcion (primera frase del frontmatter), invocabilidad y path
de cada skill, organizadas por scope (meta, fases, tech targets).

Es la SSoT de generacion del registry (Regla 18 de kb-sdd-skill-architecture):
ni wf-sdd-status ni ningun otro workflow redactan el registry a mano — todos
ejecutan este script. Un indice generado mecanicamente no puede mentir.

Uso (desde la raiz del repo o desde cualquier sitio):
    python3 sdd/scripts/generate-skill-registry.py
"""
import datetime
import re
import sys
from pathlib import Path

SDD_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = SDD_ROOT / "meta" / "skill-registry.md"
PHASES = ["prd", "spec", "design", "plan", "tasks"]
MAX_DESC = 160


def parse_frontmatter(skill_md: Path) -> dict:
    """Extrae name y description del frontmatter YAML (parser minimo)."""
    fm = {}
    try:
        lines = skill_md.read_text(encoding="utf-8").splitlines()
    except OSError:
        return fm
    if not lines or lines[0].strip() != "---":
        return fm
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^(name|description):\s*(.*)$", line)
        if m:
            value = m.group(2).strip().strip('"').strip("'")
            fm[m.group(1)] = value
    return fm


def short_desc(desc: str) -> str:
    """Primera frase, truncada a MAX_DESC. Sin pipes (rompen la tabla)."""
    desc = desc.replace("|", "/").strip()
    # Primera frase si la hay y no es absurdamente corta
    m = re.match(r"^(.{20,}?\.)\s", desc + " ")
    if m:
        desc = m.group(1).rstrip(".")
    if len(desc) > MAX_DESC:
        desc = desc[: MAX_DESC - 1].rstrip() + "…"
    return desc or "(sin description)"


def collect(skills_dir: Path) -> list:
    """Lista de entradas (name, desc, invocable, relpath) de un directorio de skills."""
    entries = []
    if not skills_dir.is_dir():
        return entries
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        fm = parse_frontmatter(skill_md)
        name = fm.get("name", skill_md.parent.name)
        desc = short_desc(fm.get("description", ""))
        invocable = "true" if name.startswith("wf-") else "false"
        relpath = skill_md.relative_to(SDD_ROOT).as_posix()
        entries.append((name, desc, invocable, relpath))
    # kb-* primero, luego wf-*, alfabetico dentro de cada grupo
    entries.sort(key=lambda e: (0 if e[0].startswith("kb-") else 1, e[0]))
    return entries


def render_table(entries: list) -> list:
    out = ["| Skill | Descripción | Invocable | Path |", "|---|---|---|---|"]
    for name, desc, invocable, relpath in entries:
        out.append(f"| {name} | {desc} | {invocable} | {relpath} |")
    return out


def main() -> int:
    sections = []  # (titulo, entries)

    # Meta-ecosistema: meta/skills + bootstrap/skills
    meta = collect(SDD_ROOT / "meta" / "skills") + collect(SDD_ROOT / "bootstrap" / "skills")
    meta.sort(key=lambda e: (0 if e[0].startswith("kb-") else 1, e[0]))
    sections.append(("Meta-Ecosistema (meta/)", meta))

    # Fases del pipeline
    for phase in PHASES:
        entries = collect(SDD_ROOT / phase / "skills")
        if entries:
            sections.append((f"Fase: {phase.upper() if phase == 'prd' else phase.capitalize()}", entries))

    # Tech targets: raiz de skills/ (global), plan/ y tasks/
    tech_dir = SDD_ROOT / "tech"
    if tech_dir.is_dir():
        for stack_dir in sorted(p for p in tech_dir.iterdir() if p.is_dir()):
            stack = stack_dir.name.upper()
            globals_ = collect(stack_dir / "skills")
            if globals_:
                sections.append((f"Tech: {stack} — Global", globals_))
            for sub, label in (("plan", "Plan"), ("tasks", "Tasks")):
                entries = collect(stack_dir / "skills" / sub)
                if entries:
                    sections.append((f"Tech: {stack} — {label}", entries))

    all_entries = [e for _, es in sections for e in es]
    total = len(all_entries)
    n_wf = sum(1 for e in all_entries if e[0].startswith("wf-"))
    n_kb = sum(1 for e in all_entries if e[0].startswith("kb-"))
    today = datetime.date.today().isoformat()

    lines = [
        "# SDD Skill Registry",
        "<!-- Auto-generado por scripts/generate-skill-registry.py. No editar manualmente. -->",
        f"<!-- Total: {total} skills | {n_wf} wf-* (user-invocable) | {n_kb} kb-* -->",
        f"<!-- Última actualización: {today} -->",
    ]
    for title, entries in sections:
        lines += ["", f"## {title}", ""] + render_table(entries)
    lines.append("")

    REGISTRY.write_text("\n".join(lines), encoding="utf-8")
    print(f"skill-registry.md regenerado: {total} skills ({n_wf} wf-*, {n_kb} kb-*) en {REGISTRY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
