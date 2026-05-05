# Android BuildConfig — Templates

Variant implementation patterns. Semantic rules for `brand` and `env` live in `kb-kmm-environments`.

## libs.versions.toml

```toml
[versions]
buildConfig = "6.0.9"

[plugins]
gradleBuildConfig = { id = "com.github.gmazzo.buildconfig", version.ref = "buildConfig" }
```

Use existing version if the plugin is already declared.

## Generated BuildConfig object

```kotlin
// Auto-generated — do not edit
object BuildConfig {
    val APP_BASE_URL: String = "https://pre-api.example.com"
}
```

Actual fields depend on the shared contract the project exposes.

## Apply plugin (composeApp/build.gradle.kts)

```kotlin
plugins {
    alias(libs.plugins.gradleBuildConfig)
}
```

## Flavor dimensions and productFlavors (inside `android { }`)

```kotlin
flavorDimensions += listOf("brand", "environment")

productFlavors {
    create("{brand1}") {
        dimension = "brand"
        applicationId = "{appId1}"
        resValue("string", "app_name", "{Brand1 Display Name}")
    }
    // repeat for each additional brand

    create("{env1}") {
        dimension = "environment"
        applicationIdSuffix = ".{env1}"  // omit if env has no suffix
    }
    create("{env2}") {
        dimension = "environment"
        // no suffix for production
    }
    // repeat for each additional env
}
```

## buildConfig block (after `android { }`)

Fixed scaffold for `brand`/`env` resolution + project field declarations.

```kotlin
buildConfig {
    packageName("{basePackage}")

    val taskNames = gradle.startParameter.taskNames.joinToString(" ").lowercase()

    val brand = project.findProperty("app.brand")?.toString()?.lowercase()
        ?: if (taskNames.contains("{brand2}")) "{brand2}" else "{brand1}"

    val env = project.findProperty("app.env")?.toString()?.lowercase()
        ?: if (taskNames.contains("{env2}")) "{env2}" else "{env1}"

    val properties = Properties().apply {
        load(project.rootProject.file("${brand}-${env}.properties").reader())
    }

    // Declare only fields needed by the shared contract:
    // buildConfigField("APP_BASE_URL", properties.getProperty("APP_BASE_URL").trim())
}
```

## brand/env resolution for 3+ environments

```kotlin
val env = project.findProperty("app.env")?.toString()?.lowercase()
    ?: when {
        taskNames.contains("env3") -> "env3"
        taskNames.contains("env2") -> "env2"
        else -> "env1"
    }
```