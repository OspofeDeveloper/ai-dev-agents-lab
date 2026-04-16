# BackHandler — Ejemplos de Código

## `BackHandler` en commonMain

```kotlin
// Import correcto para commonMain (CMP 1.6+)
import androidx.compose.ui.platform.BackHandler

@Composable
fun FormScreen(hasUnsavedChanges: Boolean, onConfirmLeave: () -> Unit) {
    BackHandler(enabled = hasUnsavedChanges) {
        // Mostrar confirmación antes de salir
        showDiscardDialog = true
    }
}
```
