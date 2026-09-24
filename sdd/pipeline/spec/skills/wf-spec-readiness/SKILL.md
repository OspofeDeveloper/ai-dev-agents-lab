---
name: wf-spec-readiness
description: "Genera un informe de readiness desde los artefactos post-spec (specs, READMEs, _features.md, _conflict_report.md): que features estan listas para plan, cuales bloqueadas y por que, y el orden de implementacion recomendado."
when_to_use: "Activa en frases como 'que features estan listas', 'readiness de las features', 'cuales puedo planificar', 'orden de implementacion', 'verifica readiness', 'que falta para planificar'."
argument-hint: "<path/features/>"
effort: medium
allowed-tools: [Read, Bash]
context: fork
agent: sdd-spec-auditor
user-invocable: true
---

# Workflow: READINESS

Tu objetivo es sintetizar el estado de los artefactos post-spec-generation en un informe accionable que diga exactamente qué features pueden pasar a planificación y en qué orden. **No tocas los specs que lees**: escribes tu informe y nada más. Usa `kb-gap-conventions` para interpretar marcadores y severidades, y `kb-conflict-expert` para interpretar severidades de conflictos.

**Regla de oro:** tu informe **es el veredicto**, no una fotografía neutra. Cuando los informes de conflicto se contradicen entre sí, **arbitras tú** (Paso 4c) — y el regenerador del índice toma tu `## Matriz de readiness` como autoridad por encima de la derivación mecánica. Lo que no haces es **resolver** lo que falta: señalas qué bloquea y dónde está, y quien corresponda lo arregla.

> **Antes esto decía dos cosas incompatibles ([[D-067]]).** La regla de oro afirmaba *"no propone
> resoluciones"* y *"no modifica artefactos"* —prosa anterior a [[D-047]]— mientras el Paso 4c te
> nombra árbitro y el 8.5 hace tu veredicto autoritativo. Manda lo segundo.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Directorio de features**: el primer argumento. Debe ser el directorio que contiene las carpetas de features (ej: `docs/features/`).

Si no hay argumento, intenta inferir buscando un directorio `features/` en el directorio actual.

Si no hay argumento y no se puede inferir, informa al usuario:
> "Necesito el directorio donde viven las features, para revisar cuáles están listas."

---

## Paso 2: Localizar artefactos

1. Busca `*_features.md` en el directorio padre del directorio de features (ej: si features/ está en `docs/features/`, busca `docs/*_features.md`).
2. Busca todos los `*_spec.md` cubriendo ambos layouts de feature: `<features-dir>/*/spec/*_spec.md` (subcarpetas) y `<features-dir>/*/*_spec.md` (plano legacy).
3. Busca todos los `README.md` dentro de `<features-dir>/*/README.md`.
4. Busca los informes de conflictos **en los dos sitios donde se escriben** (opcional — pueden no existir):
   - **Consolidado**: `*_conflict_report.md` en el directorio padre del directorio de features — lo escribe `/wf-spec-conflict` cuando se verifica el directorio entero de una vez.
   - **Por feature**: `<features-dir>/*/spec/*_conflict_report.md` (subcarpetas) y `<features-dir>/*/*_conflict_report.md` (plano legacy) — es lo que produce el fan-out del Paso 7 de `wf-spec-features-first`, que lanza **un auditor por spec** y cada uno escribe junto a su spec.

   Buscar solo en la raíz deja fuera **todos** los informes del fan-out, que es el camino por defecto ([[D-047]]): el readiness se declararía "sin análisis de conflictos" teniendo N informes en disco, y esa advertencia no bloquea — se pierde en silencio.

Valida:
- Si no hay `_features.md` → detén: "No se encontró `_features.md` en `<directorio_padre>`. Hay que generar antes los specs por feature."
- Si no hay specs → detén: "No se encontraron specs de feature en `<features-dir>`. Hay que generarlos antes."
- Si falta algún README → advertencia no bloqueante: "Falta README.md en `<feature>/`. Las dependencias de esta feature se inferirán solo del `_features.md`."
- Si no hay **ningún** informe de conflictos en ninguno de los dos sitios → advertencia no bloqueante: "No se encontró ningún `_conflict_report.md`. Un análisis de conflictos completo daría más información; continúo sin él."

---

## Paso 3: Leer todos los artefactos

Lee el contenido completo de:
- `_features.md`
- Cada `*_spec.md` de feature
- Cada `README.md` de feature (los que existan)
- **Todos** los informes de conflictos localizados en el Paso 2.4 (el consolidado y los de cada feature), no solo el primero que encuentres

---

## Paso 4: Inventariar estado de cada feature

Para cada feature, extrae:

### 4a — Identificación

Del `_features.md`, extrae para cada feature:
- Feature ID (F-001, F-002, etc.)
- Nombre de la feature
- Ruta al spec (si existe)

**Detección de features no generadas aún**: si una feature del `_features.md` no tiene archivo `*_spec.md` correspondiente en `<features-dir>/<nombre>/`, marca la feature como `PENDIENTE_GENERACIÓN` y omite los Pasos 4b–4d para ella (no hay spec que inspeccionar). Sus dependencias se infieren solo del `_features.md`.

### 4b — Gaps (marcadores [INCOMPLETO])

Busca la cadena literal `[INCOMPLETO]` en el spec de la feature. Para cada HU marcada:
- ID de la HU (ej: HU-003)
- Gaps que la bloquean (referenciados en la línea que contiene `Pendiente de gap(s):` o `[P-XXX]` cercanos al marcador)

Clasifica la feature como **BLOQUEADA** si tiene al menos una HU `[INCOMPLETO]`.

### 4c — Conflictos no resueltos

Para **cada** informe de conflictos localizado:
- Primero verifica su estado general. Debe indicar explícitamente `SIN_CONFLICTOS` o `CONFLICTOS_DETECTADOS`.
- Si el archivo existe pero no deja ese estado de forma inequívoca, trátalo como artefacto ambiguo y repórtalo en el informe de readiness.
- **Y comprueba su vigencia por el campo `Conjunto comparado` de la cabecera ([[D-090]]).** Si ese
  conjunto **no incluye** todos los specs que hay ahora en `features/`, el informe describe un
  universo que ya no existe: márcalo **ESTANCADO** en tu informe, di contra qué se calculó y qué
  specs no vio, y **conserva sus hallazgos** —siguen siendo ciertos sobre las features que sí
  comparó— pero no los presentes como cobertura del conjunto actual. Un informe sin el campo (de
  antes de v0.116.0) se trata como **vigencia desconocida** y se dice, no se asume vigente.
  Es el caso normal de la iteración por subsets: la primera tanda comparó 2 specs, la segunda 5, y
  los informes de la primera se quedan en disco con pinta de actuales.
- **Y un ESTANCADO se cierra en tu informe, no se queda en diagnóstico ([[D-093]]).** Antes de
  proponer nada, mira **quién cubre los pares que ese informe no vio**: el fan-out compara cada
  spec nuevo contra **todos** los que hay, así que el par (viejo, nuevo) lo miró el auditor del
  nuevo. Lo normal, entonces, es que la **cobertura por pares esté completa** y lo viejo sea el
  **documento**, no el análisis. Dilo así de explícito —*"el veredicto de F-002 solo cubre el par
  F-002×F-003; sus choques con F-001, F-004 y F-007 están en los informes vigentes de esas tres"*—
  y **añade la acción en «Próximos pasos»**: rehacer ese informe cuando se quiera tenerlo al día,
  o, si al cruzarlo detectas un par que de verdad **no ha mirado nadie**, pedir una revisión de
  conflictos para ese par, que ahí sí falta análisis. Un ESTANCADO sin acción deja al lector con
  el diagnóstico y sin el cierre — y el informe viejo sigue en disco diciendo lo que decía.
- Busca todos los conflictos de severidad **ALTA** que involucren esta feature.
- Un conflicto se considera no resuelto si aparece en algún informe (el informe refleja el estado en el momento de su generación; si se resolvió, la verificación de conflictos tuvo que volver a pasarse después).

Clasifica la feature como **BLOQUEADA** si tiene al menos un conflicto ALTA asociado.

> **Cuando los informes se contradicen, arbitras tú ([[D-047]]).** Con el fan-out de features-first
> hay **un auditor por feature**, y cada uno mira el mismo grafo desde su lado: es esperable que
> sobre un mismo par uno levante un conflicto y otro declare `SIN_CONFLICTOS`. Tú eres el primer
> lector que ve **todos** los specs y **todos** los informes a la vez, así que la contradicción se
> resuelve aquí y no antes.
>
> Reglas de arbitraje:
> - **Un `SIN_CONFLICTOS` no refuta un hallazgo.** Significa "no lo vi desde mi feature", que es
>   justo lo que pasa cuando el conflicto está en el lado del otro. Nunca cierres un conflicto por
>   recuento de informes.
> - **Resuelve mirando los specs**, que sí tienes: comprueba en el texto si la contradicción existe.
>   Un conflicto solo se descarta con la cita concreta que lo desmiente.
> - **Deja constancia del desacuerdo** en el informe: el ID del conflicto, quién lo levantó, quién no
>   lo vio, y tu veredicto con su evidencia. Un conflicto silenciosamente desaparecido entre dos
>   pasadas es indistinguible de uno resuelto. Al justificar por qué tu veredicto pesa más, di
>   **"la regla de arbitraje de este informe"** — no el nombre del workflow que la define (Paso 7).
> - **Y si tu arbitraje confirma el conflicto, la portada del informe que no lo vio queda
>   desmentida — dilo donde se lee ([[D-095]]).** Ese informe sigue abriendo con
>   `SIN_CONFLICTOS` sobre un conjunto que **incluye** la feature que tú acabas de bloquear, y
>   quien abre el informe de una feature empieza por su portada. No lo edites —es de su auditor—:
>   márcalo en la cabecera de vigencia como **`VIGENTE — portada desmentida por el arbitraje
>   (CF-F001-01)`** — **solo si el par confirmado está en el alcance de ese informe** ([[D-096]]).
>   Un informe en modo feature cubre los pares que incluyen su spec: que no viera un choque entre
>   otros dos specs no lo desmiente, porque no le tocaba. Si aun así se pronunció sobre ese par
>   ajeno (*"el resto de pares no presenta choques"*), sí queda desmentido, y dilo así: se salió
>   de su alcance y acertó menos que el auditor dueño del par y añade la acción en «Próximos pasos»: su portada no es el estado de esa
>   feature, lo es este informe, y queda al día al rehacer ese informe **una vez resuelto el
>   conflicto** (rehacerlo antes solo repite el desacuerdo).
> - **Si no puedes resolverlo con los specs**, no lo cierres: mantenlo **abierto** con la severidad
>   más alta que le haya dado cualquier informe y marca la feature `BLOQUEADA`. El coste de un falso
>   bloqueo lo paga una revisión; el de un falso "listo" lo paga el plan.
>
> **Los IDs de hallazgo ya vienen desambiguados: cítalos tal cual ([[D-090]]).** Desde v0.116.0
> cada auditor numera con su feature delante (`CF-F001-01`), así que dos informes distintos no
> pueden chocar y **no tienes que inventarte un espacio de nombres propio**: renumerar rompe la
> trazabilidad contra el informe de origen, que es lo que abre quien va a arreglar el choque.
> **Excepción, y dilo cuando pase:** si te llegan informes viejos con IDs locales que **sí**
> colisionan (tres `CF-002` distintos), desambigua citando `<feature>:<ID>` —
> `registro-de-movimientos:CF-002`— en vez de renumerar; el ID sigue siendo el del informe y la
> referencia es única.

### 4d — Dependencias

Del README de la feature, extrae la sección `## Dependencias`:
- **Requiere**: lista de features que deben implementarse antes
- **Bloquea**: lista de features que dependen de esta

Complementa con el `_features.md`: si una feature referencia un shared model cuyo owner es otra feature, la feature referenciadora depende de la feature owner (a menos que ya esté en la lista de Requiere).

Construye la lista unificada de dependencias para cada feature.

### 4e — Sello del spec

De la cabecera de cada `*_spec.md`, extrae la línea `Estado:` — **con `grep`, no de tu
lectura** (extracción determinista y acotada, [[D-048]]):

```bash
!grep -m1 -E '^\s*>?\s*\**Estado' "<path_del_spec>"
```

- `VALIDADO` → el sello está puesto; no aporta bloqueante.
- `BORRADOR` → clasifica la feature como **BLOQUEADA** con el bloqueante
  *"pendiente de validación"* ([[D-061]]/[[D-077]]). Es el estado de un spec recién
  generado y el de cualquiera al que un delta, una enmienda o una resincronización le
  reabrieron la validación.
- `RETIRADO` → `RETIRADA` (ver Paso 6); no se mezcla con los demás bloqueantes.
- **Sin línea `Estado:`** → no concluyas nada. Un spec legacy anterior a [[D-061]] no la
  lleva, y el gate tampoco lo bloquea por eso: misma política conservadora que
  `status_sync`. Sigue con el resto de criterios.

---

## Paso 5: Construir el grafo de dependencias

1. Crea un grafo dirigido donde cada nodo es una feature y cada arista va de la dependencia hacia la feature que la requiere.
2. Detecta ciclos. Si hay un ciclo → repórtalo en la sección correspondiente del informe pero no detengas la ejecución. Excluye las features del ciclo del topological sort.
3. Realiza un **topological sort** agrupando en fases (waves) las features que pueden ejecutarse en paralelo:
   - **Fase 1**: features sin dependencias entrantes (nodos raíz)
   - **Fase 2**: features cuyas dependencias están todas en Fase 1
   - **Fase N**: features cuyas dependencias están todas en fases anteriores

---

## Paso 6: Determinar readiness de cada feature

Para cada feature, asigna un estado:

| Estado | Condición |
|--------|-----------|
| `LISTA` | Sin `[INCOMPLETO]`, sin conflictos ALTA, sin artefactos ambiguos, sin dependencias bloqueantes **y con el spec sellado `Estado: VALIDADO`** |
| `BLOQUEADA` | Tiene HUs `[INCOMPLETO]`, conflictos ALTA, dependencias bloqueantes, artefactos ambiguos que impiden decidir con seguridad, **o el spec sigue en `Estado: BORRADOR`** (bloqueante: *"pendiente de validación"*) |
| `PENDIENTE_GENERACIÓN` | Identificada en el discovery pero aún no se ha generado spec (no se ha incluido en ninguna iteración de `wf-spec-features-first`). No es un bloqueo accionable — refleja que el humano aún no ha pedido procesarla. |
| `REQUIERE_CAMBIO_PRD` | El spec o `_features.md` declara alcance derivado desde analysis que debería consolidarse primero en PRD, o el artefacto explicita un aviso de gobernanza pendiente |
| `RETIRADA` | El spec declara `Estado: RETIRADO`: el producto dio de baja esa capacidad ([[D-074]]). **No es un bloqueo**, es un final — no lleva bloqueantes que resolver, y va en la columna el `CR-XXX` que la decidió |

Una feature puede tener múltiples bloqueos simultáneos. En ese caso, listar todos los motivos en la columna de bloqueantes. La prioridad de display es: CAMBIO_PRD > GAPS > CONFLICTOS > DEPENDENCIAS > AMBIGÜEDAD_DE_ARTEFACTO > SIN_VALIDAR.

> **`SIN_VALIDAR` va el último de la lista a propósito ([[D-077]]).** Un spec con gaps o
> conflictos abiertos **no se puede validar** —`sdd-seal.py spec --check` lo rechaza—, así que
> encabezar con *"pendiente de validación"* manda a un callejón sin salida. Primero el motivo
> que sí se puede resolver; el sello queda como lo que es, el último paso antes de planificar.

**Nota importante**: el readiness report usa solo estados canónicos. El detalle fino se expresa en la columna `Bloqueantes`, no creando variantes de estado adicionales.

> **`LISTA` significa "el gate de la fase siguiente la deja pasar" ([[D-077]]).** No es una
> valoración de la calidad del spec: es una **predicción**, y el que la verifica es
> `gate_spec_fiable`. Por eso el sello entra en la condición — desde [[D-061]] ese gate
> deniega `wf-prepare-plan` sobre un spec en `BORRADOR`, y un spec recién generado **nace en
> borrador**. Hasta [[D-077]] la rúbrica no lo miraba: el recorrido normal de la fase
> terminaba con un informe diciendo `LISTA` y un gate denegando, y el usuario se enteraba al
> pedir el plan. Lo mide `CU-3.o` punto 4.
>
> **Dilo como lo que es.** El bloqueante se escribe *"pendiente de validación"*, no como si el
> spec tuviera un defecto: falta un paso del proceso, y su contenido puede estar impecable.
> Las features en ese estado **sí participan** del orden de implementación — a diferencia de
> `PENDIENTE_GENERACIÓN` y `RETIRADA` —, porque lo que les falta es una firma, no trabajo.

> **Un conflicto ALTA bloquea en este informe y en ningún otro sitio ([[D-077]]).** Ningún gate
> mecánico lee los `_conflict_report.md`, y **no debe leerlos**: la severidad la asigna un
> juicio experto y los auditores del fan-out se contradicen sobre el mismo par por diseño
> ([[D-047]]). `wf-prepare-plan` **avisa y continúa**. Así que tu `BLOQUEADA` por conflicto es
> lo único que se interpone: escribe el bloqueante para que se entienda **qué hay que acordar
> y con quién**, no como un trámite que alguien vaya a destrabar por ti.

**Nota sobre `RETIRADA`**: igual que las `PENDIENTE_GENERACIÓN`, **no participan del topological sort ni del orden de implementación** — pero por el motivo opuesto: no es que todavía no haya spec, es que ya no hay feature. Si otra feature declara una dependencia sobre una `RETIRADA`, eso **sí** se reporta como bloqueante de la que depende: se quedó apuntando a algo que el producto retiró.

**Nota sobre `PENDIENTE_GENERACIÓN`**: estas features se incluyen en el `_features.md` y en el informe de readiness como visibilidad del backlog, pero no participan del topological sort ni del orden de implementación — no hay spec con dependencias declaradas hasta que se generen. Si otra feature ya generada declara una dependencia sobre una `PENDIENTE_GENERACIÓN`, esa dependencia se reporta como "dependencia hacia feature no generada todavía" (no bloquea readiness de la feature ya generada, pero sí señala al usuario qué generar a continuación).

---

## Paso 7: Formato del informe

Usa `${CLAUDE_SKILL_DIR}/references/readiness_report_template.md` para estructurar el informe.

> **Lo que escribes aquí lo lee una persona, y esa persona no invoca comandos.** Los
> **bloqueantes** y lo que propongas para desbloquearlos van en lenguaje natural, nombrando **la
> acción**: *"responder los gaps que bloquean sus historias"*, *"resolver el conflicto CF-F003-01 con
> F-006"*, *"generar el spec de F-007"* — nunca el workflow que lo hace, ni con barra ni sin ella.
> Estados, IDs y marcadores (`LISTA`, `BLOQUEADA`, `PENDIENTE_GENERACIÓN`, `F-00X`, `CF-F001-01`,
> `[INCOMPLETO]`) **son contrato** y se quedan tal cual.
>
> **Y esto vale para el informe entero, no solo para los bloqueantes.** Medido dos veces: pasada 9
> de CU-3.a —un nombre de workflow en la "Sugerencia de resolución", con la guía de fase
> **cargada**— y pasada 16, donde se coló en un sitio que esta norma no nombraba: **la
> justificación del arbitraje** (*"regla de arbitraje explícita del propio `wf-spec-readiness`"*).
> Ahí no estabas recomendando una acción, estabas citando tu autoridad para contradecir a un
> auditor — y se cita igual sin nombrar el workflow: **"la regla de arbitraje de este informe"**.
> La guía da contexto; esta línea es la instrucción.
>
> **Y la misma norma vale para el nombre de una `kb-*` ([[D-091]]).** Es la forma que se escapó en
> la pasada de `CU-3.d` del 2026-09-18, dos veces en este informe: *"Regla 4 de
> `kb-conflict-expert`"*, *"la tabla de severidad de `kb-conflict-expert` da ALTA por defecto"*.
> Cita la regla **por lo que dice** —*"el mismo modelo con comportamientos distintos en dos CAs de
> features diferentes"*, *"un shared model inconsistente corrompe el modelo de dominio"*—: el
> veredicto se sostiene igual y quien lo lee no tiene que saber qué es una kb.

---

## Paso 8: Escribir el resultado

Path de salida: directorio padre del directorio de features + `<basename>_readiness_report.md`
- El basename se toma del `_features.md` encontrado (ej: si es `prd-hogar-sad_features.md` → `prd-hogar-sad_readiness_report.md`)
- Ejemplo: `docs/prd-hogar-sad_features.md` → `docs/prd-hogar-sad_readiness_report.md`

**Si ya existe, sobreescríbelo sin preguntar ([[D-064]]).** Un informe de readiness es un artefacto
**derivado**: no guarda ninguna decisión humana dentro, y quien lanza el flujo lo regenera en
cada pasada. Un gate aquí no protegería nada — y, siendo `context: fork`, tampoco podrías
presentarlo. Lo que sí haces es **decir en tu informe que lo reemplazaste**.

Escribe el informe en el archivo correspondiente.

> **Con qué lo escribes, y por qué no con `Write` ([[D-051]]).** El agente que ejecuta esta
> skill tiene `Write` y `Edit` **prohibidos**: es el candado que impide que un auditor
> reescriba lo que audita. Tu informe **sí** lo escribes tú, con redirección por `Bash`
> (`cat > "<path>" <<'EOF' … EOF`). **No le pases la escritura al hilo principal:** el
> informe es tu output, y main no escribe artefactos ([[D-060]]).
>
> Y que quede claro el alcance del candado: con `Bash` disponible, técnicamente nada te
> impide tocar los specs que lees. **No lo haces por norma, no porque no puedas.**

---

## Paso 8.5: Regenerar `_features.md` desde el report

No edites `_features.md` a mano: el veredicto vive en TU informe y el índice lo deriva de ahí. `_features.md` es un índice **generado**: el regenerador `sdd-features-index.py` lee tu `## Matriz de readiness` y la usa como **veredicto autoritativo** del estado por feature (anula la derivación marcador-based). Basta con regenerar el índice desde la raíz del proyecto (el directorio que contiene `.sdd/`):

```
python3 .sdd/scripts/sdd-features-index.py <raíz_spec>
```

`<raíz_spec>` es el directorio que contiene `features/` y `_features.md` (el directorio padre del de features, localizado en el Paso 2). El estado y los bloqueantes de cada feature se propagan desde tu report. Si el script no existe:
> "⚠ Falta `.sdd/scripts/sdd-features-index.py`. Re-ejecuta la instalación del ecosistema (`install.sh`) para reponer los scripts de enforcement. El índice `_features.md` no se ha regenerado."

---

## Paso 9: Informar al usuario

Informa: path del informe, resumen (N listas de M totales, N bloqueadas por tipo, N `PENDIENTE_GENERACIÓN`). Siguientes pasos según estado, **descritos como acciones que puede pedirte**: si todas listas → **generar el plan técnico** feature a feature, siguiendo el orden por fases del informe; si algunas listas → empezar por las primeras fases; si ninguna → resolver antes los bloqueos que el informe lista; si hay `PENDIENTE_GENERACIÓN` → nombrar esas features por su `F-00X` y ofrecerle **generar sus specs** cuando quiera.
