---
name: kb-sdd-conformance
description: "SSoT del metodo de conformidad del ecosistema SDD: como derivar y escribir escenarios de Caso de Uso (CU-N.x) para una skill, el template verbatim del escenario, los 4 ejes de cobertura (happy/edge/harness/args), el formato de la matriz del ROADMAP y su ciclo de estados, y el protocolo de validacion de conducta no determinista (>=3 corridas, determinista vs conductual, recalibracion del contrato). No cubre el catalogo de CU en si (vive en conformance/casos-de-uso) ni la arquitectura de skills (kb-sdd-skill-architecture)."
effort: high
allowed-tools: [Read, Bash]
user-invocable: false
---

# KB SDD Conformance

Usa esta knowledge base como SSoT cuando haya que **auditar la cobertura de conformidad** de una `wf-*` del ecosistema y **escribir los escenarios de Caso de Uso que falten**. Codifica el método que hasta ahora se ejercía a mano: leer un `SKILL.md` → cruzarlo con los Casos de Uso existentes → derivar los 4 ejes → escribir solo los huecos en formato verbatim → actualizar la matriz del ROADMAP.

El **catálogo** de Casos de Uso vive en `conformance/casos-de-uso/cu-*.md` (la SSoT del "qué debería pasar"); la **matriz de cobertura** vive en `conformance/ROADMAP.md`. Esta KB define **cómo se producen y mantienen**, no su contenido.

> No confundir con la fase QA del pipeline de producto (`wf-qa-plan`/`wf-qa-verify`, que derivan TC-XXX desde los CAs de un *spec de feature*). Aquí el "producto bajo prueba" es **el propio ecosistema SDD**: cada CU es un Criterio de Aceptación observable del sistema, verificable sin leer código.

---

## Regla 1: El esquema de identificadores

- **`CU-N`** — un Caso de Uso orientado a un **objetivo de usuario**, no a un comando (ej. `CU-1 — Inicializar un proyecto SDD`). Vive en un fichero `cu-0N-<slug>.md`.
- **`CU-N.x`** — un **escenario de aceptación** dentro del CU (`a`, `b`, `c`…). Es la **unidad citable** en incidencias.
- Los IDs **no se reutilizan**: si un escenario se retira, su letra queda libre pero no se reasigna (igual que los CAs de un spec). Al añadir escenarios nuevos, continúa la secuencia de letras existente en ese fichero — **nunca** reinsertes una letra ya usada.
- Antes de cerrar, **verifica unicidad** de IDs nuevos:
  ```bash
  grep -oE 'CU-[0-9]+\.[a-z]+' conformance/casos-de-uso/cu-0N-*.md | sort | uniq -d
  ```
  Cualquier salida = ID duplicado → renombra antes de cerrar.

## Regla 2: El template verbatim del escenario

Cada escenario se escribe **exactamente** con esta forma (ver `references/cu_template.md` para el bloque copiable):

```markdown
### CU-N.x — <escenario de aceptación>
**Precondición:** <estado de partida>.
**Mecanismo:** <skill / subagente / script / hook implicado>.

1. <acción del usuario, en lenguaje natural — NUNCA "ejecuta /wf-x">
   → **Esperado:** <comportamiento del agente · output · artefacto con su path ·
     estado sellado · mensaje literal si aplica>
2. …

**Resultado:** PASS si <…> · FALLO si <…>
**Desviación → reportar:** issue citando `CU-N.x`.
```

Convenciones inviolables:

- **Acción del usuario en lenguaje natural.** Nunca "ejecuta `/wf-x`": el routing es parte de lo que se verifica (ver CU-11/CU-13). Se escribe lo que el usuario *dice* ("pídele que genere las tasks sin validar el plan"), no el comando.
- **El bloque `Mecanismo`** hace explícito qué skill se invoca, qué subagente la ejecuta y qué script/hook participa. Es el único sitio donde aparecen nombres de `wf-*`/agente/script.
- **`Esperado`** describe qué hace, **qué NO hace**, el artefacto con su path y el **mensaje literal** cuando aplica (entre comillas).
- **`Resultado`** da el criterio PASS/FALLO sin ambigüedad.
- **`Desviación → reportar`** cierra siempre citando el ID propio del escenario.

## Regla 3: Los 4 ejes de cobertura

Toda `wf-*` debe quedar cubierta en cuatro ejes. Para derivarlos, **lee su `SKILL.md`** y mapea sus señales:

| Eje | Qué verifica | Cómo se deriva del `SKILL.md` |
|---|---|---|
| **Happy** | Invocación canónica con precondiciones satisfechas → artefacto correcto + sello. | El "Paso 1…N" feliz del skill: su input canónico y su output declarado (qué archivo escribe y dónde). |
| **Edge** | Args parciales/ausentes, layout legacy plano, subset `--features`, idempotencia, re-ejecución, monorepo. | Flags opcionales, ramas de parseo, defaults, y los modos alternativos del skill (`analyze\|apply`, `discover\|generate`). |
| **Harness** | Invocar **saltándose** una precondición o gate → debe **bloquear** (`[SDD-GATE]`, veredicto no-`LISTO`, parada por gap crítico). Se prueba **en negativo**. | Las precondiciones/gates que el skill declara (gate de plan validado, spec fiable, QA APTO, parada por `[CRÍTICO]`). Por cada gate, un escenario que pide saltárselo. |
| **Args OK** | El orquestador traduce el lenguaje natural a los **args correctos** y **no** inyecta overrides peligrosos sin petición explícita. | Los flags peligrosos (`--allow-open-critical-gaps`, `--all-features`, `--force`, `--allow-derived-scope-from-analysis`) y los paths/modos que deben construirse a partir de lo que el usuario dice. |

Un eje puede marcarse `—` (no aplica) con justificación: p. ej. **Args OK** no aplica a un skill de **arg único posicional** sin overrides; **Harness** no aplica si el skill no tiene precondición que saltarse.

## Regla 4: La matriz del ROADMAP

`conformance/ROADMAP.md` invierte la vista del catálogo: **una fila por `wf-*`**, en orden de pipeline, agrupada por fase. El formato de fila (ver `references/roadmap_format.md` para la cabecera y leyenda copiables):

```
| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
```

- **Ejes** se marcan `✅` cubierto · `🟡` parcial · `❌` hueco · `—` no aplica.
- **CU que lo ejercitan** lista los `CU-N.x` (separados por `·`) que tocan esa skill. Es la trazabilidad skill→escenarios.
- **Estado** sigue el ciclo de la Regla 5.
- **Huecos detectados** anota en una frase qué falta o por qué un eje es `🟡`/`—`. Cuando un eje parcial se cubre vía un escenario transversal (p. ej. "`--force` cubierto vía CU-11.f"), se anota aquí.

> La matriz referencia skills **por nombre**, nunca por ruta de fichero → es agnóstica al layout físico del árbol fuente.

## Regla 5: El ciclo de estados de una fila

```
PENDIENTE → REVISADO → CON-HUECOS → COMPLETADO
```

- **PENDIENTE** — la fila existe pero la skill no se ha cruzado contra el catálogo.
- **REVISADO** — cruzada, **sin huecos**: los 4 ejes están `✅` o justificadamente `—`. No requiere escribir escenarios nuevos.
- **CON-HUECOS** — cruzada y se detectó al menos un eje `🟡`/`❌` que exige escenarios nuevos.
- **COMPLETADO** — los huecos detectados se rellenaron con escenarios escritos en el `cu-NN` correcto.

Una skill puede ir de `PENDIENTE` directo a `REVISADO` si no tiene huecos. Solo pasa por `CON-HUECOS` si hubo algo que escribir.

## Regla 6: El contador de progreso

La sección **Progreso** del ROADMAP mantiene un contador agregado que **debe cuadrar** con la suma de estados de las filas:

```
**Revisadas: X / N** ✅ · Completadas: C · Revisadas sin huecos: R · Con huecos: H · Pendientes: P
```

donde `Revisadas = Completadas + Revisadas-sin-huecos`, y `Completadas + Revisadas-sin-huecos + Con-huecos + Pendientes = N` (total de `wf-*` del core). Tras tocar cualquier fila, **recalcula el contador** y verifica que cuadra contando los estados reales:

```bash
grep -cE '\| COMPLETADO \|' conformance/ROADMAP.md
grep -cE '\| REVISADO \|' conformance/ROADMAP.md
grep -cE '\| CON-HUECOS \|' conformance/ROADMAP.md
grep -cE '\| PENDIENTE \|' conformance/ROADMAP.md
```

## Regla 7: El método, paso a paso

Para auditar una skill y rellenar sus huecos:

1. **Lee el `SKILL.md`** de la skill objetivo (frontmatter + pasos + precondiciones/gates + flags).
2. **Cruza con el catálogo**: localiza su fila en `ROADMAP.md` (columna *CU que lo ejercitan*) y abre los `cu-NN-*.md` que la tocan. Lee qué escenarios ya existen.
3. **Clasifica por eje** (Regla 3): para cada uno de los 4, decide si está cubierto, parcial o ausente con lo ya escrito.
4. **Escribe SOLO los huecos**: por cada eje `❌`/`🟡` que lo merezca, redacta un escenario nuevo en formato verbatim (Regla 2), en el `cu-NN` temáticamente correcto, continuando la secuencia de letras (Regla 1).
5. **Actualiza la fila del ROADMAP**: marca los ejes, añade los nuevos `CU-N.x` a *CU que lo ejercitan*, mueve el **Estado** según la Regla 5 y anota *Huecos detectados*.
6. **Recalcula el contador** (Regla 6) y **verifica unicidad de IDs** (Regla 1, el `grep` de duplicados).

## Regla 8: Dónde escribir cada escenario

Un escenario va al `cu-NN` cuyo **journey/tema** coincide, no al de la fase de la skill por defecto. Guía:

- Happy/edge/harness propios de una fase → el CU de esa fase (prd→CU-2, spec→CU-3, design→CU-5, plan/tasks/qa/release→CU-6, mantenimiento→CU-8…).
- Gate **en negativo** (anti-alucinación) → **CU-9**.
- Disparador NL → skill correcto (Args OK de routing) → **CU-13** (matriz de enrutado), con apoyo de CU-11.
- Pedir una fase sin su prerequisito → **CU-14** (secuenciación).
- Skills **meta** (autoría del ecosistema) → **CU-17**, con su routing en CU-13.h.

Si un escenario no encaja en ningún CU existente y es un journey nuevo, ese es un CU nuevo (Regla 1): asigna el siguiente `CU-N` libre y créalo con la cabecera estándar del catálogo (objetivo · proyecto a usar · cobertura automática).

## Regla 9: Protocolo de validación de conducta no determinista

Las Reglas 1-8 dicen **cómo escribir** los escenarios. Esta dice **cómo ejecutarlos y cuándo confiar en el veredicto** — porque el "producto bajo prueba" es software gobernado por IA: buena parte de los CU los juzga un agente, y **su veredicto no es repetible**. Aplica al **validar** un CU (ejecutarlo y marcar PASS/FALLO), no al escribirlo.

1. **Determinista vs conductual — decláralo.** Separa lo que verifica una **máquina** (script, `grep`, la suite `run-tests.sh` → repetible, lo cubre CI) de lo que juzga el **agente** (→ no repetible, CI **no** lo cubre). En la nota de validación di cuál es cuál. La capa determinista de un CU es su ancla; la conductual es la que exige el resto de esta regla.

2. **≥3 corridas para todo veredicto conductual.** Un PASS único puede ser suerte del muestreo, y un FALLO único, un despiste. Ejecuta el CU **al menos 3 veces** —variando la frase, no repitiéndola literal, para descartar caché conversacional— antes de sellar PASS. Excepción: un **FALLO reproducible** con 1-2 corridas ya basta para parar y reportar (no necesitas 3 para documentar algo que falla siempre). *Aprendido: CU-2.d se saltó un gate 2/2 de forma razonada; CU-2.c prueba 2 colapsó en un gate adyacente y no aisló lo que creía probar — una sola corrida habría engañado en cualquier dirección.*

3. **Registra la procedencia** en la nota de validación del `cu-NN`: **fecha**, **modelo** usado, **proyecto consumidor** real y **versión del ecosistema** instalada. La conducta deriva entre versiones de modelo y de ecosistema → una validación sin esos datos **caduca en silencio** (no se sabe si sigue vigente).

4. **Recalibración, no maquillaje.** Si un CU marca **FALLO** una conducta que, mirada de cerca, es **razonable**, el defecto suele estar en el **contrato del CU**, no en el agente. Entonces: corrige el CU **y** registra la decisión (`D-NNN` en `DECISIONS.md`) que lo justifica — **nunca** relajes el criterio en silencio para forzar el verde. Es el análogo de la regla `DIVERGENTE` de QA (un test que falla contra un CA no se ajusta, se investiga). *Aprendido: D-024 recalibró CU-2.d de "siempre pregunta" a ponderado-por-riesgo tras ver que la conducta del agente era correcta.*

5. **Congela la frase que falló.** Cuando un bug conductual motiva un cambio, el **prompt exacto** que lo destapó se convierte en un sub-caso permanente (Regla 1/2) → esa regresión no vuelve en silencio. Cada bug encontrado es cobertura nueva.

6. **Valida la rama protectora, no solo el happy.** Cuando el comportamiento correcto es *bloquear/avisar/parar*, no basta ver que el gate salta: verifica también que **la vía de escape hace lo que promete** (declinar deja el artefacto intacto, cancelar no escribe, etc.). *Aprendido: en D-024 había que ver que "Conservar el actual" dejaba el PRD sellado intacto, no solo que el aviso aparecía.*

> Esta regla es la SSoT que referencia la plantilla de PR (`docs/MEJORAS_FUTURAS.md` O-6): la sección "Impacto conductual" de un PR se rellena aplicando los puntos 1-3 y 6.

## Regla de oro

> Escribe el escenario que un humano pueda **ejecutar hablando** sobre un proyecto real y comparar contra su `Esperado` sin leer código. Si no puedes redactar su criterio PASS/FALLO sin ambigüedad, el hueco aún no está listo para escribirse — lee más el `SKILL.md` primero.
