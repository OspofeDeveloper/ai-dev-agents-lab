# Backlog de skills KMM — Pendientes Fase 2

Skills identificadas como necesarias para uso profesional completo, pendientes de crear cuando el flujo actual esté consolidado.

---

## Skills pendientes

### 1. `kb-kmm-gradle-modules` (planning)
Estructura de módulos Gradle: convenciones de nombrado, qué pertenece a `:core:*`, `:feature:*`, `:app`, convention plugins, `build.gradle.kts` compartido. Permite al plan traducir capas lógicas a módulos físicos.

### 2. `kb-kmm-offline-strategy` (planning)
Estrategia de caché y offline-first: cuándo implementar caché, single source of truth desde base de datos, stale-while-revalidate, flujo de datos en ausencia de conectividad. Depende de la skill de Room.

### 3. `kb-kmm-secrets-cicd` (planning)
Gestión de secretos en CI/CD: cómo transportar API keys y valores sensibles sin commitearlos. Variables de entorno, `.properties` ignorados, integración con sistemas de secretos (GitHub Secrets, etc.).

---

## Notas de arquitectura

- **Room en lugar de SQLDelight**: el stack de persistencia relacional usa Room (no SQLDelight). Cuando se creen las skills de base de datos, deben cubrir Room para KMM y su integración con la estrategia offline.
