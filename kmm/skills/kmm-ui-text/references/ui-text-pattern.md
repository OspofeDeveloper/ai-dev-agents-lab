# Patrón UiText — Implementación Completa

## 1. Sealed interface en commonMain

```kotlin
// shared/src/commonMain/kotlin/com/example/core/ui/model/UiText.kt
package com.example.core.ui.model

import androidx.compose.runtime.Composable
import org.jetbrains.compose.resources.StringResource
import org.jetbrains.compose.resources.stringResource

sealed interface UiText {

    data class DynamicString(val value: String) : UiText

    data class ResourceString(
        val resource: StringResource,
        val args: List<Any> = emptyList()
    ) : UiText
}

@Composable
fun UiText.asString(): String {
    return when (this) {
        is UiText.DynamicString -> value
        is UiText.ResourceString -> {
            if (args.isEmpty()) {
                stringResource(resource)
            } else {
                stringResource(resource, *args.toTypedArray())
            }
        }
    }
}
```

## 2. Uso en State

```kotlin
@Immutable
data class LoginState(
    val email: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val error: UiText? = null
)
```

## 3. Creación desde ViewModel

```kotlin
import myapp.shared.generated.resources.Res
import myapp.shared.generated.resources.login_error
import myapp.shared.generated.resources.profile_greeting

// Error de recurso (traducible, recomendado)
val error = UiText.ResourceString(Res.string.login_error)

// Error dinámico (cuando el mensaje viene del servidor)
val error = UiText.DynamicString("Server error: 500")

// Con argumentos
val greeting = UiText.ResourceString(
    resource = Res.string.profile_greeting,
    args = listOf(userName)
)
```

## 4. Uso en Composables

```kotlin
@Composable
fun LoginScreen(state: LoginState) {
    state.error?.let { error ->
        Text(
            text = error.asString(),
            color = MaterialTheme.colorScheme.error
        )
    }
}
```

## 5. Test sin @Composable

```kotlin
@Test
fun onLoginFailed_stateHasResourceError() {
    viewModel.onLoginFailed()
    val error = viewModel.state.value.error
    assertEquals(UiText.ResourceString(Res.string.login_error), error)
}
```
