# Remote Data Patterns Within a Feature — Structure Examples

## 1. Canonical `data` structure

```text
data/
  remote/
    <Feature>Api.kt            ← executes HTTP calls; the only piece that touches the HTTP client
    dto/                       ← request and response DTOs
  responseHandlers/
    handle<Feature>Response.kt ← optional; HTTP handlers when they carry their own logic
  local/                       ← local data sources, if any
  repository/
    <Feature>RepositoryImpl.kt ← receives the Api as a dependency; maps DTO → domain
```

## 2. Remote boundary rule

`<Feature>Api` is the only `data` piece that talks to the HTTP client. Each method:

- receives a request model or request DTO when the input has a clear semantic unit
- executes the call wrapped in `tryCall` from `core/network`
- returns `AppResult<Dto, AppError>`

If a `responseHandler` is small, it may remain private inside the `Api`. If it grows or develops enough semantics of its own, the project preference is to move it to `data/responseHandlers/`.

## 3. Repository rule

`<Feature>RepositoryImpl` receives the `Api` as a constructor dependency. It does not call the HTTP client directly.

Its responsibilities are:

- invoke the `Api`
- transform the result with `.map { it.toDomain() }`
- adapt the error to the domain error taxonomy only if the feature requires it