---
name: wf-spec-analyze
description: "Recopila las decisiones de negocio que necesitan los Specs desde un PRD vigente: mapea que elementos del Spec saldran del PRD, detecta contaminacion tecnica y formula preguntas concretas. Genera un _analysis.md."
when_to_use: "Activa en frases como 'prepara los inputs para los specs', 'que decisiones de negocio faltan para los specs', 'analiza este PRD para empezar los specs', 'genera el analisis previo al spec'."
argument-hint: "<archivo.md> [--allow-overwrite-analysis]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-explorer
user-invocable: true
---

# Workflow: ANALYZE

Este workflow pertenece a la fase Spec y **requiere un PRD o documento de requisitos previo** como entrada. Si el usuario todavía no tiene ese artefacto, remítelo a la fase PRD antes de continuar.

Tu objetivo es **recopilar las decisiones de negocio que los Specs necesitarán** a partir de un PRD vigente. No auditas el PRD ni le buscas defectos funcionales por deporte: el PRD ya hizo su trabajo en la fase anterior y, según `kb-prd-expert`, no tiene por qué contener HUs, Journeys, CAs ni Checklist — esos elementos pertenecen al Spec y se generarán después.

Usa `kb-spec-expert` para aplicar los 3 checks. El Check 1 mapea qué elementos del Spec se generarán a partir del PRD; el Check 2 detecta contaminación técnica (única condición que sí justifica retocar el PRD dentro del propio analyze); el Check 3 evalúa la testabilidad si el PRD ya tuviera CAs formales.

**Regla de oro:** Nunca rellenas huecos funcionales. Si algo no está definido o es ambiguo, lo marcas con `_(pendiente)_` en el campo "Respuesta" del gap (consulta `kb-gap-conventions` para el formato exacto) y formulas una pregunta concreta. El cliente decide, tú detectas. Si la respuesta pendiente realmente encubre un cambio de alcance, prioridad o reglas de negocio, debes remitir a `wf-prd-change`.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del archivo a analizar.

Si no hay argumento, informa al usuario:
> "Necesito el path del PRD o documento de requisitos que quieres analizar."

---

## Paso 2: Verificar el archivo

Verifica que el archivo existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

Si el nombre termina en `_spec.md`, `_plan.md` o `_tasks.md` → informa:
> "Este archivo parece un artefacto posterior del pipeline SDD. El análisis previo opera sobre PRDs o documentos de requisitos previos a Spec."

**Readiness del PRD (advisory, [[D-020]]).** Analyze solo produce un `_analysis.md` (no genera specs), así que **no bloquea**, pero **sí surfacea** las asunciones sin confirmar del PRD —la red que la fase PRD promete pero que este análisis, por sí solo, no resolvía—:
```
!python3 .sdd/scripts/sdd-prd-ready.py "<path>"
```
Si el veredicto es `OPEN_ASSUMPTIONS`/`ASSUMPTION_MISMATCH`, inclúyelo en el informe (Paso 8) como aviso: "el PRD arrastra N `[ASUNCIÓN]` sin confirmar; conviene revisarlas y cerrarlas antes de generar specs — este análisis no las resuelve". Si falta el script, omite el aviso y continúa.

---

## Paso 3: Leer el contenido

Lee el archivo en su totalidad.

---

## Paso 4: Mapear elementos del Spec y detectar problemas reales

### Check 1 — Mapeo de elementos del Spec a generar
Para cada uno de los 8 elementos del Spec (consulta `kb-spec-expert` para su definición), determina su estado de partida en el PRD:

- Actores
- Historias de Usuario (Como/quiero/para que)
- Recorridos de Usuario
- Resultados y Éxito
- Instrucciones Inambiguas (incluyendo tabla de destinos de navegación si hay flujos de navegación)
- Criterios de Aceptación (GIVEN/WHEN/THEN)
- Checklist de Validación
- Fuera de Alcance

Para cada uno, indica si ya viene en el PRD, si se generará entero durante la fase Spec, o si está parcial y se completará en Spec. **Esto no es un score de defectos**: lo normal en un PRD es que HUs formales, Journeys paso a paso, CAs en GIVEN/WHEN/THEN y Checklist no estén — pertenecen al Spec, no al PRD (`kb-prd-expert` Regla 9). El propósito de este check es dar visibilidad de qué se va a generar después, no señalar carencias.

### Check 2 — Pureza (única vía legítima para tocar el PRD)
Consulta `prohibited_items.md` y `error_patterns.md` del skill `kb-spec-expert` antes de emitir tu veredicto. Para cada frase problemática:
- Cita el fragmento exacto
- Explica por qué es técnico
- Propón la reescritura funcional

**Importante**: ésta es la **única** condición que justifica devolver el documento a la fase PRD. Si el Check 2 está limpio, el PRD se considera correcto tal cual está y se procede con los Specs, incluso si los Checks 1 o 3 reportan elementos ausentes (es lo esperable).

### Check 3 — Testabilidad
Si el PRD ya incluye CAs formales (poco habitual en un PRD), cada uno debe ser verificable objetivamente e independientemente, tener GIVEN/WHEN/THEN completo, y referenciar su HU padre. Los que no cumplan estos criterios deben aparecer con su reformulación sugerida. Si no hay CAs en el PRD, indica `NO_APLICA` — los CAs se generarán en la fase Spec.

---

## Paso 5: Formular gaps funcionales → preguntas [P-XXX]

Si encuentras información funcional ausente o ambigua (no técnica), formúlala como pregunta para el cliente. Cada gap debe ser:
- Concreto (no "¿qué más falta?")
- Sin opciones inventadas (el cliente decide)
- Neutro: no empujes hacia una solución que ya expanda el producto

Consulta `kb-gap-conventions` para el formato de IDs `[P-XXX]`, las definiciones de severidad `[CRÍTICO]` / `[INFORMATIVO]`, el marcador `_(pendiente)_` y el formato exacto de cada gap en el informe.

**Importante:** si el problema detectado no es una ambigüedad sino una contradicción entre el PRD vigente y una decisión nueva de negocio ("esto pasa de fase 2 a MVP", "se elimina esta exclusión", "ahora otro actor puede hacerlo"), no lo reduzcas a un gap normal. Márcalo explícitamente como **requiere change request** y remite a `wf-prd-change`.

**Importante 2 — posibles respuestas que expanden capacidad:** detecta también cuándo la propia pregunta puede desembocar fácilmente en una expansión funcional no comprometida en el PRD. En esos casos:

- añade el marcador advisory `[PUEDE_REQUERIR_CR]`
- redacta la pregunta de forma neutra, sin presentar como opciones "normales" soluciones expansivas
- deja claro que, si la respuesta introduce una entidad persistente, un catálogo reutilizable, una nueva granularidad funcional o un flujo adicional de usuario, deberá reevaluarse con `kb-product-change-governance`

Ejemplo de mala formulación:
- "¿catálogo persistente o texto libre?"

Mejor:
- "¿cómo se identifica este elemento en el producto actual?"
- y, si la respuesta introduce catálogo persistente o gestión reutilizable, escalar a `wf-prd-change`

### Cómo se redacta la prosa del gap: el ID es contrato, la sigla suelta es jerga

Los campos `Contexto`, `Problema` y la pregunta al cliente **los lee una persona** —normalmente de
producto, no del pipeline— y son los que deciden si sabe qué contestar. Ahí rige la norma de la
guía de fase ("lo que escribes en un artefacto lo lee una persona"), aplicada al vocabulario:

- **Los IDs se quedan siempre, tal cual**: `CA-001`, `HU-003`, `RF-006`, `P-011`. Son estado y los
  parsean los scripts (`sdd-seal.py` sella los encabezados `### CA-XXX`; `sdd-features-index.py`
  deriva la trazabilidad RF→HU→CA). Todas esas regex exigen el `-NNN`.
- **Las siglas sueltas y el vocabulario de formato van en claro**: *"el CA de X"* → *"el criterio
  de aceptación de X"*; *"no tiene un THEN verificable"* → *"no tiene un resultado verificable"*;
  *"la HU de alta"* → *"la historia de usuario de alta"*. `GIVEN`/`WHEN`/`THEN` **no los lee ningún
  script**: son el formato del CA **dentro del spec**, no vocabulario con el que explicarle un
  hueco a alguien.

**Tres bordes que no se cruzan.**

1. El campo `Afecta` lista **IDs** y se queda como está — es lo que el writer usa para marcar las
   historias `[INCOMPLETO]`.
2. Esto **no toca el spec**: allí los CAs se escriben en GIVEN/WHEN/THEN porque ese es su formato
   (`kb-spec-expert`).
3. Esto aplica a los bloques **`[P-XXX]`**, no a la sección **Testabilidad**. Ahí el formato **es
   el asunto** —un CA al que le falta el `THEN` es literalmente el defecto que reportas—, así que
   nombrarlo es correcto y la plantilla lo hace a propósito. La diferencia: en Testabilidad hablas
   *del formato*; en un gap usabas el formato *como abreviatura* de otra cosa.

> **Por qué la norma está aquí y no en quien presenta el gap (pasada 9 de CU-3.a).** El
> orquestador tiene contrato de leer estos campos **verbatim** y aun así reescribió *"el CA … no
> tiene un THEN verificable"* como *"el criterio de aceptación … no tiene un resultado
> verificable"*. La reescritura mejoraba el texto y el contrato era correcto: el defecto estaba
> aguas arriba. Si el campo **nace** en claro, no hay nada que traducir, y `verbatim` se queda
> estricto — que es lo que lo hace medible con un diff en vez de con un juicio.

### Campo "Afecta" (obligatorio en CRÍTICO)

Para cada gap `[CRÍTICO]`, determina qué HUs del documento no pueden completarse sin la respuesta a este gap. Lista sus IDs en el campo `- **Afecta**: [HU-001, HU-003]`. Si las HUs aún no tienen IDs asignados (porque el documento es un PRD sin HUs formales), describe las funcionalidades afectadas en texto libre (ej: `- **Afecta**: funcionalidad de login, recuperación de contraseña`).

### Clasificación de severidad (obligatoria)

Consulta `kb-gap-conventions` para las definiciones completas. Resumen:

- **`[CRÍTICO]`**: las HUs indicadas en "Afecta" quedarán marcadas `[INCOMPLETO]` en el spec si no se responde. Se generarán con la información disponible pero no podrán avanzar a plan/tasks.
- **`[INFORMATIVO]`**: continúa con asunción por defecto (edge cases asumibles, preferencias menores). **Siempre incluye una "Asunción por defecto"** con lo que se aplicará si el cliente no responde.
- **`[PUEDE_REQUERIR_CR]`**: marcador advisory opcional. Añádelo si la futura respuesta podría introducir expansión de capacidad y, por tanto, exigir `wf-prd-change` antes de derivar specs.

---

## Paso 6: Formato del informe

Consulta [output_template.md](output_template.md) para la estructura exacta del informe.

> **La cabecera lleva la versión del PRD, no solo su path ([[D-051]]).** `Archivo origen`
> se escribe como `<path> (v<X.Y>)`, tomando `<X.Y>` del `version:` del frontmatter del PRD
> (`!grep -nE '^version:' "<prd>"`). Es lo que permite a `wf-spec-discover` comprobar que
> no está construyendo el mapa de features sobre un análisis de una versión que ya no
> existe. Sin ese dato, un análisis viejo y uno vigente son indistinguibles.

---

## Paso 7: Escribir el resultado

Determina el directorio de salida (regla de layout): si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.prd`, usa ese directorio (relativo a la raíz que contiene `.sdd/`); si no, usa el mismo directorio que el archivo de entrada. Nombre: nombre base del archivo de entrada + `_analysis.md`.
- Ejemplo (sin mapa): `docs/requisitos.md` → `docs/requisitos_analysis.md`
- Ejemplo (con `"artifacts": {"prd": "docs/prd"}`): → `docs/prd/requisitos_analysis.md`

Antes de escribir, verifica si el archivo ya existe:
```bash
!test -f "<path_calculado>" && echo "EXISTE" || echo "NO_EXISTE"
```
- **`NO_EXISTE`** → sigue.
- **`EXISTE` sin `--allow-overwrite-analysis`** → **detente sin escribir nada** y devuelve el bloqueo a quien te
  lanzó, con veredicto operativo `STOP_ARTEFACTO_EXISTE`:
  > "Ya existe `<path>` y contiene <N> respuesta(s) escritas. Regenerarlo las pisa, y son decisiones de negocio de una persona, no material regenerable. No lo he tocado."
- **`EXISTE` con `--allow-overwrite-analysis`** → sobreescribe y **dilo en tu informe final**. Antes de escribir, **rescata sus respuestas** (ver abajo).

> **Por qué aquí no preguntas ([[D-064]]).** Corres en `context: fork`, y un subagente no puede
> presentarle una elección al usuario: la instrucción que este paso tenía antes no era
> ejecutable ([[D-045]]). Paras y reportas; el gate lo presenta quien puede ([[D-026]]).

El número de respuestas escritas te lo da el script, no tu lectura ([[D-042]]):
```bash
!python3 .sdd/scripts/sdd-analysis-gaps.py "<path>" --check --json
```

### 7.1 Rescatar las respuestas antes de sobrescribir ([[D-051]])

Regenerar **sobrescribe**. Si el análisis que vas a pisar tiene respuestas escritas, se
pierden — y ese no es un caso raro: es el caso normal. Un PRD cambia **después** de que
alguien haya respondido sus gaps (un `wf-prd-change` de por medio), y esas respuestas son
decisiones de negocio de una persona, no material regenerable.

**Antes** de escribir nada:

```bash
!python3 .sdd/scripts/sdd-analysis-gaps.py "<path>" --export-answers > "<path>.answers.json"
```

Escribe el informe nuevo en `<path>`, y **después**:

```bash
!python3 .sdd/scripts/sdd-analysis-gaps.py "<path>" --import-answers "<path>.answers.json"
```

- **exit 0** → todas volvieron a su sitio. Borra el `.answers.json` y sigue.
- **exit 2** → alguna **no** se pudo devolver. **Conserva el fichero**, y en el Paso 8 di
  cuáles y por qué, con su texto, para que el usuario las recoloque.

> **Por qué el script no las coloca solas.** Empareja por ID **y por título**, y lo que no
> case exacto no lo escribe. El análisis **no es reproducible** —medido: sobre un PRD
> byte-idéntico, pasadas sucesivas dieron 11/5, 12/7, 11/7, 16/11, 5/2 y 7/4 gaps—, así que
> el mismo `P-XXX` puede ser **otra pregunta** en el documento nuevo. Colocar ahí una
> respuesta de negocio por coincidencia de ID sería un error invisible: el documento queda
> con pinta de respondido y dice algo que nadie dijo. Ante la duda, el hueco es mejor.
>
> Los tres motivos que devuelve son `titulo_distinto`, `id_ausente` y `ya_respondido`. **No
> los resuelvas tú**: ni reescribas la respuesta con tus palabras, ni la des por equivalente
> porque "va de lo mismo". Se las presentas al usuario.

Escribe el informe generado en ese path.

---

## Paso 8: Informar al usuario

Tras escribir el archivo, informa:
- Path del archivo generado
- Veredicto del Estado de preparación para Specs
- Resumen: cuántos elementos del Spec se generarán desde cero vs. ya parciales en PRD, cuántas contaminaciones técnicas detectadas (si las hay), cuántos `[P-XXX]` pendientes (desglosados: CRÍTICOS e INFORMATIVOS)
- Siguiente paso:
  - Si veredicto = `LISTO_PARA_SPECS`: "Anota cualquier aclaración adicional en `<path>_analysis.md`. Cuando quieras, pídeme que **genere las specs por feature**; o si prefieres ir paso a paso, que **descubra primero las features**."
  - Si veredicto = `LISTO_PARA_SPECS_CON_PREGUNTAS`: **no basta con decir "responde los pendientes"** — quien tiene que contestar no debería tener que bucear en el informe para saber qué le toca. Da las tres cosas: (1) el **path exacto** del `_analysis.md`; (2) la lista de gaps `[CRÍTICO]`, cada uno como `[P-XXX] — <su "Pregunta para el cliente" en una línea>`; (3) qué se sustituye literalmente: en el bloque de cada gap, `- **Respuesta**: _(pendiente)_` → la respuesta. Y cierra con las dos vías, **descritas como decisiones, no como comandos**: "(a) responder primero los `[CRÍTICO]` y pedirme entonces que genere las specs; (b) pedirme que las genere igualmente, aceptando que las HUs afectadas salgan `[INCOMPLETO]`." La segunda vía la arma el usuario **eligiéndola** ([[D-026]]): no le enseñes el flag que la activa.

    > **Las respuestas las escribe el usuario en el fichero** ([[D-042]], tabla de ámbito en `kb-gap-conventions`). Si prefiere dictarlas en la conversación, el hilo principal las aplica con `sdd-analysis-gaps.py --answer P-XXX "texto"` — **nadie edita el `_analysis.md` a mano desde main**, y nadie inventa el contenido de una respuesta.
  - Si veredicto = `REQUIERE_LIMPIEZA_PRD`: "Hay contaminación técnica en el PRD. Tienes dos vías para limpiarlo: (a) aplicar tú mismo las reescrituras de la sección Pureza del análisis; (b) pedirme que lo **revise contigo** para un diagnóstico más estructurado antes de corregir. Cuando esté corregido, dime que **lo vuelva a analizar**."
  - Si detectaste cambio de producto: "Antes de continuar con Specs hay que **formalizar el cambio en el PRD** — dímelo y lo abro; después **mido qué artefactos derivados quedan afectados**."
