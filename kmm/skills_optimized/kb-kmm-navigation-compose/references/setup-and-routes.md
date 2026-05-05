# Setup and Routes — Code Examples

## Gradle dependencies

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

---

## Serialization plugin

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

---

## Route definitions with `@Serializable`

```kotlin
// shared/src/commonMain/kotlin/com/example/app/navigation/AppRoutes.kt
package com.example.app.navigation

import kotlinx.serialization.Serializable

// Route with no arguments
@Serializable
object LoginRoute

@Serializable
object HomeRoute

// Route with required arguments
@Serializable
data class ProfileRoute(val userId: String)

// Route with optional arguments (with default value)
@Serializable
data class DetailRoute(
    val itemId: String,
    val showComments: Boolean = false
)

// Nested graph root routes
@Serializable
object AuthGraph

@Serializable
object MainGraph
```