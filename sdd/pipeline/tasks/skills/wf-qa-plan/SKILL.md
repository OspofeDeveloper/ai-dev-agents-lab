---
name: wf-qa-plan
description: "Genera el plan de QA de una feature: deriva casos de prueba TC-XXX trazables desde los CAs GIVEN/WHEN/THEN del feature spec (afinados con plan/tasks y project state si existen) y produce <feature>_qa_plan.md. Delega a qa-engineer."
when_to_use: "Activa con frases como 'genera el plan de QA', 'deriva los casos de prueba', 'qa plan de la feature', 'qué casos de prueba salen de estos CAs', 'prepara el testing de la feature'. No activa para escribir tests (owner implementador/tester del stack) ni para verificar cobertura tras implementar (usa wf-qa-verify)."
argument-hint: "generate <feature_spec.md>"
effort: medium
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: qa-engineer
user-invocable: true
---

# Workflow: QA-PLAN

Tu objetivo es producir el `_qa_plan.md` de una feature: la matriz de casos de prueba que convierte cada CA del spec en algo ejecutable y trazable. La metodología (formato TC, reglas de derivación, niveles) es la de `kb-qa-expert`.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: `generate` (único soportado)
- **Path del spec**: el `_spec.md` de la feature

Si falta alguno:
> "Uso: `/wf-qa-plan generate <feature_spec.md>`"

---

## Paso 2: Precondición — spec fiable

El gate PreToolUse (`sdd-gate-check.py`) ya verifica mecánicamente que el spec no tiene `[INCOMPLETO]`, `[CRÍTICO]` ni `[INFERIDO]`, que `status_sync` es fiable y que no hay deriva del PRD. Replica la comprobación por si el gate no está instalado: si el spec falla cualquiera de esas condiciones, detente y remite a `/wf-spec-gap-resolve` o `/wf-spec-sync-from-prd` según corresponda. Derivar TCs de un spec inestable produce un QA plan muerto al nacer.

Detecta el modo del spec: si el header declara `> Modo: ligero`, aplica la proporcionalidad de `kb-qa-expert` (Modo ligero).

---

## Paso 3: Recoger contexto de la feature

Desde la ubicación del spec, localiza (subcarpetas de fase primero, raíz de la feature como fallback legacy):
- `_plan.md` y `_tasks.md` de la feature → si existen, afinan niveles de prueba, suites y owners de las acciones recomendadas
- `<stack>_project_state.md` en la raíz del proyecto → sus suites, source sets y comandos declarados mandan sobre los criterios genéricos

Ninguno es obligatorio: el QA plan deriva del spec; plan/tasks/project state solo lo afinan.

---

## Paso 4: Derivar los casos de prueba

Delega en `qa-engineer` la derivación completa según `kb-qa-expert`:
- ≥1 TC por CA (cobertura total), un TC por rama observable que el CA prometa
- GIVEN/WHEN/THEN concretos con datos reales
- Nivel y `Automatizable` justificados; `Estado: PENDIENTE` en todos
- Si aparece comportamiento que necesita prueba sin CA que lo respalde: NO derivar el TC — listarlo como **gap de spec** en la salida

---

## Paso 5: Escribir el artefacto

El QA plan vive junto al `_tasks.md` de la feature: `features/<nombre>/tasks/<nombre>_qa_plan.md` (subcarpetas) o `features/<nombre>/<nombre>_qa_plan.md` (plano legacy — no mezclar layouts).

Si ya existe → pregunta al usuario si desea regenerarlo (no → informa del path y detén; los `Estado` previos escritos por `wf-qa-verify` se pierden al regenerar — adviértelo).

Header de trazabilidad obligatorio:

```markdown
# QA Plan: <Feature>
> Versión: 1.0 | Fecha: YYYY-MM-DD
> Spec origen: <ruta relativa desde este archivo al _spec.md>
> Spec versión: <Versión del header del spec>
> Modo: standard | ligero
> Total TCs: N (automatizables: X, manuales: Y)
```

---

## Paso 6: Informar al usuario

- Path del `_qa_plan.md`, total de TCs, desglose por CA y por nivel, manuales con su justificación.
- Gaps de spec detectados (si los hay) → recomendar `/wf-spec-delta analyze <spec> --new-reqs <descripción>`.
- Siguiente paso: implementar los tests con sus owners (tasks de test vía `/wf-task-run`, o el tester del stack); cuando la feature esté implementada → `/wf-qa-verify <path>_qa_plan.md`.
