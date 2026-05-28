# BackHandler — Ejemplos de Código

## `BackHandler` en commonMain

```kotlin
import androidx.compose.ui.platform.BackHandler

@Composable
fun FormScreen(hasUnsavedChanges: Boolean, onConfirmLeave: () -> Unit) {
    BackHandler(enabled = hasUnsavedChanges) {
        showDiscardDialog = true
    }
}
```
