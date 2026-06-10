# Reglas de Granularidad de Tasks

---

## Principio fundamental

> Una Task debe poder ser completada por un único agente KMM owner y producir artefactos coherentes con el resto del proyecto.

---

## Tamaño correcto por tipo de componente

El owner por defecto se decide por el `Layer` del componente (ver routing en `kb-tasks-expert`): Model/Repo-int/UseCase → `domain`; DTO+Mapper/DataSource/RepositoryImpl → `data`; ambos → `kmm-feature-logic-implementer`. ViewModel/Screen → `presentation` → `kmm-feature-ui-implementer`. Scaffold/expect-actual/navgraph → `platform`/`app` → `kmm-platform-integrator`. Remoto transversal/`core` → `kmm-network-auth-implementer`. Tests → implementador de la capa del componente, o `kmm-tester` en suites dedicadas.

| Componente | Tamaño recomendado | Owner agent por defecto | Notas |
|---|---|---|---|
| Scaffold de módulo o wiring base | 1 Task por feature o bloque estructural | `kmm-platform-integrator` | Siempre T-000 |
| Un Model de feature | 1 Task (puede agrupar modelos relacionados simples) | `kmm-feature-logic-implementer` | `Layer: domain`. Si son entidades independientes → Tasks separadas |
| Un Repository interface de feature | 1 Task | `kmm-feature-logic-implementer` | `Layer: domain`. Puede agruparse con el Model si es inseparable |
| Un UseCase | 1 Task | `kmm-feature-logic-implementer` | `Layer: domain`. Un UseCase por acción principal |
| DTOs + Mapper de una entidad de feature | 1 Task | `kmm-feature-logic-implementer` | `Layer: data`. DTO y mapper van juntos |
| Un DataSource remote compartido o transversal | 1 Task | `kmm-network-auth-implementer` | Si vive en `core` o sirve a varias features |
| Un DataSource remote específico de feature | 1 Task | `kmm-feature-logic-implementer` | `Layer: data`. Si es borde remoto de una sola feature (frontera remota H2) |
| Un DataSource local | 1 Task | `kmm-feature-logic-implementer` | `Layer: data`. Interfaz + implementación juntas |
| Un RepositoryImpl | 1 Task | `kmm-feature-logic-implementer` | `Layer: data`. Puede necesitar dividirse si hay múltiples DataSources |
| Expect/actual o bridge de plataforma | 1 Task | `kmm-platform-integrator` | `Layer: platform`. commonMain + androidMain + iosMain |
| ViewModel + UiState + UiEvent | 1 Task | `kmm-feature-ui-implementer` | `Layer: presentation`. Los tres van siempre juntos |
| Screen Composable | 1 Task | `kmm-feature-ui-implementer` | `Layer: presentation`. Separada del ViewModel |
| NavGraph / rutas / wiring de app | 1 Task | `kmm-platform-integrator` | `Layer: app`. No pertenece al feature por sí solo |
| Tests de un UseCase | 1 Task | `kmm-feature-logic-implementer` | `Layer: test`. Happy path + error + edge cases (o `kmm-tester` si es suite dedicada) |
| Tests de un RepositoryImpl | 1 Task | `kmm-feature-logic-implementer` | `Layer: test`. Fakes de DataSources, no red real |
| Tests de un ViewModel | 1 Task | `kmm-feature-ui-implementer` | `Layer: test`. runTest + Turbine (o `kmm-tester` si es suite dedicada) |

---

## Señales de que una Task es demasiado grande

- La descripción contiene "y también" o "además"
- El campo `Input` menciona más de 2 entidades de negocio distintas
- La `Definition of done` lista más de 6 artefactos significativos
- La Task mezcla dos owner agents potenciales

**Solución:** divide en dos Tasks con dependencia explícita y owner agent distinto si hace falta.

---

## Señales de que una Task es demasiado pequeña

- La Task solo crea un archivo de menos de 10 líneas reales
- La Task no puede compilar ni tener valor sin otra Task inmediata e inseparable

**Solución:** agrupa con la Task relacionada.

---

## Definition of Done por tipo de componente

| Tipo | Artefactos que deben existir al completar |
|---|---|
| Scaffold | Directorios estructurales + `build.gradle.kts` o wiring base actualizado |
| Domain Model | `NombreModel.kt` en `domain/model/` — data class pura |
| Repository Interface | `NombreRepository.kt` en `domain/repository/` |
| UseCase | `NombreUseCase.kt` en `domain/usecase/` con `operator fun invoke()` |
| DTO + Mapper | `NombreDto.kt` + `NombreMapper.kt` |
| DataSource Remote | interfaz + implementación remota coherente con el borde de red definido |
| DataSource Local | interfaz + implementación local coherente con la persistencia elegida |
| RepositoryImpl | `NombreRepositoryImpl.kt` en `data/repository/` |
| Expect/Actual | `expect` en `commonMain` + `actual` en plataformas requeridas |
| ViewModel | `NombreViewModel.kt` + `NombreUiState.kt` + `NombreUiEvent.kt` |
| Screen | `NombreScreen.kt` en `presentation/screen/` |
| Navigation | grafo, rutas o wiring de navegación integrados en `app` o módulo correspondiente |
| Tests UseCase | `NombreUseCaseTest.kt` en `commonTest/` o suite equivalente |
| Tests Repository | `NombreRepositoryImplTest.kt` en `commonTest/` o suite equivalente |

---

## Orden canónico detallado (dentro de cada feature)

```text
1.  Scaffold / wiring base
2.  Models de domain
3.  Repository interfaces
4.  UseCases
5.  DTOs + Mappers de feature
6.  DataSources remote/local de feature
7.  Infraestructura remota o auth transversal (si aplica)
8.  RepositoryImpl
9.  Expect/Actual o bridges de plataforma
10. ViewModel + State + Events
11. Screen Composable
12. Navegación / wiring de app
13. Tests de domain
14. Tests de data
```
