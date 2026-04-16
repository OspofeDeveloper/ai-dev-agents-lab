# Deep Links — Ejemplos de Código

## `navDeepLink<T>` con `basePath` (recomendado para rutas @Serializable)

```kotlin
import androidx.navigation.navDeepLink

composable<ProfileRoute>(
    deepLinks = listOf(
        navDeepLink<ProfileRoute>(
            basePath = "https://example.com/profile"
        )
    )
) { backStackEntry ->
    val route: ProfileRoute = backStackEntry.toRoute()
    ProfileScreen(userId = route.userId)
}
```

Los argumentos del URI se mapean automáticamente a los campos de la ruta `@Serializable`.

## `NavDeepLink` builder — URI custom con placeholders

```kotlin
composable<DetailRoute>(
    deepLinks = listOf(
        navDeepLink {
            uriPattern = "myapp://detail/{itemId}?showComments={showComments}"
        }
    )
) { ... }
```

Los placeholders `{campo}` deben coincidir con los nombres de los parámetros de la data class.

---

## Configuración Android (`AndroidManifest.xml`)

`android:launchMode="singleTop"` es necesario para que los deep links funcionen correctamente cuando la app ya está en ejecución.

```xml
<!-- androidApp/src/main/AndroidManifest.xml -->
<activity
    android:name=".MainActivity"
    android:launchMode="singleTop">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="https"
              android:host="example.com"
              android:pathPrefix="/profile" />
    </intent-filter>
</activity>
```

## Manejo en `MainActivity` — app ya abierta

Cuando la actividad es `singleTop` y la app ya está corriendo, el deep link llega por `onNewIntent`, no por `onCreate`. Sin esto, los deep links solo funcionan en cold start:

```kotlin
// androidApp/src/main/kotlin/.../MainActivity.kt
override fun onNewIntent(intent: Intent) {
    super.onNewIntent(intent)
    navController.handleDeepLink(intent)
}
```

`navController` debe ser accesible a nivel de actividad — hoistarlo fuera del composable o guardarlo en una variable de instancia.

---

## Configuración iOS

En `iosApp/`:
- **URL Scheme**: añadir `URL types` en `Info.plist` con el esquema `myapp`
- **Universal Links**: configurar `apple-app-site-association` en el servidor y añadir `Associated Domains` en `Entitlements`

### Puente Swift → NavController

El URL llega en Swift pero el NavController vive en Kotlin/Compose. Se necesita un puente. Patrón: clase injectable con Koin en `commonMain`:

```kotlin
// commonMain — DeepLinkHandler.kt
class DeepLinkHandler {
    private val _pendingUrl = MutableStateFlow<String?>(null)
    val pendingUrl: StateFlow<String?> = _pendingUrl.asStateFlow()

    fun handle(url: String) { _pendingUrl.value = url }
    fun consume() { _pendingUrl.value = null }
}

// Módulo Koin (commonMain)
val deepLinkModule = module {
    single { DeepLinkHandler() }
}
```

En Swift, obtener la instancia vía el bridge de Koin e inyectar el URL:

```swift
// iosApp/ContentView.swift
.onOpenURL { url in
    // get() resuelve DeepLinkHandler desde el contenedor Koin
    KoinHelper.shared.getDeepLinkHandler().handle(url.absoluteString)
}
```

En Compose, observar y navegar. **Nota:** `navigate(Uri)` es el workaround necesario para el puente iOS — el URI debe coincidir con el `basePath` definido en `navDeepLink<T>` del composable destino para que Navigation resuelva la ruta correctamente:

```kotlin
// Composable con acceso al navController
val deepLinkHandler: DeepLinkHandler = koinInject()
val pendingUrl by deepLinkHandler.pendingUrl.collectAsState()

LaunchedEffect(pendingUrl) {
    pendingUrl?.let { url ->
        navController.navigate(Uri.parse(url))   // workaround iOS — ver nota
        deepLinkHandler.consume()
    }
}
```