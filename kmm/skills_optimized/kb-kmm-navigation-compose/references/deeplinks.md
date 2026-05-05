# Deep Links — Code Examples

## `navDeepLink<T>` with `basePath` (recommended for `@Serializable` routes)

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

URI arguments are automatically mapped to the fields of the `@Serializable` route.

---

## `NavDeepLink` builder — custom URI with placeholders

```kotlin
composable<DetailRoute>(
    deepLinks = listOf(
        navDeepLink {
            uriPattern = "myapp://detail/{itemId}?showComments={showComments}"
        }
    )
) { ... }
```

The `{field}` placeholders must match the parameter names of the data class.

---

## Android configuration (`AndroidManifest.xml`)

`android:launchMode="singleTop"` is required for deep links to work correctly when the app is already running.

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

---

## Handling in `MainActivity` — app already open

When the activity is `singleTop` and the app is already running, the deep link arrives via `onNewIntent`, not `onCreate`. Without this, deep links only work on cold start:

```kotlin
// androidApp/src/main/kotlin/.../MainActivity.kt
override fun onNewIntent(intent: Intent) {
    super.onNewIntent(intent)
    navController.handleDeepLink(intent)
}
```

`navController` must be accessible at the activity level — hoist it out of the composable or store it in an instance variable.

---

## iOS configuration

In `iosApp/`:
- **URL Scheme**: add `URL types` in `Info.plist` with the `myapp` scheme.
- **Universal Links**: configure `apple-app-site-association` on the server and add `Associated Domains` in `Entitlements`.

### Swift → NavController bridge

The URL arrives in Swift but the `NavController` lives in Kotlin/Compose. A bridge is needed. Pattern: injectable class via Koin in `commonMain`:

```kotlin
// commonMain — DeepLinkHandler.kt
class DeepLinkHandler {
    private val _pendingUrl = MutableStateFlow<String?>(null)
    val pendingUrl: StateFlow<String?> = _pendingUrl.asStateFlow()

    fun handle(url: String) { _pendingUrl.value = url }
    fun consume() { _pendingUrl.value = null }
}

// Koin module (commonMain)
val deepLinkModule = module {
    single { DeepLinkHandler() }
}
```

In Swift, resolve the instance via the Koin bridge and inject the URL:

```swift
// iosApp/ContentView.swift
.onOpenURL { url in
    // get() resolves DeepLinkHandler from the Koin container
    KoinHelper.shared.getDeepLinkHandler().handle(url.absoluteString)
}
```

In Compose, observe and navigate. **Note:** `navigate(Uri)` is the required workaround for the iOS bridge — the URI must match the `basePath` defined in `navDeepLink<T>` of the target composable so that Navigation resolves the route correctly:

```kotlin
// Composable with access to navController
val deepLinkHandler: DeepLinkHandler = koinInject()
val pendingUrl by deepLinkHandler.pendingUrl.collectAsState()

LaunchedEffect(pendingUrl) {
    pendingUrl?.let { url ->
        navController.navigate(Uri.parse(url))   // iOS workaround — see note
        deepLinkHandler.consume()
    }
}
```