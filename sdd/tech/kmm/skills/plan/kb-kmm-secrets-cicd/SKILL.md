---
name: kb-kmm-secrets-cicd
description: Mecánica de transporte de secretos en CI/CD para KMM: cómo llevar API keys, client secrets y signing keys desde local y CI hasta Android (BuildConfig) e iOS (xcconfig) sin commitearlos. Materializa la política de config sensible de kb-kmm-environments (Regla 7). Úsalo cuando el plan deba decidir cómo inyectar valores sensibles en el build.
allowed-tools: [Read]
effort: low
user-invocable: false
---

# Secretos en CI/CD para KMM — Planificación

Esta KB aporta la **mecánica concreta** de transporte de secretos. NO redefine la política:

→ **Política** de config sensible (qué se commitea y qué no, que CI inyecta): `kb-kmm-environments` **Regla 7** (SSoT). Esta skill la referencia y la materializa, no la reescribe.
→ **Materialización por variante/plataforma** (flavors, BuildConfig, XCConfig): `kb-kmm-android-environments`, `kb-kmm-ios-environments`. Esta skill no duplica cómo se declaran las variantes; solo cómo el **valor sensible** entra en ese mecanismo.

La política, en una línea: los secretos no se commitean; CI los inyecta en build sin romper la matriz de variantes (Regla 7 de `kb-kmm-environments`). El resto es transporte.

## Qué es secreto y qué no

| Sensible (no se commitea) | No sensible (puede vivir versionado) |
|---|---|
| API keys, client secrets, signing keystore + passwords, tokens de servicios | URLs base públicas, flags de entorno, identificadores no secretos |

La distinción es la de la Regla 7. Esta skill solo se ocupa del lado sensible.

## Transporte local (desarrollador)

Para no commitear el secreto en el repo:

- `local.properties` (gitignored por convención Android) o `gradle.properties` en `$HOME/.gradle/` (fuera del repo) — el dev pone ahí su valor.
- Gradle lee la propiedad y la expone al build. El fichero **nunca** entra en git.

`$HOME/.gradle/gradle.properties` es preferible para secretos personales: vive fuera del repo, no hay riesgo de commit accidental.

## Transporte en CI

CI no tiene `local.properties`: el valor viaja por el secret store del runner.

```
GitHub Secret  →  env var del job  →  propiedad Gradle  →  BuildConfig / xcconfig
```

- El secreto se guarda en el secret store del CI (GitHub Secrets, etc.).
- El job lo expone como variable de entorno.
- Gradle la recibe como propiedad: `ORG_GRADLE_PROJECT_<nombre>` (env var que Gradle mapea a propiedad de proyecto) o `-P<nombre>=...` en la invocación.
- Desde la propiedad, el build la inyecta en Android/iOS (abajo).

## Inyección en Android (BuildConfig field desde Gradle property)

El valor llega a código vía un `buildConfigField` alimentado por la propiedad Gradle (no hardcodeado):

```kotlin
val apiKey = providers.gradleProperty("API_KEY").orNull ?: ""
buildConfigField("String", "API_KEY", "\"$apiKey\"")
```

La declaración del BuildConfig field por variante es de `kb-kmm-android-environments`; aquí solo importa que el valor **viene de la propiedad**, no del fuente.

## Inyección en iOS (xcconfig / build settings)

En iOS el valor entra por `.xcconfig` o build setting:

- el `.xcconfig` con el secreto se genera en CI desde la env var (no se commitea), o
- el build setting se inyecta vía script de build desde la variable de entorno.

El detalle de XCConfig/scheme es de `kb-kmm-ios-environments`; aquí solo el origen del valor (env de CI, no versionado).

## Signing keystore en CI

La keystore de firma es binaria y no se commitea:

1. base64-encode de la keystore → se guarda como secret de CI.
2. en el job: decode del secret a un fichero temporal.
3. Gradle firma con ese fichero + el password (otro secret) vía propiedades.
4. el fichero temporal se descarta al terminar el job.

## Qué NUNCA va a git

- keystores, `.jks`, `.p12`, claves privadas
- ficheros con secretos en claro (`local.properties`, `secrets.properties`)
- BuildConfig/xcconfig con el valor hardcodeado

El plan declara el `.gitignore` de estas rutas como parte del setup.

## Qué debe contemplar el plan

1. Qué valores son secretos (criterio de la Regla 7) y cuáles públicos.
2. Origen del valor por entorno: local (`$HOME/.gradle` o `local.properties`) vs CI (secret store).
3. Cómo cada secreto llega a Android (BuildConfig field desde property) e iOS (xcconfig/build setting).
4. Si hay firma: estrategia keystore base64 en CI.
5. Entradas de `.gitignore` para todo lo sensible.

## Relación con otras skills del plan

- Política de sensibilidad (SSoT): `kb-kmm-environments` Regla 7
- Materialización por variante: `kb-kmm-android-environments`, `kb-kmm-ios-environments`
- Catálogo de variantes que consume estos valores: `kb-kmm-brands`, `kb-kmm-environments`
