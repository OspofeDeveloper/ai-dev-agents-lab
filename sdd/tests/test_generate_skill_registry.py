"""Black-box tests para scripts/generate-skill-registry.py.

NOTA DE AISLAMIENTO: este script NO acepta argumento de ruta ni flag --check;
resuelve su raiz como `Path(__file__).resolve().parent.parent` y SIEMPRE escribe
meta/skill-registry.md de esa raiz. Para aislarlo sin tocar el repo real,
copiamos el script a un arbol-fixture (<tmp>/scripts/gen.py) con un meta/ y
unas skills sinteticas: al ejecutarse desde ahi, escanea el fixture y escribe
<tmp>/meta/skill-registry.md. Asi probamos escaneo + idempotencia sin riesgo.

LIMITACION DOCUMENTADA: al carecer de --check, no se puede testear un modo de
verificacion de drift (no existe). La idempotencia se prueba por igualdad de
bytes entre dos ejecuciones.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import SCRIPTS, run_script_at, write  # noqa: E402


def skill(name, desc):
    return f"---\nname: {name}\ndescription: {desc}\n---\n\n# {name}\n\nCuerpo.\n"


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # arbol-fixture con el script copiado a <root>/scripts/
        (self.root / "scripts").mkdir(parents=True)
        self.script = self.root / "scripts" / "generate-skill-registry.py"
        shutil.copy(SCRIPTS / "generate-skill-registry.py", self.script)
        (self.root / "meta").mkdir(parents=True)
        # 3 skills sinteticas: 1 meta-kb, 1 meta-wf, 1 de fase spec
        write(self.root / "meta" / "skills" / "kb-foo" / "SKILL.md",
              skill("kb-foo", "Una kb de prueba. Segunda frase."))
        write(self.root / "meta" / "skills" / "wf-bar" / "SKILL.md",
              skill("wf-bar", "Un workflow de prueba que hace cosas."))
        write(self.root / "spec" / "skills" / "kb-baz" / "SKILL.md",
              skill("kb-baz", "Otra kb de fase spec."))

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self):
        return run_script_at(self.script)

    def test_scans_and_lists_skills(self):
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        reg = (self.root / "meta" / "skill-registry.md").read_text(encoding="utf-8")
        self.assertIn("kb-foo", reg)
        self.assertIn("wf-bar", reg)
        self.assertIn("kb-baz", reg)
        # totales en el header generado
        self.assertIn("Total: 3 skills", reg)
        self.assertIn("1 wf-* (user-invocable)", reg)
        self.assertIn("2 kb-*", reg)
        # invocabilidad correcta por tabla: wf-* true, kb-* false
        self.assertRegex(reg, r"\|\s*wf-bar\s*\|.*\|\s*true\s*\|")
        self.assertRegex(reg, r"\|\s*kb-foo\s*\|.*\|\s*false\s*\|")

    def test_idempotent_byte_identical(self):
        self._run()
        first = (self.root / "meta" / "skill-registry.md").read_text(encoding="utf-8")
        self._run()
        second = (self.root / "meta" / "skill-registry.md").read_text(encoding="utf-8")
        self.assertEqual(first, second,
                         "regenerar sin cambios debe producir bytes identicos")

    def test_new_skill_appears_after_regen(self):
        self._run()
        write(self.root / "spec" / "skills" / "wf-nuevo" / "SKILL.md",
              skill("wf-nuevo", "Workflow recien anadido."))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        reg = (self.root / "meta" / "skill-registry.md").read_text(encoding="utf-8")
        self.assertIn("wf-nuevo", reg)
        self.assertIn("Total: 4 skills", reg)


if __name__ == "__main__":
    unittest.main()
