# SDD Spec — Etapas 1 y 2: Specify y Decompose

Este directorio contiene todos los agentes y skills que transforman un documento de requisitos en Specs SDD válidos y autocontenidos por feature. Cubre las dos primeras etapas del pipeline Spec Driven Development: **Specify** (del PRD al Spec monolítico) y **Decompose** (del Spec monolítico a Specs por feature).

Diagramas detallados de esta fase: [DIAGRAMS.md](DIAGRAMS.md).

## Precondición de esta fase

La fase `spec` **no arranca desde cero**. Requiere un PRD o documento de requisitos previo, normalmente salido de `sdd/prd`.

Si todavía no existe ese artefacto, hay que volver a la fase anterior y usar `wf-prd-create` o `wf-prd-review`. Esta fase no debe depender de la fase PRD completa, pero sí instala los handoffs mínimos cross-fase que necesita (`wf-prd-review`, `wf-prd-change`, `prd-expert` y sus kb).

**Excepción brownfield.** Si el sistema **ya existe** y no hay PRD que lo describa, la fase tiene una segunda entrada: `wf-spec-from-code` (caso 2.b), donde la fuente de verdad es el código y el producto son specs de **caracterización**. No exige PRD, ni `analyze`, ni discovery de PRD.

---

## Casos de uso

### 1. Proyecto nuevo (Greenfield) — flujo completo

Tienes un PRD o documento de requisitos y quieres convertirlo en Specs SDD para todo el producto de una vez.

```
/wf-spec-analyze prd.md
  → genera prd_analysis.md con:
      · mapa de elementos del Spec que se generarán desde el PRD (informativo)
      · pureza del PRD (contaminación técnica si la hay)
      · gaps [CRÍTICO] e [INFORMATIVO] para responder
      · marcador `[PUEDE_REQUERIR_CR]` cuando una futura respuesta puede expandir el producto
  → veredicto: LISTO_PARA_SPECS | LISTO_PARA_SPECS_CON_PREGUNTAS | REQUIERE_LIMPIEZA_PRD
  Las respuestas a gaps se anotan en el `_analysis.md`. Si aparece un cambio real de producto, se formaliza con `wf-prd-change` antes de resincronizar derivados.

[si el análisis deja gaps [CRÍTICO], decide:]
  a) responderlos en prd_analysis.md
  b) continuar igualmente aceptando HUs [INCOMPLETO]

/wf-spec-features-first prd.md
  → si faltaba `prd_analysis.md`, lo genera y te lo presenta antes de seguir
  → si quedan gaps [CRÍTICO], te pregunta: responderlos primero o continuar aceptando HUs [INCOMPLETO]
  → si las respuestas del analysis introducen expansión de capacidad, te pregunta: formalizar el cambio con `wf-prd-change` o continuar con alcance derivado
  → si el discovery detecta más de 5 features, te pregunta el alcance de la pasada (subset o todas)
  → los gates se resuelven en el momento; no hay que relanzar el flujo con flags
  → ejecuta discover + fast-track por feature en paralelo
  → genera prd_discovery.md, prd_features.md
  → genera features/<nombre>/spec/<nombre>_spec.md por cada feature
  → ejecuta verificación de conflictos y readiness automáticamente
```

**Cuándo usarlo**: cuando tienes un PRD acotado y quieres procesar todas las features en una sola pasada. Si el discovery saca muchas features, el propio workflow te empuja a iterar por subset para controlar coste y contexto.

---

### 1.b. Proyecto nuevo (Greenfield) — iterativo por fases / subset

Tienes un PRD que cubre todo el producto pero solo quieres generar las specs de un subconjunto de features (por ejemplo, "fase 1" o "iteración inicial"). Las features no se definen en el PRD: se identifican en el discovery, así que primero hay que ejecutarlo y luego elegir el subset.

```
/wf-spec-analyze prd.md
  → genera prd_analysis.md (igual que en el caso 1)

[responde gaps [CRÍTICO] o decide continuar luego con `--allow-open-critical-gaps`]

/wf-spec-discover prd.md --analysis prd_analysis.md
  → genera prd_discovery.md con el mapa completo de features (F-001..F-N)

# Si el analysis contiene respuestas expansivas y se decide continuar
# excepcionalmente con alcance derivado:
# /wf-spec-discover prd.md --analysis prd_analysis.md --allow-derived-scope-from-analysis

[revisa el mapa y elige qué Feature IDs entran en esta iteración]

/wf-spec-features-first prd.md --features F-001,F-002,F-003
  → genera specs solo para las features indicadas
  → prd_features.md indexa TODAS las features:
      · las generadas en esta iteración → LISTA / BLOQUEADA / REQUIERE_CAMBIO_PRD
      · las que aún no se han procesado → PENDIENTE_GENERACIÓN
      · las que el producto dio de baja → RETIRADA
  → conflict + readiness se ejecutan sobre el subset

# Más adelante, cuando quieras la siguiente fase:
/wf-spec-features-first prd.md --features F-004,F-005
  → añade specs sin tocar los anteriores
  → prd_features.md se actualiza incrementalmente
```

**Cuándo usarlo**: cuando el PRD describe un producto amplio pero el delivery va por fases. Permite priorizar features sin tener que rehacer el PRD ni perder la visión global del producto.

**Recomendación operativa**: para PRDs con más de 5 features, este modo iterativo pasa a ser el camino por defecto. El modo full queda como override explícito con `--all-features`.

**Nota de gobernanza**: si una respuesta en `_analysis.md` añade una entidad persistente, un catálogo reutilizable, una nueva granularidad funcional, un nuevo modelo owner o un flujo adicional no comprometido en el PRD, no debe derivarse directamente a specs. Primero hay que formalizarlo con `wf-prd-change`. Si excepcionalmente se continúa con `--allow-derived-scope-from-analysis`, los derivados deben marcar `Origen de alcance: PRD + analysis respondido` y dejar `Avisos de gobernanza`.

---

### 2. Feature única sin spec previo (Fast-Track)

Quieres documentar solo una capacidad concreta sin pasar por el spec monolítico. Útil para añadir features a proyectos maduros o arrancar documentando una sola área.

```
/wf-spec-fast-track notifications.md --capability push-notifications
  → genera features/push-notifications/spec/push-notifications_spec.md directamente
```

**Cuándo usarlo**: cuando el documento de entrada ya describe una sola capacidad acotada y no necesitas documentar el sistema completo. El spec resultante puede tener `## Items Pendientes` si hay gaps críticos, y `## Asunciones Aplicadas` si se resolvieron gaps informativos con asunciones razonables.

---

### 2.b. Sistema existente sin PRD (Brownfield) — specs de caracterización

No hay PRD y el software ya está en producción. La fuente de verdad es el código, y el spec no describe lo que el sistema *debería* hacer sino lo que **hace hoy**, con evidencia por criterio.

```
/wf-spec-from-code discover backend/ --scope src/billing
  → explora entrypoints, tests, modelos persistentes y permisos
  → genera <scope>_code_discovery.md: capacidades F-C-00X con actor, superficie,
    punteros de evidencia y nota de confianza (alta / media / baja)
  → SE DETIENE SIEMPRE: el mapa lo valida un humano antes de generar ningún spec

[confirmas, corriges o descartas capacidades — las descartadas se marcan, no se borran]

/wf-spec-from-code generate backend/ --feature F-C-001
  → genera features/<nombre>/spec/<nombre>_spec.md con Origen: characterization
  → cada CA lleva su campo Evidencia (archivo:línea, test::nombre)
  → lo que no se observó directamente entra como CA [INFERIDO]
  → lo que parece un defecto se documenta tal cual + [SOSPECHA_BUG]

/wf-spec-gap-resolve features/<nombre>/spec/<nombre>_spec.md
  → confirma los [INFERIDO] uno a uno; eso es lo que desbloquea el spec
```

**Cuándo usarlo**: para documentar un legacy antes de tocarlo, o para dar entrada al pipeline a un sistema que nunca tuvo PRD. La regla que gobierna estos specs vive en `kb-spec-characterization`: **un CA sin evidencia no existe**.

**Cuándo NO**: si existe un PRD, la entrada es `wf-spec-features-first` (casos 1 y 1.b). Y si lo que quieres es **cambiar** el comportamiento, no documentarlo, eso es `wf-spec-delta` sobre el spec de caracterización ya generado.

**Bloqueo**: los `[INFERIDO]` se tratan como `[INCOMPLETO]` y bloquean `wf-prepare-plan` hasta confirmarse.

---

### 3. Evolución incremental de un spec existente (Delta)

El software ya existe, hay un `_spec.md` en producción y quieres añadir o modificar una funcionalidad sin regenerar todo.

```
/wf-spec-delta analyze features/auth/spec/auth_spec.md --new-reqs new_auth_requirements.md
  → genera features/auth/spec/auth_delta_analysis.md con HUs/CAs añadidos, modificados, eliminados
  → si el cambio redefine alcance del producto, te pregunta antes: formalizarlo en el PRD o
    tratarlo como delta de esta feature
  → si el requisito admite varias lecturas, te las presenta; "no lo decido ahora" deja un gap
    [D-XXX] con las opciones dentro, en vez de elegir por ti

[revisa el delta, responde gaps [CRÍTICO]]

/wf-spec-delta apply features/auth/spec/auth_spec.md features/auth/spec/auth_delta_analysis.md
  → si quedan gaps [CRÍTICO] sin responder, te pregunta: responderlos primero o aplicar aceptando
    HUs [INCOMPLETO] (que bloquearán el plan)
  → actualiza auth_spec.md (versión 1.0 → 1.1) con sección Changelog y reabre su validación
```

**Cuándo usarlo**: cuando el spec ya existe y el cambio es incremental (nueva HU, modificación de un comportamiento, eliminación de una funcionalidad deprecada). El delta es quirúrgico: no toca lo que no cambia.

#### Completar HUs incompletas (resolver gaps pendientes)

Si el spec tiene HUs marcadas `[INCOMPLETO]` por gaps `[CRÍTICO]` sin responder:

```
[responde los gaps [P-XXX] en el _analysis.md]

/wf-spec-gap-resolve features/auth/spec/auth_spec.md
  → auto-descubre el _analysis.md, integra respuestas, completa HUs y CAs, versión 1.0 → 1.1
```

**Cuándo usarlo**: después de generar un feature spec que dejó HUs incompletas por gaps sin responder. El usuario responde los gaps en el `_analysis.md` y `wf-spec-gap-resolve` integra las respuestas en el feature spec.

#### CA ambiguo descubierto al implementar (back-edge tasks→spec)

Si durante `wf-task-run` el dev descubre que un CA admite varias implementaciones y el texto no determina cuál:

```
/wf-spec-amend features/auth/spec/auth_spec.md --ca CA-003 --from-task T-004
  → gate de clasificación (¿aclaración o cambio de comportamiento?), confirmación humana,
    edición quirúrgica del CA con changelog E-00X, anotación `Enmienda pendiente` en el plan
    (solo retiene las tasks que referencian ese CA — el resto sigue ejecutable)
```

**Cuándo usarlo**: solo para ACLARACIONES estrictas (la intención del CA no cambia; el texto era ambiguo). Si el comportamiento esperado cambia, la vía es `/wf-spec-delta`; si la divergencia es sobre código ya entregado, `/wf-bug`.

#### Cambio de producto tras entrar en Spec

Si la "respuesta" realmente cambia el alcance o el roadmap del producto:

```
/wf-prd-change prd.md --new-reqs cambio.md
  → actualiza el PRD, registra el cambio y deja trazabilidad

/wf-prd-sync-impact prd.md
  → detecta qué discovery/specs/planes/tasks quedaron afectados

/wf-spec-sync-from-prd analyze prd.md
  → genera requisitos de sync por feature

/wf-spec-sync-from-prd apply prd.md --features F-001,F-003
  → resincroniza los specs afectados
```

**Cuándo usarlo**: cuando el producto vigente cambia de verdad, por ejemplo mover una capacidad de fase 2 a MVP.

#### El producto retira una capacidad (dar de baja una feature)

Si el cambio no mueve una capacidad sino que la **saca del producto**, sus specs no se resincronizan: se dan de baja. No hay con qué poner al día un spec cuyo referente desapareció, y regenerarlo lo volvería a escribir.

```
/wf-prd-change prd.md --new-reqs retirada.md
  → clasificación DEPRECATION confirmada en su gate; el change-request nombra
    las features afectadas

/wf-spec-retire features/pagos/spec/pagos_spec.md --change CR-007 --reason "..."
  → audita quién depende de la feature: shared models que posee, features que la
    declaran dependencia, conflictos abiertos y artefactos ya generados
  → te presenta ese impacto y te pregunta; si hay release, te dice que el código
    sigue entregado y que darlo de baja aquí no lo retira
  → sella el spec `Estado: RETIRADO` + `Retirada: CR-007 — <razón> (<fecha>)`
  → degrada el plan a BORRADOR y regenera el índice: la feature pasa a RETIRADA
```

**Qué cambia a partir de ahí**: readiness la saca del orden de implementación, el estado del proyecto deja de pedir trabajo sobre ella, y los gates deniegan planificarla, generarle tareas o ejecutarlas. Su `F-00X` **se conserva y no se reutiliza** (`kb-traceability-rules` Regla 12): la siguiente feature toma el siguiente número libre, no el hueco.

**Cuándo NO**: si la capacidad solo se pospone a una fase futura, **no** se retira — sigue comprometida, y eso es un cambio de prioridad. Y si lo que desaparece es una HU o un CA concretos dentro de una feature que sigue viva, eso es `wf-spec-delta`, que los marca como tombstone.

**Si la decisión cambia**:

```
/wf-spec-retire reactivate features/pagos/spec/pagos_spec.md
  → el spec vuelve a BORRADOR y se retira la traza `Retirada:`
  → el índice deja de marcarla RETIRADA y los gates vuelven a dejarla pasar
```

No lleva gate: es la dirección segura, no destruye nada. Lo que **no** restaura es el sello — ni el del spec ni el del plan, que sigue en `BORRADOR` desde la baja: los dos hay que validarlos otra vez. Y si el PRD sigue sin contemplar la capacidad, el spec reactivado **contradice al PRD vigente**: reactivar un spec no reactiva la decisión de producto.

---

### 4. Validar un spec tras edición manual

Editas manualmente un `_spec.md` y quieres verificar que no introdujiste contaminación técnica ni rompiste la estructura SDD.

```
/wf-spec-validate features/auth/spec/auth_spec.md
  → audita el spec (pureza, testabilidad, completitud) y presenta el informe
  → veredicto APROBADO / REQUIERE_REVISIÓN
  → si aprueba, te pregunta quién lo aprueba y sella el estado operativo del spec
    (`Estado: VALIDADO`, `Aprobado por: <nombre> (<fecha>)`) — el sello lo estampa el
    script, no el informe
```

**Cuándo usarlo**: después de cualquier edición manual a un spec. También como gate antes de planificar: el sello es lo que deja constancia de **quién** dio por bueno el spec, y a partir de ahí regenerarlo exige `--allow-overwrite-sealed-spec`.

---

### 5. Detectar conflictos entre specs de features

Quieres verificar que los specs de las diferentes features del proyecto son coherentes entre sí: sin HUs duplicadas, CAs contradictorios ni scope overlap.

```
/wf-spec-conflict features/auth/spec/auth_spec.md --features-dir features/
  → genera features/auth/spec/auth_conflict_report.md si hay conflictos
```

**Cuándo usarlo**: después de modificar un spec existente o añadir una nueva feature con fast-track o delta, para verificar que el cambio no choca con el resto del sistema. También se ejecuta automáticamente al final de `/wf-spec-features-first` (modo no bloqueante).

---

### 6. Exploración o diagnóstico de artefactos Spec

Quieres entender el estado actual de un PRD, de un spec o de un conjunto de artefactos antes de decidir el siguiente paso.

```
sdd-spec-explorer
  → diagnostica el estado
  → identifica gaps, contaminación o ambigüedad de scope
  → recomienda workflow o agente siguiente
```

**Cuándo usarlo**: cuando la duda principal es “qué tengo delante” o “qué workflow corresponde ahora” — incluida la petición ambigua que mezcla varias intenciones (crear, evolucionar, auditar) y hay que separarlas antes de ejecutar nada.

---

### 7. Consulta directa sobre qué es un Spec SDD

Preguntas conceptuales o revisión de un spec a mano, sin pasar por el flujo orquestado.

```
sdd-spec-explorer
```

**Cuándo usarlo**: para aprender, revisar o depurar specs directamente en conversación, sin invocar el pipeline completo.

---

## Mapa de componentes

La fase `spec` se apoya en tres tipos de piezas:

- `wf-*`: puntos de entrada operativos. Parsean argumentos, validan precondiciones y delegan el trabajo.
- agentes: workers especializados por tipo de razonamiento (`explorer` diagnostica, `writer` escribe, `auditor` verifica).
- `kb-*`: conocimiento de fondo cargado por los agentes como contexto reusable.

La lógica exacta de routing y la política de skills viven en [CLAUDE.md](CLAUDE.md). Este README mantiene solo el mapa funcional de la fase.

### Workflows

| Skill | Comando | Produce |
|-------|---------|---------|
| `wf-spec-analyze` | `/wf-spec-analyze` | `_analysis.md` (mapa Spec, pureza del PRD, gaps de negocio) |
| `wf-spec-validate` | `/wf-spec-validate` | Informe de auditoría inline + sello del estado operativo en el propio spec (`Estado:`, `Aprobado por:`) |
| `wf-spec-features-first` | `/wf-spec-features-first [--features F-XXX,...] [--allow-open-critical-gaps] [--allow-derived-scope-from-analysis] [--all-features]` | `_discovery.md`, `_features.md` (Project Hub incremental con estados canónicos y trazabilidad de gobernanza), `features/<x>/spec/<x>_spec.md` |
| `wf-spec-discover` | `/wf-spec-discover [--analysis <analysis.md>] [--allow-derived-scope-from-analysis]` | `_discovery.md` con mapa de features y metadata de gobernanza |
| `wf-spec-fast-track` | `/wf-spec-fast-track` | `features/<x>/spec/<x>_spec.md` directamente, con marca de origen de alcance si aplica |
| `wf-spec-from-code` | `/wf-spec-from-code discover \| generate` | `_code_discovery.md` (mapa de capacidades con evidencia) y specs de caracterización `F-C-00X` |
| `wf-spec-conflict` | `/wf-spec-conflict` | `_conflict_report.md` |
| `wf-spec-delta` | `/wf-spec-delta` | `_delta_analysis.md` (analyze), spec actualizado (apply) |
| `wf-spec-gap-resolve` | `/wf-spec-gap-resolve` | spec actualizado desde `_analysis.md` |
| `wf-spec-retire` | `/wf-spec-retire --change CR-XXX \| reactivate` | Spec sellado `Estado: RETIRADO` + `Retirada: CR-XXX`; el índice pasa la feature a `RETIRADA`. El modo `reactivate` lo deshace, devolviéndolo a `BORRADOR` |
| `wf-spec-amend` | `/wf-spec-amend --ca CA-XXX [--from-task T-00X]` | CA aclarado con changelog `E-00X`, anotación `Enmienda pendiente` en el `_plan.md` (vía `sdd-amend.py`) |
| `wf-prd-change` | `/wf-prd-change` | PRD actualizado, `product-changelog.md`, `changes/CR-XXX/change-request.md`, `changes/CR-XXX/decision.md` |
| `wf-prd-sync-impact` | `/wf-prd-sync-impact` | `_sync_report.md` |
| `wf-spec-sync-from-prd` | `/wf-spec-sync-from-prd` | `*_sync_requirements.md`, specs resincronizados |
| `wf-spec-readiness` | `/wf-spec-readiness` | `_readiness_report.md`, actualiza estado en `_features.md` |

### Agentes

| Agente | Qué razona | Quién lo invoca |
|--------|------------|-----------------|
| `sdd-spec-explorer` | diagnóstico de PRD/spec, análisis de gaps, discovery | los `wf-*` que **diagnostican** antes de tocar nada, y la exploración directa en conversación |
| `sdd-spec-writer` | fast-track, delta, sync desde PRD, caracterización desde código, resolución de gaps | los `wf-*` que **escriben o evolucionan** un artefacto de Spec |
| `sdd-spec-auditor` | validate, conflict, readiness, sync impact, impacto de una baja | los `wf-*` que **verifican lo que otro escribió** (autor≠verificador, [[D-059]]) |

> **El binding exacto no se lista aquí ([[D-069]]).** Un `wf-*` que corre en fork lo declara en su
> `agent:`; uno que corre en el hilo principal, en el `subagent_type` de cada delegación. Enumerarlo
> en este README era una tercera copia del mismo dato, y derivó: se quedó sin
> `wf-spec-features-first` —que invoca a los tres— en las filas del explorer y del auditor.

### Knowledge bases

| Skill | Qué aporta |
|-------|------------|
| `kb-spec-expert` | Conocimiento SDD: los 8 elementos, la Prueba de Pureza, la testabilidad |
| `kb-decompose-expert` | Partición en features, shared models, ownership y el índice `_features.md` |
| `kb-conflict-expert` | Las 5 reglas de detección de conflictos entre specs |
| `kb-gap-conventions` | SSoT de gaps y marcadores: formatos de ID, severidades y reglas de bloqueo |
| `kb-traceability-rules` | Trazabilidad PRD → spec → plan → tasks y estados de sincronización |
| `kb-spec-characterization` | Specs brownfield: evidencia obligatoria por CA, `[INFERIDO]`, `[SOSPECHA_BUG]` |
| `kb-prd-expert` ⚠ | Reglas del PRD, para leer con criterio el documento de entrada |
| `kb-product-change-governance` ⚠ | Gap vs. change request, e impacto de negocio de una respuesta |

> **Quién carga cada una no se enumera aquí ([[D-069]]).** Una `kb-*` la carga el **agente**, no el
> workflow: vive en su frontmatter `skills: [...]` y el harness la inyecta en el contexto del
> subagente. Una columna "usado en modos" en este README es una tercera copia de ese dato, y además
> finge una precisión que el mecanismo no tiene —el agente entra con todas sus KBs cargadas, ejecute
> el modo que ejecute—. Derivó como era de esperar: en la revisión de v0.107.0, **seis de sus ocho
> filas** ya no coincidían con el árbol. El reparto real se lee en los tres `agents/*.md`, y
> `sdd-kb-check.py` verifica que ningún agente enumere una lista parcial.

> ⚠ `kb-prd-expert` y `kb-product-change-governance` viven físicamente en `sdd/pipeline/prd/skills/`: son kb cross-fase.
>
> **`install.sh spec` ya instala automáticamente estas dos kb cross-fase y también `wf-prd-change`, `wf-prd-review` + `prd-expert`,** porque el ecosistema Spec necesita ese handoff cuando una respuesta a un gap se convierte en cambio real de producto o cuando el analyze exige limpiar el PRD antes de continuar.

---

## Artefactos producidos

```
proyecto/
├── prd.md                                    ← Input
├── prd_analysis.md                           ← /wf-spec-analyze (recomendado)
├── prd_discovery.md                          ← /wf-spec-discover
├── <scope>_code_discovery.md                 ← /wf-spec-from-code discover (brownfield)
├── prd_features.md                           ← /wf-spec-features-first — PROJECT HUB (index + trazabilidad + estado)
├── prd_sync_report.md                        ← /wf-prd-sync-impact
├── prd_conflict_report.md                    ← /wf-spec-features-first (automático) o /wf-spec-conflict
├── prd_readiness_report.md                   ← /wf-spec-readiness
└── features/
    └── <nombre-feature>/
        ├── README.md                         ← /wf-spec-fast-track
        ├── spec/
        │   ├── <nombre>_spec.md              ← /wf-spec-fast-track
        │   ├── <nombre>_delta_analysis.md    ← /wf-spec-delta analyze
        │   ├── <nombre>_sync_requirements.md ← /wf-spec-sync-from-prd analyze
        │   └── <nombre>_conflict_report.md   ← /wf-spec-conflict
        ├── design/                           ← etapa Design (flows, views, ui_prompt)
        ├── plan/
        │   └── <nombre>_plan.md              ← /wf-prepare-plan (etapa siguiente)
        └── tasks/
            └── <nombre>_tasks.md             ← /wf-prepare-tasks (etapa siguiente)
```

> Features creadas con el layout plano legacy (todos los artefactos directamente en `features/<nombre>/`) siguen siendo válidas: los workflows leen ambos layouts y no los mezclan dentro de una misma feature.

---

## Checkpoints humanos

El pipeline nunca es completamente automático. Estos son los momentos donde el humano debe intervenir:

| Momento | Qué hacer | Bloquea si no se hace |
|---------|-----------|-----------------------|
| Tras `analyze` | Responder gaps `[CRÍTICO]` con `_(pendiente)_` en `_analysis.md` (en el propio archivo, no en el PRD) | No bloquea generación de specs, pero las HUs afectadas quedan `[INCOMPLETO]` y bloquean `prepare-plan` |
| Tras `analyze` o validación con cliente | Si la respuesta cambia el alcance o el roadmap, ejecutar `wf-prd-change` antes de seguir | Sí — evita derivar specs desde una verdad de negocio obsoleta |
| Tras `analyze` | Responder gaps `[INFORMATIVO]` con `_(pendiente)_` (opcional) | No — se aplican asunciones por defecto |
| Tras `analyze` con veredicto `REQUIERE_LIMPIEZA_PRD` | Aplicar las reescrituras de la sección Pureza al PRD y volver a ejecutar `/wf-spec-analyze` | Sí — único caso en que se toca el PRD por contaminación técnica dentro del analyze |
| Tras `discover` (modo iterativo) | Elegir los Feature IDs que entran en la próxima iteración | Sí — `wf-spec-features-first --features` los necesita |
| Tras `features-first` | Revisar `_features.md` y validar la partición de features | No — pero afecta la calidad del plan |
| Tras `features-first` | Revisar `_conflict_report.md` si hay conflictos `ALTA` | No — pero pueden propagarse problemas al plan |
| Al dar de baja una feature | Confirmar la baja con el impacto delante: qué artefactos derivados quedan sin origen y qué otras features se quedan sin el shared model que esta poseía | Sí — es la única vía: no hay override, y sin confirmación no se retira nada |
| Tras `validate` con veredicto `APROBADO` | Dar el nombre de quien aprueba: el sellador lo estampa en la cabecera (`Estado: VALIDADO`, `Aprobado por:`) | No — pero el spec se queda sin constancia de quién lo dio por bueno y sin la protección que obliga a `--allow-overwrite-sealed-spec` para regenerarlo |
| Tras `wf-prd-sync-impact` | Revisar artefactos `stale` o `needs_review` y decidir qué features resincronizar | Sí — bloquea avanzar con specs desalineados |
| Durante `delta analyze` | Decidir si el cambio es de producto (va antes al PRD) y, si el requisito es ambiguo, cuál es la lectura | Sí — sin decisión, la ambigüedad se marca como gap `[D-XXX]` y el delta no la resuelve |
| Tras `delta analyze` | Responder gaps `[CRÍTICO]` con `_(pendiente)_` en `_delta_analysis.md` | Sí — `delta apply` pregunta antes de seguir, y aplicar igualmente deja HUs `[INCOMPLETO]` que bloquean `prepare-plan` |
| Tras `from-code discover` | Confirmar, corregir o descartar las capacidades del `_code_discovery.md` | Sí — `generate --feature` no arranca sin ese mapa validado |
| Tras `from-code generate` | Confirmar los CAs `[INFERIDO]` uno a uno (vía `wf-spec-gap-resolve`) y decidir qué hacer con los `[SOSPECHA_BUG]` | Sí — los `[INFERIDO]` bloquean `prepare-plan` igual que un `[INCOMPLETO]` |

---

## Estructura de directorios

La fase se organiza en las tres piezas del mapa de componentes: `agents/` (los tres workers),
`skills/` (las `wf-*` y las `kb-*` de la fase) y `shared/templates/`. Junto a este README están
`CLAUDE.md` (orquestador local), [routing.md](routing.md) (precondiciones, desambiguación y
fronteras) y [DIAGRAMS.md](DIAGRAMS.md).

> El listado exacto de ficheros **no se copia aquí**: un árbol mantenido a mano duplica lo que
> `ls` ya dice y deriva en silencio en cuanto se añade o se retira una pieza (precedente:
> [[D-023]]). Lo que este README mantiene es el mapa funcional — qué existe y para qué —, no el
> inventario.

---

## Cómo extender el sistema

Para añadir un nuevo modo al pipeline:

1. **Decide antes que nada dónde corre** ([[D-045]], [[D-070]]). ¿El modo necesita una decisión del
   usuario en algún punto — clasificar, elegir entre lecturas, confirmar algo irreversible, registrar
   quién aprueba?
   - **Sí** → va en el **hilo principal**: sin `context: fork`, con `AskUserQuestion` en
     `allowed-tools`, y el trabajo se **delega** con la tool `Agent` al agente que toque. Un fork no
     tiene turno: un gate escrito ahí dentro no se presenta, se decide solo — y el artefacto sale
     con pinta de correcto, así que nadie se entera.
   - **No** → es un worker `context: fork` con su `agent:` especializado (`sdd-spec-explorer`
     diagnostica, `sdd-spec-writer` escribe, `sdd-spec-auditor` verifica). Un worker **no delega**:
     ya *es* su agente, y invocarlo forkearía un clon suyo ([[D-044]]). Si en ejecución aparece una
     decisión humana, para con un veredicto `STOP_*` y deja que la presente quien te invocó ([[D-064]]).
2. **Escribe el workflow** en `skills/wf-spec-<nombre>/SKILL.md`: ahí van las instrucciones paso a paso.
3. **Crea o reutiliza una `kb-*`** solo si el modo necesita reglas transversales reutilizables por varios workflows o agentes.
4. **Registra el knowledge en el agente correcto**: añádelo al frontmatter `skills: [...]` y documenta su responsabilidad.
5. **Registra en `CLAUDE.md` y en este README** solo los entrypoints y handoffs que cambien el mapa funcional de la fase.

La política transversal para diseñar skills y agentes no vive ya en este README. Debe mantenerse como SSoT fuera de la fase, para evitar que `spec` replique reglas globales de frontmatter o arquitectura.
