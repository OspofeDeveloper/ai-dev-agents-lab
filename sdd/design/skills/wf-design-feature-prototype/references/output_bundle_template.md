# Bundle de salida esperado

El agente debe devolver tres bloques claramente delimitados:

```md
===FILE: <feature>_flows.md===
<contenido completo>

===FILE: <feature>_views.md===
<contenido completo>

===FILE: <feature>_ui_prompt.md===
<contenido completo>
```

Si hay gaps, debe devolver solo:

```md
## DESIGN_GAPs

- [DESIGN_GAP-001]: <descripcion>
```
