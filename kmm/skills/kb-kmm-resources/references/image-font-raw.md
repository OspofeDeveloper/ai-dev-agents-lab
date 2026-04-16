# Imágenes, Fonts y Raw Files — Ejemplos de Código

## 1. Image resources

```kotlin
import myapp.shared.generated.resources.Res
import myapp.shared.generated.resources.ic_logo
import org.jetbrains.compose.resources.painterResource

@Composable
fun AppLogo() {
    Image(
        painter = painterResource(Res.drawable.ic_logo),
        contentDescription = "App logo"
    )
}
```

## 2. Font resources

```kotlin
import myapp.shared.generated.resources.Res
import myapp.shared.generated.resources.roboto_regular
import org.jetbrains.compose.resources.Font

@Composable
fun AppTheme(content: @Composable () -> Unit) {
    val robotoRegular = FontFamily(Font(Res.font.roboto_regular))
    MaterialTheme(
        typography = Typography(bodyMedium = TextStyle(fontFamily = robotoRegular))
    ) {
        content()
    }
}
```

## 3. Raw files y assets

Los archivos raw van en `composeResources/files/`.

```kotlin
import myapp.shared.generated.resources.Res
import org.jetbrains.compose.resources.ExperimentalResourceApi

@OptIn(ExperimentalResourceApi::class)
suspend fun loadConfig(): String {
    return Res.readBytes("files/config.json").decodeToString()
}
```
