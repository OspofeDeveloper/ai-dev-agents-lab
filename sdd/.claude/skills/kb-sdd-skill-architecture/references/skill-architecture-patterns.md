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

## Antipatrones a evitar

- `README.md` de fase definiendo política global de frontmatters
- `wf-*` repitiendo reglas completas de una `kb-*`
- `kb-*` con pasos operativos o scripts embebidos en `SKILL.md`
- un agente que hace exploración, escritura y auditoría sin necesidad real
- dos skills hermanas definiendo la misma regla con formulaciones distintas
