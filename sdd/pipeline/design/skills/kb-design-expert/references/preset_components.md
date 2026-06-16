# Preset starter components

Componentes base ya escritos para los presets. `wf-design-system` los incluye automaticamente cuando el preset corresponde, con sus estados completos (Regla 7 de `kb-design-system-contract`).

Todos los componentes asumen referencias a tokens del frontmatter del starter kit del mismo preset (ver `preset_starter_kits.md`).

---

## Componentes comunes a todos los presets

### `button-primary`

```yaml
button-primary:
  default:
    backgroundColor: "{colors.light.primary}"
    textColor: "{colors.light.on-primary}"
    rounded: "{rounded.md}"
    padding: "12px 20px"
    typography: "{typography.label}"
  hover:
    backgroundColor: "{colors.light.primary}"
    textColor: "{colors.light.on-primary}"
    opacity: "0.92"
  focus-visible:
    backgroundColor: "{colors.light.primary}"
    textColor: "{colors.light.on-primary}"
    outlineColor: "{colors.light.accent}"
    outlineWidth: "2px"
    outlineOffset: "2px"
  active:
    backgroundColor: "{colors.light.primary}"
    opacity: "0.88"
    transform: "scale(0.98)"
  disabled:
    backgroundColor: "{colors.light.border}"
    textColor: "{colors.light.on-surface-muted}"
    opacity: "0.6"
  loading:
    backgroundColor: "{colors.light.primary}"
    textColor: "{colors.light.on-primary}"
    cursor: "wait"
```

### `button-secondary`

```yaml
button-secondary:
  default:
    backgroundColor: "{colors.light.surface}"
    textColor: "{colors.light.on-surface}"
    borderColor: "{colors.light.border-strong}"
    borderWidth: "1px"
    rounded: "{rounded.md}"
    padding: "12px 20px"
    typography: "{typography.label}"
  hover:
    backgroundColor: "{colors.light.background}"
    borderColor: "{colors.light.on-surface-muted}"
  focus-visible:
    backgroundColor: "{colors.light.surface}"
    outlineColor: "{colors.light.accent}"
    outlineWidth: "2px"
    outlineOffset: "2px"
  active:
    backgroundColor: "{colors.light.background}"
    transform: "scale(0.98)"
  disabled:
    backgroundColor: "{colors.light.surface}"
    textColor: "{colors.light.on-surface-muted}"
    borderColor: "{colors.light.border}"
    opacity: "0.6"
  loading:
    backgroundColor: "{colors.light.surface}"
    cursor: "wait"
```

### `input-text`

```yaml
input-text:
  default:
    backgroundColor: "{colors.light.surface}"
    borderColor: "{colors.light.border}"
    textColor: "{colors.light.on-surface}"
    rounded: "{rounded.sm}"
    padding: "12px 14px"
    typography: "{typography.body}"
  focus:
    backgroundColor: "{colors.light.surface}"
    borderColor: "{colors.light.accent}"
    outlineColor: "{colors.light.accent}"
    outlineWidth: "2px"
  filled:
    backgroundColor: "{colors.light.surface}"
    borderColor: "{colors.light.border-strong}"
  invalid:
    backgroundColor: "{colors.light.surface}"
    borderColor: "{colors.light.error}"
    textColor: "{colors.light.on-surface}"
  disabled:
    backgroundColor: "{colors.light.background}"
    borderColor: "{colors.light.border}"
    textColor: "{colors.light.on-surface-muted}"
    opacity: "0.6"
  read-only:
    backgroundColor: "{colors.light.background}"
    borderColor: "{colors.light.border}"
    textColor: "{colors.light.on-surface}"
```

### `card-default`

```yaml
card-default:
  default:
    backgroundColor: "{colors.light.surface}"
    borderColor: "{colors.light.border}"
    borderWidth: "1px"
    rounded: "{rounded.md}"
    padding: "{spacing.lg}"
    elevation: "{elevation.level-1}"
  hover:
    backgroundColor: "{colors.light.surface}"
    elevation: "{elevation.level-2}"
  selected:
    backgroundColor: "{colors.light.surface}"
    borderColor: "{colors.light.accent}"
    borderWidth: "2px"
  loading:
    backgroundColor: "{colors.light.surface}"
    opacity: "0.7"
```

### `list-item`

```yaml
list-item:
  default:
    backgroundColor: "{colors.light.surface}"
    textColor: "{colors.light.on-surface}"
    padding: "16px 20px"
    typography: "{typography.body}"
  hover:
    backgroundColor: "{colors.light.background}"
  pressed:
    backgroundColor: "{colors.light.background}"
    opacity: "0.88"
  focus-visible:
    backgroundColor: "{colors.light.surface}"
    outlineColor: "{colors.light.accent}"
    outlineWidth: "2px"
    outlineOffset: "-2px"
  selected:
    backgroundColor: "{colors.light.background}"
    borderLeftColor: "{colors.light.accent}"
    borderLeftWidth: "3px"
  disabled:
    backgroundColor: "{colors.light.surface}"
    textColor: "{colors.light.on-surface-muted}"
    opacity: "0.6"
```

### `modal`

```yaml
modal:
  default:
    backgroundColor: "{colors.light.surface}"
    textColor: "{colors.light.on-surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.xl}"
    elevation: "{elevation.level-3}"
    maxWidth: "560px"
  entering:
    backgroundColor: "{colors.light.surface}"
    transform: "translateY(8px)"
    opacity: "0"
  exiting:
    backgroundColor: "{colors.light.surface}"
    transform: "translateY(0)"
    opacity: "0"
```

---

## Componentes especificos de `fintech-trust`

### `input-currency`

```yaml
input-currency:
  default:
    backgroundColor: "{colors.light.surface}"
    borderColor: "{colors.light.border}"
    textColor: "{colors.light.on-surface}"
    rounded: "{rounded.sm}"
    padding: "12px 14px"
    typography: "{typography.body}"
    prefixColor: "{colors.light.on-surface-muted}"
  focus:
    backgroundColor: "{colors.light.surface}"
    borderColor: "{colors.light.accent}"
    outlineColor: "{colors.light.accent}"
    outlineWidth: "2px"
  filled:
    backgroundColor: "{colors.light.surface}"
    borderColor: "{colors.light.border-strong}"
  invalid:
    backgroundColor: "{colors.light.surface}"
    borderColor: "{colors.light.error}"
  disabled:
    backgroundColor: "{colors.light.background}"
    opacity: "0.6"
  read-only:
    backgroundColor: "{colors.light.background}"
    textColor: "{colors.light.on-surface}"
```

### `card-balance`

```yaml
card-balance:
  default:
    backgroundColor: "{colors.light.primary}"
    textColor: "{colors.light.on-primary}"
    rounded: "{rounded.lg}"
    padding: "{spacing.xl}"
    elevation: "{elevation.level-2}"
  loading:
    backgroundColor: "{colors.light.primary}"
    opacity: "0.7"
```

### `transaction-list-item`

```yaml
transaction-list-item:
  default:
    backgroundColor: "{colors.light.surface}"
    textColor: "{colors.light.on-surface}"
    padding: "14px 20px"
    typography: "{typography.body}"
    amountColor: "{colors.light.on-surface}"
    amountTypography: "{typography.body}"
  hover:
    backgroundColor: "{colors.light.background}"
  pressed:
    backgroundColor: "{colors.light.background}"
  focus-visible:
    outlineColor: "{colors.light.accent}"
    outlineWidth: "2px"
    outlineOffset: "-2px"
```

### `status-badge`

```yaml
status-badge:
  default:
    backgroundColor: "{colors.light.surface}"
    textColor: "{colors.light.on-surface-muted}"
    borderColor: "{colors.light.border}"
    borderWidth: "1px"
    rounded: "{rounded.pill}"
    padding: "4px 10px"
    typography: "{typography.caption}"
  success:
    backgroundColor: "{colors.light.success}"
    textColor: "{colors.light.on-success}"
    borderWidth: "0"
  warning:
    backgroundColor: "{colors.light.warning}"
    textColor: "{colors.light.on-warning}"
    borderWidth: "0"
  error:
    backgroundColor: "{colors.light.error}"
    textColor: "{colors.light.on-error}"
    borderWidth: "0"
  pending:
    backgroundColor: "{colors.light.surface}"
    textColor: "{colors.light.on-surface-muted}"
    borderColor: "{colors.light.border-strong}"
    borderWidth: "1px"
```

---

## Componentes especificos de `consumer-lifestyle`

### `card-feature`

Card mas prominente con imagery, propia de consumer.

```yaml
card-feature:
  default:
    backgroundColor: "{colors.light.surface}"
    rounded: "{rounded.lg}"
    padding: "0"
    elevation: "{elevation.level-1}"
    overflow: "hidden"
  hover:
    elevation: "{elevation.level-2}"
    transform: "translateY(-2px)"
  pressed:
    transform: "translateY(0)"
    opacity: "0.92"
```

### `list-item-rich`

Item con avatar + primary text + secondary text + trailing action.

```yaml
list-item-rich:
  default:
    backgroundColor: "{colors.light.surface}"
    textColor: "{colors.light.on-surface}"
    padding: "16px 20px"
    typography: "{typography.body}"
    secondaryColor: "{colors.light.on-surface-muted}"
    secondaryTypography: "{typography.body-sm}"
  hover:
    backgroundColor: "{colors.light.background}"
  pressed:
    backgroundColor: "{colors.light.background}"
    opacity: "0.92"
  selected:
    backgroundColor: "{colors.light.background}"
    borderLeftColor: "{colors.light.accent}"
    borderLeftWidth: "3px"
```

### `bottom-sheet`

```yaml
bottom-sheet:
  default:
    backgroundColor: "{colors.light.surface}"
    textColor: "{colors.light.on-surface}"
    rounded: "20px 20px 0 0"
    padding: "{spacing.lg}"
    elevation: "{elevation.level-3}"
  entering:
    transform: "translateY(100%)"
  exiting:
    transform: "translateY(100%)"
```

---

## Componentes especificos de `content-editorial`

### `card-article`

```yaml
card-article:
  default:
    backgroundColor: "{colors.light.surface}"
    textColor: "{colors.light.on-surface}"
    padding: "{spacing.xl}"
    typography: "{typography.body}"
    rounded: "0"
    borderBottomColor: "{colors.light.border}"
    borderBottomWidth: "1px"
  hover:
    backgroundColor: "{colors.light.background}"
```

### `hero-banner`

```yaml
hero-banner:
  default:
    backgroundColor: "{colors.light.background}"
    textColor: "{colors.light.on-background}"
    padding: "{spacing.2xl} {spacing.xl}"
    typography: "{typography.display}"
```

### `button-text`

```yaml
button-text:
  default:
    backgroundColor: "transparent"
    textColor: "{colors.light.on-surface}"
    padding: "8px 0"
    typography: "{typography.label}"
    textDecoration: "underline"
    textUnderlineOffset: "3px"
  hover:
    textColor: "{colors.light.accent}"
  active:
    opacity: "0.8"
  focus-visible:
    outlineColor: "{colors.light.accent}"
    outlineWidth: "2px"
    outlineOffset: "4px"
  disabled:
    textColor: "{colors.light.on-surface-muted}"
    opacity: "0.6"
```

---

## Reglas operativas

1. Cuando `wf-design-system` corre con un preset declarado, **incluye automaticamente** los componentes comunes + los especificos del preset en el `DESIGN.md` resultante.
2. El agente puede ampliar componentes (anadir mas o anadir estados) segun necesidades del producto. No puede eliminar estados de los componentes base.
3. Si un producto no necesita un componente especifico del preset (ej. `bottom-sheet` no aplica a un consumer-lifestyle minimalista), declarar `# N/A: <razon>` en lugar de eliminarlo silenciosamente.
4. Para anadir un componente nuevo al preset, editar este archivo + documentar en `sdd/pipeline/design/README.md > Como extender el sistema`.
