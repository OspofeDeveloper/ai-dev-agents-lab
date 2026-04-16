---
name: wf-kmm-ktor-setup
description: "Configura Ktor Client en un proyecto KMM: dos HttpClients (IDSKtorClient + AppKtorClient), IdentityPlugin de autenticación automática con refresh token, CoreRepository con DataStore, tryCall/handleResponse y qualifiers Koin. Activar con frases como 'configurar Ktor', 'añadir cliente HTTP', 'setup networking', 'configurar autenticación Ktor', 'añadir Ktor KMM'."
argument-hint: "[URLs de la API y del Identity Server, realm de Keycloak si aplica]"
effort: high
allowed-tools: [Read, Write, Edit, Bash]
context: fork
agent: kmm-implementer
---

# wf-kmm-ktor-setup

Configura la capa de red completa en un proyecto KMM siguiendo el patrón de dos clientes descrito en `kb-ktor`. El resultado es un `AppKtorClient` con autenticación automática (Bearer + refresh transparente) y un `IDSKtorClient` para login/refresh, todo integrado con Koin.

---

## Paso 1 — Recopilar requisitos

Si el usuario no ha especificado todos los parámetros, preguntar:

1. **APP_BASE_URL** — URL base de la API principal (ej. `https://api.example.com/`)
2. **IDS_BASE_URL** — URL del Identity Server (ej. `https://identity.example.com/`)
3. **APP_CLIENT_ID** — Client ID para Keycloak/OAuth
4. **Realm** — Nombre del realm de Keycloak (ej. `MyApp`) para construir la ruta del token endpoint
5. **Entornos** — ¿Hay pre/pro u otros entornos? ¿Las URLs varían por entorno?
6. **Polimorfismo JSON** — ¿El backend usa un campo `"$type"` para tipos polimórficos?

Confirmar los datos antes de tocar ningún fichero.

---

## Paso 2 — Leer el estado actual del proyecto

Leer los siguientes ficheros para entender qué existe y qué falta:

- `gradle/libs.versions.toml` — versiones de Ktor declaradas
- `composeApp/build.gradle.kts` — dependencias actuales
- `composeApp/src/commonMain/kotlin/.../core/di/coreModule.kt` — si ya existe
- `app.properties` o ficheros de propiedades en la raíz — URLs actuales
- `composeApp/src/commonMain/kotlin/.../app/di/initKoin.kt` — módulos registrados

---

## Paso 3 — Consultar kb-ktor

Consultar el skill `kb-ktor` para los criterios técnicos canónicos que guían los pasos 4–9. En particular:
- **Regla 1**: por qué son dos clientes
- **Regla 2**: qualifiers
- **Regla 5**: lógica del IdentityPlugin
- **Regla 8**: tryCall y handleResponse

---

## Paso 4 — Añadir dependencias Ktor

En `gradle/libs.versions.toml`, verificar que estén declaradas las entradas de Ktor. Si faltan, añadirlas:

```toml
[versions]
ktor = "3.x.x"   # usar la versión más reciente estable

[libraries]
ktor-client-core              = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation", version.ref = "ktor" }
ktor-serialization            = { module = "io.ktor:ktor-serialization-kotlinx-json", version.ref = "ktor" }
ktor-client-logging           = { module = "io.ktor:ktor-client-logging", version.ref = "ktor" }
ktor-client-okhttp            = { module = "io.ktor:ktor-client-okhttp", version.ref = "ktor" }
ktor-client-darwin            = { module = "io.ktor:ktor-client-darwin", version.ref = "ktor" }
```

En `composeApp/build.gradle.kts`, verificar que los sourceSets incluyan:

```kotlin
commonMain.dependencies {
    implementation(libs.ktor.client.core)
    implementation(libs.ktor.client.content.negotiation)
    implementation(libs.ktor.serialization)
    implementation(libs.ktor.client.logging)
}
androidMain.dependencies {
    implementation(libs.ktor.client.okhttp)
}
iosMain.dependencies {
    implementation(libs.ktor.client.darwin)
}
```

Si las dependencias ya están, pasar al Paso 5 sin modificar nada.

Después de modificar `libs.versions.toml` o `build.gradle.kts`, sincronizar Gradle:

```bash
./gradlew --quiet help
```

---

## Paso 5 — Crear qualifiers

Siguiendo la **Regla 2** del `kb-ktor`, crear los dos archivos de qualifiers si no existen:

- `core/di/CoreQualifiers.kt`
- `core/identity/data/IdentityQualifiers.kt`

Consultar `kb-ktor/references/ktor_clients_templates.md § Qualifiers` para el código exacto.

---

## Paso 6 — Crear utilidades de red

Crear los archivos de red comunes si no existen:

- `core/network/NetworkError.kt` — sealed interface con todos los tipos de error
- `core/network/NetworkUtils.kt` — funciones `tryCall`, `handleResponse`, `Exception.toNetError`
- `core/utils/TokenUtils.kt` — función `isTokenExpired`
- `core/utils/KtorCustomLogger.kt` — wrapper del logger

Consultar `kb-ktor/references/network_utils_templates.md` para el código de cada archivo.

Si `AppLogger` (expect/actual) no existe, crearlo también en `commonMain`, `androidMain` e `iosMain`.

---

## Paso 7 — Crear CoreRepository e IdentityPlugin

### 7a. CoreRepository

Crear `core/domain/CoreRepository.kt` con la interfaz y `core/datastore/CoreRepositoryImpl.kt` con la implementación en DataStore.

Consultar `kb-ktor/references/identity_plugin_template.md § CoreRepository — interfaz` para el contrato completo.

Si DataStore no está configurado, añadir la dependencia y la inicialización expect/actual (`nativeModule`).

### 7b. IdentityPlugin

Crear `core/identity/data/IdentityPlugin.kt` y `core/identity/utils/IdentityEvents.kt`.

Consultar `kb-ktor/references/identity_plugin_template.md` para el código completo del plugin y los eventos.

---

## Paso 8 — Crear IdentityApi e IdentityApiImpl

Crear:
- `core/identity/data/api/IdentityApi.kt` — interfaz con `login` y `refreshToken`
- `features/auth/data/datasource/remote/api/IdentityApiImpl.kt` — implementación con `submitForm`

La ruta del token endpoint es `/realms/{realm}/protocol/openid-connect/token` donde `{realm}` es el valor del Paso 1.

Consultar `kb-ktor/references/ktor_clients_templates.md § IdentityApi — interfaz y implementación`.

---

## Paso 9 — Crear o actualizar coreModule

Crear `core/di/coreModule.kt` (o actualizar si existe) con:
- Singles de configuración desde `BuildConfig`
- `CoreRepository`
- `IDSKtorClient`
- `AppKtorClient` con `IdentityPlugin`
- `IdentityApi`

Consultar `kb-ktor/references/ktor_clients_templates.md § coreModule — registro completo`.

Si el `classDiscriminator = "\$type"` no es necesario (Paso 1, pregunta 6), omitirlo del `AppKtorClient`.

---

## Paso 10 — Registrar en initKoin

En `app/di/initKoin.kt`, asegurarse de que `coreModule` está registrado antes que los módulos de feature, y que `nativeModule` (DataStore) va el primero:

```kotlin
modules(
    nativeModule,   // DataStore y plataforma
    coreModule,     // HttpClients, CoreRepository, IdentityApi
    authModule,     // consume AppKtorClient
    // resto de módulos de feature...
)
```

---

## Paso 11 — Informar al usuario

Reportar:
- Lista de ficheros creados y modificados
- Si hay pasos manuales pendientes (ej. configurar DataStore en iOS con `getDataStore()`)
- Recordatorio: todos los servicios de feature deben inyectar `AppKtorClient` con `get(named(CoreQualifiers.AppKtorClient))`
- Recordatorio: endpoints públicos con `AppKtorClient` necesitan `header("No-Auth", "true")`