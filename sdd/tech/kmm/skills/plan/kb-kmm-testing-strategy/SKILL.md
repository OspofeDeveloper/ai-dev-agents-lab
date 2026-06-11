---
name: kb-kmm-testing-strategy
description: "Estrategia de testing para proyectos KMM: pirámide de tests, propiedad por capa, ciclo TDD RED-GREEN-REFACTOR, asignación a source sets y política de test doubles. Define cuándo y qué probar, sin prescribir implementación concreta."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Estrategia de Testing KMM — Base de Conocimiento

## Regla 1: La propiedad de un test sigue la propiedad de su sujeto

Cada agente KMM es responsable de los tests de los componentes que implementa:

- `kmm-feature-logic-implementer` — tests de UseCases y RepositoryImpl propios de la feature (capas `domain`/`data`)
- `kmm-feature-ui-implementer` — tests de ViewModels propios de la feature (capa `presentation`)
- `kmm-platform-integrator` — tests de grafo de navegación, wiring de app y screenshots
- `kmm-network-auth-implementer` — tests de contratos de red, autenticación e integración cross-layer de infraestructura
- `kmm-tester` — agente especializado en diseñar, escribir y auditar tests de cualquier tipo cuando el scope es exclusivamente de testing

Esta regla decide el owner agent de cualquier task de test en el `_tasks.md`.

---

## Regla 2: La pirámide de testing mapea a source sets KMM

La granularidad de testing sigue la estructura de source sets del proyecto:

- **`commonTest`**: lógica pura sin dependencias de plataforma — UseCases, Repositories con fakes, ViewModels con turbine. Es el source set más amplio y prioritario.
- **`androidTest`**: tests instrumentados que requieren runtime Compose o APIs de plataforma — composeTestRule, TestNavHostController, Roborazzi. No usar para tests que puedan correr en commonTest.
- **`iosTest`**: comportamiento específico de plataforma iOS — APIs nativas, expect/actual de plataforma.

**Regla de colocación:** el test debe vivir en el source set más compartido donde pueda ejecutarse correctamente. Un test que solo usa interfaces puras de dominio pertenece a commonTest aunque su sujeto sea una feature con UI.

---

## Regla 3: El ciclo TDD es RED-GREEN-REFACTOR por componente testable

Toda task que crea un componente testable (UseCase, RepositoryImpl, ViewModel) tiene una task de test correspondiente con número de orden menor en el `_tasks.md`.

La task de test tiene:
- `Layer: test`
- `Execution domain` igual al del componente que testa
- una entrada en `Dependencies` de la task de implementación correspondiente

**Definition of Done de una task RED**: el archivo de test existe, compila, y falla con un mensaje claro que indica la ausencia de implementación. No se exige que pase.

La task de implementación (GREEN) no puede cerrarse sin que la task de test correspondiente esté definida y entregada. El REFACTOR es parte del cierre de la task de implementación o una task separada si hay deuda técnica significativa.

Los patrones de implementación del ciclo TDD viven en `kb-tasks-kmm-unit-testing` y `kb-tasks-kmm-integration-testing`.

---

## Regla 4: Fakes escritos a mano sobre mocks — política de proyecto

La política de test doubles en proyectos KMM es **fakes sobre mocks**:

- Un fake es una implementación in-memory de una interfaz, escrita a mano, que vive en `commonTest/fakes/`.
- Los fakes implementan la interfaz completa y se reutilizan entre suites de test.
- No se usan librerías de mocking (MockK, Mockative) salvo que el tamaño de la interfaz haga inviable el fake manual y se justifique explícitamente.

Esta política permite que los tests de dominio corran en `commonTest` sin dependencias de plataforma.

---

## Regla 5: Los fakes viven en `commonTest/fakes/` con nombre `Fake<NombreInterfaz>`

Convención de ubicación y nombrado:

- directorio: `commonTest/fakes/`
- nombre de clase: `Fake<NombreInterfaz>` (ej: `FakeUserRepository`, `FakeAuthDataSource`)
- los fakes de navegación siguen la convención establecida en `${CLAUDE_SKILL_DIR}/../../tasks/kb-kmm-navigation-compose/references/testing.md` — esa skill es el SSoT para FakeNavigation y navegación en tests, esta skill no la duplica.

Un stub parcial (que solo implementa la superficie que ejercita el test) es válido solo cuando la interfaz es muy amplia y el test cubre una fracción conocida. Debe marcarse como `Stub` en el nombre, no `Fake`.

---

## Regla 6: Herramientas de test por source set

| Source set | Herramientas |
|---|---|
| `commonTest` | `kotlin.test`, `kotlinx-coroutines-test`, Turbine |
| `androidTest` | `compose-ui-test` (composeTestRule), Roborazzi |
| `iosTest` | `kotlin.test`, APIs nativas vía expect/actual |

**Turbine** es la librería canónica para colectar emisiones de Flow y StateFlow en tests. No sustituir por patrones manuales de `toList()` con canal.

Los patrones de implementación concretos con estas herramientas viven en:
- `kb-tasks-kmm-unit-testing` — patrones de unit test para commonTest
- `kb-tasks-kmm-integration-testing` — patrones de integration test para androidTest

---

## Regla 7: Cobertura mínima por tipo de componente

Todo plan de feature debe incluir tests para:

| Componente | Test mínimo requerido |
|---|---|
| UseCase | Test en commonTest del happy path y al menos un error path |
| RepositoryImpl | Test en commonTest con fake DataSource (happy path) |
| ViewModel | Test en commonTest del happy path de State y al menos un evento de Events |
| Screen Composable | Test en androidTest con composeTestRule solo cuando el spec CA cubre un user journey de UI explícito |

Si el plan omite alguno de estos tests, el task-generator debe añadirlos antes de cerrar la lista de tasks.

---

## Regla 8: Esta skill no redefine criterios de accesibilidad ni diseño visual

Los criterios de accesibilidad que deben verificarse con tests provienen de `kb-plan-expert`. Esta skill no los duplica.

Los patrones de implementación de tests de accesibilidad (useUnmergedTree, hasContentDescription) viven en `kb-tasks-kmm-integration-testing`.

La estrategia de screenshot testing (cuándo hacer screenshots, golden files, CI) la define `kb-tasks-kmm-integration-testing`, no esta skill.
