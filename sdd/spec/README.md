# SDD Spec — Etapas 1 y 2: Specify y Decompose

Este directorio contiene todos los agentes y skills que transforman un documento de requisitos en Specs SDD válidos y autocontenidos por feature. Cubre las dos primeras etapas del pipeline Spec Driven Development: **Specify** (del PRD al Spec monolítico) y **Decompose** (del Spec monolítico a Specs por feature).

Diagramas detallados de esta fase: [DIAGRAMS.md](DIAGRAMS.md).

## Precondición de esta fase

La fase `spec` **no arranca desde cero**. Requiere un PRD o documento de requisitos previo, normalmente salido de `sdd/prd`.

Si todavía no existe ese artefacto, hay que volver a la fase anterior y usar `wf-prd-create` o `wf-prd-review`. Esta fase no debe depender de la fase PRD completa, pero sí instala los handoffs mínimos cross-fase que necesita (`wf-prd-review`, `wf-prd-change`, `prd-expert` y sus kb).

---

## Casos de uso

### 1. Proyecto nuevo (Greenfield) — flujo completo

Tienes un PRD o documento de requisitos y quieres convertirlo en Specs SDD para todo el producto de una vez.

```
/wf-spec-analyze prd.md
  → genera prd_analysis.md con:
      · mapa de elementos del Spec que se generarán desde el PRD (informativo)
      · pureza del PRD (contaminación técnica si la hay)
      · gaps [CRÍTICO] e [INFORMATIVO] para responder
      · marcador `[PUEDE_REQUERIR_CR]` cuando una futura respuesta puede expandir el producto
  → veredicto: LISTO_PARA_SPECS | LISTO_PARA_SPECS_CON_PREGUNTAS | REQUIERE_LIMPIEZA_PRD
  Las respuestas a gaps se anotan en el `_analysis.md`. Si aparece un cambio real de producto, se formaliza con `wf-prd-change` antes de resincronizar derivados.

[si el análisis deja gaps [CRÍTICO], decide:]
  a) responderlos en prd_analysis.md
  b) continuar igualmente aceptando HUs [INCOMPLETO]

/wf-spec-features-first prd.md
  → si faltaba `prd_analysis.md`, lo genera y se detiene
  → si quedan gaps [CRÍTICO], se detiene salvo que añadas `--allow-open-critical-gaps`
  → si las respuestas del analysis introducen expansión de capacidad, se detiene y remite a `wf-prd-change`, salvo override explícito con `--allow-derived-scope-from-analysis`
  → si el discovery detecta más de 5 features, se detiene salvo que añadas `--all-features`
  → ejecuta discover + fast-track por feature en paralelo
  → genera prd_discovery.md, prd_features.md
  → genera features/<nombre>/spec/<nombre>_spec.md por cada feature
  → ejecuta verificación de conflictos y readiness automáticamente
```

**Cuándo usarlo**: cuando tienes un PRD acotado y quieres procesar todas las features en una sola pasada. Si el discovery saca muchas features, el propio workflow te empuja a iterar por subset para controlar coste y contexto.

---

### 1.b. Proyecto nuevo (Greenfield) — iterativo por fases / subset

Tienes un PRD que cubre todo el producto pero solo quieres generar las specs de un subconjunto de features (por ejemplo, "fase 1" o "iteración inicial"). Las features no se definen en el PRD: se identifican en el discovery, así que primero hay que ejecutarlo y luego elegir el subset.

```
/wf-spec-analyze prd.md
  → genera prd_analysis.md (igual que en el caso 1)

[responde gaps [CRÍTICO] o decide continuar luego con `--allow-open-critical-gaps`]

/wf-spec-discover prd.md --analysis prd_analysis.md
  → genera prd_discovery.md con el mapa completo de features (F-001..F-N)

# Si el analysis contiene respuestas expansivas y se decide continuar
# excepcionalmente con alcance derivado:
# /wf-spec-discover prd.md --analysis prd_analysis.md --allow-derived-scope-from-analysis

[revisa el mapa y elige qué Feature IDs entran en esta iteración]

/wf-spec-features-first prd.md --features F-001,F-002,F-003
  → genera specs solo para las features indicadas
  → prd_features.md indexa TODAS las features:
      · las generadas en esta iteración → LISTA / BLOQUEADA / REQUIERE_CAMBIO_PRD
      · las que aún no se han procesado → PENDIENTE_GENERACIÓN
  → conflict + readiness se ejecutan sobre el subset

# Más adelante, cuando quieras la siguiente fase:
/wf-spec-features-first prd.md --features F-004,F-005
  → añade specs sin tocar los anteriores
  → prd_features.md se actualiza incrementalmente
```

**Cuándo usarlo**: cuando el PRD describe un producto amplio pero el delivery va por fases. Permite priorizar features sin tener que rehacer el PRD ni perder la visión global del producto.

**Recomendación operativa**: para PRDs con más de 5 features, este modo iterativo pasa a ser el camino por defecto. El modo full queda como override explícito con `--all-features`.

**Nota de gobernanza**: si una respuesta en `_analysis.md` añade una entidad persistente, un catálogo reutilizable, una nueva granularidad funcional, un nuevo modelo owner o un flujo adicional no comprometido en el PRD, no debe derivarse directamente a specs. Primero hay que formalizarlo con `wf-prd-change`. Si excepcionalmente se continúa con `--allow-derived-scope-from-analysis`, los derivados deben marcar `Origen de alcance: PRD + analysis respondido` y dejar `Avisos de gobernanza`.

---

### 2. Feature única sin spec previo (Fast-Track)

Quieres documentar solo una capacidad concreta sin pasar por el spec monolítico. Útil para añadir features a proyectos maduros o arrancar documentando una sola área.

```
/wf-spec-fast-track notifications.md --capability push-notifications
  → genera features/push-notifications/spec/push-notifications_spec.md directamente
```

**Cuándo usarlo**: cuando el documento de entrada ya describe una sola capacidad acotada y no necesitas documentar el sistema completo. El spec resultante puede tener `## Items Pendientes` si hay gaps críticos, y `## Asunciones Aplicadas` si se resolvieron gaps informativos con asunciones razonables.

---

### 3. Evolución incremental de un spec existente (Delta)

El software ya existe, hay un `_spec.md` en producción y quieres añadir o modificar una funcionalidad sin regenerar todo.

```
/wf-spec-delta analyze features/auth/spec/auth_spec.md --new-reqs new_auth_requirements.md
  → genera features/auth/spec/auth_delta_analysis.md con HUs/CAs añadidos, modificados, eliminados

[revisa el delta, responde gaps [CRÍTICO]]

/wf-spec-delta apply features/auth/spec/auth_spec.md features/auth/spec/auth_delta_analysis.md
  → actualiza auth_spec.md (versión 1.0 → 1.1) con sección Changelog
```

**Cuándo usarlo**: cuando el spec ya existe y el cambio es incremental (nueva HU, modificación de un comportamiento, eliminación de una funcionalidad deprecada). El delta es quirúrgico: no toca lo que no cambia.

#### Completar HUs incompletas (resolver gaps pendientes)

Si el spec tiene HUs marcadas `[INCOMPLETO]` por gaps `[CRÍTICO]` sin responder:

```
[responde los gaps [P-XXX] en el _analysis.md]

/wf-spec-gap-resolve features/auth/spec/auth_spec.md
  → auto-descubre el _analysis.md, integra respuestas, completa HUs y CAs, versión 1.0 → 1.1
```

**Cuándo usarlo**: después de generar un feature spec que dejó HUs incompletas por gaps sin responder. El usuario responde los gaps en el `_analysis.md` y `wf-spec-gap-resolve` integra las respuestas en el feature spec.

#### CA ambiguo descubierto al implementar (back-edge tasks→spec)

Si durante `wf-task-run` el dev descubre que un CA admite varias implementaciones y el texto no determina cuál:

```
/wf-spec-amend features/auth/spec/auth_spec.md --ca CA-003 --from-task T-004
  → gate de clasificación (¿aclaración o cambio de comportamiento?), confirmación humana,
    edición quirúrgica del CA con changelog E-00X, anotación `Enmienda pendiente` en el plan
    (solo retiene las tasks que referencian ese CA — el resto sigue ejecutable)
```

**Cuándo usarlo**: solo para ACLARACIONES estrictas (la intención del CA no cambia; el texto era ambiguo). Si el comportamiento esperado cambia, la vía es `/wf-spec-delta`; si la divergencia es sobre código ya entregado, `/wf-bug`.

#### Cambio de producto tras entrar en Spec

Si la "respuesta" realmente cambia el alcance o el roadmap del producto:

```
/wf-prd-change prd.md --new-reqs cambio.md
  → actualiza el PRD, registra el cambio y deja trazabilidad

/wf-prd-sync-impact prd.md
  → detecta qué discovery/specs/planes/tasks quedaron afectados

/wf-spec-sync-from-prd analyze prd.md
  → genera requisitos de sync por feature

/wf-spec-sync-from-prd apply prd.md --features F-001,F-003
  → resincroniza los specs afectados
```

**Cuándo usarlo**: cuando el producto vigente cambia de verdad, por ejemplo mover una capacidad de fase 2 a MVP.

---

### 4. Validar un spec tras edición manual

Editas manualmente un `_spec.md` y quieres verificar que no introdujiste contaminación técnica ni rompiste la estructura SDD.

```
/wf-spec-validate features/auth/spec/auth_spec.md
  → imprime informe APROBADO / REQUIERE_REVISIÓN (no genera archivo)
```

**Cuándo usarlo**: después de cualquier edición manual a un spec. También útil como gate antes de ejecutar `/wf-prepare-plan`.

---

### 5. Detectar conflictos entre specs de features

Quieres verificar que los specs de las diferentes features del proyecto son coherentes entre sí: sin HUs duplicadas, CAs contradictorios ni scope overlap.

```
/wf-spec-conflict features/auth/spec/auth_spec.md --features-dir features/
  → genera features/auth/spec/auth_conflict_report.md si hay conflictos
```

**Cuándo usarlo**: después de modificar un spec existente o añadir una nueva feature con fast-track o delta, para verificar que el cambio no choca con el resto del sistema. También se ejecuta automáticamente al final de `/wf-spec-features-first` (modo no bloqueante).

---

### 6. Exploración o diagnóstico de artefactos Spec

Quieres entender el estado actual de un PRD, de un spec o de un conjunto de artefactos antes de decidir el siguiente paso.

```
sdd-spec-explorer
  → diagnostica el estado
  → identifica gaps, contaminación o ambigüedad de scope
  → recomienda workflow o agente siguiente
```

**Cuándo usarlo**: cuando la duda principal es “qué tengo delante” o “qué workflow corresponde ahora”.

---

### 7. Planificación del approach sobre specs

La petición es ambigua o mezcla varias intenciones (crear, mejorar, dividir, evolucionar, auditar) y quieres decidir el approach correcto antes de ejecutar nada.

```
sdd-spec-planner
  → separa intención
  → ordena fases
  → recomienda workflows/agentes
```

**Cuándo usarlo**: cuando el problema todavía necesita descomposición operativa.

---

### 8. Consulta directa sobre qué es un Spec SDD

Preguntas conceptuales o revisión de un spec a mano, sin pasar por el flujo orquestado.

```
sdd-spec-explorer
```

**Cuándo usarlo**: para aprender, revisar o depurar specs directamente en conversación, sin invocar el pipeline completo.

---

## Mapa de componentes

La fase `spec` se apoya en tres tipos de piezas:

- `wf-*`: puntos de entrada operativos. Parsean argumentos, validan precondiciones y delegan el trabajo.
- agentes: workers especializados por tipo de razonamiento (`explorer`, `planner`, `writer`, `auditor`).
- `kb-*`: conocimiento de fondo cargado por los agentes como contexto reusable.

La lógica exacta de routing y la política de skills viven en [CLAUDE.md](CLAUDE.md). Este README mantiene solo el mapa funcional de la fase.

### Workflows

| Skill | Comando | Produce |
|-------|---------|---------|
| `wf-spec-analyze` | `/wf-spec-analyze` | `_analysis.md` (mapa Spec, pureza del PRD, gaps de negocio) |
| `wf-spec-validate` | `/wf-spec-validate` | Informe inline (sin archivo) |
| `wf-spec-features-first` | `/wf-spec-features-first [--features F-XXX,...] [--allow-open-critical-gaps] [--allow-derived-scope-from-analysis] [--all-features]` | `_discovery.md`, `_features.md` (Project Hub incremental con estados canónicos y trazabilidad de gobernanza), `features/<x>/spec/<x>_spec.md` |
| `wf-spec-discover` | `/wf-spec-discover [--analysis <analysis.md>] [--allow-derived-scope-from-analysis]` | `_discovery.md` con mapa de features y metadata de gobernanza |
| `wf-spec-fast-track` | `/wf-spec-fast-track` | `features/<x>/spec/<x>_spec.md` directamente, con marca de origen de alcance si aplica |
| `wf-spec-conflict` | `/wf-spec-conflict` | `_conflict_report.md` |
| `wf-spec-delta` | `/wf-spec-delta` | `_delta_analysis.md` (analyze), spec actualizado (apply) |
| `wf-spec-gap-resolve` | `/wf-spec-gap-resolve` | spec actualizado desde `_analysis.md` |
| `wf-spec-amend` | `/wf-spec-amend --ca CA-XXX [--from-task T-00X]` | CA aclarado con changelog `E-00X`, anotación `Enmienda pendiente` en el `_plan.md` (vía `sdd-amend.py`) |
| `wf-prd-change` | `/wf-prd-change` | PRD actualizado, `product-changelog.md`, `changes/CR-XXX/change-request.md`, `changes/CR-XXX/decision.md` |
| `wf-prd-sync-impact` | `/wf-prd-sync-impact` | `_sync_report.md` |
| `wf-spec-sync-from-prd` | `/wf-spec-sync-from-prd` | `*_sync_requirements.md`, specs resincronizados |
| `wf-spec-readiness` | `/wf-spec-readiness` | `_readiness_report.md`, actualiza estado en `_features.md` |

### Agentes

| Agente | Modos soportados | Invocado desde |
|--------|-----------------|----------------|
| `sdd-spec-explorer` | diagnóstico de PRD/spec, análisis de gaps, discovery | `wf-spec-analyze`, `wf-spec-discover`, exploración directa |
| `sdd-spec-planner` | planificación de approach | uso directo por el orquestador cuando la petición es ambigua |
| `sdd-spec-writer` | fast-track, delta apply, sync desde PRD, escritura de artefactos | `wf-spec-fast-track`, `wf-spec-delta`, `wf-spec-gap-resolve`, `wf-spec-amend`, `wf-spec-sync-from-prd`, `wf-spec-features-first` |
| `sdd-spec-auditor` | validate, conflict, readiness, sync impact | `wf-spec-validate`, `wf-spec-conflict`, `wf-spec-readiness`, `wf-prd-sync-impact` |

### Knowledge bases

| Skill | Tipo | Usado en modos |
|-------|------|----------------|
| `kb-spec-expert` | Conocimiento SDD (8 elementos, Prueba de Pureza, Testabilidad) | Todos |
| `kb-decompose-expert` | Partición de features, shared models, ownership | `discover`, `fast-track` |
| `kb-conflict-expert` | 5 reglas de detección de conflictos entre specs | `conflict` |
| `kb-gap-conventions` | SSoT de convenciones de gaps | Todos los modos que generen o verifiquen gaps |
| `kb-traceability-rules` | Trazabilidad entre PRD, specs, plan y tasks | `gap-resolve`, `sync-from-prd`, `readiness`, `sync-impact` |
| `kb-prd-expert` ⚠ | Reglas del PRD (cargada por agentes Spec para leer el PRD de entrada) | `analyze`, `discover`, `fast-track`, exploración |
| `kb-product-change-governance` ⚠ | Reglas para distinguir gap vs. change request y gestionar impacto de negocio | `analyze`, `gap-resolve`, `sync-from-prd`, `sync-impact`, planning |

> ⚠ `kb-prd-expert` y `kb-product-change-governance` viven físicamente en `sdd/prd/skills/`. Son kb cross-fase. La carga concreta por agente:
> - `kb-prd-expert`: `sdd-spec-explorer`, `sdd-spec-writer`, `sdd-spec-planner` (el auditor no la necesita porque audita specs ya escritos).
> - `kb-product-change-governance`: los 4 agentes Spec.
>
> **`install.sh spec` ya instala automáticamente estas dos kb cross-fase y también `wf-prd-change`, `wf-prd-review` + `prd-expert`,** porque el ecosistema Spec necesita ese handoff cuando una respuesta a un gap se convierte en cambio real de producto o cuando el analyze exige limpiar el PRD antes de continuar.

---

## Artefactos producidos

```
proyecto/
├── prd.md                                    ← Input
├── prd_analysis.md                           ← /wf-spec-analyze (recomendado)
├── prd_discovery.md                          ← /wf-spec-discover
├── prd_features.md                           ← /wf-spec-features-first — PROJECT HUB (index + trazabilidad + estado)
├── prd_sync_report.md                        ← /wf-prd-sync-impact
├── prd_conflict_report.md                    ← /wf-spec-features-first (automático) o /wf-spec-conflict
├── prd_readiness_report.md                   ← /wf-spec-readiness
└── features/
    └── <nombre-feature>/
        ├── README.md                         ← /wf-spec-fast-track
        ├── spec/
        │   ├── <nombre>_spec.md              ← /wf-spec-fast-track
        │   ├── <nombre>_delta_analysis.md    ← /wf-spec-delta analyze
        │   ├── <nombre>_sync_requirements.md ← /wf-spec-sync-from-prd analyze
        │   └── <nombre>_conflict_report.md   ← /wf-spec-conflict
        ├── design/                           ← etapa Design (flows, views, ui_prompt)
        ├── plan/
        │   └── <nombre>_plan.md              ← /wf-prepare-plan (etapa siguiente)
        └── tasks/
            └── <nombre>_tasks.md             ← /wf-prepare-tasks (etapa siguiente)
```

> Features creadas con el layout plano legacy (todos los artefactos directamente en `features/<nombre>/`) siguen siendo válidas: los workflows leen ambos layouts y no los mezclan dentro de una misma feature.

---

## Checkpoints humanos

El pipeline nunca es completamente automático. Estos son los momentos donde el humano debe intervenir:

| Momento | Qué hacer | Bloquea si no se hace |
|---------|-----------|-----------------------|
| Tras `analyze` | Responder gaps `[CRÍTICO]` con `_(pendiente)_` en `_analysis.md` (en el propio archivo, no en el PRD) | No bloquea generación de specs, pero las HUs afectadas quedan `[INCOMPLETO]` y bloquean `prepare-plan` |
| Tras `analyze` o validación con cliente | Si la respuesta cambia el alcance o el roadmap, ejecutar `wf-prd-change` antes de seguir | Sí — evita derivar specs desde una verdad de negocio obsoleta |
| Tras `analyze` | Responder gaps `[INFORMATIVO]` con `_(pendiente)_` (opcional) | No — se aplican asunciones por defecto |
| Tras `analyze` con veredicto `REQUIERE_LIMPIEZA_PRD` | Aplicar las reescrituras de la sección Pureza al PRD y volver a ejecutar `/wf-spec-analyze` | Sí — único caso en que se toca el PRD por contaminación técnica dentro del analyze |
| Tras `discover` (modo iterativo) | Elegir los Feature IDs que entran en la próxima iteración | Sí — `wf-spec-features-first --features` los necesita |
| Tras `features-first` | Revisar `_features.md` y validar la partición de features | No — pero afecta la calidad del plan |
| Tras `features-first` | Revisar `_conflict_report.md` si hay conflictos `ALTA` | No — pero pueden propagarse problemas al plan |
| Tras `wf-prd-sync-impact` | Revisar artefactos `stale` o `needs_review` y decidir qué features resincronizar | Sí — bloquea avanzar con specs desalineados |
| Tras `delta analyze` | Responder gaps `[CRÍTICO]` con `_(pendiente)_` en `_delta_analysis.md` | Sí — `delta apply` no avanza |

---

## Estructura de directorios

```
sdd/spec/
├── CLAUDE.md                                  ← orquestador local de la fase Spec
├── README.md                                  ← este archivo
├── agents/
│   ├── sdd-spec-auditor.md                    ← L2 worker: auditoría
│   ├── sdd-spec-explorer.md                   ← L2 worker: diagnóstico
│   ├── sdd-spec-planner.md                    ← L2 worker: planificación
│   └── sdd-spec-writer.md                     ← L2 worker: escritura/evolución
├── shared/
│   └── templates/
│       ├── feature_readme_template.md
│       └── feature_spec_template.md
└── skills/
    ├── kb-conflict-expert/
    │   └── SKILL.md
    ├── kb-decompose-expert/
    │   └── SKILL.md
    ├── kb-gap-conventions/
    │   └── SKILL.md
    ├── kb-spec-expert/
    │   └── SKILL.md
    ├── kb-traceability-rules/
    │   └── SKILL.md
    ├── wf-prd-sync-impact/
    │   └── SKILL.md
    ├── wf-spec-analyze/
    │   ├── SKILL.md
    │   └── output_template.md
    ├── wf-spec-conflict/
    │   └── SKILL.md
    ├── wf-spec-delta/
    │   └── SKILL.md
    ├── wf-spec-discover/
    │   └── SKILL.md
    ├── wf-spec-fast-track/
    │   └── SKILL.md
    ├── wf-spec-features-first/
    │   └── SKILL.md
    ├── wf-spec-gap-resolve/
    │   └── SKILL.md
    ├── wf-spec-readiness/
    │   └── SKILL.md
    ├── wf-spec-sync-from-prd/
    │   └── SKILL.md
    └── wf-spec-validate/
        └── SKILL.md
```

---

## Cómo extender el sistema

Para añadir un nuevo modo al pipeline:

1. **Crea el workflow** en `skills/wf-spec-<nombre>/SKILL.md` con el `agent:` especializado correcto (`sdd-spec-explorer`, `sdd-spec-writer` o `sdd-spec-auditor`). Aquí van las instrucciones paso a paso de qué debe hacer el agente.
2. **Crea o reutiliza una `kb-*`** solo si el modo necesita reglas transversales reutilizables por varios workflows o agentes.
3. **Registra el knowledge en el agente correcto**: añádelo al frontmatter `skills: [...]` y documenta su responsabilidad.
4. **Registra en `CLAUDE.md` y en este README** solo los entrypoints y handoffs que cambien el mapa funcional de la fase.

La política transversal para diseñar skills y agentes no vive ya en este README. Debe mantenerse como SSoT fuera de la fase, para evitar que `spec` replique reglas globales de frontmatter o arquitectura.
