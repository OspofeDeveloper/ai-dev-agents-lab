---
name: wf-project-init
description: "Onboarding para inicializar un proyecto SDD. Instala siempre el backbone del pipeline (spec, plan, tasks) y añade prd/design segun la entrevista. El perfil de quien inicializa (desarrollo, producto, diseño, personalizado) decide que preguntas tecnicas se hacen ahora y cuales quedan pendientes. Genera un CLAUDE.md raiz adaptado, registra el estado en .sdd/project-init.json y despacha al workflow init especialista del stack cuando el perfil es desarrollo. Soporta ampliacion incremental sobre un init previo."
when_to_use: "Activa con frases como 'inicializa el proyecto', 'arranca el setup tecnico', 'init del proyecto', 'prepara este proyecto para SDD', 'quiero trabajar specs aqui', 'configura este repo para diseño', 'completa la entrevista tecnica del proyecto'. No activa para crear skills o agentes del ecosistema SDD (usa wf-skill-create, wf-agent-create) ni para ejecutar el init concreto de un stack ya conocido (invoca directamente wf-<stack>-init)."
argument-hint: "[--profile <dev|product|design|custom>] [--type <app|web|backend|other>] [--stack <nombre>] [--name <nombre>] [--sdd-path <path>] [--force]"
effort: low
allowed-tools: [Read, Write, Bash]
context: fork
---

# wf-project-init — Onboarding de proyecto SDD

Tu rol es de **onboarding y dispatcher**: detectas el contexto, entrevistas lo mínimo según el perfil, instalas las fases y despachas al init especialista del stack cuando aplica.

**ESTE WORKFLOW ES BLOQUEANTE.** Si el usuario tenía una petición pendiente (una consulta, una tarea), NO la atiendas hasta completar el Paso 9 (verificación) con todos los checks en verde. Un init sin fases instaladas es un init FALLIDO aunque existan los JSON de estado.

**Reglas de la entrevista:**

1. **Toda pregunta usa `AskUserQuestion`** — nunca texto libre. No producir texto antes de la primera pregunta.
2. **No preguntar lo que ya se sabe** — argumentos, `KNOWN_STATE` o artefactos detectados pre-rellenan. Valor conocido → confirmación ("Sí, correcto" / "No, cambiar"); desconocido → pregunta completa.
3. **Opciones exactas** — las escritas aquí. No añadir, quitar ni sustituir.
4. **Backbone fijo**: `spec`, `plan` y `tasks` se instalan SIEMPRE. La entrevista solo decide `prd`, `design` y cuánta información técnica se captura ahora.

---

## Paso 1: Parsear argumentos

- `--profile`: `dev`, `product`, `design`, `custom`. Omite la pregunta de perfil.
- `--type`: `app`, `web`, `backend`, `other`. Omite la pregunta de tipo.
- `--stack`: nombre del stack. Omite framework/targets.
- `--name`: nombre del proyecto. Default: `basename $PWD`.
- `--sdd-path`: ruta al framework. Default: auto-detección (Paso 2).
- `--force`: rehacer el init sobreescribiendo fases.

---

## Paso 2: Detectar SDD_HOME

Precedencia: `--sdd-path` → `$SDD_HOME` → `~/.sdd-home`. Si ninguna resuelve, abortar:
> "No puedo localizar el framework SDD. Ejecuta `bash setup.sh` desde el repo del ecosistema, o pasa `--sdd-path /ruta/a/sdd`."

Verificar que existe `$SDD_HOME/install.sh`. Si no, abortar explicándolo.

---

## Paso 3: Detectar estado previo

```bash
test -f .sdd/project-init.json && echo "init-found"
test -f .claude/sdd-mode.json && echo "mode-found"
for f in prd spec design plan tasks; do
  test -f ".claude/rules/sdd-$f.md" -o -f "$f/.claude/CLAUDE.md" && echo "phase-installed:$f"
done
```

(El segundo test cubre proyectos con el layout legacy de fases en subdirectorios.)

**3a. Modo libre.** Si `sdd-mode.json` tiene `"mode": "free"`, confirmar con AskUserQuestion ("Sí, convertir a SDD" / "No, mantener modo libre"). "No" → cerrar sin tocar nada.

**3b. Init previo.** Si existe `project-init.json`, leerlo, poblar `KNOWN_STATE` (profile, type, stack, phases) y mostrar resumen compacto. Luego AskUserQuestion:

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

`MODE=extend` mantiene lo instalado y solo pregunta lo que falte (ej. un PM inicializó y ahora un dev completa la entrevista técnica). Si hay `--force` como argumento, rehacer sin preguntar.

**3c. Artefactos.** Refinar `KNOWN_STATE`: `prd/PRD.md` → `use_prd=true`; `design/DESIGN.md` o `DESIGN_BRIEF.md` → `design_strategy="existing_design"`; specs existentes (`spec/features/` o specs detectados en otra ruta) → `specs_exist=true` (anotar la ruta real si no es la canónica).

**3d. Carpetas candidatas de artefactos.** Detectar carpetas propias del proyecto que puedan ser el hogar de los artefactos de cada fase:

```bash
for d in specs docs/specs documentation/specs; do test -d "$d" && echo "candidate:spec:$d"; done
for d in docs/prd product docs/product requirements; do test -d "$d" && echo "candidate:prd:$d"; done
for d in docs/design design-system; do test -d "$d" && echo "candidate:design:$d"; done
```

Guardar en `KNOWN_STATE.artifact_candidates`. Estas carpetas alimentan la pregunta 5.7 (solo se pregunta si hay candidatas).

---

## Paso 4: Analizar el proyecto en silencio

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

| Condición | DETECTED_STACK (y tipo implícito) |
|---|---|
| `gradle-found` + (`iosApp-found` o `composeApp-found`) | `kmm` (app) |
| `flutter-found` | `flutter` (app) |
| `android-build-found` sin `iosApp-found` | `android` (app) |
| `next-found` / `vite-react-found` / `astro-found` | `next` / `vite-react` / `astro` (web) |
| `ktor-found` / `express-found` / `fastapi-found` | `ktor` / `node-express` / `fastapi` (backend) |
| Ninguna | sin detección |

Con detección: pre-rellenar `KNOWN_STATE.project_type` y, si es stack app, `KNOWN_STATE.app_framework` (`kmm`→`compose_multiplatform`, etc.).

---

## Paso 5: Entrevista

Secuencia única para todos los perfiles — lo que varía es qué pasos aplican:

```
5.0 Perfil     → siempre (salvo --profile)
5.1 PRD        → siempre
5.2 Tipo       → SIEMPRE (identidad del proyecto, no del perfil)
5.3 Diseño     → según perfil y tipo (tabla abajo)
5.4 Framework  → SOLO perfil dev y tipo app
5.5 Targets    → SOLO framework multiplataforma
5.6 Stack      → derivar sin preguntar
5.7 Artefactos → SOLO si hay carpetas candidatas detectadas (3d)
5.8 Pipeline   → siempre (salvo ampliación con valor previo)
5.9 Resumen    → siempre
```

### 5.0 — Perfil

```
question: "¿Cómo se va a trabajar en este proyecto?"
header: "Perfil"
opciones:
  - label: "Desarrollo"
    description: "Pipeline completo con entrevista técnica: se configura el stack ahora"
  - label: "Producto"
    description: "PRD y specs. La configuración técnica queda pendiente para cuando entre desarrollo"
  - label: "Diseño"
    description: "Sistema visual y prototipado desde PRD/specs. Sin configuración técnica ahora"
  - label: "Personalizado"
    description: "Decidir fase a fase qué se instala ahora"
```

`PROFILE = dev | product | design | custom`.

### 5.0b — Topología [SOLO perfil dev]

```
question: "¿Este repo contiene sus propios specs o los consume de otro repo?"
header: "Topología"
opciones:
  - label: "Specs propios (Recomendado)"
    description: "Monorepo o producto único: PRD/specs y código viven aquí. Pipeline completo"
  - label: "Consume specs de otro repo"
    description: "Repo técnico (server, app, web) de un producto multi-repo: los specs viven en un repo SSoT compartido. Aquí solo se instalan plan y tasks (+ overlay de stack)"
```

Si **consume** → `TOPOLOGY = consumer` y preguntar (texto libre vía "Other") el **path local al checkout del repo SSoT** (sibling `../<repo>` o submodule). Validar: el path existe y contiene specs (`features/` o `*_features.md`, buscando también bajo `artifacts.spec` de SU `project-init.json` si lo tiene). Si no valida → re-preguntar o detener con instrucciones de clonarlo. Guardar `ARTIFACTS_SOURCE = <path>` y el pin `ARTIFACTS_SOURCE_PIN = git -C <path> rev-parse --short HEAD` (si es repo git; si no, `unknown`).

En modo consumer: **saltar 5.1 (PRD), 5.3 (Diseño) y 5.7 (Artefactos)** — la autoría vive en el repo SSoT. La entrevista técnica (5.2, 5.4-5.6) aplica igual: este repo ES el código.

Si specs propios → `TOPOLOGY = standalone` (comportamiento de siempre, no guardar campos extra).

### 5.1 — PRD [siempre, salvo consumer]

```
question: "¿Vas a partir de un PRD o vas a crear uno?"
header: "PRD"
opciones:
  - label: "Sí voy a usar PRD"
    description: "Se instalará prd/ con sus skills"
  - label: "No voy a usar PRD"
    description: "El pipeline arranca en spec/ desde tus documentos de requisitos"
```

### 5.2 — Tipo [SIEMPRE, ningún perfil lo salta]

```
question: "¿Qué tipo de software es este proyecto?"
header: "Tipo"
opciones:
  - label: "App"
    description: "App móvil o multiplataforma (Android, iOS, Desktop)"
  - label: "Web"
    description: "Aplicación web (Next.js, React, Astro, Vue...)"
  - label: "Backend"
    description: "API o microservicio (Ktor, Express, FastAPI...)"
  - label: "Otro software"
    description: "Librería, CLI, tooling, scripts, ecosistemas de agentes... El plan y las tasks se fundamentan en el propio repo"
```

`project_type = app | web | backend | other`.

### 5.3 — Diseño

| Perfil | Tipo | Acción |
|---|---|---|
| `design` | cualquiera | `design` SE INSTALA siempre. Preguntar estrategia solo si no hay diseño detectado: "Voy a crear un diseño" / "Ya tengo un diseño" |
| `dev` o `custom` | `app` o `web` | Pregunta completa de 3 opciones (abajo) |
| `dev` o `custom` | `backend` u `other` | OMITIR — sin design |
| `product` | cualquiera | OMITIR — sin design (ampliable después) |

```
question: "¿Vas a querer implementar diseño o partes de un diseño?"
header: "Diseño"
opciones:
  - label: "Voy a crear un diseño"
    description: "Se instalará design/ con skills de sistema visual, prototipado y tokens"
  - label: "Ya tengo un diseño"
    description: "Se instalará design/ para trabajar con el diseño existente"
  - label: "No vamos a usar diseño"
    description: "El pipeline irá de Spec directamente a Plan"
```

`design_strategy = create_design | existing_design | no_design`.

### 5.4 — Framework [SOLO perfil dev y tipo app]

Exactamente estas cuatro opciones; no añadir tecnologías web/backend:

```
question: "¿Qué tipo de app vas a hacer?"
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

### 5.5 — Targets [SOLO compose_multiplatform o flutter]

```
question: "¿Qué targets va a soportar?"
header: "Targets"
multiSelect: true
opciones: [Android, iOS, Desktop]
```

Mínimo uno. Guardar en minúscula.

### 5.6 — Derivar STACK (sin preguntar)

| Caso | STACK |
|---|---|
| `--stack` pasado | ese valor (precedencia total) |
| `project_type == "other"` | `"agnostico"` (decisión explícita: sin stack) |
| Perfil `dev`, tipo app | por framework: `android`/`ios`/`kmm`/`flutter` |
| Perfil `dev`, tipo web/backend | `DETECTED_STACK` si hubo detección; si no, `"agnostico"` |
| Perfil `product`/`design`/`custom` (sin entrevista técnica) | `null` (**pendiente** — la completará desarrollo vía "Completar / ampliar") |

> `null` ≠ `agnostico`: `null` significa "aún no se ha hecho la entrevista técnica" (el gate de plan la exigirá); `agnostico` significa "este software no tiene stack especialista, modo genérico".

### 5.7 — Ubicación de artefactos [SOLO si `KNOWN_STATE.artifact_candidates` no está vacío]

El layout por defecto es el canónico: los artefactos de cada fase viven en su directorio (`prd/`, `spec/`, `design/`). Si el proyecto ya tiene carpetas propias (3d), preguntar **una vez por fase con candidata**:

```
question: "He detectado la carpeta `<candidata>`. ¿Dónde deben vivir los artefactos de la fase <fase>?"
header: "Artefactos"
opciones:
  - label: "Usar <candidata>"
    description: "Los artefactos de <fase> (specs, análisis, features/...) se crearán bajo <candidata>/"
  - label: "Usar la canónica (<fase>/)"
    description: "Layout estándar del pipeline SDD"
```

Resultado → `ARTIFACTS_MAP` con un directorio por fase instalada (canónico si no se preguntó). Sin candidatas: `ARTIFACTS_MAP` canónico sin preguntar.

### 5.8 — Modo del pipeline [siempre, salvo ampliación con valor previo]

```
question: "¿Qué rigor de pipeline quieres por defecto en este proyecto?"
header: "Pipeline"
opciones:
  - label: "Standard (Recomendado)"
    description: "Specs completos (8 elementos, ≥3 CAs), análisis previo como artefacto. Para productos con specs estables"
  - label: "Ligero"
    description: "Specs proporcionales (núcleo de 4 elementos, ≥1 CA), análisis inline. Para scrum cambiante y features pequeñas. Los gates anti-alucinación son idénticos; cada feature puede forzar el otro modo con --light/--standard"
```

Resultado → `PIPELINE_MODE` (`standard` | `light`).

### 5.9 — Resumen y confirmación [siempre]

```
Configuración del proyecto
──────────────────────────────────────────────────
Perfil:    <Desarrollo / Producto / Diseño / Personalizado>
Tipo:      <App / Web / Backend / Otro software>
Fases:     <prd → spec → design → plan → tasks>   (backbone spec/plan/tasks + las elegidas)
Stack:     <stack / agnóstico / pendiente de entrevista técnica>
Targets:   <android, ios, desktop>                [solo si multiplataforma]
Pipeline:  <standard / ligero>
Modo:      <instalación nueva / ampliación>
──────────────────────────────────────────────────
```

Confirmar con AskUserQuestion ("Instalar" / "Cambiar algo" → vuelve a 5.0).

---

## Paso 6: Derivar fases e instalar

```
TOPOLOGY == standalone:
  SELECTED_PHASES = [spec, plan, tasks]                            ← backbone
  use_prd == true                  → anteponer prd
  design según tabla 5.3 == sí     → insertar design tras spec

TOPOLOGY == consumer:
  SELECTED_PHASES = [plan, tasks]                                  ← sin autoría
  (la autoría de prd/spec/design vive en el repo SSoT; las kb de lectura
   cross-fase — kb-spec-expert, kb-a11y-expert — las trae install.sh plan
   como dependencia)
```

Orden canónico: `prd → spec → design → plan → tasks` (solo las presentes).

Instalación única **desde la raíz del proyecto** (toda la infraestructura va al `.claude/` raíz; los CLAUDE.md de fase quedan como reglas de carga perezosa por path en `.claude/rules/sdd-<fase>.md`):

```bash
bash "$SDD_HOME/install.sh" <fase1,fase2,...>
```

En `MODE=extend`, pasar solo las fases que falten. Con `--force`, pasar todas.

Crear además los directorios de artefactos según `ARTIFACTS_MAP` (5.7):

```bash
mkdir -p <artifacts.prd> <artifacts.design>          # solo las fases instaladas
mkdir -p <artifacts.spec>/features
```

En `TOPOLOGY=consumer` no hay `ARTIFACTS_MAP`: crear solo `mkdir -p features` (ahí vivirán las subcarpetas `plan/` y `tasks/` de cada feature, con `Spec origen` apuntando al checkout del SSoT).

**Ajustar los globs de las reglas al layout del proyecto**: si algún directorio de `ARTIFACTS_MAP` difiere del canónico, edita el frontmatter `paths:` de la regla correspondiente (`.claude/rules/sdd-prd.md`, `sdd-spec.md`, `sdd-design.md`) sustituyendo el glob del directorio canónico (p. ej. `"spec/**"`) por el real (p. ej. `"specs/**"`). Los globs por nombre de artefacto (`**/*_spec.md`...) no se tocan: son independientes del layout.

No continuar al Paso 7 sin haber ejecutado el install con TODAS las fases seleccionadas.

---

## Paso 7: Generar CLAUDE.md raíz

**No copiar `$SDD_HOME/CLAUDE.md`.** Generar `.claude/CLAUDE.md` con esta plantilla (solo filas de fases instaladas). **Siempre se sobreescribe** el que `install.sh` haya copiado en el Paso 6 — la plantilla del proyecto manda:

```markdown
# <nombre-proyecto> — Proyecto SDD

Proyecto gestionado con Spec Driven Development. Fases instaladas: <lista en orden>.

## Cómo operar

- Toda la infraestructura (skills, agentes, reglas) vive en este `.claude/`. Las instrucciones detalladas de cada fase son reglas de carga perezosa (`.claude/rules/sdd-<fase>.md`): el harness las carga automáticamente al tocar los artefactos de esa fase. Si vas a operar una fase sin haber tocado aún sus artefactos, léelas primero. No improvises workflows.
- Respeta el orden del pipeline: una fase consume artefactos de la anterior.
- Modo de pipeline por defecto: **<standard|ligero>** (`pipeline_mode` de `.sdd/project-init.json`). Cada feature puede forzar el otro modo con `--light`/`--standard` al generar su spec; los gates anti-alucinación son idénticos en ambos.
- Estado del proyecto: `.sdd/project-init.json`. Para completar la entrevista técnica o añadir fases: `/wf-project-init` → "Completar / ampliar".

## Layout de artefactos

Los artefactos de cada fase viven en el directorio declarado en `artifacts` de `.sdd/project-init.json` (rutas relativas a la raíz del proyecto):

| Fase | Directorio de artefactos | Qué contiene |
|---|---|---|
| PRD | `<artifacts.prd>/` | `prd.md`, `*_analysis.md`, `*_discovery.md` |
| Spec | `<artifacts.spec>/` | `_features.md`, `features/<nombre>/` (una carpeta por feature) |
| Design | `<artifacts.design>/` | `DESIGN_BRIEF.md`, `DESIGN.md`, `tokens/` |

Cada feature organiza sus artefactos en subcarpetas por fase, con el `README.md` en su raíz:

```
features/<nombre>/
  README.md
  spec/    <nombre>_spec.md (+ deltas, sync_requirements, conflict_report)
  design/  <nombre>_flows.md, _views.md, _ui_prompt.md (+ discovery, moodboard, variantes)
  plan/    <nombre>_plan.md
  tasks/   <nombre>_tasks.md (+ <nombre>_bugs.md, mantenimiento)
```

Los `_plan.md` y `_tasks.md` de cada feature viven SIEMPRE dentro de su carpeta de feature para preservar la trazabilidad por rutas relativas (`Spec origen: ../spec/<nombre>_spec.md`). Las features creadas con el layout plano legacy (artefactos directamente en `features/<nombre>/`) siguen siendo válidas: los workflows leen ambos layouts y no los mezclan dentro de una misma feature. Los workflows resuelven sus rutas de salida desde este mapa — no escribas artefactos fuera de él.

## Fases y sus reglas

| Fase | Regla (se carga sola al tocar sus artefactos) |
|---|---|
| PRD | `.claude/rules/sdd-prd.md` |
| Spec | `.claude/rules/sdd-spec.md` |
| Design | `.claude/rules/sdd-design.md` |
| Plan | `.claude/rules/sdd-plan.md` |
| Tasks | `.claude/rules/sdd-tasks.md` |

El rootmap de workflows de cada fase vive en su regla, no aquí: este orquestador no conoce detalles de ninguna fase. Para arrancar una fase cuyos artefactos aún no existen, lee su regla primero.

## Política de git

- Se commitea TODO `.claude/` (skills, agentes, rules, settings.json) y TODO `.sdd/` (estado, scripts de enforcement, sello de versión): el repo funciona para cualquier dev y en CI sin tener el ecosistema SDD instalado.
- Excepción única: `.claude/settings.local.json` (permisos personales de sesión) — está en `.gitignore` y nunca se commitea.
- Los artefactos SDD (PRD, `features/`, design) son el producto del pipeline: se commitean siempre.

### Trabajo en paralelo: una feature por rama

- **Una feature = una rama.** Cada feature vive en su carpeta `features/<nombre>/` (spec, design, plan, tasks): dos devs en features distintas tocan ficheros distintos y no colisionan.
- **`_features.md` es un índice GENERADO, no se edita a mano.** Lo regenera `python3 .sdd/scripts/sdd-features-index.py <raíz_spec>` desde el discovery + los specs + el readiness report. Un conflicto de merge sobre `_features.md` es ruido: acéptalo o regéneralo tras el merge (`git checkout --theirs`/`--ours` da igual; la verdad se reconstruye del disco).
- El registro de inits de stack es el log append-only `.sdd/stack-runs.jsonl` (no un array en `project-init.json`): los `>>` de ramas distintas se combinan sin pisarse.
```

(Solo filas de fases instaladas. Si hay stack especialista, añadir la fila `| Stack <stack> | .claude/rules/sdd-<stack>.md |`.)

**Variante consumer** (`TOPOLOGY=consumer`): sustituir la sección "Layout de artefactos" por:

```markdown
## Topología: repo consumidor

Los PRD/specs/design de este producto viven en el repo SSoT: `<artifacts_source>` (checkout local). Este repo solo PLANIFICA y EJECUTA:

- Specs (solo lectura): `<artifacts_source>/.../features/<nombre>/spec/<nombre>_spec.md`
- Planes y tasks (de este repo): `features/<nombre>/plan/` y `features/<nombre>/tasks/` — cada repo consumidor tiene SU propio plan de la misma feature, con `Spec origen` apuntando al checkout del SSoT.
- Cambios de spec → se piden en el repo SSoT, nunca se editan aquí.
- Pin de specs: `artifacts_source_pin` en `.sdd/project-init.json` — si el SSoT avanza, los workflows de plan avisan.
```

En `MODE=extend`, regenerar con la unión de fases. En el flujo de init, este archivo siempre sustituye al que `install.sh` copió en el Paso 6.

**`.gitignore` del proyecto**: asegura que contiene la línea `.claude/settings.local.json` — añádela si falta (crea el archivo si no existe; nunca toques el resto del contenido). Es la única pieza SDD que no se commitea (política de git de la plantilla de arriba).

---

## Paso 8: Registrar estado y despachar

1. `mkdir -p .sdd`. Timestamp real: ejecutar `date -u +%Y-%m-%dT%H:%M:%SZ` y usar SU SALIDA — nunca escribir un timestamp de memoria.
2. Escribir `.sdd/project-init.json` con **EXACTAMENTE estos campos — ni uno más, ni uno menos**. No añadir objetos por fase ni estado de features (eso vive en `_features.md`):

```json
{
  "name": "<nombre-proyecto>",
  "profile": "<dev|product|design|custom>",
  "type": "<app|web|backend|other>",
  "stack": "<stack|agnostico|null>",
  "targets": ["..."] ,
  "phases": ["<fases en orden canónico>"],
  "artifacts": { "prd": "<dir>", "spec": "<dir>", "design": "<dir>" },
  "pipeline_mode": "<standard|light>",
  "sdd_version": "<version+commit del sello>",
  "initialized_at": "<salida de date -u>",
  "dispatcher": "wf-project-init",
  "specialist_workflow": "<wf-<stack>-init | null>"
}
```

> El registro de ejecuciones del init de stack **no** vive en `project-init.json` (sería un array creciente dentro de un fichero de config compartido → conflicto de merge garantizado con varios devs). Vive en un log append-only aparte, `.sdd/stack-runs.jsonl` (una línea JSON por run), que lo escribe `wf-<stack>-init`. `project-init.json` queda como config estable.

(`sdd_version` sale de `.sdd/sdd-version.json` — lo escribe `install.sh` en el Paso 6: concatenar `<version>+<commit>`. Si el sello no existe (instalación anómala), usar `unknown`. Las actualizaciones posteriores las gestiona `/wf-sdd-update`, no este workflow. `pipeline_mode` sale de la pregunta 5.8: es el default del proyecto — cada feature puede forzar el otro modo con `--light`/`--standard`.)

**Variante consumer** (`TOPOLOGY=consumer`, 5.0b): sustituir la clave `artifacts` por estas dos:

```json
  "artifacts_source": "<path local al checkout del repo SSoT>",
  "artifacts_source_pin": "<commit corto del SSoT al hacer el init | unknown>"
```

(`phases` será `["plan", "tasks"]`. El pin registra contra qué versión de los specs se inicializó este repo: los workflows de plan avisan — sin bloquear — si el checkout del SSoT avanzó respecto al pin. Para refrescar el pin tras revisar los cambios: actualizar el valor con `git -C <artifacts_source> rev-parse --short HEAD`.)

(`targets` solo si multiplataforma; en otro caso omitir esa clave. `specialist_workflow` solo si el stack es concreto Y existe `wf-<stack>-init`. `artifacts` sale de `ARTIFACTS_MAP` (5.7): una clave por fase instalada de entre `prd`/`spec`/`design`, valor relativo a la raíz — canónico es el nombre de la fase, p. ej. `"spec": "spec"`. plan/tasks no tienen clave: sus artefactos viven dentro de la carpeta de cada feature — subcarpetas `plan/` y `tasks/`, hermanas de `spec/`.)

3. Escribir `.claude/sdd-mode.json`:

```json
{ "mode": "sdd", "decided_at": "<salida de date -u>", "decided_by": "wf-project-init" }
```

4. **Solo si** `specialist_workflow` no es null → invocar `wf-<stack>-init` **via Skill tool** (nunca `tech/<stack>/install.sh` a mano).

---

## Paso 9: VERIFICACIÓN OBLIGATORIA

Ejecutar y mostrar el resultado. Si algún check falla, corregirlo y re-verificar ANTES de dar el init por terminado o atender cualquier otra petición:

```bash
for f in <SELECTED_PHASES>; do
  test -f ".claude/rules/sdd-$f.md" && echo "OK fase $f" || echo "FALLO fase $f — ejecutar: bash $SDD_HOME/install.sh $f"
done
test -f .claude/CLAUDE.md && echo "OK claude-md" || echo "FALLO claude-md"
test -f .sdd/project-init.json && echo "OK init-json" || echo "FALLO init-json"
grep -q '"dispatcher": "wf-project-init"' .sdd/project-init.json && echo "OK schema" || echo "FALLO schema — reescribir con los campos exactos del Paso 8"
grep -q '"artifacts"' .sdd/project-init.json && echo "OK artifacts-map" || echo "FALLO artifacts-map — añadir el mapa artifacts del Paso 8"
test -f .sdd/scripts/sdd-gate-check.py && test -f .sdd/scripts/sdd-seal.py && test -f .sdd/scripts/sdd-task-state.py && test -f .sdd/scripts/sdd-sync-check.py && test -f .sdd/scripts/sdd-skill-allow.py && echo "OK enforcement-scripts" || echo "FALLO enforcement-scripts — copiar desde $SDD_HOME/scripts/ (Paso 6)"
test -f .sdd/sdd-version.json && echo "OK sdd-version" || echo "FALLO sdd-version — re-ejecutar install.sh (Paso 6) para sellar la versión"
grep -qx '\.claude/settings\.local\.json' .gitignore 2>/dev/null && echo "OK gitignore" || echo "FALLO gitignore — añadir la línea .claude/settings.local.json (Paso 7)"
```

---

## Paso 10: Informe final

- **Perfil, tipo y fases instaladas** (backbone + elegidas)
- **Stack**: configurado y despachado / agnóstico (modo genérico) / **pendiente de entrevista técnica** (indicar que desarrollo deberá ejecutar `/wf-project-init` → "Completar / ampliar")
- **Verificación**: resultado de los checks del Paso 9
- **Siguiente paso según perfil**: prd → `/wf-prd-create` o `/wf-prd-review`; product sin prd → `/wf-spec-analyze`; design → `/wf-design-intake generate <feature_spec>`; dev → primer paso de la fase más temprana
- Si en el Paso 3c se detectaron artefactos fuera del directorio que declara `artifacts` (ej. specs bajo el directorio del PRD), avisar al usuario: el pipeline espera `<artifacts.spec>/features/`; ofrecer moverlos o actualizar el mapa `artifacts` para reflejar la ruta real
