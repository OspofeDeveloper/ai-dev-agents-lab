---
name: kb-decompose-expert
description: Experto en partición de Specs SDD monolíticos en Specs por feature. Contiene las reglas para identificar features válidas, declarar shared models y generar el índice de features. Úsalo cuando necesites saber cómo dividir un Spec grande en specs independientes, qué criterios definen una feature válida, o cómo gestionar modelos compartidos entre features. No activa para análisis de pureza (usa kb-spec-expert) ni para planificación técnica (usa kb-plan-expert).
argument-hint: "[concepto_a_consultar]"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Decompose Expert — Partición de Specs SDD

Eres el experto en descomposición de Specs monolíticos. Tu conocimiento define cómo identificar features válidas, cómo gestionar modelos compartidos entre ellas, y qué formato deben tener los artefactos resultantes de la partición.

---

## ¿Qué es una feature en términos SDD?

Una feature es una **unidad funcional cohesiva** que puede tener su propio Spec SDD válido con los 8 elementos completos, sin necesitar contexto de otras features para entenderse.

**Prueba de independencia**: ¿Puede esta feature ser desarrollada por un equipo diferente sin coordinar con otro equipo más allá de los contratos de domain compartidos? Si sí → es una feature independiente.

---

## Criterios para que una feature sea válida

Una feature válida debe cumplir **los tres criterios**:

1. **Journeys independientes**: tiene al menos un User Journey propio que no depende de un Journey de otra feature para tener sentido
2. **CAs propios**: tiene mínimo 3 Criterios de Aceptación que le pertenecen exclusivamente
3. **Actor claro**: el actor principal y su objetivo están bien definidos para esta feature

Si una feature candidata no cumple los tres criterios → **fusionarla** con la feature funcionalmente más cercana.

---

## Señales de que dos funcionalidades son una sola feature

- Comparten exactamente el mismo actor y objetivo
- Los Journeys de una no tienen sentido sin los de la otra
- Tienen menos de 3 CAs propios cada una
- Son pantallas de un mismo flujo (ej: "seleccionar fecha" y "confirmar reserva" forman parte del mismo Journey)

---

## Lo que NO es una feature

- Infraestructura transversal (autenticación de red, almacenamiento de sesión)
- Configuración de la app (tema, idioma, notificaciones on/off)
- Componentes UI reutilizables
- Módulos de utilidades (logging, analytics)

Estas son responsabilidades de módulos `:core:*` en el Plan — no generan specs de feature.

---

## Reglas para identificar features

**Por cohesión funcional, no por estructura del documento.**

El documento origen puede tener secciones como "Módulo de Servicios" que internamente describe 3 features distintas (listado, detalle, y seguimiento). La partición usa lógica funcional:

1. Identifica todos los **actores distintos** del Spec
2. Para cada actor, identifica sus **objetivos principales**
3. Agrupa por objetivo: un objetivo principal = una feature candidata
4. Aplica los criterios de validación del apartado anterior
5. Si una candidata no es válida → fusiona con la más cercana

---

## Shared Models — Definición y reglas

Un **shared model** es un modelo de domain que aparece como entidad relevante en más de una feature.

### Regla de ownership

Cada shared model tiene exactamente **una feature owner**: la feature que lo **crea o define** funcionalmente. No la que más lo usa.

**Criterios de desempate (aplicar en orden hasta resolver la ambigüedad):**

1. **Creación explícita**: la feature con CAs que describen la *creación* de la entidad (WHEN: el usuario crea / registra / da de alta)
2. **Gestión completa**: si ninguna "crea", la feature con CAs que describen operaciones CRUD completas sobre la entidad (no solo lectura)
3. **Mayor cobertura**: si empatan en gestión, la feature con más CAs que referencian directamente la entidad
4. **Proximidad semántica**: si aún empatan, la feature cuyo nombre es más semánticamente cercano al modelo (ej: el modelo `Appointment` pertenece a la feature `appointment-management`, no a `user-profile`)

Ejemplos:
- `User` → owner: feature de autenticación (crea y gestiona la sesión)
- `Zone` → owner: feature de disponibilidad (el usuario define sus zonas)
- `Service` → owner: feature de servicios (el coordinador crea los servicios)

### Lo que implica ser owner

La feature owner **define** el modelo completo en su Plan. Las features que lo referencian **no lo redefinen** — solo declaran que lo usan y apuntan al Plan de la feature owner.

---

## `_features.md` es un artefacto GENERADO

`_features.md` **no se edita a mano** y ningún workflow lo escribe componiendo texto. Lo regenera de forma determinista el script `sdd-features-index.py` (igual que `generate-skill-registry.py` regenera el registry). El motivo es de concurrencia: era un hub monolítico que varios fast-tracks escribían en paralelo y que dos devs en ramas distintas pisaban en cada merge aunque tocaran features distintas. Al ser generado, un conflicto de merge sobre `_features.md` es ruido — se regenera tras el merge — y la SSoT real vive repartida y co-localizada por feature.

**Reparto de SSoT (ninguna fuente redefine lo de otra):**

| Fuente | SSoT de |
|---|---|
| `_discovery.md` | universo de features (todas las F-XXX, incluidas las aún no generadas), shared models + ownership, mapeo RF→Feature |
| `features/<n>/spec/<n>_spec.md` | que la feature **está generada** + su estado real (marcadores `[INCOMPLETO]`/`[CRÍTICO]`/`[INFERIDO]`), `Feature ID`, HUs y CAs |
| `_readiness_report.md` (opcional) | veredicto refinado por feature (conflictos ALTA, dependencias) — su `## Matriz de readiness` |

**Derivación de Estado por feature** (la calcula el script, no se escribe a mano):

- sin spec → `PENDIENTE_GENERACIÓN`
- con spec y con veredicto en el readiness report → ese veredicto (autoridad)
- con spec, sin readiness → provisional: marcador presente → `BLOQUEADA`; avisos de gobernanza ≠ ninguno → `REQUIERE_CAMBIO_PRD`; limpio → `LISTA`

Estados canónicos (sin variantes): `LISTA`, `BLOQUEADA`, `PENDIENTE_GENERACIÓN`, `REQUIERE_CAMBIO_PRD`.

**Regenerar** (desde la raíz del proyecto, el directorio que contiene `.sdd/`):

```
python3 .sdd/scripts/sdd-features-index.py <raíz_spec>
```

Lo invocan `wf-spec-fast-track` y `wf-spec-from-code` (tras escribir un spec), `wf-spec-features-first` (pasada autoritativa final), `wf-spec-readiness` (tras escribir su report) y `wf-spec-delta` (tras aplicar). La salida es función pura de las entradas (sin timestamp de reloj) → idempotente.

**Estructura emitida** (no editar; documentada solo para lectores):

```markdown
# Features Index: [nombre del proyecto]
> GENERADO por `sdd-features-index.py` — NO editar a mano. Regenera con: `python3 .sdd/scripts/sdd-features-index.py <dir>`
> Fuentes: discovery=[sí|no], specs=[N], readiness=[sí|no]
> Spec origen: [PRD origen del discovery | omitido]

## Features identificadas

### F-001: [nombre-kebab-case]
- **Descripción**: [del discovery]
- **Actor principal**: [del discovery]
- **Journeys propios**: [del discovery]
- **CAs propios**: [CA-001 a CA-00X — del spec si existe; derivables del discovery si no]
- **Modelos propios**: [del discovery]
- **Modelos compartidos (owner)**: [del discovery]
- **Modelos compartidos (ref)**: [del discovery]
- **Ruta spec**: features/[nombre]/spec/[nombre]_spec.md  [o "(pendiente de generación)"]
- **Estado**: [LISTA | BLOQUEADA | PENDIENTE_GENERACIÓN | REQUIERE_CAMBIO_PRD]
- **Origen de alcance**: [del spec o del discovery]
- **Avisos de gobernanza**: [del spec o del discovery]

[Repetir por cada feature. Las PENDIENTE_GENERACIÓN llevan la nota de cómo procesarlas.]

---

## Resumen de estado

| Feature | Estado | Bloqueantes |
|---------|--------|-------------|
| F-001: [nombre] | LISTA | — |

---

## Tabla de shared models

| Modelo | Feature Owner | Features que lo referencian |
|---|---|---|
| [NombreModelo] | F-00X: [nombre] | F-00Y, F-00Z |

---

## Trazabilidad RF → HU → Feature

| RF | Feature | HU | Estado |
|---|---|---|---|
| RF-001 | F-001: [nombre] | HU-001, HU-002 | LISTA |
```

> No hay `## Historial de cambios` manual: el audit-trail de cada cambio vive en el `## Changelog` de cada spec y en git. Un índice generado no necesita narrar su propia historia.

---

## Formato de cada `_spec.md` por feature

Cada spec de feature es un **Spec SDD completo y autocontenido**. Contiene exactamente los 8 elementos obligatorios (ver `kb-spec-expert`), extraídos del spec monolítico y filtrados al scope de la feature:

0. **Actores** — solo los actores relevantes a esta feature
1. **Historias de Usuario** — solo las HUs que pertenecen a esta feature
2. **Recorridos de Usuario** — solo los Journeys de esta feature
3. **Resultados y Éxito** — definición de hecho para esta feature
4. **Instrucciones Inambiguas** — reglas de comportamiento y destinos de navegación de esta feature
5. **Criterios de Aceptación** — solo los CAs de esta feature, renumerados desde CA-001
6. **Checklist de Validación** — los 9 checkpoints estándar
7. **Fuera de Alcance** — exclusiones funcionales relevantes a esta feature

**Renumeración de CAs**: cada feature spec renumera sus CAs desde CA-001. No se heredan los números del spec monolítico. Esto garantiza que la trazabilidad es local a la feature.

**Header del spec de feature**:
```markdown
# Spec: [Nombre de la Feature]
> Versión: 1.0 | Fecha: [YYYY-MM-DD]
> Spec monolítico origen: [path/_spec.md]
> Feature ID: F-00X
```

---

## Qué NO debe hacer el agente al descomponer

- **No inventar** Journeys o CAs que no estaban en el spec monolítico
- **No fusionar** CAs de features distintas en un solo spec de feature
- **No omitir** información funcional relevante al filtrar — si hay duda, incluirla
- **No reescribir** — los HUs, Journeys y CAs se copian literalmente del spec origen, solo se filtran
- **No cambiar** la semántica de los CAs al renumerarlos
