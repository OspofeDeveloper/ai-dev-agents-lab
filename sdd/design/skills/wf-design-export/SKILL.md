---
name: wf-design-export
description: Workflow SDD que exporta los tokens del DESIGN.md a formatos consumibles por equipos de desarrollo (CSS variables, Style Dictionary universal, Compose para Android, SwiftUI para iOS, Tailwind config). Cierra el puente entre diseno y codigo sin duplicar SSoT. Activa en frases como "exporta los tokens", "genera tokens para iOS", "necesito el CSS de los colores", "convierte el DESIGN.md a Style Dictionary".
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

### `css`

Output: `<output-dir>/tokens.css`

Estructura:
- `:root` con tokens del modo light.
- `[data-theme="dark"]` con tokens del modo dark.
- `@media (prefers-contrast: more)` con tokens high-contrast si existe.
- Tokens de typography como variables: `--font-h1-size`, `--font-h1-weight`, etc.
- Spacing, rounded, elevation como variables.

Ejemplo:
```css
:root {
  --color-background: #F7F7F5;
  --color-surface: #FFFFFF;
  --color-primary: #0E0E10;
  --spacing-md: 16px;
  --rounded-md: 16px;
}

[data-theme="dark"] {
  --color-background: #0E0E10;
  --color-surface: #1A1A1D;
  --color-primary: #FFFFFF;
}
```

### `style-dictionary`

Output: `<output-dir>/tokens.json` siguiendo el formato W3C Design Tokens.

Estructura:
```json
{
  "color": {
    "light": {
      "background": { "value": "#F7F7F5", "type": "color" }
    },
    "dark": {
      "background": { "value": "#0E0E10", "type": "color" }
    }
  },
  "spacing": {
    "md": { "value": "16px", "type": "dimension" }
  }
}
```

### `compose` (Android)

Output: `<output-dir>/DesignTokens.kt`

Genera un object Kotlin con companion objects por categoria:

```kotlin
object DesignTokens {
    object Colors {
        val backgroundLight = Color(0xFFF7F7F5)
        val backgroundDark = Color(0xFF0E0E10)
        val surfaceLight = Color(0xFFFFFFFF)
        // ...
    }
    object Spacing {
        val md = 16.dp
    }
    object Typography {
        val h1 = TextStyle(
            fontSize = 32.sp,
            fontWeight = FontWeight.W700,
            lineHeight = 36.8.sp
        )
    }
}
```

### `swiftui` (iOS)

Output: `<output-dir>/DesignTokens.swift`

Genera enums y extensions:

```swift
import SwiftUI

enum DesignTokens {
    enum Colors {
        static let backgroundLight = Color(hex: "#F7F7F5")
        static let backgroundDark = Color(hex: "#0E0E10")
    }
    enum Spacing {
        static let md: CGFloat = 16
    }
}
```

### `tailwind`

Output: `<output-dir>/tailwind.config.js` (parcial; el usuario integra a su config existente).

Estructura:
```js
module.exports = {
  theme: {
    extend: {
      colors: {
        background: { light: '#F7F7F5', DEFAULT: '#F7F7F5', dark: '#0E0E10' },
        surface: { light: '#FFFFFF', DEFAULT: '#FFFFFF', dark: '#1A1A1D' }
      },
      spacing: {
        md: '16px'
      },
      borderRadius: {
        md: '16px'
      }
    }
  }
}
```

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
