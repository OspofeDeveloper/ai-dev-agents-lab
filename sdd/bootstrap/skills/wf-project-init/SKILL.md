---
name: wf-project-init
description: "Inicializa o amplia un proyecto SDD a partir de la TOPOLOGIA de contenido del repo: authoring (PRD/specs/sistema de diseño, sin código), consumer (código que consume specs de un repo SSoT), standalone (todo junto) o design (repo SSoT de solo-diseño). El backbone instalado depende de la topología. Genera el CLAUDE.md raiz, registra el estado en .sdd/project-init.json y despacha al init especialista del stack cuando hay código."
when_to_use: "Activa con frases como 'inicializa el proyecto', 'arranca el setup tecnico', 'init del proyecto', 'prepara este proyecto para SDD', 'quiero trabajar specs aqui', 'configura este repo para diseño', 'completa la entrevista tecnica del proyecto'. No activa para crear skills o agentes del ecosistema SDD (usa wf-skill-create, wf-agent-create) ni para ejecutar el init concreto de un stack ya conocido (invoca directamente wf-<stack>-init)."
argument-hint: "[--topology <authoring|consumer|standalone|design>] [--surfaces <mobile,desktop,web,backend,other>] [--design-targets <mobile,mobile-android,web,...>] [--prd] [--design] [--stack <nombre>] [--name <nombre>] [--sdd-path <path>] [--force]"
effort: low
allowed-tools: [Read, Write, Bash, AskUserQuestion]
user-invocable: true
---

# wf-project-init — Onboarding de proyecto SDD

Tu rol es de **onboarding y dispatcher**: detectas el contexto, identificas la **topología de contenido** del repo, entrevistas lo mínimo que esa topología exige, instalas las fases que correspondan y despachas al init especialista del stack cuando el repo lleva código.

**ESTE WORKFLOW ES BLOQUEANTE.** Si el usuario tenía una petición pendiente (una consulta, una tarea), NO la atiendas hasta completar el Paso 9 (verificación) con todos los checks en verde. Un init sin fases instaladas es un init FALLIDO aunque existan los JSON de estado.

**El eje primario es la topología, no el rol de quien inicializa:**

- **`authoring`** — el repo es la **fuente de verdad** del producto: PRD, specs y, si aplica, el sistema de diseño (`DESIGN.md`). Agnóstico de tecnología y de superficie. El código vive en otros repos. **No instala `plan`/`tasks` ni stack.**
- **`consumer`** — el repo es **una superficie** (app móvil, desktop, web o backend) que **consume** los specs de un repo `authoring` (SSoT). Instala `plan`+`tasks` (+ overlay de stack) y, si tiene UI, la capa de diseño de feature. **No autora PRD/spec.**
- **`standalone`** — el repo lo tiene **todo** (proyecto único o monorepo): PRD/specs/diseño + código. Pipeline completo.
- **`design`** *(D-011)* — el repo es **solo diseño**: SSoT del sistema visual (`DESIGN.md`, brief, tokens) **y** de los bundles de feature (flows/views/ui_prompt + overrides per-view por design target), agnóstico de superficie. Instala únicamente la fase `design`, pero con **rol *full*** (necesita **ambos** agentes: `design-system-architect` para el sistema **y** `design-feature-architect` para los bundles de feature). **Sin `prd`/`spec`/`plan`/`tasks`** — los consume de otros repos. Es el repo de diseño dedicado para equipos con diseño propio / varias superficies que comparten un mismo sistema.

**Reglas de la entrevista:**

1. **Toda pregunta usa `AskUserQuestion`** — nunca texto libre. No producir texto antes de la primera pregunta.
2. **No preguntar lo que ya se sabe** — argumentos, `KNOWN_STATE` o artefactos detectados pre-rellenan. Valor conocido → confirmación ("Sí, correcto" / "No, cambiar"); desconocido → pregunta completa.
3. **Opciones exactas** — las escritas aquí. No añadir, quitar ni sustituir.
4. **Backbone variable por topología** — lo que se instala depende del eje primario (SDD es un flujo agnóstico a la tecnología: siempre hay spec→plan→tasks en algún repo, nunca implementación directa, pero esas fases se reparten según la topología):
   - `authoring` → `spec` (+ `prd` si aplica, + `design` rol *system* si aplica). **Sin `plan`/`tasks`.**
   - `consumer` → `plan` + `tasks` (+ `design` rol *feature* si la superficie tiene UI). **Sin `prd`/`spec`** (viven en el SSoT).
   - `standalone` → `spec` + `plan` + `tasks` (+ `prd`/`design` rol *full* según se decida).
   - `design` → solo `design` (rol *full*: sistema + bundles de feature). **Sin `prd`/`spec`/`plan`/`tasks`**: repo SSoT de solo-diseño (D-011).
   La entrevista decide `prd`, `design`, las superficies y cuánta información técnica se captura — nunca el reparto de backbone, que lo fija la topología.
5. **Agrupa preguntas independientes** — las que no se gatean entre sí van en una sola llamada a `AskUserQuestion` (hasta 4 por llamada). Abre una llamada nueva solo cuando una respuesta previa decide si —o qué— se pregunta después. El orden de las llamadas está en el Paso 5.

---

## Paso 1: Parsear argumentos

Los argumentos llegan en `$ARGUMENTS` — tanto si el usuario teclea `/wf-project-init <flags>` como si el orquestador invoca el skill pasándolos en el campo `args` del Skill tool. Pre-rellenan `KNOWN_STATE` (regla 2 de la entrevista): un valor pasado por flag no se vuelve a preguntar, solo se confirma.

- `--topology`: `authoring`, `consumer`, `standalone`, `design`. Omite la pregunta Q1 de contenido.
- `--surfaces`: lista separada por comas de `mobile`, `desktop`, `web`, `backend`, `other`. Omite la pregunta de superficie.
- `--design-targets`: lista separada por comas de design targets (`<familia>[-<plataforma>][-<formfactor>]`, familia ∈ `{mobile,web,desktop}`). Solo topología `design`; omite la pregunta de targets.
- `--prd`: el proyecto usa PRD (omite la pregunta de PRD; ausencia ≠ "no", solo deja la pregunta abierta).
- `--design`: el proyecto tiene diseño (omite la pregunta de diseño).
- `--stack`: nombre del stack. Omite framework/targets.
- `--name`: nombre del proyecto. Default: `basename $PWD`.
- `--sdd-path`: ruta al framework. Default: auto-detección (Paso 2).
- `--force`: rehacer el init sobreescribiendo fases.

---

## Paso 2: Detectar SDD_HOME

`~/.sdd-home` **es un fichero-puntero** (lo escribe `setup.sh`) que contiene la ruta al repo del ecosistema, **no es un directorio**. Resuélvelo leyendo su contenido — no lo uses como path directo, o `$SDD_HOME/install.sh` no existirá. Precedencia: `--sdd-path` → `$SDD_HOME` si ya apunta a un directorio válido → contenido de `~/.sdd-home`:

```bash
if [ -n "$SDD_PATH" ]; then SDD_HOME="$SDD_PATH"
elif [ -d "$SDD_HOME" ] && [ -f "$SDD_HOME/install.sh" ]; then :   # $SDD_HOME ya es válido
elif [ -f "$HOME/.sdd-home" ]; then SDD_HOME="$(cat "$HOME/.sdd-home")"
fi
```

Si `$SDD_HOME/install.sh` no existe tras resolver, abortar:
> "No puedo localizar el framework SDD. Ejecuta `bash setup.sh` desde el repo del ecosistema, o pasa `--sdd-path /ruta/a/sdd`."

---

## Paso 3: Detectar estado previo

**Detección determinista (un solo comando).** Toda la detección de este paso la produce el detector; ejecútalo desde el cwd:

```bash
python3 "$SDD_HOME/scripts/sdd-init-detect.py" detect --json
```

Emite el JSON que puebla `KNOWN_STATE`: `sdd_root` y `sdd_root_is_ancestor` (find-up de un init/modo previo hacia arriba, con techo en el git toplevel — misma lógica que el hook de sesión), `init_found`, `mode_found`, `mode`, `installed_phases` (reconoce también el layout legacy `<fase>/.claude/CLAUDE.md`), `artifact_candidates` (claves spec/prd/design con las carpetas detectadas) y `detected_stack`/`detected_type`/`app_framework` (Paso 4). Si no hay `python3`, usa el **Fallback sin python3** del final de este paso.

**3.0 — Raíz del proyecto en monorepos.** Si `sdd_root_is_ancestor` es `true`, el monorepo ya tiene SDD inicializado en su raíz (`sdd_root`). **NO inicialices anidado.** Pregunta con `AskUserQuestion`:
  - **"Operar desde la raíz `<sdd_root>`"** (recomendado) → detente e indica al usuario: `cd <sdd_root>` y relanza `/wf-project-init` desde ahí.
  - **"Inicializar aquí (subproyecto independiente)"** → continúa el flujo normal en el cwd.

Si `sdd_root_is_ancestor` es `false` (o `sdd_root` es `null`) → continúa relativo al cwd.

**3a. Modo libre.** Si `mode` es `free`, confirmar con AskUserQuestion ("Sí, convertir a SDD" / "No, mantener modo libre"). "No" → cerrar sin tocar nada.

**3b. Init previo.** Si `init_found`, lee `project-init.json`, puebla `KNOWN_STATE` (topology, surfaces, design_role, stack, phases) y muestra resumen compacto. Luego AskUserQuestion:

```
question: "Este proyecto ya está inicializado. ¿Qué quieres hacer?"
header: "Init previo"
opciones:
  - label: "Completar / ampliar"
    description: "Mantiene lo instalado, añade fases o información que falte (incluida la entrevista técnica pendiente)"
  - label: "Rehacer desde cero"
    description: "Re-entrevista completa y reinstalación (equivale a --force)"
  - label: "Dejar como está"
    description: "Cierra sin cambios"
```

`MODE=extend` mantiene lo instalado y solo pregunta lo que falte. Si hay `--force` como argumento, rehacer sin preguntar.

> **Reparación de fase declarada pero no instalada (extend).** No la pongas en cuestión ni preguntes el rol: `phases` es el contrato (el mismo campo con el que el hook declara `init-incomplete`). Ejecuta `python3 "$SDD_HOME/scripts/sdd-init-detect.py" repair-plan` y **aplica su plan**: instala `missing_phases` y fija `design_role`/`artifacts` según `expected_design_role` — derivado de la topología por el script (SSoT en código, testeado), **sin** `AskUserQuestion`. Quitar una fase declarada **no** es reparación: es un cambio explícito de alcance. Informa post-hoc de lo instalado (p. ej. "instalé `design` rol system porque estaba declarado; quítalo con 'Completar / ampliar' si no lo querías").

> **Esquema nuevo (sin retrocompatibilidad).** Un `project-init.json` con el esquema legacy (`profiles`/`profile`/`type` en vez de `topology`/`surfaces`) **no es válido**: trátalo como init corrupto y ofrece "Rehacer desde cero". No migres campos legacy.

**3c. Artefactos.** Refinar `KNOWN_STATE`: `prd/PRD.md` → `use_prd=true`; `design/DESIGN.md` o `DESIGN_BRIEF.md` → `has_design=true`; specs existentes (`spec/features/` o specs detectados en otra ruta) → `specs_exist=true` (anotar la ruta real si no es la canónica).

**3d. Carpetas candidatas de artefactos.** Las trae `artifact_candidates` del detector (claves `spec`/`prd`/`design`). Si no está vacío, alimentan la pregunta 5.6 (solo se pregunta si hay candidatas).

**Fallback sin python3.** Si no hay `python3`, reproduce la detección con estos comandos:

```bash
# find-up (sdd_root / sdd_root_is_ancestor)
TOP="$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "$TOP" ]; then CEIL="$(cd "$TOP" && pwd -P)"; else CEIL="$(pwd -P)"; fi
d="$(pwd -P)"; SDD_ROOT_FOUND=""
while :; do
  if [ -f "$d/.sdd/project-init.json" ] || [ -f "$d/.claude/sdd-mode.json" ]; then SDD_ROOT_FOUND="$d"; break; fi
  [ "$d" = "$CEIL" ] && break; [ "$d" = "/" ] && break; d="$(dirname "$d")"
done
echo "cwd:$(pwd -P)"; echo "sdd-root:${SDD_ROOT_FOUND:-ninguno}"
# init_found / mode_found / installed_phases (incluye layout legacy)
test -f .sdd/project-init.json && echo "init-found"
test -f .claude/sdd-mode.json && echo "mode-found"
for f in prd spec design plan tasks; do
  test -f ".claude/rules/sdd-$f.md" -o -f "$f/.claude/CLAUDE.md" && echo "phase-installed:$f"
done
# artifact_candidates
for d in specs docs/specs documentation/specs; do test -d "$d" && echo "candidate:spec:$d"; done
for d in docs/prd product docs/product requirements; do test -d "$d" && echo "candidate:prd:$d"; done
for d in docs/design design-system; do test -d "$d" && echo "candidate:design:$d"; done
```

---

## Paso 4: Analizar el proyecto en silencio (hint de stack/superficie)

El detector del Paso 3 ya devolvió `detected_stack`, `detected_type` y `app_framework`. Son **pistas**, no decisiones: la superficie y el stack los confirma/decide la entrevista. Tabla de mapeo (referencia; fallback bash al final):

| Condición | DETECTED_STACK (superficie implícita) |
|---|---|
| `gradle-found` + (`iosApp-found` o `composeApp-found`) | `kmm` (mobile) |
| `flutter-found` | `flutter` (mobile) |
| `android-build-found` sin `iosApp-found` | `android` (mobile) |
| `next-found` / `vite-react-found` / `astro-found` | `next` / `vite-react` / `astro` (web) |
| `ktor-found` / `express-found` / `fastapi-found` | `ktor` / `node-express` / `fastapi` (backend) |
| Ninguna | sin detección |

Con detección: usa `detected_type` como superficie pre-rellenada (mobile/web/backend) y `app_framework` para confirmar el framework móvil (`kmm`→`compose_multiplatform`, etc.).

**Fallback sin python3:**

```bash
test -f gradle/libs.versions.toml && echo "gradle-found"
test -d iosApp && echo "iosApp-found"
test -d composeApp && echo "composeApp-found"
test -f pubspec.yaml && grep -q "flutter:" pubspec.yaml && echo "flutter-found"
test -f app/build.gradle.kts && echo "android-build-found"
test -f package.json && grep -q '"next"' package.json && echo "next-found"
test -f package.json && grep -q '"vite"' package.json && grep -q '"react"' package.json && echo "vite-react-found"
test -f astro.config.mjs -o -f astro.config.ts && echo "astro-found"
test -f build.gradle.kts && grep -q "ktor" build.gradle.kts && echo "ktor-found"
test -f package.json && grep -q '"express"' package.json && echo "express-found"
test -f pyproject.toml && grep -q "fastapi" pyproject.toml && echo "fastapi-found"
test -f requirements.txt && grep -qi "fastapi" requirements.txt && echo "fastapi-found"
```

---

## Paso 5: Entrevista

Las preguntas que no se gatean entre sí se agrupan en una misma llamada a `AskUserQuestion` (regla 5). De cada grupo, pregunta solo lo que siga abierto tras `KNOWN_STATE` (regla 2); si un grupo se queda sin preguntas abiertas, se omite entero. Orden de las llamadas:

```
Llamada 1 — incondicional: Q1 Contenido (gatea toda la rama)
Rama según Q1:
  authoring   → ¿PRD? + ¿Sistema visual?
  consumer    → path al SSoT + Superficie (gatea técnica)  → Framework/Targets si móvil
  standalone  → ¿PRD? + ¿Diseño? + Superficie(s)           → Framework/Targets si móvil
Siempre al final: Resumen y confirmación
```

> **El init NO pregunta el rigor del pipeline (standard/ligero).** `pipeline_mode` arranca en `standard` por defecto. El modo es una elección **deliberada por feature** que se ofrece al crear el spec (ver `pipeline/spec/CLAUDE.md`), no un default normalizable a nivel proyecto — fijarlo a ciegas en t=0, sin features delante, normalizaría specs finos por inercia. Un equipo que de verdad sea ligero-por-defecto puede editar `pipeline_mode` a mano en `.sdd/project-init.json`.

### 5.0 — Q1 Contenido del repositorio [siempre, salvo `--topology`]

```
question: "¿Qué va a contener este repositorio?"
header: "Contenido"
opciones:
  - label: "Producto (specs + PRD/diseño opcionales)"
    description: "Specs son el núcleo (la fuente de verdad agnóstica del producto). PRD y sistema de diseño son opcionales y se deciden a continuación. El código vive en otros repos; no se configura stack aquí"
  - label: "Desarrollo (consume specs)"
    description: "El código de una superficie (app, web, desktop, backend) que consume los specs de un repo de Producto. Instala plan y tasks (+ stack), y diseño de feature si tiene UI"
  - label: "Autónomo (todo aquí)"
    description: "Specs y código juntos: proyecto único o monorepo. Pipeline completo de spec a tasks. Para el caso mínimo, di luego que no a PRD y a diseño"
  - label: "Diseño (repo de solo-diseño)"
    description: "Repo SSoT de solo diseño: sistema visual (DESIGN.md, brief, tokens) Y los bundles de feature (flows/views/ui_prompt) por design target, agnóstico de superficie. No instala PRD/spec/plan/tasks ni stack. A continuación declaras los design targets que cubre"
```
> **Q1 está ahora en el tope de 4 opciones** de `AskUserQuestion` (sin "Other"): no cabe una 5ª topología sin rediseñar la pregunta (D-011).

`TOPOLOGY = authoring | consumer | standalone | design`.

`PIPELINE_MODE = standard` (fijo; el init no lo pregunta — ver la nota de arriba). La elección standard/ligero se ofrece por feature al crear el spec.

---

### Rama AUTHORING

Llamada 2 — dos preguntas independientes:

**5.A1 — PRD:**
```
question: "¿Este producto va a usar un PRD?"
header: "PRD"
opciones:
  - label: "Sí, con PRD"
    description: "Se instala prd/ con sus skills"
  - label: "No, solo specs"
    description: "El pipeline arranca en spec/ desde tus documentos de requisitos"
```

**5.A2 — Sistema visual:**
```
question: "¿Este producto va a tener sistema de diseño (DESIGN.md)?"
header: "Diseño"
opciones:
  - label: "Sí, sistema visual"
    description: "Se instala design (rol system): brief, DESIGN.md y tokens. Las superficies derivan sus flows/views en sus repos"
  - label: "No"
    description: "Sin diseño aquí; cada superficie que lo necesite lo añade en su repo, o el diseño vive en un repo de diseño dedicado (topología Diseño)"
```

> **Un solo SSoT de diseño por producto (D-012).** Responde **No** si el diseño vivirá en un repo de diseño dedicado (topología **Diseño**): no actives el sistema aquí **y además** montes un repo `design` para el mismo producto — serían dos `DESIGN.md` compitiendo. El sistema co-localizado (**Sí**) es para cuando el diseño vive **en este repo**.

Authoring **no** pregunta superficie, framework ni stack: es agnóstico. `STACK = agnostico`, `surfaces = []`, `has_ui = false`. `design_role = system` si hay sistema visual, si no `null`.

---

### Rama CONSUMER

**5.C0 — Path al repo SSoT** (texto libre vía opción "Other" de AskUserQuestion, o pregúntalo directamente si el usuario ya lo dio): path local al checkout del repo `authoring` (sibling `../<repo>` o submodule). Validar: el path existe y contiene specs (`features/` o `*_features.md`, buscando también bajo `artifacts.spec` de SU `project-init.json` si lo tiene). Si no valida → re-preguntar o detener con instrucciones de clonarlo. Guardar `ARTIFACTS_SOURCE = <path>` y `ARTIFACTS_SOURCE_PIN = git -C <path> rev-parse --short HEAD` (o `unknown`).

**5.C1 — Superficie** (en la misma llamada que el path no, porque el path se valida antes):
```
question: "¿Qué superficie implementa este repo?"
header: "Superficie"
opciones:
  - label: "App móvil"
    description: "Android, iOS o multiplataforma. Tiene UI: se instala la capa de diseño de feature"
  - label: "App desktop"
    description: "App de escritorio. Tiene UI: se instala la capa de diseño de feature"
  - label: "Web"
    description: "Aplicación web. Tiene UI: se instala la capa de diseño de feature"
  - label: "Backend (servicio/API)"
    description: "Sin UI: pasa de Spec directamente a Plan. No se instala diseño"
```

`surfaces = [<una>]`. `has_ui = surface ∈ {mobile, desktop, web}`. Si `has_ui` es falso (backend): `design_role = null`, sin diseño, salta 5.C1b.

**5.C1b — Dónde vive el diseño** [solo si `has_ui`]:
```
question: "¿Dónde vive el sistema de diseño (DESIGN.md y los flows/views) de este producto?"
header: "Diseño"
opciones:
  - label: "En el mismo repo de specs (SSoT)"
    description: "El DESIGN.md vive junto a los specs en el repo SSoT; este repo autora aquí sus flows/views de feature leyendo ese DESIGN.md (rol feature). Comportamiento de siempre"
  - label: "En un repo de diseño aparte"
    description: "Hay un repo de diseño dedicado (topología design, D-011); este repo NO autora flows/views: los resuelve (base ⊕ override por su target) desde ese repo en solo lectura"
```
- **SSoT de specs** (caso de siempre): `design_role = feature`, se instala la fase `design` (autoría de feature); los flows/views se autoran aquí leyendo el `DESIGN.md` del SSoT.
- **Repo de diseño aparte** (D-011): `design_role = null`, **NO se instala la fase `design`** aquí (el diseño se resuelve del repo `design` en solo lectura). Captura:
  - `DESIGN_SOURCE` = path local al checkout del repo `design` (validar como 5.C0: existe y contiene `DESIGN.md` o `features/`); `DESIGN_SOURCE_PIN = git -C <design_source> rev-parse --short HEAD` (o `unknown`).
  - `DESIGN_TARGETS` = los design target(s) que este repo consume (multiSelect, mismas opciones que 5.D1; validar con `sdd-init-detect.py target-platforms`). P. ej. un repo Android-nativo consume `mobile-android`.
  - **Guard de SSoT único de diseño (D-012):** comprueba que el repo SSoT de specs (`ARTIFACTS_SOURCE`) **no** traiga además diseño co-localizado — lee `<ARTIFACTS_SOURCE>/.sdd/project-init.json`: si declara la fase `design` (o `design_role` ∈ {system, full}), **avisa** (no bloquea): «el repo de specs ya trae un `DESIGN.md` co-localizado y vas a apuntar a un repo de diseño aparte → dos SSoT de diseño para el mismo producto; gana `design_source` y el co-localizado quedará ignorado. Confirma que es intencional (p. ej. ventana de migración)». Una vez escrito el `project-init.json`, este conflicto lo reporta de forma determinista `sdd-source-drift.py check` (`design_ssot.dual_design_ssot`).

**5.C2 — Framework/Targets** [solo si superficie móvil] → ver 5.X abajo. Para web/backend, derivar stack de la detección (Paso 4) o `agnostico`.

---

### Rama STANDALONE

Llamada 2 — preguntas independientes (PRD, Diseño, Superficies):

**5.S1 — PRD:** idéntica a 5.A1.

**5.S2 — Diseño:**
```
question: "¿Este proyecto va a tener diseño?"
header: "Diseño"
opciones:
  - label: "Sí, sistema + features"
    description: "Se instala design completo (rol full): DESIGN.md + flows/views/ui_prompt por feature"
  - label: "No"
    description: "El pipeline irá de Spec directamente a Plan"
```
`design_role = full` si sí; si no `null`.

**5.S3 — Superficie(s)** [multiSelect]:
```
question: "¿Qué superficie(s) cubre este repo?"
header: "Superficies"
multiSelect: true
opciones:                                  # EXACTAMENTE 4 — ver nota abajo
  - label: "App móvil"   (Android/iOS/multiplataforma)
  - label: "App desktop"
  - label: "Web"
  - label: "Backend (servicio/API)"
```
> **No añadas "Otro" como quinta opción.** `AskUserQuestion` admite **máximo 4 opciones** y provee el slot **"Other"** automáticamente (texto libre). El caso librería/CLI/tooling/módulo entra por ese "Other": cualquier respuesta vía "Other" (sea "librería", "Módulo BLE", etc.) se mapea a `surfaces = [other]` (headless, sin UI). El enunciado puede recordarlo: "…si es librería/CLI/tooling/módulo, usa 'Other'".

`surfaces = [...]` (los labels elegidos → `mobile|desktop|web|backend`; cualquier valor por "Other" → `other`). `has_ui = surfaces ∩ {mobile, desktop, web} ≠ ∅`. **Caso mínimo**: PRD=no + Diseño=no + `surfaces = [other]` → `STACK = agnostico`, solo backbone `spec`/`plan`/`tasks`.

**5.S4 — Framework/Targets** [solo si `surfaces` incluye móvil] → ver 5.X.

> **Deuda multi-superficie (single-repo).** Si `surfaces` tiene más de una superficie con stack distinto (p. ej. móvil + backend), hoy solo se aplica **un** overlay de stack. Elige la superficie primaria para el stack ahora y avisa al usuario: las demás se completan después con "Completar / ampliar" (un overlay por pasada).

---

### Rama DESIGN *(D-011)*

El repo `design` no tiene superficie ni stack: es agnóstico y autora **solo** diseño, pero **ambos niveles** (sistema + bundles de feature). `STACK = agnostico`, `surfaces = []`, `has_ui = false`, `design_role = full`. No pregunta PRD ni superficie.

**5.D1 — Design targets que cubre** [multiSelect; omitida si llegó `--design-targets`]:
```
question: "¿Qué design targets cubre este repo de diseño?"
header: "Design targets"
multiSelect: true
opciones:                                  # EXACTAMENTE 4 — el resto, vía "Other"
  - label: "mobile"            (una sola base móvil; Android e iOS comparten diseño)
  - label: "mobile-android"    (Material; diverge de iOS a nivel de componente/vista)
  - label: "mobile-ios"        (HIG; diverge de Android)
  - label: "web"
```
> **No añadas "Otro" como quinta opción.** Para `desktop`, `mobile-tablet`, `desktop-windows`, etc., usa el slot **"Other"** (texto libre). Convención validada: `<familia>[-<plataforma>][-<formfactor>]`, **familia obligatoria** ∈ `{mobile,web,desktop}` (`tablet`/`phone` son form-factor, no familia).

**Validar y derivar `target_platforms` con el subcomando determinista** (no a mano — es la función foundational de 12.0):
```bash
python3 "$SDD_HOME/scripts/sdd-init-detect.py" target-platforms --targets "<t1,t2,...>" --json
```
Si `all_valid` es `false`, muestra los `invalid` al usuario y **re-pregunta** (familia inválida o patrón roto); no continúes con targets inválidos. Con `all_valid: true`, guarda `DESIGN_TARGETS = <lista>` y `TARGET_PLATFORMS = .target_platforms` (familias derivadas, p. ej. `[mobile-android, mobile-ios, desktop] → [mobile, desktop]`).

---

### 5.X — Framework y Targets [solo si hay superficie móvil y no llegó `--stack`]

```
question: "¿Qué tipo de app móvil vas a hacer?"
header: "Framework"
opciones:
  - label: "Android (Nativa)"
    description: "Jetpack Compose, Kotlin — solo Android"
  - label: "iOS (Nativa)"
    description: "SwiftUI, Swift — solo iOS"
  - label: "Compose Multiplatform (Multiplataforma)"
    description: "Kotlin Multiplatform + Compose — Android, iOS, Desktop"
  - label: "Flutter (Multiplataforma)"
    description: "Dart + Flutter — Android, iOS, Desktop"
```
Mapeo: `android` / `ios` / `compose_multiplatform` / `flutter`.

**Targets** [solo `compose_multiplatform` o `flutter`]:
```
question: "¿Qué targets va a soportar?"
header: "Targets"
multiSelect: true
opciones: [Android, iOS, Desktop]
```
Mínimo uno. Guardar en minúscula.

### 5.6 — Ubicación de artefactos [solo si `artifact_candidates` no vacío y hay fase con artefactos]

El layout por defecto es el canónico (`prd/`, `spec/`, `design/`). Si el proyecto ya tiene carpetas propias (3d), preguntar **una vez por fase con candidata**:

```
question: "He detectado la carpeta `<candidata>`. ¿Dónde deben vivir los artefactos de la fase <fase>?"
header: "Artefactos"
opciones:
  - label: "Usar <candidata>"
    description: "Los artefactos de <fase> se crearán bajo <candidata>/"
  - label: "Usar la canónica (<fase>/)"
    description: "Layout estándar del pipeline SDD"
```

Resultado → `ARTIFACTS_MAP`. En `consumer` no aplica (no autora prd/spec/design).

### 5.7 — Derivar STACK (sin preguntar)

| Caso | STACK |
|---|---|
| `--stack` pasado | ese valor (precedencia total) |
| `TOPOLOGY == authoring` | `agnostico` (no hay código aquí) |
| `surfaces` solo `other` | `agnostico` |
| Superficie móvil (con framework elegido) | `android`/`ios`/`kmm`/`flutter` |
| Superficie web/backend | `DETECTED_STACK` si hubo detección; si no, `agnostico` |
| Multi-superficie standalone | el de la superficie primaria (deuda: un overlay) |

### 5.8 — Resumen y confirmación [siempre]

```
Configuración del proyecto
──────────────────────────────────────────────────
Contenido:  <Producto (authoring) / Desarrollo (consumer) / Autónomo (standalone)>
Superficie: <mobile, web, ...>                       [no en authoring]
SSoT:       <path al repo de specs>                  [solo consumer]
Fases:      <prd → spec → design → plan → tasks>     (según topología)
Diseño:     <sistema / feature / completo / sin diseño>
Stack:      <stack / agnóstico>
Targets:    <android, ios, desktop>                  [solo multiplataforma]
Pipeline:   standard (default; el modo se elige por feature al crear el spec)
Modo:       <instalación nueva / ampliación>
──────────────────────────────────────────────────
```

Confirmar con AskUserQuestion ("Instalar" / "Cambiar algo" → vuelve a 5.0).

---

## Paso 6: Derivar fases e instalar

```
TOPOLOGY == authoring:
  SELECTED_PHASES = [spec]
  use_prd == true     → anteponer prd
  has_design == true  → insertar design (rol system) tras spec
  (sin plan/tasks, sin overlay de stack)

TOPOLOGY == consumer:
  SELECTED_PHASES = [plan, tasks]
  has_ui == true Y diseño co-localizado (SSoT de specs) → anteponer design (rol feature)
  has_ui == true Y diseño en repo aparte (design_source) → NO se instala design (se resuelve del repo design, solo lectura)
  (sin prd/spec; la autoría vive en el SSoT)

TOPOLOGY == standalone:
  SELECTED_PHASES = [spec, plan, tasks]
  use_prd == true     → anteponer prd
  has_design == true  → insertar design (rol full) tras spec

TOPOLOGY == design:
  SELECTED_PHASES = [design]   (rol full: sistema + bundles de feature; sin prd/spec/plan/tasks)
```

Orden canónico: `prd → spec → design → plan → tasks` (solo las presentes).

Instalación única **desde la raíz del proyecto**. Pasa siempre `--no-claude-md` (este skill autora el `CLAUDE.md` raíz en el Paso 7; sin el flag, `install.sh` lo sembraría y tu `Write` chocaría con un fichero pre-existente no leído). Cuando `design` está en las fases, añade `--design-role`:

```bash
DESIGN_ROLE=<system|feature|full>   # según design_role; omitir el flag si no hay design
bash "$SDD_HOME/install.sh" <fase1,fase2,...> --no-claude-md ${DESIGN_ROLE:+--design-role=$DESIGN_ROLE}
```

En `MODE=extend`, pasar solo las fases que falten. Con `--force`, pasar todas.

Crear los directorios de artefactos según `ARTIFACTS_MAP` (5.6):

```bash
mkdir -p <artifacts.prd> <artifacts.design>          # solo las fases instaladas
mkdir -p <artifacts.spec>/features                   # solo si se instala spec (authoring/standalone)
```

En `consumer` no hay `ARTIFACTS_MAP`: crear solo `mkdir -p features` (ahí vivirán las subcarpetas `design/` (si UI), `plan/` y `tasks/` de cada feature, con `Spec origen` apuntando al checkout del SSoT).

En `design` (D-011): `mkdir -p <artifacts.design> features` — el sistema visual (`DESIGN.md`/brief/tokens) vive en `<artifacts.design>/`; los bundles por feature (flows/views/ui_prompt base + overrides por target) en `features/<nombre>/design/`.

**Ajustar los globs de las reglas al layout del proyecto**: si algún directorio de `ARTIFACTS_MAP` difiere del canónico, edita el frontmatter `paths:` de la regla correspondiente (`.claude/rules/sdd-prd.md`, `sdd-spec.md`, `sdd-design.md`) sustituyendo el glob del directorio canónico por el real. Los globs por nombre de artefacto no se tocan.

No continuar al Paso 7 sin haber ejecutado el install con TODAS las fases seleccionadas.

---

## Paso 7: Generar CLAUDE.md raíz

**No copiar `$SDD_HOME/CLAUDE.md`.** En el Paso 6 instalaste con `--no-claude-md`, así que en una instalación nueva **no existe** `.claude/CLAUDE.md` todavía y tu `Write` lo crea limpio. En un reinit (`--force` / "Rehacer desde cero") el fichero ya existe: **léelo primero con Read** antes del `Write` (el harness exige leer un fichero antes de sobreescribirlo). Generar `.claude/CLAUDE.md` con esta plantilla (solo filas de fases instaladas):

```markdown
# <nombre-proyecto> — Proyecto SDD

Proyecto gestionado con Spec Driven Development. Topología: **<authoring|consumer|standalone|design>**. Fases instaladas: <lista en orden>.

## Cómo operar

- Toda la infraestructura (skills, agentes, reglas) vive en este `.claude/`. Las instrucciones de cada fase son reglas de carga perezosa (`.claude/rules/sdd-<fase>.md`): el harness las carga al tocar los artefactos de esa fase. No improvises workflows.
- Respeta el orden del pipeline: una fase consume artefactos de la anterior.
- Modo de pipeline por defecto: **standard** (`pipeline_mode` de `.sdd/project-init.json`). El rigor (standard/ligero) se decide **por feature** al crear el spec — no es un default de proyecto. Para forzarlo en una feature concreta: `--light`/`--standard`. Para cambiar el default del proyecto entero: edita `pipeline_mode` a mano.
- Estado del proyecto: `.sdd/project-init.json`. Para completar la entrevista técnica o añadir fases: `/wf-project-init` → "Completar / ampliar".

## Layout de artefactos

[Variante según topología — ver abajo]

## Fases y sus reglas

| Fase | Regla (se carga sola al tocar sus artefactos) |
|---|---|
| PRD | `.claude/rules/sdd-prd.md` |
| Spec | `.claude/rules/sdd-spec.md` |
| Design | `.claude/rules/sdd-design.md` |
| Plan | `.claude/rules/sdd-plan.md` |
| Tasks | `.claude/rules/sdd-tasks.md` |

(Solo filas de fases instaladas. Si hay stack especialista, añadir `| Stack <stack> | .claude/rules/sdd-<stack>.md |`.)

## Política de git

- Se commitea TODO `.claude/` y TODO `.sdd/`: el repo funciona para cualquier dev y en CI sin tener el ecosistema SDD instalado.
- Excepción única: `.claude/settings.local.json` (en `.gitignore`).
- Los artefactos SDD (PRD, `features/`, design) se commitean siempre.

### Trabajo en paralelo: una feature por rama

- **Una feature = una rama.** Cada feature vive en su carpeta `features/<nombre>/`.
- **`_features.md` es un índice GENERADO** (`python3 .sdd/scripts/sdd-features-index.py <raíz_spec>`), no se edita a mano.
- El registro de inits de stack es el log append-only `.sdd/stack-runs.jsonl`.
```

**Variantes de "Layout de artefactos" según topología:**

- **authoring / standalone** — tabla canónica:
  ```markdown
  Los artefactos de cada fase viven en el directorio declarado en `artifacts` de `.sdd/project-init.json`:

  | Fase | Directorio | Qué contiene |
  |---|---|---|
  | PRD | `<artifacts.prd>/` | `prd.md`, `*_analysis.md`, `*_discovery.md` |
  | Spec | `<artifacts.spec>/` | `_features.md`, `features/<nombre>/` |
  | Design | `<artifacts.design>/` | `DESIGN_BRIEF.md`, `DESIGN.md`, `tokens/` |

  Cada feature organiza sus artefactos en subcarpetas por fase (`spec/`, `design/`, `plan/`, `tasks/`), con su `README.md` en la raíz. En authoring solo existen las fases de autoría (sin `plan/`/`tasks/`).
  ```
  En **authoring** añadir: "Este repo es la **fuente de verdad** del producto: autora PRD/specs/`DESIGN.md` agnósticos. El código y la planificación viven en los repos de superficie (consumer), que leen estos artefactos."

- **consumer** — sustituir "Layout de artefactos" por:
  ```markdown
  ## Topología: repo consumidor

  Los PRD/specs/`DESIGN.md` de este producto viven en el repo SSoT: `<artifacts_source>` (checkout local). Este repo solo PLANIFICA y EJECUTA su superficie (`<surface>`):

  - Specs y `DESIGN.md` (solo lectura): bajo `<artifacts_source>/.../features/<nombre>/`.
  - Diseño de feature: **(a)** si el diseño es co-localizado en el SSoT (`design_role: feature`), se autora en ESTE repo en `features/<nombre>/design/` leyendo el `DESIGN.md` del SSoT; **(b)** si hay repo de diseño aparte (`design_source`), NO se autora aquí — los flows/views se **resuelven en solo lectura** desde `<design_source>` (`base ⊕ override` por los `design_targets` de este repo, vía `.sdd/scripts/sdd-design-resolve.py`).
  - Planes y tasks (de este repo): `features/<nombre>/plan/` y `features/<nombre>/tasks/`, con `Spec origen` apuntando al checkout del SSoT.
  - Cambios de spec o de sistema visual → se piden en el repo SSoT (o en el repo `design` si aplica), nunca se editan aquí.
  - Pins: `artifacts_source_pin` (specs) y, si hay repo de diseño aparte, `design_source_pin` (diseño) en `.sdd/project-init.json` — si la fuente avanza, los workflows de plan avisan.
  ```

- **design** *(D-011)* — sustituir "Layout de artefactos" por:
  ```markdown
  ## Topología: repo de diseño (SSoT visual)

  Este repo es la fuente de verdad del **diseño** del producto, agnóstico de superficie. No tiene PRD/spec/plan/tasks: los consume de otros repos.

  - Sistema visual (`design-system-architect`): `<artifacts.design>/` — `DESIGN_BRIEF.md`, `DESIGN.md`, `tokens/`.
  - Bundles por feature (`design-feature-architect`): `features/<nombre>/design/` — flows/views/ui_prompt base agnóstica + overrides **por design target** (solo donde diverge).
  - Design targets que cubre: `design_targets` de `.sdd/project-init.json`; `target_platforms` (familias `{mobile,web,desktop}`) se deriva de ellos.
  - Los repos de superficie (consumer) consumen este diseño en **solo lectura** (resuelven `base ⊕ override` por su target).
  ```

**`.gitignore` del proyecto**: asegura la línea `.claude/settings.local.json` (créalo si no existe; no toques el resto).

---

## Paso 8: Registrar estado y despachar

1. `mkdir -p .sdd`. Timestamp real: `date -u +%Y-%m-%dT%H:%M:%SZ` y usar SU SALIDA.
2. **Resuelve `sdd_version` ANTES de escribir** (no escribas un placeholder `unknown` para corregirlo luego con un segundo `Edit`/`Update` — eso choca con la regla de "leer antes de editar" del harness). Léelo de `.sdd/sdd-version.json` (lo dejó `install.sh` en el Paso 6):
   ```bash
   SDD_VER=$(python3 -c "import json;d=json.load(open('.sdd/sdd-version.json'));print(f\"{d['version']}+{d['commit']}\")" 2>/dev/null || echo unknown)
   ```
3. Escribir `.sdd/project-init.json` **en una sola operación** (vía Bash heredoc o Write sobre fichero nuevo), con el `sdd_version` ya resuelto y **EXACTAMENTE estos campos**:

```json
{
  "name": "<nombre-proyecto>",
  "topology": "<authoring|consumer|standalone|design>",
  "surfaces": ["<mobile|desktop|web|backend|other>", "..."],
  "has_ui": <true|false>,
  "design_role": "<system|feature|full|null>",
  "stack": "<stack|agnostico>",
  "targets": ["..."],
  "phases": ["<fases en orden canónico>"],
  "artifacts": { "prd": "<dir>", "spec": "<dir>", "design": "<dir>" },
  "pipeline_mode": "standard",
  "sdd_version": "<version+commit del sello>",
  "initialized_at": "<salida de date -u>",
  "dispatcher": "wf-project-init",
  "specialist_workflow": "<wf-<stack>-init | null>"
}
```

Reglas de los campos:
- `surfaces`: `[]` en authoring y en `design`. `has_ui`: derivado (`surfaces ∩ {mobile,desktop,web} ≠ ∅`); `false` en `design`.
- `design_role`: `system` (authoring con diseño: solo el sistema, los consumers derivan flows/views en sus repos), `feature` (consumer con UI), `full` (standalone con diseño **o topología `design`**: ambos agentes — sistema + bundles de feature), `null` (sin diseño).
- `targets`: solo si multiplataforma; en otro caso omitir la clave.
- **En topología `design` (D-011)** se añaden dos claves (omitidas en las demás topologías): `design_targets` (lista de etiquetas validadas `<familia>[-plataforma][-formfactor]`) y `target_platforms` (familias `{mobile,web,desktop}` **derivadas** de ellas vía el subcomando `target-platforms`, no a mano). `phases` = `["design"]`; `artifacts` lleva solo la clave `design`.
- `artifacts`: una clave por fase de autoría instalada (`prd`/`spec`/`design`), relativa a la raíz. **En `consumer` se sustituye `artifacts` por**:
  ```json
  "artifacts_source": "<path local al checkout del repo SSoT>",
  "artifacts_source_pin": "<commit corto del SSoT al hacer el init | unknown>"
  ```
  (en consumer `phases` no incluye prd/spec; el `design` de consumer es rol feature y sus artefactos viven dentro de cada feature.)
- **Consumer con diseño en repo aparte (D-011, 5.C1b)**: además de `artifacts_source`, añade `design_source` + `design_source_pin` (checkout del repo `design`) y `design_targets` (los que este repo consume). En ese caso `phases` **no** incluye `design` y `design_role` es `null` (no se autora diseño aquí; se resuelve del repo `design` en solo lectura con `sdd-design-resolve.py`).
  ```json
  "design_source": "<path local al checkout del repo design>",
  "design_source_pin": "<commit corto del repo design al init | unknown>",
  "design_targets": ["<design target(s) que consume este repo>"]
  ```
- `specialist_workflow`: solo si el stack es concreto Y existe `wf-<stack>-init`.
- `pipeline_mode`: **siempre `standard`** en el init (no se pregunta). El rigor por feature se decide al crear el spec; el override de proyecto es editar este campo a mano.
- `sdd_version`: de `.sdd/sdd-version.json` (lo escribe `install.sh`): `<version>+<commit>`. Si no existe, `unknown`.

> El registro de ejecuciones del init de stack vive en `.sdd/stack-runs.jsonl` (append-only), no aquí. `project-init.json` queda como config estable.

> **`topology` no se acumula** (a diferencia del antiguo `profiles`): un repo es lo que es. La evolución legítima es authoring→standalone (se le añade código) vía "Completar / ampliar", que **reescribe** `topology` y recalcula fases. No se mantiene historial de topologías.

4. Escribir `.claude/sdd-mode.json`:

```json
{ "mode": "sdd", "decided_at": "<salida de date -u>", "decided_by": "wf-project-init" }
```

5. **Solo si** `specialist_workflow` no es null → invocar `wf-<stack>-init` **via Skill tool** (nunca `tech/<stack>/install.sh` a mano).

---

## Paso 9: VERIFICACIÓN OBLIGATORIA

Ejecuta el verificador con las fases instaladas. Si algún check falla, corrígelo (típicamente re-ejecutar `install.sh <fase>`) y re-verifica ANTES de dar el init por terminado:

```bash
python3 "$SDD_HOME/scripts/sdd-init-detect.py" verify --phases <fase1,fase2,...> --json
```

> `--phases` espera **un solo argumento separado por comas, sin espacios** (p. ej. `--phases prd,spec,design`). No las pases separadas por espacios (`--phases prd spec design`) — argparse las tomaría como posicionales y abortaría con `unrecognized arguments`.

Emite un check por entrada cubriendo: reglas `.claude/rules/sdd-<fase>.md` de cada fase, `.claude/CLAUDE.md`, `.sdd/project-init.json` + esquema (`dispatcher`, `topology`), mapa de artefactos (`artifacts` en authoring/standalone o `artifacts_source` en consumer), scripts de enforcement en `.sdd/scripts/`, `.sdd/sdd-version.json` y la línea `.claude/settings.local.json` en `.gitignore`. **Exit 2** = al menos un check en FALLO; **exit 0** = todo OK.

**Fallback sin python3:**

```bash
for f in <SELECTED_PHASES>; do
  test -f ".claude/rules/sdd-$f.md" && echo "OK fase $f" || echo "FALLO fase $f — ejecutar: bash $SDD_HOME/install.sh $f"
done
test -f .claude/CLAUDE.md && echo "OK claude-md" || echo "FALLO claude-md"
test -f .sdd/project-init.json && echo "OK init-json" || echo "FALLO init-json"
grep -q '"dispatcher": "wf-project-init"' .sdd/project-init.json && echo "OK schema" || echo "FALLO schema"
grep -q '"topology"' .sdd/project-init.json && echo "OK topology" || echo "FALLO topology — añadir el campo topology (Paso 8)"
grep -q '"artifacts"' .sdd/project-init.json || grep -q '"artifacts_source"' .sdd/project-init.json && echo "OK artifacts-map" || echo "FALLO artifacts-map"
test -f .sdd/scripts/sdd-gate-check.py && test -f .sdd/scripts/sdd-seal.py && test -f .sdd/scripts/sdd-task-state.py && test -f .sdd/scripts/sdd-sync-check.py && test -f .sdd/scripts/sdd-skill-allow.py && echo "OK enforcement-scripts" || echo "FALLO enforcement-scripts"
test -f .sdd/sdd-version.json && echo "OK sdd-version" || echo "FALLO sdd-version"
grep -qx '\.claude/settings\.local\.json' .gitignore 2>/dev/null && echo "OK gitignore" || echo "FALLO gitignore"
```

---

## Paso 9b: Aviso de SSoT sin git (advisory, solo topologías productoras de SSoT)

Las topologías que **producen un SSoT** que otros repos consumen —`authoring`, `design` y `standalone`— son pineadas por SHA desde los consumers (`artifacts_source_pin` / `design_source_pin` = `git rev-parse --short HEAD`). Si el repo **no está bajo git**, ese pin queda `unknown` y el subsistema de drift cross-repo (D-011/D-012) se degrada a no-op para esta fuente.

Emite el aviso con un `echo` **determinista** (no lo parafrasees: garantiza el texto exacto y que solo aparezca cuando aplica). El propio bloque comprueba la condición —topología productora de SSoT (`authoring`/`design`/`standalone`, **no** `consumer`) **y** `is_git_repo: false`— y no imprime nada en caso contrario:

```bash
TOPOLOGY="<TOPOLOGY>"   # la topología elegida en Q1
case "$TOPOLOGY" in
  authoring|design|standalone)
    if python3 "$SDD_HOME/scripts/sdd-init-detect.py" detect --json | grep -q '"is_git_repo": false'; then
      echo "⚠ Este repo es un SSoT de $TOPOLOGY que los repos consumidores pinearán por SHA, pero no está bajo control de versiones. Ejecuta git init (y un primer commit) para que sea pineable; sin git, el pin de los consumers quedará unknown y el aviso de drift cross-repo no podrá funcionar."
    fi ;;
esac
```

`consumer` no entra en el `case` (no es SSoT; su falta de git no rompe pins ajenos). Si está bajo git, o es `consumer`, el bloque no imprime nada. Muestra al usuario, tal cual, la línea que emita el `echo` (no la reformules).

---

## Paso 10: Informe final

- **Topología, superficie(s) y fases instaladas**
- **Stack**: configurado y despachado / agnóstico (modo genérico) / no aplica (authoring)
- **Diseño**: rol instalado (system / feature / full / sin diseño)
- **Verificación**: resultado de los checks del Paso 9
- **Siguiente paso según topología**:
  - authoring → `/wf-prd-create` o `/wf-prd-review` (si PRD); si no, `/wf-spec-analyze`. Si hay diseño: `/wf-design-intake generate <feature_spec>`.
  - consumer → leer specs del SSoT y `/wf-prepare-plan generate <feature_spec>` (si UI, antes `/wf-design-feature-prototype`).
  - standalone → primer paso de la fase más temprana instalada.
- Si en 3c se detectaron artefactos fuera del directorio que declara `artifacts`, avisar y ofrecer mover o actualizar el mapa.
- Si hubo deuda multi-superficie (5.S4), recordar que las superficies con stack pendiente se completan con "Completar / ampliar".

---

## Paso 11: Recordatorio de activación

**Siempre, como última acción del init** (tras el informe del Paso 10). `install.sh` ya emite este aviso, pero su salida queda **colapsada** en el output del Paso 6 y el usuario no lo ve. Emítelo con un `echo` **determinista** (no lo parafrasees: garantiza el texto exacto y que siempre aparezca):

```bash
echo "Ejecuta /skills y /agents para revisar que Claude ha cargado correctamente el ecosistema. Si quieres empezar con contexto limpio, ejecuta /clear."
```
- **Recordatorio de activación (siempre, como última línea del informe):** indica al usuario que ejecute `/skills` y `/agents` para revisar que Claude ha cargado correctamente el ecosistema, y `/clear` si quiere empezar con contexto limpio. `install.sh` emite este aviso, pero su salida queda **colapsada** en el output del Paso 6, así que el informe del skill **debe** repetirlo explícitamente o el usuario no lo verá.
