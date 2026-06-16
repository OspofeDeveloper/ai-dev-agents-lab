# Tabla de Elementos Prohibidos en un Spec

Estos elementos contaminan el Spec y rompen el flujo SDD. Pertenecen exclusivamente al **Plan**:

> **Relación con `kb-prd-expert/references/prd_prohibited_items.md`:** Este catálogo es **subset** del catálogo del PRD. El Spec admite cosas que el PRD prohíbe (pantallas, flujos de navegación con destinos específicos, etc.) porque el Spec ya describe comportamiento funcional concreto. Pero todo lo prohibido aquí también está prohibido en el PRD.

| Elemento prohibido | Por qué está prohibido | Dónde pertenece |
|---|---|---|
| Lenguajes de programación (Python, Kotlin, Swift, JS) | Hace el Spec tecnología-dependiente | Plan |
| Frameworks (React, Django, Spring, Ktor) | Detalle de implementación | Plan |
| Bases de datos o almacenamiento específico | Arquitectura técnica | Plan |
| Patrones de diseño (MVVM, MVC, microservicios, Clean Architecture) | Arquitectura técnica | Plan |
| Requisitos de rendimiento técnico (latencia, throughput) | Restricción técnica | Plan |
| Detalles de seguridad de implementación (OAuth scopes, JWT, hashing) | Restricción técnica | Plan |
| Endpoints de API o integraciones de bajo nivel | Detalle técnico | Plan |
| Bloques de código de cualquier tipo | No es lenguaje natural | Plan/Tasks |
| Nombres de componentes UI específicos de plataforma (RecyclerView, UITableView, Composable) | Específico de plataforma | Plan |
| Especificaciones estéticas profundas (colores hex, tipografías, espaciados) | Diseño visual técnico | Plan |

## Nota sobre la sección "Fuera de Alcance"

La sección `## Fuera de Alcance` es obligatoria y debe contener **exclusiones funcionales**, no técnicas.

| Correcto (funcional) | Incorrecto (técnico — va al Plan) |
|---------------------|----------------------------------|
| "La gestión de contraseñas queda fuera de este spec" | "No usaremos PostgreSQL" |
| "Las notificaciones push son parte del spec de Notificaciones, no de este" | "No se implementará caché en este feature" |
| "El histórico de versiones no está incluido en esta entrega" | "Sin soporte para iOS < 14" |

## La Prueba de Pureza

Ante cualquier frase en el Spec, pregunta: "¿Cambiaría esto si pasáramos de mobile a web, o de Kotlin a Python?"
- **SÍ cambia** → es un detalle técnico → va al Plan
- **NO cambia** → es funcional → puede quedarse en el Spec
