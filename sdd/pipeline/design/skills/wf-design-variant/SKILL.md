---
name: wf-design-variant
description: "Permite el A/B testing visual de una feature. Genera dos o mas variantes de los _views.md (y/o _ui_prompt.md) compartiendo el mismo spec, con hipotesis y metrica esperada declaradas. Output: <feature>_variants.md con tabla comparativa."
when_to_use: "Activa en frases como 'quiero probar dos versiones del checkout', 'haz un A/B del onboarding', 'compara variantes de esta feature'."
argument-hint: "create <feature_spec.md> --variants <A,B,...> [--hypothesis <texto>] | compare <feature_variants.md>"
effort: medium
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# design-variant — A/B testing visual

**Corres en el hilo principal.** Este workflow pregunta cuatro veces: la hipotesis del A/B, en que
difiere cada variante, y —en modo `compare`— que metrica dio cada una y que aprendiste. Nada de eso se
puede hacer desde un `context: fork` ([[D-002]]/[[D-045]]), y sin usuario el riesgo no es pararse: es
**inventar la hipotesis**, que es justo lo que este workflow existe para no hacer ([[D-072]]).

Tu rol es de **orquestador**: sostienes esas preguntas con `AskUserQuestion` y **delegas** la
generacion y la actualizacion de artefactos en `design-feature-architect` (tool `Agent`,
`run_in_background: false` — [[D-043]]). No lees el spec ni el `DESIGN.md` ([[D-031]]) y no escribes
los artefactos ([[D-060]]): pasas paths, y el agente lee, redacta y escribe.

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
4. La feature debe tener Success Metrics declarados en el brief para que el A/B tenga sentido. Si no los hay, **presenta la eleccion con `AskUserQuestion`**: cerrar antes las metricas en el brief (recomendado) o continuar sabiendo que el A/B no tendra criterio de victoria. Si continua, queda registrado en el `_variants.md`.

### 2.2 Capturar hipotesis

Si `--hypothesis` no se paso, pregúntasela al usuario **en conversacion** (es abierta: no la metas en
un menu de opciones). Dale un ejemplo para calibrar la forma: *"una version con CTA mas prominente
aumentara el task completion en checkout"*.

La hipotesis debe ser:
- Especifica (que cambia en cada variante).
- Medible (con que metrica del brief se evalua).
- Acotada en alcance (vista, flujo, componente).

Si el usuario no da una hipotesis especifica, **para y dilo**: sin ella el A/B es decoracion, no
validacion. **No la inventes tu** ni la derives del spec: la hipotesis es lo que alguien quiere
aprender, y eso no esta escrito en ningun artefacto.

### 2.3 Generar variantes

Por cada variante (`A`, `B`, ...):

1. Pregunta al usuario, en conversacion, en que difiere de las demas (1-2 frases). Su respuesta viaja **literal** al delegado.
2. Delega la generacion en `design-feature-architect` (tool `Agent`, `run_in_background: false`) con este contrato:
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
3. **Los escribe el agente** ([[D-059]]/[[D-060]]), en el mismo directorio que los artefactos de prototipado de la feature: la subcarpeta `design/` de la feature si el spec esta en `features/<nombre>/spec/` (que crea si no existe); el mismo directorio del spec en otros casos (layout plano legacy). Emite **las N llamadas en un unico mensaje** si generas varias variantes: con el flag, esa es la barrera que necesita el 2.4 ([[D-047]]). **No hay llamada de prueba** ([[D-084]]): el numero de variantes lo fijaste al decidirlas, no lo confirma la primera que vuelve.

### 2.4 Generar `<feature>_variants.md`

Documento maestro siguiendo la plantilla de `${CLAUDE_SKILL_DIR}/references/variant_templates.md`, en el mismo directorio que las variantes. **Lo escribe tambien el agente**, en una ultima delegacion con la hipotesis, las descripciones literales del usuario y los paths ya generados. Comprueba despues con `test -f` que esta; si falta, reportalo y para — no lo escribas tu.

### 2.5 Informar al usuario

- archivos generados
- siguiente paso, en lenguaje natural: cuando el A/B termine y haya resultados, te los cuenta y registras el ganador. **No le des el comando** — te lo pide hablando.

## Paso 3: Modo `compare`

### 3.1 Verificar

Comprobacion mecanica, sin leer el documento entero:

```bash
!test -f "<path_variants>" && grep -q 'status: *pending_validation' "<path_variants>" && echo PENDIENTE || echo NO_PENDIENTE
```

`NO_PENDIENTE` → o no existe, o ya se valido: dilo y para.

### 3.2 Capturar resultados

Pregunta al usuario, en el hilo principal, y **no rellenes lo que no conteste**:
1. La metrica que dio cada variante.
2. Que variante gano — o "empate" / "no concluyente", que son resultados validos.
3. Que aprendio (notas cualitativas).

Si no hay datos de metrica, el resultado se registra como **no concluyente con la razon**; nunca se
deduce un ganador de la variante que "parece mejor".

### 3.3 Actualizar el documento (delegado)

Delega en `design-feature-architect` con las respuestas literales: añade la sección `## Resultados`
siguiendo la plantilla de `${CLAUDE_SKILL_DIR}/references/variant_templates.md` y cambia
`status: pending_validation` a `status: validated`. **Lo edita el agente**, que es el autor del
documento ([[D-060]]).

### 3.4 Sugerir siguiente paso

- Si hay ganador y se decide aplicar: sugerir `/wf-design-delta analyze` con los cambios de la variante ganadora.
- Si no hay ganador concluyente: documentar y dejar el control como esta.
- Si la conclusion es iterar, sugerir nuevo `wf-design-variant create` con variantes ajustadas.

## Regla operativa

- Las variantes comparten spec. No introducen funcionalidad nueva: si lo hacen, son features distintas, no variantes.
- Las variantes deben ser comparables (mismo journey, misma metric).
- Maximo 3-4 variantes simultaneas. Mas de 4 dispara complejidad estadistica del A/B.
- Tras validacion, el ganador se aplica al sistema; las perdedoras se descartan o se documentan como hipotesis cerrada.
