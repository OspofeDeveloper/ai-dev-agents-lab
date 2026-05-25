---
name: wf-design-feature-prototype
description: Orquestador SDD para derivar artefactos de prototipado visual de una feature a partir de su _spec.md y un DESIGN.md. Genera flows, views y prompt para Stitch listos para contrastar con cliente antes del plan tecnico. Activa en frases como "genera las vistas para Stitch", "crea el prototipo de la feature", "prepara flows y prompt de diseno", "deriva las pantallas desde el spec". No activa para modificar el spec, ni para generar plan o tasks.
argument-hint: "generate <feature_spec.md> [--design-file DESIGN.md]"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: design-architect
---

# design-feature-prototype — Orquestador del Flujo SDD (Etapa Design)

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el Spec y el `DESIGN.md` estan listos, delegas la derivacion de artefactos al agente `design-architect`, y escribes los resultados.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (solo `generate` esta soportado)
- **Path del spec**: primer argumento posicional
- **Path de DESIGN.md** mediante `--design-file` opcional

Si no hay argumento o el modo no es valido, informa:
> "Uso: `/wf-design-feature-prototype generate <archivo_spec.md> [--design-file DESIGN.md]`"

## Paso 2: Verificar el Spec

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Deten la ejecucion si:
   - hay HUs `[INCOMPLETO]`
   - hay items `[CRITICO]_(pendiente)_`
   - `status_sync: stale`
   - `status_sync: needs_review`
4. Verifica que parece un Spec SDD validado.

## Paso 3: Resolver DESIGN.md

- Si se pasa `--design-file`, usalo.
- Si no, busca `DESIGN.md`:
  - dos niveles arriba si el spec esta en `features/<nombre>/`
  - en el mismo directorio en otros casos

Si no existe, deten:
> "No se encontro `DESIGN.md`. Primero ejecuta `/wf-design-system generate <spec.md>` o indica `--design-file`."

Lee `DESIGN.md` completo.

## Paso 4: Determinar outputs

En el mismo directorio del spec, crea:
- `<feature>_flows.md`
- `<feature>_views.md`
- `<feature>_ui_prompt.md`

Donde `<feature>` es el nombre base del spec sin `_spec.md`.

## Paso 5: Delegar al agente design-architect

Invoca al agente siguiendo la **Regla 3**, la **Regla 7**, la **Regla 8** y la **Regla 9** de `kb-design-expert`: `flows` describen secuencia y navegacion, `views` son la SSoT de la pantalla, y `ui_prompt` debe ensamblar sin volver a definir.

Usa este prompt:

```text
Modo: feature-prototype
Path del spec: <path_spec>
Contenido del Spec:
---
<contenido_spec>
---
Contenido del DESIGN.md:
---
<contenido_design>
---
INSTRUCCION: produce tres artefactos separados y completos:
1. <feature>_flows.md
2. <feature>_views.md
3. <feature>_ui_prompt.md

Cada vista debe trazar a HUs, journeys y CAs del spec.
No inventes funcionalidad fuera del spec.
Responsabilidades:
- <feature>_flows.md: secuencias, precondiciones y transiciones. No metas componentes ni estados visuales detallados.
- <feature>_views.md: contrato canonico de pantallas, componentes, acciones, estados visuales y notas de layout.
- <feature>_ui_prompt.md: prompt de ensamblaje para Stitch que referencia DESIGN.md, flows y views sin duplicar su contenido pantalla por pantalla.
Si faltan datos criticos, devuelve DESIGN_GAPs y no produzcas artefactos parciales.
```

## Paso 6: Manejar DESIGN_GAPs

Si el agente devuelve `DESIGN_GAP` o `DESIGN_GAPs`:
- informa al usuario
- no escribas archivos

## Paso 7: Escribir resultados

Escribe cada artefacto en su archivo correspondiente.

## Paso 8: Informar al usuario

- paths generados
- total de vistas derivadas
- siguiente paso recomendado:
  > "Usa `<feature>_ui_prompt.md` junto con `DESIGN.md` en Stitch para generar las vistas y, tras validar con cliente, continua con `/wf-prepare-plan generate <feature_spec.md>`"
