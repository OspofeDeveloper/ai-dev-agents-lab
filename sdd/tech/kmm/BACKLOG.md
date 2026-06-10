# Backlog de skills KMM — Pendientes Fase 2

Skills identificadas como necesarias para uso profesional completo.

> **ROADMAP 6.4 (2026-06-10): backlog cerrado.** Las tres skills pendientes y la nota de Room se implementaron en el slice 6.4 (Par Room plan+tasks + `wf-kmm-database-setup`). No quedan pendientes en este backlog.

---

## Skills pendientes

_(ninguna — backlog vacío)_

---

## Completadas

### 1. `kb-kmm-gradle-modules` (planning) — ✅ 6.4 (2026-06-10)
Estructura de módulos Gradle: convenciones de nombrado, qué pertenece a `:core:*`, `:feature:*`, `:app`, convention plugins, `build.gradle.kts` compartido. Permite al plan traducir capas lógicas a módulos físicos.

### 2. `kb-kmm-offline-strategy` (planning) — ✅ 6.4 (2026-06-10)
Estrategia de caché y offline-first: cuándo implementar caché, single source of truth desde base de datos, stale-while-revalidate, flujo de datos en ausencia de conectividad. Depende de la skill de Room.

### 3. `kb-kmm-secrets-cicd` (planning) — ✅ 6.4 (2026-06-10)
Gestión de secretos en CI/CD: cómo transportar API keys y valores sensibles sin commitearlos. Variables de entorno, `.properties` ignorados, integración con sistemas de secretos (GitHub Secrets, etc.).

---

## Notas de arquitectura

- **Room en lugar de SQLDelight**: el stack de persistencia relacional usa Room (no SQLDelight). ✅ Cubierto en 6.4 con `kb-plan-kmm-room` + `kb-tasks-kmm-room` (Room 2.7+ con soporte KMP) y su integración con la estrategia offline (`kb-kmm-offline-strategy`). El workflow de setup es `wf-kmm-database-setup`.
