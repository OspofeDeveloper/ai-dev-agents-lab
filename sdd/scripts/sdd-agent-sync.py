#!/usr/bin/env python3
"""Gate PreToolUse sobre la tool `Agent`: la delegacion a un agente SDD es sincrona.

Se registra como hook PreToolUse (matcher: Agent) en el settings.json del
proyecto, hermano de `sdd-gate-check.py` (matcher: Skill). Deniega una llamada
`Agent` a un subagente DEL ECOSISTEMA que no pase `run_in_background: false`.

POR QUE EXISTE (D-048)
----------------------
Desde Claude Code v2.1.198 los subagentes corren en BACKGROUND por defecto.
D-043 respondio prescribiendo `run_in_background: false` en el cuerpo de las
skills que delegan. Medido en CU-3.a pasada 4, con el flag escrito en las cinco
prescripciones de `wf-spec-features-first`: viajo en 0 de 10 llamadas `Agent`.
Cero. En tres skills distintas.

La conducta no fue mala — el orquestador cedio el turno y consumio el informe de
la notificacion de fin, sin sondear el disco (por eso D-047 sanciona esa via).
Pero deja el ecosistema dependiendo de que el modelo sostenga a mano la barrera
del fan-out: lanzar N delegados y no continuar hasta tener las N notificaciones.
Eso es exactamente el tipo de garantia que D-043 dio por buena mirando el
`tool_use` sin mirar el `tool_result`, y que resulto no serlo.

La leccion acumulada de D-038/D-042/D-043/D-045 es la misma: la prosa no es
enforcement. Cuando una propiedad IMPORTA, hay que hacerla mecanica. Este hook
convierte "pasa el flag" de aspiracion a hecho: si falta, la llamada se deniega
con el motivo, y el modelo reintenta con el flag.

RELACION CON D-047 (no se contradicen)
--------------------------------------
D-047 dice que esperar es que TE ENTREGUEN el informe, y sanciona dos vias: el
`tool_result` de la llamada, o la notificacion de fin. Eso define que cuenta como
FALLO de conducta. Este hook no cambia esa definicion: elimina la ambiguedad en
el ORIGEN, forzando la via (a) siempre que se pueda. La via (b) sigue siendo la
red de seguridad — para proyectos sin el hook instalado, o con el desactivado.

ALCANCE: SOLO AGENTES DEL ECOSISTEMA
------------------------------------
`SDD_AGENTS` es una lista cerrada. Un `Agent` a `general-purpose`, `Explore` o a
un agente propio del usuario NO se toca. El ecosistema se instala en repos ajenos
y no le corresponde forzarle el modo de ejecucion a los agentes de nadie — mismo
motivo por el que D-045 descarto `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, que
habria apagado el background de TODO el repo.

DOS MENSAJES, NO UNO (D-049)
----------------------------
Un gate SIN ESTADO que responde lo mismo a un reintento corregido le esta ensenando
al modelo que el gate esta roto. Medido en CU-3.a pasada 5: el agente corrigio bien
—anadio el parametro— pero lo paso como la cadena "false"; el gate devolvio el
mensaje identico las tres veces, y el agente concluyo (razonablemente) que el
contrato era incumplible. Por eso hay dos motivos distintos: uno para "falta el
parametro" y otro para "esta, pero el valor no es el booleano". Cada reintento tiene
que producir informacion NUEVA, o el modelo no puede converger.

ESCOTILLA
---------
`SDD_ALLOW_ASYNC_AGENTS=1` desactiva el gate por completo. Existe porque un gate
que no se puede apagar es un gate que puede dejar un repo inoperable: si algun
dia el harness deja de aceptar el parametro, denegar en bucle bloquearia el
pipeline entero sin via de escape.

Politica conservadora, igual que `sdd-gate-check.py`: solo se deniega con
evidencia POSITIVA (subagente SDD conocido + flag ausente o distinto de false).
stdin ilegible, tool distinta, `subagent_type` ausente o desconocido, o
cualquier excepcion interna -> se PERMITE y se sale 0. El gate es una red de
seguridad, no un validador de toda la sintaxis.
"""
import json
import os
import sys

# Agentes del ecosistema SDD (los de `*/agents/*.md` + overlays de stack).
# Un subagent_type fuera de esta lista es del usuario o del harness: no se toca.
SDD_AGENTS = frozenset({
    # meta
    "sdd-author", "sdd-auditor", "sdd-conformance",
    # prd
    "prd-expert",
    # spec
    "sdd-spec-explorer", "sdd-spec-planner", "sdd-spec-writer", "sdd-spec-auditor",
    # design
    "design-system-architect", "design-feature-architect",
    # plan / tasks / qa
    "plan-architect", "plan-auditor", "task-generator", "qa-engineer",
    # overlay kmm
    "kmm-explorer", "kmm-planner", "kmm-tester", "kmm-platform-integrator",
    "kmm-network-auth-implementer", "kmm-feature-logic-implementer",
    "kmm-feature-ui-implementer",
})

_COMUN = (
    "Asi el informe del delegado te llega dentro del `tool_result` de tu propia "
    "llamada, en vez de tener que ceder el turno y sostener tu la barrera "
    "(D-043/D-047/D-048). Si delegas a varios en paralelo, emite TODAS las llamadas "
    "en un unico mensaje: con el flag, ese mensaje no vuelve hasta que han terminado "
    "todas, y esa es la barrera que el paso siguiente necesita. No cambies de "
    "estrategia ni reconstruyas el resultado por tu cuenta."
)

# Falta el parametro.
REASON_AUSENTE = (
    "[SDD-SYNC] Delegacion asincrona a `{agent}`. Las delegaciones a agentes del "
    "ecosistema SDD son SINCRONAS: vuelve a llamar a `Agent` con exactamente los "
    "mismos `subagent_type`, `prompt` y `description`, anadiendo "
    "`run_in_background: false` — el booleano `false`, sin comillas. " + _COMUN +
    " Solo faltaba el parametro."
)

# El parametro esta, pero con un valor que NO es el booleano false (D-049).
# Mensaje DISTINTO a proposito: un gate sin estado que responde lo mismo a un
# reintento corregido le ensena al modelo que el gate esta roto. Medido en CU-3.a
# pasada 5: el reintento llego con la cadena "false", el gate devolvio el mensaje
# identico, y a los tres intentos el agente concluyo —razonablemente— que el
# contrato era incumplible, y publico como causa una limitacion del entorno que
# nunca comprobo.
REASON_TIPO = (
    "[SDD-SYNC] Valor incorrecto. Has pasado `run_in_background` a `{agent}` con el "
    "valor {valor}, y tiene que ser `run_in_background: false` — el **booleano** "
    "`false`, sin comillas: no la cadena \"false\", ni 0, ni \"no\". Es lo unico que "
    "falta: repite la MISMA llamada cambiando solo eso. " + _COMUN
)


def main() -> int:
    if os.environ.get("SDD_ALLOW_ASYNC_AGENTS") == "1":
        return 0

    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # stdin ilegible -> no interferir

    try:
        if payload.get("tool_name") != "Agent":
            return 0
        tool_input = payload.get("tool_input") or {}
        if not isinstance(tool_input, dict):
            return 0

        agent = tool_input.get("subagent_type")
        if not isinstance(agent, str) or agent.strip() not in SDD_AGENTS:
            return 0  # agente del usuario o del harness -> no es asunto nuestro

        # Denegar solo con evidencia positiva: el flag no esta puesto al booleano
        # false. Ausente == background por defecto, que es justo lo que se corrige.
        #
        # `is False` es a proposito: `0 == False` en Python, y un 0 no expresa la
        # peticion de primer plano. Tampoco se acepta la cadena "false": no sabemos
        # que hace el harness con un string donde espera un booleano (si lo coacciona
        # a truthy, el subagente seguiria yendo a background) y permitirlo seria
        # sancionar una llamada asincrona creyendo lo contrario. Se exige el booleano
        # y se dice con precision que falta.
        valor = tool_input.get("run_in_background")
        if valor is False:
            return 0

        if "run_in_background" in tool_input:
            reason = REASON_TIPO.format(agent=agent.strip(), valor=repr(valor))
        else:
            reason = REASON_AUSENTE.format(agent=agent.strip())

        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))
    except Exception:
        return 0  # error interno del gate -> nunca bloquear el pipeline
    return 0


if __name__ == "__main__":
    sys.exit(main())
