# Reporte de Auditoria SDD — Modo: full | Alcance: global
Fecha: 2026-06-11
Ecosistema: sdd/ (excluyendo .claude/ que son copias de despliegue)
Archivos auditados: ~130 SKILL.md (canonicos), 22 agentes canonicos, 9 CLAUDE.md

---

## SECCIÓN 1 — Auditoria Estructural

### Estado global: CONSISTENTE

No se detectaron referencias rotas, skills con nombre desincronizado ni agentes con skill: inexistente. Los hallazgos a continuación son advertencias y mejoras.

---

### [ADVERTENCIA] HUERFANA: kb-delivery-discipline

**Archivo:** `sdd/tasks/skills/kb-delivery-discipline/SKILL.md`
**Descripción:** Ningún agente la carga en su `skills: [...]`. La KB existe como SSoT del criterio de empaquetado de commits/PRs y es referenciada por texto desde `wf-task-run`, `wf-bug` y `kb-tasks-method`, pero no como dependencia cargada en contexto de ningún agente.
**Accion sugerida:** Evaluar si `task-generator` o `qa-engineer` deben cargarla. Si la KB es solo referenciada como enlace textual (no como contexto de razonamiento), documentar explícitamente que es una KB de referencia sin consumidor de agente, y añadir un comentario en `tasks/CLAUDE.md`.

---

### [NOTA] Nombres duplicados intencionales: kb-plan-expert y kb-tasks-expert

**Archivos:**
- `sdd/plan/skills/kb-plan-expert/SKILL.md` (genérico)
- `sdd/tech/kmm/skills/plan/kb-plan-expert/SKILL.md` (override KMM)
- `sdd/tasks/skills/kb-tasks-expert/SKILL.md` (genérico)
- `sdd/tech/kmm/skills/tasks/kb-tasks-expert/SKILL.md` (override KMM)

**Descripción:** Dos skills con el mismo `name:` en distintas rutas. Patrón documentado como intencional en `kb-sdd-stack-overlay-contract` (mecanismo de override por nombre de `install.sh`). No es un error estructural.
**Accion sugerida:** Ninguna. Patrón correcto de overlay.

---

## SECCIÓN 2 — Auditoria de Contenido

### Estado global: CON HALLAZGOS

---

### [MEDIA] INCONSISTENCIA: wf-project-init — effort declarado vs densidad real

**Archivo:** `sdd/bootstrap/skills/wf-project-init/SKILL.md`
**Sección:** Frontmatter — campo `effort`
**Descripción:** El workflow declara `effort: low` pero tiene 531 líneas de body y 10 pasos explícitos con lógica de entrevista, detección de estado, instalación de fases y verificación obligatoria. Por criterio de `kb-sdd-creation-guide`: `effort: low` es para ≤ 3 pasos simples sin delegación de agente. `wf-project-init` supera con creces el umbral de `high` (6+ pasos con contexto rico, incluyendo `AskUserQuestion` interactivo y llamadas shell).
**Accion sugerida:** Cambiar `effort: low` a `effort: high`. Evaluar también si parte del body puede moverse a `references/` para reducir la densidad del SKILL.md por debajo del umbral de 150 líneas (actualmente 531).

---

### [MEDIA] INCONSISTENCIA: wf-design-a11y-audit — effort medium con 14 pasos y agent

**Archivo:** `sdd/design/skills/wf-design-a11y-audit/SKILL.md`
**Sección:** Frontmatter — campo `effort`
**Descripción:** 14 pasos explícitos con delegación a agente. Por criterio de `kb-sdd-creation-guide`: `effort: medium` es para 3-6 pasos con posible delegación. Un workflow con 14 pasos y agente cae claramente en `effort: high`.
**Accion sugerida:** Cambiar `effort: medium` a `effort: high`.

---

### [MEDIA] INCONSISTENCIA: prd-expert — trigger phrase en description de agente

**Archivo:** `sdd/prd/agents/prd-expert.md`
**Sección:** Frontmatter — campo `description`
**Descripción:** La `description` termina con `"Invócalo cuando necesites crear un PRD desde cero, reorganizar uno existente, o revisar si el documento está bien planteado antes de entrar en Spec."` — esta es una frase de activación/trigger que, por convención de `kb-sdd-creation-guide`, pertenece al CUÁNDO (propio de `when_to_use` en `wf-*`, o ausente en agentes). La `description` debe describir el QUÉ hace el agente, no cuándo invocarlo.
**Accion sugerida:** Recortar la `description` para que termine en `"...procesable por el pipeline."` y eliminar la frase `"Invócalo cuando..."`. Opcionalmente añadir ese contexto al body del agente en la sección de rol.

---

### [BAJA] INCONSISTENCIA: agentes con "Invócalo desde wf-X" en description

**Archivos:**
- `sdd/plan/agents/plan-architect.md`
- `sdd/plan/agents/plan-auditor.md`
- `sdd/tasks/agents/task-generator.md`
- `sdd/tech/kmm/agents/plan-architect.md`
- `sdd/tech/kmm/agents/plan-auditor.md`
- `sdd/tech/kmm/agents/task-generator.md`

**Sección:** Frontmatter — campo `description`
**Descripción:** Todos incluyen `"Invócalo desde wf-X"` al final de la `description`. Esto mezcla el QUÉ hace el agente con una instrucción de activación. Las descriptions de agentes deben ser concisas y descriptivas del dominio; la instrucción de invocación puede vivir en el body del agente (sección de rol) o estar implícita desde el `CLAUDE.md` de fase.
**Accion sugerida:** Eliminar el sufijo `"Invócalo desde wf-X"` de las `description` de estos agentes. Mantener la referencia al workflow delegante en el body del agente si se considera útil.

---

### [MEDIA] INCONSISTENCIA (Criterio 6): wf-design-discover — sin check de existencia antes de escribir artefacto

**Archivo:** `sdd/design/skills/wf-design-discover/SKILL.md`
**Sección:** Entre Paso 4 (determinar path de salida) y Paso 9 (escribir el discovery)
**Descripción:** El workflow determina el path de `_design_discovery.md` en Paso 4 y lo escribe en Paso 9, pero no verifica si el archivo ya existe antes de sobreescribir. Un re-run sobre un discovery ya validado lo destruiría silenciosamente.
**Accion sugerida:** Añadir entre Paso 4 y Paso 5 un check de existencia: `!test -f "<path_calculado>" && echo "EXISTE" || echo "NO_EXISTE"`. Si existe, preguntar al usuario si quiere regenerar o detener.

---

### [MEDIA] INCONSISTENCIA (Criterio 6): wf-design-feedback — sin check de existencia en modo capture

**Archivo:** `sdd/design/skills/wf-design-feedback/SKILL.md`
**Sección:** Paso 2 (modo capture), instrucción de escritura de `_design_feedback.md`
**Descripción:** El modo `capture` escribe `<basename>_design_feedback.md` sin verificar si ya existe. Un feedback previo podría sobreescribirse silenciosamente.
**Accion sugerida:** Antes de la instrucción de escritura en el modo capture, añadir check de existencia con opción al usuario de sobreescribir, appendear o detener.

---

### [MEDIA] INCONSISTENCIA (Criterio 6): wf-prd-sync-impact — sin check de existencia antes de generar informe

**Archivo:** `sdd/spec/skills/wf-prd-sync-impact/SKILL.md`
**Sección:** Paso 5 (generar informe `_sync_report.md`)
**Descripción:** El workflow genera un `<basename>_sync_report.md` directamente en Paso 5 sin verificar si existe un informe previo. Sobreescritura silenciosa posible en re-runs.
**Accion sugerida:** Añadir check de existencia antes del Paso 5. Si existe, informar al usuario y pedir confirmación.

---

### [BAJA] INCONSISTENCIA: densidad de wf-* que superan threshold de 150 líneas

**Archivos:**
- `sdd/design/skills/wf-design-feature-prototype/SKILL.md` (164 líneas)
- `sdd/design/skills/wf-design-system/SKILL.md` (158 líneas)
- `sdd/plan/skills/wf-prepare-plan/SKILL.md` (164 líneas)
- `sdd/spec/skills/wf-spec-fast-track/SKILL.md` (173 líneas)
- `sdd/spec/skills/wf-spec-readiness/SKILL.md` (155 líneas)
- `sdd/spec/skills/wf-spec-delta/SKILL.md` (153 líneas)
- `sdd/tech/kmm/skills/wf-kmm-init/SKILL.md` (305 líneas)

**Descripción:** Superan el umbral de 150 líneas que activa revisión de SRP según `kb-sdd-creation-guide`. Los de 153-173 líneas son marginalmente superados y probablemente no necesitan acción urgente. `wf-kmm-init` con 305 líneas y `wf-project-init` con 531 son los casos más notables.
**Accion sugerida:** Revisar `wf-kmm-init` y `wf-project-init` para evaluar si pasos detallados pueden moverse a `references/` sin perder prescripción operativa. Para los casos marginales (153-173 líneas), solo actuar si se detecta SRP violation real.

---

## Resumen Ejecutivo

| Tipo | Severidad | Cantidad |
|---|---|---|
| HUERFANA | Advertencia | 1 |
| INCONSISTENCIA (effort) | Media | 2 |
| INCONSISTENCIA (trigger en description) | Media + Baja | 2 grupos |
| INCONSISTENCIA (Criterio 6 — existencia) | Media | 3 |
| INCONSISTENCIA (densidad) | Baja | 7 |

**Bloqueantes:** ninguno.
**Contradicciones:** ninguna detectada.
**Violaciones SSoT:** ninguna detectada.
**Violaciones SRP:** ninguna detectada (densidad elevada en wf-project-init y wf-kmm-init merece revisión pero no viola SRP actualmente).

---

## Siguiente paso

Revisa este reporte en `sdd/docs/audit_full_global.md` y usa `/wf-sdd-refactor <path>` para aplicar las correcciones, o delega directamente a `sdd-author` en modo refactor para los cambios de frontmatter. Una vez resueltos todos los hallazgos, elimina este archivo.
