# Plantilla de prompt para el agente design-architect (design-system)

```text
Modo: design-system
Path del spec: <path_spec>
Path del DESIGN.md destino: <path_design>
Contenido del Spec:
---
<contenido_completo_spec>
---
PRD del producto:
---
<contenido_prd_o_N/A>
---
DESIGN_BRIEF del producto:
---
<contenido_brief_o_N/A>
---
Research de apps de referencia:
---
<resumen_research_o_N/A>
---
DESIGN.md actual:
---
<contenido_actual_o_N/A>
---
INSTRUCCION: produce un DESIGN.md de producto reutilizable por Stitch y futuras features. No introduzcas funcionalidades no presentes en el spec. Contrato visual persistente de producto, no de una sola feature.

Aplica las reglas de kb-design-expert, kb-design-brief y kb-design-style-taxonomy que tienes en contexto:
- Regla 2: DESIGN.md es de producto, no de feature
- Regla 6: formato @google/design.md (front matter YAML + markdown), orden de secciones canonicas y token types validos
- Regla 11: Visual Personality derivada del PRD (si disponible) o del spec; obligatoria en todo DESIGN.md y con perfil estructurado completo
- Regla 12: Reference Apps con el research (si disponible); obligatoria en todo DESIGN.md
- Regla 13: elegir `style_family` antes de tokens y componentes
- Regla 14: DESIGN.md materializa el brief, no lo reabre (jerarquia de fuentes vive en kb-design-brief Regla 10)
- Regla 15: si ya existe DESIGN.md, preserva tokens y componentes previos; toda mutacion debe marcarse y justificarse en `## Changelog`, o derivarse a `wf-design-delta` si afecta a valores existentes
- kb-design-brief: respetar `autonomy_policy`, `clarity_vs_brand`, `reference_apps_policy` y el resto de variables cerradas
- kb-design-style-taxonomy: usar solo familias validas; si ninguna encaja, aplicar Regla 12 (`custom`) con sus 5 condiciones
- Si faltan datos criticos para jerarquia, tono o patrones base, devuelve DESIGN_GAPs y no produzcas archivo final

Formato de output: ver ${CLAUDE_SKILL_DIR}/references/output_notes.md
```
