---
name: wf-spec-validate
description: "Audita uno o varios _spec.md ya generados para detectar regresiones de pureza, testabilidad o completitud, y sella el estado operativo de cada uno registrando quien lo aprobo."
when_to_use: "Activa en frases como 'valida el spec', 'valida todos los specs', 'comprueba si el spec sigue siendo valido', 'verifica el spec', 'audita el spec'."
argument-hint: "<archivo_spec.md> [<otro_spec.md> ...] | --all [--aprobador \"<nombre>\"] [--con-conflictos]"
effort: high
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# Workflow: VALIDATE

Tu rol es de **orquestador puro**: compruebas que el spec existe, delegas la auditoría al agente `sdd-spec-auditor`, presentas su informe y cierras el gate humano que sella el estado operativo. No auditas tú el contenido y **no escribes el spec**.

Este workflow corre en el **hilo principal** (igual que `wf-prd-review`, `wf-plan-validate` y `wf-qa-verify`, y **no** en `context: fork`) por una razón concreta ([[D-065]]): es un **gate de sellado**, y los gates de sellado registran **quién aprobó** (`kb-traceability-rules` Regla 10). Capturar esa identidad exige preguntar, y un subagente no puede. Mientras esto fue un fork, el spec era el único artefacto del pipeline que llegaba a `VALIDADO` sin que constara nadie.

**Regla de oro:** no hagas `Read` ni `cat` del spec. Lo que necesitas saber sale del informe de tu delegado y del sellador determinista ([[D-031]]/[[D-060]]). Esto vale **aunque las tools estén disponibles** — `allowed-tools` es declarativo, no una jaula ([[D-038]]).

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del spec a validar, **o varios** (separados por espacio), **o
`--all`** para todos los que siguen en borrador. Con `--all`, la lista sale del script, no de tu
lectura: los `features` del pendiente `validar` de
`sdd-project-status.py <raíz_spec> --spec-pending --json`, mapeados a su `Ruta spec` en el índice.
Si no hay argumento:
> "Necesito el path del spec que quieres validar."

Y dos opcionales (v0.128.0), que solo llegan desde una opción del cierre de la fase:
- **`--aprobador "<nombre>"`**: el usuario eligió una opción que dice *"si pasan la auditoría, quedan
  validadas a nombre de <nombre>"*. Es su aprobación de lo que pase: en el Paso 5 no la vuelves a
  preguntar. Nunca te lo auto-suministres.
- **`--con-conflictos`**: el cambio que se valida no ha pasado aún por la revisión de conflictos.
  La lanzas tú, en el mismo mensaje que las auditorías (Paso 3).

> **En lote ([[D-102]]): se audita y se sella cada spec por separado; lo único que se comparte es
> quién aprueba.** Un spec que sale con hallazgos bloqueantes o con el script en rojo **no se sella**
> y no para a los demás. Al final, un resumen: cuáles quedaron sellados y cuáles no, con su motivo.

---

## Paso 2: Verificar el archivo

```bash
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa con la ruta exacta y detén. Si no termina en `_spec.md`:
> "Esperaba un spec ya generado (`_spec.md`). Si lo que quieres es analizar un documento de requisitos, dímelo y hago el análisis previo."

---

## Paso 3: Delegar la auditoría (tool `Agent`, y esperar)

Delega con la tool `Agent` ([[D-043]]), `subagent_type: "sdd-spec-auditor"` y **`run_in_background: false`**, con el prompt:

  prompt: "Audita el spec <path>. Detecta primero el modo: si el header declara 'Modo: ligero', aplica las reglas de proporcionalidad de kb-spec-expert. Aplica sus 3 checks. Completitud: en standard los 8 elementos SDD; en ligero el núcleo de 4 (Actores, HUs, CAs, Fuera de Alcance) con las omitidas marcadas 'N/A — modo ligero' — una sección ausente sin esa marca ES un hallazgo. Pureza: consulta prohibited_items.md y error_patterns.md de kb-spec-expert y cita cualquier frase que viole la Prueba de Pureza. Testabilidad: cada CA con GIVEN/WHEN/THEN completo, verificable objetivamente y referenciando su HU padre. Estructura el informe según .claude/skills/wf-spec-validate/references/output_template.md. NO escribas ningún archivo: devuélveme el informe. Al terminar di explícitamente si hay hallazgos BLOQUEANTES o no, aplicando el umbral del Paso 4 de 'Cómo validar un Spec' de kb-spec-expert: bloquean SOLO un elemento obligatorio ausente, contaminación dura (fila de prohibited_items.md) o un CA que no se puede verificar tal como está escrito. NO bloquean las sugerencias de redacción, las notas borderline documentadas, los huecos que son materia de Plan, ni lo que ya dictamina sdd-seal.py --check (incompletos, gaps críticos, inferidos, asunciones sin rastro): eso lo mide el script, no tú. Lo que deja el spec prometiendo algo que no se probará (una regla sin CA, un ítem del checklist marcado que no se cumple) va en 'Sugerencias con arreglo', en llano y con su arreglo. Tus notas son solo de este spec: no recomiendes otras auditorías ni comentes otros artefactos. Cada hallazgo BLOQUEANTE, además, en una línea en llano para quien lo lee —qué pasa — cómo se arregla—, sin rutas ni números de línea: es lo que queda escrito en el spec."

**Con `--con-conflictos`**, en ese **mismo mensaje** emite también, por cada spec, la verificación de
sus conflictos: tool `Agent`, `subagent_type: "sdd-spec-auditor"`, `run_in_background: false`, con el
encargo *"Lee `.claude/skills/wf-spec-conflict/SKILL.md` y ejecuta sus pasos TÚ MISMO sobre: <path del
spec> --features-dir <directorio de features> --cambio <su análisis de cambio más reciente>. NO uses
el `Skill` tool"*. El análisis más reciente es el último `*_delta_analysis.md` de la carpeta del spec
(`ls -t <carpeta>/*_delta_analysis.md | head -1`). Auditar el spec y verificar sus conflictos no
dependen el uno del otro: en serie, la pasada 1 de `CU-3.ac (3)` esperó 5 minutos de más por vuelta.
Si una verificación devuelve un conflicto **nuevo** sobre un spec, ese spec no se sella en este lote:
dilo con el conflicto, y la lista de pendientes lo traerá.

**En lote**, emite las N llamadas `Agent` —una por spec, mismo prompt con su path— en un único
mensaje, **sin llamada de prueba**: lanzar una "a ver si va" y el resto después serializa igual
([[D-084]]). Los auditores no escriben nada, así que no hay nada que coordinar entre ellos.

**Has esperado cuando el informe está en tu contexto como resultado de tu propia llamada** ([[D-047]]). Si no lo tienes, **paras y lo dices**: no reconstruyes el veredicto leyendo el spec por tu cuenta.

---

## Paso 4: Presentar el informe

Imprime el informe del auditor tal como te lo dio. **No lo escribes en ningún archivo** ([[D-060]]): es un diagnóstico para el usuario, no un artefacto del proyecto.

---

## Paso 5: Sellar el estado y registrar quién aprueba

El estado del spec **solo** lo escribe el sellador determinista (autor≠verificador: el veredicto del auditor es necesario, no suficiente). Nunca edites la línea `Estado:` a mano.

> **Qué cuenta como bloqueante no lo decides aquí ([[D-076]]).** El umbral vive en
> `kb-spec-expert` (Paso 4 de «Cómo validar un Spec») y es cerrado: elemento obligatorio ausente ·
> contaminación dura · CA no verificable. Lo demás se reporta y **no degrada** el veredicto. Sin
> umbral escrito, la misma clase de hallazgo sella en una pasada y bloquea en la siguiente — medido
> en el PRD antes de [[D-035]], que es el espejo de esta regla.

**Con hallazgos bloqueantes** → reabre, **deja escrito por qué**, y detén:
```bash
!python3 .sdd/scripts/sdd-seal.py spec "<path>" --unseal --blocked "<hallazgo en llano — arreglo>" [--blocked …]
```
Un `--blocked` por hallazgo bloqueante, con lo que dijo el auditor **en llano** (qué pasa y cómo se
arregla: *"repite una regla de los movimientos que ya está en registro de movimientos — citarla en
vez de copiarla"*), sin rutas ni números de línea. Queda en la cabecera del spec, y de ahí lo leen
el resultado del lote, el mapa y la opción *"Corregir lo que pidió la validación"* (v0.127.1).
Medido en la pasada 2 de `CU-3.ac`: sin él, el cierre decía *"la auditoría encontró algo que
corregir, o no se aprobó"* y el mapa recomendaba validar otra vez lo que acababa de fallar.
Informa qué hay que corregir y que lo revalidas cuando esté.

**Sin hallazgos bloqueantes** → comprueba primero las condiciones mecánicas:
```bash
!python3 .sdd/scripts/sdd-seal.py spec "<path>" --check
```

- **exit 2** → el script dice qué condición falló (HU `[INCOMPLETO]`, gap `[CRÍTICO]` abierto, CA `[INFERIDO]`, `status_sync` no fiable, deriva de PRD, CA sin HU padre, o una asunción aplicada que no dejó rastro en `## Asunciones Aplicadas` — [[D-063]]). Trata cada `✗` como hallazgo, ejecuta `--unseal` y detén. **Un veredicto limpio del auditor no basta**: si el script deniega, manda el script.
  - **Excepción: si el `✗` es que el spec está `RETIRADO`, NO ejecutes `--unseal` ([[D-078]]).** Esa condición no es un hallazgo de calidad que se corrija reabriendo: la feature está dada de baja y no hay validación que reabrir. Informa de la baja con su traza `Retirada:` delante y detén ahí. (El script ya se niega —`--unseal` sobre un retirado sale `2` sin tocar nada—, pero decirle al usuario "he reabierto la validación" de algo que no se reabrió es la mitad del fallo que sigue siendo tuya.)
- **exit 2 y el único `✗` es el alcance derivado** (*"Alcance derivado formalizado o aceptado con
  nombre"*, [[D-102]]) → **no es un hallazgo de calidad, es una decisión de producto pendiente**: no
  ejecutes `--unseal` todavía. Pregunta con `AskUserQuestion`: *Formalizarlo antes en el PRD
  (Recomendado)* —el spec se queda en borrador y lo dices— o *Aceptarlo con nombre y sellar* —sigues
  con la captura del aprobador y sellas añadiendo
  `--accept-derived-scope "<nombre> (<fecha real de tu contexto>)"`—. El aviso del spec se queda: la
  aceptación no lo borra, deja constancia de que alguien lo vio y decidió seguir.
- **exit 0 con `--aprobador`** (v0.128.0) → sella con ese nombre y la fecha real de tu contexto, sin
  preguntar: el usuario lo aprobó al elegir la opción, que decía a nombre de quién y que solo se
  sella lo que pasa la auditoría. Dilo en la línea del resultado (*"validada a nombre de …"*).
- **exit 0** → captura la **identidad de quien aprueba** con `AskUserQuestion` ([[D-027]]): **precarga el nombre** con `!git config user.name` como default, rol opcional; si git no da nombre, cae al rol. Sella con ese valor:
  ```bash
  !python3 .sdd/scripts/sdd-seal.py spec "<path>" --seal --approved-by "<nombre> [(<rol>)] (<fecha real de tu contexto>)" [--suggest "<sugerencia>" …]
  ```
  Cada línea de **Sugerencias con arreglo** del auditor va en su `--suggest`, literal (v0.126.2):
  no bloquean, pero así quedan en la cabecera y la lista de pendientes las ofrece.
  **No autoapruebes.** Si el usuario no responde, no selles: el spec se queda en `BORRADOR`, que es el estado **correcto**, no un defecto. Si elige **no sellar todavía**, déjalo escrito: `sdd-seal.py spec "<path>" --unseal --not-approved` (v0.127.1), para que el cierre diga que pasó la auditoría y no se aprobó.
  **En lote**, el aprobador se captura **una sola vez** —después de las auditorías, antes del primer
  sello— y se reutiliza para cada spec que pase.
  **Una vez por lote, en cada lote** ([[D-111]]): un lote nuevo —otra validación, aunque sea de la
  misma sesión— vuelve a preguntarlo. Y la pregunta es **esta**, después de las auditorías: no la
  des por respondida porque una opción que **tú** escribiste dijera *"con la aprobación a tu
  nombre"*. La excepción es `--aprobador` (v0.128.0): esa opción la escribe el script, nombra al
  aprobador y dice que solo se sella lo que pasa la auditoría. Si en un lote anterior el aprobador llevaba rol, ofrécelo con el rol como primera
  opción. Medido en la pasada 4 de la tanda de continuación: el segundo lote se selló sin preguntar,
  y sin el rol del primero.
  **Salvo una cosa** (v0.126.2): si el lote viene de una decisión en la que el usuario **acaba de
  darse por responsable** —eligió *"Aceptarlo con mi nombre y validar"*— y en esta sesión ya hay un
  aprobador capturado, ese es el aprobador: dilo en la línea del resultado (*"aprobado por …, como
  en el lote anterior"*) y no lo vuelvas a preguntar. Elegir *validar* a secas no cuenta.
- **Contratos de modelos compartidos** ([[D-111]]): si el `✗` es la condición 10 —una petición al
  dueño sin atender, o el catálogo de orígenes del dueño sin la fila de otra feature— no es un
  hallazgo de calidad de este spec: es trabajo sobre el **dueño**, y la lista de pendientes lo trae
  como `peticion`. Ejecuta `--unseal`, dilo en una línea y cierra con la lista.
- **script ausente** → **no escribas el estado a mano**: informa de que falta `.sdd/scripts/sdd-seal.py` y que hay que reponer los scripts reinstalando el ecosistema.

> **Por qué el `Aprobado por:` lo estampa el script y no tú ([[D-065]]).** El dato es humano —lo acabas de capturar— pero escribirlo en el artefacto no es cosa del hilo principal ([[D-060]]). Se lo pasas al sellador, que es quien toca la cabecera. Mismo reparto que en el PRD, donde el sello lo estampa `sdd-prd-apply.py --seal "<valor>"` y no el orquestador.

---

## Paso 6: Informar el siguiente paso

- **Sellado** → dilo con su aprobador. Que se pueda **planificar** lo dice el `mapa` de la lista de pendientes, feature a feature ([[D-112]]): un spec sellado sin decisiones propias se planifica aunque otras features tengan decisiones abiertas.
- **En borrador** → enumera lo que falta y ofrécete a revalidarlo cuando esté corregido. Descríbele la acción en lenguaje natural, sin nombrar el workflow.
- **En lote, cerrando con la lista de pendientes** (lo normal) → el resultado del lote **encabeza
  el cierre** (v0.126.2): pide la lista con `--lote` y las rutas validadas, y copia `cierre` como
  siempre. Su pregunta ya empieza por qué se validó, quién lo aprobó, qué no y por qué, y las
  sugerencias que dejó la validación:

  ```bash
  !python3 .sdd/scripts/sdd-project-status.py <raíz_spec> --spec-pending --json --lote <spec1.md> <spec2.md> …
  ```

  Medido en `CU-3.ac`: la tabla se imprimía en una herramienta y main pasaba directo al mapa; las
  notas quedaron en un párrafo que se ve resumido.
- **En lote, sin cierre** (validación suelta) → la tabla la imprime el sellador; **cópiala tal cual** ([[D-107]]):

  ```bash
  !python3 .sdd/scripts/sdd-seal.py spec --report <spec1.md> <spec2.md> …
  ```

  **Cada spec, un argumento**: escribe las rutas una detrás de otra. No las metas en una variable
  entre comillas (`"$L"`), que el script recibe como **una sola** ruta y la tabla sale vacía o
  rota — medido en la pasada 4 de la tanda de continuación, que tuvo que repetirla.

  Una fila por spec: sellado con su aprobador, o el motivo —la condición que falla, o que pasa el
  sellador pero no se selló—. Si alguno no se selló por un **hallazgo de auditoría**, añade debajo una
  línea por hallazgo. Y si las auditorías dejaron **notas menores** que no bloquean, dilas en una
  línea, sin esconderlas. Como plantilla para componer a mano, la tabla no salió en dos pasadas
  seguidas de `CU-3.z`.

  Si un spec no se sella por una condición del sellador que no cuadra con su contenido, **dilo como
  posible fallo del sellador y no toques el spec para esquivarlo** ([[D-104]]).

**Y cierra con el siguiente pendiente de la fase** ([[D-102]]): `sdd-project-status.py <raíz_spec>
--spec-pending --json` y la pregunta sobre el primero, según la tabla de seguimiento de la guía de la
fase.
