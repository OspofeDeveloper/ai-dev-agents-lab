# Model Boundary Templates

Illustrative examples only. They show the preferred null-tolerant edge and cleaned internal models.

## Nullable response DTO

```kotlin
data class UserProfileDto(
    val id: String? = null,
    val name: String? = null,
    val avatarUrl: String? = null,
    val tags: List<String?>? = null,
)
```

## Domain model with defaults

```kotlin
data class UserProfile(
    val id: String = "",
    val name: String = "",
    val avatarUrl: String = "",
    val tags: List<String> = emptyList(),
)
```

## Presentation model with defaults

```kotlin
data class UserProfileState(
    val isLoading: Boolean = false,
    val title: String = "",
    val avatarUrl: String = "",
    val tags: List<String> = emptyList(),
    val error: UIText? = null,
)
```

## Data-to-domain cleanup mapper

```kotlin
fun UserProfileDto.toDomain(): UserProfile {
    return UserProfile(
        id = id.orEmpty(),
        name = name.orEmpty(),
        avatarUrl = avatarUrl.orEmpty(),
        tags = tags.orEmpty().filterNotNull(),
    )
}
```

## Mapping that escalates invalid payloads

```kotlin
fun SessionDto.toDomainOrNull(): Session? {
    val token = token ?: return null
    val userId = userId ?: return null

    return Session(
        token = token,
        userId = userId,
        refreshToken = refreshToken.orEmpty(),
    )
}
```

When a required remote field is missing, prefer failing or returning a controlled error over leaking nullability into domain.
