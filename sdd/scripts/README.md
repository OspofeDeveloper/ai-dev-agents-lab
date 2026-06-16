# `scripts/` — Herramientas deterministas

**Qué es.** Los scripts Python que hacen el trabajo **mecanizable** del ecosistema (sellado, gates,
estado, resolución de rutas, generación de índices, lint estructural). El principio rector: lo que
debe verificarse o computarse de forma reproducible **no se confía a la prosa** de un agente.

**Dos clases (importante).**

1. **Enforcement — viajan al consumidor.** `install.sh` los copia (con sello de versión) a
   `<proyecto>/.sdd/scripts/`; los ejecutan los hooks/CI del proyecto. Son contrato de producto:
   ```
   sdd-seal.py · sdd-gate-check.py · sdd-task-state.py · sdd-sync-check.py · sdd-skill-allow.py
   sdd-amend.py · sdd-features-index.py · sdd-project-status.py · sdd-kb-check.py · sdd-release.py
   sdd-next-id.py · sdd-resolve-path.py
   ```
2. **Solo-ecosistema — no se instalan.** Sirven al desarrollo/CI de este repo:
   ```
   generate-skill-registry.py · sdd-structural-lint.py · sdd-conformance-coverage.py
   sdd-meta-lint-hook.py · sdd-scaffold.py · merge-claude-settings.py
   ```

**Qué NO es / qué no va aquí.**
- No contienen lógica de producto que dependa de juicio semántico (eso vive en agentes + `kb-*`).
- No deben moverse de nivel: cada script resuelve la raíz del ecosistema con
  `Path(__file__).resolve().parent.parent`, así que `scripts/` cuelga **directo de `sdd/`**.

**A quién sirve.** A ambos lados, según la clase: los de enforcement al **consumidor**; el resto al
**ecosistema-dev**. La lista exacta de enforcement que se distribuye es la de `../install.sh`
(sección "Instalar scripts de enforcement"). Cobertura de la suite: [`../tests/`](../tests/README.md).
