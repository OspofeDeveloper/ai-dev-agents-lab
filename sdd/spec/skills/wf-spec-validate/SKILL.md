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
> "Uso: `/wf-spec-validate <archivo_spec.md>`"
> "Ejemplo: `/wf-spec-validate docs/requisitos_spec.md`"

---

## Paso 2: Verificar el archivo

Verifica que el archivo termina en `_spec.md`. Si no → informa:
> "Este skill espera un spec generado (`_spec.md`). Para analizar un PRD usa `/wf-spec-analyze`."

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

Imprime el informe directamente (no escribe ningún archivo).

- Si el resultado es **VÁLIDO**: confirma que el spec pasa los 3 checks y está listo para la siguiente fase
- Si el resultado es **REQUIERE_REVISIÓN**: indica los problemas encontrados y sugiere corregirlos manualmente antes de continuar
