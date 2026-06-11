---
name: kb-kmm-ios-environments
description: "Base de conocimiento de implementación iOS del sistema multi-brand/multi-environment en KMM: XCConfig, target/build configuration/scheme, flujo XCConfig → Script Build Phase → Gradle y estructura de ficheros en Xcode."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# iOS Environments KMM — Base de Conocimiento

## Regla 1: Esta skill implementa iOS, no define la semántica global

Esta skill describe cómo materializar en iOS la matriz `brand × env`.

No define:

- qué significa `brand`
- qué significa `env`
- qué valores forman parte del contrato compartido
- la política general de sensibilidad

Esas reglas viven en:

- `kb-kmm-brands`
- `kb-kmm-environments`

---

## Regla 2: iOS usa XCConfig como fuente operativa de variante

La materialización iOS se basa en:

- `XCConfig`
- target
- build configuration
- scheme
- script build phase

La selección del scheme y la configuración activa en Xcode determinan la variante que iOS materializa.

---

## Regla 3: Flujo XCConfig → Script → Gradle

El flujo operativo estándar es:

1. el desarrollador selecciona un scheme
2. el scheme activa un target y una build configuration
3. el XCConfig asociado expone valores como `APP_ENV`
4. el script build phase lee esos valores
5. el script invoca Gradle con propiedades explícitas

La implementación concreta de ese script vive en `${CLAUDE_SKILL_DIR}/references/ios_script_build_phase_template.md`.

---

## Regla 4: La jerarquía XCConfig separa capas compartidas y variante

La configuración iOS distingue:

- un nivel compartido
- un nivel debug/release
- un nivel brand×env

El archivo brand×env no debe absorber por sí solo la capa debug/release; ambas se asignan desde la configuración de Xcode.

→ Templates: `${CLAUDE_SKILL_DIR}/references/ios_xcconfig_templates.md`

---

## Regla 5: Target, Build Configuration y Scheme son responsabilidades distintas

En iOS:

- el target representa la unidad de compilación de una marca
- la build configuration representa la capa debug/release × env
- el scheme elige qué combinación se activa por acción

No deben confundirse como si fueran el mismo mecanismo.

---

## Regla 6: La implementación iOS no define Android

Esta skill no contiene reglas de:

- plugin BuildConfig
- product flavors Android
- `.properties`
- resolución por nombre de tarea Gradle

La implementación Android pertenece a `kb-kmm-android-environments`.

---

## Regla 7: Los valores que el script pasa a Gradle deben ser mínimos y explícitos

El script build phase no debe reconstruir lógica de variante más allá de pasar a Gradle las propiedades necesarias para identificar la variante activa.

La semántica de la variante ya viene resuelta por:

- target
- build configuration
- scheme
- XCConfig

→ Templates: `${CLAUDE_SKILL_DIR}/references/ios_script_build_phase_template.md`

---

## Regla 8: Troubleshooting iOS pertenece a esta dimensión

Los errores relacionados con:

- XCConfig no enlazado
- `APP_ENV` vacío
- target equivocado
- scheme incorrecto
- build configuration mal asignada

se tratan en esta dimensión y no en la skill semántica global.
