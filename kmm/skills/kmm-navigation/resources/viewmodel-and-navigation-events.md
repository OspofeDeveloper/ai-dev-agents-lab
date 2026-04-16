# ViewModel Scoping y NavigationSideEffect — Ejemplos de Código

## Efectos de navegación — definición compartida

Los efectos nombran **hechos de dominio**, no destinos. Ambos patrones (Channel y StateFlow) usan el mismo sealed interface:

```kotlin
sealed interface LoginEffect {
    data object LoginSuccess : LoginEffect
    data object RegistrationRequired : LoginEffect
}
```

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

## NavigationSideEffect — Patrón Channel (recomendado)

El NavHost decide adónde ir; la feature declara qué ocurrió.

### ViewModel

```kotlin
// composeApp/src/commonMain/kotlin/com/example/app/screens/login/LoginViewModel.kt
class LoginViewModel : ViewModel() {

    private val _effect = Channel<LoginEffect>(Channel.BUFFERED)
    val effect = _effect.receiveAsFlow()

    fun onLoginSuccess() {
        viewModelScope.launch {
            _effect.send(LoginEffect.LoginSuccess)
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
        viewModel.effect.collect { effect ->
            when (effect) {
                LoginEffect.LoginSuccess        -> onLoginSuccess()
                LoginEffect.RegistrationRequired -> onRegistrationRequired()
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

---

## NavigationSideEffect — Alternativa StateFlow con reset

### ViewModel

```kotlin
data class LoginUiState(
    val isLoading: Boolean = false,
    val effect: LoginEffect? = null   // null = sin efecto pendiente
)

class LoginViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState = _uiState.asStateFlow()

    fun onLoginSuccess() {
        _uiState.update { it.copy(effect = LoginEffect.LoginSuccess) }
    }

    fun onEffectHandled() {
        _uiState.update { it.copy(effect = null) }
    }
}
```

### Composable — consumir y resetear

```kotlin
val uiState by viewModel.uiState.collectAsState()

LaunchedEffect(uiState.effect) {
    uiState.effect?.let { effect ->
        when (effect) {
            LoginEffect.LoginSuccess        -> onLoginSuccess()
            LoginEffect.RegistrationRequired -> onRegistrationRequired()
        }
        viewModel.onEffectHandled()
    }
}
```
