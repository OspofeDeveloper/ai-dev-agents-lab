---
name: kb-kmm-navigation-contracts
description: "Base de conocimiento de contratos de navegación en proyectos KMM: ownership entre app y features, rutas como contrato central, encapsulación del NavController y separación entre navegación, features y composición."
argument-hint: ""
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KMM Navigation Contracts — Base de Conocimiento

## Regla 1: La navegación es una decisión de composición de `app`

La navegación concreta pertenece a `app`, no a las features.

`app` decide:

- qué grafo existe
- qué destino se activa
- cómo se resuelven las salidas de una feature
- cómo se compone el shell de navegación

Esto se alinea con:

- `kb-kmm-app-layer`
- `kb-kmm-clean-architecture`

---

## Regla 2: Las features emiten salidas; no navegan directamente

Una feature no recibe el `NavController` ni decide rutas concretas.

La feature:

- expone callbacks de salida
- emite hechos de navegación o efectos de dominio
- delega en `app` la resolución del destino concreto

Esto mantiene la feature desacoplada del grafo global.

---

## Regla 3: El contrato de rutas es central y compartido

Las rutas o destinos forman un contrato central de navegación accesible desde `app`.

Las features no dependen entre sí para navegar. Si una feature necesita salir hacia otra, lo expresa mediante un callback o efecto, nunca importando directamente su destino concreto.

---

## Regla 4: El `NavController` está encapsulado

El `NavController` o equivalente vive en el shell composable de nivel superior o en el owner del grafo.

No debe:

- exponerse a features
- guardarse en un `CompositionLocal` global
- formar parte del estado de dominio

---

## Regla 5: Las rutas son contrato; el mecanismo concreto vive en otra skill

Esta skill define el contrato arquitectónico de navegación:

- ownership
- fronteras
- flujo entre `app` y features

No define cómo se implementa ese contrato con una librería concreta.

La implementación Compose Navigation vive en `kb-kmm-navigation-compose`.

---

## Regla 6: Los efectos de navegación son un contrato distinto del grafo

Cuando la navegación depende de lógica de negocio, el ViewModel emite un efecto o evento de navegación.

La forma de modelar ese efecto en ViewModel/Composable vive en `kb-plan-kmm-navigation-viewmodel-events`, no en esta skill.

---

## Regla 7: La navegación no rompe la independencia entre features

Las features:

- no conocen rutas de otras features
- no dependen unas de otras para navegar
- no comparten `NavController`

La composición entre features se resuelve desde `app`.
