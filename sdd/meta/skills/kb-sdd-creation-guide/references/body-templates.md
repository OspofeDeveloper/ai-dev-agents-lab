# Plantillas de estructura de cuerpo

Plantillas para el cuerpo de cada tipo de pieza. Copiar y adaptar. Los criterios de qué formato elegir viven en el `SKILL.md` de `kb-sdd-creation-guide`.

---

## Estructura: `kb-*`

Dos formatos válidos; la elección depende del tipo de contenido:

**Formato A — Reglas numeradas** (`## Regla N: <enunciado>`): para reglas discretas y cross-referenciables. Permite que workflows y agentes citen "Regla N de kb-X". Preferido para la mayoría de `kb-*` técnicas y de stack.

**Formato B — Secciones descriptivas** (`## <Título descriptivo>`): para procesos, criterios de decisión complejos o estructura narrativa. Apropiado para skills meta y skills con pocas reglas largas.

No mezclar ambos formatos dentro de una misma skill.

Para `kb-*` de nivel `tasks/`, estructura mínima recomendada:
1. Referencia a la `kb-*` de nivel `plan/` equivalente (si existe)
2. Templates o código concreto por sección
3. Checklist de implementación (opcional pero recomendado)

---

## Estructura: `wf-*`

Pasos numerados con encabezados `## Paso N: <accion>`. Cada paso incluye:

1. Qué hace (una línea)
2. Qué verifica o valida
3. Qué produce o escribe
4. Cómo maneja bloqueos (con mensajes estándar)

Patrón de mensajes de bloqueo:
```
> "❌ <condicion bloqueante>. <Accion correctiva con comando concreto>."
> "⚠ <advertencia no bloqueante>. <Descripcion del impacto>."
```

Último paso siempre: informar al usuario del output generado y el siguiente paso sugerido.

Tabla de qué va inline y qué se delega:

| Tipo de paso | Ejecutar |
|---|---|
| Parseo de argumentos y flags | Inline |
| Verificación de precondiciones (archivo existe, nombre válido) | Inline |
| Colección mecánica de rutas o conteos | Inline |
| Generación de contenido (skill body, frontmatter, artefactos) | Delegar al agente |
| Diagnóstico de violaciones o decisiones arquitectónicas | Delegar al agente |
| Escritura del artefacto generado por el agente | Inline |
| Reporte final al usuario | Inline |

Una `wf-*` que genera contenido sin delegar a un agente es una señal de alarma: está haciendo razonamiento que no le corresponde.

---

## Estructura: agente

Secciones H2 fijas:

```markdown
## Skills disponibles
<lista de kb con una línea: qué aporta cada una a este agente>

## Cómo operar
### Entrada que recibes
<lista de inputs esperados por el workflow o el orquestador>

### Proceso por modo
<subsección por cada modo cognitivo que soporta el agente>

## Verificación de contexto
<para cada KB declarada en skills: [...]: nombre y concepto clave que confirma su presencia>
Incluye `## KB Load Status` al final de cada respuesta (ver Regla 19 de kb-sdd-skill-architecture).

## Regla de oro
<máxima de una o dos líneas que define el límite del agente>

## Nota de evolución (opcional)
<cuándo conviene partir el agente; mantener como ancla para decisión futura>
```

Secciones prohibidas en el cuerpo de un agente:
- listas de pasos shell o comandos a ejecutar (eso es una `wf-*`)
- política global de frontmatters o arquitectura del ecosistema (eso es `kb-sdd-skill-architecture`)

---

## Estructura: `CLAUDE.md` de fase

Secciones H2 fijas:

```markdown
## Tu rol: <título del orquestador>
<Una o dos frases: qué hace y qué NO hace.>
<Ej: "No ejecutas el trabajo directamente. No construyes prompts manualmente.">

## Rootmap de workflow skills
| Intención del usuario | Skill | Argumentos |
|---|---|---|
| <frase de intención natural> | `/wf-<nombre>` | `<args>` |

## Cómo actuar ante una petición
<Reglas de matching semántico, patrones especiales y bloqueos. Solo lo que no cubre el rootmap.>

## Agentes disponibles  ← solo si los agentes son accesibles directamente desde el orquestador
| Agente | Dominio |
|---|---|
| `<nombre>` | <una línea de dominio> |
```

Secciones prohibidas en `CLAUDE.md`:
- plantillas de frontmatter o convenciones de nombrado (eso es `kb-sdd-creation-guide`)
- reglas de arquitectura transversal (eso es `kb-sdd-skill-architecture`)
- listas de pasos operativos (eso es una `wf-*`)
- descripción interna del razonamiento de skills o agentes
