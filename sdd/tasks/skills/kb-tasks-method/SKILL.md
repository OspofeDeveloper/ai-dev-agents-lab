---
name: kb-tasks-method
description: Procedimiento operativo compartido de la fase tasks SDD — los pasos stack-agnósticos para descomponer un Plan validado en un _tasks.md. Núcleo metodológico que cargan las variantes genérica y de overlay de task-generator; cada una aporta solo su especialización de stack sobre los hooks marcados.
effort: low
user-invocable: false
allowed-tools: [Read]
---

# Tasks Method — Procedimiento compartido de la fase tasks

Esta KB es el **procedimiento metodológico común** de `task-generator`: descomponer un
`_plan.md` validado en un `_tasks.md` con tasks atómicas, ordenadas por dependencias y
asignadas a su owner. Es **idéntico en cualquier stack** — lo que cambia entre el modo
genérico y un overlay (KMM, etc.) es solo el contenido de los **hooks de especialización**,
que el cuerpo del agente rellena.

> SSoT de la metodología de agente: vive aquí, no duplicada en cada `agents/*.md`.
> El formato obligatorio de una task, la regla de owner por dominio de ejecución, el orden
> canónico y los templates viven en `kb-tasks-expert`; esta KB es el *cómo operar*.

## Hooks de especialización de stack

Donde este procedimiento dice **‹especialización de stack›**, el cuerpo del agente aporta
el detalle concreto:

- **Modo genérico (stack agnóstico)**: el owner de cada task es `orquestador` (Claude
  implementa directamente, en orden, validando el DoD); el desglose sigue las secciones
  reales del Plan sin imponer una topología fija; las tasks referencian rutas y artefactos
  reales del repositorio.
- **Overlay de stack**: los owners son los agentes del stack; el desglose de componentes y
  las reglas de dependencia siguen la arquitectura prescriptiva del stack como **default**,
  y los templates son los del overlay. Pero **el repo destino manda sobre el dogma**: si el
  repositorio real organiza los componentes o las dependencias de otra forma (capturado en
  `<stack>_project_state.md`), las tasks respetan lo que el repo hace; el canon del stack
  rellena huecos donde el repo no se ha pronunciado, no sobrescribe convenciones divergentes
  ya presentes.

El procedimiento, el formato de task, los estados y el formato del artefacto **no cambian**
entre modos (contrato de overlay, `kb-sdd-stack-overlay-contract`).

---

## Entrada que recibes
- Contenido completo del `_plan.md`
- Path del archivo origen

## Proceso

**1. Lista todos los componentes del Plan**

Recorre cada sección real del Plan y extrae todos los componentes a implementar. No asumas
un conjunto fijo de capas: usa las secciones que el Plan define realmente. El mapa concreto
de tipos de componente (qué capas, qué nombres) lo prescribe ‹especialización de stack›.
Como guía agnóstica de tipos habituales:
- **Contratos y modelos:** tipos, interfaces, contratos y modelos de dominio que otros componentes consumen
- **Implementaciones:** lógica que materializa esos contratos (casos de uso, repositorios, servicios, fuentes de datos)
- **Integración / wiring:** composición, inyección de dependencias, configuración transversal y bordes de plataforma
- **UI / superficie:** pantallas, vistas, endpoints o cualquier superficie de salida del sistema

**2. Asigna el orden canónico por dependencias**

Consulta `kb-tasks-expert` para el orden correcto. El baseline:
- contratos y modelos antes que las implementaciones que los consumen
- implementaciones antes que su integración o wiring
- integración antes que la UI o la superficie que la usa
- los tests acompañan a cada bloque

La integración transversal se adelanta o retrasa según las dependencias reales del Plan.
El orden fino dentro de las capas lo prescribe ‹especialización de stack›.

**3. Genera cada Task**

Para cada componente, usa el template de `kb-tasks-expert` que corresponda (la ruta del
fichero de templates la indica ‹especialización de stack›).
Asigna el número correlativo (T-000, T-001, T-002...).
Rellena todos los campos del formato obligatorio de `kb-tasks-expert`: Spec CA, Plan ref,
componente, layer, execution domain, owner agent, suggested workflow, input, dependencies
y definition of done.

**4. Define dependencias explícitas**

Reglas de dependencia derivadas del orden por dependencias:
- las implementaciones dependen de los contratos y modelos que consumen
- la integración / wiring depende de las implementaciones que compone
- la UI / superficie depende de la implementación o integración que la respalda
- los tests dependen del componente que testean

Las reglas finas entre capas concretas las prescribe ‹especialización de stack›.

**5. Añade Tasks de tests con orden TDD**

Añade una Task de test por cada componente testable cuando el Plan incluya testing en scope.

Aplica el orden TDD: **la task de test precede a la task de implementación** que valida. La
task de test tiene `Layer: test` y aparece listada en el campo `Dependencies` de la task de
implementación correspondiente. El DoD de una task de test RED es: "el archivo de test
existe, compila y falla con mensaje claro indicando la ausencia de implementación".

El owner de las tasks de test y qué componentes se consideran testables lo define
‹especialización de stack›. Si el Plan no incluye testing explícitamente, coloca las tasks
de test al final, acompañando al bloque de implementación que validan.

> Empaquetado: los tests viajan en la misma unidad de trabajo / PR que el código que cubren
> (la pareja RED/GREEN son commits adyacentes en la misma rama). SSoT del criterio:
> `kb-delivery-discipline`.

**6. Verifica cobertura**

¿Todos los componentes del Plan tienen su Task?
¿Todas las Tasks referenciadas como dependencias existen?

**7. Propaga la deuda técnica del Plan (si la hay)**

Si el Plan declara `## Deuda técnica asumida`, cada task cuyo componente esté en los
`Componentes afectados` de una `TD-00X` lleva la línea `- **Deuda asumida:** TD-00X —
<título corto>` en su bloque (ver `kb-tasks-expert`). **No generes tasks para saldar la
deuda** — eso es trabajo futuro que vive en el `Queda pendiente` del Plan.

**8. Produce el output**

Formatea el `_tasks.md` completo con el header de trazabilidad. Si el Plan declara metadata
de trazabilidad (`Spec origen`, `PRD origen`, `PRD version`, `Change ref`, `Status sync`),
refléjala en el header; si falta, usa `unknown` o `N/A` de forma explícita. El desglose del
resumen de implementación por owner lo prescribe ‹especialización de stack›.

Estructura del header de salida:

```
# Tasks: [Nombre de la Feature]
> **Plan origen:** [path/_plan.md]
> **Spec origen:** [path/_spec.md | unknown]
> **PRD origen:** [path/al/PRD.md | unknown]
> **PRD version:** [1.0 | unknown]
> **Change ref:** [CR-XXX | N/A]
> **Status sync:** [in_sync | needs_review | stale | unknown]
> **Fecha:** [YYYY-MM-DD]
> **Total tasks:** N
```

Las tasks van en orden T-000, T-001, T-002, ..., seguidas de un `## Resumen de
implementación` (tabla Dominio / Tasks / Owner) y la línea `**Orden recomendado de
ejecución:** T-000 → ... → T-N`.

## Regla de oro

> Cada Task debe ser ejecutable por su owner habiendo leído solo el Plan y las Tasks
> anteriores como contexto, sin necesitar ninguna decisión adicional del desarrollador.
