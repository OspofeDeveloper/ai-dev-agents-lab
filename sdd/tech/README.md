# `tech/` — Overlays de especialización por stack

**Qué es.** El conocimiento específico de cada **stack de implementación** (KMM, y a futuro otros).
Un overlay es **ortogonal** a las fases: no es una fase del pipeline, sino una capa que aporta
conocimiento técnico a las fases `plan` y `tasks`.

**Qué contiene.** Una carpeta por stack. Hoy:

```
tech/
└── kmm/            Kotlin Multiplatform Mobile
    ├── skills/
    │   ├── plan/    kb-* cargadas por el plan-architect del stack
    │   └── tasks/   kb-* cargadas por el task-generator del stack
    ├── agents/      agentes específicos del stack (opcional)
    ├── install.sh   instala el overlay sobre la base ya instalada
    ├── CLAUDE.md    routing específico del stack (si aplica)
    └── BACKLOG.md
```

El overlay **sobreescribe por basename** las piezas genéricas de `plan`/`tasks` con su variante
especializada (p. ej. una `kb-plan-expert` KMM sustituye a la genérica). Se instala **después** de
la base: primero `install.sh`, luego `tech/<stack>/install.sh`.

**Qué NO es / qué no va aquí.**
- No es una fase: un directorio de stack al mismo nivel que `prd/`/`spec/`… rompería la separación
  fases ↔ targets.
- No redefine la metodología de las fases; solo aporta la capa de stack sobre los hooks genéricos.
- La definición canónica del contrato de overlay vive en `kb-sdd-skill-architecture` (Regla 16) y en
  `kb-sdd-stack-overlay-contract`; este README no la duplica.

**A quién sirve.** Al **proyecto consumidor** cuyo `stack` lo declara (lo aplica `wf-project-init`
delegando al init del stack). `tech/kmm/install.sh` asume estar a dos niveles de la raíz `sdd/`
(`../../`): mantener esa profundidad al tocar el árbol.
