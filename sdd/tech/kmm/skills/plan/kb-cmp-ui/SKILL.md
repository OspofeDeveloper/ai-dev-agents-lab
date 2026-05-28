---
name: kb-cmp-ui
description: Base de conocimiento de la capa presentation en proyectos Compose Multiplatform (CMP): estructura del módulo UI compartida en commonMain, entry point iOS, ciclo de vida, expect/actual de UI y relación con ViewModels KMM. Úsalo cuando el stack sea CMP y haya que planificar pantallas, navegación o componentes UI.
allowed-tools: [Read]
---

# CMP UI — Capa Presentation en Compose Multiplatform

## Qué es Compose Multiplatform en este contexto

Compose Multiplatform (CMP) comparte la capa `presentation` completa entre Android e iOS
usando Kotlin Multiplatform. A diferencia de KMM con UI nativa, **no hay SwiftUI ni
Activity/Fragment de Android** en el código de feature — todo está en commonMain.

## Estructura del módulo de presentación

La capa `presentation/` de una feature vive íntegra en `commonMain`:

```
feature/<nombre>/
└── presentation/
    ├── screen/         → Composables de pantalla (stateless)
    ├── viewmodel/      → ViewModel (commonMain, usa kotlin-coroutines)
    ├── state/          → UiState (data class, sealed class)
    ├── event/          → UiEvent (sealed class)
    └── effect/         → NavigationEffect o SideEffect (Channel)
```

No hay `androidMain/presentation/` ni `iosMain/presentation/` para código de feature normal.
El expect/actual de UI solo aparece para casos de plataforma explícita (ver abajo).

## Entry point por plataforma

| Plataforma | Entry point | Dónde vive |
|---|---|---|
| Android | `MainActivity` → `setContent { App() }` | `:composeApp` androidMain |
| iOS | `ComposeUIViewController { App() }` | `:composeApp` iosMain |

`App()` es un Composable en commonMain que arranca la navegación raíz.
`initKoin()` se llama dentro del `configure` del `ComposeUIViewController`.

## Ciclo de vida en CMP

Los APIs de ciclo de vida de Compose funcionan en commonMain sin cambios:
- `LaunchedEffect`, `DisposableEffect`, `SideEffect` → válidos en CMP
- `rememberCoroutineScope` → válido
- `LifecycleOwner` → disponible via `LocalLifecycleOwner` en CMP (desde `lifecycle-runtime-compose`)

No usar `Activity.lifecycleScope` ni `Fragment.viewLifecycleOwner` — son Android-only.

## Expect/Actual de UI: cuándo aplica

Solo cuando un Composable tiene comportamiento diferente por plataforma:

| Necesidad | ¿Expect/Actual? | Ejemplo |
|---|---|---|
| Pantallas, listas, formularios | NO | `AccountListScreen.kt` en commonMain |
| Color de status bar / navigation bar | SÍ | `SystemBarsController` |
| Back gesture / back handler | NO | `BackHandler` disponible en CMP desde 1.6 sin expect/actual |
| Sharing nativo (share sheet iOS / Intent Android) | SÍ | `ShareHelper` |
| Haptics | SÍ | `HapticFeedback` |

## Previews

Los `@Preview` de Compose Multiplatform funcionan en commonMain usando la anotación
`@Preview` del paquete `org.jetbrains.compose.ui.tooling.preview`. Requiere la
dependencia `compose.uiTooling` en el source set correspondiente.

No usar `@Preview` del paquete `androidx.compose.ui.tooling.preview` en commonMain.

## Reglas

1. Toda pantalla de feature vive en commonMain — nunca en androidMain/iosMain salvo expect/actual justificado.
2. Los ViewModels son clases de commonMain que extienden `ViewModel` de `lifecycle-viewmodel`.
3. El ViewModel no importa nada de `android.*` ni `platform.UIKit`.
4. Los Composables son stateless: reciben `UiState` y emiten `UiEvent`. El estado vive en el ViewModel.
5. Para recursos (strings, imágenes, fonts), usar siempre `compose-resources` (ver `kb-cmp-resources`).
