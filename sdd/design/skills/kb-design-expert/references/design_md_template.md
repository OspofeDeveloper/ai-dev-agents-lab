# Template de DESIGN.md

```md
---
version: alpha
name: <Nombre del producto>
description: <Resumen breve del tono visual y contexto del producto>
colors:
  primary: "#000000"
  secondary: "#666666"
  accent: "#0F766E"
  surface: "#FFFFFF"
  background: "#F7F7F5"
  success: "#15803D"
  warning: "#B45309"
  danger: "#B91C1C"
typography:
  h1:
    fontFamily: <Familia principal>
    fontSize: 2.5rem
    fontWeight: 700
    lineHeight: 1.1
  h2:
    fontFamily: <Familia principal>
    fontSize: 1.75rem
    fontWeight: 600
    lineHeight: 1.2
  body:
    fontFamily: <Familia secundaria>
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: <Familia secundaria>
    fontSize: 0.875rem
    fontWeight: 500
    lineHeight: 1.3
rounded:
  sm: 8px
  md: 16px
  lg: 24px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    borderRadius: "{rounded.md}"
  input-default:
    backgroundColor: "{colors.surface}"
    borderColor: "{colors.secondary}"
    borderRadius: "{rounded.sm}"
  card-default:
    backgroundColor: "{colors.surface}"
    borderRadius: "{rounded.md}"
---

## Overview

Describe el caracter general del producto, la sensacion que debe transmitir y 2-4 principios de marca integrados en prose o bullets cortos.

## Colors

Explica como usar la paleta, donde reservar el color acento y que colores evitar.

## Typography

Explica jerarquia visual, contraste entre titulares y cuerpo, y tono editorial o utilitario.

## Layout

Define densidad, espaciado, ritmos verticales y anchuras habituales.

## Shapes

Explica el caracter de bordes, radios y geometria general si es relevante para la identidad.

## Components

Explica como deben sentirse formularios, listas, cards, tabs, dialogs y acciones destructivas. Incluye aqui el tratamiento comun de estados recurrentes si afecta a componentes.

## Do's and Don'ts

- Haz:
  - Regla positiva 1
  - Regla positiva 2
- Evita:
  - Regla negativa 1
  - Regla negativa 2
```
