---
name: kb-decompose-expert
description: Experto en partición de Specs SDD monolíticos en Specs por feature. Contiene las reglas para identificar features válidas, declarar shared models y generar el índice de features. Úsalo cuando necesites saber cómo dividir un Spec grande en specs independientes, qué criterios definen una feature válida, o cómo gestionar modelos compartidos entre features. No activa para análisis de pureza (usa kb-spec-expert) ni para planificación técnica (usa kb-plan-expert).
argument-hint: "[concepto_a_consultar]"
effort: low
allowed-tools: [Read]
disable-model-invocation: true
context: fork
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

## Formato de `_features.md`

```markdown
# Features Index: [nombre del proyecto]
> Spec origen: [path/_spec.md] | Fecha: [YYYY-MM-DD]

## Features identificadas

### F-001: [nombre-kebab-case]
- **Descripción**: [una frase del objetivo de esta feature]
- **Actor principal**: [quién]
- **Journeys propios**: [Journey 1, Journey 2, ...]
- **CAs propios**: [CA-001 a CA-00X]
- **Modelos propios**: [Modelo1, Modelo2]
- **Modelos compartidos (owner)**: [ModeloX] ← esta feature lo define
- **Modelos compartidos (ref)**: [ModeloY (owner: F-00Z)]
- **Ruta spec**: features/[nombre]/[nombre]_spec.md

[Repetir por cada feature]

---

## Tabla de shared models

| Modelo | Feature Owner | Features que lo referencian |
|---|---|---|
| [NombreModelo] | F-00X: [nombre] | F-00Y, F-00Z |
```

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
