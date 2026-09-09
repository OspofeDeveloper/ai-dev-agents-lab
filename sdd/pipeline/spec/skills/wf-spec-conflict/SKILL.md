---
name: wf-spec-conflict
description: "Detecta conflictos entre Specs SDD de un mismo proyecto: HUs duplicadas, CAs contradictorios, scope overlap, shared models inconsistentes."
when_to_use: "Activa en frases como 'verifica conflictos entre specs', 'hay conflictos entre features', 'comprueba si este spec choca con los existentes', 'detecta inconsistencias entre specs'."
argument-hint: "<feature_spec.md> --features-dir <path/features/>"
effort: high
allowed-tools: [Read, Bash]
context: fork
agent: sdd-spec-auditor
user-invocable: true
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
> "Necesito el spec de la feature y el directorio donde viven las demás, para poder compararlos."

---

## Paso 2: Localizar todos los specs

1. Verifica que el spec objetivo existe.
2. Busca todos los archivos `*_spec.md` dentro del directorio `--features-dir`, cubriendo ambos layouts de feature: `features/*/spec/*_spec.md` (subcarpetas) y `features/*/*_spec.md` (plano legacy).
3. Si no hay specs en el directorio → informa: "No se encontraron specs en `<features-dir>`. Comprueba la ruta, o genera antes los specs por feature."
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

> **Lo que escribes aquí lo lee una persona, y esa persona no invoca comandos.** La
> **Sugerencia de resolución** va en lenguaje natural y nombra **la acción**, no el workflow que
> la ejecuta: *"formalizar el cambio en el PRD antes de seguir"*, no *"lanzar `wf-prd-change`"*;
> *"pedir que se aclare el CA-004"*, no *"ejecutar `wf-spec-amend`"*. Los IDs y los veredictos
> (`CF-001`, `ALTA`, `SIN_CONFLICTOS`) **sí** se quedan: los parsean los gates.
>
> Medido (pasada 9 de CU-3.a): **2 de los 4** nombres de workflow que se colaron en artefactos
> salieron justo de este campo, con la guía de fase **cargada**. Por eso la norma está aquí y no
> solo allí: la guía es contexto de fase, y esto es tu instrucción de rol.

Si no se detecta ningún conflicto → prepara un informe breve con estado `SIN_CONFLICTOS`, indica explícitamente que el número de conflictos ALTA y MEDIA es `0`, y conserva el inventario de comparaciones realizadas.

---

## Paso 7: Formato del informe

Usa `${CLAUDE_SKILL_DIR}/references/conflict_report_template.md` para estructurar el informe.

---

## Paso 8: Escribir el resultado

Determina el path de salida:
- Si se verificó un spec específico: mismo directorio del spec objetivo + `<nombre_base>_conflict_report.md`
  - Ejemplo: `features/auth/spec/auth_spec.md` → `features/auth/spec/auth_conflict_report.md`
- Si se verificaron todos los specs del directorio: raíz del directorio de features + `_conflict_report.md`
  - Ejemplo: `features/` → `features/_conflict_report.md`

**Si ya existe, sobreescríbelo sin preguntar ([[D-064]]).** Un informe de conflicto es un artefacto
**derivado**: no guarda ninguna decisión humana dentro, y quien lanza el flujo lo regenera en
cada pasada. Un gate aquí no protegería nada — y, siendo `context: fork`, tampoco podrías
presentarlo. Lo que sí haces es **decir en tu informe que lo reemplazaste**.

Escribe el informe en el archivo correspondiente.

> **Con qué lo escribes, y por qué no con `Write` ([[D-051]]).** El agente que ejecuta esta
> skill tiene `Write` y `Edit` **prohibidos**: es el candado que impide que un auditor
> reescriba lo que audita. Tu informe **sí** lo escribes tú, con redirección por `Bash`
> (`cat > "<path>" <<'EOF' … EOF`). **No le pases la escritura al hilo principal:** el
> informe es tu output, y main no escribe artefactos ([[D-060]]; [[D-031]] es la mitad de leer).
>
> Y que quede claro el alcance del candado: con `Bash` disponible, técnicamente nada te
> impide tocar el spec auditado. **No lo haces por norma, no porque no puedas.** Auditas y
> reportas; corregir el spec es de `wf-spec-delta` o `wf-spec-amend`.

---

## Paso 9: Informar al usuario

- Path del informe generado
- Resumen: estado general (SIN_CONFLICTOS o CONFLICTOS_DETECTADOS)
- Si hay conflictos: cuántos de severidad ALTA y cuántos MEDIA
- Siguiente paso:
  - Sin conflictos: "Los specs están listos para pasar a planificación cuando quieras."
  - Con conflictos ALTA: "Resuelve los conflictos marcados como ALTA antes de planificar. Edita los specs afectados y pídeme una nueva revisión de conflictos para verificarlo."
