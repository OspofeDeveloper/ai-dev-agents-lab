---
name: wf-skill-create
description: "Orquestador SDD para crear una nueva skill (kb-* o wf-*) en el ecosistema. Parsea tipo, nombre, fase y opciones, verifica que no existe ya una skill equivalente, y delega la creacion al agente sdd-author."
when_to_use: "Activa con frases como 'crea una kb de X', 'necesito un nuevo workflow para Y', 'añade una knowledge base de', 'crea la skill wf-Z', 'quiero un workflow que haga'. No activa para crear agentes (usa wf-agent-create), ni para refactorizar skills existentes."
argument-hint: "<kb|wf> <nombre> --phase <prd|spec|design|plan|tasks|tech/<stack>|global> [--description <desc>] [--agent <nombre>] [--effort <low|medium|high>]"
effort: medium
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: sdd-author
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
| `kb` | `prd` | `sdd/prd/skills/kb-<nombre>/` |
| `kb` | `spec` | `sdd/spec/skills/kb-<nombre>/` |
| `kb` | `design` | `sdd/design/skills/kb-<nombre>/` |
| `kb` | `plan` | `sdd/plan/skills/kb-<nombre>/` |
| `kb` | `tasks` | `sdd/tasks/skills/kb-<nombre>/` |
| `kb` | `tech/<stack>` | `sdd/tech/<stack>/skills/kb-<nombre>/` |
| `kb` | `global` | `sdd/meta/skills/kb-<nombre>/` |
| `wf` | `prd` | `sdd/prd/skills/wf-<nombre>/` |
| `wf` | `spec` | `sdd/spec/skills/wf-<nombre>/` |
| `wf` | `design` | `sdd/design/skills/wf-<nombre>/` |
| `wf` | `plan` | `sdd/plan/skills/wf-<nombre>/` |
| `wf` | `tasks` | `sdd/tasks/skills/wf-<nombre>/` |
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

## Paso 6: Delegar al agente sdd-author

Construye el prompt para el agente con:

```text
Modo: create-<kb|wf>
Nombre canonico: <kb-nombre> o <wf-nombre>
Fase: <fase>
Directorio destino: <path calculado en paso 3>
Descripcion del dominio: <--description o "no proporcionada">
Agente destino (solo wf): <--agent o "ninguno">
Effort (solo wf): <--effort o "medium">
```

Invoca el agente `sdd-author` con ese prompt.

---

## Paso 7: Escribir la skill

Crea el directorio destino si no existe:
```bash
mkdir -p <directorio_destino>
```

Escribe el contenido generado por el agente en `<directorio_destino>/SKILL.md`.

---

## Paso 8: Actualizar el registry e informar al usuario

Regenera el skill registry con el generador determinista (no bloqueante: si python3 no está disponible o el script falla, avisa con `⚠ skill-registry.md no actualizado`):
```bash
python3 sdd/scripts/generate-skill-registry.py
```

Reporta:
- Path del archivo creado
- Frontmatter generado (nombre, description, tipo)
- Si es una `wf-*`: indica el rootmap entry que hay que añadir en el `CLAUDE.md` correspondiente:
  > "Añade esta entrada al rootmap de `sdd/<fase>/CLAUDE.md` (o de `sdd/CLAUDE.md` si es global):"
  > `| <intencion> | \`/<nombre>\` | \`<argument-hint>\` |`
- Si es una `kb-*`: indica que agentes deben actualizarse para cargarla
- Siguiente paso sugerido segun el tipo
