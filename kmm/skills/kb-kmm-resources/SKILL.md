---
name: kb-kmm-resources
description: "Base de conocimiento sobre recursos compartidos en Compose Multiplatform: strings, imágenes, fonts, raw files y localización con compose.resources."
argument-hint: "tema a consultar (opcional): strings, images, fonts, raw, localization"
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Compose Multiplatform — Recursos Compartidos (compose.resources)

---

## Contrato de Recursos

Invariantes de arquitectura para recursos en KMM:

- **Todos los recursos compartidos en `commonMain/composeResources/`**: strings, drawables, fonts y raw files. Nunca en `androidMain` ni `iosMain` si son compartidos.
- **Acceso siempre vía `Res`**: usar las funciones de `org.jetbrains.compose.resources` (`stringResource`, `painterResource`, `Font`, `Res.readBytes`). Nunca hardcodear strings ni rutas.
- **`stringResource()` en Composables, `getString()` fuera solo cuando procede**: `getString()` es suspend y solo debe usarse fuera de Composables cuando el caso realmente necesita un `String` resuelto en ese punto. Si el proyecto usa `UiText`, ViewModels no resuelven strings; exponen referencias y la UI las resuelve.
- **Localización con carpetas `values-{locale}/`**: el archivo `strings.xml` por defecto va en `values/`; las traducciones en `values-es/`, `values-fr/`, etc.
- **`@StringRes` prohibido en `commonMain`**: es una API Android-only. Usar `StringResource` de `compose.resources`.
- **Recursos platform-specific fuera de `commonMain`**: launch icons, splash screens y assets nativos van en `androidApp/` o `iosApp/`, no en `commonMain`.

Todo lo que sigue es la implementación de este contrato.

---

## 1. Setup y estructura de directorios

El módulo compartido (`shared`) declara `compose.components.resources` en `commonMain.dependencies`. La configuración `compose.resources { ... }` en `build.gradle.kts` del módulo controla la visibilidad de la clase `Res`, el paquete generado y cuándo se genera la clase.

Los recursos se organizan bajo `commonMain/composeResources/` en subcarpetas por tipo:

| Carpeta | Contenido |
|---|---|
| `values/` | Strings XML y plurals |
| `values-{locale}/` | Traducciones (mismo `strings.xml`) |
| `drawable/` | PNG, JPEG, WebP, SVG/XML vector |
| `font/` | TTF, OTF |
| `files/` | Archivos raw (JSON, binarios, etc.) |

- Para la configuración Gradle completa y la estructura de directorios, ver [setup-and-structure.md](references/setup-and-structure.md)

---

## 2. String resources

### 2.1 Definición

Los strings se declaran en `commonMain/composeResources/values/strings.xml`. Soportan argumentos posicionales (`%1$s`, `%1$d`) y plurals. Las traducciones van en carpetas `values-{locale}/` con el mismo nombre de archivo.

### 2.2 Uso en Composables

```kotlin
// Simple
Text(text = stringResource(Res.string.login_title))

// Con argumento
Text(text = stringResource(Res.string.profile_greeting, userName))

// Plural
Text(text = pluralStringResource(Res.plurals.items_count, count, count))
```

### 2.3 Uso fuera de Composables

`getString()` es suspend y requiere un coroutine scope. No puede usarse en inicialización síncrona.

Si el proyecto usa `kb-kmm-ui-text`, el ViewModel no debe resolver strings; debe exponer `UiText` y delegar la resolución a la UI.

`getString()` queda reservado para casos donde realmente se necesita el string materializado fuera de un Composable, por ejemplo:

- texto que se envía a una API o share sheet
- adapters o bridges que no operan con `UiText`
- utilidades de infraestructura o composición externa a la UI

```kotlin
suspend fun buildShareText(): String = getString(Res.string.share_message)
```

- Para el XML completo de strings y ejemplos de localización, ver [string-resources.md](references/string-resources.md)

---

## 3. Imágenes, fonts y raw files

### 3.1 Imágenes (`drawable/`)

Soportan PNG, JPEG, BMP, WebP y SVG (como XML vector drawable). Se accede con `painterResource(Res.drawable.nombre)`.

### 3.2 Fonts (`font/`)

Se carga con `Font(Res.font.nombre)` dentro de un `FontFamily`. El bloque es `@Composable`.

### 3.3 Raw files (`files/`)

Se leen con `Res.readBytes("files/nombre.ext")`, que es `suspend` y devuelve `ByteArray`. Apto para JSON de configuración, archivos de datos, etc.

- Para código completo de los tres tipos, ver [image-font-raw.md](references/image-font-raw.md)

---

## Requisitos NO Negociables

### Obligatorio

- Strings y drawables compartidos en `commonMain/composeResources/`
- `stringResource()` para textos en Composables
- `getString()` solo cuando realmente se necesita el `String` resuelto fuera de UI
- `painterResource()` para imágenes compartidas
- Soporte de localización con carpetas `values-{locale}/`

### Prohibido

- Hardcodear strings en Composables
- `@StringRes` en `commonMain` — API de Android, no disponible en iOS
- Recursos platform-specific (launch icons, splash screens) en `commonMain`
- Resolver strings en ViewModels si el proyecto adopta el patrón `UiText`

---

**Version**: 2.0.0
**Última actualización**: 2026-04-11
**Compatibilidad**: Compose Multiplatform 1.6+, Kotlin 2.0+
