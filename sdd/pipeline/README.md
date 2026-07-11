# `pipeline/` — Las fases del pipeline SDD

**Qué es.** El producto central del ecosistema: las cinco fases del Spec Driven Development,
en orden de pipeline. Es lo que se instala en un proyecto consumidor (vía `install.sh`).

**Qué contiene.** Una carpeta por fase, cada una autocontenida con sus capas (`kb-*`/`wf-*`/agente)
y su documentación local:

| Fase | Responsabilidad | Layout |
|---|---|---|
| `prd/` | Crear y revisar el PRD | `skills/` · `agents/` · `CLAUDE.md` · `README.md` · `DIAGRAMS.md` |
| `spec/` | Discovery + escritura/validación de specs por feature | íd. (+ `shared/templates/`) |
| `design/` | Sistema visual y artefactos de feature (Stitch) | íd. |
| `plan/` | Spec → Plan técnico | íd. |
| `tasks/` | Plan → Tasks + ejecución + QA + release | `skills/` · `agents/` · `CLAUDE.md` |

Cada fase aplica las **3 capas fijas** (orquestador `CLAUDE.md` → `wf-*` → agente → `kb-*`),
cuya definición canónica vive en `kb-sdd-skill-architecture` (Regla 1). El enrutado efectivo lo
hacen las `description` de los skills (eager) + `sdd-routing.md`; el `CLAUDE.md` de fase quedó como
**marcador fino** tras D-023 (sin rootmap). El `README.md` de fase es su mapa humano.

**Layout por feature (en el proyecto consumidor).** Cada feature usa subcarpetas por fase
(`spec/`, `design/`, `plan/`, `tasks/`); el layout plano legacy (`features/<n>/<n>_spec.md`)
sigue siendo válido. Esto pertenece a los artefactos del consumidor, no a este directorio fuente.

**Qué NO es / qué no va aquí.**
- No es gobernanza del ecosistema (eso es `../meta/`).
- No es especialización por stack (eso es `../tech/`): las fases son **stack-agnósticas**.
- Los nombres de fase (`prd`/`spec`/`design`/`plan`/`tasks`) son **contrato de producto** — aparecen
  en `.sdd/project-init.json`, en `.claude/rules/sdd-<fase>.md` del consumidor y en
  `generate-skill-registry.py`/`install.sh`. No se renombran sin actualización transversal.

**A quién sirve.** Al **proyecto consumidor**: estas piezas se copian a su `.claude/`.

> Mapa de cada fase: [`prd/README.md`](prd/README.md) · [`spec/README.md`](spec/README.md) ·
> [`design/README.md`](design/README.md) · [`plan/README.md`](plan/README.md). El orquestador
> global del pipeline vive en [`../CLAUDE.md`](../CLAUDE.md).
