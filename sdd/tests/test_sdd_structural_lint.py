"""Black-box tests para scripts/sdd-structural-lint.py.

Usa el flag --root <path> (anadido en ROADMAP 11.3 para testabilidad: default =
comportamiento de siempre, escanear el arbol del ecosistema) para apuntar el
linter a arboles-fixture aislados. Cada tipo de finding se prueba con un fixture
que planta la violacion (debe marcarla) y, donde aporta, un fixture limpio (no
debe marcarla). Ademas verifica exit codes, forma del --json, y los DOS
edge-cases criticos que NO deben regresar:
  (a) lineas `description:` de frontmatter no se marcan como CITED-RULE-MISSING,
  (b) un wf con `context: fork` + `agent:` no se marca por Agent en
      ALLOWED-TOOLS-MISMATCH.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


def lint(root, *flags):
    return run_script("sdd-structural-lint.py", "--root", root, *flags)


def types_in(root, *flags):
    """Devuelve el set de tipos de finding emitidos en --json (filtro de flags)."""
    r = run_script("sdd-structural-lint.py", "--root", root, "--json", *flags)
    return r, {f["type"] for f in json.loads(r.stdout)}


def skill_md(name, body, extra_fm=""):
    return (f"---\nname: {name}\ndescription: una skill.\n"
            f"user-invocable: {'true' if name.startswith('wf-') else 'false'}\n"
            f"{extra_fm}---\n\n# {name}\n\n{body}\n")


class StructuralLintTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    # --- KB con N reglas, para citas validas/invalidas ---------------------
    def _kb_with_rules(self, name, n):
        rules = "\n".join(f"## Regla {i}: regla {i}\nTexto." for i in range(1, n + 1))
        write(self.root / "spec" / "skills" / name / "SKILL.md",
              skill_md(name, rules))

    # === CITED-RULE-MISSING ===============================================
    def test_cited_rule_missing_flagged(self):
        self._kb_with_rules("kb-real", 3)
        write(self.root / "spec" / "skills" / "kb-otra" / "SKILL.md",
              skill_md("kb-otra", "Ver Regla 9 de kb-real para el detalle."))
        r, types = types_in(self.root)
        self.assertIn("CITED-RULE-MISSING", types, r.stdout)

    def test_cited_rule_existing_not_flagged(self):
        self._kb_with_rules("kb-real", 3)
        write(self.root / "spec" / "skills" / "kb-otra" / "SKILL.md",
              skill_md("kb-otra", "Ver Regla 2 de kb-real para el detalle."))
        _, types = types_in(self.root)
        self.assertNotIn("CITED-RULE-MISSING", types)

    # === CITED-SKILL-MISSING ==============================================
    def test_cited_skill_missing_flagged(self):
        write(self.root / "spec" / "skills" / "kb-otra" / "SKILL.md",
              skill_md("kb-otra", "Segun Regla 1 de kb-fantasma esto aplica."))
        _, types = types_in(self.root)
        self.assertIn("CITED-SKILL-MISSING", types)

    # === CITED-RULE-ON-WORKFLOW ===========================================
    def test_cited_rule_on_workflow_flagged(self):
        write(self.root / "spec" / "skills" / "kb-otra" / "SKILL.md",
              skill_md("kb-otra", "Como dice la Regla 3 de wf-algo."))
        _, types = types_in(self.root)
        self.assertIn("CITED-RULE-ON-WORKFLOW", types)

    # === ABSOLUTE-PATH ====================================================
    def test_absolute_path_flagged(self):
        write(self.root / "spec" / "skills" / "kb-otra" / "SKILL.md",
              skill_md("kb-otra", "Lee /Users/oscar/proyecto/spec.md como entrada."))
        _, types = types_in(self.root)
        self.assertIn("ABSOLUTE-PATH", types)

    def test_absolute_path_in_docs_not_flagged(self):
        # docs/ se excluye: el path absoluto es evidencia narrativa
        write(self.root / "docs" / "ROADMAP.md",
              "# Roadmap\n\nHallazgo en /Users/oscar/x.md durante la auditoria.\n")
        _, types = types_in(self.root)
        self.assertNotIn("ABSOLUTE-PATH", types)

    # === NAME-MISMATCH ====================================================
    def test_name_mismatch_flagged(self):
        # name del frontmatter != nombre del directorio
        write(self.root / "spec" / "skills" / "kb-dir" / "SKILL.md",
              skill_md("kb-otro-nombre", "Cuerpo."))
        _, types = types_in(self.root)
        self.assertIn("NAME-MISMATCH", types)

    def test_name_match_not_flagged(self):
        write(self.root / "spec" / "skills" / "kb-dir" / "SKILL.md",
              skill_md("kb-dir", "Cuerpo."))
        _, types = types_in(self.root)
        self.assertNotIn("NAME-MISMATCH", types)

    # === REFERENCE-PATH-MISSING ===========================================
    def test_reference_path_missing_flagged(self):
        write(self.root / "spec" / "skills" / "kb-ref" / "SKILL.md",
              skill_md("kb-ref",
                       "Consulta ${CLAUDE_SKILL_DIR}/references/no_existe.md aqui."))
        _, types = types_in(self.root)
        self.assertIn("REFERENCE-PATH-MISSING", types)

    def test_reference_path_existing_not_flagged(self):
        write(self.root / "spec" / "skills" / "kb-ref" / "references" / "guia.md",
              "contenido")
        write(self.root / "spec" / "skills" / "kb-ref" / "SKILL.md",
              skill_md("kb-ref",
                       "Consulta ${CLAUDE_SKILL_DIR}/references/guia.md aqui."))
        _, types = types_in(self.root)
        self.assertNotIn("REFERENCE-PATH-MISSING", types)

    # === SKILL-REF-MISSING ================================================
    def test_skill_ref_missing_flagged_in_readme(self):
        write(self.root / "spec" / "README.md",
              "# Fase spec\n\nUsa `kb-inexistente` para esto.\n")
        _, types = types_in(self.root)
        self.assertIn("SKILL-REF-MISSING", types)

    def test_skill_ref_real_not_flagged(self):
        write(self.root / "spec" / "skills" / "kb-existe" / "SKILL.md",
              skill_md("kb-existe", "Cuerpo."))
        write(self.root / "spec" / "README.md",
              "# Fase spec\n\nUsa `kb-existe` para esto.\n")
        _, types = types_in(self.root)
        self.assertNotIn("SKILL-REF-MISSING", types)

    # === ALLOWED-TOOLS-MISMATCH ===========================================
    def test_allowed_tools_bash_missing_flagged(self):
        write(self.root / "plan" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "Paso 1.\n\n!git rev-parse HEAD\n",
                       extra_fm="allowed-tools: [Read, Write]\n"))
        _, types = types_in(self.root)
        self.assertIn("ALLOWED-TOOLS-MISMATCH", types)

    def test_allowed_tools_bash_present_not_flagged(self):
        write(self.root / "plan" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "Paso 1.\n\n!git rev-parse HEAD\n",
                       extra_fm="allowed-tools: [Read, Write, Bash]\n"))
        _, types = types_in(self.root)
        self.assertNotIn("ALLOWED-TOOLS-MISMATCH", types)

    # === DESCRIPTION-TOO-LONG =============================================
    def test_description_too_long_flagged(self):
        long_desc = "x" * 230
        write(self.root / "spec" / "skills" / "kb-long" / "SKILL.md",
              f"---\nname: kb-long\ndescription: {long_desc}\n"
              f"user-invocable: false\n---\n\n# kb-long\n\nCuerpo.\n")
        _, types = types_in(self.root)
        self.assertIn("DESCRIPTION-TOO-LONG", types)

    # === USER-INVOCABLE-MISSING ===========================================
    def test_user_invocable_missing_on_wf_flagged(self):
        write(self.root / "spec" / "skills" / "wf-noui" / "SKILL.md",
              "---\nname: wf-noui\ndescription: un wf.\n---\n\n# wf-noui\n\nCuerpo.\n")
        _, types = types_in(self.root)
        self.assertIn("USER-INVOCABLE-MISSING", types)

    def test_user_invocable_missing_on_kb_flagged(self):
        # kb sin `user-invocable: false`
        write(self.root / "spec" / "skills" / "kb-noui" / "SKILL.md",
              "---\nname: kb-noui\ndescription: una kb.\n---\n\n# kb-noui\n\nCuerpo.\n")
        _, types = types_in(self.root)
        self.assertIn("USER-INVOCABLE-MISSING", types)

    # === EDGE-CASE (a): description: no se marca como CITED-RULE-MISSING ===
    def test_description_provenance_not_flagged_as_cited_rule(self):
        # La linea description: cita una Regla N de una kb que no la define;
        # NO debe marcarse (provenance historica intencionada).
        self._kb_with_rules("kb-real", 2)
        write(self.root / "spec" / "skills" / "kb-prov" / "SKILL.md",
              "---\nname: kb-prov\n"
              "description: SSoT extraida de Regla 9 de kb-real (provenance).\n"
              "user-invocable: false\n---\n\n# kb-prov\n\nCuerpo limpio sin citas.\n")
        r, types = types_in(self.root)
        self.assertNotIn("CITED-RULE-MISSING", types, r.stdout)
        self.assertNotIn("CITED-SKILL-MISSING", types, r.stdout)

    # === EDGE-CASE (b): context: fork + agent: no se marca por Agent =======
    def test_fork_pattern_not_flagged_for_agent(self):
        body = "Paso 1: el agente, con sus skills en contexto, hace el trabajo.\n"
        write(self.root / "design" / "skills" / "wf-fork" / "SKILL.md",
              skill_md("wf-fork", body,
                       extra_fm="allowed-tools: [Read]\ncontext: fork\n"
                                "agent: design-architect\n"))
        r, types = types_in(self.root, "--severity", "warning")
        self.assertNotIn("ALLOWED-TOOLS-MISMATCH", types, r.stdout)

    # === Exit codes =======================================================
    def test_exit_0_when_clean(self):
        # Un arbol con una sola skill perfectamente formada -> sin findings
        write(self.root / "spec" / "skills" / "kb-clean" / "SKILL.md",
              skill_md("kb-clean", "Cuerpo limpio."))
        r = lint(self.root, "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_exit_1_when_only_warnings(self):
        write(self.root / "spec" / "skills" / "wf-noui" / "SKILL.md",
              "---\nname: wf-noui\ndescription: un wf.\n---\n\n# wf-noui\n\nCuerpo.\n")
        r = lint(self.root, "--check")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_exit_2_when_blocking(self):
        write(self.root / "spec" / "skills" / "kb-x" / "SKILL.md",
              skill_md("kb-x", "Lee /Users/oscar/x.md como entrada."))
        r = lint(self.root, "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    # === Forma del --json =================================================
    def test_json_shape(self):
        write(self.root / "spec" / "skills" / "kb-x" / "SKILL.md",
              skill_md("kb-x", "Lee /Users/oscar/x.md como entrada."))
        r = lint(self.root, "--json")
        data = json.loads(r.stdout)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        for f in data:
            self.assertEqual(set(f.keys()),
                             {"severity", "type", "file", "line", "message"})
            self.assertIn(f["severity"], ("blocking", "warning"))
            self.assertIsInstance(f["line"], int)

    def test_severity_filter_blocking_only(self):
        # arbol con un blocking (path) y un warning (kb sin user-invocable)
        write(self.root / "spec" / "skills" / "kb-x" / "SKILL.md",
              "---\nname: kb-x\ndescription: una kb.\n---\n\n"
              "# kb-x\n\nLee /Users/oscar/x.md aqui.\n")
        r = lint(self.root, "--json", "--severity", "blocking")
        data = json.loads(r.stdout)
        self.assertTrue(all(f["severity"] == "blocking" for f in data), r.stdout)
        self.assertTrue(any(f["type"] == "ABSOLUTE-PATH" for f in data))


class DefaultScanTest(unittest.TestCase):
    """El escaneo por defecto (sin --root) sigue funcionando sobre el repo real."""

    def test_default_scan_no_blocking(self):
        # El repo sano debe estar en blocking=0 (ver ROADMAP 11.4a).
        r = run_script("sdd-structural-lint.py", "--check", "--severity", "blocking")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)  # 0 blocking pero hay warnings -> exit 1
        self.assertIn("0 blocking", r.stdout)


if __name__ == "__main__":
    unittest.main()
