---
name: kb-kmm-android-environments
description: "Base de conocimiento de implementación Android del sistema multi-brand/multi-environment en KMM: product flavors, plugin BuildConfig (gmazzo), resolución brand/env, ficheros .properties y generación del contrato compartido."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Android Environments KMM — Base de Conocimiento

## Regla 1: Esta skill implementa Android, no define la semántica global

Esta skill describe cómo materializar en Android la matriz `brand × env`.

No define:

- qué significa `brand`
- qué significa `env`
- qué valores deben existir por variante
- la política de sensibilidad de secretos

Esas reglas viven en:

- `kb-kmm-brands`
- `kb-kmm-environments`

---

## Regla 2: El plugin BuildConfig materializa el contrato compartido

La implementación Android usa `com.github.gmazzo.buildconfig` para generar un objeto accesible desde `commonMain`.

Si el proyecto ya tiene ese plugin con otra versión, se usa la versión existente.

→ Templates: `${CLAUDE_SKILL_DIR}/references/android_buildconfig_templates.md`

---

## Regla 3: Android modela las variantes con flavors por dimensión

La materialización Android usa:

- una dimensión de flavor para `brand`
- una dimensión de flavor para `env`

La combinación de ambas dimensiones produce las variantes Android.

→ Templates: `${CLAUDE_SKILL_DIR}/references/android_buildconfig_templates.md`

---

## Regla 4: La resolución de `brand` y `env` tiene prioridad explícita

El orden de resolución es:

```text
1. Propiedades Gradle explícitas
2. Inferencia desde nombre de tarea
3. Valores por defecto
```

La prioridad explícita es la vía estable para CI y para cualquier integración donde no convenga depender del nombre de la tarea.

→ Templates: `${CLAUDE_SKILL_DIR}/references/android_buildconfig_templates.md`

---

## Regla 5: Los `.properties` solo almacenan valores declarativos

Los ficheros `{brand}-{env}.properties` viven en la raíz del proyecto.

Solo contienen valores que Android no puede derivar automáticamente a partir de `brand` y `env`.

No deben usarse para persistir valores puramente derivados si el propio bloque `buildConfig` ya puede calcularlos.

→ Templates: `${CLAUDE_SKILL_DIR}/references/android_properties_templates.md`

---

## Regla 6: El bloque `buildConfig` combina scaffold fijo y campos de proyecto

La implementación Android tiene dos zonas distintas:

- un scaffold fijo de resolución de variante y carga de properties
- los `buildConfigField` concretos que el proyecto necesita exponer

La skill no obliga a exponer todos los campos posibles; solo los que el proyecto haya decidido publicar en su contrato compartido.

→ Templates: `${CLAUDE_SKILL_DIR}/references/android_buildconfig_templates.md`

---

## Regla 7: La implementación Android no define iOS

Esta skill no contiene reglas de:

- `XCConfig`
- schemes
- build configurations de Xcode
- scripts build phase

La implementación de iOS pertenece a `kb-kmm-ios-environments`.

---

## Regla 8: Troubleshooting Android pertenece a esta dimensión

Los errores relacionados con:

- plugin BuildConfig
- flavors Android
- carga de `.properties`
- resolución `-Papp.brand` / `-Papp.env`

se tratan en esta dimensión y no en la skill semántica global.
