---
name: kb-plan-method
description: Procedimiento operativo compartido de la fase plan SDD — los pasos de generar un Plan (plan-architect) y de auditarlo (plan-auditor), stack-agnósticos. Es el núcleo metodológico que cargan las variantes genérica y de overlay de los agentes; cada una solo aporta su capa de especialización de stack sobre los hooks marcados aquí.
effort: low
user-invocable: false
allowed-tools: [Read]
---

# Plan Method — Procedimiento compartido de la fase plan

Esta KB es el **procedimiento metodológico común** de los agentes de la fase `plan`:
la **Sección A** (producir un Plan) la sigue `plan-architect`; la **Sección B** (auditar
un Plan) la sigue `plan-auditor`. Ambas son **idénticas en cualquier stack** — lo que
cambia entre el modo genérico y un overlay (KMM, etc.) es solo el contenido de los
**hooks de especialización**, que el cuerpo del agente rellena.

> SSoT de la metodología de agente: vive aquí, no duplicada en cada `agents/*.md`.
> Las reglas normativas del Plan (qué debe contener, taxonomía de gaps, deuda técnica,
> estados, regla canónica de Design) viven en `kb-plan-expert`; esta KB es el *cómo
> operar*, no el *qué es válido*.

## Hooks de especialización de stack

Donde este procedimiento dice **‹especialización de stack›**, el cuerpo del agente
aporta el detalle concreto:

- **Modo genérico (stack agnóstico)**: el repositorio manda. Fundamenta cada decisión en
  la estructura, lenguaje, frameworks y convenciones ya presentes en el repo; no impongas
  capas, librerías ni patrones que el repo no use; si el repo no da evidencia suficiente
  para cerrar una decisión necesaria, es `TECH_GAP`/`PLAN_GAP`, no invención.
- **Overlay de stack**: el cuerpo del agente declara la arquitectura prescriptiva del stack
  (capas, módulos, librerías, convenciones) como **default del stack**. Pero **el repo
  destino manda sobre el dogma**: si el repositorio real ya resuelve algo de otra forma —otra
  librería de DI, otro tipo de resultado, otra organización de módulos— se respeta lo que el
  repo hace (capturado en `<stack>_project_state.md`) y se justifica en el Plan. El canon del
  stack rellena los huecos donde el repo no se ha pronunciado (greenfield); **no sobrescribe
  convenciones divergentes ya presentes**. Imponer el canon del stack sobre un repo que
  diverge es el mismo fallo que inventar en modo genérico.

El procedimiento, la taxonomía de gaps, los estados y el formato del artefacto **no
cambian** entre modos (contrato de overlay, `kb-sdd-stack-overlay-contract`).

---

# Sección A — Producir un Plan (generate-plan)

## Entrada que recibes
- Contenido completo del `_spec.md`
- Path del archivo origen
- Contenido de `DESIGN.md`, `*_flows.md` y `*_views.md` cuando la feature tiene UI o navegación

Tu único modo es **generate-plan**: producir un `_plan.md` nuevo en estado `BORRADOR` a
partir de un Spec validado y el handoff de Design cuando aplique.

## Proceso

**1. Carga y respeta el handoff de Design cuando exista**

Si el prompt incluye `DESIGN.md`, `*_flows.md` o `*_views.md`:
- trátalos como fuentes normativas para UI, navegación y accesibilidad
- no reinventes journeys, pantallas ni estados visuales que ya estén cerrados ahí
- si hay contradicción entre spec y design, devuelve `DESIGN_GAP`

Si la feature tiene UI visible pero el prompt no trae estos artefactos, devuelve
`DESIGN_GAP` en lugar de inferir.

**2. Extrae todos los CAs del Spec**

Lista todos los Criterios de Aceptación. Son tu contrato: el Plan debe cubrir cada uno
sin excepción.

**3. Identifica las entidades de dominio**

Para cada concepto funcional mencionado en el Spec (usuario, oferta de trabajo, servicio,
turno, ausencia...) → un modelo de dominio. Los nombres deben ser funcionales, no técnicos.
La nomenclatura de capa concreta y dónde vive el modelo lo define ‹especialización de stack›.

**3.5. Verifica Shared Models (solo si el prompt incluye esa sección)**

Si el prompt contiene una sección "Shared models del proyecto":
- Los modelos listados en esa tabla **no se redefinen** en este Plan.
- Si esta feature es la **owner** del modelo → defínelo completamente con todos sus campos.
- Si esta feature **referencia** el modelo (no es owner) → en la tabla de Modelos escribe:
  ```
  | NombreModelo | — | Definido en: <feature-owner>_plan.md | CA-XXX |
  ```
  No repitas los campos, no copies la definición. Solo declara la referencia.
- Nunca crear un modelo con el mismo nombre que uno en la tabla de shared models aunque
  parezca "ligeramente distinto".

**4. Mapea las acciones a unidades de comportamiento**

Para cada acción principal del usuario que tenga un CA dedicado → una unidad de
comportamiento (la forma concreta — caso de uso, servicio, UseCase... — la define
‹especialización de stack›).

Regla:
- si dos CAs pertenecen al mismo flujo y comparten trigger → pueden ser la misma unidad
- si son flujos distintos → unidades distintas

**5. Diseña la estructura técnica**

Para cada unidad de comportamiento, define cómo se obtienen, transforman y persisten los
datos (¿datos remotos? ¿persistencia local? ¿ambas, y por tanto una estrategia de caché?).
Para cada Journey del Spec con surface UI, define los componentes de presentación necesarios.

La topología concreta (qué capas, qué componentes, qué nombres) la prescribe
‹especialización de stack›.

Si el prompt incluye `*_flows.md` y `*_views.md`:
- usa esos artefactos para decidir pantallas, transiciones y ownership de navegación
- refleja el handoff en la sección `Handoff desde Design`
- documenta semantic primitives, test tooling a11y y constraints técnicos derivados del diseño

**6. Detecta dependencias de plataforma**

Si algún CA requiere una API de plataforma específica (biometría, notificaciones push,
almacenamiento seguro, GPS) → documenta la dependencia y cómo se resuelve. El mecanismo
concreto (expect/actual u otro) lo define ‹especialización de stack›.

**7. Detecta gaps normativos**

Usa exclusivamente la taxonomía de `kb-plan-expert` (`DESIGN_GAP`, `TECH_GAP`,
`TRACE_GAP`, `PLAN_GAP`):
- `DESIGN_GAP`: bloqueo en el handoff visual o contradicción entre design y spec.
- `TECH_GAP`: ambigüedad funcional en el Spec que impide tomar una decisión técnica concreta.
- `TRACE_GAP`: CA sin cobertura o trazabilidad rota que no puedes resolver sin cambiar el contrato del plan.
- `PLAN_GAP`: falta una sección, ownership o contrato técnico necesario para que el plan sea entregable.

Si hay `DESIGN_GAPs`, `TECH_GAPs`, `TRACE_GAPs` o `PLAN_GAPs` → lista todos con
descripción y detén. No produzcas el Plan parcialmente.

**7b. Distingue gap de deuda técnica (no toda incertidumbre bloquea)**

Antes de emitir un `TECH_GAP`, aplica el **test de admisión de deuda** de `kb-plan-expert`
(sección "Deuda técnica asumida"). Es **deuda `TD-00X`** — no gap — cuando: (1) existe un
camino técnico viable prescriptible hoy; (2) no contradice el Spec; (3) el riesgo es
acotado y enunciable. Frontera **QUÉ vs CÓMO**: duda funcional → `TECH_GAP` (bloquea);
duda técnica con camino viable (módulo legacy sin tests, API opaca, librería sin doc) →
propón `TD-00X` y **continúa el Plan**. Regístrala en `## Deuda técnica asumida` con todos
los campos y **siempre `Aprobada por: PENDIENTE`** (tú propones, el humano aprueba en
`wf-plan-validate`). Ante la duda entre gap y deuda, es gap.

**8. Verifica la trazabilidad**

¿Cada CA tiene al menos un componente del Plan que lo implementa?
Si un CA no tiene cobertura y no es un gap → es un olvido → añade el componente faltante.

**9. Produce el Plan**

Si no hay gaps:
- produce el Plan usando la plantilla de `kb-plan-expert/references/plan_structure.md`
- rellena todos los campos obligatorios: stack, estructura técnica, dominio, datos,
  presentación y trazabilidad
- rellena `Handoff desde Design` **solo si** la regla canónica determina que `Design` es
  obligatorio para esta feature
- incluye la sección `## Deuda técnica asumida` **solo si** registraste alguna `TD-00X` en
  el paso 7b (con `Aprobada por: PENDIENTE`); si no hay deuda, omite la sección
- fija `Estado: BORRADOR`
- si el spec de entrada declara metadata como `derived_from_prd`, `derived_from_prd_version`,
  `derived_from_change` o `status_sync`, propágala al header del Plan
- si falta metadata, usa `unknown` de forma explícita en lugar de omitir el campo

## Regla de oro (producir)

> Cada componente del Plan existe porque un CA del Spec o un handoff normativo de Design
> lo requiere. Si un componente no traza a un CA o a una decisión cerrada de Design, es
> especulación — no va en el Plan.

---

# Sección B — Auditar un Plan (validate-plan)

## Entrada que recibes
- Contenido completo del `_plan.md` a auditar
- Contenido del `_spec.md` origen
- Contenido de `DESIGN.md`, `*_flows.md` y `*_views.md` cuando el plan declara `Handoff desde Design`
- Contenido de `_features.md` si existe, para auditar shared models

No rediseñas el contenido arquitectónico del Plan. Solo auditas si lo que está escrito es
correcto, completo y trazable.

## Proceso de auditoría

**Check 1: Trazabilidad**
¿Cada CA del Spec tiene al menos un componente del Plan que lo implementa? Usa el Checklist
de Trazabilidad del Plan como punto de partida; verifica que no haya CAs omitidos.

**Check 2: Completitud Técnica**
¿Los elementos obligatorios del Plan están presentes y completos? El conjunto y nombre
concreto de secciones de estructura lo define ‹especialización de stack›.

**Check 2b: Handoff desde Design (solo si el Plan declara esa sección)**
- ¿El Plan refleja los journeys y pantallas de `*_flows.md` y `*_views.md`?
- ¿La accesibilidad está materializada como decisiones técnicas en la presentación?
- ¿Hay contradicciones con `DESIGN.md`? Si las hay, son `DESIGN_GAP`.

**Check 3: Independencia de Implementación**
¿El Plan puede entregarse a un desarrollador para implementar sin tomar decisiones
arquitectónicas adicionales?

**Check 4: Shared Models**
Si hay `_features.md`, ¿el Plan respeta la tabla de shared models sin redefinir modelos
cuyo owner es otra feature?

**Check 5: Deuda técnica asumida (solo si el Plan declara la sección)**
Para cada `### TD-00X` de `## Deuda técnica asumida`, verifica contra el test de admisión
de `kb-plan-expert`:
- ¿Es realmente deuda (CÓMO, camino viable, riesgo acotado) y **no un gap funcional
  disfrazado**? Si la "decisión" deja sin determinar un comportamiento que el Spec exige →
  es `TECH_GAP`, no deuda: degrádala a gap en tu reporte.
- ¿Están todos los campos completos y `Queda pendiente` es accionable (no vago)?
- La aprobación (`Aprobada por`) la gestiona el humano en `wf-plan-validate`; tú no
  apruebas deuda. Pero sí señalas si una TD no debería existir como deuda.

## Output

Si el Plan supera todos los checks:
- Devuelve `OK` con un resumen breve: número de CAs cubiertos, secciones verificadas,
  estado objetivo `VALIDADO`.

Si el Plan tiene hallazgos bloqueantes:
- Devuelve un reporte usando el formato de `kb-plan-expert` "Formato de output para revisiones".
- Incluye al final un bloque normalizado con estas cuatro líneas exactas para persistir en
  el `_plan.md`:

```
**DESIGN_GAPs:** [ninguno | descripción]
**TECH_GAPs:** [ninguno | descripción]
**TRACE_GAPs:** [ninguno | descripción]
**PLAN_GAPs:** [ninguno | descripción]
```

Usa solo la taxonomía de `kb-plan-expert`: `DESIGN_GAP`, `TECH_GAP`, `TRACE_GAP`, `PLAN_GAP`.

## Regla de oro (auditar)

> Auditas lo que está escrito en el Plan, no lo que el Plan podría haber sido.
> Si un componente existe pero no traza a ningún CA, es especulación — regístralo como `TRACE_GAP`.
> Si un CA existe pero no tiene componente, es una omisión — regístralo como `TRACE_GAP`.
