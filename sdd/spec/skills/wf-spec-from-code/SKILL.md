---
name: wf-spec-from-code
description: "Ingeniería inversa de specs desde código existente (brownfield): descubre capacidades con evidencia (archivo:línea, rutas, tests) y genera specs de caracterización que describen lo que el sistema hace hoy. Entrada alternativa al pipeline cuando no hay PRD."
when_to_use: "Activa en frases como 'genera specs del código existente', 'documenta lo que hace este sistema', 'specs de este proyecto legacy', 'ingeniería inversa de specs', 'caracteriza este módulo'. No activa si existe un PRD como fuente (usa wf-spec-features-first), ni para cambiar comportamiento (usa wf-spec-delta sobre el spec de caracterización)."
argument-hint: "discover <path_codigo> [--scope <subdir>] | generate <path_codigo> --feature <F-C-00X> [--discovery <file>] | generate <path_codigo> --capability <nombre> --scope <subdir>"
effort: high
allowed-tools: [Read, Write, Bash, Grep, Glob, Agent]
context: fork
agent: sdd-spec-writer
---

# spec-from-code — Specs de caracterización desde código

Tu rol: explorar el código con rigor de evidencia y delegar la redacción. La regla central viene de `kb-spec-characterization` (en el contexto del agente escritor): **un CA sin evidencia no existe**. Tú recolectas la evidencia; el agente redacta sin inventar.

---

## Paso 1: Parsear argumentos

- **Modo**: `discover` | `generate`
- `discover <path_codigo> [--scope <subdir>]`
- `generate <path_codigo> --feature <F-C-00X> [--discovery <file>]` — desde un discovery validado
- `generate <path_codigo> --capability <nombre> --scope <subdir>` — directo, una capacidad que el usuario ya nombra y acota (la validación humana es implícita)

Sin modo válido → informa el uso. `generate --feature` sin `_code_discovery.md` existente → detén:
> "No hay `_code_discovery.md`. Ejecuta primero `/wf-spec-from-code discover <path>` — el mapa de capacidades validado por el usuario es el gate de este flujo."

## Paso 2 (discover): Explorar el código y mapear capacidades

Explora el repo (limitado a `--scope` si se pasó). Busca **superficies de comportamiento observable**, en este orden:

1. **Entrypoints**: rutas HTTP/endpoints (routers, controllers, anotaciones), pantallas/views registradas, comandos CLI, jobs/crons, consumers de colas.
2. **Tests existentes**: nombres de suites y casos — son evidencia de máxima fuerza y delimitan capacidades reales.
3. **Modelos persistentes**: esquemas, migraciones, entidades — delimitan los datos que el sistema gestiona.
4. **Permisos/roles**: indican actores reales.

NO especules sobre código que no llegues a leer: una capacidad entra al mapa solo con al menos un puntero de evidencia.

Agrupa en capacidades funcionales (`F-C-001`, `F-C-002`...) con: nombre, actor (real del código o `usuario del sistema`), superficie (entrypoints), evidencia (paths concretos), nº de tests que la ejercitan, y una nota de confianza (`alta` = tests + código claro; `media` = código claro sin tests; `baja` = mucha inferencia → candidata a descartar o investigar).

## Paso 3 (discover): Escribir el mapa y DETENERTE (gate humano)

Escribe `<nombre_proyecto|scope>_code_discovery.md` en el directorio raíz de artefactos spec (regla de layout: `artifacts.spec` de `.sdd/project-init.json` si está declarado; si no, el directorio actual). Incluye header con `Evidencia base: commit <SHA corto>` (`git rev-parse --short HEAD`).

**Detente SIEMPRE aquí.** Presenta el mapa (ID, nombre, actor, superficie, confianza) y pide al usuario que confirme/corrija/descarte capacidades:
> "Este mapa es lo que el código evidencia — revísalo antes de generar specs. ¿Qué capacidades son reales y cuáles quieres caracterizar? Cuando confirmes: `/wf-spec-from-code generate <path> --feature F-C-00X`"

Las correcciones del usuario se aplican al `_code_discovery.md` (marca las descartadas como `DESCARTADA — <motivo>`, no las borres).

## Paso 4 (generate): Recolectar el dossier de evidencia

Para la capacidad elegida, relee a fondo su superficie declarada en el discovery (o el `--scope` en modo directo):

- entrypoints completos (firma, validaciones, respuestas de error)
- flujo principal y ramas observables (condicionales con efecto visible)
- tests que la ejercitan (literal: qué afirman)
- modelos/esquemas implicados
- reglas de autorización

Construye un **dossier**: lista de comportamientos observados, cada uno con su puntero (`archivo:línea`, `test path::nombre`). Lo que deduzcas sin observación directa va en una sección separada `INFERIDOS` con la razón de la inferencia. No mezcles.

## Paso 5 (generate): Delegar la redacción a sdd-spec-writer

Invoca el agente `sdd-spec-writer` con:

```
Redacta un SPEC DE CARACTERIZACIÓN para la capacidad <nombre> (F-C-00X).
Aplica kb-spec-characterization estrictamente: header obligatorio (Origen:
characterization, PRD origen: N/A, Evidencia base: commit <SHA>), cada CA con
campo Evidencia, comportamientos del bloque INFERIDOS como CAs [INFERIDO] con
su Confirmación pendiente. No añadas NINGÚN comportamiento que no esté en el
dossier. Comportamiento sospechoso de defecto → documenta lo actual + [SOSPECHA_BUG].

DOSSIER DE EVIDENCIA:
<comportamientos observados con punteros>

INFERIDOS:
<deducciones con su razón>

CONTEXTO: <actor, superficie, modelos del discovery>
```

## Paso 6 (generate): Escribir artefactos

Layout estándar (mismas reglas que `wf-spec-fast-track`):

1. **Spec**: `<raíz_spec>/features/<nombre>/spec/<nombre>_spec.md` (feature plana legacy existente: en su raíz). Si ya existe → pregunta antes de regenerar.
2. **README** de la feature en su raíz, con `Origen de alcance: characterization (código, commit <SHA>)`.
3. **`_features.md`**: crea o actualiza la entrada de la feature marcando origen characterization. Si el índice no existe, créalo mínimo (index + estado por feature).

## Paso 7: Informar

- Paths generados y nº de CAs por nivel de evidencia (tests / código / config / `[INFERIDO]`).
- **Los `[INFERIDO]` bloquean `/wf-prepare-plan`** (los gates los tratan como `[INCOMPLETO]`): siguiente paso para confirmarlos → `/wf-spec-gap-resolve <spec.md>`.
- Si hay `[SOSPECHA_BUG]`: listarlos — decisión de producto pendiente (mantener o `wf-spec-delta`).
- Si el proyecto no tiene tests: recomienda characterization tests para los CAs de mayor riesgo antes de refactorizar.
