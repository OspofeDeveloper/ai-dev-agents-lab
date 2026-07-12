---
name: wf-prd-create
description: "Crea un PRD inicial guiado para el pipeline SDD. Puede partir de notas, un brief o una idea suelta, y genera un prd.md limpio, orientado a negocio y listo para revision."
when_to_use: "Activa en frases como 'ayudame a crear el PRD', 'genera un PRD', 'construye el documento de requisitos', 'convierte estas notas en un PRD'."
argument-hint: "<directorio_proyecto> [--source <notas.md>] [--output <prd.md>]"
effort: medium
allowed-tools: [Read, Write, Bash, Agent, AskUserQuestion]
user-invocable: true
---

# Workflow: PRD Create

Tu objetivo es ayudar al usuario a crear un `prd.md` usable por el pipeline SDD. Delegas la redacción del contenido al agente `prd-expert`.

Este workflow corre en el **hilo principal** (igual que `wf-prd-review`, y **no** en `context: fork`): necesita `AskUserQuestion` para dos gates —pedir un brief mínimo si no hay `--source` (Paso 3) y confirmar la sobreescritura —de forma ponderada por riesgo— si el PRD ya existe (Paso 4)—, una tool que no existe dentro de un subagente. La **redacción** del PRD la hace el agente `prd-expert` (carga `kb-prd-expert`), al que invocas **una sola vez** vía la tool `Agent`, en **foreground** (`run_in_background: false`, Paso 5), y de quien **esperas** el resultado.

**Regla de oro:** generas un PRD, no un Spec. Mantén el nivel en negocio, actores, alcance y reglas transversales.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Directorio del proyecto**: primer argumento obligatorio
- **Flag opcional**: `--source <archivo.md>` — notas, brief, discovery call o requisitos informales
- **Flag opcional**: `--output <archivo.md>` — nombre o ruta de salida del PRD

Si no hay directorio, informa al usuario:
> "Uso: `/wf-prd-create <directorio_proyecto> [--source <notas.md>] [--output <prd.md>]`"
> "Ejemplo: `/wf-prd-create docs/producto --source notes/kickoff.md`"

---

## Paso 2: Verificar el directorio (y la fuente)

Verifica que el directorio existe:
```
!test -d "<dir>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe, informa al usuario con la ruta exacta y detén.

Si se proporcionó `--source`, verifica que el archivo existe:
```
!test -f "<source>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe, informa al usuario con la ruta exacta y detén.

---

## Paso 3: Recoger el material de entrada

### Si hay `--source`

**No leas el fichero en el hilo principal.** Solo verificaste que existe (Paso 2); pásalo por **path** a `prd-expert` (Paso 5), que lo leerá con su propia `Read`. Así el contenido no se duplica en el contexto del orquestador ni se incrusta en el prompt del agente.

### Si NO hay `--source`

Pide al usuario una base mínima con `AskUserQuestion` (o en texto libre si encaja mejor) **antes** de delegar:
- nombre del producto
- actores principales
- problema que resuelve
- capacidades principales
- fuera de alcance conocido, si existe

No continúes sin esa base: si el usuario no aporta nada, no inventes el PRD. Si aporta texto libre, úsalo como brief inicial (se lo pasarás al agente en el Paso 5).

---

## Paso 4: Determinar el path de salida y confirmar sobreescritura (ponderada por riesgo)

Resuelve el path **antes** de delegar la escritura:
- Si el usuario proporcionó `--output`, úsalo.
- Si no (regla de layout): si `.sdd/project-init.json` (en `<directorio_proyecto>` o un ancestro) declara `artifacts.prd`, el path es `<raíz>/<artifacts.prd>/prd.md`; si no, por defecto `<directorio_proyecto>/prd.md`.

Verifica si ya existe y, si existe, si está **sellado** (tiene un `Aprobado por:` relleno — señal de que pasó por `wf-prd-review`):
```bash
!if [ ! -f "<path_calculado>" ]; then echo NO_EXISTE; elif grep -iq "Aprobado por:" "<path_calculado>" && ! grep -i "Aprobado por:" "<path_calculado>" | grep -qi pendiente; then echo EXISTE_SELLADO; else echo EXISTE_DRAFT; fi
```
> Sellado ⇔ existe una línea `Aprobado por:` **y** no contiene `pendiente`. (No uses `grep -v` en pipe: en BSD/macOS `<vacío> | grep -qv` devuelve 0, y clasificaría como sellado un PRD sin línea de sello.)

La confirmación **no es un "¿seguro?" plano**: se pondera por lo que hay que perder. Actúa según el resultado:

- **`NO_EXISTE`** → continúa al Paso 5.
- **`EXISTE_SELLADO`** → **siempre** confirma con `AskUserQuestion`, avisando del descarte:
  > "Ya existe un PRD **aprobado** en `<path>` (`Aprobado por: <rol>`). Regenerarlo **descarta el trabajo de review** (asunciones confirmadas y sello). ¿Regenerar de todas formas?"
  - **No** → informa el path del PRD aprobado y **detén** (no delegues ni escribas). **Da igual lo explícito que fuera el comando**: un PRD sellado no se pisa sin confirmación.
  - **Sí** → continúa al Paso 5.
- **`EXISTE_DRAFT`** (draft sin sellar):
  - Si la petición del usuario es una **intención explícita de regenerar/sobreescribir** ese PRD ("regenera", "rehaz", "vuélveme a generar", "sobreescribe" apuntando al artefacto) → el consentimiento **ya está dado**: continúa al Paso 5 **sin re-preguntar** (re-confirmar aquí es fricción redundante).
  - Si la petición es **ambigua** (p. ej. "créame el PRD" y el usuario quizá no sabe que ya existe uno) → confirma con `AskUserQuestion`:
    > "Ya existe `<path>` (draft). ¿Lo regenero (se sobreescribe) o prefieres conservarlo?"
    - **Conservar / No** → informa el path y **detén**.
    - **Regenerar / Sí** → continúa al Paso 5.

> **Por qué ponderada** (ver `DECISIONS.md` D-024): el valor del gate no es "¿te refieres a este fichero?" —eso ya lo dice un comando explícito— sino **avisar de que se descarta un PRD revisado/sellado**. Confirmar siempre es *nagging* en el caso común (regenerar un draft que el usuario acaba de pedir regenerar); no confirmar nunca deja pisar en silencio trabajo aprobado. El sello `Aprobado por:` es la línea objetiva (canon: `kb-traceability-rules` Regla 10).

---

## Paso 5: Delegar la redacción al agente `prd-expert` (vía la tool `Agent`, y esperar)

Invoca al agente `prd-expert` **una sola vez** con la tool `Agent`, en **foreground (síncrono)**: pásale explícitamente **`run_in_background: false`** en la invocación. Esto es **obligatorio** — desde Claude Code v2.1.198 los subagentes corren en **background por defecto**, y aquí el orquestador necesita el resultado en el acto (el Paso 6 hace `grep` sobre el fichero que el agente escribe). Sin `run_in_background: false`, el harness puede lanzar el agente en background y el orquestador contaría/reportaría **antes** de que termine de escribir → lectura prematura o race. **Espera** su resultado: no sondees el filesystem para decidir si "no se creó" ni relances un segundo agente. (Una sola invocación síncrona evita el race de dos agentes escribiendo el mismo `prd.md`.)

Pásale:
- **el material de entrada por referencia, no incrustado**: si hay `--source`, la **ruta** del fichero fuente (que `prd-expert` leerá con `Read`), nunca su contenido pegado en el prompt; si NO hay `--source`, el brief que el usuario dio en sesión (Paso 3)
- el **path de salida** ya resuelto (Paso 4), donde debe escribir el PRD con `Write`
- la instrucción de producir un PRD completo en Markdown

Indícale explícitamente:
- que use `kb-prd-expert` como SSoT (estructura + frontmatter en Regla 3 + `references/prd_structure_guide.md`)
- **que aplique la Regla 12 (anti-fabricación)**: toda afirmación de negocio (actor, capacidad, exclusión, regla, objetivo) traza al material fuente / al brief del usuario, o se marca `[ASUNCIÓN]` inline y se recopila en `## Asunciones del PRD` con un `[ASN-XXX]` por entrada. Prohibido inventar contenido de negocio sin marcarlo: ante la duda, se marca.
- que convierta detalles técnicos en observaciones a excluir, no en contenido del PRD
- que mantenga una estructura compatible con `wf-spec-analyze`
- que en su mensaje final te devuelva el **path** y los **huecos cualitativos** (qué trazó a la fuente vs qué infirió, qué asunciones son las más sensibles), **no un recuento numérico**: el número de `[ASUNCIÓN]` lo obtienes tú de forma determinista con grep (Paso 6), nunca de su narración — un agente cuenta mal sobre su propio texto

**Énfasis si NO hay `--source`** (el material es un brief breve dado en sesión): casi todo lo que exceda lo que el usuario dijo literalmente es inferencia → marcar `[ASUNCIÓN]` de forma agresiva. Un PRD honestamente lleno de `[ASUNCIÓN]` es correcto; un PRD que presenta invenciones como hechos es el fallo que esta regla previene.

---

## Paso 6: Informar al usuario

El `prd-expert` ya escribió el PRD en el path (Paso 5). Tras recibir su resultado, informa:
- path del PRD generado
- si se usó o no archivo fuente
- **número de `[ASUNCIÓN]` marcadas**, obtenido de forma determinista con `grep -c "\[ASUNCIÓN" <path>` (**nunca** de la narración del agente: cuenta mal sobre su propio texto), y aviso de que el PRD **no está listo** hasta confirmarlas: son afirmaciones que la generación infirió, no datos que el usuario haya dado. Cuantas más, más débil era la fuente.
- si quedaron huecos explícitos que el usuario debería revisar manualmente

**DETENTE aquí. No resuelvas tú las asunciones.**
El gate de confirmación de las `[ASUNCIÓN]`/`[ASN-XXX]` (presentarlas una a una,
confirmar/rechazar/editar, limpiar la sección `## Asunciones del PRD`, subir versión y sellar
`Aprobado por:`) es **exclusivo de `wf-prd-review`** (sus Pasos 5.5 y 6). No lances
`AskUserQuestion` por las asunciones, no edites el PRD para integrarlas y no improvises ese
gate aquí: es trabajo de otra skill. Si el usuario no ejecuta review, las asunciones residuales
bajan como gaps a `wf-spec-analyze` (`kb-prd-expert` Regla 12) — nunca las resuelves tú.

**Siguiente paso:**
> Revisa el PRD y luego ejecuta `/wf-prd-review <path/prd.md>`: confirmará una a una las
> asunciones `[ASN-XXX]`, validará la entrada y sellará la aprobación antes del análisis SDD.
