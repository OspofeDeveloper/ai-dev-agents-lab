---
name: kb-kmm-http-ktor
description: "Base de conocimiento de implementación HTTP con Ktor en proyectos KMM: configuración de HttpClient, plugins, serialización JSON, logging, timeouts, rutas relativas y utilidades específicas de Ktor."
argument-hint: ""
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Ktor HTTP KMM — Base de Conocimiento

## Regla 1: Esta skill define mecanismo, no política

Esta skill describe cómo implementar el cliente HTTP con Ktor. No define reglas de arquitectura, DI ni estrategia de auth por sí sola.

Implementa el mecanismo técnico que ejecuta el contrato remoto definido por `kb-kmm-network-contracts`.

Cuando necesite apoyarse en otras decisiones, debe referenciar sus skills correspondientes.

No define:

- taxonomía de errores de red
- contratos remotos estables
- ubicación en `core` o feature
- registro en DI
- estrategia de autenticación

---

## Regla 2: Configuración estándar del HttpClient

Un `HttpClient` de Ktor en KMM configura, como mínimo, estos aspectos cuando aplican al proyecto:

- `ContentNegotiation` con `Json`
- `Logging` con logger del proyecto
- `DefaultRequest` para URL base y headers comunes
- `HttpTimeout` para timeouts homogéneos

El orden de plugins debe ser explícito y coherente con la estrategia del proyecto.

La configuración concreta debe servir al contrato remoto del proyecto, no redefinirlo.

→ Templates: `references/ktor_http_templates.md`

---

## Regla 3: Rutas relativas y URL base centralizada

Los servicios remotos usan rutas relativas. La URL base se configura en el cliente, no se repite en cada servicio.

→ Templates: `references/ktor_http_templates.md`

---

## Regla 4: Formularios OAuth o similares usan `submitForm`

Cuando un endpoint requiere `application/x-www-form-urlencoded`, la implementación con Ktor usa `submitForm` en lugar de `setBody` JSON.

---

## Regla 5: Las utilidades de Ktor viven fuera de las features

Helpers como `tryCall`, `responseHandler` por defecto, mappers de excepción o loggers de Ktor viven en `core/network` o equivalente. No se duplican por feature.

Esas utilidades implementan el contrato remoto estable del proyecto; no deben inventar un contrato paralelo distinto del definido en `kb-kmm-network-contracts`.

→ Templates: `references/ktor_http_templates.md`

`tryCall` y su `responseHandler` por defecto deben devolver `AppResult<T, AppError>`. `NetworkError` es una implementación concreta de `AppError`, no el contrato principal que se propaga por la app.

---

## Regla 6: Logging de Ktor detrás del logger transversal

El plugin `Logging` no habla directamente con una librería de logging de plataforma. Debe delegar en una abstracción compartida del proyecto.

---

## Regla 7: Convenciones JSON opcionales se aplican por cliente

Opciones como `ignoreUnknownKeys` o `classDiscriminator = "\$type"` pertenecen a la configuración del cliente concreto. Si una API no necesita esa convención, no se aplica por defecto.

---

## Regla 8: La estrategia de auth no se define aquí

Si el proyecto usa Bearer automático, refresh token o varios clientes, consultar:

- `kb-kmm-auth-contracts`
- `kb-kmm-auth-oauth-keycloak` si aplica
- `kb-kmm-auth-ktor-plugin` si el mecanismo usa plugins de Ktor

---

## Regla 9: Esta skill implementa el borde remoto, no la adaptación a dominio

Ktor llega hasta el límite remoto:

- construye requests
- ejecuta llamadas HTTP
- aplica serialización
- traduce excepciones y respuestas al contrato remoto acordado

La transformación desde ese contrato remoto a dominio pertenece al repositorio y se rige por:

- `kb-kmm-network-contracts`
- `kb-kmm-feature-clean-architecture`
- `kb-kmm-core-layer` si la pieza es transversal

Cuando una feature define una pieza HTTP propia, el naming preferido del proyecto para ese borde concreto es `<Feature>Api`.

---

## Regla 10: `tryCall` centraliza excepciones; `responseHandler` es inyectable para contratos HTTP especiales

`tryCall` captura todas las excepciones del cliente Ktor y las normaliza a `AppError`. Es el único punto donde se tocan `ConnectTimeoutException`, `SocketTimeoutException`, `JsonConvertException` y similares.

La interpretación del `HttpResponse` no es fija: `tryCall` acepta un parámetro `responseHandler` que se puede sustituir cuando un endpoint necesita tratar éxitos no estándar (`202`, `204`, etc.), parsear bodies de error ricos o devolver una taxonomía distinta a `NetworkError`.

- `defaultResponseHandler` es la implementación por defecto: resuelve el caso común (`2xx -> body<T>()`) y mapea errores HTTP a `NetworkError`
- los handlers alternativos se usan desde la `Api` de la feature o desde `core/network/` y devuelven `AppResult<T, AppError>`
- si el handler es trivial, puede quedarse privado en la `Api`; si tiene lógica propia o crece, la preferencia es extraerlo a `data/responseHandlers/`
- las clases `Api` no repiten parsing de status código por código fuera de su `responseHandler` específico

→ Templates: `references/ktor_http_templates.md`

## Checklist antes de cerrar

- ¿Cada llamada HTTP de la `Api` usa `tryCall` como wrapper común?
- ¿Se evitó duplicar manualmente `try/catch` y parsing de status codes dentro de la `Api`?
- ¿Los contratos HTTP especiales del endpoint se resolvieron con `responseHandler` en lugar de reimplementar el wrapper?
- ¿La `Api` devuelve DTOs o modelos técnicos, y no modelos de dominio?
- ¿Los `responseHandler` no triviales están separados del request-building cuando ya tienen entidad propia?
- ¿La `Api` sigue siendo el único punto de `data` que toca el cliente HTTP?
