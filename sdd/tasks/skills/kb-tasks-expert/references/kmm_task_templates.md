# Templates de Task por Dominio de Ejecución KMM

Usa estos templates para formatear cada Task en el `_tasks.md`. Sustituye los valores `[EN CORCHETES]`.

---

## Template: Scaffold / wiring base

```markdown
## T-000: Platform — [Nombre del módulo o bloque]

- **Spec CA:** —
- **Plan ref:** §Módulos Gradle
- **Módulo:** [:feature:nombre | :app | :core:nombre]
- **Layer:** platform
- **Execution domain:** platform
- **Owner agent:** kmm-platform-integrator
- **Suggested workflow:** —
- **Input:** Feature: [nombre], módulos: [lista], wiring base requerido: [síntesis]
- **Dependencies:** ninguna
- **Definition of done:** Estructura base creada o actualizada, módulos conectados y wiring mínimo preparado para las Tasks posteriores.
```

---

## Template: Feature Domain Model

```markdown
## T-00X: Feature Domain — [NombreModel]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Domain Layer > Modelos
- **Módulo:** [:feature:nombre]
- **Layer:** domain
- **Execution domain:** feature
- **Owner agent:** kmm-feature-implementer
- **Suggested workflow:** —
- **Input:** Data class con campos: `campo1: Tipo, campo2: Tipo?`
- **Dependencies:** [T-000]
- **Definition of done:** `NombreModel.kt` en `domain/model/` — modelo puro sin dependencias de framework.
```

---

## Template: Feature Repository Interface

```markdown
## T-00X: Feature Domain — [NombreRepository] interface

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Domain Layer > Repository Interfaces
- **Módulo:** [:feature:nombre]
- **Layer:** domain
- **Execution domain:** feature
- **Owner agent:** kmm-feature-implementer
- **Suggested workflow:** —
- **Input:** Interfaz con métodos: `[firma(s) en términos de domain]`
- **Dependencies:** [T-00X (Model)]
- **Definition of done:** `NombreRepository.kt` en `domain/repository/` — contratos expresados en modelos de domain.
```

---

## Template: Feature UseCase

```markdown
## T-00X: Feature Domain — [NombreUseCase]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Domain Layer > Use Cases
- **Módulo:** [:feature:nombre]
- **Layer:** domain
- **Execution domain:** feature
- **Owner agent:** kmm-feature-implementer
- **Suggested workflow:** —
- **Input:** Parámetros: `[param: Tipo]`. Retorno: `[tipo funcional]`
- **Dependencies:** [T-00X (Repository interface)]
- **Definition of done:** `NombreUseCase.kt` en `domain/usecase/` con dependencias inyectadas por constructor.
```

---

## Template: Feature DTO + Mapper

```markdown
## T-00X: Feature Data — [NombreDto] + Mapper

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Data Layer > DTOs
- **Módulo:** [:feature:nombre]
- **Layer:** data
- **Execution domain:** feature
- **Owner agent:** kmm-feature-implementer
- **Suggested workflow:** —
- **Input:** DTO con campos remotos: `[campos]`. Mapea hacia: `[NombreModel]`
- **Dependencies:** [T-00X (Model)]
- **Definition of done:** DTO remoto y mapper hacia dominio definidos en la estructura de data de la feature.
```

---

## Template: Feature Remote DataSource

```markdown
## T-00X: Feature Data — [NombreRemoteDataSource]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Data Layer > DataSources
- **Módulo:** [:feature:nombre]
- **Layer:** data
- **Execution domain:** feature
- **Owner agent:** kmm-feature-implementer
- **Suggested workflow:** —
- **Input:** Endpoint o contrato remoto: `[método/endpoint]`. Retorna: `[DTO/resultado]`
- **Dependencies:** [T-00X (DTO + Mapper)]
- **Definition of done:** borde remoto de la feature definido de forma coherente con los contratos de red existentes.
```

---

## Template: Shared Remote/Auth Infrastructure

```markdown
## T-00X: Network/Auth — [Nombre del componente]

- **Spec CA:** [CA-XXX | —]
- **Plan ref:** [§Remote integration | §Auth | §Core]
- **Módulo:** [:core:nombre | :feature:nombre]
- **Layer:** core
- **Execution domain:** network-auth
- **Owner agent:** kmm-network-auth-implementer
- **Suggested workflow:** [wf-kmm-network-setup | wf-kmm-auth-setup-keycloak | wf-kmm-stack-setup-ktor-keycloak-koin | —]
- **Input:** Contrato o mecanismo: `[cliente HTTP | plugin auth | session contract | datasource compartido]`
- **Dependencies:** [T-XXX | ninguna]
- **Definition of done:** componente remoto o de auth implementado respetando contratos estables y ubicación correcta en `core` o módulo correspondiente.
```

---

## Template: Feature RepositoryImpl

```markdown
## T-00X: Feature Data — [NombreRepositoryImpl]

- **Spec CA:** [CA-XXX, CA-YYY]
- **Plan ref:** §Data Layer > Repository Implementations
- **Módulo:** [:feature:nombre]
- **Layer:** data
- **Execution domain:** feature
- **Owner agent:** kmm-feature-implementer
- **Suggested workflow:** —
- **Input:** Implementa `[NombreRepository]`. Estrategia: `[Remote-first | Cache-first | Local-only]`
- **Dependencies:** [T-00X (Repository interface), T-00X (DataSources)]
- **Definition of done:** repository de feature implementado y adaptado al borde remoto/local sin romper contratos de domain.
```

---

## Template: Platform Bridge / Expect-Actual

```markdown
## T-00X: Platform — [NombrePlatformApi]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Expect/Actual
- **Módulo:** [:feature:nombre | :core:nombre | :app]
- **Layer:** platform
- **Execution domain:** platform
- **Owner agent:** kmm-platform-integrator
- **Suggested workflow:** —
- **Input:** Integración requerida: `[expect/actual | host bridge | platform API]`
- **Dependencies:** [T-00X]
- **Definition of done:** integración de plataforma definida en `commonMain` y plataformas requeridas, o bridge del host cableado en el módulo correcto.
```

---

## Template: Feature ViewModel + State + Events

```markdown
## T-00X: Feature Presentation — [NombreViewModel] + State + Events

- **Spec CA:** [CA-XXX, CA-YYY]
- **Plan ref:** §Presentation Layer > ViewModels
- **Módulo:** [:feature:nombre]
- **Layer:** presentation
- **Execution domain:** feature
- **Owner agent:** kmm-feature-implementer
- **Suggested workflow:** —
- **Input:** UiState: `[campos]`. UiEvent: `[variantes]`
- **Dependencies:** [T-00X (UseCase)]
- **Definition of done:** ViewModel, UiState y UiEvent implementados siguiendo las reglas de la feature y de exposición de texto/UI.
```

---

## Template: Feature Screen

```markdown
## T-00X: Feature Presentation — [NombreScreen]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Presentation Layer > Screens
- **Módulo:** [:feature:nombre]
- **Layer:** presentation
- **Execution domain:** feature
- **Owner agent:** kmm-feature-implementer
- **Suggested workflow:** —
- **Input:** Renderiza `[UiState]`, emite `[UiEvent]`, journeys cubiertos: `[lista]`
- **Dependencies:** [T-00X (ViewModel + State + Events)]
- **Definition of done:** Screen composable implementada y conectada al contrato de presentation de la feature.
```

---

## Template: Navigation / App Wiring

```markdown
## T-00X: Platform Navigation — [AppNavGraph / FeatureGraph integration]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Navegación
- **Módulo:** [:app | :feature:nombre]
- **Layer:** app
- **Execution domain:** platform
- **Owner agent:** kmm-platform-integrator
- **Suggested workflow:** —
- **Input:** Rutas: `[lista]`. StartDestination: `[Route]`. Tipo de integración: `[AppNavGraph | featureGraph | host deep link]`
- **Dependencies:** [T-00X (Screen Composables)]
- **Definition of done:** navegación o wiring de app integrada respetando ownership, rutas type-safe y comportamiento del host.
```

---

## Template: Feature Tests

```markdown
## T-00X: Feature Tests — [Nombre del componente]

- **Spec CA:** [CA-XXX]
- **Plan ref:** [§Domain Layer | §Data Layer | §Presentation Layer]
- **Módulo:** [:feature:nombre]
- **Layer:** test
- **Execution domain:** feature
- **Owner agent:** kmm-feature-implementer
- **Suggested workflow:** —
- **Input:** Componente a validar: `[UseCase | RepositoryImpl | ViewModel]`. Casos: `[lista]`
- **Dependencies:** [T-00X (componente implementado)]
- **Definition of done:** suite de tests o validación automatizada implementada con doubles apropiados y sin dependencias accidentales del runtime real.
```
