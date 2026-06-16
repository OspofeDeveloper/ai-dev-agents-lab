# Plantillas verbatim de Caso de Uso

SSoT del formato. Copia el bloque y rellena. No alteres la estructura ni el orden de los campos.

## Bloque de un escenario (`CU-N.x`)

```markdown
### CU-N.x — <escenario de aceptación>
**Precondición:** <estado de partida>.
**Mecanismo:** <skill / subagente / script / hook implicado>.

1. <acción del usuario, en lenguaje natural — NUNCA "ejecuta /wf-x">
   → **Esperado:** <comportamiento del agente · output · artefacto con su path ·
     estado sellado · mensaje literal si aplica>
2. <siguiente acción, si la hay>
   → **Esperado:** <…>

**Resultado:** PASS si <criterio sin ambigüedad> · FALLO si <criterio sin ambigüedad>
**Desviación → reportar:** issue citando `CU-N.x`.
```

### Reglas de relleno

- **Acción del usuario**: lenguaje natural, lo que el usuario *dice*. Prohibido "ejecuta `/wf-x`" — el routing es parte de lo que se verifica.
- **Mecanismo**: único sitio donde aparecen nombres de `wf-*` / subagente / script / hook.
- **Esperado**: qué hace · qué NO hace · artefacto con path · estado sellado · mensaje literal entre comillas.
- **Resultado**: PASS/FALLO sin ambigüedad.
- Para gates en negativo, el `Esperado` debe incluir el prefijo de denegación literal (`[SDD-GATE] <skill>: …`) y "no se crea ningún artefacto".

## Cabecera de un CU nuevo

Solo si el journey no encaja en ningún CU existente. Usa el siguiente `CU-N` libre.

```markdown
# CU-N — <objetivo de usuario>

**Objetivo:** <qué journey cubre, en una o dos frases>.
**Proyecto a usar:** <qué tipo de proyecto real y cómo llegar al estado de partida>.
**Cobertura automática:** <qué parte ya cubre sdd/tests/, si aplica; o "ninguna: depende
de la conducta del agente">.

---

## CU-N.a — <primer escenario>
...
```

Tras crear un CU nuevo, añádelo a la tabla **El catálogo de Casos de Uso** y al **Orden de ejecución sugerido** de `conformance/README.md`.
