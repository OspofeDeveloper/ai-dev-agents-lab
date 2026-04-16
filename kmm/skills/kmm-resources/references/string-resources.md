# String Resources — Ejemplos de Código

## 1. Definición en strings.xml

```xml
<!-- commonMain/composeResources/values/strings.xml -->
<resources>
    <string name="app_name">My App</string>
    <string name="login_title">Welcome Back</string>
    <string name="login_button">Log In</string>
    <string name="login_error">Invalid credentials</string>
    <string name="profile_greeting">Hello, %1$s</string>
    <plurals name="items_count">
        <item quantity="one">%1$d item</item>
        <item quantity="other">%1$d items</item>
    </plurals>
</resources>
```

## 2. Uso en Composables

```kotlin
import myapp.shared.generated.resources.Res
import myapp.shared.generated.resources.login_title
import myapp.shared.generated.resources.profile_greeting
import myapp.shared.generated.resources.items_count
import org.jetbrains.compose.resources.stringResource
import org.jetbrains.compose.resources.pluralStringResource

@Composable
fun LoginScreen() {
    Text(text = stringResource(Res.string.login_title))
}

@Composable
fun ProfileHeader(userName: String) {
    Text(text = stringResource(Res.string.profile_greeting, userName))
}

@Composable
fun ItemCounter(count: Int) {
    Text(text = pluralStringResource(Res.plurals.items_count, count, count))
}
```

## 3. Uso fuera de Composables (suspend)

Para obtener un string en un ViewModel o UseCase sin contexto `@Composable`:

```kotlin
import myapp.shared.generated.resources.Res
import myapp.shared.generated.resources.share_message
import org.jetbrains.compose.resources.getString

suspend fun buildShareText(): String {
    return getString(Res.string.share_message)
}
```

## 4. Localización

Crear carpetas `values-{locale}/` con el mismo `strings.xml` traducido. `stringResource()` y `getString()` seleccionan automáticamente el idioma según el locale del dispositivo.

```
composeResources/
├── values/          ← idioma por defecto (inglés)
│   └── strings.xml
├── values-es/       ← español
│   └── strings.xml
└── values-fr/       ← francés
    └── strings.xml
```
