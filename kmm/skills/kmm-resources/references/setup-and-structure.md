# Setup y Estructura — Ejemplos de Código

## 1. Estructura de directorios

```
shared/
└── src/
    └── commonMain/
        └── composeResources/
            ├── values/
            │   └── strings.xml
            ├── values-es/
            │   └── strings.xml
            ├── values-fr/
            │   └── strings.xml
            ├── drawable/
            │   ├── ic_logo.xml
            │   └── img_placeholder.png
            ├── font/
            │   └── roboto_regular.ttf
            └── files/
                └── config.json
```

## 2. Configuración Gradle

```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(compose.components.resources)
        }
    }
}

compose.resources {
    publicResClass = true
    packageOfResClass = "myapp.shared.generated.resources"
    generateResClass = always
}
```
