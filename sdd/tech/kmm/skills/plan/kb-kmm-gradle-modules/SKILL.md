---
name: kb-kmm-gradle-modules
description: Estructura de módulos Gradle en KMM como decisión de plan: cómo materializar las capas lógicas (app/core/feature) en módulos físicos (:composeApp, :core:*, :feature:*), convenciones de nombrado, convention plugins en build-logic/, version catalog y dependencias permitidas entre módulos. Úsalo cuando el plan deba traducir capas lógicas a módulos Gradle concretos.
allowed-tools: [Read]
effort: low
user-invocable: false
---

# Módulos Gradle en KMM — Planificación

Esta KB materializa las **capas lógicas** del stack en **módulos físicos** de Gradle. El ownership lógico y las reglas de capa NO se redefinen aquí:

→ Qué pertenece a cada capa y por qué: `kb-kmm-clean-architecture` (topología `app/features/core`), `kb-kmm-core-layer` (qué es transversal), `kb-kmm-feature-clean-architecture` (microarquitectura interna de feature).

Esta skill solo decide **cómo se reparte ese mapa lógico en módulos Gradle**: cuándo una capa lógica merece un módulo propio, cómo se nombra y qué puede depender de qué.

## Capa lógica vs módulo físico

Una capa lógica no es siempre un módulo separado. La granularidad física es una decisión de plan:

| Capa lógica | Módulo físico típico | Cuándo se separa |
|---|---|---|
| `app` (composition root, navegación) | `:composeApp` (KMP) o `:app` (Android-only) | Siempre — es el host |
| `core` transversal | `:core:network`, `:core:database`, `:core:designsystem`, `:core:common`... | Un módulo por dominio transversal estable |
| `feature` | `:feature:<nombre>` | Un módulo por feature con superficie propia |

No fragmentar en módulos antes de tiempo: un `core` pequeño puede empezar como `:core:common` único y dividirse cuando una pieza (DB, network) gana peso propio. El plan declara la granularidad inicial y justifica cada split.

## Convenciones de nombrado

- Host: `:composeApp` (proyecto KMP con Compose Multiplatform) o `:app` (si el repo ya lo nombra así — manda el repo).
- Transversales: `:core:<dominio>` — p. ej. `:core:network`, `:core:database`, `:core:designsystem`, `:core:common`, `:core:datastore`.
- Features: `:feature:<nombre>` — un nombre por capacidad funcional.

Si el `kmm_project_state.md` declara otra convención de nombrado real del repo, **manda el repo** (precedencia de `kb-kmm-project-state-protocol`, Regla 7). El canon de arriba es el default para greenfield.

## Dependencias permitidas entre módulos

La dirección de dependencias física debe respetar las fronteras lógicas:

```
:composeApp ──▶ :feature:* ──▶ :core:*
                              ▲
:feature:* ───────────────────┘   (features dependen de core)
```

Reglas duras:

- `:feature:*` puede depender de `:core:*`. **Nunca** `:core:*` de `:feature:*`.
- Dos features **no se ven entre sí**: lo compartido sube a `core` (criterio lógico en `kb-kmm-core-layer`).
- `:composeApp` ve features y core; nadie depende de `:composeApp`.

Una dependencia que viole esto es señal de que una pieza está mal ubicada lógicamente — se resuelve en la capa lógica, no parcheando el grafo Gradle.

## Convention plugins y version catalog

La configuración repetida de `build.gradle.kts` no se copia por módulo:

- **`build-logic/`**: convention plugins compartidos (compilación KMP, targets, configuración común de KSP/Compose). Cada módulo aplica el plugin de convención que le toca en vez de repetir bloques.
- **`libs.versions.toml`** (version catalog): única fuente de versiones y coordenadas de dependencias. Los módulos referencian `libs.*`, no versiones literales.

Si el repo ya tiene buildSrc o composición distinta, se respeta (manda el repo).

## Qué debe contemplar el plan

1. Qué módulos físicos existen y cuáles se crean nuevos para esta feature.
2. A qué módulo pertenece cada pieza lógica del plan (mapeo capa → módulo).
3. Dependencias nuevas entre módulos y verificación de que respetan la dirección permitida.
4. Si una pieza transversal nueva justifica un `:core:<dominio>` propio o entra en uno existente.
5. Convention plugin y entradas de version catalog necesarias para los módulos tocados.

## Relación con otras skills del plan

- Ownership lógico y fronteras de capa: `kb-kmm-clean-architecture`, `kb-kmm-core-layer`, `kb-kmm-feature-clean-architecture` (SSoT — no duplicar aquí).
- Módulo de base de datos (`:core:database`): `kb-plan-kmm-room`.
- Wiring DI entre módulos: `kb-plan-koin`.
- Precedencia del repo real sobre el canon: `kb-kmm-project-state-protocol`, Regla 7.
