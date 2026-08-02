---
name: wf-prd-change
description: "Gestiona cambios de producto sobre un PRD existente: clasifica el cambio (aclaracion vs change request), actualiza el PRD si corresponde y deja trazabilidad con matriz de impacto sobre specs, plan y tasks."
when_to_use: "Activa en frases como 'cambia el alcance del PRD', 'esto pasa de fase 2 a MVP', 'actualiza el PRD con esta decision', 'gestiona este cambio de producto', 'abre un change request sobre el PRD'."
argument-hint: "<prd.md> --new-reqs <cambio.md|texto> [--defer-decisions]"
effort: high
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# Workflow: PRD-CHANGE

Tu objetivo es gestionar cambios de producto una vez que el PRD ya existe y el pipeline puede haber generado artefactos derivados.

Este workflow corre en el **hilo principal** ([[D-040]]): un cambio de producto exige decisiones que solo el humano puede tomar —cómo se clasifica y, cuando la petición admite varias lecturas de alcance, cuál es— y `AskUserQuestion` no existe dentro de un subagente. El **análisis** del cambio (clasificación, secciones afectadas, bifurcaciones) y la **escritura** del PRD y de la traza los hace el agente `prd-expert`, que carga `kb-prd-expert` y `kb-product-change-governance`; tú lo invocas vía la tool `Agent` (Pasos 4 y 6) y sostienes el gate aquí, en el hilo principal.

**No leas el PRD ni lo escribas tú** ([[D-031]]/[[D-038]]): su lectura y su edición son del `prd-expert`. Lo único que ejecutas sobre el fichero es `sdd-prd-apply.py --reopen` por `Bash` (Paso 7) — igual que `wf-prd-review` ejecuta `--seal`. Esto vale **aunque tengas otras tools disponibles**: el `allowed-tools` de un skill **no es enforcement duro**, así que la restricción es normativa. Si te descubres a punto de hacer `Read`/`Edit` del PRD, para y delega.

**Regla de oro:** si el cambio altera el producto comprometido, el PRD se actualiza primero y la trazabilidad se registra antes de hablar de specs.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:

- path del `PRD.md`
- **el cambio propuesto**, en cualquiera de sus dos formas: `--new-reqs <archivo.md>` o **el texto del cambio inline** (lo que el usuario dijo en la conversación). Las dos son válidas: exigir un fichero te obligaría a **escribirlo tú**, y en el hilo principal no escribes ficheros. Lo que importa no es que el cambio llegue como fichero, sino que su **texto literal quede recogido** en `changes/CR-XXX/change-request.md` (Paso 6) — ahí es donde se convierte en trazabilidad.
- `--defer-decisions` (opcional): desactiva el gate del Paso 5. Ver «Modo sin gate» al final.

Si falta el PRD o el cambio:
> "Uso: `/wf-prd-change <prd.md> --new-reqs <cambio.md>` (o descríbeme el cambio directamente)"

## Paso 2: Verificar archivos

Comprueba por `Bash` que existe el PRD (y el documento de cambio, si vino como fichero).

Si no existe alguno, informa y detén.

## Paso 3: Estado mecánico del PRD

```
!python3 .sdd/scripts/sdd-prd-ready.py "<path>" --json
```

Te dice si está sellado (`sealed`, `approved_by`) y si ya había asunciones abiertas (`inline_marks`). Lo necesitas para dos cosas: saber si habrá que reabrir el sello (Paso 7) y, si ya había marcas, avisar al usuario de que ese PRD **no estaba aprobado** antes de este cambio.

No cargues el PRD aquí.

## Paso 4: Analizar y clasificar el cambio (delegado, read-only)

Invoca al `prd-expert` vía la tool `Agent`. Recibe el **path** del PRD y el texto del cambio; devuelve un diagnóstico estructurado y **no escribe nada todavía**:

- **clasificación** siguiendo `kb-product-change-governance`: `CLARIFICATION` · `BEHAVIOR_CHANGE` · `SCOPE_CHANGE` · `PRIORITY_CHANGE` · `DEPRECATION`, con **severidad** (`BAJA|MEDIA|ALTA`), si **exige editar el PRD** (`sí/no`) y **por qué**
- **secciones que tocaría** y qué quedaría falso o contradictorio si no se tocan
- **bifurcaciones de alcance**: si la petición admite dos o más lecturas con impacto distinto en el PRD, enumérialas con lo que implica cada una. **No elijas** — esa es la decisión del Paso 5
- **asunciones que propondría**: qué afirmaciones tendría que escribir que **no trazan** al texto del cambio (ver el brief del Paso 6)

Que el experto **no aplique nada** en este paso es lo que hace posible el gate: no se puede pedir permiso sobre algo ya escrito.

## Paso 5 (gate, hilo principal): Confirmar clasificación y resolver bifurcaciones

**Siempre**, con `AskUserQuestion`, y en **un solo gate** que agrupe:

1. **La clasificación** que propone el experto, con su razonamiento y su consecuencia práctica —la que importa es si **se edita el PRD o no**—, para que el usuario la confirme o la corrija.
2. **Cada bifurcación de alcance** que el experto haya surfaceado, con lo que implica cada rama.

**Siempre, sin excepción por trivialidad.** Decidir *cuándo* preguntar es un juicio, y es exactamente el juicio que falló: en conformance (CU-7.b) la misma clase de bifurcación se preguntó en una pasada y se resolvió en solitario en la otra. Un gate que salta según el criterio del agente no es un gate.

> **El usuario puede corregir la clasificación; tú no.** Es el product owner: si dice "esto era solo una aclaración" o "no, esto sí cambia el alcance", manda. Lo que **no** haces es enrutar contra el experto por tu cuenta ([[D-038]]): tú presentas su clasificación, no la sustituyes por la tuya.

Si la clasificación confirmada es **`CLARIFICATION` que no contradice el PRD**:

- el PRD **no** se reescribe
- se genera igualmente la traza del cambio (Paso 6)
- se recomienda `wf-spec-gap-resolve` o `wf-spec-delta` según el artefacto afectado

## Paso 6: Aplicar el cambio y registrar la traza (delegado)

Invoca de nuevo al `prd-expert` vía `Agent` con un brief quirúrgico que lleve **las decisiones del Paso 5**, no la petición cruda. El experto:

**A. Edita el PRD** (solo si la clasificación confirmada lo exige):

1. actualiza versión y fecha del PRD
2. reescribe **únicamente** las secciones afectadas; conserva el resto intacto
3. si una exclusión de fase futura pasa a MVP, elimina o corrige esa exclusión
4. localiza **por texto**, nunca por número de línea
5. nunca mete detalles técnicos

**B. Marca `[ASUNCIÓN]` todo lo que escriba y no trace a la petición** ([[D-039]]). La anti-fabricación de `kb-prd-expert` (Regla 12) **no caduca al sellar**: rige cada escritura sobre el PRD, no solo la creación. Un cambio casi nunca llega completo, y lo que se añada para dejarlo coherente **es inferencia del agente, no decisión del usuario**. Traza al origen (el cambio pedido o lo decidido en el gate) → va tal cual. No traza → **marca inline `[ASUNCIÓN]` + entrada `[ASN-XXX]`**, con el formato y el invariante 1:1 de `kb-prd-expert`.

- **La capacidad pedida traza; lo que la rodea, normalmente no.** Si piden "marcar gastos como deducibles", *marcar* traza; **"consultar el conjunto de deducibles" es inferencia** → marca.
- **Estrechar o reinterpretar una exclusión o una regla transversal existente es una decisión de producto, y va marcada.** Es el caso más fácil de colar porque se siente como higiene ("si no la matizo, queda contradictoria"). No lo es: elegir **dónde** queda la nueva frontera —"lo que sigue fuera es el fichero oficial, marcar y consultar entra"— es alcance que nadie ha pedido. Fallo real observado en conformance CU-7.b pasada 2.
- **No razones "esto es materia de Spec, lo dejo para `wf-spec-analyze`" sobre una decisión de alcance.** Materia de Spec es el detalle de *cómo* (¿el total agregado?, ¿admite porcentaje?); la **frontera del producto** es materia de PRD y se marca aquí. Diferir lo pequeño mientras se decide lo grande en solitario es el patrón exacto que [[D-039]] cierra.
- **Numeración e IDs:** continúa desde el `[ASN-XXX]` más alto presente en el documento; si no queda ninguno —lo normal en un PRD ya revisado, donde el review vació y **eliminó** la sección— arranca de nuevo en `ASN-001` y **recrea la sección** `## Asunciones del PRD` con su callout, tal como la define `kb-prd-expert`.
- **El experto no las resuelve.** Corre como subagente, así que **no puedes presentar preguntas al usuario** desde ahí: si no puedes preguntar, no puedes decidir. Lo que quedó marcado lo resuelve el humano en el gate de `wf-prd-review`, y hasta entonces `sdd-prd-ready.py` dará `OPEN_ASSUMPTIONS`, que es el estado **correcto**, no un defecto.

**C. Registra la trazabilidad.** Escribe o actualiza:

- `product-changelog.md` — índice global
- `changes/CR-XXX/change-request.md`
- `changes/CR-XXX/decision.md`

Toda la documentación detallada del cambio queda agrupada dentro de `changes/CR-XXX/`. La entrada mínima del changelog incluye ID del cambio, fecha, tipo, resumen de la decisión, secciones del PRD tocadas y artefactos potencialmente afectados.

`changes/CR-XXX/change-request.md` lleva:

- clasificación del cambio **y quién la confirmó** (la decisión del gate, no solo la propuesta del experto)
- **el texto literal de la petición**, tal como llegó (fichero o conversación)
- **las bifurcaciones planteadas y cuál se eligió**, con el motivo — es lo que hace auditable que la decisión fue humana
- diff funcional resumido
- **asunciones introducidas** ([[D-039]]): por cada `[ASN-XXX]` añadida, su **texto literal** y el hueco que rellena. Los IDs se reciclan entre ciclos de review, así que el ID por sí solo no es trazabilidad
- impacto preliminar sobre analysis · discovery · features index · specs · plan · tasks
- siguiente workflow recomendado

`changes/CR-XXX/decision.md` lleva la decisión aprobada, el motivo, las secciones del PRD tocadas y el resumen de artefactos afectados.

## Paso 7: Reabrir el sello (script, hilo principal)

Solo si el Paso 6 editó el PRD **y** el Paso 3 lo encontró sellado (`status: approved` con `Aprobado por:` relleno).

**Reabre el sello ([[D-028]]/[[D-032]]).** El cambio de contenido invalida esa aprobación —atestiguaba un contenido que ya no existe—. Reábrela de forma **determinista** por script, no editando el frontmatter a mano:

```
!python3 .sdd/scripts/sdd-prd-apply.py "<path>" --reopen
```

baja `status:` a `in-review` y **resetea la línea `Aprobado por:` al placeholder pendiente**, para que el sello nunca certifique contenido no revisado. **No re-selles tú aquí:** el sello lo restablece **solo** el gate de review (que sube `status:` a `approved`, [[D-032]]), para que "sellado" siga significando "un humano aprobó *este* contenido".

Verifica el resultado y quédate con el veredicto para el informe:

```
!python3 .sdd/scripts/sdd-prd-ready.py "<path>" --json
```

## Paso 8: Informar siguiente paso

- Si fue **solo aclaración**:
  > "El cambio no altera el producto comprometido. No fue necesario reescribir el PRD. Continúa con `wf-spec-gap-resolve` o `wf-spec-delta` según el artefacto afectado."

- Si hubo cambio de producto **y quedaron asunciones** ([[D-039]]) — cita el veredicto del Paso 7:
  > "El PRD se actualizó y se registró el cambio, pero el cambio no venía completo: quedan N asunciones inferidas por confirmar (`OPEN_ASSUMPTIONS`). Re-aprueba con `wf-prd-review`, que las resuelve una a una contigo y vuelve a sellar. Después, `wf-prd-sync-impact <prd.md>` para medir los derivados."

  No presentes las asunciones como una pega del cambio ni las resuelvas por tu cuenta: son el registro honesto de lo inferido, y el gate del review es su sitio.

- Si hubo cambio de producto **sin** asunciones (todo trazaba a la petición y al gate):
  > "El PRD se actualizó y se registró el cambio. Re-aprueba con `wf-prd-review` (el sello quedó reabierto) y ejecuta `wf-prd-sync-impact <prd.md>` para medir qué artefactos derivados han quedado desincronizados."

## Modo sin gate — `--defer-decisions`

Para invocaciones **desde otro workflow** que corre como subagente y por tanto no puede preguntar: hoy, `wf-prd-change-cascade` ([[D-040]]).

Con `--defer-decisions` se **omite el Paso 5** y rige un invariante duro:

> **Sin humano, la ambigüedad se marca — nunca se decide.**

Es decir:

- **cada bifurcación de alcance** que el experto surfacee en el Paso 4 se resuelve por la lectura **más conservadora** (la que menos alcance añade) **y esa elección se marca `[ASUNCIÓN]`** con las alternativas anotadas en `change-request.md`;
- **toda afirmación que no trace** se marca, como siempre (Paso 6.B);
- **la clasificación** es la del experto, se **reporta** sin confirmar, y queda registrada como *no confirmada por humano* en `change-request.md`;
- el PRD queda `OPEN_ASSUMPTIONS`, y el informe dice explícitamente que **la decisión no se ha perdido: está aplazada** al gate de `wf-prd-review`, que la resolverá una a una.

Lo que **no** cambia con este flag: la reapertura del sello (Paso 7) y la traza (Paso 6.C). Un cambio aplicado sin gate sigue sin poder quedar `approved`.

**No uses `--defer-decisions` en una invocación conversacional.** Si el usuario está delante, el gate existe y es obligatorio.
