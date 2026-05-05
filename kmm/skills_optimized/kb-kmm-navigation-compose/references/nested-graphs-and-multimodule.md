# Nested Graphs and Multi-module — Code Examples

## Nested NavGraph

```kotlin
NavHost(navController = navController, startDestination = AuthGraph) {

    // Authentication nested graph
    navigation<AuthGraph>(startDestination = LoginRoute) {
        composable<LoginRoute> { LoginScreen(...) }
        composable<RegisterRoute> { RegisterScreen(...) }
        composable<ForgotPasswordRoute> { ForgotPasswordScreen(...) }
    }

    // Main nested graph
    navigation<MainGraph>(startDestination = HomeRoute) {
        composable<HomeRoute> { HomeScreen(...) }
        composable<ProfileRoute> { backStackEntry ->
            val route: ProfileRoute = backStackEntry.toRoute()
            ProfileScreen(userId = route.userId, ...)
        }
    }
}
```

---

## Navigating to a graph vs a specific route

```kotlin
// Navigate to a nested graph (lands on its startDestination)
navController.navigate(MainGraph)

// Navigate to a specific route within the graph (regardless of which graph it belongs to)
navController.navigate(ProfileRoute(userId = "123"))
```

---

## Feature module with an independent graph

Routes live in `:app/navigation/`, not in `:core`. Features do not reference navigation destinations — they emit callbacks — so they have no need to know the routes. The `NavController` never leaves `:app`.

```kotlin
// :app/navigation/AppNavGraph.kt — extension defined in :app, not in the feature
fun NavGraphBuilder.authGraph(onAuthComplete: () -> Unit) {
    navigation<AuthGraph>(startDestination = LoginRoute) {
        composable<LoginRoute> {
            LoginScreen(onSuccess = onAuthComplete)
        }
    }
}

// :app NavHost — feature graph composition
NavHost(navController, startDestination = AuthGraph) {
    authGraph(onAuthComplete = {
        navController.navigate(MainGraph) {
            popUpTo(AuthGraph) { inclusive = true }
        }
    })
    mainGraph(
        onNavigateToProfile = { userId ->
            navController.navigate(ProfileRoute(userId))
        }
    )
}
```

---

## Module structure

Routes live in `:app`, not in `:core`. `core/` contains nothing related to navigation.

```
:app/navigation/
  AppRoutes.kt        ← all routes (@Serializable or sealed class)
  AppNavGraph.kt      ← NavHost + NavGraphBuilder extensions
```

Correct dependencies — features never depend on each other or on navigation routes:

```
:app           → depends on :feature:auth, :feature:home, :core
:feature:auth  → depends on :core
:feature:home  → depends on :core
```

---

## Graph registration in `:app`

```kotlin
NavHost(navController, startDestination = AuthGraph) {
    authGraph(
        onAuthComplete = {
            navController.navigate(MainGraph) {
                popUpTo(AuthGraph) { inclusive = true }
            }
        }
    )
    homeGraph(
        onNavigateToProfile = { userId ->
            navController.navigate(ProfileRoute(userId))
        }
    )
    profileGraph(
        onNavigateBack = { navController.popBackStack() }
    )
}
```

Each feature exposes its screens as composables. The `NavGraphBuilder.featureGraph(...)` extensions are defined in `:app` and receive only lambdas for exit actions. A feature **never** receives the `NavController` — it only emits callbacks.