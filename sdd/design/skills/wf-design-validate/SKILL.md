---
name: wf-design-validate
description: "Audita un DESIGN.md ya existente contra el contrato visual (kb-design-expert, kb-design-style-taxonomy, kb-design-brief) y el linter oficial de Google design.md. No regenera el archivo, solo reporta DESIGN_GAP o OK."
when_to_use: "Activa en frases como 'valida el DESIGN.md', 'revisa que el sistema visual esta bien', 'audita el design despues de editarlo', 'comprueba que el DESIGN.md cumple el brief'. No activa para generar o modificar el archivo."
argument-hint: "<DESIGN.md> [--brief <DESIGN_BRIEF.md>] [--views <feature_views.md>] [--lenient] [--pedagogical]"
effort: medium
allowed-tools: [Read, Bash]
context: fork
agent: design-architect
---

# design-validate — Orquestador del Flujo SDD (Etapa Design)

Tu rol es de **auditor puro**: leer un `DESIGN.md` existente, contrastar contra brief y kbs, ejecutar el linter de Google y devolver una lista de hallazgos. No escribes el archivo.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del DESIGN.md**: primer argumento posicional.
- **Path del brief** opcional mediante `--brief`.
- **Path de un `*_views.md`** opcional mediante `--views`: si se pasa, valida tambien microcopy y estados de vista (Reglas 19-20 de `kb-design-expert`).
- **Flag `--lenient`** opcional: relaja el comportamiento por defecto. Hallazgos no-criticos no bloquean. Por defecto la validacion es **estricta** (cualquier `[CRITICO]` o `[ALTO]` cuenta como fallo).
- **Flag `--pedagogical`** opcional: cada hallazgo lleva explicacion extendida, referencia a la regla concreta y enlace al ejemplo o checklist relevante. Pensado para diseñadores junior.

Si no hay path o no se reconoce el comando, informa:
> "Uso: `/wf-design-validate <DESIGN.md> [--brief <DESIGN_BRIEF.md>] [--views <feature_views.md>] [--lenient] [--pedagogical]`"

## Paso 2: Verificar el DESIGN.md

1. Verifica que el archivo existe.
2. Lee el archivo completo (frontmatter YAML + markdown).
3. Si no parece un `DESIGN.md` (sin frontmatter o sin secciones canonicas), informa:
   > "Este archivo no parece un `DESIGN.md` SDD. Genera uno con `/wf-design-system` o indica un path valido."

## Paso 3: Resolver DESIGN_BRIEF.md

1. Si se paso `--brief <path>`, leelo.
2. Si no, busca `DESIGN_BRIEF.md` en el mismo directorio del DESIGN.md.
3. Si existe, leelo y usalo para contrastar.
4. Si no existe, registra `BRIEF_GAP: sin brief disponible para contrastar coherencia` y continua. La auditoria sigue valida; solo se acota a estructura.

## Paso 4: Ejecutar el linter de Google design.md

Ejecuta:
```bash
npx @google/design.md lint <path_design>
```

Captura el resultado:
- **Sin errores** → registrar `linter: OK`.
- **Con errores** → guardar la lista completa de errores.
- **npx no disponible** → registrar `linter: SKIPPED` con explicacion.

## Paso 5: Delegar auditoria estructural al agente design-architect

Invoca al agente cargando `kb-design-expert`, `kb-design-style-taxonomy`, `kb-design-brief` y `kb-a11y-expert` con este prompt:

```text
Modo: design-validate
Path del DESIGN.md: <path_design>
Contenido del DESIGN.md:
---
<contenido_completo_design>
---
DESIGN_BRIEF.md (si existe):
---
<contenido_brief_o_N/A>
---
Resultado del linter:
---
<resultado_linter>
---
Flag --strict: <true|false>

INSTRUCCION: audita el DESIGN.md sin reescribirlo. Devuelve una lista de hallazgos con severidad.

Checks obligatorios:

1. **Estructura canonica (kb-design-expert Regla 6)**
   - Orden de secciones correcto
   - Token types validos (sin `fontVariantNumeric`; `fontFeature: "tnum"` aceptado)
   - Valores de `components:` como strings entrecomillados

2. **Visual Personality completo (kb-design-expert Regla 11)**
   - Frontmatter `visual_personality` con `style_family`, `density`, `depth`, `typography_mode`, `color_energy`, `motion_level`, `adjectives`, `anti_patterns`
   - Seccion markdown con 5-7 adjetivos con implicacion concreta
   - Seccion markdown con 2-4 anti-patrones
   - Explicacion de por que la `style_family` encaja

3. **Reference Apps (kb-design-expert Regla 12)**
   - 3-5 apps reales del mercado con aspecto concreto a tomar y justificacion
   - O bien marca `[DESIGN_GAP: investigar apps de referencia en la categoria <X>]`

4. **Familia y escalas validas (kb-design-style-taxonomy)**
   - `style_family` ∈ {productive-minimal, calm-minimal, expressive-modern, editorial-premium, depth-material, custom}
   - `density` ∈ {low, medium, high}
   - `depth` ∈ {flat, low, medium, high}
   - `motion_level` ∈ {none, low, medium}
   - `typography_mode` ∈ {utilitarian, neutral-humanist, brand-forward, editorial}
   - `color_energy` ∈ {low, medium, high}
   - Si `style_family: custom`, debe haber justificacion explicita y anti-patrones reforzados

5. **Anti-patrones declarados no aparecen en Do's**
   - Ningun anti-patron de la Regla 7 de kb-design-style-taxonomy (`generic-saas`, `dribbblified-overdesigned`, `pseudo-realistic`, `playful-when-trust-is-required`, `flat-without-hierarchy`, `premium-but-illegible`, `brand-saturated-at-cost-of-clarity`) aparece descrito como deseable

6. **Coherencia con DESIGN_BRIEF.md (si existe)**
   - `style_family`, `density`, `depth`, `typography_mode`, `color_energy`, `motion_level` coinciden con el brief
   - `clarity_vs_brand` materializado de forma coherente en la jerarquia visual
   - `accessibility_target` (AA/AAA) reflejado en la seccion Accessibility
   - `target_platforms` reflejados (si solo iOS o Android, no documentar tokens especificos de la otra plataforma)
   - Si hay contradiccion con el brief, marca como CRITICO

7. **Accessibility minima (kb-a11y-expert)**
   - Seccion `## Accessibility` presente
   - Contraste documentado, touch targets, motion handling, dynamic type

8. **Estados completos de componente (kb-design-expert Regla 16)**
   - Cada componente interactivo declara los estados aplicables segun su tipologia:
     - Interactivos: default, focus-visible, active, disabled, loading (+ hover si target_platforms incluye Web/desktop, + selected si aplica)
     - Inputs: default, focus, filled, invalid, disabled, read-only
     - Contenedores con estado: default, selected, expanded/collapsed si aplica
   - Estados omitidos sin justificacion `# N/A: <razon>` se reportan como `[ALTO]`
   - Cada estado debe tener decisiones visuales concretas, no solo el label

9. **Type scale completa (kb-design-expert Regla 17)**
   - `typography` declara al menos: h1, h2, h3, body, body-sm, label, caption (y `code` si aplica)
   - Cada rol tiene `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing` (este ultimo opcional pero recomendado en displays/labels)
   - `typography_mode` del brief coherente con la(s) familia(s) de fuentes declaradas

10. **Color modes (kb-design-expert Regla 18)**
    - `colors` declara `light` y `dark` como minimo. `high-contrast` opcional segun `accessibility_target`
    - Cada token de color en `light` tiene equivalente en `dark`. Si falta alguno, `[CRITICO]`
    - `color_mode_policy` declarada (default, user_toggle, high_contrast)
    - Seccion `## Color Modes` presente

11. **Estados de vista en `*_views.md` (kb-design-expert Regla 19)**
    - Solo aplica si la validacion incluye un `*_views.md` adicional via `--views <path>`
    - Cada vista declara: default, loading, empty, error (+ partial/success si aplica)
    - Si un estado no aplica, documentado con `# N/A: <razon>`

12. **Iconography (kb-design-iconography-expert)**
    - Frontmatter `iconography` con `library`, `style`, `stroke_width`/`fill_rule`, `grid`, `sizes`, `semantic_colors`
    - Una sola libreria base declarada
    - `stroke_width` consistente (1.5 o 2, no mezclar)
    - Seccion `## Iconography` presente con justificacion de la libreria elegida

13. **Motion catalog (kb-design-motion-expert)**
    - Frontmatter `motion` con `level`, `reduced_motion_policy`, `durations` (al menos fast, base, medium) y `easing` por rol activo
    - `motion.level` coincide con el brief
    - Seccion `## Motion & Micro-interactions` presente con catalogo de micro-interacciones por componente clave
    - No se declara `motion_level: high` (no existe en este sistema)

14. **Voice & microcopy (kb-design-voice + kb-design-expert Regla 20)**
    - DESIGN.md tiene seccion `## Voice & Microcopy` con los 4 ejes (formality, expertise, warmth, playfulness)
    - Glosario de 5-15 terminos clave presente
    - Politica de mayusculas, puntuacion y emojis declarada
    - Cuando se valide con `--views <path>`: cada vista declara microcopy de accion primaria, empty, error y loading aplicables. Vista con estado declarado sin copy → `[ALTO]`

15. **Forms (kb-design-forms + kb-design-expert Regla 21)**
    - Si el producto declara componentes de form (`input-text`, `input-textarea`, `select`, `date-picker`, `file-upload`, `form-actions`), cada uno tiene los estados aplicables de Regla 3 de `kb-design-forms`
    - Si una vista contiene un formulario (detectable por la presencia de campos en el `*_views.md`), debe listar campos con label, tipo, obligatoriedad y validacion resumida
    - Patrones de form complejos (multistep, autosave) deben documentarse explicitamente cuando aplican

16. **Layout y responsive (kb-design-layout)**
    - Seccion `## Layout` presente con spacing scale, navegacion top-level y safe areas declaradas
    - Si `target_platforms` incluye web o tablet: declarar breakpoints y, si aplica, grid en frontmatter
    - Si `target_platforms` incluye foldables: politicas de postura y dual-screen
    - Spacing scale del frontmatter coherente con `density` del visual_personality

17. **Versionado semver (kb-design-expert Regla 22)**
    - Frontmatter `version: MAJOR.MINOR.PATCH` presente
    - Version coherente con el ultimo entry de `## Changelog`
    - Si hay cambios entre versiones que rompen trazabilidad (cambio de style_family, primary, tipografia), el bump debe ser MAJOR
    - Si el version bump no coincide con la naturaleza del ultimo cambio, marca `[CRITICO]`

Formato de salida estandar:

```
=== DESIGN.md VALIDATION REPORT ===
Path: <path>
Brief: <path o N/A>
Views: <path o N/A>
Linter: OK | ERRORS | SKIPPED

[CRITICO] <descripcion concreta>
[ALTO] <descripcion>
[MEDIO] <descripcion>
[BAJO] <descripcion>

Total: X criticos, Y altos, Z medios, W bajos.
Estado: PASS | PASS_WITH_GAPS | FAIL
```

Formato `--pedagogical` (cada hallazgo lleva contexto extendido):

```
[ALTO] El componente `button-primary` no declara estado `loading`.
  Regla: kb-design-expert Regla 16 (estados de componente).
  Checklist: ${CLAUDE_SKILL_DIR}/../kb-design-expert/references/component_anatomy_checklist.md > "button-primary".
  Por que importa: un boton que dispara accion async sin estado loading
  permite doble click y deja al usuario sin saber si paso algo.
  Como arreglarlo: anade al frontmatter components.button-primary.loading
  con cambio visual (cursor, opacity, spinner inline o cambio de label).
  Ejemplo: ver template ${CLAUDE_SKILL_DIR}/../kb-design-expert/references/design_md_template.md linea 174.
```

Usa el modo pedagogical cuando el usuario sea diseñador junior o pida `--learn` en otros workflows. En el resto, el formato estandar es mas compacto y se prefiere.

Reglas de estado (modo estricto por defecto):
- FAIL: hay al menos un [CRITICO] o [ALTO].
- PASS_WITH_GAPS: hay hallazgos [MEDIO] o [BAJO] solo.
- PASS: ningun hallazgo.

En modo `--lenient`:
- FAIL: solo si hay [CRITICO].
- PASS_WITH_GAPS: cualquier otro hallazgo.
- PASS: ningun hallazgo.

No reescribas el archivo. No propongas patches. Solo reporta.
```

## Paso 6: Informar al usuario

Muestra el reporte tal como lo devuelva el agente. Anade:

- path del DESIGN.md auditado
- path del brief usado (o `N/A`)
- siguiente paso recomendado:
  - si `PASS` → continuar con `/wf-design-feature-prototype`
  - si `PASS_WITH_GAPS` → considerar `/wf-design-delta analyze` para resolverlos
  - si `FAIL` → corregir manualmente o regenerar con `/wf-design-system`

No escribas ningun archivo en este workflow.
