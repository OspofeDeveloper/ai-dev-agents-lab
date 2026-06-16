---
name: wf-conformance-author
description: "Audita la cobertura de conformance de una skill (o de una fase entera) contra el catalogo de Casos de Uso y escribe los escenarios CU-N.x que falten en formato verbatim, actualizando la matriz del ROADMAP. Delega al agente sdd-conformance. Espejo de autoria de wf-sdd-audit."
when_to_use: "Activa con frases como 'escribe los casos de conformance de wf-spec-delta', 'audita la cobertura de conformidad de esta skill', 'que escenarios CU le faltan a la fase plan', 'completa los huecos del ROADMAP de conformance', 'deriva los 4 ejes de esta skill'. No activa para auditar el ecosistema en busca de SSoT/referencias rotas (usa wf-sdd-audit) ni para ver la cobertura sin escribir (usa wf-conformance-status). Tampoco para QA de un spec de producto (usa wf-qa-plan/wf-qa-verify)."
argument-hint: "<skill-name|phase> [--cu <cu-NN>]"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: sdd-conformance
user-invocable: true
---

# wf-conformance-author — Autoría de escenarios de conformance

Tu rol es de **orquestador puro**: parseas el objetivo, localizas el/los `SKILL.md` + los `cu-NN` que lo tocan + su fila del ROADMAP, construyes el contexto para el agente y dejas que escriba. No derivas los ejes ni redactas escenarios directamente: eso lo hace el agente `sdd-conformance` con `kb-sdd-conformance` cargada.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Objetivo** (primer token posicional): el `name` de una `wf-*` (`wf-spec-delta`) **o** una fase (`prd`, `spec`, `design`, `plan`, `tasks`, `meta`, `bootstrap`).
- **`--cu <cu-NN>`** (opcional): fuerza el fichero `cu-NN` donde el agente debe escribir (p. ej. `--cu cu-03`). Si se omite, el agente elige el CU temáticamente correcto (`kb-sdd-conformance` Regla 8).

Si falta el objetivo, informa:
> "Uso: `/wf-conformance-author <skill-name|phase> [--cu <cu-NN>]`"
>
> - `<skill-name>` — audita y completa la cobertura de una sola `wf-*` (ej. `wf-spec-delta`).
> - `<phase>` — recorre todas las `wf-*` de esa fase del ROADMAP.

---

## Paso 2: Resolver el alcance de skills

**Si el objetivo es un `wf-*` concreto**, localiza su `SKILL.md`:
```bash
find sdd/ -path "*/<objetivo>/SKILL.md" 2>/dev/null
```
Si no aparece, informa que la skill no existe y para.

**Si el objetivo es una fase**, lista sus `wf-*` desde la sección de esa fase del ROADMAP:
```bash
find sdd/ -path "*/<fase>/skills/wf-*/SKILL.md" 2>/dev/null
```
(en modo fase, el alcance son las filas de esa sección del ROADMAP; procesa una skill a la vez para no diluir el contexto del agente).

---

## Paso 3: Localizar el contexto de conformance

Para la skill objetivo:

1. **Su fila del ROADMAP** — extrae la fila de `conformance/ROADMAP.md` cuya primera celda es el nombre de la skill, incluyendo la columna *CU que lo ejercitan*:
   ```bash
   grep -nE "^\| <objetivo> \|" conformance/ROADMAP.md
   ```
2. **Los `cu-NN` que la tocan** — los IDs `CU-N` que aparecen en esa columna (o el `--cu` forzado). Lee esos ficheros completos:
   ```bash
   ls conformance/casos-de-uso/cu-*.md
   ```
3. **Los IDs ya usados** en esos ficheros, para que el agente continúe la secuencia sin colisión:
   ```bash
   grep -oE 'CU-[0-9]+\.[a-z]+' conformance/casos-de-uso/cu-0N-*.md | sort -u
   ```

Lee también el `SKILL.md` objetivo completo (frontmatter + pasos + gates + flags).

---

## Paso 4: Delegar al agente sdd-conformance

Construye el prompt:

```text
Objetivo: <skill-name>
CU forzado: <cu-NN o "elige el temáticamente correcto">

=== SKILL.md BAJO PRUEBA ===
Path: <path>
---
<contenido completo del SKILL.md>
---

=== FILA ACTUAL EN ROADMAP ===
<la fila + su columna "CU que lo ejercitan">

=== ESCENARIOS YA EXISTENTES (cu-NN que la tocan) ===
Path: conformance/casos-de-uso/<cu-NN>.md
---
<contenido completo de cada cu-NN relevante>
---

=== IDS YA USADOS (no reutilizar) ===
<lista de CU-N.x existentes>

Tarea: aplica el método de kb-sdd-conformance. Cruza el SKILL.md contra los escenarios
existentes, clasifica los 4 ejes, escribe SOLO los huecos en formato verbatim en el cu-NN
correcto continuando la secuencia de letras, y actualiza la fila del ROADMAP (ejes, CU que
lo ejercitan, Estado, Huecos detectados). Recalcula el contador de progreso.
```

Invoca el agente `sdd-conformance` con ese prompt. El agente escribe directamente en los `cu-NN` y en `ROADMAP.md`.

---

## Paso 5: Verificación determinista post-escritura

Tras el agente, comprueba que no quedaron IDs duplicados (gate de `kb-sdd-conformance` Regla 1):
```bash
grep -hoE 'CU-[0-9]+\.[a-z]+' conformance/casos-de-uso/cu-*.md | sort | uniq -d
```
Cualquier salida = ID duplicado introducido → repórtalo como bloqueo y pide al agente renombrar antes de cerrar.

Verifica también que el contador de **Progreso** del ROADMAP cuadra con la suma de estados (Regla 6):
```bash
grep -cE '\| (COMPLETADO|REVISADO|CON-HUECOS|PENDIENTE) \|' conformance/ROADMAP.md
```

---

## Paso 6: Informar al usuario

Reporta:
- Skill(s) procesada(s) y su **Estado** resultante en el ROADMAP.
- Escenarios nuevos escritos: sus `CU-N.x` y el fichero donde aterrizaron.
- Ejes que quedaron `🟡`/`❌`/`—` con su justificación (los *Huecos detectados*).
- Si la verificación del Paso 5 detectó duplicados o el contador no cuadra: **márcalo como bloqueante** y no des la skill por cerrada.
- Siguiente paso sugerido:
  - Si quedan huecos abiertos: `"Resuélvelos con otra pasada de /wf-conformance-author <skill> o ejecuta los escenarios y reporta desviaciones."`
  - Si la skill quedó `COMPLETADO`/`REVISADO`: `"Cobertura cerrada. Usa /wf-conformance-status para ver el progreso global (X/N)."`
