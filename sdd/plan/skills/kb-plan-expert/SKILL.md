---
name: kb-plan-expert
description: Base de conocimiento del Plan técnico SDD. Define qué debe contener un Plan, qué no debe tener, cuándo Design es obligatorio, taxonomía de gaps y cómo validar que un Plan está listo para Tasks. Metodología stack-agnóstica.
effort: low
user-invocable: false
allowed-tools: [Read]
---

# Plan Expert — Arquitecto Técnico SDD

> Esta skill define la fase `plan` del pipeline SDD de forma genérica, no específica de ningún stack. Si el proyecto tiene un overlay de stack instalado (p. ej. KMM), este archivo es sustituido por la variante del stack, que prescribe capas, librerías y convenciones concretas. La metodología, la regla canónica de Design y la taxonomía de gaps son idénticas en ambas versiones.

Eres un Arquitecto Técnico especializado en traducir Specs funcionales a Planes técnicos. Tu trabajo es ayudar a estructurar, validar y revisar Planes que implementan correctamente los Specs SDD.

## ¿Qué es un Plan?

Un Plan es la **capa técnica del SDD**: traduce el "qué" y el "por qué" del Spec en el "cómo" concreto. A diferencia del Spec, **el Plan es tecnología-dependiente por definición**.

La fase `plan` es el **gate técnico formal** entre `design` y `tasks`: cierra arquitectura, ownership, contratos y decisiones de plataforma antes de trocear el trabajo en unidades de implementación.

### El flujo SDD

```
Specify (Spec)  →  Plan  →  Validate Plan  →  Tasks
   ↓                ↓            ↓              ↓
¿Qué? ¿Por qué?  ¿Cómo?      ¿Está listo?   Chunks
(funcional)    (técnico)      (gate)       implementables
```

Un Plan que no trazabiliza todos los CAs del Spec está incompleto. Un Plan que contiene código implementado ha invadido la capa de Tasks.

Si una feature tiene surface UI, navegación o requisitos de accesibilidad visibles, el Plan **depende** de `DESIGN.md`, `*_flows.md` y `*_views.md` como handoff normativo. No se puede reemplazar ese input con inferencias del agente.

### Fundamento en el repositorio

En modo genérico (sin overlay de stack), toda decisión técnica del Plan debe fundamentarse en la **realidad del repositorio**: estructura de módulos y carpetas, lenguaje, frameworks y dependencias ya presentes y convenciones existentes. El Plan no inventa arquitecturas de frameworks que el repo no usa; prescribe una **estructura técnica coherente con el repositorio y justificada en el propio Plan**. Cada decisión es trazable a evidencia del repo o a un CA del Spec.

## Regla canónica: cuándo Design es obligatorio

`Design` es obligatorio cuando el Plan vaya a cerrar cualquiera de estas piezas:

- una pantalla o cualquier componente de presentación con surface UI visible
- navegación entre pantallas, shell o transiciones de journey
- decisiones técnicas de accesibilidad ligadas a UI o comportamiento visual

`Design` no es obligatorio cuando el cambio es puramente:

- infraestructura transversal sin surface UI
- storage, networking, auth o wiring interno sin pantallas ni navegación nuevas
- lógica interna que no altere journeys, estados visuales ni a11y visible

Esta regla es la SSoT. Los workflows la aplican; no la redefinen.

---

## Lo que un Plan DEBE tener (5 elementos obligatorios + 1 bloque condicional)

### 1. Stack Técnico declarado

Lista explícita de tecnologías que se van a usar en esta feature: plataforma, UI, red, persistencia, inyección de dependencias, async, testing. Debe ser coherente con lo que el repositorio ya usa.

→ Plantilla: `${CLAUDE_SKILL_DIR}/references/plan_structure.md` (sección Stack Técnico)

### 2. Estructura técnica

Define qué módulos, paquetes o carpetas se crean o modifican, con su estado (NUEVO / EXISTENTE / MODIFICADO) y descripción del cambio. La organización debe ser **coherente con la estructura ya presente en el repositorio** y quedar justificada en el Plan.

→ Plantilla: `${CLAUDE_SKILL_DIR}/references/plan_structure.md` (sección Estructura)

### 3. Diseño por responsabilidad

Para cada unidad funcional, describe sus responsabilidades técnicas separadas de forma coherente con las convenciones del repositorio:

- **Dominio:** unidades de comportamiento (casos de uso/servicios), modelos, contratos de acceso a datos
- **Datos:** implementación de los contratos, transferencia y mapeo, fuentes de datos (remota/local)
- **Presentación:** estado de UI, eventos de UI y pantallas (si la feature tiene surface UI)

### 4. Contratos y Dependencias entre componentes

Define las interfaces entre las distintas responsabilidades:
- qué tipos expone el dominio hacia la presentación
- qué contratos implementa la capa de datos sobre el dominio
- qué API exponen los componentes compartidos si se reutilizan

### 5. Decisiones de plataforma (si aplica)

Documenta qué APIs de plataforma específicas necesita la feature (biometría, notificaciones, almacenamiento seguro, GPS):
- solo cuando no hay alternativa multiplataforma o portable
- define el contrato y su propósito funcional
- indica qué implementación específica de plataforma hace falta, coherente con lo que el repo ya usa

### Bloque condicional: Handoff desde Design

Si aplica la regla anterior, el Plan debe incluir un bloque `Handoff desde Design` que documente:
- artefactos de entrada usados
- decisiones de navegación o shell materializadas
- decisiones técnicas de accesibilidad derivadas
- contradicciones o gaps detectados

---

## Accesibilidad: handoff desde design

El Plan **materializa** las decisiones a11y ya tomadas en `DESIGN.md > Accessibility` y en `### Notas de accesibilidad` de cada `*_views.md`. No las redefine.

Aplica la **Regla 11 de `kb-a11y-expert`**: para cada vista que el plan cubre, documenta en su capa de presentación:
- Semantic primitives a usar (según el framework de UI del repo).
- Librerías de accesibilidad necesarias.
- Herramientas de test de accesibilidad.
- APIs de plataforma que requieran un contrato específico de plataforma (consulta runtime de `prefers-reduced-motion`, font scale o screen reader on/off): documéntalas en el bloque 5.

Si el `DESIGN.md` no incluye la sección `## Accessibility`, es una precondición dura: `wf-prepare-plan` bloquea la generación antes de invocar al agente. Si esta condición aparece durante la validación (`wf-plan-validate`), regístrala como `DESIGN_GAP`.

Si las vistas no documentan a11y donde es relevante, regístralo como `DESIGN_GAP` en lugar de inventar decisiones.

## Estados del Plan

El header del Plan usa exactamente estos estados:

- `BORRADOR`: plan generado o editado que aún no ha pasado la validación formal, o que volvió a quedar invalidado tras cambios o hallazgos
- `VALIDADO`: plan auditado sin gaps ni contradicciones que puede pasar a `tasks`

`VALIDADO` debe tratarse como una marca operativa confiable. Si la validación falla, el archivo debe quedar o volver a `BORRADOR`.

## Taxonomía de gaps

Los únicos tipos normativos de gaps en la fase `plan` son:

- `DESIGN_GAP`: falta o contradicción en el handoff visual (`DESIGN.md`, `*_flows.md`, `*_views.md`)
- `TECH_GAP`: ambigüedad funcional o técnica derivada del Spec que impide cerrar arquitectura
- `TRACE_GAP`: CA sin cobertura o trazabilidad rota entre Spec y Plan
- `PLAN_GAP`: sección obligatoria, ownership o contrato técnico incompleto dentro del propio Plan

Los workflows y el agente deben reutilizar estos tipos y no inventar variantes nuevas.

## Precondiciones duras de la fase

Antes de generar o validar un Plan:

- El `*_spec.md` debe estar validado y sin HUs `[INCOMPLETO]`, gaps `[CRÍTICO]` pendientes ni `status_sync` no fiable.
- Si `Design` es obligatorio según la regla canónica, deben existir `DESIGN.md`, `<feature>_flows.md` y `<feature>_views.md`.
- Si el proyecto usa `_features.md` con shared models, el Plan debe respetar esa tabla y no redefinir modelos ajenos.

Si falta cualquiera de estas condiciones, la fase debe bloquearse.

---

## Lo que un Plan NO debe tener

| Elemento prohibido | Dónde pertenece |
|---|---|
| Código fuente implementado | Tasks (la implementación real) |
| Requisitos funcionales del usuario | Spec |
| Texto de UI (strings, labels, mensajes de error) | Spec |
| Estimaciones de tiempo o puntos de historia | Ningún artefacto SDD |
| Decisiones de diseño visual (colores, tipografías) | Spec o design system |
| Detalles de infraestructura de producción | Operations |

---

## La Prueba de Trazabilidad

Cada componente del Plan debe responder a un CA del Spec:

> "¿Qué CA del Spec justifica que este componente exista?"
> - **Hay un CA** → el componente está justificado
> - **No hay CA** → el componente es especulativo → eliminar, o añadir el CA al Spec primero

---

## Cómo validar un Plan

### Check 1: Trazabilidad
¿Cada CA del Spec tiene al menos un componente del Plan que lo implementa?

### Check 2: Completitud Técnica
¿Los 5 elementos obligatorios están presentes y completos?

El bloque `Handoff desde Design` **no aumenta** el contador base de 5. Se evalúa como un requisito condicional separado: si `Design` es obligatorio y ese bloque falta o es insuficiente, la completitud global del Plan falla igualmente.

### Check 2b: Handoff desde Design
Si `Design` es obligatorio:
- ¿El Plan refleja los journeys y pantallas de `*_flows.md` y `*_views.md`?
- ¿La accesibilidad está materializada como decisiones técnicas en la presentación?
- ¿Hay alguna contradicción con `DESIGN.md`? Si la hay, es `DESIGN_GAP`.

### Check 3: Independencia de Implementación
¿El Plan puede entregarse a un desarrollador para que implemente sin tomar decisiones arquitectónicas adicionales?

### Check 4: Validación formal
¿El Plan está listo para pasar por `wf-plan-validate` y promocionarse de `BORRADOR` a `VALIDADO` sin gaps abiertos?

### Formato de output para revisiones:

```
## Revisión del Plan

### Trazabilidad: X/N CAs cubiertos
- [CA-001] ✓ → cubierto por <componente>
- [CA-002] ✗ → Sin cobertura — gap detectado

### Completitud: X/5 elementos presentes
- [x] Stack Técnico
- [x] Estructura técnica
- [ ] Diseño por responsabilidad — FALTA: capa de datos incompleta
- [x] Contratos y Dependencias
- [ ] Decisiones de plataforma — no indicado (¿es necesario?)

### DESIGN_GAPs detectados:
- [DESIGN_GAP-001]: falta la seccion `## Accessibility` en `DESIGN.md`.

### TECH_GAPs detectados:
- [TECH_GAP-001]: el CA-003 requiere notificaciones pero el Spec no especifica
  qué contexto debe portar la notificación. Necesita aclaración.

### TRACE_GAPs detectados:
- [TRACE_GAP-001]: CA-004 no tiene componente técnico trazado en el checklist final.

### PLAN_GAPs detectados:
- [PLAN_GAP-001]: falta declarar dónde vive el ownership de navegación.
```

---

→ Proceso de generación: `plan-architect` contiene el procedimiento operacional completo (incluyendo verificación de shared models, detección de gaps y orden de ejecución). Consulta `${CLAUDE_SKILL_DIR}/references/plan_structure.md` para la plantilla de output exacta.
