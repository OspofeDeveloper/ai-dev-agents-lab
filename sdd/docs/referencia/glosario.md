# Glosario

Términos del ecosistema SDD, en una línea. Los conceptos con desarrollo propio
enlazan a su explicación.

## Pipeline y artefactos

**PRD** (Product Requirements Document)
: Documento de negocio: problema, actores, alcance, reglas. Sin tecnología.

**Spec**
: Comportamiento observable de una feature, sin tecnología. Contiene los CAs.

**DESIGN.md**
: Contrato visual **persistente del producto** (color, tipografía, motion, voice).

**DESIGN_BRIEF.md**
: Decisiones de dirección visual cerradas antes de generar el `DESIGN.md`. Gate de la fase Design.

**Plan**
: El *cómo* técnico de una feature, fundamentado en la realidad del repo.

**Tasks**
: Pasos atómicos `T-00X` con dependencias, owner y trazabilidad al CA.

**Feature**
: Unidad funcional con artefactos por fase en `features/<nombre>/{spec,design,plan,tasks}/`.

## Identificadores y trazabilidad

**RF**
: Requisito funcional del PRD.

**HU**
: Historia de Usuario del Spec.

**CA** (Criterio de Aceptación)
: Condición testable en formato `GIVEN/WHEN/THEN`. La unidad de verdad del comportamiento.

**TC** (Test Case)
: Caso de prueba derivado de un CA (un TC ↔ exactamente un CA).

**T-00X / B-00X / E-00X / R-00X / TD-00X**
: IDs secuenciales de task / bug / enmienda / release / deuda técnica.

**Cadena de trazabilidad**
: `RF → HU → CA → TC → task → commit → release`. Cada eslabón apunta al anterior.

**SSoT** (Single Source of Truth)
: Fuente única de una verdad. Duplicarla = riesgo de drift.

## Estados y marcadores

**`[INCOMPLETO]` / `[CRÍTICO]`**
: Marcadores de hueco en un Spec que **bloquean** el avance de fase.

**`[INFERIDO]`**
: En specs de *characterization*, comportamiento sin evidencia en el código. Bloquea como `[INCOMPLETO]`.

**`[ASUNCIÓN]` / `[ASN-XXX]`**
: Afirmación de negocio del PRD sin material fuente, a confirmar por el humano en el review.

**`BORRADOR` / `VALIDADO`**
: Estados de un Plan. `VALIDADO` lo escribe solo `sdd-seal.py` tras verificar.

**`PENDIENTE / EN_CURSO / HECHA / BLOQUEADA`**
: Estados de una task, escritos solo por `sdd-task-state.py`.

**`APTO / APTO_CON_RESERVAS / NO_APTO`**
: Veredictos de QA. Solo `APTO`/`APTO_CON_RESERVAS` permiten release.

**`status_sync`**
: Estado de sincronización spec↔PRD (`in_sync` / `needs_review` / `stale`). La deriva real la detecta el hash.

**`PENDIENTE_GENERACIÓN`**
: Feature descubierta pero aún no generada (iteración por subset).

## Conceptos de diseño

[**Autor ≠ verificador**](../entender/funcional.md)
: El que genera un artefacto no certifica su validez; lo hace un script determinista.

[**Gate**](../entender/tecnico.md)
: Precondición de fase verificada mecánicamente (hook `PreToolUse`). Deniega con evidencia positiva.

**Sellado**
: Escritura de un estado de confianza tras verificar condiciones mecánicas.

[**Fail-open**](../entender/tecnico.md)
: Política de los gates: ante incertidumbre, permiten; solo deniegan con prueba.

[**Carga lazy**](../entender/tecnico.md)
: Conocimiento traído solo cuando se necesita (rules por `paths:`, kb por declaración del agente).

[**Overlay de stack**](../guias/contribuidor.md)
: Especialización de Plan/Tasks para un stack (p. ej. KMM), por sustitución de basename.

**Characterization**
: Spec/DESIGN derivado por ingeniería inversa de código/UI existente (brownfield).

**Modo ligero**
: Proporcionalidad para features pequeñas (menos secciones, ≥1 CA) **sin** relajar invariantes.

[**Back-edge / enmienda**](../guias/desarrollador.md)
: Aclaración de un CA ambiguo descubierto al implementar, sin re-descender el waterfall (`wf-spec-amend`).

**Layout de feature**
: Subcarpetas por fase (`spec/ design/ plan/ tasks/`) o el plano legacy. Ambos válidos, no mezclados.
