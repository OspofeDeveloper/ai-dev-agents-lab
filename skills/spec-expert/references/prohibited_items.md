# Tabla de Elementos Prohibidos en un Spec

Estos elementos contaminan el Spec y rompen el flujo SDD. Pertenecen exclusivamente al **Plan**:

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

## La Prueba de Pureza

Ante cualquier frase en el Spec, pregunta: "¿Cambiaría esto si pasáramos de mobile a web, o de Kotlin a Python?"
- **SÍ cambia** → es un detalle técnico → va al Plan
- **NO cambia** → es funcional → puede quedarse en el Spec
