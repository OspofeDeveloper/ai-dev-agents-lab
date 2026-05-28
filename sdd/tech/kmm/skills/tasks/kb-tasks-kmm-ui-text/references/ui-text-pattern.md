# Patrón UIText — Implementación Completa

## 1. Sealed class en commonMain

```kotlin
// composeApp/src/commonMain/kotlin/com/example/cuideo/core/ui/UIText.kt
package com.example.cuideo.core.ui

import androidx.compose.runtime.Composable
import org.jetbrains.compose.resources.StringResource
import org.jetbrains.compose.resources.stringResource

sealed class UIText {

    data class Dynamic(val value: String) : UIText()

    data class Resource(
        val resource: StringResource,
        val args: List<Any> = emptyList()
    ) : UIText()

    @Composable
    fun asString(): String = when (this) {
        is Dynamic -> value
        is Resource -> if (args.isEmpty()) {
            stringResource(resource)
        } else {
            stringResource(resource, *args.toTypedArray())
        }
    }
}
```

## 2. Uso en State (errores y mensajes)

```kotlin
@Immutable
data class LoginState(
    val email: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val error: UIText? = null
)
```

## 3. Creación desde ViewModel

```kotlin
import cuideo.composeapp.generated.resources.Res
import cuideo.composeapp.generated.resources.login_error
import cuideo.composeapp.generated.resources.profile_greeting

// Texto traducible (recomendado para errores y mensajes fijos)
val error = UIText.Resource(Res.string.login_error)

// Texto dinámico (cuando el mensaje viene del servidor o de datos externos)
val error = UIText.Dynamic("Server error: 500")

// Con argumentos de formato
val greeting = UIText.Resource(
    resource = Res.string.profile_greeting,
    args = listOf(userName)
)
```

## 4. Uso en UiModels (campos de dato localizables)

`UIText` también puede usarse en UiModels para campos cuya representación depende del locale o de lógica condicional que decide entre un string de recurso y un string dinámico.

Caso típico: un campo de fecha que muestra "Hoy, 12/05/2025" cuando es la fecha actual, o "Lunes, 05/05/2025" cuando no lo es.

```kotlin
data class ServiceUiModel(
    val id: String,
    val startDate: UIText,   // puede ser Dynamic o Resource según la lógica del mapper
    val patientName: String,
    // ...
)
```

El mapper de presentación construye el `UIText` apropiado:

```kotlin
private fun formatStartDate(isoDate: String): UIText {
    // ... parsing de fecha ...
    return if (isToday) {
        UIText.Resource(Res.string.home_today_format, listOf(formatted))
    } else {
        UIText.Dynamic("$dayOfWeek, $formatted")
    }
}

fun Service.toUiModel(): ServiceUiModel = ServiceUiModel(
    startDate = formatStartDate(startDate),
    // ...
)
```

El Composable lo materializa sin lógica condicional:

```kotlin
@Composable
fun ServiceItem(service: ServiceUiModel) {
    Text(text = service.startDate.asString())
}
```

**Cuándo usar `UIText` en un UiModel vs. `StringResource` directamente:**
- Usa `UIText` cuando el campo puede ser dinámico (dato del servidor) O traducible según condición.
- Usa `StringResource` directamente cuando el campo es siempre un recurso fijo (sin datos externos), como `contractType: StringResource`.

**Qué no hacer:**
- No expongas `startDateText: String` junto con `isToday: Boolean` para que la UI decida si usa `stringResource(...)`.
- No expongas un `String` ya formateado más un flag para que el Composable reconstruya la frase final.
- No repartas la decisión textual entre varios campos cuando un único `UIText` representa mejor la intención visual final.

El mapper o ViewModel debe devolver el valor final como `UIText`. La UI solo lo materializa con `asString()`.

## 5. Uso en Composables

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

## 6. Test sin @Composable

```kotlin
@Test
fun onLoginFailed_stateHasResourceError() {
    viewModel.onLoginFailed()
    val error = viewModel.state.value.error
    assertEquals(UIText.Resource(Res.string.login_error), error)
}
```
