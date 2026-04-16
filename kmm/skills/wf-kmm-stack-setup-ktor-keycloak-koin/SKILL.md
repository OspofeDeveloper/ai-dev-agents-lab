---
name: wf-kmm-stack-setup-ktor-keycloak-koin
description: "Atajo para configurar el stack KMM más habitual basado en Koin, Ktor y OAuth con Keycloak, componiendo skills separadas sin convertirlas en una única fuente mezclada."
argument-hint: "[APP_BASE_URL, IDS_BASE_URL, realm, client_id, grant types, entornos y uso opcional de $type]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-implementer
---

# wf-kmm-stack-setup-ktor-keycloak-koin

## Paso 1: Tratar esta workflow como composición, no como fuente normativa

Esta skill existe como atajo para tu stack habitual. No define reglas nuevas: compone varias skills especializadas.

---

## Paso 2: Aplicar primero las reglas de arquitectura por capa

Aplicar:

- `kb-kmm-clean-architecture`
- `kb-kmm-core-layer`
- `kb-kmm-feature-clean-architecture`
- `kb-kmm-app-layer`
- `kb-koin`

Con esto se decide:

- qué piezas van a `core`
- qué piezas viven dentro de una feature
- qué wiring o composición pertenece a `app`
- cómo se registran dependencias en Koin

---

## Paso 3: Aplicar contratos estables antes que mecanismos concretos

Aplicar:

- `kb-kmm-network-contracts`
- `kb-kmm-auth-contracts`
- `kb-kmm-auth-oauth-keycloak`

Con esto se fijan:

- contrato remoto y taxonomía de errores
- política de sesión y refresh
- contrato específico con Keycloak

No implementar todavía Ktor ni el plugin de auth antes de tener cerrados estos contratos.

---

## Paso 4: Aplicar implementaciones técnicas concretas

Aplicar:

- `kb-kmm-http-ktor`
- `kb-kmm-auth-ktor-plugin`

Con esto se implementa:

- el borde HTTP con Ktor
- la integración técnica de auth automática sobre Ktor
- el patrón de dos clientes si el refresh interceptado lo requiere

No trasladar a estas skills decisiones de política de auth, proveedor OAuth o ubicación arquitectónica.

---

## Paso 5: Ejecutar la configuración del proyecto

1. añadir dependencias necesarias de Ktor, Koin y auth
2. crear contratos compartidos en `core` o contratos propios en feature según indiquen las skills de capa
3. implementar `IdentityApi` y demás piezas específicas de Keycloak
4. implementar cliente HTTP de identidad y cliente HTTP de app
5. instalar el plugin de auth en el cliente de app si aplica
6. registrar dependencias en Koin sin mezclar contratos con implementaciones
7. verificar que las features consumen solo el cliente autenticado y no coordinan refresh manualmente

---

## Paso 6: Mantener separación explícita entre contrato, proveedor y mecanismo

Durante la ejecución, distinguir siempre estas tres dimensiones:

- contrato remoto y contrato de sesión
- proveedor OAuth concreto, como Keycloak
- mecanismo técnico usado para aplicar auth en Ktor

Si una decisión cambia al sustituir Keycloak pero no al sustituir Ktor, no pertenece a `kb-kmm-auth-ktor-plugin`.

Si una decisión cambia al sustituir Ktor pero no al sustituir Keycloak, no pertenece a `kb-kmm-auth-oauth-keycloak`.

---

## Paso 7: Informar sin mezclar capas

Reportar al usuario en tres bloques:

- contratos y reglas estructurales aplicadas
- implementaciones concretas elegidas
- pasos manuales pendientes por entorno o plataforma
