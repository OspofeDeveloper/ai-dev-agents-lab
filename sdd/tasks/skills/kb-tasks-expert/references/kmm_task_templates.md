# Templates de Task por Skill KMM

Usa estos templates para formatear cada Task en el `_tasks.md`. Sustituye los valores `[EN CORCHETES]`.

---

## Template: /kmm-scaffold

```markdown
## T-000: Scaffold — [Nombre del módulo]

- **Spec CA:** —
- **Plan ref:** §Módulos Gradle
- **Módulo:** [:feature:nombre]
- **Layer:** scaffold
- **Skill:** /kmm-scaffold
- **Input:** Feature: [nombre], módulos: [:feature:nombre], capas: domain/data/presentation
- **Dependencies:** ninguna
- **Definition of done:** Directorios `domain/model/`, `domain/repository/`, `domain/usecase/`, `data/remote/dto/`, `data/mapper/`, `data/repository/`, `presentation/` creados. `build.gradle.kts` configurado con dependencias base (Koin, Coroutines).
```

---

## Template: /kmm-domain (Model)

```markdown
## T-00X: Domain — [NombreModel]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Domain Layer > Modelos
- **Módulo:** [:feature:nombre]
- **Layer:** domain
- **Skill:** /kmm-domain
- **Input:** Data class con campos: `campo1: Tipo, campo2: Tipo?`
- **Dependencies:** [T-000]
- **Definition of done:** `NombreModel.kt` en `domain/model/` — data class pura sin anotaciones de framework.
```

---

## Template: /kmm-domain (Repository Interface)

```markdown
## T-00X: Domain — [NombreRepository] interface

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Domain Layer > Repository Interfaces
- **Módulo:** [:feature:nombre]
- **Layer:** domain
- **Skill:** /kmm-domain
- **Input:** Interfaz con métodos: `fun getSomething(param: Type): Flow<Result<NombreModel>>`
- **Dependencies:** [T-00X (NombreModel)]
- **Definition of done:** `NombreRepository.kt` en `domain/repository/` — interface con contratos en términos de domain models, sin DTOs.
```

---

## Template: /kmm-domain (UseCase)

```markdown
## T-00X: Domain — [NombreUseCase]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Domain Layer > Use Cases
- **Módulo:** [:feature:nombre]
- **Layer:** domain
- **Skill:** /kmm-domain
- **Input:** Parámetros: `[param: Tipo]`. Retorno: `Flow<Result<NombreModel>>` / `suspend: Result<T>`
- **Dependencies:** [T-00X (NombreRepository interface)]
- **Definition of done:** `NombreUseCase.kt` en `domain/usecase/` con `operator fun invoke()`. Inyecta el Repository por constructor.
```

---

## Template: /kmm-data (DTO + Mapper)

```markdown
## T-00X: Data — [NombreDto] + Mapper

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Data Layer > DTOs
- **Módulo:** [:feature:nombre]
- **Layer:** data
- **Skill:** /kmm-data
- **Input:** DTO con campos JSON: `campo: String, campo2: Int`. Mapea hacia: `NombreModel`
- **Dependencies:** [T-00X (NombreModel en domain)]
- **Definition of done:** `NombreDto.kt` en `data/remote/dto/` (con `@Serializable`) + `NombreMapper.kt` en `data/mapper/` con función `fun NombreDto.toModel(): NombreModel`.
```

---

## Template: /kmm-data (DataSource Remote)

```markdown
## T-00X: Data — [NombreRemoteDataSource]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Data Layer > DataSources
- **Módulo:** [:feature:nombre]
- **Layer:** data
- **Skill:** /kmm-data
- **Input:** Endpoint: `GET /api/nombre`. Retorna: `NombreDto`
- **Dependencies:** [T-00X (NombreDto)]
- **Definition of done:** `NombreRemoteDataSource.kt` (interfaz) + `NombreRemoteDataSourceImpl.kt` (implementación Ktor) en `data/remote/datasource/`.
```

---

## Template: /kmm-data (DataSource Local)

```markdown
## T-00X: Data — [NombreLocalDataSource]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Data Layer > DataSources
- **Módulo:** [:feature:nombre]
- **Layer:** data
- **Skill:** /kmm-data
- **Input:** Operaciones: `save(entity: NombreEntity)`, `getAll(): List<NombreEntity>`
- **Dependencies:** [T-000]
- **Definition of done:** `NombreLocalDataSource.kt` (interfaz) + `NombreLocalDataSourceImpl.kt` (SQLDelight) en `data/local/datasource/`.
```

---

## Template: /kmm-data (RepositoryImpl)

```markdown
## T-00X: Data — [NombreRepositoryImpl]

- **Spec CA:** [CA-XXX, CA-YYY]
- **Plan ref:** §Data Layer > Repository Implementations
- **Módulo:** [:feature:nombre]
- **Layer:** data
- **Skill:** /kmm-data
- **Input:** Implementa `NombreRepository`. DataSources: `NombreRemoteDataSource` [+ `NombreLocalDataSource`]. Estrategia: [Remote-first | Cache-first | Local-only]
- **Dependencies:** [T-00X (NombreRepository interface), T-00X (DataSources)]
- **Definition of done:** `NombreRepositoryImpl.kt` en `data/repository/` implementando la interfaz de domain. Usa los DataSources inyectados, nunca Ktor directamente.
```

---

## Template: /kmm-expect-actual

```markdown
## T-00X: Expect/Actual — [NombrePlatformApi]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Expect/Actual
- **Módulo:** [:feature:nombre o :core:nombre]
- **Layer:** expect-actual
- **Skill:** /kmm-expect-actual
- **Input:** `expect fun/class NombrePlatformApi` — propósito: [qué hace funcionalmente]. Plataformas: Android + iOS
- **Dependencies:** [T-00X]
- **Definition of done:** `NombrePlatformApi.kt` en `commonMain/` (expect) + `NombrePlatformApi.android.kt` en `androidMain/` (actual) + `NombrePlatformApi.ios.kt` en `iosMain/` (actual).
```

---

## Template: /kmm-presentation (ViewModel + State + Events)

```markdown
## T-00X: Presentation — [NombreViewModel] + State + Events

- **Spec CA:** [CA-XXX, CA-YYY]
- **Plan ref:** §Presentation Layer > ViewModels
- **Módulo:** [:feature:nombre]
- **Layer:** presentation
- **Skill:** /kmm-presentation
- **Input:** UiState campos: `isLoading: Boolean, data: NombreModel?, error: String?`. UiEvent variantes: `OnButtonClicked, OnInputChanged(value: String), OnRetry`
- **Dependencies:** [T-00X (NombreUseCase)]
- **Definition of done:** `NombreViewModel.kt` (expone `StateFlow<NombreUiState>` y `onEvent(NombreUiEvent)`) + `NombreUiState.kt` + `NombreUiEvent.kt` (sealed class) en `presentation/`.
```

---

## Template: /kmm-presentation (Screen Composable)

```markdown
## T-00X: Presentation — [NombreScreen] Composable

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Presentation Layer > ViewModels
- **Módulo:** [:feature:nombre]
- **Layer:** presentation
- **Skill:** /kmm-presentation
- **Input:** Recibe `NombreUiState`, emite `NombreUiEvent`. Journeys cubiertos: [Journey 1, Journey 2]
- **Dependencies:** [T-00X (NombreViewModel + State + Events)]
- **Definition of done:** `NombreScreen.kt` en `presentation/screen/` — Composable stateless que renderiza el UiState y delega toda lógica al ViewModel vía UiEvent.
```

---

## Template: /kmm-tests (UseCase)

```markdown
## T-00X: Tests — [NombreUseCase]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Domain Layer > Use Cases
- **Módulo:** [:feature:nombre]
- **Layer:** test
- **Skill:** /kmm-tests
- **Input:** Componente: `NombreUseCase`. Casos a cubrir: happy path, error de repositorio, estado vacío
- **Dependencies:** [T-00X (NombreUseCase)]
- **Definition of done:** `NombreUseCaseTest.kt` en `src/commonTest/` usando JUnit5. Si devuelve Flow → usar Turbine. Repository mockeado con fake implementation.
```

---

## Template: /kmm-tests (RepositoryImpl)

```markdown
## T-00X: Tests — [NombreRepositoryImpl]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Data Layer > Repository Implementations
- **Módulo:** [:feature:nombre]
- **Layer:** test
- **Skill:** /kmm-tests
- **Input:** Componente: `NombreRepositoryImpl`. Casos: remote success, remote error, cache hit, cache miss
- **Dependencies:** [T-00X (NombreRepositoryImpl)]
- **Definition of done:** `NombreRepositoryImplTest.kt` en `src/commonTest/` con DataSources fake (no mocks de Ktor). Verifica estrategia de caché si aplica.
```

---

## Template: /kmm-navigation

```markdown
## T-00X: Navigation — [AppNavGraph / FeatureNavGraph]

- **Spec CA:** [CA-XXX]
- **Plan ref:** §Navegación
- **Módulo:** [:app o :feature:nombre]
- **Layer:** presentation
- **Skill:** /kmm-navigation
- **Input:** Rutas: [ListaDeRutas]. StartDestination: [Route]. ¿Nested en?: [:app NavHost | standalone]
- **Dependencies:** [T-00X (Screen Composables)]
- **Definition of done:** NavGraph definido en commonMain con todas las rutas type-safe. NavHost wired en el entry point de la plataforma. Rutas extraídas con toRoute() en cada destination.
```
