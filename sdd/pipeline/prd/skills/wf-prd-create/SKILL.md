---
name: wf-prd-create
description: "Crea un PRD inicial guiado para el pipeline SDD. Puede partir de notas, un brief o una idea suelta, y genera un prd.md limpio, orientado a negocio y listo para revision."
when_to_use: "Activa en frases como 'ayudame a crear el PRD', 'genera un PRD', 'construye el documento de requisitos', 'convierte estas notas en un PRD'."
argument-hint: "<directorio_proyecto> [--source <notas.md>] [--output <prd.md>]"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
agent: prd-expert
user-invocable: true
---

# Workflow: PRD Create

Tu objetivo es ayudar al usuario a crear un `prd.md` usable por el pipeline SDD. Delegas la redacción y organización del contenido al agente `prd-expert`.

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

## Paso 2: Verificar el directorio

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

**No leas el fichero en el hilo principal.** Solo verificaste que existe (Paso 2); pásalo por **path** a `prd-expert` (Paso 4), que lo leerá con su propia `Read`. Así el contenido no se duplica en el contexto del orquestador ni se incrusta en el prompt del agente.

### Si NO hay `--source`

Pide al usuario una base mínima antes de delegar:
- nombre del producto
- actores principales
- problema que resuelve
- capacidades principales
- fuera de alcance conocido, si existe

Si el usuario aporta texto libre, úsalo como brief inicial.

---

## Paso 4: Delegar al agente `prd-expert`

Invoca al agente `prd-expert` con:
- **el material de entrada por referencia, no incrustado**: si hay `--source`, la **ruta** del fichero fuente (que `prd-expert` leerá con `Read`), nunca su contenido pegado en el prompt; si NO hay `--source`, el brief que el usuario dio en sesión (Paso 3)
- la ruta objetivo
- la instrucción de producir un PRD completo en Markdown

Indícale explícitamente:
- que use `kb-prd-expert` como SSoT
- **que aplique la Regla 12 (anti-fabricación)**: toda afirmación de negocio (actor, capacidad, exclusión, regla, objetivo) traza al material fuente / al brief del usuario, o se marca `[ASUNCIÓN]` inline y se recopila en `## Asunciones del PRD` con un `[ASN-XXX]` por entrada. Prohibido inventar contenido de negocio sin marcarlo: ante la duda, se marca.
- que convierta detalles técnicos en observaciones a excluir, no en contenido del PRD
- que mantenga una estructura compatible con `wf-spec-analyze`
- que en su mensaje final te devuelva el **path** y los **huecos cualitativos** (qué trazó a la fuente vs qué infirió, qué asunciones son las más sensibles), **no un recuento numérico**: el número de `[ASUNCIÓN]` lo obtienes tú de forma determinista con grep (Paso 7), nunca de su narración — un agente cuenta mal sobre su propio texto

**Énfasis si NO hay `--source`** (el material es un brief breve dado en sesión): casi todo lo que exceda lo que el usuario dijo literalmente es inferencia → marcar `[ASUNCIÓN]` de forma agresiva. Un PRD honestamente lleno de `[ASUNCIÓN]` es correcto; un PRD que presenta invenciones como hechos es el fallo que esta regla previene.

---

## Paso 5: Determinar path de salida

Si el usuario proporcionó `--output`, úsalo.

Si no lo proporcionó (regla de layout): si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.prd`, escribe en `<raíz>/<artifacts.prd>/prd.md`; si no, escribe por defecto:
```
<directorio_proyecto>/prd.md
```

Antes de escribir, verifica si el archivo ya existe:
```bash
!test -f "<path_calculado>" && echo "EXISTE" || echo "NO_EXISTE"
```
Si ya existe → pregunta al usuario:
> "Ya existe `<path>`. ¿Deseas regenerarlo?"
- Si responde **no** → informa el path del artefacto existente y detén.
- Si responde **sí** → continúa.

---

## Paso 6: Escribir el PRD

Escribe el documento generado en el path de salida.

La estructura y el frontmatter del PRD los define `kb-prd-expert` (Regla 3 + `references/prd_structure_guide.md`) — la SSoT que el agente aplica; esta skill **no la replica**. Solo dos recordatorios operativos: la sección `## Asunciones del PRD` aparece **si y solo si** se marcó algún `[ASUNCIÓN]` (Regla 12), y el frontmatter (`version`, `status`) lo consumen aguas abajo `wf-prd-review` (bump de versión, sello) y la gobernanza de cambios.

---

## Paso 7: Informar al usuario

Tras escribir el archivo, informa:
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
