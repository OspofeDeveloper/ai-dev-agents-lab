# CU-12 — Overlay de stack KMM

**Objetivo:** verificar el overlay específico de **Kotlin Multiplatform (KMM)**: que el
init del stack produce el estado técnico que leen todos los agentes KMM, y que los
workflows de scaffolding (networking, auth, storage, entornos, testing, stack completo)
configuran su pieza **respetando la separación de responsabilidades** y el estado del
proyecto, sin mezclar capas.
**Proyecto a usar:** un **proyecto KMM real** (gradle + `composeApp`/`iosApp` o
equivalente) inicializado en modo SDD con `stack: kmm`.
**Cobertura automática:** `sdd/tests/test_kmm_install_sh.py` cubre la **instalación** del
overlay (override por basename de `plan-architect`/`kb-plan-expert`, agentes/KBs KMM, no
pisar el `CLAUDE.md` raíz). La conducta de los workflows (qué scaffolding generan y si
respetan capas) es juicio de los agentes KMM → **manual**.

> [!IMPORTANT]
> **El overlay solo aplica con `stack: kmm`.** Se instala vía `wf-kmm-init` despachado
> por `wf-project-init` (ver `CU-1.h`) y **sobrevive a las actualizaciones** re-aplicado
> tras la base (ver `CU-10.a`). Todos los agentes KMM leen `kmm_project_state.md` al
> arrancar. Agentes del overlay: `kmm-explorer`, `kmm-network-auth-implementer`,
> `kmm-platform-integrator`.

---

## CU-12.a — Init del stack en modo detect (proyecto KMM existente)

**Precondición:** un proyecto KMM ya con código, sin `kmm_project_state.md`.
**Mecanismo:** skill `wf-kmm-init --mode detect` → subagente **`kmm-explorer`**. Output:
`kmm_project_state.md`.

1. Le pides detectar el estado KMM del proyecto ("detecta el estado KMM").
   → **Esperado:** `kmm-explorer` auto-explora el repo y escribe `kmm_project_state.md`
     con el estado técnico real (targets, arquitectura, DI, networking, auth, storage,
     recursos, navegación, testing, build commands) — fundamentado en el código, no
     inventado.

**Resultado:** PASS si genera el estado técnico trazado al repo real · FALLO si fabrica
piezas que el proyecto no tiene, o no produce el `kmm_project_state.md`.
**Desviación → reportar:** issue citando `CU-12.a`.

## CU-12.b — Init en modo configure y guarda de re-ejecución

**Precondición:** un proyecto KMM nuevo (o pides reconfigurar).
**Mecanismo:** skill `wf-kmm-init --mode configure` → **`kmm-explorer`**; registra el run
en `.sdd/stack-runs.jsonl`.

1. Le pides configurar un proyecto KMM nuevo.
   → **Esperado:** hace las preguntas de configuración y escribe `kmm_project_state.md`;
     registra el run en `.sdd/stack-runs.jsonl`.
2. Vuelves a lanzar el init con un `kmm_project_state.md` ya existente.
   → **Esperado:** **pregunta si rehacerlo** antes de sobrescribir (no lo pisa en
     silencio); solo regenera con confirmación o `--force`.

**Resultado:** PASS si configura, registra el run y pregunta antes de rehacer · FALLO si
sobrescribe el estado sin preguntar, o no registra el run.
**Desviación → reportar:** issue citando `CU-12.b`.

## CU-12.c — Stack completo (Ktor + Keycloak + Koin) por composición

**Precondición:** proyecto KMM con `kmm_project_state.md`.
**Mecanismo:** skill `wf-kmm-stack-setup-ktor-keycloak-koin` → subagente
**`kmm-network-auth-implementer`**.

1. Le pides configurar el stack habitual de una vez ("configura el stack completo KMM
   con Koin, Ktor y Keycloak").
   → **Esperado:** configura networking + auth + DI **componiendo las skills separadas**
     (networking, auth, datastore) sin fundirlas en una única fuente mezclada; respeta
     el estado del proyecto.

**Resultado:** PASS si configura el stack por composición sin mezclar capas · FALLO si
mezcla networking/auth/DI en una fuente única, o ignora el estado del proyecto.
**Desviación → reportar:** issue citando `CU-12.c`.

## CU-12.d — Networking sin acoplar a una estrategia de auth

**Precondición:** proyecto KMM con `kmm_project_state.md`.
**Mecanismo:** skill `wf-kmm-network-setup` → **`kmm-network-auth-implementer`**.

1. Le pides añadir la capa de red sin auth ("configura networking en KMM, solo red").
   → **Esperado:** configura el cliente HTTP (Ktor) y su DI **sin acoplarse a una única
     estrategia de auth**; si después hace falta auth, es `wf-kmm-auth-setup-keycloak`.

**Resultado:** PASS si configura red desacoplada de auth · FALLO si embute una estrategia
de auth concreta en el setup de red.
**Desviación → reportar:** issue citando `CU-12.d`.

## CU-12.e — Auth OAuth con Keycloak separando contratos

**Precondición:** proyecto KMM con networking ya configurado.
**Mecanismo:** skill `wf-kmm-auth-setup-keycloak` → **`kmm-network-auth-implementer`**.

1. Le pides configurar autenticación OAuth con Keycloak.
   → **Esperado:** separa **contratos de sesión / proveedor OAuth / mecanismo de
     integración** con el cliente HTTP (no los funde); resuelve la estrategia de refresh
     declarada.

**Resultado:** PASS si separa contratos de sesión, proveedor y mecanismo · FALLO si
acopla la sesión al cliente HTTP en una sola pieza indivisible.
**Desviación → reportar:** issue citando `CU-12.e`.

## CU-12.f — Persistencia relacional (Room)

**Precondición:** proyecto KMM con `kmm_project_state.md`.
**Mecanismo:** skill `wf-kmm-database-setup` → subagente **`kmm-platform-integrator`**.

1. Le pides añadir base de datos local ("configura Room en KMM").
   → **Esperado:** compone ownership del módulo de DB, entidades/DAOs en `commonMain`,
     builder por plataforma, KSP/driver y wiring de DI, separando **DAO de repositorio**;
     lo coloca en el módulo destino indicado (core vs feature).

**Resultado:** PASS si configura Room con separación DAO/repositorio en el módulo
correcto · FALLO si mezcla DAO y repositorio, o ignora el módulo destino.
**Desviación → reportar:** issue citando `CU-12.f`.

## CU-12.g — Storage clave-valor (Preferences DataStore)

**Precondición:** proyecto KMM con `kmm_project_state.md`.
**Mecanismo:** skill `wf-kmm-datastore-setup` → **`kmm-platform-integrator`**.

1. Le pides storage local de preferencias ("configura DataStore en KMM").
   → **Esperado:** configura Preferences DataStore por capas con DI y providers por
     plataforma, **sin mezclar storage local con auth o networking**.

**Resultado:** PASS si configura DataStore aislado de auth/networking · FALLO si lo
acopla a la capa de red o de sesión.
**Desviación → reportar:** issue citando `CU-12.g`.

## CU-12.h — Multi-brand / multi-environment

**Precondición:** proyecto KMM con `kmm_project_state.md`.
**Mecanismo:** skill `wf-kmm-environments` → **`kmm-platform-integrator`**.

1. Le pides configurar entornos/brands ("configura pre y pro en KMM", "multi-brand").
   → **Esperado:** define una **semántica estable de variantes** y sus implementaciones
     en Android e iOS, coherente entre plataformas.

**Resultado:** PASS si crea variantes con semántica estable en ambas plataformas · FALLO
si la semántica de variantes diverge entre Android e iOS.
**Desviación → reportar:** issue citando `CU-12.h`.

## CU-12.i — Infraestructura de testing

**Precondición:** proyecto KMM con `kmm_project_state.md`.
**Mecanismo:** skill `wf-kmm-testing-setup` → **`kmm-platform-integrator`**.

1. Le pides preparar el testing ("configura testing en el proyecto", `unit|integration|screenshot|all`).
   → **Esperado:** añade las dependencias Gradle por tipo de test, los source sets
     `commonTest`/`androidTest`/`iosTest` y el directorio `commonTest/fakes/`, acotado a
     los módulos indicados.

**Resultado:** PASS si configura los source sets y deps por tipo de test · FALLO si crea
una configuración de test que no compila o ignora los módulos pedidos.
**Desviación → reportar:** issue citando `CU-12.i`.
