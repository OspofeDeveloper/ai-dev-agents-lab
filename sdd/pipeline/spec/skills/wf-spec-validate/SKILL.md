---
name: wf-spec-validate
description: "Audita un _spec.md ya generado para detectar regresiones de pureza, testabilidad o completitud introducidas por ediciones manuales. No genera ningun archivo — imprime el informe directamente."
when_to_use: "Activa en frases como 'valida el spec', 'comprueba si el spec sigue siendo valido', 'verifica el spec', 'audita el spec'."
argument-hint: "<archivo_spec.md>"
effort: high
allowed-tools: [Read, Bash]
context: fork
agent: sdd-spec-auditor
user-invocable: true
---

# Workflow: VALIDATE

Tu objetivo es auditar un `_spec.md` ya generado para detectar regresiones de pureza, testabilidad o completitud introducidas por ediciones manuales. Usa `kb-spec-expert` para aplicar los 3 checks.

**No produces ningún archivo nuevo.** El informe se imprime directamente al usuario.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del spec a validar.

Si no hay argumento, informa al usuario:
> "Necesito el path del spec que quieres validar."

---

## Paso 2: Verificar el archivo

Verifica que el archivo termina en `_spec.md`. Si no → informa:
> "Esperaba un spec ya generado (`_spec.md`). Si lo que quieres es analizar un PRD, dímelo y hago el análisis previo."

Verifica que el archivo existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

---

## Paso 3: Leer el contenido

Lee el spec en su totalidad.

---

## Paso 4: Auditar el spec

Detecta primero el modo: si el header declara `Modo: ligero`, aplica las reglas de proporcionalidad de `kb-spec-expert` ("Modo ligero").

Aplica los 3 checks definidos en `kb-spec-expert`:

- **Check 1 — Completitud**: en standard, los 8 elementos SDD presentes; en ligero, el núcleo de 4 (Actores, HUs, CAs, Fuera de Alcance) y las secciones omitidas con `N/A — modo ligero` explícito — una sección ausente sin esa marca ES un hallazgo (consulta `kb-spec-expert` para las definiciones)
- **Check 2 — Pureza**: consulta `prohibited_items.md` y `error_patterns.md` del skill `kb-spec-expert`; cita cualquier frase que viole la Prueba de Pureza (idéntico en ambos modos)
- **Check 3 — Testabilidad**: cada CA tiene GIVEN/WHEN/THEN completo, es verificable objetivamente, y referencia su HU padre (`← HU-XXX`) (idéntico en ambos modos)

---

## Paso 5: Formato del informe

Consulta `${CLAUDE_SKILL_DIR}/references/output_template.md` para la estructura exacta del informe de validación.

---

## Paso 6: Informar al usuario

Imprime el informe directamente: **el informe no se escribe en ningún archivo**.

Lo que sí cambia en el spec es su **estado operativo**, y no lo escribes tú ([[D-061]]):

```bash
# veredicto sin hallazgos bloqueantes
!python3 .sdd/scripts/sdd-seal.py spec "<path_del_spec>" --seal
# con hallazgos bloqueantes
!python3 .sdd/scripts/sdd-seal.py spec "<path_del_spec>" --unseal
```

- **exit 0** → el spec queda `VALIDADO`. Díselo al usuario y que ya puede planificar sobre él.
- **exit 2** → el script muestra qué condición mecánica falló (HU `[INCOMPLETO]`, gap `[CRÍTICO]`
  abierto, CA `[INFERIDO]`, `status_sync` no fiable, deriva de PRD, CA sin HU padre, o una asunción
  aplicada que no dejó rastro en `## Asunciones Aplicadas` — [[D-063]]). El spec queda en
  `BORRADOR`. Trata cada `✗` como hallazgo.
- **script ausente** → **no escribas el estado a mano**: informa de que falta
  `.sdd/scripts/sdd-seal.py` y que hay que reponer los scripts reinstalando el ecosistema.

> **Por qué esto no rompe tu read-only ([[D-051]]).** Tú no modificas el spec: **ejecutas un
> verificador** que comprueba condiciones y escribe una marca de estado. Es el mismo reparto
> autor≠verificador del plan — tu veredicto experto no basta para sellar, y por eso el sello es
> una marca fiable. Lo que sigues sin tocar es el **contenido** de lo que auditas.


- Si el resultado es **VÁLIDO**: confirma que el spec pasa los 3 checks y está listo para la siguiente fase
- Si el resultado es **REQUIERE_REVISIÓN**: indica los problemas encontrados y sugiere corregirlos manualmente antes de continuar
