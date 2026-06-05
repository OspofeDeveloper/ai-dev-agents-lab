# Checklists de registro

Checklists completos para verificar que cada pieza del ecosistema queda correctamente registrada tras su creación o actualización.

---

## Tras crear una `kb-*`

- [ ] `SKILL.md` con frontmatter correcto en el directorio correcto
- [ ] Agente(s) que la consumen actualizados: añadir a su `skills: [...]`
- [ ] Si es cross-fase: documentar dependencia en el `CLAUDE.md` de la fase consumidora
- [ ] Si formaliza una regla que estaba inline en otros archivos: eliminar los duplicados
- [ ] Si tiene archivos de soporte: referencias usan `${CLAUDE_SKILL_DIR}/<path>`
- [ ] Ejecutar `wf-sdd-status` para regenerar `sdd/meta/skill-registry.md`

---

## Tras crear una `wf-*`

- [ ] `SKILL.md` en el directorio correcto con `context: fork`
- [ ] `description` contiene solo la funcionalidad; triggers y exclusiones en `when_to_use`
- [ ] Entrada en el rootmap del `CLAUDE.md` de fase (o del orquestador global si es transversal)
- [ ] Si tiene `agent:`: verificar que el agente existe y acepta el modo operativo
- [ ] Precondiciones documentadas en el body del `SKILL.md`
- [ ] Output explícito: qué archivo escribe y en qué directorio
- [ ] Si genera un artefacto de salida: incluye verificación de existencia previa justo antes del paso de escritura (patrón `!test -f "<path>" + pregunta al usuario`)
- [ ] Si tiene archivos de soporte: referencias usan `${CLAUDE_SKILL_DIR}/<path>`
- [ ] Ejecutar `wf-sdd-status` para regenerar `sdd/meta/skill-registry.md`

---

## Tras crear un agente

- [ ] Archivo `.md` con frontmatter correcto en `agents/`
- [ ] `model` seleccionado según tabla de criterios: decisión arquitectónica/codificación agéntica → `claude-opus-4-7`; escritura estructurada/exploración/auditoría/planificación → `claude-sonnet-4-6`
- [ ] `effort: high` añadido si el agente genera artefactos complejos
- [ ] `disallowedTools: Write, Edit` añadido si el system prompt declara que no escribe archivos (y el agente no produce artefactos diagnósticos intermedios)
- [ ] `color` asignado según fase/dominio del agente (tabla en `frontmatter-templates.md`)
- [ ] Sección `## Agentes disponibles` del `CLAUDE.md` de fase actualizada
- [ ] Todas las `kb-*` en `skills: [...]` existen físicamente
- [ ] Si el agente es el target de una `wf-*`: verificar que `agent: <nombre>` apunta al nombre correcto
- [ ] Ejecutar `wf-sdd-status` para regenerar `sdd/meta/skill-registry.md`

---

## Para crear un nuevo `CLAUDE.md`

- [ ] Sección `## Tu rol` con límites explícitos (qué hace y qué NO hace)
- [ ] Rootmap completo con todas las `wf-*` y agentes accesibles desde esta fase
- [ ] Cada `wf-*` del rootmap existe físicamente en `skills/`
- [ ] Cada agente referenciado existe físicamente en `agents/`
- [ ] No duplica reglas de `kb-sdd-skill-architecture` ni `kb-sdd-creation-guide`
- [ ] No contiene plantillas de frontmatter, comandos shell ni listas de pasos operativos
- [ ] Si es un `CLAUDE.md` de fase: solo referencia agentes y skills de esa fase
- [ ] El orquestador no contiene lógica de ejecución inline: delega siempre a una `wf-*` o agente (Regla 17 de `kb-sdd-skill-architecture`)

---

## Para actualizar un `CLAUDE.md` existente

- [ ] Nueva `wf-*` añadida al rootmap con intención, nombre y argumentos correctos
- [ ] Nuevo agente añadido a `## Agentes disponibles` si es accesible directamente
- [ ] Si se eliminó una `wf-*` o agente: entrada eliminada del rootmap
- [ ] Si se renombró: referencia actualizada en rootmap y sección de agentes
- [ ] Sección `## Cómo actuar` sigue siendo coherente con el estado actual del rootmap
