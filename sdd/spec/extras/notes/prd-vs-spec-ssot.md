# PRD vs Spec: Fuente de Verdad en SDD

## La pregunta

¿Puede el PRD ser la fuente de verdad (SSoT) del proyecto? ¿Debería el equipo modificar el PRD cuando quiere cambiar algo?

## Respuesta corta

No. El PRD es el documento de entrada — se consume para generar el Spec. Una vez que el Spec existe, **el Spec es el SSoT**. El PRD pasa a ser un artefacto histórico.

---

## Por qué el PRD no puede ser el SSoT

Un PRD con RFs y Criterios de Aceptación no es equivalente a un Spec SDD. Las diferencias son estructurales:

| PRD | Spec SDD |
|---|---|
| RFs con CAs narrativos | HUs con CAs testables y sin ambigüedad |
| Referencias a endpoints (algunos pendientes) | Contratos de interfaz completos |
| Descripción general de comportamiento | Modelos de dominio, estados, transiciones |
| Sin gestión de gaps | Gaps detectados, resueltos y registrados |
| Sin versionado formal | Versión semántica con changelog |

El pipeline `wf-spec-analyze` + `wf-spec-finalize` no solo reformatea el PRD — lo enriquece con los 8 elementos SDD, resuelve ambigüedades y documenta las asunciones tomadas. Si alguien modifica el PRD después de este proceso, esa información extra se pierde.

## El problema de mantener el PRD como SSoT

Si el equipo modifica el PRD tras tener Specs generados, hay dos escenarios, ambos problemáticos:

1. **Regenerar todo el pipeline**: se pierden los gaps resueltos, las asunciones validadas y las decisiones de partición de features tomadas durante el proceso de Spec.

2. **No regenerar**: el PRD y los Specs divergen. Existen dos "verdades" contradictorias y no hay forma de saber cuál es la correcta ni qué impacto tiene el cambio en el plan y las tareas.

---

## El modelo correcto

```
PRD  ──────►  Spec  ──────►  Plan  ──────►  Tasks
 │              │
 │ se congela   │ SSoT — documento vivo
 │ tras Spec    │ evoluciona con wf-spec-delta
 ▼              ▼
snapshot       fuente de verdad
(histórico)    (versionada, con changelog)
```

**El PRD se congela** una vez que el Spec está generado. Queda como referencia histórica de los requisitos originales, útil para entender el origen, pero no para tomar decisiones.

---

## Cómo gestionar cambios una vez que existe el Spec

Cuando el equipo quiere añadir, modificar o eliminar algo:

```
"Quiero cambiar X"
        ↓
Describir el cambio en un archivo (p.ej. cambios.md)
        ↓
/wf-spec-delta analyze feature_spec.md --new-reqs cambios.md
        ↓
feature_delta_analysis.md
(muestra qué HUs se añaden, modifican o eliminan, y detecta gaps)
        ↓
[humano revisa, responde gaps críticos si los hay]
        ↓
/wf-spec-delta apply feature_spec.md feature_delta_analysis.md
        ↓
feature_spec.md v1.1  (actualizado, con changelog)
```

El delta es **quirúrgico**: solo toca lo que cambia. No regenera el spec completo ni invalida el trabajo previo.

---

## Sobre la integración con Jira

Si el equipo usa Jira como trazabilidad, el mapeo correcto es:

```
PRD RF-4.1  →  Spec HU-AUTH-003  →  JIRA-123
```

Los tickets de Jira deben apuntar a HUs del Spec, no a RFs del PRD. Así, cuando algo cambia en el Spec (via delta), se puede actualizar Jira con precisión quirúrgica, sabiendo exactamente qué HUs se vieron afectadas.

El mapeo PRD → Jira es solo trazabilidad de origen. No es suficiente para derivar un Plan técnico.

---

## Regla práctica

> Si alguien dice "modifiqué el RF-4 del PRD", la respuesta correcta es:
> "¿Qué HU del Spec corresponde a ese cambio? Aplica el delta sobre el Spec."
>
> Si el Spec aún no existe, la respuesta es:
> "Primero generamos el Spec y luego gestionamos cambios sobre él."
