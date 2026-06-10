# Templates Room para KMP

Room con soporte KMP (Room `2.7+`). Todo el contrato (entidades, DAOs, `@Database`) vive en `commonMain`; solo el builder se divide por plataforma.

## Entidad en `commonMain`

```kotlin
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    val name: String,
    val updatedAt: Long,
)
```

## DAO en `commonMain` (lecturas con `Flow`)

```kotlin
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface UserDao {

    @Query("SELECT * FROM users ORDER BY name")
    fun observeAll(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE id = :id")
    fun observeById(id: String): Flow<UserEntity?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(users: List<UserEntity>)

    @Query("DELETE FROM users")
    suspend fun clear()
}
```

## `@Database` + constructor en `commonMain`

```kotlin
import androidx.room.ConstructedBy
import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.RoomDatabaseConstructor

@Database(entities = [UserEntity::class], version = 1)
@ConstructedBy(AppDatabaseConstructor::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

// El `actual` lo genera el compilador de Room por target.
// Se declara como expect object en commonMain.
@Suppress("NO_ACTUAL_FOR_EXPECT")
expect object AppDatabaseConstructor : RoomDatabaseConstructor<AppDatabase> {
    override fun initialize(): AppDatabase
}
```

## Builder por plataforma (factory en cada source set)

> **No es expect/actual**: la firma difiere (Android necesita `Context`, iOS no). Son factories de plataforma que se inyectan en `nativeModule`. El único par expect/actual es el `RoomDatabaseConstructor` de arriba (lo genera el compilador).

`commonMain` (solo el nombre común del fichero):

```kotlin
internal const val DB_FILE_NAME = "app.db"
```

`androidMain` (usa `Context`):

```kotlin
import android.content.Context
import androidx.room.Room
import androidx.room.RoomDatabase

fun getDatabaseBuilder(context: Context): RoomDatabase.Builder<AppDatabase> {
    val dbFile = context.getDatabasePath(DB_FILE_NAME)
    return Room.databaseBuilder<AppDatabase>(
        context = context.applicationContext,
        name = dbFile.absolutePath,
    )
}
```

`iosMain` (filesystem nativo, `NSDocumentDirectory`):

```kotlin
import androidx.room.Room
import androidx.room.RoomDatabase
import kotlinx.cinterop.ExperimentalForeignApi
import platform.Foundation.NSDocumentDirectory
import platform.Foundation.NSFileManager
import platform.Foundation.NSUserDomainMask

@OptIn(ExperimentalForeignApi::class)
fun getDatabaseBuilder(): RoomDatabase.Builder<AppDatabase> {
    val documentDirectory = NSFileManager.defaultManager.URLForDirectory(
        directory = NSDocumentDirectory,
        inDomain = NSUserDomainMask,
        appropriateForURL = null,
        create = false,
        error = null,
    )
    val dbFilePath = requireNotNull(documentDirectory).path + "/$DB_FILE_NAME"
    return Room.databaseBuilder<AppDatabase>(name = dbFilePath)
}
```

## Construcción final del `AppDatabase` (común)

```kotlin
import androidx.room.RoomDatabase
import androidx.sqlite.driver.bundled.BundledSQLiteDriver
import kotlinx.coroutines.Dispatchers

fun buildDatabase(builder: RoomDatabase.Builder<AppDatabase>): AppDatabase =
    builder
        .setDriver(BundledSQLiteDriver())
        .setQueryCoroutineContext(Dispatchers.IO)
        .build()
```

## Bloque Gradle: plugin Room, KSP por target y driver bundled

`build.gradle.kts` del módulo de base de datos:

```kotlin
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidLibrary)
    alias(libs.plugins.room)
    alias(libs.plugins.ksp)
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.androidx.room.runtime)
            implementation(libs.androidx.sqlite.bundled)
        }
    }
}

room {
    schemaDirectory("$projectDir/schemas")
}

dependencies {
    // KSP de Room debe declararse por target, no con un único `ksp(...)`.
    add("kspAndroid", libs.androidx.room.compiler)
    add("kspIosSimulatorArm64", libs.androidx.room.compiler)
    add("kspIosArm64", libs.androidx.room.compiler)
    add("kspIosX64", libs.androidx.room.compiler)
}
```

Entradas relevantes en `libs.versions.toml`:

```toml
[versions]
room = "2.7.1"
sqlite = "2.5.1"

[libraries]
androidx-room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
androidx-room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }
androidx-sqlite-bundled = { module = "androidx.sqlite:sqlite-bundled", version.ref = "sqlite" }

[plugins]
room = { id = "androidx.room", version.ref = "room" }
ksp = { id = "com.google.devtools.ksp", version = "..." }
```

## Migración (esquema versionado)

```kotlin
import androidx.room.migration.Migration
import androidx.sqlite.SQLiteConnection
import androidx.sqlite.execSQL

val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(connection: SQLiteConnection) {
        connection.execSQL(
            "ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT ''"
        )
    }
}

// En el builder:
// builder.addMigrations(MIGRATION_1_2)
```

Al subir `version` en `@Database`, Room exporta el esquema nuevo a `schemaDirectory`. Versionar el directorio `schemas/` en git para que las migraciones sean auditables.

## Registro en DI (`nativeModule`)

El builder depende de plataforma → vive en `nativeModule` (patrón de `kb-tasks-koin`):

`androidMain`:

```kotlin
actual val nativeModule = module {
    single { getDatabaseBuilder(get()) }          // Context lo provee Koin Android
    single { buildDatabase(get()) }               // AppDatabase
    single { get<AppDatabase>().userDao() }        // DAO
}
```

`iosMain`:

```kotlin
actual val nativeModule = module {
    single { getDatabaseBuilder() }
    single { buildDatabase(get()) }
    single { get<AppDatabase>().userDao() }
}
```

El repositorio (que recibe el DAO) se registra en su módulo común, no aquí.
