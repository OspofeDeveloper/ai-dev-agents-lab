# CU-11 — Enrutado por lenguaje natural

**Objetivo:** verificar que el usuario **habla** (nunca teclea `/wf-*`) y el
orquestador acierta el skill o el agente correcto, construye bien los argumentos (rutas
resueltas, flags, modos), y que esos argumentos **sobreviven** el salto orquestador →
workflow → subagente y los gates `PreToolUse` los reciben en el formato que esperan.
**Proyecto a usar:** cualquier proyecto real — transversal: este CU se valida
**mientras ejecutas los demás**, hablando en vez de teclear comandos.
**Cobertura automática:** ninguna — es la parte más dependiente del LLM, se valida a
mano (ROADMAP 11.1). Es el sustrato del playbook 11.6.

> [!IMPORTANT]
> **El orquestador no ejecuta el trabajo ni construye prompts a mano:** mapea tu
> intención al skill/agente correcto y lo activa con los argumentos correctos. La SSoT
> del routing es el rootmap intención→skill→args de `sdd/CLAUDE.md`.

> [!NOTE]
> **CU-11 prueba el *mecanismo* del enrutado; la *matriz exhaustiva* frase→skill (los 50
> workflows + los pares de desambiguación) vive en
> [`cu-13-enrutado-matriz.md`](cu-13-enrutado-matriz.md).**

---

## 🧪 Qué se prueba aquí (por componente)

CU-11 es un **objetivo de usuario** (hablar y que el orquestador acierte y propague bien),
no una sola skill: sus escenarios ejercitan el **orquestador** desde cuatro mecanismos de
enrutado. Marca cada escenario al ejecutarlo. El estado de cobertura autoritativo (ejes
happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) — esta vista es la
**transpuesta** para leer/ejecutar el CU.

### Orquestador — enrutado por lenguaje natural (matching semántico + delegación a agente) (2)
- [ ] CU-11.a — Hablar, no teclear comandos · **sub-caso 2 (narración: no surfacear `wf-*`/comandos, [[D-019]] capa 1) ✓ 2026-07-09** (`myops-app-specs` 0.53.0, 2/2 raíz+subdir: recomienda "revisar el PRD contigo" sin nombrar el skill; la excepción "¿qué comando por dentro?" también PASS — da el nombre y avisa de no teclearlo a mano). Sub-caso 1 (routing NL→skill correcto, features-first vs discover) pendiente
- [ ] CU-11.e — Delegación a agente cuando no hay workflow exacto

### Orquestador — construcción y paso de argumentos (4)
- [ ] CU-11.b — Construcción correcta de argumentos
- [ ] CU-11.f — Los overrides peligrosos NO se inyectan sin petición explícita
- [ ] CU-11.g — Input oral cuando el skill espera un argumento de fichero
- [ ] CU-11.h — Argumentos de selección y multivalor

### Orquestador → workflow (`context: fork`) → sub-workflows / subagente — propagación de args (1)
- [ ] CU-11.c — Los argumentos sobreviven los saltos wf→wf y wf→agente

### Orquestador → hook `PreToolUse` (`sdd-gate-check.py`) — los args llegan al gate (1)
- [ ] CU-11.d — Los gates reciben los args aunque los construya un agente

---

## CU-11.a — Hablar, no teclear comandos

**Precondición:** un proyecto SDD inicializado.
**Mecanismo:** orquestador → matching semántico por las `description` de los skills (eager) + desambiguación de la regla eager `sdd-routing.md` ([[D-022]]); el rootmap-tabla de la regla de fase es solo referencia.

1. Pides algo en lenguaje natural sin nombrar ningún skill ("quiero crear las specs de
   este PRD").
   → **Esperado:** el orquestador mapea la intención al skill correcto
     (`wf-spec-features-first <prd.md>`, no `wf-spec-discover`) y lo invoca; nunca te
     exige teclear `/wf-*`. Variante subset: "solo la fase 1 / estas features" → discover
     primero, pregunta qué IDs, luego features-first `--features`.
   → **De-risk de [[D-022]]:** este sub-caso valida que el enrutado por `description` +
     desambiguación eager basta (habilita el roll-out y el futuro adelgazamiento del
     rootmap). PASS aquí = no hace falta el rootmap-tabla eager.
2. **Narración de salida (handoff agnóstico a comandos, [[D-019]]).** En cualquier
   respuesta al usuario —recomendar el siguiente paso, ofrecer una acción, reportar un
   resultado—, el orquestador **no surfacea proactivamente nombres de skill (`wf-*`) ni
   slash-commands con argumentos**; describe la acción en lenguaje natural ("reviso el
   PRD contigo", "genero las specs por feature").
   → **Esperado:** no aparecen `wf-…`/`/wf-…` en la prosa dirigida al usuario. La
     disciplina vive en la regla eager `sdd-orchestration.md`. Excepción legítima: si el
     usuario pide explícitamente el comando o el nombre técnico, dárselo no es FALLO.

**Resultado:** PASS si (1) acierta el skill desde lenguaje natural y (2) narra sin
surfacear nombres de skill/comando · FALLO si te pide el comando, enruta a un skill
equivocado de la misma fase, o menciona `wf-*`/`/wf-*` al ofrecer/recomendar acciones sin
que se lo hayas pedido.
**Nota:** (2) es capa 1 de D-019 (narración del orquestador); las plantillas de salida de
los propios `wf-*` que aún emiten comandos son la capa 2 (roll-out pendiente).
**Desviación → reportar:** issue citando `CU-11.a`.

## CU-11.b — Construcción correcta de argumentos

**Precondición:** una petición que implica flags o modos.
**Mecanismo:** orquestador → construcción de args según el `argument-hint` del skill.

1. Pides un subset ("genera solo las features 1 y 2").
   → **Esperado:** resuelve la ruta del PRD y construye `--features F-001,F-002`
     (tras el discovery, si los IDs no existían aún — ver `CU-3.c`).
2. Pides un modo concreto ("analiza el impacto", "aplícalo").
   → **Esperado:** elige el modo correcto del skill (`analyze` / `apply` / `generate`)
     y resuelve los paths del artefacto.

**Resultado:** PASS si construye flags/modos/paths coherentes con el skill · FALLO si
omite flags necesarios, o pasa un modo o path inexistente.
**Desviación → reportar:** issue citando `CU-11.b`.

## CU-11.c — Los argumentos sobreviven los saltos wf→wf y wf→agente

**Precondición:** una petición que dispara una pipeline encadenada (p. ej.
`wf-spec-features-first`, que internamente invoca discover y fast-track).
**Mecanismo:** orquestador → workflow (`context: fork`) → sub-workflows / subagente.

1. Lanzas un workflow que delega en otros y en un subagente.
   → **Esperado:** los argumentos (rutas, `--features`, modos) **se propagan** intactos
     a través de los saltos; el subagente recibe el contexto que necesita sin que tú lo
     repitas.

**Resultado:** PASS si los args llegan correctos al final de la cadena · FALLO si se
pierden o se corrompen entre wf→wf o wf→agente.
**Desviación → reportar:** issue citando `CU-11.c`.

## CU-11.d — Los gates reciben los args aunque los construya un agente

**Precondición:** un workflow con gate `PreToolUse` invocado por enrutado natural.
**Mecanismo:** orquestador construye la invocación → hook `PreToolUse` →
`sdd-gate-check.py` resuelve el artefacto del argumento.

1. Hablando, disparas un workflow con gate (p. ej. pides el plan de una feature).
   → **Esperado:** el gate recibe el argumento en el formato que espera (un `.md`
     resoluble) aunque lo haya construido el agente y no un humano; evalúa la
     precondición correctamente (deny o permite según corresponda).

**Resultado:** PASS si el gate resuelve el artefacto y decide bien · FALLO si el gate no
puede leer el argumento por venir mal construido, y permite/bloquea por error.
**Desviación → reportar:** issue citando `CU-11.d`.

## CU-11.e — Delegación a agente cuando no hay workflow exacto

**Precondición:** una petición de exploración/planificación/escritura/auditoría que no
encaja en una workflow cerrada.
**Mecanismo:** orquestador → agente SDD del dominio (p. ej. `sdd-spec-explorer`).

1. Pides algo abierto ("diagnostica en qué estado están mis specs").
   → **Esperado:** al no haber workflow exacto, delega al **agente** cuyo dominio
     coincide (aquí `sdd-spec-explorer`), no fuerza un workflow inadecuado ni lo hace él
     mismo a pelo.

**Resultado:** PASS si elige el agente correcto del dominio · FALLO si fuerza un
workflow que no aplica, o ejecuta el trabajo sin delegar.
**Desviación → reportar:** issue citando `CU-11.e`.

## CU-11.f — Los overrides peligrosos NO se inyectan sin petición explícita

**Precondición:** una petición normal sobre un skill que admite flags de override de
gates o de comportamiento destructivo.
**Mecanismo:** orquestador → construcción de args. Los flags peligrosos
(`--allow-open-critical-gaps`, `--all-features`, `--allow-derived-scope-from-analysis`,
`--dry-run`, `--review-before-apply`, `--no-commit`, `--no-tag`, `--force`) son **opt-in
explícito**: el orquestador no los añade por iniciativa propia.

1. Pides "genera las specs de este PRD" sobre un PRD con gaps `[CRÍTICO]` abiertos.
   → **Esperado:** el orquestador **no** inyecta `--allow-open-critical-gaps`; pide
     decisión explícita (responder los gaps o continuar con el override) — nunca lo decide solo.
2. Pides "propaga el cambio por el pipeline" (cascade normal).
   → **Esperado:** invoca sin `--dry-run` ni `--review-before-apply`; solo los añade si
     dices "solo diagnostica" / "no apliques nada todavía".
3. Pides "ejecuta las tasks" / "releasa la feature".
   → **Esperado:** invoca sin `--no-commit` / sin `--no-tag`; solo los añade si pides
     explícitamente "sin commitear" / "no hagas tag".

**Resultado:** PASS si ningún override aparece sin que lo pidas y el orquestador para a
pedir decisión donde el rootmap lo exige · FALLO si auto-inyecta cualquier flag peligroso,
o salta un gate por su cuenta añadiendo el override.
**Desviación → reportar:** issue citando `CU-11.f`.

## CU-11.g — Input oral cuando el skill espera un argumento de fichero

**Precondición:** un skill cuyo `argument-hint` pide un `.md`, pero describes el contenido
de viva voz sin pasar fichero.
**Mecanismo:** orquestador → resolución del argumento. Algunos skills aceptan texto inline
(`wf-bug <descripcion.md|texto>`, `wf-design-feedback capture <feedback.md|texto>`); otros
exigen un fichero (`wf-prd-change --new-reqs <cambio.md>`).

1. Describes un bug o un feedback de viva voz ("la app crashea al pagar en grupo").
   → **Esperado:** usa la forma de **texto inline** que el skill admite, sin exigirte un `.md`.
2. Describes un cambio de producto de viva voz y el skill exige `--new-reqs <fichero>`.
   → **Esperado:** captura tu descripción a un documento de cambio (o te pide el fichero)
     y lo pasa como `--new-reqs`; **no** falla silenciosamente por falta de argumento ni
     inventa una ruta inexistente.

**Resultado:** PASS si usa texto inline donde se admite y materializa/pide el fichero donde
se exige · FALLO si exige un `.md` que el skill no necesita, o invoca con un `--new-reqs`
apuntando a un fichero que no existe.
**Desviación → reportar:** issue citando `CU-11.g`.

## CU-11.h — Argumentos de selección y multivalor

**Precondición:** una petición que fija una selección concreta (plataformas, tag, task,
variantes, CA).
**Mecanismo:** orquestador → construcción de args multivalor/posicionales según el
`argument-hint`.

1. "exporta los tokens a CSS y Tailwind".
   → **Esperado:** `wf-design-export <DESIGN.md> --platforms css,tailwind` (lista separada
     por comas, solo las pedidas).
2. "releasa la feature con el tag v1.2.0" · "ejecuta solo la task T-003" · "aclara el CA-014".
   → **Esperado:** `--tag v1.2.0` · `--task T-003` · `--ca CA-014` respectivamente, sin
     añadir selección que no pediste (p. ej. no `--all`).

**Resultado:** PASS si construye el valor de selección exacto que pediste · FALLO si exporta
plataformas de más, ignora el tag/task/CA concreto, o amplía la selección por su cuenta.
**Desviación → reportar:** issue citando `CU-11.h`.
