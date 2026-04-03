# Spec: [nombre de la funcionalidad]
> Versión: 1.0 | Fecha: [YYYY-MM-DD] | Generado desde: [path]

---

## Resumen de generación

### Estado de los 8 elementos SDD
| Elemento | Estado |
|----------|--------|
| Actores | [COMPLETO / INCOMPLETO — detalle] |
| Historias de Usuario | [COMPLETO / INCOMPLETO — detalle] |
| Recorridos de Usuario | [COMPLETO / INCOMPLETO — detalle] |
| Resultados y Éxito | [COMPLETO / INCOMPLETO — detalle] |
| Instrucciones Inambiguas | [COMPLETO / INCOMPLETO — detalle] |
| Criterios de Aceptación | [COMPLETO / INCOMPLETO — detalle] |
| Checklist de Validación | [COMPLETO / INCOMPLETO — detalle] |
| Fuera de Alcance | [COMPLETO / INCOMPLETO — detalle] |

### HUs incompletas
<!-- Si no hay HUs incompletas, escribir "Ninguna." -->
| HU | Título | Gaps pendientes |
|----|--------|-----------------|
| [HU-XXX] | [título] | [P-XXX, P-YYY] |

### Asunciones por defecto aplicadas
<!-- Si no se aplicaron asunciones, escribir "Ninguna." -->
| Sección | Asunción aplicada | Origen (gap) |
|---------|-------------------|--------------|
| [sección] | [texto de la asunción] | [P-XXX] |

### Contaminaciones de Pureza procesadas
<!-- Si no hubo contaminaciones, escribir "Ninguna." -->
| ID | Acción | Detalle |
|----|--------|---------|
| [C-XXX] | [ACEPTAR / EDITAR / RECHAZAR / defecto] | [breve descripción] |

---

## Actores
| Actor | Descripción | Capacidades en este spec |
|-------|-------------|--------------------------|
| [nombre] | [quién es] | [qué puede hacer] |

---

## Historias de Usuario
### HU-001: [título]
Como [usuario] / quiero [acción] / para que [valor]

---

## Recorridos de Usuario
### Journey 1: [nombre]
Actor: [quién] | Objetivo: [qué quiere]
1. [paso]
2. [paso]

Estado de éxito: [qué experimenta el usuario al completar]
Flujos alternativos: Si [condición] → [resultado]

---

## Resultados y Éxito
[Definición observable de qué significa "hecho" para este spec. No cómo se implementa — qué experimenta el usuario cuando todo funciona correctamente.]

---

## Instrucciones Inambiguas
### Reglas de comportamiento
- [Regla concreta de comportamiento que no encaja en un Journey ni en un CA individual]

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| [pantalla/estado] | [acción o condición] | [destino exacto] |

<!-- Omitir esta sección si no hay flujos de navegación condicional en este spec -->

---

## Criterios de Aceptación
### CA-001: [título] ← HU-001
GIVEN [precondición]
WHEN [acción del usuario]
THEN [resultado observable]

---

## Checklist de Validación
<!-- Marca [x] los items que puedes verificar directamente del spec que generaste -->
<!-- Deja [ ] los que requieren validación humana posterior -->
- [ ] Actores identificados
- [ ] Flujos principales descritos paso a paso
- [ ] Estados de éxito definidos
- [ ] Edge cases documentados
- [ ] Estados de error definidos
- [ ] Ambigüedades resueltas
- [ ] Cada CA referencia su HU padre
- [ ] Cada CA es testable de forma independiente
- [ ] Destinos de navegación enumerados con sus variantes

---

## Fuera de Alcance
[Lista explícita de funcionalidades excluidas de este spec.]
[Si el cliente no definió exclusiones: "No se han definido exclusiones explícitas en esta versión del spec."]

---

<!-- Si quedan gaps sin resolver tras la integración: -->
## Items pendientes
- [PENDIENTE] [P-XXX]: [descripción del gap no resuelto]
