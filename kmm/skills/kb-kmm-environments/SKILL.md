---
name: kb-kmm-environments
description: "Base de conocimiento del sistema multi-brand/multi-environment en KMM: arquitectura, plugin BuildConfig (gmazzo), prioridad de resolución brand/env, flujo XCConfig → Gradle en iOS, estructura de ficheros, jerarquía XCConfig, target vs scheme en Xcode, valores sensibles y troubleshooting."
argument-hint: ""
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# KMM Environments — Base de Conocimiento

## Regla 1: Arquitectura del sistema

El sistema tiene dos ejes de configuración independientes:

| Dimensión | Controla |
|-----------|----------|
| **brand** | App ID, nombre de la app, assets, lógica de negocio específica de marca |
| **env** | URL de API, sufijo del App ID (ej. `.pre`), flags de entorno |

Cada combinación brand×env produce una **variante**. Con 2 brands y 2 entornos hay 4 variantes; con N brands y M entornos hay N×M variantes.

El sistema genera un único objeto `BuildConfig` compartido en `commonMain` que es accesible desde todo el código Kotlin (Android e iOS). El valor de `BuildConfig` depende de qué variante se está compilando.

---

## Regla 2: Plugin BuildConfig (gmazzo)

Plugin: `com.github.gmazzo.buildconfig`, versión por defecto `6.0.9`.

Genera un objeto Kotlin en tiempo de compilación accesible desde `commonMain` con los campos declarados en el bloque `buildConfig { }` del módulo. Se registra como plugin en `gradle/libs.versions.toml` y se aplica en `composeApp/build.gradle.kts`.

Si el proyecto ya tiene el plugin con otra versión, usar la versión existente.

→ Templates: `references/android_buildconfig_templates.md`

---

## Regla 3: Prioridad de resolución brand/env en Android

```
Prioridad 1: Propiedad Gradle explícita   -Papp.brand=brand1   -Papp.env=env1
                 ↓ (si ausente)
Prioridad 2: Inspección del nombre de tarea   "assembleBrand1Env2Debug" → brand=brand1, env=env2
                 ↓ (si no hay coincidencia)
Prioridad 3: Valores por defecto   brand=brand1, env=env1 (el primer valor de cada dimensión)
```

iOS **siempre** usa la Prioridad 1 porque el Script Build Phase pasa explícitamente `-Papp.brand` y `-Papp.env`.

Android en CI/CD puede usar la Prioridad 1 también: `./gradlew assembleBrand1Env2Release -Papp.brand=brand1 -Papp.env=env2`.

Para proyectos con 3+ entornos, la lógica de Prioridad 2 usa un bloque `when` encadenado en lugar de un `if/else` simple.

→ Implementación: `references/android_buildconfig_templates.md`

---

## Regla 4: Flujo XCConfig → Gradle en iOS

1. El desarrollador selecciona un **Scheme** en Xcode (ej. `Brand1-Env1`)
2. El Scheme apunta a una **Build Configuration** (ej. `Debug-Env1`) que incluye el XCConfig de marca (ej. `Brand1/Brand1-Env1.xcconfig`)
3. El XCConfig define `APP_ENV = env1`
4. Cuando Xcode ejecuta el **Script Build Phase**, todos los valores del XCConfig activo están disponibles como variables de entorno de shell
5. El script lee `${APP_ENV}` y lo pasa a Gradle: `-Papp.env=${APP_ENV}`
6. Gradle recibe la propiedad explícita y usa la Prioridad 1

La selección del scheme en Xcode es la única fuente de verdad para los builds iOS. No hay ambigüedad posible.

→ Script: `references/ios_script_build_phase_template.md`

---

## Regla 5: Estructura de ficheros

| Fichero | Propósito |
|---------|-----------|
| `gradle/libs.versions.toml` | Declaración de versión y alias del plugin |
| `composeApp/build.gradle.kts` | Flavors Android + bloque `buildConfig` |
| `{brand}-{env}.properties` (raíz del proyecto) | Valores por variante que Gradle no puede derivar (URLs, keys) |
| `iosApp/Configuration/Shared.xcconfig` | Team ID, versión de marketing — compartido por todos los targets |
| `iosApp/Configuration/Debug.xcconfig` | `KOTLIN_FRAMEWORK_BUILD_TYPE = debug` |
| `iosApp/Configuration/Release.xcconfig` | `KOTLIN_FRAMEWORK_BUILD_TYPE = release` |
| `iosApp/Configuration/{Brand}/{Brand}-{Env}.xcconfig` | Configuración específica de marca×entorno para iOS |

Los ficheros `.properties` van en la **raíz del proyecto**, no dentro de ningún módulo.

---

## Regla 6: Jerarquía XCConfig

```
Debug.xcconfig
└── #include "Shared.xcconfig"

Release.xcconfig
└── #include "Shared.xcconfig"

{Brand}/{Brand}-{Env}.xcconfig
└── #include "../Shared.xcconfig"
    (NO incluye Debug.xcconfig ni Release.xcconfig)
```

En la pestaña Info del proyecto Xcode, cada fila de Build Configuration apunta a un XCConfig específico. Xcode aplica internamente las capas debug/release y la capa brand×env como configuraciones separadas asignadas a la misma build configuration row.

El XCConfig de brand×env **no incluye** el de debug/release; ambos se asignan en paralelo desde los settings del proyecto Xcode.

→ Templates: `references/ios_xcconfig_templates.md`

---

## Regla 7: Target vs Build Configuration vs Scheme en Xcode

El modelo de Xcode tiene tres capas que hay que crear en orden:

```
Target ──── Build Configuration ──── XCConfig
              │
  Scheme ─────┘  (scheme = target + build configuration por acción)
```

- **Target** = una unidad de compilación por **brand** (bundle ID base, firma, Info.plist, Build Phases). Con 1 brand se usa el target por defecto; con 2+ brands se duplica el target por cada brand adicional.
- **Build Configuration** = una por combinación **debug/release × env**. Siempre hay que crearlas, independientemente del número de brands. Con 2 envs: `Debug-{Env1}`, `Debug-{Env2}`, `Release-{Env1}`, `Release-{Env2}`. Se crean duplicando las configuraciones Debug/Release existentes del proyecto.
- **Scheme** = uno por **brand × env** (controla qué target + qué Build Configuration está activa al correr/archivar). Acción Run → `Debug-{Env}`; acción Archive → `Release-{Env}`.

### Árbol de decisión (a partir de la matriz brand×env del Paso 1)

```
brands.size - 1  →  targets adicionales a crear (0 si hay 1 brand)
envs.size × 2    →  Build Configurations a crear (Debug-{Env} + Release-{Env} por env)
brands × envs    →  schemes a crear
```

Con 1 brand, 2 envs: 0 targets nuevos, 4 Build Configurations, 2 schemes.  
Con 2 brands, 2 envs: 1 target nuevo, 4 Build Configurations, 4 schemes.

### Asignación XCConfig a Build Configurations (dos niveles)

Xcode permite asignar XCConfig a **nivel proyecto** y a **nivel target** sobre la misma Build Configuration. Ambos aplican en paralelo (no se excluyen):

| Build Configuration | XCConfig nivel proyecto | XCConfig nivel target |
|---------------------|-------------------------|-----------------------|
| Debug-{Env1}        | `Debug.xcconfig`        | `{Brand}/{Brand}-{Env1}.xcconfig` |
| Debug-{Env2}        | `Debug.xcconfig`        | `{Brand}/{Brand}-{Env2}.xcconfig` |
| Release-{Env1}      | `Release.xcconfig`      | `{Brand}/{Brand}-{Env1}.xcconfig` |
| Release-{Env2}      | `Release.xcconfig`      | `{Brand}/{Brand}-{Env2}.xcconfig` |

Así `KOTLIN_FRAMEWORK_BUILD_TYPE` viene del XCConfig de proyecto y `APP_ENV`/`APP_BRAND` vienen del XCConfig de target, sin colisión.

---

## Regla 8: Valores sensibles

**Pueden commitearse:**
- `APP_BASE_URL` (URLs de API no son secretas normalmente)
- Cualquier valor que no sea una credencial o clave privada

**NO deben commitearse (añadir a `.gitignore`):**
- API keys, tokens de analytics, secrets
- Cualquier valor que dé acceso a sistemas externos

**Patrón para CI:**
1. Añadir `.properties` a `.gitignore` para desarrollo local
2. En CI, generar los ficheros `.properties` en tiempo de build desde variables de entorno o un secrets manager
3. Para XCConfig, usar Xcode user-defined build settings o inyección desde CI

---

## Regla 9: Troubleshooting

| Síntoma | Causa | Solución |
|---------|-------|----------|
| `FileNotFoundException: brand1-env1.properties` | Fichero `.properties` no existe | Crear el fichero en la raíz del proyecto |
| `BuildConfig` no encontrado en el IDE | No se ha compilado todavía | Ejecutar cualquier tarea `assemble` una vez |
| iOS build usa la URL incorrecta | XCConfig no enlazado a la build configuration | Enlazar el XCConfig en la pestaña Info del proyecto Xcode |
| `APP_ENV` vacío en el script | XCConfig no aplicado | Verificar que el scheme usa la build configuration correcta |
| Brand incorrecto en iOS build | Script Build Phase tiene `-Papp.brand=` hardcodeado con valor erróneo | Revisar el valor en el script del target correspondiente |
| Variante errónea en Android IDE | Prioridad 2: el nombre de la tarea de sync contiene el nombre de un entorno | Usar Prioridad 1 en CI o cambiar el Variant selector en el IDE |