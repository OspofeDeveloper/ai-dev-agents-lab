# Conformidad del ecosistema SDD — Casos de Uso

Esta área es el **contrato de comportamiento observable del propio ecosistema**,
escrito como un catálogo de **Casos de Uso** que tú ejecutas a mano: para cada
objetivo de usuario, qué debe hacer exactamente el sistema, paso a paso. Es la "Spec
del SDD" — sus propios Criterios de Aceptación, verificables sin leer código.

No es documentación de usuario (esa vive en [`../docs/`](../docs/) → sitio MkDocs).
Es la herramienta interna de **verificación y QA** del ecosistema, y realiza el
**playbook 11.6** del ROADMAP. Sirve para:

1. **Verificar** que el ecosistema hace lo que debe, ejecutando cada caso sobre un
   **proyecto real** (cada CU dice qué tipo de proyecto buscar; ver
   [Sobre qué proyectos ejecutar](#sobre-qué-proyectos-ejecutar)).
2. **Reportar** desviaciones con un lenguaje común: cada escenario tiene un ID citable.

```
conformance/
  README.md          ← esto (rol de playbook: qué ejecutar y en qué orden)
  casos-de-uso/      ← los Casos de Uso (cu-0N-*.md), la SSoT del "qué debería pasar"
```

> [!NOTE]
> **No hay fixtures sintéticos.** Los casos se ejecutan sobre **proyectos reales**
> tuyos (más honesto que un seed de juguete y sin mantenimiento). Cada CU abre con un
> bloque **"Proyecto a usar"** que describe qué buscar y cómo llegar al estado de
> partida.

> [!NOTE]
> **Flujo típico de uso.** Eliges un CU → lo ejecutas sobre tu proyecto **hablando**
> (nunca tecleando `/wf-*`) → comparas cada paso con su **Esperado** → si **diverge**,
> abres una incidencia citando el ID del escenario (ver [Cómo reportar](#cómo-reportar)).

---

## El esquema de identificadores

- **`CU-N`** — un Caso de Uso, orientado a un **objetivo de usuario** (no a un comando).
  Ej.: `CU-1 — Inicializar un proyecto SDD`.
- **`CU-N.x`** — un escenario de aceptación dentro del CU (`a`, `b`, `c`…). **Es la
  unidad citable en incidencias.**
- Dentro de cada escenario, **pasos numerados**: cada paso es una acción del usuario en
  lenguaje natural → el **Esperado** (comportamiento del agente · output · artefacto con
  su path · estado sellado · mensaje literal si aplica).
- Los IDs **no se reutilizan**: si un caso se retira, su número queda libre pero no se
  reasigna (igual que los CAs de un spec).

---

## El catálogo de Casos de Uso

| CU | Fichero | Objetivo | Proyecto a usar |
|----|---------|----------|---------|
| CU-1 | [`casos-de-uso/cu-01-inicializar.md`](casos-de-uso/cu-01-inicializar.md) | Inicializar un proyecto SDD: wizard de modo, init por topología (authoring/consumer/standalone), init-incompleto, version-drift, modo libre, monorepo | repo nuevo/virgen **externo** al ecosistema |
| CU-2 | [`casos-de-uso/cu-02-prd.md`](casos-de-uso/cu-02-prd.md) | Crear y dejar listo un PRD: create (con/sin notas), review (asunciones + sello) | producto real con notas/brief |
| CU-3 | [`casos-de-uso/cu-03-specs.md`](casos-de-uso/cu-03-specs.md) | Generar specs de un PRD: analyze→gaps, discover→subset, features-first, fast-track, validate, conflict, readiness, gap-resolve | el de CU-2, con PRD `LISTO` |
| CU-4 | [`casos-de-uso/cu-04-brownfield.md`](casos-de-uso/cu-04-brownfield.md) | Specs desde código existente: `wf-spec-from-code` discover→gate→generate, `[INFERIDO]` bloquea plan | código heredado real sin specs |
| CU-5 | [`casos-de-uso/cu-05-design.md`](casos-de-uso/cu-05-design.md) | Diseñar una feature: intake (gate), system, feature-prototype; extract (brownfield); validate/a11y/delta/sync/export | producto con UI + frontend real (extract) |
| CU-6 | [`casos-de-uso/cu-06-entrega.md`](casos-de-uso/cu-06-entrega.md) | De spec a entrega: prepare-plan, plan-validate, prepare-tasks, task-run, qa-plan, qa-verify, release | el de CU-3, con stack compilable/testeable |
| CU-7 | [`casos-de-uso/cu-07-cambio-producto.md`](casos-de-uso/cu-07-cambio-producto.md) | Cambio de producto: prd-change, prd-sync-impact, spec-sync-from-prd, prd-change-cascade | el de CU-3 (PRD + specs derivados) |
| CU-8 | [`casos-de-uso/cu-08-mantenimiento.md`](casos-de-uso/cu-08-mantenimiento.md) | Mantenimiento: `wf-bug` (CODE_BUG/SPEC_CHANGE/UNSPEC), `wf-spec-amend` (back-edge) | el de CU-6 (feature entregada) + bug real |
| CU-9 | [`casos-de-uso/cu-09-gates.md`](casos-de-uso/cu-09-gates.md) | Anti-alucinación: los gates **en negativo** (pedir saltarse pasos y comprobar que NO ceden) | cualquiera a mitad de pipeline |
| CU-10 | [`casos-de-uso/cu-10-robustez.md`](casos-de-uso/cu-10-robustez.md) | Robustez/instalación: update con overlay, `--prune`, layout legacy plano, monorepo, sin python3, `wf-project-status` | proyecto SDD instalado + monorepo real |
| CU-11 | [`casos-de-uso/cu-11-enrutado.md`](casos-de-uso/cu-11-enrutado.md) | Enrutado por lenguaje natural: hablar sin teclear `/wf-*`, routing correcto, args que sobreviven saltos wf→wf y wf→agente | cualquiera (transversal) |
| CU-12 | [`casos-de-uso/cu-12-overlay-kmm.md`](casos-de-uso/cu-12-overlay-kmm.md) | Overlay de stack KMM: `wf-kmm-init` (detect/configure) + scaffolding (networking, auth, Room, DataStore, entornos, testing, stack completo) respetando capas | proyecto KMM real |
| CU-13 | [`casos-de-uso/cu-13-enrutado-matriz.md`](casos-de-uso/cu-13-enrutado-matriz.md) | **Matriz de enrutado**: disparador NL → skill correcto, para los 50 workflows + los pares de desambiguación (la trampa real del routing) | cualquiera (transversal) |
| CU-14 | [`casos-de-uso/cu-14-secuenciacion.md`](casos-de-uso/cu-14-secuenciacion.md) | **Secuenciación**: pedir una fase sin su prerequisito → el orquestador te redirige al paso que falta (no fabrica ni corre hacia delante) | proyecto en fase temprana |
| CU-15 | [`casos-de-uso/cu-15-deriva-trazabilidad-recuperacion.md`](casos-de-uso/cu-15-deriva-trazabilidad-recuperacion.md) | **Edge — deriva/trazabilidad/recuperación**: hand-edit y deriva, refs colgantes tras delta/amend, ejecución parcial y reanudación, idempotencia de generadores | proyecto con pipeline avanzado |
| CU-16 | [`casos-de-uso/cu-16-ambiguedad-presion-infra.md`](casos-de-uso/cu-16-ambiguedad-presion-infra.md) | **Edge — ambigüedad/presión/infra**: petición ambigua o multi-feature, presión sostenida sobre gates, editar sello a mano, project-init corrupto, git sucio en release, escala | varios reales |
| CU-17 | [`casos-de-uso/cu-17-meta.md`](casos-de-uso/cu-17-meta.md) | **Meta — autoría del ecosistema**: skill/agent/stack-create (scaffold + gate estructural + duplicados), sdd-audit (lint determinista manda), sdd-refactor (preserva SSoT), sdd-status (inventario read-only) | el **propio repo del ecosistema** `sdd/` |

> [!NOTE]
> **Cobertura.** Los 17 Casos de Uso están redactados en formato CU. Lo que queda es
> **ejecutarlos** sobre proyectos reales y registrar las desviaciones que aparezcan:
> cada FALLO alimenta un ítem del ROADMAP. El catálogo separa dos planos:
> - **Happy-path por fase** (CU-1…8, CU-12): el camino correcto de cada fase.
> - **Robustez en uso real** (transversal): gate mecánico (**CU-9**), routing correcto
>   (**CU-13**), orden de pipeline (**CU-14**), y los edge cases del desorden real —
>   deriva/trazabilidad/recuperación (**CU-15**) y ambigüedad/presión/infra (**CU-16**).
> - **Autoría del ecosistema** (**CU-17**): las skills meta que crean/auditan/mantienen el
>   propio SDD, con su gate estructural determinista.
>
> El cruce skill-por-skill de los CU contra las 48 `wf-*` del core vive en
> [`ROADMAP.md`](ROADMAP.md) (matriz de cobertura por los 4 ejes: happy/edge/harness/args).
>
> CU-9 es el modelo de formato de referencia. En CU-15 hay escenarios-**sonda** (🔎) que
> pueden revelar un hueco real del sistema: ese es justo su valor.

---

## Sobre qué proyectos ejecutar

No hay fixtures sintéticos: cada CU se corre sobre un **proyecto real**. Con un puñado
de proyectos cubres casi todo el catálogo:

1. **Un producto nuevo real** que lleves de PRD → release → cubre **CU-1, 2, 3, 5, 6,
   7, 8, 9, 11**.
2. **Un código heredado real** (backend o app sin specs) → **CU-4** y, si tiene UI,
   **CU-5 (extract)**.
3. **Un monorepo real** (con `.sdd/` en la raíz) → **CU-10.d** (el resto de CU-10 va
   sobre el #1).
4. **Un proyecto KMM real** → **CU-12**.
5. *(opcional)* **un proyecto SDD viejo** en layout plano → **CU-10.c**, o reprodúcelo a
   mano (`features/<n>/<n>_spec.md` sin subcarpeta).

Dos matices sobre el estado de partida: **CU-9** necesita artefactos en un estado
concreto (un plan en `BORRADOR`, un spec con gaps) — se consigue **a mitad del
pipeline** del #1 o editando el artefacto a mano; **CU-1** debe correr **fuera del repo
del ecosistema** (ver aviso abajo).

---

## El formato de un Caso de Uso

Cada fichero `cu-0N-*.md` abre con su objetivo, el **proyecto a usar** y la cobertura
automática, y desglosa los escenarios. Cada escenario:

```markdown
## CU-N.a — <escenario de aceptación>
**Precondición:** estado de partida.
**Mecanismo:** skill / subagente / script / hook implicado.

1. <acción del usuario, en lenguaje natural — NUNCA "ejecuta /wf-x">
   → **Esperado:** <comportamiento del agente · output · artefacto con su path ·
     estado sellado · mensaje literal si aplica>
2. …

**Resultado:** PASS si <…> · FALLO si <…>
**Desviación → reportar:** issue citando `CU-N.a`.
```

- **Acción del usuario** — siempre en lenguaje natural (el routing es parte de lo que
  se verifica; ver CU-11). El bloque **Mecanismo** hace explícito qué skill se invoca,
  qué subagente lo ejecuta y qué script/hook participa.
- **Esperado** — qué hace, **qué NO hace**, el artefacto con su path y el mensaje
  literal cuando aplica.
- **Resultado** — el criterio PASS/FALLO sin ambigüedad.

---

## Relación con el resto

- **`casos-de-uso/`** describe el comportamiento esperado (SSoT) y, con el orden de
  abajo, cumple el rol del **playbook 11.6**: qué ejecutar y en qué secuencia.
- **`sdd/tests/`** (ROADMAP 11.3) automatiza el subconjunto **determinista** (scripts
  de estado, gates, installers, hook de sesión). Cada CU declara en **Cobertura
  automática** qué parte ya cubre la suite; los escenarios manuales son los que
  dependen de la conducta del agente (juicio, anti-alucinación, enrutado).
- **Proyectos reales** son el sustrato donde se ejecutan los casos. Cada CU dice en
  **"Proyecto a usar"** qué buscar y cómo llegar al estado de partida.

> [!NOTE]
> **Autoría y cobertura, asistidas.** El método de derivar escenarios (leer un
> `SKILL.md` → cruzar con los CU → 4 ejes → escribir los huecos en formato verbatim →
> actualizar el ROADMAP) está codificado en `kb-sdd-conformance` y se conduce con dos
> workflows:
> - **`/wf-conformance-author <skill-name|phase>`** — audita la cobertura de una skill
>   (o fase) y **escribe** los escenarios que falten, actualizando la matriz del
>   ROADMAP. Delega en el agente `sdd-conformance`.
> - **`/wf-conformance-status [--phase <fase>]`** — snapshot **read-only** de cobertura
>   (estado por eje y progreso `X/N`) leyendo la matriz del ROADMAP; núcleo determinista
>   `sdd/scripts/sdd-conformance-coverage.py`.

---

## Orden de ejecución sugerido

Sigue el pipeline para que cada CU parta de artefactos que dejó el anterior:

1. **CU-1** — Inicializar (sobre un repo virgen **externo al repo del ecosistema**, ver aviso abajo).
2. **CU-2** — Crear y dejar listo el PRD (producto nuevo real).
3. **CU-3** — Generar las specs del PRD.
4. **CU-4** — (alternativa brownfield) specs desde código existente.
5. **CU-5** — Diseñar una feature.
6. **CU-6** — De spec a entrega (plan → tasks → QA → release).
7. **CU-7** — Cambiar el producto y propagar.
8. **CU-8** — Mantenimiento (bug / enmienda) sobre lo entregado.
9. **CU-9** — Gates en negativo (puede ejecutarse en cualquier momento sobre artefactos
   en el estado adecuado).
10. **CU-10** — Robustez e instalación (proyecto SDD instalado + un monorepo real).
11. **CU-11** — Enrutado por lenguaje natural (transversal: se valida mientras ejecutas
    los demás, hablando en vez de teclear comandos).
12. **CU-12** — Overlay de stack KMM (solo si trabajas un proyecto `stack: kmm`; requiere
    un proyecto KMM real).
13. **CU-13** — Matriz de enrutado (transversal: verifica que cada frase dispara el skill
    correcto; útil como checklist mientras ejecutas los demás).
14. **CU-14** — Secuenciación / pedir fuera de orden (mejor con un proyecto en fase
    temprana: pides una fase adelantada y compruebas que te redirige al paso que falta).
15. **CU-15** — Edge: deriva, trazabilidad y recuperación (sobre un proyecto con pipeline
    avanzado: provocas hand-edits, borrados de CA, fallos parciales e interrupciones).
16. **CU-16** — Edge: ambigüedad, presión e infra degradada (peticiones ambiguas, presión
    sostenida sobre gates, e infra rota a propósito).

> [!NOTE]
> **Cobertura actual y pendiente de futuro.** El catálogo cubre el **pipeline de
> producto** (CU-1…11) más el **overlay de stack KMM** (CU-12). Quedan dos huecos
> **conscientes, que sí queremos testear más adelante** (apuntados en el ROADMAP como
> **11.6b**):
> - **Meta-skills de autoría del ecosistema** (`wf-skill-create`, `wf-agent-create`,
>   `wf-stack-create`, `wf-sdd-audit`, `wf-sdd-refactor`, `wf-sdd-status`): sirven para
>   **construir** el ecosistema, no para usar un proyecto SDD → futuro **CU-13**.
> - **Proyecto KMM de referencia para CU-12**: los escenarios están escritos; falta
>   ejecutarlos sobre un proyecto KMM real.
>
> Otros overlays de stack (no-KMM) se cubrirían con su propio CU cuando existan.

> [!CAUTION]
> **CU-1 no se puede probar dentro del repo del ecosistema.** El hook de sesión se
> silencia en cualquier sesión bajo el git toplevel del propio ecosistema. Para CU-1
> (wizard de modo) usa un **proyecto real en un directorio FUERA del repo** (p. ej.
> `~/sdd-pruebas/…`) y abre Claude Code ahí.

---

## Cómo reportar

Si observas una desviación de un escenario:

1. Reúne lo que dice el escenario (ID `CU-N.x` + su **Esperado**/**Resultado**) y lo
   que realmente pasó (mensaje exacto, artefacto creado o no, estado sellado).
2. Abre una incidencia con la plantilla **"Desviación de comportamiento"**
   (`.github/ISSUE_TEMPLATE/desviacion-comportamiento.md`).

Reportar contra un ID convierte "esto no va bien" en "`CU-9.c` no se cumple en estas
condiciones" — accionable y trazable.
