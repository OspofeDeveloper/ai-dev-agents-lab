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

## Arquitectura cross-repo (exploratorio)

- [ ] 🔴 **O-4 — ¿MCP para comunicar los repos `spec` / `design` / `consumer`? (exploratorio, gated a escala).** Hoy el acoplamiento cross-repo es **git-native y determinista**: `artifacts_source`/`design_source` (rutas relativas a checkouts locales) + `*_pin` (SHA git); `sdd-source-drift.py` = `git diff pin..HEAD`; `sdd-design-resolve.py` = merge de ficheros local. Reproducible, offline, auditable, CI-safe. La ocurrencia: exponer specs/design como un **MCP** consultable, en vez de exigir checkouts locales.

  **CUÁNDO SÍ aporta (condiciones que deben darse juntas):**
  - **Escala multi-repo real**: muchos repos consumer y una plataforma/SSoT central de specs+design; la fricción de "clona y mantén frescos `../specs` y `../design` en cada consumer" es un coste tangible y repetido.
  - Se diseña como **capa de SOLO LECTURA que sirve una versión PINEADA** (no "lo último"), **complementando** git — nunca reemplazando el pin.
  - El valor está en **vistas computadas** como tool (CAs de F-XXX, shared models por feature, resolución `base ⊕ override` de un target, drift) y en **acceso cross-tool/IDE**, no en "leer un .md" (eso ya lo hace el filesystem).

  **CUÁNDO NO (y por qué NO implementarlo entonces):**
  - **Dev individual o equipo pequeño** / pocos repos: el modelo file+git es más simple y robusto; el MCP solo añade infra.
  - Si sirviera **"lo último" en vez de una versión pineada**: rompe el *pinning* —que es el punto del contrato consumer↔SSoT (construir contra una versión conocida)— y se convierte en "git con más pasos".
  - **Contexto CI/headless**: los MCP autenticados interactivamente **desaparecen en runners headless/cron**; sustituir el checkout git por MCP en el contrato lo vuelve frágil donde hoy es determinista.
  - Como **SSoT del contrato**: jamás. El MCP sería capa de conveniencia/alcance; la fuente de verdad sigue siendo el repo + git.

  - *Regla de oro:* cambiar git por MCP en el núcleo = cambiar **determinismo por liveness**, el trade equivocado para un sistema de contratos. Solo entra como capa read-only pineada **encima** de git, y solo cuando la fricción de clonado a escala lo justifique.
  - *Coste:* alto — servidor MCP (build/host/auth/versionado), mantener el esquema en sync, y fragilidad en CI. No es drop-in.
  - *Origen:* conversación 2026-06-26 (ocurrencia sobre comunicar spec/design/consumer); explícitamente marcado para **no implementar si no aporta** (ver "cuándo no").

---

## Gobernanza del repo / CI (infra del ecosistema)

- [ ] 🔴 **O-5 — Adoptar GitFlow + CI de tests como gate de merge (cuando el repo se abra al equipo).** Hoy se commitea **directo a `develop`** y la suite se corre **a mano** antes de commitear (disciplina manual, sin red de seguridad). Cuando el repo esté disponible para todo el equipo, formalizar el flujo para que **nadie pueda integrar cambios sin pasar los tests** ni tocar `develop`/`main` directamente.
  - *Mejora posible (componentes):*
    - **CI (GitHub Actions):** workflow que corra `bash sdd/tests/run-tests.sh` en cada push/PR. Los tests son `unittest` puro + bash, **sin dependencias externas** → un runner `ubuntu-latest` con Python 3 los ejecuta tal cual (~15 min hoy, 417 tests). El hook de sesión SDD ya se **auto-silencia en CI** (`CI=true` / `SDD_NON_INTERACTIVE=1`), así que no interfiere.
    - **Branch protection en `develop` y `main`:** prohibir push directo; exigir PR + status check verde (el job de CI) + ≥1 review.
    - **PR-per-change:** cada cambio en su rama (`feature/*`, `fix/*`), PR contra `develop`, merge solo con CI en verde.
    - **GitFlow completo:** `main` (releases estables) ← `develop` (integración) ← `feature/*`/`fix/*`; `release/*` para congelar versión; `hotfix/*` desde `main`.
  - *Enganche natural:* el bump de `VERSION` + `CHANGELOG` —que ya se olvida (ver el rezago de D-023, que dejó `VERSION` sin bumpear y por eso no propagaba vía `wf-sdd-update`)— encaja como **paso obligatorio de la rama `release/*`**, y CI podría **chequear que todo cambio sobre artefactos instalables toca `VERSION`** (guardarraíl determinista contra ese rezago).
  - *Por qué no es crítico ahora:* con un solo desarrollador la disciplina manual (correr la suite antes de commitear, que es lo que se hace) basta; el gate automático aporta valor cuando hay **varias manos** que pueden saltárselo.
  - *Coste:* medio-alto — el YAML de Actions es pequeño y directo, pero **establecer y hacer cumplir GitFlow en el equipo** es cambio de proceso (branch protection, plantillas de PR, convención de ramas, formación).
  - *Origen:* conversación 2026-07-12, tras commitear D-024 directo a `develop`: deseo de que a futuro los tests sean **gate de merge** y no se pueda actuar directamente sobre `develop`.

- [ ] 🔴 **O-6 — Plantilla de PR obligatoria, con foco en conducta no determinista (complementa O-5).** Al ser software gobernado por IA, hay **dos capas de test con garantías distintas**: la **determinista** (`run-tests.sh`, que CI puede exigir) y la **conductual** (los CU de conformance, juicio del agente → **no deterministas**, un solo run no prueba nada y CI **no** los cubre). Un PR debe hacer explícita **qué capa toca y cómo se validó**, para que el reviewer vea que no se rompe nada que CI no vigila. La **SSoT de estas normas** (≥3 corridas, determinista vs conductual, procedencia, recalibración, rama protectora) es **`kb-sdd-conformance` Regla 9** — la plantilla solo la operativiza en el PR. Plantilla propuesta (→ futuro `.github/PULL_REQUEST_TEMPLATE.md`):

  ```markdown
  ## Qué cambia
  <qué se ha modificado, 1-2 frases>

  ## Por qué
  <motivación / problema de diseño o negocio>

  ## Qué fallaba antes
  <el comportamiento incorrecto previo — el fallo concreto que este cambio corrige>

  ## Cobertura determinista (la vigila CI)
  - [ ] Test(s) añadido(s): `<nombre_test>` — qué asegura
  - [ ] Suite completa en verde (`run-tests.sh`): <N>/<N> OK

  ## Impacto conductual (NO lo cubre CI — re-validación manual)
  - CUs afectados: `CU-X.y`, ...
  - [ ] ¿Validados junto con este cambio? <sí/no + por qué>
  - Evidencia (no determinista → ≥3 corridas por CU): <resumen PASS/FALLO, o enlace a logs>
  - Consumidor + versión del ecosistema usados: <p. ej. myops-app-specs @ 0.60.0>
  - Modelo usado para validar: <modelo + fecha> (la conducta puede derivar entre versiones de modelo)

  ## Gobernanza
  - [ ] Decisión registrada si cambia un contrato: `D-NNN`
  - [ ] `CHANGELOG.md` actualizado; `VERSION` bumpeado si toca artefacto instalable
  - [ ] Marcado ⚠ si afecta a proyectos ya inicializados
  - Reversibilidad: <git revert basta / requiere re-install en consumidores>
  ```

  - *Extras de safety incluidos (más allá de los 5 campos pedidos):*
    - **Capa determinista vs conductual separadas**: hace visible que un cambio conductual con CI verde **no** está probado — la evidencia manual es obligatoria, no opcional.
    - **≥3 corridas por CU afectado**: un PASS único puede ser suerte del muestreo (lo vivimos: CU-2.d rama draft se saltó el gate 2/2 de forma *razonada*; una sola corrida habría engañado en cualquier dirección).
    - **Modelo + fecha de validación**: la conducta del agente puede cambiar al cambiar de modelo; una validación caduca si el modelo cambia.
    - **No debilitar un CU para que pase**: si el cambio haría fallar un CU existente, eso es **señal**, no se relaja el CU para forzar el verde (salvo que el CU esté mal calibrado, y entonces se justifica por escrito — como D-024 recalibró CU-2.d). Análogo a la regla `DIVERGENTE` de QA (un test que falla contra un CA no se ajusta, se investiga).
    - **Validar la rama protectora, no solo el happy path**: p. ej. en D-024 no bastaba ver que salta el gate; había que ver que **declinar deja el fichero intacto**.
    - **Alcance en consumidores + reversibilidad**: si toca artefacto instalable, decir que requiere `wf-sdd-update`/re-install y cómo se revierte.
  - *Mejora posible:* materializar la plantilla en `.github/PULL_REQUEST_TEMPLATE.md` cuando se abra O-5; opcionalmente un check de CI que **falle el PR si la sección "Impacto conductual" está vacía** cuando el diff toca `pipeline/**/skills/**`, `**/agents/**` o `**/routing.md` (heurística de "esto es conductual").
  - *Por qué no es crítico ahora:* con un dev la disciplina ya se aplica de facto (cada cambio conductual se valida en consumidor real y se anota en el CU); la plantilla la vuelve **obligatoria y auditable** cuando entra más gente.
  - *Coste:* bajo el fichero de plantilla; medio el check de CI heurístico; el grueso es **cultura de PR** (que se rellene de verdad).
  - *Origen:* conversación 2026-07-12 — al ser software de IA, los tests no deterministas deben re-probarse antes de integrar; el PR debe dar visibilidad de qué se validó y qué no.

---

## Completado

_(vacío)_
