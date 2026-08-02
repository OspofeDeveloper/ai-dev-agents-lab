---
name: wf-bug
description: "Fast-lane de mantenimiento: triaje de un bug contra los specs de la feature, fix con trazabilidad (B-00X, CA-XXX) y registro en <feature>_bugs.md. Solo escala a wf-spec-delta si el comportamiento esperado cambia. Un bug es divergencia entre spec y código, no un cambio de spec."
when_to_use: "Activa en frases como 'hay un bug', 'esto no funciona como debería', 'arregla este fallo', 'la app crashea cuando', 'reporta este defecto'. No activa para cambiar el comportamiento esperado de una feature (usa wf-spec-delta), ni para implementar tasks pendientes (usa wf-task-run)."
argument-hint: "<descripcion.md|texto> [--feature <nombre>]"
effort: medium
allowed-tools: [Read, Write, Edit, Bash, Agent, Grep, Glob, AskUserQuestion]
user-invocable: true
---

# bug — Fast-lane de mantenimiento con triaje contra spec

Tu rol: triajear el bug contra el spec ANTES de tocar código. La pregunta central no es "¿cómo lo arreglo?" sino **"¿qué dice el spec que debería pasar?"**. Sin esa respuesta no hay fix, hay parche ciego.

> **Corre en el hilo principal (sin `context: fork`).** El Paso 3 presenta el triaje y **espera tu confirmación** antes de actuar: ese gate necesita `AskUserQuestion`, que un fork/subagente no puede usar (`[[D-016]]`, mismo principio que `[[D-015]]`). El trabajo pesado —el fix de código— se delega al agente owner vía la tool `Agent` (Paso 4), que aísla su contexto igual de bien.

---

## Paso 1: Parsear argumentos

- **Descripción del bug**: primer argumento — path a un `.md` (léelo) o texto inline.
- `--feature <nombre>`: opcional, acota la búsqueda del spec.

Sin descripción → informa:
> "Uso: `/wf-bug <descripcion.md|texto> [--feature <nombre>]`. Describe qué pasa, qué esperabas y cómo reproducirlo."

## Paso 2: Localizar la feature y su spec

1. Resuelve el directorio de specs (regla de layout: `artifacts.spec` de `.sdd/project-init.json` si está declarado; si no, busca `features/` o `*_features.md` desde el directorio actual).
2. Con `--feature` → su spec directamente: `features/<nombre>/spec/<nombre>_spec.md` (subcarpetas) o `features/<nombre>/<nombre>_spec.md` (plano legacy).
3. Sin `--feature` → usa `_features.md` (índice) y los síntomas del bug para identificar la feature candidata. Si hay ambigüedad entre varias, pregunta al usuario antes de continuar.
4. Si no hay specs en el proyecto → este flujo no aplica; informa que `wf-bug` exige una feature con spec y sugiere `/wf-spec-from-code` (si existe) o un fix manual fuera del pipeline.

## Paso 3: Localizar el CA violado (corazón del triaje)

Lee el spec completo. Contrasta el comportamiento reportado con los Criterios de Aceptación (`### CA-XXX`):

- **Hay un CA que define el comportamiento esperado y el código lo viola** → candidato a `CODE_BUG`. Anota el CA-XXX exacto.
- **Hay un CA, pero lo que el usuario espera es DISTINTO de lo que el CA dice** → `SPEC_CHANGE`. El "bug" es un cambio de comportamiento esperado.
- **Ningún CA cubre el comportamiento reportado** → `UNSPEC`. El spec tiene un hueco; arreglarlo en silencio agrandaría la divergencia documental.

Presenta el triaje al usuario con el CA citado textualmente y tu clasificación razonada. **Confirma con `AskUserQuestion`** (hilo principal, nunca texto libre) antes de actuar — el triaje decide si se toca código, spec o nada:

```
question: "Triaje del bug: <clasificación>. <CA-XXX citado>. ¿Procedo así?"
header: "Triaje"
opciones:
  - label: "Confirmar <CODE_BUG|SPEC_CHANGE|UNSPEC>"
    description: "Procede según el triaje: fix de código / escalar a wf-spec-delta / registrar hueco de spec"
  - label: "Reclasificar"
    description: "El triaje no es correcto; reconsidera contra el CA antes de actuar"
  - label: "Cancelar"
    description: "No toca código ni spec"
```

Solo pasa al Paso 4 con la confirmación. Con "Reclasificar" vuelve al triaje; con "Cancelar" cierra sin tocar nada.

## Paso 4: Actuar según triaje

### `CODE_BUG` — fix directo, el spec NO se toca

1. Determina el owner del fix con la misma regla de dominio de ejecución de `kb-tasks-expert`: agente del overlay de stack si hay `"stack"` en `.sdd/project-init.json`, o tú (orquestador) en modo agnóstico. Si existe el `_tasks.md` de la feature, la task cuyo `Componente` cubre el área del bug indica el owner natural.
2. Delega vía la tool `Agent` con **`run_in_background: false`** ([[D-043]]: los subagentes corren en background por defecto y el punto 3 verifica el fix y el punto 4 lo commitea — sin el flag verificarías sobre código a medio escribir), o implementa tú en modo agnóstico. En ambos casos, este contrato:
   ```
   Corrige el bug B-00X de la feature <nombre>.
   Comportamiento esperado (CA-XXX, literal del spec): <texto del CA>
   Comportamiento actual: <síntoma reportado + reproducción>
   INSTRUCCIONES: el CA es el contrato — el fix debe hacer que el comportamiento
   coincida con él, nada más. No refactorices alrededor. Si el fix exige cambiar
   el CA, detente y repórtalo: eso es SPEC_CHANGE, no CODE_BUG.
   Reporta evidencia: archivos tocados, causa raíz, y test/verificación que demuestra el fix.
   ```
3. **Verificación ejecutable**: igual que `wf-task-run` Paso 6 — comandos del `<stack>_project_state.md` o runner detectado; si no hay, regístralo explícitamente. Si la feature tiene tests del CA violado, deben pasar; valora añadir un test de regresión si no existe (recomiéndalo siempre, hazlo si el usuario acepta).
4. Registra y commitea (Pasos 5-6).

### `SPEC_CHANGE` — escala, no arregles

No toques código. Informa:
> "Esto no es un bug: el CA-XXX define ese comportamiento. Cambiarlo es un cambio de spec → `/wf-spec-delta analyze <spec.md> --new-reqs <descripción>`. Si además expande el producto (entidad nueva, flujo no comprometido), tocará pasar por `/wf-prd-change`."

Prepara el material: escribe la descripción del cambio en un `.md` listo para `--new-reqs` si el usuario quiere continuar. Registra la entrada B-00X con resolución `ESCALADO_SPEC_DELTA` (Paso 5) para que el reporte no se pierda.

### `UNSPEC` — decisión del usuario, nunca fix silencioso

Presenta el hueco: qué comportamiento no está cubierto por ningún CA. Opciones:
- **Formalizar primero** (recomendado): `/wf-spec-delta analyze` para añadir el CA que falta, luego re-entrar por `wf-bug` como `CODE_BUG` contra el CA nuevo.
- **Fix con gobernanza explícita**: si el usuario lo pide, ejecuta el fix como `CODE_BUG` pero la entrada B-00X lleva `CA: NINGUNO — comportamiento no especificado` y `Aviso de gobernanza: fix sin respaldo de spec, pendiente de formalizar`. Nunca lo registres como si hubiera CA.

## Paso 5: Registrar en `<feature>_bugs.md`

El registro vive junto al `_tasks.md` de la feature: `features/<nombre>/tasks/<nombre>_bugs.md` (subcarpetas) o `features/<nombre>/<nombre>_bugs.md` (plano legacy). Créalo si no existe con header `Spec origen` (ruta relativa al registro). Añade una entrada:

```markdown
## B-00X: <título corto>

- **Fecha:** <YYYY-MM-DD>
- **CA:** CA-XXX | NINGUNO — comportamiento no especificado
- **Triaje:** CODE_BUG | SPEC_CHANGE | UNSPEC
- **Síntoma:** <qué pasaba + reproducción>
- **Causa raíz:** <diagnóstico real, no el síntoma repetido>
- **Resolución:** FIX (commit <hash>) | ESCALADO_SPEC_DELTA | PENDIENTE
- **Aviso de gobernanza:** ninguno | <fix sin respaldo de spec...>
```

El ID `B-00X` es secuencial dentro del archivo. **No lo cuentes a mano** (una colisión corrompe el registro): obtén el siguiente con el script determinista
```bash
!python3 .sdd/scripts/sdd-next-id.py B <ruta_al_bugs.md>
```
(emite `B-001` si el archivo no existe o aún no tiene bugs). Si python3 o el script no están disponibles, cae a contar el máximo `B-NNN` del archivo + 1.

## Paso 6: Commit trazable

Solo para `CODE_BUG` con fix aplicado:

```bash
!git add <archivos del fix + bugs.md> && git commit -m "B-00X: <título> [CA-XXX]"
```

Un commit por bug, incluyendo el `_bugs.md`. Sin CA (`UNSPEC` con override) → `[CA:none]`.

> SSoT del criterio de empaquetado: `kb-delivery-discipline`. Mismo principio que el commit-por-task: el fix y su test de regresión van en la misma unidad de trabajo / PR (tests junto al código), nunca diferidos a un commit posterior.

## Paso 7: Informar

- Triaje final y CA implicado (citado).
- Para fix: causa raíz, archivos tocados, verificación ejecutable (o su ausencia explícita), commit.
- Para escalados: el comando exacto de `/wf-spec-delta` listo para lanzar.
- Path del registro `_bugs.md` actualizado.
