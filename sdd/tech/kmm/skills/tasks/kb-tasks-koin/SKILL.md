---
name: kb-tasks-koin
description: Implementación concreta de Koin DI en proyectos KMM: DSL de registro (single/factory/viewModelOf), nativeModule expect/actual, initKoin completo con llamadas Android e iOS, y módulo de feature tipo. Úsalo cuando haya que implementar módulos Koin, registrar dependencias o configurar la inicialización de DI.
allowed-tools: [Read]
effort: low
user-invocable: false
---

# Koin DI KMM — Implementación

→ Organización arquitectónica de módulos y reglas de ownership: `kb-plan-koin`

## DSL de registro

→ Regla de oro de registro (`single`/`factory`/`viewModelOf`): `kb-plan-koin`

→ Templates: `${CLAUDE_SKILL_DIR}/references/koin_templates.md` — módulo de feature, nativeModule, initKoin, qualifiers, factory expect/actual

## nativeModule — expect/actual

`nativeModule` es un `expect val` en commonMain con `actual` en androidMain e iosMain. Se registra **primero** en `initKoin`.

→ Templates: `${CLAUDE_SKILL_DIR}/references/koin_templates.md`

## initKoin completo

Una única función `initKoin(config: KoinAppDeclaration? = null)` en commonMain. Android la llama en `Application.onCreate()` con `androidLogger` y `androidContext`; iOS la llama en `ComposeUIViewController(configure = { initKoin() })`.

→ Templates: `${CLAUDE_SKILL_DIR}/references/koin_templates.md`

## Qualifiers con enum

Cuando hay múltiples instancias del mismo tipo, se usan enums como qualifiers agrupados por dominio (`NetworkQualifiers`, `AuthQualifiers`).

→ Templates: `${CLAUDE_SKILL_DIR}/references/koin_templates.md`

## Módulo con factory function expect/actual

Para una única implementación por plataforma sin qualifier: `expect fun platformModule(): Module` con `actual` por plataforma.

→ Templates: `${CLAUDE_SKILL_DIR}/references/koin_templates.md`
