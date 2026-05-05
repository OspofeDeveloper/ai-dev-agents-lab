# Bottom Navigation and Adaptive Navigation — Code Examples

## Canonical `AppNavGraph` signature

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

The `navController` is created in the shell, not inside `AppNavGraph`, so the navigation component (bottom bar / rail / drawer) and the `NavHost` share the same instance.

---

## Tab navigation options — shared helper

All three layouts use the same block. Extract it as a `NavOptionsBuilder` extension:

```kotlin
// :app/navigation/NavOptionsExt.kt
import androidx.navigation.NavOptionsBuilder

fun NavOptionsBuilder.tabSwitchOptions() {
    popUpTo<HomeRoute> { saveState = true }   // HomeRoute = NavHost startDestination
    launchSingleTop = true
    restoreState = true
}

// Usage in any layout:
navController.navigate(item.route) { tabSwitchOptions() }
```

---

## Adaptive `AppShell`

The shell creates the `navController` once and selects the navigation component based on screen size:

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
            modifier = Modifier.padding(innerPadding)   // innerPadding from Scaffold
        )
    }
}
```

---

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

---

## Permanent NavigationDrawer (Expanded)

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

All three components use `tabSwitchOptions()` — only the visual container changes.