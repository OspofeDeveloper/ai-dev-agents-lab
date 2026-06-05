# Skill Architecture Patterns

## Frontmatter base recomendada

### `kb-*`

```yaml
---
name: kb-<nombre>
description: "Conocimiento reusable y normativo para <dominio>."
argument-hint: "[pregunta o contexto]"
effort: low
allowed-tools: [Read]
user-invocable: false
---
```

### `wf-*`

```yaml
---
name: wf-<nombre>
description: "Workflow para <pipeline cerrada>."
argument-hint: "<input principal> [flags]"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
agent: <agente-si-aplica>
---
```

## Prueba rápida para decidir entre piezas

### Crear `kb-*`

Sí, si la respuesta es "sí" a dos o más:

- ¿La misma regla la usarán varias workflows?
- ¿La misma regla la usarán varios agentes?
- ¿El contenido seguiría siendo válido aunque cambie el flujo operativo?
- ¿El contenido es normativo y conceptual?

### Crear `wf-*`

Sí, si la respuesta es "sí" a dos o más:

- ¿Hay parseo de argumentos o flags?
- ¿Hay precondiciones o bloqueos claros?
- ¿La secuencia de trabajo es repetible?
- ¿Produce archivos o mutaciones concretas?

### Crear agente

Sí, si la respuesta es "sí" a dos o más:

- ¿Hace falta juicio experto continuo?
- ¿Hay que sintetizar varias fuentes o artefactos?
- ¿No basta con un procedimiento fijo?
- ¿La responsabilidad encaja mejor como modo cognitivo especializado?

## Tech Target Directory Structure

### Estructura canónica

```
sdd/
  prd/    spec/    design/    plan/    tasks/    ← fases, tech-agnostic
  tech/
    <stack>/
      agents/                  ← agentes propietarios del stack
      skills/
        plan/                  ← kb-* cargadas por plan-architect cuando tech=<stack>
        tasks/                 ← kb-* cargadas por task-generator cuando tech=<stack>
        wf-<stack>-*/          ← workflows cross-fase específicos del stack
```

### Ejemplo real con `kmm`

```
sdd/tech/kmm/
  agents/
  skills/
    plan/     ← kb-kmm-clean-architecture, kb-kmm-feature-clean-architecture, ...
    tasks/    ← kb-kmm-http-ktor, kb-kmm-environments, kb-kmm-navigation-compose, ...
    wf-kmm-auth-setup-keycloak/
    wf-kmm-datastore-setup/
    ...
```

## Antipatrones a evitar

- `README.md` de fase definiendo política global de frontmatters
- `wf-*` repitiendo reglas completas de una `kb-*`
- `kb-*` con pasos operativos o scripts embebidos en `SKILL.md`
- un agente que hace exploración, escritura y auditoría sin necesidad real
- dos skills hermanas definiendo la misma regla con formulaciones distintas
