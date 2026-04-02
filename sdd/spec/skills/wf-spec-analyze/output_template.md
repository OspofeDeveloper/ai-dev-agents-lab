# Análisis SDD: [Nombre del documento]

> **Generado por**: sdd-analyst (modo analyze)
> **Fecha**: [YYYY-MM-DD]
> **Archivo origen**: [path/al/archivo.md]

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
> - `[CRÍTICO]`: **debe responderse** antes de ejecutar `finalize`.
> - `[INFORMATIVO]`: si no se responde, se aplicará la "Asunción por defecto" indicada.

### [P-001][CRÍTICO] [Título del gap — describe qué falta]
- **Contexto**: [cita del documento o descripción de dónde aparece la ambigüedad]
- **Problema**: [por qué esto es un gap funcional que bloquea el spec]
- **Pregunta para el cliente**: [pregunta concreta y específica, sin opciones inventadas]
- **Respuesta**: _(pendiente)_

### [P-002][INFORMATIVO] [Título del gap — describe qué falta]
- **Contexto**: [cita del documento o descripción de dónde aparece la ambigüedad]
- **Pregunta para el cliente**: [pregunta concreta y específica, sin opciones inventadas]
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: [lo que se aplicará si el cliente no responde antes de ejecutar finalize]

---

## Próximos pasos

1. Revisar las contaminaciones de la sección "Pureza" y confirmar las reescrituras sugeridas
2. Responder los puntos `[CRÍTICO]` marcados como _(pendiente)_ — son obligatorios para continuar
3. Responder los puntos `[INFORMATIVO]` si tienes la información — si no, se aplicará la asunción por defecto
4. Una vez completados los `[CRÍTICO]`, ejecutar:
   ```
   /wf-spec-finalize [path/al/archivo.md]
   ```
