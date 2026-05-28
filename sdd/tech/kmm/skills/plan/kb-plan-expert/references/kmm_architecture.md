# Arquitectura KMM con Clean Architecture

Reglas de arquitectura aplicadas en todos los Planes de este ecosistema. Estas decisiones son invariables — no se re-evalúan por feature.

---

## Estructura de Módulos Gradle

```
:app                    → Punto de entrada, wiring DI, navegación raíz
:feature:<nombre>       → Feature completa (domain + data + presentation)
:core:network           → Cliente HTTP (Ktor), interceptores, manejo de errores de red
:core:database          → Persistencia local. Room KMP.
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
│   ├── entity/     → Entidades Room KMP (o clases para DataStore/preferencias)
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
├── state/          → <Screen>State: todo lo que la pantalla necesita para renderizarse
├── intent/         → <Screen>Intent: acciones del usuario que el ViewModel procesa (sealed interface)
├── event/          → <Screen>Events: efectos de salida one-shot (navegación, toasts)
└── screen/         → Composable de la pantalla (stateless: recibe State, emite Intent)
```

**Reglas:**
- El ViewModel expone: `val uiState: StateFlow<ScreenState>` y `fun onIntent(intent: ScreenIntent)`
- Los Composable no tienen lógica de negocio — solo renderizan State y emiten Intent al ViewModel
- El ViewModel no referencia ningún tipo de View, Context, o Activity directamente
- Los Events (efectos one-shot) se emiten siempre por `Channel`

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
| Base de datos | NO | Room KMP |
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
| Entity (Room KMP) | `<Entidad>Entity` | `UserEntity`, `ServiceRecordEntity` |
| DataSource (interfaz) | `<Entidad><Tipo>DataSource` | `AuthRemoteDataSource`, `JobOffersLocalDataSource` |
| DataSource (impl) | `<Entidad><Tipo>DataSourceImpl` | `AuthRemoteDataSourceImpl` |
| ViewModel | `<Screen>ViewModel` | `LoginViewModel`, `JobOffersViewModel` |
| State | `<Screen>State` | `LoginState`, `JobOffersState` |
| Intent (entrada UI) | `<Screen>Intent` | `LoginIntent` (sealed interface) |
| Events (efectos one-shot) | `<Screen>Events` | `LoginEvents` (sealed interface) |
| Screen Composable | `<Screen>Screen` | `LoginScreen`, `JobOffersScreen` |
| Módulo Koin | `<feature>Module` | `authModule`, `jobOffersModule` |

---

## UI: Compose Multiplatform

Este proyecto usa Compose Multiplatform (CMP): la capa `presentation` completa
vive en `commonMain` y es compartida por Android e iOS.

- **No hay SwiftUI.** El entry point iOS es `ComposeUIViewController`, no una vista nativa.
- **UI en commonMain.** Pantallas, ViewModels, UiState y UiEvent se declaran en commonMain.
- **Recursos compartidos.** Strings, drawables y fonts usan `compose-resources` (`Res.*`).
- **Expect/actual de UI.** Solo cuando el comportamiento de un Composable difiere por plataforma
  (p.ej. status bar color, sharing nativo). Para el resto, commonMain es suficiente.
- **BD local.** Room KMP (`androidx.room:room-runtime`). Consulta `kb-room-kmp` cuando esté disponible.

Consulta `kb-cmp-ui` para las reglas de la capa presentation en CMP
y `kb-cmp-resources` para el uso de `compose-resources`.
