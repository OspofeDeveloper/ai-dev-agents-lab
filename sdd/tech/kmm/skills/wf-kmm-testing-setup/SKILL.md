---
name: wf-kmm-testing-setup
description: "Configura la infraestructura de testing en un proyecto KMM: dependencias Gradle por tipo de test (unit, integration, screenshot), source sets commonTest/androidTest/iosTest y directorio commonTest/fakes/."
when_to_use: "Activar con frases como 'configura testing en el proyecto', 'añade soporte de tests', 'setup de infraestructura de testing KMM'."
argument-hint: "[unit|integration|screenshot|all] [--modules <lista_módulos>]"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-platform-integrator
user-invocable: true
---

# wf-kmm-testing-setup

## Paso 1: Determinar el alcance del setup

Antes de configurar nada, confirmar:

1. qué tipos de test se configuran: `unit`, `integration`, `screenshot` o `all`
2. qué módulos del proyecto se ven afectados (`:app`, `:feature:nombre`, `:core`, etc.)
3. si los source sets `commonTest`, `androidTest`, `iosTest` ya existen o hay que crearlos
4. si ya existe alguna dependencia de testing en el `build.gradle.kts` para evitar duplicados

Aplicar:
- `kb-kmm-testing-strategy` — para confirmar las herramientas correctas por source set
- `kb-tasks-kmm-unit-testing` — para las dependencias de unit test
- `kb-tasks-kmm-integration-testing` — para las dependencias de integration y screenshot test

---

## Paso 2: Verificar o crear source sets

Verificar que existen los source sets necesarios en el `build.gradle.kts` del módulo KMM (`kotlin { sourceSets { ... } }`):

```kotlin
val commonTest by getting {
    dependencies {
        implementation(kotlin("test"))
    }
}
val androidTest by getting {
    dependencies {
        // dependencias de androidTest según el tipo de setup
    }
}
```

Si no existen, crearlos. Si ya existen, añadir dependencias sin reemplazar las existentes.

---

## Paso 3: Añadir dependencias Gradle según el alcance

### Para `unit` (siempre en commonTest):
```kotlin
// commonTest
implementation(kotlin("test"))
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:$coroutinesVersion")
implementation("app.cash.turbine:turbine:$turbineVersion")
```

### Para `integration` (en androidTest):
```kotlin
// androidTest
implementation("androidx.compose.ui:ui-test-junit4:$composeVersion")
implementation("androidx.compose.ui:ui-test-manifest:$composeVersion")
```

### Para `screenshot` (en androidTest, requiere también integration):
```kotlin
// plugins en build.gradle.kts
id("io.github.takahirom.roborazzi") version "<roborazziVersion>"

// androidTest deps
implementation("io.github.takahirom.roborazzi:roborazzi:$roborazziVersion")
implementation("io.github.takahirom.roborazzi:roborazzi-compose:$roborazziVersion")
testImplementation("org.robolectric:robolectric:$robolectricVersion")

// android block
testOptions {
    unitTests {
        isIncludeAndroidResources = true
    }
}
```

---

## Paso 4: Crear el directorio `commonTest/fakes/`

Si no existe, crear el directorio `src/commonTest/kotlin/<paquete_base>/fakes/` en cada módulo configurado.

Añadir un archivo `.gitkeep` si el directorio queda vacío, para que el commit lo incluya.

Seguir la **Regla 5** de `kb-kmm-testing-strategy` para la convención de nombrado de fakes.

---

## Paso 5: Verificar compilación

Ejecutar la compilación de tests para verificar que la configuración es correcta:

```bash
./gradlew compileDebugAndroidTestKotlin  # si hay androidTest
./gradlew compileTestKotlinMetadata       # si hay commonTest
```

Si hay errores de compilación, reportarlos antes de cerrar el setup.

---

## Paso 6: Reportar al usuario

Informar con claridad:

- módulos configurados y tipos de test activados
- source sets creados o actualizados
- dependencias añadidas (con versiones o indicación de que se usan las del catálogo del proyecto)
- directorio `fakes/` creado si aplica
- si la compilación fue exitosa o hay errores pendientes
- siguiente paso sugerido: cargar `kb-tasks-kmm-unit-testing` o `kb-tasks-kmm-integration-testing` según el tipo de test a implementar
