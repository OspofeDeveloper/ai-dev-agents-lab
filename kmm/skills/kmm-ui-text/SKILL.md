---
name: kb-kmm-ui-text
description: "Base de conocimiento sobre el patrón UiText en Compose Multiplatform: sealed interface para desacoplar ViewModel de la capa UI, manejo de strings traducibles y dinámicos."
argument-hint: "implementación, uso en state, uso en viewmodel, testing"
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Patrón UiText — Compose Multiplatform

---

## Contrato UiText

Invariantes de arquitectura para el manejo de textos en KMM:

- **El ViewModel no usa `@Composable`**: produce `UiText`, nunca `String` resuelto mediante `stringResource()`.
- **`UiText` en `commonMain`**: el sealed interface y su función `asString()` viven en `commonMain`. No dependen de Android ni de contexto de plataforma.
- **`@StringRes` prohibido en `commonMain`**: usar `StringResource` de `compose.resources`.
- **`asString()` solo en la capa UI**: la resolución del texto ocurre en el Composable, no en el ViewModel ni en el dominio.
- **Tests sin `@Composable`**: en tests se compara directamente el valor `UiText` (tipo + referencia a recurso) sin renderizar UI.

---

## 1. Definición del sealed interface

```kotlin
// shared/src/commonMain/kotlin/com/example/core/ui/model/UiText.kt
sealed interface UiText {
    data class DynamicString(val value: String) : UiText
    data class ResourceString(
        val resource: StringResource,
        val args: List<Any> = emptyList()
    ) : UiText
}

@Composable
fun UiText.asString(): String = when (this) {
    is UiText.DynamicString -> value
    is UiText.ResourceString ->
        if (args.isEmpty()) stringResource(resource)
        else stringResource(resource, *args.toTypedArray())
}
```

`DynamicString` — para textos que vienen de una fuente externa (API, base de datos). No se traduce.
`ResourceString` — para textos definidos en `strings.xml`. Se traduce automáticamente según el locale.

---

## 2. Uso en State y ViewModel

El estado de UI expone `UiText?` para mensajes de error y similares. El ViewModel construye `UiText` con referencias a `Res.string.*` sin necesitar contexto Composable.

```kotlin
// Estado
@Immutable
data class LoginState(
    val error: UiText? = null
)

// ViewModel
val error = UiText.ResourceString(Res.string.login_error)                          // error traducible
val error = UiText.DynamicString("Server error: 500")                              // error dinámico
val greeting = UiText.ResourceString(Res.string.profile_greeting, listOf(userName)) // con argumento
```

---

## 3. Resolución en Composables

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

---

## 4. Testing

Los tests de ViewModel comparan el `UiText` directamente, sin render:

```kotlin
@Test
fun onLoginFailed_stateHasResourceError() {
    viewModel.onLoginFailed()
    assertEquals(UiText.ResourceString(Res.string.login_error), viewModel.state.value.error)
}
```

- Para la implementación completa con imports, ver [ui-text-pattern.md](references/ui-text-pattern.md)

---

## Requisitos NO Negociables

### Obligatorio

- `UiText` en `commonMain`, sin dependencias de plataforma
- `asString()` solo invocado desde Composables
- `ResourceString` para strings traducibles; `DynamicString` para strings externos

### Prohibido

- `@StringRes` en `commonMain`
- Llamar a `stringResource()` en el ViewModel para resolver strings
- Comparar strings resueltos en tests de ViewModel (comparar el `UiText` directamente)

---

**Version**: 1.0.0
**Última actualización**: 2026-04-11
**Compatibilidad**: Compose Multiplatform 1.6+, Kotlin 2.0+
