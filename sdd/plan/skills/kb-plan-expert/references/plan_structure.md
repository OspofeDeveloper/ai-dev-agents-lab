# Plantilla de Output: Plan Técnico

Usa esta estructura para producir un Plan válido. Todos los campos marcados `[obligatorio]` son requeridos. Las tecnologías, módulos y capas concretas deben ser **coherentes con la estructura ya presente en el repositorio**, no impuestas por un framework que el repo no usa.

---

```markdown
# Plan: [Nombre de la Feature]
> **Versión:** 1.0
> **Spec origen:** [path/al/_spec.md]
> **PRD origen:** [path/al/PRD.md | unknown]
> **PRD version:** [1.0 | unknown]
> **Change ref:** [CR-XXX | N/A]
> **Status sync:** [in_sync | needs_review | stale | unknown]
> **Fecha:** [YYYY-MM-DD]
> **Estado:** [BORRADOR | VALIDADO]

---

## Stack Técnico [obligatorio]

Lista de tecnologías que se usan en esta feature, coherentes con las ya presentes en el repositorio.

| Área | Tecnología |
|---|---|
| Lenguaje / plataforma | [según el repo] |
| UI | [framework de UI del repo, si la feature tiene surface UI] |
| Red | [cliente HTTP del repo, si aplica] |
| Persistencia | [mecanismo de persistencia del repo, si aplica] |
| Inyección de dependencias | [mecanismo del repo, si aplica] |
| Async / concurrencia | [según el repo] |
| Tests | [framework de test del repo] |

---

## Estructura técnica [obligatorio]

Qué módulos, paquetes o carpetas se crean o modifican, coherentes con la organización existente del repo.

| Unidad (módulo / paquete / carpeta) | Estado | Descripción del cambio |
|---|---|---|
| `<unidad de la feature>` | NUEVO | Comportamiento, datos y presentación de la feature |
| `<unidad compartida existente>` | EXISTENTE | Sin cambios (o: cambio concreto) |
| `<punto de composición / entrada>` | MODIFICADO | Wiring, navegación o registro de dependencias |

---

## Diseño por responsabilidad [obligatorio]

Para cada unidad de la feature, describe sus responsabilidades técnicas separadas según las convenciones del repo.

### Dominio

#### Modelos

| Modelo | Campos | CAs que implementa |
|---|---|---|
| `NombreModel` | `id: ..., campo2: ...` | CA-001, CA-002 |

#### Contratos de acceso a datos

| Contrato | Operaciones | Firma de retorno |
|---|---|---|
| `NombreRepository` | `getSomething(param)` | `[tipo de retorno del repo]` |

#### Unidades de comportamiento (casos de uso / servicios)

| Unidad | Entrada | Retorno | CA que implementa |
|---|---|---|---|
| `NombreUseCase` | `param` | `[tipo de retorno]` | CA-001 |

### Datos

| Componente | Tipo | Responsabilidad |
|---|---|---|
| `NombreRemoteDataSource` | Remoto | Obtención remota |
| `NombreLocalDataSource` | Local | Persistencia local |
| `NombreRepositoryImpl` | Implementación | Implementa `NombreRepository` con estrategia [remote-first / cache-first / ...] |
| `NombreDto` + `Mapper` | Transferencia | Mapeo a/desde `NombreModel` |

### Presentación (si la feature tiene surface UI)

| Componente | Estado de UI | Eventos de UI | Pantalla asociada |
|---|---|---|---|
| `NombreViewModel` (o equivalente) | `NombreUiState` | `NombreUiEvent` | `NombreScreen` |

Describe los campos del estado de UI y las variantes de evento de forma coherente con el patrón de presentación del repo.

---

## Contratos y Dependencias [obligatorio]

- Qué tipos expone el dominio hacia la presentación
- Qué contratos implementa la capa de datos sobre el dominio
- Qué API exponen los componentes compartidos si se reutilizan

---

## Handoff desde Design [obligatorio si aplica]

### Artefactos usados

| Artefacto | Path | Uso en el Plan |
|---|---|---|
| `DESIGN.md` | `/path/DESIGN.md` | Sistema visual, accesibilidad, constraints de UI |
| `<feature>_flows.md` | `/path/<feature>_flows.md` | Journeys, transiciones, ownership de navegación |
| `<feature>_views.md` | `/path/<feature>_views.md` | Pantallas, estados, notas a11y y comportamiento visual |

### Decisiones materializadas

- Navegación o shell afectados: [sí/no + detalle]
- Semantic primitives / accesibilidad técnica: [detalle según el framework de UI del repo]
- Dependencias de plataforma derivadas del diseño: [ninguna | detalle]
- Contradicciones con design: [ninguna | lista como `DESIGN_GAP`]

---

## Decisiones de plataforma [omitir esta sección si no aplica]

Solo cuando un CA requiere una API de plataforma específica sin alternativa portable.

| API | Contrato | Implementación por plataforma |
|---|---|---|
| `NombrePlatformApi` | `[contrato y propósito]` | `[detalle por plataforma, coherente con el repo]` |

---

## Checklist de Trazabilidad [obligatorio]

| CA del Spec | Componente del Plan que lo implementa | Estado |
|---|---|---|
| CA-001: [descripción breve] | `NombreUseCase` + `NombreRepositoryImpl` | ✓ cubierto |
| CA-002: [descripción breve] | `NombreViewModel` (evento OnButtonClicked) | ✓ cubierto |
| CA-003: [descripción breve] | — | ✗ sin cobertura → [TECH_GAP] |

**CAs sin cobertura:** [ninguno | lista aquí los gaps]
**DESIGN_GAPs:** [ninguno | descripción de cada gap de design que bloquea el plan]
**TECH_GAPs:** [ninguno | descripción de cada gap que bloquea el plan]
**TRACE_GAPs:** [ninguno | descripción de cada gap de trazabilidad que bloquea el plan]
**PLAN_GAPs:** [ninguno | descripción de cada gap estructural del plan]
```
