# Plantilla de Output: Plan Técnico KMM

Usa esta estructura para producir un Plan válido. Todos los campos marcados `[obligatorio]` son requeridos.

---

```markdown
# Plan: [Nombre de la Feature]
> **Versión:** 1.0
> **Spec origen:** [path/al/_spec.md]
> **PRD origen:** [path/al/PRD.md | unknown]
> **PRD version:** [1.0 | unknown]
> **Change ref:** [CR-XXX | N/A]
> **Status sync:** [in_sync | needs_review | stale | unknown]
> **Fecha:** [YYYY-MM-DD]
> **Estado:** BORRADOR

---

## Stack Técnico [obligatorio]

| Área | Tecnología |
|---|---|
| Plataforma | Kotlin Multiplatform Mobile |
| UI Android | Jetpack Compose |
| UI iOS | SwiftUI |
| Red | Ktor Client |
| BD Local | SQLDelight (si aplica, omitir si no) |
| DI | Koin |
| Async | Coroutines + Flow |
| Tests | JUnit5 + Turbine (Flows) |

---

## Módulos Gradle [obligatorio]

| Módulo | Estado | Descripción |
|---|---|---|
| `:feature:<nombre>` | NUEVO | Feature completa: domain, data, presentation |
| `:core:network` | EXISTENTE | Sin cambios (o: añadir interceptor X) |
| `:app` | MODIFICADO | Añadir rutas de navegación + módulo Koin |

---

## Domain Layer [obligatorio]

### Modelos

| Clase | Campos | CAs que implementa |
|---|---|---|
| `NombreModel` | `id: String, campo2: Type` | CA-001, CA-002 |

### Repository Interfaces

| Interfaz | Métodos | Firma de retorno |
|---|---|---|
| `NombreRepository` | `getSomething(param: Type)` | `Flow<Result<List<NombreModel>>>` |
| `NombreRepository` | `doSomething(param: Type)` | `suspend fun: Result<Unit>` |

### Use Cases

| UseCase | Parámetros de entrada | Retorno | CA que implementa |
|---|---|---|---|
| `NombreUseCase` | `param: Type` | `Flow<Result<NombreModel>>` | CA-001 |
| `OtroUseCase` | `—` | `suspend: Result<List<NombreModel>>` | CA-002, CA-003 |

---

## Data Layer [obligatorio]

### DTOs (Remote)

| DTO | Campos JSON | Mapper hacia |
|---|---|---|
| `NombreDto` | `campo: String` (serializable) | `NombreModel` |

### DataSources

| DataSource | Tipo | Operaciones principales |
|---|---|---|
| `NombreRemoteDataSource` | Remote (Ktor) | `getSomething(): NombreDto` |
| `NombreLocalDataSource` | Local (SQLDelight) | `save(model)`, `getAll(): List<NombreEntity>` |

### Repository Implementations

| Implementación | Implementa | Estrategia de datos |
|---|---|---|
| `NombreRepositoryImpl` | `NombreRepository` | Remote-first (cache local tras fetch) |

---

## Presentation Layer [obligatorio]

### ViewModels

| ViewModel | UiState | UiEvent | Screen asociada |
|---|---|---|---|
| `NombreViewModel` | `NombreUiState` | `NombreUiEvent` | `NombreScreen` |

### UiState — campos

```
NombreUiState:
  isLoading: Boolean        = false
  data: NombreModel?        = null
  items: List<NombreModel>  = emptyList()
  error: String?            = null
```

### UiEvent — variantes (sealed class)

```
NombreUiEvent:
  OnButtonClicked
  OnInputChanged(value: String)
  OnItemSelected(id: String)
  OnRetry
```

---

## Expect/Actual [omitir esta sección si no aplica]

| API | commonMain (expect) | androidMain | iosMain |
|---|---|---|---|
| `NombrePlatformApi` | `expect fun doX(): Y` | `ActualAndroid` | `ActualIos` |

---

## Checklist de Trazabilidad [obligatorio]

| CA del Spec | Componente del Plan que lo implementa | Estado |
|---|---|---|
| CA-001: [descripción breve] | `NombreUseCase` + `NombreRepositoryImpl` | ✓ cubierto |
| CA-002: [descripción breve] | `NombreViewModel.onEvent(OnButtonClicked)` | ✓ cubierto |
| CA-003: [descripción breve] | — | ✗ sin cobertura → [TECH_GAP] |

**CAs sin cobertura:** [ninguno | lista aquí los gaps]
**TECH_GAPs:** [ninguno | descripción de cada gap que bloquea el plan]
```
