---
name: wf-spec-decompose
description: Parte un Spec monolítico validado en Specs por feature independientes. Genera un _features.md con el índice de features y shared models, y una carpeta features/<nombre>/<nombre>_spec.md por cada feature. Activa en frases como "parte el spec en features", "descompón el spec por features", "separa el spec en specs individuales", "crea un spec por feature", "divide el spec monolítico". No activa para analizar o generar specs (usa wf-spec-analyze) ni para planificar (usa wf-prepare-plan).
argument-hint: "<archivo_spec.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-analyst
---

# Workflow: DECOMPOSE

Tu objetivo es partir el Spec monolítico en Specs por feature independientes y autocontenidos. Usa `kb-decompose-expert` para cada decisión de partición y `kb-spec-expert` para verificar que cada spec de feature resultante es un Spec SDD válido.

**Regla de oro:** Nunca inventas — solo filtras y renumeras. Los HUs, Journeys y CAs del spec de feature son copias literales del spec monolítico, nunca reescrituras.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del archivo spec.

Si no hay argumento, informa al usuario:
> "Uso: `/wf-spec-decompose <archivo_spec.md>`"
> "Ejemplo: `/wf-spec-decompose docs/proyecto_spec.md`"

---

## Paso 2: Verificar el Spec

1. Verifica que el archivo existe.
2. Verifica que el nombre termina en `_spec.md`. Si no → informa:
   > "Este archivo no parece un Spec procesado. Primero genera el spec con `/wf-spec-finalize <archivo.md>`"
3. Lee el archivo completo.
4. Comprueba si contiene `_(pendiente)_` sin responder (excluyendo HUs marcadas `[INCOMPLETO]`). Si hay `_(pendiente)_` fuera de contexto `[INCOMPLETO]` → lista cuáles y detén:
   > "El Spec tiene items pendientes sin procesar. Ejecuta `/wf-spec-finalize` primero."
5. Si hay HUs marcadas `[INCOMPLETO]` → informa al usuario: "El Spec tiene X HUs marcadas `[INCOMPLETO]`. Se propagarán a los feature specs correspondientes." **Continúa.**
5. Verifica que contiene evidencia de Spec SDD válido (presencia de "Criterios de Aceptación" e "Historias de Usuario"). Si no → informa:
   > "Este archivo no parece un Spec SDD procesado. Primero ejecuta `/wf-spec-finalize <archivo.md>`"

---

## Paso 3: Identificar y validar features

Usando las reglas de `kb-decompose-expert` (cohesión funcional, no secciones del documento):

1. **Identificar features** candidatas
2. **Validar cada feature candidata** contra los 3 criterios: Journeys independientes, mínimo 3 CAs propios, actor claro
3. **Declarar shared models**: para cada modelo que aparezca en más de una feature, determinar su owner usando las reglas de `kb-decompose-expert`

---

## Paso 4: Ownership checkpoint (bloqueo si hay ambigüedad)

Antes de generar los artefactos, verifica los shared models:

1. Busca cualquier modelo que tenga owner ambiguo, marcado como "?" o sin desempate explícito.

2. **Si hay modelos sin owner definitivo:**
   - Presenta la tabla al usuario con los modelos ambiguos:
     ```
     | Modelo | Candidatos | Criterio aplicable (kb-decompose-expert) |
     ```
   - Para cada modelo, aplica el criterio de desempate de `kb-decompose-expert` y explica al usuario cuál candidato sale ganador y por qué
   - **Espera respuesta del usuario** confirmando o corrigiendo el owner propuesto antes de continuar

3. **Si todos los modelos tienen owner claro** → continúa directamente al Paso 5.

---

## Paso 5: Generar los artefactos

### Restricciones de contenido

- Los HUs, Journeys y CAs se copian literalmente del spec monolítico — nunca reescribir
- Los CAs de cada feature se renumeran desde CA-001 (la numeración es local a la feature)
- Si hay duda sobre si un elemento pertenece a una feature → incluirlo (no omitir)
- Los actores de cada feature spec son un subconjunto filtrado de los actores del spec monolítico
- Las HUs marcadas `[INCOMPLETO]` se copian con su marca intacta al feature spec correspondiente

### Formatos

- Para el índice de features: consulta `references/features_template.md`
- Para cada spec de feature: consulta `references/feature_spec_template.md`
- Para el README de cada carpeta de feature: consulta `references/feature_readme_template.md`

Por cada feature generada, produce también un `README.md` en su carpeta. El README incluye: Feature ID, actor principal, path del spec, tabla de shared models (propios y referenciados) y la tabla de artefactos con el estado inicial (spec=✓, plan=—, tasks=—). Las dependencias entre features se infieren de los shared models: una feature que solo *referencia* un modelo depende de la feature que lo *ownnea*.

---

## Paso 6: Escribir los artefactos

**Artefacto 1 — Índice de features**

Path: mismo directorio que el spec + nombre base + `_features.md`
- Ejemplo: `docs/proyecto_spec.md` → `docs/proyecto_features.md`

**Artefacto 2 — Specs y READMEs por feature**

Para cada feature:
1. Directorio: `<mismo_directorio_del_spec>/features/<nombre-feature>/`
2. Crear el directorio si no existe
3. Escribir `<nombre-feature>_spec.md`
4. Escribir `README.md`

Ejemplo para `docs/proyecto_spec.md`:
```
docs/proyecto_features.md
docs/features/authentication/authentication_spec.md
docs/features/authentication/README.md
docs/features/services/services_spec.md
docs/features/services/README.md
```

**Artefacto 3 — Trazabilidad RF → HU → Feature en `_features.md`**

Lee la sección `## Anexo: Trazabilidad RF → HU` del spec monolítico. Esta sección contiene la tabla de mapeo RF→HU generada por `wf-spec-finalize`.

**Si el spec contiene el anexo:**
- Enriquece cada fila añadiendo dos columnas: Feature (nombre de la feature asignada) y Estado (`activo`)
- Genera la tabla completa `## Trazabilidad RF → HU → Feature` en `_features.md` (ver template)
- Genera la tabla `## Cobertura por RF` completando la columna "Features involucradas"
- Genera la sección `## Historial de cambios` con una fila: fecha de hoy, tipo "decompose", descripción "Features asignadas desde wf-spec-decompose"

**Si el spec NO contiene el anexo** (generado por una versión anterior de finalize):
- Emite un aviso no bloqueante al usuario (se incluirá en el Paso 8): "El spec no contiene el anexo de trazabilidad RF→HU. La sección de trazabilidad de `_features.md` quedará vacía. Puedes regenerar el spec con `/wf-spec-finalize` para obtener la trazabilidad."
- Genera `_features.md` sin las secciones de trazabilidad

---

**Artefacto 4 — Archivar el spec monolítico**

Añade al inicio del spec monolítico (antes del encabezado `# Spec:`) el siguiente banner:

```
> ⚠️ **ARCHIVO** — Este spec monolítico ha sido descompuesto en features independientes.
> Consulta `<basename>_features.md` como hub del proyecto y `features/` para los specs individuales.
> Fecha de archivo: [YYYY-MM-DD]

```

No modifiques ningún otro contenido del spec.

---

## Paso 7: Verificación automática de conflictos (no bloqueante)

Si se generaron **2 o más features**, ejecuta el workflow `wf-spec-conflict` pasándole el contenido de todos los specs de feature generados.

- Si detecta conflictos → escribe el informe en `<directorio_base>_conflict_report.md` e incluye un aviso en el Paso 8.
- Si no detecta conflictos → menciona brevemente en el Paso 8 que no se detectaron conflictos.

Este paso es **informativo y no bloquea** el flujo.

---

## Paso 8: Informar al usuario

- Path del `_features.md` generado (Project Hub)
- Lista de features identificadas con sus rutas
- Tabla de shared models detectados
- Estado de la trazabilidad:
  - Si se incluyó trazabilidad en `_features.md`: "✓ Trazabilidad RF→HU→Feature integrada en `_features.md`."
  - Si el spec no tenía anexo de trazabilidad: "⚠ `_features.md` generado sin trazabilidad. Regenera el spec con `/wf-spec-finalize` para obtener la trazabilidad."
- Estado del archivo del spec monolítico: "✓ Spec monolítico archivado con banner de aviso."
- Resultado de la verificación de conflictos:
  - Sin conflictos: "✓ Sin conflictos detectados entre los specs generados."
  - Con conflictos: "⚠ Se detectaron conflictos. Revisa `<path>_conflict_report.md` antes de continuar con `/wf-prepare-plan` en las features afectadas."
- Siguiente paso:
  > "`<path>_features.md` es tu hub del proyecto. Revísalo y ajusta el scope si es necesario."
  > "Para ver qué features están listas y el orden recomendado:"
  > ```
  > /wf-spec-readiness <path>/features/
  > ```
  > "Para planificar una feature lista:"
  > ```
  > /wf-prepare-plan generate features/<nombre>/<nombre>_spec.md
  > ```
