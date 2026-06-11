# Checklist de validación de DESIGN.md

18 checks normativos que el agente `design-architect` debe ejecutar en modo `design-validate`. Cada check indica la regla de referencia, la severidad si falla y lo que se debe verificar.

Estado declarado sin decisiones visuales concretas = estado vacío (no cuenta). Campo obligatorio ausente sin justificación = severidad indicada.

---

## 1. Estructura canónica (kb-design-system-contract Regla 2)

- Orden de secciones correcto (Overview → Visual Personality → Colors → Typography → Layout → Elevation → Shapes → Components → Do's and Don'ts; secciones custom en posiciones recomendadas)
- Token types válidos (sin `fontVariantNumeric`; `fontFeature: "tnum"` aceptado)
- Valores dentro de `components:` como strings entrecomillados (un bare integer crashea el linter)

---

## 2. Visual Personality completo (kb-design-system-contract Regla 3)

- Frontmatter `visual_personality` con todos los campos: `style_family`, `density`, `depth`, `typography_mode`, `color_energy`, `motion_level`, `adjectives`, `anti_patterns`
- Sección markdown con 5-7 adjetivos de marca con implicación concreta en UI
- Sección markdown con 2-4 anti-patrones explícitos
- Explicación de por qué la `style_family` elegida encaja con el producto, actor y tarea dominante

---

## 3. Reference Apps (kb-design-system-contract Regla 4)

- 3-5 apps reales del mercado con aspecto concreto a tomar (no solo nombre) y justificación de relevancia para este producto
- O bien sección marcada `[DESIGN_GAP: investigar apps de referencia en la categoría <X>]`
- Un DESIGN.md sin Reference Apps → severidad `[ALTO]`

---

## 4. Familia y escalas válidas (kb-design-style-taxonomy)

- `style_family` ∈ {productive-minimal, calm-minimal, expressive-modern, editorial-premium, depth-material, custom}
- `density` ∈ {low, medium, high}
- `depth` ∈ {flat, low, medium, high}
- `motion_level` ∈ {none, low, medium}
- `typography_mode` ∈ {utilitarian, neutral-humanist, brand-forward, editorial}
- `color_energy` ∈ {low, medium, high}
- Si `style_family: custom`: justificación escrita de 2+ párrafos y mínimo 4 anti-patrones

---

## 5. Anti-patrones declarados no aparecen como deseables

Verificar que ninguno de estos anti-patrones de kb-design-style-taxonomy Regla 7 aparece en la sección `## Do's and Don'ts` como comportamiento deseable:
- `generic-saas`
- `dribbblified-overdesigned`
- `pseudo-realistic`
- `playful-when-trust-is-required`
- `flat-without-hierarchy`
- `premium-but-illegible`
- `brand-saturated-at-cost-of-clarity`

---

## 6. Coherencia con DESIGN_BRIEF.md (si existe) — `[CRITICO]` si hay contradicción

- `style_family`, `density`, `depth`, `typography_mode`, `color_energy`, `motion_level` coinciden con el brief
- `clarity_vs_brand` materializado de forma coherente en la jerarquía visual
- `accessibility_target` (AA/AAA) reflejado en la sección Accessibility
- `target_platforms` reflejados (no documentar tokens de plataforma no declarada)

---

## 7. Accesibilidad mínima (kb-a11y-expert)

- Sección `## Accessibility` presente
- Contraste documentado (al menos par primary/on-primary)
- Touch targets declarados
- Motion handling y `prefers-reduced-motion` mencionados
- Dynamic type policy declarada

---

## 8. Estados completos de componente (kb-design-system-contract Regla 7)

Para cada componente interactivo del frontmatter `components:`:
- Interactivos (button, link, tab, toggle, checkbox, radio, switch): `default`, `focus-visible`, `active`, `disabled`, `loading` si async, `selected` si aplica. `hover` solo si target_platforms incluye Web/desktop.
- Inputs (text-input, textarea, select, date-picker, file-picker): `default`, `focus`, `filled`, `invalid`, `disabled`, `read-only`. `loading` si valida async.
- Contenedores con estado (card, list-item, accordion): `default`, `selected`, `disabled`, `loading`, `expanded`/`collapsed` si aplica.

Estados omitidos sin `# N/A: <razón>` → `[ALTO]`. Cada estado debe tener decisiones visuales concretas.

→ Checklist detallado por componente: `${CLAUDE_SKILL_DIR}/../kb-design-system-contract/references/component_anatomy_checklist.md`

---

## 9. Type scale completa (kb-design-system-contract Regla 8)

- `typography` declara al menos: `display`, `h1`, `h2`, `h3`, `body`, `body-sm`, `label`, `caption`. `code` si aplica.
- Cada rol tiene `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`. `letterSpacing` recomendado en displays y labels.
- `typography_mode` del brief coherente con la(s) familia(s) de fuentes declaradas

---

## 10. Color modes (kb-design-system-contract Regla 9)

- `colors` declara `light` y `dark` como mínimo. `high-contrast` opcional según `accessibility_target`
- Cada token en `light` tiene equivalente en `dark`. Si falta alguno → `[CRITICO]`
- `color_mode_policy` declarada (default, user_toggle, high_contrast)
- Sección `## Color Modes` presente

---

## 11. Estados de vista en `*_views.md` (kb-design-feature-artifacts Regla 4)

Solo aplica si se pasa `--views <path>`.
- Cada vista declara: `default`, `loading`, `empty`, `error`. `partial` y `success` si aplican.
- Si un estado no aplica, documentado con `# N/A: <razón>`
- Vista con `empty` declarado sin copy → `[ALTO]`
- Vista con `error` declarado sin copy o acción de recuperación → `[ALTO]`

---

## 12. Iconografía (kb-design-iconography-expert)

- Frontmatter `iconography` con `library`, `style`, `stroke_width`/`fill_rule`, `grid`, `sizes`, `semantic_colors`
- Una sola librería base declarada
- `stroke_width` consistente (1.5 o 2, no mezclar salvo justificación)
- Sección `## Iconography` presente con justificación de la librería elegida

---

## 13. Catálogo de motion (kb-design-motion-expert)

- Frontmatter `motion` con `level`, `reduced_motion_policy`, `durations` (al menos `fast`, `base`, `medium`) y `easing` por rol activo
- `motion.level` coincide con el brief
- Sección `## Motion & Micro-interactions` con catálogo de micro-interacciones por componente clave
- `motion_level: high` no existe en este sistema → `[CRITICO]` si aparece

---

## 14. Voice & microcopy (kb-design-voice + kb-design-feature-artifacts Regla 5)

- Sección `## Voice & Microcopy` con los 4 ejes: `formality`, `expertise`, `warmth`, `playfulness`
- Glosario de 5-15 términos clave del dominio del producto
- Política de mayúsculas, puntuación y emojis declarada
- Con `--views`: cada vista declara microcopy de acción primaria, empty, error y loading aplicables. Vista con estado declarado sin copy → `[ALTO]`

---

## 15. Formularios (kb-design-forms + kb-design-feature-artifacts Regla 6)

Si el producto declara componentes de form (`input-text`, `input-textarea`, `select`, `date-picker`, `file-upload`, `form-actions`):
- Cada uno tiene los estados aplicables del check 8
- Si una vista contiene un formulario: lista campos con label, tipo, obligatoriedad y validación resumida
- Patrones complejos (multistep, autosave) documentados explícitamente cuando aplican

---

## 16. Layout y responsive (kb-design-layout)

- Sección `## Layout` presente con spacing scale, navegación top-level y safe areas declaradas
- Si `target_platforms` incluye web o tablet: breakpoints declarados y grid en frontmatter
- Si `target_platforms` incluye foldables: políticas de postura y dual-screen
- Spacing scale coherente con `density` del `visual_personality`

---

## 17. Versionado semver (kb-design-governance Regla 3)

- Frontmatter `version: MAJOR.MINOR.PATCH` presente
- Versión coherente con el último entry de `## Changelog`
- Si hay cambios que rompen trazabilidad (cambio de style_family, primary, tipografía principal), el bump debe ser MAJOR
- Version bump inconsistente con la naturaleza del último cambio → `[CRITICO]`

---

## 18. Procedencia y confianza de dirección (kb-design-system-contract Regla 10)

- Frontmatter `origin` ∈ {generated, generated-provisional, extracted} (ausencia = generated). Valor fuera de ese conjunto → `[ALTO]`
- Si `origin: generated-provisional`: debe llevar `direction_confidence: provisional` y los campos de dirección inferidos sin evidencia (`style_family`, `primary`/`accent`, `motion_level`) marcados `[INFERIDO]`. Coherencia rota (provisional sin marcadores, o confirmed con marcadores de dirección) → `[MEDIO]`
- El `[INFERIDO]` aquí es **informativo y NO bloquea** ningún gate (la fase Design no tiene sellador mecánico): se **reporta**, no se computa como `[CRITICO]`/`[ALTO]` por sí mismo
- Si `direction_confidence: provisional` y la auditoría de dirección (checks 2/4/6/13) pasa sin hallazgos `[CRITICO]`/`[ALTO]`: el `DESIGN.md` es **promovible**. La promoción `provisional → confirmed` la decide el Paso 5b de `wf-design-validate` con confirmación humana explícita — el agente solo lo **señala** en el reporte, no promueve

---

## Formato de salida estándar

```
=== DESIGN.md VALIDATION REPORT ===
Path: <path>
Brief: <path o N/A>
Views: <path o N/A>
Linter: OK | ERRORS | SKIPPED

[CRITICO] <descripción concreta>
[ALTO] <descripción>
[MEDIO] <descripción>
[BAJO] <descripción>

Total: X críticos, Y altos, Z medios, W bajos.
Estado: PASS | PASS_WITH_GAPS | FAIL
```

Reglas de estado (modo estricto por defecto):
- FAIL: al menos un `[CRITICO]` o `[ALTO]`
- PASS_WITH_GAPS: solo hallazgos `[MEDIO]` o `[BAJO]`
- PASS: ningún hallazgo

Modo `--lenient`:
- FAIL: solo si hay `[CRITICO]`
- PASS_WITH_GAPS: cualquier otro hallazgo

## Formato `--pedagogical`

```
[ALTO] El componente `button-primary` no declara estado `loading`.
  Regla: kb-design-system-contract Regla 7 (estados de componente).
  Checklist: component_anatomy_checklist.md > "button-primary".
  Por qué importa: un botón async sin loading permite doble click.
  Cómo arreglarlo: añade components.button-primary.loading con cambio visual.
  Ejemplo: ver design_md_template.md línea 174.
```
