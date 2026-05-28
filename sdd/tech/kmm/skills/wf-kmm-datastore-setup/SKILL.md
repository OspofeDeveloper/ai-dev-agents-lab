---
name: wf-kmm-datastore-setup
description: "Configura Preferences DataStore en un proyecto KMM componiendo arquitectura por capas, wiring de DI y providers por plataforma sin mezclar storage local con auth o networking."
argument-hint: "[ámbito del storage, módulo destino, DI activa y consumers previstos]"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-platform-integrator
---

# wf-kmm-datastore-setup

## Paso 1: Confirmar ownership y consumers

Antes de crear nada, confirmar o inferir:

1. si el storage es transversal (`core`) o propio de una feature
2. qué consumer lo va a usar: auth, settings, app state o una feature concreta
3. qué DI está activa, siguiendo `kb-koin` si aplica
4. qué plataformas están activas y cómo se resuelven dependencias nativas

Aplicar:

- `kb-kmm-core-layer`
- `kb-kmm-feature-clean-architecture`
- `kb-kmm-datastore-preferences`

---

## Paso 2: Crear primero la base técnica compartida

Crear la pieza común de `Preferences DataStore` en `commonMain`, siguiendo la **Regla 2** y la **Regla 10** de `kb-kmm-datastore-preferences`.

Esto incluye:

- factory común
- nombre de fichero
- utilidades realmente compartidas, si hacen falta

No introducir todavía keys de negocio ni lógica de auth.

---

## Paso 3: Crear providers por plataforma

Implementar la resolución del path físico por plataforma, siguiendo la **Regla 3** de `kb-kmm-datastore-preferences`.

En particular:

- `androidMain` usa `Context`
- `iosMain` usa filesystem nativo

No mezclar aquí wiring de repositorios ni consumers de dominio.

---

## Paso 4: Crear keys y adapter con semántica explícita

Crear encima del `DataStore<Preferences>` una pieza con intención clara, siguiendo la **Regla 5** y la **Regla 6** de `kb-kmm-datastore-preferences`.

Ejemplos válidos:

- `SessionLocalDataSource`
- `SettingsStore`
- `UserPreferencesRepository`

Agrupar keys junto a esa pieza o en un fichero de keys del mismo ámbito.

---

## Paso 5: Mantener separado storage local de coordinación remota

Si el consumer final también usa red o auth, no mezclar por defecto:

- persistencia local en DataStore
- llamadas remotas
- refresh de sesión

Seguir la **Regla 8** de `kb-kmm-datastore-preferences` y dejar el adapter local separado de la coordinación superior, salvo que el proyecto ya tenga una razón clara para otra cosa.

---

## Paso 6: Registrar en DI sin convertirla en fuente normativa

Registrar:

- provider de `DataStore<Preferences>`
- adapter/store/repositorio local que lo consume

Seguir:

- `kb-koin` para el wiring
- la **Regla 4** de `kb-kmm-datastore-preferences`

Si la creación depende de plataforma, usar `nativeModule` o el patrón equivalente del proyecto.

---

## Paso 7: Verificar la frontera final

Comprobar que el resultado cumple:

- `DataStore<Preferences>` no se propaga crudo por capas superiores
- las keys no están mezcladas en contratos de dominio sin necesidad
- los helpers de storage no viven bajo paquetes de red
- el ownership (`core` vs feature) sigue las skills de capa

---

## Paso 8: Informar al usuario con separación clara

Reportar por separado:

- base técnica de DataStore creada
- providers por plataforma creados
- adapter/store/repositorio local creado
- wiring en DI realizado
- consumers que todavía quedan por conectar
