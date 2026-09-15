# Validación SDD: [nombre del spec]
> Fecha: [YYYY-MM-DD] | Archivo: [path]

---

## Resultado: [APROBADO | REQUIERE_REVISIÓN]
> [1-2 frases del estado. Si REQUIERE_REVISIÓN: menciona los bloqueantes principales.]

<!-- El umbral NO es de juicio: lo fija `kb-spec-expert` (Paso 4 de «Cómo validar un
     Spec»). REQUIERE_REVISIÓN exige al menos un bloqueante de los tres tipos. Una
     nota no bloqueante NUNCA degrada el veredicto. -->

### Hallazgos BLOQUEANTES (degradan el veredicto)
<!-- Si no hay ninguno, escribe "Ninguno". Nunca lo dejes vacío: el silencio no se
     distingue de haberlo olvidado, y este bloque decide si el spec se sella. -->
1. [elemento obligatorio ausente | contaminación dura citada | CA no verificable]

### Notas NO bloqueantes (no cambian el veredicto)
- [borderline aceptable, con el porqué | sugerencia de redacción | materia de Plan]

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
