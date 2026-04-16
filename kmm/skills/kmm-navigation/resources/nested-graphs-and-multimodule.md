# Nested Graphs y Multi-módulo — Ejemplos de Código

## Nested NavGraph

```kotlin
NavHost(navController = navController, startDestination = AuthGraph) {

    // Nested graph de autenticación
    navigation<AuthGraph>(startDestination = LoginRoute) {
        composable<LoginRoute> { LoginScreen(...) }
        composable<RegisterRoute> { RegisterScreen(...) }
        composable<ForgotPasswordRoute> { ForgotPasswordScreen(...) }
    }

    // Nested graph principal
    navigation<MainGraph>(startDestination = HomeRoute) {
        composable<HomeRoute> { HomeScreen(...) }
        composable<ProfileRoute> { backStackEntry ->
            val route: ProfileRoute = backStackEntry.toRoute()
            ProfileScreen(userId = route.userId, ...)
        }
    }
}
```

## Navegar al graph vs a una ruta específica

```kotlin
// Navegar al nested graph (aterriza en su startDestination)
navController.navigate(MainGraph)

// Navegar a una ruta específica dentro del graph (sin importar en qué graph está)
navController.navigate(ProfileRoute(userId = "123"))
```

## Feature module con grafo independiente

Las rutas viven en `:app/navigation/`, no en `:core`. Las features no referencian destinos de navegación — emiten callbacks — por lo que no necesitan conocer las rutas. El `NavController` nunca sale de `:app`.

```kotlin
// :app/navigation/AppNavGraph.kt — extensión definida en :app, no en la feature
fun NavGraphBuilder.authGraph(onAuthComplete: () -> Unit) {
    navigation<AuthGraph>(startDestination = LoginRoute) {
        composable<LoginRoute> {
            LoginScreen(onSuccess = onAuthComplete)
        }
    }
}

// :app NavHost — composición de grafos de features
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

## Estructura de módulos

Las rutas viven en `:app`, no en `:core`. `core/` no contiene nada de navegación.

```
:app/navigation/
  AppRoutes.kt        ← todas las rutas (@Serializable o sealed class)
  AppNavGraph.kt      ← NavHost + extensiones NavGraphBuilder
```

Dependencias correctas — features nunca dependen entre sí ni de rutas de navegación:

```
:app           → depende de :feature:auth, :feature:home, :core
:feature:auth  → depende de :core
:feature:home  → depende de :core
```

## Registro de grafos en `:app`

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

Cada feature expone sus screens como composables. Las extensiones `NavGraphBuilder.featureGraph(...)` se definen en `:app` y reciben únicamente lambdas para las acciones de salida. El feature **nunca** recibe el `NavController` — solo emite callbacks.