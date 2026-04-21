# ViewModel Scoping y LoginEvents — Ejemplos de Código

## Efectos de navegación — definición compartida

Los efectos nombran **hechos de dominio**, no destinos. Ambos patrones (Channel y StateFlow) usan el mismo sealed interface:

```kotlin
sealed interface LoginEvents {
    data object LoginSuccess : LoginEvents
    data object RegistrationRequired : LoginEvents
}
```

## Separación entre `State` y `Events`

El patrón correcto no es "todo error a eventos" ni "todo outcome a state".

Ejemplo de login:

```kotlin
data class LoginState(
    val isLoading: Boolean = false,
    val error: LoginUiError? = null,
)

sealed interface LoginUiError {
    data class InvalidCredentials(val attemptsRemaining: Int?) : LoginUiError
    data object AccountBlocked : LoginUiError
    data object Generic : LoginUiError
}

sealed interface LoginEvents {
    data object LoginSuccess : LoginEvents
    data object FirstLoginRequired : LoginEvents
    data object AccountInactive : LoginEvents
}
```

Regla práctica del ejemplo:

- `InvalidCredentials`, `AccountBlocked`, `Generic` viven en `State`
- `LoginSuccess`, `FirstLoginRequired`, `AccountInactive` viven en `Events`

`AccountInactive` va en `Events` aunque una app termine mostrándolo como error, porque esa traducción depende de composición externa y puede variar por brand.

## ViewModel scoped a pantalla (default)

```kotlin
// Con Koin (recomendado en CMP)
composable<HomeRoute> {
    val viewModel: HomeViewModel = koinNavViewModel()
    HomeScreen(viewModel = viewModel)
}
```

## ViewModel scoped a nested graph

```kotlin
composable<ProfileRoute> { backStackEntry ->
    // Obtener el backStackEntry del grafo padre (no de esta ruta)
    val graphEntry = remember(backStackEntry) {
        navController.getBackStackEntry(MainGraph)
    }
    val viewModel: SharedViewModel = koinViewModel(viewModelStoreOwner = graphEntry)
    ProfileScreen(viewModel = viewModel)
}
```

## `koinNavViewModel()` con parámetros desde la ruta

```kotlin
// composeApp/src/commonMain/kotlin/com/example/app/screens/profile/ProfileScreen.kt
composable<ProfileRoute> { backStackEntry ->
    val route: ProfileRoute = backStackEntry.toRoute()
    val viewModel: ProfileViewModel = koinNavViewModel(
        parameters = { parametersOf(route.userId) }
    )
    ProfileScreen(viewModel = viewModel)
}
```

---

## LoginEvents — Patrón Channel (recomendado)

El NavHost decide adónde ir; la feature declara qué ocurrió.

### ViewModel

```kotlin
// composeApp/src/commonMain/kotlin/com/example/app/screens/login/LoginViewModel.kt
class LoginViewModel : ViewModel() {

    private val _events = Channel<LoginEvents>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    fun onLoginSuccess() {
        viewModelScope.launch {
            _events.send(LoginEvents.LoginSuccess)
        }
    }
}
```

### Composable receptor

```kotlin
@Composable
fun LoginScreen(
    viewModel: LoginViewModel = koinNavViewModel(),
    onLoginSuccess: () -> Unit,
    onRegistrationRequired: () -> Unit
) {
    LaunchedEffect(viewModel) {  // key = viewModel, no Unit
        viewModel.events.collect { event ->
            when (event) {
                LoginEvents.LoginSuccess        -> onLoginSuccess()
                LoginEvents.RegistrationRequired -> onRegistrationRequired()
            }
        }
    }
    // ... UI
}
```

### NavHost — decide el destino

```kotlin
composable<LoginRoute> {
    LoginScreen(
        onLoginSuccess        = { navController.navigate(HomeRoute) },
        onRegistrationRequired = { navController.navigate(RegisterRoute) }
    )
}
```

## Mismo hecho, distinta traducción por app

El ViewModel no decide si un mismo hecho navega o muestra error visual. Esa traducción pertenece a `app`.

### ViewModel

```kotlin
when (error) {
    is AuthError.AccountInactive -> {
        _events.send(LoginEvents.AccountInactive)
    }
    is AuthError.AccountBlocked -> {
        _state.update { it.copy(error = LoginUiError.AccountBlocked) }
    }
}
```

### App FelizVita

```kotlin
LoginScreen(
    onAccountInactive = {
        navController.navigate(AccountInactiveRoute)
    },
)
```

### App Cuideo

```kotlin
LoginScreen(
    onAccountInactive = {
        showInactiveAccountError()
    },
)
```

Lo importante es que el hecho emitido por el ViewModel es el mismo. La diferencia de comportamiento no se modela dentro de la feature.

---

## LoginEvents — Alternativa StateFlow con reset

### ViewModel

```kotlin
data class LoginState(
    val isLoading: Boolean = false,
    val event: LoginEvents? = null   // null = sin evento pendiente
)

class LoginViewModel : ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state = _state.asStateFlow()

    fun onLoginSuccess() {
        _state.update { it.copy(event = LoginEvents.LoginSuccess) }
    }

    fun onEventHandled() {
        _state.update { it.copy(event = null) }
    }
}
```

### Composable — consumir y resetear

```kotlin
val state by viewModel.state.collectAsState()

LaunchedEffect(state.event) {
    state.event?.let { event ->
        when (event) {
            LoginEvents.LoginSuccess        -> onLoginSuccess()
            LoginEvents.RegistrationRequired -> onRegistrationRequired()
        }
        viewModel.onEventHandled()
    }
}
```
