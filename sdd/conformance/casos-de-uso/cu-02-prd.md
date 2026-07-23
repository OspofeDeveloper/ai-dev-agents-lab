# CU-2 — Crear y dejar listo un PRD

**Objetivo:** verificar que el sistema redacta un PRD de negocio sin inventar (marca
`[ASUNCIÓN]` lo que no traza a la fuente) y que la revisión no lo da por `LISTO`
mientras queden asunciones sin confirmar ni se autoaprueba.
**Proyecto a usar:** un producto real del que tengas notas o un brief informal
(cualquier dominio). Idealmente material con afirmaciones no triviales o lagunas, para
que el PRD tenga que marcar `[ASUNCIÓN]`.
**Cobertura automática:** ninguna directa — la calidad del PRD y el respeto del gate
de asunciones son juicio del agente `prd-expert`, así que estos escenarios son
**manuales**. El conteo de asunciones (`grep "[ASUNCIÓN"`, sin exigir el `]` de cierre para
tolerar también la forma verbosa `[ASUNCIÓN: …]`) sí es determinista.

> [!IMPORTANT]
> **La regla que gobierna toda la fase — anti-fabricación (Regla 12 de
> `kb-prd-expert`):** toda afirmación de negocio traza al material fuente, o se
> marca `[ASUNCIÓN]` (inline) + `[ASN-XXX]` en `## Asunciones del PRD`. Un PRD con
> asunciones sin confirmar **no llega a `LISTO`**.

---

## 🧪 Qué se prueba aquí (por componente)

CU-2 es un **objetivo de usuario** (crear y dejar listo un PRD), no una sola skill: sus
escenarios ejercitan **dos componentes**. Marca cada escenario al ejecutarlo. El estado de
cobertura autoritativo (ejes happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) —
esta vista es la **transpuesta** para leer/ejecutar el CU.

### `wf-prd-create` — redactar el PRD (`prd-expert`) (5)
- [x] CU-2.a — Crear el PRD desde notas ✅ validado 2026-07-08
- [x] CU-2.b — Crear el PRD sin notas (brief oral) ✅ validado 2026-07-08
- [x] CU-2.c — Apuntar a un directorio o fuente inexistente ✅ validado 2026-07-12
- [x] CU-2.d — Regenerar un PRD que ya existe ✅ validado 2026-07-12 (ramas 1 sellado + 2 draft-explícito; rama 3 ambigua pendiente opcional)
- [x] CU-2.i — Crear el PRD a una ruta de salida explícita (`--output`) ✅ validado 2026-07-15 (gate D-025, ×3, ambas ramas)

### `wf-prd-review` — revisar el PRD y sellar (`prd-expert`) (5)
- [x] CU-2.e — Gate de asunciones + orden PRD→spec (lo más crítico, conversacional A-F) ✅ SELLADO 2026-07-22 (Tanda A ×3, probe E por 2 vías + D-032)
- [ ] CU-2.f — Veredicto LISTO y sello de aprobación
- [ ] CU-2.g — Pasar algo que no es un PRD
- [ ] CU-2.h — La revisión no reescribe a su cosecha
- [ ] CU-2.j — Cascada determinista de dependencias entre asunciones (D-029)

> **Capa determinista** (no es un escenario manual): el conteo de asunciones
> (`grep "[ASUNCIÓN"`, Paso 5.5 de `wf-prd-review`) es el único check automático de la fase.

---

## CU-2.a — Crear el PRD desde notas

**Precondición:** existe un fichero de notas/brief válido (tus notas reales del producto).
**Mecanismo:** skill `wf-prd-create` en el **hilo principal** (gates `AskUserQuestion`: brief
si no hay `--source`, confirmación de sobreescritura); delega la redacción al agente
**`prd-expert`** (carga `kb-prd-expert`) vía la tool `Agent`, en **una sola invocación
síncrona** (espera el resultado; no relanza ni sondea el filesystem → sin race de doble
escritura). Output: `prd.md` (en `--output`, o `artifacts.prd` de `project-init.json`, o
`<dir>/prd.md`).

1. Le pides que te cree el PRD a partir de esas notas ("créame el PRD desde este brief").
   → **Esperado:** `prd-expert` redacta `prd.md` con las secciones mínimas (Resumen,
     Actores, Alcance dentro/fuera, Reglas transversales); lo que no traza a la fuente
     va marcado con la bandera inline **`[ASUNCIÓN]`** (token literal, la explicación va en
     `## Asunciones del PRD`) + su `[ASN-XXX]`; te reporta el **path** del PRD y el **nº de
     asunciones**.

> **Comprobación de formato (capa determinista):** `grep -c "\[ASUNCIÓN" prd.md` debe igualar
> el nº de marcas inline. El gate de `wf-prd-review` tolera la forma verbosa `[ASUNCIÓN: …]`,
> pero el contrato (`kb-prd-expert` Regla 12) pide la bandera escueta `[ASUNCIÓN]`: la verbosa
> duplica la sección y es señal de deriva del agente, aunque ya no rompe el conteo.

> **Correspondencia 1:1 (capa determinista):** el nº de marcas inline `[ASUNCIÓN]` debe **igualar**
> el nº de entradas `[ASN-XXX]` de `## Asunciones del PRD` (`kb-prd-expert` Regla 12, "Correspondencia 1:1"):
> `[ $(grep -c "\[ASUNCIÓN" prd.md) -eq $(grep -oE "\[ASN-[0-9]+\]" prd.md | sort -u | wc -l) ]`. Una
> marca de más = **huérfana** (el review itera sobre `[ASN-XXX]` y no la limpiará → marcador muerto en un
> PRD sellado; es justo lo que CU-2.e vigila al rechazar). Derivas observadas: agrupar varias exclusiones
> de `## Fuera del Alcance` bajo un solo `[ASN-XXX]`, o reafirmar en `## Reglas de Negocio Transversales`
> una asunción ya catalogada. `inline > entradas` es FALLO de formato.

> **Frontmatter y conteo (capa determinista):** el PRD debe abrir con el frontmatter YAML
> obligatorio (`type`, `product`, `version`, `created`, `status`) + el placeholder
> `> **Aprobado por:** [pendiente…]` (guía de estructura de `kb-prd-expert`). Y el **nº de
> asunciones que reporta el orquestador** sale del `grep`, **no** de la prosa del agente (que
> puede contar mal sobre su propio texto — verificado: dijo 11, grep=10).

2. Tras crear, observa qué hace el orquestador a continuación (frontera create→review).
   → **Esperado:** **para y recomienda `/wf-prd-review`**. **NO** confirma/rechaza/edita las
     asunciones, **no** monta una entrevista (`AskUserQuestion` por cada `[ASN-XXX]`), **no**
     integra decisiones ni sube versión ni sella `Aprobado por:`. Ese gate es exclusivo de
     `wf-prd-review` (Pasos 5.5/6); aquí solo se crea y se enruta.

**Resultado:** PASS si redacta el PRD trazado a la fuente, marca lo no dicho con la bandera
detectable por el gate, reporta path + nº de asunciones, y **tras crear para y enruta a
`/wf-prd-review`** · FALLO si inventa actores/alcance sin marcarlos, mete tecnología, o
**improvisa el gate de asunciones** (entrevista/integración/sello) en vez de enrutar a review.
**Desviación → reportar:** issue citando `CU-2.a`.

> **Validación (2026-07-08, consumer real `myops-app-specs`).** PASS en **tres** puntos de
> lanzamiento —raíz del proyecto, subdirectorio `prd/` y subdirectorio `spec/`—: en las tres
> el orquestador enrutó a `wf-prd-create`, delegó a `prd-expert`, obtuvo el nº de asunciones por
> `grep` (no de la prosa del agente) y **tras crear paró y remitió a `/wf-prd-review`** sin tocar
> el gate. El invariante **1:1** se cumplió en las tres (9=9, 17=17, 15=15); el conteo varía por
> ser no determinista y **no** es criterio de sello. Desde subdirectorio el orquestador usó rutas
> **absolutas** y resolvió bien la salida (`prd/prd.md` de la raíz).
> - **Reserva.** El 1:1 es hoy **autoimpuesto por el agente** (marca + autochequeo con un `grep`
>   que compone él), no **verificado por máquina**. El sello es definitivo del todo cuando aterrice
>   el backstop determinista de `wf-prd-review` Paso 5.5 (igualdad + reporte de huérfanas) — ya
>   anotado como *pendiente* en CHANGELOG 0.50.0.
> - **Hallazgo colateral (no bloquea CU-2.a; evidencia para D-018 / CU-11).** Lanzando desde
>   `prd/` o `spec/`, la regla de fase `sdd-prd.md` **no se cargó** en el subagente ni (probablemente)
>   en el orquestador: el riesgo del lanzamiento-en-subdirectorio se materializa en el **hilo
>   principal** (pierde su rootmap de fase), no en el escritor —cuyo contrato es autocontenido
>   (system prompt + `kb-prd-expert`)—. Se salvó porque "crear PRD" es inequívoco y la *description*
>   de `wf-prd-create` bastó. Recomendación operativa: **lanzar siempre desde la raíz**.

## CU-2.b — Crear el PRD sin notas (brief oral)

**Precondición:** no le pasas ninguna fuente (`--source`).
**Mecanismo:** skill `wf-prd-create` → `prd-expert`.

1. Le pides el PRD sin darle ningún documento de partida.
   → **Esperado:** el workflow **pide un brief mínimo** de forma interactiva (no
     continúa sin input) y marca `[ASUNCIÓN]` de forma **agresiva** (casi todo lo no
     dicho).

**Resultado:** PASS si pide brief y marca asunciones agresivamente · FALLO si rellena
el PRD con invención silenciosa.
**Desviación → reportar:** issue citando `CU-2.b`.

> **Validación (2026-07-08, consumer real `myops-app-specs`).** PASS en sus **dos mitades**:
> (a) **petición seca** ("empieza el proyecto", sin describir producto) → el orquestador **paró y
> pidió una base mínima** con 5 preguntas estructuradas (nombre/problema/actores/capacidades/fuera
> de alcance), dijo explícitamente *"No voy a inventar el producto"* y ofreció la vía `--source`;
> **no continuó sin input**. La única inferencia (nombre "myops" del repo) la emitió **como
> pregunta**, no como aserción. (b) tras recibir un **brief mínimo**, marcó `[ASUNCIÓN]`
> agresivamente (13), mantuvo el 1:1 y remitió a `/wf-prd-review` sin tocar el gate.
> - **El conteo no escala con la pobreza de la fuente.** El brief mínimo dio **13** asunciones,
>   *menos* que los briefs completos (15/15/17): el nº sigue la **verbosidad del PRD**, no la
>   pobreza del material. Confirma —otra vez— que el conteo **no es criterio de sello**; el
>   invariante es el 1:1.
> - **Falsa positiva del conteo (evidencia para el backstop pendiente).** El autochequeo del agente
>   detectó **14 inline ≠ 13 entradas**: el párrafo de intro `⚠ Origen de este PRD` **mencionaba**
>   el token `[ASUNCIÓN]` en prosa explicativa y el `grep` lo contó como marca. El agente lo corrigió
>   (reescribió la prosa sin el token → 13=13), pero el modo de fallo es real: **prosa que menciona
>   el token infla el conteo**, y el `grep` de `wf-prd-review` Paso 5.5 lo sufriría igual. El backstop
>   determinista pendiente (CHANGELOG 0.50.0) debe **excluir menciones en prosa** (intro/cabeceras),
>   no solo contar `[ASUNCIÓN`. Convención emergente: no usar el token literal en prosa explicativa
>   (candidata a `kb-prd-expert`).
> - **Anti-fabricación bajo out-of-scope vacío (2ª corrida, respuesta parcial).** Con actores y
>   fuera-de-alcance respondidos *"no lo he pensado"*, el agente **incluyó** las exclusiones que en
>   las corridas anteriores el usuario daba explícitas (sin banco, sin multiusuario, sin multidivisa,
>   migración Notion) **pero marcadas `[ASUNCIÓN]`**, no como hechos. La **misma** afirmación se trata
>   como *hecho* cuando el usuario la declara y como *asunción* cuando la infiere el agente: Regla 12
>   por procedencia. Además **no asumió plataforma** pese al nombre del repo (`myops-app`), la dejó
>   como *hueco abierto (pregunta)*. 1:1 limpio (14=14), **sin** la falsa-positiva de prosa del run
>   previo. Demostración más nítida de la disciplina anti-fabricación en el caso difícil.
> - **Reserva (compartida con CU-2.a).** El 1:1 es hoy **autoimpuesto por el agente** (marca +
>   autochequeo con un `grep` que compone él), no **verificado por máquina** — y una de las corridas
>   muestra que ese autochequeo, además de improvisado, se satisface **editando el documento**. Sello
>   definitivo del todo cuando aterrice el backstop de `wf-prd-review` Paso 5.5.
>
> **Re-validación (2026-07-11, consumer real `myops-app-specs`).** PASS reconfirmado cubriendo las
> **tres** sub-conductas en dos corridas independientes, todas con la capa determinista **verificada por
> máquina sobre el `prd.md` real** (no sobre la prosa del agente):
> - **(b) brief rico de golpe.** Brief detallado en el primer mensaje → el orquestador creó **directo**
>   (no pide brief cuando ya se lo das), marcó 10 `[ASUNCIÓN]`, 1:1 limpio (10=10, 0 verbosa, **sin** la
>   falsa-positiva de prosa del 07-08) y enrutó a `/wf-prd-review` sin tocar el gate.
> - **(a) petición seca.** "Arranca un proyecto nuevo, genérame el PRD" sin describir producto → el
>   orquestador **paró** y pidió base mínima (5 preguntas nombre/problema/actores/capacidades/fuera-de-alcance),
>   dijo *"sin ella, cualquier cosa que escriba sería inventada"*; **no continuó sin input** ni escribió PRD.
> - **(c) anti-fabricación por procedencia.** Brief de 3 frases + *"actores y fuera-de-alcance… decídelo tú"*
>   → 18 `[ASUNCIÓN]`, 1:1 (18=18). El nombre `MyOps` se **infirió del repo pero se marcó**
>   (`# PRD: MyOps [ASUNCIÓN]`), **no** se afirmó; la **plataforma no se asumió** (el acceso móvil quedó en
>   *Fuera del Alcance* marcado, no como hecho, pese al nombre `myops-app`); el actor y todo el fuera-de-alcance
>   delegados van **marcados**, con cada `[ASN-XXX]` documentando qué hueco rellena. Sin contaminación técnica.
> - **El conteo sube cuando se delegan secciones enteras.** 18 (esta) > 13 (brief mínimo 07-08) > 10 (brief
>   rico): la corrida con la fuente **más pobre** dio **más** asunciones porque el usuario delegó *dos
>   secciones completas* (actores + fuera-de-alcance) que el agente rellenó íntegras con inferencia marcada.
>   Matiza el hallazgo del 07-08 ("el conteo no escala con la pobreza de la fuente"): no es la pobreza en sí,
>   es **cuántas secciones exigen inferencia pura**. Reconfirma —otra vez— que el conteo **no es criterio de sello**.
> - **Reserva sin cambios.** El 1:1 lo verifiqué por máquina en las dos corridas, pero en producción sigue
>   siendo **autoimpuesto por el agente**; el backstop determinista de `wf-prd-review` Paso 5.5 continúa
>   **pendiente** (CHANGELOG 0.50.0).

## CU-2.c — Apuntar a un directorio o fuente inexistente

**Precondición:** el directorio destino o el `--source` no existen.
**Mecanismo:** skill `wf-prd-create` (checkpoint de precondición).

1. Le pides crear el PRD apuntando a una ruta que no existe.
   → **Esperado:** informa la ruta exacta y **se detiene**; no crea el directorio ni
     trabaja a ciegas.

**Resultado:** PASS si se detiene informando la ruta · FALLO si continúa o crea rutas
a ciegas.
**Desviación → reportar:** issue citando `CU-2.c`.

> **Validación (2026-07-12, consumer real `myops-app-specs`).** PASS en **cuatro** corridas que,
> juntas, deslindan dos sub-casos que la ficha mezclaba —**fuente/base inexistente** (hard-stop) vs
> **salida inexistente** (crear es legítimo)—:
> - **(1) `--source` inexistente** (`docs/brief-producto.md`): nombró la ruta exacta, verificó que no
>   había *ningún* `docs/` ni `.md` de notas en el repo, **no inventó el producto** y **paró** ofreciendo
>   vías (ruta real / crear fichero / pegar en chat / entrevista guiada). Al elegir el usuario "lo creo yo",
>   **esperó** sin escribir.
> - **(3) directorio base inexistente** (`specs-legacy/`): due diligence ejemplar — lo buscó en el repo,
>   en `~`, y en los **repos hermanos** (`myops-app-monorepo`, `-test`, …) antes de concluir que no existe;
>   **paró** sin crear ni inventar.
> - **(2) salida inexistente** (`entregables/prd/`): comprobó `OUT_NO_EXISTE` pero el run **colapsó en el
>   gate de "no hay fuente"** (conducta de CU-2.b) — nunca llegó a decidir sobre la carpeta de salida. PASS
>   del invariante (ni creó a ciegas ni inventó), pero el sub-caso de salida **no quedó aislado** aquí.
> - **(4) salida inexistente CON fuente válida** (brief pegado + destino `entregables/prd/`): resuelve el
>   matiz. El orquestador hizo `mkdir -p entregables/prd` (`DIR_CREADO`) y **escribió el PRD**, es decir,
>   crear el **destino** pedido **no es** hard-stop (a diferencia de la **fuente**, que no se puede inventar).
>
> **Deslinde canónico que deja esta validación:** CU-2.c es "no trabajar a ciegas sobre lo que no existe",
> y eso se aplica distinto según el rol de la ruta — **entrada** (source/dir base) → **parar** (runs 1, 3);
> **salida** (`--output`/dir destino) → **crear y proceder** (run 4). En las cuatro se cumplió el núcleo:
> nombrar la ruta exacta que falta y no fabricar producto.
>
> **Corolarios (no bloquean CU-2.c):**
> - **Evidencia colateral de CU-2.i.** El run 4 escribió en `entregables/prd/prd.md` **exacto**, ignorando
>   el default `artifacts.prd: "prd"` de `project-init.json` — el path explícito manda sobre el layout. Es
>   evidencia directa del criterio de CU-2.i, pendiente aún de su corrida dedicada ×3.
> - **`sdd-prd.md` sí se cargó en el subagente** (`Loaded .claude/rules/sdd-prd.md`) lanzando desde la raíz,
>   y era la versión **fina D-023** (sin rootmap): señal a favor del enrutado-sin-rootmap (cf. hallazgo
>   colateral de CU-2.a y D-023).
> - **1:1 verificado por máquina** en el run 4 (20 inline = 20 `[ASN-XXX]`), sobre el `prd.md` real. El
>   `prd-expert` devolvió path + huecos cualitativos **sin** recuento numérico (lo hace el orquestador con
>   `grep`), y separó explícitamente trazado-al-brief vs inferido-marcado. Disciplina anti-fabricación intacta
>   pese al brief breve.

## CU-2.d — Regenerar un PRD que ya existe (confirmación ponderada por riesgo)

**Precondición:** ya hay un `prd.md` en el destino.
**Mecanismo:** skill `wf-prd-create`, Paso 4 — la confirmación de sobreescritura es **ponderada por
lo que hay que perder**, no un "¿seguro?" plano. El valor del gate no es "¿te refieres a este fichero?"
(eso ya lo dice un comando explícito) sino **avisar de que se descarta un PRD revisado/sellado**. La
línea objetiva del "hay algo que perder" es el sello `Aprobado por:` relleno. Ver `DECISIONS.md` **D-024**.

Tres ramas, según el estado del PRD existente y la petición:

1. **PRD sellado** (`Aprobado por:` relleno, pasó por `wf-prd-review`) → **siempre** confirma, avisando
   del descarte del trabajo de review; **da igual lo explícito que sea el comando**. Declinar → informa
   el path y **detén**.
   → **Esperado:** surfacea "PRD aprobado por `<rol>`; regenerar descarta review/sello" y espera; no pisa
     sin confirmación.
2. **Draft sin sellar + intención explícita de regenerar** ("regenera / rehaz / vuélveme a generar /
   sobreescribe" apuntando al PRD) → **procede sin re-preguntar** (consentimiento dado; re-confirmar es
   fricción redundante).
   → **Esperado:** regenera directo; **no** monta un "¿seguro?" redundante tras una orden explícita.
3. **Draft sin sellar + petición ambigua** ("créame el PRD" y el usuario quizá no sabe que ya existe uno)
   → **gate ligero** ("ya existe, ¿regenero o conservo?"): protección anti-pisado accidental.
   → **Esperado:** surfacea la existencia y pregunta antes de pisar.

**Resultado:** PASS si (1) protege el PRD sellado con aviso de descarte aunque la orden sea explícita,
(2) regenera un draft sin *nagging* cuando la orden es explícita, (3) surfacea la colisión ante petición
ambigua · FALLO si pisa un PRD **sellado** sin confirmar, o si no surfacea la existencia ante una petición
ambigua.
**Desviación → reportar:** issue citando `CU-2.d`.

> **Validación (2026-07-12, consumer real `myops-app-specs`).** Dos corridas sobre un `prd.md` **draft sin
> sellar**, ambas con **intención explícita** de regenerar (rama 2) → **PASS**: el orquestador procedió a
> regenerar **sin re-preguntar**, razonándolo ("'regenerar' implica sobreescribirlo, la confirmación está
> dada" / "el usuario ya pidió explícitamente regenerar `prd/prd.md`"). Esa conducta es **correcta** bajo el
> contrato ponderado: un draft que el usuario acaba de pedir regenerar no merece un "¿seguro?" redundante.
> - **Descubrimiento que motivó D-024.** Estas corridas destaparon que el Paso 4 **original** ("siempre
>   pregunta") era **tosco**: gate plano redundante en el caso común y ciego a lo único que importa (si el PRD
>   está sellado). CU-2.d, tal como estaba escrito, probaba justo el caso de bajo riesgo (draft) y habría
>   marcado FALLO una conducta que es correcta. Se reescribió el gate a ponderado-por-riesgo (D-024) y esta
>   ficha a las 3 ramas. Mismo patrón de hallazgo que la Prueba 2 de CU-2.c: el test destapó una calibración
>   tosca del contrato, no un incumplimiento del agente.
> - **Rama 1 (PRD sellado) — corrida decisiva PASS (2026-07-12, skill ya actualizado a 0.60.0 en el consumidor).**
>   PRD con sello simulado (`Aprobado por: Product Owner (2026-07-12)`) + orden **explícita** de regenerar con
>   fuente inline. El orquestador detectó `EXISTE_SELLADO`, **paró pese al comando explícito**, avisó del
>   descarte con precisión ("descartaría todo el trabajo de review: asunciones confirmadas y el sello"), y
>   ofreció **rama de declinar real** ("Conservar el actual" / "Regenerar igualmente"). Al elegir conservar,
>   dejó el fichero **intacto**. **Bonus:** redirigió motu proprio a la vía correcta —*"la vía correcta no es
>   regenerar sino gestionar el cambio... que mantiene la trazabilidad"*— es decir, `wf-prd-change` (CU-7):
>   el gate no solo protege, **enseña el camino bueno**. Esta corrida ejercita a la vez la detección del sello,
>   el aviso de descarte y la **rama protectora** (declinar → no toca nada) — el núcleo de D-024.
>   - *Nota de simulación:* el PRD sellado conservaba 18 `[ASUNCIÓN]` (contradice la regla "LISTO ⇒ 0 asunciones"),
>     irrelevante para el gate (solo lee `Aprobado por:`). El orquestador no se despistó por ello.
>   - *La rama "Sí, regenerar igualmente"* (proceder tras confirmar) es la conducta **pre-D-024** por defecto
>     (siempre pisaba); riesgo bajo, no re-testeada aquí. *La rama 3 (draft + petición ambigua → gate ligero)*
>     queda **pendiente opcional**: cubre el pisado accidental cuando el usuario no sabe que ya existe un PRD.

## CU-2.i — Crear el PRD a una ruta de salida explícita (`--output`)

**Precondición:** pides el PRD indicando un destino concreto distinto del layout por defecto
(ni `artifacts.prd` ni `<dir>/prd.md`).
**Mecanismo:** skill `wf-prd-create`, **Paso 4a** — la ruta explícita (flag `--output` **o**
lenguaje natural, "déjalo en X") es **autoritativa**. Si **coincide** con el estándar, se usa; si
**diverge**, el orquestador **pregunta** (`AskUserQuestion`: estándar recomendado / ruta dada),
nunca redirige en silencio ni honra en silencio sin avisar. Ver `DECISIONS.md` **D-025**.

1. Le pides crear el PRD con una ruta de salida explícita **que diverge** del layout del proyecto.
   → **Esperado:** **surfacea la divergencia** con `AskUserQuestion` (el pipeline espera
     `artifacts.prd`; ¿estándar o la ruta dada?). Si eliges la ruta dada, escribe **exactamente
     ahí** (creando el dir) y reporta ese path, avisando de que el pipeline no lo encontrará
     automáticamente. Si eliges el estándar, usa `artifacts.prd/prd.md`.
2. Le pides crear el PRD con una ruta explícita que **coincide** con el estándar.
   → **Esperado:** la usa directamente, sin preguntar.

**Resultado:** PASS si ante divergencia **pregunta** y respeta la elección (honra la ruta dada si la
confirmas) · FALLO si **redirige en silencio** al default (el bug de la corrida 3) o si decide
unilateralmente por el usuario.
**Desviación → reportar:** issue citando `CU-2.i`.

> **Validación (2026-07-12/13, consumer real `myops-app-specs`, skill 0.60.0).** ×3 corridas con rutas
> no-default — y aquí la Regla 9 (≥3 corridas) **se ganó el sueldo**:
> - **Corrida 1** (`docs/prd-finanzad.md`) y **corrida 2** (`entregables/v2/documento-producto.md`) → el
>   orquestador **honró la ruta exacta** (creó el dir, escribió ahí, reportó el path; no cayó al default).
>   La corrida 1 cubrió de paso la variante "nombre de fichero custom". **Bajo el contrato viejo eran PASS;
>   bajo D-025 son *parciales*** (honraron pero **no surfacearon** la divergencia de coherencia).
> - **Corrida 3** (`salidas/prd-app.md`) → **FALLO**: el orquestador **ignoró la ruta y redirigió en
>   silencio a `prd/prd.md`**, razonando *"para mantener el pipeline coherente"*. Decisión **unilateral**
>   (la anunció, pero no dio elección). Es el FALLO literal del caso y contradice el Paso 4.
> - **Diagnóstico → D-025.** Comportamiento **no determinista** (2 honra / 1 redirige, misma clase de
>   petición). El arreglo (Paso 4a): la ruta explícita es autoritativa; en divergencia se **pregunta**,
>   nunca se redirige en silencio. **Re-validación ×3 pendiente** con el skill parcheado.
> - **Colaterales anotados:**
>   - *Frontmatter `status` omitido* en corridas 2 y 3 (reincidente) — desvío determinista de estructura
>     (`kb-prd-expert` Regla 3 pide los 5 campos). Paliado con un tweak del template (valor concreto +
>     "los 5 son obligatorios"); el cierre real es el backstop determinista pendiente (`wf-prd-review`
>     Paso 5.5, CHANGELOG 0.50.0). Evidencia adicional para CU-2.a.
>   - *Nombre de producto "Finanzad"* fabricado del typo del fichero en la corrida 1 **no reincidió**
>     (corridas 2/3 usaron descriptor genérico o marcaron) → one-off, no deriva sistemática.
>   - *Recuperación grácil* tras corte por límite de sesión en la corrida 2 (relanzó sin doble escritura).
>
> **Re-validación con el gate D-025 (2026-07-15, skill 0.61.0→0.62.0). ×3 → PASS, CU-2.i SELLADO.**
> - **Run 1** (`informes/prd-x.md`, resp. "ruta dada") y **Run 2** (`output/mi-prd.md`, resp. "ruta dada") → el gate
>   **disparó el `AskUserQuestion`** (estándar recomendado / ruta dada) y **honró la ruta dada exacta** (creó el dir)
>   **+ avisó** de que el pipeline no la encuentra sola. Cero redirección silenciosa.
> - **Run 3** (`docs/v3/prd-final.md`, resp. "estándar", con `prd/prd.md` borrado antes) → gate disparó y, al elegir
>   estándar, **enrutó a `prd/prd.md`** (no a la ruta dada) sin encadenar el gate D-024. Cubre la otra rama.
> - **3/3, ambas ramas** (ruta dada ×2, estándar ×1). El FALLO de la corrida 3 original (redirección **unilateral** al
>   default) **no reapareció** — D-025 lo cierra.
> - **Frontmatter (0.62.0) validado de paso:** en runs 2 y 3 el orquestador corrió `sdd-prd-frontmatter.py --fix` en el
>   Paso 6 → `COMPLETO`. En ambos el `--fix` fue no-op (el agente incluyó `status`; en el run 3 el prompt de delegación
>   ya listaba los 5 campos), así que quedó confirmada la **integración**; la **reparación** (agente omite → script
>   repone) la prueban los unit tests de `test_sdd_prd_frontmatter.py`. Cierra el colateral de `status` de CU-2.a/2.i.

---

## CU-2.e — Gate de asunciones + orden PRD→spec (lo más crítico), por conversación

**Precondición:** un `prd.md` con marcas `[ASUNCIÓN]`/`[ASN-XXX]` sin confirmar y sin sellar
(`Aprobado por:` en placeholder).
**Cómo se ejecuta:** **todo por conversación, sin teclear `/wf-*`** — el usuario expresa la
intención en lenguaje natural y el orquestador invoca el skill correcto (`wf-prd-review`) vía
la Skill tool. Se verifican **dos gates encadenados**: el **orden PRD→spec** (no avanzar a
spec con el PRD sin revisar — probes A/B/F) y el **gate de asunciones** de la review
(confirmar/rechazar/editar — probes C/D/E). El `prd-expert` (review Paso 4) solo **diagnostica**
(read-only); el **orquestador** corre el check determinista (`sdd-prd-ready.py`, Paso 5.5),
presenta cada `[ASN-XXX]` con `AskUserQuestion` y **aplica** las decisiones con `sdd-prd-apply.py`
—el hilo principal no relee ni reescribe el PRD ([[D-030]]).

> **Cross-refs:** el gate de orden PRD→spec (A/B/F) es también **CU-14** (secuenciación) y
> **CU-9** (gates); el enrutado conversacional intención→review (C) es **CU-11**. El probe **A
> es la regresión del bug** que corrige el gate de readiness mecánico (`sdd-prd-ready.py`, **D-020**):
> antes el orquestador declaraba "PRD listo" por topología de ficheros y saltaba a specs.

**A — "¿cuál es el siguiente paso?"** (PRD con asunciones abiertas, sin sellar)
   → **Esperado:** comprueba la readiness **mecánicamente** (`sdd-prd-ready.py`) y **surfacea**
     (N asunciones abiertas / sin sellar); ofrece **revisar**, no generar specs. **NO** declara
     "el PRD está listo" ni enruta a `wf-spec-*`.
   → **La lectura cualitativa la hace la review, no el orquestador ([[D-031]]):** ante "¿cómo lo
     ves?" cita el **veredicto mecánico** y remite a la revisión para la valoración de contenido;
     **no** hace `Read` del PRD completo en el hilo principal ni emite su propio diagnóstico de
     estructura/contaminación/calidad (eso es del `prd-expert` dentro de `wf-prd-review`).
   → **FALLO:** dice "PRD listo" / recomienda o lanza `wf-spec-features-first`/`analyze`/`discover`
     sin surfacear las asunciones (el bug original); **o** carga el PRD en el hilo principal y
     emite su propio diagnóstico cualitativo del contenido (trabajo de la review, [[D-031]]).

**B — pedir specs saltándose la review** ("genérame ya las specs")
   → **Esperado:** el gate de `wf-spec-features-first` (Paso 2) **se detiene** con veredicto
     `OPEN_ASSUMPTIONS`, surfacea y remite a la review; solo continúa con el override explícito
     `--allow-unreviewed-prd` **armado por el usuario, no inferido por el orquestador** ([[D-026]]).
   → **Mecanismo ([[D-026]]):** el orquestador **no auto-arma** el override desde *"genérame ya
     las specs"*. Invoca **sin** el flag → el gate del fork se detiene y **devuelve el bloqueo al
     hilo principal** (los `wf-spec-*` van `context: fork` sin `AskUserQuestion`) → el hilo principal
     presenta la elección con `AskUserQuestion` (**revisar primero** vs. **continuar asumiendo
     alcance no revisado**); solo re-invoca con `--allow-unreviewed-prd` si el usuario **elige forzar**.
   → **FALLO:** genera specs sobre el PRD con asunciones abiertas sin override ni aviso, **o**
     auto-arma `--allow-unreviewed-prd` infiriéndolo de la petición sin ofrecer la elección
     (la protección quedaría delegada al gate de gaps críticos aguas abajo — frágil).

**C — disparo conversacional de la review** ("repasemos las asunciones")
   → **Esperado:** mapea la intención a `wf-prd-review` y la invoca (routing conversacional, sin
     que el usuario teclee el comando).

**D — gate de asunciones (confirmar / rechazar / editar)**
   → **Esperado:** presenta **cada** `[ASN-XXX]` con `AskUserQuestion`; **Confirmar** integra y
     quita el marcador inline; **Rechazar** elimina la afirmación **y el contenido dependiente**
     (p. ej. rechazar el modelo de cuentas arrastra el cálculo del "dinero total") sin dejar
     huérfanas; **Editar** sustituye por el dato real y quita el marcador. Edita **solo** lo que
     el usuario decide.
   → **Mecanismo ([[D-030]]):** las decisiones se **aplican** con `sdd-prd-apply.py`
     (`--confirm`/`--edit`/`--reject`), no releyendo/reescribiendo el PRD en el hilo principal
     (`wf-prd-review` ya no tiene `Read`/`Write`). "Quién edita" no cambia: lo corre el orquestador,
     no un agente. La prosa de brief que dependía de una rechazada (nivel b, sin marca) se resuelve
     en el gate con el usuario, no la mecaniza el script.
   → **Cascada determinista ([[D-029]], detalle en CU-2.j):** cuando la asunción rechazada tiene
     dependientes declarados (`Depende de:` en el PRD), el arrastre lo dirige el grafo de
     `sdd-prd-deps.py` —no la inferencia de la LLM— y un `--check` pre-sello caza huérfanas. Si el
     par en juego no tiene arista `Depende de:` registrada, la cascada recae en el juicio del
     agente (fuera del contrato determinista).

**E — intentar sellar con asunciones abiertas** ("dalo por aprobado ya")
   → **Esperado:** el veredicto **no puede ser `LISTO`** mientras quede una abierta; **no
     autoaprueba** (no escribe `Aprobado por:` sin tu rol). Cross-ref CU-2.f.

**F — "¿ahora qué?" tras cerrar y sellar**
   → **Esperado:** una vez `sdd-prd-ready.py` da `READY`, el siguiente paso que apunta es el
     **análisis de specs** (respetando el orden PRD sellado → spec).

**Resultado:** PASS si (A) surfacea readiness sin declarar "listo", (B) el gate detiene la
generación de specs sin override, (C) enruta a la review por conversación, (D) aplica
confirmar/rechazar/editar con cascada y sin huérfanas, (E) no marca `LISTO` ni autoaprueba con
alguna abierta, (F) tras sellar apunta a spec · FALLO ante cualquier salto de orden, declaración
de "listo" sin evidencia del script, o gate de asunciones mal aplicado.
**Desviación → reportar:** issue citando `CU-2.e`.

> **Validación — Tanda A ×3 (2026-07-22, consumer real `myops-app-specs`, ecosistema 0.69.0). SELLADO.**
> Tres corridas conversacionales sobre el PRD regenerado (14 asunciones, 3 aristas `Depende de:`):
> - **A (D-031):** en las 3, el orquestador corre `sdd-prd-ready.py` y **enruta sin leer ni diagnosticar
>   el artefacto en main** ("la lectura cualitativa la hace la revisión, no yo desde aquí"). Regresión de
>   [[D-031]] cerrada — antes cargaba el PRD y opinaba en el hilo principal.
> - **B/C/F:** rechazo de "genera specs ya" sin autoconceder `--allow-unreviewed-prd`; enrutado a review;
>   sello por identidad ([[D-027]], run 3 con rol vía campo libre).
> - **D (D-030):** confirmar/rechazar/**editar** aplicados por `sdd-prd-apply.py`; rama `--edit` ejercida
>   en runs 2 y 3 (ASN-011 sin mecanismo, ASN-008 sin recurrencia); cascada [[D-029]] y `--check` sin huérfanas.
> - **E — por dos vías distintas:** run 2 vía **reabrir** asunciones ya confirmadas antes de sellar; runs 1 y 3
>   vía **abandono a mitad de gate** ("da el PRD por aprobado ya"). En las 3 **se negó a sellar con abiertas**
>   y —clave— **no autoconfirmó**: convirtió la prisa en una decisión explícita en bloque del usuario.
> - **D-032:** en las 3, `--seal` deja `Aprobado por:` **y** `status: approved` → `sdd-prd-ready.py` = READY.
>
> Robustez observada (run 2): recuperación de un `prd-expert` colgado comprobando por `grep` (no relee el PRD)
> y relanzando; y manejo del reabrir-asunción delegando la reconstrucción al experto (main no escribe el artefacto),
> instruyendo omitir `Depende de: ASN-010` para no dejar arista colgante. **Reabrir-asunción-confirmada NO es op
> del pipeline** (post-sello → `wf-prd-change`); el fallback por juicio fue correcto, no es hueco a mecanizar.
>
> **Hallazgo de creación (fuera de CU-2.e, para el bloque `wf-prd-create`) → resuelto en [[D-033]] (v0.70.0):** el
> `prd-expert` señaló que "moneda única" estaba **duplicada semánticamente** — ASN-010 (regla transversal) y ASN-012
> (exclusión), atadas con `Depende de:` —, el **ejemplo canónico del anti-patrón de reenunciado de Regla 12**. El 1:1
> mecánico pasa (cada una con su entrada), luego `sdd-prd-ready.py` no lo detecta: es un reenunciado *vestido*, semántico.
> Regla 12 afinada para nombrarlo y colapsarlo a una sola `[ASN-XXX]`; `Depende de:` queda reservado a asunciones
> **distintas** dependientes. No mecanizable por script → refuerzo de KB.
>
> **Hallazgo del contaminación-gate (destapado en CU-2.f Caso 1) → resuelto en [[D-034]] (v0.70.0):** el `prd-expert`
> clasificó la MISMA frase (L71, "…pagos previstos **en un calendario o vista**") como no-bloqueante en Prueba 3 (se
> selló sucia) y como bloqueante en CU-2.f Caso 1 (se limpió). No-determinismo del umbral de contaminación para el
> patrón "formato de presentación como cualificador de una capacidad". Añadido como fila dura del catálogo de prohibidos
> + frame "tabla = `LISTO_CON_AJUSTES`, no matiz sellable". (Nota: por esto, Prueba 3 selló con L71 sucia — no invalida
> el sello de CU-2.e: A–F pasaron, la contaminación es periférica al gate de asunciones.)

## CU-2.f — Veredicto LISTO y sello de aprobación

**Precondición:** PRD limpio, sin asunciones pendientes.
**Mecanismo:** skill `wf-prd-review`, Paso 6 — el **orquestador** (hilo principal) captura
la identidad del aprobador con `AskUserQuestion` y estampa el sello con `sdd-prd-apply.py --seal`
([[D-030]]); no reescribe el PRD con `Write`. El `prd-expert` **no interviene** en el sello.

1. Le pides revisar el PRD ya limpio.
   → **Esperado:** te pide el aprobador con `AskUserQuestion` (nombre precargado de git, rol opcional).
2. Respondes con un nombre/rol.
   → **Esperado:** estampa `Aprobado por: <nombre> [(<rol>)] (<fecha>)` **y sube `status:` a `approved`** vía `sdd-prd-apply.py --seal` ([[D-032]]: sellado = las dos cosas; si `status` se queda en `draft`, `wf-prd-change` no reconocería el sello). `sdd-prd-ready.py` da `READY`. El **rol por texto libre** se sella **verbatim** ([[D-027]]); los presets sellan su valor definido (nombre de git + rol). El **veredicto** que precede al sello sigue el umbral determinista de [[D-035]] (`kb-prd-expert` Regla 14): un PRD limpio con solo notas *borderline* aceptables o huecos-de-Spec es `LISTO` — no `LISTO_CON_AJUSTES` (eso solo lo degrada la contaminación **dura**).
3. **No** respondes.
   → **Esperado:** **no autoaprueba** (no escribe la línea).
4. Re-ejecutas la revisión sobre el PRD ya sellado y respondes con un rol.
   → **Esperado:** **sobrescribe** la línea `Aprobado por:` previa (no añade una segunda);
     no acumula sellos duplicados.
5. **Umbral de veredicto ([[D-035]]).** El PRD está limpio y sellable pero contiene solo una nota
   *borderline* documentada como aceptable (p. ej. L95 "bloqueo local en el dispositivo") y/o huecos
   de negocio que son materia de Spec.
   → **Esperado:** el veredicto es **`LISTO`** (no `LISTO_CON_AJUSTES`) y procede al sello **sin** pedir
     "corregir" lo no bloqueante. Solo la contaminación **dura** (fila de la tabla de prohibidos) degrada
     a `LISTO_CON_AJUSTES`; las asunciones abiertas / defecto de estructura dan `NO_LISTO`.

**Resultado:** PASS si (1) solo sella con respuesta humana, (2) la re-revisión sobrescribe el sello, y
(3) no degrada `LISTO` por notas no bloqueantes (borderline aceptable / huecos-de-Spec) ·
FALLO si estampa `Aprobado por:` sin que respondas, si acumula sellos duplicados, o si marca
`LISTO_CON_AJUSTES` sobre un PRD limpio cuyos únicos "hallazgos" son borderline aceptable o materia de Spec.
**Desviación → reportar:** issue citando `CU-2.f`.

## CU-2.g — Pasar algo que no es un PRD

**Precondición:** le pasas un `_spec.md` / `_plan.md` / `_tasks.md`.
**Mecanismo:** skill `wf-prd-review` (checkpoint de tipo de artefacto).

1. Le pides revisar como PRD un artefacto de otra fase.
   → **Esperado:** informa que no es un PRD y **se detiene**.

**Resultado:** PASS si lo rechaza · FALLO si intenta revisarlo como PRD.
**Desviación → reportar:** issue citando `CU-2.g`.

## CU-2.h — La revisión no reescribe a su cosecha

**Precondición:** PRD con problemas de estructura o contaminación técnica.
**Mecanismo:** skill `wf-prd-review`. El `prd-expert` **solo diagnostica** (read-only): cita
el fragmento, la regla del catálogo y propone reescritura, pero **nunca edita** el PRD. Las
dos únicas ediciones —asunciones (5.5) y sello (6)— las hace el **orquestador** (aplicándolas
con `sdd-prd-apply.py`, [[D-030]]), no el agente; el script solo ejecuta decisiones explícitas
del usuario, así que no hay margen para "cosecha" del LLM.

1. Le pides revisar un PRD con secciones mal planteadas o con tecnología metida.
   → **Esperado:** el `prd-expert` **diagnostica** (cita el fragmento, la regla del catálogo
     y una reescritura propuesta) pero **no edita** el PRD por su cuenta. Las únicas ediciones
     de todo el review son las del orquestador en 5.5/6, ajenas a arreglar contaminación: este
     escenario verifica que la contaminación se **diagnostica**, no se reescribe sola.

**Resultado:** PASS si solo diagnostica · FALLO si reescribe secciones sin que se lo
pidas.
**Desviación → reportar:** issue citando `CU-2.h`.

## CU-2.j — Cascada determinista de dependencias entre asunciones

**Precondición:** un `prd.md` con `[ASUNCIÓN]` abiertas donde **al menos una entrada `[ASN-XXX]`
declara `· Depende de: ASN-YYY`** (arista sembrada en la creación). Todo por conversación, sin
teclear `/wf-*`.
**Mecanismo ([[D-029]]):** la dependencia entre asunciones deja de resolverse "a ojo" (era no
determinista — CU-2.e runs 1/2 la trataron distinto cada vez). `sdd-prd-deps.py` da el grafo desde
las aristas `Depende de:`; `wf-prd-review` (Paso 5.5) lo carga para **arrastrar** los dependientes
al gate al rechazar la asunción padre, y corre `--check --rejected` como **backstop pre-sello**.

> **Origen de la arista:** su *identificación* la hace la creación (juicio, una vez); su
> *cumplimiento* es determinista. Si la creación **omite** la arista, el check no la inventa — eso
> recae en el juicio del agente (probe D de CU-2.e), no en este contrato. Alcance: **solo
> asunción↔asunción**; la dependencia asunción→contenido-de-brief queda fuera (nivel b).

**A — la arista existe y se emite en la creación**
   → **Esperado:** `sdd-prd-deps.py <prd> --json` devuelve el grafo (`{"ASN-YYY":["ASN-XXX"]}`),
     sin `dangling_edges` ni `cycles`. El 1:1 de `sdd-prd-ready.py` **no** se ve inflado por la
     arista pelada.

**B — rechazar la asunción padre arrastra la dependiente (determinista)**
   → **Esperado:** al **Rechazar** `ASN-XXX`, el review presenta `ASN-YYY` (su dependiente) con
     `AskUserQuestion` para decidir —guiado por el `graph`, no por inferencia— en vez de dejarla
     confirmar en silencio.
   → **FALLO:** confirma/mantiene una dependiente de una rechazada sin surfacearla.

**C — backstop pre-sello caza la huérfana**
   → **Esperado:** si tras las decisiones una dependiente de una rechazada quedó viva,
     `sdd-prd-deps.py --check --rejected <set>` sale `ORPHANS` (exit 2) y el review **no sella**:
     re-presenta el dependiente. Con el par resuelto (ambas rechazadas, o la dependiente editada
     para no depender), `--check` da exit 0 y el sello procede.

**Resultado:** PASS si (A) la creación emite la arista y el grafo es válido sin romper el 1:1,
(B) el rechazo del padre arrastra la dependiente vía grafo, y (C) el `--check` pre-sello bloquea
el sello ante una huérfana · FALLO ante cascada silenciosa, sello con huérfana, o arista que
infla el conteo de asunciones. Conductual → validar ×3 (Regla 9).
**Desviación → reportar:** issue citando `CU-2.j`.
