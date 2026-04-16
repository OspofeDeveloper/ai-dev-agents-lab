# Referencia de uso post-configuración

## § Comandos de build Android

```bash
./gradlew :composeApp:assemble{Brand}{Env}Debug
# ej: ./gradlew :composeApp:assembleBrand1Env1Debug

./gradlew :composeApp:assemble{Brand}{Env}Release
# ej: ./gradlew :composeApp:assembleBrand2Env2Release
```

Con propiedades explícitas (Prioridad 1, recomendado en CI/CD):
```bash
./gradlew assembleBrand1Env2Release -Papp.brand=brand1 -Papp.env=env2
```

## § Build iOS

Seleccionar el scheme en Xcode (ej. `Brand1-Env1`) y ejecutar normalmente. La selección del scheme es la única fuente de verdad — no hay ambigüedad posible.

---

## § Usar BuildConfig en código compartido

```kotlin
import {basePackage}.BuildConfig

if (BuildConfig.IS_PRE) {
    // lógica solo en staging
}

val baseUrl = BuildConfig.APP_BASE_URL

when {
    BuildConfig.BRAND.startsWith("{BRAND1}") -> { /* lógica brand1 */ }
    BuildConfig.BRAND.startsWith("{BRAND2}") -> { /* lógica brand2 */ }
}
```

---

## § Añadir una variable nueva

1. Añadirla a todos los ficheros `.properties` (ver `references/android_properties_templates.md`)
2. En `composeApp/build.gradle.kts`, añadir dentro del bloque `buildConfig { }`:
   ```kotlin
   buildConfigField("KEY", properties.getProperty("KEY").trim())
   ```
3. Si el código Swift de iOS también la necesita: añadirla a cada XCConfig y referenciarla en `Info.plist` como `$(KEY)`
