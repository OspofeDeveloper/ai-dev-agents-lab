# Koin DI KMM — Templates de implementación

## Módulo de feature tipo

```kotlin
val featureModule = module {
    // Infraestructura
    single { MyApi(get()) }
    single<MyRepository> { MyRepositoryImpl(get()) }

    // Use Cases
    factory { GetSomethingUseCase(get()) }
    factory { SaveSomethingUseCase(get()) }

    // ViewModels
    viewModelOf(::MyViewModel)
}
```

## nativeModule — expect/actual

```kotlin
// commonMain
expect val nativeModule: Module

// androidMain
actual val nativeModule = module {
    single { androidContext().dataStore }
}

// iosMain
actual val nativeModule = module {
    single { createDataStore() }
}
```

## initKoin completo

```kotlin
// commonMain
fun initKoin(config: KoinAppDeclaration? = null) {
    startKoin {
        config?.invoke(this)
        modules(
            nativeModule,
            coreModule,
            featureAModule,
            featureBModule,
            appModule,
        )
    }
}

// androidMain — Application.onCreate()
override fun onCreate() {
    super.onCreate()
    initKoin {
        androidLogger()
        androidContext(this@MyApp)
    }
}

// iosMain — ComposeUIViewController configure
fun MainViewController() = ComposeUIViewController(
    configure = { initKoin() }
) { App() }
```

## Qualifiers con enum

```kotlin
// core/di/NetworkQualifiers.kt
enum class NetworkQualifiers { APP_CLIENT, IDENTITY_CLIENT }

val coreModule = module {
    single(NetworkQualifiers.APP_CLIENT) { buildAppClient() }
    single(NetworkQualifiers.IDENTITY_CLIENT) { buildIdentityClient() }
}

// consumidor
val appClient: HttpClient by inject(NetworkQualifiers.APP_CLIENT)
```

## Módulo con factory function expect/actual

Para una única implementación por plataforma sin qualifier:

```kotlin
// commonMain
expect fun platformModule(): Module

// androidMain
actual fun platformModule() = module { single { AndroidBleManager() } }

// iosMain
actual fun platformModule() = module { single { IosBleManager() } }
```
