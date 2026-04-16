---
name: kb-koin
description: "Base de conocimiento de Koin DI en proyectos KMM: organización de módulos por feature, tipos de registro, patrón qualifier con enums, nativeModule expect/actual, initKoin y orden de módulos."
argument-hint: ""
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Koin DI KMM — Base de Conocimiento

## Regla 1: Koin define wiring, no ownership arquitectónico

Koin solo resuelve y cablea dependencias. No decide por sí sola qué pieza pertenece a `core`, a una feature o a `app`.

La ubicación y ownership de cada pieza se decide con:

- `kb-kmm-core-layer`
- `kb-kmm-feature-clean-architecture`
- `kb-kmm-app-layer`
- `kb-kmm-clean-architecture`

Una vez decidida esa ubicación, Koin registra las piezas en módulos coherentes con esa estructura.

---

## Regla 2: Organización de módulos alineada con la arquitectura

```text
app/di/
  initKoin.kt       ← punto de entrada, registra todos los módulos
  appModule.kt      ← ViewModels y UseCases de nivel app

core/di/
  coreModule.kt     ← infraestructura transversal y configuración BuildConfig
  nativeModule.kt   ← expect val nativeModule para código específico de plataforma

features/<feature>/di/
  <feature>Module.kt
```

Todos los módulos se registran en `initKoin`. No hay módulos dinámicos ni carga lazy de módulos.

→ Templates: `references/koin_init_templates.md`

---

## Regla 3: initKoin — inicialización

Existe una única función `initKoin(config: KoinAppDeclaration? = null)` en `commonMain`. Cada plataforma la llama de forma distinta:

- **Android**: en `Application.onCreate()`, pasando `androidLogger` y `androidContext`
- **iOS**: en `ComposeUIViewController(configure = { initKoin() })`

El parámetro `config` permite que cada plataforma inyecte configuración específica sin que `initKoin` necesite conocer detalles de plataforma.

→ Templates: `references/koin_init_templates.md`

---

## Regla 4: Tipos de registro

| Tipo | DSL | Ciclo de vida | Cuándo usarlo |
|------|-----|---------------|---------------|
| `single` | `single { }` / `singleOf(::Class)` | Una instancia para toda la app | Repositorios, servicios, APIs, clientes de infraestructura, configuración |
| `factory` | `factory { }` / `factoryOf(::Class)` | Nueva instancia en cada inyección | Use Cases |
| `viewModel` | `viewModelOf(::Class)` | Gestionado por el ciclo de vida de Compose/Voyager | ViewModels de screens |
| `single` (ViewModel) | `singleOf(::Class)` | Una instancia compartida entre screens | ViewModels compartidos, uso excepcional |

**Regla de oro**: si tienes dudas entre `single` y `factory` para un Use Case, usa `factory`.

---

## Regla 5: Los qualifiers distinguen instancias, no definen arquitectura

Cuando hay múltiples instancias del mismo tipo en el grafo de Koin, se usan **enums como qualifiers** para distinguirlas.

```kotlin
enum class NetworkQualifiers { ApiHttpClient, ApiBaseUrl }

single(named(NetworkQualifiers.ApiHttpClient)) { HttpClient { ... } }

single { AuthService(get(named(NetworkQualifiers.ApiHttpClient))) }
```

Los qualifiers se agrupan por dominio, no por librería. Ejemplos habituales:

| Enum | Fichero | Qué distingue |
|------|---------|---------------|
| `NetworkQualifiers` | `core/di/NetworkQualifiers.kt` | clientes HTTP, URLs base, configuración de red |
| `AuthQualifiers` | `core/auth/data/AuthQualifiers.kt` | cliente de Identity, client_id, grant types |
| `AndroidQualifiers` | `androidMain/.../AndroidQualifiers.kt` | implementaciones Android |
| `iOSQualifier` | `iosMain/.../iOSQualifier.kt` | implementaciones iOS |

Los qualifiers de plataforma se usan solo en `nativeModule` y no se consumen desde `commonMain`.

---

## Regla 6: Los módulos registran la estructura ya decidida por las skills de capa

En una feature típica, el módulo suele registrar dependencias en un orden parecido a este:

```text
single     -> Api / Service
single     -> Repository
factory    -> Use Cases
viewModelOf -> ViewModels
```

Ese orden es un patrón de wiring habitual, no una regla arquitectónica independiente de las skills de capa.

Short form con `singleOf` y `factoryOf`:

```kotlin
val authModule = module {
    singleOf(::RemoteAuthService)
    singleOf(::AuthRepositoryImpl) bind AuthRepository::class
    factoryOf(::LoginUseCase)
    viewModelOf(::LoginViewModel)
}
```

Cuando el constructor necesita un qualifier, se usa la forma larga:

```kotlin
single { RemoteAuthService(get(named(NetworkQualifiers.ApiHttpClient))) }
```

→ Templates: `references/koin_feature_module_template.md`

---

## Regla 7: nativeModule — código específico de plataforma

`nativeModule` es un `expect val` en `commonMain` con implementaciones `actual` en `androidMain` e `iosMain`. Se usa para registrar dependencias cuya implementación varía por plataforma: DataStore, BLE, Firebase o equivalentes.

`nativeModule` siempre se registra **primero** en `initKoin` cuando otros módulos dependen de infraestructura de plataforma.

→ Templates: `references/koin_init_templates.md`

---

## Regla 8: Módulos con factory function expect/actual

Cuando `commonMain` necesita una única implementación por plataforma y no hace falta distinguir varias instancias, puede usarse una factory function `expect`/`actual` en lugar de qualifiers de plataforma.

---

## Regla 9: Orden en initKoin y resolución lazy

Koin resuelve dependencias de forma **lazy**: una instancia se crea la primera vez que se solicita, no cuando se registra el módulo.

El orden recomendado es:

```text
nativeModule
coreModule
[features]
appModule
```

El orden expresa dependencias estructurales, no inicialización inmediata.

---

## Regla 10: Koin no define arquitectura ni stack técnico

Koin solo cablea dependencias. Las reglas de arquitectura viven en la skill correspondiente. Las reglas de networking, auth o persistencia viven en sus propias skills.

Si una regla sigue siendo cierta aunque cambie Koin, no pertenece aquí.

---

## Regla 11: Esta skill se combina con las skills de capa y de infraestructura

Esta skill se usa junto con:

- `kb-kmm-core-layer`
- `kb-kmm-feature-clean-architecture`
- `kb-kmm-app-layer`
- skills de networking, auth o storage cuando la dependencia registrada pertenezca a esas dimensiones

Koin registra y resuelve dependencias; no redefine las reglas conceptuales de esas piezas.
