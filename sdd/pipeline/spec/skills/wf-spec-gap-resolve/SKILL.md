---
name: wf-spec-gap-resolve
description: "Completa HUs y CAs [INCOMPLETO] desde respuestas ya escritas en un _analysis.md y confirma CAs [INFERIDO] de specs de caracterizacion. Via recomendada para resolver gaps sin tratarlos como delta funcional amplio."
when_to_use: "Activa en frases como 'resuelve estos gaps del spec', 'completa incompletos desde el analysis', 'aplica respuestas del analysis al spec', 'cerrar HUs incompletas', 'confirma los inferidos del spec'."
argument-hint: "<feature_spec.md> [--analysis <analysis.md>]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-writer
user-invocable: true
---

# Workflow: SPEC-GAP-RESOLVE

Tu objetivo es integrar respuestas a gaps ya detectados sobre un feature spec que contiene HUs `[INCOMPLETO]`.

**Un gap puede vivir en dos sitios, y los dos son legítimos** (SSoT: `kb-gap-conventions`, "Dónde vive un gap"): en el `_analysis.md` del documento origen, o en el `## Items Pendientes` **del propio spec** cuando el gap nació al escribirlo (`wf-spec-fast-track` Paso 6 lo prescribe así, y en modo directo o brownfield **no hay analysis en absoluto**). **Resuelves el gap donde está definido su bloque.**

Esta skill existe para separar dos casos:

- resolver una ambigüedad ya detectada
- cambiar el producto o el comportamiento de forma más amplia

Si al leer la respuesta detectas que en realidad cambió el alcance o una exclusión del PRD, detén e indica que debe usarse `wf-prd-change` antes de continuar.

## Paso 1: Parsear argumentos

Extrae:

- path del spec
- `--analysis <analysis.md>` opcional

Si falta el spec:
> "Necesito el spec cuyas historias incompletas hay que completar."

## Paso 2: Verificar archivos

Comprueba que el spec existe y termina en `_spec.md`.

Si no se proporcionó `--analysis`, auto-descubre el `_analysis.md` en el directorio base del proyecto. **Que no haya ninguno no es un error**: un spec de modo directo o de caracterización no tiene analysis, y sus gaps viven en su propia sección.

## Paso 3: Leer y extraer gaps

Lee el spec y detecta:

- HUs `[INCOMPLETO]`
- IDs `[P-XXX]` referenciados
- CAs `[INFERIDO]` (specs de caracterización, `Origen: characterization`)

**Localiza cada `[P-XXX]` en su hogar, empezando por el spec** ([[D-054]]). El script es agnóstico
al documento —parsea cualquier fichero con bloques de gap—, así que se le pregunta a él, primero
al spec y después al analysis:

```bash
!python3 .sdd/scripts/sdd-analysis-gaps.py "<feature_spec.md>" --list --json
!python3 .sdd/scripts/sdd-analysis-gaps.py "<analysis.md>" --list --json   # si existe
```

Cada ID referenciado queda emparejado con **el fichero donde vive su bloque**; si está en los dos,
manda el del spec. Ese emparejamiento es el que gobierna los Pasos 5 y 7: la respuesta se lee y se
escribe **en ese fichero**, con `--answer` apuntado a él.

> **Por qué esto estaba roto ([[D-054]]).** Este paso ya leía el spec para sacar los IDs, pero
> buscaba **todas** las respuestas en el `_analysis.md`. Medido en conformance (2026-09-07): un
> spec quedó con 4 HUs `[INCOMPLETO]` por un gap de **segundo orden** —nacido del cruce de dos
> respuestas, así que imposible de haber estado en el análisis— definido en su propio
> `## Items Pendientes`. Con el análisis dando `CRITICAL_ANSWERED, 0 abiertos`, esta skill habría
> concluido *"no queda nada que resolver"* mientras el gate seguía bloqueando el plan de esa
> feature. Callejón sin salida: el gate correcto, y la vía sancionada sin alcanzar el gap.

### Caso `[INFERIDO]` — confirmación humana, no analysis

Los `[INFERIDO]` no se resuelven desde un `_analysis.md`: la fuente de confirmación es el usuario (o evidencia nueva que aporte). Para cada CA `[INFERIDO]`, presenta el comportamiento deducido + su `Confirmación pendiente` y pregunta:
- **Confirmado** → elimina el marcador y actualiza `Evidencia:` a `confirmado por <usuario> el <fecha>` (mantén la evidencia parcial original).
- **Incorrecto** → corrige el CA con el comportamiento real que indique el usuario (con su nueva evidencia si la aporta) o elimínalo si la capacidad no existe.
- **No lo sé** → el marcador se queda; ese CA sigue bloqueando el plan (regla de `kb-spec-characterization`).

## Paso 4: Validar que sigue siendo un gap y no un change request

Si la respuesta:

- contradice el PRD vigente
- mueve algo entre MVP y fase futura
- altera una exclusión explícita
- redefine reglas de negocio de forma sustancial

detén y remite a `wf-prd-change`.

## Paso 5: Integrar respuestas

Aplica la misma lógica de integración necesaria para completar un spec ya generado, pero limitada a:

- texto faltante de HUs
- CAs que no pudieron generarse
- eliminación de marcadores `[INCOMPLETO]`
- actualización de `Items Pendientes`

## Paso 6: Versionado y trazabilidad

Incrementa versión menor del spec y registra en changelog:

- HUs completadas
- gaps resueltos
- analysis usado

## Paso 7: Informar siguiente paso

Si ya no quedan HUs `[INCOMPLETO]` ni CAs `[INFERIDO]`:
> "El spec quedó completo. Si quieres, lo valido antes de seguir; y cuando digas, pasamos a planificarlo."

Si quedan gaps sin respuesta — **cuáles quedan lo dice el script, no tu lectura** ([[D-042]]), y
hay que checkear **los dos hogares** ([[D-054]]): un `--check` contra el análisis no dice nada
sobre los gaps que viven en el spec.

```
!python3 .sdd/scripts/sdd-analysis-gaps.py "<feature_spec.md>" --check --json
!python3 .sdd/scripts/sdd-analysis-gaps.py "<analysis.md>" --check --json   # si existe
```

> "Quedan [N] gap(s) `[CRÍTICO]` pendiente(s) ([IDs]). Respóndelos —sustituyendo `- **Respuesta**: _(pendiente)_` en el bloque de cada uno, o dictándomelos— y retomamos el completado."

Di **en qué fichero** está cada uno: no es lo mismo abrir el análisis del PRD que la sección del
propio spec, y el usuario necesita saber dónde escribir. Las respuestas las escribe él; si te las
dicta, se aplican con `sdd-analysis-gaps.py "<fichero donde vive el gap>" --answer P-XXX "texto"`.
Nunca las completes tú (tabla de ámbito en `kb-gap-conventions`).

Si quedan `[INFERIDO]` sin confirmar:
> "Quedan N CAs [INFERIDO] sin confirmar — siguen **bloqueando el paso a planificación**. Confirma o corrige esos comportamientos cuando tengas la evidencia."
