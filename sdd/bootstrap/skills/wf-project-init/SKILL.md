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
for f in prd spec design plan tasks; do test -f "$f/.claude/CLAUDE.md" && echo "phase-installed:$f"; done
```

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

### 5.1 — PRD [siempre]

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

### 5.9 — Resumen y confirmación [siempre]

```
Configuración del proyecto
──────────────────────────────────────────────────
Perfil:    <Desarrollo / Producto / Diseño / Personalizado>
Tipo:      <App / Web / Backend / Otro software>
Fases:     <prd → spec → design → plan → tasks>   (backbone spec/plan/tasks + las elegidas)
Stack:     <stack / agnóstico / pendiente de entrevista técnica>
Targets:   <android, ios, desktop>                [solo si multiplataforma]
Modo:      <instalación nueva / ampliación>
──────────────────────────────────────────────────
```

Confirmar con AskUserQuestion ("Instalar" / "Cambiar algo" → vuelve a 5.0).

---

## Paso 6: Derivar fases e instalar

```
SELECTED_PHASES = [spec, plan, tasks]                              ← SIEMPRE
use_prd == true                  → anteponer prd
design según tabla 5.3 == sí     → insertar design tras spec
```

Orden canónico: `prd → spec → design → plan → tasks` (solo las presentes).

Para cada fase **no instalada ya** (en `MODE=extend` saltar las existentes; con `--force` reinstalar):

```bash
mkdir -p <fase>/features
(cd <fase> && bash "$SDD_HOME/install.sh" <fase>)
```

No continuar al Paso 7 sin haber ejecutado el install de TODAS las fases seleccionadas.

---

## Paso 7: Generar CLAUDE.md raíz

**No copiar `$SDD_HOME/CLAUDE.md`.** Generar `.claude/CLAUDE.md` con esta plantilla (solo filas de fases instaladas):

```markdown
# <nombre-proyecto> — Proyecto SDD

Proyecto gestionado con Spec Driven Development. Fases instaladas: <lista en orden>.

## Cómo operar

- Cada fase vive en su directorio (`<fase>/`) con su propio `.claude/CLAUDE.md`: al trabajar una fase, opera desde ese directorio siguiendo sus instrucciones. No improvises workflows.
- Respeta el orden del pipeline: una fase consume artefactos de la anterior.
- Estado del proyecto: `.sdd/project-init.json`. Para completar la entrevista técnica o añadir fases: `/wf-project-init` → "Completar / ampliar".

## Entrypoints por fase

| Fase | Directorio | Primer paso |
|---|---|---|
| PRD | `prd/` | `/wf-prd-create` para redactar, `/wf-prd-review` si ya existe |
| Spec | `spec/` | `/wf-spec-analyze <doc>` y después `/wf-spec-features-first <prd>` |
| Design | `design/` | `/wf-design-intake generate <feature_spec>` (gate obligatorio) |
| Plan | `plan/` | `/wf-prepare-plan generate <feature_spec>` |
| Tasks | `tasks/` | `/wf-prepare-tasks generate <feature_plan>` tras `/wf-plan-validate` |
```

En `MODE=extend`, regenerar con la unión de fases. Sin extend ni `--force`, no sobreescribir uno existente.

---

## Paso 8: Registrar estado y despachar

1. `mkdir -p .sdd`. Timestamp real: ejecutar `date -u +%Y-%m-%dT%H:%M:%SZ` y usar SU SALIDA — nunca escribir un timestamp de memoria.
2. Escribir `.sdd/project-init.json` con **EXACTAMENTE estos campos — ni uno más, ni uno menos**. No añadir `version`, ni objetos por fase, ni estado de features (eso vive en `_features.md`):

```json
{
  "name": "<nombre-proyecto>",
  "profile": "<dev|product|design|custom>",
  "type": "<app|web|backend|other>",
  "stack": "<stack|agnostico|null>",
  "targets": ["..."] ,
  "phases": ["<fases en orden canónico>"],
  "initialized_at": "<salida de date -u>",
  "dispatcher": "wf-project-init",
  "specialist_workflow": "<wf-<stack>-init | null>",
  "stack_workflows_run": []
}
```

(`targets` solo si multiplataforma; en otro caso omitir esa clave. `specialist_workflow` solo si el stack es concreto Y existe `wf-<stack>-init`.)

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
  test -f "$f/.claude/CLAUDE.md" && echo "OK fase $f" || echo "FALLO fase $f — ejecutar: (cd $f && bash $SDD_HOME/install.sh $f)"
done
test -f .claude/CLAUDE.md && echo "OK claude-md" || echo "FALLO claude-md"
test -f .sdd/project-init.json && echo "OK init-json" || echo "FALLO init-json"
grep -q '"dispatcher": "wf-project-init"' .sdd/project-init.json && echo "OK schema" || echo "FALLO schema — reescribir con los campos exactos del Paso 8"
```

---

## Paso 10: Informe final

- **Perfil, tipo y fases instaladas** (backbone + elegidas)
- **Stack**: configurado y despachado / agnóstico (modo genérico) / **pendiente de entrevista técnica** (indicar que desarrollo deberá ejecutar `/wf-project-init` → "Completar / ampliar")
- **Verificación**: resultado de los checks del Paso 9
- **Siguiente paso según perfil**: prd → `/wf-prd-create` o `/wf-prd-review`; product sin prd → `/wf-spec-analyze`; design → `/wf-design-intake generate <feature_spec>`; dev → primer paso de la fase más temprana
- Si en el Paso 3c se detectaron artefactos en rutas no canónicas (ej. specs bajo `prd/features/`), avisar al usuario: el pipeline espera `spec/features/`; ofrecer moverlos o anotar la ruta real
