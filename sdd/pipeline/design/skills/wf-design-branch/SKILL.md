---
name: wf-design-branch
description: Permite explorar variantes paralelas del sistema visual sin comprometerse. Crea ramas del DESIGN.md (DESIGN.<branch>.md), las compara, las mergea a main o las descarta. Pensado para hipotesis de direccion visual o presentaciones A/B al cliente.
when_to_use: "Activa en frases como 'explora una variante mas brand-forward del sistema', 'crea una rama del DESIGN con dark mode prominente', 'compara estas dos versiones del DESIGN.md', 'haz un branch para probar otra familia'."
argument-hint: "create <branch-name> | list | compare <branch-a> <branch-b> | merge <branch> --into <target> [--allow-breaking-merge] | discard <branch> [--allow-discard-branch]"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
agent: design-system-architect
user-invocable: true
---

# design-branch — Exploraciones paralelas

Tu rol es permitir variantes vivas del sistema visual sin tocar `DESIGN.md` principal hasta que el usuario decida. No reescribe nada en main salvo en modo `merge`.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: `create | list | compare | merge | discard`.
- Argumentos especificos por modo (ver siguientes pasos).

Si el modo no es valido, informa:
> "Uso:"
> - "`/wf-design-branch create <branch-name>`"
> - "`/wf-design-branch list`"
> - "`/wf-design-branch compare <branch-a> <branch-b>`"
> - "`/wf-design-branch merge <branch> --into <target>`"
> - "`/wf-design-branch discard <branch>`"

## Paso 2: Modo `create`

Argumentos: `<branch-name>` obligatorio. Nombre alfanumerico con guiones, sin espacios.

Pasos:
1. Resolver `DESIGN.md` actual (busca en raiz del producto).
2. Verificar que no existe ya `DESIGN.<branch-name>.md`. Si existe, deten:
   > "Ya existe `DESIGN.<branch>.md`. Usa otro nombre o `discard` primero."
3. Copiar `DESIGN.md` a `DESIGN.<branch-name>.md`.
4. Anadir al frontmatter del branch:
   ```yaml
   branch: <branch-name>
   branched_from: main
   branched_at: <fecha ISO>
   ```
5. Anadir entry al `## Changelog` del branch: `[<fecha>] [branch:<name>] Branch creado desde main version X.Y.Z`.
6. Informar al usuario:
   > "Branch `<name>` creado en `DESIGN.<name>.md`. Itera ahi con `/wf-design-delta apply` o edicion manual. Para compararlo con main: `/wf-design-branch compare main <name>`."

## Paso 3: Modo `list`

Pasos:
1. Listar todos los archivos `DESIGN.*.md` en la raiz del producto (excluyendo `DESIGN.md`).
2. Para cada uno, leer frontmatter y mostrar:
   - nombre del branch
   - fecha de creacion
   - version del branch
   - branched_from
   - estado (`active` si tuvo cambios desde branched_at, `stale` si no)

Output ejemplo:
```
Branches activas:
- brand-forward     v0.2.0    creado 2026-05-10    activo
- mas-densidad      v0.1.5    creado 2026-05-15    stale
- explorar-editorial v0.3.0   creado 2026-05-20    activo

main: v0.4.0
```

## Paso 4: Modo `compare`

Argumentos: `<branch-a> <branch-b>`. Cualquiera puede ser `main` para referirse a `DESIGN.md`.

Pasos:
1. Resolver paths reales: `main` → `DESIGN.md`, otros → `DESIGN.<branch>.md`.
2. Leer ambos.
3. Compara **tú** ambos branches (eres el `agent:` de esta skill, [[D-070]]) siguiendo la instrucción de comparación estructurada de `${CLAUDE_SKILL_DIR}/references/compare_prompt_template.md`.
4. Escribir output en `<dir_producto>/DESIGN_compare_<a>_vs_<b>_<fecha>.md`.
5. Informar al usuario del path y del resumen.

## Paso 5: Modo `merge`

Argumentos: `<branch>` y `--into <target>` (target normalmente `main`).

Pasos:
1. Resolver paths.
2. Ejecutar internamente `compare` primero, sin escribir output, solo en memoria.
3. Si el diff es `breaking` (cambia style_family, primary, tipografia, elimina componentes) y **no** viene `--allow-breaking-merge`, **detente sin escribir nada** con veredicto operativo `STOP_MERGE_BREAKING`:
   > "El merge de `<branch>` en `<target>` es un cambio **MAJOR** (`kb-design-governance` Regla 3, criterios de MAJOR): cambia `<lo concreto: style_family / primary / tipografia / componentes eliminados>`. Sobrescribe `<target>` y bumpea su version mayor. No lo he tocado. La decision es de quien pueda confirmarla; si la toma, relanzame con `--allow-breaking-merge`."

   > **Por que aqui no preguntas ([[D-064]]).** Corres en `context: fork` y un subagente no puede
   > presentar una eleccion: la confirmacion cerrada que este paso dictaba **no era ejecutable**
   > ([[D-045]]). Paras y reportas; el gate lo presenta quien puede, y el override lo arma el usuario
   > eligiendo ([[D-026]]).
4. Si el diff no es breaking, o viene `--allow-breaking-merge`:
   - Copiar el contenido del branch al target.
   - Eliminar del frontmatter del target los campos `branch`, `branched_from`, `branched_at` (esos campos son solo para branches).
   - Bumpear la version segun la naturaleza del cambio (MAJOR / MINOR / PATCH).
   - Anadir entry al `## Changelog` del target: `[<fecha>] [merge:<branch>] <resumen del diff>`.
5. **El branch se queda.** Informa de que el merge termino (`<target>`, version `<X.Y.Z>`) y de que
   `DESIGN.<name>.md` sigue ahi. Descartarlo es una **accion propia y explicita** —el modo `discard`—,
   no una coletilla del merge: asi el usuario lo pide cuando quiera y con su gate, en vez de
   contestar a una pregunta que un fork no puede hacerle.

## Paso 6: Modo `discard`

Argumentos: `<branch-name> [--allow-discard-branch]`.

Pasos:
1. Verificar que `DESIGN.<branch-name>.md` existe.
2. Sin `--allow-discard-branch`, **detente sin borrar nada** con veredicto operativo `STOP_DISCARD_IRREVERSIBLE`:
   > "Descartar el branch `<name>` (`DESIGN.<name>.md`) **borra el fichero y no es reversible**: se pierde la exploracion visual que contiene, incluidas las decisiones que no esten en `DESIGN.md`. No lo he tocado. Si aun asi se quiere descartar, relanzame con `--allow-discard-branch`."
3. Con el flag, eliminar el archivo.
4. Si existe un `<branch_name>_compare_*` cercano, **no lo borres ni lo ofrezcas**: nombralo en el informe como fichero que quedo huerfano, y que lo decida quien pueda decidirlo.
5. Anadir entry al `## Changelog` de `DESIGN.md` principal: `[<fecha>] [branch-discarded:<name>] Branch descartado sin merge.`
6. Informar al usuario.

## Regla operativa

- Un branch nunca afecta a `DESIGN.md` principal hasta `merge`.
- Los branches pueden tener su propio `## Changelog` interno con cambios exploratorios.
- Si una feature usa un branch para prototipo (`wf-design-feature-prototype` con un branch), debe declararlo en el `_views.md`. No mezclar branches en producccion.
- Las exploraciones son baratas: descarta libremente.

## Anti-patrones

- Mantener mas de 5 branches simultaneos sin merge ni discard: pierde control.
- Mergear sin haber comparado antes (`compare` es gratis).
- Bumpear PATCH al mergear un branch breaking.
- Usar branches para evitar `wf-design-intake` cuando hay cambio de brief real: branches son visuales, no de brief.
