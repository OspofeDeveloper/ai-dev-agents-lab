# Setup y Rutas — Ejemplos de Código

## Dependencias Gradle

### libs.versions.toml

```toml
[versions]
navigationCompose = "2.9.2"

[libraries]
navigation-compose = { module = "org.jetbrains.androidx.navigation:navigation-compose", version.ref = "navigationCompose" }
```

### composeApp/build.gradle.kts

```kotlin
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.navigation.compose)
        }
    }
}
```

## Plugin de serialización

```kotlin
// composeApp/build.gradle.kts
plugins {
    kotlin("plugin.serialization")
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.serialization.json)
        }
    }
}
```

## Definición de rutas con `@Serializable`

```kotlin
// shared/src/commonMain/kotlin/com/example/app/navigation/AppRoutes.kt
package com.example.app.navigation

import kotlinx.serialization.Serializable

// Ruta sin argumentos
@Serializable
object LoginRoute

@Serializable
object HomeRoute

// Ruta con argumentos requeridos
@Serializable
data class ProfileRoute(val userId: String)

// Ruta con argumentos opcionales (con valor por defecto)
@Serializable
data class DetailRoute(
    val itemId: String,
    val showComments: Boolean = false
)

// Rutas raíz de nested graphs
@Serializable
object AuthGraph

@Serializable
object MainGraph
```