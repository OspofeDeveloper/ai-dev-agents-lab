# Reporte de Auditoría SDD — full / global
**Fecha:** 2026-05-31
**Alcance:** Ecosistema completo (91 skills, 17 agentes, 8 CLAUDE.md)
**Modo:** full (structural + content)

---

## Parte 1: Auditoría Estructural

### Estado global: INCONSISTENTE

---

#### [ADVERTENCIA] INCONSISTENCIA — Frontmatter: `agent:` declarado sin `Agent` en `allowed-tools`

**Archivo:** `sdd/prd/skills/wf-prd-create/SKILL.md`
**Referencia:** campo `agent: prd-expert` + `allowed-tools: [Read, Write, Bash]`
**Descripción:** `wf-prd-create` declara `agent: prd-expert` y en su cuerpo (Paso 4) invoca explícitamente al agente `prd-expert`. Sin embargo, `allowed-tools` no incluye `Agent`, lo que impide que el harness resuelva la delegación correctamente.
**Acción sugerida:** Añadir `Agent` a `allowed-tools: [Read, Write, Bash, Agent]`.

---

#### [ADVERTENCIA] INCONSISTENCIA — Frontmatter: `agent:` declarado pero el cuerpo no delega al agente

**Archivos:** `sdd/prd/skills/wf-prd-change/SKILL.md` y `sdd/prd/skills/wf-prd-review/SKILL.md`
**Referencia:** campo `agent: prd-expert` en ambos; cuerpos operan inline usando las KBs directamente sin invocar subagente
**Descripción:** Ambas workflows declaran `agent: prd-expert` en el frontmatter, pero sus cuerpos (pasos de análisis y escritura) no invocan a `prd-expert` como subagente — trabajan inline consultando `kb-prd-expert`. El campo `agent:` en una `wf-*` solo tiene sentido cuando la delegación es real y debe ir acompañada de `Agent` en `allowed-tools`. Aquí el campo es un residuo que no coincide con el comportamiento real.
**Acción sugerida:** Eliminar el campo `agent: prd-expert` de ambas workflows (y confirmar que ninguna necesita delegación real). Si en el futuro se refactorizan para delegar, añadir `Agent` a `allowed-tools`.

---

#### [ADVERTENCIA] INCONSISTENCIA — Modelo no canónico en `wf-spec-features-first`

**Archivo:** `sdd/spec/skills/wf-spec-features-first/SKILL.md`
**Referencia:** `model: claude-opus-4-6`
**Descripción:** Los modelos válidos definidos en `kb-sdd-creation-guide` son `claude-opus-4-7`, `claude-sonnet-4-6` y `claude-haiku-4-5`. El valor `claude-opus-4-6` no pertenece a la lista canónica actual. Las `wf-*` normalmente no declaran `model` — ese campo es propio de agentes. Si la intención es que esta wf use un modelo específico como orquestador propio, el modelo declarado debe ser uno de los válidos.
**Acción sugerida:** Actualizar `model: claude-opus-4-6` a `model: claude-sonnet-4-6` (o al modelo que corresponda) o eliminar el campo si no es necesario.

---

### Estado global Estructural: INCONSISTENTE (3 hallazgos de advertencia, 0 bloqueantes)

**Sin hallazgos de:**
- Referencias rotas en `skills: [...]` de agentes (todas las KBs declaradas existen)
- `wf-*` con `agent:` que apuntan a archivos inexistentes
- Entradas de rootmap en CLAUDE.md apuntando a skills inexistentes
- Skills huérfanas sin consumidor
- Nombres de directorio desincronizados con `name:` de frontmatter
- Agentes con `name:` desincronizado del nombre de archivo

---

## Parte 2: Auditoría de Contenido

### Estado global: CON HALLAZGOS

---

### SSoT / Inconsistencias de frontmatter masivas

#### [MEDIA] INCONSISTENCIA — `argument-hint` presente en la mayoría de `kb-*` (campo prohibido por template)

**Archivos afectados:** 47 de 54 `kb-*` del ecosistema (ver lista al final)
**Sección:** frontmatter
**Descripción:** La plantilla canónica de `kb-*` en `kb-sdd-creation-guide` (sección "Frontmatter para kb-*") establece explícitamente: "Nunca añadir `context: fork`, `agent:` ni `argument-hint` a una `kb-*`." Sin embargo, 47 de 54 KBs del ecosistema tienen el campo `argument-hint`. Las 7 sin el campo son: `kb-plan-kmm-ui-text`, `kb-cmp-resources`, `kb-plan-cmp-ui`, `kb-plan-expert`, `kb-plan-kmm-datastore-preferences`, `kb-tasks-kmm-navigation-viewmodel-events`, `kb-tasks-cmp-ui`, `kb-tasks-koin`, `kb-tasks-expert`.

El campo parece haberse heredado de una convención anterior o de un template distinto. En las KBs de `design` y `spec` el valor es del tipo "(cargada automaticamente por...)", lo que es informativo pero no es `argument-hint` en el sentido de las `wf-*`. En las KBs de `kmm/tasks/` los valores sí parecen hints de uso. En cualquier caso, el campo no está en el contrato formal de `kb-*`.

**ACCION-COMPLEJA:** Actualizar 47 archivos para eliminar o mover el campo. Antes de ejecutar, confirmar si el harness de Claude Code usa `argument-hint` en KBs de alguna forma especial — si no, es una limpieza de rutina.
**Acción sugerida:** Ejecutar `/wf-sdd-refactor` sobre las KBs en lotes por fase. Alternativamente, si la intención es mantener `argument-hint` en KBs como campo descriptivo, actualizar el template en `kb-sdd-creation-guide` para documentar esta excepción.

---

#### [BAJA] INCONSISTENCIA — `when_to_use` presente en muchas `kb-*` (campo no contemplado en template de KB)

**Archivos afectados:** 37 de 54 `kb-*` (principalmente `spec/`, `design/`, `prd/`, `tasks/` y `tech/kmm/tasks/`)
**Sección:** frontmatter
**Descripción:** La sección "Frontmatter para `kb-*`" del template canónico no incluye `when_to_use`. Ese campo está definido como exclusivo de `wf-*` (frases de activación y exclusiones). Algunas KBs con `when_to_use` contienen frases del tipo "Activa cuando el usuario quiera...", que mezclan semántica de routing (propio de `wf-*`) con la KB.

No hay contradicción normativa explícita que lo prohíba para `kb-*` (a diferencia de `argument-hint`), pero sí hay inconsistencia: las KBs del meta-ecosistema (`.claude/skills/kb-sdd-*`) no tienen `when_to_use` sino `argument-hint`, mientras que las KBs de fases operativas usan el patrón inverso.

**Acción sugerida:** Decidir una política uniforme: (a) eliminar `when_to_use` de las KBs que lo tienen y mover las frases de activación a la `description`, o (b) actualizar el template para permitir `when_to_use` en KBs con finalidad de routing parcial. Aplicar con `/wf-sdd-refactor` o `/wf-skill-create` según decisión.

---

### SRP

#### [REVISAR] SRP — `sdd-author` cubre creación y refactorización (advertencia documentada)

**Archivo:** `sdd/.claude/agents/sdd-author.md`
**Sección:** "Nota de evolucion"
**Descripción:** El propio agente documenta explícitamente que mezcla dos modos cognitivos (`create` y `refactor`) y señala cuándo convendría separar. No es una violación activa — hay evidencia de que el autor es consciente y la decisión está documentada. La partición se aplaza hasta evidencia de degradación de calidad.
**Acción sugerida:** Ninguna por ahora. Revisar si los próximos usos reales de `wf-sdd-refactor` muestran degradación de calidad en el modo `refactor` respecto al modo `create`. Si ocurre, activar la partición: crear `sdd-author` (creator) + `sdd-refactorer` (refactorer).

---

#### [REVISAR] SRP — `design-architect` cubre 5 modos cognitivos (advertencia documentada)

**Archivo:** `sdd/design/agents/design-architect.md`
**Sección:** "Nota de evolucion"
**Descripción:** Al igual que `sdd-author`, el agente documenta la mezcla de modos y la condición para partir. No es violación activa. El agente cubre generación, validación, evolución, auditoría de accesibilidad y triage de feedback.
**Acción sugerida:** Ninguna por ahora. El propio archivo tiene el recordatorio de cuándo partir.

---

### Inconsistencias de frontmatter específicas

#### [MEDIA] INCONSISTENCIA — `kb-plan-expert` ubicada en `tech/kmm/` pero define la fase genérica `plan`

**Archivo:** `sdd/tech/kmm/skills/plan/kb-plan-expert/SKILL.md`
**Sección:** Nota de ubicación (línea 11)
**Descripción:** La KB documenta explícitamente que su contenido no es específico de KMM sino del pipeline SDD genérico, y que está en `tech/kmm/` solo porque KMM es el único tech target actual. Si se añade un segundo tech target, esta KB deberá moverse a `sdd/plan/skills/`. Actualmente `plan-architect` y `plan-auditor` la cargan desde `tech/kmm/skills/plan/`, lo cual funciona pero crea una dependencia implícita al stack cuando la regla dice que la fase `plan` debería ser tech-agnostic.
**Acción sugerida:** Crear `sdd/plan/skills/kb-plan-expert/` y mover el contenido antes de añadir un segundo tech target. No es urgente mientras KMM sea el único stack.

---

#### [BAJA] INCONSISTENCIA — `plan-auditor` no carga `kb-plan-cmp-ui` ni `kb-cmp-resources` que sí carga `plan-architect`

**Archivos:** `sdd/plan/agents/plan-auditor.md` vs `sdd/plan/agents/plan-architect.md`
**Sección:** `skills: [...]` de cada agente
**Descripción:** `plan-architect` carga `kb-plan-cmp-ui` y `kb-cmp-resources` para decidir la arquitectura de presentación CMP. `plan-auditor` no las carga. En teoría el auditor debería poder verificar que el plan usa correctamente las convenciones CMP (si la feature tiene UI), pero actualmente no tiene ese contexto.
**Acción sugerida:** Evaluar si `plan-auditor` necesita verificar decisiones de CMP en su auditoría. Si sí, añadir `kb-plan-cmp-ui` y `kb-cmp-resources` a su `skills: [...]`.

---

### Inconsistencias de contenido

#### [BAJA] INCONSISTENCIA — `wf-design-intake` no declara `agent:` pero la tabla CLAUDE.md de design la describe como que "delega"

**Archivo:** `sdd/design/skills/wf-design-intake/SKILL.md`
**Sección:** frontmatter (sin campo `agent:`)
**Descripción:** `wf-design-intake` opera completamente inline (sin delegación a agente), lo cual es correcto por diseño — el proceso de cerrar el brief es interactivo y estructurado. Sin embargo, el `CLAUDE.md` de la fase design la describe en la tabla de capas como "capa intake" diferenciada, lo que podría llevar a confusión sobre si usa `design-architect`. La skill opera de forma autónoma correctamente.
**Acción sugerida:** Ninguna en el código. Solo documentar en el body de `wf-design-intake` (si aún no existe) que el workflow es autónomo y no delega a un agente.

---

### Resumen de hallazgos

| Severidad | Tipo | Total |
|---|---|---|
| Advertencia | INCONSISTENCIA frontmatter (agent/allowed-tools) | 3 |
| Media | INCONSISTENCIA frontmatter argument-hint en kb-* | 1 (47 archivos afectados) |
| Baja | INCONSISTENCIA when_to_use en kb-* | 1 (37 archivos afectados) |
| Revisar | SRP documentado y bajo control | 2 |
| Media | INCONSISTENCIA ubicación kb-plan-expert | 1 |
| Baja | INCONSISTENCIA cobertura plan-auditor vs plan-architect | 1 |
| Baja | INCONSISTENCIA wf-design-intake autónoma no documentada | 1 |

**Pares con contradicciones bloqueantes:** ninguno

**Sin hallazgos de:**
- Violaciones de SSoT (reglas duplicadas en múltiples lugares)
- Contradicciones entre skills (ningún par de skills define de forma incompatible la misma decisión o frontera)
- Inconsistencias de nombrado entre fases (todas las skills siguen el patrón `kb-<fase>-<dominio>` o `wf-<fase>-<accion>`)
- Agentes sin sección `## Verificación de contexto` (todos los agentes con `skills: [...]` la tienen)
- `wf-*` con Write sin existencia check (todas tienen `!test -f`)

---

## Estado global del ecosistema

| Dimensión | Estado |
|---|---|
| Estructural | INCONSISTENTE (advertencias de frontmatter, 0 bloqueantes) |
| Contenido | CON HALLAZGOS (ninguno bloqueante ni contradictorio) |

**Hallazgo prioritario de acción:** El campo `argument-hint` en 47 `kb-*` es el hallazgo más extendido. Es una operación de limpieza masiva con bajo riesgo funcional pero alto ruido de inconsistencia respecto al template canónico.

**Segundo hallazgo prioritario:** Las tres workflows PRD con campo `agent:` inconsistente (una sin `Agent` en `allowed-tools`, dos con `agent:` fantasma).

---

## Siguiente paso sugerido

Revisa este reporte y usa `/wf-sdd-refactor` para corregir los hallazgos, empezando por:

1. `wf-prd-create`: añadir `Agent` a `allowed-tools`
2. `wf-prd-change` y `wf-prd-review`: eliminar campo `agent:` fantasma
3. `wf-spec-features-first`: actualizar `model: claude-opus-4-6` a valor canónico
4. Plan de limpieza para `argument-hint` en `kb-*` (47 archivos — coordinar con usuario)

**Ciclo de vida de este reporte:** Eliminar `sdd/.claude/audit_full_global.md` cuando todos los hallazgos estén corregidos.
