# Spec: [Nombre de la Feature]
> Versión: 1.0 | Fecha: [YYYY-MM-DD]
> Spec monolítico origen: [path/_spec.md]
> Feature ID: F-00X
> Source requirements: [path/al/documento_origen.md]
> derived_from_prd: [path/al/PRD.md | N/A]
> derived_from_prd_version: [1.0 | unknown | N/A]
> derived_from_prd_hash: [N/A | sha256:<hex>]
<!-- derived_from_prd_hash lo escribe `sdd-sync-check.py seal`, nunca a mano: déjalo en N/A.
     La instrucción va AQUÍ y no dentro del corchete a propósito ([[D-084]]): un placeholder
     que lleva la explicación dentro del valor se sustituye a medias — quien pone el hash se
     deja el rabo pegado y el campo, que es contrato parseable, queda con prosa dentro. -->
> derived_from_change: [CR-XXX | N/A]
> status_sync: [in_sync | needs_review | stale | unknown]
> Origen de alcance: [PRD | PRD + analysis respondido | characterization]
<!-- Specs de caracterización (wf-spec-from-code): añadir Origen: characterization,
     Evidencia base: commit SHA, y campo Evidencia en cada CA — ver kb-spec-characterization. -->
> Avisos de gobernanza: [ninguno | alcance derivado desde P-00X]
> Respuestas del análisis aplicadas: [ninguna | P-00X, P-00Y]

---

## Decisiones derivadas del analysis
<!-- Omitir si no aplica. Usar solo cuando el scope se apoye en respuestas resueltas del _analysis.md que expandan o concreten el alcance. -->
- **[P-00X]**: [respuesta resumida] → [impacto funcional derivado]

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| [nombre] | [quién es — copia literal del spec monolítico] | [qué puede hacer en esta feature] |

---

## Historias de Usuario
<!-- Solo las HUs que pertenecen al scope de esta feature — copia literal del spec monolítico -->
### HU-001: [título]
Como [usuario] / quiero [acción] / para que [valor]

---

## Recorridos de Usuario
<!-- Solo los Journeys de esta feature — copia literal del spec monolítico -->
### Journey 1: [nombre]
Actor: [quién] | Objetivo: [qué quiere]
1. [paso]
2. [paso]

Estado de éxito: [qué experimenta el usuario al completar]
Flujos alternativos: Si [condición] → [resultado]

---

## Resultados y Éxito
[Definición de "hecho" para esta feature — filtrada del spec monolítico]

---

## Instrucciones Inambiguas
### Reglas de comportamiento
[Reglas del spec monolítico filtradas al scope de esta feature]
<!-- Solo las reglas de ESTA feature ([[D-111]]). Las de un modelo compartido de otra feature
     viven en su contrato (se citan en "Modelos de otras features"), y las transversales del
     producto viven en el PRD: se citan por lo que dicen ("como fija el PRD, el histórico conserva
     la cuenta de cada movimiento"), no se copian como regla propia. -->

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
[Destinos filtrados al scope de esta feature]

<!-- Omitir si no hay navegación condicional en esta feature -->

---

## Contrato de modelos compartidos
<!-- Solo si esta feature es DUEÑA de algún modelo compartido (índice: "Modelos compartidos
     (owner)"); si no, omite la sección entera. Es la API pública del modelo ([[D-111]]): la ÚNICA
     fuente de sus reglas. Las demás features la citan y no la reescriben.
     - Un `### <Modelo>` por cada modelo compartido del que esta feature es dueña.
     - "Orígenes externos": una fila por cada operación de OTRA feature que crea o cambia el
       modelo —sácalas de la discovery (journeys de las features que lo referencian) y del PRD—.
       Toda feature que escribe sobre el modelo tiene al menos una fila; las que solo lo leen, no.
     - Si una fila no está decidida (¿se puede tocar desde aquí?, ¿qué pasa con su origen?), NO la
       inventes: abre UN gap [CRÍTICO] por modelo con todas las filas abiertas a la vista, para que
       se decidan juntas en una sola pregunta.
     - Una fila que atiende una petición de otra feature la cita: `F-00Y (nombre) · R-00N`. -->
### [Modelo]
- **Ciclo de vida / estados**: [estados por los que pasa, o "sin estados"]
- **Qué puede hacer el [actor]**: [crear · editar · eliminar, y sus límites]
- **Invariantes** (nunca puede pasar): [p. ej. el saldo disponible nunca queda negativo]

#### Orígenes externos
| Origen | Operación | Qué crea o cambia | ¿Se puede tocar desde aquí? | Si se toca, qué pasa con su origen |
|--------|-----------|-------------------|-----------------------------|-----------------------------------|
| F-00Y (nombre) | [operación de esa feature] | [qué crea o cambia en el modelo] | [sí · no · solo junto con X] | [qué le pasa al origen] |

---

## Modelos de otras features
<!-- Solo si esta feature USA modelos compartidos de los que es dueña otra feature (índice:
     "Modelos compartidos (ref)"); si no, omite la sección entera ([[D-111]]).
     - Una fila por cada uso. La columna `Uso` dice `lectura` si solo lo lee y `escritura` si lo
       crea o lo cambia: es lo que decide si el dueño tiene que recogerlo en su catálogo (D-112).
     - La regla NO se escribe aquí ni en los CAs: se cita al contrato del dueño. Un CA puede decir
       el efecto observable de SU operación ("se registra un gasto") pero no cómo se comporta
       después ese modelo (si se edita, si se borra, cómo aparece): eso es del dueño.
     - Si necesitas una regla que el contrato del dueño no tiene, o una distinta, NO la escribas:
       regístrala como petición al dueño. Se atiende con un cambio en el dueño, que la cita en su
       catálogo de orígenes; aquí no hay que volver a tocar nada. -->
| Modelo | Dueña | Uso | Qué hace esta feature con él | Regla que aplica |
|--------|-------|-----|------------------------------|------------------|
| [Modelo] | F-00X | [lectura · escritura] | [crea / cambia … al …, o qué lee y para qué] | [Contrato de F-00X · Orígenes externos de F-00X] |

### Peticiones al dueño
<!-- Omitir si no hay. Formato contrato: lo parsea `sdd-model-contracts.py`. -->
### [R-001] A F-00X ([Modelo]): [qué necesita esta feature, en una frase sobre el comportamiento]
- **Por qué**: [qué operación de esta feature lo necesita]
- **Ejemplo**: [un caso concreto con el actor, sacado del spec o del PRD; si no hay, omite la línea]
<!-- Sin campo de estado (D-112): está atendida cuando el dueño la cita en su catálogo
     (`F-00Y (nombre) · R-00N`), y eso lo comprueba un script. Un "Estado: pendiente" aquí sería
     una segunda fuente de verdad que se queda vieja en cuanto el dueño la atiende. -->

---

## Criterios de Aceptación
<!-- Renumerados desde CA-001 — copia literal del spec monolítico, solo filtrados -->
### CA-001: [título] ← HU-001
GIVEN [precondición]
WHEN [acción del usuario]
THEN [resultado observable]

---

## Checklist de Validación
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
[Exclusiones relevantes a esta feature extraídas del spec monolítico, o "No se han definido exclusiones explícitas para esta feature."]
