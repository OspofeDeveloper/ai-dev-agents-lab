# Registro de decisiones del ecosistema SDD

Constancia de las **decisiones de diseño** y los **aprendizajes** del ecosistema: por qué se hizo algo de una manera y no de otra, qué aprendimos al equivocarnos. Complementa al `CHANGELOG.md` (qué cambió, por versión) respondiendo al **por qué**.

Formato: una entrada `## D-NNN — <título>` por decisión, **más reciente arriba** (como el CHANGELOG). Cada entrada lleva: fecha, estado, contexto, decisión, alternativas descartadas, consecuencias/aprendizaje y referencias. Las entradas son append-only: si una decisión se revierte, no se borra — se añade una nueva que la supersede y se marca la vieja `Superada por D-MMM`.

---

## D-038 — El ámbito de edición de `wf-prd-review` es cerrado y explícito; el hilo principal nunca escribe el artefacto (y `allowed-tools` no es enforcement)

- **Fecha:** 2026-07-23 · **Estado:** Adoptada (bloque normativo en `wf-prd-review` Paso 5.5). · **Relacionada:** [[D-030]] (cuya premisa de enforcement corrige), [[D-031]] (main no diagnostica ni carga el artefacto), [[D-037]] (prosa nivel b en el momento), CU-2.j / CU-2.e / CU-2.h.

**Contexto.** En tres runs de conformance (CU-2.j pasadas 1-3) la **misma clase de edición** —limpiar contaminación dura decidida por el usuario y realinear prosa "nivel b" que un rechazo dejó falsa— se resolvió de **tres formas distintas**: (1) delegando al `prd-expert`; (2) declarándose "no autorizado para una tercera edición" y enrutando a `wf-prd-change`; (3) editando el PRD **él mismo con `Update` en el hilo principal**. Agravantes: en (2) el `prd-expert` había clasificado explícitamente el ajuste como *"no exige `wf-prd-change`; es una CLARIFICATION dentro del alcance ya comprometido"* citando el 5º trigger de Regla 4 — y el orquestador **ofreció como recomendada** la vía de cambio de producto, contradiciendo a su propio experto (lo reconoció al ser corregido). En (3) quedó **falsada la premisa de enforcement de [[D-030]]**: `wf-prd-review` declara `allowed-tools: [Bash, Agent, AskUserQuestion]` y el log confirma "3 tools allowed", pero el hilo principal ejecutó `Read` y dos `Update` sobre el PRD sin impedimento. Raíz: el Paso 5.5 decía que la prosa nivel b "se resuelve en el gate con el usuario" sin declarar **(i)** que eso es competencia del review y no un cambio de producto, ni **(ii)** **quién** aplica la edición dado que main no debe escribir. Vacío de contrato → improvisación distinta en cada invocación.

**Decisión.** Fijar el ámbito en una **tabla cerrada** (qué edición es del review y por qué mecanismo): decisiones de asunción y sello → `sdd-prd-apply.py`; contaminación dura decidida y prosa nivel b consecuencia de un rechazo → **delegar al `prd-expert`** con brief quirúrgico (localizar por texto, no por línea; enumerar qué no tocar; no reintroducir marcadores); capacidad nueva / expansión / retirada de algo comprometido → `wf-prd-change`. Más tres reglas: (1) **el hilo principal nunca escribe ni lee entero el artefacto**, y esto vale **aunque las tools estén disponibles** — se documenta explícitamente que `allowed-tools` **no es enforcement duro**, así que la restricción es **normativa** y hay que sostenerla por regla, no confiar en el harness; (2) **la clasificación de gobernanza es del `prd-expert`**: si dice "aclaración, no cambio de producto", el orquestador **no** enruta a `wf-prd-change` contra él; (3) una edición de contenido **no** se vuelve cambio de producto por ser la tercera.

**Alternativas descartadas.**
- *Dejar que main edite con `Read`/`Edit` (es más corto)* → reintroduce el bloat que [[D-030]] evita y debilita la separación diagnostica/escribe que sostiene CU-2.h; además main no tiene el catálogo de prohibidos cargado, así que su criterio de reescritura es peor que el del experto.
- *Enrutar toda edición de contenido a `wf-prd-change`* → convierte una corrección de redacción, consecuencia directa de una decisión tomada **en este mismo gate**, en un rodeo por otro workflow con su propia trazabilidad. `wf-prd-change` es para cambios de **producto**, no de **fraseo**.
- *Buscar enforcement mecánico real (hook que bloquee `Edit` durante el skill)* → no existe hoy ese punto de control por-skill, y un hook global de `Edit` rompería el resto del trabajo. Se acepta que la garantía sea normativa + **medida** (el `diff` contra pristine de CU-2.h), y se deja anotado como mejora del harness, no de este skill.

**Consecuencias / aprendizaje.** Dos aprendizajes, y el segundo es el importante. (a) Un contrato que dice "resuélvelo con el usuario" sin decir **quién ejecuta** deja al agente eligiendo mecanismo, y elegirá distinto cada vez. (b) **`allowed-tools` de un skill es declarativo, no una jaula**: cualquier invariante que se justifique con "es estructuralmente imposible porque el skill no declara esa tool" está **sobreafirmado**. Corrige la premisa de [[D-030]] ("el signo estructural que hace el bloat imposible") y la nota de sello de CU-2.h, que se rebaja de "estructuralmente fuerte" a "conducta verificada en N pasadas". Regla general para esta campaña: **una garantía vale lo que su medición**, no lo que su declaración.

**Referencias.** `sdd/pipeline/prd/skills/wf-prd-review/SKILL.md` (Paso 5.5, bloque de ámbito), `sdd/conformance/casos-de-uso/cu-02-prd.md` (CU-2.j probe E, CU-2.e probe D, nota de sello de CU-2.h), `sdd/tests/test_install_sh.py`, `sdd/CHANGELOG.md`.

---

## D-037 — El backstop de dependencias corre ANTES de aplicar, falla ruidosamente si es vacuo, y admite el tercer desenlace (`--keep`)

- **Fecha:** 2026-07-23 · **Estado:** Adoptada (`sdd-prd-deps.py` + orden normativo en `wf-prd-review` Paso 5.5). · **Relacionada:** [[D-029]] (grafo de dependencias, al que corrige), [[D-030]] (la edición la aplica `sdd-prd-apply.py`), CU-2.j.

**Contexto.** En conformance (CU-2.j pasada 1) el review **selló un PRD con una dependiente sin decidir** y el backstop dijo `OK`. Reproducido: con ASN-002 rechazada y ASN-003 (su dependiente) viva, `sdd-prd-deps.py --check --rejected ASN-002` da `ORPHANS` (exit 2) **antes** de aplicar y `OK` (exit 0) **después**. La razón es estructural: el check lee las entradas `[ASN-XXX]` y sus aristas, y `sdd-prd-apply.py` retira las decididas y **elimina la sección** si queda vacía — después del apply no hay aristas que comprobar. El SKILL decía "**antes** de aplicar/sellar" pero **colocaba el bloque después** del de `apply`; el orquestador siguió el orden visual, razonablemente. Un no-op silencioso es peor que no correrlo: se lee como garantía verificada. Segundo hueco descubierto en el mismo run: el modelo de "resuelto" del check era binario (rechazada o editada-para-no-depender) y no contemplaba el desenlace legítimo que ocurrió —el usuario **conservó** ASN-003 a conciencia porque "presupuesto por categoría" sigue en pie sobre categorías fijas—, así que en el orden correcto el review habría quedado atascado en `ORPHANS` perpetuo o forzado a rechazar contra la decisión del usuario.

**Decisión.** Tres cambios acoplados: (1) **Orden normativo** — el bloque del backstop se mueve **delante** del `apply` en el Paso 5.5, con una nota de por qué el orden no es cosmético. (2) **Guarda de vacuidad** — si se pasan rechazos sobre un documento sin entradas `[ASN-XXX]`, el script sale `VACUOUS` (exit 2) en vez de `OK`: el fallo por orden invertido se vuelve **ruidoso y autodiagnosticado** ("si ves VACUOUS, lo corriste tarde"). Sin rechazos no hay vacuidad (nada podía quedar huérfano). (3) **`--keep ASN-XXX`** — declara un dependiente **conservado conscientemente** tras presentárselo al usuario; deja de contar como huérfano. Es deliberadamente **separado de `--confirm`**: hay que **nombrar** el dependiente, lo que exige haber visto la cascada — confirmar todo en bloque no silencia el check. Además el Paso 5.5 ahora prescribe **cuándo** plantear la consecuencia de un rechazo (el PRD queda mudo sobre algo que otra confirmada presupone): **al recoger esa decisión**, no al final antes de sellar.

**Alternativas descartadas.**
- *Solo mover el bloque de orden* → deja el modo de fallo silencioso: cualquier futuro orquestador que lo corra tarde vuelve a obtener un falso `OK`. La guarda de vacuidad es lo que convierte el contrato en verificable.
- *Que `--check` acepte el set completo de decididas (`--confirmed`)* → lo haría inútil: el gate decide **todas** las asunciones, así que "decidida" no distingue "presentada por cascada" de "confirmada en silencio" — el check pasaría siempre. `--keep` conserva los dientes porque es una declaración extra y nominal.
- *Correr el check también después, como doble red* → no hay nada que comprobar después; sería teatro. La red posterior real es `sdd-prd-ready.py` (1:1 + sello), que es ortogonal.
- *Hacer que `apply` no borre la sección* → rompería la condición de `READY` (inline==0 && entries==0) y el diseño de [[D-030]]; el problema es el orden del check, no el borrado.

**Consecuencias / aprendizaje.** El backstop de [[D-029]] pasa de garantía nominal a garantía real. Aprendizaje transversal: **un verificador cuyo insumo lo destruye un paso anterior es un no-op silencioso, y el orden entre pasos deterministas es parte del contrato, no presentación** — cuando el texto de un SKILL y la posición del bloque se contradicen, gana la posición (es lo que el agente ejecuta), así que hay que alinearlas y, mejor, hacer que el script detecte el orden equivocado por sí mismo. Backstop de contenido: `test_install_sh.py` compara **posiciones** (`--check` antes de `--confirm`), no solo presencia de cadenas.

**Referencias.** `sdd/scripts/sdd-prd-deps.py`, `sdd/pipeline/prd/skills/wf-prd-review/SKILL.md` (Paso 5.5), `sdd/tests/test_sdd_prd_deps.py`, `sdd/tests/test_install_sh.py`, `sdd/conformance/casos-de-uso/cu-02-prd.md` (CU-2.j), `sdd/CHANGELOG.md`.

---

## D-036 — La dimensión temporal de una capacidad no lava su cualificador de formato: "en un calendario" sigue siendo contaminación dura

- **Fecha:** 2026-07-23 · **Estado:** Adoptada (refuerzo de la nota de `kb-prd-expert/references/prd_prohibited_items.md`). · **Relacionada:** [[D-034]] (formato de presentación = dura), Regla 6 (Prueba de Negocio), CU-2.h.

**Contexto.** Residual de [[D-034]] destapado en conformance (CU-2.h, 3 pasadas sobre el mismo PRD pristine): el `prd-expert` clasificó **la misma** frase —«ver los pagos previstos… **en un calendario o vista de próximos gastos**» (L71)— como *borderline aceptable* (no degrada) en las pasadas 1 y 2, y como **contaminación dura** (citando la fila exacta del catálogo) en la pasada 3. D-034 la fijó como el ejemplo canónico de fila dura → la clasificación correcta es dura y las pasadas 1-2 fueron inconsistentes con el KB. Raíz del titubeo: el experto racionalizaba que *"la organización temporal (próximos gastos / próximas semanas) es negocio"* para bajar la severidad, y la nota de D-034 ("quita el formato, conserva la capacidad") **no cubría ese razonamiento** — no ataja que la dimensión temporal de la capacidad no lava el cualificador de presentación pegado a ella. Impacto acotado: en las 3 pasadas el experto **igualmente** señaló L71 y propuso la misma reescritura; lo único que bailaba era la *etiqueta de severidad* (dura → `LISTO_CON_AJUSTES` vs borderline → `LISTO`+nota). No afectó a CU-2.h (las 3 pasadas byte-idénticas: el review nunca reescribió).

**Decisión.** Ampliar la nota "sobre el formato de presentación de una capacidad" con el frame **"la dimensión temporal no lava el formato"**: la parte temporal de la capacidad ("de las próximas semanas", "del último mes") es negocio y se conserva; que la capacidad organice datos en el tiempo **no** convierte en negocio el widget que los presenta ("en un calendario / línea de tiempo / agenda / vista de X" siguen siendo dura). Se explicita el mal razonamiento a evitar ("como organiza datos temporales, el calendario es negocio") separando el *qué se consulta* (temporal, se queda) del *cómo se muestra* (calendario, se va).

**Alternativas descartadas.**
- *Dejarlo como está (D-034 ya lo cubre)* → el residual demuestra que no: el escape temporal no estaba atajado y producía 2/3 de misclasificación.
- *Mecanizar la clasificación con un script* → sigue siendo semántico (¿es este sufijo formato o negocio?), no sintáctico; el lever correcto es la nitidez del KB, no un verificador. Es la misma naturaleza que D-034.
- *Aceptar la varianza como no-determinismo inherente del LLM* → cierto que afinar el KB **reduce** la varianza sin anularla (es juicio, no script), pero el escape era **concreto y nombrado** por el propio experto → barato de preemptar; no cerrarlo sería dejar un hueco identificado.

**Consecuencias / aprendizaje.** Cierra el escape observado del par temporal; se asume explícitamente que baja la varianza, no la elimina (juicio de LLM). Aprendizaje: cuando un residual de un refuerzo de KB reaparece, mirar **qué razonamiento concreto usó el agente para escaparse** y atajarlo por su nombre en la nota, en vez de repetir el frame general. Backstop de contenido: `test_install_sh.py` (la nota menciona la dimensión temporal).

**Referencias.** `sdd/pipeline/prd/skills/kb-prd-expert/references/prd_prohibited_items.md`, `sdd/conformance/casos-de-uso/cu-02-prd.md` (CU-2.h), `sdd/tests/test_install_sh.py`, `sdd/CHANGELOG.md`.

---

## D-035 — El umbral del veredicto del review es determinista: solo lo bloqueante degrada `LISTO`; borderline aceptable y huecos-de-Spec se reportan sin bajar el veredicto

- **Fecha:** 2026-07-23 · **Estado:** Adoptada (nueva Regla 14 en `kb-prd-expert` + Paso 6 de `wf-prd-review`). · **Relacionada:** [[D-034]] (contaminación dura vs borderline), [[D-033]] (consistencia de juicio), Regla 13 (sello atado al veredicto), CU-2.f.

**Contexto.** En conformance (CU-2.f, 2ª pasada) el `prd-expert` etiquetó **`LISTO_CON_AJUSTES` leves** sobre un PRD que su propio cuerpo describía como sin nada bloqueante (borderline L95 aceptable + huecos que son materia de Spec); para **el mismo** estado limpio, en otros runs dijo `LISTO`. El titubeo no era de clasificación de hallazgos (eso lo fijó D-034: L95 = borderline, no dura) sino del **mapeo hallazgo → etiqueta de veredicto**, que no estaba definido. Agravante: Regla 13 **ata la etiqueta al sello** ("con `LISTO_CON_AJUSTES` no se escribe el sello"), así que un orquestador que honrase la etiqueta al pie de la letra **se negaría a sellar** un PRD sellable → fricción falsa. Aquí el orquestador leyó la sustancia y selló bien, pero anulando de facto la etiqueta: contrato ambiguo.

**Decisión.** Definir el umbral de forma **determinista** (nueva Regla 14, SSoT en `kb-prd-expert`; restatement en `wf-prd-review` Paso 6): `NO_LISTO` = asunciones sin confirmar o defecto de estructura/elemento obligatorio; `LISTO_CON_AJUSTES` = existe contaminación **dura** (fila de la tabla de `prd_prohibited_items.md`) que corregir; `LISTO` = ninguno de los anteriores. **Solo lo bloqueante degrada.** Explícitamente, **no** bajan `LISTO`: (1) notas *borderline* documentadas como aceptables, (2) huecos de negocio que `wf-spec-analyze` resolverá (materia de Spec, no defectos del PRD — Reglas 7 y 9). El template del Paso 6 separa "Ajustes bloqueantes (degradan)" de "Notas no bloqueantes (no cambian `LISTO`)".

**Alternativas descartadas.**
- *Dejarlo al juicio del experto (statu quo)* → es justo la fuente del titubeo; el veredicto gobierna el sello (Regla 13), no puede ser no-determinista.
- *Que el orquestador siga interpretando la sustancia por encima de la etiqueta* → funcionó por suerte, pero deja el contrato etiqueta↔sello contradictorio y frágil ante un orquestador estricto.
- *Mecanizar el veredicto con un script* → parte del insumo (contaminación dura, huecos de negocio) es cualitativo; el lever correcto es definir el umbral en el KB, no un verificador nuevo. El gate mecánico duro (`sdd-prd-ready.py`: asunciones + sello) ya existe y es ortogonal.

**Consecuencias / aprendizaje.** Cierra el trío "consistencia de juicio del `prd-expert` → se afila el KB" (D-033 dedup · D-034 contaminación · D-035 umbral de veredicto). Impacto acotado: sin el fix el techo del daño era fricción (falso `LISTO_CON_AJUSTES`), nunca falso-sello (el gate mecánico protege). Backstop de contenido: `test_install_sh.py` (Regla 14 define el umbral y el "no degrada").

**Referencias.** `sdd/pipeline/prd/skills/kb-prd-expert/SKILL.md` (Regla 14), `sdd/pipeline/prd/skills/wf-prd-review/SKILL.md` (Paso 6), `sdd/conformance/casos-de-uso/cu-02-prd.md` (CU-2.f), `sdd/tests/test_install_sh.py`, `sdd/CHANGELOG.md`.

---

## D-034 — El formato de presentación de una capacidad es contaminación dura del PRD (fila de catálogo), no un matiz "muy menor" sellable

- **Fecha:** 2026-07-22 · **Estado:** Adoptada (refuerzo de `kb-prd-expert/references/prd_prohibited_items.md`). · **Relacionada:** Regla 6 (Prueba de Negocio), [[D-033]] (hermana: consistencia de juicio cualitativo del `prd-expert`), CU-2.e / CU-2.f / CU-2.h.

**Contexto.** En conformance (CU-2.f Caso 1 vs CU-2.e Prueba 3) el `prd-expert` clasificó **la misma** frase —«ver los pagos previstos… **en un calendario o vista de próximos gastos**» (L71 del PRD del consumidor)— de forma **opuesta** en dos invocaciones: en un run la llamó "muy menor, **no** viola 'pantalla como unidad de feature', no bloqueante" → el orquestador **selló con la contaminación dentro**; en otro la llamó "**viola** 'pantallas como unidad de feature', bloquea el sello (`LISTO_CON_AJUSTES`)" → la limpió antes de sellar. Mismo texto, misma entrada de catálogo, veredicto contradictorio y acción downstream distinta. Raíz: el catálogo no cubría con nitidez el patrón "formato de presentación como **cualificador** de una capacidad" (distinto de "pantalla como **unidad** de feature"), dejando el umbral bloqueante/no-bloqueante al juicio variable del agente.

**Decisión.** Añadir el patrón como **fila propia** del catálogo de prohibidos ("Formato de presentación de una capacidad: en un calendario / en una lista / en un dashboard / en una vista de X → Spec/Diseño") con nota trabajada (permitido «consultar los pagos previstos» vs prohibido «…en un calendario o vista»), y anclar el frame general: **lo que está en la tabla es contaminación dura** → veredicto `LISTO_CON_AJUSTES` y corrección antes de `LISTO`, no un matiz opcional. Un fraseo genuinamente de negocio que solo *roce* la frontera (p. ej. "bloqueo local en el dispositivo") se documenta como *borderline* en notas y puede dejarse; la tabla, no. La corrección canónica: **quita el formato, conserva la capacidad**.

**Alternativas descartadas.**
- *Mecanizar la detección con un script* → es semántico ("¿este sufijo es formato de presentación o negocio?"); no lo captura un regex como el 1:1. El lever correcto es la nitidez del KB que consume el `prd-expert`, no un nuevo verificador.
- *Hacer TODA contaminación bloqueante sin matiz* → borraría la categoría legítima *borderline* (business-meaningful) y forzaría reescrituras que restan significado. La distinción tabla-dura / nota-borderline se mantiene explícita.

**Consecuencias / aprendizaje.** Convergen los veredictos del experto para esta clase de frase → menos no-determinismo en el gate de contaminación. Aprendizaje transversal con [[D-033]]: los huecos de **consistencia de juicio cualitativo** del `prd-expert` se cierran afilando su KB (catálogo/reglas), no con scripts. Backstop de contenido: `test_install_sh.py` (KB cita el patrón de formato de presentación).

**Referencias.** `sdd/pipeline/prd/skills/kb-prd-expert/references/prd_prohibited_items.md`, `sdd/conformance/casos-de-uso/cu-02-prd.md` (nota de CU-2.e/2.f), `sdd/tests/test_install_sh.py`, `sdd/CHANGELOG.md`.

---

## D-033 — Reenunciado de una decisión (misma decisión en regla transversal + su exclusión-complemento) es UNA asunción, no dos atadas con `Depende de:`

- **Fecha:** 2026-07-22 · **Estado:** Adoptada (refuerzo de `kb-prd-expert` Regla 12). · **Relacionada:** Regla 12 (anti-fabricación, 1:1), [[D-029]] (`Depende de:` entre asunciones), [[D-034]] (hermana), CU-2.e / CU-2.j.

**Contexto.** En conformance (CU-2.e Prueba 3) el `prd-expert` señaló que «moneda única» aparecía **dos veces**: ASN-010 (regla transversal «opera con una única moneda») y ASN-012 (exclusión «multi-divisa fuera de alcance»), **atadas con `Depende de: ASN-010`**. Son dos caras de **la misma** decisión de producto, y Regla 12 usa literalmente "moneda única" como ejemplo del anti-patrón de reenunciado. Pero la Regla 12 vigente solo describía el reenunciado *desnudo* (segunda marca **sin** entrada → huérfana, que rompe el 1:1); el caso observado era un reenunciado *vestido* (cada formulación con **su propia** entrada), que **pasa** el invariante 1:1 de `sdd-prd-ready.py` y por eso ningún script lo detecta. El daño: el usuario decide dos veces lo mismo y puede quedar incoherente (confirmar la regla, rechazar la exclusión).

**Decisión.** Afinar Regla 12: (1) el `Depende de:` ([[D-029]]) es para asunciones **distintas** donde una necesita a la otra (p. ej. «presupuesto por categoría» ← «categorías gestionables»); **no** para atar dos formulaciones de la misma decisión — usarlo así es la señal de que sobra una. (2) La deriva de "no repitas" ahora nombra **las dos formas**: reenunciado desnudo (huérfana, rompe 1:1) y reenunciado vestido (pasa el 1:1, sutil). (3) Ejemplo canónico explícito: regla positiva + su exclusión-complemento = **una** `[ASN-XXX]` en su forma más informativa (la regla/capacidad positiva subsume a la exclusión).

**Alternativas descartadas.**
- *Detectar el reenunciado vestido con un script (extender `sdd-prd-deps.py`/`sdd-prd-ready.py`)* → requiere juzgar equivalencia semántica entre "opera con moneda única" y "multi-divisa fuera de alcance"; no es sintáctico. Recae en el juicio del `prd-expert` en creación → refuerzo de KB, no verificador.
- *Prohibir toda exclusión que tenga una regla relacionada* → demasiado amplio; una exclusión puede ser una decisión inferida **distinta** (no complemento) y entonces sí es su propia asunción. La regla distingue complemento (reenunciado) de decisión distinta.

**Consecuencias / aprendizaje.** Cierra un hueco que el 1:1 mecánico no ve, del lado **creación** (`wf-prd-create`). Es un defecto de creación surfaceado por el review, no de CU-2.e (el review lo manejó bien). Con [[D-034]] forma el par "consistencia de juicio cualitativo del `prd-expert` → se afila el KB". Backstop de contenido: `test_install_sh.py` (Regla 12 nombra el reenunciado vestido y el ejemplo canónico).

**Referencias.** `sdd/pipeline/prd/skills/kb-prd-expert/SKILL.md` (Regla 12), `sdd/conformance/casos-de-uso/cu-02-prd.md` (nota de CU-2.e), `sdd/tests/test_install_sh.py`, `sdd/CHANGELOG.md`.

---

## D-032 — "Sellado" es `status: approved` + `Aprobado por:` a la vez: el sello sube el status y la reapertura lo baja, deterministamente

- **Fecha:** 2026-07-22 · **Estado:** Adoptada (implementada en `sdd-prd-apply.py` + `wf-prd-review`/`wf-prd-change`). · **Relacionada:** [[D-027]] (identidad del aprobador), [[D-028]] (un cambio reabre el sello), [[D-030]] (edición del review por script), Regla 10 (SSoT del sello), CU-2.f / CU-7.b.

**Contexto.** En un run de conformance de CU-2.e (Tanda A, run 1) el PRD quedó tras el review con `Aprobado por: <nombre>` **pero `status: draft`**. El sello (`sdd-prd-apply.py --seal`) solo escribía la línea `Aprobado por:`; `sdd-prd-frontmatter.py --fix` únicamente rellena `status` si **falta** (y por defecto `draft`), así que nunca subía a `approved`. Estado incoherente (aprobado por alguien, pero en `draft`), y —lo grave— **desactivaba D-028**: `wf-prd-change` decide reabrir el sello si el PRD estaba sellado (`status: approved`); como el review nunca ponía `approved`, la reapertura **nunca podía dispararse** y CU-7.b habría fallado.

**Decisión.** "Sellado" es un estado de **dos campos a la vez**: `status: approved` **y** `Aprobado por:` relleno. `sdd-prd-apply.py --seal` sube `status:` a `approved` además de escribir el aprobador (falla si no hay `status:` en el frontmatter). Simétricamente, la reapertura se mecaniza: `sdd-prd-apply.py --reopen` baja `status:` a `in-review` y resetea `Aprobado por:` al placeholder pendiente; `wf-prd-change` (Paso 5) la invoca en vez de editar el frontmatter a mano. Invariante: un PRD `approved` ⟺ un humano aprobó su contenido vigente vía el gate de review; cualquier cambio posterior lo devuelve a `in-review` hasta re-aprobar.

**Alternativas descartadas.**
- *Dejar `status` como estaba y que D-028 detecte "sellado" solo por `Aprobado por:`* → deja el enum `status` (draft|in-review|approved) sin usar y el frontmatter incoherente; `status` es la señal natural del ciclo de aprobación.
- *Reabrir editando el frontmatter a mano en `wf-prd-change`* → frágil (edición de YAML por el agente); mismo motivo por el que la edición del review pasó a script (D-030). `--reopen` lo hace determinista y testeable.
- *Subir el status en `sdd-prd-frontmatter.py --fix`* → ese script repone campos **ausentes**, no cambia el ciclo de vida; mezclar responsabilidades. El sello es quien conoce la transición.

**Consecuencias / aprendizaje.** Cierra el ciclo del sello (D-027 quién · D-028 contenido vigente · D-032 estado coherente y reapertura determinista) y **hace realmente vivo D-028/Q4**, que estaba latente-muerto. Hallazgo destapado por conformance (run real), como D-026/D-031: un hueco pre-existente invisible en verde de tests hasta ejercitar el flujo. Backstops: `test_sdd_prd_apply.py` (seal sube approved, reopen resetea status+sello), `test_prd_change_reopens_seal` en `test_install_sh.py`.

**Referencias.** `sdd/scripts/sdd-prd-apply.py` (`--seal`/`--reopen`), `sdd/pipeline/prd/skills/wf-prd-review/SKILL.md` (Paso 6), `sdd/pipeline/prd/skills/wf-prd-change/SKILL.md` (Paso 5), `sdd/conformance/casos-de-uso/cu-02-prd.md` (CU-2.f) / `cu-07-cambio-producto.md` (CU-7.b), `sdd/tests/`, `sdd/CHANGELOG.md`.

---

## D-031 — Al orientar sobre readiness, el orquestador cita el veredicto mecánico y enruta; la lectura cualitativa del artefacto es del experto dentro de su skill

- **Fecha:** 2026-07-22 · **Estado:** Adoptada (implementada en `orchestration.md`). · **Relacionada:** [[D-030]] (el hilo principal no carga el PRD en el review), [[D-020]] (readiness mecánica), [[D-026]] (el orquestador no auto-arma overrides), principio del orquestador en `CLAUDE.md` ("no analizas, no ejecutas el trabajo directamente"), CU-2.e (probe A) / CU-2.h.

**Contexto.** En un run de conformance de CU-2.e (probe A), ante "¿cómo lo ves? ¿cuál es el siguiente paso?" el orquestador corrió `sdd-prd-ready.py` (correcto) **pero además** hizo `Read` del PRD completo en el hilo principal y emitió un diagnóstico cualitativo ("está bien planteado", "no veo contaminación técnica", "granularidad adecuada"). Eso es trabajo del `prd-expert` (con `kb-prd-expert` como autoridad) dentro de `wf-prd-review`: el orquestador (1) cargó el documento entero en su contexto —lo que D-030 evita en el review— y (2) opinó sobre estructura/contaminación **sin** la KB, pudiendo contradecir luego al gate (CU-2.h reserva el diagnóstico de contaminación al experto). La disciplina "no cargues/analices el artefacto en el hilo principal" existía **solo dentro** de `wf-prd-review` (Paso 3); a nivel de **enrutado** —antes de invocar skill alguna— la regla eager pedía el check mecánico pero no prohibía leer y opinar.

**Decisión.** Se generaliza D-030 al nivel de enrutado, transversal a fases: al orientar sobre readiness o el siguiente paso, el orquestador **cita el veredicto del verificador mecánico y enruta** a la skill de la fase para cualquier valoración de contenido; **no** hace `Read` del artefacto completo en el hilo principal ni emite su propio diagnóstico cualitativo (estructura, contaminación, calidad, alcance). Esa lectura, con la `kb-*` autoritativa, es del agente experto **dentro de su skill**. "¿Cómo lo ves?" se responde con el veredicto mecánico + "lo vemos en detalle en la revisión/análisis".

**Alternativas descartadas.**
- *Dejar que el orquestador lea y opine (estado previo)* → mete el documento entero en el contexto del hilo principal (el bloat que D-030 combate) y produce un diagnóstico sin KB que puede contradecir al gate; rompe el principio "el orquestador no analiza".
- *Restringirlo solo al PRD* → el hueco es transversal (cualquier "¿está listo mi X?"); se fija en la disciplina de orquestación, no en una fase.
- *Prohibir todo `Read` del orquestador* → demasiado: leer un veredicto de script o un fichero de estado pequeño es legítimo; lo que se veta es cargar el **artefacto de contenido** para diagnosticarlo a pelo.

**Consecuencias / aprendizaje.** El orquestador se mantiene como director (enruta con la evidencia mecánica) y la valoración de contenido queda donde tiene la autoridad (`kb-*`) y el aislamiento de contexto (la skill/su agente). Hermano de D-026 a nivel de enrutado: el mismo patrón de "el orquestador hace trabajo que debe delegar", cazado por conformance. Backstop: `test_orchestration_rule_delegates_qualitative_read` en `test_install_sh.py`; conductual en CU-2.e probe A.

**Referencias.** `sdd/pipeline/orchestration.md` ("Readiness antes de avanzar"), `sdd/pipeline/prd/skills/wf-prd-review/SKILL.md` (Paso 3, D-030), `sdd/conformance/casos-de-uso/cu-02-prd.md` (CU-2.e probe A), `sdd/tests/test_install_sh.py`, `sdd/CHANGELOG.md`.

---

## D-030 — La edición del PRD en el review se aplica por script determinista, no releyendo/reescribiendo el documento en el hilo principal

- **Fecha:** 2026-07-21 · **Estado:** Adoptada (implementada en `sdd-prd-apply.py` + `wf-prd-review`). · **Relacionada:** [[D-020]] (invariante 1:1 de `sdd-prd-ready.py`), [[D-029]] (grafo de dependencias / cascada), Regla 9 de `kb-sdd-conformance` (lo mecanizable no se deja al agente), convención `fork ⊥ AskUserQuestion` ([[D-015]]/[[D-016]]), CU-2.e (probe D) / CU-2.f / CU-2.h.

**Contexto.** `wf-prd-review` ya delega el *análisis* del PRD al `prd-expert` (Paso 4, read-only) y el Paso 3 declara "no cargues el PRD en el hilo principal". Pero las dos ediciones del fichero —decisiones de asunciones (Paso 5.5) y sello (Paso 6)— seguían en el hilo principal **sin mecanismo especificado**: la forma natural de aplicarlas con un LLM (`Read` del documento entero + `Write`) reintroduce en el contexto del orquestador justo el PRD que el Paso 3 pide no cargar. Y esas ediciones son **mecánicas** (marcar/quitar el marcador `[ASUNCIÓN]`, sustituir/borrar una afirmación, retirar la entrada `[ASN-XXX]`, escribir `Aprobado por:`), justo lo que la Regla 9 pide mecanizar.

**Decisión.** Un script determinista, `sdd-prd-apply.py`, aplica las decisiones que el gate recoge: `--confirm`/`--edit`/`--reject` sobre las asunciones y `--seal "<valor>"` para el sello. El orquestador lo invoca por `Bash` desde las decisiones acumuladas en el gate — nunca releyendo el fichero. `wf-prd-review` pierde `Read` y `Write` de `allowed-tools`. ⚠ **Premisa corregida por [[D-038]]:** aquí se afirmó que eso hacía **estructuralmente imposible** que el hilo principal cargue o reescriba el PRD. **No es cierto** — en conformance (CU-2.j pasada 3) main ejecutó `Read` y `Update` sobre el PRD con ese mismo `allowed-tools`: el campo es **declarativo, no una jaula**. La restricción sigue en pie, pero como **norma medida** (ver [[D-038]] regla 1 y el `diff` contra pristine de CU-2.h), no como imposibilidad mecánica. **"Quién edita" no cambia** (lo ejecuta el orquestador, no un agente); solo cambia el mecanismo. La ligadura marca-inline↔entrada se resuelve en dos pasadas (el marcador inline es anónimo por diseño): (1) **texto exacto normalizado** cuando la entrada cita la afirmación literal y es única; (2) para las residuales —la creación a veces parafrasea o abrevia la entrada— **máximo solapamiento de palabras de contenido**, con asignación golosa determinista. Precondición dura de 1:1 (exit 2 si no cuadra) y guarda fail-safe: una entrada a tocar que no case por texto ni comparta contenido con marca alguna no se asigna → exit 2, nunca se edita a ciegas.

**Alternativas descartadas.**
- *Delegar la escritura a un writer-agente vía la tool `Agent`* (espejo de `wf-prd-create`→`prd-expert`) → cambia mecánica por juicio de LLM (contra Regla 9, menos fiable para operaciones deterministas), obliga a reformular CU-2.e/2.f/2.h ("las ediciones las hace el orquestador, no el agente") y **debilita** la garantía de CU-2.h. `wf-prd-review` además no puede forkearse (usa `AskUserQuestion`).
- *Dejar el mecanismo sin especificar (estado previo)* → el LLM aplica con `Read`+`Write` del documento entero: el bloat que el Paso 3 quería evitar, reintroducido.
- *Ligadura puramente posicional (N-ésima marca ↔ N-ésima entrada)* → **frágil, descartada tras un fallo real**: una PRD regenerada emitió el cuerpo (exclusiones antes que reglas transversales) y la sección (numeración inversa) en órdenes distintos, y confirmar el bloqueo-PIN habría limpiado la línea de *inversiones*. La guarda de contenido no lo cazaba (compartían "financieros"). Por eso la ligadura primaria es por texto y el fallback por solapamiento, no por posición.
- *Ligadura por ID incrustado en el marcador* → obligaría a romper el diseño anónimo del marcador (y el conteo 1:1 de `sdd-prd-ready.py`); más invasivo.

**Consecuencias / aprendizaje.** El hilo principal deja de cargar el PRD para editarlo; las ediciones son deterministas y auditables por test black-box. Refuerza CU-2.h: el script solo aplica decisiones explícitas del usuario, sin margen para "cosecha" del LLM. Límite honesto (heredado de Q2a/[[D-029]]): la prosa de brief que dependía de una asunción rechazada (nivel b, líneas sin marca) no la toca el script — se resuelve en el gate con el usuario. Aprendizaje de campaña: la primera implementación fue **posicional** y una PRD regenerada real la rompió al vuelo (cuerpo y sección en órdenes distintos) — el propio conformance destapó el defecto antes de sellar; la ligadura pasó a texto-exacto + solapamiento de contenido, robusta a paráfrasis y reordenación. Cualquier residual sin contenido compartido falla seguro (exit 2), nunca edita a ciegas. Backstops: `test_sdd_prd_apply.py` (script, incl. regresión de orden divergente e integración con `sdd-prd-ready.py`), `test_prd_review_applies_edits_via_script` en `test_install_sh.py` (cita el script y verifica que `allowed-tools` no tiene `Read`/`Write`).

**Referencias.** `sdd/scripts/sdd-prd-apply.py`, `sdd/pipeline/prd/skills/wf-prd-review/SKILL.md` (frontmatter + Pasos 3/5.5/6), `sdd/conformance/casos-de-uso/cu-02-prd.md` (probe D de CU-2.e, CU-2.f), `sdd/tests/test_sdd_prd_apply.py`, `sdd/tests/test_install_sh.py`, `sdd/CHANGELOG.md`.

---

## D-029 — Las dependencias entre asunciones se registran en la creación y se hacen cumplir deterministamente en el review

- **Fecha:** 2026-07-19 · **Estado:** Adoptada (implementada en `sdd-prd-deps.py` + `kb-prd-expert`/`wf-prd-create`/`wf-prd-review`). · **Relacionada:** [[D-020]] (invariante 1:1 de `sdd-prd-ready.py`), Regla 9 de `kb-sdd-conformance` (lo mecanizable no se deja al agente), Regla 12 de `kb-prd-expert`, CU-2.e (probe D) / CU-2.j.

**Contexto.** En CU-2.e (runs 1 y 2) el gate de asunciones detectó la tensión ASN-006↔ASN-007 (rechazar "cuentas gestionables" deja huérfano "saldo por cuenta") **solo por razonamiento de la LLM** — la cazó las dos veces, pero por suerte, no por garantía, y trató la dependencia **distinto cada run** (nota pasiva vs. exclusión explícita). El formato `[ASN-XXX]` no registraba dependencias; el único invariante mecánico era el 1:1 (`sdd-prd-ready.py`). Dejar la cascada al juicio del agente en cada review es justo lo que la Regla 9 pide mecanizar.

**Decisión.** La dependencia **entre asunciones** se registra en la **creación** con un sufijo `· **Depende de:** ASN-XXX` (ID **pelado**, sin corchetes, para no colisionar con `ASN_ENTRY_RE` del 1:1) en la entrada dependiente, y se hace cumplir **deterministamente** en el review: `sdd-prd-deps.py` parsea el grafo, valida que no haya aristas colgantes ni ciclos, y en modo `--check --rejected` reporta **huérfanas** (dependiente de una rechazada que no se rechazó). `wf-prd-review` (Paso 5.5) carga el grafo para arrastrar los dependientes al gate al rechazar la asunción padre, y corre `--check` como backstop **pre-sello**. Alcance: **solo asunción↔asunción**; la dependencia asunción→contenido-de-brief (líneas sin marca) queda fuera (nivel b, futuro).

**Alternativas descartadas.**
- *Dejar la cascada al juicio de la LLM (estado previo)* → no determinista (comportamiento distinto entre runs de CU-2.e); una dependencia no detectada deja el PRD sellado con una huérfana.
- *Marcar también el contenido de brief dependiente* → requiere anotar líneas no-asunción; más invasivo. Aplazado a nivel b.
- *Verificar la dependencia sin registrarla en la creación* → imposible deterministamente (la relación es semántica); por eso se **recuerda** en la creación (juicio una vez) y se **cumple** después (mecánico).

**Consecuencias / aprendizaje.** La *identificación* de la arista sigue siendo juicio de la creación (recordado una vez), pero su *cumplimiento* pasa a ser determinista y auditable — estrictamente mejor que re-inferirla en cada review. Refuerza CU-2.h: la cascada es explícita y decidida por el usuario, no cosecha de la LLM. Límite honesto: si la creación **omite** una arista, el check no la inventa. Backstops: `test_sdd_prd_deps.py` (script), regresión en `test_sdd_prd_ready.py` (la arista pelada no infla el 1:1), `test_prd_review_uses_dependency_graph` en `test_install_sh.py`.

**Referencias.** `sdd/scripts/sdd-prd-deps.py`, `sdd/pipeline/prd/skills/kb-prd-expert/SKILL.md` (formato `Depende de:`), `sdd/pipeline/prd/skills/wf-prd-create/SKILL.md`, `sdd/pipeline/prd/skills/wf-prd-review/SKILL.md` (Paso 5.5), `sdd/conformance/casos-de-uso/cu-02-prd.md` (CU-2.j), `sdd/tests/`, `sdd/CHANGELOG.md`.

---

## D-028 — Un cambio de PRD reabre el sello: el sello solo lo establece el gate de review, nunca sobrevive a un cambio de contenido

- **Fecha:** 2026-07-18 · **Estado:** Adoptada (implementada en `wf-prd-change` Paso 5). · **Relacionada:** [[D-027]] (identidad del aprobador), [[D-024]] (regenerar un artefacto sellado), Regla 10 (SSoT del sello), CU-2.e (pregunta 4) / CU-7.

**Contexto.** Revisando el proceso PRD completo (CU-2.e, pregunta del usuario sobre cambios post-sello) se detectó que `wf-prd-change` actualizaba versión/fecha y reescribía las secciones afectadas, pero **no tocaba el sello** (`Aprobado por:` / `status: approved`). Tras un cambio, el PRD quedaba `approved` con una línea `Aprobado por:` que **atestiguaba un contenido que ya no existía** — un agujero de trazabilidad: el sello es un checkpoint humano (Regla 10) y certificaba algo distinto de lo que el documento decía. Hermano del hueco que cerró D-027 (rol anónimo): aquí el sello es directamente **stale**.

**Decisión.** Un cambio de contenido sobre un PRD sellado **reabre el sello**. `wf-prd-change` (Paso 5), si el PRD estaba sellado, baja `status:` a `in-review` y **resetea `Aprobado por:` al placeholder pendiente**, y remite a `wf-prd-review` para re-aprobar. El sello se establece **exclusivamente** por el gate de review (que re-verifica asunciones con `sdd-prd-ready.py` y re-captura la identidad, D-027): `wf-prd-change` **no re-sella por su cuenta**. Invariante que se preserva: *"sellado" ⇒ un humano aprobó **este** contenido a través del gate de review* — nunca un contenido anterior.

**Alternativas descartadas.**
- *Dejar el sello intacto tras el cambio (estado previo)* → el sello certifica contenido inexistente; rompe el propósito de Regla 10.
- *Re-sellar dentro de `wf-prd-change` con la fecha nueva* → duplica la lógica de sellado fuera del único gate que la posee, y saltaría la re-verificación de asunciones (un cambio puede introducir nuevas `[ASUNCIÓN]`). Un solo escritor del sello (el review) es más simple y seguro.
- *Bajar a `draft` en vez de `in-review`* → `draft` sugiere "sin revisar nunca"; `in-review` refleja mejor "revisado antes, pendiente de re-aprobar el cambio".

**Consecuencias / aprendizaje.** Cierra el ciclo de coherencia del sello junto a D-027: el sello **identifica a quién** aprobó (D-027) **el contenido vigente** (D-028). La fricción (re-review tras cada cambio) es proporcionada: un cambio de producto es significativo, y con 0 asunciones abiertas el re-sello es un solo paso. Backstop: `test_prd_change_reopens_seal` en `test_install_sh.py`.

**Referencias.** `sdd/pipeline/prd/skills/wf-prd-change/SKILL.md` (Paso 5), `sdd/pipeline/prd/skills/wf-prd-review/SKILL.md` (único sellador), `sdd/pipeline/spec/skills/kb-traceability-rules/SKILL.md` (Regla 10), `sdd/tests/test_install_sh.py`, `sdd/CHANGELOG.md`.

---

## D-027 — El sello de aprobación registra la identidad (nombre, precargado de git), no un rol genérico; el rol es opcional

- **Fecha:** 2026-07-15 · **Estado:** Adoptada (implementada en los 3 gates de sellado + `kb-traceability-rules` Regla 10). · **Relacionada:** [[D-020]] (readiness/sello), Regla 10 (SSoT del convenio `Aprobado por`), Regla 11 (release captura el SHA de git sin teclear — misma filosofía), CU-2.e/CU-2.f.

**Contexto.** Sellando el PRD en CU-2.e, el `AskUserQuestion` de aprobación ofrecía solo dos **roles** (`PM` / `Product Owner`) y el sello quedó `Aprobado por: PM (2026-07-17)`. El propósito declarado de Regla 10 es *"trazabilidad de autoría — **quién aprobó** — en proyectos multi-desarrollador"*, y un **rol pelado no identifica a nadie** (con 3 PMs, `PM` no dice quién). Además Regla 10 remarca que `Aprobado por` es un **dato humano no verificable** (ningún script lo escribe ni valida): su único valor es la rendición de cuentas, lo que hace un rol anónimo casi inútil. La capacidad de dar nombre ya existía (Regla 10 lo permitía, "Tech Lead — Ana"), pero el framing del `AskUserQuestion` empujaba al rol.

**Decisión.** El sello registra la **identidad del aprobador** como valor prioritario: el `AskUserQuestion` **precarga el nombre con `git config user.name`** como default (misma filosofía que `sdd-release.py` capturando el SHA: no se teclea lo que git ya sabe), con el **rol por fase como opcional/complementario**. Formato: `Aprobado por: <nombre> [(<rol>)] (<fecha>)`. Si git no da nombre, cae al rol por defecto. Aplica a los **tres** gates (PRD `wf-prd-review`, Plan `wf-plan-validate`, QA `wf-qa-verify`) porque Regla 10 es SSoT compartida. Se mantiene **No autoaprobar**.

**Alternativas descartadas.**
- *Seguir con rol pelado* → no cumple el propósito de Regla 10 (quién aprobó); un rol anónimo no es trazabilidad de autoría.
- *Pedir el nombre a mano cada vez sin default* → fricción innecesaria cuando `git config user.name` ya identifica al dev que corre el gate; el default precargado es override-able.
- *Escribirlo con un script determinista* → Regla 10 dice explícitamente que `Aprobado por` **no** es mecánicamente verificable (es un checkpoint humano); no se automatiza el sello, solo se **precarga** el default de la pregunta.

**Consecuencias / aprendizaje.** Un gate de atribución vale por **identificar a la persona responsable**, no por dejar una etiqueta de función. Alinea el sello de aprobación con la filosofía de la coordenada de release (Regla 11): el dato de trazabilidad que git ya conoce se precarga, no se teclea. Backstop: `test_seal_gates_prefill_approver_from_git` en `test_install_sh.py` (los 3 skills instalados citan `git config user.name`).

**Referencias.** `sdd/pipeline/prd/skills/wf-prd-review/SKILL.md` (Paso 6), `sdd/pipeline/plan/skills/wf-plan-validate/SKILL.md`, `sdd/pipeline/tasks/skills/wf-qa-verify/SKILL.md`, `sdd/pipeline/spec/skills/kb-traceability-rules/SKILL.md` (Regla 10), `sdd/tests/test_install_sh.py`, `sdd/CHANGELOG.md`.

---

## D-026 — Los overrides `--allow-*` los arma el usuario, nunca el orquestador; ante precondición bloqueante se presenta la elección explícita

- **Fecha:** 2026-07-15 · **Estado:** Adoptada (implementada en el carril eager `sdd-orchestration.md`). · **Relacionada:** [[D-020]] (gate de readiness PRD→spec que se auto-bypaseó), [[D-024]]/[[D-025]] (misma filosofía de cuándo interrumpir), CU-2.e (probe B).

**Contexto.** Validando **CU-2.e** (probe B: "pedir specs saltándose la review") sobre un consumidor real, con un PRD de 17 asunciones abiertas, al decir *"genérame directamente las specs"* el **orquestador (hilo principal) auto-armó `--allow-unreviewed-prd`** —infiriéndolo de la frase— y forkeó `wf-spec-features-first` con el flag ya puesto. El gate `OPEN_ASSUMPTIONS` de su Paso 2 ([[D-020]]) **nunca disparó** porque el override ya venía dado; la protección recayó, por suerte, en el gate *siguiente* (gaps críticos). Frágil: un PRD **sin** gaps críticos pero **con** asunciones abiertas se colaría a specs con solo un aviso, horneando 17 inferencias no validadas. La investigación de forks confirmó dónde vive el fallo: los skills de generación (`wf-spec-*`) van `context: fork` **sin** `AskUserQuestion`, así que la elección **no puede** presentarse desde el fork — el único punto de decisión es el hilo principal, al **construir los argumentos**. El carril eager ya decía "los gates no se bypasean", pero daba por hecho que el gate *dispara*; auto-armar el flag es un bypass que hace que **nunca reporte** el bloqueo.

**Decisión.** El orquestador **nunca auto-suministra un flag `--allow-*`** (`--allow-unreviewed-prd`, `--allow-open-critical-gaps`, `--allow-derived-scope-from-analysis`, …): son **escotillas de seguridad que arma el usuario**, no atajos inferibles de una petición impaciente. Ante una precondición que un `--allow-*` cruzaría: invocar el skill **sin** el override → el gate se detiene y **devuelve el bloqueo al hilo principal** → surfacearlo y presentar la elección explícita **con `AskUserQuestion`** (cerrar/revisar primero vs. continuar asumiendo el riesgo) → **solo** re-invocar con el flag si el usuario elige forzar. Se codifica en el carril eager `sdd-orchestration.md` (sección "Los gates son de su fase; no se bypasean").

**Alternativas descartadas.**
- *Formalizar el auto-armado (aceptar que "genérame las specs" implica el override)* → defendible por el aviso previo del probe A, pero **vacía [[D-020]]**: convierte una escotilla deliberada en el camino por defecto y la protección pasa a depender de que exista *otro* gate aguas abajo.
- *Mensaje pasivo + continuar* → el aviso se ignora; los derivados salen sobre alcance no revisado igualmente (mismo problema que descartó [[D-025]]).
- *Presentar la elección desde dentro del fork* → imposible con la arquitectura actual: `wf-spec-features-first` es fork sin `AskUserQuestion`. La decisión es del hilo principal por diseño.

**Consecuencias / aprendizaje.** Extiende el principio unificador de [[D-024]]/[[D-025]] a los flags de override: *interrumpir para que el usuario elija conscientemente lo de alto impacto, no decidirlo por él.* Confirma la convención de forks del ecosistema: **skill que necesita preguntar → no forkeado (hilo principal, con `AskUserQuestion`); skill de generación pesada → forkeado, sin preguntar, devuelve el bloqueo al principal.** El gate D-020 del skill se conserva intacto como backstop determinista (se detiene bien si se le invoca sin flag). Backstop: `test_orchestration_rule_forbids_auto_arming_overrides` en `test_install_sh.py`.

**Referencias.** `sdd/pipeline/orchestration.md` (sección de gates), `sdd/conformance/casos-de-uso/cu-02-prd.md` (CU-2.e probe B), `sdd/tests/test_install_sh.py` (backstop), `sdd/CHANGELOG.md`.

---

## D-025 — Una ruta de salida explícita es autoritativa; en divergencia con el layout se pregunta, nunca se redirige en silencio

- **Fecha:** 2026-07-13 · **Estado:** Adoptada (implementada en `wf-prd-create` Paso 4a). · **Relacionada:** [[D-024]] (gate de sobreescritura del mismo Paso 4; reverso de su principio), CU-2.i.

**Contexto.** Validando **CU-2.i** (`--output` explícito) con ≥3 corridas (Regla 9 de `kb-sdd-conformance`), 2 corridas honraron rutas no-default (`docs/…`, `entregables/v2/…`) pero la 3ª —misma clase de petición, "déjalo en `salidas/prd-app.md`"— el orquestador **la ignoró y redirigió en silencio a `prd/prd.md`**, razonando *"para mantener el pipeline coherente"* (`artifacts.prd` = `prd/`). Eso es el FALLO literal de CU-2.i y contradice el Paso 4 (*"si `--output`, úsalo"*). Comportamiento **no determinista** (2 PASS / 1 FALLO) — de no haber corrido las 3, se sella con un bug dentro. La tensión es real: si el PRD acaba en `salidas/`, `wf-prd-review`/`wf-spec-analyze` (que miran `artifacts.prd`) no lo encuentran. Pero **redirigir en silencio la intención explícita del usuario es peor** que el riesgo de coherencia, y un mensaje pasivo se ignora → el fallo aparece tarde.

**Decisión.** La ruta de salida que da el usuario —flag `--output` **o** en lenguaje natural ("déjalo en X")— es **autoritativa**. Si **coincide** con el path estándar (`artifacts.prd/prd.md` o el default), se usa sin más. Si **diverge**, el orquestador **no decide por su cuenta**: `AskUserQuestion` con dos opciones —**usar el estándar (recomendado)**, explicando que el pipeline lo espera ahí; o **dejarlo en la ruta dada**, avisando de que el pipeline no lo encontrará automáticamente—. **Prohibido** redirigir en silencio al estándar y **prohibido** honrar en silencio sin surfacear la divergencia.

**Alternativas descartadas.**
- *Redirigir al estándar (lo que hizo la corrida 3)* → pisa la intención explícita del usuario y contradice el contrato; además fue unilateral (lo anunció pero no dio elección).
- *Honrar en silencio + mensaje pasivo* → respeta la ruta pero el aviso de coherencia **se ignora** en el muro de salida; el usuario descubre tarde que review/specs no encuentran el PRD. Sin la interacción, el dato que le falta (el pipeline espera `prd/`) no aterriza a tiempo.
- *Honrar siempre sin avisar* → mismo problema de coherencia sin ninguna señal.

**Consecuencias / aprendizaje.** Complementa a [[D-024]] y cierra el **principio unificador de cuándo interrumpir**: *interrumpe para informar lo que el usuario **no sabe** y cambia su decisión; no interrumpas para re-confirmar lo que ya te dijo.* En D-024 (draft + "regenera") no se pregunta porque el usuario lo sabe todo; aquí sí, porque le falta el dato del layout. Regla 9 vindicada: la 3ª corrida cazó lo que 1-2 habrían sellado como PASS. Backstop: `test_prd_create_honors_explicit_output_path` en `test_install_sh.py` (el gate de divergencia sigue en el skill instalado).

**Referencias.** `sdd/pipeline/prd/skills/wf-prd-create/SKILL.md` (Paso 4a), `sdd/conformance/casos-de-uso/cu-02-prd.md` (CU-2.i reescrito + corrida 3 FALLO), `sdd/tests/test_install_sh.py` (backstop), `sdd/CHANGELOG.md`.

---

## D-024 — La confirmación de sobreescritura de artefactos se pondera por riesgo (sellado ≠ draft), no es un "¿seguro?" plano

- **Fecha:** 2026-07-12 · **Estado:** Adoptada (implementada en `wf-prd-create` Paso 4; **principio general** para regeneración de artefactos en todas las fases). · **Relacionada:** [[D-020]] (readiness/sello mecánico del PRD), CU-2.d.

**Contexto.** Al probar **CU-2.d** (regenerar un PRD que ya existe) sobre un consumidor real, el orquestador **no re-preguntó** antes de regenerar: razonó *"'regenerar' implica sobreescribirlo, la confirmación está dada"*. El Paso 4 de `wf-prd-create` **mandaba** un gate incondicional ("Ya existe `<path>`. ¿Deseas regenerarlo?" → No detiene). O sea: el agente **se saltó una instrucción escrita**. Pero al analizarlo, su conducta era **defensible**: tras un *"regenérame `prd/prd.md` con estas notas"* —consentimiento explícito y dirigido—, re-preguntar es *nagging* redundante (justo lo que un buen agente evita). El fallo de fondo no era del agente: era que el gate estaba **mal calibrado**. Un "¿seguro?" plano (a) es redundante cuando el comando ya es explícito y (b) es **ciego a lo único que de verdad importa**: si el PRD existente está **sellado/revisado** (asunciones confirmadas + `Aprobado por:`), regenerarlo desde un brief nuevo **destruye ese trabajo en silencio**. CU-2.d, tal como estaba, probaba solo el caso de bajo riesgo (draft) y habría marcado FALLO una conducta correcta.

**Decisión.** La confirmación de sobreescritura al **regenerar un artefacto existente** se **pondera por riesgo**, con el estado de aprobación como línea objetiva:
- **Artefacto sellado/aprobado** (para el PRD: `Aprobado por:` relleno, no `[pendiente]`) → **siempre** confirma, y el mensaje **avisa del descarte** del trabajo de review, **con independencia de lo explícito que sea el comando**. Declinar → detén sin escribir.
- **Draft sin sellar + intención explícita de regenerar** → **procede sin re-preguntar** (el consentimiento ya está dado).
- **Draft sin sellar + petición ambigua** (el usuario puede no saber que ya existe) → **gate ligero** que surfacea la colisión (protección anti-pisado accidental).

Implementado ahora en `wf-prd-create` Paso 4 (detección con `grep "Aprobado por:" | grep -qv pendiente`). Se declara **principio general**: cualquier `wf-*` que regenere un artefacto con estado de aprobación/sellado (spec validado, DESIGN.md, plan VALIDADO, …) debe seguir la misma ponderación cuando se toque su flujo de regeneración — no se propaga a las otras fases en este cambio, se hereda al mantenerlas.

**Alternativas descartadas.**
- *"Siempre preguntar" (mantener el Paso 4 plano)* → convierte en FALLO una conducta correcta (regenerar un draft recién pedido); *nagging* redundante en el caso común. Máxima protección nominal, peor UX real.
- *"Confiar en el comando explícito" (formalizar el salto del agente)* → cero fricción pero **cero red de seguridad**: deja pisar en silencio un PRD aprobado. Descarta justo el caso caro.
- *Detectar "trabajo invertido" por heurística más rica (nº de ediciones, longitud, etc.)* → no hay señal objetiva y estable; el sello `Aprobado por:` es binario, canónico ([[D-020]] / `kb-traceability-rules` Regla 10) y ya existe. Un draft muy editado a mano pero sin sellar no se protege — trade-off asumido: es coherente con su `status: draft`.

**Consecuencias / aprendizaje.** Un gate de confirmación no vale por interrumpir, sino por **la información que carga**: "¿te refieres a este fichero?" ya lo responde un comando explícito; lo que merece interrumpir es "vas a **descartar trabajo aprobado**". Cuando un test de conformance (CU-2.d) marca como desviación una conducta que resulta razonable, la lección suele ser que **el contrato está mal calibrado, no el agente** — mismo patrón que la Prueba 2 de CU-2.c (gate adyacente enmascarando el propio). Backstop determinista: `test_prd_create_overwrite_gate_is_risk_weighted` en `test_install_sh.py` (las 3 ramas siguen en el skill instalado).

**Referencias.** `sdd/pipeline/prd/skills/wf-prd-create/SKILL.md` (Paso 4), `sdd/conformance/casos-de-uso/cu-02-prd.md` (CU-2.d reescrito a 3 ramas + validación 2026-07-12), `sdd/tests/test_install_sh.py` (backstop), `sdd/CHANGELOG.md`.

---

## D-023 — Rootmap plano eliminado del cuerpo lazy; el pre-gate CU-13 se releva por reversibilidad + validación rodada

- **Fecha:** 2026-07-11 · **Estado:** Adoptada. Completa y supersede el paso pendiente de [[D-022]] (borrado del rootmap plano). · **Relacionada:** [[D-022]] (dejó este paso gated), [[D-021]] (carril eager), [[D-018]] (dual-audience).

**Contexto.** [[D-022]] dejó pendiente lo único irreversible —borrar el rootmap-tabla plano de las reglas de fase lazy— **gated en `CU-13.a–g` + `CU-11.a` sub-caso 1**. Al revisar ese gate: (1) el rootmap vive en ficheros **trackeados** (`pipeline/<fase>/CLAUDE.md`), así que revertir el borrado es **un `git revert`** — coste casi nulo; (2) [[D-022]] ya probó **empíricamente** que el rootmap lazy **no es load-bearing** (en CU-14.j el enrutado funcionó sin él cargado); el enrutado corre sobre las `description` (eager) + `sdd-routing.md` (eager); (3) correr `CU-13` **ahora** es prematuro: la campaña de conformance en curso (CU-2…) puede **reconfigurar el set de skills** (añadir/quitar/modificar), lo que invalidaría una corrida de CU-13 y, peor, obligaría a **re-mantener el rootmap en 5 ficheros** o dejarlo **derivar a stale** (ya se observó una copia pre-D-022 stale en una instalación de consumidor). Mantener el rootmap durante ese periodo de cambio es **coste y riesgo de deriva, no seguridad**.

**Decisión.** Se **releva** el pre-gate `CU-13.a–g` para este borrado (no se salta en silencio: se supera por esta decisión registrada) y se **ejecuta** el borrado. De las 5 `pipeline/<fase>/CLAUDE.md` se quita el rootmap-tabla plano + la sección "Reparto de trabajo" + la tabla "Agentes disponibles" (todo redundante con `orchestration.md`/`sdd-routing.md`/`description`). La regla de fase queda como **marcador fino**: frontmatter `paths:` (funcional — lazy-scope + validado por el check `rule-globs`) + intro + nota **"Audiencia"** (dual-audience) + puntero a `sdd-routing.md` y a `skill-registry.md`. Se **conserva** su función de marcador de instalación (existencia del fichero + `paths:`; comprobada por el hook y `sdd-init-detect.py`). La validación del enrutado pasa a **cobertura rodada**: cada CU conversacional ejercita intención→skill; ante una regresión, `git revert` o parchear la `description` del skill implicado. **`CU-13.a–g` queda como confirmación final opcional** cuando el set de skills se estabilice, ya no como pre-gate.

**Alternativas descartadas.**
- *Correr CU-13 ahora y luego borrar* → prematuro: el set de skills es inestable durante la campaña de conformance; la corrida sería invalidable y bloquearía la limpieza sin aportar seguridad real (el rootmap no es load-bearing).
- *Mantener el rootmap como referencia inofensiva* → durante la campaña hay que reeditarlo en 5 ficheros a cada cambio de skill o deja de reflejar la realidad (stale, peor que ausente). Sin upside: no lo usa el enrutado.
- *Borrarlo sin registrar la decisión* → sentaría el precedente de saltarse gates autoimpuestos cuando molestan; se supera por escrito para mantener honesto el rastro.

**Consecuencias / aprendizaje.** Un gate autoimpuesto no es sagrado si su premisa cambia; lo correcto no es ignorarlo sino **superarlo por decisión registrada**. La **reversibilidad barata** (ficheros trackeados) convierte "borra y observa con validación rodada" en estrategia legítima frente a "valida exhaustivo y luego borra", cuando lo que se borra no es load-bearing. Backstop nuevo determinista: `test_phase_rules_have_no_rootmap_table` en `test_install_sh.py` (la tabla no reaparece en ninguna fase).

**Referencias.** `sdd/pipeline/{prd,spec,design,plan,tasks}/CLAUDE.md` (cuerpos recortados), `sdd/tests/test_install_sh.py` (backstop anti-regresión), `sdd/CHANGELOG.md`, `sdd/conformance/casos-de-uso/cu-13-enrutado-matriz.md` y `cu-11-enrutado.md` (recalificados a confirmación final opcional).

---

## D-022 — Las `description` ya enrutan: el rootmap de las reglas es redundante; a eager va solo la desambiguación

- **Fecha:** 2026-07-09 · **Estado:** Adoptada; roll-out **completo** en las 5 fases (spec+prd+design+plan+tasks). El paso irreversible pendiente (borrar el rootmap plano lazy) se **completó vía [[D-023]]** (gate `CU-13.a–g` relevado por reversibilidad + validación rodada). · **Relacionada:** [[D-023]] (completa el borrado), [[D-021]] (carril eager), [[D-018]] (dual-audience + herencia en subagentes), [[D-019]] (capa 2 fuera de alcance).

**Contexto.** Las reglas de fase `.claude/rules/sdd-<fase>.md` son mayormente **enrutado de orquestador** pero cargan **lazy** (`paths:`), así que el orquestador —que rara vez toca ficheros al orientar— no las tiene cuando las necesita. Auditoría (3 Explore): (1) las **`description` de los skills ya cargan eager** y hacen el enrutado intención→skill — el rootmap-tabla de las reglas es **redundante** (prueba empírica: es lazy, no estaba cargado en las corridas de orientación de CU-14.j, y el enrutado funcionó igual → no es load-bearing); (2) lo que las descriptions **no** cubren es la **desambiguación** ("crea specs → features-first, no discover"; patrón "fase X"; elección de rigor) y las **precondiciones/fronteras de entrada**; (3) la **disciplina D** (autonomía por capas, "no bypasees", readiness mecánica) ya está **duplicada** en `orchestration.md`; (4) el framing **dual-audience** era inconsistente (solo `prd`/`orchestration` tenían nota "Audiencia."; `spec/design/plan/tasks` usaban "Eres el orquestador", contradicción de rol de [[D-018]] heredada por los subagentes escritores).

**Decisión.** El enrutado intención→skill lo hacen las **`description`** (eager); **no se replica el rootmap-tabla en eager**. A una regla eager dedicada **`sdd-routing.md`** (sin `paths:`, ensamblada topology-gated por `install_routing_rule` desde `pipeline/<fase>/routing.md`) va **solo la desambiguación + precondiciones/fronteras** que las descriptions no cubren. Se **deduplica** la disciplina D de las reglas de fase (ya vive en `orchestration.md`) y se completa el **dual-audience** de [[D-018]] en las reglas restantes. El **rootmap-tabla plano se queda lazy** en la regla de fase como referencia (inofensivo); su adelgazamiento hacia `skill-registry.md` queda **pendiente de validar** que el enrutado por descriptions aguanta (CU-11.a sub-caso 1) — no se borra a ciegas. **Piloto en spec**; roll-out a las demás fases tras validar.

**Alternativas descartadas.**
- *Mover todo el rootmap a eager* → paga coste de herencia en subagentes (toda regla eager la heredan los ~13 escritores sin opt-out) por información **duplicada** con las descriptions. Poco justificado una vez visto que las descriptions ya enrutan.
- *Borrar ya los rootmaps de las reglas lazy* → apuesta de calidad de enrutado tomada a ciegas en 5 ficheros; se difiere hasta validar CU-11.a sub-caso 1.
- *Dejar el enrutado lazy tal cual* → el orquestador sigue sin la desambiguación al orientar (el hueco que abrió [[D-021]]).

**Consecuencias / aprendizaje.** El coste fijo del catálogo son las `description` (eager); una `description` precisa **es** el enrutado, y duplicarlo en una regla es redundante. Lo que merece un carril eager propio es lo que la `description` no puede expresar: desambiguación entre skills de la misma fase y precondiciones de frontera. Backstops en `test_install_sh.py`: dual-audience en las reglas migradas; `sdd-routing.md` eager (sin `paths:`), dual-audience y topology-gated; la precondición de spec se movió fuera de `sdd-spec.md` al carril eager. Validación de que descriptions bastan: **CU-11.a sub-caso 1** (routing "crea specs" → features-first, no discover) — habilita el roll-out y el futuro adelgazamiento del rootmap. Fuera de alcance: capa 2 de [[D-019]] (~150 emisiones `/wf-X` user-facing).

**Estrategia de roll-out (refinada 2026-07-09, tras el piloto).** Al planear el roll-out se separó lo que el gate-por-piloto conflaba: **(a) añadir la regla eager `sdd-routing.md`** (relocalizar desambiguación lazy→eager, dedup D, dual-audience) es **aditivo y reversible** —el orquestador pasa a *ver* la desambiguación al orientar y el rootmap-tabla se queda como referencia; no hay regresión posible, solo más contexto disponible—; **(b) borrar el rootmap plano** es **irreversible** y es lo único que de verdad necesita la prueba conductual. El gate del piloto frenaba (a) por miedo a (b), y además forzaba probar spec antes de validar PRD (fuera de orden de pipeline). **Resolución:** el roll-out de (a) se hace **fase a fase ya**, respaldado por lo determinista (suite unit + `CU-1.u` on-disk); la **validación conductual** cae en la campaña de conformance de cada fase, en orden, vía **`CU-13.a–g`** (matriz frase→skill por fase) — no hace falta inventar CUs nuevos: CU-13 ya *es* esa checklist. Solo **(b) sigue gated** en que esos `CU-13.x` pasen. Cero apuestas a ciegas, nada fuera de orden.

**Auditoría de cobertura (2026-07-09, tras cerrar el roll-out).** Auditoría exhaustiva con 6 agentes (una por fase + transversal) cruzando cada `routing.md`/cambio contra toda la suite de conformance, para garantizar que ninguna desambiguación movida a eager quede sin CU que pille su regresión al testear. Resultado: cobertura mayoritaria y **sin disciplina huérfana** tras el dedup (readiness/no-bypass en CU-14.j, capas/enrutado en CU-11.a, instalación en CU-1.t/CU-1.u). Halló y corrigió **3 contradicciones** — (1) `style_family`/`clarity_vs_brand`: la matriz CU-13 enrutaba a `wf-design-delta` contra la SSoT (`kb-design-governance` R4 → `wf-design-intake`, es cambio de **brief**); `routing.md` ya estaba bien, se corrigió CU-13.c/g#2; (2) la propia `kb-design-governance` se autocontradecía (R2.3 decía `delta`, R4 dice `intake`) → R2.3 reescrita; (3) CU-1.u *Mecanismo* stale (test renombrado + semántica de ausencia ya superada). Y cerró **5 huecos** con casos nuevos: `CU-3.r`.5 (light→standard forzado por shared models/entidades/alcance), `CU-13.a` (duda conceptual → `prd-expert`), `CU-13.c` ("que decida menos la IA" → intake; negativo branch↔delta), `CU-6.l`.5 (taxonomía de gaps del handoff, códigos reales de `kb-plan-expert`). Dual-audience de las reglas de fase queda con cobertura **solo determinista** (`test_phase_rules_are_dual_audience`), aceptable por ser un riesgo textual. Cerrado como v0.58.1.

**Referencias.** `sdd/pipeline/{prd,spec,design,plan,tasks}/CLAUDE.md` (reglas lazy adelgazadas, las 5) y `.../routing.md` (carril eager, las 5), `sdd/pipeline/design/skills/kb-design-governance` (fix SSoT R2.3), `sdd/install.sh` (`install_routing_rule`), `sdd/tests/test_install_sh.py`, `sdd/conformance/casos-de-uso/`: `cu-11-enrutado.md` (CU-11.a), `cu-13-enrutado-matriz.md` (matriz por fase + fixes), `cu-01-inicializar.md` (CU-1.u), `cu-03-specs.md` (CU-3.r), `cu-06-entrega.md` (CU-6.l), `sdd/docs/entender/tecnico.md`.

---

## D-019 — Handoff agnóstico a comandos: el orquestador no surfacea nombres de skill al usuario

- **Fecha:** 2026-07-09 · **Estado:** Adoptada (capa 1; capa 2 en roll-out) · **Relacionada:** [[D-021]] (vive en la regla eager), CU-11.a. *(Reservada desde [[D-020]]; se ubica arriba por orden de recencia aunque su número sea anterior.)*

**Contexto.** El ecosistema se concibe **agnóstico a comandos**: el usuario conduce por conversación y el hilo principal mapea intención → workflow/agente y lo invoca, construyendo los argumentos (ahí viven CU-11.b/c/g/h). Pero en la práctica el orquestador **narra** los nombres técnicos —"¿lanzo `wf-prd-review <archivo_prd.md>`?", "lo natural es `wf-spec-features-first`"— (visto en las corridas de CU-14.j). Eso invita al usuario a **teclear `/wf-x` con argumentos a mano**, saltándose la construcción de argumentos del hilo principal y comprometiendo las validaciones. El nombre de skill es necesario **internamente** (para invocar), no para mostrarlo.

**Decisión.** El hilo principal **no surfacea proactivamente nombres de skill (`wf-*`) ni slash-commands al usuario**; describe la acción en **lenguaje natural** ("reviso el PRD contigo", "genero las specs por feature"). Los nombres son internos para invocar. Excepción: si el usuario pide explícitamente el comando o el nombre técnico, se le da. Implementación en **dos capas**: **(1)** disciplina de narración del orquestador → va en la **regla eager** `sdd-orchestration.md` (misma casa que [[D-021]]: aplica en toda interacción, antes de tocar ficheros) — **adoptada ahora**; **(2)** las plantillas de salida user-facing de los propios `wf-*` (~25 sitios que emiten "ejecuta /wf-X") y la presentación del rootmap → **roll-out pendiente**, plegado con la auditoría de la capa de reglas (línea D-022).

**Alternativas descartadas.**
- *Prohibir del todo pronunciar un nombre de skill* → hostil si el usuario pregunta explícitamente por el comando; la regla es "no surfacear proactivamente", no "callar bajo orden directa".
- *Solo hacer el roll-out de las plantillas (capa 2) sin la disciplina eager (capa 1)* → deja el hueco principal (lo que el orquestador improvisa al narrar) sin cubrir; la capa 1 ataca el 80% del riesgo de inmediato.
- *Renombrar/ocultar los skills* → rompe la invocación y el mapa humano; el problema no es el nombre, es surfacearlo.

**Consecuencias / aprendizaje.** El nombre de una pieza puede ser **necesario para el sistema y ruido (o trampa) para el usuario**: la interfaz conversacional debe traducir intención↔acción sin exponer el andamiaje. Backstop en `test_install_sh.py` (la regla eager contiene la disciplina de comunicación). Cobertura de conformance: CU-11.a (sub-caso de narración: el orquestador no surfacea `wf-*`/comandos). El roll-out de la capa 2 cerrará los sitios donde los propios workflows emiten comandos.

**Referencias.** `sdd/pipeline/orchestration.md` (sección "Comunicación con el usuario"), `sdd/install.sh` (`install_orchestration_rule`), `sdd/tests/test_install_sh.py`, `sdd/conformance/casos-de-uso/cu-11-enrutado.md` (CU-11.a).

---

## D-021 — Disciplina de orquestación en una regla *eager* dedicada (`sdd-orchestration.md`)

- **Fecha:** 2026-07-08 · **Estado:** Adoptada · **Relacionada:** [[D-020]] (el gate mecánico que esta regla complementa), [[D-018]] (dual-audience + límite del subdirectorio).

**Contexto.** El fix de [[D-020]] tiene un núcleo mecánico robusto (`sdd-prd-ready.py` dispara **dentro** de la invocación del skill y corta el daño), pero su **capa de guía** vive en las reglas de fase `.claude/rules/sdd-<fase>.md`, que son **lazy por `paths:`**: solo cargan cuando el hilo toca un artefacto que matchea. El escenario que destapó el bug —el orquestador respondiendo *"¿cuál es el siguiente paso?"* **sin** leer/editar ningún fichero— **no** carga esa guía, así que el orquestador podía seguir declarando "PRD listo" por topología antes de que el gate mecánico lo parase. Es un fallo de **corrección/UX** (frase equivocada), no de integridad (el daño ya lo corta D-020).

**Decisión.** La disciplina **transversal** que el orquestador necesita **antes de tocar ficheros** (readiness mecánica y no por topología; orden del pipeline; no bypasear gates) vive en una regla dedicada `.claude/rules/sdd-orchestration.md` que se genera **sin frontmatter `paths:`**. Confirmado en la doc oficial de Claude Code (*memory* §path-specific-rules): una regla **sin `paths:` se carga eager** (al arrancar la sesión, como un `CLAUDE.md`); solo es lazy *porque* declara `paths:`. La regla la genera `install.sh` (que ya es dueño de `.claude/rules/`), a partir de la fuente única `pipeline/orchestration.md`, con una línea específica de la frontera PRD→Spec **activada por topología** (`has_phase prd && has_phase spec`). Complementa —no sustituye— el gate mecánico de D-020 y las reglas de fase lazy. Es **dual-audience por construcción** (invariantes de proyecto, no rol en 2ª persona): al ser eager la heredan también los subagentes escritores, igual que las reglas de fase — mismo invariante que [[D-018]].

**Alternativas descartadas.**
- *Inyectar trozos de cada `CLAUDE.md` de fase en el `CLAUDE.md` raíz* → dos dueños del mismo fichero (lo autora `wf-project-init` con `Write`, install lo omite con `--no-claude-md`) y engorda el raíz eager con N resúmenes de fase. Lo eager-worthy es disciplina **cross-fase**, pequeña, no un resumen por fase.
- *Splice de un bloque gestionado (markers + awk, patrón SDD-BOOTSTRAP) en el raíz* → misma pelea de dueños con `wf-project-init`. El carril nativo de rules lo evita.
- *Hook `SessionStart`/`UserPromptSubmit` inyectando la disciplina* → el texto de hook entra como *system-reminder* (prioridad menor que la memoria) y añade lógica de shell con estado; peor que un fichero de memoria para esto.
- *Extracción por marcador (`<!-- sdd:eager -->`) de cada fase* → maquinaria (contrato de marcador + splice) desproporcionada para **una** frontera con verificador hoy. Si aparecen más, se evoluciona sin cambiar el destino (`sdd-orchestration.md`).

**Consecuencias / aprendizaje.** El eje **eager vs lazy** de las rules no es "rules = lazy": lo determina la **presencia de `paths:`**. Eso da un tercer carril que no estábamos usando —una regla eager separada del `CLAUDE.md` raíz y de las reglas de fase— ideal para "disciplina siempre presente + detalle de fase bajo demanda". **Robustez validada (CU-14.j, `myops-app-specs` 0.52.0, 2026-07-09):** el carril eager **carga incluso lanzando la sesión desde un subdirectorio** (`prd/`) — 3/3 corridas aplicaron la disciplina. Esto **refina [[D-018]]**: la memoria *eager* (`CLAUDE.md` raíz + rules sin `paths:`) se carga por **walk-up desde cualquier cwd**; lo que NO dispara desde un subdirectorio son las **rules lazy** (su glob `paths:` es relativo a la raíz y no matchea el path relativo al cwd) — eso, y no un "des-registro de memoria", fue lo que D-018 observó. El carril eager no tiene glob que desalinear, así que es inmune: un **argumento a favor de mover a eager el enrutado del orquestador** (línea de trabajo D-022). La recomendación "operar desde la raíz" sigue vigente, pero por las **rules de fase lazy** y la resolución de paths relativos, no por el carril eager. **Hallazgo cosmético:** `sdd-prd-ready.py` sale con código `2` (no listo) por diseño; ejecutado pelado la UI lo marca "fallido" y colapsa stdout, pero el veredicto está ahí y el orquestador lo lee — se endureció el texto de la frontera para dejarlo explícito. Backstops en `test_install_sh.py`: `sdd-orchestration.md` existe, **sin** clave `paths:` (eager), dual-audience (sin rol en 2ª persona) y con la línea de readiness **topology-gated**. Cobertura de conformance: CU-1.t (instalación en toda topología) y CU-14.j (carga eager al orientar sin tocar ficheros, raíz **y** subdir).

**Referencias.** `sdd/pipeline/orchestration.md`, `sdd/install.sh` (`install_orchestration_rule`), `sdd/tests/test_install_sh.py`, `sdd/conformance/casos-de-uso/cu-01-inicializar.md` (CU-1.t), `sdd/conformance/casos-de-uso/cu-14-secuenciacion.md` (CU-14.j). Docs Claude Code: *memory* (path-specific rules; import; discovery).

---

## D-020 — Gate de readiness PRD→spec mecánico (`sdd-prd-ready.py`)

- **Fecha:** 2026-07-08 · **Estado:** Adoptada · **Relacionada:** [[D-018]] (evidencia empírica de CU-2.a/b); reserva del 1:1 de CHANGELOG 0.50.0. *(D-019 queda reservada para el handoff agnóstico a comandos — punto 1, roll-out aparte.)*

**Contexto.** Probando **CU-2.e** en el consumer real `myops-app-specs` (prueba A: *"¿cuál es el siguiente paso?"*), el orquestador —con un PRD con **9 `[ASUNCIÓN]` abiertas y sin sellar**— declaró **"El PRD está listo"** y enrutó directo a `wf-spec-features-first`, **saltándose el gate de revisión**. Habría horneado 9 inferencias sin confirmar en los specs. Causa raíz (a nivel de source): (1) el orquestador decidió el siguiente paso por **topología de ficheros** (`spec/features/` vacío → toca spec), no por la readiness del PRD; (2) **ninguna precondición de readiness** en la entrada a spec — `wf-spec-features-first` Paso 2 solo comprueba existencia, Paso 2.5 gatea gaps `[CRÍTICO]` del `_analysis.md`, no las `[ASUNCIÓN]`/sello del PRD; (3) **no hay gate mecánico** PRD→spec (los `sdd-seal`/hook son de plan/tasks); (4) **la red documentada no existía**: `prd/CLAUDE.md` prometía que *"las asunciones bajan como gaps a `wf-spec-analyze`"*, pero `wf-spec-analyze` (Checks 1-3) **no lee las `[ASUNCIÓN]`** — era aspiracional.

**Decisión.** La readiness de un PRD para pasar a spec se verifica **mecánicamente** con `sdd-prd-ready.py` (autor≠verificador, mismo principio que `sdd-seal.py`), **no** por juicio del orquestador ni por topología de ficheros. Un PRD es `READY` si no tiene `[ASUNCIÓN]` inline abiertas, cumple el 1:1 (marcas == entradas `[ASN-XXX]`) y está sellado (`Aprobado por:` real). El gate se aplica en las entradas de spec con **respuesta graduada**: `OPEN_ASSUMPTIONS`/`ASSUMPTION_MISMATCH` (basadas en marcadores → inequívocamente un PRD SDD en revisión) **bloquean** la generación de specs (`wf-spec-features-first`) salvo override explícito `--allow-unreviewed-prd`; `UNSEALED` es **advisory** (no bloquea — evita false-bloquear documentos de requisitos crudos en `wf-spec-analyze`, que no tienen concepto de sello). `wf-spec-analyze`/`wf-spec-discover` **surfacean** las asunciones abiertas sin bloquear (producen análisis/mapa, no specs) — esto **implementa de verdad** la red antes aspiracional. El orquestador, ante *"¿siguiente paso?"*, comprueba readiness antes de recomendar spec y **nunca declara "PRD listo" sin la evidencia del script**. El mismo script cierra la **verificación mecánica del 1:1** de `wf-prd-review` Paso 5.5 (reserva de CU-2.a/b) y excluye las menciones del token en prosa que inflaban el `grep` crudo (falsa-positiva de CU-2.b).

**Alternativas descartadas.**
- *Gate duro (revisar siempre, sin escapatoria)* → rompe la coherencia del ecosistema, donde todos los gates permiten override explícito (`--allow-open-critical-gaps`, `--allow-derived-scope-from-analysis`) y proceder sin review es un camino legítimo.
- *Solo guía (reescribir precondiciones con grep improvisado)* → deja el chequeo como "grep a ojo" del agente; no cierra la reserva del 1:1 ni la falsa-positiva de prosa. El script es reutilizable y determinista.
- *Bloquear también en `UNSEALED`* → false-bloquearía documentos de requisitos crudos (sin sello) que `wf-spec-analyze` acepta legítimamente. Por eso `UNSEALED` es advisory.
- *Confiar en `wf-spec-analyze` como red ("bajan como gaps")* → no leía las `[ASUNCIÓN]`; la promesa era falsa. Se implementa surfaceándolas.

**Consecuencias / aprendizaje.** La readiness de un artefacto **no es "el fichero existe" ni "la carpeta siguiente está vacía"**, sino un estado verificable (asunciones resueltas + sello); confiarlo al juicio del hilo principal lo hace saltable. Aprendizaje: toda frontera de fase que dependa de un estado del artefacto anterior necesita un verificador mecánico, no prosa "no avances si…". Backstops: test unitario de `sdd-prd-ready.py` y `test_install_sh.py` (la regla `sdd-spec.md` contiene la precondición de readiness). Cobertura de conformance: CU-2.e probes A/B/F (regresión del bug). Pendiente de roll-out: `wf-spec-fast-track` (generador de spec directo) aplica hoy el gate vía `wf-spec-features-first` cuando se invoca en cadena; endurecer su invocación directa en una pasada posterior.

**Referencias.** `sdd/scripts/sdd-prd-ready.py`, `sdd/pipeline/spec/CLAUDE.md`, `sdd/pipeline/prd/CLAUDE.md`, `sdd/pipeline/spec/skills/{wf-spec-features-first,wf-spec-analyze,wf-spec-discover}/SKILL.md`, `sdd/pipeline/prd/skills/wf-prd-review/SKILL.md` (Paso 5.5), `sdd/conformance/casos-de-uso/cu-02-prd.md` (CU-2.e), `sdd/tests/test_sdd_prd_ready.py`.

---

## D-018 — Las reglas de fase (`.claude/rules/sdd-<fase>.md`) son dual-audience: no afirman un rol de orquestador exclusivo

- **Fecha:** 2026-07-07 · **Estado:** Adoptada; roll-out **completo** en las 5 fases (prd+spec+design+plan+tasks), cerrado con [[D-022]] · **Relacionada:** [[D-022]] (lo cerró junto al carril eager `sdd-routing.md`), [[D-021]]

**Contexto.** Probando **CU-2.a** en el consumer real `myops-app-specs`, el subagente `prd-expert` cargaba en su contexto `.claude/rules/sdd-prd.md` (además del `CLAUDE.md` raíz). Esa regla es contenido de **orquestador** —"*Eres el orquestador. No redactas el documento final por tu cuenta*"— e inyectarla en el agente cuyo único trabajo es **redactar** el PRD es una **contradicción de rol**. Se confirmó vía docs de Claude Code que **los subagentes heredan toda la jerarquía de memoria del hilo principal (CLAUDE.md + project rules) por defecto**, y que **solo los built-in Explore/Plan se lo saltan, sin campo de frontmatter para opt-out**. Las reglas por `paths:` disparan cuando se lee/escribe un fichero que matchea el glob — y el agente escritor toca ese fichero por definición. El leak es sistémico: afecta a ~13 subagentes escritores (pipeline + overlay KMM); los read-only (`disallowedTools: Write, Edit`) son inmunes.

**Decisión.** El contenido de las reglas de fase debe ser **dual-audience**: describir el **reparto de trabajo** de la fase (cierto para cualquier lector) en vez de **direccionar en 2ª persona al orquestador** ni **afirmar un rol** ("eres el orquestador / no redactas"). Se conserva todo el contenido útil (rootmap de enrutado, tabla de agentes, precondiciones, frontera create→review); solo cambia el *marco*. El rootmap **no se puede borrar ni mover a la raíz**: en topologías authoring/consumer, el `CLAUDE.md` raíz que autora `wf-project-init` es mínimo y **apunta** a las reglas, así que la regla de fase es la **única** fuente de enrutado de esa fase para el hilo principal. Piloto en `pipeline/prd/CLAUDE.md`; roll-out al resto (spec/design/plan/tasks/kmm) tras validar.

**Alternativas descartadas.**
- *Excluir la regla de los subagentes por config* → **no existe** mecanismo documentado (ni frontmatter de agente ni opt-out de rules).
- *Levantar Claude por directorio de fase para "escopar" por cwd* → los globs `paths:` matchean **relativo a la raíz del proyecto, no al cwd**; lanzar en un subdirectorio no re-escopa nada y rompería el pipeline cross-fase (features-first lee `prd/` y escribe `spec/` en una sesión). No es cómo funciona la carga perezosa.
- *Guard de audiencia ligero* (prepend "si eres subagente, ignora el rol de abajo") → depende de obediencia a prosa (lo que el diseño por `paths:` evita) y deja el cuerpo contradictorio intacto.
- *Reorganizar skills/agents por directorio de fase* → no arregla el leak (es prosa de rules, no skills); además los **agents no son escopables** en Claude Code y `paths:` en una skill **no** retira su descripción del contexto.

**Consecuencias / aprendizaje.** Un fichero de instrucciones que se carga por `paths:` es leído por **quien toque el artefacto**, hilo principal o subagente indistintamente; escribirlo en 2ª persona asumiendo un único lector (el orquestador) inyecta órdenes equivocadas en el especialista. Aprendizaje: el contenido cargado por path debe ser **agnóstico del lector**. Backstop determinista en `test_install_sh.py`: el invariante se elevó de la regla PRD (`test_prd_rule_is_dual_audience`, piloto) a **las 5 fases** (`test_phase_rules_are_dual_audience` sobre `DUAL_AUDIENCE_PHASES`), que verifica presencia de la nota `Audiencia.` y ausencia de framing de rol en 2ª persona. Roll-out cerrado con [[D-022]].

**Evidencia empírica (2026-07-08, validación de CU-2.a en `myops-app-specs`).** Al lanzar la sesión desde los subdirectorios `prd/` y `spec/` (en vez de la raíz), la regla `sdd-prd.md` **no llegó a cargarse** —ni siquiera con el glob `**/prd*.md`, que sí matchearía—: lanzar en un subdirectorio no re-escopa la regla, la **desregistra** (Claude no ancla la memoria de proyecto en la raíz). Corolario que matiza esta decisión: el riesgo del contenido de la regla se concentra en el **hilo principal** (que, en authoring/consumer, se queda sin su única fuente de enrutado de fase), no en el subagente escritor —cuyo contrato real es su system prompt + `kb-prd-expert`, ambos independientes de la regla—. En las tres corridas el `prd-expert` redactó correctamente con y sin la regla cargada, confirmando que el marco dual-audience lo deja como contexto benigno. Refuerza el descarte de "levantar Claude por directorio de fase": no solo no escopa, sino que rompe el enrutado del hilo principal. Recomendación operativa derivada: lanzar siempre desde la raíz del proyecto.

**Refinamiento (2026-07-09, evidencia de CU-14.j / [[D-021]]).** El diagnóstico "lanzar en subdir desregistra la memoria de proyecto (ni raíz ni rules cargan)" era **demasiado fuerte**. Al validar la regla **eager** `sdd-orchestration.md` (sin `paths:`) desde `prd/`, **sí cargó** por walk-up (3/3 corridas aplicaron la disciplina). El modelo correcto: la memoria *eager* (`CLAUDE.md` raíz + rules sin `paths:`) se carga por walk-up desde cualquier cwd; lo que falla desde un subdirectorio son las **rules lazy** (`paths:`), porque su glob es relativo a la raíz y no matchea el path relativo al cwd — no es un des-registro de memoria, es un desalineamiento de glob. La recomendación "lanzar desde la raíz" se mantiene (por las rules de fase lazy y la resolución de paths), pero **no** aplica al carril eager.

**Referencias.** `sdd/pipeline/prd/CLAUDE.md`, `sdd/install.sh` (`install_phase_rule` L307-318), `sdd/tests/test_install_sh.py`, CU-2.a. Docs Claude Code: *sub-agents* (What loads at startup), *memory* (path-specific rules).

---

## D-017 — Las fuentes externas del consumer se pinean por ruta RELATIVA, con detección explícita de fuente movida

- **Fecha:** 2026-06-21 · **Estado:** Adoptada · **Extiende:** D-011/D-012 (subsistema de drift cross-repo)

**Contexto.** Probando CU-1.i esc. 1 en repos reales (`myops-app-specs` SSoT + `myops-app-dev-kmm` consumer web), `wf-project-init` guardó `artifacts_source` como **ruta absoluta** (un path tipo `/abs/…/myops-app-specs`). Un consumer pinea sus fuentes (SSoT de specs, y repo de diseño si aplica) por path en `project-init.json`; con ruta absoluta, **mover o clonar el workspace rompe el enlace** aunque la disposición relativa entre repos se mantenga. Además, el `CLAUDE.md` raíz ya mostraba la relativa (`../myops-app-specs`) → incoherencia doc/estado.

**Decisión.** Dos piezas:
1. **Pin por ruta relativa.** `wf-project-init` persiste `artifacts_source` y `design_source` **relativos a la raíz del repo consumer** (`os.path.relpath`, típicamente `../<repo>`). Los lectores ya resolvían relativo a la raíz (`sdd-source-drift.py`: `root / path`; los tests cubrían `specs_repo`), así que es solo cambio de escritura — y la absoluta seguía resolviendo (`root / abs = abs`), por lo que los consumers ya inicializados no se rompen. La relativa sobrevive al caso común: mover el **workspace entero** preservando el offset.
2. **Detección explícita de fuente movida.** La relativa **no** protege el movimiento *independiente* de un repo (cambia el offset; ningún esquema sobrevive → hay que re-apuntar). Antes ese caso era un **fallo silencioso**: `sdd-source-drift.py` marcaba `git_ok:false`, indistinguible de "fuente sin git". Ahora emite **`exists`** por fuente y **`any_missing`** de nivel superior; `wf-prepare-plan` (Paso 2.5) lo consume como precondición y **se detiene** si la fuente que necesita no resuelve, indicando re-apuntar con `/wf-project-init` → "Completar / ampliar".

**Alternativas descartadas.**
- *Seguir con ruta absoluta* → rompe al mover/clonar el workspace, el caso de portabilidad más común; e incoherente con el `CLAUDE.md` que ya mostraba relativa.
- *Intentar auto-reparar un movimiento independiente* → imposible sin heurística frágil (buscar el repo por nombre podría acertar el equivocado). Lo correcto es un diagnóstico claro y re-apuntar explícito por el usuario.
- *Dejar la detección como `git_ok:false`* → colapsa dos causas distintas (movido vs sin git) en una señal; el `exists` explícito las separa.

**Consecuencias / aprendizaje.** El pin cross-repo es ahora portable por defecto y los movimientos independientes dejan de ser silenciosos. Aprendizaje: una señal booleana que **colapsa dos causas** (`git_ok` = "tiene git Y pin conocido Y resuelve") esconde el fallo accionable; separar el "resuelve en disco" (`exists`) del "está bajo git" hace el diagnóstico preciso. El veredicto sigue siendo **advisory** en el subsistema de drift; la única parada dura es en `wf-prepare-plan` cuando la fuente que necesita para trabajar no existe.

**Referencias.** `bootstrap/skills/wf-project-init/SKILL.md` (5.C0 / 5.C1b / Paso 8) · `scripts/sdd-source-drift.py` (`exists`, `any_missing`) · `pipeline/plan/skills/wf-prepare-plan/SKILL.md` (Paso 2.5) · `tests/test_sdd_source_drift.py` · `conformance/casos-de-uso/cu-01-inicializar.md` (CU-1.i) · D-011/D-012 (subsistema de pin/drift cross-repo).

---

## D-016 — Barrido completo del bug *fork ⊥ interacción de usuario*: `wf-sdd-update` y `wf-bug` al hilo principal; el lint cubre también gates de confirmación

- **Fecha:** 2026-06-21 · **Estado:** Adoptada · **Extiende:** [[D-015]] (mismo principio, instancias restantes)

**Contexto.** Validando D-015 en una sesión real, `/wf-sdd-update` reprodujo el síntoma que D-015 acababa de cerrar en las KMM: era `context: fork`, presentaba el plan de actualización y **"Espera confirmación del usuario"** (Paso 3.4) antes de instalar — pero un fork no puede usar `AskUserQuestion`, así que la ejecución forked devolvía una respuesta genérica sin hacer el trabajo real. Es el **hermano olvidado de `wf-project-init`**: el sweep de 0.33.0 des-forkeó éste pero no a `wf-sdd-update`. Al rastrear el ecosistema (`grep 'context: fork'` + frase de confirmación) apareció un **tercer caso idéntico, `wf-bug`**: forkeado, con gate "**Espera confirmación** antes de actuar" (Paso 3) seguido de "Paso 4: Actuar según triaje". El gate de triaje es el corazón de la skill (un fix sin confirmar es justo lo que prohíbe) y bajo fork no puede renderizarse. El `FORK-INTERVIEW` de D-015 **no** los cazaba: su `INTERVIEW_RE` solo tenía marcadores de *entrevista* (`pregunta secuencialmente`, …), no de *gate de confirmación* (`espera confirmación`).

**Decisión.** Des-forkear las dos skills restantes (mismo principio que D-015 y `wf-project-init`):
- **`wf-sdd-update`** corre en el hilo principal; el gate del Paso 3 usa `AskUserQuestion` (Actualizar / Cancelar). No hay exploración pesada que delegar — reinstala lo que `project-init.json` ya declara —, así que queda **todo en hilo principal** (sin `Agent`), espejo de `wf-project-init`.
- **`wf-bug`** corre en el hilo principal; el gate de triaje del Paso 3 usa `AskUserQuestion` (Confirmar / Reclasificar / Cancelar). **Conserva `Agent`**: el trabajo pesado —el fix de código— se sigue delegando al agente owner (Paso 4), que aísla su contexto igual de bien. Es el ejemplo canónico del principio: *preguntar → orquestador; trabajo pesado → subagente*.
- **Lint:** `INTERVIEW_RE` se extiende con `espera(r) confirmación` para que `FORK-INTERVIEW` cubra también gates de confirmación, no solo entrevistas. Sigue siendo **warning** (heurística de prosa).

**Alternativas descartadas.**
- *Arreglar solo `wf-sdd-update`* → dejaría `wf-bug` con el mismo bug latente y silencioso; el barrido sistemático de esta clase de bug exige cerrarla entera.
- *No extender el lint* → la frase `espera confirmación` se escaparía y un futuro `context: fork` + gate volvería a colarse (es exactamente cómo se escapó `wf-sdd-update` del sweep de 0.33.0).
- *Añadir el marcador laxo "confirmación del usuario"* → marcaría `kb-design-style-taxonomy` (que la contiene). Se elige el verbo de gate `espera(r) confirmación`, preciso; además el check fork solo corre sobre `wf-*`, no sobre `kb-*`.

**Consecuencias / aprendizaje.** Tras el fix, `FORK-INTERVIEW` marca **0** skills reales (ambas arregladas); el lint queda como red de seguridad para la próxima. `wf-sdd-update` es **bootstrap global** → su corrección se propaga a `~/.claude` re-ejecutando `setup.sh` (no `wf-sdd-update`); `wf-bug` es overlay de proyecto → llega a los proyectos con `wf-sdd-update`. Aprendizaje: cuando una clase de bug se descubre, el barrido debe ser **exhaustivo por construcción** (grep del patrón completo, no solo el caso que saltó), y el detector debe ampliarse al **fraseo real** que se escapó, no solo al que ya cazaba.

**Referencias.** `bootstrap/skills/wf-sdd-update/SKILL.md` (Paso 3 gate) · `pipeline/tasks/skills/wf-bug/SKILL.md` (Paso 3 gate; `Agent` en Paso 4) · `scripts/sdd-structural-lint.py` (`INTERVIEW_RE`, `FORK-INTERVIEW`) · `tests/test_sdd_structural_lint.py` (`test_fork_confirmation_gate_flagged_as_warning`) · [[D-015]] · 0.33.0 (fork ⊥ `AskUserQuestion`).

---

## D-015 — Las skills de stack que entrevistan corren en el hilo principal (no `context: fork`); el fork solo para delegación pura

- **Fecha:** 2026-06-21 · **Estado:** Adoptada · **Extiende:** la regla de 0.33.0 (fork ⊥ `AskUserQuestion`)

**Contexto.** Al validar D-014, el primer `/wf-kmm-init` real sobre un proyecto destapó cuatro síntomas: (1) hacía las preguntas como texto plano ("No hay herramienta AskUserQuestion disponible"), (2) re-preguntaba los `targets` que `wf-project-init` ya había capturado, (3) relanzaba `Skill(wf-kmm-init)`, y (4) preguntaba "¿el código está en otro repo?" en un proyecto **standalone** (donde el código vive aquí). Causa raíz de (1) y (3): `wf-kmm-init` tenía `context: fork` + `agent: kmm-explorer`, y su modo configure es una **entrevista de 10 preguntas** — pero un fork no puede usar `AskUserQuestion` (mismo muro que cerró 0.33.0). (2) y (4) eran aguas abajo: no leía `project-init.json` (ni `targets` ni `topology`), así que el agente del fork improvisaba la topología. El sweep de 0.33.0 corrigió 8 skills concretas y la regla de lint `FORK-ASKUSER-CONFLICT` solo caza forks que **declaran** `AskUserQuestion`; estas skills **entrevistan en prosa** sin declararla, así que pasaron por debajo del radar. De las 8 `wf-kmm-*` (todas `context: fork`), solo 2 entrevistan: `wf-kmm-init` y `wf-kmm-environments`.

**Decisión.** Una `wf-*` que **entrevista** al usuario (preguntas que ramifican, confirmaciones que bloquean escritura) corre en el **hilo principal** (sin `context: fork`) y usa `AskUserQuestion`; el trabajo pesado lo delega vía la tool `Agent` (contexto aislado, ortogonal al fork). El `context: fork` queda reservado para skills de **delegación pura** (toman params de `$ARGUMENTS` o los infieren leyendo el repo, sin preguntar). Aplicado a `wf-kmm-init` (configure entrevista con `AskUserQuestion`; detect delega a `kmm-explorer` vía `Agent`; lee `project-init.json` para no re-preguntar `targets` ni improvisar topología) y `wf-kmm-environments` (entrevista + confirmación de matriz en hilo principal; implementación delegada a `kmm-platform-integrator`). Las otras 6 `wf-kmm-*` son delegación pura → se quedan con fork.

**Alternativas descartadas.**
- *Globalizar / dejar el fork y pedir en prosa* → es exactamente el bug no determinista que 0.33.0 prohibió.
- *Convertir el lint en blocking para forks-que-entrevistan* → la señal es prosa (heurística) y arriesga falsos positivos sobre las 6 que dicen "confirmar **o** inferir". Se elige **warning** `FORK-INTERVIEW` (no blocking): avisa sin romper CI por una heurística.

**Consecuencias / aprendizaje.** Nueva regla de lint `FORK-INTERVIEW` (warning): `context: fork` + marcadores fuertes de entrevista en prosa (`pregunta secuencialmente`, `una opción a la vez`, `esperar respuesta`, `antes de tocar ning…`), calibrada para no marcar las 6 sanas. Aprendizaje: el lint estructural debe vigilar no solo lo que una skill **declara** sino lo que su **prosa hace** — una entrevista sin `AskUserQuestion` declarada es igual de rota bajo fork. Es overlay de proyecto: los proyectos KMM ya inicializados reciben las skills corregidas con `wf-sdd-update`.

**Referencias.** `tech/kmm/skills/wf-kmm-init/SKILL.md` · `tech/kmm/skills/wf-kmm-environments/SKILL.md` · `scripts/sdd-structural-lint.py` (`FORK-INTERVIEW`, `INTERVIEW_RE`) · `tests/test_sdd_structural_lint.py` · `conformance/casos-de-uso/cu-12-overlay-kmm.md` (CU-12.b) · 0.33.0 (fork ⊥ `AskUserQuestion`) · D-014 (que hizo invocable `wf-kmm-init` y destapó esto).

---

## D-014 — El init técnico de stack es un handoff a sesión nueva (directiva `specialist-init-pending`), no una invocación in-session

- **Fecha:** 2026-06-20 · **Estado:** Adoptada · **Corrige:** el Paso 8.5 de `wf-project-init`

**Contexto.** Probando el escenario 3 de CU-1.h (standalone con stack KMM detectable) sobre un repo real, el despacho prescrito en `wf-project-init` Paso 8 (*"invocar `wf-<stack>-init` via Skill tool"*) falló con **`Unknown skill: wf-kmm-init`**. Dos defectos encadenados: **(A)** el Paso 6 instala el backbone **antes** de escribir `project-init.json`, así que la cola de `install.sh` que aplica el overlay (`tech/<stack>/install.sh`) es un no-op (aún no hay stack declarado) → el overlay, que **contiene** `wf-kmm-init`, no se instala antes del despacho. **(B)** aunque el overlay estuviera en disco, skills y agentes se cargan al **arrancar** la sesión; un overlay recién instalado no es invocable in-session (y en proyecto virgen `.claude/skills/` ni se vigila hasta reiniciar). `wf-kmm-init` además forka a `kmm-explorer` (agente local), que tampoco estaría cargado. La sesión del init solo "se salvó" porque el orquestador improvisó un re-run de `install.sh`; el flujo prescrito era incapaz de cumplirse.

**Decisión.** Separar instalación de ejecución. **(A)** `wf-project-init` Paso 8, tras escribir `project-init.json`, **re-ejecuta `install.sh <fases>`**: ahora la cola ve el stack y aplica el overlay por el camino canónico (nunca `tech/<stack>/install.sh` a mano). **(B)** el init **no** invoca `wf-<stack>-init`; su trabajo acaba en "overlay instalado y verificado en disco". La ejecución del init técnico se difiere a una **sesión nueva** y la dispara el hook `SessionStart` con una directiva nueva, **`specialist-init-pending`**: pendiente = `specialist_workflow` no nulo en `project-init.json` **y** sin run en `.sdd/stack-runs.jsonl`. Es **precondición contextual, no bloqueante**: en PRD/spec/design solo se menciona en una línea; antes de cualquier trabajo de stack (plan/tasks/implementación) se invoca `wf-<stack>-init` como precondición. Modelo idéntico a `init-pending`/`mode-undecided`: el hook detecta, la directiva instruye, el modelo actúa en una sesión donde el overlay **sí** está cargado.

**Alternativas descartadas.**
- *Invocar `wf-<stack>-init` in-session tras instalar el overlay* → imposible de raíz: la carga de skills/agentes es al arranque de sesión (verificado con claude-code-guide); en proyecto virgen ni hay live-reload.
- *Globalizar los `wf-<stack>-init` en `setup.sh`* → no basta (forkan a agentes y KBs locales del overlay, que seguirían sin cargar) y contamina el namespace global de cualquier usuario con todos los stacks. 
- *Auto-run inmediato o pregunta al arrancar* → más intrusivo; lanzar el cuestionario técnico a quien solo quería escribir un PRD. La precondición contextual no interrumpe las fases tempranas.

**Consecuencias / aprendizaje.** Señal de detección genérica y agnóstica de stack: `.sdd/stack-runs.jsonl` (lo escribe `wf-<stack>-init` al completar) — no hace falta que el hook conozca el fichero de estado de cada stack. Aprendizaje: un workflow **no puede invocar via Skill tool un skill que él mismo acaba de instalar** en la misma sesión; lo recién instalado se ejecuta en la siguiente. El init deja el sistema *listo*; el primer uso lo *activa*.

**Referencias.** `bootstrap/skills/wf-project-init/SKILL.md` (Paso 8.5, Paso 10) · `scripts/sdd-init-detect.py` (`specialist_status`, subcomando `specialist-status`) · `bootstrap/sdd-session-check.sh` (rama `specialist-init-pending`) · `bootstrap/claude-global-block.md` (directiva + fallback) · `install.sh` (cola de re-aplicación de overlay, L475) · `conformance/casos-de-uso/cu-01-inicializar.md` (CU-1.h.3 instalación, CU-1.s emisión+handoff) · `conformance/casos-de-uso/cu-14-secuenciacion.md` (CU-14.i: disparo como precondición del trabajo de stack).

---

## D-013 — La topología `design` instala rol `full`, no `system` (corrección de D-011)

- **Fecha:** 2026-06-20 · **Estado:** Adoptada · **Corrige:** D-011 (slice 12.3)

**Contexto.** Probando el init de la topología `design` (CU-1.b/CU-1.q) sobre repos reales se vio que
solo se instalaba `design-system-architect` + workflows de sistema: **faltaban** `design-feature-architect`,
`wf-design-feature-prototype`, `wf-design-variant` y `kb-design-feature-artifacts`. Causa: D-011 (12.3)
fijó `DESIGN_ROLE_BY_TOPOLOGY["design"] = "system"`, y `install.sh --design-role=system` instala solo el
agente de sistema. Pero la **definición** de la topología `design` (en el propio SKILL) es que el repo
autora **ambos** niveles: el sistema visual (`DESIGN.md`/brief/tokens) **y** los bundles de feature
(flows/views/ui_prompt + overrides `base ⊕ override per-view`). Con rol `system`, el repo de diseño **no
podía producir los bundles per-view** — que son el núcleo de D-011 (lo que prueba CU-5.w). El bug era
auto-contradictorio: el `CLAUDE.md` generado y el informe del init prometían `wf-design-feature-prototype`
y `features/<nombre>/design/`, workflows que no quedaban instalados.

**Decisión.** La topología `design` deriva **`design_role: full`** (ambos agentes). `full` aquí significa
"los dos agentes de la fase design" (system + feature); **no** arrastra plan/tasks — eso lo gobierna
`phases` (`["design"]`), no el `design_role`. Distinción que se mantiene: `authoring` con diseño sigue en
rol `system` (ahí los consumers derivan flows/views en SUS repos), mientras que el repo `design` **sí**
autora los bundles localmente — esa es su razón de ser. Cambio en la función pura testeada
(`DESIGN_ROLE_BY_TOPOLOGY`), no en prosa.

**Alternativas descartadas.**
- *Mantener `system` y documentar que los bundles se autoran en otro sitio* → contradice D-011 (el repo
  `design` ES el SSoT de los bundles per-view) y deja `wf-design-feature-prototype` sin hogar.
- *Ampliar el rol `system` para que instale también el feature-architect* → rompe la semántica de `system`
  (que en authoring debe seguir instalando solo el sistema); el rol correcto ya existe: `full`.

**Consecuencias / aprendizaje.** `RepairPlanTest` se endurece: un repo `design` con rol `system` es
**inconsistente** (`needs_repair`), y la reparación determinista lo lleva a `full`. Los proyectos `design`
inicializados antes de este fix tienen el feature-architect ausente: se reparan con `/wf-project-init` →
"Completar / ampliar" (el repair-plan instala lo que falta) tras `bash setup.sh`. Aprendizaje: cuando una
topología declara una capacidad ("autora bundles de feature"), el rol de instalación debe **instalar el
agente que la ejecuta** — el `design_role` no es una etiqueta descriptiva, es el contrato de qué se instala.

**Referencias.** `scripts/sdd-init-detect.py` (`DESIGN_ROLE_BY_TOPOLOGY["design"]`) ·
`tests/test_sdd_init_detect.py` (`RepairPlanTest.test_design_topology_derives_full`,
`test_design_topology_system_role_is_inconsistent`) · `bootstrap/skills/wf-project-init/SKILL.md` (rama
DESIGN, def de topología, esquema) · `conformance/casos-de-uso/cu-01-inicializar.md` (CU-1.q) ·
`install.sh` (`--design-role`) · D-011 (topología design).

---

## D-012 — Un solo SSoT de diseño por producto: las opciones de diseño son un fork excluyente, con guard advisory en el consumer

- **Fecha:** 2026-06-19 · **Estado:** Adoptada

**Contexto.** Tras D-011, el diseño puede vivir en dos sitios: co-localizado en el repo `authoring`
(rol `system`, para equipos pequeños) o en un repo `design` dedicado (topología `design`). Probando
`CU-1.b` se planteó la duda: ¿es contraproducente ofrecer diseño en `authoring` **y** además la
topología `design`? ¿No deberíamos unificar todo el diseño en el repo SSoT y usarlo siempre, aunque
el equipo sea pequeño? El riesgo real percibido: que un producto acabe con **dos `DESIGN.md`**
(uno co-localizado en specs + uno en el repo de diseño), violando la SSoT.

**Decisión.** Las dos opciones **se mantienen** y son un **fork excluyente** (no una duplicación):
el diseño de un producto vive **en exactamente un sitio** — co-localizado en `authoring` (equipo
pequeño, un repo) **o** en un repo `design` dedicado (equipo de diseño / multi-superficie), nunca en
ambos. No se unifica a la fuerza en el repo de diseño: obligar a un equipo de un solo repo a mantener
**dos** repos solo para tener un `DESIGN.md` es el coste que D-011 decidió evitar (regresión de
ergonomía, no mejora). El invariante **«un solo SSoT de diseño por producto»** se protege con un
**guard advisory en el consumer** —el único punto que ve ambos repos a la vez—, no con un hard-block
en el init (los repos se inicializan por separado y no se ven entre sí):
1. Detección **determinista** en `sdd-source-drift.py` (`dual_design_ssot`): un consumer con
   `design_source` cuyo `artifacts_source` **también** declara la fase `design` → `dual_design_ssot:
   true`. Expuesto en `check` (campo `design_ssot`).
2. `wf-prepare-plan` (Paso 2.5) y `wf-project-init` 5.C1b **avisan** (no bloquean): el handoff se
   resuelve por `design_source` y el co-localizado queda ignorado; unifica en un solo SSoT.
3. **Nudge** en la pregunta de diseño de `authoring` (5.A2): responde *No* si el diseño vivirá en un
   repo dedicado.

**Alternativas descartadas.**
- *Quitar diseño de `authoring`* → mata el caso pequeño co-localizado que D-011 protegió expresamente.
- *Unificar siempre en el repo de diseño (obligatorio)* → peaje de dos repos para todo equipo; peor
  ergonomía sin beneficio para quien no tiene función de diseño separada.
- *Hard-block en el init* → inviable: el init es per-repo y no ve de forma fiable el otro checkout. El
  consumer es la única junta donde el conflicto es observable.
- *Dejarlo solo en prosa* → el conflicto quedaba silencioso (el handoff elige `design_source` sin
  avisar de que hay un `DESIGN.md` compitiendo); por eso el veredicto es determinista (script testeado).

**Consecuencias / aprendizaje.** El guard es **advisory**, no bloqueante: una ventana de migración
(mover el diseño de co-localizado a repo dedicado) es legítima y transitoria. La detección vive donde
el conflicto es visible (consumer), no donde se origina (dos inits independientes). `DualDesignSsotTest`
(4 casos) fija el invariante. Conformance: `CU-1.i` (caso 4) y `CU-6.k`.

**Referencias.** `scripts/sdd-source-drift.py` (`dual_design_ssot`) · `tests/test_sdd_source_drift.py`
(`DualDesignSsotTest`) · `bootstrap/skills/wf-project-init/SKILL.md` (5.A2 nudge, 5.C1b guard) ·
`pipeline/plan/skills/wf-prepare-plan/SKILL.md` (Paso 2.5) · D-011 (topologías de diseño).

---

## D-011 — Topología `design`: repo de diseño SSoT con bundles de feature por target (base ⊕ override) y consumer multi-fuente

- **Fecha:** 2026-06-18 · **Estado:** Propuesta (borrador — pendiente de implementación en ciclo aparte)

**Contexto.** El modelo de 3 topologías (D-005) coloca el sistema de diseño (`DESIGN.md`, rol `system`)
dentro de `authoring` y deja que los `consumer` autoren `flows`/`views` localmente (rol `feature`)
consumiendo un único SSoT (`artifacts_source`, CU-1.i). La regla de copia agnóstica de flows/views
(hoy inline en la **Regla 7** de `kb-design-feature-artifacts`, `SKILL.md:131-136` — no hay "Regla 8"
numerada) **fuerza `flows`/`views` a una sola copia agnóstica** + "Notas responsive"; solo el
`ui_prompt` diverge por familia. Eso **no contempla** ni el split de componentes nativos Android/iOS
ni phone/tablet, que exigen divergencia a nivel views/flows. Investigando el init se vio además que
`surfaces`/`targets`/`has_ui` de `project-init.json` son **write-only** (se escriben, nadie los lee
aguas abajo) y que `target_platforms` no se deriva de nada (el template del brief lo hardcodea a
`iOS/Android`, `design_brief_template.md:18`).

**Decisión.** Se adopta una **4ª topología `design`**: un repo SSoT de diseño que autora (a) el
sistema agnóstico (`DESIGN.md`, brief, tokens; `design_role: system`, `phases:["design"]`, sin
prd/spec/plan/tasks) y (b) los **bundles de feature por design target**. Núcleo:
1. **Design target** = etiqueta con convención **validada** `<familia>[-<plataforma>][-<formfactor>]`;
   la **familia es obligatoria** y debe ser una de `{mobile, web, desktop}` (token del que se deriva
   `target_platforms`); el resto de tokens, libres.
2. **base ⊕ override**: `flows`/`views` se autoran una vez como **base agnóstica**; un target añade
   su **override** solo cuando diverge de verdad (componentes nativos, layout tablet). El consumidor
   resuelve `base ⊕ override(target)` (el override gana donde existe). Relaja la regla de copia
   agnóstica preservando el principio de no duplicar (solo se materializa lo que cambia).
3. Los `flows`/`views` de feature **se mueven al repo `design`** en el caso consumer-con-repo-`design`:
   el consumer los resuelve en **solo lectura** y ya no los autora localmente — esto **supersede a
   CU-1.i** para ese caso. El caso co-localizado (`authoring`/`standalone`) los mantiene locales.
4. `target_platforms` (familias) se **deriva** de los design targets declarados.
5. El consumer con UI pasa a ser **multi-fuente**: declara dónde vive el `DESIGN.md` (mismo SSoT de
   specs o repo `design` aparte → `design_source` + pin) y qué `design_targets` consume.
6. **Aditivo, no reemplazo**: el caso co-localizado sigue válido para equipos pequeños.

**Expansión de fit (decisión de producto, no técnica).** El fit declarado de la fase design
(`pipeline/design/CLAUDE.md`, `design/README.md`, ROADMAP 7.1) era **equipos SIN diseñador dedicado,
greenfield, prototipado Stitch/web-generic**; ROADMAP 7.6 descartó Figma con la condición textual
*"reconsiderable solo si el fit se expandiera a equipos con diseñador propio — decisión de producto,
no técnica"*. Esta decisión **es esa expansión**: el caso que motiva D-011 (repo de diseño SSoT
propio, multi-superficie con divergencia nativa Android/iOS y phone/tablet, varios repos de código
consumiendo un diseño compartido) es propio de **organizaciones con función de diseño dedicada y
escala multi-repo**. Se asume conscientemente: el ecosistema pasa a cubrir también ese perfil. No
reabre Figma por sí sola (sigue fuera por 7.6), pero **retira la premisa "sin diseñador" como límite
duro** y la condición de 7.6 queda satisfecha — quien quiera reevaluar Figma ya tiene el gancho. El
fit escrito en `design/CLAUDE.md`/`README.md` se actualizará **cuando la capacidad se implemente**
(no antes, para no anunciar lo que aún no existe); este ciclo solo registra la decisión y reconcilia
el ROADMAP.

**Alternativas descartadas.**
- *Modelar diseño como overlay/tecnología* → rompe el modelo de fases/targets; es topología, no stack.
- *Etiquetas de target totalmente libres* → la derivación de `target_platforms` (familias) deja de ser
  determinista; por eso la familia es token validado obligatorio.
- *Duplicar `flows`/`views` completos por target* → viola el principio de no duplicar; el override
  parcial sobre una base compartida lo respeta.
- *Mantener `flows`/`views` locales en el consumer con repo `design`* → reintroduce duplicación y
  divergencia entre repos; el SSoT único de diseño lo evita (a costa de staleness cross-repo, abajo).
- *Mantener el fit "sin diseñador" y no soportar este caso* → descartado: el equipo objetivo real
  (PM + diseño + devs) lo necesita; el coste de no cubrirlo es que el diseño multi-superficie viva
  fuera del pipeline. La expansión es deliberada (ver arriba).

**Consecuencias / aprendizaje.** (1) La 4ª opción de Q1 **agota el cupo de 4** de `AskUserQuestion`
(`wf-project-init/SKILL.md:283-289`): futuras topologías necesitarían otra UX (pregunta en dos pasos).
(2) Mover flows/views al repo `design` **multiplica la superficie de staleness cross-repo** (specs
SSoT + design SSoT + N repos de código): exige pin de `design_source` y extender `wf-design-sync`
para drift entre repos — es subsistema, no nota al pie. (3) Convierte campos write-only en derivables.
(4) **Corrección factual respecto al borrador inicial:** `derive_target_platforms` **no existe** hoy;
el trabajo previo (2) entregó `derive_design_role` + los write-only, no esta función — hay que
**construirla** net-new siguiendo el patrón de D-010 (función pura testeada en `sdd-init-detect.py`).
(5) **Grano del override (RESUELTO): per-view, con la divergencia de sistema empujada al `DESIGN.md`.**
El override de `views` es **por vista entera** (la unidad ya es la pantalla — `views` es "SSoT de
pantallas"): si un design target tiene override de una vista, gana esa vista completa; si no, hereda la
base intacta. Resolución trivial y determinista (alineada con D-009/D-010), y coherente con el layout
ya bocetado (`targets/<target>/<feature>_views.md` es un fichero de vista completo). **Per-component se
descarta**: `views` es markdown en prosa, no un árbol de componentes con IDs estables, y fusionar prosa
componente-a-componente sería el grano *menos* determinista. La especificidad de **componente nativo**
(Material vs HIG, patrón de navegación) **no es de la vista sino del sistema**: vive en una **capa de
mapeo de componentes por plataforma en el `DESIGN.md`** (esto resuelve también la open Q1) — así la
vista queda agnóstica y solo se overridea cuando la *composición/layout* de la pantalla diverge de
verdad (tablet), o se overridea `flows` si cambia la navegación. *Per-state* queda como refinamiento
futuro opt-in (el vocabulario de estados es cerrado, así que es viable) solo si el uso real muestra
vistas que divergen en un único estado y duplicarlas molesta — YAGNI hasta entonces. Coste aceptado:
una vista overrideada **re-enuncia sus estados no cambiados**; está acotado a las vistas que divergen.
(6) **Vocabulario de familias fijado:** `target_platforms` ∈ `{mobile, web, desktop}` (3 familias).
`tablet` NO es familia: es un **form-factor** dentro de `mobile`/`desktop` (un token más del design
target, p. ej. `mobile-tablet`), tal como `kb-design-layout` ya lo trata como breakpoint. Esto resuelve
la incoherencia del borrador (que en un punto listaba `{mobile, web, desktop, tablet}`).

**Implementación por fases.** Se ejecuta de forma incremental, no en bloque (con el grano del override
ya resuelto —ver (5)—, el **subsistema de staleness cross-repo** es el punto de mayor riesgo restante). **Este ciclo (foundational, valor
independiente):** se construyen en `sdd-init-detect.py` las funciones puras testeadas
`derive_target_platforms` (familias desde design targets) y la validación de la convención de
etiquetas (familia obligatoria), siguiendo el patrón de `derive_design_role` (D-010); y se alinea el
vocabulario del template del brief (`design_brief_template.md`, hoy `iOS/Android`) a familias. Estas
piezas tienen valor por sí solas (dan función a campos hoy write-only) aunque el resto no se construya.
**Ciclos posteriores (diferido, tras cerrar el grano del override):** Q1 (4ª opción `design`), esquema
de `project-init.json` (`design_targets`, `design_source`/pin), `kb-design-feature-artifacts` (promover
la regla de copia agnóstica a una **Regla 8** numerada y relajarla), wiring del consumer multi-fuente,
subsistema de staleness cross-repo y `CU-01`.

**Referencias.** `floating-splashing-eclipse.md` (propuesta completa) ·
`pipeline/design/skills/kb-design-feature-artifacts/SKILL.md:131-136` (regla de copia agnóstica) ·
`bootstrap/skills/wf-project-init/SKILL.md` (Q1, límite de 4 opciones) ·
`scripts/sdd-init-detect.py` (`derive_design_role` como precedente de patrón) ·
`pipeline/design/skills/kb-design-brief/references/design_brief_template.md:18` (familias) ·
D-005 (topologías), D-010 (función pura testeada).

---

## D-010 — La reparación de un init a medias es determinista: `phases` es el contrato, no se repregunta el rol

- **Fecha:** 2026-06-18 · **Estado:** Adoptada

**Contexto.** Probando `CU-1.e` (`init-incomplete`: una fase declarada en `phases` de
`project-init.json` pero sin instalar), dos corridas del mismo escenario divergieron: en authoring
con `design` declarado y `design_role: null`, una corrida abría un `AskUserQuestion` ("instalar design
system / quitar design") y otra resolvía sola a `system`. Ambas pasaban el criterio de entonces
(*"repara sin re-entrevistar de cero"*) porque una pregunta puntual no es re-entrevistar. La causa raíz:
el SKILL recitaba en prosa la lógica de reparación y dejaba latitud al agente, así que el rol —que es
**determinado** por la topología— se trataba como ambiguo.

**Decisión.** La reparación (extend) es **determinista y silenciosa**: `phases` es el contrato (es el
mismo campo con el que el hook declara `init-incomplete`), así que lo declarado-pero-no-instalado **se
instala**, y el `design_role` se **deriva de la topología** (authoring→`system`, consumer-con-UI→
`feature`, standalone→`full`) — sin `AskUserQuestion` para decidir el rol. Quitar una fase declarada
**no** es reparación: es un cambio de alcance explícito (otra acción), no una verja insertada en cada
repair. Para sacar el *qué* de la prosa, la derivación vive como **función pura testeada** en
`sdd-init-detect.py` (`derive_design_role` + subcomando `repair-plan`, con `missing_phases`,
`expected_design_role`, `needs_repair`); el SKILL solo dice "aplica el `repair-plan`, no preguntes". El
agente informa **post-hoc** de lo instalado (p. ej. "instalé `design` rol system porque estaba
declarado; quítalo con 'Completar / ampliar' si no lo querías").

**Alternativas descartadas.**
- *Preguntar siempre instalar-vs-quitar al reparar* → relitiga la misma declaración que disparó el
  repair; añade fricción al caso común; el rol nunca es ambiguo dada la topología.
- *Respetar `design_role: null` como "no hay diseño"* → contradice `phases` (que sí declara design);
  `phases` es el campo autoritativo, `design_role` es metadato derivado a recomputar.
- *Dejar la lógica solo en prosa del SKILL* → es lo que causó la divergencia; no es testeable.

**Consecuencias / aprendizaje.** `CU-1.e` se endurece: abrir un `AskUserQuestion` para decidir el rol
o el instalar-vs-quitar de una fase ya declarada es **FALLO**. El *qué repara* queda como invariante
automático (`RepairPlanTest`, 9 casos); lo único manual es que el agente **aplique** el plan sin
preguntar. Aprendizaje transversal (mismo patrón que D-009): cuando una conducta determinista se deja
en prosa, el agente improvisa y diverge — hay que **codificarla** y dejar a la prosa solo el *cómo
aplicarla*. Requiere `bash setup.sh` para propagar el SKILL nuevo a `~/.claude/skills/` (instala por
copia, no symlink); hasta entonces el agente carga la regla vieja.

**Referencias.** `scripts/sdd-init-detect.py` (`derive_design_role`, `repair-plan`) ·
`tests/test_sdd_init_detect.py` (`RepairPlanTest`) · `bootstrap/skills/wf-project-init/SKILL.md`
(reparación de fase declarada en extend) · `conformance/casos-de-uso/cu-01-inicializar.md` (`CU-1.e`).

---

## D-009 — La visibilidad del modo SDD es AMBIENTE (status line), no anuncios en el chat

- **Fecha:** 2026-06-17 · **Estado:** Adoptada

**Contexto.** Probando `CU-1.c` (modo libre), el agente anunciaba en el chat "el proyecto está en
modo libre" en **cada** sesión. El usuario quería **ver** que el proyecto está en SDD/libre (por si
algún día cambia), pero un anuncio por-sesión en el chat es ruido recurrente que contradice el valor
mismo del modo libre (cero huella de SDD) y, por repetición, se vuelve invisible — no cumple ni el
objetivo de discoverability. El spec ya pedía silencio en chat (`claude-global-block.md` modo libre:
"No vuelvas a mencionar SDD…"); el anuncio era el agente saliéndose del spec.

**Decisión.** Separar **avisar** (chat, puntual) de **recordar** (ambiente, permanente): el chat
permanece en silencio sobre SDD en modo libre, y la visibilidad del estado SDD se da en la **status
line** mediante un helper `bootstrap/sdd-statusline.sh` que imprime un **segmento corto** —
`⚙ SDD:<topology>` (inicializado), `⚙ SDD:libre` (modo libre, tenue), `⚙ SDD:init pendiente` — por
**find-up** (mismo criterio que el hook), o **nada** si SDD no aplica. Es **componible**: imprime solo
el segmento, sin separadores, para encajar en cualquier status line. `setup.sh` lo copia a
`~/.claude/hooks/` y registra una `statusLine` **solo si no hay una** (jamás pisa la del usuario; si
existe, imprime la guía para llamarlo). El helper es **fuente única** de la lógica (sin duplicar en
cada status line); `uninstall` borra el helper y desregistra la status line solo si es la nuestra.

**Alternativas descartadas.**
- *Anuncio por sesión en el chat* → ruido recurrente; se ignora por repetición; rompe el "cero huella".
- *Silencio total sin indicador* → pierde la discoverability que el usuario pedía.
- *Inlinear la lógica en cada status line* → drift entre copias; mejor un helper único.
- *Auto-inyectar el segmento en la status line existente del usuario desde setup.sh* → inviable/invasivo
  (puede ser cualquier comando); se documenta la integración manual en su lugar.

**Consecuencias / aprendizaje.** `CU-1.c` se matiza: silencio en chat = correcto; que la status line
muestre `⚙ SDD:libre` = esperado, no fallo. Para usuarios con status line propia la integración es
manual (en este repo, el `statusline.py` del autor —fuera del repo— llama al helper con `cwd`, envuelto
en try/except para no poder romper la línea). El helper **nunca falla** (siempre exit 0, imprime nada
ante error): una status line no puede permitirse tumbar por un segmento.

**Hueco detectado al implementar:** el silencio en chat estaba solo *implícito*. La rama de modo
libre del wizard sí lo decía ("No vuelvas a mencionar SDD"), pero las secciones **"Sin directiva"** y
el **fallback** del `claude-global-block.md` —que gobiernan las **sesiones recurrentes** (free ya
fijado)— no lo prohibían, así que el agente anunciaba el modo "por transparencia" (visto en `CU-1.c`).
Se endureció el bloque para **prohibir explícitamente anunciar el modo en el chat** (la status line es
el canal). Requiere `bash setup.sh` para propagar el bloque a `~/.claude/CLAUDE.md`; hasta entonces el
contexto del agente lleva el bloque viejo y la línea puede reaparecer.

**Referencias.** `bootstrap/sdd-statusline.sh` · `setup.sh` (paso 4b + limpieza en uninstall) ·
`conformance/casos-de-uso/cu-01-inicializar.md` (`CU-1.c`) · `bootstrap/claude-global-block.md`
(silencio en chat en modo libre).

---

## D-008 — Vista de cobertura "por componente" en cada CU (forward), con checklist de ejecución

- **Fecha:** 2026-06-17 · **Estado:** Adoptada

**Contexto.** La batería de conformance (`conformance/casos-de-uso/cu-*.md`) está organizada por
**objetivo de usuario** (journey), no por skill. El cruce skill→CU existía solo en dirección inversa
y en otro fichero (`conformance/ROADMAP.md`, una fila por `wf-*` con columna "CU que lo ejercitan"),
que además había quedado **stale** (la fila `wf-project-init` decía `--profile`/`--type`/`context: fork`
y le faltaban `CU-1.n/o/p` y `CU-3.r`). Al ejecutar los CU a mano no había forma, abriendo un CU, de
ver **qué componente valida cada escenario** ni de marcar el progreso. Además se descubrió que **CU-1
no prueba solo `wf-project-init`**: es híbrido (10 escenarios de la skill + 6 del hook de sesión).

**Decisión.** Cada `cu-NN.md` lleva una cabecera **`## 🧪 Qué se prueba aquí (por componente)`**
(tras el bloque intro, antes del primer escenario): la **transpuesta forward** (CU → componentes),
con los escenarios agrupados por su componente primario (`wf-*` skill / agente / script / hook /
orquestador, leído de la línea `Mecanismo:` de cada escenario) y un **checklist `- [ ]` por escenario**
para marcar al ejecutar. El **ROADMAP sigue siendo la SSoT backward** del estado de cobertura (ejes
happy/edge/harness/args + Estado); la cabecera del CU **apunta a él** y no duplica el veredicto por
ejes. Convención de marcado (estado de PASS = humano): `- [x] … · ✓ <fecha>` para PASS acordado;
`- [ ] … · ⚠️ FALLO → #issue` para divergencia. Se refrescó la fila stale de `wf-project-init` y se
añadió `CU-3.r` a las filas de spec.

**Alternativas descartadas.**
- *Solo dashboard central en ROADMAP* → descartada: no resuelve el forward al abrir un CU.
- *Reordenar físicamente los escenarios por skill* → descartada: los IDs `CU-N.x` son citables y
  estables; el orden "que tiene sentido" se da en la vista agrupada de la cabecera, no moviendo el cuerpo.
- *Generar la cabecera con script desde el principio* → diferida: las líneas `Mecanismo:` son prosa,
  parsearlas fiable exige estandarizar antes un mini-formato. Se hizo **a mano** el rollout (piloto en
  CU-1, luego los 16 restantes vía subagentes en paralelo).

**Consecuencias / aprendizaje.** Tres representaciones del mismo dato (líneas `Mecanismo:`, columna
del ROADMAP, cabecera del CU) = riesgo de drift — ya mordió con el ROADMAP stale. **Follow-up
pendiente:** extender `scripts/sdd-conformance-coverage.py` para (a) **generar** la cabecera desde las
`Mecanismo:` y (b) un modo **`--check`** que falle si las tres divergen; el generador debe
**preservar** las marcas de PASS (`[x]`/`✓ fecha`/`⚠️ FALLO`) — merge, no clobber, porque el estado
PASS es humano (ejecución manual), no derivable. Verificado en el rollout: los 17 CU tienen la
cabecera con el SET de IDs idéntico al del cuerpo (sin faltantes ni duplicados) y el agregador
determinista sigue parseando el ROADMAP (48/48, exit 0).

**Referencias.** `conformance/casos-de-uso/cu-01-inicializar.md` (piloto) + los 16 restantes ·
`conformance/ROADMAP.md` (fila `wf-project-init` refrescada; `CU-3.r` añadido) · `conformance/README.md`
(formato del CU) · `scripts/sdd-conformance-coverage.py` (follow-up de generación/`--check`).

---

## D-007 — Endurecimiento del bootstrap descubierto al ejecutar el init topología-first E2E

- **Fecha:** 2026-06-17 · **Estado:** Adoptada

**Contexto.** Al correr `/wf-project-init` varias veces sobre un repo greenfield real afloraron asperezas de bootstrap que el test del detector no captura. Primera tanda: (1) `wf-project-init` Paso 2 trataba `~/.sdd-home` como un directorio, cuando `setup.sh` lo escribe como **fichero-puntero** con la ruta dentro → `install.sh: MISSING` en el primer intento y recuperación a mano en **cada** ejecución; (2) `install.sh` copia el `CLAUDE.md` del ecosistema (191 líneas) siempre que hay ≥2 fases, y `wf-sdd-update` reejecuta `install.sh` → en cada update **pisaría** el `CLAUDE.md` lean del proyecto con el genérico (bug latente, solo visible al ejercitar el ciclo init→update); (3) el mensaje final "Reinicia Claude Code" era impreciso — los skills/agents del proyecto ya aparecían vía `/skills` y `/agents` sin reiniciar. Segunda tanda (run posterior): (4) **fricción de escritura recurrente** — `install.sh` sembraba `CLAUDE.md` y el Paso 7 lo sobreescribía con `Write` → choque con la regla del harness "leer antes de sobreescribir" (`Error writing file`); y el Paso 8 creaba `project-init.json` por Bash y luego lo corregía con `Update` (escribía `sdd_version: unknown` y lo parcheaba) → `File must be read first`. Ambos se recuperaban solos, pero ensuciaban cada init. (5) el `CLAUDE.md`/mensaje seguían pidiendo "reiniciar" cuando lo idiomático es `/clear`. (6) la opción Q1 "Producto (specs + diseño)" sobrevende: PRD y diseño son **opcionales** y se preguntan a continuación.

**Decisión.** (1) Paso 2 resuelve `~/.sdd-home` **leyendo su contenido** (es puntero, no directorio), igual que ya hacía `wf-sdd-update`. (2) `install.sh` siembra `CLAUDE.md` **solo si no existe**; contrato: **`install.sh` nunca pisa un `CLAUDE.md` ya presente** — así un `wf-sdd-update` no degrada el específico al genérico. (4) Para eliminar la fricción de escritura: `install.sh` acepta **`--no-claude-md`** y `wf-project-init` lo pasa siempre → en una instalación nueva el `CLAUDE.md` **no existe** y el `Write` del Paso 7 lo crea limpio (en reinit, el Paso 7 hace `Read` antes del `Write`); y el Paso 8 **resuelve `sdd_version` ANTES** y escribe `project-init.json` en **una sola** operación (sin placeholder + `Update`). (3+5) Mensaje final → "Ejecuta `/skills` y `/agents` para revisar que Claude ha cargado correctamente el ecosistema. Si quieres empezar con contexto limpio, ejecuta `/clear`." (6) Q1 → "Producto (specs + PRD/diseño opcionales)" con la opcionalidad explícita en la descripción.

**Consecuencias / aprendizaje.** El clobber de `CLAUDE.md` en update y la fricción de escritura eran invisibles para los tests automáticos: solo se ven **ejecutando el init/update a mano**. La causa raíz de (4) es estructural — el harness exige `Read` antes de sobreescribir/editar; la cura no es "leer y reintentar" sino **no crear el conflicto**: o el fichero no existe cuando el skill lo escribe (`--no-claude-md`), o se computa todo antes de un único write (sin `Update` correctivo). Confirma que las pruebas E2E manuales del init/update son la red que atrapa la regresión de bootstrap, complementaria al `test_sdd_init_detect.py`. (7) Aprendizaje adicional de la tercera pasada: el aviso final de `install.sh` **no llega al usuario** porque su stdout queda colapsado en el output del Paso 6. Se resuelve con un **Paso 11 dedicado** que emite el recordatorio (`/skills`+`/agents`+`/clear`) con un `echo` **determinista** — no prosa del modelo (coherente con [[D-004]]: garantiza texto exacto y presencia siempre, y un `echo` corto en su propia llamada no se colapsa). (8) Cuarta pasada (dos repos en paralelo): las instalaciones salieron **byte-idénticas** (project-init.json, CLAUDE.md, 3 rules, 6 agents, 48 skills, 12 scripts; modulo nombre+timestamp), pero en uno el agente invocó `verify --phases prd spec design` (espacios) → argparse abortó (`unrecognized arguments`) y reintentó. Causa: el placeholder `<SELECTED_PHASES>` del Paso 9 no decía "separadas por coma". Fix: el ejemplo del Paso 9 usa `--phases <fase1,fase2,...>` con nota explícita anti-espacios. Aprendizaje: los placeholders en los comandos del skill deben mostrar el **formato literal** (coma vs espacio), no un nombre abstracto, o el modelo elige formato y a veces falla.

**Referencias.** `bootstrap/skills/wf-project-init/SKILL.md` (Paso 2 · Paso 6 `--no-claude-md` · Paso 7 read-if-exists · Paso 8 `sdd_version` inline · Q1 5.0) · `install.sh` (flag `--no-claude-md`, siembra de `CLAUDE.md`, mensaje final) · `bootstrap/skills/wf-sdd-update/SKILL.md` (Paso 4).

---

## D-006 — El rigor del pipeline (standard/ligero) se elige por feature al crear el spec, no en el init

- **Fecha:** 2026-06-17 · **Estado:** Adoptada · **Refina:** [[D-001]] (el eje "rigor" deja de ser un *recorded-only* del init) · **Se apoya en:** [[D-002]] (la oferta interactiva vive en el hilo principal, no en el fork)

**Contexto.** El init preguntaba el "rigor del pipeline" (standard/ligero) y lo persistía como `pipeline_mode`. En pruebas E2E del init topología-first se vio que esa pregunta se hacía en **t=0, sin features delante** (un PM en authoring no puede decidirla informado), e incluso en topología `consumer` —que no instala la fase `spec`, así que su `pipeline_mode` es inerte—. Riesgo de fondo señalado por el usuario: un default `light` a nivel proyecto **normaliza specs finos por inercia**, convirtiendo un modo proporcional legítimo en un atajo a specs incompletas.

**Decisión.** El init **no pregunta** el rigor; `pipeline_mode` arranca en `standard`. La elección standard/ligero se ofrece **por feature al crear el spec**, donde la información existe. Como las workflows de creación (`wf-spec-fast-track`, `wf-spec-features-first`) son `context: fork` y no pueden usar `AskUserQuestion` ([[D-002]]), **el orquestador de la fase Spec ofrece la elección en el hilo principal antes de delegar**: respeta un flag explícito; respeta `pipeline_mode: light` si el equipo lo fijó a mano; si no, pregunta (default `standard`); en `features-first` pregunta **una sola vez por lote**. `pipeline_mode` se conserva como override de proyecto **editable a mano**.

**Alternativas descartadas.**
- *Mantener la pregunta en el init pero solo si hay `spec` (authoring/standalone)* → descartada: arregla el ruido en consumer pero no el problema de fondo (decisión a ciegas en t=0 y normalización de `light`).
- *Preguntar dentro de `wf-spec-fast-track`* → imposible: es `context: fork` ([[D-002]]); la interacción vive en el hilo principal.
- *Eliminar `pipeline_mode` del todo* → descartada: el escape "proyecto ligero-por-defecto" es legítimo; se conserva como campo editable, solo deja de normalizarse vía wizard.

**Consecuencias / aprendizaje.** El modo ligero queda como **opt-in deliberado**, no atajo: su blindaje contra specs incompletas es estructural (invariantes idénticos a standard, secciones omitidas marcadas `N/A — modo ligero` explícito, marcadores `[INCOMPLETO]`/`[CRÍTICO]` que bloquean igual). Cambia el **modelo de cobertura de CU-1** (el eje "rigor" sale del init) y exige que los CU de la fase Spec ejerciten la **oferta de modo al crear el spec**. La oferta vive en `pipeline/spec/CLAUDE.md`, que `install.sh` instala como `rules/sdd-spec.md` (carga perezosa) → llega a los proyectos sin tocar las workflows-fork.

**Referencias.** `bootstrap/skills/wf-project-init/SKILL.md` (Paso 5 / 5.8 / 7 / 8) · `pipeline/spec/CLAUDE.md` ("Elección del rigor del pipeline") · `pipeline/spec/skills/wf-spec-fast-track/SKILL.md` (Paso 1, resolución de modo) · `kb-spec-expert` ("Modo ligero") · `conformance/casos-de-uso/cu-01-inicializar.md` + `cu-03-specs.md`.

---

## D-005 — El eje primario del init es la TOPOLOGÍA de contenido del repo, no el perfil de quien inicializa

- **Fecha:** 2026-06-17 · **Estado:** Adoptada · **Supersede:** [[D-003]] (backbone-siempre) y el modelo de perfiles (`profiles`)

**Contexto.** El init preguntaba primero un **perfil** (`dev`/`product`/`design`/`minimal`) y, solo para dev, una topología (standalone/consumer). Al modelar un producto multi-superficie real (app móvil + desktop + web sobre los **mismos specs**) afloraron tres defectos: (1) `type` (app/web/backend) era una pregunta **técnica disfrazada de pregunta de proyecto** — para un PM que autora specs agnósticos es incorrecta (el spec no tiene superficie) y operativamente inerte; (2) el verdadero eje que determina qué se instala no es el rol sino **qué contiene el repo** (¿autora specs o los consume?, ¿lleva código?, ¿dónde vive el diseño?); (3) el diseño tiene dos capas —sistema (`DESIGN.md`, compartido entre superficies) y feature (`flows`/`views`/`ui_prompt`, divergentes por superficie)— que el modelo de fase única no separaba.

**Decisión.** La primera pregunta del init es la **topología de contenido**: `authoring` (PRD/specs/sistema de diseño, sin código), `consumer` (código de una superficie que consume specs de un SSoT) o `standalone` (todo junto). El backbone instalado **depende de la topología** (authoring sin plan/tasks; consumer sin spec/prd; standalone completo). `type` se sustituye por `surfaces` (mobile/desktop/web/backend/other), que solo se pregunta en ramas con código y alimenta a la vez el stack y el `target_platforms` del diseño. El consumer se parte en *con-UI* (instala diseño de feature) y *headless*. La fase `design` se reparte en dos agentes (`design-system-architect` / `design-feature-architect`) según `design_role`. El esquema de `project-init.json` rompe compatibilidad: `topology`/`surfaces`/`has_ui`/`design_role` sustituyen a `profiles`/`type` (sin migración; reinit).

**Alternativas descartadas.**
- *Parchear solo `type`→agnóstico para product/minimal, manteniendo perfiles* → descartada: trata el síntoma, no la causa; el eje seguiría siendo el rol, que es una aproximación torpe a la topología.
- *Repo solo-diseño como cuarta topología* → descartada: el caso multi-superficie no lo necesita (el `DESIGN.md` compartido se pliega en authoring y los flows/views por superficie viven en cada repo consumer). Queda como opción organizativa, no estructural.
- *Partir `design` en dos juegos de skills instalables aislados* → descartada: feature-prototype necesita el contrato del sistema en contexto. El split correcto es de **agente** (dos agentes, el de feature carga el contrato como referencia de solo-lectura), no de skills mutuamente excluyentes.

**Consecuencias / aprendizaje.** El "backbone-siempre" de [[D-003]] queda como caso particular (standalone); la regla general es "backbone según topología", espejo simétrico de la excepción consumer que D-003 ya contemplaba. "Mínimo" deja de ser un perfil: es la configuración de standalone con PRD=no/diseño=no/stack agnóstico. **Deuda anotada:** standalone multi-superficie con stacks distintos (app+backend) instala hoy un solo overlay de stack — se elige superficie primaria y el resto se completa con "Completar / ampliar".

**Referencias.** `bootstrap/skills/wf-project-init/SKILL.md` (Regla 4, Paso 5 árbol de llamadas, Paso 6/8) · `sdd/scripts/sdd-init-detect.py` (check `topology`) · `sdd/tests/test_sdd_init_detect.py` · `pipeline/design/agents/design-system-architect.md` + `design-feature-architect.md` · `pipeline/design/skills/kb-design-feature-artifacts` (ui_prompt por superficie) · `conformance/casos-de-uso/cu-01-inicializar.md`.

---

## D-004 — La lógica determinista del init vive en un script, no en bash inline

- **Fecha:** 2026-06-16 · **Estado:** Adoptada · **Versión:** 0.33.0

**Contexto.** `wf-project-init` recitaba en bash inline su lógica determinista (find-up del raíz en monorepos, detección de estado previo, carpetas candidatas, detección de stack, verificación post-install). El modelo la retecleaba cada init: no testeable y propensa a variación. Va contra el principio del ecosistema ("recolección determinista, no agente") y contra la migración prosa→script ya hecha (inventario 11.2).

**Decisión.** Extraer esa lógica a `sdd/scripts/sdd-init-detect.py` (subcomandos `detect` pre-install y `verify --phases` post-install). Es herramienta de **ecosistema**, no de proyecto: NO se distribuye a `.sdd/scripts/`; se invoca vía `$SDD_HOME/scripts/…` — disponible pre-install igual que `$SDD_HOME/install.sh` (mismo modelo que `sdd-structural-lint.py`/`sdd-scaffold.py`). La **entrevista** (`AskUserQuestion`) se queda en el skill: es interactiva, no scriptable. El bash inline se conserva como **fallback explícito** sin python3 (mismo patrón que el cableado de `sdd-resolve-path.py`).

**Alternativas descartadas.**
- *Bundlear el script en `${CLAUDE_SKILL_DIR}/scripts/`* → descartada: estrenaría un patrón sin precedente (ningún skill bundlea scripts hoy) cuando `$SDD_HOME/scripts/` ya es el hogar canónico y está disponible pre-install.
- *Scriptar también la escritura de `project-init.json` (Paso 8)* → fuera de alcance por ahora; el esquema es simple y `verify` lo comprueba.

**Consecuencias / aprendizaje.**
- **Aprendizaje:** lo interactivo no se puede testear headless (`AskUserQuestion` no existe sin hilo principal). Por eso la frontera correcta es *script determinista (testeable) + capa de entrevista delgada (manual)*. Cuanto más se mete en el script, más cae bajo test; el `CU-1.p` (args) queda como prueba manual mínima.
- `verify` arregla de paso un falso negativo latente: el check viejo `grep -q '"artifacts"'` fallaba en topología consumer (que usa `artifacts_source`), reportando FALLO en un init correcto. Ahora acepta ambos.
- Cubierto por `test_sdd_init_detect.py` (17 tests).

**Referencias.** `sdd/scripts/sdd-init-detect.py` · `sdd/tests/test_sdd_init_detect.py` · `bootstrap/skills/wf-project-init/SKILL.md` (Pasos 3/4/9) · `CHANGELOG.md` 0.33.0 · [[D-002]] (mismo principio: lo interactivo en el hilo principal).

---

## D-003 — El backbone `spec`/`plan`/`tasks` siempre se instala (standalone): SDD es un flujo agnóstico a la tecnología

- **Fecha:** 2026-06-16 · **Estado:** Superada por [[D-005]] (el backbone pasa a depender de la topología; el principio agnóstico se conserva en standalone)

**Contexto.** Al analizar `wf-project-init` surgió si el "backbone fijo" (spec/plan/tasks siempre) era correcto en todos los casos. La Regla 4 decía "SIEMPRE" pero la topología consumer instala solo `plan`+`tasks`.

**Decisión.** El backbone-siempre es **deliberado** en topología *standalone* (lo normal, incluida la inicialización de proyectos sin stack especializado, p. ej. C++): SDD se usa como **flujo de trabajo agnóstico a la tecnología** — aun sin skills de stack, se define spec → se genera plan → se generan tasks; nunca se implementa "a pelo". La **única excepción** es la topología *consumer* (repo técnico de un producto multi-repo cuyos specs viven en un repo SSoT): instala solo `plan`+`tasks`, porque la autoría de specs no ocurre ahí. La Regla 4 se reescribe para reflejar esa única excepción; no se cuestiona el backbone en standalone.

**Consecuencias / aprendizaje.** El perfil `custom` prometía "decidir fase a fase qué se instala", pero el backbone no es negociable → etiqueta templada (custom decide `prd`/`design`, no el backbone). El valor de SDD como contrato de proceso (no como tooling de un stack) queda explícito: instalar plan/tasks aunque no haya owner-agent de stack es la feature, no un desperdicio.

**Referencias.** `bootstrap/skills/wf-project-init/SKILL.md` (Regla 4, Paso 5.0b consumer, Paso 5.0 custom) · `conformance/casos-de-uso/cu-01-inicializar.md` (CU-1.i consumer).

---

## D-002 — `context: fork` es incompatible con `AskUserQuestion`

- **Fecha:** 2026-06-16 · **Estado:** Adoptada · **Versión:** 0.33.0

**Contexto.** Durante las pruebas manuales de CU-1, la entrevista de `wf-project-init` salía con orden y descripciones distintos entre ejecuciones, pese a que el SKILL.md exige opciones y secuencia exactas. La causa: el skill llevaba `context: fork` y la entrevista usaba `AskUserQuestion`. La documentación oficial de Claude Code es explícita: `AskUserQuestion` (y otras tools dependientes de la UI del hilo principal) **no está disponible en subagentes ni forks**, falla aunque esté en `allowed-tools`. El fork no podía preguntar, así que el orquestador del hilo principal improvisaba la interacción de memoria. Afectaba a **8 workflows** que compartían el patrón.

**Decisión.** Una `wf-*` que use `AskUserQuestion` **no puede llevar `context: fork`**: corre en el hilo principal. La delegación de trabajo pesado a un agente es **ortogonal al fork** — se hace vía la tool `Agent`, que aísla el contexto igual de bien. El campo `agent:` (destino de inyección del fork) desaparece junto con el fork; el cuerpo nombra al agente y lo invoca por `Agent`.

**Alternativas descartadas.**
- *"El harness debería dejar preguntar al fork"* → descartada: es comportamiento documentado e intencional de la plataforma, no un bug del harness.
- *Round-trip (mantener el fork; que devuelva "necesito decisión" y el hilo principal pregunte y reinvoque)* → descartada: más compleja y frágil, sin ganancia de contexto (el `Agent` ya aísla el trabajo pesado).

**Consecuencias / aprendizaje.**
- 7 skills eran patrón orquestador (delegación limpia) → quitar el fork fue trivial. `wf-prd-review` era "fork-como-agente" (su cuerpo corría *como* `prd-expert` para tener `kb-prd-expert` en contexto) → hubo que reestructurarlo a delegación explícita.
- El bug se **autogeneraba**: el scaffold (`sdd-scaffold.py`) hardcodeaba `context: fork` en todo `wf-*`, y la guía (`kb-sdd-creation-guide`) lo declaraba obligatorio. Arreglar solo los 8 skills no habría bastado: hay que arreglar también las fuentes que reproducen el patrón.
- **Aprendizaje transversal:** la interacción con el usuario vive SIEMPRE en el hilo principal; los subagentes/forks son para trabajo no interactivo. Cualquier patrón nuevo que mezcle ambos es sospechoso.
- Guardarraíl permanente: regla blocking `FORK-ASKUSER-CONFLICT` en el linter — la clase de bug ya no puede regresar en verde.

**Referencias.** `CHANGELOG.md` 0.33.0 · linter `FORK-ASKUSER-CONFLICT` · `kb-sdd-creation-guide` (frontmatter `wf-*`) · incidencia GitHub `[CU-1.b]`.

---

## D-001 — Cobertura de CU-1 por ramas de decisión, no por producto cartesiano

- **Fecha:** 2026-06-16 · **Estado:** Adoptada

**Contexto.** Al probar el wizard de init manualmente, la combinatoria de ejes (perfil × PRD × tipo × rigor …) parecía inabarcable y sin cubrir en los casos de uso. Pero no todos los ejes cambian lo que se instala: en perfil producto, `tipo` y `rigor` no alteran el set de fases — solo se persisten en `project-init.json`.

**Decisión.** CU-1 prueba **ramas de decisión**, no combinaciones de valores. Un eje merece un caso por rama solo si cambia el set instalado o el flujo de preguntas (*behavior-changing*); los ejes que solo se registran (*recorded-only*) se cubren con un único caso parametrizado. `cu-01-inicializar.md` lleva una tabla "Modelo de cobertura" que clasifica cada eje y marca su cobertura honesta (`✓` / `parcial` / `—`).

**Consecuencias / aprendizaje.** Disuelve la explosión combinatoria (`producto/prd/app/standard` y `producto/prd/web/ligero` instalan lo mismo → no son casos distintos). La tabla hace **visibles los gaps reales** en lugar de esconderlos en una falsa sensación de cobertura total. Casos nuevos: `CU-1.n` (ejes recorded-only) y `CU-1.o` (ramas behavior-changing de tipo/framework/custom).

**Referencias.** `conformance/casos-de-uso/cu-01-inicializar.md` (Modelo de cobertura, CU-1.n, CU-1.o).
