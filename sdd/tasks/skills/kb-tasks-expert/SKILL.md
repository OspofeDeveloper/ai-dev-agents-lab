---
name: kb-tasks-expert
description: Reglas tech-neutral para descomponer Planes técnicos en Tasks atómicas delegables a un owner claro: formato obligatorio de task, granularidad, orden canónico por dependencias, criterios de asignación de owner por dominio de ejecución (agentes del stack si hay overlay, u orquestador en modo agnóstico) y definición de done por task. El overlay de stack especializa la regla de owners mediante una variante con el mismo nombre. No cubre la generación del Plan (kb-plan-expert) ni la validación de Specs (kb-spec-expert).
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Tasks Expert — Coordinador de Implementación SDD

Eres un experto en descomponer Planes técnicos en Tasks atómicas, ordenadas y accionables. Tu trabajo es garantizar que cada Task es delegable a un owner claro sin requerir decisiones adicionales del desarrollador.

---

## ¿Qué es una Task?

Una Task es la **unidad mínima de implementación delegable**: un componente o cambio cohesivo, en un dominio de ejecución concreto, asignado a un owner responsable.

**Regla de oro:** Una Task = Un owner claro.

No modeles la Task en torno a una CLI skill por capa. El punto de ejecución principal es el **owner de la task** (un agente del stack cuando hay overlay, o el orquestador en modo agnóstico).

---

## Lo que una Task DEBE tener (formato obligatorio)

Además del bloque de Tasks individuales, el `_tasks.md` debe llevar un header de trazabilidad mínima con:

- `Plan origen`
- `Spec origen`
- `PRD origen`
- `PRD version`
- `Change ref`
- `Status sync`

```markdown
## T-[número]: [Área] — [Nombre del componente]

- **Estado:** PENDIENTE
- **Spec CA:** [CA-XXX que implementa, o — si no aplica]
- **Plan ref:** [§sección del Plan]
- **Componente:** [módulo, paquete o ruta del repositorio según el Plan]
- **Layer:** [capa lógica según las secciones reales del Plan | test]
- **Execution domain:** [dominio de ejecución según el Plan, o — si no aplica]
- **Owner agent:** [agente del overlay de stack | orquestador en modo agnóstico]
- **Suggested workflow:** [wf-* concreta si existe y aplica | —]
- **Input:** [qué contrato, modelo, pantalla o configuración recibe o crea]
- **Dependencies:** [T-XXX, T-YYY | ninguna]
- **Deuda asumida:** [TD-XXX — título corto | omitir la línea si la task no toca componentes con deuda]
- **Definition of done:** [qué artefactos deben existir o quedar integrados al finalizar]
```

Consulta `${CLAUDE_SKILL_DIR}/references/task_templates.md` para templates por tipo de componente.

**Deuda asumida** (opcional) aparece solo si el Plan declara `## Deuda técnica asumida` y esta task toca un componente listado en los `Componentes afectados` de una `TD-00X`. Es contexto heredado, no editable: el owner implementa **respetando la decisión documentada en el Plan** (no improvisa una solución a la limitación ni la "resuelve" por su cuenta — saldar la deuda es trabajo futuro fuera del alcance de la task). Lo escribe `wf-prepare-tasks` al generar; `sdd-task-state.py` no lo toca.

**Estado** es el campo de ejecución persistente (`PENDIENTE | EN_CURSO | HECHA | BLOQUEADA`). Se genera siempre como `PENDIENTE`. A partir de ahí **solo lo escribe el script determinista** `.sdd/scripts/sdd-task-state.py` (invocado por `wf-task-run`), que valida transiciones y dependencias y regenera la tabla `## Progreso` — nunca se edita a mano. Archivos `_tasks.md` anteriores a este campo se inicializan con `sdd-task-state.py init`.

---

## Lo que una Task NO debe tener

| Elemento prohibido | Dónde pertenece |
|---|---|
| Código fuente | La implementación real |
| Decisiones arquitectónicas nuevas | Plan |
| Scope multi-dominio sin owner claro | Dividir en dos Tasks |
| Scope multi-feature | Tasks separadas por feature |
| Criterios funcionales de negocio | Spec |
| El comando o prompt exacto que usará el orquestador | Capa de ejecución, no la Task |

---

## Regla central: el owner se decide por dominio de ejecución, no por capa aislada

Nunca asumas que una capa lógica (`domain`, `data`, `presentation` o equivalente) implica por sí sola un owner distinto. El owner se decide por la **naturaleza del cambio** y por el **modo de ejecución del proyecto**:

- **(a) Proyecto con overlay de stack**
  El owner es uno de los **agentes del stack**. La variante de esta KB instalada por el overlay especializa esta regla, definiendo el catálogo de agentes y el criterio exacto de asignación por dominio. En este modo, el campo `Owner agent` lleva el nombre del agente del stack responsable.
- **(b) Proyecto agnóstico (sin overlay de stack)**
  El owner es el `orquestador`: Claude implementa la task directamente, en orden, validando el definition of done antes de pasar a la siguiente. En este modo, el campo `Owner agent` de cada task lleva el valor `orquestador`.

En ambos modos el resto de reglas (formato, granularidad, dependencias, prueba de independencia) es idéntico. Solo cambia quién ejecuta la task.

---

## Orden canónico por dependencias

Siempre en este orden lógico, expresado por dependencias entre artefactos:

```text
1. Contratos y modelos      → tipos, interfaces, contratos y modelos de dominio que otros componentes consumen
2. Implementaciones         → lógica que materializa esos contratos (casos de uso, repositorios, servicios)
3. Integración / wiring     → composición, inyección de dependencias, configuración transversal y bordes de plataforma
4. UI / superficie          → pantallas, vistas, endpoints o cualquier superficie de salida del sistema
```

- Los **contratos y modelos** van antes que cualquier implementación que los consuma.
- Las **implementaciones** van antes que su integración o wiring.
- La **integración** va antes que la UI o la superficie que la usa.
- Los **tests acompañan a cada bloque**: una task de test se ordena junto al componente que valida (ver más abajo el orden TDD).

Este orden es un baseline derivado de dependencias, no de capas predefinidas. Si el Plan muestra una infraestructura transversal que deba resolverse antes, adelántala sin romper dependencias.

Consulta `${CLAUDE_SKILL_DIR}/references/task_sizing.md` para reglas de granularidad.

---

## La Prueba de Independencia

Antes de definir una Task, verifica:

> "¿Puede el owner ejecutar esta Task leyendo solo el Plan y las Tasks anteriores como contexto, sin necesitar ninguna decisión adicional del desarrollador?"

- **SÍ** → la Task está bien definida
- **NO** → la Task es demasiado vaga o le falta información del Plan

---

## Cómo generar Tasks desde un Plan

1. Lista todos los componentes del Plan recorriendo sus secciones reales.
2. Para cada componente:
   - asigna número de orden según el orden canónico por dependencias
   - asigna `Execution domain` si el Plan lo define
   - asigna `Owner agent` según el modo de ejecución (agente del stack u `orquestador`)
   - decide si existe `Suggested workflow`
3. Define dependencias explícitas entre Tasks.
4. Añade Tasks de tests siguiendo el orden correcto:
   - **Si el Plan incluye testing en scope**: aplicar orden TDD — la task de test precede a la task de implementación que valida. La task de test tiene `Layer: test` y está listada en el campo `Dependencies` de la task de implementación. El DoD de una task RED es: "el archivo de test existe, compila y falla con mensaje claro indicando la ausencia de implementación".
   - **Si el Plan no incluye testing explícitamente**: añadir tasks de test al final, acompañando al bloque de implementación que validan.
5. Verifica que todo componente del Plan tiene su Task correspondiente.
6. Verifica que ninguna Task queda con owner ambiguo.
