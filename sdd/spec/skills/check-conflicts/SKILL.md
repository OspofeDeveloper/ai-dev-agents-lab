---
name: check-conflicts
description: Orquestador SDD para detectar conflictos entre Specs SDD de un mismo proyecto. Compara un spec contra todos los specs existentes en el directorio features/ y produce un informe de conflictos (HUs duplicadas, CAs contradictorios, scope overlap, shared models inconsistentes). Activa en frases como "verifica conflictos entre specs", "hay conflictos entre features", "comprueba si este spec choca con los existentes", "detecta inconsistencias entre specs".
argument-hint: "<feature_spec.md> --features-dir <path/features/>"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
disable-model-invocation: true
context: fork
agent: sdd-analyst
---

# check-conflicts — Orquestador de Detección de Conflictos SDD

Tu rol es de **orquestador puro**: localizas todos los specs relevantes, delegas la comparación al agente `sdd-analyst` en modo `conflict`, y escribes el informe resultante.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del spec objetivo**: el primer argumento (el spec a verificar contra los existentes). Puede ser un `_spec.md` específico o `.` para verificar todos los specs de un directorio.
- **Directorio de features**: el argumento después de `--features-dir`

Si no hay `--features-dir`, intenta inferir el directorio de features como `features/` relativo al directorio del spec objetivo.

Si no hay argumento, informa al usuario:
> "Uso: `/check-conflicts <feature_spec.md> --features-dir <path/features/>`"
> "Ejemplo: `/check-conflicts features/auth/auth_spec.md --features-dir features/`"

---

## Paso 2: Localizar todos los specs

1. Verifica que el spec objetivo existe.
2. Busca todos los archivos `*_spec.md` dentro del directorio `--features-dir` (recursivo, un nivel de profundidad: `features/*/<nombre>_spec.md`).
3. Si no hay specs en el directorio → informa: "No se encontraron specs en `<features-dir>`. Asegúrate de haber ejecutado `/decompose-spec` o de que la ruta es correcta."
4. Si solo hay 1 spec en total (contando el objetivo) → informa: "Solo hay 1 spec. Se necesitan al menos 2 specs para verificar conflictos."

---

## Paso 3: Leer todos los specs

Lee el contenido completo de:
- El spec objetivo
- Todos los specs encontrados en el directorio de features (excluyendo el spec objetivo si ya está incluido)

---

## Paso 4: Delegar al agente sdd-analyst

Invoca el agente `sdd-analyst` pasándole como prompt:

```
Modo: conflict
Spec objetivo: <path_completo>
Features a comparar: <N> specs

Contenido del Spec objetivo ([nombre]):
---
<contenido>
---

Contenido de [feature-1] ([path]):
---
<contenido>
---

Contenido de [feature-2] ([path]):
---
<contenido>
---

[... repetir por cada spec ...]
```

Espera a que el agente complete su ejecución y recibe su output estructurado.

---

## Paso 5: Escribir el resultado

Determina el path de salida:
- Si se verificó un spec específico: mismo directorio del spec objetivo + `<nombre_base>_conflict_report.md`
  - Ejemplo: `features/auth/auth_spec.md` → `features/auth/auth_conflict_report.md`
- Si se verificaron todos los specs del directorio: raíz del directorio de features + `_conflict_report.md`
  - Ejemplo: `features/` → `features/_conflict_report.md`

Escribe el informe del agente en el archivo correspondiente.

---

## Paso 6: Informar al usuario

- Path del informe generado
- Resumen: estado general (SIN_CONFLICTOS o CONFLICTOS_DETECTADOS)
- Si hay conflictos: cuántos de severidad ALTA (bloquean `/prepare-plan` en las features afectadas) y cuántos MEDIA
- Siguiente paso:
  - Sin conflictos: "Los specs están listos. Continúa con `/prepare-plan generate <feature_spec.md>`"
  - Con conflictos ALTA: "Resuelve los conflictos marcados como ALTA antes de continuar con `/prepare-plan`. Edita los specs afectados y vuelve a ejecutar `/check-conflicts` para verificar."
