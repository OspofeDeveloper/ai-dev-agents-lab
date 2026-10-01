# Plantilla de salida — Paso 9: Informar al usuario

## Resumen de ejecución

**[Iteración sobre el subset `[F-001, F-002]` | Generación completa]** · rigor [Standard | Ligero]

<!-- Esa línea va la PRIMERA del mensaje, copiada con los valores de esta pasada, en cada tanda
     (D-099/D-101). No la sustituyas por una frase ("He generado las specs de…"): es lo que dice qué
     ha hecho *esta* pasada, y como instrucción se perdió en la primera tanda de la corrida 2. -->

| Feature | Origen | Spec | Gaps críticos | Estado |
|---------|--------|------|---------------|--------|
| F-001: [nombre] | Esta iteración | ✓ / ✗ | [N] | [LISTA / BLOQUEADA / REQUIERE_CAMBIO_PRD] |
| F-002: [nombre] | Iteración previa | ✓ | [N] | [LISTA / BLOQUEADA / REQUIERE_CAMBIO_PRD] |
| F-003: [nombre] | — | — | — | PENDIENTE_GENERACIÓN |
| F-004: [nombre] | Iteración previa | ✓ | — | RETIRADA |

## Artefactos

- Discovery: `<path>_discovery.md`
- Features index: `<path>_features.md` (actualizado incrementalmente)
- Specs, **una línea por cada spec del índice** —los de esta tanda y los de tandas anteriores—, con
  su ruta completa:
  - `features/<nombre>/spec/<nombre>_spec.md` (esta tanda)
  - `features/<nombre>/spec/<nombre>_spec.md` (tanda anterior)
- Informes de conflictos, uno por línea y con su ruta completa (los de tandas anteriores, marcados así)
- Readiness report: `<path>_readiness_report.md` (si aplica)

<!-- Rutas que se pueden abrir: nada de llaves ni comodines (`{a,b}/spec/<nombre>_spec.md`).
     Medido en la corrida 3 de CU-3.c (D-103): la segunda tanda listó solo sus 4 specs, con llaves,
     y dejó fuera los 2 de la tanda anterior. -->

> **La lista va completa en cada tanda, no solo en la primera ([[D-099]]).** En la segunda y
> siguientes también el discovery y **los informes de conflictos de esta tanda, con su ruta**
> (uno por feature junto a su spec): es donde está el detalle de los conflictos que el resumen
> cita. Medido en la tanda A (2026-09-25/28): los dos resúmenes de primera tanda listaban todo; los
> dos de segunda tanda dejaron fuera el discovery y los informes de conflictos, justo cuando traían
> un conflicto ALTA.

## Siguientes pasos (bloques condicionales)

> **Estos mensajes los lee el usuario, así que van en lenguaje natural.** No le des nombres de
> workflow ni comandos con flags: el ecosistema se conduce **hablando**, y quien construye los
> argumentos —con sus validaciones— eres tú, no él. Un comando surfaceado invita a teclearlo a
> mano y a saltarse esa construcción.

**Si hay features con gaps `[CRÍTICO]`:**
> "Las siguientes features tienen gaps críticos sin resolver: [lista]. Responde los gaps
> marcados como _(pendiente)_ en `<path>_analysis.md` y pídeme que **complete las historias
> incompletas** de esas features."

**Si se usó `_analysis.md` con gaps `[CRÍTICO]` sin responder:**
> "Hay [N] gaps críticos del análisis previo que no fueron respondidos. Los specs afectados
> tienen HUs marcadas `[INCOMPLETO]`, y eso **bloquea el paso a planificación**. Responde los
> gaps en `<path>_analysis.md` y dímelo para retomarlo."

**Si hay conflictos de severidad ALTA:**
> "Se detectaron conflictos entre features. Están en `<path>_conflict_report.md`: léelo, dime
> qué feature manda en cada choque y **aplico el cambio sobre el spec que toque** — cada
> corrección reabre su validación, así que después los revalidamos."

> Ofrecer el cambio, y no *"edítalos tú"*, es deliberado ([[D-082]]): un spec editado a mano
> conserva su sello aunque su contenido ya no sea el auditado, y el gate de planificación lo
> deja pasar.

**Si el subset incluía features dadas de baja:**
> "Estas features ya no están en el producto: [lista con su `CR-XXX`]. No les he tocado el
> spec. Si alguna vuelve al alcance, dímelo y la recupero — volvería en borrador, para
> validarla otra vez."

> No se pisan ni se saltan calladas ([[D-080]]): su `F-00X` sigue en el discovery, que no se
> regenera, así que aparecerán en cada pasada posterior mientras el mapa no cambie.

**Si hay features `BLOQUEADA` por «pendiente de validación» (el caso normal de una pasada recién generada):**
> "Los specs recién generados quedan en borrador, sin auditar: [lista]. Cuando quieras los
> valido —de uno en uno o de golpe— y, ya sellados, pasamos a planificar."

> Esto sale **siempre** tras generar specs nuevos y no es un problema: un spec nace en
> `Estado: BORRADOR` ([[D-061]]) y la validación es un gate humano que registra **quién**
> aprueba ([[D-065]]), así que no se puede auto-resolver aquí. Lo que no vale es callarlo:
> hasta [[D-077]] esta plantilla saltaba de "generadas" a "pueden avanzar a planificación" y
> el paso que falta solo aparecía como una denegación, dos pasos después.

**Si hay features LISTA:**
> "Las features marcadas como LISTA pueden avanzar a planificación: [lista]. Dime cuál quieres
> planificar —o si prefieres empezar por todas— y me encargo."

**Si todo está listo y no hay pendientes** (es decir: los specs están además **validados** —
recién generados no lo están):
> "Todas las features están listas para planificar. Dime por cuál empezamos."

## Cierre: el siguiente pendiente ([[D-102]])

Después de los bloques de arriba, ejecuta `sdd-project-status.py <raíz_spec> --spec-pending --json` y
cierra con **"Quedan N pendientes"** y un `AskUserQuestion` sobre el primero, según la tabla de
seguimiento de la guía de la fase. Los bloques de siguientes pasos explican; la pregunta es la que
hace avanzar.

> **Las features sin generar no llevan bloque propio** ([[D-103]]): son un pendiente más de la lista
> y salen en ella. Un *"Quedan N features sin spec, dime cuáles"* justo antes de *"Quedan N
> pendientes"* dice lo mismo dos veces —medido en las dos tandas de la corrida 3 de `CU-3.c`—.
