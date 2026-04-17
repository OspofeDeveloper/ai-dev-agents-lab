---
name: kb-kmm-auth-contracts
description: "Base de conocimiento de contratos de autenticación en proyectos KMM: tokens, refresh, expiración de sesión, endpoints públicos y separación entre política de auth y mecanismo de transporte."
argument-hint: ""
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Auth Contracts KMM — Base de Conocimiento

## Regla 1: La auth es una política transversal

La autenticación define reglas de sesión y acceso, no la tecnología concreta que la implementa. Esta skill describe la política estable aunque cambie Ktor, el proveedor OAuth o la DI.

La ubicación concreta de estos contratos se decide con las skills de capa:

- `kb-kmm-core-layer` si el contrato es transversal
- `kb-kmm-feature-clean-architecture` si la pieza pertenece a una única feature
- `kb-kmm-app-layer` si solo existe como wiring o coordinación de composición

---

## Regla 2: Contrato explícito de tokens y sesión

Si el proyecto usa access token y refresh token, debe existir un contrato claro para:

- leer y guardar access token
- leer y guardar refresh token
- conocer expiración del access token
- conocer expiración del refresh token
- limpiar sesión
- emitir eventos de sesión expirada cuando aplique

Si las operaciones de login, refresh o lectura técnica de sesión devuelven resultado, la convención preferida es `AppResult<T, AppError>`.

→ Templates: `references/auth_contracts_templates.md`

---

## Regla 3: Refresh automático es una política, no un detalle de cliente

La regla estable es: si el access token expira y todavía existe refresh token válido, el sistema intenta renovarlo antes de dar la sesión por perdida.

Cómo se implementa ese refresh depende de la tecnología concreta y debe vivir en una skill de implementación.

El refresh no debe inventar un contrato de error distinto al resto del proyecto. Si falla, devuelve `AppError` y deja que el mecanismo técnico o la capa superior reaccionen en consecuencia.

---

## Regla 4: Endpoints públicos y privados

El proyecto debe poder distinguir endpoints públicos de endpoints autenticados. La convención concreta para hacer bypass de auth depende del mecanismo técnico usado.

---

## Regla 5: Los consumers no conocen el refresh interno

Use cases, ViewModels y servicios de feature no deberían coordinar manualmente el ciclo de refresh si la estrategia del proyecto lo automatiza. Deben consumir la API ya autenticada.

---

## Regla 6: Los proveedores OAuth son variantes de implementación

Keycloak, Auth0 u otro proveedor no cambian la política general de sesión. Lo específico del proveedor debe vivir en una skill separada.

---

## Regla 7: Esta skill define política de sesión; otras skills definen proveedor y mecanismo

Esta skill se combina con:

- skills de proveedor OAuth, como `kb-kmm-auth-oauth-keycloak`
- skills de mecanismo técnico, como `kb-kmm-auth-ktor-plugin`
- skills de capa para decidir ubicación y ownership

No duplicar aquí reglas propias del proveedor, del cliente HTTP o de la DI.
