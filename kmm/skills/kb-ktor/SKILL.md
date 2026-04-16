---
name: kb-ktor
description: "Base de conocimiento de Ktor Client en proyectos KMM: patrón de dos clientes (IDSKtorClient/AppKtorClient), plugin de autenticación personalizado (IdentityPlugin), No-Auth header, tryCall/handleResponse, CoreRepository para persistencia de tokens, discriminador $type en JSON, y KtorCustomLogger. Para el registro Koin de los clientes ver kb-koin."
argument-hint: ""
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Ktor Client KMM — Base de Conocimiento

## Regla 1: Patrón de dos clientes

El proyecto usa siempre **dos instancias separadas de `HttpClient`**:

| Cliente | Qualifier | Propósito |
|---------|-----------|-----------|
| `IDSKtorClient` | `IdentityQualifiers.IDSKtorClient` | Autenticación contra Identity Server (login, refresh token). Sin Bearer token propio. |
| `AppKtorClient` | `CoreQualifiers.AppKtorClient` | API principal de la app. Autenticación automática vía `IdentityPlugin`. |

La separación es obligatoria para evitar dependencias circulares: el `IdentityPlugin` instalado en `AppKtorClient` necesita hacer refresh token, y ese refresh usa `IdentityApi`, que a su vez usa `IDSKtorClient`. Si hubiera un solo cliente, el refresh token intentaría autenticarse a sí mismo.

→ Templates: `references/ktor_clients_templates.md`

---

## Regla 2: Qualifiers para distinguir los dos clientes

Al haber dos instancias de `HttpClient`, se aplica el patrón qualifier descrito en `kb-koin` **Regla 4**. Los enums concretos usados son:

| Enum | Fichero | Qualifiers de Ktor |
|------|---------|-------------------|
| `CoreQualifiers` | `core/di/CoreQualifiers.kt` | `AppKtorClient`, `AppBaseUrl` |
| `IdentityQualifiers` | `core/identity/data/IdentityQualifiers.kt` | `IDSKtorClient`, `IDSBaseUrl`, `AppClientId`, `LoginGrantType`, `RefreshTokenGrantType` |

Todos los servicios de feature consumen `AppKtorClient`. Solo `IdentityApiImpl` consume `IDSKtorClient`.

→ Concepto de qualifiers y DSL de registro: `kb-koin` Regla 4
→ Código completo del coreModule: `references/ktor_clients_templates.md`

---

## Regla 3: IDSKtorClient — cliente de Identity

El cliente de Identity es simple: sin `IdentityPlugin`, sin `HttpTimeout`, sin `Content-Type` por defecto.

Plugins instalados:
- `ContentNegotiation` con `Json { ignoreUnknownKeys = true }`
- `Logging` con `KtorCustomLogger()` y `LogLevel.ALL`
- `DefaultRequest` con la URL base del IDS

`IdentityApiImpl` usa `submitForm` (no `setBody`) porque el endpoint de Keycloak espera `application/x-www-form-urlencoded`.

→ Templates: `references/ktor_clients_templates.md`

---

## Regla 4: AppKtorClient — cliente autenticado

El cliente de la app instala cinco plugins en este orden:

1. `ContentNegotiation` — JSON con `ignoreUnknownKeys = true` y `classDiscriminator = "\$type"` (ver Regla 10)
2. `Logging` — `KtorCustomLogger()` y `LogLevel.ALL`
3. `DefaultRequest` — URL base + `contentType(ContentType.Application.Json)`
4. `IdentityPlugin` — plugin personalizado de autenticación (ver Regla 5)
5. `HttpTimeout` — 30 segundos en todas las fases (request, connect, socket)

→ Templates: `references/ktor_clients_templates.md`

---

## Regla 5: IdentityPlugin — plugin de autenticación

Plugin personalizado creado con `createClientPlugin`. Se instala solo en `AppKtorClient`.

Lógica en `onRequest { }`:

```
1. Si la request tiene header "No-Auth: true" → eliminar header y salir (endpoint público)
2. Leer refreshToken, refreshExpiredDate, accessToken, expiredDate de CoreRepository
3. Si refreshToken está expirado → emitir IdentityEvents.RefreshTokenExpired al canal
4. Si accessToken está expirado:
   a. Llamar a coreRepository.refreshToken(refreshToken)
   b. Si éxito → guardar nuevos tokens, actualizar accessToken local
   c. Si error → limpiar tokens, emitir RefreshTokenExpired, accessToken = null
5. Si accessToken != null → añadir header "Authorization: Bearer {accessToken}"
```

El plugin usa `runBlocking` para operaciones suspendidas (limitación de la API de plugins de Ktor).

→ Templates: `references/identity_plugin_template.md`

---

## Regla 6: CoreRepository — persistencia de tokens

`CoreRepository` es la abstracción que el `IdentityPlugin` usa para acceder a los tokens. Se implementa con DataStore.

Expone:
- `accessToken: Flow<String?>` + `saveAccessToken()`
- `refreshToken: Flow<String?>` + `saveRefreshToken()`
- `expiredDate: Flow<Long?>` + `saveExpiredData()` — timestamp epoch ms de expiración del access token
- `refreshTokenExpired: Flow<Long?>` + `saveRefreshExpiredData()` — timestamp epoch ms de expiración del refresh token
- `refreshExpiredChannel: Channel<IdentityEvents>` + `refreshExpiredFlow` — canal para emitir eventos de sesión expirada
- `clearTokens()` — limpia todos los tokens almacenados
- `suspend fun refreshToken(refreshToken: String): AppResult<TokenInfoModel, AppError>` — llama a `IdentityApi` para renovar tokens

La función auxiliar de expiración compara el timestamp actual contra el guardado:

```kotlin
fun String?.isTokenExpired(expiredDate: Long?): Boolean {
    if (this.isNullOrBlank()) return true
    if (expiredDate == null) return true
    return Clock.System.now().toEpochMilliseconds() >= expiredDate
}
```

---

## Regla 7: Header No-Auth para endpoints públicos

Los endpoints públicos que se llaman con `AppKtorClient` (no con `IDSKtorClient`) deben incluir el header `No-Auth: true`. El `IdentityPlugin` lo detecta, lo elimina antes de enviar la request, y omite la autenticación.

```kotlin
httpClient.post("api/Account/CreateUser") {
    header("No-Auth", "true")
    setBody(registrationDto)
}
```

Cuándo usar `No-Auth`:
- Registro de nuevo usuario
- Recuperación de contraseña
- Cualquier endpoint público que por diseño va con `AppKtorClient`

Cuándo NO usar `No-Auth`:
- Llamadas con `IDSKtorClient` (ya no tiene el plugin)
- Endpoints que requieren autenticación

---

## Regla 8: tryCall y handleResponse — manejo centralizado de errores

Todas las llamadas HTTP pasan por `tryCall`, que captura excepciones de red y de serialización y devuelve `AppResult`.

```
tryCall { httpClient.get(...) }
  → éxito: handleResponse(response) → AppResult.Success o AppResult.Error según status code
  → excepción: e.toNetError() → AppResult.Error(NetworkError)
```

Tipos de `NetworkError`:
- `NoInternet` — `UnresolvedAddressException`
- `Serialization` — `SerializationException` / `JsonConvertException`
- `Unauthorized` — HTTP 401
- `Conflict` — HTTP 409
- `RequestTimeout` — HTTP 408
- `PayloadTooLarge` — HTTP 413
- `ServerError` — HTTP 500–599
- `CustomError(message)` — HTTP 400
- `Unknown` — resto de casos

→ Templates: `references/network_utils_templates.md`

---

## Regla 9: KtorCustomLogger

El logger de Ktor es un wrapper sobre `AppLogger` (expect/actual por plataforma) que etiqueta los mensajes con `"SERVER_RESPONSE"`:

```kotlin
class KtorCustomLogger : Logger {
    override fun log(message: String) {
        AppLogger.i(tag = "SERVER_RESPONSE", message = message)
    }
}
```

Se pasa como `logger = KtorCustomLogger()` en el bloque `install(Logging)` de ambos clientes.

→ Templates: `references/network_utils_templates.md`

---

## Regla 10: Discriminador de tipos JSON ($type)

El `AppKtorClient` configura `classDiscriminator = "\$type"` en el `Json` de `ContentNegotiation`. Esto permite deserializar respuestas polimórficas donde el backend envía un campo `"$type"` para indicar el subtipo concreto.

Solo aplica al `AppKtorClient`. El `IDSKtorClient` no lo necesita porque el Identity Server devuelve JSON plano (no polimórfico).

Si el backend no usa polimorfismo con `"$type"`, eliminar `classDiscriminator` del cliente.

---

## Regla 11: Rutas relativas en los servicios

Los servicios de feature usan rutas relativas, nunca URLs absolutas. La URL base la aporta `DefaultRequest` del cliente.

```kotlin
// Correcto
httpClient.get("api/Pump/GetUserPumps")

// Incorrecto
httpClient.get("https://api.sacipumps.com/api/Pump/GetUserPumps")
```

Para path params:
```kotlin
httpClient.get("api/Pump/GetPumpById") {
    url { appendPathSegments(pumpId) }
}
```

Para query params:
```kotlin
httpClient.get("api/Alarm/GetAlarms") {
    url { parameters.append("pumpId", pumpId) }
}
```
