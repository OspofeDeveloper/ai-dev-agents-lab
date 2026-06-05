# Templates de scaffold para overlays de stack

Esqueletos de partida para `wf-stack-create`. Sustituir `<stack>` y los valores `[EN CORCHETES]`. El modelo de referencia completo es `tech/kmm/`.

---

## Template: `tech/<stack>/install.sh`

```bash
#!/bin/bash
# install.sh — Despliega el overlay <stack> al .claude del proyecto
# Ejecutar desde el directorio del proyecto destino, SIEMPRE después del
# install base de fases: bash /path/to/tech/<stack>/install.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$(pwd)/.claude"
shopt -s nullglob

# 1. Agentes (override por basename: sustituyen a los genéricos homónimos)
mkdir -p "$CLAUDE_DIR/agents"
for agent_file in "$SCRIPT_DIR/agents"/*.md; do
  cp "$agent_file" "$CLAUDE_DIR/agents/$(basename "$agent_file")"
  echo "  ✓ agents/$(basename "$agent_file")"
done

# 2. Skills de plan/tasks + workflows del stack (override por basename)
mkdir -p "$CLAUDE_DIR/skills"
install_skill() {
  local src_dir="${1%/}"; local name; name=$(basename "$src_dir")
  rm -rf "$CLAUDE_DIR/skills/$name"; mkdir -p "$CLAUDE_DIR/skills/$name"
  find "$src_dir" -type f ! -name ".DS_Store" | while read -r file; do
    rel="${file#"$src_dir/"}"; dest="$CLAUDE_DIR/skills/$name/$rel"
    mkdir -p "$(dirname "$dest")"; cp "$file" "$dest"
  done
  echo "  ✓ skills/$name/"
}
for subdir in plan tasks; do
  for skill_dir in "$SCRIPT_DIR/skills/$subdir"/*/; do install_skill "$skill_dir"; done
done
for skill_dir in "$SCRIPT_DIR/skills"/wf-*/; do install_skill "$skill_dir"; done

# 3. CLAUDE.md del overlay
cp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
echo "  ✓ CLAUDE.md"
echo "Done. Reinicia Claude Code para activar el overlay <stack>."
```

---

## Template: `tech/<stack>/skills/wf-<stack>-init/SKILL.md` (estructura)

```yaml
---
name: wf-<stack>-init
description: "Init especialista del stack <stack>. Produce <stack>_project_state.md con el estado tecnico del proyecto: [targets/runtime], [arquitectura], [dependencias clave], comandos de build y test. Soporta modo detect (auto-exploracion de proyectos existentes) y configure (preguntas con opciones para proyectos nuevos). Si ya existe <stack>_project_state.md muestra el estado y pregunta si rehacerlo. Registra el run en stack_workflows_run dentro de .sdd/project-init.json."
when_to_use: "Activa con frases como 'init de <stack>', 'inicializa el stack <stack>', 'detecta el estado <stack> del proyecto'. No activa para el init generico (usa wf-project-init, que despacha a este)."
argument-hint: "[--mode detect|configure] [--force] [--output <path>]"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
user-invocable: true
---
```

Pasos mínimos del cuerpo (modelo: `tech/kmm/skills/wf-kmm-init/SKILL.md`):
1. Parsear argumentos (`--mode`, `--force`, `--output`)
2. Si existe `<stack>_project_state.md` sin `--force` → resumen + AskUserQuestion (mantener / rehacer / actualizar campos)
3. Inferir modo: indicios de proyecto existente → `detect`; proyecto vacío → `configure`
4. `detect`: explorar [archivos canónicos del stack] y derivar el estado real. `configure`: AskUserQuestion con opciones cerradas por cada dimensión del brief
5. Escribir `<stack>_project_state.md` (secciones mínimas: Targets/Runtime, Arquitectura, Dependencias clave, Comandos build/test, Fecha del init)
6. Registrar en `.sdd/project-init.json` → `stack_workflows_run += ["wf-<stack>-init@<timestamp>"]`
7. Informe final con siguiente paso

---

## Template: `tech/<stack>/CLAUDE.md` (estructura)

```markdown
# <Stack> Overlay — Instrucciones para el Orquestador

Paquete de especialización <stack> para las fases plan/tasks del pipeline SDD.

## Rootmap de workflow skills
| Intención del usuario | Skill | Argumentos |
|---|---|---|
| Inicializar o calibrar el estado técnico <stack> | `/wf-<stack>-init` | `[--mode detect|configure] [--force]` |

## Agentes disponibles
[Tabla solo si --with-agents o agentes de implementación propios]

## Principio de precondiciones
Todos los agentes y workflows del stack leen `<stack>_project_state.md` antes de operar.
Si no existe, ejecutar `/wf-<stack>-init` primero.
```

---

## Template: variantes de agentes (solo `--with-agents`)

Partir de la pieza **genérica** correspondiente (`sdd/plan/agents/plan-architect.md`, `sdd/plan/agents/plan-auditor.md`, `sdd/tasks/agents/task-generator.md`) y especializarla, NUNCA al revés:

- Mismo `name` (el override es por basename).
- `skills`: las genéricas de la pieza + las KBs del stack que existan.
- Identidad: "especializado en <stack>" con las reglas arquitectónicas del brief.
- Conservar intacto el contrato externo: taxonomía de gaps, estados `BORRADOR`/`VALIDADO`, formato del artefacto, regla canónica de Design.
- En `task-generator`: owners = agentes del stack (o `orquestador` si el overlay no aporta implementadores).
- `color: red` (tech target, según kb-sdd-creation-guide).
