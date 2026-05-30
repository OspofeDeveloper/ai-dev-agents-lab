---
name: kb-kmm-auth-ktor-plugin
description: "Base de conocimiento de autenticación automática implementada con plugins de Ktor en proyectos KMM: dos clientes HTTP, plugin de auth, bypass para endpoints públicos y refresh transparente de tokens."
argument-hint: ""
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Auth con Plugin de Ktor — Base de Conocimiento

## Regla 1: Esta skill implementa el mecanismo de auth automática sobre Ktor

Esta skill es una implementación concreta. Depende de:

- `kb-kmm-auth-contracts` para política de sesión
- `kb-kmm-http-ktor` para el mecanismo HTTP
- `kb-tasks-koin` o la skill de DI activa para el registro de dependencias

No define:

- política general de sesión
- contrato del proveedor OAuth
- taxonomía global de errores
- ubicación arquitectónica de capas
- la librería de DI concreta

---

## Regla 2: Patrón de dos clientes cuando el refresh usa HTTP independiente

Si el refresh token se ejecuta desde el propio mecanismo HTTP interceptado, usar dos instancias separadas de cliente:

| Cliente | Propósito |
|---------|-----------|
| Cliente Identity | login y refresh contra el proveedor OAuth |
| Cliente App | API principal con autenticación automática |

La separación evita recursión o dependencias circulares durante el refresh.

→ Templates: `${CLAUDE_SKILL_DIR}/references/ktor_auth_plugin_templates.md`

---

## Regla 3: Plugin de autenticación en el cliente de app

El cliente autenticado instala un plugin que:

1. detecta bypass para endpoints públicos
2. consulta tokens almacenados
3. comprueba expiración
4. intenta refresh si procede
5. inyecta el Bearer token si existe
6. emite evento de sesión expirada si el refresh ya no es válido

→ Templates: `${CLAUDE_SKILL_DIR}/references/ktor_auth_plugin_templates.md`

---

## Regla 4: Convención de bypass para endpoints públicos

Si un endpoint público se ejecuta con el cliente autenticado, debe existir una convención explícita para omitir auth.

La convención concreta puede variar. En una implementación típica se usa un header técnico como `No-Auth: true`, que el plugin elimina antes de enviar la request.

---

## Regla 5: El plugin puede necesitar bloqueo controlado

La API de plugins de Ktor puede obligar a usar `runBlocking` para leer flows o ejecutar refresh dentro de hooks como `onRequest`. Ese detalle pertenece solo a esta implementación.

Si la operación de refresh devuelve resultado, la convención preferida es `AppResult<TokenInfo, AppError>` o equivalente. El plugin reacciona a `onSuccess` / `onError`; no necesita un contrato especial distinto del resto del proyecto.

La definición transversal de `AppResult` y `AppError` pertenece a `kb-kmm-app-errors`. Esta skill solo implementa cómo el plugin técnico se integra con ese contrato.

---

## Regla 6: Los servicios de feature consumen solo el cliente autenticado

Las features consumen el cliente principal. Solo la implementación del proveedor de identidad usa el cliente secondary de Identity.

---

## Regla 7: Esta skill automatiza refresh; no define el proveedor ni el contrato de sesión

El plugin de Ktor solo orquesta:

- lectura del estado de sesión
- decisión técnica de adjuntar token o intentar refresh
- bypass de endpoints públicos
- emisión del comportamiento técnico cuando la sesión ya no es recuperable

La semántica de sesión, expiración y proveedor OAuth pertenece a:

- `kb-kmm-app-errors`
- `kb-kmm-auth-contracts`
- la skill del proveedor concreta, como `kb-kmm-auth-oauth-keycloak`

---

## Regla 8: La integración con DI y configuración es externa al plugin

El plugin necesita dependencias como session store, función de refresh o URLs base, pero esta skill no impone cómo se resuelven.

La resolución concreta por DI, factories o wiring manual pertenece a la skill de DI activa o al composition root del proyecto.
