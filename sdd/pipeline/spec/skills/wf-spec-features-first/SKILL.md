---
name: wf-spec-features-first
description: "Orquestador del flujo features-first: ejecuta discover sobre el PRD y lanza fast-track en paralelo por feature (todas o un subset con --features), con guardrails de gaps criticos y alcance, y cierra con conflict check y readiness."
when_to_use: "Activa en frases como 'genera specs por feature del PRD', 'flujo features-first completo', 'specs en paralelo del PRD', 'genera todas las features del PRD', 'genera specs de la fase 1', 'genera specs de estas features', 'features-first completo'."
argument-hint: "<prd_archivo.md> [--features F-001,F-002,...] [--light|--standard] [--allow-open-critical-gaps] [--allow-derived-scope-from-analysis] [--all-features] [--skip-conflict] [--skip-readiness]"
effort: high
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# Workflow: FEATURES-FIRST (Orquestador)

Este workflow pertenece a la fase Spec y **requiere un PRD o documento de requisitos previo** como entrada. Si el usuario todavía no tiene ese artefacto, remítelo a la fase PRD antes de continuar.

Tu objetivo es ejecutar el flujo features-first: identificar features de un PRD y generar un spec por cada una en paralelo. Puede operar sobre **todo el PRD** o sobre un **subset de features** (iteración / fase) cuando se proporciona `--features`. Este skill **no realiza el análisis ni la escritura por sí mismo** — orquesta otros workflow skills.

Este workflow corre en el **hilo principal** (igual que `wf-prd-create`, `wf-prd-review` y `wf-prd-change`, y **no** en `context: fork`) por dos razones ([[D-045]]): sostiene **cuatro gates** que requieren `AskUserQuestion` —readiness del PRD, gaps críticos, expansión de alcance y coste de PRD grande—, una tool que no existe dentro de un subagente; y la delegación síncrona que necesita para consumir el resultado del paso siguiente **solo se obtiene desde el hilo principal** (con fork mode activo —el default interactivo— un subagente no puede pedir el primer plano para sus propios delegados).

**Regla de oro:** Eres un orquestador. No analizas contenido, no generas specs, no tomas decisiones funcionales. Invocas skills en el orden correcto y consolidas resultados. **No hagas `Read` ni `cat` de ningún artefacto** —ni del PRD, ni del `_analysis.md`, ni del `_discovery.md`, ni de un spec, ni del `_features.md`—: lo que necesitas saber sale del script determinista o del reporte de quien delegaste ([[D-031]]/[[D-042]]). Esto vale **aunque las tools estén disponibles** — `allowed-tools` es declarativo, no una jaula ([[D-038]]), así que la restricción se sostiene por norma.

> **Dónde está la frontera con `Bash` ([[D-048]]).** La prohibición no es sobre la tool, es sobre **cargar el artefacto en tu contexto**: un `cat` y un `grep` sin límites hacen exactamente lo mismo. Lo que sí puedes hacer es una **extracción acotada**, y solo si cumple las tres:
> - **determinista** (un patrón fijo, no "a ver qué encuentro"),
> - **delimitada** (con `-c`, `-o`, o un `head` de pocas líneas — nunca `-A`/`-B` generosos),
> - **de metadatos**: IDs, veredictos, recuentos, paths. **Nunca prosa del artefacto para que la interpretes tú** — eso es analizar contenido, y es el trabajo de tu delegado.
>
> Ejemplos legítimos: `grep -nE "^### F-[0-9]{3}:" <discovery>` (los IDs del Paso 4), `sdd-analysis-gaps.py --check --json` (el recuento), el stdout de `sdd-features-index.py` (cuántas features indexó). Ejemplo que **no** lo es: `grep -A 12 "CRÍTICO" <analysis>` o `cat <_features.md>` — traen el contenido, y encima cuando el informe del delegado ya te lo había dado.
>
> **Recortar no convierte prosa en metadato.** El criterio es **qué** extraes, no cuánto.
> Un `grep` de campos redactados —`Pregunta para el cliente`, `Asunción por defecto`,
> `Contexto`, `Respuesta`— sigue siendo prosa aunque lo pases por `cut -c1-400` o por un
> `head`: te llevas nueve párrafos de contenido a tu contexto para interpretarlos tú, que es
> justo el trabajo de tu delegado. Los recortes acotan **volumen**; la frontera es de
> **naturaleza**. Si lo que sacas hay que *leerlo* para entenderlo, no es metadato.
>
> **Y el recuento no se hace dos veces.** Si vas a preguntarle al script, pregúntale
> **primero**: contar marcadores a mano antes es trabajo tirado y, peor, te deja en contexto
> un número que compite con el bueno. Medido: un `grep -oE '\[CRÍTICO\]'` sobre un análisis
> devolvió **10** —contando la leyenda y la tabla de marcadores— donde el script decía **4**.

> **Cómo delegas — un solo mecanismo, y el resultado se recibe, no se deduce ([[D-043]], corregida
> por [[D-045]] y [[D-047]]).** Los cinco puntos de delegación de este workflow (analyze, discover,
> fast-track, conflict, readiness) se invocan **siempre** con la tool `Agent`, pasando el
> `subagent_type` que se indica en cada paso, y **no** con el `Skill` tool (no paraleliza y no
> devuelve un handle síncrono).
>
> **El primer plano lo permite el proyecto, no lo negocias tú ([[D-050]]).** El `settings.json`
> declara `CLAUDE_CODE_FORK_SUBAGENT=0`, y eso es lo que hace que `run_in_background: false`
> surta efecto: con fork mode activo el harness ni siquiera evalúa la petición. Tú solo pasas el
> flag. Si aun así la delegación vuelve como asíncrona, **no cambies de mecanismo ni hagas el
> trabajo tú**: espera la notificación de fin (vía (b), abajo) y sigue.
>
> **Qué es haber esperado ([[D-047]]).** Has esperado cuando **el texto del informe del delegado
> está en tu contexto**, y ha llegado por una de estas **dos** vías:
> - **(a) El `tool_result` de tu llamada `Agent`**, porque la hiciste con `run_in_background: false`.
> - **(b) La notificación de fin de ese agente**, si el harness lo lanzó en segundo plano: cedes el
>   turno sin hacer nada más y el informe te llega en un turno posterior.
>
> Las dos son legítimas: en ambas el informe **te lo entregan**. Lo que separa esperar de deducir no
> es en qué turno llega, es **quién lo trae**.
>
> **Lo que no es esperar** — da igual lo convincente que parezca: que el fichero exista, que su
> tamaño deje de cambiar, que un script te dé un veredicto sobre él, o que **tú vayas a leer** el
> `.output`, el log o cualquier otro buzón del entorno donde el harness escribe el progreso. Eso es
> ir a buscar el dato, y ese dato no es el informe: es tu reconstrucción de él.
>
> **Mientras esperas, no adelantes trabajo que dependa del resultado.** Ni sondear, ni "ir haciendo"
> el paso siguiente, ni relanzar un segundo delegado sobre lo mismo (eso no es esperar: es un race
> de doble escritura sobre el mismo artefacto).
>
> **Si no tienes el informe, para.** No continúes y **no reconstruyas**: di que la delegación no
> devolvió resultado y detente. En particular, **nunca presentes como dicho por el delegado un dato
> que has obtenido tú por tu cuenta** — un path, un veredicto o un recuento sacados del disco
> suben con la misma apariencia de verdad que los del informe, y ahí es donde el error deja de
> notarse.
>
> **No afirmes limitaciones del entorno que no has comprobado.** Si una tool rechaza un parámetro,
> la evidencia es su error de validación; sin ese error, no se afirma. Justificar un atajo con una
> limitación supuesta convierte una decisión tuya en un hecho del harness.
>
> **El delegado ejecuta la skill, no la re-despacha ([[D-044]]).** El prompt le dice que **lea el
> `SKILL.md` y ejecute sus pasos él mismo**, y le **prohíbe** usar el `Skill` tool. El motivo es
> estructural: las sub-skills llevan `context: fork`, así que invocarlas con `Skill` **forkea otro
> subagente** — y como su `agent:` es el mismo que acabas de lanzar, ese fork es un **clon** del
> delegado. Medido en CU-3.a pasada 2: el envoltorio intermedio costó **~210 KB por delegación**
> (casi tanto como el que hacía el trabajo, porque recibe su reporte entero y lo re-emite), y ese
> salto extra vuelve a ser **asíncrono**. En el fan-out del Paso 5 esto se multiplica por feature.

> **Cómo presentas un gate ([[D-045]]).** Los cuatro gates de este workflow (Pasos 2, 2.5, 2.5 de
> alcance y 4a.1) se presentan **en el momento, con `AskUserQuestion`**, y el flujo **continúa en el
> mismo turno** con lo que el usuario elija. No le digas "vuelve a ejecutar añadiendo `--allow-…`":
> re-invocar el workflow entero repite los pasos ya hechos (parseo, readiness, check de gaps) y
> pierde el contexto de la parada.
>
> Lo que **no** cambia ([[D-026]]): **tú nunca armas un `--allow-*` por tu cuenta** ni lo infieres de
> una petición impaciente. Son escotillas de seguridad, y quien las abre es el usuario **eligiendo
> explícitamente** en el gate. Los flags siguen siendo válidos si vienen **de entrada** en
> `$ARGUMENTS`: en ese caso el gate correspondiente ya está decidido y no se presenta — deja
> constancia y sigue.
>
> Antes de la pregunta, da en el texto los datos que hacen falta para decidir (paths, veredicto,
> IDs, recuentos), sacados del script o del reporte del delegado. La pregunta no sustituye a la
> información: la acompaña.

**Sobre el flujo iterativo por subset:** las "fases" o "iteraciones" no se definen en el PRD ni en el discovery — son una decisión humana de delivery sobre qué features procesar en cada pasada. El usuario decide el subset **después** de ver el discovery; cada ejecución con `--features` actualiza `_features.md` de forma incremental, sin borrar las features ya generadas en pasadas anteriores ni las pendientes para futuras.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del PRD**: el primer argumento
- **Flags opcionales**: `--features F-001,...` (IDs a procesar, requiere discovery previo); `--light`/`--standard` (modo del pipeline — se propaga a cada fast-track; sin flag rige `pipeline_mode` de `.sdd/project-init.json`); `--allow-open-critical-gaps` (genera con gaps críticos abiertos → HUs `[INCOMPLETO]`); `--allow-derived-scope-from-analysis` (continúa aunque el analysis expanda el PRD); `--allow-unreviewed-prd` (continúa aunque el PRD tenga `[ASUNCIÓN]` sin confirmar / sin sellar → alcance no-revisado); `--all-features` (full-run override para PRDs grandes); `--skip-conflict`/`--skip-readiness` (omitir checks finales).

Si no hay argumento, informa el uso con todos los flags opcionales y ejemplos de los modos principales: completo sin flags, subset con `--features`, con `--allow-open-critical-gaps`, con `--allow-derived-scope-from-analysis`.

---

## Paso 2: Verificar el archivo y la readiness del PRD

Verifica que el archivo PRD existe; si no → informa con ruta exacta y detén.

**Gate de readiness PRD→spec ([[D-020]]).** Un PRD con `[ASUNCIÓN]` sin confirmar hornearía inferencias no validadas en los specs. Compruébalo mecánicamente (no a ojo ni por topología):
```
!python3 .sdd/scripts/sdd-prd-ready.py "<prd.md>"
```
- Veredicto `READY` → continúa.
- `OPEN_ASSUMPTIONS` o `ASSUMPTION_MISMATCH`, y **no** se pasó `--allow-unreviewed-prd` → **presenta el gate**: informa del veredicto y del detalle que dio el script, y pregunta con `AskUserQuestion`:
  - *Revisar el PRD primero* (recomendada) — el flujo se detiene aquí; el usuario **cierra las asunciones revisando el PRD** y vuelve cuando esté sellado.
  - *Continuar sobre un PRD no-revisado* — equivale a `--allow-unreviewed-prd`: sigues al Paso 2.5 dejando constancia explícita de que los derivados se generan sobre alcance **no-revisado**.
- `UNSEALED` → **advisory**: avisa ("el PRD no está sellado; conviene cerrar la aprobación antes de derivar specs — dime si quieres que lo revisemos primero") y continúa.
- Con `--allow-unreviewed-prd` de entrada sobre un veredicto bloqueante → no presentes el gate; continúa dejando constancia explícita de que los derivados se generan sobre un PRD **no-revisado**.
- Si falta el script (`.sdd/scripts/sdd-prd-ready.py` no existe) → avisa (reinstala el ecosistema con `install.sh`) y continúa (conservador: no bloquees por falta de tooling).

---

## Paso 2.5: Análisis de gaps (obligatorio)

1. Busca si existe un `*_analysis.md` para este PRD (convención: `<basename>_analysis.md`). Búscalo en el directorio de artefactos prd (`artifacts.prd` de `.sdd/project-init.json`, si está declarado) y en el mismo directorio del PRD.
2. **Si NO existe** → genera el análisis delegando con la tool `Agent` ([[D-043]]), y **espera su resultado**:
   ```
   Agent(
     subagent_type: "sdd-spec-explorer",
     run_in_background: false,
     prompt: "Lee `.claude/skills/wf-spec-analyze/SKILL.md` y ejecuta sus pasos TÚ MISMO sobre estos argumentos: <prd.md>. NO uses el `Skill` tool: ya eres el agente al que esa skill delega (`agent: sdd-spec-explorer`), así que invocarla te forkearía en un clon tuyo. Dentro de ese SKILL.md, las rutas que empiecen por la variable de directorio de skill (`CLAUDE_SKILL_DIR`) se resuelven contra `.claude/skills/wf-spec-analyze/`. Al terminar, informa del path exacto del `_analysis.md` generado, su veredicto y el nº de gaps por severidad."
   )
   ```
   El path del `_analysis.md` lo tomas **del informe del delegado**, no buscándolo en el disco. Marca este análisis como **recién generado**: el usuario aún no lo ha visto, así que el gate del punto 6 se presenta igualmente aunque el script no reporte críticos abiertos (con la opción de revisarlo antes de generar specs).
3. **Estado mecánico de los gaps — antes de decidir nada** ([[D-042]]):
   ```
   !python3 .sdd/scripts/sdd-analysis-gaps.py "<path>_analysis.md" --check --json
   ```
   Da `verdict` (`CRITICAL_OPEN` / `CRITICAL_ANSWERED` / `VACUOUS`), `critical_open` y `critical_open_ids`. **Este conteo no se hace leyendo el informe**: contar marcadores `_(pendiente)_` no es juicio, y de él cuelgan las dos ramas duras de los puntos 5 y 6. Si el veredicto es `VACUOUS`, el documento no se ha podido parsear — **detente** y dilo, no lo trates como "sin gaps".
4. **Si existe** → **no lo leas.** Lo que necesitas sale del script y de una extracción acotada de metadatos, nunca de abrir el artefacto ([[D-051]]):
   - **Estado de cada gap** —IDs, severidad, **flags**, título y si está respondido—:
     ```bash
     !python3 .sdd/scripts/sdd-analysis-gaps.py "<path>_analysis.md" --list --json
     ```
   - **Veredicto del análisis**:
     ```bash
     !grep -oE 'LISTO_PARA_SPECS_CON_PREGUNTAS|LISTO_PARA_SPECS|REQUIERE_LIMPIEZA_PRD' "<path>_analysis.md" | head -1
     ```

   > **El detalle de un gap se pide cuando hace falta, y de uno en uno ([[D-053]]).** `--list`
   > emite además `contexto`, `problema` y `afecta`, pero **no los traigas todos ahora**: con 7
   > gaps eso te mete media prosa del informe en contexto por la puerta de atrás, que es
   > exactamente lo que la Regla de oro evita. Se piden con `--gap <P-XXX>` **solo en la rama de
   > dictar** (punto 6b), gap a gap. Y si el usuario elige escribir él en el fichero o continuar
   > aceptando el riesgo, **no se piden nunca**: el gate no los necesita.

   > **Por qué esto era un agujero, y no un detalle ([[D-051]]).** El texto anterior te pedía
   > *"léelo para lo que sí es juicio… y si las respuestas ya escritas introducen expansión
   > funcional"*, en contradicción directa con la Regla de oro de este mismo SKILL. No se notó
   > porque en el caso habitual las respuestas te las **dicta el usuario** en la conversación y
   > ya las tienes en contexto. Pero el caso normal de verdad es el otro: los gaps se responden
   > un martes y se sigue el jueves, en **sesión nueva**. Ahí no tienes el texto de ninguna
   > respuesta, y la única forma de "inspeccionarlas" sería abrir el fichero.
   >
   > **Tú no juzgas respuestas: enrutas por el flag y delegas el juicio** (punto 8). El
   > `PUEDE_REQUERIR_CR` que viene en `flags` es exactamente el disparador que necesitas, y lo
   > puso el analyze precisamente para esto. Mismo reparto que [[D-031]]: citas el veredicto
   > mecánico y la lectura la hace quien tiene el documento delante.
5. Si el veredicto del análisis es `REQUIERE_LIMPIEZA_PRD` → **DETENERSE** e informar al usuario:
   > "El análisis previo marca `REQUIERE_LIMPIEZA_PRD`. Corrige la contaminación técnica del PRD antes de continuar y vuelve a ejecutar el flujo."
6. Si el script dio `CRITICAL_OPEN` y **no** se pasó `--allow-open-critical-gaps` de entrada, o si el análisis está **recién generado** (punto 2) → **presenta el gate**.

   **La decisión se pregunta UNA VEZ, para toda la tanda ([[D-053]]).** Antes de preguntar, di:
   el **path exacto** del `_analysis.md`, cuántos `[CRÍTICO]` hay abiertos, y **sus IDs con el
   título en una línea cada uno** (de `--list`, punto 4 — no abras el fichero). Eso le deja ver
   el alcance de lo que se le pide **antes** de elegir cómo responderlo.

   Después, **un solo `AskUserQuestion`** con tres opciones en un eje —cómo se responde—:
   - *Me los dictas aquí* (recomendada) — te los presento uno a uno con su contexto y los vas
     respondiendo en el chat; cada respuesta la aplicas con el script y el `_analysis.md` cambia
     **solo** en esa línea. Puede cerrar solo los que tenga claros.
   - *Los escribes tú en el fichero* — el flujo se detiene aquí. Le das el path y qué se
     sustituye (`- **Respuesta**: _(pendiente)_`), y se retoma cuando estén cerrados.
   - *Continuar aceptando el riesgo* — equivale a `--allow-open-critical-gaps`: sigues al Paso 3
     dejando constancia explícita de que las HUs afectadas podrán salir `[INCOMPLETO]` y
     quedarán bloqueadas para plan/tasks hasta completarse.

   > **Una decisión, una pregunta ([[D-053]]).** Antes esto se preguntaba **una vez por gap**, y
   > el propio menú lo delataba: la tercera opción tenía que aclarar *"(aplica a los 4 gaps
   > críticos, no solo este)"* — una opción de ámbito global metida dentro de una pregunta de
   > ámbito individual. Si una opción necesita explicar que no va con su propia pregunta, la
   > pregunta está en el sitio equivocado. Además obliga a decidir cuatro veces lo mismo antes de
   > poder responder nada.
   >
   > Y hay un ahorro real: si elige escribir él en el fichero o continuar aceptando el riesgo,
   > **el detalle de los gaps no hace falta para nada** — y el gate se arma solo con el recuento
   > de `--check`, que ya tienes.

   Si el análisis estaba recién generado pero el script **no** reporta críticos abiertos, el gate se reduce a dos vías: *revisar el análisis antes de generar* o *continuar ya*. En cualquiera de las dos, **pasa igualmente por el punto 6c**: que no haya críticos no significa que no haya decisiones tomándose solas.

6b. **Solo si eligió dictar** → presenta los gaps **en la conversación, de uno en uno**. Para cada `[CRÍTICO]` abierto, en orden:

   ```bash
   !python3 .sdd/scripts/sdd-analysis-gaps.py "<path>_analysis.md" --list --gap <P-XXX> --json
   ```

   Escribe en el chat, **verbatim**, lo que devuelve: el ID y su título, el `contexto`, el
   `problema`, el `afecta` y la **pregunta** literal. Si sus `flags` incluyen
   `PUEDE_REQUERIR_CR`, añade **una línea** avisando de que la respuesta puede expandir el
   producto y que entonces habrá que formalizarlo en el PRD (punto 8). Luego **cede el turno**:
   el usuario responde en texto libre.

   Con su respuesta, y solo con ella:
   ```bash
   !python3 .sdd/scripts/sdd-analysis-gaps.py "<path>_analysis.md" --answer <P-XXX> "<lo que dijo, literal>"
   ```

   **Literal incluye la ortografía.** No añadas tildes, no cierres con punto, no reordenes. Medido
   (pasada 11): *"Si,"* se aplicó como *"Sí,"* y a dos respuestas se les añadió punto final. No
   inventó nada y no es un fallo — pero *"corregir la tilde"* y *"mejorar la frase"* son el mismo
   gesto con distinto tamaño, y la línea que los separa no la puedes trazar tú a mitad de un
   dictado. Si algo del texto te parece un error que importa, **pregunta**; no lo arregles al
   pasarlo.
   Confirma en una línea que se aplicó y pasa al siguiente. Cuando no queden críticos, vuelve a
   correr `--check` y **sigue por el punto 6c**. Si cierra solo algunos y quiere parar, `--check`
   reevalúa el gate con los que queden — no hace falta anunciarlo como rama.

   > **Por qué en el chat y no con `AskUserQuestion` ([[D-053]]).** `AskUserQuestion` es para
   > **elegir entre opciones**. La respuesta a un gap es **prosa abierta**: no hay opciones, así
   > que el camino principal acababa siendo la escotilla *"Other → escribe algo"* del selector.
   > Y el coste no era solo de fricción: **la pantalla del selector no tiene sitio para el
   > `contexto` ni el `problema`**, que son justo los campos que dicen *por qué* importa y
   > *cuánto* detalle hace falta. Medido: al usuario le llegaba la pregunta pelada y los dos
   > campos se tiraban. Una pregunta amputada se contesta peor, que es contra lo que se
   > construyó [[D-042]].
   >
   > **Y de uno en uno por atribución, no por comodidad.** Si presentas los cuatro juntos y te
   > responde en un bloque, tienes que **repartir** su texto entre cuatro IDs — y eso es
   > interpretar una respuesta que no dio literalmente, que es el FALLO del paso 4 de `CU-3.a`.
   > Gap a gap, la atribución es inequívoca por construcción. **Nunca compones, completas ni
   > reinterpretas una respuesta**: si lo que dijo no responde a lo que se preguntaba, se lo
   > dices y le dejas reformular.

6c. **Cuando ya no quedan críticos abiertos, ofrece repasar los informativos** ([[D-057]]).
   Un `[INFORMATIVO]` sin responder **no se queda sin decidir**: se aplica su asunción por defecto
   y esa asunción entra en los CAs del spec. Es la opción conservadora, así que no expande el
   producto — pero es una decisión tomada en nombre de alguien que quizá no sabe que existe.

   Del `--check --json` que ya tienes sale `informative_open` con sus IDs. Si es **0**, sigue. Si
   no, pide sus asunciones —una llamada, todos los IDs no hace falta uno a uno— y **escríbelas en
   una línea cada una** antes de preguntar:

   ```bash
   !python3 .sdd/scripts/sdd-analysis-gaps.py "<path>_analysis.md" --list --json
   ```

   `P-004 — Periodicidad del presupuesto → se asumirá: mes natural, del 1 al último día.`

   Y entonces **una sola pregunta** con dos vías: *repasarlos ahora* / *aplicar esas asunciones y
   seguir*. Una pregunta para toda la tanda, igual que en el punto 6 y por el mismo motivo.

   **Los que lleven `PUEDE_REQUERIR_CR` se enseñan siempre**, aunque elija seguir: ese flag declara
   que la respuesta **podría mover el producto**, así que su línea lleva el `⚠` y dice que, si la
   respuesta fuera otra, habría que formalizarlo en el PRD. No preguntar nunca equivale a garantizar
   que esa vía de gobernanza no se recorre.

   **Si elige repasarlos** → mismo formato conversacional que 6b, uno a uno, con el `contexto` y la
   `asuncion` **verbatim** del script. Dos salidas por gap:
   - **la asunción le vale** → se aplica con `--answer` **escribiendo el texto de la asunción**.
     `_(pendiente)_` significa *nadie lo ha mirado*; una respuesta significa *alguien lo decidió*, y
     aguas abajo no son lo mismo.
   - **quiere otra cosa** → `--answer` con lo que diga, literal. Si eso introduce capacidad nueva,
     sigues por el punto 8 como con cualquier otra respuesta expansiva.

   **Si elige seguir** → no insistas: las asunciones se aplican solas, que es el comportamiento
   documentado. Ya se lo has enseñado, que era lo que faltaba.

   Salgas por donde salgas, **desde aquí se va al punto 8 o al 9** según el veredicto de `--check`.
   Ojo a la costura: si respondió un informativo que llevaba `PUEDE_REQUERIR_CR`, ese gap **ya
   cuenta** para el punto 8 —su condición es *"lo lleva y está respondido"*, sin mirar la
   severidad—, así que la evaluación de gobernanza le aplica igual que a un crítico.

7. Si el script dio `CRITICAL_OPEN` y `--allow-open-critical-gaps` vino **de entrada** en `$ARGUMENTS` → no presentes el gate; continúa al Paso 3 dejando constancia explícita de que las HUs afectadas podrán salir `[INCOMPLETO]`.
8. Si el script dio `CRITICAL_ANSWERED`, hay que saber si alguna respuesta introduce señales de cambio de producto según `kb-product-change-governance`. **Tú no las lees ([[D-051]]):** mira los `flags` que devolvió `--list --json` y **delega el juicio**.

   - **Si ningún gap respondido lleva `PUEDE_REQUERIR_CR`** → no hay disparador. Continúa al Paso 3.
   - **Si alguno lo lleva y está respondido** → delega la evaluación al agente que **sí** tiene el PRD y el análisis delante, y espera su veredicto:
     ```
     Agent(
       subagent_type: "sdd-spec-explorer",
       run_in_background: false,
       prompt: "Los gaps de <path>_analysis.md están respondidos (`--check` da CRITICAL_ANSWERED). Los siguientes llevan el flag `[PUEDE_REQUERIR_CR]`: <IDs>. Relee sus respuestas y evalúa con `kb-product-change-governance` si alguna introduce señal de cambio de producto —entidad persistente nueva, catálogo reutilizable, nueva granularidad funcional, modelo owner nuevo o flujo no comprometido en el PRD—. Contrasta cada respuesta con lo que el PRD comprometía de verdad, citando su texto. Informa: veredicto (SIN_SEÑALES | CON_SEÑALES), y por cada señal el ID del gap, qué introduce y con qué línea del PRD choca."
     )
     ```
     El flag lo puso el analyze **precisamente para esto**: marca los gaps cuya futura respuesta era de riesgo, así que es el índice de qué hay que reevaluar y evita releerlo todo.
   - **Si su veredicto es `CON_SEÑALES`** y **NO** vino `--allow-derived-scope-from-analysis` de entrada → **presenta el gate**. Di qué respuesta concreta introduce qué señal —**citando el informe del delegado, no tu lectura**— y pregunta con `AskUserQuestion`:
     - *Formalizar el cambio en el PRD* (recomendada) — el flujo se detiene; **el cambio se formaliza primero en el PRD** y los derivados se generan después, sobre PRD limpio.
     - *Continuar con alcance derivado* — equivale a `--allow-derived-scope-from-analysis`: sigues dejando constancia de que el discovery, `_features.md` y los specs marcarán ese alcance como **scope derivado** y no como PRD puro.
   - si `--allow-derived-scope-from-analysis` vino **de entrada** → no presentes el gate; continúa dejando constancia explícita de que el discovery, `_features.md` y los specs deberán marcar ese alcance como **scope derivado** y no como PRD puro.
9. Si el script dio `CRITICAL_ANSWERED` y no se detectan señales de cambio → continuar al Paso 3 usando el `_analysis.md` como contexto.

**Importante:** `[INFORMATIVO]` nunca bloquea (el script los reporta aparte: cada uno aplicará su asunción por defecto) — **pero no bloquear no es no enseñar**: se repasan en el punto 6c, porque esa asunción es una decisión de producto que se toma sola ([[D-057]]); `[CRÍTICO]` abiertos requieren `--allow-open-critical-gaps`. Para señales de expansión consulta `kb-product-change-governance`. Si el PRD cambió después de generar specs previos, puede ser necesario `wf-prd-sync-impact` antes de mezclar pasadas.

> **Las respuestas de los gaps no las escribes tú** ([[D-042]]; tabla de ámbito en `kb-gap-conventions`). Las escribe el usuario en el `_analysis.md`; si te las dicta, las aplicas con `sdd-analysis-gaps.py --answer P-XXX "texto"`. Nunca edites el informe a mano ni completes una respuesta que el usuario no ha dado.

---

## Paso 3: Ejecutar discover (o reutilizarlo)

**Caso A — `--features` está presente**:
El `_discovery.md` **debe existir previamente** (los IDs `F-XXX` solo tienen sentido contra un discovery existente). Busca `<basename>_discovery.md` en el directorio de artefactos prd (`artifacts.prd` de `.sdd/project-init.json`, si está declarado) y en el mismo directorio del PRD.
- Si existe → continúa al Paso 4 reutilizándolo.
- Si NO existe → **detente** e informa al usuario:
  > "Has indicado features concretas, pero todavía no existe `<path>_discovery.md`. Las features no están en el PRD: se identifican descubriéndolas. Déjame descubrirlas primero, revisas el mapa, y me dices qué IDs quieres de esa lista."

**Caso B — `--features` no está presente**:

**Mira primero si ya existe**, con la misma búsqueda del Caso A ([[D-081]]). Un `_discovery.md` en
disco **se reutiliza**, no se regenera: los `F-00X` son la trazabilidad que los specs ya citan en su
cabecera, y volver a descubrir puede renumerarlos. Si existe → continúa al Paso 4 reutilizándolo, y
dilo en el informe ("reutilizo el mapa de features que ya había"). Si no existe → delégalo.

> **Por qué esto estaba mal, y era invisible ([[D-081]]).** Este caso delegaba el discovery
> **siempre**, y el worker se detiene por sí mismo cuando el artefacto existe — con razón, es su
> trabajo. Pero el único camino que su bloqueo nombra es regenerarlo pisando lo anterior, que es
> justo el peligroso, mientras que la salida correcta —reutilizar— solo estaba escrita en el Caso A,
> detrás de `--features`. Un usuario que primero pregunta *"¿qué features tiene este PRD?"* y luego
> dice *"vale, genéralas"* llegaba aquí por la puerta sin salida buena.

Delega el discovery con la tool `Agent` ([[D-043]]):
```
Agent(
  subagent_type: "sdd-spec-explorer",
  run_in_background: false,
  prompt: "Lee `.claude/skills/wf-spec-discover/SKILL.md` y ejecuta sus pasos TÚ MISMO sobre estos argumentos: <prd.md> [--analysis <analysis.md>] [--allow-derived-scope-from-analysis si aplica]. NO uses el `Skill` tool: ya eres el agente al que esa skill delega (`agent: sdd-spec-explorer`), así que invocarla te forkearía en un clon tuyo. Dentro de ese SKILL.md, las rutas que empiecen por la variable de directorio de skill (`CLAUDE_SKILL_DIR`) se resuelven contra `.claude/skills/wf-spec-discover/`. Al terminar, informa del path exacto del `_discovery.md`, la lista de features (ID + nombre + actor), los shared models y si te detuviste por ambigüedad."
)
```
Espera su resultado (el de la tool, no el del disco) y obtén de él el path del `_discovery.md`.

**Si volvió con un `STOP_*` en vez de con el discovery, no lo interpretes: preséntalo** ([[D-026]]/[[D-081]]). Son dos, y no se resuelven igual:
- **`STOP_OWNERSHIP_AMBIGUO`** (shared models con dueño empatado) → transmite la tabla que te dio y **espera la decisión del usuario**; sin ella no hay discovery que reutilizar.
- **`STOP_ARTEFACTO_EXISTE`** → no debería ocurrir si hiciste la comprobación de arriba, y si ocurre es que el worker resolvió otro path que tú. **No lo relances con `--allow-overwrite-discovery` por tu cuenta**: regenerar renumera los `F-00X`. Di qué path encontró él, y pregunta con `AskUserQuestion` si reutilizar ese mapa (recomendada) o regenerarlo asumiendo la renumeración.

---

## Paso 4: Determinar el subset a procesar

Necesitas la lista de features (ID + nombre kebab-case) y su total `N_total`. **No hagas `Read` del `_discovery.md`** (Regla de oro):
- **Discovery recién generado** (Caso B cuando no existía) → la lista viene en el **informe del delegado**, que la reporta explícitamente.
- **Discovery reutilizado** (Caso A, y Caso B cuando ya existía) → extráela con una consulta **acotada** por `Bash`, no cargando el documento:
  ```
  !grep -nE "^### F-[0-9]{3}:" "<path>_discovery.md"
  ```
  Una extracción determinista y delimitada no es "leer el artefacto": lo que la Regla de oro prohíbe es traerte el contenido para opinar sobre él.

### 4a — Determinar el subset

- **Si NO hay `--features`**: el subset a procesar = todas las features del discovery.
- **Si hay `--features F-001,F-002,...`**:
  1. Valida que **todos** los IDs solicitados existen en el discovery.
  2. Si alguno no existe → **detén** con mensaje claro: "Los siguientes IDs no aparecen en `<path>_discovery.md`: [lista]. IDs válidos: [lista del discovery]."
  3. El subset = solo las features cuyos IDs aparecen en `--features`.
- **Features NO incluidas en el subset** (caso `--features`): se registrarán en `_features.md` con estado `PENDIENTE_GENERACIÓN` y no se les lanza fast-track en esta ejecución.

### 4a.1 — Guardrail de coste para PRDs grandes

Si no hay `--features` y el discovery contiene >5 features, y **no** vino `--all-features` de entrada → **presenta el gate**. Muestra el mapa de features (ID, nombre, actor, RFs) tal como te lo reportó el delegado, di cuántas son, y pregunta con `AskUserQuestion` qué alcance quiere en esta pasada:
- *Un subset de features* — el usuario nombra los IDs; equivale a `--features F-001,...`. Las no incluidas quedan `PENDIENTE_GENERACIÓN` y se generan en pasadas posteriores sin perder lo anterior. **No elijas tú el subset**: puedes agrupar por dependencia o por gaps abiertos para ayudar a decidir, pero la selección es del usuario.
- *Todas de una pasada* — equivale a `--all-features`.

Si hay gaps `[CRÍTICO]` abiertos, dilo aquí también: indica qué features quedarían con HUs `[INCOMPLETO]`, porque cambia la decisión de alcance. Con `--all-features` o `--features` **de entrada** → no presentes el gate; continúa.

### 4b — Clasificar specs preexistentes (ponderado por riesgo, [[D-024]])

Un spec que ya existe **no se pisa en silencio, pero tampoco se salta en silencio**. Lo que decide
no es "existe / no existe" sino **cuánto trabajo hay que perder**, y desde [[D-061]] esa línea es
objetiva: el campo `Estado:` de la cabecera del spec. Se lee **entero**, con sus tres valores
([[D-080]]): un `RETIRADO` leído como "no está validado" cae en la clase que se regenera.

Clasifica **todas** las features del subset de una vez (una sola llamada, no una por feature):

```bash
!for f in <capabilities del subset, separadas por espacio>; do
  p=$(python3 .sdd/scripts/sdd-resolve-path.py find spec "<raíz_spec>/features/$f/spec/${f}_spec.md" 2>/dev/null)
  if [ -z "$p" ]; then echo "$f NO_EXISTE"; continue; fi
  e=$(sed -nE 's/^[[:space:]]*[-*>]?[[:space:]]*\*{0,2}Estado:?\*{0,2}[[:space:]]*:?[[:space:]]*(BORRADOR|VALIDADO|RETIRADO).*/\1/p' "$p" | head -1)
  case "$e" in
    RETIRADO) echo "$f RETIRADA $p" ;;
    VALIDADO) echo "$f SELLADO $p" ;;
    *)        echo "$f DRAFT $p" ;;
  esac
done
```

> Esto **no** es leer el artefacto: es una extracción acotada de **un** campo de metadatos, la misma
> vía sancionada que usas en el Paso 3 para el `_analysis.md` ([[D-051]]). No hagas `Read` ni `cat`
> del spec para verlo "en contexto".

Actúa por clase. **Los gates de abajo son uno solo cada uno**, con la lista de features dentro:
preguntar feature a feature por un lote de nueve es justo el *nagging* que [[D-024]] existe para
evitar.

- **`NO_EXISTE`** → van al fast-track (Paso 5), como siempre.

- **`RETIRADA`** → **fuera del fast-track, y no hay gate que ofrecer** ([[D-078]]/[[D-080]]). Esa
  feature la sacó del producto un cambio formalizado con su `CR-XXX`; regenerarle el spec la
  devolvería viva sin `CR`, sin el gate de impacto y sin que nadie lo vea. **Pero no la saltes en
  silencio**: nómbrala en el informe del Paso 9, con su traza `Retirada:`, y di que si el producto
  la recupera eso se decide aparte —y la deja en borrador, pendiente de validar otra vez—. No
  preguntes aquí si regenerarla: la pregunta insinúa una salida que no existe.

  > **Por qué sigue apareciendo en el subset.** El `_discovery.md` **no se regenera** (lo protege su
  > propio bloqueo: renumerar los `F-00X` rompería la trazabilidad de los specs que ya los citan),
  > así que sigue listando el `F-00X` de una feature dada de baja — y su ID **se conserva sin
  > reutilizarse** (`kb-traceability-rules` Regla 12). Que llegue hasta aquí es lo normal, no una
  > anomalía del proyecto.

- **`SELLADO`** → **siempre** confirma, y el mensaje **avisa del descarte**, con independencia de lo
  explícito que fuera la petición. Un solo `AskUserQuestion` **nombrando las features selladas**:
  > "Estas features ya tienen un spec **validado**: `<lista>`. Regenerarlas **descarta el trabajo de
  > validación** (y los gaps ya respondidos en ellas). ¿Qué hago?"
  - **Conservarlas (recomendado)** → quedan fuera del fast-track; se reportan como "ya generada
    (sellada)".
  - **Regenerarlas** → entran al fast-track **con `--allow-overwrite-sealed-spec`**. Ese flag lo
    arma el usuario **eligiendo aquí**; nunca lo pongas por tu cuenta ([[D-026]]).

- **`DRAFT`** → depende de lo que pidió el usuario, no del fichero:
  - **Intención explícita de regenerar** esas features ("regenera el spec de F-003", "rehaz las
    specs de la fase 1", "vuelve a generarlas") → entran al fast-track **sin re-preguntar**: el
    consentimiento ya está dado.
  - **Petición ambigua** (p. ej. "genera las specs del PRD" y resulta que algunas ya tienen draft;
    el usuario puede no saberlo) → **gate ligero**, un solo `AskUserQuestion` con la lista:
    > "Estas features ya tienen un spec en borrador: `<lista>`. ¿Las regenero (se sobreescriben) o
    > las conservo?"
    - **Conservar (recomendado)** → fuera del fast-track, se reportan como "ya generada".
    - **Regenerar** → entran al fast-track (no hace falta flag: un draft no está sellado).

Informa al usuario: N_total totales, N_subset a procesar, N_a_generar nuevas, N_conservadas
(distinguiendo selladas de draft), **N_retiradas** (nombrándolas) y N_pendientes futuras.

> **Por qué esto cambió** (ver `DECISIONS.md` [[D-062]]): antes este paso **excluía del fast-track
> cualquier spec preexistente**, sellado o borrador, sin preguntar. Preservar trabajo es el default
> correcto, pero tomarlo en silencio convierte un "regenérame F-003, he cambiado el PRD" en un
> **no-op reportado como éxito** ("ya generada"). El gate no vale por interrumpir: vale por la
> información que carga.

---

## Paso 5: Lanzar fast-track en paralelo (solo features a generar)

Lanza fast-track únicamente para las features que el Paso 4b dejó **a generar**: las `NO_EXISTE`, más las preexistentes que el usuario decidió regenerar en sus gates. Las que decidió conservar se preservan tal cual; las que están fuera del subset no se tocan.

### 5.0 — Reparte los rangos de ID de gap **antes** de lanzar ([[D-056]])

Cada escritor puede levantar gaps propios en su spec y ninguno ve a sus hermanos: van en paralelo y
sus ficheros aún no existen en disco. Si cada uno pide el siguiente ID libre, **todos obtienen el
mismo**. Tú eres el único punto que los ve a la vez, así que el reparto es tuyo.

Pide el primer ID libre del linaje —el análisis más los specs que ya existan— y reparte bloques de
**10** en el orden en que vas a lanzar:

```bash
!python3 .sdd/scripts/sdd-next-id.py P <analysis.md, si hay> <specs existentes…>
```

Si devuelve `P-008`, el primer escritor arranca en **`P-011`** (redondea hacia arriba a la decena
siguiente, para que los bloques se lean de un vistazo), el segundo en `P-021`, el tercero en
`P-031`, y así. Cada uno recibe su arranque en `--gap-id-start`.

**Los huecos entre bloques son deliberados** y la SSoT los sanciona: un ID sin usar no cuesta nada,
dos gaps distintos con el mismo ID corrompen la trazabilidad. Sin análisis en el linaje, el primer
bloque empieza en `P-001`.

> **Medido (pasada 11 de CU-3.a).** Con 4 escritores en paralelo, `movement-tracking` y
> `debt-tracking` reclamaron **los dos** `[P-009]` para gaps distintos —uno informativo, otro
> crítico y bloqueante—. Ocurrió en la **primera** pasada paralela tras documentarse como riesgo
> teórico: con este fan-out no es un caso raro, es el caso normal.

Para cada feature F-00X a generar, lanza un subagente con el `Agent` tool usando `subagent_type: sdd-spec-writer`. **Antes de emitir, cuéntalas**: el Paso 4b ya fijó cuántas son, y todas salen en **este** mensaje — no hay llamada de prueba (ver abajo):

```
Agent(
  subagent_type: "sdd-spec-writer",
  run_in_background: false,
  prompt: "Lee `.claude/skills/wf-spec-fast-track/SKILL.md` y ejecuta sus pasos TÚ MISMO sobre estos argumentos: <prd.md> --scope-from <discovery.md> --feature F-00X --gap-id-start P-0NN --skip-index [--light|--standard si se pasó o si project-init declara pipeline_mode] [--analysis <analysis.md> si disponible] [--allow-derived-scope-from-analysis **si el Paso 2.5 lo dejó decidido**, sea porque vino de entrada o porque el usuario eligió continuar con alcance derivado en su gate] [--allow-overwrite-sealed-spec **solo** si el usuario eligió regenerar esa feature sellada en el gate del Paso 4b]. NO uses el `Skill` tool: esa skill es `context: fork` y invocarla te forkearía otro subagente en cascada. Dentro de ese SKILL.md, las rutas que empiecen por la variable de directorio de skill (`CLAUDE_SKILL_DIR`) se resuelven contra `.claude/skills/wf-spec-fast-track/`. Al terminar, informa del path del spec generado, nº de gaps `[CRÍTICO]`, nº de asunciones aplicadas y los IDs de gap que hayas usado."
)
```

> **`--skip-index` va siempre en el fan-out ([[D-087]]).** El Paso 10 de `wf-spec-fast-track` manda
> regenerar `_features.md` al terminar — correcto cuando corre suelto, y **N regeneraciones parciales
> cuando corren a la vez**: cada escritor llega en un momento distinto y reescribe el índice del
> proyecto con lo que hay en disco en ese instante. Es inocuo (el regenerador escribe atómico) pero
> deja un índice completo, bien formado y equivocado mientras dura la tanda, que es la clase de
> fallo que no se nota. El flag corta eso **donde nace la instrucción**, en el contrato del escritor,
> no con una prohibición tuya que compita con su propio Paso 10 ([[D-085]]). Tú lo regeneras **una
> sola vez**, en el Paso 6, con la tanda entera delante.

> **La decisión de alcance viaja con el encargo, no se queda en tu contexto ([[D-081]]).** El
> escritor recibe `--analysis`, así que **vuelve a evaluar** las respuestas por su cuenta y se
> detiene con `STOP_REQUIERE_PRD_CHANGE` en cuanto una expande el producto — es su trabajo, y lo
> hace bien. Si el usuario ya resolvió eso arriba y el flag no baja hasta aquí, la pasada entera se
> para levantando N veces una pregunta **ya contestada**, dentro de forks que no pueden
> presentarla. Un gate que se decide en un sitio y se aplica en otro solo sirve si la decisión
> **viaja**. Lo que sigue prohibido es lo de siempre: **tú no armas un `--allow-*`** ([[D-026]]) —
> aquí solo transportas el que el usuario ya eligió.

**CRÍTICO: emite TODOS los `Agent` tool calls en un único mensaje** — no esperes entre ellos. Cada subagente es completamente independiente. Si hay 6 features a generar, tu respuesta debe contener 6 llamadas al `Agent` tool simultáneas, todas con `subagent_type: sdd-spec-writer`. **Y si son 2, ese mensaje lleva 2**: el invariante es el cardinal, no el tamaño de la tanda.

> **No hay llamada de prueba ([[D-084]]).** El número de llamadas de ese mensaje **ya está fijado**
> por el paso anterior: si son cuatro, el mensaje lleva cuatro. Lanzar **una** para ver si el patrón
> funciona y emitir el resto después ya rompió la barrera, aunque las restantes salgan juntas. Es el
> desvío natural —parece prudente, y el informe de la primera parece "confirmar" que se puede
> seguir—, pero no confirma nada que no supieras: los delegados son independientes, no comparten
> estado y ninguno depende del anterior. Si el primero fuera a fallar por una precondición común,
> los otros fallan igual y te enteras en el mismo turno, no en el siguiente.
>
> **Medido (pasada 14 de CU-3.a, 2026-09-15).** Con el subset ya fijado en cuatro features, main
> emitió `F-001` **sola**, esperó sus 351 s y solo entonces mandó las tres restantes en un mensaje,
> narrándolo como *"F-001 listo. Lanzo las tres restantes en paralelo."* — literalmente cierto y aun
> así serializado: 10,6 min de fan-out donde cabían ~6. **El mismo orquestador, en el paso de
> conflictos, emitió los cuatro auditores juntos**: el patrón se sabe. Lo que falla no es el
> conocimiento, es la tentación de probar primero — y con `run_in_background: false` de verdad
> activo, esa tentación ya no es inocua.
>
> **Y vuelve a pasar con N=2, que es donde menos se nota ([[D-092]]).** Pasada de `CU-3.d` del
> 2026-09-18, con este contrato ya reforzado: la primera tanda (dos features) salió `1 + 1` —una
> llamada, 4m13s esperando, y la segunda—, y la **misma sesión** mandó las tres de la tanda
> siguiente juntas. Con dos, "lanzo las dos en paralelo" y emitir una se parecen demasiado: no hay
> un grupo visible que delate al que falta, y el coste (duplicar el paso) es el mismo que con seis.
> **Antes de emitir, di el número y cuenta las llamadas del mensaje contra él.** Si no coinciden,
> el fan-out no ha salido — no lo completes con un segundo mensaje: eso ya es la forma `1 + (N-1)`
> consumada. Y que se mida solo: el probe `sdd-fanout-check.py` cuenta las llamadas por mensaje
> en el transcript, así que esto deja rastro aunque nadie estuviera mirando.


> **Aquí el fan-out es una barrera, y por eso `run_in_background: false` es obligatorio en este paso
> ([[D-047]]).** El Paso 6 regenera el índice leyendo del disco los specs de **todas** las features:
> arrancarlo con una a medias produce un índice incompleto que además se sella como bueno. Las dos
> piezas se sostienen juntas: **N llamadas en un único mensaje** + **el flag**. Un mensaje con las N
> las hace correr a la vez y el flag hace que el mensaje no vuelva hasta que **todas** han acabado —
> una sola barrera para todo el fan-out. Emitirlas en mensajes separados **serializa** el fan-out en
> cuanto el flag surte efecto: cada mensaje espera a su agente antes de lanzar el siguiente, y seis
> features pasan de una tanda a seis rondas.
>
> Si aun así el harness te los lanza en segundo plano, la vía (b) sigue siendo válida — pero
> entonces la barrera la sostienes tú: **no sigas al Paso 6 hasta tener las N notificaciones**, y
> cuenta cuántas te faltan en vez de mirar cuántos ficheros hay en `features/`.

No uses el `Skill` tool para esto — no soporta ejecución paralela.

Espera a que **todas** terminen según el criterio de arriba: tienes el informe de cada delegado. Que los ficheros hayan aparecido en `features/` no te dice que los fast-tracks terminaran, ni con qué resultado. Para cada una, registra **de su informe**:
- Feature ID y nombre
- Si se completó con éxito o falló
- Path del spec generado
- Número de gaps `[CRÍTICO]` encontrados (si los hay)
- Número de asunciones aplicadas

**Si alguno vuelve con un veredicto `STOP_*` en vez de con su spec, esa feature no se ha generado — y eso no es "falló"** ([[D-081]]). Un `STOP_*` es un bloqueo con nombre, y presentarlo es tuyo ([[D-026]]/[[D-064]]): **no lo relances con un `--allow-*` por tu cuenta, ni lo entierres como error genérico en el resumen**. Los demás escritores siguen siendo válidos: continúa con ellos al Paso 6 y trata los parados aparte.
- **`STOP_REQUIERE_PRD_CHANGE`** → si llega **después** de que el Paso 2.5 resolviera el alcance, revisa primero si se te olvidó pasarle el flag; si el alcance no estaba decidido, preséntalo con `AskUserQuestion` (formalizar el cambio en el PRD, recomendada / continuar con alcance derivado) y relanza **solo esas** features con lo que elija.
- **`STOP_SPEC_SELLADO`** → no debería llegar: el Paso 4b ya clasificó y armó el flag. Si llega, preséntalo como el gate de sellados de ese paso, sin decidir tú.
- **`STOP_SPEC_RETIRADO`** → tampoco debería llegar (el Paso 4b las excluye) y **ningún flag lo cierra**: nómbrala como retirada en el informe y sigue.

Si el subset está vacío tras filtrar specs preexistentes (todas las features pedidas ya tenían spec), salta al Paso 6 con el conjunto vacío de "recién generadas".

---

## Paso 6: Regenerar `_features.md` (pasada autoritativa)

`_features.md` es un artefacto **generado**, no editado a mano: lo produce el regenerador determinista `sdd-features-index.py` escaneando el discovery (universo de features + shared models + RF→Feature) + todos los specs presentes (estado real por marcadores, HUs/CAs) + el readiness report si existe (veredicto). Esto elimina de raíz la colisión de escrituras paralelas de los fast-tracks **y** los conflictos de merge entre devs sobre el hub monolítico (un conflicto en `_features.md` pasa a ser ruido: se regenera tras el merge).

Tras esperar a que terminen todos los fast-tracks, ejecuta la pasada autoritativa **una sola vez** desde la raíz del proyecto (el directorio que contiene `.sdd/`):

> **Autoritativa porque es la única, y ahora lo es de verdad ([[D-087]]).** Los escritores reciben
> `--skip-index` en el Paso 5, así que durante el fan-out **nadie toca `_features.md`**: hasta que
> ejecutes esta pasada, el índice sigue diciendo lo que decía antes de empezar. Eso es correcto y es
> el punto — un índice viejo se reconoce, uno reescrito a medias no. **No sigas sin ejecutarla**, ni
> cites el índice en tu resumen antes de hacerlo: lo que se generó sale de los informes de tus
> delegados. Y si la tanda se corta a medias (límite de sesión, un `STOP_*`), ejecútala igual con lo
> que haya: los specs en disco son reales aunque falten los demás.

```
python3 .sdd/scripts/sdd-features-index.py <raíz_spec>
```

`<raíz_spec>` es el directorio raíz de artefactos spec donde viven `features/` y `_features.md` (regla de layout: `artifacts.spec` de `.sdd/project-init.json` si está declarado; si no, el directorio del PRD de entrada). El resultado cubre TODAS las features del discovery: las del subset recién generadas quedan con su estado real, las preexistentes se reflejan tal cual desde sus specs en disco, y las que aún no tienen spec aparecen como `PENDIENTE_GENERACIÓN` — sin que tú tengas que preservar estado a mano. Si el script no existe:
> "⚠ Falta `.sdd/scripts/sdd-features-index.py`. Re-ejecuta la instalación del ecosistema (`install.sh`) para reponer los scripts de enforcement. El índice `_features.md` no se ha regenerado."

> **Comprueba la salida antes de dar el paso por bueno ([[D-046]]).** El script imprime cuántas
> features ha indexado y avisa por `stderr` si no encontró discovery. **Ese recuento tiene que
> coincidir con el universo del discovery**, no con las features que acabas de generar: si sale
> `discovery=no` o el número es el del subset, el índice ha perdido las `PENDIENTE_GENERACIÓN` y
> deja de ser el mapa del producto. En topología `authoring` el discovery vive con el PRD
> (`artifacts.prd`), no en `<raíz_spec>` — el script cruza esa frontera solo mediante
> `.sdd/project-init.json`. Si el aviso aparece, re-ejecuta pasando el discovery explícito:
> `python3 .sdd/scripts/sdd-features-index.py <raíz_spec> --discovery <path_discovery>`.
>
> No arregles esto editando `_features.md` a mano: es un artefacto generado y la siguiente
> regeneración se lleva tu parche por delante.

---

## Paso 7: Conflict check (si no `--skip-conflict`)

Opera sobre **todas las features con spec en `features/`**, incluyendo preexistentes de iteraciones anteriores. Con ≥2 specs: por cada spec recién generado delega con la tool `Agent` ([[D-043]]), `subagent_type: "sdd-spec-auditor"` y `run_in_background: false`, con el prompt `"Lee .claude/skills/wf-spec-conflict/SKILL.md y ejecuta sus pasos TÚ MISMO sobre: <spec.md> --features-dir <features_dir>. NO uses el Skill tool ([[D-044]]): ya eres su agente y te forkearía en un clon."` (solo los nuevos se chequean contra todos). **Emite las N llamadas en un único mensaje**, con el flag: igual que el Paso 5, es una barrera — el Paso 8 lee lo que escriben todas ([[D-047]]). Y como en el Paso 5, **no hay llamada de prueba** ([[D-084]]): el número lo fija el conjunto de specs nuevos, no el resultado del primer auditor — **también cuando ese número es 2** ([[D-092]]). **El informe lo escribe cada auditor**, en `features/<nombre>/spec/<nombre>_conflict_report.md`, junto a su spec: tú no escribes ninguno ([[D-059]]). Sin specs nuevos → omitir.

> **Los auditores pueden contradecirse, y tú no eres el árbitro ([[D-047]]).** Cada auditor mira el
> mismo grafo desde su feature, así que sobre un mismo par es normal que uno levante un conflicto y
> otro no. **No descartes el hallazgo minoritario ni promedies veredictos**: un `SIN_CONFLICTOS` es
> "yo no lo veo desde aquí", no "no existe". Tampoco te pongas a leer los specs para decidir quién
> tiene razón — eso es analizar contenido, y no es tu papel (Regla de oro).
>
> Lo que sí haces: **recoger la divergencia de los informes y pasársela al Paso 8 en el prompt**,
> nombrando el par, el ID del conflicto y quién lo levantó frente a quién lo negó. El readiness es
> un cuarto lector independiente sobre el conjunto y es **quien arbitra**; llega con encargo
> explícito o no arbitra nada. Si no delegas readiness (`--skip-readiness`), el conflicto queda
> **abierto y así lo reportas** — no lo cierres tú por mayoría.

> **Y no consolides sus informes en un fichero ([[D-059]]).** La frase anterior decía *"Escribe
> `_conflict_report.md` si hay conflictos"* en un párrafo dirigido a ti, así que se leía como
> encargo tuyo. **Medido (pasada 13 de CU-3.a):** el orquestador escribió un
> `spec/_conflict_report.md` consolidando los cuatro informes —con buen criterio: lo etiquetó como
> "no es un arbitraje", atribuyó cada hallazgo a su auditor y pasó igualmente las divergencias en
> el prompt—. Y aun así **se equivocó al transcribir**: adjudicó un conflicto al auditor
> equivocado, y lo cazó el readiness al ir a las fuentes. Consolidar te obliga a copiar contenido
> que no produjiste, y copiar introduce errores que no estaban en el original. La vista
> consolidada con autoridad la produce el readiness; hasta entonces, la divergencia viaja **en el
> prompt**, que no es un artefacto que nadie gobierne.

> **Los informes de las tandas anteriores se quedan en disco, y no los tocas ([[D-090]]).** Iterando
> por subsets, los de la primera tanda compararon un universo más pequeño que el de ahora. No los
> relances ni los borres: cada informe declara en su cabecera el `Conjunto comparado`, y el Paso 8
> los marca **ESTANCADO** por ese campo cuando no cubren los specs actuales. Tampoco tienes que
> avisar de la colisión de IDs —desde v0.116.0 cada auditor numera con su feature delante
> (`CF-F001-01`), así que no hay dos hallazgos homónimos que desambiguar—. Las dos cosas se
> improvisaron a mano en la pasada del 2026-09-18, y lo que un orquestador improvisa una vez, el
> siguiente no lo hace.

---

## Paso 8: Readiness check (si no `--skip-readiness`)

Delega con la tool `Agent` ([[D-043]]), `subagent_type: "sdd-spec-auditor"` y `run_in_background: false`, con el prompt `"Lee .claude/skills/wf-spec-readiness/SKILL.md y ejecuta sus pasos TÚ MISMO sobre: <features_dir>/. NO uses el Skill tool ([[D-044]]): ya eres su agente y te forkearía en un clon."`. Si el Paso 7 dejó veredictos divergentes, **añade al prompt el encargo de arbitrarlos**, con el par, el ID y las dos posturas. Genera `_readiness_report.md` en el directorio raíz de artefactos spec (junto a `_features.md`) y actualiza `_features.md` con el estado de cada feature (incluyendo `PENDIENTE_GENERACIÓN` para las no procesadas aún).

---

## Paso 9: Informar al usuario

Presenta el resumen siguiendo la plantilla de `${CLAUDE_SKILL_DIR}/references/output_template.md` (consúltala por `Bash`; es material **del skill**, no un artefacto del proyecto — la Regla de oro habla de PRD, analysis y specs). Diferencia features procesadas en esta iteración vs preexistentes de iteraciones anteriores vs pendientes de futura generación. Incluye **todos** los bloques condicionales de siguientes pasos que apliquen — la plantilla los lista; no los enumeres de memoria aquí ([[D-069]]), que es como se quedó fuera el de las features dadas de baja.
