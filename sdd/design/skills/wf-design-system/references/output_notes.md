# Notas de salida para `wf-design-system`

- El output final debe ser solo el contenido completo de `DESIGN.md`.
- El frontmatter declara la procedencia (`kb-design-system-contract` Regla 10):
  - direccion anclada → `origin: generated`, `direction_confidence: confirmed`.
  - direccion no anclada → `origin: generated-provisional`, `direction_confidence: provisional`, con `[INFERIDO]` en los campos de direccion inferidos sin evidencia y `## Changelog` marcando `[direccion: provisional]`. El `[INFERIDO]` es informativo: NO bloquea gates (la fase Design no tiene sellador mecanico).
- Si hay gaps, usar el bloque:

```md
## DESIGN_GAPs

- [DESIGN_GAP-001]: <descripcion>
- [DESIGN_GAP-002]: <descripcion>
```
