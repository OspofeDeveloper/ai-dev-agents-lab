---
name: kb-plan-kmm-datastore-preferences
description: Preferences DataStore en KMM como decisión arquitectónica: cuándo usarlo, qué módulos se ven afectados, ownership core vs feature, separación storage/networking y contrato de factory compartida. Úsalo cuando haya que planificar persistencia local de preferencias en un proyecto KMM.
allowed-tools: [Read]
effort: low
user-invocable: false
---

# DataStore Preferences — Planificación

→ Implementación concreta (factory, path por plataforma, templates): `kb-tasks-kmm-datastore-preferences`

## Qué es Preferences DataStore en este contexto

`Preferences DataStore` es el mecanismo de persistencia clave-valor local en proyectos KMM.
Expone lectura reactiva mediante `Flow` y encapsula detalles de almacenamiento por plataforma.

No es un contrato de dominio ni un repositorio con semántica de negocio.
Sobre él debe existir un adapter o repositorio con intención explícita.

## Arquitectura del mecanismo

```
commonMain
  └── factory compartida        → crea DataStore<Preferences> (sin path concreto)
  └── adapter/store/repository  → expone operaciones con significado

androidMain
  └── path con Context          → resuelve la ubicación física del fichero

iosMain
  └── path con APIs nativas     → resuelve la ubicación física del fichero
```

## Cuándo contemplar DataStore en el plan

Incluirlo cuando:
- Una feature necesita persistir configuración, sesión, preferencias o estado entre arranques
- El equipo de auth necesita guardar/recuperar tokens de forma reactiva
- Múltiples features comparten estado persistido (→ sube a `core`)

No incluirlo si el estado es solo en memoria durante la sesión → basta con `StateFlow`.

## Ownership: core vs feature

| Situación | Ubicación |
|---|---|
| Estado compartido por varias features | `core` — infraestructura transversal |
| Auth, tokens, sesión global | `core` o módulo de auth en `core` |
| Estado propio de una sola feature | dentro de la feature |

El plan debe declarar explícitamente si el adapter vive en `core` o en la feature, y por qué.

## Separación storage / coordinación remota

El plan no debe mezclar en una misma tarea:
- persistencia local (DataStore)
- llamadas HTTP o refresh de sesión

Si la feature necesita ambas, son tareas separadas con piezas separadas.

## Qué debe contemplar el plan

1. Módulo donde vive el adapter (feature o core)
2. Nombre semántico del adapter (`SessionLocalDataSource`, `SettingsStore`, etc.)
3. Si el path de plataforma necesita configuración específica (Android Context, iOS filesystem)
4. Registro en DI (normalmente en `nativeModule` si la creación depende de plataforma)
5. Consumers: qué features o capas leen/escriben sobre este adapter

## Relación con otras skills del plan

- Ownership de módulos: `kb-kmm-core-layer`, `kb-kmm-feature-clean-architecture`
- Wiring DI: `kb-plan-koin`
- Si persiste tokens: `kb-kmm-auth-contracts`
