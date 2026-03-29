---
name: decompose-spec
description: Orquestador SDD para partir un Spec monolítico limpio en Specs por feature. Úsalo cuando tengas un _spec.md validado (sin pendientes, con los 6 elementos SDD) y quieras obtener un spec independiente por cada feature del proyecto. Genera un _features.md con el índice de features y shared models, y una carpeta features/<nombre>/<nombre>_spec.md por cada feature. Activa en frases como "parte el spec en features", "descompón el spec por features", "separa el spec en specs individuales", "crea un spec por feature", "divide el spec monolítico". No activa para analizar o generar specs (usa prepare-spec) ni para planificar (usa prepare-plan).
argument-hint: "<archivo_spec.md>"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
disable-model-invocation: true
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

Ejemplo para un spec en `docs/proyecto_spec.md`:
```
docs/proyecto_features.md
docs/features/authentication/authentication_spec.md
docs/features/services/services_spec.md
docs/features/time-tracking/time-tracking_spec.md
```

---

## Paso 6: Informar al usuario

- Path del `_features.md` generado
- Lista de features identificadas con sus rutas
- Tabla de shared models detectados
- Advertencia si hay features con pocos CAs (< 3) para que el usuario valide la partición
- Siguiente paso:
  > "Revisa `<path>_features.md` y ajusta el scope si es necesario. Luego, por cada feature ejecuta:"
  > ```
  > /prepare-plan generate features/<nombre>/<nombre>_spec.md
  > /prepare-tasks generate features/<nombre>/<nombre>_plan.md
  > ```
  > "Empieza por las features owner de shared models (marcadas en la tabla)."
