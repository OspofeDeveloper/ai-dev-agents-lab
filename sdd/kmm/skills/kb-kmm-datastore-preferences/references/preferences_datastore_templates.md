# Factory común en `commonMain`

```kotlin
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.PreferenceDataStoreFactory
import androidx.datastore.preferences.core.Preferences
import okio.Path.Companion.toPath

fun createPreferencesDataStore(
    producePath: () -> String
): DataStore<Preferences> =
    PreferenceDataStoreFactory.createWithPath(
        produceFile = { producePath().toPath() }
    )

internal const val dataStoreFileName = "app.preferences_pb"
```

## Provider Android

```kotlin
fun providePreferencesDataStore(context: Context): DataStore<Preferences> =
    createPreferencesDataStore(
        producePath = { context.filesDir.resolve(dataStoreFileName).absolutePath }
    )
```

## Provider iOS

```kotlin
@OptIn(ExperimentalForeignApi::class)
fun providePreferencesDataStore(): DataStore<Preferences> =
    createPreferencesDataStore(
        producePath = {
            val documentDirectory = NSFileManager.defaultManager.URLForDirectory(
                directory = NSDocumentDirectory,
                inDomain = NSUserDomainMask,
                appropriateForURL = null,
                create = false,
                error = null,
            )
            requireNotNull(documentDirectory).path + "/$dataStoreFileName"
        }
    )
```

## Keys agrupadas por adapter

```kotlin
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey

internal object SessionPreferencesKeys {
    val accessToken = stringPreferencesKey("access_token")
    val refreshToken = stringPreferencesKey("refresh_token")
    val isUserLogged = booleanPreferencesKey("is_user_logged")
}
```

## Adapter sobre DataStore

```kotlin
class SessionLocalDataSource(
    private val dataStore: DataStore<Preferences>
) {
    val accessToken: Flow<String?> =
        dataStore.data.map { it[SessionPreferencesKeys.accessToken] }

    suspend fun saveAccessToken(value: String) {
        dataStore.edit { it[SessionPreferencesKeys.accessToken] = value }
    }

    suspend fun clear() {
        dataStore.edit {
            it.remove(SessionPreferencesKeys.accessToken)
            it.remove(SessionPreferencesKeys.refreshToken)
            it.remove(SessionPreferencesKeys.isUserLogged)
        }
    }
}
```

## Registro en DI

```kotlin
val storageModule = module {
    single { providePreferencesDataStore(get()) }
    single { SessionLocalDataSource(get()) }
}
```
