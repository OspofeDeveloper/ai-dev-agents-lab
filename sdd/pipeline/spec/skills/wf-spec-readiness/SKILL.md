---
name: wf-spec-readiness
description: "Genera un informe de readiness desde los artefactos post-spec (specs, READMEs, _features.md, _conflict_report.md): que features estan listas para plan, cuales bloqueadas y por que, y el orden de implementacion recomendado."
when_to_use: "Activa en frases como 'que features estan listas', 'readiness de las features', 'cuales puedo planificar', 'orden de implementacion', 'verifica readiness', 'que falta para planificar'."
argument-hint: "<path/features/>"
effort: medium
allowed-tools: [Read, Bash]
context: fork
agent: sdd-spec-auditor
user-invocable: true
---

# Workflow: READINESS

Tu objetivo es sintetizar el estado de los artefactos post-spec-generation en un informe accionable que le diga al usuario exactamente qué features puede pasar a `/wf-prepare-plan` y en qué orden. No generas ni modificas ningún artefacto existente — solo lees y sintetizas. Usa `kb-gap-conventions` para interpretar marcadores `[INCOMPLETO]` y severidades, y `kb-conflict-expert` para interpretar severidades de conflictos.

**Regla de oro:** Este informe es una fotografía del estado actual. No propone resoluciones — indica qué falta y dónde encontrarlo.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Directorio de features**: el primer argumento. Debe ser el directorio que contiene las carpetas de features (ej: `docs/features/`).

Si no hay argumento, intenta inferir buscando un directorio `features/` en el directorio actual.

Si no hay argumento y no se puede inferir, informa al usuario:
> "Necesito el directorio donde viven las features, para revisar cuáles están listas."

---

## Paso 2: Localizar artefactos

1. Busca `*_features.md` en el directorio padre del directorio de features (ej: si features/ está en `docs/features/`, busca `docs/*_features.md`).
2. Busca todos los `*_spec.md` cubriendo ambos layouts de feature: `<features-dir>/*/spec/*_spec.md` (subcarpetas) y `<features-dir>/*/*_spec.md` (plano legacy).
3. Busca todos los `README.md` dentro de `<features-dir>/*/README.md`.
4. Busca los informes de conflictos **en los dos sitios donde se escriben** (opcional — pueden no existir):
   - **Consolidado**: `*_conflict_report.md` en el directorio padre del directorio de features — lo escribe `/wf-spec-conflict` cuando se verifica el directorio entero de una vez.
   - **Por feature**: `<features-dir>/*/spec/*_conflict_report.md` (subcarpetas) y `<features-dir>/*/*_conflict_report.md` (plano legacy) — es lo que produce el fan-out del Paso 7 de `wf-spec-features-first`, que lanza **un auditor por spec** y cada uno escribe junto a su spec.

   Buscar solo en la raíz deja fuera **todos** los informes del fan-out, que es el camino por defecto ([[D-047]]): el readiness se declararía "sin análisis de conflictos" teniendo N informes en disco, y esa advertencia no bloquea — se pierde en silencio.

Valida:
- Si no hay `_features.md` → detén: "No se encontró `_features.md` en `<directorio_padre>`. Hay que generar antes los specs por feature."
- Si no hay specs → detén: "No se encontraron specs de feature en `<features-dir>`. Hay que generarlos antes."
- Si falta algún README → advertencia no bloqueante: "Falta README.md en `<feature>/`. Las dependencias de esta feature se inferirán solo del `_features.md`."
- Si no hay **ningún** informe de conflictos en ninguno de los dos sitios → advertencia no bloqueante: "No se encontró ningún `_conflict_report.md`. Un análisis de conflictos completo daría más información; continúo sin él."

---

## Paso 3: Leer todos los artefactos

Lee el contenido completo de:
- `_features.md`
- Cada `*_spec.md` de feature
- Cada `README.md` de feature (los que existan)
- **Todos** los informes de conflictos localizados en el Paso 2.4 (el consolidado y los de cada feature), no solo el primero que encuentres

---

## Paso 4: Inventariar estado de cada feature

Para cada feature, extrae:

### 4a — Identificación

Del `_features.md`, extrae para cada feature:
- Feature ID (F-001, F-002, etc.)
- Nombre de la feature
- Ruta al spec (si existe)

**Detección de features no generadas aún**: si una feature del `_features.md` no tiene archivo `*_spec.md` correspondiente en `<features-dir>/<nombre>/`, marca la feature como `PENDIENTE_GENERACIÓN` y omite los Pasos 4b–4d para ella (no hay spec que inspeccionar). Sus dependencias se infieren solo del `_features.md`.

### 4b — Gaps (marcadores [INCOMPLETO])

Busca la cadena literal `[INCOMPLETO]` en el spec de la feature. Para cada HU marcada:
- ID de la HU (ej: HU-003)
- Gaps que la bloquean (referenciados en la línea que contiene `Pendiente de gap(s):` o `[P-XXX]` cercanos al marcador)

Clasifica la feature como **BLOQUEADA** si tiene al menos una HU `[INCOMPLETO]`.

### 4c — Conflictos no resueltos

Para **cada** informe de conflictos localizado:
- Primero verifica su estado general. Debe indicar explícitamente `SIN_CONFLICTOS` o `CONFLICTOS_DETECTADOS`.
- Si el archivo existe pero no deja ese estado de forma inequívoca, trátalo como artefacto ambiguo y repórtalo en el informe de readiness.
- Busca todos los conflictos de severidad **ALTA** que involucren esta feature.
- Un conflicto se considera no resuelto si aparece en algún informe (el informe refleja el estado en el momento de su generación; si se resolvió, la verificación de conflictos tuvo que volver a pasarse después).

Clasifica la feature como **BLOQUEADA** si tiene al menos un conflicto ALTA asociado.

> **Cuando los informes se contradicen, arbitras tú ([[D-047]]).** Con el fan-out de features-first
> hay **un auditor por feature**, y cada uno mira el mismo grafo desde su lado: es esperable que
> sobre un mismo par uno levante un conflicto y otro declare `SIN_CONFLICTOS`. Tú eres el primer
> lector que ve **todos** los specs y **todos** los informes a la vez, así que la contradicción se
> resuelve aquí y no antes.
>
> Reglas de arbitraje:
> - **Un `SIN_CONFLICTOS` no refuta un hallazgo.** Significa "no lo vi desde mi feature", que es
>   justo lo que pasa cuando el conflicto está en el lado del otro. Nunca cierres un conflicto por
>   recuento de informes.
> - **Resuelve mirando los specs**, que sí tienes: comprueba en el texto si la contradicción existe.
>   Un conflicto solo se descarta con la cita concreta que lo desmiente.
> - **Deja constancia del desacuerdo** en el informe: el ID del conflicto, quién lo levantó, quién no
>   lo vio, y tu veredicto con su evidencia. Un conflicto silenciosamente desaparecido entre dos
>   pasadas es indistinguible de uno resuelto.
> - **Si no puedes resolverlo con los specs**, no lo cierres: mantenlo **abierto** con la severidad
>   más alta que le haya dado cualquier informe y marca la feature `BLOQUEADA`. El coste de un falso
>   bloqueo lo paga una revisión; el de un falso "listo" lo paga el plan.

### 4d — Dependencias

Del README de la feature, extrae la sección `## Dependencias`:
- **Requiere**: lista de features que deben implementarse antes
- **Bloquea**: lista de features que dependen de esta

Complementa con el `_features.md`: si una feature referencia un shared model cuyo owner es otra feature, la feature referenciadora depende de la feature owner (a menos que ya esté en la lista de Requiere).

Construye la lista unificada de dependencias para cada feature.

---

## Paso 5: Construir el grafo de dependencias

1. Crea un grafo dirigido donde cada nodo es una feature y cada arista va de la dependencia hacia la feature que la requiere.
2. Detecta ciclos. Si hay un ciclo → repórtalo en la sección correspondiente del informe pero no detengas la ejecución. Excluye las features del ciclo del topological sort.
3. Realiza un **topological sort** agrupando en fases (waves) las features que pueden ejecutarse en paralelo:
   - **Fase 1**: features sin dependencias entrantes (nodos raíz)
   - **Fase 2**: features cuyas dependencias están todas en Fase 1
   - **Fase N**: features cuyas dependencias están todas en fases anteriores

---

## Paso 6: Determinar readiness de cada feature

Para cada feature, asigna un estado:

| Estado | Condición |
|--------|-----------|
| `LISTA` | Sin `[INCOMPLETO]`, sin conflictos ALTA, sin artefactos ambiguos y sin dependencias bloqueantes |
| `BLOQUEADA` | Tiene HUs `[INCOMPLETO]`, conflictos ALTA, dependencias bloqueantes o artefactos ambiguos que impiden decidir con seguridad |
| `PENDIENTE_GENERACIÓN` | Identificada en el discovery pero aún no se ha generado spec (no se ha incluido en ninguna iteración de `wf-spec-features-first`). No es un bloqueo accionable — refleja que el humano aún no ha pedido procesarla. |
| `REQUIERE_CAMBIO_PRD` | El spec o `_features.md` declara alcance derivado desde analysis que debería consolidarse primero en PRD, o el artefacto explicita un aviso de gobernanza pendiente |

Una feature puede tener múltiples bloqueos simultáneos. En ese caso, listar todos los motivos en la columna de bloqueantes. La prioridad de display es: CAMBIO_PRD > GAPS > CONFLICTOS > DEPENDENCIAS > AMBIGÜEDAD_DE_ARTEFACTO.

**Nota importante**: el readiness report usa solo estados canónicos. El detalle fino se expresa en la columna `Bloqueantes`, no creando variantes de estado adicionales.

**Nota sobre `PENDIENTE_GENERACIÓN`**: estas features se incluyen en el `_features.md` y en el informe de readiness como visibilidad del backlog, pero no participan del topological sort ni del orden de implementación — no hay spec con dependencias declaradas hasta que se generen. Si otra feature ya generada declara una dependencia sobre una `PENDIENTE_GENERACIÓN`, esa dependencia se reporta como "dependencia hacia feature no generada todavía" (no bloquea readiness de la feature ya generada, pero sí señala al usuario qué generar a continuación).

---

## Paso 7: Formato del informe

Usa `${CLAUDE_SKILL_DIR}/references/readiness_report_template.md` para estructurar el informe.

> **Lo que escribes aquí lo lee una persona, y esa persona no invoca comandos.** Los
> **bloqueantes** y lo que propongas para desbloquearlos van en lenguaje natural, nombrando **la
> acción**: *"responder los gaps que bloquean sus historias"*, *"resolver el conflicto CF-001 con
> F-003"*, *"generar el spec de F-007"* — nunca el workflow que lo hace, ni con barra ni sin ella.
> Estados, IDs y marcadores (`LISTA`, `BLOQUEADA`, `PENDIENTE_GENERACIÓN`, `F-00X`, `CF-001`,
> `[INCOMPLETO]`) **son contrato** y se quedan tal cual.
>
> Medido (pasada 9 de CU-3.a): un nombre de workflow se coló en la "Sugerencia de resolución" de
> este informe teniendo la guía de fase **cargada**. La guía da contexto; esta línea es la
> instrucción.

---

## Paso 8: Escribir el resultado

Path de salida: directorio padre del directorio de features + `<basename>_readiness_report.md`
- El basename se toma del `_features.md` encontrado (ej: si es `prd-hogar-sad_features.md` → `prd-hogar-sad_readiness_report.md`)
- Ejemplo: `docs/prd-hogar-sad_features.md` → `docs/prd-hogar-sad_readiness_report.md`

Antes de escribir, verifica si el archivo ya existe:
- `!test -f "<path>"` — si existe, informa al usuario del path y pregunta: `[sobreescribir | cancelar]`. Continua solo si elige sobreescribir.

Escribe el informe en el archivo correspondiente.

> **Con qué lo escribes, y por qué no con `Write` ([[D-051]]).** El agente que ejecuta esta
> skill tiene `Write` y `Edit` **prohibidos**: es el candado que impide que un auditor
> reescriba lo que audita. Tu informe **sí** lo escribes tú, con redirección por `Bash`
> (`cat > "<path>" <<'EOF' … EOF`). **No le pases la escritura al hilo principal:** el
> informe es tu output, y main no escribe artefactos ([[D-060]]).
>
> Y que quede claro el alcance del candado: con `Bash` disponible, técnicamente nada te
> impide tocar los specs que lees. **No lo haces por norma, no porque no puedas.**

---

## Paso 8.5: Regenerar `_features.md` desde el report

No edites `_features.md` a mano (esta workflow no modifica artefactos — solo lee y sintetiza; el veredicto vive en TU report). `_features.md` es un índice **generado**: el regenerador `sdd-features-index.py` lee tu `## Matriz de readiness` y la usa como **veredicto autoritativo** del estado por feature (anula la derivación marcador-based). Basta con regenerar el índice desde la raíz del proyecto (el directorio que contiene `.sdd/`):

```
python3 .sdd/scripts/sdd-features-index.py <raíz_spec>
```

`<raíz_spec>` es el directorio que contiene `features/` y `_features.md` (el directorio padre del de features, localizado en el Paso 2). El estado y los bloqueantes de cada feature se propagan desde tu report. Si el script no existe:
> "⚠ Falta `.sdd/scripts/sdd-features-index.py`. Re-ejecuta la instalación del ecosistema (`install.sh`) para reponer los scripts de enforcement. `_features.md` no refleja el veredicto de readiness hasta regenerarlo."

---

## Paso 9: Informar al usuario

Informa: path del informe, resumen (N listas de M totales, N bloqueadas por tipo, N `PENDIENTE_GENERACIÓN`). Siguientes pasos según estado, **descritos como acciones que puede pedirte**: si todas listas → **generar el plan técnico** feature a feature, siguiendo el orden por fases del informe; si algunas listas → empezar por las primeras fases; si ninguna → resolver antes los bloqueos que el informe lista; si hay `PENDIENTE_GENERACIÓN` → nombrar esas features por su `F-00X` y ofrecerle **generar sus specs** cuando quiera.
