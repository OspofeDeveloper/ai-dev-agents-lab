---
name: wf-sdd-audit
description: "Audita el ecosistema SDD detectando referencias rotas, skills huerfanas, violaciones de SSoT/SRP, contradicciones e inconsistencias. Soporta modos structural (rapido), content (profundo) y full (ambos). Delega al agente sdd-auditor."
when_to_use: "Activa con frases como 'audita el ecosistema', 'revisa que las skills sean SSoT', 'comprueba si hay contradicciones', 'verifica single responsibility', 'busca inconsistencias en las skills', 'chequea el estado del ecosistema'. No activa para crear o modificar skills (usa wf-skill-create, wf-agent-create) ni para auditar artefactos del pipeline SDD como specs o planes (usa wf-spec-validate, wf-plan-validate)."
argument-hint: "<structural|content|full> [--phase <prd|spec|design|plan|tasks|tech/<stack>|global>]"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: sdd-auditor
---

# wf-sdd-audit — Orquestador de Auditoria del Ecosistema SDD

Tu rol es de **orquestador puro**: parseas el modo y el alcance, recopilas los archivos a auditar, construyes el contexto para el agente y escribes el reporte final. No ejecutas la logica de auditoria directamente.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: primera palabra (`structural`, `content` o `full`)
- **`--phase`**: fase o `global` (por defecto `global` si no se especifica)

Si el modo no es valido, informa:
> "Uso: `/wf-sdd-audit <structural|content|full> [--phase <prd|spec|design|plan|tasks|tech/<stack>|global>]`"
>
> - `structural` — detecta referencias rotas, skills huerfanas y rootmap invalido (rapido)
> - `content` — detecta violaciones de SSoT, SRP, contradicciones e inconsistencias (profundo)
> - `full` — ambos modos en orden

---

## Paso 2: Determinar el alcance de archivos

Segun `--phase`:

**Si `--phase global` o no especificado:**
```bash
find sdd/ -name "SKILL.md" 2>/dev/null
find sdd/ -name "*.md" -path "*/agents/*" 2>/dev/null
find sdd/ -name "CLAUDE.md" 2>/dev/null
```

**Si `--phase <fase>`:**
```bash
find sdd/<fase>/ -name "SKILL.md" 2>/dev/null
find sdd/<fase>/ -name "*.md" -path "*/agents/*" 2>/dev/null
find sdd/<fase>/CLAUDE.md 2>/dev/null
# Incluir siempre el meta-ecosistema
find sdd/meta/ -name "SKILL.md" 2>/dev/null
find sdd/meta/ -name "*.md" -path "*/agents/*" 2>/dev/null
find sdd/meta/CLAUDE.md 2>/dev/null
```

Informa al usuario el numero de archivos encontrados:
> "Alcance: X skills, Y agentes, Z CLAUDE.md en <fase|ecosistema completo>."

---

## Paso 3: Leer todos los archivos del alcance

Lee el contenido completo de cada archivo encontrado en el paso anterior.

Para el modo `structural`: basta con leer frontmatter y secciones de rootmap.
Para los modos `content` y `full`: leer el cuerpo completo de cada skill y agente.

---

## Paso 4: Delegar al agente sdd-auditor

Construye el prompt para el agente con:

```text
Modo: <structural|content|full>
Alcance: <fase o global>
Numero de archivos: X skills, Y agentes, Z CLAUDE.md

Archivos a auditar:

=== SKILLS ===
[Para cada SKILL.md encontrado]
Path: <path>
---
<contenido completo>
---

=== AGENTES ===
[Para cada agente .md encontrado]
Path: <path>
---
<contenido completo>
---

=== CLAUDE.md ===
[Para cada CLAUDE.md encontrado]
Path: <path>
---
<contenido completo>
---
```

Invoca el agente `sdd-auditor` con ese prompt.

---

## Paso 5: Escribir el reporte

Determina el path de salida:
- `sdd/docs/audit_<modo>_<fase>.md`
- Ejemplo: `sdd/docs/audit_full_global.md`, `sdd/docs/audit_content_design.md`

Escribe el reporte del agente en ese archivo.

---

## Paso 6: Informar al usuario

Reporta:
- Path del reporte generado
- Resumen ejecutivo: total de hallazgos por severidad y tipo
- Si hay hallazgos bloqueantes (`[ROTO]` o `[CONTRADICCION]` bloqueante): listarlos directamente en la respuesta
- Estado global del ecosistema: `CONSISTENTE` / `INCONSISTENTE` (structural) y/o `LIMPIO` / `CON HALLAZGOS` (content)
- Siguiente paso sugerido:
  - Si hay hallazgos: `"Revisa el reporte en <path> y usa /wf-skill-create o /wf-agent-create para corregir, o delega directamente a sdd-author en modo refactor."`
  - Si no hay hallazgos: `"El ecosistema esta en buen estado. Proxima auditoria recomendada tras los proximos cambios significativos."`

**Ciclo de vida del reporte:** Una vez que todos los hallazgos del reporte hayan sido corregidos, elimina el archivo `sdd/docs/audit_<modo>_<fase>.md`. El reporte es un artefacto temporal de trabajo, no documentacion permanente del ecosistema.
