# Compose Integration Test Templates

> SSoT de patrones de navegación con TestNavHostController y FakeNavigation: `kb-kmm-navigation-compose/references/testing.md`. No duplicar aquí.

## Template: test semántico básico

```kotlin
@RunWith(AndroidJUnit4::class)
class MyFeatureScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun `muestra lista de items cuando el estado es Success`() {
        val items = listOf(MyItem(1, "Elemento 1"), MyItem(2, "Elemento 2"))

        composeTestRule.setContent {
            MyFeatureScreen(state = MyState.Success(items))
        }

        composeTestRule.onNodeWithText("Elemento 1").assertIsDisplayed()
        composeTestRule.onNodeWithText("Elemento 2").assertIsDisplayed()
    }

    @Test
    fun `muestra indicador de carga cuando el estado es Loading`() {
        composeTestRule.setContent {
            MyFeatureScreen(state = MyState.Loading)
        }

        composeTestRule.onNodeWithContentDescription("Cargando").assertIsDisplayed()
    }
}
```

## Template: test con useUnmergedTree

```kotlin
@Test
fun `el chip de categoría muestra el texto correcto en su nodo interno`() {
    composeTestRule.setContent {
        CategoryChip(label = "Tecnología", selected = true)
    }

    // useUnmergedTree cuando el Chip mergea semántica del Row interno
    composeTestRule
        .onNode(hasText("Tecnología"), useUnmergedTree = true)
        .assertExists()
        .assertIsSelected()
}
```

## Template: test de accesibilidad

```kotlin
@Test
fun `el botón de acción principal tiene contentDescription y acción de click`() {
    composeTestRule.setContent {
        PrimaryActionButton(label = "Guardar", onClick = {})
    }

    composeTestRule
        .onNode(hasContentDescription("Guardar"))
        .assertIsEnabled()
        .assertHasClickAction()
}

@Test
fun `los items de la lista tienen contentDescription con información completa`() {
    val item = MyItem(id = 1, name = "Item Test", description = "Descripción")
    composeTestRule.setContent {
        MyItemCard(item = item)
    }

    composeTestRule
        .onNode(hasContentDescription("Item Test: Descripción"))
        .assertExists()
}
```
