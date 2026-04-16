# iOS Script Build Phase — Template

Script a añadir como **Run Script Build Phase** en cada target de Xcode. Ver Regla 4 del kb- para entender cómo `${APP_ENV}` llega al script desde el XCConfig activo.

Cada target tiene el brand fijo (`-Papp.brand=`) porque un target representa una marca concreta. El entorno viene dinámico desde el XCConfig a través de `${APP_ENV}`.

---

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

---

Reemplazar `{brand1}`, `{brand2}` por los nombres en minúscula de cada marca (deben coincidir exactamente con los valores declarados en los `productFlavors` de Gradle).
