---
name: kb-design-style-decision-tree
description: SSoT de la UX de navegacion para cerrar style_family y las variables visuales del brief — la secuencia ordenada de preguntas, las ramas de deteccion de conflicto y los fallbacks de guia junior. NO define los valores contexto→variable (esos los dictamina kb-design-style-taxonomy); este arbol solo ordena las preguntas que llevan a ellos. Pensado para diseñadores junior. Cargada por `wf-design-intake` en modo guided.
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Design Style Decision Tree

Eres el guia que ayuda a una persona sin experiencia a cerrar las decisiones del brief. **No redefines los criterios de direccion visual: los traduces a preguntas concretas y secuenciales.** La pregunta y su orden son de este arbol; el veredicto contexto→valor lo dictamina la taxonomia.

## Reparto de SSoT (leelo antes de usar el arbol)

Este arbol es la SSoT de **como se navega** hacia una direccion visual, no de **que valor** corresponde a cada contexto:

- **Que valor recomienda cada variable por contexto** (familia, density, depth, color_energy, motion_level, typography_mode) lo define `kb-design-style-taxonomy`. Este arbol referencia la regla concreta en cada nodo en vez de reescribir el mapeo.
- **`clarity_vs_brand`** no es una variable de la taxonomia: su SSoT (valores y heuristica contexto→valor) vive en `kb-design-brief`.
- **`voice_tone`** no es una variable de la taxonomia: su SSoT vive en `kb-design-voice`.
- Lo que es **exclusivamente de este arbol**: la secuencia ordenada de preguntas, las ramas de deteccion de conflicto (P1a/P2a/P3a, Q4), los fallbacks de guia junior (`[REQUIERE_REVISION_SENIOR]`, default conservador) y la integracion con `wf-design-intake`.

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

El mapeo contexto-de-producto → familia lo define `kb-design-style-taxonomy` Regla 4. Este arbol solo ordena las preguntas para llegar a el: cada pregunta aisla un contexto y, cuando se confirma, la familia resultante es la que esa Regla 4 asigna a ese contexto. Las ramas `Pna` son deteccion de conflicto propias del arbol.

Preguntas, en orden (la familia de cada rama "Si" es la que taxonomy Regla 4 asigna al contexto de la pregunta):

**P1: ¿Es B2B / herramienta de trabajo / backoffice / dashboard / fintech operativa?**
- Si → familia segun taxonomy Regla 4 para ese contexto. Verificar P1a.
  - **P1a**: ¿Hay capas, paneles, mapas o jerarquia espacial fuerte? → marcar la familia de jerarquia espacial (taxonomy Regla 4) como secundaria.
- No → P2.

**P2: ¿El producto opera en salud, bienestar, mindfulness, self-service de confianza o servicios financieros que requieren transmitir calma?**
- Si → familia segun taxonomy Regla 4 para ese contexto. Verificar P2a.
  - **P2a**: ¿La marca exige alto contraste cromatico o expresividad? → marcar conflicto y considerar la familia de engagement emocional (taxonomy Regla 4) con `clarity-first`.
- No → P3.

**P3: ¿Es consumer / lifestyle / fitness / social / entertainment con necesidad de diferenciacion emocional?**
- Si → familia segun taxonomy Regla 4 para ese contexto. Verificar P3a.
  - **P3a**: ¿El producto maneja datos numericos densos o transacciones criticas? → marcar conflicto y considerar la familia de tarea/claridad (taxonomy Regla 4) con `brand-forward` adjectives.
- No → P4.

**P4: ¿Es media / lectura / contenido curado / luxury / experiencia aspiracional?**
- Si → familia segun taxonomy Regla 4 para ese contexto.
- No → P5.

**P5: ¿La interfaz se apoya fuertemente en jerarquia espacial, overlays, paneles, mapas o colecciones multi-capa?**
- Si → familia segun taxonomy Regla 4 para ese contexto.
- No → P6.

**P6: Ninguna familia encaja claramente.**
- Si el junior llega aqui, **no recomendar `custom` automaticamente** (las condiciones de `custom` las fija taxonomy Regla 12). Volver atras y preguntar por el actor y la tarea dominante, no por la marca.
- Si tras dos vueltas no encaja, marcar `[REQUIERE_REVISION_SENIOR]` y proponer como default conservador la familia de tarea/claridad (taxonomy Regla 4).

## Regla 3: Decision tree para clarity_vs_brand

`clarity_vs_brand` no es una variable de la taxonomia. Sus valores (`clarity-first` / `balanced` / `brand-forward`) y la heuristica contexto→valor son SSoT de `kb-design-brief`. Este arbol solo ordena las preguntas que llevan a ese valor; el veredicto de cada rama es el que `kb-design-brief` asigna al contexto de la pregunta.

Preguntas, en orden:

**Q1: ¿El producto se rige por normativa (financiero, salud, seguros, gobierno, accesibilidad obligatoria)?**
- Si → valor segun `kb-design-brief` para producto regulado.
- No → Q2.

**Q2: ¿El usuario usa el producto como herramienta de trabajo intensa varias horas al dia?**
- Si → valor segun `kb-design-brief` para producto operativo (la marca no debe entorpecer la tarea).
- No → Q3.

**Q3: ¿La diferenciacion de marca es una necesidad comercial explicita (segmento muy competido, marca como ventaja)?**
- Si → valor segun `kb-design-brief` para consumer con diferenciacion.
- No → valor por defecto segun `kb-design-brief`.

**Q4 (rama de conflicto, propia del arbol): Si Q3=si y el producto es B2B o regulado → marcar conflicto, recomendar el valor intermedio de `kb-design-brief` y documentar el tradeoff en el brief.**

## Regla 4: Decision tree para density

El valor de `density` por contexto lo define `kb-design-style-taxonomy` Regla 8 (escala + disciplina) y las tablas por familia de su `references/style-families.md`. Este arbol solo ordena las preguntas para llegar a el:

1. Pregunta por la carga de datos por pantalla y el tipo de producto (B2B/dashboard vs consumer vs editorial/inmersivo).
2. Una vez fijado el contexto y la `style_family`, el valor de `density` es el que taxonomy Regla 8 / `style-families.md` asigna a esa familia.
3. Si el usuario duda dentro del rango valido de la familia, prefiere el valor mas conservador del rango.

## Regla 5: Decision tree para depth

El valor de `depth` por familia lo define `kb-design-style-taxonomy` Regla 8 y las tablas de `references/style-families.md`. Este arbol solo pregunta para fijar el contexto:

1. Pregunta si la interfaz se apoya en jerarquia espacial, overlays, paneles o colecciones multi-capa.
2. El valor de `depth` resultante es el que taxonomy asigna a la familia ya elegida (P5 de la Regla 2 captura el caso de jerarquia espacial fuerte).
3. Si el producto es flat-design intencional, pregunta para confirmarlo y aplica el valor `flat` de la escala de taxonomy Regla 8, con nota en `## Elevation & Depth`.

## Regla 6: Decision tree para color_energy

El valor de `color_energy` por contexto lo define `kb-design-style-taxonomy` Regla 10 (incluida la excepcion de dominios de calma) y las tablas por familia de `references/style-families.md`. Este arbol solo ordena las preguntas:

1. Pregunta por `clarity_vs_brand` (ya cerrado en Regla 3) y el dominio del producto.
2. El valor de `color_energy` resultante es el que taxonomy Regla 10 asigna a ese contexto y a la familia elegida.

## Regla 7: Decision tree para motion_level

El valor de `motion_level` por contexto lo define `kb-design-style-taxonomy` Regla 8 (`medium` como maximo por defecto; reducir motion ante necesidad de confianza/precision/velocidad) y las tablas de `references/style-families.md`. Este arbol solo pregunta:

1. Pregunta por la intensidad de uso (regulado / B2B intensivo vs consumer vs onboarding gamificado).
2. El valor resultante es el que taxonomy asigna al contexto y la familia.
3. `motion_level: none` solo si el dominio lo exige (epilepsia, terminales medicas, etc.) — caso recogido en la escala de taxonomy Regla 8.

## Regla 8: Decision tree para typography_mode

El valor de `typography_mode` lo define `kb-design-style-taxonomy` Regla 9 (tipografia por rol funcional) y las tablas por familia de `references/style-families.md`. Este arbol solo deriva desde la `style_family` ya elegida:

1. Una vez fijada la familia, el `typography_mode` es el que taxonomy Regla 9 / `style-families.md` asigna a esa familia.
2. Override valido si la marca aporta una fuente propia (dentro de los valores validos de taxonomy Regla 9).

## Regla 9: Decision tree para voice_tone

`voice_tone` no es una variable de la taxonomia: su SSoT es `kb-design-voice`. Este arbol solo ofrece una derivacion rapida de partida a partir de `style_family` + `clarity_vs_brand` para que un junior no llegue al brief con la voz en blanco; el dictamen final de la voz (ejes, microcopy, consistencia) lo gobierna `kb-design-voice`, y si el `voice_tone` declarado contradice al `clarity_vs_brand`, manda el brief (regla de `kb-design-voice`).

Derivacion rapida de partida (ajustable contra `kb-design-voice`):

- familia de tarea/claridad + `clarity-first` → neutral + tecnico/mixto + neutro + serio.
- familia de calma + `balanced` → cercano + accesible + humano + medido.
- familia de engagement + `brand-forward` → cercano + accesible + calido + medido/ludico.
- familia editorial → neutral + mixto + humano + medido.
- familia de jerarquia espacial → neutral + mixto + neutro + medido.

El usuario puede aceptar el default o ajustar uno o dos ejes con justificacion, validando contra `kb-design-voice`.

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
2. Marca cada variable con `source: inferred` (las variables operativas que el brief cierra son SSoT de `kb-design-brief` Regla 5).
3. Si encuentra conflicto P1a/P2a/P3a/Q4, prefiere la opcion conservadora y documenta razon.

## Regla 11: Anti-patrones del arbol

Anti-patrones propios de la **navegacion** (lo que este arbol prohibe como guia):

- Saltar a la respuesta sin recorrer las preguntas (el arbol enseña a decidir, no solo decide).
- Decidir `custom` sin haber agotado P1-P5 (las condiciones de `custom` las fija taxonomy Regla 12).
- Usar el arbol para forzar al usuario; siempre debe poder anular una respuesta con motivo.

El catalogo de **combinaciones de valores bloqueadas** (p. ej. `clarity-first` + `color_energy: high`, `motion_level: medium` sin justificacion en producto operativo, alta densidad en familia de calma) NO se redeclara aqui: son criterio normativo de `kb-design-style-taxonomy` (coherencia familia↔campos, Reglas 3 y 8) y de `kb-design-brief` (combinaciones invalidas del brief). El arbol, al detectar una de esas combinaciones, marca conflicto y remite a esas reglas en vez de definir la suya.
