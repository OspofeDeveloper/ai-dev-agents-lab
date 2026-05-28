---
name: kb-tasks-kmm-navigation-viewmodel-events
description: Implementación concreta del patrón Intent/Events en proyectos KMM: Channel para efectos one-shot, LaunchedEffect(viewModel), naming de sealed interfaces y coordinación ViewModel-Composable. Úsalo cuando haya que implementar navegación por efectos desde un ViewModel.
allowed-tools: [Read]
user-invocable: false
---

# KMM Navigation ViewModel Events — Implementación

→ Reglas arquitectónicas del patrón Intent/Events: `kb-plan-kmm-navigation-viewmodel-events`

## Estructura base del ViewModel

```kotlin
class LoginViewModel : ViewModel() {

    private val _state = MutableStateFlow(LoginUiState())
    val state: StateFlow<LoginUiState> = _state.asStateFlow()

    private val _events = Channel<LoginEvents>(Channel.BUFFERED)
    val events: ReceiveChannel<LoginEvents> = _events

    fun onIntent(intent: LoginIntent) {
        when (intent) {
            is LoginIntent.Submit -> handleSubmit(intent.email, intent.password)
        }
    }

    private fun handleSubmit(email: String, password: String) {
        viewModelScope.launch {
            // lógica de negocio...
            _events.send(LoginEvents.LoginSuccess)
        }
    }
}
```

## Sealed interfaces Intent y Events

```kotlin
sealed interface LoginIntent {
    data class Submit(val email: String, val password: String) : LoginIntent
    data object ForgotPassword : LoginIntent
}

sealed interface LoginEvents {
    data object LoginSuccess : LoginEvents
    data object RegistrationRequired : LoginEvents
    data object SessionExpired : LoginEvents
}
```

Los eventos nombran hechos semánticos, no destinos concretos del grafo.

## Colección de efectos en el Composable

```kotlin
@Composable
fun LoginScreen(
    viewModel: LoginViewModel = koinViewModel(),
    onLoginSuccess: () -> Unit,
    onRegistrationRequired: () -> Unit,
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    // LaunchedEffect usa el viewModel como key — no Unit
    LaunchedEffect(viewModel) {
        viewModel.events.consumeEach { event ->
            when (event) {
                LoginEvents.LoginSuccess -> onLoginSuccess()
                LoginEvents.RegistrationRequired -> onRegistrationRequired()
                LoginEvents.SessionExpired -> { /* manejado en app */ }
            }
        }
    }

    LoginContent(
        state = state,
        onIntent = viewModel::onIntent,
    )
}
```

## Decisión de navegación en el NavHost (capa app)

```kotlin
// app/navigation/AppNavHost.kt
composable<Route.Login> {
    LoginScreen(
        onLoginSuccess = { navController.navigate(Route.Home) },
        onRegistrationRequired = { navController.navigate(Route.Registration) },
    )
}
```

El ViewModel emite el hecho; el NavHost decide la ruta concreta.

## Checklist de implementación

- ¿`<Pantalla>Intent` como sealed interface de entrada?
- ¿`<Pantalla>Events` como sealed interface de salida con `Channel`?
- ¿`LaunchedEffect(viewModel)` — no `LaunchedEffect(Unit)`?
- ¿El ViewModel no recibe `NavController` ni emite rutas concretas?
- ¿Los efectos nombran hechos (`LoginSuccess`) no destinos (`GoToHome`)?
- ¿El `State` solo contiene datos renderizables?
