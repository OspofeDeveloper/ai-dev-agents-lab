---
name: wf-spec-validate
description: "Audita un _spec.md ya generado para detectar regresiones de pureza, testabilidad o completitud, y sella su estado operativo registrando quien lo aprobo."
when_to_use: "Activa en frases como 'valida el spec', 'comprueba si el spec sigue siendo valido', 'verifica el spec', 'audita el spec'."
argument-hint: "<archivo_spec.md>"
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

Extrae de `$ARGUMENTS` el path del spec a validar. Si no hay argumento:
> "Necesito el path del spec que quieres validar."

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

  prompt: "Audita el spec <path>. Detecta primero el modo: si el header declara 'Modo: ligero', aplica las reglas de proporcionalidad de kb-spec-expert. Aplica sus 3 checks. Completitud: en standard los 8 elementos SDD; en ligero el núcleo de 4 (Actores, HUs, CAs, Fuera de Alcance) con las omitidas marcadas 'N/A — modo ligero' — una sección ausente sin esa marca ES un hallazgo. Pureza: consulta prohibited_items.md y error_patterns.md de kb-spec-expert y cita cualquier frase que viole la Prueba de Pureza. Testabilidad: cada CA con GIVEN/WHEN/THEN completo, verificable objetivamente y referenciando su HU padre. Estructura el informe según .claude/skills/wf-spec-validate/references/output_template.md. NO escribas ningún archivo: devuélveme el informe. Al terminar di explícitamente si hay hallazgos BLOQUEANTES o no, aplicando el umbral del Paso 4 de 'Cómo validar un Spec' de kb-spec-expert: bloquean SOLO un elemento obligatorio ausente, contaminación dura (fila de prohibited_items.md) o un CA que no se puede verificar tal como está escrito. NO bloquean las sugerencias de redacción, las notas borderline documentadas, los huecos que son materia de Plan, ni lo que ya dictamina sdd-seal.py --check (incompletos, gaps críticos, inferidos, asunciones sin rastro): eso lo mide el script, no tú."

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

**Con hallazgos bloqueantes** → reabre y detén:
```bash
!python3 .sdd/scripts/sdd-seal.py spec "<path>" --unseal
```
Informa qué hay que corregir y que lo revalidas cuando esté.

**Sin hallazgos bloqueantes** → comprueba primero las condiciones mecánicas:
```bash
!python3 .sdd/scripts/sdd-seal.py spec "<path>" --check
```

- **exit 2** → el script dice qué condición falló (HU `[INCOMPLETO]`, gap `[CRÍTICO]` abierto, CA `[INFERIDO]`, `status_sync` no fiable, deriva de PRD, CA sin HU padre, o una asunción aplicada que no dejó rastro en `## Asunciones Aplicadas` — [[D-063]]). Trata cada `✗` como hallazgo, ejecuta `--unseal` y detén. **Un veredicto limpio del auditor no basta**: si el script deniega, manda el script.
  - **Excepción: si el `✗` es que el spec está `RETIRADO`, NO ejecutes `--unseal` ([[D-078]]).** Esa condición no es un hallazgo de calidad que se corrija reabriendo: la feature está dada de baja y no hay validación que reabrir. Informa de la baja con su traza `Retirada:` delante y detén ahí. (El script ya se niega —`--unseal` sobre un retirado sale `2` sin tocar nada—, pero decirle al usuario "he reabierto la validación" de algo que no se reabrió es la mitad del fallo que sigue siendo tuya.)
- **exit 0** → captura la **identidad de quien aprueba** con `AskUserQuestion` ([[D-027]]): **precarga el nombre** con `!git config user.name` como default, rol opcional; si git no da nombre, cae al rol. Sella con ese valor:
  ```bash
  !python3 .sdd/scripts/sdd-seal.py spec "<path>" --seal --approved-by "<nombre> [(<rol>)] (<fecha real de tu contexto>)"
  ```
  **No autoapruebes.** Si el usuario no responde, no selles: el spec se queda en `BORRADOR`, que es el estado **correcto**, no un defecto.
- **script ausente** → **no escribas el estado a mano**: informa de que falta `.sdd/scripts/sdd-seal.py` y que hay que reponer los scripts reinstalando el ecosistema.

> **Por qué el `Aprobado por:` lo estampa el script y no tú ([[D-065]]).** El dato es humano —lo acabas de capturar— pero escribirlo en el artefacto no es cosa del hilo principal ([[D-060]]). Se lo pasas al sellador, que es quien toca la cabecera. Mismo reparto que en el PRD, donde el sello lo estampa `sdd-prd-apply.py --seal "<valor>"` y no el orquestador.

---

## Paso 6: Informar el siguiente paso

- **Sellado** → dilo con su aprobador, y que ya se puede planificar sobre él.
- **En borrador** → enumera lo que falta y ofrécete a revalidarlo cuando esté corregido. Descríbele la acción en lenguaje natural, sin nombrar el workflow.
