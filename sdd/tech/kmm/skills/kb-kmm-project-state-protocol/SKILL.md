---
name: kb-kmm-project-state-protocol
description: "Protocolo de precondicion de contexto tecnico para agentes KMM. Define la obligacion de leer kmm_project_state.md al inicio de la operacion si existe, el bloqueo con mensaje de error estandar si no existe, y la excepcion unica para kmm-explorer cuando es invocado por wf-kmm-init en modo detect (su trabajo es generar el archivo). SSoT del protocolo compartido por kmm-explorer, kmm-planner, kmm-feature-implementer, kmm-platform-integrator, kmm-network-auth-implementer y kmm-tester."
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
- `kmm-feature-implementer`
- `kmm-platform-integrator`
- `kmm-network-auth-implementer`
- `kmm-tester`

No aplica a los workflows `wf-*` del stack KMM: los workflows orquestan y delegan; son los agentes los que necesitan el contexto tecnico para razonar.

## Regla 5: Esta KB es la SSoT del protocolo

Cualquier mencion del protocolo en agentes, workflows o documentacion debe referenciar esta KB y no reescribir las reglas inline. Si se detecta una copia inline del protocolo en otro archivo:

1. Sustituirla por una referencia corta a `kb-kmm-project-state-protocol` (por ejemplo, "Aplica el protocolo de precondicion de `kb-kmm-project-state-protocol`").
2. Mantener solo el mensaje de bloqueo de la Regla 2 si el agente lo emite literalmente; el resto del protocolo se delega a esta KB.

Cambios futuros en el mensaje, la lista de agentes afectados o las condiciones de excepcion se hacen aqui primero y se propagan a los consumidores.
