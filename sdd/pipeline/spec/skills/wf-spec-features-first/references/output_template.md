# Plantilla de salida — Paso 9: Informar al usuario

## Resumen de ejecución

Indica el modo: "Iteración sobre subset `[F-001, F-002, ...]`" o "Generación completa".

| Feature | Origen | Spec | Gaps críticos | Estado |
|---------|--------|------|---------------|--------|
| F-001: [nombre] | Esta iteración | ✓ / ✗ | [N] | [LISTA / BLOQUEADA / REQUIERE_CAMBIO_PRD] |
| F-002: [nombre] | Iteración previa | ✓ | [N] | [LISTA / BLOQUEADA / REQUIERE_CAMBIO_PRD] |
| F-003: [nombre] | — | — | — | PENDIENTE_GENERACIÓN |
| F-004: [nombre] | Iteración previa | ✓ | — | RETIRADA |

## Artefactos

- Discovery: `<path>_discovery.md`
- Features index: `<path>_features.md` (actualizado incrementalmente)
- Specs: `features/<nombre>/spec/<nombre>_spec.md` (recién generados + preexistentes; features planas legacy: sin subcarpeta)
- Conflict report: `<path>_conflict_report.md` (si aplica)
- Readiness report: `<path>_readiness_report.md` (si aplica)

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

**Si hay features `PENDIENTE_GENERACIÓN`:**
> "Quedan [N] features identificadas en el discovery que aún no se han procesado: [lista de
> IDs]. Cuando quieras generarlas, dímelo indicando cuáles."

**Si todo está listo y no hay pendientes** (es decir: los specs están además **validados** —
recién generados no lo están):
> "Todas las features están listas para planificar. Dime por cuál empezamos."
