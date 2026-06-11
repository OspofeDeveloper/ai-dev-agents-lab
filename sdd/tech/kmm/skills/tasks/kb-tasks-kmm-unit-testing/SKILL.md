---
name: kb-tasks-kmm-unit-testing
description: "Patrones de implementación de tests unitarios en proyectos KMM: tests de ViewModel con runTest + Turbine, tests de UseCase con fakes, tests de RepositoryImpl con fakes de DataSource. Aserciones en kotlin.test, estructura Arrange/Act/Assert. Cargada por kmm-feature-logic-implementer, kmm-feature-ui-implementer, kmm-network-auth-implementer y kmm-tester."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Tests Unitarios KMM — Patrones de Implementación

> Decisiones arquitectónicas de cuándo y por qué testear: `kb-kmm-testing-strategy`.

## Regla 1: Tests de ViewModel usan runTest + Turbine + fakes inyectados por constructor

El ViewModel recibe sus dependencias (repositorios, casos de uso) por constructor en el test. No se usa Koin ni ningún framework de DI en tests.

```kotlin
@Test
fun `cuando se carga la lista, el estado pasa a Success con los items`() = runTest {
    // Arrange
    val fakeRepo = FakeItemRepository()
    fakeRepo.items = listOf(Item(1, "Item 1"))
    val viewModel = ItemListViewModel(GetItemsUseCase(fakeRepo))

    // Act + Assert con Turbine
    viewModel.state.test {
        val initial = awaitItem()
        assertEquals(ItemListState.Loading, initial)
        val success = awaitItem()
        assertTrue(success is ItemListState.Success)
        assertEquals(1, (success as ItemListState.Success).items.size)
        cancelAndIgnoreRemainingEvents()
    }
}
```

**Para eventos del Channel:** usar `awaitItem()` de Turbine sobre el Flow de eventos, o consumir con `toList()` tras `advanceUntilIdle()` si el canal tiene buffer.

**Para aserciones sobre UIText en el ViewModel:** la regla vive en `kb-tasks-kmm-ui-text` Regla 8. Esta skill no la duplica: los tests comparan valores `UIText` directamente, sin resolver strings.

Consulta `${CLAUDE_SKILL_DIR}/references/unit-test-templates.md` para templates completos.

---

## Regla 2: Tests de UseCase validan lógica de negocio, no plumbing

Un test de UseCase:
1. crea fakes de los repositorios que necesita
2. llama al UseCase con inputs de test
3. afirma sobre el modelo de dominio devuelto o el tipo de error (`AppResult<T, AppError>`)

No testea que el fake fue llamado con los parámetros correctos (eso es comportamiento de mock). Testea el resultado o la transformación del UseCase.

```kotlin
@Test
fun `cuando el repositorio falla, el UseCase propaga el error`() = runTest {
    val fakeRepo = FakeItemRepository()
    fakeRepo.shouldFail = true
    val useCase = GetItemsUseCase(fakeRepo)

    val result = useCase()

    assertTrue(result is AppResult.Error)
}
```

---

## Regla 3: Tests de RepositoryImpl usan fakes de DataSource

El RepositoryImpl recibe fakes de sus DataSources por constructor. Los fakes de DataSource remoto retornan `AppResult<T, AppError>` o listas/modelos de dominio según el contrato del proyecto. Sin red real, sin filesystem.

```kotlin
@Test
fun `cuando el DataSource remoto tiene datos, el repositorio los mapea a dominio`() = runTest {
    val fakeRemote = FakeItemRemoteDataSource()
    fakeRemote.response = listOf(ItemDto(id = 1, name = "Item 1"))
    val repo = ItemRepositoryImpl(fakeRemote)

    val result = repo.getItems()

    assertTrue(result is AppResult.Success)
    assertEquals(1, (result as AppResult.Success).data.size)
}
```

---

## Regla 4: Fakes en `commonTest/fakes/`, nombrados `Fake<NombreInterfaz>`

Los fakes implementan la interfaz completa. Para controlar el comportamiento del fake en el test, exponer propiedades mutables en el fake:

```kotlin
class FakeItemRepository : ItemRepository {
    var items: List<Item> = emptyList()
    var shouldFail: Boolean = false

    override suspend fun getItems(): AppResult<List<Item>, AppError> {
        return if (shouldFail) AppResult.Error(AppError.Unknown)
        else AppResult.Success(items)
    }
}
```

---

## Regla 5: `kotlin.test` es el SSoT para aserciones en commonTest

Usar exclusivamente `kotlin.test`:
- `assertEquals(expected, actual)`
- `assertTrue(condition)`
- `assertFalse(condition)`
- `assertNotNull(value)`
- `assertNull(value)`
- `assertIs<Type>(value)`

No importar JUnit4 (`org.junit.Assert`) en archivos de `commonTest`. JUnit4 puede usarse en `androidTest`.

---

## Regla 6: Estructura Arrange / Act / Assert obligatoria

Cada método de test debe tener los tres bloques claramente delimitados. Usar comentarios `// Arrange`, `// Act`, `// Assert` cuando el test tiene más de 5 líneas. En tests cortos, la estructura puede ser implícita pero mantenerse en el mismo orden.

Esta estructura mapea directamente al ciclo RED-GREEN-REFACTOR a nivel de test individual: el Arrange prepara el estado RED, el Act ejecuta el componente, el Assert verifica el resultado GREEN esperado.
