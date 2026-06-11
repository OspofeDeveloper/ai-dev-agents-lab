---
name: kb-tasks-kmm-integration-testing
description: "Patrones de implementación de tests de integración KMM/CMP: árbol semántico Compose con composeTestRule, accesibilidad con useUnmergedTree, screenshot regression con Roborazzi y capa de datos con DB in-memory."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Tests de Integración KMM — Patrones de Implementación

> Decisiones de arquitectura de testing: `kb-kmm-testing-strategy`.
> **Patrones de test de grafo de navegación (TestNavHostController, FakeNavigation): SSoT en `${CLAUDE_SKILL_DIR}/../kb-kmm-navigation-compose/references/testing.md`. Esta skill no los duplica.**

## Regla 1: Los tests de integración viven en `androidTest` cuando requieren runtime Compose

Cualquier test que use `composeTestRule`, `TestNavHostController`, `createAndroidComposeRule` o Roborazzi vive en `androidTest`. No hay alternativa en commonTest para estos tests porque requieren el runtime de Compose para Android o Robolectric.

```kotlin
// androidTest
@get:Rule
val composeTestRule = createComposeRule()
```

---

## Regla 2: Los tests de integración validan contratos entre capas, no componentes aislados

Un test de integración conecta al menos dos capas reales. Ejemplos válidos:

- RepositoryImpl + Room in-memory (sin red real)
- ViewModel + UseCase + FakeRepository (sin fake del UseCase)
- Screen Composable + ViewModel real con fakes de sus dependencias

El objetivo es detectar fallos en la frontera entre capas que los tests unitarios con fakes no pueden detectar.

---

## Regla 3: Tests del árbol semántico Compose usan `composeTestRule` con nodos semánticos

El árbol semántico mergeado es el default. Usar `useUnmergedTree = true` solo cuando el layout usa un contenedor custom que merge nodos y necesitas acceder a nodos internos.

```kotlin
@Test
fun `la pantalla muestra el título de la feature`() {
    composeTestRule.setContent {
        MyFeatureScreen(state = MyState.Success(title = "Mi Feature"))
    }

    composeTestRule
        .onNodeWithText("Mi Feature")
        .assertIsDisplayed()
}

// Con useUnmergedTree para nodos internos de un contenedor custom:
composeTestRule
    .onNode(hasText("Label interno"), useUnmergedTree = true)
    .assertExists()
```

Consulta `${CLAUDE_SKILL_DIR}/references/compose-integration-test-templates.md` para más ejemplos.

---

## Regla 4: Screenshot regression testing con Roborazzi en `androidTest`

Roborazzi es la librería canónica para screenshot tests en este stack porque soporta Robolectric (no requiere emulador físico para CI).

- Golden files en `src/androidTest/snapshots/`
- Usar `@RoborazziRule` o `captureRoboImage()` directamente
- En CI: ejecutar con modo de verificación (`--stacktrace` si falla); en local: regenerar con `recordRoborazziDebug`

```kotlin
@Test
@Config(qualifiers = "w411dp-h891dp")  // Pixel 4 like
fun `screenshot del estado Success de la pantalla`() {
    composeTestRule.setContent {
        MyFeatureScreen(state = MyState.Success(items = fakeItems))
    }
    composeTestRule.onRoot().captureRoboImage()
}
```

Consulta `${CLAUDE_SKILL_DIR}/references/screenshot-testing.md` para configuración de Gradle y CI.

---

## Regla 5: Tests de accesibilidad verifican role semántico, descripción y estado

Los tests de accesibilidad forman parte del ciclo de tests de integración y verifican que los nodos semánticos son correctos para lectores de pantalla.

```kotlin
@Test
fun `el botón de confirmación tiene contentDescription y está habilitado`() {
    composeTestRule.setContent {
        ConfirmButton(onConfirm = {})
    }

    composeTestRule
        .onNode(hasContentDescription("Confirmar acción"))
        .assertIsEnabled()
        .assertHasClickAction()
}

// Con useUnmergedTree para componentes que agrupan semántica:
composeTestRule
    .onNode(hasContentDescription("Elemento de lista: Item 1"), useUnmergedTree = true)
    .assertExists()
```

Los criterios de qué debe tener contentDescription y qué roles son obligatorios provienen de `kb-plan-expert`. Esta skill solo define cómo verificarlos.

---

## Regla 6: Tests de capa de datos usan bases de datos in-memory

Cuando el RepositoryImpl usa Room, el test de integración usa la factory in-memory:

```kotlin
val db = Room.inMemoryDatabaseBuilder(
    ApplicationProvider.getApplicationContext(),
    AppDatabase::class.java
).allowMainThreadQueries().build()
val dao = db.myEntityDao()
val fakeRemote = FakeMyRemoteDataSource()
val repo = MyRepositoryImpl(dao, fakeRemote)
```

No hacer llamadas HTTP reales en tests de integración. El DataSource remoto siempre es un fake.
