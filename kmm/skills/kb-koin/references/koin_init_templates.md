# Templates — initKoin y nativeModule

Estos ejemplos muestran patrones de inicialización y registro en Koin. No fijan dominios concretos del proyecto ni una infraestructura específica más allá del wiring de plataforma.

## initKoin — commonMain

```kotlin
// app/di/initKoin.kt
fun initKoin(config: KoinAppDeclaration? = null): KoinApplication {
    return startKoin {
        config?.invoke(this)
        modules(
            nativeModule,
            coreModule,
            featureAModule,
            featureBModule,
            appModule
        )
    }
}
```

---

## Inicialización Android — Application

```kotlin
class SampleApp : Application() {
    override fun onCreate() {
        super.onCreate()
        initKoin {
            androidLogger(Level.DEBUG)
            androidContext(this@SampleApp)
        }
    }
}
```

---

## Inicialización iOS — MainViewController

```kotlin
fun MainViewController() = ComposeUIViewController(configure = { initKoin() }) {
    AppEntryPoint()
}
```

---

## nativeModule — Android

```kotlin
actual val nativeModule = module {
    single<PlatformStorage> { AndroidPlatformStorage(get()) }
    single<PlatformNotifier> { AndroidPlatformNotifier(get()) }
}
```

---

## nativeModule — iOS

```kotlin
actual val nativeModule = module {
    single<PlatformStorage> { IOSPlatformStorage() }
    single<PlatformNotifier> { IOSPlatformNotifier() }
}
```

---

## expect/actual nativeModule — commonMain

```kotlin
expect val nativeModule: Module
```
