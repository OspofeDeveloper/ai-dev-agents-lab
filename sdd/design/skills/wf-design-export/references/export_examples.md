# Export Examples by Platform

## CSS (`tokens.css`)

`:root` para modo light, `[data-theme="dark"]` para modo dark, `@media (prefers-contrast: more)` para high-contrast si existe. Typography como variables `--font-<role>-size`, `--font-<role>-weight`, etc.

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

## Style Dictionary (`tokens.json`)

Formato W3C Design Tokens.

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

## Compose / Android (`DesignTokens.kt`)

`object DesignTokens` con companion objects por categoría.

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

## SwiftUI / iOS (`DesignTokens.swift`)

`enum DesignTokens` con enums y extensions.

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

## Tailwind (`tailwind.config.js`)

Objeto parcial `theme.extend`. El usuario lo integra a su config existente.

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
