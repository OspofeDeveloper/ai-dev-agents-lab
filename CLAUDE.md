# Guías globales de Claude Code

## Patrones para crear skills

### Tipos de skills

#### `kb-` (Knowledge Base)
Bases de conocimiento puras. Definen reglas, convenciones y criterios de referencia. No ejecutan flujos — son consultadas por las skills `wf-*` como fuentes autoritativas (SSoT).

- `allowed-tools: [Read]` o vacío — nunca Write ni Bash
- El cuerpo se organiza en secciones `## Regla N: ...`
- **SKILL.md solo contiene reglas conceptuales** — sin bloques de código de implementación. Los diagramas ASCII de estructura (jerarquías, flujos) sí pueden quedarse porque son conocimiento, no implementación.
- Cuando una regla necesita código concreto (templates, snippets), añade al final de la regla un puntero: `→ Templates: references/nombre_fichero.md`. El agente leerá ese fichero bajo demanda.

#### `wf-` (Workflow)
Ejecutan pasos operacionales de un pipeline: parsean argumentos, leen/escriben archivos, y en algunos casos orquestan subagentes en paralelo.

- `disable-model-invocation` no se incluye (habilitado implícitamente)
- `allowed-tools: [Read, Write, Bash]` como mínimo
- Llevan `agent: <nombre-agente>` si la skill está pensada para ser ejecutada por un agente concreto
- El cuerpo se organiza en secciones `## Paso N: ...`
- **SKILL.md solo contiene pasos procedimentales** — sin bloques de código de implementación. Cada paso referencia la regla del kb- correspondiente (ej. "siguiendo la **Regla 3** del kb-") y opcionalmente el fichero de references concreto dentro del kb-.

Las `wf-*` consultan a las `kb-*` explícitamente en sus pasos para mantener las reglas en un único sitio.

---

### Frontmatter: qué ponemos y qué no

**Siempre presentes en todas las skills:**
```yaml
name: nombre-skill
description: "..."
argument-hint: "..."
effort: low | medium | high
allowed-tools: [...]
context: fork
```

**Solo en `kb-`:**
```yaml
disable-model-invocation: true
```

**Solo en `wf-` cuando la skill es para un agente concreto:**
```yaml
agent: nombre-agente
```

**NO ponemos (de momento):**
- `model:` — solo se añade en casos excepcionales y justificados (ej. orquestador que necesita un modelo más potente)
- Parámetros del modelo: temperatura, timeouts, etc.

**`context: fork`** — todas las skills lo llevan, sin excepción.

---

### Estructura de ficheros

```
<skill-name>/
├── SKILL.md
└── references/          ← obligatorio si SKILL.md necesitaría bloques de código
    ├── *_templates.md   ← snippets, plantillas de output, ejemplos de código
    └── *_patterns.md    ← catálogos de patrones o tablas de lookup
```

**Cuándo crear `references/`:**
- En `kb-*`: siempre que una regla necesite código de implementación concreto (snippets de configuración, templates de ficheros, etc.). El SKILL.md apunta a ellos; el agente los lee bajo demanda.
- En `wf-*`: cuando el workflow genera artefactos complejos cuya estructura es una plantilla reutilizable (templates de output, scaffolds de ficheros).

**Qué va en `references/` y qué no:**
- Sí: código de implementación, snippets, templates de ficheros, catálogos de patrones, tablas de lookup
- No: definiciones normativas ni reglas — esas van siempre en SKILL.md (SSoT)

---

### Arquitectura de carga por capas

Cuando un agente tiene skills `kb-*` declaradas en su frontmatter, esos SKILL.md se cargan en contexto automáticamente. Para mantener ese contexto ligero y eficiente, se aplica lazy-loading:

```
Agente (tiene kb- en contexto via frontmatter)
  → SKILL.md del kb- = reglas conceptuales, ligero, siempre disponible
  → Ejecuta un paso del wf- que dice "aplicar Regla X del kb-"
  → Regla X (ya en contexto) dice "→ Templates: references/fichero.md"
  → Agente lee references/fichero.md bajo demanda, solo cuando lo necesita
```

**Implicaciones al diseñar una skill:**
- Si el código de un snippet va en SKILL.md, se carga siempre aunque no se use → va a `references/`.
- Si la regla conceptual va en `references/`, no está disponible sin leer → va en SKILL.md.
- El wf- nunca duplica código: si necesita un snippet, referencia el kb- que lo tiene en sus references.

---

### Principios de calidad de skills

#### Single Source of Truth (SSoT)
Cada regla, convención o restricción debe vivir en **un único lugar**. Si la misma regla aparece en SKILL.md y en un archivo de referencia, hay dos fuentes y una se quedará desactualizada.

- Las reglas van en SKILL.md. Los archivos de `references/` solo contienen código de ejemplo o templates — nunca definiciones normativas duplicadas.
- Si una `wf-*` consulta una `kb-*`, no repite las reglas inline: las delega por completo a la `kb-*`.

#### Single Responsibility (SRP)
Cada skill tiene **una responsabilidad bien delimitada**. Si el `description` del frontmatter necesita dos frases con "y" para explicarse, probablemente son dos skills.

- Una `kb-*` cubre un único dominio conceptual (ej. navegación, recursos, inyección de dependencias).
- Una `wf-*` ejecuta un único pipeline (ej. generar tasks, crear un módulo de feature).

#### Sin contradicciones entre skills
Antes de crear o actualizar un skill, verificar que no contradice ni duplica contenido de otro skill existente.

- Si dos `kb-*` cubren conceptos solapados, uno de ellos debe ser la fuente autoritativa y el otro debe referenciarla explícitamente.
- Si una regla cambia, actualizar **solo** la skill SSoT — las demás la delegan.
