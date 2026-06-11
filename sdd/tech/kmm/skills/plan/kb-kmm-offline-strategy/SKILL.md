---
name: kb-kmm-offline-strategy
description: "Estrategia de caché y offline-first en KMM como decisión de plan: cuándo cachear, Room como Single Source of Truth, patrón stale-while-revalidate, flujo sin conectividad, frescura vs disponibilidad y errores de red con caché."
allowed-tools: [Read]
effort: low
user-invocable: false
---

# Offline-first y caché en KMM — Planificación

Esta KB añade la dimensión **caché/offline** encima del repositorio de feature. NO redefine el repositorio:

→ Patrón de repositorio (Api → repo, DTO → dominio): `kb-kmm-feature-clean-architecture` (ver `references/feature_remote_data_patterns.md`). SSoT — no se reescribe aquí.
→ Mecanismo de persistencia que actúa como SSoT de caché: `kb-plan-kmm-room` / `kb-tasks-kmm-room`.

**Depende de Room**: el offline-first descrito aquí usa Room como el lugar donde vive la caché. Sin una DB local, gran parte de esta estrategia no aplica.

## Cuándo cachear (no siempre)

La caché no es gratis: añade una DB, sincronización y migraciones. El plan la incluye solo cuando aporta:

- el dato debe seguir disponible sin conectividad (offline-first real)
- el dato se consulta mucho y cambia poco (coste de red evitable)
- la UI necesita arranque instantáneo con el último estado conocido

No cachear si el dato es efímero, siempre requiere frescura absoluta (precio en vivo, OTP) o solo vive durante la sesión → basta `StateFlow` en memoria.

## La base de datos como Single Source of Truth

El invariante del offline-first:

- la **UI observa la DB** vía `Flow`, nunca la red directamente.
- la **red escribe en la DB**; la UI reacciona al cambio de la DB.
- no hay dos fuentes de verdad: la DB es la única que la UI lee.

Esto desacopla la UI de la conectividad: con o sin red, la UI siempre tiene una fuente (la DB) de la que leer.

## Patrón stale-while-revalidate / NetworkBoundResource

El flujo canónico:

1. La UI se suscribe al `Flow` de la DB y muestra de inmediato lo cacheado (aunque sea stale).
2. En paralelo, el repositorio lanza un refresh de red **en background**.
3. La red, al responder, **escribe en la DB**; la UI se actualiza sola por el `Flow`.
4. Si la red falla y hay caché, la UI sigue mostrando lo stale (no rompe).

La red refresca la DB; la UI nunca depende directamente de la red. El plan declara qué entidades siguen este patrón.

## Frescura vs disponibilidad

El plan elige, por dato, la política:

| Prioridad | Comportamiento |
|---|---|
| Disponibilidad (offline-first) | Mostrar caché siempre; refrescar en background; tolerar stale |
| Frescura | Bloquear hasta tener red, o invalidar caché agresivamente con TTL corto |

No es global: una misma feature puede priorizar disponibilidad en una lista y frescura en un detalle transaccional.

## Manejo de errores de red con caché presente

Con caché disponible, un fallo de red **no es necesariamente un error de UI**:

- hay caché → la UI muestra lo stale; el error de refresh se degrada (indicador discreto, no pantalla de error).
- no hay caché y falla la red → ahí sí se propaga el error a la UI (taxonomía `AppError`, de `kb-kmm-app-errors`).

El repositorio distingue "fallo de refresh con caché" de "fallo sin nada que mostrar".

## Qué debe contemplar el plan

1. Qué datos se cachean y cuáles no (criterio de arriba).
2. Política por dato: disponibilidad vs frescura.
3. TTL / invalidación: cuándo lo cacheado se considera stale y cuándo se purga.
4. Módulo donde vive la caché (normalmente el mismo `:core:database` o el módulo de feature — ver `kb-kmm-gradle-modules`).
5. Degradación de errores de red cuando hay caché.

## Relación con otras skills del plan

- Repositorio base (no se redefine): `kb-kmm-feature-clean-architecture`
- DB como SSoT de caché: `kb-plan-kmm-room`, `kb-tasks-kmm-room`
- Módulo físico de la caché: `kb-kmm-gradle-modules`
- Taxonomía de errores: `kb-kmm-app-errors`
