---
name: wf-kmm-init
description: "Init especialista del stack KMM: produce kmm_project_state.md con el estado tecnico (targets, arquitectura, DI, networking, auth, storage, recursos, navegacion, testing, build commands). Modo detect (auto-exploracion delegando en kmm-explorer) y modo configure (preguntas para proyectos nuevos); si ya existe pregunta si rehacerlo y registra el run en .sdd/stack-runs.jsonl. Lo leen todos los agentes KMM al inicio."
when_to_use: "Activa con frases como 'init de KMM', 'inicializa el stack KMM', 'detecta el estado KMM del proyecto', 'configura un nuevo proyecto KMM', 'arranca el setup KMM', 'genera el estado tecnico KMM'. No activa para el init generico de stack desconocido (usa wf-project-init que despacha a este) ni para configurar piezas concretas como auth o networking (usa wf-kmm-auth-setup-keycloak, wf-kmm-network-setup, wf-kmm-stack-setup-ktor-keycloak-koin)."
argument-hint: "[--mode detect|configure] [--force] [--output <path>]"
effort: medium
allowed-tools: [Read, Write, Bash, AskUserQuestion, Agent]
user-invocable: true
---

# wf-kmm-init — Init especialista del stack KMM

Tu rol es de **orquestador** y corres en el **hilo principal** (no `context: fork`): decides el modo de operacion (detect o configure), recoges el estado actual y escribes `kmm_project_state.md` con el resultado consolidado.

- En **modo configure** entrevistas al usuario con la herramienta **`AskUserQuestion`** (preguntas reales con opciones, no texto libre). Esto solo es posible porque corres en el hilo principal — un fork no puede preguntar ([[D-015]]).
- En **modo detect** delegas la exploracion del repositorio al agente **`kmm-explorer`** mediante la herramienta **`Agent`** (contexto aislado, sin fork). No diagnosticas la arquitectura por tu cuenta — eso es trabajo del agente.

---

## Paso 1: Parsear argumentos y leer el contexto del proyecto

Extrae de `$ARGUMENTS`:

- `--mode`: `detect` o `configure`. Opcional. Si no se especifica, se infiere en el paso 3.
- `--force`: rehacer aunque ya exista `kmm_project_state.md`.
- `--output`: path del archivo a generar. Por defecto `kmm_project_state.md` en la raiz del proyecto.

Luego lee `.sdd/project-init.json` (si existe) y quédate con `topology`, `stack`, `targets` y `surfaces`. **No re-preguntes lo que ya está decidido ahí** — en particular los `targets` (Paso 5.1) y la topología:

```bash
test -f .sdd/project-init.json && python3 -c 'import json;d=json.load(open(".sdd/project-init.json"));print("topology="+str(d.get("topology")),"stack="+str(d.get("stack")),"targets="+str(d.get("targets")))' 2>/dev/null
```

- **`topology: standalone`** → el código vive **en este mismo repo**. La decisión detect/configure es "¿ya hay código KMM **aquí**?" (Paso 3), **no** "¿en qué otro repo está el código?". Nunca preguntes por un repo de código aparte.
- **`topology: consumer`** → el código vive aquí (es la superficie); los specs/diseño se resuelven del SSoT. Igual: opera sobre este repo.
- Si no existe `project-init.json`, continúa igual (Paso 7 ya avisa de que el flujo recomendado es `wf-project-init` primero).

---

## Paso 2: Comprobar si ya existe `kmm_project_state.md`

```bash
test -f kmm_project_state.md && echo "state-found"
```

Si existe y **no** hay `--force`:

1. Leer el archivo y mostrar al usuario un resumen (targets, arquitectura, fecha del ultimo init).
2. Preguntar con **`AskUserQuestion`** (header "KMM state", opciones):
   - **Mantener** — conservar el estado actual y cerrar el workflow.
   - **Rehacer** — regenerar entero (equivale a `--force`).
   - **Actualizar campos** — regenerar solo los campos que indique el usuario.

3. Segun la respuesta:
   - Opcion 1 → cerrar workflow con confirmacion.
   - Opcion 2 → continuar al paso 3 como si fuera primera vez.
   - Opcion 3 → continuar al paso 3 pero solo regenerar los campos indicados, preservando el resto.

Si existe y hay `--force`, avisar que se va a sobreescribir y continuar al paso 3.

---

## Paso 3: Decidir modo de operacion

Si `--mode` se especifico, usar ese valor. Si no, inferir asi:

```bash
# Indicios de proyecto KMM existente
test -f gradle/libs.versions.toml && echo "gradle-versions"
test -d composeApp && echo "compose-app"
test -d iosApp && echo "ios-app"
test -d shared && echo "shared-module"
test -f settings.gradle.kts && echo "settings-kts"
```

Los indicios se buscan **en este repo** (no en otro): en `standalone`/`consumer` el código KMM, si existe, vive aquí.

- Si hay al menos 2 indicios → `detect` (ya hay código KMM en este repo).
- Si no hay indicios o solo hay 1 debil → `configure` (greenfield: aún no hay código KMM aquí).
- Si la inferencia es ambigua, preguntar con **`AskUserQuestion`** (header "KMM mode"):
  - **detect** — auto-explorar el código KMM que ya hay en el repo.
  - **configure** — definir el stack desde cero (aún no hay código).

---

## Paso 4 (modo detect): Delegar exploracion a `kmm-explorer` vía `Agent`

Invoca al agente `kmm-explorer` con la herramienta **`Agent`** (subagente de contexto aislado; **no** es un fork de este workflow). Construye el prompt:

```text
Modo: kmm-init-detect

Tu mision es producir el contenido completo de `kmm_project_state.md` para este proyecto KMM existente.

Explora el repositorio y rellena las siguientes secciones:

1. Targets — Android (minSdk, targetSdk, compileSdk), iOS (deployment target, frameworks), desktop si aplica.
2. Arquitectura — modulos detectados (app, features, core, shared), respeto a kb-kmm-clean-architecture, ownership por capa.
3. DI — si usa Koin, modulos registrados, presencia de initKoin, qualifiers detectados.
4. Networking — stack HTTP (Ktor u otro), engine por plataforma, base URLs configuradas, plugins activos.
5. Auth — si hay sesion configurada, proveedor (Keycloak u otro), mecanismo HTTP (plugin Ktor, interceptor manual).
6. Storage — DataStore Preferences, paths actual por plataforma, factory.
7. Recursos — Compose Resources activo, modulos que los declaran, localizacion configurada.
8. Navegacion — Compose Navigation u otro, grafo principal, patron de eventos ViewModel↔Composable.
9. Testing — unit (commonTest), integration (androidTest), screenshot regression (Roborazzi), cobertura aproximada.
10. Brands / Environments — variantes configuradas, application IDs por brand×env, XCConfigs en iOS.
11. Build commands — comandos canonicos para build Android, build iOS, run desktop si aplica, tests.

Por cada seccion, cita la ruta concreta de los archivos clave (build.gradle.kts, libs.versions.toml, etc.) y la regla relevante de las kb-kmm-* cuando detectes desviaciones.

Devuelve el contenido en formato markdown listo para escribirse como `kmm_project_state.md`. No incluyas plan de remediacion: solo el estado actual.
```

Invoca `kmm-explorer` con la tool `Agent` pasando ese prompt y espera el contenido generado.

---

## Paso 5 (modo configure): Entrevistar al usuario con `AskUserQuestion`

Cada decisión es una pregunta con **`AskUserQuestion`** (opciones reales, no texto libre). Puedes **agrupar** varias preguntas relacionadas en una sola llamada de `AskUserQuestion`. Corres en el hilo principal, así que la herramienta está disponible.

### 5.1 Targets

**Si `project-init.json` ya declara `targets`** (caso normal cuando llegas despachado por `wf-project-init`), **NO los re-preguntes**: dalos por buenos y, como mucho, confírmalos en una línea. Solo si no hay `targets` declarados, pregunta con `AskUserQuestion` (multiSelect):

- Android · iOS · Desktop (JVM)

Para cada plataforma, recoge sus versiones mínimas (minSdk Android, deployment target iOS, JVM target) — preferentemente en la misma tanda de preguntas.

### 5.2 Arquitectura

```
Que estructura de modulos quieres seguir?
1. Clean Architecture KMM completa: app + features/ + core/
2. Monolitica: shared/ unico
3. Custom (describe)
```

Opcion 1 es la recomendada por `kb-kmm-clean-architecture`.

### 5.3 DI

```
Que sistema de DI vas a usar?
1. Koin (recomendado, alineado con kb-plan-koin / kb-tasks-koin)
2. Kodein
3. Manual (sin framework)
4. Aun no decidido
```

### 5.4 Networking

```
Stack HTTP:
1. Ktor (recomendado, alineado con kb-kmm-http-ktor)
2. Otro
3. Sin networking de momento
```

Si Ktor o otro: preguntar URLs base y si habra contenido JSON con kotlinx-serialization.

### 5.5 Auth

```
Auth:
1. Keycloak / OAuth (alineado con kb-kmm-auth-oauth-keycloak)
2. Custom token-based
3. Sin auth
```

Si Keycloak: preguntar IDS_BASE_URL, realm, client_id, grant types.

### 5.6 Storage

```
Persistencia local:
1. DataStore Preferences (recomendado para clave-valor, kb-tasks-kmm-datastore-preferences)
2. SQLDelight (para datos relacionales)
3. Ambos
4. Sin storage local de momento
```

### 5.7 Recursos y UI text

```
Compose Resources:
1. Si, con localizacion multi-idioma (kb-kmm-resources)
2. Si, monolingue
3. No por ahora
```

### 5.8 Navegacion

```
Navegacion:
1. Compose Navigation (kb-kmm-navigation-compose)
2. Decompose
3. Custom
4. Aun no decidido
```

### 5.9 Testing

```
Estrategia de testing inicial:
1. Pirámide completa (unit + integration + screenshot Roborazzi)
2. Solo unit tests por ahora
3. Sin tests inicialmente
```

### 5.10 Brands / Environments

```
Multi-brand o multi-environment?
1. Si — multi-brand y multi-environment
2. Solo multi-environment (pre, pro, etc.)
3. Single brand / single env
```

Si 1 o 2: preguntar brands y environments concretos.

---

## Paso 6: Componer `kmm_project_state.md`

Estructura del archivo:

```markdown
# KMM Project State

> Generado por `wf-kmm-init`. Actualizar con `wf-kmm-init --force` o ediciones puntuales si cambia el stack.

## Metadata

- Modo de generacion: detect | configure
- Fecha: <ISO-8601>
- Stack: KMM

## Targets

<seccion>

## Arquitectura

<seccion>

## DI

<seccion>

## Networking

<seccion>

## Auth

<seccion>

## Storage

<seccion>

## Recursos

<seccion>

## Navegacion

<seccion>

## Testing

<seccion>

## Brands / Environments

<seccion>

## Build commands

<seccion>

## Notas y desviaciones detectadas

<solo en modo detect: hallazgos del kmm-explorer sobre contradicciones con kb-kmm-*>
```

En **modo detect**, el cuerpo de cada seccion lo aporta el agente `kmm-explorer`.
En **modo configure**, el cuerpo de cada seccion se sintetiza a partir de las respuestas del usuario, marcando como `<pendiente de setup>` lo que aun no se ha configurado en codigo.

Escribir el resultado en el path indicado por `--output` o `kmm_project_state.md` en la raiz del proyecto.

---

## Paso 7: Registrar el run en `.sdd/stack-runs.jsonl`

El registro de ejecuciones del init es un **log append-only**, no un array dentro de `project-init.json` (eso garantizaba conflicto de merge entre devs sobre un fichero de config compartido). Añade una línea JSON al final de `.sdd/stack-runs.jsonl` (crea el archivo si no existe; `mkdir -p .sdd` antes). **Nunca reescribas líneas anteriores** — solo se añade al final.

Timestamp real: ejecuta `date -u +%Y-%m-%dT%H:%M:%SZ` y usa SU salida.

```
echo '{"workflow":"wf-kmm-init","stack":"kmm","mode":"detect|configure","executed_at":"<salida de date -u>","output":"<path de kmm_project_state.md>"}' >> .sdd/stack-runs.jsonl
```

(Un objeto JSON compacto por línea — formato JSON Lines. El `>>` en modo append es seguro ante escrituras concurrentes de líneas cortas.)

`project-init.json` no se toca aquí. Si no existe `.sdd/project-init.json`, registra el run igual en el log y avisa al usuario de que el flujo recomendado es invocar primero `wf-project-init`.

---

## Paso 8: Informe final

Reportar al usuario:

- Modo ejecutado (detect / configure / re-init con `--force`)
- Path del `kmm_project_state.md` generado
- Resumen de las secciones rellenadas
- En modo detect: principales hallazgos o desviaciones detectadas
- En modo configure: piezas marcadas como `<pendiente de setup>` y workflows recomendados para completarlas:
  - Networking → `wf-kmm-network-setup`
  - Auth Keycloak → `wf-kmm-auth-setup-keycloak`
  - Stack compuesto → `wf-kmm-stack-setup-ktor-keycloak-koin`
  - DataStore → `wf-kmm-datastore-setup`
  - Environments → `wf-kmm-environments`
  - Testing → `wf-kmm-testing-setup`
- Recordatorio: todos los agentes KMM (`kmm-explorer`, `kmm-planner`, implementadores) leen `kmm_project_state.md` al inicio si existe.
