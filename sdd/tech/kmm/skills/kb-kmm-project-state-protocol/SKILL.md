---
name: kb-kmm-project-state-protocol
description: "Protocolo de precondicion de contexto tecnico para agentes KMM. Define la obligacion de leer kmm_project_state.md al inicio de la operacion si existe, el bloqueo con mensaje de error estandar si no existe, la excepcion unica para kmm-explorer invocado por wf-kmm-init en modo detect, el contrato de cierre verificable de los agentes implementadores (build y tests con los comandos del project state, reporte honesto), y la precedencia del repo real (project_state) sobre el canon KMM por defecto. SSoT del protocolo compartido por kmm-explorer, kmm-planner, kmm-feature-logic-implementer, kmm-feature-ui-implementer, kmm-platform-integrator, kmm-network-auth-implementer y kmm-tester."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KB KMM Project State Protocol

Esta KB es la SSoT del protocolo de precondicion de contexto tecnico para agentes KMM. Cualquier agente del stack KMM que opere sobre un proyecto real debe respetar estas reglas antes de razonar sobre la peticion.

`kmm_project_state.md` es el snapshot del estado tecnico del proyecto (targets, arquitectura, DI, networking, auth, storage, variants, navegacion, testing, build commands). Lo genera `wf-kmm-init` (directamente o via `wf-project-init`). Sin ese archivo, los agentes KMM no tienen contexto suficiente para emitir un diagnostico, un plan o una implementacion alineada con el proyecto.

## Regla 1: Precondicion obligatoria de lectura

Antes de procesar cualquier peticion, todo agente KMM debe comprobar si existe `kmm_project_state.md` en la raiz del proyecto.

1. Si existe, el agente debe leerlo completo antes de iniciar su trabajo.
2. El contenido leido se usa como contexto de fondo para todo el razonamiento posterior: ownership, ubicacion de piezas, decisiones de arquitectura, eleccion de stack, validaciones cruzadas.
3. El diagnostico, plan o implementacion del agente debe alinearse con el estado descrito. Si la peticion entra en conflicto con ese estado, el agente debe sennalarlo explicitamente antes de proceder.

## Regla 2: Bloqueo si no existe `kmm_project_state.md`

Si `kmm_project_state.md` no existe en la raiz del proyecto, el agente debe detener su operacion y responder al usuario con este mensaje estandar:

> "No encuentro `kmm_project_state.md` en la raiz del proyecto. Necesito el estado tecnico del proyecto antes de operar. Ejecuta primero `/wf-project-init` (o `/wf-kmm-init` si ya sabes que el stack es KMM) para generarlo."

El agente no debe:

- intentar inferir el estado del proyecto explorando el filesystem por su cuenta
- continuar con asunciones por defecto sobre targets, arquitectura o stack
- proponer un plan o implementacion sin haber leido el archivo

El bloqueo es duro: el unico desbloqueo valido es que el usuario ejecute el init.

## Regla 3: Excepcion unica para `kmm-explorer` invocado por `wf-kmm-init` en modo detect

Existe una sola excepcion al bloqueo de la Regla 2: cuando `kmm-explorer` es invocado por `wf-kmm-init` en modo `detect`, el archivo todavia no existe porque el trabajo del agente *es* generarlo.

Condiciones de la excepcion:

- el invocador es `wf-kmm-init` (no el orquestador directamente, no otro workflow)
- el modo es `detect` (no `configure`)
- el workflow pasa la instruccion explicita de explorar para producir el contenido de `kmm_project_state.md`

Cuando se cumplen las tres condiciones, `kmm-explorer` procede sin bloquear: explora el filesystem, diagnostica la arquitectura y devuelve el contenido al workflow, que se encarga de escribir el archivo.

Fuera de esta excepcion, `kmm-explorer` se comporta como el resto de agentes KMM y aplica el bloqueo de la Regla 2.

## Regla 4: Quien debe aplicar el protocolo

El protocolo aplica a todos los agentes del stack KMM que operan sobre el proyecto del usuario:

- `kmm-explorer` (con la excepcion de la Regla 3)
- `kmm-planner`
- `kmm-feature-logic-implementer`
- `kmm-feature-ui-implementer`
- `kmm-platform-integrator`
- `kmm-network-auth-implementer`
- `kmm-tester`

No aplica a los workflows `wf-*` del stack KMM: los workflows orquestan y delegan; son los agentes los que necesitan el contexto tecnico para razonar.

## Regla 5: Esta KB es la SSoT del protocolo

Cualquier mencion del protocolo en agentes, workflows o documentacion debe referenciar esta KB y no reescribir las reglas inline. Si se detecta una copia inline del protocolo en otro archivo:

1. Sustituirla por una referencia corta a `kb-kmm-project-state-protocol` (por ejemplo, "Aplica el protocolo de precondicion de `kb-kmm-project-state-protocol`").
2. Mantener solo el mensaje de bloqueo de la Regla 2 si el agente lo emite literalmente; el resto del protocolo se delega a esta KB.

Cambios futuros en el mensaje, la lista de agentes afectados o las condiciones de excepcion se hacen aqui primero y se propagan a los consumidores.

## Regla 6: Contrato de cierre verificable (agentes implementadores)

Aplica a los agentes que modifican codigo: `kmm-feature-logic-implementer`, `kmm-feature-ui-implementer`, `kmm-platform-integrator`, `kmm-network-auth-implementer` (y a `kmm-tester` cuando escribe tests). Una implementacion NO esta terminada hasta cumplir este contrato:

1. **Build y tests ejecutados de verdad.** Antes de declarar el trabajo hecho, compila los modulos afectados y ejecuta la suite relevante usando los comandos de build/test declarados en `kmm_project_state.md`. Si la seccion de comandos no existe o esta incompleta, usa `./gradlew` con los targets estandar del modulo afectado y sennala la laguna del project state.
2. **El resultado esperado depende del orden TDD.** En una task `Layer: test` con DoD RED, el cierre correcto es: el test compila y FALLA con mensaje claro (verde prematuro = fallo de DoD). En el resto de casos, el cierre correcto es build verde y suite pasando.
3. **Reporte honesto, siempre.** El reporte de cierre incluye el comando ejecutado y un resumen real de su salida. Si el build falla o hay tests rojos no esperados, se reporta tal cual y el trabajo queda como NO terminado — esta prohibido declarar "compila" o "los tests pasan" sin haberlos ejecutado, y prohibido maquillar un fallo como exito parcial.
4. **Ausencia de verificacion = declaracion explicita.** Si no hay forma razonable de ejecutar nada (entorno sin toolchain, sandbox sin gradle), el cierre debe decir literalmente "verificacion ejecutable: no disponible — <motivo>". Nunca presentar como verificado lo que no se ejecuto. Si el `kmm_project_state.md` declara `tests: none` o un `build:` degradado, ese es el `<motivo>` valido y no se exige suite verde inexistente — la degradacion generica del cierre verificable (incluida la guia characterization-first) vive en `kb-sdd-stack-overlay-contract`, "Estado de tooling degradado".

Este contrato es la contraparte dentro del agente de lo que `wf-task-run` (Paso 6) y `wf-bug` (Paso 4) exigen desde fuera: ambos lados deben coincidir. El criterio generico para cualquier stack vive en `kb-sdd-stack-overlay-contract` (invariante de cierre verificable); esta regla es su concrecion KMM.

## Regla 7: El repo real (project_state) manda sobre el canon KMM

`kmm_project_state.md` captura las convenciones REALES de ESTE repo: que libreria de DI usa, que tipo de resultado, como organiza los modulos, que stack HTTP, como maneja recursos y navegacion. El canon KMM por defecto (Koin, `AppResult<T, AppError>`, `compose-resources`, Clean Architecture por capas `app/features/core`, navegacion por contrato...) es el **default del stack para greenfield o donde el project_state no se pronuncia** — no una imposicion.

Cuando el `kmm_project_state.md` declara una convencion distinta del canon, **manda el project_state** (= el repo real). Ejemplos:

- el repo usa Hilt o inyeccion manual en vez de Koin → se respeta lo del repo; no se impone Koin
- el repo usa `Result`/`Either`/excepciones en vez de `AppResult` → se respeta lo del repo
- el repo organiza los modulos de otra forma (monolitico, por capas distintas) → el plan/tasks siguen esa organizacion real
- el repo usa recursos Android `R.*` en un target unico → no se fuerza `compose-resources`

Aplica a TODOS los agentes KMM, incluidos los implementadores: antes de prescribir o escribir codigo con el canon, comprueba que el `kmm_project_state.md` no declare otra cosa. Imponer el dogma KMM sobre un repo que ya resuelve algo de otra forma es un defecto — el mismo principio anti-imposicion que rige el modo generico ("el repo manda"). El canon solo rellena los huecos donde el repo no tiene opinion. Si el project_state no captura una dimension necesaria y el repo tampoco da evidencia, es `TECH_GAP`, no licencia para imponer el canon.

Criterio generico (cualquier overlay) en `kb-sdd-stack-overlay-contract`; metodo de plan/tasks en `kb-plan-method` / `kb-tasks-method` (hook "Overlay de stack").
