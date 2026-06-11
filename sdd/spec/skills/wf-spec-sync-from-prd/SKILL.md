---
name: wf-spec-sync-from-prd
description: "Resincroniza specs de feature tras un PRD actualizado. Modo analyze: identifica features afectadas y genera requisitos de sincronizacion por feature; modo apply: integra esos cambios via delta sobre los specs afectados y actualiza su trazabilidad."
when_to_use: "Activa en frases como 'sincroniza los specs con el PRD', 'aplica el cambio de PRD a las features', 'que specs tengo que actualizar tras cambiar el PRD', 'resincroniza specs desde el PRD'."
argument-hint: "analyze <prd.md> | apply <prd.md> --features F-001,F-002,..."
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-writer
---

# Workflow: SPEC-SYNC-FROM-PRD

Tu objetivo es propagar un cambio de PRD a los feature specs afectados sin regenerar todo el sistema salvo que sea necesario.

Usa `kb-product-change-governance` para entender el cambio y `kb-traceability-rules` para decidir si basta con delta o si el impacto es demasiado amplio.

## Paso 1: Parsear argumentos

Modos soportados:

- `analyze <prd.md>`
- `apply <prd.md> --features F-001,F-002,...`

Si falta argumento:
> "Uso: `/wf-spec-sync-from-prd analyze <prd.md>`"
> "Uso: `/wf-spec-sync-from-prd apply <prd.md> --features F-001,F-002`"

## Paso 2: Preconditions

Requiere que exista al menos uno de:

- `<basename>_sync_report.md`
- `<basename>_features.md`
- specs bajo `features/`

Si no hay specs de feature, informa que todavía no hay nada que resincronizar y que debe generarse el flujo Spec normal.

## Submodo ANALYZE

### Paso 3A: Identificar features afectadas

**Pre-pass determinista**: antes del análisis experto, ejecuta desde la raíz del proyecto (si el script existe):

```
python3 .sdd/scripts/sdd-sync-check.py check-all <directorio_de_features> --mark
```

Los specs reportados `DERIVA` tienen evidencia mecánica de que el PRD cambió desde su sellado (el flag `--mark` degrada su `status_sync` a `needs_review`); los `IN_SYNC` están verificados contra el PRD actual. Usa ese resultado como punto de partida: el análisis experto decide si la deriva afecta realmente a cada feature (Regla 4 de `kb-traceability-rules`).

Usa `*_sync_report.md` si existe. Si no existe, deriva el impacto leyendo:

- PRD actual
- `*_features.md`
- specs existentes

Para cada feature potencialmente afectada:

- indica por qué está afectada
- clasifica severidad: `minor | major | structural`
- decide acción recomendada:
  - `delta`
  - `manual_review`
  - `rediscover`

### Paso 4A: Generar requisitos de sync por feature

Para cada feature afectada, escribe un archivo junto al spec de la feature (en el mismo directorio donde vive su `_spec.md`, sea `features/<nombre>/spec/` o `features/<nombre>/` en layout plano legacy):

`<directorio_del_spec>/<nombre>_sync_requirements.md`

Debe contener:

- cambio del PRD relevante para esa feature
- HUs y CAs probablemente afectados
- instrucciones para delta
- shared models o reglas transversales afectadas

### Paso 5A: Salida

Resume qué features pueden resolverse con delta y cuáles necesitan rediscovery o revisión manual.

## Submodo APPLY

### Paso 3B: Validar features solicitadas

Comprueba que los IDs existen en `_features.md` o pueden mapearse a specs existentes.

### Paso 4B: Aplicar sync por feature

Para cada feature solicitada:

1. localiza `<nombre>_sync_requirements.md`
2. si no existe, genera uno de forma mínima
3. aplica una actualización quirúrgica del spec siguiendo la misma disciplina que `wf-spec-delta`
4. actualiza la metadata de trazabilidad del spec para reflejar la versión actual del PRD (`derived_from_prd_version`, `derived_from_change`, `status_sync: in_sync`)
5. re-sella el hash de deriva ejecutando desde la raíz del proyecto: `python3 .sdd/scripts/sdd-sync-check.py seal <path_del_spec>` — NUNCA edites `derived_from_prd_hash` a mano (separación autor/verificador). Si el script falta, informa (⚠ re-ejecutar `install.sh`) y deja constancia de que el spec queda sin sello de deriva

Si el cambio rebasa un delta razonable, detén esa feature y marca:
> "Esta feature necesita rediscovery o rediseño de spec; no se aplicó sync automático."

### Paso 5B: Post-proceso

Después de cada spec actualizado:

- recomienda `wf-spec-conflict`
- recomienda `wf-spec-readiness`
- si hay planes existentes para esa feature, marca que deben revisarse
