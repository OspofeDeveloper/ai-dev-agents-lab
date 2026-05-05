# Navigation Testing — Code Examples

## `TestNavHostController` — graph integration (androidTest)

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

---

## Verify `navigate()` with the correct route (androidTest)

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

---

## Fake navigation for isolated ViewModel tests (commonTest)

```kotlin
class LoginViewModelTest {

    @Test
    fun onLoginSuccess_emitsLoginSuccess() = runTest {
        val viewModel = LoginViewModel(fakeAuthUseCase)

        val events = mutableListOf<LoginEvents>()
        val job = launch { viewModel.events.toList(events) }

        viewModel.onLoginSuccess()
        advanceUntilIdle()

        assertEquals(listOf(LoginEvents.LoginSuccess), events)
        job.cancel()
    }
}
```