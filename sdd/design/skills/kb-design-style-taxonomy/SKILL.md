---
name: kb-design-style-taxonomy
description: Base de conocimiento para clasificar estilos visuales de producto digital de forma operativa. Define familias de estilo, senales visuales, criterios de seleccion por contexto de producto y anti-patrones para que DESIGN.md no quede en adjetivos genericos. Activa cuando un agente necesite decidir o revisar la direccion visual de una app, derivar Visual Personality, elegir densidad, profundidad, tipografia, color y motion, o evitar resultados genericos tipo "moderno" o "minimalista" sin concretar.
argument-hint: "(cargada automaticamente por agentes de design)"
effort: medium
allowed-tools: [Read]
user-invocable: false
---

# Design Style Taxonomy

Eres la fuente de verdad para convertir una intencion visual vaga en una direccion de producto concreta, consistente y reusable dentro de `DESIGN.md`.

## Regla 1: No uses etiquetas vagas como fuente normativa

Etiquetas como `moderno`, `minimalista`, `premium`, `realista` o `bonito` no son suficientes como decision de diseno porque no fijan comportamiento visual.

Toda direccion visual debe expresarse como una combinacion explicita de:
- `style_family`
- `density`
- `depth`
- `typography_mode`
- `color_energy`
- `motion_level`
- `anti_patterns`

Los adjetivos de marca siguen siendo utiles, pero solo como capa semantica. La capa operativa la gobiernan los campos anteriores.

## Regla 2: Las familias de estilo validas son cerradas

Para producto digital mobile o app-like, usa una de estas familias como base principal:

- `productive-minimal`: foco en tarea, claridad, alta eficiencia, ornamento bajo
- `calm-minimal`: claridad serena, ritmo aireado, confianza, friccion visual baja
- `expressive-modern`: energia visual, identidad de marca visible, contrastes y formas mas marcadas
- `editorial-premium`: tipografia y composicion como protagonistas, ritmo visual sofisticado
- `depth-material`: jerarquia apoyada por superficies, elevacion, capas y materiales

Una direccion visual puede combinar una familia principal con una secundaria, pero nunca mezclar mas de dos. Si hay dos, una debe declararse dominante.

## Regla 3: Cada familia implica senales visuales concretas

Mapeo normativo por familia:

- `productive-minimal`
  - densidad: media o alta
  - depth: flat o low
  - typography_mode: utilitarian
  - color_energy: low o medium
  - motion_level: low
  - iconography_base: outline (Lucide / Phosphor), stroke 1.5, grid 20-24
  - motion_roles_activos: feedback + transition discretos
- `calm-minimal`
  - densidad: baja o media
  - depth: flat o low
  - typography_mode: neutral-humanist
  - color_energy: low
  - motion_level: low o medium
  - iconography_base: outline ligero (Phosphor light), stroke 1.5, grid 24
  - motion_roles_activos: feedback + transition + attention sutil
- `expressive-modern`
  - densidad: media
  - depth: low o medium
  - typography_mode: brand-forward
  - color_energy: medium o high
  - motion_level: medium
  - iconography_base: fill o duo-tone (Phosphor fill, Solar), grid 24
  - motion_roles_activos: feedback + transition + attention + expression en momentos clave
- `editorial-premium`
  - densidad: baja o media
  - depth: flat o low
  - typography_mode: editorial
  - color_energy: low o medium
  - motion_level: low o medium
  - iconography_base: outline fino editorial (Tabler / custom), stroke 1, grid 24
  - motion_roles_activos: transition con duraciones `medium`/`slow` tipo cinematografico
- `depth-material`
  - densidad: media
  - depth: medium o high
  - typography_mode: neutral-humanist o utilitarian
  - color_energy: low o medium
  - motion_level: medium
  - iconography_base: Material Symbols rounded/filled, grid 24
  - motion_roles_activos: orientation y transition refuerzan la jerarquia espacial

Las pautas de motion concretas (durations, easing por rol) viven en `kb-design-motion-expert`. Las pautas de iconografia (stroke, fill rule, tamanos por rol) viven en `kb-design-iconography-expert`.

**Cuando NO usar cada familia (contraejemplos pedagogicos):**

- `productive-minimal` **NO** se usa cuando: el producto necesita expresividad de marca como ventaja comercial; es entertainment/lifestyle; los datos son escasos y el contenido es narrativo.
- `calm-minimal` **NO** se usa cuando: el producto requiere alta densidad informacional; el dominio es transaccional intenso (trading, e-commerce de alta velocidad); la marca demanda energia y urgencia.
- `expressive-modern` **NO** se usa cuando: el producto es regulado o financiero serio; el actor pasa horas al dia operando; la legibilidad de datos numericos es critica.
- `editorial-premium` **NO** se usa cuando: la densidad de informacion es media-alta; el producto es transaccional; el actor entra y sale rapido sin tiempo de inmersion.
- `depth-material` **NO** se usa cuando: la interfaz es simple y lineal sin jerarquia espacial real; el producto no tiene paneles, mapas, overlays ni colecciones multi-capa; se aplica solo "porque queda moderno".

Si dudas, vuelve a la heuristica de Regla 4 (contexto > marca) y al arbol de decision de `kb-design-style-decision-tree`.

Si el resto de campos contradice la familia elegida, la direccion visual esta mal definida.

## Regla 4: Selecciona la familia por contexto de producto, no por gusto abstracto

Heuristica principal de seleccion:

- producto B2B, operaciones, backoffice, fintech utilitaria, dashboards -> `productive-minimal`
- salud, bienestar, self-service, productos de confianza o calma -> `calm-minimal`
- consumer, lifestyle, fitness, social, engagement emocional -> `expressive-modern`
- media, lectura, contenido curado, luxury, experiencia aspiracional -> `editorial-premium`
- productos con mucha jerarquia espacial, multicapas, overlays, paneles, mapas o colecciones -> `depth-material`

Si el producto tiene una alta carga numerica o formularios frecuentes, prioriza claridad y legibilidad sobre expresividad. Si la diferenciacion de marca es una necesidad comercial explicita, permite mas expresividad sin sacrificar trazabilidad funcional.

## Regla 5: "Realista" no es una familia por defecto en producto digital

No uses `realista` como categoria base de app UI salvo que el producto exija simular materiales o objetos del mundo fisico por razones claras de dominio.

En la mayoria de productos, lo que parece "realista" se resuelve realmente como una decision de:
- `depth`
- tratamiento de superficies
- sombras
- blur o translucencia
- ilustracion o imagery

Si un stakeholder pide "realista", traduce esa peticion a senales concretas y reubicala dentro de una de las familias validas.

## Regla 6: Visual Personality debe declarar el perfil estructurado completo

Todo `DESIGN.md` debe incluir, dentro del frontmatter, un bloque `visual_personality` con esta estructura minima:

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
    - clear: jerarquia evidente y labels directos
    - efficient: vistas compactas con foco en tarea principal
  anti_patterns:
    - generic-saas
    - decorative-gradients-without-meaning
```

`secondary_family` es opcional. El resto de campos son obligatorios.

→ Templates: `references/style_profile_examples.md`

## Regla 7: Los anti-patrones son obligatorios

Toda direccion visual debe explicitar que se evita. Sin eso, el sistema cae en promedios genericos.

Anti-patrones recomendados:
- `generic-saas`
- `dribbblified-overdesigned`
- `pseudo-realistic`
- `playful-when-trust-is-required`
- `flat-without-hierarchy`
- `premium-but-illegible`
- `brand-saturated-at-the-cost-of-clarity`

Solo declara anti-patrones compatibles con el producto. No uses listas largas por inercia.

## Regla 8: Densidad, profundidad y motion se eligen con disciplina

Escalas normativas:

- `density`: `low`, `medium`, `high`
- `depth`: `flat`, `low`, `medium`, `high`
- `motion_level`: `none`, `low`, `medium`

Reglas:
- `high` density exige jerarquia tipografica y espaciado extremadamente claros
- `high` depth solo es valida si mejora comprension de capas; nunca como maquillaje
- `medium` motion es el maximo por defecto para producto; mas alla de eso suele degradar claridad y a11y
- si el producto requiere confianza, precision o velocidad, reduce motion y saturacion antes que aumentar ambas

## Regla 9: La tipografia se decide por rol funcional

Valores validos de `typography_mode`:
- `utilitarian`: lectura rapida, tablas, cifras, labels compactos
- `neutral-humanist`: equilibrio entre calidez y claridad
- `brand-forward`: mas personalidad formal, pesos y formas con mas identidad
- `editorial`: composicion y ritmo tipografico como recurso principal

La seleccion depende del contenido dominante:
- cifras, estados, forms, listas -> `utilitarian`
- confianza, guidance, acompanamiento -> `neutral-humanist`
- marca consumer con diferenciacion visible -> `brand-forward`
- contenido, storytelling o aspiracional -> `editorial`

## Regla 10: El color se define por energia, no por moda

Valores validos de `color_energy`:
- `low`: paleta sobria, pocos acentos, foco en contenido
- `medium`: marca visible pero contenida
- `high`: acentos dominantes y contraste cromatico mas expresivo

`high` solo debe usarse si:
- la marca realmente necesita protagonismo visual
- la app no depende de lectura densa constante
- el contraste sigue siendo robusto en estados y accesibilidad

## Regla 11: Una familia no sustituye la investigacion de referencias

La taxonomia ayuda a decidir estructura visual, pero no reemplaza `Reference Apps`.

- La familia define el tipo de sistema visual.
- Las referencias reales afinan como se materializa esa familia en un sector concreto.

Si dos apps del mismo sector resuelven bien el mismo problema, extrae el patron compartido; no copies la estetica superficial.

## Regla 12: Familia custom solo con justificacion explicita

Si ninguna de las familias cerradas (`productive-minimal`, `calm-minimal`, `expressive-modern`, `editorial-premium`, `depth-material`) encaja con el producto, esta permitido usar `style_family: custom`. No es una via libre.

Una familia `custom` exige:

1. **Justificacion escrita** en `## Visual Personality` del `DESIGN.md`: dos parrafos minimo explicando por que ninguna familia cerrada encaja y que combinacion concreta de propiedades define la direccion visual.
2. **Perfil estructurado completo** (`density`, `depth`, `typography_mode`, `color_energy`, `motion_level`) usando solo escalas validas — `custom` no rompe las escalas, solo la familia.
3. **Anti-patrones reforzados**: minimo 4 anti-patrones explicitos (vs los 2-4 habituales), para evitar que `custom` regrese a "moderno generico".
4. **Reference Apps especialmente solidas**: minimo 4 apps de referencia con aspecto concreto, ya que no hay familia que ancle la decision.
5. **Confirmacion del usuario** si el modo del workflow no es `auto`: el agente debe declarar `custom` como propuesta y pedir confirmacion explicita.

Si una de estas condiciones falla, el agente debe declinar el uso de `custom` y volver a una familia cerrada con justificacion alternativa.

Anti-patron: usar `custom` para evitar el coste de elegir entre familias cerradas. Si el producto realmente cabe en una familia, fuerzala.
