---
name: wf-spec-sync-from-prd
description: "Resincroniza specs de feature tras un PRD actualizado. Modo analyze: identifica features afectadas y genera requisitos de sincronizacion por feature; modo apply: integra esos cambios via delta sobre los specs afectados y actualiza su trazabilidad."
when_to_use: "Activa en frases como 'sincroniza los specs con el PRD', 'aplica el cambio de PRD a las features', 'que specs tengo que actualizar tras cambiar el PRD', 'resincroniza specs desde el PRD'. **Aplica** el cambio sobre los specs. Si solo se quiere saber qué quedó stale sin tocar nada, es wf-prd-sync-impact."
argument-hint: "analyze <prd.md> | apply <prd.md> --features F-001,F-002,..."
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-writer
user-invocable: true
---

# Workflow: SPEC-SYNC-FROM-PRD

Tu objetivo es propagar un cambio de PRD a los feature specs afectados sin regenerar todo el sistema salvo que sea necesario.

Usa `kb-product-change-governance` para entender el cambio y `kb-traceability-rules` para decidir si basta con delta o si el impacto es demasiado amplio.

## Paso 1: Parsear argumentos

Modos soportados:

- `analyze <prd.md>`
- `apply <prd.md> --features F-001,F-002,...`

Si falta argumento:
> "Necesito el PRD y si quieres solo el diagnóstico o aplicar ya la resincronización (y sobre qué features)."

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
  - `repartition` — el cambio **mueve la frontera entre features** (una se parte, dos se funden).
    No es una acción que ejecute nadie de una pieza: se resuelve **componiendo** las vías que sí
    existen, y por eso siempre va al conjunto de decisión humana (ver la nota de abajo)
  - `retire` — la capacidad que esta feature especifica **ya no está en el PRD** ([[D-074]]). No es una deriva que se pueda cerrar: es una feature que el producto retiró

### Paso 4A: Generar requisitos de sync por feature

Para cada feature afectada, escribe un archivo junto al spec de la feature (en el mismo directorio donde vive su `_spec.md`, sea `features/<nombre>/spec/` o `features/<nombre>/` en layout plano legacy):

`<directorio_del_spec>/<nombre>_sync_requirements.md`

Debe contener:

- cambio del PRD relevante para esa feature
- HUs y CAs probablemente afectados
- instrucciones para delta
- shared models o reglas transversales afectadas

### Paso 5A: Salida

Resume qué features pueden resolverse con delta y cuáles necesitan revisión manual o repartición.

> **`repartition` no se despacha re-corriendo el discovery ([[D-075]]).** Es tentador decir
> *"esto necesita rediscovery"* y quedarse tan ancho, pero **no hay vía que lo ejecute**:
> regenerar el `_discovery.md` **renumera los `F-00X`**, y los specs ya generados los citan en su
> cabecera — la trazabilidad acabaría apuntando a otra feature. El propio `wf-spec-discover` se
> detiene por eso. Lo que sí existe, y es lo que tienes que recomendar en concreto:
>
> - **la feature que sigue viva** se evoluciona con un delta, marcando como tombstone las HUs y
>   CAs que se van (los IDs no se reutilizan, Regla 12 de `kb-traceability-rules`);
> - **la capacidad que sale del producto** se da de baja, con su `CR-XXX` y su gate de impacto;
> - **la feature nueva que emerge** se genera desde cero y **toma el siguiente `F-00X` libre**,
>   no el hueco de ninguna retirada.
>
> Descríbelo así —qué le pasa a cada feature—, en lenguaje natural y sin nombrar workflows
> ([[D-019]]): quien te invocó sabe enrutarlo.

## Submodo APPLY

### Paso 3B: Validar features solicitadas

Comprueba que los IDs existen en `_features.md` o pueden mapearse a specs existentes.

### Paso 4B: Aplicar sync por feature

Para cada feature solicitada:

1. localiza `<nombre>_sync_requirements.md`
2. si no existe, genera uno de forma mínima
3. **la escritura del spec sigue el contrato de integración del delta, no uno tuyo ([[D-067]]).**
   Aplica el del Paso 4B de `wf-spec-delta` —reglas de
   `wf-spec-delta/references/spec_delta_integration_rules.md`, reapertura de la validación
   (`--unseal`), versión menor, `## Changelog` y regeneración del índice— sobre ese spec, con el
   `_sync_requirements.md` como entrada de cambios. **Eres `sdd-spec-writer`, que es justo el agente
   al que ese workflow delega esa parte** ([[D-070]]): ejecutas el contrato, no invocas el workflow
   —desde [[D-073]] corre en el hilo principal y sostiene gates que tú no puedes presentar—.
4. actualiza la metadata de trazabilidad para reflejar la versión del PRD:
   `derived_from_prd_version` y `derived_from_change`. **`status_sync` no lo escribes tú**: el
   apply reabre la validación del spec (`--unseal`, [[D-061]]) y el sello de deriva lo estampa el
   script del punto 5. Un spec recién modificado no se declara `in_sync` a mano.
5. re-sella el hash de deriva ejecutando desde la raíz del proyecto: `python3 .sdd/scripts/sdd-sync-check.py seal <path_del_spec>` — NUNCA edites `derived_from_prd_hash` a mano (separación autor/verificador). Si el script falta, informa (⚠ re-ejecutar `install.sh`) y deja constancia de que el spec queda sin sello de deriva

> **Por qué se cita el contrato en vez de describir un segundo apply ([[D-067]]).** Este paso decía
> *"siguiendo la misma disciplina que `wf-spec-delta`"* y le faltaban cuatro de sus cinco piezas:
> reapertura de la validación, versión menor, `## Changelog` y regeneración del índice. El resultado era un spec
> **`VALIDADO`, con contenido cambiado y declarándose sincronizado** — exactamente el estado que
> [[D-061]] existe para impedir. Lo tuyo es el Paso 4A (decidir **qué** cambia por feature); el
> **cómo se escribe** tiene ya un dueño.

Si el cambio rebasa un delta razonable, detén esa feature y marca:
> "El cambio rebasa lo que un delta quirúrgico puede integrar en esta feature: mueve su frontera. No se ha tocado nada. Lo que corresponde es decidir, con una persona delante, qué parte sigue viva y se evoluciona, qué parte sale del producto y qué capacidad nueva hay que especificar aparte."

**Las features con `acción: retire` se saltan siempre, y se reportan.** No les apliques nada: ni delta, ni regeneración, ni el sello de sync. Dar de baja una feature es una decisión de producto con coste irreversible —hay planes y tareas construidos encima— y **corres en un fork: no tienes turno para preguntarla** ([[D-045]]). Márcalas así y termina:
> "Esta feature especifica una capacidad que el PRD ya no contempla. No se ha tocado: su baja se confirma aparte, con el impacto delante."

### Paso 5B: Post-proceso

Después de cada spec actualizado:

- recomienda **revisar conflictos entre specs**
- recomienda **medir el readiness** de las features
- si hay planes existentes para esa feature, marca que deben revisarse
