# Análisis SDD: [Nombre del documento]

> **Generado por**: sdd-spec-explorer
> **Fecha**: [YYYY-MM-DD]
> **Archivo origen**: [path/al/archivo.md]

> **Nota**: este análisis prepara la información que los Specs van a necesitar. Las respuestas a gaps se anotan **en este archivo**. Si durante la validación aparece un cambio real de producto, debe formalizarse en el PRD mediante `wf-prd-change` antes de seguir resincronizando derivados.

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

## Estado de preparación para Specs

> **[LISTO_PARA_SPECS | LISTO_PARA_SPECS_CON_PREGUNTAS | REQUIERE_LIMPIEZA_PRD]**
>
> Resumen en 1-2 frases del estado del documento de cara a generar los Specs.

**Significado de los veredictos:**
- `LISTO_PARA_SPECS`: el PRD está limpio (sin contaminación técnica) y no hay gaps `[CRÍTICO]` pendientes. Se puede arrancar la generación de Specs directamente.
- `LISTO_PARA_SPECS_CON_PREGUNTAS`: el PRD está limpio, pero hay gaps `[CRÍTICO]` por responder. Se puede generar Specs igualmente — las HUs afectadas saldrán marcadas `[INCOMPLETO]` y se podrán completar luego con `/wf-spec-gap-resolve`.
- `REQUIERE_LIMPIEZA_PRD`: se detectó contaminación técnica en el PRD (Check 2). **Única condición** que requiere modificar el PRD antes de continuar.

---

## Elementos del Spec a generar desde este PRD

> Esta sección es **informativa**, no diagnóstica. Mapea qué partes del Spec final ya están en el PRD y cuáles se generarán durante la fase Spec. Es normal y esperable que un PRD bien formado no contenga HUs formales, Journeys paso a paso, CAs en GIVEN/WHEN/THEN ni Checklist — esos elementos pertenecen al Spec (`kb-prd-expert` Regla 9), no al PRD.

- **Actores** — [ya en PRD / a generar en Spec / parcial — se completará en Spec]
- **Historias de Usuario (Como/quiero/para que)** — [ya en PRD / a generar en Spec / parcial — se completará en Spec]
- **Recorridos de Usuario** — [ya en PRD / a generar en Spec / parcial — se completará en Spec]
- **Resultados y Éxito** — [ya en PRD / a generar en Spec / parcial — se completará en Spec]
- **Instrucciones Inambiguas** — [ya en PRD / a generar en Spec / parcial — se completará en Spec]
- **Criterios de Aceptación (GIVEN/WHEN/THEN)** — [ya en PRD / a generar en Spec / parcial — se completará en Spec]
- **Checklist de Validación** — [ya en PRD / a generar en Spec / parcial — se completará en Spec]
- **Fuera de Alcance** — [ya en PRD / a generar en Spec / parcial — se completará en Spec]

---

## Pureza: [APROBADO | CONTAMINADO]

<!-- Si APROBADO: "No se encontraron elementos técnicos en el documento." -->
<!-- Si CONTAMINADO: listar cada instancia encontrada — éste es el único caso que requiere editar el PRD por contaminación técnica detectada en analyze -->

#### [C-001] [Título breve de la contaminación]
- **Cita**: > "[fragmento exacto del documento]"
- **Problema**: [por qué pertenece al Plan, qué hace al Spec tecnología-dependiente]
- **Reescritura sugerida**: "[versión funcional equivalente]"
- **Acción**: `[ ] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

<!-- Instrucciones para el usuario:
     - ACEPTAR: la reescritura se aplicará al PRD tal cual y luego se usará en el spec final
     - EDITAR: modifica el texto de "Reescritura sugerida" arriba y marca esta opción
     - RECHAZAR: añade tu justificación tras "RECHAZAR"; el texto original se conservará como excepción consciente
     Solo marca UNA de las tres opciones por contaminación. -->

---

## Testabilidad: [APROBADO | REQUIERE_MEJORA | NO_APLICA]

<!-- Si APROBADO: "Todos los CAs encontrados son verificables de forma objetiva e independiente." -->
<!-- Si REQUIERE_MEJORA: listar CAs problemáticos -->
<!-- Si NO_APLICA: "El PRD no contiene CAs formales — esperado en un PRD. Los CAs se generarán en la fase Spec." -->

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
>
> **Las respuestas se escriben en este archivo, no en el PRD**, salvo que la propia respuesta cambie el producto comprometido. En ese caso, usa `wf-prd-change`.
> Escribe la respuesta de cada cliente en el campo "Respuesta" del gap correspondiente.
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

**Si el veredicto es `LISTO_PARA_SPECS` o `LISTO_PARA_SPECS_CON_PREGUNTAS`**:

1. Anota la respuesta de cada `[P-XXX]` que puedas resolver **en este archivo**, en el campo `Respuesta` (sustituye `_(pendiente)_` por la respuesta real). Si al responder descubres que cambia el producto comprometido, usa `wf-prd-change` y no trates la decisión como un simple gap.
2. Los `[CRÍTICO]` que queden sin respuesta marcarán sus HUs como `[INCOMPLETO]` en el spec (se generarán pero no podrán avanzar a plan/tasks hasta completarse).
3. Los `[INFORMATIVO]` que queden sin respuesta aplicarán su asunción por defecto.
4. Ejecuta el flujo completo automático:
   ```
   /wf-spec-features-first [path/al/archivo.md]
   ```
   O para el paso a paso (solo discovery):
   ```
   /wf-spec-discover [path/al/archivo.md] --analysis [path/al/archivo_analysis.md]
   ```
5. Para completar HUs marcadas `[INCOMPLETO]` más tarde: responde los gaps pendientes en este archivo y ejecuta `/wf-spec-gap-resolve <feature_spec.md>`.

**Si el veredicto es `REQUIERE_LIMPIEZA_PRD`** (único caso de edición del PRD por contaminación técnica detectada en analyze):

1. En la sección "Pureza", para cada contaminación marca **una** de las tres acciones:
   - `[x] ACEPTAR` — aplica la reescritura sugerida al PRD
   - `[x] EDITAR` — modifica el texto de "Reescritura sugerida" y marca esta opción; luego aplica ese texto al PRD
   - `[x] RECHAZAR (justificar)` — añade tu justificación; el texto original se conservará como excepción documentada
2. Tras editar el PRD, vuelve a ejecutar `/wf-spec-analyze [path/al/archivo.md]` para confirmar que la limpieza es completa antes de avanzar.
