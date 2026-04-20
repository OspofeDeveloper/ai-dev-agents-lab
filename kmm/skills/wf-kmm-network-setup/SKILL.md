---
name: wf-kmm-network-setup
description: "Configura la capa de networking en un proyecto KMM componiendo reglas de arquitectura, DI y la implementación HTTP elegida sin acoplar la skill a una única estrategia de auth."
argument-hint: "[stack HTTP, URLs base, entornos, convenciones JSON y estrategia de auth si aplica]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-network-auth-implementer
---

# wf-kmm-network-setup

## Paso 1: Recopilar decisiones estructurales

Confirmar con el usuario o inferir del proyecto:

1. arquitectura base del proyecto y ubicación de capas, siguiendo `kb-kmm-clean-architecture`
2. reglas de `core`, siguiendo `kb-kmm-core-layer`
3. reglas de microarquitectura de feature, siguiendo `kb-kmm-feature-clean-architecture`
4. reglas de `app`, siguiendo `kb-kmm-app-layer`
5. librería de DI activa, siguiendo la skill correspondiente (`kb-koin` si aplica)
6. contrato transversal de resultado y error, siguiendo `kb-kmm-app-errors`
7. implementación HTTP elegida (`kb-kmm-http-ktor` si aplica)
8. si existe auth y cuál es su estrategia (`kb-kmm-auth-contracts` + skill específica)
9. convenciones del backend como discriminadores JSON, errores especiales o múltiples URLs base

No asumir una estrategia de auth concreta por el mero hecho de configurar networking.

---

## Paso 2: Leer el estado actual del proyecto

Leer dependencias, módulos DI, configuración por entorno, estructura de `core/` y features para detectar qué contratos ya existen y qué piezas faltan.

---

## Paso 3: Crear primero los contratos estables

Aplicar:

- `kb-kmm-clean-architecture` para respetar la topología global
- `kb-kmm-core-layer` para decidir qué contratos o infraestructura van a `core`
- `kb-kmm-feature-clean-architecture` para decidir qué piezas viven dentro de una feature
- `kb-kmm-app-layer` para reservar en `app` solo el wiring y la composición final
- `kb-kmm-app-errors` para fijar el contrato transversal `AppResult` / `AppError`
- `kb-kmm-network-contracts` para definir errores, resultados y límites entre servicios y repositorios
- la skill de DI activa para definir el patrón de registro

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

Si el stack no es Ktor, usar la skill equivalente y no mezclar criterios de esta workflow con una librería distinta.

---

## Paso 5: Integrar auth solo si forma parte del alcance

Si el proyecto requiere autenticación:

- aplicar `kb-kmm-auth-contracts`
- aplicar la skill del proveedor OAuth correspondiente si existe
- aplicar la skill del mecanismo concreto de integración con el cliente HTTP solo si está confirmada

---

## Paso 6: Registrar en DI respetando la separación de responsabilidades

Registrar clientes, APIs, repositorios y configuración en la DI activa sin trasladar reglas de arquitectura o auth a la skill de DI.

La selección de ubicación antes del registro sigue estas reglas:

- contratos o utilidades realmente transversales -> `core`
- repositorios, data sources y servicios propios de una única feature -> dentro de la feature
- composición global o wiring final -> `app`

---

## Paso 7: Informar con separación clara

Reportar al usuario qué contratos se han creado, qué implementaciones concretas se han elegido y qué partes quedan abiertas por depender de decisiones de proveedor o mecanismo.
