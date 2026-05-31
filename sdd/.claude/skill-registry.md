# SDD Skill Registry
<!-- Auto-generado por wf-sdd-status. No editar manualmente. -->
<!-- Total: 96 skills | 29 user-invocable (wf-*) | 67 kb-* -->
<!-- Última actualización: 2026-05-30 -->

## Meta-Ecosistema (.claude/)

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-sdd-audit-content | Criterios normativos para detectar problemas de calidad de contenido: SSoT, SRP, contradicciones, inconsistencias | false | .claude/skills/kb-sdd-audit-content/SKILL.md |
| kb-sdd-audit-structural | Criterios normativos para detectar problemas estructurales: referencias rotas, skills huérfanas, rootmap inválido | false | .claude/skills/kb-sdd-audit-structural/SKILL.md |
| kb-sdd-creation-guide | Guía operativa para crear y registrar skills, agentes y actualizar el ecosistema SDD | false | .claude/skills/kb-sdd-creation-guide/SKILL.md |
| kb-sdd-skill-architecture | Reglas transversales para decidir cuándo crear kb, workflow o agente; SSoT/SRP; tech targets | false | .claude/skills/kb-sdd-skill-architecture/SKILL.md |
| wf-agent-create | Orquestador para crear un nuevo agente; valida KBs, delega a sdd-author | true | .claude/skills/wf-agent-create/SKILL.md |
| wf-sdd-audit | Audita el ecosistema detectando referencias rotas, SSoT/SRP violations; modos structural/content/full | true | .claude/skills/wf-sdd-audit/SKILL.md |
| wf-sdd-refactor | Refactoriza una skill o agente existente; delega a sdd-author | true | .claude/skills/wf-sdd-refactor/SKILL.md |
| wf-sdd-status | Inventario del ecosistema y actualización de skill-registry.md; sin agente | true | .claude/skills/wf-sdd-status/SKILL.md |
| wf-skill-create | Orquestador para crear una nueva kb-* o wf-*; valida duplicados, delega a sdd-author | true | .claude/skills/wf-skill-create/SKILL.md |

## Fase: PRD

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-prd-expert | Base de conocimiento normativa del PRD: estructura válida, alcance, actores, fuera de alcance | false | prd/skills/kb-prd-expert/SKILL.md |
| kb-product-change-governance | Criterios de gobernanza de cambios: clasificación, control de alcance, trazabilidad entre PRD y derivados | false | prd/skills/kb-product-change-governance/SKILL.md |
| wf-prd-change | Formaliza un cambio de producto sobre un PRD existente; clasifica, actualiza, registra changelog | true | prd/skills/wf-prd-change/SKILL.md |
| wf-prd-create | Crea un PRD desde notas, brief o idea inicial; genera prd.md guiado | true | prd/skills/wf-prd-create/SKILL.md |
| wf-prd-review | Revisa si un PRD está limpio y bien planteado antes de entrar en Spec | true | prd/skills/wf-prd-review/SKILL.md |

## Fase: Spec

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-conflict-expert | Criterios para detectar y resolver conflictos entre specs de features | false | spec/skills/kb-conflict-expert/SKILL.md |
| kb-decompose-expert | Reglas para descomponer capacidades de PRD en features con HUs y shared models | false | spec/skills/kb-decompose-expert/SKILL.md |
| kb-gap-conventions | Convenciones SSoT para marcar, escalar y resolver gaps en specs | false | spec/skills/kb-gap-conventions/SKILL.md |
| kb-spec-expert | Base de conocimiento normativa del spec SDD: estructura, HUs, criterios de aceptación, pureza funcional | false | spec/skills/kb-spec-expert/SKILL.md |
| kb-traceability-rules | Reglas de trazabilidad RF→HU→Feature entre PRD, discovery, specs, plan y tasks | false | spec/skills/kb-traceability-rules/SKILL.md |
| wf-prd-sync-impact | Mide impacto de un cambio de PRD sobre artefactos Spec derivados | true | spec/skills/wf-prd-sync-impact/SKILL.md |
| wf-spec-analyze | Analiza un PRD para detectar gaps y decisiones de negocio antes de generar specs | true | spec/skills/wf-spec-analyze/SKILL.md |
| wf-spec-conflict | Detecta conflictos entre specs de features: HUs duplicadas, CAs contradictorios, overlaps | true | spec/skills/wf-spec-conflict/SKILL.md |
| wf-spec-delta | Actualiza un spec con requisitos nuevos; modos analyze y apply | true | spec/skills/wf-spec-delta/SKILL.md |
| wf-spec-discover | Identifica features de un PRD por cohesión funcional; genera _discovery.md | true | spec/skills/wf-spec-discover/SKILL.md |
| wf-spec-fast-track | Genera spec directo de una feature; una capacidad por run | true | spec/skills/wf-spec-fast-track/SKILL.md |
| wf-spec-features-first | Orquestador completo features-first: discover → fast-track en paralelo → conflict → readiness | true | spec/skills/wf-spec-features-first/SKILL.md |
| wf-spec-gap-resolve | Completa HUs incompletas usando respuestas de _analysis.md sin cambio de alcance | true | spec/skills/wf-spec-gap-resolve/SKILL.md |
| wf-spec-readiness | Evalúa qué features están listas, bloqueadas y el orden de implementación | true | spec/skills/wf-spec-readiness/SKILL.md |
| wf-spec-sync-from-prd | Resincroniza specs tras un cambio de PRD; modos analyze y apply | true | spec/skills/wf-spec-sync-from-prd/SKILL.md |
| wf-spec-validate | Valida un spec existente contra criterios de pureza, completitud y testabilidad | true | spec/skills/wf-spec-validate/SKILL.md |

## Fase: Design

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-a11y-expert | Criterios WCAG 2.2 mapeados a mobile: contraste, touch targets, focus order, screen reader | false | design/skills/kb-a11y-expert/SKILL.md |
| kb-design-brief | Contrato de DESIGN_BRIEF.md: modos guided/hybrid/auto, autonomy_policy, presets, validaciones | false | design/skills/kb-design-brief/SKILL.md |
| kb-design-conflict-expert | Detección de conflictos visuales entre features: componentes duplicados, navegación incoherente, tokens contradichos | false | design/skills/kb-design-conflict-expert/SKILL.md |
| kb-design-expert | Reglas de la fase design: separación DESIGN.md/artefactos por feature, trazabilidad, contrato para Stitch | false | design/skills/kb-design-expert/SKILL.md |
| kb-design-forms | Patrones de formulario: layout, validación, estados de campo, multistep, autosave, file upload | false | design/skills/kb-design-forms/SKILL.md |
| kb-design-iconography-expert | Sistema de iconografía: librería base, stroke/fill rule, grid, tamaños por rol, política de custom icons | false | design/skills/kb-design-iconography-expert/SKILL.md |
| kb-design-layout | Sistema de layout: spacing, breakpoints, grid, adaptive vs responsive, safe areas, foldables | false | design/skills/kb-design-layout/SKILL.md |
| kb-design-motion-expert | Catálogo de motion: roles, durations, easing curves, micro-interacciones, prefers-reduced-motion | false | design/skills/kb-design-motion-expert/SKILL.md |
| kb-design-style-decision-tree | Árbol de decisión navegable para elegir style_family y variables visuales por contexto de producto | false | design/skills/kb-design-style-decision-tree/SKILL.md |
| kb-design-style-taxonomy | Clasificación operativa de estilos visuales: familias, señales de selección, anti-patrones | false | design/skills/kb-design-style-taxonomy/SKILL.md |
| kb-design-voice | UX writing y voice & tone: ejes de voz, estructura de errores, microcopy, glosario, políticas | false | design/skills/kb-design-voice/SKILL.md |
| wf-design-a11y-audit | Auditoría ejecutiva de accesibilidad: contraste, touch targets, focus order; targets AA/AAA | true | design/skills/wf-design-a11y-audit/SKILL.md |
| wf-design-branch | Explora variante paralela del DESIGN.md sin comprometer main; create/list/compare/merge/discard | true | design/skills/wf-design-branch/SKILL.md |
| wf-design-delta | Evoluciona DESIGN.md incrementalmente; modos analyze y apply con versionado semver | true | design/skills/wf-design-delta/SKILL.md |
| wf-design-discover | Descubre apps de referencia con research validado por el usuario; genera _design_discovery.md | true | design/skills/wf-design-discover/SKILL.md |
| wf-design-export | Exporta tokens del DESIGN.md a CSS, Style Dictionary, Compose, SwiftUI o Tailwind | true | design/skills/wf-design-export/SKILL.md |
| wf-design-feature-prototype | Genera flows, views y ui_prompt para Stitch desde un feature spec | true | design/skills/wf-design-feature-prototype/SKILL.md |
| wf-design-feedback | Captura feedback no estructurado de stakeholders y lo triajea en categorías accionables | true | design/skills/wf-design-feedback/SKILL.md |
| wf-design-intake | Cierra DESIGN_BRIEF.md antes de generar el sistema visual; modos guided/hybrid/auto | true | design/skills/wf-design-intake/SKILL.md |
| wf-design-moodboard | Captura inspiración visual antes del intake; mood board de vibes, paletas, fotografía | true | design/skills/wf-design-moodboard/SKILL.md |
| wf-design-system | Crea o actualiza DESIGN.md desde Spec validado y DESIGN_BRIEF.md | true | design/skills/wf-design-system/SKILL.md |
| wf-design-validate | Audita DESIGN.md existente sin regenerarlo; reporta gaps o OK | true | design/skills/wf-design-validate/SKILL.md |
| wf-design-variant | A/B testing visual de una feature; crea variantes con hipótesis y métrica | true | design/skills/wf-design-variant/SKILL.md |

## Fase: Plan

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| wf-plan-validate | Valida si un _plan.md está listo para pasar a Tasks; certifica VALIDADO o devuelve hallazgos | true | plan/skills/wf-plan-validate/SKILL.md |
| wf-prepare-plan | Transforma Spec validado + handoff de Design en un _plan.md técnico KMM | true | plan/skills/wf-prepare-plan/SKILL.md |

## Fase: Tasks

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-tasks-expert | Base de conocimiento normativa de tasks SDD: formato, granularidad, orden, owner, definition of done | false | tasks/skills/kb-tasks-expert/SKILL.md |
| wf-prepare-tasks | Transforma _plan.md validado en tasks atómicas ordenadas y asignadas a agentes KMM | true | tasks/skills/wf-prepare-tasks/SKILL.md |

## Tech: KMM — Plan

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-cmp-resources | Compose Resources: sistema, carpetas, localización, qué módulos la necesitan (planificación) | false | tech/kmm/skills/plan/kb-cmp-resources/SKILL.md |
| kb-kmm-app-errors | Contrato transversal AppResult/AppError y ownership de taxonomías de error | false | tech/kmm/skills/plan/kb-kmm-app-errors/SKILL.md |
| kb-kmm-app-layer | Capa app: composition root, navegación, composición entre features, estado efímero | false | tech/kmm/skills/plan/kb-kmm-app-layer/SKILL.md |
| kb-kmm-auth-contracts | Contratos de autenticación: tokens, refresh, expiración, endpoints públicos, separación transporte | false | tech/kmm/skills/plan/kb-kmm-auth-contracts/SKILL.md |
| kb-kmm-brands | Brands: identidad de producto por marca, catálogo, valores base, assets, brand vs environment | false | tech/kmm/skills/plan/kb-kmm-brands/SKILL.md |
| kb-kmm-clean-architecture | Arquitectura por capas app/core/features: dependencias, composición, shared data | false | tech/kmm/skills/plan/kb-kmm-clean-architecture/SKILL.md |
| kb-kmm-core-layer | Capa core: dominio compartido, infraestructura transversal, escalación de responsabilidad | false | tech/kmm/skills/plan/kb-kmm-core-layer/SKILL.md |
| kb-kmm-environments | Semántica de entornos: matriz brand×env, valores declarativos vs derivados | false | tech/kmm/skills/plan/kb-kmm-environments/SKILL.md |
| kb-kmm-feature-clean-architecture | Arquitectura interna de feature: capas presentation/domain/data, contratos, reglas de dependencia | false | tech/kmm/skills/plan/kb-kmm-feature-clean-architecture/SKILL.md |
| kb-kmm-navigation-contracts | Contratos de navegación: ownership, routes como contrato central, encapsulación de NavController | false | tech/kmm/skills/plan/kb-kmm-navigation-contracts/SKILL.md |
| kb-kmm-navigation-platform-behaviors | Comportamientos de navegación de plataforma: BackHandler, predictive back, deep links | false | tech/kmm/skills/plan/kb-kmm-navigation-platform-behaviors/SKILL.md |
| kb-kmm-network-contracts | Contratos de networking: errores de red, resultados tipados, límites entre servicios y repos | false | tech/kmm/skills/plan/kb-kmm-network-contracts/SKILL.md |
| kb-kmm-testing-strategy | Estrategia de testing: pirámide, ownership por capa, TDD RED-GREEN-REFACTOR, fakes sobre mocks | false | tech/kmm/skills/plan/kb-kmm-testing-strategy/SKILL.md |
| kb-plan-cmp-ui | CMP presentation layer: estructura commonMain, expect/actual de UI, relación ViewModel (planificación) | false | tech/kmm/skills/plan/kb-plan-cmp-ui/SKILL.md |
| kb-plan-expert | Reglas del Plan técnico SDD KMM: cuándo Design es obligatorio, secciones, taxonomía de gaps | false | tech/kmm/skills/plan/kb-plan-expert/SKILL.md |
| kb-plan-kmm-datastore-preferences | Preferences DataStore como decisión arquitectónica: cuándo usarlo, ownership core/feature | false | tech/kmm/skills/plan/kb-plan-kmm-datastore-preferences/SKILL.md |
| kb-plan-kmm-navigation-viewmodel-events | Intent/Events: patrón arquitectónico ViewModel↔Composable, Channel vs StateFlow | false | tech/kmm/skills/plan/kb-plan-kmm-navigation-viewmodel-events/SKILL.md |
| kb-plan-kmm-ui-text | UIText: desacoplamiento ViewModel-UI para texto translatable/dinámico (planificación) | false | tech/kmm/skills/plan/kb-plan-kmm-ui-text/SKILL.md |
| kb-plan-koin | Koin DI: organización de módulos, tipos de registro, qualifier pattern, nativeModule | false | tech/kmm/skills/plan/kb-plan-koin/SKILL.md |

## Tech: KMM — Tasks

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-kmm-android-environments | Implementación Android multi-brand/multi-environment: product flavors, BuildConfig, resolución | false | tech/kmm/skills/tasks/kb-kmm-android-environments/SKILL.md |
| kb-kmm-auth-ktor-plugin | Auth automática con plugins Ktor: dos clientes HTTP, auth plugin, bypass público, refresh transparente | false | tech/kmm/skills/tasks/kb-kmm-auth-ktor-plugin/SKILL.md |
| kb-kmm-auth-oauth-keycloak | OAuth Keycloak: endpoints de token, grant types, form-urlencoded, configuración de env | false | tech/kmm/skills/tasks/kb-kmm-auth-oauth-keycloak/SKILL.md |
| kb-kmm-http-ktor | HTTP con Ktor: HttpClient config, plugins, serialización JSON, logging, timeouts | false | tech/kmm/skills/tasks/kb-kmm-http-ktor/SKILL.md |
| kb-kmm-ios-environments | Implementación iOS multi-brand/multi-environment: XCConfig, targets, build configurations | false | tech/kmm/skills/tasks/kb-kmm-ios-environments/SKILL.md |
| kb-kmm-navigation-compose | Compose Navigation: @Serializable routes, NavHost, back stack, deep links | false | tech/kmm/skills/tasks/kb-kmm-navigation-compose/SKILL.md |
| kb-kmm-resources | Compose Resources: strings, imágenes, fonts, raw files, localización (implementación) | false | tech/kmm/skills/tasks/kb-kmm-resources/SKILL.md |
| kb-tasks-cmp-ui | CMP presentation layer: entry points Android/iOS, initKoin, lifecycle, @Preview (implementación) | false | tech/kmm/skills/tasks/kb-tasks-cmp-ui/SKILL.md |
| kb-tasks-kmm-datastore-preferences | DataStore Preferences: factory compartida, path por plataforma, keys, storage adapters | false | tech/kmm/skills/tasks/kb-tasks-kmm-datastore-preferences/SKILL.md |
| kb-tasks-kmm-integration-testing | Tests de integración: Compose semantic tree, a11y testing, screenshot regression con Roborazzi | false | tech/kmm/skills/tasks/kb-tasks-kmm-integration-testing/SKILL.md |
| kb-tasks-kmm-navigation-viewmodel-events | Intent/Events implementación: Channel, LaunchedEffect, sealed interfaces, coordinación | false | tech/kmm/skills/tasks/kb-tasks-kmm-navigation-viewmodel-events/SKILL.md |
| kb-tasks-kmm-ui-text | UIText implementación: sealed interface, estado, ViewModel, testing | false | tech/kmm/skills/tasks/kb-tasks-kmm-ui-text/SKILL.md |
| kb-tasks-kmm-unit-testing | Unit tests: ViewModel con Turbine, UseCase con fakes, Repository con fakes | false | tech/kmm/skills/tasks/kb-tasks-kmm-unit-testing/SKILL.md |
| kb-tasks-koin | Koin DI implementación: DSL, nativeModule expect/actual, initKoin completo, módulos de feature | false | tech/kmm/skills/tasks/kb-tasks-koin/SKILL.md |

## Tech: KMM — Workflows

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| wf-kmm-auth-setup-keycloak | Configura autenticación OAuth con Keycloak en KMM: contratos, provider, integración HTTP | true | tech/kmm/skills/wf-kmm-auth-setup-keycloak/SKILL.md |
| wf-kmm-datastore-setup | Configura Preferences DataStore en KMM: arquitectura, DI, providers de plataforma | true | tech/kmm/skills/wf-kmm-datastore-setup/SKILL.md |
| wf-kmm-environments | Configura multi-brand/multi-environment en KMM: implementaciones Android e iOS | true | tech/kmm/skills/wf-kmm-environments/SKILL.md |
| wf-kmm-network-setup | Configura networking en KMM: arquitectura, DI, implementación HTTP, sin auth | true | tech/kmm/skills/wf-kmm-network-setup/SKILL.md |
| wf-kmm-stack-setup-ktor-keycloak-koin | Atajo para stack KMM típico: Koin + Ktor + OAuth Keycloak | true | tech/kmm/skills/wf-kmm-stack-setup-ktor-keycloak-koin/SKILL.md |
| wf-kmm-testing-setup | Configura infraestructura de testing en KMM: Gradle deps, source sets, estructura de directorios | true | tech/kmm/skills/wf-kmm-testing-setup/SKILL.md |
