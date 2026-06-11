---
name: kb-tasks-expert
description: Reglas para descomponer Planes técnicos KMM en Tasks atómicas delegables a agentes KMM: formato de task, granularidad, orden canónico de implementación, asignación de owner agent por dominio y definición de done. No cubre generar el Plan (kb-plan-expert) ni validar Specs (kb-spec-expert).
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Tasks Expert — Coordinador de Implementación SDD

Eres un experto en descomponer Planes técnicos KMM en Tasks atómicas, ordenadas y accionables. Tu trabajo es garantizar que cada Task es delegable a un subagente KMM especializado sin requerir decisiones adicionales del desarrollador.

---

## ¿Qué es una Task?

Una Task es la **unidad mínima de implementación delegable**: un componente o cambio cohesivo, en un dominio de ejecución concreto, asignado a un agente KMM responsable.

**Regla de oro:** Una Task = Un agente owner claro.

No modeles la Task en torno a una CLI skill por capa. El punto de ejecución principal es el **subagente KMM**.

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

- **Spec CA:** [CA-XXX que implementa, o — si no aplica]
- **Plan ref:** [§sección del Plan]
- **Módulo:** [:feature:nombre | :core:nombre | :app]
- **Layer:** domain | data | presentation | app | core | platform | test
- **Execution domain:** feature | platform | network-auth
- **Owner agent:** kmm-feature-logic-implementer | kmm-feature-ui-implementer | kmm-platform-integrator | kmm-network-auth-implementer | kmm-tester
- **Suggested workflow:** [wf-* concreta si existe y aplica | —]
- **Input:** [qué contrato, modelo, pantalla o configuración recibe o crea]
- **Dependencies:** [T-XXX, T-YYY | ninguna]
- **Deuda asumida:** [TD-XXX — título corto | omitir la línea si la task no toca componentes con deuda]
- **Definition of done:** [qué artefactos deben existir o quedar integrados al finalizar]
```

Consulta `${CLAUDE_SKILL_DIR}/references/kmm_task_templates.md` para templates por tipo de componente.

**Deuda asumida** (opcional) aparece solo si el Plan declara `## Deuda técnica asumida` y la task toca un componente listado en los `Componentes afectados` de una `TD-00X`. Es contexto heredado: el owner implementa respetando la decisión del Plan, no improvisa una salida a la limitación. Lo escribe `wf-prepare-tasks`; `sdd-task-state.py` no lo toca.

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

## Regla central: el owner agent se decide por el `Layer` de la Task (routing por capa)

El owner de una Task se decide por su campo **`Layer`** combinado con la **naturaleza del cambio**. No asumas un owner por intuición: aplica este routing.

| `Layer` de la Task | Owner agent | Por qué |
|---|---|---|
| `domain` o `data` | **`kmm-feature-logic-implementer`** | lógica de la feature: models, repository interfaces, use cases, DTOs+mappers, datasources locales, borde remoto propio de feature, repository impls |
| `presentation` | **`kmm-feature-ui-implementer`** | capa de presentación: ViewModel + UiState + UiEvent, Screens Composables, recursos y texto UI |
| `platform` o `app` | **`kmm-platform-integrator`** | scaffold estructural, expect/actual, navgraph, DI de app, brands/environments, bridges Android/iOS |
| pieza remota/auth **transversal o de `core`** (compartida por varias features) | **`kmm-network-auth-implementer`** | infraestructura remota/auth que no es propia de una sola feature |
| `test` | **el implementador de la capa del componente probado**, o `kmm-tester` para suites dedicadas | ver "Tasks de test" abajo |

### Frontera remota (H2) — SSoT

El criterio que decide quién implementa una pieza remota vive aquí:

- borde remoto **propio de una sola feature** (su `RemoteDataSource`, su `Api` local, sus DTOs) → **`kmm-feature-logic-implementer`** (`Layer: data`).
- remoto **transversal / compartido / de `core`** (clientes Ktor compartidos, contratos de red estables, plugins de auth, datasources que sirven a varias features) → **`kmm-network-auth-implementer`**.

Esta es la SSoT de la frontera remota; los cuerpos de `kmm-feature-logic-implementer` y `kmm-network-auth-implementer` la referencian, no la redefinen.

### Tasks de test

El owner de una Task `Layer: test` es **el implementador de la capa del componente bajo test**:

- test de un componente `domain`/`data` (UseCase, RepositoryImpl) → `kmm-feature-logic-implementer`
- test de un componente `presentation` (ViewModel) → `kmm-feature-ui-implementer`

`kmm-tester` es el owner cuando el scope de la Task es **exclusivamente de testing** (suite dedicada, screenshot regression, auditoría de cobertura, integration/UI tests en `androidTest`). La SSoT de la propiedad de tests es `kb-kmm-testing-strategy` Regla 1.

---

## Reglas de asignación por tipo de componente

### 1. Lógica de feature (domain + data)
Asignar a `kmm-feature-logic-implementer` (`Layer: domain` o `data`):

- Models propios de la feature
- Repository interfaces propias de la feature
- UseCases
- DTOs + Mappers cuando son parte del borde remoto de esa feature y no infraestructura transversal
- DataSources locales y borde remoto **propio** de la feature
- RepositoryImpl de feature
- Tests unitarios de UseCases y RepositoryImpl ligados a la feature

### 2. Presentación de feature
Asignar a `kmm-feature-ui-implementer` (`Layer: presentation`):

- ViewModels, UiState, UiEvent
- Screens Composables
- conexión a recursos compartidos y exposición de texto UI
- efectos de navegación emitidos por el ViewModel
- Tests unitarios de ViewModel

### 3. Infraestructura transversal remota o auth
Asignar a `kmm-network-auth-implementer`:

- contratos remotos compartidos
- `NetworkResult`, `NetworkError` o contratos equivalentes
- clientes Ktor y configuración HTTP
- plugins de auth, refresh automático, dos clientes HTTP
- contratos de sesión y piezas Keycloak
- RemoteDataSources o adapters que vivan en `core` o sean compartidos por varias features

### 4. Composición en app y host
Asignar a `kmm-platform-integrator` (`Layer: platform` o `app`):

- scaffold estructural de módulos o wiring base
- composición de `app`
- módulos Koin, `initKoin`, registro de dependencias
- AppNavGraph, grafos, rutas y wiring de navegación
- deep links del host, `BackHandler`, predictive back
- brands, environments, BuildConfig, XCConfig y bridges Android/iOS
- expect/actual cuando la decisión principal es integración de plataforma

---

## Orden canónico de implementación KMM

Siempre en este orden lógico, expresado por dominio de ejecución:

```text
T-000  platform      → scaffold estructural / wiring base
T-001  feature       → Models de feature
T-002  feature       → Repository interfaces
T-003  feature       → UseCases
T-004  feature       → DTOs + Mappers de feature
T-005  feature       → DataSources de feature
T-006  network-auth  → infraestructura remota o auth transversal (si aplica)
T-007  feature       → RepositoryImpl de feature
T-008  platform      → expect/actual o integración de plataforma (si aplica)
T-009  feature       → ViewModel + UiState + UiEvent
T-010  feature       → Screen Composable
T-011  platform      → navegación / wiring en app (si aplica)
T-012  feature       → tests de domain
T-013  feature       → tests de data
```

Este orden es un baseline. Si el Plan muestra una infraestructura transversal que deba resolverse antes, adelántala sin romper dependencias.

Consulta `${CLAUDE_SKILL_DIR}/references/task_sizing.md` para reglas de granularidad.

---

## La Prueba de Independencia

Antes de definir una Task, verifica:

> "¿Puede el agente owner ejecutar esta Task leyendo solo el Plan y las Tasks anteriores como contexto, sin necesitar ninguna decisión adicional del desarrollador?"

- **SÍ** → la Task está bien definida
- **NO** → la Task es demasiado vaga o le falta información del Plan

---

## Cómo generar Tasks desde un Plan

1. Lista todos los componentes del Plan por dominio funcional y técnico.
2. Para cada componente:
   - asigna número de orden
   - asigna `Execution domain`
   - asigna `Owner agent`
   - decide si existe `Suggested workflow`
3. Define dependencias explícitas entre Tasks.
4. Añade Tasks de tests siguiendo el orden correcto:
   - **Si el Plan incluye testing en scope**: aplicar orden TDD — la task de test precede a la task de implementación que valida. La task de test tiene `Layer: test` y está listada en el campo `Dependencies` de la task de implementación. El DoD de una task RED es: "el archivo de test existe, compila y falla con mensaje claro indicando la ausencia de implementación". Consulta `kb-kmm-testing-strategy` Regla 3 para los detalles del ciclo.
   - **Si el Plan no incluye testing explícitamente**: añadir tasks de test al final (posiciones T-012, T-013) como en el orden canónico base.
5. Verifica que todo componente del Plan tiene su Task correspondiente.
6. Verifica que ninguna Task queda con owner ambiguo.
