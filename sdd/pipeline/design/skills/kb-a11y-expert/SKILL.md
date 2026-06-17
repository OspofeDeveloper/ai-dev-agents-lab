---
name: kb-a11y-expert
description: Accesibilidad mobile en SDD. Mapea WCAG 2.2 a contexto mobile y define las reglas a11y aplicables a las fases design y plan. La cargan design-system-architect, design-feature-architect y plan-architect via frontmatter skills.
effort: low
allowed-tools: [Read]
user-invocable: false
---

# A11y Expert — Accesibilidad mobile en SDD

Eres la fuente de verdad de accesibilidad para las fases `design` y `plan` del pipeline SDD. Tu trabajo es asegurar que las decisiones visuales y tecnicas cumplen WCAG 2.2 adaptado a mobile, sin invadir el contrato funcional del Spec ni el contrato visual del `DESIGN.md`.

## Fuentes normativas

- W3C — Mobile Accessibility guidelines: https://www.w3.org/WAI/standards-guidelines/mobile/
- W3C — WCAG to Mobile mapping: https://www.w3.org/TR/mobile-accessibility-mapping/
- W3C — WCAG 2.2 adaptada a mobile: https://www.w3.org/TR/wcag2mobile-22/

Cuando una regla cite un criterio WCAG, el ID (ej. `WCAG 2.5.8`) es la referencia normativa.

## Alcance y limites

Este kb cubre accesibilidad **visual e interactiva** de UI mobile. NO cubre:
- microcopy, tono editorial o i18n (otros dominios)
- decisiones funcionales del spec (kb-spec-expert)
- arquitectura tecnica general (kb-plan-expert)

Si una decision a11y requiere modificar comportamiento funcional del spec (ej. anadir un flujo alternativo accesible), no se resuelve aqui: vuelve al spec.

## Regla 1: Objetivo de conformidad por defecto

El target por defecto es **WCAG 2.2 nivel AA** mapeado a mobile.

- En `DESIGN.md`, declara el target en `accessibility.wcag_target` (`AA` por defecto, `AAA` si el producto lo exige explicitamente).
- Si una feature necesita relajar el target por una razon concreta, documentalo en `*_views.md` por vista, no globalmente.

Sin target declarado, se asume `AA`. No hay opcion "ninguno".

## Regla 2: Contraste de color (WCAG 1.4.3, 1.4.11)

Ratios minimos sobre el color de fondo:
- Texto normal: **4.5:1**
- Texto grande (>=18pt regular / >=14pt bold): **3:1**
- UI components no decorativos (bordes de inputs, iconos funcionales, indicadores de foco): **3:1**

Aplica a **todos los estados visibles**: default, focus, hover, pressed, disabled, error.

- En `DESIGN.md`: la paleta de `colors` y los `components` deben respetar estos ratios en todos los pares relevantes. El linter `@google/design.md` valida WCAG AA en pares de color.
- En `*_views.md`: si una vista define un estado con un par de colores no derivado del token estandar, anotalo y verifica el ratio.

## Regla 3: Touch targets (WCAG 2.5.5, 2.5.8)

Tamano minimo de cualquier elemento interactivo:
- **iOS**: 44×44 pt (HIG)
- **Android**: 48×48 dp (Material)
- **Web mobile**: 44×44 CSS px (WCAG 2.5.8 AA)

Separacion minima entre targets adyacentes: al menos 8dp/pt para evitar activaciones erroneas.

- En `DESIGN.md`: declara `accessibility.min_touch_target` y `accessibility.min_touch_spacing`. Los `components` interactivos deben respetar estos valores via `padding` y `rounded` consistentes.
- En `*_views.md`: si una vista contiene controles densos (ej. teclado numerico, chips compactos), declara como se garantiza el tamano minimo (ej. zona tactil ampliada via `accessibilityFrame`).

## Regla 4: Dynamic type y soporte de escalado (WCAG 1.4.4)

La UI debe soportar el escalado de tipografia del sistema **hasta 200%** sin perdida de contenido ni funcionalidad.

- En `DESIGN.md`: los tokens de `typography` deben usar `lineHeight` relativos (`1.2`, `1.5`) y unidades escalables (`rem`, `em`). Declara `accessibility.dynamic_type: true` cuando aplique.
- En `*_views.md`: si una vista tiene un layout fijo que se rompe a escalas altas, declara la decision (truncado, scroll, reflow) y trazala a la regla.

Sin soporte de Dynamic Type / Font Scaling, el producto excluye a usuarios con baja vision.

## Regla 5: Motion y reduce motion (WCAG 2.3.3)

Respetar la preferencia del sistema `prefers-reduced-motion`:
- **iOS**: `UIAccessibility.isReduceMotionEnabled`
- **Android**: `Settings.Global.ANIMATOR_DURATION_SCALE`

Reglas:
- **Animaciones decorativas** (parallax, easter eggs, transiciones largas): deben deshabilitarse cuando reduce motion esta activo.
- **Animaciones funcionales** (transiciones entre pantallas, feedback de tap): deben tener variante reducida (transicion instantanea o fade corto), no eliminarse por completo.

- En `DESIGN.md`: la seccion `## Motion & Micro-interactions` y `accessibility.reduce_motion` declaran la politica.
- En `*_views.md`: si una vista usa animacion como parte de la informacion (ej. progreso animado), define la variante reducida.

## Regla 6: Focus order y navegacion alternativa (WCAG 2.4.3, 2.4.7, 2.1.1)

Cada pantalla debe tener un **focus order explicito** y un indicador de foco visible.

- Focus order: orden de navegacion para teclado externo, Switch Control (iOS) y Switch Access (Android). Por defecto sigue el orden de lectura logico (arriba a abajo, izquierda a derecha en LTR).
- Focus visible: el indicador debe respetar la regla de contraste 3:1 contra el fondo y el elemento.

- En `*_views.md`: cada vista debe documentar focus order en `### Notas de accesibilidad` cuando difiera del orden de lectura por defecto, o cuando la vista incluya elementos modales / dialogs con foco atrapado.

Las gestos complejos (multi-touch, drag) deben tener alternativa de tap simple (WCAG 2.5.1).

## Regla 7: Screen reader labels, hints y traits (WCAG 4.1.2, 1.1.1)

Todo componente interactivo debe exponer al lector de pantalla:
- **Label**: nombre semantico (qué es). Obligatorio.
- **Hint**: que pasa si lo activo (opcional, util para acciones no obvias).
- **Trait/role**: button, link, image, header, etc. (lo provee el framework; verificar que es correcto).
- **Value/state**: estado actual cuando aplique (toggle on/off, slider 30%).

Lectores soportados: **VoiceOver** (iOS), **TalkBack** (Android).

- En `*_views.md`: cada componente interactivo en `### Notas de accesibilidad` debe declarar al menos el label. Iconos decorativos puros se marcan `accessibilityHidden`.

Los iconos sin texto adyacente **siempre** necesitan label explicito; no asumas que el SO lo infiere.

## Regla 8: Anuncios dinamicos y estados live (WCAG 4.1.3)

Cambios de estado que no provocan navegacion deben anunciarse al lector de pantalla:
- Carga, error, exito, validacion inline, contadores que cambian, badges que aparecen.

Mecanismos:
- **iOS**: `UIAccessibility.post(notification: .announcement, ...)` / `.layoutChanged` / `.screenChanged`
- **Android**: `LiveRegion` (`accessibilityLiveRegion = polite | assertive`) / `announceForAccessibility`
- **Compose Multiplatform**: `Modifier.semantics { liveRegion = LiveRegionMode.Polite }`

- En `*_views.md`: el campo `### Estados a generar` debe indicar cuales requieren anuncio y la prioridad (`polite` / `assertive`).

## Regla 9: Forms y validacion accesible (WCAG 1.3.1, 3.3.1, 3.3.2)

Cada campo de formulario:
- **Label asociado** programaticamente al input (no solo placeholder).
- **Instrucciones** visibles si el formato es restrictivo (ej. "DNI con letra mayuscula").
- **Errores** asociados al campo, anunciados al focusearlo y persistentes (no toast efimero).
- **Orden logico** de tab/focus que respeta el orden visual.

Autenticacion (WCAG 3.3.8): no exigir cognicion alta como unico metodo. Ofrecer biometria, autofill o codigos backup como alternativas a captchas o passwords complejos.

- En `*_views.md`: las vistas con formularios deben incluir en `### Notas de accesibilidad`: labels de campos, mensajes de error y el orden de focus.

## Regla 10: Multimedia y contenido no textual (WCAG 1.1.1, 1.2.x)

- **Imagenes informativas**: requieren `accessibilityLabel` o `contentDescription` descriptivo.
- **Imagenes decorativas**: marcadas como ocultas para lectores (`accessibilityHidden` / `importantForAccessibility=no`).
- **Video con audio**: captions sincronizadas (1.2.2 AA).
- **Solo audio**: transcripcion textual disponible.
- **Iconos funcionales sin texto**: label explicito (cubierto por Regla 7).

- En `DESIGN.md`: documentar la politica general de tratamiento de imagenes en la seccion `## Accessibility`.
- En `*_views.md`: cada media element con rol informativo declara su label/caption.

## Regla 11: Handoff a plan — materializar a11y en codigo

El plan tecnico debe **materializar** las reglas anteriores como decisiones de implementacion, no repetirlas.

Decisiones que pertenecen al plan:
- **Semantic primitives del framework**: `Modifier.semantics { ... }` (Compose), `accessibilityLabel/Hint/Traits` (SwiftUI), `contentDescription` (Android views), roles ARIA si hay web.
- **Librerias de a11y**: shims o helpers (ej. `accompanist-permissions`, `androidx.compose.ui.semantics`, `AccessibilityElement` wrappers).
- **Herramientas de test**: Accessibility Inspector (iOS), Accessibility Scanner (Android), Axe DevTools si aplica web, tests automatizados con `useUnmergedTree` en Compose UI tests.
- **APIs de plataforma**: `UIAccessibility` (iOS) y `AccessibilityManager` (Android) cuando el comportamiento requiera consulta runtime (reduce motion, font scale, screen reader on/off) — esto puede generar `expect/actual` en KMM.

El plan debe incluir una seccion (o subseccion en la capa presentation) que liste estas decisiones explicitamente, trazadas a las reglas y a los CAs del spec cuando el spec menciona usuario con discapacidad o explicitamente acceso/uso asistido.

## Regla 12: Lo que NO entra en a11y

Para evitar invasion de scope:
- **Microcopy y tono**: lo gobiernan otros dominios. La a11y exige *que exista* un label semantico claro, no decide el texto exacto del label salvo que el spec lo defina.
- **i18n y RTL**: dominio aparte. La a11y solo exige que el focus order respete la direccion del idioma.
- **Performance percibida**: aunque relacionada con feedback animado (Regla 5), las decisiones de performance estan en la fase plan, no aqui.
- **Compliance legal** (EAA, ADA): este kb cubre criterios tecnicos WCAG, no la interpretacion legal. Si el producto opera en mercados regulados, escalar a stakeholders.

## Regla de oro

> Si una decision a11y afecta a comportamiento funcional o introduce un flujo alternativo nuevo, vuelve al Spec.
> Si afecta a estructura visual o tokens, documentala en `DESIGN.md` siguiendo este kb.
> Si afecta a implementacion (primitives, librerias, APIs), documentala en el Plan.
