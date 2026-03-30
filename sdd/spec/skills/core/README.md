# Core — Knowledge Bases Compartidos

Este directorio contiene los **knowledge bases de Capa 3** que el agente `sdd-analyst` carga como contexto. Son reglas puras: no ejecutan lógica, no escriben archivos. Solo existen para ser inyectados en el contexto del agente según el modo activo.

---

## Skills disponibles

### `spec-expert`

**Qué es**: El SSoT de qué es y qué debe contener un Spec SDD válido.

**Contiene**:
- Los 8 elementos obligatorios (Actores, HUs, Journeys, Resultados, Instrucciones, CAs, Checklist, Fuera de Alcance)
- La Prueba de Pureza: un Spec describe "qué" y "para qué", nunca "cómo"
- Los 3 checks de validación: Completitud, Pureza y Testabilidad
- `references/prohibited_items.md`: tabla completa de elementos técnicos prohibidos
- `references/error_patterns.md`: patrones de contaminación técnica más frecuentes

**Usado en**: todos los modos (`analyze`, `finalize`, `validate`, `decompose`, `delta`, `fast-track`, `conflict`)

---

### `gap-conventions`

**Qué es**: El SSoT de las convenciones de gaps y marcadores de pendiente del pipeline.

**Contiene**:
- Formatos de ID: `[P-XXX]` para analyze/finalize/fast-track, `[D-XXX]` para delta
- Severidades: `[CRÍTICO]` (bloquea la siguiente fase) vs `[INFORMATIVO]` (continúa con asunción)
- El marcador `_(pendiente)_` para respuestas sin completar
- Reglas de bloqueo que los orquestadores deben respetar antes de avanzar

**Usado en**: `analyze`, `finalize`, `delta`, `fast-track`

---

### `decompose-expert`

**Qué es**: Las reglas para partir un Spec monolítico en Specs por feature.

**Contiene**:
- Definición de feature válida: unidad funcional cohesiva con journeys independientes, mínimo 3 CAs y actor claro
- Test de independencia: una feature no necesita contexto de otra para entenderse
- Reglas de ownership de shared models y criterios de desempate
- Formato del `_features.md` (índice de features con tabla de shared models)

**Usado en**: `decompose`, `fast-track`

---

### `conflict-expert`

**Qué es**: Las 5 reglas de detección de conflictos entre Specs SDD de un mismo proyecto.

**Contiene**:
- Regla 1 — HUs duplicadas: mismo actor + verbo + objetivo en features distintas
- Regla 2 — CAs contradictorios: mismo GIVEN/WHEN, THEN incompatibles
- Regla 3 — Scope overlap: el journey de una feature es el core de otra
- Regla 4 — Shared models inconsistentes: mismo modelo, definiciones distintas
- Regla 5 — Out-of-scope contradictorios: lo que una excluye, otra lo incluye
- Clasificación de severidad: `ALTA` (bloquea planificación) vs `MEDIA` (problema de frontera)

**Usado en**: `conflict`, `delta` (cuando existe `_features.md`), post-`decompose` (automático, no bloqueante)

---

## Principio de diseño

Ningún skill de este directorio tiene `model-invocation` activa. Son **contexto puro** — texto que el agente lee como reglas, no como instrucciones de ejecución. Esto garantiza que el razonamiento esté centralizado en el agente `sdd-analyst` (Capa 2) y que los knowledge bases no generen output propio.
