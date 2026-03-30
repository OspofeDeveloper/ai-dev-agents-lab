---
name: spec-decompose
description: Workflow interno para el modo DECOMPOSE del agente sdd-analyst. Define cómo partir un Spec monolítico en Specs por feature independientes. Cargado como contexto por sdd-analyst — no invocar directamente.
allowed-tools: [Read]
disable-model-invocation: true
---

# Workflow: DECOMPOSE

Tu objetivo es partir el Spec monolítico en Specs por feature independientes y autocontenidos. Usa `decompose-expert` para cada decisión de partición y `spec-expert` para verificar que cada spec de feature resultante es un Spec SDD válido.

**Regla de oro:** Nunca inventas — solo filtras y renumeras. Los HUs, Journeys y CAs del spec de feature son copias literales del spec monolítico, nunca reescrituras.

---

## Qué debes hacer

1. **Identificar features** usando las reglas de `decompose-expert` (cohesión funcional, no secciones del documento)
2. **Validar cada feature candidata** contra los 3 criterios: Journeys independientes, mínimo 3 CAs propios, actor claro
3. **Declarar shared models**: para cada modelo que aparezca en más de una feature, determinar su owner usando las reglas de `decompose-expert`
4. **Producir `_features.md`** usando `references/features_template.md`
5. **Producir un `_spec.md` por feature** usando `references/feature_spec_template.md`

---

## Restricciones de contenido

- Los HUs, Journeys y CAs se copian literalmente del spec monolítico — nunca reescribir
- Los CAs de cada feature se renumeran desde CA-001 (la numeración es local a la feature)
- Si hay duda sobre si un elemento pertenece a una feature → incluirlo (no omitir)
- Los actores de cada feature spec son un subconjunto filtrado de los actores del spec monolítico

---

## Formatos de output

- Para el índice de features: consulta `references/features_template.md`
- Para cada spec de feature: consulta `references/feature_spec_template.md`
- Para el README de cada carpeta de feature: consulta `references/feature_readme_template.md`

Por cada feature generada, produce también un `README.md` en su carpeta usando el template. El README incluye: Feature ID, actor principal, path del spec, tabla de shared models (propios y referenciados) y la tabla de artefactos con el estado inicial (spec=✓, plan=—, tasks=—). Las dependencias entre features (cuáles deben implementarse antes) se infieren de los shared models: una feature que solo *referencia* un modelo depende de la feature que lo *ownnea*.
