# NavHost y Back Stack — Ejemplos de Código

## NavHost básico en commonMain

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

## Extracción de argumentos con `toRoute()`

```kotlin
composable<DetailRoute> { backStackEntry ->
    val route: DetailRoute = backStackEntry.toRoute()
    DetailScreen(
        itemId = route.itemId,
        showComments = route.showComments
    )
}
```

## `rememberNavController()` — producción vs test

`AppNavGraph` declara `navController` como parámetro requerido. El owner es siempre el caller — `AppShell` en producción o el test que lo invoca.

```kotlin
// Producción: AppShell crea el navController y lo pasa
@Composable
fun AppShell() {
    val navController = rememberNavController()
    AppNavGraph(navController = navController)
}

// Test: se inyecta un TestNavHostController externo
composeTestRule.setContent {
    AppNavGraph(navController = testNavController)
}
```

---

## `popUpTo` + `inclusive`

```kotlin
// Login → Home: eliminar el login del back stack para que Back no vuelva a login
navController.navigate(HomeRoute) {
    popUpTo(LoginRoute) { inclusive = true }
}

// Tab switching: volver a la raíz del grafo actual limpiando el stack intermedio
navController.navigate(HomeRoute) {
    popUpTo<LoginRoute>()   // usar el startDestination concreto del NavHost
}
```

## `launchSingleTop`

```kotlin
navController.navigate(HomeRoute) {
    launchSingleTop = true  // no crea duplicado si HomeRoute ya está en el top
}
```

## `saveState` / `restoreState`

```kotlin
navController.navigate(route) {
    saveState = true     // guarda el state del back stack de la tab actual
    restoreState = true  // restaura el state si la tab ya fue visitada
    launchSingleTop = true
}
```

## `popBackStack()` con fallback para deep links

```kotlin
// Pantalla que puede ser entry point de deep link
val popped = navController.popBackStack()
if (!popped) {
    // No había back stack: navegar al home como fallback
    navController.navigate(HomeRoute) {
        launchSingleTop = true
    }
}
```
