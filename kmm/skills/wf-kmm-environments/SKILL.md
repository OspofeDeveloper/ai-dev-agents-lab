---
name: wf-kmm-environments
description: "Configura un sistema multi-brand/multi-environment en un proyecto KMM: Android (Gradle product flavors + BuildConfig) e iOS (XCConfig + Script Build Phase). Usar cuando el usuario quiera configurar entornos, flavors, variantes de build o multi-brand en un proyecto KMM. Activar con frases como 'configurar entornos', 'añadir pre/pro', 'configurar flavors', 'configurar variantes de build', 'añadir staging/production', 'setup environments', 'multi-brand KMM'."
argument-hint: "[brands y entornos, ej: 'pre pro' o 'cuideo felizvita con pre y pro']"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-implementer
---

# wf-kmm-environments

Configura un sistema multi-brand/multi-environment en un proyecto KMM. El resultado es un objeto `BuildConfig` compartido en `commonMain`, conectado con Android (Gradle product flavors) e iOS (XCConfig + Script Build Phase).

---

## Paso 1 — Recopilar requisitos

Si el usuario no ha especificado todos los parámetros, preguntar:

1. **Brands** — ¿Cuántas marcas? ¿Nombres y Application IDs?
2. **Entornos** — ¿Qué entornos de build? ¿Alguno añade sufijo al App ID?
3. **URLs de API** — Una URL base por combinación brand×env.
4. **Variables adicionales** — API keys, feature flags, claves de analytics que varíen por variante.

Cuando tengas los datos, calcular la **matriz de variantes** y confirmarla con el usuario antes de tocar ningún fichero:

```
Variantes a generar:
  {brand1}-{env1}  →  {appId1}.{env1suffix}    URL: https://...
  {brand1}-{env2}  →  {appId1}                 URL: https://...
  {brand2}-{env1}  →  {appId2}.{env1suffix}    URL: https://...
  {brand2}-{env2}  →  {appId2}                 URL: https://...
```

---

## Paso 2 — Leer el estado actual del proyecto

Leer estos ficheros para entender qué hay y qué falta:

- `gradle/libs.versions.toml`
- `composeApp/build.gradle.kts`
- `iosApp/iosApp.xcodeproj/project.pbxproj` (targets y schemes existentes)
- `iosApp/Configuration/` (verificar si ya existen XCConfigs)

---

## Paso 3 — Consultar la semántica estable de variantes

Consultar `kb-kmm-brands` y `kb-kmm-environments` para fijar:

- catálogo de brands
- matriz `brand × env`
- valores declarativos vs derivados
- sensibilidad de variables
- contrato compartido que consumirá `commonMain`

---

## Paso 4 — Aplicar implementación Android

Consultar `kb-kmm-android-environments` para:

- registrar el plugin BuildConfig
- configurar flavor dimensions y productFlavors
- implementar resolución `brand/env`
- declarar los `buildConfigField` del contrato compartido
- crear `.properties` solo para valores declarativos

---

## Paso 5 — Sincronizar Gradle

Ejecutar un sync de Gradle para que el IDE resuelva el plugin recién declarado y sus dependencias estén disponibles antes de editar `build.gradle.kts`:

```bash
./gradlew --quiet help
```

Esperar a que termine sin errores antes de continuar. Si el sync falla, revisar que el plugin se añadió correctamente en `libs.versions.toml`.

---

## Paso 6 — Aplicar implementación iOS

Consultar `kb-kmm-ios-environments` para:

- crear jerarquía XCConfig
- preparar targets, build configurations y schemes
- añadir el script build phase
- pasar a Gradle solo las propiedades mínimas de variante

> **Instrucciones manuales para el usuario** — estos pasos los ejecuta el usuario en Xcode, no el agente.

Los sub-pasos manuales de Xcode deben ejecutarse en orden.

**6a. Añadir Build Configurations**

En la pestaña **Info** del proyecto Xcode, sección Configurations:
1. Duplicar `Debug` una vez por cada env → renombrar a `Debug-{Env1}`, `Debug-{Env2}`, …
2. Duplicar `Release` una vez por cada env → renombrar a `Release-{Env1}`, `Release-{Env2}`, …
3. Eliminar las filas `Debug` y `Release` originales si ya no se usarán (opcional, pero evita confusión).

**6b. Añadir targets adicionales si hay más de una brand**

Por cada brand adicional (brand2, brand3, …):
1. File → Duplicate Target → seleccionar el target `iosApp`
2. Renombrarlo a `{Brand}App`
3. En Build Settings del nuevo target, revisar Bundle Identifier y Display Name

Si solo hay 1 brand, omitir este sub-paso.

**6c. Enlazar XCConfig a cada Build Configuration**

Para cada fila de Build Configuration creada en 6a, en la pestaña Info → Configurations:
- Columna del **proyecto**: asignar `Debug.xcconfig` a las filas `Debug-{Env}` y `Release.xcconfig` a las filas `Release-{Env}`
- Columna de cada **target**: asignar el `{Brand}/{Brand}-{Env}.xcconfig` correspondiente

**6d. Crear Schemes**

Product → Scheme → New Scheme → seleccionar el target del brand correspondiente:
1. Nombrar el scheme `{Brand}-{Env}` (ej. `Brand1-Pre`, `Cuideo-Pro`)
2. Editar el scheme (Edit Scheme):
   - Acción **Run** → Build Configuration: `Debug-{Env}`
   - Acción **Archive** → Build Configuration: `Release-{Env}`
   - Resto de acciones (Test, Profile, Analyze): `Debug-{Env}`

**6e. Script Build Phase**

Cada target necesita un **Run Script Build Phase**.

---

## Paso 7 — Informar al usuario

Tras aplicar todos los cambios, reportar:

- Lista de ficheros creados o modificados
- Si hubo pasos manuales de Xcode pendientes (Paso 6): recordárselos explícitamente
- Referencia de uso post-configuración: leer `references/usage_reference.md` del skill `kb-kmm-environments` y mostrar su contenido al usuario
- Siguiente paso sugerido: verificar el build ejecutando la variante por defecto en Android y seleccionando un scheme en Xcode
