# Plantillas de prompt para el agente plan-architect

## Bloque base (siempre presente)

```text
Modo: generate-plan
Path del spec: <path_completo>
Contenido del Spec:
---
<contenido_completo_del_spec>
---
```

## Bloque shared models (si existe `_features.md`)

```text
Shared models del proyecto (NO redefinir — solo referenciar):
---
<sección relevante o contenido completo de _features.md>
---
INSTRUCCIÓN: Si algún modelo de la tabla anterior aparece en el Spec de esta feature, no lo redefinas en el Plan salvo que esta feature sea la owner.
```

## Bloque handoff de Design (si la feature requiere Design)

```text
La feature requiere handoff de Design.
Contenido de DESIGN.md:
---
<contenido_design>
---
Contenido de <feature>_flows.md:
---
<contenido_flows>
---
Contenido de <feature>_views.md:
---
<contenido_views>
---
INSTRUCCIÓN: trata estos artefactos como fuentes normativas para UI, navegación y accesibilidad. Si detectas contradicciones o falta información crítica, devuelve `DESIGN_GAPs` y no produzcas el Plan.
```

## Bloque sin Design (si la feature no tiene UI)

```text
La feature no tiene superficie UI visible. No se adjunta handoff de Design.
```

## Bloque final (siempre presente)

```text
INSTRUCCIÓN: Propaga al header del Plan cualquier metadata de trazabilidad presente en el Spec (`derived_from_prd`, `derived_from_prd_version`, `derived_from_change`, `status_sync`). Si falta, usa `unknown`.
INSTRUCCIÓN: El Plan generado debe salir con `Estado: BORRADOR`.
```
