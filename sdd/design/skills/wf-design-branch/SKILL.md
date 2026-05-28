---
name: wf-design-branch
description: Workflow SDD para explorar variantes paralelas del sistema visual sin comprometerse. Permite crear ramas del DESIGN.md (DESIGN.<branch>.md), compararlas, mergearlas a main o descartarlas. Pensado para hipotesis de direccion visual o presentaciones A/B al cliente. Activa en frases como "explora una variante mas brand-forward del sistema", "crea una rama del DESIGN con dark mode prominente", "compara estas dos versiones del DESIGN.md", "haz un branch para probar otra familia".
argument-hint: "create <branch-name> | list | compare <branch-a> <branch-b> | merge <branch> --into <target> | discard <branch>"
effort: medium
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: design-architect
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
3. Delegar al agente con este prompt:
   ```text
   Modo: design-branch-compare
   Branch A: <path-a>
   Branch B: <path-b>
   Contenido A:
   ---
   <contenido_a>
   ---
   Contenido B:
   ---
   <contenido_b>
   ---

   INSTRUCCION: produce un comparativo estructurado (semantic diff, no diff literal):

   ## Diferencias en visual_personality
   - <campo>: A=<valor> vs B=<valor>

   ## Diferencias en colors
   - <token>: A=<valor> vs B=<valor> (en modo light/dark)

   ## Diferencias en typography
   - <rol>: A=<...> vs B=<...>

   ## Diferencias en components
   - <componente>: estados anadidos/quitados/cambiados

   ## Diferencias en motion / iconography / layout

   ## Diferencias en voice & microcopy

   ## Resumen
   - Cuantos tokens difieren
   - Severidad del diff (cosmetic / structural / breaking)
   - Recomendacion: merge directo, requiere triage, no fusionable

   No reescribas archivos. Solo compara.
   ```
4. Escribir output en `<dir_producto>/DESIGN_compare_<a>_vs_<b>_<fecha>.md`.
5. Informar al usuario del path y del resumen.

## Paso 5: Modo `merge`

Argumentos: `<branch>` y `--into <target>` (target normalmente `main`).

Pasos:
1. Resolver paths.
2. Ejecutar internamente `compare` primero, sin escribir output, solo en memoria.
3. Si el diff es `breaking` (cambia style_family, primary, tipografia, elimina componentes), pedir confirmacion explicita al usuario:
   > "Este merge introduce un cambio MAJOR (segun Regla 22). ¿Quieres continuar? Esto sobrescribira `<target>` y bumpeara la version. (y/n)"
4. Si el usuario confirma o el diff no es breaking:
   - Copiar el contenido del branch al target.
   - Eliminar del frontmatter del target los campos `branch`, `branched_from`, `branched_at` (esos campos son solo para branches).
   - Bumpear la version segun la naturaleza del cambio (MAJOR / MINOR / PATCH).
   - Anadir entry al `## Changelog` del target: `[<fecha>] [merge:<branch>] <resumen del diff>`.
5. Preguntar si descartar el branch tras merge:
   > "Merge completado en `<target>` (version <X.Y.Z>). ¿Quieres descartar el branch `<name>`? (y/n)"
6. Si el usuario dice si, ejecutar `discard` internamente.

## Paso 6: Modo `discard`

Argumentos: `<branch-name>`.

Pasos:
1. Verificar que `DESIGN.<branch-name>.md` existe.
2. Pedir confirmacion:
   > "Vas a descartar el branch `<name>` (`DESIGN.<name>.md`). Esto no es reversible. ¿Continuar? (y/n)"
3. Si confirma, eliminar el archivo.
4. Si existe un `<branch_name>_compare_*` cercano, ofrecer eliminarlo tambien.
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
