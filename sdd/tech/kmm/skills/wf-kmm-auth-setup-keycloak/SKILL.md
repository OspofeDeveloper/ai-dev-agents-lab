---
name: wf-kmm-auth-setup-keycloak
description: "Configura autenticación OAuth con Keycloak en un proyecto KMM separando contratos de sesión, proveedor OAuth y mecanismo técnico de integración con el cliente HTTP."
when_to_use: "Activa con frases como 'configura auth con Keycloak', 'añade autenticación OAuth al proyecto KMM', 'setup de Keycloak', 'integra autenticación con el cliente HTTP'. No activa para configurar el stack completo (usa wf-kmm-stack-setup-ktor-keycloak-koin) ni para setup de networking sin auth (usa wf-kmm-network-setup)."
argument-hint: "[IDS_BASE_URL, realm, client_id, grant types, estrategia de refresh y mecanismo HTTP]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-network-auth-implementer
user-invocable: true
---

# wf-kmm-auth-setup-keycloak

## Paso 1: Tratar esta workflow como composición, no como fuente normativa

Esta skill configura auth con Keycloak componiendo varias skills especializadas.

No define reglas nuevas de arquitectura, sesión, proveedor ni mecanismo HTTP.

---

## Paso 2: Confirmar primero arquitectura y ubicación de piezas

Aplicar:

- `kb-kmm-clean-architecture` -> **Regla 2**
- `kb-kmm-core-layer` -> **Regla 7** y **Regla 13**
- `kb-kmm-feature-clean-architecture` -> **Regla 7** y **Regla 12**
- `kb-kmm-app-layer` -> **Regla 8**
- `kb-kmm-app-errors` -> **Regla 1**, **Regla 5** y **Regla 6**

Con esto se decide:

- dónde vive el contrato de sesión
- qué contrato transversal de resultado y error usa la app
- qué piezas son transversales y van a `core`
- qué implementaciones pertenecen a una feature concreta
- qué wiring final o composición pertenece a `app`

---

## Paso 3: Confirmar la política de auth

Aplicar `kb-kmm-auth-contracts` para confirmar:

- si hay access token y refresh token
- cómo se detecta la sesión expirada
- qué endpoints son públicos
- dónde vive el contrato de sesión o store de tokens
- cómo auth se integra en `AppResult` / `AppError`

Usar como ancla la **Regla 2**, la **Regla 3** y la **Regla 4** de `kb-kmm-auth-contracts`.

---

## Paso 4: Confirmar detalles específicos de Keycloak

Aplicar `kb-kmm-auth-oauth-keycloak` y recopilar:

- `IDS_BASE_URL`
- `realm`
- `client_id`
- grant type de login
- grant type de refresh
- entornos y variaciones de configuración

Usar como ancla la **Regla 2**, la **Regla 3** y la **Regla 4** de `kb-kmm-auth-oauth-keycloak`.

---

## Paso 5: Leer el mecanismo HTTP activo

Detectar si el proyecto usa Ktor u otra librería HTTP. No asumir que Keycloak implica Ktor.

---

## Paso 6: Crear contratos antes que implementaciones

Crear o verificar:

- store o repositorio de sesión
- eventos de sesión
- API de identidad
- modelos internos de token

La ubicación de estas piezas debe respetar las skills de capa. No asumir que todo contrato de auth vive automáticamente en `core` sin comprobar si es realmente transversal.

La separación entre contrato, proveedor e implementación debe seguir la **Regla 7** de `kb-kmm-auth-contracts`.

---

## Paso 7: Implementar el proveedor Keycloak

Crear la implementación de `IdentityApi` con formulario y ruta del token endpoint siguiendo `kb-kmm-auth-oauth-keycloak`.

Aplicar específicamente la **Regla 2**, la **Regla 3** y la **Regla 5** de esa skill.

Si la `Api` necesita parsear errores ricos del login o tratar respuestas de éxito especiales, hacerlo a través del `responseHandler` del wrapper remoto común descrito en `kb-kmm-http-ktor`, no duplicando `try/catch`.

---

## Paso 8: Implementar el mecanismo técnico de refresh solo después

Separar explícitamente estas dimensiones:

- política de sesión -> `kb-kmm-auth-contracts`
- proveedor OAuth -> `kb-kmm-auth-oauth-keycloak`
- mecanismo técnico -> skill HTTP o plugin correspondiente

No mezclar decisiones de proveedor con decisiones de mecanismo.

---

## Paso 9: Implementar el mecanismo técnico de refresh

Solo si el proyecto usa Ktor y la estrategia acordada es auth automática en el cliente, aplicar `kb-kmm-auth-ktor-plugin`.

Usar como ancla la **Regla 1**, la **Regla 2**, la **Regla 4** y la **Regla 7** de `kb-kmm-auth-ktor-plugin`.

Si el proyecto usa otro mecanismo, implementar la variante correspondiente sin introducir reglas de Ktor en esta workflow.

---

## Paso 10: Registrar e informar

Registrar las piezas en DI respetando la separación entre contratos, proveedor e implementaciones técnicas.

Reportar por separado:

- contratos de auth creados
- integración Keycloak creada
- mecanismo técnico elegido para aplicar auth en requests
