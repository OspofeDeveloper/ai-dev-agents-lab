---
name: wf-design-system
description: Orquestador SDD para crear o actualizar el DESIGN.md de un producto a partir de un feature spec validado. Usalo cuando ya exista un _spec.md y quieras definir la identidad visual persistente que alimentara Stitch y futuros prototipos de features. Activa en frases como "crea el DESIGN.md", "genera el sistema visual desde el spec", "prepara el contrato visual del producto", "actualiza el DESIGN.md". No activa para generar planes KMM ni tasks.
argument-hint: "generate <feature_spec.md> [--prd <prd.md>] [--design-file DESIGN.md]"
effort: high
allowed-tools: [Read, Write, Bash, Agent, WebSearch, WebFetch]
context: fork
agent: design-architect
---

# design-system — Orquestador del Flujo SDD (Etapa Design)

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el Spec esta listo, delegas la definicion del sistema visual al agente `design-architect`, y escribes el `DESIGN.md` resultante.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (solo `generate` esta soportado)
- **Path del spec**: primer argumento posicional tras el modo
- **Path del PRD** opcional mediante `--prd`
- **Path de DESIGN.md** opcional mediante `--design-file`

Si no hay argumento o el modo no es valido, informa:
> "Uso: `/wf-design-system generate <archivo_spec.md> [--prd <prd.md>] [--design-file DESIGN.md]`"

## Paso 2: Verificar el Spec

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Deten la ejecucion si ocurre cualquiera de estos casos:
   - hay HUs `[INCOMPLETO]`
   - hay items `[CRITICO]_(pendiente)_`
   - `status_sync: stale`
   - `status_sync: needs_review`
4. Si el archivo no parece un Spec SDD validado (no contiene "Historias de Usuario" y "Criterios de Aceptacion"), informa:
   > "Este archivo no parece un Spec SDD validado. Primero ejecuta los workflows de spec."

## Paso 2b: Obtener PRD

Si se paso `--prd <path>` en los argumentos, lee ese archivo directamente.

Si no se paso `--prd`:
1. Pregunta al usuario:
   > "¿Tienes un PRD del producto disponible? Proporciona la ruta al archivo o escribe `no` para continuar sin él."
2. Si el usuario proporciona una ruta: verifica que el archivo existe, leelo completo y guarda su contenido para el Paso 4.
3. Si el usuario responde `no` o deja en blanco: continua sin PRD.

El PRD enriquece la derivacion de Visual Personality con nombre, vision y audiencia reales del producto, pero no es bloqueante.

## Paso 2c: Research de apps de referencia

A partir del spec y el PRD (si esta disponible), identifica el contexto del producto:
- **Sector**: categoria principal (ej: "fintech", "salud y fitness", "productividad", "e-commerce")
- **Actor principal**: perfil del usuario (ej: "profesional autonomo", "usuario casual diario", "equipo de trabajo")
- **Flujos dominantes**: tipo de tareas principales (ej: "consulta de saldo y transacciones", "registro de actividad fisica", "gestion de proyectos")
- **Tono funcional**: caracter de la interaccion (ej: "rapido y utilitario", "motivador y gamificado", "confiable y profesional")

Con ese contexto, deriva 2-3 queries de busqueda adaptadas a este producto concreto — no uses plantillas fijas:
- Una query orientada a apps referentes del sector con diseno reconocido
- Una query orientada a patrones UI especificos de los flujos dominantes de esta app
- Una query adicional si el tono, audiencia o nicho lo justifican (ej: "award winning <sector> app design", "<sector> app dark mode inspiration")

Ejecuta las busquedas con WebSearch y extrae de los resultados:
- Nombres de apps mencionadas como referentes de diseno en la categoria
- Patrones especificos destacados (densidad, paleta, tipografia numerica, componentes frecuentes)

Guarda un resumen de 3-5 apps con una descripcion breve de cada una para usarlo en el Paso 4.
Si las busquedas no devuelven resultados utiles, continua sin research — el agente marcara DESIGN_GAP en Reference Apps.

## Paso 3: Determinar paths

- Si se paso `--design-file`, usa ese path.
- Si no, crea o actualiza `DESIGN.md` en el directorio raiz del producto:
  - si el spec esta en `features/<nombre>/`, usa dos niveles arriba
  - en otros casos, usa el mismo directorio del spec

Si el archivo ya existe, leelo completo para usarlo como base.

## Paso 4: Delegar al agente design-architect

Invoca al agente siguiendo la **Regla 2**, la **Regla 3**, la **Regla 6**, la **Regla 11** y la **Regla 12** de `kb-design-expert`: `DESIGN.md` es de producto, SSoT visual persistente, con secciones de Visual Personality y Reference Apps obligatorias ademas del orden canonico de Google design.md.

Usa este prompt:

```text
Modo: design-system
Path del spec: <path_spec>
Path del DESIGN.md destino: <path_design>
Contenido del Spec:
---
<contenido_completo_spec>
---
PRD del producto:
---
<contenido_prd_o_N/A>
---
Research de apps de referencia:
---
<resumen_research_o_N/A>
---
DESIGN.md actual:
---
<contenido_actual_o_N/A>
---
INSTRUCCION: produce un DESIGN.md de producto reutilizable por Stitch y futuras features. No introduzcas funcionalidades no presentes en el spec. Contrato visual persistente de producto, no de una sola feature.

Aplica las reglas de kb-design-expert que tienes en contexto:
- Regla 2: DESIGN.md es de producto, no de feature
- Regla 6: formato @google/design.md (front matter YAML + markdown), orden de secciones canonicas y token types validos
- Regla 11: Visual Personality derivada del PRD (si disponible) o del spec; obligatoria en todo DESIGN.md
- Regla 12: Reference Apps con el research (si disponible); obligatoria en todo DESIGN.md
- Si faltan datos criticos para jerarquia, tono o patrones base, devuelve DESIGN_GAPs y no produzcas archivo final

Formato de output: ver references/output_notes.md de esta skill.
```

## Paso 5: Manejar DESIGN_GAPs

Si el agente devuelve `DESIGN_GAP` o `DESIGN_GAPs`:
- informa la lista al usuario
- no escribas el archivo
- sugiere completar el spec o aportar contexto visual de producto

## Paso 6: Escribir y validar el resultado

1. Escribe el output del agente en el path destino como `DESIGN.md`.
2. Ejecuta el linter de Google design.md sobre el archivo generado:
   ```bash
   npx @google/design.md lint <path_design>
   ```
3. Segun el resultado:
   - **Sin errores**: confirma al usuario que el archivo supera la validacion `@google/design.md`.
   - **Con errores**: muestra la lista completa. Indica cuales requieren correccion manual (tokens rotos, referencias inexistentes, contraste WCAG insuficiente, orden de secciones canonicas incorrecto).
   - **npx no disponible o fallo de entorno**: informa al usuario e indica que puede ejecutarlo manualmente con `npx @google/design.md lint <path_design>`.

## Paso 7: Informar al usuario

- path del `DESIGN.md` generado
- resultado de la validacion del linter (OK, errores o no ejecutado)
- breve resumen del sistema visual: paleta principal, personalidad visual derivada y apps de referencia usadas
- siguiente paso recomendado:
  > "Ahora ejecuta `/wf-design-feature-prototype generate <feature_spec.md> [--design-file <DESIGN.md>]`"
