# Patrones De Presentation Con ViewModel — Estructura Preferida

## 1. Estructura de carpetas

```text
features/<feature>/presentation/<pantalla>/
├── <Pantalla>Screen.kt
└── viewmodel/
    ├── <Pantalla>ViewModel.kt
    ├── <Pantalla>State.kt
    ├── <Pantalla>Intent.kt
    └── <Pantalla>Events.kt
```

## 2. Naming preferido

- `<Pantalla>State` para estado mutable de pantalla
- `<Pantalla>Intent` para eventos de entrada UI -> ViewModel
- `<Pantalla>Events` para efectos de salida ViewModel -> UI

## 3. Forma preferida del ViewModel

```kotlin
var state by mutableStateOf(LoginState())
    private set

private val _events = Channel<LoginEvents>()
val events = _events.receiveAsFlow()

fun onEvent(intent: LoginIntent) {
    when (intent) {
        // ...
    }
}
```
