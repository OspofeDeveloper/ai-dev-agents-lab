---
name: wf-spec-discover
description: "Analiza un PRD e identifica features candidatas por cohesion funcional. Genera un _discovery.md con el mapa de features, scope por feature y shared models. No genera specs — solo el roadmap para ejecutar wf-spec-fast-track por feature."
when_to_use: "Activa en frases como 'identifica features del PRD', 'descubre las features', 'que features tiene este PRD', 'mapa de features', 'que features hay en este documento'. No activa ante una petición general de crear las specs ('crea las specs', 'genera las specs del PRD', 'features-first'): ese es wf-spec-features-first, que ya ejecuta el discovery por dentro."
argument-hint: "<prd_archivo.md> [--analysis <analysis.md>] [--allow-derived-scope-from-analysis] [--allow-overwrite-discovery]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-explorer
user-invocable: true
---

# Workflow: DISCOVER

Este workflow pertenece a la fase Spec y **requiere un PRD o documento de requisitos previo** como entrada. Si el usuario todavía no tiene ese artefacto, remítelo a la fase PRD antes de continuar.

Tu objetivo es leer un PRD y producir un mapa de features candidatas con su scope, sin generar ningún spec. Usa `kb-decompose-expert` para las reglas de identificación de features y shared models.

**Regla de oro:** No generas specs, no generas HUs, no generas CAs completos. Solo identificas features, validas que cumplen los 3 criterios, asignas shared models y mapeas qué parte del PRD corresponde a cada feature.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del PRD**: el primer argumento
- **Flag opcional**: `--analysis <path>` — path a un `_analysis.md` generado previamente por `/wf-spec-analyze`
- **Flag opcional**: `--allow-derived-scope-from-analysis` — permite continuar aunque el `_analysis.md` introduzca expansión funcional no consolidada todavía en el PRD. Sin este flag, el workflow se detiene y remite a `wf-prd-change`.

Si no hay argumento, informa al usuario:
> "Necesito el path del PRD del que quieres descubrir las features. Si ya hay un análisis previo respondido, dímelo y lo uso como contexto."

---

## Paso 2: Verificar el archivo

Verifica que el archivo existe; si no → informa con ruta exacta y detén. Si el nombre termina en `_spec.md`, `_plan.md` o `_tasks.md` → informa que este skill opera sobre PRDs, no sobre artefactos derivados del pipeline.

**Readiness del PRD (advisory, [[D-020]]).** Discover produce un mapa de features (no specs), así que **no bloquea**, pero surfacea si el PRD arrastra asunciones sin confirmar —el mapa se estaría construyendo sobre inferencias no validadas—:
```
!python3 .sdd/scripts/sdd-prd-ready.py "<path>"
```
Si el veredicto es `OPEN_ASSUMPTIONS`/`ASSUMPTION_MISMATCH`, avísalo en la salida ("el PRD arrastra N `[ASUNCIÓN]` sin confirmar; el flujo de generación se detendrá para que decidas si continuar"). Si falta el script, omite el aviso y continúa.

---

## Paso 3: Leer el contenido

Lee el archivo PRD en su totalidad.

**Si se proporcionó `--analysis`**, antes de usarlo **comprueba que es de la versión vigente
del PRD** ([[D-051]]):

```bash
!grep -nE '^version:' "<prd>"; grep -nE '^> \*\*Archivo origen\*\*' "<analysis>"
```

La cabecera del análisis declara `<path> (v<X.Y>)`. Si esa versión **no coincide** con el
`version:` del frontmatter del PRD → **DETENTE** y dilo: el mapa de features estaría
saliendo de un análisis que no conoce el PRD actual, y el `_discovery.md` acabaría
declarando `Status sync: in_sync` sobre una entrada obsoleta. Remite a regenerar el
análisis con `wf-spec-analyze`.

> **Se puede parar sin coste porque regenerar ya no destruye nada ([[D-051]]).** El Paso 7.1
> de `wf-spec-analyze` rescata las respuestas antes de sobrescribir y las devuelve después.
> Antes de eso, avisar de un análisis obsoleto obligaba a elegir entre seguir con datos
> viejos o perder las decisiones del usuario; ahora no hay dilema.
>
> Si el análisis **no declara versión** (generado antes de esta convención), no bloquees:
> avisa de que no se ha podido verificar y continúa. Un formato antiguo no es una
> desincronización probada.

Con la versión verificada: lee el `_analysis.md`. Extrae los gaps respondidos (donde el campo "Respuesta" no es `_(pendiente)_`). Las respuestas del cliente se usan como contexto adicional para:
- **Paso 5**: identificar features con mayor precisión (las respuestas pueden clarificar scopes ambiguos)
- **Paso 7**: asignar shared models (las respuestas pueden aclarar ownership)

Los gaps sin responder (`_(pendiente)_`) se ignoran en discover — no bloquean la identificación de features.

**Guardrail de gobernanza:** inspecciona si alguna respuesta resuelta del `_analysis.md` introduce señales de cambio de producto según `kb-product-change-governance`. Si detectas alguna: sin `--allow-derived-scope-from-analysis` → **DETENTE** e informa al usuario de formalizar el cambio con `wf-prd-change` o re-ejecutar con el flag; con el flag → continúa marcando el `_discovery.md` como `PRD + analysis respondido`.

---

## Paso 4: Identificar Requisitos Funcionales (RFs)

Escanea el PRD para extraer los requisitos funcionales:

- **Si el PRD tiene RFs numerados explícitamente** (ej: "RF-4 Control Horario"): usa esos IDs y títulos directamente.
- **Si el PRD tiene secciones funcionales sin numeración** (ej: "## Control Horario"): crea IDs RF-001, RF-002... basándose en los títulos de sección y marca en el output: `> Los IDs de RF son inferidos de las secciones funcionales del PRD — el documento original no los numera explícitamente.`
- **Si el PRD no tiene estructura clara**: agrupa el contenido por tema funcional, crea IDs RF sintéticos y añade la misma nota.

Registra para cada RF: ID, título y sección/párrafo del PRD donde aparece.

---

## Paso 5: Identificar features candidatas

Consulta `kb-decompose-expert` y aplica el algoritmo de identificación por cohesión funcional:

1. **Identifica todos los actores distintos** mencionados en el PRD
2. **Para cada actor, identifica sus objetivos principales**
3. **Agrupa por objetivo**: un objetivo principal = una feature candidata
4. **Nombra cada candidata** en kebab-case descriptivo (ej: `appointment-management`, `time-tracking`)

**Nota:** No existen HUs/CAs formales aún — razona sobre journeys anticipados y CAs derivables del contenido del PRD.

---

## Paso 6: Validar cada feature candidata

Para cada candidata, verifica los 3 criterios de `kb-decompose-expert`:

1. **Journeys independientes**: tiene al menos un journey anticipado que no depende de un journey de otra feature
2. **CAs derivables (mínimo 3)**: se pueden anticipar al menos 3 criterios de aceptación verificables a partir del contenido del PRD para esta feature
3. **Actor claro**: el actor principal y su objetivo están bien definidos

**Si una candidata no cumple los tres criterios:**
- Fusiona con la feature candidata funcionalmente más cercana
- Documenta la decisión de merge: candidata original, destino, y razón

---

## Paso 7: Shared models + ownership

Identifica modelos de dominio que aparecen en más de una feature candidata.

Para cada shared model, asigna ownership aplicando las reglas de `kb-decompose-expert` (en este orden):
1. **Creación explícita**: la feature cuyo scope del PRD describe la creación de la entidad
2. **Gestión completa**: la feature con operaciones CRUD completas
3. **Mayor cobertura**: la feature con más RFs que referencian la entidad
4. **Proximidad semántica**: la feature cuyo nombre es más cercano al modelo

### Ownership checkpoint

Si algún modelo tiene ownership ambiguo (empate tras aplicar los 4 criterios), **detente sin
escribir el discovery** y devuelve el bloqueo con veredicto operativo `STOP_OWNERSHIP_AMBIGUO`:
- la tabla de modelos ambiguos con sus candidatos
- qué criterio aplicaste y por qué hay empate
- qué cambia según quién sea el owner (es el dato que hace útil la decisión)

> **Por qué paras en vez de esperar ([[D-068]]).** Corres en `context: fork`: no tienes turno en el
> que quedarte aguardando a una persona, así que la instrucción que este paso tenía antes no era
> ejecutable. Quien te lanzó **ya sabe qué hacer con esto** — `wf-spec-features-first` tiene escrito
> que, si te detienes por shared models ambiguos, transmite tu mensaje y sostiene la resolución—, y
> es quien puede presentar la elección ([[D-026]]).

Si todos los modelos tienen owner claro → continúa directamente.

---

## Paso 8: Mapear scope PRD → Feature

Para cada feature validada, determina con precisión qué contenido del PRD le corresponde:

- **Scope (RFs)**: lista de IDs de RF que pertenecen a esta feature
- **Scope (secciones PRD)**: títulos de sección o párrafos del PRD que contienen la información relevante

Este mapeo es crítico: será usado por `wf-spec-fast-track` en modo scoped para filtrar el PRD y generar el spec de cada feature.

**Regla**: cada RF debe estar asignado a exactamente una feature. Si un RF abarca funcionalidad de dos features, descompón el RF en sub-RFs más específicos.

---

## Paso 9: Generar `_discovery.md`

Consulta `${CLAUDE_SKILL_DIR}/references/discovery_template.md` para la estructura exacta del artefacto.

**`Origen de alcance` es POR FEATURE y su criterio es binario ([[D-051]]).** No describe qué
entradas usaste tú; describe **de dónde sale el alcance de esa feature concreta**:

- **`PRD`** — todo lo que esa feature cubre está comprometido en el PRD. **Este es el caso
  normal**, incluso habiendo usado `--analysis`: leer el análisis para desambiguar no cambia
  el origen del alcance.
- **`PRD + analysis respondido`** — **solo** si el alcance de esa feature incluye algo que
  **únicamente** existe en una respuesta del análisis y **no** está en el PRD. Va siempre
  acompañado de un `Avisos de gobernanza` que **cita el `P-XXX`** responsable.

`Avisos de gobernanza` es `ninguno` salvo que esa feature arrastre alcance derivado (o una
excepción ya formalizada en el PRD / un change request referenciado).

**El nombre kebab-case de cada feature va en el idioma del documento de origen.** No es
cosmética: ese nombre **es el nombre del directorio** (`features/<nombre>/`) y aparece en el
índice, en los informes y en las rutas de todos los artefactos derivados. Medido (pasadas 9 y 11
de CU-3.a, mismo PRD en español): una dio `registro-de-movimientos`, `cuentas-y-tarjetas`; la otra
`movement-tracking`, `account-management`. Dos árboles incompatibles y cualquier documento que
cite una feature por su nombre queda obsoleto al regenerar el discovery.

> **Lo que escribes aquí lo lee una persona, y esa persona no invoca comandos.** El aviso
> cita el `P-XXX` responsable —eso es estado y es obligatorio— y explica **en lenguaje natural**
> qué habría que hacer con él: *"el usuario eligió continuar con este alcance derivado en vez de
> formalizarlo antes en el PRD"*. **No nombres el workflow** que formaliza el cambio.
>
> Medido (pasada 9 de CU-3.a): este campo cerró con *"…en vez de formalizarlo antes en el PRD con
> `wf-prd-change`"* teniendo la guía de fase cargada. El resto de la frase estaba bien; sobraban
> dos palabras.

> **Por qué esto estaba mal y por qué importa ([[D-051]]).** Antes decía *"como `PRD` o `PRD +
> analysis respondido` **según corresponda**"* sin definir el corte, y el campo admitía dos
> lecturas: "usé el analysis como entrada" vs "el alcance deriva de una respuesta". Medido en
> conformance: una pasada marcó **2 de 4** features y la siguiente marcó **las 8** sin haber
> alcance derivado en ninguna.
>
> Un marcador puesto a todas **no discrimina nada**: `Origen de alcance` existe para que una
> persona sepa de un vistazo qué features tienen el alcance sin consolidar, y con el valor
> puesto en bloque deja de responder a eso. Y de paso vuelve inverificable el probe de
> `CU-3.b`, que exige el contraste entre marcadas y no marcadas.
>
> **Regla de coherencia, autocomprobable:** `Origen de alcance: PRD + analysis respondido` y
> `Avisos de gobernanza: ninguno` **no pueden ir juntos** en la misma feature. Si no tienes un
> `P-XXX` que citar, el origen es `PRD`.

Determina el directorio de salida (regla de layout): si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.prd`, usa ese directorio (relativo a la raíz que contiene `.sdd/`); si no, usa el mismo directorio que el archivo de entrada. Nombre: nombre base del archivo de entrada + `_discovery.md`.
- Ejemplo (sin mapa): `docs/requisitos.md` → `docs/requisitos_discovery.md`

Antes de escribir, verifica si el archivo ya existe:
```bash
!test -f "<path_calculado>" && echo "EXISTE" || echo "NO_EXISTE"
```
- **`NO_EXISTE`** → sigue.
- **`EXISTE` sin `--allow-overwrite-discovery`** → **detente sin escribir nada** y devuelve el bloqueo a quien te
  lanzó, con veredicto operativo `STOP_ARTEFACTO_EXISTE`:
  > "Ya existe `<path>`. Regenerarlo puede **renumerar los `F-00X`**, y los specs ya generados los citan en su cabecera: la trazabilidad quedaría apuntando a otra feature. No lo he tocado."
- **`EXISTE` con `--allow-overwrite-discovery`** → sobreescribe y **dilo en tu informe final**.

> **Por qué aquí no preguntas ([[D-064]]).** Corres en `context: fork`, y un subagente no puede
> presentarle una elección al usuario: la instrucción que este paso tenía antes no era
> ejecutable ([[D-045]]). Paras y reportas; el gate lo presenta quien puede ([[D-026]]).

Escribe el artefacto generado en ese path.

---

## Paso 10: Informar al usuario

Tras escribir el archivo, informa: path generado, número de features, tabla resumen (Feature | Actor principal | RFs cubiertos | Shared models). Si hubo merges: listar candidatas fusionadas y razón. Si hay ownership ambiguo pendiente: listarlo. Si se usó `--analysis`: mencionar que se utilizó como contexto.

Siempre mostrar los siguientes pasos **como decisión, no como comando**: puede pedir que se **generen las specs de todas las features** (en paralelo), o **la de una feature concreta** citándola por su `F-00X`. El mapa que acabas de escribir es lo que necesita para elegir.
