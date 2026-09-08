# CU-3 — Generar las specs de un PRD

**Objetivo:** verificar que el camino PRD → specs por feature respeta el analyze
obligatorio, para en los gaps críticos, descubre features (no las inventa el PRD),
permite trabajar por subset, genera specs en paralelo y deja la trazabilidad e índice
correctos.
**Proyecto a usar:** el mismo producto real de CU-2, con su PRD ya `LISTO`. Idealmente
con alguna decisión de negocio sin cerrar, para que el analyze produzca al menos un gap
`[CRÍTICO]`.
**Cobertura automática:** parcial — los índices y marcadores deterministas
(`sdd-features-index.py`, `sdd-gap-conventions`) tienen tests, pero la calidad del
análisis, el discovery y los specs es juicio de los agentes → **manual**.

> [!IMPORTANT]
> **El analyze es obligatorio y las features no están en el PRD.** Ningún `F-XXX`
> existe hasta correr el discovery. Para una petición general ("crea las specs"), el
> entrypoint es `wf-spec-features-first <prd.md>`, **no** `wf-spec-discover`.

---

## 🧪 Qué se prueba aquí (por componente)

CU-3 es un **objetivo de usuario** (generar las specs de un PRD), no una sola skill: sus
escenarios ejercitan **ocho componentes** de la fase Spec. Marca cada escenario al ejecutarlo.
El estado de cobertura autoritativo (ejes happy/edge/harness/args) vive en
[`ROADMAP.md`](../ROADMAP.md) — esta vista es la **transpuesta** para leer/ejecutar el CU.

### `wf-spec-analyze` — analyze obligatorio y pureza (`sdd-spec-explorer`) (2)
- [ ] CU-3.a — El analyze es obligatorio y para en gaps críticos
- [ ] CU-3.k — Analyze: contaminación técnica detiene y las preguntas de riesgo van neutras

### `wf-spec-discover` — mapa de features y ownership (`sdd-spec-explorer`) (2)
- [ ] CU-3.c — Discovery: mapa de features y elección de subset
- [ ] CU-3.i — Discovery: ownership ambiguo de shared model para en checkpoint humano

### `wf-spec-features-first` — orquestador del flujo features-first (2)
- [ ] CU-3.d — Generación por feature (features-first) en paralelo
- [ ] CU-3.l — Features-first: `--features` con IDs inexistentes en el discovery

### `wf-spec-fast-track` — spec directo de una feature (`sdd-spec-writer`) (2)
- [ ] CU-3.e — Spec directo de una feature (fast-track)
- [ ] CU-3.j — Fast-track: documento multi-feature, pares de flags y feature ID inexistente

### `sdd-spec-auditor` — validate / conflict / readiness (read-only) (4)
- [ ] CU-3.f — Validar, conflictos y readiness
- [ ] CU-3.m — Validate en modo ligero: proporcionalidad sin relajar invariantes
- [ ] CU-3.n — Conflict: precondición de specs insuficientes
- [ ] CU-3.o — Readiness: sin índice, ciclos de dependencia y scope derivado

### `wf-spec-gap-resolve` — completar incompletos y confirmar inferidos (`sdd-spec-writer`) (2)
- [ ] CU-3.g — Completar HUs incompletas (gap-resolve)
- [ ] CU-3.q — Gap-resolve: confirmación de `[INFERIDO]` (tres vías)

### `wf-spec-delta` — evolución incremental del spec (`sdd-spec-writer`) (1)
- [ ] CU-3.h — Evolucionar un spec con requisitos nuevos (delta)

### orquestador de la fase Spec — guardrail de cambio de producto y oferta de rigor (3)
- [ ] CU-3.b — Expansión de alcance desde las respuestas del analysis
- [ ] CU-3.p — Delta / gap-resolve: un cambio de producto encubierto detiene y remite a wf-prd-change
- [ ] CU-3.r — El rigor (standard/ligero) se elige al crear el spec, no en el init (D-006)

> **Capa determinista** (no son escenarios manuales): los índices y marcadores
> (`sdd-features-index.py`, `sdd-gap-conventions`) están cubiertos por unittests; la calidad
> del análisis, el discovery y los specs es juicio de los agentes y queda en esta vista manual.

---

## 🔎 Verificación transversal de la pasada (aplica a cualquier escenario de CU-3)

Tres comprobaciones **mecánicas** sobre lo que la pasada dejó en disco y en los transcripts. Van
aquí y no dentro de un escenario porque no dependen de qué skill se ejercitó: cualquier corrida
que genere artefactos de Spec las admite.

**V1 — Ningún artefacto enseña comandos (ROADMAP 11.10).** Sobre el consumer, tras la pasada:

```bash
grep -rnE "\bwf-[a-z][a-z0-9-]*" spec/ prd/*_analysis.md prd/*_discovery.md prd/*_features.md \
  --include="*.md" | grep -v "Generado por:" | grep -v "Generado via:"
```

→ **Esperado: 0 líneas.** La procedencia en su forma sancionada (`Generado por: wf-spec-discover`)
es estado y se excluye a propósito.
→ **Acota a lo que la pasada escribe.** Un `prd/` entero arrastra los `changes/CR-*` de CU-7, que
son artefactos de la fase **PRD** y caen en el 11.10 **pendiente** de esa fase (12 hallazgos): son
positivos verdaderos, pero de otro CU, y ahogan la señal.
→ **Clasifica cada hallazgo antes de contarlo**, que no todos pesan igual:
  - **Fuga** — un nombre de workflow en un campo de **recomendación**. Es lo que este check busca.
  - **Procedencia fuera de forma** — decir de dónde salió el artefacto sin usar `Generado por:`
    (p. ej. *"4 informes por feature (fan-out de `wf-spec-features-first`)"*). No enseña a teclear
    nada, pero se escribe en la forma canónica o el check no puede distinguirla sola.
  - **Diagnóstico** — nombrar el workflow al explicar **qué produjo** un defecto encontrado
    (*"el fan-out paralelo de `wf-spec-features-first` lanzó varios escritores a la vez y dos
    reclamaron el mismo ID"*). **No es fuga**: quitarlo empeora el informe. La prueba, en una
    pregunta — **si borras el nombre, ¿el lector pierde comprensión o pierde una instrucción?**
→ **Dónde ha fugado las dos veces que se buscó a mano**, para mirar ahí primero: "Sugerencia de
resolución" del `_conflict_report`, los bloqueantes del `_readiness_report` y el
`Avisos de gobernanza` del `_discovery`.
→ **Validado contra la pasada 9** (artefactos pre-arreglo): devuelve **5** — 4 fugas y 1
procedencia fuera de forma. No es una regla vacua.
→ **Por qué este check existe:** 11.10 es el hallazgo más repetido de la campaña (pasadas 8 y 9)
y hasta v0.92.0 **ningún probe lo medía** — lo encontró un revisor a mano las dos veces. Un banco
no debe depender de eso.

**V2 — La prosa de los gaps está en claro ([[v0.92.0]]).** En el `_analysis.md` generado:

```bash
grep -nE "\b(CA|HU|THEN|GIVEN|WHEN)\b" prd/*_analysis.md | grep -vE "CA-[0-9]|HU-[0-9]"
```

→ **Ámbito: el `_analysis.md`, no los specs.** Dentro de un spec, `CA` y `HU` son el vocabulario
**estructural del propio documento** —su checklist dice *"cada CA referencia su HU padre"*— y eso
es correcto: quien lee un spec lee sus elementos por su nombre. La norma protege la prosa que le
explica **un hueco** a alguien de producto, no la nomenclatura interna del artefacto.
→ **Esperado:** solo coincidencias en la sección **Testabilidad** (donde el formato *es* el
asunto) y en la leyenda de marcadores. **FALLO:** una sigla suelta dentro del `Contexto`, el
`Problema` o la `Pregunta para el cliente` de un bloque `[P-XXX]` — *"el CA de X"*, *"sin THEN
verificable"*—, que es lo que obliga a quien presenta el gap a traducir teniendo contrato de
leerlo **verbatim**.
→ El campo `Afecta` lista IDs (`HU-001, HU-003`) y **no** cuenta como fuga.
→ **Validado contra la pasada 9**: devuelve 5 líneas, de las que **solo una** es real — el
`Problema` de un `[P-XXX]` con *"el CA … no tiene un THEN verificable"*. Las otras cuatro son la
leyenda de marcadores y la sección informativa, que son exactamente las exenciones de arriba.

**V3 — La norma de forma le llegó a quien escribió, y a tiempo ([[D-055]]).** En los transcripts
de subagente (`~/.claude/projects/<slug>/<session>/subagents/agent-*.jsonl`).

**Antes de medir, clasifica al agente**, porque los dos casos no admiten el mismo check:

- **Generador** (escribe un artefacto que no existía: `wf-spec-analyze`, `wf-spec-discover`,
  `wf-spec-fast-track`, `wf-spec-from-code`). **La guía de fase NO puede llegarle** — una regla de
  `.claude/rules/` se carga al tocar un path que matchea sus globs, y su primer contacto con ese
  path es el `Write` final. Pedirle que la tenga es pedir lo imposible.
- **Editor / auditor** (lee un artefacto existente y luego escribe o informa: `wf-spec-gap-resolve`,
  `wf-spec-delta`, `wf-spec-conflict`, `wf-spec-readiness`, `wf-spec-validate`). A este **sí** le
  llega, en el `Read`.

```bash
grep -c "Prueba de Pureza" agent-*.jsonl   # kb-spec-expert  → TODOS, y en las primeras lineas
grep -c "Spec Lab"        agent-*.jsonl    # guia de fase    → solo los editores/auditores
```

→ **Esperado en un generador:** `kb-spec-expert` presente **desde el arranque** (es lo que porta la
norma a tiempo); la guía de fase, indiferente.
→ **Esperado en un editor:** las dos.
→ **FALLO real, y es de contenido, no de carga:** que el artefacto salga con un nombre de workflow
o con jerga en la prosa — es decir, **V1 o V2 en rojo**. V3 solo sirve para explicar *por qué*
cuando alguna de esas dos falla.
→ **Cómo se localiza la inyección**, si hace falta el detalle: numera las líneas del `.jsonl` y
cruza la posición de la regla con la del `Read`/`Write` que la disparó. Medido en la pasada 10:
`Read prd/prd.md` en la 29 → guía de PRD en la **33**; `Write prd/prd_analysis.md` en la **44**, la
última llamada. Ese hueco es la demostración.

> **Por qué este probe cambió ([[D-055]]).** Nació como *"¿cargó cada agente la guía de su fase?"*
> tras la pasada 9, atribuyendo a los globs los 0 hits de los exploradores. La pasada 10, ya con
> los globs arreglados, volvió a dar 0 — y el transcript enseñó que la causa es **cuándo** se
> evalúa el match, no qué paths cubre. Un probe que pide una propiedad inalcanzable por
> construcción reporta FALLO donde no lo hay: el mismo daño que uno vacuo, en el otro sentido.

---

## ♻️ Reset del banco entre pasadas

Verificado contra el layout real del consumer (`myops-app-specs`, 2026-09-07). Sin esto la
pasada N+1 no arranca del mismo estado que la N y las corridas no son independientes
(`kb-sdd-conformance`, Regla 9 punto 6).

```bash
cp .conformance-attic/.prd-sealed.bak prd/prd.md
rm -f  prd/prd_analysis.md prd/prd_discovery.md
rm -rf spec/features spec/spec_features.md spec/spec_readiness_report.md
rm -rf .claude/agent-memory/sdd-spec-explorer .claude/agent-memory/sdd-spec-writer \
       .claude/agent-memory/sdd-spec-auditor
```

**Lo que NO se borra, y por qué:** `prd/changes/` y `prd/product-changelog.md` son los CRs de
CU-7 que llevaron el PRD de 1.0 a 1.5. El fixture **es** el PRD 1.5 con su historia detrás;
borrarlos cambiaría el documento de entrada.

**Comprobación de que el reset quedó bien**, antes de arrancar:

```bash
md5 -q prd/prd.md .conformance-attic/.prd-sealed.bak   # las dos iguales
cat .sdd/sdd-version.json                              # la versión que vas a medir
```

La versión instalada **se lee del fichero, no de la memoria de nadie**: la nota de la pasada 9
llegó a decir `v0.88.0` cuando el consumer tenía `0.89.0+e548522`, y la versión es justo lo que
nombra el contrato que la pasada mide.

---

## CU-3.a — El analyze es obligatorio y para en gaps críticos

**Precondición:** PRD `LISTO`, sin `_analysis.md` todavía.
**Mecanismo:** skill `wf-spec-analyze` → subagente **`sdd-spec-explorer`**. Output:
`<basename>_analysis.md`.

1. Le pides empezar a generar las specs del PRD.
   → **Esperado:** como no hay `_analysis.md`, ejecuta primero el analyze (o
     `wf-spec-features-first` lo lanza y **se detiene**), produce `_analysis.md` con
     gaps `[P-XXX]` y severidad, y te pide revisarlo antes de continuar.
2. El analysis deja gaps `[CRÍTICO]` abiertos y pides seguir igualmente.
   → **Esperado:** el gate se presenta con **UN SOLO** `AskUserQuestion`, para toda la tanda
     ([[D-053]]) y en un eje —cómo se responde—: *me los dictas aquí* / *los escribes tú en el
     fichero* / *continuar aceptando el riesgo*. **El flujo continúa en el mismo turno** con lo
     que elijas ([[D-045]]). No avanza en silencio. El conteo de críticos abiertos sale de
     `sdd-analysis-gaps.py --check` ([[D-042]]), **no** de la lectura del informe — y ese check
     corre **antes** de la rama que gobierna.
   → **FALLO ([[D-053]]):** que el menú se repita **una vez por gap** —decidir N veces lo mismo
     antes de poder responder nada—. Señal inequívoca: una opción que tiene que aclarar su
     propio ámbito (*"aplica a los N gaps, no solo a este"*) dentro de una pregunta individual.
   → **FALLO ([[D-053]]):** traer el detalle de los gaps (`contexto`/`problema`) **antes** de
     que elija. Si dice *"los escribo yo"* o *"continuar"*, ese detalle no hacía falta, y
     traerlo mete prosa del informe en el contexto de main por la puerta de atrás.
   → **FALLO:** decidir la rama citando una lectura propia del `_analysis.md`; tratar un
     veredicto `VACUOUS` (documento no parseado) como "sin gaps críticos"; **auto-armar** el
     `--allow-open-critical-gaps` sin que tú lo elijas ([[D-026]]); o pedirte que **vuelvas a
     ejecutar** el workflow con el flag — eso repite parseo, readiness y check de gaps, y era el
     síntoma de que el gate vivía en un fork que no podía preguntar ([[D-045]]).
3. **El mensaje del gate te dice qué se te va a pedir, sin que abras el fichero** ([[D-042]]).
   → **Esperado:** path exacto del `_analysis.md`, el recuento, y los IDs `[CRÍTICO]` **con su
     título en una línea cada uno**, para que veas el alcance **antes** de elegir cómo
     responderlos. En la rama *"los escribes tú"*, además, qué se sustituye
     (`- **Respuesta**: _(pendiente)_`).
   → **FALLO:** un "responde las preguntas marcadas como `_(pendiente)_`" genérico que
     te obliga a bucear entre todos los gaps para saber cuáles bloquean.
4. **Cómo se dictan y quién las escribe** ([[D-042]], [[D-053]]). Elige *"me los dictas aquí"*.
   → **Esperado:** main te los presenta **en la conversación, de uno en uno** —no con
     `AskUserQuestion`: la respuesta es prosa abierta, no una elección entre opciones—, y cada
     uno llega **con su `contexto`, su `problema` y su `afecta`**, no solo con la pregunta
     pelada. Eso sale de `sdd-analysis-gaps.py --list --gap <P-XXX>`. Respondes en texto libre y
     el hilo principal aplica con `--answer P-XXX "texto"` por `Bash`; el fichero cambia **solo**
     en esa línea.
   → **FALLO ([[D-053]]):** pedir la respuesta con un `AskUserQuestion` y que el camino real sea
     su escotilla *"Other"* — la pantalla del selector no tiene sitio para el contexto, así que
     la pregunta te llega amputada. O presentarte los N gaps juntos y **repartir** tu respuesta
     entre los IDs: repartir es interpretar lo que no dijiste literalmente.
   → **FALLO (tres formas):** que main haga `Read`/`Edit`/`Write` del `_analysis.md`;
     que **rehúse** ayudar remitiéndote al editor cuando existe vía sancionada; o —el
     grave— que **complete o reinterprete** una respuesta que no diste.
   → **Ojo al verificar:** que el frontmatter no declare `Write` **no lo impide**
     (`allowed-tools` no es enforcement, [[D-038]]). Hay que mirar los logs.

5. **Cómo delega el orquestador** ([[D-043]], corregido por [[D-045]]) — se lee en los logs de
   `wf-spec-features-first`, no hay que provocarlo.
   → **Precondición estructural ([[D-045]]):** `wf-spec-features-first` corre en el **hilo
     principal**, no en `context: fork`. Desde un fork esta propiedad **no es alcanzable**: con
     fork mode activo —el default interactivo— un subagente no puede pedir el primer plano para
     sus delegados. Si en los logs el workflow aparece como subagente, el probe no aplica: es un
     FALLO de arquitectura, no de conducta.
   → **Esperado ([[D-047]]):** invoca el analyze con la tool `Agent` y `subagent_type:
     sdd-spec-explorer`, y **el informe del delegado le llega entregado** por una de las dos
     vías: el `tool_result` de esa llamada (si pasó `run_in_background: false`) o la
     **notificación de fin** del agente, habiendo cedido el turno sin hacer nada más mientras
     tanto. Un solo reporte final.
   → **La vía (b) no es un FALLO.** Medido en la pasada 4: el flag viajó en **0 de 10**
     delegaciones y las 10 esperas fueron impecables. Lo que se mide aquí es **quién trae el
     informe**, no en qué turno llega.
   → **Hay una tercera puerta, y el contrato todavía no la gobierna: `SendMessage`** (observada
     por primera vez en la pasada 8). En vez de lanzar un delegado nuevo, main puede **reanudar
     uno anterior** —`ToolSearch {"query": "select:SendMessage"}` y luego `SendMessage` al
     `agentId`— para reaprovechar el contexto que ese agente ya tenía. Es legítimo como táctica
     y puede ser mejor que relanzar, pero **`SendMessage` no admite `run_in_background`**, así
     que ni [[D-043]] ni [[D-050]] le aplican, y su `tool_result` es **un acuse de recibo**
     (`{"success":true,"message":"Resuming agent…"}`), no el informe. Tiene exactamente la forma
     que el resto de este probe marca como FALLO.
     **Cómo se verifica mientras el contrato no lo cierre (ROADMAP 11.11), dos comprobaciones
     separadas:**
     1. **¿Llegó el informe?** El acuse **no** cuenta. Hay que localizar el texto del veredicto
        del agente reanudado en el contexto de main —en un turno posterior— antes de que main
        siga. **FALLO:** que main continúe al paso siguiente teniendo solo el `success:true`.
     2. **¿El agente reanudado seguía sabiendo lo que se le supone?** Un agente puede haber sido
        compactado entre su primera invocación y la reanudación. Se cruza lo que responde con lo
        que tenía en su `.jsonl` la primera vez: si cita algo que solo estaba en la parte
        perdida, no lo estaba recordando.
     **No lo des por PASS "porque salió bien".** En la pasada 8 salió bien y el probe no tenía
     criterio: lo resolvió el revisor a mano, que es justo lo que un banco no debe necesitar.
   → **El flag ya no lo fuerza ningún hook — lo habilita el proyecto ([[D-050]]).** [[D-048]]
     puso un `PreToolUse` (`sdd-agent-sync.py`) que denegaba la delegación sin el flag;
     [[D-050]] lo **retiró entero** al descubrir la causa real: con fork mode activo el flag
     ni siquiera llegaba a evaluarse. Lo que lo sustituye es
     `CLAUDE_CODE_FORK_SUBAGENT=0` en el `settings.json` del consumer, que devuelve el
     efecto a `run_in_background: false`. **Verifica eso, no el hook:** que la variable esté
     en el `settings.json` del consumer. **No busques `deny` con `[SDD-SYNC]`, ni el script en
     `.sdd/scripts/`, ni `SDD_ALLOW_ASYNC_AGENTS`** — nada de eso existe ya, y su ausencia
     **no** es señal de instalación incompleta.
   → **FALLO de contexto ([[D-048]], antes O-8):** que el orquestador cargue un artefacto
     entero por `Bash` —`cat` del `_features.md`, del PRD o del analysis, o un `grep -A/-B`
     generoso—. La prohibición es sobre **lo que acaba en su contexto**, no sobre la tool: un
     `grep -c`, un `grep -nE "^### F-[0-9]{3}:"` o el stdout de un script son legítimos.
   → **FALLO (cinco señales, cualquiera basta):** que el `tool_result` diga *"Async agent
     launched"* y el flujo **continúe igualmente sin esperar la notificación**; espera a mano
     mirando si el artefacto aparece o si deja de crecer; lectura del buzón intermedio del
     harness (`tasks/*.output`) para saber si el delegado terminó; un segundo agente relanzado
     sobre el mismo trabajo; o el reporte final **emitido dos veces** (delata que el stream
     asíncrono cerró después). Deducir del disco no es esperar.
   → **FALLO en el fan-out (Pasos 5 y 7, donde hay barrera — [[D-047]]):** que las N llamadas
     `Agent` salgan en **mensajes separados** en vez de en uno solo. Hoy es inocuo porque van
     asíncronas y solapan igual, **pero eso es exactamente lo que lo hace peligroso**: el día
     que el flag surta efecto, mensajes separados serializan el fan-out (cada uno espera a su
     agente antes de emitir el siguiente). Se mide contando los mensajes del transcript, no los
     agentes. En la misma familia: continuar al Paso 6 sin tener las N respuestas.
   → **FALLO grave y silencioso — el dato fabricado ([[D-045]]):** que el orquestador **reporte
     como venido del delegado** un path, un veredicto o un recuento que ha obtenido él por su
     cuenta. Es el que no se nota: el informe que sube *parece correcto*. Se detecta cruzando lo
     que el orquestador reportó con lo que el delegado escribió en su `.jsonl` — si el
     orquestador nunca recibió el `tool_result` con el informe, todo lo que citó es suyo.
   → **FALLO adicional (Regla de oro):** que el orquestador haga `cat`/`Read` del PRD, del
     `_analysis.md` o del `_discovery.md` — lo que necesita sale del script, de una extracción
     acotada por `grep`, o del reporte del delegado.
   → **FALLO adicional (la excusa no comprobada, [[D-045]]):** que justifique un atajo afirmando
     una limitación del entorno sin haberla provocado. Sin error de validación en el transcript,
     la limitación no está demostrada.
   → **Sin salto sobrante ([[D-044]]):** el delegado **ejecuta** la sub-skill (lee su
     `SKILL.md`), **no** la invoca con el `Skill` tool. **FALLO:** que aparezca un agente con
     `spawnDepth: 3` — sería el clon que el re-despacho forkea —, o que el delegado responda
     *"lo he lanzado en segundo plano, te aviso"* antes de tener el resultado.
   → **Cómo se verifica (instrumento de la campaña):** en
     `~/.claude/projects/<proyecto>/<sesión>/subagents/` hay un `.jsonl` y un `.meta.json` por
     subagente, con `spawnDepth`, `parentAgentId` y **los parámetros exactos de cada tool call**
     (ahí se lee si `run_in_background: false` viajó de verdad). **No hace falta poner los
     agentes en background para capturar sus logs — y hacerlo contamina esta medición**, porque
     un padre backgroundeado hace indistinguible el estado de sus hijos.

**Resultado:** PASS si genera el analysis, presenta el gate de críticos por veredicto de
script **sin relanzarse**, te dice cuáles son sin abrir el fichero, ni escribe ni inventa
las respuestas, y recibe el informe de su delegado en la propia llamada · FALLO si salta el
analyze, avanza con críticos sin elección explícita, decide por lectura propia, toca el
informe a mano, espera a mano, o **reporta como del delegado un dato que reconstruyó él**.
**Desviación → reportar:** issue citando `CU-3.a`.

> **Pasada 1 (2026-08-02, v0.76.0) — PASS en el paso 1; origen de [[D-042]].** El analyze
> corrió primero y el flujo **se detuvo** con `spec/features/` intacto; pureza `APROBADO`
> con la línea borderline de L95 reconocida como patrón válido (no sobre-disparó
> `REQUIERE_LIMPIEZA_PRD`); 5 `[CRÍTICO]` + 6 `[INFORMATIVO]`, con P-001 y P-009 marcados
> `[PUEDE_REQUERIR_CR]` y redactados en **neutro**. El paso 2 **no se ejercitó**: el
> orquestador se adelantó ofreciendo él mismo la bifurcación antes de que el usuario
> empujara — conducta correcta y más fuerte que la pedida, pero el probe no llegó a correrse.
>
> **El hallazgo:** main ofreció *"me los dictas y **yo los anoto** en el análisis"*, una vía
> que **el contrato no contemplaba** — los tres sitios que hablan del tema (SKILL de analyze,
> Paso 2.5 de features-first y la cabecera del propio artefacto) dicen siempre que escribe el
> usuario. Vacío de la misma forma que cerró [[D-038]] en la fase PRD. Al investigarlo apareció
> el defecto mayor: la detección de "¿quedan `[CRÍTICO]` sin responder?" era **juicio de agente
> sobre prosa** gobernando dos ramas duras. Ambos cerrados en [[D-042]]; los pasos 2, 3 y 4 de
> arriba son nuevos y **no tienen aún ninguna pasada**.
>
> **El segundo hallazgo — busy-wait ([[D-043]]).** El log de `wf-spec-features-first` es literal:
> `Skill(wf-spec-analyze)` → `Monitor(wait for prd_analysis.md)` → `cat …/prd.md` (el orquestador
> cargándose el PRD entero) → `ls -la prd/` → *"I'll wait for the analysis skill to finish"* →
> `ls -la prd/` otra vez → reporte final **duplicado**. Causa: el Paso 5 prescribía la tool exacta
> y los otros cuatro puntos de delegación decían solo *"invoca `/wf-spec-analyze`"*; el fork
> rellenó el hueco con `Skill` (que ni estaba en su `allowed-tools` — tercera confirmación de
> [[D-038]]) y sin handle síncrono se puso a sondear. Al contarlo: **7 skills delegaban por
> `Agent` y solo `wf-prd-create` pasaba `run_in_background: false`**. Cerrado en [[D-043]] con
> barrido de las 7 + regla blocking `AGENT-DISPATCH-UNSYNCED`. El paso 5 de arriba es nuevo y
> **no tiene aún ninguna pasada**: el linter garantiza que el flag está escrito, no que el
> orquestador lo teclee.

> **Pasada 2 (2026-08-02, v0.79.0, `myops-app-specs`, turnos 1–2) — pasos 1, 2, 3 y 5 PASS;
> origen de [[D-044]].** Los cinco síntomas de la pasada 1 desaparecieron: delegó con
> `Agent(subagent_type: sdd-spec-explorer)` en vez de `Skill`, **cero `Monitor`**, cero `ls`
> repetido sobre `prd/`, **un solo** reporte final, y **no hizo `cat` del PRD**. El **paso 2**,
> que la pasada 1 no llegó a ejercitar, corrió por fin: gate explícito con `AskUserQuestion` y
> conteo tomado de `sdd-analysis-gaps.py --check --json` (`CRITICAL_OPEN`, 7 IDs). El paso 3
> también: el mensaje de cierre llevó path, los 7 `[P-XXX]` **cada uno con su pregunta** y qué
> sustituir. El **paso 4 no se ejercitó** (se eligió dictar y luego se cambió de rumbo).
> **[[D-041]] queda MEDIDO por primera vez, 1/3:** `.claude/agent-memory/` **no reapareció**.
>
> **Hallazgo → [[D-044]].** Los transcripts de subagente probaron que `run_in_background: false`
> **sí viajaba**, y que el defecto estaba un nivel más abajo: el prompt *"Ejecuta el skill
> `/wf-spec-analyze`"* hacía que el delegado re-despachara con `Skill`, forkeando un **clon**
> (`spawnDepth: 3`, mismo `agentType`). Coste medido: **210 KB** de envoltorio por delegación, y
> el salto extra otra vez asíncrono, con un *"lo he lanzado, te aviso"* emitido antes de tener
> nada.
>
> **Observación A — el análisis no es reproducible.** Mismo PRD byte-idéntico: pasada 1 dio
> **11 gaps / 5 críticos**; pasada 2, **12 gaps / 7 críticos**. Los conjuntos se solapan (el
> contenido de la visión general aparece en ambas con ID distinto), pero la partición
> crítico/informativo se mueve. **Consecuencia metodológica: ningún probe puede citar `P-XXX`
> concretos** — se cita el veredicto y el conteo, no los IDs. Y como candidato de contrato: que
> el nº de **bloqueantes** oscile 5→7 sugiere que el umbral crítico/informativo de
> `kb-gap-conventions` está menos definido de lo que se creía (familia [[D-033]]/[[D-034]]/[[D-035]]:
> consistencia de juicio → se afila el KB).
>
> **Observación B — el `grep` que D-042 debía haber hecho innecesario.** Main ejecutó
> `grep -n "CRÍTICO" -A 12 prd_analysis.md | head -150` **después** de que el delegado le
> hubiera entregado los 7 IDs con sus preguntas. No viola la regla (que nombra
> `Read`/`Edit`/`Write`), pero mete ~150 líneas del informe en el hilo principal: el mismo coste
> que [[D-042]] evitaba, entrando por otra puerta. Candidato.
>
> **Pregunta de contrato abierta.** Ante *"Los gaps ya los miraré luego. Genérame ya las specs"*,
> main auto-armó `--allow-open-critical-gaps` sin abrir un gate nuevo — pero el menú de 3 opciones
> estaba en pantalla **un turno antes**, con la opción 3 descrita como *"requiere el override
> explícito que solo puedes autorizar tú"*. ¿Autoriza un menú del turno N un override en el N+1?
> [[D-026]] dice que la impaciencia no es autorización; aquí hubo elección informada previa. Se
> deja como pregunta, no como FALLO.

> **Pasada 3 (2026-08-20, v0.80.0, `myops-app-specs`, banco limpio) — pasos 1, 2 y 3 PASS;
> [[D-044]] PASS; paso 5 **FALLO**; origen de [[D-045]].** [[D-044]] queda medido por primera vez y
> pasa: `spawnDepth` máximo **2**, cero clones, el delegado leyó el `SKILL.md` y lo ejecutó.
> [[D-041]] 2/3: `agent-memory/` no reapareció. El paso 4 **no se ejercitó** (se eligió "continuar
> asumiendo el riesgo" en el gate). Tercera muestra de la Observación A: **11 gaps / 7 críticos**
> (serie 11/5 → 12/7 → 11/7: el total oscila, la partición crítico/informativo también).
>
> **El fallo del paso 5, en tres capas.** (1) El fork delegó **sin** `run_in_background: false`,
> teniendo la instrucción literal en su contexto — verificado en su transcript. (2) Sin resultado,
> improvisó la espera: `find` en bucle con `sleep 3`×160, polling del `.output` del harness con
> `sleep 45`, y dos lecturas de ese fichero. (3) **Nunca recibió el informe del delegado**:
> reconstruyó path, veredicto y conteo con `find` + `grep` + script y se los reportó a main como
> si fueran del delegado. El informe del explorer, completo, se tiró. La tercera capa es la que
> importa: lo que subió *parecía correcto*.
>
> **La causa no era conductual, era arquitectónica.** Investigándolo se cayeron dos premisas.
> Primera: en la **pasada 2** el flag **sí se pasó** y el `tool_result` fue igualmente
> *"Async agent launched successfully"* — o sea que [[D-043]] nunca funcionó desde un fork, y lo
> que interpretamos como éxito era el parámetro viajando, no surtiendo efecto. Segunda: la doc de
> Claude Code lo explica —con fork mode activo, el default interactivo, *"Claude no puede pedir el
> primer plano"*—, y las únicas delegaciones síncronas registradas en el consumer (3 de 20) salen
> **todas del hilo principal**. Verificado además en vivo el 2026-08-26 con Claude Code 2.1.245:
> main → `Agent(run_in_background: false)` devuelve el informe dentro del `tool_result`.
> Cerrado en [[D-045]] sacando `wf-spec-features-first` del fork.
>
> **Reinicio de recuentos.** El cambio de arquitectura invalida las pasadas anteriores de este
> escenario: los pasos 1–5 vuelven a **0/3**. Duele en el paso 1, que iba 3/3.
>
> **Hallazgo de método — el banco incluye el ciclo de vida de los agentes.** La **pasada 2**
> estaba contaminada y no lo sabíamos: se backgroundeó un agente a mano para capturar logs. Y
> `Cmd+B` **no deja rastro en los transcripts** (cero coincidencias en los 20 ficheros de sesión
> del consumer), así que "background" por decisión del harness y "background" por decisión del
> humano son **indistinguibles a posteriori**. Recogido en la Regla 9 de `kb-sdd-conformance`.
>
> **Hallazgo de autoría — la prohibición que enseña.** Los dos forks hicieron
> `ToolSearch {"query": "select:Monitor"}` justo después de delegar. `Monitor` es una tool
> *deferred*: solo tenían el nombre, y se lo dio **nuestra propia cláusula anti-sondeo**. El
> cuerpo de un SKILL viaja al contexto del agente; las señales de FALLO viven aquí, que no se
> instala. Recogido en `kb-sdd-creation-guide`.

> **Pasada 4 (2026-08-26, v0.81.0+a29d67b, `myops-app-specs`, banco limpio) — pasos 1, 2, 3, 4 y
> 5 PASS; [[D-045]] medido y confirmado; origen de [[D-046]] y [[D-047]].** La mejor pasada de la
> campaña: 36 tool calls, 10 subagentes, **todos con `spawnDepth: 1` y sin `parentAgentId`** — no
> hay `.forked-skill.json`, features-first corrió en main. [[D-044]] PASS (cero clones),
> [[D-041]] **3/3 → sellable**.
>
> **El paso 4 pasa por primera vez en toda la campaña.** Once respuestas dictadas entraron por
> `sdd-analysis-gaps.py --answer P-XXX 'texto'` (en dos scripts batched), decrementando el
> contador hasta `CRITICAL_ANSWERED`, con **cero `Read`/`Edit`/`Write`** del `_analysis.md`. Los
> cuatro gates se presentaron con `AskUserQuestion` **sin relanzar el workflow** ni una sola vez —
> se acabó el "vuelve a ejecutar añadiendo `--allow-…`". Y [[CU-3.b]] queda medido por primera vez:
> una respuesta que ampliaba alcance (P-008) disparó el guardrail y remitió a `wf-prd-change` sin
> continuar; al cortar el cambio, el PRD quedó **byte-idéntico** a `.prd-sealed.bak`.
>
> **Hallazgo 1 — el flag no viaja, y eso resultó ser culpa del contrato ([[D-047]]).**
> `run_in_background: false` apareció en **0 de las 10** llamadas `Agent`, en tres skills
> distintas. Pero las 10 esperas fueron correctas: main cedió el turno y consumió el informe de la
> notificación de fin, sin sondear nada. Diez de diez no es despiste — nuestro criterio
> (*"como resultado de tu propia llamada… ninguna otra cosa cuenta"*) excluía por redacción una
> ruta legítima de la plataforma. Aplicada la **Regla 9.4**, el defecto estaba en el contrato, no
> en la conducta. Corregido: dos vías sancionadas, y el flag obligatorio donde hay **barrera**.
>
> **Hallazgo 2 — el índice no ve el discovery ([[D-046]], FALLO de [[CU-3.d]]).** Con
> `artifacts.prd != artifacts.spec`, `sdd-features-index.py` globeaba `*_discovery.md` solo dentro
> de la raíz spec. Resultado: `spec/spec_features.md` con `discovery=no`, **3 features de 9**,
> **cero `PENDIENTE_GENERACIÓN`** y el nombre del proyecto tomado del directorio. Las 6 features
> pendientes desaparecieron del hub. Y lo peligroso: **main narró al usuario la tabla correcta de
> 9** mientras el fichero decía 3 — la conversación dice la verdad y el artefacto no. Mismo defecto
> destapado en `wf-spec-readiness`, que buscaba los `_conflict_report.md` solo en la raíz mientras
> el fan-out los escribe junto a cada spec.
>
> **Hallazgo 3 — el fan-out en mensajes separados.** Los tres `sdd-spec-writer` salieron en
> msg#62/63/64 y los tres auditores en msg#82/83/84, contra el `CRÍTICO: … en un único mensaje` del
> SKILL. Hoy inocuo (van asíncronos), **pero load-bearing en cuanto el flag funcione**: serializaría
> el fan-out. Es un requisito enmascarado por el incumplimiento de otro — los dos se rompen a la vez.
>
> **Hallazgo 4 — los auditores se contradicen.** Sobre el mismo par F-001/F-005, dos declararon
> `SIN_CONFLICTOS` y el tercero levantó `CF-001` (ALTA). **Main lo gestionó bien**: no arbitró por su
> cuenta y escaló al readiness como cuarto lector independiente con encargo explícito. Codificado en
> el Paso 7 y en `wf-spec-readiness` (un `SIN_CONFLICTOS` no refuta un hallazgo; nunca cerrar por
> mayoría). Familia [[D-033]]/[[D-034]]/[[D-035]].
>
> **Conducta destacable:** main **reportó al usuario los hallazgos 2 y 4 por su cuenta**, en su
> mensaje de cierre, nombrando la causa del índice ("el regenerador lo busca con un glob dentro de
> `spec/`, y en topología *authoring* vive en `prd/`") y la falta de consolidación de los informes.
> Detectar y declarar un defecto del propio ecosistema mientras se ejecuta es exactamente lo que el
> banco quiere premiar.
>
> **Cuarta muestra de la Observación A, y la peor:** **16 gaps / 11 críticos** (serie
> 11/5 → 12/7 → 11/7 → **16/11**), un salto del ~45% en el total sobre un PRD byte-idéntico. Y el
> discovery tampoco es reproducible: **9 features frente a 8** en la pasada 3, con una `F-009:
> security-lock` derivada de la regla transversal de PIN/biometría. Abierto como `O-12`.
>
> **Recuentos tras la pasada:** pasos 1/2/3 **1/3**, paso 4 **1/3** (primera vez), paso 5 **1/3**
> en anti-sondeo. [[CU-3.b]] **1/3**, [[CU-3.c]] **1/3**, [[CU-3.d]] **FALLO** (índice),
> [[CU-3.r]] PASS.

> **Pasada 5 (2026-08-26, v0.82.0, `myops-app-specs`, banco limpio) — ABORTADA en el paso 1 por
> un bug del ecosistema; origen de [[D-049]].** No mide CU-3.a: el flujo se detuvo en la primera
> delegación. Lo que sí dejó:
>
> **[[D-046]] PASS determinista, en vivo.** Con el mismo `prd_discovery.md` en disco y solo el
> script cambiado, el índice pasó de **3 a 9** features. Es el fix de esta versión medido de forma
> aislada, sin conducta de por medio.
>
> **[[D-048]] confirmado a medias.** El hook **disparó** — el payload de `PreToolUse` trae
> `tool_input` para la tool `Agent`, que era la incógnita que no se había podido verificar. Pero
> el gate resultó insatisfacible: el reintento llegó con `run_in_background` como **cadena**
> `"false"` y el hook comprobaba `is False`. Y devolvió **el mismo mensaje las tres veces**, así
> que el agente concluyó —razonablemente, con lo que podía observar— que el contrato era
> incumplible. Corregido en [[D-049]]: dos mensajes distintos, y el segundo devuelve el valor
> recibido.
>
> **CU-9.n: PASS en el eje crítico, FALLO en el diagnóstico.** El orquestador **no rodeó** —ni
> `Skill`, ni hacer el análisis él, ni degradar el paso—, paró a los tres intentos y ofreció la
> escotilla. Esa es la salida sancionada, y funcionó. Pero al explicarlo afirmó que *"la tool
> `Agent` de esta sesión no declara `run_in_background` y tiene cerradas las propiedades extra"*:
> falso, autorrefutable (con `additionalProperties: false` la llamada habría muerto en validación,
> no habría llegado al hook) y **escrito como hecho en un bug report**. Es la conducta de
> [[D-045]] reaparecida en cuanto volvió la presión "prohibido X y necesito X". Tenía el hook a un
> `Read` de distancia, en `.sdd/scripts/`, y no lo abrió.
>
> **Sin muestra de la serie de gaps:** el analyze no llegó a correr.

> **Pasada 6 (2026-08-27, v0.83.0, `myops-app-specs`, banco limpio, **modelo `sonnet-5`/`opus-5`**
> — primer cambio de modelo de la campaña, ver procedencia abajo) — la primera de la campaña que
> llega al final con todo dentro. Pasos 1–5 PASS; [[D-050]] medido; [[D-046]] y [[D-047]]
> confirmados en flujo real.** 21 tool calls para el flujo entero (la pasada 4 gastó 36), 9
> subagentes, **todos `spawnDepth: 1` y sin padre**.
>
> **La medición que lo cambia todo: 5 de 5.** `run_in_background: false` viajó en **las cinco**
> delegaciones —analyze, discovery, tres escritores, tres auditores, readiness— y el informe volvió
> **dentro del `tool_result`** cada vez. Contra 0 de 10 en la pasada 4. Y viajó como **booleano**,
> emitido por el modelo siguiendo la prosa del SKILL, sin ningún mensaje de error recordándoselo:
> confirma que el 0/10 nunca fue desobediencia, era una petición sin sitio donde aterrizar
> ([[D-050]]).
>
> **Fan-out en un único mensaje, las dos veces** ([[D-047]]). Los tres `sdd-spec-writer` salieron en
> un solo mensaje del asistente, y los tres `sdd-spec-auditor` en otro — verificado agrupando los
> `tool_use` por `message.id`, no contando entradas del `.jsonl`. En la pasada 4 fueron seis
> mensajes.
>
> **[[D-046]], las dos mitades, en flujo real.** El índice cruzó la frontera de topología
> (`> Discovery: ../prd/prd_discovery.md (fuera de esta raíz de artefactos)`) y registró **8 de 8**
> features, con las 5 no generadas visibles como `PENDIENTE_GENERACIÓN`; `--check` da `EN_SYNC`. Y
> el readiness **encontró los tres `_conflict_report.md` junto a cada spec** —los nombró con path—
> y además **declaró en voz alta** lo que faltaba: *"fan-out por feature, sin informe consolidado en
> `spec/`"*.
>
> **[[D-047]], el arbitraje, con divergencia legítima.** `expense-categories` declaró
> `SIN_CONFLICTOS` mientras los otros dos levantaban `CF-001`. Esta vez la divergencia **era
> correcta** —F-003 no es parte de ese par— y el readiness lo resolvió sin promediar: dejó F-003
> `BLOQUEADA` por dependencia **transitiva**, lo distinguió explícitamente de un conflicto propio, y
> lo justificó **citando fichero y línea** de los dos README. Exactamente la conducta que pedía la
> regla.
>
> **Paso 4 PASS (2ª vez).** Dos `--answer` encadenados con los textos dictados; cero `Read`/`Edit`/
> `Write` del analysis. **O-8 PASS:** el único `cat` de la sesión fue el `output_template.md` de la
> propia skill — material de skill, no artefacto del proyecto. **PRD byte-idéntico** al sellado;
> `agent-memory` ausente ([[D-041]]); cero HUs `[INCOMPLETO]`.
>
> **Hallazgo que cae solo, y es material de [[CU-3.o]]:** el readiness detectó y nombró un **ciclo
> de dependencias explícito F-001 ↔ F-003**. Ese escenario estaba sin medir.
>
> **Ruido del harness, no del contrato:** un `AskUserQuestion` llegó malformado
> (`__unparsedToolInput`) y se reintentó bien acto seguido.
>
> **⚠ Procedencia — cambió el modelo, y eso reordena la serie de gaps.** Esta pasada corrió con
> **`claude-sonnet-5`** (verificado en el `.jsonl` del subagente); las pasadas 1–5 fueron con
> `claude-sonnet-4-6`. Los agentes se bumpearon a `opus-5`/`sonnet-5` **una hora antes** de
> lanzarla.
>
> Sexta muestra de la Observación A y la más extrema: **5 gaps / 2 críticos**, contra la serie
> 11/5 → 12/7 → 11/7 → 16/11. Discovery: **8 features** (frente a 9 y 8). Pero **no es comparable
> con las anteriores**: cruza una frontera de modelo, que es justo lo que la Regla 9 punto 3 avisa
> que hace caducar una validación en silencio. El sospechoso principal del salto es el modelo, no
> fork mode. `O-12` sigue abierta, pero su serie se parte aquí: hacen falta ≥2 muestras más en
> `sonnet-5` antes de comparar nada.
>
> **Reinicio de recuentos, por partida doble.** [[D-050]] cambia el mecanismo de ejecución de las
> delegaciones **y** el modelo de los agentes cambió a la vez — dos variables movidas en la misma
> pasada, que es exactamente lo que el banco pide no hacer. Esta es la **1/3** del régimen nuevo, y
> conviene que la 7 y la 8 no muevan nada más.
>
> **Lo que esta pasada NO midió:** fue una pasada *fácil*. Sin `[INCOMPLETO]`, sin disparar el
> guardrail de alcance ([[CU-3.b]] no se ejercitó), y con el índice `EN_SYNC` a la primera. Falta
> ver cómo se comporta el régimen nuevo **cuando algo falla a mitad del fan-out**.

> **Pasada 7 (2026-08-31, v0.83.0, `myops-app-specs`, banco limpio, modelo `sonnet-5`/`opus-5`) —
> la mejor de la campaña. Pasos 1–5 PASS (2/3); [[CU-3.b]] medido de verdad por primera vez; la
> rama de alcance derivado, nunca antes ejercitada, PASS entera.** 27 tool calls, 11 delegaciones.
>
> **11 de 11 con el flag**, booleano y sin que nadie se lo recordara. **Los dos fan-outs en un
> único mensaje** (4 escritores, 4 auditores), verificado agrupando por `message.id`. **Cero
> artefactos cargados por main** — el único `cat` de la sesión fue el `output_template.md` de la
> propia skill. Índice 8/8 y `EN_SYNC`. PRD **byte-idéntico** tras dos desvíos de alcance.
> `agent-memory` ausente. Cero HUs `[INCOMPLETO]`.
>
> **[[CU-3.b]] saltó en dos etapas, y las dos veces con razón.** (1) **En main**, sobre una
> respuesta cargada a propósito (reglas de auto-confirmación "guardadas y reutilizables"): nombró
> las dos señales exactas y detectó incluso que *"por comercio"* presupone comercio como entidad
> con identidad. (2) **En el discovery**, sobre otras dos respuestas que el operador creía
> conservadoras y no lo eran — verificado contra el PRD: comprometía *"marcar una deuda como
> saldada, total o parcial"* (un estado) frente a un saldo numérico decreciente, y su bloque de
> ahorro **no menciona cuentas** frente a un acoplamiento con `Cuenta/Tarjeta` y `Movimiento`.
>
> **Y por qué hicieron falta dos etapas — no es un defecto, es la Regla de oro produciendo defensa
> en profundidad.** Main **no lee el PRD**, así que solo puede juzgar por el texto de la respuesta:
> pilla lo que se delata solo. Comparar contra lo que el PRD comprometía **exige tenerlo delante**,
> y eso solo puede hacerlo el delegado del discovery. Las dos capas cubren cosas distintas por
> construcción. Conviene no "arreglar" esto dándole el PRD a main.
>
> **La rama de alcance derivado, medida por primera vez.** Elegido *continuar* en el gate ([[D-026]]:
> el override lo arma el usuario), los marcadores propagan **discovery → spec → índice** y **solo a
> quien toca**: F-006 y F-008 con `Origen de alcance: PRD + analysis respondido` + su aviso citando
> el gap concreto, y F-001/F-005 limpias con `ninguno`. El índice deriva para las dos afectadas el
> estado **`REQUIERE_CAMBIO_PRD`**, que no se había observado nunca en toda la campaña.
>
> **El arbitraje de [[D-047]], ejecutado mejor de lo que está redactado.** `debt-tracking` declaró
> `SIN_CONFLICTOS` frente a tres `CONFLICTOS_DETECTADOS` sobre `CF-001`. El readiness escribió
> *"el criterio que decide aquí es la lectura del texto, **no el recuento 3 a 1**"*, explicó que el
> voto minoritario no refuta porque esa feature *"literalmente no tenía superficie para verlo"*,
> citó los CAs concretos (F-001 `CA-002` exige categoría obligatoria; F-008 `CA-004` crea un
> `Movimiento` sin ese paso) y listó **los cuatro** informes, marcando el discrepante como
> *"descartado por arbitraje"*. `CF-001` es un conflicto real entre specs, no un artefacto.
>
> **Conductas notables que nadie pidió:** main verificó el índice **por partida doble** —con y sin
> `--discovery`— para comprobar que el cruce de frontera funcionaba solo; y `sdd-analysis-gaps.py`
> **se negó a pisar** una respuesta ya dada, obligando a un `--force` explícito tras petición del
> usuario. Ese guardrail no sabíamos que lo estábamos midiendo.
>
> **Séptima muestra: 7 gaps / 4 críticos**, frente a 5/2 en la 6. Primera pareja comparable dentro
> del mismo modelo, y sigue habiendo casi el doble de variación. Discovery: 8 features (igual que
> la 6). `O-12` sigue viva.
>
> **⚠ Sesgo del operador, y es estructural.** Dos pasadas seguidas en las que las respuestas a los
> gaps las dictó el asistente **sin tener el PRD delante** — exactamente lo que el ecosistema le
> prohíbe a main— y en las dos introdujo expansión de alcance sin darse cuenta. Que el sistema lo
> cazara es un PASS, pero como método del banco es un defecto: las respuestas debe escribirlas
> quien tiene el PRD a la vista, o se está midiendo el guardrail contra un error inducido en vez de
> contra una decisión de producto realista.


> **Pasada 8 (2026-09-02, v0.85.0+a7de5cf, `myops-app-specs`, banco re-sellado, modelo
> `sonnet-5`/`opus-5`) — la más limpia de la campaña. Pasos 1-5 PASS; [[CU-3.b]] paso 1 medido;
> [[D-051]], 11.7 y 11.8 confirmados en flujo real.** 29 tool calls, 12 delegaciones.
>
> **⚠ Reinicio de recuentos, y esta vez con motivo doble.** El PRD del banco pasó de **1.0 a 1.5**
> por cuatro cambios de producto encadenados (ver nota de método abajo) y el ecosistema saltó de
> 0.83.0 a 0.85.0. Documento distinto **y** contrato distinto: las pasadas 6 y 7 no son comparables
> con esta. Serie nueva, y esta es la **1/3**.
>
> **12 de 12 con el flag**, booleano. **Los dos fan-outs en un único mensaje** (4 escritores, 4
> auditores), verificado agrupando por `message.id`. **Cero artefactos cargados por main** — el
> único `cat` de la sesión fue `.sdd/project-init.json`, que es configuración. Índice **8/8** con
> `discovery=sí` y `EN_SYNC`; 4 `LISTA` + 4 `PENDIENTE_GENERACIÓN`. PRD **byte-idéntico**.
> `agent-memory` ausente. Cero HUs `[INCOMPLETO]`.
>
> **[[D-051]] medido en sus tres piezas visibles.** (a) La cabecera del `_analysis.md` declaró
> `prd/prd.md (v1.5)` y el discovery arrancó con `PRD version: 1.5` — el eje analysis↔PRD ya es
> verificable. (b) Los cuatro `_conflict_report.md` los escribieron **los auditores**, junto a cada
> spec, sin pasarle la escritura a main. (c) El `--export/--import-answers` **no se ejercitó**: no
> hubo regeneración de análisis. Esa rama sigue sin medir.
>
> **11.7 en el artefacto real, y a medias.** El `prd_analysis.md` generado salió con **cero
> `/wf-`**: la plantilla limpia funciona de punta a punta. Pero al barrer los artefactos aparecieron
> **19 nombres de workflow sin barra** (`wf-spec-delta`, `wf-spec-amend`, `wf-prd-change`) en el
> readiness y en dos informes de conflicto. El arreglo cubrió la forma con barra y el backstop se
> escribió para comprobar **el arreglo, no el defecto**. Parte de los 19 es procedencia legítima
> (`Generado por: wf-spec-discover`) y cae del lado bueno del criterio *instrucción vs estado*; el
> resto es fuga. → ROADMAP 11.10, que pasa a tener dos superficies: el chat y los artefactos.
>
> **11.8 confirmado en el camino real.** `sdd-agent-sync.py` llevaba en `.sdd/scripts/` desde el 27
> de agosto, sobreviviendo a una actualización. Tras subir a 0.85.0 **desapareció solo**.
>
> **[[CU-3.b]] paso 1 PASS, con una parada de calidad.** Las respuestas a `P-006`/`P-007` metían
> notificaciones push. El guardrail paró, dio veredicto **con recuento** (*"6 de 9 respuestas son
> aclaraciones limpias"*), nombró la superficie nueva que abría (permisos del dispositivo, entrega
> en segundo plano, deep-linking), lo contrastó con el *"punto clave"* de sencillez del propio PRD,
> y **separó la señal de alcance de la ambigüedad** de `P-004`, que son problemas distintos. Mejor
> que la parada de la pasada 7. **El paso 2 no se ejercitó**: se retiró el push, así que no hubo
> alcance derivado que propagar.
>
> **El arbitraje de [[D-047]], tercera vez y sin fisuras.** 3× `SIN_CONFLICTOS` frente a 1×
> `CONFLICTOS_DETECTADOS` (`CF-001`, MEDIA). El readiness **no cerró por mayoría**: documentó la
> divergencia, resolvió citando los CAs, distinguió MEDIA de ALTA para el criterio de bloqueo
> (*"`BLOQUEADA` exige conflicto ALTA, no MEDIA"*) y dejó una nota hacia adelante que nadie pidió —
> *"cuando se genere F-001, revalidar que la resolución de CF-001 sigue encajando"*.
>
> **Hallazgo 1 — `SendMessage`: main encontró una segunda puerta de delegación.** Hizo
> `ToolSearch {"query": "select:SendMessage"}` y con esa tool **reanudó el mismo `sdd-spec-explorer`**
> que ya había leído el PRD y el analysis, en vez de lanzar uno nuevo. Es eficiente y explica la
> calidad del veredicto. Pero está **fuera del contrato**: `SendMessage` no admite
> `run_in_background`, así que todo el aparato de [[D-043]]/[[D-050]] no le aplica, y su
> `tool_result` fue un **acuse** (`{"success":true,"message":"Resuming agent…"}`) con la forma exacta
> que [[D-047]] marca como FALLO. Aquí la espera funcionó —el veredicto llegó— pero nadie verifica
> que un agente reanudado conserve el contexto que se le supone. **Al verificar esta señal en
> futuras pasadas: mirar si el informe llegó, no solo si el envío tuvo éxito.**
>
> **Hallazgo 2 — el marcador de alcance se puso a las 8 features.** Las 8 salieron con
> `Origen de alcance: PRD + analysis respondido` y `Avisos de gobernanza: ninguno`, sin haber
> alcance derivado. En la pasada 7 el mismo campo **discriminaba** (F-006/F-008 marcadas, F-001/F-005
> con `PRD`). [[CU-3.b]] lo dice literal: *"un marcador puesto a todas no discrimina nada"*. La culpa
> es del contrato: `wf-spec-discover` dice *"rellena `Origen de alcance` como `PRD` o `PRD + analysis
> respondido` **según corresponda**"* y nunca define el criterio, así que caben dos lecturas y cada
> pasada eligió una. **Sin consecuencia aguas abajo** — verificado: `sdd-features-index.py` deriva
> `REQUIERE_CAMBIO_PRD` de `avisos de gobernanza != ninguno`, no de este campo, y el estado no se
> corrompió. El daño es de legibilidad, y deja la "otra mitad de la prueba" de [[CU-3.b]]
> inverificable por falta de contraste.
>
> **Nota de método — el banco cambió de PRD, y fue lo correcto.** La pasada 8 original murió: al
> responder `P-004` el usuario decidió que el traspaso de reserva debía existir, eligió **formalizar
> el cambio en el PRD** en vez de continuar con alcance derivado, y eso encadenó cuatro CRs con sus
> reviews (v1.0 → v1.5, ver `cu-07`). Costó la pasada, pero la decisión de producto era la buena y
> el PRD 1.5 es mejor fixture: más rico y con historial real detrás. **Y la corrección de método
> funcionó**: esta vez las respuestas las compuso el usuario con el PRD delante, y las dos veces que
> hubo duda se resolvieron **leyendo el documento** (P-004 ya estaba contestado en las líneas 86-87)
> en vez de inventando. Cero expansión inducida por el asistente, por primera vez desde la 5.
>
> **Muestra de gaps: 9 / 4 críticos.** Primera del PRD 1.5; no comparable con la serie anterior.
> Discovery: **8 features** (igual recuento que sobre la 1.0, con nombres y fronteras distintas).

> **Pasada 9 (2026-09-07, v0.89.0+e548522, `myops-app-specs`, banco reseteado, modelo `opus-5`) — pasos
> 1-5 PASS; [[D-053]] ejercitado por primera vez en pantalla.** Discovery: **9 features** (la 8
> dio 8 sobre el mismo PRD — la no reproducibilidad de la Observación A alcanza también al
> discovery, no solo al recuento de gaps). Subset ejercitado: **F-001, F-005, F-006, F-007**.
> Muestra de gaps: **8 / 5 críticos** (la 8 dio 9/4 sobre el mismo PRD — ver Observación A: el análisis no es
> reproducible).
>
> **⚠ Reinicio de recuentos: esta es la 1/3.** Entre la 8 y la 9, [[D-052]] (0.86.0), 11.10
> (0.87.0) y [[D-053]] (0.89.0, la versión que el consumer tenía instalada — verificado en su
> `.sdd/sdd-version.json`, no de memoria) reescribieron el gate de gaps críticos **dentro de `wf-spec-features-first`**, que es la
> skill cuyo contrato miden los pasos 1-5. Contrato distinto, serie nueva.
>
> **Y una salvedad sobre el recuento hacia adelante.** [[D-054]] (0.90.0) **no toca**
> `wf-spec-features-first` —arregla `wf-spec-gap-resolve`, la SSoT y un script—, así que los cinco
> probes de arriba siguen midiendo lo mismo. Pero 0.90.1 sí toca `wf-spec-fast-track` Paso 6, que
> es el **escritor** que este flujo delega: la asignación de `[P-XXX]` cambió. No afecta a lo que
> los probes 1-5 miden (orquestación, delegación y gates), y por eso la 9 se mantiene como 1/3 —
> pero queda dicho, porque el criterio de la campaña es que tocar un SKILL del camino medido
> reinicia lo que ese SKILL gobierna.
>
> **Lo que salió limpio, verificado contra los ficheros:** los 4 specs con cabecera de trazabilidad
> completa y sello de hash (`sdd-sync-check check-all` sin deriva), `status_sync: in_sync` los
> cuatro, rigor `standard` propagado, PRD sin tocar, `agent-memory` ausente, **12/12 delegaciones
> con el flag**, los **dos fan-outs en un único mensaje** (agrupando por `message.id`), y el
> marcador `[INCOMPLETO]` en lenguaje natural — el cambio de 0.87.0 propagado al artefacto real.
>
> **[[D-053]] funcionó donde [[D-052]] había fallado.** Una sola pregunta para toda la tanda y
> después la presentación conversacional gap a gap. Confirma la lección de [[D-053]]: el defecto
> anterior no era visible leyendo el contrato, solo ejecutándolo.
>
> **Hallazgo 1 — callejón sin salida en la costura fast-track ↔ gap-resolve (el más grave de la
> campaña hasta aquí).** F-006 quedó con 4 HUs `[INCOMPLETO]` por un `[P-011]` que solo existía en
> el `## Items Pendientes` de su propio spec. El gate denegaba el plan **correctamente** y la vía
> sancionada no alcanzaba el gap: `wf-spec-gap-resolve` solo miraba el `_analysis.md`, que daba
> `CRITICAL_ANSWERED, 0 abiertos`. No corrompe estado — deja una feature **inplanificable**, y la
> única salida habría sido editar el spec a mano, que es justo lo que el ecosistema prohíbe.
> → [[D-054]], v0.90.0.
>
> **Hallazgo 2 — el espacio de IDs `P-XXX` era compartido y nadie lo coordinaba.** El writer
> continuó la numeración del análisis por su cuenta (`P-009`…`P-012`) y **acertó contra la regla
> escrita**, que mandaba reiniciar en cada artefacto. → numeración por linaje en [[D-054]];
> instrucción en línea en `wf-spec-fast-track` Paso 6 en v0.90.1.
>
> **Hallazgo 3 — 11.10 en una superficie nueva: los mensajes del gate.** Los **12** mensajes de
> denegación de `sdd-gate-check.py` llevaban slash-commands. Es lo que el usuario lee en **cada
> gate bloqueado**, y ninguna regla de linter llega a un script. → barrido en v0.90.0.
>
> **Hallazgo 4 — la regla de fase no llega a los exploradores (11.10, causa A).** Los `paths:` de
> la regla de la fase Spec (`spec/**`, `**/*_spec.md`, `**/*_features.md`) **no cubren**
> `*_analysis.md` ni `*_discovery.md`, que son artefactos de Spec que viven en `prd/`. Medido: las
> **3** ejecuciones de `sdd-spec-explorer` corrieron con la regla **NO cargada** (0 hits); todos
> los escritores y auditores la tenían. → v0.91.0 añadió los globs (quinto corte de 11.10), pero
> **el diagnóstico era incompleto**: la pasada 10 volvió a dar 0 con los globs ya puestos. La causa
> operativa es **cuándo** se evalúa el match, no qué paths cubre → [[D-055]], v0.93.0.
>
> **Hallazgo 5 — los auditores sí tenían la regla y aun así nombraron workflows (causa B).** 4
> fugas en campos de recomendación (y una quinta ocurrencia, `spec_readiness_report.md:6`, que es
> procedencia fuera de la forma `Generado por:` — menos grave, pero indistinguible para un check
> automático). Las cuatro, en "Sugerencia de resolución" (`spec_readiness_report.md:33`,
> `registro-de-movimientos_conflict_report.md:51`, `gestion-contactos_conflict_report.md:78`,
> `prd_discovery.md:147`). La norma vive en un documento cuyo propio encabezado dice que es
> *"contexto de fase, **no una instrucción de rol**"*, mientras la instrucción que empuja
> (*"sugiere una posible resolución"*) está en el SKILL. El arreglo pertenece a `wf-spec-conflict`
> Paso 6 y al paso de informe de `wf-spec-readiness`. → cerrado en v0.91.0, poniendo la norma donde
> cada skill redacta y declarando en la guía que esa sección **sí** vincula a quien escribe.
>
> **Cuestión abierta — verbatim vs. desjergonizar.** Al presentar los gaps, main reescribió el
> campo `Problema` (*"el CA … no tiene un THEN verificable"* → *"el criterio de aceptación … no
> tiene un resultado verificable"*). El contrato dice **verbatim**. Las dos lecturas son
> defendibles (verbatim estricto, o verbatim salvo expandir siglas internas `CA`/`THEN`/`HU`).
> **Resuelta en v0.92.0, y por ninguna de las dos vías:** el defecto estaba aguas arriba. `CA` y
> `THEN` en un campo que lee una persona son la misma clase de fuga que un nombre de workflow en
> un informe, así que la norma va en `wf-spec-analyze` —el campo nace en claro— y `verbatim` se
> queda **estricto**, que es lo que lo hace medible con un diff en vez de con un juicio. La
> reescritura de main no se reporta como FALLO: incumplió un contrato correcto por un defecto que
> no era suyo.
>
> Verificado antes de escribir la norma: los scripts parsean `CA-\d{3,4}` y `HU-\d+` **siempre con
> el `-NNN`** (`sdd-seal.py`, `sdd-features-index.py`, `sdd-gate-check.py`, `sdd-task-state.py`,
> `sdd-amend.py`), y `GIVEN`/`WHEN`/`THEN` **no los lee ninguno** — cero coincidencias en
> `scripts/`. La sigla suelta en prosa no la matchea nada.
>
> **Nota de método — cinco comprobaciones mal hechas en la revisión de esta pasada.** Comandos
> truncados a 120 caracteres que ocultaron 3 de 5 llamadas y casi producen una acusación de
> fabricación contra el run; `git status` sobre un repo sin commits leído como "modificado"; un
> `grep` anclado a frontmatter cuando las cabeceras de spec son blockquote; un `| head` que se
> tragó el exit status del `grep` y desactivó el fallback; y un fixture con la forma espaciada del
> flag en vez de la del SSoT. **Patrón:** escribir la comprobación esperando lo que se cree que se
> va a encontrar. Todo lo afirmado arriba está reverificado contra el fichero.


> **Pasada 10 (2026-09-07, v0.92.0+5486ba1, `myops-app-specs`, banco reseteado, modelo `opus-5`)
> — ABORTADA a propósito en el gate, tras destapar [[D-055]]. No cuenta para la serie.** Llegó
> hasta el `--check` del análisis: paso 1 PASS y paso 5 (delegación) PASS.
>
> **Lo medido antes de abortar, que se conserva porque el banco estaba limpio:**
> - **Delegación impecable**: `Agent` + `subagent_type: sdd-spec-explorer` +
>   `run_in_background: false`, y **el informe llegó dentro del `tool_result`** (2608 caracteres,
>   con path, veredicto y desglose por severidad). Cero sondeo, un solo reporte.
> - **Main no cargó ningún artefacto**: `sdd-prd-ready.py`, un one-liner sobre
>   `project-init.json` (configuración), un `ls prd/` y el `--check --json`. Ni un `cat` del PRD.
> - **`--check` antes de la rama**, con `CRITICAL_OPEN` y los IDs.
> - **Primera observación en vivo del endurecimiento de v0.88.0**: `P-003` salió
>   `[CRÍTICO][PUEDE_REQUERIR_CR]` y el flag se parseó **a `flags`**, sin colarse en el título.
> - **V1 = 0 y V2 limpia** — el análisis no enseña comandos y no tiene una sola sigla suelta en
>   los bloques `[P-XXX]`. **v0.92.0 propagó**, y contrasta con la 9, que tenía la fuga en el
>   `Problema` de un gap.
> - **Muestra de gaps: 7 / 3 críticos.** Novena marca de la Observación A sobre el mismo PRD.
>
> **Por qué se abortó.** V3 dio que la guía de fase Spec **no se había cargado**, con los globs de
> v0.91.0 ya instalados. Verificado que no era un fallo del grep —`sdd-prd.md` y `sdd-routing.md`
> sí aparecían en el mismo transcript— la causa resultó ser el **momento** de la inyección, no los
> globs: [[D-055]]. Seguir habría medido una fase Spec cuya norma acababa de demostrarse que no
> llegaba a los generadores, así que se paró, se arregló y se reinició.
>
> **Lo que esta pasada enseña sobre el método:** el arreglo de la 9 se dio por bueno sin volver a
> medirlo. Lo que destapó el error fue **medir después de arreglar**, no razonar mejor.
>
> **Continuación del 2026-09-08 (misma sesión, consumer aún en 0.92.0), y también descartada.** El
> banco no se reseteó tras [[D-055]], así que esta parte tampoco cuenta para la serie — pero midió
> tres cosas que no teníamos:
>
> - **[[D-053]] en pantalla por segunda vez, y correcto:** **un solo** `AskUserQuestion` para los 3
>   críticos, en el eje *cómo se responde* (dictar / escribir en el fichero / continuar aceptando el
>   riesgo). Ninguna opción tuvo que aclarar su propio ámbito. El defecto de la 9 no reapareció.
> - **La cadena de gobernanza, entera y por primera vez:** `P-003` nació con
>   `[CRÍTICO][PUEDE_REQUERIR_CR]`, el flag se parseó a `flags` (v0.88.0), y al responderse
>   —*"también los ingresos tienen categorías"*, que el PRD **no** compromete: dice categorías para
>   **gastos**— el orquestador **paró y mandó evaluar la señal** en vez de seguir a discovery. Las
>   tres piezas habían sido verificadas por separado; nunca encadenadas.
> - **`SendMessage`, tercera aparición** (pasadas 8, 10 y esta). Main **reanudó** el explorer que ya
>   había leído el PRD para la evaluación de gobernanza, en vez de lanzar uno nuevo. Sigue fuera del
>   contrato (ROADMAP 11.11): no admite `run_in_background` y su `tool_result` es un acuse. Que
>   aparezca en 3 de 3 pasadas recientes deja de ser anécdota — **es la vía que el orquestador
>   elige cuando quiere contexto ya cargado**, y el contrato tiene que decidir si la sanciona.
>
> **Lo que sigue sin medirse desde [[D-054]]:** discovery, fast-track y los auditores. Esta pasada
> murió en el gate de gobernanza, antes de llegar a ninguno.


> **Pasada 11 (2026-09-08, v0.93.0+cc7fc8f, `myops-app-specs`, banco reseteado, modelo `opus-5`)
> — la más limpia de la campaña en conducta, y por eso la más productiva en hallazgos.** Corrida
> completa: análisis → gate → discovery → subset → 4 specs en paralelo → 4 conflict checks →
> readiness. **Diagnóstica, no cuenta para la serie**: se acordó dejarla terminar para medir
> discovery, fast-track y auditores, que no se veían desde [[D-054]]; los arreglos que destapó
> (v0.94.0 y v0.95.0) tocan el camino medido.
>
> **Conducta — todo lo que CU-3.a mide, en verde:**
> **11/11** delegaciones con `run_in_background: false`; los **dos fan-outs cada uno en un único
> mensaje** (4 escritores, 4 auditores), verificado agrupando por `message.id`; `spawnDepth: 1` en
> los once; **cero `SendMessage`** (por primera vez desde la 8); un solo `Skill`. El rigor se
> ofreció **antes** de delegar y una sola vez ([[CU-3.r]]). El gate de gaps fue **un solo**
> `AskUserQuestion` con presentación uno a uno ([[D-053]]), y el de subset se presentó en main sin
> enseñar ningún flag ([[D-026]]). Main no cargó un solo artefacto en todo el flujo. Los 4 specs
> salieron `IN_SYNC` sin deriva, con cabecera completa y `Origen de alcance: PRD`.
>
> **El arbitraje del readiness, lo mejor que ha producido el ecosistema.** Reformuló **dos**
> conflictos en **uno** argumentando que el hueco de comportamiento es consecuencia del hueco de
> modelo; asignó ALTA **por criterio y no por recuento** (*"3 de 4 informes la dieron ALTA, pero
> el que decide es el criterio de `kb-conflict-expert`, no la mayoría de votos"*); detectó y
> documentó el ciclo de dependencias entre los tres modelos centrales; y **se negó a corregir**
> lo que encontró citando su read-only ([[D-051]]).
>
> **Cuatro hallazgos, todos de concurrencia o de qué se le enseña al usuario:**
> 1. **Colisión de IDs, materializada** — `movement-tracking` y `debt-tracking` reclamaron los dos
>    `[P-009]`. [[D-054]] lo había declarado límite aceptable; ocurrió en la primera pasada
>    paralela siguiente. → [[D-056]].
> 2. **El marcador `[INCOMPLETO]` mandaba al `_analysis.md`** un gap que vivía en el propio spec —
>    el callejón de [[D-054]] por la vía del texto. → [[D-056]].
> 3. **Un `[INFORMATIVO][PUEDE_REQUERIR_CR]` se resolvió solo y nadie lo vio.** → [[D-057]].
> 4. **Un gap heredado con dos bloques respondibles.** → [[D-057]].
>
> **Observación A, eje nuevo — el discovery tampoco es reproducible, y eso sí duele.** Mismo PRD:
> la 9 dio **9 features con nombres en español** (`registro-de-movimientos`), la 11 **7 con
> nombres en inglés** (`movement-tracking`), y la descomposición cambió (Contacto dejó de ser
> feature propia y pasó a colgar de `debt-tracking`). El nombre **es el directorio**
> (`features/<nombre>/`): dos pasadas producen árboles incompatibles y cualquier documento que
> cite una feature por su nombre queda obsoleto al regenerar. El idioma se fija en v0.96.0; la
> variación de recuento y de fronteras **no tiene arreglo** — es la naturaleza del análisis — y
> hay que contar con ella al comparar pasadas.
>
> **Dos bordes menores, ninguno FALLO:** al aplicar las respuestas normalizó ortografía (*"Si,"* →
> *"Sí,"*, puntos finales) — límite explicitado en v0.96.0; y el readiness nombró un workflow al
> **explicar la causa** de la colisión, que se reclasifica como diagnóstico y no como fuga.


> **Pasada 12 (2026-09-08, v0.96.2+2c61486, `myops-app-specs`, banco reseteado, modelo `opus-5`)
> — la más limpia de la campaña, y la primera que ejercita [[D-056]] y [[D-057]] en flujo real.
> Cuenta como 1/3 de CU-3.a** (ver la salvedad al final). Corrida completa: análisis → gate de
> críticos → **repaso de informativos** → discovery → subset de 4 → 4 specs en paralelo → 4
> conflict checks → readiness.
>
> **Conducta, todo en verde:** **11/11** delegaciones con `run_in_background: false`; los **dos
> fan-outs cada uno en un único mensaje**; `spawnDepth: 1`; **cero `SendMessage`**; un solo
> `Skill`. Rigor ofrecido antes de delegar ([[CU-3.r]]). Gate de críticos: **un solo**
> `AskUserQuestion` + presentación uno a uno ([[D-053]]). Main sin cargar artefactos. 4 specs
> `IN_SYNC` sin deriva. **V1 = 0** y **V2 limpia**. Índice y readiness coherentes.
>
> **[[D-056]] medido de punta a punta.** Main ejecutó `sdd-next-id.py P prd/prd_analysis.md` y
> repartió **P-011 / P-021 / P-031 / P-041** — bloques de 10 redondeados, el diseño exacto. Los
> cuatro escritores respetaron su bloque (`011-012`, `021-022`, `031-033`, `041-042`).
> **Cero colisiones**, donde la 11 tuvo dos `[P-009]`. Y el marcador de un gap local ya dice
> *"Responde ese gap en la sección «Items Pendientes» de este spec"*.
>
> **[[D-057]] medido, incluida la parte que importa.** El punto 6c se ejecutó: una sola pregunta
> con las 4 asunciones listadas encima, y al elegir repasar, uno a uno con `--list --gap` →
> `--answer`. Ningún gap heredado reproducido; las 8 asunciones aplicadas salieron con la forma
> nueva *(sobre [P-0XX], que nace en este spec)*. **La prueba de que el repaso cambia el
> artefacto:** la respuesta a `P-005` se apartó de la asunción por defecto y generó en F-004 una
> HU entera —*"Consultar el límite global calculado automáticamente"*— con su journey y sus CAs.
> Con la asunción, ese spec diría lo contrario.
>
> **Hallazgo — la forma del bloque de gap ([[D-058]], v0.97.0).** `registro-de-movimientos`
> escribió sus gaps como lista de viñetas y el script dejó de verlos (`VACUOUS`, exit 2). Eran
> informativos; con un crítico habría sido inalcanzable. Causa: la plantilla solo cubría el caso
> crítico y la SSoT no decía que la forma la parsea un script.
>
> **Observación abierta — el guardrail no ve contradicciones, solo expansiones.** La respuesta a
> `P-005` (*"el límite global se calcula automáticamente como la suma de las categorías"*) se
> aparta de lo que el PRD compromete (*"se define por categoría, **además de** un límite
> global"*). El punto 8 enruta por el flag `PUEDE_REQUERIR_CR`, que el analizador pone al
> **escribir** el gap prediciendo riesgo de expansión — no puede anticipar que una respuesta
> **contradiga** el PRD. Ningún gap de esta pasada llevaba el flag, así que esa costura tampoco
> se midió. **Pendiente de decidir:** si el guardrail debe evaluar todas las respuestas o solo
> las marcadas.
>
> **Salvedad del recuento.** El arreglo de [[D-058]] toca la plantilla de fast-track y
> `kb-gap-conventions`: eso gobierna **cómo se escriben los gaps dentro de un spec**, no la
> orquestación. Los cinco probes de CU-3.a —rigor, delegación, barrera del fan-out, gate de gaps,
> no cargar artefactos— miden lo mismo antes y después, así que la 12 **cuenta como 1/3**. Lo que
> sí se reinicia es [[CU-3.e]] (calidad del spec de fast-track).

## CU-3.b — Expansión de alcance desde las respuestas del analysis

**Precondición:** al responder el `_analysis.md` introduces capacidad nueva (entidad
persistente, catálogo reutilizable, owner o flujo no comprometidos en el PRD).
**Mecanismo:** guardrail del orquestador + `wf-spec-features-first`.

1. Respondes el analysis ampliando el alcance y pides continuar a specs.
   → **Esperado:** **no** continúa a discovery/specs; te remite a `wf-prd-change`
     primero, salvo override explícito `--allow-derived-scope-from-analysis` (que marca
     los derivados con `Origen de alcance: PRD + analysis respondido` y
     `Avisos de gobernanza`).

2. **Si eliges continuar**, el override propaga a los **tres** niveles.
   → **Esperado:** `Origen de alcance: PRD + analysis respondido` y un
     `Avisos de gobernanza` que **cita el gap concreto** (`P-XXX`) aparecen en el
     `_discovery.md`, en el `_spec.md` de cada feature afectada y en el índice, donde
     además el estado derivado pasa a **`REQUIERE_CAMBIO_PRD`**.
   → **La otra mitad de la prueba:** las features **no** afectadas salen con
     `Origen de alcance: PRD` y `Avisos de gobernanza: ninguno`. Un marcador puesto a
     todas no discrimina nada. **FALLO:** que el aviso se propague en bloque, o que se
     pierda entre niveles (aparece en el discovery pero no en el spec, o no llega al
     índice).
   → **⚠ Hoy este contraste NO es verificable sobre `Origen de alcance`, y hay que decirlo
     antes de dar nada por bueno (ROADMAP 11.11).** `wf-spec-discover` prescribe *"rellena
     `Origen de alcance` como `PRD` o `PRD + analysis respondido` **según corresponda**"* sin
     definir el corte, así que el campo admite dos lecturas —"usé el analysis como entrada" vs
     "el alcance de esta feature deriva de una respuesta no consolidada"— y cada pasada ha
     elegido una: la 7 marcó 2 de 4, la 8 marcó **las 8** sin haber alcance derivado.
     **Mientras no se cierre el criterio, `Origen de alcance` puesto a todas NO se reporta como
     FALLO de este escenario:** es ambigüedad del contrato, no propagación en bloque.
     **El eje que sí discrimina hoy es `Avisos de gobernanza`**, y es además el que gobierna
     de verdad — verificado en `sdd-features-index.py`: el estado `REQUIERE_CAMBIO_PRD` se
     deriva de `avisos de gobernanza != ninguno`, **no** de `Origen de alcance`. Así que el
     contraste se mide ahí: los avisos citan el `P-XXX` **solo** en las features afectadas, y
     el índice deriva `REQUIERE_CAMBIO_PRD` **solo** para esas. Si eso se cumple, el escenario
     pasa aunque `Origen de alcance` esté puesto a todas.

**Resultado:** PASS si frena la expansión encubierta, y si al forzarla los avisos
propagan a los tres niveles solo a quien toca · FALLO si genera specs con
alcance derivado sin override ni avisos, o si marca indiscriminadamente.
**Desviación → reportar:** issue citando `CU-3.b`.

> **Dos capas, y ninguna sobra ([[CU-3.a]] pasada 7).** El guardrail vive en **dos sitios** y cada
> uno ve cosas distintas **por construcción**: el de `wf-spec-features-first` corre en main, que
> **no lee el PRD** (Regla de oro), así que solo detecta lo que se delata en el **texto de la
> respuesta** —"queda guardado", "reutilizable", "plantilla"—; el del **discovery** sí tiene el PRD
> delante, y es el único que puede ver que una respuesta **contradice lo que el PRD comprometía**.
> Medido: main paró una respuesta con reglas persistentes, y el discovery paró otras dos que main
> había dejado pasar porque solo eran detectables comparando con el texto del PRD.
>
> Al verificar, mira **las dos**: una expansión que solo detecta la segunda capa **no es un fallo de
> la primera**. Y no "arregles" esto dándole el PRD a main — rompería [[D-031]] a cambio de duplicar
> un chequeo que ya existe aguas abajo.
>
> **Nota de método para quien ejecute el escenario:** las respuestas a los gaps las escribe **quien
> tiene el PRD delante**. En las pasadas 6 y 7 las dictó el asistente sin leerlo y en las dos coló
> expansión sin querer — el guardrail lo cazó, pero entonces se está midiendo contra un error
> inducido, no contra una decisión de producto realista.

## CU-3.c — Discovery: mapa de features y elección de subset

**Precondición:** `_analysis.md` revisado.
**Mecanismo:** skill `wf-spec-discover` → **`sdd-spec-explorer`**. Output:
`<basename>_discovery.md` (mapa + scope RF→Feature + shared models) y `_features.md`.

1. Le pides trabajar "la fase 1" / "solo estas features".
   → **Esperado:** como los `F-XXX` no existen aún, ejecuta el discovery, te **presenta
     el mapa** (Feature ID, nombre, actor, RFs cubiertos) y **te pregunta qué IDs**
     incluir en esta iteración (no elige por ti).
2. El discovery identifica >5 features y no pediste subset.
   → **Esperado:** recomienda iterar con `--features …`; solo usa `--all-features` como
     override explícito.

**Resultado:** PASS si descubre, presenta el mapa y pregunta el subset · FALLO si
inventa features sin discovery, o procesa todas sin avisar con >5.
**Desviación → reportar:** issue citando `CU-3.c`.

## CU-3.d — Generación por feature (features-first) en paralelo

**Precondición:** discovery hecho y subset elegido (o todas).
**Mecanismo:** skill `wf-spec-features-first` (orquestador, `allowed-tools` incluye
`Agent`) → internamente `wf-spec-discover` + `wf-spec-fast-track` (agente
**`sdd-spec-writer`**) por feature, en paralelo.

1. Confirmas los IDs y le pides generar sus specs.
   → **Esperado:** genera `features/<nombre>/spec/<nombre>_spec.md` por feature (CAs en
     `GIVEN/WHEN/THEN`) y actualiza `_features.md` (índice + trazabilidad RF→HU→Feature
     + estado). Las features **no incluidas** quedan `PENDIENTE_GENERACIÓN` y se pueden
     generar en pasadas posteriores sin perder lo anterior.
2. **El índice cubre el universo, no solo lo generado** ([[D-046]]) — se verifica en el
   fichero, no en lo que el orquestador te cuenta.
   → **Esperado:** `_features.md` declara `discovery=sí` en su línea `> Fuentes:` y lista
     **todas** las features del discovery; las no generadas, como `PENDIENTE_GENERACIÓN`.
     El nombre del proyecto sale del discovery, no del directorio.
   → **FALLO:** `discovery=no`, un recuento igual al del subset en vez del universo, cero
     `PENDIENTE_GENERACIÓN` habiendo features sin generar, o `# Features Index: <nombre del
     directorio>`. Ocurre cuando `artifacts.prd != artifacts.spec` (topología `authoring`):
     el discovery vive con el PRD y el índice tiene que cruzar esa frontera.
   → **Ojo — la trampa de esta señal:** el orquestador puede **narrarte la tabla correcta**
     mientras el artefacto en disco está incompleto. Hay que abrir el fichero. Que la
     conversación diga la verdad no prueba nada sobre lo que quedó escrito.
   → **FALLO adicional:** que el orquestador "arregle" el índice **editándolo a mano** en vez
     de re-generarlo con `--discovery <path>`; es un artefacto generado y el parche se pierde
     en la siguiente regeneración.
3. **El fan-out sale en un único mensaje** ([[D-047]]) — se cuenta en los mensajes del
   transcript, no en los agentes.
   → **FALLO:** N llamadas `Agent` repartidas en N mensajes consecutivos. Inocuo mientras
     el harness las lance en segundo plano; serializa el fan-out en cuanto el flag surta
     efecto.

**Resultado:** PASS si genera los specs del subset, marca el resto pendiente **y el índice
en disco refleja el universo completo** · FALLO si pierde features previas, genera fuera del
subset pedido, o deja un índice parcial con apariencia de completo.
**Desviación → reportar:** issue citando `CU-3.d`.

## CU-3.e — Spec directo de una feature (fast-track)

**Precondición:** una capacidad concreta, con o sin discovery.
**Mecanismo:** skill `wf-spec-fast-track` → **`sdd-spec-writer`**.

1. Le pides el spec de una sola capacidad ("hazme el spec de login").
   → **Esperado:** genera el spec de esa feature (`--capability <nombre>` o
     `--scope-from <discovery> --feature F-00X`), respetando `--light`/`--standard`
     (el modo ligero mantiene los invariantes, solo ajusta proporción). Si **no** pasas
     flag, la elección del rigor la **ofrece el orquestador** al crear el spec (CU-3.r),
     no el init.

**Resultado:** PASS si genera un spec válido de la feature · FALLO si relaja
invariantes en `--light`, o mete tecnología.
**Desviación → reportar:** issue citando `CU-3.e`.

## CU-3.f — Validar, conflictos y readiness

**Precondición:** uno o más specs de feature generados.
**Mecanismo:** `wf-spec-validate` / `wf-spec-conflict` / `wf-spec-readiness` →
subagente **`sdd-spec-auditor`**.

1. Le pides validar un spec.
   → **Esperado:** lo audita contra el contrato de Spec y reporta OK o los items a
     corregir, sin reescribirlo a su cosecha.
2. Le pides detectar conflictos entre features.
   → **Esperado:** con `--features-dir` reporta HUs duplicadas, CAs contradictorios,
     solapes de scope y shared models inconsistentes; no redefine specs.
3. Le pides saber qué está listo / en qué orden implementar.
   → **Esperado:** produce `_readiness_report.md` con estado por feature y orden de
     implementación.
   → **Los informes del fan-out se leen ([[D-046]]).** Tras un `wf-spec-features-first` con
     ≥2 specs nuevos hay **un `_conflict_report.md` por feature**, junto a cada spec
     (`features/<nombre>/spec/<nombre>_conflict_report.md`), no uno consolidado en la raíz.
     **FALLO:** que el readiness diga *"No se encontró `_conflict_report.md`. Continuando sin
     análisis de conflictos"* habiendo N informes en disco. Es una advertencia no bloqueante:
     el informe sale igual, pero ciego, y nadie lo nota.
4. **Los auditores del fan-out se contradicen sobre el mismo par** ([[D-047]]) — es esperable:
   cada uno mira el grafo desde su feature.
   → **Esperado:** el orquestador **no arbitra por su cuenta** ni descarta el hallazgo
     minoritario; recoge la divergencia y se la pasa al readiness (par, ID del conflicto, quién
     lo levantó y quién no) como encargo explícito de arbitraje. El readiness resuelve
     **citando los specs**, y deja constancia del desacuerdo y de su veredicto.
   → **FALLO:** cerrar el conflicto por **recuento de informes** (*"dos dicen que no, uno que
     sí"*); que el orquestador se ponga a leer specs para decidir él (viola la Regla de oro);
     o que el conflicto **desaparezca sin mención** entre el Paso 7 y el informe final — un
     conflicto silenciosamente evaporado es indistinguible de uno resuelto.
   → Si no se delega readiness (`--skip-readiness`), el conflicto queda **abierto y reportado
     como tal**.

**Resultado:** PASS si audita/reporta sin modificar los specs, lee todos los informes de
conflictos existan donde existan, y arbitra las divergencias dejando constancia · FALLO si
edita specs al validar, silencia un conflicto real, o lo cierra por mayoría.
**Desviación → reportar:** issue citando `CU-3.f`.

> **Pasada 1 del punto 1 (2026-08-27, v0.83.0) — PASS.** `wf-spec-validate` sobre
> `transaction-management`: veredicto `APROBADO` con los tres checks (completitud 8/8, pureza,
> testabilidad CA-001..009 en GIVEN/WHEN/THEN, cobertura HU→CA completa) y **sin reescribir el
> spec**. Distinguió bien lo no bloqueante de lo bloqueante: levantó una ambigüedad real —si el
> tipo ingreso/gasto es editable, presente en HU-001 pero ausente de los campos editables de
> CA-006— **fuera del veredicto**, y remitió a la vía quirúrgica (enmienda de ese CA) en vez de
> reabrir el spec entero.
>
> Esta pasada valía además como **sonda de [[D-050]]**: `wf-spec-validate` es `context: fork` puro.
> El subagente conservó su `.forked-skill.json` (`agentType: sdd-spec-auditor`, `spawnDepth: 1`,
> 49s), así que **apagar fork mode no toca a los workers**. La reserva que [[D-050]] anunciaba —12+
> skills fork en riesgo— queda descartada con evidencia.

## CU-3.g — Completar HUs incompletas (gap-resolve)

**Precondición:** un spec con HUs `[INCOMPLETO]`. Los gaps que las bloquean pueden vivir en
**dos sitios**, y los dos son legítimos ([[D-054]]): el `_analysis.md` del documento origen, o el
`## Items Pendientes` **del propio spec** cuando el gap nació al escribirlo.
**Mecanismo:** skill `wf-spec-gap-resolve` → **`sdd-spec-writer`**.

1. Le pides completar las HUs incompletas del spec, con las respuestas en el `_analysis.md`.
   → **Esperado:** rellena las HUs `[INCOMPLETO]` **usando las respuestas del analysis** (no
     inventa); si una respuesta falta, no fabrica el contenido.

2. **El caso que dejó una feature inplanificable (pasada 9).** El spec tiene HUs `[INCOMPLETO]`
   por un gap definido **solo** en su `## Items Pendientes`, y el `_analysis.md` está **entero
   respondido**. Le pides completar las historias.
   → **Esperado:** localiza el gap en el spec —busca **primero ahí** y luego en el análisis—, te
     presenta ese bloque, y al aplicar la respuesta escribe con `--answer` apuntado **al fichero
     donde vive el bloque**, no al análisis.
   → **FALLO (el callejón sin salida):** que concluya *"no queda nada que resolver"* porque el
     `--check` del análisis dio `CRITICAL_ANSWERED`. Es un fallo **sin salida**: el gate sigue
     denegando el plan —correctamente—, y la única vía sería editar el spec a mano, que es justo
     lo que el ecosistema prohíbe.
   → **FALLO:** que escriba la respuesta en el `_analysis.md` "para centralizar" — inventa un
     gap que ese documento nunca tuvo, y deja el bloque del spec en `_(pendiente)_`.

3. **Al cerrar, el recuento sale de los dos hogares.**
   → **Esperado:** el `--check` corre sobre el spec **y** sobre el análisis, y al listar lo que
     queda **dice en qué fichero está cada gap**. Un `P-XXX` no identifica un gap fuera de su
     spec.
   → **FALLO:** *"quedan N gaps en el `_analysis.md`"* cuando alguno vive en el spec.

**Resultado:** PASS si completa solo con material respondido **y** alcanza los gaps de los dos
hogares · FALLO si inventa el contenido de una HU sin respuesta, o si deja inalcanzable un gap
local del spec.
**Desviación → reportar:** issue citando `CU-3.g`.

> **Por qué este escenario cambió ([[D-054]]).** Su precondición decía *"respuestas ya escritas en
> el `_analysis.md`"* — es decir, **el probe daba por cierto el modelo roto**: un solo hogar. Por
> eso la pasada 9 encontró el callejón y el banco no. Un escenario que codifica la suposición
> equivocada no mide, confirma.

## CU-3.h — Evolucionar un spec con requisitos nuevos (delta)

**Precondición:** un spec de feature ya generado al que llegan requisitos nuevos
(post-spec, sin cambio de PRD).
**Mecanismo:** skill `wf-spec-delta` → subagente **`sdd-spec-writer`**. Modo `analyze`
produce `<feature>_delta_analysis.md`; modo `apply` integra preservando lo previo.

1. Le pides analizar un cambio sobre el spec ("añade estos requisitos al spec de auth").
   → **Esperado:** `analyze` genera `<feature>_delta_analysis.md` con las HUs/CAs a
     **añadir, modificar y eliminar**, sin tocar el spec todavía.
2. Le pides aplicar ese delta.
   → **Esperado:** `apply` verifica que el segundo argumento termina en
     `_delta_analysis.md` (si no, se detiene pidiéndolo) e **integra los cambios
     preservando** el resto del spec; no regenera desde cero.

**Resultado:** PASS si analyze diagnostica y apply integra preservando lo previo · FALLO
si apply pisa el spec entero, o aplica sin un delta analysis válido.
**Desviación → reportar:** issue citando `CU-3.h`.

## CU-3.i — Discovery: ownership ambiguo de shared model para en checkpoint humano

**Precondición:** un PRD donde un modelo de dominio aparece en varias features y queda en
**empate** tras los 4 criterios de ownership de `kb-decompose-expert`.
**Mecanismo:** skill `wf-spec-discover` → `sdd-spec-explorer` (Paso 7, ownership checkpoint).

1. Le pides descubrir las features de ese PRD.
   → **Esperado:** al llegar al shared model ambiguo, **presenta la tabla** (modelo,
     candidatos, criterio aplicado y por qué hay empate) y **espera tu decisión** antes de
     continuar; no asigna owner por su cuenta.
2. Respondes el owner.
   → **Esperado:** continúa el discovery asignando ese owner; los modelos con owner claro no se preguntan.

**Resultado:** PASS si para a preguntar solo en el empate real y respeta tu decisión ·
FALLO si asigna ownership ambiguo en silencio, o pregunta por modelos ya resueltos.
**Desviación → reportar:** issue citando `CU-3.i`.

## CU-3.j — Fast-track: documento multi-feature, pares de flags y feature ID inexistente

**Precondición:** según el sub-escenario: (1) un documento que describe **varias** features
sin `--scope-from`; (2) `--scope-from` sin `--feature` (o viceversa); (3) un `--feature`
que no existe en el `_discovery.md`.
**Mecanismo:** skill `wf-spec-fast-track` → `sdd-spec-writer` (Scope Check Paso 4; validación de args Paso 1; resolución de feature Paso 3).

1. Le pides el fast-track de un documento que en realidad describe varias capacidades, sin acotar.
   → **Esperado:** no genera un spec contaminado de multi-feature: **remite** a `/wf-spec-discover` + `/wf-spec-features-first`.
2. Pides el modo scoped pero solo aportas uno de los dos flags acoplados.
   → **Esperado:** error "`--scope-from` y `--feature` deben usarse juntos"; no asume el que falta.
3. Pides el fast-track de un `F-00X` que no está en el discovery.
   → **Esperado:** se detiene listando las features disponibles; no inventa el scope.

**Resultado:** PASS si redirige el multi-feature, exige los flags acoplados y rechaza el
ID inexistente · FALLO si genera un spec multi-feature, asume un flag ausente, o procesa un feature ID que no existe.
**Desviación → reportar:** issue citando `CU-3.j`.

## CU-3.k — Analyze: contaminación técnica detiene y las preguntas de riesgo van neutras

**Precondición:** un PRD con contaminación técnica (stack, endpoints, esquemas) y/o un gap
funcional cuya respuesta podría expandir el producto.
**Mecanismo:** skill `wf-spec-analyze` → `sdd-spec-explorer` (Check 2 pureza; Paso 5 framing de gaps).

1. Le pides analizar un PRD con tecnología metida.
   → **Esperado:** Check 2 detecta la contaminación, el veredicto es `REQUIERE_LIMPIEZA_PRD`
     y te remite a limpiar el PRD (o `wf-prd-review`/`prd-expert`) **antes** de continuar a specs; no genera specs sobre un PRD sucio.
2. El analysis formula un gap cuya respuesta podría introducir capacidad nueva.
   → **Esperado:** marca el gap `[PUEDE_REQUERIR_CR]` y redacta la pregunta **neutra** (no
     ofrece como opción "normal" una solución expansiva tipo "¿catálogo persistente o texto libre?").

3. **La prosa del gap se escribe para quien la va a contestar ([[v0.92.0]]).**
   → **Esperado:** en `Contexto`, `Problema` y `Pregunta para el cliente`, los **IDs se quedan**
     (`CA-001`, `HU-003`, `RF-006`) y las **siglas sueltas van en claro**: *"el criterio de
     aceptación de X"*, *"no tiene un resultado verificable"*. Ver **V2** de la verificación
     transversal para el comando.
   → **FALLO:** *"el CA de X"*, *"sin THEN verificable"* dentro de un bloque `[P-XXX]`. No es
     cosmético: quien presenta el gap tiene contrato de leerlo **verbatim**, así que una sigla
     ahí lo empuja a traducir — y traducir bien no se puede medir con un diff.
   → **No cuenta como fallo:** el formato nombrado en la sección **Testabilidad** (ahí el formato
     *es* el defecto que reporta) ni los IDs del campo `Afecta`.

**Resultado:** PASS si detiene por contaminación, formula neutro los gaps de riesgo y redacta su
prosa sin jerga · FALLO si genera specs con un PRD contaminado, empuja hacia una respuesta
expansiva, o deja siglas internas en los campos que lee una persona.
**Desviación → reportar:** issue citando `CU-3.k`.

## CU-3.l — Features-first: `--features` con IDs inexistentes en el discovery

**Precondición:** existe `_discovery.md`; pides un subset con al menos un ID que **no** está en él.
**Mecanismo:** skill `wf-spec-features-first` (Paso 4a — validación del subset contra el discovery).

1. Le pides generar las features de un subset que incluye un ID inventado (p. ej. `F-099`).
   → **Esperado:** **se detiene** indicando qué IDs no aparecen en el discovery y listando los
     IDs válidos; no genera nada del subset hasta que corrijas.

**Resultado:** PASS si valida el subset contra el discovery y para con el ID inválido · FALLO
si ignora el ID inexistente, o genera solo los válidos sin avisar del inválido.
**Desviación → reportar:** issue citando `CU-3.l`.

## CU-3.m — Validate en modo ligero: proporcionalidad sin relajar invariantes

**Precondición:** un spec con header `Modo: ligero`, con el núcleo de 4 presente, una sección
no-núcleo omitida **con** `N/A — modo ligero` y otra omitida **sin** esa marca.
**Mecanismo:** skill `wf-spec-validate` → `sdd-spec-auditor` (Paso 4, detección de modo).
**Read-only** (`allowed-tools: [Read, Bash]`, sin Write).

1. Le pides validar el spec ligero.
   → **Esperado:** no marca como hallazgo las secciones núcleo legítimamente omitidas con
     `N/A — modo ligero`, pero **sí** reporta como hallazgo la sección omitida **sin** la
     marca; no reescribe el spec (no tiene Write).
2. El spec ligero tiene un CA sin GIVEN/WHEN/THEN completo.
   → **Esperado:** el Check 3 lo reporta — la testabilidad es **idéntica** en ambos modos;
     el modo ligero ajusta proporción, no relaja invariantes.

**Resultado:** PASS si respeta el núcleo de 4, exige la marca `N/A` y mantiene los invariantes ·
FALLO si marca como error una omisión legítima, deja pasar una sección sin marca, o tolera un CA no testable en ligero.
**Desviación → reportar:** issue citando `CU-3.m`.

## CU-3.n — Conflict: precondición de specs insuficientes

**Precondición:** un directorio de features con 0 o 1 spec.
**Mecanismo:** skill `wf-spec-conflict` → `sdd-spec-auditor` (Paso 2).

1. Le pides detectar conflictos con un solo spec.
   → **Esperado:** informa que **se necesitan al menos 2 specs** y no fabrica un conflicto.
2. Le pides conflictos en un directorio sin specs.
   → **Esperado:** informa que no encontró specs y remite a generarlos (`wf-spec-features-first` / `wf-spec-fast-track`).

**Resultado:** PASS si exige ≥2 specs y guía cuando faltan · FALLO si reporta conflictos con
<2 specs, o falla sin explicar qué falta.
**Desviación → reportar:** issue citando `CU-3.n`.

## CU-3.o — Readiness: sin índice, ciclos de dependencia y scope derivado

**Precondición:** según el sub-escenario: (1) directorio de features sin `_features.md`;
(2) features con dependencias en ciclo; (3) una feature con alcance derivado del analysis no
consolidado en el PRD.
**Mecanismo:** skill `wf-spec-readiness` → `sdd-spec-auditor` (Pasos 2, 5, 6). Solo lee y sintetiza.

1. Le pides el readiness sin que exista `_features.md`.
   → **Esperado:** **se detiene** indicando ejecutar `wf-spec-features-first`/`wf-spec-fast-track` primero; no inventa el índice.
2. Hay un ciclo de dependencias entre features.
   → **Esperado:** **reporta el ciclo** y excluye esas features del orden de implementación,
     pero **no aborta** el resto del informe.
3. Una feature declara alcance derivado del analysis sin consolidar en PRD.
   → **Esperado:** la clasifica `REQUIERE_CAMBIO_PRD`, **no** `LISTA`.

**Resultado:** PASS si para sin índice, reporta el ciclo sin abortar y marca el scope derivado ·
FALLO si fabrica el índice, aborta todo el informe por un ciclo, o marca `LISTA` una feature con scope sin consolidar.
**Desviación → reportar:** issue citando `CU-3.o`.

## CU-3.p — Delta / gap-resolve: un cambio de producto encubierto detiene y remite a wf-prd-change

**Precondición:** un spec ya generado; le pasas un "requisito nuevo" (delta) o una "respuesta de
gap" (gap-resolve) que en realidad mueve alcance, exclusión o regla de negocio del PRD.
**Mecanismo:** skill `wf-spec-delta` (Paso 7A) / `wf-spec-gap-resolve` (Paso 4) → `sdd-spec-writer`.

1. Pides añadir al spec un "requisito" que en realidad cambia el alcance del producto (`delta analyze`).
   → **Esperado:** detecta que no es un delta de spec sino un cambio de producto; **detiene** y
     remite a `wf-prd-change` antes de seguir.
2. Pides completar un `[INCOMPLETO]` con una "respuesta" que contradice el PRD o mueve algo MVP↔fase futura (`gap-resolve`).
   → **Esperado:** **detiene** y remite a `wf-prd-change`; no integra el cambio como si fuera un gap normal.

**Resultado:** PASS si ambas vías frenan el cambio de producto encubierto y remiten a `wf-prd-change` ·
FALLO si integran la expansión/contradicción como delta o gap normal.
**Desviación → reportar:** issue citando `CU-3.p`.

## CU-3.q — Gap-resolve: confirmación de `[INFERIDO]` (tres vías)

**Precondición:** un spec de caracterización con CAs `[INFERIDO]` sin confirmar.
**Mecanismo:** skill `wf-spec-gap-resolve` → `sdd-spec-writer` (Paso 3, caso `[INFERIDO]`). La fuente
de confirmación es **el usuario**, no un `_analysis.md`.

1. Pides confirmar los `[INFERIDO]` y respondes **"Confirmado"**.
   → **Esperado:** elimina el marcador y actualiza `Evidencia:` a `confirmado por <usuario> el <fecha>`
     (mantiene la evidencia parcial original); no lo resuelve desde un `_analysis.md`.
2. Respondes **"Incorrecto"** con el comportamiento real.
   → **Esperado:** corrige el CA con ese comportamiento (o lo elimina si la capacidad no existe).
3. Respondes **"No lo sé"**.
   → **Esperado:** el marcador `[INFERIDO]` **se queda** y ese CA **sigue bloqueando** `wf-prepare-plan`.

**Resultado:** PASS si las tres respuestas se tratan distinto y "No lo sé" mantiene el bloqueo · FALLO
si confirma un `[INFERIDO]` desde el analysis, o lo da por resuelto sin confirmación humana.
**Desviación → reportar:** issue citando `CU-3.q`.

## CU-3.r — El rigor (standard/ligero) se elige al crear el spec, no en el init (D-006)

**Precondición:** proyecto SDD ya inicializado con `pipeline_mode: standard` (el default; el init
ya no pregunta el rigor — ver `cu-01-inicializar.md` CU-1.n). Le pides crear el spec de una feature.
**Mecanismo:** orquestador de la fase Spec (`pipeline/spec/CLAUDE.md` → instalado como
`.claude/rules/sdd-spec.md`, sección "Elección del rigor del pipeline"). El rigor es un **argumento**
que se propaga a cada `wf-spec-fast-track`, y esos son `context: fork` sin `AskUserQuestion`
([[D-002]]), así que debe estar resuelto **antes** del fan-out: la oferta ocurre en el hilo principal.

> **Nota ([[D-045]]):** desde que `wf-spec-features-first` corre en el hilo principal, *podría*
> preguntar el rigor él mismo. **No se ha cambiado**: la oferta sigue en el orquestador antes de
> invocar, y este escenario mide eso. Mover la elección dentro del workflow es un candidato abierto,
> no una desviación — si una pasada la ve dentro, es un FALLO contra el contrato actual.

1. Pides el spec de una feature **sin** especificar el modo.
   → **Esperado:** antes de invocar la workflow, el orquestador **ofrece** Standard (recomendado) /
     Ligero con `AskUserQuestion` y pasa el flag elegido. No asume ligero por su cuenta ni genera sin ofrecer.
2. Pides el spec pasando explícitamente `--light` (o `--standard`).
   → **Esperado:** **no** pregunta — respeta el flag.
3. El proyecto tiene `pipeline_mode: light` fijado a mano (override de proyecto) y no pasas flag.
   → **Esperado:** usa `light` sin preguntar (el equipo ya fijó el default de proyecto).
4. Pides generar un lote con `wf-spec-features-first` sin flag.
   → **Esperado:** pregunta el modo **una sola vez** para toda la pasada, nunca feature a feature.
5. Pides `--light` sobre una feature que **toca shared models, introduce entidades nuevas o expande alcance**.
   → **Esperado:** el rigor ligero **se prohíbe solo**: la workflow lo fuerza a `standard` pese al flag (regla en `kb-spec-expert`), porque en ese perfil de feature se relaja ceremonia pero **no** rigor. No genera un spec ligero sobre una feature con shared models / entidades nuevas / alcance expandido. (Es el guardrail de la última línea de `pipeline/spec/routing.md`.)

**Resultado:** PASS si ofrece la elección al crear (no en el init), respeta el flag explícito y el
override de proyecto, pregunta una sola vez por lote, y **fuerza standard cuando la feature toca shared
models / entidades / alcance pese a `--light`** · FALLO si genera ligeros sin ofrecer la elección,
re-pregunta pese a un flag explícito, pregunta feature a feature en un lote, o **deja pasar un spec ligero
sobre una feature que expande alcance / toca shared models**.
**Desviación → reportar:** issue citando `CU-3.r`.
