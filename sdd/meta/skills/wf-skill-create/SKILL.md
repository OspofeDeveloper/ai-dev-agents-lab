---
name: wf-skill-create
description: "Orquestador SDD para crear una nueva skill (kb-* o wf-*) en el ecosistema. Parsea tipo, nombre, fase y opciones, verifica que no existe ya una skill equivalente, y delega la creacion al agente sdd-author."
when_to_use: "Activa con frases como 'crea una kb de X', 'necesito un nuevo workflow para Y', 'añade una knowledge base de', 'crea la skill wf-Z', 'quiero un workflow que haga'. No activa para crear agentes (usa wf-agent-create), ni para refactorizar skills existentes."
argument-hint: "<kb|wf> <nombre> --phase <prd|spec|design|plan|tasks|tech/<stack>|global> [--description <desc>] [--agent <nombre>] [--effort <low|medium|high>]"
effort: medium
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: sdd-author
user-invocable: true
---

# wf-skill-create — Orquestador de Creacion de Skills

Tu rol es de **orquestador puro**: parseas los argumentos, verificas precondiciones, buscas duplicados y delegas la creacion al agente `sdd-author`. No generas el contenido de la skill directamente.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Tipo**: primera palabra (`kb` o `wf`)
- **Nombre**: segunda palabra (sin prefijo `kb-` o `wf-`, el agente lo añade)
- **`--phase`**: fase destino o `global`
- **`--description`**: descripcion libre del dominio (opcional pero recomendado)
- **`--agent`**: agente al que delega la wf (solo para tipo `wf`, opcional)
- **`--effort`**: `low`, `medium` o `high` (solo para tipo `wf`, por defecto `medium`)

Si `$ARGUMENTS` esta vacio o el tipo no es `kb` ni `wf`, informa:
> "Uso: `/wf-skill-create <kb|wf> <nombre> --phase <fase> [--description <desc>] [--agent <agente>] [--effort <low|medium|high>]`"

Si falta `--phase`, informa:
> "❌ Falta `--phase`. Indica la fase destino: `prd`, `spec`, `design`, `plan`, `tasks`, `tech/<stack>` o `global`."

---

## Paso 2: Validar nombre y convencion

1. Verifica que el nombre no incluye ya el prefijo (`kb-` o `wf-`): si lo incluye, extrae solo la parte del nombre.
2. Construye el nombre canonico: `kb-<nombre>` o `wf-<nombre>`.
3. Valida que el nombre sigue el patron de la fase: `<fase>-<dominio>` para skills de fase, `sdd-<dominio>` o nombre directo para skills globales.
4. Si el nombre parece generico (menos de dos palabras separadas por `-`), advierte:
> "⚠ El nombre `<nombre>` puede ser demasiado generico. Considera un nombre mas descriptivo como `<sugerencia>`."

---

## Paso 3: Determinar el directorio destino

Segun el tipo y la fase:

| Tipo | Fase | Directorio |
|---|---|---|
| `kb` | `prd` | `sdd/pipeline/prd/skills/kb-<nombre>/` |
| `kb` | `spec` | `sdd/pipeline/spec/skills/kb-<nombre>/` |
| `kb` | `design` | `sdd/pipeline/design/skills/kb-<nombre>/` |
| `kb` | `plan` | `sdd/pipeline/plan/skills/kb-<nombre>/` |
| `kb` | `tasks` | `sdd/pipeline/tasks/skills/kb-<nombre>/` |
| `kb` | `tech/<stack>` | `sdd/tech/<stack>/skills/kb-<nombre>/` |
| `kb` | `global` | `sdd/meta/skills/kb-<nombre>/` |
| `wf` | `prd` | `sdd/pipeline/prd/skills/wf-<nombre>/` |
| `wf` | `spec` | `sdd/pipeline/spec/skills/wf-<nombre>/` |
| `wf` | `design` | `sdd/pipeline/design/skills/wf-<nombre>/` |
| `wf` | `plan` | `sdd/pipeline/plan/skills/wf-<nombre>/` |
| `wf` | `tasks` | `sdd/pipeline/tasks/skills/wf-<nombre>/` |
| `wf` | `tech/<stack>` | `sdd/tech/<stack>/skills/wf-<nombre>/` |
| `wf` | `global` | `sdd/meta/skills/wf-<nombre>/` |

---

## Paso 4: Verificar que no existe una skill equivalente

```bash
find sdd/ -name "SKILL.md" | xargs grep -l "<nombre>" 2>/dev/null
```

Si se encuentran resultados, lee los `SKILL.md` encontrados y evalua si cubren el mismo dominio:

- Si existe una skill con el mismo dominio: detener y reportar al usuario:
  > "⚠ Ya existe `<path>` que cubre un dominio similar. Revisa si puedes extender esa skill en vez de crear una nueva. Si el dominio es claramente distinto, indica `--force` para continuar."
- Si existe `--force` en los argumentos o el usuario confirma: continuar.
- Si no hay solapamiento: continuar.

---

## Paso 5: Verificar el agente destino (solo para `wf` con `--agent`)

Si se especifico `--agent`:

1. Busca el archivo del agente:
   ```bash
   find sdd/ -name "<agente>.md" -path "*/agents/*"
   ```
2. Si no existe: advertir pero no bloquear:
   > "⚠ El agente `<agente>` no existe todavia. La skill se creara con `agent: <agente>` en el frontmatter, pero deberas crear el agente antes de invocar el workflow."

---

## Paso 6: Generar el esqueleto canonico (scaffold determinista)

El frontmatter y la ubicacion NO se redactan por prosa: los produce el script
`sdd/scripts/sdd-scaffold.py`, que escribe el `SKILL.md` con el frontmatter
canonico por construccion (segun `kb-sdd-creation-guide`) y un cuerpo-esqueleto
con `TODO`. Asi la pieza pasa el gate del Paso 9 sin retoques de frontmatter.

```bash
# kb
python3 sdd/scripts/sdd-scaffold.py kb <nombre> --phase <fase> \
  [--description "<desc>"] [--effort <low|medium|high>]
# wf
python3 sdd/scripts/sdd-scaffold.py wf <nombre> --phase <fase> \
  [--description "<desc>"] [--agent <agente>] [--effort <low|medium|high>]
```

El script resuelve el directorio destino (Paso 3) y el nombre canonico; rechaza
con exit 2 si el destino ya existe (consistente con el chequeo de duplicados del
Paso 4). Si python3 o el script no estan disponibles, cae al modo manual: crea
el directorio y escribe el frontmatter siguiendo `kb-sdd-creation-guide`.

---

## Paso 7: Delegar a sdd-author el relleno del cuerpo

Construye el prompt para el agente con:

```text
Modo: fill-body-<kb|wf>
Archivo scaffoldeado: <path del SKILL.md creado en Paso 6>
Nombre canonico: <kb-nombre> o <wf-nombre>
Fase: <fase>
Descripcion del dominio: <--description o "no proporcionada">
Agente destino (solo wf): <--agent o "ninguno">
```

Invoca el agente `sdd-author`. Su trabajo es **editar** el archivo ya
scaffoldeado: reemplazar el cuerpo-esqueleto `TODO` por el contenido real y
afinar la `description` del frontmatter si procede. NO debe alterar los campos
estructurales del frontmatter (`name`, `user-invocable`, `effort`,
`allowed-tools`, `context`, `agent`) salvo necesidad justificada — los puso el
scaffold y el gate del Paso 9 los verifica.

---

## Paso 8: Regenerar el registry

Regenera el skill registry con el generador determinista (no bloqueante: si python3 no está disponible o el script falla, avisa con `⚠ skill-registry.md no actualizado`):
```bash
python3 sdd/scripts/generate-skill-registry.py
```

---

## Paso 9: Gate estructural obligatorio (cierre)

Este paso es **determinista y obligatorio**: ninguna skill se da por creada con defectos estructurales mecanizables. La SSoT de qué se valida es el script `sdd/scripts/sdd-structural-lint.py` (no se re-describen los checks aquí; el script es la autoridad).

Ejecuta el linter sobre el árbol fuente:
```bash
python3 sdd/scripts/sdd-structural-lint.py --check
```

Interpreta el exit code:

- **Exit 2 (hay BLOCKING)**: NO declares la creación con éxito. El baseline del repo es `blocking=0`, así que cualquier blocking nuevo es atribuible a la pieza recién creada. Ejecuta `python3 sdd/scripts/sdd-structural-lint.py --severity blocking` para ver el detalle, reporta los findings al usuario y exige corregirlos antes de cerrar.
  - Si — y solo si — algún blocking es sobre **piezas ajenas preexistentes** (no la recién creada), dílo explícitamente, sepáralo de lo atribuible a esta skill, y deja que el usuario decida si lo aborda ahora o aparte.
- **Exit 1 (solo WARNING)**: NO bloquea el cierre. Reporta un resumen de **una línea** con el conteo por tipo (p. ej. `Hygiene: 78 DESCRIPTION-TOO-LONG, 53 USER-INVOCABLE-MISSING, 7 SKILL-REF-MISSING — no bloqueante`).
- **Exit 0 (limpio)**: cierra sin observaciones de lint.

Si python3 o el script no están disponibles, avisa con `⚠ gate estructural no ejecutado` y no bloquees por ello.

---

## Paso 10: Informar al usuario

Reporta:
- Path del archivo creado
- Frontmatter generado (nombre, description, tipo)
- Si es una `wf-*`: indica el rootmap entry que hay que añadir en el `CLAUDE.md` correspondiente:
  > "Añade esta entrada al rootmap de `sdd/<fase>/CLAUDE.md` (o de `sdd/CLAUDE.md` si es global):"
  > `| <intencion> | \`/<nombre>\` | \`<argument-hint>\` |`
- Si es una `kb-*`: indica que agentes deben actualizarse para cargarla
- Siguiente paso sugerido segun el tipo
