# Transition Animations — Code Examples

## Global transitions in `NavHost`

```kotlin
NavHost(
    navController = navController,
    startDestination = LoginRoute,
    enterTransition = {
        slideIntoContainer(
            towards = AnimatedContentTransitionScope.SlideDirection.Start,
            animationSpec = tween(300)
        )
    },
    exitTransition = {
        slideOutOfContainer(
            towards = AnimatedContentTransitionScope.SlideDirection.Start,
            animationSpec = tween(300)
        )
    },
    popEnterTransition = {
        slideIntoContainer(
            towards = AnimatedContentTransitionScope.SlideDirection.End,
            animationSpec = tween(300)
        )
    },
    popExitTransition = {
        slideOutOfContainer(
            towards = AnimatedContentTransitionScope.SlideDirection.End,
            animationSpec = tween(300)
        )
    }
) { ... }
```

## Per-route transitions

Override the global transitions for a specific route:

```kotlin
composable<ModalRoute>(
    enterTransition = {
        slideIntoContainer(AnimatedContentTransitionScope.SlideDirection.Up)
    },
    exitTransition = { fadeOut() },
    popEnterTransition = { EnterTransition.None },
    popExitTransition = {
        slideOutOfContainer(AnimatedContentTransitionScope.SlideDirection.Down)
    }
) { ModalScreen() }
```