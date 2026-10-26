# Conflict Report: [Nombre del proyecto]

> **Generado por**: sdd-spec-auditor
> **Fecha**: [YYYY-MM-DD]
> **Specs analizados**: [N] features
> **Features**: [lista de feature IDs y nombres]
> **Conjunto comparado**: [F-001 nombre, F-003 nombre, … — TODOS los specs que entraron en la
> comparación, el objetivo incluido. Si excluiste alguno por `Estado: RETIRADO`, nómbralo aquí
> como excluido.] Este informe vale para **este** conjunto: si después aparece un spec nuevo,
> queda estancado hasta que se rehaga.

---

## Estado general

> **[SIN_CONFLICTOS | CONFLICTOS_DETECTADOS]** ([alcance, en una de las tres formas de abajo])

<!-- Las tres formas del alcance, copiadas tal cual (sin etiquetas delante, D-097):
       F-002 contra los otros 4 specs: F-001, F-003, F-004, F-007     ← modo feature
       F-003 contra el otro spec: F-004                               ← modo feature, un solo spec más
       entre los 5 specs comparados: F-001, F-002, F-003, F-004, F-007 ← modo consolidado -->
>
> Resumen en 1-2 frases. Si hay conflictos, indicar cuántos son de severidad ALTA y cuántos MEDIA.
>
> [Solo en modo feature, el del fan-out:] Visto desde [F-00X]. Si otro auditor levanta un choque
> que incluye esta feature, lo arbitra el informe de readiness, y su veredicto manda sobre este.

<!-- En modo feature solo se comparan los pares que incluyen el spec objetivo (D-096): el resumen
     no se pronuncia sobre pares entre otros specs, ni para decir que están limpios. -->
<!-- El token va PRIMERO y literal — lo parsea la medición de readiness. El conjunto va detrás,
     entre paréntesis (D-093): un `SIN_CONFLICTOS` a secas se lee como "esta feature no choca con
     nada", y lo que dice de verdad es "no choca con los N specs que había cuando se escribió". -->

---

## Resumen de conflictos

<!-- Si SIN_CONFLICTOS: "No se detectaron conflictos entre los [N] specs analizados." -->
<!-- Si SIN_CONFLICTOS: indicar explícitamente "Conflictos ALTA: 0 | Conflictos MEDIA: 0". -->

| ID | Tipo | Severidad | Features involucradas |
|----|------|:---------:|-----------------------|
| CF-F001-01 | HU duplicada | ALTA | feature-a, feature-b |
| CF-F001-02 | CA contradictorio | ALTA | feature-b, feature-c |
| CF-F001-03 | Scope overlap | MEDIA | feature-a, feature-c |

<!-- El ID lleva delante el F-00X del spec auditado (D-090): en el fan-out hay un auditor por
     spec y ninguno ve lo que numeran los demás. En modo consolidado (un solo informe de todo
     el directorio) no hay con quién colisionar: ahí es CF-01, CF-02, … -->

---

## Detalle de conflictos

<!-- Repetir este bloque por cada conflicto detectado -->

### [CF-F001-01] [Tipo de conflicto] — Severidad: [ALTA | MEDIA]

**Features involucradas**: `[feature-a]`, `[feature-b]`

**Descripción**: [explicación del conflicto en lenguaje natural]

**En `[feature-a]`**:
> "[cita exacta de la HU, CA, Journey o regla en conflicto — con su ID]"

**En `[feature-b]`**:
> "[cita exacta de la sección en conflicto — con su ID]"

**Causa** (solo si es de un modelo compartido): [Duplica | Supone | Efecto no catalogado | Sin dueño | Decisión] — [una frase: qué regla de qué modelo, y de qué feature es dueña]

**Por qué es un conflicto**: [explicación específica de la incompatibilidad. Si citas la regla
que sostiene tu veredicto, cítala por lo que dice —"el mismo modelo con comportamientos distintos
en dos CAs de features diferentes"—, nunca por el nombre de la kb que la define (D-091).]

**Decisión de producto**:
- **Qué hay que decidir**: [una frase sobre el comportamiento del producto, no sobre los documentos — ej: "qué pasa cuando alguien quiere cambiar o borrar un gasto que tiene una deuda asociada"]
- **Ejemplo**: [un caso concreto con el actor de las specs, sacado de sus journeys o CAs — ej: "el Usuario paga 30 € de una cena por Ana y se registran el gasto y la deuda; después ve que eran 25 €"]
- **Afecta también a**: [solo si hay: F-00Z (nombre) — qué lee que esta decisión cambia; si no, omite la línea]
- **Opción 1 — [título corto]**: [qué le pasa al actor con esta opción]. *Cambia:* [F-00X (nombre), F-00Y (nombre)]
- **Opción 2 — [título corto]**: [qué le pasa al actor]. *Cambia:* [F-00X (nombre)]

<!-- Si la causa es «Sin trasladar» (D-113) —el dueño ya decidió la regla en su contrato y otra
     feature no la ha copiado— o «Decidido fuera del dueño» (v0.127.1) —el usuario ya lo
     respondió, quedó escrito en otra feature y el dueño no dice nada—, NO hay Decisión de
     producto: en su lugar va

**Traslado**:
- **Qué**: [la regla en llano, como la vería el actor — ej: "reservar dinero para un objetivo exige saldo suficiente en la cuenta". NUNCA la sección que se edita ("en ## Modelos de otras features, separar la fila…"): esto es lo que lee el usuario en la opción *Aplicar lo ya decidido*]
- **Decidido en**: [F-00X (nombre) — cita del contrato, o la respuesta del usuario: "respuesta a D-006"]
- **Falta en**: [F-00Y (nombre) — en «Decidido fuera del dueño», el dueño]

     y la lista de pendientes lo aplica sin preguntar al usuario.
     También es Traslado una corrección SIN comportamiento en disputa (una tabla que no declara lo
     que sus propios CAs ya hacen): su Qué dice lo que el spec pasará a decir —"objetivos de ahorro
     dirá que reservar desde una cuenta crea el movimiento"—. Nunca una Decisión de una sola opción:
     si solo te sale una, es esto (v0.128.0; la lista la trata igual, pero con tu texto). -->

<!-- La Decisión de producto se presenta TAL CUAL al usuario (D-109): la extrae el script de
     pendientes y el hilo principal la copia. Por eso:
     - El Ejemplo sale de las specs o del PRD, NUNCA inventado: un ejemplo inventado cuela un
       comportamiento que nadie ha decidido.
     - Las opciones describen al ACTOR de las specs —Usuario, cliente de la API, operador, el
       asistente…—, no los criterios: "el Usuario no puede borrar el gasto mientras exista la
       deuda", no "se añaden dos CAs de bloqueo".
     - Entre 2 y 4 opciones; incluye siempre las dos de "una se ajusta a la otra" si aplican.
     - *Cambia:* nombra al menos un spec —el que tendrá que recogerlo—, aunque solo sea dejarlo
       escrito. Es la lista sobre la que se corregirá con un delta. Si la opción fija una regla
       de un modelo compartido, *Cambia:* nombra a su DUEÑO (D-111): la regla se escribe solo ahí.
     - Cada opción describe UN comportamiento: no la expliques comparándola con dos cosas que se
       comportan distinto ("igual que A o que B"), porque quien la aplica no sabe cuál eligió.
     - Si una opción da al actor algo que el PRD no recoge (una operación nueva, como "deshacer
       un cobro"), dilo EN la opción: "… Ojo: amplía el PRD". Que se entere al elegirla, no después.
     - "Afecta también a" (D-112): features que NINGUNA opción cambia pero que leen algo que la
       decisión cambia (si reservar pasa a crear un gasto, presupuesto, que suma gastos). Esas
       features esperan a la decisión sin entrar en su bloque. Sin la línea, no espera nadie: no la
       pongas "por si acaso", porque frena a quien no hace falta.
     - Consecuencias directas (v0.128.0): si elegir una opción abre una pregunta que es su
       consecuencia inmediata, dila EN la opción con lo que la propia opción implica, o parte la
       opción en dos. Medido en CU-3.ac: "el saldo puede quedar negativo" se eligió sin decir qué
       pasa al eliminar una cuenta en negativo, y esa pregunta salió después como otra vuelta.
     - Sin recomendación: es una decisión de producto, no tuya. -->

---

## Inventario de comparaciones realizadas

> Esta sección garantiza trazabilidad de qué se comparó contra qué.

| Check | Features comparadas | Conflictos encontrados |
|-------|---------------------|:---------------------:|
| HUs duplicadas | Todos los pares | N |
| CAs contradictorios | Todos los pares | N |
| Scope overlap | Todos los pares | N |
| Shared models inconsistentes | Todos los specs | N |
| Fuera de alcance contradictorio | Todos los pares | N |

---

## Próximos pasos

<!-- Si SIN_CONFLICTOS -->
> No hay choques entre estos specs. Eso no los hace planificables por sí solo (D-077): el gate de
> planificación exige además el spec **validado**, y uno recién generado nace en borrador.

<!-- Si CONFLICTOS_DETECTADOS -->
1. Revisar cada conflicto de severidad **ALTA** — deben resolverse antes de planificar las features afectadas
2. Los conflictos de severidad **MEDIA** pueden documentarse como decisiones de diseño y resolverse en la fase de implementación
3. Para cada conflicto resuelto: decidir **qué feature manda** y pedir que se aplique el cambio
   sobre el spec que toque, que reabre su validación; después, una nueva revisión de conflictos
   para verificar que se eliminó. **No editar los specs a mano** (D-082): una edición fuera de las
   vías de evolución conserva el sello `VALIDADO` y el gate de planificación la deja pasar.
