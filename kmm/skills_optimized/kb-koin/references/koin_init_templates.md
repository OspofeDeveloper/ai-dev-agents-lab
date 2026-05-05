# Templates — initKoin and nativeModule

## initKoin — commonMain

```kotlin
// app/di/initKoin.kt
fun initKoin(config: KoinAppDeclaration? = null): KoinApplication =
    startKoin {
        config?.invoke(this)
        modules(nativeModule, coreModule, featureAModule, featureBModule, appModule)
    }
```

## Android — Application.onCreate

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

## iOS — MainViewController

```kotlin
fun MainViewController() = ComposeUIViewController(configure = { initKoin() }) {
    AppEntryPoint()
}
```

## nativeModule — expect (commonMain)

```kotlin
expect val nativeModule: Module
```

## nativeModule — actual Android / iOS

```kotlin
// androidMain
actual val nativeModule = module {
    single<PlatformStorage> { AndroidPlatformStorage(get()) }
    single<PlatformNotifier> { AndroidPlatformNotifier(get()) }
}

// iosMain
actual val nativeModule = module {
    single<PlatformStorage> { IOSPlatformStorage() }
    single<PlatformNotifier> { IOSPlatformNotifier() }
}
```