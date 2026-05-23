---
name: wf-prd-review
description: Revisión rápida de un PRD o documento de requisitos antes de entrar en la fase Spec. Comprueba si el documento está limpio, si explicita actores y alcance, y si su estructura es procesable por el pipeline SDD. Activa en frases como "revisa mi PRD", "¿este PRD está bien para empezar?", "haz preflight del PRD", "valida el documento de requisitos antes del spec".
argument-hint: "<archivo_prd.md>"
effort: medium
allowed-tools: [Read, Bash]
context: fork
agent: prd-expert
---

# Workflow: PRD Review

Tu objetivo es revisar si un PRD está preparado para entrar en el pipeline SDD. No generas Spec, no generas features y no corriges el documento por tu cuenta: emites un diagnóstico claro y accionable.

Usa `kb-prd-expert` como fuente autoritativa.

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

Si el nombre termina en `_spec.md`, `_plan.md` o `_tasks.md`, informa:
> "Este archivo parece un artefacto posterior del pipeline. `/wf-prd-review` opera sobre PRDs o documentos de requisitos iniciales."

---

## Paso 3: Leer el contenido

Lee el PRD completo.

---

## Paso 4: Revisar estructura y frontera

Evalúa el documento contra `kb-prd-expert`:
- ¿Describe un único producto o está partido artificialmente?
- ¿Los actores están explícitos?
- ¿El alcance dentro/fuera está claro?
- ¿Hay reglas de negocio transversales?
- ¿La estructura es procesable por el pipeline?

**Estructuras aceptables:**
- por actor
- por RFs numerados
- por secciones funcionales

No penalices la estructura elegida si el documento sigue siendo claro y trazable.

---

## Paso 5: Revisar contaminación técnica

Detecta fragmentos que deberían salir del PRD por pertenecer a Plan o Tasks:
- tecnologías
- arquitectura
- detalles de API o almacenamiento
- instrucciones de implementación

Para cada caso, cita el fragmento y explica por qué está fuera de frontera.

---

## Paso 6: Emitir veredicto

Responde con este formato:

```markdown
## Revisión del PRD

### Veredicto general
LISTO / LISTO_CON_AJUSTES / NO_LISTO

### Estructura
- ...

### Frontera negocio/técnica
- ...

### Problemas a corregir antes del Spec
1. ...

### Siguiente paso
- Si está listo: `/wf-spec-analyze <archivo_prd.md>`
- Si no está listo: corregir el PRD y volver a ejecutar `/wf-prd-review <archivo_prd.md>`
```

No inventes requisitos faltantes. Si hay huecos, señálalos como problemas de entrada.
