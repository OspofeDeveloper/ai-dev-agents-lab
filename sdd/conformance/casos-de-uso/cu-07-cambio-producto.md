# CU-7 — Cambiar el producto y propagar el cambio

**Objetivo:** verificar que un cambio de producto se gestiona con traza
(clasificación, changelog, CR), que medir su impacto aguas abajo es read-only y
conservador, y que la cascada propaga el cambio parando solo en los checkpoints
humanos reales.
**Proyecto a usar:** un proyecto real con un PRD ya `LISTO` (CU-2) y artefactos
derivados (specs, plans, de CU-3/CU-6), sobre el que introduzcas un cambio de alcance
real.
**Cobertura automática:** el pre-pass de hash de `wf-prd-sync-impact` está cubierto
por `sdd/tests/test_sdd_sync_check.py`; la clasificación del cambio y la conducta de
la cascada son juicio del agente → **manuales**.

> [!IMPORTANT]
> **Distinción rectora.** Una `CLARIFICATION` no toca el PRD ni dispara sync. Solo un
> cambio de producto real (`BEHAVIOR`/`SCOPE`/`PRIORITY`/`DEPRECATION`) abre traza y
> se propaga. La gobernanza la aplica `prd-expert` con `kb-product-change-governance`.

---

## 🧪 Qué se prueba aquí (por componente)

CU-7 es un **objetivo de usuario** (cambiar el producto y propagar el cambio), no una
sola skill: sus escenarios ejercitan **5 componentes** del subsistema de cambio de
producto. Marca cada escenario al ejecutarlo. El estado de cobertura autoritativo (ejes
happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) — esta vista es la
**transpuesta** para leer/ejecutar el CU.

### `wf-prd-change` — gestionar un cambio de producto (4)
- [ ] CU-7.a — Un cambio que es solo aclaración (CLARIFICATION)
- [ ] CU-7.b — Un cambio de producto real + reapertura del sello (D-028)
- [ ] CU-7.c — Expansión de capacidad disfrazada de aclaración (Regla 4.1)
- [ ] CU-7.n — El gate del cambio: clasificación confirmada y bifurcación resuelta por el humano (D-040)
- [ ] CU-7.o — Una capacidad sale del producto: `DEPRECATION`, no `SCOPE_CHANGE` (D-074)

### `wf-spec-retire` — dar de baja la feature (3) ⏱ **sin pasada**
- [ ] CU-7.p — La baja se confirma con el impacto delante, y el estado lo estampa el script (D-074)
- [ ] CU-7.q — Nadie retira desde un fork: sync-from-prd lo señala y no lo aplica (D-074)
- [ ] CU-7.s — Volver: la reactivación es la única vuelta atrás, y no restaura sellos (D-074/D-078)

> ⏱ **`wf-spec-retire` nace sin medir** ([[D-074]]). Estos tres escenarios están escritos y **no
> ejecutados**; la fila del ROADMAP es `PENDIENTE`. Y ojo con el alcance: **CU-7.p no puede medir
> aquí el bloqueo aguas abajo** —el proyecto de CU-7 arranca sin plan ni tasks—, así que la
> denegación de generar y ejecutar tareas sobre una feature retirada se mide sobre el proyecto de
> CU-6, donde sí hay cadena completa.

> ⚠ **[[D-040]] reinicia el recuento conductual de este bloque (2026-07-30).** `wf-prd-change` deja de
> ser `context: fork` y pasa al hilo principal con **gate obligatorio**; el `prd-expert` analiza
> read-only y escribe por delegación; la cascada, que entonces no podía heredar el gate, la invocaba
> con `--defer-decisions` —flag **retirado en [[D-075]]**, porque desde que la cascada corre en el
> hilo principal el gate se presenta dentro de ella—. Las pasadas de
> CU-7.b hechas antes (1 y 2, 2026-07-30) midieron la **arquitectura vieja**: quién clasifica, quién
> pregunta y quién llama a `--reopen` son otros ahora, así que su evidencia conductual **no cuenta**.
> Lo único que sobrevive es la del probe **2bis** ([[D-039]]), porque marcar las inferencias lo hace el
> `prd-expert`, que sigue siendo subagente. Al re-probar, CU-7.a y CU-7.c también cambian de mecanismo
> (su clasificación pasa a estar tras el gate).

### `wf-prd-sync-impact` — medir impacto aguas abajo (2)
- [ ] CU-7.d — Matriz de impacto por artefacto
- [ ] CU-7.e — Criterio conservador

### `wf-prd-change-cascade` — propagar el cambio por el pipeline (7)
- [ ] CU-7.f — Cascada normal (auto + paradas reales)
- [ ] CU-7.g — La cascada con un cambio que es solo aclaración
- [ ] CU-7.h — Cascada sin un cambio que propagar
- [ ] CU-7.i — Features no triviales en el conjunto STOP
- [ ] CU-7.j — `--dry-run` / `--review-before-apply` no escriben
- [ ] CU-7.k — Profundidad adaptativa y degradación con gracia
- [ ] CU-7.r — El cascade no redacta el informe de sus delegados ni enseña comandos (D-060/D-075)

### `wf-spec-sync-from-prd` — resincronizar specs tras el cambio (2)
- [ ] CU-7.l — Analizar y aplicar la resincronización de specs
- [ ] CU-7.m — Resincronización que rebasa un delta razonable

> **Capa determinista**: el pre-pass de hash de `wf-prd-sync-impact`
> (`sdd-sync-check.py`) está cubierto por `sdd/tests/test_sdd_sync_check.py`; aquí se
> verifica solo la **conducta del agente** (clasificación del cambio y conducta de la
> cascada).

---

## `wf-prd-change` — gestionar un cambio de producto

> **Mecanismo común (actualizado por [[D-040]]):** skill `wf-prd-change` en el **hilo principal**
> (`allowed-tools: [Bash, Agent, AskUserQuestion]`, **sin `Read`/`Write`**) → **gate obligatorio** de
> clasificación + bifurcaciones → subagente **`prd-expert`** (+ `kb-product-change-governance`), que
> analiza read-only **antes** del gate y escribe **después**. La reapertura del sello la ejecuta main
> por script (`sdd-prd-apply.py --reopen`). Output según clasificación: nada / PRD actualizado +
> `product-changelog.md` + `changes/CR-XXX/{change-request,decision}.md`.
>
> Antes de [[D-040]] la skill era `context: fork`: clasificaba, decidía el alcance y escribía sin punto
> de intervención humana. **El detalle del gate vive en CU-7.n**; los casos de abajo dan por supuesto
> que existe.

### CU-7.a — Un cambio que es solo aclaración (CLARIFICATION)

**Precondición:** el cambio no contradice el PRD ni mueve alcance.
**Mecanismo:** `wf-prd-change` → `prd-expert` (clasificación) → **gate**: el usuario confirma
que es solo una aclaración ([[D-040]]). Que no se toque el PRD deja de ser decisión del
agente y pasa a ser decisión confirmada.

1. Le describes un cambio que en realidad solo aclara algo ya comprometido.
   → **Esperado:** clasifica `CLARIFICATION`, **no reescribe el PRD**, recomienda
     `wf-spec-gap-resolve` o `wf-spec-delta` según el artefacto afectado y **se
     detiene** (no resincroniza).

**Resultado:** PASS si no toca el PRD ni abre CR · FALLO si edita el PRD o abre
`changes/CR-XXX/` para una aclaración.
**Desviación → reportar:** issue citando `CU-7.a`.

### CU-7.b — Un cambio de producto real (y la reapertura del sello, D-028)

**Precondición:** un PRD ya **sellado** (`status: approved`, `Aprobado por:` relleno — el
estado natural tras pasar la review) y un cambio que altera alcance, reglas o prioridades.
**Mecanismo:** `wf-prd-change` → `prd-expert`. La **reapertura del sello** la hace
`wf-prd-change` (Paso 5), pero **no re-sella**: el sello solo lo restablece `wf-prd-review`.

1. Le describes un cambio que mueve el alcance ("ahora también quiero compartir gastos en
   grupo con otras personas").
   → **Esperado:** actualiza versión/fecha y **solo** las secciones afectadas del PRD;
     registra `product-changelog.md` + `changes/CR-XXX/`; recomienda `wf-prd-sync-impact`.
2. **Reapertura del sello ([[D-028]]/[[D-032]]):** como el PRD estaba sellado (`status: approved`),
   tras aplicar el cambio `wf-prd-change` llama a `sdd-prd-apply.py --reopen` — baja `status:` a
   `in-review` y **resetea `Aprobado por:` al placeholder pendiente** (el sello no puede certificar
   un contenido que ya cambió), y remite a `wf-prd-review`.
   → **Esperado (verificable):** `sdd-prd-ready.py` sobre el PRD cambiado da `UNSEALED`
     (o `OPEN_ASSUMPTIONS` si el cambio introdujo nuevas `[ASUNCIÓN]`), **nunca `READY`**;
     `status: in-review` y `wf-prd-change` **no** escribe un `Aprobado por:` nuevo.
2bis. **Anti-fabricación del cambio ([[D-039]]).** Un cambio casi nunca llega completo. Todo lo que
   `wf-prd-change` escriba y **no trace** al `--new-reqs` o a lo que dijo el usuario va con marca
   inline `[ASUNCIÓN]` + entrada `[ASN-XXX]` (formato e invariante 1:1 de `kb-prd-expert`),
   recreando la sección si un review anterior la eliminó.
   → **Esperado:** el PRD queda `OPEN_ASSUMPTIONS` y el `change-request.md` recoge el **texto** de
     cada asunción introducida. `wf-prd-change` **no** las resuelve (es `context: fork`: no puede
     preguntar, así que no puede decidir); las resuelve el gate de `wf-prd-review` en el paso 3.
   → **FALLO (observado, origen de [[D-039]]):** escribir contenido inferido **sin marca**. Dos
     formas, ambas vistas: (a) una capacidad más amplia que la pedida ("consultar" cuando solo se
     pidió "marcar"); (b) **estrechar o reinterpretar una exclusión o regla transversal existente**
     para que no contradiga la capacidad nueva — se cuela porque se siente como higiene, pero elegir
     dónde queda la frontera es alcance que el usuario no ha dicho. Agravante del mismo fallo:
     **diferir a Spec lo pequeño mientras se decide lo grande** ("¿el total agregado?" a
     `wf-spec-analyze`, la frontera fiscal por su cuenta).
   → **Cómo se verifica:** `grep -c "\[ASUNCIÓN" <prd>` > 0 cuando el cambio no venía completo. Ojo:
     **el check mecánico no delata este fallo** — sin marcas, `sdd-prd-ready.py` da `0 = 0`,
     `one_to_one: true`, y el review posterior declara `LISTO` sobre contenido fabricado. Hay que
     leer el `diff` y preguntarse qué de lo escrito estaba en la petición.
3. Vuelves a pasar `wf-prd-review` sobre el PRD cambiado y lo apruebas.
   → **Esperado:** el sello se restablece **solo aquí**, re-capturando la identidad (D-027)
     y con la fecha del cambio; el `Aprobado por:` vuelve a estar relleno.

**Resultado:** PASS si toca solo lo afectado, deja traza completa, **reabre el sello** al
cambiar (queda `in-review` / `UNSEALED`) y solo `wf-prd-review` lo re-sella · FALLO si
reescribe secciones intactas, mete tecnología, no deja traza, **o deja el PRD `approved`
con un `Aprobado por:` que certifica el contenido viejo** (el agujero que cierra D-028).
**Desviación → reportar:** issue citando `CU-7.b`.

> **Pasada 1 (2026-07-30, v0.74.0+`c7ff537`) — PASS en los tres pasos. Primera medición conductual de
> [[D-028]]/[[D-032]]/Q4**, implementados desde v0.69.0 y hasta ahora solo verificados por script.
> Fixture: `prd/.prd-sealed.bak` (v1.0 aprobado, READY). Cambio pedido en conversación: *"ahora también
> quiero poder compartir gastos en grupo con otras personas"* — elegido a propósito porque **choca de
> frente** con el pilar más repetido del PRD (uso individual, presente en Puntos Clave + exclusión +
> regla transversal).
>
> **Paso 1 — alcance del cambio.** `wf-prd-change` **paró antes de escribir** para resolver una
> bifurcación real: (a) reparto local single-user vs (b) colaboración multiusuario. Es la Regla 12
> anti-fabricación aplicada a un cambio en vez de a una asunción. Elegida (a), el `diff` contra el
> fixture da **4 hunks y nada más**: frontmatter, capacidades del actor, sección de deudas y la
> exclusión de multiusuario. **Lo verificado no es el diff, es dónde NO tocó:** bajo (a) el "uso
> estrictamente individual" del resumen y la regla transversal siguen siendo verdad, y los dejó
> intactos — matizó la **exclusión** en vez de degradar el pilar. Tampoco fabricó el método de reparto
> (partes iguales vs importes): lo dejó como hueco de Spec.
>
> **Paso 2 — reapertura del sello, verificada en el fichero (no en la narración):** `status: approved`
> → `in-review`, `Aprobado por:` de vuelta al placeholder en **una sola línea**, `sdd-prd-ready.py` →
> `UNSEALED` (exit 2, `sealed: false`, `approved_by: null`), **nunca `READY`**. `wf-prd-change` **no**
> escribió sello nuevo. Traza completa: `product-changelog.md` + `changes/CR-001/{change-request,
> decision}.md`, con la bifurcación (a)/(b) y por qué se descartó (b). El agujero que [[D-028]] existía
> para cerrar —quedarse `approved` certificando contenido viejo— no se produjo.
>
> **Paso 3 — re-sello.** Solo `wf-prd-review` lo restableció: `READY`, `status: approved`,
> `Aprobado por: Oscar Pozo Fernandez (2026-07-30)`. El `diff` final contra el fixture v1.0 es
> **exactamente** el CR-001; la línea del sello queda byte-idéntica a la original y `version: 1.1` /
> `updated:` se conservan (el review no los resetea). Veredicto `LISTO` por [[D-035]] con mapeo
> determinista explícito.
>
> **Recuento: 1/3** (conductual → Regla 9). Ramas **sin ejercitar**: (i) un cambio que introduzca
> `[ASUNCIÓN]` nuevas → `OPEN_ASSUMPTIONS` y gate antes de re-sellar; (ii) la interpretación (b), el
> pivote real → comprobar que **sí** reescribe los pilares cuando toca (el inverso de esta pasada:
> aquí se midió que no sobre-edita, falta medir que no sub-edita).
>
> **Hallazgo 1 — `updated:` no es campo sancionado.** `sdd-prd-frontmatter.py` valida
> `REQUIRED = (type, product, version, created, status)` y `updated` **no aparece en ninguna parte del
> ecosistema**. El `prd-expert` lo añadió tras comprobar que las claves extra no rompen el validador —
> cuidadoso, pero *tolerado por el validador* ≠ *declarado por la convención*. El ecosistema no tiene
> sitio declarado para "cuándo se cambió este PRD por última vez": o lo declara el template, o la fecha
> vive solo en el changelog. Candidato menor.
>
> **Hallazgo 2 — `--new-reqs` es "obligatorio" y se saltó sin consecuencia.** El SKILL lo exige en el
> `argument-hint`, en precondiciones (*"`--new-reqs <archivo.md>` obligatorio"*) y tiene mensaje de uso.
> El orquestador pasó el cambio como **string inline**; el `prd-expert` lo detectó (*"llegó como texto
> inline, no como `--new-reqs`"*) y continuó igual. Misma familia que el `allowed-tools`: **una
> declaración que no ata**. Aquí el texto de la petición es la SSoT de qué se pidió y sobrevivió solo
> porque el experto decidió capturarlo en el `change-request.md`. Dos arreglos posibles y opuestos: que
> el orquestador materialice el input oral en fichero (lo que mide CU-11.g) o que el SKILL legitime el
> texto inline. Hay que **elegir uno**.
>
> **No hallazgo, verificado:** las escrituras del `prd-expert` en `.claude/agent-memory/prd-expert/`
> son capacidad **declarada** (`memory: project` en el frontmatter del agente), no un efecto lateral
> inventado; persistió la bifurcación sin decidir y la actualizó al aplicarla, que es la higiene
> correcta. Sí queda como hueco: **ningún caso de conformance cubre ese mecanismo** — los agentes
> escriben en el repo del consumidor y el `ROADMAP.md` no les da fila (su alcance es solo `wf-*`).
>
> **Superado por [[D-041]] (2026-08-02):** la capacidad ya no existe — ningún agente declara
> `memory:`. Lo que aquí se anotó como "higiene correcta" resultó ser, medido en CU-3.a, un
> **segundo contrato invisible**: la memoria del `sdd-spec-explorer` llegó a instruir a las pasadas
> futuras. El hueco de cobertura que este párrafo señalaba se cierra por retirada del mecanismo, no
> por añadirle un caso.
>
> **Pasada 2 (2026-07-30, v0.74.0) — FALLO en 2bis → origen de [[D-039]].** Cambio pedido:
> *"quiero poder marcar algunos gastos como deducibles para cuando toque hacer la declaración"* —
> elegido **deliberadamente incompleto** (no dice quién define qué es deducible, ni si implica un
> informe) para provocar `[ASUNCIÓN]` nuevas. **No las produjo: 0 marcas.** Y no por juicio, sino
> porque `wf-prd-change` **no mencionaba `[ASUNCIÓN]`, `[ASN-XXX]`, la Regla 12 ni la anti-fabricación
> en ningún sitio** — la rama `OPEN_ASSUMPTIONS` que este probe describía **ningún camino de código
> podía producirla** (error del probe, corregido arriba con el paso 2bis).
>
> Lo que escribió sin marca: (a) *"El Usuario puede **consultar** el conjunto de gastos marcados como
> deducibles"* cuando solo se pidió *marcar*; (b) **estrechó la exclusión fiscal** de "Informes o
> exportaciones fiscales/contables: fuera del alcance" a "Generación de informes… **en formatos
> oficiales para la Agencia Tributaria**: fuera… El Usuario puede marcar y consultar dentro de la
> aplicación, pero la aplicación no produce el documento ni el fichero". Dónde queda esa frontera
> —etiquetar vs ayudar a declarar— es alcance que el usuario nunca dijo. Verificado en el fichero:
> `inline_marks: 0`, `asn_entries: 0`, `one_to_one: true`, `UNSEALED` → el review habría declarado
> `LISTO` sobre contenido fabricado.
>
> **Lo bien hecho igualmente:** reapertura del sello correcta otra vez (`in-review`, placeholder,
> `UNSEALED`), diff acotado a lo afectado, traza completa. El fallo es de **anti-fabricación**, no de
> [[D-028]]/[[D-032]], que siguen 2/2.
>
> **Y el hallazgo estructural detrás:** `wf-prd-change` es `context: fork` con
> `allowed-tools: [Read, Write, Bash]` — **sin gate humano, por declaración**, y su Paso 5 dice
> literalmente "proponer **y aplicar**". La pasada 1 solo tuvo gate porque el agente **se salió del
> guion** (paró, reportó la bifurcación) y main improvisó la pregunta y lo reanudó. Eso es 1 de 2:
> una garantía que depende de que el agente improvise no es garantía. `sdd-structural-lint` lo dice
> con su propio mensaje al detectar `FORK-ASKUSER-CONFLICT`: *"quita `context: fork` — la skill
> interactiva corre en el hilo principal y delega el trabajo pesado vía `Agent`"*. Es la **pieza 2**
> de [[D-039]] (re-arquitecturar al modelo de `wf-prd-review`), decidida y pendiente, con su propia
> re-prueba de CU-7.
>
> **Contaminación del banco de pruebas, corregida:** los fixtures `.prd-*.bak` vivían en `prd/`, el
> `prd-expert` los leyó, diffeó uno y se lo reportó al usuario como "andamiaje que conviene limpiar".
> Movidos a `.conformance-attic/`. Igual la memoria del agente (`memory: project`), que recordaba un
> CR-001 ya revertido. **Probe no diseñado que sale de aquí:** ¿confía un agente en su memoria por
> encima del artefacto? Nada lo mide hoy; va junto al hueco de cobertura de `agent-memory`.
> — **Cerrado por retirada ([[D-041]], 2026-08-02):** ningún agente declara ya `memory:`, así que
> no hay memoria en la que confiar y el probe queda sin objeto. La lección **sí** sobrevive, y es
> más general: lo que un agente escribe **fuera del artefacto** contamina las pasadas siguientes.
> Está recogida como punto 6 de la Regla 9 de `kb-sdd-conformance` (aislar cada pasada).
>
> **Refinamiento de un candidato abierto:** el brief que main improvisa para el `prd-expert` incluyó
> aquí *"Contexto adicional: este PRD acaba de ser modificado por CR-001… presta atención especial a
> que Fuera del Alcance y las reglas transversales sigan coherentes"* — y esa adaptación es justo lo
> que hizo bueno el diagnóstico. Así que el candidato "fijar la plantilla del brief" (nacido de la
> deriva de la taxonomía de impacto en CU-2.j) debe **re-acotarse**: fijar solo el **eje de taxonomía**,
> dejando libre la parte contextual. Congelar el brief entero perdería esto.

### CU-7.c — Expansión de capacidad disfrazada de aclaración (Regla 4.1)

**Precondición:** la "aclaración" introduce una entidad/catálogo/flujo/owner nuevo no
comprometido.
**Mecanismo:** `wf-prd-change` → `prd-expert` (reclasificación por Regla 4.1).

1. Le presentas como simple aclaración algo que en realidad añade capacidad nueva.
   → **Esperado:** lo **reclasifica** como `BEHAVIOR_CHANGE` o `SCOPE_CHANGE` (no basta
     `CLARIFICATION`) y lo trata como cambio de producto con su traza.

**Resultado:** PASS si reclasifica y deja traza · FALLO si lo deja pasar como
aclaración y expande el alcance en silencio.
**Desviación → reportar:** issue citando `CU-7.c`.

> **Mecanismo actualizado por [[D-040]]:** la reclasificación sigue siendo del `prd-expert`, pero ahora
> se **presenta en el gate** del Paso 5 y el usuario la confirma. Ojo al verificar: el PASS no es "el
> orquestador la reclasificó", es "el experto la reclasificó **y el humano la vio**". Y el FALLO gana
> una forma nueva: que main **sustituya** la clasificación del experto por la suya (prohibido por
> [[D-038]]) en vez de presentarla.

### CU-7.n — El gate del cambio: clasificación confirmada y bifurcación resuelta por el humano ([[D-040]])

**Precondición:** un PRD sellado y una petición de cambio que **admite dos lecturas** con
impacto de alcance distinto (p. ej. "quiero compartir gastos en grupo" → reparto local
single-user *vs* colaboración multiusuario real; o "quiero marcar gastos deducibles" →
solo etiquetar *vs* que la app ayude a declarar). Todo por conversación, sin teclear `/wf-*`.
**Mecanismo ([[D-040]]):** `wf-prd-change` corre en el **hilo principal** (`AskUserQuestion`),
el `prd-expert` analiza **read-only** en el Paso 4 y escribe por delegación en el Paso 6.
Antes era `context: fork`: no podía preguntar, así que clasificaba, decidía el alcance y
escribía sin punto de intervención humana.

**A — el análisis no escribe**
   → **Esperado:** el Paso 4 devuelve clasificación, severidad, secciones afectadas,
     bifurcaciones y asunciones que propondría, **sin tocar el PRD**. Verificable: entre el
     Paso 4 y el gate, `diff` contra el fixture → **byte-idéntico**.
   → **FALLO:** llegar al gate con el PRD ya editado. No se pide permiso sobre lo ya escrito.

**B — el gate existe y es único**
   → **Esperado:** **un** `AskUserQuestion` en el hilo principal que agrupa la clasificación
     (con el razonamiento del experto y su consecuencia práctica: se edita el PRD o no) **y**
     cada bifurcación de alcance surfaceada.
   → **FALLO:** no preguntar; o preguntar solo la clasificación dejando la bifurcación
     decidida; o trocearlo en varios gates sucesivos por el mismo cambio.

**C — siempre, sin excepción por trivialidad**
   → **Esperado:** el gate salta también en cambios pequeños y sin ambigüedad aparente.
   → **FALLO:** saltárselo "porque estaba claro". Decidir *cuándo* preguntar es el juicio que
     falló 1 de 2 pasadas antes de [[D-040]]; un gate a criterio del agente no es un gate.

**D — el humano puede corregir la clasificación, main no**
   → **Esperado:** si el usuario dice "esto era solo una aclaración" (o lo contrario), manda —
     es el product owner. Pero main **presenta** la clasificación del experto, no la sustituye
     por la suya ni enruta contra él ([[D-038]]).
   → **FALLO:** main reclasificando por su cuenta, en cualquier dirección.

**E — main no lee ni escribe el artefacto**
   → **Esperado:** en los logs, **ningún** `Read`/`Edit`/`Write` sobre el PRD desde el hilo
     principal. La edición y la traza las escribe el `prd-expert` por delegación; lo único que
     main ejecuta sobre el fichero es `sdd-prd-apply.py --reopen` por `Bash`.
   → **Ojo al verificar:** que el frontmatter declare `allowed-tools: [Bash, Agent,
     AskUserQuestion]` **no lo impide** — el campo es declarativo, no una jaula (comprobado en
     CU-2.j pasada 3). Hay que mirar los logs.

**F — la traza registra que la decisión fue humana**
   → **Esperado:** `change-request.md` recoge la clasificación **y quién la confirmó**, el
     **texto literal** de la petición (venga de fichero o de conversación), y **las
     bifurcaciones planteadas con cuál se eligió y por qué**.
   → **FALLO:** una traza que no permita distinguir una decisión humana de una del agente.

**G — el gate no tiene modo de escape ([[D-075]])**
   → **Precondición:** invocación **desde la cascada** (`wf-prd-change-cascade`), que desde
     v0.109.0 corre en el hilo principal.
   → **Esperado:** el gate se presenta **igual que en una invocación conversacional** — las
     instrucciones de esta skill entran en la misma conversación que la cascada, así que el
     `AskUserQuestion` llega al usuario. No hay diferencia observable entre venir del cascade y
     venir de una petición directa.
   → **FALLO:** que exista cualquier vía de omitir el Paso 5 (un flag, una rama "si me invoca
     otro workflow"), o que la clasificación se dé por confirmada sin que nadie la confirme.
   → **Nota de historia:** hasta v0.108.x existía `--defer-decisions` para esto, porque la
     cascada era un fork sin turno. Si lo ves reaparecer en el árbol, es una regresión.

**Resultado:** PASS si (A) el análisis no escribe, (B) hay un gate único en main, (C) salta
siempre, (D) el humano decide y main no reclasifica, (E) main no toca el fichero salvo por
script, (F) la traza distingue decisión humana de decisión del agente, y (G) el gate llega igual
cuando quien invoca es el cascade · FALLO ante gate ausente u opcional, PRD editado antes del gate,
main reescribiendo, o bifurcación resuelta en silencio. Conductual → validar ×3 (Regla 9).
**Desviación → reportar:** issue citando `CU-7.n`.

---

## `wf-prd-sync-impact` — medir impacto aguas abajo

> **Mecanismo común:** skill `wf-prd-sync-impact` (vive en la fase **spec**) →
> subagente **`sdd-spec-auditor`**. **Read-only.** Pre-pass determinista
> `sdd-sync-check.py check-all <dir> --mark`. Output: `<basename>_sync_report.md`.

### CU-7.d — Matriz de impacto por artefacto

**Precondición:** un PRD cambiado con artefactos derivados (analysis, discovery,
features, specs, plans, tasks).
**Mecanismo:** `wf-prd-sync-impact` → `sdd-spec-auditor` + `sdd-sync-check.py`.

1. Tras cambiar el PRD, le pides ver qué quedó desactualizado aguas abajo.
   → **Esperado:** produce `<basename>_sync_report.md` con estado por artefacto
     (`in_sync` / `needs_review` / `stale` / `unknown`) + motivo + acción recomendada.
     Un spec que el script reporta `DERIVA` queda **al menos** `needs_review`. **No
     modifica** ningún artefacto.

**Resultado:** PASS si reporta sin tocar nada y respeta la deriva por hash · FALLO si
modifica artefactos, o marca `in_sync` algo con deriva detectada.
**Desviación → reportar:** issue citando `CU-7.d`.

### CU-7.e — Criterio conservador

**Precondición:** un artefacto sin metadata ni evidencia suficiente para decidir.
**Mecanismo:** `wf-prd-sync-impact` → `sdd-spec-auditor`.

1. Le pides el impacto con algún artefacto sin metadata de procedencia.
   → **Esperado:** lo marca `unknown` (revisión manual), **nunca** `in_sync` por
     optimismo.

**Resultado:** PASS si marca `unknown` lo que no puede demostrar · FALLO si asume
sincronía sin poder demostrarla.
**Desviación → reportar:** issue citando `CU-7.e`.

---

## `wf-prd-change-cascade` — propagar el cambio por el pipeline

> ⚠ **Este bloque se reescribió dos veces por la misma causa, y la segunda la cerró ([[D-040]]
> 2026-07-30 → [[D-075]] 2026-09-14).** La cascada declaraba cuatro **checkpoints humanos** siendo
> `context: fork`: ninguno era presentable. D-040 solo pudo desmentir el primero —el cambio pasó a
> invocarse con `--defer-decisions`, aplazando la decisión— porque arreglar el resto exigía sacar la
> cascada del fork, y eso quedó anotado allí mismo como *candidato aparte*. **D-075 lo ejecuta:** la
> cascada corre en el hilo principal, delega los workers por la tool `Agent` y sostiene sus gates con
> `AskUserQuestion`. Al re-probar CU-7.f–k, lo que cambia de forma: los checkpoints **se preguntan**
> (antes, en el mejor de los casos, se reportaban), el gate de clasificación de `wf-prd-change` llega
> al usuario **dentro** de la pasada, y **no hay `_cascade_report.md`**. Lección transversal, ahora
> con dos iteraciones de evidencia: **un checkpoint declarado en prosa no es un checkpoint si la
> arquitectura no puede sostenerlo** — al auditar paradas, comprobar quién puede preguntar.

> **Mecanismo común:** skill `wf-prd-change-cascade` → **orquestador en el hilo principal**
> (sin `context: fork`, con `AskUserQuestion`; [[D-075]]). Invoca `wf-prd-change` con el
> `Skill` tool —corre en main igual que ella, así que su gate se presenta— y delega los
> workers por la tool `Agent` con `run_in_background: false`: `wf-prd-sync-impact` y
> `wf-spec-conflict`/`wf-spec-readiness` en `sdd-spec-auditor`, `wf-spec-sync-from-prd`
> analyze/apply en `sdd-spec-writer`, `wf-design-sync` en `design-system-architect`.
> **Sin artefacto de salida propio:** el resumen por fase se presenta en la conversación
> ([[D-060]]). Flags: `--review-before-apply`, `--dry-run`, `--features`, `--skip-design`.

### CU-7.f — Cascada normal (auto + paradas reales)

**Precondición:** un cambio de producto real para propagar.
**Mecanismo:** `wf-prd-change-cascade`.

1. Le pides propagar el cambio por todo el pipeline, hablando.
   → **Esperado:** corre lo mecánico read-only, **auto-aplica** los deltas inequívocos
     (`severidad: minor` + `acción: delta`), y **pregunta** en los checkpoints humanos que
     apliquen: clasificación del cambio (la sostiene `wf-prd-change` dentro de la misma
     conversación), features no triviales, decisiones de Design, revalidación de plan. Cada
     pregunta llega como `AskUserQuestion` y **se resuelve en el mismo turno**: no hay
     relanzado ni "vuelve a pedírmelo con el flag".
   → **Esperado (cierre):** presenta un resumen por fase distinguiendo ejecutado / parado /
     omitido, y dice **qué specs quedaron en `BORRADOR`** por haberse resincronizado.
   → **FALLO adicional:** que aparezca un `<basename>_cascade_report.md` en disco — el
     orquestador no redacta el informe de sus delegados ([[D-060]], y ver CU-7.r).

**Resultado:** PASS si auto-aplica solo lo inequívoco y **pregunta** en los checkpoints reales
· FALLO si aplica cambios `major` solos, si no para en un checkpoint real, o si un checkpoint
se "presenta" como texto informativo sin preguntar nada.
**Desviación → reportar:** issue citando `CU-7.f`.

### CU-7.g — La cascada con un cambio que es solo aclaración

**Precondición:** `wf-prd-change` clasifica el `--new-reqs` como `CLARIFICATION`.
**Mecanismo:** `wf-prd-change-cascade`.

1. Le pides la cascada con un cambio que resulta ser una aclaración.
   → **Esperado:** **detiene** el cascade (no hay producto que propagar); recomienda
     `wf-spec-gap-resolve` / `wf-spec-delta`.

**Resultado:** PASS si se detiene · FALLO si propaga sync sobre una aclaración.
**Desviación → reportar:** issue citando `CU-7.g`.

### CU-7.h — Cascada sin un cambio que propagar

**Precondición:** no pasas `--new-reqs` y no existe `product-changelog.md` ni `changes/`.
**Mecanismo:** `wf-prd-change-cascade`.

1. Le pides la cascada sin haber gestionado ningún cambio antes.
   → **Esperado:** **se detiene**: no hay cambio gestionado; pide arrancar con
     `--new-reqs` o `wf-prd-change` primero.

**Resultado:** PASS si se detiene · FALLO si ejecuta la cascada sin un cambio que
propagar.
**Desviación → reportar:** issue citando `CU-7.h`.

### CU-7.i — Features no triviales en el conjunto STOP

**Precondición:** alguna feature sale `major` / `manual_review` / `rediscover`.
**Mecanismo:** `wf-prd-change-cascade`.

1. Lanzas una cascada donde algunas features cambian de forma no trivial.
   → **Esperado:** esas features se **preguntan** con `AskUserQuestion`, con la lista delante
     (ID, nombre, severidad y por qué no es automática) y dos salidas: continuar con el resto,
     o parar aquí. **No se aplican.** Si el usuario elige continuar, el cascade **no aborta**:
     sigue con el conjunto AUTO-APPLY.
   → **Esperado (forma):** lo que necesita cada feature se describe en **lenguaje natural**
     —evolucionar el spec, revisarlo a mano, rehacer su partición, darla de baja—, sin nombrar
     workflows ni comandos ([[D-019]]).
   → **Por qué este escenario cambió de forma ([[D-075]]):** antes pedía que se "presentaran al
     usuario" desde un fork, que no tiene turno. Era inejecutable, y pasaba por interpretación
     benévola de un reporte. Ahora se mide lo que dice: **si no hay pregunta, es FALLO.**

**Resultado:** PASS si pregunta por las no triviales sin aplicarlas y continúa con el
resto · FALLO si las aplica solas, si aborta todo el cascade por ellas, o si se limita a
listarlas sin preguntar.
**Desviación → reportar:** issue citando `CU-7.i`.

### CU-7.j — `--dry-run` / `--review-before-apply` no escriben

**Precondición:** pasas uno de los dos flags.
**Mecanismo:** `wf-prd-change-cascade` (flags conservadores).

1. Lanzas la cascada con `--dry-run` (o con `--review-before-apply`).
   → **Esperado:** **no escribe nada**: `--dry-run` solo diagnostica;
     `--review-before-apply` para antes de aplicar incluso los `minor` y te ofrece aplicarlos
     cuando lo confirmes — **en lenguaje natural, sin dictarte el comando** ([[D-019]]).

**Resultado:** PASS si no aplica ningún delta · FALLO si aplica algo con cualquiera de
los dos flags.
**Desviación → reportar:** issue citando `CU-7.j`.

### CU-7.k — Profundidad adaptativa y degradación con gracia

**Precondición:** falta la fase Design (sin `DESIGN.md`), o un sub-workflow no está
instalado o falla.
**Mecanismo:** `wf-prd-change-cascade`.

1. Lanzas la cascada en un proyecto sin Design (o con un sub-workflow caído).
   → **Esperado:** omite Design si no aplica; un sub-workflow ausente/fallido se
     registra como `no disponible` y el cascade **continúa** con las fases
     independientes (salvo prerequisito duro). Todo queda reflejado en el **resumen que
     presenta al cerrar** — que es donde vive, porque no escribe informe.

**Resultado:** PASS si degrada con gracia y lo refleja · FALLO si aborta por una fase
opcional ausente, o silencia la omisión.
**Desviación → reportar:** issue citando `CU-7.k`.

### CU-7.r — El cascade no redacta el informe de sus delegados ni enseña comandos

**Precondición:** una pasada de cascade que haya llegado al final (sirve la de CU-7.f).
**Mecanismo:** `wf-prd-change-cascade` en el hilo principal ([[D-060]]/[[D-019]]/[[D-075]]).

1. Tras la pasada, busca el informe consolidado en disco:
   ```bash
   ls *_cascade_report.md 2>/dev/null | wc -l
   ```
   → **Esperado: 0.** El resumen por fase se presenta en la conversación. Consolidar en un
     fichero lo que produjeron sus delegados es redactar un artefacto ajeno: cada informe
     (`_sync_report.md`, `_conflict_report.md`, `_readiness_report.md`) tiene un autor
     declarado, y esa autoría es lo que lo hace auditable.
   → **Por qué se mide:** medido en CU-3.a pasada 13, el orquestador consolidó cuatro informes
     de conflicto y, al transcribir contenido que no había producido, **adjudicó un hallazgo al
     auditor equivocado**. El fichero no era el problema: era la transcripción.

2. Revisa el resumen que presentó y los mensajes de sus gates.
   → **Esperado:** ningún nombre de workflow ni slash-command (`wf-…`, `/wf-…`) en lo que lee
     el usuario — ni en las opciones del `AskUserQuestion`, ni en el cierre. Lo que hay que
     hacer después se describe hablando ("cuando quieras revalidamos los specs que han
     cambiado").
   → **Excepción que NO es fuga:** el usuario pidió explícitamente el nombre técnico.

3. Comprueba que los artefactos que sí existen los escribió quien tocaba:
   ```bash
   grep -l "Generado por:" *_sync_report.md features/*/spec/*_conflict_report.md 2>/dev/null
   ```
   → **Esperado:** cada uno declara su procedencia, y el cascade no figura como autor de
     ninguno.

**Resultado:** PASS si no hay informe consolidado, la procedencia de cada artefacto apunta a su
autor real y nada de lo que lee el usuario contiene un nombre de workflow · FALLO si el cascade
escribe un `_cascade_report.md`, si consolida hallazgos ajenos en su respuesta atribuyéndolos
mal, o si surfacea comandos.
**Desviación → reportar:** issue citando `CU-7.r`.

---

## `wf-spec-sync-from-prd` — resincronizar specs tras el cambio (paso a paso)

> **Mecanismo común:** skill `wf-spec-sync-from-prd` → subagente **`sdd-spec-writer`**.
> Es el eslabón spec-side que el cascade (CU-7.f) orquesta, también invocable suelto.
> Modo `analyze <prd.md>` produce `<basename>_sync_report.md`; `apply <prd.md>
> --features F-…` integra vía delta sobre los specs afectados.

### CU-7.l — Analizar y aplicar la resincronización de specs

**Precondición:** un PRD cambiado (CU-7.b) con specs de feature derivados.
**Mecanismo:** `wf-spec-sync-from-prd` → `sdd-spec-writer`.

1. Le pides analizar qué specs hay que resincronizar con el PRD nuevo.
   → **Esperado:** `analyze` identifica las features afectadas y genera por feature los
     **requisitos de sincronización** (en `<basename>_sync_report.md`), sin tocar los
     specs todavía.
2. Le pides aplicar la resincronización a un subset (`--features F-001,F-002`).
   → **Esperado:** `apply` integra esos cambios **vía delta** sobre los specs afectados
     y actualiza su trazabilidad (incluido el sello PRD→spec), solo en las features
     indicadas.
   → **Esperado (sello):** cada spec tocado sale con su **validación reabierta** —
     `Estado: BORRADOR`, vía `sdd-seal.py --unseal` ([[D-061]])— y el informe **lo dice**:
     lo que alguien validó ya no es lo que hay. Es el mismo invariante que CU-7.b mide sobre
     el PRD.
   → **FALLO:** un spec con contenido cambiado que siga declarándose `VALIDADO`, o que salga
     en borrador **sin que nadie lo mencione**.
   → **Por qué el aviso es lo único que protege aquí ([[D-077]]):** este FALLO decía
     *"(el readiness lo bloqueará y el usuario no sabrá por qué)"*, y **no lo bloquea** —
     su veredicto `LISTA` no mira el sello (`kb-decompose-expert`, derivación de Estado),
     así que un spec recién desellado sale `LISTA` en el informe y en `_features.md`. Quien
     lo deniega es `gate_spec_fiable`, **una fase más tarde**, al pedir el plan. Si el apply
     no menciona la reapertura, entre el desello y la denegación no hay nada que se lo diga
     al usuario — que era justo lo que esta línea creía tener cubierto. La coherencia
     informe↔gate la mide `CU-3.o` punto 4.

**Resultado:** PASS si analyze diagnostica por feature, apply integra vía delta solo
el subset y deja constancia de la reapertura · FALLO si apply toca features fuera del
subset, resincroniza sin diagnóstico previo, o conserva el sello sobre contenido nuevo.
**Desviación → reportar:** issue citando `CU-7.l`.

### CU-7.m — Resincronización que rebasa un delta razonable

**Precondición:** un PRD cambiado donde una feature afectada tiene un cambio **estructural** (rebasa
lo que un delta quirúrgico puede integrar).
**Mecanismo:** `wf-spec-sync-from-prd` → `sdd-spec-writer` (analyze clasifica severidad por feature;
apply Paso 4B detiene la feature que rebasa delta).

1. Le pides analizar la resincronización.
   → **Esperado:** clasifica por feature `severidad: minor|major|structural` y
     `acción: delta|manual_review|repartition|retire`; las `structural`/`repartition` no se marcan
     como auto-aplicables.
2. Le pides aplicar (`apply`) una feature cuyo cambio es estructural.
   → **Esperado:** **no fuerza un delta**: detiene esa feature y dice que el cambio **mueve su
     frontera**; no aplica un sync automático que falsee la trazabilidad.
3. **La recomendación tiene que ser ejecutable** ([[D-075]]).
   → **Esperado:** lo que propone para esa feature son **vías que existen**, descritas en lenguaje
     natural: evolucionar con un delta la parte que sigue viva (tombstones, IDs no reutilizados),
     dar de baja la capacidad que sale del producto, y especificar aparte la que emerge —con el
     siguiente `F-00X` libre—.
   → **FALLO:** recomendar *"rehacer el discovery"* / *"rediscovery"*. **No hay vía que lo
     ejecute**: regenerar el `_discovery.md` renumera los `F-00X` que los specs ya citan, y el
     propio `wf-spec-discover` se detiene por eso. Una acción recomendada que ninguna vía puede
     cumplir es una promesa, no un siguiente paso.

**Resultado:** PASS si clasifica por severidad, detiene las features que rebasan delta y propone
solo vías ejecutables · FALLO si fuerza un delta sobre un cambio estructural, auto-aplica una
repartición, o remite a re-correr el discovery sobre un sistema ya especificado.
**Desviación → reportar:** issue citando `CU-7.m`.

### CU-7.o — Una capacidad sale del producto (`DEPRECATION`, no `SCOPE_CHANGE`)

**Precondición:** un PRD sellado con varias capacidades comprometidas y specs derivados de al menos
dos de ellas.
**Mecanismo:** `wf-prd-change` (hilo principal) → `prd-expert` clasifica read-only → gate del Paso 5.

1. Le dices, hablando, que el producto deja de contemplar una de las capacidades — que se cae, que
   ya no va.
   → **Esperado:** el experto la clasifica **`DEPRECATION`**, no `SCOPE_CHANGE`. Es FALLO
     clasificarla `SCOPE_CHANGE`: desde [[D-074]] esa etiqueta es para **añadir** o mover entre MVP
     y fase futura, y la frontera importa porque decide si los derivados se resincronizan o se dan
     de baja.
2. Observas el gate.
   → **Esperado:** presenta la clasificación **con su consecuencia práctica** —que las features que
     especifican esa capacidad no se resincronizan, se retiran— y espera. No la da por buena.
3. Le dices, en cambio, que esa capacidad **se pospone a la fase 2**.
   → **Esperado:** eso **no** es `DEPRECATION`: la capacidad sigue comprometida, solo llega más
     tarde. FALLO si propone retirar nada.
4. Miras el `changes/CR-XXX/change-request.md`.
   → **Esperado:** **nombra las features afectadas**, porque la baja se ejecuta feature a feature y
     quien la ejecute necesita saber cuáles son. Y el PRD queda con el sello reabierto.

**Resultado:** PASS si distingue retirar de posponer, presenta la consecuencia en el gate y deja las
features nombradas en la traza · FALLO si colapsa `DEPRECATION` en `SCOPE_CHANGE`, si retira un
aplazamiento, o si **toca algún spec** desde aquí (esta fase decide producto, no edita derivados).
**Desviación → reportar:** issue citando `CU-7.o`.

---

### CU-7.p — La baja se confirma con el impacto delante, y la estampa el script

**Precondición:** el `CR-XXX` de CU-7.o ya registrado, y la feature afectada con su spec
`Estado: VALIDADO`. Si además posee un shared model que otra feature referencia, mejor: es el caso
que importa.
**Mecanismo:** `wf-spec-retire` (hilo principal) → `sdd-spec-auditor` diagnostica → gate →
`sdd-seal.py --retire` + `sdd-features-index.py`.

1. Le pides dar de baja esa feature, hablando.
   → **Esperado:** antes de preguntar nada, **presenta el impacto**: qué shared models quedan sin
     dueño y qué features los referencian, quién la declara dependencia, y qué artefactos derivados
     existen ya. Es FALLO presentar el gate **sin** ese diagnóstico: un gate sin el impacto delante
     es la firma de algo que no se ha visto.
2. Observas la pregunta.
   → **Esperado:** un `AskUserQuestion` con retirar / no retirar. **No hay flag de override**, y es
     FALLO que se ofrezca uno o que se invente un `--allow-*`: este workflow puede preguntar, así
     que el gate es el mecanismo ([[D-026]]).
3. Confirmas la baja. Miras la cabecera del spec.
   → **Esperado:** `Estado: RETIRADO` y `Retirada: CR-XXX — <razón> (<fecha>)`, escritas **por el
     script**. FALLO si las escribe el orquestador a mano ([[D-060]]).
4. Miras `_features.md` y el estado del proyecto.
   → **Esperado:** la feature figura como **`RETIRADA`**, con el `CR-XXX` como motivo, y **no
     aparece en «Siguiente foco»** ni pide ninguna acción. FALLO si desaparece del informe: eso
     significa que una copia del vocabulario de estados se quedó corta.
5. Le pides ahora que planifique esa feature.
   → **Esperado:** **se deniega**, y el mensaje dice que está dada de baja — no que le falten gaps
     por responder.
6. Pruebas a retirarla otra vez.
   → **Esperado:** informa de que ya estaba retirada y no vuelve a preguntar ni a estampar.

**Resultado:** PASS si el impacto precede al gate, el script estampa, el índice deriva `RETIRADA` y
planificar queda denegado · FALLO si retira sin preguntar, si acepta hacerlo sin `CR-XXX`, o si el
estado lo escribe alguien que no es el sellador.
**Desviación → reportar:** issue citando `CU-7.p`.

> ⏱ **Los pasos 5-6 solo miden el primer frente.** Generar tareas y ejecutarlas sobre una feature
> retirada **también** debe denegarse, pero eso exige plan y tasks ya generados: se mide sobre el
> proyecto de CU-6, no aquí.

---

### CU-7.q — Nadie retira desde un fork

**Precondición:** el PRD ya actualizado con la retirada y specs derivados sin tocar.
**Mecanismo:** `wf-prd-sync-impact` y `wf-spec-sync-from-prd` (los dos `context: fork`).

1. Le pides medir el impacto del cambio de PRD.
   → **Esperado:** para la feature cuya capacidad ya no está en el PRD, la acción recomendada dice
     **darla de baja**. Es FALLO recomendar "aplicar la sincronización" o "regenerarla": las dos son
     falsas —no hay con qué poner al día un spec cuyo referente desapareció, y regenerarlo lo
     volvería a escribir.
2. Le pides analizar la resincronización.
   → **Esperado:** esa feature sale clasificada con `acción: retire`.
3. Le pides **aplicar** la resincronización incluyéndola.
   → **Esperado:** **no la toca**. Ni delta, ni regeneración, ni sello de sync: la reporta como
     pendiente de una baja que se confirma aparte. FALLO si le aplica cualquier cosa, y FALLO
     también si **promete** retirarla — un fork no tiene turno para preguntarlo.
4. Ejecutas la cascada completa sobre ese cambio.
   → **Esperado:** la feature entra en el conjunto **STOP**, nunca en AUTO-APPLY, por baja que sea
     su severidad.

**Resultado:** PASS si los tres forks señalan la baja y ninguno la ejecuta · FALLO si alguno
resincroniza, regenera o estampa el estado de una feature retirada.
**Desviación → reportar:** issue citando `CU-7.q`.

---

### CU-7.s — Volver: la reactivación es la única vuelta atrás, y no restaura sellos ⏱ **sin pasada**

**Precondición:** la feature dada de baja en `CU-7.p`, con `Estado: RETIRADO`, su traza
`Retirada: CR-XXX` y su plan degradado a `BORRADOR` en la misma pasada. El PRD sigue **sin**
contemplar la capacidad.
**Mecanismo:** `wf-spec-retire` modo `reactivate` → `sdd-seal.py --unretire` (único camino de
salida de `RETIRADO`) + `sdd-features-index.py`.

1. Le dices que al final sí la hacéis ("recupera la feature de pagos", "vuelve a activarla").
   → **Esperado:** la reactiva. **No lleva gate**: es la dirección segura, no destruye nada — y es
     FALLO exigir aquí una confirmación que la baja sí exige, o pedir un `CR-XXX` para volver.
2. Miras la cabecera del spec.
   → **Esperado:** `Estado: BORRADOR`, **no `VALIDADO`** — la reactivación deja el sello
     **pendiente**, no lo reabre— y la línea `Retirada:` **ha desaparecido**. FALLO encontrar el
     spec vigente con una traza de baja todavía puesta: afirma una retirada que el estado ya
     niega, y la leen tanto el índice como una persona.
3. Miras el plan de esa feature.
   → **Esperado:** **sigue en `BORRADOR`** desde la baja, y te lo dice: también hay que
     revalidarlo. FALLO que la reactivación le devuelva el sello — nadie lo ha vuelto a auditar.
4. Miras `_features.md` y el estado del proyecto.
   → **Esperado:** deja de figurar `RETIRADA` y vuelve a pedir trabajo. Su `F-00X` **es el mismo
     de siempre**: no se renumera ni se le asigna uno nuevo ([[D-074]], Regla 12).
5. Le pides ahora el plan de esa feature.
   → **Esperado:** ya no se deniega **por la baja** — pero sí **por el sello**, que quedó
     pendiente (`CU-9.n`). FALLO que pase directo a planificar: la reactivación no revalida nada.
6. **La contradicción que nadie resuelve sola.** Le preguntas cómo queda respecto al PRD.
   → **Esperado:** te dice que el PRD vigente **sigue sin contemplar** esa capacidad, así que el
     spec reactivado lo contradice: reactivar un spec **no reactiva la decisión de producto**, y
     eso se formaliza aparte. FALLO callarlo, y FALLO también decir que "ya está todo alineado".
7. **La vuelta que NO existe.** Sobre otra feature aún retirada, le pides evolucionarla en vez de
   reactivarla.
   → **Esperado:** deniega y te remite a reactivarla primero — nunca la devuelve al producto como
     efecto colateral de escribir en su spec ([[D-078]]). El detalle del gate se mide en `CU-9.o`;
     aquí lo que importa es que **el journey solo tiene una puerta de vuelta**.

**Resultado:** PASS si reactiva sin gate, devuelve a `BORRADOR` sin restaurar ningún sello, retira
la traza, conserva el `F-00X` y avisa de que el PRD sigue sin contemplarla · FALLO si sella el spec
o el plan, si deja la traza `Retirada:` puesta, si renumera la feature, si oculta la contradicción
con el PRD, o si alguna vía distinta de la reactivación la devuelve viva.
**Desviación → reportar:** issue citando `CU-7.s`.

> **Por qué se escribe ahora.** El ROADMAP ya anotaba que *"el modo `reactivate` tampoco tiene
> escenario"* desde [[D-074]] — lo que faltaba era el punto 7, que llegó con [[D-078]]: la salida
> de `RETIRADO` tenía una **segunda puerta no sancionada**, el `--unseal` de los flujos de
> evolución. Cerrada esa, el journey queda con una sola, y esta es la que la mide.
