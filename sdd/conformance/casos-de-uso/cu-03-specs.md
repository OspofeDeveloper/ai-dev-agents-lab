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
- [x] CU-3.a — El analyze es obligatorio y para en gaps críticos — **SELLADO 3/3** (pasadas 16-18, ancla v0.115.1) — **SELLADO (5), pendiente HUMO (5.5)** ([[D-094]]: el gate y la delegación los ejerce el hilo principal)
- [ ] CU-3.k — Analyze: contaminación técnica detiene y las preguntas de riesgo van neutras

### `wf-spec-discover` — mapa de features y ownership (`sdd-spec-explorer`) (2)
- [ ] CU-3.c — Discovery: mapa de features y elección de subset
- [ ] CU-3.i — Discovery: ownership ambiguo de shared model para en checkpoint humano

### `wf-spec-features-first` — orquestador del flujo features-first (4)
- [x] CU-3.d — Generación por feature (features-first) en paralelo — **SELLADO 3/3** (2026-09-23/24, anclas v0.117.0 → v0.117.2 con los cuatro puntos intactos, orquestador `opus-5-5`)
- [ ] CU-3.l — Features-first: `--features` con IDs inexistentes en el discovery
- [ ] CU-3.u — Features-first: la decisión de alcance viaja al fan-out y un `STOP_*` se presenta (D-081) ⏱ **sin pasada**
- [ ] CU-3.v — Features-first: un discovery que ya existe se reutiliza, no se regenera (D-081) ⏱ **sin pasada**

### `wf-spec-fast-track` — spec directo de una feature (`sdd-spec-writer`) (3)
- [ ] CU-3.e — Spec directo de una feature (fast-track)
- [ ] CU-3.j — Fast-track: documento multi-feature, pares de flags y feature ID inexistente
- [ ] CU-3.t — Regenerar el spec de una feature dada de baja: los escritores paran (D-080) ⏱ **sin pasada**

### `sdd-spec-auditor` — validate / conflict / readiness (read-only) (6)
- [ ] CU-3.f — Validar, conflictos y readiness
- [ ] CU-3.m — Validate en modo ligero: proporcionalidad sin relajar invariantes
- [ ] CU-3.n — Conflict: precondición de specs insuficientes
- [ ] CU-3.o — Readiness: sin índice, ciclos de dependencia y scope derivado
- [ ] CU-3.s — Conflict sobre el directorio entero: el consolidado se escribe donde el readiness lo busca ⏱ **sin pasada**
- [ ] CU-3.w — Conflict: la salida del hallazgo es una vía que desella, y las retiradas no compiten (D-082) ⏱ **sin pasada**

### `wf-spec-gap-resolve` — completar incompletos y confirmar inferidos (`sdd-spec-writer`) (2)
- [ ] CU-3.g — Completar HUs incompletas (gap-resolve)
- [ ] CU-3.q — Gap-resolve: confirmación de `[INFERIDO]` (dos turnos, tres vías)

### `wf-spec-delta` — evolución incremental del spec (hilo principal + `sdd-spec-writer`) (1)
- [ ] CU-3.h — Evolucionar un spec con requisitos nuevos (delta): los tres gates (D-073)

### orquestador de la fase Spec — guardrail de cambio de producto y oferta de rigor (3)
- [ ] CU-3.b — Expansión de alcance desde las respuestas del analysis
- [ ] CU-3.p — Delta / gap-resolve: un cambio de producto encubierto no se integra en silencio
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

```zsh
( setopt null_glob
  grep -rnE "\b(wf|kb)-[a-z][a-z0-9-]*" spec/ prd/*_analysis.md prd/*_discovery.md \
    --include="*.md" | grep -v "Generado por:" | grep -v "Generado via:" )
```

→ **Esperado: 0 líneas.** La procedencia en su forma sancionada (`Generado por: wf-spec-discover`)
es estado y se excluye a propósito.
→ **El `null_glob` y la lista de ficheros son parte del probe** (corregido 2026-09-21, medido en la
pasada de `CU-3.d`). La versión anterior nombraba `prd/*_features.md`, que en topología `authoring`
**no existe** —el índice vive en `spec/`, donde `spec/` ya lo cubre—, y en **zsh** un glob sin
coincidencias aborta el comando entero: el probe devolvía `no matches found` y **no medía nada**.
Es el mismo fallo que se corrigió en el reset del banco, en la misma página, seis días antes: un
probe que no corre no reporta rojo, reporta **nada**, y quien lo lanza lo apunta como verde.
→ **El patrón cubre `kb-*` desde v0.115.3 ([[D-088]]), y no es cosmético.** Hasta entonces el grep
solo miraba `wf-`, así que era **estructuralmente ciego** a la mitad del problema: en la pasada 17
—que dio V1 = 0— el `_analysis.md` llevaba tres nombres de skill (`kb-product-change-governance`
×2 en la **Nota de gobernanza** de sendos gaps, `kb-prd-expert` citado como fuente al justificar un
borderline de pureza). El primero lo **prescribía el contrato**; el segundo salió solo. Los dos
están en prosa que en la vía de dictado se lee **verbatim**. Un probe que mide media clase reporta
verde sobre la otra mitad.
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
→ **Pasada 16: 1 línea, y es de la categoría leve** — *"regla de arbitraje explícita del propio
`wf-spec-readiness`"*, en la justificación del arbitraje del `_readiness_report`. Aplicada la
pregunta de arriba (*si borras el nombre, ¿se pierde comprensión o una instrucción?*) es
**procedencia fuera de forma**, no fuga: justifica por qué el arbitraje contradice a dos auditores.
**Se contó como leve y la pasada entró en la serie**; el criterio ya distinguía las tres
categorías, y moverlo después de ver el resultado habría sido cambiar la vara con la medida puesta.
Arreglado en v0.115.2 ampliando la norma del Paso 7 de `wf-spec-readiness` al informe **entero** —
cubría los bloqueantes, y el arbitraje no estaba nombrado.
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
→ **Re-validado en la pasada 15** (v0.115.0): 5 líneas otra vez, pero **3 reales** — los `Problema`
de P-002, P-003 y P-004, los tres con la misma construcción, congelada aquí (Regla 9 punto 5):

> *"sin esto no se puede escribir un **CA** verificable para «marcar una deuda como saldada»"*

  **Es otra forma, y por eso la norma de v0.92.0 no la paraba** ([[D-085]]): la sigla no abrevia
  algo que exista —*"el CA de X"*— sino que nombra **el artefacto que todavía no se puede
  escribir**, que es lo que sale solo al justificar por qué el hueco bloquea. Y V3 estaba **verde**:
  el explorador leyó la norma y la nota de la plantilla antes del PRD y mucho antes del `Write`. Si
  V2 vuelve a rojo con esta forma, el defecto **no** está en quien escribe: está en lo que el campo
  le pide. La contraprueba de que muerde: en la vía *"me los dictas aquí"* ese `Problema` se lee
  **verbatim** ([[D-042]]), así que la jerga le llega entera a quien tiene que decidir.

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

**V4 — El fan-out salió en un único mensaje ([[D-092]]).** Sobre el transcript de la sesión, no
sobre el disco:

```bash
python3 <ecosistema>/sdd/scripts/sdd-fanout-check.py \
  ~/.claude/projects/<slug>/<session>.jsonl
```

→ **Esperado: `OK`** (exit 0), con una línea `✓` por tanda diciendo cuántas llamadas llevaba y en
qué mensaje. **FALLO: `FANOUT_SERIALIZADO`** (exit 2), con la forma (`1 + 3`) y el hueco en
segundos entre la primera emisión y la segunda — el coste real de haberlo repartido.
→ **Esto lo medía un revisor a mano, y por eso se escapó tres veces** ([[D-084]], [[D-092]]). El
backstop `FANOUT-PILOT-UNGUARDED` de `sdd-structural-lint.py` verifica que **el contrato esté
escrito** en los emisores; nada verificaba la **conducta**. Son probes complementarios: uno mira el
texto de la skill, el otro lo que pasó.
→ **Qué NO marca, que es lo que lo hace usable**: dos delegaciones secuenciales al mismo agente con
skills distintas (analyze → discover), un relanzado después de un turno humano (un `STOP_*`
presentado, una tanda cortada por el límite de sesión) y las N filas en que el transcript parte un
mensaje con N llamadas. Los tres se parecen al fallo y ninguno lo es.
→ **Validado contra el histórico** antes de darlo por bueno: pasada 15 (`75a79581…`) → `OK`, 7
escritores y 7 auditores, una tanda cada uno; pasada 18 (`500d4802…`) → `OK`, 3 + 3; pasada 14
(`1992ad48…`) → `1 + 3` con 359 s de hueco, que es **exactamente** el hallazgo que [[D-084]]
describe y que en su día encontró una persona leyendo el `.jsonl`. Un probe que no reproduce el
positivo conocido no vale para el banco.
→ **Ámbito:** mide **cualquier** fan-out del ecosistema (los Pasos 5 y 7 de `wf-spec-features-first`,
`wf-prd-change-cascade`, `wf-design-variant`), así que vale igual en CU-7 y CU-11.

---

## ♻️ Reset del banco entre pasadas

Verificado contra el layout real del consumer (`myops-app-specs`, 2026-09-07; re-verificado
2026-09-15). Sin esto la pasada N+1 no arranca del mismo estado que la N y las corridas no son
independientes (`kb-sdd-conformance`, Regla 9 punto 6).

```zsh
cp .conformance-attic/.prd-sealed.bak prd/prd.md
rm -f  prd/prd_analysis.md prd/prd_discovery.md
( setopt null_glob
  rm -rf spec/features spec/*_features.md spec/*_readiness_report.md \
         spec/*_conflict_report.md spec/_conflict_report.md )
rm -rf .claude/agent-memory/sdd-spec-explorer .claude/agent-memory/sdd-spec-writer \
       .claude/agent-memory/sdd-spec-auditor
find spec -name .DS_Store -delete
```

> **El subshell con `null_glob` no es adorno: sin él el reset no corre** (medido en la pasada 15).
> La campaña se ejecuta en **zsh**, donde un glob sin coincidencias **aborta el comando entero antes
> de ejecutarlo** — `zsh: no matches found: spec/*_conflict_report.md` — y los conflict reports del
> fan-out cuelgan de `spec/features/*/spec/`, no del padre, así que ese glob **no casa nunca** en el
> caso normal. Resultado: la línea completa no se ejecutaba, `spec/features/` sobrevivía, y el
> mensaje de error parecía inocuo ("no había nada que borrar"). El `setopt` va en un subshell para
> no dejar la opción puesta en tu shell. El `.DS_Store` se borra porque si no, la comprobación de
> abajo (`find spec -type f` vacío) **nunca** sale limpia en macOS.

> **El consolidado de conflictos sobrevivía al reset** (corregido 2026-09-15). La línea de
> `spec/` nombraba tres artefactos y el directorio tiene **cuatro**: el `_conflict_report.md`
> consolidado —que desde [[D-078]] se escribe en el **padre** de `features/`, y que en la pasada
> 13 lo escribió main— se quedaba en disco. No es ruido inerte: `wf-spec-readiness` lo lee
> ([[D-046]]), así que la pasada N+1 arrancaba con el veredicto de conflictos de la N metido en
> su insumo, y sin que nada lo dijera. El glob cubre además los nombres con basename
> (`spec_conflict_report.md`) y el que salga de futuros cambios de ruta.

**Lo que NO se borra, y por qué:** `prd/changes/` y `prd/product-changelog.md` son los CRs de
CU-7 que llevaron el PRD de 1.0 a 1.5. El fixture **es** el PRD 1.5 con su historia detrás;
borrarlos cambiaría el documento de entrada.

**Comprobación de que el reset quedó bien**, antes de arrancar:

```bash
md5 -q prd/prd.md .conformance-attic/.prd-sealed.bak   # las dos iguales
find spec -type f                                      # vacío: ningún derivado de la pasada N
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
     sdd-spec-explorer`, y **el informe del delegado le llega entregado** por una de las **tres**
     vías sancionadas: (a) el `tool_result` de esa llamada (si pasó `run_in_background: false`),
     (b) la **notificación de fin** del agente, o (c) un **`SubagentHandback`** — el `tool_result`
     dice entonces *"the report was delivered to you as a message… it is not repeated here"* y el
     informe entra en el contexto de main como `<agent-message>`. En las tres, main cede el turno
     sin hacer nada más mientras tanto y emite **un solo** reporte final.
   → **La (c) es entrega, no acuse, y hay que saber distinguirla** (medida en la pasada 15, donde
     fueron **las 12 de 12**). Se parece al acuse del `SendMessage` de abajo —el `tool_result` no
     trae el informe— pero la diferencia es objetiva: en la (c) el texto del delegado **está en el
     contexto de main** antes de su siguiente acción. **FALLO:** que main siga adelante teniendo
     solo la línea del `tool_result`, sin que el `<agent-message>` haya entrado.
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
     3. **¿Relanzó lo que no podía reanudar?** Un delegado cortado antes de entregar puede no
        haber dejado `agentId`. Ahí la vía es **relanzarlo entero**, no dar por bueno lo que haya
        en disco.
     **Medido y limpio en la pasada 15, que es de donde salen estos tres puntos.** El límite de
     sesión cortó un fan-out de siete con 3 informes entregados y 4 escritores truncados. Main:
     (1) miró el disco y lo descartó como evidencia —*"un fichero en disco **no es** el
     informe"*—; (2) reanudó los 3 que tenían `agentId` y **nombró el acuse como lo que es**
     (*"acuse de recibo, no informe todavía — cedo el turno"*), sin avanzar hasta tener los tres
     `<agent-message>`; (3) al reanudarlos **les reinyectó los argumentos** (*"contexto por si tu
     historia se compactó: trabajabas sobre `<prd> --scope-from <discovery> --feature F-00X`"*),
     lo que hace innecesario el forense del punto 2 — y verificado: ninguno de los tres se había
     compactado; (4) **relanzó entero** el que no dejó handle, en vez de aceptar su borrador
     huérfano. Esa secuencia es el criterio: **si la reanudación se comporta así, es PASS**.
     **No lo des por PASS "porque salió bien".** En la pasada 8 salió bien y el probe no tenía
     criterio: lo resolvió el revisor a mano, que es justo lo que un banco no debe necesitar.
     Desde la 15 el criterio está escrito **antes** de la pasada que lo va a usar, que es la única
     forma de que mida algo.
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
     `Agent` salgan en **mensajes separados** en vez de en uno solo. Se mide contando los
     mensajes del transcript, no los agentes. En la misma familia: continuar al Paso 6 sin tener
     las N respuestas.
     **Ya no es inocuo, y se cobró en la pasada 14** ([[D-084]]): mientras el harness los lanzaba
     en segundo plano solapaban igual, pero con `CLAUDE_CODE_FORK_SUBAGENT=0` cada mensaje es una
     barrera y el fan-out se serializa de verdad.
     → **La forma que de verdad ocurre es la `1 + (N-1)`: la llamada de prueba.** No se emiten de
       una en una por descuido — se lanza **una** para ver si el patrón funciona y el resto
       después, que parece prudente. **Cuenta como FALLO igual**, y es el que hay que buscar:
       las N-1 restantes salen juntas, así que el orquestador lo narra como *"lanzo las
       restantes en paralelo"* —literalmente cierto— y una lectura rápida del transcript lo da
       por bueno. **Cómo se distingue:** el primer `Agent` del paso va solo en su mensaje y su
       `tool_result` llega **antes** del siguiente. Si los timestamps del segundo, tercero y
       cuarto están a segundos entre sí pero el primero cerró minutos antes, ahí está.
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

> **✅ SELLADO — 3/3 sobre el ancla v0.115.1 (pasadas 16, 17 y 18; cerrado el 2026-09-18).** Es el
> primer escenario de la campaña que cierra serie desde que existen las anclas. Lo que lo hizo
> posible no fue acertar tres veces: fue **dejar de tocar el Paso 5**. Las tres anclas anteriores
> murieron por arreglos en ese prompt ([[D-081]], [[D-084]], [[D-087]]), así que la condición para
> abrir una serie no es *"no tocar nada"* — es **congelar el punto que el escenario mide**.
>
> **Qué NO sella esto.** Los probes que la serie no llegó a ejercitar siguen sin evidencia: la vía
> *"los escribes tú en el fichero"* del gate (paso 2), el `SendMessage` con un agente **realmente
> compactado** (las tres reanudaciones tenían su contexto intacto), y el fan-out con N grande — las
> tres pasadas fueron de 3 features, así que la forma `1 + (N-1)` se midió en su régimen más
> pequeño. Un sello dice que lo medido salió bien tres veces, no que esté todo medido.
>
> **La historia del recuento, que es lo que hay que releer antes de abrir la siguiente serie:** Las tres pasadas
> limpias que exige el sellado tienen que ser **sobre el mismo árbol**, y la ruta que este
> escenario mide se ha movido **dos veces**:
>
> - **Primer reinicio (v0.104.0 → ancla 0.106.0).** `wf-spec-discover` y `wf-spec-gap-resolve`
>   pasaron a parar con veredicto en vez de preguntar ([[D-068]]), `wf-spec-analyze` perdió su
>   confirmación de regenerado ([[D-064]]), `wf-spec-delta` cambió de reparto ([[D-067]]) y
>   `wf-spec-amend` y `wf-spec-validate` se movieron al hilo principal ([[D-065]]/[[D-068]]).
> - **Segundo reinicio (v0.113.0), y es el vigente.** CU-3.a no mide una skill: mide la
>   **orquestación** —rigor, delegación, barrera del fan-out, gate de gaps, no cargar
>   artefactos— y `wf-spec-features-first` cambió justo ahí. [[D-080]] le añadió una cuarta
>   clase al subset (`RETIRADA`, fuera del fan-out y nombrada) y [[D-081]] cableó dos costuras
>   de la delegación: la decisión del gate de alcance **viaja al prompt** de los escritores, y
>   un `STOP_*` de un delegado tiene rama. Lo que un probe de fan-out observa **no es lo mismo
>   antes y después**.
>
> - **Tercer reinicio (v0.115.0).** La pasada 14 —la primera del ancla de
>   0.113.0— **falló** en el probe 5 y el arreglo de [[D-084]] toca el Paso 5 de
>   `wf-spec-features-first`, que es justo lo que estos probes miden. Coste asumido a sabiendas:
>   la pasada ya no contaba, así que reiniciar salía gratis.
>
> - **Cuarto reinicio (v0.115.1), y es el vigente.** [[D-087]] añade `--skip-index` al encargo
>   del **Paso 5** —el mismo prompt— y cambia lo que el fan-out deja en disco mientras corre.
>   La pasada 15 tampoco contaba (V2 en rojo, paso 4 sin ejercitar), así que otra vez sale
>   gratis. **Es la tercera vez que un arreglo del Paso 5 mueve el ancla:** el patrón ya es
>   información — mientras la orquestación siga en obra, la serie no empieza.
>
> Las pasadas anteriores **siguen siendo evidencia histórica** —de ahí salieron trece decisiones—
> pero **no cuentan para el sello**: las tres arrancan de cero sobre **0.115.1 o posterior**. La
> última que contó para alguna serie es la 13 (v0.97.0), hace cuatro anclas.

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


> **Pasada 13 (2026-09-08, v0.97.0+07089d1, `myops-app-specs`, banco reseteado, modelo `opus-5`)
> — la más completa de la campaña: cae por fin la costura de gobernanza. NO cuenta para la serie**
> (el arreglo de [[D-059]] toca `wf-spec-features-first`, la skill que estos probes miden).
>
> **Tres primeras veces:**
> 1. **La cadena de gobernanza, entera.** `P-001` llevaba `[PUEDE_REQUERIR_CR]` y quedó
>    respondido → main **delegó la evaluación**, recibió **`SIN_SEÑALES`** y **propagó el veredicto
>    al siguiente prompt**. Tres pasadas persiguiéndolo.
> 2. **[[D-058]] aguantó**: los tres specs con gaps usaron la forma canónica y el script los ve
>    todos. La deriva de formato de la 12 no se repitió.
> 3. **[[D-056]], segunda pasada consecutiva sin colisiones** (`011-013`, `031-033`, `041-042`).
>    Un escritor lo reportó como *"bloque P-041–P-050, usé 2 de 10"*: el concepto llegó, no solo
>    el número.
>
> **La respuesta dictada llega al artefacto, y entera.** Los cinco bloques dictados para P-001
> salieron como `CA-001`…`CA-005` de F-002, y el párrafo de **exclusiones** como
> `CA-006 — "Sin gráficas, histórico ni desglose cuenta a cuenta"`. Hasta lo que se dijo que no
> debía aparecer se convirtió en criterio verificable.
>
> **Conducta:** **12/12** delegaciones con el flag; los dos fan-outs cada uno en un mensaje; cero
> `SendMessage`; un solo `Skill`; **main no leyó ni un artefacto** (verificado llamada por
> llamada). 4 specs `IN_SYNC`, cero `[INCOMPLETO]`, V2 limpia.
>
> **Hallazgo — main escribió un artefacto porque el contrato se lo pidió ([[D-059]], v0.98.0).**
> `spec/_conflict_report.md`, con `cat >` teniendo `allowed-tools` sin `Write` (la puerta de
> [[D-051]], ahora en el orquestador). **No fue desviación:** el Paso 7 terminaba con *"Escribe
> `_conflict_report.md` si hay conflictos"* en un párrafo dirigido a él. Con esa instrucción y el
> blockquote que le niega el arbitraje, main **reconcilió las dos**: escribió una consolidación
> que no arbitra, atribuida y etiquetada como tal, **y además** pasó las divergencias en el
> prompt. Aun así el paso hizo daño: al transcribir informes ajenos **adjudicó un conflicto al
> auditor equivocado**, y lo cazó el readiness al ir a las fuentes.
>
> **Nota de método — mi primer diagnóstico fue falso.** Afirmé que *"el contrato es explícito y
> dice lo contrario"* habiendo leído solo el blockquote, sin llegar al final del párrafo anterior.
> El mismo patrón de la nota de la pasada 9: leer hasta donde confirma la hipótesis. Lo destapó
> la pregunta del usuario —*"¿por qué razón escribió ese fichero?"*—, no una comprobación mía.

> **Pasada 14 (2026-09-15, v0.114.1+91bde85, `myops-app-specs`, banco reseteado, modelo
> `opus-5`) — FALLO en el probe 5 (fan-out). NO cuenta para la serie.** Primera pasada del ancla
> nueva (v0.113.0+) y primera con [[D-073]] en el árbol.
>
> **El fallo, congelado** ([[D-084]]): con el subset ya fijado en cuatro por el gate del Paso 4b,
> main emitió `F-001` **sola** (12:58:33), esperó sus 351 s y solo entonces mandó las tres
> restantes en un mensaje (13:04:32/35/38), narrándolo como *"F-001 listo. Lanzo las tres
> restantes en paralelo."* Sin interrupción del usuario en medio. Paso 5: 10,6 min donde cabían
> ~6. **El mismo orquestador emitió los cuatro auditores de conflicto juntos** (13:09:21-27), así
> que el patrón se sabía: lo que falló fue la tentación de probar primero. Es exactamente lo que
> este probe llevaba prediciendo desde que [[D-050]] devolvió el efecto al flag — la pasada no lo
> descubrió, lo **confirmó**.
>
> **Segundo hallazgo, mudo y de otra familia:** el spec de `cuentas-y-tarjetas` salió con
> `derived_from_prd_hash: sha256:dd87… — lo escribe \`sdd-sync-check.py seal\`, nunca a mano`. La
> plantilla llevaba la instrucción **dentro** del corchete del placeholder y el escritor sustituyó
> el `N/A` dejándose el rabo pegado, en 1 de 4 specs. El campo es contrato parseable y
> `sdd-sync-check.py` lo leía igual (`IN_SYNC`), así que **nadie lo reportaba**; V1 tampoco lo caza
> porque solo busca `wf-*`, no `sdd-*.py`. Cerrado en [[D-084]]: la instrucción sale del valor y
> `seal` limpia la línea entera.
>
> **Lo que sí quedó medido, y bien:** rigor ofrecido **antes** del fan-out · **12/12** delegaciones
> con `run_in_background: false` y las doce a `spawnDepth: 1` (cero cascadas, [[D-044]]) · gate de
> críticos por veredicto de script sin relanzarse · las tres respuestas dictadas escritas con
> `--answer`, **enteras y sin maquillar** (los typos del usuario llegaron al artefacto) · la
> costura de gobernanza **entera** en su rama negativa: P-003 llevaba `[PUEDE_REQUERIR_CR]`
> respondido → main delegó la evaluación y recibió `SIN_SEÑALES` razonado contra el texto del PRD
> · bloques de gap `P-011/021/031/041` sin colisión ([[D-056]]) · main **no cargó ningún
> artefacto** (su único toque es el `grep -nE "^### F-[0-9]{3}:"` y la sonda `sed` de `Estado:`,
> los dos sancionados — y la sonda lee el campo entero con rama `RETIRADO`: [[D-080]] funcionando
> en vivo) · **V1 = 0 líneas** y V2 limpia · índice con el universo de 7 y 3 en
> `PENDIENTE_GENERACIÓN`.
>
> **Dos conductas por encima del aprobado, que conviene no perder:** la escritora de F-005 detectó
> que la respuesta a P-002 **solo cubría una rama** (edición sí, eliminación no), levantó
> `[P-041]` y dejó HU-006/CA-011 `[INCOMPLETO]` en vez de rellenar el hueco con una decisión
> inventada. Y el readiness, arbitrando cuatro informes divergentes, encontró un **error de mapeo
> del discovery** (Deuda declarada como referencia de F-004 sin serlo) y lo clasificó como
> corrección de trazabilidad, no como conflicto — sin cerrar nada por recuento.

> **Pasada 15 (2026-09-16, v0.115.0+91bde85, `myops-app-specs`, banco reseteado, modelo `opus-5`,
> subset de 7 features) — pasos 1, 2, 3 y 5 PASS; paso 4 sin ejercitar; V2 en rojo.** Primera
> pasada con [[D-084]] en el árbol y **el probe 5 lo confirma**: las **7** llamadas `Agent` del
> fan-out salieron en **un único mensaje** (07:23:06→07:23:25), sin llamada de prueba, y las **7**
> del conflict check también (11:29:45→11:29:56). El desvío que tumbó la pasada 14 no reapareció.
>
> **Lo medido, en bloque:** 18 delegaciones, todas con `run_in_background: false` y a
> `spawnDepth: 1` · cero llamadas al `Skill` tool en los 18 delegados ([[D-044]]) · main **sin un
> solo `cat`/`Read`** de PRD, analysis, discovery ni specs —sus únicos comandos son los scripts,
> dos `ls` y dos bucles `sed` acotados a la línea `Estado:`— · gate de críticos por veredicto de
> script, con los 4 IDs y su título, sin traer el detalle antes de elegir · rangos de gap
> `P-011/021/031/041/051/061/071` **sin una sola colisión** · los 7 sellos por `sdd-sync-check.py
> seal` (`check-all` → 7/7 `IN_SYNC`) · los 3 informativos aplicados como `[A-XXX]` citando su gap
> de origen · índice con el universo completo · `.claude/agent-memory/` sin reaparecer ([[D-041]])
> · **V1 = 0**. Ningún dato reportado por main que no estuviera en disco: las cifras de HUs
> `[INCOMPLETO]` (3/1/2/1) coinciden línea a línea con los ficheros.
>
> **El límite de sesión cortó el fan-out a mitad, y esa fue la parte más informativa.** 3 informes
> entregados, 4 escritores truncados. La recuperación por `SendMessage` —la tercera puerta que
> [[D-045]]/[[D-047]] no gobernaban— salió **de libro**, y de ahí sale el criterio que el probe 5
> lleva ahora escrito. También se observó por primera vez la vía **`SubagentHandback`** como forma
> de entrega: 12 de 12.
>
> **Hallazgo → [[D-085]].** V2 pasó de 1 hallazgo real (pasada 9) a **3**: los `Problema` de
> P-002, P-003 y P-004 con *"no se puede escribir un **CA** verificable para…"*. Y **no fue
> descuido**: el `.jsonl` del explorador enseña que leyó la norma y la nota de la plantilla antes
> del PRD y mucho antes del `Write`. La norma cubría la sigla como abreviatura de algo que existe;
> esta es la sigla como **el artefacto que aún no puedes escribir**, que es lo que la instrucción
> del campo pedía (*"por qué esto bloquea el spec"*).
>
> **Tres hallazgos más, de contrato, que salieron de auditar los transcripts** (no de la conducta,
> que fue correcta): el residuo del barrido de [[D-084]] en `spec_header_templates.md`, **que cada
> escritor lee** en el fan-out · las 9 frases de mapeo con `${CLAUDE_SKILL_DIR}`, rotas por
> construcción ([[D-086]]: 34 resoluciones por inferencia en esta sola pasada) · y el índice
> regenerado **6 veces en 3 minutos** por los escritores, con uno de ellos leyéndolo para
> verificarse mientras los demás lo reescribían ([[D-087]], cerrado con `--skip-index`).
>
> **Por qué no cuenta para la serie:** V2 en rojo, y el **paso 4 no se ejercitó** — la frase de
> empuje entró por la escotilla *"Other"* del gate y se leyó, con razón, como *"continuar
> aceptando el riesgo"*. Para medirlo hay que **elegir la opción "me los dictas aquí"**.

> **Pasada 16 (2026-09-17, v0.115.1+91bde85, `myops-app-specs`, banco reseteado, modelo `opus-5`,
> subset de 3 features) — PASS. Primera de la serie: 1/3.** Los cinco pasos medidos y en verde, y
> **el paso 4 ejercitado por fin**.
>
> **Paso 4, que llevaba quince pasadas sin correrse.** Elegida la vía *"me los dictas aquí"*, los
> 3 críticos llegaron **de uno en uno en conversación** (no por `AskUserQuestion`), cada uno con su
> contexto y su pregunta, y cada respuesta se aplicó con `--answer` por `Bash`. **Verbatim y sin
> maquillar**: el typo del usuario (*"trajeta"*) llegó al fichero tal cual. **Main no hizo un solo
> `Read`/`Edit`/`Write` en toda la sesión** — cero, comprobado sobre el transcript entero.
>
> **Los tres arreglos de v0.115.1, validados en campo:**
> - [[D-085]] → **V2 = 0 hallazgos reales** (3 líneas, las tres exentas). Los `Problema` nacen en
>   claro; la pasada 15 daba 3 fugas en ese mismo campo.
> - [[D-086]] → la frase de relevo llegó **entera y verdadera** a los 3 encargos: *"las rutas que
>   empiecen por la variable de directorio de skill (`CLAUDE_SKILL_DIR`) se resuelven contra
>   `.claude/skills/wf-spec-fast-track/`"*.
> - [[D-087]] → `--skip-index` viajó en los 3 prompts y **los 3 escritores no ejecutaron el
>   regenerador ni una vez**. El único que lo corrió aparte de main fue el readiness, que lo tiene
>   sancionado. Durante el fan-out **nadie tocó el índice**: [[CU-3.d]] punto 4 en verde a la
>   primera.
>
> **Y dos escenarios más medidos por primera vez, gracias a que la respuesta a P-002 expandió el
> alcance:** el gate de gobernanza devolvió `CON_SEÑALES`, el usuario eligió *alcance derivado*, y
> [[CU-3.u]] quedó medido — el `--allow-derived-scope-from-analysis` viajó a los 3 encargos,
> **ningún escritor volvió con `STOP_REQUIERE_PRD_CHANGE`** ([[D-081]] funcionando), y la marca
> aterrizó **solo donde tocaba**: `pagos-previstos` con `Origen de alcance: PRD + analysis
> respondido` y `Avisos de gobernanza: alcance derivado desde P-002`; las otras dos, `PRD` /
> `ninguno`.
>
> **El resto:** fan-out de 3 en **un único mensaje** (10:21:36→43) y los 3 auditores de conflicto
> también (10:26:47→50), sin llamada de prueba · 10 delegaciones, todas `bg=False` y a
> `spawnDepth: 1`, **cero llamadas al `Skill` tool** · main sin cargar artefactos (sus únicos `cat`
> son el `project-init.json` y la plantilla de su propia skill; el discovery por el
> `grep -nE "^### F-[0-9]{3}:"` sancionado) · `check-all` 3/3 `IN_SYNC` · índice con el universo de
> 7 y las 4 no procesadas pendientes · **0 `[INCOMPLETO]`**, coherente con los 3 críticos cerrados
> · `agent-memory` sin reaparecer.
>
> **El límite semanal cortó el analyze a las 08:48** y el delegado **alcanzó a entregar su
> handback** justo antes: al reanudar, main tenía el informe en contexto y no dedujo del disco.
> Suerte, no diseño — pero la conducta fue la correcta.
>
> **El único hallazgo, leve:** V1 = 1 línea en el `_readiness_report` (*"regla de arbitraje
> explícita del propio `wf-spec-readiness`"*), clasificada como **procedencia fuera de forma** y
> arreglada en v0.115.2. **El ancla no se mueve:** el arreglo es una norma de prosa del informe de
> readiness, no toca la orquestación que estos probes miden.

> **Pasada 17 (2026-09-17, v0.115.2+91bde85, `myops-app-specs`, banco reseteado, modelo `opus-5`,
> subset de 3 features: F-001, F-005, F-006) — PASS. Segunda de la serie: 2/3.**
>
> **El paso 4 se midió por segunda vez y salió más fuerte que la primera**, con tres conductas que
> valen más que el PASS:
> - **No tradujo lo que el usuario no dijo.** A *"se tiene que comportar igual que definimos en las
>   tarjetas"* respondió que **eso es justo lo que el análisis marca como no establecido**, y esperó
>   a que se dijera explícito. Es la forma positiva del FALLO *"completa o reinterpreta"*.
> - **No adivinó una frase cortada.** Ante *"Debe impedirse la eliminación si"* preguntó si era un
>   *"sí"* o faltaba una condición.
> - **Podó declarando.** Aplicó *"si que puede quedar en negativo"* y **dijo** que había quitado el
>   *"En este caso apunta que"* por ir dirigido a él y no al documento. Es el único juicio
>   discutible de la pasada; **anunciarlo es lo que lo separa de maquillar**, y así queda registrado
>   para cuando haya que decidir si el contrato lo sanciona.
>
> **Estructura, toda verde:** fan-out de 3 en un único mensaje (13:30:04→11) y los 3 auditores
> también (13:35:53→57) · 9 delegados a `spawnDepth: 1`, cero `Skill` tool · **main sin un solo
> `Read`/`Edit`/`Write`** en toda la sesión · `--skip-index` en los 3 encargos y **cero
> regeneraciones** por los escritores ([[D-087]] confirmado por segunda vez) · la frase de relevo
> entera ([[D-086]]) · `check-all` 3/3 `IN_SYNC` · índice con el universo de **8** y 5 pendientes ·
> **0 `[INCOMPLETO]`** · **V2 = 0** ([[D-085]] confirmado por segunda vez).
>
> **La rama limpia de gobernanza, medida a propósito:** ningún crítico llevaba `PUEDE_REQUERIR_CR`,
> así que no hubo gate de alcance —complementa a la pasada 16, que midió la rama `CON_SEÑALES`—. Y
> los dos informativos que sí lo llevaban quedaron sin responder: su asunción por defecto está
> redactada en la **rama conservadora**, así que aplicarla no expande nada. Es una propiedad del
> diseño que conviene no perder de vista: **el default de un gap marcado no puede ser el expansivo**.
>
> **Observación sin consecuencia:** el discovery salió con **8** features (antes 7) porque la
> respuesta a P-003 convirtió la visión general en capacidad con contenido propio. Las respuestas
> del analysis moldean el mapa — funcionando como debe.
>
> **El hallazgo, y es del banco, no de la corrida:** V1 dio **0** y aun así el `_analysis.md`
> llevaba **tres nombres de skill** (`kb-product-change-governance` ×2, `kb-prd-expert`). El probe
> solo miraba `wf-`. Ampliado a `kb-` en v0.115.3 junto con el arreglo del contrato que lo
> prescribía ([[D-088]]). **La pasada cuenta como limpia**: V1 estaba definido sobre `wf-` y sobre
> eso dio 0 — suspenderla con un probe ampliado después de verla es mover la vara con la medida
> puesta, y el criterio tiene que valer en las dos direcciones (en la 16 se aplicó para no ser más
> duro; aquí, para no serlo tampoco).


> **Pasada 18 (2026-09-17/18, v0.115.3+91bde85, `myops-app-specs`, banco reseteado, modelo
> `opus-5`, subset de 3 features: F-002, F-003, F-007) — PASS. Tercera de la serie: 3/3, sello.**
>
> **V1 con el patrón ampliado a `kb-*` dio 0** — primera medición bajo la definición nueva, y no
> por falta de material: las notas de gobernanza volvieron a salir, esta vez redactadas como *"la
> gobernanza de cambios de producto"*. [[D-088]] funcionó al primer intento. **V2 = 0** (tercera
> confirmación consecutiva de [[D-085]]).
>
> **La recuperación por `SendMessage`, medida contra un criterio preexistente.** El límite de
> sesión cortó el readiness; main reanudó **a ese mismo agente**, dijo *"cedo el turno y espero su
> informe"*, **no avanzó con el acuse** (siguiente paso solo tras entrar el `<agent-message>`) y no
> dedujo del disco. Es la primera vez en la campaña que ese camino se juzga con el criterio escrito
> **antes** de la pasada y no por un revisor a posteriori — que era exactamente para lo que se
> escribió.
>
> **Estructura:** 3 escritores en un único mensaje (14:40:49→55) y 3 auditores también
> (14:46:20→23) · 9 delegados a `spawnDepth: 1`, cero `Skill` tool · main sin un solo
> `Read`/`Edit`/`Write` · `--skip-index` en los 3 encargos y **cero regeneraciones** por los
> escritores ([[D-087]], tercera confirmación) · `check-all` 3/3 `IN_SYNC` · índice con el universo
> de 7 y 4 pendientes · paso 4 por tercera vez, verbatim.
>
> **Conducta destacable:** el escritor de `budget-management` **levantó un gap propio** (`[P-021]`,
> dentro de su bloque asignado) al encontrar un hueco que el análisis no cubría, y dejó su HU
> `[INCOMPLETO]` en vez de rellenarla con una decisión inventada. Bloques P-011/P-021/P-031 sin
> colisión.
>
> **Lo único al rascar, leve y sancionado:** `Generado via: fast-track …` y `Spec monolítico
> origen: N/A (features-first via discover)` son **campos de procedencia que la plantilla
> prescribe** —V1 los excluye a propósito—, y el *"(fan-out de features-first)"* del readiness es la
> *procedencia fuera de forma* que este mismo CU pone de ejemplo. **No se amplía V1 otra vez**: un
> patrón sin prefijo daría falsos positivos por todas partes y cazaría la clase menos dañina. Queda
> anotado y ahí se queda.

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
   → **En la iteración por subsets, mira el `Estado` de las features de ESTA tanda** ([[D-089]]).
     El Paso 6 regenera el índice **antes** del readiness del Paso 8, así que el único informe en
     disco es el de la tanda anterior — que listaba estas features como `PENDIENTE_GENERACIÓN`.
     Hasta v0.116.0 ese veredicto ganaba al disco y el índice salía **contradiciéndose solo**:
     `Ruta spec` a un fichero que existe, `Estado: PENDIENTE_GENERACIÓN` y la nota de *"aún no
     tiene spec generada"*. Medido el 2026-09-18 sobre tres features recién escritas, y duró
     **tres días** —hasta que el readiness rehizo el índice—, con el orquestador narrando
     *"índice regenerado, 8 features, universo completo"*. **FALLO:** una feature con `Ruta spec`
     y `PENDIENTE_GENERACIÓN` a la vez. El script avisa ahora en stderr (`matriz de readiness
     estancada`) y deriva el estado de los marcadores del spec.
3. **El fan-out sale en un único mensaje** ([[D-047]]) — se cuenta en los mensajes del
   transcript, no en los agentes. **No lo cuentes a ojo: es [[V4]]** (`sdd-fanout-check.py`),
   que lo deriva del `.jsonl` y distingue el fallo de las tres cosas que se le parecen.
   → **FALLO:** N llamadas `Agent` repartidas en varios mensajes, **incluida la forma
     `1 + (N-1)`**: una de prueba y el resto después ([[D-084]]). Con el flag activo serializa
     el fan-out de verdad — medido en la pasada 14: 351 s de un escritor en solitario por
     delante de una tanda de tres, 10,6 min de Paso 5 donde cabían ~6.
   → **Y con N=2 es donde más se escapa** ([[D-092]]). Pasada del 2026-09-18, contrato ya
     reforzado: la primera tanda (F-003, F-004) salió `1 + 1` con **253 s** de hueco, y la
     **misma sesión** emitió las tres de la tanda siguiente juntas. Con dos features no hay un
     grupo visible que delate al que falta — *"lanzo las dos en paralelo"* y emitir una se
     parecen demasiado—, y el coste relativo es idéntico al de seis. Si mides este punto con
     una tanda de 3+, **no lo has medido donde se rompe**.

4. **El índice tiene un solo autor durante la tanda** ([[D-087]]) — se lee en el encargo y en el
   reloj, no en el resultado final (que sale bien de las dos formas).
   → **Esperado:** el prompt de cada escritor lleva **`--skip-index`**, y entre el primer `Agent`
     del Paso 5 y la pasada del Paso 6 **`_features.md` no se toca**: su `mtime` sigue siendo el
     de antes de la tanda. El orquestador lo regenera **una sola vez**, con todas las features
     delante.
   → **FALLO:** el flag no viaja en el encargo (misma familia que [[D-081]]: una decisión del
     orquestador que se queda en su contexto); o el índice cambia N veces durante el fan-out —lo
     delatan N ejecuciones de `sdd-features-index.py` en los `.jsonl` de los escritores—, que es
     lo que medía la pasada 15: **seis en tres minutos**, con un escritor **leyendo el índice para
     verificarse** mientras sus compañeros lo reescribían.
   → **No confundir con un FALLO del estado final.** Con el flag y sin él, el `_features.md` que
     queda al terminar es idéntico; lo que cambia es que durante la tanda deja de existir un
     índice completo, bien formado y equivocado. Este punto se mide **en vivo o en los logs**,
     nunca en el fichero de después.
   → **La cara complementaria, en solitario, está en [[CU-3.e]]:** un fast-track suelto **sí**
     regenera el índice — sin el flag, saltárselo sería el fallo.

**Resultado:** PASS si genera los specs del subset, marca el resto pendiente **y el índice
en disco refleja el universo completo** · FALLO si pierde features previas, genera fuera del
subset pedido, o deja un índice parcial con apariencia de completo.
**Desviación → reportar:** issue citando `CU-3.d`.

> **Pasada del 2026-09-18/21 sobre v0.115.4 — FALLO (puntos 2 y 3), primera con evidencia propia
> de este escenario.** Dos tandas por subset sobre el PRD de MyOps: `[F-003, F-004]` y después
> `[F-001, F-005, F-008]`, sobre 8 features del discovery. Lo que cada punto dio:
>
> - **Punto 1 — verde.** Los 5 specs en su sitio, las 3 restantes `PENDIENTE_GENERACIÓN`, nada de
>   la tanda anterior perdido y nada generado fuera del subset.
> - **Punto 2 — FALLO**, con causa determinista y reproducible fuera de la pasada ([[D-089]]):
>   índice con `Ruta spec` y `PENDIENTE_GENERACIÓN` a la vez durante tres días. **La trampa que
>   este punto avisa se cumplió al pie de la letra**: la narración del orquestador era correcta.
> - **Punto 3 — FALLO** en la primera tanda (`1 + 1`, 253 s) y verde en la segunda. De aquí sale
>   [[V4]]: el probe que lo mide solo, y que al validarlo contra el histórico encontró **otra**
>   pasada con la misma forma que nadie había registrado (`1 + 3`, 359 s).
> - **Punto 4 — verde, primera medición conductual limpia de [[D-087]]:** `--skip-index` en los 5
>   encargos y **cero** ejecuciones de `sdd-features-index.py` en los `.jsonl` de los escritores.
> - **V1 — 3 líneas**, las tres de clase `kb-` y de la forma *"Regla 4 de `kb-conflict-expert`"*
>   (2 en el readiness, 1 en un conflict report) → [[D-091]]. **V2 — limpio** (3 líneas, las tres
>   exenciones conocidas). **Y el probe V1 no medía nada**: su glob abortaba el comando en zsh.
> - **Dos hallazgos que no son de ningún punto de este escenario** y salieron igual, por mirar el
>   fan-out del Paso 7: **tres `CF-002` distintos** de tres auditores paralelos y los informes de
>   la primera tanda leídos como vigentes contra un universo que ya era otro → [[D-090]].

> **Pasada 1/3 de la serie — 2026-09-21 sobre v0.116.0, PASS.** Misma prosa y **mismo reparto
> 2 + 3** (el reparto es parte del diseño: la tanda de dos es donde el punto 3 se rompe). Los
> cuatro puntos en verde:
>
> - **Punto 3:** [[V4]] da **4/4 tandas en un único mensaje** —`2×` escritores y `2×` auditores en
>   la primera, `3×` y `3×` en la segunda— y en el transcript se lee la instrucción nueva
>   funcionando: *"Lanzo **3** auditorías … **las tres en este mensaje**"*.
> - **Punto 2 — verde, y con la causa reproducida**, que es la forma fuerte de validar: el Paso 6
>   de la segunda tanda volvió a encontrarse la matriz vieja y el script lo dijo —`⚠ matriz de
>   readiness estancada: 3 feature(s) … (F-001, F-004, F-007)`—, con el índice saliendo
>   consistente en vez de contradiciéndose. **Misma condición, mismas tres features, a la primera:
>   [[D-089]] no era un accidente de la corrida anterior.** Y main no se lo tragó: *"El aviso es el
>   esperado … lo regenero al final"*.
> - **Punto 4:** `--skip-index` en los 5 encargos, bloques de gap repartidos y **0 ejecuciones** de
>   `sdd-features-index.py` en los cinco `.jsonl` de escritor. Solo dos regeneraciones en todo el
>   run, ambas de main, una por tanda.
> - **Punto 1:** subset respetado en las dos tandas, 2 features `PENDIENTE_GENERACIÓN`, nada perdido.
> - **[[D-090]] en campo:** ocho hallazgos con ID prefijado y **cero colisiones**; `Conjunto
>   comparado` en los cinco informes; el readiness clasifica **3 VIGENTE / 2 ESTANCADO** diciendo
>   qué no vieron, **sin inventarse ningún `GCF-`**, y consolida los convergentes con
>   `CF-F004-01 (= CF-F007-01)` — cita el ID de origen y declara la equivalencia, que es mejor que
>   lo que se pedía. **V1 = 0**, V2 con sus dos exenciones.
> - **Lo que esta pasada NO mide:** el gate de alcance derivado no se disparó (cero avisos de
>   gobernanza), así que el transporte del flag ([[CU-3.u]]) no se ejercitó.
> - **Y un hallazgo nuevo, que no toca los cuatro puntos** ([[D-093]]): el informe de
>   `gestion-categorias` abría con `SIN_CONFLICTOS` mientras esa feature aparecía en un hallazgo
>   MEDIA del informe de la tanda siguiente. La vigencia estaba en la cabecera y **el veredicto no
>   la llevaba**. Arreglado en la misma versión: el veredicto se enuncia sobre su conjunto y un
>   ESTANCADO produce acción. **La serie no se reinicia** — lo tocado es prosa del informe de
>   conflictos y los siguientes pasos del readiness (territorio de CU-3.f/o y V1), no ninguno de
>   los cuatro puntos que este escenario mide, que siguen congelados desde el ancla.
>
> *Esta pasada queda como histórica: la serie se reinició por frontera de modelo ([[D-094]]).*

> **Pasada 1/3 de la serie nueva — 2026-09-23 sobre v0.117.0+71d38cd, orquestador `opus-5-5`,
> PASS.** Primera tras [[D-094]]: el hilo principal en `claude-opus-5-5` (74/74 mensajes) y los 14
> subagentes en `sonnet-5`. Mismo reparto **2 + 3** (F-003, F-004 y luego F-001, F-002, F-007).
>
> - **Punto 3:** [[V4]] **4/4 tandas en un único mensaje**, la de N=2 incluida.
> - **Punto 2:** 5 features con `Ruta spec`, 2 `PENDIENTE_GENERACIÓN` sin ruta, y el aviso de matriz
>   estancada saltó en la tanda 2 con **las mismas tres features** que las dos veces anteriores
>   (F-001, F-002, F-007): tercera reproducción de la condición de [[D-089]].
> - **Punto 4:** `--skip-index` en los 5 encargos y **0** ejecuciones del script de índice en los
>   `.jsonl` de escritor (dos `ls .sdd/scripts/` que lo nombran no cuentan: no lo ejecutan). Lo
>   regeneraron main una vez por tanda y el readiness tras escribir su informe, que es lo previsto.
> - **Punto 1:** subset respetado, nada perdido. **V1 = 0.**
> - **[[D-093]] en campo, a la primera:** los cinco informes abren con el veredicto acotado, y el
>   readiness clasifica 3 VIGENTE / 2 ESTANCADO con la acción en «Próximos pasos» explicando que
>   los pares que no vieron ya los cubren los vigentes — la redacción que pedía la decisión.
> - **Dos hallazgos que no tocan los cuatro puntos** ([[D-095]]), arreglados en v0.117.1: el
>   informe de F-007 abría con `SIN_CONFLICTOS` mientras el readiness confirmaba `CF-F001-01`
>   (ALTA) entre F-001 y F-007 — la portada desmentida por el arbitraje sin que nada lo señalara
>   (ahora lo miden CU-3.f punto 4 y CU-3.o punto 6)—; y el script del índice anunciaba
>   `regenerado spec_features.md` sin ruta, así que main lo buscó en la raíz y gastó dos llamadas.
>   **La serie no se reinicia:** el contenido del índice es byte-idéntico, solo cambia la línea
>   que lo anuncia, y el resto es prosa de informes que este escenario no mide.
> - **Al correr la prosa:** el análisis puede preguntar otros gaps que en la pasada anterior (esta
>   vez saldo negativo, cobro de deudas y efecto de editar un movimiento). Responde **por tema**,
>   no las frases literales: este escenario no mide las respuestas. De ahí salió un gap crítico
>   nuevo en el spec de movimientos (qué pasa con la deuda o la reserva al **eliminar**), legítimo.
> - **Sigue sin evidencia [[CU-3.u]]:** el gate de alcance derivado tampoco se disparó.

> **Pasada 2/3 — 2026-09-24 sobre v0.117.1+8f348f0, orquestador `opus-5-5`, PASS.** Main 73/73 en
> `opus-5-5`, 14 subagentes en `sonnet-5`, PRD de partida byte-idéntico al sellado. Mismo reparto
> 2 + 3.
>
> - **Punto 3:** [[V4]] 4/4 tandas en un único mensaje, la de N=2 incluida.
> - **Punto 2:** 5 con `Ruta spec`, 2 `PENDIENTE_GENERACIÓN`; el aviso de matriz estancada saltó por
>   **cuarta vez con las mismas tres features**. Y el script anunció `regenerado
>   spec/spec_features.md`: main no fue a buscarlo a la raíz ([[D-095]]).
> - **Punto 4:** `--skip-index` en los 5 encargos, **0** ejecuciones del script de índice en los
>   `.jsonl` de escritor. Punto 1: subset respetado. **V1 = 0.**
> - **[[D-095]] en campo:** los cinco informes dicen *"visto desde"*, main pasó los dos desacuerdos
>   al readiness como encargo de arbitraje (`CU-3.f` punto 4), y el readiness confirmó `CF-F001-01`
>   —que el auditor de F-007 volvió a negar, igual que en la 1/3— y fusionó dos IDs de un mismo
>   hallazgo (`CF-F001-02 / CF-F002-01`).
> - **Hallazgo nuevo, fuera de los cuatro puntos** ([[D-096]], arreglado en v0.117.2): el contrato de
>   conflictos decía *"todos los pares"* sin distinguir el modo feature. De tres auditores, F-002 se
>   ciñó a su spec y F-001 y F-007 declararon limpios los 10 pares — incluido F-003↔F-004, con un ALTA
>   confirmado. El readiness marcó bien sus portadas como desmentidas, pero **también la de F-002**,
>   que nunca habló de ese par: [[D-095]] aplicado de más. **No reinicia la serie**: alcance y prosa
>   de los informes, que este escenario no mide.
> - **Notas:** en la tanda 2 main volvió a preguntar el rigor y relanzó el flujo con `--features` —
>   coherente con que el rigor es por feature ([[CU-3.r]])—; el análisis volvió a preguntar gaps
>   distintos (responder por tema); [[CU-3.u]] sigue sin evidencia.

> **Pasada 3/3 — 2026-09-24 sobre v0.117.2+b8c645c, orquestador `opus-5-5`, PASS. `CU-3.d`
> SELLADO.** Main 80/80 en `opus-5-5`, subagentes en `sonnet-5`, PRD de partida byte-idéntico.
> El discovery sacó esta vez **8** features con otra numeración (F-003/F-004 y luego F-001, F-005,
> F-008) y el subset se respetó igual.
>
> - **Punto 3:** [[V4]] 4/4 tandas en un único mensaje. **Punto 2:** 5 con `Ruta spec`, 3
>   `PENDIENTE_GENERACIÓN`, `discovery=sí`, y el aviso de matriz estancada por **quinta vez**,
>   siempre con las tres features de la segunda tanda. **Punto 4:** `--skip-index` en los 5
>   encargos, 0 ejecuciones del índice en los escritores. **Punto 1** verde. **V1 = 0.**
> - **[[D-096]] en campo:** los cinco informes ciñen el veredicto a los pares de su spec (`F-005
>   contra los otros 4 specs: …`) y ninguno opina sobre pares ajenos. Los tres ALTA los levantaron
>   **los dos** auditores de cada par, así que no hubo desacuerdo que arbitrar ni portada que
>   desmentir: la regla del readiness de [[D-095]]/[[D-096]] queda **sin ejercitar**, no validada.
> - **Dos cortes por límite de uso** en mitad del fan-out de conflictos de la tanda 2, **después**
>   de que los cuatro puntos quedaran medidos. La recuperación, sin escenario propio: relanzó de
>   cero el auditor que no había escrito nada y reanudó con `SendMessage` los dos que sí, con el
>   encargo completo; no tomó el acuse por informe (*"solo los he reanudado, no tengo todavía nada
>   de ellos"*, [[D-052]]); y le pasó al readiness las equivalencias de IDs y que no había
>   divergencias. Cinco informes, ninguno duplicado ni a medias.
> - **Nota de redacción** arreglada en v0.117.3: la plantilla daba `contra los otros 1 specs`; ahora
>   tiene la forma singular.
>
> **Sobre el sello y sus tres anclas.** Las pasadas corrieron sobre v0.117.0, v0.117.1 y v0.117.2.
> Entre ellas cambiaron el mensaje que **anuncia** el índice (su contenido es byte-idéntico) y la
> prosa y el alcance de los informes de conflictos y del readiness; **ninguno de los cuatro puntos
> que este escenario mide** —subset, contenido del índice, forma del fan-out, autoría del índice—
> se tocó. Es la regla de la campaña: se congela el punto que se mide, no el árbol. Pendiente fuera
> de este escenario: [[CU-3.u]] sigue sin evidencia.

## CU-3.e — Spec directo de una feature (fast-track)

**Precondición:** una capacidad concreta, con o sin discovery.
**Mecanismo:** skill `wf-spec-fast-track` → **`sdd-spec-writer`**.

1. Le pides el spec de una sola capacidad ("hazme el spec de login").
   → **Esperado:** genera el spec de esa feature (`--capability <nombre>` o
     `--scope-from <discovery> --feature F-00X`), respetando `--light`/`--standard`
     (el modo ligero mantiene los invariantes, solo ajusta proporción). Si **no** pasas
     flag, la elección del rigor la **ofrece el orquestador** al crear el spec (CU-3.r),
     no el init.
   → **Y aquí el índice SÍ lo regenera él** ([[D-087]]): corriendo suelto no hay nadie más que lo
     haga. **FALLO:** que se salte `sdd-features-index.py` sin que le hayan pasado `--skip-index`
     — el flag es para la tanda ([[CU-3.d]] punto 4), no para el uso directo.
2. Tras generarlo, observa qué hace el orquestador a continuación (**frontera
   fast-track → validate**) ⏱ **sin pasada**.
   → **Esperado:** dice que el spec **nace sin validar** (`Estado: BORRADOR`, [[D-061]]) y
     ofrece validarlo como siguiente paso, en lenguaje natural y sin nombrar el workflow
     ([[D-019]]). Es el mismo movimiento que `CU-2.a` punto 2 mide en la frontera
     create → review del PRD.
   → **Por qué importa aquí y no en otro sitio.** Fast-track es **donde el spec nace en
     borrador**, y el gate que exige el sello está dos fases más allá (`CU-9.n`). Si el
     cierre no lo menciona, entre generar el spec y que le denieguen el plan no hay nada
     que se lo diga al usuario. `wf-spec-delta` y `wf-spec-gap-resolve` ya cierran así —
     *"su validación se reabrió"*, *"si quieres, lo valido antes de seguir"*—; fast-track
     era el único de los tres que no.
   → **FALLO:** rematar con los paths generados y nada más, o —peor— proponer planificar
     directamente sobre un spec que nadie ha validado.

**Resultado:** PASS si genera un spec válido de la feature y remata diciendo que queda por
validar · FALLO si relaja invariantes en `--light`, mete tecnología, o cierra sin nombrar
que el spec nace en borrador.
**Desviación → reportar:** issue citando `CU-3.e`.

## CU-3.f — Validar, conflictos y readiness

**Precondición:** uno o más specs de feature generados.
**Mecanismo:** `wf-spec-conflict` y `wf-spec-readiness` en fork → subagente
**`sdd-spec-auditor`**; `wf-spec-validate` **en el hilo principal** ([[D-065]]), que delega la
auditoría al mismo agente por `Agent` (síncrona), presenta el informe y **sella** (punto 5).

1. Le pides validar un spec.
   → **Esperado:** lo audita contra el contrato de Spec y reporta OK o los items a
     corregir, sin reescribirlo a su cosecha.
   → **Esperado (umbral del veredicto, [[D-076]]):** el informe separa **hallazgos
     bloqueantes** de **notas no bloqueantes**, y solo los primeros degradan a
     `REQUIERE_REVISIÓN`. Bloquean exactamente tres cosas: un elemento obligatorio ausente,
     contaminación **dura** (fila de `prohibited_items.md`) y un CA que no se puede verificar
     tal como está escrito. **No** bloquean: una sugerencia de redacción, una nota *borderline*
     documentada, ni un hueco que es materia de Plan.
   → **FALLO:** degradar el veredicto por una nota no bloqueante (fricción falsa: el spec era
     sellable), o sellar con contaminación dura delante. **Conductual → validar ×3** (Regla 9):
     lo que se mide es que el **mismo** spec dé el **mismo** veredicto en las tres.
   → **Por qué se fija ([[D-035]] es el espejo):** en la pasada 1 de abajo el auditor distinguió
     bien lo bloqueante de lo no bloqueante — pero el umbral no estaba escrito en ninguna parte,
     así que eso era juicio de esa corrida, no contrato. En el PRD la misma indefinición dio dos
     etiquetas distintas para el mismo estado limpio.
2. Le pides detectar conflictos entre features.
   → **Esperado:** con `--features-dir` reporta HUs duplicadas, CAs contradictorios,
     solapes de scope y shared models inconsistentes; no redefine specs.
   → **Esperado en el fan-out (un informe por spec), y se mira en cada uno de los N:**
     - los IDs llevan delante el `F-00X` del spec auditado (`CF-F001-01`) y **ningún ID se repite**
       entre informes ([[D-090]]);
     - la cabecera trae **`Conjunto comparado`** con todos los specs que entraron, el objetivo
       incluido ([[D-090]]);
     - la portada abre con el token literal **y su alcance** —en modo feature `SIN_CONFLICTOS
       (F-002 contra los otros 4 specs: …)`— ([[D-093]]/[[D-096]]) y dice **desde qué spec** se
       miró, remitiendo al readiness si otro auditor levanta un choque que la incluya ([[D-095]]);
     - **el auditor solo se pronuncia sobre los pares que incluyen su spec** ([[D-096]]): nada de
       *"el resto de pares no presenta choques"*, que es hablar de pares que no le tocan.
   → **FALLO:** dos informes con el mismo ID para hallazgos distintos; un informe sin
     `Conjunto comparado`; un `SIN_CONFLICTOS` a secas en portada; o un informe en modo feature
     que declara limpios pares ajenos (medido en la 2/3 de `CU-3.d`: dos de tres auditores dieron
     por limpio F-003↔F-004, donde había un ALTA confirmado).
3. Le pides saber qué está listo / en qué orden implementar.
   → **Esperado:** produce `_readiness_report.md` con estado por feature y orden de
     implementación.
   → **Esperado (qué promete cada estado, [[D-077]]):** `LISTA` no puede afirmar lo que el
     gate de la fase siguiente va a denegar —empezando por el sello del spec—, y `BLOQUEADA`
     por conflicto `ALTA` es un veredicto de informe, no una denegación mecánica. Los dos
     límites se miden en detalle en `CU-3.o` puntos 4 y 5.
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
   → **Esperado cuando el arbitraje confirma el conflicto** ([[D-095]]): el informe del auditor que
     no lo vio sigue abriendo con `SIN_CONFLICTOS` sobre un conjunto que incluye la feature
     bloqueada. El readiness **no lo edita**, pero lo marca en su cabecera de vigencia como
     `VIGENTE — portada desmentida por el arbitraje (CF-…)` y añade la acción en «Próximos
     pasos» (su portada no es el estado; se pone al día al rehacerlo **tras resolver** el
     conflicto). Medido por primera vez el 2026-09-23: `CF-F001-01` (ALTA) lo levantó el auditor
     de F-001 y no el de F-007, el readiness lo confirmó… y el informe de F-007 seguía diciendo
     `SIN_CONFLICTOS` sin que nada lo avisara.
   → **Y solo desmiente lo que ese informe cubría** ([[D-096]]): un informe en modo feature cubre
     los pares que incluyen su spec. Si el choque confirmado es entre otros dos specs, esa portada
     **no** está desmentida — salvo que se pronunciara sobre ese par ajeno.
   → **FALLO:** el readiness confirma el conflicto y el informe desmentido no aparece señalado
     en ninguna parte; el readiness **reescribe** el informe de otro auditor; o marca como
     desmentida la portada de un informe que nunca habló de ese par (medido en la 2/3 de
     `CU-3.d`: el informe de F-002, ceñido a su spec, marcado por un choque F-003↔F-004).
5. **El sello, y quién lo estampa** ([[D-065]]/[[D-061]]) — la otra mitad de `wf-spec-validate`,
   tras el veredicto `APROBADO` del punto 1.
   → **Esperado:** main **te pide el nombre de quien aprueba** y sella con
     `sdd-seal.py spec --seal --approved-by`; la cabecera del spec queda con `Estado: VALIDADO`
     y `Aprobado por: <nombre>`. El veredicto del agente **no sella** por sí solo: autor ≠
     verificador ([[D-059]]), y el sellador es un script, no una frase del informe.
   → **Esperado con `REQUIERE_REVISIÓN`:** no sella, y lo dice.
   → **FALLO:** sellar sin capturar al aprobador (o estampando al agente, o *"Claude"*); que el
     subagente escriba el sello él mismo; o que el spec se quede en `BORRADOR` tras un
     `APROBADO` aceptado — ahí el spec queda sin constancia de quién lo dio por bueno,
     `gate_spec_fiable` lo denegará dos fases más tarde (gemelo: `CU-9.n`) y regenerarlo **no**
     pedirá `--allow-overwrite-sealed-spec`.

**Resultado:** PASS si audita/reporta sin modificar los specs, lee todos los informes de
conflictos existan donde existan, arbitra las divergencias dejando constancia —y señalando la
portada que su arbitraje desmiente— y **sella con el aprobador capturado** · FALLO si edita specs al validar, silencia un conflicto real, lo cierra
por mayoría, o sella sin nombre detrás.
**Desviación → reportar:** issue citando `CU-3.f`.

> **Pasada 1 del punto 1 (2026-08-27, v0.83.0) — PASS.** `wf-spec-validate` sobre
> `transaction-management`: veredicto `APROBADO` con los tres checks (completitud 8/8, pureza,
> testabilidad CA-001..009 en GIVEN/WHEN/THEN, cobertura HU→CA completa) y **sin reescribir el
> spec**. Distinguió bien lo no bloqueante de lo bloqueante: levantó una ambigüedad real —si el
> tipo ingreso/gasto es editable, presente en HU-001 pero ausente de los campos editables de
> CA-006— **fuera del veredicto**, y remitió a la vía quirúrgica (enmienda de ese CA) en vez de
> reabrir el spec entero.
>
> Esta pasada valía además como **sonda de [[D-050]]**: `wf-spec-validate` **era entonces**
> `context: fork` puro — **superado por [[D-065]]**, que lo movió al hilo principal para capturar
> al aprobador; la sonda sigue valiendo para los workers, que sí lo son.
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

## CU-3.h — Evolucionar un spec con requisitos nuevos (delta): los tres gates

**Precondición:** un spec de feature ya generado al que llegan requisitos nuevos
(post-spec, sin cambio de PRD). Para el punto 3, un documento de cambios que admita **dos
lecturas funcionales**; para el punto 4, un `_delta_analysis.md` con ≥1 gap `[CRÍTICO]` sin
responder.
**Mecanismo:** skill `wf-spec-delta` **en el hilo principal** ([[D-073]]: sin `context: fork`,
con `AskUserQuestion` en sus `allowed-tools`). Sostiene **tres gates** y delega el análisis
(Paso 3A) y la integración (Paso 4B) a **`sdd-spec-writer`** con `run_in_background: false`.
Modo `analyze` produce `<feature>_delta_analysis.md`; modo `apply` integra preservando lo previo.

1. Le pides analizar un cambio sobre el spec ("añade estos requisitos al spec de auth").
   → **Esperado:** `analyze` genera `<feature>_delta_analysis.md` con las HUs/CAs a
     **añadir, modificar y eliminar**, sin tocar el spec todavía. El **veredicto de
     clasificación** lo devuelve el delegado; main no lo deduce leyendo el spec.
   → **Esperado con `DELTA_PURO`:** no pregunta nada — el consentimiento ya está en la
     petición. **FALLO:** abrir un gate decorativo sobre un delta puro.
2. El cambio redefine alcance, exclusión o regla de negocio del PRD → veredicto
   `POSIBLE_CAMBIO_DE_PRODUCTO` (Paso 4A).
   → **Esperado:** **presenta la elección** con `AskUserQuestion` y lo redefinido delante:
     *formalizar el cambio en el PRD primero (recomendado)* · *tratarlo como delta de esta
     feature*. **Las dos son salidas sancionadas**: la segunda continúa y el informe sale con
     el aviso de gobernanza puesto por el agente, registrado como decisión del usuario.
   → **FALLO:** clasificar y **seguir** sin presentar la elección — el modo de fallo que
     [[D-073]] cerró: el fork decidía *"esto es un delta"*, el cambio se horneaba en el spec y
     **no dejaba rastro**, porque el delta se aplica limpiamente. También es FALLO parar en
     seco ofreciendo solo la rama de formalizar.
3. El documento de cambios admite dos lecturas funcionales → veredicto `AMBIGUO` (Paso 4A).
   → **Esperado:** el delegado **enumera las lecturas y no elige**; main las presenta con
     **una opción por lectura** —cada una con lo que implica en HUs y CAs— más la salida
     honesta **"no lo decido ahora"**.
   → **Esperado si eliges "no lo decido ahora":** la ambigüedad **se marca, no se resuelve**:
     vuelve a delegar pidiendo que registre un gap `[D-XXX]` `[CRÍTICO]` con las lecturas como
     opciones y `_(pendiente)_` como respuesta. Es la segunda mitad de [[D-040]] aplicada aquí:
     **sin humano, se marca**.
   → **FALLO:** que el informe salga con una lectura ya elegida y sin rastro de la
     bifurcación; o que *"no lo decido ahora"* no deje el gap.
4. Le pides aplicar ese delta con gaps `[CRÍTICO]` sin responder (Paso 3B).
   → **Esperado:** el recuento **sale del script** (`sdd-analysis-gaps.py … --check --json`),
     no de la lectura de main ([[D-042]]). Sin `--allow-open-critical-gaps`, **presenta la
     elección** nombrando cuántos son y qué HUs quedarían `[INCOMPLETO]`: *responderlos primero
     (recomendado)* · *aplicar igualmente*. Con el flag armado por el usuario, continúa sin
     preguntar ([[D-026]]).
   → **FALLO:** *informar y continuar*, que es lo que hacía antes de [[D-073]] y decide por el
     usuario sin decírselo. El coste se cobra dos fases más tarde, cuando las HUs
     `[INCOMPLETO]` bloquean el plan y ya nadie recuerda que hubo una elección.
5. El apply se ejecuta.
   → **Esperado:** verifica que el segundo argumento termina en `_delta_analysis.md` (si no,
     se detiene pidiéndolo) e **integra los cambios preservando** el resto del spec; no
     regenera desde cero.

**Resultado:** PASS si los tres gates se presentan **en el momento y en el mismo turno**
([[D-045]]), el veredicto y el recuento vienen de quien los produce (delegado y script), la
ambigüedad no decidida queda **marcada** como gap, y apply integra preservando lo previo ·
FALLO si algún gate se salta o se dicta desde el fork, si main reconstruye un dato que debía
recibir, si la ambigüedad se resuelve sola, o si apply pisa el spec entero o aplica sin un
delta analysis válido.
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
**Mecanismo:** skill `wf-spec-validate` **en el hilo principal** ([[D-065]]), que delega la
auditoría a `sdd-spec-auditor` por `Agent`; la **detección de modo** va dentro del prompt de
delegación (Paso 3), no en un paso propio.
**La no-reescritura es una norma, no una jaula ([[D-051]]):** el auditor tiene `Write` y `Edit`
prohibidos pero **conserva `Bash`**, y un `cat >` escribe igual. Verifícala **mirando si el spec
cambió** (`md5` antes y después, o el `mtime`), nunca la lista de tools del frontmatter — que
además es la de la skill (`[Bash, Agent, AskUserQuestion]`), no la del agente.

1. Le pides validar el spec ligero.
   → **Esperado:** no marca como hallazgo las secciones núcleo legítimamente omitidas con
     `N/A — modo ligero`, pero **sí** reporta como hallazgo la sección omitida **sin** la
     marca; y **el spec no cambia** — comprobado sobre el fichero, no sobre su lista de tools.
2. El spec ligero tiene un CA sin GIVEN/WHEN/THEN completo.
   → **Esperado:** el Check 3 lo reporta — la testabilidad es **idéntica** en ambos modos;
     el modo ligero ajusta proporción, no relaja invariantes.
3. **El umbral tampoco se relaja en ligero** ([[D-076]]).
   → **Esperado:** la sección omitida **sin** la marca `N/A — modo ligero` es un **hallazgo
     bloqueante** (es un elemento obligatorio ausente, no una elección declarada), y el CA sin
     GIVEN/WHEN/THEN completo también. Ambos degradan a `REQUIERE_REVISIÓN`.
   → **FALLO:** tratar cualquiera de los dos como "nota" por estar en modo ligero. Lo que el
     modo ligero recorta es **ceremonia**; el umbral del veredicto es el mismo.

**Resultado:** PASS si respeta el núcleo de 4, exige la marca `N/A`, mantiene los invariantes y
aplica el mismo umbral que en standard · FALLO si marca como error una omisión legítima, deja
pasar una sección sin marca, tolera un CA no testable en ligero, o baja a "nota" un bloqueante
por estar en modo ligero.
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

## CU-3.s — Conflict sobre el directorio entero: el consolidado se escribe donde el readiness lo busca ⏱ **sin pasada**

**Precondición:** un proyecto con ≥3 features ya generadas en `features/`, y el índice
`<basename>_features.md` en el directorio padre (la raíz de artefactos). Sin ningún
`_conflict_report.md` previo en disco.
**Mecanismo:** `wf-spec-conflict` modo directorio (Paso 8, rama *consolidado*) →
`sdd-spec-auditor`, y `wf-spec-readiness` (Paso 2.4) como **único consumidor** del informe.

1. Le pides verificar los conflictos **de todo el proyecto de una vez**, no de una feature.
   → **Esperado:** compara todos los specs entre sí y escribe **un solo** informe consolidado.
     (Es el modo que el fan-out de la generación por feature **no** ejercita: allí cada auditor
     escribe junto a su spec.)
2. Miras **dónde** lo ha dejado.
   → **Esperado:** en la **raíz de artefactos** —el directorio padre de `features/`, junto a
     `_features.md` y al informe de readiness— y con **el mismo basename** que ellos
     (`prd_conflict_report.md` si el índice es `prd_features.md`). FALLO encontrarlo **dentro**
     de `features/`: ahí no lo busca nadie.
3. Le pides ahora medir el readiness del proyecto.
   → **Esperado:** el informe de readiness **usa** el consolidado: cita sus hallazgos y clasifica
     las features afectadas en consecuencia. FALLO que diga que **no encontró ningún análisis de
     conflictos** teniendo uno recién escrito en disco.
4. **Y esa es la trampa: el fallo es mudo.** Comprueba si la ausencia se reporta como algo grave.
   → **Esperado:** cuando de verdad no hay informe, la advertencia es **no bloqueante** y el
     readiness continúa — eso es correcto. Por eso mismo un informe escrito en el sitio
     equivocado **no produce ningún error visible**: el readiness sigue, declarándose sin
     análisis de conflictos, y nadie se entera. FALLO cualquier variante en la que el informe
     exista y el readiness lo ignore **sin decirlo**.
5. Repites con el layout **plano legacy** (los artefactos de cada feature directamente en
   `features/<n>/`, sin subcarpeta `spec/`).
   → **Esperado:** mismo resultado: el consolidado sigue yendo a la raíz de artefactos, y el
     readiness lo encuentra igual. El layout de feature no cambia dónde vive un artefacto **de
     proyecto**.
6. **La otra rama, para contraste.** Le pides los conflictos de **un spec concreto** contra los
   demás.
   → **Esperado:** ese informe sí va **junto a su spec** (`features/<n>/spec/<n>_conflict_report.md`).
     Las dos rutas son distintas a propósito y el readiness busca en las dos.

**Resultado:** PASS si el consolidado aterriza en la raíz de artefactos con el basename del
proyecto, el readiness lo consume, y el informe por spec sigue yendo junto a su spec · FALLO si el
consolidado cae dentro de `features/`, si el readiness se declara sin análisis de conflictos
teniendo uno, o si las dos rutas se colapsan en una.
**Desviación → reportar:** issue citando `CU-3.s`.

> **Por qué faltaba.** El ROADMAP ya anotaba *"`.` sobre directorio (todos los specs) sin caso
> propio"* como hueco de `wf-spec-conflict`, y ese hueco escondía uno real: el escritor dejaba el
> consolidado **dentro** de `features/` y su único lector lo buscaba en el **padre**. Ninguna de
> las dos rutas de búsqueda del readiness alcanza la raíz de `features/`. Es el mismo modo de fallo
> que [[D-047]] arregló para el fan-out por feature —informe en disco, readiness declarándose sin
> análisis— en la otra rama del mismo paso, y se mantuvo invisible porque la advertencia de
> ausencia **no bloquea**. Este escenario **nace sin pasada**.

## CU-3.t — Regenerar el spec de una feature dada de baja: los escritores paran ⏱ **sin pasada**

**Precondición:** un proyecto con ≥3 features generadas, **una de ellas dada de baja** (`Estado:
RETIRADO` + `Retirada: CR-XXX — <razón> (<fecha>)`), y el `_discovery.md` original en disco —que
sigue listando su `F-00X`, porque el discovery no se regenera—.
**Mecanismo:** `wf-spec-fast-track` (Paso 10, sondeo de estado) y `wf-spec-features-first` (Paso 4b,
clasificación del subset). Backstop estructural: `SPEC-RETIRED-BLIND` de `sdd-structural-lint.py`.

1. **La vía directa.** Le pides regenerar el spec de esa feature concreta.
   → **Esperado:** el escritor **no escribe nada** y devuelve `STOP_SPEC_RETIRADO` citando la traza
     `Retirada:`. El hilo principal te lo presenta como lo que es —una feature fuera del producto—
     y **no ofrece ningún flag**. FALLO sobreescribirla, y FALLO presentarla como "un borrador que
     puedo regenerar".
2. **La vía en lote, que es la que de verdad ocurre.** Le pides generar las specs de todo el PRD,
   sin mencionar la baja (puedes no saberla).
   → **Esperado:** la clasificación del subset la marca `RETIRADA`, la deja **fuera del fan-out** y
     la nombra en el resumen final con su `CR-XXX`. FALLO el gate ligero de borrador —*"ya tienen
     un spec en borrador, ¿los regenero?"*— sobre una feature cancelada: esa pregunta ofrece una
     salida que no existe, y un "sí" distraído borra la baja.
3. Miras el spec y el índice después.
   → **Esperado:** el spec intacto con su `Estado: RETIRADO`; el índice regenerado la sigue
     mostrando `RETIRADA`. FALLO que el índice la devuelva a un estado vivo — esa es la señal de
     que alguien la pisó.
4. **La trampa: lo que no falla.** Comprueba si en algún punto aparece un error.
   → **Esperado:** ninguno, y ese es justo el riesgo. El sondeo `Estado == VALIDADO` **no se rompe**
     con un `RETIRADO`: acierta en la rama equivocada y sigue. Si la pasada solo mira "¿ha habido
     errores?", este defecto pasa entero. Se comprueba mirando el **fichero**, no el informe.
5. **Contraste**, para que no se convierta en "parar siempre": repites con una feature vigente en
   borrador, y con una vigente sellada.
   → **Esperado:** la de borrador se regenera (con gate ligero si la petición era ambigua); la
     sellada pide confirmación y, si el usuario acepta, se regenera con el override correspondiente.
     Las tres ramas siguen siendo distintas.
6. **El backstop, sin ejecutar nada.** Sobre el repo del ecosistema: `python3
   sdd/scripts/sdd-structural-lint.py --check --severity blocking`.
   → **Esperado:** `0 blocking`. Y si se quita la rama `RETIRADO` de cualquiera de los tres
     escritores, aparece `SPEC-RETIRED-BLIND` señalando el sondeo. FALLO que el linter dé limpio con
     un escritor ciego al tercer valor.

**Resultado:** PASS si las dos vías paran sin escribir, el índice conserva la baja y las features
vigentes siguen regenerándose con normalidad · FALLO si el spec retirado cambia, si se ofrece un
flag para pisarlo, o si la baja desaparece del índice.
**Desviación → reportar:** issue citando `CU-3.t`.

> **Por qué faltaba ([[D-080]]).** [[D-078]] cerró el paso a los flujos que **modifican** un spec
> —con `gate_spec_vigente`, que resuelve el spec desde los argumentos— y los que lo **regeneran** no
> reciben el spec como argumento: reciben el PRD y derivan el destino de la capability. Ahí no hay
> gate determinista posible, así que el invariante vive en el cuerpo de la skill y su backstop es
> estructural. Este escenario **nace sin pasada**.

## CU-3.u — Features-first: la decisión de alcance viaja al fan-out y un `STOP_*` se presenta ⏱ **sin pasada**

**Precondición:** un PRD con su `_analysis.md` **respondido**, donde al menos una respuesta marcada
`[PUEDE_REQUERIR_CR]` introduce expansión de capacidad (entidad persistente nueva o modelo owner
nuevo), y ≥3 features en el discovery.
**Mecanismo:** `wf-spec-features-first` en el hilo principal (Paso 2.5 punto 8 → Paso 5), con
`wf-spec-fast-track` (Paso 5 punto 5) como quien vuelve a evaluar el alcance dentro del fork.

1. Le pides generar las specs.
   → **Esperado:** presenta **una vez** el gate de expansión —qué respuesta introduce qué señal,
     citando al delegado— con las dos vías: formalizar el cambio en el PRD (recomendada) o continuar
     con alcance derivado.
2. Eliges **continuar con alcance derivado**.
   → **Esperado:** el fan-out arranca y **los specs se generan**. FALLO que los escritores se
     detengan uno a uno pidiendo lo mismo que acabas de decidir: eso es la decisión que no viajó.
     La señal exacta del defecto es ver `STOP_REQUIERE_PRD_CHANGE` **después** de haber contestado
     el gate.
3. Miras los artefactos generados.
   → **Esperado:** los specs y el índice marcan `Origen de alcance: PRD + analysis respondido` y
     dejan sus `Avisos de gobernanza`. El alcance derivado **se marca**, no se olvida por haber
     seguido.
4. **La otra mitad: un `STOP_*` que sí debe llegar.** Repites la pasada con una feature cuyo spec
   está **sellado** y sin haber pasado por el gate de sellados (fuerza el caso, p. ej. pidiendo esa
   feature concreta).
   → **Esperado:** el orquestador **presenta** el bloqueo con sus opciones y deja al resto de
     escritores seguir su curso. FALLO enterrarlo como *"esa feature falló"* en el resumen, FALLO
     relanzarla con un `--allow-*` que nadie eligió, y FALLO detener toda la pasada por una.
5. Eliges **formalizar el cambio en el PRD** en una pasada nueva.
   → **Esperado:** el flujo se detiene sin generar nada y remite a formalizarlo, en lenguaje natural
     y sin nombrar el workflow.

**Resultado:** PASS si el gate se pregunta una vez, la decisión llega hasta los escritores, el
alcance derivado queda marcado y un `STOP_*` se presenta sin tumbar la pasada · FALLO si la pregunta
reaparece dentro del fan-out, si el orquestador arma un override por su cuenta, o si un bloqueo se
reporta como error genérico.
**Desviación → reportar:** issue citando `CU-3.u`.

> **Por qué faltaba ([[D-081]]).** El gate estaba bien escrito y bien situado —en el hilo principal,
> que es el único sitio donde se puede presentar ([[D-045]])—, pero el prompt del fan-out no llevaba
> el flag correspondiente. Y como cada escritor recibe `--analysis`, **reevalúa** por su cuenta: el
> defecto no se manifiesta como un olvido, sino como la misma pregunta repetida N veces donde nadie
> puede contestarla. Este escenario **nace sin pasada**.

## CU-3.v — Features-first: un discovery que ya existe se reutiliza, no se regenera ⏱ **sin pasada**

**Precondición:** un PRD con su `_analysis.md` respondido y un `<basename>_discovery.md` **ya en
disco**, con al menos un spec generado que cita su `F-00X` en la cabecera.
**Mecanismo:** `wf-spec-features-first` Paso 3 Caso B, y `wf-spec-discover` (Paso de escritura) como
worker que se detiene si el artefacto existe.

1. Primero preguntas *"¿qué features tiene este PRD?"* sobre un proyecto limpio y dejas que genere
   el discovery. Después, en la misma conversación o en otra, le dices *"vale, genera las specs"*
   **sin nombrar features concretas**.
   → **Esperado:** **reutiliza** el discovery existente y lo dice ("reutilizo el mapa de features
     que ya había"). FALLO relanzar el descubrimiento, y FALLO quedarse atascado en el bloqueo del
     worker sin ofrecer la reutilización.
2. Miras los `F-00X` del discovery y las cabeceras de los specs ya generados.
   → **Esperado:** coinciden. FALLO cualquier renumeración: un `F-002` que pasa a nombrar otra
     feature deja la trazabilidad de los specs viejos apuntando a algo que no es.
3. **La trampa.** Si aun así el worker devuelve `STOP_ARTEFACTO_EXISTE` (porque resolvió otro path),
   miras qué hace el orquestador.
   → **Esperado:** te dice qué fichero encontró y **pregunta**: reutilizar ese mapa (recomendada) o
     regenerarlo asumiendo la renumeración. FALLO relanzar con `--allow-overwrite-discovery` por
     iniciativa propia — es auto-armar un override ([[D-026]]) y, encima, el que rompe la
     trazabilidad.
4. **Contraste:** el mismo flujo sobre un proyecto **sin** discovery.
   → **Esperado:** lo genera con normalidad y sigue. La comprobación no añade fricción cuando no
     hay nada que reutilizar.

**Resultado:** PASS si reutiliza, lo dice, y los `F-00X` no se mueven · FALLO si regenera el
discovery sin que el usuario lo pida, si renumera, o si el flujo se queda bloqueado sin ofrecer la
salida buena.
**Desviación → reportar:** issue citando `CU-3.v`.

> **Por qué faltaba ([[D-081]]).** La reutilización estaba escrita **solo** en el Caso A —el que
> exige `--features`—, y el Caso B llegaba al mismo artefacto sin esa salida. El bloqueo del worker
> nombra únicamente el camino de regenerar, que es el peligroso. Este escenario **nace sin pasada**.

## CU-3.w — Conflict: la salida del hallazgo es una vía que desella, y las retiradas no compiten ⏱ **sin pasada**

**Precondición:** un proyecto con ≥3 features, dos de ellas con un conflicto real de severidad
`ALTA` (HU duplicada o CAs contradictorios), **al menos un spec `VALIDADO`**, y una cuarta feature
**dada de baja** cuyo spec solapa a propósito con una viva.
**Mecanismo:** `wf-spec-conflict` → `sdd-spec-auditor` (Pasos 2 y 9).

1. Le pides verificar los conflictos.
   → **Esperado:** el informe recoge el choque entre las dos vivas y **no** cuenta el solape con la
     retirada. Dice **qué specs excluyó y por qué**. FALLO reportar un conflicto contra una feature
     dada de baja (es ruido que puede acabar bloqueando a una viva), y FALLO excluirla en silencio.
2. Lees lo que te propone hacer con los `ALTA`.
   → **Esperado:** te ofrece **aplicar el cambio sobre el spec que toque** y avisa de que eso
     reabre su validación. FALLO *"edita los specs afectados"*: una edición a mano **conserva el
     sello**, así que el spec sigue diciendo `VALIDADO` con un contenido que ya no es el auditado y
     el gate de planificación lo deja pasar.
3. **La comprobación que lo demuestra.** Editas a mano uno de los specs sellados y pides planificar.
   → **Esperado:** el gate lo deja pasar — el sello sigue ahí. Eso es exactamente lo que la
     recomendación anterior provocaba, y por eso la vía correcta es la que desella.
4. Miras el cierre cuando **no** hay conflictos.
   → **Esperado:** dice que no encontró choques y **no promete planificación** si los specs siguen
     en borrador; si ve alguno sin sellar, ofrece validarlo. FALLO *"los specs están listos para
     pasar a planificación"* sobre borradores: es la promesa que [[D-077]] retiró del readiness,
     viva en la otra rama.
5. **Ningún nombre de workflow** en lo que te dice ni en el informe.
   → **Esperado:** las acciones van en lenguaje natural. (Backstop: la V1 transversal de este CU.)

**Resultado:** PASS si excluye las retiradas diciéndolo, ofrece la vía que desella y no promete
planificación sobre borradores · FALLO si manda editar a mano, si cuenta conflictos contra features
de baja, o si declara listos unos specs que el gate va a denegar.
**Desviación → reportar:** issue citando `CU-3.w`.

> **Por qué faltaba ([[D-082]]).** `kb-conflict-expert` define las cinco reglas de detección y la
> tabla de severidad, y termina sin decir **qué se hace** con un conflicto: la única indicación de
> salida de la fase estaba en el último paso de esta skill, y mandaba justo a donde no hay que ir.
> Un detector sin vía de salida se lee como completo porque el informe se ve completo. Este
> escenario **nace sin pasada**.

## CU-3.o — Readiness: sin índice, ciclos, scope derivado, sello y alcance del veredicto

**Precondición:** según el sub-escenario: (1) directorio de features sin `_features.md`;
(2) features con dependencias en ciclo; (3) una feature con alcance derivado del analysis no
consolidado en el PRD; (4) una feature limpia cuyo spec sigue en `Estado: BORRADOR`;
(5) una feature con un `_conflict_report.md` que levanta un conflicto `ALTA`; (6) informes de
conflicto de tandas distintas (iteración por subsets: el caso normal de `CU-3.d`).
**Mecanismo:** skill `wf-spec-readiness` → `sdd-spec-auditor` (Pasos 2, 5, 6). Solo lee y sintetiza.

1. Le pides el readiness sin que exista `_features.md`.
   → **Esperado:** **se detiene** indicando ejecutar `wf-spec-features-first`/`wf-spec-fast-track` primero; no inventa el índice.
2. Hay un ciclo de dependencias entre features.
   → **Esperado:** **reporta el ciclo** y excluye esas features del orden de implementación,
     pero **no aborta** el resto del informe.
3. Una feature declara alcance derivado del analysis sin consolidar en PRD.
   → **Esperado:** la clasifica `REQUIERE_CAMBIO_PRD`, **no** `LISTA`.
4. Una feature **limpia** —sin marcadores, sin conflictos, sin dependencias abiertas— cuyo
   spec sigue en `Estado: BORRADOR` porque nadie lo ha validado todavía ⏱ **sin pasada**.
   → **Esperado:** el veredicto **no afirma que se pueda planificar**. `LISTA` significa
     *lista para el siguiente paso*, y el siguiente paso de un spec sin validar es validarlo:
     `gate_spec_fiable` va a denegar el plan ([[D-061]]), así que un informe que la dé por
     `LISTA` a secas está prometiendo algo que el gate incumple una fase más tarde.
   → **Lo que se mide es la coherencia, no el literal.** No importa si se resuelve con un
     estado distinto, con el motivo en la columna de bloqueantes o con una nota: importa que
     **el informe y el gate digan lo mismo**. El mismo invariante, visto desde el gate, es
     `CU-9.n` punto 3.
   → **FALLO:** `LISTA` sin mención del sello sobre un spec en `BORRADOR` — el usuario lee
     "puedes planificar", pide el plan, y se lo deniegan sin que nada se lo hubiera avisado.
5. Una feature con un conflicto `ALTA` abierto en su `_conflict_report.md`.
   → **Esperado:** la clasifica `BLOQUEADA` nombrando el conflicto y la otra feature.
   → **Esperado (alcance del veredicto, [[D-077]]):** ese `BLOQUEADA` es un **veredicto de
     informe**, no una denegación mecánica: ningún gate lee los `_conflict_report.md`, y
     `wf-prepare-plan` **avisa pero no para** por un conflicto abierto. El informe no debe
     dar a entender que el pipeline lo impedirá por sí solo.
   → **Por qué se deja así y no se convierte en gate.** La severidad `ALTA` la asigna un
     juicio experto, y los auditores del fan-out se contradicen sobre el mismo par por diseño
     ([[D-047]], `CU-3.f` punto 4). Un gate mecánico que leyera ese informe sería el único del
     ecosistema que se fía del veredicto de un agente, y el `ALTA` de un auditor minoritario
     bloquearía trabajo que el arbitraje ya resolvió, sin vía de cierre.

6. **Hay informes de conflicto calculados contra conjuntos distintos** ([[D-090]]/[[D-093]]) —
   la primera tanda comparó 2 specs, la segunda 5—. Se mira en la cabecera y en «Próximos pasos».
   → **Esperado:** la cabecera trae **`Vigencia de los informes de conflicto`** con uno por
     informe: `VIGENTE`, `ESTANCADO` (diciendo qué comparó y qué specs no vio) o `VIGENCIA
     DESCONOCIDA` (sin campo `Conjunto comparado`), leído del campo y no de la fecha.
   → **Esperado (un ESTANCADO produce acción, [[D-093]]):** en «Próximos pasos», un punto por los
     estancados que diga **quién cubre los pares que no vieron** —normalmente los informes
     vigentes, porque cada spec nuevo se compara contra todos— y que el documento **puede
     rehacerse cuando convenga**. Solo si aparece un par que no ha mirado nadie, la acción es
     pedir análisis, y va como prioritaria.
   → **Esperado (los IDs se citan tal cual, [[D-090]]):** ningún espacio de nombres inventado
     (`GCF-…`); informes viejos con IDs colisionados se citan `<feature>:<ID>`.
   → **FALLO:** un informe de la tanda anterior presentado como cobertura del conjunto actual;
     ESTANCADOS listados sin acción; proponer relanzar N auditores cuando la cobertura por pares
     ya está completa; o renumerar los hallazgos.

**Resultado:** PASS si para sin índice, reporta el ciclo sin abortar, marca el scope derivado,
no promete planificación sobre un spec sin validar, acota qué significa `BLOQUEADA` y clasifica la
vigencia de cada informe de conflicto con su acción ·
FALLO si fabrica el índice, aborta todo el informe por un ciclo, marca `LISTA` una feature con
scope sin consolidar o con el spec en `BORRADOR`, presenta un conflicto `ALTA` como si
fuese a bloquear el pipeline por su cuenta, o lee un informe estancado como vigente.
**Desviación → reportar:** issue citando `CU-3.o`.

## CU-3.p — Delta / gap-resolve: un cambio de producto encubierto no se integra en silencio

**Precondición:** un spec ya generado; le pasas un "requisito nuevo" (delta) o una "respuesta de
gap" (gap-resolve) que en realidad mueve alcance, exclusión o regla de negocio del PRD.
**Mecanismo:** skill `wf-spec-delta` **en el hilo principal** (Paso 4A, primer gate de
clasificación, con `AskUserQuestion` — [[D-073]]) / `wf-spec-gap-resolve` (Paso 4, en fork) →
`sdd-spec-writer`. **Las dos vías no terminan igual, y es deliberado:** una puede preguntar y
la otra no.

1. Pides añadir al spec un "requisito" que en realidad cambia el alcance del producto (`delta analyze`).
   → **Esperado:** el delegado devuelve `POSIBLE_CAMBIO_DE_PRODUCTO` y main **presenta la
     elección** con lo redefinido delante: *formalizar el cambio en el PRD primero
     (recomendado)* · *tratarlo como delta de esta feature*.
   → **Esperado si eliges formalizar:** para ahí y remite a la gobernanza de cambio de
     producto; el delta se retoma después, contra el PRD ya actualizado.
   → **Esperado si eliges tratarlo como delta:** continúa, y el informe sale con el **aviso de
     gobernanza** puesto por el agente. **Esto NO es FALLO** ([[D-073]]): es una decisión del
     usuario con el coste delante, y queda registrada como tal.
   → **FALLO:** integrar la expansión **sin presentar la elección**; o presentar solo la rama
     de parar, que es decidir por el usuario en el otro sentido.
2. Pides completar un `[INCOMPLETO]` con una "respuesta" que contradice el PRD o mueve algo MVP↔fase futura (`gap-resolve`).
   → **Esperado:** el worker corre en **fork** y no puede preguntar ([[D-002]]): **detiene**,
     devuelve el bloqueo y remite a la gobernanza de cambio de producto; no integra el cambio
     como si fuera un gap normal. Presentarlo —y ofrecer la salida— es de quien lo invocó
     ([[D-026]]).

**Resultado:** PASS si la vía de delta **presenta** el gate y honra cualquiera de sus dos
salidas, y la de gap-resolve **para y devuelve el bloqueo** en vez de decidir · FALLO si alguna
integra el cambio de producto en silencio, si el delta decide por el usuario en cualquiera de
los dos sentidos, o si el fork de gap-resolve se arroga una elección que no puede presentar.
**Desviación → reportar:** issue citando `CU-3.p`.

## CU-3.q — Gap-resolve: confirmación de `[INFERIDO]` (dos turnos, tres vías)

**Precondición:** un spec de caracterización con CAs `[INFERIDO]` sin confirmar.
**Mecanismo:** skill `wf-spec-gap-resolve` → `sdd-spec-writer`, en `context: fork` (Paso 3, caso
`[INFERIDO]`). La fuente de confirmación es **el usuario**, no un `_analysis.md` — y como un fork no
puede preguntar ([[D-002]]/[[D-045]]), el escenario tiene **dos turnos**: el subagente **para** con
veredicto `STOP_INFERIDO_SIN_CONFIRMAR` y devuelve el material; **quien lo invocó presenta las tres
vías**; las decisiones vuelven en una invocación nueva, que las aplica tal cual ([[D-068]]).

> **Esto cambió de forma.** Hasta [[D-068]] el escenario se escribía como un diálogo dentro del
> workflow. Si una pasada ve al subagente conduciendo la conversación —o diciendo que "esperará tu
> respuesta"— eso **es el FALLO**, no el PASS.

**Turno 1 — la parada**

1. Pides confirmar los `[INFERIDO]` del spec.
   → **Esperado:** el subagente **no decide ninguno**. Para y devuelve, **por cada CA**: su ID, el
     comportamiento deducido **verbatim**, su `Confirmación pendiente` y la evidencia parcial que
     tenga. El hilo principal te presenta las tres vías (una elección por CA, no un texto libre).

**Turno 2 — las tres vías, ya con el usuario**

2. Respondes **"Confirmado"**.
   → **Esperado:** elimina el marcador y actualiza `Evidencia:` a `confirmado por <usuario> el <fecha>`
     (mantiene la evidencia parcial original); no lo resuelve desde un `_analysis.md`.
3. Respondes **"Incorrecto"** con el comportamiento real.
   → **Esperado:** corrige el CA con ese comportamiento (o lo elimina si la capacidad no existe).
4. Respondes **"No lo sé"**.
   → **Esperado:** el marcador `[INFERIDO]` **se queda** y ese CA **sigue bloqueando** `wf-prepare-plan`.

5. **Por dónde vuelven las decisiones** ([[D-082]]). Mira la invocación del segundo turno en el
   transcript.
   → **Esperado:** las decisiones viajan en el argumento `--inferred`, con las tres vías como
     valores exactos (`confirmado` / `incorrecto: <texto>` / `no-lo-se`) y un CA por entrada.
     FALLO que la decisión llegue **solo** como prosa en el prompt: ahí el segundo turno se cierra
     por parecido, no por contrato, y es el caso normal —sesión nueva, otro día— el que lo rompe.
6. **Decisión parcial**, que es lo que de verdad pasa: respondes dos de los cuatro `[INFERIDO]`.
   → **Esperado:** aplica esos dos y **vuelve a devolver** los otros dos con el mismo veredicto. Los
     que no aparecen en `--inferred` **no se dan por resueltos**. FALLO cerrarlos por arrastre, y
     FALLO también inventarse una vía si el valor viene mal escrito: eso se rechaza y se pide
     reformular, no se interpreta.

**Resultado:** PASS si (a) el primer turno **para sin decidir** y entrega el material verbatim,
(b) las tres respuestas se tratan distinto y "No lo sé" mantiene el bloqueo, y (c) las decisiones
entran por `--inferred` y las omitidas siguen abiertas · FALLO si confirma un `[INFERIDO]` desde el
analysis, si lo da por resuelto sin confirmación humana, si el subagente **dicta la pregunta y da
por hecho que recibirá la respuesta** en el mismo turno, o si una decisión no nombrada se cierra
sola.
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
