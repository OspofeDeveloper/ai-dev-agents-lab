# Análisis SDD: [Nombre del documento]

> **Generado por**: sdd-spec-explorer
> **Fecha**: [YYYY-MM-DD]
> **Archivo origen**: [path/al/archivo.md] (v[X.Y])

> **Nota**: este análisis prepara la información que los Specs van a necesitar. Las respuestas a gaps se anotan **en este archivo**. Si durante la validación aparece un cambio real de producto, debe formalizarse en el PRD —pídeselo a Claude como un cambio de producto— antes de seguir resincronizando derivados.

---

## Leyenda de notación

| Código | Significado | Dónde aparece |
|--------|-------------|---------------|
| `[C-XXX]` | Contaminación técnica detectada | Sección Pureza |
| `[CA-XXX]` | Criterio de Aceptación problemático | Sección Testabilidad |
| `[P-XXX]` | Pregunta pendiente de validación con el cliente | Sección Puntos pendientes |
| `[CRÍTICO]` | Gap que impide completar las HUs afectadas — quedarán marcadas `[INCOMPLETO]` en el spec si no se responde | Sección Puntos pendientes |
| `[INFORMATIVO]` | Gap con asunción por defecto — se aplica automáticamente si no se responde | Sección Puntos pendientes |
| `[PUEDE_REQUERIR_CR]` | Gap cuya futura respuesta puede introducir cambio de producto y exigir formalizarlo en el PRD | Sección Puntos pendientes |
| `_(pendiente)_` | Respuesta aún no proporcionada por el cliente | Campo "Respuesta" de cada gap |

---

## Estado de preparación para Specs

> **[LISTO_PARA_SPECS | LISTO_PARA_SPECS_CON_PREGUNTAS | REQUIERE_LIMPIEZA_PRD]**
>
> Resumen en 1-2 frases del estado del documento de cara a generar los Specs.

**Significado de los veredictos:**
- `LISTO_PARA_SPECS`: el PRD está limpio (sin contaminación técnica) y no hay gaps `[CRÍTICO]` pendientes. Se puede arrancar la generación de Specs directamente.
- `LISTO_PARA_SPECS_CON_PREGUNTAS`: el PRD está limpio, pero hay gaps `[CRÍTICO]` por responder. Se puede continuar hacia Specs, pero al generar las specs se te pedirá una decisión explícita: responder primero esos gaps o continuar. Si se continúa, las HUs afectadas saldrán marcadas `[INCOMPLETO]` y se podrán completar después.
- `REQUIERE_LIMPIEZA_PRD`: se detectó contaminación técnica en el PRD (Check 2). **Única condición** que requiere modificar el PRD antes de continuar.

---

## Elementos del Spec a generar desde este PRD

> Esta sección es **informativa**, no diagnóstica. Mapea qué partes del Spec final ya están en el PRD y cuáles se generarán durante la fase Spec. Es normal y esperable que un PRD bien formado no contenga HUs formales, Journeys paso a paso, CAs en GIVEN/WHEN/THEN ni Checklist — esos elementos pertenecen al Spec, no al PRD.

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
> **Las respuestas se escriben en este archivo, no en el PRD**, salvo que la propia respuesta cambie el producto comprometido. En ese caso, dile a Claude que quieres formalizar un cambio de producto sobre el PRD.
> Escribe la respuesta de cada cliente en el campo "Respuesta" del gap correspondiente, sustituyendo `_(pendiente)_`.
> Si prefieres dictárselas a Claude en la conversación, él las aplicará por ti — no editará este archivo a mano ni completará una respuesta que no hayas dado.
>
> - `[CRÍTICO]`: afecta directamente a las HUs indicadas en "Afecta". Si se deja sin responder, esas HUs se marcarán como `[INCOMPLETO]` en el spec — se generarán con la información disponible pero no podrán avanzar a plan/tasks hasta completarse.
> - `[INFORMATIVO]`: si no se responde, se aplicará la "Asunción por defecto" indicada.
> - `[PUEDE_REQUERIR_CR]`: no cambia la severidad, pero obliga a reevaluar la respuesta con la gobernanza de cambios de producto si introduce expansión de capacidad.
>
> **Al redactar cada gap:** `Contexto`, `Problema` y `Pregunta para el cliente` las lee una persona de producto. Los **IDs se quedan** (`CA-001`, `HU-003`, `RF-006`); las **siglas sueltas no** — *"el CA de X"* → *"el criterio de aceptación de X"*, *"sin THEN verificable"* → *"sin resultado verificable"*. El campo `Afecta` lista IDs y no se toca.

### [P-001][CRÍTICO] [Título del gap — describe qué falta]
- **Contexto**: [cita del documento o descripción de dónde aparece la ambigüedad]
- **Problema**: [por qué esto es un gap funcional que bloquea el spec]
- **Afecta**: [HU-001, HU-003 — lista de HUs que no pueden completarse sin esta respuesta]
- **Pregunta para el cliente**: [pregunta concreta y específica, sin opciones inventadas]
- **Respuesta**: _(pendiente)_

### [P-002][CRÍTICO][PUEDE_REQUERIR_CR] [Título del gap — respuesta sensible de alcance]
- **Contexto**: [cita del documento o descripción de dónde aparece la ambigüedad]
- **Problema**: [por qué esto bloquea o condiciona el spec]
- **Afecta**: [HU-002]
- **Pregunta para el cliente**: [pregunta neutra, sin empujar hacia una solución expansiva]
- **Respuesta**: _(pendiente)_

### [P-003][INFORMATIVO] [Título del gap — describe qué falta]
- **Contexto**: [cita del documento o descripción de dónde aparece la ambigüedad]
- **Pregunta para el cliente**: [pregunta concreta y específica, sin opciones inventadas]
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: [lo que se aplicará si el cliente no responde antes de ejecutar discover/fast-track]

---

## Próximos pasos

**Si el veredicto es `LISTO_PARA_SPECS` o `LISTO_PARA_SPECS_CON_PREGUNTAS`**:

1. Anota la respuesta de cada `[P-XXX]` que puedas resolver **en este archivo**, en el campo `Respuesta` (sustituye `_(pendiente)_` por la respuesta real). Si al responder descubres que cambia el producto comprometido, o que la respuesta introduce una entidad persistente, un catálogo reutilizable, una nueva granularidad funcional o un flujo adicional no comprometido en el PRD, **no lo trates como un simple gap**: dile a Claude que quieres **formalizar un cambio de producto sobre el PRD** y lo llevará por la vía de gobernanza.
2. Los `[CRÍTICO]` que queden sin respuesta marcarán sus HUs como `[INCOMPLETO]` en el spec (se generarán pero no podrán avanzar a plan/tasks hasta completarse).
3. Los `[INFORMATIVO]` que queden sin respuesta aplicarán su asunción por defecto.
4. Cuando quieras generar las specs, **pídeselo a Claude en lenguaje natural** — él elige el
   flujo y construye los argumentos:
   - Si el veredicto es `LISTO_PARA_SPECS`: *"genera las specs de este PRD"*.
   - Si es `LISTO_PARA_SPECS_CON_PREGUNTAS`, tienes dos vías y te las ofrecerá al llegar al
     gate: **responder antes los `[CRÍTICO]`** (recomendada), o **continuar aceptando** que
     las HUs afectadas salgan `[INCOMPLETO]`. Puedes anticiparlo diciéndolo —*"genera las
     specs aunque queden gaps críticos abiertos"*— y él pedirá tu confirmación explícita.
   - Si solo quieres el mapa de features sin generar nada todavía: *"descubre las features
     de este PRD"*.
5. Para completar más tarde las HUs marcadas `[INCOMPLETO]`: responde aquí los gaps que
   quedaron pendientes y pídele *"completa las historias incompletas de este spec"*.

**Si el veredicto es `REQUIERE_LIMPIEZA_PRD`** (único caso de edición del PRD por contaminación técnica detectada en analyze):

1. En la sección "Pureza", para cada contaminación marca **una** de las tres acciones:
   - `[x] ACEPTAR` — aplica la reescritura sugerida al PRD
   - `[x] EDITAR` — modifica el texto de "Reescritura sugerida" y marca esta opción; luego aplica ese texto al PRD
   - `[x] RECHAZAR (justificar)` — añade tu justificación; el texto original se conservará como excepción documentada
2. Tras editar el PRD, pídele que **vuelva a analizarlo** para confirmar que la limpieza es completa antes de avanzar.
