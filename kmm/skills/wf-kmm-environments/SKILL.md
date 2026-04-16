---
name: wf-kmm-environments
description: "Configura un sistema multi-brand/multi-environment en un proyecto KMM: Android (Gradle product flavors + BuildConfig) e iOS (XCConfig + Script Build Phase). Usar cuando el usuario quiera configurar entornos, flavors, variantes de build o multi-brand en un proyecto KMM. Activar con frases como 'configurar entornos', 'añadir pre/pro', 'configurar flavors', 'configurar variantes de build', 'añadir staging/production', 'setup environments', 'multi-brand KMM'."
argument-hint: "[brands y entornos, ej: 'pre pro' o 'cuideo felizvita con pre y pro']"
effort: high
allowed-tools: [Read, Write, Edit, Bash]
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

## Paso 3 — Consultar kb-kmm-environments

Consultar las reglas del skill `kb-kmm-environments` para obtener los criterios técnicos canónicos que guían los pasos 4–8. En particular las reglas sobre el plugin BuildConfig, prioridad de resolución brand/env, estructura de ficheros, jerarquía XCConfig y valores sensibles.

---

## Paso 4 — Registrar el plugin BuildConfig

En `gradle/libs.versions.toml`, añadir el plugin gmazzo si no está presente siguiendo la **Regla 2** del kb-. Si ya existe el plugin con otra versión, usar la versión existente.

Consultar `kb-kmm-environments/references/android_buildconfig_templates.md § libs.versions.toml` para el snippet exacto.

---

## Paso 4b — Sincronizar Gradle

Ejecutar un sync de Gradle para que el IDE resuelva el plugin recién declarado y sus dependencias estén disponibles antes de editar `build.gradle.kts`:

```bash
./gradlew --quiet help
```

Esperar a que termine sin errores antes de continuar. Si el sync falla, revisar que el plugin se añadió correctamente en `libs.versions.toml`.

---

## Paso 5 — Configurar Android

En `composeApp/build.gradle.kts`, realizar tres acciones siguiendo las **Reglas 2, 3 y 5** del kb-:

1. Aplicar el plugin al bloque `plugins { }`.
2. Declarar `flavorDimensions` y `productFlavors` dentro de `android { }` con los datos de Paso 1.
3. Añadir el bloque `buildConfig { }` después de `android { }`. El bloque siempre incluye el scaffold de resolución brand/env y la carga de properties. Los `buildConfigField` se añaden **únicamente** para las variables que el usuario especificó en el Paso 1 — ni más ni menos. No añadir `BRAND`, `IS_PRE` ni ningún otro campo por iniciativa propia.

Consultar `kb-kmm-environments/references/android_buildconfig_templates.md` para los templates de cada sección. Para 3+ entornos, usar la variante `§ Lógica de resolución para 3+ entornos`.

---

## Paso 6 — Crear ficheros .properties

Crear un fichero `.properties` por variante brand×env en la **raíz del proyecto** siguiendo la **Regla 5** del kb-. Solo incluir valores que Gradle no puede derivar (URLs, API keys). No incluir `BRAND` ni `IS_PRE`.

Consultar la **Regla 8** del kb- para decidir qué valores son seguros de commitear. Consultar `kb-kmm-environments/references/android_properties_templates.md` para la estructura de cada fichero.

---

## Paso 7 — Configurar iOS

### 7a. Crear la jerarquía XCConfig

Crear en `iosApp/Configuration/` los ficheros XCConfig siguiendo la **Regla 6** del kb- para la jerarquía de includes. Consultar `kb-kmm-environments/references/ios_xcconfig_templates.md` para los templates completos de cada fichero.

### 7b. Targets, Build Configurations y Schemes en Xcode

> **Instrucciones manuales para el usuario** — estos pasos los ejecuta el usuario en Xcode, no el agente.

Ver **Regla 7** del kb- para la relación target/build configuration/scheme y el árbol de decisión. Los sub-pasos deben ejecutarse en orden.

**7b-1. Añadir Build Configurations (siempre, para todo proyecto con N envs)**

En la pestaña **Info** del proyecto Xcode, sección Configurations:
1. Duplicar `Debug` una vez por cada env → renombrar a `Debug-{Env1}`, `Debug-{Env2}`, …
2. Duplicar `Release` una vez por cada env → renombrar a `Release-{Env1}`, `Release-{Env2}`, …
3. Eliminar las filas `Debug` y `Release` originales si ya no se usarán (opcional, pero evita confusión).

**7b-2. Añadir targets adicionales (solo si brands.size > 1)**

Por cada brand adicional (brand2, brand3, …):
1. File → Duplicate Target → seleccionar el target `iosApp`
2. Renombrarlo a `{Brand}App`
3. En Build Settings del nuevo target, revisar Bundle Identifier y Display Name

Si solo hay 1 brand, omitir este sub-paso.

**7b-3. Enlazar XCConfig a cada Build Configuration (dos niveles)**

Para cada fila de Build Configuration creada en 7b-1, en la pestaña Info → Configurations:
- Columna del **proyecto**: asignar `Debug.xcconfig` a las filas `Debug-{Env}` y `Release.xcconfig` a las filas `Release-{Env}`
- Columna de cada **target**: asignar el `{Brand}/{Brand}-{Env}.xcconfig` correspondiente

Consultar la tabla de asignación de la **Regla 7** del kb- para el mapeo exacto.

**7b-4. Crear Schemes (uno por brand×env)**

Product → Scheme → New Scheme → seleccionar el target del brand correspondiente:
1. Nombrar el scheme `{Brand}-{Env}` (ej. `Brand1-Pre`, `Cuideo-Pro`)
2. Editar el scheme (Edit Scheme):
   - Acción **Run** → Build Configuration: `Debug-{Env}`
   - Acción **Archive** → Build Configuration: `Release-{Env}`
   - Resto de acciones (Test, Profile, Analyze): `Debug-{Env}`

### 7c. Script Build Phase

Cada target necesita un **Run Script Build Phase**. Seguir la **Regla 4** del kb- para entender el flujo `${APP_ENV}` → Gradle. Consultar `kb-kmm-environments/references/ios_script_build_phase_template.md` para el script de cada target.

---

## Paso 8 — Informar al usuario

Tras aplicar todos los cambios, reportar:

- Lista de ficheros creados o modificados
- Si hubo pasos manuales de Xcode pendientes (7b): recordárselos explícitamente
- Referencia de uso post-configuración: leer `kb-kmm-environments/references/usage_reference.md` y mostrar su contenido al usuario
- Siguiente paso sugerido: verificar el build ejecutando la variante por defecto en Android y seleccionando un scheme en Xcode
