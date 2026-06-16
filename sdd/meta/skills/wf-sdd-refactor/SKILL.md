---
name: wf-sdd-refactor
description: "Orquestador SDD para refactorizar una skill (kb-* o wf-*) o agente existente del ecosistema. Parsea el path del artefacto y el motivo del cambio, lee el estado actual, y delega el diagnostico y la refactorizacion al agente sdd-author."
when_to_use: "Activa con frases como 'refactoriza esta skill', 'esta kb es demasiado ancha', 'separa esta skill en dos', 'esta wf mezcla responsabilidades', 'extrae una SSoT de', 'actualiza el frontmatter de', 'corrige la estructura de este agente'. No activa para crear piezas nuevas (usa wf-skill-create, wf-agent-create) ni para auditar el ecosistema en general (usa wf-sdd-audit)."
argument-hint: "<path-skill-o-agente> [--reason <motivo>]"
effort: medium
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: sdd-author
user-invocable: true
---

# wf-sdd-refactor — Orquestador de Refactorizacion de Skills y Agentes

Tu rol es de **orquestador puro**: lees el artefacto existente, recopilas el contexto necesario y delegas el diagnostico y la refactorizacion al agente `sdd-author`. No ejecutas la refactorizacion directamente.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path**: ruta al `SKILL.md` o al archivo `.md` del agente
- **`--reason`**: descripcion libre del motivo del cambio (opcional pero recomendado)

Si `$ARGUMENTS` esta vacio o no hay path, informa:
> "Uso: `/wf-sdd-refactor <path-skill-o-agente> [--reason <motivo>]`"
>
> Ejemplos:
> - `/wf-sdd-refactor sdd/pipeline/design/skills/kb-design-expert/SKILL.md --reason "mezcla reglas de trazabilidad y de tokens"`
> - `/wf-sdd-refactor sdd/pipeline/spec/agents/sdd-spec-writer.md --reason "cubre escritura y auditoria a la vez"`

---

## Paso 2: Verificar que el artefacto existe

```bash
ls <path>
```

Si no existe:
> "❌ No se encontro el archivo `<path>`. Verifica el path e inténtalo de nuevo."

---

## Paso 3: Leer el artefacto y su contexto

1. Lee el artefacto completo.
2. Determina el tipo: `kb-*`, `wf-*` o agente.
3. Busca piezas relacionadas que puedan verse afectadas por la refactorizacion:

**Si es una `kb-*`:**
```bash
# Agentes que la cargan
grep -rl "<nombre-kb>" sdd/ --include="*.md" 2>/dev/null
```

**Si es una `wf-*`:**
```bash
# CLAUDE.md que la referencian en el rootmap
grep -rl "<nombre-wf>" sdd/ --include="CLAUDE.md" 2>/dev/null
# Agente al que delega si tiene agent:
```

**Si es un agente:**
```bash
# Workflows que delegan a este agente
grep -rl "agent: <nombre>" sdd/ --include="SKILL.md" 2>/dev/null
```

Lee el contenido de las piezas relacionadas encontradas.

---

## Paso 4: Delegar al agente sdd-author

Construye el prompt para el agente con:

```text
Modo: refactor
Path del artefacto: <path>
Tipo: <kb|wf|agente>
Motivo del cambio: <--reason o "no especificado — diagnosticar">
Contenido actual del artefacto:
---
<contenido completo>
---
Piezas relacionadas que pueden verse afectadas:
[Para cada pieza relacionada encontrada]
Path: <path>
---
<contenido>
---
INSTRUCCION: Diagnostica el problema, propone el cambio (extension, particion o correccion de frontmatter/estructura) y aplica solo lo que sea seguro sin eliminar reglas que sean SSoT de otras piezas. Si la refactorizacion implica crear nuevas piezas, descríbelas pero no las crees: informa al usuario para que use wf-skill-create o wf-agent-create.
```

Invoca el agente `sdd-author` con ese prompt.

---

## Paso 5: Aplicar los cambios

Escribe el contenido refactorizado en el path original del artefacto.

Si el agente indica que la refactorizacion requiere crear nuevas piezas (extraccion de SSoT, particion), no las crees: informa al usuario:
> "⚠ La refactorizacion completa requiere crear las siguientes piezas nuevas. Usa los workflows indicados para cada una:"
> [lista de piezas con comando sugerido]

---

## Paso 6: Regenerar el registry

Si la refactorizacion cambio el `name:`, la `description:` o la ubicacion del artefacto, regenera el skill registry (no bloqueante; si falla, avisa con `⚠`):
```bash
python3 sdd/scripts/generate-skill-registry.py
```

---

## Paso 7: Gate estructural obligatorio (cierre)

Este paso es **determinista y obligatorio**, y corre **siempre** (una refactorización puede romper citas de regla, renombrar piezas o invalidar rutas de references aunque no cambie el `name:`). La SSoT de qué se valida es el script `sdd/scripts/sdd-structural-lint.py` (no se re-describen los checks aquí; el script es la autoridad).

Ejecuta el linter sobre el árbol fuente:
```bash
python3 sdd/scripts/sdd-structural-lint.py --check
```

Interpreta el exit code:

- **Exit 2 (hay BLOCKING)**: NO declares la refactorización cerrada con éxito. El baseline del repo es `blocking=0`, así que cualquier blocking nuevo es atribuible a la pieza recién refactorizada (o a piezas que la referencian y quedaron con cita rota). Ejecuta `python3 sdd/scripts/sdd-structural-lint.py --severity blocking` para ver el detalle, reporta los findings al usuario y exige corregirlos antes de cerrar.
  - Si — y solo si — algún blocking es sobre **piezas ajenas preexistentes** no tocadas por esta refactorización, dílo explícitamente, sepáralo de lo atribuible al cambio, y deja que el usuario decida.
- **Exit 1 (solo WARNING)**: NO bloquea el cierre. Reporta un resumen de **una línea** con el conteo por tipo.
- **Exit 0 (limpio)**: cierra sin observaciones de lint.

Si python3 o el script no están disponibles, avisa con `⚠ gate estructural no ejecutado` y no bloquees por ello.

---

## Paso 8: Informar al usuario

Reporta:
- Que cambio se aplico y por que
- Si hay piezas relacionadas que deben actualizarse manualmente (agentes que cargan la KB, CLAUDE.md con rootmap entries, etc.)
- Si quedan pasos pendientes (crear nuevas piezas, eliminar duplicados)
- Siguiente paso sugerido
