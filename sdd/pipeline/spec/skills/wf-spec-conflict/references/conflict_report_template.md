# Conflict Report: [Nombre del proyecto]

> **Generado por**: sdd-spec-auditor
> **Fecha**: [YYYY-MM-DD]
> **Specs analizados**: [N] features
> **Features**: [lista de feature IDs y nombres]
> **Conjunto comparado**: [F-001 nombre, F-003 nombre, … — TODOS los specs que entraron en la
> comparación, el objetivo incluido. Si excluiste alguno por `Estado: RETIRADO`, nómbralo aquí
> como excluido.] Este informe vale para **este** conjunto: si después aparece un spec nuevo,
> queda estancado hasta que se rehaga.

---

## Estado general

> **[SIN_CONFLICTOS | CONFLICTOS_DETECTADOS]** ([modo feature: F-00X contra los otros [N-1] specs: F-00Y, F-00Z] | [modo consolidado: entre los [N] specs comparados: F-00Y, F-00Z])
>
> Resumen en 1-2 frases. Si hay conflictos, indicar cuántos son de severidad ALTA y cuántos MEDIA.
>
> [Solo en modo feature, el del fan-out:] Visto desde [F-00X]. Si otro auditor levanta un choque
> que incluye esta feature, lo arbitra el informe de readiness, y su veredicto manda sobre este.

<!-- En modo feature solo se comparan los pares que incluyen el spec objetivo (D-096): el resumen
     no se pronuncia sobre pares entre otros specs, ni para decir que están limpios. -->
<!-- El token va PRIMERO y literal — lo parsea la medición de readiness. El conjunto va detrás,
     entre paréntesis (D-093): un `SIN_CONFLICTOS` a secas se lee como "esta feature no choca con
     nada", y lo que dice de verdad es "no choca con los N specs que había cuando se escribió". -->

---

## Resumen de conflictos

<!-- Si SIN_CONFLICTOS: "No se detectaron conflictos entre los [N] specs analizados." -->
<!-- Si SIN_CONFLICTOS: indicar explícitamente "Conflictos ALTA: 0 | Conflictos MEDIA: 0". -->

| ID | Tipo | Severidad | Features involucradas |
|----|------|:---------:|-----------------------|
| CF-F001-01 | HU duplicada | ALTA | feature-a, feature-b |
| CF-F001-02 | CA contradictorio | ALTA | feature-b, feature-c |
| CF-F001-03 | Scope overlap | MEDIA | feature-a, feature-c |

<!-- El ID lleva delante el F-00X del spec auditado (D-090): en el fan-out hay un auditor por
     spec y ninguno ve lo que numeran los demás. En modo consolidado (un solo informe de todo
     el directorio) no hay con quién colisionar: ahí es CF-01, CF-02, … -->

---

## Detalle de conflictos

<!-- Repetir este bloque por cada conflicto detectado -->

### [CF-F001-01] [Tipo de conflicto] — Severidad: [ALTA | MEDIA]

**Features involucradas**: `[feature-a]`, `[feature-b]`

**Descripción**: [explicación del conflicto en lenguaje natural]

**En `[feature-a]`**:
> "[cita exacta de la HU, CA, Journey o regla en conflicto — con su ID]"

**En `[feature-b]`**:
> "[cita exacta de la sección en conflicto — con su ID]"

**Por qué es un conflicto**: [explicación específica de la incompatibilidad. Si citas la regla
que sostiene tu veredicto, cítala por lo que dice —"el mismo modelo con comportamientos distintos
en dos CAs de features diferentes"—, nunca por el nombre de la kb que la define (D-091).]

**Sugerencia de resolución**: [recomendación concreta — ej: "Considerar que HU-003 de feature-a es la definición canónica y eliminar la HU-007 de feature-b", o "Clarificar con el cliente qué feature es la responsable de X"]

---

## Inventario de comparaciones realizadas

> Esta sección garantiza trazabilidad de qué se comparó contra qué.

| Check | Features comparadas | Conflictos encontrados |
|-------|---------------------|:---------------------:|
| HUs duplicadas | Todos los pares | N |
| CAs contradictorios | Todos los pares | N |
| Scope overlap | Todos los pares | N |
| Shared models inconsistentes | Todos los specs | N |
| Fuera de alcance contradictorio | Todos los pares | N |

---

## Próximos pasos

<!-- Si SIN_CONFLICTOS -->
> No hay choques entre estos specs. Eso no los hace planificables por sí solo (D-077): el gate de
> planificación exige además el spec **validado**, y uno recién generado nace en borrador.

<!-- Si CONFLICTOS_DETECTADOS -->
1. Revisar cada conflicto de severidad **ALTA** — deben resolverse antes de planificar las features afectadas
2. Los conflictos de severidad **MEDIA** pueden documentarse como decisiones de diseño y resolverse en la fase de implementación
3. Para cada conflicto resuelto: decidir **qué feature manda** y pedir que se aplique el cambio
   sobre el spec que toque, que reabre su validación; después, una nueva revisión de conflictos
   para verificar que se eliminó. **No editar los specs a mano** (D-082): una edición fuera de las
   vías de evolución conserva el sello `VALIDADO` y el gate de planificación la deja pasar.
