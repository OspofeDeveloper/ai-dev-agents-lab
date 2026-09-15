---
name: wf-prd-sync-impact
description: "Analiza el impacto de un PRD actualizado sobre los artefactos SDD ya generados (analysis, discovery, features, specs, plan, tasks) y produce un informe de sincronizacion con estado por artefacto y siguientes pasos."
when_to_use: "Activa en frases como 'que impacto tiene este cambio de PRD', 'que specs han quedado stale', 'analiza sync PRD → specs', 'que artefactos hay que revisar tras cambiar el PRD'. **Mide** el impacto y produce el informe; no toca ningún spec. Si lo que se quiere es **aplicar** el cambio a los specs, es wf-spec-sync-from-prd."
argument-hint: "<prd.md>"
effort: high
allowed-tools: [Read, Bash]
context: fork
agent: sdd-spec-auditor
user-invocable: true
---

# Workflow: PRD-SYNC-IMPACT

Tu objetivo es determinar qué artefactos derivados deben revisarse tras un cambio en el PRD.

Usa `kb-product-change-governance` y `kb-traceability-rules` para aplicar criterios conservadores: si no puedes demostrar que un artefacto sigue alineado, no lo marques `in_sync`.

## Paso 1: Parsear argumentos

Extrae el path del PRD.

Si falta:
> "Necesito el path del PRD cuyo impacto sobre los derivados quieres medir."

## Paso 2: Descubrir artefactos relacionados

En el directorio del PRD, busca si existen:

- `*_analysis.md`
- `*_discovery.md` — **no** los `*_code_discovery.md` ([[D-083]]): el mapa de capacidades del
  onramp brownfield encaja en ese glob por sufijo y **no deriva del PRD**, sino del código. Medir
  su deriva contra un cambio de producto es declarar `stale` lo que ningún cambio de PRD afecta
- `*_features.md`
- `features/*/spec/*_spec.md` (subcarpetas) **y** `features/*/*_spec.md` (plano legacy)
- `features/*/plan/*_plan.md` (subcarpetas) **y** `features/*/*_plan.md` (plano legacy)
- `features/*/tasks/*_tasks.md` (subcarpetas) **y** `features/*/*_tasks.md` (plano legacy)
- `product-changelog.md`
- `changes/CR-XXX/change-request.md`
- `changes/CR-XXX/decision.md`

> **Los dos layouts, siempre ([[D-067]]).** Buscar solo el plano legacy es el modo de fallo que
> [[D-046]] declaró inaceptable: en un proyecto con el layout estándar (subcarpetas por fase) este
> paso no encontraba **ningún** spec, plan ni tasks, y producía una matriz de impacto vacía que se
> lee como *"todo sincronizado"*. No falla: miente en silencio.

## Paso 3: Leer el contexto mínimo necesario

Lee:

- PRD actual
- changelog del producto si existe
- artefactos del cambio más recientes en `changes/CR-XXX/` si existen
- índice `_features.md` si existe
- headers y metadata de specs, plans y tasks
- contenido completo de los artefactos cuya sincronía no pueda decidirse solo por metadata

Si existe carpeta `changes/`, úsala como fuente prioritaria para entender el alcance exacto del último cambio aprobado. `product-changelog.md` sirve como índice; `change-request.md` y `decision.md` contienen el detalle operativo.

## Paso 4: Evaluar estado por artefacto

**Pre-pass determinista sobre los specs**: ejecuta desde la raíz del proyecto (si el script existe):

```
python3 .sdd/scripts/sdd-sync-check.py check-all <directorio_de_features> --mark
```

El resultado es evidencia mecánica, no opinión: `DERIVA` = el PRD cambió desde el sellado del spec (su `status_sync` queda en `needs_review`); `IN_SYNC` = verificado por hash contra el PRD actual; `SIN_SELLO`/`PRD_NO_RESUELVE` = sin evidencia (aplica el criterio conservador de `kb-traceability-rules`, Regla 3). Nunca marques `in_sync` un spec que el script reporta `DERIVA`.

Para cada artefacto, asigna uno de estos estados:

- `in_sync`
- `needs_review`
- `stale`
- `unknown`

Justifica el estado con una línea concreta.

Reglas:

- si el script reporta `DERIVA` para un spec, al menos `needs_review` (evidencia por hash)
- si el PRD cambió en una sección que afecta claramente al artefacto, al menos `needs_review`
- si el artefacto contradice el PRD actual, `stale`
- si no hay metadata ni evidencia suficiente, `unknown`

## Paso 5: Generar matriz de impacto

Produce un informe `<basename>_sync_report.md` con tablas separadas para:

> **Con qué lo escribes ([[D-051]]).** `sdd-spec-auditor` tiene `Write` y `Edit`
> **prohibidos** —el candado que impide que un auditor reescriba lo que audita—, así que
> este informe lo escribes **tú, con redirección por `Bash`** (`cat > "<path>" <<'EOF' …
> EOF`). **No le pases la escritura al hilo principal:** main no escribe artefactos
> ([[D-060]]), y si lo hace acaba volcando un heredoc con tu texto y firmándolo como suyo.
>
> **Este informe es efímero y lo dice en su cabecera.** Registra el estado de un momento:
> en cuanto el PRD vuelva a cambiar, o el derivado que señala se regenere, deja de ser
> cierto. Abre el documento con una línea `> Vigente para: PRD v<X.Y> — caduca al siguiente
> cambio de PRD`, y en el mensaje de cierre ofrece **no volcarlo** cuando el único derivado
> señalado se vaya a regenerar acto seguido: la conclusión ya está en la conversación y en
> el `product-changelog.md`.

- analysis/discovery/features index
- specs por feature
- plans por feature
- tasks por feature

Cada fila debe incluir:

- artefacto
- versión base conocida
- estado sync
- motivo
- acción recomendada

## Paso 6: Recomendar acciones

Mapea cada estado a un siguiente paso:

- `in_sync` → sin acción
- `needs_review` → **analizar la sincronización** de esa feature antes de tocar nada
- `stale` → **aplicar la sincronización** sobre ese spec, o regenerarlo explícitamente
- `stale` **porque la capacidad ya no está en el PRD** → ni sincronizar ni regenerar: **dar la feature de baja** ([[D-074]]). Dilo así en la columna, y nombra el `CR-XXX` que la retira. Las otras dos acciones son falsas aquí — no hay con qué poner al día un spec cuyo referente desapareció, y regenerarlo lo volvería a escribir. La baja la confirma una persona; tú solo la señalas

> **En lenguaje natural, no con el nombre del workflow.** Esta columna acaba **dentro del
> `_sync_report.md`**, que lo lee una persona: describe la acción, no la invocación. El usuario no
> teclea comandos, te lo pide hablando — y surfacear el nombre le enseña a pasar argumentos a mano
> saltándose las validaciones (regla de fase, `sdd-spec.md`).
- `unknown` → revisión manual o análisis de sync
