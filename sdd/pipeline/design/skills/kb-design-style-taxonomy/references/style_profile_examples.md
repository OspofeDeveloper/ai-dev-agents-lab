# Ejemplos de perfiles visuales con bien vs mal

Estos ejemplos son ilustrativos. No sustituyen las reglas normativas de `SKILL.md`. Cada familia tiene un ejemplo positivo (bien hecho) y uno negativo (errores comunes que debes evitar).

---

## productive-minimal

### Bien hecho — Fintech operativa para profesionales

```yaml
visual_personality:
  style_family: productive-minimal
  secondary_family: depth-material
  density: medium
  depth: low
  typography_mode: utilitarian
  color_energy: low
  motion_level: low
  adjectives:
    - trustworthy: contraste robusto, estados visibles y tono sobrio
    - efficient: listas compactas y acciones primarias muy claras
    - numerical: cifras prominentes con alineacion consistente (tabular nums)
    - scannable: jerarquia tipografica clara entre titulares y datos
    - calm: paleta de grises calidos sin acentos cromaticos competidores
  anti_patterns:
    - generic-saas
    - playful-when-trust-is-required
    - decorative-gradients-without-meaning
    - flat-without-hierarchy
```

Por que funciona: la familia se alinea con la tarea (lectura intensa de datos), la voz sobria reduce friccion, el `motion_level: low` evita distracciones en sesiones largas.

### Mal hecho — Dashboard con personalidad forzada

```yaml
visual_personality:
  style_family: productive-minimal
  density: medium
  depth: medium
  typography_mode: brand-forward      # contradice utilitarian de la familia
  color_energy: high                  # genera saturacion incompatible
  motion_level: medium                # ruido en sesiones largas
  adjectives:
    - modern: vacio
    - clean: redundante con la familia
    - sleek: marketing-talk sin implicacion
  anti_patterns:
    - generic-saas                    # solo este, dejando otros riesgos sin cubrir
```

Por que esta mal:
- `color_energy: high` choca con la naturaleza analitica del producto.
- Adjetivos vacios sin implicacion concreta.
- Solo un anti-patron declarado (deberian ser 2-4).
- `typography_mode` rompe la familia base.

---

## calm-minimal

### Bien hecho — App de mindfulness

```yaml
visual_personality:
  style_family: calm-minimal
  density: low
  depth: flat
  typography_mode: neutral-humanist
  color_energy: low
  motion_level: low
  adjectives:
    - calm: espacios amplios y ritmo visual pausado
    - reassuring: mensajes y jerarquia que reducen ansiedad
    - supportive: formularios y estados que guian sin saturar
    - warm: paleta calida con tonos tierra
    - quiet: ausencia deliberada de notificaciones visuales agresivas
  anti_patterns:
    - dribbblified-overdesigned
    - brand-saturated-at-cost-of-clarity
    - aggressive-color-states
    - density-when-calm-is-required
```

### Mal hecho — Producto de salud con energy alta

```yaml
visual_personality:
  style_family: calm-minimal
  density: medium
  depth: low
  typography_mode: brand-forward      # rompe neutral-humanist
  color_energy: medium                # demasiado para calm
  motion_level: medium                # excede el caracter calmo
  adjectives:
    - serene: ok
    - vibrant: contradice calm        # adjetivo conflictivo
    - playful: incompatible con health-trust
  anti_patterns:
    - generic-saas
```

Por que esta mal:
- Adjetivos contradictorios entre si (`serene` + `vibrant` + `playful`).
- `color_energy` y `motion_level` no coherentes con la familia.
- Un solo anti-patron, omitiendo los riesgos reales (`brand-saturated-at-cost-of-clarity`).

---

## expressive-modern

### Bien hecho — App de fitness consumer

```yaml
visual_personality:
  style_family: expressive-modern
  density: medium
  depth: low
  typography_mode: brand-forward
  color_energy: high
  motion_level: medium
  adjectives:
    - energetic: acentos intensos y CTA claramente protagonistas
    - motivational: progresos y logros visibles sin ruido excesivo
    - social: imagery y componentes que favorecen participacion
    - bold: tipografia display con peso fuerte en hero moments
    - vibrant: paleta saturada usada con disciplina (solo en acentos)
  anti_patterns:
    - premium-but-illegible
    - flat-without-hierarchy
    - dribbblified-overdesigned
```

### Mal hecho — Producto financiero "moderno"

```yaml
visual_personality:
  style_family: expressive-modern     # familia incompatible con dominio
  density: low
  depth: medium
  typography_mode: brand-forward
  color_energy: high
  motion_level: medium
  adjectives:
    - modern: vacio
    - fresh: marketing-talk
  anti_patterns:
    - generic-saas
```

Por que esta mal:
- La familia no encaja con el dominio (un fintech necesita `productive-minimal` o `calm-minimal`, no expresivo).
- `color_energy: high` baja la legibilidad de datos numericos densos.
- Si la marca exige expresividad en fintech, la solucion es `productive-minimal` con `clarity_vs_brand: brand-forward` en el brief, no cambiar de familia.

---

## editorial-premium

### Bien hecho — Plataforma de lectura curada

```yaml
visual_personality:
  style_family: editorial-premium
  density: low
  depth: flat
  typography_mode: editorial
  color_energy: low
  motion_level: low
  adjectives:
    - refined: tipografia serif con espaciado generoso
    - immersive: hero sections con foto a sangrado completo
    - quiet: paleta monocromatica con un acento minimo
    - timeless: composicion clasica, no perseguir tendencias
    - aspirational: detalles cuidados (line-height generoso, kerning manual)
  anti_patterns:
    - premium-but-illegible
    - dribbblified-overdesigned
    - density-when-immersion-is-required
```

### Mal hecho — News app con editorial-premium

```yaml
visual_personality:
  style_family: editorial-premium
  density: high                       # contradice editorial
  depth: low
  typography_mode: editorial
  color_energy: medium
  motion_level: medium
  adjectives:
    - elegant: vacio
    - premium: marketing-talk
```

Por que esta mal:
- News con `density: high` no es editorial-premium; es probablemente `productive-minimal` con tono editorial en hero.
- Adjetivos vacios.

---

## depth-material

### Bien hecho — App de gestion de proyectos con multiples paneles

```yaml
visual_personality:
  style_family: depth-material
  density: medium
  depth: medium
  typography_mode: neutral-humanist
  color_energy: low
  motion_level: medium
  adjectives:
    - layered: elevation usado para jerarquia, no decoracion
    - spatial: cards y paneles refuerzan navegacion mental
    - tactile: estados de pressed con scale + opacity
    - organized: separaciones claras entre contextos via elevation
  anti_patterns:
    - shadow-soup
    - inconsistent-elevation-tiers
    - depth-without-purpose
```

### Mal hecho — App simple con depth-material por moda

```yaml
visual_personality:
  style_family: depth-material
  density: low
  depth: high                         # excesivo
  typography_mode: editorial
  color_energy: medium
  motion_level: medium
  adjectives:
    - modern: vacio
    - elevated: redundante con la familia
```

Por que esta mal:
- `depth-material` con producto simple sin jerarquia espacial real produce sombras sin sentido.
- `depth: high` sin justificacion convierte cada componente en una caja flotante.
- Si el producto no tiene multiples capas, paneles, mapas u overlays, no es depth-material.

---

## Patrones transversales de "mal hecho"

Independientemente de la familia, estos errores aparecen en briefs de junior:

1. **Adjetivos vacios**: "modern", "clean", "fresh", "minimal", "sleek" sin implicacion concreta en UI.
2. **Adjetivos contradictorios**: `serene` + `vibrant`, `quiet` + `bold` en la misma personality.
3. **Anti-patrones genericos**: declarar solo `generic-saas` cuando los riesgos reales son otros.
4. **`color_energy` o `motion_level` que choca con la familia**: la incoherencia se nota inmediatamente en producto.
5. **`secondary_family` por miedo a comprometerse**: si no la necesitas, no la declares (`secondary_family: none` es valido).
6. **Personalidad heredada de otro producto sin justificacion**: copiar el visual_personality de Stripe en un producto que no es fintech B2B.
