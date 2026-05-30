---
name: wf-design-variant
description: "Permite el A/B testing visual de una feature. Genera dos o mas variantes de los _views.md (y/o _ui_prompt.md) compartiendo el mismo spec, con hipotesis y metrica esperada declaradas. Output: <feature>_variants.md con tabla comparativa."
when_to_use: "Activa en frases como 'quiero probar dos versiones del checkout', 'haz un A/B del onboarding', 'compara variantes de esta feature'."
argument-hint: "create <feature_spec.md> --variants <A,B,...> [--hypothesis <texto>] | compare <feature_variants.md>"
effort: medium
allowed-tools: [Read, Write, Agent]
context: fork
agent: design-architect
---

# design-variant — A/B testing visual

Tu rol es producir y comparar variantes paralelas de una feature compartiendo spec y `DESIGN.md`, para validar hipotesis visuales antes de comprometerse.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: `create` o `compare`.
- En modo `create`:
  - **Path del spec**: primer argumento tras el modo.
  - **`--variants`**: lista separada por comas con identificadores de variante (`A,B` minimo; opcional `C`, `D`).
  - **`--hypothesis`** opcional: descripcion de la hipotesis que se quiere validar.
- En modo `compare`:
  - **Path del `<feature>_variants.md`** existente.

Si no hay argumento valido, informa:
> "Uso:"
> - "`/wf-design-variant create <feature_spec.md> --variants A,B [--hypothesis 'texto']`"
> - "`/wf-design-variant compare <feature_variants.md>`"

## Paso 2: Modo `create`

### 2.1 Verificar precondiciones

1. Spec valido (Reglas estandar de SDD).
2. `DESIGN.md` existe.
3. `DESIGN_BRIEF.md` cerrado (salvo override `--no-brief`).
4. La feature debe tener Success Metrics declarados en el brief para que el A/B tenga sentido. Si no los hay, advertir:
   > "El `DESIGN_BRIEF.md` no declara `Success Metrics`. Sin metricas no se puede evaluar la variante ganadora. ¿Continuar igualmente? (y/n)"

### 2.2 Capturar hipotesis

Si `--hypothesis` no se paso, preguntar al usuario:
> "¿Cual es la hipotesis que quieres validar con estas variantes? (ej: 'una version con CTA mas prominente aumentara el task completion en checkout')"

La hipotesis debe ser:
- Especifica (que cambia en cada variante).
- Medible (con que metrica del brief se evalua).
- Acotada en alcance (vista, flujo, componente).

Si el usuario no proporciona hipotesis clara, deten:
> "Sin hipotesis especifica, el A/B es decoracion, no validacion. Define que esperas que cambie entre las variantes."

### 2.3 Generar variantes

Por cada variante (`A`, `B`, ...):

1. Pedir al usuario una descripcion corta de en que difiere de las demas (1-2 frases).
2. Delegar al agente con este prompt:
   ```text
   Modo: design-variant-generate
   Path del spec: <path>
   Path del DESIGN.md: <path>
   Path del brief: <path>
   Contenido spec: <...>
   Contenido DESIGN.md: <...>
   Contenido brief: <...>

   Variante: <X>
   Descripcion de esta variante: <texto del usuario>
   Hipotesis general del A/B: <hypothesis>

   INSTRUCCION: produce `<feature>_views.<X>.md`, `<feature>_flows.<X>.md` y `<feature>_ui_prompt.<X>.md` para esta variante. Las variantes comparten spec y DESIGN.md; solo difieren en como materializan la feature. Aplica las reglas estandar de wf-design-feature-prototype.

   Documenta en cada artefacto que es variante <X> y enlaza a la hipotesis.
   ```
3. Escribir los archivos resultantes.

### 2.4 Generar `<feature>_variants.md`

Documento maestro con esta estructura:

```markdown
---
spec: <path>
design: <path>
brief: <path>
variants: [A, B, ...]
hypothesis: "<texto>"
metric: "<metric clave del brief que evalua>"
status: pending_validation
created_at: <fecha>
---

# Variants — <feature name>

## Hipotesis

> <texto literal>

## Metrica clave

<que metric del brief se va a usar para decidir>

## Variantes

### Variante A
- **Descripcion**: <texto>
- **Archivos**:
  - `<feature>_views.A.md`
  - `<feature>_flows.A.md`
  - `<feature>_ui_prompt.A.md`
- **Diferencias clave respecto a B**: <bullets>

### Variante B
- **Descripcion**: <texto>
- **Archivos**: ...

## Plan de validacion

1. Implementar ambas variantes en codigo (lectura del `_ui_prompt.<X>.md` para Stitch o handoff a dev).
2. Definir el split (50/50, 70/30, otro).
3. Definir el periodo (X dias o N usuarios).
4. Definir criterio de decision (mejora >= Y% en metric).

## Resultados

Pendiente. Tras la validacion, actualizar este documento con:
- ganador
- delta de la metrica
- decision: aplicar ganador via `wf-design-delta apply` o iterar.
```

### 2.5 Informar al usuario

- archivos generados
- siguiente paso recomendado:
  > "Cuando el A/B termine y tengas resultados, ejecuta `/wf-design-variant compare <feature>_variants.md` y registra el ganador."

## Paso 3: Modo `compare`

### 3.1 Verificar

Leer `<feature>_variants.md`. Verificar que `status: pending_validation`.

### 3.2 Capturar resultados

Preguntar al usuario:
1. ¿Cual fue la metric de cada variante?
2. ¿Que variante gano? (o "empate", "no concluyente").
3. ¿Que aprendiste? (notas cualitativas relevantes).

### 3.3 Actualizar el documento

Anadir seccion `## Resultados`:

```markdown
## Resultados (validados el <fecha>)

| Variante | Metric | Delta vs control | Observaciones |
|---|---|---|---|
| A | XX% | baseline | <notas> |
| B | YY% | +Z% | <notas> |

**Ganador**: <X | empate | no concluyente>
**Decision**: <aplicar X via wf-design-delta | iterar | descartar A/B>

## Aprendizajes

- <bullet>
- <bullet>
```

Cambiar `status: pending_validation` a `status: validated`.

### 3.4 Sugerir siguiente paso

- Si hay ganador y se decide aplicar: sugerir `/wf-design-delta analyze` con los cambios de la variante ganadora.
- Si no hay ganador concluyente: documentar y dejar el control como esta.
- Si la conclusion es iterar, sugerir nuevo `wf-design-variant create` con variantes ajustadas.

## Regla operativa

- Las variantes comparten spec. No introducen funcionalidad nueva: si lo hacen, son features distintas, no variantes.
- Las variantes deben ser comparables (mismo journey, misma metric).
- Maximo 3-4 variantes simultaneas. Mas de 4 dispara complejidad estadistica del A/B.
- Tras validacion, el ganador se aplica al sistema; las perdedoras se descartan o se documentan como hipotesis cerrada.
