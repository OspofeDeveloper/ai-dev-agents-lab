# Plantilla de estructura — DESIGN Delta Analysis

```markdown
# DESIGN Delta Analysis

## Resumen
<una linea>

## Extensiones propuestas (anadir sin tocar lo existente)

### Tokens nuevos
- <token>: <valor> — <justificacion> — [origen: <feature/brief/spec>]

### Componentes nuevos
- <componente>: <descripcion breve> — <justificacion>

### Secciones nuevas
- <seccion>: <razon>

## Mutaciones propuestas (cambian valores existentes)

> Cada mutacion debe estar justificada y tener impacto evaluado.

### M-001: <descripcion corta>
- Antes: <valor actual>
- Despues: <valor propuesto>
- Justificacion: <por que>
- Impacto: <componentes / features afectados>
- Severidad: [BAJA | MEDIA | ALTA | CRITICA]
- Estado: [confirmado | _(pendiente)_]

## Items a eliminar (raros, requieren justificacion fuerte)

- <item>: <razon> — Severidad: [ALTA | CRITICA]_(pendiente)_

## Conflictos detectados con brief
- <descripcion o `ninguno`>

## Cambios bloqueantes (requieren actualizar el brief primero)
- [BRIEF_CHANGE_REQUIRED] <descripcion>

## Plan de aplicacion
1. <paso>
2. <paso>
```
