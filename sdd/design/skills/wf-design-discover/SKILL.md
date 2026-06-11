---
name: wf-design-discover
description: "Descubre 3-5 apps reales del mercado como referencias de diseno para una feature, mediante research web y validacion interactiva con el usuario. Genera <basename>_design_discovery.md reutilizable aguas abajo en la fase design."
when_to_use: "Activa en frases como 'busca apps de referencia', 'explora referentes visuales para esta feature', 'haz research de apps para el sistema visual', 'que apps deberiamos mirar para el design'. No activa para crear DESIGN.md ni flows/views."
argument-hint: "<feature_spec.md> [--prd <prd.md>] [--brief <DESIGN_BRIEF.md>] [--output <path>] [--mode interactive|auto]"
effort: high
allowed-tools: [Read, Write, Bash, WebSearch, WebFetch]
context: fork
---

# design-discover — Research de referencias visuales

Tu rol es producir `<basename>_design_discovery.md` con apps reales del mercado que sirvan de referencia concreta para el sistema visual. Reduce el riesgo de diseno generico al anclar el DESIGN.md a inspiracion real.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del spec**: primer argumento posicional.
- **Path del PRD** opcional mediante `--prd`.
- **Path del brief** opcional mediante `--brief`.
- **Path de salida** opcional mediante `--output`.
- **Modo** opcional mediante `--mode` (`interactive` por defecto, `auto` para flujos no asistidos).

Si no hay path, informa:
> "Uso: `/wf-design-discover <feature_spec.md> [--prd <prd.md>] [--brief <DESIGN_BRIEF.md>] [--output <path>] [--mode interactive|auto]`"

## Paso 2: Verificar el Spec

1. Verifica que el spec existe.
2. Lee el archivo completo.
3. Si no parece un Spec SDD validado, deten:
   > "Este archivo no parece un Spec SDD validado. Primero ejecuta los workflows de spec."

## Paso 3: Resolver brief y PRD

Si `--brief` se paso, leelo. Si no, intenta resolver `DESIGN_BRIEF.md` en la raiz del producto.
Si `--prd` se paso, leelo. El brief y el PRD ayudan a guiar el research, pero no son bloqueantes.

## Paso 4: Determinar path de salida

- Si `--output` se paso, usalo.
- Si no, escribe `<basename>_design_discovery.md` (donde `<basename>` es el nombre del spec sin `_spec.md`): en la subcarpeta `design/` de la feature si el spec esta en `features/<nombre>/spec/` (crea el directorio si no existe); en el mismo directorio del spec en otros casos (layout plano legacy).

## Paso 5: Derivar contexto base

Extrae del spec, PRD y brief:
- sector
- actor principal
- flujos dominantes
- tono funcional
- familia visual esperada (si esta cerrada en el brief)

## Paso 6: Generar queries

Deriva 2-3 queries adaptadas al contexto. No uses plantillas fijas:
- Una orientada a apps referentes del sector con diseno reconocido.
- Una orientada a patrones UI especificos de los flujos dominantes.
- Una adicional si el tono o nicho lo justifican (ej. "award winning <sector> app design").

## Paso 7: Ejecutar research

Ejecuta WebSearch con cada query. De los resultados extrae:
- Nombre de la app.
- Sector y plataforma (iOS/Android/Web).
- Aspecto concreto destacable: densidad de informacion, paleta, tipografia numerica, micro-interacciones, componentes recurrentes.
- Por que es relevante para esta feature concreta (no copies el nombre sin razonamiento).

Si una busqueda devuelve resultados pobres, intenta una segunda query mas especifica. Si tras dos intentos no hay material util, marca `DESIGN_GAP` y continua.

## Paso 8: Validar con el usuario

### Modo `interactive` (por defecto)

Presenta la lista preliminar al usuario:
```
Encontre estas apps como referencias candidatas:
1. <App A> — <aspecto> — <plataforma>
2. <App B> — <aspecto> — <plataforma>
...
```

Pregunta:
> "¿Quieres mantener todas, ajustar la lista o anadir alguna tu? (mantener / quitar N / anadir <app>)"

Iterar hasta que el usuario confirme. Maximo 5 apps en el resultado final.

### Modo `auto`

No preguntar. Tomar las 3-5 mejores referencias del research y marcarlas con `source: research` en el output.

## Paso 9: Escribir el discovery

Escribe `<basename>_design_discovery.md` con esta estructura:

```markdown
---
spec: <path_spec>
mode: interactive | auto
generated_at: <fecha ISO>
---

# Design Discovery — <feature name>

## Contexto

- **Sector**: <sector>
- **Actor principal**: <actor>
- **Flujos dominantes**: <flujos>
- **Tono funcional**: <tono>

## Queries usadas

1. `<query 1>`
2. `<query 2>`
3. `<query 3>`

## Apps de referencia

### <App 1>
- **Plataforma**: <iOS / Android / Web>
- **Aspecto a tomar**: <densidad / paleta / tipografia / componentes / micro-interacciones>
- **Justificacion**: <por que es relevante para esta feature concreta>
- **Fuente**: <research | usuario>

### <App 2>
...

## Gaps detectados (si los hay)

- [DESIGN_GAP] <descripcion>
```

## Paso 10: Informar al usuario

Reporta:
- path del discovery
- numero de apps validadas
- gaps detectados (si los hay)
- siguiente paso recomendado:
  > "Ahora ejecuta `/wf-design-system generate <feature_spec.md> [--brief <DESIGN_BRIEF.md>]` — el sistema visual consumira este discovery automaticamente si esta en el directorio esperado."
