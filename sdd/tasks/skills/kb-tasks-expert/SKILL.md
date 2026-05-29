---
name: kb-tasks-expert
description: Reglas para descomponer Planes técnicos KMM en Tasks atómicas delegables a agentes KMM especializados: formato obligatorio de task, granularidad, orden canónico de implementación, criterios de asignación de owner agent por dominio de trabajo y definición de done por task. No cubre la generación del Plan (kb-plan-expert) ni la validación de Specs (kb-spec-expert).
effort: low
allowed-tools: [Read]
disable-model-invocation: true
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
- **Owner agent:** kmm-feature-implementer | kmm-platform-integrator | kmm-network-auth-implementer
- **Suggested workflow:** [wf-* concreta si existe y aplica | —]
- **Input:** [qué contrato, modelo, pantalla o configuración recibe o crea]
- **Dependencies:** [T-XXX, T-YYY | ninguna]
- **Definition of done:** [qué artefactos deben existir o quedar integrados al finalizar]
```

Consulta `references/kmm_task_templates.md` para templates por tipo de componente.

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

## Regla central: el owner agent se decide por dominio de trabajo, no por capa aislada

Nunca asumas que `domain`, `data` o `presentation` implican por sí solos un agente distinto. El owner se decide por la **naturaleza del cambio**:

- **`kmm-feature-implementer`**
  cuando la Task pertenece al interior de una feature y su intención principal es implementar comportamiento funcional de esa feature.
- **`kmm-platform-integrator`**
  cuando la Task vive en `app`, en navegación, DI, brands/environments o integración con Android/iOS.
- **`kmm-network-auth-implementer`**
  cuando la Task define infraestructura remota, contratos de red/auth o piezas transversales de `core` ligadas a networking/auth.

---

## Reglas de asignación por tipo de componente

### 1. Dominio funcional de feature
Asignar a `kmm-feature-implementer`:

- Models propios de la feature
- Repository interfaces propias de la feature
- UseCases
- DTOs + Mappers cuando son parte del borde remoto de esa feature y no infraestructura transversal
- RepositoryImpl de feature
- ViewModels, UiState, UiEvent, Screens
- Tests unitarios de UseCases y RepositoryImpl ligados a la feature

### 2. Infraestructura transversal remota o auth
Asignar a `kmm-network-auth-implementer`:

- contratos remotos compartidos
- `NetworkResult`, `NetworkError` o contratos equivalentes
- clientes Ktor y configuración HTTP
- plugins de auth, refresh automático, dos clientes HTTP
- contratos de sesión y piezas Keycloak
- RemoteDataSources o adapters que vivan en `core` o sean compartidos por varias features

### 3. Composición en app y host
Asignar a `kmm-platform-integrator`:

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

Consulta `references/task_sizing.md` para reglas de granularidad.

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
