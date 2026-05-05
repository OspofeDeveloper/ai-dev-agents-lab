# UiText Pattern — Complete Implementation

## 1. Sealed interface in `commonMain`

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

## 2. Usage in `State`

```kotlin
@Immutable
data class LoginState(
    val email: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val error: UiText? = null
)
```

## 3. Creation from ViewModel

```kotlin
import myapp.shared.generated.resources.Res
import myapp.shared.generated.resources.login_error
import myapp.shared.generated.resources.profile_greeting

// Resource error (translatable, recommended)
val error = UiText.ResourceString(Res.string.login_error)

// Dynamic error (when the message comes from the server)
val error = UiText.DynamicString("Server error: 500")

// With arguments
val greeting = UiText.ResourceString(
    resource = Res.string.profile_greeting,
    args = listOf(userName)
)
```

## 4. Usage in `UiModels`

`UiText` can also be used in UI models for fields whose representation depends on locale or on conditional logic that switches between a resource-backed string and a dynamic string.

Typical case: a date field that shows "Today, 12/05/2025" when the date is today, or "Monday, 05/05/2025" otherwise.

```kotlin
data class ServiceUiModel(
    val id: String,
    val startDate: UiText,
    val patientName: String,
)
```

The presentation mapper builds the final `UiText`:

```kotlin
private fun formatStartDate(isoDate: String): UiText {
    return if (isToday) {
        UiText.ResourceString(Res.string.home_today_format, listOf(formatted))
    } else {
        UiText.DynamicString("$dayOfWeek, $formatted")
    }
}
```

The Composable materializes it without conditional text-selection logic:

```kotlin
@Composable
fun ServiceItem(service: ServiceUiModel) {
    Text(text = service.startDate.asString())
}
```

When to use `UiText` in a UI model vs. `StringResource` directly:
- Use `UiText` when a field can be dynamic or translatable depending on the condition.
- Use `StringResource` directly when the field is always a fixed resource and never comes from external data.

What not to do:
- Do not expose `startDateText: String` plus `isToday: Boolean` so the UI decides whether to call `stringResource(...)`.
- Do not expose an already formatted `String` plus a flag so the Composable reconstructs the final sentence.
- Do not split text-selection decisions across multiple fields when one `UiText` better represents the final visual intent.

The mapper or ViewModel must return the final value as `UiText`. The UI only materializes it with `asString()`.

## 5. Usage in Composables

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

## 6. Test without `@Composable`

```kotlin
@Test
fun onLoginFailed_stateHasResourceError() {
    viewModel.onLoginFailed()
    val error = viewModel.state.value.error
    assertEquals(UiText.ResourceString(Res.string.login_error), error)
}
```
