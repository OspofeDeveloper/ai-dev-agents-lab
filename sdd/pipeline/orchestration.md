# Disciplina de orquestación SDD (transversal)

Principios que gobiernan **cómo se avanza entre fases** del pipeline SDD, independientes de la fase concreta. A diferencia de las guías de fase (`sdd-<fase>.md`, que cargan al tocar sus artefactos), esta disciplina debe estar presente **antes de tocar ningún fichero**: se aplica al orientar ("¿cuál es el siguiente paso?"), al recomendar una fase o al enrutar una petición.

> **Audiencia.** El **hilo principal (orquestador)** aplica esta disciplina al mapear la petición del usuario y al decidir el siguiente paso. Un **subagente especialista** que la herede la lee como **contexto de proyecto** (invariantes del pipeline), no como una instrucción de rol: su contrato de trabajo es su propio system prompt + sus `kb-*`.

## Readiness antes de avanzar: mecánica, no por topología

- El estado de una fase **no se decide a ojo ni por la topología de ficheros**: que una carpeta de la siguiente fase esté vacía **no** significa "toca esa fase", y "he terminado de mirarlo" **no** es "está aprobado".
- **No se declara una fase "lista" ni se avanza a la siguiente sin la evidencia del verificador mecánico** de esa frontera (autor≠verificador). Si existe un script de readiness para la frontera, se ejecuta y se cita su veredicto; si no está en estado listo, se surfacea el motivo y se remite al paso que lo cierra —no se avanza en silencio.

## Orden del pipeline

- Cada fase consume artefactos **listos/sellados** de la anterior (PRD → Spec → Design → Plan → Tasks). Ante una petición fuera de orden, el hilo principal redirige al paso pendiente en vez de saltárselo.

## Los gates son de su fase; no se bypasean

- Los workflow skills tienen sus propias validaciones de precondición. **No se bypasean.** Si un skill reporta bloqueos o pendientes, el hilo principal los comunica al usuario y espera a que los resuelva antes de reintentar.
- **Los overrides `--allow-*` los arma el usuario, nunca el hilo principal ([[D-026]]).** Los flags de escape (`--allow-unreviewed-prd`, `--allow-open-critical-gaps`, `--allow-derived-scope-from-analysis`, …) desactivan un gate de seguridad; **no** se auto-suministran ni se infieren de una petición impaciente ("genérame ya las specs" **no** es "asumo alcance no revisado"). Ante una precondición que un `--allow-*` cruzaría: invoca el skill **sin** el override → el gate se detiene y **devuelve el bloqueo al hilo principal** → surfacéalo y **presenta la elección explícita con `AskUserQuestion`** (p. ej. *revisar/cerrar primero* vs. *continuar asumiendo el riesgo*) → **solo** re-invoca con el `--allow-*` si el usuario elige forzar. Auto-armar el flag es un bypass en espíritu: el gate nunca llega a reportar el bloqueo. Mismo principio que [[D-024]]/[[D-025]]: interrumpir para que el usuario decida conscientemente lo de alto impacto, sin re-confirmar lo que ya dijo.

## Comunicación con el usuario

- Los nombres de skill (`wf-*`) y los slash-commands (`/wf-…`) son **internos**: sirven para invocar, no para mostrárselos al usuario. Lo que se comunica al usuario se describe en **lenguaje natural** —"reviso el PRD contigo", "genero las specs por feature", "audito el diseño"—, no con nombres de workflow ni comandos con argumentos.
- El motivo: si se surfacea `/wf-x <args>`, el usuario cree que debe teclear comandos y puede pasar argumentos a mano, saltándose la construcción de argumentos que hace el hilo principal (donde viven las validaciones). El ecosistema es **agnóstico a comandos**: se conduce por conversación.
- Excepción: si el usuario pide explícitamente el nombre técnico o el comando ("¿qué workflow es?", "dame el comando"), se le da sin problema.
