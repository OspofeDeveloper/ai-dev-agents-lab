# CU-1 — Inicializar un proyecto SDD

**Objetivo:** verificar que, al abrir un proyecto, el sistema decide correctamente el
modo de trabajo (wizard SDD/libre), inicializa el ecosistema según el perfil de quien
arranca, repara instalaciones a medias, avisa de versiones viejas sin bloquear, y
encuentra los marcadores hacia arriba en un monorepo.
**Proyecto a usar:** un repo/carpeta real **FUERA del repo del ecosistema** (p. ej.
`~/sdd-pruebas/mi-proyecto/`): uno **nuevo o virgen** para el wizard de modo, y aparte
uno ya en SDD que manipules para `init-pending`/`init-incomplete`/`version-drift`.
**Cobertura automática:** el hook está muy cubierto por `sdd/tests/test_session_hook.py`
y los installers por `test_install_sh.py` / `test_setup_sh.py`. Lo que prueban a mano
estos escenarios es la **conducta del agente** ante cada directiva (presentar el
wizard antes de nada, invocar el init, no autoaprobar el modo).

> [!CAUTION]
> **CU-1 no se puede probar dentro del repo del ecosistema.** El hook
> `bootstrap/sdd-session-check.sh` calcula el git toplevel del propio ecosistema (vía
> `~/.sdd-home`) y **se silencia** en cualquier sesión bajo él. Para ver el wizard,
> usa un **proyecto real en un directorio externo** y abre Claude Code ahí. Atajo para
> iterar sin wizard: `cd <proyecto> && bash <repo>/sdd/install.sh all`.

---

## CU-1.a — Configuración SDD vs libre en un proyecto virgen

**Precondición:** proyecto virgen, sin `.sdd/project-init.json` ni `.claude/sdd-mode.json`.
**Mecanismo:** hook `SessionStart` `bootstrap/sdd-session-check.sh` → directiva
`[SDD-PROTOCOL] mode-undecided` → bloque de protocolo en `~/.claude/CLAUDE.md`.

1. Abres Claude Code en el directorio de proyecto virgen.
   → **Esperado:** el agente presenta el wizard de modo con `AskUserQuestion`
     ("Modo SDD" / "Modo libre") **ANTES** de atender ninguna petición.

**Resultado:** PASS si aparece el wizard antes de cualquier otra cosa · FALLO si no
pregunta, o atiende tu petición sin preguntar.
**Desviación → reportar:** issue citando `CU-1.a`.

## CU-1.b — Elegir "Modo SDD" arranca el init

**Precondición:** wizard de modo presentado (CU-1.a).
**Mecanismo:** bloque de protocolo → escribe `.claude/sdd-mode.json` → invoca el skill
`wf-project-init` (subagente: orquestador del propio skill, `context: fork`).

1. Eliges "Modo SDD".
   → **Esperado:** se crea `.claude/sdd-mode.json` con `{"mode":"sdd",…}` y a
     continuación se invoca `wf-project-init`, que **entrevista por perfil**
     (desarrollo / producto / diseño / personalizado) antes de instalar nada.
2. Completas la entrevista.
   → **Esperado:** instala siempre el backbone (`spec`, `plan`, `tasks`) y añade
     `prd`/`design` según perfil y tipo; escribe `.sdd/project-init.json` (con
     `phases`, `profiles` como array, `artifacts`, `sdd_version`…), genera el
     `.claude/CLAUDE.md` raíz, y si el perfil es **desarrollo** con stack concreto
     despacha a `wf-<stack>-init`.

**Resultado:** PASS si escribe el JSON de modo, entrevista por perfil e instala el
backbone + lo que el perfil decida · FALLO si instala sin preguntar el perfil, o no
escribe `project-init.json`.
**Desviación → reportar:** issue citando `CU-1.b`.

## CU-1.c — Elegir "Modo libre" silencia SDD para siempre

**Precondición:** wizard de modo presentado (CU-1.a).
**Mecanismo:** bloque de protocolo → escribe `.claude/sdd-mode.json` modo `free`.

1. Eliges "Modo libre".
   → **Esperado:** se crea `.claude/sdd-mode.json` con `{"mode":"free",…}` y la sesión
     continúa con normalidad.
2. Abres una sesión nueva en el mismo proyecto.
   → **Esperado:** el hook lee `mode: free` y **no vuelve a mencionar SDD** (sin
     wizard, sin init).

**Resultado:** PASS si escribe el JSON `free` y no vuelve a preguntar · FALLO si
reinstala, o vuelve a presentar el wizard en sesiones posteriores.
**Desviación → reportar:** issue citando `CU-1.c`.

## CU-1.d — Modo SDD marcado pero init no completado (`init-pending`)

**Precondición:** existe `.claude/sdd-mode.json` con `mode: sdd` pero **no** existe
`.sdd/project-init.json`.
**Mecanismo:** hook → directiva `[SDD-PROTOCOL] init-pending`.

1. Abres Claude Code en ese proyecto.
   → **Esperado:** el agente invoca `wf-project-init` **directamente**, sin repetir el
     wizard de modo.

**Resultado:** PASS si arranca el init sin re-preguntar el modo · FALLO si repite el
wizard, o ignora el init pendiente.
**Desviación → reportar:** issue citando `CU-1.d`.

## CU-1.e — Init a medias: fases declaradas no instaladas (`init-incomplete`)

**Precondición:** `.sdd/project-init.json` declara fases (p. ej. `design`) cuyos
ficheros de instalación no están presentes.
**Mecanismo:** hook → directiva `[SDD-PROTOCOL] init-incomplete`.

1. Abres Claude Code en ese proyecto.
   → **Esperado:** el agente invoca `wf-project-init` en modo **"Completar / ampliar"**
     para reparar las fases que faltan, **antes** de atender tu petición, y sin repetir
     el wizard de modo.

**Resultado:** PASS si repara las fases ausentes sin re-entrevistar de cero · FALLO si
ignora el hueco, o rehace todo el init.
**Desviación → reportar:** issue citando `CU-1.e`.

## CU-1.f — Instalación de versión anterior (`version-drift`)

**Precondición:** `.sdd/sdd-version.json` declara una versión/commit anterior a la del
ecosistema (`$SDD_HOME/VERSION`).
**Mecanismo:** hook → directiva `[SDD-PROTOCOL] version-drift` (**solo informativa**).

1. Abres Claude Code en ese proyecto y pides algo normal.
   → **Esperado:** el agente menciona **en una línea** que puedes actualizar con
     `/wf-sdd-update` cuando te convenga, y **atiende tu petición con normalidad**. No
     actualiza sin que lo pidas ni repite el aviso en la misma sesión.

**Resultado:** PASS si avisa en una línea, no bloquea y no actualiza solo · FALLO si
bloquea la petición, o actualiza sin pedírselo, o repite el aviso.
**Desviación → reportar:** issue citando `CU-1.f`.

## CU-1.g — Sesión abierta en un subdirectorio (monorepo)

**Precondición:** los marcadores (`.sdd/`, `.claude/sdd-mode.json`) viven en un
**ancestro** (la raíz del proyecto), y abres la sesión en un subpaquete.
**Mecanismo:** hook → búsqueda de marcadores hacia arriba, con techo en el git toplevel
(`_sdd_find_up`).

1. Abres Claude Code dentro de un subpaquete del monorepo.
   → **Esperado:** el hook encuentra los marcadores en el ancestro más cercano (sin
     pasar del git root) y trata el proyecto como **ya inicializado** — no presenta el
     wizard ni reinicializa el subpaquete.

**Resultado:** PASS si reconoce la instalación del ancestro · FALLO si vuelve a
preguntar el modo o intenta inicializar el subpaquete por su cuenta.
**Desviación → reportar:** issue citando `CU-1.g`.

## CU-1.h — El perfil decide qué se instala

**Precondición:** proyecto virgen; eliges "Modo SDD" (CU-1.b).
**Mecanismo:** `wf-project-init` (entrevista por perfil).

1. Inicializas con perfil **producto**.
   → **Esperado:** instala backbone + `prd`, **omite `design`** y deja la config
     técnica (stack) pendiente; `phases` no incluye `design`.
2. Inicializas con perfil **diseño**.
   → **Esperado:** instala `design` **siempre**, sin pedir framework de stack.
3. Inicializas con perfil **desarrollo** sobre un proyecto con stack detectable.
   → **Esperado:** entrevista técnica, registra el `stack` y despacha a
     `wf-<stack>-init` al cerrar.

**Resultado:** PASS si el set de fases instaladas coincide con el perfil elegido ·
FALLO si instala fases que el perfil omite, o salta la entrevista técnica en
desarrollo.
**Desviación → reportar:** issue citando `CU-1.h`.

## CU-1.i — Topología consumer: repo que consume specs de un SSoT

**Precondición:** un repo técnico (server/app/web) que **no** aloja sus specs; los specs viven
en otro repo SSoT del que tienes un checkout local (sibling `../<repo>` o submodule con
`features/` o `*_features.md`).
**Mecanismo:** `wf-project-init` perfil **dev** → pregunta de topología (Paso 5.0b). `consumer` →
salta PRD/Diseño/Artefactos; instala **solo `plan` y `tasks`**; escribe `artifacts_source` +
`artifacts_source_pin` en `project-init.json` (no la clave `artifacts`).

1. Inicializas con perfil desarrollo y eliges **"Consume specs de otro repo"**; das el path al checkout del SSoT.
   → **Esperado:** valida que el path existe y contiene specs; instala `phases: ["plan","tasks"]`
     (sin prd/spec/design), crea `features/` y escribe `artifacts_source` + `artifacts_source_pin`
     (commit corto del SSoT) en `project-init.json`. El `CLAUDE.md` raíz lleva la sección
     **"Topología: repo consumidor"** (specs en solo lectura desde el SSoT).
2. Das un path que **no** contiene specs.
   → **Esperado:** **no** continúa: re-pregunta el path o detiene con instrucciones de clonar el SSoT;
     no inventa una raíz de specs ni instala como standalone.

**Resultado:** PASS si instala solo plan+tasks con `artifacts_source`/pin y exige un SSoT válido ·
FALLO si instala prd/spec/design en un consumer, escribe la clave `artifacts` canónica, o acepta un path sin specs.
**Desviación → reportar:** issue citando `CU-1.i`.

## CU-1.j — Init invocado desde un subpaquete de un monorepo ya inicializado (gate de workflow)

**Precondición:** un monorepo con `.sdd/project-init.json` en la **raíz**; pides el init **desde un
subpaquete** (no es el hook de sesión de `CU-1.g`, sino invocar `wf-project-init` explícitamente).
**Mecanismo:** `wf-project-init` Paso 3.0 — busca marcadores hacia arriba hasta el git toplevel; si
el `sdd-root` es un **ancestro distinto del cwd**, presenta `AskUserQuestion`.

1. Le pides inicializar/configurar SDD estando dentro del subpaquete.
   → **Esperado:** detecta que la raíz ya tiene SDD y pregunta **"Operar desde la raíz `<sdd-root>`"** /
     **"Inicializar aquí (subproyecto independiente)"** — **no** inicializa anidado por su cuenta.
2. Eliges "Operar desde la raíz".
   → **Esperado:** se detiene e indica `cd <sdd-root>` y relanzar el init desde ahí; no escribe nada en el subpaquete.

**Resultado:** PASS si pregunta antes de anidar y respeta la raíz · FALLO si inicializa el subpaquete
sin preguntar, o ignora la instalación del ancestro.
**Desviación → reportar:** issue citando `CU-1.j`.

## CU-1.k — Verificación bloqueante: un init sin fases instaladas es un init FALLIDO

**Precondición:** tenías una petición pendiente (una consulta normal) al arrancar el init; el install
de alguna fase declarada **no** dejó su `.claude/rules/sdd-<fase>.md`.
**Mecanismo:** `wf-project-init` Paso 9 (verificación obligatoria) — el workflow es **BLOQUEANTE**.

1. Completas la entrevista y el init llega al Paso 9 con un check en FALLO (fase declarada sin instalar).
   → **Esperado:** **no** da el init por terminado ni atiende tu petición pendiente: reporta el FALLO,
     corrige (re-ejecuta `install.sh <fase>`) y re-verifica hasta tener todos los checks en verde.
2. Pides que atienda tu consulta original mientras el init sigue incompleto.
   → **Esperado:** mantiene el bloqueo — un init con fases declaradas no instaladas no se considera completado.

**Resultado:** PASS si bloquea hasta verificación en verde y no atiende la petición pendiente ·
FALLO si declara el init terminado con checks en FALLO, o atiende la petición dejando fases sin instalar.
**Desviación → reportar:** issue citando `CU-1.k`.

## CU-1.l — `profiles` es acumulativo entre perfiles (producto → desarrollo)

**Precondición:** un proyecto inicializado antes por un PM con perfil **producto**
(`project-init.json` con `profiles: ["product"]`); ahora entra desarrollo a completar la entrevista técnica.
**Mecanismo:** `wf-project-init` `MODE=extend`, Paso 8 — `profiles` es **unión** (orden de aparición,
sin duplicar), nunca sobrescritura; back-compat migra `profile` (string) → `profiles` (array).

1. Reinicializas eligiendo **"Completar / ampliar"** con perfil **desarrollo**.
   → **Esperado:** `profiles` pasa a `["product","dev"]` (unión, sin perder `product`); completa la
     entrevista técnica pendiente (stack) sin re-preguntar lo ya conocido. Re-correr el mismo perfil
     deja la lista igual (unión idempotente).
2. (back-compat) el `project-init.json` previo trae la clave legacy `profile: "product"` (string singular).
   → **Esperado:** al reescribir el JSON **migra** a `profiles: [...]` y **elimina** la clave `profile`;
     no quedan ambas a la vez.

**Resultado:** PASS si acumula perfiles sin sobrescribir y migra el legacy · FALLO si deja `profiles`
solo con el último perfil, o conserva `profile` y `profiles` simultáneamente.
**Desviación → reportar:** issue citando `CU-1.l`.

## CU-1.m — Ubicación de artefactos no canónica (carpeta propia del proyecto)

**Precondición:** un proyecto que ya tiene una carpeta propia candidata para una fase (p. ej. `specs/`
o `docs/specs/`).
**Mecanismo:** `wf-project-init` Paso 3d (detección de candidatas) + 5.7 (pregunta por fase) + Paso 6
(ajuste del frontmatter `paths:` de `.claude/rules/sdd-<fase>.md`).

1. Inicializas; el init detecta la carpeta candidata.
   → **Esperado:** pregunta dónde deben vivir los artefactos de esa fase ("Usar `<candidata>`" /
     "Usar la canónica (`<fase>/`)") y guarda la elección en el mapa `artifacts` de `project-init.json`.
2. Eliges la carpeta **no canónica** (p. ej. `specs/`).
   → **Esperado:** `artifacts.spec` apunta a `specs/` y el init **edita el glob de directorio** de la
     regla (`"spec/**"` → `"specs/**"`); los globs por nombre de artefacto (`**/*_spec.md`) **no** se tocan.

**Resultado:** PASS si registra la ruta elegida y ajusta solo el glob de directorio de la regla · FALLO
si ignora la candidata, o deja la regla apuntando al directorio canónico que no se usa.
**Desviación → reportar:** issue citando `CU-1.m`.
