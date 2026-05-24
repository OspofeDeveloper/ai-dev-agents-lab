---
name: wf-spec-gap-resolve
description: Completa HUs y CAs marcadas como `[INCOMPLETO]` a partir de respuestas ya escritas en un `_analysis.md`, sin tratar el cambio como un delta funcional amplio. Es la vía recomendada para resolver gaps del analyze cuando no ha cambiado el alcance del producto. Activa en frases como "resuelve estos gaps del spec", "completa incompletos desde el analysis", "aplica respuestas del analysis al spec", "cerrar HUs incompletas".
argument-hint: "<feature_spec.md> [--analysis <analysis.md>]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-writer
---

# Workflow: SPEC-GAP-RESOLVE

Tu objetivo es integrar respuestas a gaps ya detectados en un `_analysis.md` sobre un feature spec que contiene HUs `[INCOMPLETO]`.

Esta skill existe para separar dos casos:

- resolver una ambigüedad ya detectada
- cambiar el producto o el comportamiento de forma más amplia

Si al leer la respuesta detectas que en realidad cambió el alcance o una exclusión del PRD, detén e indica que debe usarse `wf-prd-change` antes de continuar.

## Paso 1: Parsear argumentos

Extrae:

- path del spec
- `--analysis <analysis.md>` opcional

Si falta el spec:
> "Uso: `/wf-spec-gap-resolve <feature_spec.md> [--analysis <analysis.md>]`"

## Paso 2: Verificar archivos

Comprueba que el spec existe y termina en `_spec.md`.

Si no se proporcionó `--analysis`, auto-descubre el `_analysis.md` en el directorio base del proyecto.

## Paso 3: Leer y extraer gaps

Lee el spec y detecta:

- HUs `[INCOMPLETO]`
- IDs `[P-XXX]` referenciados

Lee el `_analysis.md` y recupera las respuestas existentes.

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

Si ya no quedan HUs `[INCOMPLETO]`:
> "El spec quedó completo. Puedes validarlo con `/wf-spec-validate <spec.md>` y después avanzar a `/wf-prepare-plan generate <spec.md>`."

Si quedan gaps sin respuesta:
> "Quedan gaps pendientes en el `_analysis.md`. Responde esos items antes de volver a ejecutar `wf-spec-gap-resolve`."
