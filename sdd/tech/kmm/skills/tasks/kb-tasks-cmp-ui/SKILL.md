---
name: kb-tasks-cmp-ui
description: Implementación concreta de la capa presentation en proyectos Compose Multiplatform (CMP): entry points Android e iOS, setup de initKoin en iOS, ciclo de vida en commonMain y configuración de @Preview. Úsalo cuando haya que implementar pantallas, entry points o componentes UI en CMP.
allowed-tools: [Read]
user-invocable: false
---

# CMP UI — Capa Presentation en Compose Multiplatform (implementación)

→ Estructura del módulo y cuándo usar expect/actual: `kb-plan-cmp-ui`

## Entry point Android

```kotlin
// :composeApp / androidMain / MainActivity.kt
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            App()
        }
    }
}
```

`App()` es un Composable en commonMain que arranca el NavHost raíz.

## Entry point iOS

```kotlin
// :composeApp / iosMain / MainViewController.kt
fun MainViewController() = ComposeUIViewController(
    configure = { initKoin() }
) {
    App()
}
```

`initKoin()` se llama una sola vez dentro del bloque `configure`.
No llamar `initKoin()` desde `App()` ni desde el ViewModel.

## Ciclo de vida en commonMain

Los APIs de ciclo de vida de Compose funcionan en commonMain sin cambios:

```kotlin
// válidos en CMP
LaunchedEffect(key) { ... }
DisposableEffect(key) { onDispose { ... } }
rememberCoroutineScope()
val lifecycleOwner = LocalLifecycleOwner.current  // lifecycle-runtime-compose
```

Prohibido en commonMain:
- `Activity.lifecycleScope`
- `Fragment.viewLifecycleOwner`
- cualquier import de `android.*` o `platform.UIKit`

## @Preview en CMP

```kotlin
import org.jetbrains.compose.ui.tooling.preview.Preview

@Preview
@Composable
fun MyScreenPreview() {
    MyScreen(state = MyUiState())
}
```

Requiere `compose.uiTooling` en el source set del módulo compartido.
No usar `@Preview` del paquete `androidx.compose.ui.tooling.preview` en commonMain.

## Reglas de implementación

1. Toda pantalla de feature vive en `commonMain` — nunca en `androidMain`/`iosMain` salvo expect/actual justificado.
2. El ViewModel extiende `ViewModel` de `lifecycle-viewmodel` (commonMain).
3. El ViewModel no importa nada de `android.*` ni `platform.UIKit`.
4. Los Composables son stateless: reciben `UiState` y emiten `UiEvent`. El estado vive en el ViewModel.
