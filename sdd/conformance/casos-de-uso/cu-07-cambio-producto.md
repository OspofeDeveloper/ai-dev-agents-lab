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
sola skill: sus escenarios ejercitan **4 componentes** del subsistema de cambio de
producto. Marca cada escenario al ejecutarlo. El estado de cobertura autoritativo (ejes
happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) — esta vista es la
**transpuesta** para leer/ejecutar el CU.

### `wf-prd-change` — gestionar un cambio de producto (4)
- [ ] CU-7.a — Un cambio que es solo aclaración (CLARIFICATION)
- [ ] CU-7.b — Un cambio de producto real + reapertura del sello (D-028)
- [ ] CU-7.c — Expansión de capacidad disfrazada de aclaración (Regla 4.1)
- [ ] CU-7.n — El gate del cambio: clasificación confirmada y bifurcación resuelta por el humano (D-040)

> ⚠ **[[D-040]] reinicia el recuento conductual de este bloque (2026-07-30).** `wf-prd-change` deja de
> ser `context: fork` y pasa al hilo principal con **gate obligatorio**; el `prd-expert` analiza
> read-only y escribe por delegación; la cascada la invoca con `--defer-decisions`. Las pasadas de
> CU-7.b hechas antes (1 y 2, 2026-07-30) midieron la **arquitectura vieja**: quién clasifica, quién
> pregunta y quién llama a `--reopen` son otros ahora, así que su evidencia conductual **no cuenta**.
> Lo único que sobrevive es la del probe **2bis** ([[D-039]]), porque marcar las inferencias lo hace el
> `prd-expert`, que sigue siendo subagente. Al re-probar, CU-7.a y CU-7.c también cambian de mecanismo
> (su clasificación pasa a estar tras el gate).

### `wf-prd-sync-impact` — medir impacto aguas abajo (2)
- [ ] CU-7.d — Matriz de impacto por artefacto
- [ ] CU-7.e — Criterio conservador

### `wf-prd-change-cascade` — propagar el cambio por el pipeline (6)
- [ ] CU-7.f — Cascada normal (auto + paradas reales)
- [ ] CU-7.g — La cascada con un cambio que es solo aclaración
- [ ] CU-7.h — Cascada sin un cambio que propagar
- [ ] CU-7.i — Features no triviales en el conjunto STOP
- [ ] CU-7.j — `--dry-run` / `--review-before-apply` no escriben
- [ ] CU-7.k — Profundidad adaptativa y degradación con gracia

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

**G — `--defer-decisions`: sin humano se marca, no se decide**
   → **Precondición:** invocación desde la cascada (`wf-prd-change-cascade`, que es subagente).
   → **Esperado:** se omite el gate; cada bifurcación se resuelve por la lectura **más
     conservadora** y **queda marcada `[ASUNCIÓN]`** con las alternativas en
     `change-request.md`; la clasificación se registra como **no confirmada por humano**; el PRD
     sale `OPEN_ASSUMPTIONS` y el informe dice que la decisión está **aplazada** al gate del
     review, no perdida.
   → **FALLO:** decidir la bifurcación en silencio sin marcarla (es el fallo de [[D-039]] con
     otro disfraz), o dejar el PRD sellable sin pasar por review.
   → **FALLO grave:** usar `--defer-decisions` en una invocación **conversacional**, con el
     usuario delante.

**Resultado:** PASS si (A) el análisis no escribe, (B) hay un gate único en main, (C) salta
siempre, (D) el humano decide y main no reclasifica, (E) main no toca el fichero salvo por
script, (F) la traza distingue decisión humana de decisión del agente, y (G) el modo sin gate
marca en vez de decidir · FALLO ante gate ausente u opcional, PRD editado antes del gate,
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

> ⚠ **Corrección de premisa por [[D-040]] (2026-07-30).** La cascada declaraba como **primer
> checkpoint humano** "aprobar el cambio de producto (`wf-prd-change`)". **Nunca fue un checkpoint:**
> la cascada es `context: fork` e invocaba otra skill que también era fork — no había nadie a quien
> preguntar. Ahora invoca `wf-prd-change` con **`--defer-decisions`**: las bifurcaciones se resuelven
> por la lectura más conservadora y **quedan marcadas `[ASUNCIÓN]`**, la clasificación se registra como
> *no confirmada por humano*, el PRD sale `OPEN_ASSUMPTIONS` y la decisión queda **aplazada** al gate de
> `wf-prd-review`, que **no** forma parte de este cascade. Al probar CU-7.f–k: el paso del cambio **no**
> debe presentarse como parada humana, y el reporte final debe decir cuántas asunciones quedaron
> abiertas y que el PRD no puede re-sellarse sin pasar por review. Lección transversal: **un checkpoint
> declarado en prosa no es un checkpoint si la arquitectura no puede sostenerlo** — al auditar paradas,
> comprobar quién puede preguntar, no qué dice el documento.

> **Mecanismo común:** skill `wf-prd-change-cascade` → **sin agente** (orquestador
> puro, `context: fork`). Invoca en orden `wf-prd-change` → `wf-prd-sync-impact` →
> `wf-spec-sync-from-prd analyze/apply` → `wf-spec-conflict` + `wf-spec-readiness` →
> `wf-design-sync` → reporte plan/tasks. Output: `<basename>_cascade_report.md`.
> Flags: `--review-before-apply`, `--dry-run`, `--features`, `--skip-design`.

### CU-7.f — Cascada normal (auto + paradas reales)

**Precondición:** un cambio de producto real para propagar.
**Mecanismo:** `wf-prd-change-cascade`.

1. Le pides propagar el cambio por todo el pipeline en un comando.
   → **Esperado:** corre lo mecánico read-only, **auto-aplica** los deltas inequívocos
     (`severidad: minor` + `acción: delta`), y se detiene solo en los 4 checkpoints
     humanos (aprobación del cambio, features no triviales, decisiones de Design,
     revalidación de plan). Produce `<basename>_cascade_report.md` distinguiendo
     ejecutado / parado / omitido.

**Resultado:** PASS si auto-aplica solo lo inequívoco y para en los checkpoints reales
· FALLO si aplica cambios `major` solos, o no para en un checkpoint real.
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
   → **Esperado:** esas features se **presentan al usuario** (recomendando
     `wf-spec-delta` / revisión / `wf-spec-discover`) y **no se aplican**, pero el
     cascade **no aborta**: sigue aplicando el conjunto AUTO-APPLY.

**Resultado:** PASS si presenta las no triviales sin aplicarlas y continúa con el
resto · FALLO si las aplica solas, o aborta todo el cascade por ellas.
**Desviación → reportar:** issue citando `CU-7.i`.

### CU-7.j — `--dry-run` / `--review-before-apply` no escriben

**Precondición:** pasas uno de los dos flags.
**Mecanismo:** `wf-prd-change-cascade` (flags conservadores).

1. Lanzas la cascada con `--dry-run` (o con `--review-before-apply`).
   → **Esperado:** **no escribe nada**: `--dry-run` solo diagnostica;
     `--review-before-apply` para antes de aplicar incluso los `minor` e informa el
     comando manual.

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
     independientes (salvo prerequisito duro). Todo queda reflejado en el reporte.

**Resultado:** PASS si degrada con gracia y lo refleja · FALLO si aborta por una fase
opcional ausente, o silencia la omisión.
**Desviación → reportar:** issue citando `CU-7.k`.

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

**Resultado:** PASS si analyze diagnostica por feature y apply integra vía delta solo
el subset · FALLO si apply toca features fuera del subset, o resincroniza sin
diagnóstico previo.
**Desviación → reportar:** issue citando `CU-7.l`.

### CU-7.m — Resincronización que rebasa un delta razonable

**Precondición:** un PRD cambiado donde una feature afectada tiene un cambio **estructural** (rebasa
lo que un delta quirúrgico puede integrar).
**Mecanismo:** `wf-spec-sync-from-prd` → `sdd-spec-writer` (analyze clasifica severidad por feature;
apply Paso 4B detiene la feature que rebasa delta).

1. Le pides analizar la resincronización.
   → **Esperado:** clasifica por feature `severidad: minor|major|structural` y
     `acción: delta|manual_review|rediscover`; las `structural`/`rediscover` no se marcan como auto-aplicables.
2. Le pides aplicar (`apply`) una feature cuyo cambio es estructural.
   → **Esperado:** **no fuerza un delta**: detiene esa feature y marca que necesita rediscovery o
     rediseño de spec; no aplica un sync automático que falsee la trazabilidad.

**Resultado:** PASS si clasifica por severidad y detiene las features que rebasan delta · FALLO si
fuerza un delta sobre un cambio estructural, o auto-aplica un rediscover.
**Desviación → reportar:** issue citando `CU-7.m`.
