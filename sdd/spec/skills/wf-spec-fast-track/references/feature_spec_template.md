# Spec: [Nombre de la Feature]
> Versión: 1.0 | Fecha: [YYYY-MM-DD]
> Spec monolítico origen: [path/_spec.md]
> Feature ID: F-00X
> Source requirements: [path/al/documento_origen.md]
> derived_from_prd: [path/al/PRD.md | N/A]
> derived_from_prd_version: [1.0 | unknown | N/A]
> derived_from_prd_hash: [N/A — lo escribe `sdd-sync-check.py seal`, nunca a mano]
> derived_from_change: [CR-XXX | N/A]
> status_sync: [in_sync | needs_review | stale | unknown]
> Origen de alcance: [PRD | PRD + analysis respondido | characterization]
<!-- Specs de caracterización (wf-spec-from-code): añadir Origen: characterization,
     Evidencia base: commit SHA, y campo Evidencia en cada CA — ver kb-spec-characterization. -->
> Avisos de gobernanza: [ninguno | alcance derivado desde P-00X]

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

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
[Destinos filtrados al scope de esta feature]

<!-- Omitir si no hay navegación condicional en esta feature -->

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
