# NavHost and Back Stack — Code Examples

## Basic NavHost in `commonMain`

```kotlin
// composeApp/src/commonMain/kotlin/com/example/app/navigation/AppNavGraph.kt
package com.example.app.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.toRoute

@Composable
fun AppNavGraph(
    navController: NavHostController,
    startDestination: Any = LoginRoute,
    modifier: Modifier = Modifier
) {
    NavHost(
        navController = navController,
        startDestination = startDestination,
        modifier = modifier
    ) {
        composable<LoginRoute> {
            LoginScreen(
                onNavigateToHome = {
                    navController.navigate(HomeRoute) {
                        popUpTo(LoginRoute) { inclusive = true }
                    }
                }
            )
        }

        composable<HomeRoute> {
            HomeScreen(
                onNavigateToProfile = { userId ->
                    navController.navigate(ProfileRoute(userId))
                },
                onNavigateToSettings = {
                    navController.navigate(SettingsRoute)
                }
            )
        }

        composable<ProfileRoute> { backStackEntry ->
            val route: ProfileRoute = backStackEntry.toRoute()
            ProfileScreen(
                userId = route.userId,
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
```

---

## Argument extraction with `toRoute()`

```kotlin
composable<DetailRoute> { backStackEntry ->
    val route: DetailRoute = backStackEntry.toRoute()
    DetailScreen(
        itemId = route.itemId,
        showComments = route.showComments
    )
}
```

---

## `rememberNavController()` — production vs test

`AppNavGraph` declares `navController` as a required parameter. The owner is always the caller — `AppShell` in production or the test that invokes it.

```kotlin
// Production: AppShell creates the navController and passes it down
@Composable
fun AppShell() {
    val navController = rememberNavController()
    AppNavGraph(navController = navController)
}

// Test: an external TestNavHostController is injected
composeTestRule.setContent {
    AppNavGraph(navController = testNavController)
}
```

---

## `popUpTo` + `inclusive`

```kotlin
// Login → Home: remove login from the back stack so Back does not return to login
navController.navigate(HomeRoute) {
    popUpTo(LoginRoute) { inclusive = true }
}

// Tab switching: return to the graph root, clearing the intermediate stack
navController.navigate(HomeRoute) {
    popUpTo<LoginRoute>()   // use the concrete startDestination of the NavHost
}
```

---

## `launchSingleTop`

```kotlin
navController.navigate(HomeRoute) {
    launchSingleTop = true  // does not create a duplicate if HomeRoute is already on top
}
```

---

## `saveState` / `restoreState`

```kotlin
navController.navigate(route) {
    saveState = true     // saves the back stack state of the current tab
    restoreState = true  // restores state if the tab was previously visited
    launchSingleTop = true
}
```

---

## `popBackStack()` with deep link fallback

```kotlin
// Screen that may be a deep link entry point
val popped = navController.popBackStack()
if (!popped) {
    // No back stack: navigate to home as fallback
    navController.navigate(HomeRoute) {
        launchSingleTop = true
    }
}
```