---
name: kb-spec-characterization
description: "Reglas para specs de caracterización brownfield: evidencia obligatoria por CA, marcador [INFERIDO], qué no especular y degradación sin tests."
---

# Specs de caracterización (brownfield)

Un spec de caracterización describe **lo que el sistema hace hoy, verificado contra el código** — no lo que debería hacer ni la intención de negocio. Es la entrada alternativa al pipeline cuando no existe PRD: el código es la única fuente de verdad disponible.

## Regla de oro

**Un CA sin evidencia no existe.** Cada CA de un spec de caracterización lleva un campo `Evidencia:` con un puntero verificable. Si no puedes señalar dónde el código produce ese comportamiento, no lo escribas como CA — o márcalo `[INFERIDO]`.

## Jerarquía de evidencia (de más a menos fuerte)

1. **Test existente que pasa** — `Evidencia: test <path::nombre_test>`
2. **Código leído con ruta exacta** — `Evidencia: <archivo:línea-línea>` (la lógica es legible y directa)
3. **Configuración, migración o esquema** — `Evidencia: <archivo>` (constata estructura, no flujo)
4. **`[INFERIDO]`** — comportamiento deducido (convención del framework, código indirecto, reflexión, magia del ORM) pero no observado directamente. Formato:

```markdown
### CA-005 [INFERIDO]
GIVEN ... WHEN ... THEN ...
- **Evidencia:** parcial — <qué se vio y qué se deduce>
- **Confirmación pendiente:** <qué habría que ejecutar/preguntar para verificarlo>
```

## `[INFERIDO]` bloquea como `[INCOMPLETO]`

Los gates del pipeline (gate de plan, sellador) tratan `[INFERIDO]` igual que `[INCOMPLETO]`: un plan no puede construirse sobre comportamiento no confirmado. La vía de salida es `wf-spec-gap-resolve`: el humano confirma o corrige cada inferido y el marcador desaparece (la evidencia pasa a ser `confirmado por <quién> el <fecha>`).

## Header obligatorio

```markdown
> **Origen:** characterization
> **PRD origen:** N/A (brownfield)
> **Evidencia base:** commit <SHA corto> (<fecha>)
> **Status sync:** in_sync
```

`Evidencia base` ancla el spec en el tiempo: las afirmaciones eran verdad en ese commit. Si el código avanza mucho, el spec puede estar desactualizado — eso es deriva, no error del spec.

## Lo que NUNCA hace un spec de caracterización

| Prohibido | Por qué |
|---|---|
| Inventar la intención ("para que el usuario pueda...") | La intención no está en el código; si se conoce, viene de un humano y se marca como aportación |
| Convertir un comportamiento extraño en "lo deseado" | Characterization documenta lo que HAY. Si parece un bug, se registra el comportamiento actual + nota `[SOSPECHA_BUG]` — cambiarlo es decisión de producto (`wf-bug` / `wf-spec-delta`) |
| Especular sobre código muerto o rutas inalcanzables | Si no hay forma de llegar, no es comportamiento observable |
| Completar huecos "porque es lo estándar" | Lo estándar sin evidencia es `[INFERIDO]`, no un CA limpio |
| Derivar HUs de features que el código no implementa | El alcance del spec es el código, no el deseo |

## `[SOSPECHA_BUG]`

Nota informativa (no bloquea): el comportamiento documentado parece defectuoso. El CA describe igualmente lo que el código hace, y la nota lo deriva: si el comportamiento actual es el correcto → quitar la nota; si debe cambiar → `wf-spec-delta` (cambio de comportamiento esperado) o `wf-bug` si ya existe un CA que lo contradiga.

## Degradación sin tests

Si el proyecto no tiene tests (legacy real), la evidencia máxima disponible es lectura de código (nivel 2). En ese caso:

- El spec lo declara en el header: `> **Cobertura de evidencia:** sin tests — evidencia por lectura de código`
- Recomienda characterization tests para los CAs de mayor riesgo antes de refactorizar (los CAs ya escritos en GIVEN/WHEN/THEN son la semilla directa de esos tests)
- No bajes el listón de evidencia: sin tests, MÁS lecturas con ruta exacta, no menos

## Relación con el resto del pipeline

- El spec de caracterización fluye a Design/Plan/Tasks como cualquier spec (mismos gates).
- "El sistema hace X, ahora quiero Y" = `wf-spec-delta` sobre el spec de caracterización — el delta separa limpio el comportamiento actual del cambio pedido.
- La HU de caracterización usa actor real si es identificable en el código (roles, permisos); si no, `Actor: usuario del sistema` — nunca personas inventadas.
