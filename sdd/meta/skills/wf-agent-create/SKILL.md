---
name: wf-agent-create
description: "Orquestador SDD para crear un nuevo agente dentro del ecosistema. Parsea nombre, fase y skills, verifica que no existe ya un agente con responsabilidad equivalente, comprueba que las KBs existen y delega la creacion al agente sdd-author."
when_to_use: "Activa con frases como 'crea un agente para X', 'necesito un agente que haga Y', 'añade un agente Z a la fase', 'quiero un agente especializado en'. No activa para crear skills (usa wf-skill-create), ni para generar skills o agentes del pipeline SDD (usa las wf-* de fase correspondiente)."
argument-hint: "<nombre> --phase <prd|spec|design|plan|tasks|tech/<stack>|global> --skills <kb1,kb2,...> [--description <desc>] [--model <modelo>] [--effort high] [--read-only]"
effort: medium
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: sdd-author
user-invocable: true
---

# wf-agent-create — Orquestador de Creacion de Agentes

Tu rol es de **orquestador puro**: parseas los argumentos, verificas precondiciones, buscas duplicados, validas las KBs y delegas la creacion al agente `sdd-author`. No generas el contenido del agente directamente.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Nombre**: primera palabra del agente (sin extension `.md`)
- **`--phase`**: fase destino o `global`
- **`--skills`**: lista de KBs separadas por comas (opcional pero recomendado)
- **`--description`**: descripcion libre del dominio cognitivo (opcional pero recomendado)
- **`--model`**: modelo a usar (por defecto derivado del rol — ver criterio en `kb-sdd-creation-guide`)
- **`--effort high`**: override explicito para forzar `effort: high` (normalmente se deriva del rol)
- **`--read-only`**: override explicito para añadir `disallowedTools: Write, Edit` (normalmente se deriva del rol)

Si `$ARGUMENTS` esta vacio o falta el nombre, informa:
> "Uso: `/wf-agent-create <nombre> --phase <fase> --skills <kb1,kb2,...> [--description <desc>] [--model <modelo>] [--effort high] [--read-only]`"

Si falta `--phase`, informa:
> "❌ Falta `--phase`. Indica la fase destino: `prd`, `spec`, `design`, `plan`, `tasks`, `tech/<stack>` o `global`."

---

## Paso 2: Validar nombre y convencion

1. Verifica que el nombre sigue el patron segun la fase:
   - Fase unica: `<fase>-<rol>` (ejemplo: `design-architect`, `spec-writer`)
   - Stack: `<stack>-<rol>` (ejemplo: `kmm-planner`)
   - Global/meta: `sdd-<rol>` (ejemplo: `sdd-author`)
2. Si el nombre no sigue el patron, sugiere la correccion:
   > "⚠ El nombre propuesto `<nombre>` no sigue el patron `<fase>-<rol>`. Considera `<sugerencia>`."
   > Continua de todas formas salvo que el usuario indique lo contrario.

---

## Paso 3: Determinar el directorio destino

Segun la fase:

| Fase | Directorio |
|---|---|
| `prd` | `sdd/prd/agents/` |
| `spec` | `sdd/spec/agents/` |
| `design` | `sdd/design/agents/` |
| `plan` | `sdd/plan/agents/` |
| `tasks` | `sdd/tasks/agents/` |
| `tech/<stack>` | `sdd/tech/<stack>/agents/` |
| `global` | `sdd/meta/agents/` |

---

## Paso 4: Verificar que no existe un agente equivalente

```bash
find sdd/ -name "*.md" -path "*/agents/*" 2>/dev/null
```

Lee cada agente encontrado en la misma fase y evalua si su descripcion cubre el mismo dominio cognitivo:

- Si existe un agente con dominio solapado: detener y reportar:
  > "⚠ Ya existe `<path>` que cubre un dominio similar (`<descripcion_breve>`). Revisa si puedes extender ese agente añadiendo un nuevo modo. Si el dominio es claramente distinto, indica `--force` para continuar."
- Si existe `--force` o el usuario confirma: continuar.
- Si no hay solapamiento: continuar.

---

## Paso 5: Verificar que las KBs existen

Para cada KB en `--skills`:

```bash
find sdd/ -name "SKILL.md" -path "*/<kb-nombre>/*" 2>/dev/null
```

Si alguna KB no existe: advertir pero no bloquear:
> "⚠ La KB `<kb-nombre>` no existe todavia. El agente se creara con esa KB en su `skills: [...]`, pero deberas crear la KB antes de que el agente pueda usarla correctamente."

Reporta la lista completa de KBs verificadas y las que faltan.

---

## Paso 6: Delegar al agente sdd-author

Construye el prompt para el agente con:

```text
Modo: create-agent
Nombre: <nombre>
Fase: <fase>
Directorio destino: <path calculado en paso 3>
Skills a cargar: <lista de KBs o "ninguna especificada">
Descripcion del dominio cognitivo: <--description o "no proporcionada">
Modelo: <--model, o derivar de criterio kb-sdd-creation-guide según rol>
Override effort: <"high" si --effort high presente, o "derivar de criterio kb-sdd-creation-guide">
Override read-only: <"sí" si --read-only presente, o "derivar de criterio kb-sdd-creation-guide">
```

Aplica los criterios de `kb-sdd-creation-guide` para los campos de frontmatter derivables:
- `model`: opus para escritores/implementadores, sonnet para auditores/exploradores/planificadores
- `effort: high` si el agente genera artefactos complejos; omitir si audita, explora o planifica approach
- `disallowedTools: Write, Edit` si el system prompt declara que no modifica archivos y no produce artefactos diagnósticos intermedios
- `color`: según tabla de fase en `kb-sdd-creation-guide` (purple/blue/green/pink/orange/cyan/red)

Invoca el agente `sdd-author` con ese prompt.

---

## Paso 7: Escribir el agente

Crea el directorio destino si no existe:
```bash
mkdir -p <directorio_destino>
```

Escribe el contenido generado por el agente en `<directorio_destino>/<nombre>.md`.

---

## Paso 8: Gate estructural obligatorio (cierre)

Este paso es **determinista y obligatorio**: ningún agente se da por creado con defectos estructurales mecanizables. La SSoT de qué se valida es el script `sdd/scripts/sdd-structural-lint.py` (no se re-describen los checks aquí; el script es la autoridad). Un agente recién creado puede introducir, p. ej., un `NAME-MISMATCH` (el `name:` del frontmatter no coincide con el basename del archivo).

> Nota: este workflow **no** regenera `skill-registry.md` — el registry solo indexa skills, no agentes. Solo corre el gate estructural.

Ejecuta el linter sobre el árbol fuente:
```bash
python3 sdd/scripts/sdd-structural-lint.py --check
```

Interpreta el exit code:

- **Exit 2 (hay BLOCKING)**: NO declares la creación con éxito. El baseline del repo es `blocking=0`, así que cualquier blocking nuevo es atribuible al agente recién creado. Ejecuta `python3 sdd/scripts/sdd-structural-lint.py --severity blocking` para ver el detalle, reporta los findings al usuario y exige corregirlos antes de cerrar.
  - Si — y solo si — algún blocking es sobre **piezas ajenas preexistentes** (no el recién creado), dílo explícitamente, sepáralo de lo atribuible a este agente, y deja que el usuario decida.
- **Exit 1 (solo WARNING)**: NO bloquea el cierre. Reporta un resumen de **una línea** con el conteo por tipo.
- **Exit 0 (limpio)**: cierra sin observaciones de lint.

Si python3 o el script no están disponibles, avisa con `⚠ gate estructural no ejecutado` y no bloquees por ello.

---

## Paso 9: Informar al usuario

Reporta:
- Path del archivo creado
- Frontmatter generado (nombre, skills cargadas, modelo, effort si aplica, disallowedTools si aplica, color asignado)
- Lista de KBs verificadas y las que aun no existen
- La entrada que hay que añadir en la seccion `## Agentes disponibles` del `CLAUDE.md` correspondiente:
  > "Añade esta entrada a `sdd/<fase>/CLAUDE.md` (o al orquestador global si es `global`):"
  > `| \`<nombre>\` | <descripcion_breve> |`
- Si el agente es el target de una `wf-*` existente: verificar que `agent: <nombre>` en esa workflow apunta al nombre correcto
- Siguiente paso sugerido: crear KBs faltantes, crear `wf-*` que invoque este agente, o actualizar el `CLAUDE.md`
