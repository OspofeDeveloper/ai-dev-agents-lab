---
name: wf-prd-create
description: Crea un PRD inicial guiado para el pipeline SDD. Puede partir de notas, un brief o una idea suelta, y genera un `prd.md` limpio, orientado a negocio y listo para revisión. Activa en frases como "ayúdame a crear el PRD", "genera un PRD", "construye el documento de requisitos", "convierte estas notas en un PRD".
argument-hint: "<directorio_proyecto> [--source <notas.md>] [--output <prd.md>]"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
agent: prd-expert
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

Lee el archivo completo y úsalo como material base para el PRD.

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
- el contenido fuente disponible
- la ruta objetivo
- la instrucción de producir un PRD completo en Markdown

Indícale explícitamente:
- que use `kb-prd-expert` como SSoT
- que no invente decisiones de negocio ausentes
- que convierta detalles técnicos en observaciones a excluir, no en contenido del PRD
- que mantenga una estructura compatible con `wf-spec-analyze`

---

## Paso 5: Determinar path de salida

Si el usuario proporcionó `--output`, úsalo.

Si no lo proporcionó, escribe por defecto:
```
<directorio_proyecto>/prd.md
```

---

## Paso 6: Escribir el PRD

Escribe el documento generado en el path de salida.

El resultado debe incluir como mínimo:
- `# PRD: ...`
- `## Resumen Ejecutivo`
- `## Actores`
- `## Alcance`
- `### Dentro del Alcance`
- `### Fuera del Alcance`
- `## Reglas de Negocio Transversales`

---

## Paso 7: Informar al usuario

Tras escribir el archivo, informa:
- path del PRD generado
- si se usó o no archivo fuente
- si quedaron huecos explícitos que el usuario debería revisar manualmente

**Siguiente paso recomendado:**
> "Revisa el PRD y luego ejecuta `/wf-prd-review <path/prd.md>` para validar la entrada antes del análisis SDD."
