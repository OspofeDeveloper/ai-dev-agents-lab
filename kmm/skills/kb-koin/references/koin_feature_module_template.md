# Templates — Módulos de feature

Estos ejemplos muestran patrones de registro en Koin. La ubicación arquitectónica de cada pieza se decide con las skills de capa; aquí solo se ilustra cómo cablearlas.

Cuando una dependencia necesita distinguir varias instancias del mismo tipo, usar qualifiers agrupados por dominio de resolución, no necesariamente por tecnología.

```kotlin
enum class FeatureQualifiers {
    RemoteClient,
}
```

## Módulo de feature estándar (forma completa)

```kotlin
// features/profile/di/profileModule.kt
val profileModule = module {

    // --- Capa de datos ---
    single { ProfileRemoteDataSource(get(named(FeatureQualifiers.RemoteClient))) }
    single<ProfileRepository> { ProfileRepositoryImpl(get(), get()) }

    // --- Use Cases ---
    factoryOf(::LoadProfileUseCase)
    factoryOf(::SaveProfileUseCase)

    // --- ViewModels ---
    viewModelOf(::ProfileViewModel)
}
```

---

## Módulo de feature mínimo (forma corta)

```kotlin
val catalogModule = module {
    single { CatalogRemoteDataSource(get(named(FeatureQualifiers.RemoteClient))) }
    single<CatalogRepository> { CatalogRepositoryImpl(get()) }
    factoryOf(::LoadCatalogUseCase)
    viewModelOf(::CatalogViewModel)
}
```

---

## Módulo con ViewModel como single (caso excepcional)

Usar `singleOf` en lugar de `viewModelOf` solo cuando el ViewModel necesita sobrevivir a la navegación entre screens o ser compartido.

```kotlin
val editorModule = module {
    single { EditorRemoteDataSource(get(named(FeatureQualifiers.RemoteClient))) }
    single<EditorRepository> { EditorRepositoryImpl(get()) }

    singleOf(::SharedEditorViewModel)
    viewModelOf(::EditorDetailsViewModel)

    factoryOf(::LoadEditorContentUseCase)
    factoryOf(::SaveEditorContentUseCase)
}
```

---

## Módulo de app (ViewModels y UseCases multi-feature)

```kotlin
// app/di/appModule.kt
val appModule = module {
    viewModelOf(::AppViewModel)
    viewModelOf(::HomeScreenViewModel)

    factoryOf(::BootstrapAppUseCase)
    factoryOf(::SyncSessionStateUseCase)
}
```

---

## Módulos con expect/actual factory function

```kotlin
val platformStorageModule = module {
    single<PlatformStorage> { createPlatformStorage() }
}

val platformNotifierModule = module {
    single<PlatformNotifier> { createPlatformNotifier() }
}
```
