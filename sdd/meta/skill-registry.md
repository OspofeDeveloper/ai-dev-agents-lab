# SDD Skill Registry
<!-- Auto-generado por scripts/generate-skill-registry.py. No editar manualmente. -->
<!-- Total: 124 skills | 55 wf-* (user-invocable) | 69 kb-* -->
<!-- Última actualización: 2026-06-10 -->

## Meta-Ecosistema (meta/)

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-sdd-audit-content | Criterios normativos para detectar problemas de calidad de contenido en skills y agentes del ecosistema SDD: violaciones de SSoT (regla duplicada en dos sitios… | false | meta/skills/kb-sdd-audit-content/SKILL.md |
| kb-sdd-audit-structural | Criterios normativos para detectar problemas estructurales en el ecosistema SDD: referencias rotas, skills huerfanas, entradas de rootmap invalidas y agentes c… | false | meta/skills/kb-sdd-audit-structural/SKILL.md |
| kb-sdd-creation-guide | Guia operativa para crear y registrar skills (kb-* y wf-*), agentes y actualizar el ecosistema SDD | false | meta/skills/kb-sdd-creation-guide/SKILL.md |
| kb-sdd-skill-architecture | Reglas transversales para decidir cuando crear una kb, workflow o agente dentro de sdd, y como repartir responsabilidades entre CLAUDE.md, README y skills sin… | false | meta/skills/kb-sdd-skill-architecture/SKILL.md |
| kb-sdd-stack-overlay-contract | Contrato normativo que debe cumplir un overlay de stack (tech/<stack>) para integrarse en el ecosistema SDD: piezas obligatorias y opcionales, mecanismo de ove… | false | meta/skills/kb-sdd-stack-overlay-contract/SKILL.md |
| wf-agent-create | Orquestador SDD para crear un nuevo agente dentro del ecosistema | true | meta/skills/wf-agent-create/SKILL.md |
| wf-project-init | Onboarding para inicializar un proyecto SDD | true | bootstrap/skills/wf-project-init/SKILL.md |
| wf-sdd-audit | Audita el ecosistema SDD detectando referencias rotas, skills huerfanas, violaciones de SSoT/SRP, contradicciones e inconsistencias | true | meta/skills/wf-sdd-audit/SKILL.md |
| wf-sdd-refactor | Orquestador SDD para refactorizar una skill (kb-* o wf-*) o agente existente del ecosistema | true | meta/skills/wf-sdd-refactor/SKILL.md |
| wf-sdd-status | Genera un inventario rapido del ecosistema SDD y actualiza sdd/meta/skill-registry.md: cuantas skills y agentes hay por fase, que KBs existen, que workflows es… | true | meta/skills/wf-sdd-status/SKILL.md |
| wf-sdd-update | Actualiza la instalación SDD de un proyecto a la versión actual del ecosistema, sin re-entrevistar: relee fases y stack de project-init.json, reinstala con --p… | true | bootstrap/skills/wf-sdd-update/SKILL.md |
| wf-skill-create | Orquestador SDD para crear una nueva skill (kb-* o wf-*) en el ecosistema | true | meta/skills/wf-skill-create/SKILL.md |
| wf-stack-create | Orquestador SDD para crear el esqueleto de un nuevo overlay de stack (tech/<stack>) conforme a kb-sdd-stack-overlay-contract: estructura de directorios, instal… | true | meta/skills/wf-stack-create/SKILL.md |

## Fase: PRD

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-prd-expert | Experto en Product Requirements Documents (PRD) para el pipeline SDD | false | prd/skills/kb-prd-expert/SKILL.md |
| kb-product-change-governance | Reglas de gobernanza para cambios de producto en el ecosistema SDD | false | prd/skills/kb-product-change-governance/SKILL.md |
| wf-prd-change | Gestiona cambios de producto sobre un PRD existente | true | prd/skills/wf-prd-change/SKILL.md |
| wf-prd-change-cascade | Orquestador del cascade de cambio de producto: tras un cambio de PRD encadena en un solo comando la secuencia que hoy se ejecuta a mano (change → sync-impact →… | true | prd/skills/wf-prd-change-cascade/SKILL.md |
| wf-prd-create | Crea un PRD inicial guiado para el pipeline SDD | true | prd/skills/wf-prd-create/SKILL.md |
| wf-prd-review | Revision rapida de un PRD o documento de requisitos antes de entrar en la fase Spec | true | prd/skills/wf-prd-review/SKILL.md |

## Fase: Spec

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-conflict-expert | Experto en detección de conflictos entre Specs SDD de features | false | spec/skills/kb-conflict-expert/SKILL.md |
| kb-decompose-expert | Experto en partición de Specs SDD monolíticos en Specs por feature | false | spec/skills/kb-decompose-expert/SKILL.md |
| kb-gap-conventions | Convenciones SSoT para el sistema de gaps y marcadores del pipeline SDD | false | spec/skills/kb-gap-conventions/SKILL.md |
| kb-spec-characterization | Reglas para specs de caracterización brownfield: evidencia obligatoria por CA, marcador [INFERIDO], qué no especular y degradación sin tests | false | spec/skills/kb-spec-characterization/SKILL.md |
| kb-spec-expert | Experto en Spec Driven Development (SDD): qué debe y qué NO debe contener un Spec | false | spec/skills/kb-spec-expert/SKILL.md |
| kb-traceability-rules | Reglas de trazabilidad entre PRD, discovery, specs, plan y tasks en el ecosistema SDD | false | spec/skills/kb-traceability-rules/SKILL.md |
| wf-prd-sync-impact | Analiza el impacto de un PRD actualizado sobre los artefactos SDD ya generados | true | spec/skills/wf-prd-sync-impact/SKILL.md |
| wf-spec-amend | Enmienda quirúrgica de un CA ambiguo descubierto durante la implementación (back-edge tasks→spec) | true | spec/skills/wf-spec-amend/SKILL.md |
| wf-spec-analyze | Recopila las decisiones de negocio que necesitaran los Specs a partir de un PRD vigente | true | spec/skills/wf-spec-analyze/SKILL.md |
| wf-spec-conflict | Detecta conflictos entre Specs SDD de un mismo proyecto: HUs duplicadas, CAs contradictorios, scope overlap, shared models inconsistentes | true | spec/skills/wf-spec-conflict/SKILL.md |
| wf-spec-delta | Evoluciona un Spec de feature existente de forma incremental | true | spec/skills/wf-spec-delta/SKILL.md |
| wf-spec-discover | Analiza un PRD e identifica features candidatas por cohesion funcional | true | spec/skills/wf-spec-discover/SKILL.md |
| wf-spec-fast-track | Genera el Spec de una feature directamente desde un documento de requisitos acotado a una sola capacidad | true | spec/skills/wf-spec-fast-track/SKILL.md |
| wf-spec-features-first | Orquestador completo del flujo features-first | true | spec/skills/wf-spec-features-first/SKILL.md |
| wf-spec-from-code | Ingeniería inversa de specs desde código existente (brownfield): descubre capacidades con evidencia (archivo:línea, rutas, tests) y genera specs de caracteriza… | true | spec/skills/wf-spec-from-code/SKILL.md |
| wf-spec-gap-resolve | Completa HUs y CAs marcadas como [INCOMPLETO] a partir de respuestas ya escritas en un _analysis.md, y confirma CAs [INFERIDO] de specs de caracterización con… | true | spec/skills/wf-spec-gap-resolve/SKILL.md |
| wf-spec-readiness | Analiza los artefactos post-spec-generation (specs de feature, READMEs, _features.md, _conflict_report.md) y genera un informe de readiness que indica que feat… | true | spec/skills/wf-spec-readiness/SKILL.md |
| wf-spec-sync-from-prd | Resincroniza specs de feature a partir de un PRD actualizado | true | spec/skills/wf-spec-sync-from-prd/SKILL.md |
| wf-spec-validate | Audita un _spec.md ya generado para detectar regresiones de pureza, testabilidad o completitud introducidas por ediciones manuales | true | spec/skills/wf-spec-validate/SKILL.md |

## Fase: Design

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-a11y-expert | Base de conocimiento de accesibilidad mobile | false | design/skills/kb-a11y-expert/SKILL.md |
| kb-design-brief | Base de conocimiento para capturar decisiones de direccion visual antes de generar un DESIGN.md | false | design/skills/kb-design-brief/SKILL.md |
| kb-design-characterization | Reglas para extraer un DESIGN.md desde una UI ya en produccion (CSS/tokens/componentes/capturas): evidencia obligatoria por token/decision visual, jerarquia de… | false | design/skills/kb-design-characterization/SKILL.md |
| kb-design-conflict-expert | Base de conocimiento para detectar conflictos visuales y de UX entre varias features dentro de un mismo producto | false | design/skills/kb-design-conflict-expert/SKILL.md |
| kb-design-expert | Skill raiz de la fase design del pipeline SDD | false | design/skills/kb-design-expert/SKILL.md |
| kb-design-feature-artifacts | Contrato normativo de los artefactos de feature en la fase design — flows (secuencias, navegacion y transiciones), views (SSoT de pantallas con todos los estad… | false | design/skills/kb-design-feature-artifacts/SKILL.md |
| kb-design-forms | Base de conocimiento para patrones de formulario en mobile y web | false | design/skills/kb-design-forms/SKILL.md |
| kb-design-governance | Gobernanza del sistema visual del producto a lo largo del tiempo | false | design/skills/kb-design-governance/SKILL.md |
| kb-design-iconography-expert | Base de conocimiento para el sistema de iconografia del producto | false | design/skills/kb-design-iconography-expert/SKILL.md |
| kb-design-layout | Base de conocimiento para sistemas de layout y responsive | false | design/skills/kb-design-layout/SKILL.md |
| kb-design-motion-expert | Base de conocimiento operativa para motion y micro-interacciones en mobile | false | design/skills/kb-design-motion-expert/SKILL.md |
| kb-design-style-decision-tree | Arbol de decision navegable para elegir style_family y variables visuales clave segun el contexto del producto | false | design/skills/kb-design-style-decision-tree/SKILL.md |
| kb-design-style-taxonomy | Base de conocimiento para clasificar estilos visuales de producto digital de forma operativa | false | design/skills/kb-design-style-taxonomy/SKILL.md |
| kb-design-system-contract | Contrato normativo del DESIGN.md como artefacto de producto del pipeline SDD | false | design/skills/kb-design-system-contract/SKILL.md |
| kb-design-voice | Base de conocimiento para UX writing y voice & tone del producto | false | design/skills/kb-design-voice/SKILL.md |
| wf-design-a11y-audit | Audita un DESIGN.md y opcionalmente un *_views.md frente a las reglas de kb-a11y-expert | true | design/skills/wf-design-a11y-audit/SKILL.md |
| wf-design-branch | Permite explorar variantes paralelas del sistema visual sin comprometerse | true | design/skills/wf-design-branch/SKILL.md |
| wf-design-delta | Evoluciona un DESIGN.md existente de forma incremental | true | design/skills/wf-design-delta/SKILL.md |
| wf-design-discover | Descubre 3-5 apps reales del mercado como referencias de diseno para una feature, mediante research web y validacion interactiva con el usuario | true | design/skills/wf-design-discover/SKILL.md |
| wf-design-export | Exporta los tokens del DESIGN.md a formatos consumibles por equipos de desarrollo: CSS variables, Style Dictionary universal, Compose para Android, SwiftUI par… | true | design/skills/wf-design-export/SKILL.md |
| wf-design-extract | Ingenieria inversa de un DESIGN.md desde una UI ya en produccion (CSS/tokens/componentes/capturas): descubre tokens, paleta, tipografia y componentes con evide… | true | design/skills/wf-design-extract/SKILL.md |
| wf-design-feature-prototype | Deriva artefactos de prototipado visual de una feature a partir de su _spec.md, un DESIGN.md y, si existe, un DESIGN_BRIEF.md | true | design/skills/wf-design-feature-prototype/SKILL.md |
| wf-design-feedback | Captura feedback no estructurado de stakeholders (cliente, PM, dev, QA) y lo triajea en categorias accionables: cambio de brief, delta visual, ajuste de featur… | true | design/skills/wf-design-feedback/SKILL.md |
| wf-design-intake | Cierra un DESIGN_BRIEF.md antes de generar el sistema visual | true | design/skills/wf-design-intake/SKILL.md |
| wf-design-moodboard | Captura inspiracion visual no estructurada antes del discovery | true | design/skills/wf-design-moodboard/SKILL.md |
| wf-design-sync | Analiza el impacto de un cambio en el sistema visual o en los specs sobre los artefactos de diseño ya derivados | true | design/skills/wf-design-sync/SKILL.md |
| wf-design-system | Crea o actualiza el DESIGN.md de un producto a partir de un feature spec validado y un DESIGN_BRIEF.md cerrado | true | design/skills/wf-design-system/SKILL.md |
| wf-design-validate | Audita un DESIGN.md ya existente contra el contrato visual (kb-design-expert, kb-design-style-taxonomy, kb-design-brief) y el linter oficial de Google design.md | true | design/skills/wf-design-validate/SKILL.md |
| wf-design-variant | Permite el A/B testing visual de una feature | true | design/skills/wf-design-variant/SKILL.md |

## Fase: Plan

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-plan-expert | Base de conocimiento del Plan técnico SDD | false | plan/skills/kb-plan-expert/SKILL.md |
| kb-plan-method | Procedimiento operativo compartido de la fase plan SDD — los pasos de generar un Plan (plan-architect) y de auditarlo (plan-auditor), stack-agnósticos | false | plan/skills/kb-plan-method/SKILL.md |
| wf-plan-validate | Audita un _plan.md existente contra su Spec, el handoff de Design y las reglas de kb-plan-expert | true | plan/skills/wf-plan-validate/SKILL.md |
| wf-prepare-plan | Transforma Specs validados y el handoff de Design en Planes tecnicos | true | plan/skills/wf-prepare-plan/SKILL.md |

## Fase: Tasks

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-delivery-discipline | Criterios stack-agnósticos de empaquetado del trabajo implementado en commits y PRs: la Task como unidad de trabajo (un commit atómico y verde por task), los t… | false | tasks/skills/kb-delivery-discipline/SKILL.md |
| kb-qa-expert | Metodologia QA del pipeline SDD: derivacion de casos de prueba TC-XXX desde los CAs GIVEN/WHEN/THEN del spec, niveles y tipos de prueba, trazabilidad CA→TC y c… | false | tasks/skills/kb-qa-expert/SKILL.md |
| kb-tasks-expert | Reglas tech-neutral para descomponer Planes técnicos en Tasks atómicas delegables a un owner claro: formato obligatorio de task, granularidad, orden canónico p… | false | tasks/skills/kb-tasks-expert/SKILL.md |
| kb-tasks-method | Procedimiento operativo compartido de la fase tasks SDD — los pasos de descomponer un Plan validado en un _tasks.md, stack-agnósticos | false | tasks/skills/kb-tasks-method/SKILL.md |
| wf-bug | Fast-lane de mantenimiento: triaje de un bug contra los specs de la feature, fix con trazabilidad (B-00X, CA-XXX) y registro en <feature>_bugs.md | true | tasks/skills/wf-bug/SKILL.md |
| wf-prepare-tasks | Transforma Planes tecnicos validados en Tasks de implementacion | true | tasks/skills/wf-prepare-tasks/SKILL.md |
| wf-project-status | Informe PM read-only del estado del proyecto SDD: por cada feature, en qué fase del pipeline está (Spec/Plan/Tasks/QA/Cerrada), su estado, el bloqueo y la sigu… | true | tasks/skills/wf-project-status/SKILL.md |
| wf-qa-plan | Genera el plan de QA de una feature: deriva casos de prueba TC-XXX trazables desde los CAs GIVEN/WHEN/THEN del feature spec (afinados con plan/tasks y project… | true | tasks/skills/wf-qa-plan/SKILL.md |
| wf-qa-verify | Verifica la cobertura real de CAs de una feature tras implementar: localiza y ejecuta los tests que ejercitan cada TC del qa_plan, registra evidencia, escribe… | true | tasks/skills/wf-qa-verify/SKILL.md |
| wf-release | Vincula el cierre de una feature (QA APTO) a un punto verificable de producción: registra el commit SHA y, opcionalmente, un tag de release | true | tasks/skills/wf-release/SKILL.md |
| wf-task-run | Ejecuta las tasks de un _tasks.md con estado persistente, validación de DoD y commits trazables (T-00X, CA-XXX) | true | tasks/skills/wf-task-run/SKILL.md |

## Tech: KMM — Global

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-kmm-project-state-protocol | Protocolo de precondicion de contexto tecnico para agentes KMM | false | tech/kmm/skills/kb-kmm-project-state-protocol/SKILL.md |
| wf-kmm-auth-setup-keycloak | Configura autenticación OAuth con Keycloak en un proyecto KMM separando contratos de sesión, proveedor OAuth y mecanismo técnico de integración con el cliente… | true | tech/kmm/skills/wf-kmm-auth-setup-keycloak/SKILL.md |
| wf-kmm-datastore-setup | Configura Preferences DataStore en un proyecto KMM componiendo arquitectura por capas, wiring de DI y providers por plataforma sin mezclar storage local con au… | true | tech/kmm/skills/wf-kmm-datastore-setup/SKILL.md |
| wf-kmm-environments | Configura un sistema multi-brand/multi-environment en un proyecto KMM componiendo semántica estable de variantes y sus implementaciones Android e iOS | true | tech/kmm/skills/wf-kmm-environments/SKILL.md |
| wf-kmm-init | Init especialista del stack KMM | true | tech/kmm/skills/wf-kmm-init/SKILL.md |
| wf-kmm-network-setup | Configura la capa de networking en un proyecto KMM componiendo reglas de arquitectura, DI y la implementación HTTP elegida sin acoplar la skill a una única est… | true | tech/kmm/skills/wf-kmm-network-setup/SKILL.md |
| wf-kmm-stack-setup-ktor-keycloak-koin | Atajo para configurar el stack KMM más habitual basado en Koin, Ktor y OAuth con Keycloak, componiendo skills separadas sin convertirlas en una única fuente me… | true | tech/kmm/skills/wf-kmm-stack-setup-ktor-keycloak-koin/SKILL.md |
| wf-kmm-testing-setup | Configura la infraestructura de testing en un proyecto KMM: dependencias Gradle por tipo de test (unit, integration, screenshot), source sets commonTest/androi… | true | tech/kmm/skills/wf-kmm-testing-setup/SKILL.md |

## Tech: KMM — Plan

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-cmp-resources | Base de conocimiento de recursos compartidos en Compose Multiplatform con compose-resources (Res.*): qué es el sistema, estructura de carpetas, semántica de lo… | false | tech/kmm/skills/plan/kb-cmp-resources/SKILL.md |
| kb-kmm-app-errors | Base de conocimiento del contrato transversal de errores y resultados en proyectos KMM: AppResult, AppError, ownership de taxonomías de error y reglas de adapt… | false | tech/kmm/skills/plan/kb-kmm-app-errors/SKILL.md |
| kb-kmm-app-layer | Base de conocimiento de la capa app en proyectos KMM: composition root, navegación, composición entre features, coordinación de estado efímero de pantalla y de… | false | tech/kmm/skills/plan/kb-kmm-app-layer/SKILL.md |
| kb-kmm-auth-contracts | Base de conocimiento de contratos de autenticación en proyectos KMM: tokens, refresh, expiración de sesión, endpoints públicos y separación entre política de a… | false | tech/kmm/skills/plan/kb-kmm-auth-contracts/SKILL.md |
| kb-kmm-brands | Base de conocimiento de brands en proyectos KMM: identidad de producto por marca, catálogo de brands, valores base por marca, assets/naming/bundle id base y se… | false | tech/kmm/skills/plan/kb-kmm-brands/SKILL.md |
| kb-kmm-clean-architecture | Base de conocimiento de la arquitectura por capas en proyectos KMM: roles de app/core/features, dependencias permitidas, composición, navegación, agregación en… | false | tech/kmm/skills/plan/kb-kmm-clean-architecture/SKILL.md |
| kb-kmm-core-layer | Base de conocimiento de la capa core en proyectos KMM: dominio compartido, infraestructura transversal, criterios para subir responsabilidades desde features y… | false | tech/kmm/skills/plan/kb-kmm-core-layer/SKILL.md |
| kb-kmm-environments | Base de conocimiento de entornos y variantes en proyectos KMM: semántica estable de env, composición de la matriz brand×env, valores derivados vs declarativos,… | false | tech/kmm/skills/plan/kb-kmm-environments/SKILL.md |
| kb-kmm-feature-clean-architecture | Base de conocimiento de la arquitectura interna de una feature KMM: capas presentation/domain/data, ubicación de contratos e implementaciones, dependencias per… | false | tech/kmm/skills/plan/kb-kmm-feature-clean-architecture/SKILL.md |
| kb-kmm-navigation-contracts | Base de conocimiento de contratos de navegación en proyectos KMM: ownership entre app y features, rutas como contrato central, encapsulación del NavController… | false | tech/kmm/skills/plan/kb-kmm-navigation-contracts/SKILL.md |
| kb-kmm-navigation-platform-behaviors | Reglas para integración de navegación con comportamientos de plataforma en KMM, como BackHandler, predictive back y bridges de deep links | false | tech/kmm/skills/plan/kb-kmm-navigation-platform-behaviors/SKILL.md |
| kb-kmm-network-contracts | Base de conocimiento de contratos de networking en proyectos KMM: errores de red, resultados tipados, límites entre servicios remotos y repositorios, y reglas… | false | tech/kmm/skills/plan/kb-kmm-network-contracts/SKILL.md |
| kb-kmm-testing-strategy | Estrategia de testing para proyectos KMM: pirámide de tests, propiedad por capa, ciclo TDD RED-GREEN-REFACTOR, asignación a source sets y política de test doub… | false | tech/kmm/skills/plan/kb-kmm-testing-strategy/SKILL.md |
| kb-plan-cmp-ui | Base de conocimiento de la capa presentation en proyectos Compose Multiplatform (CMP): estructura del módulo UI compartida en commonMain, cuándo usar expect/ac… | false | tech/kmm/skills/plan/kb-plan-cmp-ui/SKILL.md |
| kb-plan-expert | Base de conocimiento del Plan técnico SDD para proyectos KMM | false | tech/kmm/skills/plan/kb-plan-expert/SKILL.md |
| kb-plan-kmm-datastore-preferences | Preferences DataStore en KMM como decisión arquitectónica: cuándo usarlo, qué módulos se ven afectados, ownership core vs feature, separación storage/networkin… | false | tech/kmm/skills/plan/kb-plan-kmm-datastore-preferences/SKILL.md |
| kb-plan-kmm-navigation-viewmodel-events | Base de conocimiento de eventos y efectos de navegación desde ViewModel en proyectos KMM: patrón Intent/Events, Channel vs StateFlow, reglas de LaunchedEffect… | false | tech/kmm/skills/plan/kb-plan-kmm-navigation-viewmodel-events/SKILL.md |
| kb-plan-kmm-ui-text | Patrón UIText en Compose Multiplatform como decisión arquitectónica: cuándo usarlo, qué problema resuelve, separación ViewModel-UI para texto traducible y diná… | false | tech/kmm/skills/plan/kb-plan-kmm-ui-text/SKILL.md |
| kb-plan-koin | Base de conocimiento de Koin DI en proyectos KMM: organización de módulos por feature, tipos de registro, patrón qualifier con enums, nativeModule expect/actua… | false | tech/kmm/skills/plan/kb-plan-koin/SKILL.md |

## Tech: KMM — Tasks

| Skill | Descripción | Invocable | Path |
|---|---|---|---|
| kb-kmm-android-environments | Base de conocimiento de implementación Android del sistema multi-brand/multi-environment en KMM: product flavors, plugin BuildConfig (gmazzo), resolución brand… | false | tech/kmm/skills/tasks/kb-kmm-android-environments/SKILL.md |
| kb-kmm-auth-ktor-plugin | Base de conocimiento de autenticación automática implementada con plugins de Ktor en proyectos KMM: dos clientes HTTP, plugin de auth, bypass para endpoints pú… | false | tech/kmm/skills/tasks/kb-kmm-auth-ktor-plugin/SKILL.md |
| kb-kmm-auth-oauth-keycloak | Base de conocimiento de OAuth con Keycloak en proyectos KMM: endpoints de token, parámetros requeridos, grant types, payloads form-urlencoded y configuración p… | false | tech/kmm/skills/tasks/kb-kmm-auth-oauth-keycloak/SKILL.md |
| kb-kmm-http-ktor | Base de conocimiento de implementación HTTP con Ktor en proyectos KMM: configuración de HttpClient, plugins, serialización JSON, logging, timeouts, rutas relat… | false | tech/kmm/skills/tasks/kb-kmm-http-ktor/SKILL.md |
| kb-kmm-ios-environments | Base de conocimiento de implementación iOS del sistema multi-brand/multi-environment en KMM: XCConfig, target/build configuration/scheme, flujo XCConfig → Scri… | false | tech/kmm/skills/tasks/kb-kmm-ios-environments/SKILL.md |
| kb-kmm-navigation-compose | Base de conocimiento de implementación de navegación con Compose Navigation + Kotlin Serialization en KMM: rutas @Serializable, NavHost, nested graphs, back st… | false | tech/kmm/skills/tasks/kb-kmm-navigation-compose/SKILL.md |
| kb-kmm-resources | Base de conocimiento sobre recursos compartidos en Compose Multiplatform: strings, imágenes, fonts, raw files y localización con compose.resources | false | tech/kmm/skills/tasks/kb-kmm-resources/SKILL.md |
| kb-tasks-cmp-ui | Implementación concreta de la capa presentation en proyectos Compose Multiplatform (CMP): entry points Android e iOS, setup de initKoin en iOS, ciclo de vida e… | false | tech/kmm/skills/tasks/kb-tasks-cmp-ui/SKILL.md |
| kb-tasks-expert | Reglas para descomponer Planes técnicos KMM en Tasks atómicas delegables a agentes KMM especializados: formato obligatorio de task, granularidad, orden canónic… | false | tech/kmm/skills/tasks/kb-tasks-expert/SKILL.md |
| kb-tasks-kmm-datastore-preferences | Base de conocimiento para usar Preferences DataStore en proyectos KMM: factory compartida, resolución de path por plataforma, ownership de keys y adapters sobr… | false | tech/kmm/skills/tasks/kb-tasks-kmm-datastore-preferences/SKILL.md |
| kb-tasks-kmm-integration-testing | Patrones de implementación de tests de integración en proyectos KMM con CMP: tests de árbol semántico Compose con composeTestRule, tests de accesibilidad con u… | false | tech/kmm/skills/tasks/kb-tasks-kmm-integration-testing/SKILL.md |
| kb-tasks-kmm-navigation-viewmodel-events | Implementación concreta del patrón Intent/Events en proyectos KMM: Channel para efectos one-shot, LaunchedEffect(viewModel), naming de sealed interfaces y coor… | false | tech/kmm/skills/tasks/kb-tasks-kmm-navigation-viewmodel-events/SKILL.md |
| kb-tasks-kmm-ui-text | Base de conocimiento sobre el patrón UiText en Compose Multiplatform: `UIText` desacopla ViewModel y UI para manejar textos traducibles y dinámicos | false | tech/kmm/skills/tasks/kb-tasks-kmm-ui-text/SKILL.md |
| kb-tasks-kmm-unit-testing | Patrones de implementación de tests unitarios en proyectos KMM: tests de ViewModel con runTest + Turbine, tests de UseCase con fakes, tests de RepositoryImpl c… | false | tech/kmm/skills/tasks/kb-tasks-kmm-unit-testing/SKILL.md |
| kb-tasks-koin | Implementación concreta de Koin DI en proyectos KMM: DSL de registro (single/factory/viewModelOf), nativeModule expect/actual, initKoin completo con llamadas A… | false | tech/kmm/skills/tasks/kb-tasks-koin/SKILL.md |
