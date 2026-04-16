---
name: kb-koin
description: "Base de conocimiento de Koin DI en proyectos KMM: organización de módulos por feature, tipos de registro (single/factory/viewModelOf/singleOf), patrón qualifier con enums, nativeModule expect/actual para código de plataforma, initKoin en Android e iOS, y orden de módulos."
argument-hint: ""
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Koin DI KMM — Base de Conocimiento

## Regla 1: Organización de módulos

Cada feature tiene su propio módulo Koin en `<feature>/di/<feature>Module.kt`. Los módulos de infraestructura viven en `core/`. El módulo de app (`appModule`) agrupa ViewModels y Use Cases que pertenecen a múltiples features o a la navegación principal.

```
app/di/
  initKoin.kt       ← punto de entrada, registra todos los módulos
  appModule.kt      ← ViewModels y UseCases de nivel app

core/di/
  coreModule.kt     ← HttpClients, CoreRepository, configuración BuildConfig
  nativeModule.kt   ← expect val nativeModule (DataStore, BLE, Firebase por plataforma)

core/ble/di/
  BLEModule.kt      ← BLERepository via expect/actual factory function

core/firebase/di/
  firebaseModule.kt ← FirebaseRepository via expect/actual factory function

features/<feature>/di/
  <feature>Module.kt
```

Todos los módulos se registran en `initKoin`. No hay módulos dinámicos ni carga lazy de módulos.

→ Templates: `references/koin_init_templates.md`

---

## Regla 2: initKoin — inicialización

Existe una única función `initKoin(config: KoinAppDeclaration? = null)` en `commonMain`. Cada plataforma la llama de forma distinta:

- **Android**: en `Application.onCreate()`, pasando `androidLogger` y `androidContext`
- **iOS**: en `ComposeUIViewController(configure = { initKoin() })`

El parámetro `config` permite que cada plataforma inyecte configuración específica (contexto Android, logger) sin que `initKoin` necesite saber nada de plataforma.

→ Templates: `references/koin_init_templates.md`

---

## Regla 3: Tipos de registro

| Tipo | DSL | Ciclo de vida | Cuándo usarlo |
|------|-----|---------------|---------------|
| `single` | `single { }` / `singleOf(::Class)` | Una instancia para toda la app | Repositorios, APIs/Services, HttpClients, configuración BuildConfig |
| `factory` | `factory { }` / `factoryOf(::Class)` | Nueva instancia en cada inyección | Use Cases |
| `viewModel` | `viewModelOf(::Class)` | Gestionado por el ciclo de vida de Compose/Voyager | ViewModels de screens |
| `single` (ViewModel) | `singleOf(::Class)` | Una instancia compartida entre screens | ViewModels que deben sobrevivir a la navegación — uso excepcional |

**Regla de oro**: si tienes dudas entre `single` y `factory` para un Use Case, usa `factory`. Los Use Cases son operaciones, no servicios.

---

## Regla 4: Patrón qualifier

Cuando hay múltiples instancias del mismo tipo en el grafo de Koin, se usan **enums como qualifiers** para distinguirlas. Esto evita colisiones de tipos y hace el código legible.

```kotlin
// Declaración del qualifier (un enum por dominio)
enum class CoreQualifiers { AppKtorClient, AppBaseUrl, FirebaseRegionUrl }

// Registro con qualifier
single(named(CoreQualifiers.AppKtorClient)) { HttpClient { ... } }

// Consumo con qualifier
single { AuthService(get(named(CoreQualifiers.AppKtorClient))) }
```

Los qualifiers del proyecto se agrupan por dominio:

| Enum | Fichero | Qué distingue |
|------|---------|---------------|
| `CoreQualifiers` | `core/di/CoreQualifiers.kt` | HttpClient de app, URLs de app |
| `IdentityQualifiers` | `core/identity/data/IdentityQualifiers.kt` | HttpClient de Identity, URLs y credenciales OAuth |
| `AndroidQualifiers` | `androidMain/.../AndroidQualifiers.kt` | Implementaciones Android de BLE y Firebase |
| `iOSQualifier` | `iosMain/.../iOSQualifier.kt` | Implementaciones iOS de BLE y Firebase |

Los qualifiers de plataforma (`AndroidQualifiers`, `iOSQualifier`) se usan solo en `nativeModule` y no se consumen desde `commonMain`.

---

## Regla 5: Estructura estándar de módulo de feature

Todo módulo de feature sigue esta estructura de registro, de más compartido a más volátil:

```
single  → Api / Service      (inyecta HttpClient con qualifier)
single  → Repository         (inyecta Api/Service)
factory → Use Cases          (inyectan Repository)
viewModelOf → ViewModels     (inyectan Use Cases)
```

Short form con `singleOf` y `factoryOf`:

```kotlin
val authModule = module {
    singleOf(::AuthService)          // si no necesita qualifier
    singleOf(::AuthRepositoryImpl) bind AuthRepository::class
    factoryOf(::LoginUseCase)
    viewModelOf(::LoginViewModel)
}
```

Cuando el constructor necesita un qualifier (caso habitual para el HttpClient), se usa la forma larga:

```kotlin
single { AuthService(get(named(CoreQualifiers.AppKtorClient))) }
```

→ Templates: `references/koin_feature_module_template.md`

---

## Regla 6: nativeModule — código específico de plataforma

`nativeModule` es un `expect val` en `commonMain` con implementaciones `actual` en `androidMain` e `iosMain`. Se usa para registrar dependencias cuya implementación varía por plataforma: DataStore, BLE y Firebase.

Cada plataforma usa sus propios qualifiers (`AndroidQualifiers` / `iOSQualifier`) para registrar las implementaciones específicas:

```kotlin
// androidMain
actual val nativeModule = module {
    single<BLERepository>(named(AndroidQualifiers.AndroidBleRepository)) {
        AndroidBLERepositoryImpl(get())
    }
    single { dataStore(get()) }   // DataStore con contexto Android
}

// iosMain
actual val nativeModule = module {
    single<BLERepository>(named(iOSQualifier.iOSBleRepository)) {
        IOSBLERepositoryImpl(get())
    }
    single { getDataStore() }     // DataStore en iOS no necesita contexto
}
```

`nativeModule` siempre se registra **primero** en `initKoin` porque `coreModule` depende de DataStore.

→ Templates: `references/koin_init_templates.md`

---

## Regla 7: Módulos con factory function expect/actual

`BLEModule` y `firebaseModule` usan una factory function `expect`/`actual` para crear la implementación de plataforma sin usar qualifiers de plataforma en commonMain:

```kotlin
// commonMain — BLEModule.kt
val BLEModule = module {
    single<BLERepository> { createBLERepositoryImpl() }
}

// expect en commonMain
expect fun createBLERepositoryImpl(): BLERepository

// actual en androidMain
actual fun createBLERepositoryImpl(): BLERepository = AndroidBLERepositoryImpl(...)

// actual en iosMain
actual fun createBLERepositoryImpl(): BLERepository = IOSBLERepositoryImpl(...)
```

Este patrón es más limpio que el qualifier de plataforma cuando la implementación es única por plataforma y no hay necesidad de distinguir entre varias. Se usa cuando `commonMain` solo necesita **una** instancia del tipo.

---

## Regla 8: Orden en initKoin y resolución lazy

Koin resuelve dependencias de forma **lazy**: una instancia se crea la primera vez que se solicita, no cuando se registra el módulo. Por eso el orden de los módulos en `initKoin` no determina el orden de instanciación.

El único orden que importa es:

```
nativeModule    ← primero: aporta DataStore, que coreModule necesita
coreModule      ← segundo: aporta HttpClients y CoreRepository, que las features necesitan
[features]      ← cualquier orden entre ellas
appModule       ← último o junto a features: depende de que las features estén registradas
```

En Android, el bloque `config?.invoke(this)` (que añade `androidContext`) se ejecuta antes de `modules(...)`, por lo que el contexto está siempre disponible independientemente del orden de módulos.

---

## Regla 9: Dependencias de build

```toml
# gradle/libs.versions.toml
[libraries]
koin-core              = { module = "io.insert-koin:koin-core" }
koin-android           = { module = "io.insert-koin:koin-android" }
koin-compose           = { module = "io.insert-koin:koin-compose" }
koin-compose-viewmodel = { module = "io.insert-koin:koin-compose-viewmodel" }
koin-test              = { module = "io.insert-koin:koin-test" }
voyager-koin           = { module = "cafe.adriel.voyager:voyager-koin" }
```

En `composeApp/build.gradle.kts`:

```kotlin
commonMain.dependencies {
    implementation(libs.koin.core)
    implementation(libs.koin.compose)
    implementation(libs.koin.compose.viewmodel)
    implementation(libs.voyager.koin)
}
androidMain.dependencies {
    implementation(libs.koin.android)
}
```
