---
name: wf-spec-gap-resolve
description: "Completa HUs y CAs [INCOMPLETO] desde respuestas ya escritas en un _analysis.md y confirma CAs [INFERIDO] de specs de caracterizacion. Via recomendada para resolver gaps sin tratarlos como delta funcional amplio."
when_to_use: "Activa en frases como 'resuelve estos gaps del spec', 'completa incompletos desde el analysis', 'aplica respuestas del analysis al spec', 'cerrar HUs incompletas', 'confirma los inferidos del spec'."
argument-hint: "<feature_spec.md> [--analysis <analysis.md>] [--inferred 'CA-XXX=confirmado; CA-YYY=incorrecto: <comportamiento real>; CA-ZZZ=no-lo-se']"
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
- `--inferred '<decisiones>'` opcional — las decisiones **ya tomadas con el usuario** sobre los CAs
  `[INFERIDO]`, que es como vuelve la segunda mitad de este flujo ([[D-068]]/[[D-082]]). Formato:
  entradas `CA-XXX=<vía>` separadas por `;`, con una de las tres vías exactas —`confirmado`,
  `incorrecto: <comportamiento real>`, `no-lo-se`—. Ejemplo:
  `--inferred 'CA-003=confirmado; CA-005=incorrecto: reintenta 3 veces antes de fallar; CA-007=no-lo-se'`

  > **Por qué el contrato existe ([[D-082]]).** Este paso decía *"si vienen decididos, aplícalas tal
  > cual"* y no había **por dónde** vinieran: ni argumento que las transportara ni formato que las
  > nombrara. La vuelta del bloqueo quedaba a que el texto libre de la invocación se pareciera lo
  > suficiente. Un `STOP_*` que espera una respuesta necesita el canal por el que esa respuesta
  > entra, o el flujo solo se cierra por casualidad.
  >
  > **Un `CA-XXX` que no esté `[INFERIDO]` en el spec no se toca**: dilo y sigue con los demás. Y
  > una vía mal escrita **no se interpreta** —`no-lo-se` no es `incorrecto`—: para y pide que se
  > reformule. Adivinar aquí es decidir por el usuario sobre comportamiento de producción.

Si falta el spec:
> "Necesito el spec cuyas historias incompletas hay que completar."

## Paso 2: Verificar archivos

Comprueba que el spec existe y termina en `_spec.md`.

**Y que la feature sigue viva ([[D-078]]):**

```bash
!grep -Eq '^[[:space:]]*[-*>]?[[:space:]]*\*{0,2}Estado:?\*{0,2}[[:space:]]*:?[[:space:]]*RETIRADO' "<path_spec>" && echo RETIRADO || echo VIGENTE
```

`RETIRADO` → detén sin tocar nada e informa con la traza `Retirada:` delante. Los gaps de una feature
dada de baja no bloquean nada que vaya a ejecutarse, y el `--unseal` del Paso 6 la devolvería al
producto en silencio. Reactivarla es una decisión aparte; completar sus HUs no la toma.

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

Los `[INFERIDO]` no se resuelven desde un `_analysis.md`: la fuente de confirmación es el usuario (o
evidencia nueva que aporte). **Tú no puedes recogerla**: corres en `context: fork` y no tienes turno
en el que preguntar ([[D-068]]).

**Si el spec tiene CAs `[INFERIDO]` sin confirmar y no vienen decididos en `--inferred`**, aplica
todo lo demás que sí puedas resolver y **cierra devolviendo el bloqueo** con veredicto operativo
`STOP_INFERIDO_SIN_CONFIRMAR`. Por cada uno, dale a quien te lanzó lo que necesita para presentarlo:
el ID del CA, el comportamiento deducido **verbatim**, su `Confirmación pendiente` y la evidencia
parcial que tenga. **Las tres vías las presenta quien puede preguntar**, no tú:

- **Confirmado** → se elimina el marcador y `Evidencia:` pasa a `confirmado por <usuario> el <fecha>` (la evidencia parcial original se mantiene).
- **Incorrecto** → el CA se corrige con el comportamiento real que indique el usuario (con su nueva evidencia si la aporta), o se elimina si la capacidad no existe.
- **No lo sé** → el marcador se queda; ese CA sigue bloqueando el plan (regla de `kb-spec-characterization`).

**Si vienen decididos en `--inferred`** (quien te lanza ya los resolvió con el usuario), aplica cada
vía tal cual sobre el CA que nombra, y **enumera en tu informe qué hiciste con cada uno** — incluidos
los `no-lo-se`, que siguen bloqueando. Los `[INFERIDO]` que **no** aparezcan en `--inferred` siguen
sin confirmar: vuelve a devolverlos con el mismo veredicto, no los des por resueltos porque la
invocación traía otros. Lo que **nunca** haces es decidir tú: si no puedes preguntar, no puedes
decidir — el mismo invariante que rige la anti-fabricación ([[D-063]]).

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

### 5.1 — Lo que completes más allá de la respuesta va marcado ([[D-063]])

Una respuesta a un gap casi nunca trae **todo** lo que hace falta para cerrar la HU. Lo que falte
lo pones tú, y ahí es donde entra la fabricación silenciosa: el gap se cierra, el `[INCOMPLETO]`
desaparece, el spec queda impecable — y contiene decisiones que nadie tomó.

**La regla es la misma de la generación, y no caduca porque el spec ya exista** (SSoT:
`kb-gap-conventions`, "La obligación de marcar rige cada escritura"): **lo que escribas y no trace
a la respuesta, al spec vigente o al PRD es una asunción y va con su `[A-00X]` en
`## Asunciones Aplicadas`**, citando de dónde sale. Si la sección no existe, créala arrancando en
`A-001`; si existe, continúa desde el ID más alto.

Las dos escapatorias que hay que nombrar porque se sienten inocentes:

- **Ajustar un CA vecino "para que no quede contradictorio" con la respuesta nueva es una decisión,
  no higiene.** Ajustarlo está bien; ajustarlo sin marca, no.
- **No difieras a Design ni a Plan una decisión de alcance.** Dejar el detalle fino para la fase
  siguiente mientras resuelves por tu cuenta qué hace la feature es diferir lo pequeño y decidir lo
  grande.

Y **no confundas marcar con decidir**: si lo que falta no es un detalle sino una bifurcación real
del producto, no la marques — es el Paso 4, y se detiene. Corres sin poder preguntar, así que
tampoco puedes decidir; marcar es para lo conservador y menor, parar es para lo demás.

> **Verificación mecánica, para que no dependa de tu criterio.** Al sellarse el spec,
> `sdd-seal.py spec --check` deniega si un gap `[INFORMATIVO]` sin responder no tiene entrada que
> lo cite ([[D-063]]). No juzga si tu asunción es buena —eso no es mecanizable—: exige que sea
> **visible**.

## Paso 6: Versionado y trazabilidad

> **Al modificar un spec, su validación se reabre ([[D-061]]).** Tras escribir, ejecuta:
> ```bash
> !python3 .sdd/scripts/sdd-seal.py spec "<path_del_spec>" --unseal
> ```
> Degradar a `BORRADOR` siempre es seguro y siempre es correcto: lo que se validó ya no es lo que
> hay. Es la misma norma que en el PRD, donde un cambio reabre el sello ([[D-028]]).

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
