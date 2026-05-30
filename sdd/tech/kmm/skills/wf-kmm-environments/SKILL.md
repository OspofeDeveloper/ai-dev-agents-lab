---
name: wf-kmm-environments
description: "Configura un sistema multi-brand/multi-environment en un proyecto KMM componiendo semántica estable de variantes y sus implementaciones Android e iOS."
when_to_use: "Activa con frases como 'configura entornos en KMM', 'añade multi-environment al proyecto', 'setup de variantes por brand', 'necesito pre y pro en KMM', 'configura multi-brand'. No activa para el stack completo (usa wf-kmm-stack-setup-ktor-keycloak-koin) ni para configurar solo networking (usa wf-kmm-network-setup)."
argument-hint: "[brands y entornos, ej: 'pre pro' o 'cuideo felizvita con pre y pro']"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-platform-integrator
---

# wf-kmm-environments

Configura un sistema multi-brand/multi-environment en un proyecto KMM componiendo semántica estable y sus implementaciones por plataforma.

---

## Paso 1: Recopilar requisitos

Si el usuario no ha especificado todos los parámetros, preguntar:

1. **Brands** — ¿Cuántas marcas? ¿Nombres y Application IDs?
2. **Entornos** — ¿Qué entornos de build? ¿Alguno añade sufijo al App ID?
3. **URLs de API** — Una URL base por combinación brand×env.
4. **Variables adicionales** — API keys, feature flags, claves de analytics que varíen por variante.

Cuando tengas los datos, calcular la matriz `brand × env` y confirmarla con el usuario antes de tocar ningún fichero, siguiendo la **Regla 2** de `kb-kmm-environments` y la **Regla 2** de `kb-kmm-brands`.

---

## Paso 2: Leer el estado actual del proyecto

Leer estos ficheros para entender qué hay y qué falta:

- `gradle/libs.versions.toml`
- `composeApp/build.gradle.kts`
- `iosApp/iosApp.xcodeproj/project.pbxproj` (targets y schemes existentes)
- `iosApp/Configuration/` (verificar si ya existen XCConfigs)

---

## Paso 3: Consultar la semántica estable de variantes

Consultar `kb-kmm-brands` y `kb-kmm-environments` para fijar:

- catálogo de brands
- matriz `brand × env`
- valores declarativos vs derivados
- sensibilidad de variables
- contrato compartido que consumirá `commonMain`

Usar como ancla:

- `kb-kmm-brands` -> **Regla 1**, **Regla 2** y **Regla 4**
- `kb-kmm-environments` -> **Regla 1**, **Regla 2**, **Regla 4**, **Regla 5** y **Regla 7**

---

## Paso 4: Aplicar implementación Android

Consultar `kb-kmm-android-environments` para:

- registrar el plugin BuildConfig
- configurar flavor dimensions y productFlavors
- implementar resolución `brand/env`
- declarar los `buildConfigField` del contrato compartido
- crear `.properties` solo para valores declarativos

Usar como ancla la **Regla 2**, la **Regla 3**, la **Regla 4** y la **Regla 5** de `kb-kmm-android-environments`.

---

## Paso 5: Sincronizar Gradle

Ejecutar un sync de Gradle para verificar que el plugin recién declarado y sus dependencias quedan resolubles antes de seguir. Si falla, revisar primero la declaración en `libs.versions.toml`.

---

## Paso 6: Aplicar implementación iOS

Consultar `kb-kmm-ios-environments` para:

- crear jerarquía XCConfig
- preparar targets, build configurations y schemes
- añadir el script build phase
- pasar a Gradle solo las propiedades mínimas de variante

Usar como ancla la **Regla 2**, la **Regla 3**, la **Regla 4** y la **Regla 7** de `kb-kmm-ios-environments`.

Si el proyecto requiere pasos manuales en Xcode, derivarlos desde las references de `kb-kmm-ios-environments`; no convertir esta workflow en la fuente normativa de esos pasos.

---

## Paso 7: Informar al usuario

Tras aplicar todos los cambios, reportar:

- Lista de ficheros creados o modificados
- Si hubo pasos manuales de Xcode pendientes (Paso 6): recordárselos explícitamente
- Referencia de uso post-configuración: leer `${CLAUDE_SKILL_DIR}/../plan/kb-kmm-environments/references/usage_reference.md` del skill `kb-kmm-environments` y mostrar su contenido al usuario
- Siguiente paso sugerido: verificar el build ejecutando la variante por defecto en Android y seleccionando un scheme en Xcode
