---
name: wf-spec-from-code
description: "Ingeniería inversa de specs desde código existente (brownfield): descubre capacidades con evidencia (archivo:línea, rutas, tests) y genera specs de caracterización que describen lo que el sistema hace hoy. Entrada alternativa al pipeline cuando no hay PRD."
when_to_use: "Activa en frases como 'genera specs del código existente', 'documenta lo que hace este sistema', 'specs de este proyecto legacy', 'ingeniería inversa de specs', 'caracteriza este módulo'. No activa si existe un PRD como fuente (usa wf-spec-features-first), ni para cambiar comportamiento (usa wf-spec-delta sobre el spec de caracterización)."
argument-hint: "discover <path_codigo> [--scope <subdir>] | generate <path_codigo> --feature <F-C-00X> [--discovery <file>] [--allow-overwrite-sealed-spec] | generate <path_codigo> --capability <nombre> --scope <subdir> [--allow-overwrite-sealed-spec]"
effort: high
allowed-tools: [Read, Write, Bash, Grep, Glob, Agent]
context: fork
agent: sdd-spec-writer
user-invocable: true
---

# spec-from-code — Specs de caracterización desde código

Tu rol: explorar el código con rigor de evidencia y delegar la redacción. La regla central viene de `kb-spec-characterization` (en el contexto del agente escritor): **un CA sin evidencia no existe**. Tú recolectas la evidencia; el agente redacta sin inventar.

---

## Paso 1: Parsear argumentos

- **Modo**: `discover` | `generate`
- `discover <path_codigo> [--scope <subdir>]`
- `generate <path_codigo> --feature <F-C-00X> [--discovery <file>]` — desde un discovery validado
- `generate <path_codigo> --capability <nombre> --scope <subdir>` — directo, una capacidad que el usuario ya nombra y acota (la validación humana es implícita)
- **Flag opcional** (modo `generate`): `--allow-overwrite-sealed-spec` → autoriza sobreescribir un spec de caracterización cuya cabecera declare `Estado: VALIDADO`. Sin él, si el spec de destino está sellado **te detienes** (Paso 6). Solo llega armado por quien te lanza, porque el usuario lo eligió en un gate ([[D-024]]/[[D-026]]).

Sin modo válido → informa el uso. `generate --feature` sin `_code_discovery.md` existente → detén:
> "No hay `_code_discovery.md`. Primero hay que **descubrir las capacidades del código** — ese mapa, validado por ti, es el gate de este flujo."

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
> "Este mapa es lo que el código evidencia — revísalo antes de generar specs. ¿Qué capacidades son reales y cuáles quieres caracterizar? Dime cuáles y genero su spec."

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

1. **Spec**: `<raíz_spec>/features/<nombre>/spec/<nombre>_spec.md` (feature plana legacy existente: en su raíz). El header declara `> Feature ID: F-C-00X` y `> Origen de alcance: characterization` — el índice los deriva de ahí.

   **Si ya existe, mira su estado antes de escribir ([[D-024]]/[[D-062]])** — pisar un borrador no es lo mismo que pisar un spec validado:

   ```bash
   !grep -Eq '^[[:space:]]*[-*>]?[[:space:]]*\*{0,2}Estado:?\*{0,2}[[:space:]]*:?[[:space:]]*VALIDADO' "<path_existente>" && echo SELLADO || echo DRAFT
   ```

   - **`DRAFT`** (o no existe) → reescribe en su ubicación actual y sigue.
   - **`SELLADO` sin `--allow-overwrite-sealed-spec`** → **detente sin escribir nada** y devuelve el bloqueo con veredicto operativo `STOP_SPEC_SELLADO`:
     > "El spec de caracterización de `<nombre>` ya existe y está **validado** (`Estado: VALIDADO`) en `<path>`. Regenerarlo desde el código descarta el trabajo de validación —incluidos los `[INFERIDO]` que ya se confirmaron uno a uno—. No lo he tocado. Si el usuario quiere rehacerlo desde cero igualmente, relánzame con `--allow-overwrite-sealed-spec`. Si lo que quiere es **reflejar un cambio de comportamiento**, no hace falta rehacerlo: se aplica ese cambio sobre el spec existente y su validación se reabre en vez de descartarse — dile que te lo pida y lo enrutas tú."
   - **`SELLADO` con `--allow-overwrite-sealed-spec`** → reescribe y **dilo en el Paso 7**. El spec nuevo nace en `Estado: BORRADOR`.

   > **Por qué aquí no preguntas.** Corres en `context: fork`, y un subagente **no puede presentarle una pregunta al usuario**: la instrucción anterior —*"pregunta antes de regenerar"*— **no era ejecutable** ([[D-045]]). Paras y reportas; el gate lo presenta quien puede ([[D-026]]).

2. **README** de la feature en su raíz, con `Origen de alcance: characterization (código, commit <SHA>)`.
3. **`_features.md`**: NO lo escribas a mano (es un índice generado). Tras escribir el spec, regenéralo desde la raíz del proyecto (el directorio que contiene `.sdd/`):

   ```
   python3 .sdd/scripts/sdd-features-index.py <raíz_spec>
   ```

   Sin discovery (caso brownfield típico), el script construye el índice solo desde los specs presentes — la feature de characterization aparece con su `F-C-00X` y estado derivado de sus marcadores (un `[INFERIDO]` → BLOQUEADA). Si falta el script:
   > "⚠ Falta `.sdd/scripts/sdd-features-index.py`. Re-ejecuta la instalación del ecosistema (`install.sh`). El índice `_features.md` no se ha regenerado."

## Paso 7: Informar

- Paths generados y nº de CAs por nivel de evidencia (tests / código / config / `[INFERIDO]`).
- **Los `[INFERIDO]` bloquean el paso a planificación** (los gates los tratan como `[INCOMPLETO]`): el siguiente paso es **confirmarlos uno a uno con el usuario**, que es lo que desbloquea el spec.
- Si hay `[SOSPECHA_BUG]`: listarlos — decisión de producto pendiente (mantener o `wf-spec-delta`).
- Si el proyecto no tiene tests: recomienda characterization tests para los CAs de mayor riesgo antes de refactorizar.
