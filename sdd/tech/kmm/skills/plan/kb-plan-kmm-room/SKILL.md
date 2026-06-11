---
name: kb-plan-kmm-room
description: Persistencia relacional con Room en KMM como decisión arquitectónica de plan: cuándo Room vs Preferences DataStore, la base de datos como Single Source of Truth, entidades y DAOs como contrato local, ownership del módulo de DB (core vs feature) y qué debe contemplar el plan.
allowed-tools: [Read]
effort: low
user-invocable: false
---

# Room en KMM — Planificación

→ Implementación concreta (entidades, DAOs, @Database, builder por plataforma, KSP, migraciones): `kb-tasks-kmm-room`

## Qué es Room en este contexto

El stack usa **Room** para persistencia relacional en KMP, **no SQLDelight**. Room expone entidades, DAOs y consultas tipadas sobre SQLite, con lecturas reactivas vía `Flow`. Es el mecanismo cuando los datos son relacionales, consultables o colecciones que se filtran/ordenan.

No es un contrato de dominio: sobre los DAOs vive un repositorio con semántica de negocio (patrón de `kb-kmm-feature-clean-architecture`).

## Room vs Preferences DataStore

| Necesidad | Mecanismo |
|---|---|
| Datos relacionales, colecciones, consultas, filtrado, joins | **Room** |
| Clave-valor simple: preferencias, sesión, flags, configuración | **Preferences DataStore** → `kb-plan-kmm-datastore-preferences` |

No usar Room para guardar cuatro flags; no usar DataStore para una lista consultable de entidades. El plan elige el mecanismo por la forma del dato, no por costumbre.

## La base de datos como Single Source of Truth

Cuando hay caché/offline, la DB es la fuente de verdad: la UI observa la DB vía `Flow`, la red **escribe** en la DB, la UI no depende directamente de la red. Esta dimensión caché/offline (stale-while-revalidate, frescura vs disponibilidad) vive en `kb-kmm-offline-strategy`, que se apoya en Room como mecanismo de SSoT. Aquí solo se fija que Room es el sitio donde esa SSoT materializa.

## Ownership del módulo de DB: core vs feature

| Situación | Ubicación |
|---|---|
| La DB la comparten varias features (catálogo, sesión, datos transversales) | `:core:database` — infraestructura transversal |
| El estado persistido es propio de una sola feature y no tiene significado fuera | dentro de la feature |

El criterio lógico de "qué es transversal" es de `kb-kmm-core-layer`; la decisión de microarquitectura interna, de `kb-kmm-feature-clean-architecture`. La materialización en módulo Gradle (`:core:database`) la cubre `kb-kmm-gradle-modules`. El plan declara explícitamente dónde vive la DB y por qué.

## Qué debe contemplar el plan

1. Módulo donde vive la base de datos (`:core:database` transversal o módulo de feature).
2. Entidades a persistir y su relación con el dominio (las entidades de DB no son los modelos de dominio crudos).
3. DAOs como contrato local: lecturas exponen `Flow<…>`; escrituras `suspend`.
4. Estrategia de migraciones: esquema versionado desde el inicio.
5. Registro DI del builder/DB (apóyate en `kb-plan-koin`; normalmente en el módulo dependiente de plataforma).
6. Que sobre los DAOs existe un repositorio con semántica — no se propaga el DAO crudo a capas superiores.

## Relación con otras skills del plan

- Decisión clave-valor alternativa: `kb-plan-kmm-datastore-preferences`
- Caché y offline-first sobre Room: `kb-kmm-offline-strategy`
- Ownership de capa y módulo: `kb-kmm-core-layer`, `kb-kmm-feature-clean-architecture`, `kb-kmm-gradle-modules`
- Wiring DI: `kb-plan-koin`
- Implementación concreta: `kb-tasks-kmm-room`
