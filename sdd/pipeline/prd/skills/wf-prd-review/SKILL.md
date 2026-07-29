---
name: wf-prd-review
description: "Revision rapida de un PRD o documento de requisitos antes de entrar en la fase Spec. Comprueba si el documento esta limpio, si explicita actores y alcance, y si su estructura es procesable por el pipeline SDD."
when_to_use: "Activa en frases como 'revisa mi PRD', '¿este PRD esta bien para empezar?', 'haz preflight del PRD', 'valida el documento de requisitos antes del spec'."
argument-hint: "<archivo_prd.md>"
effort: medium
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# Workflow: PRD Review

Tu objetivo es revisar si un PRD está preparado para entrar en el pipeline SDD. No generas Spec, no generas features y no corriges el documento por tu cuenta: emites un diagnóstico claro y accionable. **Dos excepciones acotadas** en las que sí se edita el PRD: (1) la confirmación de asunciones del Paso 5.5 — solo lo que el usuario decide explícitamente sobre cada `[ASUNCIÓN]`, nunca de tu cosecha; (2) el sello de aprobación del review cuando el veredicto es `LISTO` (Paso 6) — solo la línea `Aprobado por:` en el header. Ninguna otra reescritura.

Este workflow corre en el **hilo principal** (necesita confirmar las asunciones contigo en el Paso 5.5, vía `AskUserQuestion` — una tool que no existe dentro de un subagente). El **análisis experto** del PRD lo hace el agente `prd-expert`, que carga `kb-prd-expert` como fuente autoritativa; tú lo invocas vía la tool `Agent` (Paso 4) y gestionas los gates humanos aquí, en el hilo principal.

**El hilo principal no carga ni reescribe el PRD.** No tienes `Read` ni `Write` sobre el documento: las dos ediciones (asunciones, sello) se aplican **deterministamente** con `sdd-prd-apply.py` vía `Bash`, desde las decisiones que recoges en el gate — nunca releyendo el fichero entero en contexto ([[D-030]]). "Quién edita" no cambia: lo ejecuta el orquestador, no un agente; solo cambia el mecanismo (script en vez de `Read`+`Write`).

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del archivo PRD.

Si no hay argumento, informa al usuario:
> "Uso: `/wf-prd-review <archivo_prd.md>`"

---

## Paso 2: Verificar el archivo

Verifica que el archivo existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe, informa al usuario con la ruta exacta y detén.

Si el nombre termina en `_spec.md`, `_plan.md` o `_tasks.md`, informa y **detén** (no continúes a los Pasos 3-4):
> "Este archivo parece un artefacto posterior del pipeline. `/wf-prd-review` opera sobre PRDs o documentos de requisitos iniciales."

---

## Paso 3: No cargues el PRD en el hilo principal

No leas el PRD completo aquí: su lectura y análisis se delegan al `prd-expert` (Paso 4), que recibe el **path** y lo lee con su propia `Read` + `kb-prd-expert`. El orquestador solo vuelve a tocar el fichero —de forma puntual y acotada, **siempre por script `Bash`, nunca con `Read`+`Write`**— cuando tiene que **editarlo**: el gate de asunciones (Paso 5.5, `sdd-prd-apply.py`, solo si quedan marcas > 0) y el sello (Paso 6, `sdd-prd-apply.py --seal`, solo si el veredicto es `LISTO`). Así el contexto del orquestador no carga el documento entero (que además se duplicaría en el prompt del agente).

---

## Paso 4: Delegar el análisis a `prd-expert` (estructura, frontera y contaminación técnica)

El análisis del PRD lo hace el agente `prd-expert` (carga `kb-prd-expert` en su contexto). Invócalo vía la tool `Agent` con este encargo — devuelve un diagnóstico estructurado, **sin reescribir el PRD**:

```text
Modo: review-prd
Path del PRD: <path>
INSTRUCCIÓN: lee el PRD con `Read` desde ese path y evalúalo contra `kb-prd-expert`; devuelve un diagnóstico estructurado:
1. Estructura y frontera: ¿describe un único producto o está partido artificialmente?, ¿actores explícitos?, ¿alcance dentro/fuera claro?, ¿reglas de negocio transversales?, ¿estructura procesable (por actor / por RFs numerados / por secciones funcionales — no penalices la elegida si es clara y trazable)?
2. Contaminación técnica: aplica la Prueba de Negocio (`kb-prd-expert` Regla 6) a cada sección y cótejala contra el catálogo de elementos prohibidos (`references/prd_prohibited_items.md` de `kb-prd-expert`: stack, frameworks, patrones de diseño, endpoints, esquemas de datos, timelines, criterios técnicos de QA, pantallas como unidad de feature, etc.). Por cada fragmento problemático: cita el fragmento exacto, indica qué entrada del catálogo viola y propón la reescritura funcional equivalente. La SSoT de la frontera es `kb-prd-expert`, no una frontera inline.
3. Asunciones: reporta los marcadores `[ASUNCIÓN]`/`[ASN-XXX]` presentes (su confirmación con el usuario la gestiona el orquestador en el Paso 5.5; tú solo los listas).
INSTRUCCIÓN: no edites el PRD ni inventes requisitos faltantes; los huecos se señalan como problemas de entrada.
```

El diagnóstico que devuelve `prd-expert` alimenta el veredicto del Paso 6. Las ediciones del PRD (confirmación de asunciones, sello de aprobación) las hace el orquestador en el hilo principal — nunca el agente.

> **Espera el diagnóstico antes de abrir el gate — no lo paralelices.** Invoca al `prd-expert` en **foreground** (síncrono) y **aguarda su resultado** antes de presentar el gate de asunciones (Paso 5.5). El gate **depende** del diagnóstico: usa los flags de gobernanza del experto (qué `[ASN-XXX]` son de alto impacto y por qué) para presentar cada asunción con contexto. Lanzarlo en background y abrir el gate en paralelo presenta las asunciones **sin** ese contexto y fuerza a re-presentarlas cuando el experto termina (carrera observada en CU-2.e). No hay nada útil que paralelizar: el único trabajo pendiente es el gate, que consume esta salida.

---

## Paso 5.5: Confirmar asunciones del PRD (anti-fabricación)

`kb-prd-expert` Regla 12 obliga a que toda afirmación de negocio no trazable a la fuente esté marcada `[ASUNCIÓN]`. Este paso es el **gate de confirmación humana** de esas asunciones — el contrapunto a la generación: el autor marca lo que infirió, el review lo confirma o lo descarta.

**Detección determinista** (no a ojo). Usa `sdd-prd-ready.py`, que cuenta las marcas inline `[ASUNCIÓN]` (incluida la variante verbosa `[ASUNCIÓN: …]`) **excluyendo menciones en prosa** —callouts `>`, la nota de la sección— que inflan un `grep -c` crudo (la falsa-positiva de CU-2.b), y **verifica el invariante 1:1** (marcas inline == entradas `[ASN-XXX]`), reportando huérfanas:
```
!python3 .sdd/scripts/sdd-prd-ready.py "<path>" --json
!grep -n "\[ASUNCIÓN" "<path>"   # localización línea a línea para procesar cada una
```
El campo `inline_marks` es el conteo real; `ASSUMPTION_MISMATCH` señala una marca huérfana o una entrada sin marca — corrígela antes de seguir. Esto **cierra la verificación mecánica del 1:1** que antes dependía de un `grep` improvisado por el agente (reserva de CU-2.a/b). Si falta el script, cae al `grep -c "\[ASUNCIÓN"` como degradación.

**Grafo de dependencias entre asunciones ([[D-029]]).** Antes de abrir el gate, carga el grafo determinista — así conoces qué asunciones dependen de cuáles **sin inferirlo a ojo** (la cascada era no determinista en CU-2.e):
```
!python3 .sdd/scripts/sdd-prd-deps.py "<path>" --json
```
El campo `graph` (`{"ASN-007": ["ASN-006"], …}`) te dice, por cada asunción, de qué otras depende. Úsalo en el gate (abajo). Si `sdd-prd-deps.py` sale con `MALFORMED` (arista a un `ASN` inexistente o ciclo), avisa y corrígelo antes de procesar.

- **`inline_marks` es `0`** → no hay asunciones pendientes; sigue al veredicto.
- **`inline_marks` `> 0`** → recorre **cada `[ASN-XXX]` una a una con el usuario** (usa `AskUserQuestion` cuando haya varias): para cada una, presenta la afirmación inferida y su hueco (con los flags de gobernanza del experto), y **recoge** la decisión. No edites el PRD entrada a entrada: **acumula** las decisiones y aplícalas al final en **una sola** llamada a `sdd-prd-apply.py`. Las tres decisiones y su flag:
  - **Confirmar** → es correcta (pasa a hecho de negocio): `--confirm ASN-XXX` — quita el marcador `[ASUNCIÓN]` inline de esa afirmación y retira su entrada de la sección.
  - **Rechazar** → no es lo que el negocio quiere: `--reject ASN-XXX` — elimina del PRD la afirmación y su marcador. **Cascada determinista ([[D-029]]):** si el `graph` indica que otras asunciones **dependen** de la que se rechaza, arrástralas al flujo de decisión —preséntalas con `AskUserQuestion`— en vez de dejarlas confirmar en silencio; una dependiente de una rechazada normalmente se rechaza también, o se edita para no depender de ella, o —tercer desenlace legítimo— se **conserva** porque la dependencia queda satisfecha de otro modo (entonces decláralo con `--keep` en el backstop de abajo, [[D-037]]). *(La prosa de brief que dependía de una rechazada —líneas sin marca, nivel b— no la toca el script: si el diagnóstico del `prd-expert` la señaló, resuélvela con el usuario en el gate; queda fuera del automatismo.)*
  - **Editar** → el usuario da el dato real, **en el momento**: en la descripción de la opción "Editar" del `AskUserQuestion`, indícale que **para editar escriba el texto nuevo en el campo libre** ("Otro"/texto) de esa asunción en vez de seleccionar "Editar". Un valor de texto libre sobre una asunción se interpreta como su edición → `--edit ASN-XXX="<texto nuevo>"`: sustituye la afirmación por ese texto y quita el marcador — **sin diferirlo al final**.

**Backstop de dependencias ([[D-029]]) — corre ANTES de aplicar ([[D-037]]).** Con las decisiones ya recogidas y **antes** de tocar el fichero, verifica que ninguna dependiente de una rechazada quedó sin decidir:
```
!python3 .sdd/scripts/sdd-prd-deps.py "<path>" --check --rejected ASN-006,ASN-0XX [--keep ASN-00Y]
```
- `--rejected` = las que el usuario **rechazó**. `--keep` = dependientes que, tras presentárselas, decidió **conservar** conscientemente (la dependencia queda satisfecha de otro modo — p. ej. se rechaza "el Usuario gestiona el catálogo de categorías" pero "presupuesto por categoría" sigue en pie sobre categorías fijas). `--keep` es una declaración **deliberada**: no basta con confirmarlas, hay que nombrarlas.
- `ORPHANS` (exit 2) → **re-presenta** esos dependientes al usuario para decidir antes de continuar; luego re-corre el check con la decisión reflejada (`--reject`… o `--keep`…). No apliques ni selles con una huérfana.
- Exit 0 → coherente, sigue al apply.

> ⚠ **El orden no es cosmético.** Este check lee las entradas `[ASN-XXX]` y sus aristas. `sdd-prd-apply.py` retira las decididas y borra la sección si queda vacía, así que **después** del apply no hay nada que comprobar. Correrlo tarde no es "verificar por si acaso": es un no-op que se lee como garantía (fallo real observado en conformance CU-2.j — se selló con una dependiente sin decidir y el check dijo `OK`). Por eso el script sale `VACUOUS` (exit 2) si le pasas rechazos sobre un documento sin entradas: si ves `VACUOUS`, lo corriste en el orden equivocado.

**Consecuencia del rechazo, en el momento ([[D-037]]).** Rechazar **borra** la afirmación pero no añade el hecho contrario: el PRD puede quedar **mudo** sobre algo que otra asunción confirmada da por existente (p. ej. rechazada "el Usuario gestiona las categorías", el PRD ya no dice de dónde salen). Cuando el rechazo deje ese hueco, plantéalo **al recoger esa decisión** —mientras el contexto está fresco— y no al final antes de sellar: pregunta si quiere dejar constancia de la decisión contraria como regla transversal, o dejarlo para `wf-spec-analyze`. Es el nivel b (prosa sin marca) que el script no toca.

Aplica todas las decisiones acumuladas en una pasada (el script empareja cada `ASN-XXX` con su marca inline por texto/contenido, preserva el 1:1 y, si la sección de asunciones queda vacía, la elimina entera):
```
!python3 .sdd/scripts/sdd-prd-apply.py "<path>" --confirm ASN-001,ASN-003 --edit ASN-004="<texto>" --reject ASN-006,ASN-007
```
Si sale exit 2 (1:1 roto o desalineación), **no continúes**: resuélvelo (`sdd-prd-ready.py`) antes de reintentar — el script no edita a ciegas.

A diferencia del resto de `wf-prd-review` (que solo diagnostica), aquí **sí** se edita el PRD, pero solo lo que el usuario decide explícitamente sobre cada asunción (aplicado por `sdd-prd-apply.py`) — no reescrituras de tu cosecha.

**Efecto en el veredicto:** mientras queden marcadores `[ASUNCIÓN]` sin confirmar, el PRD **no puede ser `LISTO`** (es contenido fabricado sin validar). Si el usuario no quiere resolverlas ahora, el veredicto es `NO_LISTO` con las asunciones pendientes listadas.

---

## Paso 6: Emitir veredicto

Si el veredicto es `LISTO` (y por tanto no quedan `[ASUNCIÓN]` pendientes tras el Paso 5.5), registra la **atribución de aprobación humana** del gate antes de emitir el veredicto, según `kb-traceability-rules` Regla 10:

0. **Frontmatter completo antes de sellar.** Un PRD que se va a aprobar no debe tener campos obligatorios ausentes (`kb-prd-expert` Regla 3). Asegúralo de forma determinista:
   ```bash
   !python3 .sdd/scripts/sdd-prd-frontmatter.py "<path>" --fix
   ```
   Repone los campos mecánicos que falten (`type`, `version`, `created`, `status`). Si sale con exit ≠0 por falta de `product`, no selles: es un hueco de contenido que hay que resolver antes.
1. Captura la **identidad del aprobador** con `AskUserQuestion` ([[D-027]]): **precarga el nombre** con `!git config user.name` como opción por defecto (lo que sella es *quién* aprobó, no un rol genérico), y ofrece **rol opcional** (PM / Product Owner). El usuario confirma el nombre precargado, lo cambia, o añade rol. Si `git config user.name` está vacío, cae al rol como default.
2. Si el usuario responde, estampa el sello con el script (no con `Write`) — sobrescribe la línea `Aprobado por:` del header con el valor `<nombre> [(<rol>)] (<fecha real de tu contexto>)` **y sube `status:` a `approved`** ([[D-032]]: "sellado" son las dos cosas juntas — si `status` no llega a `approved`, `wf-prd-change` no reconocería el PRD como sellado y su reapertura no dispararía):
   ```bash
   !python3 .sdd/scripts/sdd-prd-apply.py "<path>" --seal "Oscar Pozo (Product Owner) (2026-07-17)"
   ```
   En re-revisión sobrescribe la línea previa. **No autoapruebes**: si no hay respuesta, no llames a `--seal`.

Si el veredicto es `LISTO_CON_AJUSTES` o `NO_LISTO`, **no** escribas la atribución.

**Cómo decidir el veredicto (determinista — SSoT `kb-prd-expert` Regla 14):** `NO_LISTO` si quedan `[ASUNCIÓN]` sin confirmar o falta un elemento obligatorio / estructura; `LISTO_CON_AJUSTES` si hay contaminación **dura** (una fila de la tabla de `prd_prohibited_items.md`) que corregir; `LISTO` en cualquier otro caso. **No degrades `LISTO`** por notas *borderline* aceptables (p. ej. "bloqueo local en el dispositivo") ni por **huecos de negocio que resolverá `wf-spec-analyze`** — esos se **reportan** como notas, no bajan el veredicto. Solo lo bloqueante degrada. (Cierra el titubeo `LISTO` ↔ `LISTO_CON_AJUSTES` sobre un mismo estado limpio.)

Responde con este formato:

```markdown
## Revisión del PRD

### Veredicto general
LISTO / LISTO_CON_AJUSTES / NO_LISTO

> Con `[ASUNCIÓN]` sin confirmar, el veredicto NO puede ser `LISTO`.

### Estructura
- ...

### Frontera negocio/técnica
- ...

### Asunciones (anti-fabricación)
- `[ASN-XXX]` confirmadas: N · rechazadas: M · pendientes: K
- (si quedan pendientes) listarlas — el PRD no está listo hasta resolverlas

### Ajustes bloqueantes (degradan el veredicto)
1. ... (solo asunciones/estructura → `NO_LISTO`, o contaminación **dura** → `LISTO_CON_AJUSTES`; si no hay, "ninguno")

### Notas no bloqueantes (no cambian `LISTO`)
- Borderline aceptable (p. ej. "bloqueo local") · huecos de negocio que resolverá `wf-spec-analyze`

### Siguiente paso
- Si está listo: `/wf-spec-analyze <archivo_prd.md>`
- Si no está listo por contaminación técnica o estructura: corregir el PRD (manualmente o delegando a `prd-expert`) y volver a ejecutar `/wf-prd-review <archivo_prd.md>`
- Si la revisión revela que falta alcance comprometido, una capacidad necesita cambiar de fase, o una exclusión deja de ser válida: no se trata de un fix de redacción sino de un cambio de producto. Remite a `/wf-prd-change <archivo_prd.md> --new-reqs <cambio.md>` para formalizarlo con trazabilidad.
```

No inventes requisitos faltantes. Si hay huecos, señálalos como problemas de entrada.
