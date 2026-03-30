# Test 09 — `prepare-tasks`

**Propósito del workflow:** Descomponer un plan técnico KMM (`*_plan.md`) en tasks atómicas, ordenadas, con dependencias explícitas y asignadas a skills de implementación. Es el último paso antes de la implementación.

---

## Prompt de activación

```
/prepare-tasks generate sdd/features/hogar/hogar_plan.md
```

---

## Flujo esperado paso a paso

### Paso 1 — El orquestador L1 parsea el comando
**Actor:** skill `prepare-tasks` (L1)
**Acción:** Lee `generate` y el path del plan.
**Verifica precondiciones:**
- El archivo existe y es un `*_plan.md`
- El plan tiene las secciones mínimas (domain, data, presentation)

**Señal de correcto:** El agente no genera tasks directamente — lanza el subagente.

---

### Paso 2 — El orquestador lanza el subagente `task-generator`
**Actor:** skill `prepare-tasks` (L1)
**Acción:** Invoca `Agent(subagent_type="task-generator")` con:
```
plan: <contenido del plan>
feature_name: hogar
```

**Señal de correcto:** Se invoca `task-generator`, no `sdd-analyst` ni `plan-architect`.

---

### Paso 3 — El subagente `task-generator` carga su contexto
**Actor:** agente `task-generator` (L2)
**Carga como contexto:**
- Knowledge `plan-expert` — para entender la estructura del plan que va a descomponer
- Knowledge `tasks-expert` — formato obligatorio de task, orden canónico, Prueba de Independencia
- Referencias de `tasks-expert`: `task_sizing.md` y `kmm_task_templates.md`

---

### Paso 4 — El subagente ejecuta la generación de tasks
**Actor:** agente `task-generator` (L2), guiado por `tasks-expert` (L3)
**Acciones en orden:**

**4a. Respetar el orden canónico KMM:**
```
T-000  /kmm-scaffold      → estructura de módulos
T-001  /kmm-domain        → Models
T-002  /kmm-domain        → Repository interfaces
T-003  /kmm-domain        → UseCases
T-004  /kmm-data          → DTOs + Mappers
T-005  /kmm-data          → DataSource remote
T-006  /kmm-data          → DataSource local
T-007  /kmm-data          → RepositoryImpl
T-008  /kmm-expect-actual → APIs platform-specific
T-009  /kmm-presentation  → ViewModel + UiState + UiEvent
T-010  /kmm-presentation  → Screen Composable
T-011  /kmm-tests         → Tests domain
T-012  /kmm-tests         → Tests data
```

**4b. Para cada task, generar el formato completo:**
```markdown
## T-001: domain — HogarModel

- **Spec CA:** CA-003, CA-007
- **Plan ref:** §Domain Layer / Models
- **Módulo:** :feature:hogar
- **Layer:** domain
- **Skill:** /kmm-domain
- **Input:** ninguna
- **Dependencies:** T-000
- **Definition of done:**
  - `shared/src/commonMain/kotlin/domain/model/HogarModel.kt` existe
  - HogarModel tiene los campos: id, nombre, direccion, ...
  - Compila sin errores
```

**4c. Aplicar la Prueba de Independencia a cada task:**
> "¿Puede ejecutarse leyendo solo el Plan y las Tasks anteriores en la lista?"
> - SÍ → bien definida
> - NO → añadir la información faltante en `Input` o `Definition of done`

**4d. Verificar que las dependencias son DAG (sin ciclos):**
- T-001 depende de T-000, T-002 depende de T-001, etc.
- No puede haber ciclos

**Señal de correcto:** Cada task cita los CAs del spec que la justifican y la sección del plan de la que deriva.

---

### Paso 5 — El subagente escribe el archivo de tasks
**Actor:** agente `task-generator` (L2)
**Archivo generado:** `features/hogar/hogar_tasks.md`
**Contenido esperado:**
```markdown
# Tasks: Hogar

## Resumen
Total tasks: 13
Features: hogar

---

## T-000: scaffold — Estructura de módulos
- **Spec CA:** (ninguna, es infraestructura)
- **Plan ref:** §Módulos Gradle
- **Módulo:** :feature:hogar
- **Layer:** scaffold
- **Skill:** /kmm-scaffold
- **Input:** hogar_plan.md §Módulos Gradle
- **Dependencies:** ninguna
- **Definition of done:**
  - Directorio `:feature:hogar` creado
  - `build.gradle.kts` configurado con dependencias KMM
  - Módulo compila vacío

## T-001: domain — HogarModel
...

## T-002: domain — HogarRepository (interfaz)
- **Dependencies:** T-001
...
```

---

## Resultado esperado

| Elemento | Valor |
|----------|-------|
| Archivo generado | `features/hogar/hogar_tasks.md` |
| Bloqueo | No bloquea — si el plan tiene TECH_GAPs, los hereda pero genera lo que puede |
| Siguiente paso | Ejecutar tasks en orden con `/kmm-scaffold`, `/kmm-domain`, etc. |

---

## Señales de fallo (qué validar)

- Se invoca `sdd-analyst` o `plan-architect` en vez de `task-generator`
- El orden de tasks no respeta el orden canónico KMM (p.ej. presenta antes que domain)
- Las tasks no tienen `Definition of done` concreto (archivos que deben existir)
- Las dependencias forman un ciclo
- Los CAs del spec no están referenciados en las tasks
- Una task no supera la Prueba de Independencia (requiere contexto externo no listado)
- Tasks demasiado grandes (un solo T-001 que incluye todo domain) o demasiado pequeñas (una task por campo)
- La sección `Input` está vacía en tasks que sí necesitan input de tasks anteriores
