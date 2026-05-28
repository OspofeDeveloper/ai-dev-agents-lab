---
name: kb-cmp-resources
description: Base de conocimiento de recursos compartidos en Compose Multiplatform con compose-resources (Res.*): qué es el sistema, estructura de carpetas, semántica de localización y qué módulos se ven afectados. Úsalo cuando haya que planificar el acceso a recursos de UI en un proyecto CMP.
allowed-tools: [Read]
---

# CMP Resources — compose-resources (nivel planificación)

## Qué es compose-resources

`compose-resources` es el sistema de recursos compartidos de Compose Multiplatform.
Genera automáticamente un objeto `Res` con accessors tipados para cada recurso declarado
en `commonMain/composeResources/`.

Todos los assets compartidos (strings, drawables, fonts, raw files) viven en este sistema,
independientemente de la plataforma destino.

## Estructura de carpetas

```
src/
└── commonMain/
    └── composeResources/
        ├── drawable/    → vectoriales e imágenes rasterizadas compartidas
        ├── font/        → fuentes (.ttf, .otf)
        └── values/
            ├── strings.xml    → strings localizables
            └── colors.xml     → colores (opcional; preferir tokens Kotlin en MaterialTheme)
```

## Semántica de localización

Las traducciones viven en subcarpetas `values-{locale}/` con el mismo nombre de fichero.
La carpeta `values/` sin sufijo actúa como fallback.

## Qué módulos necesitan compose-resources

El módulo compartido (`:shared` o `:composeApp`) declara la dependencia
`compose.components.resources` y activa la generación de `Res`.
Las features consumen `Res` desde `commonMain` sin dependencia adicional.

## Criterios de planificación

- Los recursos propios de plataforma (iconos de app, launch screen, splash) **no** van en `composeResources/` — van en sus carpetas nativas.
- Los design tokens de color viven en código Kotlin (MaterialTheme), no en `colors.xml`.
- El plan debe prever la carpeta de localización si la feature expone strings traducibles.

→ Implementación concreta (build.gradle.kts, APIs Res.*): `kb-kmm-resources`
