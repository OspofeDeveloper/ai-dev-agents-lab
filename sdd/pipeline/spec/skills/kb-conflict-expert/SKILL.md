---
name: kb-conflict-expert
description: Experto en detección de conflictos entre Specs SDD de features. Reglas para identificar HUs duplicadas, CAs contradictorios, scope overlaps y shared models inconsistentes entre specs del mismo proyecto.
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Conflict Expert — Reglas de Detección de Conflictos entre Specs SDD

Estas reglas aplican cuando se compara un conjunto de Specs SDD (`_spec.md`) que pertenecen al mismo proyecto para detectar inconsistencias que podrían indicar solapamiento de scope, requisitos contradictorios o modelos mal definidos.

---

## Regla 1: HUs duplicadas

**Definición**: Dos HUs en features distintas describen la misma acción para el mismo actor.

**Criterio de detección**: Coincidencia de los tres componentes:
- Mismo actor (o rol equivalente — ej: "trabajadora" y "cuidadora" en el mismo sistema son el mismo actor)
- Mismo verbo de acción principal (registrar, consultar, editar, confirmar, etc.)
- Mismo objetivo funcional (para qué sirve la acción)

**Cómo reportar**: Cita ambas HUs con sus IDs, features de origen y la coincidencia exacta detectada.

**No es duplicado si**: Los dos verbos son distintos aunque el objetivo sea similar (ej: "visualizar" vs. "exportar" un informe), o el actor tiene capacidades estructuralmente diferentes en cada feature.

---

## Regla 2: CAs contradictorios

**Definición**: Dos CAs en features distintas que, dado el mismo GIVEN y el mismo WHEN, describen THENs incompatibles o mutuamente excluyentes.

**Criterio de detección**:
- GIVEN equivalente (misma precondición del sistema o del usuario)
- WHEN equivalente (misma acción desencadenante)
- THEN incompatible (resultados que no pueden ser verdaderos simultáneamente — ej: "el sistema muestra un error" vs. "el sistema confirma la operación" para la misma acción en el mismo estado)

**Cómo reportar**: Cita los dos CAs completos con sus IDs y features de origen. Explica por qué los THENs son incompatibles.

**No es contradicción si**: Los GIVEN son distintos (precondiciones diferentes producen resultados diferentes es comportamiento normal).

---

## Regla 3: Scope overlap

**Definición**: Una feature incluye Journeys o funcionalidad que, por cohesión funcional, pertenecen a otra feature ya definida.

**Criterio de detección** (consulta también `kb-decompose-expert`):
- Un Journey en la feature A incluye pasos que son el objetivo principal de otra feature B
- Una feature "toma prestado" un flujo completo de otra en lugar de referenciarla como dependencia

**Cómo reportar**: Describe el solapamiento con citas de los Journeys afectados. Sugiere qué feature debería ser la propietaria de ese scope.

**No es overlap si**: El Journey de A *termina* en el punto de entrada a B (es una dependencia, no un solapamiento).

---

## Regla 4: Shared models inconsistentes

**Definición**: Un modelo de dominio aparece en dos o más features con atributos, comportamientos o semántica incompatibles, o aparece en una feature nueva sin estar declarado en el `_features.md`.

**Criterio de detección**:
- Mismo nombre de modelo → atributos definidos de forma diferente en dos features
- Mismo nombre de modelo → comportamientos distintos en dos CAs de features diferentes (ej: el modelo puede estar en estado X en una feature pero ese estado no existe en la otra)
- Modelo referenciado en un spec pero no declarado como "shared" en `_features.md`

**Cómo reportar**: Cita el modelo, las features que lo referencian y la inconsistencia específica detectada.

### La causa de un conflicto de modelo compartido ([[D-111]])

Cada regla de un modelo compartido tiene un dueño: la feature dueña publica su **contrato** (ciclo
de vida, qué puede hacer el actor, invariantes y el catálogo de **orígenes externos**), y las
demás lo citan o le hacen una **petición**. Cuando dos specs chocan sobre un modelo compartido, di
**por qué** —es lo que decide dónde se corrige—, con una de estas causas:

| Causa | Qué pasa | Dónde se corrige |
|---|---|---|
| **Duplica** | el consumidor reescribe una regla del contrato del dueño **para el mismo caso**, y no coinciden | el consumidor: cita el contrato en vez de reescribirlo |
| **Supone** | el consumidor da por hecha una regla que el dueño no dice | el dueño: decide la regla en su contrato |
| **Efecto no catalogado** | una operación del consumidor crea o cambia el modelo y el catálogo de orígenes del dueño no la recoge | el dueño: añade la fila y decide qué se puede hacer con lo que crea |
| **Sin dueño** | cada spec deja la regla a la otra y nadie la tiene | el dueño del modelo, siempre |
| **Decisión** | los dos specs dicen lo que les toca y el choque es de producto | según la decisión, pero una regla del modelo se escribe solo en su dueño |
| **Sin trasladar** | el dueño **ya decidió** la regla y la tiene en su contrato, y el consumidor no la ha copiado o sigue con la versión anterior | el consumidor; no hay nada que decidir ([[D-113]]) |
| **Decidido fuera del dueño** | el **usuario ya respondió** —consta en la lista de decisiones o en el changelog de un spec— y la regla quedó escrita en otra feature; el dueño no dice nada de ese caso | el dueño la recoge y la otra feature pasa a citarla; no hay nada que decidir (v0.127.1) |

**Lo que el usuario ya decidió no se le vuelve a preguntar (v0.127.1).** Antes de escribir una
*Decisión de producto*, mira la **lista de decisiones**: las preguntas que el usuario ya respondió
en los análisis de cambio, con su respuesta literal y de quién es la regla, **y las opciones que
eligió en conflictos anteriores** (campo `conflicto`; v0.127.2)
(`sdd-analysis-gaps.py <features_dir> --decisiones --json`; tu flujo te la pasa), y los
changelog de los specs (*"Integra la decisión de producto del usuario sobre `CF-…`"*). Si uno de los
dos lados del choque **es** esa respuesta y el dueño no dice nada de ese caso, la causa es
**Decidido fuera del dueño**, y va con un bloque **Traslado** como el de abajo: *Decidido en* es la
feature donde quedó, con la referencia de la respuesta (*"F-001 (registro-movimientos), respuesta a
D-006"*), y *Falta en* es **el dueño**. Si el dueño ya decía **lo contrario** antes de la respuesta,
entonces sí es **Decisión**, y su primera opción es lo que el usuario respondió, citado como tal
(*"lo que respondiste en D-006"*): nunca le ofrezcas solo opciones que lo contradicen. Medido en la
pasada 2 de `CU-3.ac`: *"no cuenta en ningún presupuesto"*, respondido por el usuario y escrito solo
en registro de movimientos, salió como conflicto grave con una opción contraria a su respuesta; y
*"el saldo puede quedar negativo"*, decidido en un conflicto anterior y escrito solo en cuentas,
salió en dos informes como *"no hay decisión nueva que tomar"* y aun así con una *Decisión de
producto* de una única opción.

**Una decisión de una sola opción no es una decisión.** Si al redactarla solo te sale una opción,
es que ya está decidida: es **Sin trasladar** o **Decidido fuera del dueño**, con su *Traslado*.

**Duplica es solo para el mismo caso.** Si el dueño no dice nada del caso concreto (un movimiento
nuevo que su regla, escrita antes, no podía nombrar), no hay dos reglas que choquen: hay una sola,
fuera de su sitio. Es **Decidido fuera del dueño** si salió de una respuesta del usuario, y
**Supone** si no.

**"Sin trasladar" no es una decisión ([[D-113]]).** Solo cuando el contrato del dueño **dice ya** la
regla —cítala—: si el dueño la deja ambigua, es **Supone** o **Decisión**. En vez de *Decisión de
producto*, escribe un bloque **Traslado** con tres líneas: `- **Qué**:` la regla en llano, como la
vería el usuario (*"reservar dinero para un objetivo exige saldo suficiente en la cuenta"*);
`- **Decidido en**: F-00X (nombre)`; `- **Falta en**: F-00Y (nombre)`. Lo ya respondido no se
vuelve a preguntar: la lista lo ofrece como *"Aplicar lo ya decidido"* y se copia sin preguntar.
Medido en `CU-3.ac`: *"F-005 ya decidió que reservar exige saldo y F-008 no trasladó esa
respuesta"* salió como una de las cuatro decisiones menores, con su pregunta.

**Contradicción o hueco: la severidad ([[D-112]]).** Solo **Duplica** (que no coincide) y
**Decisión** son una **contradicción** —dos specs dicen cosas incompatibles—, y solo esas son
**ALTA**. **Supone**, **Efecto no catalogado** y **Sin dueño** son un **hueco**: falta una regla
que alguien tiene que decidir, pero ningún spec dice lo contrario de otro. Un hueco es **MEDIA**: no
bloquea a las features que no lo resuelven, y la lista lo ofrece como decisión de su bloque. Medido
en la pasada 1 de `CU-3.ab`: la mayoría de los *"conflictos graves"* eran huecos —el contrato de
cuentas no decía si el saldo puede quedar negativo; objetivos no repetía una regla de cuentas que le
bastaba con citar— y cada uno frenó como si dos specs se contradijeran.

Escríbela en el informe (campo **Causa** del conflicto). Y en la **Decisión de producto**, el
*Cambia:* de una opción que fija una regla del modelo nombra **al dueño**: si una opción obliga a
cambiar también al consumidor, es porque el consumidor tenía la regla duplicada — y eso se
corrige citando, no volviendo a escribirla. **El dueño de la regla, no solo el del modelo**: lo que
un modelo *es* (si se puede editar, si lleva categoría, si su saldo puede quedar negativo) es de su
dueño; lo que un cálculo *cuenta* (qué entra en el límite global) es del dueño de ese cálculo. Una
opción que fija las dos cosas nombra a los dos dueños en su *Cambia:*. Medido en la pasada 2 de
`CU-3.ac`: la opción *"el saldo puede quedar negativo con un gasto"* nombraba solo a cuentas; el
contrato de Movimiento, que es quien registra ese gasto, no la recibió, y volvió como conflicto.

**Lo que decide el usuario se escribe en sus palabras** (v0.127.1). *Qué hay que decidir*, cada
opción y el *Qué* de un traslado se copian literales como requisito y acaban **dentro de los
specs**: sin términos internos —ni *"gasto sintético"*, ni *"par enlazado"*, ni *"origen externo"*,
ni nombres de modelo como `ObjetivoAhorro`—. Di lo que ve el usuario: *"el gasto que se crea al
mover dinero entre tus cuentas"*. Medido en la pasada 2 de `CU-3.ac`: *"gasto sintético"* ya está en
cinco frases de los specs, entrado por las opciones de un conflicto.

**Un conflicto que sigue abierto se reescribe con el criterio de hoy.** Si lo traes de un informe
anterior, no copies su encabezado (*"Severidad: ALTA (se mantiene)"*): vuelve a decidir su causa y
su severidad y escribe su *Decisión de producto* (o su *Traslado*) si no la tenía. Medido en
`CU-3.ac`: nueve conflictos arrastrados seguían en ALTA con causa *"sin dueño"*, que es un hueco, y
uno sin decisión de producto; fue la medición la que tuvo que rebajarlos.

**Los conflictos de otro informe se citan con su ID tal como lo da la lista de pendientes**, o no se
citan. Medido en `CU-3.ac`: deudas citó como `CF-F005-02` lo que su dueño llama `CF-F005-01`, y la
medición tuvo que escribir un aviso en un informe que lee el usuario.

**Una opción describe un solo comportamiento.** No la expliques comparándola con dos cosas que se
comportan distinto (*"igual que una aportación directa o una transferencia"*, cuando una deja un
movimiento y la otra dos): quien la elige no sabe cuál de las dos ha elegido, y el que la aplica
tampoco. Medido en la pasada 4 de la tanda de continuación: esa opción partió el cambio en dos
lecturas, y cada spec se quedó con una.

---

## Regla 5: Fuera de alcance contradictorio

**Definición**: Una feature declara algo como fuera de su alcance que otra feature asume incluido en su propio alcance.

**Criterio de detección**:
- La sección "Fuera de Alcance" de la feature A menciona explícitamente algo que la feature B incluye en sus HUs o Journeys
- Una feature asume que otra gestiona algo, pero esa "otra feature" lo tiene explícitamente en su "Fuera de Alcance"

**Cómo reportar**: Cita la declaración de fuera de alcance y la HU/Journey que la contradice. Indica cuál de las dos debería tener razón.

---

## Severidad de los conflictos

| Tipo | Severidad | Impacto |
|------|-----------|---------|
| CAs contradictorios | ALTA | Comportamiento indefinido en producción |
| HUs duplicadas | ALTA | Implementación doble, inconsistencia de datos |
| Shared models inconsistentes — contradicción | ALTA | Modelo de dominio corrupto |
| Shared models inconsistentes — hueco (falta la regla, nadie la contradice) | MEDIA | Decisión pendiente del dueño; no corrompe nada todavía |
| Scope overlap | MEDIA | Duplicación de trabajo, boundaries difusos |
| Fuera de alcance contradictorio | MEDIA | Gap funcional no cubierto por ninguna feature |

---

## Cómo se citan estas reglas en un informe ([[D-091]])

El informe de conflictos lo lee una persona de producto que decide qué feature manda en cada
choque. Cuando justifiques un veredicto **cita la regla por lo que dice, no por dónde vive**:

| En vez de | Escribe |
|---|---|
| *"Regla 4 de `kb-conflict-expert`"* | *"el mismo modelo con comportamientos distintos en dos CAs de features diferentes"* |
| *"la tabla de severidad de `kb-conflict-expert` da ALTA por defecto"* | *"un shared model inconsistente corrompe el modelo de dominio, y eso es ALTA por defecto"* |

No es una regla de estilo: por [[D-042]] ese texto se le lee **verbatim** a quien decide, y el
nombre de una kb no le dice nada — es un detalle de cómo está construido el sistema que se lo
cuenta. La regla enunciada sostiene el veredicto ella sola; el nombre solo sostiene la
procedencia, y para eso ya está `Generado por:`. Medido tres veces en la pasada de `CU-3.d` del
2026-09-18 (probe V1), las tres con esta forma exacta.

---

## Qué NO es un conflicto

- Dos features que referencian el mismo shared model correctamente (con owner declarado) — eso es el comportamiento esperado de los shared models.
- Un consumidor que **cita** el contrato del dueño (*"según el contrato de Movimiento"*) o que tiene una **petición al dueño** registrada: es la vía correcta. Una petición sin atender no es un conflicto que arbitrar —la lista de pendientes ya la trae como trabajo sobre el dueño—. Tampoco lo es una línea **Estado** dentro de una petición (*"pendiente de que F-001 las integre"*): es de antes de [[D-112]] y no cuenta; si el dueño cita la petición en su fila, está atendida.
- CAs que describen el mismo escenario pero para **actores distintos** con capacidades distintas — son CAs distintos válidos.
- Features que mencionan la misma entidad de dominio con propósitos distintos (ej: Feature A *crea* usuarios, Feature B *lista* usuarios — no es conflicto, es colaboración correcta).
