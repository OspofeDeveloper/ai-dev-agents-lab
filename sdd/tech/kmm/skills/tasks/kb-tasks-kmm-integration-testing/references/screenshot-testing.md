# Screenshot Testing con Roborazzi

## Dependencias Gradle

En el módulo donde vivan los screenshot tests (`build.gradle.kts` del módulo app o feature):

```kotlin
// build.gradle.kts
plugins {
    id("io.github.takahirom.roborazzi") version "<version>"
}

androidTestImplementation("io.github.takahirom.roborazzi:roborazzi:$roborazziVersion")
androidTestImplementation("io.github.takahirom.roborazzi:roborazzi-compose:$roborazziVersion")
testImplementation("org.robolectric:robolectric:$robolectricVersion")

android {
    testOptions {
        unitTests {
            isIncludeAndroidResources = true
        }
    }
}
```

## Estructura de golden files

```
src/
  androidTest/
    snapshots/
      images/
        MyFeatureScreenTest_estado_success.png
        MyFeatureScreenTest_estado_loading.png
```

## Template básico

```kotlin
@RunWith(RobolectricTestRunner::class)
@Config(qualifiers = "w411dp-h891dp")  // dimensiones típicas Pixel 4
class MyFeatureScreenshotTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun `screenshot del estado Success`() {
        composeTestRule.setContent {
            AppTheme {
                MyFeatureScreen(state = MyState.Success(fakeItems))
            }
        }

        composeTestRule
            .onRoot()
            .captureRoboImage("src/androidTest/snapshots/images/MyFeatureScreen_success.png")
    }
}
```

## Comandos

```bash
# Registrar / regenerar goldens
./gradlew recordRoborazziDebug

# Verificar contra goldens (modo CI)
./gradlew verifyRoborazziDebug

# Ejecutar todos los tests incluyendo screenshots
./gradlew testDebugUnitTest
```

## Notas de CI

- Añadir `./gradlew verifyRoborazziDebug` al pipeline de CI
- Los goldens se commitean al repositorio (son la "fuente de verdad" visual)
- En PRs que cambien UI, regenerar goldens localmente y commitear los nuevos antes de mergear
- Usar la misma versión de Robolectric y los mismos qualifiers de Config en todos los tests para evitar flakiness
