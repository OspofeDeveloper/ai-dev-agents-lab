# Mejoras futuras no críticas — ecosistema SDD

**Creado:** 2026-06-25 (como `OPTIMIZACIONES.md`; renombrado a `MEJORAS_FUTURAS.md` el 2026-06-26)

**Qué es este documento.** Backlog de mejoras **no críticas**: pulido, coherencia y calidad de vida que **no afectan al funcionamiento principal** del pipeline ni bloquean ningún caso de conformance. Son cosas interesantes de abordar en el futuro, sin urgencia. El trabajo estructurado y crítico (bugs, enforcement, ciclo de vida) vive en [`ROADMAP.md`](ROADMAP.md); este fichero es deliberadamente de **baja prioridad**.

**Cómo usar.** Cada ítem tiene checkbox, etiqueta de esfuerzo y el **origen** (dónde se observó). Al abordar uno: marcar `[x]`, anotar fecha y commit. Si un ítem resulta ser crítico o bloqueante, **muévelo a `ROADMAP.md`** — aquí solo vive lo prescindible.

**Leyenda esfuerzo:** 🟢 S (una edición acotada) · 🟡 M (varias piezas o una decisión de diseño) · 🔴 L (cambio de flujo o arquitectura).

---

## Fase init (`wf-project-init`)

- [ ] 🟡 **O-1 — `design_role: full` se ofrece en superficies sin UI.** En la entrevista de standalone, la pregunta de alcance de diseño (*system* vs *full*) se hace **antes** que la de superficie, así que `full` se ofrece aunque la superficie acabe siendo sin UI (`backend`/`other`). `full` instala el tooling de diseño-por-feature (`design-feature-architect`, `wf-design-feature-prototype`, `kb-design-feature-artifacts`), que sin UI es ruido inútil — aunque el `DESIGN.md` de **sistema** sí sea legítimo si el repo es SSoT del producto. Hoy el agente **avisa** de la incoherencia y respeta la elección (comportamiento correcto, coherente con el criterio de CU-1.k: avisar y respetar la decisión informada, no gating paternalista).
  - *Mejora posible:* preguntar **superficie antes que diseño** y, si `has_ui` es `false`, no ofrecer `full` (o reconciliar `full→system` con confirmación explícita).
  - *Por qué no es crítico:* `full` sin UI no es dañino (solo instala tooling que no se usa); el aviso ya cubre el caso y el usuario puede elegir `system`.
  - *Coste:* pequeño-medio — implica reordenar el flujo de preguntas (superficie↔diseño) y, posiblemente, una reconciliación post-superficie. No es un drop-in.
  - *Refuerzo (capa determinista):* `sdd-init-detect.py repair-plan` deriva `expected_design_role: "full"` para **toda** topología standalone, **sin mirar `has_ui`**. Consecuencia: un standalone con diseño `system` (p. ej. superficie headless) se marca `design_role_consistent: false`, y un `repair`/extend lo "subiría" a `full`. O sea, el sesgo standalone⇒full no vive solo en el wizard sino también en el detector — la mejora debería tocar **ambos** (gatear `full` a `has_ui` en la derivación, no solo en el orden de preguntas).
  - *Origen:* observado probando **CU-1.l** (evolución authoring→standalone con superficie `other` + diseño `full`; y el `repair-plan` reportando `expected_design_role: full` sobre una superficie headless).

- [ ] 🟢 **O-2 — El aviso de "piezas huérfanas" de `install.sh` sugiere un `--prune` peligroso en extend.** Al ampliar con un subset de fases (p. ej. `install.sh plan,tasks` en un extend authoring→standalone), `install.sh` detecta las fases previas (prd/spec/design) como "piezas de fases no seleccionadas" y sugiere `bash install.sh plan,tasks --prune` para eliminarlas — pero en ese contexto `--prune` **borraría la autoría que el extend quiere conservar**. El agente lo maneja bien (explica que es benigno y no prunea), pero el texto es un footgun si alguien lo sigue al pie de la letra.
  - *Mejora posible:* que `wf-project-init`, en extend, pase a `install.sh` **todas** las fases del contrato (no solo las nuevas) para que no haya "huérfanas" espurias; o que el aviso de `install.sh` distinga "huérfana real" de "fase instalada en otra pasada del mismo proyecto".
  - *Por qué no es crítico:* el agente no sigue la sugerencia; las piezas previas quedan intactas y el `verify` pasa. Es ruido/footgun textual, no pérdida de datos real.
  - *Origen:* observado en las dos corridas de **CU-1.l** (extend authoring→standalone, instalando solo `plan,tasks`).

---

## Fase spec (`wf-spec-discover` / `wf-spec-readiness`)

- [ ] 🟡 **O-3 — readiness/discovery no señalan qué features dependen del diseño.** `wf-spec-readiness` ordena por dependencias + shared models + gaps/conflictos, y el discovery troquela por cohesión funcional — pero **ninguno marca, por feature, si su Plan disparará el gate de "Design obligatorio"** (presentación/navegación/a11y de UI; regla canónica de `kb-plan-expert`). Consecuencia práctica: un equipo que quiere **empezar las capas sin UI (domain/data/networking) mientras el diseño aún no está listo** no tiene una vista de "qué features son 100% construibles ya vs cuáles tienen una rebanada de presentación esperando al diseño". El orden de readiness ya front-loadea las features cimentadoras (las que más bloquean) por dependencias —lo cual ayuda—, pero no es lo mismo que un flag explícito de design-dependency.
  - *Mejora posible:* añadir al readiness report (y/o al `_features.md`/discovery) un campo por feature tipo **"🎨 necesita diseño / ✅ sin UI"**, derivado de si el spec describe journeys/pantallas con surface UI visible.
  - *Matiz:* la regla de diseño-obligatorio vive en fase **Plan** (`kb-plan-expert`), aguas abajo del readiness. El campo sería por tanto una **heurística de spec** (¿la feature describe UI visible?), no la aplicación exacta de la regla de plan — útil como semáforo, no como veredicto.
  - *Por qué no es crítico:* la base transversal (API/red/auth/storage) ya es `:core:*`/setup de stack, **independiente de discovery y diseño** (se arranca ya, p. ej. con los `wf-kmm-*-setup`); y el domain/data por feature se planifica sin diseño en cuanto existe su spec (el gate solo frena la **presentación**, no las capas de abajo). La mejora es **conveniencia de visibilidad**, no desbloquea nada que hoy esté bloqueado.
  - *Coste:* medio — heurística de detección de UI en el spec + nuevo campo en el readiness report (y, opcionalmente, en discovery/`_features.md`).
  - *Origen:* conversación 2026-06-26 sobre arrancar domain/data/networking de un consumer KMM antes de que el diseño esté listo (la regla canónica de `kb-plan-expert` exime explícitamente networking/auth/storage/domain del gate de diseño).

---

## Completado

_(vacío)_
