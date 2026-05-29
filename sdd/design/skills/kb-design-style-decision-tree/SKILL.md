---
name: kb-design-style-decision-tree
description: Arbol de decision navegable para elegir style_family y variables visuales clave segun el contexto del producto. Pensado para diseñadores junior que no saben elegir entre productive-minimal vs depth-material sin acompanamiento. Cargada por `wf-design-intake` en modo guided.
argument-hint: "(cargada automaticamente por wf-design-intake)"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Design Style Decision Tree

Eres el guia que ayuda a una persona sin experiencia a cerrar las decisiones del brief. No redefines reglas de la taxonomia: la traduces a preguntas concretas y secuenciales.

## Regla 1: El arbol es navegable, no lineal

No fuerces al usuario a recorrer las 13 variables en orden rigido. Empieza por el eje que mas impacto tiene (familia visual) y deriva el resto.

Orden recomendado:
1. **style_family** (gran impacto, fija contexto para todo lo demas)
2. **clarity_vs_brand** (afecta voice, motion, color energy)
3. **density** y **depth** (derivan en mucha parte del visual)
4. **color_energy**, **motion_level**, **typography_mode** (suelen seguir a la familia)
5. **voice_tone** (puede tomarse del default por familia)
6. **target_platforms**, **accessibility_target** (suelen venir del spec o PRD)

## Regla 2: Decision tree para style_family

Preguntas, en orden:

**P1: ¿Es B2B / herramienta de trabajo / backoffice / dashboard / fintech operativa?**
- Si → `productive-minimal`. Verificar P1a.
  - **P1a**: ¿Hay capas, paneles, mapas o jerarquia espacial fuerte? → considerar `depth-material` como secundaria.
- No → P2.

**P2: ¿El producto opera en salud, bienestar, mindfulness, self-service de confianza o servicios financieros que requieren transmitir calma?**
- Si → `calm-minimal`. Verificar P2a.
  - **P2a**: ¿La marca exige alto contraste cromatico o expresividad? → marcar conflicto y considerar `expressive-modern` con `clarity-first`.
- No → P3.

**P3: ¿Es consumer / lifestyle / fitness / social / entertainment con necesidad de diferenciacion emocional?**
- Si → `expressive-modern`. Verificar P3a.
  - **P3a**: ¿El producto maneja datos numericos densos o transacciones criticas? → marcar conflicto y considerar `productive-minimal` con `brand-forward` adjectives.
- No → P4.

**P4: ¿Es media / lectura / contenido curado / luxury / experiencia aspiracional?**
- Si → `editorial-premium`.
- No → P5.

**P5: ¿La interfaz se apoya fuertemente en jerarquia espacial, overlays, paneles, mapas o colecciones multi-capa?**
- Si → `depth-material`.
- No → P6.

**P6: Ninguna familia encaja claramente.**
- Si el junior llega aqui, **no recomendar `custom` automaticamente**. Volver atras y preguntar por el actor y la tarea dominante, no por la marca.
- Si tras dos vueltas no encaja, marcar `[REQUIERE_REVISION_SENIOR]` y proponer `productive-minimal` como default conservador.

## Regla 3: Decision tree para clarity_vs_brand

Preguntas:

**Q1: ¿El producto se rige por normativa (financiero, salud, seguros, gobierno, accesibilidad obligatoria)?**
- Si → `clarity-first`.
- No → Q2.

**Q2: ¿El usuario usa el producto como herramienta de trabajo intensa varias horas al dia?**
- Si → `clarity-first`. La marca no debe entorpecer la tarea.
- No → Q3.

**Q3: ¿La diferenciacion de marca es una necesidad comercial explicita (segmento muy competido, marca como ventaja)?**
- Si → `brand-forward`.
- No → `balanced`.

**Q4: Si Q3=si y el producto es B2B o regulado → marcar conflicto, recomendar `balanced` y documentar tradeoff en el brief.**

## Regla 4: Decision tree para density

- Producto B2B / dashboard / muchos datos por pantalla → `high`.
- Producto consumer / lifestyle → `medium`.
- Producto editorial / lectura / experiencia inmersiva → `low`.

Si el usuario duda, `medium` es el default seguro.

## Regla 5: Decision tree para depth

- Familia `depth-material` → `medium` o `high`.
- Familia `expressive-modern` con foco visual → `low` o `medium`.
- Resto de familias → `flat` o `low`.
- Si el producto es flat-design intencional → `flat` con nota en `## Elevation & Depth`.

## Regla 6: Decision tree para color_energy

- `clarity-first` o producto regulado → `low`.
- `balanced` o consumer estandar → `medium`.
- `brand-forward` o entertainment / gaming-adjacent → `high`.

Excepcion: salud y mindfulness, aunque no sean `clarity-first`, prefieren `low` por la naturaleza del dominio.

## Regla 7: Decision tree para motion_level

- Producto regulado / B2B intensivo → `low`.
- Default consumer → `low` o `medium`.
- Producto con onboarding gamificado o expresion de marca alta → `medium`.

`motion_level: none` solo si el dominio lo exige (productos para usuarios con epilepsia, terminales medicas, etc.).

## Regla 8: Decision tree para typography_mode

Derivar de `style_family`:
- `productive-minimal` → `utilitarian`.
- `calm-minimal` → `neutral-humanist`.
- `expressive-modern` → `brand-forward` (si hay budget) o `neutral-humanist`.
- `editorial-premium` → `editorial`.
- `depth-material` → `neutral-humanist` o `utilitarian`.

Override valido si la marca aporta una fuente propia.

## Regla 9: Decision tree para voice_tone

Derivar de `style_family` + `clarity_vs_brand`:

- `productive-minimal` + `clarity-first` → neutral + tecnico/mixto + neutro + serio.
- `calm-minimal` + `balanced` → cercano + accesible + humano + medido.
- `expressive-modern` + `brand-forward` → cercano + accesible + calido + medido/ludico.
- `editorial-premium` → neutral + mixto + humano + medido.
- `depth-material` → neutral + mixto + neutro + medido.

El usuario puede aceptar el default o ajustar uno o dos ejes con justificacion.

## Regla 10: Como se usa este arbol en `wf-design-intake`

En modo `guided`:
1. El workflow lee este arbol y plantea las preguntas P1-P6 (Regla 2) hasta cerrar `style_family`.
2. Luego Q1-Q4 (Regla 3) para `clarity_vs_brand`.
3. Aplica Reglas 4-9 para derivar el resto con confirmacion ligera del usuario.
4. Si se detecta conflicto (P1a, P2a, P3a, Q4), no decide unilateralmente: lo presenta al usuario.

En modo `hybrid`:
1. Aplica el arbol internamente para proponer valores.
2. Pide confirmacion solo de `style_family` y `clarity_vs_brand`.
3. Deriva el resto y los presenta como propuestas con micro-explicacion.

En modo `auto`:
1. Aplica el arbol sin preguntar.
2. Marca cada variable con `source: inferred` (segun trazabilidad de Regla 6 de `wf-design-intake`).
3. Si encuentra conflicto P1a/P2a/P3a/Q4, prefiere la opcion conservadora y documenta razon.

## Regla 11: Anti-patrones del arbol

- Saltar a la respuesta sin recorrer las preguntas (el arbol enseña a decidir, no solo decide).
- Decidir `custom` sin haber agotado P1-P5.
- Permitir combinaciones bloqueadas: `clarity-first` + `color_energy: high` sin justificacion; `productive-minimal` + `motion_level: medium` sin razon explicita; `calm-minimal` + `density: high`.
- Usar el arbol para forzar al usuario; siempre debe poder anular una respuesta con motivo.
