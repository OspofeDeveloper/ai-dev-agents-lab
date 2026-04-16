# TODO: Mejoras pendientes para la fase de specs

> Generado: 2026-04-07
> Contexto: análisis comparativo entre SDD Lab y Agent Teams Lite (agent-teams-lite-main).
> Objetivo: dejar una base sólida de specs antes de abordar la fase de plan.

---

## DONE

_(vacío por ahora)_

---

## PENDING

### [S-01] THEN observable-only — enforcement explícito en `error_patterns.md`

**Archivos a tocar:** `spec/skills/kb-spec-expert/references/error_patterns.md`

**Problema:** Algunos THENs describen estado interno del sistema, no comportamiento observable por el usuario. Ejemplo: `"THEN el sistema guarda el registro"`, `"THEN el sistema envía la notificación internamente"`. No mencionan tecnología explícita, pero describen implementación — contaminación sutil que el agente no detecta porque no está en el catálogo de patrones.

**Por qué importa antes del plan:** El plan-architect lee los CAs para decidir qué componentes construir. Un THEN interno no le dice nada verificable — le obliga a inferir la consecuencia observable, y cuando infiere, puede equivocarse o ampliar scope involuntariamente.

**Qué hacer:**
- Añadir en `error_patterns.md` la sección "THEN no observable" con ejemplos y reescrituras:
  - `"THEN el sistema guarda el registro"` → `"THEN la entrada aparece en la lista con los datos introducidos"`
  - `"THEN el sistema envía un email"` → `"THEN el usuario recibe un mensaje de confirmación en su bandeja de entrada"`
  - `"THEN el sistema calcula el total"` → `"THEN el usuario ve el importe total actualizado en el resumen"`
- Regla general a añadir: "Todo THEN debe describir lo que el usuario puede observar, leer o interactuar — no lo que el sistema procesa internamente."
- Aplicar también en `wf-spec-validate` (Check 3 — Testabilidad) y en `wf-spec-analyze` (Check 3).

---

### [S-02] RFC 2119 en los THEN de los CAs

**Archivos a tocar:** `spec/skills/kb-spec-expert/SKILL.md`, `spec/skills/wf-spec-fast-track/references/feature_spec_template.md`

**Problema:** Los THEN actuales usan lenguaje libre: `"THEN el sistema muestra un mensaje"`. No distinguen si ese comportamiento es obligatorio o uno de varios posibles. El plan-architect interpreta por defecto que todo THEN es mandatorio, lo cual puede sobreespecificar features opcionales, o infraespecificar comportamientos críticos.

**Por qué importa antes del plan:** La diferencia entre DEBE y PUEDE en un CA tiene consecuencias directas en el número de componentes a implementar y en los criterios de done de cada task. Si no está explícito en el spec, la decisión cae en el plan, que no es el lugar correcto.

**Qué hacer:**
- Añadir en `kb-spec-expert` (sección de CAs) la regla de uso de keywords:
  - `DEBE` / `MUST` — comportamiento mandatorio, sin excepción, verificable
  - `DEBERÍA` / `SHOULD` — comportamiento recomendado; puede tener excepciones documentadas en las Instrucciones Inambiguas
  - `PUEDE` / `MAY` — comportamiento opcional, no bloquea el CA si no ocurre
- Actualizar el ejemplo de CA en `kb-spec-expert` para reflejar el keyword:
  ```
  THEN el sistema DEBE mostrar un diálogo de confirmación con opciones "Cancelar" y "Confirmar"
  ```
- Actualizar `feature_spec_template.md` para que el placeholder del THEN incluya el keyword.
- Añadir al Check 3 (Testabilidad) en `wf-spec-validate` y `wf-spec-analyze`: verificar que los THENs tienen keyword de obligatoriedad explícito.

---

### [S-03] Checklist de Validación auto-completado por `wf-spec-validate`

**Archivos a tocar:** `spec/skills/wf-spec-validate/SKILL.md`

**Problema:** El spec se genera con todos los checkboxes vacíos `[ ]`. El checklist nunca se rellena porque el agente que genera el spec no lo valida al terminar, y `wf-spec-validate` produce su informe en el output pero no escribe los resultados de vuelta en el archivo del spec. El checklist es ruido visual en lugar de un gate real.

**Por qué importa antes del plan:** `wf-prepare-plan` debería poder leer el checklist y saber si el spec pasó validación sin tener que re-ejecutar la auditoría. Con el checklist siempre vacío, no hay señal de estado disponible.

**Qué hacer:**
- Modificar `wf-spec-validate` para que, al finalizar la auditoría, reescriba la sección `## Checklist de Validación` en el spec con el resultado:
  - `[x]` — check superado
  - `[!]` — check fallido (con nota inline: `[!] Actores identificados — FALTA: no hay tabla de actores`)
  - `[ ]` — no aplica o no evaluado
- Añadir al final del checklist una línea de estado global:
  ```
  **Validación:** APROBADO | REQUIERE_MEJORA — [fecha] via wf-spec-validate
  ```
- Este cambio convierte el checklist en un artefacto con estado real, legible por el plan-architect y por el usuario sin necesidad de releer el informe de validación completo.

---

### [S-04] Sección `## Open Questions` en el template de spec

**Archivos a tocar:** `spec/skills/wf-spec-fast-track/references/feature_spec_template.md`, `spec/skills/kb-spec-expert/SKILL.md`, `spec/skills/wf-spec-fast-track/SKILL.md`

**Problema:** El sistema de gaps `[P-XXX]` captura ambigüedades del PRD antes de generar el spec. Pero durante la generación del spec emergen preguntas nuevas que no bloquean la escritura del spec (no son CRÍTICO) pero sí dejan decisiones abiertas que el plan-architect tendrá que resolver. Actualmente esas preguntas o se pierden o se asumen silenciosamente. La diferencia con un gap INFORMATIVO es que aquí la pregunta surge del proceso de especificación, no del análisis del PRD.

**Por qué importa antes del plan:** El plan-architect no debería encontrarse con preguntas sin responder. Si las hay, es mejor que estén documentadas en el spec explícitamente que dispersas en las asunciones implícitas del agente.

**Qué hacer:**
- Añadir sección opcional `## Open Questions` al template, después de `## Fuera de Alcance`:
  ```markdown
  ## Open Questions
  <!-- OPCIONAL: preguntas que surgieron durante la especificación, no bloqueantes para el spec pero relevantes para el plan -->
  ### OQ-001: [título descriptivo]
  **Contexto:** [por qué surgió esta pregunta durante la especificación]
  **Impacto si no se responde:** [qué decisión del plan queda sin base]
  **Estado:** pendiente | respondida — [respuesta]
  ```
- En `wf-spec-fast-track`: el agente debe escribir aquí en lugar de asumir cuando detecta una ambigüedad no crítica que emerge durante la escritura del spec.
- En `wf-prepare-plan`: verificar que no hay OQ con estado `pendiente` antes de proceder. Si las hay → informar al usuario y pedir respuestas (comportamiento no bloqueante: informa pero continúa con advertencia, igual que los INCOMPLETO).
- Añadir al checklist de validación: `[ ] No hay Open Questions pendientes sin respuesta`.

---

### [S-05] Campo opcional `Verificación:` en los CAs

**Archivos a tocar:** `spec/skills/kb-spec-expert/SKILL.md`, `spec/skills/wf-spec-fast-track/references/feature_spec_template.md`

**Problema:** Los CAs se escriben sin indicar cómo se verificarán. Cuando se implemente la fase de verify (necesaria para cerrar el pipeline), no habrá forma de mapear specs a evidencia de test de forma sistemática sin reanalizar todos los CAs desde cero. Detectar esto en el momento de escritura del CA cuesta prácticamente nada; hacerlo retroactivamente sobre 50 specs cuesta mucho.

**Por qué importa antes del plan:** El plan-architect necesita saber qué tipo de cobertura de test exige cada CA para incluirla en el plan. Sin esta pista, o la omite (infratestado) o la inventa (scope creep en testing).

**Qué hacer:**
- Añadir campo opcional `Verificación:` debajo del THEN en cada CA:
  ```
  THEN el sistema DEBE mostrar el mensaje de confirmación
  Verificación: Test funcional E2E — flujo de confirmación visible para el usuario
  ```
- Los valores posibles son funcionales, no técnicos: `Test unitario de comportamiento`, `Test de integración`, `Test funcional E2E`, `Aceptación manual`, `No automatizable`.
- Aclarar en `kb-spec-expert`: el campo `Verificación:` describe el *tipo* de evidencia funcional necesaria para dar el CA por cumplido — no menciona frameworks, clases ni runners. La Prueba de Pureza lo acepta porque aplica igual en web, mobile o backend.
- Es opcional: no todos los CAs necesitan la pista si el tipo de verificación es obvio. Pero sí debe aparecer cuando haya ambigüedad o cuando el CA sea especialmente crítico.

---

### [S-06] Sección `## Feature Dependencies` en el template de spec

**Archivos a tocar:** `spec/skills/wf-spec-fast-track/references/feature_spec_template.md`, `spec/skills/wf-spec-fast-track/SKILL.md`

**Problema:** El sistema de shared models captura qué features comparten modelos de dominio, pero el spec de cada feature no declara de forma explícita de qué otras features depende funcionalmente. El plan-architect debe inferir el orden de implementación leyendo `_features.md` y cruzando shared models — trabajo que puede automatizarse si la dependencia está en el spec.

**Por qué importa antes del plan:** `wf-prepare-plan` usa el spec como input principal. Si las dependencias están en el spec, el plan puede reflejar el orden de implementación correcto sin leer artefactos adicionales.

**Qué hacer:**
- Añadir sección `## Feature Dependencies` al inicio del spec (antes de Actores), justo después del header:
  ```markdown
  ## Feature Dependencies
  | Feature | Tipo | Descripción |
  |---------|------|-------------|
  | auth | Precondición funcional | Esta feature requiere que el actor Usuario exista y esté autenticado |
  | user-profile | Modelo compartido | Usa el modelo UserProfile definido en user-profile (owner) |
  ```
  - **Precondición funcional**: la feature no puede ejecutarse sin que otra feature exista
  - **Modelo compartido**: usa un modelo de dominio cuyo owner es otra feature
  - **Referencia de datos**: lee datos producidos por otra feature pero no los define
- `wf-spec-fast-track` debe poblar esta sección desde `_features.md` (sección de shared models) y `_discovery.md` (dependencias de scope detectadas).
- Si no hay dependencias: `No hay dependencias con otras features.`

---

### [S-07] Heurísticas de densidad en `kb-spec-expert`

**Archivos a tocar:** `spec/skills/kb-spec-expert/SKILL.md`

**Problema:** No hay reglas explícitas de cuándo un spec está "demasiado delgado" o "demasiado gordo". Sin métricas, el agente no puede autodetectar specs incompletos o sobredimensionados, y el usuario no tiene señales de cuándo preocuparse.

**Por qué importa antes del plan:** Un spec delgado genera un plan con huecos. Un spec inflado con HUs que deberían ser features separadas genera un plan difícil de implementar en paralelo. La densidad correcta es la base de un plan bien dimensionado.

**Qué hacer:**
- Añadir en `kb-spec-expert` una sección "Heurísticas de densidad":
  ```
  MÍNIMOS (señales de spec incompleto):
  - Menos de 3 CAs por HU → sospecha de cobertura insuficiente (solo happy path)
  - Un solo Journey para una feature con múltiples actores → journeys faltantes
  - Sección "Fuera de Alcance" vacía o "No se han definido exclusiones" → posible scope implícito

  MÁXIMOS (señales de spec sobredimensionado o mal particionado):
  - Más de 8 HUs → revisar si la feature debería dividirse en dos
  - Más de 6 CAs en una sola HU → revisar si la HU cubre dos objetivos distintos
  - Más de 3 actores con capacidades solapadas → revisar si hay duplicación de roles

  NORMAL:
  - 3-6 HUs por feature
  - 3-5 CAs por HU (happy path + 1-2 alternativos + 1-2 errores/edge cases)
  - 1-2 Journeys por actor principal
  ```
- Integrar estas heurísticas en el output del `wf-spec-validate` (nuevo Check 6 — Densidad) y como paso de auto-revisión al final de `wf-spec-fast-track`.

---

### [S-08] Archive automático antes de `wf-spec-delta apply`

**Archivos a tocar:** `spec/skills/wf-spec-delta/SKILL.md`

**Problema:** `wf-spec-delta apply` sobreescribe el spec directamente. El Changelog dentro del spec registra qué cambió textualmente, pero la versión anterior del archivo se pierde. Si el delta aplicado es incorrecto, o el usuario quiere comparar el spec antes y después de un cambio, no hay forma de hacerlo sin git.

**Por qué importa antes del plan:** A medida que el proyecto madura, los specs evolucionarán varias versiones. No poder revisar el estado anterior de un spec es un problema de auditoría, especialmente cuando los cambios afectan a CAs que ya tienen tasks asociadas.

**Qué hacer:**
- En el modo `apply` de `wf-spec-delta`, antes de sobreescribir el spec, hacer una copia:
  - El spec está en `features/<nombre>/<nombre>_spec.md` con versión `vX.Y` en el header.
  - Copiar a `features/<nombre>/archive/<nombre>_spec_vX.Y.md` antes de escribir la nueva versión.
  - Crear la carpeta `archive/` si no existe.
- El mismo mecanismo aplica para el modo `resolve`.
- El Changelog en el spec ya registra los cambios — el archive añade la copia completa del estado anterior como respaldo.
- No añadir complejidad adicional: solo copy antes de write.

---

### [S-09] `wf-spec-propose` — documento de propuesta antes del fast-track

**Archivos a tocar:** Nuevo skill `spec/skills/wf-spec-propose/SKILL.md` + actualización de `spec/skills/wf-spec-features-first/SKILL.md`

**Problema:** El pipeline pasa de `_discovery.md` directamente a generar specs completos por feature sin un checkpoint de alineación de scope. Los specs pueden estar bien escritos pero responder a una feature mal-scoped: demasiado grande, demasiado pequeña, o con una intención diferente a lo que el usuario quería. Detectarlo después de tener 10 specs generados es costoso.

**Por qué importa antes del plan:** Un spec bien escrito sobre la feature equivocada genera un plan perfectamente inútil. El checkpoint de propuesta cuesta 5 minutos de revisión y puede ahorrar rehacerlo todo.

**Qué hacer:**
- Nuevo skill `wf-spec-propose` que toma `_discovery.md` + (opcionalmente) `_analysis.md` y genera un documento de propuesta ligero por feature (~300 palabras):
  ```markdown
  # Propuesta: [Feature Name] (F-00X)

  ## Intención
  [Qué problema resuelve y para qué actor principal]

  ## Dentro del scope
  - [capacidad 1]
  - [capacidad 2]

  ## Fuera del scope
  - [exclusión 1 — por qué queda fuera]

  ## Criterios de éxito
  [Qué significa que esta feature esté terminada, en lenguaje de negocio]

  ## Dependencias
  [Otras features que deben existir antes o modelos compartidos que requiere]

  ## Riesgos detectados
  [Ambigüedades o conflictos potenciales identificados en el discovery]
  ```
- El usuario revisa y aprueba (o ajusta el scope) antes de ejecutar `wf-spec-fast-track`.
- En `wf-spec-features-first`: añadir como paso opcional entre el discovery y el fast-track, activable con flag `--propose` (por defecto desactivado para no romper el flujo actual).
- También invocable manualmente: `/wf-spec-propose _discovery.md [--feature F-003]`

---

## Notas de implementación

- Los puntos S-01 a S-07 son modificaciones a archivos existentes. Se pueden hacer en una sola sesión.
- S-08 es una modificación quirúrgica a `wf-spec-delta` (añadir copy antes de write).
- S-09 es el único que requiere un skill nuevo y actualizar `wf-spec-features-first`.
- El orden sugerido de implementación refleja impacto/esfuerzo: empezar por S-01 → S-07 antes de abordar S-08 y S-09.
- Ninguno de estos cambios rompe los specs ya generados — son todos aditivos (nuevas secciones opcionales, nuevas reglas en kb, nuevos checks en validate).
