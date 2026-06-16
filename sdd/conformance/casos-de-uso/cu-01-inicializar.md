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

## Modelo de cobertura — qué ejes del wizard hay que probar y cuáles no

El wizard de `wf-project-init` tiene varios ejes (perfil, PRD, tipo, framework, rigor,
topología…). El producto cartesiano de sus valores es grande, pero **no todos los ejes
cambian lo que se instala**. CU-1 prueba **ramas de decisión**, no combinaciones de
valores: un eje solo merece un caso por rama si **cambia el set de fases instaladas o el
flujo de preguntas**. Si solo se persiste en `project-init.json`, basta un único caso
parametrizado que verifique que el valor elegido aterriza.

**Ejes que cambian comportamiento (behavior-changing) — un caso por rama.** La columna
"Cobertura" es honesta: `✓` cubierto, `parcial` rama no aseverada explícitamente, `—` sin caso.

| Eje | Pregunta | Qué ramifica | Cobertura |
|---|---|---|---|
| Perfil | 5.0 | qué fases opcionales (prd/design) y si hay entrevista técnica | `✓` dev/product/design (CU-1.h); custom (CU-1.o) |
| PRD sí/no | 5.1 | antepone (o no) la fase `prd` | `✓` (CU-1.h, CU-1.n) |
| Topología | 5.0b (solo dev) | `consumer` instala solo `plan`+`tasks` y usa `artifacts_source` | `✓` (CU-1.i) |
| Tipo (en perfil **dev**) | 5.2 | gatea 5.3 (design para app/web; omitido en backend/other) y 5.4 (framework para app) | `✓` (CU-1.o) |
| Framework | 5.4 (dev+app) | deriva el `stack` y gatea 5.5 (targets) | `✓` (CU-1.o) |
| Carpetas candidatas | 5.7 | gatea la pregunta de ubicación de artefactos | `✓` (CU-1.m) |
| Init previo | 3b | extend / rehacer / dejar; acumulación de perfiles | `✓` (CU-1.d, CU-1.e, CU-1.l) |
| Monorepo (marcadores en ancestro) | 3.0 | operar desde la raíz vs anidar | `✓` (CU-1.g, CU-1.j) |
| Modo libre previo | 3a | confirmar conversión a SDD | `✓` (CU-1.c) |

**Ejes que solo se registran (recorded-only) — un único caso parametrizado (CU-1.n).** No
cambian el install; solo escriben un campo en `project-init.json`.

| Eje | Pregunta | Dónde aterriza | Qué NO cambia |
|---|---|---|---|
| Rigor | 5.8 | `pipeline_mode` (`standard`\|`light`) | el set de fases instaladas (los gates anti-alucinación son idénticos en ambos modos) |
| Tipo (en perfil **product**/**design**, sin entrevista técnica) | 5.2 | `type` | nada instalado: design se omite (5.3) y `stack` queda `null` (5.6) sea cual sea el tipo |

> **Implicación práctica:** `producto/prd/app/standard`, `producto/prd/web/ligero`,
> `producto/prd/backend/standard`… **instalan exactamente lo mismo**. La tupla de valores
> no multiplica los casos: solo los ejes behavior-changing lo hacen. Para los recorded-only
> basta CU-1.n. El eje `tipo` es la única sutileza: es behavior-changing **en perfil dev**
> (gatea design y framework) pero recorded-only **en product/design**.

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

## CU-1.n — Ejes solo-registrados: `tipo` y `rigor` se persisten sin cambiar el install set

**Precondición:** proyecto virgen; eliges "Modo SDD" y perfil **producto** con PRD. Es el
caso parametrizado que cubre los ejes **recorded-only** de la tabla del "Modelo de cobertura"
(no hace falta un caso por cada combinación tipo×rigor).
**Mecanismo:** wizard 5.2 (Tipo) + 5.8 (Pipeline) → escritura de `project-init.json` (Paso 8).
En perfil producto, `tipo` no gatea 5.3 (design) ni 5.4 (framework), y `rigor` solo fija
`pipeline_mode`.

1. Inicializas el mismo perfil (producto + PRD) **dos veces** variando solo estos dos ejes:
   una con **App + Standard**, otra con **Web + Ligero**.
   → **Esperado:** ambos inits instalan **el mismo set de fases** (`prd, spec, plan, tasks`,
     **sin `design`**) y dejan `stack: null` (entrevista técnica pendiente). La única
     diferencia entre los dos `project-init.json` son dos campos: `type` (`app` vs `web`) y
     `pipeline_mode` (`standard` vs `light`).
2. Inspeccionas el `project-init.json` de cada uno.
   → **Esperado:** `type` y `pipeline_mode` reflejan **exactamente** lo elegido; `phases` es
     **idéntico** entre ambos; ningún otro campo cambia por efecto de tipo o rigor.
3. (negativo) Repites el de **Web + Ligero** pero esta vez vuelves a elegir **App + Standard**.
   → **Esperado:** salvo `type`/`pipeline_mode`, el resultado es indistinguible del primer
     init — cambiar estos ejes nunca añade ni quita fases.

**Resultado:** PASS si el valor elegido se persiste verbatim y el set instalado es invariante
a tipo/rigor en perfil producto · FALLO si cambiar tipo o rigor altera las fases instaladas o
el `stack`, o si el valor elegido no aterriza en `project-init.json`.
**Desviación → reportar:** issue citando `CU-1.n`.

## CU-1.o — Tipo y framework SÍ ramifican en perfil dev/custom; perfil `custom`

**Precondición:** proyecto virgen; eliges "Modo SDD". Cierra las ramas que CU-1.h dejaba en
`parcial`/`—` (ver "Modelo de cobertura"): el gate de **design por tipo** en perfil dev, las
ramas de **framework** (incluido el gate de targets), y el perfil **`custom`**.
**Mecanismo:** wizard 5.2 (Tipo) → gatea 5.3 (Diseño) y 5.4 (Framework); 5.4 → deriva `stack`
y gatea 5.5 (Targets); 5.6 (derivar stack); tabla 5.3 (perfil×tipo) y tabla 5.6 (perfil→stack).

**A — `tipo` gatea la pregunta de diseño en perfil dev.**
1. Inicializas perfil **dev** + tipo **App**.
   → **Esperado:** aparece la pregunta de **Diseño** de 3 opciones (5.3) **y** la de
     **Framework** (5.4). Eliges crear diseño → `design` entra en `phases`.
2. Inicializas perfil **dev** + tipo **Backend** (u **Otro software**).
   → **Esperado:** **NO** aparece la pregunta de Diseño (5.3 la omite) **ni** la de Framework
     (5.4 es solo dev+app); `phases` no incluye `design`; `stack` = detectado o `agnostico`,
     nunca `null` (en dev sí hay entrevista técnica).

**B — las ramas de framework derivan stack distinto y gatean targets.**
3. Inicializas perfil **dev** + tipo **App** + framework **Compose Multiplatform** (o **Flutter**).
   → **Esperado:** aparece **5.5 Targets** (multiSelect Android/iOS/Desktop, mínimo uno);
     `stack` = `kmm` (o `flutter`); `targets` se persiste en `project-init.json`.
4. Inicializas perfil **dev** + tipo **App** + framework **Android (Nativa)** (o **iOS Nativa**).
   → **Esperado:** **NO** aparece 5.5 Targets (no es multiplataforma); `stack` = `android` (o
     `ios`); la clave `targets` se **omite** del JSON.

**C — perfil `custom` se comporta como dev en design pero deja el stack pendiente.**
5. Inicializas perfil **custom** + tipo **Web**.
   → **Esperado:** aparece la pregunta de **Diseño** de 3 opciones (5.3 trata custom como dev),
     pero **NO** la de Framework (5.4 es solo dev) y **NO** entrevista técnica; `stack` = `null`
     (5.6: custom → pendiente, lo completará desarrollo con "Completar / ampliar"). Distíngalo de
     dev+web, donde `stack` sería `agnostico`/detectado, no `null`.

**Resultado:** PASS si el set de preguntas que aparecen y el `stack`/`targets`/`phases`
resultantes coinciden con las tablas 5.3/5.4/5.6 para cada combinación · FALLO si pregunta
design/framework donde la tabla los omite (o al revés), deriva un stack que no corresponde al
framework, o deja `stack: null` en un perfil dev (o `agnostico` en custom).
**Desviación → reportar:** issue citando `CU-1.o`.

## CU-1.p — Los argumentos honran y saltan preguntas (por usuario o por orquestador)

**Precondición:** proyecto virgen.
**Mecanismo:** `wf-project-init` Paso 1 (`$ARGUMENTS`) + Paso 5 regla 2 ("no preguntar lo que
ya se sabe"). Los args llegan **tecleados** (`/wf-project-init <flags>`) o vía el campo `args`
del Skill tool cuando invoca el **orquestador** (p. ej. desde el hook de sesión o una petición
en lenguaje natural). Ambas vías son equivalentes.

1. `/wf-project-init --profile product --type web`.
   → **Esperado:** NO pregunta perfil ni tipo (los da por conocidos, a lo sumo confirma); la
     entrevista sigue solo con lo que falta (PRD, pipeline). `project-init.json` registra
     `type: web` y perfil `product`.
2. `/wf-project-init --profile dev --type app --stack kmm`.
   → **Esperado:** salta perfil, tipo, framework y targets (stack derivado del flag); va directo
     a lo que falte.
3. (entrada por orquestador) Sin teclear el skill, una petición en lenguaje natural que el
   orquestador mapea a `wf-project-init` pasando `args`.
   → **Esperado:** mismo efecto que tecleado — los flags saltan sus preguntas.
4. (negativo) Un flag con valor fuera del enum (p. ej. `--profile xxx`).
   → **Esperado:** no se traga en silencio — lo ignora y pregunta, o pide un valor válido; nunca
     inicializa con un perfil inexistente.

**Resultado:** PASS si los flags válidos saltan su pregunta y aterrizan en el estado, y un flag
inválido no se acepta · FALLO si re-pregunta algo ya dado por flag, o acepta un valor fuera del enum.
**Nota de testeo:** la entrevista es interactiva (`AskUserQuestion`) → se valida **a mano**. La
parte determinista (detección/verificación) la cubren los unittest de `sdd-init-detect.py`
(`test_sdd_init_detect.py`).
**Desviación → reportar:** issue citando `CU-1.p`.
