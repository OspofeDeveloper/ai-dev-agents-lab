# BottomNavigation y Navegación Adaptativa — Ejemplos de Código

## Firma canónica de AppNavGraph

```kotlin
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
        composable<HomeRoute>  { HomeScreen(...) }
        composable<ProfileRoute> { ProfileScreen(...) }
    }
}
```

El `navController` se crea en el shell, no dentro de `AppNavGraph`, para que el componente de navegación (bottom bar / rail / drawer) y el NavHost compartan la misma instancia.

---

## Opciones de tab navigation — helper compartido

Los tres layouts usan el mismo bloque. Extráelo como extensión de `NavOptionsBuilder`:

```kotlin
// :app/navigation/NavOptionsExt.kt
import androidx.navigation.NavOptionsBuilder

fun NavOptionsBuilder.tabSwitchOptions() {
    popUpTo<HomeRoute> { saveState = true }   // HomeRoute = startDestination del NavHost
    launchSingleTop = true
    restoreState = true
}

// Uso en cualquier layout:
navController.navigate(item.route) { tabSwitchOptions() }
```

---

## AppShell adaptativo

El shell crea el `navController` una sola vez y selecciona el componente de navegación según el tamaño de pantalla:

```kotlin
import androidx.compose.material3.windowsizeclass.ExperimentalMaterial3WindowSizeClassApi
import androidx.compose.material3.windowsizeclass.WindowWidthSizeClass
import androidx.compose.material3.windowsizeclass.calculateWindowSizeClass

@OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
@Composable
fun AppShell() {
    val navController = rememberNavController()
    val windowSizeClass = calculateWindowSizeClass()

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact  -> CompactLayout(navController)   // NavigationBar
        WindowWidthSizeClass.Medium   -> MediumLayout(navController)    // NavigationRail
        WindowWidthSizeClass.Expanded -> ExpandedLayout(navController)  // NavigationDrawer
    }
}
```

---

## NavigationBar (Compact)

```kotlin
@Composable
fun CompactLayout(navController: NavHostController) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    Scaffold(
        bottomBar = {
            NavigationBar {
                navItems.forEach { item ->
                    NavigationBarItem(
                        selected = currentDestination?.hierarchy?.any {
                            it.hasRoute(item.route::class)
                        } == true,
                        onClick = {
                            navController.navigate(item.route) { tabSwitchOptions() }
                        },
                        icon = { Icon(item.icon, contentDescription = item.label) },
                        label = { Text(item.label) }
                    )
                }
            }
        }
    ) { innerPadding ->
        AppNavGraph(
            navController = navController,
            modifier = Modifier.padding(innerPadding)   // innerPadding del Scaffold
        )
    }
}
```

## NavigationRail (Medium)

```kotlin
@Composable
fun MediumLayout(navController: NavHostController) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    Row(modifier = Modifier.fillMaxSize()) {
        NavigationRail {
            navItems.forEach { item ->
                NavigationRailItem(
                    selected = currentDestination?.hierarchy?.any {
                        it.hasRoute(item.route::class)
                    } == true,
                    onClick = {
                        navController.navigate(item.route) { tabSwitchOptions() }
                    },
                    icon = { Icon(item.icon, contentDescription = item.label) },
                    label = { Text(item.label) }
                )
            }
        }
        AppNavGraph(navController = navController)
    }
}
```

## NavigationDrawer permanente (Expanded)

```kotlin
@Composable
fun ExpandedLayout(navController: NavHostController) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    PermanentNavigationDrawer(
        drawerContent = {
            PermanentDrawerSheet {
                navItems.forEach { item ->
                    NavigationDrawerItem(
                        selected = currentDestination?.hierarchy?.any {
                            it.hasRoute(item.route::class)
                        } == true,
                        onClick = {
                            navController.navigate(item.route) { tabSwitchOptions() }
                        },
                        icon = { Icon(item.icon, null) },
                        label = { Text(item.label) }
                    )
                }
            }
        }
    ) {
        AppNavGraph(navController = navController)
    }
}
```

Los tres componentes usan `tabSwitchOptions()` — solo cambia el contenedor visual.