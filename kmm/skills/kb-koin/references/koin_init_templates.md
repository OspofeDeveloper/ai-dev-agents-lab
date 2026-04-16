# Templates — initKoin y nativeModule

## initKoin — commonMain

```kotlin
// app/di/initKoin.kt
fun initKoin(config: KoinAppDeclaration? = null): KoinApplication {
    return startKoin {
        config?.invoke(this)
        modules(
            nativeModule,       // primero: DataStore, BLE, Firebase de plataforma
            coreModule,         // segundo: HttpClients, CoreRepository, IdentityApi
            authModule,
            pumpsModule,
            locationModule,
            alarmModule,
            BLEModule,
            firebaseModule,
            appModule,
            parametersModule,
            resetsModule,
            cyclesModule,
            lightsModule,
            deviceModule
        )
    }
}
```

---

## Inicialización Android — Application

```kotlin
// androidMain/.../SaciPumpsApp.kt
class SaciPumpsApp : Application() {
    override fun onCreate() {
        super.onCreate()
        initKoin {
            androidLogger(Level.DEBUG)
            androidContext(this@SaciPumpsApp)
        }
    }
}
```

---

## Inicialización iOS — MainViewController

```kotlin
// iosMain/.../MainViewController.kt
fun MainViewController(
    nativeFactory: NativeFactory
) = ComposeUIViewController(configure = { initKoin() }) {
    NativeFactoryProvider.factory = nativeFactory
    AppEntryPoint()
}
```

---

## nativeModule — Android

```kotlin
// androidMain/.../nativeModule.android.kt
actual val nativeModule = module {
    factoryOf(::AndroidBLEProvisioningService)

    single<BLERepository>(named(AndroidQualifiers.AndroidBleRepository)) {
        AndroidBLERepositoryImpl(get())
    }

    single { FirebaseApi() }

    single<FirebaseRepository>(named(AndroidQualifiers.AndroidFirebaseRepository)) {
        AndroidFirebaseRepositoryImpl(get())
    }

    single { dataStore(get()) }  // get() resuelve el contexto Android
}
```

---

## nativeModule — iOS

```kotlin
// iosMain/.../nativeModule.ios.kt
actual val nativeModule = module {
    factoryOf(::IOSBLEProvisioningService)

    single<BLERepository>(named(iOSQualifier.iOSBleRepository)) {
        IOSBLERepositoryImpl(get())
    }

    single<FirebaseRepository>(named(iOSQualifier.iOSFirebaseRepository)) {
        IOSFirebaseRepositoryImpl(get())
    }

    single { IOSFirebaseService() }

    single { getDataStore() }  // sin contexto en iOS
}
```

---

## expect/actual nativeModule — commonMain

```kotlin
// commonMain/.../nativeModule.kt
expect val nativeModule: Module
```
