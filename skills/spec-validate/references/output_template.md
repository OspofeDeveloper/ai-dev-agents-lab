# Validación SDD: [nombre del spec]
> Fecha: [YYYY-MM-DD] | Archivo: [path]

---

## Resultado: [APROBADO | REQUIERE_REVISIÓN]
> [1-2 frases del estado. Si REQUIERE_REVISIÓN: menciona los bloqueantes principales.]

---

## Completitud: X/8 elementos presentes
- [x/ ] Actores
- [x/ ] Historias de Usuario
- [x/ ] Recorridos de Usuario
- [x/ ] Resultados y Éxito
- [x/ ] Instrucciones Inambiguas
- [x/ ] Criterios de Aceptación
- [x/ ] Checklist de Validación
- [x/ ] Fuera de Alcance

---

## Pureza: [APROBADO | CONTAMINADO]

<!-- Si APROBADO: "Sin contaminaciones detectadas." -->

#### [C-001] [Título]
- **Cita**: "[fragmento exacto]"
- **Problema**: [por qué es técnico]
- **Reescritura sugerida**: "[versión funcional]"

---

## Testabilidad: [APROBADO | REQUIERE_MEJORA]

<!-- Si APROBADO: "Todos los CAs son verificables objetivamente." -->

#### [CA-001] [Título]
- **Problema**: [vago / GIVEN o THEN incompleto / sin referencia HU padre]
- **Reformulación sugerida**:
  ```
  GIVEN [precondición]
  WHEN [acción]
  THEN [resultado observable]
  ```
