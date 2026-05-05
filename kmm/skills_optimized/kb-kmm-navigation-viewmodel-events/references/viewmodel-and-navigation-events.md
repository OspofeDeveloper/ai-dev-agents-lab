# ViewModel Scoping and `LoginEvents` — Code Examples

## Shared navigation effects

Effects name **domain facts**, not destinations. Both patterns (`Channel` and `StateFlow`) use the same sealed interface:

```kotlin
sealed interface LoginEvents {
    data object LoginSuccess : LoginEvents
    data object RegistrationRequired : LoginEvents
}
```

## `State` vs `Events`

The correct pattern is neither "every error goes to events" nor "every outcome goes to state".

Login example:

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

Practical rule in this example:

- `InvalidCredentials`, `AccountBlocked`, `Generic` live in `State`
- `LoginSuccess`, `FirstLoginRequired`, `AccountInactive` live in `Events`

`AccountInactive` stays in `Events` even if one app renders it as an error, because that translation depends on external composition and may vary by brand.

## Screen-scoped ViewModel (default)

```kotlin
// With Koin (recommended in CMP)
composable<HomeRoute> {
    val viewModel: HomeViewModel = koinNavViewModel()
    HomeScreen(viewModel = viewModel)
}
```

## Nested-graph-scoped ViewModel

```kotlin
composable<ProfileRoute> { backStackEntry ->
    // Get the parent graph backStackEntry, not this route entry
    val graphEntry = remember(backStackEntry) {
        navController.getBackStackEntry(MainGraph)
    }
    val viewModel: SharedViewModel = koinViewModel(viewModelStoreOwner = graphEntry)
    ProfileScreen(viewModel = viewModel)
}
```

## `koinNavViewModel()` with route parameters

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

## `LoginEvents` — `Channel` pattern (recommended)

The `NavHost` decides where to go; the feature declares what happened.

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

### Receiving Composable

```kotlin
@Composable
fun LoginScreen(
    viewModel: LoginViewModel = koinNavViewModel(),
    onLoginSuccess: () -> Unit,
    onRegistrationRequired: () -> Unit
) {
    LaunchedEffect(viewModel) {  // key = viewModel, not Unit
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

### `NavHost` decides the destination

```kotlin
composable<LoginRoute> {
    LoginScreen(
        onLoginSuccess        = { navController.navigate(HomeRoute) },
        onRegistrationRequired = { navController.navigate(RegisterRoute) }
    )
}
```

## Same fact, different app translation

The ViewModel does not decide whether the same fact navigates or shows a visual error. That translation belongs to `app`.

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

### App A

```kotlin
LoginScreen(
    onAccountInactive = {
        navController.navigate(AccountInactiveRoute)
    },
)
```

### App B

```kotlin
LoginScreen(
    onAccountInactive = {
        showInactiveAccountError()
    },
)
```

The important point is that the fact emitted by the ViewModel is the same. Behavioral differences are not modeled inside the feature.

---

## `LoginEvents` — `StateFlow` with reset

### ViewModel

```kotlin
data class LoginState(
    val isLoading: Boolean = false,
    val event: LoginEvents? = null   // null = no pending event
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

### Composable — consume and reset

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
