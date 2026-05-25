---
name: wf-design-system
description: Orquestador SDD para crear o actualizar el DESIGN.md de un producto a partir de un feature spec validado. Usalo cuando ya exista un _spec.md y quieras definir la identidad visual persistente que alimentara Stitch y futuros prototipos de features. Activa en frases como "crea el DESIGN.md", "genera el sistema visual desde el spec", "prepara el contrato visual del producto", "actualiza el DESIGN.md". No activa para generar planes KMM ni tasks.
argument-hint: "generate <feature_spec.md> [--design-file DESIGN.md]"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: design-architect
---

# design-system — Orquestador del Flujo SDD (Etapa Design)

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el Spec esta listo, delegas la definicion del sistema visual al agente `design-architect`, y escribes el `DESIGN.md` resultante.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (solo `generate` esta soportado)
- **Path del spec**: primer argumento posicional tras el modo
- **Path de DESIGN.md** opcional mediante `--design-file`

Si no hay argumento o el modo no es valido, informa:
> "Uso: `/wf-design-system generate <archivo_spec.md> [--design-file DESIGN.md]`"

## Paso 2: Verificar el Spec

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Deten la ejecucion si ocurre cualquiera de estos casos:
   - hay HUs `[INCOMPLETO]`
   - hay items `[CRITICO]_(pendiente)_`
   - `status_sync: stale`
   - `status_sync: needs_review`
4. Si el archivo no parece un Spec SDD validado (no contiene "Historias de Usuario" y "Criterios de Aceptacion"), informa:
   > "Este archivo no parece un Spec SDD validado. Primero ejecuta los workflows de spec."

## Paso 3: Determinar paths

- Si se paso `--design-file`, usa ese path.
- Si no, crea o actualiza `DESIGN.md` en el directorio raiz del producto:
  - si el spec esta en `features/<nombre>/`, usa dos niveles arriba
  - en otros casos, usa el mismo directorio del spec

Si el archivo ya existe, leelo completo para usarlo como base.

## Paso 4: Delegar al agente design-architect

Invoca al agente siguiendo la **Regla 2**, la **Regla 3** y la **Regla 6** de `kb-design-expert`: `DESIGN.md` es de producto, debe ser la SSoT visual persistente y debe seguir el formato abierto de Google con tokens normativos + rationale.

Usa este prompt:

```text
Modo: design-system
Path del spec: <path_spec>
Path del DESIGN.md destino: <path_design>
Contenido del Spec:
---
<contenido_completo_spec>
---
DESIGN.md actual:
---
<contenido_actual_o_N/A>
---
INSTRUCCION: produce un DESIGN.md de producto reutilizable por Stitch y por futuras features. No introduzcas funcionalidades no presentes en el spec. Estructuralo como contrato visual persistente de producto, no de una sola feature. Usa front matter YAML + cuerpo markdown. Si faltan datos criticos para definir jerarquia, tono o patrones base, devuelve DESIGN_GAPs y no produzcas archivo final.
```

## Paso 5: Manejar DESIGN_GAPs

Si el agente devuelve `DESIGN_GAP` o `DESIGN_GAPs`:
- informa la lista al usuario
- no escribas el archivo
- sugiere completar el spec o aportar contexto visual de producto

## Paso 6: Escribir el resultado

Escribe el output del agente en el path destino como `DESIGN.md`.

## Paso 7: Informar al usuario

- path del `DESIGN.md` generado
- breve resumen del sistema visual
- si procede, recomendar validar el archivo con `npx @google/design.md lint DESIGN.md` para detectar problemas estructurales o de tokens
- siguiente paso recomendado:
  > "Ahora ejecuta `/wf-design-feature-prototype generate <feature_spec.md> [--design-file <DESIGN.md>]`"
