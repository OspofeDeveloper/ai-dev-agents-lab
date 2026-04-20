# Testing de navegación — Ejemplos de Código

## `TestNavHostController` — integración del grafo (androidTest)

```kotlin
// androidApp/src/androidTest/kotlin/com/example/app/navigation/AppNavGraphTest.kt
import androidx.navigation.testing.TestNavHostController
import androidx.compose.ui.test.junit4.createComposeRule

class AppNavGraphTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_onSuccess_navigatesToHome() {
        val navController = TestNavHostController(
            InstrumentationRegistry.getInstrumentation().targetContext
        )

        composeTestRule.setContent {
            AppNavGraph(navController = navController)
        }

        composeTestRule.onNodeWithText("Log In").performClick()

        assertEquals(
            HomeRoute::class.qualifiedName,
            navController.currentBackStackEntry?.destination?.route
        )
    }
}
```

## Verificar `navigate()` con la ruta correcta (androidTest)

```kotlin
@Test
fun homeScreen_onProfileClick_navigatesToProfile() {
    val navController = TestNavHostController(
        InstrumentationRegistry.getInstrumentation().targetContext
    )

    composeTestRule.setContent {
        HomeScreen(
            onNavigateToProfile = { userId ->
                navController.navigate(ProfileRoute(userId))
            }
        )
    }

    composeTestRule.onNodeWithTag("profile_button").performClick()

    val currentRoute = navController.currentBackStackEntry?.toRoute<ProfileRoute>()
    assertNotNull(currentRoute)
    assertEquals("user_123", currentRoute?.userId)
}
```

## Fake navigation para aislar ViewModels (commonTest)

```kotlin
class LoginViewModelTest {

    @Test
    fun onLoginSuccess_emitsLoginSuccess() = runTest {
        val viewModel = LoginViewModel(fakeAuthUseCase)

        val effects = mutableListOf<LoginEffect>()
        val job = launch { viewModel.effect.toList(effects) }

        viewModel.onLoginSuccess()
        advanceUntilIdle()

        assertEquals(listOf(LoginEffect.LoginSuccess), effects)
        job.cancel()
    }
}
```
