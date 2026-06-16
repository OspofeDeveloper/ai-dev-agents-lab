# `bootstrap/` — Arranque global del ecosistema

**Qué es.** La **entrada** del ecosistema: lo que se instala una vez por máquina para que cualquier
proyecto pueda decidir su modo SDD y arrancar. Vive en la raíz de `sdd/` (no bajo `pipeline/`)
porque es el instalador/bootstrap, no una fase.

**Qué contiene.**

```
bootstrap/
├── sdd-session-check.sh     hook SessionStart (se instala en ~/.claude/hooks/)
├── claude-global-block.md   bloque que se añade a ~/.claude/CLAUDE.md (protocolo de sesión)
└── skills/
    ├── wf-project-init/      inicializa/ampliar un proyecto SDD (skill global)
    └── wf-sdd-update/        actualiza la instalación SDD de un proyecto (skill global)
```

`setup.sh` (en la raíz de `sdd/`) materializa todo esto: copia las dos skills globales a
`~/.claude/skills/`, instala el hook en `~/.claude/hooks/`, escribe `~/.sdd-home` (apunta a este
repo) y añade el bloque global a `~/.claude/CLAUDE.md`. El hook lee `~/.sdd-home` en cada sesión y
emite la directiva `[SDD-PROTOCOL]` cuando procede.

**Qué NO es / qué no va aquí.**
- No son fases (`wf-project-init`/`wf-sdd-update` son skills **globales** de arranque, no de pipeline).
- No es el instalador por proyecto (eso es `../install.sh`, que copia las fases al `.claude/` local).

**A quién sirve.** Al **arranque global** (toda la máquina) y, a través del hook, a cada sesión de
cualquier proyecto. Las rutas externas que crea (`~/.sdd-home`, `~/.claude/skills/wf-project-init`,
`~/.claude/hooks/sdd-session-check.sh`) son **contrato**: no se renombran.
