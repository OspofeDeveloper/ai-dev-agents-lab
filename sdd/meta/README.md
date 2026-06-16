# `meta/` — Gobernanza del ecosistema

**Qué es.** El sistema que **construye y mantiene el propio ecosistema SDD**: crear, auditar,
refactorizar y medir la conformidad de las skills y agentes. Es la capa que opera *sobre* el
pipeline, no dentro de él.

**Qué contiene.**

```
meta/
├── CLAUDE.md            meta-orquestador (routing de autoría/auditoría del ecosistema)
├── skill-registry.md    índice persistente de TODAS las skills (autogenerado)
├── agents/              sdd-author · sdd-auditor · sdd-conformance
└── skills/              kb-* de arquitectura/creación/auditoría/conformance + wf-* de autoría
```

Workflows de autoría: `wf-skill-create`, `wf-agent-create`, `wf-stack-create`, `wf-sdd-refactor`
(delegan en `sdd-author`); `wf-sdd-audit` (delega en `sdd-auditor`); `wf-sdd-status` y
`wf-conformance-status` (mecánicos); `wf-conformance-author` (delega en `sdd-conformance`).

**Qué NO es / qué no va aquí.**
- No es una fase del pipeline (no produce PRD/Spec/Plan/Tasks de un producto).
- No es la verificación de comportamiento del ecosistema (eso es `../conformance/`).
- `skill-registry.md` **no se edita a mano**: lo regenera `../scripts/generate-skill-registry.py`.
- Las reglas transversales viven en `kb-sdd-skill-architecture` y las convenciones de creación en
  `kb-sdd-creation-guide` (la "Regla de reparto" de [`CLAUDE.md`](CLAUDE.md) dice qué vive dónde).

**A quién sirve.** Al **desarrollo del ecosistema** (dogfooding). Sus skills `meta` no se instalan
en proyectos consumidores; las dos skills globales de arranque viven en `../bootstrap/`.
