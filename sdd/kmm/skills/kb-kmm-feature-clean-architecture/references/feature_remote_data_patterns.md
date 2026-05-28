# Patrones Remotos Dentro de una Feature — Ejemplos de Estructura

## 1. Estructura canónica de `data`

```text
data/
  remote/
    <Feature>Api.kt            ← ejecuta llamadas HTTP; única pieza que toca el cliente HTTP
    dto/                       ← DTOs de request y response
  responseHandlers/
    handle<Feature>Response.kt ← opcional; handlers HTTP cuando tienen lógica propia
  local/                       ← data sources locales, si los hay
  repository/
    <Feature>RepositoryImpl.kt ← recibe la Api como dependencia, mapea DTO -> dominio
```

## 2. Regla operativa de frontera remota

`<Feature>Api` es la única pieza de `data` que habla con el cliente HTTP. Cada método:

- recibe un request model o un DTO de request cuando el dato tiene una unidad semántica clara
- ejecuta la llamada envuelta en `tryCall` de `core/network`
- devuelve `AppResult<Dto, AppError>`

Si un `responseHandler` es pequeño, puede quedarse privado en la `Api`. Si crece o tiene suficiente semántica propia, la preferencia del proyecto es moverlo a `data/responseHandlers/`.

## 3. Regla operativa del repositorio

`<Feature>RepositoryImpl` recibe la `Api` como dependencia de constructor. No llama al cliente HTTP directamente.

Su trabajo es:

- invocar la `Api`
- transformar el resultado con `.map { it.toDomain() }`
- adaptar el error a la taxonomía de dominio solo si la feature lo requiere
