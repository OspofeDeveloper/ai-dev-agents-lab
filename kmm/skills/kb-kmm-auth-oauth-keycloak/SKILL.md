---
name: kb-kmm-auth-oauth-keycloak
description: "Base de conocimiento de OAuth con Keycloak en proyectos KMM: endpoints de token, parámetros requeridos, grant types, payloads form-urlencoded y configuración por entorno."
argument-hint: ""
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# OAuth Keycloak KMM — Base de Conocimiento

## Regla 1: Keycloak es un proveedor concreto de OAuth

Esta skill solo define lo específico de Keycloak. No define por sí sola cómo se persiste la sesión ni cómo se integra con el cliente HTTP.

---

## Regla 2: El token endpoint depende del realm

La ruta de token se construye como:

```text
/realms/{realm}/protocol/openid-connect/token
```

`realm` es configuración del proyecto o del entorno. No se hardcodea dentro de la implementación.

→ Templates: `references/keycloak_auth_templates.md`

---

## Regla 3: Login y refresh usan formulario

Las peticiones de login y refresh se envían como `application/x-www-form-urlencoded` con `submitForm` o mecanismo equivalente.

Parámetros habituales:
- `grant_type`
- `client_id`
- `username` y `password` en login
- `refresh_token` en refresh

→ Templates: `references/keycloak_auth_templates.md`

---

## Regla 4: Los grant types son configuración, no literales dispersos

Valores como `password` o `refresh_token` deben venir de configuración o constantes centralizadas, no estar repetidos en varias features.

---

## Regla 5: La respuesta de Keycloak se normaliza

Los DTOs de token de Keycloak se transforman a un modelo interno del proyecto antes de ser consumidos por el resto de capas.

---

## Regla 6: El provider no define el mecanismo de refresh automático

Esta skill solo cubre el contrato con Keycloak. Si el proyecto implementa refresh automático dentro de Ktor, consultar `kb-kmm-auth-ktor-plugin`.
