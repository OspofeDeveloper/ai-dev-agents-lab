# Android BuildConfig — Templates

Estos ejemplos muestran la implementación Android del sistema de variantes. La semántica estable de `brand` y `env` vive en `kb-kmm-environments`.

## § libs.versions.toml

Declaración del plugin en `gradle/libs.versions.toml`:

```toml
[versions]
buildConfig = "6.0.9"

[plugins]
gradleBuildConfig = { id = "com.github.gmazzo.buildconfig", version.ref = "buildConfig" }
```

Si el proyecto ya tiene el plugin con otra versión, usar la versión existente.

---

## § Objeto BuildConfig generado

Ejemplo del objeto Kotlin generado automáticamente en `commonMain`:

```kotlin
// Generado automáticamente — no editar
object BuildConfig {
    val APP_BASE_URL: String = "https://pre-api.example.com"
}
```

Los campos reales dependen del contrato de configuración que el proyecto haya decidido exponer.

---

## § Aplicar plugin

Al inicio del bloque `plugins { }` en `composeApp/build.gradle.kts`:

```kotlin
alias(libs.plugins.gradleBuildConfig)
```

---

## § Flavor dimensions y productFlavors

Dentro de `android { }` en `composeApp/build.gradle.kts`:

```kotlin
flavorDimensions += listOf("brand", "environment")

productFlavors {
    create("{brand1}") {
        dimension = "brand"
        applicationId = "{appId1}"
        resValue("string", "app_name", "{Brand1 Display Name}")
    }
    // repetir por cada brand adicional

    create("{env1}") {
        dimension = "environment"
        applicationIdSuffix = ".{env1}"   // omitir si el entorno no tiene sufijo
    }
    create("{env2}") {
        dimension = "environment"
        // sin sufijo para producción
    }
    // repetir por cada entorno adicional
}
```

---

## § Bloque buildConfig

Después del bloque `android { }` en `composeApp/build.gradle.kts`.

El bloque tiene dos partes: el scaffold fijo de resolución de `brand/env` y la declaración de los campos concretos del proyecto.

```kotlin
buildConfig {
    packageName("{basePackage}")

    val taskNames = gradle.startParameter.taskNames.joinToString(" ").lowercase()

    val brand = project.findProperty("app.brand")?.toString()?.lowercase()
        ?: if (taskNames.contains("{brand2}")) "{brand2}" else "{brand1}"

    val env = project.findProperty("app.env")?.toString()?.lowercase()
        ?: if (taskNames.contains("{env2}")) "{env2}" else "{env1}"

    val propertiesFile = project.rootProject.file("${brand}-${env}.properties")
    val properties = Properties().apply { load(propertiesFile.reader()) }

    // Añadir solo los campos del contrato compartido que el proyecto necesite:
    // buildConfigField("APP_BASE_URL", properties.getProperty("APP_BASE_URL").trim())
}
```

---

## § Lógica de resolución para 3+ entornos

Variante del bloque `env` cuando hay 3 o más entornos:

```kotlin
val env = project.findProperty("app.env")?.toString()?.lowercase()
    ?: when {
        taskNames.contains("env3") -> "env3"
        taskNames.contains("env2") -> "env2"
        else -> "env1"
    }
```
