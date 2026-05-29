# Unit Test Templates — KMM

> Arquitectura y política: `kb-kmm-testing-strategy`.
> Para patrones de navegación en tests: `kb-kmm-navigation-compose/references/testing.md` (SSoT — no duplicar aquí).
> Para aserciones sobre UIText: `kb-tasks-kmm-ui-text` Regla 8 (SSoT — no duplicar aquí).

## Template: ViewModel con StateFlow

```kotlin
class MyViewModelTest {
    @Test
    fun `descripcion del comportamiento esperado`() = runTest {
        // Arrange
        val fakeRepo = FakeMyRepository()
        val viewModel = MyViewModel(GetMyItemsUseCase(fakeRepo))

        // Act + Assert via Turbine
        viewModel.state.test {
            assertEquals(MyState.Loading, awaitItem())
            val state = awaitItem()
            assertIs<MyState.Success>(state)
            assertEquals(expectedSize, state.items.size)
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

## Template: ViewModel con Channel de Events

```kotlin
@Test
fun `cuando ocurre una acción, se emite el evento correcto`() = runTest {
    // Arrange
    val fakeRepo = FakeMyRepository()
    val viewModel = MyViewModel(fakeRepo)

    // Act
    viewModel.onEvent(MyIntent.DoAction)
    advanceUntilIdle()

    // Assert
    viewModel.events.test {
        val event = awaitItem()
        assertIs<MyEvents.NavigateToDetail>(event)
        cancelAndIgnoreRemainingEvents()
    }
}
```

## Template: UseCase con fake Repository

```kotlin
class GetMyItemsUseCaseTest {
    @Test
    fun `happy path devuelve lista de items`() = runTest {
        // Arrange
        val fakeRepo = FakeMyRepository()
        fakeRepo.items = listOf(MyItem(id = 1, name = "Test"))
        val useCase = GetMyItemsUseCase(fakeRepo)

        // Act
        val result = useCase()

        // Assert
        assertIs<AppResult.Success<List<MyItem>>>(result)
        assertEquals(1, result.data.size)
    }

    @Test
    fun `cuando el repositorio falla, propaga AppError`() = runTest {
        // Arrange
        val fakeRepo = FakeMyRepository()
        fakeRepo.shouldFail = true
        val useCase = GetMyItemsUseCase(fakeRepo)

        // Act
        val result = useCase()

        // Assert
        assertIs<AppResult.Error<AppError>>(result)
    }
}
```

## Template: RepositoryImpl con fake DataSource

```kotlin
class MyRepositoryImplTest {
    @Test
    fun `mapea DTO de DataSource remoto a modelo de dominio`() = runTest {
        // Arrange
        val fakeRemote = FakeMyRemoteDataSource()
        fakeRemote.response = listOf(MyDto(id = 1, name = "Test"))
        val repo = MyRepositoryImpl(fakeRemote)

        // Act
        val result = repo.getItems()

        // Assert
        assertIs<AppResult.Success<List<MyItem>>>(result)
        assertEquals("Test", result.data.first().name)
    }
}
```

## Template: Fake base

```kotlin
class FakeMyRepository : MyRepository {
    var items: List<MyItem> = emptyList()
    var shouldFail: Boolean = false
    var errorToThrow: AppError = AppError.Unknown

    override suspend fun getItems(): AppResult<List<MyItem>, AppError> =
        if (shouldFail) AppResult.Error(errorToThrow)
        else AppResult.Success(items)
}
```
