---
name: kb-sdd-audit-content
description: "Criterios normativos para detectar problemas de calidad de contenido en skills y agentes del ecosistema SDD: violaciones de SSoT (regla duplicada en dos sitios), violaciones de SRP (pieza demasiado ancha), contradicciones entre skills y inconsistencias de criterios entre fases. Define como detectar cada tipo de hallazgo y los niveles de severidad. No incluye chequeos estructurales (ver kb-sdd-audit-structural) ni las reglas de arquitectura en si mismas (ver kb-sdd-skill-architecture)."
argument-hint: "[pregunta sobre calidad de contenido de skills o agentes]"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KB SDD Audit Content

Criterios para determinar si el contenido de skills y agentes del ecosistema SDD cumple con SSoT, SRP y coherencia interna. Estas reglas se aplican leyendo y comparando el contenido real de los archivos, no solo su estructura de referencias.

## Criterio 1: Deteccion de violaciones de SSoT

Una violacion de SSoT ocurre cuando la misma regla normativa esta formulada en dos o mas archivos distintos.

Señales de violacion:

- Dos `kb-*` que contienen una seccion con el mismo encabezado y reglas equivalentes.
- Un `CLAUDE.md` que reproduce inline el contenido de una KB (no la referencia, la reescribe).
- Una `wf-*` que define criterios normativos que deberian vivir en una KB (p.ej. "la feature requiere handoff de Design si..." definido en el workflow en vez de en `kb-plan-expert`).
- Un agente que reformula en su cuerpo reglas que ya estan en sus KBs cargadas.

Como detectar: leer las secciones de reglas de cada skill y buscar parrafos semanticamente equivalentes en otros archivos. No basta con buscar palabras clave; hay que evaluar si la _decision_ esta duplicada aunque las palabras difieran.

Severidad: **alta** cuando la duplicidad afecta a una regla de decision critica (cuando hacer algo, que produce, que bloquea). **Media** cuando es meramente descriptiva o introductoria.

## Criterio 2: Deteccion de violaciones de SRP

Una violacion de SRP ocurre cuando una pieza mezcla mas de una responsabilidad principal.

Señales en una `kb-*`:

- Contiene secciones de reglas de dominios claramente distintos (p.ej. reglas de diseño visual mezcladas con reglas de trazabilidad funcional).
- Su descripcion en frontmatter necesita mas de una clausula principal para describir su dominio.
- Diferentes workflows la cargan por razones muy distintas entre si.

Señales en una `wf-*`:

- El body mezcla dos pipelines no equivalentes (p.ej. "si el modo es A haz X; si el modo es B haz Y" donde A y B son flows completamente distintos).
- El `argument-hint` tiene dos patrones de entrada incompatibles.

Señales en un agente:

- Sus modos cognitivos requieren leer artefactos completamente distintos y producen salidas de naturaleza opuesta (p.ej. escritura de nuevo artefacto + auditoria destructiva del mismo artefacto).
- La seccion `## Como operar` tiene subsecciones de proceso que no comparten ninguna entrada ni contexto.

Como detectar: leer el cuerpo de la pieza y preguntarse "si extrajera solo la mitad de esta pieza, seguiria siendo coherente por si sola?". Si la respuesta es si, hay SRP violation.

Severidad: **media** cuando la mezcla es incipiente (dos secciones que podrian separarse). **Alta** cuando genera ambiguedad real en el comportamiento del agente o del workflow.

## Criterio 3: Deteccion de contradicciones

Una contradiccion ocurre cuando dos skills afirman cosas incompatibles sobre el mismo concepto o decision.

Tipos de contradiccion:

- **Contradiccion directa**: KB-A dice "siempre hacer X" y KB-B dice "nunca hacer X" sin que una de ellas sea la SSoT delegada por la otra.
- **Contradiccion de frontera**: dos skills definen de forma distinta donde acaba la responsabilidad de una y empieza la otra (p.ej. `kb-design-expert` y `kb-spec-expert` con definiciones incompatibles de que pertenece al Spec funcional vs al contrato visual).
- **Contradiccion de criterio**: dos workflows usan reglas distintas para decidir la misma precondicion (p.ej. cuando un Plan requiere handoff de Design).

Como detectar: identificar pares de skills que comparten un dominio liminal y comparar sus definiciones de frontera. Buscar especialmente en secciones de "cuando aplica", "precondiciones" y "que no cubre".

Severidad: **bloqueante** cuando la contradiccion afecta a una decision de bloqueo o precondicion del pipeline. **Alta** en los demas casos.

## Criterio 4: Deteccion de inconsistencias

Una inconsistencia no es una contradiccion: es una divergencia de estilo, convencion o nivel de detalle que produce confusion sin llegar a ser incompatible.

Tipos de inconsistencia:

- **Inconsistencia de nombrado**: skills en la misma fase con convenciones de nombre distintas (mezcla de idiomas, patrones `<fase>-<dominio>` vs `<dominio>-<fase>`, etc.).
- **Inconsistencia de frontmatter**: `effort` que no corresponde al tamano real del workflow, `allowed-tools` con herramientas que el workflow no usa, falta de `context: fork` en workflows que generan artefactos.
- **Inconsistencia de formato de cuerpo**: algunas skills con pasos numerados y otras sin estructura, agentes con secciones fijas y agentes con estructura libre, mensajes de bloqueo sin el patron estandar.
- **Inconsistencia de nivel de detalle**: algunas KBs con reglas muy granulares y otras con reglas vagas sobre el mismo tipo de decision.

Como detectar: comparar skills del mismo tipo dentro de una fase. Las inconsistencias se ven al poner los archivos en paralelo, no al leerlos de forma aislada.

Severidad: **baja** cuando es solo estetica. **Media** cuando puede confundir a un agente que carga varias skills y recibe senales contradictorias sobre el nivel de prescripcion esperado.

## Formato de reporte de contenido

Por cada hallazgo:

```
[SEVERIDAD] <tipo: SSoT|SRP|CONTRADICCION|INCONSISTENCIA>
Archivos afectados: <path1> [y <path2> si aplica]
Seccion: <encabezado o linea aproximada>
Descripcion: <una o dos lineas explicando el problema concreto>
Accion sugerida: <consolidar en SSoT / extraer a nueva KB / alinear criterio / corregir frontmatter>
```

Al final del reporte:
- Total de hallazgos por tipo y severidad
- Lista de pares con contradicciones bloqueantes
- Estado global: `LIMPIO` / `CON HALLAZGOS`
