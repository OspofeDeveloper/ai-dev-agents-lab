---
name: kb-tasks-kmm-room
description: "Base de conocimiento para implementar Room en KMP: entidades y DAOs en commonMain, @Database con RoomDatabaseConstructor, builder por plataforma (factory en cada source set), BundledSQLiteDriver, KSP por target, migraciones y registro DI. El stack usa Room, no SQLDelight."
argument-hint: "[sin argumentos]"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# kb-tasks-kmm-room

→ Decisión de plan (cuándo Room vs DataStore, ownership core/feature, qué contempla el plan): `kb-plan-kmm-room`

El stack usa **Room** (`2.7+`, con soporte KMP), **no SQLDelight**.

## Regla 1: Entidades, DAOs y `@Database` viven en `commonMain`

Todo el contrato de persistencia es código común:

- `@Entity` define las tablas; las entidades de Room no son los modelos de dominio crudos.
- `@Dao` define las operaciones; las lecturas exponen `Flow<…>`, las escrituras son `suspend`.
- `@Database` declara las entidades y la versión del esquema.

No hay nada de esto en `androidMain`/`iosMain`: solo el builder se divide por plataforma (Regla 3).

→ Templates: `${CLAUDE_SKILL_DIR}/references/room_kmp_templates.md`

---

## Regla 2: `@Database` declara `@ConstructedBy` y un `expect object` constructor

La clase `@Database` se anota con `@ConstructedBy(AppDatabaseConstructor::class)` y se acompaña de:

```kotlin
expect object AppDatabaseConstructor : RoomDatabaseConstructor<AppDatabase> {
    override fun initialize(): AppDatabase
}
```

El `actual` de ese object **lo genera el compilador de Room** por target — no se escribe a mano. Se declara como `expect object` en `commonMain`.

→ Templates: `${CLAUDE_SKILL_DIR}/references/room_kmp_templates.md`

---

## Regla 3: El builder se resuelve por plataforma con una factory en cada source set

La construcción del `RoomDatabase.Builder` depende del host:

- `androidMain`: `getDatabaseBuilder(context: Context)` usa `context.getDatabasePath("app.db")`
- `iosMain`: `getDatabaseBuilder()` usa filesystem nativo (`NSDocumentDirectory` vía `NSFileManager`)
- `commonMain`: solo el nombre común del fichero (`DB_FILE_NAME`)

**No es un par `expect/actual`**: la firma difiere por plataforma (Android necesita `Context`, iOS no), así que el `expect fun` no encajaría. Son **factories de plataforma** que se inyectan en `nativeModule` (Regla 7), donde Android recibe el `Context` de Koin. Lo que sí es expect/actual es el `RoomDatabaseConstructor` (Regla 2), que lo genera el compilador.

Es el **mismo principio de platform-split que Preferences DataStore** (path resuelto por plataforma): no se redefine aquí la regla general — vive en `kb-tasks-kmm-datastore-preferences` (Regla 3). Esta skill solo la aplica al builder de Room.

→ Templates: `${CLAUDE_SKILL_DIR}/references/room_kmp_templates.md`

---

## Regla 4: Driver bundled y coroutine context en la construcción final

El `AppDatabase` se construye sobre el builder con:

- `.setDriver(BundledSQLiteDriver())` — de `androidx.sqlite:sqlite-bundled`, garantiza la misma versión de SQLite en todos los targets.
- `.setQueryCoroutineContext(Dispatchers.IO)` — las queries no bloquean el hilo principal.
- `.build()`.

→ Templates: `${CLAUDE_SKILL_DIR}/references/room_kmp_templates.md`

---

## Regla 5: KSP se declara por target, con el plugin Room y `schemaDirectory`

La configuración Gradle del módulo de DB requiere:

- el plugin Room (`alias(libs.plugins.room)`) y el plugin KSP.
- el bloque `room { schemaDirectory("$projectDir/schemas") }`.
- el compilador de Room añadido **por target** (`add("kspAndroid", ...)`, `add("kspIosSimulatorArm64", ...)`, `add("kspIosArm64", ...)`, etc.) — no un único `ksp(...)`, que no cubre los targets nativos.
- `androidx.room.runtime` y `androidx.sqlite.bundled` en `commonMain`.

→ Templates: `${CLAUDE_SKILL_DIR}/references/room_kmp_templates.md`

---

## Regla 6: El esquema se versiona y las migraciones son explícitas

El esquema arranca en `version = 1` y sube de versión ante cualquier cambio estructural. Room exporta el esquema a `schemaDirectory`, que se versiona en git para que las migraciones sean auditables.

Cada salto de versión declara una `Migration(from, to)` añadida al builder con `.addMigrations(...)`. No usar `fallbackToDestructiveMigration` en producción salvo decisión explícita y justificada del proyecto.

→ Templates: `${CLAUDE_SKILL_DIR}/references/room_kmp_templates.md`

---

## Regla 7: El builder y la DB se registran en `nativeModule`

La creación de la DB depende de plataforma, así que su registro vive en `nativeModule` (o el patrón equivalente del proyecto), siguiendo `kb-tasks-koin`:

- provider del `RoomDatabase.Builder` (en Android recibe `Context`; en iOS no)
- `AppDatabase` construido (Regla 4)
- los DAOs expuestos desde la DB

El repositorio que recibe el DAO se registra en su módulo común, no en `nativeModule`.

---

## Regla 8: Sobre los DAOs vive un repositorio con semántica; no se propaga el DAO crudo

El `@Dao` es infraestructura local. La app **no propaga el DAO crudo** por las capas superiores: encima existe un repositorio que traduce entidades a dominio (`.map { it.toDomain() }`) y expone operaciones con significado.

El patrón de repositorio (Api/local → repo, DTO/entity → dominio) es SSoT de `kb-kmm-feature-clean-architecture` (ver `references/feature_remote_data_patterns.md`). Esta skill no lo redefine: solo fija que el DAO es la fuente local que el repositorio consume, igual que la `Api` es la fuente remota.

---

## Regla 9: Esta skill define Room; no cubre clave-valor ni otras DBs

Esta skill está limitada a Room sobre SQLite en KMP. No cubre:

- persistencia clave-valor / preferencias → `kb-tasks-kmm-datastore-preferences`
- SQLDelight u otros motores (el stack usa Room por decisión, ver `kb-plan-kmm-room`)
- la dimensión caché/offline sobre la DB → `kb-kmm-offline-strategy` (plan)

Si el proyecto necesita esas decisiones, viven en sus skills, no aquí.

---

## Regla 10: Esta skill se combina con capas, DI y la estrategia offline

Se apoya en:

- `kb-plan-kmm-room` para la decisión de plan (mecanismo, ownership)
- `kb-kmm-core-layer` / `kb-kmm-feature-clean-architecture` para ubicar la DB
- `kb-kmm-gradle-modules` para el módulo físico (`:core:database`)
- `kb-tasks-koin` para el wiring
- `kb-kmm-offline-strategy` cuando la DB actúa como SSoT de caché

No duplicar aquí reglas de capa, DI ni offline. Esta skill solo define cómo introducir Room con una frontera limpia.
