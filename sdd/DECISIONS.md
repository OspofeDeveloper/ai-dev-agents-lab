# Registro de decisiones del ecosistema SDD

Constancia de las **decisiones de diseño** y los **aprendizajes** del ecosistema: por qué se hizo algo de una manera y no de otra, qué aprendimos al equivocarnos. Complementa al `CHANGELOG.md` (qué cambió, por versión) respondiendo al **por qué**.

Formato: una entrada `## D-NNN — <título>` por decisión, **más reciente arriba** (como el CHANGELOG). Cada entrada lleva: fecha, estado, contexto, decisión, alternativas descartadas, consecuencias/aprendizaje y referencias. Las entradas son append-only: si una decisión se revierte, no se borra — se añade una nueva que la supersede y se marca la vieja `Superada por D-MMM`.

---

## D-096 — Un auditor del fan-out responde de los pares de su spec, y de nada más

- **Fecha:** 2026-09-24 · **Estado:** Adoptada (en modo feature el auditor compara solo los pares que incluyen su spec y lo dice en el veredicto; el readiness solo desmiente una portada sobre un par que esa portada cubría. **Salió de la pasada 2/3 de `CU-3.d`**, sobre v0.117.1). · **Relacionada:** [[D-093]] (la cobertura por pares completa, que este hace verdad por contrato), [[D-095]] (la portada desmentida, que este acota), [[D-047]].

**Contexto.** El Paso 5 de la verificación de conflictos decía *"busca conflictos entre cada par de specs"* y *"entre todos los pares"*, sin distinguir los dos modos. En el consolidado es lo correcto; en el **modo feature** —el del fan-out, un auditor por spec nuevo— no. La pasada lo midió con tres auditores sobre el mismo conjunto de 5:

- **F-002** se ciñó a su spec: *"F-002 vs F-001, F-003, F-004, F-007"*. Es lo que supone [[D-093]] cuando dice que la cobertura por pares está completa: cada spec nuevo contra todos.
- **F-001 y F-007** declararon limpios **los 10 pares**, incluido F-003↔F-004 — donde el auditor de F-004 había levantado un choque ALTA (`CF-F004-01`) que el arbitraje confirmó. Revisar un par ajeno con menos atención que su dueño no suma cobertura: suma un **falso negativo con firma**.
- **Y el readiness aplicó [[D-095]] de más**: marcó bien como desmentidas las portadas de F-001 y F-007, pero también la de **F-002**, que nunca habló de ese par.

El veredicto acotado de [[D-093]] empujaba en la dirección equivocada: *"entre los 5 specs comparados"* se lee como *"revisé los 10 pares"*.

**Decisión.**

- **En modo feature, el auditor revisa solo los pares que incluyen su spec objetivo** y no se pronuncia sobre los demás, ni para darlos por limpios. El modo consolidado sigue revisando todos.
- **El veredicto dice ese alcance**: `SIN_CONFLICTOS (F-002 contra los otros 4 specs: F-001, F-003, F-004, F-007)`. El token sigue delante y literal.
- **El readiness solo marca una portada como desmentida si el par confirmado estaba en su alcance.** Si un informe se pronunció sobre un par ajeno, sí queda desmentido, y se dice por qué.
- **Comprobación explícita** en `CU-3.f` puntos 2 y 4. La serie de `CU-3.d` no se reinicia: toca alcance y prosa de los informes, que ese escenario no mide.

**Alternativas descartadas.**
- *Que cada auditor del fan-out revise los 10 pares* → N auditorías de todos los pares para una cobertura que ya se tiene con N revisiones de su spec contra el resto, y con la redundancia hecha por quien menos mira cada par. Lo medido es justo eso: dos auditores que dieron por limpio un par que su dueño encontró sucio.
- *Dejar el contrato y que el readiness descuente los pares ajenos al leer* → el readiness no puede saber qué miró de verdad un auditor que dice *"todos los pares"*; lo que no está escrito en el alcance no se puede arbitrar.

**Consecuencias / aprendizaje.** **Un veredicto con alcance solo ayuda si el alcance es el verdadero.** [[D-093]] hizo que cada portada dijera sobre qué conjunto vale, y el formato elegido —*"entre los N"*— describía el modo consolidado, no el que corre en el fan-out. Y un arreglo nuevo aplicado a un caso vecino: [[D-095]] funcionó en su caso y se pasó en el de al lado; se vio porque la pasada siguiente lo ejercitó con un par ajeno.

**Referencias.** `pipeline/spec/skills/wf-spec-conflict/SKILL.md` (Pasos 5 y 7) + `references/conflict_report_template.md` · `pipeline/spec/skills/wf-spec-readiness/SKILL.md` (reglas de arbitraje) · `conformance/casos-de-uso/cu-03-specs.md` (CU-3.d pasada 2/3, CU-3.f puntos 2 y 4) · `CHANGELOG.md` 0.117.2.

---

## D-095 — El arbitraje también desmiente portadas, y el índice dice dónde escribe

- **Fecha:** 2026-09-23 · **Estado:** Adoptada (el readiness señala la portada de conflictos que su arbitraje desmiente; el informe de conflictos del fan-out dice desde qué spec mira; el script del índice anuncia la ruta. **Salió de la pasada 1/3 de la serie nueva de `CU-3.d`**, sobre v0.117.0). · **Relacionada:** [[D-047]] (los auditores se contradicen por diseño y el readiness arbitra), [[D-093]] (la portada tiene que llevar lo que la matiza), [[D-089]].

**Contexto.** Dos hallazgos de una pasada en verde, ninguno de los cuatro puntos de `CU-3.d`:

- **Una portada que el arbitraje desmiente y nadie lo dice.** El auditor de F-001 levantó `CF-F001-01` (ALTA) contra F-007; el de F-007, mirando el mismo par desde su lado, no lo vio y abrió con `SIN_CONFLICTOS (entre los 5 specs comparados: …)`. El readiness arbitró, confirmó el conflicto y bloqueó F-007 — y el informe de F-007 siguió diciendo *"sin conflictos"* sobre una feature bloqueada. Es exactamente lo que [[D-093]] enseñó con la vigencia: **quien abre el informe de una feature empieza por su portada**. [[D-093]] cubrió el caso en que la portada envejece por el tiempo; este es el caso en que la desmiente **otro informe**.
- **El índice anunciaba el nombre, no la ruta.** `regenerado spec_features.md`: main lo buscó en la raíz del proyecto, no estaba, y gastó dos llamadas en averiguar que vive en `spec/`.

**Decisión.**

- **El readiness señala la portada desmentida, sin editarla**: en su cabecera de vigencia, `VIGENTE — portada desmentida por el arbitraje (CF-F001-01)`, y un punto en «Próximos pasos» que dice que el estado de esa feature es el del readiness y que el documento queda al día **al rehacerlo una vez resuelto el conflicto**.
- **El informe de conflictos del fan-out dice desde qué spec mira** (*"Visto desde F-007"*) y remite al readiness si otro auditor levanta un choque que lo incluya. No es un descargo genérico: es el alcance del veredicto, la otra mitad de [[D-093]].
- **El script del índice imprime la ruta relativa al cwd.** Test propio.
- **La serie de `CU-3.d` no se reinicia.** El contenido del índice es byte-idéntico —solo cambia la línea que lo anuncia— y lo demás es prosa de informes que el escenario no mide. Donde sí se mide queda escrito: `CU-3.f` punto 2 (IDs, `Conjunto comparado`, veredicto acotado y *visto desde*) y punto 4 (portada desmentida), y un punto 6 nuevo de `CU-3.o` (vigencia y acción de los ESTANCADOS), que hasta hoy no tenían comprobación explícita de [[D-090]]/[[D-093]] en ningún escenario.

**Alternativas descartadas.**
- *Que el readiness reescriba o anote el informe del auditor que no lo vio* → el informe es de su auditor y describe lo que **él** vio; editarlo desde otro rol borra justo el desacuerdo del que [[D-047]] pide dejar constancia. Lo que se corrige es dónde lo encuentra el lector, no el documento.
- *Rehacer el informe desmentido en el momento* → repite el desacuerdo: el conflicto sigue abierto y el auditor de F-007 lo mira desde el mismo lado. Rehacerlo tiene sentido **después** de resolverlo.
- *Dejar el mensaje del índice para cuando la serie se selle* → cambia una línea de stdout y ningún dato del fichero; esperar dos pasadas cuesta dos búsquedas por pasada.

**Consecuencias / aprendizaje.** **Una portada puede quedar desmentida por el tiempo o por otro informe, y las dos veces hay que decirlo donde se lee.** [[D-093]] miró solo el eje del tiempo; el arbitraje es el otro eje, y estaba escrito en el mismo contrato —*"deja constancia del desacuerdo"*— sin decir **dónde**. Y un aprendizaje de instrumento: lo que [[D-090]] y [[D-093]] prometían **no lo comprobaba ningún escenario**; se vio porque `CU-3.d` mira el fan-out entero. Una decisión sin su comprobación en el CU que le toca vive de que otra pasada tropiece con ella.

**Referencias.** `pipeline/spec/skills/wf-spec-readiness/SKILL.md` (Paso 4c, reglas de arbitraje) + `references/readiness_report_template.md` · `pipeline/spec/skills/wf-spec-conflict/SKILL.md` (Regla de oro) + `references/conflict_report_template.md` · `scripts/sdd-features-index.py` + `tests/test_sdd_features_index.py` (`RutaDeSalidaTest`) · `conformance/casos-de-uso/cu-03-specs.md` (CU-3.d pasada 1/3, CU-3.f puntos 2 y 4, CU-3.o punto 6) · `CHANGELOG.md` 0.117.1.

---

## D-094 — Salto a Opus 5.5, y la serie que había que perder a propósito

- **Fecha:** 2026-09-23 · **Estado:** Adoptada (los 11 agentes Opus pasan a `claude-opus-5-5` y los 5 `claude-sonnet-4-6` del overlay KMM a `claude-sonnet-5`; `CU-3.d` vuelve a **0/3**). · **Relacionada:** la frontera de modelo de 2026-08-27 (4-x → 5, notas de procedencia de CU-1/CU-2), `kb-sdd-conformance` Regla 9 puntos 3 y 9.

**Contexto.** Sale Opus 5.5 y el orquestador de las sesiones ya corre en él. En el ecosistema convivían **tres generaciones**: 6 agentes del núcleo en `claude-opus-5`, 5 del overlay KMM en `claude-opus-4-8` y otros 5 del overlay en `claude-sonnet-4-6`. Y la guía no se ponía de acuerdo consigo misma: `kb-sdd-creation-guide` decía `claude-opus-5`, su checklist y la plantilla de frontmatter seguían en `claude-opus-4-8`/`claude-sonnet-4-6`, y **`sdd-scaffold.py` creaba cada agente nuevo con `claude-opus-4-8`** por defecto — el bump anterior barrió los agentes y se dejó la fábrica.

**Decisión.**

- **Todo Opus a `claude-opus-5-5`**, núcleo y overlay. Los Sonnet del overlay a `claude-sonnet-5`, que es la familia del núcleo: los 12 Sonnet quedan en `claude-sonnet-5` (no hay Sonnet 5.5).
- **La fábrica va en el mismo barrido**: default de `sdd-scaffold.py` (+ su test), checklist, plantilla de frontmatter, tabla de criterios y el `README`. Comprobación: `grep -rn "^model:" pipeline/*/agents/ meta/agents/ tech/*/agents/` da **dos** valores y nada más.
- **El overlay KMM se sube en la misma decisión**, no de arrastre: la guía pide que un overlay con conformance propia se decida aparte, y esta entrada es esa decisión. Su deuda de procedencia la hereda CU-12.
- **`CU-3.d` vuelve a 0/3.** Los agentes que ejecuta (`sdd-spec-explorer`, `sdd-spec-writer`, `sdd-spec-auditor`) son `sonnet-5` y no cambian — pero el **punto 3** (el fan-out sale en un único mensaje) lo emite el **hilo principal**, y ese pasa de `opus-5` a `opus-5-5`. Es juicio del orquestador al otro lado de una frontera: la 1/3 pasa a histórica.

**Alternativas descartadas.**
- *Terminar la serie de CU-3.d con el orquestador en `opus-5` y migrar después* → cuesta dos pasadas para sellar un escenario sobre un modelo que se retira al día siguiente. Con la serie en 1/3 se pierde una pasada; sellada, se habría perdido un sello.
- *Subir solo el núcleo y dejar el overlay para su propia campaña* → dejaría tres generaciones vivas y la fábrica emitiendo la más vieja. Lo caro de un overlay con conformance es re-validarlo, no subirlo; lo que se decide aparte es la **deuda**, y queda escrita.

**Consecuencias / aprendizaje.** **Un bump de modelo tiene dos superficies: los agentes que existen y los que se van a crear.** El de 2026-08-27 barrió la primera y dejó la segunda en 4-8 durante un mes, sin que nada lo notara porque un agente recién creado con un modelo viejo **funciona**. Y la frontera no es solo el `model:` del frontmatter: el modelo del **hilo principal** también mide, y cualquier escenario cuyo punto lo emita el orquestador —fan-out, gates con `AskUserQuestion`, arbitrajes— cruza la frontera aunque ningún agente cambie. Los sellos conductuales previos (CU-3.a, CU-2, CU-1, CU-13.a) pasan a deuda de procedencia `SELLADO (5) — pendiente HUMO (5.5)`.

**Referencias.** `pipeline/*/agents/*.md`, `meta/agents/*.md`, `tech/kmm/agents/*.md` · `scripts/sdd-scaffold.py` + `tests/test_sdd_scaffold.py` · `meta/skills/kb-sdd-creation-guide/SKILL.md` + `references/checklists.md` + `references/frontmatter-templates.md` · `README.md` · `conformance/casos-de-uso/cu-03-specs.md` · `CHANGELOG.md` 0.117.0.

---

## D-093 — La vigencia estaba en la cabecera y el veredicto seguía sin llevarla

- **Fecha:** 2026-09-23 · **Estado:** Adoptada (el veredicto del informe de conflictos se enuncia sobre su conjunto; un informe ESTANCADO produce acción en el readiness. **Salió de la pasada 1/3 de `CU-3.d` sobre v0.116.0**, la que validaba [[D-090]]). · **Relacionada:** [[D-090]] (el campo `Conjunto comparado`, que este cierra), [[D-083]] (*"bien formado y equivocado"*), [[D-089]] (el mismo defecto en el índice).

**Contexto.** [[D-090]] hizo declarar a cada informe de conflictos contra qué conjunto se calculó, y la medición de readiness lo usa para marcar **ESTANCADO** lo que ya no cubre los specs actuales. Funcionó a la primera. Pero la pasada que lo validaba enseñó la mitad que faltaba, en dos sitios:

- **El veredicto de portada no llevaba el alcance.** `gestion-categorias_conflict_report.md` abría con **`SIN_CONFLICTOS`** a secas —*"no se detectaron … entre los dos specs comparados"*, con el matiz enterrado en la frase— mientras esa misma feature aparecía en `CF-F004-02` (MEDIA) del informe de `cuentas-y-tarjetas`, generado una tanda después. La cabecera decía la verdad y la portada no. Y quien abre el informe de una feature **empieza por su portada**, no por el readiness que lo clasifica.
- **El ESTANCADO se quedaba en diagnóstico.** El readiness listó los dos informes viejos con lo que no vieron… y sus siete «Próximos pasos» no decían nada de ellos. Diagnóstico sin cierre: el lector no sabe si le falta análisis o solo le sobra un documento viejo.

**Decisión.**

- **El veredicto se enuncia sobre su conjunto**: `SIN_CONFLICTOS (entre los 2 specs comparados: F-002, F-003)`. El token va **primero y literal** —lo parsea el readiness, que exige encontrarlo— y el conjunto detrás, entre paréntesis. La regla de oro de la skill lo dice ahora entero: un veredicto sin su alcance **deja de ser inequívoco** en cuanto aparece un spec más.
- **Un ESTANCADO produce acción en «Próximos pasos»**, y antes de proponer nada el readiness mira **quién cubre los pares que ese informe no vio**.
- **Y aquí está el dato que evita el arreglo caro:** el fan-out compara cada spec **nuevo contra todos**, así que el par (viejo, nuevo) lo miró el auditor del nuevo y el par (viejo, viejo) sigue cubierto por el informe viejo. **La cobertura por pares está completa**; lo viejo es el **documento**, no el análisis. La acción normal es *"puede rehacerse cuando convenga"*, no relanzar N auditores. Solo si al cruzarlo aparece un par que **no ha mirado nadie**, eso es análisis que falta y sube a acción prioritaria.

**Alternativas descartadas.**
- *Rehacer automáticamente los informes estancados al cerrar cada tanda* → paga N auditorías para reescribir documentos cuyo contenido ya está cubierto. Es la alternativa que [[D-090]] descartó por cara, y saberlo **por qué** es justo lo que faltaba escribir.
- *Dejar solo la cabecera y confiar en que el lector la mire* → es lo que se probó: la cabecera estaba puesta y el falso negativo salió igual. Un dato que contradice al titular tiene que estar **en el titular**.

**Consecuencias / aprendizaje.** **Un matiz que vive lejos del veredicto no matiza nada.** [[D-090]] puso la vigencia donde la lee un parser y dio por hecho que con eso bastaba para la persona; el probe de campo enseñó que el lector humano entra por otra puerta. El corolario, que ya va por la segunda vez en esta tanda: cuando un artefacto pasa a ser **relativo a un estado**, hay que recorrer **todos** sus puntos de entrada —portada, cabecera, tabla resumen, informe que lo consume— y no solo el que uno tenía en la cabeza al arreglarlo.

**Referencias.** `pipeline/spec/skills/wf-spec-conflict/SKILL.md` (Regla de oro, Paso 7) + `references/conflict_report_template.md` · `pipeline/spec/skills/wf-spec-readiness/SKILL.md` (Paso 4c) + `references/readiness_report_template.md` · `conformance/casos-de-uso/cu-03-specs.md` (pasada 1/3 de CU-3.d) · `CHANGELOG.md` 0.116.0.

---

## D-092 — El contrato del fan-out no se puede medir a ojo, y con N=2 tampoco se ve

- **Fecha:** 2026-09-21 · **Estado:** Adoptada (probe determinista `sdd-fanout-check.py` con 10 tests; invariante del cardinal reforzado para N=2 en los Pasos 5 y 7 de `wf-spec-features-first`; **V4** nuevo en el banco. **Salió de la pasada de CU-3.d del 2026-09-18**). · **Relacionada:** [[D-084]] (la llamada de prueba), [[D-047]] (el fan-out es una barrera), [[D-050]] (el flag que hace que serializar duela).

**Contexto.** [[D-084]] cerró la forma `1 + (N-1)` reforzando el contrato en los tres emisores y añadiendo el backstop `FANOUT-PILOT-UNGUARDED`. Ese backstop es un lint **sobre el texto de la skill**: comprueba que el contrato esté escrito. No mide la conducta, y no puede — contar llamadas por mensaje en caliente es justo lo que [[D-048]] puso y [[D-050]] retiró por degradar el comportamiento.

Con el contrato reforzado y el backstop puesto, la pasada de CU-3.d del 2026-09-18 volvió a fallar: la primera tanda, de **dos** features, salió `1 + 1` con **253 s** de hueco — y la **misma sesión**, veinte minutos después, emitió las tres de la tanda siguiente en un único mensaje. El orquestador incluso lo dijo al corregirse: *"Emití solo una llamada cuando las dos debían salir en el mismo mensaje"*.

Dos cosas nuevas, y las dos importan:

- **Con N=2 el desvío es invisible.** *"Lanzo las dos en paralelo"* seguido de una llamada se lee igual que el caso bueno: no hay un grupo del que falte un miembro. Con seis, el mensaje con una sola llamada canta; con dos, no hay forma.
- **Las tres veces lo encontró una persona leyendo el `.jsonl`.** Un banco que depende de que alguien mire el transcript a mano no mide ese contrato: lo muestrea.

**Decisión.**

- **Probe `sdd-fanout-check.py`** (ecosistema, no se instala en el consumer): agrupa los `tool_use` de la tool `Agent` por `message.id`, los clasifica por cubo `(subagent_type, skill que el prompt manda leer)` y corta por turno humano. Dos emisiones del mismo cubo sin turno humano en medio = `FANOUT_SERIALIZADO`, con la forma (`1 + 3`) y el hueco en segundos. Exit 2, como los demás gates.
- **El cubo lleva la skill a propósito.** Sin ella, `wf-spec-analyze` → `wf-spec-discover` (dos encargos secuenciales **por contrato** al mismo `sdd-spec-explorer`) sería un falso positivo. El corte por turno humano hace lo propio con los relanzados legítimos: un `STOP_*` presentado en un gate, una tanda cortada por el límite de sesión.
- **Fusionar las filas por `message.id` es la mitad del probe.** El transcript parte un mensaje en una fila por bloque de contenido: las 3 llamadas de un fan-out bueno llegan como 3 filas. La primera versión las contaba como 3 emisiones de tamaño 1 — habría reportado rojo sobre el caso correcto.
- **Validado contra el histórico antes de darlo por bueno**: pasada 15 → `OK` (7+7), pasada 18 → `OK` (3+3), pasada 14 → `1 + 3` con 359 s, que es el hallazgo que [[D-084]] describe. Y de rebote encontró **una cuarta ocurrencia** que nadie había registrado.
- **El contrato dice ahora el caso pequeño**: *"y si son 2, ese mensaje lleva 2 — el invariante es el cardinal, no el tamaño de la tanda"*, con la instrucción operativa de **decir el número antes de emitir y contar las llamadas contra él**.

**Alternativas descartadas.**
- *Un `PreToolUse` que cuente llamadas* → descartada por [[D-050]]: ya se probó, degradó la conducta, y además el hook no sabe cuántas **debería** haber — ese número vive en una decisión tomada dos pasos antes.
- *Reescribir otra vez el párrafo del contrato* → insuficiente por sí solo: es la tercera vez. Si el texto bastara, no habría hecho falta una segunda.
- *Instalar el probe en `.sdd/scripts/` del consumer* → descartada: no es un gate del proyecto y lo que lee es el transcript del harness. Un script de conformance en `.sdd/scripts/` es contexto falso para cualquier agente que liste ese directorio (el mismo daño que los scripts zombis de ROADMAP 11.8).

**Consecuencias / aprendizaje.** **Un contrato que solo verifica su propio enunciado no está verificado.** El lint de texto y el probe de conducta no son redundantes: uno mira lo que la skill dice, el otro lo que la sesión hizo, y el fallo de [[D-084]] vive exactamente en el hueco entre los dos. Y el corolario del tamaño: **el caso pequeño no es el caso fácil, es el caso ciego** — un invariante se rompe primero donde su incumplimiento no tiene forma visible.

**Referencias.** `scripts/sdd-fanout-check.py` · `tests/test_sdd_fanout_check.py` (10 tests) · `pipeline/spec/skills/wf-spec-features-first/SKILL.md` (Pasos 5 y 7) · `conformance/casos-de-uso/cu-03-specs.md` (**V4**, CU-3.d punto 3) · `CHANGELOG.md` 0.116.0.

---

## D-091 — La tercera casa de la misma norma: citar la kb que sostiene tu veredicto

- **Fecha:** 2026-09-21 · **Estado:** Adoptada (norma de prosa extendida a la familia conflict y al informe de readiness, y generalizada en la guía de fase; **medida en la pasada de CU-3.d del 2026-09-18**). · **Relacionada:** [[D-088]] (la misma clase, en la fase PRD; su *"¿dónde más vive?"* apuntaba aquí), [[D-042]] (el artefacto se lee **verbatim** a quien decide), v0.115.2 (la norma en el informe de readiness, acotada a los workflows).

**Contexto.** [[D-088]] amplió el probe **V1** a `kb-*` y cerró la fuente en `wf-spec-analyze`, dejando anotado el pendiente: *"¿qué clase es esta, y dónde más vive?"*. La pasada de CU-3.d del 2026-09-18 lo contestó — V1 devolvió **3 líneas**, las tres de la misma forma y ninguna en la fase PRD:

- `spec_readiness_report.md`: *"Por qué es conflicto (Regla 4 de `kb-conflict-expert`…)"* y *"la tabla de severidad de `kb-conflict-expert` da ALTA por defecto"*;
- `objetivos-de-ahorro_conflict_report.md`: *"exactamente el patrón de la Regla 4 de `kb-conflict-expert`"*.

La norma existía en los dos sitios y **ninguna de las dos lo cubría**: la de `wf-spec-conflict` habla de *"no nombrar el workflow que la ejecuta"* en la **Sugerencia de resolución**, y la de `wf-spec-readiness` —ampliada en v0.115.2 al informe entero— también dice *"workflow"*. Una kb no es un workflow y esto no es una recomendación: es una **justificación**, el sitio donde citar la fuente es lo natural.

**Decisión.**

- **La norma pasa a ser de la clase entera, no del tipo de componente**: ni `wf-*` ni `kb-*`, ni al recomendar ni al justificar. Escrita en `kb-conflict-expert` (sección nueva, con tabla de "en vez de / escribe"), en el Paso 6 y el Paso 7 de `wf-spec-conflict`, en el Paso 7 de `wf-spec-readiness` y en la guía de fase (`pipeline/spec/CLAUDE.md`), que es donde vive el enunciado canónico.
- **La forma de citar es por contenido:** *"el mismo modelo con comportamientos distintos en dos CAs de features diferentes"* en vez de *"Regla 4 de `kb-conflict-expert`"*. El veredicto se sostiene igual —mejor, de hecho: dice **qué** regla es sin obligar a ir a buscarla— y la procedencia ya la lleva `Generado por:`.
- **La plantilla lo dice donde se rellena**, en el campo `Por qué es un conflicto`, no solo en el `SKILL.md`. Aprendizaje de [[D-085]]: el campo que pide el texto pesa más que la norma tres párrafos antes.

**Alternativas descartadas.**
- *Dejarlo pasar por leve* → la categoría del probe es "procedencia fuera de forma", sí, pero aquí no hay procedencia que preservar: el informe ya declara quién lo generó. Es jerga pura en el sitio donde alguien decide qué feature manda.
- *Prohibir citar reglas* → al revés de lo que se quiere: la cita **sostiene** el veredicto ante quien lo lee. Lo que sobra es el nombre del fichero donde vive.

**Consecuencias / aprendizaje.** Tercera vez que esta norma se escribe y **tercera vez que se escribió acotada al sitio donde apareció** — prosa del gap (v0.92.0), informe de readiness (v0.115.2), nota de gobernanza ([[D-088]]) y ahora la familia conflict. El patrón no es que la norma sea débil: es que cada vez se redacta con el **sustantivo del caso** (*"el workflow"*, *"la skill"*) en vez de con la clase (*"cualquier componente del ecosistema"*). Escribir la regla en términos de lo que se vio es lo que garantiza volver a verla en otro sitio.

**Referencias.** `pipeline/spec/skills/kb-conflict-expert/SKILL.md` · `pipeline/spec/skills/wf-spec-conflict/SKILL.md` (Pasos 6 y 7) + su plantilla · `pipeline/spec/skills/wf-spec-readiness/SKILL.md` (Paso 7) · `pipeline/spec/CLAUDE.md` · `conformance/casos-de-uso/cu-03-specs.md` (V1) · `CHANGELOG.md` 0.116.0.

---

## D-090 — Cinco auditores numerando en local, y un informe que no dice contra qué comparó

- **Fecha:** 2026-09-21 · **Estado:** Adoptada (IDs de hallazgo con prefijo de feature, campo `Conjunto comparado` en la cabecera del informe y detección de informe **ESTANCADO** en el readiness; **salió de la pasada de CU-3.d del 2026-09-18**). · **Relacionada:** [[D-056]] (el reparto de rangos de ID de gap antes del fan-out), [[D-047]] (los auditores se contradicen por diseño y arbitra el readiness), [[D-078]] (dónde se escribe el consolidado), [[D-089]] (la otra cara: un artefacto de una tanda leído en la siguiente).

**Contexto.** El Paso 7 de `wf-spec-features-first` lanza **un auditor de conflictos por spec nuevo**, en paralelo, y cada uno escribe su informe junto a su spec. Ninguno ve lo que numeran los demás. En la pasada del 2026-09-18, con cinco informes en disco (dos de una tanda anterior, tres de esta):

- **tres hallazgos distintos** etiquetados `CF-002` por tres auditores distintos;
- el `CF-001` de la tanda anterior, que no es el mismo hallazgo que el `CF-001` de esta;
- y los dos informes viejos, calculados contra un universo de **2** specs, leídos junto a tres calculados contra **5**, sin que nada en el fichero lo dijera.

Lo salvó el readiness inventándose un espacio de nombres global (`GCF-01`…`GCF-05`) y marcando a ojo cuáles eran "de la pasada anterior" — **porque el hilo principal le escribió el encargo a mano en el prompt**. Nada de eso está en ningún contrato. Y el daño, si no se salva, no es cosmético: quien decide *"manda F-001 en este choque"* cita el ID, y con dos hallazgos homónimos la decisión aterriza en el equivocado.

Los escritores del Paso 5 **sí** tienen resuelto esto desde [[D-056]]: el orquestador les reparte bloques de ID (`--gap-id-start P-031`) antes de lanzar. El fan-out de auditores no tenía equivalente.

**Decisión.**

- **El ID lleva delante el `F-00X` del spec auditado**: `CF-F001-01`, `CF-F001-02`. En modo consolidado (un informe de todo el directorio) no hay con quién colisionar y se numera `CF-01`.
- **Sin reparto, a propósito.** Copiar el mecanismo de [[D-056]] habría exigido un `--finding-id-start` nuevo, parseado por la skill y transportado por el orquestador: tres piezas que pueden quedarse a medias, y la de en medio es la que falló en [[D-081]]. El prefijo no necesita coordinación — **cada auditor ya sabe qué spec audita**.
- **El informe declara su vigencia**: campo `Conjunto comparado` en la cabecera con todos los specs que entraron (y los excluidos por `RETIRADO`, que [[D-080]] ya obligaba a nombrar). Un informe de conflictos **es válido para el conjunto que tenía delante**, y en la iteración por subsets ese conjunto crece en cada tanda.
- **El readiness lo lee y lo dice**: informe cuyo `Conjunto comparado` no cubre los specs actuales → **ESTANCADO**, con qué vio y qué no; sus hallazgos se conservan (siguen siendo ciertos sobre lo que comparó) pero no cuentan como cobertura del conjunto de ahora. Sin el campo (informes anteriores a v0.116.0) → **vigencia desconocida**, y se dice.
- **Y el readiness deja de renumerar**: los IDs ya son únicos, así que los cita tal cual — renumerar rompe la trazabilidad contra el informe de origen, que es lo que abre quien va a arreglar el choque. Para informes viejos con IDs colisionados, `<feature>:<ID>`, que desambigua sin inventar.

**Alternativas descartadas.**
- *`--finding-id-start` espejo de [[D-056]]* → ver arriba: más superficie y una pieza intermedia que ya demostró perderse.
- *Recalcular todos los informes en cada tanda* → caro (N auditores por tanda en vez de los nuevos) y no arregla el problema de fondo: un informe **sin fecha de caducidad escrita** vuelve a quedarse viejo en la tanda siguiente.
- *Que el orquestador avise de las dos cosas en el prompt del readiness* → es lo que pasó, y funcionó **esa vez**. Lo que un orquestador improvisa una vez, el siguiente no lo hace.

**Consecuencias / aprendizaje.** **Un identificador local deja de serlo en cuanto su artefacto tiene hermanos**, y el fan-out fabrica hermanos por diseño. Dos formas de arreglarlo: repartir el espacio antes (coordinación, [[D-056]]) o meter en el ID algo que el autor **ya sabe de sí mismo** (sin coordinación). Cuando la segunda existe, es la buena. Y su gemela temporal: **un artefacto derivado que no declara contra qué se derivó no se puede saber si sigue siendo verdad** — lo mismo que [[D-089]] arregla en el índice, aquí escrito en la cabecera del informe.

**Referencias.** `pipeline/spec/skills/wf-spec-conflict/SKILL.md` (Pasos 6 y 7) + `references/conflict_report_template.md` · `pipeline/spec/skills/wf-spec-readiness/SKILL.md` (Paso 4c) + su plantilla · `pipeline/spec/skills/wf-spec-features-first/SKILL.md` (Paso 7) · `conformance/casos-de-uso/cu-03-specs.md` (CU-3.d) · `CHANGELOG.md` 0.116.0.

---

## D-089 — El índice heredó un veredicto que el disco ya desmentía

- **Fecha:** 2026-09-21 · **Estado:** Adoptada (carve-out en `derive_state` + aviso de matriz estancada en `sdd-features-index.py`, 6 tests; **salió de la pasada de CU-3.d del 2026-09-18**). · **Relacionada:** [[D-077]] (el carve-out gemelo: el sello desmiente a `LISTA`), [[D-046]] (el índice es un artefacto generado, función pura de sus fuentes), [[D-083]] (*"bien formado y equivocado"* es el fallo que no se nota), [[D-090]] (la misma clase, en el informe de conflictos).

**Contexto.** `sdd-features-index.py` deriva el `Estado` de cada feature con una prioridad escrita: la `## Matriz de readiness` del `_readiness_report.md` es **autoridad** sobre la derivación mecánica, con un solo carve-out —un `LISTA` sobre un spec en `BORRADOR` baja a `BLOQUEADA` ([[D-077]])—.

En la iteración por subsets eso se rompe solo, y no hace falta que nadie se equivoque: el **Paso 6** de `wf-spec-features-first` regenera el índice **antes** del readiness del **Paso 8**, así que el único informe en disco es el de la **tanda anterior** — que listaba las features de esta tanda como `PENDIENTE_GENERACIÓN`, porque cuando se escribió era verdad. El veredicto ganaba, y el índice salía diciendo dos cosas incompatibles de la misma feature:

```
- **Ruta spec**: features/registro-de-movimientos/spec/registro-de-movimientos_spec.md
- **Estado**: PENDIENTE_GENERACIÓN
> F-001 está identificada en el discovery pero aún no tiene spec generada.
```

Medido el 2026-09-18 sobre las tres features recién escritas. **Duró tres días** —hasta que el readiness rehizo el índice— y durante ese tiempo el orquestador había narrado *"índice regenerado (8 features, universo completo)"*, que es exactamente la trampa que `CU-3.d` punto 2 avisa: la conversación decía la verdad y el fichero no.

**Decisión.**

- **Un `PENDIENTE_GENERACIÓN` sobre un spec que existe no es un veredicto: es matriz vieja.** Se descarta y la feature cae al camino marker-based. Mismo razonamiento que [[D-077]], en el otro sentido: que el fichero exista es un **hecho mecánico** del disco, el veredicto es un **juicio**, y el disco es más fresco.
- **El aviso va aparte y nombra al culpable correcto:** `⚠ matriz de readiness estancada: N feature(s) con spec en disco que el informe sigue dando por generar`. El índice se corrige solo; el `_readiness_report.md` del que salió **sigue estancado** y lo regenera una persona. Callarlo dejaría el informe viejo mandando en todo lo demás.
- **La señal es de contenido, no de `mtime`.** Se deriva de la contradicción misma (veredicto vs. spec en disco), así que sobrevive a un `git checkout` y no rompe la promesa de que la salida es función pura de las fuentes.
- **El carve-out es solo para `PENDIENTE_GENERACIÓN`.** `REQUIERE_CAMBIO_PRD` o `BLOQUEADA` sobre un spec existente son juicios que el disco no desmiente.

**Alternativas descartadas.**
- *Reordenar los pasos (readiness antes que índice)* → descartada: el readiness **lee** el índice (`Fuente: _features.md`) y lo regenera al cerrar (Paso 8.5). Invertirlos cambia una dependencia por la otra y deja el mismo agujero mirando al otro lado.
- *Borrar el `_readiness_report.md` al empezar una tanda* → destruye el único veredicto que hay mientras la tanda corre, y si se corta no queda ninguno.
- *Que el Paso 6 pase un flag "ignora el readiness"* → la decisión volvería a vivir en el orquestador y a depender de que viaje ([[D-081]]). El script tiene delante las dos evidencias: puede resolverlo solo.

**Consecuencias / aprendizaje.** **Una autoridad declarada sin fecha de caducidad se convierte en un fallo silencioso en cuanto el flujo es iterativo.** La prioridad *"el readiness manda"* se escribió pensando en una pasada única, donde el informe siempre es posterior a los specs; en cuanto hay tandas, el informe es **anterior** a la mitad de lo que describe. La pregunta que caza la clase, y que [[D-090]] contesta en el otro artefacto: *¿este insumo dice contra qué estado se calculó, o solo lo que concluyó?*

**Referencias.** `scripts/sdd-features-index.py` (`derive_state`, docstring de prioridad, aviso en `main`) · `tests/test_sdd_features_index.py::MatrizEstancadaTest` (6 tests) · `conformance/casos-de-uso/cu-03-specs.md` (CU-3.d punto 2) · `CHANGELOG.md` 0.116.0.

---

## D-088 — El probe medía media clase, y el contrato aprovechaba la otra mitad

- **Fecha:** 2026-09-17 · **Estado:** Adoptada (fuente corregida en `wf-spec-analyze`, norma ampliada, probe **V1** ampliado a `kb-*`; **salió de la pasada 17 de CU-3.a**). · **Relacionada:** [[D-085]] (una prohibición no gana a una instrucción que pide lo contrario), v0.92.0 y v0.115.2 (las dos mitades anteriores de la norma de prosa), [[D-042]] (el gap se lee **verbatim** a quien decide).

**Contexto.** El probe **V1** de CU-3 comprueba que ningún artefacto enseñe comandos, y lo hace con `grep -rnE "\bwf-[a-z][a-z0-9-]*"`. La pasada 17 dio **V1 = 0** — y el `_analysis.md` llevaba **tres nombres de skill**:

- `kb-product-change-governance`, dos veces, en la **Nota de gobernanza** de sendos bloques `[P-XXX]`;
- `kb-prd-expert`, citado como fuente al justificar un borderline en la sección de pureza.

El primero **lo prescribía el contrato**: `wf-spec-analyze` mandaba literalmente escribir *"deberá reevaluarse con `kb-product-change-governance`"*. El segundo salió solo, y es la misma forma que v0.115.2 acababa de cerrar en `wf-spec-readiness` —citar la norma que sostiene tu veredicto— en otra fase. Los dos están en prosa que, por [[D-042]], se le lee **verbatim** a una persona de producto en la vía de dictado.

**Decisión.**

- **V1 pasa a `\b(wf|kb)-`.** Un probe que mide media clase reporta verde sobre la otra mitad, que es peor que no tenerlo: da por cubierto lo que no mira.
- **La fuente deja de pedirlo:** la nota de gobernanza nombra ahora **la evaluación** (*"deberá reevaluarse con la gobernanza de cambios de producto"*), no la skill que la hace.
- **La norma de prosa del gap gana el caso general**, con sus dos formas: ni para recomendar un paso, ni para **citar la norma que sostiene un veredicto** (*"contemplado como aceptable en `kb-prd-expert`, Regla 14"* → *"en la norma de pureza del PRD"*). La segunda es la que se escapa: al justificar un borderline, lo natural es citar la fuente, y la fuente tiene nombre de skill.
- **La pasada 17 cuenta como limpia.** V1 estaba definido sobre `wf-` y sobre eso dio 0. Suspenderla con el probe ampliado **después** de verla sería mover la vara con la medida puesta — el mismo criterio que en la pasada 16 se aplicó para no ser **más duro**; aquí toca aplicarlo para no serlo tampoco.

**Alternativas descartadas.**
- *Ampliar V1 y recontar la 17 como fallida* → descartada por lo anterior. El hallazgo es del **instrumento**, no de la corrida: la conducta obedeció al contrato que tenía.
- *Backstop de linter sobre las plantillas* → descartada por ahora: el barrido enseña que en la fase Spec los nombres que quedan en plantillas son **procedencia sancionada** (`Generado por: wf-spec-discover`) o comentarios HTML que no viajan al artefacto. V1 mide la salida, que es donde se ve la verdad.

**Consecuencias / aprendizaje.** **Un probe que cubre media clase no es medio probe: es un falso verde sobre la mitad que no mira.** Y el corolario de método, que ya va por la tercera vez: la misma norma se ha arreglado en tres sitios distintos —prosa del gap (v0.92.0), informe de readiness (v0.115.2) y nota de gobernanza (aquí)— porque cada vez se escribió **acotada al sitio donde apareció**. La pregunta que lo caza: *¿qué clase es esta, y dónde más vive?*

**Pendiente, y queda anotado:** la fase **Design** tiene seis plantillas de artefacto con nombres de skill dentro (`kb-design-voice`, `kb-a11y-web-expert`, `kb-design-system-contract`, `wf-design-delta`, `wf-design-feedback`, `wf-design-intake`). No entran en esta versión porque no están en la ruta medida y requieren clasificar caso por caso lo que es procedencia y lo que es fuga — pero es el mismo patrón y hay que barrerlo.

**Referencias.** `pipeline/spec/skills/wf-spec-analyze/SKILL.md` (nota de gobernanza + norma de prosa) · `conformance/casos-de-uso/cu-03-specs.md` (probe **V1**, pasada 17) · `CHANGELOG.md` 0.115.3.

---

## D-087 — El índice del fan-out tenía seis autores y un dueño

- **Fecha:** 2026-09-16 · **Estado:** Adoptada (flag `--skip-index` en `wf-spec-fast-track`, transportado por el fan-out de `wf-spec-features-first`; **medido en la pasada 15 de CU-3.a**, que es de donde sale). · **Relacionada:** [[D-046]] (el índice es generado, no editado), [[D-083]] (*"bien formado y equivocado"* es el fallo que no se nota), [[D-085]] (una prohibición no gana a una instrucción que pide lo contrario), [[D-081]] (lo que se decide arriba tiene que viajar en el encargo).

**Contexto.** El Paso 10 de `wf-spec-fast-track` manda regenerar `_features.md` al terminar — correcto cuando la skill corre suelta. En el fan-out de `wf-spec-features-first` cada escritor llega a ese paso en un momento distinto, así que el índice del proyecto se reescribe N veces con universos parciales. Medido en la pasada 15 de CU-3.a: **seis regeneraciones entre las 07:26:12 y las 07:29:06**, y el escritor de F-004 **abriendo el índice para verificar su propia entrada** mientras sus compañeros lo reescribían.

No había daño en el estado final: `sdd-features-index.py` escribe con `tempfile` + `os.replace`, y el Paso 6 del orquestador hace la pasada autoritativa al cerrar. El contrato incluso lo bendecía en voz alta (*"es seguro aunque varios fast-tracks corran en paralelo"*). Pero durante tres minutos el índice del producto era **completo, bien formado y equivocado** —la clase que [[D-083]] marcó como la peligrosa, porque no se nota— y estaba a la vista de cualquiera que lo leyera: otro agente, un hook, un dev.

**Decisión.**

- **Flag `--skip-index` en `wf-spec-fast-track`**, declarado en el `argument-hint` (sus dos formas), parseado en el Paso 1, y que **omite el Paso 10 entero**. El Paso 11 deja de prometer un índice que no tocó.
- **El fan-out lo pasa siempre** (Paso 5 de `wf-spec-features-first`). Es la vía de [[D-081]]: lo que se decide en el orquestador **viaja en el encargo**.
- **El corte va donde nace la instrucción, no en una frase que compita.** Prohibirlo desde el prompt habría sido la trampa de [[D-085]] el mismo día que la escribimos: el `SKILL.md` que el delegado ejecuta le dice que regenere, así que una prohibición en el encargo es una contradicción que resuelve su juicio.
- **La atomicidad se queda como red, no como justificación.** La frase del Paso 10 lo dice ahora así: dos regeneraciones simultáneas nunca dejan un fichero a medias, pero eso no es razón para hacerlo N veces.
- **Y el escritor no se mira en el índice.** Dentro de una tanda, que su `F-00X` aparezca no significa nada y que no aparezca tampoco: lo que confirma su trabajo es el spec en disco y el `seal`.

**Alternativas descartadas.**
- *Solo las notas de contrato, sin flag* (la versión que se aplicó primero) → insuficiente: dejaba en pie seis ejecuciones que nadie usa y una ventana de índice equivocado que solo el juicio del lector evitaba. Las notas **se quedan** —son lo que explica el reparto—, pero el mecanismo lo cierra el flag.
- *Prohibirlo desde el prompt del orquestador* → descartada por [[D-085]] (ver arriba).
- *Que el escritor detecte solo si está en una tanda* → descartada: no puede saberlo sin que se lo digan, y adivinarlo es precisamente lo que un argumento evita.

**Consecuencias / aprendizaje.** **Un artefacto con N autores y un dueño no se arregla solo diciendo quién manda: se arregla quitando la pluma a quien no la necesita.** El reparto escrito ayuda a quien lee el contrato; el flag lo hace cierto aunque nadie lo lea. Contrapartida asumida y anotada: si la tanda se corta a medias, el índice ya no queda parcial — queda **como estaba antes de empezar**, hasta que alguien ejecute la pasada del Paso 6. Es el mejor de los dos estados malos: un índice viejo se reconoce, uno reescrito a medias no. El Paso 6 dice ahora que se ejecuta igual aunque la tanda se corte.

**Referencias.** `pipeline/spec/skills/wf-spec-fast-track/SKILL.md` (`argument-hint`, Pasos 1, 9, 10 y 11) · `pipeline/spec/skills/wf-spec-features-first/SKILL.md` (Pasos 5 y 6) · `scripts/sdd-features-index.py` (escritura atómica) · `conformance/ROADMAP.md` (fila de `wf-spec-fast-track`) · `conformance/casos-de-uso/cu-03-specs.md` (pasada 15) · `CHANGELOG.md` 0.115.1.

---

## D-086 — La variable de directorio de skill la expande el harness, así que no se puede relevar

- **Fecha:** 2026-09-16 · **Estado:** Adoptada (9 prompts reescritos + backstop determinista `RELAY-SKILLDIR-EXPANDED` con 6 tests; **medida en la pasada 15 de CU-3.a**). · **Relacionada:** [[D-044]] (el delegado ejecuta la sub-skill leyendo su `SKILL.md`, no la invoca con el `Skill` tool), [[D-047]] (el fan-out y su prompt), [[D-084]] (la instrucción que se cumple a medias sin que nadie lo note).

**Contexto.** Los orquestadores que delegan (`wf-spec-features-first`, `wf-prd-change-cascade`) mandan al delegado leer el `SKILL.md` de otra skill y ejecutarlo él mismo ([[D-044]]). Como ese `SKILL.md` usa `${CLAUDE_SKILL_DIR}` para referenciar sus propias plantillas, el prompt llevaba una frase de mapeo:

```
Dentro de ese SKILL.md, `${CLAUDE_SKILL_DIR}` es `.claude/skills/wf-spec-fast-track/`.
```

**Esa frase no puede funcionar, y no es culpa de quien la releva.** La documentación de Claude Code es explícita: la sustitución de `${CLAUDE_SKILL_DIR}` la hace **el harness al cargar el `SKILL.md`**, con el directorio de *esa* skill. Un token escrito en el cuerpo del emisor se expande **al directorio del emisor** antes de que el modelo lo vea. Comprobado en el transcript de la pasada 15: el contenido del `SKILL.md` que llegó al contexto de main ya venía expandido, así que lo que salió en las 10 delegaciones fue

```
Dentro de ese SKILL.md, `<raíz-del-proyecto>/.claude/skills/wf-spec-features-first` es `.claude/skills/wf-spec-analyze/`.
```

—una afirmación falsa. Main copió con fidelidad lo que le dieron; nunca tuvo el token delante.

**Y el mapeo hace falta.** El delegado no invoca la skill con el `Skill` tool: hace `cat` de su `SKILL.md`. Un `cat` es lectura de fichero y ahí **no hay sustitución**, así que recibe el token crudo. Exposición medida en una sola pasada: 8 escritores × 3 tokens + 10 exploradores/auditores × 1 = **34 resoluciones por inferencia**, todas correctas, ninguna sostenida por el contrato. El modo de fallo es concreto: un delegado que meta el token tal cual en un `cat` acaba haciendo `cat /references/feature_spec_template.md`.

**Decisión.**

- **Las 9 frases de mapeo dejan de usar la sintaxis `${...}`**: *"las rutas que empiecen por la variable de directorio de skill (`CLAUDE_SKILL_DIR`) se resuelven contra `.claude/skills/<target>/`"*. Sin `${`, no hay nada que sustituir y la información llega entera.
- **Los 7 tokens de las skills que se ejecutan por delegado se quedan como están.** Sustituirlos por rutas literales hardcodearía `.claude/skills/…`, que es justo lo que la variable existe para evitar (plugins, otras raíces de instalación). Lo que los arregla es que el mapeo funcione.
- **Backstop `RELAY-SKILLDIR-EXPANDED`** (blocking, 6 tests): un `${CLAUDE_SKILL_DIR}` dentro de una línea de `prompt:` que manda leer el `SKILL.md` de **otra** skill. La precisión viene del patrón de relevo: un token que apunta a un fichero **del propio emisor** se expande bien y no dispara.

**Alternativas descartadas.**
- *Que el orquestador lo pase literal* → **imposible**: no lo tiene. Es la lección de esta entrada.
- *Escapar el token (`$\{CLAUDE_SKILL_DIR\}` u otra forma)* → descartada: depende de los internos del sustituidor, que no están documentados. Nombrar la variable sin la sintaxis no depende de nada.
- *Quitar la frase y dejar que el delegado infiera* → descartada: funcionó 34 de 34 veces por inferencia, y un contrato que se apoya en que el delegado acierte no es un contrato.

**Consecuencias / aprendizaje.** **Una variable que expande el harness no se puede reenviar: al llegar al mensaje ya no es una variable, es el valor de quien la escribió.** El emisor no puede hablar del token porque nunca lo tiene. Y el corolario del modelo de ejecución: **[[D-044]] salta la sustitución por diseño** —el delegado lee el fichero en vez de cargar la skill—, así que todo `${CLAUDE_SKILL_DIR}` de una skill ejecutada por delegado es texto crudo para él. La pregunta que caza la clase: *¿quién expande esto, y sigue teniendo el mismo significado donde va a leerse?*

**Referencias.** `pipeline/spec/skills/wf-spec-features-first/SKILL.md` (3 prompts) · `pipeline/prd/skills/wf-prd-change-cascade/SKILL.md` (6 prompts) · `scripts/sdd-structural-lint.py` (`RELAY-SKILLDIR-EXPANDED`) · `tests/test_sdd_structural_lint.py` (6 tests) · `CHANGELOG.md` 0.115.1.

---

## D-085 — Una prohibición de vocabulario no gana a una instrucción que pide ese vocabulario

- **Fecha:** 2026-09-16 · **Estado:** Adoptada (norma ampliada + instrucción del campo reescrita en la plantilla; **medida en la pasada 15 de CU-3.a**, que es de donde sale). · **Relacionada:** [[D-042]] (el gap se presenta sin abrir el fichero, y quien lo presenta lo lee verbatim), [[D-055]] (cuándo le llega la norma a quien escribe), v0.92.0 (la prosa de los gaps en claro, y el probe V2 que la mide).

**Contexto.** v0.92.0 puso la norma de que la prosa de un gap `[P-XXX]` va en claro —el `Contexto`, el `Problema` y la `Pregunta para el cliente` los lee una persona de producto— y el probe **V2** de CU-3 la mide con un `grep` de siglas. La pasada 9 devolvió **1 hallazgo real**. La pasada 15 (2026-09-16, v0.115.0, `myops-app-specs`) devolvió **3**, los tres de la misma forma:

```
- **Problema**: sin esto no se puede escribir un CA verificable para "marcar una deuda
  como saldada": no queda claro si esa acción registra la entrada de dinero…
```

Lo que descarta la explicación fácil: **la norma llegó, y a tiempo**. El `.jsonl` del `sdd-spec-explorer` enseña el orden —`cat SKILL.md` (con la sección *"el ID es contrato, la sigla suelta es jerga"*) → `cat output_template.md` (con la nota *"Al redactar cada gap"*) → `Read prd/prd.md` → `Write prd/prd_analysis.md`—, así que V3 está verde y el defecto no es de carga. Son dos causas sumadas, las dos en el contrato:

1. **La norma cubría una sola forma de la fuga.** Todos sus ejemplos son la sigla como **abreviatura de algo que ya existe** en un documento (*"el CA de X"*, *"sin THEN verificable"*). La frase que se cuela es la otra: la sigla como **el artefacto que todavía no puedes escribir**. Ahí no se abrevia nada — se explica por qué el hueco bloquea, y lo natural es explicarlo nombrando el entregable que no sale.
2. **La instrucción del propio campo pedía justamente eso.** El placeholder decía `[por qué esto es un gap funcional que **bloquea el spec**]`. Se le pide que explique qué le impide al spec y contesta hablando del spec. Y a veinte líneas, en la misma plantilla, la sección **Testabilidad** tiene un campo **homónimo** cuyo ejemplo es jerga pura y a propósito (`[vago / no verificable / dependiente de otro CA / sin GIVEN o sin THEN]`): el único de los dos `Problema` con ejemplo redactado era el que no debía servir de modelo.

**Decisión.**

- **La norma gana la segunda forma**, con su prueba de corte: *"no se puede escribir un CA verificable para X"* → *"no se puede comprobar de forma objetiva qué pasa cuando X"*, y el criterio que separa las dos — **la frase tiene que sostenerse ante alguien que no sabe que existe una fase Spec**.
- **El campo deja de preguntar por el entregable bloqueado.** `Problema` pide ahora *"qué decisión de producto queda sin cerrar, y qué no se puede comprobar mientras siga así — en los términos del producto"*. Mismo cambio en el bloque `[PUEDE_REQUERIR_CR]`.
- **El `Problema` de Testabilidad se marca como lo que no es**: un comentario en la plantilla dice que no es el modelo del `Problema` de los `[P-XXX]`, aunque se llamen igual. El `SKILL.md` ya lo distinguía (borde 3); lo que faltaba era decirlo **donde está el ejemplo**.

**Alternativas descartadas.**
- *Backstop determinista (una regla de lint que prohíba la sigla en el campo)* → descartada por ahora: **V2 ya es el probe**, corre sobre el artefacto generado y distingue las exenciones (leyenda, Testabilidad, `Afecta`) con criterio que una regex sobre la skill no tiene. Un guard estructural aquí mediría el texto del contrato, no la prosa que sale.
- *Dejar que lo traduzca quien presenta el gap* → descartada, y ya lo estaba: [[D-042]] le da contrato de leerlo **verbatim** justo para que sea medible con un diff en vez de con un juicio. Si el campo nace en claro, no hay nada que traducir.

**Consecuencias / aprendizaje.** **Una norma que prohíbe un vocabulario no gana a una instrucción que lo pide**: mientras las dos convivan en el mismo contrato, la que se está respondiendo es la instrucción — la norma solo se recuerda, el campo se rellena. Y el corolario de forma: **dos campos homónimos con reglas opuestas, y solo uno con ejemplo, es el ejemplo el que manda**. La pregunta que caza la clase: *¿qué le pido literalmente a quien rellena este campo, y es compatible con lo que le prohíbo tres párrafos antes?*

**Referencias.** `pipeline/spec/skills/wf-spec-analyze/SKILL.md` (norma de prosa del gap) · `pipeline/spec/skills/wf-spec-analyze/references/output_template.md` (campos `Problema`, nota de redacción, comentario de Testabilidad) · `conformance/casos-de-uso/cu-03-specs.md` (probe **V2**, pasada 15) · `CHANGELOG.md` 0.115.1.

---

## D-084 — El fan-out no se rompe por ignorancia, se rompe por prudencia: la llamada de prueba

- **Fecha:** 2026-09-15 · **Estado:** Adoptada (contrato reforzado en los 3 emisores + backstop determinista con 6 tests; **medida en la pasada 14 de CU-3.a**, que es de donde sale). · **Relacionada:** [[D-047]] (el fan-out es una barrera: N llamadas en un mensaje + el flag), [[D-043]] (`run_in_background: false`), [[D-050]] (lo que devolvió el efecto al flag: `CLAUDE_CODE_FORK_SUBAGENT=0` en el consumer), [[D-048]] (el hook que contaba llamadas y se retiró por degradar la conducta), [[D-045]] (decidir en main, ejecutar en el fork).

**Contexto.** El contrato del fan-out lleva escrito desde [[D-047]] y es explícito, en negrita y en mayúsculas: *"emite TODOS los `Agent` tool calls en un único mensaje — no esperes entre ellos"*. La pasada 14 de CU-3.a (2026-09-15, v0.114.1, `myops-app-specs`) lo incumplió **sin contradecirlo**:

```
12:58:33  Agent → Spec F-001                  (un mensaje, una llamada)
13:04:24  tool_result                          ← 351 s esperando
13:04:27  «F-001 listo. Lanzo las tres restantes en paralelo.»
13:04:32  Agent → Spec F-002 ┐
13:04:35  Agent → Spec F-004 ├ (un mensaje, tres llamadas)
13:04:38  Agent → Spec F-005 ┘
```

El subset estaba fijado en cuatro **antes** de empezar (el usuario lo eligió en el gate del Paso 4b), no hubo interrupción, y el **mismo orquestador**, veinte minutos después, emitió los cuatro auditores de conflicto en un solo mensaje. No es desconocimiento del patrón: es **la tentación de probar primero**. Y la frase con la que lo narró —*"lanzo las tres restantes en paralelo"*— es literalmente cierta, que es lo que la hace difícil de ver: la instrucción hablaba de emitir juntas, y emitió juntas… las que quedaban.

El daño ya no es teórico. Hasta [[D-050]] esto era inocuo porque el harness lanzaba los delegados en segundo plano y solapaban igual; con `CLAUDE_CODE_FORK_SUBAGENT=0` el flag surte efecto de verdad, así que **cada mensaje es una barrera**: el Paso 5 tardó 10,6 min donde cabían ~6, y con seis features serían seis rondas en vez de una.

**Decisión.**

- **El número de llamadas lo fija el paso anterior, no el resultado de la primera.** Los tres emisores de fan-out del ecosistema —`wf-spec-features-first` (Pasos 5 y 7), `wf-prd-change-cascade` (Paso 6) y `wf-design-variant`— dicen ahora, además de *"todas en un único mensaje"*, que **no hay llamada de prueba**: lanzar una para ver si el patrón funciona y emitir el resto después ya rompió la barrera, aunque las restantes salgan juntas.
- **Y dicen por qué no confirma nada.** Los delegados son independientes, no comparten estado y ninguno depende del anterior: si el primero fuera a fallar por una precondición común, los otros fallan igual y te enteras en el mismo turno. El hedge se paga siempre y no compra información.
- **La instrucción se hace contable, y se coloca donde se emite.** El Paso 5 abre ahora con *"antes de emitir, cuéntalas"* justo delante del bloque `Agent(`, en vez de dejar el invariante solo en un párrafo posterior al template.
- **Backstop determinista `FANOUT-PILOT-UNGUARDED` (blocking, 6 tests)** en `sdd-structural-lint.py`: una `wf-*` que ordena emitir N llamadas `Agent` en un único mensaje y **no nombra la llamada de prueba**. La señal es la orden de fan-out, que es de alta precisión: hoy da exactamente tres sujetos, los tres emisores. **Delta probado**: con el guard retirado, el check levanta el hallazgo en `wf-spec-features-first:511`.

**Alternativas descartadas.**

- **Un `PreToolUse` que cuente llamadas `Agent` por mensaje y deniegue las tandas parciales.** Es exactamente `sdd-agent-sync.py`, que [[D-048]] puso y [[D-050]] **retiró entero**: costó dos pasadas de conformance sin medir nada y **degradaba la conducta del modelo** (siguiendo la prosa emitía el booleano 20/20; reaccionando al `deny`, mandaba la cadena `"false"` 5/5). Y aquí no funcionaría ni en principio: el hook ve una llamada, no sabe cuántas *debería* haber — el número vive en una decisión de producto tomada dos pasos antes.
- **Bajar el fan-out a un script que lance los N agentes.** Un script no puede invocar la tool `Agent`: el fan-out es del orquestador por construcción.
- **Dar el desvío por aceptable porque "acaba igual".** No acaba igual desde [[D-050]], y aunque acabara: el Paso 6 regenera el índice leyendo de disco los specs de **todas** las features, y arrancarlo con una tanda a medias produce un índice incompleto que además se sella como bueno.

**Consecuencias y aprendizaje.**

- **Una instrucción que el modelo puede cumplir a medias sin notarlo no es una instrucción, es una aspiración.** *"Emítelas en un único mensaje"* es verdadera de cualquier subconjunto que se emita junto. El invariante que no admite lectura parcial es el **cardinal**: cuántas llamadas lleva ese mensaje, fijado antes de emitir la primera.
- **El desvío que hay que nombrar no es el tonto, es el prudente.** Nadie manda las llamadas de una en una por descuido; se manda una de prueba porque parece responsable antes de gastar cuatro agentes. Un contrato que solo prohíbe la versión torpe deja pasar la versión razonable, que es la que de verdad ocurre.
- **Y el instrumento aguantó:** el escenario predijo este fallo literalmente —*"el día que el flag surta efecto, mensajes separados serializan el fan-out"*— y lo dejó escrito como FALLO citable antes de que ocurriera. La pasada no lo descubrió: lo **confirmó**.

**Referencias.** `pipeline/spec/skills/wf-spec-features-first/SKILL.md` (Pasos 5 y 7), `pipeline/prd/skills/wf-prd-change-cascade/SKILL.md` (Paso 6), `pipeline/design/skills/wf-design-variant/SKILL.md`, `scripts/sdd-structural-lint.py` (`FANOUT-PILOT-UNGUARDED`), `tests/test_sdd_structural_lint.py` (6 casos), `conformance/casos-de-uso/cu-03-specs.md` (CU-3.a probe 5 y pasada 14, CU-3.d punto 3), `conformance/ROADMAP.md`.

---

## D-083 — El gate humano del brownfield: sin puerta de vuelta y con el mapa desprotegido

- **Fecha:** 2026-09-15 · **Estado:** Adoptada (reglas escritas + backstop determinista con 6 tests; conducta **sin medir** — CU-4.g y CU-4.h nacen `⏱ sin pasada`). · **Relacionada:** [[D-081]] (el `_discovery.md` que ya existe se reutiliza), [[D-082]] (un `STOP_*` que espera respuesta declara su argumento), [[D-062]] (qué artefacto lleva gate de sobreescritura y cuál no), [[D-080]] (una decisión humana registrada no se pisa regenerando).

**Contexto.** [[D-081]] y [[D-082]] se escribieron el mismo día sobre la mitad greenfield de la fase y las dos dejaron fuera al **mismo fichero**: el `_code_discovery.md` del onramp brownfield. Son dos agujeros del mismo gate, el del Paso 3 de `wf-spec-from-code`, que **para siempre** para que una persona confirme, corrija o descarte capacidades:

1. **El mapa no estaba protegido.** `discover` escribía el `_code_discovery.md` sin comprobar si ya existía — ni `STOP_ARTEFACTO_EXISTE` ni override. Y es, por construcción, un artefacto **con trabajo humano dentro**: el gate existe precisamente para depositarlo ahí. La petición que lo destruye es la normal —*"mira también el módulo de facturación"*, *"vuelve a pasar por el código"*—: la segunda pasada reescribía el mapa entero, borraba los descartes razonados (que vuelven a proponerse como candidatas, como si nadie los hubiera mirado) y podía renumerar los `F-C-00X` que las cabeceras de los specs ya generados citan. Es literalmente el daño que [[D-081]] describió para el `_discovery.md`, en el fichero gemelo.
2. **El gate no declaraba canal de vuelta.** El Paso 3 decía que *"las correcciones que traiga esa invocación se aplican al `_code_discovery.md`"* sin que hubiera **por dónde**: el `argument-hint` no tenía nada donde cupiera una decisión por capacidad. La vuelta quedaba a que el texto libre de la re-invocación se pareciera lo suficiente — el mismo modo de fallo que [[D-082]] acababa de cerrar para los `[INFERIDO]`.
3. **Y un tercero que apareció al revisar los consumidores del fichero:** `sdd-features-index.py` busca el discovery con el glob `*_discovery.md`, y `<scope>_code_discovery.md` **encaja por puro sufijo**. En una adopción ([[D-079]]) los dos conviven en la misma raíz de artefactos y `sorted()` decide por orden alfabético: `billing_code_discovery.md` gana a `prd_discovery.md`, así que el índice salía con el universo de features equivocado —capacidades brownfield en vez de las del PRD—, y además con el nombre equivocado (`billing_code_features.md`) **cuando aún no había índice previo**: si lo hay, el script reutiliza ese fichero como salida y el daño es solo el universo, que es la mitad que nadie mira. En brownfield puro el daño es menor y también real: el mapa tiene otro formato, así que la feature se indexaba **sin nombre** (`F-C-001: F-C-001`) y la cabecera declaraba `discovery=sí` sobre un discovery que no existe.

**Decisión.**

- **El mapa se protege como cualquier artefacto con trabajo humano dentro** ([[D-062]]). `discover` resuelve el path y comprueba existencia **antes de explorar** (no después: parar tras diez minutos de exploración es un gate que cuesta lo mismo que no tenerlo), para con `STOP_ARTEFACTO_EXISTE` y solo reescribe con `--allow-overwrite-code-discovery` armado por el usuario. El bloqueo **nombra las dos salidas buenas** —aplicarle la validación, o generar el spec de una capacidad que ya está dentro— y no solo el override, que es la lección exacta de [[D-081]].
- **La validación humana vuelve por `--capabilities`**, con las tres vías como valores exactos: `F-C-00X=confirmada`, `descartada: <motivo>`, `corregida: <texto>`. Es un **segundo turno que no explora**: registra decisiones sobre el mapa existente. Lo que no se decide sigue sin validar y se nombra; lo mal escrito se rechaza en vez de traducirse a la vía más parecida; una `F-C-00X` que no está en el mapa no se inventa. El header pasa a `Validación: <fecha>` solo cuando no queda ninguna pendiente.
- **Un descarte es terminal mientras esté en el mapa.** `generate --feature` sobre una capacidad `DESCARTADA` para con `STOP_CAPACIDAD_DESCARTADA` y no escribe nada: caracterizarla reintroduce por la puerta de atrás justo lo que el gate dejó fuera. No lo cierra ningún flag —lo que corresponde es revisar el mapa, no saltárselo—, así que el párrafo de gates de `routing.md` pasa de tres `STOP_*` sin escotilla a cuatro.
- **El mapa no es un discovery, y quien lo busca por glob tiene que saberlo.** `sdd-features-index.py` descarta los `*_code_discovery.md` en su **barrido automático** (local y cruce de frontera de topología); un `--discovery <path>` explícito se respeta tal cual, porque es una orden de quien invoca y el filtro existe para el descubrimiento, no para vetar una vía. Sin mapa-como-discovery, el brownfield puro cae en la rama "sin discovery" y construye el índice **desde los specs**, que es exactamente lo que `wf-spec-from-code` promete para ese caso.
- **Y los demás que globean por sufijo, con él.** `sdd-resolve-path.py` aplica la misma exclusión a su kind `discovery` —hoy sin consumidor, mina puesta para el primero que lo use— y los dos sitios que enumeran en prosa los derivados del PRD (`wf-prd-sync-impact` Paso 2 y `kb-product-change-governance` Regla 6) dicen ahora que el mapa **no entra**: no deriva del PRD sino del código, así que medir su deriva contra un cambio de producto es declarar `stale` lo que ningún cambio de PRD afecta.
- **Backstop determinista `HUMAN-GATE-UNPROTECTED` (blocking, 6 tests)** en `sdd-structural-lint.py`: una `wf-*` que para con un `STOP_*_SIN_VALIDAR` sobre un artefacto que ella misma escribe y no nombra `STOP_ARTEFACTO_EXISTE` en ninguna parte del fichero. La señal es el **veredicto**, no el defecto: si paras para que alguien valide lo que acabas de escribir, ese fichero tendrá trabajo humano dentro en cuanto el gate se cierre. Aquí tampoco hay `PreToolUse` posible —estos flujos reciben un path de **código** o de **UI** y derivan el nombre del artefacto de su scope, así que ningún gate lo resuelve desde los argumentos—, y por eso el backstop es estructural. Sobre el árbol actual da exactamente dos sujetos: `wf-spec-from-code` (el defecto) y `wf-design-extract` (que ya cumplía).

**Alternativas descartadas.**

- **Exigir `Validación:` estampada para poder generar.** Convertiría en gate duro lo que hoy es una confirmación implícita legítima: pedir *"genera el spec de F-C-001"* **es** validar esa capacidad. Habría roto el flujo normal de quien no usa el argumento nuevo, a cambio de nada — lo que hace daño no es generar sin sello, es generar lo que alguien ya descartó.
- **Un check genérico de "escribe un artefacto y no tiene gate de sobreescritura".** Sin lista mantenida a mano no se distingue estructuralmente de los informes derivados a los que [[D-062]] **quitó** el gate por no proteger nada, y con lista es la tercera copia de un inventario que deriva ([[D-069]]). El `STOP_*_SIN_VALIDAR` es la señal que sí distingue las dos clases, porque la declara el propio autor.
- **Aplicar las decisiones en `generate` en vez de en `discover`.** Deja las capacidades **descartadas** sin sitio donde registrarse: solo se anotaría lo que se genera, y el resultado más valioso del gate —un descarte razonado— no llegaría nunca al fichero.

**Consecuencias y aprendizaje.**

- **Un nombre de fichero que encaja en un glob ajeno es un acoplamiento que nadie declaró.** El mapa brownfield no se llamó `_code_discovery.md` para que el índice lo leyera — se llamó así porque describe un descubrimiento. Basta el sufijo compartido para que otra pieza lo trague, y el fallo no es ruidoso: produce un índice completo, bien formado y equivocado.
- **Una decisión que arregla un patrón solo lo arregla donde miraste.** [[D-081]] y [[D-082]] describieron los dos defectos con precisión y los cerraron en la mitad greenfield; el onramp brownfield tiene los mismos ficheros con otro nombre (`_code_discovery.md` por `_discovery.md`, capacidades por features) y no entró en el barrido. La pregunta que lo caza: *¿cuál es el gemelo de este fichero en la otra entrada del pipeline, y también lo arreglé?*
- **Un artefacto que existe para ser validado por una persona es, desde ese momento, el más caro de recuperar.** Un spec se regenera del PRD y un informe de la pasada siguiente; el juicio de quien miró el código y dijo *"esto es código muerto"* no se regenera con nada.
- **Un gate bien diseñado en la ida puede estar sin terminar en la vuelta**, y se nota poco porque la ida es la que se prueba: el fork para, devuelve el material y el informe se ve completo.

**Referencias.** `pipeline/spec/skills/wf-spec-from-code/SKILL.md` (frontmatter y Pasos 1, 2, 3, 3b y 4), `pipeline/spec/routing.md`, `pipeline/spec/README.md` (caso 2.b, tabla de workflows, checkpoints humanos), `pipeline/orchestration.md` (familia `--allow-overwrite-*`), `scripts/sdd-structural-lint.py` (`HUMAN-GATE-UNPROTECTED`), `scripts/sdd-features-index.py` (`first_discovery`/`is_code_discovery`), `scripts/sdd-resolve-path.py` (`GLOB_EXCLUDE`), `pipeline/spec/skills/wf-prd-sync-impact/SKILL.md` (Paso 2), `pipeline/prd/skills/kb-product-change-governance/SKILL.md` (Regla 6), `tests/test_sdd_structural_lint.py`, `tests/test_sdd_features_index.py`, `tests/test_sdd_resolve_path.py`, `conformance/casos-de-uso/cu-04-brownfield.md` (CU-4.a, CU-4.b, CU-4.e, CU-4.g, CU-4.h), `conformance/ROADMAP.md`, `docs/entender/funcional.md`.

---

## D-082 — Un hallazgo sin vía de salida, y un bloqueo sin puerta de vuelta

- **Fecha:** 2026-09-15 · **Estado:** Adoptada (reglas escritas; conducta **sin medir** — CU-3.w nace `⏱ sin pasada` y CU-3.q gana un punto). · **Relacionada:** [[D-068]] (el `STOP_INFERIDO_SIN_CONFIRMAR` y sus tres vías), [[D-059]] (autor≠verificador), [[D-061]] (el sello del spec), [[D-077]] (lo que promete el informe vs. lo que exige el gate).

**Contexto.** Los dos son el mismo defecto en sitios distintos: **una pieza que termina su trabajo señalando algo, sin que exista la vía por la que ese algo se resuelve.**

1. **El informe de conflictos.** `kb-conflict-expert` define cinco reglas de detección y una tabla de severidad, y termina en "Qué NO es un conflicto": no dice en ninguna línea **qué se hace** con un conflicto detectado. La única indicación de salida de toda la fase estaba en el último paso de `wf-spec-conflict`: *"Resuelve los conflictos marcados como ALTA antes de planificar. **Edita los specs afectados** y pídeme una nueva revisión"*. Y esa frase manda exactamente a donde no hay que ir — una edición a mano **conserva el sello**: el spec sigue diciendo `Estado: VALIDADO` con un contenido que ya no es el que se auditó, y `gate_spec_fiable` lo deja pasar. Las vías de evolución existen precisamente porque desellan al tocar.
2. **La vuelta del `[INFERIDO]`.** [[D-068]] partió la confirmación en dos turnos: el fork para con `STOP_INFERIDO_SIN_CONFIRMAR` y devuelve el material; el hilo principal presenta las tres vías; **las decisiones vuelven en una invocación nueva**. El texto de `wf-spec-gap-resolve` decía *"si vienen decididos, aplícalas tal cual"* — y no había **por dónde** vinieran: su Paso 1 parseaba `<spec>` y `--analysis`, y su `argument-hint` no tenía nada donde cupiera una decisión por CA. El segundo turno dependía de que el texto libre de la invocación se pareciera lo suficiente.

**Decisión.**

- **El conflicto se corrige por las vías que desellan, y quien lo dice es el informe.** El último paso de `wf-spec-conflict` deja de mandar a editar a mano: ofrece **aplicar el cambio sobre el spec que toque** —descrito como acción, sin nombrar el workflow— y advierte de que la corrección reabre la validación. Misma corrección en la plantilla de salida de `wf-spec-features-first`.
- **Y deja de prometer planificación.** *"Los specs están listos para pasar a planificación"* era la misma promesa que [[D-077]] retiró del readiness, viva en la otra rama: que no haya conflictos no hace fiable un spec — el gate exige además el sello, y uno recién generado nace en borrador.
- **Un `STOP_*` que espera respuesta declara el argumento por el que esa respuesta entra.** `wf-spec-gap-resolve` gana `--inferred 'CA-XXX=confirmado; CA-YYY=incorrecto: <texto>; CA-ZZZ=no-lo-se'`, con las tres vías de [[D-068]] como valores exactos. Un `CA-XXX` que no esté `[INFERIDO]` no se toca; una vía mal escrita **no se interpreta** —`no-lo-se` no es `incorrecto`—; y los `[INFERIDO]` que no aparezcan siguen sin confirmar y vuelven a devolverse.

**Alternativas descartadas.**

- **Dejar que el conflicto lo resuelva quien quiera y como quiera.** Es lo que había, y el coste no se ve: el spec editado a mano pasa el gate, así que el fallo aparece dos fases más abajo, en un plan construido sobre un spec que nadie auditó.
- **Que `wf-spec-conflict` corrija lo que encuentra.** Rompe autor≠verificador ([[D-059]]) y además no puede: el auditor tiene `Write`/`Edit` prohibidos por norma ([[D-051]]).
- **Pasar las decisiones de los `[INFERIDO]` en el texto libre de la invocación.** Es lo que había de facto. Funciona cuando el que invoca y el que ejecuta comparten conversación, y falla en el caso normal —sesión nueva, otro día— exactamente igual que falló [[D-051]] con las respuestas de los gaps.

**Consecuencias y aprendizaje.**

- **Un detector sin vía de salida no está terminado.** Escribir las cinco reglas de detección es la mitad visible del trabajo; la otra es decir qué se hace con lo detectado, y es la que se olvida porque el informe ya "se ve completo".
- **Un protocolo de dos turnos necesita el canal del segundo.** [[D-068]] diseñó bien la ida —qué material devuelve el fork, quién presenta las tres vías— y dejó la vuelta sin contrato. Un bloqueo que espera una respuesta y no declara por dónde entra solo se cierra por casualidad.
- La pregunta que caza a los dos: *¿por dónde vuelve lo que acabo de pedir, y existe?*

**Referencias.** `pipeline/spec/skills/wf-spec-conflict/SKILL.md` (Pasos 2 y 9), `pipeline/spec/skills/wf-spec-gap-resolve/SKILL.md` (frontmatter y Pasos 1 y 3), `pipeline/spec/skills/wf-spec-features-first/references/output_template.md`, `pipeline/spec/routing.md`, `conformance/casos-de-uso/cu-03-specs.md` (CU-3.w, CU-3.q punto 5).

---

## D-081 — Tres puntos ciegos del orquestador: el gate que no viaja, el artefacto que ya estaba y el `STOP_*` sin rama

- **Fecha:** 2026-09-15 · **Estado:** Adoptada (reglas escritas; conducta **sin medir** — CU-3.u y CU-3.v nacen `⏱ sin pasada`). · **Relacionada:** [[D-045]] (los gates de features-first viven en main), [[D-026]] (los `--allow-*` los arma el usuario), [[D-064]] (un worker para y reporta), [[D-053]] (una decisión, una pregunta).

**Contexto.** `wf-spec-features-first` delega cinco veces y sostiene cuatro gates. Los tres defectos son de la **costura** entre esas dos mitades, no de ninguna de ellas:

1. **La decisión del gate de alcance no bajaba al fan-out.** El Paso 2.5 presenta el gate de expansión de producto y, si el usuario elige *continuar con alcance derivado*, eso equivale a `--allow-derived-scope-from-analysis`. El flag se propagaba al discover y **no al prompt de los escritores** — cuya lista de argumentos lo omitía—. Y como cada escritor recibe `--analysis`, **vuelve a evaluar** las mismas respuestas y se detiene con `STOP_REQUIERE_PRD_CHANGE`: la pasada entera se para levantando N veces una pregunta ya contestada, dentro de forks que no pueden presentarla.
2. **El Caso B del discovery no miraba si ya existía.** Sin `--features`, el workflow delegaba el discovery **siempre**. El worker se detiene por su cuenta si el artefacto está en disco —con razón: regenerarlo renumera los `F-00X` que los specs ya citan—, pero el único camino que su bloqueo nombra es `--allow-overwrite-discovery`, que es el peligroso. La salida correcta, reutilizar, solo estaba escrita en el Caso A, **detrás de `--features`**. Un usuario que primero pregunta *"¿qué features tiene este PRD?"* y luego dice *"genéralas"* llegaba por la puerta sin salida buena.
3. **Un `STOP_*` de un delegado no tenía rama.** El Paso 5 pedía registrar "si se completó con éxito o falló". Un `STOP_*` no es un fallo: es un bloqueo con nombre que alguien tiene que presentar.

**Decisión.**

- **Lo que se decide en un gate viaja con el encargo.** El prompt del fan-out lleva `--allow-derived-scope-from-analysis` cuando el Paso 2.5 lo dejó decidido —de entrada o por elección del usuario—. Lo que no cambia es [[D-026]]: el orquestador **transporta** el override que el usuario armó, nunca lo arma él.
- **Un `_discovery.md` que existe se reutiliza.** El Caso B comprueba primero, con la misma búsqueda del Caso A, y lo dice en el informe. La regla sube además a `routing.md`, porque aplica al hilo principal fuera de este workflow.
- **Cada `STOP_*` esperable tiene su rama.** El Paso 3 distingue `STOP_OWNERSHIP_AMBIGUO` de `STOP_ARTEFACTO_EXISTE`; el Paso 5 enumera los tres que puede devolver un escritor y qué hacer con cada uno, dejando claro que los demás escritores siguen siendo válidos y que un `STOP_*` **no se entierra como error genérico** ni se relanza con un `--allow-*` de cosecha propia.

**Alternativas descartadas.**

- **Que el escritor no reevalúe el alcance si ya viene un analysis respondido.** Quitaría el guardrail justo donde escribe el spec, que es el último sitio donde el alcance derivado se puede marcar. El problema no era que evaluara: era que no le llegaba la decisión.
- **Que el Caso B relance el discover con `--allow-overwrite-discovery` al ver el `STOP_*`.** Es auto-armar un override ([[D-026]]) y, encima, el override equivocado: renumera los `F-00X`.
- **Tratar cualquier retorno raro de un delegado como "falló esa feature".** Es lo que había, y convierte un bloqueo accionable en una línea de error en el resumen final.

**Consecuencias y aprendizaje.**

- **Un gate solo sirve si su decisión llega a donde se aplica.** Decidir en el hilo principal y ejecutar en un fork es el reparto correcto ([[D-045]]), pero abre una costura nueva: **lo decidido tiene que viajar en el prompt**, que es el único canal entre las dos mitades. Un gate contestado que no viaja es peor que no tenerlo — se vuelve a preguntar donde nadie puede contestar.
- **Una salida segura escrita en una sola rama no existe en las demás.** Reutilizar el discovery estaba bien resuelto en el Caso A; el Caso B llegaba al mismo artefacto sin esa opción. La pregunta que lo caza: *¿esta rama tiene las mismas salidas que su hermana?*

**Referencias.** `pipeline/spec/skills/wf-spec-features-first/SKILL.md` (Pasos 3, 4b y 5), `pipeline/spec/routing.md`, `conformance/casos-de-uso/cu-03-specs.md` (CU-3.u, CU-3.v), `conformance/ROADMAP.md` (fila de `wf-spec-features-first`).

---

## D-080 — `RETIRADO` era terminal para quien evoluciona un spec, no para quien lo regenera

- **Fecha:** 2026-09-15 · **Estado:** Adoptada (regla escrita + backstop determinista `SPEC-RETIRED-BLIND` con 6 tests; conducta **sin medir** — CU-3.t y CU-4.f nacen `⏱ sin pasada`). · **Relacionada:** [[D-074]] (la baja de una feature), [[D-078]] (`--unseal` la resucitaba), [[D-062]] (regenerar se pondera por el estado), [[D-061]] (`Estado: VALIDADO` como línea objetiva).

**Contexto.** [[D-078]] cerró la puerta lateral: los cuatro flujos que **modifican** un spec (delta, amend, gap-resolve, el apply de sync-from-prd) desellaban un `RETIRADO` a `BORRADOR` y lo devolvían vivo. Se arregló con `gate_spec_vigente` y su aprendizaje quedó escrito: *"un estado terminal hay que cerrarlo en las dos direcciones"*.

Faltaba una tercera. Los flujos que **regeneran** un spec —`wf-spec-fast-track`, `wf-spec-from-code generate` y el Paso 4b de `wf-spec-features-first`— no modifican: **sobreescriben**. Y los tres clasificaban el spec preexistente con el mismo sondeo binario:

```
grep -Eq '…Estado…VALIDADO' "$p" && echo SELLADO || echo DRAFT
```

`Estado:` tiene **tres** valores. Un spec `RETIRADO` no es `VALIDADO`, así que caía en `DRAFT` — la rama que se reescribe sin preguntar, o con un gate ligero que pregunta *"ya tienen un spec en borrador, ¿lo regenero?"* sobre una feature que el producto canceló. El resultado: se pierde la traza `Retirada: CR-XXX`, `sdd-features-index.py` la deriva otra vez a estado vivo, y **el único gate de la fase sin escotilla** —la baja, que [[D-074]] dejó deliberadamente sin `--allow-*`— queda evitado sin que nadie lo vea.

Y la ruta de llegada es la normal, no una rebuscada: el `_discovery.md` **no se regenera** (lo protege su propio bloqueo), así que sigue listando el `F-00X` de la feature retirada —cuyo ID además se conserva sin reutilizarse (`kb-traceability-rules` Regla 12)—, y cualquier pasada posterior de la generación por feature lo mete en el subset.

**Decisión.**

- **El campo `Estado:` se lee entero, con sus tres valores**, en los tres escritores. El sondeo binario se sustituye por una extracción del valor.
- **`RETIRADO` para el trabajo, y ningún flag lo cierra.** Los dos workers (`fast-track`, `from-code`) devuelven un veredicto operativo nuevo, `STOP_SPEC_RETIRADO`, sin escribir nada; el orquestador de features-first clasifica esas features como `RETIRADA`, **las deja fuera del fan-out y las nombra en el informe** con su traza. No se ofrece gate: la pregunta insinuaría una salida que no existe. La única vuelta sigue siendo la reactivación, que es una decisión de producto y devuelve el spec a `BORRADOR` ([[D-078]]).
- **Backstop determinista.** `sdd-structural-lint.py` gana el check **blocking `SPEC-RETIRED-BLIND`**: una `wf-spec-*` que sondea `Estado:` contra `VALIDADO` y no nombra `RETIRADO` en ninguna parte del fichero. No hay gate `PreToolUse` posible aquí —`gate_spec_vigente` resuelve el spec **desde los argumentos**, y estos flujos no lo reciben como argumento: reciben el PRD o un path de código y derivan el destino—, así que el backstop es estructural, sobre el texto de la skill.
- **Y el auditor deja de comparar contra difuntos**: `wf-spec-conflict` excluye los specs `RETIRADO` del conjunto y lo dice en su informe. Un choque contra una feature que no se va a implementar no es un conflicto; es ruido que puede acabar bloqueando a una viva.

**Alternativas descartadas.**

- **Extender `gate_spec_vigente` a los tres escritores.** No alcanza: el gate necesita el path del spec en los argumentos y estos flujos lo derivan de la capability y de la raíz de artefactos. Un gate que solo funciona a veces es peor que uno que no existe, porque se confía en él.
- **Tratar el `RETIRADO` como un `SELLADO` más** (confirmar y dejar regenerar con `--allow-overwrite-sealed-spec`). Convierte una decisión de producto en un override de escritura, y el flag diría que se descarta "trabajo de validación" cuando lo que se descarta es una **baja formalizada con su `CR`**.
- **Reactivar automáticamente al detectar que el discovery aún la lista.** El discovery es viejo por construcción; que siga nombrando la feature no es una señal de producto.

**Consecuencias y aprendizaje.**

- **El aprendizaje de [[D-078]] era correcto y se aplicó una vez menos de lo necesario.** *"¿Qué operaciones tocan este campo, y cuáles no saben que este estado existe?"* se respondió con las que lo **modifican**, y quedaron fuera las que lo **sobreescriben** — que ni siquiera leen el estado para decidir: lo leen para decidir **otra cosa** (si hay que confirmar antes de pisar).
- **Un valor nuevo en un enum no lo entienden los sitios que preguntan por un valor concreto.** El sondeo `== VALIDADO` no se rompe al añadir `RETIRADO`: sigue funcionando, y manda el caso nuevo a la rama por defecto. Por eso no lo destapa ninguna pasada — no falla, **acierta en la rama equivocada**.
- La pregunta que lo caza, y que el nuevo check automatiza: *¿quién parte este campo en dos ramas, y cuántos valores tiene de verdad?*

**Referencias.** `pipeline/spec/skills/wf-spec-fast-track/SKILL.md`, `pipeline/spec/skills/wf-spec-from-code/SKILL.md`, `pipeline/spec/skills/wf-spec-features-first/SKILL.md` (Paso 4b), `pipeline/spec/skills/wf-spec-conflict/SKILL.md` (Paso 2), `pipeline/spec/routing.md`, `scripts/sdd-structural-lint.py` (`SPEC-RETIRED-BLIND`), `tests/test_sdd_structural_lint.py`, `conformance/casos-de-uso/cu-03-specs.md` (CU-3.t), `conformance/casos-de-uso/cu-04-brownfield.md` (CU-4.f).

---

## D-079 — El brownfield tenía entrada al pipeline y no tenía forma de volver al producto

- **Fecha:** 2026-09-14 · **Estado:** Adoptada (regla escrita; conducta **sin medir** — CU-4.e nace `⏱ sin pasada`). · **Relacionada:** [[D-078]] (el mismo barrido), `kb-spec-characterization` (la evidencia por CA), `kb-product-change-governance` Regla 2 (`DEPRECATION` vs `PRIORITY_CHANGE`), [[D-074]] (los IDs de feature no se reutilizan).

**Contexto.** `wf-spec-from-code` es el onramp brownfield: sin PRD, el código es la fuente de verdad y el producto son specs de caracterización con `PRD origen: N/A`, `Evidencia base: commit <SHA>` y Feature IDs en un namespace propio, `F-C-00X`, deliberadamente aislado del `F-00X` de producto (`sdd-next-id.py` no los mezcla).

Lo que no existía es **la vuelta**. La secuencia natural de una adopción sobre producto vivo es: se documenta el legacy, y más tarde se escribe el PRD. En ese momento el discovery del PRD produce `F-00X` que solapan con los `F-C-00X` que ya están en disco, y no había ninguna pieza que dijera qué hacer: `kb-traceability-rules` no mencionaba `characterization` en ninguna línea, `wf-spec-sync-from-prd` opera sobre los `F-00X` del índice y nunca ve a los otros, y el README listaba el caso 2.b como entrada alternativa pero no como **estado del que se sale**. El brownfield entraba al pipeline y se quedaba fuera de la trazabilidad de producto para siempre.

**Decisión.** `kb-traceability-rules` gana la **Regla 13**, que cubre las dos mitades:

1. **La trazabilidad de un spec de caracterización mientras no hay PRD.** `PRD origen: N/A` y `status_sync: unknown` son **correctos**, no una carencia — y por eso no bloquean ningún sello (Regla 3). Su deriva no se mide contra un PRD sino contra el código: lo que caduca son los punteros `archivo:línea`, no la sincronía con producto. Un `derived_from_prd_hash` ausente **nunca** se rellena a mano para dejarlo verde.
2. **La adopción cuando el PRD aparece**, en cuatro casuísticas: el `F-00X` ya caracterizado **adopta** el spec existente como línea base (conserva sus CAs con `Evidencia` y su changelog, y pasa a declarar `PRD origen`); la diferencia entre lo que el código hace y lo que el PRD quiere es **evolución aparte**, no parte de la adopción; el `F-00X` sin código detrás es feature nueva; y el `F-C-00X` que nadie reclama **no se retira automáticamente** — que el PRD no lo contemple puede ser un olvido del PRD, y esa diferencia la decide producto.

**No se automatiza con un workflow, y es deliberado.** La correspondencia entre "lo que el sistema hace" y "lo que el producto dice querer" es un juicio humano capacidad por capacidad; un fork que lo resolviera solo produciría exactamente el artefacto con pinta de correcto que es el modo de fallo caro de esta fase. Lo que sí se hace es ponerlo en el enrutado (`pipeline/spec/routing.md`), para que el hilo principal no confunda esta petición con "crea las specs".

**Alternativas descartadas.**

- **Regenerar las features desde el PRD y olvidar los `F-C-00X`.** Tira la evidencia que costó levantar del código, y con ella los `[INFERIDO]` que alguien confirmó uno a uno. Es el atajo que parece limpio.
- **Dejar los dos juegos conviviendo.** Produce dos specs vivos para la misma capacidad — justo lo que `kb-conflict-expert` reporta como HU duplicada y scope overlap. El conflicto se detectaría, pero después de haber escrito el doble.
- **Reutilizar el `F-C-00X` como si fuera un `F-00X`.** Rompe el namespace que `sdd-next-id.py` mantiene separado a propósito, y hace que el índice cuente como features de producto capacidades que aún no lo son.

**Consecuencias y aprendizaje.**

- **Una entrada alternativa a un pipeline necesita su salida documentada, o es un callejón.** El onramp estaba completo hacia dentro —discovery con gate humano, specs con evidencia, `[INFERIDO]` bloqueando el plan— y el hueco estaba en el único sitio donde no se mira: qué pasa cuando el proyecto **deja de ser** el caso que justificó la entrada.
- **Un `[SOSPECHA_BUG]` sobrevive a la adopción.** Que aparezca un PRD no convierte en intencionado lo que el código hacía raro: o el PRD lo confirma, o pasa a ser defecto contra el CA adoptado. Es el detalle que se pierde si la adopción se hace regenerando.

**Referencias.** `pipeline/spec/skills/kb-traceability-rules/SKILL.md` (Regla 13), `pipeline/spec/routing.md`, `pipeline/spec/README.md` (caso 2.c), `scripts/sdd-next-id.py`, `conformance/casos-de-uso/cu-04-brownfield.md` (CU-4.e), `conformance/ROADMAP.md` (fila de `wf-spec-from-code`).

---

## D-078 — La retirada de una feature era reversible por efecto colateral: `--unseal` la resucitaba

- **Fecha:** 2026-09-14 · **Estado:** Adoptada (guarda en el script + gate preventivo, con tests; **capa determinista cubierta por CI, conductual sin medir** — CU-9.o y CU-7.s nacen `⏱ sin pasada`). · **Relacionada:** [[D-074]] (la retirada como estado terminal), [[D-061]] (el estado operativo del spec), [[D-073]] (`wf-spec-delta` al hilo principal), [[D-026]] (los overrides los arma el usuario), CU-3.s · CU-7.s · CU-9.o.

**Contexto.** [[D-074]] hizo de `RETIRADO` un estado terminal y lo cableó entero **aguas abajo**: `sdd-gate-check.py` deniega planificar, generar tasks y ejecutarlas resolviendo el `Spec origen` del plan y el `Plan origen` del tasks; `sdd-seal.py --seal` se niega a validar una feature dada de baja y, cuando el sellado falla, **no** la degrada —con el razonamiento escrito en el propio script: *"degradar lo resucitaría en silencio; deshacer una retirada es explícito (`--unretire`), nunca efecto colateral"*—; el índice y el estado de proyecto la muestran `RETIRADA`.

Lo que quedó abierto es **la evolución lateral dentro de la propia fase Spec**. Los cuatro flujos que modifican un spec —delta, amend, gap-resolve y el apply de sync-from-prd— cierran ejecutando `sdd-seal.py spec <path> --unseal`, porque lo que se validó ya no es lo que hay. Y esa rama del script movía el estado a `BORRADOR` **sin mirar de dónde venía**: `RETIRADO` está en el mismo enum, así que se pisaba igual. La línea `Retirada: CR-007` no se iba con él (solo `--unretire` la retira), de modo que el spec quedaba afirmando dos cosas contradictorias a la vez.

El encadenado completo, con una petición de lo más ordinaria —*"añade esto al spec de pagos"* sobre una feature retirada—: delta aplica → `--unseal` → el índice deja de verla `RETIRADA` porque compara contra `RETIRADO` → los tres gates se reabren → se puede planificar, trocear y ejecutar una capacidad que el producto canceló. Sin `CR`, sin gate, y sin que nadie se entere. **Ninguna de las cuatro skills comprobaba el estado antes de arrancar**, y el gate mecánico no las cubría: `GATES` solo tenía entradas aguas abajo.

**Decisión.** Dos capas, porque el fallo tenía dos.

1. **`RETIRADO` es terminal en las dos direcciones.** `--unseal` sobre un spec retirado no escribe nada y sale `2` con motivo accionable. Volver a `BORRADOR` es la dirección segura **desde `VALIDADO`**; desde `RETIRADO` no es un downgrade, es una **reactivación**. Se sale de `RETIRADO` por un solo sitio: `--unretire`, que es lo que ejecuta la reactivación con su gate delante.
2. **Gate preventivo `gate_spec_vigente`** para `wf-spec-delta`, `wf-spec-amend` y `wf-spec-gap-resolve`, para que ni siquiera arranquen. Mira **solo la vigencia**: un spec con `[INCOMPLETO]` o `[CRÍTICO]` abiertos es justo lo que estos flujos existen para arreglar, así que reusar `gate_spec_fiable` habría roto gap-resolve. `wf-spec-sync-from-prd` no entra en la tabla porque recibe el PRD, no el spec — su salvaguarda sigue siendo la prosa, que ya se salta las features con acción `retire`.

Y las tres skills documentan la precondición en su propio Paso 2, como backstop para cuando el hook no esté activo y, sobre todo, para dejar escrito **el motivo**. `wf-spec-validate` gana además su propia excepción: su rama de `exit 2` mandaba ejecutar `--unseal` ante **cualquier** `✗`, y `RETIRADO` es uno de ellos — el script ya se niega, pero informar de que "se ha reabierto la validación" de algo que no se reabrió es la mitad del fallo que sigue siendo de la skill.

**Alternativas descartadas.**

- **Que `--unseal` limpie también la traza `Retirada:`.** Arregla la contradicción del artefacto y **empeora** el fondo: convierte la resurrección silenciosa en una resurrección limpia y bien formateada.
- **Un `--allow-*` para forzarlo.** No hay nada que forzar: reactivar una feature ya tiene vía sancionada, con su gate. Un override aquí sería un segundo camino para la misma decisión, uno de ellos sin preguntar ([[D-026]]).
- **Cubrirlo solo con el gate, sin tocar el script.** El gate es un hook: no está activo en todas las instalaciones, y el `--unseal` lo ejecutan **subagentes** dentro de la skill, donde ningún `PreToolUse` de `Skill` los ve.
- **Cubrirlo solo con el script, sin gate.** Dejaría el flujo entero corriendo —delegación, edición del spec, changelog— para fallar en el último paso, con el spec ya modificado.

**Consecuencias y aprendizaje.**

- **Un estado terminal hay que cerrarlo en las dos direcciones, y la segunda es la que se olvida.** [[D-074]] razonó con cuidado sobre quién **consume** una feature retirada y no sobre quién la **escribe**. La pregunta que lo caza: *¿qué operaciones tocan este campo, y cuáles de ellas no saben que este estado existe?*
- **El razonamiento correcto estaba escrito veinte líneas más abajo, en el mismo fichero.** La rama del `--seal` fallido tenía el comentario exacto sobre la resurrección silenciosa; la rama del `--unseal`, justo encima, hacía precisamente eso. Un invariante escrito en el sitio donde te acordaste no protege el sitio donde no.
- **Un test que se llama `always` fija como contrato una vacuidad.** `test_unseal_always_downgrades` y `test_unseal_always_allowed` solo probaban el caso `VALIDADO`; el nombre prometía universalidad y nadie fue a comprobar el resto del enum. Renombrados a `_from_validado`, que es lo que miden.

**Referencias.** `scripts/sdd-seal.py` (rama `--unseal`), `scripts/sdd-gate-check.py` (`gate_spec_vigente`, `_retirado`), `tests/test_sdd_seal.py` (`RetireTest.test_unseal_does_not_undo_a_retirement`), `tests/test_sdd_gate_check.py` (`RetiredFeatureTest.test_lateral_evolution_denied` / `_ignores_open_gaps`), `pipeline/spec/skills/wf-spec-{delta,amend,gap-resolve,validate}/SKILL.md`, `conformance/casos-de-uso/cu-09-gates.md` (CU-9.o, nueva sección «Gate de spec vigente»), `cu-07-cambio-producto.md` (CU-7.s), `cu-03-specs.md` (CU-3.s), `conformance/ROADMAP.md` (filas de `wf-spec-retire`, `-delta`, `-amend`, `-gap-resolve`, `-validate`, `-conflict`, `-readiness`).

---

## D-077 — El informe decía «lista» de lo que el gate iba a denegar, y un CU lo daba por cubierto

- **Fecha:** 2026-09-14 · **Estado:** Adoptada (conformance escrita; conducta **sin medir** — los escenarios nacen `⏱ sin pasada`). · **Relacionada:** [[D-061]] (el sello del spec y el gate que lo exige), [[D-047]] (los auditores de conflicto se contradicen por diseño), [[D-031]] (el hilo principal no diagnostica leyendo), [[D-019]] (los comandos son internos), [[D-024]]/[[D-069]] (la propagación diferida que no se propaga), CU-3.e/f/o · CU-6.a · CU-7.l · CU-9.n · CU-13.b.

**Contexto.** Un repaso del enlazado de la fase Spec —agentes, workflows, KBs, scripts de enforcement y reglas eager— buscando qué promete una pieza que otra no cumple. La fase está bien cableada en lo mecánico: la retirada ([[D-074]]) y la enmienda están enteras de punta a punta, y `sdd-structural-lint.py` mecaniza los invariantes de arquitectura. El hueco está **en el eje del sello**, y lo abrió la propia [[D-061]].

[[D-061]] añadió `Estado: BORRADOR|VALIDADO` al spec y lo metió en `gate_spec_fiable`: pedir el plan de un spec sin validar se deniega. Lo que no tocó fue **el veredicto que el usuario lee antes de pedirlo**. `wf-spec-readiness`, la derivación de estado de `kb-decompose-expert` y `derive_state` de `sdd-features-index.py` calculan `LISTA` con los criterios pre-[[D-061]] —sin marcadores, sin conflictos `ALTA`, sin dependencias abiertas—, y **el sello no entra**. Como un spec nace en `BORRADOR` y `wf-spec-features-first` no valida en ningún paso, el recorrido normal de la fase termina con un informe que dice `LISTA` y un gate que deniega. Las *Referencias* de [[D-061]] no nombran ninguna de las tres piezas: es la propagación diferida que ella misma le reprochaba a [[D-024]], repetida dentro de su propio cambio.

**Y el catálogo de conformance no solo no lo cubría: lo daba por cubierto.** El FALLO de `CU-7.l` decía que un spec desellado que salga en borrador sin avisar es malo *"(el readiness lo bloqueará y el usuario no sabrá por qué)"*. El readiness **no lo bloquea**. Un CU que afirma un mecanismo inexistente es peor que un hueco: un hueco se ve al contar, una creencia falsa se lee como cobertura.

**Decisión.**

1. **El veredicto no puede prometer lo que el gate incumple.** `CU-3.o` gana el punto 4: un spec limpio en `BORRADOR` no sale del readiness con una afirmación de "se puede planificar". Lo que se mide es la **coherencia informe↔gate**, no un literal concreto — que se resuelva con otro estado, con el motivo en bloqueantes o con una nota es decisión de implementación.
2. **`CU-9.n`**, el gemelo que faltaba. `gate_spec_fiable` deniega por siete razones; CU-9 medía cinco y `RETIRADO` se mide desde CU-7. El sello se quedó sin escenario aunque su gemelo para el plan (`CU-9.c`) existía desde el principio.
3. **`CU-7.l` se corrige y se dice por qué** (Regla 9 punto 4 de `kb-sdd-conformance`: corrige el CU **y** registra la decisión; nunca relajes el criterio en silencio).
4. **`CU-3.e` gana la frontera fast-track → validate**, espejo de `CU-2.a` punto 2 en el PRD. Fast-track es donde el spec nace en borrador y era el único de los tres escritores que no lo decía al cerrar.
5. **`CU-13.b` gana la fila diagnóstica** (*"¿en qué estado están mis specs?"* → `sdd-spec-explorer`), espejo de la de `CU-13.a` para `prd-expert`, medida desde 2026-07-10. Aquí falta además el **portador**: `pipeline/spec/routing.md` no nombra la petición diagnóstica, así que la regla eager tampoco. El escenario nace esperando FALLO.

**Y una que se decide en negativo: el conflicto `ALTA` NO se convierte en gate.**

Un conflicto `ALTA` marca la feature `BLOQUEADA` en el readiness y **ningún gate lo lee**. La tentación es cerrar la asimetría metiéndolo en `gate_spec_fiable`. No se hace, por cuatro razones: la severidad la asigna un **juicio experto**, y sería el único gate del ecosistema que se fía del veredicto de un agente; los auditores del fan-out **se contradicen sobre el mismo par por diseño** ([[D-047]]), así que un `ALTA` minoritario bloquearía trabajo que el arbitraje ya resolvió, sin vía de cierre; la **ausencia** del informe no significa nada (existe `--skip-conflict`, y una feature sola no genera informe), de modo que exigirlo convierte un flag opcional en obligatorio; y sobre todo, **el riesgo real no es que se planifique, es que el usuario crea que no puede**. Lo que se arregla es la honestidad del veredicto (`CU-3.o` punto 5) y el aviso en el momento de planificar (`CU-6.a` punto 2: advierte y continúa, como ya hace con los `[INFORMATIVO]` y con el drift de fuentes).

**Alternativas descartadas.**

- **Quitar `BORRADOR` de `gate_spec_fiable`** para que informe y gate cuadren por abajo. Cuadrarían mintiendo los dos: [[D-061]] existe porque nada distinguía un spec validado de uno que no había mirado nadie.
- **Validar automáticamente al final de `wf-spec-features-first`.** Autor≠verificador ([[D-059]]) y, sobre todo, [[D-065]]: el sello registra **quién** aprueba, y eso exige preguntar.
- **Dejarlo en documentación sin escenario.** Es lo que ya estaba pasando: la asimetría llevaba escrita en el gate desde [[D-061]] y nadie la cruzó con el catálogo.

**Consecuencias y aprendizaje.**

- **Los huecos se ven comparando dos piezas que nadie lee juntas.** [[D-061]] lo dijo para las fases ("aparecieron al poner las tres columnas al lado") y aquí vale para **informe vs gate**: dentro de `wf-spec-readiness` todo es coherente consigo mismo, y dentro de `sdd-gate-check.py` también.
- **Un CU puede codificar una creencia falsa, y entonces es peor que un hueco.** `CU-7.l` afirmaba un bloqueo inexistente: al leerla, la asimetría parecía cubierta. Conviene mirar con lupa los Esperado que describen lo que hará **otra** pieza, porque nadie los verifica contra ella.
- **Estos cinco hallazgos no salieron de una pasada, salieron de revisión estática.** La Regla 9 punto 5 (*"congela la frase que falló"*) no aplica: no hay frase de usuario que congelar, hay que inventarla — y eso es lo que `CU-9.n` y la fila de `CU-13.b` tienen que aportar para ser ejecutables.

**Referencias.** `conformance/casos-de-uso/cu-03-specs.md` (CU-3.e punto 2, CU-3.f punto 3, CU-3.o puntos 4-5), `cu-06-entrega.md` (CU-6.a), `cu-07-cambio-producto.md` (CU-7.l), `cu-09-gates.md` (CU-9.n), `cu-13-enrutado-matriz.md` (CU-13.b), `conformance/ROADMAP.md` (filas de `wf-spec-readiness`, `wf-spec-fast-track`, `wf-spec-conflict`, `wf-spec-sync-from-prd`, `wf-prepare-plan`), `scripts/sdd-gate-check.py` (`gate_spec_fiable`), `scripts/sdd-features-index.py` (`derive_state`).

---

## D-076 — "Hallazgo bloqueante" gobernaba el sello del spec y no estaba definido en ninguna parte

- **Fecha:** 2026-09-14 · **Estado:** Adoptada (espejo de [[D-035]], que fijó lo mismo para el PRD). · **Relacionada:** [[D-035]] (el umbral del PRD y el titubeo que lo motivó), [[D-061]] (el spec gana estado operativo), [[D-065]] (quién captura y quién estampa el sello), [[D-063]] (el backstop mecánico de `sdd-seal.py spec --check`), CU-3.f/m, CU-2.f.

**Contexto.** `wf-spec-validate` bifurca el sellado en dos ramas —*"con hallazgos bloqueantes"* reabre y detiene, *"sin hallazgos bloqueantes"* comprueba el script y sella— y `kb-traceability-rules` ata el sello a la misma condición. La palabra aparece tres veces como bisagra y **no está definida en ninguna kb**: `kb-spec-expert` define veredictos por check (`Pureza: APROBADO/CONTAMINADO`, `Testabilidad: APROBADO/REQUIERE_MEJORA`) y nunca los mapea al umbral. Si la testabilidad sale `REQUIERE_MEJORA` porque un CA está mal redactado pero es perfectamente ejecutable, que eso selle o no lo decide el auditor de esa pasada.

Es la **misma indefinición que [[D-035]] midió en el PRD**, con la misma forma: la etiqueta gobierna el sello, parte del insumo es cualitativo, y el gate mecánico es ortogonal y no cubre este hueco. Allí produjo dos etiquetas distintas para el mismo estado limpio en corridas distintas. Aquí no se ha medido todavía porque la única pasada registrada (CU-3.f, 2026-08-27) **salió bien** — el auditor distinguió lo bloqueante de lo no bloqueante y dejó una ambigüedad real fuera del veredicto. Pero eso fue juicio de esa corrida: una garantía que depende de que el agente acierte no es una garantía, que es literalmente el aprendizaje de [[D-040]].

**Decisión.** Fijar el umbral en `kb-spec-expert`, como **Paso 4 de «Cómo validar un Spec»** (la SSoT que cargan los tres agentes de la fase), y **restatearlo** en `wf-spec-validate` —prompt del auditor y paso del sello— más su plantilla de informe, que pasa a separar *Hallazgos BLOQUEANTES (degradan)* de *Notas NO bloqueantes (no cambian el veredicto)*.

Bloquean **tres cosas y solo tres**: (1) falta un elemento obligatorio —los 8 en `standard`, el núcleo de 4 en `ligero`, o una sección omitida **sin** su marca `N/A — modo ligero`, que es omisión disfrazada—; (2) `Pureza: CONTAMINADO`, es decir una fila de `prohibited_items.md`; (3) un CA que **no se puede verificar tal como está escrito**. El corte del tercero es **ejecutabilidad, no elegancia**: si alguien puede montar la prueba con lo que hay, no bloquea.

**No degradan, y esa mitad es la que de verdad faltaba**: sugerencias de redacción, notas *borderline* documentadas como aceptables, y **huecos que son materia de Plan** —que el spec no diga con qué se implementa es exactamente lo que debe pasar—. Se añade una cuarta, que en el PRD no hacía falta: **lo que ya dictamina `sdd-seal.py spec --check`** (HUs `[INCOMPLETO]`, gaps `[CRÍTICO]`, CAs `[INFERIDO]`, asunciones sin rastro, deriva del PRD) **no lo cuenta el auditor como hallazgo suyo**. Duplicarlo no añade rigor: compite con el veredicto bueno y deja al workflow eligiendo entre dos fuentes.

**No se numera la regla.** `kb-spec-expert` no usa numeración `Regla N` —a diferencia de `kb-prd-expert`, donde el umbral es la Regla 14— y el check `CITED-RULE-MISSING` del linter revienta ante una cita `Regla N de kb-spec-expert` que no exista. Se referencia por nombre de sección.

**Alternativas descartadas.**
- *Dejarlo al juicio del auditor* → es la fuente exacta del titubeo que D-035 documentó, y aquí el veredicto gobierna el sello igual que allí.
- *Mecanizarlo con un script* → parte del insumo (contaminación dura, CA verificable) es cualitativo. El gate mecánico duro ya existe (`sdd-seal.py spec --check`) y es **ortogonal**: cada uno ve lo que el otro no. La palanca correcta es afilar la kb.
- *Numerarlo como `Regla N` para parecerse a `kb-prd-expert`* → obligaría a numerar retroactivamente toda la kb, y la simetría cosmética no vale el riesgo de citas rotas.
- *Escribirlo solo en `wf-spec-validate`* → deja fuera al auditor cuando trabaja desde otro workflow, y repite el patrón de norma que vive donde no la lee quien decide.

**Consecuencias / aprendizaje.** **Una pasada que sale bien no prueba que el contrato exista.** CU-3.f PASS quedó registrado con el elogio *"distinguió bien lo no bloqueante de lo bloqueante"* — y esa frase, leída un mes después, es justo la señal de alarma: lo que se estaba celebrando no lo garantizaba ningún documento. Cuando un informe de conformance elogia un juicio en vez de constatar el cumplimiento de una regla citable, ahí falta la regla.

**Referencias.** `sdd/pipeline/spec/skills/kb-spec-expert/SKILL.md` (Paso 4 + plantilla de output), `sdd/pipeline/spec/skills/wf-spec-validate/SKILL.md` (Pasos 3 y 5), `sdd/pipeline/spec/skills/wf-spec-validate/references/output_template.md`, `sdd/pipeline/spec/skills/kb-traceability-rules/SKILL.md` (tabla de sellos), `sdd/tests/test_install_sh.py` (`KbSpecExpertContentTest`), `sdd/conformance/casos-de-uso/cu-03-specs.md` (CU-3.f punto 1, CU-3.m punto 3), `sdd/conformance/ROADMAP.md`, `sdd/CHANGELOG.md`.

---

## D-075 — El último orquestador que corría en un fork, y el linter que no podía verlo

- **Fecha:** 2026-09-14 · **Estado:** Adoptada (candidato que [[D-040]] dejó escrito y no ejecutó). · **Relacionada:** [[D-040]] (la mitad que sí se pudo cerrar entonces), [[D-045]]/[[D-064]]/[[D-072]]/[[D-073]] (el gate vive donde puede presentarse), [[D-044]] (el delegado ejecuta, no re-despacha), [[D-060]] (el orquestador no redacta artefactos), [[D-061]] (aplicar reabre el sello), [[D-019]] (los comandos son internos), CU-7.f–k/**r**.

**Contexto.** El repaso de la fase Spec contra las reglas que el ecosistema ya había fijado en PRD dejó ver que `wf-prd-change-cascade` seguía siendo lo que todas las demás dejaron de ser. Era `context: fork`, encadenaba **seis** workflows con el `Skill` tool y declaraba cuatro *"checkpoints humanos"* que ningún fork puede presentar. [[D-040]] ya lo había diagnosticado —*"era un fork invocando a otro fork, sin nadie a quien preguntar"*— pero solo pudo desmentir el primero, con `--defer-decisions`; sacar la cascada entera del fork quedó anotado allí mismo como **candidato aparte**, con su motivo: *"invoca 6 workflows y obligaría a re-probar CU-7.f–k enteras"*. Los otros tres checkpoints se quedaron escritos donde no eran ejecutables, un año de versiones.

Tres agravantes, y el tercero es el que importa:

- **El informe que consolidaba lo ajeno.** Su Paso 9 escribía `_cascade_report.md` juntando lo que habían producido sus delegados, declarándose "orquestador puro" dos párrafos antes. Es el caso literal de [[D-060]], cuyo daño medido fue adjudicar un hallazgo al auditor equivocado al transcribir lo que no había escrito.
- **Los specs salían desellados y nadie lo decía.** El apply de sync reabre la validación ([[D-061]]); el Paso 3 avisaba de la reapertura del sello del PRD y ningún paso avisaba de la de los specs. El readiness del paso siguiente los reportaba bloqueados sin que el usuario supiera por qué.
- **El linter no lo veía, y creíamos que sí.** `FORK-ORCHESTRATOR` caza `context: fork` + delegación **por la tool `Agent`**. La cascada orquestaba con el `Skill` tool y **no mencionaba `Agent` ni una vez**: cero hallazgos sobre el fichero. El validador estructural existe justo para que un defecto conocido no reaparezca en silencio, y este llevaba dentro desde el día que se escribió.

**Decisión.** Sacar la cascada al **hilo principal**, con el modelo ya rodado cinco veces ([[D-045]], [[D-065]], [[D-068]], [[D-072]], [[D-073]]): fuera `context: fork`, `allowed-tools: [Bash, Agent, AskUserQuestion, Skill]`, y los cuatro gates presentados con `AskUserQuestion` en el momento. Los cinco workers se delegan por la tool `Agent` con `run_in_background: false` y la fórmula canónica —*"lee el SKILL.md y ejecuta sus pasos TÚ MISMO"*— para no forkear un clon ([[D-044]]).

**`wf-prd-change` se sigue invocando con el `Skill` tool, y eso no es una excepción a [[D-044]]:** corre en el hilo principal igual que la cascada, así que sus instrucciones entran en **la misma conversación** y su gate se presenta de verdad. No hay fork, no hay clon, no hay asincronía. Por eso **`--defer-decisions` se retira**: su único consumidor era la cascada-fork, y un modo que nadie alcanza no es una capacidad — es una promesa, el patrón que este repo ya se cobró dos veces en v0.108.

**Y el Paso 9 deja de escribir.** El resumen por fase se presenta en la conversación, como `wf-spec-validate` hace con el informe del auditor. Lo que hay que conservar ya está escrito, cada cosa por quien la hizo.

**El backstop es un check nuevo: `FORK-SKILL-DISPATCH`** (blocking), que caza `context: fork` con `Skill` en `allowed-tools` o con la orden de invocar con el `Skill` tool en el cuerpo. Dos señales de alta precisión: al escribirlo, **ninguna otra skill del ecosistema declaraba `Skill`**, y ningún fork lo nombraba salvo para prohibirlo en un prompt de delegación.

**Alternativas descartadas.**
- *Dejarlo como estaba, dado que `--defer-decisions` tapaba el checkpoint 1* → tapaba uno de cuatro. Los otros tres seguían siendo texto que describe una parada que no ocurre, que es peor que no tenerla: parece que hay un humano mirando.
- *Que la cascada deje de invocar `wf-prd-change` y pase a ser precondición* → ya descartada en [[D-040]] por la misma razón: rompe la promesa de "propaga todo en un comando", que es su razón de existir.
- *Mantener el `Skill` tool para los cinco workers ahora que corre en main* → funcionaría para los gates, pero no paraleliza ni devuelve handle síncrono, y sobre una sub-skill con `agent:` forkea un subagente encima. La tool `Agent` es el mecanismo nombrado ([[D-043]]).
- *Conservar `_cascade_report.md` escrito por un delegado* → nadie es su autor natural: ningún agente ejecutó todas las fases. Un informe cuyo autor habría que inventar es la señal de que no debe existir.
- *Ampliar `FORK-ORCHESTRATOR` en vez de crear un check* → son señales distintas (tool `Agent` vs `Skill`) con mensajes de arreglo distintos; fundirlas habría dado un finding que no dice qué cambiar.

**Consecuencias / aprendizaje.** Dos, y las dos sobre el instrumento. (a) **Una alternativa descartada "por coste de re-probar" es deuda con fecha de vencimiento, no una decisión.** D-040 la escribió honestamente —"queda como candidato aparte"— y el coste que la frenó (re-probar CU-7.f–k) hubo que pagarlo igual, con año y medio de artefactos generados encima. (b) **Un check de lint define su cobertura por la señal que mira, no por el defecto que nombra.** `FORK-ORCHESTRATOR` se llama "orchestrator" y solo veía una de las dos formas de orquestar; el fichero más obviamente culpable del ecosistema pasaba limpio, y la limpieza se leía como conformidad. Al añadir un check, preguntar **de cuántas maneras se escribe** lo que se quiere cazar.

**Referencias.** `sdd/pipeline/prd/skills/wf-prd-change-cascade/SKILL.md` (reescrita), `sdd/pipeline/prd/skills/wf-prd-change/SKILL.md` (retirada del modo sin gate), `sdd/scripts/sdd-structural-lint.py` (`FORK-SKILL-DISPATCH`), `sdd/tests/test_sdd_structural_lint.py` (4 casos), `sdd/tests/test_install_sh.py` (`test_prd_change_cascade_runs_in_main_and_delegates`), `sdd/conformance/casos-de-uso/cu-07-cambio-producto.md` (CU-7.f/i/j/k/l/n reescritos, **CU-7.r** nueva), `sdd/conformance/ROADMAP.md`, `sdd/docs/guias/producto.md`, `sdd/docs/entender/funcional.md`, `sdd/CHANGELOG.md`.

---

## D-074 — El pipeline no sabía terminar una feature: la retirada existía como etiqueta y no como estado

- **Fecha:** 2026-09-14 · **Estado:** Adoptada (sin medir en conducta: `wf-spec-retire` nace `PENDIENTE` en el instrumento). · **Relacionada:** [[D-061]]/[[D-065]] (`Estado:` lo escribe solo el sellador), [[D-069]] (enumeraciones que duplican una fuente de verdad), [[D-046]] (el artefacto parcial con apariencia de completo), [[D-026]] (el override es para lo que no puede preguntar), [[D-045]]/[[D-073]] (el gate vive donde puede presentarse), [[D-059]] (autor≠verificador), Regla 12 de `kb-traceability-rules`.

**Contexto.** Repasando la fase Spec agente por agente apareció una casuística sin cubrir: **el PRD deja de contemplar una capacidad ya especificada**. El ecosistema sabía *nombrarla* y no sabía hacer nada con ella.

`kb-product-change-governance` Regla 2 definía `DEPRECATION` —*"una capacidad deja de ser vigente"*— y `wf-prd-change` la clasificaba en su gate. Ahí se acababa: `grep DEPRECATION` daba **tres sitios funcionales** —la KB que la define, el workflow que la clasifica y un nodo de diagrama— y **cero consumidores**. Peor: la misma Regla 2 metía *"añade/**elimina** capacidad"* dentro de `SCOPE_CHANGE`, y **la cadena de precedencia no incluía ni `DEPRECATION` ni `PRIORITY_CHANGE`**, así que un cambio que retiraba algo no tenía siquiera clasificación estable.

Aguas abajo no había nada, y lo que parecía la ruta genérica tampoco lo era: `sdd-sync-check.py --mark` **nunca escribe `stale`** (solo degrada a `needs_review`), y las acciones de `wf-spec-sync-from-prd` son `delta | manual_review | rediscover` — ninguna es "darla de baja". El resultado medido sobre un fixture: un spec cuya capacidad ya no existe **está limpio** —nadie lo ha tocado—, así que `derive_state()` lo daba **`LISTA`**, `wf-prepare-plan` pasaba el gate y el estado del proyecto lo ponía en «Siguiente foco» pidiendo que se planificara.

**Decisión.** La baja es un **estado terminal del spec**, no un marcador ni una anotación del índice:

```
> Estado: RETIRADO
> Retirada: CR-007 — <razón> (<YYYY-MM-DD>)
```

- **Vive en la cabecera del spec** porque `_features.md` es **función pura** de (discovery, specs, readiness) y se reescribe entera: un estado anotado ahí se pierde en la siguiente regeneración. El spec es lo único persistente que el índice lee.
- **Lo escribe solo `sdd-seal.py spec … --retire --change CR-XXX`**, que es ya el único escritor de `Estado:` ([[D-061]]/[[D-065]]). No exige las condiciones de sellado —se retira igual un spec roto que uno sano— pero **sí exige la traza**: retirar sin `CR-XXX` es cancelar producto sin registro.
- **La decide una persona**, en `wf-spec-retire`, que corre en el hilo principal con la misma forma que `wf-spec-validate`: main pregunta, `sdd-spec-auditor` diagnostica el impacto (qué shared models quedan huérfanos, quién la declara dependencia, qué artefactos ya existen) y el script estampa. **Sin flag de override**: los `--allow-*` existen para lo que no puede preguntar ([[D-026]]), y este workflow puede — el gate **es** el mecanismo.
- **Ningún fork retira nada.** `wf-prd-sync-impact` lo señala en su columna de acción, `wf-spec-sync-from-prd` gana la cuarta acción `retire` y **se salta esas features reportándolas**, y el cascade las manda siempre al conjunto STOP.
- **El bloqueo es real, no documental**: el hook `sdd-gate-check.py` deniega planificar, generar tasks y ejecutarlas, resolviendo el `Spec origen` del plan y el `Plan origen` del tasks.

Y la Regla 2 deja de solaparse: `SCOPE_CHANGE` **añade** o mueve entre MVP y fase futura —**mover a fase futura no retira**, la capacidad sigue comprometida—; `DEPRECATION` es salir del producto, y encabeza la cadena `DEPRECATION > SCOPE_CHANGE > BEHAVIOR_CHANGE > PRIORITY_CHANGE > CLARIFICATION` por ser la única que **termina** algo ya derivado.

**Alternativas descartadas.**
- *Un marcador `[RETIRADO]` en el cuerpo, como `[INCOMPLETO]`* → un marcador de `kb-gap-conventions` señala **algo que falta por resolver** en un artefacto vigente. Una feature de baja no tiene nada que resolver. Además habría entrado en los conteos de los selladores y bloqueado por el motivo equivocado.
- *Un modo `retire` dentro de `wf-spec-delta`* → delta ya corre en main y ya es dueño de los tombstones de HU/CA, pero su `description` pasaría a prometer dos acciones distintas, que es justo lo que prohíbe `kb-sdd-creation-guide`. Retirar no es evolucionar: una conserva el spec vivo, la otra lo termina.
- *Un quinto estado de sincronización* (junto a `in_sync`/`needs_review`/`stale`/`unknown`) → confunde dos ejes. El sync mide **alineación de contenido** con el PRD; la baja es **vigencia del producto**. La Regla 2 de `kb-traceability-rules` sigue cerrada en cuatro.
- *Cubrir también la feature sin spec* (`PENDIENTE_GENERACIÓN`) → no hay cabecera que estampar; vive solo en el discovery, que no es determinista. Anotado, no hecho.

**Consecuencias / aprendizaje.** **Una etiqueta sin consumidor no es una capacidad: es una promesa.** `DEPRECATION` llevaba meses en la KB, se clasificaba correctamente, el usuario la confirmaba en un gate — y no pasaba nada. Nadie lo notó porque el fallo no es ruidoso: el pipeline sigue proponiendo construir lo que se acaba de cancelar, y desde abajo esa feature **no se distingue de una lista para empezar**. El modo de fallo de [[D-046]] otra vez: apariencia de correcto.

Dos cosas más que salieron al implementarlo, las dos del mismo tipo —**una transición que deshace lo que no debe**—:

- El sellado fallido degrada a `BORRADOR` por diseño; sobre un spec retirado eso lo **resucitaba en silencio**. Deshacer una baja tiene que ser explícito (`--unretire`), nunca efecto colateral de otra operación.
- Y `--unretire` dejaba la línea `Retirada:` colgando: una traza que afirma una baja que ya no existe, y la leen tanto el índice como una persona. La traza se va con el estado.

**Y el colateral, que resultó mayor de lo diagnosticado.** `CA_DEF_RE`/`CA_HU_RE` casaban `### CA-003 [ELIMINADO en v1.4: razón]` como un CA vigente. Se buscaba un solo síntoma —el plan tenía que "cubrir" un CA eliminado— y había dos: el spec **tampoco se podía sellar**, porque a un tombstone se le exigía declarar HU padre. O sea: **aplicar la Regla 12, que este mismo ecosistema sanciona como la forma correcta de eliminar, dejaba el spec y su plan insellables**. Una regla y su verificador escritos por separado, sin nadie que los enfrentara.

**Pendiente de medir.** `wf-spec-retire` nace **sin pasada de conformance**: la fila entra `PENDIENTE` y los escenarios de `DEPRECATION` en CU-7 están escritos pero no ejercitados. Además el bloqueo aguas abajo **no se puede medir sobre el proyecto de CU-7**, que arranca sin plan ni tasks: necesita el de CU-6.

---

## D-073 — El último fork que decidía por el usuario: `wf-spec-delta` al hilo principal, con la ambigüedad marcada en vez de resuelta

- **Fecha:** 2026-09-14 · **Estado:** Adoptada (pendiente de medir en CU-3.h/CU-3.p). · **Relacionada:** [[D-040]] (el precedente en PRD, cuya segunda mitad faltaba), [[D-045]]/[[D-002]] (el gate vive donde puede presentarse), [[D-065]]/[[D-068]]/[[D-072]] (mismo movimiento en Spec y Design), [[D-026]] (el override lo arma el usuario), [[D-042]] (el recuento sale del script), [[D-063]] (sin humano no se decide, se marca), ROADMAP 13.6.

**Contexto.** Con `wf-spec-amend` y `wf-spec-validate` en main ([[D-065]]/[[D-068]]) y las cuatro conversaciones de Design movidas ([[D-072]]), `wf-spec-delta` quedaba como **el único workflow del ecosistema que sostenía decisiones humanas desde un `context: fork`**. El ítem 13.6 lo tenía anotado con una razón: es el `wf-prd-change` de la fase Spec, y [[D-040]] movió aquel a main porque *"un cambio de producto exige decisiones que solo el humano puede tomar —cómo se clasifica y, cuando la petición admite varias lecturas de alcance, cuál es"*.

Al abrirlo aparecieron **tres** decisiones, no la que estaba anotada:

1. **Delta vs cambio de producto.** El Paso 7A decía *"si el supuesto nuevo requisito redefine el alcance del MVP, una exclusión del PRD o una regla transversal, detén el delta y remite"*. La parada existía; **la clasificación la hacía el fork solo**. Equivocarse hacia "esto es un delta" hornea en el spec un cambio de alcance que nadie formalizó — y no deja rastro, porque el delta se aplica limpiamente.
2. **La ambigüedad del requisito nuevo.** Aquí faltaba literalmente la segunda mitad de [[D-040]]: *sin humano, la ambigüedad se marca en vez de decidirse*. El Paso 5A clasificaba HUs añadidas/modificadas/eliminadas leyendo el documento de cambios; si ese documento admitía dos lecturas funcionales, **el escritor elegía una** y el informe salía sin rastro de que hubo una bifurcación.
3. **Aplicar con gaps `[CRÍTICO]` sin responder** — el hallazgo que no estaba previsto. Los Pasos 2.3 y 4B decían *"informa al usuario qué HUs se marcarán `[INCOMPLETO]`"* y **`Continúa.`**, dos veces y en negrita. Esa misma situación **es un gate** en `wf-spec-features-first` (se detiene salvo `--allow-open-critical-gaps`). Aquí se resolvía informando y siguiendo, que es decidir por el usuario sin decírselo — y el coste se cobra tarde y lejos: las HUs `[INCOMPLETO]` bloquean `wf-prepare-plan` dos fases después.

**Decisión.** `wf-spec-delta` pasa al hilo principal (fuera `context: fork` y `agent:`, `allowed-tools: [Bash, Agent, AskUserQuestion]`), con el reparto ya establecido: main sostiene los tres gates y **delega dos veces** en `sdd-spec-writer` con `run_in_background: false` — el análisis (que **escribe** el `_delta_analysis.md`) y la integración (que escribe el spec, lo des-sella, versiona, encadena el changelog y regenera el índice). Main no lee el spec ni el informe ([[D-031]]) y no escribe ningún artefacto ([[D-060]]): comprueba con `grep`/`--check` que el resultado está y, si no, lo reporta en vez de arreglarlo.

Lo que cambia de fondo, más allá de dónde corre:

- El delegado **clasifica y devuelve un veredicto** (`DELTA_PURO` / `POSIBLE_CAMBIO_DE_PRODUCTO` / `AMBIGUO`), pero **no decide**: en `AMBIGUO` enumera las lecturas con lo que implica cada una.
- El gate de ambigüedad tiene una salida que antes no existía: **"no lo decido ahora"**, que no elige — manda registrar un gap `[D-XXX]` `[CRÍTICO]` con las lecturas como opciones y `_(pendiente)_` como respuesta. Es [[D-063]] aplicado a la evolución del spec: *si no puedes preguntar, no puedes decidir*; ahora **sí** se puede preguntar, y aun así la no-respuesta se marca en vez de resolverse.
- El recuento de críticos pendientes lo da `sdd-analysis-gaps.py --check --json` ([[D-042]]): el orquestador no abre el informe para contarlos.
- `wf-spec-sync-from-prd`, que es un fork y delegaba su escritura en *"el flujo de `wf-spec-delta apply`"*, pasa a **citar el contrato de integración** en vez de al workflow: es `sdd-spec-writer`, o sea el mismo agente al que delta delega esa parte, así que ejecuta el contrato directamente ([[D-070]]). Invocar el workflow ahora sería invocar un orquestador de main desde un fork.

**Alternativas descartadas.**
- *Dejarlo en fork y añadir solo la cláusula de marcar la ambigüedad* → arregla la decisión (2) y deja (1) y (3) igual. La clasificación seguiría siendo de nadie, y "informa y continúa" seguiría siendo una decisión tomada por el workflow.
- *Un `--allow-*` para cada uno de los tres* → convierte gates en flags que el usuario tiene que conocer de antemano. [[D-026]] es explícito: el override existe para **registrar una elección ya hecha**, no para sustituir la pregunta. Solo (3) lo lleva, porque `wf-spec-features-first` ya lo tenía y la simetría importa.
- *Medir primero y mover después* (la opción que este mismo ROADMAP recomendaba) → se descarta por lo que apareció al leerlo: los tres huecos **no producen fallo visible**, así que una pasada los habría dado por PASS. Medir un defecto que no se ve no informa nada.

**Consecuencias / aprendizaje.** **El coste de un gate ausente se paga donde no se ve.** Los tres huecos comparten forma: el workflow decide, informa de lo que decidió, y el artefacto sale correcto. El que aplica con críticos abiertos ni siquiera miente — avisa —, pero el aviso va al informe de un turno y el bloqueo aparece dos fases después, en `wf-prepare-plan`, cuando ya nadie recuerda que hubo una elección. Un gate no es una cortesía: es el único momento en que la decisión y su coste están juntos delante del usuario.

Y, cerrando 13.6: **la anotación se quedó corta**. Decía "no heredó [[D-040]]" y apuntaba a una decisión; eran tres. Al heredar una norma hay que leer al destinatario entero, no solo la parte que el precedente ilumina — la misma lección que [[D-063]] ya había dejado escrita.

**Pendiente de medir.** CU-3.h y CU-3.p **cambian de forma**: el `AMBIGUO` que antes se resolvía solo ahora se presenta, y "no lo decido ahora" tiene que dejar un gap marcado. Se mide en las pasadas de CU-3. **Los escenarios se reescribieron en v0.114.1**, no el mismo día que esta decisión: 0.107.0 fue la única versión de la tanda 0.107→0.114 sin barrido de conformance, así que durante siete versiones el banco midió el fork que esta decisión había retirado —y CU-3.p llegó a **penalizar como desviación** una de las dos salidas que el gate nuevo sanciona. El aprendizaje del propio D-073 aplicado al instrumento: **el coste de un gate ausente se paga donde no se ve**, y el de un barrido ausente también.

**Referencias.** `sdd/pipeline/spec/skills/wf-spec-delta/SKILL.md`, `sdd/pipeline/spec/skills/wf-spec-sync-from-prd/SKILL.md`, `sdd/conformance/ROADMAP.md`, `sdd/docs/ROADMAP.md` (13.6), `sdd/CHANGELOG.md`.

---

## D-072 — Cuatro conversaciones de Design vivían dentro de forks; sin turno, el riesgo no es pararse, es rellenar

- **Fecha:** 2026-09-10 · **Estado:** Adoptada (regla ampliada + cuatro workflows movidos; conducta pendiente de medir). · **Relacionada:** [[D-002]] (fork ⊥ preguntar), [[D-045]] (el gate vive donde puede presentarse), [[D-064]] (la forma parar-y-reportar), [[D-065]]/[[D-068]] (el mismo movimiento en Spec), [[D-070]] (misma lectura), [[D-026]] (el override lo arma el usuario), [[D-069]] (la enumeración de skills de main que derivó seis veces).

**Contexto.** El residuo anotado en 13.11 —prosa vieja en 15 workflows— resultó tapar algo mayor: **la fase Design tenía cuatro workflows que conversan con el usuario escritos como `context: fork`**, donde no hay turno en el que preguntar.

| Workflow | Lo que le pide al usuario |
|---|---|
| `wf-design-intake` | El **árbol de decisión del brief**, "pregunta a pregunta" en `guided`; en `hybrid`, confirmar seis variables propuestas |
| `wf-design-moodboard` | **Siete preguntas abiertas** sobre cómo debe sentirse el producto |
| `wf-design-discover` | Curar la lista de apps de referencia — *"iterar hasta que el usuario confirme"* |
| `wf-design-variant` | La **hipótesis** del A/B, en qué difiere cada variante, y sus resultados |

Y siete gates de confirmación dictados en prosa dentro de workers (`wf-design-branch` ×3, `wf-design-export`, `wf-design-delta`, `wf-design-extract`, más el `wf-spec-from-code` cerrado en [[D-071]]).

**Lo que hace distinto a este bloque.** En [[D-062]]/[[D-064]] el daño de un gate no presentable era **quedarse a medias**: la skill paraba y el usuario relanzaba. Aquí no. Estos cuatro no piden permiso: piden **material que solo existe en la cabeza del usuario** —la vibe del producto, la hipótesis que quiere validar, qué referencias le sirven—. Un fork sin turno que necesita ese material y no puede pedirlo tiene una salida obvia y silenciosa: **derivarlo del spec**. Y un moodboard fabricado tiene exactamente la misma pinta que uno real; la hipótesis inventada de un A/B también. El artefacto sale, parece correcto, y la dirección visual del producto la decidió nadie.

**Decisión.** Los cuatro **pasan al hilo principal** (fuera `context: fork` y `agent:`, `allowed-tools: [Bash, Agent, AskUserQuestion]`), con el reparto que ya usan `wf-spec-validate` y `wf-spec-amend`: main sostiene las preguntas, **delega el trabajo experto** al arquitecto de la fase con `run_in_background: false`, y **el agente escribe su artefacto** ([[D-059]]/[[D-060]]) — main comprueba con `test -f` que está, y si falta lo reporta en vez de escribirlo él. `wf-design-intake` queda en tres tiempos: **6A** el experto propone contra sus KBs, **6B** el usuario decide lo suyo, **6C** el experto redacta con las respuestas literales; el modo `auto` se salta el 6B y **marca en el artefacto que nadie lo validó**.

Los siete gates de los workers adoptan la forma de [[D-064]]: veredicto `STOP_*` con lo que se pierde nombrado, y override `--allow-*` que arma el usuario (`--allow-breaking-merge`, `--allow-discard-branch`). Dos se resuelven **quitando la pregunta**: el "¿descarto el branch tras el merge?" pasa a ser una acción explícita propia, y el formato de export aplica la recomendación y la justifica (exportar deriva de un `DESIGN.md` que no se toca; repetirlo cuesta un comando).

**El detector, otra vez, vigilaba frases.** `FORK-INTERVIEW` reportaba **cero** sobre un árbol con una entrevista de siete preguntas, y `FORK-CONFIRM-GATE` no veía *"pedir confirmacion"* (conocía la forma conjugada, no la infinitiva), *"pide al usuario que confirme"*, ni el sufijo de pregunta cerrada `(y/n)`. Ampliadas ambas con las formas **observadas**, no imaginadas. Delta: **4 blocking + 2 warning → 0**.

**Alternativas descartadas.**
- *Degradar las entrevistas a `--mode auto` y quitar el modo interactivo* → es tirar el producto para arreglar la arquitectura: el moodboard **es** la entrevista, y el brief `guided` es el que ancla la dirección visual. `auto` ya existe para quien lo quiera, y ahora dice en el artefacto que nadie validó nada.
- *Dejarlas en fork y que paren pidiendo los datos* → funciona para un permiso, no para una conversación de siete preguntas: cada respuesta obligaría a relanzar el workflow entero, perdiendo lo ya recogido. Es el relanzado que [[D-045]] midió, multiplicado por siete.
- *Un solo `AskUserQuestion` con las siete* → las preguntas del moodboard son **abiertas a propósito** ("si esto fuera un espacio físico, ¿cómo sería?"); meterlas en menús de opciones cambia el material que se recoge. Van en conversación, y `AskUserQuestion` queda para las dos que sí son cerradas.

**Consecuencias / aprendizaje.** Dos. (a) **La pregunta que un fork no puede hacer no siempre es un permiso.** Cuando lo que falta es *información que solo el usuario tiene*, el fallo no es un bloqueo visible sino una **fabricación plausible**, y por eso ninguna pasada de conformance lo habría destapado: el artefacto se genera y se ve bien. El criterio para decidir dónde vive una skill deja de ser "¿tiene gates?" y pasa a ser "¿necesita algo que solo el usuario sabe?". (b) La lista de skills que corren en main que vivía en `pipeline/orchestration.md` **se quedó vieja seis veces en dos días**; se sustituye por el criterio derivable —sin `context: fork`, con `AskUserQuestion` en `allowed-tools`— que es lo único que no envejece ([[D-069]]).

**Pendiente de medir.** Que las cuatro conversaciones ocurran de verdad en main —y que el artefacto de `auto` declare que nadie lo validó— se comprueba en la primera pasada de conformance de Design, que esta fase todavía no tiene.

**Referencias.** `sdd/pipeline/design/skills/wf-design-{intake,moodboard,discover,variant,branch,export,delta,extract}/SKILL.md`, `sdd/pipeline/design/routing.md`, `sdd/pipeline/orchestration.md`, `sdd/scripts/sdd-structural-lint.py`, `sdd/tests/test_sdd_structural_lint.py`, `sdd/CHANGELOG.md`.

---

## D-071 — Un carril que se declara en el enrutado pero no en el mapa de su fase queda medio enganchado

- **Fecha:** 2026-09-10 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-070]] (salió de esta misma lectura), [[D-069]] (el planner retirado que el README seguía nombrando), [[D-023]] (borrar el inventario que duplica un `ls`), [[D-022]] (el enrutado vive en las `description`).

**Contexto.** `wf-spec-from-code` —el onramp brownfield de la fase Spec— estaba declarado donde hace falta para que **funcione**: el rootmap de `CLAUDE.md`, la regla eager `sdd-routing.md` y su propia `description`. Y no estaba en ninguno de los sitios donde hace falta para que **se mantenga**. El `README.md` de la fase, que es el mapa funcional que lee cualquiera que vaya a tocarla, tenía **cero menciones**: ni caso de uso, ni fila en la tabla de workflows, ni `kb-spec-characterization` en la tabla de KBs, ni `wf-spec-from-code` en la lista de "invocado desde" de `sdd-spec-writer`.

Como el enrutado sí funciona, nada lo delata: la skill se invoca, hace su trabajo y nadie descubre que media fase no sabe que existe. Lo que sí se degrada es todo lo que se deriva del mapa. Tres consecuencias medidas en la misma lectura:

- **`sdd-spec-explorer` no cargaba `kb-spec-characterization`.** Es el agente de **diagnóstico** de la fase, y los otros dos sí la llevan. Un spec `Origen: characterization` diagnosticado sin esas reglas se juzga con la vara de un spec greenfield — y ahí los `[INFERIDO]` y el campo `Evidencia` **son lo correcto**, no defectos. El hallazgo falso lo produce el que no tiene la KB.
- **El README seguía nombrando a `sdd-spec-planner`** (`explorer`, `planner`, `writer`, `auditor`) el día después de retirarlo en [[D-069]]. La retirada tocó `install.sh`, `CLAUDE.md`, `DIAGRAMS.md` y dos READMEs; el bullet del mapa de componentes no era una referencia al fichero y se salvó del barrido.
- **Su árbol de directorios estaba stale en cinco entradas** (le faltaban `routing.md`, `DIAGRAMS.md`, `kb-spec-characterization/`, `wf-spec-amend/` y `wf-spec-from-code/`).

**Decisión.** El carril se engancha en los cuatro sitios que lo mantienen: caso de uso propio (2.b, con el ciclo completo `discover` → gate humano → `generate` → confirmación de `[INFERIDO]`), fila en la tabla de workflows, fila de `kb-spec-characterization` en la de KBs, la excepción brownfield en la precondición de la fase, y dos filas en checkpoints humanos. `sdd-spec-explorer` **gana `kb-spec-characterization`** y la enumera en su verificación de contexto. Y el **árbol de directorios se borra**: duplicaba a mano lo que `ls` ya dice, con el mismo criterio de [[D-023]] — el README mantiene el mapa funcional, no el inventario.

**Alternativas descartadas.**
- *Dejar el brownfield fuera del README porque el rootmap ya lo enruta* → confunde las dos audiencias. El rootmap lo lee el orquestador para **invocar**; el README lo lee quien va a **tocar** la fase, y lo que no está ahí no entra en el barrido de la siguiente revisión. Los tres hallazgos derivados salieron precisamente de esa ausencia.
- *Añadir `kb-spec-characterization` solo al auditor* → ya la tenía. El que diagnostica es el explorer, y era el único de los tres sin ella.
- *Actualizar el árbol de directorios en vez de borrarlo* → volvería a quedarse viejo en la siguiente pieza que se añada. Lo mismo que ya se decidió en [[D-023]] para el rootmap de las reglas de fase.

**Consecuencias / aprendizaje.** **Enrutar una pieza y documentarla son cosas distintas, y solo la primera se nota si falta.** Una skill mal enrutada no se invoca nunca: el fallo es inmediato y ruidoso. Una skill enrutada pero ausente del mapa de su fase funciona perfectamente y se degrada en silencio — no hereda las revisiones, no aparece en los barridos, y sus agentes se quedan sin las KBs que su dominio exige. El criterio operativo al añadir un carril: **el enrutado lo hace funcionar hoy; el mapa de la fase lo hace sobrevivir a la próxima revisión.**

**Referencias.** `sdd/pipeline/spec/README.md`, `sdd/pipeline/spec/agents/sdd-spec-explorer.md`, `sdd/pipeline/spec/skills/wf-spec-from-code/SKILL.md`, `sdd/CHANGELOG.md`.

---

## D-070 — Una `wf-*` con `context: fork` que delega en su propio `agent:` se forkea un clon de sí misma

- **Fecha:** 2026-09-10 · **Estado:** Adoptada (regla blocking del linter; conducta pendiente de medir en transcripts). · **Relacionada:** [[D-044]] (midió el coste del clon, en la capa de arriba), [[D-068]] (misma clase: el detector vigila la cita, no la conducta), [[D-045]] (dónde corre cada skill), [[D-071]] (salió de la misma lectura), [[D-038]] (`allowed-tools` no es enforcement).

**Contexto.** Al enganchar `wf-spec-from-code` ([[D-071]]) apareció que su Paso 5 decía *"Invoca el agente `sdd-spec-writer`"* — siendo `sdd-spec-writer` el `agent:` de su propio frontmatter. `agent:` es el **destino de inyección del fork**: el cuerpo de esa skill ya corre como ese agente, con su contexto y sus KBs. Pedirle que lo invoque forkea un **clon suyo**, el mismo envoltorio inútil que [[D-044]] midió una capa más arriba (~210 KB de contexto duplicado por delegación, y un salto que vuelve a ser asíncrono).

La norma **ya estaba escrita** desde [[D-044]], en `kb-sdd-creation-guide`: *"`context: fork` es para workers: esas declaran `agent:` y no delegan"*. No la medía nadie. Al mecanizarla salieron **35 sitios en 15 workflows** de cinco áreas —`meta`, Design, Plan, Tasks y el de Spec—, incluidos **cuatro que abren declarando *"Tu rol es de orquestador puro… delegas al agente `X`"*** siendo `X` el agente que son. Ninguno de los 15 declara `AskUserQuestion`: no son orquestadores mal colocados, son **workers con la prosa del modelo anterior**.

**Por qué no lo cazaba `FORK-ORCHESTRATOR`.** Ese check busca el nombre de la **tool** (`Agent(`, "tool `Agent`"). Estos 35 delegan en **prosa** y no la nombran nunca. Tercera vez que la misma forma de ceguera aparece en esta campaña, después de `FORK-ASKUSER-CONFLICT` ([[D-064]]) y del propio `FORK-CONFIRM-GATE` ([[D-068]]).

**Decisión.** Regla **`FORK-SELF-DELEGATION` [blocking]**: en una `wf-*` con `context: fork` y `agent: X`, el cuerpo no puede ordenar delegar en `X`. Caza sus dos formas —la **nombrada** (*"Invoca el agente `X`"*, *"delegas la arquitectura al agente `X`"*) y la **anónima** (*"Invoca al agente con este prompt"*, que en un fork con `agent:` no puede referirse a otro)—, y excluye la negación en la misma línea para que la nota que prohíbe el patrón no case con el patrón. Delta medido: **35 → 0**.

Los 35 sitios se arreglan **convirtiendo el prompt de delegación en el contrato que la skill aplica**: el contenido del prompt ya era el contrato, solo estaba envuelto en un imperativo hacia un tercero que no existe. En la misma pasada, **17 frontmatter pierden el `Agent` sobre-declarado** en `allowed-tools` (declararlo es lo que invita al clon); el único fork que conserva la tool es `wf-task-run`, que delega de verdad y en **otros** agentes: los owners del overlay de stack.

**Alternativas descartadas.**
- *Pasarlas al hilo principal, como [[D-065]] hizo con `wf-spec-validate`* → ese movimiento es para skills que **sostienen gates humanos**, y ninguna de las 15 declara `AskUserQuestion`. Son workers: lo que sobra es la delegación, no el fork.
- *Dejar la regla en warning y arreglar solo la fase Spec* → una regla que no llega a cero deja de gobernar (es lo que acababa de pasar con la norma en prosa: escrita desde [[D-044]], incumplida en 35 sitios). Y el defecto es **idéntico** en las cinco áreas: arreglar una y documentar las otras cuatro reproduce exactamente el problema que la regla existe para cerrar.
- *Ampliar `AGENT_DISPATCH_RE` para que `FORK-ORCHESTRATOR` viera también la prosa* → mezcla dos defectos distintos con arreglos opuestos: delegar en **otro** agente desde un fork se arregla moviendo la skill a main; delegar en **sí misma** se arregla quitando la delegación. Un solo tipo de finding con dos remedios contrarios no orienta a quien lo lee.

**Consecuencias / aprendizaje.** Dos. (a) **Cambiar el frontmatter cambia el modelo de ejecución, y la prosa no se entera.** Estos cuerpos se escribieron cuando la skill era un orquestador; el día que ganaron `context: fork` + `agent:` pasaron a **ser** el agente, y las frases de rol se quedaron describiendo el mundo anterior. *"Tu rol es de orquestador puro"* no es una frase de estilo: es una **afirmación sobre dónde corre la skill**, y contradecía a su propio frontmatter. Al tocar `context:`/`agent:` hay que releer el cuerpo entero, no solo el paso que se cambia. (b) La otra mitad de la lección de [[D-068]], confirmada: **un detector caza la forma que se le enseñó**, y aquí la forma enseñada era el nombre de una tool que estos 35 sitios nunca escriben.

**Deuda declarada.** Los 15 workflows conservan prosa **descriptiva** del modelo viejo (*"escribe el output del agente"*, *"si el agente devuelve `DESIGN_GAP`"*). No es ejecutable —ya no hay orden de delegar— pero lee raro. Se cierra en la revisión de cada fase, no aquí: Design tiene además al menos un fork que entrevista al usuario (`wf-design-moodboard`), que es un problema de [[D-002]] y merece su propio bloque.

**Referencias.** `sdd/scripts/sdd-structural-lint.py` (`check_fork_self_delegation`), `sdd/tests/test_sdd_structural_lint.py` (7 tests), `sdd/meta/skills/kb-sdd-creation-guide/SKILL.md`, los 15 `SKILL.md` de `meta/`, Design, Plan, Tasks y Spec, `sdd/CHANGELOG.md`.

---

## D-069 — Lo que duplica una fuente de verdad se retira o se respalda; y una lista parcial es peor que ninguna

- **Fecha:** 2026-09-10 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-065]] (la clase de fallo: enumeraciones que gobiernan conducta), [[D-023]] (borrar el rootmap que deriva), [[D-021]]/[[D-022]] (el enrutado vive en las `description`), [[D-055]] (redundancia deliberada, la que NO se toca).

**Contexto.** Cuarta, quinta y sexta aparición de lo que [[D-065]] documentó: material que duplica una fuente de verdad y deriva sin que nada lo note. Medido:

| Duplicado | Estado |
|---|---|
| `## Verificación de contexto` de los agentes | **32 KBs sin enumerar en 6 agentes.** Spec no verificaba `kb-spec-characterization` en 2 de 4 |
| `meta/skill-registry.md` (artefacto **generado**) | Stale: conservaba la descripción pre-[[D-065]] de `wf-spec-validate`. Los tests comprobaban que el generador funciona, no que lo commiteado esté al día |
| Columna de argumentos del rootmap de `CLAUDE.md` | Stale en 3 de 3 muestreados. `install.sh:407` lo siembra como CLAUDE.md **raíz del proyecto** |
| `sdd-spec-planner` | Agente instalado que **ninguna workflow declara**; su trabajo lo movieron [[D-021]]/[[D-022]] al carril eager, y solapa con el explorer |

**Decisión.** Cada duplicado se **retira** o se **respalda**, según aporte:

1. **La enumeración de KBs se retira, no se completa.** Los dos arquitectos de Design ya tenían la forma correcta —*"para cada KB de tu frontmatter"*— y por eso eran los únicos que no podían quedarse cortos. Los cuatro agentes con lista parcial adoptan esa forma. `sdd-kb-check.py` gana la regla: **enumera todas o ninguna**; lo que se deniega es la lista **parcial**, que se lee como exhaustiva y no lo es. Remitir en genérico no es hallazgo: es lo preferido.
2. **`generate-skill-registry.py --check`** + test que falla si lo commiteado no coincide con el árbol (ignorando la línea de fecha, que cambia sola). Un generador sin `--check` no tiene forma de delatar que su salida está vieja.
3. **La columna de argumentos del rootmap se borra.** El mapa intención→skill es lo que aporta; los argumentos los arma el orquestador leyendo el `argument-hint`, que es la única fuente que no envejece. Precedente literal de [[D-023]].
4. **`sdd-spec-planner` se retira.** Su caso de uso documentado (petición ambigua que mezcla intenciones) lo absorbe `sdd-spec-explorer`, que ya declaraba la misma salida.

**Lo que NO se toca, y por qué importa distinguirlo.** El contrato del bloque de gap está duplicado a propósito entre `kb-gap-conventions` y las workflows: [[D-055]] mide que una regla de `.claude/rules/` llega **tarde** al `Write`, así que la redundancia es el mecanismo. La frontera es **qué** se duplica: el **contrato** se queda; la **anécdota histórica** que lo justifica, no. Igual con el párrafo del índice de features: lo que se unificó fue el mensaje de fallback —que ya había divergido en tres redacciones— y no la justificación local del fan-out, que es load-bearing donde está.

**Alternativas descartadas.**
- *Completar las cuatro listas parciales* → mantener cuatro duplicados en vez de tres. Habría hecho falta un backstop **más** estricto para conservar algo que no aporta.
- *Generar la columna de argumentos del rootmap* → un generador más para un dato que el orquestador ya tiene en el frontmatter de la skill que invoca.
- *Dejar el planner documentado como "uso ad-hoc"* → es lo que estaba, y el resultado fue un agente que nadie invoca, con siete KBs cargadas, y un README que le asigna la misma salida que al explorer.

**Consecuencias / aprendizaje.** Dos. (a) **La forma correcta ya estaba en el árbol**: los arquitectos de Design remitían al frontmatter mientras el resto enumeraba, y el que no duplicaba era el único inmune. Antes de escribir un backstop conviene mirar si algún sitio ya resolvió el problema por construcción. (b) **Una lista parcial es peor que ninguna**: ninguna te obliga a ir a la fuente; una parcial te convence de que ya la miraste.

**Referencias.** `sdd/scripts/sdd-kb-check.py`, `sdd/scripts/generate-skill-registry.py`, `sdd/CLAUDE.md` (rootmap), los 4 agentes alineados, `sdd/pipeline/spec/agents/sdd-spec-planner.md` (borrado), `sdd/tests/test_sdd_kb_check.py`, `sdd/tests/test_generate_skill_registry.py`, `sdd/tests/test_install_sh.py`.

---

## D-068 — `wf-spec-amend` sale del fork, y el detector de gates pasa a mirar la conducta, no una frase

- **Fecha:** 2026-09-10 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-064]] (que cazó una forma y dejó pasar tres), [[D-045]]/[[D-040]]/[[D-065]] (el mismo movimiento, tres veces antes), [[D-016]] (barrido exhaustivo por construcción), CU-3.q.

**Contexto.** [[D-064]] creó `FORK-CONFIRM-GATE` y lo dejó a 0 hallazgos. Al leer los 13 workflows enteros aparecieron **tres gates más** que la regla no veía, porque preguntan con otras palabras:

| Sitio | Forma |
|---|---|
| `wf-spec-discover:137` | *"**Espera respuesta del usuario** antes de continuar"* (ownership checkpoint) |
| `wf-spec-gap-resolve:73` | *"presenta el comportamiento deducido … **y pregunta**:"* — la confirmación de `[INFERIDO]`, o sea **CU-3.q entero** |
| `wf-spec-amend:44` y `:89` | *"preguntando al usuario:"* y *"**pide confirmación explícita** al usuario"* |

`wf-spec-amend` es el caso límite: sus **dos gates humanos son su razón de existir** —el Paso 4 se autodescribe *"el corazón — NO lo bypasses"* y el Paso 5 dice *"sin confirmación no hay enmienda"*— y ninguno era ejecutable. La skill entera dependía de algo que su arquitectura impedía.

**Decisión.** (1) **`wf-spec-amend` pasa al hilo principal**, cuarta aplicación del mismo patrón ([[D-040]], [[D-045]], [[D-065]]): orquesta, delega el análisis y la edición al `sdd-spec-writer` con `run_in_background: false`, y sostiene sus dos gates de verdad. `sdd-amend.py` sigue siendo el único que asigna `E-00X`. (2) **`wf-spec-discover` y `wf-spec-gap-resolve` paran y reportan** (`STOP_OWNERSHIP_AMBIGUO`, `STOP_INFERIDO_SIN_CONFIRMAR`); en discover **el contrato correcto ya existía** en `wf-spec-features-first:338`, y solo el fork creía que podía esperar. (3) **`FORK-CONFIRM-GATE` se afila** a las tres formas medidas, más la de esperar — porque ordenar aguardar a una persona tampoco es ejecutable sin turno. Delta: **3 → 0**.

**Alternativas descartadas.**
- *Que amend siga en fork con los gates convertidos en parada* → parte en dos el único flujo cuyo valor es la conversación dev↔humano sobre el texto de un CA, y multiplica los saltos justo donde hay una persona esperando.
- *Aflojar la regla para que no case con las notas que citan la frase prohibida* → se resolvió al revés: **la nota se reescribe**. Es la regla de autoría de [[D-045]] §4 (describir la conducta, no reproducir la forma prohibida) aplicada a la prosa explicativa.

**Consecuencias / aprendizaje.** Tres. (a) **Un detector caza la forma que se le enseñó, no la conducta** — [[D-064]] ya lo dijo y aun así su primera versión cubrió una de cuatro variantes. La lección operativa: al escribir la regla, enumerar las formas **observadas en el árbol**, no las imaginadas. (b) **Precisión y recall se pagan por separado**: al ampliarla apareció un falso positivo (`wf-prd-change-cascade` *describiendo* el gate de otra skill para explicar que no puede heredarlo), y el discriminante resultó ser algo tan pequeño como el **dos puntos** que separa la orden de la descripción. (c) Cuarta vez que un gate acaba en main: **el sitio de un gate no es una preferencia de diseño, es una consecuencia de quién puede presentarlo.**

**Referencias.** `sdd/pipeline/spec/skills/wf-spec-amend/SKILL.md` (reescrito), `wf-spec-discover/SKILL.md`, `wf-spec-gap-resolve/SKILL.md`, `sdd/scripts/sdd-structural-lint.py`, `sdd/tests/test_sdd_structural_lint.py`, `sdd/tests/test_install_sh.py`.

---

## D-067 — Cinco invariantes de la fase Spec que se rompían sin ruido

- **Fecha:** 2026-09-10 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-061]] (el sello del spec), [[D-059]] (el informe lo escribe su auditor), [[D-046]] (no encontrarlo no puede ser advertencia blanda), [[D-044]] (no encadenar forks), [[D-054]], CU-3.f / CU-3.h / CU-7.

**Contexto.** Ninguno de los cinco falla de forma visible: los cinco producen artefactos que **parecen correctos**. Salieron de leer los 13 workflows enteros, no de una pasada de conformance.

1. **`wf-spec-sync-from-prd` dejaba specs mintiendo.** Su Paso 4B decía *"siguiendo la misma disciplina que `wf-spec-delta`"* y reimplementaba el apply sin cuatro de sus cinco piezas —reapertura de la validación, versión menor, changelog, índice— y encima escribía `status_sync: in_sync` a mano. Un spec salía **`VALIDADO`, con contenido cambiado y declarándose sincronizado**: el estado exacto que [[D-061]] existe para impedir.
2. **`wf-spec-delta` hacía que el writer auditara lo que acababa de escribir**, ejecutando `wf-spec-conflict` y **firmando el `_conflict_report.md`**. Rompe autor≠verificador, encadena forks ([[D-044]]) y contradice [[D-059]], cuya copia correcta está a unos ficheros de distancia.
3. **`wf-prd-sync-impact` era ciego al layout estándar**: buscaba solo `features/*/*_spec.md`. Con subcarpetas por fase reportaba **cero specs, cero planes, cero tasks** — una matriz de impacto vacía que se lee como *"todo in_sync"*. Modo de fallo de [[D-046]].
4. **`wf-spec-from-code` miraba el sello sobre un path sin resolver**, así que no detectaba como sellado un spec en layout plano y lo pisaba.
5. **El conjunto de marcadores que bloquean el paso a Plan estaba definido en cuatro sitios y ninguno coincidía con el script.** El peor era la SSoT declarada: `kb-gap-conventions` **omitía `[CRÍTICO]`** en su patrón literal de verificación — el que un auditor copia tal cual.

Más dos verdades duplicadas: la cabecera de caracterización fijaba `Status sync: in_sync` con `PRD origen: N/A`, contra la Regla 3 que exige `unknown`; y `wf-spec-fast-track` pedía "el siguiente `F-NNN` libre" también en modo scoped, donde el ID ya lo asignó el discovery — produciendo un README `F-007` sobre un spec `F-003`.

**Decisión.** Cada invariante vuelve a tener **un solo dueño**: sync-from-prd decide *qué* cambia y **delega el *cómo se escribe*** al delta; delta **reporta** que conviene revisar conflictos y no audita; sync-impact mira los dos layouts; from-code resuelve el path antes de mirar el sello; y el conjunto de marcadores tiene **una definición** en `kb-gap-conventions` —con `[CRÍTICO]` y con la advertencia de que la autoridad es `sdd-seal.py spec --check`— y **tres citas**.

De paso, dos punteros rotos en silencio: `routing.md` atribuía a `kb-spec-expert` una prohibición del modo ligero **que no estaba escrita en ninguna parte** (ahora sí lo está, con su razón: lo que el modo ligero relaja es ceremonia, y un shared model o una entidad nueva no son ceremonia sino contrato con otras features); y `wf-spec-readiness` afirmaba en su regla de oro *"no propone resoluciones"* y *"no modifica artefactos"* mientras su Paso 4c le nombra árbitro y su veredicto es autoritativo para el índice.

**Alternativas descartadas.**
- *Completar el apply de `sync-from-prd` con las cuatro piezas que le faltan* → dos implementaciones del mismo apply, condenadas a divergir otra vez. La pregunta no era qué le falta, sino por qué hay dos.
- *Dejar que `delta` avise ejecutando el conflict "en modo informativo"* → el problema no es que bloquee o no: es **quién firma el veredicto** sobre un spec que su propio autor acaba de escribir.

**Consecuencias / aprendizaje.** Dos. (a) **Los defectos que no fallan son los que sobreviven a una campaña de conformance**: los cinco llevaban meses ahí y ninguna pasada los destapó, porque ninguno produce un error — producen un artefacto plausible. Leer el contrato entero encuentra cosas que ejecutarlo no. (b) **Una frase del tipo "siguiendo la misma disciplina que X" es una señal de alarma, no una garantía**: o se delega en X, o se está reimplementando X con menos piezas.

**Referencias.** `wf-spec-sync-from-prd`, `wf-spec-delta`, `wf-prd-sync-impact`, `wf-spec-from-code`, `wf-spec-readiness`, `wf-spec-fast-track`, `kb-gap-conventions`, `kb-traceability-rules`, `kb-spec-expert`, `kb-spec-characterization`, `pipeline/spec/routing.md`.

---

## D-066 — La cabecera del spec se verifica: el índice omitía en silencio lo que no sabía leer

- **Fecha:** 2026-09-09 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-046]] (no encontrarlo no puede ser advertencia blanda), `sdd-prd-frontmatter.py` (el precedente en PRD), [[D-060]] (main no redacta), CU-3.a.

**Contexto.** Tercer hallazgo de la revisión PRD↔Spec. El PRD tiene `sdd-prd-frontmatter.py`, que existe —según su propio docstring— porque *"al ser disciplina conductual, el agente omite algún campo de forma intermitente"*, y lo invocan **create y review**. La cabecera del spec **la consumen tres scripts** (`sdd-features-index.py`, `sdd-project-status.py`, `sdd-release.py`) y **no la validaba nadie**.

Lo que lo vuelve grave no es la ausencia del validador, sino cómo falla: `parse_spec()` **devuelve `None`** si no encuentra `Feature ID`, así que el spec **desaparece del índice entero**. No hay error, no hay aviso: sale un `_features.md` con menos features y apariencia de correcto. Es la forma exacta del incidente ya medido en la campaña —el índice mostrando 3 features mientras la conversación narraba 9— y es justo lo que [[D-046]] declaró inaceptable.

Y había una segunda pieza, invisible hasta cruzar las dos fuentes: **`kb-spec-characterization` —la SSoT de la cabecera de caracterización— no declaraba `Feature ID` ni `Origen de alcance`**, aunque `wf-spec-from-code` dijera en prosa que el header los lleva. Dos sitios describiendo la misma cabecera y contradiciéndose; un spec escrito según la plantilla se caía del índice. Además `header_field()` solo leía la forma pelada `> key: valor` y esa plantilla escribe en negrita, así que aunque los campos hubieran estado, no se habrían leído.

**Decisión.** Tres piezas. (1) **`sdd-seal.py spec --check` gana la condición 8b**: la cabecera declara `Feature ID` y `Origen de alcance`, o no se sella — el análogo de `sdd-prd-frontmatter.py`, alojado en el gate que ya existe en vez de en un script nuevo. (2) **`sdd-features-index.py` deja de omitir en silencio**: nombra en `stderr` cada spec que no pudo indexar y por qué, siguiendo el patrón que ya usaba para *"sin discovery"*. (3) **La plantilla de caracterización declara los dos campos** y `header_field()` tolera la negrita.

De paso, el hueco que la revisión encontró **en PRD**, no en Spec: `wf-prd-create` corría en el hilo principal declarando `[Read, Write, …]` y era la única de las cuatro workflows-en-main sin la norma *"y tampoco lo escribes tú"*. Tenía la mitad de lectura y le faltaba la de escritura.

**Alternativas descartadas.**
- *Un script propio, calcado de `sdd-prd-frontmatter.py`* → superficie nueva para una comprobación de tres líneas, cuando el gate de sellado ya lee el fichero y ya deniega. El PRD lo tiene aparte por historia, no por diseño.
- *Que `parse_spec` invente un ID cuando falta* → convierte un artefacto incompleto en uno **incorrecto**, que es peor: el índice diría algo falso con total aplomo.
- *Validar la cabecera entera (los 12 campos de la plantilla)* → falsos negativos garantizados: la cabecera de caracterización es legítimamente distinta de la de fast-track. Se exigen solo los dos campos que **algún consumidor lee**, que es el criterio que hace la regla defendible.

**Consecuencias / aprendizaje.** Un campo de cabecera no es documentación: es la **entrada de otro programa**, y la lista de campos obligatorios se deriva de quién los lee, no de lo bonita que quede la plantilla. Y el corolario de [[D-046]]: cuando un parser devuelve `None` ante lo que no entiende, **el silencio se propaga aguas abajo con apariencia de dato**. Validado contra los cuatro specs reales de la campaña: los cuatro declaran ambos campos, así que la condición no falsea las pasadas.

**Referencias.** `sdd/scripts/sdd-seal.py` (condición 8b), `sdd/scripts/sdd-features-index.py` (`header_field`, `SPECS_SIN_CABECERA`), `sdd/pipeline/spec/skills/kb-spec-characterization/SKILL.md`, `sdd/pipeline/prd/skills/wf-prd-create/SKILL.md`, `sdd/tests/test_sdd_seal.py`, `sdd/CHANGELOG.md`.

---

## D-065 — `wf-spec-validate` sale del fork: el único gate de sellado que no registraba a nadie

- **Fecha:** 2026-09-09 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-027]] (identidad del aprobador), [[D-061]] (el spec gana sello), [[D-045]]/[[D-040]] (el mismo movimiento, dos veces antes), [[D-060]] (main no redacta), CU-3.f / CU-3.g.

**Contexto.** `kb-traceability-rules` Regla 10 es la SSoT de la atribución de aprobación humana y empezaba diciendo *"los **tres** gates donde el pipeline sella el avance de fase — `wf-prd-review` (PRD), `wf-plan-validate` (Plan), `wf-qa-verify` (QA)"*. Esa regla **vive en la fase Spec** y Spec **no estaba en su propia lista**.

Se escribió cuando el spec no sellaba nada, así que era correcta. [[D-061]] le dio estado operativo y nadie volvió a ella: desde entonces el spec era el **único artefacto que llegaba a `VALIDADO` sin que constara nadie**, mientras el plan derivado de él sí exigía un nombre. La causa inmediata es estructural: `wf-spec-validate` era `context: fork`, y capturar la identidad exige preguntar. De los cuatro gates de sellado, era el único fork.

**Decisión.** `wf-spec-validate` pasa al **hilo principal**, con la forma exacta de `wf-plan-validate`: orquestador puro que delega la auditoría a `sdd-spec-auditor` por la tool `Agent` con `run_in_background: false`, presenta el informe, corre el `--check` y, solo si pasa, captura la identidad y sella. Es el mismo movimiento que [[D-040]] hizo con `wf-prd-change` y [[D-045]] con `wf-spec-features-first` — tercera vez, y la razón siempre es la misma: **un gate se escribe donde puede presentarse**.

Y Regla 10 se corrige en dos frentes. Pasa a enumerar **cuatro** gates con backstop en `test_install_sh.py` (una enumeración que gobierna conducta no se mantiene sola). Y separa dos cosas que conflaba: **quién captura** el dato humano (el workflow, preguntando) y **quién lo estampa** en el artefacto (un script). Decía *"ningún script lo escribe"*, cuando el PRD **ya lo escribía por script** desde siempre (`sdd-prd-apply.py --seal "<valor>"`). El spec sigue ese precedente con `sdd-seal.py … --seal --approved-by "<valor>"`, y así main no escribe contenido en un artefacto ([[D-060]]).

**Alternativas descartadas.**
- *Que el fork reporte y main estampe la línea* → main escribiendo contenido en el artefacto, justo lo que [[D-060]] cierra. Y deja el gate a merced de que el orquestador improvise la pregunta, que es lo que [[D-045]] midió fallando.
- *Dejar el spec sin atribución («total, no es verificable»)* → confunde *no verificable* con *no necesario*. La Regla 10 existe para trazabilidad de autoría en equipo, y el eslabón que se saltaba es el que decide si un plan puede construirse encima.
- *Que `sdd-seal.py` valide el nombre* → no hay nada que validar; el script transcribe un dato que recibe. Esa es exactamente la frontera que la regla ahora explicita.

**Consecuencias / aprendizaje.** Dos. (a) **Una enumeración dentro de una norma es deuda con fecha de caducidad**: «los tres gates» fue verdad hasta que dejó de serlo, y no hubo señal. Toda lista que gobierne conducta necesita backstop o derivarse del árbol. (b) *No verificable mecánicamente* dice algo sobre el **valor**, no sobre **quién lo escribe** — conflar las dos cosas es lo que dejó a Plan y QA escribiendo desde el workflow; unificarlos queda como ítem de ROADMAP, no como patrón a copiar.

**Referencias.** `sdd/pipeline/spec/skills/wf-spec-validate/SKILL.md`, `sdd/pipeline/spec/skills/kb-traceability-rules/SKILL.md` (Regla 10), `sdd/scripts/sdd-seal.py` (`--approved-by`), `sdd/tests/test_sdd_seal.py`, `sdd/tests/test_install_sh.py`, `sdd/CHANGELOG.md`.

---

## D-064 — El linter vigilaba la cita, no la conducta: diez gates escritos donde no pueden presentarse

- **Fecha:** 2026-09-09 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-062]] (que arregló dos de los diez), [[D-045]]/[[D-002]] (fork ⊥ preguntar), [[D-016]] (barrido exhaustivo por construcción), [[D-024]] (ponderación por riesgo), [[D-026]] (el override lo arma el usuario).

**Contexto.** [[D-062]] arregló el gate de sobreescritura de `wf-spec-fast-track` y `wf-spec-from-code`. Al comparar la fase PRD con la fase Spec aparecieron **cuatro más en el mismo directorio** —`wf-spec-analyze`, `wf-spec-discover`, `wf-spec-conflict`, `wf-spec-readiness`—, todos `context: fork`, todos diciendo *"pregunta al usuario"*. Mi propio barrido, hecho con la clase de bug ya identificada, se quedó corto **dentro de su propia fase**.

La razón de que nadie los viera está en el linter, y es el hallazgo que de verdad importa: `FORK-ASKUSER-CONFLICT` es **blocking** y daba **0**, porque dispara con el **nombre literal de la tool**. Un fork que pregunta en prosa era invisible. Existía además `FORK-INTERVIEW` como complemento heurístico —también **0**—, afilado en [[D-045]] para la forma «entrevista secuencial» y ciego a la forma «gate de sobreescritura», que es la común. **El detector vigilaba la cita, no la conducta.**

Al escribir la regla nueva, el conteo real fue **10**, no 6: aparecieron los seis de Design/Plan/Tasks que ya estaban registrados en el ROADMAP **y uno más** (`wf-design-intake`) que el barrido a mano no había encontrado. La regla halló lo que la revisión cuidadosa se dejó.

**Decisión.** Regla nueva **`FORK-CONFIRM-GATE` (blocking)**: un `wf-*` con `context: fork` cuyo cuerpo **dicte** un gate de confirmación en prosa. Patrones de alta precisión a propósito —cada alternativa es una instrucción de preguntar, nunca una descripción de que no se puede—, para que las notas explicativas de [[D-062]] no casen. Delta medido: **10 → 0**.

Y los diez se arreglan **según lo que haya que perder**, no con una plantilla única:
- **Artefacto con trabajo humano o estado dentro** (`_analysis.md` con respuestas, `_discovery.md` cuyos `F-00X` citan los specs, plan validado, tasks con estado de ejecución, qa plan con sus `Estado`, `DESIGN.md`, prototipos, brief) → **para y reporta** `STOP_ARTEFACTO_EXISTE`, y el override `--allow-overwrite-*` lo arma el usuario en el gate de quien sí puede preguntar ([[D-026]]). El mensaje de parada **carga el dato que hace útil al gate**: cuántas respuestas se perderían, que los IDs están citados aguas abajo, qué estado se descarta.
- **Informe derivado sin decisiones humanas dentro** (`_conflict_report.md`, `_readiness_report.md`) → **el gate se quita**. No protegía nada: quien lanza el flujo los regenera en cada pasada. Un gate que no protege trabajo es fricción, y desde un fork además es fricción imposible.

**Alternativas descartadas.**
- *Ampliar `FORK-INTERVIEW` (warning) en vez de una regla nueva* → mezcla dos cosas con precisión distinta. La heurística de entrevista tolera falsos positivos y por eso es warning; un gate de confirmación en un fork es un defecto **cierto**. Separarlas deja que cada una tenga la severidad que merece.
- *Aplicar a los diez la forma de [[D-062]]* → habría metido un gate ceremonial en dos informes que nadie edita a mano. La pregunta que ordena esto no es "¿existe?" sino "¿qué se pierde?".
- *Arreglar solo los cuatro de Spec y dejar los seis restantes al ítem de ROADMAP* → imposible sin desactivar la regla: `--check` sale 2 con cualquier blocking. Y una regla que no muerde es teatro.

**Consecuencias / aprendizaje.** Tres. (a) **Un detector que busca la cita de una norma no detecta su incumplimiento**: `FORK-ASKUSER-CONFLICT` daba 0 sobre un árbol con diez violaciones reales. Al escribir un check hay que preguntarse qué forma tiene la conducta en el mundo, no qué palabra la nombraría. (b) **Un barrido a mano no cierra una clase de bug**, ni siquiera hecho a conciencia y con el patrón delante — [[D-016]] ya lo dijo (*"exhaustivo por construcción"*) y esta vez la prueba es directa: la regla encontró uno que yo no. (c) La lección de [[D-024]] se afina: el valor de un gate es la información que carga, y **un artefacto derivado no merece gate ninguno**.

**Referencias.** `sdd/scripts/sdd-structural-lint.py` (`FORK-CONFIRM-GATE`), los diez `SKILL.md` de spec/design/plan/tasks, `sdd/pipeline/orchestration.md` (familia `--allow-overwrite-*`), `sdd/docs/ROADMAP.md` (13.2), `sdd/CHANGELOG.md`.

---

## D-063 — La anti-fabricación llega a Spec: rige cada escritura, y el sello exige que la asunción se vea

- **Fecha:** 2026-09-09 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-039]] (el precedente en PRD, declarado y no heredado), [[D-061]] (el sello del spec, que da dónde enganchar el backstop), [[D-057]] (un gap tiene un solo bloque respondible), [[D-037]] (guarda de vacuidad), [[D-055]] (qué carril llega al escritor a tiempo), CU-3.a / CU-3.f.

**Contexto.** Segundo hueco del reporte PRD↔Spec. [[D-039]] estableció en el PRD que la anti-fabricación **no caduca al sellar**: rige cada escritura, porque *"un invariante mantenido por un workflow no es un invariante del artefacto — hay que preguntarse quién más escribe ese fichero"*. En Spec eso nunca se heredó. Sobre un spec escriben **cuatro** workflows y la regla la conocían **dos**:

| Escritor | ¿Registra lo que infiere? |
|---|---|
| `wf-spec-fast-track` | sí — `## Asunciones Aplicadas` al generar |
| `wf-spec-delta` | sí — `## Asunciones Aplicadas (vX.Y)` al evolucionar |
| `wf-spec-gap-resolve` | **no** — cero menciones de asunción o inferencia en sus 135 líneas |
| `wf-spec-amend` | **no las tenía escritas** (ver la corrección de abajo) |

El caso grave es `gap-resolve`, y no es teórico: su Paso 5 integra respuestas completando *"texto faltante de HUs"* y *"CAs que no pudieron generarse"*. Una respuesta a un gap casi nunca trae **todo** lo que hace falta para cerrar una HU; lo que falte lo pone quien escribe. Y el resultado es peor que en el PRD, porque además **se borra la evidencia**: el gap se cierra, el `[INCOMPLETO]` desaparece, el spec queda impecable — y contiene decisiones que nadie tomó, sin ningún marcador que lo delate.

**Corrección de diagnóstico (el reporte inicial se pasó de frenada con `wf-spec-amend`).** Al leerlo entero resultó estar **mejor cubierto de lo que yo dije**, y por un mecanismo más fuerte que una marca: su Paso 4 es un gate de clasificación que manda a `wf-spec-delta` todo lo que *"el spec/PRD no determina"*, y su Paso 5 exige que **el humano confirme el texto final palabra por palabra**. Añadirle la maquinaria de marcado habría sido acumular prosa redundante sobre una garantía que ya existía. Lo que sí faltaba era **nombrar el mecanismo** (para que no parezca un olvido) y cerrar una costura real: su línea de changelog `E-00X` registraba *que* hubo enmienda, no **qué se fijó ni contra qué traza** — y *"aclaración CA-004"* no permite comprobar después que fuera una aclaración.

**Decisión.** Dos piezas, normativa y mecánica.

1. **La obligación sube a `kb-gap-conventions`** —la SSoT de gaps, que entra en la **línea 1** del contexto de los agentes de Spec por su `skills:` ([[D-055]]: es el único carril que llega a tiempo a quien escribe desde cero)— con la tabla de los cuatro escritores y **las dos escapatorias de [[D-039]] nombradas**: (i) estrechar o reinterpretar un CA o una regla transversal que ya estaba **no es higiene**, aunque se sienta como limpieza; (ii) **no vale diferir a Design o Plan** una decisión de alcance — el patrón *diferir lo pequeño y decidir lo grande*. `wf-spec-gap-resolve` gana el bloque operativo (Paso 5.1), con la frontera explícita entre **marcar** (lo conservador y menor) y **parar** (una bifurcación real de producto: corre en fork, no puede preguntar, luego no puede decidir).

2. **Backstop mecánico en `sdd-seal.py spec --check`:** un gap `[INFORMATIVO]` sin responder cuya asunción por defecto **ya está aplicada en los CAs** debe tener entrada que lo cite en `## Asunciones Aplicadas`, o no se sella. Con la guarda de vacuidad de [[D-037]]: si la sección existe pero no se le reconoce ninguna entrada `- **[A-00X]**`, **deniega** en vez de darla por buena.

**Lo que este backstop NO hace, dicho para que nadie lo sobrevenda.** No juzga si la asunción es correcta ni si una frase traza a lo que dijeron: eso es juicio semántico y [[D-039]] ya lo descartó como no mecanizable. Y no detecta una inferencia libre en la prosa de un CA sin gap detrás. Lo que verifica es que **la decisión sea visible** — y ese era exactamente el agujero: en el PRD el verificador *confirmaba* el invariante (`0 = 0`) precisamente porque el contenido fabricado no se había marcado.

**Sobre la mitad que se difirió, y por qué el paralelo con el PRD era falso.** El plan inicial era darle al spec el invariante **1:1** de `sdd-prd-ready.py`. No se puede: ese 1:1 empareja marcas **inline** `[ASUNCIÓN]` con entradas `[ASN-XXX]`, y el spec **no tiene marca inline** —`## Asunciones Aplicadas` es una lista sin contrapartida en el texto de los CA—, así que no hay con qué emparejar. Construirlo exigía inventarle un formato al spec: cambio de contrato, y no antes de las pasadas de sellado. La salida fue mirar qué contrapartida **sí** existe ya, y resulta que el bloque `[INFORMATIVO]` lo es: el mismo invariante, sin tocar el formato. Queda abierto en el ROADMAP si el residuo (inferencia libre sin gap detrás) merece la marca inline.

**Alternativas descartadas.**
- *Solo la norma, sin backstop* → es lo que hizo [[D-039]] en el PRD y su propio texto dice por qué no basta: la obligación de generar las marcas es normativa, pero sin nada que la verifique el spec se sella igual. [[D-061]] acababa de crear el sitio donde engancharla; no usarlo habría sido dejar la pieza a medias por segunda vez.
- *Inventar la marca inline ahora para tener el 1:1 completo* → cambio de contrato a tres pasadas de sellar la fase. El coste no es escribirla: es que todo lo que parsea specs asuma un formato que aún no se ha medido.
- *Dar a `wf-spec-amend` la misma maquinaria que a `gap-resolve`* → prosa redundante sobre una garantía más fuerte que ya existía. Cuando dos skills necesitan el mismo invariante por mecanismos distintos, duplicar el mecanismo debilita los dos: el lector deja de saber cuál manda.
- *Bloquear también por `[INFORMATIVO]` respondido* → un gap respondido **no** tiene asunción que documentar: alguien lo decidió. Bloquear ahí convertiría el check en ruido y enseñaría a rodearlo.

**Consecuencias / aprendizaje.** Tres. (a) **El sitio donde enganchar un backstop puede no existir todavía**, y esa es una razón legítima para diferir — pero entonces hay que volver: [[D-039]] no podía tener este check en Spec porque el spec no se sellaba, y en cuanto [[D-061]] lo hizo sellable, la deuda venció. (b) **Un paralelo entre fases puede ser falso por el formato, no por el principio**: el 1:1 del PRD no era portable, el principio sí; buscar qué contrapartida ya existe es más barato que replicar la del vecino. (c) **Al heredar una norma hay que leer al destinatario, no solo al precedente** — di por hueco en `wf-spec-amend` lo que era una garantía distinta y más fuerte, y de haber "arreglado" lo que creía, habría empeorado el skill.

**Referencias.** `sdd/pipeline/spec/skills/kb-gap-conventions/SKILL.md` (sección nueva, SSoT), `sdd/pipeline/spec/skills/wf-spec-gap-resolve/SKILL.md` (Paso 5.1), `sdd/pipeline/spec/skills/wf-spec-amend/SKILL.md` (Pasos 4 y 7), `sdd/scripts/sdd-seal.py` (`check_spec` condición 8), `sdd/tests/test_sdd_seal.py`, `sdd/tests/test_install_sh.py`, `sdd/docs/ROADMAP.md` (13.3 / 13.4), `sdd/CHANGELOG.md`.

---

## D-062 — La sobreescritura ponderada por riesgo llega a Spec: el silencio protector también decide en tu nombre

- **Fecha:** 2026-09-09 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-024]] (el principio general que no se heredó), [[D-061]] (que creó la línea objetiva: `Estado: VALIDADO`), [[D-045]]/[[D-026]] (dónde vive un gate y quién lo presenta), [[D-025]], CU-3.a / CU-3.f.

**Contexto.** Al comparar la fase PRD —cerrada— con la fase Spec, [[D-024]] apareció como el caso más claro de decisión declarada **"principio general"** que nunca se propagó: su propio texto dice *"no se propaga a las otras fases en este cambio, **se hereda al mantenerlas**"* y **nombra explícitamente al "spec validado"**. Al ir a heredarla aparecieron **tres** sitios, y ninguno de los tres era el que esperábamos:

1. **`wf-spec-features-first` Paso 4b** — *"si ya existe su spec → no relances (preservar trabajo previo), excluye del fast-track y anota como «ya generada»"*. Es el **extremo contrario** al "¿seguro?" plano que [[D-024]] atacó: protección máxima, cero elección. Un *"regenera el spec de F-003, he cambiado el PRD"* se convierte en un **no-op reportado como éxito**. Y es el único de los tres que está en la ruta que mide CU-3.a.
2. **`wf-spec-fast-track` Paso 10** — *"Si existe → pregunta al usuario si desea regenerarlo"*. La instrucción **no era ejecutable**: la skill es `context: fork` con `allowed-tools: [Read, Write, Bash]`, así que no tiene `AskUserQuestion`. Un gate escrito donde no puede presentarse — la misma clase de defecto que [[D-045]] encontró en los cuatro gates de features-first, sobrevivida en un quinto sitio.
3. **`wf-spec-from-code` Paso 6** — *"Si ya existe → pregunta antes de regenerar"*. Idéntico: fork, sin `AskUserQuestion`, gate inejecutable.

Los tres llevaban ahí desde antes de [[D-024]], y hasta [[D-061]] **no había forma de arreglarlos**: la ponderación necesita una línea objetiva que diga "esto está sellado", y el spec no tenía ninguna.

**Decisión.** La regla de [[D-024]] se hereda a Spec con sus tres ramas intactas (sellado → confirma siempre avisando del descarte; draft + intención explícita → procede; draft + petición ambigua → gate ligero), leyendo `Estado: VALIDADO` ([[D-061]]) donde el PRD lee `Aprobado por:`. Con **tres precisiones nuevas** que el caso del PRD no obligaba a resolver:

- **El reparto entre main y el fork.** El gate vive donde puede presentarse: `wf-spec-features-first` (hilo principal) clasifica el subset y sostiene los dos gates; `wf-spec-fast-track` y `wf-spec-from-code` (fork) **paran y reportan** con veredicto `STOP_SPEC_SELLADO` en vez de fingir que preguntan. El override es `--allow-overwrite-sealed-spec`, armado **solo** por el usuario eligiendo ([[D-026]]).
- **La cardinalidad.** El PRD es un fichero; el spec son N. El gate es **uno solo con la lista de features dentro** — preguntar feature a feature por un lote de nueve es exactamente el *nagging* que [[D-024]] existe para evitar.
- **La salida no destructiva se nombra en el propio bloqueo.** Quien quiere *cambiar* un spec validado no quiere regenerarlo: el mensaje de parada apunta a `wf-spec-delta` / `wf-spec-amend`, que **reabren** el sello ([[D-061]]) en vez de descartarlo.

Y la norma general sube a `pipeline/orchestration.md` —el carril eager que el orquestador **sí** lleva encima— con las líneas objetivas de las tres fases tabuladas, en vez de quedarse como promesa dentro del texto de una decisión ([[D-060]], mismo patrón).

**Alternativas descartadas.**
- *Dejar el salto silencioso de 4b («preservar trabajo previo» es el default seguro)* → el default **es** correcto; lo que no lo es es tomarlo sin decírselo a quien pidió lo contrario. Un no-op reportado como "ya generada" es indistinguible de un éxito, y el usuario descubre que su regeneración no ocurrió cuando lee un spec viejo tres pasos después.
- *Dar `AskUserQuestion` a los dos forks* → no existe: un subagente no puede renderizarlo ([[D-045]]). Escribirlo igualmente es lo que ya estaba y es peor que no tener gate, porque **parece** que hay uno.
- *Preguntar por cada feature del lote* → el nagging que [[D-024]] rechazó, multiplicado por N.
- *Un `--force` genérico en vez de un `--allow-*` nominal* → rompería la familia de overrides del ecosistema y su norma de armado ([[D-026]]). El flag nombra **qué** gate cruza, que es lo que permite auditarlo.

**Consecuencias / aprendizaje.** Tres, y el tercero es el que vale para la campaña. (a) **El silencio protector también es una decisión tomada en nombre de otro** — [[D-024]] atacó el gate que interrumpe de más y dejó sin nombrar el que no interrumpe nunca; las dos mitades del mismo error tardaron dos meses en aparecer juntas. (b) **Un gate escrito en un fork no es un gate**, y la revisión de [[D-045]] —que barrió features-first— no barrió a quién más le había pasado lo mismo: la clase de bug se arregló donde saltó, no donde vivía. (c) **Una decisión que difiere su propagación no se propaga**: [[D-024]] nombró el caso exacto ("spec validado") y aun así hicieron falta dos meses, una campaña de conformance y [[D-061]] para que alguien fuera a mirarlo. Por eso el mecanismo cambia: lo que se declare "principio general" para otras fases deja un **ítem abierto en `docs/ROADMAP.md`**, con dueño, no una frase de buena voluntad dentro de su propio texto.

**Referencias.** `sdd/pipeline/spec/skills/wf-spec-features-first/SKILL.md` (Paso 4b, Paso 5), `sdd/pipeline/spec/skills/wf-spec-fast-track/SKILL.md` (Paso 1, Paso 10), `sdd/pipeline/spec/skills/wf-spec-from-code/SKILL.md` (Paso 1, Paso 6), `sdd/pipeline/orchestration.md`, `sdd/docs/ROADMAP.md` (FASE 13), `sdd/tests/test_install_sh.py`, `sdd/CHANGELOG.md`.

---

## D-061 — El spec gana estado operativo: era el único eslabón del pipeline sin sello que consumir

- **Fecha:** 2026-09-09 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-028]]/[[D-032]] (el sello del PRD y su reapertura), [[D-024]] (**el precedente que se declaró general y no se heredó**), [[D-054]] (los dos hogares de un gap), [[D-037]] (nunca declarar limpio lo que no se ha parseado), [[D-051]], CU-3.f / CU-3.g.

**Contexto.** Comparando la fase PRD —cerrada— con la fase Spec, buscando normas que la primera estableció y la segunda no heredó. La más grave es un hueco **en mitad del pipeline**, con los dos vecinos resueltos:

| Fase | Estado en el artefacto | Quién lo lee | Se reabre al cambiarlo |
|---|---|---|---|
| **PRD** | `status: approved` + `Aprobado por:` | `sdd-prd-ready.py` | sí, determinista ([[D-028]]/[[D-032]]) |
| **Spec** | **nada** | — | — |
| **Plan** | `Estado: BORRADOR \| VALIDADO` | `sdd-gate-check.py` | — |

`wf-spec-validate` terminaba, literal: *"Imprime el informe directamente (**no escribe ningún archivo**)"*. Consecuencia: **nada distinguía un spec validado de uno que no había mirado nadie**. El gate de `wf-prepare-plan` comprobaba marcadores y `status_sync`, y la validación no entraba. Y como no había estado, tampoco había nada que reabrir cuando un delta o una enmienda lo cambiaban — lo que en el PRD es determinista desde [[D-028]].

La norma general **ya existía** y era Spec quien no la honraba: `orchestration.md` dice *"Cada fase consume artefactos **listos/sellados** de la anterior (PRD → Spec → Design → Plan → Tasks)"*. Spec simplemente no tenía sello que consumir.

**Decisión.**

1. **El spec lleva `Estado: BORRADOR | VALIDADO`** en su cabecera, y nace en `BORRADOR` — un spec recién generado no está auditado. Vale también para los de caracterización (`kb-spec-characterization`).
2. **El estado lo escribe un script, no un agente**: `sdd-seal.py spec <path> --check|--seal|--unseal`, con las mismas condiciones mecánicas que ya se exigían al spec origen de un plan (sin `[INCOMPLETO]`, sin críticos abiertos, sin `[INFERIDO]`, `status_sync` fiable, sin deriva de PRD) más una propia: **todo CA declara su HU padre**. Autor≠verificador: el veredicto experto del auditor no basta para sellar.
3. **`wf-spec-validate` invoca el sellador** y no escribe el estado a mano. Eso no rompe su read-only de [[D-051]]: ejecuta un verificador, no modifica el contenido que audita.
4. **Modificar un spec reabre su validación**: `wf-spec-delta apply`, `wf-spec-amend` y `wf-spec-gap-resolve` hacen `--unseal` tras escribir. Degradar siempre es seguro.
5. **El gate de `wf-prepare-plan` exige `VALIDADO`** — pero **solo si el spec declara el estado**: un spec legacy sin la línea no se bloquea (misma política conservadora que `status_sync`).

**Un callejón latente, encontrado al implementarlo.** El gate contaba `[CRÍTICO]` **en crudo**. Desde [[D-054]] un spec conserva en `## Items Pendientes` el bloque de sus gaps críticos **también después de responderlos**, por trazabilidad — así que responder un crítico dejaba la feature **bloqueada para siempre**. Ahora se cuentan los **abiertos** (bloque con `Respuesta: _(pendiente)_`).

Y al arreglarlo apareció el riesgo inverso, que la primera versión del arreglo introducía: si solo se cuentan bloques bien formados, **un crítico mal escrito se cuela** —justo la deriva de formato de [[D-058]]—. La síntesis, aplicando [[D-037]]: si hay marcas `[CRÍTICO]` **fuera** de un bloque reconocible, el gate **deniega** diciendo que no puede verificarlas. Nunca declarar limpio lo que no se ha sabido parsear.

**Alternativas descartadas.**

- **Que el auditor escriba `VALIDADO` él mismo.** Su veredicto es experto pero no verificable; el sello dejaría de ser una marca fiable. Es exactamente lo que [[D-032]] y el sellador de planes evitan.
- **Exigir `VALIDADO` siempre, también en specs sin la línea.** Rompería todo consumer con specs anteriores. La política de "solo si lo declara" es la misma que ya se usa con `status_sync`.
- **Un fichero de estado aparte.** El estado tiene que viajar con el artefacto: un `.json` paralelo se desincroniza y no sobrevive a un `git mv`.

**Consecuencias y aprendizaje.**

- **Una decisión que se declara "principio general" y difiere su propagación no se propaga.** [[D-024]] lo dice en su propio texto —*"no se propaga a las otras fases en este cambio, **se hereda al mantenerlas**"*— y nombra explícitamente al *"spec validado"*. Dos años de campaña después, no se había heredado. Una promesa sin dueño ni backstop no es un plan.
- **Los huecos se ven comparando fases, no auditando una.** Ninguna pasada de CU-3 lo habría encontrado: dentro de la fase Spec todo era coherente consigo mismo. Apareció al poner las tres columnas al lado.

**Referencias.** `scripts/sdd-seal.py` (modo `spec`), `scripts/sdd-gate-check.py` (`gate_spec_fiable`), `pipeline/spec/skills/wf-spec-validate/SKILL.md` (Paso 6), `wf-spec-delta`/`wf-spec-amend`/`wf-spec-gap-resolve` (reapertura), `spec_header_templates.md`, `kb-spec-characterization`, `tests/test_sdd_seal.py`, `tests/test_sdd_gate_check.py`.

---

## D-060 — El orquestador tampoco redacta artefactos, y hasta hoy eso no estaba escrito en ninguna parte que él cargue

- **Fecha:** 2026-09-08 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-038]] (**el precedente**: lo fija para el PRD), [[D-059]] (el defecto que lo destapó), [[D-031]] (la mitad de leer), [[D-051]] (`allowed-tools` no es enforcement), CU-3.a.

**Contexto.** Al arreglar [[D-059]] —el Paso 7 le pedía a main escribir el informe de conflictos— fui a comprobar si algo, a nivel general, se lo impedía. No lo hay.

La regla **eager** que el hilo principal siempre lleva cargada (`orchestration.md`) dice que **no lee** artefactos para diagnosticarlos ([[D-031]]) y **no dice nada de escribirlos**: cero coincidencias de "no escribe" / "nunca escribe" / "no escribas". Y [[D-031]], leída entera, trata **solo** de la lectura cualitativa y el diagnóstico sin `kb-*`; no menciona la escritura.

Peor: **dos sitios citan a [[D-031]] como si dijera eso** — `wf-spec-conflict` Paso 8 (*"main no escribe artefactos ([[D-031]])"*) y el propio agente `sdd-spec-auditor`. La norma se daba por establecida, se citaba con número, y **no existía**. Vivía como consenso: la "Regla de oro" de `wf-spec-features-first` dice *"no generas specs"* —solo specs, y solo mientras esa skill esté cargada— y el resto era costumbre.

**Precisión, tras comprobar las citas una a una:** la norma **sí existía**, pero acotada. [[D-038]] la fija con todas las letras —*"el hilo principal nunca escribe el artefacto"*— **para `wf-prd-review` y el PRD**. Lo que faltaba era generalizarla, exactamente el mismo movimiento que [[D-031]] hizo con [[D-030]] para la lectura: la mitad de leer se generalizó en su día y la mitad de escribir se quedó en la fase donde nació. Las citas a [[D-031]] son, entonces, cuatro documentos apuntando a la decisión equivocada de las dos.

Eso es lo que dejó sitio a [[D-059]]: una frase ambigua en un Paso de la fase Spec pudo interpretarse como encargo de escritura **porque ninguna norma general la contradecía** — la que lo habría hecho hablaba solo del PRD.

**Decisión.**

1. **El hilo principal no escribe contenido en un fichero del proyecto**: ni informes, ni consolidaciones de lo que le reportan sus delegados, ni resúmenes de apoyo. Queda en la regla **eager**, que es la que él siempre tiene.
2. **El motivo es la autoría, no la higiene**: cada artefacto tiene un autor declarado —el agente que lo produce dentro de su skill—, y eso es lo que lo hace auditable. Un informe firmado por quien no lo redactó pierde su autoría.
3. **Lo que necesite transmitir viaja en el prompt del siguiente delegado**, que no es un artefacto sin gobierno.
4. **La frontera es quién compone el texto.** Invocar un generador determinista que escribe ficheros (`sdd-features-index.py`, `sdd-sync-check.py seal`) **sí** es suyo: ahí no redacta, ejecuta, y el contenido lo deriva el script de sus fuentes de forma reproducible.
5. **Se corrigen las dos citas erróneas** a [[D-031]].

**Alternativas descartadas.**

- **Quitarle `Bash`.** Es su herramienta principal: con ella corre los verificadores mecánicos de los que depende todo el enrutado. Y no cerraría nada — [[D-051]] ya estableció que el candado es la norma, no la lista de herramientas.
- **Ampliar [[D-031]] en vez de crear una decisión nueva.** [[D-031]] responde a una pregunta distinta (quién diagnostica el contenido y con qué autoridad). Mezclarlas habría dejado el registro peor: parte de lo que se cita de [[D-031]] hoy es precisamente lo que no dice.

**Consecuencias y aprendizaje.**

- **Una norma citada no es una norma escrita — y una cita puede apuntar a la decisión equivocada.** **Cuatro** documentos invocaban [[D-031]] para la escritura; la que lo decía era [[D-038]], y solo para el PRD. Nadie lo comprobó, yo incluido: leí esa cita durante la investigación de [[D-059]] y la di por buena como prueba de que la norma general existía. **Al apoyarse en un `[[D-XXX]]`, hay que abrir la decisión y leer qué decide.**
- **Los huecos de este tipo no se ven arreglando el caso.** [[D-059]] quedaba cerrado con una frase; solo al preguntar *"¿y qué se lo impedía en general?"* apareció que no había nada. La pregunta que lo destapa es **"¿dónde está escrito, y lo carga quien tiene que cumplirlo?"** — la misma de [[D-055]].

**Referencias.** `pipeline/orchestration.md` (regla eager), `pipeline/spec/skills/wf-spec-conflict/SKILL.md` (Paso 8), `pipeline/spec/agents/sdd-spec-auditor.md`, `tests/test_install_sh.py`.

---

## D-059 — Un imperativo sin sujeto lo ejecuta quien lee: el orquestador escribió un artefacto porque se lo pedimos

- **Fecha:** 2026-09-08 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-047]] (el readiness arbitra), [[D-051]] (`allowed-tools` no es enforcement: un `cat >` escribe igual), [[D-045]] (la Regla de oro del orquestador), CU-3.a.

**Contexto.** Pasada 13 de CU-3.a. El orquestador escribió `spec/_conflict_report.md` —un artefacto que ningún contrato declara— consolidando los cuatro informes de conflicto de la tanda. Lo hizo con `cat >` por `Bash`, teniendo `allowed-tools: [Bash, Agent, AskUserQuestion]` **sin `Write`**: la misma puerta que [[D-051]] documentó para los auditores, ahora en el orquestador.

**Mi primer diagnóstico fue equivocado y conviene dejarlo escrito.** Lo llamé desviación tras leer el blockquote del Paso 7 (*"no eres el árbitro… lo que sí haces es recoger la divergencia y pasársela al Paso 8 en el prompt"*) y dar por hecho que el contrato decía lo contrario de lo que main hizo. No llegué al final del párrafo anterior, que termina así:

> *"**Emite las N llamadas en un único mensaje**, con el flag: igual que el Paso 5, es una barrera — el Paso 8 lee lo que escriben todas. **Escribe `_conflict_report.md` si hay conflictos.** Sin specs nuevos → omitir."*

Todas las demás frases de ese párrafo se dirigen a main —*"delega con la tool `Agent`"*, *"emite las N llamadas"*—, así que el imperativo `Escribe` cae sobre él. La intención al redactarlo era *"[cada auditor] escribe su `_conflict_report.md`"*; el sujeto se perdió y el lector asumió el único disponible: él mismo.

**Main no solo obedeció: reconcilió dos instrucciones contradictorias mejor de lo que estaban escritas.** Al ver que el blockquote le negaba el papel de árbitro, escribió una consolidación que **no arbitra**: se etiqueta a sí misma como tal, atribuye cada hallazgo al auditor que lo levantó, conserva las divergencias y nombra al readiness como quien decide. Y **además** pasó las divergencias en el prompt del readiness con un encargo de arbitraje explícito, que es lo que el blockquote pedía.

**Y aun así el paso hizo daño, medido.** Al transcribir cuatro informes ajenos **se equivocó de autor**: adjudicó el conflicto `C-A` al auditor de F-002 cuando lo habían levantado los de F-001 y F-005. Lo detectó el readiness al ir a las fuentes, y main corrigió el fichero. El sistema se salvó por tener un lector posterior que verifica, no por diseño de este paso.

**Decisión.**

1. **El informe de conflictos lo escribe cada auditor**, junto a su spec. El orquestador no escribe ninguno, y la frase lo dice con sujeto explícito.
2. **Prohibido consolidar informes en un fichero.** La divergencia viaja **en el prompt** del readiness —que no es un artefacto que nadie gobierne— y la vista consolidada con autoridad la produce el readiness.
3. **El motivo queda escrito junto a la prohibición**: consolidar obliga a copiar contenido que no produjiste, y copiar introduce errores que no estaban en el original.

**Alternativas descartadas.**

- **Sancionar el consolidado**: declararlo, darle plantilla y nombre determinista. Sería un quinto artefacto que duplica lo que ya está en cuatro ficheros más el readiness, sin sello, sin regenerador y sin nadie que detecte su deriva. Y no resuelve el error de transcripción — lo institucionaliza.
- **Dejarlo y anotar el defecto** para no reiniciar el recuento de CU-3.a. Sellar tres pasadas sobre un contrato que sabemos que pide algo indebido es sellar el defecto: las tres saldrían "en verde" produciendo cada una ese artefacto.

**Consecuencias y aprendizaje.**

- **Un imperativo sin sujeto lo ejecuta quien lee.** En un documento donde el lector es un agente con herramientas, *"Escribe X"* no es una descripción del sistema: es una orden para él. Al revisar un SKILL conviene leer cada verbo en imperativo preguntando **quién es el sujeto** — y si el sujeto es otro, nombrarlo.
- **Un contrato contradictorio no produce desobediencia: produce una síntesis.** Main no eligió una de las dos instrucciones ni se bloqueó; cumplió las dos como pudo. Eso hace que el defecto sea **difícil de ver en el resultado** —el fichero parecía razonable— y solo aparezca al preguntarse por qué existe.
- **Mi propio error tiene la misma forma que los que persigo.** Afirmé que el contrato decía lo contrario habiendo leído solo el fragmento que confirmaba mi hipótesis. Es el patrón de la nota de método de la pasada 9, otra vez.

**Referencias.** `pipeline/spec/skills/wf-spec-features-first/SKILL.md` (Paso 7), `conformance/casos-de-uso/cu-03-specs.md` (nota de la pasada 13), `tests/test_install_sh.py`.

---

## D-058 — La forma del bloque de gap es contrato, no estilo

- **Fecha:** 2026-09-08 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-037]] (la guarda que salvó la situación), [[D-042]] (`--answer` como única vía), [[D-054]] (el callejón), [[D-057]], CU-3.a.

**Contexto.** Pasada 12 de CU-3.a, la más limpia de la campaña. `registro-de-movimientos` escribió sus dos gaps locales como **lista de viñetas** —`- **[P-011][INFORMATIVO]** …` con los campos anidados— en vez de con el encabezado `### [P-011][INFORMATIVO]` que prescribe la SSoT. El contenido era correcto: contexto, pregunta, respuesta pendiente y asunción, todo bien redactado.

`sdd-analysis-gaps.py` **dejó de verlos**. Medido: `--list` devuelve cero gaps para ese spec, `--check` da `VACUOUS` con exit 2, y `--answer P-011` falla con exit 2 sin tocar el fichero.

**Lo que salvó la situación fue [[D-037]].** El script no dijo *"0 gaps abiertos"* —que habría sido una mentira tranquilizadora— sino *"no se ha podido parsear"*. La guarda que se escribió para que una regla no fuera vacua resultó ser la que impide que un fallo de formato se lea como un documento limpio. En esta pasada los gaps eran `[INFORMATIVO]`, así que no bloqueaban nada; **con un `[CRÍTICO]` ese gap habría quedado inalcanzable desde la vía sancionada**: el gate denegando el plan y el script incapaz de responderlo. Tercera vía posible hacia el callejón de [[D-054]], esta vez por el formato.

**Causa raíz, y es de contrato.** Dos huecos que se combinan:

1. **La plantilla solo cubría el caso crítico.** Su cabecera decía *"Este spec tiene gaps **críticos** sin resolver… el paso a planificación queda bloqueado"*. Dos de los cuatro escritores se encontraron con **solo informativos**, un caso que la plantilla no contempla. Uno adaptó la prosa y conservó la forma; el otro reescribió la sección entera y de paso cambió la forma del bloque.
2. **La SSoT nunca dijo que esa forma la parsea un script.** Describía el formato sin decir que era mecánico, así que un escritor podía razonablemente leerlo como estilo — igual que adaptó la cabecera, adaptó el bloque.

**Decisión.**

1. **La forma del bloque queda declarada contrato** en `kb-gap-conventions`, con lo que cuelga de ella (`--list`, `--check`, `--answer`) y con el fallo medido.
2. **La plantilla cubre los tres casos** —solo críticos, solo informativos, mixto— y da el bloque de un `[INFORMATIVO]` con su `Asunción por defecto`.
3. **Se dice explícitamente qué puede adaptar el escritor y qué no**: la prosa de la cabecera es suya; la forma del bloque, no.
4. **Si no hay gaps propios, la sección no se escribe**: ni sección vacía ni nota de "no hay nada".

**Alternativas descartadas.**

- **Hacer el parser tolerante a la forma de viñetas.** Aceptar dos formatos multiplica los casos del parser y no cierra el problema: mañana aparece un tercero. Y el formato canónico no tiene nada de incómodo — tres de los cuatro escritores lo respetaron sin esfuerzo.
- **Validar el formato en un gate.** Ya hay algo mejor: el propio `--check` devuelve `VACUOUS` y es ruidoso. El problema no era detectarlo, era que el escritor no sabía que importaba.

**Consecuencias y aprendizaje.**

- **Una plantilla incompleta no produce un hueco: produce improvisación.** El escritor no dejó la sección a medias — se inventó una entera, cabecera y formato incluidos. Al escribir una plantilla, la pregunta no es *"¿cubre el caso normal?"* sino *"¿qué hará quien se encuentre con lo que no cubre?"*.
- **Si una forma es mecánica, hay que decirlo donde se escribe.** Es la misma lección que [[D-055]] por otra puerta: la norma tiene que llegarle a quien actúa, en el momento de actuar, y aquí faltaba además el *por qué*.
- **[[D-037]] se cobró su seguro.** La guarda contra veredictos vacuos se escribió para otra cosa y es lo que convirtió esto en un fallo visible en vez de en un documento silenciosamente roto.

**Referencias.** `pipeline/spec/skills/kb-gap-conventions/SKILL.md` ("La forma del bloque de gap es contrato"), `pipeline/spec/skills/wf-spec-fast-track/references/spec_header_templates.md`, `tests/test_sdd_analysis_gaps.py` (la forma de viñetas falla ruidosamente), `tests/test_install_sh.py` (la plantilla cubre los tres casos).

---

## D-057 — Una asunción por defecto es una decisión de producto, y un gap tiene un solo sitio donde contestarse

- **Fecha:** 2026-09-08 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-054]] (los dos hogares), [[D-053]] (una decisión, una pregunta), [[D-042]] (quién escribe las respuestas), [[D-026]], CU-3.a / CU-3.b.

**Contexto.** Dos hallazgos de la pasada 11 de CU-3.a que comparten raíz: **qué se le enseña a la persona que tiene que decidir**.

**1 — Los `[INFORMATIVO]` se deciden solos y nadie los ve.** El análisis salió con 4 informativos abiertos, uno de ellos `[P-007][INFORMATIVO][PUEDE_REQUERIR_CR]`. El orquestador cerró los 3 críticos, comprobó el flag y razonó —correctamente según el contrato— que *"P-007 lo lleva, pero es informativo y sin responder: aplicará su asunción por defecto, así que no hay disparador de cambio de producto"*. Y siguió.

El razonamiento es impecable y el resultado es un agujero. La asunción por defecto es la opción **conservadora**, así que aplicarla no expande el producto: por ese lado no hay riesgo. El problema es el otro: el flag `PUEDE_REQUERIR_CR` existe para declarar que **la respuesta podría mover el producto**, y al no preguntar nunca, el sistema **garantiza que esa vía de gobernanza no se recorre jamás** — no porque alguien eligiera lo conservador, sino porque nadie se lo planteó. La decisión se toma en nombre del usuario y queda anotada solo dentro de un documento que el ecosistema le dice que no necesita abrir. Si resulta que las tarjetas de crédito sí necesitan ciclo de facturación, se descubre con el spec escrito y el plan hecho.

**2 — Un gap con dos bloques respondibles.** `account-management_spec.md` heredó `[P-007]` del análisis y lo reprodujo entero en sus `## Items Pendientes`, con su propio `- **Respuesta**: _(pendiente)_`. El writer hizo lo cuidadoso: declaró la herencia (*"heredado del análisis del PRD (`prd/prd_analysis.md`)"*) y anotó la asunción aplicada en `Asunciones Aplicadas`. Pero el resultado son **dos sitios donde contestar la misma pregunta**: responder en el análisis deja la copia del spec en `_(pendiente)_` para siempre, y los dos documentos acaban diciendo cosas distintas sobre la misma decisión. No fue descuido — la regla no existía.

**Decisión.**

1. **Un gap tiene UN solo bloque respondible**, y lo que lo hace respondible es el campo `Respuesta`. `## Items Pendientes` es **solo** para los gaps que nacen al escribir ese spec; uno heredado del análisis se **referencia** en `## Asunciones Aplicadas` —ID, fichero y asunción aplicada— **sin** campo `Respuesta`.
2. **La asunción se enseña verbatim, no se resume.** `sdd-analysis-gaps.py --list --json` emite el campo `asuncion` junto a `contexto`, `problema` y `afecta`. Sin él, quien presenta el gap tendría que redactarla de su cosecha, que es lo que el contrato verbatim existe para impedir.
3. **Tras cerrar los críticos, una pregunta más**: *repasar los informativos* o *aplicar sus asunciones y seguir*, con las asunciones listadas en una línea cada una **antes** de preguntar. Una sola pregunta para toda la tanda — misma forma que [[D-053]], mismo motivo.
4. **Los `PUEDE_REQUERIR_CR` se surfacean siempre**, incluso si declina repasar el resto.
5. **Confirmar una asunción se escribe** con `--answer` y el texto de la asunción. `_(pendiente)_` significa *nadie lo ha mirado*; una respuesta significa *alguien lo decidió*.

**Alternativas descartadas.**

- **Presentar los informativos como los críticos, uno a uno y sin preguntar antes.** Devuelve exactamente la fatiga que [[D-053]] quitó: aquí serían 7 decisiones en vez de 1, y la mayoría de las asunciones son buenas.
- **Bloquear el paso mientras haya informativos abiertos.** Convierte en crítico lo que por definición no lo es, y el pipeline dejaría de avanzar por preferencias menores.
- **Que main redacte la asunción al presentarla.** Es lo que pasa hoy si el script no la emite, y es un resumen de un texto que existe: el mismo defecto que [[D-053]] arregló para `contexto` y `problema`.

**Consecuencias y aprendizaje.**

- **"El contrato lo permite" y "el usuario lo sabe" son cosas distintas.** El orquestador razonó bien sobre el contrato y aun así el usuario se quedó sin enterarse. Cuando un flag existe para abrir una vía, hay que preguntarse **quién la abre y cuándo**, o el flag decora.
- **Cuidado con el defecto que nace de hacer las cosas bien.** El writer duplicó el gap **por ser riguroso con la trazabilidad**. La regla no dice "no lo menciones": dice dónde va lo que quería dejar dicho.

**Referencias.** `scripts/sdd-analysis-gaps.py` (`LIST_FIELDS`, campo `asuncion`), `pipeline/spec/skills/wf-spec-features-first/SKILL.md` (punto 6c), `pipeline/spec/skills/wf-spec-fast-track/SKILL.md` (Paso 6), `pipeline/spec/skills/kb-gap-conventions/SKILL.md` ("Dónde vive un gap", "Convenciones para Asunción por defecto"), `tests/test_sdd_analysis_gaps.py` (3 backstops).

---

## D-056 — En un fan-out, los IDs los reparte quien lanza; y un marcador nombra el fichero donde vive el gap

- **Fecha:** 2026-09-08 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-054]] (los dos hogares de un gap), [[D-047]] (la barrera del fan-out), ROADMAP 11.2b, CU-3.a / CU-3.g.

**Contexto.** Pasada 11 de CU-3.a, la más limpia de la campaña en conducta (11/11 delegaciones con el flag, los dos fan-outs en un mensaje, `spawnDepth: 1` en los once). Precisamente por funcionar bien destapó dos defectos que solo aparecen cuando **cuatro escritores trabajan a la vez**.

**Defecto 1 — la colisión de IDs dejó de ser teórica.** `movement-tracking` reclamó `[P-009][INFORMATIVO]` y `debt-tracking` `[P-009][CRÍTICO]`: gaps distintos, mismo ID, specs distintos. [[D-054]] lo había **declarado como límite conocido** —*"en un fan-out paralelo dos specs hermanos pueden reclamar el mismo `P-XXX`"*— con el argumento de que no corrompe la resolución porque se busca primero en el spec. Ese argumento sigue siendo cierto: el readiness lo diagnosticó, citó la SSoT y propuso la renumeración. Lo que estaba mal era la **estimación de frecuencia**: ocurrió en la primera pasada paralela siguiente, con solo 4 escritores. Un límite que se cumple siempre no es un límite aceptable.

**Defecto 2 — el marcador `[INCOMPLETO]` mandaba al fichero equivocado.** `debt-tracking_spec.md` salió con *"Pendiente de gap(s): [P-009]. Responde ese gap en el `_analysis.md`"* — y `[P-009]` vivía en el `## Items Pendientes` de ese mismo spec. La frase manda al usuario a un fichero donde el gap no existe: **el callejón de [[D-054]] otra vez**, ahora por la vía del texto en lugar de la de las herramientas. El writer no se desvió: copió la plantilla canónica de `kb-gap-conventions`, que hardcodeaba `_analysis.md`.

**Decisión.**

1. **El reparto de IDs sube al orquestador.** `wf-spec-features-first` pide el primer ID libre del linaje **antes** del fan-out y asigna a cada escritor un **bloque de 10** vía `--gap-id-start`. Es el único punto que ve a todos los hermanos a la vez; el escritor, por construcción, no puede.
2. **`--gap-id-start` manda sobre cualquier cálculo propio.** Si llega, el escritor no recalcula: el script no ve los specs que se están escribiendo ahora mismo, así que su respuesta sería peor que el dato que le dieron.
3. **Los huecos entre bloques quedan sancionados.** La SSoT decía *"sin saltos"*; ahora exceptúa los bloques reservados. Un ID sin usar no cuesta nada; dos gaps distintos con el mismo ID corrompen la trazabilidad.
4. **La plantilla del marcador nombra el hogar del gap**, con las tres formas: la ruta del análisis, la sección del propio spec, o ambas con sus IDs cuando el marcador cruza los dos.

**Alternativas descartadas.**

- **Dejarlo como límite documentado.** Era la postura de [[D-054]] y la evidencia la tumbó: se cumple en la pasada siguiente, no en un caso raro.
- **Que cada escritor bloquee un fichero de IDs.** Coordinación por disco entre agentes paralelos, con su carrera y su fichero de estado que limpiar. El orquestador ya tiene la información sin nada de eso.
- **Renumerar después, al detectar la colisión.** Es lo que propuso el readiness, y como remedio está bien — pero exige reescribir specs ya sellados y sus referencias cruzadas. Prevenir cuesta una línea en el prompt de delegación.

**Consecuencias y aprendizaje.**

- **Declarar un límite no es cerrarlo, y la frecuencia estimada es parte de la decisión.** Escribí *"no corrompe nada"* y era verdad para la resolución; lo que no evalué es cada cuánto pasaría. Un riesgo aceptable que ocurre siempre deja de serlo.
- **Un defecto arreglado en las herramientas puede seguir vivo en la prosa.** [[D-054]] arregló `wf-spec-gap-resolve`, la SSoT y el mensaje del gate — y dejó intacta la línea que el writer **copia**, tres párrafos por encima de una nota que discutía esa misma línea por otro motivo. Al cerrar un defecto conviene preguntar **qué plantillas repiten la suposición vieja**.
- **Un fan-out que funciona bien es el que destapa los defectos de concurrencia.** Las pasadas anteriores no llegaron a generar cuatro specs a la vez; esta sí, y por eso vio lo que ninguna había visto.

**Referencias.** `pipeline/spec/skills/wf-spec-features-first/SKILL.md` (Paso 5.0), `pipeline/spec/skills/wf-spec-fast-track/SKILL.md` (Paso 1 y Paso 6), `pipeline/spec/skills/kb-gap-conventions/SKILL.md` ("Formatos de ID" y "Marcador de HU incompleta"), `conformance/casos-de-uso/cu-03-specs.md` (nota de la pasada 11).

---

## D-055 — Una regla de fase no puede gobernar lo que se escribe desde cero: llega con el `Write`, no antes

- **Fecha:** 2026-09-07 · **Estado:** Adoptada (medida en la pasada 10). · **Relacionada:** ROADMAP 11.10 (causa A, que esta entrada **corrige parcialmente**), [[D-051]], CU-3.a.

**Contexto.** La pasada 9 midió que las **3** ejecuciones de `sdd-spec-explorer` corrieron sin la guía de fase Spec cargada, mientras escritores y auditores sí la tenían. Lo atribuí a los `paths:`: `*_analysis.md` y `*_discovery.md` solo estaban en los globs de la fase PRD. Se añadieron a los de Spec en v0.91.0 (causa A).

**Lo que la pasada 10 midió, y corrige ese diagnóstico.** Con los globs ya arreglados, el explorer **volvió a correr sin la guía de Spec**. El transcript dice por qué, y es mecánico:

| línea | evento |
|---|---|
| 1 | entra `kb-spec-expert` (inyectada por el `skills:` del agente) |
| 14 | `Read` del `SKILL.md` de `wf-spec-analyze` |
| 29 | `Read prd/prd.md` |
| **33** | **se inyecta la guía de fase PRD** — cuatro líneas después de tocar un path que matchea |
| 44 | `Write prd/prd_analysis.md` ← primer y único contacto con un path de los globs de Spec |
| 48 | fin del transcript |

**Una regla de `.claude/rules/` se carga cuando tocas un fichero que matchea sus globs.** Para un agente que **genera** un artefacto desde cero, ese momento es el `Write` **final**: el contenido ya está compuesto. La guía no puede influir en lo que escribe **por muchos globs que se le añadan**. Para un agente que **edita** —lee el spec y luego lo modifica— sí llega a tiempo, y por eso escritores y auditores la tenían.

**Decisión.**

1. **La norma de forma de los artefactos vive en `kb-spec-expert`**, que los tres agentes de Spec cargan por su `skills:` y entra en la **línea 1** del contexto, antes de cualquier tool call. Es el único carril fiable para quien escribe desde cero.
2. **Redundancia deliberada, en tres carriles**: la `kb-*` (siempre, y a tiempo), la instrucción de rol de cada skill que redacta (en el punto donde compone), y la guía de fase (para quien edita artefactos existentes). No es duplicación por descuido: cada carril cubre un caso que los otros no alcanzan.
3. **La guía de fase deja de prometer lo que no puede cumplir.** Su cabecera decía que la sección *"vincula a todo el que escriba uno"*; ahora dice cuándo llega y cuándo no.
4. **El arreglo de v0.91.0 no se revierte**: sigue siendo correcto y necesario para los editores. Lo que cambia es que deja de ser *la* causa y pasa a ser *una* de dos.

**Alternativas descartadas.**

- **Más globs.** Es la reacción inmediata y no puede funcionar: el problema no es qué paths matchean, es **cuándo** se evalúa el match.
- **Copiar la norma en las 6 skills que escriben y no la tienen.** Seis copias que divergen a la primera edición. La `kb-*` la sirve una vez a los tres agentes.
- **Un `kb-*` nuevo solo para esto.** Un fichero más que cargar en cada agente para tres párrafos que son, literalmente, calidad de artefacto — que es de lo que trata `kb-spec-expert`.

**Consecuencias y aprendizaje.**

- **Un diagnóstico que explica los datos no es por eso el correcto.** "Los globs no cubren el fichero" explicaba perfectamente los 0 hits de la pasada 9, era verdad, y aun así no era la causa operativa. Lo que lo destapó fue **volver a medir después de arreglar** en vez de dar el arreglo por bueno.
- **Los probes de conformance pueden pedir lo imposible.** El check "¿cargó el agente la guía de su fase?" es inalcanzable por construcción para un generador. Un probe así reporta FALLO donde no lo hay — el mismo daño que un probe vacuo, en el otro sentido. Reescrito en CU-3 para distinguir generador de editor.
- **Confirma por qué el arreglo de la causa B era el que funcionaba.** La norma en el `SKILL.md` se lee en la línea 14; por eso la pasada 10 salió con el análisis limpio de jerga y de comandos mientras la guía de fase no había llegado.

**Referencias.** `pipeline/spec/skills/kb-spec-expert/SKILL.md` (sección "Lo que escribes en un artefacto lo lee una persona"), `pipeline/spec/CLAUDE.md` (cabecera de audiencia), `conformance/casos-de-uso/cu-03-specs.md` (V3 de la verificación transversal, nota de la pasada 10), `install.sh` (los globs de v0.91.0, que se mantienen).

---

## D-054 — Un gap tiene dos hogares posibles, y se resuelve donde está definido

- **Fecha:** 2026-09-07 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-042]] (quién escribe las respuestas y con qué vía), [[D-051]] (misma familia: el defecto vive en la costura entre dos workflows), ROADMAP 11.2b (`sdd-next-id.py`), CU-3.a / CU-3.b.

**Contexto.** Medido en conformance (pasada 9, 2026-09-07). Una feature quedó con 4 HUs `[INCOMPLETO]` por un gap `[P-011]` que **no existe en el `_analysis.md`** (que llega hasta `P-008`): lo levantó el writer del spec y lo definió en el `## Items Pendientes` de ese spec.

El writer **no se desvió**: `wf-spec-fast-track` Paso 6 se titula literalmente *"Gap handling inline"*, dice *"No genera un `_analysis.md` separado… los gaps se gestionan directamente en el spec"* y su línea 82 remata: *"Si el inline analysis detecta un gap que no existe en el analysis previo → **créalo normalmente**"*. Tampoco tenía otro sitio: meter un gap en `prd/prd_analysis.md` sería escribir en el artefacto de otra fase, que [[D-042]] reserva a `--answer`.

Y el gap era de una clase que el análisis **estructuralmente no puede contener**: **de segundo orden**. Nació del cruce de dos respuestas —una fijó una relación 1:1, la otra introdujo 1:N— y el cruce ("¿y si cambias el importe cuando hay reparto?") no existía cuando se escribió el análisis, porque las respuestas no existían. El análisis se deriva del **PRD**; ese gap se deriva de las **respuestas**.

**El defecto estaba en el otro extremo de la costura.** `wf-spec-gap-resolve` ya leía el spec para sacar los `[P-XXX]` referenciados, pero buscaba **todas** las respuestas en el `_analysis.md`, y su check de cierre corría contra el análisis. Con el análisis en `CRITICAL_ANSWERED, 0 abiertos`, habría concluido *"no queda nada que resolver"* mientras el gate seguía denegando el plan de esa feature: **callejón sin salida**, con el gate correcto y la vía sancionada sin alcanzar el gap.

**Causa raíz de la deriva:** `kb-gap-conventions` —la SSoT de marcadores— **no mencionaba `Items Pendientes` ni una vez**. Sin definición compartida, cada skill asumió su fuente.

**Decisión.**

1. **Un `[P-XXX]` tiene dos hogares legítimos:** el `_analysis.md` del documento origen, o el `## Items Pendientes` del propio spec cuando el gap nace al escribirlo. Queda definido en la SSoT, con la tabla de quién escribe en cuál.
2. **La doble ubicación es forzosa, no una comodidad.** `--analysis` es opcional en `wf-spec-fast-track`: en modo directo (`--capability`) y en todo el onramp brownfield de `wf-spec-from-code` **no hay analysis en absoluto**. Centralizar los gaps en el análisis dejaría a esas dos entradas del pipeline sin sitio donde ponerlos.
3. **Se resuelve donde está definido el bloque**: se busca primero en el spec, luego en el análisis; la respuesta se escribe **en ese fichero**, con `--answer` apuntado a él. El script ya es agnóstico al documento — parsea cualquier fichero con bloques de gap—, así que no hubo que tocarlo.
4. **El check de cierre corre en los dos hogares.** Un `--check` contra el análisis **no dice nada** sobre los gaps que viven en el spec.
5. **La numeración pasa a ser por LINAJE** (el análisis más todos los specs derivados de él), no *"reiniciando en cada artefacto nuevo"* como decía la SSoT. El ID se pide a `sdd-next-id.py` pasándole todos los ficheros del linaje — ya acepta varios.
6. **La norma se le dice al writer donde numera**, no solo en la SSoT. `wf-spec-fast-track` Paso 6 gana la instrucción en línea —simétrica a la que ya tenía el `F-NNN` del Paso 9 (*"no lo cuentes a mano"*)—, porque quien asigna el ID es él y en ese punto no estaba escrito que hubiera que pedírselo al script.
7. **La garantía tiene un límite, y se declara.** El linaje se calcula sobre lo que hay **en disco**: en un fan-out paralelo dos fast-tracks hermanos pueden reclamar el mismo `P-XXX` sin verse. El invariante que sí se garantiza —y el único que hace falta— es que dentro de un mismo spec ningún gap propio comparta ID con uno de su análisis. Consecuencia: un `P-XXX` **no identifica un gap fuera de su spec**, así que al citarlo se nombra junto a su fichero (que es justo lo que [[D-054]] ya obliga a hacer al reportar gaps pendientes).

**Alternativas descartadas.**

- **Prohibir los gaps locales del spec y obligar a que todo viva en el análisis.** Es la reacción intuitiva y es inviable: rompe el modo directo de fast-track y el brownfield entero, que corren sin análisis. Además obligaría al writer a escribir en el artefacto de otra fase.
- **Dejar que `gap-resolve` fusionara ambos ficheros en una vista única.** Más código para el mismo resultado, y borra la distinción que importa al escribir la respuesta: hay que saber **en qué fichero** se sustituye el `_(pendiente)_`.

**Consecuencias y aprendizaje.**

- **Cuando dos skills comparten un artefacto, la SSoT tiene que nombrarlo.** `Items Pendientes` existía en el contrato de quien escribe y era invisible para el contrato de quien lee. Eso no es un descuido de redacción: es la firma de la familia [[D-051]] —el defecto vive en la costura— y se detecta preguntando, por cada sección que una skill produce, **quién la consume**.
- **Una regla que la práctica contradice y acierta es una regla mal escrita.** La SSoT decía *"reiniciando en cada artefacto"*; el writer continuó la numeración por su cuenta y evitó una colisión que la regla habría provocado. Se alineó la regla con la práctica, no al revés.
- **Barrido colateral:** los **12** mensajes de denegación de `sdd-gate-check.py` llevaban slash-commands. Son los mensajes que el usuario ve en **cada gate bloqueado** —la superficie más visible de ROADMAP 11.10— y ninguna regla de linter llega a un script.

**Referencias.** `pipeline/spec/skills/kb-gap-conventions/SKILL.md` (secciones "Formatos de ID" y "Dónde vive un gap"), `pipeline/spec/skills/wf-spec-gap-resolve/SKILL.md` (Pasos 2, 3 y 7), `pipeline/spec/skills/wf-spec-fast-track/SKILL.md` (Paso 6), `scripts/sdd-gate-check.py`, `tests/test_sdd_analysis_gaps.py` (3 backstops, incl. el callejón reproducido), `tests/test_sdd_next_id.py` (2 backstops de linaje).

---

## D-053 — Una decisión se pregunta una vez; una respuesta abierta no se pide con un selector

- **Fecha:** 2026-09-04 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-042]] (quién escribe las respuestas, y "no basta con decir responde los pendientes"), [[D-052]] (de la que corrige el menú y amplía `--list`), [[D-031]] (main no lee artefactos), [[D-002]] (un fork no puede preguntar), CU-3.a paso 4.

**Contexto.** [[D-052]] reconstruyó el menú del gate de gaps críticos en un solo eje y lo dio por bueno **sin haberlo visto en pantalla**. Al ejercitarlo por primera vez en una pasada real (2026-09-04) aparecieron dos defectos que el texto del contrato no dejaba ver:

1. **El menú se presentaba una vez por gap.** Con 4 críticos abiertos, el usuario tenía que decidir cuatro veces *dictar / escribir / continuar* antes de poder responder nada. El propio menú lo delataba: la tercera opción tenía que aclarar *"(aplica a los 4 gaps críticos, no solo este)"* — una opción de ámbito global dentro de una pregunta de ámbito individual. **Cuando una opción necesita explicar que no va con su propia pregunta, la pregunta está en el sitio equivocado.**
2. **La respuesta se pedía con `AskUserQuestion`.** Una respuesta de gap es **prosa abierta**: no hay opciones que elegir, así que el camino principal acababa siendo la escotilla *"Other → escribe algo"* del selector. Y el daño no era solo de fricción: **la pantalla del selector no tiene sitio para `Contexto` ni `Problema`**, los dos campos que dicen *por qué* importa el gap y *cuánto* detalle hace falta. Medido: al usuario le llegó la pregunta pelada y los dos campos se tiraron.

**Decisión.**

1. **La decisión se pregunta una vez, para toda la tanda.** Un solo `AskUserQuestion` con las tres vías. Antes de preguntar, main da el path, el recuento y **los IDs con su título**, para que se vea el alcance **antes** de elegir cómo responderlo.
2. **El detalle se trae solo en la rama de dictar, y de uno en uno.** Si elige escribir en el fichero o continuar aceptando el riesgo, **no se pide nunca**: el gate se arma con el recuento de `--check`. Y traer los N gaps de golpe metería media prosa del informe en el contexto de main por la puerta de atrás — lo mismo que la Regla de oro evita. De ahí `--list --gap <P-XXX>`.
3. **Los gaps se presentan en la conversación, no con un selector**: ID, `contexto`, `problema`, `afecta` y la pregunta, **verbatim**; el usuario responde en texto libre; main aplica con `--answer`.
4. **`--list` emite `contexto`, `problema` y `afecta`** además de la pregunta. Es lo que hace (3) posible sin abrir el artefacto.
5. **Uno a uno por atribución, no por comodidad.** Presentar los N juntos obliga a **repartir** un bloque de texto entre N IDs, y repartir es interpretar una respuesta que el usuario no dio literalmente — el FALLO del paso 4 de `CU-3.a`. Gap a gap la atribución es inequívoca por construcción.

**Alternativas descartadas.**

- **Que un `sdd-spec-explorer` lea el análisis y le reporte los gaps a main** (propuesta del usuario, y no es mala: es el patrón del ecosistema, y es exactamente lo que [[D-052]] hizo para la evaluación de gobernanza). Descartada aquí por tres razones. **Fidelidad:** main es un **relé** hacia la pantalla, no razona sobre el contenido; un agente al que le pides "reporta los gaps" **resume** —es lo que hacen los agentes— y una pregunta resumida se contesta peor, que es contra lo que se construyó [[D-042]]. Una extracción verbatim no tiene ese modo de fallo. **Coherencia:** la pregunta ya salía del script; tener la pregunta del script y su contexto de un agente son dos fuentes para el mismo bloque del mismo fichero. **Coste:** una invocación de subagente con su KB cargada para extraer tres campos que el parser **ya recorre**. El criterio que queda escrito: **delegar donde hace falta criterio, extraer donde hace falta exactitud.**
- **Dejar el menú por gap y solo arreglar la opción 3.** Trata el síntoma. El problema es el ámbito de la pregunta, no la redacción de una opción.
- **Presentar los N gaps juntos y pedir respuestas prefijadas por ID.** Traslada al usuario la carga de un formato para que main no tenga que interpretar. Si el formato se incumple —y se incumple— volvemos al reparto.

**Consecuencias y aprendizaje.**

- **Un menú no está validado hasta que se ve en pantalla.** [[D-052]] lo rediseñó sobre el texto y lo dio por cerrado; los dos defectos solo se vieron al presentarlo. Es el mismo aprendizaje que [[D-038]]: lo que el contrato dice que existe y lo que el usuario acaba viendo son cosas distintas, y solo una de las dos se puede medir leyendo.
- **`AskUserQuestion` tiene un dominio: elegir entre opciones.** Cuando el input es prosa abierta, el selector no es una comodidad — es una amputación del enunciado, porque su pantalla no tiene sitio para el contexto que hace la pregunta contestable. Criterio de autoría a aplicar en el resto del ecosistema.
- **La pasada que lo encontró se gasta.** Cambiar `wf-spec-features-first` reinicia los recuentos conductuales del escenario que lo mide; se asume y se reinicia la serie.

**Referencias.** `pipeline/spec/skills/wf-spec-features-first/SKILL.md` (Paso 2.5, puntos 4, 6 y 6b), `scripts/sdd-analysis-gaps.py` (`--list` ampliado, `--gap`), `tests/test_sdd_analysis_gaps.py` (5 casos nuevos), `conformance/casos-de-uso/cu-03-specs.md` CU-3.a pasos 2-4.

---

## D-052 — El orquestador no lee respuestas: enruta por el flag. Y una vía sancionada que vive escondida en la descripción de otra opción no existe

- **Fecha:** 2026-09-02 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-026]] (el override lo arma el usuario), [[D-031]]/[[D-042]] (quién lee y quién escribe), [[D-038]] (el vacío de la vía no ofrecida), [[D-048]] (frontera de `Bash`), [[D-051]] (de la que esto es la parte que se quedó fuera), ROADMAP 11.10 y 11.11.

**Contexto.** Tres defectos que comparten superficie —el Paso 2.5 de `wf-spec-features-first`— y una causa: **el contrato pedía cosas que main no puede hacer sin romper su propia Regla de oro**.

1. **El menú del gate escondía una vía sancionada.** Desde [[D-042]] el usuario puede **dictar** las respuestas y que main las aplique con el script. Pero eso vivía **dentro de la descripción de la opción "Responderlos primero"**, y una descripción se resume al presentarla: la vía desaparecía de la pantalla. Es la forma exacta del vacío que cerró [[D-038]] en la fase PRD — una ruta que el contrato contempla y que nadie llega a ofrecer.
2. **En sesión nueva, el Paso 2.5 era inejecutable.** Sus puntos 4 y 8 decían *"léelo para lo que sí es juicio"* e *"inspecciona las respuestas ya resueltas"*, en contradicción directa con la Regla de oro del mismo SKILL. No se notaba porque en el caso habitual las respuestas te las dicta el usuario y ya las tienes en contexto. Pero el caso normal de verdad es el otro: los gaps se responden un martes y se sigue el jueves. Medido en conformance (2026-09-02): sesión nueva, main sin el texto de ninguna respuesta, y la única forma de "inspeccionarlas" era abrir el fichero.
3. **`--list` se citaba y no existía.** El SKILL decía *"las preguntas salen del informe del delegado o de `--list`"*. Comprobado: el script solo aceptaba `--check` y `--answer`. Referencia colgante — y encima la que habría tapado el agujero de (2).

**Decisión.**

1. **`sdd-analysis-gaps.py --list`** emite los gaps con **su pregunta**: id, severidad, flags, título, pregunta y si está respondido. **No** emite el texto de las respuestas (para eso está `--export-answers`). Es la vía sancionada para armar el gate sin abrir el artefacto.
2. **El menú del gate pasa a un solo eje —cómo se responde— con la vía de dictar como opción propia:** *"Me los dictas aquí"* / *"Los escribes tú en el fichero"* / *"Continuar aceptando el riesgo"*. *"Responder solo algunas"* desaparece: mezclaba **cuántas** con **dónde**, y responder parcialmente ya funciona en las dos primeras.
3. **Main no juzga respuestas: enruta por el flag y delega.** El `PUEDE_REQUERIR_CR` que el analyze puso en el gap es el disparador. Si hay alguno respondido, main **delega la evaluación de gobernanza** al `sdd-spec-explorer` —que sí tiene el PRD y el análisis delante— y presenta el gate **citando el informe del delegado, no su lectura**. Esto codifica lo que un run real ya hizo por su cuenta.
4. **`Origen de alcance` gana criterio binario** ([[D-051]] lo dejó ambiguo): `PRD` salvo que el alcance de esa feature **solo** exista en una respuesta del análisis. Regla de coherencia autocomprobable: `PRD + analysis respondido` y `Avisos de gobernanza: ninguno` no pueden ir juntos.
5. **`SendMessage` queda sancionado como tercera vía de delegación, con su propia forma de esperar.** Reanudar un delegado es mejor que relanzarlo, pero su `tool_result` es **un acuse**, no el informe: hay que ceder el turno igual que en la vía (b). Y un agente reanudado **puede haber perdido contexto**: las referencias se le dan en el mensaje, no se asumen.
6. **Regla de linter `USER-FACING-COMMAND` [warning]** + barrido completo de la fase Spec (**30 → 0**). Un mensaje dictado al usuario no lleva comandos.

**Alternativas descartadas.**

- **Darle el PRD a main para que juzgue las respuestas.** Rompe [[D-031]] a cambio de duplicar un chequeo que ya existe aguas abajo, y encima peor: main juzgaría sin las `kb-*` del experto.
- **Un cuarto punto en el menú ("¿dónde las escribes?") tras elegir "responderlos primero".** Es una segunda ronda de `AskUserQuestion` para una pregunta que cabe en el mismo menú.
- **Que `--list` emitiera también las respuestas.** Mezcla dos propósitos y le pone a main en contexto justo lo que no debe leer.
- **Hacer `USER-FACING-COMMAND` blocking.** La señal es de forma, no de semántica, y la propia regla tiene excepción legítima ("si el usuario pide el comando, se le da"). Warning con recuento que debe bajar.

**Aprendizaje.**

**Una opción de menú es lo que se ve, no lo que está escrito.** Si una vía solo vive en la descripción de otra, no existe para el usuario. Al diseñar un gate, cada camino que quieras que alguien pueda tomar necesita **su propia línea**.

**Y el segundo, que es de método mío.** Al re-alcanzar [[D-051]] alrededor de seis hallazgos nuevos, estos tres puntos —que ya estaban acordados— se cayeron sin que nadie lo dijera. Los detectó el usuario al ver el gate en pantalla. Cuando una decisión cambia de alcance, lo que sale del alcance hay que **nombrarlo al salir**, no dejar que se evapore.

---

## D-051 — Un read-only no se declara quitando `Write`, y regenerar un análisis no puede llevarse por delante las respuestas

- **Fecha:** 2026-09-01 · **Estado:** Adoptada (pendiente de medir). · **Relacionada:** [[D-030]]/[[D-031]] (main no lee ni escribe artefactos), [[D-038]] (`allowed-tools` no es enforcement — esto es su corolario), [[D-042]] (quién escribe las respuestas de los gaps), [[D-048]] (frontera de `Bash`), ciclo de CU-7 del 2026-08-31/09-01.

**Contexto.** Cuatro cambios de producto encadenados sobre un PRD real (`CR-001`…`CR-004`, v1.0 → v1.5) con sus reviews, su ronda de asunciones —una **rechazada** por el usuario y honrada— y su análisis de impacto. El ciclo funcionó de punta a punta: 14 de 14 delegaciones síncronas, cero clones, 21 `AskUserQuestion`. **Ninguno de los seis defectos encontrados fue de conducta del agente: los seis eran huecos del contrato**, y cinco de los seis en las costuras entre workflows.

**Los dos que dan nombre a esta decisión.**

**1. El read-only del auditor era ficción.** `sdd-spec-auditor` declara `disallowedTools: Write, Edit`, y tres skills que lo tienen como `agent:` declaraban a la vez `allowed-tools: [Read, Write, Bash]`. Manda el agente, así que ese `Write` no habilitaba nada — pero el agente **conserva `Bash`**, y un `cat > fichero` escribe igual de bien. Medido: con el **mismo** frontmatter, los auditores de `wf-spec-conflict` y `wf-spec-readiness` escribieron su informe con `cat >`, y el de `wf-prd-sync-impact` concluyó que no podía y le pasó la escritura al hilo principal, que volcó el artefacto con un heredoc — violando [[D-031]] y firmando como suyo un texto que no redactó. Contrato contradictorio, conducta inconsistente.

**2. Regenerar el `_analysis.md` destruye las respuestas.** `wf-spec-analyze` Paso 7 preguntaba *"¿deseas regenerarlo?"* y, con un sí, sobrescribía. Dentro había cuatro decisiones de negocio de una persona. Y no es un caso raro: un PRD cambia **después** de que alguien responda sus gaps — es el caso normal, con un `wf-prd-change` de por medio. En el ciclo medido, main improvisó un rescate (copia al scratchpad, extracción con python, re-aplicación con `--answer`) y salió impecable. **Ese es el problema:** dependió por completo de que se le ocurriera.

**Decisión.**

1. **`allowed-tools` no declara lo que el `agent:` prohíbe.** Las cuatro skills afectadas pasan a `[Read, Bash]` (`[Read, Bash, Agent]` en `wf-sdd-audit`) y su cuerpo dice **con qué vía se escribe el informe**: redirección por `Bash`, nunca delegando la escritura a main. Regla de linter nueva **`AGENT-TOOL-CLASH` [blocking]**; delta demostrado **4 → 0** (cazó una que el barrido a mano no vio).
2. **El invariante se escribe donde vive: en el agente, como norma.** *"Tu read-only es una norma, no una jaula: tienes `Write` y `Edit` prohibidos, pero conservas `Bash`."* Nunca modifica el artefacto que audita; su **propio informe** sí lo escribe él. Ninguna lista de tools puede sostener esto — es el corolario de [[D-038]] en la dirección contraria: quitar una tool no quita la capacidad.
3. **`sdd-analysis-gaps.py` gana `--export-answers` / `--import-answers`**, y `wf-spec-analyze` los ejecuta alrededor de la sobrescritura. **Empareja por ID *y* por título, y lo que no case exacto no se escribe** — el análisis no es reproducible (11/5 → 12/7 → 11/7 → 16/11 → 5/2 → 7/4 sobre el mismo PRD), así que un `P-XXX` puede ser otra pregunta en el documento nuevo. Motivos: `titulo_distinto`, `id_ausente`, `ya_respondido`; exit 2 si queda algo por reconciliar.
4. **El changelog registra toda versión del PRD, la bumpee quien la bumpee.** Un review que corrige prosa al cerrar asunciones también mueve `version`: el ciclo medido fue de 1.4 a 1.5 y lo dejó **solo** en `changes/CR-004/decision.md`. El índice se quedó en 1.4 y mentía sobre el dato por el que se consulta.
5. **El análisis declara la versión del PRD en su cabecera** (`Archivo origen: <path> (v<X.Y>)`) y **`wf-spec-discover` la verifica** antes de construir el mapa de features. Se puede parar sin coste **porque el punto 3 ya existe**: antes, avisar de un análisis obsoleto obligaba a elegir entre datos viejos o perder las decisiones del usuario.
6. **Recortar no convierte prosa en metadato.** La frontera de [[D-048]] se afila: un `grep` de campos redactados pasado por `cut -c1-400` sigue siendo prosa. El criterio es **qué** extraes, no cuánto.

**Alternativas descartadas.**

- **Darle `Write` al auditor.** Resuelve el síntoma y borra el invariante: el candado sobre `Write`/`Edit` sigue teniendo valor como señal de intención, aunque `Bash` lo rodee.
- **Que main escriba los informes de los auditores.** Es lo que pasó, y es exactamente lo que [[D-031]] prohíbe.
- **Importar las respuestas emparejando solo por ID.** Es lo cómodo y es el error invisible: el documento queda con pinta de respondido y dice algo que nadie dijo. Ante la duda, el hueco es mejor que la respuesta inventada — mismo criterio que el inventario de 11.2 (*"un script que adivina da falso rigor"*).
- **Matching difuso de títulos.** Adivinar con más pasos sigue siendo adivinar.

**Aprendizaje.** Dos, y el segundo es de método.

**Quitar una tool no quita una capacidad.** [[D-038]] enseñó que `allowed-tools` no es una jaula; esto es su otra cara: `disallowedTools` tampoco lo es mientras quede `Bash`. Todo invariante de "no toques X" es **normativo** y hay que escribirlo como norma, en el sitio que el agente lee. La lista de tools es una declaración de intención, no un mecanismo.

**Un rescate improvisado que sale bien es un defecto, no un éxito.** El apaño de las respuestas funcionó perfectamente y por eso casi no lo vemos. Cuando el ecosistema depende de que al agente se le ocurra algo, la próxima vez puede no ocurrírsele — y el fallo será silencioso.

---

## D-050 — El primer plano no se pide al modelo: se habilita en el proyecto. Fork mode off, y el frontmatter solo para fijar background

- **Fecha:** 2026-08-27 · **Estado:** Adoptada (pendiente de medir en CU-3.a pasada 6). · **Supersede:** [[D-048]] y [[D-049]] (el hook se retira entero; sus aprendizajes de método quedan). · **Relacionada:** [[D-043]] (por fin efectiva), [[D-045]] (mismo muro visto desde dentro de un fork), [[D-047]] (intacta: sigue definiendo qué es esperar), CU-3.a pasadas 4–6.

**Contexto.** Cuatro intentos de conseguir que la delegación a un agente SDD sea síncrona, y el hallazgo que los explica todos.

La cadena de precedencia del harness, tal y como la documenta Claude Code:

```
1. ¿Lo lanzó un teammate?                   → primer plano
2. ¿CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1? → primer plano
3. ¿Fork mode ACTIVO (default interactivo)? → segundo plano, y NO se puede pedir el primer plano
4. ¿Fork mode apagado?                      → segundo plano, SALVO run_in_background: false
                                               o background: false en el frontmatter
```

**El punto 3 está por encima del 4.** Las dos palancas de primer plano —el flag de la llamada y el campo del agente— viven en el 4, así que en una sesión interactiva normal **nunca llegan a evaluarse**. No es que el modelo no obedeciera: es que la petición no tenía dónde aterrizar.

**Tres medidas que lo confirman.**
1. **0 de 10.** CU-3.a pasada 4, con `run_in_background: false` prescrito en cinco puntos del SKILL: no viajó ni una vez. Se leyó como desobediencia; era una petición inútil.
2. **El frontmatter tampoco.** Se puso `background: false` en `sdd-spec-explorer`, se instaló en el consumer a las 07:53 UTC, y una sesión arrancada a las 08:03 hizo `Agent(sdd-spec-explorer)` **sin flag** → `"Async agent launched successfully"`. El campo es **asimétrico**: hay pin hacia background, no hay pin hacia foreground.
3. **El hook fue peor que inútil.** [[D-048]] intentó forzar el flag denegando la llamada. Costó **dos pasadas de conformance** sin medir nada, y además **degradó la conducta del modelo**: siguiendo la prosa del SKILL emitía el booleano en **20 de 20** llamadas; reaccionando al texto del `deny`, emitió la cadena `"false"` en **5 de 5**. El harness descarta la clave por tipo inválido antes de que el hook la vea, así que el gate respondía *"falta el parámetro"* a un modelo que creía haberlo puesto. Un bucle perfecto.

**Decisión.**

1. **`CLAUDE_CODE_FORK_SUBAGENT=0` en el `env` del `settings.json`** que instala el ecosistema. Es lo único que devuelve el control: apaga el punto 3 y hace que el 4 aplique, de forma **declarativa** y sin depender de que el modelo teclee nada.
2. **El frontmatter de agente solo se usa para fijar lo contrario.** `background: true` clava un agente en segundo plano aunque el llamante quiera el resultado. **Hoy no lo lleva ninguno, y es a propósito**: el informe de todos ellos lo consume el paso siguiente. La lista vacía es una decisión documentada en `kb-sdd-creation-guide`, no un olvido.
3. **`run_in_background: false` se mantiene** en las prescripciones — ahora sí surte efecto.
4. **El hook se retira entero**: script, tests, matcher y escotilla. Y se **depreca** en `merge-claude-settings.py`, para que los proyectos que lo recibieron en 0.82.x se queden sin él al actualizar.
5. **El merge de `settings.json` pasa a fusionar `env` clave a clave.** Con la regla anterior —"clave de primer nivel solo si no existe"— un proyecto con su propio bloque `env` **jamás** habría recibido la variable: la clave existía y no se miraba dentro. El valor del proyecto sigue ganando siempre.

**El coste que temíamos no existe — medido.** La reserva era que apagar fork mode quitase a Claude la capacidad de lanzar forks, con **12+ skills `context: fork`** dependiendo de ello. Comprobado con una sonda de un minuto (2026-08-27): `Skill(wf-spec-validate)` sobre un spec real **sigue forkeando** — el subagente trae su `.forked-skill.json`, `agentType: sdd-spec-auditor`, `spawnDepth: 1`, y devolvió el informe completo en 49s.

La asimetría es justo la que hacía falta, y explica por qué la variable no rompe nada:

| Ruta | fork mode ON (antes) | fork mode OFF (ahora) |
|---|---|---|
| `Skill(wf-*)` worker → fork declarado en el SKILL | forkea, asíncrono | **forkea, asíncrono — sin cambio** |
| `Agent(<agente>)` desde el hilo principal | asíncrono, flag ignorado | **síncrono, flag honrado** |

`context: fork` lo aplica el harness al invocar la skill; `CLAUDE_CODE_FORK_SUBAGENT` gobierna qué hace Claude cuando **él** decide lanzar un subagente por la tool `Agent`. Son dos mecanismos distintos, y la variable solo toca el segundo.

**Alternativas descartadas.**
- *`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`* (punto 2, gana a todo) → apaga el segundo plano de **todo** el repo del usuario, incluidos sus agentes. Ya descartada en [[D-045]] por el mismo motivo: el ecosistema es un huésped.
- *Insistir con el hook* → tercera hipótesis fallida sobre el mismo mecanismo, con dos pasadas de coste y evidencia de que empeora la conducta.
- *No hacer nada y fiarlo a la conducta* → defendible: en la pasada 4 el orquestador esperó bien 10 de 10 y sostuvo la barrera del fan-out. Pero es `n=1`, y `CLAUDE_CODE_FORK_SUBAGENT=0` es declarativo y barato de revertir. Si la sonda sale mal, este es el plan B.

**Consecuencias / aprendizaje.**

1. **Antes de escribir enforcement, comprueba si lo que pides es siquiera evaluable.** Cuatro decisiones y dos pasadas para descubrir que el punto 3 anulaba la petición. La señal estaba en el 0/10: una instrucción que **nadie** cumple casi nunca es un problema de obediencia.
2. **Una nota mal tomada envejece como un hecho.** El `background` asimétrico lo tenía apuntado bien, lo contradije leyendo una doc resumida, y construí encima. Lo que zanjó la duda fue una medición de dos minutos que ya existía en los logs.
3. **El enforcement no es neutral sobre la conducta.** El mensaje de un gate es **otro prompt** que compite con el SKILL, y puede empeorar lo que quería arreglar: 20/20 booleanos siguiendo el SKILL, 5/5 cadenas siguiendo el deny.
4. **Un mecanismo nuevo se estrena en su propio escenario, nunca dentro del CU más grande.** Cuando falla, no falla solo: se lleva la medición entera. Dos pasadas.
5. **Y el orden correcto es medir y luego documentar.** [[D-048]] se registró con changelog y versión antes de tener una sola pasada que la respaldara.

**Referencias.** `settings.json`, `scripts/merge-claude-settings.py`, `pipeline/orchestration.md`, `kb-sdd-creation-guide`, `wf-spec-features-first/SKILL.md`, `tests/test_merge_claude_settings.py`, `tests/test_install_sh.py`, CU-3.a pasadas 4–6.

---

## D-049 — Un gate sin estado que repite el mismo mensaje enseña que está roto: cada reintento tiene que dar información nueva

- **⚠️ Superada por [[D-050]]** (Su gate se retira entero; sus aprendizajes de método siguen vigentes).
- **Fecha:** 2026-08-26 · **Estado:** Adoptada (pendiente de medir en CU-3.a pasada 6). · **Relacionada:** [[D-048]] (arregla su gate), [[D-045]] (la excusa no comprobada, otra vez), [[D-037]] (un backstop que no discrimina no protege), CU-3.a pasada 5, CU-9.n.

**Contexto.** Primera pasada con el hook de [[D-048]] instalado. Lo bueno primero: **el hook funciona** — el payload de `PreToolUse` trae `tool_input` para la tool `Agent`, el gate disparó, y el `deny` llegó al modelo. La única incógnita que [[D-048]] no había podido verificar en vivo queda cerrada en positivo.

Y el orquestador hizo **lo correcto en el eje que se medía** (CU-9.n): no rodeó. No invocó por `Skill`, no hizo el análisis él mismo, no degradó el paso. Añadió el parámetro, reintentó la llamada idéntica, y al tercer intento **paró, lo explicó y ofreció la escotilla** `SDD_ALLOW_ASYNC_AGENTS=1` — exactamente la salida sancionada.

**El defecto, en dos capas.**

1. **El gate era insatisfacible por un detalle de tipo.** El reintento llegó con `"run_in_background": "false"` — la **cadena**, no el booleano — y el hook comprobaba `is False`. Nunca pasa. El agente había corregido bien: añadió el parámetro que el mensaje le pedía, y lo puso como string.
2. **Y el gate le devolvió el mismo mensaje, palabra por palabra, las tres veces.** Esto es lo grave, y es de diseño, no de tipos. Un gate **sin estado** no puede distinguir "primer intento" de "reintento ya corregido"; si su respuesta no discrimina *qué* está mal, un reintento correcto recibe el mismo muro que uno vacío. Desde dentro del modelo, tres respuestas idénticas a tres llamadas distintas son evidencia razonable de que el gate no mira lo que dice mirar. Concluyó que el contrato era incumplible — **y era una inferencia correcta a partir de lo que podía observar**.

**El daño colateral, que es un patrón conocido.** Al explicarlo, el orquestador afirmó que *"la tool `Agent` de esta sesión no declara `run_in_background` en su esquema y lo tiene cerrado a propiedades extra"*. Es falso, y se refuta solo: con `additionalProperties: false` la llamada habría muerto en validación, no habría llegado al hook — la ausencia de error de validación es evidencia **en contra**. En el chat lo marcó como "causa probable"; en un informe de bug lo escribió como hecho. Es literalmente la conducta que [[D-045]] prohíbe (*"no afirmes limitaciones del entorno que no has comprobado"*), reaparecida en cuanto la situación volvió a ser "prohibido X y necesito X". Y tenía la respuesta a un `Read` de distancia: **el hook es un fichero legible en `.sdd/scripts/`** y no lo abrió.

**Decisión.**

1. **Dos motivos de deny, no uno.** `sdd-agent-sync.py` distingue *"falta el parámetro"* de *"está, pero el valor no es el booleano"*, y en el segundo **le devuelve el valor que envió** (`con el valor 'false'`) más la corrección exacta (`el booleano false, sin comillas: no la cadena "false", ni 0, ni "no"`). Cada reintento produce información nueva; el modelo puede converger.
2. **No se acepta la cadena.** Tentador, pero no sabemos qué hace el harness con un string donde espera un booleano: si lo coacciona a *truthy*, el subagente seguiría yendo a segundo plano y estaríamos **sancionando una llamada asíncrona creyendo lo contrario**. Se exige el booleano y se dice con precisión qué falta. (`is False` se mantiene a propósito: `0 == False` en Python, y un `0` no expresa la petición de primer plano.)
3. **Regla de contrato: abre el gate antes de declararlo incumplible.** Los gates son ficheros legibles en `.sdd/scripts/`. Un deny repetido casi nunca significa "esto es imposible": significa que la corrección no era la que el gate pedía.
4. **Y si aun así paras, reporta lo observado, no la causa que supones.** "He reintentado tres veces y el deny se repite" es un hecho. "La tool no expone el parámetro" es una hipótesis; sin error de validación que la respalde, afirmarla convierte una suposición en un hecho del harness — y escrita en un informe, en un hecho para terceros.

**Alternativas descartadas.**
- *Aceptar `"false"` además del booleano* → ver punto 2: permitiría una llamada posiblemente asíncrona con el sello de aprobada. Peor que denegar.
- *Hacer el gate con estado (contar intentos por sesión)* → un hook `PreToolUse` es un proceso nuevo por invocación; el estado exigiría un fichero temporal, con su limpieza y sus carreras. El mensaje discriminante resuelve lo mismo sin estado.
- *Quitar el hook y volver a la prosa* → el hook **funcionó**: disparó, se entendió y el agente corrigió. Lo que falló fue mi comprobación de tipo y mi mensaje. Retirar la pieza por un bug de la pieza sería tirar la medición que costó cinco pasadas conseguir.

**Consecuencias / aprendizaje.**

1. **El mensaje de un gate es una interfaz de convergencia, no un aviso.** Se diseña pensando en el **segundo** intento, no en el primero: ¿qué le dice al que ya corrigió y aun así falla? Si la respuesta es "lo mismo", el gate es un muro y el modelo hará lo racional — declararlo roto.
2. **Un fallo de tipo en un gate no se comporta como un fallo de tipo: se comporta como una imposibilidad.** El agente no tiene forma de ver `is False` desde fuera. Todo enforcement que compare valores debe **devolver el valor recibido** en su mensaje: es la diferencia entre un diagnóstico y un muro.
3. **Las conductas que [[D-045]] corrigió reaparecen en cuanto vuelve la situación que las causaba.** No basta con prohibir la excusa no comprobada una vez: la presión estructural —"prohibido X, necesito X"— la vuelve a generar. Lo que la desactiva no es más prohibición, es **dar una acción disponible**: aquí, leer el gate.
4. **Una pasada de conformance que falla por un bug del ecosistema sigue siendo una pasada útil.** Esta no midió CU-3.a, pero confirmó el mecanismo de [[D-048]] en vivo, produjo dos reglas nuevas y una regresión con nombre. El coste de las pasadas está en el reset y la atención, no en que salgan verdes.

**Referencias.** `scripts/sdd-agent-sync.py`, `tests/test_sdd_agent_sync.py` (6 casos nuevos, incl. la regresión literal), `pipeline/orchestration.md`, `wf-spec-features-first/SKILL.md`, CU-3.a pasada 5, CU-9.n.

---

## D-048 — La sincronía de la delegación se hace mecánica: hook `PreToolUse` sobre `Agent`. Y la frontera del orquestador no es la tool, es cargar el artefacto

- **⚠️ Superada por [[D-050]]** (El hook se retira entero; sus aprendizajes de método siguen vigentes).
- **Fecha:** 2026-08-26 · **Estado:** Adoptada (pendiente de medir en CU-3.a pasada 5). · **Relacionada:** [[D-043]] (lo hace efectivo), [[D-047]] (no lo contradice: elimina la ambigüedad en el origen), [[D-045]] (lo anotó como escalada y descartó la alternativa global), [[D-030]]/[[D-031]]/[[D-038]] (la frontera de main), O-8, CU-3.a pasada 4.

**Contexto — parte 1: la prosa no bastó, otra vez.** [[D-043]] prescribió `run_in_background: false`; [[D-045]] llevó `wf-spec-features-first` al hilo principal para que el flag **pudiera** surtir efecto; [[D-047]] reconoció que la vía de la notificación también es esperar bien. Todo correcto, y aun así el resultado medido en CU-3.a pasada 4 es que el flag **viajó en 0 de 10 llamadas**, con el texto delante del agente, en tres skills distintas.

Eso deja la **barrera del fan-out** —el Paso 6 regenera el índice leyendo del disco lo que escribieron los N delegados— sostenida a mano por el modelo: lanzar N, contar N notificaciones, no seguir hasta tenerlas. Funcionó 10 de 10 en la pasada 4. Pero es exactamente el tipo de garantía que [[D-043]] dio por buena mirando el `tool_use` sin mirar el `tool_result`, y que resultó no serlo. La lección acumulada de [[D-038]]/[[D-042]]/[[D-043]]/[[D-045]] es la misma frase: **cuando una propiedad importa, hay que hacerla mecánica.**

**Contexto — parte 2: el `Bash` que nadie prohibió.** [[D-030]]/[[D-031]]/[[D-038]] prohíben que main haga `Read`/`Write` del artefacto. No dicen nada de `Bash`, y un `cat` mete el mismo texto en el mismo contexto que un `Read`. Medido dos veces en el mismo escenario: en la pasada 2, `grep -n "CRÍTICO" -A 12 prd_analysis.md | head -150` **después** de que el delegado ya hubiera dado los IDs con sus preguntas; en la pasada 4, `cat spec/spec_features.md` entero. Ninguna de las dos viola regla alguna. Estaba abierto como `O-8` desde la pasada 2 y subió de prioridad con [[D-045]], que puso a los orquestadores en main —donde tienen `Bash` y ocasión constante—; la pasada 4 lo confirmó.

**Decisión.**

1. **Hook `PreToolUse` (matcher `Agent`) — `sdd-agent-sync.py`**, hermano de `sdd-gate-check.py`. Deniega una llamada `Agent` a un subagente **del ecosistema** que no pase `run_in_background: false`, con un motivo que le dice al modelo **qué hacer**: repetir la misma llamada añadiendo el flag, emitir el fan-out en un único mensaje, y **no** cambiar de estrategia ni reconstruir nada (la salida sancionada de [[D-045]], aplicada al propio mensaje del gate).
   - **Alcance cerrado:** `SDD_AGENTS` es una lista explícita. `general-purpose`, `Explore` o un agente propio del usuario **no se tocan**. El ecosistema se instala en repos ajenos y no le corresponde forzar el modo de ejecución de los agentes de nadie — el mismo motivo por el que [[D-045]] descartó `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, que lo habría apagado en todo el repo.
   - **Escotilla:** `SDD_ALLOW_ASYNC_AGENTS=1` lo desactiva. Un gate que no se puede apagar puede dejar un repo inoperable: si algún día el harness deja de aceptar el parámetro, denegar en bucle bloquearía el pipeline sin salida.
   - **Política conservadora** heredada de `sdd-gate-check.py`: solo se deniega con evidencia positiva; stdin ilegible, tool distinta, `subagent_type` ausente o desconocido, o excepción interna → se **permite** y se sale 0. Si el payload no trae el campo esperado, el hook simplemente nunca dispara — falla hacia el comportamiento de hoy, no hacia un bloqueo.
2. **La frontera de `Bash` queda escrita.** No se prohíbe la tool: se prohíbe **cargar el artefacto**. Una extracción es legítima si cumple las tres — **determinista** (patrón fijo), **delimitada** (`-c`, `-o`, `head` corto; nunca `-A`/`-B` generosos) y **de metadatos** (IDs, veredictos, recuentos, paths). Traer prosa para interpretarla es analizar contenido, que es el trabajo del delegado. La Regla de oro de `wf-spec-features-first` pasa a nombrar **todos** los artefactos, incluido `_features.md`, y da ejemplos de los dos lados de la línea. Cierra `O-8`.

**Alternativas descartadas.**
- *Volver a reforzar la prosa del flag* → tercera iteración del mismo intento. Ya falló con el texto literal en el contexto del agente, dos veces.
- *Aplicar el hook a todos los `Agent`* → rompe los agentes del usuario en su propio repo. El ecosistema es un huésped.
- *`permissionDecision: "ask"` en vez de `deny`* → mete al humano en un bucle de confirmaciones por cada delegación, y no aporta nada: la corrección es mecánica y el modelo puede aplicarla solo.
- *Prohibir `Bash` en el `allowed-tools` del orquestador* → `allowed-tools` no es enforcement ([[D-038]]) y además main **necesita** `Bash` para los scripts deterministas, que son justo lo que sustituye a leer artefactos. La restricción tiene que ser de criterio, no de tool.
- *Un tope numérico de líneas en la extracción* → falso rigor: `grep -c` sobre un fichero enorme está bien y `head -20` de prosa está mal. Lo que discrimina es **qué** traes, no cuánto.

**Consecuencias / aprendizaje.**

1. **Tres iteraciones de prosa sobre el mismo punto son la señal de que el punto no es gobernable por prosa.** [[D-043]] lo escribió, [[D-045]] lo hizo posible, [[D-047]] lo reencuadró — y seguía sin ocurrir. El coste de haber llegado aquí por prosa fueron cuatro pasadas de conformance; la señal para la próxima vez es la **proporción**: 0 de 10 con la instrucción delante no es un despiste que se arregle repitiéndola más fuerte.
2. **Un gate debe fallar hacia lo de siempre, no hacia el bloqueo.** Todo lo raro permite. Si el campo no existe en el payload, el hook nunca dispara y el ecosistema se comporta como antes — que es exactamente lo que quieres de una red de seguridad que corre en el repo de otro.
3. **El motivo de un `deny` es un prompt.** Se lo come el modelo, no el humano. Decir solo "prohibido" reproduce el agujero de [[D-045]]: entre la prohibición y la tarea, el agente improvisa. Por eso el mensaje trae la acción exacta, el recordatorio del fan-out y un "no cambies de estrategia".
4. **Una prohibición formulada sobre la herramienta se evade con otra herramienta.** "No hagas `Read` del artefacto" se cumple al pie de la letra con `cat`. Las restricciones de un orquestador van sobre el **efecto** (qué acaba en su contexto), no sobre el nombre de la tool.

**Referencias.** `scripts/sdd-agent-sync.py`, `tests/test_sdd_agent_sync.py` (18 casos), `settings.json`, `install.sh`, `wf-spec-features-first/SKILL.md` (Regla de oro), `kb-sdd-creation-guide`, CU-3.a paso 5, `MEJORAS_FUTURAS.md` O-8 (cerrado).

---

## D-047 — Esperar es que te entreguen el informe, no en qué turno llega: dos vías sancionadas, y el flag donde hay barrera

- **Fecha:** 2026-08-26 · **Estado:** Adoptada (pendiente de medir en CU-3.a pasada 5). · **Relacionada:** [[D-043]] (matiza su exigencia), [[D-045]] (matiza su criterio de espera), [[D-044]] (intacta), Regla 9.4 de `kb-sdd-conformance`, CU-3.a pasada 4.

**Contexto.** CU-3.a pasada 4, con [[D-045]] ya aplicado y el flag escrito en las cinco prescripciones de delegación de `wf-spec-features-first`. Medido en los transcripts: **`run_in_background: false` viajó en 0 de las 10 llamadas `Agent`** de la sesión — ni en `sdd-spec-explorer`, ni en `prd-expert`, ni en los tres `sdd-spec-writer`, ni en los cuatro `sdd-spec-auditor`. Sistemático, y en tres skills distintas.

Y sin embargo **las diez esperas fueron correctas**: main cedió el turno, no sondeó el disco, no leyó ningún `.output`, no relanzó a nadie, y consumió el informe cuando llegó por notificación. Cero deducciones en 36 tool calls.

Diez de diez no es un despiste. La plataforma documenta las dos rutas: con el flag el informe vuelve dentro del `tool_result`; sin él, el agente corre en segundo plano y **el padre recibe una notificación de fin** con el informe. Las dos entregan el informe; lo único que cambia es el turno en que llega. Nuestro contrato, escrito como *"has esperado cuando el informe está en tu contexto **como resultado de tu propia llamada `Agent`**… ninguna otra cosa cuenta"*, excluía por redacción la ruta que el agente eligió siempre — y encima nombraba "cualquier buzón intermedio del entorno", que un lector razonable puede leer como la notificación.

Aplicando la **Regla 9.4** (cuando un CU marca FALLO una conducta razonable y repetida, el defecto suele estar en el CU): el defecto está en el contrato. Una regla que la conducta correcta incumple 10 de 10 veces no gobierna nada — solo produce FALLOS falsos que enmascaran los verdaderos.

**Pero el flag no es prescindible en todas partes.** Hay un sitio donde sí decide: el **fan-out**. El Paso 5 lanza N `sdd-spec-writer` y el Paso 6 regenera el índice leyendo del disco los specs de **todas** las features; el Paso 7 lanza N auditores y el Paso 8 lee lo que escribieron todos. Ahí hace falta una **barrera**, y la barrera son dos piezas juntas: **las N llamadas en un único mensaje** + **el flag**. Con las dos, el mensaje no vuelve hasta que todas terminaron. Sin el flag, la barrera la tiene que sostener el orquestador contando notificaciones.

Y aquí aparece el segundo hallazgo de la pasada: **las tres llamadas a `sdd-spec-writer` salieron en tres mensajes consecutivos** (y las tres de auditoría, en otros tres), contra el `CRÍTICO: emite TODOS los Agent tool calls en un único mensaje` del propio SKILL. Hoy es inocuo porque van asíncronas y solapan igual — pero es una **bomba de relojería**: el día que el flag surta efecto, tres mensajes separados **serializan** el fan-out (cada mensaje espera a su agente antes de emitir el siguiente). Es decir: la asincronía que incumple el flag está **enmascarando** el incumplimiento del otro requisito, y los dos se rompen a la vez.

**Decisión.** El criterio de espera nombra **las dos vías legítimas** y mantiene intacta la frontera real:

- **(a)** El `tool_result` de la propia llamada `Agent`, con `run_in_background: false`.
- **(b)** La **notificación de fin** del agente, cediendo el turno sin hacer nada más mientras tanto.

Lo que separa esperar de deducir **no es en qué turno llega el informe, es quién lo trae**. Sigue prohibido —y con la misma dureza— todo lo que sea ir a buscar el dato: que el fichero exista, que su tamaño se estabilice, que un script dé veredicto sobre él, o leer el `.output`/log del harness. Y sigue prohibido adelantar trabajo dependiente mientras se espera, o relanzar un segundo delegado sobre lo mismo.

El flag pasa de "siempre, o es fallo" a **"siempre que se pueda, y obligatorio donde hay barrera"**, con el motivo escrito en el punto donde aplica: no es ceremonia, es lo que evita que el Paso 6 selle un índice construido sobre un fan-out a medias.

**Alternativas descartadas.**
- *Dejar el criterio como estaba y seguir contándolo FALLO* → mide una propiedad que la conducta correcta incumple. Es la trampa que Regla 9.4 describe: el CU deja de discriminar y el ruido tapa los hallazgos reales (los dos de esta misma pasada — el índice ciego y el fan-out serializable — se detectaron **a pesar** del ruido del 0/10, no gracias a él).
- *Endurecer: hook `PreToolUse` sobre `Agent` que deniegue sin el flag* → enforcement real, y el carril existe. Pero forzaría el primer plano donde no aporta nada, y la conducta que queríamos (no deducir) ya se cumple. Herramienta guardada para si algún día se rompe la vía (b).
- *`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`* → mismo motivo que en [[D-045]]: apaga una función del harness en el repo del usuario para resolver un problema nuestro.
- *Quitar el flag de las prescripciones, ya que no se teclea* → perdería la barrera del fan-out, que es donde de verdad decide. El flag no sobra; sobraba el absolutismo.

**Consecuencias / aprendizaje.**

1. **Un contrato que la conducta correcta incumple sistemáticamente es un contrato mal escrito, no un agente desobediente.** 10 de 10 es una señal, no ruido. Antes de endurecer una regla que no se cumple, comprobar si lo que prohíbe es realmente lo dañino — aquí prohibía una ruta legítima de la plataforma por cómo estaba redactada.
2. **Nombrar las vías legítimas es más barato que enumerar las prohibidas.** El criterio anterior definía por exclusión ("ninguna otra cosa cuenta") y falló en cuanto apareció un caso no previsto. Definir por **quién entrega el dato** cubre las dos rutas de hoy y las que vengan, sin abrir la puerta a deducir. Misma familia que la lección de [[D-045]] sobre no nombrar la herramienta prohibida.
3. **Un requisito puede estar enmascarado por el incumplimiento de otro.** El fan-out en mensajes separados es inocuo *sólo mientras* el flag no surta efecto. Cuando dos requisitos se sostienen mutuamente, hay que escribirlos juntos y en el mismo punto — separados, uno tapa la rotura del otro y los dos se caen a la vez.

**Referencias.** `wf-spec-features-first/SKILL.md` (contrato de espera, Pasos 5/7), `wf-spec-readiness/SKILL.md`, `kb-sdd-creation-guide`, `sdd-structural-lint.py` (`AGENT-DISPATCH-UNSYNCED`), CU-3.a pasada 4, `ROADMAP.md`.

---

## D-046 — Quien escribe y quien lee tienen que buscar en el mismo sitio; y no encontrarlo no puede ser una advertencia blanda

- **Fecha:** 2026-08-26 · **Estado:** Adoptada. · **Relacionada:** [[D-042]] (el recuento sale del script, no del ojo), [[D-037]] (un backstop vacuo no protege), CU-3.a pasada 4, CU-3.d.

**Contexto.** CU-3.a pasada 4 destapó **dos defectos con la misma forma exacta**, en dos parejas productor/consumidor distintas:

1. **El índice no ve el discovery.** `sdd-features-index.py` lo buscaba con `first_glob(directory, "*_discovery.md")` **dentro de la raíz spec**. Pero el discovery lo genera `wf-spec-discover` a partir del PRD, se llama `<basename_prd>_discovery.md` y en topología `authoring` (`artifacts.prd` != `artifacts.spec`) vive con el PRD. Resultado medido en el consumer: `spec/spec_features.md` con `> Fuentes: discovery=no`, **3 features de 9**, **cero `PENDIENTE_GENERACIÓN`** y hasta el nombre del proyecto mal (`# Features Index: spec`, el nombre del directorio). Las 6 features identificadas y no generadas eran **invisibles para cualquier herramienta que lea el índice**.
2. **El readiness no ve los informes de conflictos.** `wf-spec-readiness` los buscaba solo en el directorio padre de `features/`. Pero el fan-out del Paso 7 de `wf-spec-features-first` lanza **un auditor por spec**, y `wf-spec-conflict` los escribe **junto a cada spec** (`features/<nombre>/spec/<nombre>_conflict_report.md`). El readiness se declaraba "sin análisis de conflictos" con N informes en disco.

**La contradicción de fondo, que ya estaba escrita.** `pipeline/orchestration.md` y el `CLAUDE.md` raíz dicen que el discovery vive "en el directorio de artefactos prd… o junto al PRD"; `sdd-resolve-path.py` lo declara *kind de producto* → "la raíz que contiene `features/`". En topología monodirectorio esos dos sitios coinciden y la contradicción es invisible; en `authoring` se separan y alguien se queda ciego.

**Lo que hace grave a los dos:** ninguno falla. El consumidor no encuentra nada, emite una advertencia **no bloqueante** y sigue con lo que sí tiene, produciendo un artefacto **parcial con apariencia de completo**. Y ese artefacto se sella, se hereda y se lee en las pasadas siguientes. En el caso del índice, main **narró al usuario la tabla correcta de 9 features** mientras el fichero en disco tenía 3: la forma más peligrosa de todas, porque la conversación dice la verdad y el artefacto no.

**Decisión.**

- `sdd-features-index.py` **cruza la frontera de topología**: busca el discovery en `--discovery <path>` explícito → dentro de `<dir>` → los demás directorios de `artifacts` de `.sdd/project-init.json` (buscado hacia arriba), empezando por `prd`. Un discovery externo **no renombra el índice** (sigue siendo `<dir>_features.md`, no `<basename_prd>_features.md`): vive en otra raíz.
- **Se acaba el silencio.** Si hay specs y no hay discovery, el aviso viaja **en el propio artefacto** (`> ⚠ SIN DISCOVERY: …`) y por `stderr`. La política conservadora se mantiene —el índice se construye con lo que hay— pero deja de ser indistinguible de un índice completo.
- `wf-spec-readiness` busca los informes de conflictos **en los dos sitios** y en **ambos layouts**, y lee **todos**, no el primero.
- Regla de autoría en `kb-sdd-creation-guide`: al escribir una pieza consumidora, preguntarse **quién produce esto y dónde lo deja en cada topología y en cada layout**; y cuando no aparezca lo esperado, **decirlo en voz alta**.

**Alternativas descartadas.**
- *Mover el discovery a la raíz spec para que coincida con `sdd-resolve-path.py`* → rompe el nombrado (`<basename_prd>_discovery.md`), contradice el routing ya escrito y publicado, y obligaría a migrar los consumers existentes. Además el discovery es un derivado del PRD: su sitio natural es con el PRD.
- *Que el script aborte si no encuentra discovery* → mataría el caso legítimo de `wf-spec-fast-track` standalone, donde no hay universo de features. El problema no era continuar: era continuar **callando**.
- *Arreglar solo el glob y dejar la advertencia como estaba* → el bug volvería en la siguiente topología no prevista, y volvería igual de silencioso.
- *Una regla de linter que compruebe que productor y consumidor coinciden* → no es decidible estáticamente (las rutas se construyen en prosa y en tiempo de ejecución). Queda como regla de autoría y como señal de FALLO en CU-3.d.

**Consecuencias / aprendizaje.**

1. **Una advertencia no bloqueante sobre una fuente ausente es un fallo silencioso disfrazado.** "Continuando sin X" es aceptable cuando X es opcional de verdad; cuando X define el universo del artefacto, es un artefacto roto que se sella como bueno. El aviso tiene que viajar **dentro del artefacto**, donde lo verá quien lo lea después, no solo en la consola de quien lo generó.
2. **Cuando la narración y el artefacto divergen, gana el artefacto** — porque es lo que sobrevive al turno. Main contó las 9 features correctamente y eso hizo *parecer* que el paso había ido bien. El chequeo útil no es "¿lo contó bien?" sino "¿qué quedó escrito?".
3. **Dos defectos con la misma forma en la misma pasada no son coincidencia: es una regla de autoría que falta.** Por eso el arreglo no acaba en los dos parches, sino en la regla de `kb-sdd-creation-guide`.
4. **La topología multiplica las parejas productor/consumidor.** `artifacts.prd != artifacts.spec` es una configuración soportada y declarada, pero casi todos los tests y pasadas anteriores corrían en monodirectorio, donde la divergencia no se manifiesta. Los tests nuevos de `test_sdd_features_index.py` montan `authoring` explícitamente.

**Referencias.** `scripts/sdd-features-index.py`, `tests/test_sdd_features_index.py` (9 casos nuevos), `wf-spec-features-first/SKILL.md` (Paso 6), `wf-spec-readiness/SKILL.md` (Pasos 2/3/4c), `kb-sdd-creation-guide`, CU-3.d, `MEJORAS_FUTURAS.md` O-11.

---

## D-045 — Un fork no orquesta: `wf-spec-features-first` corre en el hilo principal, sostiene sus gates y recibe el resultado de sus delegados

- **Fecha:** 2026-08-26 · **Estado:** **Adoptada y medida** — CU-3.a pasada 4: los 10 subagentes con `spawnDepth: 1` y sin padre (ningún fork), los cuatro gates presentados con `AskUserQuestion` sin relanzar el workflow, cero sondeo. Su criterio de espera queda matizado por [[D-047]]. · **Relacionada:** [[D-043]] (corrige su premisa), [[D-044]] (intacta), [[D-047]] (matiza el criterio de espera), [[D-040]] (mismo movimiento en `wf-prd-change`), [[D-026]] (los `--allow-*` los arma el usuario), [[D-030]]/[[D-031]]/[[D-038]] (main no lee ni escribe artefactos), [[D-042]] (el conteo sale del script), CU-3.a pasadas 3 y 4.

**Contexto.** CU-3.a pasada 3, banco limpio. `wf-spec-features-first` —`context: fork`— falló el paso 5 en tres capas encadenadas, verificadas en los transcripts de subagente:

1. Delegó **sin** `run_in_background: false`, teniendo la instrucción literal en su contexto.
2. Sin resultado, improvisó la espera: `find` en bucle con `sleep 3`×160, polling del `.output` del harness con `sleep 45`, dos lecturas de ese fichero, y `ToolSearch select:Monitor` en las dos invocaciones.
3. **Nunca recibió el informe del delegado.** Reconstruyó path, veredicto y conteo con `find` + `grep` + script y se los reportó a main **como si fueran del delegado**. El informe del explorer se tiró entero.

La capa 3 es el daño real: lo que subió **parecía correcto**. Un `grep` que hubiera pillado otra línea, o un `_analysis.md` viejo de otra pasada, habrían subido con la misma apariencia de verdad.

**Dos premisas caídas al investigarlo.** (a) En la **pasada 2** el flag **sí se pasó** y el `tool_result` fue igualmente `"Async agent launched successfully"`: [[D-043]] **nunca funcionó desde un fork**, y lo que leímos como éxito era el parámetro viajando, no surtiendo efecto. (b) La doc de Claude Code lo explica —con fork mode activo, el default en sesiones interactivas, *"Claude no puede pedir el primer plano"*—, y de las 20 delegaciones registradas en el consumer, las **3** que volvieron con el informe dentro salen **todas del hilo principal**. Verificado en vivo (2026-08-26, Claude Code 2.1.245): main → `Agent(run_in_background: false)` devuelve el informe en el `tool_result`.

**Agravante estructural, ya conocido y nunca cerrado.** El mismo fork sostiene **cuatro gates** (readiness, gaps críticos, expansión de alcance, coste >5 features) y no puede presentar ninguno: `AskUserQuestion` no existe en un subagente. En la pasada 3 paró dos veces, main improvisó la pregunta dos veces y **relanzó el workflow entero** dos veces, repitiendo parseo, readiness y check de gaps (102 KB + 142 KB de fork). [[D-026]] ya lo había anotado como limitación aceptada; el texto de la regla `FORK-ASKUSER-CONFLICT` del linter ya prescribía el arreglo: *"quita `context: fork` — la skill interactiva corre en el hilo principal y delega el trabajo pesado vía `Agent`"*.

**Decisión.** `wf-spec-features-first` sale del fork, al modelo de [[D-040]]: `allowed-tools: [Bash, Agent, AskUserQuestion]` (**sin `Read` ni `Write`**, simetría con `wf-prd-review`/`wf-prd-change`), los cuatro gates se presentan **en el momento** y el flujo continúa en el mismo turno — se acabó el "vuelve a ejecutar añadiendo `--allow-*`". [[D-026]] intacto en el fondo: quien arma el override es el usuario **eligiendo** en el gate; los flags de entrada siguen valiendo y saltan el gate correspondiente.

Y el contrato de delegación gana lo que le faltaba, que es lo que provocó la improvisación:

- **Qué es haber esperado, de forma autocomprobable:** el informe del delegado está en contexto **como resultado de la propia llamada `Agent`**. Que el fichero exista, que su tamaño se estabilice, que un script dé veredicto o que se lea de un buzón intermedio del entorno **no cuenta**. Sin criterio, "espera el resultado" no es verificable y el agente puede creer honestamente que esperó.
- **La salida sancionada:** si no hay informe, **parar y decirlo**, nunca reconstruir. Y **nunca presentar como dicho por el delegado un dato obtenido por cuenta propia**.
- **No afirmar limitaciones del entorno no comprobadas:** sin error de validación, no hay evidencia. (El fork escribió al usuario *"el `Agent` tool de este harness no expone `run_in_background`"* sin haberlo intentado nunca.)

**Regla nueva de lint `FORK-ORCHESTRATOR`**, graduada porque los dos motivos son independientes: **blocking** si el fork delega **y** tiene señal de gate (`--allow-*` o interacción en prosa) — le aplican los dos; **warning** si solo delega — le aplica únicamente la asincronía. Delta medido: `wf-spec-features-first` **blocking antes, 0 después**.

**Alternativas descartadas.**
- *Reforzar la prosa de [[D-043]]* → ya falló con el texto delante del agente. Y sobre todo, pedía algo **inalcanzable** desde un fork: ninguna redacción lo arregla.
- *`background: false` en el frontmatter (Claude Code ≥ v2.1.218)* → gobierna el fork **propio** de la skill (main esperaría al workflow), no las delegaciones que ese fork emite; y deja los cuatro gates fantasma donde están. Una línea que arregla un tercio del problema. Queda anotada en la guía de autoría como palanca conocida.
- *`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` en el `settings.json` del proyecto* → funciona (es la regla 2 de la doc, por delante del fork mode), pero fuerza el primer plano de **todos** los subagentes del repo del usuario, incluidos los suyos. Mismo motivo por el que [[D-041]] descartó `autoMemoryEnabled`: el ecosistema se instala en repos ajenos y no le corresponde apagarle funciones a su herramienta. Reservado por si la pasada 4 falla.
- *Hook `PreToolUse` sobre `Agent` que deniegue sin el flag* → es enforcement real y el carril existe (`settings.json` ya instala uno para `Skill`). Pero ataca el síntoma equivocado: con el orquestador en main el flag ya se honra, y un hook no arregla los gates. Anotado como escalada.
- *Sacar también `wf-task-run` del fork* → mismo defecto y el caso con más consecuencias (delega la implementación y **commitea sobre el informe**), pero es otra fase, escribe código en modo agnóstico y obligaría a re-probar CU-6/9/10/13/14/15/16. Bloque aparte, como [[D-040]] hizo con `wf-prd-change-cascade`. Queda visible como **warning** del linter, no escondido.

**Consecuencias / aprendizaje.** Tres, y las tres trascienden este arreglo:

1. **Una garantía vale lo que su medición, y "el parámetro aparece en la llamada" no es "el parámetro surte efecto".** [[D-043]] se dio por validada viendo el flag en el `tool_use` sin mirar el `tool_result`, que decía `"Async agent launched"` al lado. Verificar el efecto, no la intención.
2. **Prohibir sin dar salida es invitar a improvisar.** Puesto entre "prohibido sondear" y "el paso siguiente necesita el resultado", el agente violó la prohibición — racionalmente. Misma forma que [[D-038]] y [[D-042]]: el hueco lo rellena el agente y elige mal. Todo contrato que prohíba debe decir **qué hacer en su lugar**.
3. **El cuerpo de un SKILL viaja al contexto del agente: nombrar la tool prohibida se la enseña.** Los dos forks fueron a buscar `Monitor` —una tool *deferred*, que no tenían cargada— justo después de delegar. Se lo dijo nuestra propia cláusula anti-sondeo. Las señales de FALLO pueden nombrar tools; viven en `conformance/`, que no se instala. Recogido en `kb-sdd-creation-guide`.

Y un cuarto, de método, que casi cuesta el diagnóstico: **el banco de conformance incluye el ciclo de vida de los agentes**. La pasada 2 se backgroundeó a mano para capturar logs, `Cmd+B` **no deja rastro en los transcripts**, y durante semanas interpretamos como comportamiento del harness algo inducido por el operador. Recogido en la Regla 9 de `kb-sdd-conformance`, con el recordatorio de que los logs de subagente ya están en disco y no hay que provocar nada para leerlos.

**Referencias.** `wf-spec-features-first/SKILL.md`, `pipeline/orchestration.md`, `kb-sdd-creation-guide` (+ `references/frontmatter-templates.md`), `kb-sdd-conformance` Regla 9 punto 7, `sdd-structural-lint.py` (`FORK-ORCHESTRATOR`), `tests/test_sdd_structural_lint.py`, `tests/test_install_sh.py`, CU-3.a, CU-2.e probe G, `ROADMAP.md`.

---

## D-044 — El delegado **ejecuta** la sub-skill; pedirle que la invoque forkea un clon suyo y devuelve la asincronía

- **Fecha:** 2026-08-02 · **Estado:** Adoptada (pendiente de medir en CU-3.a). · **Relacionada:** [[D-043]] (arregló el salto de arriba; este arregla el de abajo), [[D-002]]/[[D-015]] (qué implica `context: fork`), CU-3.a pasada 2.

**Contexto.** La pasada 2 de CU-3.a midió [[D-043]] y salió **PASS**: `wf-spec-features-first` delegó con `Agent`, sin `Monitor`, sin sondeo del disco, sin reporte duplicado. Los transcripts de subagente (`~/.claude/projects/<proyecto>/<sesión>/subagents/agent-*.jsonl`) confirman que el flag **sí viajó**, literal, en las dos delegaciones: `{"subagent_type": "sdd-spec-explorer", "run_in_background": false, …}`.

Pero los metadatos de esos mismos transcripts destaparon lo que faltaba, con `spawnDepth` y `parentAgentId` explícitos:

```
depth 1  wf-spec-features-first        (fork de skill)
depth 2  sdd-spec-explorer  ← Agent(run_in_background: false)          síncrono ✅
depth 3  wf-spec-analyze    ← Skill(…) forkea a OTRO sdd-spec-explorer  asíncrono ⚠
```

El prompt decía *"Ejecuta el skill `/wf-spec-analyze`"*, así que el delegado hizo lo único que ese imperativo permite: usar el `Skill` tool. Y como `wf-spec-analyze` declara `context: fork` **y** `agent: sdd-spec-explorer` —el mismo `subagent_type` que se acababa de lanzar—, ese fork es un **clon del delegado**. El de depth 2 existe solo para invocar al de depth 3, recibir su reporte entero y re-emitirlo.

Dos costes, ambos medidos. **Contexto:** el envoltorio pesó **210 KB** (analyze) y **214 KB** (discover), contra 222 KB y 210 KB de los que hacían el trabajo — es decir, ~210 KB duplicados **por delegación**, y en el fan-out del Paso 5 eso se multiplica por feature. **Asincronía:** el `Skill` tool **no tiene `run_in_background`**, así que el salto de depth 3 volvió a ser async y el delegado llegó a responder *"El skill se ha lanzado en segundo plano. Te avisaré cuando termine"* — un **reporte prematuro** que, de haberlo consumido su padre como retorno, habría roto la cadena. Se recuperó solo; la propiedad no está garantizada.

**Decisión.** El prompt de delegación deja de nombrar la skill como algo que *invocar* y pasa a nombrarla como algo que *leer y ejecutar*: **"lee `.claude/skills/wf-X/SKILL.md` y ejecuta sus pasos TÚ MISMO; NO uses el `Skill` tool"**, con `${CLAUDE_SKILL_DIR}` resuelto a `.claude/skills/wf-X/` y la lista de lo que debe informar al terminar. Aplicado a los cinco puntos de `wf-spec-features-first`. Eso colapsa depth 3 en depth 2: **un** salto, síncrono de punta a punta, sin envoltorio.

La regla canónica se añade a `kb-sdd-creation-guide` junto a la de [[D-043]] —son la misma lección en dos capas— y se mecaniza con **`AGENT-PROMPT-REDISPATCH` [blocking]**, que caza el imperativo `Ejecuta el skill /wf-` en el cuerpo de cualquier `wf-*`. Delta medido: **5 findings antes del fix, 0 después**.

**Alternativas descartadas.**
- *Dejar el doble salto y prohibir solo el reporte prematuro* → cura el síntoma peligroso pero deja los ~210 KB por delegación y la asincronía de depth 3 intactas. El reporte prematuro no es el problema: es el aviso de que hay un salto que no debería existir.
- *Volver a `Skill` desde `features-first` para las cuatro sub-skills que declaran `agent:`* → es **un** salto (el `Skill` tool forkea directo al agente declarado), pero sigue sin knob de sincronía. Es exactamente la pasada 1: `Skill` desde un fork es async, y de ahí salió el busy-wait. La lección que corrige a [[D-043]]: el problema **nunca fue** que `Skill` no estuviera en `allowed-tools`; es que `Skill` desde un subagente es asíncrono, punto.
- *Que el prompt lleve el trabajo en vez del nombre de la skill* → el `SKILL.md` **es** el contrato (plantilla, checks, veredictos); parafrasearlo en un prompt lo duplica y lo deja derivar. Mejor que lo lea de disco, que es lo que los forks ya hacen con sus `references/`.
- *Lint que además valide que el `subagent_type` coincide con el `agent:` de la sub-skill* → exige resolver qué skill nombra un prompt en prosa; no es mecanizable con fiabilidad. Lo cubre el backstop posicional de `test_install_sh.py`.

**Consecuencias / aprendizaje.** Tres. (a) **Un imperativo del prompt es una elección de mecanismo, aunque no lo parezca.** "Ejecuta el skill X" suena a descripción de la tarea y es en realidad una instrucción de tool-use: el delegado no tiene otra forma de obedecerla. Al escribir un prompt de delegación hay que preguntarse qué tool va a usar quien lo lea. (b) **El acoplamiento `subagent_type` ↔ `agent:` de la sub-skill ahora es explícito y hay que mantenerlo:** si el `agent:` de una sub-skill cambia, el `subagent_type` de `features-first` debe cambiar con él (el prompt lo dice para que se vea). (c) **Los transcripts de subagente son el instrumento de medida de esta campaña.** Viven en `~/.claude/projects/<proyecto>/<sesión>/subagents/`, con `spawnDepth`, `parentAgentId` y los **parámetros exactos de cada tool call** — que es lo que permitió distinguir "el flag no llega" de "el flag llega y el problema está más abajo" **sin gastar otra pasada**. Corolario operativo: no hace falta poner los agentes en background para capturar sus logs, y hacerlo **contamina la medición** de la sincronía.

**Pendiente de medir.** Que el delegado obedezca *"no uses el `Skill` tool"* es, otra vez, declarado y no medido — y esta campaña ya sabe lo que valen las declaraciones ([[D-038]]). Se cierra repitiendo el turno 1 de CU-3.a **sin backgroundear** y comprobando en `subagents/*.meta.json` que **no hay ningún agente con `spawnDepth: 3`**.

**Referencias.** `sdd/pipeline/spec/skills/wf-spec-features-first/SKILL.md` (5 prompts), `sdd/meta/skills/kb-sdd-creation-guide/SKILL.md` + `references/frontmatter-templates.md`, `sdd/scripts/sdd-structural-lint.py` (`check_agent_prompt_redispatch`), `sdd/tests/test_sdd_structural_lint.py`, `sdd/tests/test_install_sh.py` (`test_features_first_delegates_execute_not_redispatch`), `sdd/conformance/casos-de-uso/cu-03-specs.md` (CU-3.a paso 5), `sdd/CHANGELOG.md`.

---

## D-043 — La delegación de una `wf-*` es síncrona y por un mecanismo nombrado; nadie deduce del disco si un delegado terminó

- **Fecha:** 2026-08-02 · **Estado:** Adoptada (regla canónica en `kb-sdd-creation-guide` + regla blocking del linter; conducta pendiente de medir en CU-3.a). · **Relacionada:** [[D-038]] (`allowed-tools` no es enforcement — tercera confirmación), [[D-042]] (mismo origen: la pasada 1 de CU-3.a), [[D-037]] (el check nuevo se mide por su delta, no por su existencia), [[D-041]] (mismo carril de propagación: la plantilla de `kb-sdd-creation-guide`), CU-2.e (la carrera hermana, en `wf-prd-review`).

**Contexto.** Observación 3 de CU-3.a pasada 1. `wf-spec-features-first` invocó su primer sub-workflow y se quedó en **busy-wait**: `Skill(wf-spec-analyze)` → `Monitor(wait for prd_analysis.md)` → `cat prd.md` (el orquestador cargándose el PRD entero, contra su propia Regla de oro) → `ls -la prd/` → *"I'll wait for the analysis skill to finish"* → `ls -la prd/` otra vez → y el reporte final **duplicado**, porque el stream del `Monitor` cerró después.

Tres defectos encadenados con una sola raíz — **el SKILL no decía con qué tool se invoca ni que había que esperar**:

1. **Mecanismo no uniforme dentro de la misma skill.** El Paso 5 prescribía la tool exacta (`Agent` + `subagent_type: sdd-spec-writer`) y hasta prohibía la alternativa ("No uses el `Skill` tool"). Los otros cuatro puntos de delegación —analyze, discover, conflict, readiness— decían solo *"invoca `/wf-spec-analyze`"*. Ante el hueco, el agente eligió `Skill`, que ni siquiera estaba en su `allowed-tools`.
2. **Sincronicidad no declarada.** Desde Claude Code v2.1.198 los subagentes corren en **background por defecto**. Medido en el árbol: **7 skills prescribían delegación por `Agent` y solo `wf-prd-create` pasaba `run_in_background: false`** — el único sitio donde la lección estaba escrita, porque ahí se había pagado antes.
3. **Sondeo del filesystem como sustituto de la espera.** Sin handle síncrono, el fork improvisó `Monitor` + `ls` en bucle. Es el mismo fallo que CU-2.e observó en `wf-prd-review` (gate abierto en paralelo al diagnóstico), pero la lección vivía en dos skills, no como invariante del ecosistema.

**Decisión.** Una `wf-*` que delega lo hace por **un** mecanismo, **nombrado en cada punto de delegación**, **síncrono**, y **espera el retorno de la tool** — nunca deduce del disco. Concretamente: si delega por `Agent`, pasa **siempre `run_in_background: false`**; nada de averiguar si el delegado terminó con `ls`/`find` en bucle o `Monitor` sobre el fichero que va a escribir, ni de relanzar un segundo agente "por si acaso" (eso no es esperar: es un race de doble escritura sobre el mismo artefacto).

Los cinco puntos de `wf-spec-features-first` pasan a la forma canónica del Paso 5, con el `subagent_type` = el `agent:` que **el propio sub-workflow ya declara** en su frontmatter (analyze/discover → `sdd-spec-explorer`, fast-track → `sdd-spec-writer`, conflict/readiness → `sdd-spec-auditor`), para que el destino no se invente. El flag **no** rompe el fan-out del Paso 5: las N llamadas emitidas en un único mensaje siguen corriendo a la vez; solo garantiza que el mensaje no vuelve hasta que todas terminan — que es lo que el Paso 6 ya asumía al regenerar el índice leyendo los specs del disco.

**Barrido de la clase completa**, no solo del sitio observado: `wf-task-run` (el más grave — delega la implementación y acto seguido valida el DoD y commitea), `wf-bug`, `wf-prd-change` (Pasos 4 y 6), `wf-prd-review` (que decía "en **foreground** (síncrono)" en prosa; la prosa no es lo que el agente teclea) y `wf-kmm-init`. Y regla nueva del linter, **`AGENT-DISPATCH-UNSYNCED` [blocking]**, que solo mira `wf-*` (una `kb-*` que *describa* el patrón no es una prescripción) y exige el flag literal cuando el cuerpo prescribe `Agent`.

**Alternativas descartadas.**
- *Unificar todo el ecosistema en el `Skill` tool* → `Skill` no paraleliza (el fan-out del Paso 5 lo necesita) y **no tiene knob de sincronicidad**: si el harness lo despacha async, no hay nada que prescribir. `Agent` sí lo tiene, y ya era el mecanismo del punto más caliente.
- *Cambiar `wf-prd-change-cascade` a `Agent` por uniformidad global* → delega por `Skill` **declarado** y está SELLADO en CU-2.j 6/6 sin sondeo observado. La regla es **por skill** (un mecanismo, síncrono), no "todo el mundo a `Agent`": tocar una skill sellada por simetría estética habría reabierto una conformance cara sin defecto medido.
- *Confiar en `allowed-tools` para impedir el `Skill`* → ya sabíamos que no es enforcement ([[D-038]]); esta pasada es la tercera confirmación, y la primera en la que el daño no es de ámbito de edición sino de despacho.
- *Arreglar solo `wf-spec-features-first`* → es donde se midió, pero el conteo dijo 6 skills más con la misma firma. Dejarlas habría sido esperar a que cada una se manifestara en su propia campaña.
- *Regla del linter que exija además el `subagent_type` correcto contra el `agent:` del sub-workflow* → requiere resolver qué skill invoca el prompt en prosa: no es mecanizable con fiabilidad. Se cubre con el backstop posicional de `test_install_sh.py`.

**Consecuencias / aprendizaje.** Tres. (a) **Un default del harness que cambia es deuda silenciosa repartida por todo el árbol**: `wf-prd-create` documentó el cambio de v2.1.198 en su propio cuerpo y ahí se quedó — la lección no viajó porque no tenía dónde vivir (ni regla de autoría, ni linter). Cuando una lección solo existe en la skill que la sufrió, la siguiente skill la vuelve a pagar. (b) **La prosa no es el mecanismo.** `wf-prd-review` decía "en foreground (síncrono)" desde CU-2.e y aun así no pasaba el flag: describir la propiedad deseada no la produce; hay que escribir lo que el agente teclea. (c) **Especificar el mecanismo en un punto y omitirlo en el de al lado es peor que omitirlo en todos**: el contraste hace que el hueco parezca deliberado ("aquí sí importaba la tool, aquí no"), y el agente lo rellena con la alternativa más obvia. El delta del linter lo confirma sin discusión: **6 findings antes del fix, 0 después** — la medida que [[D-037]] exige para no aceptar un check vacuo.

**Pendiente de medir.** D-043 es hoy **declarado, no medido**: el linter garantiza que el flag está escrito, no que el orquestador lo teclee. Se cierra en la campaña, repitiendo el turno 1 de CU-3.a con 0.79.0 propagado y comprobando **en los logs** que aparece `Agent(subagent_type: sdd-spec-explorer, run_in_background: false)` y **cero** `Monitor`, cero `ls` repetido sobre `prd/`, un solo reporte final.

**Referencias.** `sdd/meta/skills/kb-sdd-creation-guide/SKILL.md` + `references/frontmatter-templates.md` (regla canónica), `sdd/pipeline/spec/skills/wf-spec-features-first/SKILL.md` (5 puntos), `wf-task-run`, `wf-bug`, `wf-prd-change`, `wf-prd-review`, `wf-kmm-init` (barrido), `sdd/scripts/sdd-structural-lint.py` (`check_agent_dispatch`), `sdd/tests/test_sdd_structural_lint.py`, `sdd/tests/test_install_sh.py` (`test_installed_wf_delegate_synchronously`, `test_features_first_delegates_by_agent_not_bare_slash`), `sdd/conformance/casos-de-uso/cu-03-specs.md` (CU-3.a paso 5), `sdd/CHANGELOG.md`.

---

## D-042 — Las respuestas del `_analysis.md` las escribe el usuario (o un script), y "¿quedan críticos?" deja de ser juicio

- **Fecha:** 2026-08-02 · **Estado:** Adoptada (bloque normativo en `kb-gap-conventions`). · **Relacionada:** [[D-038]] (ámbito de edición cerrado; `allowed-tools` no es enforcement), [[D-030]] (lo mecánico va por script, no por agente escritor), [[D-031]] (main no lee ni diagnostica el artefacto), [[D-037]] (orden entre pasos deterministas + guarda `VACUOUS`), CU-3.a.

**Contexto.** Dos defectos, encontrados juntos en CU-3.a pasada 1.

(a) **Vacío de ámbito.** Tras generar `prd_analysis.md`, el hilo principal ofreció: *"Puedes contestármelas aquí **y yo las anoto en el análisis**, o escribirlas tú directamente"*. Esa segunda mano **no existía en el contrato**: `wf-spec-analyze` decía *"Anota las respuestas…"*, `wf-spec-features-first` Paso 2.5 *"**Edita el archivo**…"* y la cabecera del propio artefacto *"Escribe la respuesta… en el campo Respuesta"* — siempre en segunda persona, siempre el usuario. Nadie decía qué pasa cuando el usuario **dicta**, que es lo que ocurre a diario. Main improvisó una vía que implica escribir un artefacto. Misma forma exacta que el vacío que cerró [[D-038]] en la fase PRD.

(b) **Juicio donde cabía un conteo.** `wf-spec-features-first` Paso 2.5 pedía *"léelo y determina… gaps `[CRÍTICO]` pendientes"*, y de esa lectura colgaban **dos ramas duras**: detenerse, o continuar aceptando HUs `[INCOMPLETO]` con `--allow-open-critical-gaps`. `wf-spec-gap-resolve` repetía la misma lectura al cerrar. Contar marcadores `_(pendiente)_` en bloques `[P-XXX]` no es juicio semántico: es un conteo, y estaba sin verificador.

**Decisión.** Tabla **cerrada** de ámbito + mecanismo en `kb-gap-conventions` (SSoT del sistema de gaps): responder un `[P-XXX]` es del **usuario**, editando el `_analysis.md` — vía normativa y de coste cero; si lo **dicta**, lo aplica el hilo principal con `sdd-analysis-gaps.py --answer P-XXX "texto"` por `Bash`; el **contenido** de una respuesta no lo pone nadie más (ni main ni un agente lo inventan, completan o reinterpretan); y saber si quedan gaps abiertos es `--check`. **Main nunca hace `Read`/`Edit`/`Write` del `_analysis.md`**, aunque tenga las tools ([[D-038]]).

Nuevo script `sdd-analysis-gaps.py` con las dos caras. `--check` devuelve veredicto (`CRITICAL_OPEN` / `CRITICAL_ANSWERED` / `VACUOUS`), conteos e IDs, y **corre antes** de la rama que gobierna — con backstop que compara **posiciones**, no presencia, porque la lección de [[D-037]] es que cuando el texto y la posición se contradicen gana la posición. `--answer` es sustitución quirúrgica con precondiciones fail-safe: no pisa una respuesta ya escrita por una persona salvo `--force`, y un `P-XXX` inexistente se rechaza listando los válidos. La guarda `VACUOUS` (exit 2 si no se parseó ningún bloque) evita el no-op silencioso: un verificador que responde "0 críticos abiertos" sobre un documento que no ha entendido es peor que no tenerlo.

**Y el mensaje de cierre deja de ser genérico.** *"Responde las preguntas marcadas como `_(pendiente)_`"* obliga a bucear entre 11 gaps para descubrir cuáles bloquean. Pasa a llevar path exacto, los IDs `[CRÍTICO]` **cada uno con su pregunta en una línea**, y qué se sustituye literalmente. En la pasada 1 el orquestador improvisó justamente eso y funcionó: se convierte en contrato en vez de depender de que vuelva a ocurrírsele.

**Alternativas descartadas.**
- *Recoger las respuestas con `AskUserQuestion`* → **estructuralmente inadecuado**, antes que caro: son respuestas en **prosa libre** sobre 11 gaps, y la tool admite 4 preguntas por llamada con 2–4 **opciones**; harían falta ~3 llamadas y todas las respuestas reales irían por el campo libre. Es la fricción que el usuario ya reportó en el gate de asunciones del PRD, multiplicada.
- *Que main transcriba con `Read` + `Edit`* → carga el informe entero en el hilo principal y es exactamente lo que [[D-031]]/[[D-038]] cerraron. Por script, main no carga nada.
- *Delegar la escritura al `sdd-spec-explorer`* → sustituir `_(pendiente)_` por un texto dado es mecánico y sin juicio; delegar lo mecánico a un modelo es lo que [[D-030]] descartó.
- *Prohibir el dictado y remitir siempre al editor* → cerrado y barato, pero el usuario **va a pedirlo**; sin mecanismo sancionado, main vuelve a improvisar o genera fricción negándose. Nombrar el mecanismo del caso que ocurrirá es justo la lección de [[D-038]].
- *Backstop semántico que detecte respuestas fabricadas* → no mecanizable. Lo que sí lo era —el conteo— es lo que se mecaniza aquí.

**Consecuencias / aprendizaje.** Dos. (a) **Un contrato escrito solo en segunda persona deja fuera al tercero que aparecerá**: decir "tú editas el fichero" describe el caso feliz y no dice nada del caso "hazlo tú por mí", que es donde se improvisa. Al cerrar un ámbito, enumerar **quién más podría querer hacerlo**, no solo quién debe. (b) **Antes de pedirle juicio a un agente, comprobar si lo que se le pide es contable.** "¿Quedan críticos sin responder?" parecía lectura del informe y era `grep` con estructura; el coste de haberlo dejado como juicio no fue un error observado, sino un gate sin verificador durante toda la vida de la fase spec.

**Referencias.** `sdd/scripts/sdd-analysis-gaps.py` (nuevo), `sdd/install.sh` (lista de scripts instalados), `sdd/pipeline/spec/skills/kb-gap-conventions/SKILL.md` (tabla de ámbito, SSoT), `wf-spec-analyze/SKILL.md` (Paso 8), `wf-spec-features-first/SKILL.md` (Paso 2.5), `wf-spec-gap-resolve/SKILL.md` (Paso 7), `sdd/tests/test_sdd_analysis_gaps.py`, `sdd/tests/test_install_sh.py` (`test_gap_conventions_declares_answer_remit`, `test_features_first_checks_gaps_before_deciding`), `sdd/conformance/casos-de-uso/cu-03-specs.md` (CU-3.a pasos 2–4), `sdd/CHANGELOG.md`.

---

## D-041 — Ningún agente del ecosistema declara `memory:`: el estado vive en los artefactos

- **Fecha:** 2026-08-02 · **Estado:** Adoptada (conducta pendiente de medir, ver más abajo). · **Relacionada:** [[D-018]]/[[D-021]] (qué memoria carga un subagente y cuándo), [[D-031]]/[[D-038]] (main no lee ni escribe el artefacto), CU-3.a, CU-15 (deriva y trazabilidad).

**Contexto.** **24 agentes** del ecosistema declaraban `memory: project` —los 11 del pipeline, los 3 de meta y los 10 del overlay KMM—, heredado de la plantilla de `kb-sdd-creation-guide/references/frontmatter-templates.md`: cada agente nuevo nacía con memoria. **Ninguna decisión lo justificó nunca** y ninguna regla de lint lo exigía. Era un default copiado, no una elección.

Medido en conformance (CU-3.a, pasada 1). Tras generar el análisis de gaps, `sdd-spec-explorer` se escribió `.claude/agent-memory/sdd-spec-explorer/{MEMORY.md,project_myops_context.md}` con **los 11 gaps por ID**, los defaults propuestos para los informativos, la predicción de que *"8 features emergerán del discovery"* y —lo relevante— un bloque `How to apply:` que **instruye a las pasadas futuras**: *"antes de recomendar generar specs o ejecutar discover, verificar si el usuario ha respondido los P-001 a P-005"*. Eso no es un resumen: es un **segundo contrato**, no versionado, que compite con el SKILL.

**Decisión.** Ningún agente SDD declara `memory:`. Se quita de los 24 agentes y **de la plantilla**, que es la pieza que importa: es de donde hereda su frontmatter cada agente que se cree a partir de ahora.

El motivo no es la higiene del banco de pruebas —eso fue solo el primer sitio donde se vio—, es la premisa del ecosistema: **el artefacto es la SSoT**. La memoria de agente es estado que sobrevive **fuera** del artefacto, y por tanto: ningún gate la comprueba, ningún script determinista la ve, ninguna regeneración del artefacto la invalida, y nada garantiza que el agente prefiera el fichero a lo que recuerda. Un pipeline cuya trazabilidad se construye sobre ficheros versionados no puede tener a sus agentes decidiendo desde un estado paralelo e invisible. Si un agente parece necesitar memoria, lo que necesita es **leer su artefacto** o recibir el dato en el brief.

Efecto secundario buscado: las pasadas de conformance vuelven a ser **independientes entre sí**. Con memoria, la pasada 2 de cualquier CU llega sabiendo el resultado de la 1 y deja de medir lo que dice medir.

**Por qué el frontmatter y no `autoMemoryEnabled`.** Claude Code ofrece apagarlo por proyecto (`autoMemoryEnabled: false` en `.claude/settings.json`) o por entorno (`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`). Ninguna de las dos sirve como contrato del ecosistema: la primera apagaría también la memoria del **hilo principal del usuario en su propio repo** —el ecosistema se instala en repos ajenos y no le corresponde desactivarle una función de su herramienta—, y la segunda es una variable de entorno por desarrollador, que **no viaja en git** (el mismo motivo por el que el opt-out de SDD es `.claude/sdd-mode.json` y no una env var). El campo `memory:` del agente es exactamente la superficie que sí es nuestra.

**Alternativas descartadas.**
- *Quitarlo solo a `sdd-spec-explorer`* (el que se pilló) → deja el defecto en los otros 23 y en la plantilla, que lo reintroduce al primer agente nuevo. El problema no es un agente, es un default.
- *`autoMemoryEnabled: false` en el `settings.json` instalado* → radio de explosión sobre el proyecto del usuario; ver arriba.
- *Dejar la memoria y prohibir en prosa que contradiga al artefacto* → una garantía que depende de que el agente prefiera el fichero a su memoria es exactamente la clase de garantía no medible que esta campaña lleva descartando desde [[D-040]].
- *Borrar los `.claude/agent-memory/` existentes en `wf-sdd-update`* → son datos en el repo del usuario. Se **avisa** (línea `⚠` del CHANGELOG, que el update muestra), no se borra en silencio.

**Consecuencias / aprendizaje.** Dos. (a) **Un default heredado de una plantilla no es una decisión, pero se comporta como si lo fuera**: 24 agentes con memoria porque el primer `frontmatter-templates.md` la traía. Al auditar el ecosistema, mirar qué campos vienen de plantilla y preguntar quién los eligió. (b) **Enumerar los estados que sobreviven al artefacto**, igual que [[D-039]] obligó a enumerar quién lo escribe: memoria de agente, caché, notas fuera de repo. Todo lo que persiste y ningún check ve es un contrato en la sombra.

**Pendiente de medir.** Que el frontmatter apagara la escritura está **declarado, no medido** — y esta campaña ya aprendió con [[D-038]] que `allowed-tools` declaraba sin encerrar. Se verifica re-corriendo una pasada de CU-3.a con los agentes limpios y comprobando que `.claude/agent-memory/` no reaparece. Hasta entonces, la garantía vale lo que su medición.

**Referencias.** Los 24 `*/agents/*.md` de `pipeline/`, `meta/` y `tech/kmm/`; `sdd/meta/skills/kb-sdd-creation-guide/references/frontmatter-templates.md`; `sdd/scripts/sdd-structural-lint.py` (regla `AGENT-MEMORY-DECLARED`, que cubre agentes **y** plantilla); `sdd/tests/test_sdd_structural_lint.py`, `sdd/tests/test_install_sh.py` (`test_installed_agents_declare_no_memory`); `sdd/CHANGELOG.md`.

---

## D-040 — `wf-prd-change` corre en el hilo principal con gate obligatorio; sin humano, la ambigüedad se marca en vez de decidirse

- **Fecha:** 2026-07-30 · **Estado:** Adoptada (pieza 2 de 2 de [[D-039]]). · **Relacionada:** [[D-039]] (pieza 1, la válvula que hace posible el modo sin gate), [[D-038]] (main no escribe ni lee el artefacto; la clasificación de gobernanza es del `prd-expert`), [[D-031]], [[D-028]]/[[D-032]] (reapertura del sello), CU-7.a/b/c/n, CU-7.f–k, CU-11.g, CU-13.a.

**Contexto.** `wf-prd-change` era `context: fork` + `agent: prd-expert` + `allowed-tools: [Read, Write, Bash]`: un subagente que clasificaba el cambio, decidía su alcance y escribía el PRD, **sin ningún punto en el que un humano pudiera intervenir** — y su Paso 5 se llamaba literalmente "Proponer **y aplicar**". Un fork no puede usar `AskUserQuestion`, así que el gate no era "opcional": era **imposible por construcción**. Medido en CU-7.b: la pasada 1 pareció correcta solo porque el agente **se salió del guion** (paró, reportó una bifurcación de alcance (a)/(b) y el orquestador improvisó la pregunta en main y lo reanudó); la pasada 2, ante una bifurcación equivalente —¿"deducibles" es etiquetar, o ayudar a declarar?— **la resolvió en solitario** y estrechó una exclusión explícita del PRD. Misma clase de decisión, 1 de 2. Una garantía que depende de que el agente improvise no es una garantía.

Agravante encontrado al diseñar: **`wf-prd-change-cascade` también es `context: fork`** y la invocaba con la tool `Skill`, mientras su "filosofía de paradas" declaraba *"detente donde una persona debe decidir: **(1) aprobar el cambio de producto**"*. Ese checkpoint **nunca existió**: era un fork invocando a otro fork, sin nadie a quien preguntar. Y el propio `sdd-structural-lint.py` ya prescribía el arreglo en el texto de su regla `FORK-ASKUSER-CONFLICT`: *"quita `context: fork` — la skill interactiva corre en el hilo principal y delega el trabajo pesado vía `Agent`"*.

**Decisión.** Re-arquitecturar `wf-prd-change` al modelo de `wf-prd-review`: fuera `context: fork` y `agent:`, `allowed-tools: [Bash, Agent, AskUserQuestion]` (**sin `Read` ni `Write`**, simetría exacta con el review). Main orquesta y sostiene el gate; el `prd-expert` **analiza read-only** (Paso 4: clasificación, severidad, secciones afectadas, bifurcaciones, asunciones que propondría) y **luego** escribe el PRD y la traza por delegación (Paso 6). Que el análisis no escriba es lo que hace posible el gate: no se puede pedir permiso sobre algo ya escrito. Lo único que main ejecuta sobre el fichero es `sdd-prd-apply.py --reopen` por `Bash` (Paso 7), igual que el review ejecuta `--seal`.

**El gate (Paso 5) cubre clasificación + bifurcaciones, siempre y en un solo `AskUserQuestion`.** Siempre, sin excepción por trivialidad: decidir *cuándo* preguntar es un juicio, y es precisamente el juicio que falló 1 de 2 pasadas. El humano puede **corregir** la clasificación —es el product owner—; lo que no cambia es que **main no enruta contra el experto** por su cuenta ([[D-038]] intacto): presenta su clasificación, no la sustituye.

**Modo `--defer-decisions`,** para invocaciones desde un subagente (hoy solo la cascada), bajo un invariante duro: **sin humano, la ambigüedad se marca — nunca se decide.** Cada bifurcación se resuelve por la lectura **más conservadora** y **queda marcada `[ASUNCIÓN]`** con las alternativas anotadas en `change-request.md`; la clasificación se reporta sin confirmar y se registra como *no confirmada por humano*; el PRD sale `OPEN_ASSUMPTIONS`. **La decisión humana no se pierde: se aplaza** al gate de `wf-prd-review`. [[D-039]] es lo que hace esto posible — sin la obligación de marcar, "no preguntar" solo podía significar "decidir en silencio".

**Consecuencia sobre `--new-reqs`:** deja de ser obligatorio-como-fichero y admite **texto inline**. No es una concesión: exigir fichero obligaría a **main a escribirlo**, y en la arquitectura nueva main no escribe ficheros. Lo que importa no es la forma de entrada sino que el **texto literal quede recogido** en `change-request.md`. Cierra el hallazgo 2 de CU-7.b pasada 1 (un "obligatorio" que no ataba: el orquestador pasó texto inline y el experto siguió igual) en la dirección de legitimar el inline. **CU-11.g queda obsoleto** en su ejemplo canónico de "skill que exige fichero".

**Alternativas descartadas.**
- *Que la cascada deje de invocar `wf-prd-change`* (pasa a ser precondición) → arquitectónicamente lo más limpio y sin flags, pero rompe la promesa de "propaga todo en un comando" que es la razón de existir del cascade.
- *Sacar también la cascada del fork* → heredaría el gate de verdad y arreglaría su checkpoint falso, pero invoca 6 workflows y obligaría a re-probar CU-7.f–k enteras. Queda como candidato aparte; el `--defer-decisions` no lo impide.
- *Gate solo ante bifurcaciones de alcance* → devuelve al agente la decisión de si hay bifurcación, que es el juicio que falló; y deja fuera CU-7.c (expansión disfrazada de aclaración).
- *Gate solo en la frontera editar / no editar* → cierra CU-7.c pero deja las bifurcaciones internas decidiéndose solas dentro de un cambio ya aceptado.
- *Dejar que el `prd-expert` pare y reporte, como en la pasada 1* → es exactamente la conducta medida en 1 de 2. Convertir en contrato algo que depende de salirse del guion es la definición de garantía no medible.

**Consecuencias / aprendizaje.** Dos. (a) **Un checkpoint humano declarado en prosa no es un checkpoint si la arquitectura no puede sostenerlo.** La cascada llevaba escrito "detente donde una persona debe decidir" sobre un paso donde no había persona posible; nadie lo notó porque el texto era plausible. Al auditar paradas, comprobar **quién puede preguntar**, no qué dice el documento. (b) **El validador estructural ya sabía la respuesta**: `FORK-ASKUSER-CONFLICT` describía el arreglo exacto en su mensaje de error, y solo se disparó cuando se escribió el token literal en la prosa. Una regla de lint cuyo *mensaje* contiene una decisión de arquitectura pendiente es una decisión que se está pagando en intereses.

**Referencias.** `sdd/pipeline/prd/skills/wf-prd-change/SKILL.md` (reescrito), `sdd/pipeline/prd/skills/wf-prd-change-cascade/SKILL.md` (Paso 3 + filosofía de paradas), `sdd/scripts/sdd-structural-lint.py` (`FORK-ASKUSER-CONFLICT`), `sdd/conformance/casos-de-uso/cu-07-cambio-producto.md`, `sdd/tests/test_install_sh.py` (`test_prd_change_runs_in_main_with_gate`, `test_prd_change_cascade_defers_decisions`), `sdd/CHANGELOG.md`.

---

## D-039 — La anti-fabricación rige **cada escritura** sobre el PRD: `wf-prd-change` marca sus propias inferencias

- **Fecha:** 2026-07-30 · **Estado:** Adoptada (pieza 1 de 2; bloque normativo en `wf-prd-change` Paso 5). · **Relacionada:** Regla 12 de `kb-prd-expert` (anti-fabricación), [[D-029]] (grafo de dependencias), [[D-030]] (las decisiones las aplica `sdd-prd-apply.py`), [[D-028]]/[[D-032]] (reapertura del sello), CU-7.b.

**Contexto.** La anti-fabricación se diseñó como propiedad de la **creación**: `wf-prd-create` marca `[ASUNCIÓN]` toda afirmación inferida y `wf-prd-review` tiene una máquina entera para resolverlas (gate, invariante 1:1, `sdd-prd-apply.py`, cascada determinista). Pero `wf-prd-change` escribe en **el mismo documento** y su SKILL **no mencionaba `[ASUNCIÓN]`, `[ASN-XXX]`, la Regla 12 ni la anti-fabricación en ningún sitio**. Consecuencia: el invariante "toda afirmación de negocio traza al origen o va marcada" se sostiene en la creación y **muere en el primer cambio** — es evitable simplemente enrutando contenido por `wf-prd-change`. Y el check mecánico no lo ve: sin marcas, `sdd-prd-ready.py` da `0 = 0`, `one_to_one: true`, y el review posterior declara **`LISTO` sobre contenido fabricado**.

Medido en conformance (CU-7.b pasada 2). Petición: *"quiero poder marcar algunos gastos como deducibles para cuando toque hacer la declaración"*. `wf-prd-change` escribió, con **cero marcas**: (a) una capacidad inferida —*"el Usuario puede **consultar** el conjunto de gastos marcados como deducibles"*, cuando solo se pidió *marcar*—; y (b) más grave, **estrechó una exclusión explícita** del PRD, de *"Informes o exportaciones fiscales/contables: fuera del alcance"* a *"Generación de informes… **en formatos oficiales para la Agencia Tributaria**: fuera… El Usuario puede marcar y consultar dentro de la aplicación, pero la aplicación no produce el documento ni el fichero"*. Dónde queda esa frontera —etiquetar vs ayudar a declarar— es alcance que el usuario nunca dijo. El patrón agravante: **difirió lo pequeño y decidió lo grande**, dejando explícitamente para `wf-spec-analyze` preguntas más finas ("¿el total agregado?", "¿admite porcentaje?") mientras resolvía la frontera del producto por su cuenta. Contraste con la pasada 1, donde el agente **sí** paró y reportó una bifurcación de alcance equivalente ((a) reparto local vs (b) multiusuario real) y el orquestador improvisó un `AskUserQuestion` en main para resolverla: la misma clase de decisión, tratada de dos formas en dos pasadas — no porque el contrato lo previera, sino porque el agente se salió del guion una vez de dos.

**Decisión.** La anti-fabricación **no caduca al sellar**: rige cada escritura sobre el PRD. `wf-prd-change` Paso 5 gana la obligación de marcar `[ASUNCIÓN]` + entrada `[ASN-XXX]` (formato e invariante 1:1 de `kb-prd-expert`) todo lo que escriba y no trace al `--new-reqs` o a lo que el usuario dijo. Con las dos escapatorias **nombradas explícitamente**, no solo implicadas por la regla general: (i) **estrechar o reinterpretar una exclusión o regla transversal existente es decisión de producto y va marcada** —se cuela porque se siente como higiene ("si no la matizo queda contradictoria")—; (ii) **no vale diferir a `wf-spec-analyze` una decisión de alcance** — materia de Spec es el *cómo*, la frontera del producto es materia de PRD. Más: numeración continuando desde el `[ASN-XXX]` más alto presente y **recreando la sección** si el review ya la eliminó (arrancando en `ASN-001`); el `change-request.md` recoge el **texto** de cada asunción introducida, porque los IDs se reciclan entre ciclos y el ID solo no es trazabilidad; y la prohibición de resolverlas él mismo — corre en `context: fork` **sin `AskUserQuestion`**, así que no puede preguntar y por tanto no puede decidir.

**Efecto de diseño buscado:** el PRD queda `OPEN_ASSUMPTIONS`, y eso **encadena con maquinaria ya sellada** — el gate de `wf-prd-review`, validado en 6 pasadas (CU-2.e/2.j). No se añade gate nuevo: se hace alcanzable la rama que CU-7.b ya describía y que **ningún camino de código podía producir** (error del propio probe, corregido).

**Alternativas descartadas.**
- *Dar a `wf-prd-change` su propio gate con `AskUserQuestion`* → imposible tal cual: es `context: fork` y un subagente no puede renderizarlo. Requiere re-arquitecturar la skill al modelo de `wf-prd-review` (main orquesta, el experto analiza en fork, el gate vive en main). **Es la pieza 2, decidida pero aparte**, porque toca la estructura y obliga a re-probar CU-7 entera; la pieza 1 cierra el agujero grande apoyándose en algo ya medido.
- *Que el `prd-expert` pregunte parando y reportando, como en la pasada 1* → es exactamente la conducta que falló 1 de 2 veces. Convertir en contrato algo que depende de que el agente se salga del guion es la definición de garantía no medible.
- *Backstop determinista que detecte inferencias no marcadas* → no es mecanizable: decidir si una frase traza a la petición es juicio semántico. Lo mecanizable ya existe (el 1:1 y `READY`); lo que faltaba era la **obligación** de generar las marcas, que sí es normativa.
- *Prohibir a `wf-prd-change` tocar exclusiones y reglas transversales* → dejaría PRDs contradictorios tras un cambio legítimo. El problema no es tocarlas, es tocarlas **sin marca**.

**Consecuencias / aprendizaje.** Un invariante mantenido por *un* workflow no es un invariante del artefacto: hay que preguntarse **quién más escribe ese fichero**. Aquí la creación cumplía, el review cumplía y verificaba, y el tercer escritor no sabía que la regla existía — con el añadido perverso de que el verificador mecánico *confirmaba* el invariante (0 = 0) precisamente porque el contenido fabricado no se había marcado. **Un check de consistencia entre marcas y entradas no detecta la ausencia de ambas.** Corolario para la campaña: al sellar una garantía, enumerar los escritores del artefacto, no los lectores.

**Referencias.** `sdd/pipeline/prd/skills/wf-prd-change/SKILL.md` (Pasos 5, 7 y 8), `sdd/pipeline/prd/skills/kb-prd-expert/SKILL.md` (Regla 12, SSoT del formato), `sdd/conformance/casos-de-uso/cu-07-cambio-producto.md` (CU-7.b), `sdd/tests/test_install_sh.py` (`test_prd_change_marks_its_inferences`), `sdd/CHANGELOG.md`.

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
