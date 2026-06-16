# Mapeo normativo de señales visuales por familia

Referencia de lookup para las señales visuales concretas de cada familia cerrada. Usar junto con las reglas de selección y criterios de `SKILL.md`. Si los campos aquí contradicen la familia elegida, la dirección visual está mal definida.

---

## productive-minimal

| Campo | Valores válidos |
|---|---|
| `density` | `medium` o `high` |
| `depth` | `flat` o `low` |
| `typography_mode` | `utilitarian` |
| `color_energy` | `low` o `medium` |
| `motion_level` | `low` |
| `iconography_base` | outline (Lucide / Phosphor), stroke 1.5, grid 20-24 |
| `motion_roles_activos` | feedback + transition discretos |

**NO usar cuando:** el producto necesita expresividad de marca como ventaja comercial; es entertainment/lifestyle; los datos son escasos y el contenido es narrativo.

---

## calm-minimal

| Campo | Valores válidos |
|---|---|
| `density` | `low` o `medium` |
| `depth` | `flat` o `low` |
| `typography_mode` | `neutral-humanist` |
| `color_energy` | `low` |
| `motion_level` | `low` o `medium` |
| `iconography_base` | outline ligero (Phosphor light), stroke 1.5, grid 24 |
| `motion_roles_activos` | feedback + transition + attention sutil |

**NO usar cuando:** el producto requiere alta densidad informacional; el dominio es transaccional intenso (trading, e-commerce de alta velocidad); la marca demanda energía y urgencia.

---

## expressive-modern

| Campo | Valores válidos |
|---|---|
| `density` | `medium` |
| `depth` | `low` o `medium` |
| `typography_mode` | `brand-forward` |
| `color_energy` | `medium` o `high` |
| `motion_level` | `medium` |
| `iconography_base` | fill o duo-tone (Phosphor fill, Solar), grid 24 |
| `motion_roles_activos` | feedback + transition + attention + expression en momentos clave |

**NO usar cuando:** el producto es regulado o financiero serio; el actor pasa horas al día operando; la legibilidad de datos numéricos es crítica.

---

## editorial-premium

| Campo | Valores válidos |
|---|---|
| `density` | `low` o `medium` |
| `depth` | `flat` o `low` |
| `typography_mode` | `editorial` |
| `color_energy` | `low` o `medium` |
| `motion_level` | `low` o `medium` |
| `iconography_base` | outline fino editorial (Tabler / custom), stroke 1, grid 24 |
| `motion_roles_activos` | transition con duraciones `medium`/`slow` tipo cinematográfico |

**NO usar cuando:** la densidad de información es media-alta; el producto es transaccional; el actor entra y sale rápido sin tiempo de inmersión.

---

## depth-material

| Campo | Valores válidos |
|---|---|
| `density` | `medium` |
| `depth` | `medium` o `high` |
| `typography_mode` | `neutral-humanist` o `utilitarian` |
| `color_energy` | `low` o `medium` |
| `motion_level` | `medium` |
| `iconography_base` | Material Symbols rounded/filled, grid 24 |
| `motion_roles_activos` | orientation y transition refuerzan la jerarquía espacial |

**NO usar cuando:** la interfaz es simple y lineal sin jerarquía espacial real; el producto no tiene paneles, mapas, overlays ni colecciones multi-capa; se aplica solo "porque queda moderno".

---

## Reglas de combinación

- Una dirección visual puede combinar una familia principal con una secundaria, pero nunca más de dos.
- Si hay dos, una debe declararse dominante (`style_family`) y la otra complementaria (`secondary_family`).
- Si los campos de `secondary_family` contradicen los de `style_family` en dimensiones críticas (density, depth), la combinación no es coherente.
- Si dudas, vuelve a la heurística de contexto (Regla 4 del SKILL.md) y al árbol de `kb-design-style-decision-tree`.
