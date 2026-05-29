---
name: kb-design-layout
description: Base de conocimiento para sistemas de layout y responsive. Define grid base por plataforma, breakpoints, adaptive vs responsive, safe areas, notches, foldables y tablets. Solo se activa cuando `target_platforms` del brief incluye Web o tablet; en mobile single-platform aplica una version reducida.
argument-hint: "(cargada automaticamente por agentes y workflows de design)"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Design Layout

Eres la fuente de verdad para layout y responsive. Las decisiones de spacing token-level y elevation viven en `kb-design-expert`; aqui se decide la geometria del lienzo.

## Regla 1: Activacion por target_platforms

Esta kb se aplica con distinta intensidad segun `target_platforms` del brief:

- **Solo mobile (iOS / Android)**: aplica version minima — safe areas, density spacing, orientacion.
- **Mobile + tablet**: aplica todo lo anterior + breakpoints tablet, adaptive layouts.
- **Mobile + web** o **web only**: aplica todo + grid system, breakpoints desktop, container widths.
- **Foldables**: aplica todo + dual-screen patterns.

Si `target_platforms` no incluye web ni tablet, las Reglas 5-7 de esta kb son opcionales.

## Regla 2: Spacing system base

`spacing` del frontmatter del `DESIGN.md` declara una escala fija. Reglas para usarla:

- Multiplos de 4 (4, 8, 12, 16, 24, 32, 48, 64) — alineamiento con plataformas nativas.
- Multiplos de 8 como ritmo dominante; 4 solo para ajustes finos.
- Spacing entre campos de form: `md` (16px).
- Spacing entre grupos: `lg` (24px) o `xl` (32px).
- Margen lateral mobile: 16-20px en `density: medium`, 12-16px en `density: high`, 24px en `density: low`.

## Regla 3: Safe areas y respeto de OS

- iOS: respetar safe areas (notch, dynamic island, home indicator) mediante padding inset.
- Android: respetar status bar y navigation bar (gesture nav o 3-button).
- En fullscreen content (video, mapa, foto a pantalla completa) los controles pueden invadir las safe areas pero el contenido critico no debe.
- Edge-to-edge en Android 12+: contenido bajo system bars con tratamiento de transparencia.

## Regla 4: Orientacion

Decisiones a nivel producto:

- **Portrait only**: la mayoria de apps mobile. Bloqueo en codigo.
- **Portrait + landscape**: si la app justifica landscape (video, lectura, juegos, herramientas profesionales).
- **Landscape only**: muy raro, solo si la naturaleza del contenido lo exige.

Si soporta ambas, cada pantalla declara su comportamiento landscape en `*_views.md` (raro que requiera rediseno; comun que requiera ajuste de masthead o sticky elements).

## Regla 5: Breakpoints estandar (cuando aplica)

Si `target_platforms` incluye tablet o web, declarar breakpoints en el `DESIGN.md`:

- `xs`: 0-359px (mobile pequeno, edge case).
- `sm`: 360-639px (mobile estandar).
- `md`: 640-1023px (tablet / mobile grande landscape).
- `lg`: 1024-1439px (tablet landscape / desktop pequeno).
- `xl`: 1440-1919px (desktop estandar).
- `2xl`: 1920+ (desktop grande).

Estos son breakpoints orientativos; el producto puede declarar los suyos siempre que el `DESIGN.md` los explicite.

## Regla 6: Grid system (solo si web o tablet)

Si aplica, el `DESIGN.md` declara grid en el frontmatter:

```yaml
grid:
  mobile:
    columns: 4
    gutter: 16
    margin: 16
  tablet:
    columns: 8
    gutter: 16
    margin: 24
  desktop:
    columns: 12
    gutter: 24
    margin: 32
  max_content_width: 1200
```

Reglas:
- Mobile no necesita grid de columnas; usar spacing + container.
- Tablet: 8 columnas estandar.
- Desktop: 12 columnas estandar.
- Max content width evita que texto y forms se vuelvan ilegibles en pantallas grandes (60-75ch para texto de lectura, 1200-1400px para layouts complejos).

## Regla 7: Adaptive vs Responsive

- **Responsive**: el mismo layout escala fluido entre breakpoints (cards que cambian de 1 a 2 a 3 columnas).
- **Adaptive**: el layout cambia significativamente entre breakpoints (mobile: stack; tablet: master-detail; desktop: 3 paneles).

Heuristica:
- Productos de consumo (lectura, listas, content): responsive funciona bien.
- Productos B2B con paneles complejos (dashboards, herramientas, editores): adaptive es mas adecuado.
- Forms: responsive con max-width acotado, no adaptive.

Documentar la decision en `## Layout` del `DESIGN.md`.

## Regla 8: Patrones de navegacion por plataforma

- **Mobile**:
  - Bottom navigation: 3-5 destinos top-level.
  - Drawer / hamburger: solo si bottom nav no cubre la jerarquia (raro; si necesitas drawer, replantea la jerarquia).
  - Tabs: dentro de una seccion, no como navegacion principal.
  - Back: respetar gesto del sistema; boton back en topbar opcional.

- **Tablet**:
  - Master-detail si aplica al contenido (correo, files, chat).
  - Bottom navigation se mantiene o se sustituye por side rail.

- **Desktop / Web**:
  - Top navigation horizontal en productos consumer.
  - Side navigation vertical en productos B2B / admin.
  - Breadcrumbs si la jerarquia es profunda (3+ niveles).

## Regla 9: Foldables y dual-screen (opcional, si target_platforms lo incluye)

- Posture awareness: detectar postura del dispositivo (flat, half-open, tent, book).
- Dos paneles cuando half-open: master-detail natural.
- Crossing the hinge: evitar elementos interactivos justo en el hinge.
- Fallback a single screen layout cuando el dispositivo esta plegado.

## Regla 10: Anti-patrones de layout

- Hambruger menu como navegacion principal en mobile (oculta jerarquia).
- Layouts fijos en px sin breakpoints en web.
- Texto que llega a ancho de 100+ caracteres en desktop (ilegible).
- Botones primarios alejados del thumb-reach en mobile (zona inferior).
- Sticky headers que ocupan mas del 15% de la altura disponible.
- Modales fullscreen en desktop (deberian ser dialogs centrados con max-width).
- Diseno desktop-first que se rompe en mobile.

## Regla 11: Como se documenta layout en DESIGN.md

Frontmatter YAML — bloque opcional `grid` si aplica (Regla 6).

Seccion markdown `## Layout`:

- **Spacing scale** y como usarla.
- **Container widths** y max content width.
- **Breakpoints** (si aplica) con que cambia en cada uno.
- **Adaptive vs responsive**: cual es la estrategia general.
- **Navegacion**: que patron de navegacion top-level se usa por plataforma.
- **Safe areas y orientacion**: politicas del producto.
- **Foldables**: solo si aplica al producto.
