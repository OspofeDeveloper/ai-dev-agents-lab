# Project Map: [Nombre del Proyecto]
> PRD origen: [path/al/prd.md] | Fecha: [YYYY-MM-DD]
> Generado via: wf-spec-map

---

## Scope del proyecto

[2-3 frases que describen qué resuelve el sistema desde la perspectiva del usuario, sin tecnicismos ni menciones de plataforma]

---

## Features identificadas

| ID | Nombre funcional | Actor principal | Descripción (una frase) | Riesgo |
|----|-----------------|-----------------|-------------------------|--------|
| F-001 | [nombre-kebab] | [actor] | [qué resuelve para el usuario] | ALTO / MEDIO / BAJO / — |
| F-002 | [nombre-kebab] | [actor] | [qué resuelve para el usuario] | ALTO / MEDIO / BAJO / — |

> **Criterio de feature válida**: tiene actor claro, journeys funcionalmente independientes de otras features, y al menos 3 CAs derivables. Si una entrada no cumple estos 3 criterios, debe fusionarse con otra feature o eliminarse.

---

## Interacciones entre features

| Feature A | Relación | Feature B | Descripción |
|-----------|----------|-----------|-------------|
| F-001 | depende-de | F-002 | [A no puede ejecutarse sin que B haya completado X] |
| F-001 | comparte-modelo | F-003 | [ambas usan el modelo Y; owner: F-00Z] |

> Si no hay interacciones entre features → escribir "Sin interacciones detectadas."

---

## Shared models candidatos

| Modelo | Feature owner candidata | Features que lo usan | Confianza |
|--------|------------------------|----------------------|-----------|
| [Nombre del modelo] | F-00X | F-00Y, F-00Z | ALTA / MEDIA / BAJA |

> **Owner candidato**: la feature que crea o define el modelo. Si hay ambigüedad, se resolverá durante `wf-spec-map-generate`.
> Si no hay shared models → escribir "Sin shared models detectados."

---

## Flags de riesgo

### [R-001] [ALTO / MEDIO] [Título del riesgo]
- **Feature afectada**: F-00X
- **Descripción**: [qué es ambiguo, escaso o contradictorio en el PRD para esta feature]
- **Impacto**: [qué fase del pipeline se verá afectada y por qué]

> Si no hay flags de riesgo → escribir "Sin flags de riesgo detectados."

---

## Instrucciones de validación estratégica

> Revisa la tabla de features. Comprueba que las features identificadas reflejan la arquitectura funcional que quieres construir.
>
> Para editar el mapa:
> - **Renombrar feature**: edita la celda directamente
> - **Fusionar dos features**: elimina una fila y actualiza la otra con el scope combinado
> - **Excluir feature**: elimina la fila o marca su Riesgo como `[EXCLUIDA]`
> - **Añadir feature que falta**: añade una fila con el siguiente ID disponible
> - **Corregir una interacción**: edita la tabla de interacciones directamente
>
> Cuando el mapa refleje la arquitectura funcional correcta, ejecuta:
> ```
> /wf-spec-map-analyze <prd.md>
> ```
