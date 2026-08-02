# CU-8 — Mantenimiento de features entregadas

**Objetivo:** verificar que el mantenimiento post-entrega triajea **contra el spec**
antes de tocar nada: un bug se clasifica como defecto de código, cambio de spec o hueco
no especificado; y una ambigüedad de un CA descubierta al implementar se aclara sin
re-descender el waterfall, escalando a delta si el comportamiento cambia.
**Proyecto a usar:** un proyecto real con una **feature ya entregada** (spec + tasks,
opcionalmente release, de CU-6) y un bug real (o introducido a propósito).
**Cobertura automática:** la numeración y anotaciones (`sdd-amend.py`) son
deterministas; el triaje es juicio del agente → **manual**.

> [!IMPORTANT]
> **La pregunta del triaje no es "¿cómo lo arreglo?" sino "¿qué dice el spec que
> debería pasar?".** Un bug es una **divergencia entre spec y código**, no un cambio de
> spec. Y una enmienda solo precisa el texto de un CA; si cambia el comportamiento
> esperado, no es enmienda: es delta.

---

## 🧪 Qué se prueba aquí (por componente)

CU-8 es un **objetivo de usuario** (mantenimiento de features entregadas), no una sola
skill: sus escenarios ejercitan **2 componentes**. Marca cada escenario al ejecutarlo. El
estado de cobertura autoritativo (ejes happy/edge/harness/args) vive en
[`ROADMAP.md`](../ROADMAP.md) — esta vista es la **transpuesta** para leer/ejecutar el CU.

### `wf-bug` — triaje de bug contra el spec (`CODE_BUG`/`SPEC_CHANGE`/`UNSPEC`) (5)
- [ ] CU-8.a — Bug que es defecto de código (`CODE_BUG`)
- [ ] CU-8.b — Lo reportado es un cambio de comportamiento (`SPEC_CHANGE`)
- [ ] CU-8.c — Comportamiento no especificado (`UNSPEC`)
- [ ] CU-8.f — Bug: UNSPEC con override de gobernanza y verificación del fix
- [ ] CU-8.g — El gate de triaje corre en el hilo principal y confirma con `AskUserQuestion`

### `wf-spec-amend` — aclaración quirúrgica de un CA ambiguo (back-edge) (2)
- [ ] CU-8.d — Aclarar un CA ambiguo descubierto al implementar (back-edge)
- [ ] CU-8.e — Enmendar un CA que no existe en el spec

---

## CU-8.a — Bug que es defecto de código (`CODE_BUG`)

**Precondición:** una feature entregada cuyo código viola un CA que sí define el
comportamiento esperado.
**Mecanismo:** skill `wf-bug` (orquestador con triaje). Output: registro `B-00X` en
`features/<n>/tasks/<n>_bugs.md`.

1. Le reportas el fallo ("la app crashea cuando…").
   → **Esperado:** localiza la feature y su spec, **contrasta con los CAs** y presenta
     el triaje citando el `CA-XXX` textual; clasifica `CODE_BUG` y **espera tu
     confirmación** antes de actuar.
2. Confirmas.
   → **Esperado:** arregla el código (owner según `stack`), **no toca el spec**, y
     registra `B-00X` trazado al CA.
   → **Delegación síncrona ([[D-043]]):** si delega el fix, lo hace con la tool `Agent` y
     **`run_in_background: false`**, y **espera el reporte** antes de verificar y commitear —
     los subagentes corren en background por defecto. **FALLO:** verificar o commitear sin
     el reporte, sondear el disco para saber si el owner acabó, o relanzarlo. En los logs.

**Resultado:** PASS si triajea contra el CA y arregla sin tocar el spec · FALLO si
parchea sin triaje, edita el spec para un defecto de código, o verifica el fix sin haber
esperado al owner.
**Desviación → reportar:** issue citando `CU-8.a`.

## CU-8.b — Lo reportado es un cambio de comportamiento (`SPEC_CHANGE`)

**Precondición:** lo que esperas es **distinto** de lo que el CA dice.
**Mecanismo:** skill `wf-bug` (triaje) → escala a `wf-spec-delta`.

1. Le reportas como "bug" algo que en realidad cambia lo que la feature debe hacer.
   → **Esperado:** clasifica **`SPEC_CHANGE`** (el "bug" es un cambio de comportamiento
     esperado), **no toca código a ciegas** y te remite a `wf-spec-delta` para
     formalizar el cambio antes de implementar.

**Resultado:** PASS si lo reconoce como cambio de spec y escala a delta · FALLO si
arregla el código cambiando el comportamiento sin pasar por el spec.
**Desviación → reportar:** issue citando `CU-8.b`.

## CU-8.c — Comportamiento no especificado (`UNSPEC`)

**Precondición:** **ningún CA** cubre el comportamiento reportado.
**Mecanismo:** skill `wf-bug` (triaje).

1. Le reportas un comportamiento sobre el que el spec no dice nada.
   → **Esperado:** clasifica **`UNSPEC`** (el spec tiene un hueco) y **formaliza antes**
     (delta para añadir el comportamiento) en vez de arreglarlo en silencio, que
     agrandaría la divergencia documental.

**Resultado:** PASS si detecta el hueco y formaliza antes · FALLO si "arregla" en
silencio un comportamiento no especificado.
**Desviación → reportar:** issue citando `CU-8.c`.

## CU-8.d — Aclarar un CA ambiguo descubierto al implementar (back-edge)

**Precondición:** durante una task descubres que un `CA-XXX` es ambiguo (no que su
comportamiento deba cambiar).
**Mecanismo:** skill `wf-spec-amend` → subagente **`sdd-spec-writer`**; la numeración
`E-00X` y la anotación del plan las escribe **solo** `sdd-amend.py`.

1. Le pides aclarar el CA ("implementando descubrí que el spec no aclara X").
   → **Esperado:** si es **solo aclaración**, corrige el texto del CA con versión menor
     + changelog `E-00X`, y marca el plan con `Enmienda pendiente` (la escribe
     `sdd-amend.py`). El plan **conserva su `Estado:`**; la anotación **retiene
     selectivamente** solo las tasks que referencian ese CA.
2. Lo que describes en realidad **cambia el comportamiento esperado**.
   → **Esperado:** **no enmienda**: escribe el material en `_amend_request.md` y te
     remite a `/wf-spec-delta`. (Caso dudoso = cambio → escala a delta.)

**Resultado:** PASS si aclara sin cambiar comportamiento y retiene solo las tasks del
CA, o escala a delta cuando el comportamiento cambia · FALLO si enmienda un cambio de
comportamiento encubierto, o asigna `E-00X`/anotaciones a mano.
**Desviación → reportar:** issue citando `CU-8.d`.

## CU-8.e — Enmendar un CA que no existe en el spec

**Precondición:** pides aclarar un CA que **no** está en el spec (ID equivocado, o el comportamiento
nunca se especificó).
**Mecanismo:** skill `wf-spec-amend` → Paso 2.1 (verifica que el `### CA-XXX` existe en el spec).

1. Pides "aclara el CA-099" y ese CA no aparece en el spec.
   → **Esperado:** **se detiene**; si es un comportamiento no especificado, remite a `wf-spec-delta`
     (añadir) o a `wf-bug` con triaje `UNSPEC` — no inventa el CA ni lo "enmienda".

**Resultado:** PASS si rechaza el CA inexistente y remite a delta/wf-bug · FALLO si fabrica el CA, o
lo "aclara" sin que exista en el spec.
**Desviación → reportar:** issue citando `CU-8.e`.

## CU-8.f — Bug: UNSPEC con override de gobernanza y verificación del fix

**Precondición:** un bug reportado; según el sub-escenario, un `UNSPEC` (ningún CA lo cubre) o un `CODE_BUG`.
**Mecanismo:** skill `wf-bug` (Paso 4) → Owner; registro `B-00X` vía `sdd-next-id.py`.

1. (`UNSPEC`) Pides arreglarlo igualmente, asumiendo la gobernanza, en vez de formalizar primero.
   → **Esperado:** lo ejecuta como `CODE_BUG` **pero** la entrada `B-00X` lleva `CA: NINGUNO — comportamiento
     no especificado` + `Aviso de gobernanza: fix sin respaldo de spec, pendiente de formalizar`; **nunca** lo registra como si hubiera CA.
2. (`CODE_BUG`) Confirmas un fix.
   → **Esperado:** verifica el fix con **ejecución** (comandos del project_state o runner detectado); si la
     feature tiene tests del CA violado, deben pasar; recomienda (y aplica si aceptas) un test de regresión; el commit es `B-00X [CA-XXX]` acotado.

**Resultado:** PASS si el `UNSPEC` override deja aviso de gobernanza y el `CODE_BUG` se verifica con evidencia +
regresión · FALLO si registra un `UNSPEC` como si tuviera CA, o cierra un fix sin verificación ejecutable.
**Desviación → reportar:** issue citando `CU-8.f`.

## CU-8.g — El gate de triaje corre en el hilo principal y confirma con `AskUserQuestion`

**Precondición:** una feature entregada con un bug reportado (cualquier clasificación).
**Mecanismo:** skill `wf-bug` en el **hilo principal** ([[D-016]]: sin `context: fork`; el gate del
triaje del Paso 3 usa `AskUserQuestion`). Conserva `Agent`: el fix de código se delega al owner (Paso 4).

1. Le reportas el fallo.
   → **Esperado:** presenta el triaje (CA citado + clasificación) y **confirma con `AskUserQuestion`**
     (opciones reales Confirmar / Reclasificar / Cancelar, no texto plano) antes de actuar; el gate se
     renderiza de verdad (no es una ejecución forked que devuelve respuesta genérica).
2. Eliges "Cancelar".
   → **Esperado:** cierra sin tocar código ni spec.

**Resultado:** PASS si el gate de triaje se presenta con `AskUserQuestion` en el hilo principal y el fix
se delega vía `Agent` solo tras confirmar · FALLO si pregunta como texto plano (señal de fork), actúa sin
confirmar, o la ejecución forked no presenta el gate.
**Desviación → reportar:** issue citando `CU-8.g`.

> [!NOTE]
> **El cambio de producto vive en [`cu-07-cambio-producto.md`](cu-07-cambio-producto.md).**
> `wf-prd-change` / `wf-prd-sync-impact` / `wf-prd-change-cascade` nacen del disparador
> de negocio, no del mantenimiento de una feature concreta.
