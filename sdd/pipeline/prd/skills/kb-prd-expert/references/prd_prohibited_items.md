# Elementos Prohibidos en un PRD

Estos elementos contaminan el PRD y rompen el flujo SDD. Cada uno pertenece a una capa posterior del pipeline.

> **Relación con `kb-spec-expert/references/prohibited_items.md`:** Este catálogo es **estricto-superset** del catálogo del Spec. Todo lo prohibido en el Spec también lo está en el PRD, y además el PRD prohíbe elementos que el Spec sí admite (pantallas como unidades, flujos de navegación con nombres de pantallas, timelines, estructura de módulos, criterios técnicos de QA). Si una frase sería inválida en el Spec, automáticamente lo es en el PRD.

## Tabla de prohibidos

| Elemento prohibido | Por qué está prohibido | Dónde pertenece |
|---|---|---|
| Stack tecnológico (KMM, Flutter, React Native, Swift) | El PRD debe ser agnóstico a la tecnología de implementación | Plan |
| Frameworks o librerías (Firebase, Ktor, Retrofit, Compose) | Decisiones de arquitectura técnica | Plan |
| Patrones de diseño (MVVM, Clean Architecture, Repository, UseCase) | Arquitectura interna de la app | Plan |
| Protocolos de autenticación técnicos (OAuth 2.0, JWT, PKCE) | Implementación de seguridad | Plan |
| Endpoints de API o contratos REST/GraphQL | Contratos técnicos entre sistemas | Plan |
| Esquemas de base de datos o modelos de datos formales | Arquitectura de datos | Plan |
| Nombres de componentes UI de plataforma (RecyclerView, Composable, UIViewController) | Específico de plataforma | Plan |
| Bloques de código o pseudocódigo | No es lenguaje de negocio | Plan / Tasks |
| Requisitos de rendimiento técnicos (latencia en ms, throughput, RAM) | Restricciones de ingeniería | Plan |
| Estructura de módulos o paquetes del proyecto | Organización técnica del código | Plan |
| Integraciones técnicas de bajo nivel (webhooks, colas de mensajes, eventos) | Detalle de arquitectura | Plan |
| Pantallas o vistas como unidades de feature | Las pantallas son implementación, las capacidades son negocio | Spec / Plan |
| Flujos de navegación con nombres de pantallas específicas | Detalle de UX de implementación | Spec |
| Especificaciones visuales (colores, tipografías, espaciados, tokens de diseño) | Diseño visual — no son requisitos funcionales | Fuera del pipeline SDD |
| Timelines de implementación o estimaciones de esfuerzo | Gestión de proyecto, no requisitos | Fuera del PRD |
| Criterios de aceptación técnicos (tiempo de respuesta, % de cobertura de tests) | QA técnico | Plan / Tasks |

---

## Nota sobre la plataforma

**Mención de plataforma permitida** (contexto de negocio):
> "App móvil para Android e iOS"

**Mención de plataforma prohibida** (tecnología de implementación):
> "Implementada con Kotlin Multiplatform Mobile usando Compose Multiplatform"

La primera informa al lector del tipo de producto. La segunda prescribe la tecnología — eso es Plan.

---

## Nota sobre integraciones externas

**Integración externa permitida** (capacidad de negocio):
> "El usuario puede autenticarse con su cuenta de Google"
> "El coordinador recibe alertas en tiempo real sobre cambios en los servicios"

**Integración externa prohibida** (detalle técnico):
> "Login implementado con Google Sign-In SDK y OAuth 2.0"
> "Alertas enviadas via WebSockets sobre el endpoint `/ws/services`"

La capacidad de negocio describe **qué** puede hacer el usuario. El detalle técnico describe **cómo** se implementa — eso es Plan.

---

## La Prueba de Negocio (referencia rápida)

Antes de incluir cualquier frase en el PRD, aplica estas dos preguntas:

1. **¿Puede un cliente de negocio no técnico leer y validar esta frase?**
   - SÍ → puede estar en el PRD
   - NO → pertenece al Plan

2. **¿Cambiaría esta frase si el equipo cambiara de tecnología?**
   - SÍ cambia → es un detalle de implementación → fuera del PRD
   - NO cambia → es funcional o de negocio → puede estar en el PRD
