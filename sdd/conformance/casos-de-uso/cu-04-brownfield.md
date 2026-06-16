# CU-4 — Generar specs desde código existente (brownfield)

**Objetivo:** verificar la entrada brownfield de la fase Spec: caracterizar código ya
escrito en specs, parando en un gate humano tras el descubrimiento, marcando
`[INFERIDO]` lo que el código no evidencia, y dejando esos `[INFERIDO]` como bloqueo
del plan.
**Proyecto a usar:** un **código heredado real sin specs**, idealmente con un módulo
cuya lógica tenga zonas ambiguas o sin tests (p. ej. un servicio backend antiguo, una
política a medias): justo lo que fuerza CAs `[INFERIDO]`.
**Cobertura automática:** los marcadores y el índice (`sdd-features-index.py`,
`kb-spec-characterization`) tienen soporte determinista; la caracterización en sí es
juicio del agente → **manual**.

> [!IMPORTANT]
> **Espejo brownfield de la fase Spec.** Es entrada alternativa: no exige PRD ni
> analysis. La regla de oro de la caracterización es **evidencia por CA**: lo que no
> se demuestra en el código se marca `[INFERIDO]`, no se especula como cierto.

---

## CU-4.a — Descubrir capacidades y DETENERSE en el gate humano

**Precondición:** un módulo de código real sin specs.
**Mecanismo:** skill `wf-spec-from-code` modo `discover` → subagente
**`sdd-spec-writer`**. Output: `<proyecto|scope>_code_discovery.md` con
`Evidencia base: commit <SHA corto>`.

1. Le pides generar specs a partir de ese código ("saca los specs de este módulo").
   → **Esperado:** explora el código, escribe el `_code_discovery.md` (mapa: ID,
     nombre, actor, superficie, confianza) y **se detiene SIEMPRE** presentándote el
     mapa para que **confirmes/corrijas/descartes** capacidades antes de generar nada.
2. Le pides `generate --feature F-C-00X` sin haber hecho el discover.
   → **Esperado:** se detiene con *"No hay `_code_discovery.md`. Ejecuta primero
     `/wf-spec-from-code discover <path>`…"* — el mapa validado es el gate del flujo.

**Resultado:** PASS si descubre y para en el gate humano · FALLO si genera specs sin
pasar por la confirmación del mapa.
**Desviación → reportar:** issue citando `CU-4.a`.

## CU-4.b — Caracterizar con `[INFERIDO]` donde falta evidencia

**Precondición:** `_code_discovery.md` confirmado; el código tiene una zona ambigua
(la política de bloqueo a medias del fixture).
**Mecanismo:** skill `wf-spec-from-code` modo `generate` → **`sdd-spec-writer`** (carga
`kb-spec-characterization`). Output:
`features/<nombre>/spec/<nombre>_spec.md` con `Feature ID: F-C-00X` y
`Origen de alcance: characterization`.

1. Le pides generar el spec de una capacidad descubierta.
   → **Esperado:** genera los CAs con su **campo Evidencia** (tests / código / config);
     los comportamientos que el código **no evidencia** se marcan como CAs `[INFERIDO]`
     — no los da por ciertos ni los inventa.

**Resultado:** PASS si marca `[INFERIDO]` lo no evidenciado y cita evidencia en lo
demás · FALLO si especula comportamientos como confirmados.
**Desviación → reportar:** issue citando `CU-4.b`.

## CU-4.c — Los `[INFERIDO]` bloquean el plan

**Precondición:** un spec de caracterización con al menos un CA `[INFERIDO]` sin
confirmar.
**Mecanismo:** gate `gate_spec_fiable` de `sdd-gate-check.py` (trata `[INFERIDO]` como
`[INCOMPLETO]`).

1. Le pides generar el plan de esa feature caracterizada.
   → **Esperado:** **deny** — los `[INFERIDO]` bloquean `wf-prepare-plan` igual que un
     `[INCOMPLETO]`; te remite a confirmarlos con `/wf-spec-gap-resolve` antes de
     construir nada encima. (Enlaza con `CU-9.g`.)
2. Confirmas los `[INFERIDO]` con gap-resolve y vuelves a pedir el plan.
   → **Esperado:** ya desbloqueado, el plan puede generarse.

**Resultado:** PASS si bloquea con `[INFERIDO]` y desbloquea tras confirmarlos · FALLO
si deja generar el plan sobre inferencias sin confirmar.
**Desviación → reportar:** issue citando `CU-4.c`.

## CU-4.d — Comportamiento sospechoso de defecto: `[SOSPECHA_BUG]`, no se corrige

**Precondición:** un código cuyo comportamiento observado parece un defecto (no lo que el
sistema *debería* hacer), descubierto al caracterizar.
**Mecanismo:** skill `wf-spec-from-code` modo `generate` → `sdd-spec-writer` (`kb-spec-characterization`).

1. Caracterizas una capacidad cuyo código tiene un comportamiento sospechoso de bug.
   → **Esperado:** documenta el comportamiento **ACTUAL** (lo que el código hace hoy) y lo marca
     `[SOSPECHA_BUG]`; **no** lo "corrige" en el spec ni lo describe como debería-ser. La
     caracterización describe lo que hay; arreglarlo es decisión posterior (`wf-spec-delta` / `wf-bug`).

**Resultado:** PASS si documenta lo actual + `[SOSPECHA_BUG]` sin corregir · FALLO si especula el
comportamiento "correcto" como si fuera el real, o silencia la sospecha.
**Desviación → reportar:** issue citando `CU-4.d`.
