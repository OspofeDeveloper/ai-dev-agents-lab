---
name: wf-spec-map
description: Genera un mapa funcional del proyecto desde un PRD. Extrae intenciones funcionales (no la estructura del documento), identifica features, interacciones entre ellas, scope y flags de riesgo. Produce un `_project_map.md` compacto para que el programador valide la arquitectura funcional antes de analizar features en detalle. Activa en frases como "genera el mapa del proyecto", "¿qué features tiene este PRD?", "mapea las features del PRD", "identifica las features del sistema", "genera el project map".
argument-hint: "<prd.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-analyst
---

# Workflow: SPEC-MAP

Tu objetivo es producir un `_project_map.md` compacto que le permita al programador ver de un vistazo qué features compone el sistema, cómo interactúan y dónde están los riesgos — sin necesidad de leer el PRD entero.

**Regla fundamental:** Extraes intenciones funcionales, no secciones del documento. Un PRD que habla de "microservicio de autenticación" produce una feature llamada "Acceso de Usuario". La nomenclatura técnica del PRD no debe contaminar el mapa.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del PRD.

Si no hay argumento, informa al usuario:
> "Uso: `/wf-spec-map <prd.md>`"
> "Ejemplo: `/wf-spec-map docs/requisitos.md`"

---

## Paso 2: Verificar el archivo

Verifica que el archivo existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

---

## Paso 3: Leer el PRD

Lee el archivo en su totalidad.

---

## Paso 4: Identificar actores del proyecto

Extrae los actores del sistema completo: quién usa el sistema y con qué rol. Estos serán los actores candidatos para asignar a las features.

---

## Paso 5: Extraer intenciones funcionales → features candidatas

Para cada bloque temático del PRD, extrae la intención funcional del usuario (no el título de la sección ni el término técnico). Genera un nombre en kebab-case que describa qué resuelve para el usuario.

Para cada feature candidata, aplica el test de independencia de `kb-decompose-expert`:
- ¿Tiene actor principal identificable?
- ¿Sus Journeys son funcionalmente independientes de otras features candidatas?
- ¿Se pueden derivar al menos 3 CAs verificables?

Si una candidata no pasa el test → fusionarla con la más cercana semánticamente y documentar la decisión en el flag de riesgo correspondiente.

---

## Paso 6: Detectar interacciones entre features

Para cada par de features, determina si hay:
- **dependencia**: una feature no puede ejecutarse sin que otra haya completado algo
- **modelo compartido**: ambas features operan sobre la misma entidad de dominio

Documenta las interacciones y los shared models candidatos con su owner candidato (la feature que crea o define el modelo, usando los criterios de `kb-decompose-expert`).

---

## Paso 7: Definir el scope del proyecto

Extrae del PRD:
- Qué está explícitamente **dentro** del sistema (funcionalidad declarada)
- Qué está **implícito** pero no declarado (asunciones de scope que podrían ser gaps)
- Qué está explícitamente **fuera** (si el PRD lo declara)

---

## Paso 8: Levantar flags de riesgo

Identifica situaciones que complicarán el análisis por feature en el siguiente paso:
- Features con muy poca información en el PRD (riesgo ALTO de gaps críticos)
- Secciones del PRD con contaminación técnica severa (riesgo de mal scope)
- Features cuyo scope se solapa con otra feature (riesgo de cross-feature contamination)
- Shared models con ownership ambiguo

Clasifica cada flag como ALTO (bloquea la siguiente fase si no se resuelve) o MEDIO (informativo).

---

## Paso 9: Generar el project map

Produce el `_project_map.md` siguiendo la estructura de `references/project_map_template.md`.

Determina el path de salida: mismo directorio que el PRD + nombre base + `_project_map.md`.
- Ejemplo: `docs/requisitos.md` → `docs/requisitos_project_map.md`

---

## Paso 10: Escribir el resultado

Escribe el archivo generado.

---

## Paso 11: Informar al usuario

Tras escribir el archivo, informa:
- Path del mapa generado
- Número de features identificadas con sus nombres
- Flags de riesgo detectados (resumidos)
- Siguiente paso:
  > "Revisa `<path>_project_map.md`. Valida que las features son las correctas (puedes editar directamente). Cuando el mapa refleje la arquitectura funcional correcta, ejecuta:"
  > ```
  > /wf-spec-map-analyze <prd.md>
  > ```
