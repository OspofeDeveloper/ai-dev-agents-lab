---
name: decompose-spec
description: Orquestador SDD para partir un Spec monolítico limpio en Specs por feature. Úsalo cuando tengas un _spec.md validado (sin pendientes, con los 8 elementos SDD) y quieras obtener un spec independiente por cada feature del proyecto. Genera un _features.md con el índice de features y shared models, y una carpeta features/<nombre>/<nombre>_spec.md por cada feature. Activa en frases como "parte el spec en features", "descompón el spec por features", "separa el spec en specs individuales", "crea un spec por feature", "divide el spec monolítico". No activa para analizar o generar specs (usa prepare-spec) ni para planificar (usa prepare-plan).
argument-hint: "<archivo_spec.md>"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
disable-model-invocation: true
context: fork
agent: sdd-analyst
---

# decompose-spec — Orquestador de Partición SDD

Tu rol es de **orquestador puro**: verificas que el Spec está listo para ser partido, delegas la descomposición al agente `sdd-analyst` en modo `decompose`, y escribes los artefactos resultantes. No realizas la partición directamente.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del archivo spec.

Si no hay argumento, informa al usuario:
> "Uso: `/decompose-spec <archivo_spec.md>`"
>
> "Ejemplo: `/decompose-spec docs/proyecto_spec.md`"

---

## Paso 2: Verificar el Spec

1. Verifica que el archivo existe.
2. Verifica que el nombre termina en `_spec.md`. Si no → informa:
   > "Este archivo no parece un Spec procesado. Primero genera el spec con `/prepare-spec finalize <archivo.md>`"
3. Lee el archivo completo.
4. Comprueba que no contiene `_(pendiente)_` sin responder. Si los hay → lista cuáles y detén:
   > "El Spec tiene items pendientes. Completa el análisis antes de descomponer."
5. Verifica que contiene evidencia de Spec SDD válido (presencia de "Criterios de Aceptación" e "Historias de Usuario"). Si no → informa:
   > "Este archivo no parece un Spec SDD procesado. Primero ejecuta `/prepare-spec finalize <archivo.md>`"

---

## Paso 3: Leer el contenido

Lee el `_spec.md` en su totalidad.

---

## Paso 4: Delegar al agente sdd-analyst

Invoca el agente `sdd-analyst` pasándole como prompt:

```
Modo: decompose
Path del spec: <path_completo>
Contenido del Spec monolítico:
---
<contenido_completo_del_spec>
---
```

Espera a que el agente complete su ejecución y recibe su output.

El agente devolverá:
- El contenido de `_features.md` (índice de features + tabla de shared models)
- El contenido de cada `features/<nombre>/<nombre>_spec.md`

---

## Paso 4.5: Ownership checkpoint (bloqueo si hay ambigüedad)

Antes de escribir ningún artefacto, revisa el `_features.md` recibido del agente:

1. Busca en la tabla de Shared Models cualquier modelo que tenga:
   - Owner marcado como "AMBIGUO", "?" o vacío
   - Múltiples candidatos listados sin desempate explícito

2. **Si hay modelos sin owner definitivo:**
   - Presenta la tabla al usuario con los modelos ambiguos:
     ```
     | Modelo | Candidatos | Criterio aplicable (decompose-expert) |
     ```
   - Para cada modelo, aplica el criterio de desempate del decompose-expert y explica al usuario cuál candidato sale ganador y por qué
   - **Espera respuesta del usuario** confirmando o corrigiendo el owner propuesto
   - Actualiza el contenido del `_features.md` con el owner definitivo antes de continuar

3. **Si todos los modelos tienen owner claro** → continúa directamente al Paso 5.

---

## Paso 5: Escribir los artefactos

**Artefacto 1 — Índice de features**

Determina el path: mismo directorio que el spec + nombre base + `_features.md`
- Ejemplo: `docs/proyecto_spec.md` → `docs/proyecto_features.md`

Escribe el `_features.md` recibido del agente.

**Artefacto 2 — Specs por feature**

Para cada feature en el output del agente:
1. Determina el directorio: `<mismo_directorio_del_spec>/features/<nombre-feature>/`
2. Crea el directorio si no existe
3. Escribe el spec en `<nombre-feature>_spec.md`
4. Escribe el `README.md` de la feature en el mismo directorio

Ejemplo para un spec en `docs/proyecto_spec.md`:
```
docs/proyecto_features.md
docs/features/authentication/authentication_spec.md
docs/features/authentication/README.md
docs/features/services/services_spec.md
docs/features/services/README.md
docs/features/time-tracking/time-tracking_spec.md
docs/features/time-tracking/README.md
```

---

## Paso 5.5: Verificación automática de conflictos (no bloqueante)

Si se generaron **2 o más features**, invoca el agente `sdd-analyst` en modo `conflict` pasándole el contenido de todos los specs de feature generados:

```
Modo: conflict
Features a comparar: <N> specs

Contenido de [feature-1] ([path]):
---
<contenido>
---

Contenido de [feature-2] ([path]):
---
<contenido>
---

[... repetir por cada feature ...]
```

- Si el agente detecta conflictos → escribe el informe en `<directorio_base>_conflict_report.md` e incluye un aviso en el Paso 6.
- Si no detecta conflictos → solo menciona brevemente en el Paso 6 que no se detectaron conflictos.

Este paso es **informativo y no bloquea** el flujo. El usuario decide si resolver los conflictos antes de continuar con `/prepare-plan`.

---

## Paso 6: Informar al usuario

- Path del `_features.md` generado
- Lista de features identificadas con sus rutas
- Tabla de shared models detectados
- Advertencia si hay features con pocos CAs (< 3) para que el usuario valide la partición
- Resultado de la verificación de conflictos (Paso 5.5):
  - Sin conflictos: "✓ Sin conflictos detectados entre los specs generados."
  - Con conflictos: "⚠ Se detectaron conflictos. Revisa `<path>_conflict_report.md` antes de continuar con `/prepare-plan` en las features afectadas."
- Siguiente paso:
  > "Revisa `<path>_features.md` y ajusta el scope si es necesario. Luego, por cada feature ejecuta:"
  > ```
  > /prepare-plan features/<nombre>/<nombre>_spec.md
  > /prepare-tasks features/<nombre>/<nombre>_plan.md
  > ```
  > "Empieza por las features owner de shared models (marcadas en la tabla)."
