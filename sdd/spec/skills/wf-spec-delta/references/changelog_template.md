# Plantilla de Changelog y Asunciones para _spec.md

## Changelog

Añadir o actualizar al final del spec (orden cronológico inverso):

```markdown
## Changelog

### v[X.Y] — [YYYY-MM-DD]
- **Añadidas**: HU-XXX "[título]"
- **Modificadas**: HU-XXX "[título original]" — [descripción breve del cambio]
- **Eliminadas**: HU-XXX "[título]" (y sus CAs asociados)
- **CAs nuevos**: CA-XXX a CA-YYY
- **CAs modificados**: CA-XXX "[título]"
- **CAs eliminados**: CA-XXX "[título]"
- **Reglas**: [nueva/modificada/eliminada] "[descripción breve]"
```

## Asunciones Aplicadas (si las hay)

Añadir antes del Changelog cuando se aplicaron asunciones de gaps `[INFORMATIVO]`:

```markdown
## Asunciones Aplicadas (v[X.Y])

- **[D-XXX]**: [descripción de la asunción aplicada por defecto]
```
