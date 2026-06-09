<!-- >>> SDD-BOOTSTRAP >>> (gestionado por setup.sh del ecosistema SDD — no editar a mano) -->
# Protocolo SDD de inicio de sesión

Un hook `SessionStart` (`~/.claude/hooks/sdd-session-check.sh`) comprueba el estado SDD del proyecto al iniciar cada sesión y, cuando procede, inyecta una directiva `[SDD-PROTOCOL]` en contexto. Actúa así según la directiva recibida:

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

## Directiva `[SDD-PROTOCOL] version-drift`

La instalación SDD del proyecto es de una versión anterior a la del ecosistema. Es **solo informativa y nunca bloquea**: menciona en una línea al usuario que puede actualizar con `/wf-sdd-update` cuando le convenga, y atiende su petición con total normalidad. No actualices sin que lo pida explícitamente y no repitas el aviso en la misma sesión.

## Sin directiva

No hagas ninguna comprobación SDD adicional: o el proyecto ya está inicializado (su `.claude/CLAUDE.md` de proyecto define cómo operar), o está en modo libre, o no aplica.

## Modo CI/headless

En runners no interactivos el hook se silencia solo: con `SDD_NON_INTERACTIVE=1` (opt-out explícito) o `CI=true` (estándar de los runners) no emite ninguna directiva — sin wizard, sin init, sin aviso de versión. No apliques tampoco el fallback manual de abajo si detectas esas variables. El opt-out commiteable por repo es `.claude/sdd-mode.json` (modo `free`, o modo `sdd` ya inicializado): viaja en git y vale para cualquier runner o dev sin variables de entorno.

## Opt-out por ruta y desinstalación

El hook admite dos listas opcionales de prefijos de ruta en `~/.claude/` para silenciarlo **sin marcar cada proyecto** (`#` comenta, `~` se expande a tu home, un prefijo por línea):

- `~/.claude/sdd-denylist` — el hook calla en cualquier proyecto que cuelgue de esos prefijos.
- `~/.claude/sdd-allowlist` — si contiene algún prefijo, el hook **solo** actúa dentro de esos prefijos (modo opt-in); fuera, calla.

El opt-out por repo y commiteable sigue siendo `.claude/sdd-mode.json`. Para retirar el bootstrap global por completo: `bash setup.sh --uninstall` (revierte skills globales, hook, `~/.sdd-home` y este bloque; no toca los proyectos).

## Fallback si el hook no está activo

Si no recibes directiva pero tampoco hay evidencia de que el hook se haya ejecutado (p. ej. tras una reinstalación), aplica manualmente esta máquina de estados al inicio de la sesión en un proyecto. En un monorepo los marcadores (`.sdd/`, `.claude/sdd-mode.json`) viven en la raíz del proyecto: si la sesión se abrió en un subpaquete, búscalos **hacia arriba hasta la raíz git** (gana el ancestro más cercano).

1. ¿Existe `.sdd/project-init.json` (aquí o en un ancestro hasta la raíz git)? → proyecto SDD inicializado, opera según su `.claude/CLAUDE.md`.
2. ¿Existe `.claude/sdd-mode.json` con `"mode": "free"`? → sesión normal, no preguntar nunca.
3. ¿Existe `.claude/sdd-mode.json` con `"mode": "sdd"` pero sin `.sdd/project-init.json`? → invoca `wf-project-init`.
4. ¿Nada de lo anterior y el directorio es un proyecto real (no `~`, no el repo del ecosistema SDD)? → wizard de modo de arriba.
<!-- <<< SDD-BOOTSTRAP <<< -->
