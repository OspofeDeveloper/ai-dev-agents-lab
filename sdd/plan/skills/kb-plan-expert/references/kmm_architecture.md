# Arquitectura KMM con Clean Architecture

Reglas de arquitectura aplicadas en todos los Planes de este ecosistema. Estas decisiones son invariables — no se re-evalúan por feature.

---

## Estructura de Módulos Gradle

```
:app                    → Punto de entrada, wiring DI, navegación raíz
:feature:<nombre>       → Feature completa (domain + data + presentation)
:core:network           → Cliente HTTP (Ktor), interceptores, manejo de errores de red
:core:database          → SQLDelight, DAOs base
:core:common            → Extensiones, utils, tipos compartidos
:core:ui                → Componentes Compose reutilizables, tema, design tokens
```

**Convención de nombre:** `:feature:` en minúsculas y snake_case.
Ejemplos: `:feature:auth`, `:feature:job_offers`, `:feature:time_tracking`, `:feature:messaging`.

---

## Capas dentro de cada Feature

### domain/
**Qué va aquí:** Lógica de negocio pura. Sin dependencias de Android ni de ningún framework.

```
domain/
├── model/          → Data classes que representan entidades de negocio
│                     Ejemplo: User, AuthToken, JobOffer, ServiceRecord
├── repository/     → Interfaces de repositorio (contratos, sin implementación)
│                     Ejemplo: AuthRepository, JobOffersRepository
└── usecase/        → Un UseCase por acción de negocio principal
                      Ejemplo: LoginUseCase, GetJobOffersUseCase, RequestAbsenceUseCase
```

**Reglas:**
- Los modelos de domain NO tienen anotaciones de Gson, Kotlinx Serialization, ni Room
- Los UseCases tienen un método público: `suspend operator fun invoke(params): Result<T>` o devuelven `Flow<Result<T>>`
- Las interfaces de Repository definen el contrato en términos de domain models, nunca DTOs
- **Sin imports de android.*, compose.*, o cualquier framework externo**

### data/
**Qué va aquí:** Implementación de los contratos de domain. Conoce los detalles técnicos de red y persistencia.

```
data/
├── remote/
│   ├── dto/        → Data Transfer Objects: clases que mapean la respuesta JSON de la API
│   └── datasource/ → Interfaz + implementación del datasource remoto (usa Ktor)
├── local/
│   ├── entity/     → Entidades SQLDelight (o clases para DataStore/preferencias)
│   └── datasource/ → Interfaz + implementación del datasource local
├── mapper/         → Funciones de mapeo entre capas: DTO → Model, Entity → Model
└── repository/     → RepositoryImpl que implementa la interfaz de domain
```

**Reglas:**
- Los mappers son funciones de extensión puras: `fun UserDto.toModel(): User`
- Los RepositoryImpl dependen de los DataSources (interfaces), no de Ktor o SQLDelight directamente
- Los DTOs son los únicos que conocen el formato JSON (anotaciones `@Serializable`)
- Los RepositoryImpl deciden la estrategia de datos: Remote-first, Cache-first, o Local-only

### presentation/
**Qué va aquí:** UI y estado de la UI. Solo conoce domain models, nunca DTOs ni entidades.

```
presentation/
├── viewmodel/      → ViewModel (una por screen o flujo principal)
├── state/          → UiState: todo lo que la pantalla necesita para renderizarse
├── event/          → UiEvent: acciones del usuario que el ViewModel procesa (sealed class)
├── effect/         → SideEffect: navegación, toasts, acciones one-shot (opcional)
└── screen/         → Composable de la pantalla (stateless: recibe UiState, emite UiEvent)
```

**Reglas:**
- El ViewModel expone: `val uiState: StateFlow<UiState>` y `fun onEvent(event: UiEvent)`
- Los Composable no tienen lógica de negocio — solo renderizan UiState y emiten UiEvent al ViewModel
- El ViewModel no referencia ningún tipo de View, Context, o Activity directamente
- Los SideEffects se emiten por `Channel` o `SharedFlow` con replay=0

---

## Regla de Dependencias entre Capas

```
:app  →  :feature:X:presentation  →  :feature:X:domain  ←  :feature:X:data
                                            ↑
                                       :core:*
```

- `presentation` depende de `domain` (usa Models, invoca UseCases)
- `data` depende de `domain` (implementa interfaces de Repository)
- `domain` NO depende de nadie — es el núcleo puro
- `:core:*` pueden ser dependencia de cualquier capa

**Nunca:** `presentation → data` directamente.

---

## Cuándo usar Expect/Actual

Solo para APIs que no tienen equivalente en KMM commonMain:

| Necesidad | ¿Expect/Actual? | Alternativa KMM si existe |
|---|---|---|
| Preferencias clave-valor simples | NO | Multiplatform Settings |
| Logging | NO | Kermit |
| HTTP | NO | Ktor Client |
| Base de datos | NO | SQLDelight |
| Notificaciones push (obtener token FCM/APNs) | SÍ | — |
| Biometría | SÍ | — |
| Cámara / GPS / sensores | SÍ | — |
| Crypto / Keychain / Keystore | SÍ | — |
| Permisos de sistema | SÍ | — |

Cuando se necesita expect/actual:
1. Declara la `expect` en `commonMain` con documentación funcional (qué hace, no cómo)
2. Implementa los `actual` en `androidMain` e `iosMain`
3. Inyecta vía Koin desde el módulo de plataforma correspondiente

---

## Convenciones de Nombres

| Tipo | Patrón | Ejemplos |
|---|---|---|
| UseCase | `<Acción><Entidad>UseCase` | `LoginUseCase`, `GetJobOffersUseCase`, `SubmitAbsenceUseCase` |
| Repository interface | `<Entidad>Repository` | `AuthRepository`, `JobOffersRepository` |
| Repository impl | `<Entidad>RepositoryImpl` | `AuthRepositoryImpl`, `JobOffersRepositoryImpl` |
| DTO | `<Entidad>Dto` | `UserDto`, `JobOfferDto`, `ServiceRecordDto` |
| Mapper | extensión sobre el DTO o Entity | `fun UserDto.toModel(): User` |
| Entity (SQLDelight) | `<Entidad>Entity` | `UserEntity`, `ServiceRecordEntity` |
| DataSource (interfaz) | `<Entidad><Tipo>DataSource` | `AuthRemoteDataSource`, `JobOffersLocalDataSource` |
| DataSource (impl) | `<Entidad><Tipo>DataSourceImpl` | `AuthRemoteDataSourceImpl` |
| ViewModel | `<Screen>ViewModel` | `LoginViewModel`, `JobOffersViewModel` |
| UiState | `<Screen>UiState` | `LoginUiState`, `JobOffersUiState` |
| UiEvent | `<Screen>UiEvent` | `LoginUiEvent` (sealed class) |
| Screen Composable | `<Screen>Screen` | `LoginScreen`, `JobOffersScreen` |
| Módulo Koin | `<feature>Module` | `authModule`, `jobOffersModule` |
