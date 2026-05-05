# Templates — Feature Modules

Wiring patterns only. Architectural ownership is decided by layer skills.
Multiple instances of the same type → use domain-grouped qualifiers:

```kotlin
enum class FeatureQualifiers { RemoteClient }
```

## Standard feature module

```kotlin
// features/profile/di/profileModule.kt
val profileModule = module {
    single { ProfileApi(get(named(FeatureQualifiers.RemoteClient))) }
    single<ProfileRepository> { ProfileRepositoryImpl(get(), get()) }
    factoryOf(::LoadProfileUseCase)
    factoryOf(::SaveProfileUseCase)
    viewModelOf(::ProfileViewModel)
}
```

## Minimal feature module

```kotlin
val catalogModule = module {
    single { CatalogApi(get(named(FeatureQualifiers.RemoteClient))) }
    single<CatalogRepository> { CatalogRepositoryImpl(get()) }
    factoryOf(::LoadCatalogUseCase)
    viewModelOf(::CatalogViewModel)
}
```

## Shared ViewModel (exceptional)

Use `singleOf` instead of `viewModelOf` only when the ViewModel must survive navigation or be shared across screens.

```kotlin
val editorModule = module {
    single { EditorApi(get(named(FeatureQualifiers.RemoteClient))) }
    single<EditorRepository> { EditorRepositoryImpl(get()) }
    singleOf(::SharedEditorViewModel)
    viewModelOf(::EditorDetailsViewModel)
    factoryOf(::LoadEditorContentUseCase)
    factoryOf(::SaveEditorContentUseCase)
}
```

## App module (multi-feature ViewModels and UseCases)

```kotlin
// app/di/appModule.kt
val appModule = module {
    viewModelOf(::AppViewModel)
    viewModelOf(::HomeScreenViewModel)
    factoryOf(::BootstrapAppUseCase)
    factoryOf(::SyncSessionStateUseCase)
}
```

## expect/actual factory functions

```kotlin
val platformStorageModule = module {
    single<PlatformStorage> { createPlatformStorage() }
}

val platformNotifierModule = module {
    single<PlatformNotifier> { createPlatformNotifier() }
}
```