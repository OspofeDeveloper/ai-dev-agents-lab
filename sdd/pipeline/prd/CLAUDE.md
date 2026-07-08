# PRD Lab — Guía de la fase PRD

Guía de la etapa de **PRD** dentro del pipeline SDD: creación, estructuración y revisión de Product Requirements Documents antes de entrar en Spec.

> **Audiencia.** El **hilo principal (orquestador)** usa el enrutado de abajo para mapear la petición del usuario al workflow o agente correcto. Un **subagente especialista** (p. ej. `prd-expert`) también carga esta guía al tocar artefactos de PRD: para él es **contexto de fase**, no una instrucción de rol — su contrato de trabajo es su propio system prompt + sus `kb-*`.

## Reparto de trabajo en la fase PRD

- El **hilo principal (orquestador)** entiende la petición, decide si hay que crear un PRD desde cero, revisar uno existente o resolver una duda conceptual sobre PRDs, y activa el workflow o agente correcto. **No redacta el documento final**, no hace análisis funcional de Spec y no toma decisiones técnicas de implementación.
- La **redacción, reorganización y revisión guiada** del PRD la realiza el agente **`prd-expert`**, con `kb-prd-expert` cargada en su contexto.
- El enrutado no construye prompts a mano: las workflows y `prd-expert` ya contienen el conocimiento operativo necesario; el hilo principal solo activa la pieza correcta con los argumentos correctos.

## Rootmap de workflow skills (enrutado del hilo principal)

| Intención del usuario | Skill | Argumentos |
|---|---|---|
| Crear un PRD desde notas, brief o idea inicial | `/wf-prd-create` | `<directorio_proyecto> [--source <notas.md>] [--output <prd.md>]` |
| Revisar si un PRD está limpio y bien planteado | `/wf-prd-review` | `<archivo_prd.md>` |
| Gestionar un cambio de producto sobre un PRD ya existente | `/wf-prd-change` | `<archivo_prd.md> --new-reqs <cambio.md>` |
| Propagar un cambio de PRD por todo el pipeline en un solo comando (cascade) | `/wf-prd-change-cascade` | `<archivo_prd.md> [--new-reqs <cambio.md>] [--features F-001,...] [--review-before-apply] [--skip-design] [--dry-run]` |

## Enrutado (hilo principal)

1. **Identifica la intención** usando el rootmap anterior.
2. **Si encaja en una `wf-*` cerrada**, el hilo principal invoca esa workflow con los argumentos correctos.
3. **Si no encaja en una `wf-*` pero la petición es de ayuda para redactar o reorganizar un PRD**, delega al agente `prd-expert`.
4. **Reporta al usuario** el resultado y el siguiente paso.

Si la intención no coincide exactamente, se usa matching semántico con la columna de intenciones. Si hay ambigüedad entre crear un PRD y revisar uno existente, el hilo principal pregunta por la ruta del documento o por el material base antes de invocar.

## Agentes PRD disponibles

La unidad primaria de trabajo en esta etapa es el **agente especializado en PRD**.

| Agente | Dominio |
|---|---|
| `prd-expert` | Redacción, reorganización y revisión guiada de PRDs orientados a negocio y compatibles con el pipeline SDD |

Se usan workflows cuando existe una pipeline clara y cerrada. Si la petición no requiere una workflow concreta pero sí ayuda experta para redactar o limpiar un PRD, el hilo principal delega a `prd-expert`.

## Skills de conocimiento PRD

Las `kb-*` viven en el frontmatter `skills: [...]` de los agentes de la fase; el harness las inyecta en el contexto del subagente. El hilo principal no las consulta ni necesita su inventario: vive en `sdd/meta/skill-registry.md` (mapa humano: el `README.md` de la fase).

## Principio operativo

- El hilo principal decide si una petición encaja en una `wf-*` existente o si debe delegarse directamente a `prd-expert`.
- Si existe una workflow cerrada y claramente adecuada, se usa.
- Si la petición es de redacción o reescritura de un PRD y no exige una pipeline cerrada, se usa `prd-expert`.
- Si la petición es una duda conceptual sobre qué debe contener un PRD, se resuelve delegando a `prd-expert`, que ya carga `kb-prd-expert`.
- Si una respuesta a un gap de Spec añade una entidad persistente, un catálogo reutilizable o una nueva granularidad funcional no comprometida en el PRD, se trata como cambio de producto y se activa `wf-prd-change`.
- Los subagentes trabajan con sus `kb-*` ya cargadas; el hilo principal no replica ese conocimiento.

## Principio de precondiciones

Los workflow skills tienen sus propias validaciones. **No se bypasean.** Si un skill reporta bloqueos o información faltante, el hilo principal los comunica al usuario y espera a que los resuelva antes de reintentar.

**Frontera create → review.** Tras `wf-prd-create`, si el PRD trae marcadores `[ASUNCIÓN]`/`[ASN-XXX]`, el gate de asunciones **no lo resuelve el hilo principal**: no se lanza `AskUserQuestion` por ellas, no se edita el PRD para integrarlas, no se sube versión ni se sella aprobación. Ese gate (confirmar/rechazar/editar cada asunción, limpiar la sección, sello `Aprobado por:`) es exclusivo de `wf-prd-review` (Pasos 5.5 y 6). La única acción correcta del orquestador tras crear es **parar y remitir** a `/wf-prd-review <path/prd.md>`. Si el usuario decide no revisar, las asunciones sin confirmar **no desaparecen ni "bajan como gaps" automáticamente**: la entrada a la fase spec las **detecta** (`sdd-prd-ready.py`) y **te obliga a elegir** —revisar o continuar con `--allow-unreviewed-prd` asumiendo alcance no-revisado— (ver [[D-020]]); nunca se hornean en silencio en los specs.

**Readiness antes de spec (¿cuál es el siguiente paso?).** Cuando el usuario pregunte qué sigue o pida avanzar a specs con un PRD ya existente, **no infieras "el PRD está listo" por la topología de ficheros** (que `spec/features/` esté vacío no significa que el PRD esté cerrado, y "he terminado de mirarlo" no es "está aprobado"). Comprueba la readiness **mecánicamente**: `python3 .sdd/scripts/sdd-prd-ready.py <prd.md>`. Si hay `OPEN_ASSUMPTIONS`/`ASSUMPTION_MISMATCH`, el siguiente paso correcto es **revisar el PRD** (`wf-prd-review`), no generar specs — surfacea cuántas asunciones quedan abiertas y ofrece la revisión; si solo está `UNSEALED`, recomiéndalo como advisory. Nunca declares el PRD "listo" sin la evidencia del script.

## Principio de autonomía por capas

El ecosistema PRD opera en tres capas:

- **Capa orquestador (hilo principal)**: decide intención → workflow o agente. No redacta ni prescribe lógica interna.
- **Capa workflow (`wf-*`)**: cuando existe una pipeline cerrada, recoge requisitos, verifica precondiciones y delega al agente especializado.
- **Capa agente PRD**: redacta o revisa el trabajo real con su knowledge skill cargada en contexto.

Cada capa es responsable de su nivel de decisión. Si existe workflow, se activa. Si no existe workflow y la tarea es claramente de redacción o revisión guiada de un PRD, se delega a `prd-expert`.
