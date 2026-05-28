# ViewModel Scoping en Navigation Compose — Puente de Consulta

Esta reference no define un patrón propio de scoping.

Usarla solo como recordatorio de frontera:

- el grafo Compose puede necesitar scoping por pantalla o por nested graph
- el patrón autoritativo de emisión y consumo de efectos vive en `kb-kmm-navigation-viewmodel-events`
- el mecanismo concreto de inyección y paso de parámetros depende de la DI activa, como `kb-koin` si aplica
- `SavedStateHandle` no se usa en `commonMain`; los parámetros entran por constructor desde el Composable

Para ejemplos completos, consultar:

- `kb-kmm-navigation-viewmodel-events` -> `references/viewmodel-and-navigation-events.md`
- las references de la DI activa si el proyecto necesita scoping concreto
