---
name: wf-design-discover
description: "Descubre 3-5 apps reales del mercado como referencias de diseno para una feature, mediante research web y validacion interactiva con el usuario. Genera <basename>_design_discovery.md reutilizable aguas abajo en la fase design."
when_to_use: "Activa en frases como 'busca apps de referencia', 'explora referentes visuales para esta feature', 'haz research de apps para el sistema visual', 'que apps deberiamos mirar para el design'. No activa para crear DESIGN.md ni flows/views."
argument-hint: "<feature_spec.md> [--prd <prd.md>] [--brief <DESIGN_BRIEF.md>] [--output <path>] [--mode interactive|auto]"
effort: high
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# design-discover — Research de referencias visuales

**Corres en el hilo principal.** Tu propia `description` promete *"validacion interactiva con el
usuario"*, y eso no cabe en un `context: fork`: un subagente no puede presentar una lista y esperar a
que la curen ([[D-002]]/[[D-045]]). Aqui el riesgo era doble — o el paso se saltaba, o las referencias
se daban por validadas sin que nadie las hubiera mirado ([[D-072]]).

Tu rol es de **orquestador**: verificas precondiciones, **delegas el research** en
`design-system-architect` (tool `Agent`, `run_in_background: false` — [[D-043]]), **sostienes la
curacion** con el usuario, y **delegas la escritura** del discovery al mismo agente. No lees el spec
([[D-031]]) ni escribes el artefacto ([[D-060]]): pasas paths y el agente lee, redacta y escribe.

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

```bash
!test -f "<path_spec>" && echo EXISTE || echo NO_EXISTE
```

`NO_EXISTE` → deten. Si el contenido es un Spec SDD utilizable lo valora tu delegado, que es quien lo lee.

## Paso 3: Resolver brief y PRD

Resuelve **paths**, no contenidos: `--brief` si se paso, si no `DESIGN_BRIEF.md` en la raiz del producto; `--prd` si se paso. El brief y el PRD ayudan a guiar el research, pero no son bloqueantes.

## Paso 4: Determinar path de salida

- Si `--output` se paso, usalo.
- Si no, escribe `<basename>_design_discovery.md` (donde `<basename>` es el nombre del spec sin `_spec.md`): en la subcarpeta `design/` de la feature si el spec esta en `features/<nombre>/spec/` (crea el directorio si no existe); en el mismo directorio del spec en otros casos (layout plano legacy).

## Paso 5: Contexto base y research (delegados)

Los pasos 5, 6 y 7 los hace **el agente**, en una sola delegacion: leer el spec para derivar el
contexto, componer las queries y ejecutar el research es un solo trabajo experto. Delega con la tool
`Agent`, `subagent_type: "design-system-architect"` y **`run_in_background: false`**, pasandole los
paths del Paso 3 y pidiendole que **devuelva la lista preliminar sin escribir ningun fichero**.

Lo que el agente extrae del spec, PRD y brief:
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

## Paso 8: Validar con el usuario (aqui, en el hilo principal)

### Modo `interactive` (por defecto)

Presenta la lista que devolvio el agente —app, aspecto destacable, plataforma y **por que es relevante
para esta feature**— y ofrece con `AskUserQuestion`: **mantenerlas todas**, **quitar alguna** o
**anadir una tuya**. Es una eleccion, no un formulario: puedes repetirla si el usuario ajusta y quiere
volver a ver la lista. Maximo 5 apps en el resultado final.

Las apps que anada el usuario entran **con su nombre literal** y marcadas `source: usuario`; no las
sustituyas por lo que tu creas que quiso decir.

### Modo `auto`

No preguntes. Se toman las 3-5 mejores del research, marcadas `source: research` — y el artefacto
tiene que decir que **nadie las valido**, para que aguas abajo no se lean como elegidas.

## Paso 9: Escribir el discovery (delegado)

Delega otra vez en `design-system-architect` (mismo flag) con la lista final y el path de salida. **El
agente escribe** `<basename>_design_discovery.md` — es su artefacto ([[D-059]]/[[D-060]]) — con esta
estructura:

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

## Paso 10: Comprobar e informar

```bash
!test -f "<path_discovery>" && echo ESCRITO || echo FALTA
```

`FALTA` → no lo escribas tu ([[D-060]]): reporta que el agente no dejo el artefacto y para.

Con el artefacto en su sitio, reporta:
- path del discovery
- numero de apps validadas por el usuario (y cuantas quedaron `source: research` sin validar)
- gaps detectados (si los hay)
- siguiente paso, en lenguaje natural: generar el sistema visual del producto, que consumira este discovery si esta en el directorio esperado. **No le des el comando** — te lo pide hablando.
