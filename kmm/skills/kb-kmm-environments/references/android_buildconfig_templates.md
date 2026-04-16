# Android BuildConfig — Templates

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
    val APP_BASE_URL : String  = "https://pre-api.example.com"
    val BRAND        : String  = "BRAND1_ENV1"
    val IS_PRE       : Boolean = true
}
```

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

Esto genera N_brands × N_envs × 2 build types variantes automáticamente.

---

## § Bloque buildConfig

Después del bloque `android { }` en `composeApp/build.gradle.kts`.

El bloque tiene dos partes: el **scaffold fijo** (resolución de brand/env y carga de properties) y los **buildConfigField**, que se añaden únicamente para las variables recopiladas en el Paso 1. No añadir ningún campo que el usuario no haya pedido.

```kotlin
buildConfig {
    packageName("{basePackage}")

    val taskNames = gradle.startParameter.taskNames.joinToString(" ").lowercase()

    // Brand: propiedad explícita (iOS) → nombre de tarea → default
    val brand = project.findProperty("app.brand")?.toString()?.lowercase()
        ?: if (taskNames.contains("{brand2}")) "{brand2}" else "{brand1}"

    // Env: propiedad explícita (iOS) → nombre de tarea → default (2 entornos)
    val env = project.findProperty("app.env")?.toString()?.lowercase()
        ?: if (taskNames.contains("{env2}")) "{env2}" else "{env1}"
    // Para 3+ entornos usar la variante con when{} de la sección siguiente

    val propertiesFile = project.rootProject.file("${brand}-${env}.properties")
    val properties = Properties().apply { load(propertiesFile.reader()) }

    // ── buildConfigField solo para los campos pedidos en el Paso 1 ──────────
    // Campos leídos de .properties (valores por variante como URLs, keys):
    //   buildConfigField("APP_BASE_URL", properties.getProperty("APP_BASE_URL").trim())
    //
    // Campos derivados de brand/env (no necesitan .properties):
    //   buildConfigField("BRAND", "${brand.uppercase()}_${env.uppercase()}")
    //   buildConfigField("IS_PRE", env == "{env1}")
    // ────────────────────────────────────────────────────────────────────────
}
```

---

## § Lógica de resolución para 3+ entornos

Variante del bloque `env` cuando hay 3 o más entornos (reemplaza el `if/else` simple):

```kotlin
val env = project.findProperty("app.env")?.toString()?.lowercase()
    ?: when {
        taskNames.contains("env3") -> "env3"
        taskNames.contains("env2") -> "env2"
        else -> "env1"  // default
    }
```

Encadenar condiciones `when` por orden de prioridad descendente; el último `else` es el entorno por defecto.
