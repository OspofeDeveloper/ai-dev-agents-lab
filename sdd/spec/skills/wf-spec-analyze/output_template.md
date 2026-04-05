# Análisis SDD: [Nombre del documento]

> **Generado por**: sdd-analyst (modo analyze)
> **Fecha**: [YYYY-MM-DD]
> **Archivo origen**: [path/al/archivo.md]

---

## Leyenda de notación

| Código | Significado | Dónde aparece |
|--------|-------------|---------------|
| `[C-XXX]` | Contaminación técnica detectada | Sección Pureza |
| `[CA-XXX]` | Criterio de Aceptación problemático | Sección Testabilidad |
| `[P-XXX]` | Pregunta pendiente de validación con el cliente | Sección Puntos pendientes |
| `[CRÍTICO]` | Gap que impide completar las HUs afectadas — quedarán marcadas `[INCOMPLETO]` en el spec si no se responde | Sección Puntos pendientes |
| `[INFORMATIVO]` | Gap con asunción por defecto — se aplica automáticamente si no se responde | Sección Puntos pendientes |
| `_(pendiente)_` | Respuesta aún no proporcionada por el cliente | Campo "Respuesta" de cada gap |

---

## Estado general

> **[REQUIERE_TRABAJO | APROBADO_CON_OBSERVACIONES | APROBADO]**
>
> Resumen en 1-2 frases del estado del documento y los principales bloqueantes.

---

## Completitud: X/8 elementos presentes

- [ ] **Actores** — [presente / parcial: falta X / ausente]
- [ ] **Historias de Usuario (Como/quiero/para que)** — [presente / parcial: falta X / ausente]
- [ ] **Recorridos de Usuario** — [presente / parcial: falta X / ausente]
- [ ] **Resultados y Éxito** — [presente / parcial: falta X / ausente]
- [ ] **Instrucciones Inambiguas** — [presente / parcial: falta X / ausente]
- [ ] **Criterios de Aceptación (GIVEN/WHEN/THEN)** — [presente / parcial: falta X / ausente]
- [ ] **Checklist de Validación** — [presente / parcial: falta X / ausente]
- [ ] **Fuera de Alcance** — [presente / ausente]

---

## Pureza: [APROBADO | CONTAMINADO]

<!-- Si APROBADO: "No se encontraron elementos técnicos en el documento." -->
<!-- Si CONTAMINADO: listar cada instancia encontrada -->

#### [C-001] [Título breve de la contaminación]
- **Cita**: > "[fragmento exacto del documento]"
- **Problema**: [por qué pertenece al Plan, qué hace al Spec tecnología-dependiente]
- **Reescritura sugerida**: "[versión funcional equivalente]"
- **Acción**: `[ ] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

<!-- Instrucciones para el usuario:
     - ACEPTAR: la reescritura se usará tal cual en el spec final
     - EDITAR: modifica el texto de "Reescritura sugerida" arriba y marca esta opción
     - RECHAZAR: añade tu justificación tras "RECHAZAR"; el texto original se conservará como excepción consciente
     Solo marca UNA de las tres opciones por contaminación. -->

---

## Testabilidad: [APROBADO | REQUIERE_MEJORA]

<!-- Si APROBADO: "Todos los CAs encontrados son verificables de forma objetiva e independiente." -->
<!-- Si REQUIERE_MEJORA: listar CAs problemáticos -->

#### [CA-001] [Título del CA problemático]
- **CA actual**: [descripción o cita]
- **Problema**: [vago / no verificable / dependiente de otro CA / sin GIVEN o sin THEN / sin referencia a HU padre]
- **Sugerencia de reformulación**:
  ```
  GIVEN [precondición clara]
  WHEN [acción específica del usuario]
  THEN [resultado observable y verificable]
  ```

---

## Puntos pendientes de validación con cliente

> Estos puntos **no fueron inferidos por el sistema**. Son ambigüedades o información ausente
> que debe ser definida por el cliente antes de generar el `.spec` final.
> **Instrucción**: escribe la respuesta del cliente en el campo "Respuesta" de cada punto.
>
> - `[CRÍTICO]`: afecta directamente a las HUs indicadas en "Afecta". Si se deja sin responder, esas HUs se marcarán como `[INCOMPLETO]` en el spec — se generarán con la información disponible pero no podrán avanzar a plan/tasks hasta completarse.
> - `[INFORMATIVO]`: si no se responde, se aplicará la "Asunción por defecto" indicada.

### [P-001][CRÍTICO] [Título del gap — describe qué falta]
- **Contexto**: [cita del documento o descripción de dónde aparece la ambigüedad]
- **Problema**: [por qué esto es un gap funcional que bloquea el spec]
- **Afecta**: [HU-001, HU-003 — lista de HUs que no pueden completarse sin esta respuesta]
- **Pregunta para el cliente**: [pregunta concreta y específica, sin opciones inventadas]
- **Respuesta**: _(pendiente)_

### [P-002][INFORMATIVO] [Título del gap — describe qué falta]
- **Contexto**: [cita del documento o descripción de dónde aparece la ambigüedad]
- **Pregunta para el cliente**: [pregunta concreta y específica, sin opciones inventadas]
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: [lo que se aplicará si el cliente no responde antes de ejecutar discover/fast-track]

---

## Próximos pasos

1. En la sección "Pureza", para cada contaminación marca **una** de las tres acciones:
   - `[x] ACEPTAR` — se usará la reescritura tal cual en el spec
   - `[x] EDITAR` — modifica el texto de "Reescritura sugerida" y marca esta opción
   - `[x] RECHAZAR (justificar)` — añade tu justificación; el texto original se conservará como excepción documentada
2. Responder los puntos `[CRÍTICO]` que puedas — los que queden sin respuesta marcarán sus HUs como `[INCOMPLETO]` en el spec (se generarán pero no podrán avanzar a plan/tasks)
3. Responder los puntos `[INFORMATIVO]` si tienes la información — si no, se aplicará la asunción por defecto
4. Una vez revisado, ejecutar el flujo completo automático:
   ```
   /wf-spec-features-first [path/al/archivo.md]
   ```
   O para el paso a paso (solo discovery):
   ```
   /wf-spec-discover [path/al/archivo.md] --analysis [path/al/archivo_analysis.md]
   ```
5. Para completar HUs marcadas `[INCOMPLETO]` después: responde los gaps pendientes en este archivo y ejecuta `/wf-spec-delta resolve <feature_spec.md>`
