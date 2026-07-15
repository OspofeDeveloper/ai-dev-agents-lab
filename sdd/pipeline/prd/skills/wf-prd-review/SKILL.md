---
name: wf-prd-review
description: "Revision rapida de un PRD o documento de requisitos antes de entrar en la fase Spec. Comprueba si el documento esta limpio, si explicita actores y alcance, y si su estructura es procesable por el pipeline SDD."
when_to_use: "Activa en frases como 'revisa mi PRD', '¿este PRD esta bien para empezar?', 'haz preflight del PRD', 'valida el documento de requisitos antes del spec'."
argument-hint: "<archivo_prd.md>"
effort: medium
allowed-tools: [Read, Write, Bash, Agent, AskUserQuestion]
user-invocable: true
---

# Workflow: PRD Review

Tu objetivo es revisar si un PRD está preparado para entrar en el pipeline SDD. No generas Spec, no generas features y no corriges el documento por tu cuenta: emites un diagnóstico claro y accionable. **Dos excepciones acotadas** en las que sí editas el PRD: (1) la confirmación de asunciones del Paso 5.5 — solo lo que el usuario decide explícitamente sobre cada `[ASUNCIÓN]`, nunca de tu cosecha; (2) el sello de aprobación del review cuando el veredicto es `LISTO` (Paso 6) — solo la línea `Aprobado por:` en el header. Ninguna otra reescritura.

Este workflow corre en el **hilo principal** (necesita confirmar las asunciones contigo en el Paso 5.5, vía `AskUserQuestion` — una tool que no existe dentro de un subagente). El **análisis experto** del PRD lo hace el agente `prd-expert`, que carga `kb-prd-expert` como fuente autoritativa; tú lo invocas vía la tool `Agent` (Paso 4) y gestionas los gates humanos y las ediciones del PRD aquí, en el hilo principal.

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

No leas el PRD completo aquí: su lectura y análisis se delegan al `prd-expert` (Paso 4), que recibe el **path** y lo lee con su propia `Read` + `kb-prd-expert`. El orquestador solo vuelve a tocar el fichero —de forma puntual y acotada— cuando tiene que **editarlo**: el gate de asunciones (Paso 5.5, solo si `grep -c` > 0) y el sello (Paso 6, solo si el veredicto es `LISTO`). Así el contexto del orquestador no carga el documento entero (que además se duplicaría en el prompt del agente).

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

---

## Paso 5.5: Confirmar asunciones del PRD (anti-fabricación)

`kb-prd-expert` Regla 12 obliga a que toda afirmación de negocio no trazable a la fuente esté marcada `[ASUNCIÓN]`. Este paso es el **gate de confirmación humana** de esas asunciones — el contrapunto a la generación: el autor marca lo que infirió, el review lo confirma o lo descarta.

**Detección determinista** (no a ojo). Usa `sdd-prd-ready.py`, que cuenta las marcas inline `[ASUNCIÓN]` (incluida la variante verbosa `[ASUNCIÓN: …]`) **excluyendo menciones en prosa** —callouts `>`, la nota de la sección— que inflan un `grep -c` crudo (la falsa-positiva de CU-2.b), y **verifica el invariante 1:1** (marcas inline == entradas `[ASN-XXX]`), reportando huérfanas:
```
!python3 .sdd/scripts/sdd-prd-ready.py "<path>" --json
!grep -n "\[ASUNCIÓN" "<path>"   # localización línea a línea para procesar cada una
```
El campo `inline_marks` es el conteo real; `ASSUMPTION_MISMATCH` señala una marca huérfana o una entrada sin marca — corrígela antes de seguir. Esto **cierra la verificación mecánica del 1:1** que antes dependía de un `grep` improvisado por el agente (reserva de CU-2.a/b). Si falta el script, cae al `grep -c "\[ASUNCIÓN"` como degradación.

- **`inline_marks` es `0`** → no hay asunciones pendientes; sigue al veredicto.
- **`inline_marks` `> 0`** → localiza la sección `## Asunciones del PRD` y procesa **cada `[ASN-XXX]` una a una con el usuario** (usa `AskUserQuestion` cuando haya varias): para cada una, presenta la afirmación inferida y su hueco, y pide decisión:
  - **Confirmar** → es correcta: marca la casilla `[x]` y elimina el marcador `[ASUNCIÓN]` inline de esa afirmación (pasa a ser hecho de negocio).
  - **Rechazar** → no es lo que el negocio quiere: elimina del PRD la afirmación y su marcador (y el contenido que dependía de ella).
  - **Editar** → el usuario da el dato real: sustituye la afirmación por el texto confirmado y quita el marcador.
  - Cuando una sección queda sin asunciones pendientes, elimina la entrada de `## Asunciones del PRD`; si no queda ninguna, elimina la sección entera.

A diferencia del resto de `wf-prd-review` (que solo diagnostica), aquí **sí** editas el PRD, pero solo lo que el usuario decide explícitamente sobre cada asunción — no reescrituras de tu cosecha.

**Efecto en el veredicto:** mientras queden marcadores `[ASUNCIÓN]` sin confirmar, el PRD **no puede ser `LISTO`** (es contenido fabricado sin validar). Si el usuario no quiere resolverlas ahora, el veredicto es `NO_LISTO` con las asunciones pendientes listadas.

---

## Paso 6: Emitir veredicto

Si el veredicto es `LISTO` (y por tanto no quedan `[ASUNCIÓN]` pendientes tras el Paso 5.5), registra la **atribución de aprobación humana** del gate antes de emitir el veredicto, según `kb-traceability-rules` Regla 10:

0. **Frontmatter completo antes de sellar.** Un PRD que se va a aprobar no debe tener campos obligatorios ausentes (`kb-prd-expert` Regla 3). Asegúralo de forma determinista:
   ```bash
   !python3 .sdd/scripts/sdd-prd-frontmatter.py "<path>" --fix
   ```
   Repone los campos mecánicos que falten (`type`, `version`, `created`, `status`). Si sale con exit ≠0 por falta de `product`, no selles: es un hueco de contenido que hay que resolver antes.
1. Captura el rol aprobador con `AskUserQuestion` (default `PM` / `Product Owner`), permitiendo confirmar el rol o dar nombre.
2. Si el usuario responde, escribe en el header/metadata del PRD (junto a versión/fecha del documento) la línea `Aprobado por: <rol> (<fecha real de tu contexto>)`. En re-revisión, sobrescribe la línea previa. **No autoapruebes**: si no hay respuesta, no escribas la línea.

Si el veredicto es `LISTO_CON_AJUSTES` o `NO_LISTO`, **no** escribas la atribución.

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

### Problemas a corregir antes del Spec
1. ...

### Siguiente paso
- Si está listo: `/wf-spec-analyze <archivo_prd.md>`
- Si no está listo por contaminación técnica o estructura: corregir el PRD (manualmente o delegando a `prd-expert`) y volver a ejecutar `/wf-prd-review <archivo_prd.md>`
- Si la revisión revela que falta alcance comprometido, una capacidad necesita cambiar de fase, o una exclusión deja de ser válida: no se trata de un fix de redacción sino de un cambio de producto. Remite a `/wf-prd-change <archivo_prd.md> --new-reqs <cambio.md>` para formalizarlo con trazabilidad.
```

No inventes requisitos faltantes. Si hay huecos, señálalos como problemas de entrada.
