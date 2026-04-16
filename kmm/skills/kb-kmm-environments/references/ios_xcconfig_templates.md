# iOS XCConfig — Templates

Todos los ficheros van en `iosApp/Configuration/`. Ver Regla 6 del kb- para la jerarquía de includes y Regla 7 para la relación target/scheme.

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

Variante para entorno de staging/pre (con sufijo en bundle ID):

```xcconfig
#include "../Shared.xcconfig"

PRODUCT_NAME               = {Brand Display} {Env Display}
PRODUCT_BUNDLE_IDENTIFIER  = {appId}.{env1suffix}
API_URL                    = https://{env1-subdomain}.{brand-domain}
APP_BRAND                  = {brand}
IS_PRE                     = YES
APP_ENV                    = {env1}
```

---

## § {Brand}/{Brand}-{Env_pro}.xcconfig

Variante para entorno de producción (sin sufijo en bundle ID):

```xcconfig
#include "../Shared.xcconfig"

PRODUCT_NAME               = {Brand Display}
PRODUCT_BUNDLE_IDENTIFIER  = {appId}
API_URL                    = https://{brand-domain}
APP_BRAND                  = {brand}
IS_PRE                     = NO
APP_ENV                    = {env2}
```

---

`APP_ENV` es el valor que el Script Build Phase lee como variable de entorno de shell (`${APP_ENV}`) para pasarlo a Gradle como `-Papp.env`. Es la única variable que conecta el XCConfig con el script.
