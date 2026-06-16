---
name: wf-design-extract
description: "Ingenieria inversa de un DESIGN.md desde una UI ya en produccion: descubre tokens, paleta, tipografia y componentes con evidencia (archivo:linea, mediciones) y genera un DESIGN.md de extraccion (origin: extracted) conforme al contrato. Entrada alternativa a la fase design para producto no rediseñable; delega la redaccion a design-architect."
when_to_use: "Activa en frases como 'extrae el DESIGN.md de la UI existente', 'ingenieria inversa del diseño de este proyecto', 'documenta el sistema visual que ya tenemos', 'deriva el DESIGN.md del CSS actual', 'caracteriza la UI en produccion'. No activa si se diseña desde cero (usa wf-design-system) ni para cambiar la UI ya extraida (usa wf-design-delta sobre el DESIGN.md extraido)."
argument-hint: "discover <path_ui> [--scope <subdir>] | generate <path_ui> [--from <extraction.md>] [--scope <subdir>] [--design-file DESIGN.md]"
effort: high
allowed-tools: [Read, Write, Bash, Grep, Glob, Agent]
context: fork
agent: design-architect
user-invocable: true
---

# design-extract — DESIGN.md por ingenieria inversa de la UI existente

Tu rol: explorar la UI en produccion con rigor de evidencia y delegar la redaccion. La regla central viene de `kb-design-characterization` (en el contexto del agente): **un token o decision visual sin evidencia no se inventa**. Tu recolectas la evidencia; el agente redacta sin fabricar.

Es el espejo de `wf-spec-from-code` en la fase Design. **NO exige spec validado ni `DESIGN_BRIEF.md`**: es una entrada ALTERNATIVA a la fase (igual que `wf-spec-from-code` no exige PRD). La UI existente es la fuente de verdad.

---

## Paso 1: Parsear argumentos

- **Modo**: `discover` | `generate`
- `discover <path_ui> [--scope <subdir>]`
- `generate <path_ui> [--from <extraction.md>] [--scope <subdir>] [--design-file DESIGN.md]`

Sin modo valido → informa el uso:
> "Uso: `/wf-design-extract discover <path_ui> [--scope <subdir>]` | `/wf-design-extract generate <path_ui> [--from <extraction.md>] [--scope <subdir>] [--design-file DESIGN.md]`"

`generate` sin `<producto>_design_extraction.md` existente y sin `--from` → detente:
> "No hay inventario de extraccion. Ejecuta primero `/wf-design-extract discover <path_ui>` — el inventario validado por el usuario es el gate de este flujo."

## Paso 2 (discover): Explorar la UI y mapear evidencia visual

Explora la UI (limitada a `--scope` si se paso). Busca **superficies de evidencia visual**, en este orden (jerarquia de `kb-design-characterization`):

1. **Ficheros de design tokens / theme / variables CSS** — `tokens.css`, `theme.{js,ts}`, `:root { --color-* }`, `tailwind.config.*`, `Color.kt`/`Theme.kt` (Compose), `Assets.xcassets` / `Color+.swift` (SwiftUI). Evidencia de nivel 1.
2. **Hojas CSS/SCSS/Tailwind** — reglas con valores de color, `font-size`, `border-radius`, `padding`, `box-shadow`. Evidencia de nivel 2 (leida con `archivo:linea`).
3. **Libreria de componentes en el codigo** — botones, inputs, cards, tabs: valores declarados en el componente. Evidencia de nivel 3.
4. **Capturas** — solo si el usuario las aporta. Valores medidos/muestreados (color picker, medicion de spacing). Evidencia de nivel 4.

Captura el commit base: `git rev-parse --short HEAD` (si la UI no esta en un repo git, anota `evidence_base: sin repo git — <fecha>`).

NO especules sobre codigo/estilos que no llegues a leer: un valor entra al inventario solo con al menos un puntero de evidencia.

Extrae, cada item con su **puntero de evidencia** y una **nota de confianza** (alta = token/CSS leido; media = valor en componente; baja = medido de captura):

- **Paleta cruda**: cada color con su uso observado y puntero. Si hay varios valores para el mismo rol (5 azules para "primary"), **listalos todos** — no promedies (marca `[INCONSISTENTE]`).
- **Usos tipograficos**: familias, tamaños y pesos observados, con su rol aparente.
- **Lista de componentes**: tipologia y estados observados en el codigo.
- **Spacing y radios**: escala observada.

## Paso 3 (discover): Escribir el inventario y DETENERTE (gate humano)

Resuelve donde iria el `DESIGN.md` (misma regla de layout que `wf-design-system` Paso 3):
- si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.design`, esa es la raiz de producto;
- en otro caso, la raiz de producto es el directorio que contiene `features/` si la UI cuelga de un layout de feature, o el directorio actual.

Escribe `<producto>_design_extraction.md` en esa raiz de producto. Incluye header con `Evidencia base: commit <SHA corto>` (o `sin repo git`) y `Cobertura de evidencia: <nivel de acceso>`.

**Detente SIEMPRE aqui.** Presenta el inventario (paleta con inconsistencias, tipografia, componentes, spacing — cada uno con confianza) y pide al usuario que confirme/corrija/descarte:
> "Este inventario es lo que la UI evidencia — revisalo antes de generar el DESIGN.md. Confirma que roles son correctos, que inconsistencias son reales y que quieres documentar. Cuando confirmes: `/wf-design-extract generate <path_ui>`"

Las correcciones del usuario se aplican al `_design_extraction.md` (marca lo descartado como `DESCARTADO — <motivo>`, no lo borres).

## Paso 4 (generate): Recolectar el dossier de evidencia

Relee a fondo las superficies confirmadas en el inventario (o el `--scope` si se uso `--from`). Construye un **dossier de evidencia**: cada decision visual con su puntero `archivo:linea` o medicion. Los valores **deducidos** (escala derivada, estado no observado, dark mode ausente) van en una **seccion separada `INFERIDOS`** con la razon — no se mezclan con lo observado.

Estructura del dossier:
- **Tokens de color** (observados, con puntero; inconsistencias listadas tal cual)
- **Type scale** (roles observados con puntero; roles derivados → INFERIDOS)
- **Spacing, radios, elevacion** (observados)
- **Componentes y estados** (observados; estados no encontrados → INFERIDOS)
- **INFERIDOS**: cada deduccion con su razon
- **DESIGN_GAP**: lo no inferible de la UI (Reference Apps, visual_personality si el CSS no lo permite caracterizar)

## Paso 5 (generate): Delegar la redaccion a design-architect

Resuelve el path del `DESIGN.md` (igual que `wf-design-system` Paso 3): `--design-file` si se paso; si no, `DESIGN.md` en la raiz de producto. Si ya existe, lee su contenido y pasalo como base; mas abajo se pregunta antes de sobrescribir.

Invoca al agente `design-architect` en modo `design-extract`:

```
Redacta un DESIGN.md EXTRAIDO de la UI existente.
Aplica kb-design-characterization ESTRICTAMENTE y conforma a kb-design-system-contract:
- header con origin: extracted, evidence_base: commit <SHA> (<fecha>), evidence_coverage: <nivel>
- cada token/decision con su evidencia del dossier; lo del bloque INFERIDOS va marcado [INFERIDO]
- inconsistencias reales DOCUMENTADAS (todas las variantes con su puntero + [INCONSISTENTE]), NUNCA promediadas
- NO inventes visual_personality/style_family/Reference Apps sin evidencia → [INFERIDO] o DESIGN_GAP
- NO fabriques dark mode si la UI no lo tiene → [INFERIDO]/DESIGN_GAP
- ## Changelog arranca con la entrada de extraccion

DOSSIER DE EVIDENCIA:
<decisiones observadas con punteros>

INFERIDOS:
<deducciones con su razon>

DESIGN_GAP:
<lo no inferible de la UI>

CONTEXTO: cobertura de evidencia <nivel>, commit <SHA>.
```

## Paso 6 (generate): Escribir y validar

Antes de escribir, verifica si el archivo ya existe:
```bash
!test -f "<path_design>" && echo "EXISTE" || echo "NO_EXISTE"
```
Si ya existe → pregunta al usuario:
> "Ya existe `<path_design>`. ¿Deseas sobrescribirlo con la extraccion?"
- **No** → informa el path existente y deten.
- **Si** → continua.

1. Escribe el output del agente en el path destino como `DESIGN.md`.
2. Ejecuta el linter de Google design.md:
   ```bash
   npx @google/design.md lint <path_design>
   ```
3. Segun el resultado:
   - **Sin errores**: confirma que supera la validacion `@google/design.md`.
   - **Con errores**: muestra la lista completa e indica cuales requieren correccion manual.
   - **npx no disponible o fallo de entorno**: informa al usuario e indica que puede ejecutarlo manualmente con `npx @google/design.md lint <path_design>`.

## Paso 7: Informar

- Paths generados (`_design_extraction.md` y/o `DESIGN.md`).
- **Conteo por nivel de evidencia**: nº de tokens/decisiones por nivel (tokens declarados / CSS leido / componente / captura medida / `[INFERIDO]`).
- **Lista de `[INFERIDO]` y `DESIGN_GAP`**: recordando que `[INFERIDO]` **no bloquea ningun gate** (la fase Design no tiene sellado mecanico) — es informativo. Siguiente paso para resolverlos: aportar contexto humano o auditar con `/wf-design-validate`.
- **Inconsistencias reales detectadas** (`[INCONSISTENTE]`): documentadas tal cual; unificarlas es rediseño.
- **Siguiente paso recomendado**:
  > "Para auditar el contrato extraido: `/wf-design-validate <DESIGN.md>`. Si vas a rediseñar lo que la UI hace hoy: `/wf-design-delta analyze <DESIGN.md> --new-reqs <cambios.md>`."
