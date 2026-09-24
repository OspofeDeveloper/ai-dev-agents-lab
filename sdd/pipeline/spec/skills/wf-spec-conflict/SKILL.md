---
name: wf-spec-conflict
description: "Detecta conflictos entre Specs SDD de un mismo proyecto: HUs duplicadas, CAs contradictorios, scope overlap, shared models inconsistentes."
when_to_use: "Activa en frases como 'verifica conflictos entre specs', 'hay conflictos entre features', 'comprueba si este spec choca con los existentes', 'detecta inconsistencias entre specs'."
argument-hint: "<feature_spec.md> --features-dir <path/features/>"
effort: high
allowed-tools: [Read, Bash]
context: fork
agent: sdd-spec-auditor
user-invocable: true
---

# Workflow: CONFLICT

Tu objetivo es detectar inconsistencias entre los Specs SDD de un mismo proyecto que podrían derivar en comportamiento indefinido, implementación duplicada o gaps funcionales no cubiertos. Usa `kb-conflict-expert` para las 5 reglas de detección y `kb-spec-expert` como referencia estructural.

**Regla de oro:** El informe es informativo, no bloqueante. Tu rol es detectar y describir — la decisión de cómo resolver cada conflicto la toma el humano. El informe siempre debe dejar un estado inequívoco: `SIN_CONFLICTOS` o `CONFLICTOS_DETECTADOS`, **seguido del conjunto sobre el que vale** ([[D-093]]) — un veredicto sin su alcance deja de ser inequívoco en cuanto aparece un spec más. Y en el fan-out, di **desde qué spec** lo miras ([[D-095]]): otro auditor ve el mismo par desde el otro lado y puede levantar lo que tú no viste, y quien arbitra es el informe de readiness.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del spec objetivo**: el primer argumento. Puede ser un `_spec.md` específico o `.` para verificar todos los specs de un directorio.
- **Directorio de features**: el argumento después de `--features-dir`

Si no hay `--features-dir`, intenta inferir el directorio de features como `features/` relativo al directorio del spec objetivo.

Si no hay argumento, informa al usuario:
> "Necesito el spec de la feature y el directorio donde viven las demás, para poder compararlos."

---

## Paso 2: Localizar todos los specs

1. Verifica que el spec objetivo existe.
2. Busca todos los archivos `*_spec.md` dentro del directorio `--features-dir`, cubriendo ambos layouts de feature: `features/*/spec/*_spec.md` (subcarpetas) y `features/*/*_spec.md` (plano legacy).
3. **Descarta los specs de features dadas de baja** ([[D-080]]) — los que llevan `Estado: RETIRADO` en cabecera:

   ```bash
   !for p in <specs encontrados>; do
     e=$(sed -nE 's/^[[:space:]]*[-*>]?[[:space:]]*\*{0,2}Estado:?\*{0,2}[[:space:]]*:?[[:space:]]*(BORRADOR|VALIDADO|RETIRADO).*/\1/p' "$p" | head -1)
     [ "$e" = RETIRADO ] && echo "EXCLUIDO $p"
   done
   ```

   Una feature retirada no se va a implementar, así que un choque contra ella **no es un conflicto**: es ruido que otro auditor tendrá que arbitrar y que puede acabar bloqueando a una feature viva por solaparse con una que ya no existe. **Dilo en el informe** (qué specs excluiste y por qué): excluir en silencio es la otra mitad del fallo. Si el spec **objetivo** es el retirado, no compares nada — informa de la baja con su traza `Retirada:` delante y termina.
4. Si no hay specs en el directorio → informa: "No se encontraron specs en `<features-dir>`. Comprueba la ruta, o genera antes los specs por feature."
5. Si solo hay 1 spec vigente en total (contando el objetivo) → informa: "Solo hay 1 spec. Se necesitan al menos 2 specs para verificar conflictos."

---

## Paso 3: Leer todos los specs

Lee el contenido completo de:
- El spec objetivo
- Todos los specs encontrados en el directorio de features (excluyendo el spec objetivo si ya está incluido)

---

## Paso 4: Inventariar todos los specs

Para cada spec, extrae internamente (no en el output):
- Feature ID y nombre
- Lista de actores
- Lista de HUs con sus IDs, actores y objetivos funcionales
- Lista de CAs con sus IDs, GIVEN/WHEN/THEN y HU padre
- Lista de Journeys con sus pasos principales
- Modelos de dominio mencionados (tanto propios como referenciados como shared)
- Sección Fuera de Alcance

---

## Paso 5: Aplicar las 5 reglas de kb-conflict-expert

Aplica cada regla consultando `kb-conflict-expert` y busca conflictos en **los pares que te tocan**:

> **Qué pares te tocan depende del modo ([[D-096]]).**
> - **Modo feature** (el primer argumento es un `_spec.md`; es el del fan-out): **solo los pares que
>   incluyen tu spec objetivo** —con 5 specs, tu objetivo contra los otros 4—. Los pares entre los
>   demás **no son tuyos**: no los revises ni te pronuncies sobre ellos, ni para decir que están
>   limpios. En el fan-out cada spec nuevo tiene su propio auditor, y los pares entre specs viejos
>   los cubren sus propios informes; esa es la cobertura por pares de la que depende el readiness.
> - **Modo consolidado** (`.` sobre el directorio): **todos** los pares, porque eres el único informe.
>
> Medido en la pasada 2/3 de `CU-3.d` (2026-09-24): de tres auditores en modo feature, uno se ciñó
> a su spec y dos declararon limpios **los 10 pares** — incluido F-003↔F-004, donde el auditor de
> F-004 había levantado un choque ALTA que el arbitraje confirmó. Un auditor que se pronuncia sobre
> un par ajeno con menos atención que su dueño no añade cobertura: añade un falso negativo.

En las reglas de abajo, "los pares" son los de tu modo:

1. **HUs duplicadas**: compara actores + verbos + objetivos en cada par
2. **CAs contradictorios**: compara GIVEN+WHEN de los CAs de cada par; busca THENs incompatibles
3. **Scope overlap**: analiza si los Journeys de una feature incluyen funcionalidad que es el objetivo de otra
4. **Shared models inconsistentes**: inventaría todos los modelos mencionados y cruza sus definiciones/comportamientos
5. **Fuera de alcance contradictorio**: cruza las secciones "Fuera de Alcance" de cada feature con las HUs de las demás

---

## Paso 6: Clasificar cada conflicto detectado

Por cada conflicto:
- Asigna el ID **con el `F-00X` del spec que auditas delante**: `[CF-F001-01]`, `[CF-F001-02]`, …
  (numeración local, empezando en `01`). En modo consolidado (`.` sobre el directorio) el informe
  es uno solo y no hay con quién colisionar: ahí numeras `[CF-01]`, `[CF-02]`, …
- Asigna la severidad según `kb-conflict-expert`: ALTA o MEDIA
- Describe qué features están involucradas
- Cita las secciones exactas en conflicto
- Sugiere una posible resolución (sin imponer — es una sugerencia)

> **El prefijo no es estética: casi nunca corres solo ([[D-090]]).** En el fan-out del Paso 7 de
> `wf-spec-features-first` hay un auditor por spec nuevo, cada uno escribiendo su propio informe y
> ninguno viendo lo que numeran los demás. Con numeración local a secas, la primera colisión es
> **segura**: medido en la pasada de `CU-3.d` del 2026-09-18, **tres hallazgos distintos** llamados
> `CF-002` por tres auditores, más un `CF-001` de una tanda anterior que era otra cosa. Y el daño
> no es cosmético — quien consolida (la medición de readiness) y quien decide *"manda F-001 en este
> choque"* citan el ID: con dos hallazgos homónimos, la decisión aterriza en el equivocado. El
> `F-00X` delante lo resuelve **sin coordinación**: cada auditor ya sabe qué spec audita, así que
> no hace falta que nadie reparta bloques antes de lanzar.

> **Lo que escribes aquí lo lee una persona, y esa persona no invoca comandos.** La
> **Sugerencia de resolución** va en lenguaje natural y nombra **la acción**, no el workflow que
> la ejecuta: *"formalizar el cambio en el PRD antes de seguir"*, no *"lanzar `wf-prd-change`"*;
> *"pedir que se aclare el CA-004"*, no *"ejecutar `wf-spec-amend`"*. Los IDs y los veredictos
> (`CF-F001-01`, `ALTA`, `SIN_CONFLICTOS`) **sí** se quedan: los parsean los gates.
>
> Medido (pasada 9 de CU-3.a): **2 de los 4** nombres de workflow que se colaron en artefactos
> salieron justo de este campo, con la guía de fase **cargada**. Por eso la norma está aquí y no
> solo allí: la guía es contexto de fase, y esto es tu instrucción de rol.
>
> **Y vale igual para el nombre de una kb, que es por donde se escapa aquí ([[D-091]]).** Al
> justificar un veredicto lo natural es citar la fuente —*"Regla 4 de `kb-conflict-expert`"*,
> *"la tabla de severidad de `kb-conflict-expert`"*— y la fuente tiene nombre de skill. Cita la
> regla **por lo que dice**: *"el mismo modelo con comportamientos distintos en dos CAs de
> features diferentes"*, *"un shared model inconsistente es ALTA por defecto"*. Medido en la
> pasada de `CU-3.d` del 2026-09-18: las **tres** líneas que levantó el probe V1 eran de esta
> forma, dos en el informe de readiness y una aquí. Quien lee el informe no sabe qué es una kb
> ni tiene por qué: el veredicto se sostiene solo con la regla enunciada.

Si no se detecta ningún conflicto → prepara un informe breve con estado `SIN_CONFLICTOS`, indica explícitamente que el número de conflictos ALTA y MEDIA es `0`, y conserva el inventario de comparaciones realizadas.

---

## Paso 7: Formato del informe

Usa `${CLAUDE_SKILL_DIR}/references/conflict_report_template.md` para estructurar el informe.

> **Declara en la cabecera contra qué conjunto comparaste ([[D-090]]).** El campo
> `Conjunto comparado` lista los `F-00X` de **todos** los specs que entraron en la comparación —el
> objetivo incluido— y los retirados que excluiste. No es trazabilidad de adorno: un informe de
> conflictos es válido **para el conjunto que tenía delante**, y en la iteración por subsets ese
> conjunto crece en cada tanda. Sin el campo, un informe calculado contra 2 specs es
> indistinguible de uno calculado contra 5, y quien lo consolida lo da por vigente. Medido en la
> pasada de `CU-3.d` del 2026-09-18: los informes de la primera tanda describían un universo de
> **2** specs y se leyeron junto a los de una de **5**, sin que nada en el fichero lo dijera.

> **Y el veredicto se enuncia sobre lo que comparaste, no en absoluto ([[D-093]]/[[D-096]]).** En
> modo feature, `SIN_CONFLICTOS (F-002 contra los otros 4 specs: F-001, F-003, F-004, F-007)` —con
> un solo spec más, `(F-003 contra el otro spec: F-004)`—; en
> modo consolidado, `SIN_CONFLICTOS (entre los 5 specs comparados: …)`. Nunca `SIN_CONFLICTOS` a
> secas, y en modo feature nunca *"entre los N"*: se lee como *"revisé todos los pares"*, y no
> los revisaste. El token va delante y
> **literal** —lo parsea la medición de readiness—; el conjunto va detrás, entre paréntesis.
> Medido en la pasada del 2026-09-21, ya con la cabecera `Conjunto comparado` puesta: el informe de
> `gestion-categorias` abría con **SIN_CONFLICTOS** mientras esa misma feature aparecía en un
> hallazgo `MEDIA` del informe de `cuentas-y-tarjetas`, generado una tanda después. La vigencia
> estaba escrita en la cabecera y el veredicto seguía sin llevarla — y quien abre el informe de una
> feature **empieza por su portada**, no por el readiness que lo clasifica.

---

## Paso 8: Escribir el resultado

Determina el path de salida:
- Si se verificó un spec específico: mismo directorio del spec objetivo + `<nombre_base>_conflict_report.md`
  - Ejemplo: `features/auth/spec/auth_spec.md` → `features/auth/spec/auth_conflict_report.md`
- Si se verificaron todos los specs del directorio: **directorio padre** del de features —la raíz de
  artefactos del proyecto, donde ya viven `_features.md` y `_readiness_report.md`— con el mismo
  `<nombre_base>` que ellos: `<nombre_base>_conflict_report.md`.
  - Ejemplo: `docs/features/` junto a `docs/prd_features.md` → `docs/prd_conflict_report.md`
  - Si no hay `*_features.md` del que tomar el nombre, usa el basename del directorio padre.

> **El consolidado va fuera de `features/`, y no es cosmético.** Aquí ponía
> `features/_conflict_report.md`, **dentro** del directorio — y el único consumidor de este informe,
> la medición de readiness, busca el consolidado en el padre (donde están los demás artefactos de
> proyecto) y el resto por feature en `features/*/spec/`. Ni uno ni otro alcanza la raíz de
> `features/`: el informe se escribía donde nadie lo lee, y como la ausencia de informe solo produce
> una advertencia **no bloqueante**, el readiness se declaraba "sin análisis de conflictos" teniendo
> uno en disco. Es el mismo modo de fallo que [[D-047]] arregló para el fan-out por feature, en la
> otra rama del mismo paso.

**Si ya existe, sobreescríbelo sin preguntar ([[D-064]]).** Un informe de conflicto es un artefacto
**derivado**: no guarda ninguna decisión humana dentro, y quien lanza el flujo lo regenera en
cada pasada. Un gate aquí no protegería nada — y, siendo `context: fork`, tampoco podrías
presentarlo. Lo que sí haces es **decir en tu informe que lo reemplazaste**.

Escribe el informe en el archivo correspondiente.

> **Con qué lo escribes, y por qué no con `Write` ([[D-051]]).** El agente que ejecuta esta
> skill tiene `Write` y `Edit` **prohibidos**: es el candado que impide que un auditor
> reescriba lo que audita. Tu informe **sí** lo escribes tú, con redirección por `Bash`
> (`cat > "<path>" <<'EOF' … EOF`). **No le pases la escritura al hilo principal:** el
> informe es tu output, y main no escribe artefactos ([[D-060]]; [[D-031]] es la mitad de leer).
>
> Y que quede claro el alcance del candado: con `Bash` disponible, técnicamente nada te
> impide tocar el spec auditado. **No lo haces por norma, no porque no puedas.** Auditas y
> reportas; corregir el spec es de `wf-spec-delta` o `wf-spec-amend`.

---

## Paso 9: Informar al usuario

- Path del informe generado
- Resumen: estado general (SIN_CONFLICTOS o CONFLICTOS_DETECTADOS)
- Si hay conflictos: cuántos de severidad ALTA y cuántos MEDIA
- Siguiente paso:
  - Sin conflictos: "No he encontrado choques entre estos specs." **No prometas planificación** ([[D-077]]/[[D-082]]): que no haya conflictos no hace fiable un spec — el gate de planificación exige además que esté **validado**, y un spec recién generado nace en borrador. Si ves que alguno sigue sin sellar, ofrécete a validarlo.
  - Con conflictos ALTA: "Hay [N] choques de severidad alta entre features. Dime qué feature manda en cada uno y **aplico el cambio sobre el spec que toque**; luego vuelvo a revisarlo." **No le mandes editar los specs a mano** ([[D-082]]): un spec editado fuera de las vías de evolución conserva su sello `VALIDADO` aunque su contenido ya no sea el que se auditó, y el gate de planificación lo deja pasar — la corrección tiene que reabrir la validación, y eso solo pasa si la aplica quien sabe desellar. Descríbeselo como acción, sin nombrar el workflow.
