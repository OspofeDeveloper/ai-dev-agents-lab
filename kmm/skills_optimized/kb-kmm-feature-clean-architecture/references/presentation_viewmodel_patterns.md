# Presentation Patterns With ViewModel — Preferred Structure

## 1. Folder structure

```text
features/<feature>/presentation/<screen>/
├── <Screen>Screen.kt
└── viewmodel/
    ├── <Screen>ViewModel.kt
    ├── <Screen>State.kt
    ├── <Screen>Intent.kt
    └── <Screen>Events.kt
```

## 2. Preferred naming

Screen state and presentation-owned UI models should default every parameter to a render-safe value.

- `<Screen>State` — mutable screen state
- `<Screen>Intent` — UI → ViewModel input events
- `<Screen>Events` — ViewModel → UI output effects

## 3. Preferred ViewModel shape

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