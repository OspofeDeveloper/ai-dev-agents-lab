# ViewModel Scoping — Boundary Reference

This reference does not define a scoping pattern of its own.

Use it only as a boundary reminder:

- Compose Navigation may require screen-level or nested-graph scoping
- the authoritative effect emission/consumption pattern lives in `kb-kmm-navigation-viewmodel-events`
- concrete injection and parameter passing depend on the active DI skill, such as `kb-koin`
- `SavedStateHandle` is not used in `commonMain`; parameters enter through the Composable and then through the constructor

For complete examples, see:

- `kb-kmm-navigation-viewmodel-events` → `references/viewmodel-and-navigation-events.md`
- the references of the active DI skill when the project needs concrete scoping
