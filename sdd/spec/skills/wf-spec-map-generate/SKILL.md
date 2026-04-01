---
name: wf-spec-map-generate
description: Genera los Specs SDD de cada feature directamente desde sus `_analysis.md` respondidos, sin spec monolítico intermedio. Produce `features/<X>/<X>_spec.md` por cada feature del mapa. Precondición: todas las features deben tener sus gaps `[CRÍTICO]` respondidos. Activa en frases como "genera los specs de las features", "crea los specs desde el mapa", "finaliza los specs de las features", "genera los specs desde los análisis respondidos".
argument-hint: "<prd.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-analyst
---

# Workflow: SPEC-MAP-GENERATE

Tu objetivo es generar un Spec SDD completo y válido por cada feature del mapa, usando el PRD original + el project map + el `_analysis.md` respondido de cada feature. El output es directamente specs por feature, sin intermediarios.

**Regla fundamental:** No inventas. Integras las respuestas del programador exactamente como fueron escritas, sin interpretarlas ni expandirlas. Si el programador respondió con una frase, esa frase va al spec sin modificación.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del PRD.

Si no hay argumento, informa al usuario:
> "Uso: `/wf-spec-map-generate <prd.md>`"
> "Ejemplo: `/wf-spec-map-generate docs/requisitos.md`"

---

## Paso 2: Verificar precondiciones

1. Verifica que el PRD existe.
2. Construye el path del project map: mismo directorio + nombre base + `_project_map.md`.
3. Verifica que el project map existe. Si no → informa:
   > "No se encontró el project map. Asegúrate de haber ejecutado `/wf-spec-map` y `/wf-spec-map-analyze` primero."
4. Lee el project map y extrae la lista de features (excluyendo las `[EXCLUIDA]`).
5. Para cada feature, construye el path de su `_analysis.md`:
   `<directorio_del_prd>/features/<nombre-feature>/_analysis.md`
6. Verifica que todos los `_analysis.md` existen. Si falta alguno → informa qué features no tienen análisis y detén:
   > "Las siguientes features no tienen `_analysis.md`. Ejecuta `/wf-spec-map-analyze <prd.md>` para generarlos: [lista]"
7. Lee todos los `_analysis.md`.
8. Comprueba si algún `_analysis.md` contiene `[CRÍTICO]_(pendiente)_`. Si los hay → lista las features bloqueadas y detén:
   > "Las siguientes features tienen gaps críticos sin resolver. Edita sus `_analysis.md` y responde todos los gaps `[CRÍTICO]` antes de continuar:"
   > [tabla: Feature | Path del _analysis.md | Número de CRÍTICOS pendientes]

---

## Paso 3: Leer el PRD

Lee el PRD en su totalidad.

---

## Paso 4: Generar el spec de cada feature

Para cada feature del mapa (en orden de ID):

### 4a. Construir el contenido del spec

Usando el PRD + project map + `_analysis.md` respondido de esta feature:

1. Extrae la información del PRD relevante al scope de esta feature (las mismas secciones que `wf-spec-map-analyze` usó para el análisis).
2. Integra las respuestas del programador de los gaps:
   - Respuestas a gaps `[CRÍTICO]`: se integran tal como fueron escritas, sin interpretación.
   - Gaps `[INFORMATIVO]` sin responder: aplica la asunción por defecto declarada en el `_analysis.md`.
3. Construye los 8 elementos SDD siguiendo `kb-spec-expert`:
   - **Actores**: subconjunto filtrado al scope de esta feature
   - **Historias de Usuario**: derivadas del scope + respuestas del programador
   - **Recorridos de Usuario**: paso a paso, incluyendo flujos alternativos
   - **Resultados y Éxito**: definición observable de "hecho" desde la perspectiva del usuario
   - **Instrucciones Inambiguas**: reglas de comportamiento + tabla de destinos de navegación
   - **Criterios de Aceptación**: GIVEN/WHEN/THEN, cada uno con referencia `← HU-XXX`
   - **Checklist de Validación**: auto-marcado según el estado real del spec
   - **Fuera de Alcance**: exclusiones funcionales explícitas (sin tecnicismos)

### 4b. Aplicar Prueba de Pureza

Antes de escribir el spec, aplica la Prueba de Pureza al contenido generado. Consulta `kb-spec-expert`. Si se introdujo contaminación técnica durante la generación → corrígela antes de continuar.

### 4c. Documentar asunciones aplicadas

Si se aplicaron asunciones por defecto para gaps `[INFORMATIVO]` sin responder, añade al final del spec una sección `## Asunciones Aplicadas` con cada asunción documentada.

### 4d. Estructura del header

```markdown
# Spec: [Nombre de la Feature]
> Versión: 1.0 | Fecha: [YYYY-MM-DD]
> Generado via: spec-map-generate desde [path/prd.md]
> Project Map: [path/prd_project_map.md]
> Feature ID: F-00X
> PRD origen: [path/prd.md]
```

### 4e. Generar el README de la feature

Produce el `README.md` de la feature siguiendo la estructura de `references/feature_readme_template.md`. Usa:
- Feature ID: el ID del mapa
- Actor principal: del spec generado
- PRD origen: path del PRD usado
- Artefactos: Spec ✓, Plan —, Tasks —
- Dependencias: inferidas de las interacciones del project map

---

## Paso 5: Actualizar el índice de features

Busca si existe un `*_features.md` en el directorio del PRD:
- **Si existe**: léelo y actualiza las entradas de las features generadas (estado, paths).
- **Si no existe**: genera un `_features.md` nuevo con todas las features del mapa. Incluye la tabla de shared models extraída del project map.

Usa como referencia la estructura de `_features.md` descrita en `kb-decompose-expert`.

---

## Paso 6: Escribir los artefactos

Para cada feature, escribe (crea directorios si no existen):
1. `features/<nombre-feature>/<nombre-feature>_spec.md`
2. `features/<nombre-feature>/README.md`

Y en el directorio del PRD:
3. `<nombre-base>_features.md` (nuevo o actualizado)

---

## Paso 7: Verificación automática de conflictos (no bloqueante)

Si se generaron **2 o más features**, ejecuta el workflow `wf-spec-conflict` pasándole el contenido de todos los specs generados.

- Si detecta conflictos → escribe el informe en `<directorio_base>_conflict_report.md` e incluye un aviso en el informe final.
- Si no hay conflictos → mencionar brevemente en el informe final.

Este paso es informativo y no bloquea el flujo.

---

## Paso 8: Informar al usuario

Tras escribir todos los artefactos, informa:
- Lista de specs generados con sus paths
- Path del `_features.md` creado o actualizado
- Tabla de shared models (si los hay)
- Resultado de la verificación de conflictos
- Si se aplicaron asunciones: mencionar en qué features y cuántas
- Siguiente paso:
  > "Revisa los specs generados. Para cada feature, ejecuta:"
  > ```
  > /wf-spec-validate features/<nombre>/<nombre>_spec.md
  > ```
  > "Si los specs están validados, continúa con el plan:"
  > ```
  > /prepare-plan generate features/<nombre>/<nombre>_spec.md
  > ```
  > "Empieza por las features owner de shared models."
