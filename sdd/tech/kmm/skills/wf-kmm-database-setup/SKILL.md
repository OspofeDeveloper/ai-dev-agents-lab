---
name: wf-kmm-database-setup
description: "Configura Room en un proyecto KMM componiendo ownership del módulo de DB, entidades/DAOs en commonMain, builder por plataforma, KSP y driver, wiring de DI y separación DAO/repositorio."
when_to_use: "Activa con frases como 'configura Room', 'añade base de datos a KMM', 'setup de persistencia relacional', 'necesito una DB local en KMM'. No activa para clave-valor/preferencias (usa wf-kmm-datastore-setup) ni para networking (usa wf-kmm-network-setup)."
argument-hint: "[entidades a persistir, módulo destino (core vs feature), DI activa y consumers previstos]"
effort: medium
allowed-tools: [Read, Write, Bash]
context: fork
agent: kmm-platform-integrator
user-invocable: true
---

# wf-kmm-database-setup

## Paso 1: Confirmar ownership del módulo de DB

Antes de crear nada, confirmar o inferir:

1. si la DB es transversal (`:core:database`) o propia de una feature
2. qué consumer la usa: una feature concreta, varias features, o estado transversal
3. qué DI está activa, siguiendo `kb-tasks-koin` si aplica
4. qué plataformas están activas (Android, iOS) para el builder

Aplicar:

- `kb-kmm-core-layer`
- `kb-kmm-feature-clean-architecture`
- `kb-tasks-kmm-room`

---

## Paso 2: Crear entidades y DAOs en `commonMain`

Crear las `@Entity` y los `@Dao` en código común, siguiendo la **Regla 1** de `kb-tasks-kmm-room`:

- entidades como tablas (no son los modelos de dominio crudos)
- DAOs con lecturas que exponen `Flow<…>` y escrituras `suspend`

No introducir todavía el builder de plataforma ni el repositorio.

---

## Paso 3: Crear `@Database` y constructor

Crear la clase `@Database` con `@ConstructedBy` y el `expect object` constructor, siguiendo la **Regla 2** de `kb-tasks-kmm-room`. El `actual` del constructor lo genera el compilador — no se escribe a mano.

---

## Paso 4: Crear el builder expect/actual por plataforma

Implementar la resolución del builder por plataforma, siguiendo la **Regla 3** de `kb-tasks-kmm-room`:

- `commonMain` declara `expect fun getDatabaseBuilder()`
- `androidMain` usa `Context` (`getDatabasePath`)
- `iosMain` usa filesystem nativo (`NSDocumentDirectory`)

Es el mismo patrón platform-split que DataStore; no mezclar aquí wiring de repositorios.

---

## Paso 5: Configurar KSP, driver y plugin Room en Gradle

Configurar la build del módulo de DB, siguiendo las **Reglas 4 y 5** de `kb-tasks-kmm-room`:

- plugin Room + KSP, bloque `room { schemaDirectory(...) }`
- compilador de Room añadido **por target** (`kspAndroid`, `kspIosSimulatorArm64`, ...)
- construcción final con `BundledSQLiteDriver()` y `setQueryCoroutineContext(Dispatchers.IO)`
- esquema versionado desde `version = 1` (**Regla 6** para migraciones)

---

## Paso 6: Registrar el builder y la DB en DI

Registrar en `nativeModule` (la creación depende de plataforma), siguiendo la **Regla 7** de `kb-tasks-kmm-room` y `kb-tasks-koin`:

- provider del `RoomDatabase.Builder`
- `AppDatabase` construido
- los DAOs expuestos desde la DB

El repositorio se registra en su módulo común, no en `nativeModule`.

---

## Paso 7: Separar el DAO crudo del repositorio

Asegurar que sobre los DAOs existe un repositorio con semántica, siguiendo la **Regla 8** de `kb-tasks-kmm-room`. El DAO crudo no se propaga por capas superiores: el repositorio traduce entidades a dominio.

El patrón de repositorio es de `kb-kmm-feature-clean-architecture` — no redefinirlo aquí.

---

## Paso 8: Verificar fronteras

Comprobar que el resultado cumple:

- entidades, DAOs y `@Database` viven en `commonMain`; solo el builder se divide por plataforma
- KSP declarado por target (no un único `ksp(...)`)
- el DAO no se propaga crudo; hay repositorio encima
- el ownership (`:core:database` vs feature) sigue las skills de capa
- esquema versionado y migraciones declaradas

---

## Paso 9: Informar al usuario con separación clara

Reportar por separado:

- entidades y DAOs creados (commonMain)
- `@Database` y constructor creados
- builder por plataforma creado (Android, iOS)
- configuración Gradle (KSP por target, driver, plugin, schemaDirectory)
- wiring en DI realizado
- repositorio sobre los DAOs (creado o pendiente)
- verificación ejecutable de cierre (build/tests con los comandos de `kmm_project_state.md`)
