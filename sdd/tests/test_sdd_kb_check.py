"""Black-box tests para scripts/sdd-kb-check.py.

Verificador determinista de KBs declaradas por agentes: comprueba que cada KB
del frontmatter `skills:` de un agente instalado existe como
`<claude_dir>/skills/<kb>/SKILL.md`. El auto-reporte del agente es senal
secundaria; esto es la parte verificable.

Contrato (leido del script):
  - exit 0: todas las KBs declaradas existen instaladas
  - exit 1: error de uso / `.claude/` no encontrado / agente no encontrado
  - exit 2: al menos un agente declara una KB no instalada
  - parsea frontmatter `skills:` en forma inline `[a, b]` y multilinea (`- a`)
  - acota al frontmatter (no parsea bullets del cuerpo)

Estrategia: arbol-fixture en tmpdir apuntado con --claude-dir (no toca el
`.claude/` real). Planted (KB faltante) vs clean.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


def agent_md(skills_line):
    return f"""---
name: demo-agent
description: agente de prueba
skills: {skills_line}
---

# demo-agent

Cuerpo del agente.
- esto es un bullet del cuerpo, no una skill

## Verificación de contexto

Incluye `## KB Load Status` para cada KB de tu frontmatter `skills:`.
"""


def agent_md_multiline(skills):
    items = "\n".join(f"  - {s}" for s in skills)
    return f"""---
name: demo-agent
description: agente de prueba
skills:
{items}
---

# demo-agent

## Verificación de contexto

Incluye `## KB Load Status` para cada KB de tu frontmatter `skills:`.
"""


class KbCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.claude = Path(self.tmp.name) / ".claude"
        self.agents = self.claude / "agents"
        self.skills = self.claude / "skills"
        self.agents.mkdir(parents=True)
        self.skills.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _install_kb(self, name):
        write(self.skills / name / "SKILL.md", f"# {name}\n")

    def _run(self, *extra):
        return run_script("sdd-kb-check.py", "--claude-dir", str(self.claude), *extra)

    def test_all_kbs_installed_exit_0(self):
        self._install_kb("kb-plan-expert")
        self._install_kb("kb-a11y-expert")
        write(self.agents / "demo-agent.md",
              agent_md("[kb-plan-expert, kb-a11y-expert]"))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK", r.stdout)

    # --- D-069: enumera todas o ninguna; la lista PARCIAL es la que deriva ---

    def _agent_with_section(self, skills_inline, section_body):
        return (f"---\nname: demo-agent\nskills: {skills_inline}\n---\n\n"
                f"# Demo\n\n## Verificación de contexto\n\n{section_body}\n")

    def test_partial_enumeration_exit_2(self):
        """Una lista parcial se lee como exhaustiva y no lo es.

        El `KB Load Status` solo cubre lo enumerado: la KB que falta nunca sale
        `missing`, ni ahi ni en ningun otro sitio. Es lo que dejo a dos agentes
        de Spec sin verificar `kb-spec-characterization`.
        """
        for kb in ("kb-plan-expert", "kb-a11y-expert"):
            self._install_kb(kb)
        write(self.agents / "demo-agent.md", self._agent_with_section(
            "[kb-plan-expert, kb-a11y-expert]",
            "Confirma `kb-plan-expert` e incluye `## KB Load Status`."))
        r = self._run()
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("kb-a11y-expert", r.stderr)
        self.assertIn("NO enumeradas", r.stderr)

    def test_full_enumeration_exit_0(self):
        """El delta: la misma lista, completa, pasa."""
        for kb in ("kb-plan-expert", "kb-a11y-expert"):
            self._install_kb(kb)
        write(self.agents / "demo-agent.md", self._agent_with_section(
            "[kb-plan-expert, kb-a11y-expert]",
            "Confirma `kb-plan-expert` y `kb-a11y-expert`, e incluye `## KB Load Status`."))
        self.assertEqual(self._run().returncode, 0)

    def test_generic_reference_is_not_a_finding(self):
        """Remitir al frontmatter es la forma PREFERIDA: no duplica, no deriva.

        Es lo que ya hacian los dos arquitectos de Design, y por eso eran los
        unicos que no podian quedarse cortos.
        """
        for kb in ("kb-plan-expert", "kb-a11y-expert"):
            self._install_kb(kb)
        write(self.agents / "demo-agent.md", self._agent_with_section(
            "[kb-plan-expert, kb-a11y-expert]",
            "Incluye `## KB Load Status` para cada KB de tu frontmatter `skills:`."))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_section_is_a_finding(self):
        """Sin seccion de verificacion no hay auto-reporte que valga."""
        self._install_kb("kb-plan-expert")
        write(self.agents / "demo-agent.md",
              "---\nname: demo-agent\nskills: [kb-plan-expert]\n---\n\n# Demo\n")
        self.assertEqual(self._run().returncode, 2)

    def test_missing_kb_exit_2(self):
        self._install_kb("kb-plan-expert")  # kb-a11y-expert NO instalada
        write(self.agents / "demo-agent.md",
              agent_md("[kb-plan-expert, kb-a11y-expert]"))
        r = self._run()
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("kb-a11y-expert", r.stderr)

    def test_multiline_skills_form(self):
        self._install_kb("kb-spec-expert")
        write(self.agents / "demo-agent.md",
              agent_md_multiline(["kb-spec-expert"]))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_multiline_with_missing_exit_2(self):
        self._install_kb("kb-spec-expert")
        write(self.agents / "demo-agent.md",
              agent_md_multiline(["kb-spec-expert", "kb-no-existe"]))
        r = self._run()
        self.assertEqual(r.returncode, 2)
        self.assertIn("kb-no-existe", r.stderr)

    def test_body_bullets_not_parsed_as_skills(self):
        # El frontmatter inline declara una sola KB; el bullet del cuerpo no cuenta.
        self._install_kb("kb-plan-expert")
        write(self.agents / "demo-agent.md", agent_md("[kb-plan-expert]"))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_one_agent_filter(self):
        self._install_kb("kb-plan-expert")
        write(self.agents / "good.md", agent_md("[kb-plan-expert]"))
        write(self.agents / "bad.md", agent_md("[kb-falta]"))
        # filtrando al bueno -> 0
        r = self._run("--agent", "good")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # filtrando al malo -> 2
        r2 = self._run("--agent", "bad")
        self.assertEqual(r2.returncode, 2)

    def test_agent_filter_accepts_md_suffix(self):
        self._install_kb("kb-plan-expert")
        write(self.agents / "good.md", agent_md("[kb-plan-expert]"))
        r = self._run("--agent", "good.md")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_unknown_agent_exit_1(self):
        r = self._run("--agent", "no-existe")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no encontrado", r.stderr)

    def test_no_agents_dir_exit_0(self):
        import shutil
        shutil.rmtree(self.agents)
        r = self._run()
        self.assertEqual(r.returncode, 0)
        self.assertIn("nada que verificar", r.stdout)

    def test_missing_claude_dir_exit_1(self):
        r = run_script("sdd-kb-check.py", "--claude-dir",
                       str(Path(self.tmp.name) / "no-existe"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("no se encontró", r.stderr)

    def test_quiet_suppresses_ok_summary(self):
        self._install_kb("kb-plan-expert")
        write(self.agents / "demo-agent.md", agent_md("[kb-plan-expert]"))
        r = self._run("--quiet")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "", "quiet no debe imprimir el resumen OK")

    def test_agent_without_skills_is_clean(self):
        write(self.agents / "noskills.md",
              "---\nname: x\ndescription: y\n---\n# x\n")
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
