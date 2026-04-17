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

Helpers como `tryCall`, `handleResponse`, mappers de excepción o loggers de Ktor viven en `core/network` o equivalente. No se duplican por feature.

Esas utilidades implementan el contrato remoto estable del proyecto; no deben inventar un contrato paralelo distinto del definido en `kb-kmm-network-contracts`.

→ Templates: `references/ktor_http_templates.md`

`tryCall` y `handleResponse` deben devolver `AppResult<T, AppError>`. `NetworkError` es una implementación concreta de `AppError`, no el contrato principal que se propaga por la app.

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

---

## Regla 10: El parsing de error backend y el mapeo de status viven en helpers Ktor compartidos

Cuando una API devuelve varios formatos de body de error, esa lógica se concentra en helpers compartidos del cliente Ktor.

Patrón recomendado:

- `tryCall` captura excepciones del cliente y las mapea a `AppError`
- `handleResponse` transforma status HTTP y bodies de error a `AppError`
- cuando el error es de red, la implementación concreta suele ser `NetworkError : AppError`
- las APIs concretas solo describen request y response body

Las clases API no deberían repetir parsing de `400`, `401`, `409` o variantes del backend endpoint por endpoint.
