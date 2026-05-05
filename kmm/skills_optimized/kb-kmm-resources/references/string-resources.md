# String Resources — Code Examples

## 1. Definition in `strings.xml`

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

## 2. Usage in Composables

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

## 3. Usage outside Composables (`suspend`)

Use this only when a string must be materialized outside a Composable, for example in a bridge, share sheet, or UI-external utility.

If the project uses `kb-kmm-ui-text`, the ViewModel should not resolve the string here.

```kotlin
import myapp.shared.generated.resources.Res
import myapp.shared.generated.resources.share_message
import org.jetbrains.compose.resources.getString

suspend fun buildShareText(): String {
    return getString(Res.string.share_message)
}
```

## 4. Localization

Create `values-{locale}/` folders with the translated `strings.xml`. `stringResource()` and `getString()` automatically select the language from the device locale.

```
composeResources/
├── values/          ← default language (English)
│   └── strings.xml
├── values-es/       ← Spanish
│   └── strings.xml
└── values-fr/       ← French
    └── strings.xml
```
