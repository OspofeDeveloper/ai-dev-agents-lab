---
name: kb-kmm-network-contracts
description: "Base de conocimiento de contratos de networking en proyectos KMM: errores de red, resultados tipados, límites entre servicios remotos y repositorios, y reglas estables independientes de la librería HTTP."
argument-hint: ""
effort: low
allowed-tools: [Read]
context: fork
disable-model-invocation: true
---

# Network Contracts KMM — Base de Conocimiento

## Regla 1: Separar contrato de red e implementación HTTP

La política de networking debe sobrevivir a un cambio de librería HTTP. Por eso, esta skill define conceptos estables y no detalles de Ktor, Retrofit u otra implementación.

La ubicación concreta de estos contratos se decide con las skills de capa:

- `kb-kmm-core-layer` si el contrato es transversal a varias features
- `kb-kmm-feature-clean-architecture` si el contrato pertenece a una única feature

---

## Regla 2: Esta skill define límites de integración, no arquitectura general de capas

Esta skill regula únicamente el borde entre:

- cliente HTTP o data source remoto
- contrato técnico de error y resultado
- repositorio que adapta la respuesta remota al dominio

No define:

- cómo se organiza internamente una feature
- dónde vive físicamente cada pieza
- cómo se implementa el cliente HTTP
- cómo se registran dependencias
- cómo funciona la autenticación

Si una regla aplica a cualquier integración remota aunque cambie la librería HTTP, pertenece aquí. Si habla de carpetas, DI, Ktor o auth concreta, pertenece a otra skill.

---

## Regla 3: El contrato preferido es `AppResult<T, AppError>`

Las operaciones remotas no exponen excepciones crudas a las capas superiores. Deben devolver un resultado tipado con éxito o error controlado.

La convención preferida para estas skills es:

- `AppResult<T, AppError>` como contrato transversal de resultado
- `AppError` como contrato transversal de error
- `NetworkError` como implementación concreta de `AppError` para el dominio de red

El principio estable es este: la capa superior no interpreta excepciones de transporte sin normalizar y la red se integra en el mismo contrato de resultado/error que use el resto del proyecto.

La definición del contrato transversal `AppResult` / `AppError` pertenece a `kb-kmm-app-errors`. Esta skill lo consume y lo especializa para el borde remoto.

→ Templates: `references/network_contracts_templates.md`

---

## Regla 4: `NetworkError` es una implementación concreta de `AppError`

Los errores de transporte y protocolo se mapean a un contrato técnico estable, por ejemplo:

- sin conexión
- error de serialización
- no autorizado
- timeout
- conflicto
- error servidor
- error desconocido

La taxonomía exacta puede variar, pero debe ser única y compartida dentro del dominio de red.

En esta convención:

- `AppError` es el contrato base
- `NetworkError` implementa `AppError`
- otros dominios pueden aportar otras implementaciones concretas (`BleError`, `CoreError`, etc.)

La UI y el dominio superior trabajan con `AppError`; networking solo aporta una variante concreta dentro de ese contrato.

La política general de ownership, adaptación y propagación de `AppError` pertenece a `kb-kmm-app-errors`.

→ Templates: `references/network_contracts_templates.md`

---

## Regla 5: El data source remoto expone modelos técnicos dentro de `AppResult`

El límite remoto habla en términos de transporte o integración:

- DTOs
- payloads HTTP
- errores de red normalizados
- resultados tipados aplicados al contrato transversal del proyecto

No expone directamente modelos de dominio ni detalles crudos del cliente HTTP hacia arriba.

---

## Regla 6: El repositorio adapta de contrato remoto a dominio

El repositorio consume el contrato remoto y lo adapta a las necesidades del dominio:

- transforma DTOs a modelos de dominio
- conserva o convierte errores remotos al contrato superior que corresponda
- oculta detalles del cliente HTTP a casos de uso y UI

Esta regla no decide si el repositorio vive en `core` o dentro de una feature. Esa decisión pertenece a las skills de capa.

El patrón preferido es:

- la API o remote source devuelve `AppResult<Dto, AppError>`
- el repositorio transforma el `Success` con `map { dto -> domain }`
- el error sube intacto salvo que exista una razón de negocio clara para adaptarlo

Eso evita remapeos redundantes y mantiene una sola taxonomía de error en la app.

---

## Regla 7: La URL base, headers globales y auth no forman parte del contrato remoto estable

La URL base, los headers globales, la auth automática y otras decisiones de cliente pertenecen a infraestructura.

Esta skill solo fija que esas decisiones no deben contaminar el contrato remoto estable.

---

## Regla 8: Logging y observabilidad van detrás de abstracciones

Si el proyecto registra tráfico de red, debe hacerlo a través de una abstracción reutilizable (`AppLogger` u otra), no acoplando cada servicio a una librería concreta de logging.

---

## Regla 9: Polimorfismo JSON y convenciones del backend son contratos de integración

Si el backend usa discriminadores como `"$type"`, códigos de error propios o convenciones de payload, esas reglas pertenecen al contrato de integración de red, no a la arquitectura ni a la DI.

---

## Regla 10: Esta skill define contratos remotos; otras skills deciden ubicación e implementación

Esta skill se combina con:

- `kb-kmm-app-errors` para el contrato transversal `AppResult` / `AppError`
- `kb-kmm-core-layer` para decidir si el contrato es transversal
- `kb-kmm-feature-clean-architecture` para decidir cómo se integra dentro de una feature
- `kb-kmm-http-ktor` para implementarlo con Ktor, si aplica
- skills de auth para cualquier política o mecanismo de autenticación

No duplicar aquí reglas que ya pertenezcan a esas dimensiones.

---

## Regla 11: La normalización de errores HTTP produce `AppResult<T, AppError>`

La lectura de códigos HTTP, parsing de body de error y mapeo de excepciones de cliente pertenecen al borde remoto, no al repositorio ni al ViewModel.

El patrón estable es:

- `tryCall` o helper equivalente ejecuta la llamada
- `handleResponse` o helper equivalente transforma `HttpResponse` a `AppResult<T, AppError>`
- el repositorio consume ese resultado ya normalizado

El repositorio no debe reinterpretar status codes ni parsear bodies de error del backend.

## Regla 12: La UI consume un error transversal, no un detalle HTTP

Las capas de presentación no deberían conocer `HttpResponse`, códigos de estado ni excepciones del cliente.

Lo correcto es:

- ViewModel consume `AppResult<Domain, AppError>` o equivalente
- presentation reacciona con `onSuccess` / `onError`
- la conversión a `UiText` o representación visual ocurre en presentation/UI

La red aporta una variante de error; la UI consume el contrato transversal del proyecto.
