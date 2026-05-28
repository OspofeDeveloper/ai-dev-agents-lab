---
name: kb-kmm-app-errors
description: "Base de conocimiento del contrato transversal de errores y resultados en proyectos KMM: AppResult, AppError, ownership de taxonomías de error y reglas de adaptación entre capas."
argument-hint: "[sin argumentos]"
effort: medium
allowed-tools: [Read]
user-invocable: false
---

# kb-kmm-app-errors

## Regla 1: `AppResult<T, AppError>` es el contrato transversal preferido

Si el proyecto necesita propagar éxito o error entre capas, la convención preferida es un contrato tipado basado en valores, no en excepciones propagadas.

La forma estable es:

- `AppResult<T, AppError>` como contrato transversal de resultado
- `AppError` como contrato transversal de error
- implementaciones concretas de `AppError` por dominio técnico o funcional

Esta skill no obliga a un nombre exacto de tipos, pero sí fija el principio: el contrato transversal de la app debe ser explícito, tipado y compartido.

→ Templates: `references/app_error_contract_templates.md`

---

## Regla 2: Las excepciones no son el contrato principal entre capas

Las excepciones pueden existir dentro de librerías, adapters o detalles de infraestructura, pero no deben ser el lenguaje principal entre data, domain y presentation.

Está prohibido usar como contrato estable de app:

- `kotlin.Result` como estándar transversal del proyecto
- `Throwable` o `Exception` como tipo de error expuesto por repositorios, use cases o ViewModels
- jerarquías de excepciones como sustituto del contrato `AppError`

Las excepciones se capturan y normalizan en el borde que corresponda. Lo que sube hacia arriba es `AppResult` con `AppError`.

---

## Regla 3: `AppError` es un contrato base; las taxonomías concretas se especializan por dominio

`AppError` no debe convertirse en un cajón desastre con todos los casos posibles en un único sealed enorme. La estructura correcta es:

- `AppError` como contrato base compartido
- taxonomías concretas por dominio técnico o funcional
- cada taxonomía implementa `AppError`

Ejemplos válidos:

- `NetworkError : AppError`
- `AuthError : AppError`
- `StorageError : AppError`
- `FeatureXError : AppError`, si esa taxonomía solo tiene sentido dentro de una feature

La UI consume `AppError`; las capas inferiores pueden aportar variantes concretas.

→ Templates: `references/app_error_contract_templates.md`

---

## Regla 4: Un error vive en `core` solo si su significado es transversal

Una taxonomía de error debe vivir en `core` si:

- la usan varias features
- representa una preocupación compartida de infraestructura o dominio común
- su significado no depende de una única feature

Debe vivir dentro de una feature si:

- solo aplica a esa feature
- expresa una regla o validación propia de ese dominio
- no aporta valor fuera de esa feature

Esta skill fija el criterio de ownership del error. La ubicación concreta se apoya en `kb-kmm-core-layer` y `kb-kmm-feature-clean-architecture`.

---

## Regla 5: El borde remoto normaliza a `AppResult<T, AppError>`

Las excepciones del cliente HTTP, status codes y payloads de error del backend se interpretan en el borde remoto.

Ese borde:

- captura excepciones técnicas
- parsea error bodies si hace falta
- mapea esos detalles a una implementación concreta de `AppError`
- devuelve `AppResult<T, AppError>`

El repositorio no debe recibir `HttpResponse`, `Throwable` ni `ResponseException` como contrato estable.

---

## Regla 6: El repositorio conserva el error salvo que exista una razón semántica para adaptarlo

La regla preferida es:

- transformar el `Success` a dominio
- dejar subir el `Error` intacto

Solo se adapta un error cuando cambia su significado a nivel de negocio o de frontera. Ejemplos válidos:

- colapsar varios errores técnicos en un error de negocio compartido
- traducir un error remoto a una taxonomía propia de feature porque la feature necesita una semántica distinta
- priorizar una variante concreta cuando se combinan varias fuentes

No remapear errores por ritual ni duplicar taxonomías sin necesidad.

---

## Regla 7: El use case solo transforma errores si forma parte de la lógica de negocio

Un use case puede:

- propagar `AppResult` tal cual
- combinar varios `AppResult`
- priorizar errores
- traducir un error técnico a uno de negocio

Pero solo debe hacerlo cuando esa transformación expresa una regla de negocio o una política de aplicación. Si no hay semántica nueva, el error sube intacto.

---

## Regla 8: El ViewModel no interpreta detalles técnicos; reacciona a `AppError`

El ViewModel consume el contrato transversal de error y decide cómo impacta al estado de la pantalla:

- mostrar feedback
- activar retry
- exponer `UiText`
- lanzar un side effect

No debe conocer:

- códigos HTTP
- excepciones del cliente
- bodies crudos de error
- detalles internos de transporte

---

## Regla 9: El mapping `AppError -> UiText` vive en presentation

La representación visual del error pertenece a la capa de presentación.

La dirección correcta es:

- infraestructura produce una implementación concreta de `AppError`
- repositorio y use case la propagan o adaptan si procede
- presentation la convierte a `UiText` o equivalente

Ni networking ni domain deben construir mensajes visuales como contrato principal.

→ Templates: `references/app_error_contract_templates.md`

---

## Regla 10: Un string de backend no es todavía una política de UI

Si el backend devuelve un mensaje textual, ese valor no debe asumirse automáticamente como mensaje final de UI.

Puede usarse como:

- input para una implementación concreta de `AppError`
- texto dinámico en presentation, si el proyecto lo acepta explícitamente

Pero la decisión de mostrarlo, reemplazarlo o traducirlo pertenece a presentation/UI.

---

## Regla 11: Esta skill define el contrato transversal; otras skills definen sus variantes y uso local

Esta skill se combina con:

- `kb-kmm-network-contracts` para la variante de error de red y el borde remoto
- `kb-kmm-auth-contracts` para políticas de sesión y auth
- `kb-kmm-feature-clean-architecture` para ownership y adaptación dentro de una feature
- `kb-plan-kmm-ui-text` para la representación visual del error
- `kb-kmm-core-layer` para decidir cuándo una taxonomía debe vivir en `core`

Las otras skills no deben redefinir aquí qué es `AppError` ni cómo se usa `AppResult` como contrato transversal. Deben delegar.
