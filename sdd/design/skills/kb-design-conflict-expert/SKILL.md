---
name: kb-design-conflict-expert
description: Base de conocimiento para detectar conflictos visuales y de UX entre varias features dentro de un mismo producto. Define que cuenta como conflicto (componente con doble comportamiento, navegacion incoherente, tokens contradichos, jerarquia visual rota, accesibilidad inconsistente) y como reportarlo sin redefinir el contrato visual.
argument-hint: "(cargada automaticamente por el agente design-architect y por futuros workflows de conflicto)"
effort: medium
allowed-tools: [Read]
user-invocable: false
---

# Design Conflict Expert

Eres la fuente de verdad para identificar incoherencias visuales o de interaccion entre features dentro de un mismo producto. No redefines `DESIGN.md` ni reglas de `kb-design-expert`: solo declaras que constituye conflicto y como reportarlo.

## Regla 1: Componentes con comportamiento divergente entre features son conflicto

Si dos `*_views.md` distintos describen el mismo componente (mismo nombre, misma posicion en la jerarquia visual) pero con comportamiento distinto, hay conflicto.

Ejemplos:
- `PrimaryButton` con confirmacion modal en una feature y sin confirmacion en otra.
- `BackButton` que conserva estado en una feature y descarta cambios en otra.
- `Toast` con timeout de 3s en una vista y 8s en otra.

Severidad: `ALTA` si el componente es global (header, navegacion principal, formularios), `MEDIA` si es local.

## Regla 2: Navegacion incoherente entre flows es conflicto

Los `*_flows.md` de features distintas deben respetar el mismo modelo navegacional. Constituyen conflicto:
- Distinto patron de `back` (gesture vs boton, descarte vs preservacion).
- Distinto patron de `dismiss` en modales (X, swipe down, tap outside).
- Distinto patron de `save` (autosave vs guardado explicito) sin justificacion en el spec.
- Salidas de flujo que conducen a pantallas distintas para el mismo CA.

Severidad: `ALTA` para flows de la misma actor + journey similar; `MEDIA` para journeys diferentes.

## Regla 3: Tokens visuales contradichos entre `*_views.md` y `DESIGN.md` son conflicto

Cualquier valor visual concreto en `*_views.md` (color, radio, spacing, tipografia) que no exista en `DESIGN.md` o que contradiga su valor es conflicto.

`*_views.md` debe **referenciar** tokens, no introducir literales nuevos. Si una feature necesita un token que `DESIGN.md` no tiene, debe pasar por `wf-design-delta` para extenderlo.

Severidad: `CRITICA` si rompe coherencia visual; `ALTA` si introduce decisiones no canalizadas via delta.

## Regla 4: Jerarquia visual rota entre features es conflicto

Si dos pantallas comparten contexto (mismo journey o mismo nivel navegacional) y compiten por foco visual del usuario:
- Dos CTAs primarios compitiendo en la misma vista sin jerarquia clara.
- Mismo color para acciones de distinta severidad (confirmacion y destruccion en el mismo tono).
- Densidad informacional contradictoria entre vistas hermanas (una `low`, otra `high` sin justificacion).

Severidad: `MEDIA` salvo que afecte a acciones destructivas, en cuyo caso `ALTA`.

## Regla 5: Accesibilidad inconsistente entre features es conflicto

Las decisiones a11y declaradas en `DESIGN.md` (Regla 6 de `kb-a11y-expert`) deben aplicarse de forma homogenea. Constituye conflicto:
- Una feature respeta `accessibility_target: AA` y otra introduce contraste fuera de norma.
- Touch targets distintos entre features para acciones equivalentes.
- Anuncios live ausentes en una feature pero presentes en otra para el mismo tipo de evento.

Severidad: `CRITICA` si el `accessibility_target` del brief no se cumple; `ALTA` en el resto.

## Regla 6: Formato de reporte de conflicto

Todo conflicto detectado debe declararse con:

```
[CONFLICTO-DESIGN-XX]
- Tipo: <componente | navegacion | token | jerarquia | accesibilidad>
- Severidad: BAJA | MEDIA | ALTA | CRITICA
- Features afectadas: <feature_A>, <feature_B>
- Descripcion: <que choca y donde>
- Evidencia: <referencias concretas a lineas o secciones de los archivos>
- Resolucion propuesta: <opcion A vs opcion B, o `requiere decision`>
```

No reescribas los archivos involucrados. La resolucion se canaliza siempre via `wf-design-delta` o regeneracion explicita.

## Regla 7: Que NO es conflicto

No reportes como conflicto:
- Diferencias de copy entre features (no es competencia de `design`).
- Variaciones legitimas amparadas por el spec (ej. una feature B2B y otra B2C dentro del mismo producto pueden divergir si el brief lo permite).
- Decisiones documentadas en `## Changelog` del `DESIGN.md` con justificacion.
- Componentes con el mismo nombre pero distinto contexto explicito (`PrimaryButton/onboarding` vs `PrimaryButton/checkout`).

Si dudas, declara `[POSIBLE-CONFLICTO-DESIGN-XX]` y deja decidir al usuario en lugar de inflar el reporte con falsos positivos.
