# Formato de la matriz del ROADMAP de conformance

SSoT del formato de `conformance/ROADMAP.md`. La matriz es **una fila por `wf-*`** del core, agrupada por fase, en orden de pipeline.

## Cabecera de tabla por fase

```markdown
## Fase <nombre> (<n_skills>)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-<nombre> | `<flags>` | <agente; script; hook; kb> | CU-N.x · CU-M.y | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | <frase o —> |
```

## Leyenda (copia al encabezado del documento)

```markdown
- **Ejes:** `✅` cubierto · `🟡` parcial · `❌` hueco · `—` no aplica.
  - **Happy** — invocación canónica con precondiciones satisfechas → artefacto correcto + sello.
  - **Edge** — args parciales/ausentes, layout legacy, subset, idempotencia, re-ejecución, monorepo.
  - **Harness** — invocar saltándose una precondición o gate → debe **bloquear** (`[SDD-GATE]`, veredicto no-`LISTO`, parada por gap crítico).
  - **Args OK** — un escenario verifica que el orquestador traduce el lenguaje natural a los **args correctos** del skill (y que **no** inyecta overrides peligrosos sin petición explícita).
- **Estado:** `PENDIENTE` (sin revisar) · `REVISADO` (cruzado, sin huecos) · `CON-HUECOS` (faltan escenarios) · `COMPLETADO` (huecos rellenados).
```

## Bloque de progreso (debe cuadrar con la suma de filas)

```markdown
## Progreso

**Revisadas: X / N** ✅ · Completadas: C · Revisadas sin huecos: R · Con huecos: H · Pendientes: P
```

Invariantes:
- `Revisadas (X) = Completadas (C) + Revisadas-sin-huecos (R)`
- `C + R + H + P = N` (total de `wf-*` del core)

## Reglas de columna

- **Args**: los flags relevantes del skill, en backticks. Mismo texto que el `argument-hint` del `SKILL.md` cuando exista.
- **Mecanismo**: agente que la ejecuta (o "sin agente"), scripts `sdd-*.py` y hooks implicados, kb derivadas. Es la columna donde se anota la cobertura *derivada* de agentes/scripts/kb (no tienen fila propia).
- **CU que lo ejercitan**: los `CU-N.x` separados por `·`. Trazabilidad skill→escenarios; se actualiza al escribir escenarios nuevos.
- **Estado**: ciclo `PENDIENTE → REVISADO → CON-HUECOS → COMPLETADO`.
- **Huecos detectados**: una frase por hueco, o `—` si no hay. Aquí se justifica un eje `🟡`/`—` y se anota cuándo un eje parcial queda cubierto por un escenario transversal (CU-11.*).
