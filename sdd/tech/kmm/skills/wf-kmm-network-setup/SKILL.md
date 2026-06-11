---
name: wf-kmm-network-setup
description: "Configura la capa de networking en un proyecto KMM componiendo reglas de arquitectura, DI y la implementación HTTP elegida sin acoplar la skill a una única estrategia de auth."
when_to_use: "Activa con frases como 'configura networking en KMM', 'añade capa de red al proyecto', 'setup de Ktor', 'configura el cliente HTTP', 'añade networking sin auth'. No activa si también se necesita auth con Keycloak (usa wf-kmm-auth-setup-keycloak) ni para el stack completo (usa wf-kmm-stack-setup-ktor-keycloak-koin)."
argument-hint: "[stack HTTP, URLs base, entornos, convenciones JSON y estrategia de auth si aplica]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-network-auth-implementer
user-invocable: true
---

# wf-kmm-network-setup

## Paso 1: Recopilar decisiones estructurales

Confirmar con el usuario o inferir del proyecto:

1. arquitectura base del proyecto y ubicación de capas, siguiendo la **Regla 2** de `kb-kmm-clean-architecture`
2. reglas de `core`, siguiendo la **Regla 3** y la **Regla 7** de `kb-kmm-core-layer`
3. microarquitectura de feature, siguiendo la **Regla 2** y la **Regla 7** de `kb-kmm-feature-clean-architecture`
4. reglas de `app`, siguiendo la **Regla 1** y la **Regla 8** de `kb-kmm-app-layer`
5. librería de DI activa, siguiendo la **Regla 1** y la **Regla 2** de la skill correspondiente (`kb-tasks-koin` si aplica)
6. contrato transversal de resultado y error, siguiendo la **Regla 1** y la **Regla 3** de `kb-kmm-app-errors`
7. implementación HTTP elegida, siguiendo la **Regla 1** y la **Regla 2** de la skill concreta (`kb-kmm-http-ktor` si aplica)
8. si existe auth y cuál es su estrategia, siguiendo `kb-kmm-auth-contracts` y la skill específica aplicable
9. convenciones del backend como discriminadores JSON, errores especiales o múltiples URLs base

No asumir una estrategia de auth concreta por el mero hecho de configurar networking.

---

## Paso 2: Leer el estado actual del proyecto

Leer dependencias, módulos DI, configuración por entorno, estructura de `core/` y features para detectar qué contratos ya existen y qué piezas faltan.

---

## Paso 3: Crear primero los contratos estables

Aplicar:

- `kb-kmm-clean-architecture` -> **Regla 2**
- `kb-kmm-core-layer` -> **Regla 7** y **Regla 13**
- `kb-kmm-feature-clean-architecture` -> **Regla 7** y **Regla 12**
- `kb-kmm-app-layer` -> **Regla 8**
- `kb-kmm-app-errors` -> **Regla 1**, **Regla 5** y **Regla 6**
- `kb-kmm-network-contracts` -> **Regla 3**, **Regla 5**, **Regla 6** y **Regla 11**
- la skill de DI activa -> reglas de wiring, nunca ownership

No crear todavía mecanismos acoplados a auth si no están confirmados.

---

## Paso 4: Implementar la librería HTTP elegida

Si el stack es Ktor, aplicar `kb-kmm-http-ktor` para:

- dependencias Gradle
- cliente o clientes HTTP necesarios
- serialización
- logging
- timeouts
- utilidades específicas de Ktor
- sin introducir decisiones de DI o auth que pertenezcan a otras skills

Tomar como base la **Regla 2**, la **Regla 5** y la **Regla 10** de `kb-kmm-http-ktor`.

Si el proyecto ya tiene un wrapper remoto común, reutilizarlo. No reimplementar `try/catch` ni parsing manual de status codes dentro de cada `Api`.

**Antes de escribir la versión en `libs.versions.toml`**, leer el fichero y comprobar si ya existe una entrada `ktor`. Si existe, usar esa versión; no sobreescribir con una versión por defecto.

Si el stack no es Ktor, usar la skill equivalente y no mezclar criterios de esta workflow con una librería distinta.

---

## Paso 5: Integrar auth solo si forma parte del alcance

Si el proyecto requiere autenticación:

- aplicar `kb-kmm-auth-contracts`, especialmente su separación entre política y mecanismo
- aplicar la skill del proveedor OAuth correspondiente si existe
- aplicar la skill del mecanismo concreto de integración con el cliente HTTP solo si está confirmada

Si un endpoint necesita errores ricos o contratos HTTP especiales, resolverlos mediante el `responseHandler` del wrapper común y no con lógica duplicada en el servicio.

---

## Paso 6: Registrar en DI respetando la separación de responsabilidades

Registrar clientes, APIs, repositorios y configuración en la DI activa sin trasladar reglas de arquitectura o auth a la skill de DI.

La selección de ubicación antes del registro sigue estas reglas:

- contratos o utilidades realmente transversales -> `core`
- repositorios, data sources y servicios propios de una única feature -> dentro de la feature
- composición global o wiring final -> `app`

El registro en DI sigue la **Regla 1** y la **Regla 10** de la skill de DI activa.

---

## Paso 7: Informar con separación clara

Reportar al usuario qué contratos se han creado, qué implementaciones concretas se han elegido y qué partes quedan abiertas por depender de decisiones de proveedor o mecanismo.
