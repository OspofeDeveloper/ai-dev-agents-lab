# Reglas de Granularidad de Tasks

---

## Principio fundamental

> Una Task debe poder ser completada con una sola invocación de una skill KMM y producir archivos que compilen y sean coherentes con el resto del proyecto.

---

## Tamaño correcto por tipo de componente

| Componente | Tamaño recomendado | Skill | Notas |
|---|---|---|---|
| Scaffold de módulo | 1 Task por feature | `/kmm-scaffold` | Siempre T-000 |
| Un Model de domain | 1 Task (puede agrupar modelos relacionados simples) | `/kmm-domain` | Si son entidades independientes → Tasks separadas |
| Un Repository interface | 1 Task (junto con su Model si el Model es nuevo) | `/kmm-domain` | |
| Un UseCase | 1 Task | `/kmm-domain` | Un UseCase por acción principal |
| DTOs + Mapper de una entidad | 1 Task | `/kmm-data` | DTO y su mapper van juntos |
| Un DataSource remote | 1 Task | `/kmm-data` | Interfaz + implementación juntas |
| Un DataSource local | 1 Task | `/kmm-data` | Interfaz + implementación juntas |
| Un RepositoryImpl | 1 Task | `/kmm-data` | Puede necesitar dividirse si hay múltiples DataSources |
| Expect/actual de una API | 1 Task | `/kmm-expect-actual` | commonMain expect + androidMain actual + iosMain actual |
| ViewModel + UiState + UiEvent | 1 Task | `/kmm-presentation` | Los tres van siempre juntos |
| Screen Composable | 1 Task | `/kmm-presentation` | Separada del ViewModel |
| Tests de un UseCase | 1 Task | `/kmm-tests` | Happy path + error + edge cases |
| Tests de un RepositoryImpl | 1 Task | `/kmm-tests` | Mock DataSources, no red real |

---

## Señales de que una Task es demasiado grande

- La descripción contiene "y también" o "además"
- El campo "Input" menciona más de 2 entidades de negocio distintas
- La "Definition of done" lista más de 6 archivos
- La Task abarca más de una capa (domain Y data en la misma Task)

**Solución:** Divide en dos Tasks con dependencia explícita.

---

## Señales de que una Task es demasiado pequeña

- La Task solo crea un archivo de menos de 10 líneas reales
- La Task no puede compilar sola ni tiene utilidad sin otra Task inmediata e inseparable

**Solución:** Agrupa con la Task relacionada (DTO + su Mapper es una sola Task).

---

## Definition of Done por tipo de componente

| Tipo | Archivos que deben existir al completar |
|---|---|
| Scaffold | Directorios `domain/`, `data/`, `presentation/` + `build.gradle.kts` |
| Domain Model | `NombreModel.kt` en `domain/model/` — data class pura |
| Repository Interface | `NombreRepository.kt` en `domain/repository/` |
| UseCase | `NombreUseCase.kt` en `domain/usecase/` con `operator fun invoke()` |
| DTO + Mapper | `NombreDto.kt` en `data/remote/dto/` + `NombreMapper.kt` en `data/mapper/` |
| DataSource Remote | `NombreDataSource.kt` (interfaz) + `NombreDataSourceImpl.kt` (Ktor) |
| DataSource Local | `NombreDataSource.kt` (interfaz) + `NombreDataSourceImpl.kt` (SQLDelight) |
| RepositoryImpl | `NombreRepositoryImpl.kt` en `data/repository/` |
| Expect/Actual | `NombreApi.kt` en `commonMain/` + actual en `androidMain/` + actual en `iosMain/` |
| ViewModel | `NombreViewModel.kt` + `NombreUiState.kt` + `NombreUiEvent.kt` en `presentation/` |
| Screen | `NombreScreen.kt` en `presentation/screen/` |
| Tests UseCase | `NombreUseCaseTest.kt` en `commonTest/` |
| Tests Repository | `NombreRepositoryImplTest.kt` en `commonTest/` |

---

## Orden canónico detallado (dentro de cada feature)

```
1.  Scaffold del módulo
2.  Models de domain (dependencia base de todo)
3.  Repository interfaces (dependen de los Models)
4.  UseCases (dependen de las interfaces)
5.  DTOs + Mappers (dependen de los Models de domain)
6.  DataSources remote (dependen de los DTOs)
7.  DataSources local (si aplica, dependen de entidades locales)
8.  RepositoryImpl (dependen de interfaces + DataSources)
9.  Expect/Actual (si aplica, pueden ir después de domain)
10. ViewModel + State + Events (dependen de UseCases)
11. Screen Composable (depende del ViewModel)
12. Tests de domain (dependen de UseCases)
13. Tests de data (dependen de RepositoryImpl)
```
