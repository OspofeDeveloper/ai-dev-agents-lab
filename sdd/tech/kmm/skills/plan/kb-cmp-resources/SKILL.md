---
name: kb-cmp-resources
description: Base de conocimiento de recursos compartidos en Compose Multiplatform con compose-resources (Res.*): estructura de carpetas, strings, drawables, fonts y configuración del plugin. Úsalo cuando haya que planificar acceso a recursos de UI en un proyecto CMP.
allowed-tools: [Read]
---

# CMP Resources — compose-resources

## Qué es compose-resources

`compose-resources` es el sistema de recursos compartidos de Compose Multiplatform.
Genera automáticamente un objeto `Res` con accessors tipados para cada recurso declarado
en `commonMain/composeResources/`.

## Estructura de carpetas

```
src/
└── commonMain/
    └── composeResources/
        ├── drawable/          → Imágenes vectoriales (.xml, .svg) y rasterizadas (.png, .webp)
        ├── font/              → Fuentes (.ttf, .otf)
        └── values/
            ├── strings.xml    → Strings localizables
            └── colors.xml     → Colores (opcional, preferir tokens de DESIGN.md en código Kotlin)
```

## Acceso en código

```kotlin
// Strings
stringResource(Res.string.account_name_label)

// Drawables
painterResource(Res.drawable.ic_wallet)

// Fonts (en MaterialTheme o TextStyle)
FontFamily(Font(Res.font.inter_regular))
```

## Localización

Para strings localizados, crear subcarpetas `values-es/`, `values-en/`, etc.
La carpeta `values/` sin sufijo es el fallback.

## Configuración en build.gradle.kts

```kotlin
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(compose.components.resources)
        }
    }
}

compose.resources {
    publicResClass = true
    generateResClass = always
}
```

## Reglas

1. No usar `R.string.*` ni `R.drawable.*` de Android en código de commonMain.
2. No declarar recursos en `androidMain/res/` para assets compartidos — usar `composeResources/`.
3. Los recursos propios de plataforma (iconos de app, launch screen) sí van en sus carpetas nativas.
4. Los design tokens de color viven en código Kotlin (MaterialTheme), no en `colors.xml`.
