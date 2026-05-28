# iOS Script Build Phase — Template

Este ejemplo muestra cómo pasar a Gradle la variante activa ya resuelta por Xcode. La semántica estable de `brand` y `env` vive en `kb-kmm-environments`.

Cada target tiene el brand fijo porque un target representa una marca concreta. El entorno viene del XCConfig activo mediante `${APP_ENV}`.

## § Target {brand1}

```sh
cd "$SRCROOT/.."
./gradlew :composeApp:embedAndSignAppleFrameworkForXcode \
  -Papp.brand={brand1} \
  "-Papp.env=${APP_ENV}"
```

## § Target {brand2}

```sh
cd "$SRCROOT/.."
./gradlew :composeApp:embedAndSignAppleFrameworkForXcode \
  -Papp.brand={brand2} \
  "-Papp.env=${APP_ENV}"
```
