# Handoff — Implementar el catálogo de Casos de Uso (playbook 11.6)

> **Cómo usar este documento.** Es un handoff **autocontenido**: una conversación
> nueva (contexto limpio) puede implementar todo leyendo SOLO este fichero + el repo.
> No hace falta el historial previo. Empieza por "Estado actual" y "Trabajo a
> realizar". Los "Hallazgos no obvios" evitan re-explorar cosas ya descubiertas.

---

## 1. Contexto y objetivo

El usuario quiere un set de **casos de prueba que él ejecuta a mano** para verificar
que el ecosistema SDD se comporta como debe. NO en formato "ejecuta `/wf-x`", sino
como **Casos de Uso** orientados a objetivo de usuario, con escenarios de aceptación
y pasos numerados (acción en lenguaje natural → qué debe hacer el agente → qué output
debe aparecer). Es la realización concreta del **playbook 11.6** del `docs/ROADMAP.md`.

El usuario también pidió explícitamente que cada caso deje claro **qué skill se
invoca, qué subagente lo ejecuta y qué output produce en cada paso**.

## 2. Decisiones cerradas (con el usuario, 2026-06-15)

1. **Un solo formato: Casos de Uso procedimentales.** Se ABANDONA el formato
   declarativo `EC-*` (Disparador/Esperado/Verificación/Desviación) que se había
   empezado. Las 2 páginas ya escritas en ese formato se **reescriben** a CU.
2. **Ubicación:** guiones de prueba en `sdd/conformance/casos-de-uso/`; proyectos
   fixture donde ejecutarlos en `sdd/playground/`. Cada CU dice qué fixture usar.
3. **Interno, fuera del sitio MkDocs.** El sitio (`sdd/docs/`) es solo para
   *entender y usar*. La verificación (conformance + playground) es QA interno. Por
   eso se escribe en **markdown nativo de GitHub** (alerts `> [!NOTE]` / `> [!WARNING]`
   / `> [!CAUTION]` / `> [!IMPORTANT]`, NO admoniciones MkDocs `!!!`, que no renderizan
   fuera del sitio).
4. **Reporte de incidencias:** plantilla de GitHub Issue
   (`.github/ISSUE_TEMPLATE/desviacion-comportamiento.md`), citando el ID del caso.
5. **NO tocar `VERSION` / `CHANGELOG.md` / `install.sh`:** es tooling de QA del
   meta-repo, no se distribuye a proyectos (mismo criterio que la suite de tests del
   ROADMAP 11.3 y la documentación del 11.5).

## 3. Esquema de identificadores

- `CU-N` — un Caso de Uso (objetivo de usuario). Ej: `CU-1 — Inicializar un proyecto SDD`.
- `CU-N.x` — un escenario de aceptación dentro del CU (`a`, `b`, `c`…). **Es la unidad
  citable en incidencias.**
- Pasos numerados dentro de cada escenario.
- Los IDs no se reutilizan (si se retira un caso, su número queda libre, no se reasigna).

## 4. Plantilla de formato (cada fichero `cu-0N-*.md`)

```markdown
# CU-N — <objetivo de usuario>

**Objetivo:** qué se quiere verificar (1–2 líneas).
**Fixture:** qué usar de `playground/` (o "directorio virgen externo al repo" para arranque).
**Cobertura automática:** qué parte ya cubre `sdd/tests/` (si aplica).

## CU-N.a — <escenario de aceptación>
**Precondición:** estado de partida.
**Mecanismo:** skill / subagente / script / hook implicado (lo que el usuario quiere ver explícito).

1. <acción del usuario, en lenguaje natural — NUNCA "ejecuta /wf-x">
   → **Esperado:** <comportamiento del agente · output · artefacto con su path ·
     estado sellado · mensaje literal si aplica>
2. …

**Resultado:** PASS si <…> · FALLO si <…>
**Desviación → reportar:** issue citando `CU-N.a`.
```

Ejemplo (el patrón que el usuario validó como su visión):

```markdown
## CU-1.a — Configuración SDD vs libre
**Precondición:** proyecto sin `.sdd/project-init.json` ni `.claude/sdd-mode.json`.
**Mecanismo:** hook SessionStart `bootstrap/sdd-session-check.sh` → directiva `mode-undecided`.

1. Abres Claude Code en un directorio de proyecto virgen.
   → **Esperado:** el agente presenta el wizard de modo con `AskUserQuestion`
     ("Modo SDD" / "Modo libre") ANTES de atender nada.
2. Eliges "Modo SDD".
   → **Esperado:** se crea `.claude/sdd-mode.json` con `{"mode":"sdd",...}` y a
     continuación se invoca el skill `wf-project-init`.
3. Eliges "Modo libre".
   → **Esperado:** se crea `.claude/sdd-mode.json` con `{"mode":"free",...}` y no se
     vuelve a mencionar SDD.

**Resultado:** PASS si aparece el wizard y el JSON correcto según la elección ·
FALLO si no pregunta, o atiende la petición sin preguntar, o no escribe el JSON.
**Desviación → reportar:** issue citando `CU-1.a`.
```

## 5. Lista completa de Casos de Uso (cobertura total)

Un fichero por CU en `conformance/casos-de-uso/`, rellenables **fase por fase**:

| CU | Fichero | Objetivo | Fixture |
|----|---------|----------|---------|
| CU-1 | `cu-01-inicializar.md` | Inicializar proyecto SDD: wizard modo, init por perfil, init-incompleto, version-drift, modo libre, monorepo | dir virgen externo |
| CU-2 | `cu-02-prd.md` | Crear y dejar listo un PRD: create (con/sin `--source`), review (asunciones + sello) | greenfield |
| CU-3 | `cu-03-specs.md` | Generar specs de un PRD: analyze→gaps críticos, discover→subset, features-first, fast-track, validate, conflict, readiness, gap-resolve | greenfield |
| CU-4 | `cu-04-brownfield.md` | Specs desde código existente: `wf-spec-from-code` discover→gate humano→generate, `[INFERIDO]` bloquea plan | brownfield |
| CU-5 | `cu-05-design.md` | Diseñar una feature: intake (gate), system, feature-prototype; extract (brownfield); validate/a11y/delta/sync/export | greenfield + brownfield |
| CU-6 | `cu-06-entrega.md` | De spec a entrega: prepare-plan, plan-validate (+deuda), prepare-tasks, task-run, qa-plan, qa-verify, release | greenfield |
| CU-7 | `cu-07-cambio-producto.md` | Cambio de producto: prd-change, prd-sync-impact, spec-sync-from-prd, prd-change-cascade | greenfield |
| CU-8 | `cu-08-mantenimiento.md` | Mantenimiento: `wf-bug` (3 categorías CODE_BUG/SPEC_CHANGE/UNSPEC), `wf-spec-amend` (back-edge) | greenfield |
| CU-9 | `cu-09-gates.md` | Anti-alucinación: gates en negativo (pedir saltarse pasos y comprobar que NO cede) | greenfield |
| CU-10 | `cu-10-robustez.md` | Robustez/instalación: update con overlay, `--prune`, layout legacy plano, subdir/monorepo, sin python3, `wf-project-status` | fixtures dedicados |
| CU-11 | `cu-11-enrutado.md` | Enrutado por lenguaje natural (ROADMAP 11.1): hablar sin teclear `/wf-*`, routing correcto, args sobreviven saltos wf→wf y wf→agente | greenfield |

## 6. Estado actual del repo (qué ya existe — punto de partida)

- **`sdd/conformance/`** ya existe con:
  - `README.md` — describe el esquema en formato `EC-*` (declarativo). **A reescribir**
    para el formato CU.
  - `catalogo/` — contiene las páginas en formato `EC-*` declarativo:
    - `prd.md` → casos `EC-PRD-001..019` (los 5 workflows de PRD, completos y
      precisos). **Convertir** a `casos-de-uso/cu-02-prd.md` (PRD) y la parte de
      cambio de producto a `cu-07`.
    - `gates.md` → casos `EC-GATE-001..013` (con los mensajes de deny literales del
      script). **Convertir** a `casos-de-uso/cu-09-gates.md`.
    - 7 stubs: `arranque.md`, `spec.md`, `diseno.md`, `entrega.md`, `mantenimiento.md`,
      `robustez.md`, `enrutado.md` (solo un `> [!NOTE]` con la cobertura prevista).
  - `playbook/README.md` — placeholder del 11.6. **Se elimina**: el rol de playbook
    (orden de ejecución) pasa al `README.md` de conformance + los propios ficheros CU.
- **`sdd/playground/`** ya existe con:
  - `README.md`, `.gitignore` (commitea seeds, ignora artefactos generados).
  - `greenfield/brief.md` — seed informal de "reparto de gastos compartidos",
    diseñado para provocar `[ASUNCIÓN]` (al crear PRD) y al menos un gap `[CRÍTICO]`
    (en analyze).
  - `brownfield/auth.py` + `README.md` — módulo de registro/login con una zona
    ambigua a propósito (política de bloqueo a medias) para que la caracterización
    marque `[INFERIDO]`.
- **`.github/ISSUE_TEMPLATE/desviacion-comportamiento.md`** ya existe; hoy cita
  `EC-*` y `sdd/conformance/catalogo/`. **Actualizar** a `CU-N.x` y `casos-de-uso/`.
- **`sdd/docs/guias/contribuidor.md`** ya tiene una sección "Conformidad y playground"
  que menciona el catálogo `EC-*`. **Actualizar** el puntero a Casos de Uso (`CU-*`).
- El **sitio MkDocs** (`sdd/docs/` + `sdd/mkdocs.yml`) NO contiene la sección de
  comportamiento (ya se quitó del nav). No debe volver a entrar.

## 7. Trabajo a realizar

### Paso 0 — Reestructura
- `git mv sdd/conformance/catalogo sdd/conformance/casos-de-uso` (o crear y mover).
- Eliminar `sdd/conformance/playbook/`.
- Reescribir `sdd/conformance/README.md`: explicar el **formato CU**, el esquema de
  IDs `CU-N.x`, la tabla de CUs (sección 5), la relación con `sdd/tests/` (subconjunto
  auto-cubierto) y con `playground/` (dónde ejecutar), **un orden de ejecución
  sugerido** (este README cumple el rol del playbook 11.6), y cómo reportar.

### Paso 1 — Reescribir el patrón y VALIDAR con el usuario
Convertir al formato CU (sección 4), partiendo del contenido ya correcto de los
`EC-*` existentes:
- `catalogo/gates.md` (EC-GATE-001..013) → `casos-de-uso/cu-09-gates.md`.
- `catalogo/prd.md` (EC-PRD-001..019) → `casos-de-uso/cu-02-prd.md` (create/review) y
  `casos-de-uso/cu-07-cambio-producto.md` (change/sync-impact/cascade).
- **Parar y enseñar al usuario** estos 2-3 ficheros como patrón antes de seguir.

### Paso 2 — Rellenar el resto fase por fase
Orden sugerido: CU-1, CU-3, CU-4, CU-5, CU-6, CU-8, CU-10, CU-11 (CU-2/7/9 ya en
Paso 1). Para cada CU, explorar la fase real antes de redactar (ver Paso 3).
Actualizar los stubs existentes (`arranque/spec/diseno/entrega/mantenimiento/robustez/
enrutado`) renombrándolos a `cu-0N-*.md` y convirtiéndolos.

### Paso 3 — Patrón de exploración por fase (para precisión, no de memoria)
Antes de escribir cada CU, lanzar un subagente **Explore** que devuelva un digest con
evidencia `file:line`: para cada workflow de la fase → propósito, disparador NL
(`when_to_use`), args, `allowed-tools`, **delegación** (`agent:` / `context: fork` /
inline), pasos, **output y paths**, **checkpoints humanos**, edge cases. Más el agente
de la fase y sus KBs. (Así se hizo PRD y salió exacto.)

### Paso 4 — Fixtures que faltan
- CU-10 (robustez) necesita fixtures dedicados: un proyecto con **layout legacy plano**
  (`features/<n>/<n>_spec.md` sin subcarpetas) y un **subpaquete de monorepo** (`.sdd/`
  en un ancestro). Añadirlos a `playground/` con sus seeds.
- CU-5 brownfield-design puede requerir una UI de muestra (CSS/componentes) en
  `playground/brownfield/` para `wf-design-extract`.

### Paso 5 — Punteros
- `.github/ISSUE_TEMPLATE/desviacion-comportamiento.md`: citar `CU-N.x` y
  `sdd/conformance/casos-de-uso/`.
- `sdd/docs/guias/contribuidor.md`: actualizar la mención del catálogo (`CU-*` en vez
  de `EC-*`).
- Memoria del proyecto `doc-11-5-approach.md`: reflejar el pivote a formato CU.

## 8. Hallazgos no obvios de la conversación previa (NO re-derivar)

- **`wf-prd-sync-impact` NO vive en `prd/skills/`** sino en `sdd/spec/skills/`, y
  delega en el agente **`sdd-spec-auditor`** (no en `prd-expert`). Es read-only,
  produce `<basename>_sync_report.md` y hace un pre-pass determinista
  `sdd-sync-check.py check-all <dir> --mark`.
- **El hook de sesión EXCLUYE el repo del ecosistema.** `~/.sdd-home` contiene la ruta
  `…/ai-dev-agents-lab/sdd`; el hook calcula el git toplevel (`…/ai-dev-agents-lab`) y
  se silencia en cualquier sesión bajo él. **Consecuencia:** CU-1 (arranque/wizard)
  NO se puede probar dentro de `sdd/playground/` — hay que **copiar el fixture a un
  directorio virgen FUERA del repo** (p. ej. `~/sdd-pruebas/…`) y abrir Claude ahí.
  Para iterar rápido sin wizard, alternativa: `cd <fixture> && bash <repo>/sdd/install.sh all`.
- **Mensajes de deny de los gates:** son literales en `sdd/scripts/sdd-gate-check.py`
  (ya capturados en el `catalogo/gates.md` actual — reusarlos al convertir). Los 6
  gates: `wf-prepare-tasks` (plan VALIDADO + sin enmiendas), `wf-prepare-plan` /
  `wf-design-system` / `wf-design-feature-prototype` / `wf-qa-plan` (spec sin
  `[INCOMPLETO]`/`[CRÍTICO]`/`[INFERIDO]`, `status_sync` fiable, hash PRD), `wf-task-run`
  (plan vigente + task no retenida por enmienda). Política **fail-open**: ante
  incertidumbre/sin python3/stdin malformado → PERMITE.
- **Verificación del sitio MkDocs** (debe seguir verde tras tocar docs):
  `cd sdd && python3 -m venv /tmp/v && /tmp/v/bin/pip -q install mkdocs-material && NO_MKDOCS_2_WARNING=1 /tmp/v/bin/mkdocs build --strict` (la var silencia el banner de
  Material). El catálogo NO es markdown de MkDocs: se valida leyéndolo en GitHub.
- **Rootmap de skills:** la tabla intención→skill→args canónica está en
  `sdd/CLAUDE.md` (raíz) y en los `sdd/<fase>/CLAUDE.md`. Cruzar contra ella para que
  cada CU cite skills/args reales.
- **Scripts deterministas** (para el bloque "Mecanismo" de los CU): `sdd-seal.py`,
  `sdd-gate-check.py`, `sdd-task-state.py`, `sdd-release.py`, `sdd-sync-check.py`,
  `sdd-amend.py`, `sdd-resolve-path.py`, `sdd-next-id.py`, `sdd-features-index.py`,
  `sdd-project-status.py`, `sdd-kb-check.py`, `sdd-skill-allow.py`,
  `sdd-structural-lint.py` (+ `sdd-scaffold.py`, `sdd-meta-lint-hook.py`). Viven en
  `sdd/scripts/`; se instalan en `.sdd/scripts/` del proyecto.
- **Agentes por fase:** PRD→`prd-expert`; Spec→`sdd-spec-explorer/planner/writer/auditor`;
  Design→`design-architect`; Plan→`plan-architect`/`plan-auditor`; Tasks→`task-generator`/
  `qa-engineer`.

## 9. Verificación

- **Estructura/markdown:** los CU son markdown plano para GitHub — comprobar que
  alerts `> [!…]` y tablas renderizan, y que cada CU cita skills/subagentes/scripts
  **reales** (cross-check con el rootmap y los SKILL.md).
- **Sitio MkDocs intacto:** el build `--strict` sigue verde y sin referencias
  colgantes a `comportamiento/` ni `catalogo/`.
- **Verificación real (objetivo final):** ejecutar un CU de punta a punta sobre su
  fixture (p. ej. CU-2 sobre `playground/greenfield/brief.md`, copiado a un dir
  externo para CU-1) y comprobar que cada paso produce el output esperado.
- **Incidencias:** desviación → issue citando el `CU-N.x`.

## 10. Relación con el ROADMAP

- Esto **realiza el 11.6** (playbook de testeo manual) como catálogo de Casos de Uso.
- Los fixtures de `playground/` son el sustrato del **11.3(d)** (smoke-tests de flujos
  LLM, diferido) y del **11.1** (paso de argumentos por lenguaje natural — CU-11).
- Al cerrar el catálogo, marcar el avance de 11.6 en `docs/ROADMAP.md`.
