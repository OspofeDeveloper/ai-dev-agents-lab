# Templates — Módulos de feature

## Módulo de feature estándar (forma completa)

```kotlin
// features/auth/di/authModule.kt
val authModule = module {

    // --- Capa de datos ---
    single { AuthService(get(named(CoreQualifiers.AppKtorClient))) }
    single<AuthRepository> { AuthRepositoryImpl(get(), get()) }

    // --- Use Cases ---
    factoryOf(::LoginUseCase)
    factoryOf(::ForgotPasswordUseCase)
    factoryOf(::RegistrationUseCase)
    factoryOf(::DeleteAccountUseCase)
    factoryOf(::LogoutUseCase)
    factoryOf(::GetProfileUseCase)
    factoryOf(::SaveEditProfileUseCase)
    factoryOf(::SaveChangePasswordUseCase)
    factoryOf(::SetPushTokenUseCase)

    // --- ViewModels ---
    viewModelOf(::LoginViewModel)
    viewModelOf(::ForgotPasswordViewModel)
    viewModelOf(::RegistrationViewModel)
    viewModelOf(::ProfileViewModel)
    viewModelOf(::EditProfileViewModel)
    viewModelOf(::ChangePasswordViewModel)
}
```

---

## Módulo de feature mínimo (forma corta)

```kotlin
val resetsModule = module {
    single { ResetApi(get(named(CoreQualifiers.AppKtorClient))) }
    single<ResetsRepository> { ResetsRepositoryImpl(get()) }
    factoryOf(::DoResetUseCase)
    factoryOf(::LoadResetsUseCase)
    viewModelOf(::ResetViewModel)
}
```

---

## Módulo con ViewModel como single (caso excepcional)

Usar `singleOf` en lugar de `viewModelOf` solo cuando el ViewModel necesita sobrevivir a la navegación entre screens o ser compartido. Ejemplo del proyecto:

```kotlin
val locationModule = module {
    single { LocationsService(get(named(CoreQualifiers.AppKtorClient))) }
    single<LocationsRepository> { LocationsRepositoryImpl(get()) }

    // Single porque se comparte entre dos screens de edición
    singleOf(::EditLocationViewModel)

    // ViewModel normal para el resto
    viewModelOf(::ChangeLocationNameViewModel)

    factoryOf(::DeleteLocationUseCase)
    factoryOf(::SaveChangeLocationNameUseCase)
    factoryOf(::GetUserLocationsUseCase)
}
```

---

## Módulo de app (ViewModels y UseCases multi-feature)

```kotlin
// app/di/appModule.kt
val appModule = module {

    // ViewModels de pantallas principales
    viewModelOf(::AppViewModel)
    viewModelOf(::HomeViewModel)
    viewModelOf(::AddPumpViewModel)
    viewModelOf(::PumpDetailViewModel)
    viewModelOf(::PumpAdvancedParametersViewModel)
    viewModelOf(::PumpBasicConfigViewModel)
    viewModelOf(::PumpFineAdjustmentsViewModel)
    viewModelOf(::PumpSettingsViewModel)
    viewModelOf(::PumpWifiConnectionViewModel)
    viewModelOf(::PumpResetViewModel)

    // Use Cases que orquestan múltiples features
    factoryOf(::GetAdvancedParametersUseCase)
    factoryOf(::GetFineAdjustmentsUseCase)
    factoryOf(::GetPumpDetailUseCase)
    factoryOf(::GetRealTimeTelemetryUseCase)
    factoryOf(::SetUpdateAvailableUseCase)
    factoryOf(::DeletePumpUseCase)
    factoryOf(::ResetPumpControllersUseCase)
    factoryOf(::ResetPumpAlarmsUseCase)
    factoryOf(::ResetPumpFactoryModeUseCase)
    factoryOf(::InitHomeDataUseCase)
}
```

---

## Módulos con expect/actual factory function

```kotlin
// commonMain — BLEModule.kt
val BLEModule = module {
    single<BLERepository> { createBLERepositoryImpl() }
}

// commonMain — firebaseModule.kt
val firebaseModule = module {
    single<FirebaseRepository> { createFirebaseRepositoryImpl() }
}
```
