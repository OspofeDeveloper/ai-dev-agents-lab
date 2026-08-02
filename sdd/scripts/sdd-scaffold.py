#!/usr/bin/env python3
"""Scaffold determinista de piezas del ecosistema SDD (ROADMAP 11.4d).

Genera el esqueleto de una skill (kb-* / wf-*) o un agente con el frontmatter
CANONICO por construccion (segun kb-sdd-creation-guide), en el directorio que
corresponde a su tipo y fase. Sustituye el "sigue la plantilla por prosa" de
wf-skill-create/wf-agent-create por una plantilla EJECUTABLE: lo que produce
pasa el gate estructural (sdd-structural-lint.py) sin retoques de frontmatter.

Cierra el bucle del ciclo de creacion:
  scaffold (este script) -> frontmatter canon-limpio
  gate de cierre (11.4b) -> verifica
  audit (11.4a)          -> lo demas

El cuerpo queda como esqueleto con TODO: el agente sdd-author (o el humano)
lo rellena. El scaffold NO inventa contenido de dominio.

Uso:
    sdd-scaffold.py kb  <nombre> --phase <fase> [--description D] [--effort E]
    sdd-scaffold.py wf  <nombre> --phase <fase> [--description D] [--when-to-use W]
                        [--argument-hint H] [--effort E] [--agent A]
                        [--allowed-tools "Read, Write"]
    sdd-scaffold.py agent <nombre> --phase <fase> --skills a,b,c [--description D]
                        [--model M] [--read-only]

  <fase> ∈ {prd, spec, design, plan, tasks, global, tech/<stack>}
  --root <path>   raiz del ecosistema (default: el arbol donde vive este script)
  --dry-run       imprime path + contenido sin escribir
  --force         sobreescribe si ya existe (default: rechaza con exit 2)

Salidas: exit 0 escrito/dry-run ok; 2 error de uso o destino existente.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SDD_ROOT = Path(__file__).resolve().parent.parent

PHASES = {"prd", "spec", "design", "plan", "tasks", "global"}

# Color de agente por fase/dominio (kb-sdd-creation-guide, tabla de colores).
AGENT_COLOR = {
    "global": "purple",
    "prd": "blue",
    "spec": "green",
    "design": "pink",
    "plan": "orange",
    "tasks": "cyan",
}


def _valid_phase(phase: str) -> bool:
    return phase in PHASES or phase.startswith("tech/")


def _skills_base(root: Path, phase: str) -> Path:
    """Directorio skills/ de la fase."""
    if phase == "global":
        return root / "meta" / "skills"
    if phase.startswith("tech/"):
        return root / "tech" / phase.split("/", 1)[1] / "skills"
    return root / "pipeline" / phase / "skills"


def _agents_base(root: Path, phase: str) -> Path:
    if phase == "global":
        return root / "meta" / "agents"
    if phase.startswith("tech/"):
        return root / "tech" / phase.split("/", 1)[1] / "agents"
    return root / "pipeline" / phase / "agents"


def _canonical(name: str, prefix: str) -> str:
    """Quita un prefijo kb-/wf- accidental y aplica el correcto."""
    n = name.strip()
    for p in ("kb-", "wf-"):
        if n.startswith(p):
            n = n[len(p):]
    return prefix + n


def _agent_color(phase: str) -> str:
    if phase.startswith("tech/"):
        return "red"
    return AGENT_COLOR.get(phase, "purple")


# ── Generadores de contenido ────────────────────────────────────────────────

def gen_kb(name: str, description: str, effort: str) -> str:
    desc = description or f"TODO: el QUE de {name}, caso clave primero. Sin triggers."
    fm = [
        "---",
        f"name: {name}",
        f'description: "{desc}"',
        f"effort: {effort or 'low'}",
        "allowed-tools: [Read]",
        "user-invocable: false",
        "---",
    ]
    body = [
        "",
        f"# {name}",
        "",
        "> Conocimiento de fase: no se invoca directamente; se carga en el contexto",
        "> del agente que la declara en su frontmatter `skills:`.",
        "",
        "## TODO",
        "",
        "Desarrollar el contenido siguiendo `kb-sdd-creation-guide` (estructura,",
        "densidad, SSoT). Reemplazar este esqueleto.",
        "",
    ]
    return "\n".join(fm + body)


def gen_wf(name, description, when_to_use, argument_hint, effort, agent,
           allowed_tools, interactive=False):
    desc = description or f"TODO: el QUE de {name} (pipeline que orquesta, que produce)."
    wtu = when_to_use or "TODO: frases de activacion naturales + exclusiones (No activa para X, usa wf-Y)."
    hint = argument_hint or "<modo|accion> <input_principal> [flags...]"
    if allowed_tools:
        tools = allowed_tools
    elif agent:
        # Interactiva + delega: necesita AskUserQuestion (hilo principal) y Agent.
        tools = "[Read, Write, Agent, AskUserQuestion]" if interactive else "[Read, Write, Agent]"
    elif interactive:
        tools = "[Read, Write, AskUserQuestion]"
    else:
        tools = "[Read, Write]"
    fm = [
        "---",
        f"name: {name}",
        f'description: "{desc}"',
        f'when_to_use: "{wtu}"',
        f'argument-hint: "{hint}"',
        f"effort: {effort or 'medium'}",
        f"allowed-tools: {tools}",
    ]
    # context: fork ⊥ AskUserQuestion: una skill interactiva corre en el hilo
    # principal (un fork no puede preguntar). El campo `agent:` es el destino del
    # fork, asi que tampoco se emite sin fork: la delegacion va por la tool Agent.
    if not interactive:
        fm.append("context: fork")
        if agent:
            fm.append(f"agent: {agent}")
    fm += ["user-invocable: true", "---"]
    if interactive and agent:
        deleg = (f"\nCorre en el hilo principal (pregunta al usuario con `AskUserQuestion`). "
                 f"Delega el trabajo pesado al agente `{agent}` via la tool `Agent`.\n")
    elif agent:
        deleg = f"\nDelega la ejecucion al agente `{agent}`.\n"
    else:
        deleg = ""
    body = [
        "",
        f"# {name}",
        "",
        f"> {desc}",
        deleg,
        "## Paso 1: Parsear argumentos",
        "",
        "TODO: desarrollar los pasos del workflow siguiendo `kb-sdd-creation-guide`.",
        "Reemplazar este esqueleto.",
        "",
    ]
    return "\n".join(fm + body)


def gen_agent(name, description, skills, model, read_only, phase):
    desc = description or f"TODO: razonamiento especializado de {name}. Artefactos que produce. Que NO cubre."
    skills_list = ", ".join(skills)
    fm = [
        "---",
        f"name: {name}",
        f'description: "{desc}"',
        f"skills: [{skills_list}]",
        # Sin `memory:` a proposito (D-041): el estado del proyecto vive en sus
        # artefactos. La memoria de agente sobrevive fuera de ellos y ningun gate,
        # script ni check la ve ni la invalida. Lo vigila la regla
        # AGENT-MEMORY-DECLARED de sdd-structural-lint.py.
        "permissionMode: acceptEdits",
        f"model: {model or 'claude-opus-4-8'}",
    ]
    if read_only:
        fm.append("disallowedTools: Write, Edit")
    else:
        fm.append("effort: high")
    fm += [f"color: {_agent_color(phase)}", "---"]
    body = [
        "",
        f"# {name}",
        "",
        f"> {desc}",
        "",
        "## TODO",
        "",
        "Desarrollar el rol del agente siguiendo `kb-sdd-creation-guide`.",
        "Reemplazar este esqueleto.",
        "",
    ]
    return "\n".join(fm + body)


# ── Main ──────────────────────────────────────────────────────────────────

def build_parser():
    p = argparse.ArgumentParser(add_help=True)
    sub = p.add_subparsers(dest="kind", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("name")
    common.add_argument("--phase", required=True)
    common.add_argument("--description", default="")
    common.add_argument("--root", default=str(SDD_ROOT))
    common.add_argument("--dry-run", action="store_true")
    common.add_argument("--force", action="store_true")

    kb = sub.add_parser("kb", parents=[common])
    kb.add_argument("--effort", default="low")

    wf = sub.add_parser("wf", parents=[common])
    wf.add_argument("--when-to-use", default="")
    wf.add_argument("--argument-hint", default="")
    wf.add_argument("--effort", default="medium")
    wf.add_argument("--agent", default="")
    wf.add_argument("--allowed-tools", default="")
    wf.add_argument("--interactive", action="store_true",
                    help="La skill pregunta al usuario (AskUserQuestion): corre en el hilo "
                         "principal, SIN context: fork. La delegacion a agente sigue por Agent.")

    ag = sub.add_parser("agent", parents=[common])
    ag.add_argument("--skills", default="")
    ag.add_argument("--model", default="")
    ag.add_argument("--read-only", action="store_true")
    return p


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).resolve()

    if not _valid_phase(args.phase):
        print(f"ERROR: fase no reconocida: '{args.phase}'. "
              f"Usa: prd|spec|design|plan|tasks|global|tech/<stack>", file=sys.stderr)
        return 2

    if args.kind == "kb":
        canon = _canonical(args.name, "kb-")
        target = _skills_base(root, args.phase) / canon / "SKILL.md"
        content = gen_kb(canon, args.description, args.effort)
    elif args.kind == "wf":
        canon = _canonical(args.name, "wf-")
        target = _skills_base(root, args.phase) / canon / "SKILL.md"
        content = gen_wf(canon, args.description, args.when_to_use,
                         args.argument_hint, args.effort, args.agent,
                         args.allowed_tools, args.interactive)
    else:  # agent
        canon = args.name.strip()
        skills = [s.strip() for s in args.skills.split(",") if s.strip()]
        if not skills:
            print("ERROR: un agente requiere --skills con al menos una KB.",
                  file=sys.stderr)
            return 2
        target = _agents_base(root, args.phase) / f"{canon}.md"
        content = gen_agent(canon, args.description, skills, args.model,
                            args.read_only, args.phase)

    rel = target.relative_to(root) if target.is_relative_to(root) else target

    if target.exists() and not args.force:
        print(f"ERROR: ya existe {rel} (usa --force para sobreescribir).",
              file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"# {rel}")
        print(content)
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"✓ {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
