# Test 08 — `wf-prepare-plan`

**Propósito del workflow:** Traducir un spec de feature (autocontenido, con los 8 elementos SDD) a un plan técnico KMM con Clean Architecture. Es el primer paso que introduce decisiones técnicas en el pipeline.

---

## Prompt de activación

```
/wf-prepare-plan generate sdd/features/hogar/hogar_spec.md
```

---

## Flujo esperado paso a paso

### Paso 1 — El orquestador L1 parsea el comando
**Actor:** skill `wf-prepare-plan` (L1)
**Acción:** Lee `generate` y el path del spec de feature.
**Verifica precondiciones:**
- El archivo existe y es un `*_spec.md`
- El spec tiene estructura SDD reconocible (al menos Actores e HUs presentes)
- No verifica si el spec pasó por `validate` — confía en el usuario

**Señal de correcto:** El agente no hace decisiones técnicas aquí — solo delega.

---

### Paso 2 — El orquestador lanza el subagente `plan-architect`
**Actor:** skill `wf-prepare-plan` (L1)
**Acción:** Invoca `Agent(subagent_type="plan-architect")` con:
```
spec: <contenido del spec de feature>
feature_name: hogar
```

**Configuración importante del subagente:**
- `model: claude-opus-4-6` — este es el único agente del sistema que usa Opus
- `memory: project`
- `permissionMode: acceptEdits`

**Señal de correcto:** Se invoca `plan-architect`, NO `sdd-analyst`.

---

### Paso 3 — El subagente `plan-architect` carga su contexto
**Actor:** agente `plan-architect` (L2)
**Carga como contexto:**
- Knowledge `kb-spec-expert` — para hacer la Prueba de Trazabilidad (cada componente debe tener un CA que lo justifique)
- Knowledge `kb-plan-expert` — los 5 elementos obligatorios del Plan + reglas KMM
- Referencias de `kb-plan-expert`: `kmm_architecture.md` y `plan_structure.md`

---

### Paso 4 — El subagente genera el plan
**Actor:** agente `plan-architect` (L2), guiado por `kb-plan-expert` (L3)
**Acciones en orden:**

**4a. Declarar Stack Técnico:**
- KMM, Compose Multiplatform, Ktor, SQLDelight, Koin, Coroutines/Flow
- Solo añadir librerías adicionales si algún CA lo requiere explícitamente

**4b. Diseñar Mapa de Módulos Gradle:**
- `:feature:<nombre>` — módulo de la feature
- `:core:domain`, `:core:data`, `:core:network` — módulos compartidos si aplica
- `:app` — entry point

**4c. Diseño por Capa para cada componente:**
- **domain:** Models (data classes), Repository interfaces, UseCases
- **data:** DTOs, Mappers (DTO↔Model), DataSources (remote/local), RepositoryImpl
- **presentation:** ViewModel, UiState (sealed), UiEvent (sealed), Screen Composable

**4d. Aplicar Prueba de Trazabilidad a cada componente:**
> "¿Qué CA justifica que este componente exista?"
> - Hay CA → justificado, citar CA-XXX
> - No hay CA → especulativo → eliminar del plan

**4e. Definir Contratos entre capas:**
- Qué interfaces expone domain a presentation
- Qué interfaces expone data a domain

**4f. Decisiones Expect/Actual:**
- Listar las APIs platform-specific que necesitan implementación separada en Android/iOS
- P.ej: notificaciones push, permisos, sensores, almacenamiento local

**4g. Detectar TECH_GAPs:**
- Si hay ambigüedad funcional en el spec que impide una decisión técnica concreta
- Formato: `[TECH_GAP-001] descripción del gap técnico`
- Si hay TECH_GAPs: **no produce el plan completo** — lista los gaps y detiene

**Señal de correcto:** Cada componente del plan cita el CA que lo justifica. No hay componentes "por si acaso".

---

### Paso 5 — El subagente escribe el plan
**Actor:** agente `plan-architect` (L2)
**Archivo generado:** `features/hogar/hogar_plan.md`
**Contenido esperado:**
```
# Plan: Hogar

## Stack Técnico
...

## Módulos Gradle
...

## Domain Layer
### Models
- HogarModel: id, nombre, ... (justificado por CA-003, CA-007)

### Repository interfaces
- HogarRepository: getHogares(), addHogar() (justificado por CA-003)

### UseCases
- GetHogaresUseCase (justificado por CA-003)
- AddHogarUseCase (justificado por CA-005)

## Data Layer
### DTOs
### Mappers
### DataSources
### RepositoryImpl

## Presentation Layer
### ViewModel
### UiState
### UiEvent
### Screen

## Contratos entre capas
...

## Expect/Actual
...
```

---

## Resultado esperado

| Elemento | Valor |
|----------|-------|
| Archivo generado | `features/hogar/hogar_plan.md` |
| Bloqueo | Si hay TECH_GAPs: lista los gaps y no produce el plan |
| Modelo usado | `claude-opus-4-6` (verificar en logs si es posible) |
| Siguiente paso | `/wf-prepare-tasks generate features/hogar/hogar_plan.md` |

---

## Señales de fallo (qué validar)

- Se invoca `sdd-analyst` en vez de `plan-architect`
- El plan tiene componentes sin CA que los justifique
- El plan incluye terminología de negocio del spec (debería ser solo técnico)
- No declara el Stack Técnico completo
- No identifica las APIs expect/actual necesarias
- Produce el plan aunque haya TECH_GAPs que lo bloqueen
- El modelo usado es Sonnet en vez de Opus
