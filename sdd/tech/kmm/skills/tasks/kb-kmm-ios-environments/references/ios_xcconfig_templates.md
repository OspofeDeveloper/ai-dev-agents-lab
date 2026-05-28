# iOS XCConfig — Templates

Estos ejemplos muestran la implementación iOS del sistema de variantes. La semántica de `brand` y `env` vive en `kb-kmm-environments`.

Todos los ficheros van en `iosApp/Configuration/`.

---

## § Shared.xcconfig

```xcconfig
DEVELOPMENT_TEAM = {TEAM_ID}
MARKETING_VERSION = 1.0
CURRENT_PROJECT_VERSION = 1
```

---

## § Debug.xcconfig

```xcconfig
#include "Shared.xcconfig"
KOTLIN_FRAMEWORK_BUILD_TYPE = debug
SWIFT_OPTIMIZATION_LEVEL = -Onone
```

---

## § Release.xcconfig

```xcconfig
#include "Shared.xcconfig"
KOTLIN_FRAMEWORK_BUILD_TYPE = release
SWIFT_OPTIMIZATION_LEVEL = -O
```

---

## § {Brand}/{Brand}-{Env_pre}.xcconfig

```xcconfig
#include "../Shared.xcconfig"

PRODUCT_NAME               = {Brand Display} {Env Display}
PRODUCT_BUNDLE_IDENTIFIER  = {appId}.{env1suffix}
APP_ENV                    = {env1}
```

---

## § {Brand}/{Brand}-{Env_pro}.xcconfig

```xcconfig
#include "../Shared.xcconfig"

PRODUCT_NAME               = {Brand Display}
PRODUCT_BUNDLE_IDENTIFIER  = {appId}
APP_ENV                    = {env2}
```

---

`APP_ENV` es el valor que el Script Build Phase pasa a Gradle como `-Papp.env`.
