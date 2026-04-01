# Análisis de Feature: [Nombre de la Feature]
> Feature ID: F-00X | Fecha: [YYYY-MM-DD]
> PRD origen: [path/al/prd.md]
> Project Map: [path/al/prd_project_map.md]
> Generado via: wf-spec-map-analyze

---

## Contexto del mapa

> Esta feature cubre: [descripción de una frase extraída del project_map.md]
> Actor principal: [actor extraído del mapa]
> Interactúa con: [F-00Y (nombre), F-00Z (nombre) — o "Sin interacciones"]
> Shared models candidatos: [Modelo X (owner candidato: F-00Z) — o "Ninguno"]

---

## Estado general

> **[REQUIERE_TRABAJO | APROBADO_CON_OBSERVACIONES | APROBADO]**
> [Resumen en 1-2 frases del estado de esta feature en el PRD]

---

## Completitud: X/8 elementos presentes

| Elemento SDD | Estado | Notas |
|---|---|---|
| Actores | ✓ presente / ∂ parcial / ✗ ausente | [observación o —] |
| Historias de Usuario | ✓ presente / ∂ parcial / ✗ ausente | [observación o —] |
| Recorridos de Usuario | ✓ presente / ∂ parcial / ✗ ausente | [observación o —] |
| Resultados y Éxito | ✓ presente / ∂ parcial / ✗ ausente | [observación o —] |
| Instrucciones Inambiguas | ✓ presente / ∂ parcial / ✗ ausente | [observación o —] |
| Criterios de Aceptación | ✓ presente / ∂ parcial / ✗ ausente | [observación o —] |
| Checklist de Validación | ✓ presente / ∂ parcial / ✗ ausente | [observación o —] |
| Fuera de Alcance | ✓ presente / ∂ parcial / ✗ ausente | [observación o —] |

---

## Pureza: [APROBADO | CONTAMINADO]

> Fragmentos con contaminación técnica detectada (aplica Prueba de Pureza de `kb-spec-expert`):

| Fragmento | Motivo | Reescritura funcional propuesta |
|---|---|---|
| "[texto exacto]" | [por qué es técnico] | [versión funcional] |

> Si no hay contaminación → escribir "Sin contaminación técnica detectada."

---

## Testabilidad: [APROBADO | REQUIERE_MEJORA]

> CAs que no son verificables objetivamente o les falta GIVEN/WHEN/THEN:

| CA | Problema | Reformulación sugerida |
|---|---|---|
| [descripción del CA] | [qué le falta] | [reformulación completa] |

> Si todos son testables → escribir "Todos los comportamientos son verificables."

---

## Contaminación cross-feature

> Secciones del PRD que mezclan requisitos de esta feature con los de otras. Al responder los gaps de esta feature, ignora estas secciones — pertenecen a su feature correspondiente.

| Sección del PRD | Feature a la que pertenece |
|---|---|
| [referencia a la sección] | F-00X ([nombre-feature]) |

> Si no hay mezcla → escribir "No se detectó contaminación cross-feature."

---

## Puntos pendientes

### [P-001][CRÍTICO] [Título del gap]
- **Elemento afectado**: [Historias de Usuario / Criterios de Aceptación / etc.]
- **Pregunta**: [pregunta concreta para el cliente, sin opciones inventadas]
- **Respuesta**: _(pendiente)_

### [P-002][INFORMATIVO] [Título del gap]
- **Elemento afectado**: [elemento SDD]
- **Pregunta**: [pregunta concreta]
- **Asunción por defecto**: [lo que se aplicará si no hay respuesta]
- **Respuesta**: _(pendiente)_

---

## Próximos pasos

1. Responde los gaps `[CRÍTICO]` marcados como `_(pendiente)_` editando este archivo directamente
2. Responde los gaps `[INFORMATIVO]` si tienes la información (opcional — se aplican asunciones si no respondes)
3. Cuando todos los `[CRÍTICO]` de **todas las features** estén respondidos, ejecuta:
   ```
   /wf-spec-map-generate <prd.md>
   ```
