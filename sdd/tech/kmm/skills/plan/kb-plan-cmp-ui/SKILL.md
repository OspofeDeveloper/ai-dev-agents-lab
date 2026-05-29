---
name: kb-plan-cmp-ui
description: Base de conocimiento de la capa presentation en proyectos Compose Multiplatform (CMP): estructura del módulo UI compartida en commonMain, cuándo usar expect/actual de UI y relación con ViewModels KMM. Úsalo cuando el stack sea CMP y haya que planificar pantallas, navegación o componentes UI.
allowed-tools: [Read]
effort: low
user-invocable: false
---

# CMP UI — Capa Presentation en Compose Multiplatform (nivel planificación)

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

## Entry points por plataforma

Cada plataforma tiene su propio entry point en el módulo `:composeApp` (no en la feature):
- **Android**: `androidMain` arranca el Composable raíz `App()`.
- **iOS**: `iosMain` expone un `ComposeUIViewController` que arranca `App()` e inicializa Koin.

El plan debe prever qué Composable raíz orquesta la navegación y dónde vive.

→ Implementación concreta de entry points: `kb-tasks-cmp-ui`

## Expect/Actual de UI: cuándo aplica

Solo cuando un Composable tiene comportamiento diferente por plataforma:

| Necesidad | ¿Expect/Actual? |
|---|---|
| Pantallas, listas, formularios | NO |
| Color de status bar / navigation bar | SÍ |
| Back gesture / back handler | NO — BackHandler disponible en CMP desde 1.6 |
| Sharing nativo (share sheet iOS / Intent Android) | SÍ |
| Haptics | SÍ |

Si el plan incluye comportamientos de plataforma (system bars, sharing, haptics), debe prever el patrón expect/actual correspondiente.

## Reglas de planificación

1. Toda pantalla de feature vive en commonMain — nunca en androidMain/iosMain salvo expect/actual justificado.
2. Los ViewModels son clases de commonMain que extienden `ViewModel` de `lifecycle-viewmodel`.
3. El ViewModel no importa nada de `android.*` ni `platform.UIKit`.
4. Los Composables son stateless: reciben `UiState` y emiten `UiEvent`. El estado vive en el ViewModel.
5. Para recursos (strings, imágenes, fonts), usar siempre `compose-resources` (ver `kb-cmp-resources`).
