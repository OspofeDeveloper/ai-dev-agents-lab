---
name: kb-design-motion-expert
description: Base de conocimiento operativa para motion y micro-interacciones en mobile. Define escalas de duracion, curvas de easing, motion roles, que se anima y que no, y catalogo de micro-interacciones por componente. Convierte `motion_level` del brief en decisiones concretas sin que el output sea generico.
argument-hint: "(cargada automaticamente por agentes y workflows de design)"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Design Motion Expert

Eres la fuente de verdad para las decisiones de motion del producto. No redefines reglas de `kb-design-expert` ni de la taxonomia visual: traduces el `motion_level` cerrado en el brief a tokens y patrones aplicables.

## Regla 1: Motion sirve a la comunicacion, nunca a la decoracion

Toda animacion debe responder a una de estas cinco funciones (roles):

- `feedback`: confirmar al usuario que su accion fue recibida (button press, toggle, ripple).
- `transition`: comunicar continuidad entre estados o pantallas (page transition, modal entry).
- `attention`: dirigir la mirada a un cambio importante (notification, error inline, badge update).
- `expression`: reforzar caracter de marca (splash, onboarding, celebracion).
- `orientation`: explicar relacion espacial entre elementos (drawer, accordion, master-detail).

Si una animacion no tiene rol claro, eliminarla. No anadas motion "porque queda bien".

## Regla 2: Escala de duraciones cerrada

Las duraciones deben elegirse de esta escala fija, no inventarse:

- `instant`: 0ms — sin animacion, solo cambio de estado.
- `fast`: 100-150ms — feedback inmediato (press, hover, focus).
- `base`: 200-250ms — transiciones estandar de UI (toggle, dropdown, fade).
- `medium`: 300-400ms — entradas y salidas de overlays (modal, sheet, drawer).
- `slow`: 500-700ms — transiciones contextuales mayores (page transition, hero).
- `extra-slow`: 800-1200ms — solo expression role (splash, milestone, celebration).

En productos `clarity-first` no se usa `extra-slow` salvo en expression aislada. En productos operativos no se usa `slow` salvo en page transitions.

## Regla 3: Catalogo de easing por rol

Cada rol tiene una curva preferida. No mezcles.

- `feedback`: ease-out (entra fuerte, sale suave) — la accion se siente rapida.
- `transition`: ease-in-out estandar (curva simetrica) — sensacion natural de continuidad.
- `attention`: ease-out con leve overshoot (spring sutil) — capta sin distraer.
- `expression`: spring o easing personalizado, mayor amplitud.
- `orientation`: ease-out para entrada, ease-in para salida.

Curvas concretas recomendadas:
- ease-out estandar: `cubic-bezier(0.0, 0.0, 0.2, 1)`
- ease-in-out estandar: `cubic-bezier(0.4, 0.0, 0.2, 1)`
- ease-in estandar: `cubic-bezier(0.4, 0.0, 1.0, 1)`
- spring sutil (web): `cubic-bezier(0.34, 1.56, 0.64, 1)` con duracion `base` o `medium`.

## Regla 4: Mapeo de `motion_level` del brief a politicas operativas

El `motion_level` del `DESIGN_BRIEF.md` cierra que motion roles estan permitidos y con que intensidad:

- `motion_level: none` — solo `feedback` con `instant` o `fast`. Sin transiciones ni expression. Reservado para productos extremadamente regulados o de uso intensivo prolongado.
- `motion_level: low` — `feedback` + `transition` con escalas `fast`/`base`. `attention` solo si es critica (error inline, notificacion). Sin expression salvo arranque (splash). Default seguro para B2B y productos operativos.
- `motion_level: medium` — `feedback` + `transition` + `attention` + `orientation` libres. `expression` permitido en momentos clave (onboarding, primer logro, milestone). Default para consumer y lifestyle.

No hay `motion_level: high` en este sistema: si el producto necesita motion expresiva intensa, debe justificarse en el brief con `motion_level: medium + expression-intensive` como nota.

## Regla 5: Lo que NUNCA se anima

Independientemente del `motion_level`, no animes:

- Texto largo entrando letra a letra (typewriter) salvo expression aislada.
- Scroll automatico sin trigger de usuario.
- Modales que tardan mas de `medium` en abrir.
- Inputs que rebotan al recibir focus.
- Iconos que rotan o vibran sin razon funcional.
- Loaders que sustituyen contenido durante mas de 1.5s sin skeleton.
- Elementos que entran simultaneamente desde 3+ direcciones.

Estas son anti-patrones de motion: producen sensacion amateur o ralentizan tareas reales.

## Regla 6: Motion debe respetar `prefers-reduced-motion`

Toda implementacion debe tener un fallback:

- Sustituir transitions por cross-fade de `fast`.
- Sustituir motion expressive por estado final directo.
- Mantener motion de `feedback` esencial (boton presionado) en duracion reducida.

En el `DESIGN.md` declara explicitamente la politica de reduced-motion en `## Motion & Micro-interactions`.

## Regla 7: Catalogo minimo de micro-interacciones por componente

Cada componente interactivo debe declarar al menos estas tres micro-interacciones:

- Estado de presion (`pressed`): duracion `fast`, ease-out, scale 0.97-0.98 o opacity 0.8.
- Cambio de estado (`toggle`/`select`): duracion `base`, ease-out, color/background transition.
- Aparicion/desaparicion (`mount`/`unmount`): duracion `base` o `medium` segun jerarquia.

Componentes que requieren motion extra:
- Modal/Sheet/Drawer: entrada `medium` ease-out, salida `base` ease-in.
- Toast/Notification: entrada `base` ease-out + auto-dismiss tras tiempo declarado.
- Accordion/Disclosure: `base` ease-in-out con height + opacity.
- Skeleton loader: shimmer cycle `1200-1500ms` linear.
- Pull-to-refresh: spring `medium` con threshold de activacion.

## Regla 8: Como se documenta motion en DESIGN.md

En el frontmatter YAML del `DESIGN.md`, declarar:

```yaml
motion:
  level: low | medium | none
  reduced_motion_policy: <descripcion breve>
  durations:
    fast: 120
    base: 220
    medium: 320
    slow: 500
  easing:
    feedback: "cubic-bezier(0.0, 0.0, 0.2, 1)"
    transition: "cubic-bezier(0.4, 0.0, 0.2, 1)"
    attention: "cubic-bezier(0.34, 1.56, 0.64, 1)"
```

En la seccion markdown `## Motion & Micro-interactions`:

- explicacion del rol del motion en este producto
- politica de `prefers-reduced-motion`
- catalogo de micro-interacciones por componente clave
- ejemplos textuales de transiciones entre pantallas (no codigo)

## Regla 9: Familias y motion por defecto

Como referencia base, cada familia visual sugiere un `motion_level`:

- `productive-minimal`: `motion_level: low` — feedback y transition discretos.
- `calm-minimal`: `motion_level: low` — ease-out alargado, duracion `base`.
- `expressive-modern`: `motion_level: medium` — attention y expression permitidos.
- `editorial-premium`: `motion_level: medium` — transiciones lentas (`medium`/`slow`) tipo cinematografico.
- `depth-material`: `motion_level: medium` — motion soporta jerarquia espacial.

Estas son sugerencias por defecto; el brief manda si difiere.
