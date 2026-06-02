---
name: wf-design-export
description: "Exporta los tokens del DESIGN.md a formatos consumibles por equipos de desarrollo: CSS variables, Style Dictionary universal, Compose para Android, SwiftUI para iOS, Tailwind config. Cierra el puente entre diseno y codigo sin duplicar SSoT."
when_to_use: "Activa en frases como 'exporta los tokens', 'genera tokens para iOS', 'necesito el CSS de los colores', 'convierte el DESIGN.md a Style Dictionary'."
argument-hint: "<DESIGN.md> --platforms <css,style-dictionary,compose,swiftui,tailwind> [--output-dir <path>] [--dry-run]"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
---

# design-export — Exportacion de tokens

Tu rol es leer el `DESIGN.md` y producir archivos de tokens en uno o varios formatos. No reinterpretas decisiones del DESIGN.md; las traduces fielmente.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del DESIGN.md**: primer argumento posicional.
- **Plataformas**: `--platforms <lista>` con uno o varios de: `css`, `style-dictionary`, `compose`, `swiftui`, `tailwind`. Obligatorio.
- **Output dir** opcional via `--output-dir`. Por defecto `<dir_design>/tokens/`.
- **`--dry-run`** opcional: imprime el contenido sin escribir.

Si falta path o plataformas, informa:
> "Uso: `/wf-design-export <DESIGN.md> --platforms <css,style-dictionary,compose,swiftui,tailwind> [--output-dir <path>] [--dry-run]`"

## Paso 2: Verificar el DESIGN.md

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Si no tiene frontmatter YAML valido, deten:
   > "Este archivo no parece un `DESIGN.md` SDD. Genera uno con `/wf-design-system` o indica un path valido."

## Paso 3: Detectar plataformas sugeridas

Si el brief incluye `target_platforms`, sugiere automaticamente:
- `iOS` → recomendar `swiftui` o `style-dictionary`.
- `Android` → recomendar `compose` o `style-dictionary`.
- `Web` → recomendar `css` o `tailwind` o `style-dictionary`.
- Mobile multi-plataforma → recomendar `style-dictionary` como SSoT (genera todos los formatos derivables).

Si el usuario ya paso `--platforms`, respeta su seleccion; si no, sugiere las anteriores y pide confirmacion.

## Paso 4: Parsear el frontmatter del DESIGN.md

Extrae las secciones relevantes:
- `colors` (con sus modos `light`, `dark`, `high-contrast` si existe)
- `typography` (todos los roles)
- `spacing`
- `rounded`
- `elevation`
- `iconography.sizes` y `semantic_colors`
- `motion.durations` y `easing`
- `components` (opcional, no todos los formatos lo soportan)

Si alguna seccion critica falta, marca `EXPORT_GAP: <seccion>` y omite ese bloque en la salida.

## Paso 5: Generar por plataforma

Para cada plataforma solicitada, genera el archivo de tokens siguiendo el formato y estructura de `${CLAUDE_SKILL_DIR}/references/export_examples.md`.

Salidas por plataforma:
- `css`: `<output-dir>/tokens.css` — variables `:root` (light) + `[data-theme="dark"]` + `@media (prefers-contrast: more)` si existe high-contrast
- `style-dictionary`: `<output-dir>/tokens.json` — formato W3C Design Tokens
- `compose`: `<output-dir>/DesignTokens.kt` — `object DesignTokens` con companion objects por categoría
- `swiftui`: `<output-dir>/DesignTokens.swift` — `enum DesignTokens` con enums y extensions
- `tailwind`: `<output-dir>/tailwind.config.js` — objeto parcial `theme.extend` para integrar a config existente

Si una sección crítica del DESIGN.md falta, marca `EXPORT_GAP: <sección>` y omite ese bloque en la salida.

## Paso 6: Generar manifest

Junto a los archivos exportados, escribe `<output-dir>/manifest.md` con:
- fecha de generacion
- version del DESIGN.md de origen
- plataformas generadas
- gaps detectados (`EXPORT_GAP`)
- nota: este archivo se regenera, no editar manualmente.

## Paso 7: Modo dry-run

Si `--dry-run` esta activo:
- imprime el contenido en stdout en lugar de escribir.
- util para previsualizar antes de comprometerse.

## Paso 8: Informar al usuario

Reporta:
- paths generados
- plataformas exportadas
- gaps detectados si los hay
- siguiente paso recomendado:
  - integrar los archivos en el repo de codigo (CI deberia validar coherencia).
  - regenerar tras cada `wf-design-delta apply` o cuando version del DESIGN.md cambie.

## Regla operativa

- Esta workflow es **idempotente**: ejecutar dos veces produce el mismo output.
- No introduce decisiones nuevas; si una decision del DESIGN.md no es exportable a una plataforma (ej. `motion.easing` complejo), marca `EXPORT_GAP` y deja al equipo de codigo decidir.
- Coherencia con la version del DESIGN.md: si el DESIGN.md cambia de version (Regla 22), regenerar tokens es obligatorio antes de mergear el delta.
