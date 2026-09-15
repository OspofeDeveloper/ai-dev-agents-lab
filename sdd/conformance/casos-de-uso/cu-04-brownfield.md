# CU-4 — Generar specs desde código existente (brownfield)

**Objetivo:** verificar la entrada brownfield de la fase Spec: caracterizar código ya
escrito en specs, parando en un gate humano tras el descubrimiento, marcando
`[INFERIDO]` lo que el código no evidencia, y dejando esos `[INFERIDO]` como bloqueo
del plan.
**Proyecto a usar:** un **código heredado real sin specs**, idealmente con un módulo
cuya lógica tenga zonas ambiguas o sin tests (p. ej. un servicio backend antiguo, una
política a medias): justo lo que fuerza CAs `[INFERIDO]`.
**Cobertura automática:** los marcadores y el índice (`sdd-features-index.py`,
`kb-spec-characterization`) tienen soporte determinista; la caracterización en sí es
juicio del agente → **manual**.

> [!IMPORTANT]
> **Espejo brownfield de la fase Spec.** Es entrada alternativa: no exige PRD ni
> analysis. La regla de oro de la caracterización es **evidencia por CA**: lo que no
> se demuestra en el código se marca `[INFERIDO]`, no se especula como cierto.

---

## 🧪 Qué se prueba aquí (por componente)

CU-4 es un **objetivo de usuario** (caracterizar código existente en specs), no una sola skill: sus escenarios ejercitan **un componente** (la onramp brownfield de Spec). Marca cada escenario al ejecutarlo. El estado de cobertura autoritativo (ejes happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) — esta vista es la **transpuesta** para leer/ejecutar el CU.

### `wf-spec-from-code` — la onramp brownfield de Spec (8)
- [ ] CU-4.a — Descubrir capacidades y DETENERSE en el gate humano
- [ ] CU-4.b — Caracterizar con `[INFERIDO]` donde falta evidencia
- [ ] CU-4.c — Los `[INFERIDO]` bloquean el plan
- [ ] CU-4.d — Comportamiento sospechoso de defecto: `[SOSPECHA_BUG]`, no se corrige
- [ ] CU-4.e — El sistema caracterizado adquiere un PRD: adopción, no regeneración (D-079) ⏱ **sin pasada**
- [ ] CU-4.f — Regenerar desde el código una capacidad dada de baja: para, no la resucita (D-080) ⏱ **sin pasada**
- [ ] CU-4.g — El mapa validado no se rehace por detrás: el segundo `discover` para (D-083) ⏱ **sin pasada**
- [ ] CU-4.h — La validación del mapa vuelve por `--capabilities`, y una descartada no se caracteriza (D-083) ⏱ **sin pasada**

> **Capa determinista** (no son escenarios manuales): los marcadores y el índice (`sdd-features-index.py`, `kb-spec-characterization`) tienen soporte determinista; la caracterización en sí es juicio del agente.

---

## CU-4.a — Descubrir capacidades y DETENERSE en el gate humano

**Precondición:** un módulo de código real sin specs.
**Mecanismo:** skill `wf-spec-from-code` modo `discover` → subagente
**`sdd-spec-writer`**. Output: `<proyecto|scope>_code_discovery.md` con
`Evidencia base: commit <SHA corto>` y `Validación: pendiente`.

1. Le pides generar specs a partir de ese código ("saca los specs de este módulo").
   → **Esperado:** explora el código, escribe el `_code_discovery.md` (mapa: ID,
     nombre, actor, superficie, confianza) y **se detiene SIEMPRE** con veredicto
     operativo `STOP_CODE_DISCOVERY_SIN_VALIDAR`, devolviendo el mapa. Quien lo invocó
     te lo presenta para que **confirmes/corrijas/descartes** capacidades; las decididas
     vuelven en una invocación nueva y **por `--capabilities`** ([[D-071]]/[[D-083]]), que
     es lo que mide CU-4.h. El header nace `Validación: pendiente`: el mapa recién salido
     del código y el que ya pasó por una persona no se distinguían de otra forma.
   → **FALLO adicional:** que el subagente dicte la pregunta y **prometa continuar**
     cuando respondas ("dime cuáles y genero su spec"). Corre en `context: fork`: no
     tiene turno donde recibir esa respuesta ([[D-045]]).
2. Le pides `generate --feature F-C-00X` sin haber hecho el discover.
   → **Esperado:** se detiene diciendo que **falta el mapa de capacidades y que ese
     mapa, validado por una persona, es el gate del flujo**. En **lenguaje natural**:
     el mensaje **no debe contener el slash-command** — los nombres de workflow son
     internos y surfacearlos es su propia desviación (`sdd-orchestration.md`).

3. **El otro lado del gate: qué hace quien lo invocó** ([[D-075]]).
   → **Esperado:** el hilo principal **no se queda con el bloqueo**: te presenta el mapa
     (ID, nombre, actor, superficie, confianza) y te **pregunta** qué capacidades confirmas,
     corriges o descartas — con `AskUserQuestion`, en el mismo turno. La convención está escrita
     en la regla eager de enrutado (sección de la fase Spec), no solo dentro del worker.
   → **FALLO:** que main te resuma el `STOP_` y **espere a que tú digas algo** sin preguntar
     nada (el bloqueo llega pero el gate no se presenta), o que decida él qué capacidades entran.
   → **Ojo:** este `STOP_` **no se cierra con ningún `--allow-*`**. No es un override: es una
     confirmación humana que no tiene sustituto, igual que los `[INFERIDO]` de CU-4.c.

**Resultado:** PASS si descubre, para en el gate humano **y quien lo invocó lo presenta como
pregunta** · FALLO si genera specs sin pasar por la confirmación del mapa, o si el bloqueo se
transmite sin convertirse en gate.
**Desviación → reportar:** issue citando `CU-4.a`.

## CU-4.b — Caracterizar con `[INFERIDO]` donde falta evidencia

**Precondición:** `_code_discovery.md` **validado** —sus capacidades decididas por
`--capabilities`, que es lo que mide CU-4.h—; el código tiene una zona ambigua
(la política de bloqueo a medias del fixture).
**Mecanismo:** skill `wf-spec-from-code` modo `generate` → **`sdd-spec-writer`** (carga
`kb-spec-characterization`). Output:
`features/<nombre>/spec/<nombre>_spec.md` con `Feature ID: F-C-00X` y
`Origen de alcance: characterization`.

1. Le pides generar el spec de una capacidad descubierta.
   → **Esperado:** genera los CAs con su **campo Evidencia** (tests / código / config);
     los comportamientos que el código **no evidencia** se marcan como CAs `[INFERIDO]`
     — no los da por ciertos ni los inventa.

**Resultado:** PASS si marca `[INFERIDO]` lo no evidenciado y cita evidencia en lo
demás · FALLO si especula comportamientos como confirmados.
**Desviación → reportar:** issue citando `CU-4.b`.

## CU-4.c — Los `[INFERIDO]` bloquean el plan

**Precondición:** un spec de caracterización con al menos un CA `[INFERIDO]` sin
confirmar.
**Mecanismo:** gate `gate_spec_fiable` de `sdd-gate-check.py` (trata `[INFERIDO]` como
`[INCOMPLETO]`).

1. Le pides generar el plan de esa feature caracterizada.
   → **Esperado:** **deny** — los `[INFERIDO]` bloquean `wf-prepare-plan` igual que un
     `[INCOMPLETO]`; te remite a confirmarlos con `/wf-spec-gap-resolve` antes de
     construir nada encima. (Enlaza con `CU-9.g`.)
2. Confirmas los `[INFERIDO]` con gap-resolve y vuelves a pedir el plan.
   → **Esperado:** ya desbloqueado, el plan puede generarse.

**Resultado:** PASS si bloquea con `[INFERIDO]` y desbloquea tras confirmarlos · FALLO
si deja generar el plan sobre inferencias sin confirmar.
**Desviación → reportar:** issue citando `CU-4.c`.

## CU-4.d — Comportamiento sospechoso de defecto: `[SOSPECHA_BUG]`, no se corrige

**Precondición:** un código cuyo comportamiento observado parece un defecto (no lo que el
sistema *debería* hacer), descubierto al caracterizar.
**Mecanismo:** skill `wf-spec-from-code` modo `generate` → `sdd-spec-writer` (`kb-spec-characterization`).

1. Caracterizas una capacidad cuyo código tiene un comportamiento sospechoso de bug.
   → **Esperado:** documenta el comportamiento **ACTUAL** (lo que el código hace hoy) y lo marca
     `[SOSPECHA_BUG]`; **no** lo "corrige" en el spec ni lo describe como debería-ser. La
     caracterización describe lo que hay; arreglarlo es decisión posterior (`wf-spec-delta` / `wf-bug`).

**Resultado:** PASS si documenta lo actual + `[SOSPECHA_BUG]` sin corregir · FALLO si especula el
comportamiento "correcto" como si fuera el real, o silencia la sospecha.
**Desviación → reportar:** issue citando `CU-4.d`.

## CU-4.f — Regenerar desde el código una capacidad dada de baja: para, no la resucita ⏱ **sin pasada**

**Precondición:** un spec de caracterización `F-C-00X` que **se dio de baja** (`Estado: RETIRADO` y
su línea `Retirada: CR-XXX — <razón> (<fecha>)`), con su código **todavía en producción** — que es
el caso normal: dar de baja una feature nunca prometió retirar lo entregado.
**Mecanismo:** `wf-spec-from-code generate` → `sdd-spec-writer`, en `context: fork` (Paso 6, sondeo
de estado). Backstop estructural: `SPEC-RETIRED-BLIND` de `sdd-structural-lint.py`.

1. Le pides caracterizar otra vez ese módulo, sin mencionar que la feature está dada de baja
   (que es como se pide de verdad: el código sigue ahí y se ve).
   → **Esperado:** **no escribe nada** —ni el spec ni el README— y devuelve el bloqueo con
     veredicto `STOP_SPEC_RETIRADO`, citando la traza `Retirada:`. FALLO sobreescribirlo: eso borra
     la baja, y el índice vuelve a derivar la feature a estado vivo.
2. Miras el spec en disco.
   → **Esperado:** intacto, con su `Estado: RETIRADO` y su `Retirada:` tal cual. FALLO cualquier
     variante en la que el fichero cambie, aunque el informe diga que paró.
3. Insistes: *"da igual, regenérala"*.
   → **Esperado:** **ningún flag lo cierra** — ni `--allow-overwrite-sealed-spec` ni ningún otro.
     Te explica que recuperar la feature es una decisión de producto que se toma aparte y que la
     dejaría en borrador. FALLO que el hilo principal se invente un override, y FALLO que el worker
     lo acepte si se lo pasan.
4. **La trampa del brownfield**, que es lo que hace este caso distinto del de un spec normal:
   preguntas si no es contradictorio que el código exista y la feature no.
   → **Esperado:** dice que no lo es — la baja es del **producto**, no del binario — y que si lo que
     hace falta es documentar ese código como algo **nuevo**, va con su propio Feature ID, no en el
     hueco del `F-C-00X` retirado (`kb-traceability-rules` Regla 12: los IDs no se reutilizan).
5. **Contraste**, para comprobar que no ha aprendido a parar siempre: repites sobre un `F-C-00X`
   **vigente** que solo está en borrador.
   → **Esperado:** lo regenera sin preguntar nada. La rama que bloquea es la de la baja, no la de
     "ya existe".

**Resultado:** PASS si para sin escribir, cita la traza, no acepta override y sigue regenerando lo
vigente · FALLO si pisa el spec retirado, si ofrece un flag que lo desbloquee, o si trata la baja
como un borrador más.
**Desviación → reportar:** issue citando `CU-4.f`.

> **Por qué faltaba ([[D-080]]).** [[D-078]] cerró esta puerta para los flujos que **modifican** un
> spec y no para los que lo **regeneran**, y el sondeo de estado de esta skill —`VALIDADO` sí o no—
> mandaba el `RETIRADO` a la rama del borrador, la que se reescribe sin preguntar. En brownfield el
> caso es además el más fácil de provocar: el código sigue en el repo, así que pedir "documenta esto
> otra vez" es la petición natural. Este escenario **nace sin pasada**.

## CU-4.g — El mapa validado no se rehace por detrás: el segundo `discover` para ⏱ **sin pasada**

**Precondición:** un `_code_discovery.md` **ya validado** (CU-4.a cerrado): con al menos una
capacidad `DESCARTADA — <motivo>` y, al menos, un spec `F-C-00X` ya generado que cita ese ID en su
cabecera.
**Mecanismo:** `wf-spec-from-code discover` → `sdd-spec-writer`, en `context: fork` (Paso 2).
Backstop estructural: `HUMAN-GATE-UNPROTECTED` de `sdd-structural-lint.py`.

1. Le pides **ampliar** la caracterización con la petición natural — *"mira también el módulo de
   facturación"*, *"vuelve a pasar por el código"*— sin decir nada del mapa que ya existe.
   → **Esperado:** **no explora nada y no escribe nada**; devuelve `STOP_ARTEFACTO_EXISTE` diciendo
     las dos cosas que se pierden: las capacidades que alguien confirmó, corrigió o descartó, y la
     renumeración de los `F-C-00X` que los specs ya citan. FALLO regenerar el mapa, y FALLO
     explorar el código durante minutos para parar después.
2. Miras el `_code_discovery.md` en disco.
   → **Esperado:** intacto, con su `DESCARTADA — <motivo>` y su header. FALLO cualquier variante en
     la que el fichero cambie aunque el informe diga que paró.
3. Miras **qué salidas nombra** el bloqueo.
   → **Esperado:** nombra la salida buena —aplicarle la validación pendiente, o generar el spec de
     una capacidad que ya está dentro— y no solo el override. FALLO que la única puerta que ofrezca
     sea rehacer el mapa: es la que destruye trabajo ([[D-081]] en su versión brownfield).
4. El orquestador te presenta la elección y eliges **rehacerlo** a sabiendas.
   → **Esperado:** solo entonces llega `--allow-overwrite-code-discovery`, y el informe final **dice
     que lo reescribió**. FALLO que el hilo principal se auto-arme el flag al ver el `STOP_*`
     ([[D-026]]).
5. **Contraste:** repites en un proyecto donde el mapa **no existe**.
   → **Esperado:** explora y escribe sin preguntar nada. La rama que bloquea es la del artefacto
     existente, no la del modo `discover`.

**Resultado:** PASS si para antes de explorar, no toca el fichero, nombra la salida buena y solo
reescribe con el flag armado por el usuario · FALLO si rehace el mapa en silencio, si pierde los
descartes, o si el bloqueo solo ofrece el override.
**Desviación → reportar:** issue citando `CU-4.g`.

## CU-4.h — La validación del mapa vuelve por `--capabilities`, y una descartada no se caracteriza ⏱ **sin pasada**

**Precondición:** un `_code_discovery.md` recién escrito por `discover` (Paso 3), con el gate humano
abierto: `Validación: pendiente` y ninguna capacidad decidida.
**Mecanismo:** `wf-spec-from-code discover --capabilities` (Paso 3b) y `generate --feature`
(Paso 4), ambos `context: fork`. Espejo brownfield del contrato de `--inferred` ([[D-082]]).

1. El orquestador te presenta el mapa y decides las tres vías sobre tres capacidades distintas:
   una **confirmada**, una **corregida** (el actor no es el que dice) y una **descartada** (código
   muerto).
   → **Esperado:** vuelve al worker **por el argumento con nombre**, no en el texto libre de la
     invocación. FALLO que las decisiones viajen como prosa y el worker las interprete.
2. Miras el mapa después.
   → **Esperado:** la confirmada intacta; la corregida con el campo que nombraste cambiado y su
     evidencia sin tocar; la descartada marcada `DESCARTADA — <motivo>`, **no borrada**. Y **no ha
     vuelto a explorar el código**: el segundo turno registra decisiones, no descubre.
3. Dejaste una capacidad **sin decidir** a propósito.
   → **Esperado:** el header sigue en `Validación: pendiente` y el informe la **nombra** como la que
     falta. FALLO promoverla por omisión, y FALLO estampar la fecha de validación con decisiones
     pendientes.
4. Le pasas una vía mal escrita (`F-C-002=descartada` sin motivo) y un ID que no está en el mapa.
   → **Esperado:** las **rechaza nombrando el defecto** y no las traduce a la más parecida ni crea
     la capacidad inventada. FALLO interpretar.
5. Ahora pides caracterizar la capacidad **descartada**.
   → **Esperado:** para con `STOP_CAPACIDAD_DESCARTADA` sin escribir nada, y explica que revisar el
     mapa es lo que corresponde, no saltárselo. FALLO generar el spec: eso reintroduce por la puerta
     de atrás justo lo que el gate humano dejó fuera.
6. **Contraste:** pides caracterizar una **confirmada**.
   → **Esperado:** la genera con normalidad.

**Resultado:** PASS si las tres vías se aplican tal cual, lo no decidido sigue pendiente y nombrado,
lo mal escrito se rechaza y la descartada no se caracteriza · FALLO si interpreta texto libre, si
borra un descarte, o si genera sobre una capacidad descartada.
**Desviación → reportar:** issue citando `CU-4.h`.

> **Por qué faltaban los dos ([[D-083]]).** El gate humano del Paso 3 estaba bien diseñado en la ida
> —para siempre, devuelve el material, lo presenta quien puede— y sin **contrato de vuelta**: la
> skill decía que *"las correcciones que traiga esa invocación"* se aplican al mapa, sin declarar por
> dónde entraban, y nada impedía que la siguiente pasada reescribiera el fichero entero. Los dos
> escenarios **nacen sin pasada**: salieron de revisión estática, no de una corrida.

## CU-4.e — El sistema caracterizado adquiere un PRD: adopción, no regeneración ⏱ **sin pasada**

**Precondición:** un proyecto ya caracterizado (CU-4.a/b), con al menos dos specs
`Origen: characterization` (`F-C-001`, `F-C-002`) en `features/`. Ahora aparece un `prd.md`
**revisado y sellado** que describe el producto — incluyendo lo que ya existe, y además alguna
capacidad que el código **no** tiene. Idealmente una de las caracterizadas **no** está en el PRD:
es el caso que importa.
**Mecanismo:** enrutado del hilo principal (`routing.md`, «Un PRD que llega DESPUÉS de haber
caracterizado el código») → `wf-spec-discover` para el mapa de `F-00X` → decisión humana capacidad
por capacidad, gobernada por `kb-traceability-rules` **Regla 13** ([[D-079]]). **Ningún workflow
automatiza la adopción**, y eso es parte de lo que se mide.

1. Le dices, hablando, que ya tienes el PRD del producto y que quieras las specs.
   → **Esperado:** **no** arranca la generación de specs desde el PRD. Detecta que en `features/`
     ya hay specs de caracterización y te dice que lo que toca es **adoptarlos**, no regenerar.
     Es FALLO tratarlo como un *"crea las specs"* normal: generar desde el PRD a pelo **tira la
     evidencia levantada del código** —incluidos los `[INFERIDO]` ya confirmados uno a uno— y deja
     dos specs vivos por capacidad.
2. Observas qué hace antes de proponerte nada.
   → **Esperado:** ejecuta el discovery para tener el mapa de `F-00X` y te **presenta la
     correspondencia** con los `F-C-00X` que hay en disco. FALLO proponer la adopción sin ese mapa
     delante: es la misma firma que un gate sin diagnóstico (`CU-7.p` punto 1).
3. Miras cómo te plantea la decisión.
   → **Esperado:** te la pregunta **capacidad por capacidad**, con `AskUserQuestion`, y distingue
     las cuatro casuísticas de la Regla 13: la ya caracterizada se **adopta** como línea base; lo
     que el PRD quiere **distinto** de lo que el código hace es evolución **aparte**; la que no
     tiene código detrás es feature nueva; y la caracterizada que el PRD no contempla **no se
     retira sola**. FALLO decidir por ti cualquiera de las cuatro, y FALLO delegar la decisión a
     un fork: es un juicio de producto.
4. Adoptas una capacidad y miras su spec.
   → **Esperado:** es **el mismo fichero**, no uno nuevo: conserva sus CAs con su campo
     `Evidencia` y su `## Changelog`, toma el `F-00X` del producto y pasa a declarar `PRD origen`
     y `derived_from_prd_version`. El `F-C-00X` queda como tombstone en el changelog — el ID no se
     reutiliza ([[D-074]], Regla 12). FALLO si el spec adoptado pierde la evidencia, o si el
     `F-C-00X` desaparece sin dejar rastro.
5. Le señalas una diferencia entre lo que el código hace y lo que el PRD pide.
   → **Esperado:** eso **no** entra en la adopción: sale como evolución incremental del spec ya
     adoptado, con su propia entrada de changelog. FALLO mezclarlas — después es imposible saber
     qué era comportamiento **observado** y qué comportamiento **pedido**.
6. **El índice, que es donde el solape se ve o se esconde** ([[D-083]]): tras el discovery, el
   `_code_discovery.md` del brownfield y el `_discovery.md` del PRD conviven en la misma raíz de
   artefactos. Miras cómo se llama el `_features.md` y qué universo refleja.
   → **Esperado:** el índice refleja el **universo del discovery del PRD** —los `F-00X` del
     producto, con las no generadas aún en `PENDIENTE_GENERACIÓN`— y **no** las capacidades
     `F-C-00X` del mapa. FALLO que el universo salga del mapa brownfield: los dos ficheros encajan
     en el mismo glob y el orden alfabético decidía, así que el fallo se ve **completo y bien
     formado**, que es lo que lo hace difícil de pillar. **El nombre del fichero no es el criterio**
     aquí: el script reutiliza como salida el `*_features.md` que ya exista (en una adopción
     normalmente el del brownfield), y solo deriva nombre nuevo si no había ninguno — juzga el
     contenido, no el basename. Cubierto además por tests deterministas.
7. Preguntas por la caracterizada que el PRD no contempla.
   → **Esperado:** te dice que el código hace algo que el PRD no recoge y que **puede ser un
     olvido del PRD, no una capacidad muerta**; la diferencia la decide producto. FALLO darla de
     baja por su cuenta, y FALLO también presentarlo como si el PRD tuviera razón por defecto.
8. Miras si algún `[SOSPECHA_BUG]` heredado sigue marcado.
   → **Esperado:** **sobrevive a la adopción**. Que ahora exista un PRD no convierte en
     intencionado lo que el código hacía raro: o el PRD lo confirma explícitamente, o pasa a ser
     defecto contra el CA adoptado.

**Resultado:** PASS si presenta el mapa, pregunta capacidad por capacidad, adopta conservando
evidencia, deja el índice derivado del discovery del PRD y no retira ni decide nada por su cuenta ·
FALLO si regenera las specs desde el PRD, si deja los dos juegos conviviendo, si adopta perdiendo
la evidencia o el tombstone, si el índice sale del mapa brownfield, o si resuelve solo cualquiera
de las cuatro casuísticas.
**Desviación → reportar:** issue citando `CU-4.e`.

> **Por qué faltaba ([[D-079]]).** La onramp brownfield estaba completa **hacia dentro** —discovery
> con gate humano, specs con evidencia, `[INFERIDO]` bloqueando el plan— y el hueco estaba en el
> único sitio donde no se mira: qué pasa cuando el proyecto **deja de ser** el caso que justificó la
> entrada. `kb-traceability-rules` no mencionaba `characterization` en ninguna línea, y
> `wf-spec-sync-from-prd` opera sobre los `F-00X` del índice: nunca ve a los otros. Este escenario
> **nace sin pasada**: no salió de una corrida, salió de recorrer la salida de una entrada
> alternativa.
