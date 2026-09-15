---
name: wf-spec-from-code
description: "Ingeniería inversa de specs desde código existente (brownfield): descubre capacidades con evidencia (archivo:línea, rutas, tests) y genera specs de caracterización que describen lo que el sistema hace hoy. Entrada alternativa al pipeline cuando no hay PRD."
when_to_use: "Activa en frases como 'genera specs del código existente', 'documenta lo que hace este sistema', 'specs de este proyecto legacy', 'ingeniería inversa de specs', 'caracteriza este módulo'. No activa si existe un PRD como fuente (usa wf-spec-features-first), ni para cambiar comportamiento (usa wf-spec-delta sobre el spec de caracterización)."
argument-hint: "discover <path_codigo> [--scope <subdir>] [--allow-overwrite-code-discovery] | discover <path_codigo> --capabilities 'F-C-001=confirmada; F-C-002=descartada: <motivo>; F-C-003=corregida: <texto>' | generate <path_codigo> --feature <F-C-00X> [--discovery <file>] [--allow-overwrite-sealed-spec] | generate <path_codigo> --capability <nombre> --scope <subdir> [--allow-overwrite-sealed-spec]"
effort: high
allowed-tools: [Read, Write, Bash, Grep, Glob]
context: fork
agent: sdd-spec-writer
user-invocable: true
---

# spec-from-code — Specs de caracterización desde código

Tu rol: explorar el código con rigor de evidencia y redactar **solo** lo que esa evidencia sostiene. La regla central viene de `kb-spec-characterization`, que ya tienes cargada —eres `sdd-spec-writer`—: **un CA sin evidencia no existe**. Recolectas la evidencia y redactas con ella; no inventas para rellenar.

> **Por qué el modo `discover` también corre bajo `sdd-spec-writer` y no bajo el explorer
> ([[D-075]]).** Parece diagnóstico —produce un mapa, no un spec— y en cualquier otra vía de la
> fase lo sería. Aquí no: lo que recoges en `discover` **no es un diagnóstico, es el dossier de
> evidencia** con el que después se redacta, y la regla de esta onramp es que *un CA sin evidencia
> no existe*. Partirlo en dos agentes obligaría a re-leer el código entero en `generate` o a
> fiarse de punteros que no recolectaste tú — y la evidencia de segunda mano es justo lo que
> `kb-spec-characterization` prohíbe. El contrapeso de autor≠verificador no se pierde: **lo pone
> el gate humano** del Paso 3, que valida el mapa antes de que nadie escriba un spec.

---

## Paso 1: Parsear argumentos

- **Modo**: `discover` | `generate`
- `discover <path_codigo> [--scope <subdir>]` — explora el código y escribe el mapa (primer turno)
- `discover <path_codigo> --capabilities '<decisiones>'` — **segundo turno**: aplica al mapa ya escrito lo que una persona decidió sobre cada capacidad. **No re-explora nada**
- `generate <path_codigo> --feature <F-C-00X> [--discovery <file>]` — desde un discovery validado
- `generate <path_codigo> --capability <nombre> --scope <subdir>` — directo, una capacidad que el usuario ya nombra y acota (la validación humana es implícita)
- **`--capabilities '<decisiones>'`** (modo `discover`) — las decisiones **ya tomadas con el usuario**
  sobre el mapa, que es como vuelve la segunda mitad de este flujo ([[D-083]], espejo del
  `--inferred` de `wf-spec-gap-resolve`, [[D-082]]). Formato: entradas `F-C-00X=<vía>` separadas por
  `;`, con una de las tres vías exactas —`confirmada`, `descartada: <motivo>`,
  `corregida: <texto>`—. Ejemplo:
  `--capabilities 'F-C-001=confirmada; F-C-002=descartada: código muerto, ninguna ruta lo alcanza; F-C-003=corregida: el actor es admin, no usuario'`

  > **Por qué el contrato existe ([[D-083]]).** El Paso 3 para **siempre** para que una persona
  > confirme, corrija o descarte capacidades, y este paso decía que *"las correcciones que traiga
  > esa invocación"* se aplican al mapa — sin que hubiera **por dónde** vinieran: ni argumento que
  > las transportara ni formato que las nombrara. La vuelta del bloqueo quedaba a que el texto
  > libre de la invocación se pareciera lo suficiente, que es el modo de fallo que [[D-082]] ya
  > cerró para los `[INFERIDO]`. Una vía mal escrita **no se interpreta**: se rechaza nombrándola
  > (`descartada` sin motivo no es `descartada`), y una `F-C-00X` que no esté en el mapa tampoco
  > se inventa. Las capacidades que no aparezcan siguen **sin validar**.
- **Flag opcional** (modo `discover`): `--allow-overwrite-code-discovery` → autoriza reescribir un
  `_code_discovery.md` que ya existe. Sin él, si el mapa está en disco **te detienes** (Paso 2).
  Solo llega armado por quien te lanza, porque el usuario lo eligió en un gate ([[D-024]]/[[D-026]]).
- **Flag opcional** (modo `generate`): `--allow-overwrite-sealed-spec` → autoriza sobreescribir un spec de caracterización cuya cabecera declare `Estado: VALIDADO`. Sin él, si el spec de destino está sellado **te detienes** (Paso 6). Solo llega armado por quien te lanza, porque el usuario lo eligió en un gate ([[D-024]]/[[D-026]]).

Sin modo válido → informa el uso. `generate --feature` sin `_code_discovery.md` existente → detén:
> "No hay `_code_discovery.md`. Primero hay que **descubrir las capacidades del código** — ese mapa, validado por ti, es el gate de este flujo."

## Paso 2 (discover): Resolver el turno y proteger el mapa

Antes de explorar nada, calcula el path del mapa —`<nombre_proyecto|scope>_code_discovery.md` en el
directorio raíz de artefactos spec (regla de layout: `artifacts.spec` de `.sdd/project-init.json` si
está declarado; si no, el directorio actual)— y mira si ya está en disco:

```bash
!test -f "<path_calculado>" && echo "EXISTE" || echo "NO_EXISTE"
```

- **Vino `--capabilities`** → es el **segundo turno**: salta al Paso 3b. Si el mapa `NO_EXISTE`,
  detente e informa de que no hay mapa al que aplicar esas decisiones.
- **`NO_EXISTE`** → sigue al Paso 2b y explora.
- **`EXISTE` sin `--allow-overwrite-code-discovery`** → **detente sin explorar ni escribir nada** y
  devuelve el bloqueo a quien te lanzó, con veredicto operativo `STOP_ARTEFACTO_EXISTE`:
  > "Ya existe `<path>`. Ese mapa **lleva dentro trabajo humano**: las capacidades que alguien
  > confirmó, corrigió o descartó al validarlo. Rehacerlo desde el código las borra —vuelven todas
  > como candidatas sin validar— y puede **renumerar los `F-C-00X`**, que los specs de
  > caracterización ya generados citan en su cabecera. No lo he tocado."
- **`EXISTE` con `--allow-overwrite-code-discovery`** → reescribe y **dilo en tu informe final**.

> **Las dos salidas se nombran, no solo el override ([[D-081]]/[[D-083]]).** Quien recibe este
> bloqueo casi nunca quiere rehacer el mapa: quiere **aplicarle la validación** (eso es
> `--capabilities`, el Paso 3b) o **generar** el spec de una capacidad que ya está dentro. Un
> bloqueo que solo nombra el `--allow-overwrite-*` empuja a la única salida que destruye trabajo.
> Y ese flag es para un mapa que **aún no tiene specs colgando**: si ya los hay, rehacerlo hace
> exactamente el daño que describe el bloqueo.

> **Por qué aquí no preguntas ([[D-064]]).** Corres en `context: fork`, y un subagente no puede
> presentarle una elección al usuario ([[D-045]]). Paras y reportas; el gate lo presenta quien
> puede ([[D-026]]).

## Paso 2b (discover): Explorar el código y mapear capacidades

Explora el repo (limitado a `--scope` si se pasó). Busca **superficies de comportamiento observable**, en este orden:

1. **Entrypoints**: rutas HTTP/endpoints (routers, controllers, anotaciones), pantallas/views registradas, comandos CLI, jobs/crons, consumers de colas.
2. **Tests existentes**: nombres de suites y casos — son evidencia de máxima fuerza y delimitan capacidades reales.
3. **Modelos persistentes**: esquemas, migraciones, entidades — delimitan los datos que el sistema gestiona.
4. **Permisos/roles**: indican actores reales.

NO especules sobre código que no llegues a leer: una capacidad entra al mapa solo con al menos un puntero de evidencia.

Agrupa en capacidades funcionales (`F-C-001`, `F-C-002`...) con: nombre, actor (real del código o `usuario del sistema`), superficie (entrypoints), evidencia (paths concretos), nº de tests que la ejercitan, y una nota de confianza (`alta` = tests + código claro; `media` = código claro sin tests; `baja` = mucha inferencia → candidata a descartar o investigar).

## Paso 3 (discover): Escribir el mapa y DETENERTE (gate humano)

Escribe el mapa en el path que resolviste en el Paso 2. Incluye header con `Evidencia base: commit <SHA corto>` (`git rev-parse --short HEAD`) y `Validación: pendiente` — ese campo es el que distingue un mapa recién salido del código de uno que ya pasó por una persona, y lo estampa el Paso 3b.

**Detente SIEMPRE aquí**, con veredicto operativo `STOP_CODE_DISCOVERY_SIN_VALIDAR`. Devuelve el mapa (ID, nombre, actor, superficie, confianza) y el bloqueo:
> "El mapa de capacidades está en `<path>`: es lo que el código evidencia, y **nadie lo ha validado todavía**. Generar specs sobre un mapa sin validar caracteriza como comportamiento lo que puede ser código muerto o una lectura equivocada. No he generado ninguno. Lo que falta es que una persona confirme, corrija o descarte capacidades — y eso lo presenta quien me invocó."

**No esperes respuesta**: corres en `context: fork` y no tienes turno donde recibirla ([[D-045]]); el gate lo presenta quien puede preguntar ([[D-026]]/[[D-064]]). Cuando vuelvan con las capacidades decididas, llegarán como una invocación nueva — y **por el argumento con nombre**, no en el texto libre: `discover <path_codigo> --capabilities '<decisiones>'` ([[D-083]]). Dilo así en el bloqueo, para que quien lo presente sepa por dónde devolverte lo que decida.

## Paso 3b (discover): Aplicar la validación humana al mapa

Llegas aquí **solo** con `--capabilities`, y con el mapa ya en disco. **No explores el código**: este
turno no descubre nada, registra lo que una persona decidió. Sobre el mapa existente, entrada por
entrada:

- **`F-C-00X=confirmada`** → la capacidad queda validada tal cual. No reescribas su contenido.
- **`F-C-00X=corregida: <texto>`** → aplica la corrección **al campo que el texto nombra** (actor,
  nombre, superficie, scope). Es una edición quirúrgica, no una re-redacción de la entrada, y la
  evidencia recolectada no se toca: sigue siendo la del commit del header.
- **`F-C-00X=descartada: <motivo>`** → márcala `DESCARTADA — <motivo>`. **No la borres**: un
  descarte razonado es el resultado más valioso de este gate, y borrarlo hace que la siguiente
  pasada vuelva a proponerla como si nadie la hubiera mirado.

Reglas de rechazo, sin interpretación ([[D-082]]):

- una `F-C-00X` que **no está en el mapa** no se crea: repórtala como no aplicada;
- una vía que no es una de las tres exactas no se traduce a la más parecida —`descartada` sin
  motivo, o `corregida` sin texto, se rechazan nombrando el defecto—;
- las capacidades del mapa que **no aparecen** en `--capabilities` siguen **sin validar**: no las
  promuevas por omisión.

Actualiza el header a `Validación: <YYYY-MM-DD>` **solo si** no queda ninguna capacidad sin decidir;
si quedan, déjalo en `pendiente` y **nómbralas** en tu informe: son las que seguirán bloqueando.
Informa de lo aplicado (confirmadas, corregidas, descartadas), de lo rechazado y de lo que falta.

## Paso 4 (generate): Recolectar el dossier de evidencia

**Antes, comprueba que la capacidad sigue viva en el mapa** (modo `--feature`, [[D-083]]):

```bash
!sed -n '/F-C-00X/,/^$/p' "<path_del_code_discovery>" | grep -c 'DESCARTADA'
```

Si la entrada está marcada `DESCARTADA`, **detente sin escribir nada** y devuelve el bloqueo con
veredicto operativo `STOP_CAPACIDAD_DESCARTADA`:
> "`F-C-00X` está **descartada** en el mapa de capacidades (`DESCARTADA — <motivo>`): una persona
> la miró y decidió que no es una capacidad del sistema. Caracterizarla ahora reintroduce por la
> puerta de atrás lo que ese gate dejó fuera. No he generado nada. Si la decisión fue equivocada,
> lo que corresponde es **revisar el mapa**, no saltárselo."

Un descarte es una decisión humana registrada, igual que una baja de feature: el flujo que la
ignora produce un artefacto con pinta de correcto ([[D-080]] en su versión brownfield).

Para la capacidad elegida, relee a fondo su superficie declarada en el discovery (o el `--scope` en modo directo):

- entrypoints completos (firma, validaciones, respuestas de error)
- flujo principal y ramas observables (condicionales con efecto visible)
- tests que la ejercitan (literal: qué afirman)
- modelos/esquemas implicados
- reglas de autorización

Construye un **dossier**: lista de comportamientos observados, cada uno con su puntero (`archivo:línea`, `test path::nombre`). Lo que deduzcas sin observación directa va en una sección separada `INFERIDOS` con la razón de la inferencia. No mezcles.

## Paso 5 (generate): Redactar el spec de caracterización

Redáctalo **tú**. `sdd-spec-writer` es el `agent:` de tu frontmatter, así que ya corres con su
contexto y sus KBs: pedirle a ese agente que lo escriba te forkearía en un **clon tuyo** —un
envoltorio que solo re-emite el reporte del de abajo ([[D-044]])—. La norma de la fase lo dice
sin ambigüedad: una `wf-*` con `context: fork` **hace su trabajo y reporta; no delega**
(`kb-sdd-creation-guide`, "Regla de resolución de agentes").

Aplica `kb-spec-characterization` estrictamente:

- **Header obligatorio**: `Origen: characterization`, `PRD origen: N/A`, `Evidencia base: commit <SHA>`.
- **Cada CA con su campo `Evidencia`**, tomado del dossier del Paso 4 (`archivo:línea`, `test path::nombre`).
- **Los comportamientos del bloque `INFERIDOS`** entran como CAs `[INFERIDO]` con su `Confirmación pendiente`.
- **No añadas NINGÚN comportamiento que no esté en el dossier**, ni para completar una simetría aparente.
- **Comportamiento sospechoso de defecto** → documenta lo actual y márcalo `[SOSPECHA_BUG]`; no lo "arregles" en el spec.
- El **contexto** (actor, superficie, modelos) sale del discovery, no de tu criterio.

## Paso 6 (generate): Escribir artefactos

Layout estándar (mismas reglas que `wf-spec-fast-track`):

1. **Spec**: `<raíz_spec>/features/<nombre>/spec/<nombre>_spec.md` (feature plana legacy existente: en su raíz). El header declara `> Feature ID: F-C-00X` y `> Origen de alcance: characterization` — el índice los deriva de ahí.

   **Resuelve el path existente y mira su estado antes de escribir ([[D-024]]/[[D-062]]/[[D-080]])** — pisar un borrador, pisar un spec validado y pisar una feature **dada de baja** son tres cosas distintas. **Resuelve primero el layout**: mirar el estado sobre un path sin resolver deja sin detectar un spec sellado en plano legacy y lo pisa ([[D-067]]).

   ```bash
   !python3 .sdd/scripts/sdd-resolve-path.py find spec "<raíz_spec>/features/<nombre>/spec/<nombre>_spec.md"
   !e=$(sed -nE 's/^[[:space:]]*[-*>]?[[:space:]]*\*{0,2}Estado:?\*{0,2}[[:space:]]*:?[[:space:]]*(BORRADOR|VALIDADO|RETIRADO).*/\1/p' "<path_que_devolvio>" | head -1)
   case "$e" in RETIRADO) echo RETIRADO ;; VALIDADO) echo SELLADO ;; *) echo DRAFT ;; esac
   ```

   Un spec que no existe (o sin campo `Estado:`) sale como `DRAFT`, que es la rama correcta: no hay nada que perder.

   - **`RETIRADO`** → **detente sin escribir nada** y devuelve el bloqueo con veredicto operativo `STOP_SPEC_RETIRADO`. **Ningún flag lo cierra** ([[D-078]]/[[D-080]]): la capacidad está fuera del producto y regenerar su spec desde el código la devolvería viva sin `CR` y sin gate. Que el código **siga ahí** no la reactiva — dar de baja una feature nunca prometió retirar lo entregado:
     > "El spec de caracterización de `<nombre>` existe pero la feature está **dada de baja** (`Estado: RETIRADO`, `<traza Retirada:>`). No lo he tocado. Que el código siga en producción no la devuelve al producto: eso se decide aparte, y la deja en borrador pendiente de validar. Si lo que hace falta es documentar ese código como algo **nuevo**, va con su propio Feature ID, no en el hueco de esta."
   - **`DRAFT`** (o no existe) → reescribe en su ubicación actual y sigue.
   - **`SELLADO` sin `--allow-overwrite-sealed-spec`** → **detente sin escribir nada** y devuelve el bloqueo con veredicto operativo `STOP_SPEC_SELLADO`:
     > "El spec de caracterización de `<nombre>` ya existe y está **validado** (`Estado: VALIDADO`) en `<path>`. Regenerarlo desde el código descarta el trabajo de validación —incluidos los `[INFERIDO]` que ya se confirmaron uno a uno—. No lo he tocado. Si el usuario quiere rehacerlo desde cero igualmente, relánzame con `--allow-overwrite-sealed-spec`. Si lo que quiere es **reflejar un cambio de comportamiento**, no hace falta rehacerlo: se aplica ese cambio sobre el spec existente y su validación se reabre en vez de descartarse — dile que te lo pida y lo enrutas tú."
   - **`SELLADO` con `--allow-overwrite-sealed-spec`** → reescribe y **dilo en el Paso 7**. El spec nuevo nace en `Estado: BORRADOR`.

   > **Por qué aquí no preguntas.** Corres en `context: fork`, y un subagente **no puede presentarle una pregunta al usuario**: la instrucción anterior —*"pregunta antes de regenerar"*— **no era ejecutable** ([[D-045]]). Paras y reportas; el gate lo presenta quien puede ([[D-026]]).

2. **README** de la feature en su raíz, con `Origen de alcance: characterization (código, commit <SHA>)`.
3. **`_features.md`**: NO lo escribas a mano (es un índice generado). Tras escribir el spec, regenéralo desde la raíz del proyecto (el directorio que contiene `.sdd/`):

   ```
   python3 .sdd/scripts/sdd-features-index.py <raíz_spec>
   ```

   Sin discovery (caso brownfield típico), el script construye el índice solo desde los specs presentes — la feature de characterization aparece con su `F-C-00X` y estado derivado de sus marcadores (un `[INFERIDO]` → BLOQUEADA). Si falta el script:
   > "⚠ Falta `.sdd/scripts/sdd-features-index.py`. Re-ejecuta la instalación del ecosistema (`install.sh`) para reponer los scripts de enforcement. El índice `_features.md` no se ha regenerado."

## Paso 7: Informar

- Paths generados y nº de CAs por nivel de evidencia (tests / código / config / `[INFERIDO]`).
- **Los `[INFERIDO]` bloquean el paso a planificación** (los gates los tratan como `[INCOMPLETO]`): el siguiente paso es **confirmarlos uno a uno con el usuario**, que es lo que desbloquea el spec.
- Si hay `[SOSPECHA_BUG]`: listarlos — decisión de producto pendiente: se mantiene el comportamiento tal cual, o se cambia. Descríbeselo como acción que puede pedirte, **sin nombrar el workflow** que lo hace.
- Si el proyecto no tiene tests: recomienda characterization tests para los CAs de mayor riesgo antes de refactorizar.
