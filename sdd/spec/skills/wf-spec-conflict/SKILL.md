---
name: wf-spec-conflict
description: "Detecta conflictos entre Specs SDD de un mismo proyecto: HUs duplicadas, CAs contradictorios, scope overlap, shared models inconsistentes."
when_to_use: "Activa en frases como 'verifica conflictos entre specs', 'hay conflictos entre features', 'comprueba si este spec choca con los existentes', 'detecta inconsistencias entre specs'."
argument-hint: "<feature_spec.md> --features-dir <path/features/>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-auditor
---

# Workflow: CONFLICT

Tu objetivo es detectar inconsistencias entre los Specs SDD de un mismo proyecto que podrían derivar en comportamiento indefinido, implementación duplicada o gaps funcionales no cubiertos. Usa `kb-conflict-expert` para las 5 reglas de detección y `kb-spec-expert` como referencia estructural.

**Regla de oro:** El informe es informativo, no bloqueante. Tu rol es detectar y describir — la decisión de cómo resolver cada conflicto la toma el humano. El informe siempre debe dejar un estado inequívoco: `SIN_CONFLICTOS` o `CONFLICTOS_DETECTADOS`.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del spec objetivo**: el primer argumento. Puede ser un `_spec.md` específico o `.` para verificar todos los specs de un directorio.
- **Directorio de features**: el argumento después de `--features-dir`

Si no hay `--features-dir`, intenta inferir el directorio de features como `features/` relativo al directorio del spec objetivo.

Si no hay argumento, informa al usuario:
> "Uso: `/wf-spec-conflict <feature_spec.md> --features-dir <path/features/>`"
> "Ejemplo: `/wf-spec-conflict features/auth/auth_spec.md --features-dir features/`"

---

## Paso 2: Localizar todos los specs

1. Verifica que el spec objetivo existe.
2. Busca todos los archivos `*_spec.md` dentro del directorio `--features-dir` (un nivel de profundidad: `features/*/<nombre>_spec.md`).
3. Si no hay specs en el directorio → informa: "No se encontraron specs en `<features-dir>`. Asegúrate de haber ejecutado `/wf-spec-features-first` o `/wf-spec-fast-track` o de que la ruta es correcta."
4. Si solo hay 1 spec en total (contando el objetivo) → informa: "Solo hay 1 spec. Se necesitan al menos 2 specs para verificar conflictos."

---

## Paso 3: Leer todos los specs

Lee el contenido completo de:
- El spec objetivo
- Todos los specs encontrados en el directorio de features (excluyendo el spec objetivo si ya está incluido)

---

## Paso 4: Inventariar todos los specs

Para cada spec, extrae internamente (no en el output):
- Feature ID y nombre
- Lista de actores
- Lista de HUs con sus IDs, actores y objetivos funcionales
- Lista de CAs con sus IDs, GIVEN/WHEN/THEN y HU padre
- Lista de Journeys con sus pasos principales
- Modelos de dominio mencionados (tanto propios como referenciados como shared)
- Sección Fuera de Alcance

---

## Paso 5: Aplicar las 5 reglas de kb-conflict-expert

Aplica cada regla consultando `kb-conflict-expert` y busca conflictos entre cada par de specs:

1. **HUs duplicadas**: compara actores + verbos + objetivos entre todos los pares de features
2. **CAs contradictorios**: compara GIVEN+WHEN entre todos los CAs del proyecto; busca THENs incompatibles
3. **Scope overlap**: analiza si los Journeys de una feature incluyen funcionalidad que es el objetivo de otra
4. **Shared models inconsistentes**: inventaría todos los modelos mencionados y cruza sus definiciones/comportamientos
5. **Fuera de alcance contradictorio**: cruza las secciones "Fuera de Alcance" de cada feature con las HUs de las demás

---

## Paso 6: Clasificar cada conflicto detectado

Por cada conflicto:
- Asigna el ID: `[CF-001]`, `[CF-002]`, etc.
- Asigna la severidad según `kb-conflict-expert`: ALTA o MEDIA
- Describe qué features están involucradas
- Cita las secciones exactas en conflicto
- Sugiere una posible resolución (sin imponer — es una sugerencia)

Si no se detecta ningún conflicto → prepara un informe breve con estado `SIN_CONFLICTOS`, indica explícitamente que el número de conflictos ALTA y MEDIA es `0`, y conserva el inventario de comparaciones realizadas.

---

## Paso 7: Formato del informe

Usa `${CLAUDE_SKILL_DIR}/references/conflict_report_template.md` para estructurar el informe.

---

## Paso 8: Escribir el resultado

Determina el path de salida:
- Si se verificó un spec específico: mismo directorio del spec objetivo + `<nombre_base>_conflict_report.md`
  - Ejemplo: `features/auth/auth_spec.md` → `features/auth/auth_conflict_report.md`
- Si se verificaron todos los specs del directorio: raíz del directorio de features + `_conflict_report.md`
  - Ejemplo: `features/` → `features/_conflict_report.md`

Antes de escribir, verifica si el archivo ya existe:
- `!test -f "<path>"` — si existe, informa al usuario del path y pregunta: `[sobreescribir | cancelar]`. Continua solo si elige sobreescribir.

Escribe el informe en el archivo correspondiente.

---

## Paso 9: Informar al usuario

- Path del informe generado
- Resumen: estado general (SIN_CONFLICTOS o CONFLICTOS_DETECTADOS)
- Si hay conflictos: cuántos de severidad ALTA y cuántos MEDIA
- Siguiente paso:
  - Sin conflictos: "Los specs están listos. Continúa con `/wf-prepare-plan generate <feature_spec.md>`"
  - Con conflictos ALTA: "Resuelve los conflictos marcados como ALTA antes de continuar con `/wf-prepare-plan`. Edita los specs afectados y vuelve a ejecutar `/wf-spec-conflict` para verificar."
