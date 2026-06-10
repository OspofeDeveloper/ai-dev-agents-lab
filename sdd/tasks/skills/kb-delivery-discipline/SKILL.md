---
name: kb-delivery-discipline
description: "Criterios stack-agnósticos de empaquetado del trabajo implementado en commits y PRs: la Task como unidad de trabajo (un commit atómico y verde por task), los tests viajando en la misma unidad/PR que el código que cubren, y la división de features grandes en cadenas de PRs apilados a lo largo de las fronteras de dependencia. Carga cuando se decide cómo agrupar cambios para commit o revisión. NO cubre la descomposición de tasks ni el orden por dependencias (kb-tasks-method, kb-tasks-expert), ni el tagging/coordenada de release (kb-traceability-rules Regla 11, wf-release)."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Delivery Discipline — Empaquetado de trabajo en commits y PRs

Criterios **normativos y stack-agnósticos** para empaquetar el trabajo ya implementado en
commits y Pull Requests. No definen *qué* implementar (eso es el spec/plan) ni *cómo*
descomponer el trabajo en tasks (eso es `kb-tasks-method` y `kb-tasks-expert`): definen
*cómo se agrupa lo implementado* para que el historial sea atómico y la revisión sea
posible.

> Esta KB no cambia el commit-por-task que aplica `wf-task-run`: añade el *porqué* y los
> criterios de empaquetado por encima de él. La SSoT de la descomposición, el orden por
> dependencias y el formato de task vive en `kb-tasks-method` / `kb-tasks-expert`; aquí se
> referencia, no se reescribe.
>
> Fuera de alcance: el tagging y la coordenada de release (vincular el cierre de una feature
> a un commit SHA / tag) — su SSoT es `kb-traceability-rules` Regla 11, materializada por
> `wf-release` / `sdd-release.py`. Esta KB cubre cómo se empaquetan los commits y PRs; no el
> punto de entrega a producción.

---

## La unidad de trabajo es la Task

La **unidad de empaquetado por defecto es una Task** (la unidad mínima de implementación
delegable de `kb-tasks-expert`). Un commit por task, atómico y verde. `wf-task-run` (Paso 8)
ya lo aplica; esta sección reafirma el *porqué* sin redefinir la mecánica.

Un commit-unidad bien formado cumple:

| Criterio | Qué significa |
|---|---|
| **Una sola intención** | El commit materializa una task coherente — un componente o cambio cohesivo, no un cajón de sastre de cambios sueltos |
| **Verde** | Build y tests del módulo afectado pasan. Excepción única: una task de test TDD en estado RED-by-design (el test compila y falla a propósito porque la implementación aún no existe — ver `kb-tasks-method` paso 5) |
| **Incluye el estado** | La actualización del `_tasks.md` (campo `Estado` + tabla `## Progreso`) viaja en el mismo commit que el código de la task |
| **Mensaje trazable** | `T-00X: <título> [CA-XXX]`. El `CA-XXX` sale del campo `Spec CA`; si es `—`, se omite el sufijo |

**Qué entra en el commit y qué no:**

- **Entra:** solo lo que la task tocó — los archivos del componente y su actualización de
  estado en `_tasks.md`.
- **No entra:** cambios ajenos a la task presentes en el working tree (déjalos fuera y
  avísalo). Refactors oportunistas de código que la task no toca. Cambios de otra task.
- **Nunca `git add -A` indiscriminado:** se añade el conjunto explícito de archivos de la
  task. Un `add` masivo arrastra ruido ajeno y rompe la atomicidad del commit-unidad.

Un commit que mezcla dos intenciones no es una unidad: es dos unidades mal empaquetadas.
Si un cambio coherente no cabe en una sola task, el problema está aguas arriba (la
descomposición), no en el commit — vuelve a `kb-tasks-method`.

---

## Tests junto al código

Los tests que cubren un cambio viven en la **misma unidad de trabajo / mismo PR que el
código que cubren**. Nunca se difieren a un commit, PR o sprint posterior de "añadir tests
luego".

**Principio duro:** ningún PR mergea código de producción cuyos tests aterrizan en otro PR.
Un PR de producción sin sus tests es un PR incompleto, no un PR pequeño.

Reconciliación con el orden TDD (definido en `kb-tasks-method` paso 5 — aquí se referencia,
no se redefine): la task de test (RED, `Layer: test`) precede a la task de implementación
(GREEN) que la valida y aparece en sus `Dependencies`. Esas dos tasks son **commits
adyacentes en la misma rama** y, cuando se agrupan en un PR, viajan **en el mismo PR**:
juntos forman la unidad cobertura+código. El commit RED es verde-by-design (el test falla a
propósito); el commit GREEN lo pone en verde real. Separar la pareja RED/GREEN entre PRs
distintos viola este criterio.

Esto aplica igualmente al fix de un bug: el fix y su test de regresión van en la misma
unidad (ver `wf-bug`).

---

## Chained / stacked PRs

Cuando el conjunto de tasks de una feature es **demasiado grande para un solo PR
revisable**, se divide en una **cadena de PRs apilados** (cada uno basado en el anterior),
en lugar de un único PR gigante o un PR por commit sin estructura.

Es coherente con "una feature por rama" (ROADMAP 5.4): la cadena de PRs vive dentro de la
rama de la feature; cada PR de la cadena es un tramo revisable de esa misma feature.

**Dónde cortar la cadena** — a lo largo de las **fronteras de dependencia** que define
`kb-tasks-method` (mismo orden canónico; aquí solo se reutiliza como costura de corte):

| PR de la cadena | Contenido | Por qué es una costura natural |
|---|---|---|
| 1. Contratos y modelos | Tipos, interfaces, contratos, modelos de dominio | Nada depende de código aún inexistente; base estable sobre la que apilar |
| 2. Implementaciones | Lógica que materializa los contratos (+ sus tests) | Depende solo del PR 1, ya mergeable y revisable |
| 3. Integración / wiring | Composición, DI, configuración transversal, bordes de plataforma | Depende de las implementaciones del PR 2 |
| 4. UI / superficie | Pantallas, vistas, endpoints, superficie de salida | Depende de la integración del PR 3 |

Criterios de corte:

- **Costura de dependencia:** corta donde un bloque deja de necesitar el siguiente para ser
  coherente. Un PR que no compila sin código de un PR posterior está mal cortado.
- **Tamaño revisable:** cada PR debe poder revisarse en una sesión razonable. Si un tramo
  (p. ej. todas las implementaciones) sigue siendo enorme, subdivídelo por sub-bloque de
  dependencia, no por número de líneas arbitrario.
- **Cada PR verde e independiente:** cada eslabón compila, pasa sus tests y lleva los tests
  del código que introduce (ver "Tests junto al código"). Un eslabón no puede depender de
  tests que llegan en un eslabón posterior.

**Este criterio es ADVISORY, no enforcement mecánico.** No hay script que parta PRs
automáticamente ni gate que lo rechace: es una guía de juicio para quien empaqueta la
entrega. Una feature pequeña cabe en un solo PR y no necesita cadena.

---

## Relación con lo existente

- **No cambia el commit-por-task de `wf-task-run`** (Paso 8): ese sigue siendo el mecanismo.
  Esta KB añade los criterios de empaquetado *por encima* — el porqué del commit atómico y
  el caso de las features grandes que requieren una cadena de PRs.
- **No redefine la descomposición ni el orden:** `kb-tasks-method` (proceso) y
  `kb-tasks-expert` (formato y orden canónico) son la SSoT. Las fronteras de dependencia que
  esta KB usa como costuras de corte salen de ahí.
- **Stack-agnóstico por diseño.** Un overlay de stack puede añadir puntos de corte
  adicionales (p. ej. por módulo Gradle, por target de plataforma) sobre estos criterios
  genéricos. Esta KB no los implementa: deja la extensión como posibilidad del overlay, que
  especializa sin contradecir el criterio base.

> Regla de oro: el historial cuenta una intención por commit, y ningún código de producción
> se mergea sin los tests que lo cubren en la misma unidad de revisión.
