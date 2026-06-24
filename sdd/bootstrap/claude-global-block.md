<!-- >>> SDD-BOOTSTRAP >>> (gestionado por setup.sh del ecosistema SDD — no editar a mano) -->
# Protocolo SDD de inicio de sesión

Un hook `SessionStart` (`~/.claude/hooks/sdd-session-check.sh`) comprueba el estado SDD del proyecto al iniciar cada sesión y, cuando procede, inyecta una directiva `[SDD-PROTOCOL]` en contexto. Actúa así según la directiva recibida:

> **Idioma de respuesta.** Responde siempre en el idioma del usuario (por defecto, el de su último mensaje). Manténlo también cuando la sesión arranca con un **slash-command a secas** (p. ej. `/wf-…` sin texto): en ese caso no hay mensaje del usuario al que anclarse y es fácil derivar a inglés — usa el idioma del proyecto/conversación, no el del andamiaje del comando.

## Directiva `[SDD-PROTOCOL] mode-undecided`

ANTES de atender la primera petición del usuario, presenta el wizard de modo con la herramienta `AskUserQuestion` (nunca como pregunta de texto libre):

```
question: "Este proyecto no tiene configurado el modo de trabajo de Claude. ¿Cómo quieres usarlo?"
header: "Modo Claude"
opciones:
  - label: "Modo SDD"
    description: "Inicializa el ecosistema SDD (Spec Driven Development): pipeline PRD → Spec → Design → Plan → Tasks con skills y agentes especializados"
  - label: "Modo libre"
    description: "Claude funciona con normalidad en este proyecto, sin instalar nada. No se volverá a preguntar"
```

Según la respuesta:

- **Modo SDD** → escribe `.claude/sdd-mode.json` (creando `.claude/` si no existe) con:
  ```json
  { "mode": "sdd", "decided_at": "<date -u +%Y-%m-%dT%H:%M:%SZ>", "decided_by": "sdd-session-protocol" }
  ```
  y a continuación invoca el skill `wf-project-init` (vía Skill tool), que inicializa todo el ecosistema y escribe `.sdd/project-init.json`.
- **Modo libre** → escribe `.claude/sdd-mode.json` con:
  ```json
  { "mode": "free", "decided_at": "<date -u +%Y-%m-%dT%H:%M:%SZ>", "decided_by": "sdd-session-protocol" }
  ```
  y continúa la sesión con total normalidad. No vuelvas a mencionar SDD en este proyecto salvo que el usuario lo pida explícitamente.

## Directiva `[SDD-PROTOCOL] init-pending`

El proyecto está en modo SDD pero la inicialización no se completó (no existe `.sdd/project-init.json`). Invoca el skill `wf-project-init` directamente, sin repetir el wizard de modo.

## Directiva `[SDD-PROTOCOL] init-incomplete`

El proyecto declara fases en `.sdd/project-init.json` que no están instaladas (un init anterior se quedó a medias). Invoca `wf-project-init` (opción "Completar / ampliar") para reparar ANTES de atender la petición del usuario. No repitas el wizard de modo.

## Directiva `[SDD-PROTOCOL] specialist-init-pending`

El proyecto tiene un stack con overlay instalado, pero su **init técnico** (`wf-<stack>-init`, p. ej. `wf-kmm-init`) aún no se ha ejecutado (no hay registro en `.sdd/stack-runs.jsonl`). Ese init produce el estado técnico del stack que los agentes de plan/tasks/implementación leen al arrancar. Es una **precondición contextual, nunca bloqueante** — el nombre exacto del workflow viene en la directiva (y en `specialist_workflow` de `.sdd/project-init.json`):

- Si la petición es de **PRD, spec o diseño** (o conversacional): **no lo lances**. Menciónalo en **una línea** (p. ej. "ℹ El init técnico del stack `<stack>` está pendiente; lo lanzo cuando pasemos a planificar/implementar") y atiende la petición con total normalidad.
- **Antes** de cualquier trabajo de **stack** —generar o validar plan, generar o ejecutar tasks, o implementar código— invoca `wf-<stack>-init` (vía Skill tool) como precondición, y **solo entonces** continúa con lo que pidió el usuario.
- El usuario puede forzarlo cuando quiera con `/wf-<stack>-init`.

No repitas el wizard de modo. En cuanto `wf-<stack>-init` registra su run en `.sdd/stack-runs.jsonl`, el hook deja de emitir esta directiva.

## Directiva `[SDD-PROTOCOL] version-drift`

La instalación SDD del proyecto es de una versión anterior a la del ecosistema. Es **solo informativa y nunca bloquea**: menciona en una línea al usuario que, **cuando le convenga, puede pedirte que actualices el proyecto** — y atiende su petición con total normalidad. **No le des el comando crudo (`/wf-sdd-update`)**: si te lo pide, **tú** invocas `wf-sdd-update` vía la Skill tool (así evitas que el usuario lance el slash-command a secas, que pierde contexto e idioma). No actualices sin que lo pida explícitamente. Preséntalo **una vez** como aviso de una línea; un recordatorio suave posterior (p. ej. en un bloque de notas final) no es problema, pero **no lo re-emitas como una preocupación nueva ni bloqueante**.

## Petición explícita de inicializar / configurar SDD

Cuando el usuario pida **inicializar, configurar, arrancar, preparar o reinstalar SDD** en este repo o directorio —con CUALQUIER frasing: "inicializa este proyecto", "configura SDD aquí", "arranca el init", "inicializa SDD en este directorio"— **invoca SIEMPRE el skill `wf-project-init` vía la Skill tool**. La intención es invariante al wording: "este proyecto", "este directorio" y "aquí" son lo mismo; no enrutes distinto según la palabra elegida.

**No resuelvas el estado de init por tu cuenta.** No hagas `find-up` ni `cat`/`Read` de `.sdd/project-init.json` para concluir tú mismo "ya está inicializado" y responder con una tabla de estado: esa decisión es **exclusiva de `wf-project-init`**, que tras su detector distingue de forma determinista:

- **cwd ya inicializado** (`init_found` en el cwd) → ofrece "Completar / ampliar" · "Rehacer" · "Dejar como está";
- **subpaquete de un monorepo cuya raíz ya tiene SDD** (`sdd_root_is_ancestor: true`, `init_found: false` en el cwd) → gate "Operar desde la raíz" · "Inicializar aquí (subproyecto)";
- **instalación nueva** → entrevista de topología.

Que un **ancestro** tenga `.sdd/` **no** equivale a que **este** directorio esté inicializado: aun así, delega en el skill — él presenta el gate de subpaquete. La única excepción es el modo CI/headless de abajo.

## Sin directiva

No hagas ninguna comprobación SDD adicional: o el proyecto ya está inicializado (su `.claude/CLAUDE.md` de proyecto define cómo operar), o está en modo libre, o no aplica. **No anuncies el modo SDD en el chat** (ni "estás en modo libre", ni "este proyecto usa SDD"): el indicador de modo es la **status line** (`⚙ SDD:…`), no la conversación. Atiende la petición del usuario directamente.

## Modo CI/headless

En runners no interactivos el hook se silencia solo: con `SDD_NON_INTERACTIVE=1` (opt-out explícito) o `CI=true` (estándar de los runners) no emite ninguna directiva — sin wizard, sin init, sin aviso de versión. No apliques tampoco el fallback manual de abajo si detectas esas variables. El opt-out commiteable por repo es `.claude/sdd-mode.json` (modo `free`, o modo `sdd` ya inicializado): viaja en git y vale para cualquier runner o dev sin variables de entorno.

## Opt-out por ruta y desinstalación

El hook admite dos listas opcionales de prefijos de ruta en `~/.claude/` para silenciarlo **sin marcar cada proyecto** (`#` comenta, `~` se expande a tu home, un prefijo por línea):

- `~/.claude/sdd-denylist` — el hook calla en cualquier proyecto que cuelgue de esos prefijos.
- `~/.claude/sdd-allowlist` — si contiene algún prefijo, el hook **solo** actúa dentro de esos prefijos (modo opt-in); fuera, calla.

El opt-out por repo y commiteable sigue siendo `.claude/sdd-mode.json`. Para retirar el bootstrap global por completo: `bash setup.sh --uninstall` (revierte skills globales, hook, `~/.sdd-home` y este bloque; no toca los proyectos).

## Fallback si el hook no está activo

Si no recibes directiva pero tampoco hay evidencia de que el hook se haya ejecutado (p. ej. tras una reinstalación), aplica manualmente esta máquina de estados al inicio de la sesión en un proyecto. En un monorepo los marcadores (`.sdd/`, `.claude/sdd-mode.json`) viven en la raíz del proyecto: si la sesión se abrió en un subpaquete, búscalos **hacia arriba hasta la raíz git** (gana el ancestro más cercano).

1. ¿Existe `.sdd/project-init.json` (aquí o en un ancestro hasta la raíz git)? → proyecto SDD inicializado, opera según su `.claude/CLAUDE.md`. Además, si ese `project-init.json` tiene `specialist_workflow` no nulo y **no** hay una línea para él en `.sdd/stack-runs.jsonl`, aplica la directiva `specialist-init-pending` de arriba (precondición contextual del trabajo de stack; no bloquea PRD/spec/design). **Esta regla decide si el proyecto cuenta como inicializado para no repetir el wizard de modo en peticiones normales; NO te autoriza a responder a mano una petición explícita de init** (sobre todo desde un subpaquete donde el `.sdd/` está en un ancestro pero el cwd no está inicializado): para eso aplica «Petición explícita de inicializar / configurar SDD» y delega en `wf-project-init`, que presentará el gate de subpaquete.
2. ¿Existe `.claude/sdd-mode.json` con `"mode": "free"`? → sesión normal, no preguntar nunca **ni anunciar el modo en el chat** (la status line lo muestra).
3. ¿Existe `.claude/sdd-mode.json` con `"mode": "sdd"` pero sin `.sdd/project-init.json`? → invoca `wf-project-init`.
4. ¿Nada de lo anterior y el directorio es un proyecto real (no `~`, no el repo del ecosistema SDD)? → wizard de modo de arriba.
<!-- <<< SDD-BOOTSTRAP <<< -->
