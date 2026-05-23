# SDD Spec — Etapas 1 y 2: Specify y Decompose

Este directorio contiene todos los agentes y skills que transforman un documento de requisitos en Specs SDD válidos y autocontenidos por feature. Cubre las dos primeras etapas del pipeline Spec Driven Development: **Specify** (del PRD al Spec monolítico) y **Decompose** (del Spec monolítico a Specs por feature).

## Precondición de esta fase

La fase `spec` **no arranca desde cero**. Requiere un PRD o documento de requisitos previo, normalmente salido de `sdd/prd`.

Si todavía no existe ese artefacto, hay que volver a la fase anterior y usar `wf-prd-create` o `wf-prd-review`. Esta fase no debe cargar ni orquestar workflows de PRD.

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
  → veredicto: LISTO_PARA_SPECS | LISTO_PARA_SPECS_CON_PREGUNTAS | REQUIERE_LIMPIEZA_PRD
  El PRD no se modifica salvo en REQUIERE_LIMPIEZA_PRD: las respuestas se anotan en el _analysis.md.

[edita prd_analysis.md y responde los gaps [CRÍTICO]]

/wf-spec-features-first prd.md
  → ejecuta discover + fast-track por feature en paralelo
  → genera prd_discovery.md, prd_features.md
  → genera features/<nombre>/<nombre>_spec.md por cada feature
  → ejecuta verificación de conflictos y readiness automáticamente
```

**Cuándo usarlo**: cuando tienes un PRD que cubre todo el sistema y quieres procesar todas las features en una sola pasada.

---

### 1.b. Proyecto nuevo (Greenfield) — iterativo por fases / subset

Tienes un PRD que cubre todo el producto pero solo quieres generar las specs de un subconjunto de features (por ejemplo, "fase 1" o "iteración inicial"). Las features no se definen en el PRD: se identifican en el discovery, así que primero hay que ejecutarlo y luego elegir el subset.

```
/wf-spec-analyze prd.md
  → genera prd_analysis.md (igual que en el caso 1)

[edita prd_analysis.md y responde los gaps [CRÍTICO]]

/wf-spec-discover prd.md --analysis prd_analysis.md
  → genera prd_discovery.md con el mapa completo de features (F-001..F-N)

[revisa el mapa y elige qué Feature IDs entran en esta iteración]

/wf-spec-features-first prd.md --features F-001,F-002,F-003
  → genera specs solo para las features indicadas
  → prd_features.md indexa TODAS las features:
      · las generadas en esta iteración → LISTA / BLOQUEADA_POR_GAPS
      · las que aún no se han procesado → PENDIENTE_GENERACIÓN
  → conflict + readiness se ejecutan sobre el subset

# Más adelante, cuando quieras la siguiente fase:
/wf-spec-features-first prd.md --features F-004,F-005
  → añade specs sin tocar los anteriores
  → prd_features.md se actualiza incrementalmente
```

**Cuándo usarlo**: cuando el PRD describe un producto amplio pero el delivery va por fases. Permite priorizar features sin tener que rehacer el PRD ni perder la visión global del producto.

---

### 2. Feature única sin spec previo (Fast-Track)

Quieres documentar solo una capacidad concreta sin pasar por el spec monolítico. Útil para añadir features a proyectos maduros o arrancar documentando una sola área.

```
/wf-spec-fast-track notifications.md --capability push-notifications
  → genera features/push-notifications/push-notifications_spec.md directamente
```

**Cuándo usarlo**: cuando el documento de entrada ya describe una sola capacidad acotada y no necesitas documentar el sistema completo. El spec resultante puede tener `## Items Pendientes` si hay gaps críticos, y `## Asunciones Aplicadas` si se resolvieron gaps informativos con asunciones razonables.

---

### 3. Evolución incremental de un spec existente (Delta)

El software ya existe, hay un `_spec.md` en producción y quieres añadir o modificar una funcionalidad sin regenerar todo.

```
/wf-spec-delta analyze features/auth/auth_spec.md --new-reqs new_auth_requirements.md
  → genera features/auth/auth_delta_analysis.md con HUs/CAs añadidos, modificados, eliminados

[revisa el delta, responde gaps [CRÍTICO]]

/wf-spec-delta apply features/auth/auth_spec.md features/auth/auth_delta_analysis.md
  → actualiza auth_spec.md (versión 1.0 → 1.1) con sección Changelog
```

**Cuándo usarlo**: cuando el spec ya existe y el cambio es incremental (nueva HU, modificación de un comportamiento, eliminación de una funcionalidad deprecada). El delta es quirúrgico: no toca lo que no cambia.

#### Completar HUs incompletas (resolver gaps pendientes)

Si el spec tiene HUs marcadas `[INCOMPLETO]` por gaps `[CRÍTICO]` sin responder:

```
[responde los gaps [P-XXX] en el _analysis.md]

/wf-spec-delta resolve features/auth/auth_spec.md
  → auto-descubre el _analysis.md, integra respuestas, completa HUs y CAs, versión 1.0 → 1.1
```

**Cuándo usarlo**: después de generar un feature spec que dejó HUs incompletas por gaps sin responder. El usuario responde los gaps en el `_analysis.md` y `resolve` integra las respuestas en el feature spec.

---

### 4. Validar un spec tras edición manual

Editas manualmente un `_spec.md` y quieres verificar que no introdujiste contaminación técnica ni rompiste la estructura SDD.

```
/wf-spec-validate features/auth/auth_spec.md
  → imprime informe APROBADO / REQUIERE_REVISIÓN (no genera archivo)
```

**Cuándo usarlo**: después de cualquier edición manual a un spec. También útil como gate antes de ejecutar `/wf-prepare-plan`.

---

### 5. Detectar conflictos entre specs de features

Quieres verificar que los specs de las diferentes features del proyecto son coherentes entre sí: sin HUs duplicadas, CAs contradictorios ni scope overlap.

```
/wf-spec-conflict features/auth/auth_spec.md --features-dir features/
  → genera features/auth/auth_conflict_report.md si hay conflictos
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

## Arquitectura de 3 capas

Todos los componentes de este directorio siguen el mismo patrón arquitectónico. Entender las 3 capas es clave para extender el sistema sin romper su coherencia.

```
┌─────────────────────────────────────────────────────────────┐
│  CAPA 1 — Workflows (wf-) invocables por el usuario         │
│  wf-spec-analyze │ wf-spec-validate │ wf-spec-discover     │
│  wf-spec-fast-track │ wf-spec-features-first │ wf-spec-conflict │
│  wf-spec-delta │ wf-spec-readiness                           │
│                                                             │
│  Rol: parsear args → verificar archivos → ejecutar workflow │
│  → delegar al agente → escribir resultado                   │
└────────────────────────────┬────────────────────────────────┘
                             │ invoca Agent()
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 2 — Agentes Worker                                    │
│  sdd-spec-explorer │ sdd-spec-planner │ sdd-spec-writer    │
│  sdd-spec-auditor                                         │
│                                                             │
│  Rol: explorar │ planificar │ escribir/evolucionar │ auditar│
│  memory: project  │  permissionMode: acceptEdits            │
└────────────────────────────┬────────────────────────────────┘
                             │ carga como contexto
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 3 — Knowledge Bases (kb-) — solo contexto             │
│                                                             │
│  kb-spec-expert │ kb-decompose-expert │ kb-conflict-expert  │
│  kb-gap-conventions                                         │
│                                                             │
│  Rol: reglas, templates, criterios de validación            │
│  Uso principal: contexto de agentes. Consulta directa solo  │
│  como apoyo conceptual, no como entrada operativa.          │
│  disable-model-invocation: true  │  context: fork           │
└─────────────────────────────────────────────────────────────┘
```

### Por qué esta separación

**Capa 1 (Workflows `wf-`)** son los puntos de entrada del usuario. Cada workflow contiene las instrucciones paso a paso de ejecución, parsea argumentos, verifica precondiciones, delega al agente especializado y escribe el resultado.

**Capa 2 (agentes Spec)** separa responsabilidades:
- `sdd-spec-explorer` diagnostica
- `sdd-spec-planner` decide approach
- `sdd-spec-writer` genera o evoluciona artefactos
- `sdd-spec-auditor` valida coherencia y readiness

Al estar especializados, su contexto es más estrecho, el contrato de cada uno es más claro y la arquitectura escala mejor.

**Capa 3 (Knowledge `kb-`)** son archivos de texto puro que se inyectan en el contexto del agente. Al declararlos en el frontmatter `skills: [...]` del agente, Claude Code los carga automáticamente cuando invoca el agente. Tienen `context: fork` para que no interfieran con el contexto principal.

---

## Mapa completo de componentes

### Skills workflow (Capa 1) — invocables por el usuario

| Skill | Comando | Produce |
|-------|---------|---------|
| `wf-spec-analyze` | `/wf-spec-analyze` | `_analysis.md` (mapa Spec, pureza del PRD, gaps de negocio) |
| `wf-spec-validate` | `/wf-spec-validate` | Informe inline (sin archivo) |
| `wf-spec-discover` | `/wf-spec-discover` | `_discovery.md` (mapa de features + scope RF→Feature) |
| `wf-spec-features-first` | `/wf-spec-features-first [--features F-XXX,...]` | `_discovery.md`, `_features.md` (Project Hub incremental con `PENDIENTE_GENERACIÓN` para features aún no procesadas), `features/<x>/<x>_spec.md` |
| `wf-spec-fast-track` | `/wf-spec-fast-track` | `features/<x>/<x>_spec.md` directamente |
| `wf-spec-conflict` | `/wf-spec-conflict` | `_conflict_report.md` |
| `wf-spec-delta` | `/wf-spec-delta` | `_delta_analysis.md` (analyze), spec actualizado (apply/resolve) |
| `wf-spec-readiness` | `/wf-spec-readiness` | `_readiness_report.md`, actualiza estado en `_features.md` |

### Agentes worker (Capa 2)

| Agente | Modos soportados | Invocado desde |
|--------|-----------------|----------------|
| `sdd-spec-explorer` | diagnóstico de PRD/spec, análisis de gaps, discovery | `wf-spec-analyze`, `wf-spec-discover`, exploración directa |
| `sdd-spec-planner` | planificación de approach | uso directo por el orquestador cuando la petición es ambigua |
| `sdd-spec-writer` | fast-track, delta apply/resolve, escritura de artefactos | `wf-spec-fast-track`, `wf-spec-delta`, `wf-spec-features-first` |
| `sdd-spec-auditor` | validate, conflict, readiness | `wf-spec-validate`, `wf-spec-conflict`, `wf-spec-readiness` |

### Knowledge bases (Capa 3)

| Skill | Tipo | Usado en modos |
|-------|------|----------------|
| `kb-spec-expert` | Conocimiento SDD (8 elementos, Prueba de Pureza, Testabilidad) | Todos |
| `kb-decompose-expert` | Partición de features, shared models, ownership | `discover`, `fast-track` |
| `kb-conflict-expert` | 5 reglas de detección de conflictos entre specs | `conflict` |
| `kb-gap-conventions` | SSoT de convenciones de gaps | Todos los modos que generen o verifiquen gaps |

---

## Routing recomendado del ecosistema Spec

El reparto actual de responsabilidades es este:

```text
Diagnóstico inicial o lectura del estado
  -> sdd-spec-explorer

Planificación del approach
  -> sdd-spec-planner

Escritura o evolución de artefactos
  -> sdd-spec-writer

Validación, conflictos y readiness
  -> sdd-spec-auditor
```

Los knowledge bases siguen siendo la SSoT conceptual. Lo que cambia es qué agente las consume en cada momento.

---

## Artefactos producidos

```
proyecto/
├── prd.md                                    ← Input
├── prd_analysis.md                           ← /wf-spec-analyze (recomendado)
├── prd_discovery.md                          ← /wf-spec-discover
├── prd_features.md                           ← /wf-spec-features-first — PROJECT HUB (index + trazabilidad + estado)
├── prd_conflict_report.md                    ← /wf-spec-features-first (automático) o /wf-spec-conflict
├── prd_readiness_report.md                   ← /wf-spec-readiness
└── features/
    └── <nombre-feature>/
        ├── README.md                         ← /wf-spec-fast-track
        ├── <nombre>_spec.md                  ← /wf-spec-fast-track
        ├── <nombre>_delta_analysis.md        ← /wf-spec-delta analyze
        ├── <nombre>_conflict_report.md       ← /wf-spec-conflict
        ├── <nombre>_plan.md                  ← /wf-prepare-plan (etapa siguiente)
        └── <nombre>_tasks.md                 ← /wf-prepare-tasks (etapa siguiente)
```

---

## Checkpoints humanos

El pipeline nunca es completamente automático. Estos son los momentos donde el humano debe intervenir:

| Momento | Qué hacer | Bloquea si no se hace |
|---------|-----------|-----------------------|
| Tras `analyze` | Responder gaps `[CRÍTICO]_(pendiente)_` en `_analysis.md` (en el propio archivo, no en el PRD) | No bloquea generación de specs, pero las HUs afectadas quedan `[INCOMPLETO]` y bloquean `prepare-plan` |
| Tras `analyze` | Responder gaps `[INFORMATIVO]_(pendiente)_` (opcional) | No — se aplican asunciones por defecto |
| Tras `analyze` con veredicto `REQUIERE_LIMPIEZA_PRD` | Aplicar las reescrituras de la sección Pureza al PRD y volver a ejecutar `/wf-spec-analyze` | Sí — único caso en que se toca el PRD antes de continuar |
| Tras `discover` (modo iterativo) | Elegir los Feature IDs que entran en la próxima iteración | Sí — `wf-spec-features-first --features` los necesita |
| Tras `features-first` | Revisar `_features.md` y validar la partición de features | No — pero afecta la calidad del plan |
| Tras `features-first` | Revisar `_conflict_report.md` si hay conflictos `ALTA` | No — pero pueden propagarse problemas al plan |
| Tras `delta analyze` | Responder gaps `[CRÍTICO]_(pendiente)_` en `_delta_analysis.md` | Sí — `delta apply` no avanza |

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
    ├── wf-spec-readiness/
    │   └── SKILL.md
    └── wf-spec-validate/
        └── SKILL.md
```

---

## Cómo extender el sistema

Para añadir un nuevo modo al pipeline:

1. **Crea el workflow** en `skills/wf-spec-<nombre>/SKILL.md` con el `agent:` especializado correcto (`sdd-spec-explorer`, `sdd-spec-writer` o `sdd-spec-auditor`). Aquí van las instrucciones paso a paso de qué debe hacer el agente.
2. **Crea el knowledge base** (si el modo necesita reglas propias transversales a varios workflows) en `skills/kb-<nombre>-expert/SKILL.md` con `context: fork` y `disable-model-invocation: true`.
3. **Registra el nuevo knowledge en el agente correcto**: añádelo al frontmatter `skills: [...]` y documenta su responsabilidad.
4. **Registra en CLAUDE.md y README.md**: añade la entrada en el rootmap o en el mapa del ecosistema si aplica.

**Regla de diseño**: los workflows (`wf-`) son el punto de entrada principal del usuario y contienen las instrucciones de ejecución. Los knowledge (`kb-`) viven como SSoT conceptual y se cargan como contexto del agente. La consulta directa de un `kb-*` puede servir como apoyo conceptual, pero no debe ser la forma principal de operar el pipeline.
