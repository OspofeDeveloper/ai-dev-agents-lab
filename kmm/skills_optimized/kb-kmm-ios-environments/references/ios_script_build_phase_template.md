# iOS Script Build Phase — Template

This example shows how to pass the active variant — already resolved by Xcode — to Gradle. The stable semantics of `brand` and `env` are defined in `kb-kmm-environments`.

Each target has a fixed brand because a target represents a specific brand. The environment comes from the active XCConfig via `${APP_ENV}`.

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