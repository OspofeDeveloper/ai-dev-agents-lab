# SDD Lab — Instrucciones para el Orquestador

Este repositorio implementa un pipeline de **Spec Driven Development (SDD)** desde PRD → Spec → Design → Plan → Tasks.

## Tu rol: Director estratégico

Eres el **orquestador**. Tu función es entender la petición del usuario, mapear la intención al skill de workflow correcto, e invocarlo con los argumentos adecuados.

**No ejecutas el trabajo directamente.** No analizas specs, no generas documentos, no tomas decisiones técnicas.

**No construyes prompts manualmente.** Cada workflow skill sabe cómo delegar a su agente. Tu trabajo es activar el skill correcto con los argumentos correctos.

Las `kb-*` viven en los subagentes y se cargan automáticamente en su contexto. El orquestador no usa las `kb-*` como punto de entrada principal.

## Ámbito de este paquete

Este `CLAUDE.md` describe el ecosistema SDD completo. Es útil como mapa documental o cuando decides instalar **todas** las fases a la vez.

> Para la vista física por responsabilidades (qué es cada directorio, qué se instala vs qué vive solo en el ecosistema), ver «Estructura del repositorio» en `README.md` y el `README.md` de cada directorio top-level.

Si buscas mejor rendimiento y menos carga de contexto, instala y usa el `CLAUDE.md` local de la fase correspondiente:
- `sdd/pipeline/prd/CLAUDE.md`
- `sdd/pipeline/spec/CLAUDE.md`
- `sdd/pipeline/design/CLAUDE.md`
- `sdd/pipeline/plan/CLAUDE.md`
- `sdd/pipeline/tasks/CLAUDE.md` cuando exista

## Rootmap de workflow skills

| Intención del usuario | Skill |
|---|---|
| Crear un PRD desde notas o desde cero | `/wf-prd-create` |
| Revisar si un PRD está limpio y bien planteado | `/wf-prd-review` |
| Formalizar un cambio de producto sobre un PRD existente | `/wf-prd-change` |
| Medir impacto de un cambio de PRD sobre artefactos derivados | `/wf-prd-sync-impact` |
| Propagar un cambio de PRD por todo el pipeline en un solo comando (cascade) | `/wf-prd-change-cascade` |
| Resincronizar specs tras un cambio de PRD | `/wf-spec-sync-from-prd` |
| Analizar un PRD/documento para detectar gaps | `/wf-spec-analyze` |
| Generar specs desde código existente (brownfield, sin PRD) | `/wf-spec-from-code` |
| Validar un spec existente | `/wf-spec-validate` |
| Identificar features de un PRD | `/wf-spec-discover` |
| Generar todos los specs por feature (flujo completo) | `/wf-spec-features-first` |
| Generar specs de un subset / iteración / fase de features | `/wf-spec-features-first` |
| Generar spec directo de una feature | `/wf-spec-fast-track` |
| Generar spec de una feature desde un discovery | `/wf-spec-fast-track` |
| Detectar conflictos entre specs de features | `/wf-spec-conflict` |
| Qué features están listas / orden de implementación | `/wf-spec-readiness` |
| Actualizar un spec con requisitos nuevos (análisis) | `/wf-spec-delta` |
| Aplicar un delta analysis a un spec | `/wf-spec-delta` |
| Completar HUs incompletas (gaps respondidos en analysis) | `/wf-spec-gap-resolve` |
| Aclarar un CA ambiguo descubierto al implementar (back-edge) | `/wf-spec-amend` |
| Dar de baja una feature que el producto deja de contemplar | `/wf-spec-retire` |
| Recuperar una feature que se había dado de baja | `/wf-spec-retire` |
| Cerrar el brief visual y policy de autonomia del producto | `/wf-design-intake` |
| Descubrir apps de referencia con research validado por el usuario | `/wf-design-discover` |
| Crear o actualizar el sistema visual del producto desde un feature spec | `/wf-design-system` |
| Derivar el DESIGN.md de una UI ya en producción (brownfield, sin spec ni brief) | `/wf-design-extract` |
| Auditar un DESIGN.md existente sin regenerarlo | `/wf-design-validate` |
| Analizar cambios sobre un DESIGN.md existente | `/wf-design-delta` |
| Aplicar un delta analysis a un DESIGN.md | `/wf-design-delta` |
| Medir qué artefactos de diseño (flows/views/ui_prompt/tokens) quedaron stale tras un cambio | `/wf-design-sync` |
| Generar flows, views y prompt de ensamblaje para Stitch desde un feature spec | `/wf-design-feature-prototype` |
| Capturar inspiración visual antes del intake (moodboard) | `/wf-design-moodboard` |
| Explorar una variante paralela del DESIGN.md sin comprometer main | `/wf-design-branch` |
| A/B testing visual de una feature concreta | `/wf-design-variant` |
| Exportar tokens del DESIGN.md a CSS, Style Dictionary, Compose, SwiftUI o Tailwind | `/wf-design-export` |
| Auditoría ejecutiva de accesibilidad (contraste, touch targets, focus order) | `/wf-design-a11y-audit` |
| Capturar feedback no estructurado de stakeholders | `/wf-design-feedback` |
| Triajear un feedback capturado en categorías accionables | `/wf-design-feedback` |
| Generar el plan técnico desde un spec | `/wf-prepare-plan` |
| Validar si un plan está listo para pasar a tasks | `/wf-plan-validate` |
| Generar las tasks desde un plan | `/wf-prepare-tasks` |
| Ejecutar tasks con estado y commits trazables | `/wf-task-run` |
| Derivar los casos de prueba de una feature desde sus CAs | `/wf-qa-plan` |
| Verificar la cobertura real de CAs tras implementar | `/wf-qa-verify` |
| Vincular el cierre de una feature (QA APTO) a un commit SHA / tag de release | `/wf-release` |
| Reportar o arreglar un bug de una feature entregada | `/wf-bug` |
| Ver el estado de delivery del proyecto (qué fase y qué falta por feature) | `/wf-project-status` |

> **Este mapa da la intención→skill, no los argumentos ([[D-069]]).** La columna de argumentos que
> había aquí duplicaba a mano el `argument-hint` de cada skill y llevaba tiempo derivando: le
> faltaban flags que sí existen. Los argumentos los arma el orquestador leyendo el frontmatter de la
> skill que invoca, que es la única fuente que no se queda vieja. Mismo criterio que [[D-023]] usó
> para borrar el rootmap de las reglas de fase.

## Cómo actuar ante una petición

1. **Identifica la intención** usando el rootmap anterior
2. **Invoca el skill** con los argumentos correctos
3. **Respeta la fase actual** y sus precondiciones: PRD antes de Spec, Spec antes de Design, Design antes de Plan, Plan antes de Tasks
4. **Reporta al usuario** el resultado y el siguiente paso en el pipeline

Si la intención no coincide exactamente, usa matching semántico con la columna de intenciones. Si hay ambigüedad dentro de una misma fase, delega al agente explorador de esa fase —que diagnostica el estado y recomienda el siguiente paso— antes de cargar fases ajenas.

### Patrón especial — "fase X" / "iteración X" / "subset de features"

Este patrón **solo aplica** cuando el usuario pide explícitamente trabajar por fases, por iteración o sobre un subconjunto de features. No aplica a peticiones generales como "crea las specs", "genera las specs del PRD" o "quiero crear las specs": en esos casos el entrypoint correcto es `/wf-spec-features-first <prd.md>`, no `/wf-spec-discover`.

Las features no se definen en el PRD: las genera `wf-spec-discover`. Por tanto, cuando el usuario menciona "fase 1", "iteración X", "solo estas N features", "primero estas funcionalidades", etc., los IDs `F-XXX` no existen hasta haber ejecutado el discovery.

Proceder así:

1. **Verifica si existe `<basename>_discovery.md`** — en el directorio de artefactos prd (`artifacts.prd` de `.sdd/project-init.json`, si está declarado) o junto al PRD.
2. **Si NO existe** → ejecuta `/wf-spec-discover <prd.md>` primero. Tras la generación, presenta al usuario el mapa de features (Feature ID, nombre, actor, RFs cubiertos) y **pregúntale qué IDs incluir en esta iteración**.
3. **Si SÍ existe** → presenta el mapa actual y pregunta qué IDs incluir.
4. Una vez el usuario confirma los IDs, invoca `/wf-spec-features-first <prd.md> --features F-XXX,F-YYY,...`.

`_features.md` se actualiza de forma incremental entre iteraciones: las features no incluidas quedan marcadas `PENDIENTE_GENERACIÓN` y pueden generarse en pasadas posteriores sin perder lo anterior.

## Agentes SDD disponibles

La unidad primaria de trabajo en SDD es el **agente especializado** cuando la petición no encaja limpiamente en una workflow cerrada.

| Agente | Dominio |
|---|---|
| `prd-expert` | Redacción, reorganización y revisión guiada de PRDs |
| `sdd-spec-explorer` | Exploración, diagnóstico y lectura del estado de artefactos Spec |
| `sdd-spec-writer` | Escritura y evolución de artefactos Spec |
| `sdd-spec-auditor` | Validación, conflictos y readiness de artefactos Spec |
| `design-system-architect` | Autoría del sistema visual del producto (`DESIGN.md`, agnóstico de superficie): brief, sistema, validación, evolución, exportación |
| `design-feature-architect` | Autoría de artefactos por feature (`flows`, `views`, `ui_prompt` — uno por superficie cuando aplica) consumiendo el `DESIGN.md` como contrato de solo-lectura |
| `plan-architect` | Transformación de Spec a Plan técnico |
| `task-generator` | Transformación de Plan a Tasks accionables |
| `qa-engineer` | Derivación de casos de prueba desde CAs y auditoría de cobertura con evidencia ejecutada |

Usa workflows cuando exista una pipeline clara y cerrada. Si no existe una workflow exacta, delega al agente cuyo dominio coincida con la intención real del usuario.

## Flujo del pipeline

```
Requisitos/PRD
    ↓ [/wf-prd-create] (opcional, para redactar `prd.md`)
    ↓ [/wf-prd-review] (opcional, recomendado)
    ↓ [/wf-spec-analyze] (obligatorio)
_analysis.md → [usuario responde gaps o acepta continuar con `--allow-open-critical-gaps`]
    ↓ [/wf-spec-features-first] (orquestador automático con guardrails)
    ↓ — internamente ejecuta:
    ↓   [/wf-spec-discover --analysis _analysis.md]
    ↓   _discovery.md (mapa de features + scope RF→Feature + shared models)
    ↓   [/wf-spec-fast-track --analysis _analysis.md] (en paralelo por feature
    ↓                                                 — todas o solo el subset --features)
    ↓
features/<nombre>/spec/<nombre>_spec.md
_features.md (PROJECT HUB incremental: index + trazabilidad RF→HU→Feature + estado
              incluyendo PENDIENTE_GENERACIÓN para features aún no procesadas)
    ↓ [/wf-spec-conflict]
    ↓ [/wf-spec-readiness]
_readiness_report.md (estado + orden de implementación)
    ↓ [/wf-design-intake generate — cierra brief de producto, gate obligatorio]
DESIGN_BRIEF.md
    ↓ [/wf-design-discover — opcional, research validado por usuario]
features/<nombre>/design/<nombre>_design_discovery.md
    ↓ [/wf-design-system generate — por producto, requiere brief]
DESIGN.md
    ↓ [/wf-design-validate — opcional, audita sin regenerar]
    ↓ [/wf-design-delta — para evoluciones incrementales del DESIGN.md]
    ↓ [/wf-design-feature-prototype generate — por feature, requiere brief y DESIGN.md]
features/<nombre>/design/<nombre>_flows.md
features/<nombre>/design/<nombre>_views.md
features/<nombre>/design/<nombre>_ui_prompt.md
    ↓ [Stitch / validación visual]
    ↓ [/wf-prepare-plan generate — por feature]
features/<nombre>/plan/<nombre>_plan.md
    ↓ [/wf-plan-validate — gate formal]
    ↓ [/wf-prepare-tasks generate — por feature]
features/<nombre>/tasks/<nombre>_tasks.md
    ↓ [/wf-qa-plan generate — deriva TC-XXX trazables desde los CAs; puede ejecutarse desde que el spec es fiable]
features/<nombre>/tasks/<nombre>_qa_plan.md
    ↓ [/wf-task-run — ejecuta cada task con su owner, estado persistente y commit trazable T-00X [CA-XXX]]
    ↓ [/wf-qa-verify — cobertura real de CAs con evidencia ejecutada → veredicto APTO/APTO_CON_RESERVAS/NO_APTO]
features/<nombre>/tasks/<nombre>_qa_report.md
    ↓ [/wf-release — QA APTO → vincula el cierre a commit SHA / tag → features/<nombre>/tasks/<nombre>_release.md]
    ↓ [mantenimiento posterior: /wf-bug — triaje contra CA, registro B-00X en features/<nombre>/tasks/<nombre>_bugs.md]
```

> Layout de feature: cada feature usa subcarpetas por fase (`spec/`, `design/`, `plan/`, `tasks/`; `README.md` en la raíz de la feature). Las features creadas con el layout plano legacy (todo directamente en `features/<nombre>/`) siguen siendo válidas: los workflows leen ambos layouts y no los mezclan dentro de una misma feature.
> Modo iterativo: si el usuario solo quiere un subset (fase 1, iteración X), invocar `wf-spec-features-first` con `--features F-001,F-002,...`. Las no incluidas quedan `PENDIENTE_GENERACIÓN` y se procesan en pasadas posteriores.

> Para una petición general de generar specs desde un PRD, invocar primero `/wf-spec-features-first <prd.md>`. El workflow decidirá si debe generar `_analysis.md`, detenerse por gaps críticos o recomendar subset.
> El analyze es obligatorio. `/wf-spec-features-first` lo ejecuta automáticamente si no existe `_analysis.md`, pero en ese caso se detiene para que el usuario revise el resultado antes de continuar.
> Si el `_analysis.md` mantiene gaps `[CRÍTICO]` pendientes, el orquestador debe pedir decisión explícita: responderlos primero o continuar con `--allow-open-critical-gaps`.
> Si las respuestas del `_analysis.md` introducen expansión de capacidad (entidad persistente nueva, catálogo reutilizable, nueva granularidad funcional, modelo owner nuevo o flujo adicional no comprometido), no continúes a discovery/specs: primero `wf-prd-change`, salvo override explícito con `--allow-derived-scope-from-analysis`.
> Si excepcionalmente se continúa con `--allow-derived-scope-from-analysis`, los derivados deben marcar `Origen de alcance: PRD + analysis respondido` y `Avisos de gobernanza`.
> Si el discovery identifica más de 5 features y el usuario no ha pedido un subset, el flujo recomendado es iterar con `--features ...`. Solo usar `--all-features` como override explícito.
> Para cambios post-spec: `/wf-spec-delta analyze <spec.md> --new-reqs <cambios.md>`
> Para completar HUs `[INCOMPLETO]` con respuestas ya escritas en `_analysis.md`: `/wf-spec-gap-resolve <spec.md>`
> La fase Design es **saltable por feature**: si la feature no tiene superficie de UI visible, Spec pasa a Plan directamente (la regla canónica de cuándo Design es obligatorio vive en `kb-plan-expert` y la aplica `wf-prepare-plan`). Su fit declarado (greenfield sin diseñador, Stitch; y, desde D-011, también equipos con diseño dedicado / escala multi-repo vía topología `design`; no cubre Figma) vive en `design/CLAUDE.md`.
> Onramp brownfield de Design (espejo de `/wf-spec-from-code` en Spec): si la UI **ya existe en producción** y no se va a rediseñar, deriva el `DESIGN.md` por ingeniería inversa con `/wf-design-extract` (CSS/tokens/componentes/capturas → `DESIGN.md` con `origin: extracted` y evidencia por token; `discover` se detiene en un gate humano antes de generar). No exige spec validado ni `DESIGN_BRIEF.md`: es entrada alternativa a la fase. El `DESIGN.md` extraído luego se audita (`wf-design-validate`), evoluciona (`wf-design-delta`) y exporta (`wf-design-export`) como cualquier otro.
> Para prototipado visual desde Specs listos: primero `/wf-design-intake generate <feature_spec.md>` (gate obligatorio), luego opcionalmente `/wf-design-discover`, después `/wf-design-system generate <feature_spec.md> --brief DESIGN_BRIEF.md` y finalmente `/wf-design-feature-prototype generate <feature_spec.md> --brief DESIGN_BRIEF.md`.
> Para auditar un `DESIGN.md` editado manualmente: `/wf-design-validate <DESIGN.md>`.
> Para cambios incrementales en `DESIGN.md`: `/wf-design-delta analyze <DESIGN.md> --new-reqs <cambios.md>`.
> Tras un cambio de `DESIGN.md`, brief o spec, para saber qué flows/views/ui_prompt/tokens quedaron stale: `/wf-design-sync <DESIGN.md>` (análisis de impacto de la fase Design, réplica de `wf-prd-sync-impact`).
> En la salida de Design: `flows` = secuencias y transiciones; `views` = SSoT de pantallas y estados visuales; `ui_prompt` = ensamblaje para Stitch.
> Para pasar de Plan a Tasks: `/wf-prepare-plan generate <feature_spec.md>` → `/wf-plan-validate <feature_plan.md>` → `/wf-prepare-tasks generate <feature_plan.md>`.
> Para cambios de producto (scope, prioridad, exclusiones): primero `/wf-prd-change`, luego `/wf-prd-sync-impact` y `/wf-spec-sync-from-prd`. Para encadenar toda esa cascada en un solo comando, **preguntando** en los cuatro checkpoints humanos (clasificación del cambio, features con cambio no trivial, decisiones de diseño, revalidación de plan): `/wf-prd-change-cascade <prd.md> --new-reqs <cambio.md>` — corre en el hilo principal y los sostiene con `AskUserQuestion` ([[D-075]]). Auto-aplica los deltas de spec inequívocos (`minor`) y avisa de que esos specs quedan en `BORRADOR`; `--review-before-apply` restaura la parada conservadora antes de cualquier escritura; `--dry-run` solo diagnostica.
> Tras `/wf-prepare-tasks`, la ejecución es `/wf-task-run <tasks.md>`: delega cada task a su `Owner agent` (agentes del overlay de stack, u orquestador en modo genérico), con estado persistente gestionado por `sdd-task-state.py` y un commit por task.
> Para bugs sobre features ya entregadas: `/wf-bug <descripción>` — triaje contra el CA del spec; solo escala a `/wf-spec-delta` si el comportamiento esperado cambia.
> Para un CA ambiguo descubierto DURANTE la implementación (back-edge tasks→spec): `/wf-spec-amend <spec.md> --ca CA-XXX --from-task T-00X` — aclaración quirúrgica sin re-descender el waterfall. El plan se marca con `Enmienda pendiente` (solo lo escribe `sdd-amend.py`) y solo quedan retenidas las tasks que referencian ese CA; si el comportamiento esperado cambia, no es enmienda: es `/wf-spec-delta`.
> Para cerrar el ciclo QA: `/wf-qa-plan generate <spec.md>` (matriz TC-XXX desde los CAs, gate de spec fiable) y, tras implementar, `/wf-qa-verify <qa_plan.md>` (cobertura con evidencia ejecutada; un test que falla contra un CA es DIVERGENTE → `/wf-bug`, nunca se ajusta el TC).
> Para llevar la trazabilidad a producción: `/wf-release <feature_dir> [--tag <tag>]` — solo acepta features con QA `APTO`/`APTO_CON_RESERVAS` (gate determinista), captura el commit SHA con git (no se teclea) y registra la coordenada en `<feature>_release.md`. Es el último eslabón de la cadena CA→TC→task→commit→release (SSoT en `kb-traceability-rules` Regla 11). `wf-project-status` muestra la release en la fila de la feature cerrada.

## Principio de precondiciones

Los workflow skills tienen sus propias validaciones de precondición. **No las bypasses.** Si un skill reporta bloqueos o pendientes, comunícalos al usuario y espera a que los resuelva antes de reintentar.

## Principio de autonomía por capas

El pipeline opera en tres capas:

- **Capa orquestador (tú)**: mapeas intención → workflow o agente. No prescribes lógica interna.
- **Capa workflow (`wf-*`)**: cuando existe una pipeline cerrada, recoge requisitos, verifica precondiciones y delega al agente especializado.
- **Capa agente SDD**: explora, planifica, escribe o audita con sus knowledge skills cargadas en contexto.

Cada capa es responsable de su nivel de decisión. Si existe workflow, la activas. Si no existe workflow y la petición es claramente de exploración, planificación, escritura o auditoría SDD, eliges el agente especializado correspondiente.
