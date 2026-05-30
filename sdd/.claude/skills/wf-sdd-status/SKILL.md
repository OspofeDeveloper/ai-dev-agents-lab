---
name: wf-sdd-status
description: "Genera un inventario rapido del ecosistema SDD: cuantas skills y agentes hay por fase, que KBs existen, que workflows estan registrados en los rootmaps y que KBs no tienen consumidor. Produce un snapshot estructurado sin ejecutar auditoria de contenido."
when_to_use: "Activa con frases como 'que skills tenemos', 'inventario del ecosistema', 'que hay en la fase design', 'cuantos agentes existen', 'muestra el estado del ecosistema', 'que workflows hay disponibles', 'lista todo lo que hay en sdd'. No activa para detectar problemas de SSoT o referencias rotas (usa wf-sdd-audit)."
argument-hint: "[--phase <prd|spec|design|plan|tasks|tech/<stack>|global>] [--output <path>]"
effort: low
allowed-tools: [Read, Bash]
context: fork
---

# wf-sdd-status — Inventario del Ecosistema SDD

Genera un snapshot estructurado del ecosistema. No requiere agente: es una operacion de recoleccion y conteo sin razonamiento experto.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **`--phase`**: fase a inventariar o `global` (por defecto `global`)
- **`--output`**: path del archivo de salida (opcional; si no se especifica, solo muestra en pantalla)

---

## Paso 2: Recopilar archivos por fase

**Si `--phase global` o no especificado**, recopila para cada fase (`prd`, `spec`, `design`, `plan`, `tasks`) y para el meta-ecosistema (`.claude`), y para cada tech target encontrado en `sdd/tech/`:

```bash
# Skills por fase
find sdd/<fase>/skills/ -name "SKILL.md" 2>/dev/null
find sdd/.claude/skills/ -name "SKILL.md" 2>/dev/null
find sdd/tech/ -name "SKILL.md" 2>/dev/null

# Agentes por fase
find sdd/<fase>/agents/ -name "*.md" 2>/dev/null
find sdd/.claude/agents/ -name "*.md" 2>/dev/null
find sdd/tech/ -name "*.md" -path "*/agents/*" 2>/dev/null

# Tech targets existentes
find sdd/tech/ -mindepth 1 -maxdepth 1 -type d 2>/dev/null
```

**Si `--phase <fase>`**, recopila solo para esa fase mas el meta-ecosistema.

---

## Paso 3: Leer frontmatters

Para cada `SKILL.md` encontrado, lee solo las primeras 10 lineas (frontmatter) para extraer `name:`, `description:` (primera linea) y si es `kb-*` o `wf-*`.

Para cada agente `.md` encontrado, lee solo las primeras 10 lineas para extraer `name:` y `skills: [...]`.

---

## Paso 4: Detectar KBs sin consumidor

Construye la lista de todas las KBs encontradas. Para cada una, comprueba si algun agente la lista en su `skills: [...]`:

```bash
grep -rl "<nombre-kb>" sdd/ --include="*.md" 2>/dev/null
```

Marca como `[SIN CONSUMIDOR]` las que no aparezcan en ningun agente.

---

## Paso 5: Detectar workflows sin rootmap entry

Para cada `wf-*` encontrada, comprueba si su nombre aparece en algun `CLAUDE.md`:

```bash
grep -rl "<nombre-wf>" sdd/ --include="CLAUDE.md" 2>/dev/null
```

Marca como `[SIN REGISTRAR]` las que no aparezcan en ningun rootmap.

---

## Paso 6: Construir el snapshot

Estructura el inventario con este formato:

```
# SDD Ecosystem Status
Fecha: <fecha>
Alcance: <fase o global>

## Resumen
- Skills totales: X (Y kb-*, Z wf-*)
- Agentes totales: N
- KBs sin consumidor: M
- Workflows sin registrar en rootmap: P

## Por fase

### <fase> (o .claude para meta-ecosistema)
Agentes (N):
  - <nombre> — <primera linea de description>

kb-* (Y):
  - <nombre> — <primera linea de description>

wf-* (Z):
  - <nombre> [SIN REGISTRAR?] — <primera linea de description>

### tech/<stack>
  [misma estructura]

## KBs sin consumidor
  - <path> — <nombre>

## Workflows sin registrar en rootmap
  - <path> — <nombre>
```

---

## Paso 7: Output

Si se especifico `--output`:
- Escribe el snapshot en el path indicado.
- Informa: `"Snapshot guardado en <path>."`

Si no se especifico `--output`:
- Muestra el snapshot directamente al usuario.

Sugiere al final:
- Si hay KBs sin consumidor: `"Considera conectarlas a un agente o eliminarlas. Usa /wf-sdd-audit structural para una verificacion completa."`
- Si hay workflows sin registrar: `"Añade las entradas faltantes al rootmap del CLAUDE.md correspondiente."`
